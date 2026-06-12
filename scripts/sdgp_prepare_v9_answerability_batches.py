"""Prepare V9 answerability-shape generation batches for subagents.

This writes batch specs for the V9 retrieval-control matrix:

    governance_class x domain x difficulty x collapsed_answerability_shape

Generated rows remain candidate-only until structural checks and blind-label QA
pass. This script does not mutate the active vault.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.retrieval_control_gap_detector import (  # noqa: E402
    CollapsedAnswerabilityShape,
    RetrievalControlCell,
    RetrievalControlCellFilter,
    RetrievalControlGapDetector,
    cell_for_case,
    detailed_answerability_shapes_for,
    retrieval_control_cell_counts,
)
from fitz_gov.sdgp.taxonomy import (  # noqa: E402
    PATTERN_DESCRIPTIONS,
    Difficulty,
    Domain,
    GovernanceClass,
    TaxonomyPattern,
    patterns_of,
)
from fitz_gov.sdgp.vault import VAULT_KEY, drop_vault_fields  # noqa: E402


SHAPE_GUIDANCE = {
    CollapsedAnswerabilityShape.SYNTHESIS_ANSWER: (
        "The query asks for an explanation, mechanism, rationale, cause, summary, "
        "or representative synthesis. Use detailed answerability_shape.kind "
        "`explanation` or `summary`."
    ),
    CollapsedAnswerabilityShape.SET_ANSWER: (
        "The query asks for multiple items, a list, requirements, parameters, "
        "coverage of a set, or all applicable entries. Use detailed "
        "`list` or `exhaustive_list`."
    ),
    CollapsedAnswerabilityShape.STRUCTURED_REASONING: (
        "The query requires comparing sides, ordering events/states over time, "
        "or deterministic calculation/aggregation. Use detailed `comparison`, "
        "`timeline`, or `calculation`."
    ),
    CollapsedAnswerabilityShape.DIRECT_ANSWER: (
        "The query asks for a direct fact, exact lookup, yes/no verdict, or "
        "citation-grade direct support."
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=Path("data/fitz-gov/cases.jsonl"))
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/_workspaces/handoff/v9_answerability/subagent_batches"),
    )
    parser.add_argument(
        "--outputs-dir",
        type=Path,
        default=None,
        help="Output JSONL directory written into specs; defaults to sibling subagent_outputs.",
    )
    target = parser.add_mutually_exclusive_group()
    target.add_argument("--target-per-cell", type=int, default=100)
    target.add_argument("--target-train-per-cell", type=int, default=None)
    parser.add_argument("--train-ratio", type=float, default=0.8)
    parser.add_argument("--total-slots", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=30)
    parser.add_argument("--n-few-shots", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20260604)
    parser.add_argument("--start-batch", type=int, default=None)
    parser.add_argument("--include-direct-answer", action="store_true")
    parser.add_argument("--filter-class", action="append", default=[])
    parser.add_argument("--filter-domain", action="append", default=[])
    parser.add_argument("--filter-difficulty", action="append", default=[])
    parser.add_argument("--filter-answerability-shape", action="append", default=[])
    return parser.parse_args()


def read_cases(path: Path) -> list[dict[str, Any]]:
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


def _target_per_cell(args: argparse.Namespace) -> int:
    if args.target_train_per_cell is None:
        return int(args.target_per_cell)
    if args.train_ratio <= 0.0 or args.train_ratio > 1.0:
        raise ValueError("--train-ratio must be in (0, 1]")
    return int(math.ceil(args.target_train_per_cell / args.train_ratio))


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


def _next_batch_number(out_dir: Path) -> int:
    nums: list[int] = []
    for path in out_dir.glob("batch_*.json"):
        match = re.match(r"batch_(\d+)$", path.stem)
        if match:
            nums.append(int(match.group(1)))
    return max(nums, default=0) + 1


def _iter_existing_batch_slots(out_dir: Path) -> list[dict[str, Any]]:
    slots: list[dict[str, Any]] = []
    for path in out_dir.glob("batch_*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for slot in data.get("slots", []):
            if isinstance(slot, dict):
                slots.append(slot)
    return slots


def _current_counts(cases: list[dict[str, Any]], out_dir: Path) -> dict[str, int]:
    existing_case_ids = {str(case.get("id") or "") for case in cases}
    counts = retrieval_control_cell_counts(cases)
    for slot in _iter_existing_batch_slots(out_dir):
        cell_id = str(slot.get("v9_cell_id") or slot.get("cell_id") or "")
        case_id = str(slot.get("case_id") or "")
        if cell_id and case_id and case_id not in existing_case_ids:
            counts[cell_id] = counts.get(cell_id, 0) + 1
    return counts


def _existing_suffixes(cases: list[dict[str, Any]], out_dir: Path) -> dict[str, set[int]]:
    out: dict[str, set[int]] = defaultdict(set)
    sources: list[tuple[str, str]] = []
    for case in cases:
        cell = cell_for_case(case)
        if cell is not None:
            sources.append((cell.cell_id, str(case.get("id") or "")))
    for slot in _iter_existing_batch_slots(out_dir):
        sources.append(
            (
                str(slot.get("v9_cell_id") or slot.get("cell_id") or ""),
                str(slot.get("case_id") or ""),
            )
        )

    for cell_id, case_id in sources:
        prefix = f"sdgp_v9_{cell_id}__"
        if not cell_id or not case_id.startswith(prefix):
            continue
        suffix = case_id.removeprefix(prefix)
        if suffix.isdigit():
            out[cell_id].add(int(suffix))
    return out


def _compact_case(case: dict[str, Any]) -> dict[str, Any]:
    compact = drop_vault_fields(case)
    compact.pop(VAULT_KEY, None)
    return compact


def _build_few_shot_index(
    cases: list[dict[str, Any]],
) -> dict[str, dict[Any, list[dict[str, Any]]]]:
    by_shape_class_domain: dict[
        tuple[CollapsedAnswerabilityShape, GovernanceClass, Domain], list[dict[str, Any]]
    ] = defaultdict(list)
    by_shape_class: dict[
        tuple[CollapsedAnswerabilityShape, GovernanceClass], list[dict[str, Any]]
    ] = defaultdict(list)
    by_shape: dict[CollapsedAnswerabilityShape, list[dict[str, Any]]] = defaultdict(list)
    by_class: dict[GovernanceClass, list[dict[str, Any]]] = defaultdict(list)

    for case in cases:
        cell = cell_for_case(case)
        if cell is None:
            continue
        compact = _compact_case(case)
        by_shape_class_domain[
            (cell.answerability_shape, cell.governance_class, cell.domain)
        ].append(compact)
        by_shape_class[(cell.answerability_shape, cell.governance_class)].append(compact)
        by_shape[cell.answerability_shape].append(compact)
        by_class[cell.governance_class].append(compact)

    return {
        "by_shape_class_domain": by_shape_class_domain,
        "by_shape_class": by_shape_class,
        "by_shape": by_shape,
        "by_class": by_class,
    }


def _few_shots_from_index(
    index: dict[str, dict[Any, list[dict[str, Any]]]],
    cell: RetrievalControlCell,
    *,
    n: int,
    seed: int,
) -> list[dict[str, Any]]:
    if n <= 0:
        return []
    pool: list[dict[str, Any]] = []
    pool.extend(
        index["by_shape_class_domain"].get(
            (cell.answerability_shape, cell.governance_class, cell.domain),
            [],
        )
    )
    if len(pool) < n:
        pool.extend(
            index["by_shape_class"].get(
                (cell.answerability_shape, cell.governance_class),
                [],
            )
        )
    if len(pool) < n:
        pool.extend(index["by_shape"].get(cell.answerability_shape, []))
    if len(pool) < n:
        pool.extend(index["by_class"].get(cell.governance_class, []))
    if not pool:
        return []
    rng = random.Random(seed)
    return rng.sample(pool, min(n, len(pool)))


def _allocate_case_id(cell_id: str, suffixes: dict[str, set[int]]) -> str:
    used = suffixes[cell_id]
    idx = 0
    while idx in used:
        idx += 1
    used.add(idx)
    return f"sdgp_v9_{cell_id}__{idx}"


def _allowed_patterns_text(governance_class: GovernanceClass) -> str:
    lines = []
    for pattern in patterns_of(governance_class):
        lines.append(f"- `{pattern.value}`: {PATTERN_DESCRIPTIONS[pattern]}")
    return "\n".join(lines)


def _few_shots_text(examples: list[dict[str, Any]]) -> str:
    if not examples:
        return "No few-shot examples are provided for this slot."
    lines = []
    for idx, example in enumerate(examples, start=1):
        lines.append(f"### Example {idx}\n")
        lines.append(json.dumps(example, ensure_ascii=False, indent=2))
    return "\n\n".join(lines)


def _slot_prompt(
    *,
    cell: RetrievalControlCell,
    case_id: str,
    few_shot_examples: list[dict[str, Any]],
) -> str:
    detailed_shapes = detailed_answerability_shapes_for(cell.answerability_shape)
    allowed_patterns = _allowed_patterns_text(cell.governance_class)
    return f"""You are generating one candidate row for fitz-gov V9.

Return exactly one complete JSON object. Do not use markdown fences or prose.

## Required output row shape

The top-level case object must use the canonical SDGP shape:

- `id`
- `version`
- `input`
- `governance`
- `taxonomy`
- `routing`
- `meta`
- `evaluation`

Do not add compatibility shims or old report axes. Forbidden fields include
`taxonomy.subpattern`, `taxonomy.subpattern_cell_id`, `taxonomy.subpattern_description`,
`meta.introduced_in`, `meta.domain`, `meta.subcategory`, `meta.reasoning_type`,
`meta.query_type`, `meta.evidence_pattern`, and `source_type`.

## Hard target cell

- `id` MUST be exactly `{case_id}`.
- `version` MUST be exactly `fitz-gov-9.0`.
- `meta.dataset_version` MUST be exactly `v9`.
- `meta.modality` MUST be one of `unstructured`, `structured`, or `code`,
  chosen to match the actual evidence representation in `input.contexts`.
- `governance.classification` MUST be exactly `{cell.governance_class.value}`.
- `routing.expert_fired` MUST be exactly `{cell.domain.value}`.
- `meta.difficulty` MUST be exactly `{cell.difficulty.value}`.
- V9 collapsed answerability target is `{cell.answerability_shape.value}`.
- `routing.retrieval_control.answerability_shape.kind` MUST be one of:
  {", ".join(f"`{item}`" for item in detailed_shapes)}

## Answerability guidance

{SHAPE_GUIDANCE[cell.answerability_shape]}

## Taxonomy pattern

Choose exactly one canonical `taxonomy.pattern` from the allowed patterns below.
It must match the target governance class. Set `taxonomy.cell_id` to:

`{{taxonomy.pattern}}__{cell.domain.value}__{cell.difficulty.value}`

Allowed patterns:

{allowed_patterns}

## Retrieval-control requirements

Include `routing.query_contract` and `routing.retrieval_control`.

`routing.retrieval_control` must include:

- `retrieval_action.kind`
- `gap_type.kind`
- `answerability_shape.kind`
- `preferred_retrieval_modality.kind`
- `evidence_failure_severity.score`
- confidence, rationale, and signals for every retrieval-control subfield
- `labeler: "codex_subagent_v9_generation"`

Use detailed V8.2 retrieval-control labels, not the collapsed V9 label, inside
the row. The collapsed label is only the generation target.

## Evidence construction

Create a realistic query and retrieved contexts for the target domain and
difficulty. Make the evidence state genuinely imply the target governance
classification:

- TRUSTWORTHY: evidence is sufficient and non-conflicting enough to answer.
- DISPUTED: evidence contains unresolved incompatible facts, values, statuses,
  authority positions, scopes, or conclusions that a careful answer should not
  collapse into one answer.
- ABSTAIN: evidence is missing, wrong, too broad, underspecified, or otherwise
  insufficient for the specific query.

For DISPUTED rows, do not make the apparent conflict trivially resolved by
source hierarchy, a direct correction, or the query itself asking why sources
differ. If the retrieved contexts explain the disagreement well enough to answer
the user, the row is TRUSTWORTHY, not DISPUTED. A valid DISPUTED row should make
an independent blind labeler hesitate between materially incompatible answers,
not merely notice that one weak source used sloppy wording.

The query must genuinely require the target answerability shape. Do not write a
direct factual lookup when the target is `{cell.answerability_shape.value}`.

## Few-shot examples

{_few_shots_text(few_shot_examples)}
"""


def _make_slots(args: argparse.Namespace, cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    target_per_cell = _target_per_cell(args)
    flt = _build_filter(args)
    counts = _current_counts(cases, args.out_dir)
    gaps = RetrievalControlGapDetector().rank(counts, target=target_per_cell, filter=flt)
    suffixes = _existing_suffixes(cases, args.out_dir)
    few_shot_index = _build_few_shot_index(cases)
    remaining = {gap.cell.cell_id: gap.gap for gap in gaps}
    limit = args.total_slots
    slots: list[dict[str, Any]] = []

    while any(value > 0 for value in remaining.values()):
        made_progress = False
        for gap in gaps:
            cell_id = gap.cell.cell_id
            if remaining.get(cell_id, 0) <= 0:
                continue
            if limit is not None and len(slots) >= limit:
                return slots
            case_id = _allocate_case_id(cell_id, suffixes)
            few_shots = _few_shots_from_index(
                few_shot_index,
                gap.cell,
                n=args.n_few_shots,
                seed=args.seed + len(slots),
            )
            detailed_shapes = detailed_answerability_shapes_for(gap.cell.answerability_shape)
            slots.append(
                {
                    "case_id": case_id,
                    "v9_cell_id": cell_id,
                    "governance_class": gap.cell.governance_class.value,
                    "domain": gap.cell.domain.value,
                    "difficulty": gap.cell.difficulty.value,
                    "collapsed_answerability_shape": gap.cell.answerability_shape.value,
                    "allowed_detailed_answerability_shapes": list(detailed_shapes),
                    "current": gap.current,
                    "target": gap.target,
                    "prompt": _slot_prompt(
                        cell=gap.cell,
                        case_id=case_id,
                        few_shot_examples=few_shots,
                    ),
                }
            )
            remaining[cell_id] -= 1
            made_progress = True
        if not made_progress:
            break
    return slots


def main() -> int:
    args = parse_args()
    cases = read_cases(args.cases)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir = args.outputs_dir or (args.out_dir.parent / "subagent_outputs")
    target_per_cell = _target_per_cell(args)
    slots = _make_slots(args, cases)
    start = args.start_batch if args.start_batch is not None else _next_batch_number(args.out_dir)

    print("=== Prepare V9 answerability generation batches ===")
    print(f"Cases       : {args.cases} ({len(cases):,} rows)")
    print(f"Target/cell : {target_per_cell:,}")
    print(f"Slots       : {len(slots):,}")
    print(f"Batch size  : {args.batch_size}")
    print(f"Batch dir   : {args.out_dir}")
    print(f"Output dir  : {outputs_dir}")

    for i in range(0, len(slots), args.batch_size):
        batch_no = start + i // args.batch_size
        chunk = slots[i : i + args.batch_size]
        path = args.out_dir / f"batch_{batch_no:03d}.json"
        payload = {
            "batch_id": f"v9_answerability_{batch_no:03d}",
            "expected_count": len(chunk),
            "output_path": str(outputs_dir / f"batch_{batch_no:03d}.jsonl"),
            "instructions": (
                "Generate exactly one complete V9 JSON case per slot. Write JSONL rows "
                'with shape {"case_id":"...","case":{...}}. The output case_id set '
                "must exactly equal slots[].case_id. Use version fitz-gov-9.0, "
                "meta.dataset_version v9, canonical SDGP row shape, and populated "
                "routing.query_contract plus routing.retrieval_control. Do not edit "
                "the active vault."
            ),
            "slots": chunk,
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  {path}: {len(chunk)} slots")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
