# Phase 4: Add Medium-Difficulty Cases

**Priority:** P1 (quality)
**Scope:** ~300 new cases + reclassify some existing
**Files modified:** All 6 `data/tier1_core/*.json` files

## Problem

Tier 1 difficulty distribution is severely skewed:

```
Category              Hard    Medium  % Medium
─────────────────────────────────────────────
abstention            355      32      8.3%
dispute               314      32      9.2%
grounding             190      10      5.0%
relevance             193       9      4.5%
trustworthy_direct    168      46     21.5%
trustworthy_hedged    313      17      5.2%
─────────────────────────────────────────────
TOTAL                1,533    146      8.7%
```

Target: ~30% medium / ~70% hard overall. This requires adding ~450 medium cases
or reclassifying ~300 existing hard cases to medium + adding ~150 new medium cases.

### Why This Matters

- **Discrimination**: A benchmark with 91% hard cases only tests the ceiling. It cannot
  distinguish between a 60th-percentile model and an 80th-percentile model.
- **Diagnostic value**: Medium cases help identify which *specific* capabilities a model
  has mastered vs still learning.
- **Score distribution**: With only hard cases, scores cluster near 50% (random) to 70%
  (good). Medium cases spread the distribution.

## Solution

Two-pronged approach:
1. Reclassify ~150 existing hard cases as medium (where the context makes the answer
   more accessible)
2. Generate ~150 new explicitly medium cases

### Reclassification criteria (hard -> medium)

A case should be medium if:
- The context directly contains the answer within the first 2 sentences
- The governance signal is explicit (e.g., "the sources disagree" stated plainly)
- The forbidden_claims/required_elements are about obvious facts (not subtle inference)
- The query is a simple factual question (what/is) rather than analytical (why/how/compare)

### New medium case design principles

Medium cases should be:
- Answerable by a competent model 80-90% of the time
- Still testing the right governance behavior (not trivial)
- Clearly easier than hard cases in the same subcategory

**Medium vs Hard example (abstention, wrong_entity):**

Hard: Context about CompanyA's cloud migration costs. Query asks about CompanyB's
marketing budget. No mention of CompanyB or marketing anywhere. Must abstain.

Medium: Context about CompanyA's Q3 2024 revenue. Query asks about CompanyA's Q4 2024
revenue. The entity matches but the time period doesn't. Must abstain. (Easier because
the entity match may tempt a hard-case model but the temporal gap is obvious.)

## Implementation

### Step 1: Reclassification script
`scripts/reclassify_difficulty.py`

For each category, identify cases where:
- All context passages are < 100 words AND directly state the answer/signal
- The query uses simple question form (what, is)
- Subcategory is common (>10 cases — don't reduce sparse subcategories)

Reclassify up to these targets:

| Category | Current Medium | Add Medium (reclass) | Add Medium (new) | Target Medium |
|----------|---------------|---------------------|------------------|---------------|
| abstention | 32 | 40 | 40 | 112 (29%) |
| dispute | 32 | 35 | 35 | 102 (27%) |
| grounding | 10 | 20 | 30 | 60 (26%) |
| relevance | 9 | 20 | 30 | 59 (25%) |
| trustworthy_direct | 46 | 10 | 10 | 66 (28%) |
| trustworthy_hedged | 17 | 35 | 35 | 87 (25%) |
| **Total** | **146** | **160** | **180** | **~486 (26%)** |

### Step 2: New medium case generator
`scripts/generate_medium_cases.py`

Generate 180 new medium cases across all 6 categories. Each new case gets:
- `difficulty: "medium"`
- ID format: `t1_{category}_medium_{NNN}` continuing from the last medium ID
- All 6 classification fields
- `category` and `evaluation_config` fields (from Phase 2)
- Rich contexts (learned from Phase 1)

Distribution of new medium cases across categories:
- abstention: 40 new (spread across top 8 subcategories)
- dispute: 35 new
- grounding: 30 new (with rich contexts, 80-150 words each)
- relevance: 30 new (with rich contexts)
- trustworthy_direct: 10 new
- trustworthy_hedged: 35 new

### Step 3: Validate
```bash
python -m fitz_gov.cli validate --data-dir data
python -m fitz_gov.cli stats --data-dir data
```

## Validation Criteria

- Total tier1 cases: ~1,859 (1,679 + 180 new)
- Medium share: 25-30% overall
- Every category has >= 20% medium cases
- No duplicate IDs
- All new cases have all required fields
- Difficulty breakdown in `fitz-gov stats` output looks reasonable

## Estimated Scope

- Reclassification script: ~1 hour
- New medium case generator: ~2 hours
- Validation: ~30 minutes
