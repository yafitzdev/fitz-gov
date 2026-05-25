"""Tests for fitz_gov.sdgp.checker."""

from __future__ import annotations

from typing import Any

import pytest

from fitz_gov.sdgp.checker import (
    CheckIssue,
    CheckResult,
    Checker,
    Severity,
    case_dedup_hash,
    hashes_from,
)
from fitz_gov.sdgp.taxonomy import (
    Cell,
    Difficulty,
    Domain,
    GovernanceClass,
    TaxonomyPattern,
)


# ---------------------------------------------------------------------------
# Fixtures: build minimal valid V6 / V5.1 cases
# ---------------------------------------------------------------------------


def v6_case(
    *,
    pattern: TaxonomyPattern = TaxonomyPattern.WRONG_SPECIFICITY,
    domain: Domain = Domain.HISTORY_GEOGRAPHY,
    difficulty: Difficulty = Difficulty.HARD,
    classification: GovernanceClass | None = None,
    query: str = "test query",
    contexts: list[Any] | None = None,
    governance_extra: dict | None = None,
    routing: dict | None = ...,  # type: ignore[assignment]
    meta_extra: dict | None = None,
    case_id: str = "test_case_001",
) -> dict:
    cell = Cell(pattern=pattern, domain=domain, difficulty=difficulty)
    cls = classification or cell.governance_class
    case: dict = {
        "id": case_id,
        "input": {
            "query": query,
            "contexts": contexts if contexts is not None else [{"text": "default ctx"}],
        },
        "governance": {"classification": cls.value},
        "taxonomy": {
            "governance_class": cell.governance_class.value,
            "pattern": pattern.value,
            "cell_id": cell.cell_id,
        },
        "meta": {"difficulty": difficulty.value},
    }
    if routing is ...:
        case["routing"] = {"expert_fired": domain.value, "routing_confidence": 0.9}
    elif routing is not None:
        case["routing"] = routing
    if governance_extra:
        case["governance"].update(governance_extra)
    if meta_extra:
        case["meta"].update(meta_extra)
    return case


# ---------------------------------------------------------------------------
# Happy paths
# ---------------------------------------------------------------------------


def test_minimal_v6_case_passes() -> None:
    r = Checker().check(v6_case())
    assert r.passed, [i.message for i in r.errors]
    assert not r.errors


def test_v51_shaped_case_passes_with_warnings() -> None:
    """Legacy V5.1: no taxonomy block, no governance block, just query+contexts+expected_mode."""
    case = {
        "id": "v51_x",
        "query": "test",
        "contexts": ["one"],
        "expected_mode": "abstain",
    }
    r = Checker().check(case)
    assert r.passed, [i.message for i in r.errors]


# ---------------------------------------------------------------------------
# Required keys / shape errors
# ---------------------------------------------------------------------------


def test_missing_id_is_error() -> None:
    c = v6_case()
    del c["id"]
    r = Checker().check(c)
    assert not r.passed
    assert any(i.rule == "missing_id" for i in r.errors)


def test_missing_query_is_error() -> None:
    c = v6_case()
    c["input"]["query"] = ""
    r = Checker().check(c)
    assert not r.passed
    assert any(i.rule == "missing_query" for i in r.errors)


def test_v6_missing_top_block_is_error() -> None:
    c = v6_case()
    del c["governance"]
    r = Checker().check(c)
    assert not r.passed
    assert any(i.rule == "v6_missing_block" for i in r.errors)


def test_contexts_not_a_list_is_error() -> None:
    c = v6_case()
    c["input"]["contexts"] = "not a list"
    r = Checker().check(c)
    assert not r.passed
    assert any(i.rule == "contexts_not_list" for i in r.errors)


def test_context_missing_text_is_error() -> None:
    c = v6_case(contexts=[{"not_text": "oops"}])
    r = Checker().check(c)
    assert not r.passed
    assert any(i.rule == "context_missing_text" for i in r.errors)


# ---------------------------------------------------------------------------
# Class / pattern consistency
# ---------------------------------------------------------------------------


def test_classification_must_match_pattern_class() -> None:
    """Pattern is an ABSTAIN one, but classification says TRUSTWORTHY → error."""
    c = v6_case(
        pattern=TaxonomyPattern.WRONG_SPECIFICITY,
        classification=GovernanceClass.TRUSTWORTHY,
    )
    r = Checker().check(c)
    assert not r.passed
    assert any(i.rule == "class_mismatch_pattern" for i in r.errors)


def test_taxonomy_governance_class_must_match_pattern() -> None:
    c = v6_case()
    c["taxonomy"]["governance_class"] = "DISPUTED"  # but pattern is ABSTAIN
    r = Checker().check(c)
    assert any(i.rule == "class_mismatch_taxonomy" for i in r.errors)


def test_invalid_classification_value_is_error() -> None:
    c = v6_case()
    c["governance"]["classification"] = "MAYBE"
    r = Checker().check(c)
    assert any(i.rule == "invalid_classification" for i in r.errors)


def test_invalid_pattern_is_error() -> None:
    c = v6_case()
    c["taxonomy"]["pattern"] = "not_a_real_pattern"
    r = Checker().check(c)
    assert any(i.rule == "invalid_pattern" for i in r.errors)


# ---------------------------------------------------------------------------
# Cell alignment
# ---------------------------------------------------------------------------


def test_cell_pattern_mismatch_is_error() -> None:
    c = v6_case()
    c["taxonomy"]["cell_id"] = "wrong_entity__history_geography__hard"  # pattern is wrong_specificity
    r = Checker().check(c)
    assert any(i.rule == "cell_pattern_mismatch" for i in r.errors)


def test_cell_difficulty_mismatch_is_error() -> None:
    c = v6_case(difficulty=Difficulty.HARD)
    c["meta"]["difficulty"] = "easy"  # cell says hard
    r = Checker().check(c)
    assert any(i.rule == "cell_difficulty_mismatch" for i in r.errors)


def test_cell_domain_mismatch_with_routing_is_error() -> None:
    c = v6_case(domain=Domain.HISTORY_GEOGRAPHY)
    c["routing"]["expert_fired"] = Domain.SCIENCE_MEDICINE.value
    r = Checker().check(c)
    assert any(i.rule == "cell_domain_mismatch" for i in r.errors)


def test_invalid_cell_id_is_error() -> None:
    c = v6_case()
    c["taxonomy"]["cell_id"] = "not_a_valid_cell_id"
    r = Checker().check(c)
    assert any(i.rule == "invalid_cell_id" for i in r.errors)


# ---------------------------------------------------------------------------
# V8 primary taxonomy gaps
# ---------------------------------------------------------------------------


def test_v8_gap_pattern_passes_when_primary_cell_is_consistent() -> None:
    c = v6_case(
        pattern=TaxonomyPattern.VERDICT_CONFLICT,
        domain=Domain.TECHNOLOGY_COMPUTING,
        classification=GovernanceClass.DISPUTED,
        contexts=[{"text": "Verdict PASS"}, {"text": "Verdict FAIL"}],
    )
    r = Checker().check(c)
    assert r.passed, [i.message for i in r.errors]


def test_v8_gap_pattern_cell_mismatch_is_error() -> None:
    c = v6_case(
        pattern=TaxonomyPattern.VERDICT_CONFLICT,
        domain=Domain.TECHNOLOGY_COMPUTING,
        classification=GovernanceClass.DISPUTED,
        contexts=[{"text": "Verdict PASS"}, {"text": "Verdict FAIL"}],
    )
    c["taxonomy"]["cell_id"] = "factual_contradiction__technology_computing__hard"
    r = Checker().check(c)
    assert any(i.rule == "cell_pattern_mismatch" for i in r.errors)


# ---------------------------------------------------------------------------
# Pattern structure (delegates to taxonomy.check_pattern_structure)
# ---------------------------------------------------------------------------


def test_numerical_conflict_with_one_context_fails_structure() -> None:
    c = v6_case(
        pattern=TaxonomyPattern.NUMERICAL_CONFLICT,
        classification=GovernanceClass.DISPUTED,
        contexts=[{"text": "Only one context with 5"}],
    )
    r = Checker().check(c)
    assert not r.passed
    assert any(i.rule == "pattern_structure" for i in r.errors)


def test_numerical_conflict_with_two_digit_contexts_passes_structure() -> None:
    c = v6_case(
        pattern=TaxonomyPattern.NUMERICAL_CONFLICT,
        classification=GovernanceClass.DISPUTED,
        contexts=[
            {"text": "Apple costs €5"},
            {"text": "Apple costs €3"},
        ],
        governance_extra={"conflict_density": 0.8},  # avoid signal-coherence warning
    )
    r = Checker().check(c)
    assert r.passed, [i.message for i in r.errors]


# ---------------------------------------------------------------------------
# Signal coherence
# ---------------------------------------------------------------------------


def test_argmax_mismatch_is_error() -> None:
    c = v6_case(
        pattern=TaxonomyPattern.WRONG_SPECIFICITY,
        classification=GovernanceClass.ABSTAIN,
        governance_extra={"abstain": 0.10, "disputed": 0.10, "trustworthy": 0.80},
    )
    r = Checker().check(c)
    assert not r.passed
    assert any(i.rule == "argmax_mismatch" for i in r.errors)


def test_trustworthy_with_high_hallucination_pressure_is_error() -> None:
    c = v6_case(
        pattern=TaxonomyPattern.SINGLE_AUTHORITATIVE,
        classification=GovernanceClass.TRUSTWORTHY,
        governance_extra={"hallucination_pressure": 0.85},
    )
    r = Checker().check(c)
    assert not r.passed
    assert any(i.rule == "hallucination_signal_inverted" for i in r.errors)


def test_disputed_pattern_with_low_conflict_density_is_error() -> None:
    c = v6_case(
        pattern=TaxonomyPattern.NUMERICAL_CONFLICT,
        classification=GovernanceClass.DISPUTED,
        contexts=[{"text": "Foo 1"}, {"text": "Foo 2"}],
        governance_extra={"conflict_density": 0.10},
    )
    r = Checker().check(c)
    assert not r.passed
    assert any(i.rule == "conflict_density_low_for_disputed" for i in r.errors)


def test_trustworthy_pattern_with_high_conflict_density_is_error() -> None:
    c = v6_case(
        pattern=TaxonomyPattern.MULTI_SOURCE_CORROBORATION,
        classification=GovernanceClass.TRUSTWORTHY,
        contexts=[{"text": "X"}, {"text": "X agrees"}],
        governance_extra={"conflict_density": 0.80},
    )
    r = Checker().check(c)
    assert not r.passed
    assert any(i.rule == "conflict_density_high_for_trustworthy" for i in r.errors)


def test_trustworthy_with_low_evidence_sufficiency_is_error() -> None:
    c = v6_case(
        pattern=TaxonomyPattern.SINGLE_AUTHORITATIVE,
        classification=GovernanceClass.TRUSTWORTHY,
        governance_extra={"evidence_sufficiency": 0.10},
    )
    r = Checker().check(c)
    assert not r.passed
    assert any(i.rule == "evidence_sufficiency_low_for_trustworthy" for i in r.errors)


def test_abstain_with_high_evidence_sufficiency_is_warning_not_error() -> None:
    c = v6_case(
        pattern=TaxonomyPattern.WRONG_SPECIFICITY,
        classification=GovernanceClass.ABSTAIN,
        governance_extra={"evidence_sufficiency": 0.80},
    )
    r = Checker().check(c)
    assert r.passed, [i.message for i in r.errors]  # warning only
    assert any(i.rule == "evidence_sufficiency_high_for_abstain" for i in r.warnings)


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------


def test_v6_without_routing_is_warning() -> None:
    c = v6_case(routing=None)
    r = Checker().check(c)
    assert r.passed
    assert any(i.rule == "missing_routing" for i in r.warnings)


def test_routing_with_invalid_expert_fired_is_error() -> None:
    c = v6_case()
    c["routing"]["expert_fired"] = "not_a_domain"
    r = Checker().check(c)
    assert not r.passed
    assert any(i.rule == "invalid_expert_fired" for i in r.errors)


# ---------------------------------------------------------------------------
# Dedup
# ---------------------------------------------------------------------------


def test_dedup_hash_stable_under_whitespace_changes() -> None:
    a = v6_case(query="What is X?", contexts=[{"text": "Answer  is  Y"}])
    b = v6_case(query="  what is x? ", contexts=[{"text": "Answer is Y "}])
    assert case_dedup_hash(a) == case_dedup_hash(b)


def test_dedup_hash_changes_when_query_changes() -> None:
    a = v6_case(query="What is X?")
    b = v6_case(query="What is Z?")
    assert case_dedup_hash(a) != case_dedup_hash(b)


def test_dedup_hash_order_insensitive_for_contexts() -> None:
    a = v6_case(contexts=[{"text": "ctx 1"}, {"text": "ctx 2"}])
    b = v6_case(contexts=[{"text": "ctx 2"}, {"text": "ctx 1"}])
    assert case_dedup_hash(a) == case_dedup_hash(b)


def test_duplicate_content_is_error_when_seen_hashes_provided() -> None:
    a = v6_case(case_id="a", query="dup query", contexts=[{"text": "ctx"}])
    seen = {case_dedup_hash(a)}
    b = v6_case(case_id="b", query="dup query", contexts=[{"text": "ctx"}])
    r = Checker().check(b, seen_hashes=seen)
    assert not r.passed
    assert any(i.rule == "duplicate_content" for i in r.errors)


def test_check_batch_dedupes_within_batch() -> None:
    a = v6_case(case_id="a", query="batch dup", contexts=[{"text": "ctx"}])
    b = v6_case(case_id="b", query="batch dup", contexts=[{"text": "ctx"}])
    c = v6_case(case_id="c", query="batch unique", contexts=[{"text": "ctx"}])
    results = Checker().check_batch([a, b, c])
    assert results[0].passed
    assert not results[1].passed
    assert any(i.rule == "duplicate_content" for i in results[1].errors)
    assert results[2].passed


def test_hashes_from_helper() -> None:
    a = v6_case(case_id="a", query="q1")
    b = v6_case(case_id="b", query="q2")
    hs = hashes_from([a, b])
    assert len(hs) == 2


# ---------------------------------------------------------------------------
# CheckResult helpers
# ---------------------------------------------------------------------------


def test_check_result_passed_and_bool() -> None:
    r = CheckResult(case_id="x", issues=[])
    assert r.passed and bool(r)
    r.issues.append(CheckIssue(Severity.WARNING, "w", "warn"))
    assert r.passed and bool(r)  # warnings don't block
    r.issues.append(CheckIssue(Severity.ERROR, "e", "err"))
    assert not r.passed and not bool(r)
