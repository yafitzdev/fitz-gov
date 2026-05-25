"""Blind-label execution and scoring utilities for SDGP QA.

The QA audit emits a blind-label queue without gold labels. This module turns
those queue rows into provider prompts, parses independent labels, and scores
the resulting predictions against the private manifest.
"""

from __future__ import annotations

import json
import random
import re
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Sequence

from .providers import GenerateRequest, Provider

VALID_LABELS = ("ABSTAIN", "DISPUTED", "TRUSTWORTHY")
_LABEL_RE = re.compile(r"\b(ABSTAIN|DISPUTED|TRUSTWORTHY)\b", re.IGNORECASE)
_LABEL_FIELD_RE = re.compile(
    r"\b(?:label|predicted_label|classification)\b\s*[:=]\s*[\"']?"
    r"(ABSTAIN|DISPUTED|TRUSTWORTHY)\b",
    re.IGNORECASE,
)
_LEADING_LABEL_RE = re.compile(r"^\s*(ABSTAIN|DISPUTED|TRUSTWORTHY)\b", re.IGNORECASE)
_FINAL_LABEL_RE = re.compile(
    r"\b(?:final|correct)\s+(?:label|classification|answer)\s+(?:is|:)\s*[\"']?"
    r"(ABSTAIN|DISPUTED|TRUSTWORTHY)\b",
    re.IGNORECASE,
)
_LABEL_SHOULD_RE = re.compile(
    r"\b(?:label|classification|answer)\s+(?:should\s+be|is|:)\s*[\"']?"
    r"(ABSTAIN|DISPUTED|TRUSTWORTHY)\b(?!\s*(?:,|/|or\b))",
    re.IGNORECASE,
)
_LABEL_DECISION_RE = re.compile(
    r"\b(?:(ABSTAIN|DISPUTED|TRUSTWORTHY)\s+"
    r"(?:is|seems|looks)\s+(?:the\s+)?(?:appropriate|correct|best|right|explicitly\s+triggered)"
    r"|fits\s+(ABSTAIN|DISPUTED|TRUSTWORTHY)"
    r"|->\s*(ABSTAIN|DISPUTED|TRUSTWORTHY)\b)",
    re.IGNORECASE,
)

BLIND_LABEL_SYSTEM = (
    "You are a strict label validator for the fitz-gov RAG governance benchmark. "
    "Given only a query and retrieved contexts, classify whether a downstream answer "
    "should be ABSTAIN, DISPUTED, or TRUSTWORTHY. Use ABSTAIN when the contexts do "
    "not contain enough current, specific, in-scope evidence to answer. Use DISPUTED "
    "when the contexts provide incompatible answer candidates, including conflicting "
    "numbers, definitions, time states, scope/jurisdiction/population variants for "
    "an underspecified query, or high-authority vs low-authority contradiction. Do "
    "not resolve a conflict by picking the higher-authority source; surface the "
    "dispute unless the conflict is irrelevant to the queried answer. Use "
    "TRUSTWORTHY only when the contexts consistently and sufficiently support one "
    "grounded answer. For current/latest/as-of-now questions, old release notes or "
    "date-limited contexts are not enough unless they explicitly cover the requested "
    "period. Return compact JSON only: "
    '{"label":"ABSTAIN|DISPUTED|TRUSTWORTHY","rationale":"short reason"}. '
    "Do not think step by step. Do not restate the question, contexts, or allowed labels. "
    "The first character of your response must be { and the last character must be }."
)


@dataclass(frozen=True, slots=True)
class ParsedBlindLabel:
    label: str | None
    rationale: str
    parse_ok: bool
    parse_error: str | None = None


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def normalize_label(value: Any) -> str | None:
    label = str(value or "").strip().upper()
    return label if label in VALID_LABELS else None


def case_id_from_row(row: Mapping[str, Any]) -> str:
    return str(row.get("case_id") or row.get("id") or "")


def case_ids_from_rows(rows: Iterable[Mapping[str, Any]]) -> set[str]:
    return {case_id for row in rows if (case_id := case_id_from_row(row))}


def _contexts_from_row(row: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    input_block = row.get("input") if isinstance(row.get("input"), Mapping) else {}
    raw_contexts = input_block.get("contexts") or row.get("contexts") or []
    if not isinstance(raw_contexts, Sequence) or isinstance(raw_contexts, (str, bytes)):
        return []
    return [ctx for ctx in raw_contexts if isinstance(ctx, Mapping)]


def build_blind_label_prompt(row: Mapping[str, Any]) -> str:
    """Build a gold-label-free prompt from a blind queue row or case-like dict."""
    input_block = row.get("input") if isinstance(row.get("input"), Mapping) else {}
    query = str(input_block.get("query") or row.get("query") or "")
    lines = [f"Question: {query}", "", "Retrieved contexts:"]
    for idx, ctx in enumerate(_contexts_from_row(row), start=1):
        cid = str(ctx.get("id") or f"ctx_{idx:03d}")
        text = str(ctx.get("text") or "")
        lines.append(f"[{idx}] {cid}: {text}")
    lines.extend(
        [
            "",
            "Return compact JSON only with keys label and rationale.",
            "Allowed labels: ABSTAIN, DISPUTED, TRUSTWORTHY.",
            "Do not include analysis, markdown, or any text outside the JSON object.",
        ]
    )
    return "\n".join(lines)


def parse_blind_label_response(raw: str) -> ParsedBlindLabel:
    """Parse a provider response into one of the three governance labels.

    JSON is preferred, but direct one-word labels and label-plus-rationale text
    are accepted so weaker local models can still be used.
    """
    text = str(raw or "").strip()
    if not text:
        return ParsedBlindLabel(None, "", False, "empty response")

    payload = _last_json_object(text)
    if payload is not None:
        label = normalize_label(
            payload.get("label") or payload.get("predicted_label") or payload.get("classification")
        )
        rationale = str(
            payload.get("rationale") or payload.get("reason") or payload.get("explanation") or ""
        ).strip()
        if label:
            return ParsedBlindLabel(label, rationale, True, None)
        return ParsedBlindLabel(None, rationale, False, "JSON response has no valid label")

    for pattern in (
        _LABEL_FIELD_RE,
        _FINAL_LABEL_RE,
        _LABEL_SHOULD_RE,
        _LABEL_DECISION_RE,
        _LEADING_LABEL_RE,
    ):
        match = pattern.search(text)
        if not match:
            continue
        label = normalize_label(next((g for g in match.groups() if g), None))
        return ParsedBlindLabel(label, text, True, None)
    return ParsedBlindLabel(None, text, False, "response has no valid label")


def _last_json_object(text: str) -> Mapping[str, Any] | None:
    """Return the last parseable JSON object in text, if any.

    LM Studio models sometimes wrap the requested JSON in a thinking block that
    also contains JSON examples. A greedy regex can span multiple objects and
    fail. Raw decoding from every opening brace lets us keep the final object
    without accepting arbitrary label words from the reasoning trace.
    """
    decoder = json.JSONDecoder()
    objects: list[Mapping[str, Any]] = []
    for idx, char in enumerate(text):
        if char != "{":
            continue
        try:
            payload, _ = decoder.raw_decode(text[idx:])
        except json.JSONDecodeError:
            continue
        if isinstance(payload, Mapping) and not _is_placeholder_json(payload):
            objects.append(payload)
    return objects[-1] if objects else None


def _is_placeholder_json(payload: Mapping[str, Any]) -> bool:
    rationale = str(
        payload.get("rationale") or payload.get("reason") or payload.get("explanation") or ""
    ).strip()
    return rationale.lower() in {"short reason", "...", "reason"}


def sample_queue_rows(
    queue_rows: Sequence[Mapping[str, Any]],
    *,
    sample_size: int,
    seed: int,
    excluded_case_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Return a reproducible random sample, excluding already-audited cases."""
    if sample_size < 0:
        raise ValueError("sample_size must be non-negative")
    excluded = excluded_case_ids or set()
    eligible = [dict(row) for row in queue_rows if case_id_from_row(row) not in excluded]
    rng = random.Random(seed)
    if sample_size >= len(eligible):
        rng.shuffle(eligible)
        return eligible
    return rng.sample(eligible, sample_size)


def label_queue_row(
    row: Mapping[str, Any],
    provider: Provider,
    *,
    max_tokens: int = 2048,
    temperature: float = 0.0,
) -> dict[str, Any]:
    """Run one blind-label queue row through a provider and return an audit row."""
    case_id = str(row.get("case_id") or "")
    started = time.perf_counter()
    generated_at = utcnow_iso()
    raw = ""
    error: str | None = None
    parsed = ParsedBlindLabel(None, "", False, None)
    try:
        raw = provider.generate(
            GenerateRequest(
                prompt=build_blind_label_prompt(row),
                system=BLIND_LABEL_SYSTEM,
                max_tokens=max_tokens,
                temperature=temperature,
                metadata={"case_id": case_id, "task": "blind_label"},
            )
        )
        parsed = parse_blind_label_response(raw)
    except Exception as exc:  # Provider implementations raise several concrete types.
        error = f"{type(exc).__name__}: {exc}"
        parsed = ParsedBlindLabel(None, "", False, "provider error")

    return {
        "case_id": case_id,
        "predicted_label": parsed.label,
        "rationale": parsed.rationale,
        "parse_ok": parsed.parse_ok,
        "parse_error": parsed.parse_error,
        "raw_response": raw,
        "provider": getattr(provider, "name", type(provider).__name__),
        "provider_version": getattr(provider, "version", ""),
        "generated_at": generated_at,
        "latency_s": round(time.perf_counter() - started, 3),
        "error": error,
    }


def _prediction_by_case_id(
    prediction_rows: Iterable[Mapping[str, Any]],
) -> tuple[dict[str, Mapping[str, Any]], int]:
    by_id: dict[str, Mapping[str, Any]] = {}
    total = 0
    for row in prediction_rows:
        total += 1
        case_id = str(row.get("case_id") or "")
        if case_id:
            by_id[case_id] = row
    return by_id, max(0, total - len(by_id))


def blind_label_assessment_rows(
    manifest_rows: Iterable[Mapping[str, Any]],
    prediction_rows: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Join blind-label predictions to the private manifest and mark outcomes."""
    predictions, duplicate_prediction_rows = _prediction_by_case_id(prediction_rows)
    out: list[dict[str, Any]] = []
    for manifest in manifest_rows:
        case_id = str(manifest.get("case_id") or "")
        gold = normalize_label(manifest.get("gold_label"))
        pred_row = predictions.get(case_id)
        predicted: str | None = None
        status: str
        parse_error: str | None = None
        rationale = ""
        provider = ""
        provider_version = ""
        generated_at = ""
        error: str | None = None

        if pred_row is None:
            status = "missing"
        else:
            predicted = normalize_label(pred_row.get("predicted_label"))
            if predicted is None:
                parsed = parse_blind_label_response(str(pred_row.get("raw_response") or ""))
                predicted = parsed.label
                parse_error = parsed.parse_error
            else:
                parse_error = (
                    str(pred_row.get("parse_error"))
                    if pred_row.get("parse_error") is not None
                    else None
                )
            rationale = str(pred_row.get("rationale") or "")
            provider = str(pred_row.get("provider") or "")
            provider_version = str(pred_row.get("provider_version") or "")
            generated_at = str(pred_row.get("generated_at") or "")
            error = str(pred_row.get("error")) if pred_row.get("error") else None
            if error:
                status = "error"
            elif predicted is None:
                status = "invalid"
            elif predicted == gold:
                status = "agree"
            else:
                status = "disagree"

        out.append(
            {
                "case_id": case_id,
                "gold_label": gold,
                "predicted_label": predicted,
                "status": status,
                "split": manifest.get("split"),
                "dataset_version": manifest.get("dataset_version"),
                "query_hash": manifest.get("query_hash"),
                "cell_id": manifest.get("cell_id"),
                "pattern": manifest.get("pattern"),
                "domain": manifest.get("domain"),
                "difficulty": manifest.get("difficulty"),
                "rationale": rationale,
                "provider": provider,
                "provider_version": provider_version,
                "generated_at": generated_at,
                "parse_error": parse_error,
                "error": error,
                "duplicate_prediction_rows": duplicate_prediction_rows,
            }
        )
    return out


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(numerator / denominator, 6)


def _group_counts(rows: Sequence[Mapping[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    buckets: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[str(row.get(key) or "unknown")].append(row)

    out: dict[str, dict[str, Any]] = {}
    for value, items in sorted(buckets.items()):
        statuses = Counter(str(row.get("status") or "unknown") for row in items)
        scored = statuses.get("agree", 0) + statuses.get("disagree", 0)
        out[value] = {
            "rows": len(items),
            "scored": scored,
            "agree": statuses.get("agree", 0),
            "disagree": statuses.get("disagree", 0),
            "missing": statuses.get("missing", 0),
            "invalid": statuses.get("invalid", 0),
            "error": statuses.get("error", 0),
            "agreement_rate": _rate(statuses.get("agree", 0), scored),
        }
    return out


def blind_label_score_summary(
    assessment_rows: Sequence[Mapping[str, Any]],
    *,
    prediction_rows: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    statuses = Counter(str(row.get("status") or "unknown") for row in assessment_rows)
    scored = statuses.get("agree", 0) + statuses.get("disagree", 0)
    confusion: dict[str, dict[str, int]] = {
        gold: {pred: 0 for pred in VALID_LABELS} for gold in VALID_LABELS
    }
    for row in assessment_rows:
        gold = normalize_label(row.get("gold_label"))
        pred = normalize_label(row.get("predicted_label"))
        if gold and pred:
            confusion[gold][pred] += 1

    duplicate_prediction_rows = 0
    if assessment_rows:
        duplicate_prediction_rows = int(assessment_rows[0].get("duplicate_prediction_rows") or 0)

    return {
        "total_manifest_rows": len(assessment_rows),
        "prediction_rows": len(prediction_rows or []),
        "duplicate_prediction_rows": duplicate_prediction_rows,
        "scored_rows": scored,
        "missing_rows": statuses.get("missing", 0),
        "invalid_rows": statuses.get("invalid", 0),
        "error_rows": statuses.get("error", 0),
        "agree_rows": statuses.get("agree", 0),
        "disagree_rows": statuses.get("disagree", 0),
        "coverage_rate": _rate(scored, len(assessment_rows)),
        "agreement_rate": _rate(statuses.get("agree", 0), scored),
        "status_counts": dict(sorted(statuses.items())),
        "confusion_matrix": confusion,
        "by_gold_label": _group_counts(assessment_rows, "gold_label"),
        "by_predicted_label": _group_counts(assessment_rows, "predicted_label"),
        "by_split": _group_counts(assessment_rows, "split"),
        "by_domain": _group_counts(assessment_rows, "domain"),
        "by_pattern": _group_counts(assessment_rows, "pattern"),
        "by_difficulty": _group_counts(assessment_rows, "difficulty"),
    }


def disagreement_rows(assessment_rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = [dict(row) for row in assessment_rows if row.get("status") == "disagree"]
    return sorted(rows, key=lambda row: str(row.get("case_id") or ""))


def review_queue_rows(assessment_rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows = [
        dict(row)
        for row in assessment_rows
        if row.get("status") in {"disagree", "invalid", "error", "missing"}
    ]
    return sorted(
        rows, key=lambda row: (str(row.get("status") or ""), str(row.get("case_id") or ""))
    )


def bucket_for_assessment(row: Mapping[str, Any]) -> str:
    """Map a scored assessment to the user's QA buckets."""
    return "validated" if row.get("status") == "agree" else "triage"


def bucketed_assessment_rows(
    assessment_rows: Iterable[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    validated: list[dict[str, Any]] = []
    triage: list[dict[str, Any]] = []
    for row in assessment_rows:
        item = dict(row)
        item["bucket"] = bucket_for_assessment(item)
        if item["bucket"] == "validated":
            validated.append(item)
        else:
            triage.append(item)
    return (
        sorted(validated, key=lambda row: str(row.get("case_id") or "")),
        sorted(triage, key=lambda row: str(row.get("case_id") or "")),
    )


def second_pass_ledger_rows(
    assessment_rows: Iterable[Mapping[str, Any]],
    *,
    run_id: str,
    recorded_at: str | None = None,
) -> list[dict[str, Any]]:
    """Build append-only rows for excluding second-pass-audited cases later."""
    stamp = recorded_at or utcnow_iso()
    out: list[dict[str, Any]] = []
    for row in assessment_rows:
        out.append(
            {
                "case_id": row.get("case_id"),
                "run_id": run_id,
                "recorded_at": stamp,
                "bucket": bucket_for_assessment(row),
                "status": row.get("status"),
                "gold_label": row.get("gold_label"),
                "predicted_label": row.get("predicted_label"),
                "split": row.get("split"),
                "dataset_version": row.get("dataset_version"),
                "cell_id": row.get("cell_id"),
                "pattern": row.get("pattern"),
                "domain": row.get("domain"),
                "difficulty": row.get("difficulty"),
                "provider": row.get("provider"),
                "provider_version": row.get("provider_version"),
            }
        )
    return sorted(out, key=lambda row: str(row.get("case_id") or ""))


def markdown_score_report(summary: Mapping[str, Any]) -> str:
    lines = [
        "# Blind Label Score",
        "",
        f"Manifest rows: **{summary['total_manifest_rows']}**",
        f"Prediction rows: **{summary['prediction_rows']}**",
        f"Scored rows: **{summary['scored_rows']}**",
        f"Agreement: **{summary['agree_rows']} / {summary['scored_rows']}** "
        f"({summary['agreement_rate']})",
        f"Disagreements: **{summary['disagree_rows']}**",
        f"Missing / invalid / error: **{summary['missing_rows']} / "
        f"{summary['invalid_rows']} / {summary['error_rows']}**",
        "",
        "## Confusion Matrix",
        "",
        "| Gold \\ Predicted | ABSTAIN | DISPUTED | TRUSTWORTHY |",
        "|---|---:|---:|---:|",
    ]
    confusion = summary["confusion_matrix"]
    for gold in VALID_LABELS:
        row = confusion[gold]
        lines.append(f"| {gold} | {row['ABSTAIN']} | {row['DISPUTED']} | {row['TRUSTWORTHY']} |")

    lines.extend(
        [
            "",
            "## By Gold Label",
            "",
            "| Gold | Rows | Scored | Agree | Disagree | Rate |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for label, row in summary["by_gold_label"].items():
        lines.append(
            f"| {label} | {row['rows']} | {row['scored']} | {row['agree']} | "
            f"{row['disagree']} | {row['agreement_rate']} |"
        )

    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "- `blind_label_score_summary.json`",
            "- `blind_label_score_report.md`",
            "- `blind_label_disagreements.jsonl`",
            "- `blind_label_review_queue.jsonl`",
        ]
    )
    return "\n".join(lines) + "\n"
