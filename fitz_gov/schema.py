# fitz_gov/schema.py
"""
Data schemas for fitz-gov benchmark.

These schemas define the structure of test cases and are designed to be
compatible with fitz-ai's evaluation framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AnswerMode(str, Enum):
    """Expected answer mode for governance test cases."""

    TRUSTWORTHY = "trustworthy"
    """Evidence supports answering. Answer clearly and directly."""

    DISPUTED = "disputed"
    """Sources explicitly disagree; summarize the disagreement."""

    ABSTAIN = "abstain"
    """Evidence is insufficient; do not attempt a definitive answer."""


class FitzGovCategory(str, Enum):
    """Categories of governance test cases."""

    # Governance Mode Categories (maps to AnswerMode)
    ABSTENTION = "abstention"
    """Cases where the system should refuse to answer."""

    DISPUTE = "dispute"
    """Cases where the system should flag conflicting information."""

    QUALIFICATION = "qualification"
    """Cases where the system should hedge or qualify the answer."""

    CONFIDENCE = "confidence"
    """Cases where the system should answer clearly and directly."""

    # Answer Quality Categories
    GROUNDING = "grounding"
    """Cases testing if answers are grounded in context (no hallucination)."""

    RELEVANCE = "relevance"
    """Cases testing if answers address the actual question asked."""


@dataclass
class FitzGovCase:
    """A single fitz-gov test case."""

    id: str
    """Unique identifier for the test case."""

    category: FitzGovCategory
    """Category of governance test."""

    subcategory: str
    """More specific subcategory (e.g., 'no_context', 'out_of_scope')."""

    query: str
    """The question to answer."""

    contexts: list[str]
    """Context passages to use."""

    expected_mode: AnswerMode
    """Expected answer mode (for governance categories)."""

    description: str
    """Human-readable description of what's being tested."""

    rationale: str
    """Why this mode is expected."""

    # Answer quality fields (for grounding/relevance categories)
    forbidden_claims: list[str] = field(default_factory=list)
    """For GROUNDING: Claims that indicate hallucination (should NOT appear)."""

    required_elements: list[str] = field(default_factory=list)
    """For RELEVANCE: Elements that MUST appear in the answer."""

    # Corpus references (for Mode B full pipeline evaluation)
    relevant_doc_ids: list[str] = field(default_factory=list)
    """Document IDs from corpus that are relevant to this query (for Mode B)."""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional test case metadata."""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "id": self.id,
            "category": self.category.value,
            "subcategory": self.subcategory,
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
        if self.relevant_doc_ids:
            result["relevant_doc_ids"] = self.relevant_doc_ids
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FitzGovCase:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            category=FitzGovCategory(data["category"]),
            subcategory=data["subcategory"],
            query=data["query"],
            contexts=data["contexts"],
            expected_mode=AnswerMode(data["expected_mode"]),
            description=data["description"],
            rationale=data["rationale"],
            forbidden_claims=data.get("forbidden_claims", []),
            required_elements=data.get("required_elements", []),
            relevant_doc_ids=data.get("relevant_doc_ids", []),
            metadata=data.get("metadata", {}),
        )

    def __str__(self) -> str:
        return f"FitzGovCase({self.id}, {self.category.value}, expected={self.expected_mode.value})"
