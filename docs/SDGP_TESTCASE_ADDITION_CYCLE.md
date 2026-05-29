# SDGP Testcase Addition Cycle

This is the clean cycle for adding SDGP rows to fitz-gov without poisoning the
active vault or pyrrho training manifest. Follow it exactly for V8 testcase
patches and future taxonomy expansions.

## Non-Negotiables

- Read `docs/V8_SCHEMA_CONTRACT.md` before changing V8 data, schema, export,
  or training prep.
- Candidate rows are not training rows. They become training rows only after
  structural checks and blind-label QA both pass.
- Do not merge risky candidate rows into `data/fitz-gov/cases.jsonl` just to
  score them.
- Do not train pyrrho from a manifest unless every active local cohort row in
  the vault is represented by a clean split manifest. `pyrrho/scripts/prepare_data.py`
  appends all rows with `meta.dataset_version == "v8"` from the local vault; the
  manifest supplies splits, not filtering.
- Every active or candidate row must carry `meta.modality`. Current unstructured
  text rows use `unstructured`; future table/database rows use `structured`;
  source/test/log/config rows use `code`.
- Treat these as separate gates:
  - `structural clean`: schema, checker, forbidden fields, dedup, batch IDs pass.
  - `QA clean`: independent blind label agrees with gold label and has no missing,
    invalid, or provider-error rows.
  - `model useful`: pyrrho retrain/probe improves target behavior without
    regressions.

## Required Local Blind-Label Settings

There are two supported offline blind-label paths:

- **Codex subagents**: preferred when running parallel blind QA from Codex. Keep
  the queue blind: pass only `row_index`, query, and contexts; do not expose case
  IDs, gold labels, taxonomy cells, manifests, batch specs, or generated outputs
  to worker agents. Materialize `row_index -> case_id` only after worker
  predictions are written.
- **LM Studio / Qwen**: acceptable when explicitly chosen, with the pinned
  settings below.

LM Studio healthcheck:

```powershell
$env:PYTHONIOENCODING = "utf-8"
$MODEL = "qwen3.6-35b-a3b@q5_k_s"
.\.venv\Scripts\python.exe scripts\sdgp_run_blind_label.py --provider lmstudio --model $MODEL --healthcheck-only
```

Use these settings for blind-label runs:

```powershell
--provider lmstudio
--model qwen3.6-35b-a3b@q5_k_s
--request-timeout-s 300
--max-tokens 2048
--temperature 0.0
```

Do not use the old `max_tokens=128` setting for Qwen 35B thinking-model QA. A
2026-05-25 probe on three known problematic rows reproduced the failure:

- `max_tokens=128`: scored `0/3`, invalid `3/3`.
- `max_tokens=2048`: scored `3/3`, invalid `0/3`; one row became a real
  disagreement, which is the intended QA signal.

## Step 1: Create Isolated Candidate Directories

Use a new handoff/QA pair for every patch. Never reuse a previous output
directory unless the whole run is being intentionally resumed.

```powershell
$RUN = "v8_candidate_YYYYMMDD_short_name"
$HANDOFF = "data/sdgp_handoff_$RUN"
$QA = "data/sdgp_qa_$RUN"
```

## Step 2: Prepare Batch Specs

For the whole-dataset V8 target-40 fill, use the V8 target-fill prep script.
This adds new V8 rows into the older V6/V7 taxonomy cells while preserving the
current SDGP row shape and `meta.dataset_version: "v8"` cohort marker:

```powershell
.\.venv\Scripts\python.exe scripts\sdgp_prepare_v8_target40_batches.py `
  --out-dir "$HANDOFF\subagent_batches" `
  --target 40 `
  --batch-size 30 `
  --seed 20260525
```

For modality diagnostic packs, use the modality-specific preparer. These rows
are candidate-only until structural and blind-label QA pass:

```powershell
.\.venv\Scripts\python.exe scripts\sdgp_prepare_modality_diagnostic_batches.py `
  --modality structured `
  --total-slots 300 `
  --batch-size 30
```

For the current code/structured modality local controls, three deterministic
candidate patch generators exist:

```powershell
.\.venv\Scripts\python.exe scripts\sdgp_generate_code_modality_patch.py
.\.venv\Scripts\python.exe scripts\sdgp_generate_code_retry_conflict_patch.py
.\.venv\Scripts\python.exe scripts\sdgp_generate_missing_evidence_patch.py
```

They write candidate-only workspaces under `data/_workspaces/handoff/`:

- `modality_code_patch_v1_20260528/` (**720** code rows)
- `modality_code_retry_conflict_patch_v1_20260529/` (**360** code rows)
- `modality_missing_evidence_patch_v1_20260529/` (**360** mixed code/structured rows)

These patch rows must follow the same workflow as any other candidate patch:
structural validation first, blind-label QA before merge, and no publication or
active-vault merge while labels are only trusted for local pyrrho controls.

For a full V8 gap pack:

```powershell
.\.venv\Scripts\python.exe scripts\sdgp_prepare_v8_generation_batches.py `
  --out-dir "$HANDOFF\subagent_batches" `
  --target-per-cell 5 `
  --batch-size 30 `
  --seed 20260525
```

For a focused patch, filter the target:

```powershell
.\.venv\Scripts\python.exe scripts\sdgp_prepare_v8_generation_batches.py `
  --out-dir "$HANDOFF\subagent_batches" `
  --filter-pattern verdict_conflict `
  --target-per-cell 10 `
  --batch-size 30 `
  --seed 20260525
```

The batch specs preassign case IDs. Generated output must preserve those IDs
and use this shape:

```json
{"case_id":"sdgp_v8_...","case":{...}}
```

## Step 3: Generate Candidate Rows

For deterministic template generation:

```powershell
.\.venv\Scripts\python.exe scripts\sdgp_generate_v8_template_outputs.py `
  --batch-dir "$HANDOFF\subagent_batches" `
  --out-dir "$HANDOFF\subagent_outputs"
```

For subagent generation, write one `batch_*.jsonl` file per batch spec under
`$HANDOFF\subagent_outputs`. Do not edit the vault directly.

### Current Candidate Handoff Snapshot

The latest Claude-generated V8 candidate handoff was:

`data/sdgp_handoff_v8_candidate_20260525_claude_expand/`

The raw intake snapshot at 18:56 Europe/Berlin was:

- Planned batch specs: **113** files / **3,360** assigned slots
- Main output files observed: **89** `batch_*.jsonl`
- Raw output lines observed: **2,646**
- Parseable unique candidate IDs observed: **2,643**
- Duplicate candidate IDs observed: **0**
- Assigned slots still missing: **717**
- Strict merge parser read-fail files: **4**
- Parsed rows missing core classification/domain/difficulty fields: **15**
- Fast structural dry-run result: **1,915 accepted / 0 existing / 624
  rejected**

Those raw numbers were not an acceptance count. The 2026-05-25 evening repair
normalized the handoff into:

`data/sdgp_handoff_v8_candidate_20260525_claude_expand/subagent_outputs_normalized/`

Normalized state:

- Recovered candidate rows: **2,646** unique rows from the raw handoff.
- Deterministic fallback rows for missing slots: **714**.
- Output: **113** `batch_*.jsonl` files / **3,360** rows.
- Step 4 dry-run result: **3,360 accepted / 0 existing / 0 rejected**.
- Step 5 QA dir:
  `data/sdgp_qa_v8_candidate_20260525_claude_expand_normalized/`
- Step 6 pilot score: **10/10 agreement**, **0 missing / 0 invalid / 0 error**.

Step 7 Codex subagent blind-label QA has run and is **not clean**:

- First pass (`gpt-5.4-mini`): **3,013/3,360 agreement**, **347 triage**,
  **0 missing / 0 invalid / 0 error**.
- Policy retry on the 347 triage rows recovered **223** rows.
- Combined score:
  `data/sdgp_qa_v8_candidate_20260525_claude_expand_normalized/score_codex_subagents_combined/`
  = **3,236/3,360 agreement** (**96.31%**), **124 triage**,
  **0 missing / 0 invalid / 0 error**.

Those 124 triage rows were replaced with deterministic V8 template rows in:

`data/sdgp_handoff_v8_candidate_20260525_claude_expand/subagent_outputs_patched_124_template/`

Final patched outcome:

- Structural dry-run: **3,360 accepted / 0 existing / 0 rejected**.
- Patched candidate QA:
  `data/sdgp_qa_v8_candidate_20260525_claude_expand_patched_124_template/score_codex_subagents_combined/`
  = **3,360/3,360 agreement**, **0 missing / 0 invalid / 0 error**,
  **0 triage**.
- Merge result: **3,360 added / 0 duplicate**, vault size **14,700**.
- Full V8 audit:
  `data/sdgp_v8_qa/clean_4200_score/` = **4,200/4,200 agreement**,
  **0 missing / 0 invalid / 0 error**, **0 triage**.
- Training-schema audit:
  `data/sdgp_v8_qa/training_schema_summary.json` = **4,200/4,200**
  complete.

The latest whole-dataset target-40 V8 candidate handoff was:

`data/sdgp_handoff_v8_target40/`

Final target-40 outcome:

- Batch specs: **174** files / **5,198** slots under `subagent_batches/`.
- Generated outputs: **174** `batch_*.jsonl` files / **5,198** rows under
  `subagent_outputs/`.
- Structural dry-run: **5,198 accepted / 0 existing / 0 rejected**.
- Codex subagent blind QA:
  `data/sdgp_qa_v8_target40/score_codex_subagents_combined/` =
  **5,198/5,198 agreement**, **0 missing / 0 invalid / 0 error**,
  **0 triage**.
- Merge result: batch `v8_target40_template_20260526`,
  **5,198 added / 0 duplicate**, vault size **19,898**.
- Full V8 audit: **9,398** V8 rows, **0** query-group split leakage.
- Training-schema audit:
  `data/sdgp_v8_qa/training_schema_summary.json` = **9,398/9,398**
  complete.
- Whole-dataset target-40 coverage:
  `data/sdgp_v8_qa/full_dataset_gap_target40_after_merge.json` =
  **483/483** primary cells at target, **0** total gap.

The latest whole-dataset target-50 V8 handoff was:

`data/sdgp_handoff_v8_target50/`

Final target-50 outcome:

- Batch specs: **157** files / **4,694** slots under `subagent_batches/`.
- Generated outputs: **157** `batch_*.jsonl` files / **4,694** rows under
  `subagent_outputs/`.
- Structural dry-run: **4,694 accepted / 0 existing / 0 rejected**.
- First Codex subagent blind score found **82** triage rows, isolated to
  `factual_contradiction`, `numerical_conflict`, and
  `resolved_candidate_selection` wording.
- After tightening those template families, final Codex subagent blind score:
  `data/sdgp_qa_v8_target50/score_codex_subagents_combined/` =
  **4,694/4,694 agreement**, **0 missing / 0 invalid / 0 error**,
  **0 triage**.
- Merge result: batch `v8_target50_template_20260526`,
  **4,694 added / 0 duplicate**, vault size **24,592**.
- Full V8 audit: **14,092** V8 rows, **0** query-group split leakage.
- Training-schema audit:
  `data/sdgp_v8_qa/training_schema_summary.json` = **14,092/14,092**
  complete.
- Whole-dataset target-50 coverage:
  `data/sdgp_v8_qa/full_dataset_gap_target50_after_merge.json` =
  **483/483** primary cells at target, **0** total gap.

Final stricter second-pass outcome:

- A later all-Claude/Codex full V8 second pass initially found **87**
  false-trustworthy triage rows in the hard V8-gap slice.
- Those rows were repaired in-place with batch marker
  `v8_second_pass_triage87_repair_20260526`; repair backup:
  `data/sdgp_vault_v51_enriched/cases.before_v8_second_pass_triage87_repair_20260526_102013.jsonl`.
- Narrow repaired-row blind recheck:
  `data/sdgp_v8_qa/score_second_pass_triage87_repair_only_20260526/` =
  **87/87 agreement**, **0 missing / 0 invalid / 0 error**, **0 triage**.
- Final full all-Claude/Codex second-pass score:
  `data/sdgp_v8_qa/score_claude_full_repaired87_combined_20260526/` =
  **14,092/14,092 agreement**, **0 missing / 0 invalid / 0 error**,
  **0 triage**.

## Step 4: Structural Dry Run

Run the merge checker in dry-run mode before any QA:

```powershell
.\.venv\Scripts\python.exe scripts\sdgp_merge_v8_generation_jsonl.py `
  --out-dir "$HANDOFF\subagent_outputs" `
  --batch-dir "$HANDOFF\subagent_batches" `
  --dry-run
```

The dry run must report:

```text
Accepted  : <candidate row count>
Existing  : 0
Rejected  : 0
```

If any row is rejected, fix generation and rerun from Step 3. Do not proceed to
blind-label QA with structurally rejected rows.

## Step 5: Build Offline Blind-Label QA

Build candidate QA files directly from generated JSONL. This does not merge
anything into the active vault.

```powershell
.\.venv\Scripts\python.exe scripts\sdgp_build_blind_label_from_generation_jsonl.py `
  --out-dir "$HANDOFF\subagent_outputs" `
  --qa-dir "$QA"
```

This writes:

- `$QA\blind_label_queue.jsonl`
- `$QA\blind_label_manifest.jsonl`
- `$QA\candidate_summary.json`

The manifest uses `split: "candidate"` on purpose. Real train/validation/test
splits are assigned only after rows are accepted into the active vault.

## Step 6: Blind-Label Pilot

Run a small pilot before the full QA pass:

```powershell
.\.venv\Scripts\python.exe scripts\sdgp_run_blind_label.py `
  --queue "$QA\blind_label_queue.jsonl" `
  --out "$QA\blind_label_predictions_pilot.jsonl" `
  --provider lmstudio `
  --model qwen3.6-35b-a3b@q5_k_s `
  --request-timeout-s 300 `
  --max-tokens 2048 `
  --temperature 0.0 `
  --max-rows 10 `
  --run-id "$RUN-pilot" `
  --no-resume

.\.venv\Scripts\python.exe scripts\sdgp_score_blind_labels.py `
  --manifest "$QA\blind_label_manifest.jsonl" `
  --predictions "$QA\blind_label_predictions_pilot.jsonl" `
  --out-dir "$QA\pilot_score" `
  --only-predicted
```

Pilot pass criteria:

- `Missing/invalid/error` is `0/0/0`.
- Disagreements are manually inspected before the full pass.

If the pilot has invalid rows, fix the run configuration first. If the pilot
has disagreements, fix the row wording or gold label before generating more
rows. Do not hide disagreements by changing parser logic.

## Step 7: Full Candidate Blind-Label QA

Run full QA only after the pilot is parse-clean:

```powershell
.\.venv\Scripts\python.exe scripts\sdgp_run_blind_label.py `
  --queue "$QA\blind_label_queue.jsonl" `
  --out "$QA\blind_label_predictions_qwen36_35b_q5.jsonl" `
  --provider lmstudio `
  --model qwen3.6-35b-a3b@q5_k_s `
  --request-timeout-s 300 `
  --max-tokens 2048 `
  --temperature 0.0 `
  --run-id "$RUN" `
  --no-resume

.\.venv\Scripts\python.exe scripts\sdgp_score_blind_labels.py `
  --manifest "$QA\blind_label_manifest.jsonl" `
  --predictions "$QA\blind_label_predictions_qwen36_35b_q5.jsonl" `
  --out-dir "$QA\score"
```

Candidate QA pass criteria:

- `Scored` equals total manifest rows.
- `Agreement` equals scored rows.
- `Missing/invalid/error` is `0/0/0`.
- `blind_label_disagreements.jsonl`, `blind_label_review_queue.jsonl`, and
  `blind_label_triage.jsonl` are empty JSONL files.

Any disagreement means the candidate pack is not clean. Fix the rows and rerun
candidate QA from scratch. Do not merge partial or triaged candidate rows into
the active vault.

### Codex Subagent Blind-Label Path

For Codex subagent QA, prepare blind shards from the candidate queue:

```powershell
.\.venv\Scripts\python.exe scripts\sdgp_prepare_codex_blind_shards.py `
  --qa-dir "$QA" `
  --out-dir "$QA\codex_subagent_blind" `
  --n-shards 12
```

Give each subagent exactly one `$QA\codex_subagent_blind\shards\shard_XX.jsonl`
file and one disjoint output path under
`$QA\codex_subagent_blind\predictions\shard_XX_predictions.jsonl`.
The subagent prompt must forbid opening manifests, row-index maps, generated
outputs, batch specs, taxonomy/gold metadata, score files, or backups.

After all shard predictions return, materialize and score from the parent
session:

```powershell
.\.venv\Scripts\python.exe scripts\sdgp_materialize_codex_blind_predictions.py `
  --blind-dir "$QA\codex_subagent_blind" `
  --out "$QA\codex_subagent_blind\blind_label_predictions_codex_subagents_combined.jsonl"

.\.venv\Scripts\python.exe scripts\sdgp_score_blind_labels.py `
  --manifest "$QA\blind_label_manifest.jsonl" `
  --predictions "$QA\codex_subagent_blind\blind_label_predictions_codex_subagents_combined.jsonl" `
  --out-dir "$QA\score_codex_subagents_combined"
```

If the Codex score has any disagreement, treat it as a data-quality signal.
Repair the candidate rows, rebuild the blind queue/shards, rerun affected
subagent shards, and score cleanly before merging.

## Step 8: Merge Only Clean Candidates

After the full candidate QA is clean, merge into the active vault:

```powershell
.\.venv\Scripts\python.exe scripts\sdgp_merge_v8_generation_jsonl.py `
  --out-dir "$HANDOFF\subagent_outputs" `
  --batch-dir "$HANDOFF\subagent_batches" `
  --batch-id "$RUN"
```

Immediately rebuild the full local V8 QA audit:

```powershell
.\.venv\Scripts\python.exe scripts\sdgp_v7_qa_audit.py `
  --cohort v8 `
  --out-dir data\sdgp_v8_qa
```

Use the regenerated full manifest for pyrrho prep only if every active V8 row is
known clean. If any experimental rows are in the active vault but not QA-clean,
quarantine them first or restore the pre-merge vault backup.

## Step 9: Pyrrho Prep Rule

The pyrrho V8 append path reads all `meta.dataset_version == "v8"` rows from the
local fitz-gov vault and requires every one to have a split in the manifest.
Therefore:

- The active vault must contain only accepted V8 rows.
- The manifest passed as `--append-local-manifest` must cover every active V8
  row.
- Do not point pyrrho at `blind_label_manifest.jsonl` just because the file
  exists. Point it at a manifest whose row set is known clean.

## Label-Boundary Rules That Failed Before

For `version_build_mismatch` ABSTAIN controls:

- Good: contexts only show evidence for a neighboring build/version/platform.
- Good: the neighboring key is a genuinely distinct value, such as `phase 1`
  when the query asks for `phase 2`, or `Linux package 2.5` when the query asks
  for `Linux package 2.6`.
- Bad: contexts explicitly say no final row exists for the requested build. That
  is a trustworthy negative answer, not insufficient evidence.
- Bad: the neighboring key contains the requested key as a substring, such as
  `phase 2-previous` for a `phase 2` query. The blind labeler can reasonably
  treat that as close enough to answer.

For `resolved_candidate_selection` TRUSTWORTHY controls:

- Good: one context marks an interim candidate as non-final, and another
  source-of-record explicitly supersedes or closes it with the final answer.
- Good: the non-final item is phrased as an obsolete candidate ID with no
  final-result field, while the source-of-record publishes the valid final
  record and final result.
- Risky: wording that reads like two answer candidates, such as `red` versus
  `green`, without enough resolution language. The blind labeler may reasonably
  choose DISPUTED.

For `verdict_conflict` DISPUTED controls:

- Good: same entity, same concrete build/version/testcase, both sources in
  scope, incompatible final verdicts.
- Bad: different builds, different candidate records, or a source-of-record
  statement that explicitly resolves the conflict.

## Recovery Rules

- If a blind-label run is interrupted, do not treat its output as final. Either
  resume the exact same run intentionally or delete/rebuild that run directory.
- If invalid rows are caused by truncation, rerun only after confirming the token
  budget. For Qwen 35B Q5, use `--max-tokens 2048`.
- If rows disagree after parsing cleanly, this is a data-quality signal. Fix the
  row design; do not relabel around the blind labeler.
- If bad rows were merged into the active vault, create a timestamped backup,
  remove or quarantine those exact case IDs, rebuild the full V8 audit, and
  update pyrrho handoff/log before training anything.

## Verification Commands

Run these before committing data/tooling changes:

```powershell
python -m pytest tests/sdgp/test_blind_label.py tests/sdgp/test_providers.py -q
python -m pytest tests/sdgp -q
```

For pyrrho-side training or prep changes, also run from `pyrrho`:

```powershell
pytest tests/test_smoke.py -v
```
