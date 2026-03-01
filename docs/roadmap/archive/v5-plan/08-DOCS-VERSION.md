# Phase 8: Documentation & Version Bump

**Priority:** P2 (release readiness)
**Scope:** Update docs, fix stale references, bump version to 5.0.0
**Files modified:** `CLAUDE.md`, `pyproject.toml`, `README.md`, `data/corpus/manifest.json`

## Problem

Several documentation and configuration files contain stale information:

1. **CLAUDE.md** says "Current version: 1.0.0 with 200 test cases" — wrong on both counts
2. **CLAUDE.md** data structure section shows the old flat `data/` layout, not the tiered
   `data/tier0_sanity/` + `data/tier1_core/` structure
3. **CLAUDE.md** lists `qualification` and `confidence` categories which were renamed to
   `trustworthy_hedged` and `trustworthy_direct` in v4
4. **pyproject.toml** version is `3.0.0` — needs to be `5.0.0`
5. **manifest.json** version will need updating after all data changes
6. **README.md** may need updates after phases 1-7 change case counts

## Solution

Update all stale references after phases 1-7 are complete.

## Implementation

### Step 1: Update CLAUDE.md

```markdown
# Changes needed:
- Version: "1.0.0 with 200 test cases" → "5.0.0 with ~N test cases" (actual count)
- Data structure: replace flat layout with tiered layout
- Categories: replace qualification/confidence with trustworthy_hedged/trustworthy_direct
- Key enums: update AnswerMode values (QUALIFIED/CONFIDENT → TRUSTWORTHY/HEDGED)
- Add mention of classification fields (domain, query_type, etc.)
- Add mention of tiered evaluation (tier0 gating → tier1 full eval)
```

### Step 2: Update pyproject.toml
```toml
version = "5.0.0"
```

### Step 3: Update manifest.json
Run stats to get final counts, then update manifest:
```bash
python -m fitz_gov.cli stats --data-dir data
# Use output to update manifest.json version and counts
```

### Step 4: Update README.md
After all phases complete:
- Verify case count tables are still accurate
- Update any references to version numbers
- Add mention of deduplication and difficulty balance improvements

### Step 5: Final validation
```bash
python -m fitz_gov.cli validate --data-dir data
python -m fitz_gov.cli stats --data-dir data
pytest tests/  # After Phase 3 creates the test suite
```

## Validation Criteria

- CLAUDE.md accurately describes the current data structure
- CLAUDE.md version matches pyproject.toml version
- pyproject.toml version is 5.0.0
- manifest.json version matches
- README.md case counts match actual data
- All CLI commands run without errors

## Estimated Scope

- CLAUDE.md rewrite: ~20 minutes
- Other file updates: ~10 minutes
- Validation: ~10 minutes
