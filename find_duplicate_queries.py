import json
import os
import re
import string
from collections import defaultdict
from pathlib import Path

DATA_ROOT = Path(r"C:\Users\yanfi\PycharmProjects\fitz-gov\data")
TIERS = ["tier0_sanity", "tier1_core"]

def normalize(query: str) -> str:
    """Lowercase, strip whitespace, remove punctuation."""
    q = query.lower().strip()
    q = q.translate(str.maketrans("", "", string.punctuation))
    # collapse multiple spaces
    q = re.sub(r"\s+", " ", q)
    return q

def main():
    # key: normalized query -> list of (id, category, difficulty, original_query, tier, file)
    groups = defaultdict(list)

    for tier in TIERS:
        tier_dir = DATA_ROOT / tier
        if not tier_dir.exists():
            print(f"WARNING: {tier_dir} does not exist, skipping.")
            continue
        for json_file in sorted(tier_dir.glob("*.json")):
            category_name = json_file.stem
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            cases = data.get("cases", [])
            for case in cases:
                case_id = case.get("id", "UNKNOWN")
                query = case.get("query", "")
                difficulty = case.get("difficulty", "UNKNOWN")
                norm = normalize(query)
                groups[norm].append({
                    "id": case_id,
                    "category": category_name,
                    "difficulty": difficulty,
                    "query": query,
                    "tier": tier,
                    "file": str(json_file.relative_to(DATA_ROOT)),
                })

    # Filter to groups with 2+ entries
    duplicates = {k: v for k, v in groups.items() if len(v) >= 2}

    # Sort by group size descending, then by normalized query
    sorted_groups = sorted(duplicates.items(), key=lambda x: (-len(x[1]), x[0]))

    total_affected = 0
    for i, (norm_query, entries) in enumerate(sorted_groups, 1):
        print(f"{'='*90}")
        print(f"DUPLICATE GROUP {i}  ({len(entries)} cases)")
        print(f"Normalized query: \"{norm_query}\"")
        print(f"{'-'*90}")
        for entry in entries:
            print(f"  ID:         {entry['id']}")
            print(f"  Tier:       {entry['tier']}")
            print(f"  Category:   {entry['category']}")
            print(f"  Difficulty: {entry['difficulty']}")
            print(f"  Query:      {entry['query']}")
            print()
        total_affected += len(entries)

    print(f"{'='*90}")
    print(f"SUMMARY")
    print(f"  Total duplicate groups: {len(sorted_groups)}")
    print(f"  Total affected cases:   {total_affected}")
    print(f"{'='*90}")

if __name__ == "__main__":
    main()
