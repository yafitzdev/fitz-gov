# Canonical fitz-gov Data

This directory is the stable local access point for the actual local
fitz-gov dataset.

It contains the current local data files directly:

| File | Purpose |
|---|---|
| `cases.jsonl` | Active local vault containing all 24,592 rows |
| `v8_manifest.jsonl` | Clean V8 split/QA manifest for the 14,092-row V8 cohort |
| `training_schema_summary.json` | V8 training-schema completeness summary |
| `manifest.json` | Human/machine-readable description of this bundle |

All rows in the current local bundle are unstructured-text governance rows and
carry `meta.modality: "unstructured"`. Structured-data and code rows are future
modality slices and must remain in candidate/probe workspaces until QA passes.

## Current Public Contract

- Hugging Face repo: `yafitzdev/fitz-gov`
- Config: `v8`
- Revision/tag: `v8.0.1`
- Rows: `24,592`
- Splits: train `19,674`, validation `2,459`, test `2,459`
- Public row shape: SDGP V8 (`id`, `version`, `input`, `governance`,
  `taxonomy`, `routing`, `meta`, `evaluation`)

Everything under `data/_workspaces/` is generation, QA, publish staging, or
legacy material. It is not the canonical dataset.
