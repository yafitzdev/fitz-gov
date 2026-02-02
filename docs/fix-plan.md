# FITZ-GOV Test Case Fix Plan

## Overview

This plan addresses critical issues identified in the FITZ-GOV benchmark test cases.
Fixes are ordered by priority and dependency.

---

## Phase 1: Critical Mode Fixes (Breaks Evaluation If Not Fixed) ✅ COMPLETE

### 1.1 Fix Relevance expected_mode
**Problem**: All 25 relevance cases have `expected_mode: "confident"` but test scenarios where context doesn't answer the question.

**Fix**: Change to `expected_mode: "qualified"` with rationale that system should acknowledge the specific information requested is not available.

**Files**: `data/relevance/relevance.json`

**Validation**: Review each case - if context doesn't contain the answer, mode should be "qualified"

### 1.2 Fix Grounding expected_mode
**Problem**: All 25 grounding cases have `expected_mode: "confident"` but test scenarios where specific details are missing.

**Fix**: Change to `expected_mode: "qualified"` - system should confidently state that specific details are not in context.

**Files**: `data/grounding/grounding.json`

**Validation**: The forbidden_claims mechanism still works - we test that LLM doesn't hallucinate, but the MODE should be qualified.

---

## Phase 2: Schema Standardization ✅ COMPLETE

### 2.1 Add version field to all category files
**Files**: All 6 category JSON files
**Standard**: `"version": "0.9.0"`

### 2.2 Add subcategory to all cases
**Problem**: Some older cases lack subcategory field
**Fix**: Audit and add subcategory to any case missing it

### 2.3 Standardize difficulty distribution
**Target per category**:
- Easy: 33%
- Medium: 34%
- Hard: 33%

### 2.4 Add acceptable_modes field
**New field**: `"acceptable_modes": ["qualified", "abstain"]`
**Purpose**: For ambiguous cases, define acceptable alternatives to primary expected_mode
**Apply to**: ~20% of cases that sit on category boundaries

---

## Phase 3: Forbidden Claims Refinement (Grounding) ✅ COMPLETE

### 3.1 Convert to regex patterns
**Problem**: `"$"` triggers on "no $ amount mentioned"
**Fix**: Use patterns like `"\\$\\d"` (dollar followed by digit) instead of just `"$"`

### 3.2 Add context-aware exclusions
**New field**: `"allowed_phrases": ["not specified", "no .* mentioned", "context does not"]`
**Purpose**: Phrases that can contain forbidden terms but indicate non-hallucination

### 3.3 Expand forbidden_claims coverage
**Add**: Percentage patterns, relative comparisons ("10x faster"), specific counts

---

## Phase 4: Required Elements Refinement (Relevance) ✅ COMPLETE

### 4.1 Change from OR to weighted scoring
**Problem**: Matching ANY required element counts as pass
**Fix**: Add `"min_required": 2` field - must match at least N elements

### 4.2 Add negative_elements
**New field**: `"forbidden_elements": ["here is the pricing", "costs $"]`
**Purpose**: Detect when LLM incorrectly claims to have the answer

---

## Phase 5: Difficulty Recalibration ⏭️ SKIPPED (Distribution acceptable: 30/36/34%)

### 5.1 Audit "easy" cases
**Criteria for easy**: Subtle but clear-cut, not trivially obvious
**Action**: Move obviously trivial cases to a new "trivial" difficulty or remove

### 5.2 Create true difficulty gradient
- **Easy**: Clear pattern, single reasoning step
- **Medium**: Requires careful reading, 2 reasoning steps
- **Hard**: Ambiguous elements, multi-step reasoning, real-world messiness

### 5.3 Add "trivial" baseline cases (optional)
**Purpose**: Sanity check - if LLM fails these, something is very wrong
**Count**: 2-3 per category

---

## Phase 6: Add Missing Test Scenarios ⏸️ DEFERRED (Future v1.0.0)

### 6.1 Boundary cases (10 new cases)
Cases that sit exactly on category boundaries:
- Abstention vs Qualification boundary (4 cases)
- Qualification vs Confidence boundary (3 cases)
- Dispute vs Qualification boundary (3 cases)

### 6.2 Negative cases (12 new cases)
Cases that look like they should trigger a mode but shouldn't:
- Looks like dispute but sources are actually compatible (3)
- Looks like abstention but answer is inferrable (3)
- Looks like hallucination trap but info is actually there (3)
- Looks like qualification needed but evidence is solid (3)

### 6.3 Real-world noise cases (6 new cases)
- OCR artifacts in context
- Truncated sentences
- Formatting issues (bullet points as plain text)
- Mixed formal/informal language

### 6.4 Subtle variations (8 new cases)
- Outdated context (was true, now false)
- Implicit answers (derivable but not stated)
- Partial disputes (both sources partially correct)
- Near-miss entities (iPhone 15 vs iPhone 15 Pro)

---

## Phase 7: Documentation & Validation ✅ COMPLETE

### 7.1 Update roadmap.md
- Document all changes
- Update version to 0.9.0
- Add "known limitations" section

### 7.2 Create decision tree
- Document: Given X characteristics, which mode?
- Include in docs/ as `mode-decision-tree.md`

### 7.3 Validation script
- Count cases per category/subcategory/difficulty
- Verify schema consistency
- Check for duplicate IDs

---

## Implementation Order

| Phase | Priority | Effort | Dependency |
|-------|----------|--------|------------|
| 1.1 Relevance mode fix | Critical | Low | None |
| 1.2 Grounding mode fix | Critical | Low | None |
| 2.1-2.4 Schema standardization | High | Medium | Phase 1 |
| 3.1-3.3 Forbidden claims | High | Medium | Phase 1 |
| 4.1-4.2 Required elements | High | Low | Phase 1 |
| 5.1-5.3 Difficulty recalibration | Medium | Medium | Phase 2 |
| 6.1-6.4 New scenarios | Medium | High | Phase 5 |
| 7.1-7.3 Documentation | Low | Medium | All above |

---

## Version Target

After all fixes: **v0.9.0**

**Changes summary**:
- Fix 50 cases with wrong expected_mode
- Standardize schema across all categories
- Refine evaluation mechanisms (forbidden_claims, required_elements)
- Add ~36 new test cases for edge scenarios
- Recalibrate difficulty levels
- Add decision tree documentation

**Final target**: 236 test cases (200 current + 36 new)

---

## Rollback Plan

If fixes cause issues:
1. Each phase is a separate commit
2. Can revert individual phases
3. Maintain v0.8.0 as "stable" release
4. v0.9.0 tagged as "beta" until validated

---

## Success Criteria

1. All cases have consistent schema
2. No expected_mode contradicts the test's purpose
3. Forbidden_claims has <5% false positive rate
4. Difficulty distribution is meaningful
5. Edge cases are explicitly tested
6. Documentation explains all decisions
