# V8 Unified Dataset Contract

This document is a hard constraint for fitz-gov V8 work.

V8 may add taxonomy coverage and new rows, but it must not introduce legacy
shims, compatibility payloads, or version-specific public schemas.

## Non-Negotiable Rules

1. **No legacy shims.**
   Do not add fields whose only purpose is to keep old V5/V6/V7 reports alive.
   Update tooling to read canonical SDGP fields instead.

2. **Keep the current row shape.**
   The V7.0.1 vault already has one canonical SDGP structure:
   `id`, `version`, `input`, `governance`, `taxonomy`, `routing`, `meta`, and
   `evaluation` plus local `_vault` provenance. V8 expansion rows must use this
   same structure.

3. **Do not add taxonomy shim fields.**
   V8 taxonomy gaps are first-class `taxonomy.pattern` values. Do not add
   `taxonomy.subpattern`, `taxonomy.subpattern_cell_id`,
   `taxonomy.subpattern_description`, `meta.introduced_in`, or equivalent
   side-channel fields unless a future explicit schema version bump is approved.

4. **Existing rows are not rewritten just because taxonomy expands.**
   Adding primary patterns creates new empty cells. Fill those cells with new
   V8 rows. Do not migrate 10,500 existing rows into a new field layout for this
   additive taxonomy expansion.

5. **Use the existing version field.**
   `meta.dataset_version` remains the row cohort marker (`v6`, `v7`, `v8`).
   New V8 rows use `meta.dataset_version: "v8"` and `version:
   "fitz-gov-8.0"`. Older rows keep their existing values.

6. **One public V8 config.**
   The V8 Hugging Face export should expose one canonical config, `v8`, with
   query-grouped `train` / `validation` / `test` splits. Do not publish
   compatibility configs such as `tier1_core`, `tier0_sanity`, `validation`, or
   version-specific configs.

7. **Old report axes stay forbidden.**
   Public rows must not contain pre-SDGP report axes or compatibility aliases:

   - `meta.domain`
   - `meta.subcategory`
   - `meta.reasoning_type`
   - `meta.query_type`
   - `meta.evidence_pattern`
   - `source_type`

## V8 Taxonomy Expansion

The ECU/test-management probe exposed generic governance gaps, not a need for
an automotive-only domain. V8 represents those gaps as primary taxonomy
patterns and expands them across the existing seven primary domains.

| pattern | class | coverage target |
|---|---|---|
| `resolved_candidate_selection` | TRUSTWORTHY | apparent competing candidates, but sources mark the valid one |
| `verdict_conflict` | DISPUTED | same target/check has incompatible final verdicts or statuses |
| `authority_status_conflict` | DISPUTED | raw/intermediate status conflicts with source-of-record status |
| `version_build_mismatch` | ABSTAIN | right family, wrong concrete version/build/platform/jurisdiction/cohort |
| `missing_execution_result` | ABSTAIN | setup/plan/protocol exists, but final result is absent |

Initial expansion plan: 5 new primary patterns x 7 current primary domains x 3
difficulties = **105 new primary cells**. At 5 rows/cell this is a **525-row
probe pack**. Full V7-style parity at 25 rows/cell would be **2,625 rows**.
See `docs/V8_TAXONOMY_EXPANSION_PLAN.md`.

## Current V8 State

As of 2026-05-26 morning, the active local vault is clean and V8.0.0 is
published to Hugging Face:

- Active vault: `data/sdgp_vault_v51_enriched/cases.jsonl`
- Total rows: **24,592** = 10,500 V6/V7 rows + **14,092 V8 rows**
- Hugging Face dataset: `yafitzdev/fitz-gov`
- Public version/tag: **v8.0.0**
- HF data/tag commit: `56ec1016fbaf8f7a2c488eeb8952b28a75c111c3`
- Current HF main commit after public card wording cleanup:
  `be6bddaa39d6f87d0301e1358b9a1c4ab3329ca2`
- Public config: one default config, `v8`
- Public splits: train **19,674** / validation **2,459** / test **2,459**
- Clean V8 manifest:
  `data/sdgp_v8_qa/blind_label_manifest.jsonl`
- Training-schema audit:
  `data/sdgp_v8_qa/training_schema_summary.json` = **14,092/14,092**
  complete
- Whole-dataset target-50 report:
  `data/sdgp_v8_qa/full_dataset_gap_target50_after_merge.json` =
  **483/483** primary cells at target, **0** total gap
- Stricter full V8 second-pass blind QA:
  `data/sdgp_v8_qa/score_claude_full_repaired87_combined_20260526/` =
  **14,092/14,092 agreement**, **0 missing / 0 invalid / 0 error**,
  **0 triage**
- Latest pre-merge backup:
  `data/sdgp_vault_v51_enriched/cases.before_v8_target50_merge_20260526_013413.jsonl`
- Latest repair backup:
  `data/sdgp_vault_v51_enriched/cases.before_v8_second_pass_triage87_repair_20260526_102013.jsonl`

A later Claude-generated candidate expansion was repaired and merged:

`data/sdgp_handoff_v8_candidate_20260525_claude_expand/`

Raw intake at 18:56 Europe/Berlin showed:

- Main output files observed: **89** `batch_*.jsonl`
- Raw output lines observed: **2,646**
- Parseable unique candidate IDs observed: **2,643**
- Duplicate candidate IDs observed: **0**
- Assigned slots still missing: **717** of 3,360
- Malformed/non-UTF8 output files under strict merge parsing: **4**
- Parsed rows missing core classification/domain/difficulty fields: **15**
- Fast structural dry-run result: **1,915 accepted / 0 existing / 624
  rejected**. The dominant rejection bucket is training-schema incompleteness
  (missing TRUSTWORTHY `meta.grounding_targets`, invalid `meta.category` such
  as `trust`/`abstain`, invalid abbreviated cell IDs, and invalid domain names
  such as `legal_compliance` or `clinical_evidence`).

The 2026-05-25 evening repair normalized the handoff into:

`data/sdgp_handoff_v8_candidate_20260525_claude_expand/subagent_outputs_normalized/`

Repair result:

- Parsed/recovered candidate rows: **2,646** unique rows from **89** raw output
  files, including the CP1252/non-UTF8 batches and concatenated JSON rows.
- Missing slots filled by deterministic V8 template fallback: **714**.
- Normalized output: **113** `batch_*.jsonl` files / **3,360** rows.
- Structural dry-run: **3,360 accepted / 0 existing / 0 rejected**.
- Offline QA files:
  `data/sdgp_qa_v8_candidate_20260525_claude_expand_normalized/`
- Blind-label pilot: **10/10 agreement**, **0 missing / 0 invalid / 0 error**.
- Codex subagent blind-label QA:
  `data/sdgp_qa_v8_candidate_20260525_claude_expand_normalized/score_codex_subagents_combined/`
  = **3,236/3,360 agreement** (**96.31%**), **124 triage**,
  **0 missing / 0 invalid / 0 error**.

The 124 triage rows were replaced with deterministic V8 template rows at:

`data/sdgp_handoff_v8_candidate_20260525_claude_expand/subagent_outputs_patched_124_template/`

Patched candidate result:

- Structural dry-run: **3,360 accepted / 0 existing / 0 rejected**.
- Candidate QA:
  `data/sdgp_qa_v8_candidate_20260525_claude_expand_patched_124_template/score_codex_subagents_combined/`
  = **3,360/3,360 agreement**, **0 missing / 0 invalid / 0 error**,
  **0 triage**.
- Merge result: **3,360 added / 0 duplicate**, vault size **14,700**.

The 2026-05-26 target-40 pass then added V8 rows for the 18 pre-V8 patterns
that were below whole-dataset 40/cell:

`data/sdgp_handoff_v8_target40/`

Target-40 result:

- Batch specs: **174** files / **5,198** slots.
- Generated outputs: **174** `batch_*.jsonl` files / **5,198** rows.
- Structural dry-run: **5,198 accepted / 0 existing / 0 rejected**.
- Codex subagent blind QA:
  `data/sdgp_qa_v8_target40/score_codex_subagents_combined/` =
  **5,198/5,198 agreement**, **0 missing / 0 invalid / 0 error**,
  **0 triage**.
- Merge result: batch `v8_target40_template_20260526`,
  **5,198 added / 0 duplicate**, vault size **19,898**.

The 2026-05-26 target-50 pass then added V8 rows for all primary cells still
below whole-dataset 50/cell:

`data/sdgp_handoff_v8_target50/`

- Batch specs: **157** files / **4,694** slots.
- Generated outputs: **157** `batch_*.jsonl` files / **4,694** rows.
- Structural dry-run: **4,694 accepted / 0 existing / 0 rejected**.
- Initial Codex subagent blind QA found **82** triage rows; template repairs
  tightened `factual_contradiction`, `numerical_conflict`, and
  `resolved_candidate_selection`.
- Final Codex subagent blind QA:
  `data/sdgp_qa_v8_target50/score_codex_subagents_combined/` =
  **4,694/4,694 agreement**, **0 missing / 0 invalid / 0 error**,
  **0 triage**.
- Merge result: batch `v8_target50_template_20260526`,
  **4,694 added / 0 duplicate**, vault size **24,592**.
- Whole-dataset target-50 report:
  `data/sdgp_v8_qa/full_dataset_gap_target50_after_merge.json` =
  **483/483** primary cells at target, **0** total gap.

The later stricter all-Claude/Codex full V8 second pass initially found **87**
false-trustworthy triage rows in the hard V8-gap slice. Those rows were
repaired in-place with batch marker `v8_second_pass_triage87_repair_20260526`
by making unreconciled conflicts and exact-version evidence gaps explicit:

- Repair backup:
  `data/sdgp_vault_v51_enriched/cases.before_v8_second_pass_triage87_repair_20260526_102013.jsonl`
- Narrow repaired-row blind recheck:
  `data/sdgp_v8_qa/score_second_pass_triage87_repair_only_20260526/` =
  **87/87 agreement**, **0 triage**
- Final full all-Claude/Codex second-pass score:
  `data/sdgp_v8_qa/score_claude_full_repaired87_combined_20260526/` =
  **14,092/14,092 agreement**, **0 missing / 0 invalid / 0 error**,
  **0 triage**

## Required V8 Workflow

1. Add taxonomy gaps as first-class `TaxonomyPattern` enum values.
2. Keep generated rows on the current SDGP row shape.
3. Generate V8 rows only for approved V8 expansion targets: new V8 taxonomy
   cells or explicitly approved additive target-fill rows in existing cells.
4. Re-run checker, training-schema completeness, dedup, leakage, and blind-label
   QA before publishing.
5. Publish `yafitzdev/fitz-gov` with one canonical `v8` config.
