# fitz-gov Mode Decision Tree

This document explains how to determine the correct `expected_mode` for a test case based on the relationship between the query and context.

## Quick Reference

| Context State | Expected Mode |
|--------------|---------------|
| Context is completely irrelevant to query | **ABSTAIN** |
| Context discusses topic but conflicts exist | **DISPUTED** |
| Context discusses topic and provides answer (with hedging) | **TRUSTWORTHY** (trustworthy_hedged category) |
| Context clearly and unambiguously answers the query | **TRUSTWORTHY** (trustworthy_direct category) |

---

## Decision Flow

```
START: Does the context contain information about the topic in the query?
|
+- NO -> The context is about something completely different
|       +- Expected Mode: ABSTAIN
|       +- Category: abstention
|
+- YES -> Context is on-topic. Does the context contain conflicting information?
         |
         +- YES -> Are the differences explained by methodology/scope/time?
         |         |
         |         +- YES -> Different measurement, not a factual dispute
         |         |         +- Expected Mode: TRUSTWORTHY
         |         |         +- Category: trustworthy_hedged
         |         |
         |         +- NO -> Genuine factual contradiction between sources
         |                  +- Expected Mode: DISPUTED
         |                  +- Category: dispute
         |
         +- NO -> Context is consistent. Does it fully answer the specific question?
                  |
                  +- YES -> Direct, unambiguous answer available
                  |        +- Expected Mode: TRUSTWORTHY
                  |        +- Category: trustworthy_direct
                  |
                  +- NO -> Context discusses topic but misses something specific
                          |
                          +- Missing specific numbers -> TRUSTWORTHY (trustworthy_hedged)
                          +- Missing specific names -> TRUSTWORTHY (trustworthy_hedged)
                          +- Missing specific dates -> TRUSTWORTHY (trustworthy_hedged)
                          +- Hedged/uncertain claims -> TRUSTWORTHY (trustworthy_hedged)
                          +- Answers adjacent question -> TRUSTWORTHY (trustworthy_hedged)
                          +- Answers wrong entity -> TRUSTWORTHY (trustworthy_hedged)
                          +- Answers wrong time period -> TRUSTWORTHY (trustworthy_hedged)
                          +- Source quality concerns -> TRUSTWORTHY (trustworthy_hedged)
                          +- Methodology limits -> TRUSTWORTHY (trustworthy_hedged)
                          |
                          +- Expected Mode: TRUSTWORTHY
                          +- Category: trustworthy_hedged
```

---

## Detailed Category Guidance

### ABSTAIN (abstention category)

**Use when**: Context provides NO useful information for answering the query.

**Key indicators**:
- Context is about a completely different topic
- Context is about wrong entity (asks about X, context about Y)
- Context is about wrong time period (asks about 2024, context about 2020)
- Context is about wrong version (asks about v2.0, context about v3.0)
- Context is about wrong jurisdiction (asks about US law, context about EU law)
- Context would require pure speculation to answer
- Context shares vocabulary but is about a different domain (decoy keywords)

**Example**:
- Query: "What is Apple's revenue?"
- Context: "Microsoft announced Windows 12 today..."
- Mode: ABSTAIN (wrong company entirely)

**NOT abstention if**: Context discusses the topic even tangentially — that's trustworthy_hedged.

**Boundary with Dispute**: If context has contradictory sources but about the WRONG topic, it's still ABSTAIN. The contradiction is noise if the content doesn't answer the query.

---

### DISPUTED (dispute category)

**Use when**: Context contains conflicting or contradictory information from different sources about the SAME topic.

**Key indicators**:
- Source A says X, Source B says Y (different values/facts for same measurement)
- Same source contradicts itself
- Context explicitly notes disagreement among experts
- Both positions have merit, neither can be dismissed
- Binary fact conflict (approved vs rejected, passed vs failed)
- Implicit contradiction (claims that are logically incompatible)

**Example**:
- Query: "When was the company founded?"
- Context: "According to the SEC filing, founded in 2015. The company website states founded in 2014."
- Mode: DISPUTED (sources disagree on founding year)

**NOT disputed if**:
- Sources provide compatible/complementary information
- One source is clearly more authoritative (→ trustworthy_direct with clear winner)
- Apparent conflict is due to different methodology/scope/time (→ trustworthy_hedged)
- Numbers differ because they measure different things (as-reported vs pro forma)
- Conflict exists but content is off-topic (→ ABSTAIN)

**Critical rule**: If the numerical gap is FULLY EXPLAINED by a stated methodology/scope difference, it should be trustworthy_hedged, not DISPUTED.

---

### TRUSTWORTHY - Trustworthy Hedged Category

**Use when**: Context provides partial, uncertain, or incomplete evidence for the query. The answer should be TRUSTWORTHY mode but with appropriate hedging language.

**Key indicators**:
- Context shows correlation but query asks about causation
- Context has small sample size or preliminary results
- Context provides indirect evidence requiring inference
- Context discusses topic but misses the specific detail asked
- Context answers adjacent question but not exact question
- Context provides data from wrong scope/time/entity
- Sources use hedging language ("may", "suggests", "preliminary")
- Sources have different quality levels (blog vs peer-reviewed)
- Multiple valid interpretations exist (entity/scope/metric ambiguity)
- Context is deprecated or outdated but still partially relevant
- Values differ due to methodology, not factual disagreement

**Example**:
- Query: "What causes the performance issue?"
- Context: "Performance drops when load exceeds 1000 requests/second."
- Mode: TRUSTWORTHY (with hedging — correlation shown, not causation)
- Category: trustworthy_hedged

---

### TRUSTWORTHY - Trustworthy Direct Category

**Use when**: Context clearly and unambiguously answers the query. The answer should be TRUSTWORTHY mode with direct, confident language.

**Key indicators**:
- Direct answer present with no hedging needed
- Multiple sources agree on the same answer
- Answer is explicit, not requiring inference
- No missing information that would affect the answer
- No conflicting information
- Apparent contradiction is resolved by context (different framing, methodology explained)
- Strong consensus despite minor dissent (9 studies agree, 1 disagrees)
- Data is in a table/JSON and directly extractable

**Example**:
- Query: "What is the API rate limit?"
- Context: "The API allows 1000 requests per minute for standard accounts."
- Mode: TRUSTWORTHY (confident — exact answer clearly stated)
- Category: trustworthy_direct

**NOT trustworthy_direct if**:
- Answer requires ANY inference or assumption (→ trustworthy_hedged)
- Any detail in the query is not addressed (→ trustworthy_hedged)
- Context uses hedging language ("approximately", "around", "estimated") (→ trustworthy_hedged)
- Context is about a different version/entity/time (even if plausible) (→ trustworthy_hedged or abstention)

---

## Cross-Cutting Quality Checks

In v5.0, grounding and relevance are no longer standalone categories. They are quality dimensions applied to every trustworthy case (hedged and direct).

### How Quality Checks Work

Every trustworthy case is evaluated on three dimensions:

1. **Governance mode**: Did the system correctly classify this as TRUSTWORTHY?
2. **Grounding** (`forbidden_claims`): Did the response avoid hallucinating details not in context?
3. **Relevance** (`required_elements`): Did the response actually address the question asked?

A case only passes if all three checks succeed. Quality checks are skipped when the mode is wrong — there's no point checking answer quality when the meta-decision is wrong.

### Grounding vs Trustworthy Hedged

Both involve TRUSTWORTHY mode, but test different behaviors:

| Dimension | Tests For | LLM Should... |
|-----------|-----------|---------------|
| **Grounding** | Hallucination resistance | NOT invent missing details |
| **Trustworthy hedged** | Epistemic honesty | Acknowledge uncertainty in evidence |

**Grounding example**: "What is the CEO's name?" (context doesn't mention CEO name)
- Expected mode: TRUSTWORTHY
- LLM should NOT make up a name
- Should say "The CEO's name is not mentioned in the context"

**Trustworthy hedged example**: "Does coffee cause heart disease?" (context shows correlation only)
- Expected mode: TRUSTWORTHY
- LLM should NOT claim causation
- Should say "The context shows correlation but doesn't establish causation"

### Relevance

Relevance checks test whether the system's response actually addresses the question asked, rather than drifting to related topics or summarizing the context.

---

## Boundary Decision Rules

### Dispute vs Trustworthy (Primary Bottleneck)

This is the hardest boundary. Use these rules:

| Scenario | Mode | Category | Reasoning |
|----------|------|----------|-----------|
| "$5.0M revenue" vs "$5.2M revenue" (same metric) | DISPUTED | dispute | Same measurement, different values |
| "$5.0M as-reported" vs "$5.2M pro forma" | TRUSTWORTHY | trustworthy_hedged | Different methodology explains the gap |
| "Study A: effective" vs "Study B: ineffective" | DISPUTED | dispute | Same question, opposite conclusions |
| "Study A: effective in adults" vs "Study B: ineffective in children" | TRUSTWORTHY | trustworthy_hedged | Different populations |
| "2020: 10%" vs "2023: 15%" | TRUSTWORTHY | trustworthy_hedged | Different time periods, both true |
| "Source says 10%" vs "Source says 25%" (same year, same metric) | DISPUTED | dispute | Genuine factual disagreement |

**The rule**: If the gap is FULLY EXPLAINED by a stated methodology/scope/time difference, it's TRUSTWORTHY (trustworthy_hedged). If not, it's DISPUTED.

### Abstain vs Trustworthy

| Scenario | Mode | Category | Reasoning |
|----------|------|----------|-----------|
| Query about Apple, context about Microsoft | ABSTAIN | abstention | Completely wrong entity |
| Query about Python, context about JavaScript | ABSTAIN | abstention | Wrong technology entirely |
| Query about pricing, context about features of same product | TRUSTWORTHY | trustworthy_hedged | Same product, different aspect |
| Query about v2.0, context about v3.0 of same software | ABSTAIN | abstention | Different version |
| Query about v2.0, context about v2.1 with migration guide | TRUSTWORTHY | trustworthy_hedged | Adjacent version with overlap |

### Trustworthy Direct vs Trustworthy Hedged (Both TRUSTWORTHY Mode)

| Scenario | Category | Reasoning |
|----------|----------|-----------|
| "Founded in 2015" (query asks founding year) | trustworthy_direct | Direct answer, no hedging needed |
| "Founded around 2015" | trustworthy_hedged | Hedging language in source |
| 3 sources agree on same answer | trustworthy_direct | Strong consensus |
| 1 source gives answer, no corroboration | trustworthy_direct | Single authoritative source suffices if clear |
| Answer true but outdated (2019 data for "current" question) | trustworthy_hedged | Temporal staleness requires hedging |

Note: Both categories expect TRUSTWORTHY mode. The category distinguishes whether the answer should be stated confidently or with appropriate hedging.

---

## Common Mistakes

### Mistake 1: Trustworthy_direct when specific detail missing

**Wrong**: Context lists product features -> Query asks for price -> Category: trustworthy_direct
**Right**: Should be trustworthy_hedged (price not in context, requires hedging)

### Mistake 2: Abstain when context is on-topic

**Wrong**: Context discusses company but not the specific metric -> Mode: ABSTAIN
**Right**: Mode should be TRUSTWORTHY with trustworthy_hedged category (topic is relevant, just missing specific info)

### Mistake 3: Disputed when sources are compatible

**Wrong**: Source A says "revenue grew", Source B gives "$4B revenue" -> Mode: DISPUTED
**Right**: These are compatible, not conflicting. Mode should be TRUSTWORTHY.

### Mistake 4: Trustworthy_hedged when answer is clear

**Wrong**: Context states "Founded in 2015" -> Query asks founding year -> Category: trustworthy_hedged
**Right**: Category should be trustworthy_direct (direct answer available, no hedging needed)

### Mistake 5: Disputed when methodology explains the gap

**Wrong**: "Revenue: $5.0M (as-reported)" vs "$5.2M (pro forma)" -> Mode: DISPUTED
**Right**: Mode should be TRUSTWORTHY with trustworthy_hedged category (methodology difference fully explains the gap)

---

## Mode Selection Checklist

Before assigning expected_mode, verify:

- [ ] Is the context about the topic in the query? (No -> ABSTAIN)
- [ ] Do sources conflict with each other on the SAME measurement? (Yes -> DISPUTED)
- [ ] Are numerical differences explained by methodology/scope? (Yes -> TRUSTWORTHY, not DISPUTED)
- [ ] Does context directly answer the specific question with no hedging needed? (Yes -> TRUSTWORTHY, trustworthy_direct category)
- [ ] Does context discuss topic but miss specific detail or require hedging? (Yes -> TRUSTWORTHY, trustworthy_hedged category)

---

## Version History

- v6.0.0: Schema overlay in two phases. Phase 0b adds LLM-enriched governance signals (query_rewritten, context summaries, hallucination_pressure, retrieval_retry_value, query_evidence_alignment, answer_coverage, boundary_proximity.distance, near_miss_reason). Phase 0c adds MoE multi-task training ground truth (per-chunk boundary_quality, evidence_bias_score, evidence_chain for multi-chunk cases, grounding_targets for TRUSTWORTHY cases). No category, mode, or labeling changes — decision tree unchanged.
- v5.0.0: Updated for 2,920-case tier1 benchmark with 4 categories (trustworthy_hedged/trustworthy_direct replacing qualification/confidence), grounding and relevance as cross-cutting quality checks, 113 subcategories
- v3.0.0: Updated for 1,173-case benchmark, added boundary decision rules, three-way ambiguity, dispute vs qualification guidelines
- v0.9.0: Initial decision tree document created
