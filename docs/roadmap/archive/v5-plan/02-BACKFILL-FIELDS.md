# Phase 2: Backfill Structural Fields

**Priority:** P0 (blocks release)
**Scope:** 1,679 tier1 cases + 60 tier0 cases
**Files modified:** All 12 data JSON files, `scripts/backfill_structural_fields.py`

## Problem

### Missing `category` field (827 / 1,679 = 49%)

Cases lack an explicit `category` field in the JSON. The loader infers it from the
filename, which is fragile — if cases are exported, moved between files, or consumed
by external tools, category information is lost.

Breakdown of missing cases:
```
abstention:        151 / 387 missing (39%)
dispute:           143 / 346 missing (41%)
grounding:         200 / 200 missing (100%)  ← all new cases
relevance:         202 / 202 missing (100%)  ← all new cases
trustworthy_direct: 68 / 214 missing (32%)
trustworthy_hedged: 63 / 330 missing (19%)
```

### Missing `evaluation_config` field (1,679 / 1,679 = 100%)

No tier1 case has an `evaluation_config` field. The evaluator falls back to defaults:
- `use_regex: true`
- `case_insensitive: true`
- `allowed_phrases: []`
- `min_required: 1`

This means:
- Grounding evaluation always uses case-insensitive regex with no allowed phrases
- Relevance evaluation always uses `min_required=1` (any 1 of N elements = pass)
- No case can override these defaults

For a v5 release, every case should have explicit evaluation configuration so behavior
is documented and reproducible.

## Solution

Write `scripts/backfill_structural_fields.py` that adds both fields to every case.

### `category` field

Set to the filename stem for each file:
```python
CATEGORY_MAP = {
    "abstention": "abstention",
    "dispute": "dispute",
    "grounding": "grounding",
    "relevance": "relevance",
    "trustworthy_direct": "trustworthy_direct",
    "trustworthy_hedged": "trustworthy_hedged",
}
```

### `evaluation_config` field

Set based on category and subcategory:

**Governance categories** (abstention, dispute, trustworthy_direct, trustworthy_hedged):
```json
{
  "evaluation_config": {
    "mode": "governance",
    "check_mode_match": true
  }
}
```
These cases are evaluated purely on whether `actual_mode == expected_mode`.

**Grounding cases:**
```json
{
  "evaluation_config": {
    "mode": "answer_quality",
    "use_regex": true,
    "case_insensitive": true,
    "allowed_phrases": []
  }
}
```
Where `allowed_phrases` should be populated per-case for patterns that look like
forbidden_claims but are actually in the context. This requires scanning each case's
contexts against its forbidden_claims to find legitimate matches.

**Relevance cases:**
```json
{
  "evaluation_config": {
    "mode": "answer_quality",
    "use_regex": false,
    "case_insensitive": true,
    "min_required": 1
  }
}
```
Where `min_required` should be:
- `1` for cases where required_elements are alternatives ("deadline" OR "not specified")
- `2` for cases where multiple distinct aspects must be addressed

## Implementation

### Step 1: Write the backfill script

```python
#!/usr/bin/env python3
"""Backfill category and evaluation_config on all cases."""

import json
import re
from pathlib import Path

def compute_allowed_phrases(case):
    """Find forbidden_claims patterns that match content in contexts."""
    allowed = []
    contexts_text = " ".join(case.get("contexts", []))
    for pattern in case.get("forbidden_claims", []):
        try:
            matches = re.findall(pattern, contexts_text, re.IGNORECASE)
            if matches:
                allowed.extend(m if isinstance(m, str) else m[0] for m in matches)
        except re.error:
            pass
    return list(set(allowed))

def backfill_file(filepath, category):
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    updated = 0
    for case in data["cases"]:
        changed = False

        # Add category
        if case.get("category") != category:
            case["category"] = category
            changed = True

        # Add evaluation_config
        if "evaluation_config" not in case:
            if category in ("grounding",):
                allowed = compute_allowed_phrases(case)
                case["evaluation_config"] = {
                    "mode": "answer_quality",
                    "use_regex": True,
                    "case_insensitive": True,
                    "allowed_phrases": allowed,
                }
            elif category in ("relevance",):
                case["evaluation_config"] = {
                    "mode": "answer_quality",
                    "use_regex": False,
                    "case_insensitive": True,
                    "min_required": 1,
                }
            else:
                case["evaluation_config"] = {
                    "mode": "governance",
                    "check_mode_match": True,
                }
            changed = True

        if changed:
            updated += 1

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return updated

def main():
    for tier_dir in ["tier0_sanity", "tier1_core"]:
        for filepath in sorted(Path(f"data/{tier_dir}").glob("*.json")):
            category = filepath.stem
            count = backfill_file(filepath, category)
            print(f"  {tier_dir}/{filepath.name}: {count} cases updated")

if __name__ == "__main__":
    main()
```

### Step 2: Run and validate
```bash
python scripts/backfill_structural_fields.py
python -m fitz_gov.cli validate --data-dir data
```

### Step 3: Verify
```python
# Every case should now have:
assert all(case.get("category") for case in all_cases)
assert all(case.get("evaluation_config") for case in all_cases)
```

## Validation Criteria

- 100% of cases have `category` field matching filename stem
- 100% of cases have `evaluation_config` with valid `mode` value
- Grounding cases have `use_regex: true` and `allowed_phrases` list
- Relevance cases have `min_required` integer
- Governance cases have `check_mode_match: true`
- JSON files still parse correctly
- No case IDs changed

## Estimated Scope

- Script: ~30 minutes
- Run + validate: ~15 minutes
