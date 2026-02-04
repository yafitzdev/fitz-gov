# Critical Evaluation of fitz-gov Test Cases

> **Version**: 1.0
> **Status**: Complete
> **Created**: 2026-02-04
> **Evaluated Version**: v0.9.1 (200 cases)

---

## Executive Summary

The fitz-gov benchmark is a well-structured epistemic governance evaluation with 200 test cases across 6 categories. The core concept—testing when RAG systems should abstain, dispute, qualify, or confidently answer—is sound and addresses a genuine gap in LLM evaluation. However, there are notable weaknesses in test case quality, subcategory balance, and coverage gaps that reduce its discriminative power for sophisticated models.

---

## 1. Category-by-Category Analysis

### 1.1 Abstention (40 cases)

**Strengths**:
- Clear subcategory taxonomy (different_domain, wrong_entity, wrong_time_period, etc.)
- Hard cases with "wrong_aspect" are genuinely challenging (e.g., asking for causes when given effects)
- "Decoy keywords" tests (Amazon rainforest vs Amazon.com) are clever

**Weaknesses**:
- Trivially easy "easy" cases: 12/40 cases are "completely different domain" (biology answering finance). Any competent model will catch these.
- Predictable patterns: The easy cases follow a rigid template: `[Query about X]` + `[Context about unrelated Y]`
- Missing nuanced abstention scenarios:
  - Same entity, slightly different version (iPhone 15 asked, iPhone 15 Pro context)
  - Stale data (context accurate but now outdated)
  - Near-miss relevance (context tangentially related but insufficient)

**Example of over-simplicity** (`abstain_easy_001`):
```
Query: "What was Apple's revenue in Q4 2024?"
Contexts: ["The mitochondria is the powerhouse of the cell..."]
```
This is not testing governance—it's testing basic reading comprehension. Any model trivially abstains.

**Recommendation**: Replace 6-8 of the "different_domain" easy cases with more nuanced scenarios where the domain IS correct but specific aspect/entity/timeframe is wrong.

---

### 1.2 Dispute (40 cases)

**Strengths**:
- "Conditional conflict" hard cases are excellent (coffee health, remote work productivity)
- "Methodological conflict" captures real-world scientific disagreement
- Numerical disagreements with different sources (Gartner vs IDC vs company reports) are realistic

**Weaknesses**:
- Easy cases are too binary: 12 cases are "Source A says X, Source B says NOT-X" (success vs failure, approved vs rejected)
- Missing subtle dispute types:
  - Implicit contradiction (sources don't directly conflict but conclusions are incompatible)
  - Scope disagreement (one source generalizes, another provides exceptions)
  - Confidence interval non-overlap (85±5% vs 72±3%)
  - Definition disagreements leading to different conclusions

**Problem pattern** (`dispute_easy_001` through `dispute_easy_012`):
```
"The project launch was a complete success..."
"The project launch failed catastrophically..."
```
This tests whether the model can pattern-match "success" vs "failure"—not genuine dispute detection.

**Recommendation**: Add 8-10 cases with implicit or partial contradictions where the conflict requires inference.

---

### 1.3 Qualification (40 cases)

**Strengths**:
- Correlation vs causation cases are pedagogically excellent (ice cream/crime, breakfast/grades)
- "Small sample" cases properly test statistical reasoning
- Attribution error cases with multiple confounding factors are well-designed

**Weaknesses**:
- Repetitive "why" pattern: 17 cases follow the template "Why did X happen?" + "X happened" (no cause given)
- Missing qualification triggers:
  - Hedged language in source ("probably", "may", "suggests")
  - Source quality concerns (blog post vs peer-reviewed study)
  - Temporal scope mismatch (2019 data for 2024 question)
  - Population mismatch (study on adults applied to children)
  - Self-reported vs objective data quality issues

**Missing category entirely**: "Methodological limitation awareness"—where context explicitly states study limitations that should trigger qualification.

---

### 1.4 Confidence (30 cases)

**Strengths**:
- Good subcategory diversity (10 types)
- Hard cases require recognizing complete information across multiple dimensions
- The comparison_explicit cases (Kubernetes vs Docker Swarm) are realistic decision scenarios

**Weaknesses**:
- Smallest category at 30 cases (vs 40 for others)—underweights the positive case
- Missing confidence reinforcement patterns:
  - Multi-source corroboration (3 sources agree on a fact)
  - Explicit recency ("As of January 2025...")
  - Authoritative attribution ("The official documentation states...")
  - Bounded claims with explicit scope

**Risk**: Benchmarks that underweight "confident" cases train systems toward over-hedging.

---

### 1.5 Grounding (25 cases)

**Strengths**:
- Forbidden claims regex patterns are comprehensive and well-designed
- Allowed phrases list captures legitimate abstention language patterns
- Good variety of hallucination types (numerical, name, date, location, process, attribution)

**Weaknesses**:
- Only 25 cases—should be larger given hallucination prevalence
- Missing hallucination patterns:
  - Entity blending (mixing attributes of company A and company B)
  - Temporal confusion (2020 data presented as 2024)
  - Quote fabrication (making up what someone "said")
  - Statistical inference (hallucinating percentages from vague "increased significantly")
  - Plausible but wrong details (using well-known facts that don't apply here)

**Technical issue**: Some `forbidden_claims` patterns may be too strict:
```python
"SDKs for"  # This would flag "The API provides SDKs for developers" even when not specifying languages
```

---

### 1.6 Relevance (25 cases)

**Strengths**:
- Excellent subcategory design (feature_dump, metric_avoidance, status_dump, etc.)
- "Partial answer" cases testing multi-part question handling
- Wrong_entity_focus (X1 vs X2, EMEA vs APAC) tests careful reading

**Weaknesses**:
- Only 25 cases—insufficient for comprehensive coverage
- Missing relevance failure modes:
  - Format mismatch (asked for list, got prose)
  - Granularity mismatch (asked for specific, got general)
  - Summarizing instead of answering
  - Answering a related but different question
  - Over-answering (providing unrequested additional information)

---

## 2. Corpus Quality Issues

| Domain | Count | Assessment |
|--------|-------|------------|
| business | 42 | Over-represented |
| technology | 40 | Over-represented |
| sports | 1 | Under-represented |
| consumer | 1 | Under-represented |
| industrial | 1 | Under-represented |
| legal | 2 | Under-represented |

**Issues identified**:
1. **Synthetic feel**: Documents are clearly written for test cases, not extracted from real sources
2. **Uniform length/style**: All documents are 2-4 sentences of clean prose
3. **No structured data**: No tables, JSON, or code snippets
4. **No noise**: No OCR errors, formatting issues, or incomplete documents

---

## 3. Critical Gaps in the Benchmark

### 3.1 Missing Test Categories

| Gap | Impact |
|-----|--------|
| Ambiguous queries | No tests for queries that could reasonably be interpreted multiple ways |
| Borderline cases | No cases where the correct mode is itself debatable |
| Multi-turn context | All queries are single-shot; no follow-up question handling |
| Adversarial contexts | No contexts designed to mislead or trick the model |
| Code as context | No programming/technical documentation with code samples |
| Structured data | No tables, charts, or JSON to parse |

### 3.2 Missing Difficulty Gradients

The current difficulty distribution:
- **Easy**: Often trivially easy (different domain abstention, binary contradiction)
- **Medium**: Underutilized—many categories jump from easy to hard
- **Hard**: Generally well-designed but sparse

**Recommendation**: Add 20-30 "medium" cases that bridge the gap—these are where real model differentiation occurs.

### 3.3 Missing Metacognitive Tests

No tests for:
- Model recognizing it needs clarification ("Did you mean X or Y?")
- Model expressing uncertainty about its own classification
- Model identifying when more context would help

---

## 4. Specific Improvements Recommended

### 4.1 Add These Subcategories

**Abstention**:
- `near_miss_entity`: Context about iPhone 15 when asked about iPhone 15 Pro
- `stale_data`: Context explicitly dated 2020 for 2024 question
- `partial_coverage`: Context covers 2 of 3 required aspects

**Dispute**:
- `implicit_contradiction`: Sources don't directly conflict but are incompatible
- `scope_conflict`: General claim vs specific exception
- `confidence_conflict`: Error bars that don't overlap

**Qualification**:
- `hedged_source`: Context contains "may", "possibly", "suggests"
- `source_quality`: Non-authoritative source for factual claim
- `population_mismatch`: Study on group A applied to group B

**Grounding**:
- `entity_blending`: Mixing attributes of similar entities
- `quote_fabrication`: Temptation to invent quotes
- `statistical_inference`: Vague "increased" → specific percentage

### 4.2 Corpus Improvements

1. Add 50+ documents with real-world messiness (longer, varied formatting)
2. Include structured data (tables, lists, JSON)
3. Add code snippets for technical cases
4. Balance domain coverage (add legal, government, sports)

### 4.3 Increase Case Counts

| Category | Current | Recommended |
|----------|---------|-------------|
| Abstention | 40 | 50 |
| Dispute | 40 | 50 |
| Qualification | 40 | 50 |
| Confidence | 30 | 50 |
| Grounding | 25 | 40 |
| Relevance | 25 | 40 |
| **Total** | **200** | **280** |

---

## 5. Overall Assessment

| Aspect | Score | Notes |
|--------|-------|-------|
| Concept/Design | A | Novel, addresses real gap in evaluation |
| Category Taxonomy | B+ | Well-thought-out but missing edge cases |
| Case Quality (Easy) | C | Too trivial, doesn't discriminate |
| Case Quality (Medium) | B | Solid but underutilized |
| Case Quality (Hard) | A- | Generally well-designed |
| Corpus Quality | C+ | Synthetic, lacks realism |
| Coverage Breadth | B- | Missing key scenarios |
| Regex/Validation | A- | Thoughtful, with minor over-strictness |

**Bottom Line**: The benchmark's conceptual framework is strong, but the easy cases are too easy, and significant coverage gaps exist. With the additions recommended above, this could become a definitive epistemic governance benchmark. Currently, it risks ceiling effects where sophisticated models ace the easy cases and only differ on the small number of hard cases.

---

## 6. Quick Wins (Low Effort, High Impact)

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| 1 | Replace 8 trivial abstention cases with wrong-entity-version or stale-data scenarios | Low | High |
| 2 | Add 10 medium cases across categories to smooth difficulty curve | Medium | High |
| 3 | Increase Confidence category to 40 cases to balance positive/negative cases | Medium | High |
| 4 | Add 5 implicit-contradiction dispute cases requiring inference | Low | Medium |
| 5 | Add allowed_phrases edge case handling to reduce false positives in grounding | Low | Medium |

---

## Related Documents

- [Tiered Evaluation Plan](tiered-evaluation-plan.md) - Implementation plan for restructuring into Tier 0/1/2
