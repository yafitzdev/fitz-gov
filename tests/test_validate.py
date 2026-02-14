# tests/test_validate.py
"""
Tests for fitz_gov/validate.py - validation and quality-checking logic.
"""

import pytest

from fitz_gov.validate import (
    check_quality,
    cosine_similarity,
    find_exact_duplicates,
)


def make_valid_case(**overrides):
    """Create a valid test case dict with sensible defaults."""
    case = {
        "id": "test_001",
        "query": "What is the revenue for Q4?",
        "contexts": ["Revenue data shows growth."],
        "expected_mode": "trustworthy",
        "description": "Test case",
        "rationale": "Testing",
        "category": "abstention",
    }
    case.update(overrides)
    return case


class TestCheckQuality:
    """Tests for the check_quality function."""

    def test_check_quality_valid_case(self):
        """Valid case with all fields returns empty issues list."""
        case = make_valid_case()
        issues = check_quality(case)
        assert issues == [], f"Expected no issues but got: {issues}"

    def test_check_quality_missing_id(self):
        """Catches missing id field."""
        case = make_valid_case()
        del case["id"]
        issues = check_quality(case)
        assert any("id" in issue.lower() for issue in issues)

    def test_check_quality_missing_query(self):
        """Catches missing query field."""
        case = make_valid_case()
        del case["query"]
        issues = check_quality(case)
        assert any("query" in issue.lower() for issue in issues)

    def test_check_quality_short_query(self):
        """Query < 10 chars flagged."""
        case = make_valid_case(query="Short?")
        issues = check_quality(case)
        assert any("short" in issue.lower() for issue in issues)

    def test_check_quality_long_query(self):
        """Query > 500 chars flagged."""
        case = make_valid_case(query="x" * 501)
        issues = check_quality(case)
        assert any("long" in issue.lower() for issue in issues)

    def test_check_quality_invalid_mode(self):
        """Invalid expected_mode caught."""
        case = make_valid_case(expected_mode="invalid_mode")
        issues = check_quality(case)
        assert any("expected_mode" in issue.lower() or "invalid" in issue.lower() for issue in issues)

    def test_check_quality_no_contexts(self):
        """Empty contexts array caught."""
        case = make_valid_case(contexts=[])
        issues = check_quality(case)
        assert any("context" in issue.lower() for issue in issues)

    def test_check_quality_too_many_contexts(self):
        """>10 contexts flagged."""
        case = make_valid_case(contexts=[f"Context {i}" for i in range(11)])
        issues = check_quality(case)
        assert any("too many" in issue.lower() for issue in issues)

    def test_check_quality_grounding_no_forbidden(self):
        """Grounding case without forbidden_claims flagged."""
        case = make_valid_case(category="grounding")
        # Make sure forbidden_claims is missing or empty
        case.pop("forbidden_claims", None)
        issues = check_quality(case)
        assert any("forbidden_claims" in issue for issue in issues)

    def test_check_quality_relevance_no_required(self):
        """Relevance case without required_elements flagged."""
        case = make_valid_case(category="relevance")
        case.pop("required_elements", None)
        issues = check_quality(case)
        assert any("required_elements" in issue for issue in issues)

    def test_check_quality_context_sources_valid(self):
        """Valid context_sources passes without issues."""
        case = make_valid_case(
            contexts=["Context A", "Context B"],
            context_sources=[
                {"source_id": "doc1", "source_type": "academic", "authority": "primary"},
                {"source_id": "doc2", "source_type": "news", "authority": "secondary"},
            ],
        )
        issues = check_quality(case)
        assert issues == [], f"Expected no issues but got: {issues}"

    def test_check_quality_context_sources_length_mismatch(self):
        """context_sources length != contexts length caught."""
        case = make_valid_case(
            contexts=["Context A", "Context B"],
            context_sources=[
                {"source_id": "doc1", "source_type": "academic", "authority": "primary"},
            ],
        )
        issues = check_quality(case)
        assert any("context_sources length" in issue for issue in issues)

    def test_check_quality_context_sources_missing_fields(self):
        """Missing source_id/source_type/authority caught."""
        case = make_valid_case(
            contexts=["Context A"],
            context_sources=[
                {"source_id": "doc1"},  # missing source_type and authority
            ],
        )
        issues = check_quality(case)
        assert any("source_type" in issue for issue in issues)
        assert any("authority" in issue for issue in issues)


class TestFindExactDuplicates:
    """Tests for the find_exact_duplicates function."""

    def test_find_exact_duplicates(self):
        """Detects duplicate queries."""
        cases = [
            {"query": "What is Python?"},
            {"query": "What is Java?"},
            {"query": "what is python?"},  # duplicate (case-insensitive)
        ]
        duplicates = find_exact_duplicates(cases)
        assert len(duplicates) == 1
        assert duplicates[0][0] == 0  # first index
        assert duplicates[0][1] == 2  # second index
        assert duplicates[0][2] == 1.0  # exact match similarity

    def test_find_exact_duplicates_none(self):
        """No duplicates when all unique."""
        cases = [
            {"query": "What is Python?"},
            {"query": "What is Java?"},
            {"query": "What is Rust?"},
        ]
        duplicates = find_exact_duplicates(cases)
        assert len(duplicates) == 0


class TestCosineSimilarity:
    """Tests for the cosine_similarity function."""

    def test_cosine_similarity_identical(self):
        """cosine_similarity returns 1.0 for identical vectors."""
        a = [1.0, 2.0, 3.0]
        result = cosine_similarity(a, a)
        assert abs(result - 1.0) < 1e-9

    def test_cosine_similarity_orthogonal(self):
        """cosine_similarity returns 0 for orthogonal vectors."""
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        result = cosine_similarity(a, b)
        assert abs(result) < 1e-9

    def test_cosine_similarity_zero_vector(self):
        """cosine_similarity returns 0 when a vector is zero."""
        a = [0.0, 0.0, 0.0]
        b = [1.0, 2.0, 3.0]
        result = cosine_similarity(a, b)
        assert result == 0.0
