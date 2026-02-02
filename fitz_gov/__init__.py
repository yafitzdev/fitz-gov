# fitz_gov/__init__.py
"""
FITZ-GOV: Comprehensive RAG Governance Benchmark.

A benchmark for evaluating RAG system governance - knowing when to abstain,
dispute, qualify, or confidently answer based on available evidence.

Example:
    from fitz_gov import FitzGovEvaluator, load_cases, FitzGovCategory

    # Load test cases
    cases = load_cases([FitzGovCategory.GROUNDING])

    # Create evaluator with LLM validation
    evaluator = FitzGovEvaluator(llm_validation=True)

    # Evaluate responses
    for case in cases:
        response = my_rag_system.query(case.query, case.contexts)
        result = evaluator.evaluate_case(case, response)
        print(f"{case.id}: {'PASS' if result.passed else 'FAIL'}")
"""

__version__ = "0.9.1"

from .evaluator import FitzGovEvaluator
from .loader import get_category_info, get_data_dir, load_case_by_id, load_cases
from .llm_validator import OllamaValidator, ValidationResult, ValidatorConfig
from .models import (
    AnswerMode,
    FitzGovCase,
    FitzGovCaseResult,
    FitzGovCategory,
    FitzGovCategoryResult,
    FitzGovConfusionMatrix,
    FitzGovResult,
)

__all__ = [
    # Version
    "__version__",
    # Evaluator
    "FitzGovEvaluator",
    # Loader
    "load_cases",
    "load_case_by_id",
    "get_data_dir",
    "get_category_info",
    # Models
    "FitzGovCategory",
    "AnswerMode",
    "FitzGovCase",
    "FitzGovCaseResult",
    "FitzGovCategoryResult",
    "FitzGovConfusionMatrix",
    "FitzGovResult",
    # LLM Validator
    "OllamaValidator",
    "ValidatorConfig",
    "ValidationResult",
]
