"""Tests for blind-label execution and scoring helpers."""

from __future__ import annotations

from fitz_gov.sdgp.blind_label import (
    blind_label_assessment_rows,
    blind_label_score_summary,
    bucketed_assessment_rows,
    build_blind_label_prompt,
    case_ids_from_rows,
    disagreement_rows,
    label_queue_row,
    parse_blind_label_response,
    review_queue_rows,
    sample_queue_rows,
    second_pass_ledger_rows,
)
from fitz_gov.sdgp.providers import StubProvider


def _queue_row(case_id: str = "case_1") -> dict:
    return {
        "case_id": case_id,
        "input": {
            "query": "What ended the War of 1812?",
            "contexts": [{"id": "ctx_001", "text": "The Treaty of Ghent ended the War of 1812."}],
        },
    }


def _manifest_row(case_id: str, gold: str) -> dict:
    return {
        "case_id": case_id,
        "gold_label": gold,
        "split": "test",
        "dataset_version": "v7",
        "query_hash": f"q_{case_id}",
        "cell_id": "direct_answer__history_geography__easy",
        "pattern": "direct_answer",
        "domain": "history_geography",
        "difficulty": "easy",
    }


def test_parse_blind_label_response_accepts_json_and_plain_text() -> None:
    parsed_json = parse_blind_label_response(
        '{"label":"TRUSTWORTHY","rationale":"context directly answers"}'
    )
    parsed_text = parse_blind_label_response("Disputed - sources conflict.")

    assert parsed_json.parse_ok
    assert parsed_json.label == "TRUSTWORTHY"
    assert parsed_json.rationale == "context directly answers"
    assert parsed_text.parse_ok
    assert parsed_text.label == "DISPUTED"


def test_parse_blind_label_response_does_not_grab_allowed_label_list() -> None:
    parsed = parse_blind_label_response(
        "Task: choose ABSTAIN, DISPUTED, or TRUSTWORTHY. "
        "The contexts conflict, so the correct label is DISPUTED."
    )

    assert parsed.parse_ok
    assert parsed.label == "DISPUTED"


def test_parse_blind_label_response_does_not_grab_label_should_allowed_list() -> None:
    parsed = parse_blind_label_response(
        "The label should be ABSTAIN, DISPUTED, or TRUSTWORTHY. "
        "Since the context explicitly answers the question, the label is TRUSTWORTHY."
    )

    assert parsed.parse_ok
    assert parsed.label == "TRUSTWORTHY"


def test_parse_blind_label_response_accepts_label_should_be_text() -> None:
    parsed = parse_blind_label_response(
        "The contexts directly answer the question. "
        "Therefore, the label should be TRUSTWORTHY."
    )

    assert parsed.parse_ok
    assert parsed.label == "TRUSTWORTHY"


def test_parse_blind_label_response_rejects_analysis_without_final_label() -> None:
    parsed = parse_blind_label_response(
        "Task: choose ABSTAIN, DISPUTED, or TRUSTWORTHY. "
        "ABSTAIN is not applicable. DISPUTED might apply."
    )

    assert not parsed.parse_ok
    assert parsed.label is None


def test_parse_blind_label_response_accepts_decision_phrasing() -> None:
    parsed = parse_blind_label_response(
        "The sources contain a high-authority vs low-authority contradiction, "
        "so DISPUTED is appropriate."
    )

    assert parsed.parse_ok
    assert parsed.label == "DISPUTED"


def test_parse_blind_label_response_accepts_fenced_json() -> None:
    parsed = parse_blind_label_response(
        '```json\n{"label":"ABSTAIN","rationale":"missing evidence"}\n```'
    )

    assert parsed.parse_ok
    assert parsed.label == "ABSTAIN"
    assert parsed.rationale == "missing evidence"


def test_parse_blind_label_response_uses_last_json_after_thinking_block() -> None:
    parsed = parse_blind_label_response(
        '<think>Example: {"label":"ABSTAIN","rationale":"not final"}</think>\n'
        '{"label":"TRUSTWORTHY","rationale":"final answer"}'
    )

    assert parsed.parse_ok
    assert parsed.label == "TRUSTWORTHY"
    assert parsed.rationale == "final answer"


def test_parse_blind_label_response_ignores_placeholder_json() -> None:
    parsed = parse_blind_label_response(
        '{"label":"TRUSTWORTHY","rationale":"real rationale"}\n'
        'Format reminder: {"label":"TRUSTWORTHY","rationale":"short reason"}'
    )

    assert parsed.parse_ok
    assert parsed.label == "TRUSTWORTHY"
    assert parsed.rationale == "real rationale"


def test_label_queue_row_uses_only_query_and_contexts() -> None:
    prompt = build_blind_label_prompt(_queue_row())
    provider = StubProvider(
        response='{"label":"TRUSTWORTHY","rationale":"the context answers the query"}'
    )

    result = label_queue_row(_queue_row(), provider)

    assert "gold_label" not in prompt
    assert result["case_id"] == "case_1"
    assert result["predicted_label"] == "TRUSTWORTHY"
    assert result["parse_ok"] is True
    assert result["error"] is None


def test_blind_label_score_summary_and_review_rows() -> None:
    manifest = [
        _manifest_row("a", "TRUSTWORTHY"),
        _manifest_row("b", "ABSTAIN"),
        _manifest_row("c", "DISPUTED"),
    ]
    predictions = [
        {"case_id": "a", "predicted_label": "TRUSTWORTHY"},
        {"case_id": "b", "predicted_label": "DISPUTED", "rationale": "conflict"},
    ]

    assessments = blind_label_assessment_rows(manifest, predictions)
    summary = blind_label_score_summary(assessments, prediction_rows=predictions)

    assert summary["scored_rows"] == 2
    assert summary["agree_rows"] == 1
    assert summary["disagree_rows"] == 1
    assert summary["missing_rows"] == 1
    assert summary["agreement_rate"] == 0.5
    assert len(disagreement_rows(assessments)) == 1
    assert {row["status"] for row in review_queue_rows(assessments)} == {"disagree", "missing"}


def test_sample_queue_rows_excludes_existing_ledger_case_ids() -> None:
    queue = [_queue_row(f"case_{idx}") for idx in range(10)]
    ledger = [{"case_id": "case_3"}, {"case_id": "case_7"}]

    sample = sample_queue_rows(
        queue,
        sample_size=5,
        seed=11,
        excluded_case_ids=case_ids_from_rows(ledger),
    )

    assert len(sample) == 5
    assert "case_3" not in case_ids_from_rows(sample)
    assert "case_7" not in case_ids_from_rows(sample)


def test_bucketed_rows_and_ledger_mark_validated_vs_triage() -> None:
    manifest = [_manifest_row("a", "TRUSTWORTHY"), _manifest_row("b", "ABSTAIN")]
    predictions = [
        {"case_id": "a", "predicted_label": "TRUSTWORTHY", "provider": "lm_studio"},
        {"case_id": "b", "predicted_label": "DISPUTED", "provider": "lm_studio"},
    ]
    assessments = blind_label_assessment_rows(manifest, predictions)

    validated, triage = bucketed_assessment_rows(assessments)
    ledger = second_pass_ledger_rows(assessments, run_id="pilot")

    assert [row["case_id"] for row in validated] == ["a"]
    assert [row["case_id"] for row in triage] == ["b"]
    assert {row["bucket"] for row in ledger} == {"validated", "triage"}
