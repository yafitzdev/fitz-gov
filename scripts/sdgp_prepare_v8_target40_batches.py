"""Prepare V8 whole-dataset target-fill generation batches.

This is the V8 companion to the older V7 batch-prep script. It ranks the
canonical SDGP cell space against a target count, then writes subagent batch
specs with preassigned `sdgp_v8_...` case IDs. Use it for additive V8 rows in
older V6/V7 taxonomy cells; generated rows must still use the current SDGP row
shape and the V8 cohort marker.
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

from fitz_gov.sdgp.gap_detector import CellFilter, GapDetector
from fitz_gov.sdgp.prompts import build_prompt
from fitz_gov.sdgp.taxonomy import (
    Difficulty,
    Domain,
    GovernanceClass,
    TaxonomyPattern,
    governance_class_of,
)
from fitz_gov.sdgp.vault import Vault, drop_vault_fields


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--vault", type=Path, default=Path("data/sdgp_vault_v51_enriched"))
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/sdgp_handoff_v8_target40/subagent_batches"),
    )
    p.add_argument(
        "--outputs-dir",
        type=Path,
        default=None,
        help="Output JSONL directory written into batch specs; defaults to sibling subagent_outputs.",
    )
    p.add_argument("--target", type=int, default=40)
    p.add_argument("--total-slots", type=int, default=None)
    p.add_argument("--batch-size", type=int, default=30)
    p.add_argument("--n-few-shots", type=int, default=2)
    p.add_argument("--seed", type=int, default=20260525)
    p.add_argument("--start-batch", type=int, default=None)
    p.add_argument("--filter-pattern", type=str, default=None)
    p.add_argument("--filter-class", type=str, default=None)
    p.add_argument("--filter-difficulty", type=str, default=None)
    p.add_argument("--filter-domain", type=str, default=None)
    p.add_argument(
        "--exclude-case-ids",
        type=Path,
        default=None,
        help="Optional newline-delimited case IDs to exclude from coverage counts.",
    )
    return p.parse_args()


def _build_filter(args: argparse.Namespace) -> CellFilter:
    flt = CellFilter()
    if args.filter_pattern:
        flt.patterns = {TaxonomyPattern(args.filter_pattern)}
    if args.filter_class:
        flt.classes = {GovernanceClass(args.filter_class.upper())}
    if args.filter_difficulty:
        flt.difficulties = {Difficulty(args.filter_difficulty)}
    if args.filter_domain:
        flt.domains = {Domain(args.filter_domain)}
    return flt


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


def _read_excluded_case_ids(path: Path | None) -> set[str]:
    if path is None or not path.exists():
        return set()
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def _cell_counts_excluding(vault: Vault, excluded_case_ids: set[str]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for case in vault.iter_cases():
        case_id = str(case.get("id") or "")
        if case_id in excluded_case_ids:
            continue
        cell_id = str(case.get("taxonomy", {}).get("cell_id") or "")
        if cell_id:
            counts[cell_id] += 1
    return dict(counts)


def _current_counts(vault: Vault, out_dir: Path, excluded_case_ids: set[str]) -> dict[str, int]:
    existing_ids = {str(case.get("id") or "") for case in vault.iter_cases()}
    counts = _cell_counts_excluding(vault, excluded_case_ids)
    for slot in _iter_existing_batch_slots(out_dir):
        cell_id = str(slot.get("cell_id") or "")
        case_id = str(slot.get("case_id") or "")
        if cell_id and case_id and case_id not in existing_ids:
            counts[cell_id] = counts.get(cell_id, 0) + 1
    return counts


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
    cell,
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
        + "- Use the current SDGP row shape only.\n"
        + "- Do not add taxonomy subpattern fields, meta.introduced_in, source_type, "
        + "or old pre-SDGP report axes.\n"
        + "- Return one JSON object only; no markdown fences or prose.\n"
    )


def _make_slots(args: argparse.Namespace, vault: Vault) -> list[dict[str, Any]]:
    excluded_case_ids = _read_excluded_case_ids(args.exclude_case_ids)
    counts = _current_counts(vault, args.out_dir, excluded_case_ids)
    gaps = GapDetector().rank(counts, target=args.target, filter=_build_filter(args))
    few_shot_index = _build_few_shot_index(vault)
    suffixes = _existing_suffixes(vault, args.out_dir)
    remaining = {gap.cell.cell_id: gap.gap for gap in gaps}
    limit = args.total_slots
    slots: list[dict[str, Any]] = []

    while any(v > 0 for v in remaining.values()):
        made_progress = False
        for gap in gaps:
            if remaining.get(gap.cell.cell_id, 0) <= 0:
                continue
            if limit is not None and len(slots) >= limit:
                return slots
            case_id = _allocate_case_id(gap.cell.cell_id, suffixes)
            prompt = build_prompt(
                gap.cell,
                few_shot_examples=_few_shots_from_index(
                    few_shot_index,
                    gap.cell,
                    n=args.n_few_shots,
                    seed=args.seed + len(slots),
                ),
            )
            slots.append(
                {
                    "case_id": case_id,
                    "cell_id": gap.cell.cell_id,
                    "pattern": gap.cell.pattern.value,
                    "governance_class": gap.cell.governance_class.value,
                    "domain": gap.cell.domain.value,
                    "difficulty": gap.cell.difficulty.value,
                    "current": gap.current,
                    "target": gap.target,
                    "prompt": _slot_prompt(prompt.text, case_id),
                }
            )
            remaining[gap.cell.cell_id] -= 1
            made_progress = True
        if not made_progress:
            break
    return slots


def main() -> int:
    args = parse_args()
    vault = Vault.open(args.vault)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir = args.outputs_dir or (args.out_dir.parent / "subagent_outputs")

    slots = _make_slots(args, vault)
    start = args.start_batch if args.start_batch is not None else _next_batch_number(args.out_dir)

    print("=== Prepare V8 target-fill generation batches ===")
    print(f"Vault       : {args.vault} ({len(vault)} cases)")
    print(f"Target/cell : {args.target}")
    if args.exclude_case_ids:
        print(f"Excluded IDs: {args.exclude_case_ids}")
    print(f"Slots       : {len(slots)}")
    print(f"Batch size  : {args.batch_size}")
    print(f"Batch dir   : {args.out_dir}")
    print(f"Output dir  : {outputs_dir}")

    for i in range(0, len(slots), args.batch_size):
        batch_no = start + i // args.batch_size
        chunk = slots[i : i + args.batch_size]
        path = args.out_dir / f"batch_{batch_no:03d}.json"
        payload = {
            "batch_id": f"v8_target_fill_{batch_no:03d}",
            "expected_count": len(chunk),
            "output_path": str(outputs_dir / f"batch_{batch_no:03d}.jsonl"),
            "instructions": (
                "Generate exactly one complete V8 JSON case per slot. Write JSONL rows "
                'with shape {"case_id":"...","case":{...}}. The output case_id '
                "set must exactly equal slots[].case_id. Use the current SDGP row "
                "shape with version fitz-gov-8.0 and meta.dataset_version v8. Do not "
                "add taxonomy subpattern fields, compatibility shims, source_type, or "
                "old pre-SDGP report axes. Do not edit the vault."
            ),
            "slots": chunk,
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  {path}: {len(chunk)} slots")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
