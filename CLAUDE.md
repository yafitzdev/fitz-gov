# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

fitz-gov is a RAG governance benchmark for evaluating whether RAG systems know when to abstain, dispute, hedge, or confidently answer based on available evidence. It focuses on epistemic honesty rather than just retrieval quality or answer correctness.

**Current version:** 4.0.0 with 2,114 test cases (60 tier0 + 2,054 tier1) across 6 categories

## Commands

```bash
# Install for development
pip install -e .

# Run tests
pytest tests/

# Code formatting
black fitz_gov/ tests/
isort fitz_gov/ tests/

# Type checking
mypy fitz_gov/

# Validate benchmark data
python -m fitz_gov.cli validate --data-dir data

# Show benchmark statistics
python -m fitz_gov.cli stats --data-dir data

# Show classification breakdowns (domain, query type, etc.)
python -m fitz_gov.cli stats --data-dir data --breakdown
```

## Architecture

### Core Modules

- **`fitz_gov/models.py`** - Data models using dataclasses: `FitzGovCase`, `FitzGovResult`, `FitzGovCaseResult`, `Tier0Result`, `Tier1Result`, `TieredResult`, enums `FitzGovCategory` and `AnswerMode`
- **`fitz_gov/evaluator.py`** - Main evaluation engine with `FitzGovEvaluator` class. Handles governance mode classification, answer quality assessment, and tiered evaluation with classification breakdowns
- **`fitz_gov/loader.py`** - Test case loading from JSON files: `load_cases()`, `load_tier()`, `load_case_by_id()`
- **`fitz_gov/llm_validator.py`** - Two-pass validation (regex + LLM semantic check) via `OllamaValidator`. Results cached in `~/.cache/fitz_gov/`

### Evaluation Flow

1. **Governance categories** (abstention, dispute, trustworthy_hedged, trustworthy_direct, relevance): Compare `actual_mode` to `expected_mode`
2. **Quality categories** (grounding): Two-pass validation
   - Fast regex pass checks `forbidden_claims`
   - Optional LLM pass validates flagged responses semantically
3. **Tiered evaluation**: Tier 0 sanity check (95% threshold) gates Tier 1 full benchmark

### Test Data Structure

```
data/
├── tier0_sanity/                    # 60 easy cases (sanity check, 95% threshold)
│   ├── abstention.json              # 12 cases
│   ├── dispute.json                 # 12 cases
│   ├── trustworthy_hedged.json      # 10 cases
│   ├── trustworthy_direct.json      # 10 cases
│   ├── grounding.json               # 8 cases
│   └── relevance.json               # 8 cases
├── tier1_core/                      # 2,054 medium+hard cases (core benchmark)
│   ├── abstention.json              # 467 cases
│   ├── dispute.json                 # 409 cases
│   ├── trustworthy_hedged.json      # 414 cases
│   ├── trustworthy_direct.json      # 218 cases
│   ├── grounding.json               # 271 cases
│   └── relevance.json               # 275 cases
├── corpus/
│   ├── documents.jsonl              # Reference corpus
│   └── manifest.json                # Corpus metadata
└── queries/
    └── query_mappings.json          # Query-to-document mappings
```

Each JSON file contains `cases` array with fields: `id`, `query`, `contexts`, `expected_mode`, `subcategory`, `difficulty`, `category`, `evaluation_config`, plus classification fields (`domain`, `query_type`, `source_type`, `context_count`, `reasoning_type`, `evidence_pattern`)

### Key Enums

- `FitzGovCategory`: ABSTENTION, DISPUTE, TRUSTWORTHY_HEDGED, TRUSTWORTHY_DIRECT, GROUNDING, RELEVANCE
- `AnswerMode`: ABSTAIN, DISPUTED, TRUSTWORTHY

## Code Style

- Python 3.10+ required
- Black formatting with 100-char line length
- Strict mypy type checking (`disallow_untyped_defs = true`)
- isort with black-compatible profile
