"""Prepare slim V9 answerability subagent specs from full batch specs.

The normal V9 batch specs include long per-slot prompts and few-shot examples.
Those are useful for one-off generation, but they make each 30-row spec large
enough to stall some workers. This tool preserves the target contract while
removing prompt payloads. It writes candidate-only handoff specs and never
mutates the active vault.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.taxonomy import (  # noqa: E402
    PATTERN_DESCRIPTIONS,
    GovernanceClass,
    patterns_of,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path("data/_workspaces/handoff/v9_answerability/subagent_batches"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/_workspaces/handoff/v9_answerability/slim_subagent_batches"),
    )
    parser.add_argument(
        "--outputs-dir",
        type=Path,
        default=Path("data/_workspaces/handoff/v9_answerability/subagent_outputs"),
    )
    parser.add_argument("--start-batch", type=int, required=True)
    parser.add_argument("--end-batch", type=int, required=True)
    parser.add_argument(
        "--slots-per-shard",
        type=int,
        default=0,
        help="When positive, split each source batch into shard specs of this many slots.",
    )
    return parser.parse_args()


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected JSON object")
    return data


def _patterns_by_class() -> dict[str, list[dict[str, str]]]:
    return {
        cls.value: [
            {"pattern": pattern.value, "description": PATTERN_DESCRIPTIONS[pattern]}
            for pattern in patterns_of(cls)
        ]
        for cls in GovernanceClass
    }


def _slim_slot(slot: dict[str, Any], patterns: dict[str, list[dict[str, str]]]) -> dict[str, Any]:
    keys = [
        "case_id",
        "v9_cell_id",
        "governance_class",
        "domain",
        "difficulty",
        "collapsed_answerability_shape",
        "allowed_detailed_answerability_shapes",
        "current",
        "target",
    ]
    slim = {key: slot[key] for key in keys if key in slot}
    governance_class = str(slim["governance_class"])
    slim["allowed_taxonomy_patterns"] = patterns[governance_class]
    return slim


def _source_number(path: Path) -> int:
    match = re.fullmatch(r"batch_(\d+)", path.stem)
    if match is None:
        raise ValueError(f"{path}: expected batch_NNN.json filename")
    return int(match.group(1))


def _write_spec(
    *,
    out_dir: Path,
    outputs_dir: Path,
    source_payload: dict[str, Any],
    source_no: int,
    slots: list[dict[str, Any]],
    suffix: str = "",
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    name = f"batch_{source_no:03d}{suffix}"
    payload = {
        "batch_id": f"{source_payload.get('batch_id', f'v9_answerability_{source_no:03d}')}{suffix}",
        "source_batch": f"batch_{source_no:03d}",
        "expected_count": len(slots),
        "output_path": str(outputs_dir / f"{name}.jsonl"),
        "instructions": (
            "Generate exactly one complete V9 SDGP candidate row per slot. Output JSONL "
            'wrapper rows shaped {"case_id":"...","case":{...}}. Use canonical row '
            "fields only: id, version, input, governance, taxonomy, routing, meta, "
            "evaluation."
        ),
        "slots": slots,
    }
    path = out_dir / f"{name}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> int:
    args = parse_args()
    if args.end_batch < args.start_batch:
        raise SystemExit("--end-batch must be >= --start-batch")
    if args.slots_per_shard < 0:
        raise SystemExit("--slots-per-shard must be >= 0")

    patterns = _patterns_by_class()
    written = 0
    slots_written = 0
    print("=== Prepare V9 slim subagent specs ===")
    print(f"Source dir     : {args.source_dir}")
    print(f"Spec out dir   : {args.out_dir}")
    print(f"Output row dir : {args.outputs_dir}")
    print(f"Batch range    : {args.start_batch}-{args.end_batch}")
    print(f"Slots/shard    : {args.slots_per_shard or 'none'}")

    for source_no in range(args.start_batch, args.end_batch + 1):
        source_path = args.source_dir / f"batch_{source_no:03d}.json"
        payload = _read_json(source_path)
        if _source_number(source_path) != source_no:
            raise ValueError(f"{source_path}: unexpected source number")
        slots = [
            _slim_slot(slot, patterns)
            for slot in payload.get("slots", [])
            if isinstance(slot, dict)
        ]
        if not slots:
            raise ValueError(f"{source_path}: no slots found")
        if args.slots_per_shard:
            for shard_idx, start in enumerate(range(0, len(slots), args.slots_per_shard), 1):
                shard_slots = slots[start : start + args.slots_per_shard]
                path = _write_spec(
                    out_dir=args.out_dir,
                    outputs_dir=args.outputs_dir,
                    source_payload=payload,
                    source_no=source_no,
                    slots=shard_slots,
                    suffix=f"_part{shard_idx}",
                )
                written += 1
                slots_written += len(shard_slots)
                print(f"  {path}: {len(shard_slots)} slots")
        else:
            path = _write_spec(
                out_dir=args.out_dir,
                outputs_dir=args.outputs_dir,
                source_payload=payload,
                source_no=source_no,
                slots=slots,
            )
            written += 1
            slots_written += len(slots)
            print(f"  {path}: {len(slots)} slots")

    print(f"Written specs  : {written}")
    print(f"Slots written  : {slots_written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
