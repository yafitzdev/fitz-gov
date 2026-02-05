# Tiered Evaluation Implementation Plan

> **Version**: 2.0
> **Status**: Planning
> **Created**: 2026-02-04
> **Updated**: 2026-02-05
> **Completed Release**: v1.1.0 (Tiered Structure)
> **Target Release**: v2.0.0
> **Current Phase**: Planning

## Overview

This document covers two milestones:

1. **v1.1.0 (COMPLETE)**: Restructured fitz-gov from a flat 200-case benchmark into a tiered evaluation system (60 tier0 + 160 tier1)
2. **v2.0.0 (PLANNED)**: Address critical gaps identified in the [benchmark evaluation](fitz-gov-2.0.md) including corpus quality, missing subcategories, and new test categories

---

## Motivation

### v1.1.0 (Addressed)

The original benchmark mixed trivially easy cases with genuinely challenging ones:

1. **Ceiling effects**: Sophisticated models scored similarly on easy cases
2. **Unclear failure semantics**: A 75% could mean "fails basics" or "struggles with edge cases"
3. **Wasted evaluation time**: Running 200 cases when 60 could gate the rest

**Solution**: Tiered structure with gating (Tier 0 sanity → Tier 1 core)

### v2.0.0 (To Address)

The [critical evaluation](fitz-gov-2.0.md) identified additional issues:

1. **Corpus quality**: Synthetic documents lack real-world messiness (no tables, code, varied lengths)
2. **Missing subcategories**: Key qualification triggers (hedged sources, population mismatch) absent
3. **Category gaps**: No tests for ambiguous queries, code contexts, or structured data parsing
4. **Domain imbalance**: Business/tech over-represented; legal/sports/consumer under-represented
5. **Over-hedging risk**: Confidence category (30 cases) underweighted vs negative cases (170 cases)

**Solution**: Corpus enhancement, category expansion to 280 cases, new test types

---

## Tier Definitions

### Tier 0: Sanity Check (~60 cases)

**Purpose**: Verify basic epistemic governance capability exists

| Property | Value |
|----------|-------|
| Passing threshold | 95% |
| Failure meaning | Model lacks fundamental governance awareness |
| Evaluation time | ~2 minutes |
| Use case | Gate for Tier 1, CI smoke tests, quick model screening |

**Characteristics of Tier 0 cases**:
- Unambiguous correct answer
- No inference required
- Pattern-matchable by competent models
- Binary signal: "Can you do this at all?"

### Tier 1: Core Benchmark (~160 cases)

**Purpose**: Discriminate between good and excellent models

| Property | Value |
|----------|-------|
| Scoring | Gradient (0-100%) |
| Expected range | 60-90% for production models |
| Evaluation time | ~8 minutes |
| Use case | Primary benchmark score, model comparison |

**Characteristics of Tier 1 cases**:
- Requires inference or nuanced judgment
- Multiple plausible interpretations possible
- Tests edge cases within categories
- Meaningful difficulty gradient (medium → hard)

### Tier 2: Adversarial (Future, ~40 cases)

**Purpose**: Stress test edge cases and identify specific weaknesses

| Property | Value |
|----------|-------|
| Scoring | Informational only |
| Expected range | 40-70% |
| Evaluation time | ~3 minutes |
| Use case | Detailed capability profiling, weakness identification |

**Characteristics of Tier 2 cases**:
- Ambiguous queries with multiple valid interpretations
- Adversarial contexts designed to mislead
- Borderline cases where correct mode is debatable
- Multi-turn scenarios (future)

---

## Case Distribution

### Current State (v0.9.1)

```
Total: 200 cases
├── abstention/     40 cases (12 easy, 14 medium, 14 hard)
├── dispute/        40 cases (12 easy, 14 medium, 14 hard)
├── qualification/  40 cases (10 easy, 15 medium, 15 hard)
├── confidence/     30 cases (10 easy, 10 medium, 10 hard)
├── grounding/      25 cases (8 easy, 10 medium, 7 hard)
└── relevance/      25 cases (8 easy, 9 medium, 8 hard)
```

### Target State (v1.1.0)

```
Total: 280 cases

tier0_sanity/       60 cases (from existing easy cases)
├── abstention/     12 cases
├── dispute/        12 cases
├── qualification/  10 cases
├── confidence/     10 cases
├── grounding/       8 cases
└── relevance/       8 cases

tier1_core/        160 cases (existing medium/hard + new cases)
├── abstention/     30 cases (14 existing + 16 new)
├── dispute/        30 cases (14 existing + 16 new)
├── qualification/  30 cases (15 existing + 15 new)
├── confidence/     30 cases (10 existing + 20 new)
├── grounding/      20 cases (10 existing + 10 new)
└── relevance/      20 cases (10 existing + 10 new)

tier2_adversarial/  40 cases (all new, Phase 2)
├── ambiguous/      10 cases
├── adversarial/    10 cases
├── borderline/     10 cases
└── multi_turn/     10 cases
```

---

## Implementation Phases

### Phase 1: Restructure (Week 1-2)

**Goal**: Move existing cases into tiered structure without content changes

#### Tasks

1. **Create directory structure**
   ```
   data/
   ├── tier0_sanity/
   │   ├── abstention.json
   │   ├── dispute.json
   │   ├── qualification.json
   │   ├── confidence.json
   │   ├── grounding.json
   │   └── relevance.json
   ├── tier1_core/
   │   ├── abstention.json
   │   ├── dispute.json
   │   ├── qualification.json
   │   ├── confidence.json
   │   ├── grounding.json
   │   └── relevance.json
   └── corpus/
       └── documents.jsonl
   ```

2. **Update JSON schema**
   ```json
   {
     "tier": "sanity|core|adversarial",
     "tier_description": "...",
     "passing_threshold": 0.95,  // tier0 only
     "category": "abstention",
     "version": "1.0.0",
     "cases": [...]
   }
   ```

3. **Migrate cases**
   - Move all `difficulty: easy` cases to `tier0_sanity/`
   - Move all `difficulty: medium|hard` cases to `tier1_core/`
   - Update case IDs to include tier prefix (e.g., `t0_abstain_001`)

4. **Update loader**
   - Add `load_tier(tier: str)` function
   - Add `load_cases(tiers: list[str])` parameter
   - Maintain backward compatibility with `load_cases()` returning all

5. **Update evaluator**
   - Add tier-aware evaluation with gating logic
   - Add `evaluate_tiered()` method returning `TieredResult`

#### Deliverables
- [x] New directory structure created
- [x] Cases migrated with updated IDs
- [x] `loader.py` updated with tier support
- [x] `evaluator.py` updated with tiered evaluation
- [x] `models.py` updated with `TieredResult` dataclass
- [x] All existing tests passing

#### Completion Notes (2026-02-05)
- Created `data/tier0_sanity/` with 60 easy cases (6 JSON files)
- Created `data/tier1_core/` with 140 medium/hard cases (6 JSON files)
- Migration script at `scripts/migrate_to_tiers.py`
- Backward compatibility verified: `load_cases()` returns all 200 cases
- New exports: `Tier`, `load_tier()`, `get_tier_dir()`, `get_tier_info()`
- New result types: `Tier0Result`, `Tier1Result`, `TieredResult`
- Gating logic implemented: Tier 1 skipped when Tier 0 fails

---

### Phase 2: Tier 0 Refinement (Week 3)

**Goal**: Ensure Tier 0 cases are truly baseline (no ambiguity, high agreement)

#### Tasks

1. **Audit Tier 0 cases**
   - Review each case for unambiguous correct answer
   - Remove any cases with debatable expected_mode
   - Ensure 95% threshold is meaningful

2. **Case assignment review**

   **Abstention (12 cases)**:
   - Keep: `different_domain` cases (biology/finance mismatch)
   - Move to Tier 1: Any `wrong_entity` cases requiring inference

   **Dispute (12 cases)**:
   - Keep: Binary contradiction cases (success/failure, approved/rejected)
   - Move to Tier 1: `numerical_disagreement` with close values

   **Qualification (10 cases)**:
   - Keep: "Why X?" with only "X happened" pattern
   - Move to Tier 1: Cases with partial causal hints

   **Confidence (10 cases)**:
   - Keep: Direct factual lookups (capital of France, founding year)
   - Move to Tier 1: Multi-step reasoning cases

   **Grounding (8 cases)**:
   - Keep: Obvious hallucination traps (no number → asking for number)
   - Move to Tier 1: Cases with ambiguous forbidden patterns

   **Relevance (8 cases)**:
   - Keep: Complete topic mismatch (pricing asked, features given)
   - Move to Tier 1: Partial answer cases

3. **Update passing threshold logic**
   ```python
   def evaluate_tier0(cases, responses) -> Tier0Result:
       result = evaluate_cases(cases, responses)
       passed = result.accuracy >= 0.95
       return Tier0Result(
           passed=passed,
           accuracy=result.accuracy,
           gate_tier1=passed,
           failure_cases=[c for c in result.cases if not c.passed]
       )
   ```

#### Deliverables
- [x] Tier 0 cases audited and finalized
- [x] Gating logic implemented
- [x] Documentation for Tier 0 semantics

#### Audit Results (2026-02-05)

| Category | Cases | Status | Notes |
|----------|-------|--------|-------|
| Abstention | 12 | ✓ All solid | Pure domain mismatches, unambiguous |
| Dispute | 12 | ✓ All solid | Binary contradictions |
| Qualification | 10 | ✓ All solid | Clear "why/what" pattern mismatches |
| Confidence | 10 | ✓ All solid | Explicit answers in context |
| Grounding | 8 | ✓ All solid | Clear hallucination traps |
| Relevance | 8 | ✓ Fixed | Added missing `forbidden_elements` to 3 cases |

**Fixes Applied:**
- `t0_relevance_easy_006`: Added forbidden_elements for fabricated specs
- `t0_relevance_easy_007`: Added forbidden_elements for fabricated time metrics
- `t0_relevance_easy_008`: Added forbidden_elements + cleaned up required_elements

**Gating Logic Verified:**
- Location: `evaluator.py:244-249`
- Behavior: Tier 1 skipped when gating enabled AND Tier 0 fails
- Tested: Working correctly in Phase 1 verification

---

### Phase 3: Tier 1 Enhancement (Week 4-6)

**Goal**: Add new cases to fill gaps identified in evaluation

#### New Cases to Create

**Abstention (+16 cases)**:
| Subcategory | Count | Description |
|-------------|-------|-------------|
| near_miss_entity | 4 | iPhone 15 Pro asked, iPhone 15 context |
| stale_data | 4 | Context dated 2020 for 2024 question |
| partial_coverage | 4 | 2 of 3 aspects covered |
| scope_mismatch | 4 | City asked, country-level data given |

**Dispute (+16 cases)**:
| Subcategory | Count | Description |
|-------------|-------|-------------|
| implicit_contradiction | 4 | Sources incompatible but not directly conflicting |
| scope_conflict | 4 | General claim vs specific exception |
| confidence_overlap | 4 | Error bars that barely overlap |
| definition_conflict | 4 | Different definitions lead to different answers |

**Qualification (+15 cases)**:
| Subcategory | Count | Description |
|-------------|-------|-------------|
| hedged_source | 4 | "May", "possibly", "suggests" in context |
| source_quality | 3 | Blog post vs peer-reviewed for factual claim |
| population_mismatch | 4 | Study on adults applied to children question |
| temporal_extrapolation | 4 | 2019-2022 data for 2024 prediction |

**Confidence (+20 cases)**:
| Subcategory | Count | Description |
|-------------|-------|-------------|
| multi_source_agreement | 5 | 3+ sources corroborate same fact |
| explicit_recency | 5 | "As of January 2025..." |
| bounded_claim | 5 | Explicit scope/limitations stated |
| authoritative_source | 5 | Official documentation citation |

**Grounding (+10 cases)**:
| Subcategory | Count | Description |
|-------------|-------|-------------|
| entity_blending | 3 | Context about A and B, question about A |
| quote_fabrication | 3 | Temptation to invent CEO quotes |
| statistical_inference | 4 | "Increased significantly" → specific % |

**Relevance (+10 cases)**:
| Subcategory | Count | Description |
|-------------|-------|-------------|
| format_mismatch | 3 | Asked for list, prose available |
| granularity_mismatch | 3 | Asked for specific, general available |
| over_answering | 4 | Provides unrequested information |

#### Deliverables
- [x] New Tier 1 cases created
- [x] Cases reviewed for quality
- [ ] Corpus updated with supporting documents
- [ ] Tests updated for new cases

#### Completion Notes (2026-02-05)

**Original plan estimated 87 new cases but actual migration showed we needed only 20:**

| Category | Before | After | Added |
|----------|--------|-------|-------|
| Abstention | 28 | 30 | +2 |
| Confidence | 20 | 30 | +10 |
| Dispute | 28 | 30 | +2 |
| Grounding | 17 | 20 | +3 |
| Qualification | 30 | 30 | 0 |
| Relevance | 17 | 20 | +3 |
| **Total** | **140** | **160** | **+20** |

**New subcategories added:**
- `multi_source_agreement` (confidence): Multiple independent sources converging
- `explicit_recency` (confidence): Clear effective dates stated
- `bounded_claim` (confidence): Claims with explicit limitations
- `authoritative_source` (confidence): Official documentation cited
- `near_miss_entity` (abstention): Similar but different entities
- `stale_data` (abstention): Outdated information for current questions
- `implicit_contradiction` (dispute): Mathematically incompatible sources
- `definition_conflict` (dispute): Conflicting classification systems
- `entity_blending` (grounding): Attributes from wrong entity
- `quote_fabrication` (grounding): Temptation to invent quotes
- `statistical_inference` (grounding): Qualitative → quantitative trap
- `format_mismatch` (relevance): Requested format not available
- `granularity_mismatch` (relevance): Wrong specificity level

---

### Phase 4: Evaluator & Reporting (Week 7)

**Goal**: Update evaluation output for tiered structure

#### New Result Models

```python
@dataclass
class TieredResult:
    tier0: Tier0Result
    tier1: Tier1Result | None  # None if tier0 failed
    timestamp: datetime
    evaluation_time_seconds: float

@dataclass
class Tier0Result:
    passed: bool
    accuracy: float
    threshold: float  # 0.95
    category_results: dict[str, CategoryResult]
    failure_cases: list[CaseResult]

@dataclass
class Tier1Result:
    overall_accuracy: float
    category_results: dict[str, CategoryResult]
    subcategory_results: dict[str, SubcategoryResult]
    confusion_matrix: ConfusionMatrix
    difficulty_breakdown: dict[str, float]  # medium vs hard
```

#### CLI Output Format

```
fitz-gov Tiered Evaluation
==========================

TIER 0 (Sanity Check): PASSED
  Threshold: 95% | Achieved: 98.3% (59/60)

  By Category:
    Abstention:    12/12 (100.0%)
    Dispute:       11/12 (91.7%)
    Qualification: 10/10 (100.0%)
    Confidence:    10/10 (100.0%)
    Grounding:      8/8  (100.0%)
    Relevance:      8/8  (100.0%)

  Failed Cases (1):
    - t0_dispute_007: Expected DISPUTED, got CONFIDENT

TIER 1 (Core Benchmark): 78.1%

  By Category:
    Abstention:    26/30 (86.7%)
    Dispute:       22/30 (73.3%)
    Qualification: 21/30 (70.0%)
    Confidence:    27/30 (90.0%)
    Grounding:     15/20 (75.0%)
    Relevance:     14/20 (70.0%)

  By Difficulty:
    Medium: 82.5% (66/80)
    Hard:   71.3% (57/80)

  Confusion Matrix:
              ABSTAIN  DISPUTED  QUALIFIED  CONFIDENT
    ABSTAIN      24        1         3          2
    DISPUTED      0       22         6          2
    QUALIFIED     2        3        21          4
    CONFIDENT     0        0         3         27

Summary: Tier 0 PASSED, Tier 1 Score: 78.1%
```

#### Deliverables
- [x] `TieredResult` and related models implemented
- [x] CLI output updated
- [x] JSON export format defined
- [x] Backward-compatible `FitzGovResult` still available

#### Completion Notes (2026-02-05)

**CLI Updates:**
- `stats` command now shows tiered structure with case counts per tier/category
- Added `--verbose` flag for subcategory breakdown

**Output Format:**
- `TieredResult.__str__()` produces formatted output matching planned spec
- Tier 0: shows pass/fail, threshold, accuracy with case counts, by-category breakdown
- Tier 1: shows accuracy, by-category, by-difficulty, confusion matrix
- Gating: correctly shows "Tier 1: Skipped" when Tier 0 fails

**JSON Export:**
- All result classes have `to_dict()` methods
- Full structure serializable via `json.dumps(result.to_dict())`

---

### Phase 5: Documentation & Release (Week 8)

**Goal**: Update all documentation for v1.1.0 release

#### Documentation Updates

1. **README.md**
   - Update quick start for tiered evaluation
   - Add tier explanation section
   - Update example output

2. **docs/evaluation-guide.md** (new)
   - Detailed tier semantics
   - Interpretation guide for scores
   - Common failure patterns

3. **docs/case-design.md** (new)
   - Guidelines for adding new cases
   - Subcategory definitions
   - Quality criteria

4. **CHANGELOG.md**
   - v1.1.0 release notes
   - Breaking changes (if any)
   - Migration guide from v0.9.x

#### Deliverables
- [x] All documentation updated
- [x] CHANGELOG written
- [ ] GitHub release created
- [ ] PyPI package updated

#### Completion Notes (2026-02-05)

**Documentation Updated:**
- `README.md` - Added tiered evaluation section, updated data format, API reference
- `CHANGELOG.md` - Added v1.1.0 release notes with full feature list
- `docs/evaluation-guide.md` - New comprehensive interpretation guide
- `fitz_gov/__init__.py` - Version bumped to 1.1.0

**Remaining:**
- GitHub release (manual step)
- PyPI publish (manual step)

---

# Part 2: v2.0.0 Plan (Benchmark Quality & Coverage)

Based on the [Critical Evaluation](fitz-gov-2.0.md), the following gaps remain after v1.1.0:

## Gaps to Address

### Gap 1: Missing Qualification Subcategories

The evaluation identified these missing scenarios:

| Subcategory | Description | Status |
|-------------|-------------|--------|
| `hedged_source` | Context contains "may", "possibly", "suggests" | **Not added** |
| `source_quality` | Non-authoritative source (blog vs peer-reviewed) | **Not added** |
| `population_mismatch` | Study on group A applied to question about group B | **Not added** |
| `temporal_extrapolation` | 2019 data used for 2024 prediction | **Not added** |

### Gap 2: Corpus Quality Issues

| Issue | Current State | Target |
|-------|---------------|--------|
| Domain balance | business/tech over-represented | Add legal, government, sports, consumer |
| Document style | Synthetic 2-4 sentence prose | Add real-world messiness, varied length |
| Structured data | None | Add tables, JSON, code snippets |
| Noise/errors | None | Add OCR artifacts, incomplete docs |

### Gap 3: Missing Test Categories

| Category | Description | Priority |
|----------|-------------|----------|
| Ambiguous queries | Queries with multiple valid interpretations | High |
| Code as context | Programming docs with code samples | High |
| Structured data parsing | Tables, JSON responses | Medium |
| Metacognitive tests | Model recognizes need for clarification | Medium |
| Multi-turn scenarios | Follow-up question handling | Low (Tier 2) |

### Gap 4: Case Count Targets

The evaluation recommends increasing to 280 total cases:

| Category | v1.1.0 | Target | Delta |
|----------|--------|--------|-------|
| Abstention | 42 (12+30) | 50 | +8 |
| Dispute | 42 (12+30) | 50 | +8 |
| Qualification | 40 (10+30) | 50 | +10 |
| Confidence | 40 (10+30) | 50 | +10 |
| Grounding | 28 (8+20) | 40 | +12 |
| Relevance | 28 (8+20) | 40 | +12 |
| **Total** | **220** | **280** | **+60** |

---

## v2.0 Implementation Phases

### Phase 6: Corpus Enhancement (Week 1-2)

**Goal**: Improve corpus realism and domain balance

#### Tasks

1. **Domain expansion** (+40 documents)
   - Legal/regulatory: 10 documents (contracts, compliance, court decisions)
   - Government: 10 documents (policy statements, public records)
   - Sports: 8 documents (match reports, player stats, league rules)
   - Consumer: 8 documents (product reviews, warranties, user manuals)
   - Industrial: 4 documents (manufacturing specs, safety protocols)

2. **Format variety** (+30 documents)
   - Tables: 10 documents with tabular data
   - JSON/structured: 8 documents with API responses or configs
   - Code samples: 8 documents with programming examples
   - Mixed format: 4 documents combining prose + tables + code

3. **Real-world artifacts** (+20 documents)
   - Longer documents (500+ words): 8
   - Documents with minor OCR errors: 4
   - Incomplete/truncated documents: 4
   - Documents with inconsistent formatting: 4

#### Deliverables
- [ ] 90 new documents added to corpus
- [ ] Domain distribution rebalanced
- [ ] Structured data formats represented
- [ ] Document length variety achieved

---

### Phase 7: Qualification Category Expansion (Week 3)

**Goal**: Add missing qualification subcategories

#### New Cases (+10)

| Subcategory | Count | Example Pattern |
|-------------|-------|-----------------|
| `hedged_source` | 3 | Context: "Results suggest X may improve Y" / Query: "Does X improve Y?" |
| `source_quality` | 2 | Context: Blog post claims fact / Query: Scientific question |
| `population_mismatch` | 3 | Context: Study on adults / Query: Effects on children |
| `temporal_extrapolation` | 2 | Context: 2019-2022 trends / Query: 2025 prediction |

#### Validation Criteria
- Each case must have clear qualification trigger
- Expected_mode must be `QUALIFIED`
- Include `required_elements` that mandate hedge language

#### Deliverables
- [ ] 10 new qualification cases created
- [ ] All cases use realistic corpus documents
- [ ] Two-pass validation configs complete

---

### Phase 8: Grounding & Relevance Expansion (Week 4)

**Goal**: Expand smaller categories to target counts

#### Grounding (+12 cases)

| Subcategory | Count | Description |
|-------------|-------|-------------|
| `code_hallucination` | 3 | Fabricating function names, parameters, or syntax |
| `table_inference` | 3 | Inventing data not in provided table |
| `quote_extension` | 3 | Adding words to partial quotes |
| `temporal_confusion` | 3 | Mixing dates from different events |

#### Relevance (+12 cases)

| Subcategory | Count | Description |
|-------------|-------|-------------|
| `summarization_vs_answer` | 3 | Summarizing context instead of answering question |
| `related_but_different` | 3 | Answering adjacent question |
| `over_answering` | 3 | Providing unrequested additional details |
| `granularity_mismatch` | 3 | General answer for specific question |

#### Deliverables
- [ ] 12 new grounding cases
- [ ] 12 new relevance cases
- [ ] Forbidden/required patterns validated

---

### Phase 9: Abstention & Dispute Expansion (Week 5)

**Goal**: Increase governance categories to 50 cases each

#### Abstention (+8 cases)

| Subcategory | Count | Description |
|-------------|-------|-------------|
| `version_mismatch` | 2 | v2.1 context, v2.0 question |
| `partial_coverage` | 2 | 2 of 3 required aspects present |
| `scope_mismatch` | 2 | Country data for city question |
| `temporal_gap` | 2 | 2021 context, 2024 question with explicit recency need |

#### Dispute (+8 cases)

| Subcategory | Count | Description |
|-------------|-------|-------------|
| `scope_conflict` | 2 | General rule vs specific exception in sources |
| `confidence_interval_overlap` | 2 | 85±5% vs 72±3% |
| `methodology_incompatible` | 2 | Survey vs experimental results |
| `time_context_conflict` | 2 | Same metric, different time periods |

#### Deliverables
- [ ] 8 new abstention cases
- [ ] 8 new dispute cases
- [ ] All governance modes reach 50 cases

---

### Phase 10: Confidence Expansion (Week 6)

**Goal**: Balance positive cases to prevent over-hedging bias

#### Confidence (+10 cases)

| Subcategory | Count | Description |
|-------------|-------|-------------|
| `code_documentation` | 3 | Clear API docs with exact syntax |
| `official_statement` | 2 | Quoted company/government announcement |
| `multi_source_convergence` | 2 | 3+ independent sources agree |
| `explicit_scope` | 3 | Answer bounded by stated conditions |

#### Deliverables
- [ ] 10 new confidence cases
- [ ] All use authoritative corpus documents
- [ ] Category reaches 50 cases

---

### Phase 11: New Test Categories (Week 7-8)

**Goal**: Add missing category types for comprehensive coverage

#### 11.1 Ambiguous Queries (10 cases)

Test model's ability to recognize when clarification is needed:

```json
{
  "id": "t1_ambiguous_001",
  "query": "What's the Apple policy?",
  "contexts": ["Apple Inc. return policy...", "Apple Records licensing..."],
  "expected_mode": "QUALIFIED",
  "evaluation_config": {
    "required_elements": ["clarif", "which Apple"],
    "subcategory": "entity_ambiguity"
  }
}
```

| Subcategory | Count | Pattern |
|-------------|-------|---------|
| `entity_ambiguity` | 3 | Same name, different entities |
| `scope_ambiguity` | 3 | "The project" with multiple projects |
| `temporal_ambiguity` | 2 | "Current" with multiple time contexts |
| `metric_ambiguity` | 2 | "Performance" (speed vs quality vs cost) |

#### 11.2 Code Context Cases (10 cases)

Test handling of programming documentation:

| Subcategory | Count | Pattern |
|-------------|-------|---------|
| `api_confidence` | 3 | Clear function docs → confident answer |
| `code_abstention` | 3 | Wrong language/version context |
| `deprecation_qualification` | 2 | Deprecated API in context |
| `code_grounding` | 2 | Temptation to hallucinate parameters |

#### 11.3 Structured Data Cases (10 cases)

| Subcategory | Count | Pattern |
|-------------|-------|---------|
| `table_extraction` | 4 | Answer in table cell |
| `json_navigation` | 3 | Answer in nested JSON |
| `table_absence` | 3 | Question about missing column |

#### Deliverables
- [ ] 10 ambiguous query cases
- [ ] 10 code context cases
- [ ] 10 structured data cases
- [ ] All integrated into Tier 1

---

### Phase 12: Documentation & Release (Week 9)

**Goal**: v2.0.0 release with comprehensive documentation

#### Documentation Updates

1. **README.md**
   - Update case counts and categories
   - Add corpus description
   - Document new test categories

2. **docs/corpus-guide.md** (new)
   - Corpus structure and domains
   - How to add new documents
   - Format specifications

3. **docs/case-design.md** (update)
   - New subcategory definitions
   - Guidelines for code/structured data cases
   - Ambiguity handling patterns

4. **CHANGELOG.md**
   - v2.0.0 release notes
   - Migration notes from v1.1.0

#### Deliverables
- [ ] All documentation updated
- [ ] CHANGELOG written
- [ ] GitHub release created
- [ ] PyPI package updated

---

## v2.0 Success Criteria

### Phase 6 Complete When:
- [ ] Corpus has 370+ documents (current 288 + 90 new)
- [ ] No domain has >25% representation
- [ ] Structured data formats present

### Phase 7-10 Complete When:
- [ ] Total cases reach 280
- [ ] Distribution: 50/50/50/50/40/40
- [ ] All new subcategories have 2+ cases

### Phase 11 Complete When:
- [ ] 30 new category cases added
- [ ] Code context cases use real programming docs
- [ ] Ambiguous cases have clear evaluation criteria

### Phase 12 Complete When:
- [ ] v2.0.0 released on PyPI
- [ ] All documentation reflects new structure
- [ ] Migration guide complete

---

## v2.0 Timeline Summary

| Phase | Duration | Key Deliverable |
|-------|----------|-----------------|
| Phase 6: Corpus Enhancement | Week 1-2 | 90 new documents, format variety |
| Phase 7: Qualification Expansion | Week 3 | 10 new qualification cases |
| Phase 8: Grounding & Relevance | Week 4 | 24 new cases (12+12) |
| Phase 9: Abstention & Dispute | Week 5 | 16 new cases (8+8) |
| Phase 10: Confidence Expansion | Week 6 | 10 new confidence cases |
| Phase 11: New Test Categories | Week 7-8 | 30 new cases (ambiguous, code, structured) |
| Phase 12: Documentation & Release | Week 9 | v2.0.0 release |

**Total estimated effort**: 9 weeks

---

## v2.0 Case Distribution (Target)

```
Total: 280 cases

tier0_sanity/       60 cases (unchanged from v1.1.0)
├── abstention/     12 cases
├── dispute/        12 cases
├── qualification/  10 cases
├── confidence/     10 cases
├── grounding/       8 cases
└── relevance/       8 cases

tier1_core/        220 cases (was 160, +60 new)
├── abstention/     38 cases (+8)
├── dispute/        38 cases (+8)
├── qualification/  40 cases (+10)
├── confidence/     40 cases (+10)
├── grounding/      32 cases (+12)
├── relevance/      32 cases (+12)
└── new_categories/
    ├── ambiguous/      10 cases (NEW)
    ├── code_context/   10 cases (NEW)
    └── structured/     10 cases (NEW)

tier2_adversarial/  40 cases (future, unchanged)
├── ambiguous/      10 cases
├── adversarial/    10 cases
├── borderline/     10 cases
└── multi_turn/     10 cases
```

---

# Part 1: v1.1.0 Plan (COMPLETE)

*The following documents the completed v1.1.0 implementation.*

---

## File Changes Summary

### New Files
```
data/tier0_sanity/*.json          # 6 files
data/tier1_core/*.json            # 6 files
docs/evaluation-guide.md
docs/case-design.md
fitz_gov/tiered.py                # Tiered evaluation logic
```

### Modified Files
```
fitz_gov/models.py                # Add TieredResult, Tier0Result, Tier1Result
fitz_gov/loader.py                # Add load_tier(), update load_cases()
fitz_gov/evaluator.py             # Add evaluate_tiered()
fitz_gov/cli.py                   # Update output format
README.md
CHANGELOG.md
```

### Deprecated (but kept for compatibility)
```
data/abstention/abstention.json   # Symlink to merged tier0+tier1
data/dispute/dispute.json
data/qualification/qualification.json
data/confidence/confidence.json
data/grounding/grounding.json
data/relevance/relevance.json
```

---

## Success Criteria

### Phase 1 Complete When:
- [x] All 200 existing cases accessible via new tier structure
- [x] `load_cases()` returns same cases as before
- [x] All existing tests pass

**Status: COMPLETE** (2026-02-05)

### Phase 2 Complete When:
- [x] Tier 0 has exactly 60 cases
- [x] All Tier 0 cases have >95% human agreement on expected_mode
- [x] Gating logic works correctly

**Status: COMPLETE** (2026-02-05)

### Phase 3 Complete When:
- [x] New cases added to Tier 1 (20 cases added, reaching 160 total)
- [x] Each category reaches target (30/30/30/30/20/20)
- [ ] Corpus updated with supporting documents

**Status: SUBSTANTIALLY COMPLETE** (2026-02-05) - Corpus update deferred

### Phase 4 Complete When:
- [x] `evaluate_tiered()` returns correct structure
- [x] CLI shows tiered output
- [x] JSON export includes tier information

**Status: COMPLETE** (2026-02-05)

### Phase 5 Complete When:
- [x] All documentation updated
- [ ] v1.1.0 released on PyPI
- [ ] GitHub release published

**Status: DOCUMENTATION COMPLETE** (2026-02-05) - Awaiting release

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Case migration breaks existing users | Medium | High | Maintain backward-compatible `load_cases()` |
| 95% threshold too strict/lenient | Medium | Medium | Analyze results on 3+ models before finalizing |
| New cases don't improve discrimination | Low | Medium | Test on model pairs with known capability differences |
| Scope creep in Phase 3 | High | Medium | Strict case count limits, defer edge cases to Tier 2 |

---

## Open Questions

1. **Tier 2 scope**: Should Tier 2 include multi-turn scenarios or defer to v1.1?
2. **Corpus sharing**: Should tiers share corpus or have tier-specific documents?
3. **Backward compatibility**: How long to support v0.9.x data format?
4. **Threshold tuning**: Should 95% be configurable or fixed?

---

## Appendix: Case Migration Mapping

### Abstention Cases

| Current ID | Tier | New ID | Rationale |
|------------|------|--------|-----------|
| abstain_easy_001 | 0 | t0_abstain_001 | Pure domain mismatch |
| abstain_easy_002 | 0 | t0_abstain_002 | Pure domain mismatch |
| ... | ... | ... | ... |
| abstain_medium_001 | 1 | t1_abstain_001 | Wrong entity requires inference |
| abstain_medium_002 | 1 | t1_abstain_002 | Same domain, wrong condition |
| ... | ... | ... | ... |
| abstain_hard_001 | 1 | t1_abstain_015 | Wrong aspect (effects vs causes) |

*Full mapping to be completed during Phase 1 implementation.*

---

## Timeline Summary

| Phase | Duration | Key Deliverable |
|-------|----------|-----------------|
| Phase 1: Restructure | Week 1-2 | Tiered directory structure, updated loader/evaluator |
| Phase 2: Tier 0 Refinement | Week 3 | Finalized 60 sanity cases with gating |
| Phase 3: Tier 1 Enhancement | Week 4-6 | 87 new discriminative cases |
| Phase 4: Evaluator & Reporting | Week 7 | Tiered CLI output and JSON export |
| Phase 5: Documentation & Release | Week 8 | v1.1.0 release |

**Total estimated effort**: 8 weeks
