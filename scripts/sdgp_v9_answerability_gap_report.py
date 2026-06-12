"""Report V9 retrieval-control answerability-shape coverage gaps.

This tool prepares the targeted V9 generation queue. It counts existing rows by:

    governance_class x domain x difficulty x collapsed_answerability_shape

Default target is 100 total rows per cell, which corresponds to roughly 80
train rows per cell after the standard 80/10/10 split.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.retrieval_control_gap_detector import (  # noqa: E402
    CollapsedAnswerabilityShape,
    RetrievalControlCellFilter,
    RetrievalControlGap,
    RetrievalControlGapDetector,
    parse_retrieval_control_cell_id,
    retrieval_control_cell_counts,
)
from fitz_gov.sdgp.taxonomy import Difficulty, Domain, GovernanceClass  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=Path("data/fitz-gov/cases.jsonl"))
    target = parser.add_mutually_exclusive_group()
    target.add_argument(
        "--target-per-cell",
        type=int,
        default=100,
        help="Target total rows per V9 cell. Default 100.",
    )
    target.add_argument(
        "--target-train-per-cell",
        type=int,
        default=None,
        help="Desired train rows per cell; converted to total rows using --train-ratio.",
    )
    parser.add_argument("--train-ratio", type=float, default=0.8)
    parser.add_argument("--include-direct-answer", action="store_true")
    parser.add_argument("--filter-class", action="append", default=[])
    parser.add_argument("--filter-domain", action="append", default=[])
    parser.add_argument("--filter-difficulty", action="append", default=[])
    parser.add_argument("--filter-answerability-shape", action="append", default=[])
    parser.add_argument("--max-gaps", type=int, default=30)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            row = json.loads(raw)
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: expected JSON object")
            rows.append(row)
    return rows


def _enum_set(raw: list[str], enum_cls: type) -> set[Any] | None:
    if not raw:
        return None
    values = set()
    for value in raw:
        if enum_cls is GovernanceClass:
            values.add(enum_cls(value.upper()))
        else:
            values.add(enum_cls(value))
    return values


def _build_filter(args: argparse.Namespace) -> RetrievalControlCellFilter:
    return RetrievalControlCellFilter(
        classes=_enum_set(args.filter_class, GovernanceClass),
        domains=_enum_set(args.filter_domain, Domain),
        difficulties=_enum_set(args.filter_difficulty, Difficulty),
        answerability_shapes=_enum_set(
            args.filter_answerability_shape,
            CollapsedAnswerabilityShape,
        ),
        include_direct_answer=bool(args.include_direct_answer),
    )


def _target_per_cell(args: argparse.Namespace) -> int:
    if args.target_train_per_cell is None:
        return int(args.target_per_cell)
    if args.train_ratio <= 0.0 or args.train_ratio > 1.0:
        raise ValueError("--train-ratio must be in (0, 1]")
    return int(math.ceil(args.target_train_per_cell / args.train_ratio))


def _gap_row(gap: RetrievalControlGap) -> dict[str, Any]:
    cell = gap.cell
    return {
        "cell_id": cell.cell_id,
        "governance_class": cell.governance_class.value,
        "domain": cell.domain.value,
        "difficulty": cell.difficulty.value,
        "answerability_shape": cell.answerability_shape.value,
        "current": gap.current,
        "target": gap.target,
        "gap": gap.gap,
        "coverage_ratio": gap.coverage_ratio,
        "priority": gap.priority,
    }


def _shape_totals(counts: dict[str, int]) -> dict[str, int]:
    totals: Counter[str] = Counter()
    for cell_id, count in counts.items():
        try:
            cell = parse_retrieval_control_cell_id(cell_id)
        except ValueError:
            continue
        totals[cell.answerability_shape.value] += count
    return dict(sorted(totals.items()))


def build_report(
    *,
    cases: list[dict[str, Any]],
    target_per_cell: int,
    flt: RetrievalControlCellFilter,
) -> dict[str, Any]:
    counts = retrieval_control_cell_counts(cases)
    detector = RetrievalControlGapDetector()
    gaps = detector.rank(counts, target=target_per_cell, filter=flt)
    summary = detector.coverage_summary(counts, target=target_per_cell, filter=flt)
    return {
        "schema_version": 1,
        "release_track": "fitz-gov-v9",
        "matrix": ("governance_class x domain x difficulty x collapsed_answerability_shape"),
        "target_per_cell": target_per_cell,
        "rows_read": len(cases),
        "collapsed_answerability_totals": _shape_totals(counts),
        "summary": summary,
        "gaps": [_gap_row(gap) for gap in gaps],
    }


def markdown_report(report: dict[str, Any], *, max_gaps: int) -> str:
    lines = [
        "# V9 Answerability Gap Report",
        "",
        f"- Rows read: **{report['rows_read']:,}**",
        f"- Matrix: `{report['matrix']}`",
        f"- Target per cell: **{report['target_per_cell']:,}** total rows",
        f"- Cells considered: **{report['summary']['cells_considered']:,}**",
        f"- Cells at target: **{report['summary']['cells_at_target']:,}**",
        f"- Empty cells: **{report['summary']['cells_empty']:,}**",
        f"- Total gap to fill: **{report['summary']['total_gap_to_fill']:,}** rows",
        "",
        "## Collapsed Answerability Totals",
        "",
        "| Shape | Current rows | Gap to fill |",
        "|---|---:|---:|",
    ]
    by_shape = report["summary"]["by_answerability_shape"]
    totals = report["collapsed_answerability_totals"]
    for shape in sorted(by_shape):
        gap = by_shape[shape]["total_gap_to_fill"]
        lines.append(f"| `{shape}` | {totals.get(shape, 0):,} | {gap:,} |")

    lines.extend(
        [
            "",
            f"## Top {max_gaps} Gaps",
            "",
            "| Gap | Current | Target | Class | Domain | Difficulty | Shape |",
            "|---:|---:|---:|---|---|---|---|",
        ]
    )
    for gap in report["gaps"][:max_gaps]:
        lines.append(
            "| {gap} | {current} | {target} | `{cls}` | `{domain}` | `{difficulty}` | "
            "`{shape}` |".format(
                gap=gap["gap"],
                current=gap["current"],
                target=gap["target"],
                cls=gap["governance_class"],
                domain=gap["domain"],
                difficulty=gap["difficulty"],
                shape=gap["answerability_shape"],
            )
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    cases = read_jsonl(args.cases)
    target_per_cell = _target_per_cell(args)
    flt = _build_filter(args)
    report = build_report(cases=cases, target_per_cell=target_per_cell, flt=flt)

    print("=== V9 retrieval-control answerability gap report ===")
    print(f"Cases          : {args.cases}")
    print(f"Rows read      : {report['rows_read']:,}")
    print(f"Target/cell    : {target_per_cell:,}")
    print(f"Cells          : {report['summary']['cells_considered']:,}")
    print(f"Cells at target: {report['summary']['cells_at_target']:,}")
    print(f"Empty cells    : {report['summary']['cells_empty']:,}")
    print(f"Gap to fill    : {report['summary']['total_gap_to_fill']:,}")
    print("By shape:")
    totals = report["collapsed_answerability_totals"]
    for shape, row in report["summary"]["by_answerability_shape"].items():
        print(
            f"  {shape:22s} current={totals.get(shape, 0):6d} " f"gap={row['total_gap_to_fill']:6d}"
        )
    print(f"Top gaps: {len(report['gaps'][: args.max_gaps])}")
    for gap in report["gaps"][: args.max_gaps]:
        print(
            "  gap={gap:4d} current={current:4d} target={target:4d} "
            "{cls} {domain} {difficulty} {shape}".format(
                gap=gap["gap"],
                current=gap["current"],
                target=gap["target"],
                cls=gap["governance_class"],
                domain=gap["domain"],
                difficulty=gap["difficulty"],
                shape=gap["answerability_shape"],
            )
        )

    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Wrote JSON     : {args.out_json}")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(
            markdown_report(report, max_gaps=args.max_gaps),
            encoding="utf-8",
        )
        print(f"Wrote Markdown : {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
