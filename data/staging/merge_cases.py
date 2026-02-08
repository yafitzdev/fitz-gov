# fitz-gov/data/staging/merge_cases.py
"""
Merge validated staging cases into tier1_core data files.
Handles: duplicate removal, relabeling, ID reassignment, and file merge.
"""
import json
import os
import glob
import copy

STAGING_DIR = os.path.dirname(os.path.abspath(__file__))
TIER1_DIR = os.path.join(os.path.dirname(STAGING_DIR), "tier1_core")

# === CASES TO REMOVE (duplicates) ===
REMOVE_IDS = {
    "t1_qualify_hard_332",      # Duplicate query of t1_qualify_hard_215
    "t1_confident_hard_104",    # Same query as t1_dispute_hard_117
    "t1_confident_hard_132",    # Same query as existing t1_abstain_medium_004
    "t1_confident_hard_605",    # Same query as existing t1_confident_hard_030
    "t1_qualify_hard_660",      # Same query as existing t1_abstain_medium_013
}

# === CASES TO RELABEL ===
# dispute → qualified (methodology differences, not genuine disputes)
RELABEL_TO_QUALIFIED = {
    "t1_dispute_hard_200",  # as-reported vs pro forma revenue
    "t1_dispute_hard_205",  # direct vs total project cost
    "t1_dispute_hard_206",  # count vs mass microplastic measurement
    "t1_dispute_hard_120",  # JWST "complete" vs "ongoing refinement"
}

# qualified → abstain (cross-domain transfer stretches qualify too far)
RELABEL_TO_ABSTAIN = {
    "t1_qualify_hard_630",  # JS/Node for Python query
    "t1_qualify_hard_634",  # Australia/Argentina for Chile query
    "t1_qualify_hard_635",  # GitHub/Jenkins/Azure for GitLab query
}

# Category mapping
MODE_TO_CATEGORY = {
    "abstain": "abstention",
    "disputed": "dispute",
    "qualified": "qualification",
    "confident": "confidence",
}

CATEGORY_TO_FILE = {
    "abstention": "abstention.json",
    "dispute": "dispute.json",
    "qualification": "qualification.json",
    "confidence": "confidence.json",
}


def load_staging_cases():
    """Load all staging JSON files and return flat list of cases."""
    all_cases = []
    for f in sorted(glob.glob(os.path.join(STAGING_DIR, "gen_*.json"))):
        with open(f, encoding="utf-8") as fh:
            cases = json.load(fh)
            print(f"  Loaded {len(cases)} from {os.path.basename(f)}")
            all_cases.extend(cases)
    # Also check for batch files
    for f in sorted(glob.glob(os.path.join(STAGING_DIR, "batch*.json"))):
        with open(f, encoding="utf-8") as fh:
            cases = json.load(fh)
            # Check if these are already in gen_threeway.json (might be intermediate)
            existing_ids = {c["id"] for c in all_cases}
            new_cases = [c for c in cases if c["id"] not in existing_ids]
            if new_cases:
                print(f"  Loaded {len(new_cases)} unique from {os.path.basename(f)}")
                all_cases.extend(new_cases)
            else:
                print(f"  Skipped {os.path.basename(f)} (all IDs already in gen files)")
    return all_cases


def remove_duplicates(cases):
    """Remove cases with duplicate IDs."""
    before = len(cases)
    cases = [c for c in cases if c["id"] not in REMOVE_IDS]
    removed = before - len(cases)
    print(f"  Removed {removed} duplicate cases")
    return cases


def find_max_id(cases, prefix):
    """Find the maximum ID number for a given prefix."""
    max_num = 0
    for c in cases:
        if c["id"].startswith(prefix):
            try:
                num = int(c["id"].split("_")[-1])
                max_num = max(max_num, num)
            except ValueError:
                pass
    return max_num


def relabel_cases(cases):
    """Relabel cases that need mode changes."""
    relabeled = 0
    for case in cases:
        if case["id"] in RELABEL_TO_QUALIFIED:
            case["expected_mode"] = "qualified"
            case["category"] = "qualification"
            # Generate new ID
            old_id = case["id"]
            case["id"] = f"t1_qualify_hard_7{relabeled:02d}"
            case["subcategory"] = "methodology_difference_relabeled"
            case["rationale"] += " [RELABELED: Originally marked as dispute but methodology/scope difference is not a genuine factual conflict.]"
            case["description"] += " (relabeled from dispute)"
            print(f"  Relabeled {old_id} -> {case['id']} (dispute -> qualified)")
            relabeled += 1

        elif case["id"] in RELABEL_TO_ABSTAIN:
            old_id = case["id"]
            case["expected_mode"] = "abstain"
            case["category"] = "abstention"
            case["id"] = f"t1_abstain_hard_7{relabeled:02d}"
            case["subcategory"] = "cross_domain_insufficient"
            case["rationale"] += " [RELABELED: Cross-domain transfer insufficient - contexts are about wrong language/country/platform.]"
            case["description"] += " (relabeled from qualified)"
            print(f"  Relabeled {old_id} -> {case['id']} (qualified -> abstain)")
            relabeled += 1

    print(f"  Total relabeled: {relabeled}")
    return cases


def load_existing_tier1():
    """Load existing tier1_core files."""
    existing = {}
    for cat, fname in CATEGORY_TO_FILE.items():
        fpath = os.path.join(TIER1_DIR, fname)
        if os.path.exists(fpath):
            with open(fpath, encoding="utf-8") as fh:
                data = json.load(fh)
                existing[cat] = data
                print(f"  Existing {cat}: {len(data['cases'])} cases")
    return existing


def merge_and_write(new_cases, existing):
    """Merge new cases into existing tier1_core files."""
    # Group new cases by category
    by_category = {}
    for case in new_cases:
        cat = case["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(case)

    print("\n  New cases by category:")
    for cat, cases in sorted(by_category.items()):
        print(f"    {cat}: {len(cases)}")

    # Merge into existing
    for cat, cases in by_category.items():
        if cat in existing:
            data = existing[cat]
            existing_ids = {c["id"] for c in data["cases"]}

            # Check for ID conflicts
            conflicts = [c for c in cases if c["id"] in existing_ids]
            if conflicts:
                print(f"  WARNING: {len(conflicts)} ID conflicts in {cat}!")
                for c in conflicts:
                    print(f"    Conflict: {c['id']}")
                # Skip conflicting cases
                cases = [c for c in cases if c["id"] not in existing_ids]

            data["cases"].extend(cases)

            # Sort cases by ID
            data["cases"].sort(key=lambda c: c["id"])

            # Write back
            fpath = os.path.join(TIER1_DIR, CATEGORY_TO_FILE[cat])
            with open(fpath, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
            print(f"  Wrote {cat}: {len(data['cases'])} total cases -> {CATEGORY_TO_FILE[cat]}")
        else:
            print(f"  WARNING: No existing file for category {cat}")


def main():
    print("=== Loading staging cases ===")
    cases = load_staging_cases()
    print(f"  Total loaded: {len(cases)}")

    print("\n=== Removing duplicates ===")
    cases = remove_duplicates(cases)
    print(f"  After removal: {len(cases)}")

    print("\n=== Relabeling cases ===")
    cases = relabel_cases(cases)

    print("\n=== Loading existing tier1_core ===")
    existing = load_existing_tier1()

    print("\n=== Merging ===")
    merge_and_write(cases, existing)

    # Final summary
    print("\n=== FINAL SUMMARY ===")
    total = 0
    for cat, fname in CATEGORY_TO_FILE.items():
        fpath = os.path.join(TIER1_DIR, fname)
        if os.path.exists(fpath):
            with open(fpath, encoding="utf-8") as fh:
                data = json.load(fh)
                count = len(data["cases"])
                total += count
                print(f"  {cat}: {count} cases")
    # Add tier0
    tier0_dir = os.path.join(os.path.dirname(STAGING_DIR), "tier0_sanity")
    tier0_total = 0
    for f in glob.glob(os.path.join(tier0_dir, "*.json")):
        with open(f, encoding="utf-8") as fh:
            data = json.load(fh)
            tier0_total += len(data["cases"])
    print(f"\n  Tier 0 (sanity): {tier0_total} cases")
    print(f"  Tier 1 (core): {total} cases")
    print(f"  GRAND TOTAL: {tier0_total + total} cases")


if __name__ == "__main__":
    main()
