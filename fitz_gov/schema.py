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

    TRUSTWORTHY_HEDGED = "trustworthy_hedged"
    """Cases where the system should hedge or qualify the answer (maps to TRUSTWORTHY mode)."""

    TRUSTWORTHY_DIRECT = "trustworthy_direct"
    """Cases where the system should answer clearly and directly (maps to TRUSTWORTHY mode)."""

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
            subcategory=data["subcategory"],
            query=data["query"],
            contexts=data["contexts"],
            expected_mode=AnswerMode(data["expected_mode"]),
            description=data["description"],
            rationale=data["rationale"],
            forbidden_claims=data.get("forbidden_claims", []),
            required_elements=data.get("required_elements", []),
            relevant_doc_ids=data.get("relevant_doc_ids", []),
            context_sources=data.get("context_sources", []),
            metadata=data.get("metadata", {}),
            domain=data.get("domain", ""),
            query_type=data.get("query_type", ""),
            source_type=data.get("source_type", "single"),
            context_count=data.get("context_count", 0),
            reasoning_type=data.get("reasoning_type", ""),
            evidence_pattern=data.get("evidence_pattern", ""),
        )

    def __str__(self) -> str:
        return f"FitzGovCase({self.id}, {self.category.value}, expected={self.expected_mode.value})"
