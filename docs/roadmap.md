# FITZ-GOV Test Case Roadmap

Target: **200 test cases** across 6 governance categories.

## Current Status (v0.6.0)

| Category | Current | Target | Progress |
|----------|---------|--------|----------|
| **Abstention** | **40** | 40 | **100%** |
| **Dispute** | **40** | 40 | **100%** |
| **Qualification** | **40** | 40 | **100%** |
| Confidence | 10 | 30 | 33% |
| **Grounding** | **25** | 25 | **100%** |
| Relevance | 5 | 25 | 20% |
| **Total** | **160** | **200** | **80%** |

## Category Descriptions

### Governance Mode Categories

These test the system's ability to select the correct answer mode.

**Abstention** (40/40) ✓
- System should refuse to answer when context is irrelevant or insufficient
- Subcategories:
  - different_domain (12): Query and context are completely unrelated fields
  - wrong_entity (10): Same domain but different company/person/product
  - wrong_time_period (3): Same topic but different time
  - wrong_aspect (6): Same subject but different aspect (causes vs effects)
  - partial_topic (4): Related info but missing the key detail asked
  - decoy_keywords (5): Context has keywords from query but doesn't answer

**Dispute** (40/40) ✓
- System should flag when sources contain conflicting information
- Subcategories:
  - direct_contradiction (11): Sources state opposite facts
  - numerical_disagreement (6): Different numbers for same metric
  - temporal_conflict (3): Conflicting timelines or dates
  - competing_theories (4): Alternative explanations for same phenomenon
  - source_conflict (4): Official vs unofficial sources disagree
  - conditional_conflict (6): Context-dependent contradictions
  - methodological_conflict (4): Different methodologies yield different results

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

**Grounding** (25/25) ✓
- Answers must be grounded in context (no hallucination)
- Tests use "forbidden claims" that would indicate hallucination
- Subcategories:
  - numerical_hallucination (6): Revenue, prices, percentages, counts
  - name_hallucination (2): People, founders, executives
  - date_hallucination (3): Dates, timelines, deadlines
  - technical_hallucination (3): Specs, features, languages
  - medical_hallucination (3): Side effects, dosages, success rates
  - location_hallucination (2): Addresses, countries, regions
  - process_hallucination (3): Steps, procedures, workflows
  - attribution_hallucination (3): Quotes, sources, citations

**Relevance** (5/25)
- Answers must address the actual question asked
- Tests use "required elements" that must appear in valid answers

## Expansion Priority

1. ~~**Qualification**~~ ✓ (v0.3.0) - Was 10% accuracy, now has comprehensive coverage
2. ~~**Grounding**~~ ✓ (v0.4.0) - Critical for hallucination prevention
3. ~~**Abstention**~~ ✓ (v0.5.0) - Core safety behavior
4. ~~**Dispute**~~ ✓ (v0.6.0) - Important for epistemic honesty
5. **Relevance** - Answer quality metric
6. **Confidence** - Ensure system isn't overly cautious

## Corpus Requirements

| Version | Documents | Notes |
|---------|-----------|-------|
| v0.2.0 | 100 | Initial handcrafted corpus |
| v0.3.0 | 128 | +28 for qualification expansion |
| v0.4.0 | 146 | +18 for grounding expansion |
| v0.5.0 | 175 | +29 for abstention expansion |
| v0.6.0 | 233 | +58 for dispute expansion |
| Target | ~250 | Support all 200 test cases |

Each test case expansion requires corresponding corpus documents with:
- Relevant documents that support the test query
- Decoy documents that are topically related but don't answer the question
- Conflicting documents for dispute tests

## Version History

- **v0.6.0** - Dispute expansion (10 → 40 cases, 175 → 233 docs)
- **v0.5.0** - Abstention expansion (10 → 40 cases, 146 → 175 docs)
- **v0.4.0** - Grounding expansion (5 → 25 cases, 128 → 146 docs)
- **v0.3.0** - Qualification expansion (10 → 40 cases, 100 → 128 docs)
- **v0.2.0** - Initial handcrafted test set (50 cases, 100 docs)
- **v0.1.0** - Auto-generated test set (deprecated)
