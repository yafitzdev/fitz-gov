# fitz_gov/models.py
"""
Data models for fitz-gov benchmark.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class FitzGovCategory(str, Enum):
    """Categories of governance test cases."""

    ABSTENTION = "abstention"
    """Cases where the system should refuse to answer."""

    DISPUTE = "dispute"
    """Cases where the system should flag conflicting information."""

    TRUSTWORTHY_HEDGED = "trustworthy_hedged"
    """Cases where the system should hedge or qualify the answer (maps to TRUSTWORTHY mode)."""

    TRUSTWORTHY_DIRECT = "trustworthy_direct"
    """Cases where the system should answer clearly and directly (maps to TRUSTWORTHY mode)."""


class AnswerMode(str, Enum):
    """Expected answer modes for governance evaluation."""

    TRUSTWORTHY = "trustworthy"
    DISPUTED = "disputed"
    ABSTAIN = "abstain"


@dataclass
class FitzGovCase:
    """A single fitz-gov test case."""

    id: str
    """Unique identifier for the test case."""

    category: FitzGovCategory
    """Category of governance test."""

    subcategory: str
    """More specific subcategory (e.g., "numerical_hallucination")."""

    query: str
    """The question to answer."""

    contexts: list[str]
    """Context passages to use."""

    expected_mode: AnswerMode
    """Expected answer mode."""

    description: str
    """Human-readable description of what's being tested."""

    rationale: str
    """Why this mode is expected."""

    difficulty: str = "medium"
    """Difficulty level: easy, medium, hard."""

    # Answer quality fields (cross-cutting checks on trustworthy categories)
    forbidden_claims: list[str] = field(default_factory=list)
    """Regex patterns that indicate hallucination (grounding check)."""

    required_elements: list[str] = field(default_factory=list)
    """Elements that MUST appear in the answer (relevance check)."""

    forbidden_elements: list[str] = field(default_factory=list)
    """Patterns that indicate false confidence (relevance check)."""

    evaluation_config: dict[str, Any] = field(default_factory=dict)
    """Evaluation configuration (use_regex, allowed_phrases, etc.)."""

    context_sources: list[dict[str, str]] = field(default_factory=list)
    """Source metadata for multi-source cases. Each entry has source_id, source_type, authority."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional test case metadata."""

    # Classification attributes for results slicing
    domain: str = ""
    """Domain/topic area: technology, finance, medicine, science, law, education, environment,
       sports, food, social_media, real_estate, hr_workplace, transportation, agriculture,
       history, psychology, government, general."""

    query_type: str = ""
    """Query form: what, how, why, is, does, should, when, who, which, compare."""

    source_type: str = "single"
    """Source configuration: single, multi_source."""

    context_count: int = 0
    """Number of context passages."""

    reasoning_type: str = ""
    """What reasoning the case tests: factual, causal, comparative, procedural, evaluative, temporal."""

    evidence_pattern: str = ""
    """Evidence relationship to query: direct, indirect, conflicting, absent, partial, mixed."""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "id": self.id,
            "category": self.category.value,
            "subcategory": self.subcategory,
            "difficulty": self.difficulty,
            "query": self.query,
            "contexts": self.contexts,
            "expected_mode": self.expected_mode.value,
            "description": self.description,
            "rationale": self.rationale,
            "metadata": self.metadata,
        }
        if self.forbidden_claims:
            result["forbidden_claims"] = self.forbidden_claims
        if self.required_elements:
            result["required_elements"] = self.required_elements
        if self.forbidden_elements:
            result["forbidden_elements"] = self.forbidden_elements
        if self.evaluation_config:
            result["evaluation_config"] = self.evaluation_config
        if self.context_sources:
            result["context_sources"] = self.context_sources
        if self.domain:
            result["domain"] = self.domain
        if self.query_type:
            result["query_type"] = self.query_type
        if self.source_type and self.source_type != "single":
            result["source_type"] = self.source_type
        if self.context_count:
            result["context_count"] = self.context_count
        if self.reasoning_type:
            result["reasoning_type"] = self.reasoning_type
        if self.evidence_pattern:
            result["evidence_pattern"] = self.evidence_pattern
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FitzGovCase:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            category=FitzGovCategory(data["category"]),
            subcategory=data.get("subcategory", "unknown"),
            difficulty=data.get("difficulty", "medium"),
            query=data["query"],
            contexts=data["contexts"],
            expected_mode=AnswerMode(data["expected_mode"]),
            description=data.get("description", ""),
            rationale=data.get("rationale", ""),
            forbidden_claims=data.get("forbidden_claims", []),
            required_elements=data.get("required_elements", []),
            forbidden_elements=data.get("forbidden_elements", []),
            evaluation_config=data.get("evaluation_config", {}),
            context_sources=data.get("context_sources", []),
            metadata=data.get("metadata", {}),
            domain=data.get("domain", ""),
            query_type=data.get("query_type", ""),
            source_type=data.get("source_type", "single"),
            context_count=data.get("context_count", 0),
            reasoning_type=data.get("reasoning_type", ""),
            evidence_pattern=data.get("evidence_pattern", ""),
        )


@dataclass
class FitzGovCaseResult:
    """Result for a single fitz-gov test case."""

    case: FitzGovCase
    """The test case."""

    passed: bool
    """Whether the test passed (mode correct AND quality checks, if applicable)."""

    response: str
    """The response being evaluated."""

    actual_mode: AnswerMode | None = None
    """Actual answer mode."""

    failure_reason: str | None = None
    """Why the test failed (if applicable)."""

    mode_correct: bool = True
    """Whether the governance mode matched."""

    grounding_passed: bool | None = None
    """Whether grounding check passed. None if not checked."""

    relevance_passed: bool | None = None
    """Whether relevance check passed. None if not checked."""

    grounding_failure: str | None = None
    """Grounding failure details."""

    relevance_failure: str | None = None
    """Relevance failure details."""

    llm_validations: list[dict[str, Any]] = field(default_factory=list)
    """LLM validation results for debugging."""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "case_id": self.case.id,
            "passed": self.passed,
            "response": self.response,
            "actual_mode": self.actual_mode.value if self.actual_mode else None,
            "failure_reason": self.failure_reason,
            "mode_correct": self.mode_correct,
            "llm_validations": self.llm_validations,
        }
        if self.grounding_passed is not None:
            result["grounding_passed"] = self.grounding_passed
            result["grounding_failure"] = self.grounding_failure
        if self.relevance_passed is not None:
            result["relevance_passed"] = self.relevance_passed
            result["relevance_failure"] = self.relevance_failure
        return result


@dataclass
class FitzGovCategoryResult:
    """Results for a single governance category."""

    category: FitzGovCategory
    """The category."""

    accuracy: float
    """Accuracy for this category (0-1)."""

    num_correct: int
    """Number of correct predictions."""

    num_total: int
    """Total number of test cases."""

    case_results: list[FitzGovCaseResult]
    """Individual case results."""

    subcategory_accuracy: dict[str, float] = field(default_factory=dict)
    """Accuracy by subcategory."""

    grounding_accuracy: float | None = None
    """Grounding accuracy for trustworthy categories (None for abstention/dispute)."""

    relevance_accuracy: float | None = None
    """Relevance accuracy for trustworthy categories (None for abstention/dispute)."""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "category": self.category.value,
            "accuracy": self.accuracy,
            "num_correct": self.num_correct,
            "num_total": self.num_total,
            "case_results": [r.to_dict() for r in self.case_results],
            "subcategory_accuracy": self.subcategory_accuracy,
        }
        if self.grounding_accuracy is not None:
            result["grounding_accuracy"] = self.grounding_accuracy
        if self.relevance_accuracy is not None:
            result["relevance_accuracy"] = self.relevance_accuracy
        return result


@dataclass
class FitzGovConfusionMatrix:
    """Confusion matrix for governance mode predictions."""

    matrix: dict[str, dict[str, int]] = field(default_factory=dict)
    """Matrix[expected][actual] = count."""

    def __post_init__(self):
        """Initialize empty matrix if needed."""
        if not self.matrix:
            modes = [m.value for m in AnswerMode]
            self.matrix = {exp: {act: 0 for act in modes} for exp in modes}

    def add(self, expected: AnswerMode, actual: AnswerMode) -> None:
        """Add a prediction to the matrix."""
        self.matrix[expected.value][actual.value] += 1

    def get_accuracy(self) -> float:
        """Get overall accuracy."""
        correct = sum(self.matrix[m][m] for m in self.matrix)
        total = sum(sum(row.values()) for row in self.matrix.values())
        return correct / total if total > 0 else 0.0

    def to_dict(self) -> dict[str, dict[str, int]]:
        """Convert to dictionary."""
        return self.matrix

    def __str__(self) -> str:
        """Pretty print the confusion matrix."""
        modes = [m.value for m in AnswerMode]
        # Use abbreviated headers for compact display
        abbrev = {"trustworthy": "TRST", "disputed": "DISP", "abstain": "ABST"}
        lines = ["  Confusion Matrix (rows=expected, cols=actual):"]
        header = "              " + "  ".join(f"{abbrev.get(m, m[:4]):>6}" for m in modes)
        lines.append(header)
        for exp in modes:
            row_vals = "  ".join(f"{self.matrix[exp][act]:>6}" for act in modes)
            lines.append(f"    {abbrev.get(exp, exp[:4]):>6}  {row_vals}")
        return "\n".join(lines)


@dataclass
class FitzGovResult:
    """Full fitz-gov benchmark results."""

    overall_accuracy: float
    """Overall accuracy across all categories."""

    category_results: dict[FitzGovCategory, FitzGovCategoryResult]
    """Results by category."""

    confusion_matrix: FitzGovConfusionMatrix
    """Mode confusion matrix (governance categories only)."""

    num_cases: int
    """Total number of test cases."""

    evaluation_time_seconds: float
    """Time taken for evaluation."""

    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    """When evaluation was run."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional metadata (model, config, etc.)."""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "overall_accuracy": self.overall_accuracy,
            "category_results": {
                k.value: v.to_dict() for k, v in self.category_results.items()
            },
            "confusion_matrix": self.confusion_matrix.to_dict(),
            "num_cases": self.num_cases,
            "evaluation_time_seconds": self.evaluation_time_seconds,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    def __str__(self) -> str:
        """Pretty print results."""
        lines = [
            f"fitz-gov Results (n={self.num_cases}):",
            f"  Overall Accuracy: {self.overall_accuracy:.2%}",
            "",
            "By Category:",
        ]

        for cat in FitzGovCategory:
            if cat in self.category_results:
                r = self.category_results[cat]
                line = f"  {cat.value}: {r.accuracy:.2%} ({r.num_correct}/{r.num_total})"
                # Show quality scores for trustworthy categories
                if r.grounding_accuracy is not None or r.relevance_accuracy is not None:
                    quality_parts = []
                    if r.grounding_accuracy is not None:
                        quality_parts.append(f"grounding: {r.grounding_accuracy:.1%}")
                    if r.relevance_accuracy is not None:
                        quality_parts.append(f"relevance: {r.relevance_accuracy:.1%}")
                    line += f"  |  {', '.join(quality_parts)}"
                lines.append(line)

        lines.append("")
        lines.append(str(self.confusion_matrix))
        return "\n".join(lines)


# =============================================================================
# Tiered Evaluation Results
# =============================================================================


@dataclass
class Tier0Result:
    """Result for Tier 0 (sanity check) evaluation."""

    passed: bool
    """Whether the tier passed (accuracy >= threshold)."""

    accuracy: float
    """Overall accuracy for tier 0."""

    threshold: float
    """Required threshold to pass (default 0.95)."""

    category_results: dict[FitzGovCategory, FitzGovCategoryResult]
    """Results by category."""

    failure_cases: list[FitzGovCaseResult]
    """Cases that failed (for debugging)."""

    num_cases: int
    """Total number of tier 0 cases."""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "passed": self.passed,
            "accuracy": self.accuracy,
            "threshold": self.threshold,
            "category_results": {
                k.value: v.to_dict() for k, v in self.category_results.items()
            },
            "failure_cases": [c.to_dict() for c in self.failure_cases],
            "num_cases": self.num_cases,
        }

    def __str__(self) -> str:
        """Pretty print tier 0 results."""
        status = "PASSED" if self.passed else "FAILED"
        num_correct = sum(r.num_correct for r in self.category_results.values())
        lines = [
            f"TIER 0 (Sanity Check): {status}",
            f"  Threshold: {self.threshold:.0%} | Achieved: {self.accuracy:.1%} ({num_correct}/{self.num_cases})",
            "",
            "  By Category:",
        ]

        for cat in FitzGovCategory:
            if cat in self.category_results:
                r = self.category_results[cat]
                line = f"    {cat.value}: {r.num_correct}/{r.num_total} ({r.accuracy:.1%})"
                if r.grounding_accuracy is not None or r.relevance_accuracy is not None:
                    quality_parts = []
                    if r.grounding_accuracy is not None:
                        quality_parts.append(f"grounding: {r.grounding_accuracy:.1%}")
                    if r.relevance_accuracy is not None:
                        quality_parts.append(f"relevance: {r.relevance_accuracy:.1%}")
                    line += f"  |  {', '.join(quality_parts)}"
                lines.append(line)

        if self.failure_cases:
            lines.append("")
            lines.append(f"  Failed Cases ({len(self.failure_cases)}):")
            for case_result in self.failure_cases[:5]:  # Show first 5
                lines.append(f"    - {case_result.case.id}: {case_result.failure_reason}")
            if len(self.failure_cases) > 5:
                lines.append(f"    ... and {len(self.failure_cases) - 5} more")

        return "\n".join(lines)


@dataclass
class Tier1Result:
    """Result for Tier 1 (core benchmark) evaluation."""

    accuracy: float
    """Overall accuracy for tier 1."""

    category_results: dict[FitzGovCategory, FitzGovCategoryResult]
    """Results by category."""

    confusion_matrix: FitzGovConfusionMatrix
    """Mode confusion matrix."""

    difficulty_breakdown: dict[str, float]
    """Accuracy by difficulty level (medium, hard)."""

    num_cases: int
    """Total number of tier 1 cases."""

    # Classification breakdowns (value -> accuracy)
    domain_breakdown: dict[str, float] = field(default_factory=dict)
    """Accuracy by domain."""

    query_type_breakdown: dict[str, float] = field(default_factory=dict)
    """Accuracy by query type."""

    source_type_breakdown: dict[str, float] = field(default_factory=dict)
    """Accuracy by source type."""

    reasoning_type_breakdown: dict[str, float] = field(default_factory=dict)
    """Accuracy by reasoning type."""

    evidence_pattern_breakdown: dict[str, float] = field(default_factory=dict)
    """Accuracy by evidence pattern."""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "accuracy": self.accuracy,
            "category_results": {
                k.value: v.to_dict() for k, v in self.category_results.items()
            },
            "confusion_matrix": self.confusion_matrix.to_dict(),
            "difficulty_breakdown": self.difficulty_breakdown,
            "num_cases": self.num_cases,
        }
        if self.domain_breakdown:
            result["domain_breakdown"] = self.domain_breakdown
        if self.query_type_breakdown:
            result["query_type_breakdown"] = self.query_type_breakdown
        if self.source_type_breakdown:
            result["source_type_breakdown"] = self.source_type_breakdown
        if self.reasoning_type_breakdown:
            result["reasoning_type_breakdown"] = self.reasoning_type_breakdown
        if self.evidence_pattern_breakdown:
            result["evidence_pattern_breakdown"] = self.evidence_pattern_breakdown
        return result

    def __str__(self) -> str:
        """Pretty print tier 1 results."""
        lines = [
            f"TIER 1 (Core Benchmark): {self.accuracy:.1%}",
            "",
            "  By Category:",
        ]

        for cat in FitzGovCategory:
            if cat in self.category_results:
                r = self.category_results[cat]
                line = f"    {cat.value}: {r.num_correct}/{r.num_total} ({r.accuracy:.1%})"
                if r.grounding_accuracy is not None or r.relevance_accuracy is not None:
                    quality_parts = []
                    if r.grounding_accuracy is not None:
                        quality_parts.append(f"grounding: {r.grounding_accuracy:.1%}")
                    if r.relevance_accuracy is not None:
                        quality_parts.append(f"relevance: {r.relevance_accuracy:.1%}")
                    line += f"  |  {', '.join(quality_parts)}"
                lines.append(line)

        if self.difficulty_breakdown:
            lines.append("")
            lines.append("  By Difficulty:")
            for diff, acc in sorted(self.difficulty_breakdown.items()):
                lines.append(f"    {diff}: {acc:.1%}")

        # Show classification breakdowns if populated
        for label, breakdown in [
            ("By Domain", self.domain_breakdown),
            ("By Query Type", self.query_type_breakdown),
            ("By Source Type", self.source_type_breakdown),
            ("By Reasoning Type", self.reasoning_type_breakdown),
            ("By Evidence Pattern", self.evidence_pattern_breakdown),
        ]:
            if breakdown:
                lines.append("")
                lines.append(f"  {label}:")
                for key, acc in sorted(breakdown.items(), key=lambda x: -x[1]):
                    lines.append(f"    {key}: {acc:.1%}")

        # Add confusion matrix
        lines.append("")
        lines.append(str(self.confusion_matrix))

        return "\n".join(lines)


@dataclass
class TieredResult:
    """Full tiered fitz-gov benchmark results."""

    tier0: Tier0Result
    """Tier 0 (sanity check) results."""

    tier1: Tier1Result | None
    """Tier 1 (core benchmark) results. None if tier0 failed and gating is enabled."""

    gating_enabled: bool
    """Whether tier0 gates tier1 evaluation."""

    evaluation_time_seconds: float
    """Total time taken for evaluation."""

    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    """When evaluation was run."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional metadata."""

    @property
    def tier0_passed(self) -> bool:
        """Whether tier 0 passed."""
        return self.tier0.passed

    @property
    def tier1_accuracy(self) -> float | None:
        """Tier 1 accuracy, or None if not evaluated."""
        return self.tier1.accuracy if self.tier1 else None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "tier0": self.tier0.to_dict(),
            "tier1": self.tier1.to_dict() if self.tier1 else None,
            "gating_enabled": self.gating_enabled,
            "evaluation_time_seconds": self.evaluation_time_seconds,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    def __str__(self) -> str:
        """Pretty print tiered results."""
        lines = [
            "fitz-gov Tiered Evaluation",
            "=" * 26,
            "",
            str(self.tier0),
        ]

        if self.tier1:
            lines.append("")
            lines.append(str(self.tier1))
        elif self.gating_enabled and not self.tier0.passed:
            lines.append("")
            lines.append("TIER 1: Skipped (Tier 0 failed)")

        # Summary
        lines.append("")
        lines.append("-" * 40)
        if self.tier1:
            lines.append(
                f"Summary: Tier 0 {'PASSED' if self.tier0.passed else 'FAILED'}, "
                f"Tier 1 Score: {self.tier1.accuracy:.1%}"
            )
        else:
            lines.append(f"Summary: Tier 0 {'PASSED' if self.tier0.passed else 'FAILED'}")

        return "\n".join(lines)
