# fitz-gov Test Case Roadmap

Target: **200 test cases** across 6 governance categories.

## Current Status (v0.9.0) ✓ COMPLETE

| Category | Current | Target | Progress |
|----------|---------|--------|----------|
| **Abstention** | **40** | 40 | **100%** |
| **Dispute** | **40** | 40 | **100%** |
| **Qualification** | **40** | 40 | **100%** |
| **Confidence** | **30** | 30 | **100%** |
| **Grounding** | **25** | 25 | **100%** |
| **Relevance** | **25** | 25 | **100%** |
| **Total** | **200** | **200** | **100%** |

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

**Confidence** (30/30) ✓
- System should answer confidently when evidence is clear and unambiguous
- Subcategories:
  - direct_factual (4): Simple factual questions with explicit answers
  - explicit_causal (5): Why questions with cause explicitly stated
  - complete_requirements (3): Requirements with full list provided
  - complete_explanation (4): How/mechanism questions fully explained
  - quantitative_clear (4): Number questions with precise figures
  - definition_provided (3): What-is questions with clear definitions
  - comparison_explicit (2): Comparisons with clear data for both sides
  - temporal_explicit (2): When questions with precise dates/times
  - procedural_complete (2): How-to with complete step-by-step
  - attribution_clear (1): Who questions with explicit attribution

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

**Relevance** (25/25) ✓
- Answers must address the actual question asked
- Tests use "required elements" that must appear in valid answers
- Subcategories:
  - feature_dump (3): Answers with features instead of specific requested info
  - metric_avoidance (3): Qualitative description instead of concrete numbers
  - status_dump (3): Progress/status instead of specific dates/milestones
  - symptom_only (3): Effects/symptoms instead of causes/mechanisms
  - instruction_only (2): How-to instead of specifications/requirements
  - tangent_drift (3): Context shifts to related but different topic
  - partial_answer (3): Answers part but misses key aspect asked
  - wrong_entity_focus (2): Discusses entity X when asked about entity Y
  - temporal_mismatch (2): Info from wrong time period than asked
  - scope_mismatch (1): Wrong level of detail (global vs local)

## Expansion History

1. ~~**Qualification**~~ ✓ (v0.3.0) - Was 10% accuracy, now has comprehensive coverage
2. ~~**Grounding**~~ ✓ (v0.4.0) - Critical for hallucination prevention
3. ~~**Abstention**~~ ✓ (v0.5.0) - Core safety behavior
4. ~~**Dispute**~~ ✓ (v0.6.0) - Important for epistemic honesty
5. ~~**Relevance**~~ ✓ (v0.7.0) - Answer quality metric
6. ~~**Confidence**~~ ✓ (v0.8.0) - Ensure system isn't overly cautious

## Corpus Requirements

| Version | Documents | Notes |
|---------|-----------|-------|
| v0.2.0 | 100 | Initial handcrafted corpus |
| v0.3.0 | 128 | +28 for qualification expansion |
| v0.4.0 | 146 | +18 for grounding expansion |
| v0.5.0 | 175 | +29 for abstention expansion |
| v0.6.0 | 233 | +58 for dispute expansion |
| v0.7.0 | 258 | +25 for relevance expansion |
| v0.8.0 | 288 | +30 for confidence expansion |

Each test case expansion requires corresponding corpus documents with:
- Relevant documents that support the test query
- Decoy documents that are topically related but don't answer the question
- Conflicting documents for dispute tests

## Version History

- **v0.9.0** - Schema improvements & evaluation refinements:
  - Fixed expected_mode for grounding (25) and relevance (25) categories: "confident" → "qualified"
  - Added evaluation_config with regex patterns, allowed_phrases, forbidden_elements
  - Standardized schema: version, mode_rationale, evaluation_config across all categories
  - Added validation script (scripts/validate.py)
  - Added mode decision tree documentation (docs/mode-decision-tree.md)
- **v0.8.0** - Confidence expansion (10 → 30 cases, 258 → 288 docs) - **TARGET REACHED!**
- **v0.7.0** - Relevance expansion (5 → 25 cases, 233 → 258 docs)
- **v0.6.0** - Dispute expansion (10 → 40 cases, 175 → 233 docs)
- **v0.5.0** - Abstention expansion (10 → 40 cases, 146 → 175 docs)
- **v0.4.0** - Grounding expansion (5 → 25 cases, 128 → 146 docs)
- **v0.3.0** - Qualification expansion (10 → 40 cases, 100 → 128 docs)
- **v0.2.0** - Initial handcrafted test set (50 cases, 100 docs)
- **v0.1.0** - Auto-generated test set (deprecated)

## Summary

fitz-gov v0.9.0 achieves the target of **200 test cases** with **288 corpus documents** across 6 governance categories. Version 0.9.0 includes improved schema consistency and enhanced evaluation mechanisms with regex-based forbidden_claims and forbidden_elements for detecting hallucinations and irrelevant answers.

The benchmark comprehensively tests RAG system governance including:

- **When to refuse** (abstention) - 40 cases
- **When to flag conflicts** (dispute) - 40 cases
- **When to hedge** (qualification) - 40 cases
- **When to be confident** (confidence) - 30 cases
- **Hallucination prevention** (grounding) - 25 cases
- **Answer relevance** (relevance) - 25 cases
