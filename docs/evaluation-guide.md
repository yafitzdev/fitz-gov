# fitz-gov Evaluation Guide

> **Version**: 3.0.0
> **Last Updated**: 2026-02-11

This guide explains how to interpret fitz-gov benchmark results and understand what the scores mean for your RAG system.

---

## Tiered Evaluation Structure

fitz-gov uses a two-tier evaluation system:

### Tier 0: Sanity Check

| Property | Value |
|----------|-------|
| Cases | 60 |
| Threshold | 95% |
| Purpose | Baseline functionality verification |
| Failure meaning | Model lacks fundamental governance awareness |

**Interpretation:**
- **PASS (>=95%)**: Model has basic epistemic governance capability. Proceed to Tier 1.
- **FAIL (<95%)**: Model has fundamental issues. Fix these before meaningful Tier 1 evaluation.

Tier 0 cases are intentionally easy:
- Complete domain mismatches (biology context for finance question)
- Binary contradictions (approved vs rejected)
- Obvious missing information

If a model fails Tier 0, it indicates serious problems with:
- Context relevance detection
- Contradiction recognition
- Basic information extraction

### Tier 1: Core Benchmark

| Property | Value |
|----------|-------|
| Cases | 1113 |
| Governance cases | 1047 (abstain/dispute/qualification/confidence) |
| Answer quality cases | 66 (grounding/relevance) |
| Scoring | Gradient (0-100%) |
| Unique subcategories | 54 |
| Expected range | 60-75% for production models |
| Purpose | Discriminate between good and excellent governance |

**Interpretation:**
- **<55%**: Significant governance issues
- **55-65%**: Acceptable for non-critical applications
- **65-75%**: Good governance capability
- **>75%**: Excellent governance capability

**Note**: fitz-gov v3.0 is significantly harder than v2.0 due to the addition of boundary cases, three-way ambiguity cases, and targeted edge cases. A score of 69% on v3.0 represents strong governance capability.

---

## Category Breakdown

### Governance Mode Categories

These categories test whether your system chooses the correct response mode.

#### Abstention (237 Tier 1 cases)

Tests whether your system refuses to answer when context is insufficient.

**Subcategory clusters**: wrong entity, wrong domain, wrong version, wrong jurisdiction, wrong time period, decoy keywords, domain bleed, partial schema match, code abstention, and more.

**Common failure patterns:**
- Answering with general knowledge when context is irrelevant
- Attempting to answer questions about wrong entities
- Not recognizing temporal mismatches (old data for current questions)
- Being confused by decoy keywords (shares vocabulary but different topic)
- Missing version mismatches (v2.1 context for v2.0 question)

**What good systems do:**
- Clearly state "I cannot answer this based on the provided context"
- Identify specifically what information is missing
- Don't attempt to extrapolate beyond available evidence
- Resist high embedding similarity when entities don't match

#### Dispute (196 Tier 1 cases)

Tests whether your system recognizes and flags conflicting information.

**Subcategory clusters**: same metric different values, opposing conclusions, contradictory dates/attribution/status, implicit contradiction, binary fact conflict, statistical direction conflict, competing theories, conditional conflict, and more.

**Common failure patterns:**
- Cherry-picking one source without acknowledging conflict
- Averaging contradictory numbers without noting disagreement
- Missing implicit contradictions (incompatible claims)
- Confusing methodology differences with factual disputes
- Missing binary fact conflicts (approved vs rejected)

**What good systems do:**
- Explicitly note when sources disagree
- Present both perspectives fairly
- Explain the nature of the conflict
- Distinguish genuine disputes from methodology differences

#### Qualification (360 Tier 1 cases)

Tests whether your system appropriately hedges uncertain claims. Cases in this category expect TRUSTWORTHY mode with appropriate hedging language. This is the largest and most nuanced category.

**Subcategory clusters**: same topic different aspects, mixed evidence, conditional applicability, hedged claims, temporal/entity/scope ambiguity, deprecated documentation, partial correlation, small sample, source quality variance, methodology difference, hedged vs assertive, numerical near-miss, evolving facts, pros vs cons, risk vs benefit, correlation vs causation, and more.

**Common failure patterns:**
- Presenting correlations as causation
- Stating outcomes without noting limited evidence
- Extrapolating confidently from insufficient data
- Treating methodology differences as factual contradictions
- Ignoring hedging language in source material ("may", "suggests")

**What good systems do:**
- Use hedging language ("may", "suggests", "based on limited data")
- Distinguish between what is stated vs. implied
- Note when causal explanations are not provided
- Recognize that different values can reflect different methodologies, not disputes
- Acknowledge temporal, scope, or entity ambiguity

#### Confidence (254 Tier 1 cases)

Tests whether your system answers confidently when evidence is clear. Cases in this category expect TRUSTWORTHY mode with direct, confident language.

**Subcategory clusters**: direct factual, multi-source convergence, clear procedural, unambiguous extraction, well-documented technical, clear causal explanation, different framing same fact, opposing with consensus, numerical diff methodology explained, contradiction with clear winner, and more.

**Common failure patterns:**
- Over-hedging when answer is clearly stated
- Adding unnecessary caveats to explicit facts
- Being too cautious when context directly answers the question
- Treating apparent contradictions as disputes when they're resolved by context
- Failing to recognize when multiple sources converge on the same answer

**What good systems do:**
- Provide direct answers when context clearly supports them
- Don't add artificial uncertainty to well-established facts
- Recognize when apparent contradictions are resolved (different framing, methodology explained)
- Trust strong consensus across multiple sources

### Answer Quality Categories

These categories test the content of responses, not just the mode.

#### Grounding (34 Tier 1 cases)

Tests whether responses stay grounded in context (no hallucination).

**Subcategory clusters**: numerical hallucination, name hallucination, code hallucination, table inference, quote extension, temporal confusion, and more.

**Common failure patterns:**
- Inventing specific numbers not in context
- Fabricating quotes from people mentioned
- Adding details from training data not in provided context
- Hallucinating function parameters or return types (code context)
- Inventing data not in provided tables

**What good systems do:**
- Only include information present in or directly derivable from context
- Explicitly note when specific details are not provided
- Avoid filling gaps with plausible-sounding fabrications

#### Relevance (32 Tier 1 cases)

Tests whether responses address the actual question asked.

**Subcategory clusters**: summarization vs answer, related but different, over-answering, prerequisite missing, format mismatch, granularity mismatch, and more.

**Common failure patterns:**
- Answering a related but different question
- Providing information about wrong entity/timeframe
- Summarizing context instead of answering the question
- Dumping features when pricing was asked
- Providing unrequested details instead of the specific answer

**What good systems do:**
- Directly address the specific question asked
- Note when only partial information is available
- Acknowledge mismatches between question and available data

---

## Confusion Matrix Interpretation

The confusion matrix shows how often each expected mode was predicted as each actual mode:

```
              ABST    DISP    TRST
    ABST      200       0      37
    DISP        6      131      59
    TRST       36      24     554
```

**Reading the matrix:**
- Rows = expected (ground truth)
- Columns = predicted (your system's output)
- Diagonal = correct predictions
- Off-diagonal = errors

**Common error patterns:**

| Error | Meaning | Typical Cause |
|-------|---------|---------------|
| ABST->TRST | Should abstain but answers | High embedding similarity masks irrelevant content |
| DISP->TRST | Should dispute but answers without noting conflict | Not recognizing direct contradictions |
| TRST->ABST | Should answer but refuses | Overly strict relevance thresholds |
| TRST->DISP | Should answer but flags spurious conflict | Not recognizing resolved contradictions |
| DISP->ABST | Should dispute but refuses entirely | Missing that conflict exists on-topic |
| ABST->DISP | Should abstain but flags off-topic conflict | Not checking topic relevance before disputing |

---

## Difficulty Levels

Tier 1 cases are tagged with difficulty:

- **Easy**: Only in Tier 0 (sanity checks)
- **Medium**: Requires inference but patterns are recognizable
- **Hard**: Edge cases, subtle distinctions, boundary cases, three-way ambiguity

v3.0 is 92% hard cases by design. A typical distribution for a good model:
- Medium: 80-90% accuracy
- Hard: 60-75% accuracy

If your hard accuracy is similar to medium, you may be overfitting to surface patterns. If medium accuracy is low, fundamental capability issues exist.

---

## Boundary Cases

The hardest cases in fitz-gov sit at mode boundaries. Understanding these helps diagnose failures:

| Boundary | Cases | Key Challenge |
|----------|-------|---------------|
| Dispute <-> Trustworthy | ~175 | Methodology difference vs genuine contradiction |
| Abstain <-> Trustworthy | ~25 | Topic-adjacent but no direct answer |
| Abstain <-> Dispute | ~20 | Real contradiction about wrong subject |
| Three-way ambiguity | ~90 | Multiple competing signals |

The **Dispute <-> Trustworthy boundary** is the primary bottleneck. The key rule: if the numerical gap is FULLY EXPLAINED by a stated methodology/scope difference, it should be trustworthy (with appropriate hedging or confidence based on the evidence), not disputed.

Note: Within the TRUSTWORTHY mode, the benchmark categories (qualification vs confidence) test different behaviors - whether the answer should include hedging language or be stated confidently - but both expect the same TRUSTWORTHY mode.

---

## Recommended Evaluation Workflow

1. **Run Tier 0 first**
   ```python
   result = evaluator.evaluate_tiered(..., gating_enabled=True)
   if not result.tier0_passed:
       print("Fix Tier 0 failures before proceeding")
       return
   ```

2. **Analyze Tier 1 by category**
   - Identify weakest categories
   - Check confusion matrix for systematic errors

3. **Review failure cases**
   ```python
   for case_result in result.tier1.category_results[FitzGovCategory.ABSTENTION].case_results:
       if not case_result.passed:
           print(f"Failed: {case_result.case.id}")
           print(f"Expected: {case_result.case.expected_mode}")
           print(f"Got: {case_result.actual_mode}")
   ```

4. **Check subcategory breakdown**
   ```python
   cat_result = result.tier1.category_results[FitzGovCategory.DISPUTE]
   for subcat, acc in sorted(cat_result.subcategory_accuracy.items()):
       print(f"  {subcat}: {acc:.1%}")
   ```

5. **Compare difficulty breakdown**
   - If hard cases are significantly worse, focus on edge case handling
   - If medium cases are weak, address fundamental capability gaps

---

## Benchmarking Best Practices

1. **Use consistent evaluation settings** across model comparisons
2. **Report both Tier 0 pass/fail and Tier 1 score**
3. **Include category breakdown** for detailed analysis
4. **Note LLM validation settings** if enabled for grounding
5. **Version your benchmark** (fitz-gov version affects results)

---

## FAQ

**Q: My model fails Tier 0 on one category. Should I still look at Tier 1?**

A: You can run with `gating_enabled=False`, but Tier 1 scores will be less meaningful. Fix the fundamental issue first.

**Q: Is 100% on Tier 0 required?**

A: No, 95% is the threshold. Some Tier 0 cases may have debatable answers in edge situations, but >95% should be achievable.

**Q: My grounding scores are low but I'm not hallucinating.**

A: Check for false positives in regex patterns. Enable LLM validation with `llm_validation=True` for more accurate grounding evaluation.

**Q: How do I improve my score on a specific category?**

A: Analyze the subcategory breakdown and failure cases. Each subcategory tests a specific pattern - focus on the patterns where your system fails most often.

**Q: What does 69% on v3.0 mean compared to 72% on v2.0?**

A: v3.0 is significantly harder. It has 4.5x more Tier 1 cases, with 92% at hard difficulty targeting real-world failure modes. A v3.0 score of 69% represents stronger governance than a v2.0 score of 72%.

**Q: What's the difference between the qualification and confidence categories if both expect TRUSTWORTHY mode?**

A: Both categories expect TRUSTWORTHY mode, but they test different answer behaviors. Qualification cases test whether your system appropriately hedges uncertain claims (using "may", "suggests", noting limitations), while confidence cases test whether your system answers directly when evidence is clear. The categories diagnose different failure modes: over-confidence vs over-caution. Both are critical for epistemic honesty, just at opposite ends of the certainty spectrum.
