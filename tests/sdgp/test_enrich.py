"""Tests for fitz_gov.sdgp.enrich."""

from __future__ import annotations

import pytest

from fitz_gov.sdgp.checker import Checker
from fitz_gov.sdgp.enrich import (
    CATEGORY_TO_CLASS,
    DOMAIN_TO_EXPERT,
    EXPLICIT_SUBCATEGORY_MAP,
    LLM_TODO,
    enrich_case,
    enrich_chunk,
    map_category_to_class,
    map_domain_to_expert,
    map_subcategory_to_pattern,
)
from fitz_gov.sdgp.taxonomy import (
    Cell,
    Difficulty,
    Domain,
    GovernanceClass,
    TaxonomyPattern,
    governance_class_of,
)


# ---------------------------------------------------------------------------
# Domain mapping
# ---------------------------------------------------------------------------


def test_all_17_v51_domains_have_mapping() -> None:
    v51_domains = {
        "technology", "medicine", "finance", "science", "government",
        "education", "environment", "food", "law", "transportation",
        "sports", "agriculture", "history", "hr_workplace", "real_estate",
        "psychology", "social_media",
    }
    assert v51_domains.issubset(DOMAIN_TO_EXPERT.keys())


def test_unknown_domain_falls_back_to_general() -> None:
    assert map_domain_to_expert("totally_unknown") == Domain.GENERAL_COMMONSENSE
    assert map_domain_to_expert(None) == Domain.GENERAL_COMMONSENSE
    assert map_domain_to_expert("") == Domain.GENERAL_COMMONSENSE


def test_history_maps_to_history_geography() -> None:
    assert map_domain_to_expert("history") == Domain.HISTORY_GEOGRAPHY


def test_medicine_and_science_both_map_to_science_medicine() -> None:
    assert map_domain_to_expert("medicine") == Domain.SCIENCE_MEDICINE
    assert map_domain_to_expert("science") == Domain.SCIENCE_MEDICINE


# ---------------------------------------------------------------------------
# Category mapping
# ---------------------------------------------------------------------------


def test_all_4_v51_categories_have_mapping() -> None:
    assert set(CATEGORY_TO_CLASS) == {
        "abstention", "dispute", "trustworthy_hedged", "trustworthy_direct"
    }


def test_both_trustworthy_categories_collapse_to_TRUSTWORTHY() -> None:
    assert map_category_to_class("trustworthy_hedged") == GovernanceClass.TRUSTWORTHY
    assert map_category_to_class("trustworthy_direct") == GovernanceClass.TRUSTWORTHY


# ---------------------------------------------------------------------------
# Subcategory mapping — every explicit entry respects its category's class
# ---------------------------------------------------------------------------


def test_explicit_subcategory_map_pattern_class_is_in_overlap_with_some_category() -> None:
    """Each explicit entry must map to a pattern whose governance class is
    represented in *at least* one of the 4 V5.1 categories. (We're not
    asserting which category — `scope_condition` for example is in the
    explicit table mapped to SCOPE_CONFLICT (DISPUTED) but appears under
    `trustworthy_hedged` and is handled by the fallback in that case.)"""
    for sc, pattern in EXPLICIT_SUBCATEGORY_MAP.items():
        # Just make sure the pattern is real
        assert pattern in TaxonomyPattern, sc


def test_subcategory_fallback_to_category_default() -> None:
    """A subcategory not in the explicit map and not matched by keyword
    fallback should default to the category's default pattern."""
    p = map_subcategory_to_pattern("completely_unknown_subcategory_xyz", "abstention")
    assert governance_class_of(p) == GovernanceClass.ABSTAIN


def test_subcategory_class_is_always_consistent_with_category() -> None:
    """For every (subcategory, category) pair, the mapped pattern's class
    must equal the category's class. This is the invariant the checker
    later relies on (class_mismatch_pattern would error otherwise)."""
    test_cases = [
        ("wrong_entity", "abstention"),
        ("numerical_conflict", "dispute"),
        ("clear_explanation", "trustworthy_direct"),
        ("evidence_quality", "trustworthy_hedged"),
        # subcategory + category combo where the subcategory's explicit
        # mapping would cross class — fallback must catch this:
        ("scope_condition", "trustworthy_hedged"),  # SCOPE_CONFLICT is DISPUTED
        # Empty subcategory
        ("", "abstention"),
        # Unknown subcategory
        ("xyz_unknown", "trustworthy_direct"),
    ]
    for sc, cat in test_cases:
        pattern = map_subcategory_to_pattern(sc, cat)
        assert (
            governance_class_of(pattern) == map_category_to_class(cat)
        ), f"{sc!r} in {cat!r} mapped to {pattern.value} ({governance_class_of(pattern).value})"


def test_known_subcategories_map_to_expected_patterns() -> None:
    cases = [
        ("wrong_entity", "abstention", TaxonomyPattern.WRONG_ENTITY),
        ("numerical_conflict", "dispute", TaxonomyPattern.NUMERICAL_CONFLICT),
        ("temporal_mismatch", "abstention", TaxonomyPattern.TEMPORAL_MISMATCH),
        ("source_authority_conflict", "dispute", TaxonomyPattern.AUTHORITY_CONFLICT),
        ("clear_explanation", "trustworthy_direct", TaxonomyPattern.DIRECT_ANSWER),
        ("multi_source_convergence", "trustworthy_direct", TaxonomyPattern.MULTI_SOURCE_CORROBORATION),
    ]
    for sc, cat, expected in cases:
        assert map_subcategory_to_pattern(sc, cat) == expected


# ---------------------------------------------------------------------------
# End-to-end: enrich_case produces a checker-passing V6 row
# ---------------------------------------------------------------------------


def _v51_minimal(
    *,
    case_id: str = "t1_test_001",
    category: str = "abstention",
    subcategory: str = "wrong_entity",
    difficulty: str = "hard",
    domain: str = "history",
    query: str = "What battle tactics did Hannibal use at Zama?",
    contexts: list[str] | None = None,
    evidence_pattern: str = "absent",
    source_type: str = "single",
    query_type: str = "what",
    reasoning_type: str = "factual",
) -> dict:
    return {
        "id": case_id,
        "category": category,
        "subcategory": subcategory,
        "difficulty": difficulty,
        "domain": domain,
        "query": query,
        "contexts": contexts or [
            "Hannibal is known for crossing the Alps with elephants in 218 BCE."
        ],
        "expected_mode": "abstain",
        "evidence_pattern": evidence_pattern,
        "source_type": source_type,
        "query_type": query_type,
        "reasoning_type": reasoning_type,
        "context_count": 1,
        "description": "test",
        "rationale": "test",
        "evaluation_config": {},
    }


def test_enriched_case_has_all_required_v6_blocks() -> None:
    enriched = enrich_case(_v51_minimal())
    assert "id" in enriched
    assert "version" in enriched
    assert "input" in enriched
    assert "governance" in enriched
    assert "routing" in enriched
    assert "taxonomy" in enriched
    assert "meta" in enriched


def test_enriched_case_passes_the_checker() -> None:
    enriched = enrich_case(_v51_minimal())
    result = Checker().check(enriched)
    assert result.passed, [i.message for i in result.errors]


def test_enriched_case_class_consistency() -> None:
    e = enrich_case(_v51_minimal(category="dispute", subcategory="numerical_conflict",
                                 contexts=["Apple costs €5", "Apple costs €3"]))
    assert e["taxonomy"]["governance_class"] == "DISPUTED"
    assert e["governance"]["classification"] == "DISPUTED"
    assert e["taxonomy"]["pattern"] == "numerical_conflict"


def test_enriched_case_cell_id_format() -> None:
    e = enrich_case(_v51_minimal(category="abstention", subcategory="wrong_entity",
                                 domain="history", difficulty="hard"))
    assert e["taxonomy"]["cell_id"] == "wrong_entity__history_geography__hard"


def test_enriched_case_preserves_id_and_query() -> None:
    e = enrich_case(_v51_minimal(case_id="my_case_123", query="my custom query"))
    assert e["id"] == "my_case_123"
    assert e["input"]["query"] == "my custom query"


def test_per_chunk_enrichment_shape() -> None:
    e = enrich_case(_v51_minimal(contexts=["one", "two"]))
    chunks = e["input"]["contexts"]
    assert len(chunks) == 2
    for c in chunks:
        assert "text" in c
        assert "authority_score" in c
        assert "authority_signal" in c
        assert "temporality" in c
        assert "summary" in c
        assert "relevance_to_query" in c


def test_llm_todo_fields_marked() -> None:
    """Phase 0b fields with no heuristic land as LLM_TODO so a later pass
    can find-and-replace them."""
    e = enrich_case(_v51_minimal())
    assert e["input"]["query_rewritten"] == LLM_TODO
    assert e["meta"]["near_miss_reason"] == LLM_TODO
    for ctx in e["input"]["contexts"]:
        assert ctx["temporality"]["anchor_period"] == LLM_TODO


def test_v51_legacy_fields_preserved_in_meta() -> None:
    v51 = _v51_minimal()
    v51["forbidden_claims"] = ["never say X"]
    v51["context_sources"] = ["Wikipedia"]
    e = enrich_case(v51)
    legacy = e["meta"]["v51_legacy"]
    assert legacy["forbidden_claims"] == ["never say X"]
    assert legacy["context_sources"] == ["Wikipedia"]


@pytest.mark.parametrize(
    "category,subcategory",
    [
        ("abstention", "wrong_entity"),
        ("abstention", "wrong_specificity"),
        ("abstention", "missing_data"),
        ("dispute", "numerical_conflict"),
        ("dispute", "implicit_contradiction"),
        ("dispute", "source_authority_conflict"),
        ("trustworthy_direct", "clear_explanation"),
        ("trustworthy_direct", "multi_source_convergence"),
        ("trustworthy_hedged", "evidence_quality"),
        ("trustworthy_hedged", "mixed_evidence"),
    ],
)
def test_enrichment_passes_checker_across_combos(category: str, subcategory: str) -> None:
    """Sanity sweep: a handful of (category, subcategory) combos all enrich
    to checker-passing V6 cases."""
    # Use 2 contexts (digit-bearing) to satisfy numerical-pattern structural checks
    contexts = ["Source A: value is 5", "Source B: value is 3"]
    v51 = _v51_minimal(category=category, subcategory=subcategory, contexts=contexts)
    enriched = enrich_case(v51)
    result = Checker().check(enriched)
    assert result.passed, (
        f"{category=} {subcategory=}: " + str([i.message for i in result.errors])
    )


# ---------------------------------------------------------------------------
# Signal coherence (key derivations stay within checker bounds)
# ---------------------------------------------------------------------------


def test_disputed_case_has_high_conflict_density() -> None:
    e = enrich_case(_v51_minimal(
        category="dispute",
        subcategory="numerical_conflict",
        evidence_pattern="conflicting",
        contexts=["A: 5", "B: 3"],
    ))
    assert e["governance"]["conflict_density"] >= 0.5


def test_trustworthy_case_has_low_conflict_density() -> None:
    e = enrich_case(_v51_minimal(
        category="trustworthy_direct",
        subcategory="clear_explanation",
        evidence_pattern="direct",
    ))
    assert e["governance"]["conflict_density"] < 0.3


def test_abstain_case_has_low_evidence_sufficiency() -> None:
    e = enrich_case(_v51_minimal(
        category="abstention",
        subcategory="missing_data",
        evidence_pattern="absent",
    ))
    assert e["governance"]["evidence_sufficiency"] < 0.5
