"""Prepare blind Claude residual shards by subtracting LM Studio-completed rows.

Reads the active V8 blind queue and the partial LM Studio predictions, keeps only
queue rows whose case_id is NOT in the LM Studio output, and emits blind shards plus
a row_index_to_case_id map for downstream materialization. row_index is the original
queue line index (0-based), so the existing materialize/score scripts can be reused.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--queue",
        type=Path,
        default=Path("data/sdgp_v8_qa/blind_label_queue.jsonl"),
    )
    p.add_argument(
        "--lmstudio-predictions",
        type=Path,
        default=Path(
            "data/sdgp_v8_qa/blind_label_predictions_v8_target50_full_lmstudio_qwen36_35b_q5_20260526.jsonl"
        ),
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/sdgp_v8_qa/claude_remainder_blind"),
    )
    p.add_argument("--n-shards", type=int, default=30)
    return p.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line_no, raw in enumerate(fh, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}: line {line_no} is invalid JSON: {exc}") from exc
            if not isinstance(payload, dict):
                raise ValueError(f"{path}: line {line_no} is not a JSON object")
            rows.append(payload)
    return rows


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def blind_row(row_index: int, row: Mapping[str, Any]) -> dict[str, Any]:
    case_id = str(row.get("case_id") or "")
    input_payload = row.get("input")
    if not case_id:
        raise ValueError(f"queue row {row_index} has no case_id")
    if not isinstance(input_payload, dict):
        raise ValueError(f"queue row {row_index} has no input object")
    return {
        "row_index": row_index,
        "input": {
            "query": input_payload.get("query"),
            "contexts": input_payload.get("contexts"),
        },
        "task": (
            "Classify the query and retrieved contexts as ABSTAIN, DISPUTED, or "
            "TRUSTWORTHY. Do not infer from any hidden metadata."
        ),
    }


def main() -> int:
    args = parse_args()
    if args.n_shards < 1:
        raise ValueError("--n-shards must be >= 1")

    completed_case_ids: set[str] = set()
    for row in read_jsonl(args.lmstudio_predictions):
        case_id = str(row.get("case_id") or "")
        if not case_id:
            raise ValueError(f"{args.lmstudio_predictions}: prediction row missing case_id")
        completed_case_ids.add(case_id)
    print(f"LM Studio completed case_ids: {len(completed_case_ids)}")

    queue_rows = read_jsonl(args.queue)
    print(f"Active queue rows: {len(queue_rows)}")

    mapping_rows: list[dict[str, Any]] = []
    blind_rows: list[dict[str, Any]] = []
    kept = 0
    skipped = 0
    for row_index, row in enumerate(queue_rows):
        case_id = str(row.get("case_id") or "")
        if not case_id:
            raise ValueError(f"queue row {row_index} has no case_id")
        if case_id in completed_case_ids:
            skipped += 1
            continue
        mapping_rows.append({"row_index": row_index, "case_id": case_id})
        blind_rows.append(blind_row(row_index, row))
        kept += 1

    print(f"Kept residual rows: {kept}")
    print(f"Skipped (already labeled): {skipped}")

    out_dir = args.out_dir
    shards_dir = out_dir / "shards"

    base_size, remainder = divmod(len(blind_rows), args.n_shards)
    manifest_rows: list[dict[str, Any]] = []
    start = 0
    for shard_no in range(args.n_shards):
        shard_size = base_size + (1 if shard_no < remainder else 0)
        shard = blind_rows[start : start + shard_size]
        path = shards_dir / f"shard_{shard_no:02d}.jsonl"
        write_jsonl(path, shard)
        try:
            manifest_path = path.resolve().relative_to(Path.cwd().resolve())
        except ValueError:
            manifest_path = path
        manifest_rows.append(
            {
                "shard": shard_no,
                "path": str(manifest_path),
                "start": start,
                "rows": len(shard),
            }
        )
        start += shard_size

    write_jsonl(out_dir / "row_index_to_case_id.jsonl", mapping_rows)
    write_json(
        out_dir / "shard_manifest.json",
        {
            "total_rows": len(blind_rows),
            "n_shards": args.n_shards,
            "shards": manifest_rows,
        },
    )
    print(f"Wrote {len(blind_rows)} blind rows across {args.n_shards} shards")
    print(f"Output: {out_dir}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
