"""Merge subagent-generated V7 JSONL rows into the SDGP vault.

Rows must have shape:

    {"case_id": "...", "case": {...}}

When `--batch-dir` is supplied, each output file is checked against the
matching batch spec so omitted, extra, or duplicate case ids fail fast.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.checker import Checker, Severity, case_dedup_hash, hashes_from
from fitz_gov.sdgp.vault import Provenance, Vault, new_batch_id


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--vault", type=Path, default=Path("data/sdgp_vault_v51_enriched"))
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/sdgp_handoff_v7_expand/subagent_outputs"),
    )
    p.add_argument(
        "--batch-dir",
        type=Path,
        default=Path("data/sdgp_handoff_v7_expand/subagent_batches"),
    )
    p.add_argument("--glob", type=str, default="batch_*.jsonl")
    p.add_argument("--provider", type=str, default="codex_subagent")
    p.add_argument("--provider-version", type=str, default="gpt-5.4")
    p.add_argument("--batch-id", type=str, default=None)
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            try:
                row = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: row must be a JSON object")
            rows.append(row)
    return rows


def _expected_ids(batch_dir: Path, output_path: Path) -> set[str] | None:
    batch_path = batch_dir / f"{output_path.stem}.json"
    if not batch_path.exists():
        return None
    data = json.loads(batch_path.read_text(encoding="utf-8"))
    return {str(slot["case_id"]) for slot in data.get("slots", [])}


def _validate_id_set(path: Path, rows: list[dict[str, Any]], expected: set[str] | None) -> int:
    bad = 0
    ids = [row.get("case_id") for row in rows]
    counter = Counter(ids)
    duplicates = sorted(str(cid) for cid, count in counter.items() if count > 1)
    if duplicates:
        print(f"DUPLICATE IDS {path}: {duplicates[:10]}", file=sys.stderr)
        bad += len(duplicates)
    if expected is not None:
        got = {str(cid) for cid in ids if isinstance(cid, str)}
        missing = sorted(expected - got)
        extra = sorted(got - expected)
        if missing:
            print(f"MISSING IDS {path}: {missing[:10]}", file=sys.stderr)
            bad += len(missing)
        if extra:
            print(f"EXTRA IDS {path}: {extra[:10]}", file=sys.stderr)
            bad += len(extra)
    return bad


def main() -> int:
    args = parse_args()
    vault = Vault.open(args.vault)
    files = sorted(args.out_dir.glob(args.glob))
    checker = Checker(require_training_schema=True)
    seen_hashes = hashes_from(vault.iter_cases())
    batch_id = args.batch_id or new_batch_id()

    print("=== Merge V7 generation JSONL ===")
    print(f"Vault  : {args.vault}")
    print(f"Out dir: {args.out_dir}")
    print(f"Files  : {len(files)}")
    print(f"Dry run: {args.dry_run}")
    print(f"Batch  : {batch_id}")
    print()

    n_rows = 0
    n_ok = 0
    n_bad = 0
    n_exists = 0
    accepted: list[dict[str, Any]] = []

    for path in files:
        try:
            rows = _read_jsonl(path)
        except ValueError as exc:
            print(f"READ FAIL {exc}", file=sys.stderr)
            n_bad += 1
            continue
        n_bad += _validate_id_set(path, rows, _expected_ids(args.batch_dir, path))

        for row in rows:
            n_rows += 1
            case_id = row.get("case_id")
            case = row.get("case")
            if not isinstance(case_id, str) or not isinstance(case, dict):
                print(f"BAD ROW {path}: expected case_id + case", file=sys.stderr)
                n_bad += 1
                continue
            if vault.get(case_id) is not None:
                n_exists += 1
                continue

            case["id"] = case_id
            case["version"] = "fitz-gov-7.0"
            case.setdefault("meta", {})["dataset_version"] = "v7"

            result = checker.check(case, seen_hashes=seen_hashes)
            has_errors = any(issue.severity == Severity.ERROR for issue in result.issues)
            if has_errors:
                reasons = "; ".join(f"{issue.rule}: {issue.message}" for issue in result.issues[:5])
                print(f"CHECK FAIL {case_id}: {reasons}", file=sys.stderr)
                n_bad += 1
                continue
            h = case_dedup_hash(case)
            if h:
                seen_hashes.add(h)
            accepted.append(case)
            n_ok += 1

    print(f"Rows read : {n_rows}")
    print(f"Accepted  : {n_ok}")
    print(f"Existing  : {n_exists}")
    print(f"Rejected  : {n_bad}")

    if args.dry_run:
        print("Dry run: no vault updates written.")
        return 0 if n_bad == 0 else 1

    provenance = Provenance(
        provider=args.provider,
        provider_version=args.provider_version,
        prompt_version="sdgp-prompts-v1",
        batch_id=batch_id,
    )
    added = 0
    dup = 0
    for case in accepted:
        if vault.add(case, provenance=provenance):
            added += 1
        else:
            dup += 1
    print(f"Added     : {added}")
    print(f"Duplicate : {dup}")
    print(f"Vault size: {len(vault)}")
    return 0 if n_bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
