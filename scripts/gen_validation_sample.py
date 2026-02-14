"""Generate a stratified validation sample of 250 cases for human inter-annotator agreement.

Sampling strategy:
  1. Proportional to category size (out of 2920 total)
  2. Within each category, proportional to difficulty distribution
  3. Within each difficulty stratum, proportional to domain distribution
  4. Seed=42 for reproducibility

Uses largest-remainder (Hamilton) method at each allocation level to ensure
exact totals while maintaining proportionality.
"""

import json
import math
import random
from collections import defaultdict
from pathlib import Path

SEED = 42
TOTAL_SAMPLE = 250
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "tier1_core"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "validation"

CATEGORIES = [
    "abstention",
    "dispute",
    "trustworthy_hedged",
    "trustworthy_direct",
    "grounding",
    "relevance",
]

GOLD_LABEL_MAP = {
    "abstention": "abstain",
    "dispute": "disputed",
    "trustworthy_hedged": "trustworthy",
    "trustworthy_direct": "trustworthy",
    "grounding": "trustworthy",
    "relevance": "trustworthy",
}


def largest_remainder_allocation(
    groups: list[str], sizes: dict[str, int], total_target: int
) -> dict[str, int]:
    """Allocate total_target items proportionally using largest-remainder method.

    This guarantees the allocations sum to exactly total_target while being
    as proportional as possible to the group sizes.
    """
    grand_total = sum(sizes[g] for g in groups)
    if grand_total == 0:
        return {g: 0 for g in groups}

    # Compute exact quotas
    quotas = {g: sizes[g] / grand_total * total_target for g in groups}

    # Floor allocations
    floors = {g: math.floor(quotas[g]) for g in groups}
    remainders = {g: quotas[g] - floors[g] for g in groups}

    # Distribute remaining seats by largest remainder
    remaining = total_target - sum(floors.values())
    sorted_by_remainder = sorted(groups, key=lambda g: remainders[g], reverse=True)

    result = dict(floors)
    for i in range(remaining):
        result[sorted_by_remainder[i]] += 1

    return result


def load_cases(category: str) -> list[dict]:
    """Load all cases from a tier1_core JSON file."""
    filepath = DATA_DIR / f"{category}.json"
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["cases"]


def stratified_sample_category(
    cases: list[dict],
    target_count: int,
    rng: random.Random,
) -> list[dict]:
    """Sample target_count cases from a category, stratified by difficulty then domain."""
    # Group by difficulty
    by_difficulty: dict[str, list[dict]] = defaultdict(list)
    for case in cases:
        by_difficulty[case.get("difficulty", "unknown")].append(case)

    difficulties = sorted(by_difficulty.keys())
    diff_sizes = {d: len(by_difficulty[d]) for d in difficulties}
    difficulty_targets = largest_remainder_allocation(
        difficulties, diff_sizes, target_count
    )

    sampled: list[dict] = []
    for diff in difficulties:
        diff_cases = by_difficulty[diff]
        diff_target = difficulty_targets[diff]

        if diff_target <= 0:
            continue

        # Group by domain within this difficulty
        by_domain: dict[str, list[dict]] = defaultdict(list)
        for case in diff_cases:
            by_domain[case.get("domain", "unknown")].append(case)

        domains = sorted(by_domain.keys())
        dom_sizes = {d: len(by_domain[d]) for d in domains}
        domain_targets = largest_remainder_allocation(
            domains, dom_sizes, diff_target
        )

        # Sample from each domain
        for dom in domains:
            dom_cases = by_domain[dom]
            dom_target = domain_targets[dom]
            if dom_target <= 0:
                continue
            # If we need more than available, take all
            if dom_target >= len(dom_cases):
                sampled.extend(dom_cases)
            else:
                sampled.extend(rng.sample(dom_cases, dom_target))

    return sampled


def main() -> None:
    rng = random.Random(SEED)

    # Load all categories and compute proportional targets
    all_cases: dict[str, list[dict]] = {}
    for cat in CATEGORIES:
        all_cases[cat] = load_cases(cat)

    grand_total = sum(len(v) for v in all_cases.values())
    print(f"Grand total cases: {grand_total}")

    # Compute category targets proportionally using largest-remainder
    cat_sizes = {cat: len(all_cases[cat]) for cat in CATEGORIES}
    category_targets = largest_remainder_allocation(
        CATEGORIES, cat_sizes, TOTAL_SAMPLE
    )

    print("Category targets:")
    for cat in CATEGORIES:
        print(f"  {cat}: {category_targets[cat]} (from {len(all_cases[cat])} cases)")
    print(f"  Sum: {sum(category_targets.values())}")

    # Sample from each category
    all_sampled: list[dict] = []
    categories_sampled: dict[str, int] = {}

    for cat in CATEGORIES:
        sampled = stratified_sample_category(
            all_cases[cat], category_targets[cat], rng
        )
        categories_sampled[cat] = len(sampled)
        for case in sampled:
            all_sampled.append(
                {
                    "case_id": case["id"],
                    "category": cat,
                    "difficulty": case.get("difficulty", "unknown"),
                    "domain": case.get("domain", "unknown"),
                    "query": case["query"],
                    "contexts": case["contexts"],
                    "gold_label": GOLD_LABEL_MAP[cat],
                }
            )

    # Shuffle the final list so annotators don't see categories in blocks
    rng.shuffle(all_sampled)

    # Assign sample indices and annotation placeholders
    for idx, item in enumerate(all_sampled, start=1):
        item["sample_index"] = idx
        item["annotator_1"] = {"mode": None, "confidence": None, "notes": None}
        item["annotator_2"] = {"mode": None, "confidence": None, "notes": None}
        item["agreement"] = None

    # Reorder keys so sample_index comes first
    ordered_sampled = []
    for item in all_sampled:
        ordered = {
            "sample_index": item["sample_index"],
            "case_id": item["case_id"],
            "category": item["category"],
            "difficulty": item["difficulty"],
            "domain": item["domain"],
            "query": item["query"],
            "contexts": item["contexts"],
            "gold_label": item["gold_label"],
            "annotator_1": item["annotator_1"],
            "annotator_2": item["annotator_2"],
            "agreement": item["agreement"],
        }
        ordered_sampled.append(ordered)

    output = {
        "version": "1.0",
        "description": "Stratified sample of 250 cases for human inter-annotator agreement validation",
        "sample_size": len(ordered_sampled),
        "sampling_method": "stratified by category, difficulty, and domain with seed=42",
        "annotation_guidelines_version": "1.0",
        "categories_sampled": categories_sampled,
        "cases": ordered_sampled,
    }

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "human_validation_sample.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nWrote {len(ordered_sampled)} cases to {output_path}")
    print(f"Categories sampled: {categories_sampled}")
    total_check = sum(categories_sampled.values())
    print(f"Total sampled: {total_check}")

    # Verify exact count
    assert total_check == TOTAL_SAMPLE, (
        f"Expected {TOTAL_SAMPLE} samples, got {total_check}"
    )
    print("Verification passed: exactly 250 cases sampled.")


if __name__ == "__main__":
    main()
