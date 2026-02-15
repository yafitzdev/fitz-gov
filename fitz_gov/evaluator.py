# fitz_gov/evaluator.py
"""
fitz-gov evaluation logic.

This module provides the core evaluation functionality for the fitz-gov benchmark.
All categories use governance mode matching. Trustworthy categories additionally
run grounding (forbidden_claims) and relevance (required_elements) quality checks.
"""

from __future__ import annotations

import logging
import re
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

from .llm_validator import OllamaValidator, ValidatorConfig
from .loader import Tier, load_tier
from .models import (
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

logger = logging.getLogger(__name__)

# Categories where quality checks (grounding + relevance) apply
TRUSTWORTHY_CATEGORIES = {
    FitzGovCategory.TRUSTWORTHY_HEDGED,
    FitzGovCategory.TRUSTWORTHY_DIRECT,
}


class FitzGovEvaluator:
    """
    Evaluator for fitz-gov benchmark.

    Evaluates responses against test cases using:
    1. Governance mode matching (all categories)
    2. Grounding checks via forbidden_claims regex (trustworthy categories)
    3. Relevance checks via required_elements regex (trustworthy categories)
    4. Optional LLM validation for semantic verification (two-pass)

    Example:
        evaluator = FitzGovEvaluator(llm_validation=True)

        # Evaluate a single response
        result = evaluator.evaluate_case(case, response, actual_mode)

        # Evaluate multiple responses
        results = evaluator.evaluate_all(cases, responses, modes)
    """

    def __init__(
        self,
        llm_validation: bool = False,
        llm_model: str = "qwen2.5:14b",
        llm_base_url: str = "http://localhost:11434",
    ):
        """
        Initialize evaluator.

        Args:
            llm_validation: Enable two-pass LLM validation for quality checks.
            llm_model: Ollama model for LLM validation.
            llm_base_url: Ollama API URL.
        """
        self._llm_validation = llm_validation
        self._validator: OllamaValidator | None = None

        if llm_validation:
            config = ValidatorConfig(model=llm_model, base_url=llm_base_url)
            self._validator = OllamaValidator(config)

            if not self._validator.is_available():
                logger.warning(
                    f"LLM validation enabled but Ollama not available at {llm_base_url}. "
                    f"Falling back to regex-only. Run: ollama pull {llm_model}"
                )

    def evaluate_case(
        self,
        case: FitzGovCase,
        response: str,
        actual_mode: AnswerMode | None = None,
    ) -> FitzGovCaseResult:
        """
        Evaluate a single test case.

        All categories check governance mode. Trustworthy categories additionally
        run grounding and relevance quality checks when mode is correct.

        Args:
            case: The test case to evaluate.
            response: The response to evaluate.
            actual_mode: The actual answer mode.

        Returns:
            FitzGovCaseResult with pass/fail and quality analysis.
        """
        # Step 1: Governance mode check
        if actual_mode is None:
            return FitzGovCaseResult(
                case=case,
                passed=False,
                response=response,
                actual_mode=None,
                failure_reason="No actual_mode provided",
                mode_correct=False,
            )

        mode_correct = actual_mode == case.expected_mode
        failure_reason = None
        if not mode_correct:
            failure_reason = (
                f"Expected {case.expected_mode.value}, got {actual_mode.value}"
            )

        # Step 2: Quality checks (trustworthy categories only, only when mode correct)
        grounding_passed = None
        relevance_passed = None
        grounding_failure = None
        relevance_failure = None
        llm_validations: list[dict[str, Any]] = []

        if case.category in TRUSTWORTHY_CATEGORIES and mode_correct:
            if case.forbidden_claims:
                grounding_passed, grounding_failure, g_llm = self._check_grounding(
                    case, response
                )
                llm_validations.extend(g_llm)

            if case.required_elements:
                relevance_passed, relevance_failure, r_llm = self._check_relevance(
                    case, response
                )
                llm_validations.extend(r_llm)

        # Overall: mode correct AND quality checks passed
        passed = mode_correct
        if grounding_passed is False:
            passed = False
            if not failure_reason:
                failure_reason = grounding_failure
        if relevance_passed is False:
            passed = False
            if not failure_reason:
                failure_reason = relevance_failure

        return FitzGovCaseResult(
            case=case,
            passed=passed,
            response=response,
            actual_mode=actual_mode,
            failure_reason=failure_reason,
            mode_correct=mode_correct,
            grounding_passed=grounding_passed,
            relevance_passed=relevance_passed,
            grounding_failure=grounding_failure,
            relevance_failure=relevance_failure,
            llm_validations=llm_validations,
        )

    def evaluate_all(
        self,
        cases: list[FitzGovCase],
        responses: list[str],
        modes: list[AnswerMode | None] | None = None,
    ) -> FitzGovResult:
        """
        Evaluate multiple test cases.

        Args:
            cases: Test cases to evaluate.
            responses: Responses to evaluate (same order as cases).
            modes: Actual answer modes (same order as cases), or None.

        Returns:
            FitzGovResult with aggregated metrics.
        """
        if len(cases) != len(responses):
            raise ValueError("cases and responses must have same length")

        if modes is None:
            modes = [None] * len(cases)
        elif len(modes) != len(cases):
            raise ValueError("modes must have same length as cases")

        start_time = time.time()

        # Group by category
        by_category: dict[FitzGovCategory, list[tuple[FitzGovCase, str, AnswerMode | None]]] = (
            defaultdict(list)
        )
        for case, response, mode in zip(cases, responses, modes):
            by_category[case.category].append((case, response, mode))

        # Evaluate each category
        confusion_matrix = FitzGovConfusionMatrix()
        category_results: dict[FitzGovCategory, FitzGovCategoryResult] = {}

        for cat, items in by_category.items():
            case_results: list[FitzGovCaseResult] = []
            subcategory_correct: dict[str, int] = defaultdict(int)
            subcategory_total: dict[str, int] = defaultdict(int)

            for case, response, mode in items:
                result = self.evaluate_case(case, response, mode)
                case_results.append(result)

                # Update confusion matrix for all categories
                if result.actual_mode:
                    confusion_matrix.add(case.expected_mode, result.actual_mode)

                # Track subcategory stats
                subcategory_total[case.subcategory] += 1
                if result.passed:
                    subcategory_correct[case.subcategory] += 1

            # Calculate subcategory accuracy
            subcategory_accuracy = {
                subcat: subcategory_correct[subcat] / total
                for subcat, total in subcategory_total.items()
            }

            num_correct = sum(1 for r in case_results if r.passed)

            # Calculate quality scores for trustworthy categories
            grounding_accuracy = None
            relevance_accuracy = None
            if cat in TRUSTWORTHY_CATEGORIES:
                g_checked = sum(1 for r in case_results if r.grounding_passed is not None)
                g_passed = sum(1 for r in case_results if r.grounding_passed is True)
                r_checked = sum(1 for r in case_results if r.relevance_passed is not None)
                r_passed = sum(1 for r in case_results if r.relevance_passed is True)
                if g_checked > 0:
                    grounding_accuracy = g_passed / g_checked
                if r_checked > 0:
                    relevance_accuracy = r_passed / r_checked

            category_results[cat] = FitzGovCategoryResult(
                category=cat,
                accuracy=num_correct / len(case_results) if case_results else 0.0,
                num_correct=num_correct,
                num_total=len(case_results),
                case_results=case_results,
                subcategory_accuracy=subcategory_accuracy,
                grounding_accuracy=grounding_accuracy,
                relevance_accuracy=relevance_accuracy,
            )

        # Calculate overall accuracy
        total_correct = sum(r.num_correct for r in category_results.values())
        total_cases = sum(r.num_total for r in category_results.values())
        overall_accuracy = total_correct / total_cases if total_cases > 0 else 0.0

        return FitzGovResult(
            overall_accuracy=overall_accuracy,
            category_results=category_results,
            confusion_matrix=confusion_matrix,
            num_cases=len(cases),
            evaluation_time_seconds=time.time() - start_time,
            metadata={
                "llm_validation": self._llm_validation,
            },
        )

    def evaluate_tiered(
        self,
        tier0_cases: list[FitzGovCase],
        tier0_responses: list[str],
        tier0_modes: list[AnswerMode | None] | None,
        tier1_cases: list[FitzGovCase],
        tier1_responses: list[str],
        tier1_modes: list[AnswerMode | None] | None,
        tier0_threshold: float = 0.95,
        gating_enabled: bool = True,
    ) -> TieredResult:
        """
        Evaluate cases using tiered structure.

        Args:
            tier0_cases: Tier 0 (sanity) test cases.
            tier0_responses: Responses for tier 0 cases.
            tier0_modes: Actual modes for tier 0 cases.
            tier1_cases: Tier 1 (core) test cases.
            tier1_responses: Responses for tier 1 cases.
            tier1_modes: Actual modes for tier 1 cases.
            tier0_threshold: Required accuracy to pass tier 0 (default 0.95).
            gating_enabled: If True, skip tier 1 if tier 0 fails.

        Returns:
            TieredResult with both tier results.
        """
        start_time = time.time()

        # Evaluate Tier 0
        tier0_result = self._evaluate_tier0(
            tier0_cases, tier0_responses, tier0_modes, tier0_threshold
        )

        # Evaluate Tier 1 (if not gated or tier 0 passed)
        tier1_result = None
        if not gating_enabled or tier0_result.passed:
            tier1_result = self._evaluate_tier1(
                tier1_cases, tier1_responses, tier1_modes
            )

        return TieredResult(
            tier0=tier0_result,
            tier1=tier1_result,
            gating_enabled=gating_enabled,
            evaluation_time_seconds=time.time() - start_time,
            metadata={
                "llm_validation": self._llm_validation,
            },
        )

    def _evaluate_tier0(
        self,
        cases: list[FitzGovCase],
        responses: list[str],
        modes: list[AnswerMode | None] | None,
        threshold: float,
    ) -> Tier0Result:
        """Evaluate Tier 0 (sanity check) cases."""
        if modes is None:
            modes = [None] * len(cases)

        # Use evaluate_all to get results
        result = self.evaluate_all(cases, responses, modes)

        # Collect failure cases
        failure_cases = []
        for cat_result in result.category_results.values():
            for case_result in cat_result.case_results:
                if not case_result.passed:
                    failure_cases.append(case_result)

        return Tier0Result(
            passed=result.overall_accuracy >= threshold,
            accuracy=result.overall_accuracy,
            threshold=threshold,
            category_results=result.category_results,
            failure_cases=failure_cases,
            num_cases=result.num_cases,
        )

    def _evaluate_tier1(
        self,
        cases: list[FitzGovCase],
        responses: list[str],
        modes: list[AnswerMode | None] | None,
    ) -> Tier1Result:
        """Evaluate Tier 1 (core benchmark) cases."""
        if modes is None:
            modes = [None] * len(cases)

        # Use evaluate_all to get results
        result = self.evaluate_all(cases, responses, modes)

        # Collect all case results into a flat list
        all_case_results: list[FitzGovCaseResult] = []
        for cat_result in result.category_results.values():
            all_case_results.extend(cat_result.case_results)

        # Calculate difficulty breakdown
        difficulty_correct: dict[str, int] = defaultdict(int)
        difficulty_total: dict[str, int] = defaultdict(int)

        for case_result in all_case_results:
            diff = case_result.case.difficulty
            difficulty_total[diff] += 1
            if case_result.passed:
                difficulty_correct[diff] += 1

        difficulty_breakdown = {
            diff: difficulty_correct[diff] / total
            for diff, total in difficulty_total.items()
            if total > 0
        }

        # Calculate classification breakdowns
        classification_breakdowns = self._compute_classification_breakdowns(
            all_case_results
        )

        return Tier1Result(
            accuracy=result.overall_accuracy,
            category_results=result.category_results,
            confusion_matrix=result.confusion_matrix,
            difficulty_breakdown=difficulty_breakdown,
            num_cases=result.num_cases,
            **classification_breakdowns,
        )

    @staticmethod
    def _compute_classification_breakdowns(
        case_results: list[FitzGovCaseResult],
    ) -> dict[str, dict[str, float]]:
        """Compute accuracy breakdowns by classification dimensions."""
        dimensions = [
            "domain",
            "query_type",
            "source_type",
            "reasoning_type",
            "evidence_pattern",
        ]
        counts: dict[str, dict[str, dict[str, int]]] = {
            dim: defaultdict(lambda: {"passed": 0, "total": 0})
            for dim in dimensions
        }

        for cr in case_results:
            for dim in dimensions:
                key = getattr(cr.case, dim, "") or "unknown"
                counts[dim][key]["total"] += 1
                if cr.passed:
                    counts[dim][key]["passed"] += 1

        return {
            f"{dim}_breakdown": {
                k: v["passed"] / v["total"]
                for k, v in counts[dim].items()
                if v["total"] > 0
            }
            for dim in dimensions
        }

    def _check_grounding(
        self, case: FitzGovCase, response: str
    ) -> tuple[bool, str | None, list[dict[str, Any]]]:
        """
        Check grounding: response should not contain forbidden claims.

        Returns:
            Tuple of (passed, failure_reason, llm_validations).
        """
        eval_config = case.evaluation_config
        use_regex = eval_config.get("use_regex", False)
        case_insensitive = eval_config.get("case_insensitive", True)
        allowed_phrases = eval_config.get("allowed_phrases", [])

        regex_flags = re.IGNORECASE if case_insensitive else 0

        # Pass 1: Regex check for forbidden claims
        found_violations = []
        for pattern in case.forbidden_claims:
            try:
                if use_regex:
                    matches = list(re.finditer(pattern, response, regex_flags))
                else:
                    # Simple substring match
                    search_text = response.lower() if case_insensitive else response
                    search_pattern = pattern.lower() if case_insensitive else pattern
                    if search_pattern in search_text:
                        matches = [type("Match", (), {"group": lambda p=pattern: p})]
                    else:
                        matches = []

                for match in matches:
                    matched_text = match.group() if hasattr(match, "group") else pattern
                    match_span = (
                        (match.start(), match.end())
                        if hasattr(match, "start")
                        else None
                    )

                    # Check if forbidden match overlaps with an allowed phrase
                    is_allowed = self._check_allowed_phrases(
                        response, allowed_phrases, regex_flags, match_span
                    )

                    if not is_allowed:
                        found_violations.append({
                            "matched_text": matched_text,
                            "pattern": pattern,
                        })
            except re.error as e:
                logger.warning(f"Invalid regex pattern '{pattern}': {e}")
                if pattern.lower() in response.lower():
                    found_violations.append({
                        "matched_text": pattern,
                        "pattern": pattern,
                    })

        if not found_violations:
            return True, None, []

        # Pass 2: LLM validation (if enabled)
        llm_validations: list[dict[str, Any]] = []
        if self._validator and self._validator.is_available():
            confirmed_violations = []
            for violation in found_violations:
                result = self._validator.validate_forbidden_claim(
                    response=response,
                    matched_text=violation["matched_text"],
                    pattern=violation["pattern"],
                    context=case.contexts[0] if case.contexts else "",
                    query=case.query,
                    rationale=case.rationale,
                )
                llm_validations.append({
                    "matched_text": violation["matched_text"],
                    "is_violation": result.is_violation,
                    "reasoning": result.reasoning,
                    "cached": result.cached,
                })
                if result.is_violation:
                    confirmed_violations.append(violation)
                else:
                    logger.debug(
                        f"LLM cleared false positive: '{violation['matched_text']}'"
                    )

            if not confirmed_violations:
                return True, None, llm_validations

            violations_list = [v["matched_text"] for v in confirmed_violations]
            return (
                False,
                f"HALLUCINATION: {violations_list}",
                llm_validations,
            )

        # No LLM: trust regex results
        violations_list = [v["matched_text"] for v in found_violations]
        return False, f"HALLUCINATION: {violations_list}", []

    def _check_relevance(
        self, case: FitzGovCase, response: str
    ) -> tuple[bool, str | None, list[dict[str, Any]]]:
        """
        Check relevance: response should contain required elements and not forbidden ones.

        Returns:
            Tuple of (passed, failure_reason, llm_validations).
        """
        eval_config = case.evaluation_config
        use_regex = eval_config.get("use_regex", False)
        case_insensitive = eval_config.get("case_insensitive", True)
        min_required = eval_config.get("min_required", 1)

        regex_flags = re.IGNORECASE if case_insensitive else 0

        # Check required elements
        matched_required = 0
        for element in case.required_elements:
            try:
                if use_regex:
                    if re.search(element, response, regex_flags):
                        matched_required += 1
                else:
                    search_text = response.lower() if case_insensitive else response
                    search_element = element.lower() if case_insensitive else element
                    if search_element in search_text:
                        matched_required += 1
            except re.error:
                if element.lower() in response.lower():
                    matched_required += 1

        if matched_required < min_required:
            return (
                False,
                f"Missing required elements: need {min_required}, found {matched_required}",
                [],
            )

        # Check forbidden elements
        found_forbidden = []
        for pattern in case.forbidden_elements:
            try:
                if use_regex:
                    match = re.search(pattern, response, regex_flags)
                else:
                    search_text = response.lower() if case_insensitive else response
                    search_pattern = pattern.lower() if case_insensitive else pattern
                    match = search_pattern in search_text

                if match:
                    matched_text = match.group() if hasattr(match, "group") else pattern
                    found_forbidden.append({
                        "matched_text": matched_text,
                        "pattern": pattern,
                    })
            except re.error:
                if pattern.lower() in response.lower():
                    found_forbidden.append({
                        "matched_text": pattern,
                        "pattern": pattern,
                    })

        if not found_forbidden:
            return True, None, []

        # Pass 2: LLM validation for forbidden elements
        llm_validations: list[dict[str, Any]] = []
        if self._validator and self._validator.is_available():
            confirmed_forbidden = []
            for violation in found_forbidden:
                result = self._validator.validate_forbidden_element(
                    response=response,
                    matched_text=violation["matched_text"],
                    pattern=violation["pattern"],
                    context=case.contexts[0] if case.contexts else "",
                    query=case.query,
                )
                llm_validations.append({
                    "matched_text": violation["matched_text"],
                    "is_violation": result.is_violation,
                    "reasoning": result.reasoning,
                    "cached": result.cached,
                })
                if result.is_violation:
                    confirmed_forbidden.append(violation)

            if not confirmed_forbidden:
                return True, None, llm_validations

            forbidden_list = [v["matched_text"] for v in confirmed_forbidden]
            return (
                False,
                f"FALSE_CONFIDENCE: {forbidden_list}",
                llm_validations,
            )

        # No LLM: trust regex results
        forbidden_list = [v["matched_text"] for v in found_forbidden]
        return False, f"FALSE_CONFIDENCE: {forbidden_list}", []

    def _check_allowed_phrases(
        self,
        response: str,
        allowed_phrases: list[str],
        regex_flags: int,
        forbidden_span: tuple[int, int] | None = None,
    ) -> bool:
        """Check if a forbidden match overlaps with an allowed phrase.

        Args:
            response: The full response text.
            allowed_phrases: Regex patterns for allowed phrases.
            regex_flags: Regex flags to use.
            forbidden_span: (start, end) of the forbidden match. If provided,
                only returns True when the forbidden match is *within* an
                allowed phrase match, preventing the escape-hatch where an
                allowed phrase elsewhere in the response clears an unrelated
                forbidden match.
        """
        for allowed in allowed_phrases:
            try:
                for allowed_match in re.finditer(allowed, response, regex_flags):
                    if forbidden_span is None:
                        return True
                    # Check overlap: forbidden match must be within allowed span
                    a_start, a_end = allowed_match.start(), allowed_match.end()
                    f_start, f_end = forbidden_span
                    if a_start <= f_start and f_end <= a_end:
                        return True
            except re.error:
                if allowed.lower() in response.lower():
                    if forbidden_span is None:
                        return True
        return False
