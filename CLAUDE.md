# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

fitz-gov is a RAG governance benchmark for evaluating whether RAG systems know when to abstain, dispute, hedge, or confidently answer based on available evidence. It focuses on epistemic honesty rather than just retrieval quality or answer correctness.

**Current dataset version:** 7.0.0 on Hugging Face (`yafitzdev/fitz-gov`, tag `v7.0.0`) with 10,500 rows in the default `v7` config (`train=8,400`, `validation=1,050`, `test=1,050`). V6.0.0 remains the 2,980-row V5.1 schema overlay baseline.

- **Phase 0b — core governance signals (every case):** `query_rewritten`, per-chunk `summary`/`relevance_to_query`/`temporality.anchor_period`, `governance.{hallucination_pressure, retrieval_retry_value, query_evidence_alignment, answer_coverage, boundary_proximity.distance}`, `meta.near_miss_reason`.
- **Phase 0c — MoE multi-task training ground truth:** per-chunk `boundary_quality` (0–1 cut quality), `governance.evidence_bias_score` (0–1 source one-sidedness), `input.evidence_chain` (`{order, reasoning}` — multi-chunk only), `meta.grounding_targets` (`{gold_answer, sentences[].attributions}` — TRUSTWORTHY only).

V6 uses the same 2,980 case IDs as V5.1 with additive fields. V7 adds 7,520 SDGP-generated rows and publishes a query-grouped train/validation/test contract.

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

New subpackage targeting the V7+ scale-up per [pyrrho ROADMAP.md §3–§4](../pyrrho/docs/ROADMAP.md). Cell-targeted generation of taxonomy × domain × difficulty cases. Distinct from the legacy corpus-based `fitz_gov.generator` (which stays for backward compat). (V6 = V5.1 schema overlay; V7 is the first SDGP-scaled major version.)

- **`sdgp/taxonomy.py`** — 18 canonical evidence patterns (6 per governance class), 7 primary domains + 1 meta, 3 difficulty levels. `Cell` is the (pattern, domain, difficulty) coordinate; `cell_id` format is `"{pattern}__{domain}__{difficulty}"`. Includes cheap structural pattern checks (`check_pattern_structure`) — e.g. `numerical_conflict` requires ≥2 digit-bearing contexts.
- **`sdgp/vault.py`** — Append-only JSONL store with a `cell_id → case_ids` index. `Vault.open(path).add(case, provenance=...)` is idempotent and stamps `_vault` metadata (provider, prompt_version, batch_id, run_seed, added_at). Index rebuilds from JSONL after a crash. `Vault.cell_counts()` is the input the gap detector reads.
- **`sdgp/checker.py`** — Programmatic consistency checks. Schema, class consistency (`taxonomy.pattern` ↔ `governance.classification`), cell_id alignment with `meta.difficulty` + `routing.expert_fired`, pattern structure (delegates to taxonomy), signal coherence (`conflict_density` high for DISPUTED, low for TRUSTWORTHY; argmax of (a, d, t) matches classification; hallucination_pressure tracks classification), and dedup against a caller-supplied `seen_hashes` set. Errors block the case; warnings don't. Version-aware: V5.1-shaped rows (no taxonomy) get warnings rather than errors for fields they don't carry. `Checker(pattern_structure_warning_only=True)` downgrades pattern-structure failures to warnings — useful for migrated V5.1 cases.
- **`sdgp/enrich.py`** — Phase 0 V5.1 → V5.1-enriched mapping. Programmatic (no LLM): 17 domains → 7 expert domains, 4 categories → 3 governance classes, 115 subcategories → 18 taxonomy patterns (~70 explicit 1:1 mappings + keyword/category-default fallback), per-chunk authority_score + temporality, deterministic governance signals from `category`/`evidence_pattern`/`difficulty`, near-miss heuristics. Fields requiring real LLM reasoning (`query_rewritten`, `near_miss_reason`, per-chunk `anchor_period`) land as `<TODO_LLM>` markers so a Phase 0b enrichment pass can find-and-replace them.
- **`sdgp/__init__.py`** — re-exports the public API of all four modules.

- **`sdgp/providers.py`** — Pluggable LLM backends behind a single `Provider` ABC. `LocalLlmProvider` (Ollama HTTP at `localhost:11434`), `FileHandoffProvider` (writes prompt files to `handoff_dir/in/`, polls `out/` for the subagent's response — the "no API!" path for Claude Code / Codex subagents), `RoundRobinProvider` (rotates per call), `StubProvider` (deterministic, for tests), `BlindLabelPair` (enforces ROADMAP §4: generator and validator must never be the same instance). `providers_from_env()` reads `SDGP_LOCAL_MODEL` / `SDGP_HANDOFF_DIR` for CLI defaults.
- **`sdgp/gap_detector.py`** — 3D cell-coverage analysis. `GapDetector().rank(cell_counts, target, weights, filter)` returns a list of `Gap(priority, cell, current, target)` sorted highest-priority first. `PriorityWeights` multiplies per-pattern / per-domain / per-difficulty / per-class boosts onto the raw gap. `CellFilter` scopes the queue (single pattern, single class, etc.). `CellTarget` allows per-cell threshold overrides.
- **`sdgp/prompts.py`** — Per-pattern × per-domain × per-difficulty prompt library. `PATTERN_GUIDANCE` has one paragraph per pattern explaining structural requirements; `DOMAIN_HINTS` per domain; `DIFFICULTY_HINTS` per level. `build_prompt(cell)` composes the full generator prompt. `few_shot_for_cell(vault, cell, n=2)` pulls matching examples from the vault (prefers same domain → same pattern → same class). `SYSTEM_MESSAGE` constrains the model to JSON-only output.
- **`sdgp/orchestrator.py`** — Ties everything together. `Orchestrator(vault, provider, blind_label_pair).fill_gaps(gaps, n_per_cell)` builds prompts, calls providers, parses JSON (robust to fences / prose), runs the checker, blind-labels with the validator, and either vaults or routes to `<vault>/conflicts/<batch_id>/<case_id>.json`. Retries parse/checker rejections up to `max_attempts_per_cell`; aborts the batch on provider errors. `parse_case_json` handles common LLM wrappings (fences, leading prose).
- **`sdgp/blind_label.py`** — Provider-agnostic blind-label prompt/parse/score helpers. Builds gold-label-free prompts from `blind_label_queue.jsonl`, parses JSON or plain label responses, joins predictions to `blind_label_manifest.jsonl`, and emits agreement/disagreement/review summaries.
- **`sdgp/evaluation_fields.py`** — Canonical evaluator-field promotion/audit helpers. Promotes old evaluator-only fields into `case["evaluation"]`, strips duplicate legacy aliases, and detects TRUSTWORTHY rows missing answer-quality constraints.
- **`sdgp/evaluation_completion.py`** — Prompt/parser helpers for model-authored canonical evaluator quality constraints.
- **`sdgp/monitor.py`** — Markdown coverage report. `write_coverage_report(cell_counts, out_path, target)` produces a stats table grouped by class / pattern / domain / difficulty, plus top-N most-filled and most-empty cells. Drop-in source-of-truth for "where are we?".
- **`sdgp/__init__.py`** — re-exports the full public API (70 symbols).

**Runners**:
- `scripts/sdgp_enrich_v51.py` — Phase 0a heuristic enrichment (V5.1 → V6 vault; Phase 0b LLM enrichment via `scripts/sdgp_enrich_v51_llm.py` fills the `<TODO_LLM>` markers). Phase 0 complete 2026-05-20; vault published as `yafitzdev/fitz-gov` v6.0.0.
- `scripts/sdgp_generate.py` — Phase 2 generation. Reads vault → ranks gaps → picks provider(s) from env / args → drives orchestrator → writes coverage report. Provider auto-selection (`--provider env`) picks up `SDGP_LOCAL_MODEL` and `SDGP_HANDOFF_DIR`; passing two providers enables blind labeling. Supports `--filter-pattern` / `--filter-class` / `--filter-difficulty` / `--filter-domain` for targeted batches. Rejects schema-thin rows by default; `--allow-thin` is diagnostic-only.
- `scripts/sdgp_audit_training_schema.py` — strict audit for full V6/MoE training-schema completeness. Use before publishing or expanding V7.
- `scripts/sdgp_complete_v7_schema.py` — provider-backed completion runner for schema-thin V7 rows. Sends one completion prompt per case and only writes rows that pass `audit_case_completeness()`.
- `scripts/sdgp_merge_v7_completion_outputs.py` — merges JSONL completion overlays produced by subagents, then validates with `audit_case_completeness()` + `Checker(require_training_schema=True)` before writing to the vault.
- `scripts/sdgp_merge_v7_outputs.py` — V7 merge now rejects schema-thin rows by default via `Checker(require_training_schema=True)`. Use `--allow-thin` only for legacy diagnostics.
- `scripts/sdgp_prepare_v7_generation_batches.py` — gap-ranked V7 expansion batch builder for subagents. Uses `GapDetector`, reserves existing vault IDs and pending batch IDs, and subtracts pending unmerged slots from coverage counts so parallel workers do not overfill the same cells.
- `scripts/sdgp_merge_v7_generation_jsonl.py` — strict JSONL merge path for subagent-generated expansion batches. Requires exact batch ID-set coverage, `Checker(require_training_schema=True)`, and dedup checks before vault writes.
- `scripts/sdgp_v7_qa_audit.py` — V7 release-candidate QA artifact builder. Emits duplicate/leakage reports, query-grouped split assignments, a blind-label queue without gold labels, and a gold-label manifest for later disagreement scoring.
- `scripts/sdgp_run_blind_label.py` — provider-backed runner for `blind_label_queue.jsonl`. Supports LM Studio, Ollama, file handoff, stub smoke tests, resume mode, and health checks. Default output: `data/sdgp_v7_qa/blind_label_predictions.jsonl`.
- `scripts/sdgp_score_blind_labels.py` — joins prediction rows to `blind_label_manifest.jsonl` and emits `blind_label_score_summary.json`, `blind_label_score_report.md`, `blind_label_assessments.jsonl`, `blind_label_disagreements.jsonl`, and `blind_label_review_queue.jsonl`.
- `scripts/sdgp_promote_evaluation_fields.py` — promotes legacy evaluator fields into canonical `evaluation` and strips duplicate aliases from the vault.
- `scripts/sdgp_prepare_evaluation_field_batches.py` — prepares subagent batches for V7 TRUSTWORTHY rows missing evaluator quality constraints.
- `scripts/sdgp_merge_evaluation_field_outputs.py` — validates and merges subagent-produced evaluator constraints into the vault.
- `scripts/sdgp_upload_v7_hf.py` — stages and publishes cleaned V7 to Hugging Face as Parquet. Default config is `v7` with query-grouped `train` / `validation` / `test`; compatibility configs are `tier1_core`, `tier0_sanity`, and `validation`.

**Coverage as of 2026-05-24** (after V7 expansion + evaluator unification + triage repair + cross-label query review + HF publish):
- 10,500 cases = 2,980 v6 + 7,520 v7. Target 25/cell is complete across all 378 primary cells; target 30/cell has 20 / 378 cells at target and a remaining gap of 1,575.
- V7 training-schema completeness is complete: strict audit shows **7,520/7,520 V7 rows complete**. Canonical evaluator fields are also complete: **10,500/10,500 rows** have `evaluation`, and **0** V6/V7 TRUSTWORTHY rows are missing answer-quality constraints. Do not add new primary domains to V7; domain-focused expansions such as automotive/ECU test analysis are deferred to V8.
- V7 is published on Hugging Face as `yafitzdev/fitz-gov` v7.0.0, commit `c41e5aa113699273240c6cc5ab2e8357c6d518cd`, tag `v7.0.0`. The default `v7` config is query-grouped and leakage-safe: train=8,400 / validation=1,050 / test=1,050. QA audit artifacts exist under `data/sdgp_v7_qa/`: `blind_label_queue.jsonl` has 7,520 V7 rows for an independent labeler; duplicate reports list 562 exact-query duplicate groups and 218 cross-label exact-query groups. Cross-label semantic review passed: 0 cross-label pairs have the same exact context set, and the only shared-context pair was adjudicated valid because the DISPUTED row adds a contradictory second source.
- Blind-label QA with LM Studio `qwen3.6-35b-a3b`: full second-pass coverage is **7,520/7,520 V7 rows**, with **7,520 validated / 0 triage** after strict-prompt recheck and repair. The original full pass flagged 842 rows; resolution path was 362 fixed by stricter prompt/parser recheck, 389 by repair pass 1, 52 by repair pass 2, 21 by repair pass 3, and 18 by final manual holdout repair. `data/sdgp_v7_qa/training_excluded_triage_case_ids.txt` is now empty. Global summary is `data/sdgp_v7_qa/blind_label_global_summary.json`; final resolution ledger is `data/sdgp_v7_qa/blind_label_final_resolution_ledger.jsonl`.
- Remaining pyrrho-side work: train/evaluate `pyrrho-nano-g2` on the published V7 contract, then decide whether to run `small-g2`. The previous 842-row human-triage blocker, cross-label exact-query review blocker, and final export/publish blocker are closed.
- Biggest remaining target-30 coverage gaps: `history_geography` (235), `law_policy` (232), `culture_society` (232), `technology_computing` (228), `general_commonsense` (226), `economics_finance` (225), `science_medicine` (197).

**Legacy fields:** the local V7 candidate vault has been unified. Canonical consumers should read `evaluation`, `governance.*`, `meta.*`, `taxonomy.*`, `routing.*`, and `input.*`. The old V6 `meta.v51_legacy` block and early V7 compatibility aliases were removed after promoting useful evaluator fields into `evaluation`: `evaluation_config` -> `evaluation.{mode,check_mode_match,config}`, plus `required_elements`, `forbidden_claims`, and `forbidden_elements`. Old `description`, `rationale`, `detection_labels`, provenance, and sparse metadata aliases are superseded by V6/MoE canonical fields.

Test suite: `tests/sdgp/` covers all SDGP modules (264 tests as of 2026-05-23). Run via `pytest tests/sdgp/ -q`.

Still to build (lower priority — operational quality, not on the critical path to V7):
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
