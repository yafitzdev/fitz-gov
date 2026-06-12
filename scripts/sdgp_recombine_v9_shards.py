"""Recombine 10-row V9 shard outputs into normal 30-row batch files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

CANONICAL_CASE_FIELDS = {
    "id",
    "version",
    "input",
    "governance",
    "taxonomy",
    "routing",
    "meta",
    "evaluation",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-batch", type=int, required=True)
    parser.add_argument("--end-batch", type=int, required=True)
    parser.add_argument(
        "--spec-dir",
        type=Path,
        default=Path("data/_workspaces/handoff/v9_answerability/slim_subagent_shards"),
    )
    parser.add_argument(
        "--shard-dir",
        type=Path,
        default=Path("data/_workspaces/handoff/v9_answerability/subagent_shard_outputs"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/_workspaces/handoff/v9_answerability/subagent_outputs"),
    )
    parser.add_argument("--parts", type=int, default=3)
    return parser.parse_args()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected JSON object")
    return data


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            data = json.loads(line)
            if not isinstance(data, dict):
                raise ValueError(f"{path}:{line_no}: expected JSON object")
            rows.append(data)
    return rows


def validate_row(path: Path, line_no: int, row: dict[str, Any]) -> None:
    case_id = row.get("case_id")
    case = row.get("case")
    if not isinstance(case_id, str) or not case_id:
        raise ValueError(f"{path}:{line_no}: missing wrapper case_id")
    if not isinstance(case, dict):
        raise ValueError(f"{path}:{line_no}: missing wrapper case")
    if case.get("id") != case_id:
        raise ValueError(f"{path}:{line_no}: case.id does not match case_id")
    fields = set(case)
    if fields != CANONICAL_CASE_FIELDS:
        extra = sorted(fields - CANONICAL_CASE_FIELDS)
        missing = sorted(CANONICAL_CASE_FIELDS - fields)
        raise ValueError(
            f"{path}:{line_no}: non-canonical case fields; extra={extra}, missing={missing}"
        )


def recombine_batch(args: argparse.Namespace, batch_no: int) -> int:
    combined: list[dict[str, Any]] = []
    for part_no in range(1, args.parts + 1):
        spec_path = args.spec_dir / f"batch_{batch_no:03d}_part{part_no}.json"
        shard_path = args.shard_dir / f"batch_{batch_no:03d}_part{part_no}.jsonl"
        spec = read_json(spec_path)
        expected_ids = [slot["case_id"] for slot in spec.get("slots", []) if isinstance(slot, dict)]
        if not expected_ids:
            raise ValueError(f"{spec_path}: no slot case IDs found")
        rows = read_jsonl(shard_path)
        for line_no, row in enumerate(rows, 1):
            validate_row(shard_path, line_no, row)
        got_ids = [str(row["case_id"]) for row in rows]
        if got_ids != expected_ids:
            raise ValueError(
                f"{shard_path}: case IDs do not match spec order; "
                f"expected={len(expected_ids)}, got={len(got_ids)}"
            )
        print(f"  {shard_path.name}: {len(rows)} rows")
        combined.extend(rows)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.out_dir / f"batch_{batch_no:03d}.jsonl"
    out_path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in combined)
        + "\n",
        encoding="utf-8",
    )
    print(f"  wrote {out_path}: {len(combined)} rows")
    return len(combined)


def main() -> int:
    args = parse_args()
    if args.end_batch < args.start_batch:
        raise SystemExit("--end-batch must be >= --start-batch")
    total = 0
    print("=== Recombine V9 shards ===")
    print(f"Batch range: {args.start_batch}-{args.end_batch}")
    for batch_no in range(args.start_batch, args.end_batch + 1):
        total += recombine_batch(args, batch_no)
    print(f"Rows written: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
