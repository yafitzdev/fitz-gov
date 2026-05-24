"""Score blind-label predictions against the private V7 QA manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.blind_label import (
    blind_label_assessment_rows,
    blind_label_score_summary,
    bucketed_assessment_rows,
    case_ids_from_rows,
    disagreement_rows,
    markdown_score_report,
    review_queue_rows,
    second_pass_ledger_rows,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/sdgp_v7_qa/blind_label_manifest.jsonl"),
    )
    p.add_argument(
        "--predictions",
        type=Path,
        default=Path("data/sdgp_v7_qa/blind_label_predictions.jsonl"),
    )
    p.add_argument("--out-dir", type=Path, default=Path("data/sdgp_v7_qa"))
    p.add_argument(
        "--only-predicted",
        action="store_true",
        help="Score only manifest rows that have a prediction row. Use for sampled pilots.",
    )
    p.add_argument(
        "--ledger",
        type=Path,
        default=Path("data/sdgp_v7_qa/blind_label_second_pass_ledger.jsonl"),
    )
    p.add_argument("--update-ledger", action="store_true")
    p.add_argument("--run-id", type=str, default="blind_label")
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
                raise ValueError(f"{path}: line {line_no} is not valid JSON: {exc}") from exc
            if not isinstance(payload, dict):
                raise ValueError(f"{path}: line {line_no} is not a JSON object")
            rows.append(payload)
    return rows


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8"
    )


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def append_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("a", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            count += 1
    return count


def main() -> int:
    args = parse_args()
    manifest = read_jsonl(args.manifest)
    predictions = read_jsonl(args.predictions)
    if args.only_predicted:
        predicted_case_ids = case_ids_from_rows(predictions)
        manifest = [row for row in manifest if str(row.get("case_id") or "") in predicted_case_ids]
    assessments = blind_label_assessment_rows(manifest, predictions)
    summary = blind_label_score_summary(assessments, prediction_rows=predictions)
    validated, triage = bucketed_assessment_rows(assessments)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "blind_label_score_summary.json", summary)
    (args.out_dir / "blind_label_score_report.md").write_text(
        markdown_score_report(summary),
        encoding="utf-8",
    )
    write_jsonl(args.out_dir / "blind_label_assessments.jsonl", assessments)
    write_jsonl(args.out_dir / "blind_label_disagreements.jsonl", disagreement_rows(assessments))
    write_jsonl(args.out_dir / "blind_label_review_queue.jsonl", review_queue_rows(assessments))
    write_jsonl(args.out_dir / "blind_label_validated.jsonl", validated)
    write_jsonl(args.out_dir / "blind_label_triage.jsonl", triage)
    (args.out_dir / "blind_label_triage_case_ids.txt").write_text(
        "".join(f"{row['case_id']}\n" for row in triage),
        encoding="utf-8",
    )

    ledger_appended = 0
    if args.update_ledger:
        existing = case_ids_from_rows(read_jsonl(args.ledger)) if args.ledger.exists() else set()
        ledger_rows = [
            row
            for row in second_pass_ledger_rows(assessments, run_id=args.run_id)
            if str(row.get("case_id") or "") not in existing
        ]
        ledger_appended = append_jsonl(args.ledger, ledger_rows)

    print("=== Blind label score ===")
    print(f"Manifest     : {args.manifest}")
    print(f"Predictions  : {args.predictions}")
    print(f"Out dir      : {args.out_dir}")
    print(f"Scored       : {summary['scored_rows']} / {summary['total_manifest_rows']}")
    print(
        f"Agreement    : {summary['agree_rows']} / {summary['scored_rows']} ({summary['agreement_rate']})"
    )
    print(f"Disagreements: {summary['disagree_rows']}")
    print(
        "Missing/invalid/error: "
        f"{summary['missing_rows']}/{summary['invalid_rows']}/{summary['error_rows']}"
    )
    print(f"Validated   : {len(validated)}")
    print(f"Triage      : {len(triage)}")
    if args.update_ledger:
        print(f"Ledger      : appended {ledger_appended} rows to {args.ledger}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
