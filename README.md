# fitz-gov: Comprehensive RAG Governance Benchmark

fitz-gov is a benchmark for evaluating RAG system governance - the ability to know when to abstain, dispute, qualify, or confidently answer questions.

## Why fitz-gov?

Most RAG benchmarks focus on retrieval quality (BEIR) or answer correctness (RAGAS). But real-world RAG systems need **epistemic honesty** - knowing what they don't know.

fitz-gov measures:

| Category | What it Tests | Maps to |
|----------|--------------|---------|
| **Abstention** | Refuses when context is insufficient | `ABSTAIN` mode |
| **Dispute** | Flags conflicting sources | `DISPUTED` mode |
| **Qualification** | Hedges uncertain claims | `QUALIFIED` mode |
| **Confidence** | Answers confidently when evidence is clear | `CONFIDENT` mode |
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
- **Tier 1 (Core)**: 271 discriminative cases with gradient scoring

```python
from fitz_gov import FitzGovEvaluator, load_tier, Tier, AnswerMode

# Load tiered cases
tier0_cases = load_tier(Tier.SANITY)  # 60 cases
tier1_cases = load_tier(Tier.CORE)    # 271 cases

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
# TIER 1 (Core Benchmark): 78.1%
#   By Category:
#     abstention: 26/30 (86.7%)
#     dispute: 22/30 (73.3%)
#     ...
#
# Summary: Tier 0 PASSED, Tier 1 Score: 78.1%
```

### With Fitz RAG Engine

```python
from fitz_ai.evaluation.benchmarks import FitzGovBenchmark

# Create benchmark and evaluate your engine
benchmark = FitzGovBenchmark()
results = benchmark.evaluate(engine)

print(results)
```

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

# Load specific test case
case = load_case_by_id("abstain_001")

# Your system's response
response = "Based on the context provided, I cannot find information about..."
mode = AnswerMode.ABSTAIN

# Evaluate
result = evaluator.evaluate_case(case, response, mode)
print(f"Passed: {result.passed}")
print(f"Expected: {case.expected_mode.value}, Got: {mode.value}")
```

## Two-Pass Validation (Answer Quality Categories)

For grounding and relevance categories, fitz-gov uses **two-pass validation** to reduce false positives:

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
    │
    ├─ No  → PASS (no hallucination detected)
    │
    └─ Yes → LLM validates: "Is this an actual hallucination?"
                │
                ├─ LLM says no (e.g., "no revenue mentioned") → PASS
                │
                └─ LLM says yes (fabricated specific value) → FAIL
```

### Caching

LLM validation results are cached for 7 days to speed up repeated evaluations:
- Cache location: `~/.cache/fitz_gov/`
- Automatic cache cleanup on startup

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
tier1_cases = load_tier(Tier.CORE)    # 271 core cases

# Load all cases (331 total)
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
├── tier0_sanity/          # 60 cases - baseline verification (95% threshold)
│   ├── abstention.json    # 12 cases
│   ├── dispute.json       # 12 cases
│   ├── qualification.json # 10 cases
│   ├── confidence.json    # 10 cases
│   ├── grounding.json     # 8 cases
│   └── relevance.json     # 8 cases
├── tier1_core/            # 271 cases - discriminative benchmark
│   ├── abstention.json    # 51 cases
│   ├── dispute.json       # 43 cases
│   ├── qualification.json # 58 cases
│   ├── confidence.json    # 53 cases
│   ├── grounding.json     # 34 cases
│   └── relevance.json     # 32 cases
└── corpus/
    └── documents.jsonl    # 378 reference documents
```

Each case has:

```json
{
  "id": "abstain_001",
  "query": "What is the company's revenue for 2024?",
  "contexts": ["The company was founded in 2010..."],
  "expected_mode": "abstain",
  "subcategory": "different_domain",
  "difficulty": "medium",
  "mode_rationale": "Context contains no financial data",
  "evaluation_config": {
    "forbidden_claims": ["\\$\\d"],
    "allowed_phrases": ["not specified", "cannot find"]
  }
}
```

## Version

Current version: **2.0.0**

See [CHANGELOG.md](CHANGELOG.md) for release history and [docs/roadmap](docs/roadmap/) for implementation details.

## Architecture Note

fitz-gov is designed as a standalone package so that:

1. **Any RAG system** can benchmark against the same test cases
2. **Evaluation logic is consistent** - all systems get identical evaluation
3. **Test data is versioned** - reproducible benchmarks across releases

For Fitz RAG engine integration, see `fitz_ai.evaluation.benchmarks.FitzGovBenchmark` which wraps this package.

## Contributing

We welcome contributions! To add new test cases:

1. Fork this repo
2. Add cases to the appropriate `data/<category>/` directory
3. Run validation: `python scripts/validate.py`
4. Submit a PR

## License

MIT License - see [LICENSE](LICENSE) for details.
