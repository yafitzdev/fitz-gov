"""Plan V8 primary taxonomy-pattern expansion across current domains.

Usage:
    python scripts/sdgp_plan_v8_taxonomy_expansion.py
    python scripts/sdgp_plan_v8_taxonomy_expansion.py --target-per-cell 25
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.taxonomy import (
    PRIMARY_DOMAINS,
    Cell,
    Difficulty,
    V8_GAP_PATTERNS,
    governance_class_of,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--target-per-cell", type=int, default=5)
    p.add_argument(
        "--output",
        type=Path,
        default=Path("docs/V8_TAXONOMY_EXPANSION_PLAN.md"),
    )
    return p.parse_args()


def _cells() -> list[Cell]:
    return [
        Cell(pattern=pattern, domain=domain, difficulty=difficulty)
        for pattern in V8_GAP_PATTERNS
        for domain in PRIMARY_DOMAINS
        for difficulty in Difficulty
    ]


def render(target_per_cell: int) -> str:
    cells = _cells()
    by_pattern = Counter(cell.pattern for cell in cells)
    grouped: dict[str, list[str]] = defaultdict(list)
    for cell in cells:
        grouped[cell.pattern.value].append(
            f"| {cell.cell_id} | {cell.governance_class.value} | {cell.domain.value} | {cell.difficulty.value} |"
        )

    lines: list[str] = [
        "# V8 Taxonomy Expansion Plan",
        "",
        "V8 adds the discovered governance gaps as first-class `taxonomy.pattern` values.",
        "It does not add subpattern fields and does not rewrite existing rows.",
        "",
        "## Summary",
        "",
        f"- New primary patterns: **{len(V8_GAP_PATTERNS)}**",
        f"- Current primary domains: **{len(PRIMARY_DOMAINS)}**",
        f"- Difficulties: **{len(Difficulty)}**",
        f"- New cells: **{len(cells)}**",
        f"- Probe target: **{target_per_cell} rows/cell = {len(cells) * target_per_cell} rows**",
        f"- Full V7-style parity at 25 rows/cell: **{len(cells) * 25} rows**",
        "",
        "## Pattern Targets",
        "",
        "| pattern | class | cells | probe rows |",
        "|---|---:|---:|---:|",
    ]
    for pattern in V8_GAP_PATTERNS:
        class_name = governance_class_of(pattern).value
        cell_count = by_pattern[pattern]
        lines.append(
            f"| `{pattern.value}` | {class_name} | {cell_count} | {cell_count * target_per_cell} |"
        )

    lines.extend(
        [
            "",
            "## Cells",
            "",
            "| cell_id | governance_class | domain | difficulty |",
            "|---|---|---|---|",
        ]
    )
    for pattern in V8_GAP_PATTERNS:
        lines.append(f"| **{pattern.value}** |  |  |  |")
        lines.extend(grouped[pattern.value])

    lines.extend(
        [
            "",
            "## Row Contract",
            "",
            "- Use the current SDGP row shape: `id`, `version`, `input`, `governance`, `taxonomy`, `routing`, `meta`, `evaluation`.",
            "- New rows use `version: \"fitz-gov-8.0\"` and `meta.dataset_version: \"v8\"`.",
            "- Do not add `taxonomy.subpattern`, `taxonomy.subpattern_cell_id`, `taxonomy.subpattern_description`, or `meta.introduced_in`.",
            "- Do not reintroduce `meta.domain`, `meta.subcategory`, `meta.reasoning_type`, `meta.query_type`, or `meta.evidence_pattern`.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    text = render(args.target_per_cell)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
