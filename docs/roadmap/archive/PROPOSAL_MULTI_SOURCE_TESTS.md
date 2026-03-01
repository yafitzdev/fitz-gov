# Proposal: Multi-Source Test Cases for fitz-gov

> **Status**: Draft
> **Created**: 2026-02-10
> **Target Version**: v4.0.0
> **Depends On**: fitz-ai classifier source agreement feature work

---

## Problem

The fitz-gov test suite is overwhelmingly single-source. Analysis from fitz-ai classifier development (Experiment 6, 1113-case evaluation) found that **1098/1113 cases (98.7%) have `num_unique_sources=1`**. Each test case's `contexts` list contains passages that are either from a single document or are synthetic passages with no distinct source identity.

This creates three concrete blockers:

1. **Source agreement features cannot be trained.** The `num_unique_sources` feature is high-value for governance classification (source diversity predicts confident vs disputed), but the classifier cannot learn from it when the training data has near-zero variance on this dimension.

2. **The test set does not reflect production conditions.** Real knowledge bases contain multiple documents from different authors, time periods, and quality levels. A system ingesting a company wiki, regulatory docs, and vendor reports will routinely retrieve chunks from 3-5 distinct sources per query. The current test set never exercises this path.

3. **Cross-source signal development is blocked.** Features like claim alignment across sources, source authority weighting, and inter-source consistency scoring require multi-source test cases to evaluate. Without them, these features cannot be validated or tuned.

### Current Source Distribution

| num_unique_sources | Case Count | Percentage |
|--------------------|-----------|------------|
| 1                  | ~1098     | 98.7%      |
| 2+                 | ~15       | 1.3%       |

The few multi-context cases that exist (e.g., dispute cases with 2-4 contradicting passages) simulate multiple sources textually but do not carry distinct source metadata. From the classifier's perspective, they are all single-source.

---

## What Multi-Source Tests Require

Multi-source test cases differ from existing cases in two ways:

### 1. Distinct Source Identity per Context

Each context passage must have an explicit source identifier (simulating different documents in a knowledge base). The existing `contexts` field remains a list of strings, but a new `context_sources` field maps each context to its source metadata.

Proposed addition to the test case schema:

```json
{
  "id": "t1_dispute_ms_001",
  "category": "dispute",
  "subcategory": "cross_source_contradiction",
  "difficulty": "hard",
  "query": "What is the company's annual revenue?",
  "contexts": [
    "TechCorp reported annual revenue of $4.2 billion in its 2024 annual report.",
    "According to the SEC 10-K filing, TechCorp's 2024 revenue was $3.8 billion.",
    "A Bloomberg analyst note estimated TechCorp revenue at $4.0 billion for 2024."
  ],
  "context_sources": [
    {"source_id": "techcorp_annual_report_2024", "source_type": "company_report", "authority": "primary"},
    {"source_id": "sec_10k_techcorp_2024", "source_type": "regulatory_filing", "authority": "authoritative"},
    {"source_id": "bloomberg_techcorp_analysis", "source_type": "analyst_note", "authority": "secondary"}
  ],
  "expected_mode": "disputed",
  "description": "Three sources report different revenue figures for the same company and period",
  "rationale": "Revenue figures conflict across sources ($4.2B vs $3.8B vs $4.0B) despite covering the same entity and period"
}
```

### 2. Source Metadata Fields

Each source entry in `context_sources` carries:

| Field | Type | Purpose |
|-------|------|---------|
| `source_id` | string | Unique document identifier (simulates `chunk.doc_id`) |
| `source_type` | string | Document type (e.g., `regulatory_filing`, `blog_post`, `peer_reviewed`) |
| `authority` | string | Source quality tier: `authoritative`, `primary`, `secondary`, `weak` |

These fields enable the classifier to compute:
- `num_unique_sources` (count of distinct `source_id` values)
- Source agreement signals (do authoritative sources agree?)
- Authority-weighted confidence (authoritative source vs blog post)

---

## Proposed Test Categories

### Category 1: Multi-Source Agreement

**Subcategory**: `cross_source_agreement`
**Expected Mode**: `confident`
**Count**: 15 cases

Multiple independent sources provide the same answer. The system should recognize cross-source convergence as a confidence booster.

Example patterns:
- 3 authoritative sources agree on a factual claim
- Regulatory filing + company report + independent audit all state the same figure
- Multiple technical references converge on the same specification

```json
{
  "subcategory": "cross_source_agreement",
  "query": "What is the minimum capital requirement for EU banks under Basel III?",
  "contexts": [
    "The European Banking Authority (EBA) requires a minimum CET1 ratio of 4.5% under Basel III.",
    "The ECB's supervisory guidance document states the Basel III minimum CET1 ratio is 4.5%.",
    "BIS published standards confirm the minimum Common Equity Tier 1 ratio at 4.5%."
  ],
  "context_sources": [
    {"source_id": "eba_guidelines_2024", "source_type": "regulatory", "authority": "authoritative"},
    {"source_id": "ecb_supervisory_2024", "source_type": "regulatory", "authority": "authoritative"},
    {"source_id": "bis_basel3_standards", "source_type": "international_standard", "authority": "authoritative"}
  ],
  "expected_mode": "confident",
  "rationale": "Three independent regulatory bodies state the identical figure"
}
```

**Classifier signal**: High `num_unique_sources` + low cross-source variance = confident.

### Category 2: Multi-Source Conflict

**Subcategory**: `cross_source_contradiction`
**Expected Mode**: `disputed`
**Count**: 15 cases

Sources directly contradict each other on factual claims. The system should detect the disagreement regardless of individual source quality.

Example patterns:
- Two authoritative sources report different numbers for the same metric
- One source says "approved", another says "rejected"
- Technical specifications conflict across vendor documentation

**Classifier signal**: High `num_unique_sources` + high cross-source variance = disputed.

### Category 3: Multi-Source Partial Agreement

**Subcategory**: `cross_source_partial`
**Expected Mode**: `qualified`
**Count**: 10 cases

Sources agree on some claims but diverge on others. The system should qualify its answer, noting the areas of agreement and divergence.

Example patterns:
- All sources agree on the general direction (revenue grew) but disagree on magnitude (15% vs 22%)
- Sources agree on what happened but disagree on why
- Multiple sources report overlapping but non-identical lists (3 of 5 risk factors match)

```json
{
  "subcategory": "cross_source_partial",
  "query": "What were the main causes of the product recall?",
  "contexts": [
    "The manufacturer cited a faulty sensor and software glitch as the two causes of the recall.",
    "The NHTSA investigation identified the faulty sensor, software glitch, and inadequate quality control as contributing factors.",
    "An independent lab found the sensor issue but attributed the software behavior to a design flaw rather than a glitch."
  ],
  "context_sources": [
    {"source_id": "manufacturer_statement", "source_type": "company_report", "authority": "primary"},
    {"source_id": "nhtsa_investigation", "source_type": "regulatory_filing", "authority": "authoritative"},
    {"source_id": "independent_lab_report", "source_type": "technical_report", "authority": "secondary"}
  ],
  "expected_mode": "qualified",
  "rationale": "Sources agree on the sensor issue but diverge on root cause characterization and completeness"
}
```

**Classifier signal**: High `num_unique_sources` + moderate cross-source variance + partial claim overlap = qualified.

### Category 4: Source Quality Asymmetry

**Subcategory**: `source_authority_conflict`
**Expected Mode**: varies (see below)
**Count**: 10 cases

Sources of different authority levels disagree. Tests whether the system appropriately weights source quality.

Sub-patterns:

| Pattern | Expected Mode | Rationale |
|---------|--------------|-----------|
| Authoritative vs weak source disagree | `qualified` | Authoritative source likely correct, but conflict exists |
| Two authoritative sources disagree | `disputed` | Cannot resolve by authority alone |
| Weak source confirms authoritative | `confident` | Agreement despite quality gap reinforces confidence |

```json
{
  "subcategory": "source_authority_conflict",
  "query": "Is the drug effective for treating migraines?",
  "contexts": [
    "The FDA-approved prescribing information states the drug reduces migraine frequency by 50% in clinical trials.",
    "A wellness blog reports the drug is ineffective based on user anecdotes."
  ],
  "context_sources": [
    {"source_id": "fda_prescribing_info", "source_type": "regulatory_filing", "authority": "authoritative"},
    {"source_id": "wellness_blog_2024", "source_type": "blog_post", "authority": "weak"}
  ],
  "expected_mode": "qualified",
  "rationale": "Authoritative source supports efficacy, but a conflicting source exists even if weak"
}
```

### Category 5: Temporal Source Disagreement

**Subcategory**: `temporal_source_conflict`
**Expected Mode**: varies
**Count**: 10 cases

Sources from different time periods provide different information. Tests whether the system can reason about temporal validity.

Sub-patterns:

| Pattern | Expected Mode | Rationale |
|---------|--------------|-----------|
| Newer source supersedes older | `confident` (on newer data) | More recent information takes precedence |
| Both old and new are valid for their periods | `qualified` | Answer depends on time frame |
| Contradicting sources with unclear temporal ordering | `disputed` | Cannot determine which is current |

---

## Summary of Proposed Cases

| Category | Subcategory | Expected Mode | Count |
|----------|-------------|---------------|-------|
| Multi-source agreement | `cross_source_agreement` | confident | 15 |
| Multi-source conflict | `cross_source_contradiction` | disputed | 15 |
| Multi-source partial agreement | `cross_source_partial` | qualified | 10 |
| Source quality asymmetry | `source_authority_conflict` | varies | 10 |
| Temporal source disagreement | `temporal_source_conflict` | varies | 10 |
| **Total** | | | **60** |

---

## Integration with Existing Tiers

### Tier Placement: Tier 1 (Core Benchmark)

Multi-source cases are **Tier 1 only**. Rationale:

- These are hard classification problems that test nuanced signal processing, not basic functionality.
- Tier 0 (sanity gate, 95% threshold) should remain single-source to verify baseline mode selection works.
- Multi-source reasoning is an advanced capability; failing on it should not gate Tier 1 evaluation.

### File Organization

New cases go into existing category files in `data/tier1_core/`:

| File | New Subcategories Added |
|------|------------------------|
| `confidence.json` | `cross_source_agreement` |
| `dispute.json` | `cross_source_contradiction` |
| `qualification.json` | `cross_source_partial`, `source_authority_conflict` (qualified variants), `temporal_source_conflict` (qualified variants) |
| `dispute.json` | `source_authority_conflict` (disputed variants), `temporal_source_conflict` (disputed variants) |
| `confidence.json` | `source_authority_conflict` (confident variants), `temporal_source_conflict` (confident variants) |

### ID Convention

Follow existing pattern with a `_ms_` (multi-source) infix:

```
t1_dispute_ms_001
t1_confident_ms_001
t1_qualify_ms_001
```

This makes multi-source cases easy to filter without a schema change.

---

## Schema Changes

### FitzGovCase Model

Add an optional `context_sources` field:

```python
@dataclass
class FitzGovCase:
    # ... existing fields ...
    context_sources: list[dict[str, str]] = field(default_factory=list)
    """Source metadata for each context. Maps 1:1 with contexts list.
    Each dict has: source_id, source_type, authority."""
```

### JSON Schema

Add `context_sources` as an optional array in the case JSON. Existing cases without it are treated as single-source (backward compatible).

### Loader Changes

The loader (`loader.py`) requires no changes -- `context_sources` flows through `metadata` or is added as a first-class field via `from_dict()`.

### Evaluator Changes

The evaluator (`evaluator.py`) requires no changes for governance mode evaluation. Mode comparison (`expected_mode == actual_mode`) is source-agnostic. The source metadata is consumed by the fitz-ai classifier during feature extraction, not by the fitz-gov evaluator.

---

## Corpus Requirements

Multi-source cases need corresponding corpus documents when used in Mode B (full pipeline) evaluation. For each multi-source case:

- Add 2-4 documents to `data/corpus/documents.jsonl` with distinct `id` values.
- Each document's content should match the test case context it represents.
- Update `data/corpus/manifest.json` with revised document count.
- Add `query_mappings` entries linking queries to their relevant document IDs.

Estimated corpus additions: **100-150 new documents** (60 cases x 2-3 sources per case, minus reuse).

---

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| fitz-ai `num_unique_sources` feature extraction | Exists | Already computed as `len(set(c.doc_id for c in chunks))` |
| fitz-ai source agreement features | Blocked by this work | Cannot develop without multi-source test data |
| fitz-gov schema update for `context_sources` | Required | Backward-compatible addition |
| Corpus document expansion | Required | 100-150 new documents |

---

## Implementation Plan

### Phase 1: Schema and Infrastructure (1 week)

1. Add `context_sources` field to `FitzGovCase` in `models.py` and `schema.py`.
2. Update `from_dict()` and `to_dict()` methods.
3. Update `validate.py` to validate `context_sources` when present.
4. Verify backward compatibility (all existing 1173 cases load without error).

### Phase 2: Test Case Authoring (2-3 weeks)

1. Write 15 `cross_source_agreement` cases (confident).
2. Write 15 `cross_source_contradiction` cases (disputed).
3. Write 10 `cross_source_partial` cases (qualified).
4. Write 10 `source_authority_conflict` cases (mixed modes).
5. Write 10 `temporal_source_conflict` cases (mixed modes).
6. Add corresponding corpus documents.

### Phase 3: Validation and Integration (1 week)

1. Run `fitz-gov validate` on updated dataset.
2. Verify `num_unique_sources` distribution: target >= 5% of total cases with `num_unique_sources >= 2`.
3. Run fitz-ai classifier evaluation with expanded dataset.
4. Measure impact on source agreement feature importance.

### Phase 4: Release (1 week)

1. Update CHANGELOG.md, README.md.
2. Bump version to 4.0.0 (major: new schema field).
3. Update manifest and distribution counts.
4. Tag and release.

**Total estimated effort**: 5-6 weeks.

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Multi-source cases added | >= 60 |
| Cases with `num_unique_sources >= 2` | >= 5% of total |
| Cases with `num_unique_sources >= 3` | >= 2% of total |
| All existing tests still pass validation | 100% |
| `context_sources` field present on all new cases | 100% |
| Classifier `num_unique_sources` feature importance | Measurable (non-zero) in GBT |

---

## Open Questions

1. **Should `context_sources` be required or optional?** Proposed: optional, with validation warning if missing on cases with 2+ contexts.

2. **Should authority levels be an enum or free-form string?** Proposed: enum (`authoritative`, `primary`, `secondary`, `weak`) to enable structured feature extraction.

3. **Should we retroactively add `context_sources` to existing multi-context cases?** Proposed: yes, for the ~15 existing cases that have 2+ contexts, to improve data consistency.

4. **Version: v3.0 or v4.0?** The user request references v4.0. If v3.0 is already planned for other work, these go in v4.0. If not, this could be v3.0.
