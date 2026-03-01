# Phase 3: Write Test Suite

**Priority:** P0 (blocks release)
**Scope:** New `tests/` directory, >80% code coverage
**Files created:** 6 new test files + conftest.py

## Problem

Zero unit tests exist. `pyproject.toml` line 75 points to `testpaths = ["tests"]` but
the directory doesn't exist. Core evaluation logic, data loading, model serialization,
and data integrity are completely untested.

## Solution

Create a comprehensive test suite covering all core modules.

## Test Files

### `tests/conftest.py` — Shared fixtures

```python
# Fixtures needed:
# - sample_case() -> FitzGovCase with all fields populated
# - sample_grounding_case() -> case with forbidden_claims
# - sample_relevance_case() -> case with required_elements
# - sample_governance_case() -> case for each category
# - tier0_cases() -> load actual tier0 data
# - tier1_sample() -> 10 cases from tier1 (2 per governance cat, 1 ground, 1 relevance)
# - evaluator() -> FitzGovEvaluator(llm_validation=False)
```

### `tests/test_models.py` — Data model tests (~20 tests)

| Test | What it verifies |
|------|------------------|
| `test_answer_mode_values` | TRUSTWORTHY, DISPUTED, ABSTAIN exist |
| `test_category_values` | All 6 categories exist |
| `test_case_to_dict_roundtrip` | `from_dict(case.to_dict()) == case` |
| `test_case_to_dict_includes_classification` | domain, query_type etc. in dict |
| `test_case_to_dict_omits_empty_optionals` | No forbidden_claims key if empty |
| `test_case_from_dict_defaults` | Missing optional fields get defaults |
| `test_case_result_to_dict` | CaseResult serializes correctly |
| `test_category_result_to_dict` | CategoryResult with accuracy |
| `test_confusion_matrix_add` | Adding predictions updates matrix |
| `test_confusion_matrix_accuracy` | Accuracy calculation |
| `test_fitz_gov_result_str` | Result __str__ includes all categories |
| `test_tier0_result_passed` | Tier0Result with threshold |
| `test_tier1_result_difficulty_breakdown` | Difficulty breakdown dict |
| `test_tiered_result_gating` | Tier0 fail -> tier1 None |
| `test_tiered_result_str` | TieredResult __str__ format |

### `tests/test_loader.py` — Data loading tests (~15 tests)

| Test | What it verifies |
|------|------------------|
| `test_load_tier0` | Returns 60 cases |
| `test_load_tier1` | Returns 1,679 cases (or current count) |
| `test_load_tier0_categories` | All 6 categories present |
| `test_load_tier1_categories` | All 6 categories present |
| `test_load_tier_filter_category` | Filtering by category works |
| `test_load_cases_all` | Returns tier0 + tier1 combined |
| `test_load_case_by_id_tier0` | Finds a t0_ case |
| `test_load_case_by_id_tier1` | Finds a t1_ case |
| `test_load_case_by_id_missing` | Returns None for bad ID |
| `test_case_has_category` | Every loaded case has category field |
| `test_case_has_classification_fields` | domain, query_type etc. present |
| `test_get_tier_info` | Returns correct counts per tier |
| `test_get_category_info` | Returns correct counts per category |
| `test_tier_enum` | Tier.SANITY and Tier.CORE values |
| `test_legacy_structure_detection` | Handles old data/ layout gracefully |

### `tests/test_evaluator.py` — Evaluation logic tests (~25 tests)

| Test | What it verifies |
|------|------------------|
| **Governance mode** | |
| `test_abstention_correct_mode` | ABSTAIN expected, ABSTAIN given = pass |
| `test_abstention_wrong_mode` | ABSTAIN expected, TRUSTWORTHY given = fail |
| `test_dispute_correct_mode` | DISPUTED expected, DISPUTED given = pass |
| `test_trustworthy_correct_mode` | TRUSTWORTHY expected, TRUSTWORTHY given = pass |
| `test_mode_case_insensitive` | Mode matching ignores case |
| **Grounding evaluation** | |
| `test_grounding_no_forbidden_match` | Response without forbidden pattern = pass |
| `test_grounding_forbidden_match` | Response with forbidden pattern = fail |
| `test_grounding_allowed_phrase_override` | Forbidden match but in allowed_phrases = pass |
| `test_grounding_regex_case_insensitive` | Case insensitive regex matching |
| `test_grounding_multiple_patterns` | Fails if ANY pattern matches |
| **Relevance evaluation** | |
| `test_relevance_required_present` | Response with required element = pass |
| `test_relevance_required_missing` | Response without any required element = fail |
| `test_relevance_min_required_1` | Only 1 of N required = pass (default) |
| `test_relevance_min_required_2` | Need 2 of N required elements |
| **Batch evaluation** | |
| `test_evaluate_all_returns_result` | evaluate_all returns FitzGovResult |
| `test_evaluate_all_category_breakdown` | Results per category |
| `test_evaluate_all_confusion_matrix` | Matrix populated |
| **Tiered evaluation** | |
| `test_tiered_tier0_pass` | Tier0 above threshold |
| `test_tiered_tier0_fail_gates_tier1` | Tier0 below threshold -> tier1 skipped |
| `test_tiered_tier0_pass_runs_tier1` | Tier0 pass -> tier1 evaluated |
| `test_tiered_difficulty_breakdown` | Hard/medium breakdown in tier1 |
| **Edge cases** | |
| `test_empty_response` | Empty string response |
| `test_empty_contexts` | Case with no contexts |
| `test_evaluate_case_returns_case_result` | Single case evaluation |

### `tests/test_validate.py` — Validation logic tests (~15 tests)

| Test | What it verifies |
|------|------------------|
| `test_check_quality_valid_case` | Valid case passes all checks |
| `test_check_quality_missing_id` | Catches missing ID |
| `test_check_quality_missing_query` | Catches missing query |
| `test_check_quality_short_query` | Catches query < 10 chars |
| `test_check_quality_invalid_mode` | Catches bad expected_mode value |
| `test_check_quality_no_contexts` | Catches empty contexts array |
| `test_check_quality_grounding_no_forbidden` | Catches grounding without forbidden_claims |
| `test_check_quality_relevance_no_required` | Catches relevance without required_elements |
| `test_check_quality_context_sources_valid` | Valid context_sources passes |
| `test_check_quality_context_sources_invalid` | Bad context_sources caught |
| `test_find_exact_duplicates` | Detects duplicate case IDs |
| `test_find_semantic_duplicates` | Detects near-duplicate queries |
| `test_validate_classification_fields` | Validates domain/query_type enums |
| `test_validate_category_field` | Validates category matches filename |
| `test_validate_evaluation_config` | Validates config structure |

### `tests/test_data_integrity.py` — Data file integrity (~15 tests)

| Test | What it verifies |
|------|------------------|
| `test_all_tier0_files_parse` | All 6 tier0 JSON files are valid |
| `test_all_tier1_files_parse` | All 6 tier1 JSON files are valid |
| `test_no_duplicate_ids` | No duplicate case IDs across all files |
| `test_all_cases_have_required_fields` | id, query, contexts, expected_mode |
| `test_all_cases_have_category` | After Phase 2 backfill |
| `test_all_cases_have_evaluation_config` | After Phase 2 backfill |
| `test_all_cases_have_classification` | domain, query_type, etc. |
| `test_valid_expected_modes` | Only trustworthy/disputed/abstain |
| `test_valid_domains` | All domains in approved set |
| `test_valid_query_types` | All query_types in approved set |
| `test_valid_reasoning_types` | All reasoning_types in approved set |
| `test_valid_evidence_patterns` | All evidence_patterns in approved set |
| `test_grounding_have_forbidden_claims` | All grounding cases |
| `test_relevance_have_required_elements` | All relevance cases |
| `test_context_count_matches_contexts` | context_count == len(contexts) |

### `tests/test_cli.py` — CLI command tests (~5 tests)

| Test | What it verifies |
|------|------------------|
| `test_cli_stats_runs` | `stats` command exits 0 |
| `test_cli_validate_runs` | `validate` command exits 0 |
| `test_cli_stats_output` | Output contains case counts |
| `test_cli_help` | `--help` exits 0 |
| `test_cli_stats_verbose` | `-v` flag shows subcategories |

## Implementation

### Step 1: Create tests directory structure
```
tests/
  __init__.py
  conftest.py
  test_models.py
  test_loader.py
  test_evaluator.py
  test_validate.py
  test_data_integrity.py
  test_cli.py
```

### Step 2: Write conftest.py with fixtures
### Step 3: Write test files (can be parallelized)
### Step 4: Run and ensure >80% coverage
```bash
pytest tests/ -v --cov=fitz_gov --cov-report=term-missing
```

### Step 5: Fix any bugs discovered by tests

## Estimated Scope

- Fixtures + test_models: ~1 hour
- test_loader + test_data_integrity: ~1 hour
- test_evaluator: ~1.5 hours (most complex)
- test_validate + test_cli: ~1 hour
- Bug fixes: ~1 hour
- Total: ~5.5 hours
