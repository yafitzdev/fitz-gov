# fitz-gov/scripts/consolidate_subcategories.py
"""
Consolidate ~156 subcategory slugs into ~54 canonical types.

Rationale: Many subcategories are slug variants of the same concept
(e.g. wrong_entity, wrong_entity_pure, high_similarity_wrong_entity).
For classifier training, we need subcategories that are:
1. Distinct enough to be meaningful diagnostic categories
2. Large enough to measure (5+ cases each)
3. Not so many that analysis is unwieldy

This script:
1. Remaps subcategory slugs to canonical types
2. Preserves the original subcategory in a new `original_subcategory` field
3. Writes updated files back to tier1_core/
4. Prints a before/after summary
"""
import json
import os
from collections import Counter

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
TIER1_DIR = os.path.join(DATA_DIR, "tier1_core")

# === CONSOLIDATION MAP ===
# Format: "original_slug" -> "canonical_slug"
# Slugs not listed here are kept as-is.

ABSTENTION_MAP = {
    # wrong_entity family (25 cases)
    "wrong_entity_pure": "wrong_entity",
    "high_similarity_wrong_entity": "wrong_entity",
    "near_miss_entity": "wrong_entity",
    "vague_entity_reference": "wrong_entity",
    # wrong_domain family (16)
    "domain_bleed": "wrong_domain",
    "partial_topic": "wrong_domain",
    # wrong_version family (12)
    "version_near_miss": "wrong_version",
    "version_mismatch": "wrong_version",
    # wrong_jurisdiction family (12)
    "jurisdictional_mismatch": "wrong_jurisdiction",
    "wrong_jurisdiction_conflicts": "wrong_jurisdiction",
    # temporal_mismatch family (13)
    "wrong_time_period": "temporal_mismatch",
    "temporal_gap": "temporal_mismatch",
    "temporal_staleness": "temporal_mismatch",
    "stale_data": "temporal_mismatch",
    # wrong_product family (10)
    "adjacent_product": "wrong_product",
    # wrong_specificity family (13)
    "scope_mismatch": "wrong_specificity",
    "wrong_aspect": "wrong_specificity",
    # missing_data family (16)
    "partial_schema_match": "missing_data",
    "table_absence": "missing_data",
    "partial_coverage": "missing_data",
    "insufficient_comparative": "missing_data",
    # off_topic_contradiction family (16)
    "off_topic_contradicting": "off_topic_contradiction",
    "irrelevant_internal_tension": "off_topic_contradiction",
    # keep as-is: decoy_keywords(11), format_impossible(5), topic_adjacent(5),
    #             code_abstention(3), cross_domain_insufficient(3)
}

CONFIDENCE_MAP = {
    # direct_factual family (9)
    "direct_factual_pure": "direct_factual",
    "definition_provided": "direct_factual",
    "explicit_recency": "direct_factual",
    # authoritative_source family (10)
    "single_authoritative": "authoritative_source",
    "official_statement": "authoritative_source",
    "expert_consensus": "authoritative_source",
    # multi_source_convergence family (13)
    "multi_source_convergence_pure": "multi_source_convergence",
    "multi_source_agreement": "multi_source_convergence",
    # clear_explanation family (24)
    "complete_explanation": "clear_explanation",
    "clear_causal_explanation": "clear_explanation",
    "explicit_causal": "clear_explanation",
    "clear_procedural": "clear_explanation",
    "procedural_complete": "clear_explanation",
    # quantitative_answer family (17)
    "quantitative_available": "quantitative_answer",
    "quantitative_clear": "quantitative_answer",
    "unambiguous_extraction": "quantitative_answer",
    "table_extraction": "quantitative_answer",
    "bounded_claim": "quantitative_answer",
    # technical_documented family (17)
    "well_documented_technical": "technical_documented",
    "api_confidence": "technical_documented",
    "code_documentation": "technical_documented",
    "json_navigation": "technical_documented",
    "complete_requirements": "technical_documented",
    # different_framing family (15)
    "different_framing_same_fact": "different_framing",
    "apparent_contradiction_granularity": "different_framing",
    "minor_disagreement_clear_answer": "different_framing",
    # contradiction_resolved family (15)
    "contradiction_clear_winner": "contradiction_resolved",
    "slight_variation_same_answer": "contradiction_resolved",
    "numerical_diff_methodology_explained": "contradiction_resolved",
    # near_complete family (10)
    "clear_answer_minor_edge": "near_complete_evidence",
    # conditional_confidence family (6)
    "regulatory_specification": "conditional_confidence",
    "comparison_explicit": "conditional_confidence",
    # keep as-is: opposing_with_consensus(6)
}

DISPUTE_MAP = {
    # numerical_conflict family (16)
    "same_metric_different_values": "numerical_conflict",
    "same_claim_different_values": "numerical_conflict",
    "numerical_disagreement": "numerical_conflict",
    "unit_scale_mismatch": "numerical_conflict",
    "confidence_interval_overlap": "numerical_conflict",
    # opposing_conclusions family (20)
    "opposing_conclusions_genuine": "opposing_conclusions",
    "opposing_recommendations": "opposing_conclusions",
    # implicit_contradiction family (12)
    "semantic_ambiguity": "implicit_contradiction",
    # binary_conflict family (10)
    "binary_fact_conflict": "binary_conflict",
    "contradictory_status": "binary_conflict",
    "definition_conflict": "binary_conflict",
    # temporal_conflict family (12)
    "contradictory_dates": "temporal_conflict",
    "time_context_conflict": "temporal_conflict",
    "time_dependent_contradiction": "temporal_conflict",
    # methodology_conflict family (8)
    "methodological_conflict": "methodology_conflict",
    "methodology_incompatible": "methodology_conflict",
    "scope_conflict": "methodology_conflict",
    "scope_disagreement": "methodology_conflict",
    # keep as-is: contradictory_attribution(5), statistical_direction_conflict(5),
    #             competing_theories(6), conditional_conflict(6), source_conflict(4)
}

QUALIFICATION_MAP = {
    # hedged_evidence family (18)
    "hedged_claims": "hedged_evidence",
    "hedged_source": "hedged_evidence",
    "hedged_vs_assertive": "hedged_evidence",
    # methodology_difference — keep, absorb relabeled (14)
    "methodology_difference_relabeled": "methodology_difference",
    # temporal_uncertainty family (20)
    "same_claim_different_timeperiods": "temporal_uncertainty",
    "temporal_extrapolation": "temporal_uncertainty",
    "outdated_confidence": "temporal_uncertainty",
    "temporal_ordering_unclear": "temporal_uncertainty",
    "temporal_ambiguity": "temporal_uncertainty",
    # scope_condition family (15)
    "same_claim_different_conditions": "scope_condition",
    "conditional_applicability": "scope_condition",
    # causal_uncertainty family (22)
    "causal_without_evidence": "causal_uncertainty",
    "correlation_causation": "causal_uncertainty",
    "reverse_causation": "causal_uncertainty",
    "multiple_confounders": "causal_uncertainty",
    "partial_correlation": "causal_uncertainty",
    # evidence_quality family (23)
    "source_quality_variance": "evidence_quality",
    "source_quality_asymmetry": "evidence_quality",
    "source_quality": "evidence_quality",
    "small_sample_weak": "evidence_quality",
    "small_sample": "evidence_quality",
    "population_mismatch": "evidence_quality",
    # mixed_evidence family (16)
    "incomplete_evidence": "mixed_evidence",
    "prediction_insufficient_data": "mixed_evidence",
    # entity_ambiguity family (20)
    "scope_ambiguity_pure": "entity_ambiguity",
    "scope_ambiguity": "entity_ambiguity",
    "multiple_interpretations": "entity_ambiguity",
    "metric_ambiguity": "entity_ambiguity",
    # partial_answer family (20)
    "related_missing_specific": "partial_answer",
    "right_topic_wrong_infotype": "partial_answer",
    "tangential_useful": "partial_answer",
    # evolving_facts family (17)
    "evolving_facts_source_quality": "evolving_facts",
    # different_aspects family (35)
    "same_topic_different_aspects": "different_aspects",
    "pros_cons_same_thing": "different_aspects",
    "risk_vs_benefit": "different_aspects",
    # version_overlap family (19)
    "adjacent_version_overlap": "version_overlap",
    "version_mismatch_breaking": "version_overlap",
    "deprecated_documented": "version_overlap",
    "deprecation_qualification": "version_overlap",
    # stale_source family (19)
    "stale_authoritative": "stale_source",
    "stale_contradictory_partial": "stale_source",
    "old_likely_valid": "stale_source",
    # implicit_assumptions family (7)
    "attribution_error": "implicit_assumptions",
    # adjacent_entity family (13)
    "adjacent_entity_overlap": "adjacent_entity",
    "adjacent_entity_contradictory_hedged": "adjacent_entity",
    # keep as-is: hedged_contradiction_corroborated(8), numerical_near_miss(10)
    # cross_domain_transfer family (11)
    "partial_answer_definitive": "cross_domain_transfer",
}

CATEGORY_MAPS = {
    "abstention": ABSTENTION_MAP,
    "confidence": CONFIDENCE_MAP,
    "dispute": DISPUTE_MAP,
    "qualification": QUALIFICATION_MAP,
}


def consolidate():
    total_remapped = 0
    summary = {}

    for cat, slug_map in CATEGORY_MAPS.items():
        fname = f"{cat}.json"
        fpath = os.path.join(TIER1_DIR, fname)

        with open(fpath, encoding="utf-8") as f:
            data = json.load(f)

        cases = data["cases"]
        before_counts = Counter(c["subcategory"] for c in cases)
        remapped = 0

        for case in cases:
            old_subcat = case["subcategory"]
            if old_subcat in slug_map:
                case["original_subcategory"] = old_subcat
                case["subcategory"] = slug_map[old_subcat]
                remapped += 1

        after_counts = Counter(c["subcategory"] for c in cases)
        total_remapped += remapped

        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        summary[cat] = {
            "before": len(before_counts),
            "after": len(after_counts),
            "remapped": remapped,
            "counts": after_counts,
        }

        print(f"\n{'=' * 60}")
        print(f"  {cat.upper()}: {len(before_counts)} -> {len(after_counts)} subcategories ({remapped} cases remapped)")
        print(f"{'=' * 60}")
        for subcat, count in sorted(after_counts.items(), key=lambda x: (-x[1], x[0])):
            marker = " <<<" if count <= 2 else (" <<" if count <= 4 else "")
            print(f"  {count:3d}  {subcat}{marker}")

    print(f"\n{'=' * 60}")
    print(f"  TOTAL: {sum(s['before'] for s in summary.values())} -> {sum(s['after'] for s in summary.values())} subcategories")
    print(f"  Cases remapped: {total_remapped}")
    print(f"{'=' * 60}")

    # Check for remaining thin subcategories
    thin = []
    for cat, s in summary.items():
        for subcat, count in s["counts"].items():
            if count < 3:
                thin.append((cat, subcat, count))
    if thin:
        print(f"\n  WARNING: {len(thin)} subcategories still have <3 cases:")
        for cat, subcat, count in thin:
            print(f"    {cat}/{subcat}: {count}")


if __name__ == "__main__":
    consolidate()
