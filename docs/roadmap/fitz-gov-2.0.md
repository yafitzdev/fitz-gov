# Critical Evaluation of fitz-gov Test Cases (v1.1.0)

> **Version**: 2.0
> **Status**: Complete
> **Created**: 2026-02-04
> **Updated**: 2026-02-05
> **Evaluated Version**: v1.1.0 (220 cases, tiered structure)

---

## Executive Summary

The fitz-gov benchmark has been significantly improved with v1.1.0's tiered evaluation structure. The separation of Tier 0 sanity checks (60 cases, 95% threshold) from Tier 1 core evaluation (160 cases, gradient scoring) addresses the original ceiling effect concerns. Many recommendations from the initial evaluation have been implemented, including new subcategories like `near_miss_entity`, `stale_data`, `implicit_contradiction`, and `multi_source_agreement`.

**Remaining gaps** focus primarily on:
1. Corpus quality (still synthetic, no structured data)
2. Missing qualification subcategories (hedged sources, population mismatch)
3. No code/programming context cases
4. Confidence category still leans conservative (10 tier0 + 30 tier1 vs 50+ for negative modes)

---

## 1. Tiered Structure Assessment

### 1.1 Tier 0 Sanity Check (60 cases)

| Category | Cases | Subcategories | Assessment |
|----------|-------|---------------|------------|
| Abstention | 12 | `different_domain` only | **Excellent** - Pure domain mismatches, trivially correct |
| Dispute | 12 | `direct_contradiction`, `numerical_disagreement` | **Excellent** - Binary contradictions (success/failure, approved/rejected) |
| Qualification | 10 | `causal_without_evidence`, `prediction_insufficient_data` | **Good** - Clear "why X?" with only "X happened" patterns |
| Confidence | 10 | `direct_factual`, `temporal_explicit`, `quantitative_clear`, `definition_provided`, `attribution_clear` | **Excellent** - Explicit answers in context |
| Grounding | 8 | `numerical_hallucination`, `name_hallucination`, `date_hallucination`, `technical_hallucination`, `medical_hallucination`, `location_hallucination` | **Excellent** - Clear hallucination traps with forbidden_claims |
| Relevance | 8 | `feature_dump`, `metric_avoidance`, `status_dump`, `symptom_only`, `instruction_only`, `tangent_drift` | **Good** - Required/forbidden elements well-defined |

**Overall Tier 0 Grade: A**

The 95% threshold is appropriate. Cases are unambiguous and pattern-matchable. Any model failing Tier 0 has fundamental governance deficits.

### 1.2 Tier 1 Core Benchmark (160 cases)

| Category | Cases | Notable Subcategories | Assessment |
|----------|-------|----------------------|------------|
| Abstention | 30 | `wrong_entity`, `wrong_time_period`, `decoy_keywords`, `wrong_aspect`, `near_miss_entity`✓, `stale_data`✓ | **Excellent** - Good progression from obvious to subtle |
| Dispute | 30 | `numerical_disagreement`, `conditional_conflict`, `methodological_conflict`, `implicit_contradiction`✓, `definition_conflict`✓ | **Excellent** - Hard cases require inference |
| Qualification | 30 | `correlation_causation`, `small_sample`, `incomplete_evidence`, `attribution_error` | **Good** - Missing `hedged_source`, `population_mismatch` |
| Confidence | 30 | `multi_source_agreement`✓, `explicit_recency`✓, `bounded_claim`✓, `authoritative_source`✓ | **Excellent** - New subcategories address over-hedging risk |
| Grounding | 20 | `entity_blending`✓, `quote_fabrication`✓, `statistical_inference`✓ | **Excellent** - New subtle hallucination types added |
| Relevance | 20 | `partial_answer`, `wrong_entity_focus`, `format_mismatch`✓, `granularity_mismatch`✓ | **Good** - Covers most failure modes |

✓ = New subcategory added in v1.1.0

**Overall Tier 1 Grade: B+**

The discriminative cases are generally well-designed. Main weakness is qualification category gaps.

---

## 2. Category-by-Category Deep Dive

### 2.1 Abstention (42 cases total)

**Improvements since v0.9.1:**
- Added `near_miss_entity` (iPhone 15 vs iPhone 15 Pro Max)
- Added `stale_data` (2023 stock data for current price question)
- Better difficulty gradient from Tier 0 → Tier 1

**Remaining gaps:**
| Missing Scenario | Priority | Example |
|------------------|----------|---------|
| `version_mismatch` | Medium | Python 3.11 docs for 3.12 question |
| `partial_coverage` | Low | 2 of 3 required dimensions present |

**Grade: A-**

### 2.2 Dispute (42 cases total)

**Improvements since v0.9.1:**
- Added `implicit_contradiction` (mathematically incompatible without direct conflict)
- Added `definition_conflict` (tomato: botanical fruit vs legal vegetable)
- Excellent `conditional_conflict` cases (coffee health, remote work productivity)

**Remaining gaps:**
| Missing Scenario | Priority | Example |
|------------------|----------|---------|
| `confidence_interval_overlap` | Medium | 85±5% vs 72±3% |
| `time_context_conflict` | Low | Same metric, different reporting periods |

**Grade: A**

### 2.3 Qualification (40 cases total)

**Current subcategories:**
- `causal_without_evidence` (17 cases) - "Why did X happen?" with only "X happened"
- `correlation_causation` (9 cases) - Ice cream/crime, breakfast/grades
- `small_sample` (3 cases) - Pilot with 12 participants
- `incomplete_evidence` (4 cases) - Phase 2 trial only
- `attribution_error` (3 cases) - Multiple simultaneous factors
- `prediction_insufficient_data` (4 cases) - Future predictions

**Critical gaps:**

| Missing Scenario | Priority | Example | Impact |
|------------------|----------|---------|--------|
| `hedged_source` | **High** | Context says "may improve", "suggests" | Common in real RAG |
| `source_quality` | **High** | Blog post cited for medical claim | Trust calibration |
| `population_mismatch` | Medium | Study on adults, question about children | Generalization error |
| `temporal_extrapolation` | Medium | 2019-2022 data for 2025 prediction | Common business need |

**Recommendation:** Add 10 cases covering these gaps. The qualification category relies too heavily on `causal_without_evidence` pattern.

**Grade: B**

### 2.4 Confidence (40 cases total)

**Major improvements since v0.9.1:**
- `multi_source_agreement` (3 cases) - Multiple authoritative sources converge
- `explicit_recency` (3 cases) - "As of January 2025..."
- `bounded_claim` (2 cases) - Answer with explicit scope/limitations
- `authoritative_source` (2 cases) - RFC citations, GDPR articles

**Remaining concerns:**
- Still the smallest category at 40 cases (10+30) vs 42 for abstention/dispute
- Over-hedging bias risk: models may learn to hedge by default

**Recommendation:** Add 10 more cases to reach 50, focusing on:
- `code_documentation` - Clear API docs with exact syntax
- `official_statement` - Quoted company announcements
- `regulatory_specification` - Explicit legal requirements

**Grade: B+**

### 2.5 Grounding (28 cases total)

**Major improvements since v0.9.1:**
- `entity_blending` - Mixing attributes of Company A and Company B
- `quote_fabrication` - Inventing CEO quotes
- `statistical_inference` - "Significant improvement" → specific %

**Forbidden_claims patterns are well-designed:**
```python
# Strong regex coverage:
"\\$\\d"                    # Dollar amounts
"\\d+\\s*(million|billion)" # Large numbers
"(CEO|he|she) said[,:]? "   # Quote fabrication
"AES-?\\d*"                 # Technical standards
```

**Minor gap:**
| Missing Scenario | Priority | Example |
|------------------|----------|---------|
| `code_hallucination` | Medium | Fabricating function parameters |
| `table_inference` | Low | Inventing data not in provided table |

**Grade: A-**

### 2.6 Relevance (28 cases total)

**Good coverage:**
- `partial_answer` - Multi-part question, single-part answer
- `wrong_entity_focus` - X1 specs asked, X2 provided
- `temporal_mismatch` - Q1 2024 asked, Q3-Q4 2023 provided
- `format_mismatch` - Asked for list, prose provided
- `granularity_mismatch` - City data asked, state data provided

**Required/forbidden elements well-structured:**
```json
{
  "required_elements": ["not specified", "deadline", "not mentioned"],
  "forbidden_elements": ["\\$\\d", "costs?\\s+\\$?\\d"]
}
```

**Minor gaps:**
| Missing Scenario | Priority | Example |
|------------------|----------|---------|
| `summarization_vs_answer` | Low | Summarizing context instead of answering |
| `over_answering` | Low | Providing unrequested additional details |

**Grade: B+**

---

## 3. Corpus Quality Assessment

### 3.1 Current State (288 documents)

| Domain | Count | % | Assessment |
|--------|-------|---|------------|
| business | 42 | 15% | Over-represented |
| technology | 40 | 14% | Over-represented |
| medical/health | 24 | 8% | Adequate |
| finance | 18 | 6% | Adequate |
| history | 15 | 5% | Adequate |
| science | 12 | 4% | Adequate |
| sports | 1 | 0.3% | **Under-represented** |
| legal | 2 | 0.7% | **Under-represented** |
| consumer | 1 | 0.3% | **Under-represented** |

### 3.2 Quality Issues

| Issue | Status | Impact |
|-------|--------|--------|
| Synthetic prose | **Not fixed** | Documents feel test-generated |
| Uniform length | **Not fixed** | All 2-4 sentences |
| No structured data | **Not fixed** | No tables, JSON, code |
| No noise/artifacts | **Not fixed** | No OCR errors, truncation |

### 3.3 Recommendations

**Phase 1 (High priority):**
- Add 40 documents with tables (financial reports, specs sheets)
- Add 20 documents with JSON/structured data (API responses)
- Add 15 documents with code samples (documentation)

**Phase 2 (Medium priority):**
- Rebalance domains: +10 legal, +10 sports, +8 consumer
- Add longer documents (500+ words): 20 cases
- Add documents with minor imperfections: 10 cases

---

## 4. Test Category Gaps

### 4.1 Missing Categories

| Category | Description | Priority | Recommended Cases |
|----------|-------------|----------|-------------------|
| **Ambiguous queries** | Queries with multiple valid interpretations | High | 10 |
| **Code context** | Programming docs with code samples | High | 10 |
| **Structured data** | Tables, JSON in context | Medium | 10 |
| **Metacognitive** | Model recognizes need for clarification | Low | 5 |

### 4.2 Ambiguous Query Examples

```json
{
  "id": "t1_ambiguous_001",
  "query": "What's the Apple policy?",
  "contexts": [
    "Apple Inc. offers a 14-day return policy for all products...",
    "Apple Records has strict licensing policies for Beatles music..."
  ],
  "expected_mode": "qualified",
  "rationale": "Model should recognize entity ambiguity and ask for clarification"
}
```

### 4.3 Code Context Examples

```json
{
  "id": "t1_code_001",
  "query": "What parameters does the `authenticate()` function accept?",
  "contexts": [
    "def authenticate(username: str, password: str, mfa_token: Optional[str] = None) -> User:\n    '''Authenticate a user and return User object.'''"
  ],
  "expected_mode": "confident",
  "rationale": "Function signature clearly shows parameters"
}
```

---

## 5. Scoring & Threshold Assessment

### 5.1 Tier 0 Threshold (95%)

| Consideration | Assessment |
|---------------|------------|
| Is 95% achievable? | Yes - cases are unambiguous |
| Is 95% meaningful? | Yes - failing indicates fundamental issues |
| Risk of false negatives? | Low - cases have clear correct answers |

**Recommendation:** Keep 95% threshold. Consider adding 1-2 more cases per category to reduce variance.

### 5.2 Tier 1 Expected Range (60-90%)

| Model Capability | Expected Score |
|------------------|----------------|
| Basic RAG (no governance) | 40-55% |
| Standard production model | 60-75% |
| Well-tuned governance system | 75-85% |
| State-of-the-art | 85-92% |

**Recommendation:** Current difficulty distribution is appropriate.

---

## 6. Overall Assessment Summary

### 6.1 Improvements from v0.9.1 → v1.1.0

| Aspect | Before | After | Change |
|--------|--------|-------|--------|
| Structure | Flat 200 cases | Tiered 220 cases | **+10%** |
| Ceiling effects | High | Low | **Fixed** |
| Abstention subcategories | 5 | 7 (+2) | **Improved** |
| Dispute subcategories | 6 | 8 (+2) | **Improved** |
| Confidence subcategories | 6 | 10 (+4) | **Much improved** |
| Grounding subcategories | 6 | 9 (+3) | **Improved** |
| Relevance subcategories | 6 | 8 (+2) | **Improved** |

### 6.2 Remaining Gaps (v2.0 Targets)

| Gap | Priority | Estimated Effort |
|-----|----------|------------------|
| Qualification subcategories | High | 10 new cases |
| Corpus quality | High | 90 new documents |
| Code context cases | High | 10 new cases |
| Ambiguous query cases | Medium | 10 new cases |
| Confidence expansion | Medium | 10 new cases |
| Structured data cases | Medium | 10 new cases |

### 6.3 Grade Summary

| Component | v0.9.1 Grade | v1.1.0 Grade | Change |
|-----------|--------------|--------------|--------|
| Tier 0 Cases | N/A | A | New |
| Tier 1 Cases | B | B+ | +0.5 |
| Abstention | B+ | A- | +0.5 |
| Dispute | B | A | +1.0 |
| Qualification | B- | B | +0.5 |
| Confidence | C+ | B+ | +1.0 |
| Grounding | B+ | A- | +0.5 |
| Relevance | B | B+ | +0.5 |
| Corpus | C+ | C+ | No change |
| **Overall** | **B-** | **B+** | **+1.0** |

---

## 7. Quick Wins for v2.0

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| 1 | Add 10 qualification cases (hedged_source, population_mismatch) | Medium | High |
| 2 | Add 30 corpus documents with structured data (tables, JSON) | Medium | High |
| 3 | Add 10 code context cases | Medium | High |
| 4 | Expand confidence to 50 cases | Medium | Medium |
| 5 | Add 10 ambiguous query cases | Low | Medium |

---

## Related Documents

- [Tiered Evaluation Plan](tiered-evaluation-plan.md) - Implementation plan for v1.1.0 and v2.0
