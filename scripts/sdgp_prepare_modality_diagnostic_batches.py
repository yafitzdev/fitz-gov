"""Prepare structured/code modality diagnostic generation batches.

These batches are candidate-only. They are meant for Claude Code or another
subagent runner to generate rows outside the active vault, followed by normal
structural and blind-label QA.

Run from the fitz-gov project root:
    python scripts/sdgp_prepare_modality_diagnostic_batches.py --modality structured
    python scripts/sdgp_prepare_modality_diagnostic_batches.py --modality code
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.modality import validate_modality
from fitz_gov.sdgp.prompts import build_prompt
from fitz_gov.sdgp.taxonomy import (
    Cell,
    Difficulty,
    Domain,
    GovernanceClass,
    TaxonomyPattern,
    governance_class_of,
)


DEFAULT_PATTERNS: dict[str, tuple[TaxonomyPattern, ...]] = {
    "structured": (
        TaxonomyPattern.DIRECT_ANSWER,
        TaxonomyPattern.QUANTITATIVE_CONSENSUS,
        TaxonomyPattern.CONSISTENT_CHAIN,
        TaxonomyPattern.NUMERICAL_CONFLICT,
        TaxonomyPattern.VERDICT_CONFLICT,
        TaxonomyPattern.SCOPE_CONFLICT,
        TaxonomyPattern.MISSING_EXECUTION_RESULT,
        TaxonomyPattern.VERSION_BUILD_MISMATCH,
        TaxonomyPattern.WRONG_SPECIFICITY,
        TaxonomyPattern.EVIDENCE_ABSENT,
    ),
    "code": (
        TaxonomyPattern.DIRECT_ANSWER,
        TaxonomyPattern.CONSISTENT_CHAIN,
        TaxonomyPattern.RESOLVED_CANDIDATE_SELECTION,
        TaxonomyPattern.FACTUAL_CONTRADICTION,
        TaxonomyPattern.VERDICT_CONFLICT,
        TaxonomyPattern.AUTHORITY_STATUS_CONFLICT,
        TaxonomyPattern.MISSING_EXECUTION_RESULT,
        TaxonomyPattern.PARTIAL_OVERLAP,
        TaxonomyPattern.VERSION_BUILD_MISMATCH,
        TaxonomyPattern.WRONG_ENTITY,
    ),
}

DEFAULT_DOMAINS: dict[str, tuple[Domain, ...]] = {
    "structured": (Domain.ECONOMICS_FINANCE, Domain.TECHNOLOGY_COMPUTING),
    "code": (Domain.TECHNOLOGY_COMPUTING,),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modality", choices=("structured", "code"), required=True)
    parser.add_argument("--total-slots", type=int, default=300)
    parser.add_argument("--batch-size", type=int, default=30)
    parser.add_argument("--seed", type=int, default=20260527)
    parser.add_argument("--start-batch", type=int, default=None)
    parser.add_argument("--n-few-shots", type=int, default=2)
    parser.add_argument(
        "--patterns",
        type=str,
        default=None,
        help="Comma-separated taxonomy patterns. Defaults are modality-specific.",
    )
    parser.add_argument(
        "--domains",
        type=str,
        default=None,
        help="Comma-separated expert domains. Defaults are modality-specific.",
    )
    parser.add_argument(
        "--difficulties",
        type=str,
        default="easy,medium,hard",
        help="Comma-separated difficulties.",
    )
    parser.add_argument(
        "--probe-root",
        type=Path,
        default=Path("data/modality_probes"),
        help="Local 10-row probe root used for few-shots when available.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Batch-spec output dir; defaults under data/_workspaces/handoff.",
    )
    parser.add_argument(
        "--outputs-dir",
        type=Path,
        default=None,
        help="Output JSONL dir written into specs; defaults to sibling subagent_outputs.",
    )
    return parser.parse_args()


def _parse_patterns(value: str | None, modality: str) -> tuple[TaxonomyPattern, ...]:
    if value is None:
        return DEFAULT_PATTERNS[modality]
    return tuple(TaxonomyPattern(item.strip()) for item in value.split(",") if item.strip())


def _parse_domains(value: str | None, modality: str) -> tuple[Domain, ...]:
    if value is None:
        return DEFAULT_DOMAINS[modality]
    return tuple(Domain(item.strip()) for item in value.split(",") if item.strip())


def _parse_difficulties(value: str) -> tuple[Difficulty, ...]:
    return tuple(Difficulty(item.strip()) for item in value.split(",") if item.strip())


def _next_batch_number(out_dir: Path) -> int:
    nums = []
    for path in out_dir.glob("batch_*.json"):
        match = re.match(r"batch_(\d+)$", path.stem)
        if match:
            nums.append(int(match.group(1)))
    return max(nums, default=0) + 1


def _load_probe_rows(probe_root: Path, modality: str) -> list[dict[str, Any]]:
    path = probe_root / modality / "cases.jsonl"
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for raw in handle:
            if raw.strip():
                rows.append(json.loads(raw))
    return rows


def _build_few_shot_index(rows: list[dict[str, Any]]) -> dict[str, dict[Any, list[dict[str, Any]]]]:
    by_pattern_domain: dict[tuple[TaxonomyPattern, Domain], list[dict[str, Any]]] = defaultdict(list)
    by_pattern: dict[TaxonomyPattern, list[dict[str, Any]]] = defaultdict(list)
    by_class: dict[GovernanceClass, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        tax = row.get("taxonomy") if isinstance(row.get("taxonomy"), dict) else {}
        try:
            pattern = TaxonomyPattern(tax.get("pattern"))
        except (TypeError, ValueError):
            continue
        cell_id = str(tax.get("cell_id") or "")
        domain = None
        for candidate in Domain:
            if candidate.value in cell_id:
                domain = candidate
                break
        compact = {
            "id": row.get("id"),
            "input": row.get("input"),
            "taxonomy": row.get("taxonomy"),
            "governance": {
                "classification": row.get("governance", {}).get("classification"),
            },
            "meta": {"modality": row.get("meta", {}).get("modality")},
        }
        if domain is not None:
            by_pattern_domain[(pattern, domain)].append(compact)
        by_pattern[pattern].append(compact)
        by_class[governance_class_of(pattern)].append(compact)
    return {
        "by_pattern_domain": by_pattern_domain,
        "by_pattern": by_pattern,
        "by_class": by_class,
    }


def _few_shots(
    index: dict[str, dict[Any, list[dict[str, Any]]]],
    cell: Cell,
    *,
    n: int,
    seed: int,
) -> list[dict[str, Any]]:
    if n <= 0:
        return []
    pool: list[dict[str, Any]] = []
    pool.extend(index["by_pattern_domain"].get((cell.pattern, cell.domain), []))
    if len(pool) < n:
        pool.extend(index["by_pattern"].get(cell.pattern, []))
    if len(pool) < n:
        pool.extend(index["by_class"].get(governance_class_of(cell.pattern), []))
    if not pool:
        return []
    return random.Random(seed).sample(pool, min(n, len(pool)))


def _slot_prompt(base_prompt: str, *, case_id: str, modality: str) -> str:
    return (
        base_prompt
        + "\n\n## Additional hard requirement\n\n"
        + f'- The top-level `"id"` MUST equal "{case_id}" exactly.\n'
        + '- The top-level `"version"` MUST equal "fitz-gov-modality-diagnostic-0.1".\n'
        + '- `"meta.dataset_version"` MUST equal "v8".\n'
        + f'- `"meta.modality"` MUST equal "{modality}".\n'
        + "- This is candidate data only; do not imply it is already in the active vault.\n"
        + "- Do not add taxonomy subpattern fields, meta.introduced_in, source_type, "
        + "or old pre-SDGP report axes.\n"
        + "- Return one JSON object only; no markdown fences or prose.\n"
    )


def _cells(
    *,
    patterns: tuple[TaxonomyPattern, ...],
    domains: tuple[Domain, ...],
    difficulties: tuple[Difficulty, ...],
) -> list[Cell]:
    return [
        Cell(pattern=pattern, domain=domain, difficulty=difficulty)
        for pattern in patterns
        for domain in domains
        for difficulty in difficulties
    ]


def _make_slots(args: argparse.Namespace, cells: list[Cell]) -> list[dict[str, Any]]:
    modality = validate_modality(args.modality)
    few_shot_index = _build_few_shot_index(_load_probe_rows(args.probe_root, modality))
    slots: list[dict[str, Any]] = []
    suffixes: dict[str, int] = defaultdict(int)
    while len(slots) < args.total_slots:
        made_progress = False
        for cell in cells:
            if len(slots) >= args.total_slots:
                break
            suffix = suffixes[cell.cell_id]
            suffixes[cell.cell_id] += 1
            case_id = f"sdgp_{modality}_diag_{cell.cell_id}__{suffix:03d}"
            prompt = build_prompt(
                cell,
                few_shot_examples=_few_shots(
                    few_shot_index,
                    cell,
                    n=args.n_few_shots,
                    seed=args.seed + len(slots),
                ),
                modality=modality,
            )
            slots.append(
                {
                    "case_id": case_id,
                    "cell_id": cell.cell_id,
                    "modality": modality,
                    "pattern": cell.pattern.value,
                    "governance_class": cell.governance_class.value,
                    "domain": cell.domain.value,
                    "difficulty": cell.difficulty.value,
                    "prompt": _slot_prompt(prompt.text, case_id=case_id, modality=modality),
                }
            )
            made_progress = True
        if not made_progress:
            break
    return slots


def main() -> int:
    args = parse_args()
    modality = validate_modality(args.modality)
    patterns = _parse_patterns(args.patterns, modality)
    domains = _parse_domains(args.domains, modality)
    difficulties = _parse_difficulties(args.difficulties)
    cells = _cells(patterns=patterns, domains=domains, difficulties=difficulties)
    if not cells:
        print("ERROR: no cells selected", file=sys.stderr)
        return 1

    out_dir = args.out_dir or Path(
        f"data/_workspaces/handoff/sdgp_modality_{modality}_diagnostic_20260527/subagent_batches"
    )
    outputs_dir = args.outputs_dir or (out_dir.parent / "subagent_outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    slots = _make_slots(args, cells)
    start = args.start_batch if args.start_batch is not None else _next_batch_number(out_dir)

    print("=== Prepare modality diagnostic batches ===")
    print(f"Modality   : {modality}")
    print(f"Cells      : {len(cells)}")
    print(f"Slots      : {len(slots)}")
    print(f"Batch size : {args.batch_size}")
    print(f"Batch dir  : {out_dir}")
    print(f"Output dir : {outputs_dir}")

    for i in range(0, len(slots), args.batch_size):
        batch_no = start + i // args.batch_size
        chunk = slots[i : i + args.batch_size]
        path = out_dir / f"batch_{batch_no:03d}.json"
        payload = {
            "batch_id": f"modality_{modality}_diagnostic_{batch_no:03d}",
            "modality": modality,
            "expected_count": len(chunk),
            "output_path": str(outputs_dir / f"batch_{batch_no:03d}.jsonl"),
            "instructions": (
                "Generate exactly one complete SDGP JSON case per slot. Write JSONL rows "
                'with shape {"case_id":"...","case":{...}}. The output case_id set must '
                "exactly equal slots[].case_id. These are candidate diagnostic rows only; "
                "do not edit the active vault. Every case must use meta.modality "
                f"{modality!r} and meta.dataset_version 'v8'."
            ),
            "slots": chunk,
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  {path}: {len(chunk)} slots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
