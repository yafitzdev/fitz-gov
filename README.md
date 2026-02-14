# fitz-gov: Comprehensive RAG Governance Benchmark

fitz-gov is a benchmark for evaluating RAG system governance - the ability to know when to abstain, dispute, or provide trustworthy answers.

## Why fitz-gov?

Most RAG benchmarks focus on retrieval quality (BEIR) or answer correctness (RAGAS). But real-world RAG systems need **epistemic honesty** - knowing what they don't know.

fitz-gov measures:

| Category | What it Tests | Maps to |
|----------|--------------|---------|
| **Abstention** | Refuses when context is insufficient | `ABSTAIN` mode |
| **Dispute** | Flags conflicting sources | `DISPUTED` mode |
| **Trustworthy Hedged** | Hedges uncertain claims | `TRUSTWORTHY` mode |
| **Trustworthy Direct** | Answers confidently when evidence is clear | `TRUSTWORTHY` mode |
| **Grounding** | Answers are grounded in context (no hallucination) | Answer quality |
| **Relevance** | Answers address the actual question | Answer quality |

## Installation

```bash
pip install fitz-gov
```

Or install from local path during development:

```bash
pip install -e path/to/fitz-gov
```

## Quick Start

### Tiered Evaluation (Recommended)

fitz-gov uses a two-tier evaluation system:
- **Tier 0 (Sanity)**: 60 easy cases with 95% pass threshold - gates Tier 1
- **Tier 1 (Core)**: 2,920 discriminative cases with gradient scoring

```python
from fitz_gov import FitzGovEvaluator, load_tier, Tier, AnswerMode

# Load tiered cases
tier0_cases = load_tier(Tier.SANITY)  # 60 cases
tier1_cases = load_tier(Tier.CORE)    # 2,920 cases

# Your RAG system generates responses and modes for each tier
tier0_responses, tier0_modes = your_rag_system.evaluate(tier0_cases)
tier1_responses, tier1_modes = your_rag_system.evaluate(tier1_cases)

# Run tiered evaluation
evaluator = FitzGovEvaluator()
result = evaluator.evaluate_tiered(
    tier0_cases, tier0_responses, tier0_modes,
    tier1_cases, tier1_responses, tier1_modes,
)

print(result)
# fitz-gov Tiered Evaluation
# ==========================
#
# TIER 0 (Sanity Check): PASSED
#   Threshold: 95% | Achieved: 98.3% (59/60)
#
# TIER 1 (Core Benchmark): 69.1%
#   By Category:
#     abstention: 201/237 (84.8%)
#     dispute: 131/196 (66.8%)
#     ...
#
# Summary: Tier 0 PASSED, Tier 1 Score: 69.1%
```

### With Fitz RAG Engine

```python
from fitz_ai.evaluation.benchmarks import FitzGovBenchmark

# Create benchmark and evaluate your engine
benchmark = FitzGovBenchmark()
results = benchmark.evaluate(engine)

print(results)
```

**Note**: Both fitz-ai and fitz-gov use the same 3-mode system (TRUSTWORTHY, DISPUTED, ABSTAIN). The benchmark categories (trustworthy_hedged, trustworthy_direct) are test categories that describe what aspect of governance is being tested, not different modes.

### Standalone Usage (Any RAG System)

The `fitz-gov` package contains all evaluation logic, so any RAG system can be evaluated:

```python
from fitz_gov import FitzGovEvaluator, load_cases, FitzGovCategory, AnswerMode

# Load test cases
cases = load_cases()

# Create evaluator
evaluator = FitzGovEvaluator()

# Evaluate your RAG system's responses
responses = []
modes = []

for case in cases:
    # Your RAG system generates response
    response = your_rag_system.query(case.query, case.contexts)
    mode = your_rag_system.classify_mode(response)  # Your mode classification

    responses.append(response)
    modes.append(mode)

# Get comprehensive results
results = evaluator.evaluate_all(cases, responses, modes)
print(f"Overall accuracy: {results.overall_accuracy:.1%}")
```

### Evaluating Individual Cases

```python
from fitz_gov import FitzGovEvaluator, load_case_by_id

evaluator = FitzGovEvaluator()

# Load specific test case (IDs prefixed with t0_ or t1_)
case = load_case_by_id("t1_abstain_medium_001")

# Your system's response
response = "Based on the context provided, I cannot find information about..."
mode = AnswerMode.ABSTAIN

# Evaluate
result = evaluator.evaluate_case(case, response, mode)
print(f"Passed: {result.passed}")
print(f"Expected: {case.expected_mode.value}, Got: {mode.value}")
```

## Two-Pass Validation (Answer Quality Categories)

For grounding categories, fitz-gov uses **two-pass validation** to reduce false positives:

1. **Regex pass**: Fast pattern matching catches obvious violations
2. **LLM pass**: Semantic validation for flagged cases

### Enable LLM Validation

```python
from fitz_gov import FitzGovEvaluator

# Enable LLM validation with local Ollama
evaluator = FitzGovEvaluator(
    llm_validation=True,
    llm_model="qwen2.5:14b",  # or any Ollama model
    llm_base_url="http://localhost:11434"
)

# Responses flagged by regex are sent to LLM for semantic check
results = evaluator.evaluate_all(cases, responses, modes)
```

### Validation Flow

```
Response contains forbidden_claim pattern?
    |
    +- No  -> PASS (no hallucination detected)
    |
    +- Yes -> LLM validates: "Is this an actual hallucination?"
                |
                +- LLM says no (e.g., "no revenue mentioned") -> PASS
                |
                +- LLM says yes (fabricated specific value) -> FAIL
```

### Caching

LLM validation results are cached for 7 days to speed up repeated evaluations:
- Cache location: `~/.fitz/cache/llm_validation/`
- Automatic cache cleanup on expiry

## API Reference

### Core Classes

```python
from fitz_gov import (
    # Evaluator
    FitzGovEvaluator,

    # Data loading
    load_cases,
    load_tier,
    load_case_by_id,
    get_category_info,
    get_tier_info,
    get_data_dir,
    get_tier_dir,
    Tier,

    # Models
    FitzGovCategory,
    AnswerMode,
    FitzGovCase,
    FitzGovCaseResult,
    FitzGovCategoryResult,
    FitzGovConfusionMatrix,
    FitzGovResult,

    # Tiered Results
    TieredResult,
    Tier0Result,
    Tier1Result,

    # LLM Validation
    OllamaValidator,
    ValidatorConfig,
    ValidationResult,
)
```

### FitzGovEvaluator

```python
evaluator = FitzGovEvaluator(
    llm_validation=False,      # Enable two-pass validation
    llm_model="qwen2.5:14b",   # Ollama model for validation
    llm_base_url="http://localhost:11434"
)

# Tiered evaluation (recommended)
result = evaluator.evaluate_tiered(
    tier0_cases, tier0_responses, tier0_modes,
    tier1_cases, tier1_responses, tier1_modes,
    tier0_threshold=0.95,      # Default: 95%
    gating_enabled=True,       # Skip Tier 1 if Tier 0 fails
)

# Flat evaluation (all cases together)
results = evaluator.evaluate_all(cases, responses, modes)

# Evaluate single case
result = evaluator.evaluate_case(case, response, mode)
```

### Loading Test Cases

```python
# Load by tier (recommended)
tier0_cases = load_tier(Tier.SANITY)  # 60 sanity cases
tier1_cases = load_tier(Tier.CORE)    # 2,920 core cases

# Load all cases (2,980 total)
all_cases = load_cases()

# Load specific categories from a tier
abstention_tier0 = load_tier(Tier.SANITY, [FitzGovCategory.ABSTENTION])

# Load specific categories across all tiers
governance_cases = load_cases([
    FitzGovCategory.ABSTENTION,
    FitzGovCategory.DISPUTE,
])

# Load single case by ID (IDs prefixed with t0_ or t1_)
case = load_case_by_id("t1_dispute_medium_005")
```

## Data Format

Test cases are organized in a tiered structure:

```
data/
+-- tier0_sanity/               # 60 cases - baseline verification (95% threshold)
|   +-- abstention.json         # 12 cases
|   +-- dispute.json            # 12 cases
|   +-- trustworthy_hedged.json # 10 cases
|   +-- trustworthy_direct.json # 10 cases
|   +-- grounding.json          # 8 cases
|   +-- relevance.json          # 8 cases
+-- tier1_core/                 # 2,920 cases - discriminative benchmark
|   +-- abstention.json         # 685 cases
|   +-- dispute.json            # 675 cases
|   +-- trustworthy_hedged.json # 484 cases
|   +-- trustworthy_direct.json # 400 cases
|   +-- relevance.json          # 340 cases
|   +-- grounding.json          # 336 cases
+-- corpus/
|   +-- documents.jsonl    # reference documents
+-- queries/
|   +-- query_mappings.json  # query-to-document mappings
+-- validation/
    +-- human_validation_sample.json  # 250-case stratified sample for IAA
```

### Benchmark Distribution (v4.1)

#### Categories

**Tier 1 Core** (2,920 cases across 6 categories):

| Category | Cases | Med | Hard | Med % | Mode | Purpose |
|----------|------:|----:|-----:|------:|------|---------|
| Abstention | 685 | 255 | 430 | 37% | `abstain` | Refuses when evidence is insufficient |
| Dispute | 675 | 261 | 414 | 39% | `disputed` | Flags conflicting sources |
| Trustworthy Hedged | 484 | 171 | 313 | 35% | `trustworthy` | Hedges uncertain claims |
| Trustworthy Direct | 400 | 145 | 255 | 36% | `trustworthy` | Answers confidently when clear |
| Relevance | 340 | 129 | 211 | 38% | `trustworthy` | Answers address the actual question |
| Grounding | 336 | 128 | 208 | 38% | `trustworthy` | No hallucination beyond context |

**Tier 0 Sanity** (60 easy cases, 95% pass threshold):

| Category | Cases |
|----------|------:|
| Abstention | 12 |
| Dispute | 12 |
| Trustworthy Hedged | 10 |
| Trustworthy Direct | 10 |
| Grounding | 8 |
| Relevance | 8 |

#### Governance Mode Distribution

The 3-class classifier target distribution across tier1:

| Mode | Cases | % | Categories |
|------|------:|--:|------------|
| TRUSTWORTHY | 1,560 | 53.4% | Trustworthy Hedged + Direct + Grounding + Relevance |
| ABSTAIN | 685 | 23.5% | Abstention |
| DISPUTED | 675 | 23.1% | Dispute |

#### Difficulty Distribution

| Difficulty | Cases | % | Description |
|------------|------:|--:|-------------|
| Hard | 1,831 | 62.7% | Subtle patterns requiring careful reasoning |
| Medium | 1,089 | 37.3% | Clear patterns, moderate complexity |
| Easy | 60 | tier0 only | Obvious cases for sanity checking |

#### Domain Distribution

17 domains with no catch-all "general" category. Every case maps to a specific domain:

| Domain | Cases | % | Domain | Cases | % |
|--------|------:|--:|--------|------:|--:|
| Technology | 412 | 14.1% | Transportation | 131 | 4.5% |
| Medicine | 309 | 10.6% | Sports | 127 | 4.3% |
| Finance | 296 | 10.1% | Agriculture | 126 | 4.3% |
| Science | 192 | 6.6% | History | 122 | 4.2% |
| Government | 155 | 5.3% | HR/Workplace | 121 | 4.1% |
| Education | 152 | 5.2% | Real Estate | 119 | 4.1% |
| Environment | 147 | 5.0% | Psychology | 119 | 4.1% |
| Food | 143 | 4.9% | Social Media | 113 | 3.9% |
| Law | 136 | 4.7% | | | |

#### Query Type Distribution

| Type | Cases | % | Type | Cases | % |
|------|------:|--:|------|------:|--:|
| what | 821 | 28.1% | should | 135 | 4.6% |
| how | 694 | 23.8% | when | 121 | 4.1% |
| is | 437 | 15.0% | which | 97 | 3.3% |
| does | 284 | 9.7% | who | 77 | 2.6% |
| why | 213 | 7.3% | compare | 41 | 1.4% |

#### Source Type Distribution

| Source Type | Cases | % | Description |
|-------------|------:|--:|-------------|
| Single source | 2,656 | 91.0% | All contexts from one source |
| Multi-source | 264 | 9.0% | Contexts from different sources with `context_sources` metadata |

#### Reasoning Type Distribution

| Reasoning Type | Cases | % | Description |
|----------------|------:|--:|-------------|
| Factual | 1,588 | 54.4% | Straightforward fact retrieval |
| Evaluative | 596 | 20.4% | Requires judgment or assessment |
| Causal | 239 | 8.2% | Cause-and-effect reasoning |
| Comparative | 187 | 6.4% | Comparing entities or claims |
| Temporal | 178 | 6.1% | Time-dependent reasoning |
| Procedural | 132 | 4.5% | Step-by-step or process reasoning |

#### Evidence Pattern Distribution

| Evidence Pattern | Cases | % | Description |
|------------------|------:|--:|-------------|
| Direct | 1,039 | 35.6% | Context directly addresses the query |
| Absent | 637 | 21.8% | No relevant evidence in context |
| Conflicting | 587 | 20.1% | Sources contradict each other |
| Partial | 428 | 14.7% | Some evidence, but incomplete |
| Indirect | 195 | 6.7% | Evidence requires inference |
| Mixed | 34 | 1.2% | Combination of patterns |

#### Context Count Distribution

| Contexts per Case | Cases | % |
|-------------------|------:|--:|
| 1 | 923 | 31.6% |
| 2 | 1,094 | 37.5% |
| 3 | 785 | 26.9% |
| 4 | 115 | 3.9% |
| 5 | 3 | 0.1% |

#### Subcategories per Category

**Abstention** (23 subcategories):

| Subcategory | Cases | Subcategory | Cases |
|-------------|------:|-------------|------:|
| wrong_entity | 88 | converted_insufficient | 20 |
| wrong_specificity | 70 | converted_off_domain | 15 |
| temporal_mismatch | 66 | wrong_version | 12 |
| missing_data | 66 | implicit_only | 12 |
| off_topic_contradiction | 53 | wrong_granularity | 12 |
| wrong_domain | 51 | converted_wrong_entity | 10 |
| wrong_jurisdiction | 38 | multi_source_gap | 10 |
| outdated_context | 37 | cross_source_irrelevant | 9 |
| wrong_product | 34 | code_abstention | 8 |
| cross_domain_insufficient | 31 | topic_adjacent | 5 |
| decoy_keywords | 28 | format_impossible | 5 |
| | | converted_wrong_scope | 5 |

**Dispute** (19 subcategories):

| Subcategory | Cases | Subcategory | Cases |
|-------------|------:|-------------|------:|
| numerical_conflict | 86 | methodology_conflict | 38 |
| implicit_contradiction | 81 | interpretation_conflict | 33 |
| binary_conflict | 73 | competing_theories | 27 |
| opposing_conclusions | 72 | scientific_replication | 21 |
| temporal_conflict | 56 | cross_source_contradiction | 20 |
| statistical_direction_conflict | 45 | converted_contradiction | 19 |
| source_authority_conflict | 44 | conditional_conflict | 15 |
| | | converted_consensus_removed | 15 |
| | | converted_framing_conflict | 10 |
| | | temporal_source_conflict | 10 |
| | | contradictory_attribution | 5 |
| | | converted_version_conflict | 5 |

**Trustworthy Hedged** (20 subcategories):

| Subcategory | Cases | Subcategory | Cases |
|-------------|------:|-------------|------:|
| evidence_quality | 50 | evolving_facts | 26 |
| hedged_evidence | 33 | entity_ambiguity | 23 |
| different_aspects | 33 | partial_answer | 22 |
| causal_uncertainty | 32 | scope_condition | 21 |
| mixed_evidence | 32 | numerical_near_miss | 18 |
| temporal_uncertainty | 32 | cross_source_partial | 18 |
| version_overlap | 30 | implicit_assumptions | 17 |
| methodology_difference | 28 | adjacent_entity | 15 |
| stale_source | 28 | cross_domain_transfer | 13 |
| | | hedged_contradiction_corroborated | 8 |
| | | different_framing | 5 |

**Trustworthy Direct** (14 subcategories):

| Subcategory | Cases | Subcategory | Cases |
|-------------|------:|-------------|------:|
| technical_documented | 51 | cross_source_agreement | 25 |
| clear_explanation | 50 | direct_factual | 23 |
| contradiction_resolved | 40 | multi_source_convergence | 23 |
| opposing_with_consensus | 38 | authoritative_source | 22 |
| different_framing | 34 | near_complete_evidence | 21 |
| quantitative_answer | 30 | conditional_confidence | 17 |
| | | step_by_step | 13 |
| | | definitional | 13 |

**Grounding** (18 subcategories):

| Subcategory | Cases | Subcategory | Cases |
|-------------|------:|-------------|------:|
| numerical_hallucination | 37 | causal_hallucination | 16 |
| attribution_hallucination | 33 | comparative_hallucination | 13 |
| temporal_confusion | 33 | geographic_hallucination | 11 |
| entity_blending | 30 | technical_hallucination | 8 |
| process_hallucination | 28 | date_hallucination | 7 |
| quote_fabrication | 26 | location_hallucination | 7 |
| statistical_inference | 26 | code_grounding | 6 |
| code_hallucination | 23 | medical_hallucination | 5 |
| table_inference | 22 | quote_extension | 5 |

**Relevance** (19 subcategories):

| Subcategory | Cases | Subcategory | Cases |
|-------------|------:|-------------|------:|
| partial_answer | 31 | format_mismatch | 18 |
| wrong_entity_focus | 27 | summarization_vs_answer | 18 |
| temporal_mismatch | 27 | cherry_picking | 15 |
| tangent_drift | 26 | false_precision | 13 |
| related_but_different | 26 | assumption_injection | 10 |
| over_answering | 26 | symptom_only | 7 |
| granularity_mismatch | 24 | status_dump | 7 |
| prerequisite_missing | 24 | feature_dump | 7 |
| scope_mismatch | 22 | instruction_only | 6 |
| | | metric_avoidance | 6 |

#### Classification Attributes

Every case has 6 structured fields for slicing results:

| Field | Values | Purpose |
|-------|--------|---------|
| `domain` | 17 domains (technology, finance, medicine, ...) | Slice by topic area |
| `query_type` | what, how, is, does, why, should, when, who, which, compare | Slice by question form |
| `source_type` | single, multi_source | Single vs multi-source evidence |
| `context_count` | 1-5 | Number of context passages |
| `reasoning_type` | factual, evaluative, temporal, comparative, causal, procedural | What reasoning is tested |
| `evidence_pattern` | direct, absent, partial, conflicting, indirect, mixed | Evidence relationship to query |

#### Human Validation

A stratified 250-case sample is included at `data/validation/human_validation_sample.json` for computing inter-annotator agreement (IAA). See `docs/ANNOTATION_GUIDE.md` for annotation instructions and the decision tree for TRUSTWORTHY vs DISPUTED vs ABSTAIN classification.

Each case has:

```json
{
  "id": "t1_abstain_medium_001",
  "query": "What is the company's revenue for 2024?",
  "contexts": ["The company was founded in 2010..."],
  "expected_mode": "abstain",
  "category": "abstention",
  "subcategory": "wrong_entity",
  "difficulty": "medium",
  "description": "Query asks about revenue but context has no financial data",
  "rationale": "Context contains no financial data for the queried entity",
  "forbidden_claims": ["\\$\\d"],
  "required_elements": [],
  "domain": "finance",
  "query_type": "what",
  "source_type": "single",
  "context_count": 1,
  "reasoning_type": "factual",
  "evidence_pattern": "absent",
  "metadata": {"tier": "tier1_core"}
}
```

### Case Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique ID (prefixed `t0_` or `t1_`) |
| `query` | string | The question to answer |
| `contexts` | list[str] | Context passages provided to the RAG system |
| `expected_mode` | string | Expected governance mode (`abstain`, `disputed`, `trustworthy`) |
| `category` | string | Evaluation category (abstention, dispute, trustworthy_hedged, trustworthy_direct, grounding, relevance) |
| `subcategory` | string | Specific test pattern (e.g., `wrong_entity`, `implicit_contradiction`) |
| `difficulty` | string | `easy`, `medium`, or `hard` |
| `description` | string | What the case tests |
| `rationale` | string | Why this mode is expected |
| `forbidden_claims` | list[str] | Regex patterns indicating hallucination (grounding) |
| `required_elements` | list[str] | Elements that must appear in the answer (relevance) |
| `domain` | string | Topic area (technology, finance, medicine, etc.) |
| `query_type` | string | Question form (what, how, is, does, why, etc.) |
| `source_type` | string | `single` or `multi_source` |
| `context_count` | int | Number of context passages |
| `reasoning_type` | string | factual, causal, comparative, procedural, evaluative, temporal |
| `evidence_pattern` | string | direct, indirect, conflicting, absent, partial, mixed |

## Version

Current version: **4.1.0**

See [CHANGELOG.md](CHANGELOG.md) for release history and [docs/roadmap](docs/roadmap/) for implementation details.

## Architecture Note

fitz-gov is designed as a standalone package so that:

1. **Any RAG system** can benchmark against the same test cases
2. **Evaluation logic is consistent** - all systems get identical evaluation
3. **Test data is versioned** - reproducible benchmarks across releases

For Fitz RAG engine integration, see `fitz_ai.evaluation.benchmarks.FitzGovBenchmark` which wraps this package. Both fitz-ai and fitz-gov use the same 3-mode system (TRUSTWORTHY, DISPUTED, ABSTAIN). The benchmark categories (trustworthy_hedged, trustworthy_direct, etc.) are test categories that describe different governance behaviors being tested, not different output modes.

## Contributing

We welcome contributions! To add new test cases:

1. Fork this repo
2. Add cases to the appropriate `data/tier0_sanity/` or `data/tier1_core/` JSON file
3. Run validation: `python -m fitz_gov.cli validate --data-dir data`
4. Submit a PR

## License

MIT License - see [LICENSE](LICENSE) for details.
