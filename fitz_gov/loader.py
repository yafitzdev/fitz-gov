# fitz_gov/loader.py
"""
Data loader for fitz-gov benchmark test cases.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from .models import FitzGovCase, FitzGovCategory

logger = logging.getLogger(__name__)

# Package data directory
PACKAGE_DATA_DIR = Path(__file__).parent.parent / "data"


def get_data_dir() -> Path:
    """Get the path to the benchmark data directory."""
    return PACKAGE_DATA_DIR


def load_cases(
    categories: list[FitzGovCategory] | None = None,
    data_dir: Path | None = None,
) -> list[FitzGovCase]:
    """
    Load test cases from data directory.

    Args:
        categories: Categories to load. Defaults to all.
        data_dir: Data directory. Defaults to package data dir.

    Returns:
        List of FitzGovCase objects.
    """
    if data_dir is None:
        data_dir = PACKAGE_DATA_DIR

    if not data_dir.exists():
        logger.warning(f"Data directory not found: {data_dir}")
        return []

    cases: list[FitzGovCase] = []
    target_categories = categories or list(FitzGovCategory)

    for cat in target_categories:
        cat_dir = data_dir / cat.value
        if not cat_dir.exists():
            logger.debug(f"Category directory not found: {cat_dir}")
            continue

        for json_file in cat_dir.glob("*.json"):
            try:
                loaded = _load_category_file(json_file, cat)
                cases.extend(loaded)
            except Exception as e:
                logger.warning(f"Failed to load {json_file}: {e}")

    logger.info(f"Loaded {len(cases)} test cases from {data_dir}")
    return cases


def _load_category_file(json_file: Path, category: FitzGovCategory) -> list[FitzGovCase]:
    """Load test cases from a single category JSON file."""
    with open(json_file, encoding="utf-8") as f:
        data = json.load(f)

    # Get category-level evaluation config
    category_eval_config = data.get("evaluation_config", {})

    cases = []
    for case_data in data.get("cases", []):
        case_data["category"] = category.value

        # Use file stem as subcategory if not specified
        if "subcategory" not in case_data:
            case_data["subcategory"] = json_file.stem

        # Merge category-level eval config with case-level
        case_eval_config = case_data.get("evaluation_config", {})
        merged_config = {**category_eval_config, **case_eval_config}
        case_data["evaluation_config"] = merged_config

        cases.append(FitzGovCase.from_dict(case_data))

    return cases


def load_case_by_id(case_id: str, data_dir: Path | None = None) -> FitzGovCase | None:
    """
    Load a single test case by ID.

    Args:
        case_id: The case ID (e.g., "grounding_easy_001").
        data_dir: Data directory. Defaults to package data dir.

    Returns:
        FitzGovCase if found, None otherwise.
    """
    # Parse category from case_id
    for cat in FitzGovCategory:
        if case_id.startswith(cat.value):
            cases = load_cases([cat], data_dir)
            for case in cases:
                if case.id == case_id:
                    return case
            break

    # Fallback: search all categories
    all_cases = load_cases(data_dir=data_dir)
    for case in all_cases:
        if case.id == case_id:
            return case

    return None


def get_category_info(data_dir: Path | None = None) -> dict[str, dict]:
    """
    Get metadata about each category.

    Returns:
        Dict mapping category name to metadata (description, version, case count).
    """
    if data_dir is None:
        data_dir = PACKAGE_DATA_DIR

    info = {}
    for cat in FitzGovCategory:
        cat_dir = data_dir / cat.value
        if not cat_dir.exists():
            continue

        # Load first JSON file to get metadata
        json_files = list(cat_dir.glob("*.json"))
        if not json_files:
            continue

        with open(json_files[0], encoding="utf-8") as f:
            data = json.load(f)

        case_count = sum(
            len(json.load(open(jf, encoding="utf-8")).get("cases", []))
            for jf in json_files
        )

        info[cat.value] = {
            "description": data.get("description", ""),
            "version": data.get("version", "unknown"),
            "mode_rationale": data.get("mode_rationale", ""),
            "case_count": case_count,
        }

    return info
