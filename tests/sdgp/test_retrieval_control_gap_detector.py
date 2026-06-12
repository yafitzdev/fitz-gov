"""Tests for the V9 retrieval-control gap detector."""

from __future__ import annotations

import pytest

from fitz_gov.sdgp.retrieval_control_gap_detector import (
    CollapsedAnswerabilityShape,
    RetrievalControlCell,
    RetrievalControlCellFilter,
    RetrievalControlGapDetector,
    all_retrieval_control_cells,
    cell_for_case,
    collapse_answerability_shape,
    detailed_answerability_shapes_for,
    parse_retrieval_control_cell_id,
    retrieval_control_cell_counts,
)
from fitz_gov.sdgp.taxonomy import Difficulty, Domain, GovernanceClass


def test_collapse_answerability_shape_groups_detailed_v8_2_labels() -> None:
    assert collapse_answerability_shape("single_fact") == CollapsedAnswerabilityShape.DIRECT_ANSWER
    assert (
        collapse_answerability_shape("citation_required")
        == CollapsedAnswerabilityShape.DIRECT_ANSWER
    )
    assert collapse_answerability_shape("summary") == CollapsedAnswerabilityShape.SYNTHESIS_ANSWER
    assert collapse_answerability_shape("list") == CollapsedAnswerabilityShape.SET_ANSWER
    assert (
        collapse_answerability_shape("calculation")
        == CollapsedAnswerabilityShape.STRUCTURED_REASONING
    )
    with pytest.raises(ValueError):
        collapse_answerability_shape("not_a_shape")


def test_detailed_answerability_shapes_for_returns_v8_2_members() -> None:
    assert detailed_answerability_shapes_for("direct_answer") == (
        "single_fact",
        "exact_lookup",
        "yes_no",
        "citation_required",
    )
    assert detailed_answerability_shapes_for(CollapsedAnswerabilityShape.STRUCTURED_REASONING) == (
        "comparison",
        "timeline",
        "calculation",
    )


def test_cell_id_round_trip() -> None:
    cell = RetrievalControlCell(
        governance_class=GovernanceClass.TRUSTWORTHY,
        domain=Domain.SCIENCE_MEDICINE,
        difficulty=Difficulty.EASY,
        answerability_shape=CollapsedAnswerabilityShape.STRUCTURED_REASONING,
    )
    assert cell.cell_id == "trustworthy__science_medicine__easy__structured_reasoning"
    assert parse_retrieval_control_cell_id(cell.cell_id) == cell


def test_all_retrieval_control_cells_defaults_to_minority_shapes() -> None:
    cells = all_retrieval_control_cells()
    assert len(cells) == 189
    assert all(
        cell.answerability_shape != CollapsedAnswerabilityShape.DIRECT_ANSWER for cell in cells
    )


def test_all_retrieval_control_cells_can_include_direct_answer() -> None:
    cells = all_retrieval_control_cells(include_direct_answer=True)
    assert len(cells) == 252
    assert any(
        cell.answerability_shape == CollapsedAnswerabilityShape.DIRECT_ANSWER for cell in cells
    )


def test_cell_for_case_reads_canonical_retrieval_control_row() -> None:
    case = {
        "governance": {"classification": "TRUSTWORTHY"},
        "routing": {
            "expert_fired": "science_medicine",
            "retrieval_control": {
                "answerability_shape": {"kind": "comparison"},
            },
        },
        "meta": {"difficulty": "hard"},
    }
    cell = cell_for_case(case)
    assert cell is not None
    assert cell.cell_id == ("trustworthy__science_medicine__hard__structured_reasoning")


def test_cell_for_case_reads_flattened_training_row() -> None:
    row = {
        "label": "ABSTAIN",
        "route": "law_policy",
        "difficulty": "medium",
        "answerability_shape": "exhaustive_list",
    }
    cell = cell_for_case(row)
    assert cell is not None
    assert cell.cell_id == "abstain__law_policy__medium__set_answer"


def test_retrieval_control_cell_counts_skips_incomplete_rows() -> None:
    rows = [
        {
            "label": "ABSTAIN",
            "route": "law_policy",
            "difficulty": "medium",
            "answerability_shape": "summary",
        },
        {
            "label": "ABSTAIN",
            "route": "law_policy",
            "difficulty": "medium",
            "answerability_shape": "summary",
        },
        {"label": "ABSTAIN", "route": "law_policy"},
    ]
    counts = retrieval_control_cell_counts(rows)
    assert counts == {"abstain__law_policy__medium__synthesis_answer": 2}


def test_gap_detector_ranks_biggest_gap_first_and_excludes_filled_cells() -> None:
    detector = RetrievalControlGapDetector()
    filled = RetrievalControlCell(
        GovernanceClass.ABSTAIN,
        Domain.LAW_POLICY,
        Difficulty.MEDIUM,
        CollapsedAnswerabilityShape.SET_ANSWER,
    )
    sparse = RetrievalControlCell(
        GovernanceClass.DISPUTED,
        Domain.ECONOMICS_FINANCE,
        Difficulty.EASY,
        CollapsedAnswerabilityShape.SET_ANSWER,
    )
    gaps = detector.rank(
        {
            filled.cell_id: 10,
            sparse.cell_id: 2,
        },
        target=10,
        filter=RetrievalControlCellFilter(
            answerability_shapes={CollapsedAnswerabilityShape.SET_ANSWER}
        ),
    )
    assert filled.cell_id not in {gap.cell.cell_id for gap in gaps}
    row = next(gap for gap in gaps if gap.cell == sparse)
    assert row.gap == 8
    assert gaps[0].gap == 10


def test_coverage_summary_groups_by_answerability_shape() -> None:
    detector = RetrievalControlGapDetector()
    flt = RetrievalControlCellFilter(
        classes={GovernanceClass.TRUSTWORTHY},
        domains={Domain.SCIENCE_MEDICINE},
        difficulties={Difficulty.EASY},
    )
    summary = detector.coverage_summary({}, target=5, filter=flt)
    assert summary["cells_considered"] == 3
    assert summary["cells_empty"] == 3
    assert summary["total_gap_to_fill"] == 15
    assert summary["by_answerability_shape"]["synthesis_answer"]["total_gap_to_fill"] == 5
    assert summary["by_answerability_shape"]["set_answer"]["total_gap_to_fill"] == 5
    assert summary["by_answerability_shape"]["structured_reasoning"]["total_gap_to_fill"] == 5
