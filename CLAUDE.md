# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

fitz-gov is a RAG governance benchmark for evaluating whether RAG systems know when to abstain, dispute, hedge, or confidently answer based on available evidence. It focuses on epistemic honesty rather than just retrieval quality or answer correctness.

**Current version:** 5.0.0 with 2,980 test cases (60 tier0 + 2,920 tier1) across 4 governance categories (grounding/relevance are now cross-cutting quality checks)

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

### SDGP (Synthetic Data Generation Pipeline) — `fitz_gov/sdgp/`

New subpackage targeting the V6+ scale-up per [pyrrho ROADMAP.md §3–§4](../pyrrho/docs/ROADMAP.md). Cell-targeted generation of taxonomy × domain × difficulty cases. Distinct from the legacy corpus-based `fitz_gov.generator` (which stays for backward compat).

- **`sdgp/taxonomy.py`** — 18 canonical evidence patterns (6 per governance class), 7 primary domains + 1 meta, 3 difficulty levels. `Cell` is the (pattern, domain, difficulty) coordinate; `cell_id` format is `"{pattern}__{domain}__{difficulty}"`. Includes cheap structural pattern checks (`check_pattern_structure`) — e.g. `numerical_conflict` requires ≥2 digit-bearing contexts.
- **`sdgp/vault.py`** — Append-only JSONL store with a `cell_id → case_ids` index. `Vault.open(path).add(case, provenance=...)` is idempotent and stamps `_vault` metadata (provider, prompt_version, batch_id, run_seed, added_at). Index rebuilds from JSONL after a crash. `Vault.cell_counts()` is the input the gap detector reads.
- **`sdgp/checker.py`** — Programmatic consistency checks. Schema, class consistency (`taxonomy.pattern` ↔ `governance.classification`), cell_id alignment with `meta.difficulty` + `routing.expert_fired`, pattern structure (delegates to taxonomy), signal coherence (`conflict_density` high for DISPUTED, low for TRUSTWORTHY; argmax of (a, d, t) matches classification; hallucination_pressure tracks classification), and dedup against a caller-supplied `seen_hashes` set. Errors block the case; warnings don't. Version-aware: V5.1-shaped rows (no taxonomy) get warnings rather than errors for fields they don't carry. `Checker(pattern_structure_warning_only=True)` downgrades pattern-structure failures to warnings — useful for migrated V5.1 cases.
- **`sdgp/enrich.py`** — Phase 0 V5.1 → V5.1-enriched mapping. Programmatic (no LLM): 17 domains → 7 expert domains, 4 categories → 3 governance classes, 115 subcategories → 18 taxonomy patterns (~70 explicit 1:1 mappings + keyword/category-default fallback), per-chunk authority_score + temporality, deterministic governance signals from `category`/`evidence_pattern`/`difficulty`, near-miss heuristics. Fields requiring real LLM reasoning (`query_rewritten`, `near_miss_reason`, per-chunk `anchor_period`) land as `<TODO_LLM>` markers so a Phase 0b enrichment pass can find-and-replace them.
- **`sdgp/__init__.py`** — re-exports the public API of all four modules.

- **`sdgp/providers.py`** — Pluggable LLM backends behind a single `Provider` ABC. `LocalLlmProvider` (Ollama HTTP at `localhost:11434`), `FileHandoffProvider` (writes prompt files to `handoff_dir/in/`, polls `out/` for the subagent's response — the "no API!" path for Claude Code / Codex subagents), `RoundRobinProvider` (rotates per call), `StubProvider` (deterministic, for tests), `BlindLabelPair` (enforces ROADMAP §4: generator and validator must never be the same instance). `providers_from_env()` reads `SDGP_LOCAL_MODEL` / `SDGP_HANDOFF_DIR` for CLI defaults.
- **`sdgp/gap_detector.py`** — 3D cell-coverage analysis. `GapDetector().rank(cell_counts, target, weights, filter)` returns a list of `Gap(priority, cell, current, target)` sorted highest-priority first. `PriorityWeights` multiplies per-pattern / per-domain / per-difficulty / per-class boosts onto the raw gap. `CellFilter` scopes the queue (single pattern, single class, etc.). `CellTarget` allows per-cell threshold overrides.
- **`sdgp/prompts.py`** — Per-pattern × per-domain × per-difficulty prompt library. `PATTERN_GUIDANCE` has one paragraph per pattern explaining structural requirements; `DOMAIN_HINTS` per domain; `DIFFICULTY_HINTS` per level. `build_prompt(cell)` composes the full generator prompt. `few_shot_for_cell(vault, cell, n=2)` pulls matching examples from the vault (prefers same domain → same pattern → same class). `SYSTEM_MESSAGE` constrains the model to JSON-only output.
- **`sdgp/orchestrator.py`** — Ties everything together. `Orchestrator(vault, provider, blind_label_pair).fill_gaps(gaps, n_per_cell)` builds prompts, calls providers, parses JSON (robust to fences / prose), runs the checker, blind-labels with the validator, and either vaults or routes to `<vault>/conflicts/<batch_id>/<case_id>.json`. Retries parse/checker rejections up to `max_attempts_per_cell`; aborts the batch on provider errors. `parse_case_json` handles common LLM wrappings (fences, leading prose).
- **`sdgp/monitor.py`** — Markdown coverage report. `write_coverage_report(cell_counts, out_path, target)` produces a stats table grouped by class / pattern / domain / difficulty, plus top-N most-filled and most-empty cells. Drop-in source-of-truth for "where are we?".
- **`sdgp/__init__.py`** — re-exports the full public API (70 symbols).

**Runners**:
- `scripts/sdgp_enrich_v51.py` — Phase 0 enrichment (V5.1 → V5.1-enriched vault).
- `scripts/sdgp_generate.py` — Phase 2 generation. Reads vault → ranks gaps → picks provider(s) from env / args → drives orchestrator → writes coverage report. Provider auto-selection (`--provider env`) picks up `SDGP_LOCAL_MODEL` and `SDGP_HANDOFF_DIR`; passing two providers enables blind labeling. Supports `--filter-pattern` / `--filter-class` / `--filter-difficulty` / `--filter-domain` for targeted batches.

**Coverage as of 2026-05-20** (after V5.1 enrichment, target 20/cell):
- 2,980 cases, 34 / 378 cells at target (9.0%), 148 cells empty (39.2%), total gap 5,584.
- Skew: science_medicine 29.6% at target vs history_geography 1.9%; TRUSTWORTHY 15.1% vs ABSTAIN 4.8%; hard 18.3% vs easy 0.0%. These are the V6 generation targets the gap detector now prioritizes.
- See `data/sdgp_reports/v51_enriched.md` for the full markdown breakdown.

Test suite: `tests/sdgp/` covers all SDGP modules (194 tests as of 2026-05-20). Run via `pytest tests/sdgp/ -q`.

Still to build (lower priority — operational quality, not on the critical path to V6):
- **Conflict-resolution CLI** (triage `<vault>/conflicts/*.json` interactively — currently they're just written to disk for manual handling).
- **Cost tracking per cell** (tokens × provider).
- **Near-miss generation mode** (ROADMAP §3: 20–25% of cases should be at taxonomy boundaries; needs a separate generator path that takes *two* adjacent patterns).

### Evaluation Flow

1. **Governance categories** (abstention, dispute, trustworthy_hedged, trustworthy_direct): Compare `actual_mode` to `expected_mode`
2. **Quality categories** (grounding, relevance): Two-pass validation
   - Fast regex pass checks `forbidden_claims` / `required_elements`
   - Optional LLM pass validates flagged responses semantically
3. **Tiered evaluation**: Tier 0 sanity check (95% threshold) gates Tier 1 full benchmark

### Test Data Structure

```
data/
├── tier0_sanity/                    # 60 easy cases (sanity check, 95% threshold)
│   ├── abstention.json              # 12 cases
│   ├── dispute.json                 # 12 cases
│   ├── trustworthy_hedged.json      # 26 cases
│   └── trustworthy_direct.json      # 10 cases
├── tier1_core/                      # 2,920 medium+hard cases (core benchmark)
│   ├── abstention.json              # 685 cases
│   ├── dispute.json                 # 675 cases
│   ├── trustworthy_hedged.json      # 1,160 cases
│   └── trustworthy_direct.json      # 400 cases
├── corpus/
│   ├── documents.jsonl              # Reference corpus
│   └── manifest.json                # Corpus metadata
└── queries/
    └── query_mappings.json          # Query-to-document mappings
```

Each JSON file contains `cases` array with fields: `id`, `query`, `contexts`, `expected_mode`, `subcategory`, `difficulty`, `category`, `evaluation_config`, plus classification fields (`domain`, `query_type`, `source_type`, `context_count`, `reasoning_type`, `evidence_pattern`)

### Key Enums

- `FitzGovCategory`: ABSTENTION, DISPUTE, TRUSTWORTHY_HEDGED, TRUSTWORTHY_DIRECT
- `AnswerMode`: ABSTAIN, DISPUTED, TRUSTWORTHY

## Code Style

- Python 3.10+ required
- Black formatting with 100-char line length
- Strict mypy type checking (`disallow_untyped_defs = true`)
- isort with black-compatible profile
