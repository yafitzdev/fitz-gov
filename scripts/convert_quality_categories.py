#!/usr/bin/env python3
"""
Convert grounding and relevance cases into trustworthy_hedged.

Part of fitz-gov v5.0 migration: grounding and relevance become cross-cutting
quality checks on all trustworthy cases, not standalone categories.

This script:
1. Loads grounding.json and relevance.json from tier0 and tier1
2. Changes category to trustworthy_hedged
3. Prefixes subcategories with grounding_/relevance_ to avoid conflicts
4. Updates evaluation_config from answer_quality to governance
5. Appends cases to trustworthy_hedged.json
6. Deletes old grounding.json and relevance.json files
"""

import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def convert_grounding_case(case: dict) -> dict:
    """Convert a grounding case to trustworthy_hedged."""
    case["category"] = "trustworthy_hedged"
    # Prefix subcategory to avoid conflicts with existing trustworthy_hedged subcategories
    if not case.get("subcategory", "").startswith("grounding_"):
        case["subcategory"] = f"grounding_{case.get('subcategory', 'unknown')}"
    # Update evaluation_config
    ec = case.get("evaluation_config", {})
    ec["mode"] = "governance"
    ec["check_mode_match"] = True
    # Keep use_regex, case_insensitive, allowed_phrases as-is
    case["evaluation_config"] = ec
    return case


def convert_relevance_case(case: dict) -> dict:
    """Convert a relevance case to trustworthy_hedged."""
    case["category"] = "trustworthy_hedged"
    if not case.get("subcategory", "").startswith("relevance_"):
        case["subcategory"] = f"relevance_{case.get('subcategory', 'unknown')}"
    ec = case.get("evaluation_config", {})
    ec["mode"] = "governance"
    ec["check_mode_match"] = True
    case["evaluation_config"] = ec
    return case


def process_tier(tier_dir: Path, tier_name: str) -> None:
    """Process a single tier directory."""
    grounding_file = tier_dir / "grounding.json"
    relevance_file = tier_dir / "relevance.json"
    hedged_file = tier_dir / "trustworthy_hedged.json"

    if not hedged_file.exists():
        print(f"  WARNING: {hedged_file} not found, skipping {tier_name}")
        return

    # Load existing trustworthy_hedged
    with open(hedged_file, encoding="utf-8") as f:
        hedged_data = json.load(f)

    original_count = len(hedged_data["cases"])
    converted_count = 0

    # Also update file-level metadata
    file_eval_config = hedged_data.get("evaluation_config", {})

    # Convert grounding cases
    if grounding_file.exists():
        with open(grounding_file, encoding="utf-8") as f:
            grounding_data = json.load(f)

        # Preserve file-level allowed_phrases from grounding for reference
        grounding_file_config = grounding_data.get("evaluation_config", {})

        for case in grounding_data["cases"]:
            # Merge file-level eval config into case if case doesn't have its own
            if "evaluation_config" not in case:
                case["evaluation_config"] = dict(grounding_file_config)
            else:
                # Case-level overrides file-level
                merged = dict(grounding_file_config)
                merged.update(case["evaluation_config"])
                case["evaluation_config"] = merged

            converted = convert_grounding_case(case)
            hedged_data["cases"].append(converted)
            converted_count += 1

        print(f"  Converted {len(grounding_data['cases'])} grounding cases from {tier_name}")
        grounding_file.unlink()
        print(f"  Deleted {grounding_file}")
    else:
        print(f"  No grounding.json in {tier_name}")

    # Convert relevance cases
    if relevance_file.exists():
        with open(relevance_file, encoding="utf-8") as f:
            relevance_data = json.load(f)

        relevance_file_config = relevance_data.get("evaluation_config", {})

        for case in relevance_data["cases"]:
            if "evaluation_config" not in case:
                case["evaluation_config"] = dict(relevance_file_config)
            else:
                merged = dict(relevance_file_config)
                merged.update(case["evaluation_config"])
                case["evaluation_config"] = merged

            converted = convert_relevance_case(case)
            hedged_data["cases"].append(converted)
            converted_count += 1

        print(f"  Converted {len(relevance_data['cases'])} relevance cases from {tier_name}")
        relevance_file.unlink()
        print(f"  Deleted {relevance_file}")
    else:
        print(f"  No relevance.json in {tier_name}")

    # Update file metadata
    hedged_data["version"] = "5.0.0"
    hedged_data["description"] = (
        "Queries where context provides partial/uncertain evidence - "
        "system should answer with hedging (TRUSTWORTHY mode, hedged behavior). "
        "Includes grounding and relevance quality checks."
    )

    # Write updated trustworthy_hedged
    with open(hedged_file, "w", encoding="utf-8") as f:
        json.dump(hedged_data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    total = len(hedged_data["cases"])
    print(f"  trustworthy_hedged.json: {original_count} original + {converted_count} converted = {total} total")


def main():
    print("=== Converting grounding/relevance to cross-cutting quality checks ===\n")

    # Process tier0
    tier0_dir = DATA_DIR / "tier0_sanity"
    if tier0_dir.exists():
        print("Processing tier0_sanity:")
        process_tier(tier0_dir, "tier0")

    print()

    # Process tier1
    tier1_dir = DATA_DIR / "tier1_core"
    if tier1_dir.exists():
        print("Processing tier1_core:")
        process_tier(tier1_dir, "tier1")

    print("\n=== Verification ===")
    # Verify the results
    for tier_name in ["tier0_sanity", "tier1_core"]:
        tier_dir = DATA_DIR / tier_name
        if not tier_dir.exists():
            continue
        json_files = list(tier_dir.glob("*.json"))
        print(f"\n{tier_name} files: {[f.name for f in json_files]}")
        for jf in sorted(json_files):
            with open(jf, encoding="utf-8") as f:
                data = json.load(f)
            print(f"  {jf.name}: {len(data['cases'])} cases")

    # Verify no grounding/relevance files remain
    for tier_name in ["tier0_sanity", "tier1_core"]:
        tier_dir = DATA_DIR / tier_name
        for old_file in ["grounding.json", "relevance.json"]:
            if (tier_dir / old_file).exists():
                print(f"\n  ERROR: {tier_dir / old_file} still exists!")
                sys.exit(1)

    print("\nDone! Grounding and relevance merged into trustworthy_hedged.")


if __name__ == "__main__":
    main()
