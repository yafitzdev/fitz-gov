# fitz_gov/loader.py
"""
Data loader for FITZ-GOV benchmark cases.
"""

from __future__ import annotations

import json
from pathlib import Path

from .schema import FitzGovCase, FitzGovCategory

# Data directory is relative to this package
DATA_DIR = Path(__file__).parent.parent / "data"


def get_data_dir() -> Path:
    """Get the path to the benchmark data directory."""
    return DATA_DIR


def load_cases(
    categories: list[str] | None = None,
    data_dir: Path | str | None = None,
) -> list[FitzGovCase]:
    """
    Load FITZ-GOV test cases.

    Args:
        categories: List of category names to load. Defaults to all.
        data_dir: Custom data directory. Defaults to bundled data.

    Returns:
        List of FitzGovCase objects.
    """
    data_path = Path(data_dir) if data_dir else DATA_DIR
    cases: list[FitzGovCase] = []

    if not data_path.exists():
        raise FileNotFoundError(f"Data directory not found: {data_path}")

    # Map category names to FitzGovCategory
    category_map = {c.value: c for c in FitzGovCategory}

    # Determine which categories to load
    if categories:
        target_categories = [category_map[c] for c in categories if c in category_map]
    else:
        target_categories = list(FitzGovCategory)

    for cat in target_categories:
        cat_dir = data_path / cat.value
        if not cat_dir.exists():
            continue

        for json_file in cat_dir.glob("*.json"):
            try:
                with open(json_file, encoding="utf-8") as f:
                    data = json.load(f)

                for case_data in data.get("cases", []):
                    # Ensure category is set correctly
                    case_data["category"] = cat.value
                    case_data["subcategory"] = json_file.stem
                    cases.append(FitzGovCase.from_dict(case_data))

            except Exception as e:
                print(f"Warning: Failed to load {json_file}: {e}")

    return cases


def validate_cases(cases: list[FitzGovCase]) -> list[str]:
    """
    Validate test cases for common issues.

    Returns:
        List of validation error messages (empty if valid).
    """
    errors: list[str] = []
    seen_ids: set[str] = set()

    for case in cases:
        # Check for duplicate IDs
        if case.id in seen_ids:
            errors.append(f"Duplicate case ID: {case.id}")
        seen_ids.add(case.id)

        # Check required fields
        if not case.query.strip():
            errors.append(f"Case {case.id}: Empty query")

        if not case.contexts:
            errors.append(f"Case {case.id}: No contexts provided")

        if not case.description.strip():
            errors.append(f"Case {case.id}: Empty description")

        if not case.rationale.strip():
            errors.append(f"Case {case.id}: Empty rationale")

        # Category-specific validation
        if case.category == FitzGovCategory.GROUNDING:
            if not case.forbidden_claims:
                errors.append(f"Case {case.id}: GROUNDING case missing forbidden_claims")

        if case.category == FitzGovCategory.RELEVANCE:
            if not case.required_elements:
                errors.append(f"Case {case.id}: RELEVANCE case missing required_elements")

    return errors
