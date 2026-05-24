"""Audit SDGP vault rows for full V6/MoE training-schema completeness."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.completeness import summarize_completeness
from fitz_gov.sdgp.vault import Vault


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--vault", type=Path, default=Path("data/sdgp_vault_v51_enriched"))
    p.add_argument("--cohort", type=str, default=None, help="Optional meta.dataset_version filter")
    p.add_argument("--top", type=int, default=25)
    p.add_argument("--json-out", type=Path, default=None)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    vault = Vault.open(args.vault)
    cases = []
    for case in vault.iter_cases():
        meta = case.get("meta") if isinstance(case.get("meta"), dict) else {}
        if args.cohort and meta.get("dataset_version") != args.cohort:
            continue
        cases.append(case)

    summary = summarize_completeness(cases)
    print("=== Training-schema completeness audit ===")
    print(f"Vault : {args.vault}")
    print(f"Rows  : {len(cases)}")
    print()

    totals = summary["totals"]
    complete = summary["complete"]
    for cohort, total in sorted(totals.items()):
        done = complete.get(cohort, 0)
        pct = 100.0 * done / max(total, 1)
        print(f"{cohort}: {done}/{total} complete ({pct:.1f}%)")

    print()
    print(f"Top missing paths (top {args.top}):")
    for cohort, paths in summary["missing_by_path"].items():
        print(f"\n[{cohort}]")
        for path, count in sorted(paths.items(), key=lambda kv: (-kv[1], kv[0]))[: args.top]:
            print(f"  {path}: {count}")

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"\nJSON report: {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
