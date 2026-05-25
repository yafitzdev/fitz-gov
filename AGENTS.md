# AGENTS.md — fitz-gov project instructions

Loaded into Codex sessions opened in this repository.

## Hard V8 Data Contract

Before touching V8 schema, generation, export, upload, or validation code, read:

- [docs/V8_SCHEMA_CONTRACT.md](docs/V8_SCHEMA_CONTRACT.md)
- [docs/SDGP_TESTCASE_ADDITION_CYCLE.md](docs/SDGP_TESTCASE_ADDITION_CYCLE.md)

The short version:

- No legacy shims.
- No compatibility configs.
- V8 expansion keeps the current V7.0.1 SDGP row shape.
- Taxonomy gaps are first-class `taxonomy.pattern` values, not subpattern/shim fields.
- Do not add `taxonomy.subpattern`, `taxonomy.subpattern_cell_id`, `taxonomy.subpattern_description`, or `meta.introduced_in`.
- Existing rows are not rewritten for additive taxonomy expansion.
- New V8 rows use the existing `meta.dataset_version: "v8"` cohort marker.
- Public V8 export/audit must fail if old pre-SDGP report axes reappear.

Do not solve V8 by preserving old V5/V6/V7 report axes. Add new rows with the
current canonical SDGP shape and update tooling to read that shape.

For testcase additions, do not merge candidate rows into the active vault before
offline structural and blind-label QA pass. The current local blind-label
settings for LM Studio Qwen 35B Q5 are documented in
`docs/SDGP_TESTCASE_ADDITION_CYCLE.md`; notably, Qwen thinking-model QA needs
`--max-tokens 2048`, not the old 128-token budget.
