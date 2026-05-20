"""Tests for fitz_gov.sdgp.llm_enrich."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fitz_gov.sdgp.llm_enrich import (
    LLM_TODO,
    ENRICHMENT_SYSTEM,
    build_enrichment_prompt,
    case_needs_enrichment,
    cases_needing_enrichment,
    enrich_case_with_provider,
    merge_enrichment,
    parse_enrichment_response,
)
from fitz_gov.sdgp.providers import GenerateRequest, StubProvider
from fitz_gov.sdgp.vault import Vault


def _todo_case(case_id: str = "t1_x") -> dict:
    """A V5.1-enriched-shaped case with the typical TODO_LLM markers."""
    return {
        "id": case_id,
        "version": "fitz-gov-5.1-enriched",
        "input": {
            "query": "What is the speed of light?",
            "query_rewritten": LLM_TODO,
            "contexts": [
                {"id": "ctx_001", "text": "Light travels at 299,792,458 m/s in vacuum.",
                 "authority_score": 0.85, "summary": "truncated stub...",
                 "relevance_to_query": 0.5,
                 "temporality": {"is_time_sensitive": False, "anchor_period": LLM_TODO, "staleness_risk": "low"}},
            ],
        },
        "governance": {
            "classification": "TRUSTWORTHY",
            "hallucination_pressure": 0.3,
            "retrieval_retry_value": 0.3,
            "query_evidence_alignment": 0.6,
            "answer_coverage": 0.75,
            "boundary_proximity": {"nearest_class": "DISPUTED", "distance": 0.6},
        },
        "taxonomy": {
            "governance_class": "TRUSTWORTHY",
            "pattern": "direct_answer",
            "cell_id": "direct_answer__science_medicine__easy",
        },
        "routing": {"expert_fired": "science_medicine"},
        "meta": {
            "difficulty": "easy",
            "near_miss_class": "DISPUTED",
            "near_miss_reason": LLM_TODO,
        },
    }


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------


def test_prompt_includes_locked_field_warning() -> None:
    p = build_enrichment_prompt(_todo_case())
    assert "Locked fields (do NOT change)" in p
    assert "do NOT change" in p


def test_prompt_includes_case_metadata() -> None:
    p = build_enrichment_prompt(_todo_case("my_id"))
    assert "my_id" in p
    assert "direct_answer" in p
    assert "science_medicine" in p


def test_prompt_lists_required_output_fields() -> None:
    p = build_enrichment_prompt(_todo_case())
    for f in ("query_rewritten", "summary", "relevance_to_query",
              "anchor_period", "hallucination_pressure",
              "retrieval_retry_value", "query_evidence_alignment",
              "answer_coverage", "boundary_proximity_distance",
              "near_miss_reason"):
        assert f in p


def test_prompt_omits_TODO_markers_to_keep_it_compact() -> None:
    """The prompt sends a trimmed-down view of the case — TODO markers
    aren't sent (the LLM doesn't need to see its job description twice)."""
    p = build_enrichment_prompt(_todo_case())
    assert "<TODO_LLM>" not in p


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------


def test_parse_plain_json() -> None:
    assert parse_enrichment_response('{"query_rewritten": "x"}') == {"query_rewritten": "x"}


def test_parse_fenced_json() -> None:
    raw = '```json\n{"x": 1}\n```'
    assert parse_enrichment_response(raw) == {"x": 1}


def test_parse_with_leading_prose() -> None:
    raw = "Here you go:\n{\"x\": 1}\nDone."
    assert parse_enrichment_response(raw) == {"x": 1}


def test_parse_empty_raises() -> None:
    with pytest.raises(ValueError):
        parse_enrichment_response("")


def test_parse_no_json_raises() -> None:
    with pytest.raises(ValueError):
        parse_enrichment_response("nothing parseable")


# ---------------------------------------------------------------------------
# merge_enrichment
# ---------------------------------------------------------------------------


def test_merge_fills_query_rewritten() -> None:
    case = _todo_case()
    res = merge_enrichment(case, {"query_rewritten": "What is c in m/s?"})
    assert case["input"]["query_rewritten"] == "What is c in m/s?"
    assert "input.query_rewritten" in res.fields_filled


def test_merge_skips_empty_query_rewritten() -> None:
    case = _todo_case()
    merge_enrichment(case, {"query_rewritten": "  "})
    assert case["input"]["query_rewritten"] == LLM_TODO  # unchanged


def test_merge_per_chunk_summary_and_relevance() -> None:
    case = _todo_case()
    enrichment = {
        "contexts": [
            {
                "id": "ctx_001",
                "summary": "Speed of light in vacuum.",
                "relevance_to_query": 0.95,
                "temporality": {"anchor_period": "current"},
            }
        ]
    }
    res = merge_enrichment(case, enrichment)
    ctx = case["input"]["contexts"][0]
    assert ctx["summary"] == "Speed of light in vacuum."
    assert ctx["relevance_to_query"] == 0.95
    assert ctx["temporality"]["anchor_period"] == "current"
    assert any("relevance_to_query" in f for f in res.fields_filled)


def test_merge_clamps_floats_to_01_range() -> None:
    case = _todo_case()
    merge_enrichment(case, {
        "governance": {
            "hallucination_pressure": 1.5,         # over → 1.0
            "retrieval_retry_value": -0.2,         # under → 0.0
            "query_evidence_alignment": "0.7",     # string → 0.7
            "answer_coverage": "not a number",     # invalid → unchanged
        }
    })
    assert case["governance"]["hallucination_pressure"] == 1.0
    assert case["governance"]["retrieval_retry_value"] == 0.0
    assert case["governance"]["query_evidence_alignment"] == 0.7
    # answer_coverage stays at the pre-existing heuristic value
    assert case["governance"]["answer_coverage"] == 0.75


def test_merge_patches_boundary_distance_only() -> None:
    case = _todo_case()
    merge_enrichment(case, {
        "governance": {"boundary_proximity_distance": 0.42}
    })
    bp = case["governance"]["boundary_proximity"]
    assert bp["distance"] == 0.42
    assert bp["nearest_class"] == "DISPUTED"  # preserved


def test_merge_near_miss_reason() -> None:
    case = _todo_case()
    merge_enrichment(case, {
        "meta": {"near_miss_reason": "single-source physics constant; could look like a contested measurement."}
    })
    assert case["meta"]["near_miss_reason"].startswith("single-source")
    assert "<TODO_LLM>" not in case["meta"]["near_miss_reason"]


def test_merge_aligns_chunks_positionally_when_no_id() -> None:
    case = _todo_case()
    case["input"]["contexts"].append({"id": "ctx_002", "text": "more context"})
    enrichment = {
        "contexts": [
            {"summary": "first chunk summary", "relevance_to_query": 0.9},
            {"summary": "second chunk summary", "relevance_to_query": 0.3},
        ]
    }
    merge_enrichment(case, enrichment)
    # ID-aware fallback should still align positionally since enrichment chunks lack id
    assert case["input"]["contexts"][0]["summary"] == "first chunk summary"
    assert case["input"]["contexts"][1]["summary"] == "second chunk summary"


# ---------------------------------------------------------------------------
# enrich_case_with_provider — end-to-end with StubProvider
# ---------------------------------------------------------------------------


def test_enrich_case_with_provider_end_to_end() -> None:
    case = _todo_case("t1_test_001")
    response = json.dumps({
        "query_rewritten": "Light speed in m/s?",
        "contexts": [
            {
                "id": "ctx_001",
                "summary": "Vacuum speed of light is 299,792,458 m/s.",
                "relevance_to_query": 0.98,
                "temporality": {"anchor_period": "timeless physical constant"},
            }
        ],
        "governance": {
            "hallucination_pressure": 0.05,
            "retrieval_retry_value": 0.1,
            "query_evidence_alignment": 0.95,
            "answer_coverage": 0.95,
            "boundary_proximity_distance": 0.85,
        },
        "meta": {"near_miss_reason": "single number, no other sources to dispute."},
    })
    provider = StubProvider(response=response, name="stub", version="v1")
    res = enrich_case_with_provider(case, provider)
    assert res.case_id == "t1_test_001"
    assert res.changed
    assert case["input"]["query_rewritten"] == "Light speed in m/s?"
    assert case["governance"]["hallucination_pressure"] == 0.05
    assert case["meta"]["near_miss_reason"].startswith("single number")
    assert case["input"]["contexts"][0]["temporality"]["anchor_period"] == "timeless physical constant"


# ---------------------------------------------------------------------------
# case_needs_enrichment + cases_needing_enrichment
# ---------------------------------------------------------------------------


def test_case_needs_enrichment_when_todo_present() -> None:
    case = _todo_case()
    assert case_needs_enrichment(case) is True


def test_case_no_longer_needs_after_full_enrichment() -> None:
    case = _todo_case()
    case["input"]["query_rewritten"] = "fixed"
    case["meta"]["near_miss_reason"] = "fixed"
    case["input"]["contexts"][0]["temporality"]["anchor_period"] = "fixed"
    assert case_needs_enrichment(case) is False


def test_cases_needing_enrichment_filters() -> None:
    cases = [_todo_case("a"), _todo_case("b")]
    cases[1]["input"]["query_rewritten"] = "done"
    cases[1]["meta"]["near_miss_reason"] = "done"
    cases[1]["input"]["contexts"][0]["temporality"]["anchor_period"] = "done"
    ids = cases_needing_enrichment(cases)
    assert ids == ["a"]


# ---------------------------------------------------------------------------
# Vault.update_cases — in-place revision support
# ---------------------------------------------------------------------------


def test_vault_update_cases_replaces_matching_ids(tmp_path: Path) -> None:
    from fitz_gov.sdgp.vault import Provenance

    v = Vault.open(tmp_path / "vault")
    case_a = _todo_case("a")
    case_b = _todo_case("b")
    v.add(case_a, provenance=Provenance(provider="test"))
    v.add(case_b, provenance=Provenance(provider="test"))

    enriched_a = dict(case_a)
    enriched_a["input"]["query_rewritten"] = "enriched query for a"
    res = v.update_cases({"a": enriched_a})
    assert res["updated"] == 1
    assert res["passthrough"] == 1
    assert res["unknown"] == 0

    stored_a = v.get("a")
    assert stored_a is not None
    assert stored_a["input"]["query_rewritten"] == "enriched query for a"
    assert stored_a[VAULT_KEY := "_vault"]["revisions"] == 1
    assert stored_a["_vault"]["provider"] == "test"  # preserved
    # B unchanged
    stored_b = v.get("b")
    assert stored_b is not None
    assert stored_b["input"]["query_rewritten"] == LLM_TODO


def test_vault_update_cases_reports_unknown_ids(tmp_path: Path) -> None:
    v = Vault.open(tmp_path / "vault")
    v.add(_todo_case("a"))
    res = v.update_cases({"nonexistent_id": _todo_case("nonexistent_id")})
    assert res["unknown"] == 1
    assert res["updated"] == 0
