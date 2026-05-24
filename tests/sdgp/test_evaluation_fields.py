from __future__ import annotations

from fitz_gov.sdgp.evaluation_fields import (
    audit_evaluation_fields,
    merge_evaluation_overlay,
    needs_evaluation_enrichment,
    promote_evaluation_fields,
)


def _case(classification: str = "TRUSTWORTHY", dataset_version: str = "v6"):
    return {
        "id": "case_001",
        "input": {"contexts": [{"id": "ctx_001", "text": "Alpha happened in 2024."}]},
        "governance": {"classification": classification},
        "meta": {
            "dataset_version": dataset_version,
            "v51_legacy": {
                "evaluation_config": {
                    "mode": "governance",
                    "check_mode_match": True,
                    "use_regex": True,
                    "case_insensitive": True,
                    "min_required": 1,
                },
                "required_elements": ["Alpha", "2024"],
                "forbidden_claims": ["Beta happened"],
                "forbidden_elements": ["guaranteed"],
                "detection_labels": ["legacy-only"],
                "description": "legacy description",
                "rationale": "legacy rationale",
            },
        },
    }


def test_promote_evaluation_fields_strips_legacy_and_aliases() -> None:
    case = _case()
    case["required_elements"] = ["root wins"]
    case["conflict_density"] = 0.7
    case["governance"]["trustworthy_score"] = 0.8

    result = promote_evaluation_fields(case)

    assert result.changed
    assert case["evaluation"] == {
        "mode": "governance",
        "check_mode_match": True,
        "required_elements": ["root wins"],
        "forbidden_claims": ["Beta happened"],
        "forbidden_elements": ["guaranteed"],
        "config": {
            "case_insensitive": True,
            "min_required": 1,
            "use_regex": True,
        },
    }
    assert "v51_legacy" not in case["meta"]
    assert "required_elements" not in case
    assert "conflict_density" not in case
    assert "trustworthy_score" not in case["governance"]
    assert audit_evaluation_fields(case) == []


def test_needs_evaluation_enrichment_only_for_v7_trustworthy_without_quality_lists() -> None:
    trustworthy = {
        "id": "v7_t",
        "governance": {"classification": "TRUSTWORTHY"},
        "meta": {"dataset_version": "v7"},
    }
    promote_evaluation_fields(trustworthy)
    assert needs_evaluation_enrichment(trustworthy) is True

    abstain = {
        "id": "v7_a",
        "governance": {"classification": "ABSTAIN"},
        "meta": {"dataset_version": "v7"},
    }
    promote_evaluation_fields(abstain)
    assert needs_evaluation_enrichment(abstain) is False


def test_merge_evaluation_overlay_adds_quality_lists() -> None:
    case = {
        "id": "v7_t",
        "governance": {"classification": "TRUSTWORTHY"},
        "meta": {"dataset_version": "v7"},
    }
    promote_evaluation_fields(case)
    result = merge_evaluation_overlay(
        case,
        {
            "evaluation": {
                "required_elements": ["Alpha", "2024"],
                "forbidden_claims": ["Beta"],
                "forbidden_elements": [],
                "config": {"use_regex": True},
            }
        },
    )

    assert result.changed
    assert case["evaluation"]["required_elements"] == ["Alpha", "2024"]
    assert case["evaluation"]["forbidden_claims"] == ["Beta"]
    assert needs_evaluation_enrichment(case) is False
