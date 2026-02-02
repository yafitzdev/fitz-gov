# scripts/validate.py
"""
Validation script for FITZ-GOV benchmark test data.

Verifies:
- Schema consistency across all category files
- No duplicate case IDs
- Difficulty distribution
- Required fields present
- Version consistency
"""

import json
import os
import sys
from collections import Counter
from pathlib import Path


def load_category(base_path: Path, category: str) -> dict:
    """Load a category JSON file."""
    path = base_path / category / f"{category}.json"
    with open(path) as f:
        return json.load(f)


def validate_case_schema(case: dict, category: str) -> list[str]:
    """Validate a single case has required fields."""
    errors = []
    required = ["id", "difficulty", "query", "contexts", "expected_mode", "description", "rationale"]

    for field in required:
        if field not in case:
            errors.append(f"{case.get('id', 'UNKNOWN')}: Missing required field '{field}'")

    # Validate difficulty value
    if case.get("difficulty") not in ["easy", "medium", "hard"]:
        errors.append(f"{case.get('id')}: Invalid difficulty '{case.get('difficulty')}'")

    # Validate expected_mode value
    valid_modes = ["abstain", "disputed", "qualified", "confident"]
    if case.get("expected_mode") not in valid_modes:
        errors.append(f"{case.get('id')}: Invalid expected_mode '{case.get('expected_mode')}'")

    # Validate contexts is non-empty list
    if not case.get("contexts") or not isinstance(case.get("contexts"), list):
        errors.append(f"{case.get('id')}: contexts must be non-empty list")

    # Category-specific validations
    if category == "grounding" and "forbidden_claims" not in case:
        errors.append(f"{case.get('id')}: Grounding case missing forbidden_claims")

    if category == "relevance" and "required_elements" not in case:
        errors.append(f"{case.get('id')}: Relevance case missing required_elements")

    return errors


def validate_category(base_path: Path, category: str) -> tuple[list[str], dict]:
    """Validate a category and return errors and stats."""
    errors = []
    stats = {
        "total": 0,
        "easy": 0,
        "medium": 0,
        "hard": 0,
        "subcategories": Counter(),
    }

    try:
        data = load_category(base_path, category)
    except FileNotFoundError:
        errors.append(f"Category file not found: {category}")
        return errors, stats
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in {category}: {e}")
        return errors, stats

    # Check top-level fields
    if "version" not in data:
        errors.append(f"{category}: Missing version field")

    if "mode_rationale" not in data:
        errors.append(f"{category}: Missing mode_rationale field")

    if "cases" not in data:
        errors.append(f"{category}: Missing cases array")
        return errors, stats

    # Validate each case
    seen_ids = set()
    for case in data["cases"]:
        case_id = case.get("id", "UNKNOWN")

        # Check for duplicate IDs
        if case_id in seen_ids:
            errors.append(f"{category}: Duplicate case ID '{case_id}'")
        seen_ids.add(case_id)

        # Validate case schema
        case_errors = validate_case_schema(case, category)
        errors.extend(case_errors)

        # Collect stats
        stats["total"] += 1
        difficulty = case.get("difficulty")
        if difficulty in stats:
            stats[difficulty] += 1

        subcategory = case.get("subcategory", "unknown")
        stats["subcategories"][subcategory] += 1

    return errors, stats


def main():
    """Run validation on all categories."""
    base_path = Path(__file__).parent.parent / "data"
    categories = ["abstention", "dispute", "qualification", "confidence", "grounding", "relevance"]

    all_errors = []
    all_stats = {}
    all_ids = set()
    global_duplicate_ids = []

    print("=" * 60)
    print("FITZ-GOV Validation Report")
    print("=" * 60)

    for category in categories:
        print(f"\nValidating {category}...")
        errors, stats = validate_category(base_path, category)
        all_errors.extend(errors)
        all_stats[category] = stats

        # Check for cross-category duplicate IDs
        for case in load_category(base_path, category).get("cases", []):
            case_id = case.get("id")
            if case_id in all_ids:
                global_duplicate_ids.append(case_id)
            all_ids.add(case_id)

        print(f"  Cases: {stats['total']}")
        print(f"  Difficulty: easy={stats['easy']}, medium={stats['medium']}, hard={stats['hard']}")
        print(f"  Errors: {len([e for e in errors if category in e])}")

    # Global checks
    if global_duplicate_ids:
        for dup_id in global_duplicate_ids:
            all_errors.append(f"GLOBAL: Duplicate ID across categories: '{dup_id}'")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    total_cases = sum(s["total"] for s in all_stats.values())
    total_easy = sum(s["easy"] for s in all_stats.values())
    total_medium = sum(s["medium"] for s in all_stats.values())
    total_hard = sum(s["hard"] for s in all_stats.values())

    print(f"\nTotal cases: {total_cases}")
    print(f"Difficulty distribution:")
    print(f"  Easy:   {total_easy:3d} ({total_easy*100/total_cases:.1f}%)")
    print(f"  Medium: {total_medium:3d} ({total_medium*100/total_cases:.1f}%)")
    print(f"  Hard:   {total_hard:3d} ({total_hard*100/total_cases:.1f}%)")

    print(f"\nPer-category breakdown:")
    for cat, stats in all_stats.items():
        print(f"  {cat}: {stats['total']} cases")

    print(f"\n" + "=" * 60)
    if all_errors:
        print(f"ERRORS FOUND: {len(all_errors)}")
        print("=" * 60)
        for error in all_errors:
            print(f"  [ERROR] {error}")
        sys.exit(1)
    else:
        print("[OK] All validations passed!")
        print("=" * 60)
        sys.exit(0)


if __name__ == "__main__":
    main()
