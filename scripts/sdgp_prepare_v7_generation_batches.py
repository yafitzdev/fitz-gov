"""Prepare gap-ranked V7 generation batches for subagents.

This writes JSON batch specs containing concrete generation prompts and
preassigned case ids. Subagents write JSONL output; the parent process merges
only rows that pass the strict V7 training-schema checker.
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
        default=Path("data/sdgp_handoff_v7_expand/subagent_batches"),
    )
    p.add_argument("--target", type=int, default=20)
    p.add_argument("--total-slots", type=int, default=180)
    p.add_argument("--batch-size", type=int, default=30)
    p.add_argument("--n-few-shots", type=int, default=2)
    p.add_argument("--seed", type=int, default=20260522)
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


def _existing_suffixes(vault: Vault) -> dict[str, set[int]]:
    out: dict[str, set[int]] = defaultdict(set)
    for case in vault.iter_cases():
        cell_id = str(case.get("taxonomy", {}).get("cell_id") or "")
        cid = str(case.get("id") or "")
        prefix = f"sdgp_v7_{cell_id}__"
        if not cell_id or not cid.startswith(prefix):
            continue
        suffix = cid.removeprefix(prefix)
        if suffix.isdigit():
            out[cell_id].add(int(suffix))
    return out


def _iter_existing_batch_slots(out_dir: Path) -> list[dict[str, Any]]:
    slots: list[dict[str, Any]] = []
    for path in out_dir.glob("batch_*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for slot in data.get("slots", []):
            if not isinstance(slot, dict):
                continue
            slots.append(slot)
    return slots


def _reserve_existing_batches(out_dir: Path, suffixes: dict[str, set[int]]) -> None:
    for slot in _iter_existing_batch_slots(out_dir):
            cell_id = str(slot.get("cell_id") or "")
            case_id = str(slot.get("case_id") or "")
            prefix = f"sdgp_v7_{cell_id}__"
            if not cell_id or not case_id.startswith(prefix):
                continue
            suffix = case_id.removeprefix(prefix)
            if suffix.isdigit():
                suffixes[cell_id].add(int(suffix))


def _pending_batch_cell_counts(out_dir: Path, vault: Vault) -> dict[str, int]:
    existing_ids = {str(case.get("id") or "") for case in vault.iter_cases()}
    pending: dict[str, int] = defaultdict(int)
    for slot in _iter_existing_batch_slots(out_dir):
        cell_id = str(slot.get("cell_id") or "")
        case_id = str(slot.get("case_id") or "")
        if cell_id and case_id and case_id not in existing_ids:
            pending[cell_id] += 1
    return pending


def _read_excluded_case_ids(path: Path | None) -> set[str]:
    if path is None or not path.exists():
        return set()
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def _cell_counts_excluding(vault: Vault, excluded_case_ids: set[str]) -> dict[str, int]:
    if not excluded_case_ids:
        return dict(vault.cell_counts())
    counts: dict[str, int] = defaultdict(int)
    for case in vault.iter_cases():
        case_id = str(case.get("id") or "")
        if case_id in excluded_case_ids:
            continue
        cell_id = str(case.get("taxonomy", {}).get("cell_id") or "")
        if cell_id:
            counts[cell_id] += 1
    return dict(counts)


def _build_few_shot_index(vault: Vault) -> dict[str, dict[Any, list[dict[str, Any]]]]:
    """Index few-shot candidates once instead of scanning the vault per slot."""
    by_pattern_domain: dict[tuple[TaxonomyPattern, Domain], list[dict[str, Any]]] = defaultdict(list)
    by_pattern: dict[TaxonomyPattern, list[dict[str, Any]]] = defaultdict(list)
    by_class: dict[GovernanceClass, list[dict[str, Any]]] = defaultdict(list)

    for case in vault.iter_cases():
        tax = case.get("taxonomy") if isinstance(case.get("taxonomy"), dict) else {}
        pattern_s = tax.get("pattern")
        cell_id = str(tax.get("cell_id") or "")
        try:
            pattern = TaxonomyPattern(pattern_s)
        except (TypeError, ValueError):
            continue
        domain = None
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
    return f"sdgp_v7_{cell_id}__{idx}"


def _slot_prompt(base_prompt: str, case_id: str) -> str:
    return (
        base_prompt
        + "\n\n## Additional hard requirement\n\n"
        + f'- The top-level `"id"` MUST equal "{case_id}" exactly.\n'
        + "- Return one JSON object only; no markdown fences or prose.\n"
    )


def _make_slots(args: argparse.Namespace, vault: Vault) -> list[dict[str, Any]]:
    detector = GapDetector()
    excluded_case_ids = _read_excluded_case_ids(args.exclude_case_ids)
    cell_counts = _cell_counts_excluding(vault, excluded_case_ids)
    for cell_id, pending in _pending_batch_cell_counts(args.out_dir, vault).items():
        cell_counts[cell_id] = cell_counts.get(cell_id, 0) + pending
    gaps = detector.rank(cell_counts, target=args.target, filter=_build_filter(args))
    few_shot_index = _build_few_shot_index(vault)
    remaining = {gap.cell.cell_id: gap.gap for gap in gaps}
    suffixes = _existing_suffixes(vault)
    _reserve_existing_batches(args.out_dir, suffixes)
    slots: list[dict[str, Any]] = []

    while len(slots) < args.total_slots:
        made_progress = False
        for gap in gaps:
            if len(slots) >= args.total_slots:
                break
            if remaining.get(gap.cell.cell_id, 0) <= 0:
                continue
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

    slots = _make_slots(args, vault)
    start = args.start_batch if args.start_batch is not None else _next_batch_number(args.out_dir)

    print("=== Prepare V7 generation batches ===")
    print(f"Vault      : {args.vault} ({len(vault)} cases)")
    print(f"Target/cell: {args.target}")
    if args.exclude_case_ids:
        print(f"Excluded IDs: {args.exclude_case_ids}")
    print(f"Slots      : {len(slots)}")
    print(f"Batch size : {args.batch_size}")
    print(f"Out dir    : {args.out_dir}")

    for i in range(0, len(slots), args.batch_size):
        batch_no = start + i // args.batch_size
        chunk = slots[i : i + args.batch_size]
        path = args.out_dir / f"batch_{batch_no:03d}.json"
        payload = {
            "batch_id": f"v7_expand_{batch_no:03d}",
            "expected_count": len(chunk),
            "output_path": str(
                Path("data/sdgp_handoff_v7_expand/subagent_outputs") / f"batch_{batch_no:03d}.jsonl"
            ),
            "instructions": (
                "Generate exactly one complete V7 JSON case per slot. Write JSONL rows "
                'with shape {"case_id":"...","case":{...}}. The output case_id '
                "set must exactly equal slots[].case_id. No duplicates. Do not edit "
                "the vault."
            ),
            "slots": chunk,
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  {path}: {len(chunk)} slots")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
