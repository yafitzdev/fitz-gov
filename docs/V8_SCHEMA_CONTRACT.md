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

## Required V8 Workflow

1. Add taxonomy gaps as first-class `TaxonomyPattern` enum values.
2. Keep generated rows on the current SDGP row shape.
3. Generate V8 rows only for the new cells.
4. Re-run checker, training-schema completeness, dedup, leakage, and blind-label
   QA before publishing.
5. Publish `yafitzdev/fitz-gov` with one canonical `v8` config.
