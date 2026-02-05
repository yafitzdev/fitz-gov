# fitz-gov v2.0 Roadmap: Test Case Expansion

> **Version**: 2.0
> **Status**: In Progress
> **Created**: 2026-02-05
> **Target Release**: v2.0.0
> **Current Phase**: Phase 7 - Documentation & Release

## Overview

Expand fitz-gov from 220 cases to 280 cases by addressing gaps identified in the v1.1.0 benchmark evaluation. Focus areas: qualification subcategories, corpus quality, and new test categories (code context, ambiguous queries, structured data).

---

## Current State (v1.1.0)

| Tier | Category | Cases | Subcategories |
|------|----------|-------|---------------|
| Tier 0 | Abstention | 12 | different_domain |
| Tier 0 | Dispute | 12 | direct_contradiction |
| Tier 0 | Qualification | 10 | causal_without_evidence, prediction_insufficient_data |
| Tier 0 | Confidence | 10 | direct_factual, temporal_explicit, definition_provided |
| Tier 0 | Grounding | 8 | numerical/name/date/technical/medical/location hallucination |
| Tier 0 | Relevance | 8 | feature_dump, metric_avoidance, status_dump |
| **Tier 0 Total** | | **60** | |
| Tier 1 | Abstention | 30 | wrong_entity, wrong_time_period, decoy_keywords, wrong_aspect, near_miss_entity, stale_data |
| Tier 1 | Dispute | 30 | numerical_disagreement, conditional_conflict, methodological_conflict, implicit_contradiction, definition_conflict |
| Tier 1 | Qualification | 30 | correlation_causation, small_sample, incomplete_evidence, attribution_error |
| Tier 1 | Confidence | 30 | multi_source_agreement, explicit_recency, bounded_claim, authoritative_source |
| Tier 1 | Grounding | 20 | entity_blending, quote_fabrication, statistical_inference |
| Tier 1 | Relevance | 20 | partial_answer, wrong_entity_focus, format_mismatch, granularity_mismatch |
| **Tier 1 Total** | | **160** | |
| **Grand Total** | | **220** | |

---

## Gaps to Address

### Gap 1: Missing Qualification Subcategories

| Subcategory | Description | Current | Target |
|-------------|-------------|---------|--------|
| `hedged_source` | Context contains "may", "possibly", "suggests" | 0 | 3 |
| `source_quality` | Non-authoritative source (blog vs peer-reviewed) | 0 | 2 |
| `population_mismatch` | Study on group A, question about group B | 0 | 3 |
| `temporal_extrapolation` | Historical data for future prediction | 0 | 2 |

### Gap 2: Corpus Quality

| Issue | Current | Target |
|-------|---------|--------|
| Documents with tables | 0 | 40 |
| Documents with JSON/structured data | 0 | 20 |
| Documents with code samples | 0 | 15 |
| Legal/regulatory documents | 2 | 12 |
| Sports documents | 1 | 9 |
| Longer documents (500+ words) | 0 | 20 |

### Gap 3: Missing Test Categories

| Category | Description | Cases Needed |
|----------|-------------|--------------|
| Code context | Programming docs with code samples | 10 |
| Ambiguous queries | Multiple valid interpretations | 10 |
| Structured data | Tables, JSON in context | 10 |

### Gap 4: Category Balance

| Category | Current | Target | Delta |
|----------|---------|--------|-------|
| Abstention | 42 | 50 | +8 |
| Dispute | 42 | 50 | +8 |
| Qualification | 40 | 50 | +10 |
| Confidence | 40 | 50 | +10 |
| Grounding | 28 | 40 | +12 |
| Relevance | 28 | 40 | +12 |
| **Total** | **220** | **280** | **+60** |

---

## Implementation Phases

### Phase 1: Corpus Enhancement (Week 1-2) ✅ COMPLETE

**Goal**: Add 90 new documents with format variety and domain balance

#### Tasks

1. **Structured data documents** (+40)
   - Financial tables: 15 documents
   - Product spec sheets: 10 documents
   - API response examples (JSON): 15 documents

2. **Code documentation** (+15)
   - Python function docs with signatures: 5
   - REST API endpoint docs: 5
   - Configuration file examples: 5

3. **Domain expansion** (+20)
   - Legal/regulatory: 10 documents
   - Sports: 8 documents
   - Consumer products: 2 documents

4. **Longer documents** (+15)
   - 500-1000 word documents: 15

#### Deliverables
- [x] 90 new documents in `data/corpus/documents.jsonl` ✓ (288 → 378 total)
- [x] Domain distribution rebalanced ✓ (legal: 12, sports: 9, consumer: 3)
- [x] `data/corpus/manifest.json` updated ✓ (added format_distribution)

---

### Phase 2: Qualification Expansion (Week 3) ✅ COMPLETE

**Goal**: Add 10 new qualification cases with missing subcategories

#### New Cases

| ID | Subcategory | Query Pattern | Context Pattern |
|----|-------------|---------------|-----------------|
| t1_qualify_hard_016 | hedged_source | "Does X improve Y?" | "Results suggest X may improve Y" |
| t1_qualify_hard_017 | hedged_source | "Is X effective?" | "Preliminary findings indicate X could be effective" |
| t1_qualify_hard_018 | hedged_source | "Will X happen?" | "Experts believe X is likely" |
| t1_qualify_hard_019 | source_quality | "What causes X?" | Blog post claiming causal mechanism |
| t1_qualify_hard_020 | source_quality | "Is X safe?" | Social media post about safety |
| t1_qualify_hard_021 | population_mismatch | "Effect on children?" | Study conducted on adults only |
| t1_qualify_hard_022 | population_mismatch | "Works for enterprise?" | Case study from startup |
| t1_qualify_hard_023 | population_mismatch | "Effective in US?" | Study from different country |
| t1_qualify_hard_024 | temporal_extrapolation | "2025 prediction?" | 2019-2022 trend data |
| t1_qualify_hard_025 | temporal_extrapolation | "Current market size?" | 3-year-old market report |

#### Deliverables
- [x] 10 new cases in `data/tier1_core/qualification.json` ✓ (30 → 40 total)
- [x] Required corpus documents added ✓ (contexts self-contained)
- [x] All cases have evaluation_config ✓ (follows existing case format)

---

### Phase 3: Grounding & Relevance Expansion (Week 4) ✅ COMPLETE

**Goal**: Add 24 new cases (12 grounding + 12 relevance)

#### Grounding Cases (+12)

| Subcategory | Count | Description |
|-------------|-------|-------------|
| `code_hallucination` | 3 | Fabricating function parameters, return types |
| `table_inference` | 3 | Inventing data not in provided table |
| `quote_extension` | 3 | Adding words to partial quotes |
| `temporal_confusion` | 3 | Mixing dates from different events |

#### Relevance Cases (+12)

| Subcategory | Count | Description |
|-------------|-------|-------------|
| `summarization_vs_answer` | 3 | Summarizing instead of answering |
| `related_but_different` | 3 | Answering adjacent question |
| `over_answering` | 3 | Providing unrequested details |
| `prerequisite_missing` | 3 | Answer requires unstated context |

#### Deliverables
- [x] 12 new grounding cases ✓ (20 → 32 total)
- [x] 12 new relevance cases ✓ (20 → 32 total)
- [x] forbidden_claims patterns for all ✓

---

### Phase 4: Abstention & Dispute Expansion (Week 5) ✅ COMPLETE

**Goal**: Add 16 new cases (8 abstention + 8 dispute)

#### Abstention Cases (+8)

| Subcategory | Count | Description |
|-------------|-------|-------------|
| `version_mismatch` | 2 | v2.1 context, v2.0 question |
| `partial_coverage` | 2 | 2 of 3 required aspects present |
| `scope_mismatch` | 2 | Country data for city question |
| `temporal_gap` | 2 | Context too old for "current" question |

#### Dispute Cases (+8)

| Subcategory | Count | Description |
|-------------|-------|-------------|
| `confidence_interval_overlap` | 2 | 85±5% vs 72±3% |
| `scope_conflict` | 2 | General rule vs specific exception |
| `methodology_incompatible` | 2 | Survey vs experimental results |
| `time_context_conflict` | 2 | Same metric, different periods |

#### Deliverables
- [x] 8 new abstention cases ✓ (30 → 38 total)
- [x] 8 new dispute cases ✓ (30 → 38 total)

---

### Phase 5: Confidence Expansion (Week 6) ✅ COMPLETE

**Goal**: Add 10 new confidence cases to balance positive/negative ratio

#### New Cases (+10)

| Subcategory | Count | Description |
|-------------|-------|-------------|
| `code_documentation` | 3 | Clear API docs with exact syntax |
| `official_statement` | 2 | Quoted company announcement |
| `regulatory_specification` | 2 | Explicit legal requirement |
| `multi_source_convergence` | 3 | 3+ independent sources agree |

#### Deliverables
- [x] 10 new confidence cases ✓ (t1_confident_hard_021-030)
- [x] All use authoritative corpus documents ✓

---

### Phase 6: New Test Categories (Week 7-8) ✅ COMPLETE

**Goal**: Add 30 new cases in new categories

#### 6.1 Code Context Cases (10)

| Subcategory | Count | Expected Mode | Description |
|-------------|-------|---------------|-------------|
| `api_confidence` | 3 | CONFIDENT | Clear function docs → confident answer |
| `code_abstention` | 3 | ABSTAIN | Wrong language/version context |
| `deprecation_qualification` | 2 | QUALIFIED | Deprecated API in context |
| `code_grounding` | 2 | QUALIFIED | Temptation to hallucinate parameters |

#### 6.2 Ambiguous Query Cases (10)

| Subcategory | Count | Expected Mode | Description |
|-------------|-------|---------------|-------------|
| `entity_ambiguity` | 3 | QUALIFIED | "Apple" - company or records? |
| `scope_ambiguity` | 3 | QUALIFIED | "The project" with multiple projects |
| `temporal_ambiguity` | 2 | QUALIFIED | "Current" with multiple time contexts |
| `metric_ambiguity` | 2 | QUALIFIED | "Performance" - speed, quality, or cost? |

#### 6.3 Structured Data Cases (10)

| Subcategory | Count | Expected Mode | Description |
|-------------|-------|---------------|-------------|
| `table_extraction` | 4 | CONFIDENT | Answer clearly in table cell |
| `json_navigation` | 3 | CONFIDENT | Answer in nested JSON |
| `table_absence` | 3 | ABSTAIN | Question about missing column |

#### Deliverables
- [x] 10 code context cases ✓ (api_confidence→confidence, code_abstention→abstention, deprecation_qualification→qualification, code_grounding→grounding)
- [x] 10 ambiguous query cases ✓ (entity_ambiguity, scope_ambiguity, temporal_ambiguity, metric_ambiguity→qualification)
- [x] 10 structured data cases ✓ (table_extraction, json_navigation→confidence, table_absence→abstention)
- [x] Supporting corpus documents ✓ (contexts self-contained)

---

### Phase 7: Documentation & Release (Week 9)

**Goal**: v2.0.0 release

#### Tasks

1. Update README.md with new case counts and categories
2. Update CHANGELOG.md with v2.0.0 release notes
3. Update `fitz_gov/__init__.py` version to 2.0.0
4. Run full test suite
5. Create GitHub release
6. Publish to PyPI

#### Deliverables
- [ ] All documentation updated
- [ ] Tests passing
- [ ] v2.0.0 released

---

## Actual Distribution (v2.0)

```
Total: 310 cases

tier0_sanity/       60 cases (unchanged)
├── abstention/     12 cases
├── dispute/        12 cases
├── qualification/  10 cases
├── confidence/     10 cases
├── grounding/       8 cases
└── relevance/       8 cases

tier1_core/        250 cases (+90 from v1.1.0)
├── abstention/     44 cases (+14)
├── dispute/        38 cases (+8)
├── qualification/  52 cases (+22)
├── confidence/     50 cases (+20)
├── grounding/      34 cases (+14)
├── relevance/      32 cases (+12)
└── (new categories integrated into existing files)
```

---

## Success Criteria

| Phase | Complete When |
|-------|---------------|
| Phase 1 | ~~Corpus has 370+ documents, structured data present~~ ✅ Done (378 docs) |
| Phase 2 | ~~Qualification reaches 50 cases with 4 new subcategories~~ ✅ Done (40 cases, 4 new subcats) |
| Phase 3 | ~~Grounding reaches 40, Relevance reaches 40~~ ✅ Done (32 each in Tier 1) |
| Phase 4 | ~~Abstention reaches 50, Dispute reaches 50~~ ✅ Done (38 each in Tier 1) |
| Phase 5 | ~~Confidence reaches 50 cases~~ ✅ Done (50 cases in Tier 1) |
| Phase 6 | ~~30 new category cases added~~ ✅ Done (30 cases across categories) |
| Phase 7 | v2.0.0 released on PyPI |

---

## Timeline Summary

| Phase | Duration | Key Deliverable |
|-------|----------|-----------------|
| Phase 1 | Week 1-2 | ~~90 new corpus documents~~ ✅ Done |
| Phase 2 | Week 3 | ~~10 new qualification cases~~ ✅ Done |
| Phase 3 | Week 4 | ~~24 new grounding/relevance cases~~ ✅ Done |
| Phase 4 | Week 5 | ~~16 new abstention/dispute cases~~ ✅ Done |
| Phase 5 | Week 6 | ~~10 new confidence cases~~ ✅ Done |
| Phase 6 | Week 7-8 | ~~30 new category cases~~ ✅ Done |
| Phase 7 | Week 9 | v2.0.0 release |

**Total estimated effort**: 9 weeks
