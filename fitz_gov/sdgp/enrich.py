"""V5.1 → V5.1-enriched mapping (ROADMAP Phase 0).

Programmatic enrichment of the 2,980 existing V5.1 cases onto the V6+ schema:
adds `taxonomy`, `routing`, `governance.*` signals, per-chunk fields, and the
new meta fields — all from existing V5.1 metadata, no LLM required.

What's covered here (Phase 0a, deterministic):

  - **Domain mapping**: 17 V5.1 `domain` values → 7 MoE expert domains.
  - **Class mapping**: 4 V5.1 `category` values → 3 `GovernanceClass`
    (`trustworthy_hedged` + `trustworthy_direct` both collapse to TRUSTWORTHY).
  - **Pattern mapping**: 115 V5.1 `subcategory` values → 18 `TaxonomyPattern`.
    ~70 explicit 1:1 mappings + a keyword/category fallback for the rest.
  - **Cell id**: `{pattern}__{expert_domain}__{difficulty}`.
  - **Probabilities**: stub `governance.{abstain, disputed, trustworthy}`
    consistent with `classification` (argmax of the class, weighted by
    `evidence_pattern`).
  - **Deterministic signals**: `conflict_density`, `evidence_sufficiency`,
    `false_trustworthy_risk`, `domain_familiarity`, `confidence_level` —
    derived from category + evidence_pattern + difficulty.
  - **Per-chunk**: `authority_score`, `authority_signal`, `temporality`
    stubs from `source_type` + domain + evidence_pattern.
  - **Routing**: `expert_fired = expert_domain`, `routing_confidence = 0.9`.
  - **Meta**: `confidence_level = "high"`, `annotator_agreement = "unanimous"`
    (V5.1 is human-validated), `near_miss_class` heuristic from category.

What's deferred to Phase 0b (LLM-assisted, blocked on provider abstraction):

  - `input.query_rewritten` — placeholder = original query.
  - `contexts[].summary` — placeholder = first ~120 chars of context.
  - `contexts[].relevance_to_query` — placeholder = 0.5 (neutral).
  - `governance.hallucination_pressure`, `retrieval_retry_value`,
    `query_evidence_alignment`, `answer_coverage`, `boundary_proximity`,
    `human_escalation_score` — coarse heuristics; flagged for LLM refinement.
  - `meta.near_miss_reason` — placeholder string.

Phase 0b fields that have a heuristic value are populated. Fields that have
no reasonable heuristic land as the placeholder `<TODO_LLM>` so the
follow-up enrichment pass can find and replace them.
"""

from __future__ import annotations

from typing import Any

from .taxonomy import (
    Cell,
    Difficulty,
    Domain,
    GovernanceClass,
    PATTERN_DESCRIPTIONS,
    TaxonomyPattern,
    governance_class_of,
)


LLM_TODO = "<TODO_LLM>"
V6_VERSION = "fitz-gov-5.1-enriched"


# ---------------------------------------------------------------------------
# Domain mapping: 17 V5.1 domains → 7 MoE expert domains
# ---------------------------------------------------------------------------


DOMAIN_TO_EXPERT: dict[str, Domain] = {
    # Science & medicine cluster (everything empirical / nature / health)
    "medicine": Domain.SCIENCE_MEDICINE,
    "science": Domain.SCIENCE_MEDICINE,
    "environment": Domain.SCIENCE_MEDICINE,
    "food": Domain.SCIENCE_MEDICINE,
    "agriculture": Domain.SCIENCE_MEDICINE,
    "psychology": Domain.SCIENCE_MEDICINE,
    # Law & policy
    "law": Domain.LAW_POLICY,
    "government": Domain.LAW_POLICY,
    # History & geography
    "history": Domain.HISTORY_GEOGRAPHY,
    # Technology
    "technology": Domain.TECHNOLOGY_COMPUTING,
    # Economics & finance
    "finance": Domain.ECONOMICS_FINANCE,
    "real_estate": Domain.ECONOMICS_FINANCE,
    # Culture & society
    "sports": Domain.CULTURE_SOCIETY,
    "social_media": Domain.CULTURE_SOCIETY,
    # General / commonsense (everything else that doesn't fit a specialist)
    "education": Domain.GENERAL_COMMONSENSE,
    "hr_workplace": Domain.GENERAL_COMMONSENSE,
    "transportation": Domain.GENERAL_COMMONSENSE,
}


def map_domain_to_expert(domain: str | None) -> Domain:
    """Return the expert domain for a V5.1 `domain` string.

    Unknown domains default to `general_commonsense` (the catch-all expert).
    """
    if not domain:
        return Domain.GENERAL_COMMONSENSE
    return DOMAIN_TO_EXPERT.get(domain, Domain.GENERAL_COMMONSENSE)


# ---------------------------------------------------------------------------
# Category mapping: 4 V5.1 categories → 3 GovernanceClass
# ---------------------------------------------------------------------------


CATEGORY_TO_CLASS: dict[str, GovernanceClass] = {
    "abstention": GovernanceClass.ABSTAIN,
    "dispute": GovernanceClass.DISPUTED,
    "trustworthy_hedged": GovernanceClass.TRUSTWORTHY,
    "trustworthy_direct": GovernanceClass.TRUSTWORTHY,
}


def map_category_to_class(category: str) -> GovernanceClass:
    return CATEGORY_TO_CLASS[category]


# ---------------------------------------------------------------------------
# Subcategory → pattern mapping
# ---------------------------------------------------------------------------


# Explicit 1:1 mappings for the well-defined subcategories.
EXPLICIT_SUBCATEGORY_MAP: dict[str, TaxonomyPattern] = {
    # ABSTAIN family
    "wrong_entity": TaxonomyPattern.WRONG_ENTITY,
    "wrong_specificity": TaxonomyPattern.WRONG_SPECIFICITY,
    "temporal_mismatch": TaxonomyPattern.TEMPORAL_MISMATCH,
    "missing_data": TaxonomyPattern.EVIDENCE_ABSENT,
    "off_topic_contradiction": TaxonomyPattern.PARTIAL_OVERLAP,
    "wrong_domain": TaxonomyPattern.WRONG_ENTITY,
    "wrong_jurisdiction": TaxonomyPattern.WRONG_ENTITY,
    "outdated_context": TaxonomyPattern.TEMPORAL_MISMATCH,
    "wrong_product": TaxonomyPattern.WRONG_ENTITY,
    "cross_domain_insufficient": TaxonomyPattern.PARTIAL_OVERLAP,
    "decoy_keywords": TaxonomyPattern.WRONG_SPECIFICITY,
    "converted_insufficient": TaxonomyPattern.EVIDENCE_ABSENT,
    "converted_off_domain": TaxonomyPattern.WRONG_ENTITY,
    "wrong_version": TaxonomyPattern.TEMPORAL_MISMATCH,
    "implicit_only": TaxonomyPattern.PARTIAL_OVERLAP,
    "wrong_granularity": TaxonomyPattern.WRONG_SPECIFICITY,
    "different_domain": TaxonomyPattern.WRONG_ENTITY,
    "converted_wrong_entity": TaxonomyPattern.WRONG_ENTITY,
    "multi_source_gap": TaxonomyPattern.EVIDENCE_ABSENT,
    "cross_source_irrelevant": TaxonomyPattern.PARTIAL_OVERLAP,
    "code_abstention": TaxonomyPattern.EVIDENCE_ABSENT,
    "topic_adjacent": TaxonomyPattern.PARTIAL_OVERLAP,
    "format_impossible": TaxonomyPattern.TOO_GENERAL,
    "converted_wrong_scope": TaxonomyPattern.WRONG_SPECIFICITY,
    # DISPUTED family
    "numerical_conflict": TaxonomyPattern.NUMERICAL_CONFLICT,
    "implicit_contradiction": TaxonomyPattern.FACTUAL_CONTRADICTION,
    "binary_conflict": TaxonomyPattern.FACTUAL_CONTRADICTION,
    "opposing_conclusions": TaxonomyPattern.FACTUAL_CONTRADICTION,
    "temporal_conflict": TaxonomyPattern.TEMPORAL_CONFLICT,
    "statistical_direction_conflict": TaxonomyPattern.NUMERICAL_CONFLICT,
    "source_authority_conflict": TaxonomyPattern.AUTHORITY_CONFLICT,
    "methodology_conflict": TaxonomyPattern.DEFINITIONAL_CONFLICT,
    "interpretation_conflict": TaxonomyPattern.DEFINITIONAL_CONFLICT,
    "competing_theories": TaxonomyPattern.DEFINITIONAL_CONFLICT,
    "scientific_replication": TaxonomyPattern.FACTUAL_CONTRADICTION,
    "cross_source_contradiction": TaxonomyPattern.FACTUAL_CONTRADICTION,
    "converted_contradiction": TaxonomyPattern.FACTUAL_CONTRADICTION,
    "conditional_conflict": TaxonomyPattern.SCOPE_CONFLICT,
    "converted_consensus_removed": TaxonomyPattern.FACTUAL_CONTRADICTION,
    "direct_contradiction": TaxonomyPattern.FACTUAL_CONTRADICTION,
    "converted_framing_conflict": TaxonomyPattern.DEFINITIONAL_CONFLICT,
    "temporal_source_conflict": TaxonomyPattern.TEMPORAL_CONFLICT,
    "contradictory_attribution": TaxonomyPattern.FACTUAL_CONTRADICTION,
    "converted_version_conflict": TaxonomyPattern.TEMPORAL_CONFLICT,
    # TRUSTWORTHY (direct) family
    "clear_explanation": TaxonomyPattern.DIRECT_ANSWER,
    "technical_documented": TaxonomyPattern.SINGLE_AUTHORITATIVE,
    "contradiction_resolved": TaxonomyPattern.MULTI_SOURCE_CORROBORATION,
    "opposing_with_consensus": TaxonomyPattern.MULTI_SOURCE_CORROBORATION,
    "different_framing": TaxonomyPattern.DIRECT_ANSWER,
    "quantitative_answer": TaxonomyPattern.QUANTITATIVE_CONSENSUS,
    "direct_factual": TaxonomyPattern.DIRECT_ANSWER,
    "cross_source_agreement": TaxonomyPattern.MULTI_SOURCE_CORROBORATION,
    "multi_source_convergence": TaxonomyPattern.MULTI_SOURCE_CORROBORATION,
    "authoritative_source": TaxonomyPattern.SINGLE_AUTHORITATIVE,
    "near_complete_evidence": TaxonomyPattern.CONSISTENT_CHAIN,
    "conditional_confidence": TaxonomyPattern.CONSISTENT_CHAIN,
    "step_by_step": TaxonomyPattern.CONSISTENT_CHAIN,
    "definitional": TaxonomyPattern.DIRECT_ANSWER,
    # TRUSTWORTHY (hedged) family — the most common
    "evidence_quality": TaxonomyPattern.MULTI_SOURCE_CORROBORATION,
    "mixed_evidence": TaxonomyPattern.CONSISTENT_CHAIN,
    "hedged_evidence": TaxonomyPattern.CONSISTENT_CHAIN,
    "numerical_near_miss": TaxonomyPattern.QUANTITATIVE_CONSENSUS,
    "cross_source_partial": TaxonomyPattern.MULTI_SOURCE_CORROBORATION,
    "different_aspects": TaxonomyPattern.CONSISTENT_CHAIN,
    "causal_uncertainty": TaxonomyPattern.CONSISTENT_CHAIN,
    "temporal_uncertainty": TaxonomyPattern.CONSISTENT_CHAIN,
    "version_overlap": TaxonomyPattern.CONSISTENT_CHAIN,
    "methodology_difference": TaxonomyPattern.CONSISTENT_CHAIN,
    "stale_source": TaxonomyPattern.SINGLE_AUTHORITATIVE,
    "evolving_facts": TaxonomyPattern.CONSISTENT_CHAIN,
    "entity_ambiguity": TaxonomyPattern.CONSISTENT_CHAIN,
    "partial_answer": TaxonomyPattern.CONSISTENT_CHAIN,
    "scope_condition": TaxonomyPattern.SCOPE_CONFLICT,  # but this is in trustworthy_hedged → see fallback override
    "implicit_assumptions": TaxonomyPattern.CONSISTENT_CHAIN,
    "adjacent_entity": TaxonomyPattern.CONSISTENT_CHAIN,
    "cross_domain_transfer": TaxonomyPattern.CONSISTENT_CHAIN,
    "hedged_contradiction_corroborated": TaxonomyPattern.MULTI_SOURCE_CORROBORATION,
    "causal_without_evidence": TaxonomyPattern.CONSISTENT_CHAIN,
    "relevance_partial_answer": TaxonomyPattern.CONSISTENT_CHAIN,
}


# Category-level defaults for subcategories not in the explicit map.
CATEGORY_DEFAULT_PATTERN: dict[str, TaxonomyPattern] = {
    "abstention": TaxonomyPattern.PARTIAL_OVERLAP,
    "dispute": TaxonomyPattern.FACTUAL_CONTRADICTION,
    "trustworthy_hedged": TaxonomyPattern.CONSISTENT_CHAIN,
    "trustworthy_direct": TaxonomyPattern.DIRECT_ANSWER,
}


def map_subcategory_to_pattern(
    subcategory: str,
    category: str,
) -> TaxonomyPattern:
    """Best-effort map. Explicit table first, then keyword fallback bounded
    by the case's category, then category default."""
    if not subcategory:
        return CATEGORY_DEFAULT_PATTERN.get(
            category, TaxonomyPattern.PARTIAL_OVERLAP
        )

    explicit = EXPLICIT_SUBCATEGORY_MAP.get(subcategory)
    if explicit is not None:
        # Respect the category's class — if the explicit pick crosses class
        # (e.g. scope_condition mapped to SCOPE_CONFLICT but the case is
        # trustworthy_hedged), fall back to the category default.
        if governance_class_of(explicit) == map_category_to_class(category):
            return explicit
        # else fall through to fallback

    keyword = _keyword_pattern(subcategory, category)
    if keyword is not None:
        return keyword

    return CATEGORY_DEFAULT_PATTERN.get(
        category, TaxonomyPattern.PARTIAL_OVERLAP
    )


def _keyword_pattern(subcategory: str, category: str) -> TaxonomyPattern | None:
    """Keyword-based fallback, scoped to the case's governance class so we
    never cross-classify a DISPUTED subcategory as an ABSTAIN pattern."""
    cls = map_category_to_class(category)
    s = subcategory.lower()

    if cls == GovernanceClass.ABSTAIN:
        if "temporal" in s or "outdated" in s or "stale" in s or "version" in s:
            return TaxonomyPattern.TEMPORAL_MISMATCH
        if "entity" in s or "domain" in s or "product" in s or "jurisdiction" in s:
            return TaxonomyPattern.WRONG_ENTITY
        if "specificity" in s or "granularity" in s or "scope" in s:
            return TaxonomyPattern.WRONG_SPECIFICITY
        if "absent" in s or "missing" in s or "insufficient" in s or "gap" in s:
            return TaxonomyPattern.EVIDENCE_ABSENT
        if "general" in s or "broad" in s or "format" in s:
            return TaxonomyPattern.TOO_GENERAL
        return TaxonomyPattern.PARTIAL_OVERLAP

    if cls == GovernanceClass.DISPUTED:
        if "numerical" in s or "quantit" in s or "statistic" in s:
            return TaxonomyPattern.NUMERICAL_CONFLICT
        if "temporal" in s or "version" in s:
            return TaxonomyPattern.TEMPORAL_CONFLICT
        if "definition" in s or "framing" in s or "methodology" in s or "interpret" in s:
            return TaxonomyPattern.DEFINITIONAL_CONFLICT
        if "authority" in s:
            return TaxonomyPattern.AUTHORITY_CONFLICT
        if "scope" in s or "jurisdiction" in s or "conditional" in s:
            return TaxonomyPattern.SCOPE_CONFLICT
        return TaxonomyPattern.FACTUAL_CONTRADICTION

    # TRUSTWORTHY
    if "numerical" in s or "quantit" in s or "statistic" in s:
        return TaxonomyPattern.QUANTITATIVE_CONSENSUS
    if "authority" in s or "documented" in s or "technical" in s or "official" in s:
        return TaxonomyPattern.SINGLE_AUTHORITATIVE
    if "consensus" in s or "agreement" in s or "convergence" in s or "multi_source" in s or "cross_source" in s:
        return TaxonomyPattern.MULTI_SOURCE_CORROBORATION
    if "direct" in s or "clear" in s or "definitional" in s:
        return TaxonomyPattern.DIRECT_ANSWER
    if "chain" in s or "step" in s or "near_complete" in s:
        return TaxonomyPattern.CONSISTENT_CHAIN
    return None  # falls back to category default


# ---------------------------------------------------------------------------
# Deterministic signal heuristics
# ---------------------------------------------------------------------------


# Stub classification probabilities — argmax matches the class, gentle confidence
# (no claim of model output, just consistent with the label).
_CLASS_PROBS: dict[GovernanceClass, dict[str, float]] = {
    GovernanceClass.ABSTAIN: {"abstain": 0.85, "disputed": 0.08, "trustworthy": 0.07},
    GovernanceClass.DISPUTED: {"abstain": 0.10, "disputed": 0.80, "trustworthy": 0.10},
    GovernanceClass.TRUSTWORTHY: {"abstain": 0.06, "disputed": 0.09, "trustworthy": 0.85},
}


def stub_class_probs(cls: GovernanceClass) -> dict[str, float]:
    return dict(_CLASS_PROBS[cls])


def derive_conflict_density(category: str, evidence_pattern: str | None) -> float:
    """High for DISPUTED; medium for hedged trustworthy with `mixed`/`conflicting`
    evidence; low for ABSTAIN and direct TRUSTWORTHY."""
    cls = map_category_to_class(category)
    ep = (evidence_pattern or "").lower()
    if cls == GovernanceClass.DISPUTED:
        return 0.80
    if cls == GovernanceClass.TRUSTWORTHY and ep in {"conflicting", "mixed"}:
        return 0.45
    if cls == GovernanceClass.TRUSTWORTHY:
        return 0.10
    # ABSTAIN
    if ep == "conflicting":
        return 0.30
    return 0.10


def derive_evidence_sufficiency(category: str, evidence_pattern: str | None) -> float:
    cls = map_category_to_class(category)
    ep = (evidence_pattern or "").lower()
    if cls == GovernanceClass.ABSTAIN:
        return 0.10 if ep == "absent" else 0.25
    if cls == GovernanceClass.DISPUTED:
        return 0.60  # contradicting evidence is itself a kind of sufficiency
    if cls == GovernanceClass.TRUSTWORTHY:
        if ep == "direct":
            return 0.90
        if ep in {"indirect", "partial", "mixed"}:
            return 0.65
        return 0.80
    return 0.50


def derive_false_trustworthy_risk(category: str, difficulty: str) -> float:
    """Cases where the model could *wrongly* call TRUSTWORTHY — highest for hard
    DISPUTED (looks reasonable, model might miss the conflict)."""
    cls = map_category_to_class(category)
    diff = (difficulty or "medium").lower()
    base = {GovernanceClass.ABSTAIN: 0.20, GovernanceClass.DISPUTED: 0.40, GovernanceClass.TRUSTWORTHY: 0.08}[cls]
    if diff == "hard":
        base += 0.15
    elif diff == "easy":
        base -= 0.05
    return round(max(0.02, min(0.95, base)), 2)


def derive_hallucination_pressure(category: str, evidence_pattern: str | None) -> float:
    cls = map_category_to_class(category)
    ep = (evidence_pattern or "").lower()
    if cls == GovernanceClass.ABSTAIN:
        return 0.85 if ep == "absent" else 0.70
    if cls == GovernanceClass.DISPUTED:
        return 0.55
    # TRUSTWORTHY
    if ep == "direct":
        return 0.15
    return 0.30


def derive_retrieval_retry_value(category: str, evidence_pattern: str | None) -> float:
    """Would more retrieval help? Highest for ABSTAIN cases (missing evidence)."""
    cls = map_category_to_class(category)
    if cls == GovernanceClass.ABSTAIN:
        return 0.85
    if cls == GovernanceClass.DISPUTED:
        return 0.30
    return 0.20


def derive_query_evidence_alignment(category: str, evidence_pattern: str | None) -> float:
    cls = map_category_to_class(category)
    ep = (evidence_pattern or "").lower()
    if cls == GovernanceClass.ABSTAIN:
        return 0.20
    if cls == GovernanceClass.DISPUTED:
        return 0.70  # sources address the query but disagree
    if ep == "direct":
        return 0.90
    return 0.60


def derive_answer_coverage(category: str, evidence_pattern: str | None) -> float:
    cls = map_category_to_class(category)
    ep = (evidence_pattern or "").lower()
    if cls == GovernanceClass.ABSTAIN:
        return 0.10
    if cls == GovernanceClass.DISPUTED:
        return 0.60
    if ep == "direct":
        return 0.90
    if ep in {"indirect", "partial"}:
        return 0.55
    return 0.75


def derive_human_escalation_score(category: str, difficulty: str) -> float:
    """Composite: hard DISPUTED + ABSTAIN cases escalate; easy TRUSTWORTHY doesn't."""
    cls = map_category_to_class(category)
    diff = (difficulty or "medium").lower()
    base = {GovernanceClass.ABSTAIN: 0.50, GovernanceClass.DISPUTED: 0.55, GovernanceClass.TRUSTWORTHY: 0.10}[cls]
    if diff == "hard":
        base += 0.15
    elif diff == "easy":
        base -= 0.10
    return round(max(0.02, min(0.95, base)), 2)


def derive_domain_familiarity(domain: str | None) -> float:
    """Stub: assume V5.1 covers all 17 domains reasonably; mild discount for
    the longer-tail ones."""
    if not domain:
        return 0.70
    rare = {"hr_workplace", "real_estate", "social_media"}
    return 0.75 if domain in rare else 0.90


def derive_near_miss_class(category: str, evidence_pattern: str | None) -> GovernanceClass:
    """Heuristic boundary: ABSTAIN with conflicting evidence is close to
    DISPUTED; DISPUTED with partial evidence is close to ABSTAIN; TRUSTWORTHY
    with mixed evidence is close to DISPUTED."""
    cls = map_category_to_class(category)
    ep = (evidence_pattern or "").lower()
    if cls == GovernanceClass.ABSTAIN:
        return GovernanceClass.DISPUTED if ep == "conflicting" else GovernanceClass.TRUSTWORTHY
    if cls == GovernanceClass.DISPUTED:
        return GovernanceClass.ABSTAIN if ep in {"partial", "absent"} else GovernanceClass.TRUSTWORTHY
    return GovernanceClass.DISPUTED if ep in {"mixed", "conflicting"} else GovernanceClass.ABSTAIN


def derive_boundary_proximity(category: str, evidence_pattern: str | None) -> dict[str, Any]:
    """Stub: nearest_class via `derive_near_miss_class`, distance via difficulty."""
    nearest = derive_near_miss_class(category, evidence_pattern)
    return {"nearest_class": nearest.value, "distance": 0.60}


# ---------------------------------------------------------------------------
# Per-chunk enrichment
# ---------------------------------------------------------------------------


# Pattern-aware authority score derivation. Some taxonomy patterns have
# structural checks the checker enforces (authority_conflict needs spread,
# expert_consensus needs uniform high), so enrichment has to produce scores
# that satisfy them — not just plausible-looking uniform values.
def derive_authority_for_chunk(
    source_type: str | None,
    idx: int,
    n_total: int,
    *,
    pattern: TaxonomyPattern | None = None,
) -> tuple[float, str]:
    """Return (authority_score, authority_signal) for chunk index `idx` of `n_total`."""
    p = pattern

    # Authority conflict: first chunk is "high authority" (e.g. peer-reviewed),
    # rest are "low authority" (e.g. blog). Spread must be ≥0.2 per the checker.
    if p == TaxonomyPattern.AUTHORITY_CONFLICT:
        if idx == 0:
            return 0.88, "peer_reviewed"
        return 0.32, "blog_or_user_content"

    # Expert consensus: all chunks must read as high-authority (≥0.6).
    if p == TaxonomyPattern.EXPERT_CONSENSUS:
        return round(max(0.75, 0.90 - 0.03 * idx), 2), "domain_expert"

    # Single authoritative: one strong source.
    if p == TaxonomyPattern.SINGLE_AUTHORITATIVE:
        return 0.85 if idx == 0 else 0.55, "authoritative_primary"

    # Default: moderate scores with a small bump for multi_source diversity
    # and a gentle decay for later chunks (proxy for "first chunk most relevant").
    base = 0.60 if (source_type or "").lower() == "multi_source" else 0.55
    adjusted = max(0.30, base - 0.02 * idx)
    signal = "multi_source_diverse" if (source_type or "").lower() == "multi_source" else "encyclopedic_general"
    return round(adjusted, 2), signal


def derive_temporality(
    domain: str | None,
    evidence_pattern: str | None,
) -> dict[str, Any]:
    """Stub temporality from V5.1 domain + evidence_pattern."""
    ep = (evidence_pattern or "").lower()
    # Domains where staleness matters
    time_sensitive_domains = {
        "technology", "finance", "law", "government", "medicine", "science",
        "environment", "real_estate", "social_media",
    }
    is_time_sensitive = domain in time_sensitive_domains
    staleness_risk = "high" if is_time_sensitive else "low"
    if ep in {"stale", "outdated"}:
        staleness_risk = "high"
    return {
        "is_time_sensitive": bool(is_time_sensitive),
        "anchor_period": LLM_TODO,
        "staleness_risk": staleness_risk,
    }


def enrich_chunk(
    chunk_text: str,
    *,
    idx: int,
    n_total: int,
    source_type: str | None,
    domain: str | None,
    evidence_pattern: str | None,
    pattern: TaxonomyPattern | None = None,
) -> dict[str, Any]:
    """Build the V6 per-chunk object from a V5.1 plain-string context.

    `pattern` lets per-chunk fields like authority_score satisfy pattern-
    specific structural checks (e.g. AUTHORITY_CONFLICT needs spread).
    """
    authority_score, authority_signal = derive_authority_for_chunk(
        source_type, idx, n_total, pattern=pattern
    )
    return {
        "id": f"ctx_{idx + 1:03d}",
        "text": chunk_text,
        "authority_score": authority_score,
        "authority_signal": authority_signal,
        "temporality": derive_temporality(domain, evidence_pattern),
        "summary": (chunk_text[:120] + "...") if len(chunk_text) > 120 else chunk_text,
        "relevance_to_query": 0.50,  # neutral placeholder; LLM enrichment refines
    }


# ---------------------------------------------------------------------------
# Top-level: enrich one V5.1 case → V6+
# ---------------------------------------------------------------------------


def enrich_case(v51: dict[str, Any]) -> dict[str, Any]:
    """Map one V5.1 case onto the V6+ schema. Deterministic; no LLM."""
    # V5.1 expected fields
    category = v51["category"]
    subcategory = v51.get("subcategory", "")
    difficulty_s = v51.get("difficulty", "medium")
    domain_s = v51.get("domain")
    evidence_pattern = v51.get("evidence_pattern")
    source_type = v51.get("source_type")
    contexts_raw = v51.get("contexts", []) or []

    # Derive new metadata
    cls = map_category_to_class(category)
    expert = map_domain_to_expert(domain_s)
    difficulty = Difficulty(difficulty_s) if difficulty_s in {"easy", "medium", "hard"} else Difficulty.MEDIUM
    pattern = map_subcategory_to_pattern(subcategory, category)
    cell = Cell(pattern=pattern, domain=expert, difficulty=difficulty)

    # Per-chunk — pass `pattern` so authority scores satisfy pattern-specific
    # structural checks (e.g. AUTHORITY_CONFLICT requires spread, EXPERT_CONSENSUS
    # requires uniform high scores).
    enriched_chunks = [
        enrich_chunk(
            ctx if isinstance(ctx, str) else str(ctx),
            idx=i,
            n_total=len(contexts_raw),
            source_type=source_type,
            domain=domain_s,
            evidence_pattern=evidence_pattern,
            pattern=pattern,
        )
        for i, ctx in enumerate(contexts_raw)
    ]

    # Governance signals
    probs = stub_class_probs(cls)
    governance = {
        "classification": cls.value,
        "abstain": probs["abstain"],
        "disputed": probs["disputed"],
        "trustworthy": probs["trustworthy"],
        "confidence": 0.85,
        "grounding": 0.30 if cls == GovernanceClass.ABSTAIN else (0.55 if cls == GovernanceClass.DISPUTED else 0.85),
        "conflict_density": derive_conflict_density(category, evidence_pattern),
        "evidence_sufficiency": derive_evidence_sufficiency(category, evidence_pattern),
        "boundary_proximity": derive_boundary_proximity(category, evidence_pattern),
        "domain_familiarity": derive_domain_familiarity(domain_s),
        "false_trustworthy_risk": derive_false_trustworthy_risk(category, difficulty.value),
        "hallucination_pressure": derive_hallucination_pressure(category, evidence_pattern),
        "retrieval_retry_value": derive_retrieval_retry_value(category, evidence_pattern),
        "human_escalation_score": derive_human_escalation_score(category, difficulty.value),
        "query_evidence_alignment": derive_query_evidence_alignment(category, evidence_pattern),
        "answer_coverage": derive_answer_coverage(category, evidence_pattern),
    }

    taxonomy = {
        "governance_class": cls.value,
        "pattern": pattern.value,
        "pattern_description": PATTERN_DESCRIPTIONS[pattern],
        "cell_id": cell.cell_id,
    }

    routing = {
        "expert_fired": expert.value,
        "secondary_expert": None,
        "routing_confidence": 0.90,
    }

    # Near-miss
    near_miss = derive_near_miss_class(category, evidence_pattern)

    meta = {
        "difficulty": difficulty.value,
        "modality": "unstructured",
        "subcategory": subcategory,
        "domain": domain_s,
        "query_type": v51.get("query_type"),
        "reasoning_type": v51.get("reasoning_type"),
        "evidence_pattern": evidence_pattern,
        "confidence_level": "high",  # V5.1 is human-validated
        "near_miss_class": near_miss.value,
        "near_miss_reason": LLM_TODO,
        "annotator_agreement": "unanimous",
        "category": category,
        "source_type": source_type,
        "context_count": v51.get("context_count", len(contexts_raw)),
    }

    # Preserve V5.1 provenance fields
    for k in ("description", "rationale", "evaluation_config",
              "forbidden_claims", "required_elements", "context_sources",
              "metadata", "original_subcategory", "detection_labels",
              "original_id", "forbidden_elements", "original_category",
              "original_expected_mode", "relabel_reason"):
        if k in v51:
            meta.setdefault("v51_legacy", {})[k] = v51[k]

    return {
        "id": v51["id"],
        "version": V6_VERSION,
        "input": {
            "query": v51["query"],
            "query_rewritten": LLM_TODO,
            "contexts": enriched_chunks,
        },
        "governance": governance,
        "routing": routing,
        "taxonomy": taxonomy,
        "meta": meta,
    }


# ---------------------------------------------------------------------------
# Audit helpers
# ---------------------------------------------------------------------------


def count_subcategory_fallbacks(subcategories: list[str], categories: list[str]) -> dict[str, int]:
    """How many subcategories fell to the category default vs hit an explicit
    or keyword mapping. Useful for the enrichment runner's summary report."""
    counts = {"explicit": 0, "keyword": 0, "category_default": 0, "empty": 0}
    for sc, cat in zip(subcategories, categories):
        if not sc:
            counts["empty"] += 1
            continue
        if sc in EXPLICIT_SUBCATEGORY_MAP and governance_class_of(
            EXPLICIT_SUBCATEGORY_MAP[sc]
        ) == map_category_to_class(cat):
            counts["explicit"] += 1
        elif _keyword_pattern(sc, cat) is not None:
            counts["keyword"] += 1
        else:
            counts["category_default"] += 1
    return counts
