"""Run V7 release-candidate QA audits and emit review artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.gap_detector import GapDetector
from fitz_gov.sdgp.qa import (
    assign_query_grouped_splits,
    blind_label_manifest_rows,
    blind_label_queue_rows,
    cross_label_query_groups,
    duplicate_summary,
    jsonl_text,
    markdown_report,
    query_duplicate_groups,
    rows_from_cases,
    split_assignment_rows,
    split_summary,
    summarize_rows,
)
from fitz_gov.sdgp.vault import Vault


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--vault", type=Path, default=Path("data/sdgp_vault_v51_enriched"))
    p.add_argument("--out-dir", type=Path, default=Path("data/sdgp_v7_qa"))
    p.add_argument(
        "--cohort",
        type=str,
        default="v7",
        help="Dataset cohort for blind-label queue. Use 'all' to include every row.",
    )
    p.add_argument("--seed", type=int, default=20260522)
    p.add_argument("--train-ratio", type=float, default=0.8)
    p.add_argument("--validation-ratio", type=float, default=0.1)
    p.add_argument("--test-ratio", type=float, default=0.1)
    return p.parse_args()


def _cohort_cases(cases: list[dict[str, Any]], cohort: str) -> list[dict[str, Any]]:
    if cohort == "all":
        return list(cases)
    out = []
    for case in cases:
        meta = case.get("meta") if isinstance(case.get("meta"), dict) else {}
        if meta.get("dataset_version") == cohort:
            out.append(case)
    return out


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def main() -> int:
    args = parse_args()
    vault = Vault.open(args.vault)
    cases = list(vault.iter_cases())
    cohort_cases = _cohort_cases(cases, args.cohort)
    all_rows = rows_from_cases(cases)
    cohort_rows = rows_from_cases(cohort_cases)

    ratios = {
        "train": args.train_ratio,
        "validation": args.validation_ratio,
        "test": args.test_ratio,
    }
    assignments = assign_query_grouped_splits(all_rows, seed=args.seed, ratios=ratios)
    split_info = split_summary(all_rows, assignments)

    detector = GapDetector()
    counts = vault.cell_counts()
    gap_summary = {
        str(target): detector.coverage_summary(counts, target=target)
        for target in (20, 25, 30)
    }

    summary = {
        "vault": str(args.vault),
        "cohort": args.cohort,
        "seed": args.seed,
        "all_rows": summarize_rows(all_rows),
        "cohort_rows": summarize_rows(cohort_rows),
        "gap_summary": gap_summary,
        "duplicates": duplicate_summary(all_rows),
        "split_summary": split_info,
        "artifacts": {
            "report": "report.md",
            "query_duplicate_groups": "query_duplicate_groups.jsonl",
            "cross_label_query_groups": "cross_label_query_groups.jsonl",
            "split_assignments": "split_assignments.jsonl",
            "blind_label_queue": "blind_label_queue.jsonl",
            "blind_label_manifest": "blind_label_manifest.jsonl",
        },
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    _write_json(args.out_dir / "summary.json", summary)
    (args.out_dir / "report.md").write_text(markdown_report(summary), encoding="utf-8")
    (args.out_dir / "query_duplicate_groups.jsonl").write_text(
        jsonl_text(query_duplicate_groups(all_rows)),
        encoding="utf-8",
    )
    (args.out_dir / "cross_label_query_groups.jsonl").write_text(
        jsonl_text(cross_label_query_groups(all_rows)),
        encoding="utf-8",
    )
    (args.out_dir / "split_assignments.jsonl").write_text(
        jsonl_text(split_assignment_rows(all_rows, assignments)),
        encoding="utf-8",
    )
    cohort_assignments = {row.case_id: assignments[row.case_id] for row in cohort_rows}
    (args.out_dir / "blind_label_queue.jsonl").write_text(
        jsonl_text(blind_label_queue_rows(cohort_cases)),
        encoding="utf-8",
    )
    (args.out_dir / "blind_label_manifest.jsonl").write_text(
        jsonl_text(blind_label_manifest_rows(cohort_rows, cohort_assignments)),
        encoding="utf-8",
    )

    print("=== V7 QA audit ===")
    print(f"Vault      : {args.vault}")
    print(f"Out dir    : {args.out_dir}")
    print(f"Rows       : {summary['all_rows']['rows']}")
    print(f"Cohort     : {args.cohort} ({summary['cohort_rows']['rows']} rows)")
    print(
        "Duplicates : "
        f"ids={summary['duplicates']['duplicate_ids']['groups']} "
        f"inputs={summary['duplicates']['duplicate_exact_input']['groups']} "
        f"checker={summary['duplicates']['duplicate_checker_hash']['groups']} "
        f"query_groups={summary['duplicates']['exact_query_duplicates']['groups']} "
        f"cross_label_queries={summary['duplicates']['cross_label_query_duplicates']['groups']}"
    )
    print(
        "Splits     : "
        + ", ".join(
            f"{name}={summary['split_summary']['splits'][name]['rows']}"
            for name in ("train", "validation", "test")
        )
    )
    print(
        "Leakage    : "
        f"{summary['split_summary']['query_group_leakage']['groups']} query groups cross splits"
    )
    print(f"Blind queue: {len(cohort_cases)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
