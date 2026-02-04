# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

fitz-gov is a RAG governance benchmark for evaluating whether RAG systems know when to abstain, dispute, qualify, or confidently answer based on available evidence. It focuses on epistemic honesty rather than just retrieval quality or answer correctness.

**Current version:** 1.0.0 with 200 test cases across 6 categories

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
```

## Architecture

### Core Modules

- **`fitz_gov/models.py`** - Data models using dataclasses: `FitzGovCase`, `FitzGovResult`, `FitzGovCaseResult`, enums `FitzGovCategory` and `AnswerMode`
- **`fitz_gov/evaluator.py`** - Main evaluation engine with `FitzGovEvaluator` class. Handles governance mode classification and answer quality assessment
- **`fitz_gov/loader.py`** - Test case loading from JSON files: `load_cases()`, `load_case_by_id()`
- **`fitz_gov/llm_validator.py`** - Two-pass validation (regex + LLM semantic check) via `OllamaValidator`. Results cached in `~/.cache/fitz_gov/`

### Evaluation Flow

1. **Governance categories** (abstention, dispute, qualification, confidence): Compare `actual_mode` to `expected_mode`
2. **Quality categories** (grounding, relevance): Two-pass validation
   - Fast regex pass checks `forbidden_claims` / `required_elements`
   - Optional LLM pass validates flagged responses semantically

### Test Data Structure

```
data/
├── abstention/abstention.json    # 40 cases - when to refuse
├── dispute/dispute.json          # 40 cases - conflicting sources
├── qualification/qualification.json  # 40 cases - incomplete evidence
├── confidence/confidence.json    # 30 cases - clear answers
├── grounding/grounding.json      # 25 cases - hallucination prevention
├── relevance/relevance.json      # 25 cases - answer relevance
└── corpus/documents.jsonl        # 288 reference documents
```

Each JSON file contains `cases` array with fields: `id`, `query`, `contexts`, `expected_mode`, `subcategory`, `difficulty`, `evaluation_config`

### Key Enums

- `FitzGovCategory`: ABSTENTION, DISPUTE, QUALIFICATION, CONFIDENCE, GROUNDING, RELEVANCE
- `AnswerMode`: ABSTAIN, DISPUTED, QUALIFIED, CONFIDENT

## Code Style

- Python 3.10+ required
- Black formatting with 100-char line length
- Strict mypy type checking (`disallow_untyped_defs = true`)
- isort with black-compatible profile
