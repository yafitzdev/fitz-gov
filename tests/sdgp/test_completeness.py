"""Tests for full training-schema completeness checks."""

from __future__ import annotations

from fitz_gov.sdgp.checker import Checker
from fitz_gov.sdgp.completeness import audit_case_completeness, is_training_complete


def _complete_case() -> dict:
    return {
        "id": "complete_001",
        "version": "fitz-gov-7.0",
        "input": {
            "query": "Who wrote Hamlet?",
            "query_rewritten": "Who is credited with writing Hamlet?",
            "contexts": [
                {
                    "id": "ctx_001",
                    "text": "The Folger Shakespeare Library credits William Shakespeare with Hamlet.",
                    "authority_score": 0.92,
                    "authority_signal": "domain_expert",
                    "temporality": {
                        "is_time_sensitive": False,
                        "anchor_period": "none",
                        "staleness_risk": "none",
                    },
                    "summary": "A domain-expert source credits Shakespeare with Hamlet.",
                    "relevance_to_query": 0.96,
                    "boundary_quality": 0.95,
                }
            ],
        },
        "governance": {
            "classification": "TRUSTWORTHY",
            "abstain": 0.04,
            "disputed": 0.06,
            "trustworthy": 0.90,
            "confidence": 0.90,
            "grounding": 0.93,
            "conflict_density": 0.05,
            "evidence_sufficiency": 0.91,
            "boundary_proximity": {"nearest_class": "ABSTAIN", "distance": 0.82},
            "domain_familiarity": 0.95,
            "false_trustworthy_risk": 0.04,
            "hallucination_pressure": 0.08,
            "retrieval_retry_value": 0.12,
            "human_escalation_score": 0.03,
            "query_evidence_alignment": 0.96,
            "answer_coverage": 0.94,
            "evidence_bias_score": 0.20,
        },
        "routing": {
            "expert_fired": "culture_society",
            "secondary_expert": None,
            "routing_confidence": 0.91,
        },
        "taxonomy": {
            "governance_class": "TRUSTWORTHY",
            "pattern": "single_authoritative",
            "pattern_description": "One high-authority source, no contradictions, directly answers query",
            "cell_id": "single_authoritative__culture_society__easy",
        },
        "evaluation": {
            "mode": "governance",
            "check_mode_match": True,
            "required_elements": ["Answer must identify William Shakespeare as the credited author."],
            "forbidden_claims": [],
            "forbidden_elements": [],
        },
        "meta": {
            "dataset_version": "v7",
            "difficulty": "easy",
            "category": "trustworthy_direct",
            "confidence_level": "high",
            "near_miss_class": "ABSTAIN",
            "near_miss_reason": "A naive reader might abstain from a single source, but it is authoritative and direct.",
            "grounding_targets": {
                "gold_answer": "William Shakespeare is credited with writing Hamlet.",
                "sentences": [
                    {
                        "text": "William Shakespeare is credited with writing Hamlet.",
                        "attributions": ["ctx_001"],
                    }
                ],
            },
        },
    }


def test_complete_case_has_no_issues() -> None:
    case = _complete_case()
    assert audit_case_completeness(case) == []
    assert is_training_complete(case)


def test_trustworthy_requires_grounding_targets() -> None:
    case = _complete_case()
    del case["meta"]["grounding_targets"]
    issues = audit_case_completeness(case)
    assert any(i.path == "meta.grounding_targets" for i in issues)
    assert not is_training_complete(case)


def test_checker_can_require_training_schema() -> None:
    case = _complete_case()
    del case["input"]["contexts"][0]["summary"]

    loose = Checker().check(case)
    strict = Checker(require_training_schema=True).check(case)

    assert loose.passed
    assert not strict.passed
    assert any(i.rule == "training_schema_incomplete" for i in strict.errors)
