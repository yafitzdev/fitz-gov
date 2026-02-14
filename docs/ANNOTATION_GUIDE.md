# Annotation Guide for fitz-gov Human Validation

Version: 1.0

## Overview

This guide describes the annotation task for validating the fitz-gov benchmark. Annotators classify query-context pairs into one of three governance modes: **TRUSTWORTHY**, **DISPUTED**, or **ABSTAIN**. Each annotation determines whether a RAG system, given the provided context, should answer the query, flag conflicting information, or refuse to answer.

The goal is to measure inter-annotator agreement on 250 stratified-sampled cases across six benchmark categories. Your annotations will be compared against gold labels and against a second annotator to establish benchmark reliability.

## The Three Modes

### TRUSTWORTHY

The context provides sufficient evidence to answer the query, either confidently or with appropriate hedging and caveats.

- The context directly addresses the question asked
- The information may be partial or require qualifications, but it is still useful for forming a response
- Sources within the context are consistent with each other (they do not contradict one another on the core claim)
- Includes cases where the system should hedge (e.g., "the data suggests X, but the sample size is limited") as well as cases where a direct answer is warranted

### DISPUTED

The context contains conflicting or contradictory information from different sources, making it impossible to give a single definitive answer without acknowledging the disagreement.

- Two or more sources within the context reach different conclusions about the same question
- The contradiction is substantive (not merely a difference in emphasis or framing)
- The system should present both perspectives rather than choosing one
- The conflict is between the provided sources, not between the sources and external knowledge

### ABSTAIN

The context is irrelevant to the query or completely insufficient to provide any answer. The system should refuse to answer rather than speculate.

- The context discusses a different topic, entity, or time period than what the query asks about
- The context is tangentially related but lacks any information that would help answer the specific question
- Answering would require the system to rely entirely on its own knowledge rather than the provided context

## Decision Tree

Follow these steps in order when classifying a case:

```
Step 1: Is the context relevant to the query?
  |
  +-- NO --> ABSTAIN
  |          The context does not address the question. It may discuss
  |          a related topic, a different entity, or a different time
  |          period. The system cannot answer from this context alone.
  |
  +-- YES (proceed to Step 2)
      |
      Step 2: Do the sources within the context contradict each other?
        |
        +-- YES --> DISPUTED
        |           The sources provide conflicting information on the
        |           core claim. The system should flag the disagreement
        |           and present multiple perspectives.
        |
        +-- NO (proceed to Step 3)
            |
            Step 3: Does the context provide enough information to give
                    any answer (even a partial or hedged one)?
              |
              +-- YES --> TRUSTWORTHY
              |           The system can answer, possibly with caveats
              |           about what is and is not covered.
              |
              +-- NO --> ABSTAIN
                         The context touches the topic but contains
                         no actionable information for answering.
```

## Examples

### TRUSTWORTHY -- Example 1

**Query:** What are the benefits of regular exercise for cardiovascular health?

**Context:**
- "A meta-analysis of 33 clinical trials found that moderate aerobic exercise (150 minutes per week) reduces systolic blood pressure by 5-7 mmHg and diastolic by 3-5 mmHg in hypertensive adults."
- "The American Heart Association recommends at least 150 minutes of moderate-intensity exercise per week, citing reductions in coronary artery disease risk of 20-30%."

**Label:** TRUSTWORTHY

**Reasoning:** Both sources consistently support the benefits of exercise for cardiovascular health with specific, compatible data points. The system can answer directly and confidently.

### TRUSTWORTHY -- Example 2

**Query:** Does green tea help with weight loss?

**Context:**
- "A 2020 review of 15 studies found that green tea catechins combined with caffeine produced a modest reduction in body weight, averaging 1.3 kg over 12 weeks compared to placebo. However, the authors noted high heterogeneity across studies and cautioned that the effect size may not be clinically meaningful."

**Label:** TRUSTWORTHY

**Reasoning:** The context addresses the question directly. Even though the evidence is mixed and requires hedging ("modest," "may not be clinically meaningful"), the system can still provide an answer grounded in what the context says. A hedged answer is still TRUSTWORTHY.

### DISPUTED -- Example 1

**Query:** Is remote work more productive than office work?

**Context:**
- "A Stanford study found remote workers were 13% more productive, with fewer breaks and sick days."
- "Microsoft research showed that while individual task completion increased, cross-team collaboration declined by 25%, reducing overall innovation output."
- "A Harvard study found productivity varied by role: creative work suffered while routine tasks improved by 20%."

**Label:** DISPUTED

**Reasoning:** The sources reach different conclusions. Stanford says productivity increased, while Microsoft and Harvard identify areas where it decreased. The system should acknowledge this disagreement rather than presenting a single answer.

### DISPUTED -- Example 2

**Query:** Are electric vehicles better for the environment than gasoline cars?

**Context:**
- "A lifecycle analysis by the European Environment Agency concluded that EVs produce 50-70% fewer greenhouse gas emissions over their lifetime compared to conventional vehicles, even accounting for battery manufacturing."
- "A study published in the Journal of Industrial Ecology found that when accounting for cobalt mining, battery disposal, and electricity generation from coal-heavy grids, certain EV models have a higher total environmental impact than fuel-efficient gasoline cars for the first 80,000 miles of driving."

**Label:** DISPUTED

**Reasoning:** One source concludes EVs are clearly better; the other concludes that under certain conditions they may be worse. These are substantive contradictions about the core claim, not just different framings of the same conclusion.

### ABSTAIN -- Example 1

**Query:** What specific battle tactics did Hannibal use at the Battle of Zama in 202 BCE?

**Context:**
- "Hannibal Barca is considered one of history's greatest military commanders, known for crossing the Alps with war elephants in 218 BCE."
- "The Battle of Cannae in 216 BCE demonstrated Hannibal's famous double-envelopment tactic, killing an estimated 50,000 Roman soldiers."
- "Hannibal's campaigns in Italy lasted 15 years before he was recalled to defend Carthage."

**Label:** ABSTAIN

**Reasoning:** The query asks specifically about the Battle of Zama, but the context only discusses other events (Alps crossing, Cannae, Italian campaigns). Despite being about the same historical figure, the context contains no information about Zama. The system should not speculate.

### ABSTAIN -- Example 2

**Query:** What is the mechanism of action of aspirin?

**Context:**
- "Aspirin is commonly used to reduce fever, relieve pain, and reduce inflammation."
- "The recommended dosage is typically 325-650 mg every 4-6 hours as needed."
- "Side effects may include stomach upset and gastrointestinal bleeding."

**Label:** ABSTAIN

**Reasoning:** The query asks about how aspirin works at a biochemical level (mechanism of action), but the context only describes its uses, dosage, and side effects. The system would need to rely on its own knowledge to explain COX inhibition, which means it cannot answer from the provided context.

## Edge Cases

The following are common points of confusion. Study them carefully before annotating.

### Hedged or partial answers are still TRUSTWORTHY, not ABSTAIN

If the context contains some relevant information that supports even a qualified answer, the label is TRUSTWORTHY. ABSTAIN is reserved for cases where the context provides no useful information at all.

- "The study found a correlation but could not establish causation" -- this supports a hedged answer (TRUSTWORTHY)
- "Preliminary data suggests X, but more research is needed" -- the system can relay what the data suggests (TRUSTWORTHY)

### Different framing is not contradiction

If two sources discuss the same phenomenon from different angles but do not reach incompatible conclusions, the label is TRUSTWORTHY, not DISPUTED.

- Source A says "the policy reduced unemployment by 2%" and Source B says "the policy had a modest positive effect on employment" -- these are compatible statements (TRUSTWORTHY)
- Source A says "the drug was effective in 60% of patients" and Source B says "40% of patients did not respond to the drug" -- these say the same thing (TRUSTWORTHY)

### Context about the wrong entity or time period is ABSTAIN

Even if the context discusses a closely related topic, if it does not address the specific entity, time period, or scope asked about in the query, the label is ABSTAIN.

- Query asks about "ProTab X1" but context discusses "ProTab X2" -- ABSTAIN
- Query asks about "2024 Q3 earnings" but context covers "2023 Q3 earnings" -- ABSTAIN
- Query asks about "federal regulations" but context discusses "state regulations in California" -- ABSTAIN

### Different methodologies reaching different conclusions is DISPUTED

When sources use different approaches and arrive at meaningfully different answers to the same question, this is a genuine dispute.

- One study uses survey data and finds X; another uses experimental data and finds the opposite -- DISPUTED
- An industry report says a market is growing; an academic study says it is shrinking -- DISPUTED

### Missing specific details when general information exists

If the query asks for a specific detail (e.g., price, date, exact steps) and the context discusses the topic but omits that specific detail, the label depends on whether the context supports any partial answer:

- Context describes features of a plan but not its price, and the query asks for the price -- the system can state what features exist and note the price is not mentioned (TRUSTWORTHY, because it can provide a grounded partial answer)
- Context is entirely about a different product -- ABSTAIN

## Annotation Instructions

### Before you begin

1. Read this guide completely before starting your first annotation
2. Annotate a practice set of 5 cases and compare with the gold labels to calibrate
3. Do not discuss individual cases with the other annotator during the annotation period

### For each case

1. **Read the query first.** Understand what is being asked before looking at the context.
2. **Read all contexts carefully.** Note what information is present and what is absent.
3. **Follow the decision tree.** Apply the three steps in order: relevance, contradiction, sufficiency.
4. **Choose your mode independently.** Do not look at the gold label before making your decision. The gold label field exists for later analysis only.
5. **Rate your confidence (1-5):**
   - 1 = Very uncertain, could easily go either way
   - 2 = Somewhat uncertain, leaning toward this label
   - 3 = Moderately confident
   - 4 = Confident, unlikely to change my mind
   - 5 = Certain, this is unambiguous
6. **Add notes for non-obvious decisions.** If you hesitated between two labels, explain your reasoning. Notes are especially important for confidence ratings of 1-3.

### Filling out the annotation form

For each case in the validation sample JSON, fill in your annotator field:

```json
"annotator_1": {
  "mode": "trustworthy",
  "confidence": 4,
  "notes": "Context clearly addresses the query with consistent sources."
}
```

Valid values for `mode`: `"trustworthy"`, `"disputed"`, `"abstain"`

Valid values for `confidence`: `1`, `2`, `3`, `4`, `5`

The `notes` field is free-text. Use it whenever your confidence is below 4.

### Pacing

- Aim for 2-3 minutes per case on average
- Take breaks every 30-40 cases to avoid fatigue-driven errors
- Total estimated time: 8-12 hours across multiple sessions

## Quality Metrics

The following metrics will be computed from the completed annotations:

### Cohen's Kappa

Cohen's kappa measures agreement between two annotators while accounting for chance agreement. We compute this across all 250 cases for the three-class problem (TRUSTWORTHY vs. DISPUTED vs. ABSTAIN).

| Kappa Range | Interpretation          |
|-------------|-------------------------|
| 0.81 - 1.00 | Almost perfect agreement |
| 0.61 - 0.80 | Substantial agreement    |
| 0.41 - 0.60 | Moderate agreement       |
| 0.21 - 0.40 | Fair agreement           |
| 0.00 - 0.20 | Slight agreement         |

**Target:** kappa >= 0.70 (substantial agreement) to validate benchmark quality.

### Per-Category Agreement Rates

Raw agreement percentage computed separately for each of the six source categories (abstention, dispute, trustworthy_hedged, trustworthy_direct, grounding, relevance). This identifies categories where the gold labels may need revision.

### Confusion Patterns

A 3x3 confusion matrix between annotator labels reveals systematic disagreement patterns:

- **TRUSTWORTHY vs. ABSTAIN confusion** suggests the boundary between "partial evidence" and "insufficient evidence" needs clearer definition in the benchmark
- **TRUSTWORTHY vs. DISPUTED confusion** suggests some cases have ambiguous source agreement
- **DISPUTED vs. ABSTAIN confusion** is rare but may indicate cases where irrelevant contexts appear contradictory

### Gold Label Accuracy

For cases where both annotators agree but disagree with the gold label, the gold label will be reviewed and potentially corrected. This feedback loop improves benchmark quality.
