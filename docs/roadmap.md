# FITZ-GOV Test Case Roadmap

Target: **200 test cases** across 6 governance categories.

## Current Status (v0.3.0)

| Category | Current | Target | Progress |
|----------|---------|--------|----------|
| Abstention | 10 | 40 | 25% |
| Dispute | 10 | 40 | 25% |
| **Qualification** | **40** | 40 | **100%** |
| Confidence | 10 | 30 | 33% |
| Grounding | 5 | 25 | 20% |
| Relevance | 5 | 25 | 20% |
| **Total** | **80** | **200** | **40%** |

## Category Descriptions

### Governance Mode Categories

These test the system's ability to select the correct answer mode.

**Abstention** (10/40)
- System should refuse to answer when context is irrelevant or insufficient
- Subcategories: no_relevant_context, out_of_scope, insufficient_detail

**Dispute** (10/40)
- System should flag when sources contain conflicting information
- Subcategories: direct_contradiction, numeric_disagreement, competing_theories

**Qualification** (40/40) ✓
- System should hedge when evidence is incomplete or uncertain
- Subcategories:
  - causal_without_evidence (12): "Why" questions with only "what/that" data
  - correlation_causation (8): Confounding variable traps
  - prediction_insufficient_data (9): Future predictions from historical data
  - small_sample (4): Generalizations from tiny samples
  - incomplete_evidence (5): Partial information presented as complete
  - attribution_error (2): Multiple factors for single outcome

**Confidence** (10/30)
- System should answer confidently when evidence is clear and unambiguous
- Subcategories: direct_factual, explicit_causal, complete_requirements

### Answer Quality Categories

These test the quality of generated answers.

**Grounding** (5/25)
- Answers must be grounded in context (no hallucination)
- Tests use "forbidden claims" that would indicate hallucination

**Relevance** (5/25)
- Answers must address the actual question asked
- Tests use "required elements" that must appear in valid answers

## Expansion Priority

1. ~~**Qualification**~~ ✓ (v0.3.0) - Was 10% accuracy, now has comprehensive coverage
2. **Grounding** - Critical for hallucination prevention
3. **Abstention** - Core safety behavior
4. **Dispute** - Important for epistemic honesty
5. **Relevance** - Answer quality metric
6. **Confidence** - Ensure system isn't overly cautious

## Corpus Requirements

| Version | Documents | Notes |
|---------|-----------|-------|
| v0.2.0 | 100 | Initial handcrafted corpus |
| v0.3.0 | 128 | +28 for qualification expansion |
| Target | ~250 | Support all 200 test cases |

Each test case expansion requires corresponding corpus documents with:
- Relevant documents that support the test query
- Decoy documents that are topically related but don't answer the question
- Conflicting documents for dispute tests

## Version History

- **v0.3.0** - Qualification expansion (10 → 40 cases, 100 → 128 docs)
- **v0.2.0** - Initial handcrafted test set (50 cases, 100 docs)
- **v0.1.0** - Auto-generated test set (deprecated)
