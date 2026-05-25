# V8 Taxonomy Expansion Plan

V8 adds the discovered governance gaps as first-class `taxonomy.pattern` values.
It does not add subpattern fields and does not rewrite existing rows.

## Summary

- New primary patterns: **5**
- Current primary domains: **7**
- Difficulties: **3**
- New cells: **105**
- Probe target: **5 rows/cell = 525 rows**
- Full V7-style parity at 25 rows/cell: **2625 rows**

## Local Status

The 525-row probe pack has been generated and merged into the local vault:

- Vault total: **11025 rows**
- V8 rows: **525**
- Cell coverage: **105/105 cells at 5 rows/cell**
- Training-schema audit: **525/525 complete**
- Forbidden old/shim fields: **0**
- Exact duplicate checker hashes: **0**
- Query-group leakage: **0**
- QA artifacts: `data/sdgp_v8_qa/`
- Blind-label QA: LM Studio `qwen3.6-35b-a3b@q5_k_s` scored **525/525** rows.
- Triage repair: repaired all 210 rows in the two affected patterns, `missing_execution_result` and `authority_status_conflict`, after the initial pass found **502 validated / 23 triage**.
- Final blind-label result: **525 validated / 0 triage**, with **0 missing / 0 invalid / 0 error**.

## Pattern Targets

| pattern | class | cells | probe rows |
|---|---:|---:|---:|
| `resolved_candidate_selection` | TRUSTWORTHY | 21 | 105 |
| `verdict_conflict` | DISPUTED | 21 | 105 |
| `authority_status_conflict` | DISPUTED | 21 | 105 |
| `version_build_mismatch` | ABSTAIN | 21 | 105 |
| `missing_execution_result` | ABSTAIN | 21 | 105 |

## Cells

| cell_id | governance_class | domain | difficulty |
|---|---|---|---|
| **resolved_candidate_selection** |  |  |  |
| resolved_candidate_selection__science_medicine__easy | TRUSTWORTHY | science_medicine | easy |
| resolved_candidate_selection__science_medicine__medium | TRUSTWORTHY | science_medicine | medium |
| resolved_candidate_selection__science_medicine__hard | TRUSTWORTHY | science_medicine | hard |
| resolved_candidate_selection__law_policy__easy | TRUSTWORTHY | law_policy | easy |
| resolved_candidate_selection__law_policy__medium | TRUSTWORTHY | law_policy | medium |
| resolved_candidate_selection__law_policy__hard | TRUSTWORTHY | law_policy | hard |
| resolved_candidate_selection__history_geography__easy | TRUSTWORTHY | history_geography | easy |
| resolved_candidate_selection__history_geography__medium | TRUSTWORTHY | history_geography | medium |
| resolved_candidate_selection__history_geography__hard | TRUSTWORTHY | history_geography | hard |
| resolved_candidate_selection__technology_computing__easy | TRUSTWORTHY | technology_computing | easy |
| resolved_candidate_selection__technology_computing__medium | TRUSTWORTHY | technology_computing | medium |
| resolved_candidate_selection__technology_computing__hard | TRUSTWORTHY | technology_computing | hard |
| resolved_candidate_selection__economics_finance__easy | TRUSTWORTHY | economics_finance | easy |
| resolved_candidate_selection__economics_finance__medium | TRUSTWORTHY | economics_finance | medium |
| resolved_candidate_selection__economics_finance__hard | TRUSTWORTHY | economics_finance | hard |
| resolved_candidate_selection__culture_society__easy | TRUSTWORTHY | culture_society | easy |
| resolved_candidate_selection__culture_society__medium | TRUSTWORTHY | culture_society | medium |
| resolved_candidate_selection__culture_society__hard | TRUSTWORTHY | culture_society | hard |
| resolved_candidate_selection__general_commonsense__easy | TRUSTWORTHY | general_commonsense | easy |
| resolved_candidate_selection__general_commonsense__medium | TRUSTWORTHY | general_commonsense | medium |
| resolved_candidate_selection__general_commonsense__hard | TRUSTWORTHY | general_commonsense | hard |
| **verdict_conflict** |  |  |  |
| verdict_conflict__science_medicine__easy | DISPUTED | science_medicine | easy |
| verdict_conflict__science_medicine__medium | DISPUTED | science_medicine | medium |
| verdict_conflict__science_medicine__hard | DISPUTED | science_medicine | hard |
| verdict_conflict__law_policy__easy | DISPUTED | law_policy | easy |
| verdict_conflict__law_policy__medium | DISPUTED | law_policy | medium |
| verdict_conflict__law_policy__hard | DISPUTED | law_policy | hard |
| verdict_conflict__history_geography__easy | DISPUTED | history_geography | easy |
| verdict_conflict__history_geography__medium | DISPUTED | history_geography | medium |
| verdict_conflict__history_geography__hard | DISPUTED | history_geography | hard |
| verdict_conflict__technology_computing__easy | DISPUTED | technology_computing | easy |
| verdict_conflict__technology_computing__medium | DISPUTED | technology_computing | medium |
| verdict_conflict__technology_computing__hard | DISPUTED | technology_computing | hard |
| verdict_conflict__economics_finance__easy | DISPUTED | economics_finance | easy |
| verdict_conflict__economics_finance__medium | DISPUTED | economics_finance | medium |
| verdict_conflict__economics_finance__hard | DISPUTED | economics_finance | hard |
| verdict_conflict__culture_society__easy | DISPUTED | culture_society | easy |
| verdict_conflict__culture_society__medium | DISPUTED | culture_society | medium |
| verdict_conflict__culture_society__hard | DISPUTED | culture_society | hard |
| verdict_conflict__general_commonsense__easy | DISPUTED | general_commonsense | easy |
| verdict_conflict__general_commonsense__medium | DISPUTED | general_commonsense | medium |
| verdict_conflict__general_commonsense__hard | DISPUTED | general_commonsense | hard |
| **authority_status_conflict** |  |  |  |
| authority_status_conflict__science_medicine__easy | DISPUTED | science_medicine | easy |
| authority_status_conflict__science_medicine__medium | DISPUTED | science_medicine | medium |
| authority_status_conflict__science_medicine__hard | DISPUTED | science_medicine | hard |
| authority_status_conflict__law_policy__easy | DISPUTED | law_policy | easy |
| authority_status_conflict__law_policy__medium | DISPUTED | law_policy | medium |
| authority_status_conflict__law_policy__hard | DISPUTED | law_policy | hard |
| authority_status_conflict__history_geography__easy | DISPUTED | history_geography | easy |
| authority_status_conflict__history_geography__medium | DISPUTED | history_geography | medium |
| authority_status_conflict__history_geography__hard | DISPUTED | history_geography | hard |
| authority_status_conflict__technology_computing__easy | DISPUTED | technology_computing | easy |
| authority_status_conflict__technology_computing__medium | DISPUTED | technology_computing | medium |
| authority_status_conflict__technology_computing__hard | DISPUTED | technology_computing | hard |
| authority_status_conflict__economics_finance__easy | DISPUTED | economics_finance | easy |
| authority_status_conflict__economics_finance__medium | DISPUTED | economics_finance | medium |
| authority_status_conflict__economics_finance__hard | DISPUTED | economics_finance | hard |
| authority_status_conflict__culture_society__easy | DISPUTED | culture_society | easy |
| authority_status_conflict__culture_society__medium | DISPUTED | culture_society | medium |
| authority_status_conflict__culture_society__hard | DISPUTED | culture_society | hard |
| authority_status_conflict__general_commonsense__easy | DISPUTED | general_commonsense | easy |
| authority_status_conflict__general_commonsense__medium | DISPUTED | general_commonsense | medium |
| authority_status_conflict__general_commonsense__hard | DISPUTED | general_commonsense | hard |
| **version_build_mismatch** |  |  |  |
| version_build_mismatch__science_medicine__easy | ABSTAIN | science_medicine | easy |
| version_build_mismatch__science_medicine__medium | ABSTAIN | science_medicine | medium |
| version_build_mismatch__science_medicine__hard | ABSTAIN | science_medicine | hard |
| version_build_mismatch__law_policy__easy | ABSTAIN | law_policy | easy |
| version_build_mismatch__law_policy__medium | ABSTAIN | law_policy | medium |
| version_build_mismatch__law_policy__hard | ABSTAIN | law_policy | hard |
| version_build_mismatch__history_geography__easy | ABSTAIN | history_geography | easy |
| version_build_mismatch__history_geography__medium | ABSTAIN | history_geography | medium |
| version_build_mismatch__history_geography__hard | ABSTAIN | history_geography | hard |
| version_build_mismatch__technology_computing__easy | ABSTAIN | technology_computing | easy |
| version_build_mismatch__technology_computing__medium | ABSTAIN | technology_computing | medium |
| version_build_mismatch__technology_computing__hard | ABSTAIN | technology_computing | hard |
| version_build_mismatch__economics_finance__easy | ABSTAIN | economics_finance | easy |
| version_build_mismatch__economics_finance__medium | ABSTAIN | economics_finance | medium |
| version_build_mismatch__economics_finance__hard | ABSTAIN | economics_finance | hard |
| version_build_mismatch__culture_society__easy | ABSTAIN | culture_society | easy |
| version_build_mismatch__culture_society__medium | ABSTAIN | culture_society | medium |
| version_build_mismatch__culture_society__hard | ABSTAIN | culture_society | hard |
| version_build_mismatch__general_commonsense__easy | ABSTAIN | general_commonsense | easy |
| version_build_mismatch__general_commonsense__medium | ABSTAIN | general_commonsense | medium |
| version_build_mismatch__general_commonsense__hard | ABSTAIN | general_commonsense | hard |
| **missing_execution_result** |  |  |  |
| missing_execution_result__science_medicine__easy | ABSTAIN | science_medicine | easy |
| missing_execution_result__science_medicine__medium | ABSTAIN | science_medicine | medium |
| missing_execution_result__science_medicine__hard | ABSTAIN | science_medicine | hard |
| missing_execution_result__law_policy__easy | ABSTAIN | law_policy | easy |
| missing_execution_result__law_policy__medium | ABSTAIN | law_policy | medium |
| missing_execution_result__law_policy__hard | ABSTAIN | law_policy | hard |
| missing_execution_result__history_geography__easy | ABSTAIN | history_geography | easy |
| missing_execution_result__history_geography__medium | ABSTAIN | history_geography | medium |
| missing_execution_result__history_geography__hard | ABSTAIN | history_geography | hard |
| missing_execution_result__technology_computing__easy | ABSTAIN | technology_computing | easy |
| missing_execution_result__technology_computing__medium | ABSTAIN | technology_computing | medium |
| missing_execution_result__technology_computing__hard | ABSTAIN | technology_computing | hard |
| missing_execution_result__economics_finance__easy | ABSTAIN | economics_finance | easy |
| missing_execution_result__economics_finance__medium | ABSTAIN | economics_finance | medium |
| missing_execution_result__economics_finance__hard | ABSTAIN | economics_finance | hard |
| missing_execution_result__culture_society__easy | ABSTAIN | culture_society | easy |
| missing_execution_result__culture_society__medium | ABSTAIN | culture_society | medium |
| missing_execution_result__culture_society__hard | ABSTAIN | culture_society | hard |
| missing_execution_result__general_commonsense__easy | ABSTAIN | general_commonsense | easy |
| missing_execution_result__general_commonsense__medium | ABSTAIN | general_commonsense | medium |
| missing_execution_result__general_commonsense__hard | ABSTAIN | general_commonsense | hard |

## Row Contract

- Use the current SDGP row shape: `id`, `version`, `input`, `governance`, `taxonomy`, `routing`, `meta`, `evaluation`.
- New rows use `version: "fitz-gov-8.0"` and `meta.dataset_version: "v8"`.
- Do not add `taxonomy.subpattern`, `taxonomy.subpattern_cell_id`, `taxonomy.subpattern_description`, or `meta.introduced_in`.
- Do not reintroduce `meta.domain`, `meta.subcategory`, `meta.reasoning_type`, `meta.query_type`, or `meta.evidence_pattern`.
