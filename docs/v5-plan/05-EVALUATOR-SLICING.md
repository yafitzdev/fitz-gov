# Phase 5: Evaluator Slicing Support

**Priority:** P1 (make classification fields useful)
**Scope:** Code changes to evaluator, models, and CLI
**Files modified:** `fitz_gov/evaluator.py`, `fitz_gov/models.py`, `fitz_gov/cli.py`

## Problem

v4.1 added 6 classification fields to every case (domain, query_type, source_type,
context_count, reasoning_type, evidence_pattern). But the evaluator, result models,
and CLI don't use them:

- `FitzGovResult` only reports per-category accuracy
- `Tier1Result` only adds difficulty breakdown
- CLI `stats` only shows category counts and difficulty
- No way to answer: "What's my model's accuracy on medical causal questions?"

The fields exist in the data but provide zero evaluation value.

## Solution

### 1. Add slice breakdowns to result models

**`fitz_gov/models.py`** — extend `Tier1Result`:

```python
@dataclass
class Tier1Result:
    accuracy: float
    category_results: dict[str, FitzGovCategoryResult]
    confusion_matrix: FitzGovConfusionMatrix
    difficulty_breakdown: dict[str, float]  # existing
    num_cases: int

    # NEW: classification breakdowns
    domain_breakdown: dict[str, float] = field(default_factory=dict)
    query_type_breakdown: dict[str, float] = field(default_factory=dict)
    source_type_breakdown: dict[str, float] = field(default_factory=dict)
    reasoning_type_breakdown: dict[str, float] = field(default_factory=dict)
    evidence_pattern_breakdown: dict[str, float] = field(default_factory=dict)
```

Each breakdown is `{value: accuracy}` where accuracy is pass_count / total_count
for that slice.

Update `to_dict()` and `__str__()` to include the new breakdowns.

### 2. Compute breakdowns in evaluator

**`fitz_gov/evaluator.py`** — extend `_evaluate_tier1()`:

After computing all case results, group by each classification dimension:

```python
def _evaluate_tier1(self, cases, responses, modes):
    # ... existing evaluation logic ...

    # Compute classification breakdowns
    domain_results = defaultdict(lambda: {"passed": 0, "total": 0})
    query_type_results = defaultdict(lambda: {"passed": 0, "total": 0})
    # ... same for source_type, reasoning_type, evidence_pattern

    for case, result in zip(cases, case_results):
        for dim, results_dict in [
            ("domain", domain_results),
            ("query_type", query_type_results),
            # ...
        ]:
            key = getattr(case, dim, "") or "unknown"
            results_dict[key]["total"] += 1
            if result.passed:
                results_dict[key]["passed"] += 1

    domain_breakdown = {
        k: v["passed"] / v["total"]
        for k, v in domain_results.items()
        if v["total"] > 0
    }
    # ... same for others

    return Tier1Result(
        ...,
        domain_breakdown=domain_breakdown,
        query_type_breakdown=query_type_breakdown,
        source_type_breakdown=source_type_breakdown,
        reasoning_type_breakdown=reasoning_type_breakdown,
        evidence_pattern_breakdown=evidence_pattern_breakdown,
    )
```

### 3. Add breakdown display to CLI stats

**`fitz_gov/cli.py`** — extend `cmd_stats()`:

Add `--breakdown` flag that shows classification distributions:

```
$ fitz-gov stats --data-dir data --breakdown

Tier 1 Core (1,679 cases):
  ...existing output...

  Domain Distribution:
    technology      531 (31.6%)
    medicine        183 (10.9%)
    finance         180 (10.7%)
    ...

  Query Type Distribution:
    what            779 (46.4%)
    how             264 (15.7%)
    ...

  Source Type:
    single         1,537 (91.5%)
    multi_source     142 (8.5%)

  Reasoning Type:
    factual        1,009 (60.1%)
    evaluative       320 (19.1%)
    ...

  Evidence Pattern:
    direct           723 (43.1%)
    absent           313 (18.6%)
    ...
```

### 4. Add slicing to result display

When evaluation results are printed, show breakdowns if verbose:

```
Tier 1 Score: 72.3%
  By Category:
    abstention: 85.2%
    dispute: 68.4%
    ...
  By Domain (top 5 / bottom 5):
    law: 82.1%
    education: 79.3%
    ...
    social_media: 58.2%
    history: 55.8%
  By Query Type:
    is: 78.4%
    what: 73.1%
    ...
    why: 61.2%
```

## Implementation

### Step 1: Update models.py
- Add 5 new `dict[str, float]` fields to `Tier1Result`
- Update `to_dict()` and `__str__()` methods
- Update `FitzGovResult` similarly (for flat evaluation)

### Step 2: Update evaluator.py
- Add breakdown computation in `_evaluate_tier1()`
- Add breakdown computation in `evaluate_all()` for flat mode
- Both use the same grouping logic — extract to helper method

### Step 3: Update cli.py
- Add `--breakdown` flag to stats command
- Display classification distributions
- Sorted by count descending

### Step 4: Update tests
- Add tests for breakdown computation
- Add tests for edge cases (unknown domain, empty slice)

## Validation Criteria

- `evaluate_all()` result includes all 5 breakdowns
- `evaluate_tiered()` tier1 result includes all 5 breakdowns
- CLI `--breakdown` shows all dimensions
- Breakdowns sum to overall accuracy (weighted by case count)
- Empty slices (0 cases) are omitted

## Estimated Scope

- models.py changes: ~30 minutes
- evaluator.py changes: ~1 hour
- cli.py changes: ~30 minutes
- Tests: ~30 minutes
- Total: ~2.5 hours
