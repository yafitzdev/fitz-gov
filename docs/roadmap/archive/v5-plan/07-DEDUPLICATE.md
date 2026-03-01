# Phase 7: Deduplicate Queries

**Priority:** P1 (score validity)
**Scope:** Remove ~27 duplicate cases
**Files modified:** `data/tier1_core/abstention.json`, `data/tier1_core/dispute.json`, `data/tier1_core/trustworthy_direct.json`, `data/tier1_core/trustworthy_hedged.json`

## Problem

27 cases share exact duplicate query text with another case in the same category:

```
abstention:        5 duplicate queries (6 extra cases)
dispute:           9 duplicate queries (9 extra cases)
trustworthy_direct: 6 duplicate queries (6 extra cases)
trustworthy_hedged: 5 duplicate queries (6 extra cases)
```

Grounding and relevance have no duplicates (they were generated with unique queries).

### Why This Matters

- Duplicate queries inflate per-category scores (model gets credit twice for same skill)
- They reduce effective test coverage (27 cases that add no discriminative value)
- They may indicate copy-paste errors during case generation

## Solution

For each duplicate pair/group, keep the case with:
1. Richer contexts (more words)
2. More complete metadata
3. The original (lower ID number, as it was created first)

Remove the duplicate(s).

## Implementation

### Step 1: Write deduplication script
`scripts/deduplicate_queries.py`

```python
#!/usr/bin/env python3
"""Find and remove duplicate queries within each category."""

import json
from pathlib import Path
from collections import defaultdict

def deduplicate_file(filepath):
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    cases = data["cases"]
    query_groups = defaultdict(list)
    for case in cases:
        query_groups[case["query"].strip().lower()].append(case)

    keep = []
    removed = []
    for query, group in query_groups.items():
        if len(group) == 1:
            keep.append(group[0])
        else:
            # Sort by: context richness (total words), then by ID (lower = original)
            group.sort(key=lambda c: (
                -sum(len(ctx.split()) for ctx in c.get("contexts", [])),
                c["id"],
            ))
            keep.append(group[0])  # keep the best
            removed.extend(group[1:])  # remove the rest

    if removed:
        data["cases"] = keep
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")

    return removed

def main():
    total_removed = 0
    for filepath in sorted(Path("data/tier1_core").glob("*.json")):
        removed = deduplicate_file(filepath)
        if removed:
            ids = [c["id"] for c in removed]
            print(f"  {filepath.stem}: removed {len(removed)} duplicates: {ids}")
            total_removed += len(removed)
    print(f"\nTotal removed: {total_removed}")

if __name__ == "__main__":
    main()
```

### Step 2: Run and validate
```bash
python scripts/deduplicate_queries.py
python -m fitz_gov.cli validate --data-dir data
```

### Step 3: Update corpus and mappings
Remove any query_mappings entries that reference removed case IDs.

### Step 4: Add deduplication check to validate.py
Add a check in `check_quality()` or `validate_and_clean()` that flags duplicate
queries within the same category file, so they can't be reintroduced.

## Validation Criteria

- Zero duplicate queries within any category file
- All remaining cases still have valid structure
- No orphaned query_mappings entries
- Total case count decreases by exactly the number of removed duplicates
- No case ID is referenced by another case (no broken dependencies)

## Estimated Scope

- Script: ~30 minutes
- Validation + cleanup: ~30 minutes
