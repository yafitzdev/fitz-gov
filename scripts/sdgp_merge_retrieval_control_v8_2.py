"""Merge validated V8.2 retrieval-control labels into the local fitz-gov vault.

This script is mechanical only: labels must already exist as subagent JSONL
outputs. The script validates complete coverage, backs up the vault JSONL, and
adds `routing.retrieval_control` to each case.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sdgp_validate_retrieval_control_v8_2 import (  # noqa: E402
    read_cases,
    read_label_files,
    validation_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=Path("data/fitz-gov/cases.jsonl"))
    parser.add_argument(
        "--label-dir",
        type=Path,
        default=Path("data/_workspaces/retrieval_control_v8_2/subagent_labels"),
    )
    parser.add_argument("--glob", type=str, default="*.jsonl")
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=Path("data/_workspaces/retrieval_control_v8_2/backups"),
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> int:
    args = parse_args()
    cases = read_cases(args.cases)
    labels, read_errors = read_label_files(args.label_dir, args.glob)
    report = validation_report(cases=cases, labels=labels, read_errors=read_errors)

    print("=== Merge V8.2 retrieval-control labels ===")
    print(f"Cases     : {args.cases}")
    print(f"Label dir : {args.label_dir}")
    print(f"Rows      : {report['rows_total']}")
    print(f"Labels    : {report['labels_total']}")
    print(f"Missing   : {report['missing_total']}")
    print(f"Errors    : {len(report['read_errors']) + len(report['validation_errors'])}")
    print(f"Dry run   : {args.dry_run}")

    if report["read_errors"] or report["validation_errors"] or report["missing_total"]:
        print("ERROR: refusing to merge incomplete or invalid retrieval-control labels", file=sys.stderr)
        if report["missing_first"]:
            print(f"First missing row indexes: {report['missing_first'][:20]}", file=sys.stderr)
        for err in (report["read_errors"] + report["validation_errors"])[:20]:
            print(f"  {err}", file=sys.stderr)
        return 1

    merged: list[dict[str, Any]] = []
    for row_index, case in enumerate(cases, start=1):
        row = dict(case)
        routing = dict(row.get("routing") or {})
        control = labels[row_index]["retrieval_control"]
        routing["retrieval_control"] = control
        row["routing"] = routing
        merged.append(row)

    if args.dry_run:
        print("Dry run: no file written.")
        return 0

    args.backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = args.backup_dir / f"cases.before_v8_2_retrieval_control_{stamp}.jsonl"
    shutil.copy2(args.cases, backup)
    write_jsonl(args.cases, merged)
    print(f"Backup : {backup}")
    print(f"Merged : {len(merged)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
