# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

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

[Unreleased]: https://github.com/yafitzdev/fitz-gov/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yafitzdev/fitz-gov/releases/tag/v1.0.0
