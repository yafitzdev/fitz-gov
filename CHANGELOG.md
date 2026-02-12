# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

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

[Unreleased]: https://github.com/yafitzdev/fitz-gov/compare/v3.0.1...HEAD
[3.0.1]: https://github.com/yafitzdev/fitz-gov/compare/v3.0.0...v3.0.1
[3.0.0]: https://github.com/yafitzdev/fitz-gov/compare/v2.0.0...v3.0.0
[2.0.0]: https://github.com/yafitzdev/fitz-gov/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.com/yafitzdev/fitz-gov/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/yafitzdev/fitz-gov/releases/tag/v1.0.0
