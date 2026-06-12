# V9 Retrieval-Control Expansion Plan

Status: target-100 candidate generation, blind-label QA, validated-only merges, closure buffering, and Hugging Face publication are complete as of 2026-06-12. The public `yafitzdev/fitz-gov` dataset is tagged **v9.0.0** at commit `874fd18d4952eec0e72b6df2264f8281615fd350`. The local vault has **40,755** rows and the V9 retrieval-control answerability matrix is closed at **189/189** cells with **0** remaining gap at **100/cell**.

V9 is the next additive data expansion after published V8.2.0. It is not
`v8.3`. V8.2 remains the published retrieval-control enrichment over the V8 row
set; V9 is a new targeted generation release for stronger retrieval-control
coverage.

## Reason

V8/V8.2 is balanced for the old SDGP matrix:

```text
taxonomy_pattern x domain x difficulty
```

That matrix is still the core governance benchmark. It does not guarantee a
healthy distribution for retrieval-control labels. The weakest V8.2
answerability labels are minority operational shapes, especially set answers
and structured reasoning.

## V9 Target Matrix

The first V9 generation queue targets collapsed answerability shape:

```text
governance_class x domain x difficulty x collapsed_answerability_shape
```

Default target shapes:

```text
synthesis_answer
set_answer
structured_reasoning
```

`direct_answer` remains a valid collapsed label for reporting and training, but
it is excluded from the default V9 generation queue because the V8.2 row set
already has many direct-answer rows.

## Collapse Map

| V9 collapsed label | V8.2 detailed labels |
|---|---|
| `direct_answer` | `single_fact`, `exact_lookup`, `yes_no`, `citation_required` |
| `synthesis_answer` | `explanation`, `summary` |
| `set_answer` | `list`, `exhaustive_list` |
| `structured_reasoning` | `comparison`, `timeline`, `calculation` |

## Tooling

The V9 gap detector is implemented in:

```text
fitz_gov/sdgp/retrieval_control_gap_detector.py
```

Report command:

```powershell
python scripts/sdgp_v9_answerability_gap_report.py `
  --cases data/fitz-gov/cases.jsonl `
  --target-per-cell 100 `
  --out-json data/_workspaces/v9_answerability_gap_report_target100.json `
  --out-md data/_workspaces/v9_answerability_gap_report_target100.md
```

Batch-prep command:

```powershell
python scripts/sdgp_prepare_v9_answerability_batches.py `
  --cases data/fitz-gov/cases.jsonl `
  --out-dir data/_workspaces/handoff/v9_answerability/subagent_batches `
  --outputs-dir data/_workspaces/handoff/v9_answerability/subagent_outputs `
  --target-train-per-cell 80 `
  --batch-size 30 `
  --n-few-shots 2
```

The default `100` total rows per cell is intended to yield roughly `80` train
rows per cell after the standard 80/10/10 split. Across 63 cells per minority
shape, that is the practical path toward about 5,000 train rows each for
`synthesis_answer`, `set_answer`, and `structured_reasoning`.

The first full prep pass produced:

```text
slots: 16,144
batch specs: 539
batch dir: data/_workspaces/handoff/v9_answerability/subagent_batches
expected output dir: data/_workspaces/handoff/v9_answerability/subagent_outputs
```

The batch-prep script writes candidate specs only. It preassigns `sdgp_v9_...`
case IDs, uses `version: "fitz-gov-9.0"` and `meta.dataset_version: "v9"` in
the prompts, and requires each generated row to populate both
`routing.query_contract` and `routing.retrieval_control`. Generated output rows
must still be structurally checked and blind-label QAed before any merge.

Pilot lesson from 2026-06-04: structurally valid rows are not enough. The first
3-row GPT-5.4 pilot passed the V9 merge dry-run, but blind-label QA scored only
**1/3** because both DISPUTED rows were actually resolvable by source hierarchy
or by explanation. The prompt now explicitly requires DISPUTED rows to contain
unresolved material conflict. Do not use pre-hardening batch specs for full V9
generation.

Hardened pilot result from 2026-06-04:

```text
handoff: data/_workspaces/handoff/v9_answerability_pilot_hardened
qa: data/_workspaces/qa/v9_answerability_pilot_hardened
rows: 3
structural dry-run: Accepted 3 / Rejected 0
Codex blind-label QA: Agreement 3/3, disagreements 0, missing/invalid/error 0/0/0
```

First scaled slice from 2026-06-04:

```text
handoff: data/_workspaces/handoff/v9_answerability
generated files: batch_001.jsonl through batch_007.jsonl
rows: 210
aggregate structural dry-run: Accepted 210 / Existing 0 / Rejected 0
batch_001 initial Codex blind-label QA: Agreement 27/30, disagreements 3, missing/invalid/error 0/0/0
```

The initial `batch_001` disagreements were all ABSTAIN rows that were too
answerable:

```text
sdgp_v9_abstain__general_commonsense__easy__structured_reasoning__0
sdgp_v9_abstain__history_geography__medium__synthesis_answer__0
sdgp_v9_abstain__culture_society__easy__synthesis_answer__0
```

Those three rows were repaired in
`data/_workspaces/handoff/v9_answerability/subagent_outputs/batch_001.jsonl`.
Repaired `batch_001` result:

```text
qa: data/_workspaces/qa/v9_answerability_batch001_repaired
structural dry-run: Accepted 30 / Existing 0 / Rejected 0
Codex blind-label QA: Agreement 30/30, disagreements 0, missing/invalid/error 0/0/0
```

`batch_001` was initially merge-clean, then one DISPUTED query was later
hardened as part of the full-slice repair pass.

Batches `002`-`007` initial and repair QA path:

```text
initial QA: Agreement 174/180, disagreements 6, missing/invalid/error 0/0/0
repair pass 1: Agreement 176/180, disagreements 4, missing/invalid/error 0/0/0
repair pass 2: Agreement 173/180, disagreements 7, missing/invalid/error 0/0/0
repair pass 3: Agreement 179/180, disagreements 1, missing/invalid/error 0/0/0
repair pass 4: Agreement 179/180, disagreements 1, missing/invalid/error 0/0/0
repair pass 5: Agreement 179/180, disagreements 1, missing/invalid/error 0/0/0
```

The repeated repair passes exposed two prompt/data-shape lessons:

```text
DISPUTED rows must not ask "why did sources differ?" or "explain the discrepancy";
that can make conflict explanation itself answerable.

ABSTAIN rows that ask for a stated reason must make the missing stated-record
requirement explicit, otherwise background evidence can look answerable.
```

After hardening those query shapes, the full `batch_001`-`batch_007` gate passed:

```text
qa: data/_workspaces/qa/v9_answerability_batches001_007_repaired_full2
structural dry-run: Accepted 210 / Existing 0 / Rejected 0
Codex blind-label QA: Agreement 210/210, disagreements 0, missing/invalid/error 0/0/0
```

Live local vault merge result:

```text
merge batch: 2913478b095a
provider-version: gpt-5.4-v9-batches001-007-full2-clean
added: 210
duplicate: 0
vault size: 24,802
```

Post-merge local cohort counts:

```text
v6: 2,980
v7: 7,520
v8: 14,092
v9: 210
```

First V9 slice distribution:

```text
governance: ABSTAIN 69 / DISPUTED 75 / TRUSTWORTHY 66
difficulty: easy 72 / medium 70 / hard 68
domains: 28-32 rows per existing primary domain
```

Target-100 gap report after first merge:

```text
rows read: 24,802
cells: 189
cells at target: 0
empty cells: 0
gap to fill: 15,934
set_answer: current 809 / gap 5,491
structured_reasoning: current 705 / gap 5,595
synthesis_answer: current 1,452 / gap 4,848
report: data/_workspaces/v9_answerability_gap_report_target100_after_first_merge.md
```

Second scaled slice from 2026-06-04:

```text
generated files: batch_008.jsonl through batch_013.jsonl
rows: 180
initial structural dry-run: Accepted 180 / Existing 0 / Rejected 0
initial Codex blind-label QA:
  batch_008-009: Agreement 55/60, disagreements 5, missing/invalid/error 0/0/0
  batch_010-013: Agreement 118/120, disagreements 2, missing/invalid/error 0/0/0
```

Repair pass notes:

```text
Fixed 10 mechanical schema issues in batch_010 where TRUSTWORTHY rows had
meta.near_miss_class equal to TRUSTWORTHY.

Repaired 11 ambiguous evidence/query rows across batch_008, batch_009,
batch_010, and batch_013. Main fixes were the same as slice one: remove
resolvable source precedence, make conflicts same-scope/same-date, and make
ABSTAIN rows require missing exact records rather than inferable logic.
```

Final QA and merge result:

```text
batch_008-009 repaired3 QA: Agreement 60/60, disagreements 0, missing/invalid/error 0/0/0
batch_010-013 repaired2 QA: Agreement 120/120, disagreements 0, missing/invalid/error 0/0/0

merge batch_008-009: 0481bd6ab006
provider-version: gpt-5.4-v9-batches008-009-repaired3-clean
added: 60
duplicate: 0

merge batch_010-013: 02bd541ce508
provider-version: gpt-5.4-v9-batches010-013-repaired2-clean
added: 120
duplicate: 0
vault size: 24,982
```

Post-second-merge local cohort counts:

```text
v6: 2,980
v7: 7,520
v8: 14,092
v9: 390
```

Merged V9 distribution after two slices:

```text
governance: ABSTAIN 130 / DISPUTED 133 / TRUSTWORTHY 127
difficulty: easy 132 / medium 129 / hard 129
domains: 54-58 rows per existing primary domain
```

Target-100 gap report after second merge:

```text
rows read: 24,982
cells: 189
cells at target: 0
empty cells: 0
gap to fill: 15,754
set_answer: current 871 / gap 5,429
structured_reasoning: current 765 / gap 5,535
synthesis_answer: current 1,510 / gap 4,790
report: data/_workspaces/v9_answerability_gap_report_target100_after_second_merge.md
```

Third scaled slice from 2026-06-04:

```text
generated files: batch_014.jsonl through batch_019.jsonl
rows: 180
initial structural dry-run: Accepted 24 / Existing 0 / Rejected 156
normalized structural dry-run: Accepted 180 / Existing 0 / Rejected 0
initial Codex blind-label QA: Agreement 166/180, disagreements 14, missing/invalid/error 0/0/0
repaired-triage QA: Agreement 13/14, disagreements 1, missing/invalid/error 0/0/0
final single-row QA: Agreement 1/1, disagreements 0, missing/invalid/error 0/0/0
combined final QA: Agreement 180/180, disagreements 0, missing/invalid/error 0/0/0
```

Repair pass notes:

```text
The third slice initially failed mostly because generated rows used invalid
natural-language enum names such as collect_missing_scope, targeted_refresh,
structured_records, policy_document, and missing_result. These were normalized
to the V9 retrieval-control enum contract before semantic QA.

The 14 semantic disagreements repeated the earlier lesson: ABSTAIN rows must
make the missing record/fact impossible to infer, and DISPUTED rows must contain
same-scope unresolved conflict rather than context that can be cleanly reconciled.
```

Final QA and merge result:

```text
merge batch_014-019: eb5fef5ba32d
provider-version: gpt-5.4-v9-batches014-019-combined-clean
added: 180
duplicate: 0
vault size: 25,162
```

Post-third-merge local cohort counts:

```text
v6: 2,980
v7: 7,520
v8: 14,092
v9: 570
```

Merged V9 distribution after three slices:

```text
governance: ABSTAIN 190 / DISPUTED 191 / TRUSTWORTHY 189
difficulty: easy 191 / medium 189 / hard 190
domains: 81-82 rows per existing primary domain
```

Target-100 gap report after third merge:

```text
rows read: 25,162
cells: 189
cells at target: 0
empty cells: 0
gap to fill: 15,574
set_answer: current 931 / gap 5,369
structured_reasoning: current 826 / gap 5,474
synthesis_answer: current 1,569 / gap 4,731
report: data/_workspaces/v9_answerability_gap_report_target100_after_third_merge.md
```

Fourth scaled slice from 2026-06-04:

```text
generated files: batch_020.jsonl through batch_025.jsonl
rows: 180
initial structural dry-run: Accepted 170 / Existing 0 / Rejected 10
repaired structural dry-run: Accepted 180 / Existing 0 / Rejected 0
initial Codex blind-label QA: Agreement 174/180, disagreements 6, missing/invalid/error 0/0/0
repaired-triage QA: Agreement 6/6, disagreements 0, missing/invalid/error 0/0/0
combined final QA: Agreement 180/180, disagreements 0, missing/invalid/error 0/0/0
```

Repair pass notes:

```text
The fourth slice had much less mechanical enum drift than the third slice.
Structural repairs were mostly TRUSTWORTHY grounding shape normalization
(`sentence_attributions` -> `sentences`) plus one authority-score spread fix and
two quantitative-consensus numeric-context fixes.

The six semantic disagreements were all DISPUTED rows whose query asked the
blind labeler to compare two conflicting values. That made the disagreement
itself answerable. Repairs changed those rows to ask for the single operative
value or controlling explanation.
```

Final QA and merge result:

```text
merge batch_020-025: 4d30f0ae4feb
provider-version: gpt-5.4-v9-batches020-025-combined-clean
added: 180
duplicate: 0
vault size: 25,342
```

Post-fourth-merge local cohort counts:

```text
v6: 2,980
v7: 7,520
v8: 14,092
v9: 750
```

Merged V9 distribution after four slices:

```text
governance: ABSTAIN 252 / DISPUTED 252 / TRUSTWORTHY 246
difficulty: easy 251 / medium 250 / hard 249
domains: 106-108 rows per existing primary domain
```

Target-100 gap report after fourth merge:

```text
rows read: 25,342
cells: 189
cells at target: 0
empty cells: 0
gap to fill: 15,394
set_answer: current 993 / gap 5,307
structured_reasoning: current 888 / gap 5,412
synthesis_answer: current 1,625 / gap 4,675
report: data/_workspaces/v9_answerability_gap_report_target100_after_fourth_merge.md
```

Fast raw-generation wave from 2026-06-04:

```text
generated files: batch_026.jsonl through batch_099.jsonl
rows: 2,220
mode: raw candidates only
structural dry-run: not run for this wave
blind-label QA: not run for this wave
merge: not run for this wave
```

All `batch_001.jsonl` through `batch_099.jsonl` now exist under:

```text
data/_workspaces/handoff/v9_answerability/subagent_outputs
```

Each file has 30 JSONL lines, for **2,970** raw candidate rows total. Only
`batch_001` through `batch_025` are merged into the local active vault. Rows
from `batch_026` through `batch_099` are unvalidated candidates and must not be
treated as dataset rows until structural dry-run, repair, QA, and merge gates
are explicitly resumed.

Compact semantic-plan pilot from 2026-06-04:

```text
spec files: data/_workspaces/handoff/v9_answerability_compact_pilot/batch_specs/batch_100.json through batch_103.json
semantic plan files: data/_workspaces/handoff/v9_answerability_compact_pilot/semantic_plan_outputs/batch_100.jsonl through batch_103.jsonl
expanded files: data/_workspaces/handoff/v9_answerability_compact_pilot/expanded_outputs/batch_100.jsonl through batch_103.jsonl
rows: 100
semantic-plan generation: 100/100 lines
expansion: 100/100 rows
structural dry-run: Accepted 100 / Existing 0 / Rejected 0
blind-label QA: not run
merge: not run
```

The pilot keeps meaning generation with subagents but moves deterministic JSON
plumbing into scripts:

```text
scripts/sdgp_prepare_v9_compact_plan_pilot.py
scripts/sdgp_expand_v9_compact_plans.py
```

First dry-run after expansion accepted **80/100** and rejected **20** for
mechanical taxonomy-shape issues (`authority_conflict` authority-score spread,
`numerical_conflict` digit-bearing context requirements, and one
`quantitative_consensus` numeric-context requirement). The expander was then
hardened to canonicalize taxonomy aliases and normalize/redirect mechanically
invalid pattern choices without changing the target governance class. The
second structural dry-run accepted **100/100**. This is **not** a semantic QA
result; blind-label QA is still required before any merge.

Larger compact scale test from 2026-06-04:

```text
spec files: data/_workspaces/handoff/v9_answerability_compact_scale600/batch_specs/batch_104.json through batch_127.json
target slots: 600
workers: 6 Codex subagents, 100 rows each
completed workers: 3/6
completed semantic plans: 300
stalled workers: 3/6, 0 output files each, shut down
expansion: 300/300 rows
structural dry-run: Accepted 158 / Existing 0 / Rejected 142
blind-label QA: not run
merge: not run
```

The scale test is a negative result for the compact-template path. The rejected
rows were duplicate-content failures inside the candidate set, caused by
templated/reused plans rather than live-vault duplicates. Worker quality varied:
one worker produced **100/100** structurally unique rows, one produced **49/100**,
and one produced only **9/100**. Compact specs are much smaller than full-row
specs, but this run did not prove a throughput win and showed a real diversity
risk. Do not scale compact generation unless prompts explicitly forbid reusable
templates and force domain-specific evidence/query variation.

Normal full-row raw wave from 2026-06-04 evening:

```text
generated files: batch_103.jsonl through batch_117.jsonl
rows: 450
line/JSON/id validation: 450/450 pass
structural dry-run: Accepted 267 / Existing 0 / Rejected 183
blind-label QA: not run
merge: not run
```

`batch_100` through `batch_102` did not land as valid normal outputs. The first
3-batch worker stalled. A later single-batch retry for `batch_100` wrote
malformed non-JSON output; it was moved to:

```text
data/_workspaces/handoff/v9_answerability/rejected_outputs/batch_100.malformed_20260604_1758.jsonl
```

`batch_101` and `batch_102` remain absent. The completed `batch_103`-`117`
normal rows are raw candidates only. Dry-run rejects are mostly mechanical:
invalid retrieval-control enum synonyms, wrong `meta.category`, missing
TRUSTWORTHY `meta.grounding_targets`, and taxonomy-pattern structure misses.
Repair or normalize them before blind-label QA.

Normalizer and later full-row waves from 2026-06-04 evening:

```text
normalizer: scripts/sdgp_normalize_v9_answerability_jsonl.py
normalized gap-fill batch_100-102 + 139-144: 270/270 structural dry-run accepted
normalized batch_103-117: 450/450 structural dry-run accepted
normalized batch_118-135: 540/540 structural dry-run accepted
normalized partial batch_136-153: 360/360 structural dry-run accepted
normalized batch_154-159: 180/180 structural dry-run accepted
normalized batch_160-165: 180/180 structural dry-run accepted
normalized batch_166-171: 180/180 structural dry-run accepted
normalized batch_172-177: 180/180 structural dry-run accepted
normalized batch_178-183: 180/180 structural dry-run accepted
normalized batch_184-189: 180/180 structural dry-run accepted
normalized batch_190-195: 180/180 structural dry-run accepted
normalized batch_196-198: 90/90 structural dry-run accepted
normalized batch_199-202: 120/120 structural dry-run accepted
normalized batch_203-205: 90/90 structural dry-run accepted
normalized batch_206-210: 150/150 structural dry-run accepted
normalized batch_211-212: 60/60 structural dry-run accepted
normalized batch_213: 30/30 structural dry-run accepted
normalized batch_214: 30/30 structural dry-run accepted
normalized batch_215: 30/30 structural dry-run accepted
normalized batch_216: 30/30 structural dry-run accepted
normalized batch_217: 30/30 structural dry-run accepted
normalized batch_218: 30/30 structural dry-run accepted
normalized batch_219: 30/30 structural dry-run accepted
normalized batch_220: 30/30 structural dry-run accepted
normalized batch_221: 30/30 structural dry-run accepted
normalized batch_222: 30/30 structural dry-run accepted
normalized batch_223: 30/30 structural dry-run accepted
normalized batch_224: 30/30 structural dry-run accepted
normalized batch_225: 30/30 structural dry-run accepted
normalized batch_226: 30/30 structural dry-run accepted
normalized batch_227: 30/30 structural dry-run accepted
normalized batch_228: 30/30 structural dry-run accepted
normalized batch_229: 30/30 structural dry-run accepted
normalized batch_230: 30/30 structural dry-run accepted
normalized batch_231: 30/30 structural dry-run accepted
normalized batch_232: 30/30 structural dry-run accepted
normalized batch_233: 30/30 structural dry-run accepted
normalized batch_234: 30/30 structural dry-run accepted
normalized batch_235: 30/30 structural dry-run accepted
normalized batch_236: 30/30 structural dry-run accepted
normalized batch_237: 30/30 structural dry-run accepted
normalized batch_238: 30/30 structural dry-run accepted
normalized batch_239: 30/30 structural dry-run accepted
normalized batch_240: 30/30 structural dry-run accepted
normalized batch_241: 30/30 structural dry-run accepted
normalized batch_242: 30/30 structural dry-run accepted
normalized batch_243: 30/30 structural dry-run accepted
normalized batch_244: 30/30 structural dry-run accepted
normalized batch_245: 30/30 structural dry-run accepted
normalized batch_246: 30/30 structural dry-run accepted
normalized batch_247: 30/30 structural dry-run accepted
normalized batch_248: 30/30 structural dry-run accepted
normalized batch_249: 30/30 structural dry-run accepted
normalized batch_250: 30/30 structural dry-run accepted after regenerating from corrected shard source
normalized batch_251: 30/30 structural dry-run accepted
normalized batch_252: 30/30 structural dry-run accepted
normalized batch_253: 30/30 structural dry-run accepted
normalized batch_254: 30/30 structural dry-run accepted
normalized batch_255: 30/30 structural dry-run accepted
normalized batch_256: 30/30 structural dry-run accepted
normalized batch_257: 30/30 structural dry-run accepted
normalized batch_258: 30/30 structural dry-run accepted
normalized batch_259: 30/30 structural dry-run accepted
normalized batch_260: 30/30 structural dry-run accepted
normalized batch_261: 30/30 structural dry-run accepted
normalized batch_262: 30/30 structural dry-run accepted
normalized batch_263: 30/30 structural dry-run accepted
normalized batch_264-265: 60/60 structural dry-run accepted
normalized batch_266-267: 60/60 structural dry-run accepted
normalized batch_268-269: 60/60 structural dry-run accepted
normalized batch_270-271: 60/60 structural dry-run accepted
normalized batch_272: 30/30 structural dry-run accepted
normalized batch_273: 30/30 structural dry-run accepted
normalized batch_274-275: 60/60 structural dry-run accepted
normalized batch_276-277: 60/60 structural dry-run accepted
normalized batch_278-279: 60/60 structural dry-run accepted
normalized batch_280: 30/30 structural dry-run accepted
normalized batch_281: 30/30 structural dry-run accepted
normalized batch_282: 30/30 structural dry-run accepted
normalized batch_283: 30/30 structural dry-run accepted
normalized batch_284-285: 60/60 structural dry-run accepted
normalized batch_286-287: 60/60 structural dry-run accepted
normalized batch_288: 30/30 structural dry-run accepted
normalized batch_289: 30/30 structural dry-run accepted
normalized batch_290: 30/30 structural dry-run accepted
normalized batch_291: 30/30 structural dry-run accepted
normalized batch_292: 30/30 structural dry-run accepted
normalized batch_293-294: 60/60 structural dry-run accepted
normalized batch_295: 30/30 structural dry-run accepted
normalized batch_296: 30/30 structural dry-run accepted
normalized batch_297: 30/30 structural dry-run accepted
normalized batch_298: 30/30 structural dry-run accepted
normalized batch_299: 30/30 structural dry-run accepted
normalized batch_300: 30/30 structural dry-run accepted
normalized batch_301: 30/30 structural dry-run accepted
normalized batch_302: 30/30 structural dry-run accepted
normalized batch_303: 30/30 structural dry-run accepted
normalized batch_304: 30/30 structural dry-run accepted
normalized batch_305: 30/30 structural dry-run accepted
normalized batch_306: 30/30 structural dry-run accepted
normalized batch_307: 30/30 structural dry-run accepted
normalized batch_308: 30/30 structural dry-run accepted
normalized batch_309: 30/30 structural dry-run accepted
normalized batch_310: 30/30 structural dry-run accepted
normalized batch_312-313: 60/60 structural dry-run accepted
normalized batch_314: 30/30 structural dry-run accepted
normalized batch_315: 30/30 structural dry-run accepted
normalized batch_316-317: 60/60 structural dry-run accepted
normalized batch_318: 30/30 structural dry-run accepted
normalized batch_319: 30/30 structural dry-run accepted
normalized batch_320: 30/30 structural dry-run accepted
normalized batch_321: 30/30 structural dry-run accepted
normalized batch_322: 30/30 structural dry-run accepted
normalized batch_323: 30/30 structural dry-run accepted
normalized batch_324: 30/30 structural dry-run accepted
normalized batch_325: 30/30 structural dry-run accepted
normalized batch_326: 30/30 structural dry-run accepted
normalized batch_327: 30/30 structural dry-run accepted
normalized batch_328: 30/30 structural dry-run accepted
normalized batch_329: 30/30 structural dry-run accepted
normalized batch_330: 30/30 structural dry-run accepted
normalized batch_331: 30/30 structural dry-run accepted
normalized batch_332: 30/30 structural dry-run accepted
normalized batch_333: 30/30 structural dry-run accepted
normalized batch_334: 30/30 structural dry-run accepted
normalized batch_335: 30/30 structural dry-run accepted
normalized batch_336: 30/30 structural dry-run accepted
normalized batch_337: 30/30 structural dry-run accepted
normalized batch_338: 30/30 structural dry-run accepted
normalized batch_339: 30/30 structural dry-run accepted
normalized batch_340-341: 60/60 structural dry-run accepted
normalized batch_342-343: 60/60 structural dry-run accepted
normalized batch_344: 30/30 structural dry-run accepted
normalized batch_345: 30/30 structural dry-run accepted
normalized batch_346: 30/30 structural dry-run accepted
normalized batch_347: 30/30 structural dry-run accepted
normalized batch_348: 30/30 structural dry-run accepted
normalized batch_349: 30/30 structural dry-run accepted
normalized batch_350: 30/30 structural dry-run accepted
normalized batch_351: 30/30 structural dry-run accepted
normalized batch_352: 30/30 structural dry-run accepted
normalized batch_353: 30/30 structural dry-run accepted
normalized batch_354: 30/30 structural dry-run accepted
normalized batch_355: 30/30 structural dry-run accepted
normalized batch_356: 30/30 structural dry-run accepted
normalized batch_357: 30/30 structural dry-run accepted
normalized batch_358: 30/30 structural dry-run accepted
normalized batch_359: 30/30 structural dry-run accepted
normalized batch_360-361: 60/60 structural dry-run accepted
normalized batch_362: 30/30 structural dry-run accepted
normalized batch_363: 30/30 structural dry-run accepted
normalized batch_364: 30/30 structural dry-run accepted
normalized batch_365: 30/30 structural dry-run accepted
normalized batch_366: 30/30 structural dry-run accepted
normalized batch_367-368: 60/60 structural dry-run accepted
normalized batch_369: 30/30 structural dry-run accepted
normalized batch_370: 30/30 structural dry-run accepted
normalized batch_371: 30/30 structural dry-run accepted
normalized batch_372: 30/30 structural dry-run accepted
normalized batch_373: 30/30 structural dry-run accepted
normalized batch_374: 30/30 structural dry-run accepted
normalized batch_375: 30/30 structural dry-run accepted
normalized batch_376: 30/30 structural dry-run accepted
normalized batch_377: 30/30 structural dry-run accepted
normalized batch_378: 30/30 structural dry-run accepted
normalized batch_379: 30/30 structural dry-run accepted
normalized batch_380: 30/30 structural dry-run accepted
normalized batch_381: 30/30 structural dry-run accepted
normalized batch_382: 30/30 structural dry-run accepted
normalized batch_383: 30/30 structural dry-run accepted
normalized batch_384: 30/30 structural dry-run accepted
normalized batch_385: 30/30 structural dry-run accepted
normalized batch_386: 30/30 structural dry-run accepted
normalized batch_387: 30/30 structural dry-run accepted
normalized batch_388: 30/30 structural dry-run accepted
normalized batch_389: 30/30 structural dry-run accepted
normalized batch_390: 30/30 structural dry-run accepted
normalized batch_391: 30/30 structural dry-run accepted
normalized batch_392: 30/30 structural dry-run accepted
normalized batch_393: 30/30 structural dry-run accepted
normalized batch_394: 30/30 structural dry-run accepted
normalized batch_395: 30/30 structural dry-run accepted
normalized batch_396: 30/30 structural dry-run accepted
normalized batch_397: 30/30 structural dry-run accepted
normalized batch_398: 30/30 structural dry-run accepted
normalized batch_399: 30/30 structural dry-run accepted
normalized batch_400: 30/30 structural dry-run accepted
normalized batch_401: 30/30 structural dry-run accepted
normalized batch_402: 30/30 structural dry-run accepted
normalized batch_403: 30/30 structural dry-run accepted
normalized batch_404: 30/30 structural dry-run accepted
normalized batch_405: 30/30 structural dry-run accepted
normalized batch_406: 30/30 structural dry-run accepted
normalized batch_407: 30/30 structural dry-run accepted
normalized batch_408: 30/30 structural dry-run accepted
normalized batch_409: 30/30 structural dry-run accepted
normalized batch_410: 30/30 structural dry-run accepted
normalized batch_411: 30/30 structural dry-run accepted
normalized batch_412: 30/30 structural dry-run accepted
normalized batch_413: 30/30 structural dry-run accepted
normalized batch_414: 30/30 structural dry-run accepted
normalized batch_415: 30/30 structural dry-run accepted
normalized batch_416: 30/30 structural dry-run accepted
normalized batch_417: 30/30 structural dry-run accepted
normalized batch_418: 30/30 structural dry-run accepted
normalized batch_419: 30/30 structural dry-run accepted
normalized batch_420: 30/30 structural dry-run accepted
normalized batch_421: 30/30 structural dry-run accepted
normalized batch_422: 30/30 structural dry-run accepted
normalized batch_423: 30/30 structural dry-run accepted
normalized batch_424: 30/30 structural dry-run accepted
normalized batch_425: 30/30 structural dry-run accepted
normalized batch_426: 30/30 structural dry-run accepted
normalized batch_427: 30/30 structural dry-run accepted
normalized batch_428: 30/30 structural dry-run accepted
normalized batch_429: 30/30 structural dry-run accepted
normalized batch_430: 30/30 structural dry-run accepted
normalized batch_431: 30/30 structural dry-run accepted
normalized batch_432: 30/30 structural dry-run accepted
normalized batch_433: 30/30 structural dry-run accepted
normalized batch_434: 30/30 structural dry-run accepted
normalized batch_435: 30/30 structural dry-run accepted
normalized batch_436: 30/30 structural dry-run accepted
normalized batch_437: 30/30 structural dry-run accepted
normalized batch_438: 30/30 structural dry-run accepted
normalized batch_439: 30/30 structural dry-run accepted
normalized batch_440: 30/30 structural dry-run accepted
normalized batch_441: 30/30 structural dry-run accepted
normalized batch_442: 30/30 structural dry-run accepted
normalized batch_443: 30/30 structural dry-run accepted
normalized batch_444: 30/30 structural dry-run accepted
normalized batch_445: 30/30 structural dry-run accepted
normalized batch_446: 30/30 structural dry-run accepted
normalized batch_447: 30/30 structural dry-run accepted
normalized batch_448: 30/30 structural dry-run accepted
normalized batch_449: 30/30 structural dry-run accepted
normalized batch_450: 30/30 structural dry-run accepted
normalized batch_451: 30/30 structural dry-run accepted
normalized batch_452: 30/30 structural dry-run accepted
normalized batch_453: 30/30 structural dry-run accepted
normalized batch_454: 30/30 structural dry-run accepted
normalized batch_455: 30/30 structural dry-run accepted
normalized batch_456: 30/30 structural dry-run accepted after one synthesis-shape repair
normalized batch_457: 30/30 structural dry-run accepted
normalized batch_458: 30/30 structural dry-run accepted
normalized batch_459: 30/30 structural dry-run accepted
normalized batch_460: 30/30 structural dry-run accepted
normalized batch_461: 30/30 structural dry-run accepted
normalized batch_462: 30/30 structural dry-run accepted
normalized batch_463: 30/30 structural dry-run accepted
normalized batch_464: 30/30 structural dry-run accepted
normalized batch_465: 30/30 structural dry-run accepted
normalized batch_466: 30/30 structural dry-run accepted
normalized batch_467: 30/30 structural dry-run accepted
normalized batch_468: 30/30 structural dry-run accepted
normalized batch_469: 30/30 structural dry-run accepted
normalized batch_470: 30/30 structural dry-run accepted
normalized batch_471: 30/30 structural dry-run accepted
normalized batch_472: 30/30 structural dry-run accepted
normalized batch_473: 30/30 structural dry-run accepted
normalized batch_474: 30/30 structural dry-run accepted
normalized batch_475: 30/30 structural dry-run accepted
normalized batch_476: 30/30 structural dry-run accepted
normalized batch_477: 30/30 structural dry-run accepted
normalized batch_478: 30/30 structural dry-run accepted
normalized batch_479: 30/30 structural dry-run accepted
normalized batch_480: 30/30 structural dry-run accepted
normalized batch_481: 30/30 structural dry-run accepted
normalized batch_482: 30/30 structural dry-run accepted
normalized batch_483: 30/30 structural dry-run accepted
normalized batch_484: 30/30 structural dry-run accepted
normalized batch_485: 30/30 structural dry-run accepted
normalized batch_486: 30/30 structural dry-run accepted
normalized batch_487: 30/30 structural dry-run accepted
normalized batch_488: 30/30 structural dry-run accepted
normalized batch_489: 30/30 structural dry-run accepted
normalized batch_490: 30/30 structural dry-run accepted
normalized batch_491: 30/30 structural dry-run accepted
normalized batch_492: 30/30 structural dry-run accepted
normalized batch_493: 30/30 structural dry-run accepted
normalized batch_494: 30/30 structural dry-run accepted
normalized batch_495: 30/30 structural dry-run accepted
normalized batch_496: 30/30 structural dry-run accepted after one worker retry
normalized batch_497: 30/30 structural dry-run accepted
normalized batch_498: 30/30 structural dry-run accepted
normalized batch_499: 30/30 structural dry-run accepted
normalized batch_500: 30/30 structural dry-run accepted
normalized batch_501: 30/30 structural dry-run accepted
normalized batch_502: 30/30 structural dry-run accepted
normalized batch_503: 30/30 structural dry-run accepted
normalized batch_504: 30/30 structural dry-run accepted after one taxonomy-pattern repair
normalized batch_505: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_506: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_507: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_508: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_509: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_510: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_511: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_512: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_513: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_514: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_515: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_516: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_517: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_518: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_519: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_520: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_521: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_522: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_523: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_524: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_525: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_526: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_527: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_528: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_529: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_530: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_531: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_532: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_533: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_534: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_535: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_536: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_537: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_538: 30/30 structural dry-run accepted via pyrrho-local staging
normalized batch_539: 4/4 structural dry-run accepted via pyrrho-local staging final-tail

```

The planned unmerged target-100 candidate block `batch_026`-`539` is now
structurally clean:

```text
files: 514
rows: 15,394
missing batches: 0
ID-set mismatches against original specs: 0
strict dry-run rejected rows: 0
```

Breakdown:

```text
batch_026-099: 2,220/2,220 accepted after deterministic normalization
batch_100-538: 13,170/13,170 accepted through normal full-row worker waves
batch_539: 4/4 final-tail rows accepted
```

The gap-fill rows `batch_100`-`102` and `batch_139`-`144` were recovered with
slim subagent specs; `batch_142`-`144` needed 10-row shards and were recombined
into normal 30-row files. The follow-up `batch_154`-`271` waves also needed
10-row shards after 30-row slim specs stalled. `batch_270_part3` was split into
two 5-row partial outputs and then mechanically combined in slot order before
the normal gate. Generation resumed on 2026-06-10 through `batch_456`; the
fastest path was one full 30-row batch per worker, with each worker writing
three 10-row shard outputs. `batch_456` initially had one
`synthesis_answer` slot generated as `comparison`; it was repaired to a genuine
`explanation` synthesis row and then passed the normal gate.

The early raw `batch_026`-`099` wave was salvaged by hardening
`scripts/sdgp_normalize_v9_answerability_jsonl.py` for deterministic drift:
invalid class fields from `sdgp_v9_...` IDs, taxonomy aliases,
answerability-shape aliases, missing `meta` objects, inverted scalar drift, and
list-valued context `text`/`summary` fields.

Consolidated structural proof:

```text
data/_workspaces/handoff/v9_answerability/normalized_outputs_026_539_complete
merge dry-run log: data/_workspaces/handoff/v9_answerability/merge_dryrun_026_539_complete.log
result: 15,394 read / 15,394 accepted / 0 rejected / 0 existing
```

Candidate blind-label QA queue:

```text
data/_workspaces/qa/v9_answerability_target100_candidates_026_539
queue rows: 15,394
manifest rows: 15,394
Codex blind shards: codex_subagent_blind_60/shards
shard files: 257 (231 shards x 60 rows, 26 shards x 59 rows)
```

Full Codex-subagent blind-label QA is complete:

```text
prediction shards: 257/257
prediction rows: 15,394/15,394
structural prediction errors: 0
score: 13,988 agreement / 1,406 triage / 0 missing / 0 invalid / 0 error
agreement rate: 90.8666%
score dir: data/_workspaces/qa/v9_answerability_target100_candidates_026_539/score_full_codex_subagents
```

Validated-only merge:

```text
merge batch: v9_answerability_026_539_validated_20260612
validated rows added: 13,988
triage rows skipped: 1,406
rejected rows: 0
active vault size after merge: 39,330
```

The merge used `scripts/sdgp_merge_v9_answerability_jsonl.py --case-id-allowlist`
with `blind_label_validated.jsonl`, so triage rows were not admitted into the
active vault.

Candidate structural dry-run:

```powershell
python scripts/sdgp_merge_v9_answerability_jsonl.py `
  --out-dir data/_workspaces/handoff/v9_answerability/normalized_outputs_026_539_complete `
  --batch-dir data/_workspaces/handoff/v9_answerability/subagent_batches `
  --dry-run
```

Candidate blind-label queue:

```powershell
python scripts/sdgp_build_blind_label_from_generation_jsonl.py `
  --out-dir data/_workspaces/handoff/v9_answerability/normalized_outputs_026_539_complete `
  --qa-dir data/_workspaces/qa/v9_answerability_target100_candidates_026_539 `
  --version fitz-gov-9.0 `
  --dataset-version v9
```

Accepted rows may be merged only after the structural dry-run and blind-label
QA are clean. The merge script rejects missing `case.id`, `version`,
`meta.dataset_version`, `meta.modality`, target-cell mismatches, forbidden
legacy fields, duplicate output IDs, and duplicate case content. If any row is
rejected, a live merge writes nothing.

## Non-Goals

- Do not rewrite correct `direct_answer` rows just to flatten the distribution.
- Do not make the first V9 hard matrix include retrieval action, gap type, and
  retrieval modality all at once; that explodes the cell space.
- Do not mutate `data/fitz-gov/cases.jsonl` before generated candidates pass
  structural checks and blind-label QA.

## Next Step

V9 target-100 is published. Rebuild pyrrho-side V9 training prep from the
official query-grouped public splits and train the first `pyrrho-nano-g4`
candidate.

Final target-100 closeout:

```text
local vault size: 40,755 rows
target/cell: 100
cells considered: 189
cells at target: 189
empty cells: 0
gap to fill: 0
set_answer: 6,308 rows / gap 0
structured_reasoning: 6,302 rows / gap 0
synthesis_answer: 6,309 rows / gap 0
final report: data/_workspaces/qa/v9_answerability_closure_buffer_20260612/gap_after_closure_buffer_validated_merge.json
HF dataset: yafitzdev/fitz-gov
HF tag: v9.0.0
HF commit: 874fd18d4952eec0e72b6df2264f8281615fd350
public splits: train 32,625 / validation 4,104 / test 4,026
V9-only splits: train 12,951 / validation 1,645 / test 1,567
exact-query split leakage: 0
```

Validated-only merge sequence:

```text
initial target-100 block: 13,988/15,394 validated, 1,406 triage skipped
replacement block: 1,219/1,406 validated, 187 triage skipped
final replacement block: 177/187 validated, 10 triage skipped
closure buffer: 29/30 validated, 1 triage skipped
```

The active vault only admitted rows that passed both strict structural dry-run
and independent blind-label agreement. Triage rows remain unmerged.




