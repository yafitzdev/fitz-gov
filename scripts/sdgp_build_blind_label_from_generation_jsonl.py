"""Build blind-label QA files from generated SDGP JSONL rows without merging.

Generated row files must contain:

    {"case_id": "...", "case": {...}}

This is for candidate-row QA. The emitted manifest uses split="candidate";
real train/validation/test assignments still come from a full vault QA audit
after rows are accepted into the active vault.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.qa import (
    blind_label_manifest_rows,
    blind_label_queue_rows,
    jsonl_text,
    rows_from_cases,
    summarize_rows,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/sdgp_handoff_v8_expand/subagent_outputs"),
        help="Directory containing generated batch_*.jsonl files.",
    )
    p.add_argument("--glob", type=str, default="batch_*.jsonl")
    p.add_argument(
        "--qa-dir",
        type=Path,
        default=Path("data/sdgp_candidate_qa"),
        help="Directory to write blind_label_queue.jsonl and blind_label_manifest.jsonl.",
    )
    p.add_argument("--version", type=str, default="fitz-gov-8.0")
    p.add_argument("--dataset-version", type=str, default="v8")
    return p.parse_args()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: row must be a JSON object")
            rows.append(row)
    return rows


def _candidate_cases(
    files: list[Path],
    *,
    version: str,
    dataset_version: str,
) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    ids: list[str] = []
    for path in files:
        for row in _read_jsonl(path):
            case_id = row.get("case_id")
            case = row.get("case")
            if not isinstance(case_id, str) or not isinstance(case, dict):
                raise ValueError(f"{path}: expected every row to contain string case_id and object case")
            item = dict(case)
            item["id"] = case_id
            item["version"] = version
            meta = item.get("meta") if isinstance(item.get("meta"), dict) else {}
            item["meta"] = dict(meta)
            item["meta"]["dataset_version"] = dataset_version
            ids.append(case_id)
            cases.append(item)

    duplicates = sorted(case_id for case_id, count in Counter(ids).items() if count > 1)
    if duplicates:
        raise ValueError(f"duplicate case_id values in generated outputs: {duplicates[:10]}")
    return cases


def main() -> int:
    args = parse_args()
    files = sorted(args.out_dir.glob(args.glob))
    if not files:
        print(f"No files matched {args.out_dir / args.glob}", file=sys.stderr)
        return 2

    try:
        cases = _candidate_cases(
            files,
            version=args.version,
            dataset_version=args.dataset_version,
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    rows = rows_from_cases(cases)
    assignments = {row.case_id: "candidate" for row in rows}

    args.qa_dir.mkdir(parents=True, exist_ok=True)
    (args.qa_dir / "blind_label_queue.jsonl").write_text(
        jsonl_text(blind_label_queue_rows(cases)),
        encoding="utf-8",
    )
    (args.qa_dir / "blind_label_manifest.jsonl").write_text(
        jsonl_text(blind_label_manifest_rows(rows, assignments)),
        encoding="utf-8",
    )
    (args.qa_dir / "candidate_summary.json").write_text(
        json.dumps(
            {
                "source_dir": str(args.out_dir),
                "files": [str(path) for path in files],
                "summary": summarize_rows(rows),
            },
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    print("=== Build blind-label candidate QA ===")
    print(f"Source files: {len(files)}")
    print(f"Rows        : {len(cases)}")
    print(f"QA dir      : {args.qa_dir}")
    print(f"Queue       : {args.qa_dir / 'blind_label_queue.jsonl'}")
    print(f"Manifest    : {args.qa_dir / 'blind_label_manifest.jsonl'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
