# V8.2 Retrieval-Control Enrichment Schema

Status: draft contract for the next fitz-gov enrichment pass.

V8.2 is a row-label enrichment over the published V8.1.0 dataset. It keeps the
same row set, query-grouped splits, governance labels, taxonomy labels, and V8
public config. The purpose is to add retrieval-control supervision for
`pyrrho-nano-g3.2` without changing the core `ABSTAIN` / `DISPUTED` /
`TRUSTWORTHY` benchmark.

## Placement

Add one object under `routing`:

```json
"routing": {
  "expert_fired": "history_geography",
  "secondary_expert": null,
  "routing_confidence": 0.9,
  "query_contract": {
    "kind": "evidence_sufficiency",
    "confidence": 0.88,
    "rationale": "...",
    "signals": ["..."],
    "labeler": "codex_subagent_v8_1",
    "row_index": 1
  },
  "retrieval_control": {
    "retrieval_action": {
      "kind": "retrieve_more",
      "confidence": 0.92,
      "rationale": "...",
      "signals": ["..."]
    },
    "gap_type": {
      "kind": "missing_specific_fact",
      "confidence": 0.9,
      "rationale": "...",
      "signals": ["..."]
    },
    "answerability_shape": {
      "kind": "single_fact",
      "confidence": 0.82,
      "rationale": "...",
      "signals": ["..."]
    },
    "preferred_retrieval_modality": {
      "kind": "unstructured_text",
      "confidence": 0.75,
      "rationale": "...",
      "signals": ["..."]
    },
    "evidence_failure_severity": {
      "score": 0.86,
      "confidence": 0.88,
      "rationale": "...",
      "signals": ["..."]
    },
    "labeler": "codex_subagent_v8_2",
    "row_index": 1
  }
}
```

`routing.retrieval_control` is the canonical V8.2 supervised target. Do not add
parallel top-level aliases, legacy report axes, or `taxonomy.subpattern` fields.

## Field Semantics

### `retrieval_action.kind`

The recommended next retrieval-system action for the current `(query,
contexts)` evidence state.

| Value | Meaning |
|---|---|
| `answer_now` | Evidence is sufficient and non-conflicting enough to answer. |
| `retrieve_more` | Evidence is relevant but incomplete; continue focused retrieval. |
| `broaden_search` | Current evidence is too narrow, adjacent, or off target; rewrite or broaden retrieval. |
| `resolve_conflict` | Evidence conflicts; search for source-of-record or tie-breaker evidence. |
| `ask_clarifying_question` | The user query is too broad or underspecified for a reliable retrieval target. |
| `structured_lookup` | Use an exact/table/code/config lookup path rather than ordinary semantic retrieval. |

### `gap_type.kind`

The primary evidence gap or conflict type. Use `none` when the row is
`TRUSTWORTHY` and evidence is sufficient.

| Value | Meaning |
|---|---|
| `none` | No meaningful evidence failure in this row. |
| `missing_specific_fact` | Topic is relevant, but the requested fact/aspect is absent. |
| `missing_timeframe` | Evidence misses the requested date, quarter, version date, or currentness requirement. |
| `missing_comparison_side` | A comparison query lacks one or more sides or comparable metrics. |
| `missing_source_authority` | Evidence exists but lacks the required authoritative/source-of-record status. |
| `conflicting_values` | Sources give incompatible facts, values, statuses, or conclusions. |
| `wrong_entity` | Evidence is about the wrong person, product, organization, jurisdiction, or object. |
| `wrong_version_or_scope` | Evidence is about the right family but wrong version, build, platform, region, cohort, or release. |
| `too_broad` | The query asks for broad overview coverage where no single sufficiency verdict is appropriate. |
| `incomplete_enumeration` | The query asks for all/list/requirements coverage and evidence is partial. |
| `unsupported_inference` | Evidence supports nearby facts but not the inference the answer would need. |
| `ambiguous_query` | The query itself is underspecified enough that multiple retrieval targets are plausible. |

### `answerability_shape.kind`

The answer form implied by the query. This is query-oriented, not a verdict on
current evidence quality.

| Value | Meaning |
|---|---|
| `single_fact` | A direct factual value or short answer is requested. |
| `explanation` | A mechanism, cause, rationale, or conceptual explanation is requested. |
| `list` | Several items are requested, but not necessarily an exhaustive set. |
| `exhaustive_list` | The query asks for all requirements, all parameters, full text, complete set, or complete coverage. |
| `comparison` | The answer must compare two or more entities, periods, metrics, policies, or versions. |
| `timeline` | Ordered temporal sequence or time-sensitive state is central. |
| `calculation` | Numeric computation or deterministic aggregation is required. |
| `yes_no` | The answer is primarily a boolean or feasibility verdict. |
| `summary` | A representative overview or synthesis is requested. |
| `citation_required` | The query explicitly needs provenance, source status, legal/regulatory authority, or citation-grade support. |
| `exact_lookup` | The query asks for an exact table field, function signature, config key, identifier, formula, or named value. |

### `preferred_retrieval_modality.kind`

The best retrieval channel for the query. This is separate from
`meta.modality`, which remains the row-level evidence representation in the
public dataset.

| Value | Meaning |
|---|---|
| `unstructured_text` | Ordinary prose/document retrieval is appropriate. |
| `structured_table` | Table, spreadsheet, row/column, metric, or exact structured lookup is preferred. |
| `code` | Code symbol, function, API, implementation, stack trace source, or code documentation retrieval is preferred. |
| `configuration` | Config key/value, environment variable, deployment setting, or policy file lookup is preferred. |
| `log_trace` | Log/event/timestamp retrieval is preferred. |
| `pdf_layout` | Page/section/layout-aware retrieval is needed. |
| `mixed` | Multiple retrieval channels are materially needed. |

### `evidence_failure_severity.score`

Continuous score from `0.0` to `1.0`, calibrated on the current evidence state:

| Range | Meaning |
|---|---|
| `0.00-0.20` | No material failure; answerable. |
| `0.21-0.45` | Minor weakness; answer may need caution or one more source. |
| `0.46-0.70` | Meaningful gap/conflict; retrieval should continue or resolve. |
| `0.71-1.00` | Severe failure; answering would likely hallucinate, mislead, or ignore conflict. |

## Label Object Rules

Every categorical subfield must contain:

- `kind`: one allowed enum value.
- `confidence`: decimal `0.0` to `1.0`.
- `rationale`: one concise sentence tied to the row evidence.
- `signals`: short list of concrete textual reasons.

`evidence_failure_severity` must contain:

- `score`: decimal `0.0` to `1.0`.
- `confidence`: decimal `0.0` to `1.0`.
- `rationale`: one concise sentence tied to the row evidence.
- `signals`: short list of concrete textual reasons.

The parent `retrieval_control` object must contain:

- `labeler`: model/process identifier, initially `codex_subagent_v8_2`.
- `row_index`: 1-based row index in `data/fitz-gov/cases.jsonl`.

## Labeling Rules

- Labels are semantic judgments from the full row, not deterministic transforms
  from the existing governance class.
- Do not label by script, keyword map, or regex. Scripts may only prepare
  shards, validate JSON shape, count labels, and merge accepted labels.
- Prefer the smallest correct action. Example: use `retrieve_more` when focused
  retrieval can likely fix the row; use `broaden_search` when current evidence
  is adjacent or systematically wrong.
- For `DISPUTED`, prefer `resolve_conflict` unless the row is better explained
  by wrong scope/version or missing authority.
- For `TRUSTWORTHY`, use `answer_now`, `gap_type: none`, and low severity unless
  the row is intentionally borderline and still needs a caution signal.
- `answerability_shape` is about the query's requested answer form, not whether
  current evidence succeeds.
- `preferred_retrieval_modality` is about the best retrieval channel, not the
  current row's `meta.modality`.

## V8.2 Release Gates

Before publishing V8.2:

- All 24,592 rows have `routing.retrieval_control`.
- Every categorical value is in the allowed enum.
- Every subfield has confidence, rationale, and signals.
- Numeric scores are finite and in range.
- Label counts are reviewed for collapsed classes and impossible combinations.
- A blind-label QA pass reviews at least the high-risk slices:
  `TRUSTWORTHY` with high severity, non-`none` gap types, `ABSTAIN` with
  `answer_now`, and `DISPUTED` without `resolve_conflict`.
- Public export keeps one `v8` config and query-grouped splits.

## Subagent Labeling Run

Use subagents for semantic labels. Do not use a script, regex map, or
deterministic transform to assign `retrieval_control` labels.

Recommended run shape:

1. Calibration pilot across all governance classes and query-contract kinds.
2. Review the pilot for enum coverage and ambiguous definitions.
3. Split the full 24,592 rows into balanced shards by
   `governance.classification`, `routing.query_contract.kind`,
   `taxonomy.pattern`, and `routing.expert_fired`.
4. Send each shard to a gpt-5.4 labeler with this schema as the rubric.
5. Store outputs under
   `data/_workspaces/retrieval_control_v8_2/subagent_labels/`.
6. Run mechanical validation for JSON shape, enum membership, numeric ranges,
   duplicate row indexes, missing row indexes, and impossible combinations.
7. Run blind-label QA on high-risk slices before merging into
   `data/fitz-gov/cases.jsonl`.

The first calibration artifact is:

`data/_workspaces/retrieval_control_v8_2/pilot_subagent_labels.jsonl`

It contains 18 gpt-5.4-labeled rows: 6 ABSTAIN, 6 DISPUTED, and 6 TRUSTWORTHY
examples across evidence-sufficiency, structured-lookup, temporal,
comparison, exhaustive, and representative-overview contracts.

## Intended Pyrrho Heads

`pyrrho-nano-g3.2` should train these additional heads on top of the g3.1
multitask surface:

- `retrieval_action`
- `gap_type`
- `answerability_shape`
- `preferred_retrieval_modality`
- `evidence_failure_severity`

Existing g3.1 heads remain:

- governance
- query contract
- route/domain
- taxonomy pattern
- scalar governance signals
