# Phase 1: Rewrite Grounding/Relevance Content

**Priority:** P0 (blocks release)
**Scope:** 336 cases (166 grounding + 170 relevance)
**Files modified:** `data/tier1_core/grounding.json`, `data/tier1_core/relevance.json`

## Problem

The 336 new grounding/relevance cases generated in v4.1 use template-based generation
that produces shallow, formulaic content:

### Grounding (166 new cases)
- **Median context length: 17 words** (target: 80-200 words)
- Query templates heavily reused:
  - "What is the total cost of the..." used 20x
  - "Is there an official statement from..." used 14x
  - "How do you configure the advanced..." used 10x
- `forbidden_claims` patterns: only 413 unique out of 966 total (57% reuse)
  - `\$\d` used 21x (same pattern on every numerical_hallucination case)
  - 5 patterns each used 20x (one per numerical_hallucination template)
- 5 duplicate descriptions out of 200

### Relevance (170 new cases)
- **Median context length: 23 words** (target: 60-150 words)
- Query templates heavily reused:
  - "What are the specific metrics AND..." used 16x
  - "What are the current 2025 figures..." used 14x
  - "What are the day-by-day details of..." used 12x
  - "What is the overall assessment of..." used 12x
- `required_elements`: only 204 unique out of 1,196 total
  - "not mentioned" used 51x, "not specified" used 38x

### Why This Matters
A benchmark tests discrimination between models. One-sentence contexts with
the same query template and same forbidden_claims pattern cannot distinguish
between a weak model and a strong one — both will trivially avoid hallucinating
when the context says almost nothing.

## Solution

Rewrite all 336 cases with:
1. **Rich contexts** (80-200 words each) — detailed, domain-specific passages
2. **Unique queries** — no two queries should start with the same 6-word prefix
3. **Targeted forbidden_claims/required_elements** — specific to each case's content
4. **Hallucination traps** — contexts that are detailed enough to *tempt* hallucination

## Implementation

### Step 1: Write grounding content rewriter script
`scripts/rewrite_grounding_content.py`

For each of the 166 new grounding cases (IDs t1_grounding_hard_025 through t1_grounding_hard_190):

**Context rewrite rules by subcategory:**

| Subcategory | Context Strategy | Target Words |
|-------------|-----------------|--------------|
| numerical_hallucination (20) | Rich context with many numbers EXCEPT the one asked about | 100-150 |
| attribution_hallucination (18) | Two detailed source passages, each 80-120 words | 80-120 each |
| temporal_confusion (18) | Multiple dated events with overlapping timelines | 100-150 |
| entity_blending (18) | Two entity descriptions, similar domains, distinct facts | 80-120 each |
| process_hallucination (14) | Detailed outcome description without step-by-step process | 100-150 |
| quote_fabrication (14) | Context about a person's work, no direct quotes | 100-150 |
| statistical_inference (14) | Historical stats without projections or trends | 100-150 |
| code_hallucination (10) | Feature overview without config syntax | 80-120 |
| table_inference (10) | Data points without causal explanations | 100-150 |
| causal_hallucination (12) | Correlation data, explicit "no causation established" | 100-200 |
| comparative_hallucination (10) | One entity detailed, other vague | 80-120 each |
| geographic_hallucination (8) | Activity described without specific locations | 80-120 |

**Forbidden claims rewrite rules:**
- Each case must have 3-6 patterns
- At most 2 patterns can be shared with any other case
- Patterns must be specific to the content (not generic like `\$\d`)
- Include at least 1 pattern that a mid-tier LLM would likely trigger

**Query rewrite rules:**
- No two queries should share the same 6-word prefix
- Query should reference specific details from the context
- Query must ask for information that is *plausibly* but *not actually* in the context

### Step 2: Write relevance content rewriter script
`scripts/rewrite_relevance_content.py`

For each of the 170 new relevance cases (IDs t1_relevance_hard_024 through t1_relevance_hard_193):

**Context rewrite rules by subcategory:**

| Subcategory | Context Strategy | Target Words |
|-------------|-----------------|--------------|
| partial_answer (16) | Detailed answer to PART of a multi-part question | 80-150 |
| wrong_entity_focus (14) | Detailed info about Entity A when question asks about Entity B | 80-150 |
| temporal_mismatch (14) | Detailed but dated information (explicitly timestamped) | 80-120 |
| tangent_drift (14) | Starts on-topic (1-2 sentences) then drifts to related tangent | 100-200 |
| over_answering (12) | Rich context with many metrics when only one is asked about | 100-150 |
| summarization_vs_answer (12) | Comprehensive report when question asks for yes/no judgment | 100-200 |
| related_but_different (12) | Operational data when strategy is asked, or vice versa | 80-150 |
| prerequisite_missing (12) | Planning/prep details without actual outcomes | 80-150 |
| granularity_mismatch (12) | Annual/aggregate data when daily/component detail asked | 80-150 |
| scope_mismatch (12) | Regional data when global scope asked | 80-120 |
| format_mismatch (10) | Prose when structured output (steps/list/table) requested | 80-150 |
| cherry_picking (12) | 3 sources: positive, negative, balanced conclusion | 60-100 each |
| false_precision (10) | Explicitly approximate/preliminary data | 60-100 each |
| assumption_injection (8) | Pilot-only results with dedicated resources noted | 80-150 |

**Required elements rewrite rules:**
- Each case must have 3-6 elements
- Elements should be specific to the case (not generic "not mentioned")
- At least 1 element should reference a specific entity, number, or term from the context
- Elements are alternatives (any one matching = relevant), not all-required

### Step 3: Run scripts and validate
```bash
python scripts/rewrite_grounding_content.py
python scripts/rewrite_relevance_content.py
python -m fitz_gov.cli validate --data-dir data
```

### Step 4: Verify quality metrics
```bash
python scripts/coverage_report.py  # check context word counts
```

Post-rewrite targets:
- Grounding median context: >= 80 words
- Relevance median context: >= 60 words
- Zero shared 6-word query prefixes (within each category)
- forbidden_claims uniqueness: >= 80% (up from 43%)
- required_elements uniqueness: >= 60% (up from 17%)

## Approach

The rewrite scripts should use the existing domain content pools from the generators
as a starting point but expand each context into a full paragraph. The key insight
is that each domain already has 10 topic templates — these need to be expanded from
one-liners into multi-sentence passages with specific details that create hallucination
temptation.

**Example transformation (numerical_hallucination, technology):**

Before (17 words):
```
"The enterprise cloud migration project deployed 47 microservices across three AWS
regions. The project timeline spans 18 months with quarterly milestones."
```

After (120 words):
```
"The enterprise cloud migration project, codenamed Atlas, deployed 47 microservices
across three AWS regions (us-east-1, eu-west-1, ap-southeast-1) between January and
September 2024. The migration team of 23 engineers handled the transition from on-premises
VMware infrastructure to containerized workloads running on EKS. Performance benchmarks
showed that API response times improved from an average of 340ms to 89ms after migration,
with the CDN layer handling approximately 12,000 requests per second at peak. The project
timeline spans 18 months with quarterly milestones, and the team reported 99.97% uptime
during the transition period. Security audit identified zero critical vulnerabilities
in the new architecture, though 8 medium-severity items remain in the remediation backlog."
```

The richer context tempts hallucination about the project COST (not mentioned anywhere)
while providing many other specific numbers the LLM might incorrectly reference.

## Risks

- Script generation may still produce some formulaic patterns. Manual review of a sample
  (10% of cases) should be done before committing.
- Rich contexts increase JSON file sizes significantly (~3-5x for grounding/relevance files).
- Some domain pools may produce less natural content than others — social_media and history
  may need extra attention.

## Estimated Scope

- Script development: ~2 hours
- Content generation: automated
- Manual review of 10% sample: ~1 hour
- Validation: ~15 minutes
