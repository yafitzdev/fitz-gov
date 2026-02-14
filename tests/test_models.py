"""Tests for fitz_gov.models."""

import pytest
from datetime import datetime, timezone

from fitz_gov.models import (
    AnswerMode,
    FitzGovCase,
    FitzGovCaseResult,
    FitzGovCategory,
    FitzGovCategoryResult,
    FitzGovConfusionMatrix,
    FitzGovResult,
    Tier0Result,
    Tier1Result,
    TieredResult,
)


# ---------------------------------------------------------------------------
# AnswerMode & FitzGovCategory enums
# ---------------------------------------------------------------------------


class TestEnums:
    def test_answer_mode_values(self):
        """TRUSTWORTHY, DISPUTED, ABSTAIN exist as AnswerMode values."""
        assert AnswerMode.TRUSTWORTHY.value == "trustworthy"
        assert AnswerMode.DISPUTED.value == "disputed"
        assert AnswerMode.ABSTAIN.value == "abstain"
        assert len(AnswerMode) == 3

    def test_category_values(self):
        """All 6 FitzGovCategory values exist."""
        expected = {
            "abstention",
            "dispute",
            "trustworthy_hedged",
            "trustworthy_direct",
            "grounding",
            "relevance",
        }
        actual = {cat.value for cat in FitzGovCategory}
        assert actual == expected
        assert len(FitzGovCategory) == 6


# ---------------------------------------------------------------------------
# FitzGovCase serialization
# ---------------------------------------------------------------------------


class TestFitzGovCase:
    def test_case_to_dict_roundtrip(self, sample_governance_case):
        """from_dict(case.to_dict()) preserves all essential fields."""
        d = sample_governance_case.to_dict()
        restored = FitzGovCase.from_dict(d)

        assert restored.id == sample_governance_case.id
        assert restored.category == sample_governance_case.category
        assert restored.subcategory == sample_governance_case.subcategory
        assert restored.query == sample_governance_case.query
        assert restored.contexts == sample_governance_case.contexts
        assert restored.expected_mode == sample_governance_case.expected_mode
        assert restored.description == sample_governance_case.description
        assert restored.rationale == sample_governance_case.rationale
        assert restored.difficulty == sample_governance_case.difficulty
        assert restored.domain == sample_governance_case.domain
        assert restored.query_type == sample_governance_case.query_type
        assert restored.reasoning_type == sample_governance_case.reasoning_type
        assert restored.evidence_pattern == sample_governance_case.evidence_pattern

    def test_case_to_dict_includes_classification(self, sample_governance_case):
        """domain, query_type etc. appear in dict when set."""
        d = sample_governance_case.to_dict()

        assert d["domain"] == "finance"
        assert d["query_type"] == "what"
        assert d["reasoning_type"] == "factual"
        assert d["evidence_pattern"] == "absent"

    def test_case_to_dict_omits_empty_optionals(self):
        """No forbidden_claims key if empty list."""
        case = FitzGovCase(
            id="test_min_001",
            category=FitzGovCategory.ABSTENTION,
            subcategory="test",
            query="Test?",
            contexts=["ctx"],
            expected_mode=AnswerMode.ABSTAIN,
            description="desc",
            rationale="rat",
        )
        d = case.to_dict()

        assert "forbidden_claims" not in d
        assert "required_elements" not in d
        assert "forbidden_elements" not in d
        assert "context_sources" not in d
        # source_type defaults to "single" which is also omitted
        assert "source_type" not in d

    def test_case_from_dict_defaults(self):
        """Missing optional fields get proper defaults."""
        data = {
            "id": "test_default_001",
            "category": "abstention",
            "query": "What?",
            "contexts": ["ctx"],
            "expected_mode": "abstain",
        }
        case = FitzGovCase.from_dict(data)

        assert case.subcategory == "unknown"
        assert case.difficulty == "medium"
        assert case.description == ""
        assert case.rationale == ""
        assert case.forbidden_claims == []
        assert case.required_elements == []
        assert case.forbidden_elements == []
        assert case.evaluation_config == {}
        assert case.context_sources == []
        assert case.metadata == {}
        assert case.domain == ""
        assert case.query_type == ""
        assert case.source_type == "single"
        assert case.context_count == 0
        assert case.reasoning_type == ""
        assert case.evidence_pattern == ""

    def test_case_from_dict_minimal(self):
        """Works with just id, category, query, contexts, expected_mode."""
        data = {
            "id": "min_001",
            "category": "dispute",
            "query": "Are sources aligned?",
            "contexts": ["A says yes.", "B says no."],
            "expected_mode": "disputed",
        }
        case = FitzGovCase.from_dict(data)

        assert case.id == "min_001"
        assert case.category == FitzGovCategory.DISPUTE
        assert case.expected_mode == AnswerMode.DISPUTED
        assert len(case.contexts) == 2


# ---------------------------------------------------------------------------
# FitzGovCaseResult
# ---------------------------------------------------------------------------


class TestFitzGovCaseResult:
    def test_case_result_to_dict(self, sample_governance_case):
        """FitzGovCaseResult serializes correctly."""
        result = FitzGovCaseResult(
            case=sample_governance_case,
            passed=False,
            response="The revenue was $5 billion.",
            actual_mode=AnswerMode.TRUSTWORTHY,
            failure_reason="Mode mismatch: expected abstain, got trustworthy",
        )
        d = result.to_dict()

        assert d["case_id"] == "test_abstain_001"
        assert d["passed"] is False
        assert d["response"] == "The revenue was $5 billion."
        assert d["actual_mode"] == "trustworthy"
        assert d["failure_reason"] == "Mode mismatch: expected abstain, got trustworthy"
        assert d["llm_validations"] == []


# ---------------------------------------------------------------------------
# FitzGovCategoryResult
# ---------------------------------------------------------------------------


class TestFitzGovCategoryResult:
    def test_category_result_accuracy(self, sample_governance_case):
        """FitzGovCategoryResult accuracy calculation."""
        case_result = FitzGovCaseResult(
            case=sample_governance_case,
            passed=True,
            response="I don't have that data.",
            actual_mode=AnswerMode.ABSTAIN,
        )
        cat_result = FitzGovCategoryResult(
            category=FitzGovCategory.ABSTENTION,
            accuracy=0.75,
            num_correct=3,
            num_total=4,
            case_results=[case_result],
        )

        assert cat_result.accuracy == 0.75
        assert cat_result.num_correct == 3
        assert cat_result.num_total == 4

        d = cat_result.to_dict()
        assert d["category"] == "abstention"
        assert d["accuracy"] == 0.75
        assert len(d["case_results"]) == 1


# ---------------------------------------------------------------------------
# FitzGovConfusionMatrix
# ---------------------------------------------------------------------------


class TestConfusionMatrix:
    def test_confusion_matrix_init(self):
        """Empty matrix has all 3x3 modes."""
        cm = FitzGovConfusionMatrix()

        modes = ["trustworthy", "disputed", "abstain"]
        for exp in modes:
            assert exp in cm.matrix
            for act in modes:
                assert act in cm.matrix[exp]
                assert cm.matrix[exp][act] == 0

    def test_confusion_matrix_add(self):
        """Adding predictions updates correct cell."""
        cm = FitzGovConfusionMatrix()
        cm.add(AnswerMode.ABSTAIN, AnswerMode.TRUSTWORTHY)

        assert cm.matrix["abstain"]["trustworthy"] == 1
        assert cm.matrix["abstain"]["abstain"] == 0

        cm.add(AnswerMode.ABSTAIN, AnswerMode.TRUSTWORTHY)
        assert cm.matrix["abstain"]["trustworthy"] == 2

    def test_confusion_matrix_accuracy(self):
        """Diagonal sum / total."""
        cm = FitzGovConfusionMatrix()
        # 2 correct trustworthy
        cm.add(AnswerMode.TRUSTWORTHY, AnswerMode.TRUSTWORTHY)
        cm.add(AnswerMode.TRUSTWORTHY, AnswerMode.TRUSTWORTHY)
        # 1 correct abstain
        cm.add(AnswerMode.ABSTAIN, AnswerMode.ABSTAIN)
        # 1 wrong
        cm.add(AnswerMode.DISPUTED, AnswerMode.ABSTAIN)

        # 3 correct out of 4
        assert cm.get_accuracy() == pytest.approx(0.75)

    def test_confusion_matrix_str(self):
        """__str__ includes TRST, DISP, ABST."""
        cm = FitzGovConfusionMatrix()
        text = str(cm)

        assert "TRST" in text
        assert "DISP" in text
        assert "ABST" in text
        assert "Confusion Matrix" in text


# ---------------------------------------------------------------------------
# FitzGovResult
# ---------------------------------------------------------------------------


class TestFitzGovResult:
    def test_fitz_gov_result_str(self, sample_governance_case):
        """FitzGovResult __str__ includes categories."""
        case_result = FitzGovCaseResult(
            case=sample_governance_case,
            passed=True,
            response="I cannot answer.",
            actual_mode=AnswerMode.ABSTAIN,
        )
        cat_result = FitzGovCategoryResult(
            category=FitzGovCategory.ABSTENTION,
            accuracy=1.0,
            num_correct=1,
            num_total=1,
            case_results=[case_result],
        )
        result = FitzGovResult(
            overall_accuracy=1.0,
            category_results={FitzGovCategory.ABSTENTION: cat_result},
            confusion_matrix=FitzGovConfusionMatrix(),
            num_cases=1,
            evaluation_time_seconds=0.5,
        )
        text = str(result)

        assert "fitz-gov Results" in text
        assert "abstention" in text
        assert "Governance Mode Categories" in text


# ---------------------------------------------------------------------------
# Tier0Result
# ---------------------------------------------------------------------------


class TestTier0Result:
    def _make_tier0(self, accuracy, threshold=0.95):
        """Helper to build a Tier0Result."""
        return Tier0Result(
            passed=accuracy >= threshold,
            accuracy=accuracy,
            threshold=threshold,
            category_results={},
            failure_cases=[],
            num_cases=60,
        )

    def test_tier0_result_passed(self):
        """passed=True when accuracy >= threshold."""
        t0 = self._make_tier0(0.97)
        assert t0.passed is True

    def test_tier0_result_failed(self):
        """passed=False when accuracy < threshold."""
        t0 = self._make_tier0(0.90)
        assert t0.passed is False

        text = str(t0)
        assert "FAILED" in text


# ---------------------------------------------------------------------------
# Tier1Result
# ---------------------------------------------------------------------------


class TestTier1Result:
    def test_tier1_result_difficulty(self):
        """difficulty_breakdown dict has correct values."""
        t1 = Tier1Result(
            accuracy=0.72,
            category_results={},
            confusion_matrix=FitzGovConfusionMatrix(),
            difficulty_breakdown={"medium": 0.80, "hard": 0.65},
            num_cases=1679,
        )

        assert t1.difficulty_breakdown["medium"] == pytest.approx(0.80)
        assert t1.difficulty_breakdown["hard"] == pytest.approx(0.65)

        text = str(t1)
        assert "medium" in text
        assert "hard" in text
        assert "By Difficulty" in text


# ---------------------------------------------------------------------------
# TieredResult
# ---------------------------------------------------------------------------


class TestTieredResult:
    def _make_tier0(self, passed, accuracy=0.97):
        return Tier0Result(
            passed=passed,
            accuracy=accuracy,
            threshold=0.95,
            category_results={},
            failure_cases=[],
            num_cases=60,
        )

    def _make_tier1(self, accuracy=0.72):
        return Tier1Result(
            accuracy=accuracy,
            category_results={},
            confusion_matrix=FitzGovConfusionMatrix(),
            difficulty_breakdown={"medium": 0.80, "hard": 0.65},
            num_cases=1679,
        )

    def test_tiered_result_gating(self):
        """tier1=None when tier0 failed and gating enabled."""
        tr = TieredResult(
            tier0=self._make_tier0(passed=False, accuracy=0.80),
            tier1=None,
            gating_enabled=True,
            evaluation_time_seconds=1.0,
        )

        assert tr.tier0.passed is False
        assert tr.tier1 is None
        assert tr.gating_enabled is True

        text = str(tr)
        assert "Skipped" in text

    def test_tiered_result_str(self):
        """TieredResult __str__ includes both tiers."""
        tr = TieredResult(
            tier0=self._make_tier0(passed=True),
            tier1=self._make_tier1(),
            gating_enabled=True,
            evaluation_time_seconds=5.0,
        )
        text = str(tr)

        assert "TIER 0" in text
        assert "TIER 1" in text
        assert "PASSED" in text
        assert "Summary" in text

    def test_tiered_result_properties(self):
        """tier0_passed and tier1_accuracy properties work."""
        tr = TieredResult(
            tier0=self._make_tier0(passed=True),
            tier1=self._make_tier1(accuracy=0.72),
            gating_enabled=True,
            evaluation_time_seconds=5.0,
        )

        assert tr.tier0_passed is True
        assert tr.tier1_accuracy == pytest.approx(0.72)

        # When tier1 is None
        tr_no_t1 = TieredResult(
            tier0=self._make_tier0(passed=False, accuracy=0.80),
            tier1=None,
            gating_enabled=True,
            evaluation_time_seconds=1.0,
        )
        assert tr_no_t1.tier0_passed is False
        assert tr_no_t1.tier1_accuracy is None
