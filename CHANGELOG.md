# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [5.0.0] - 2026-02-15

### Highlights

**Grounding & Relevance Are Now Cross-Cutting Quality Checks** - Eliminated grounding and relevance as standalone categories. They are now quality dimensions applied to every trustworthy case (hedged and direct). Each trustworthy case now produces three scores: governance mode accuracy, grounding (did the response avoid hallucination?), and relevance (did the response address the question?). The benchmark drops from 6 categories to 4, with no data loss -- all 2,980 cases preserved.

### Breaking Changes

- **Removed `FitzGovCategory.GROUNDING` and `FitzGovCategory.RELEVANCE`** enum values
- **4 categories only**: abstention, dispute, trustworthy_hedged, trustworthy_direct
- `grounding.json` and `relevance.json` data files no longer exist (merged into `trustworthy_hedged.json`)
- `FitzGovCaseResult` has new fields: `mode_correct`, `grounding_passed`, `relevance_passed`, `grounding_failure`, `relevance_failure`
- `FitzGovCategoryResult` has new fields: `grounding_accuracy`, `relevance_accuracy`
- Score comparisons between v4.1 and v5.0 are NOT directly comparable due to structural changes

### Data Migration

- **676 grounding/relevance cases** converted to trustworthy_hedged with prefixed subcategories (`grounding_*`, `relevance_*`)
- **884 existing trustworthy cases** enriched with `forbidden_claims` and `required_elements` annotations
- All trustworthy cases (1,560 tier1 + 36 tier0) now have both quality annotation fields
- Trustworthy Hedged tier1: 484 → 1,160 cases (absorbed 336 grounding + 340 relevance)
- Trustworthy Direct: unchanged at 400 tier1 / 10 tier0
- All existing case IDs preserved

### Evaluation Changes

- **Unified evaluation flow**: All categories use governance mode classification. Trustworthy categories additionally run grounding and relevance quality checks when mode is correct.
- **Quality checks are conditional**: If the system picks the wrong governance mode, quality checks are skipped (no point checking answer quality when the meta-decision is wrong)
- **3-dimensional scoring** for trustworthy categories:
  ```
  trustworthy_hedged: 71.2% (826/1160)  |  grounding: 89.3%  relevance: 85.1%
  trustworthy_direct: 78.5% (314/400)   |  grounding: 92.1%  relevance: 88.7%
  ```
- **No LLM-as-judge**: Quality checks use regex-only validation (optional LLM validation still supported)
- All 4 categories participate in the confusion matrix

### Quality Annotation Details

- **Hedged cases**: `forbidden_claims` catch hallucinated specifics (dollar amounts, percentages, dates not in context); `required_elements` require hedging language appropriate to subcategory
- **Direct cases**: `forbidden_claims` catch unsupported embellishments; `required_elements` require key factual terms from context
- Annotations are subcategory-aware (e.g., `causal_uncertainty` cases require correlation/confounding language)

### Distribution (Tier 1)

| Category | Cases | Medium | Hard | Med % |
|----------|------:|-------:|-----:|------:|
| Trustworthy Hedged | 1,160 | 435 | 725 | 38% |
| Abstention | 685 | 255 | 430 | 37% |
| Dispute | 675 | 261 | 414 | 39% |
| Trustworthy Direct | 400 | 145 | 255 | 36% |

| Metric | v4.1 | v5.0 |
|--------|------|------|
| Categories | 6 | 4 |
| Total cases | 2,980 | 2,980 |
| Cases with forbidden_claims | 344 | ~1,596 |
| Cases with required_elements | 348 | ~1,596 |
| Subcategories | 113 | 113 |

### Subcategories (Trustworthy Hedged)

57 subcategories after merge:
- **20 original hedged**: evidence_quality, hedged_evidence, different_aspects, causal_uncertainty, mixed_evidence, temporal_uncertainty, version_overlap, methodology_difference, stale_source, evolving_facts, entity_ambiguity, partial_answer, scope_condition, numerical_near_miss, cross_source_partial, implicit_assumptions, adjacent_entity, cross_domain_transfer, hedged_contradiction_corroborated, different_framing
- **18 from grounding**: grounding_numerical_hallucination, grounding_attribution_hallucination, grounding_temporal_confusion, grounding_entity_blending, grounding_process_hallucination, grounding_quote_fabrication, grounding_statistical_inference, grounding_code_hallucination, grounding_table_inference, grounding_causal_hallucination, grounding_comparative_hallucination, grounding_geographic_hallucination, grounding_technical_hallucination, grounding_date_hallucination, grounding_location_hallucination, grounding_code_grounding, grounding_medical_hallucination, grounding_quote_extension
- **19 from relevance**: relevance_partial_answer, relevance_wrong_entity_focus, relevance_temporal_mismatch, relevance_tangent_drift, relevance_related_but_different, relevance_over_answering, relevance_granularity_mismatch, relevance_prerequisite_missing, relevance_scope_mismatch, relevance_format_mismatch, relevance_summarization_vs_answer, relevance_cherry_picking, relevance_false_precision, relevance_assumption_injection, relevance_symptom_only, relevance_status_dump, relevance_feature_dump, relevance_instruction_only, relevance_metric_avoidance

### Migration Notes

- `pip install fitz-gov==5.0.0` to upgrade
- Remove any references to `FitzGovCategory.GROUNDING` or `FitzGovCategory.RELEVANCE`
- `GOVERNANCE_MODE_CATEGORIES` and `ANSWER_QUALITY_CATEGORIES` constants removed; use `TRUSTWORTHY_CATEGORIES` instead
- Case IDs unchanged -- grounding/relevance case IDs still work with `load_case_by_id()`
- `evaluate_case()` now returns richer results with quality check fields

---

## [4.1.0] - 2026-02-15

### Highlights

**Benchmark Credibility Hardening** - From 2,488 to 2,980 test cases (60 tier0 + 2,920 tier1). Addressed five structural gaps that would undermine credibility with serious benchmark consumers: expanded trustworthy_direct from 218 to 400 cases, added 310 medium-difficulty cases across 5 categories, expanded multi-source cases from 138 to 264, eliminated all "general" domain cases, and added a 250-case human validation sample with annotation guide.

### Data Expansion

- **2,920 tier1 cases** (up from 2,428):
  - Abstention: 685 (+60 medium)
  - Dispute: 675 (+50 medium)
  - Trustworthy Hedged: 484 (+70 medium)
  - Trustworthy Direct: 400 (+182 mixed hard/medium)
  - Grounding: 336 (+65 medium)
  - Relevance: 340 (+65 medium)
- **Difficulty rebalance**: 37.3% medium / 62.7% hard (was 28.4% / 71.6%)
- **Multi-source expansion**: 264 cases (9.0%, up from 138 / 5.7%), all with `context_sources` metadata
- **Domain cleanup**: Eliminated all 63 "general" domain cases, reclassified into proper 17 domains
- **Zero duplicate queries**: Fixed 26 duplicate groups introduced during generation
- **Zero sparse subcategories**: All subcategories have >= 5 cases

### New Features

- **Human validation sample** (`data/validation/human_validation_sample.json`):
  - 250 cases stratified by category, difficulty, and domain (seed=42)
  - Null-initialized annotator fields for inter-annotator agreement (IAA) studies
  - Gold labels mapped from categories (abstention->abstain, dispute->disputed, etc.)
- **Annotation guide** (`docs/ANNOTATION_GUIDE.md`):
  - Decision tree for TRUSTWORTHY vs DISPUTED vs ABSTAIN classification
  - 6 worked examples (2 per mode) with query, context, label, and reasoning
  - Edge case documentation for common confusion points
  - Cohen's kappa interpretation guide

### New Subcategories

- **Trustworthy Direct**: `step_by_step` (13 cases) - procedural answers with clear steps, `definitional` (13 cases) - clear term/concept definitions
- All existing subcategories expanded proportionally with new medium-difficulty cases

### Corpus & Infrastructure

- **5,043 corpus documents** (up from 4,271), 772 new documents from expanded cases
- **3,800 query mappings** (up from 3,248), 552 new mappings
- **Manifest updated** to v4.1.0 with accurate domain counts
- **README rewritten** with comprehensive statistics: categories, modes, difficulty, domains, query types, source types, reasoning types, evidence patterns, context counts, and all 113 subcategories

### Distribution (Tier 1)

| Category | Cases | Medium | Hard | Med % |
|----------|------:|-------:|-----:|------:|
| Abstention | 685 | 255 | 430 | 37% |
| Dispute | 675 | 261 | 414 | 39% |
| Trustworthy Hedged | 484 | 171 | 313 | 35% |
| Trustworthy Direct | 400 | 145 | 255 | 36% |
| Relevance | 340 | 129 | 211 | 38% |
| Grounding | 336 | 128 | 208 | 38% |

| Mode | Cases | % |
|------|------:|--:|
| TRUSTWORTHY | 1,560 | 53.4% |
| ABSTAIN | 685 | 23.5% |
| DISPUTED | 675 | 23.1% |

| Domain | Cases | % | Domain | Cases | % |
|--------|------:|--:|--------|------:|--:|
| Technology | 412 | 14.1% | Transportation | 131 | 4.5% |
| Medicine | 309 | 10.6% | Sports | 127 | 4.3% |
| Finance | 296 | 10.1% | Agriculture | 126 | 4.3% |
| Science | 192 | 6.6% | History | 122 | 4.2% |
| Government | 155 | 5.3% | HR/Workplace | 121 | 4.1% |
| Education | 152 | 5.2% | Real Estate | 119 | 4.1% |
| Environment | 147 | 5.0% | Psychology | 119 | 4.1% |
| Food | 143 | 4.9% | Social Media | 113 | 3.9% |
| Law | 136 | 4.7% | | | |

### Migration Notes

- All existing case IDs preserved
- 17 field value corrections: 3 invalid domains, 11 invalid reasoning_types, 3 invalid evidence_patterns
- 4 tier0 subcategory merges (sparse into established subcategories)
- Score comparisons between v4.0 and v4.1 are NOT directly comparable due to case count and difficulty distribution changes
- `pip install fitz-gov==4.1.0` to upgrade

---

## [4.0.0] - 2026-02-12

### Highlights

**Massive Benchmark Expansion** - From 1,173 to 2,114 test cases (60 tier0 + 2,054 tier1). Added 364 medium-difficulty cases (25% of tier1), expanded grounding from 34 to 271 cases and relevance from 32 to 275 cases with hand-written rich content, added 6 classification attributes to every case for results slicing.

### Data Expansion

- **2,054 tier1 cases** (up from 1,113):
  - Abstention: 467 (+230), Dispute: 409 (+213)
  - Trustworthy Hedged: 414 (+54), Trustworthy Direct: 218 (-36, net after conversions)
  - Grounding: 271 (+237), Relevance: 275 (+243)
- **364 medium-difficulty cases** across all 6 categories (25% of tier1)
- **Rewritten grounding/relevance content** - all 336 cases replaced with hand-written rich content (80-150 word contexts, domain-specific detail)
- **Domain rebalancing** - converted 106 cases from over-represented domains (tech/finance/medicine) to under-represented ones (social media, history, psychology, government, agriculture)
- **30 multi-source trustworthy cases** with context_sources metadata
- **100 new abstain cases** and **100 new dispute cases**
- **Sparse subcategory expansion** - all subcategories now have >= 5 cases
- **29 duplicate queries removed** via deduplication pass

### New Features

- **6 classification attributes** on every case for results slicing:
  - `domain` (18 values), `query_type` (10 values), `source_type`, `context_count`, `reasoning_type` (6 values), `evidence_pattern` (6 values)
- **Evaluator classification breakdowns** - `Tier1Result` includes `domain_breakdown`, `query_type_breakdown`, `source_type_breakdown`, `reasoning_type_breakdown`, `evidence_pattern_breakdown`
- **CLI `--breakdown` flag** - `python -m fitz_gov.cli stats --data-dir data --breakdown` shows distribution by domain, query type, etc.
- **Comprehensive test suite** - 103 tests covering models, loader, evaluator, data integrity, validation, CLI

### Code Quality

- Removed dead `schema.py` (duplicate of `models.py`)
- Fixed `__init__.py` version (was stuck at 3.0.0)
- Removed unused `Callable` import from evaluator
- Fixed 107 `context_count` mismatches in grounding/relevance data
- Fixed stale docstrings in generator.py referencing old category names

### Distribution

| Category | Cases | % |
|----------|------:|--:|
| Abstention | 467 | 22.7% |
| Trustworthy Hedged | 414 | 20.2% |
| Dispute | 409 | 19.9% |
| Relevance | 275 | 13.4% |
| Grounding | 271 | 13.2% |
| Trustworthy Direct | 218 | 10.6% |

| Difficulty | Cases | % |
|-----------|------:|--:|
| Hard | 1,551 | 75.5% |
| Medium | 503 | 24.5% |

### Migration Notes

- All existing case IDs preserved
- `context_sources` field added for multi-source cases (138 cases)
- Classification attributes have defaults, so older JSON loads without breaking
- Score comparisons between v3.0 and v4.0 are NOT directly comparable due to case count and difficulty changes

---

## [3.0.1] - 2026-02-11

### Changed

- **Category rename**: `qualification` → `trustworthy_hedged`, `confidence` → `trustworthy_direct`
  - Eliminates ambiguity between test category names and the old 4-class mode names (QUALIFIED, CONFIDENT)
  - Both categories still map to TRUSTWORTHY mode — the rename makes this relationship obvious
  - Data files renamed: `qualification.json` → `trustworthy_hedged.json`, `confidence.json` → `trustworthy_direct.json`
  - Case IDs unchanged (`t1_qualify_*`, `t1_confident_*`) — stable identifiers

### Fixed

- **validate.py**: `valid_modes` list now correctly uses 3-mode values (`["abstain", "disputed", "trustworthy"]`) instead of stale 4-mode values

---

## [3.0.0] - 2026-02-11

### 🎉 Highlights

**Massive Benchmark Expansion** - Expanded from 331 to 1173 test cases (3.5x) with 92% hard-difficulty cases targeting real-world governance failure modes. Added 54 unique subcategories, three-way ambiguity cases, and boundary cases that discriminate between good and excellent governance. Designed to support ML-based governance classifier training.

**3-Mode System Alignment** - fitz-gov now uses the same 3-mode system as fitz-ai (TRUSTWORTHY, DISPUTED, ABSTAIN). The benchmark categories (qualification, confidence) remain as test categories that describe what's being tested, but both now expect TRUSTWORTHY mode. This eliminates the mode mapping complexity between fitz-ai and fitz-gov.

### 📊 Test Set Changes

- **1173 test cases** (up from 331) across 2 tiers:
  - **Tier 0 (Sanity)**: 60 cases - unchanged
  - **Tier 1 (Core)**: 1113 cases (up from 271)
    - 1047 governance mode cases (abstain/dispute/qualify/confident)
    - 66 answer quality cases (grounding/relevance)

- **Category breakdown (Tier 1)**:
  - `abstention`: 237 cases (+186)
  - `dispute`: 196 cases (+153)
  - `qualification`: 360 cases (+302)
  - `confidence`: 254 cases (+201)
  - `grounding`: 34 cases (unchanged)
  - `relevance`: 32 cases (unchanged)

- **378 corpus documents** (unchanged)

- **54 unique subcategories** across all categories (consolidated from expansion phases)

### 🆕 New Subcategory Clusters

**Abstention**:
- `wrong_entity`, `wrong_domain`, `wrong_version`, `wrong_jurisdiction`, `wrong_time_period`
- `decoy_keywords` - Shares vocabulary but different domain
- `domain_bleed` - Related but distinct domains
- `partial_schema_match` - Structural similarity without content match
- `code_abstention` - Wrong language/framework context

**Dispute**:
- `same_metric_different_values` - Direct numerical contradiction
- `opposing_conclusions` - Same question, opposite answers
- `contradictory_dates`, `contradictory_attribution`, `contradictory_status`
- `implicit_contradiction` - Logically incompatible claims
- `binary_fact_conflict` - Approved vs rejected, passed vs failed
- `statistical_direction_conflict` - Increase vs decrease
- `competing_theories`, `conditional_conflict`

**Qualification**:
- `same_topic_different_aspects`, `mixed_evidence`, `conditional_applicability`
- `hedged_claims` - Source uses "may", "suggests", "preliminary"
- `temporal_ambiguity`, `entity_ambiguity`, `scope_ambiguity`
- `deprecated_documentation` - Outdated but partially relevant
- `correlation_vs_causation` - Evidence shows correlation, query asks causation
- `methodology_difference` - Values differ due to methodology, not fact
- `hedged_vs_assertive`, `numerical_near_miss`, `evolving_facts`
- `pros_vs_cons`, `risk_vs_benefit`, `small_sample`, `source_quality_variance`

**Confidence**:
- `direct_factual`, `multi_source_convergence`, `clear_procedural`
- `unambiguous_extraction` - Answer clearly in table/JSON
- `well_documented_technical` - Clear API/code documentation
- `clear_causal_explanation` - Mechanism explained, not just correlation
- `different_framing_same_fact` - Apparent contradiction resolved by framing
- `opposing_with_consensus` - Strong consensus despite minor dissent
- `numerical_diff_methodology_explained` - Gap explained by stated methodology
- `contradiction_with_clear_winner` - One source clearly more authoritative

### 🔀 Boundary Cases

Added ~355 boundary cases that sit at mode decision boundaries:

| Boundary | Cases | Key Challenge |
|----------|-------|---------------|
| Dispute <-> Qualify | ~175 | Methodology difference vs genuine contradiction |
| Abstain <-> Qualify | ~25 | Topic-adjacent but no direct answer |
| Qualify <-> Confident | ~30 | Evidence exists but needs caveats |
| Abstain <-> Dispute | ~20 | Real contradiction about wrong subject |
| Dispute <-> Confident | ~15 | Apparent contradiction resolved by context |
| Three-way ambiguity | ~90 | Multiple competing signals |

### 🔧 Evaluation Changes

- **3-mode system**: Collapsed CONFIDENT and QUALIFIED into TRUSTWORTHY mode (matching fitz-ai)
- **Confusion matrix**: Now 3x3 (TRST/DISP/ABST) instead of 4x4
- **Category distinction**: qualification and confidence categories still exist to test different behaviors (hedging vs confidence) but both expect TRUSTWORTHY mode
- **Relevance category** now evaluated as governance mode classification (not answer quality text check)
- **Difficulty distribution**: 92% hard cases in Tier 1 (by design)
- **Expected score range**: 60-75% for production models on v3.0 (v3.0 is significantly harder than v2.0)
- **Score interpretation**: 69% on v3.0 represents stronger governance than 72% on v2.0

### 🚀 Improvements

- Cases designed for ML classifier training (58-feature extraction support)
- Three-way ambiguity cases with >93% independent blind labeling agreement
- Comprehensive boundary case coverage for dispute vs qualification distinction
- Primary bottleneck documentation: methodology/scope differences are QUALIFIED, not DISPUTED

### ⚠️ Migration Notes

- **Mode system change**: expected_mode values are now "trustworthy", "disputed", "abstain" (was "confident", "qualified", "disputed", "abstain")
- **No mode mapping needed**: fitz-ai and fitz-gov now use identical 3-mode system
- All existing case IDs preserved (backward compatible)
- New cases use sequential IDs with `t1_` prefix
- Score comparisons between v2.0 and v3.0 are NOT directly comparable due to increased difficulty
- Systems scoring 72% on v2.0 may score ~65-69% on v3.0

---

## [2.0.0] - 2026-02-05

### 🎉 Highlights

**Major Test Case Expansion** - Expanded benchmark from 220 to 331 cases (+50%) with comprehensive coverage of real-world RAG failure modes. Added new subcategories for code context, ambiguous queries, structured data extraction, and adversarial edge cases.

### 📊 Test Set Changes

- **331 test cases** (up from 220) across 2 tiers:
  - **Tier 0 (Sanity)**: 60 cases - unchanged
  - **Tier 1 (Core)**: 271 cases (up from 160)

- **Category breakdown (Tier 1)**:
  - `abstention`: 51 cases (+21)
  - `dispute`: 43 cases (+13)
  - `qualification`: 58 cases (+28)
  - `confidence`: 53 cases (+23)
  - `grounding`: 34 cases (+14)
  - `relevance`: 32 cases (+12)

- **378 corpus documents** (up from 288):
  - Added structured data documents (tables, JSON)
  - Added code documentation (Python, REST API, config files)
  - Expanded legal, sports, and consumer domains
  - Added long-form documents (500-1000 words)

### 🆕 New Subcategories

**Phase 2 - Qualification Expansion**:
- `hedged_source` - Context uses "may", "suggests", "preliminary"
- `source_quality` - Non-authoritative sources (blogs, social media)
- `population_mismatch` - Study on group A, question about group B
- `temporal_extrapolation` - Historical data for future predictions

**Phase 3 - Grounding & Relevance**:
- `code_hallucination` - Fabricating function parameters/return types
- `table_inference` - Inventing data not in provided tables
- `quote_extension` - Adding words to partial quotes
- `temporal_confusion` - Mixing dates from different events
- `summarization_vs_answer` - Summarizing instead of answering
- `related_but_different` - Answering adjacent questions
- `over_answering` - Providing unrequested details
- `prerequisite_missing` - Answer requires unstated context

**Phase 4 - Abstention & Dispute**:
- `version_mismatch` - Wrong software version in context
- `partial_coverage` - Some but not all required aspects present
- `scope_mismatch` - Geographic/demographic scope mismatch
- `temporal_gap` - Context too old for "current" questions
- `confidence_interval_overlap` - Statistically indistinguishable differences
- `scope_conflict` - General rule vs specific exception
- `methodology_incompatible` - Different measurement methods
- `time_context_conflict` - Same metric, different time periods

**Phase 5 & 6 - New Categories**:
- `code_documentation` - Clear API docs with exact syntax
- `official_statement` - Quoted company announcements
- `regulatory_specification` - Explicit legal requirements
- `multi_source_convergence` - 3+ independent sources agree
- `api_confidence` - Clear function documentation
- `code_abstention` - Wrong language/version context
- `deprecation_qualification` - Deprecated API in context
- `code_grounding` - Temptation to hallucinate parameters
- `entity_ambiguity` - "Apple" could be company or fruit
- `scope_ambiguity` - "The project" with multiple projects
- `temporal_ambiguity` - "Current" with multiple time contexts
- `metric_ambiguity` - "Performance" could mean speed, accuracy, cost
- `table_extraction` - Answer clearly in table cell
- `json_navigation` - Answer in nested JSON structure
- `table_absence` - Question about missing column

**Phase 7.5 - Edge Cases**:
- `temporal_staleness` - Context too old without explicit dating
- `jurisdictional_mismatch` - Different legal regimes
- `domain_bleed` - Related but legally/technically distinct domains
- `vague_entity_reference` - "The company" when multiple mentioned
- `insufficient_comparative` - Comparison needs but only one entity
- `time_dependent_contradiction` - True then, false now
- `unit_scale_mismatch` - Same value, different units
- `scope_disagreement` - Both true for different populations
- `semantic_ambiguity` - Apparent contradiction resolved by definition
- `multiple_confounders` - Multiple simultaneous changes
- `reverse_causation` - Causation could flow either direction
- `temporal_ordering_unclear` - Events in same period
- `outdated_confidence` - Old claim superseded by new data
- `conditional_confidence` - True under specific conditions
- `expert_consensus` - Multiple authoritative sources agree

### 🚀 Improvements

- Enhanced corpus with structured data formats (tables, JSON, code)
- Better domain balance (legal, sports, consumer expanded)
- More adversarial test cases for real-world failure modes
- Comprehensive edge case coverage for production RAG systems

### ⚠️ Migration Notes

- All existing case IDs preserved (backward compatible)
- New cases use sequential IDs continuing from v1.1.0
- Corpus document count increased; existing IDs unchanged

---

## [1.1.0] - 2026-02-05

### 🎉 Highlights

**Tiered Evaluation** - Restructured benchmark into a two-tier system for clearer evaluation semantics. Tier 0 (sanity check) gates Tier 1 (core benchmark), providing fast baseline verification before detailed scoring.

### 📊 Test Set Changes

- **220 test cases** (up from 200) across 2 tiers:
  - **Tier 0 (Sanity)**: 60 cases - 95% threshold gate
  - **Tier 1 (Core)**: 160 cases - gradient scoring

- **New subcategories added**:
  - `multi_source_agreement` - Multiple sources converging on same fact
  - `explicit_recency` - Claims with clear effective dates
  - `bounded_claim` - Claims with explicit limitations stated
  - `authoritative_source` - Official documentation citations
  - `near_miss_entity` - Similar but different entities
  - `stale_data` - Outdated information for current questions
  - `implicit_contradiction` - Mathematically incompatible sources
  - `definition_conflict` - Conflicting classification systems
  - `entity_blending` - Attribute confusion between entities
  - `quote_fabrication` - Temptation to invent quotes
  - `statistical_inference` - Qualitative to quantitative traps
  - `format_mismatch` - Requested format not available
  - `granularity_mismatch` - Wrong specificity level

### 🚀 New Features

- **Tiered Evaluation API**:
  - `evaluate_tiered()` - Run both tiers with optional gating
  - `load_tier(Tier.SANITY)` / `load_tier(Tier.CORE)` - Load tier-specific cases
  - `TieredResult`, `Tier0Result`, `Tier1Result` - New result models

- **Gating Logic**: Tier 1 automatically skipped when Tier 0 fails (configurable)

- **CLI Updates**:
  - `stats` command shows tiered structure with case counts
  - `--verbose` flag for subcategory breakdown

- **Improved Output Format**:
  - Tier 0: pass/fail with threshold, by-category breakdown
  - Tier 1: accuracy, by-category, by-difficulty, confusion matrix

### 📦 Data Structure

New tiered directory layout (backward compatible):
```
data/
├── tier0_sanity/    # 60 easy cases (95% threshold)
│   ├── abstention.json (12)
│   ├── dispute.json (12)
│   ├── qualification.json (10)
│   ├── confidence.json (10)
│   ├── grounding.json (8)
│   └── relevance.json (8)
├── tier1_core/      # 160 medium/hard cases
│   ├── abstention.json (30)
│   ├── dispute.json (30)
│   ├── qualification.json (30)
│   ├── confidence.json (30)
│   ├── grounding.json (20)
│   └── relevance.json (20)
└── corpus/
    └── documents.jsonl
```

### ⚠️ Migration Notes

- `load_cases()` still returns all cases (backward compatible)
- Case IDs now prefixed with `t0_` or `t1_` indicating tier
- Legacy flat structure still supported but deprecated

---

## [1.0.0] - 2026-02-04

### 🎉 Highlights

**Initial Stable Release** - First frozen benchmark for RAG governance evaluation. This version establishes the baseline test set for measuring epistemic honesty in RAG systems.

### 📊 Test Set

- **200 test cases** across 6 governance categories:
  - `abstention` - 40 cases (when to refuse answering)
  - `dispute` - 40 cases (conflicting source handling)
  - `qualification` - 40 cases (incomplete evidence handling)
  - `confidence` - 30 cases (clear answer scenarios)
  - `grounding` - 25 cases (hallucination prevention)
  - `relevance` - 25 cases (answer relevance validation)

- **288 corpus documents** in `data/corpus/documents.jsonl`

### 🧪 Baseline Results

| System | Score |
|--------|-------|
| fitz-ai RAG | 72.5% |

### 🚀 Features

- `FitzGovEvaluator` - Main evaluation engine for governance mode classification
- `OllamaValidator` - Two-pass validation (regex + LLM semantic check)
- `load_cases()` / `load_case_by_id()` - Test case loading utilities
- CLI validation and statistics commands
- Pip-installable package

### 📦 Package

- Python 3.10+ required
- Minimal dependencies (httpx only)
- MIT licensed

---

[Unreleased]: https://github.com/yafitzdev/fitz-gov/compare/v5.0.0...HEAD
[5.0.0]: https://github.com/yafitzdev/fitz-gov/compare/v4.1.0...v5.0.0
[4.1.0]: https://github.com/yafitzdev/fitz-gov/compare/v4.0.0...v4.1.0
[4.0.0]: https://github.com/yafitzdev/fitz-gov/compare/v3.0.0...v4.0.0
[3.0.1]: https://github.com/yafitzdev/fitz-gov/compare/v3.0.0...v3.0.1
[3.0.0]: https://github.com/yafitzdev/fitz-gov/compare/v2.0.0...v3.0.0
[2.0.0]: https://github.com/yafitzdev/fitz-gov/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.com/yafitzdev/fitz-gov/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/yafitzdev/fitz-gov/releases/tag/v1.0.0
