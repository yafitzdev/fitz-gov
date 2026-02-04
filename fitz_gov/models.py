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

    # Governance Mode Categories
    ABSTENTION = "abstention"
    """Cases where the system should refuse to answer."""

    DISPUTE = "dispute"
    """Cases where the system should flag conflicting information."""

    QUALIFICATION = "qualification"
    """Cases where the system should hedge or qualify the answer."""

    CONFIDENCE = "confidence"
    """Cases where the system should answer confidently."""

    # Answer Quality Categories
    GROUNDING = "grounding"
    """Cases testing if answers are grounded in context (no hallucination)."""

    RELEVANCE = "relevance"
    """Cases testing if answers address the actual question asked."""


class AnswerMode(str, Enum):
    """Expected answer modes for governance evaluation."""

    ABSTAIN = "abstain"
    DISPUTED = "disputed"
    QUALIFIED = "qualified"
    CONFIDENT = "confident"


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

    # Answer quality fields (for grounding/relevance categories)
    forbidden_claims: list[str] = field(default_factory=list)
    """For GROUNDING: Regex patterns that indicate hallucination."""

    required_elements: list[str] = field(default_factory=list)
    """For RELEVANCE: Elements that MUST appear in the answer."""

    forbidden_elements: list[str] = field(default_factory=list)
    """For RELEVANCE: Patterns that indicate false confidence."""

    evaluation_config: dict[str, Any] = field(default_factory=dict)
    """Evaluation configuration (use_regex, allowed_phrases, etc.)."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional test case metadata."""

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
            metadata=data.get("metadata", {}),
        )


@dataclass
class FitzGovCaseResult:
    """Result for a single fitz-gov test case."""

    case: FitzGovCase
    """The test case."""

    passed: bool
    """Whether the test passed."""

    response: str
    """The response being evaluated."""

    actual_mode: AnswerMode | None = None
    """Actual answer mode (for governance categories)."""

    failure_reason: str | None = None
    """Why the test failed (if applicable)."""

    llm_validations: list[dict[str, Any]] = field(default_factory=list)
    """LLM validation results for debugging."""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "case_id": self.case.id,
            "passed": self.passed,
            "response": self.response,
            "actual_mode": self.actual_mode.value if self.actual_mode else None,
            "failure_reason": self.failure_reason,
            "llm_validations": self.llm_validations,
        }


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

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "category": self.category.value,
            "accuracy": self.accuracy,
            "num_correct": self.num_correct,
            "num_total": self.num_total,
            "case_results": [r.to_dict() for r in self.case_results],
            "subcategory_accuracy": self.subcategory_accuracy,
        }


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
        abbrev = {"abstain": "ABST", "disputed": "DISP", "qualified": "QUAL", "confident": "CONF"}
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
        ]

        # Governance categories
        gov_cats = [
            FitzGovCategory.ABSTENTION,
            FitzGovCategory.DISPUTE,
            FitzGovCategory.QUALIFICATION,
            FitzGovCategory.CONFIDENCE,
        ]
        lines.append("Governance Mode Categories:")
        for cat in gov_cats:
            if cat in self.category_results:
                r = self.category_results[cat]
                lines.append(f"  {cat.value}: {r.accuracy:.2%} ({r.num_correct}/{r.num_total})")

        # Quality categories
        quality_cats = [FitzGovCategory.GROUNDING, FitzGovCategory.RELEVANCE]
        if any(cat in self.category_results for cat in quality_cats):
            lines.append("")
            lines.append("Answer Quality Categories:")
            for cat in quality_cats:
                if cat in self.category_results:
                    r = self.category_results[cat]
                    lines.append(f"  {cat.value}: {r.accuracy:.2%} ({r.num_correct}/{r.num_total})")

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
                lines.append(f"    {cat.value}: {r.num_correct}/{r.num_total} ({r.accuracy:.1%})")

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

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "accuracy": self.accuracy,
            "category_results": {
                k.value: v.to_dict() for k, v in self.category_results.items()
            },
            "confusion_matrix": self.confusion_matrix.to_dict(),
            "difficulty_breakdown": self.difficulty_breakdown,
            "num_cases": self.num_cases,
        }

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
                lines.append(f"    {cat.value}: {r.num_correct}/{r.num_total} ({r.accuracy:.1%})")

        if self.difficulty_breakdown:
            lines.append("")
            lines.append("  By Difficulty:")
            for diff, acc in sorted(self.difficulty_breakdown.items()):
                lines.append(f"    {diff}: {acc:.1%}")

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
