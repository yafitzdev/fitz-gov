import pytest
from pathlib import Path
from fitz_gov.models import (
    FitzGovCase,
    FitzGovCategory,
    AnswerMode,
    FitzGovCaseResult,
    FitzGovCategoryResult,
    FitzGovConfusionMatrix,
)


@pytest.fixture
def data_dir():
    """Path to the actual data directory."""
    return Path(__file__).parent.parent / "data"


@pytest.fixture
def sample_governance_case():
    """A sample abstention case with all fields populated."""
    return FitzGovCase(
        id="test_abstain_001",
        category=FitzGovCategory.ABSTENTION,
        subcategory="missing_data",
        query="What is the revenue for Q4 2025?",
        contexts=["The company reported Q3 2024 revenue of $4.2 billion."],
        expected_mode=AnswerMode.ABSTAIN,
        description="Test abstention case",
        rationale="Q4 2025 data not in context",
        difficulty="hard",
        domain="finance",
        query_type="what",
        source_type="single",
        context_count=1,
        reasoning_type="factual",
        evidence_pattern="absent",
        evaluation_config={"mode": "governance", "check_mode_match": True},
    )


@pytest.fixture
def sample_grounding_case():
    """A sample trustworthy_hedged case with forbidden_claims (grounding check)."""
    return FitzGovCase(
        id="test_grounding_001",
        category=FitzGovCategory.TRUSTWORTHY_HEDGED,
        subcategory="grounding_numerical_hallucination",
        query="What was the project budget?",
        contexts=[
            "The migration deployed 47 microservices across 3 regions with 23 engineers."
        ],
        expected_mode=AnswerMode.TRUSTWORTHY,
        description="Budget question with no budget in context",
        rationale="Must not invent budget numbers",
        difficulty="hard",
        forbidden_claims=["budget (was|is) \\$?\\d", "\\$\\d+\\s*(million|billion)"],
        evaluation_config={
            "mode": "governance",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": [],
        },
        domain="technology",
        query_type="what",
    )


@pytest.fixture
def sample_relevance_case():
    """A sample trustworthy_hedged case with required_elements (relevance check)."""
    return FitzGovCase(
        id="test_relevance_001",
        category=FitzGovCategory.TRUSTWORTHY_HEDGED,
        subcategory="relevance_partial_answer",
        query="What are the results AND the timeline?",
        contexts=["The trial showed 85% success rate across 200 patients."],
        expected_mode=AnswerMode.TRUSTWORTHY,
        description="Asks for results AND timeline, only results provided",
        rationale="Timeline is missing from context",
        difficulty="hard",
        required_elements=["timeline", "not mentioned", "not specified"],
        evaluation_config={
            "mode": "governance",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 1,
        },
        domain="medicine",
        query_type="what",
    )
