# fitz-gov v5.0 Release Plan

## Summary

v5.0 addresses every known quality, structural, and testing gap in the benchmark.
The work is split into 8 sequential phases, each independently committable.

## Current State (v4.1)

- 1,739 total cases (60 tier0 + 1,679 tier1)
- 6 categories, 18 domains, 10 query types
- 6 classification attributes on every case
- 0% unit test coverage
- 49% of cases missing `category` field
- 100% of cases missing `evaluation_config`
- Grounding/relevance contexts are template-generated (median 17-23 words)
- 91% of tier1 cases are "hard" difficulty

## Phase Sequence

| # | Phase | Priority | Cases Touched | Key Deliverable |
|---|-------|----------|---------------|-----------------|
| 1 | [Rewrite grounding/relevance content](./01-REWRITE-CONTENT.md) | P0 | 336 | Rich, unique contexts (50-200 words each) |
| 2 | [Backfill structural fields](./02-BACKFILL-FIELDS.md) | P0 | 1,679 | `category` + `evaluation_config` on all cases |
| 3 | [Write test suite](./03-TEST-SUITE.md) | P0 | 0 | >80% code coverage, CI-ready |
| 4 | [Add medium-difficulty cases](./04-DIFFICULTY-BALANCE.md) | P1 | ~300 new | 35% medium / 65% hard in tier1 |
| 5 | [Evaluator slicing support](./05-EVALUATOR-SLICING.md) | P1 | 0 | Per-domain/query-type accuracy reporting |
| 6 | [Expand sparse subcategories](./06-SPARSE-SUBCATS.md) | P1 | ~50 new | All subcategories >= 5 cases |
| 7 | [Deduplicate queries](./07-DEDUPLICATE.md) | P1 | ~27 removed | Zero duplicate queries |
| 8 | [Documentation and version bump](./08-DOCS-VERSION.md) | P2 | 0 | CLAUDE.md, CHANGELOG, pyproject.toml = 5.0.0 |

## Expected Final State (v5.0)

| Metric | v4.1 | v5.0 |
|--------|------|------|
| Total tier1 cases | 1,679 | ~2,000 |
| Unit test coverage | 0% | >80% |
| Cases with `category` field | 51% | 100% |
| Cases with `evaluation_config` | 0% | 100% |
| Grounding median context words | 17 | ~100 |
| Relevance median context words | 23 | ~80 |
| Unique grounding queries | ~180/200 | 200/200 |
| Unique relevance queries | ~190/202 | 202/202 |
| Difficulty: medium share | 8.7% | ~30% |
| Subcategories with <5 cases | 15 | 0 |
| Duplicate queries | 27 | 0 |
| Evaluator slicing dimensions | 0 | 6 |
| Version | 3.0.0/4.1.0 (conflicting) | 5.0.0 |

## Execution Notes

- Each phase has its own plan file with detailed steps
- Phases are designed to be executed sequentially (later phases may depend on earlier ones)
- Each phase should be committed separately
- Run `python -m fitz_gov.cli validate --data-dir data` after each data-touching phase
