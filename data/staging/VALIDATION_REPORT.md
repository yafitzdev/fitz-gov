# Staging Validation Report

**Date**: 2026-02-08
**Total new cases**: 525
**Total existing cases (tier0+tier1)**: 331
**Staging files**: 7

## File Summary

| File | Cases | Modes |
|------|-------|-------|
| gen_boundary_abstain.json | 65 | abstain:40, qualified:25 |
| gen_boundary_confident.json | 45 | confident:35, qualified:10 |
| gen_dq_boundary_1.json | 70 | disputed:20, qualified:50 |
| gen_dq_boundary_2.json | 70 | confident:10, disputed:10, qualified:50 |
| gen_pure_abstain_dispute.json | 90 | abstain:50, disputed:40 |
| gen_pure_qualify_confident.json | 95 | confident:35, qualified:60 |
| gen_threeway.json | 90 | abstain:12, confident:12, qualified:66 |

---

## 1. Schema Violations

**0 violations. All 525 cases pass schema checks.**

Every case has all required fields (`id`, `category`, `subcategory`, `difficulty`, `query`, `contexts`, `expected_mode`, `description`, `rationale`), correct ID format (`t1_<cat>_hard_NNN`), valid category-mode mapping, difficulty="hard", query length 10-500 chars, 1-10 non-empty contexts, and non-empty description/rationale.

---

## 2. ID Uniqueness

**0 issues. All IDs are unique across new and existing cases.**

No duplicate IDs found within the 525 new cases, and no ID conflicts with any of the 331 existing tier0/tier1 cases.

---

## 3. Query Duplicates

### Exact Duplicates (5 found - BLOCKERS)

| New Case | Duplicate Of | Query | Issue Type |
|----------|-------------|-------|------------|
| t1_qualify_hard_332 | t1_qualify_hard_215 (new) | "What is the market share of electric vehicles in Norway?" | Internal same-mode dupe |
| t1_confident_hard_104 | t1_dispute_hard_117 (new) | "Who invented the World Wide Web?" | **Internal cross-mode conflict** |
| t1_confident_hard_132 | t1_abstain_medium_004 (existing) | "What is the population of Tokyo?" | **Cross-mode conflict with existing** |
| t1_confident_hard_605 | t1_confident_hard_030 (existing) | "What is the speed of light?" | Same-mode dupe with existing |
| t1_qualify_hard_660 | t1_abstain_medium_013 (existing) | "What is the current price of Bitcoin?" | **Cross-mode conflict with existing** |

**Cross-mode analysis**:
- `t1_confident_hard_104` says "confident" for "Who invented the WWW?" (contexts: CERN + ACM both credit Berners-Lee). `t1_dispute_hard_117` says "disputed" for the same query (contexts: CERN credits Berners-Lee alone vs Belgian Academy credits Cailliau as co-inventor). This is a valid pedagogical scenario -- same question, different contexts produce different modes -- but having identical query text in the benchmark is problematic for evaluation. **Remove the confident version** (t1_confident_hard_104) since the dispute case is more interesting/harder.
- `t1_confident_hard_132` (confident, contexts about Tokyo) vs existing `t1_abstain_medium_004` (abstain). Same query text, different contexts. **Remove the new case.**
- `t1_qualify_hard_660` (qualified) vs existing `t1_abstain_medium_013` (abstain). Same query text. **Remove the new case.**

### Near-Duplicates (Jaccard > 0.75) -- 13 pairs

These are flagged for manual review but are **not blockers** unless noted.

#### Within new cases (7 pairs)

| Case A | Case B | Jaccard | Assessment |
|--------|--------|---------|------------|
| t1_abstain_hard_259 | t1_qualify_hard_452 | 0.83 | OK - different countries (Japan vs Brazil) |
| t1_qualify_hard_212 | t1_qualify_hard_124 | 0.78 | OK - different sectors (manufacturing vs technology) |
| t1_qualify_hard_215 | t1_qualify_hard_122 | 0.82 | OK - different regions (Norway vs US) |
| t1_qualify_hard_244 | t1_dispute_hard_105 | 0.78 | OK - different framing (weight management vs weight loss), cross-mode |
| t1_dispute_hard_105 | t1_qualify_hard_603 | 0.88 | **BORDERLINE** - "long-term weight loss" vs "weight loss", very similar |
| t1_confident_hard_132 | t1_confident_hard_604 | 0.86 | MOOT - t1_confident_hard_132 already flagged for removal |
| t1_confident_hard_134 | t1_confident_hard_602 | 0.88 | **BORDERLINE** - "melting point of gold" vs "melting point of pure gold" |

#### New vs existing (6 pairs)

| New Case | Existing Case | Jaccard | Assessment |
|----------|--------------|---------|------------|
| t1_abstain_hard_200 | t1_abstain_medium_009 | 0.88 | **BORDERLINE** - "treatment protocol for Parkinson's" vs "treatment for Parkinson's" |
| t1_qualify_hard_130 | t1_qualify_hard_031 | 0.86 | OK - "migration project" vs "project" (more specific) |
| t1_qualify_hard_134 | t0_confident_easy_009 | 0.86 | OK - "the application" vs "the grant application" (cross-mode too) |
| t1_confident_hard_604 | t1_abstain_medium_004 | 0.86 | MOOT - related to already-removed t1_confident_hard_132 |
| t1_qualify_hard_613 | t1_abstain_hard_018 | 0.80 | OK - more specific (pattern matching features vs new features) |
| t1_qualify_hard_618 | t1_abstain_hard_024 | 0.86 | **BORDERLINE** - "CEO of Twitter" vs "current CEO of Twitter" |

---

## 4. Quality Spot Check

### Context Statistics (all 525 cases, 1151 total contexts)

| Metric | Value |
|--------|-------|
| Min context length | 331 chars |
| Max context length | 1514 chars |
| Mean context length | 848 chars |
| Median context length | 856 chars |
| Contexts < 200 chars | 0 |

All contexts are substantial (300+ chars minimum). No template markers or placeholder text detected.

### Manual Content Review (35 cases sampled across all 7 files)

All 35 sampled cases received **PASS** ratings:

| File | Cases Sampled | Result | Notes |
|------|--------------|--------|-------|
| gen_boundary_abstain.json | 5 | All PASS | Contexts are topically adjacent but don't answer the query (correct for abstain). Qualified cases have genuine hedging. |
| gen_boundary_confident.json | 5 | All PASS | Single-context confident cases are clear and unambiguous. Two-context cases show convergence. |
| gen_dq_boundary_1.json | 5 | All PASS | Disputed cases have genuine factual contradictions. Qualified cases have nuanced differences. |
| gen_dq_boundary_2.json | 5 | All PASS | Good variety of domains. Contexts read like real documents with specific data. |
| gen_pure_abstain_dispute.json | 5 | All PASS | Strong abstain cases (e.g., Alzheimer's contexts for Parkinson's query). Disputes have clear contradictions. |
| gen_pure_qualify_confident.json | 5 | All PASS | Good balance of efficacy-vs-safety qualification patterns. Confident cases have strong multi-source convergence. |
| gen_threeway.json | 5 | All PASS | Three-context cases include good mix of peer-reviewed + blog/informal + newer study patterns. |

### Specific Noteworthy Cases (Manual Deep Review)

**t1_abstain_hard_100** (abstain) - Query about Parkinson's tremor treatment; contexts are about Alzheimer's. Well-constructed misdirection -- the diseases are both neurodegenerative but treatments differ fundamentally. Correct abstain.

**t1_dispute_hard_100** (disputed) - Rivian FY2024 revenue: $4.97B (10-K filing) vs $5.34B (Bloomberg). The description notes methodology differences. Legitimate dispute with good sourcing.

**t1_dispute_hard_117** (disputed) - WWW invention: CERN credits Berners-Lee alone vs Belgian Academy credits Cailliau as co-inventor. Historically nuanced dispute. High quality.

**t1_qualify_hard_100** (qualified) - Drug efficacy vs safety: strong Phase III data but hepatotoxicity signals. Classic qualification pattern, well-executed.

**t1_confident_hard_100** (confident) - Linux kernel language: multiple authoritative sources (code analysis + official docs + Torvalds quotes) all confirm C. Clean confident case.

**t1_qualify_hard_603** (qualified, threeway) - Intermittent fasting: 2019 NEJM review (positive), blog (exaggerated), 2023 JAMA trial (questioning unique benefit). Good evolution-of-evidence pattern.

---

## 5. Mode Distribution

| Mode | Count | Percentage |
|------|-------|------------|
| abstain | 102 | 19.4% |
| confident | 92 | 17.5% |
| disputed | 70 | 13.3% |
| qualified | 261 | 49.7% |

### Category Distribution

| Category | Count | Percentage |
|----------|-------|------------|
| abstention | 102 | 19.4% |
| confidence | 92 | 17.5% |
| dispute | 70 | 13.3% |
| qualification | 261 | 49.7% |

**WARNING**: Mode distribution is imbalanced (max/min ratio = 3.7x).

- `qualified` is heavily over-represented at 49.7% (261 cases).
- `disputed` is the most under-represented at 13.3% (70 cases).
- This is because most boundary files (gen_boundary_abstain, gen_boundary_confident, gen_dq_boundary_1, gen_dq_boundary_2) use `qualified` as the contrasting mode, and gen_threeway is 73% qualified.

**Impact assessment**: This may bias benchmark evaluation toward qualification patterns. However, since these are "hard" boundary cases specifically designed to test decision boundaries, some skew toward qualification is expected -- qualification is the most common boundary partner for all other modes. The imbalance should be documented but is acceptable for a boundary-focused test set.

### After removing 5 flagged cases:

| Mode | Count | Percentage |
|------|-------|------------|
| abstain | 102 | 19.6% |
| confident | 89 | 17.1% |
| disputed | 70 | 13.5% |
| qualified | 259 | 49.8% |

---

## 6. Cases to REMOVE

**5 case(s) must be removed.**

| # | ID | Source File | Reason |
|---|-----|-------------|--------|
| 1 | t1_qualify_hard_332 | gen_dq_boundary_2.json | Exact duplicate query of t1_qualify_hard_215 (both "qualified", same query about EV market share in Norway) |
| 2 | t1_confident_hard_104 | gen_pure_qualify_confident.json | Exact duplicate query of t1_dispute_hard_117 ("Who invented the World Wide Web?") -- cross-mode conflict; dispute version is more nuanced |
| 3 | t1_confident_hard_132 | gen_pure_qualify_confident.json | Exact duplicate query of existing t1_abstain_medium_004 ("What is the population of Tokyo?") -- cross-mode conflict |
| 4 | t1_confident_hard_605 | gen_threeway.json | Exact duplicate query of existing t1_confident_hard_030 ("What is the speed of light?") -- same-mode redundancy |
| 5 | t1_qualify_hard_660 | gen_threeway.json | Exact duplicate query of existing t1_abstain_medium_013 ("What is the current price of Bitcoin?") -- cross-mode conflict |

### Additional cases to REVIEW (not blocking, but recommended)

These near-duplicates are borderline and should be reviewed for distinctiveness:

| ID | Near-Duplicate Of | Jaccard | Concern |
|----|------------------|---------|---------|
| t1_qualify_hard_603 | t1_dispute_hard_105 | 0.88 | "Is intermittent fasting effective for weight loss?" vs "...for long-term weight loss?" - very similar |
| t1_confident_hard_602 | t1_confident_hard_134 | 0.88 | "melting point of pure gold" vs "melting point of gold" - near identical |
| t1_abstain_hard_200 | existing t1_abstain_medium_009 | 0.88 | "treatment protocol for Parkinson's" vs "treatment for Parkinson's" |
| t1_qualify_hard_618 | existing t1_abstain_hard_024 | 0.86 | "CEO of Twitter" vs "current CEO of Twitter" |

---

## 7. Overall Recommendation

**CONDITIONAL PASS** - Remove the 5 identified duplicate cases, then the batch is ready for merge.

**Summary**:
- Schema: CLEAN (0 violations across 525 cases)
- IDs: CLEAN (0 duplicates)
- Queries: 5 exact duplicates must be removed; 13 near-duplicate pairs identified (most are genuinely distinct)
- Context quality: GOOD (all contexts 300+ chars, no templating, substantive content verified in manual review)
- Mode distribution: ACCEPTABLE with caveat (qualified over-represented at 49.7%, but expected for boundary test cases)

**After removing 5 cases**: 520 cases ready for merge into tier1_core.

**Action items**:
1. Remove the 5 cases listed in Section 6
2. Optionally review the 4 borderline near-duplicates
3. Document the qualification skew in the benchmark notes
