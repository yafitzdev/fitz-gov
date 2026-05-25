"""Prepare V8 taxonomy-gap generation batches for subagents.

This targets only the V8 primary gap patterns. It writes JSON batch specs with
preassigned `sdgp_v8_...` case IDs. Subagents write JSONL rows shaped as
`{"case_id":"...","case":{...}}`; the merge path should then run the normal
checker, training-schema completeness, dedup, and blind-label QA.
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

from fitz_gov.sdgp.prompts import build_prompt
from fitz_gov.sdgp.taxonomy import (
    PRIMARY_DOMAINS,
    Cell,
    Difficulty,
    Domain,
    GovernanceClass,
    TaxonomyPattern,
    V8_GAP_PATTERNS,
    governance_class_of,
)
from fitz_gov.sdgp.vault import Vault, drop_vault_fields


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--vault", type=Path, default=Path("data/sdgp_vault_v51_enriched"))
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/sdgp_handoff_v8_expand/subagent_batches"),
    )
    p.add_argument("--target-per-cell", type=int, default=5)
    p.add_argument("--total-slots", type=int, default=None)
    p.add_argument("--batch-size", type=int, default=30)
    p.add_argument("--n-few-shots", type=int, default=2)
    p.add_argument("--seed", type=int, default=20260525)
    p.add_argument("--start-batch", type=int, default=None)
    p.add_argument("--filter-pattern", type=str, default=None)
    p.add_argument("--filter-class", type=str, default=None)
    p.add_argument("--filter-difficulty", type=str, default=None)
    p.add_argument("--filter-domain", type=str, default=None)
    return p.parse_args()


def _patterns(args: argparse.Namespace) -> set[TaxonomyPattern]:
    patterns = set(V8_GAP_PATTERNS)
    if args.filter_pattern:
        patterns &= {TaxonomyPattern(args.filter_pattern)}
    if args.filter_class:
        cls = GovernanceClass(args.filter_class.upper())
        patterns = {p for p in patterns if governance_class_of(p) == cls}
    return patterns


def _domains(args: argparse.Namespace) -> set[Domain]:
    domains = set(PRIMARY_DOMAINS)
    if args.filter_domain:
        domains &= {Domain(args.filter_domain)}
    return domains


def _difficulties(args: argparse.Namespace) -> set[Difficulty]:
    difficulties = set(Difficulty)
    if args.filter_difficulty:
        difficulties &= {Difficulty(args.filter_difficulty)}
    return difficulties


def _target_cells(args: argparse.Namespace) -> list[Cell]:
    cells = [
        Cell(pattern=pattern, domain=domain, difficulty=difficulty)
        for pattern in sorted(_patterns(args), key=lambda p: p.value)
        for domain in sorted(_domains(args), key=lambda d: d.value)
        for difficulty in sorted(_difficulties(args), key=lambda d: d.value)
    ]
    return sorted(cells, key=lambda c: c.cell_id)


def _next_batch_number(out_dir: Path) -> int:
    nums = []
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


def _existing_suffixes(vault: Vault, out_dir: Path) -> dict[str, set[int]]:
    out: dict[str, set[int]] = defaultdict(set)
    sources: list[tuple[str, str]] = []
    for case in vault.iter_cases():
        sources.append(
            (
                str(case.get("taxonomy", {}).get("cell_id") or ""),
                str(case.get("id") or ""),
            )
        )
    for slot in _iter_existing_batch_slots(out_dir):
        sources.append((str(slot.get("cell_id") or ""), str(slot.get("case_id") or "")))

    for cell_id, case_id in sources:
        prefix = f"sdgp_v8_{cell_id}__"
        if not cell_id or not case_id.startswith(prefix):
            continue
        suffix = case_id.removeprefix(prefix)
        if suffix.isdigit():
            out[cell_id].add(int(suffix))
    return out


def _current_counts(vault: Vault, out_dir: Path) -> dict[str, int]:
    existing_ids = {str(case.get("id") or "") for case in vault.iter_cases()}
    counts = dict(vault.cell_counts())
    for slot in _iter_existing_batch_slots(out_dir):
        cell_id = str(slot.get("cell_id") or "")
        case_id = str(slot.get("case_id") or "")
        if cell_id and case_id and case_id not in existing_ids:
            counts[cell_id] = counts.get(cell_id, 0) + 1
    return counts


def _build_few_shot_index(vault: Vault) -> dict[str, dict[Any, list[dict[str, Any]]]]:
    by_pattern_domain: dict[tuple[TaxonomyPattern, Domain], list[dict[str, Any]]] = defaultdict(list)
    by_pattern: dict[TaxonomyPattern, list[dict[str, Any]]] = defaultdict(list)
    by_class: dict[GovernanceClass, list[dict[str, Any]]] = defaultdict(list)

    for case in vault.iter_cases():
        tax = case.get("taxonomy") if isinstance(case.get("taxonomy"), dict) else {}
        try:
            pattern = TaxonomyPattern(tax.get("pattern"))
        except (TypeError, ValueError):
            continue
        domain = None
        cell_id = str(tax.get("cell_id") or "")
        for candidate in Domain:
            if candidate.value in cell_id:
                domain = candidate
                break
        compact = drop_vault_fields(case)
        if domain is not None:
            by_pattern_domain[(pattern, domain)].append(compact)
        by_pattern[pattern].append(compact)
        by_class[governance_class_of(pattern)].append(compact)

    return {
        "by_pattern_domain": by_pattern_domain,
        "by_pattern": by_pattern,
        "by_class": by_class,
    }


def _few_shots_from_index(
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
    rng = random.Random(seed)
    return rng.sample(pool, min(n, len(pool)))


def _allocate_case_id(cell_id: str, suffixes: dict[str, set[int]]) -> str:
    used = suffixes[cell_id]
    idx = 0
    while idx in used:
        idx += 1
    used.add(idx)
    return f"sdgp_v8_{cell_id}__{idx}"


def _slot_prompt(base_prompt: str, case_id: str) -> str:
    return (
        base_prompt
        + "\n\n## Additional hard requirement\n\n"
        + f'- The top-level `"id"` MUST equal "{case_id}" exactly.\n'
        + '- The top-level `"version"` MUST equal "fitz-gov-8.0".\n'
        + '- `"meta.dataset_version"` MUST equal "v8".\n'
        + "- Do not add taxonomy subpattern fields or legacy report axes.\n"
        + "- Return one JSON object only; no markdown fences or prose.\n"
    )


def _make_slots(args: argparse.Namespace, vault: Vault) -> list[dict[str, Any]]:
    cells = _target_cells(args)
    counts = _current_counts(vault, args.out_dir)
    suffixes = _existing_suffixes(vault, args.out_dir)
    few_shot_index = _build_few_shot_index(vault)
    limit = args.total_slots
    slots: list[dict[str, Any]] = []

    remaining = {
        cell.cell_id: max(args.target_per_cell - int(counts.get(cell.cell_id, 0)), 0)
        for cell in cells
    }
    while any(v > 0 for v in remaining.values()):
        made_progress = False
        for cell in cells:
            if remaining[cell.cell_id] <= 0:
                continue
            if limit is not None and len(slots) >= limit:
                return slots
            case_id = _allocate_case_id(cell.cell_id, suffixes)
            prompt = build_prompt(
                cell,
                few_shot_examples=_few_shots_from_index(
                    few_shot_index,
                    cell,
                    n=args.n_few_shots,
                    seed=args.seed + len(slots),
                ),
            )
            slots.append(
                {
                    "case_id": case_id,
                    "cell_id": cell.cell_id,
                    "pattern": cell.pattern.value,
                    "governance_class": cell.governance_class.value,
                    "domain": cell.domain.value,
                    "difficulty": cell.difficulty.value,
                    "current": counts.get(cell.cell_id, 0),
                    "target": args.target_per_cell,
                    "prompt": _slot_prompt(prompt.text, case_id),
                }
            )
            remaining[cell.cell_id] -= 1
            made_progress = True
        if not made_progress:
            break
    return slots


def main() -> int:
    args = parse_args()
    vault = Vault.open(args.vault)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    slots = _make_slots(args, vault)
    start = args.start_batch if args.start_batch is not None else _next_batch_number(args.out_dir)

    print("=== Prepare V8 taxonomy-gap generation batches ===")
    print(f"Vault       : {args.vault} ({len(vault)} cases)")
    print(f"Target/cell : {args.target_per_cell}")
    print(f"Slots       : {len(slots)}")
    print(f"Batch size  : {args.batch_size}")
    print(f"Out dir     : {args.out_dir}")

    for i in range(0, len(slots), args.batch_size):
        batch_no = start + i // args.batch_size
        chunk = slots[i : i + args.batch_size]
        path = args.out_dir / f"batch_{batch_no:03d}.json"
        payload = {
            "batch_id": f"v8_taxonomy_gap_{batch_no:03d}",
            "expected_count": len(chunk),
            "output_path": str(
                Path("data/sdgp_handoff_v8_expand/subagent_outputs")
                / f"batch_{batch_no:03d}.jsonl"
            ),
            "instructions": (
                "Generate exactly one complete V8 JSON case per slot. Write JSONL rows "
                'with shape {"case_id":"...","case":{...}}. The output case_id '
                "set must exactly equal slots[].case_id. Use the current SDGP row "
                "shape; do not add subpattern fields or legacy report axes. Do not "
                "edit the vault."
            ),
            "slots": chunk,
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  {path}: {len(chunk)} slots")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
