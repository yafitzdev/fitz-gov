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
- **Tier 1 (Core)**: 2,054 discriminative cases with gradient scoring

```python
from fitz_gov import FitzGovEvaluator, load_tier, Tier, AnswerMode

# Load tiered cases
tier0_cases = load_tier(Tier.SANITY)  # 60 cases
tier1_cases = load_tier(Tier.CORE)    # 2,054 cases

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
tier1_cases = load_tier(Tier.CORE)    # 2,054 core cases

# Load all cases (2,114 total)
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
+-- tier1_core/                 # 2,054 cases - discriminative benchmark
|   +-- abstention.json         # 467 cases
|   +-- dispute.json            # 409 cases
|   +-- trustworthy_hedged.json # 414 cases
|   +-- trustworthy_direct.json # 218 cases
|   +-- grounding.json          # 271 cases
|   +-- relevance.json          # 275 cases
+-- corpus/
|   +-- documents.jsonl    # 1,420 reference documents
+-- queries/
    +-- query_mappings.json  # 898 query-to-document mappings
```

### Benchmark Distribution (v4.0)

**Categories** (2,054 tier1 cases):

| Category | Cases | Mode | Purpose |
|----------|------:|------|---------|
| Abstention | 467 | `abstain` | Refuses when evidence is insufficient |
| Trustworthy Hedged | 414 | `trustworthy` | Hedges uncertain claims |
| Dispute | 409 | `disputed` | Flags conflicting sources |
| Relevance | 275 | `trustworthy` | Answers address the actual question |
| Grounding | 271 | `trustworthy` | No hallucination beyond context |
| Trustworthy Direct | 218 | `trustworthy` | Answers confidently when clear |

**Domains** (18 domains, no domain untestable):

| Domain | Cases | % | Domain | Cases | % |
|--------|------:|--:|--------|------:|--:|
| Technology | 584 | 28.4 | Sports | 69 | 3.4 |
| Medicine | 227 | 11.1 | Food | 68 | 3.3 |
| Finance | 214 | 10.4 | HR/Workplace | 66 | 3.2 |
| Science | 109 | 5.3 | Social Media | 64 | 3.1 |
| Education | 95 | 4.6 | Agriculture | 63 | 3.1 |
| Environment | 82 | 4.0 | Real Estate | 58 | 2.8 |
| Law | 78 | 3.8 | History | 57 | 2.8 |
| Government | 74 | 3.6 | Psychology | 55 | 2.7 |
| Transportation | 71 | 3.5 | General | 20 | 1.0 |

**Query Types** (10 types):

| Type | Cases | % | Type | Cases | % |
|------|------:|--:|------|------:|--:|
| what | 822 | 40.0 | should | 86 | 4.2 |
| how | 379 | 18.5 | why | 82 | 4.0 |
| is | 285 | 13.9 | when | 78 | 3.8 |
| does | 184 | 9.0 | which | 63 | 3.1 |
| | | | who | 45 | 2.2 |
| | | | compare | 30 | 1.5 |

**Classification Attributes** - every case has 6 structured fields for results slicing:

| Field | Values | Purpose |
|-------|--------|---------|
| `domain` | 18 domains (technology, finance, medicine, ...) | Slice by topic area |
| `query_type` | what, how, is, does, why, should, when, who, which, compare | Slice by question form |
| `source_type` | single, multi_source (138 cases) | Single vs multi-source evidence |
| `context_count` | 1-5 | Number of context passages |
| `reasoning_type` | factual, evaluative, temporal, comparative, causal, procedural | What reasoning is tested |
| `evidence_pattern` | direct, absent, partial, conflicting, indirect, mixed | Evidence relationship to query |

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

Current version: **4.0.0**

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
