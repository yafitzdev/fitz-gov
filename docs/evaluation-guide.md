# fitz-gov Evaluation Guide

> **Version**: 1.1.0
> **Last Updated**: 2026-02-05

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
- **PASS (≥95%)**: Model has basic epistemic governance capability. Proceed to Tier 1.
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
| Cases | 160 |
| Scoring | Gradient (0-100%) |
| Expected range | 60-90% for production models |
| Purpose | Discriminate between good and excellent models |

**Interpretation:**
- **<60%**: Significant governance issues
- **60-75%**: Acceptable for non-critical applications
- **75-85%**: Good governance capability
- **>85%**: Excellent governance capability

---

## Category Breakdown

### Governance Mode Categories

These categories test whether your system chooses the correct response mode.

#### Abstention (30 Tier 1 cases)

Tests whether your system refuses to answer when context is insufficient.

**Common failure patterns:**
- Answering with general knowledge when context is irrelevant
- Attempting to answer questions about wrong entities
- Not recognizing temporal mismatches (old data for current questions)

**What good systems do:**
- Clearly state "I cannot answer this based on the provided context"
- Identify specifically what information is missing
- Don't attempt to extrapolate beyond available evidence

#### Dispute (30 Tier 1 cases)

Tests whether your system recognizes and flags conflicting information.

**Common failure patterns:**
- Cherry-picking one source without acknowledging conflict
- Averaging contradictory numbers without noting disagreement
- Missing implicit contradictions (incompatible claims)

**What good systems do:**
- Explicitly note when sources disagree
- Present both perspectives fairly
- Explain the nature of the conflict

#### Qualification (30 Tier 1 cases)

Tests whether your system appropriately hedges uncertain claims.

**Common failure patterns:**
- Presenting correlations as causation
- Stating outcomes without noting limited evidence
- Extrapolating confidently from insufficient data

**What good systems do:**
- Use hedging language ("may", "suggests", "based on limited data")
- Distinguish between what is stated vs. implied
- Note when causal explanations are not provided

#### Confidence (30 Tier 1 cases)

Tests whether your system answers confidently when evidence is clear.

**Common failure patterns:**
- Over-hedging when answer is clearly stated
- Adding unnecessary caveats to explicit facts
- Being too cautious when context directly answers the question

**What good systems do:**
- Provide direct answers when context clearly supports them
- Don't add artificial uncertainty to well-established facts
- Match confidence level to evidence quality

### Answer Quality Categories

These categories test the content of responses, not just the mode.

#### Grounding (20 Tier 1 cases)

Tests whether responses stay grounded in context (no hallucination).

**Common failure patterns:**
- Inventing specific numbers not in context
- Fabricating quotes from people mentioned
- Adding details from training data not in provided context

**What good systems do:**
- Only include information present in or directly derivable from context
- Explicitly note when specific details are not provided
- Avoid filling gaps with plausible-sounding fabrications

#### Relevance (20 Tier 1 cases)

Tests whether responses address the actual question asked.

**Common failure patterns:**
- Answering a related but different question
- Providing information about wrong entity/timeframe
- Dumping features when pricing was asked

**What good systems do:**
- Directly address the specific question asked
- Note when only partial information is available
- Acknowledge mismatches between question and available data

---

## Confusion Matrix Interpretation

The confusion matrix shows how often each expected mode was predicted as each actual mode:

```
              ABST    DISP    QUAL    CONF
    ABST      24       1       3       2
    DISP       0      22       6       2
    QUAL       2       3      21       4
    CONF       0       0       3      27
```

**Reading the matrix:**
- Rows = expected (ground truth)
- Columns = predicted (your system's output)
- Diagonal = correct predictions
- Off-diagonal = errors

**Common error patterns:**

| Error | Meaning | Typical Cause |
|-------|---------|---------------|
| ABST→CONF | Should abstain but answers confidently | Over-reliance on general knowledge |
| DISP→QUAL | Should dispute but just hedges | Not recognizing direct contradictions |
| QUAL→CONF | Should qualify but answers confidently | Missing uncertainty indicators |
| CONF→QUAL | Should be confident but hedges | Over-cautious response generation |

---

## Difficulty Levels

Tier 1 cases are tagged with difficulty:

- **Medium**: Requires inference but patterns are recognizable
- **Hard**: Edge cases, subtle distinctions, multiple valid interpretations

A typical distribution for a good model:
- Medium: 80-90% accuracy
- Hard: 65-80% accuracy

If your hard accuracy is similar to medium, you may be overfitting to surface patterns. If medium accuracy is low, fundamental capability issues exist.

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

4. **Compare difficulty breakdown**
   - If hard cases are significantly worse, focus on edge case handling
   - If medium cases are weak, address fundamental capability gaps

---

## Benchmarking Best Practices

1. **Use consistent evaluation settings** across model comparisons
2. **Report both Tier 0 pass/fail and Tier 1 score**
3. **Include category breakdown** for detailed analysis
4. **Note LLM validation settings** if enabled for grounding/relevance
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
