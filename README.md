# FITZ-GOV: Comprehensive RAG Governance Benchmark

FITZ-GOV is a benchmark for evaluating RAG system governance - the ability to know when to abstain, dispute, qualify, or confidently answer questions.

## Why FITZ-GOV?

Most RAG benchmarks focus on retrieval quality (BEIR) or answer correctness (RAGAS). But real-world RAG systems need **epistemic honesty** - knowing what they don't know.

FITZ-GOV measures:

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

### With Fitz RAG Engine

```python
from fitz_ai.evaluation.benchmarks import FitzGovBenchmark

# Create benchmark and evaluate your engine
benchmark = FitzGovBenchmark()
results = benchmark.evaluate(engine)

print(results)
# FITZ-GOV Results (n=200):
#   Overall Accuracy: 78.33%
#
# Governance Mode Categories:
#   Abstention: 82.50% (33/40)
#   Dispute: 75.00% (30/40)
#   Qualification: 72.50% (29/40)
#   Confidence: 85.00% (34/40)
#
# Answer Quality Categories:
#   Grounding: 80.00% (20/25)
#   Relevance: 77.50% (19/25)
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

For grounding and relevance categories, FITZ-GOV uses **two-pass validation** to reduce false positives:

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
    load_case_by_id,
    get_category_info,
    get_data_dir,

    # Models
    FitzGovCategory,
    AnswerMode,
    FitzGovCase,
    FitzGovCaseResult,
    FitzGovCategoryResult,
    FitzGovConfusionMatrix,
    FitzGovResult,

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

# Evaluate all cases
results = evaluator.evaluate_all(cases, responses, modes)

# Evaluate single case
result = evaluator.evaluate_case(case, response, mode)
```

### Loading Test Cases

```python
# Load all cases (200 total)
cases = load_cases()

# Load specific categories
governance_cases = load_cases([
    FitzGovCategory.ABSTENTION,
    FitzGovCategory.DISPUTE,
])

quality_cases = load_cases([
    FitzGovCategory.GROUNDING,
    FitzGovCategory.RELEVANCE,
])

# Load single case by ID
case = load_case_by_id("dispute_005")
```

## Data Format

Test cases are JSON files organized by category:

```
data/
├── abstention/
│   └── abstention.json    # 40 cases
├── dispute/
│   └── dispute.json       # 40 cases
├── qualification/
│   └── qualification.json # 40 cases
├── confidence/
│   └── confidence.json    # 30 cases
├── grounding/
│   └── grounding.json     # 25 cases
└── relevance/
    └── relevance.json     # 25 cases
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

Current version: **0.9.1**

See [docs/roadmap.md](docs/roadmap.md) for test case coverage details.

## Architecture Note

FITZ-GOV is designed as a standalone package so that:

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
