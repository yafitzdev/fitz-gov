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
# Just the data (no generator)
pip install fitz-gov

# With synthetic test case generator
pip install fitz-gov[generator]
```

## Usage with Fitz

```python
from fitz_ai.evaluation.benchmarks import FitzGovBenchmark

# Downloads data automatically from GitHub releases
benchmark = FitzGovBenchmark()
results = benchmark.evaluate(engine)

print(results)
# FITZ-GOV Results (n=240):
#   Overall Accuracy: 78.33%
#
# Governance Mode Categories:
#   Abstention: 82.50% (33/40)
#   Dispute: 75.00% (30/40)
#   Qualification: 72.50% (29/40)
#   Confidence: 85.00% (34/40)
#
# Answer Quality Categories:
#   Grounding: 80.00% (32/40)
#   Relevance: 77.50% (31/40)
```

## Standalone Usage

```python
from fitz_gov import load_cases, FitzGovCase

# Load all test cases
cases = load_cases()

# Load specific category
abstention_cases = load_cases(categories=["abstention"])

# Evaluate your own system
for case in cases:
    your_answer = your_rag_system.answer(case.query, case.contexts)
    your_mode = classify_answer_mode(your_answer)
    passed = your_mode == case.expected_mode
```

## Bootstrapping from BEIR

The recommended way to generate FITZ-GOV benchmark data is to bootstrap from BEIR corpora:

```bash
# Install with generator dependencies
pip install fitz-gov[generator]

# See available BEIR datasets
fitz-gov bootstrap --list-datasets

# Bootstrap from recommended datasets (scifact, nfcorpus, fiqa)
export OPENAI_API_KEY=your_key
fitz-gov bootstrap --output ./data --num-cases 50

# Or use specific datasets
fitz-gov bootstrap --datasets scifact,hotpotqa --output ./data

# Use Anthropic instead
export ANTHROPIC_API_KEY=your_key
fitz-gov bootstrap --llm-provider anthropic --output ./data
```

This downloads BEIR corpus documents and uses an LLM to generate governance test cases.

## Generating Custom Test Cases

Generate benchmark cases from your own corpus:

```bash
# Generate abstention cases
fitz-gov generate abstention --corpus ./my_docs --output ./my_cases

# Generate all categories
fitz-gov generate all --corpus ./my_docs --output ./my_cases
```

```python
from fitz_gov.generator import FitzGovGenerator

generator = FitzGovGenerator(llm_client=your_client)

# Generate from your chunks
cases = generator.generate_abstention_cases(your_chunks, num_cases=50)
cases += generator.generate_dispute_cases(your_chunks, num_cases=50)
# ... etc
```

## Data Format

Test cases are JSON files organized by category:

```
data/
├── abstention/
│   ├── no_context.json
│   └── out_of_scope.json
├── dispute/
│   └── contradicting_facts.json
├── qualification/
│   └── causal_without_evidence.json
├── confidence/
│   └── clear_answers.json
├── grounding/
│   └── hallucination_traps.json
└── relevance/
    └── off_topic_traps.json
```

Each JSON file:

```json
{
  "description": "Category description",
  "cases": [
    {
      "id": "abstain_001",
      "query": "What is the company's revenue for 2024?",
      "contexts": ["The company was founded in 2010..."],
      "expected_mode": "abstain",
      "description": "Question about data not in context",
      "rationale": "Context contains no financial data",
      "forbidden_claims": [],
      "required_elements": []
    }
  ]
}
```

## Contributing

We welcome contributions! To add new test cases:

1. Fork this repo
2. Add cases to the appropriate `data/<category>/` directory
3. Run validation: `fitz-gov validate`
4. Submit a PR

## License

MIT License - see [LICENSE](LICENSE) for details.
