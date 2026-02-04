#!/usr/bin/env python3
"""
Migrate fitz-gov cases to tiered structure.

Splits cases by difficulty:
- easy -> tier0_sanity
- medium/hard -> tier1_core
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
TIER0_DIR = DATA_DIR / "tier0_sanity"
TIER1_DIR = DATA_DIR / "tier1_core"

CATEGORIES = ["abstention", "dispute", "qualification", "confidence", "grounding", "relevance"]


def migrate_category(category: str) -> tuple[int, int]:
    """Migrate a single category to tiered structure."""
    source_file = DATA_DIR / category / f"{category}.json"

    if not source_file.exists():
        print(f"  Skipping {category}: source file not found")
        return 0, 0

    with open(source_file, encoding="utf-8") as f:
        data = json.load(f)

    # Split cases by difficulty
    tier0_cases = []
    tier1_cases = []

    for case in data.get("cases", []):
        difficulty = case.get("difficulty", "medium")

        # Create new ID with tier prefix
        old_id = case["id"]

        if difficulty == "easy":
            # Tier 0: t0_<category_prefix>_<number>
            new_id = f"t0_{old_id}"
            case["id"] = new_id
            case["original_id"] = old_id
            tier0_cases.append(case)
        else:
            # Tier 1: t1_<category_prefix>_<number>
            new_id = f"t1_{old_id}"
            case["id"] = new_id
            case["original_id"] = old_id
            tier1_cases.append(case)

    # Build tier0 JSON
    tier0_data = {
        "tier": "sanity",
        "tier_description": "Baseline functionality verification - models should score 95%+",
        "passing_threshold": 0.95,
        "category": category,
        "description": data.get("description", ""),
        "version": "1.0.0",
        "mode_rationale": data.get("mode_rationale", ""),
        "cases": tier0_cases,
    }

    # Include evaluation_config if present (for grounding/relevance)
    if "evaluation_config" in data:
        tier0_data["evaluation_config"] = data["evaluation_config"]

    # Build tier1 JSON
    tier1_data = {
        "tier": "core",
        "tier_description": "Primary benchmark for model discrimination",
        "category": category,
        "description": data.get("description", ""),
        "version": "1.0.0",
        "mode_rationale": data.get("mode_rationale", ""),
        "cases": tier1_cases,
    }

    if "evaluation_config" in data:
        tier1_data["evaluation_config"] = data["evaluation_config"]

    # Write tier0
    tier0_file = TIER0_DIR / f"{category}.json"
    with open(tier0_file, "w", encoding="utf-8") as f:
        json.dump(tier0_data, f, indent=2, ensure_ascii=False)

    # Write tier1
    tier1_file = TIER1_DIR / f"{category}.json"
    with open(tier1_file, "w", encoding="utf-8") as f:
        json.dump(tier1_data, f, indent=2, ensure_ascii=False)

    return len(tier0_cases), len(tier1_cases)


def main():
    """Run migration."""
    print("Migrating fitz-gov cases to tiered structure...")
    print(f"Source: {DATA_DIR}")
    print(f"Tier 0: {TIER0_DIR}")
    print(f"Tier 1: {TIER1_DIR}")
    print()

    # Ensure directories exist
    TIER0_DIR.mkdir(parents=True, exist_ok=True)
    TIER1_DIR.mkdir(parents=True, exist_ok=True)

    total_tier0 = 0
    total_tier1 = 0

    for category in CATEGORIES:
        t0, t1 = migrate_category(category)
        print(f"  {category}: {t0} -> tier0, {t1} -> tier1")
        total_tier0 += t0
        total_tier1 += t1

    print()
    print(f"Total: {total_tier0} tier0 cases, {total_tier1} tier1 cases")
    print(f"Combined: {total_tier0 + total_tier1} cases")
    print()
    print("Migration complete!")


if __name__ == "__main__":
    main()
