# fitz_gov/__init__.py
"""
fitz-gov: Comprehensive RAG Governance Benchmark.

A benchmark for evaluating RAG system governance - knowing when to abstain,
dispute, or answer trustworthily based on available evidence.

Example:
    from fitz_gov import FitzGovEvaluator, load_cases, FitzGovCategory, AnswerMode

    # Load test cases
    cases = load_cases([FitzGovCategory.TRUSTWORTHY_HEDGED])

    # Create evaluator
    evaluator = FitzGovEvaluator()

    # Evaluate responses
    for case in cases:
        response = my_rag_system.query(case.query, case.contexts)
        mode = my_rag_system.classify_mode(response)
        result = evaluator.evaluate_case(case, response, mode)
        print(f"{case.id}: {'PASS' if result.passed else 'FAIL'}")

Tiered Evaluation Example:
    from fitz_gov import FitzGovEvaluator, load_tier, Tier

    # Load tiered cases
    tier0_cases = load_tier(Tier.SANITY)
    tier1_cases = load_tier(Tier.CORE)

    # Evaluate with tiered structure
    evaluator = FitzGovEvaluator()
    result = evaluator.evaluate_tiered(
        tier0_cases, tier0_responses, tier0_modes,
        tier1_cases, tier1_responses, tier1_modes,
    )
    print(result)
"""

__version__ = "5.0.0"

from .evaluator import FitzGovEvaluator
from .loader import (
    Tier,
    get_category_info,
    get_data_dir,
    get_tier_dir,
    get_tier_info,
    load_case_by_id,
    load_cases,
    load_tier,
)
from .llm_validator import OllamaValidator, ValidationResult, ValidatorConfig
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

__all__ = [
    # Version
    "__version__",
    # Evaluator
    "FitzGovEvaluator",
    # Loader
    "load_cases",
    "load_tier",
    "load_case_by_id",
    "get_data_dir",
    "get_tier_dir",
    "get_category_info",
    "get_tier_info",
    "Tier",
    # Models
    "FitzGovCategory",
    "AnswerMode",
    "FitzGovCase",
    "FitzGovCaseResult",
    "FitzGovCategoryResult",
    "FitzGovConfusionMatrix",
    "FitzGovResult",
    # Tiered Models
    "Tier0Result",
    "Tier1Result",
    "TieredResult",
    # LLM Validator
    "OllamaValidator",
    "ValidatorConfig",
    "ValidationResult",
]
