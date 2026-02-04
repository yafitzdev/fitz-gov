# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

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

[Unreleased]: https://github.com/yafitzdev/fitz-gov/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/yafitzdev/fitz-gov/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/yafitzdev/fitz-gov/releases/tag/v1.0.0
