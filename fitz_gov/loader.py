# fitz_gov/loader.py
"""
Data loader for fitz-gov benchmark test cases.

Supports both legacy flat structure and new tiered structure:
- tier0_sanity/: Baseline functionality verification (easy cases)
- tier1_core/: Primary benchmark discrimination (medium/hard cases)
"""

from __future__ import annotations

import json
import logging
from enum import Enum
from pathlib import Path
from typing import Literal

from .models import FitzGovCase, FitzGovCategory

logger = logging.getLogger(__name__)

# Package data directory
PACKAGE_DATA_DIR = Path(__file__).parent.parent / "data"

# Tier directories
TIER0_DIR = "tier0_sanity"
TIER1_DIR = "tier1_core"


class Tier(str, Enum):
    """Evaluation tiers."""

    SANITY = "tier0_sanity"
    """Tier 0: Baseline functionality - 95% threshold."""

    CORE = "tier1_core"
    """Tier 1: Primary benchmark - gradient scoring."""


def get_data_dir() -> Path:
    """Get the path to the benchmark data directory."""
    return PACKAGE_DATA_DIR


def get_tier_dir(tier: Tier | str, data_dir: Path | None = None) -> Path:
    """Get the path to a tier directory."""
    if data_dir is None:
        data_dir = PACKAGE_DATA_DIR

    if isinstance(tier, Tier):
        tier_name = tier.value
    else:
        tier_name = tier

    return data_dir / tier_name


def load_tier(
    tier: Tier | str,
    categories: list[FitzGovCategory] | None = None,
    data_dir: Path | None = None,
) -> list[FitzGovCase]:
    """
    Load test cases from a specific tier.

    Args:
        tier: Tier to load (Tier.SANITY or Tier.CORE).
        categories: Categories to load. Defaults to all.
        data_dir: Data directory. Defaults to package data dir.

    Returns:
        List of FitzGovCase objects from the specified tier.
    """
    if data_dir is None:
        data_dir = PACKAGE_DATA_DIR

    tier_dir = get_tier_dir(tier, data_dir)

    if not tier_dir.exists():
        logger.warning(f"Tier directory not found: {tier_dir}")
        return []

    cases: list[FitzGovCase] = []
    target_categories = categories or list(FitzGovCategory)

    for cat in target_categories:
        json_file = tier_dir / f"{cat.value}.json"
        if not json_file.exists():
            logger.debug(f"Category file not found: {json_file}")
            continue

        try:
            loaded = _load_tier_file(json_file, cat)
            cases.extend(loaded)
        except Exception as e:
            logger.warning(f"Failed to load {json_file}: {e}")

    tier_name = tier.value if isinstance(tier, Tier) else tier
    logger.info(f"Loaded {len(cases)} test cases from {tier_name}")
    return cases


def load_cases(
    categories: list[FitzGovCategory] | None = None,
    data_dir: Path | None = None,
    tiers: list[Tier | str] | None = None,
) -> list[FitzGovCase]:
    """
    Load test cases from data directory.

    Args:
        categories: Categories to load. Defaults to all.
        data_dir: Data directory. Defaults to package data dir.
        tiers: Tiers to load. Defaults to all tiers (tier0 + tier1).
               Pass [Tier.SANITY] for tier0 only, [Tier.CORE] for tier1 only.

    Returns:
        List of FitzGovCase objects.
    """
    if data_dir is None:
        data_dir = PACKAGE_DATA_DIR

    if not data_dir.exists():
        logger.warning(f"Data directory not found: {data_dir}")
        return []

    # Check if tiered structure exists
    tier0_exists = (data_dir / TIER0_DIR).exists()
    tier1_exists = (data_dir / TIER1_DIR).exists()

    if tier0_exists or tier1_exists:
        # Use tiered loading
        if tiers is None:
            tiers = [Tier.SANITY, Tier.CORE]

        cases: list[FitzGovCase] = []
        for tier in tiers:
            tier_cases = load_tier(tier, categories, data_dir)
            cases.extend(tier_cases)

        logger.info(f"Loaded {len(cases)} test cases from tiered structure")
        return cases

    # Fall back to legacy flat structure
    return _load_legacy_cases(categories, data_dir)


def _load_legacy_cases(
    categories: list[FitzGovCategory] | None = None,
    data_dir: Path | None = None,
) -> list[FitzGovCase]:
    """Load cases from legacy flat structure (backward compatibility)."""
    if data_dir is None:
        data_dir = PACKAGE_DATA_DIR

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
    """Load test cases from a single category JSON file (legacy format)."""
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


def _load_tier_file(json_file: Path, category: FitzGovCategory) -> list[FitzGovCase]:
    """Load test cases from a tier JSON file."""
    with open(json_file, encoding="utf-8") as f:
        data = json.load(f)

    # Get tier metadata
    tier = data.get("tier", "unknown")

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

        # Add tier to metadata
        if "metadata" not in case_data:
            case_data["metadata"] = {}
        case_data["metadata"]["tier"] = tier

        cases.append(FitzGovCase.from_dict(case_data))

    return cases


def load_case_by_id(case_id: str, data_dir: Path | None = None) -> FitzGovCase | None:
    """
    Load a single test case by ID.

    Args:
        case_id: The case ID (e.g., "t0_abstain_easy_001" or legacy "grounding_easy_001").
        data_dir: Data directory. Defaults to package data dir.

    Returns:
        FitzGovCase if found, None otherwise.
    """
    # Determine tier from prefix
    tiers_to_search: list[Tier | str] | None = None
    search_id = case_id

    if case_id.startswith("t0_"):
        tiers_to_search = [Tier.SANITY]
        search_id = case_id  # Keep full ID for matching
    elif case_id.startswith("t1_"):
        tiers_to_search = [Tier.CORE]
        search_id = case_id

    # Parse category from case_id (after tier prefix if present)
    id_without_prefix = case_id[3:] if case_id.startswith(("t0_", "t1_")) else case_id

    for cat in FitzGovCategory:
        if id_without_prefix.startswith(cat.value):
            cases = load_cases([cat], data_dir, tiers=tiers_to_search)
            for case in cases:
                if case.id == search_id:
                    return case
            break

    # Fallback: search all cases
    all_cases = load_cases(data_dir=data_dir, tiers=tiers_to_search)
    for case in all_cases:
        if case.id == search_id:
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

    # Check if tiered structure exists
    tier0_exists = (data_dir / TIER0_DIR).exists()
    tier1_exists = (data_dir / TIER1_DIR).exists()

    if tier0_exists or tier1_exists:
        return _get_tiered_category_info(data_dir)

    # Legacy structure
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


def _get_tiered_category_info(data_dir: Path) -> dict[str, dict]:
    """Get category info from tiered structure."""
    info = {}

    for cat in FitzGovCategory:
        tier0_count = 0
        tier1_count = 0
        description = ""
        version = "unknown"
        mode_rationale = ""

        # Count from tier0
        tier0_file = data_dir / TIER0_DIR / f"{cat.value}.json"
        if tier0_file.exists():
            with open(tier0_file, encoding="utf-8") as f:
                data = json.load(f)
            tier0_count = len(data.get("cases", []))
            description = data.get("description", "")
            version = data.get("version", version)
            mode_rationale = data.get("mode_rationale", "")

        # Count from tier1
        tier1_file = data_dir / TIER1_DIR / f"{cat.value}.json"
        if tier1_file.exists():
            with open(tier1_file, encoding="utf-8") as f:
                data = json.load(f)
            tier1_count = len(data.get("cases", []))
            if not description:
                description = data.get("description", "")
            if version == "unknown":
                version = data.get("version", version)
            if not mode_rationale:
                mode_rationale = data.get("mode_rationale", "")

        if tier0_count > 0 or tier1_count > 0:
            info[cat.value] = {
                "description": description,
                "version": version,
                "mode_rationale": mode_rationale,
                "case_count": tier0_count + tier1_count,
                "tier0_count": tier0_count,
                "tier1_count": tier1_count,
            }

    return info


def get_tier_info(data_dir: Path | None = None) -> dict[str, dict]:
    """
    Get metadata about each tier.

    Returns:
        Dict mapping tier name to metadata (description, threshold, case counts).
    """
    if data_dir is None:
        data_dir = PACKAGE_DATA_DIR

    info = {}

    for tier in Tier:
        tier_dir = data_dir / tier.value
        if not tier_dir.exists():
            continue

        total_cases = 0
        categories = {}

        for cat in FitzGovCategory:
            json_file = tier_dir / f"{cat.value}.json"
            if not json_file.exists():
                continue

            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)

            case_count = len(data.get("cases", []))
            total_cases += case_count
            categories[cat.value] = case_count

            # Get tier metadata from first file
            if "description" not in info.get(tier.value, {}):
                info[tier.value] = {
                    "tier": data.get("tier", tier.value),
                    "description": data.get("tier_description", ""),
                    "passing_threshold": data.get("passing_threshold"),
                    "version": data.get("version", "unknown"),
                }

        if tier.value in info:
            info[tier.value]["total_cases"] = total_cases
            info[tier.value]["categories"] = categories

    return info
