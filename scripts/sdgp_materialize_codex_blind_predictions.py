"""Materialize blind Codex subagent shard predictions for SDGP scoring."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping


VALID_LABELS = {"ABSTAIN", "DISPUTED", "TRUSTWORTHY"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--blind-dir",
        type=Path,
        default=Path("data/sdgp_qa_v8_target40/codex_subagent_blind"),
        help="Directory containing shards, shard_manifest.json, row_index_to_case_id.jsonl, and predictions/.",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path(
            "data/sdgp_qa_v8_target40/codex_subagent_blind/"
            "blind_label_predictions_codex_subagents_combined.jsonl"
        ),
    )
    p.add_argument("--provider", default="codex_subagents")
    p.add_argument("--provider-version", default="gpt-5-codex-blind-shards")
    return p.parse_args()


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


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


def required_int(row: Mapping[str, Any], key: str, path: Path) -> int:
    value = row.get(key)
    if not isinstance(value, int):
        raise ValueError(f"{path}: expected integer {key}, got {value!r}")
    return value


def load_index_map(path: Path) -> dict[int, str]:
    mapping: dict[int, str] = {}
    for row in read_jsonl(path):
        row_index = required_int(row, "row_index", path)
        case_id = str(row.get("case_id") or "")
        if not case_id:
            raise ValueError(f"{path}: row_index {row_index} has no case_id")
        if row_index in mapping:
            raise ValueError(f"{path}: duplicate row_index {row_index}")
        mapping[row_index] = case_id
    return mapping


def validate_prediction_rows(
    *,
    prediction_path: Path,
    expected_indices: set[int],
) -> list[dict[str, Any]]:
    predictions = read_jsonl(prediction_path)
    seen: set[int] = set()
    out: list[dict[str, Any]] = []
    for row in predictions:
        row_index = required_int(row, "row_index", prediction_path)
        if row_index in seen:
            raise ValueError(f"{prediction_path}: duplicate row_index {row_index}")
        seen.add(row_index)
        label = str(row.get("predicted_label") or "").strip().upper()
        if label not in VALID_LABELS:
            raise ValueError(
                f"{prediction_path}: row_index {row_index} has invalid predicted_label {label!r}"
            )
        out.append(
            {
                "row_index": row_index,
                "predicted_label": label,
                "rationale": str(row.get("rationale") or ""),
            }
        )

    missing = sorted(expected_indices - seen)
    extra = sorted(seen - expected_indices)
    if missing or extra:
        preview_missing = ", ".join(str(i) for i in missing[:10])
        preview_extra = ", ".join(str(i) for i in extra[:10])
        raise ValueError(
            f"{prediction_path}: row_index mismatch; "
            f"missing={len(missing)} [{preview_missing}], extra={len(extra)} [{preview_extra}]"
        )
    return out


def main() -> int:
    args = parse_args()
    blind_dir = args.blind_dir
    shard_manifest = read_json(blind_dir / "shard_manifest.json")
    index_map = load_index_map(blind_dir / "row_index_to_case_id.jsonl")

    materialized: list[dict[str, Any]] = []
    generated_at = dt.datetime.now(dt.UTC).isoformat()
    for shard in shard_manifest["shards"]:
        shard_no = int(shard["shard"])
        shard_path = blind_dir / "shards" / f"shard_{shard_no:02d}.jsonl"
        prediction_path = blind_dir / "predictions" / f"shard_{shard_no:02d}_predictions.jsonl"
        input_rows = read_jsonl(shard_path)
        expected_indices = {required_int(row, "row_index", shard_path) for row in input_rows}
        if len(expected_indices) != len(input_rows):
            raise ValueError(f"{shard_path}: duplicate row_index in input shard")
        prediction_rows = validate_prediction_rows(
            prediction_path=prediction_path,
            expected_indices=expected_indices,
        )
        for row in prediction_rows:
            row_index = int(row["row_index"])
            case_id = index_map.get(row_index)
            if not case_id:
                raise ValueError(f"{prediction_path}: no case_id map for row_index {row_index}")
            materialized.append(
                {
                    "case_id": case_id,
                    "predicted_label": row["predicted_label"],
                    "rationale": row["rationale"],
                    "provider": args.provider,
                    "provider_version": args.provider_version,
                    "generated_at": generated_at,
                    "source_shard": shard_no,
                }
            )

    expected_total = int(shard_manifest["total_rows"])
    if len(materialized) != expected_total:
        raise ValueError(f"expected {expected_total} predictions, got {len(materialized)}")

    write_jsonl(args.out, materialized)
    print(f"Materialized {len(materialized)} predictions")
    print(f"Output: {args.out}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
