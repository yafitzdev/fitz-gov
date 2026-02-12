# fitz-gov/scripts/merge_staging_v2.py
"""
Merge staging_v2 cases into tier1_core after applying blind validation relabels.

Relabels (from blind validation):
1. t1_dispute_hard_407: disputed -> qualified (methodology_difference, not factual dispute)
2. t1_dispute_hard_419: disputed -> qualified (different metrics, not factual dispute)
3. t1_abstain_hard_867: abstain -> qualified (engineering practices ARE compliance-relevant)
4. t1_dispute_hard_506: disputed -> qualified (false premise with unanimous refutation)
"""
import json
import os
from collections import Counter

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
TIER1_DIR = os.path.join(DATA_DIR, "tier1_core")
STAGING_DIR = os.path.join(DATA_DIR, "staging_v2")

# Relabels from blind validation
RELABELS = {
    "t1_dispute_hard_407": {
        "category": "trustworthy_hedged",
        "expected_mode": "qualified",
        "subcategory": "methodology_difference",
        "relabel_reason": "EPA vs ACC use transparently different definitions of 'recycled'; structurally identical to qualified methodology_difference cases",
    },
    "t1_dispute_hard_419": {
        "category": "trustworthy_hedged",
        "expected_mode": "qualified",
        "subcategory": "methodology_difference",
        "relabel_reason": "ONS vs Fawcett Society measure different metrics (median hourly FT vs total annual all-workers); policy disagreement, not factual dispute",
    },
    "t1_abstain_hard_867": {
        "category": "trustworthy_hedged",
        "expected_mode": "qualified",
        "subcategory": "partial_answer",
        "relabel_reason": "Engineering practices (CI/CD, code review, monitoring) ARE compliance controls under SOC 2/ISO 27001; context is relevant but needs framework qualification",
    },
    "t1_dispute_hard_506": {
        "category": "trustworthy_hedged",
        "expected_mode": "qualified",
        "subcategory": "different_framing",
        "relabel_reason": "Both sources unanimously refute the query's false premise (revenue grew, not declined); structurally identical to qualified false-premise cases 907/908",
    },
}

# Category to tier1 filename mapping
CATEGORY_FILE_MAP = {
    "abstention": "abstention.json",
    "dispute": "dispute.json",
    "trustworthy_hedged": "trustworthy_hedged.json",
    "trustworthy_direct": "trustworthy_direct.json",
}


def load_staging_cases():
    """Load all staging_v2 JSON files and return flat list of cases."""
    all_cases = []
    staging_files = [
        "gen_dispute_boundary.json",
        "gen_edge_cases.json",
        "gen_code_adversarial.json",
    ]
    for fname in staging_files:
        fpath = os.path.join(STAGING_DIR, fname)
        if os.path.exists(fpath):
            with open(fpath, encoding="utf-8") as f:
                cases = json.load(f)
            print(f"  Loaded {len(cases)} cases from {fname}")
            all_cases.extend(cases)
    return all_cases


def apply_relabels(cases):
    """Apply blind validation relabels."""
    relabeled = 0
    for case in cases:
        cid = case["id"]
        if cid in RELABELS:
            relabel = RELABELS[cid]
            old_cat = case["category"]
            old_mode = case["expected_mode"]
            case["original_category"] = old_cat
            case["original_expected_mode"] = old_mode
            case["category"] = relabel["category"]
            case["expected_mode"] = relabel["expected_mode"]
            case["subcategory"] = relabel["subcategory"]
            case["relabel_reason"] = relabel["relabel_reason"]
            relabeled += 1
            print(f"  Relabeled {cid}: {old_cat}/{old_mode} -> {relabel['category']}/{relabel['expected_mode']}")
    return relabeled


def check_id_collisions(cases):
    """Check for ID collisions between staging and tier1."""
    existing_ids = set()
    for cat, fname in CATEGORY_FILE_MAP.items():
        fpath = os.path.join(TIER1_DIR, fname)
        if os.path.exists(fpath):
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
            for c in data["cases"]:
                existing_ids.add(c["id"])

    collisions = [c["id"] for c in cases if c["id"] in existing_ids]
    if collisions:
        print(f"  WARNING: {len(collisions)} ID collisions: {collisions[:5]}")
    else:
        print("  No ID collisions found")
    return collisions


def merge_into_tier1(cases):
    """Merge cases into tier1_core files by category."""
    # Group by category
    by_category = {}
    for case in cases:
        cat = case["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(case)

    total_merged = 0
    for cat, cat_cases in by_category.items():
        fname = CATEGORY_FILE_MAP[cat]
        fpath = os.path.join(TIER1_DIR, fname)

        with open(fpath, encoding="utf-8") as f:
            data = json.load(f)

        existing_ids = {c["id"] for c in data["cases"]}
        added = 0
        for case in cat_cases:
            if case["id"] not in existing_ids:
                data["cases"].append(case)
                added += 1

        # No metadata block in tier1_core files — just cases array in a wrapper

        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        total_merged += added
        print(f"  {cat}: added {added} cases (total now: {len(data['cases'])})")

    return total_merged


def main():
    print("=" * 60)
    print("  MERGE STAGING_V2 INTO TIER1_CORE")
    print("=" * 60)

    print("\n1. Loading staging cases...")
    cases = load_staging_cases()
    print(f"   Total: {len(cases)} cases")

    print("\n2. Applying blind validation relabels...")
    relabeled = apply_relabels(cases)
    print(f"   Relabeled: {relabeled} cases")

    print("\n3. Category distribution after relabels:")
    cat_counts = Counter(c["category"] for c in cases)
    for cat, count in sorted(cat_counts.items()):
        print(f"   {cat}: {count}")

    print("\n4. Checking for ID collisions...")
    collisions = check_id_collisions(cases)
    if collisions:
        print("   ABORTING: Fix collisions first")
        return

    print("\n5. Merging into tier1_core...")
    merged = merge_into_tier1(cases)
    print(f"   Total merged: {merged}")

    # Final summary
    print("\n" + "=" * 60)
    print("  FINAL TIER1_CORE COUNTS")
    print("=" * 60)
    grand_total = 0
    for cat, fname in CATEGORY_FILE_MAP.items():
        fpath = os.path.join(TIER1_DIR, fname)
        with open(fpath, encoding="utf-8") as f:
            data = json.load(f)
        n = len(data["cases"])
        grand_total += n
        print(f"  {cat}: {n} cases")
    print(f"  TOTAL: {grand_total} cases")
    print("=" * 60)


if __name__ == "__main__":
    main()
