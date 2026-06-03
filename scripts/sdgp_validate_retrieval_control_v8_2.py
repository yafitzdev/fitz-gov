"""Validate V8.2 retrieval-control labels from Codex subagent JSONL outputs.

This script is mechanical only: it checks shape, enum membership, coverage, and
high-risk combinations. It does not assign semantic labels.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any


RETRIEVAL_ACTIONS = {
    "answer_now",
    "retrieve_more",
    "broaden_search",
    "resolve_conflict",
    "ask_clarifying_question",
    "structured_lookup",
}
GAP_TYPES = {
    "none",
    "missing_specific_fact",
    "missing_timeframe",
    "missing_comparison_side",
    "missing_source_authority",
    "conflicting_values",
    "wrong_entity",
    "wrong_version_or_scope",
    "too_broad",
    "incomplete_enumeration",
    "unsupported_inference",
    "ambiguous_query",
}
ANSWERABILITY_SHAPES = {
    "single_fact",
    "explanation",
    "list",
    "exhaustive_list",
    "comparison",
    "timeline",
    "calculation",
    "yes_no",
    "summary",
    "citation_required",
    "exact_lookup",
}
RETRIEVAL_MODALITIES = {
    "unstructured_text",
    "structured_table",
    "code",
    "configuration",
    "log_trace",
    "pdf_layout",
    "mixed",
}

CATEGORICAL_FIELDS: tuple[tuple[str, set[str]], ...] = (
    ("retrieval_action", RETRIEVAL_ACTIONS),
    ("gap_type", GAP_TYPES),
    ("answerability_shape", ANSWERABILITY_SHAPES),
    ("preferred_retrieval_modality", RETRIEVAL_MODALITIES),
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
    parser.add_argument("--allow-partial", action="store_true")
    parser.add_argument("--max-examples", type=int, default=20)
    return parser.parse_args()


def read_cases(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            row = json.loads(raw)
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: case row must be an object")
            rows.append(row)
    return rows


def _short_context(path: Path, line_no: int) -> str:
    return f"{path.name}:{line_no}"


def read_label_files(label_dir: Path, glob: str) -> tuple[dict[int, dict[str, Any]], list[str]]:
    labels: dict[int, dict[str, Any]] = {}
    errors: list[str] = []
    for path in sorted(label_dir.glob(glob)):
        with path.open(encoding="utf-8") as handle:
            for line_no, raw in enumerate(handle, start=1):
                if not raw.strip():
                    continue
                context = _short_context(path, line_no)
                try:
                    row = json.loads(raw)
                except json.JSONDecodeError as exc:
                    errors.append(f"{context}: invalid JSON: {exc}")
                    continue
                if not isinstance(row, dict):
                    errors.append(f"{context}: label row must be an object")
                    continue
                row_index = row.get("row_index")
                if not isinstance(row_index, int):
                    errors.append(f"{context}: row_index must be an integer")
                    continue
                if row_index in labels:
                    errors.append(f"{context}: duplicate row_index {row_index}")
                    continue
                row["_source_file"] = path.name
                row["_source_line"] = line_no
                labels[row_index] = row
    return labels, errors


def _validate_probability(value: Any, context: str, errors: list[str], field: str) -> None:
    if not isinstance(value, int | float) or not math.isfinite(float(value)):
        errors.append(f"{context}: {field} must be a finite number")
        return
    if not 0.0 <= float(value) <= 1.0:
        errors.append(f"{context}: {field}={value!r} is outside 0.0..1.0")


def _validate_signals(value: Any, context: str, errors: list[str], field: str) -> None:
    if not isinstance(value, list) or not value:
        errors.append(f"{context}: {field}.signals must be a non-empty list")
        return
    if not all(isinstance(item, str) and item.strip() for item in value):
        errors.append(f"{context}: {field}.signals must contain non-empty strings")


def validate_retrieval_control(
    *,
    labels: dict[int, dict[str, Any]],
    cases: list[dict[str, Any]],
) -> tuple[list[str], Counter[str], Counter[str]]:
    errors: list[str] = []
    counts: Counter[str] = Counter()
    high_risk: Counter[str] = Counter()
    for row_index, label_row in sorted(labels.items()):
        context = f"{label_row.get('_source_file')}:{label_row.get('_source_line')}:row {row_index}"
        if row_index < 1 or row_index > len(cases):
            errors.append(f"{context}: row_index outside 1..{len(cases)}")
            continue
        case = cases[row_index - 1]
        case_id = label_row.get("case_id")
        if case_id != case.get("id"):
            errors.append(
                f"{context}: case_id mismatch got {case_id!r}, expected {case.get('id')!r}"
            )
        control = label_row.get("retrieval_control")
        if not isinstance(control, dict):
            errors.append(f"{context}: retrieval_control must be an object")
            continue
        if control.get("row_index") != row_index:
            errors.append(f"{context}: retrieval_control.row_index must match row_index")
        if not isinstance(control.get("labeler"), str) or not control.get("labeler"):
            errors.append(f"{context}: retrieval_control.labeler must be a non-empty string")

        kinds: dict[str, str] = {}
        for field, allowed in CATEGORICAL_FIELDS:
            block = control.get(field)
            if not isinstance(block, dict):
                errors.append(f"{context}: {field} must be an object")
                continue
            kind = block.get("kind")
            if kind not in allowed:
                errors.append(f"{context}: {field}.kind={kind!r} is not allowed")
            else:
                kinds[field] = str(kind)
                counts[f"{field}:{kind}"] += 1
            _validate_probability(block.get("confidence"), context, errors, f"{field}.confidence")
            rationale = block.get("rationale")
            if not isinstance(rationale, str) or not rationale.strip():
                errors.append(f"{context}: {field}.rationale must be a non-empty string")
            _validate_signals(block.get("signals"), context, errors, field)

        severity = control.get("evidence_failure_severity")
        if not isinstance(severity, dict):
            errors.append(f"{context}: evidence_failure_severity must be an object")
            continue
        _validate_probability(severity.get("score"), context, errors, "severity.score")
        _validate_probability(
            severity.get("confidence"), context, errors, "severity.confidence"
        )
        if not isinstance(severity.get("rationale"), str) or not severity.get("rationale"):
            errors.append(f"{context}: severity.rationale must be a non-empty string")
        _validate_signals(severity.get("signals"), context, errors, "severity")

        classification = (case.get("governance") or {}).get("classification")
        score = severity.get("score")
        action = kinds.get("retrieval_action")
        gap = kinds.get("gap_type")
        if classification == "TRUSTWORTHY":
            if isinstance(score, int | float) and float(score) > 0.45:
                high_risk["TRUSTWORTHY_severity_gt_0_45"] += 1
            if gap and gap != "none":
                high_risk["TRUSTWORTHY_gap_not_none"] += 1
        if classification == "ABSTAIN" and action == "answer_now":
            high_risk["ABSTAIN_answer_now"] += 1
        if classification == "DISPUTED" and action not in {None, "resolve_conflict"}:
            high_risk["DISPUTED_not_resolve_conflict"] += 1

    return errors, counts, high_risk


def validation_report(
    *,
    cases: list[dict[str, Any]],
    labels: dict[int, dict[str, Any]],
    read_errors: list[str],
) -> dict[str, Any]:
    validation_errors, counts, high_risk = validate_retrieval_control(
        labels=labels,
        cases=cases,
    )
    missing = [idx for idx in range(1, len(cases) + 1) if idx not in labels]
    return {
        "rows_total": len(cases),
        "labels_total": len(labels),
        "missing_total": len(missing),
        "missing_first": missing[:50],
        "read_errors": read_errors,
        "validation_errors": validation_errors,
        "counts": dict(counts),
        "high_risk": dict(high_risk),
    }


def main() -> int:
    args = parse_args()
    cases = read_cases(args.cases)
    labels, read_errors = read_label_files(args.label_dir, args.glob)
    report = validation_report(cases=cases, labels=labels, read_errors=read_errors)

    print("=== V8.2 retrieval-control validation ===")
    print(f"Cases       : {args.cases}")
    print(f"Label dir   : {args.label_dir}")
    print(f"Glob        : {args.glob}")
    print(f"Rows        : {report['rows_total']}")
    print(f"Labels      : {report['labels_total']}")
    print(f"Missing     : {report['missing_total']}")
    if report["missing_first"]:
        print(f"Missing head: {report['missing_first'][:args.max_examples]}")
    print(f"Read errors : {len(report['read_errors'])}")
    for err in report["read_errors"][: args.max_examples]:
        print(f"  {err}")
    print(f"Validation  : {len(report['validation_errors'])} errors")
    for err in report["validation_errors"][: args.max_examples]:
        print(f"  {err}")
    print("High risk   :")
    for key, count in sorted(report["high_risk"].items()):
        print(f"  {key:34s}: {count}")
    print("Counts      :")
    for key, count in sorted(report["counts"].items()):
        print(f"  {key:52s}: {count}")

    has_errors = bool(report["read_errors"] or report["validation_errors"])
    incomplete = report["missing_total"] > 0
    if has_errors or (incomplete and not args.allow_partial):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
