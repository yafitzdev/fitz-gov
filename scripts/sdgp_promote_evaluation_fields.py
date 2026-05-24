"""Promote legacy evaluator fields into the canonical SDGP `evaluation` block."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.evaluation_fields import (
    audit_evaluation_fields,
    needs_evaluation_enrichment,
    promote_evaluation_fields,
)
from fitz_gov.sdgp.vault import Vault


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--vault", type=Path, default=Path("data/sdgp_vault_v51_enriched"))
    p.add_argument(
        "--report",
        type=Path,
        default=Path("data/sdgp_v7_qa/evaluation_fields_summary.json"),
    )
    p.add_argument("--dry-run", action="store_true")
    p.add_argument(
        "--keep-legacy",
        action="store_true",
        help="Promote fields but keep meta.v51_legacy for audit/debug.",
    )
    p.add_argument(
        "--keep-aliases",
        action="store_true",
        help="Promote fields but keep duplicate root/meta/governance aliases.",
    )
    return p.parse_args()


def _cohort(case: dict[str, Any]) -> str:
    meta = case.get("meta") if isinstance(case.get("meta"), dict) else {}
    return str(meta.get("dataset_version") or "unknown")


def main() -> int:
    args = parse_args()
    vault = Vault.open(args.vault)
    updates: dict[str, dict[str, Any]] = {}
    changed_by_cohort: Counter[str] = Counter()
    stripped_paths: Counter[str] = Counter()
    changed_paths: Counter[str] = Counter()
    issue_paths: dict[str, Counter[str]] = defaultdict(Counter)
    totals: Counter[str] = Counter()
    needs_enrichment: Counter[str] = Counter()

    for case in vault.iter_cases():
        case_id = str(case.get("id") or "")
        cohort = _cohort(case)
        totals[cohort] += 1

        result = promote_evaluation_fields(
            case,
            strip_legacy=not args.keep_legacy,
            strip_aliases=not args.keep_aliases,
        )
        if result.changed:
            updates[case_id] = case
            changed_by_cohort[cohort] += 1
            changed_paths.update(result.changed_paths)
            stripped_paths.update(result.stripped_paths)

        for issue in audit_evaluation_fields(case):
            issue_paths[cohort][issue.path] += 1
        if needs_evaluation_enrichment(case):
            needs_enrichment[cohort] += 1

    summary = {
        "vault": str(args.vault),
        "dry_run": args.dry_run,
        "total_rows": len(vault),
        "totals_by_cohort": dict(sorted(totals.items())),
        "rows_changed": len(updates),
        "rows_changed_by_cohort": dict(sorted(changed_by_cohort.items())),
        "changed_paths": dict(sorted(changed_paths.items())),
        "stripped_paths": dict(sorted(stripped_paths.items())),
        "evaluation_issues_by_cohort": {
            k: dict(sorted(v.items())) for k, v in sorted(issue_paths.items())
        },
        "needs_evaluation_enrichment_by_cohort": dict(sorted(needs_enrichment.items())),
    }

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=== Promote SDGP evaluation fields ===")
    print(f"Vault      : {args.vault} ({len(vault)} rows)")
    print(f"Dry run    : {args.dry_run}")
    print(f"Changed    : {len(updates)} rows")
    print(f"Report     : {args.report}")
    print("Needs enrichment by cohort:")
    for cohort, n in sorted(needs_enrichment.items()):
        print(f"  {cohort}: {n}")

    if args.dry_run:
        print("Dry run: no vault update written.")
        return 0

    if updates:
        print(f"Writing {len(updates)} updates...")
        print(vault.update_cases(updates))
    else:
        print("No updates to write.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
