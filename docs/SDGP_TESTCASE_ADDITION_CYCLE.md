# SDGP Testcase Addition Cycle

This is the clean cycle for adding SDGP rows to fitz-gov without poisoning the
active vault or pyrrho training manifest. Follow it exactly for V8 testcase
patches and future taxonomy expansions.

## Non-Negotiables

- Read `docs/V8_SCHEMA_CONTRACT.md` before changing V8 data, schema, export,
  or training prep.
- Candidate rows are not training rows. They become training rows only after
  structural checks and blind-label QA both pass.
- Do not merge risky candidate rows into
  `data/sdgp_vault_v51_enriched/cases.jsonl` just to score them.
- Do not train pyrrho from a manifest unless every active local cohort row in
  the vault is represented by a clean split manifest. `pyrrho/scripts/prepare_data.py`
  appends all rows with `meta.dataset_version == "v8"` from the local vault; the
  manifest supplies splits, not filtering.
- Treat these as separate gates:
  - `structural clean`: schema, checker, forbidden fields, dedup, batch IDs pass.
  - `QA clean`: independent blind label agrees with gold label and has no missing,
    invalid, or provider-error rows.
  - `model useful`: pyrrho retrain/probe improves target behavior without
    regressions.

## Required Local Blind-Label Settings

The current local QA backend is LM Studio with Qwen 35B Q5:

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
- Bad: contexts explicitly say no final row exists for the requested build. That
  is a trustworthy negative answer, not insufficient evidence.

For `resolved_candidate_selection` TRUSTWORTHY controls:

- Good: one context marks an interim candidate as non-final, and another
  source-of-record explicitly supersedes or closes it with the final answer.
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
