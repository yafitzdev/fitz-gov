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
        lines = ["Confusion Matrix (rows=expected, cols=actual):"]
        header = "           " + " ".join(f"{m[:8]:>10}" for m in modes)
        lines.append(header)
        for exp in modes:
            row_vals = " ".join(f"{self.matrix[exp][act]:>10}" for act in modes)
            lines.append(f"{exp[:10]:>10} {row_vals}")
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
