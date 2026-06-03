# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- Added draft V8.2 retrieval-control schema in `docs/V8_2_RETRIEVAL_CONTROL_SCHEMA.md`, defining `routing.retrieval_control` labels for retrieval action, gap type, answerability shape, preferred retrieval modality, and evidence failure severity.
- Started the V8.2 subagent enrichment pilot with 18 gpt-5.4-labeled rows across ABSTAIN, DISPUTED, and TRUSTWORTHY examples. Pilot labels are staged locally at `data/_workspaces/retrieval_control_v8_2/pilot_subagent_labels.jsonl` and validate cleanly for enum/range/shape.

### Changed

- Removed `data/fitz-gov/v8_manifest.jsonl` as a canonical local artifact; `data/fitz-gov/cases.jsonl` is now the single row source, and V8-only indexes should be derived from it when needed.
- Removed obsolete top-level `find_duplicate_queries.py`; duplicate-query audits now live in the SDGP QA tooling instead of a hardcoded legacy V5 helper.

---

## [8.1.0] - 2026-06-02

### Added

- Added V8.1 query-contract annotations to all 24,592 canonical rows under `routing.query_contract`, labeled from query text by six Codex subagent shards. Counts: `evidence_sufficiency` 11,828; `structured_lookup` 7,048; `temporal_grounding` 3,249; `exhaustive_coverage` 1,657; `comparison_coverage` 532; `representative_overview` 278.
- Published Hugging Face dataset `yafitzdev/fitz-gov` **v8.1.0** at commit `8023af209379e5e07145f5ae748b9c8f6a80e0be`, tag `v8.1.0`. The row set, labels, and query-grouped splits are unchanged from V8.0.1; public rows now expose `routing.query_contract`.

---

## [8.0.1] - 2026-05-27

### Added

- Added row-level `meta.modality` support for future unstructured / structured / code governance splits, including validation, generator prompt constraints, and modality diagnostic batch prep.

### Changed

- Backfilled the current local fitz-gov data bundle as `meta.modality: "unstructured"` and documented `data/fitz-gov/` as the canonical local data access point.
- Published Hugging Face dataset `yafitzdev/fitz-gov` **v8.0.1** at commit `0d01bb999e80e4c6b01027763b054b4aa48d2334`, tag `v8.0.1`. The row set, labels, and query-grouped splits are unchanged from V8.0.0; the public rows now expose `meta.modality`.
- Clarified the Hugging Face dataset card language for V8.0.0 so the public README explains the benchmark in plain terms instead of using internal SDGP shorthand or pyrrho project cross-promo. Card-only HF commit: `be6bddaa39d6f87d0301e1358b9a1c4ab3329ca2`.

---

## [8.0.0] - 2026-05-26

### Added

- Added `docs/V8_SCHEMA_CONTRACT.md` and `AGENTS.md` to pin the V8 data rule: keep the current V7.0.1 SDGP row shape, no legacy shims, no compatibility configs, no subpattern fields, and no `meta.introduced_in`.
- Added five V8 taxonomy gaps as first-class primary patterns: `resolved_candidate_selection`, `verdict_conflict`, `authority_status_conflict`, `version_build_mismatch`, and `missing_execution_result`.
- Added `docs/V8_TAXONOMY_EXPANSION_PLAN.md` and `scripts/sdgp_plan_v8_taxonomy_expansion.py`, enumerating 105 new primary cells across the existing 7 primary domains and 3 difficulties.
- Added V8 generation/merge helpers: `scripts/sdgp_prepare_v8_generation_batches.py` and `scripts/sdgp_merge_v8_generation_jsonl.py`.
- Added `scripts/sdgp_generate_v8_template_outputs.py` and used it for the V8 target-fill/template repair passes.
- Added `docs/SDGP_TESTCASE_ADDITION_CYCLE.md`, the runbook for adding SDGP rows without poisoning the active vault or pyrrho training manifest.
- Added `scripts/sdgp_build_blind_label_from_generation_jsonl.py` so generated candidate rows can be blind-label QAed before being merged into the active vault.
- Added `scripts/sdgp_upload_v8_hf.py`, which publishes the one-config V8 Hugging Face dataset as Parquet and checks the final V8 release gates before upload.
- Added V8 blind-label QA artifacts under `data/sdgp_v8_qa/`, including the stopped LM Studio partial, all-Claude/Codex replacement predictions, repaired-row recheck, final full second-pass score, manifests, split assignments, and audit reports.
- Updated the training-schema completeness gate so current rows and future V8 rows require the canonical `evaluation` block and accept `meta.dataset_version: "v8"`.

### Changed

- Published Hugging Face dataset `yafitzdev/fitz-gov` **v8.0.0** at commit `56ec1016fbaf8f7a2c488eeb8952b28a75c111c3`, tag `v8.0.0`. The default public config is now `v8`.
- Public V8.0.0 has **24,592 rows**: V6 **2,980**, V7 **7,520**, V8 **14,092**.
- Default query-grouped splits are train **19,674**, validation **2,459**, test **2,459**, with **0 query-group leakage**.
- Whole-dataset target **50/cell** coverage is complete across all **483/483** canonical generation cells with **0** remaining gap.
- Strict V8 training-schema audit is **14,092/14,092 complete** with **0** issue paths.
- Full all-Claude/Codex V8 second-pass blind-label QA is **14,092/14,092 agreement** with **0 missing / 0 invalid / 0 error / 0 triage** after repairing 87 false-trustworthy rows from the hard V8-gap slice.
- Public rows strip local `_vault` provenance and the legacy report axes `meta.domain`, `meta.subcategory`, `meta.reasoning_type`, `meta.query_type`, `meta.evidence_pattern`, and `source_type`.
- Changed blind-label runner defaults to `max_tokens=2048` and `request_timeout_s=300` for the current Qwen thinking-model QA path. A 2026-05-25 config probe reproduced the old failure (`max_tokens=128` -> **0/3 scored, 3 invalid**) and verified the corrected parse budget (`max_tokens=2048` -> **3/3 scored, 0 invalid**).
- Repaired and merged the Claude handoff, target-40, and target-50 packs into the active vault. The active V8 cohort is now **14,092** rows and supersedes the older 525-row, 840-row, and 4,200-row local V8 checkpoints.

---

## [7.0.1] - 2026-05-24

### Changed

- Republished V7 as a schema-clean public contract with the same 10,500 rows, labels, and query-grouped splits as V7.0.0.
- Removed pre-SDGP report axes from public rows: `meta.domain`, `meta.subcategory`, `meta.reasoning_type`, `meta.query_type`, and `meta.evidence_pattern`.
- Removed V5/V6 compatibility configs from the Hugging Face dataset card/export path; the public config is now the canonical `v7` split set.
- Updated the strict training-schema completeness gate to use SDGP canonical fields instead of requiring old report axes.

---

## [7.0.0] - 2026-05-24

### Added

- Strict V7 training-schema audit tooling:
  - `fitz_gov.sdgp.completeness`
  - `scripts/sdgp_audit_training_schema.py`
- V7 schema-completion workflow:
  - `fitz_gov.sdgp.v7_completion`
  - `scripts/sdgp_complete_v7_schema.py`
  - `scripts/sdgp_merge_v7_completion_outputs.py`
- Tests for training-schema completeness and V7 completion merge logic.
- Local V7 vault schema completion: all 1,400 V7 rows now pass the strict rich V6/MoE training-schema audit.
- Local V7 expansion to the 10.5k target: vault is now **10,500 rows** total (**2,980 V6 + 7,520 V7**) with strict training-schema completeness at **7,520/7,520 V7 rows**.
- Target 25/cell coverage is complete across all **378/378** primary taxonomy cells; target 30/cell remains a future stretch target with 1,575 rows of gap.
- Gap-ranked subagent expansion tooling:
  - `scripts/sdgp_prepare_v7_generation_batches.py`
  - `scripts/sdgp_merge_v7_generation_jsonl.py`
- V7 QA audit tooling:
  - `fitz_gov.sdgp.qa`
  - `scripts/sdgp_v7_qa_audit.py`
  - `tests/sdgp/test_qa.py`
- V7 blind-label execution and scoring tooling:
  - `fitz_gov.sdgp.blind_label`
  - `scripts/sdgp_run_blind_label.py`
  - `scripts/sdgp_score_blind_labels.py`
  - `tests/sdgp/test_blind_label.py`
- Canonical evaluator-field unification tooling:
  - `fitz_gov.sdgp.evaluation_fields`
  - `fitz_gov.sdgp.evaluation_completion`
  - `scripts/sdgp_promote_evaluation_fields.py`
  - `scripts/sdgp_prepare_evaluation_field_batches.py`
  - `scripts/sdgp_merge_evaluation_field_outputs.py`
  - `tests/sdgp/test_evaluation_fields.py`
- Coverage snapshots for expansion milestones:
  - `data/sdgp_handoff_v7_expand/coverage_target1_5520.md`
  - `data/sdgp_handoff_v7_expand/coverage_target2_6510.md`
  - `data/sdgp_handoff_v7_expand/coverage_target3_7500.md`
- Final local coverage reports:
  - `data/sdgp_vault_v51_enriched/coverage_report_v7_target25.md`
  - `data/sdgp_vault_v51_enriched/coverage_report_v7_target30.md`
- V7 QA artifacts:
  - `data/sdgp_v7_qa/summary.json`
  - `data/sdgp_v7_qa/report.md`
  - `data/sdgp_v7_qa/query_duplicate_groups.jsonl`
  - `data/sdgp_v7_qa/cross_label_query_groups.jsonl`
  - `data/sdgp_v7_qa/split_assignments.jsonl`
  - `data/sdgp_v7_qa/blind_label_queue.jsonl`
  - `data/sdgp_v7_qa/blind_label_manifest.jsonl`
- Initial 50-row V7 blind-label pilot artifacts:
  - `data/sdgp_v7_qa/pilots/20260522_initial50_qwen36_35b_a3b/pilot_assessment.md`
  - `data/sdgp_v7_qa/pilots/20260522_initial50_qwen36_35b_a3b/blind_label_validated.jsonl`
  - `data/sdgp_v7_qa/pilots/20260522_initial50_qwen36_35b_a3b/blind_label_triage.jsonl`
  - `data/sdgp_v7_qa/blind_label_second_pass_ledger.jsonl`
- Second 100-row V7 blind-label pilot artifacts:
  - `data/sdgp_v7_qa/pilots/20260523_next100_qwen36_35b_a3b/pilot_assessment.md`
  - `data/sdgp_v7_qa/pilots/20260523_next100_qwen36_35b_a3b/blind_label_validated.jsonl`
  - `data/sdgp_v7_qa/pilots/20260523_next100_qwen36_35b_a3b/blind_label_triage.jsonl`
- Full remaining-row blind-label run artifacts:
  - `data/sdgp_v7_qa/pilots/20260523_remaining7370_qwen36_35b_a3b/blind_label_sample.jsonl`
  - `data/sdgp_v7_qa/pilots/20260523_remaining7370_qwen36_35b_a3b/blind_label_predictions.jsonl`
  - `data/sdgp_v7_qa/pilots/20260523_remaining7370_qwen36_35b_a3b/blind_label_predictions_combined.jsonl`
  - `data/sdgp_v7_qa/pilots/20260523_remaining7370_qwen36_35b_a3b/blind_label_retry_predictions_max1024.jsonl`
  - `data/sdgp_v7_qa/pilots/20260523_remaining7370_qwen36_35b_a3b/blind_label_retry2_predictions_max2048.jsonl`
- Global blind-label bucket artifacts:
  - `data/sdgp_v7_qa/blind_label_global_summary.json`
  - `data/sdgp_v7_qa/blind_label_validated_case_ids_all.txt`
  - `data/sdgp_v7_qa/blind_label_triage_case_ids_all.txt`
  - `data/sdgp_v7_qa/training_excluded_triage_case_ids.txt`
- V7 triage repair workflow and artifacts:
  - `scripts/sdgp_repair_v7_triage_cases.py`
  - `data/sdgp_v7_qa/triage_recheck_20260523/`
  - `data/sdgp_v7_qa/triage_repair_20260523*/`
  - `data/sdgp_v7_qa/triage_repair_20260523_final/`
  - `data/sdgp_v7_qa/blind_label_final_resolution_ledger.jsonl`
  - `data/sdgp_v7_qa/training_schema_after_final_triage_repair.json`
- V7 cross-label exact-query semantic review tooling and artifacts:
  - `scripts/sdgp_review_cross_label_queries.py`
  - `data/sdgp_v7_qa/cross_label_query_semantic_review_summary.json`
  - `data/sdgp_v7_qa/cross_label_query_semantic_review_candidates.jsonl`
  - `data/sdgp_v7_qa/cross_label_query_semantic_review_adjudications.jsonl`
  - `data/sdgp_v7_qa/cross_label_query_semantic_review.md`
- V7 Hugging Face publish tooling:
  - `scripts/sdgp_upload_v7_hf.py`
  - Default HF config `v7` with query-grouped `train` / `validation` / `test` Parquet splits.
  - Compatibility HF configs: `tier1_core`, `tier0_sanity`, and `validation`.
- Canonical evaluator-field batch artifacts under `data/sdgp_handoff_evaluation_fields/` for all 2,348 V7 TRUSTWORTHY rows.

### Changed

- V7 generator prompt now requests complete V7 training rows instead of treating rich V6/MoE fields as optional.
- `scripts/sdgp_generate.py` and `scripts/sdgp_merge_v7_outputs.py` now reject schema-thin V7 rows by default via `Checker(require_training_schema=True)`. `--allow-thin` remains available for legacy diagnostics.
- V7 completion overlay merge now rejects duplicate case IDs and backfills legacy `governance.*_score` probability aliases into the canonical `governance.{abstain,disputed,trustworthy}` triplet.
- Vault rewrites retry transient Windows `PermissionError` failures around atomic replace with a longer retry window.
- The local V7 candidate vault now uses one canonical evaluator field block: `evaluation.{mode,check_mode_match,required_elements,forbidden_claims,forbidden_elements,config}`.
- Duplicate legacy/compatibility fields were removed from the local vault after promotion: `meta.v51_legacy`, root evaluator fields, root `conflict_density` / `evidence_sufficiency` / `near_miss_class`, `governance.*_score`, misplaced `grounding_targets`, and sparse old metadata aliases.
- `scripts/sdgp_merge_evaluation_field_outputs.py` now indexes vault cases once instead of scanning the JSONL once per overlay.
- V7 expansion batch preparation now accounts for pending, unmerged batch specs when ranking gaps, preventing parallel workers from repeatedly reserving the same sparse cells before merges land.
- V7 JSONL generation merge now reports checker failures via `CheckIssue.rule` instead of crashing while formatting a rejected row.
- V7 scope decision: keep the existing 7-domain taxonomy at the reached 10,500-row target; defer new primary domains and domain-focused packs, including automotive/ECU test analysis, to V8.
- V7 QA split decision: use query-grouped split assignments before training to prevent repeated-query leakage across train/validation/test. Current generated split is train=8,400 / validation=1,050 / test=1,050 with 0 query-group leakage.
- V7 blind-label decision: keep gold labels in `blind_label_manifest.jsonl` only; provider predictions are written separately to `blind_label_predictions.jsonl`, then joined by the scorer into disagreement/review queues.
- V7 blind-label pilot result: `qwen3.6-35b-a3b` validated 46 / 50 random sampled rows. The 4 triage rows are all `scope_conflict` cases where the local model treats scoped/conditional evidence as TRUSTWORTHY rather than DISPUTED.
- V7 blind-label pilot cumulative result after the second pilot: **150 unique rows audited**, **137 validated**, **13 triage**. The second 100-row pilot validated 91 / 100; manual read suggests 8 / 9 triage rows are legitimate dataset/convention flags and 1 is a Qwen temporal-staleness miss.
- V7 evaluator unification result: **10,500/10,500** vault rows have canonical `evaluation`; **2,348/2,348** V7 TRUSTWORTHY rows received quality constraints; **0** V6/V7 TRUSTWORTHY rows are missing evaluator quality constraints; strict V6/V7 training-schema audit remains clean.
- Full V7 blind-label result: **7,520/7,520** V7 rows ledgered; **6,678 validated / 842 triage**. The full 7,370-row pass required retrying truncated outputs with higher token budgets (`max_tokens=1024`, final 21 at `2048`) because `128` tokens produced mostly prose truncated before JSON.
- V7 blind-label triage result after repair: **7,520/7,520 validated / 0 triage**. The original 842-row triage queue was resolved via stricter validator prompt/parser repair (**362**), provider-authored row repairs validated by recheck (**389 + 52 + 21** across three passes), and final manual holdout repairs (**18**). `training_excluded_triage_case_ids.txt` is now empty. Post-repair strict schema audit remains **V6 2,980/2,980 complete** and **V7 7,520/7,520 complete**.
- V7 QA duplicate counts improved slightly after repair: exact-query duplicate groups **581 → 562**, cross-label exact-query groups **219 → 218**, with **0** duplicate IDs, exact inputs, checker hashes, or query-group split leakage.
- V7 cross-label exact-query semantic review passed across the full 10,500-row vault: **218** cross-label exact-query groups / **921** rows, **0** cross-label pairs with the same exact context set, **1** shared-context pair manually adjudicated valid, **0** unresolved review pairs. Repeated raw queries are intentionally allowed when retrieved contexts differ; the release blocker is materially equivalent evidence with different labels.
- V7.0.0 published to Hugging Face at `yafitzdev/fitz-gov`, commit `c41e5aa113699273240c6cc5ab2e8357c6d518cd`, tag `v7.0.0`. Published files are Parquet to avoid brittle nested-schema inference from chunked JSONL loading.
- Blind-label parser now avoids treating allowed-label setup text like "label should be ABSTAIN, DISPUTED, or TRUSTWORTHY" as an ABSTAIN prediction and accepts explicit decision phrasing such as "DISPUTED is appropriate."

---

## [6.0.0] - 2026-05-20

### LLM-Enriched Schema (SDGP Phase 0b + 0c)

All 2,980 cases annotated with V6 fields via Sonnet 3.7 subagents and Qwen3-35B / Qwen3-27B (LM Studio).
No case IDs changed; this is a schema overlay on V5.1.

**Phase 0b — Core governance signals (every case):**

| Field | Location | Description |
|---|---|---|
| `query_rewritten` | `input` | Semantically equivalent query re-expressed for retrieval clarity |
| `summary` | `input.contexts[]` | One-sentence LLM summary of the context chunk |
| `relevance_to_query` | `input.contexts[]` | 0–1 float relevance to the query |
| `anchor_period` | `input.contexts[].temporality` | Detected temporal anchor (e.g. "2023 Q4") |
| `hallucination_pressure` | `governance` | 0–1 — how strongly this query pattern invites confabulation |
| `retrieval_retry_value` | `governance` | 0–1 — expected gain from better retrieval |
| `query_evidence_alignment` | `governance` | 0–1 — semantic overlap between query and contexts |
| `answer_coverage` | `governance` | 0–1 — fraction of query answerable from contexts |
| `distance` | `governance.boundary_proximity` | Distance from decision boundary to nearest other class |
| `near_miss_reason` | `meta` | Plain-English explanation of why this case could fool a model |

**Phase 0c — Multi-task MoE training ground truth:**

| Field | Location | Description |
|---|---|---|
| `boundary_quality` | `input.contexts[]` | 0–1 chunk-cut quality (1.0 = clean sentence boundary, 0.3 = hard mid-sentence cut) |
| `evidence_bias_score` | `governance` | 0–1 source one-sidedness (0 = balanced, 1 = single perspective) |
| `evidence_chain` | `input` | `{order, reasoning}` — chunk consumption order + one-sentence rationale; multi-chunk cases only |
| `grounding_targets` | `meta` | `{gold_answer, sentences: [{text, attributions}]}` — TRUSTWORTHY cases only; per-sentence chunk attributions |

**Schema additions:**

- Top-level `label` field (lowercase: `abstain` / `disputed` / `trustworthy`) for quick consumption
- Top-level `tier` field (0 or 1)
- `taxonomy.{governance_class, pattern, cell_id}` — cell-targeted generation taxonomy

**HF dataset:** Published at `yafitzdev/fitz-gov` (three configs: `tier1_core`, `tier0_sanity`, `validation`). 16.4 MB of JSONL.

**No breaking changes** — all V5.1 fields preserved under their original keys; V6 fields are additive.

---

## [5.1.0] - 2026-03-01

### 🔧 Data Fixes

- **Relabeled 199 trustworthy-with-gap cases** to abstain — cases where context had insufficient evidence were incorrectly labeled as trustworthy
- **Removed 10 mislabeled single-context dispute cases** — disputes require multiple sources; single-context cases cannot be genuine disputes
- **Fixed 51 broken queries** across the dataset
- Updated test suite to match new labels

### 📚 Documentation Refresh

- **README.md**: Redesigned with centered header, badges, hero code snippet, collapsible sections, Mermaid evaluation flow diagram, and "About" section
- **docs/evaluation-guide.md**: Full rewrite for v5 — 4 categories, cross-cutting quality checks, updated counts/difficulty/FAQ, Mermaid per-case evaluation diagram
- **docs/mode-decision-tree.md**: Updated category names (qualification → trustworthy_hedged, confidence → trustworthy_direct), rewrote grounding/relevance as cross-cutting checks, added v5.0.0 version history entry
- **docs/GOVERNANCE_CASE_TAXONOMY.md**: Updated version to 5.0.0, case counts to current values, removed hardcoded Windows path and broken link
- **CHANGELOG.md**: Restored emoji consistency on v4.0–v5.0 subsection headers
- **CLAUDE.md**: Updated to reflect v5.0.0 architecture
- **Archived** completed `docs/v5-plan/` and `docs/roadmap/PROPOSAL_MULTI_SOURCE_TESTS.md` to `docs/roadmap/archive/`

### 📊 Data Corrections

- Fixed stale trustworthy_hedged difficulty breakdown (435/725 → 428/732 medium/hard) in README and CHANGELOG

---

## [5.0.0] - 2026-02-15

### 🎉 Highlights

**Grounding & Relevance Are Now Cross-Cutting Quality Checks** - Eliminated grounding and relevance as standalone categories. They are now quality dimensions applied to every trustworthy case (hedged and direct). Each trustworthy case now produces three scores: governance mode accuracy, grounding (did the response avoid hallucination?), and relevance (did the response address the question?). The benchmark drops from 6 categories to 4, with no data loss -- all 2,980 cases preserved.

### ⚠️ Breaking Changes

- **Removed `FitzGovCategory.GROUNDING` and `FitzGovCategory.RELEVANCE`** enum values
- **4 categories only**: abstention, dispute, trustworthy_hedged, trustworthy_direct
- `grounding.json` and `relevance.json` data files no longer exist (merged into `trustworthy_hedged.json`)
- `FitzGovCaseResult` has new fields: `mode_correct`, `grounding_passed`, `relevance_passed`, `grounding_failure`, `relevance_failure`
- `FitzGovCategoryResult` has new fields: `grounding_accuracy`, `relevance_accuracy`
- Score comparisons between v4.1 and v5.0 are NOT directly comparable due to structural changes

### 📊 Data Migration

- **676 grounding/relevance cases** converted to trustworthy_hedged with prefixed subcategories (`grounding_*`, `relevance_*`)
- **884 existing trustworthy cases** enriched with `forbidden_claims` and `required_elements` annotations
- All trustworthy cases (1,560 tier1 + 36 tier0) now have both quality annotation fields
- Trustworthy Hedged tier1: 484 → 1,160 cases (absorbed 336 grounding + 340 relevance)
- Trustworthy Direct: unchanged at 400 tier1 / 10 tier0
- All existing case IDs preserved

### 🔧 Evaluation Changes

- **Unified evaluation flow**: All categories use governance mode classification. Trustworthy categories additionally run grounding and relevance quality checks when mode is correct.
- **Quality checks are conditional**: If the system picks the wrong governance mode, quality checks are skipped (no point checking answer quality when the meta-decision is wrong)
- **3-dimensional scoring** for trustworthy categories:
  ```
  trustworthy_hedged: 71.2% (826/1160)  |  grounding: 89.3%  relevance: 85.1%
  trustworthy_direct: 78.5% (314/400)   |  grounding: 92.1%  relevance: 88.7%
  ```
- **No LLM-as-judge**: Quality checks use regex-only validation (optional LLM validation still supported)
- All 4 categories participate in the confusion matrix

### 🆕 Quality Annotation Details

- **Hedged cases**: `forbidden_claims` catch hallucinated specifics (dollar amounts, percentages, dates not in context); `required_elements` require hedging language appropriate to subcategory
- **Direct cases**: `forbidden_claims` catch unsupported embellishments; `required_elements` require key factual terms from context
- Annotations are subcategory-aware (e.g., `causal_uncertainty` cases require correlation/confounding language)

### 📊 Distribution (Tier 1)

| Category | Cases | Medium | Hard | Med % |
|----------|------:|-------:|-----:|------:|
| Trustworthy Hedged | 1,160 | 428 | 732 | 37% |
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

### 🆕 Subcategories (Trustworthy Hedged)

57 subcategories after merge:
- **20 original hedged**: evidence_quality, hedged_evidence, different_aspects, causal_uncertainty, mixed_evidence, temporal_uncertainty, version_overlap, methodology_difference, stale_source, evolving_facts, entity_ambiguity, partial_answer, scope_condition, numerical_near_miss, cross_source_partial, implicit_assumptions, adjacent_entity, cross_domain_transfer, hedged_contradiction_corroborated, different_framing
- **18 from grounding**: grounding_numerical_hallucination, grounding_attribution_hallucination, grounding_temporal_confusion, grounding_entity_blending, grounding_process_hallucination, grounding_quote_fabrication, grounding_statistical_inference, grounding_code_hallucination, grounding_table_inference, grounding_causal_hallucination, grounding_comparative_hallucination, grounding_geographic_hallucination, grounding_technical_hallucination, grounding_date_hallucination, grounding_location_hallucination, grounding_code_grounding, grounding_medical_hallucination, grounding_quote_extension
- **19 from relevance**: relevance_partial_answer, relevance_wrong_entity_focus, relevance_temporal_mismatch, relevance_tangent_drift, relevance_related_but_different, relevance_over_answering, relevance_granularity_mismatch, relevance_prerequisite_missing, relevance_scope_mismatch, relevance_format_mismatch, relevance_summarization_vs_answer, relevance_cherry_picking, relevance_false_precision, relevance_assumption_injection, relevance_symptom_only, relevance_status_dump, relevance_feature_dump, relevance_instruction_only, relevance_metric_avoidance

### 📦 Migration Notes

- `pip install fitz-gov==5.0.0` to upgrade
- Remove any references to `FitzGovCategory.GROUNDING` or `FitzGovCategory.RELEVANCE`
- `GOVERNANCE_MODE_CATEGORIES` and `ANSWER_QUALITY_CATEGORIES` constants removed; use `TRUSTWORTHY_CATEGORIES` instead
- Case IDs unchanged -- grounding/relevance case IDs still work with `load_case_by_id()`
- `evaluate_case()` now returns richer results with quality check fields

---

## [4.1.0] - 2026-02-15

### 🎉 Highlights

**Benchmark Credibility Hardening** - From 2,488 to 2,980 test cases (60 tier0 + 2,920 tier1). Addressed five structural gaps that would undermine credibility with serious benchmark consumers: expanded trustworthy_direct from 218 to 400 cases, added 310 medium-difficulty cases across 5 categories, expanded multi-source cases from 138 to 264, eliminated all "general" domain cases, and added a 250-case human validation sample with annotation guide.

### 📊 Data Expansion

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

### 🆕 New Features

- **Human validation sample** (`data/validation/human_validation_sample.json`):
  - 250 cases stratified by category, difficulty, and domain (seed=42)
  - Null-initialized annotator fields for inter-annotator agreement (IAA) studies
  - Gold labels mapped from categories (abstention->abstain, dispute->disputed, etc.)
- **Annotation guide** (`docs/ANNOTATION_GUIDE.md`):
  - Decision tree for TRUSTWORTHY vs DISPUTED vs ABSTAIN classification
  - 6 worked examples (2 per mode) with query, context, label, and reasoning
  - Edge case documentation for common confusion points
  - Cohen's kappa interpretation guide

### 🆕 New Subcategories

- **Trustworthy Direct**: `step_by_step` (13 cases) - procedural answers with clear steps, `definitional` (13 cases) - clear term/concept definitions
- All existing subcategories expanded proportionally with new medium-difficulty cases

### 📦 Corpus & Infrastructure

- **5,043 corpus documents** (up from 4,271), 772 new documents from expanded cases
- **3,800 query mappings** (up from 3,248), 552 new mappings
- **Manifest updated** to v4.1.0 with accurate domain counts
- **README rewritten** with comprehensive statistics: categories, modes, difficulty, domains, query types, source types, reasoning types, evidence patterns, context counts, and all 113 subcategories

### 📊 Distribution (Tier 1)

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

### 📦 Migration Notes

- All existing case IDs preserved
- 17 field value corrections: 3 invalid domains, 11 invalid reasoning_types, 3 invalid evidence_patterns
- 4 tier0 subcategory merges (sparse into established subcategories)
- Score comparisons between v4.0 and v4.1 are NOT directly comparable due to case count and difficulty distribution changes
- `pip install fitz-gov==4.1.0` to upgrade

---

## [4.0.0] - 2026-02-12

### 🎉 Highlights

**Massive Benchmark Expansion** - From 1,173 to 2,114 test cases (60 tier0 + 2,054 tier1). Added 364 medium-difficulty cases (25% of tier1), expanded grounding from 34 to 271 cases and relevance from 32 to 275 cases with hand-written rich content, added 6 classification attributes to every case for results slicing.

### 📊 Data Expansion

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

### 🆕 New Features

- **6 classification attributes** on every case for results slicing:
  - `domain` (18 values), `query_type` (10 values), `source_type`, `context_count`, `reasoning_type` (6 values), `evidence_pattern` (6 values)
- **Evaluator classification breakdowns** - `Tier1Result` includes `domain_breakdown`, `query_type_breakdown`, `source_type_breakdown`, `reasoning_type_breakdown`, `evidence_pattern_breakdown`
- **CLI `--breakdown` flag** - `python -m fitz_gov.cli stats --data-dir data --breakdown` shows distribution by domain, query type, etc.
- **Comprehensive test suite** - 103 tests covering models, loader, evaluator, data integrity, validation, CLI

### 🔧 Code Quality

- Removed dead `schema.py` (duplicate of `models.py`)
- Fixed `__init__.py` version (was stuck at 3.0.0)
- Removed unused `Callable` import from evaluator
- Fixed 107 `context_count` mismatches in grounding/relevance data
- Fixed stale docstrings in generator.py referencing old category names

### 📊 Distribution

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

### 📦 Migration Notes

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

[Unreleased]: https://github.com/yafitzdev/fitz-gov/compare/v8.1.0...HEAD
[8.1.0]: https://huggingface.co/datasets/yafitzdev/fitz-gov/tree/v8.1.0
[8.0.1]: https://huggingface.co/datasets/yafitzdev/fitz-gov/tree/v8.0.1
[8.0.0]: https://huggingface.co/datasets/yafitzdev/fitz-gov/tree/v8.0.0
[7.0.1]: https://huggingface.co/datasets/yafitzdev/fitz-gov/tree/v7.0.1
[7.0.0]: https://huggingface.co/datasets/yafitzdev/fitz-gov/tree/v7.0.0
[6.0.0]: https://github.com/yafitzdev/fitz-gov/compare/v5.1.0...v6.0.0
[5.1.0]: https://github.com/yafitzdev/fitz-gov/compare/v5.0.0...v5.1.0
[5.0.0]: https://github.com/yafitzdev/fitz-gov/compare/v4.1.0...v5.0.0
[4.1.0]: https://github.com/yafitzdev/fitz-gov/compare/v4.0.0...v4.1.0
[4.0.0]: https://github.com/yafitzdev/fitz-gov/compare/v3.0.0...v4.0.0
[3.0.1]: https://github.com/yafitzdev/fitz-gov/compare/v3.0.0...v3.0.1
[3.0.0]: https://github.com/yafitzdev/fitz-gov/compare/v2.0.0...v3.0.0
[2.0.0]: https://github.com/yafitzdev/fitz-gov/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.com/yafitzdev/fitz-gov/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/yafitzdev/fitz-gov/releases/tag/v1.0.0
