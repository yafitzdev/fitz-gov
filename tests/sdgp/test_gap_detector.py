"""Tests for fitz_gov.sdgp.gap_detector."""

from __future__ import annotations

from pathlib import Path

import pytest

from fitz_gov.sdgp.gap_detector import (
    CellFilter,
    CellTarget,
    Gap,
    GapDetector,
    PriorityWeights,
    rank_from_vault,
)
from fitz_gov.sdgp.taxonomy import (
    Cell,
    Difficulty,
    Domain,
    GovernanceClass,
    PRIMARY_DOMAINS,
    TaxonomyPattern,
    all_cells,
)
from fitz_gov.sdgp.vault import Vault


# ---------------------------------------------------------------------------
# CellTarget
# ---------------------------------------------------------------------------


def test_cell_target_default() -> None:
    t = CellTarget(default=20)
    cell = Cell(
        pattern=TaxonomyPattern.WRONG_ENTITY,
        domain=Domain.HISTORY_GEOGRAPHY,
        difficulty=Difficulty.HARD,
    )
    assert t.for_cell(cell) == 20
    assert t.for_cell(cell.cell_id) == 20


def test_cell_target_override() -> None:
    cell = Cell(
        pattern=TaxonomyPattern.NUMERICAL_CONFLICT,
        domain=Domain.SCIENCE_MEDICINE,
        difficulty=Difficulty.HARD,
    )
    t = CellTarget(default=20, overrides={cell.cell_id: 50})
    assert t.for_cell(cell) == 50


# ---------------------------------------------------------------------------
# GapDetector.rank — basic behaviour
# ---------------------------------------------------------------------------


def test_rank_excludes_at_target_cells() -> None:
    detector = GapDetector()
    counts = {
        # Filled to target — should be excluded
        Cell(TaxonomyPattern.WRONG_ENTITY, Domain.HISTORY_GEOGRAPHY, Difficulty.HARD).cell_id: 20,
        # Empty — should be included
        Cell(TaxonomyPattern.NUMERICAL_CONFLICT, Domain.SCIENCE_MEDICINE, Difficulty.HARD).cell_id: 0,
    }
    gaps = detector.rank(counts, target=20)
    cell_ids = {g.cell.cell_id for g in gaps}
    assert "wrong_entity__history_geography__hard" not in cell_ids
    assert "numerical_conflict__science_medicine__hard" in cell_ids


def test_rank_sorted_biggest_first() -> None:
    detector = GapDetector()
    cell_a = Cell(TaxonomyPattern.WRONG_ENTITY, Domain.HISTORY_GEOGRAPHY, Difficulty.HARD)
    cell_b = Cell(TaxonomyPattern.NUMERICAL_CONFLICT, Domain.SCIENCE_MEDICINE, Difficulty.HARD)
    counts = {cell_a.cell_id: 5, cell_b.cell_id: 18}  # gap_a=15, gap_b=2
    gaps = detector.rank(counts, target=20)
    # Find both
    sub = [g for g in gaps if g.cell in (cell_a, cell_b)]
    assert sub[0].cell == cell_a  # biggest gap first


def test_rank_empty_cells_have_full_gap() -> None:
    detector = GapDetector()
    gaps = detector.rank({}, target=20)
    # Default V8 cell space (excluding meta) = 23 * 7 * 3 = 483
    assert len(gaps) == 483
    assert all(g.gap == 20 for g in gaps)


def test_rank_target_can_be_int_or_cell_target() -> None:
    detector = GapDetector()
    g1 = detector.rank({}, target=10)
    g2 = detector.rank({}, target=CellTarget(default=10))
    assert len(g1) == len(g2) == 483
    assert all(g.gap == 10 for g in g1)
    assert all(g.gap == 10 for g in g2)


def test_gap_coverage_ratio() -> None:
    cell = Cell(TaxonomyPattern.WRONG_ENTITY, Domain.HISTORY_GEOGRAPHY, Difficulty.HARD)
    detector = GapDetector()
    gaps = detector.rank({cell.cell_id: 5}, target=20)
    row = next(g for g in gaps if g.cell == cell)
    assert row.gap == 15
    assert row.coverage_ratio == 0.25


# ---------------------------------------------------------------------------
# Priority weights
# ---------------------------------------------------------------------------


def test_priority_weights_boost_hard_cases() -> None:
    detector = GapDetector()
    counts = {}  # all empty → all have gap=20
    weights = PriorityWeights(by_difficulty={Difficulty.HARD: 5.0})
    gaps = detector.rank(counts, target=20, weights=weights)
    # Top of the queue should be hard cells
    assert gaps[0].cell.difficulty == Difficulty.HARD


def test_priority_weights_boost_specific_pattern() -> None:
    detector = GapDetector()
    weights = PriorityWeights(
        by_pattern={TaxonomyPattern.NUMERICAL_CONFLICT: 10.0}
    )
    gaps = detector.rank({}, target=20, weights=weights)
    assert gaps[0].cell.pattern == TaxonomyPattern.NUMERICAL_CONFLICT


def test_priority_weights_boost_class() -> None:
    detector = GapDetector()
    weights = PriorityWeights(by_class={GovernanceClass.ABSTAIN: 100.0})
    gaps = detector.rank({}, target=20, weights=weights)
    from fitz_gov.sdgp.taxonomy import governance_class_of
    # First 10+ entries should all be ABSTAIN patterns
    for g in gaps[:5]:
        assert governance_class_of(g.cell.pattern) == GovernanceClass.ABSTAIN


def test_priority_weights_default_to_one() -> None:
    """No weights = unweighted ranking; biggest gap wins."""
    detector = GapDetector()
    cell_a = Cell(TaxonomyPattern.WRONG_ENTITY, Domain.HISTORY_GEOGRAPHY, Difficulty.HARD)
    cell_b = Cell(TaxonomyPattern.NUMERICAL_CONFLICT, Domain.SCIENCE_MEDICINE, Difficulty.HARD)
    counts = {cell_a.cell_id: 0, cell_b.cell_id: 10}
    gaps = detector.rank(counts, target=20)
    # cell_a has gap=20, cell_b has gap=10 — a wins
    relevant = [g for g in gaps if g.cell in (cell_a, cell_b)]
    assert relevant[0].cell == cell_a


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------


def test_filter_to_single_pattern() -> None:
    detector = GapDetector()
    flt = CellFilter(patterns={TaxonomyPattern.NUMERICAL_CONFLICT})
    gaps = detector.rank({}, target=20, filter=flt)
    # 7 primary domains * 3 difficulties = 21
    assert len(gaps) == 21
    assert all(g.cell.pattern == TaxonomyPattern.NUMERICAL_CONFLICT for g in gaps)


def test_filter_to_single_class() -> None:
    detector = GapDetector()
    flt = CellFilter(classes={GovernanceClass.DISPUTED})
    gaps = detector.rank({}, target=20, filter=flt)
    # 8 DISPUTED patterns * 7 domains * 3 difficulties = 168
    assert len(gaps) == 168


def test_filter_to_difficulty() -> None:
    detector = GapDetector()
    flt = CellFilter(difficulties={Difficulty.HARD})
    gaps = detector.rank({}, target=20, filter=flt)
    # 23 patterns * 7 domains * 1 difficulty = 161
    assert len(gaps) == 161
    assert all(g.cell.difficulty == Difficulty.HARD for g in gaps)


def test_filter_include_meta_domain() -> None:
    detector = GapDetector()
    flt = CellFilter(include_meta_domain=True)
    gaps = detector.rank({}, target=20, filter=flt)
    # 23 * 8 * 3 = 552
    assert len(gaps) == 552


def test_filter_excludes_meta_domain_by_default() -> None:
    detector = GapDetector()
    gaps = detector.rank({}, target=20)
    assert all(g.cell.domain != Domain.CONFLICT_DETECTION for g in gaps)


# ---------------------------------------------------------------------------
# Coverage summary
# ---------------------------------------------------------------------------


def test_coverage_summary_all_empty() -> None:
    detector = GapDetector()
    s = detector.coverage_summary({}, target=20)
    assert s["cells_considered"] == 483
    assert s["cells_empty"] == 483
    assert s["cells_at_target"] == 0
    assert s["total_cases"] == 0
    assert s["total_gap_to_fill"] == 483 * 20


def test_coverage_summary_some_filled() -> None:
    detector = GapDetector()
    cell = Cell(TaxonomyPattern.WRONG_ENTITY, Domain.HISTORY_GEOGRAPHY, Difficulty.HARD)
    counts = {cell.cell_id: 25}  # over target
    s = detector.coverage_summary(counts, target=20)
    assert s["cells_at_target"] == 1
    assert s["cells_with_some_cases"] == 1
    assert s["cells_empty"] == 482
    assert s["total_cases"] == 25
    assert s["total_gap_to_fill"] == 482 * 20


# ---------------------------------------------------------------------------
# Vault integration
# ---------------------------------------------------------------------------


def test_rank_from_vault_reads_cell_counts(tmp_path: Path) -> None:
    from fitz_gov.sdgp.vault import Provenance

    vault = Vault.open(tmp_path / "v")
    # Add a single case for a known cell
    cell = Cell(
        TaxonomyPattern.WRONG_ENTITY, Domain.HISTORY_GEOGRAPHY, Difficulty.HARD
    )
    case = {
        "taxonomy": {
            "governance_class": "ABSTAIN",
            "pattern": cell.pattern.value,
            "cell_id": cell.cell_id,
        },
        "input": {"query": "q", "contexts": [{"text": "c"}]},
        "id": "x",
    }
    vault.add(case, provenance=Provenance(provider="test"))
    gaps = rank_from_vault(vault, target=20)
    row = next(g for g in gaps if g.cell == cell)
    assert row.current == 1
    assert row.gap == 19
