# Phase 6: Expand Sparse Subcategories

**Priority:** P1 (per-subcategory reliability)
**Scope:** ~50 new cases
**Files modified:** `data/tier1_core/grounding.json`, `data/tier1_core/relevance.json`, `data/tier1_core/trustworthy_hedged.json`

## Problem

15 subcategories across 4 categories have <= 2 cases. Per-subcategory metrics
are meaningless at n=1-2.

### Sparse subcategories

**Grounding (5 subcats):**
```
location_hallucination:    1 case  ← singleton
code_grounding:            2 cases
date_hallucination:        2 cases
medical_hallucination:     2 cases
technical_hallucination:   2 cases
```

**Relevance (5 subcats):**
```
feature_dump:              1 case  ← singleton
instruction_only:          1 case  ← singleton
metric_avoidance:          1 case  ← singleton
status_dump:               2 cases
symptom_only:              2 cases
```

**Governance (5 subcats):**
```
short_query (abstention):  2 cases
short_query (dispute):     2 cases
short_query (trust_direct):2 cases
short_query (trust_hedged):2 cases  (present as implicit, via query length)
different_framing:         1 case  ← singleton (trustworthy_hedged)
```

## Solution

Expand each sparse subcategory to at least 5 cases. This requires ~35 new cases
for grounding/relevance and ~15 for governance categories.

### New cases per subcategory

| Category | Subcategory | Current | Add | Total |
|----------|------------|---------|-----|-------|
| grounding | location_hallucination | 1 | 4 | 5 |
| grounding | code_grounding | 2 | 3 | 5 |
| grounding | date_hallucination | 2 | 3 | 5 |
| grounding | medical_hallucination | 2 | 3 | 5 |
| grounding | technical_hallucination | 2 | 3 | 5 |
| relevance | feature_dump | 1 | 4 | 5 |
| relevance | instruction_only | 1 | 4 | 5 |
| relevance | metric_avoidance | 1 | 4 | 5 |
| relevance | status_dump | 2 | 3 | 5 |
| relevance | symptom_only | 2 | 3 | 5 |
| trustworthy_hedged | different_framing | 1 | 4 | 5 |
| **Total** | | | **~38** | |

The governance `short_query` subcategories (2 each in 4 files) can be expanded to 5
each by adding 3 per file = 12 more cases. But these are less critical since short_query
is a cross-cutting concern, not a unique subcategory. Consider merging them into the
parent subcategory instead.

**Decision:** Expand grounding/relevance/trustworthy_hedged sparse subcats (+38 cases).
Leave governance `short_query` at 2 each — these are edge cases, not core subcategories.

## Implementation

### Step 1: Write expansion script
`scripts/expand_sparse_subcategories.py`

For each sparse subcategory, generate new cases following the same pattern as
existing cases in that subcategory but with different domains and query types.

**Case design guidelines per subcategory:**

**Grounding subcats:**
- `location_hallucination`: Contexts about events/organizations without specific locations.
  Forbidden: invented city/country names. Domains: spread across 4 different domains.
- `code_grounding`: Contexts about software tools with general descriptions.
  Forbidden: invented API names, method signatures, config options.
- `date_hallucination`: Contexts with vague temporal references ("recently", "last year").
  Forbidden: specific dates not in context.
- `medical_hallucination`: Contexts about treatments/conditions without specific dosages.
  Forbidden: invented dosages, frequencies, duration.
- `technical_hallucination`: Contexts about technology with general capabilities.
  Forbidden: specific version numbers, performance figures.

**Relevance subcats:**
- `feature_dump`: Query asks for a specific feature. Context lists many features.
  Required: the specific asked feature or acknowledgment it's not listed.
- `instruction_only`: Query asks for an explanation. Context only gives instructions.
  Required: acknowledgment that explanation (not just steps) was requested.
- `metric_avoidance`: Query asks for a specific metric. Context discusses qualitatively.
  Required: the metric name or acknowledgment it's not quantified.
- `status_dump`: Query asks about a specific aspect. Context dumps full status report.
  Required: the specific aspect, not general status.
- `symptom_only`: Query asks about cause. Context only describes symptoms.
  Required: acknowledgment that cause is not identified.

### Step 2: All new cases must have:
- Rich contexts (80+ words) — learned from Phase 1
- All classification fields
- `category` and `evaluation_config` fields
- Mix of difficulty (some medium, some hard)
- Different domains from existing cases in the subcategory

### Step 3: Validate
```bash
python -m fitz_gov.cli validate --data-dir data
# Verify no subcategory has < 5 cases
python -c "
import json
from pathlib import Path
from collections import Counter
for fp in sorted(Path('data/tier1_core').glob('*.json')):
    with open(fp, encoding='utf-8') as f:
        data = json.load(f)
    subcats = Counter(c.get('subcategory') for c in data['cases'])
    sparse = {k: v for k, v in subcats.items() if v < 5}
    if sparse:
        print(f'{fp.stem}: {sparse}')
"
```

## Validation Criteria

- Zero subcategories with < 5 cases (across grounding, relevance, trustworthy_hedged)
- All new cases have rich contexts (>= 80 words per context)
- No duplicate IDs
- All classification and structural fields present

## Estimated Scope

- Script: ~1 hour
- Validation: ~15 minutes
