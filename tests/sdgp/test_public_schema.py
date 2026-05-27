"""Tests for the schema-clean public SDGP export contract."""

from __future__ import annotations

from fitz_gov.sdgp.public_schema import (
    find_legacy_public_fields,
    strip_legacy_public_fields,
)


def test_public_schema_strips_legacy_report_axes() -> None:
    row = {
        "id": "case_001",
        "domain": "finance",
        "query_type": "what",
        "source_type": "multi_source",
        "meta": {
            "dataset_version": "v7",
            "difficulty": "hard",
            "domain": "economics_finance",
            "subcategory": "wrong_entity",
            "reasoning_type": "factual",
            "query_type": "what",
            "evidence_pattern": "absent",
        },
    }

    clean = strip_legacy_public_fields(row)

    assert find_legacy_public_fields(clean) == []
    assert clean["meta"] == {"dataset_version": "v7", "difficulty": "hard"}
    assert "domain" not in clean
    assert "query_type" not in clean
    assert "source_type" not in clean


def test_public_schema_does_not_mutate_source_row() -> None:
    row = {"meta": {"domain": "science_medicine", "difficulty": "easy"}}

    clean = strip_legacy_public_fields(row)

    assert clean == {"meta": {"difficulty": "easy"}}
    assert row == {"meta": {"domain": "science_medicine", "difficulty": "easy"}}
