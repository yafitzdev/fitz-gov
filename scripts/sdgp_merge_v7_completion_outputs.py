"""Merge subagent-produced V7 completion overlays into the vault.

Input files are JSONL, one row per case:

    {"case_id": "...", "overlay": {...}}

Rows are merged into a copy of the existing vault case, then required to pass:
- `audit_case_completeness(case) == []`
- `Checker(require_training_schema=True).check(case).passed`

Only passing rows are written back to the vault.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.checker import Checker
from fitz_gov.sdgp.completeness import audit_case_completeness
from fitz_gov.sdgp.v7_completion import merge_v7_completion
from fitz_gov.sdgp.vault import Vault


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--vault", type=Path, default=Path("data/sdgp_vault_v51_enriched"))
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/sdgp_handoff_v7_complete/subagent_outputs"),
    )
    p.add_argument("--glob", type=str, default="*.jsonl")
    p.add_argument("--overwrite", action="store_true")
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


def main() -> int:
    args = parse_args()
    vault = Vault.open(args.vault)
    files = sorted(args.out_dir.glob(args.glob))

    print("=== Merge V7 completion overlays ===")
    print(f"Vault  : {args.vault}")
    print(f"Out dir: {args.out_dir}")
    print(f"Files  : {len(files)}")
    print(f"Dry run: {args.dry_run}")
    print()

    checker = Checker(require_training_schema=True)
    updates: dict[str, dict[str, Any]] = {}
    seen_case_ids: set[str] = set()
    n_rows = 0
    n_ok = 0
    n_bad = 0

    for path in files:
        try:
            rows = _read_jsonl(path)
        except ValueError as exc:
            print(f"READ FAIL {exc}", file=sys.stderr)
            n_bad += 1
            continue

        for row in rows:
            n_rows += 1
            case_id = row.get("case_id")
            overlay = row.get("overlay")
            if not isinstance(case_id, str) or not isinstance(overlay, dict):
                print(f"BAD ROW {path}: expected case_id + overlay", file=sys.stderr)
                n_bad += 1
                continue
            if case_id in seen_case_ids:
                print(f"DUPLICATE CASE {case_id} in {path}", file=sys.stderr)
                n_bad += 1
                continue
            seen_case_ids.add(case_id)

            case = vault.get(case_id)
            if case is None:
                print(f"UNKNOWN CASE {case_id}", file=sys.stderr)
                n_bad += 1
                continue

            merge_v7_completion(case, overlay, overwrite=args.overwrite)
            missing = audit_case_completeness(case)
            if missing:
                print(
                    f"INCOMPLETE {case_id}: {len(missing)} fields remain; first={missing[0].path}",
                    file=sys.stderr,
                )
                n_bad += 1
                continue

            result = checker.check(case)
            if not result.passed:
                print(
                    f"CHECK FAIL {case_id}: "
                    + "; ".join(f"{i.rule}: {i.message}" for i in result.errors[:5]),
                    file=sys.stderr,
                )
                n_bad += 1
                continue

            updates[case_id] = case
            n_ok += 1

    print(f"Rows read : {n_rows}")
    print(f"Accepted  : {n_ok}")
    print(f"Rejected  : {n_bad}")

    if args.dry_run:
        print("Dry run: no vault update written.")
        return 0 if n_bad == 0 else 1

    if updates:
        print(f"Writing {len(updates)} updates...")
        print(vault.update_cases(updates))
    else:
        print("No updates to write.")

    return 0 if n_bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
