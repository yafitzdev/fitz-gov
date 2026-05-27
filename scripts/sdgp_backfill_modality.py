"""Backfill or verify row-level ``meta.modality`` in SDGP JSONL files.

The current V8 benchmark rows are unstructured-text governance rows. This
script labels that existing local dataset explicitly without changing labels,
taxonomy, routing, or evaluation fields.

Run from the fitz-gov project root:
    python scripts/sdgp_backfill_modality.py --jsonl data/fitz-gov/cases.jsonl
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.modality import DEFAULT_MODALITY, MODALITIES, set_modality


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--jsonl",
        type=Path,
        default=Path("data/fitz-gov/cases.jsonl"),
        help="Case JSONL file to update.",
    )
    parser.add_argument(
        "--modality",
        choices=MODALITIES,
        default=DEFAULT_MODALITY,
        help="Modality to require/backfill.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing different modality values instead of failing.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and report without writing changes.",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Do not create a timestamped backup before replacing the JSONL.",
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=Path("data/_workspaces/backups"),
        help="Directory for timestamped backups.",
    )
    return parser.parse_args()


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _iter_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            try:
                row = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: row must be a JSON object")
            rows.append(row)
    return rows


def _write_jsonl_atomic(path: Path, rows: list[dict[str, Any]]) -> None:
    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=str(path.parent),
        prefix=path.name + ".",
        suffix=".tmp",
        delete=False,
        newline="\n",
    )
    try:
        with tmp:
            for row in rows:
                tmp.write(json.dumps(row, ensure_ascii=False) + "\n")
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp.name, path)
    except Exception:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass
        raise


def _backup(path: Path, backup_dir: Path) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{path.stem}.before_modality_backfill_{_utc_stamp()}{path.suffix}"
    shutil.copy2(path, backup_path)
    return backup_path


def main() -> int:
    args = parse_args()
    if not args.jsonl.exists():
        print(f"ERROR: JSONL not found: {args.jsonl}", file=sys.stderr)
        return 1

    rows = _iter_rows(args.jsonl)
    changed = 0
    errors: list[str] = []
    for idx, row in enumerate(rows, start=1):
        try:
            if set_modality(row, args.modality, overwrite=args.overwrite):
                changed += 1
        except ValueError as exc:
            case_id = row.get("id") or row.get("case_id") or f"line {idx}"
            errors.append(f"{case_id}: {exc}")

    print("=== SDGP modality backfill ===")
    print(f"JSONL     : {args.jsonl}")
    print(f"Rows      : {len(rows)}")
    print(f"Modality  : {args.modality}")
    print(f"Changed   : {changed}")
    print(f"Dry run   : {args.dry_run}")

    if errors:
        print("\nERROR: modality validation failed:", file=sys.stderr)
        for error in errors[:20]:
            print(f"  - {error}", file=sys.stderr)
        if len(errors) > 20:
            print(f"  ... {len(errors) - 20} more", file=sys.stderr)
        return 1

    if args.dry_run:
        return 0
    if changed == 0:
        print("No write needed.")
        return 0

    backup_path = None
    if not args.no_backup:
        backup_path = _backup(args.jsonl, args.backup_dir)
    _write_jsonl_atomic(args.jsonl, rows)
    if backup_path:
        print(f"Backup    : {backup_path}")
    print("Wrote updated JSONL.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
