"""Tests for V7 training-schema completion merge logic."""

from __future__ import annotations

from fitz_gov.sdgp.completeness import audit_case_completeness
from fitz_gov.sdgp.v7_completion import (
    merge_v7_completion,
    parse_v7_completion_response,
)


def _thin_case() -> dict:
    return {
        "id": "sdgp_v7_wrong_entity__history_geography__easy__0",
        "input": {
            "query": "What treaty ended the War of 1812?",
            "query_rewritten": "Which treaty formally ended the War of 1812?",
            "contexts": [
                {
                    "id": "ctx_001",
                    "text": "The Treaty of Versailles ended World War I in 1919.",
                    "authority_score": 0.80,
                    "authority_signal": "encyclopedic_general",
                    "boundary_quality": 0.95,
                },
                {
                    "id": "ctx_002",
                    "text": "The Treaty of Paris in 1783 ended the American Revolutionary War.",
                    "authority_score": 0.78,
                    "authority_signal": "encyclopedic_general",
                    "boundary_quality": 0.93,
                },
            ],
        },
        "governance": {
            "classification": "ABSTAIN",
            "abstain": 0.86,
            "disputed": 0.07,
            "trustworthy": 0.07,
        },
        "routing": {"expert_fired": "history_geography"},
        "taxonomy": {
            "governance_class": "ABSTAIN",
            "pattern": "wrong_entity",
            "cell_id": "wrong_entity__history_geography__easy",
        },
        "meta": {"dataset_version": "v7", "difficulty": "easy"},
    }


def _payload() -> dict:
    return {
        "input": {
            "query_rewritten": "Which treaty formally ended the War of 1812?",
            "contexts": [
                {
                    "id": "ctx_001",
                    "summary": "This chunk describes the Treaty of Versailles ending World War I.",
                    "relevance_to_query": 0.10,
                    "temporality": {
                        "is_time_sensitive": False,
                        "anchor_period": "1919",
                        "staleness_risk": "none",
                    },
                    "boundary_quality": 0.95,
                },
                {
                    "id": "ctx_002",
                    "summary": "This chunk describes the Treaty of Paris ending the Revolutionary War.",
                    "relevance_to_query": 0.15,
                    "temporality": {
                        "is_time_sensitive": False,
                        "anchor_period": "1783",
                        "staleness_risk": "none",
                    },
                    "boundary_quality": 0.93,
                },
            ],
            "evidence_chain": {
                "order": ["ctx_001", "ctx_002"],
                "reasoning": "Both chunks are wrong-entity treaty examples, so either order shows absence.",
            },
        },
        "governance": {
            "confidence": 0.90,
            "grounding": 0.10,
            "conflict_density": 0.05,
            "evidence_sufficiency": 0.08,
            "boundary_proximity": {"nearest_class": "TRUSTWORTHY", "distance": 0.85},
            "domain_familiarity": 0.90,
            "false_trustworthy_risk": 0.12,
            "hallucination_pressure": 0.85,
            "retrieval_retry_value": 0.92,
            "human_escalation_score": 0.25,
            "query_evidence_alignment": 0.12,
            "answer_coverage": 0.05,
            "evidence_bias_score": 0.30,
        },
        "routing": {"secondary_expert": None, "routing_confidence": 0.93},
        "meta": {
            "category": "abstention",
            "confidence_level": "high",
            "near_miss_class": "TRUSTWORTHY",
            "near_miss_reason": "A naive reader might see treaty facts, but both chunks address different wars.",
        },
    }


def test_parse_v7_completion_response_handles_fences() -> None:
    assert parse_v7_completion_response('```json\n{"x": 1}\n```') == {"x": 1}


def test_merge_v7_completion_fills_thin_case() -> None:
    case = _thin_case()
    assert audit_case_completeness(case)

    res = merge_v7_completion(case, _payload())

    assert res.changed
    assert case["version"] == "fitz-gov-7.0"
    assert case["taxonomy"]["pattern_description"]
    assert audit_case_completeness(case) == []


def test_merge_v7_completion_backfills_probability_aliases() -> None:
    case = _thin_case()
    gov = case["governance"]
    del gov["abstain"]
    del gov["disputed"]
    del gov["trustworthy"]
    gov["abstain_score"] = 0.84
    gov["disputed_score"] = 0.09
    gov["trustworthy_score"] = 0.07

    merge_v7_completion(case, _payload())

    assert gov["abstain"] == 0.84
    assert gov["disputed"] == 0.09
    assert gov["trustworthy"] == 0.07
    assert audit_case_completeness(case) == []
