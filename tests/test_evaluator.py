# tests/test_evaluator.py
"""Tests for the fitz-gov evaluator."""

import pytest

from fitz_gov.evaluator import FitzGovEvaluator, GOVERNANCE_MODE_CATEGORIES
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
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def evaluator():
    """Evaluator with LLM validation disabled."""
    return FitzGovEvaluator(llm_validation=False)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_governance_case(category, expected_mode, **kwargs):
    """Create a governance-category test case with sensible defaults."""
    defaults = {
        "id": "test_001",
        "subcategory": "test",
        "query": "Test query?",
        "contexts": ["Test context."],
        "description": "Test",
        "rationale": "Test",
        "difficulty": "medium",
        "evaluation_config": {"mode": "governance", "check_mode_match": True},
    }
    defaults.update(kwargs)
    return FitzGovCase(
        category=FitzGovCategory(category),
        expected_mode=AnswerMode(expected_mode),
        **defaults,
    )


def make_grounding_case(**kwargs):
    """Create a grounding test case with sensible defaults."""
    defaults = {
        "id": "test_ground_001",
        "category": FitzGovCategory.GROUNDING,
        "subcategory": "numerical_hallucination",
        "query": "What was the budget?",
        "contexts": ["The project had 47 services."],
        "expected_mode": AnswerMode.TRUSTWORTHY,
        "description": "Test",
        "rationale": "Test",
        "difficulty": "medium",
        "forbidden_claims": ["budget (was|is) \\$?\\d"],
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": [],
        },
    }
    defaults.update(kwargs)
    return FitzGovCase(**defaults)


def make_relevance_case(**kwargs):
    """Create a relevance test case with sensible defaults.

    NOTE: Because RELEVANCE is in GOVERNANCE_MODE_CATEGORIES, evaluate_case
    routes these to _evaluate_governance (not _evaluate_relevance).  Tests
    that exercise the content-check logic call _evaluate_relevance directly.
    """
    defaults = {
        "id": "test_rel_001",
        "category": FitzGovCategory.RELEVANCE,
        "subcategory": "partial_answer",
        "query": "What are the results AND timeline?",
        "contexts": ["Success rate was 85%."],
        "expected_mode": AnswerMode.TRUSTWORTHY,
        "description": "Test",
        "rationale": "Test",
        "difficulty": "medium",
        "required_elements": ["timeline", "not mentioned"],
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 1,
        },
    }
    defaults.update(kwargs)
    return FitzGovCase(**defaults)


# ===========================================================================
# Governance mode tests
# ===========================================================================


class TestGovernanceMode:
    """Tests for governance mode matching via evaluate_case."""

    def test_abstention_correct_mode(self, evaluator):
        """ABSTAIN expected and ABSTAIN given should pass."""
        case = make_governance_case("abstention", "abstain")
        result = evaluator.evaluate_case(case, "I cannot answer.", AnswerMode.ABSTAIN)
        assert result.passed is True
        assert result.failure_reason is None

    def test_abstention_wrong_mode(self, evaluator):
        """ABSTAIN expected but TRUSTWORTHY given should fail."""
        case = make_governance_case("abstention", "abstain")
        result = evaluator.evaluate_case(case, "The answer is 42.", AnswerMode.TRUSTWORTHY)
        assert result.passed is False
        assert "Expected abstain" in result.failure_reason
        assert "got trustworthy" in result.failure_reason

    def test_dispute_correct_mode(self, evaluator):
        """DISPUTED expected and DISPUTED given should pass."""
        case = make_governance_case("dispute", "disputed")
        result = evaluator.evaluate_case(case, "Sources disagree.", AnswerMode.DISPUTED)
        assert result.passed is True
        assert result.failure_reason is None

    def test_trustworthy_correct_mode(self, evaluator):
        """TRUSTWORTHY expected and TRUSTWORTHY given should pass."""
        case = make_governance_case("trustworthy_direct", "trustworthy")
        result = evaluator.evaluate_case(case, "Yes, confirmed.", AnswerMode.TRUSTWORTHY)
        assert result.passed is True

    def test_governance_no_mode_fails(self, evaluator):
        """Passing actual_mode=None for a governance case should fail."""
        case = make_governance_case("abstention", "abstain")
        result = evaluator.evaluate_case(case, "anything", actual_mode=None)
        assert result.passed is False
        assert "No actual_mode provided" in result.failure_reason

    def test_mode_matching_is_exact(self, evaluator):
        """Each distinct mode is not equal to the others."""
        case_abstain = make_governance_case("abstention", "abstain")
        case_dispute = make_governance_case("dispute", "disputed")
        case_trust = make_governance_case("trustworthy_direct", "trustworthy")

        # TRUSTWORTHY != DISPUTED
        r1 = evaluator.evaluate_case(case_trust, "x", AnswerMode.DISPUTED)
        assert r1.passed is False

        # DISPUTED != ABSTAIN
        r2 = evaluator.evaluate_case(case_dispute, "x", AnswerMode.ABSTAIN)
        assert r2.passed is False

        # ABSTAIN != TRUSTWORTHY
        r3 = evaluator.evaluate_case(case_abstain, "x", AnswerMode.TRUSTWORTHY)
        assert r3.passed is False


# ===========================================================================
# Grounding evaluation tests
# ===========================================================================


class TestGroundingEvaluation:
    """Tests for _evaluate_grounding (forbidden claims / hallucination detection)."""

    def test_grounding_no_forbidden_match(self, evaluator):
        """Response without any forbidden pattern match should pass."""
        case = make_grounding_case()
        result = evaluator.evaluate_case(case, "The project deployed 47 services.")
        assert result.passed is True

    def test_grounding_forbidden_match(self, evaluator):
        """Response containing a forbidden regex match should fail."""
        case = make_grounding_case()
        result = evaluator.evaluate_case(case, "The budget was $5 million.")
        assert result.passed is False
        assert "HALLUCINATION" in result.failure_reason

    def test_grounding_allowed_phrase_override(self, evaluator):
        """A forbidden match inside an allowed phrase should still pass."""
        case = make_grounding_case(
            evaluation_config={
                "mode": "answer_quality",
                "use_regex": True,
                "case_insensitive": True,
                # allowed_phrases is a regex that matches the *response*
                "allowed_phrases": ["budget (was|is) not specified"],
            },
        )
        # The forbidden claim "budget (was|is) \$?\d" matches, but the response
        # also matches the allowed phrase pattern "budget (was|is) not specified",
        # so _check_allowed_phrases returns True and the violation is cleared.
        result = evaluator.evaluate_case(
            case, "The budget is not specified in the documents."
        )
        assert result.passed is True

    def test_grounding_regex_case_insensitive(self, evaluator):
        """Case-insensitive matching should catch uppercase variants."""
        case = make_grounding_case(
            evaluation_config={
                "mode": "answer_quality",
                "use_regex": True,
                "case_insensitive": True,
                "allowed_phrases": [],
            },
        )
        result = evaluator.evaluate_case(case, "The BUDGET WAS $9 allocated.")
        assert result.passed is False

    def test_grounding_multiple_patterns(self, evaluator):
        """Fail if ANY forbidden pattern matches."""
        case = make_grounding_case(
            forbidden_claims=["pattern_alpha", "pattern_beta"],
            evaluation_config={
                "mode": "answer_quality",
                "use_regex": False,
                "case_insensitive": True,
                "allowed_phrases": [],
            },
        )
        # Only pattern_beta is present, but that's enough to fail
        result = evaluator.evaluate_case(case, "This has pattern_beta in it.")
        assert result.passed is False
        assert "HALLUCINATION" in result.failure_reason

    def test_grounding_invalid_regex_fallback(self, evaluator):
        """Invalid regex falls back to substring check."""
        case = make_grounding_case(
            forbidden_claims=["budget[invalid"],  # broken regex
            evaluation_config={
                "mode": "answer_quality",
                "use_regex": True,
                "case_insensitive": True,
                "allowed_phrases": [],
            },
        )
        # The invalid regex triggers re.error, then substring fallback kicks in
        result = evaluator.evaluate_case(case, "The budget[invalid is mentioned.")
        assert result.passed is False
        assert "HALLUCINATION" in result.failure_reason


# ===========================================================================
# Relevance evaluation tests
# ===========================================================================


class TestRelevanceEvaluation:
    """Tests for _evaluate_relevance content checks.

    Because RELEVANCE is in GOVERNANCE_MODE_CATEGORIES, evaluate_case routes
    relevance cases to _evaluate_governance (mode matching), NOT to
    _evaluate_relevance.  These tests therefore call _evaluate_relevance
    directly to exercise the content-check logic.
    """

    def test_relevance_required_present(self, evaluator):
        """Response that contains a required element should pass."""
        case = make_relevance_case()
        result = evaluator._evaluate_relevance(
            case, "The timeline was not mentioned in the source."
        )
        assert result.passed is True

    def test_relevance_required_missing(self, evaluator):
        """Response missing all required elements should fail."""
        case = make_relevance_case()
        result = evaluator._evaluate_relevance(case, "The success rate was 85%.")
        assert result.passed is False
        assert "Missing required elements" in result.failure_reason

    def test_relevance_min_required_1(self, evaluator):
        """Only 1 of N required elements needed when min_required=1 (default)."""
        case = make_relevance_case(
            required_elements=["alpha", "beta", "gamma"],
            evaluation_config={
                "mode": "answer_quality",
                "use_regex": False,
                "case_insensitive": True,
                "min_required": 1,
            },
        )
        # Only "beta" present
        result = evaluator._evaluate_relevance(case, "We found beta results.")
        assert result.passed is True

    def test_relevance_min_required_2(self, evaluator):
        """Need 2+ elements when min_required=2."""
        case = make_relevance_case(
            required_elements=["alpha", "beta", "gamma"],
            evaluation_config={
                "mode": "answer_quality",
                "use_regex": False,
                "case_insensitive": True,
                "min_required": 2,
            },
        )
        # Only 1 of 3 present -> fail
        result_one = evaluator._evaluate_relevance(case, "Found alpha here.")
        assert result_one.passed is False

        # 2 of 3 present -> pass
        result_two = evaluator._evaluate_relevance(
            case, "Found alpha and beta here."
        )
        assert result_two.passed is True

    def test_relevance_forbidden_elements(self, evaluator):
        """Response with a forbidden element should fail even if required present."""
        case = make_relevance_case(
            required_elements=["success"],
            forbidden_elements=["guaranteed"],
            evaluation_config={
                "mode": "answer_quality",
                "use_regex": False,
                "case_insensitive": True,
                "min_required": 1,
            },
        )
        result = evaluator._evaluate_relevance(
            case, "The success is guaranteed by design."
        )
        assert result.passed is False
        assert "FALSE_CONFIDENCE" in result.failure_reason

    def test_relevance_case_insensitive(self, evaluator):
        """Case-insensitive element matching should find uppercase elements."""
        case = make_relevance_case(
            required_elements=["timeline"],
            evaluation_config={
                "mode": "answer_quality",
                "use_regex": False,
                "case_insensitive": True,
                "min_required": 1,
            },
        )
        result = evaluator._evaluate_relevance(case, "The TIMELINE was not given.")
        assert result.passed is True


# ===========================================================================
# Batch evaluation tests
# ===========================================================================


class TestEvaluateAll:
    """Tests for evaluate_all batch evaluation."""

    def test_evaluate_all_returns_result(self, evaluator):
        """evaluate_all should return a FitzGovResult instance."""
        case = make_governance_case("abstention", "abstain")
        result = evaluator.evaluate_all(
            [case], ["I cannot answer."], [AnswerMode.ABSTAIN]
        )
        assert isinstance(result, FitzGovResult)
        assert result.num_cases == 1

    def test_evaluate_all_category_breakdown(self, evaluator):
        """Results should contain per-category accuracy."""
        cases = [
            make_governance_case("abstention", "abstain", id="a1"),
            make_governance_case("abstention", "abstain", id="a2"),
            make_governance_case("dispute", "disputed", id="d1"),
        ]
        responses = ["no answer", "wrong answer", "sources conflict"]
        modes = [AnswerMode.ABSTAIN, AnswerMode.TRUSTWORTHY, AnswerMode.DISPUTED]

        result = evaluator.evaluate_all(cases, responses, modes)

        # Abstention: 1/2 correct
        abstention_result = result.category_results[FitzGovCategory.ABSTENTION]
        assert abstention_result.accuracy == pytest.approx(0.5)
        assert abstention_result.num_correct == 1
        assert abstention_result.num_total == 2

        # Dispute: 1/1 correct
        dispute_result = result.category_results[FitzGovCategory.DISPUTE]
        assert dispute_result.accuracy == pytest.approx(1.0)

    def test_evaluate_all_confusion_matrix(self, evaluator):
        """Confusion matrix should be populated for governance categories."""
        cases = [
            make_governance_case("abstention", "abstain", id="a1"),
            make_governance_case("dispute", "disputed", id="d1"),
        ]
        responses = ["I cannot", "It conflicts"]
        modes = [AnswerMode.TRUSTWORTHY, AnswerMode.DISPUTED]

        result = evaluator.evaluate_all(cases, responses, modes)
        matrix = result.confusion_matrix.matrix

        # Expected=abstain, actual=trustworthy -> count 1
        assert matrix["abstain"]["trustworthy"] == 1
        # Expected=disputed, actual=disputed -> count 1
        assert matrix["disputed"]["disputed"] == 1

    def test_evaluate_all_length_mismatch(self, evaluator):
        """Raises ValueError if cases and responses differ in length."""
        case = make_governance_case("abstention", "abstain")
        with pytest.raises(ValueError, match="cases and responses must have same length"):
            evaluator.evaluate_all([case], ["a", "b"])

        # Also test modes length mismatch
        with pytest.raises(ValueError, match="modes must have same length"):
            evaluator.evaluate_all(
                [case], ["a"], [AnswerMode.ABSTAIN, AnswerMode.DISPUTED]
            )


# ===========================================================================
# Tiered evaluation tests
# ===========================================================================


class TestTieredEvaluation:
    """Tests for evaluate_tiered (tier 0 + tier 1 structure)."""

    def _make_tier_cases(self, n, category="abstention", expected="abstain"):
        """Create n identical governance cases with sequential ids."""
        return [
            make_governance_case(category, expected, id=f"tier_{i}")
            for i in range(n)
        ]

    def test_tiered_tier0_pass(self, evaluator):
        """Tier0 accuracy >= threshold should set passed=True."""
        cases = self._make_tier_cases(4)
        responses = ["x"] * 4
        modes = [AnswerMode.ABSTAIN] * 4  # all correct

        tier1_cases = self._make_tier_cases(2, "dispute", "disputed")
        tier1_responses = ["x"] * 2
        tier1_modes = [AnswerMode.DISPUTED] * 2

        result = evaluator.evaluate_tiered(
            cases, responses, modes,
            tier1_cases, tier1_responses, tier1_modes,
            tier0_threshold=0.95,
        )
        assert result.tier0.passed is True
        assert result.tier0.accuracy == pytest.approx(1.0)
        assert result.tier1 is not None

    def test_tiered_tier0_fail_gates_tier1(self, evaluator):
        """Tier0 below threshold with gating=True should leave tier1=None."""
        cases = self._make_tier_cases(4)
        responses = ["x"] * 4
        # Only 1 of 4 correct -> 25% < 95% threshold
        modes = [
            AnswerMode.ABSTAIN,
            AnswerMode.TRUSTWORTHY,
            AnswerMode.TRUSTWORTHY,
            AnswerMode.TRUSTWORTHY,
        ]

        tier1_cases = self._make_tier_cases(2, "dispute", "disputed")
        tier1_responses = ["x"] * 2
        tier1_modes = [AnswerMode.DISPUTED] * 2

        result = evaluator.evaluate_tiered(
            cases, responses, modes,
            tier1_cases, tier1_responses, tier1_modes,
            tier0_threshold=0.95,
            gating_enabled=True,
        )
        assert result.tier0.passed is False
        assert result.tier1 is None

    def test_tiered_tier0_fail_no_gating(self, evaluator):
        """Tier0 below threshold with gating=False should still evaluate tier1."""
        cases = self._make_tier_cases(4)
        responses = ["x"] * 4
        modes = [
            AnswerMode.ABSTAIN,
            AnswerMode.TRUSTWORTHY,
            AnswerMode.TRUSTWORTHY,
            AnswerMode.TRUSTWORTHY,
        ]

        tier1_cases = self._make_tier_cases(2, "dispute", "disputed")
        tier1_responses = ["x"] * 2
        tier1_modes = [AnswerMode.DISPUTED] * 2

        result = evaluator.evaluate_tiered(
            cases, responses, modes,
            tier1_cases, tier1_responses, tier1_modes,
            tier0_threshold=0.95,
            gating_enabled=False,
        )
        assert result.tier0.passed is False
        assert result.tier1 is not None
        assert result.tier1.accuracy == pytest.approx(1.0)

    def test_tiered_difficulty_breakdown(self, evaluator):
        """Tier1Result should have a difficulty_breakdown dict."""
        cases = self._make_tier_cases(2)
        responses = ["x"] * 2
        modes = [AnswerMode.ABSTAIN] * 2

        tier1_cases = [
            make_governance_case(
                "dispute", "disputed", id="t1_easy", difficulty="easy"
            ),
            make_governance_case(
                "dispute", "disputed", id="t1_hard", difficulty="hard"
            ),
        ]
        tier1_responses = ["x", "x"]
        tier1_modes = [AnswerMode.DISPUTED, AnswerMode.TRUSTWORTHY]

        result = evaluator.evaluate_tiered(
            cases, responses, modes,
            tier1_cases, tier1_responses, tier1_modes,
            tier0_threshold=0.5,
        )
        assert result.tier1 is not None
        breakdown = result.tier1.difficulty_breakdown
        assert isinstance(breakdown, dict)
        # easy case was correct, hard case was wrong
        assert breakdown["easy"] == pytest.approx(1.0)
        assert breakdown["hard"] == pytest.approx(0.0)


# ===========================================================================
# Edge case tests
# ===========================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_response(self, evaluator):
        """Empty string response should not crash the evaluator."""
        # Governance: should fail because mode doesn't match
        gov_case = make_governance_case("abstention", "abstain")
        result = evaluator.evaluate_case(gov_case, "", AnswerMode.TRUSTWORTHY)
        assert result.passed is False

        # Grounding: empty response has no forbidden matches -> pass
        ground_case = make_grounding_case()
        result = evaluator.evaluate_case(ground_case, "")
        assert result.passed is True

    def test_empty_forbidden_claims(self, evaluator):
        """Grounding case with empty forbidden_claims list should pass."""
        case = make_grounding_case(
            forbidden_claims=[],
            evaluation_config={
                "mode": "answer_quality",
                "use_regex": True,
                "case_insensitive": True,
                "allowed_phrases": [],
            },
        )
        result = evaluator.evaluate_case(case, "Anything at all is fine here.")
        assert result.passed is True
