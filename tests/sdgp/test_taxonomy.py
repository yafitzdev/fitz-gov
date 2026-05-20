"""Tests for fitz_gov.sdgp.taxonomy."""

from __future__ import annotations

import pytest

from fitz_gov.sdgp.taxonomy import (
    PATTERN_DESCRIPTIONS,
    PATTERN_MIN_CONTEXTS,
    PATTERN_TO_CLASS,
    PRIMARY_DOMAINS,
    Cell,
    Difficulty,
    Domain,
    GovernanceClass,
    PatternCheckResult,
    TaxonomyPattern,
    all_cells,
    check_pattern_structure,
    governance_class_of,
    parse_cell_id,
    patterns_of,
)


# ---------------------------------------------------------------------------
# Pattern <-> class mapping
# ---------------------------------------------------------------------------


def test_every_pattern_has_class_and_description() -> None:
    """Module-level asserts already enforce this; pin it as a real test too."""
    assert set(PATTERN_TO_CLASS.keys()) == set(TaxonomyPattern)
    assert set(PATTERN_DESCRIPTIONS.keys()) == set(TaxonomyPattern)


def test_six_patterns_per_class() -> None:
    for cls in GovernanceClass:
        ps = patterns_of(cls)
        assert len(ps) == 6, f"{cls.value} has {len(ps)} patterns, expected 6"


def test_governance_class_of_is_inverse_of_patterns_of() -> None:
    for pattern in TaxonomyPattern:
        cls = governance_class_of(pattern)
        assert pattern in patterns_of(cls)


def test_eighteen_total_patterns() -> None:
    assert len(list(TaxonomyPattern)) == 18


# ---------------------------------------------------------------------------
# Cells + cell_id round-trip
# ---------------------------------------------------------------------------


def test_cell_id_format() -> None:
    c = Cell(
        pattern=TaxonomyPattern.WRONG_SPECIFICITY,
        domain=Domain.HISTORY_GEOGRAPHY,
        difficulty=Difficulty.HARD,
    )
    assert c.cell_id == "wrong_specificity__history_geography__hard"
    assert str(c) == c.cell_id


def test_cell_governance_class() -> None:
    c = Cell(
        pattern=TaxonomyPattern.NUMERICAL_CONFLICT,
        domain=Domain.SCIENCE_MEDICINE,
        difficulty=Difficulty.MEDIUM,
    )
    assert c.governance_class == GovernanceClass.DISPUTED


def test_parse_cell_id_round_trip_over_all_cells() -> None:
    for cell in all_cells(include_meta_domain=True):
        parsed = parse_cell_id(cell.cell_id)
        assert parsed == cell


def test_parse_cell_id_rejects_malformed() -> None:
    with pytest.raises(ValueError):
        parse_cell_id("not_three_parts__only_two")
    with pytest.raises(ValueError):
        parse_cell_id("wrong_specificity__history_geography__not_a_difficulty")
    with pytest.raises(ValueError):
        parse_cell_id("not_a_pattern__history_geography__hard")


# ---------------------------------------------------------------------------
# Cell enumeration
# ---------------------------------------------------------------------------


def test_all_cells_default_excludes_meta_domain() -> None:
    cells = all_cells()
    assert len(cells) == 18 * 7 * 3  # 378
    assert all(c.domain != Domain.CONFLICT_DETECTION for c in cells)
    assert len(PRIMARY_DOMAINS) == 7


def test_all_cells_with_meta_domain() -> None:
    cells = all_cells(include_meta_domain=True)
    assert len(cells) == 18 * 8 * 3  # 432 (the ROADMAP estimate)
    assert any(c.domain == Domain.CONFLICT_DETECTION for c in cells)


def test_all_cells_unique() -> None:
    cells = all_cells(include_meta_domain=True)
    assert len({c.cell_id for c in cells}) == len(cells)


# ---------------------------------------------------------------------------
# Structural pattern checks
# ---------------------------------------------------------------------------


def _v6_case(contexts: list[dict] | list[str]) -> dict:
    """Minimal V6-shaped case (only the fields the checks read)."""
    return {"input": {"contexts": contexts}}


def _v51_case(contexts: list[str]) -> dict:
    """Minimal V5.1-shaped case (flat string contexts)."""
    return {"contexts": contexts}


class TestMinContextCount:
    def test_evidence_absent_passes_with_zero_contexts(self) -> None:
        r = check_pattern_structure(TaxonomyPattern.EVIDENCE_ABSENT, _v6_case([]))
        assert r.passed, r.reason

    def test_multi_source_requires_at_least_two_contexts(self) -> None:
        r = check_pattern_structure(
            TaxonomyPattern.MULTI_SOURCE_CORROBORATION,
            _v6_case([{"text": "only one"}]),
        )
        assert not r.passed

    def test_multi_source_passes_with_two_contexts(self) -> None:
        r = check_pattern_structure(
            TaxonomyPattern.MULTI_SOURCE_CORROBORATION,
            _v6_case([{"text": "first"}, {"text": "second"}]),
        )
        assert r.passed, r.reason


class TestNumericalChecks:
    def test_numerical_conflict_needs_two_digit_bearing_contexts(self) -> None:
        # 2 contexts but only 1 has digits → fail
        r = check_pattern_structure(
            TaxonomyPattern.NUMERICAL_CONFLICT,
            _v6_case([{"text": "Apple costs €5"}, {"text": "Apples are fruit"}]),
        )
        assert not r.passed
        assert "digit" in r.reason.lower()

    def test_numerical_conflict_passes_with_two_digit_contexts(self) -> None:
        r = check_pattern_structure(
            TaxonomyPattern.NUMERICAL_CONFLICT,
            _v6_case([{"text": "Apple costs €5"}, {"text": "Apple costs €3"}]),
        )
        assert r.passed, r.reason

    def test_quantitative_consensus_needs_digit_bearing(self) -> None:
        r = check_pattern_structure(
            TaxonomyPattern.QUANTITATIVE_CONSENSUS,
            _v6_case([{"text": "About three euros"}, {"text": "Around three euros"}]),
        )
        # Neither has digits → fail
        assert not r.passed


class TestAuthorityChecks:
    def test_authority_conflict_passes_with_spread(self) -> None:
        r = check_pattern_structure(
            TaxonomyPattern.AUTHORITY_CONFLICT,
            _v6_case([
                {"text": "Nature paper finds X", "authority_score": 0.92},
                {"text": "Blog post claims Y", "authority_score": 0.21},
            ]),
        )
        assert r.passed, r.reason

    def test_authority_conflict_fails_without_spread(self) -> None:
        r = check_pattern_structure(
            TaxonomyPattern.AUTHORITY_CONFLICT,
            _v6_case([
                {"text": "Source A", "authority_score": 0.81},
                {"text": "Source B", "authority_score": 0.83},
            ]),
        )
        assert not r.passed

    def test_authority_conflict_v51_shape_passes_without_scores(self) -> None:
        """V5.1 cases don't have authority_score; we don't penalize that here."""
        r = check_pattern_structure(
            TaxonomyPattern.AUTHORITY_CONFLICT,
            _v51_case(["high authority claim", "low authority claim"]),
        )
        assert r.passed, r.reason

    def test_expert_consensus_passes_with_uniform_high_authority(self) -> None:
        r = check_pattern_structure(
            TaxonomyPattern.EXPERT_CONSENSUS,
            _v6_case([
                {"text": "Study A", "authority_score": 0.85},
                {"text": "Study B", "authority_score": 0.91},
                {"text": "Study C", "authority_score": 0.78},
            ]),
        )
        assert r.passed, r.reason

    def test_expert_consensus_fails_with_low_authority(self) -> None:
        r = check_pattern_structure(
            TaxonomyPattern.EXPERT_CONSENSUS,
            _v6_case([
                {"text": "Study A", "authority_score": 0.85},
                {"text": "Forum post", "authority_score": 0.32},
            ]),
        )
        assert not r.passed


class TestVersionedShape:
    def test_v51_flat_contexts_work_for_min_count(self) -> None:
        r = check_pattern_structure(
            TaxonomyPattern.MULTI_SOURCE_CORROBORATION,
            _v51_case(["first", "second", "third"]),
        )
        assert r.passed, r.reason


# ---------------------------------------------------------------------------
# PatternCheckResult bool conversion
# ---------------------------------------------------------------------------


def test_pattern_check_result_is_truthy_on_pass() -> None:
    assert bool(PatternCheckResult(True, "ok"))
    assert not bool(PatternCheckResult(False, "nope"))
