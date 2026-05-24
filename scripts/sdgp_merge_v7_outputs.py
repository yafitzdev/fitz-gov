"""sdgp_merge_v7_outputs.py — validate Sonnet V7-generation outputs + add to vault.

Walks `data/sdgp_handoff_v7/out/*.json` (and `out/merged/*.json` for stragglers),
parses each as a fitz-gov case, runs the structural Checker, tags new cases with
`meta.dataset_version: "v7"`, and adds via `Vault.add()` (idempotent).

Files that pass checker → vault. Files that fail → archived to `out/rejected/`
with the failure reason logged. Files that already exist in the vault (same
case ID) are skipped.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.checker import Checker, Severity, case_dedup_hash, hashes_from
from fitz_gov.sdgp.orchestrator import parse_case_json
from fitz_gov.sdgp.vault import Provenance, Vault, new_batch_id


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--vault", type=Path, default=Path("data/sdgp_vault_v51_enriched"))
    p.add_argument("--out-dir", type=Path, default=Path("data/sdgp_handoff_v7/out"))
    p.add_argument(
        "--batch-id",
        type=str,
        default=None,
        help="Vault provenance batch_id (default: auto-generated)",
    )
    p.add_argument(
        "--no-archive", action="store_true", help="Don't move processed out/*.json files"
    )
    p.add_argument(
        "--allow-thin",
        action="store_true",
        help="Allow structurally valid but training-schema-incomplete rows",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    vault = Vault.open(args.vault)
    print(f"Vault: {len(vault)} cases before merge")

    # Collect both unmerged out/ and unmerged out/merged/ files
    files = sorted(args.out_dir.glob("*.json"))
    merged_dir = args.out_dir / "merged"
    if merged_dir.exists():
        for f in sorted(merged_dir.glob("*.json")):
            files.append(f)
    print(f"Output files to process: {len(files)}")
    if not files:
        return 0

    checker = Checker(require_training_schema=not args.allow_thin)
    seen_hashes = hashes_from(vault.iter_cases())
    batch_id = args.batch_id or new_batch_id()
    print(f"Using batch_id: {batch_id}")
    print(f"Require training schema: {not args.allow_thin}")

    n_added = 0
    n_parse_fail = 0
    n_check_fail = 0
    n_dup = 0
    n_exists = 0

    rejected_dir = args.out_dir / "rejected"
    archived_dir = args.out_dir / "merged"
    rejected_dir.mkdir(exist_ok=True)
    archived_dir.mkdir(exist_ok=True)

    for f in files:
        try:
            raw = f.read_text(encoding="utf-8")
            case = parse_case_json(raw)
        except Exception as exc:
            n_parse_fail += 1
            (rejected_dir / f.name).write_text(
                f"PARSE FAIL: {exc}\n\n{raw[:2000]}", encoding="utf-8"
            )
            f.unlink(missing_ok=True)
            continue

        # Tag as v7 + canonical version
        case.setdefault("meta", {})["dataset_version"] = "v7"
        case["version"] = "fitz-gov-7.0"

        # Skip if vault already has this id
        if case.get("id") and vault.get(case["id"]) is not None:
            n_exists += 1
            if not args.no_archive:
                shutil.move(str(f), str(archived_dir / f.name))
            continue

        # Structural check
        result = checker.check(case, seen_hashes=seen_hashes)
        has_errors = any(i.severity == Severity.ERROR for i in result.issues)
        if has_errors:
            n_check_fail += 1
            reasons = "; ".join(f"[{i.severity}] {i.code}: {i.message}" for i in result.issues)
            (rejected_dir / f.name).write_text(
                f"CHECKER FAIL: {reasons}\n\n{json.dumps(case, indent=2, ensure_ascii=False)[:3000]}",
                encoding="utf-8",
            )
            f.unlink(missing_ok=True)
            continue

        # Add to vault
        prov = Provenance(
            provider="sonnet_subagent",
            provider_version="sonnet-4.6",
            prompt_version="sdgp-prompts-v1",
            batch_id=batch_id,
        )
        try:
            vault.add(case, provenance=prov)
            n_added += 1
            seen_hashes.add(case_dedup_hash(case))
            if not args.no_archive:
                shutil.move(str(f), str(archived_dir / f.name))
        except Exception as exc:
            n_dup += 1
            (rejected_dir / f.name).write_text(
                f"VAULT ADD FAIL: {exc}\n\n{json.dumps(case, indent=2, ensure_ascii=False)[:3000]}",
                encoding="utf-8",
            )
            f.unlink(missing_ok=True)

    print(f"\nMerge stats:")
    print(f"  added       : {n_added}")
    print(f"  exists      : {n_exists}")
    print(f"  parse fails : {n_parse_fail}")
    print(f"  check fails : {n_check_fail}")
    print(f"  dup fails   : {n_dup}")
    print(f"  vault size  : {len(vault)} cases after merge")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
