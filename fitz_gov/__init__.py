# fitz_gov/__init__.py
"""
FITZ-GOV: Comprehensive RAG Governance Benchmark.

This package provides:
1. Benchmark test data for evaluating RAG governance
2. Synthetic test case generator for creating custom benchmarks
3. CLI tools for working with benchmark data

Usage:
    from fitz_gov import load_cases, FitzGovCase

    cases = load_cases()
    for case in cases:
        # Evaluate your RAG system
        ...
"""

__version__ = "0.1.0"

__all__ = [
    # Schema
    "FitzGovCategory",
    "FitzGovCase",
    "AnswerMode",
    # Data loading
    "load_cases",
    "get_data_dir",
    # Generator (requires [generator] extra)
    "FitzGovGenerator",
    # Bootstrap (requires [generator] extra + beir)
    "bootstrap_from_beir",
]


def __getattr__(name: str):
    """Lazy imports."""
    if name in ("FitzGovCategory", "FitzGovCase", "AnswerMode"):
        from .schema import AnswerMode, FitzGovCase, FitzGovCategory

        if name == "FitzGovCategory":
            return FitzGovCategory
        elif name == "FitzGovCase":
            return FitzGovCase
        return AnswerMode

    if name in ("load_cases", "get_data_dir"):
        from .loader import get_data_dir, load_cases

        if name == "load_cases":
            return load_cases
        return get_data_dir

    if name == "FitzGovGenerator":
        from .generator import FitzGovGenerator

        return FitzGovGenerator

    if name == "bootstrap_from_beir":
        from .bootstrap import bootstrap_from_beir

        return bootstrap_from_beir

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
