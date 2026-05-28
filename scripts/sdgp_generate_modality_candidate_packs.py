"""Generate candidate SDGP V8 rows for structured-data and code modalities.

Produces two isolated candidate workspaces:

    data/_workspaces/handoff/modality_structured_v1_20260527/
    data/_workspaces/handoff/modality_code_v1_20260527/

Each workspace contains 10,000 SDGP-shaped candidate rows that follow the current
V8 row contract (no taxonomy shims, no compat fields). The rows are not merged
into the active vault, not published to Hugging Face, and IDs are namespaced as
``sdgp_v8_modality_<modality>_<NNNNN>`` so they cannot collide with existing
canonical or modality-probe IDs.

Run from repo root::

    python scripts/sdgp_generate_modality_candidate_packs.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

from fitz_gov.sdgp.taxonomy import PATTERN_DESCRIPTIONS, TaxonomyPattern


VERSION = "fitz-gov-modality-candidate-0.1"
DATASET_VERSION = "v8"
PROVIDER = "claude-code"
PROVIDER_VERSION = "claude-opus-4-7"
PROMPT_VERSION = "modality-candidate-0.1"
BUILD_TS = "2026-05-27T22:09:50Z"

OUT_ROOT = Path("data/_workspaces/handoff")
STRUCTURED_WORKSPACE = OUT_ROOT / "modality_structured_v1_20260527"
CODE_WORKSPACE = OUT_ROOT / "modality_code_v1_20260527"

BATCH_SIZE = 60  # 167 batches per modality (10,000 / 60, last batch partial)

DIFFICULTY_CYCLE = ["easy", "medium", "hard"]

STRUCTURED_DOMAINS = [
    "economics_finance",
    "technology_computing",
    "science_medicine",
    "law_policy",
    "history_geography",
    "culture_society",
    "general_commonsense",
]
CODE_DOMAINS = [
    "technology_computing",
    "technology_computing",
    "technology_computing",
    "technology_computing",
    "technology_computing",
    "economics_finance",
    "science_medicine",
]


# ---------------------------------------------------------------------------
# Pattern -> class map (verified against data/fitz-gov/cases.jsonl)
# ---------------------------------------------------------------------------
PATTERN_CLASS: dict[str, str] = {
    "direct_answer": "TRUSTWORTHY",
    "single_authoritative": "TRUSTWORTHY",
    "consistent_chain": "TRUSTWORTHY",
    "quantitative_consensus": "TRUSTWORTHY",
    "multi_source_corroboration": "TRUSTWORTHY",
    "expert_consensus": "TRUSTWORTHY",
    "resolved_candidate_selection": "TRUSTWORTHY",
    "factual_contradiction": "DISPUTED",
    "numerical_conflict": "DISPUTED",
    "scope_conflict": "DISPUTED",
    "verdict_conflict": "DISPUTED",
    "authority_status_conflict": "DISPUTED",
    "definitional_conflict": "DISPUTED",
    "authority_conflict": "DISPUTED",
    "temporal_conflict": "DISPUTED",
    "evidence_absent": "ABSTAIN",
    "missing_execution_result": "ABSTAIN",
    "partial_overlap": "ABSTAIN",
    "version_build_mismatch": "ABSTAIN",
    "wrong_entity": "ABSTAIN",
    "wrong_specificity": "ABSTAIN",
    "temporal_mismatch": "ABSTAIN",
    "too_general": "ABSTAIN",
}

ALLOWED_PATTERNS = set(PATTERN_CLASS)


# ---------------------------------------------------------------------------
# Score templates (coherent governance scalars per class)
# ---------------------------------------------------------------------------
def scores_for(cls: str, difficulty: str) -> dict[str, Any]:
    base_easy = {"confidence_bonus": 0.04, "grounding_bonus": 0.04}
    bonus = base_easy if difficulty == "easy" else {"confidence_bonus": 0.0, "grounding_bonus": 0.0}
    if cls == "TRUSTWORTHY":
        return {
            "abstain": 0.05,
            "disputed": 0.08,
            "trustworthy": 0.87,
            "confidence": round(0.83 + bonus["confidence_bonus"], 2),
            "grounding": round(0.86 + bonus["grounding_bonus"], 2),
            "conflict_density": 0.10,
            "evidence_sufficiency": 0.88,
            "nearest_class": "ABSTAIN" if difficulty != "easy" else "DISPUTED",
            "distance": 0.78,
            "domain_familiarity": 0.82,
            "false_trustworthy_risk": 0.08,
            "hallucination_pressure": 0.10,
            "retrieval_retry_value": 0.16,
            "human_escalation_score": 0.14,
            "query_evidence_alignment": 0.9,
            "answer_coverage": 0.88,
            "evidence_bias_score": 0.14,
        }
    if cls == "DISPUTED":
        return {
            "abstain": 0.08,
            "disputed": 0.83,
            "trustworthy": 0.09,
            "confidence": 0.83,
            "grounding": 0.64,
            "conflict_density": 0.82,
            "evidence_sufficiency": 0.58,
            "nearest_class": "TRUSTWORTHY",
            "distance": 0.74,
            "domain_familiarity": 0.8,
            "false_trustworthy_risk": 0.6,
            "hallucination_pressure": 0.34,
            "retrieval_retry_value": 0.5,
            "human_escalation_score": 0.72,
            "query_evidence_alignment": 0.84,
            "answer_coverage": 0.56,
            "evidence_bias_score": 0.4,
        }
    return {
        "abstain": 0.84,
        "disputed": 0.08,
        "trustworthy": 0.08,
        "confidence": 0.84,
        "grounding": 0.42,
        "conflict_density": 0.12,
        "evidence_sufficiency": 0.2,
        "nearest_class": "TRUSTWORTHY",
        "distance": 0.76,
        "domain_familiarity": 0.78,
        "false_trustworthy_risk": 0.62,
        "hallucination_pressure": 0.74,
        "retrieval_retry_value": 0.82,
        "human_escalation_score": 0.54,
        "query_evidence_alignment": 0.34,
        "answer_coverage": 0.16,
        "evidence_bias_score": 0.22,
    }


def _category(cls: str, *, direct: bool = False) -> str:
    if cls == "TRUSTWORTHY":
        return "trustworthy_direct" if direct else "trustworthy_hedged"
    if cls == "DISPUTED":
        return "dispute"
    return "abstention"


def _make_context(
    idx: int,
    text: str,
    *,
    authority_score: float,
    authority_signal: str,
    summary: str,
    relevance: float = 0.9,
    boundary: float = 0.85,
    anchor: str = "modality candidate seed",
    stale: str = "low",
    time_sensitive: bool = True,
) -> dict[str, Any]:
    return {
        "id": f"ctx_{idx:03d}",
        "text": text,
        "authority_score": authority_score,
        "authority_signal": authority_signal,
        "temporality": {
            "is_time_sensitive": time_sensitive,
            "anchor_period": anchor,
            "staleness_risk": stale,
        },
        "summary": summary,
        "relevance_to_query": relevance,
        "boundary_quality": boundary,
    }


@dataclass
class Spec:
    """A single (label, mechanism, pattern) plan to fill with N rows."""

    label: str
    mechanism: str
    pattern: str
    serialization: str  # for structured: markdown/csv/key_value/sql_grid/dashboard/schema/etl
    count: int
    builder: Callable[["RowCtx"], dict[str, Any]]


@dataclass
class RowCtx:
    """Per-row deterministic context passed to a builder."""

    seq: int  # 0..count-1 within mechanism
    domain: str
    difficulty: str
    serialization: str
    label: str
    mechanism: str
    pattern: str


# ---------------------------------------------------------------------------
# Row assembly
# ---------------------------------------------------------------------------
def build_row(
    *,
    modality: str,
    case_id: str,
    pattern: str,
    domain: str,
    difficulty: str,
    query: str,
    query_rewritten: str | None,
    contexts: list[dict[str, Any]],
    required_elements: list[str],
    forbidden_claims: list[str],
    forbidden_elements: list[str],
    near_miss_reason: str,
    mechanism: str,
    serialization: str | None,
    gold_answer: str | None = None,
    grounding_attributions: list[str] | None = None,
    direct: bool = False,
    evidence_chain_reason: str | None = None,
) -> dict[str, Any]:
    cls = PATTERN_CLASS[pattern]
    sc = scores_for(cls, difficulty)
    row: dict[str, Any] = {
        "id": case_id,
        "version": VERSION,
        "input": {
            "query": query,
            "query_rewritten": query_rewritten or query,
            "contexts": contexts,
        },
        "governance": {
            "classification": cls,
            "abstain": sc["abstain"],
            "disputed": sc["disputed"],
            "trustworthy": sc["trustworthy"],
            "confidence": sc["confidence"],
            "grounding": sc["grounding"],
            "conflict_density": sc["conflict_density"],
            "evidence_sufficiency": sc["evidence_sufficiency"],
            "boundary_proximity": {
                "nearest_class": sc["nearest_class"],
                "distance": sc["distance"],
            },
            "domain_familiarity": sc["domain_familiarity"],
            "false_trustworthy_risk": sc["false_trustworthy_risk"],
            "hallucination_pressure": sc["hallucination_pressure"],
            "retrieval_retry_value": sc["retrieval_retry_value"],
            "human_escalation_score": sc["human_escalation_score"],
            "query_evidence_alignment": sc["query_evidence_alignment"],
            "answer_coverage": sc["answer_coverage"],
            "evidence_bias_score": sc["evidence_bias_score"],
        },
        "taxonomy": {
            "governance_class": cls,
            "pattern": pattern,
            "pattern_description": PATTERN_DESCRIPTIONS[TaxonomyPattern(pattern)],
            "cell_id": f"{pattern}__{domain}__{difficulty}",
        },
        "evaluation": {
            "mode": "governance",
            "check_mode_match": True,
            "required_elements": required_elements,
            "forbidden_claims": forbidden_claims,
            "forbidden_elements": forbidden_elements,
        },
        "routing": {
            "expert_fired": domain,
            "secondary_expert": "conflict_detection" if cls == "DISPUTED" else None,
            "routing_confidence": 0.88,
        },
        "meta": {
            "dataset_version": DATASET_VERSION,
            "modality": modality,
            "difficulty": difficulty,
            "category": _category(cls, direct=direct),
            "confidence_level": "high" if difficulty == "easy" else "medium",
            "near_miss_class": sc["nearest_class"],
            "near_miss_reason": near_miss_reason,
            "mechanism": mechanism,
        },
        "_vault": {
            "added_at": BUILD_TS,
            "provider": PROVIDER,
            "provider_version": PROVIDER_VERSION,
            "prompt_version": PROMPT_VERSION,
            "batch_id": f"{modality}_candidate_v1",
            "last_modified_at": BUILD_TS,
            "revisions": 1,
        },
    }
    if serialization is not None:
        row["meta"]["serialization"] = serialization
    if len(contexts) >= 2:
        row["input"]["evidence_chain"] = {
            "order": [c["id"] for c in contexts],
            "reasoning": evidence_chain_reason
            or "Read the retrieved records together because the governance decision depends on whether they answer, conflict, or omit the requested fact.",
        }
    if cls == "TRUSTWORTHY":
        attribs = grounding_attributions or [contexts[0]["id"]]
        answer = gold_answer or (required_elements[0] if required_elements else "(see contexts)")
        row["meta"]["grounding_targets"] = {
            "gold_answer": answer,
            "sentences": [{"text": answer, "attributions": attribs}],
        }
    return row


# ---------------------------------------------------------------------------
# Structured-modality builders
# ---------------------------------------------------------------------------
STRUCTURED_DOMAIN_FLAVOR = {
    "economics_finance": {
        "entity_name": "warehouse",
        "prefix": "WH",
        "metric": "returns",
        "metrics": ["returns", "net_revenue", "refunds", "units_shipped", "chargebacks"],
        "id_field": "warehouse_id",
        "table": "warehouse_returns",
        "schema_field": "balance_usd",
        "region_field": "region",
    },
    "technology_computing": {
        "entity_name": "service",
        "prefix": "svc",
        "metric": "p95_latency_ms",
        "metrics": ["p95_latency_ms", "error_rate_ppm", "requests_total", "p99_latency_ms", "saturation_pct"],
        "id_field": "service",
        "table": "service_metrics",
        "schema_field": "latency_ms",
        "region_field": "cluster",
    },
    "science_medicine": {
        "entity_name": "cohort",
        "prefix": "Cohort",
        "metric": "completion_rate",
        "metrics": ["completion_rate", "enrollment_count", "adverse_events", "dropout_rate", "adherence_pct"],
        "id_field": "cohort_id",
        "table": "trial_cohort_summary",
        "schema_field": "completion_pct",
        "region_field": "site",
    },
    "law_policy": {
        "entity_name": "case",
        "prefix": "Case-2025",
        "metric": "filings_count",
        "metrics": ["filings_count", "motions_count", "exhibits_count", "hearings_count", "rulings_count"],
        "id_field": "case_id",
        "table": "docket_filings_q",
        "schema_field": "filings_count",
        "region_field": "jurisdiction",
    },
    "history_geography": {
        "entity_name": "region",
        "prefix": "Region",
        "metric": "population_2025",
        "metrics": ["population_2025", "land_area_km2", "settlements_count", "households", "migration_net"],
        "id_field": "region_name",
        "table": "regional_census_2025",
        "schema_field": "population",
        "region_field": "province",
    },
    "culture_society": {
        "entity_name": "venue",
        "prefix": "Venue",
        "metric": "event_count",
        "metrics": ["event_count", "attendance_total", "bookings_count", "cancellations", "members_count"],
        "id_field": "venue_id",
        "table": "venue_events_q",
        "schema_field": "event_count",
        "region_field": "district",
    },
    "general_commonsense": {
        "entity_name": "store",
        "prefix": "Store",
        "metric": "tickets_open",
        "metrics": ["tickets_open", "orders_count", "returns_count", "footfall", "reviews_count"],
        "id_field": "store_id",
        "table": "support_tickets_daily",
        "schema_field": "tickets_open",
        "region_field": "territory",
    },
}

# --- Structured diversity helpers -------------------------------------------
# Programmatic pools sized far above any per-builder row count so identifiers do
# not repeat within a mechanism. seq is unique within a (label, mechanism), so
# threading it through these helpers yields unique queries/contexts per row.
_PERIODS = [
    f"{y}-{m:02d}"
    for y in (2024, 2025, 2026)
    for m in range(1, 13)
] + [f"{y}-Q{q}" for y in (2024, 2025, 2026) for q in range(1, 5)]
_REGIONS = [
    "EMEA", "AMER", "APAC", "LATAM", "ANZ", "MENA", "Nordics", "DACH",
    "Iberia", "Benelux", "GreaterChina", "SoutheastAsia", "EastAfrica", "WestAfrica",
]


def _entity(flv: dict[str, Any], idx: int) -> str:
    return f"{flv['prefix']}-{idx % 100000:04d}"


def _metric(flv: dict[str, Any], idx: int) -> str:
    return flv["metrics"][idx % len(flv["metrics"])]


def _period(idx: int) -> str:
    return _PERIODS[idx % len(_PERIODS)]


def _region_val(idx: int, *, skip: str | None = None) -> str:
    pool = [r for r in _REGIONS if r != skip]
    return pool[idx % len(pool)]


def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    head = " | ".join(headers)
    sep = " | ".join(["---"] * len(headers))
    body = "\n".join(" | ".join(r) for r in rows)
    return f"{head}\n{sep}\n{body}"


def _csv_block(headers: list[str], rows: list[list[str]]) -> str:
    out = [",".join(headers)]
    for r in rows:
        out.append(",".join(r))
    return "\n".join(out)


def _kv_block(rows: list[list[str]]) -> str:
    return "; ".join(f"{k}={v}" for r in rows for k, v in [r])


def _serialize_table(serialization: str, table_name: str, headers: list[str], rows: list[list[str]]) -> str:
    if serialization == "markdown":
        return f"{table_name} (markdown):\n" + _md_table(headers, rows)
    if serialization == "csv":
        return f"{table_name}.csv\n" + _csv_block(headers, rows)
    if serialization == "key_value":
        return f"{table_name} key-value evidence packet: " + "; ".join(
            f"row_{i+1}: " + ", ".join(f"{h}={v}" for h, v in zip(headers, r))
            for i, r in enumerate(rows)
        )
    if serialization == "sql_grid":
        head = " | ".join(headers)
        body = "\n".join(" | ".join(r) for r in rows)
        return f"SQL result grid for {table_name}:\n{head}\n{body}"
    if serialization == "dashboard":
        return f"Dashboard export ({table_name}): " + "; ".join(
            ", ".join(f"{h}: {v}" for h, v in zip(headers, r)) for r in rows
        )
    if serialization == "schema":
        cols = ", ".join(headers)
        sample = "\n".join("  " + " | ".join(r) for r in rows)
        return f"Database schema for {table_name}: columns ({cols}). Sample rows:\n{sample}"
    if serialization == "etl_status":
        head = " | ".join(headers)
        body = "\n".join(" | ".join(r) for r in rows)
        return f"ETL/job status table {table_name}:\n{head}\n{body}"
    return _md_table(headers, rows)


# --- Structured TRUSTWORTHY builders -----------------------------------------
def b_struct_t_exact_row(ctx: RowCtx) -> dict[str, Any]:
    flv = STRUCTURED_DOMAIN_FLAVOR[ctx.domain]
    target = _entity(flv, ctx.seq)
    other_a = _entity(flv, ctx.seq + 31)
    other_b = _entity(flv, ctx.seq + 62)
    value = 100 + (ctx.seq * 7) % 900
    headers = [flv["id_field"], flv["metric"]]
    rows = [
        [target, str(value)],
        [other_a, str(value - 23)],
        [other_b, str(value + 17)],
    ]
    table_block = _serialize_table(ctx.serialization, f"q4_{flv['table']}", headers, rows)
    q = f"Which {flv['entity_name']} recorded exactly {value} {flv['metric']} in the Q4 {flv['table']} table?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(
                1,
                table_block,
                authority_score=0.93,
                authority_signal=f"{flv['table']}_export",
                summary=f"The Q4 table directly maps {value} {flv['metric']} to {target}.",
                relevance=0.92,
                boundary=0.88,
                anchor="2026-Q4",
            )
        ],
        required_elements=[target],
        forbidden_claims=[f"{other_a} recorded {value} {flv['metric']}", f"{other_b} recorded {value} {flv['metric']}"],
        forbidden_elements=[],
        near_miss_reason="A model could pick an adjacent row instead of matching the exact value.",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
        gold_answer=f"{target} recorded {value} {flv['metric']}.",
        direct=True,
    )


def b_struct_t_aggregate(ctx: RowCtx) -> dict[str, Any]:
    flv = STRUCTURED_DOMAIN_FLAVOR[ctx.domain]
    total = 1200 + (ctx.seq * 31) % 8000
    period = _period(ctx.seq)
    headers = ["period", "metric", "value"]
    rows = [[period, f"total_{flv['metric']}", str(total)]]
    blob = _serialize_table(ctx.serialization, f"agg_{flv['table']}", headers, rows)
    q = f"What was the total {flv['metric']} in {period}?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(
                1,
                blob,
                authority_score=0.92,
                authority_signal="warehouse_aggregate",
                summary=f"The aggregate row reports total {flv['metric']} for {period} as {total}.",
                anchor=period,
            )
        ],
        required_elements=[str(total)],
        forbidden_claims=[f"total {flv['metric']} was {total + 100}", f"total {flv['metric']} was {total - 100}"],
        forbidden_elements=[],
        near_miss_reason="A model might invent a per-row breakdown instead of citing the published total.",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
        gold_answer=f"The total {flv['metric']} in {period} was {total}.",
    )


def b_struct_t_join(ctx: RowCtx) -> dict[str, Any]:
    flv = STRUCTURED_DOMAIN_FLAVOR[ctx.domain]
    target = _entity(flv, ctx.seq)
    plan_id = f"plan-{ctx.seq:04d}"
    value = 200 + (ctx.seq * 11) % 700
    a = _serialize_table(
        ctx.serialization,
        f"{flv['table']}_plans",
        [flv["id_field"], "plan_id"],
        [[target, plan_id]],
    )
    b = _serialize_table(
        ctx.serialization,
        f"{flv['table']}_results",
        ["plan_id", flv["metric"]],
        [[plan_id, str(value)]],
    )
    q = f"What {flv['metric']} did {target} report in the joined plan/result tables?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(
                1, a, authority_score=0.88, authority_signal=f"{flv['table']}_plans_export",
                summary=f"Plans table maps {target} to {plan_id}.",
            ),
            _make_context(
                2, b, authority_score=0.91, authority_signal=f"{flv['table']}_results_export",
                summary=f"Results table maps {plan_id} to {value}.",
            ),
        ],
        required_elements=[str(value)],
        forbidden_claims=[f"{target} reported {value + 50}", f"{target} reported {value - 50}"],
        forbidden_elements=[],
        near_miss_reason="The answer requires joining plan id to result row, not reading either alone.",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
        gold_answer=f"{target} reported {value} {flv['metric']} after joining the plan and result tables.",
        grounding_attributions=["ctx_001", "ctx_002"],
        evidence_chain_reason="Join the plan and result rows on plan_id to resolve the metric for the requested entity.",
    )


def b_struct_t_threshold(ctx: RowCtx) -> dict[str, Any]:
    flv = STRUCTURED_DOMAIN_FLAVOR[ctx.domain]
    target = _entity(flv, ctx.seq)
    value = 200 + (ctx.seq * 11) % 700
    threshold = value - 25
    a = _serialize_table(
        ctx.serialization,
        f"{flv['table']}_metric",
        [flv["id_field"], flv["metric"]],
        [[target, str(value)]],
    )
    b = _serialize_table(
        ctx.serialization,
        f"{flv['table']}_thresholds",
        [flv["id_field"], "threshold"],
        [[target, str(threshold)]],
    )
    q = f"Did {target} exceed the published {flv['metric']} threshold this quarter?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(
                1, a, authority_score=0.92, authority_signal=f"{flv['table']}_metric",
                summary=f"{target} value is {value}.",
            ),
            _make_context(
                2, b, authority_score=0.9, authority_signal=f"{flv['table']}_thresholds",
                summary=f"{target} threshold is {threshold}.",
            ),
        ],
        required_elements=["exceeded", str(value), str(threshold)],
        forbidden_claims=[f"{target} did not exceed the threshold"],
        forbidden_elements=[],
        near_miss_reason="Two numbers must be compared explicitly; the answer requires both.",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
        gold_answer=f"{target} exceeded the threshold ({value} vs {threshold}).",
        grounding_attributions=["ctx_001", "ctx_002"],
    )


def b_struct_t_multi_corro(ctx: RowCtx) -> dict[str, Any]:
    flv = STRUCTURED_DOMAIN_FLAVOR[ctx.domain]
    value = 1000 + (ctx.seq * 17) % 5000
    period = _period(ctx.seq)
    a = _serialize_table(
        ctx.serialization,
        "finance_primary",
        ["period", "metric", "value"],
        [[period, f"{flv['metric']}_total", str(value)]],
    )
    b = _serialize_table(
        ctx.serialization,
        "bi_reconciliation",
        ["period", "metric", "value"],
        [[period, f"{flv['metric']}_total", str(value)]],
    )
    c = _serialize_table(
        ctx.serialization,
        "warehouse_audit",
        ["period", "metric", "value"],
        [[period, f"{flv['metric']}_total", str(value)]],
    )
    q = f"What does the {period} reporting say about total {flv['metric']}?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, a, authority_score=0.9, authority_signal="finance_primary", summary=f"Primary reports {value}."),
            _make_context(2, b, authority_score=0.88, authority_signal="bi_reconciliation", summary=f"BI reports {value}."),
            _make_context(3, c, authority_score=0.92, authority_signal="warehouse_audit", summary=f"Audit reports {value}."),
        ],
        required_elements=[str(value)],
        forbidden_claims=[f"different tables disagree about {flv['metric']}"],
        forbidden_elements=[],
        near_miss_reason="Three independent tables align on the same value.",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
        gold_answer=f"All three tables agree that {period} total {flv['metric']} was {value}.",
        grounding_attributions=["ctx_001", "ctx_002", "ctx_003"],
    )


def b_struct_t_schema_resolve(ctx: RowCtx) -> dict[str, Any]:
    """schema documentation plus result-grid alignment -> resolved_candidate_selection."""
    flv = STRUCTURED_DOMAIN_FLAVOR[ctx.domain]
    target = _entity(flv, ctx.seq)
    candidate_a = "legacy_balance"
    candidate_b = flv["schema_field"]
    value = 100 + (ctx.seq * 13) % 800
    schema_block = (
        f"Schema doc for {flv['table']}: column {candidate_a} is deprecated and must not be used; "
        f"the canonical metric column is {candidate_b}. Source-of-record: data_dictionary v3."
    )
    result_block = _serialize_table(
        ctx.serialization,
        flv["table"],
        [flv["id_field"], candidate_a, candidate_b],
        [[target, "NULL", str(value)]],
    )
    q = f"What is {target}'s {candidate_b} according to the current schema?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(
                1, schema_block, authority_score=0.93, authority_signal="data_dictionary",
                summary=f"Schema deprecates {candidate_a} and marks {candidate_b} canonical.",
            ),
            _make_context(
                2, result_block, authority_score=0.9, authority_signal=f"{flv['table']}_query_result",
                summary=f"Result grid populates {candidate_b}={value} for {target}.",
            ),
        ],
        required_elements=[str(value), candidate_b],
        forbidden_claims=[f"{target} {candidate_a} is {value}"],
        forbidden_elements=[],
        near_miss_reason="Two candidate columns exist; the schema resolves which one is valid.",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
        gold_answer=f"{target}'s {candidate_b} is {value} (the canonical column per the schema).",
        grounding_attributions=["ctx_001", "ctx_002"],
        evidence_chain_reason="Use the schema to pick the canonical column, then read the result grid for the value.",
    )


def b_struct_t_dashboard(ctx: RowCtx) -> dict[str, Any]:
    flv = STRUCTURED_DOMAIN_FLAVOR[ctx.domain]
    value = 80 + (ctx.seq * 5) % 200
    period = _period(ctx.seq)
    text = (
        f"Dashboard export (executive_overview, {period}): KPI={flv['metric']}_total, "
        f"value={value}, source=primary warehouse, owner=analytics_team."
    )
    text2 = (
        f"Dashboard export (analytics_review, {period}): KPI={flv['metric']}_total, value={value}, "
        "expert review note: matches primary warehouse extract."
    )
    q = f"According to the {period} executive dashboards, what was total {flv['metric']}?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, text, authority_score=0.9, authority_signal="executive_dashboard",
                          summary=f"Executive dashboard publishes total {flv['metric']} as {value}."),
            _make_context(2, text2, authority_score=0.91, authority_signal="analytics_dashboard",
                          summary=f"Analytics dashboard agrees on {value} with expert sign-off."),
        ],
        required_elements=[str(value)],
        forbidden_claims=[f"the dashboards disagreed on {flv['metric']}"],
        forbidden_elements=[],
        near_miss_reason="Two expert dashboards converge on the same KPI value.",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
        gold_answer=f"The executive and analytics dashboards both reported total {flv['metric']} as {value} for {period}.",
        grounding_attributions=["ctx_001", "ctx_002"],
    )


# --- Structured ABSTAIN builders --------------------------------------------
def b_struct_a_wrong_date(ctx: RowCtx) -> dict[str, Any]:
    flv = STRUCTURED_DOMAIN_FLAVOR[ctx.domain]
    target = _entity(flv, ctx.seq)
    asked_period = _period(ctx.seq)
    have_period = _period(ctx.seq + 1)
    value = 100 + (ctx.seq * 7) % 800
    table = _serialize_table(
        ctx.serialization,
        flv["table"],
        [flv["id_field"], "month", flv["metric"]],
        [[target, have_period, str(value)]],
    )
    q = f"What was {target}'s {flv['metric']} in the {asked_period} partition?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(
                1, table, authority_score=0.87, authority_signal=f"{flv['table']}_partition",
                summary=f"Retrieved partition is {have_period}, not {asked_period}.",
                anchor=have_period,
            )
        ],
        required_elements=[],
        forbidden_claims=[f"{asked_period} {flv['metric']} was {value}"],
        forbidden_elements=[],
        near_miss_reason=f"Entity matches but partition is {have_period}, not the requested {asked_period}.",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
    )


def b_struct_a_wrong_entity(ctx: RowCtx) -> dict[str, Any]:
    flv = STRUCTURED_DOMAIN_FLAVOR[ctx.domain]
    asked = _entity(flv, ctx.seq)
    have = _entity(flv, ctx.seq + 41)
    value = 100 + (ctx.seq * 13) % 800
    table = _serialize_table(
        ctx.serialization,
        flv["table"],
        [flv["id_field"], flv["metric"]],
        [[have, str(value)]],
    )
    q = f"What was {asked}'s {flv['metric']}?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(
                1, table, authority_score=0.88, authority_signal=f"{flv['table']}_partition",
                summary=f"Retrieved row is for {have}, not {asked}.",
            )
        ],
        required_elements=[],
        forbidden_claims=[f"{asked}'s {flv['metric']} was {value}"],
        forbidden_elements=[],
        near_miss_reason=f"The retrieved row is the wrong {flv['entity_name']}.",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
    )


def b_struct_a_wrong_region(ctx: RowCtx) -> dict[str, Any]:
    flv = STRUCTURED_DOMAIN_FLAVOR[ctx.domain]
    asked = _region_val(ctx.seq)
    have = _region_val(ctx.seq + 3, skip=_region_val(ctx.seq))
    target = _entity(flv, ctx.seq)
    period = _period(ctx.seq)
    value = 100 + (ctx.seq * 11) % 600
    table = _serialize_table(
        ctx.serialization,
        flv["table"],
        [flv["id_field"], "region", flv["metric"]],
        [[target, have, str(value)]],
    )
    q = f"What was {target}'s {flv['metric']} in the {asked} region in {period}?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(
                1, table, authority_score=0.87, authority_signal="regional_metric_table",
                summary=f"Row covers {have}, not {asked}.",
            )
        ],
        required_elements=[],
        forbidden_claims=[f"{asked} {flv['metric']} was {value}"],
        forbidden_elements=[],
        near_miss_reason=f"Region filter mismatch: retrieved {have} instead of {asked}.",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
    )


def b_struct_a_wrong_metric(ctx: RowCtx) -> dict[str, Any]:
    flv = STRUCTURED_DOMAIN_FLAVOR[ctx.domain]
    target = _entity(flv, ctx.seq)
    asked_col = f"net_{flv['metric']}"
    have_col = f"gross_{flv['metric']}"
    value = 100 + (ctx.seq * 17) % 900
    table = _serialize_table(
        ctx.serialization,
        flv["table"],
        [flv["id_field"], have_col],
        [[target, str(value)]],
    )
    q = f"What was {target}'s {asked_col} in the current period?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(
                1, table, authority_score=0.87, authority_signal="metric_table",
                summary=f"Only {have_col} is present; {asked_col} column is not in the extract.",
            )
        ],
        required_elements=[],
        forbidden_claims=[f"{target}'s {asked_col} was {value}"],
        forbidden_elements=[],
        near_miss_reason=f"Right entity, wrong metric column ({have_col} vs {asked_col}).",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
    )


def b_struct_a_missing_grid(ctx: RowCtx) -> dict[str, Any]:
    flv = STRUCTURED_DOMAIN_FLAVOR[ctx.domain]
    job_id = f"nightly-{ctx.seq:04d}"
    text = (
        f"Job control row for {job_id}: status=STARTED, expected_partitions=12, "
        "result_table=NULL, completed_at=NULL."
    )
    q = f"What was the final {flv['metric']} produced by job {job_id}?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(
                1, text, authority_score=0.88, authority_signal="job_control_table",
                summary="Setup metadata present but the result table is null.",
            )
        ],
        required_elements=[],
        forbidden_claims=[f"the job produced a final {flv['metric']} value"],
        forbidden_elements=[],
        near_miss_reason="Job started but the result grid was never written.",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
    )


def b_struct_a_empty_result(ctx: RowCtx) -> dict[str, Any]:
    flv = STRUCTURED_DOMAIN_FLAVOR[ctx.domain]
    asked = _entity(flv, ctx.seq)
    text = (
        f"Query result for {flv['table']} where {flv['id_field']}='{asked}': "
        "0 rows returned. The query executed successfully with an empty result set; "
        "the table contains other entities but none matching this filter."
    )
    q = f"What does the warehouse report for {asked}?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(
                1, text, authority_score=0.7, authority_signal="empty_query_result",
                summary=f"The filtered query returned no rows for {asked}.",
                relevance=0.4, boundary=0.5,
            )
        ],
        required_elements=[],
        forbidden_claims=[f"{asked} has any {flv['metric']} value in the retrieved evidence"],
        forbidden_elements=[],
        near_miss_reason="The retrieved evidence is an empty result set, not a populated row.",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
    )


def b_struct_a_stale_snapshot(ctx: RowCtx) -> dict[str, Any]:
    flv = STRUCTURED_DOMAIN_FLAVOR[ctx.domain]
    target = _entity(flv, ctx.seq)
    asked_period = _period(ctx.seq)
    have_period = _period(ctx.seq + 7)
    value = 100 + (ctx.seq * 7) % 800
    text = (
        f"{flv['table']} snapshot row: {flv['id_field']}={target}, snapshot_month={have_period}, "
        f"{flv['metric']}={value}. Snapshot is older than the requested {asked_period} cohort."
    )
    q = f"What is {target}'s {flv['metric']} in the {asked_period} snapshot?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(
                1, text, authority_score=0.78, authority_signal="warehouse_snapshot",
                summary=f"Snapshot is {have_period}; requested {asked_period}.",
                anchor=have_period, stale="high",
            )
        ],
        required_elements=[],
        forbidden_claims=[f"{asked_period} value for {target} was {value}"],
        forbidden_elements=[],
        near_miss_reason="Right entity, but snapshot is the wrong (stale) build/month.",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
    )


def b_struct_a_grain_mismatch(ctx: RowCtx) -> dict[str, Any]:
    flv = STRUCTURED_DOMAIN_FLAVOR[ctx.domain]
    asked_grain = "by channel"
    value = 1000 + (ctx.seq * 31) % 6000
    period = _period(ctx.seq)
    table = _serialize_table(
        ctx.serialization,
        flv["table"],
        ["period", "scope", flv["metric"]],
        [[period, "company_total", str(value)]],
    )
    q = f"What was {period} {flv['metric']} broken down {asked_grain}?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(
                1, table, authority_score=0.87, authority_signal="finance_summary_table",
                summary="Only a total grain is present; channel breakdown is absent.",
            )
        ],
        required_elements=[],
        forbidden_claims=[f"the channel breakdown of {flv['metric']} was {value}"],
        forbidden_elements=[],
        near_miss_reason=f"Aggregate grain mismatch: total provided where {asked_grain} was requested.",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
    )


def b_struct_a_sql_no_grid(ctx: RowCtx) -> dict[str, Any]:
    flv = STRUCTURED_DOMAIN_FLAVOR[ctx.domain]
    target = _entity(flv, ctx.seq)
    sql = (
        f"-- query.sql\nSELECT {flv['id_field']}, {flv['metric']} FROM {flv['table']} "
        f"WHERE {flv['id_field']}='{target}' AND month='2026-05';"
    )
    text = (
        f"SQL text retrieved from query repository:\n{sql}\nNo execution log or result grid is included "
        "in this retrieval; the query has not been run against the warehouse here."
    )
    q = f"What did the {target} {flv['metric']} query return?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(
                1, text, authority_score=0.7, authority_signal="query_repository",
                summary="SQL was retrieved but no executed result is present.",
            )
        ],
        required_elements=[],
        forbidden_claims=[f"the query returned a value for {target}"],
        forbidden_elements=[],
        near_miss_reason="Setup (SQL text) provided, but the executed result was never produced.",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
    )


def b_struct_a_schema_no_values(ctx: RowCtx) -> dict[str, Any]:
    flv = STRUCTURED_DOMAIN_FLAVOR[ctx.domain]
    target = _entity(flv, ctx.seq)
    period = _period(ctx.seq)
    text = (
        f"Schema definition for {flv['table']}: columns ({flv['id_field']} TEXT, month DATE, "
        f"{flv['metric']} NUMERIC). No sample rows or query results are included in the retrieved excerpt."
    )
    q = f"What is {target}'s {flv['metric']} value in the {period} {flv['table']} data?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(
                1, text, authority_score=0.6, authority_signal="schema_registry",
                summary="Schema present but no values are retrieved.",
                relevance=0.4, boundary=0.5,
            )
        ],
        required_elements=[],
        forbidden_claims=[f"the {flv['metric']} value is known from the retrieved evidence"],
        forbidden_elements=[],
        near_miss_reason="Schema is too general to answer a specific value query.",
        mechanism=ctx.mechanism,
        serialization="schema",  # always schema
    )


def b_struct_a_partial_slice(ctx: RowCtx) -> dict[str, Any]:
    flv = STRUCTURED_DOMAIN_FLAVOR[ctx.domain]
    asked = _entity(flv, ctx.seq)
    have = _entity(flv, ctx.seq + 53)
    other = _entity(flv, ctx.seq + 97)
    table = _serialize_table(
        ctx.serialization,
        flv["table"],
        [flv["id_field"], flv["metric"]],
        [[have, "120"], [other, "230"]],
    )
    q = f"What is the {asked} row in {flv['table']}?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(
                1, table, authority_score=0.82, authority_signal=f"{flv['table']}_excerpt",
                summary=f"Table excerpt has other rows but no {asked} row.",
            )
        ],
        required_elements=[],
        forbidden_claims=[f"{asked} appears in the excerpt"],
        forbidden_elements=[],
        near_miss_reason="The retrieved partial table does not include the requested slice.",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
    )


# --- Structured DISPUTED builders -------------------------------------------
def b_struct_d_same_metric_diff(ctx: RowCtx) -> dict[str, Any]:
    flv = STRUCTURED_DOMAIN_FLAVOR[ctx.domain]
    period = _period(ctx.seq)
    val_a = 100 + (ctx.seq * 7) % 900
    val_b = val_a + 25 + (ctx.seq % 13)
    a = _serialize_table(
        ctx.serialization, "finance_primary",
        ["period", "metric", "value", "basis"],
        [[period, f"{flv['metric']}_total", str(val_a), "management"]],
    )
    b = _serialize_table(
        ctx.serialization, "audit_export",
        ["period", "metric", "value", "basis"],
        [[period, f"{flv['metric']}_total", str(val_b), "management"]],
    )
    q = f"What was {period} total {flv['metric']}?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, a, authority_score=0.9, authority_signal="finance_primary",
                          summary=f"Primary reports {val_a}.", anchor=period),
            _make_context(2, b, authority_score=0.9, authority_signal="audit_export",
                          summary=f"Audit reports {val_b}.", anchor=period),
        ],
        required_elements=[],
        forbidden_claims=[f"{period} {flv['metric']} was {val_a}", f"{period} {flv['metric']} was {val_b}"],
        forbidden_elements=[],
        near_miss_reason="Two same-basis sources report different values for the same metric and period.",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
    )


def b_struct_d_table_dashboard(ctx: RowCtx) -> dict[str, Any]:
    flv = STRUCTURED_DOMAIN_FLAVOR[ctx.domain]
    target = _entity(flv, ctx.seq)
    val_table = 100 + (ctx.seq * 11) % 800
    val_dash = val_table + 30 + (ctx.seq % 11)
    a = _serialize_table(
        ctx.serialization, flv["table"],
        [flv["id_field"], flv["metric"]],
        [[target, str(val_table)]],
    )
    b = (
        f"Executive dashboard export: KPI={flv['metric']} for {target}, value={val_dash}, "
        "source=BI summary. Note: dashboard pulled from cube refresh."
    )
    q = f"What is {target}'s current {flv['metric']} per the company sources?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, a, authority_score=0.92, authority_signal=f"{flv['table']}_source_table",
                          summary=f"Source table reports {val_table}."),
            _make_context(2, b, authority_score=0.68, authority_signal="executive_dashboard",
                          summary=f"Executive dashboard reports {val_dash}."),
        ],
        required_elements=[],
        forbidden_claims=[f"{target} {flv['metric']} is {val_table}", f"{target} {flv['metric']} is {val_dash}"],
        forbidden_elements=[],
        near_miss_reason="Source-of-truth table and downstream dashboard publish incompatible values.",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
    )


def b_struct_d_cohort_def(ctx: RowCtx) -> dict[str, Any]:
    period = _period(ctx.seq)
    region = _region_val(ctx.seq)
    val_a = 9000 + (ctx.seq * 17) % 6000
    val_b = val_a + 1500 + (ctx.seq % 700)
    a = _serialize_table(
        ctx.serialization, "active_users_definition_a",
        ["period", "region", "cohort_definition", "value"],
        [[period, region, "logged_in_within_28d", str(val_a)]],
    )
    b = _serialize_table(
        ctx.serialization, "active_users_definition_b",
        ["period", "region", "cohort_definition", "value"],
        [[period, region, "logged_in_within_7d_and_paid", str(val_b)]],
    )
    q = f"How many active users were there in {region} in {period}?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, a, authority_score=0.88, authority_signal="cohort_definition_a",
                          summary=f"Definition A (logged in within 28 days) reports {val_a}."),
            _make_context(2, b, authority_score=0.88, authority_signal="cohort_definition_b",
                          summary=f"Definition B (logged in within 7 days and paid) reports {val_b}."),
        ],
        required_elements=[],
        forbidden_claims=[f"there were {val_a} active users", f"there were {val_b} active users", "the two cohort definitions agree"],
        forbidden_elements=[],
        near_miss_reason="Two tables use the same label but with conflicting cohort definitions.",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
    )


def b_struct_d_job_status(ctx: RowCtx) -> dict[str, Any]:
    job_id = f"daily-{ctx.seq:04d}"
    a = _serialize_table(
        ctx.serialization, "scheduler_status",
        ["job_id", "scheduled", "status"],
        [[job_id, "2026-05-22T02:00Z", "SUCCEEDED"]],
    )
    b = _serialize_table(
        ctx.serialization, "execution_log",
        ["job_id", "ended_at", "exit_code", "status"],
        [[job_id, "2026-05-22T02:13Z", "1", "FAILED"]],
    )
    c = _serialize_table(
        ctx.serialization, "result_check_table",
        ["job_id", "checks_run", "checks_failed", "status"],
        [[job_id, "5", "2", "FAILED"]],
    )
    q = f"Did job {job_id} complete successfully on 2026-05-22?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, a, authority_score=0.82, authority_signal="scheduler",
                          summary="Scheduler shows SUCCEEDED."),
            _make_context(2, b, authority_score=0.92, authority_signal="execution_log",
                          summary="Execution log shows FAILED exit code 1."),
            _make_context(3, c, authority_score=0.9, authority_signal="check_table",
                          summary="Check table shows 2 of 5 checks failed."),
        ],
        required_elements=[],
        forbidden_claims=[f"job {job_id} succeeded", f"job {job_id} failed without noting the conflict"],
        forbidden_elements=[],
        near_miss_reason="Scheduler, log, and check table give incompatible statuses for the same job run.",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
    )


def b_struct_d_pass_fail(ctx: RowCtx) -> dict[str, Any]:
    run_id = f"recon-{ctx.seq:04d}"
    a = _serialize_table(
        ctx.serialization, "recon_runs",
        ["run_id", "status", "failed_rows"],
        [[run_id, "PASS", "0"]],
    )
    b = _serialize_table(
        ctx.serialization, "audit_table",
        ["run_id", "final_verdict", "discrepancies"],
        [[run_id, "FAIL", "17"]],
    )
    q = f"Did the {run_id} reconciliation pass?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, a, authority_score=0.82, authority_signal="recon_runs",
                          summary="Scheduler status table marks the run PASS."),
            _make_context(2, b, authority_score=0.93, authority_signal="audit_table",
                          summary="Audit table marks the same run FAIL."),
        ],
        required_elements=[],
        forbidden_claims=[f"{run_id} passed", f"{run_id} failed without noting the conflict"],
        forbidden_elements=[],
        near_miss_reason="Two tables give incompatible PASS/FAIL verdicts for the same run.",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
    )


def b_struct_d_same_id_states(ctx: RowCtx) -> dict[str, Any]:
    order_id = f"ORD-{ctx.seq:05d}"
    a = _serialize_table(
        ctx.serialization, "order_state_a",
        ["order_id", "final_state"],
        [[order_id, "shipped"]],
    )
    b = _serialize_table(
        ctx.serialization, "order_state_b",
        ["order_id", "final_state"],
        [[order_id, "cancelled"]],
    )
    q = f"What is the final state of order {order_id}?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, a, authority_score=0.9, authority_signal="orders_warehouse",
                          summary="Warehouse table says shipped."),
            _make_context(2, b, authority_score=0.9, authority_signal="orders_finance",
                          summary="Finance table says cancelled."),
        ],
        required_elements=[],
        forbidden_claims=[f"{order_id} was shipped", f"{order_id} was cancelled without noting the conflict"],
        forbidden_elements=[],
        near_miss_reason="Same order ID has incompatible final states in two systems.",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
    )


def b_struct_d_stale_vs_current(ctx: RowCtx) -> dict[str, Any]:
    flv = STRUCTURED_DOMAIN_FLAVOR[ctx.domain]
    target = _entity(flv, ctx.seq)
    val_old = 100 + (ctx.seq * 9) % 700
    val_new = val_old + 50 + (ctx.seq % 7)
    a = _serialize_table(
        ctx.serialization, "snapshot_2025_12",
        [flv["id_field"], "snapshot_month", flv["metric"]],
        [[target, "2025-12", str(val_old)]],
    )
    b = _serialize_table(
        ctx.serialization, "snapshot_2026_05",
        [flv["id_field"], "snapshot_month", flv["metric"]],
        [[target, "2026-05", str(val_new)]],
    )
    q = f"What is {target}'s {flv['metric']}?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, a, authority_score=0.83, authority_signal="snapshot_old",
                          summary=f"Old snapshot shows {val_old}.", anchor="2025-12", stale="high"),
            _make_context(2, b, authority_score=0.83, authority_signal="snapshot_current",
                          summary=f"Current snapshot shows {val_new}.", anchor="2026-05"),
        ],
        required_elements=[],
        forbidden_claims=[f"{target}'s {flv['metric']} is {val_old}", f"{target}'s {flv['metric']} is {val_new} (no temporal framing)"],
        forbidden_elements=[],
        near_miss_reason="The same row appears in two snapshots with different values and no temporal framing in the query.",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
    )


def b_struct_d_total_vs_rows(ctx: RowCtx) -> dict[str, Any]:
    flv = STRUCTURED_DOMAIN_FLAVOR[ctx.domain]
    period = _period(ctx.seq)
    asked_total = 1000 + (ctx.seq * 13) % 5000
    actual_sum = asked_total - 200 - (ctx.seq % 30)
    a = _serialize_table(
        ctx.serialization, f"{flv['table']}_total",
        ["period", "metric", "value"],
        [[period, f"{flv['metric']}_total", str(asked_total)]],
    )
    b = _serialize_table(
        ctx.serialization, f"{flv['table']}_rows",
        ["period", flv["id_field"], flv["metric"]],
        [
            [period, "row_1", str(actual_sum // 3)],
            [period, "row_2", str(actual_sum // 3)],
            [period, "row_3", str(actual_sum - 2 * (actual_sum // 3))],
        ],
    )
    q = f"What was the {period} total {flv['metric']}?"
    return build_row(
        modality="structured",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, a, authority_score=0.88, authority_signal="aggregate_table",
                          summary=f"Aggregate row says total={asked_total}."),
            _make_context(2, b, authority_score=0.9, authority_signal="row_level_table",
                          summary=f"Row-level data sums to {actual_sum}."),
        ],
        required_elements=[],
        forbidden_claims=[f"the {period} total was {asked_total}", f"the {period} total was {actual_sum} without noting the conflict"],
        forbidden_elements=[],
        near_miss_reason="Aggregate total and row-level data conflict at the same scope.",
        mechanism=ctx.mechanism,
        serialization=ctx.serialization,
    )


# ---------------------------------------------------------------------------
# Code-modality builders
# ---------------------------------------------------------------------------
CODE_LANGUAGES = [
    "python",
    "typescript",
    "sql",
    "yaml",
    "shell_ci",
    "go",
    "java_kotlin",
    "rust",
    "logs_trace",
    "docs_mixed",
]


def _lang_snippet(lang: str, *, name: str, value: str, kind: str = "default") -> str:
    n = name
    v = value
    if lang == "python":
        return f"# settings.py\n{n.upper()} = {v}  # {kind}"
    if lang == "typescript":
        return f"// config.ts\nexport const {n} = {v}; // {kind}"
    if lang == "sql":
        return f"-- migrations.sql\nALTER TABLE settings SET DEFAULT {v} FOR {n}; -- {kind}"
    if lang == "yaml":
        return f"# config.yaml\n{n}: {v}  # {kind}"
    if lang == "shell_ci":
        return f"# ci.sh\nexport {n.upper()}={v} # {kind}"
    if lang == "go":
        return f"// config.go\nvar {n} = {v} // {kind}"
    if lang == "java_kotlin":
        return f"// Config.kt\nconst val {n} = {v} // {kind}"
    if lang == "rust":
        return f"// config.rs\npub const {n.upper()}: u32 = {v}; // {kind}"
    if lang == "logs_trace":
        return f"# app.log\n2026-05-22T10:11Z INFO {n}={v}  # {kind}"
    if lang == "docs_mixed":
        return f"<!-- docs/config.md -->\nThe {n} setting defaults to {v}. ({kind})"
    return f"{n} = {v}"


# --- Code diversity pools ----------------------------------------------------
# Sized so (root x qualifier) and func/route/setting spaces exceed any per-builder
# row count, so identifiers do not repeat within a mechanism.
_CODE_FEATURE_ROOTS = [
    "auth", "billing", "search", "catalog", "checkout", "users", "orders", "uploads",
    "payments", "invoices", "notifications", "webhooks", "sessions", "ratelimit",
    "audit", "reports", "exports", "imports", "scheduler", "cache", "ingest", "indexer",
    "permissions", "profiles", "subscriptions", "refunds", "shipping", "inventory",
    "pricing", "promotions", "messaging", "feeds", "comments", "media", "transcoder",
    "analytics", "telemetry", "gateway", "router", "tokens",
]
_CODE_QUALS = ["", "v2", "core", "edge", "internal", "async", "batch", "stream", "worker", "legacy", "v3", "beta", "admin"]
_CODE_FUNCS = [
    "compute_total", "build_session", "load_config", "render_page", "parse_iso",
    "normalize_email", "validate_payload", "serialize_record", "resolve_path",
    "encode_token", "hash_password", "merge_results", "filter_rows", "rank_items",
    "split_batch", "apply_discount", "round_amount", "format_currency", "build_url",
    "dispatch_event", "retry_request", "checkpoint_state", "flush_queue", "schedule_job",
    "expand_template", "compress_payload", "lookup_user", "audit_action", "emit_metric",
    "rotate_key",
]
_CODE_RESOURCES = [
    "orders", "invoices", "users", "products", "carts", "shipments", "refunds",
    "subscriptions", "tickets", "sessions", "webhooks", "files", "comments",
    "payments", "accounts", "teams",
]
_CODE_METHODS = ["GET", "POST", "PATCH", "PUT", "DELETE"]
_CODE_PACKAGES = [
    "acme-utils", "fastvec", "tinyqueue", "treeshake", "blobcache", "jsonwire",
    "retrykit", "schemaforge", "metricmux", "tokenring", "pathweaver", "configloom",
    "streamline", "batchwell", "hashbrook", "queuely",
]
_CODE_SETTINGS = [
    "HTTP_TIMEOUT_SECONDS", "CACHE_TTL_SECONDS", "MAX_RETRIES", "POOL_SIZE",
    "BATCH_SIZE", "RATE_LIMIT_PER_MIN", "SESSION_TTL_SECONDS", "PAGE_SIZE",
    "WORKER_CONCURRENCY", "QUEUE_DEPTH", "CONNECT_TIMEOUT_MS", "READ_TIMEOUT_MS",
]
_CODE_TYPES = [
    ("User", "status", ["active", "archived"]),
    ("Order", "state", ["open", "fulfilled", "cancelled"]),
    ("Invoice", "kind", ["draft", "issued", "void"]),
    ("Session", "tier", ["free", "pro", "enterprise"]),
    ("Ticket", "priority", ["low", "high", "urgent"]),
    ("Account", "role", ["member", "admin"]),
    ("Shipment", "mode", ["air", "ground", "sea"]),
    ("Payment", "method", ["card", "bank", "wallet"]),
]
_CODE_ENVS = ["staging", "development", "preview", "qa", "sandbox", "canary"]


def _cfeat(seq: int, offset: int = 0) -> str:
    i = seq + offset
    root = _CODE_FEATURE_ROOTS[i % len(_CODE_FEATURE_ROOTS)]
    qual = _CODE_QUALS[(i // len(_CODE_FEATURE_ROOTS)) % len(_CODE_QUALS)]
    return f"{root}_{qual}" if qual else root


def _cfunc(seq: int, offset: int = 0) -> str:
    i = seq + offset
    base = _CODE_FUNCS[i % len(_CODE_FUNCS)]
    suffix = (i // len(_CODE_FUNCS)) % 50
    return base if suffix == 0 else f"{base}_{suffix}"


def _cresource(seq: int, offset: int = 0) -> str:
    i = seq + offset
    base = _CODE_RESOURCES[i % len(_CODE_RESOURCES)]
    suffix = (i // len(_CODE_RESOURCES)) % 60
    return base if suffix == 0 else f"{base}{suffix}"


def _cmethod(seq: int) -> str:
    return _CODE_METHODS[seq % len(_CODE_METHODS)]


def _cpkg(seq: int) -> str:
    i = seq
    base = _CODE_PACKAGES[i % len(_CODE_PACKAGES)]
    suffix = (i // len(_CODE_PACKAGES)) % 60
    return base if suffix == 0 else f"{base}{suffix}"


def _csetting(seq: int) -> str:
    return _CODE_SETTINGS[seq % len(_CODE_SETTINGS)]


def _cenv(seq: int) -> str:
    return _CODE_ENVS[seq % len(_CODE_ENVS)]


def _cphrase(seq: int, variants: list[str]) -> str:
    return variants[seq % len(variants)]


# --- Code TRUSTWORTHY builders ----------------------------------------------
def b_code_t_exact_function(ctx: RowCtx) -> dict[str, Any]:
    lang = CODE_LANGUAGES[ctx.seq % len(CODE_LANGUAGES)]
    feature = _cfeat(ctx.seq)
    if lang == "python":
        snippet = (
            f"# {feature}/middleware.py\n"
            f"def require_auth(req):\n"
            f"    header = req.headers.get('Authorization', '')\n"
            f"    if not header.startswith('Bearer '):\n"
            f"        return Response(status=401)\n"
            f"    return verify_token(header[7:])"
        )
        q = f"Does the {feature} middleware reject requests without a Bearer token?"
        gold = f"Yes. The {feature} middleware returns 401 when the Authorization header does not start with Bearer."
    elif lang == "typescript":
        snippet = (
            f"// {feature}/middleware.ts\n"
            "export function requireAuth(req: Request) {\n"
            "  const header = req.headers.get('Authorization') ?? '';\n"
            "  if (!header.startsWith('Bearer ')) {\n"
            "    return new Response(null, { status: 401 });\n"
            "  }\n"
            "  return verifyToken(header.slice(7));\n"
            "}"
        )
        q = f"Does the {feature} middleware reject requests without a Bearer token?"
        gold = f"Yes. The {feature} middleware returns 401 when the Authorization header does not start with Bearer."
    else:
        snippet = (
            f"// {feature}/middleware.{lang}\nfunction requireAuth(req) {{\n"
            "  if (!req.headers['authorization']) { return 401; }\n  return verifyToken(req);\n}"
        )
        q = f"Does the {feature} middleware reject requests without an Authorization header?"
        gold = f"Yes. The {feature} middleware returns 401 when the Authorization header is absent."
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, snippet, authority_score=0.94, authority_signal="source_code",
                          summary=f"The {feature} middleware returns 401 for the missing header branch."),
        ],
        required_elements=["401"],
        forbidden_claims=[f"the {feature} middleware returns 200 for missing header"],
        forbidden_elements=[],
        near_miss_reason="A model could confuse token verification failure with the missing-header branch.",
        mechanism=ctx.mechanism,
        serialization=None,
        gold_answer=gold,
        direct=True,
    )


def b_code_t_test_proves(ctx: RowCtx) -> dict[str, Any]:
    lang = CODE_LANGUAGES[ctx.seq % len(CODE_LANGUAGES)]
    feature = _cfeat(ctx.seq)
    fn = _cfunc(ctx.seq)
    if lang == "python":
        impl = f"# {feature}.py\ndef {fn}(x): return round(x, 2)"
        test = (
            f"# tests/test_{feature}.py\n"
            f"def test_{fn}_two_decimals():\n"
            f"    assert {fn}(10.005) == 10.0\n"
            f"    assert {fn}(2.345) == 2.35"
        )
    else:
        impl = f"// {feature}.{lang}\nfunction {fn}(x) {{ return Math.round(x * 100) / 100; }}"
        test = (
            f"// tests/{feature}.test.{lang}\n"
            f"test('{fn} rounds to two decimals', () => {{\n"
            f"  expect({fn}(2.345)).toBe(2.35);\n}});"
        )
    q = f"Does {feature}.{fn} round to two decimals?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, impl, authority_score=0.9, authority_signal="source_code",
                          summary=f"{feature}.{fn} uses two-decimal rounding."),
            _make_context(2, test, authority_score=0.92, authority_signal="test_suite",
                          summary=f"Test asserts {feature}.{fn} returns two-decimal output."),
        ],
        required_elements=["two decimals"],
        forbidden_claims=[f"{feature}.{fn} rounds to four decimals"],
        forbidden_elements=[],
        near_miss_reason="Implementation and test corroborate the requested behavior.",
        mechanism=ctx.mechanism,
        serialization=None,
        gold_answer=f"Yes. {feature}.{fn} rounds to two decimals (impl plus test).",
        grounding_attributions=["ctx_001", "ctx_002"],
    )


def b_code_t_config_sets(ctx: RowCtx) -> dict[str, Any]:
    lang = CODE_LANGUAGES[ctx.seq % len(CODE_LANGUAGES)]
    feature = _cfeat(ctx.seq)
    setting = _csetting(ctx.seq)
    val = 60 + (ctx.seq * 5) % 600
    setting_a = _lang_snippet(lang, name=f"{feature.upper()}_{setting}", value=str(val), kind="default")
    setting_b = _lang_snippet("python", name=f"{feature.upper()}_{setting}_FALLBACK", value=str(val), kind="echoed default")
    q = f"What default {setting} does the {feature} module use?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, setting_a, authority_score=0.92, authority_signal="source_code",
                          summary=f"Primary config sets {feature}.{setting}={val}."),
            _make_context(2, setting_b, authority_score=0.86, authority_signal="source_code",
                          summary=f"Echoed default also reports {val}."),
        ],
        required_elements=[str(val)],
        forbidden_claims=[f"{feature} has no default {setting}"],
        forbidden_elements=[],
        near_miss_reason="Two configuration sources agree on the same numerical default.",
        mechanism=ctx.mechanism,
        serialization=None,
        gold_answer=f"The {feature} module defaults {setting} to {val}.",
        grounding_attributions=["ctx_001", "ctx_002"],
    )


def b_code_t_stack_trace_line(ctx: RowCtx) -> dict[str, Any]:
    file_line = 40 + (ctx.seq * 3) % 200
    func = _cfunc(ctx.seq)
    mod = _cfeat(ctx.seq)
    trace = (
        "Traceback (most recent call last):\n"
        f'  File "{mod}/{func}.py", line {file_line}, in {func}\n'
        '    return total / divisor\n'
        "ZeroDivisionError: division by zero"
    )
    candidate_a = f"{mod}/util.py:{file_line - 20} in helper_a (called earlier in the stack)"
    candidate_b = f"{mod}/{func}.py:{file_line} in {func} (final frame, raised ZeroDivisionError)"
    text = (
        f"{trace}\n\nThe candidate frames considered were:\n- {candidate_a}\n- {candidate_b}\n"
        "The final frame is the source of the raised error."
    )
    source = (
        f"# {mod}/{func}.py\n"
        f"{file_line - 2}: def {func}(total, divisor):\n"
        f"{file_line - 1}:     if total is None: return 0\n"
        f"{file_line}:     return total / divisor\n"
        f"{file_line + 1}: # caller handles ZeroDivisionError upstream"
    )
    q = f"Which line raised the ZeroDivisionError in the {func} call?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, text, authority_score=0.92, authority_signal="stack_trace",
                          summary=f"Stack trace points to {mod}/{func}.py:{file_line}."),
            _make_context(2, source, authority_score=0.9, authority_signal="source_code",
                          summary=f"Source excerpt confirms line {file_line} is the division statement."),
        ],
        required_elements=[f"{mod}/{func}.py", str(file_line)],
        forbidden_claims=[f"{mod}/util.py raised the error"],
        forbidden_elements=[],
        near_miss_reason="Two candidate frames appear, but the trace resolves which is final.",
        mechanism=ctx.mechanism,
        serialization=None,
        gold_answer=f"{mod}/{func}.py line {file_line} raised the ZeroDivisionError.",
        grounding_attributions=["ctx_001", "ctx_002"],
        evidence_chain_reason="Use the trace to identify the final frame, then verify the referenced line in the source excerpt.",
    )


def b_code_t_docs_impl_agree(ctx: RowCtx) -> dict[str, Any]:
    val = 3 + (ctx.seq % 5)
    feature = _cfeat(ctx.seq)
    doc = (
        f"<!-- README.md -->\nThe {feature} client retries failed requests up to {val} times by default."
    )
    code = (
        f"// {feature}_client.py\n{feature.upper()}_DEFAULT_RETRIES = {val}\n\n"
        f"def build_session(retries={feature.upper()}_DEFAULT_RETRIES):\n    return Retry(total=retries)"
    )
    q = f"How many times does the {feature} client retry by default?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, doc, authority_score=0.84, authority_signal="repo_documentation",
                          summary=f"README says the {feature} client default is {val} retries."),
            _make_context(2, code, authority_score=0.95, authority_signal="source_code",
                          summary=f"Code sets {feature.upper()}_DEFAULT_RETRIES = {val}."),
        ],
        required_elements=[str(val)],
        forbidden_claims=[f"the {feature} client disables retries by default"],
        forbidden_elements=[],
        near_miss_reason="Docs and code agree on the same retry count.",
        mechanism=ctx.mechanism,
        serialization=None,
        gold_answer=f"The {feature} client retries up to {val} times by default.",
        grounding_attributions=["ctx_001", "ctx_002"],
    )


def b_code_t_api_route(ctx: RowCtx) -> dict[str, Any]:
    method = _cmethod(ctx.seq)
    res = _cresource(ctx.seq)
    resource = f"/{res}"
    code = (
        f"// routes/{res}.ts\n"
        f"router.{method.lower()}('{resource}/:id', handle_{method.lower()}_{res});"
    )
    q = f"Does the API support {method} {resource}/:id?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, code, authority_score=0.94, authority_signal="source_code",
                          summary=f"Router registers {method} for {resource}/:id."),
        ],
        required_elements=[method, resource],
        forbidden_claims=[f"the API does not support {method} {resource}/:id"],
        forbidden_elements=[],
        near_miss_reason="The route declaration directly answers the API question.",
        mechanism=ctx.mechanism,
        serialization=None,
        gold_answer=f"Yes. The router declares {method} {resource}/:id.",
        direct=True,
    )


def b_code_t_type_iface(ctx: RowCtx) -> dict[str, Any]:
    type_name, field, values = _CODE_TYPES[ctx.seq % len(_CODE_TYPES)]
    feat = _cfeat(ctx.seq)
    literal = " | ".join(f"'{v}'" for v in values)
    lower = type_name.lower()
    code_iface = (
        f"// {feat}/types/{lower}.ts\n"
        f"export interface {type_name} {{\n"
        "  id: string;\n"
        f"  {field}: {literal};\n"
        "}"
    )
    code_use = (
        f"// {feat}/service.ts\nimport {{ {type_name} }} from './types/{lower}';\n"
        f"export function create_{lower}(input: Partial<{type_name}>): {type_name} {{ /* ... */ }}"
    )
    q = f"In the {feat} module, what are the allowed values for {type_name}.{field}?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, code_iface, authority_score=0.95, authority_signal="type_definition",
                          summary=f"Interface enumerates allowed {field} literals."),
            _make_context(2, code_use, authority_score=0.86, authority_signal="source_code",
                          summary="Usage import confirms the interface scope."),
        ],
        required_elements=list(values),
        forbidden_claims=[f"{type_name}.{field} allows arbitrary strings"],
        forbidden_elements=[],
        near_miss_reason="The type literal enumerates the legal values directly.",
        mechanism=ctx.mechanism,
        serialization=None,
        gold_answer=f"{type_name}.{field} is the literal union {literal}.",
        grounding_attributions=["ctx_001", "ctx_002"],
    )


# --- Code ABSTAIN builders ---------------------------------------------------
def b_code_a_missing_file(ctx: RowCtx) -> dict[str, Any]:
    feature = _cfeat(ctx.seq)
    topic = _cphrase(ctx.seq, ["retry policy", "rate limiter", "cache layer", "auth guard", "backoff policy"])
    text = (
        f"Repository search results for '{feature} {topic}':\n"
        f"- {feature}/README.md (mentions the {topic} at high level)\n"
        f"- tests/test_{feature}.py (uses a mocked {topic})\n"
        f"No source file for the actual {feature} {topic} implementation appears in the search results."
    )
    q = f"How is the {feature} {topic} implemented in code?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, text, authority_score=0.7, authority_signal="repo_search",
                          summary="Search finds README and tests but no implementation file.",
                          relevance=0.4, boundary=0.5),
        ],
        required_elements=[],
        forbidden_claims=[f"the {feature} {topic} uses any specific concrete implementation"],
        forbidden_elements=[],
        near_miss_reason="The retrieved evidence does not include the implementation file.",
        mechanism=ctx.mechanism,
        serialization=None,
    )


def b_code_a_wrong_version(ctx: RowCtx) -> dict[str, Any]:
    sdk = _cpkg(ctx.seq)
    major = 2 + (ctx.seq % 6)
    minor = 1 + (ctx.seq % 5)
    have = f"{major}.{minor}.0"
    asked = f"{major}.{minor + 1}.1"
    text = (
        f"{sdk}-{have}/docs/uploads.md: Upload retries use fixed 2 second intervals. "
        f"This page applies to {sdk} version {have}."
    )
    q = f"Does {sdk} {asked} use exponential backoff for upload retries?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, text, authority_score=0.82, authority_signal="versioned_docs",
                          summary=f"Docs are for {have}, not {asked}.", anchor=have),
        ],
        required_elements=[],
        forbidden_claims=[f"{sdk} {asked} uses fixed 2 second intervals", f"{sdk} {asked} uses exponential backoff"],
        forbidden_elements=[],
        near_miss_reason=f"Right {sdk} family but the wrong concrete version ({have} vs {asked}).",
        mechanism=ctx.mechanism,
        serialization=None,
    )


def b_code_a_incomplete_snippet(ctx: RowCtx) -> dict[str, Any]:
    res = _cresource(ctx.seq)
    asked_m = _cphrase(ctx.seq, ["PATCH", "DELETE", "PUT", "HEAD"])
    text = (
        f"// {res}/router.ts (excerpt only)\n"
        f"router.get('/{res}', list_{res});\n"
        f"router.post('/{res}', create_{res});\n"
        "// ... rest of file truncated in retrieval ..."
    )
    q = f"Does the /{res} router support {asked_m}?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, text, authority_score=0.78, authority_signal="source_code_excerpt",
                          summary=f"Excerpt shows GET and POST for /{res} but the file is truncated."),
        ],
        required_elements=[],
        forbidden_claims=[f"the /{res} router supports {asked_m}", f"{asked_m} is explicitly unsupported"],
        forbidden_elements=[],
        near_miss_reason="Excerpt is partial; the rest of the file is not retrieved.",
        mechanism=ctx.mechanism,
        serialization=None,
    )


def b_code_a_impl_no_test(ctx: RowCtx) -> dict[str, Any]:
    feature = _cphrase(ctx.seq, ["refund", "renew", "cancel", "approve", "archive", "settle", "void", "reopen"])
    obj = _cresource(ctx.seq)
    text = (
        f"# {obj}.py\n"
        f"def {feature}_{obj}({obj}_id):\n    # marks {obj} as {feature}\n    return True\n\n"
        f"# tests/ directory listing: no test file for {feature}_{obj} was retrieved."
    )
    q = f"Is there a test that proves {feature}_{obj} rejects invalid input?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, text, authority_score=0.82, authority_signal="source_code_and_test_listing",
                          summary=f"Implementation present, but no test for {feature}_{obj} in retrieval."),
        ],
        required_elements=[],
        forbidden_claims=[f"a test proves {feature}_{obj} rejects invalid input"],
        forbidden_elements=[],
        near_miss_reason="Implementation exists but the retrieved test set lacks the requested coverage.",
        mechanism=ctx.mechanism,
        serialization=None,
    )


def b_code_a_docs_no_code(ctx: RowCtx) -> dict[str, Any]:
    feature = _cfeat(ctx.seq)
    text = (
        f"<!-- docs/{feature}.md -->\nThe {feature} feature can be enabled per organization. "
        "See the implementation in src/* for details. (No source files for this feature were "
        "included in the retrieved bundle.)"
    )
    q = f"How is the {feature} feature implemented in code?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, text, authority_score=0.72, authority_signal="repo_documentation",
                          summary=f"Docs mention {feature} but no code was retrieved."),
        ],
        required_elements=[],
        forbidden_claims=[f"the {feature} feature uses a specific implementation"],
        forbidden_elements=[],
        near_miss_reason="Docs describe the feature in the abstract but the implementation is too general to answer.",
        mechanism=ctx.mechanism,
        serialization=None,
    )


def b_code_a_ambiguous_name(ctx: RowCtx) -> dict[str, Any]:
    sym = _cfunc(ctx.seq)
    mod_a = _cfeat(ctx.seq)
    mod_b = _cfeat(ctx.seq + 17)
    flow = _cfeat(ctx.seq + 5)
    text = (
        f"Symbol search for `{sym}`:\n"
        f"- {mod_a}/{sym}.py: handles {mod_a}-side processing.\n"
        f"- {mod_b}/{sym}.py: handles {mod_b}-side processing.\n"
        "No disambiguation comment was retrieved indicating which module the caller invokes."
    )
    q = f"Which {sym} is used by the {flow} flow?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, text, authority_score=0.78, authority_signal="symbol_search",
                          summary=f"Two functions named {sym} exist in different modules; no caller import retrieved."),
        ],
        required_elements=[],
        forbidden_claims=[f"the {flow} flow uses {mod_a}.{sym}", f"the {flow} flow uses {mod_b}.{sym}"],
        forbidden_elements=[],
        near_miss_reason="Symbol collision with no retrieved caller-side disambiguation.",
        mechanism=ctx.mechanism,
        serialization=None,
    )


def b_code_a_wrong_env_config(ctx: RowCtx) -> dict[str, Any]:
    target_env = _cphrase(ctx.seq, ["production", "prod-eu", "prod-us", "production-canary"])
    have_env = _cenv(ctx.seq)
    feature = _cfeat(ctx.seq)
    setting = _csetting(ctx.seq).lower()
    val = 30 + (ctx.seq * 3) % 300
    text = (
        f"# config/{have_env}.yaml\n{feature}_{setting}: {val}\n# This file is the {have_env} "
        f"environment configuration."
    )
    q = f"What is {feature} {setting} in {target_env}?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, text, authority_score=0.78, authority_signal="environment_config",
                          summary=f"Config is for {have_env}, not {target_env}.", anchor=have_env),
        ],
        required_elements=[],
        forbidden_claims=[f"{target_env} {feature} {setting} is {val}"],
        forbidden_elements=[],
        near_miss_reason=f"Config key from the wrong environment ({have_env} vs {target_env}).",
        mechanism=ctx.mechanism,
        serialization=None,
    )


def b_code_a_trace_no_root(ctx: RowCtx) -> dict[str, Any]:
    err = _cphrase(ctx.seq, ["ValueError", "KeyError", "TypeError", "RuntimeError", "AttributeError", "IndexError"])
    mod = _cfeat(ctx.seq)
    l1 = 10 + (ctx.seq * 2) % 40
    l2 = 40 + (ctx.seq * 3) % 120
    text = (
        "Stack trace excerpt (top frames only):\n"
        f"  File 'wsgi.py', line {l1}, in application\n"
        f"  File '{mod}/middleware.py', line {l2}, in __call__\n"
        "  ... (trace truncated; root frame not present in retrieval) ...\n"
        f"Error class: {err}"
    )
    q = f"Which exact line caused the {err} in {mod}?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, text, authority_score=0.8, authority_signal="stack_trace_excerpt",
                          summary="Trace shows entry frames but the root frame was truncated."),
        ],
        required_elements=[],
        forbidden_claims=[f"the {err} was raised by {mod}/middleware.py:{l2}"],
        forbidden_elements=[],
        near_miss_reason="Trace setup present but the requested final-frame line is absent.",
        mechanism=ctx.mechanism,
        serialization=None,
    )


def b_code_a_dep_docs_insuff(ctx: RowCtx) -> dict[str, Any]:
    pkg = _cpkg(ctx.seq)
    text = (
        f"<!-- {pkg}/README.md -->\n{pkg} provides high-performance data utilities. "
        "See the API reference at example.com/docs (the reference page was not included in retrieval)."
    )
    q = f"How do I configure {pkg} for a custom retry policy in my project?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, text, authority_score=0.65, authority_signal="dependency_docs",
                          summary=f"{pkg} README is too general for the specific configuration question."),
        ],
        required_elements=[],
        forbidden_claims=[f"{pkg} can be configured with a specific concrete retry policy from the retrieved evidence"],
        forbidden_elements=[],
        near_miss_reason="Dependency documentation is too general to answer the specific question.",
        mechanism=ctx.mechanism,
        serialization=None,
    )


def b_code_a_client_no_server(ctx: RowCtx) -> dict[str, Any]:
    res = _cresource(ctx.seq)
    route = f"/{res}"
    text = (
        f"// generated_client.ts\nexport async function call_{res}(input) {{\n"
        f"  return fetch('{route}', {{ method: 'POST', body: JSON.stringify(input) }});\n}}\n"
        "// No corresponding server route file was retrieved for the POST handler."
    )
    q = f"What server-side validation runs on POST {route}?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, text, authority_score=0.75, authority_signal="generated_client_only",
                          summary=f"Generated client for POST {route} present but no server route retrieved."),
        ],
        required_elements=[],
        forbidden_claims=[f"POST {route} validation is specific from the retrieved evidence"],
        forbidden_elements=[],
        near_miss_reason="The client side is present but the server-side route is the wrong aspect of the system to read here.",
        mechanism=ctx.mechanism,
        serialization=None,
    )


# --- Code DISPUTED builders --------------------------------------------------
def b_code_d_doc_vs_code(ctx: RowCtx) -> dict[str, Any]:
    code_val = 3 + (ctx.seq % 5)
    feature = _cfeat(ctx.seq)
    a = (
        f"<!-- README.md -->\nBy default the {feature} client does not retry failed requests. "
        f"Set {feature.upper()}_RETRIES to enable retries."
    )
    b = (
        f"// {feature}_client.py\n{feature.upper()}_DEFAULT_RETRIES = {code_val}\n"
        f"def build_session(retries={feature.upper()}_DEFAULT_RETRIES):\n    return Retry(total=retries)"
    )
    q = f"Are {feature} client retries disabled by default?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, a, authority_score=0.72, authority_signal="repo_documentation",
                          summary="README says retries are disabled by default."),
            _make_context(2, b, authority_score=0.95, authority_signal="source_code",
                          summary=f"Code sets DEFAULT_RETRIES = {code_val}."),
        ],
        required_elements=[],
        forbidden_claims=["retries are disabled by default", f"retries default to {code_val} without noting the documentation conflict"],
        forbidden_elements=[],
        near_miss_reason="Documentation and code directly disagree on the default.",
        mechanism=ctx.mechanism,
        serialization=None,
    )


def b_code_d_test_vs_impl(ctx: RowCtx) -> dict[str, Any]:
    name = _cfunc(ctx.seq)
    impl = f"# {name}.py\ndef {name}(x):\n    return x  # no transformation"
    test = (
        f"# tests/test_{name}.py\n"
        f"def test_{name}_transforms(): assert {name}('foo') == 'FOO'"
    )
    q = f"Does {name} transform its input?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, impl, authority_score=0.95, authority_signal="source_code",
                          summary="Implementation returns the input unchanged."),
            _make_context(2, test, authority_score=0.93, authority_signal="test_suite",
                          summary="Test asserts a transformed result."),
        ],
        required_elements=[],
        forbidden_claims=[f"{name} transforms its input", f"{name} does not transform its input without noting the test conflict"],
        forbidden_elements=[],
        near_miss_reason="Test verdict and implementation behavior contradict each other.",
        mechanism=ctx.mechanism,
        serialization=None,
    )


def b_code_d_two_files_defaults(ctx: RowCtx) -> dict[str, Any]:
    val_a = 30 + (ctx.seq * 5) % 300
    val_b = val_a + 60 + (ctx.seq % 11)
    feature = _cfeat(ctx.seq)
    setting = f"{feature.upper()}_{_csetting(ctx.seq)}"
    a = f"# {feature}/settings/base.py\n{setting} = {val_a}"
    b = f"# {feature}/settings/overrides.py\n{setting} = {val_b}  # imported last"
    q = f"What is the effective {setting} default in {feature}?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, a, authority_score=0.88, authority_signal="settings_base",
                          summary=f"Base sets {setting}={val_a}."),
            _make_context(2, b, authority_score=0.88, authority_signal="settings_overrides",
                          summary=f"Overrides sets {setting}={val_b}."),
        ],
        required_elements=[],
        forbidden_claims=[f"{setting} is {val_a}", f"{setting} is {val_b} without noting the conflict"],
        forbidden_elements=[],
        near_miss_reason="Two files define incompatible defaults for the same constant.",
        mechanism=ctx.mechanism,
        serialization=None,
    )


def b_code_d_changelog_vs_code(ctx: RowCtx) -> dict[str, Any]:
    feature = _cfeat(ctx.seq)
    a = (
        f"# CHANGELOG.md\nv2.4.0 - Removed the {feature} feature. {feature}_enabled is no "
        "longer read by the application."
    )
    b = (
        f"# settings.py\nif config.get('{feature}_enabled', False):\n"
        f"    register_{feature}_handlers()"
    )
    q = f"Is the {feature} feature still in use?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, a, authority_score=0.8, authority_signal="changelog",
                          summary=f"Changelog says {feature} was removed in v2.4.0.",
                          anchor="v2.4.0"),
            _make_context(2, b, authority_score=0.93, authority_signal="source_code",
                          summary=f"Current code still registers {feature} handlers under a config flag."),
        ],
        required_elements=[],
        forbidden_claims=[f"{feature} was removed", f"{feature} is still active without noting the changelog conflict"],
        forbidden_elements=[],
        near_miss_reason="Changelog contradicts current code behavior for the same feature.",
        mechanism=ctx.mechanism,
        serialization=None,
    )


def b_code_d_types_vs_runtime(ctx: RowCtx) -> dict[str, Any]:
    type_name, _field, _vals = _CODE_TYPES[ctx.seq % len(_CODE_TYPES)]
    fn = _cfunc(ctx.seq)
    rid = 1000 + (ctx.seq * 7) % 9000
    a = (
        "# api.py (type hints)\n"
        f"def {fn}(record_id: str) -> {type_name}:\n"
        "    return _lookup(record_id)"
    )
    b = (
        "# runtime trace\n"
        f"INFO: {fn} called with record_id=int({rid}); returned None (no {type_name} found and no exception raised)."
    )
    q = f"Does {fn} always return a {type_name} instance?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, a, authority_score=0.86, authority_signal="type_hints",
                          summary=f"Type hints declare return as {type_name}."),
            _make_context(2, b, authority_score=0.88, authority_signal="runtime_log",
                          summary="Runtime log shows None was returned with an int input."),
        ],
        required_elements=[],
        forbidden_claims=[f"{fn} always returns a {type_name}", f"{fn} never returns None"],
        forbidden_elements=[],
        near_miss_reason="The declared type contradicts an observed runtime behavior.",
        mechanism=ctx.mechanism,
        serialization=None,
    )


def b_code_d_stale_client_vs_server(ctx: RowCtx) -> dict[str, Any]:
    res = _cresource(ctx.seq)
    route = f"/{res}"
    a = (
        f"// generated_client.ts (last regen 2025-08)\nexport async function post_{res}(input) {{\n"
        f"  return fetch('{route}', {{ method: 'POST', body: JSON.stringify(input) }});\n}}"
    )
    b = (
        f"// server/routes.ts (current)\nrouter.put('{route}/:id', handle_update);\n"
        f"// Note: POST {route} is no longer registered."
    )
    q = f"Is POST {route} still a valid endpoint?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, a, authority_score=0.7, authority_signal="generated_client_stale",
                          summary=f"Generated client still posts to {route}.", anchor="2025-08", stale="high"),
            _make_context(2, b, authority_score=0.95, authority_signal="server_routes_current",
                          summary=f"Server no longer registers POST {route}."),
        ],
        required_elements=[],
        forbidden_claims=[f"POST {route} is valid", f"POST {route} was removed without noting the client conflict"],
        forbidden_elements=[],
        near_miss_reason="Stale generated client and current server route give incompatible answers.",
        mechanism=ctx.mechanism,
        serialization=None,
    )


def b_code_d_config_runtime_guard(ctx: RowCtx) -> dict[str, Any]:
    feature = _cfeat(ctx.seq)
    a = f"# config/production.yaml\n{feature}_enabled: true"
    b = (
        f"# {feature}.py\nif os.getenv('FORCE_DISABLE_{feature.upper()}', '') == '1':\n"
        f"    return None\n# In production this env var is set by the rollout guard."
    )
    q = f"Is {feature} enabled in production?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, a, authority_score=0.84, authority_signal="environment_config",
                          summary=f"Config marks {feature}_enabled=true."),
            _make_context(2, b, authority_score=0.92, authority_signal="runtime_guard_code",
                          summary=f"Runtime guard disables {feature} when FORCE_DISABLE is set."),
        ],
        required_elements=[],
        forbidden_claims=[f"{feature} is enabled in production", f"{feature} is disabled in production without noting the config conflict"],
        forbidden_elements=[],
        near_miss_reason="Configuration says enabled but runtime guard disables it.",
        mechanism=ctx.mechanism,
        serialization=None,
    )


def b_code_d_security_vs_middleware(ctx: RowCtx) -> dict[str, Any]:
    svc = _cfeat(ctx.seq)
    area = _cphrase(ctx.seq, ["admin", "billing", "internal", "ops", "console", "reports"])
    bypass = _cphrase(ctx.seq, ["x-internal", "x-service-mesh", "x-trusted", "x-bypass-auth"])
    a = (
        f"<!-- {svc}/docs/security_policy.md -->\nAll /{svc}/{area}/* endpoints must require an explicit "
        f"{area} role check. No anonymous traffic is allowed under any condition."
    )
    b = (
        f"// {svc}/middleware/{area}.ts\nexport function {area}Auth(req: Request) {{\n"
        f"  if (req.headers.get('{bypass}') === '1') return null; // skip {area} check for internal traffic\n"
        f"  return requireRole(req, '{area}');\n}}"
    )
    q = f"In the {svc} service, are anonymous-style {area} requests possible?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, a, authority_score=0.86, authority_signal="security_policy",
                          summary="Security policy bans any admin bypass."),
            _make_context(2, b, authority_score=0.92, authority_signal="middleware_source",
                          summary="Middleware bypasses admin check for x-internal traffic."),
        ],
        required_elements=[],
        forbidden_claims=["the policy and middleware agree"],
        forbidden_elements=[],
        near_miss_reason="Security policy scope and middleware behavior disagree about admin bypass.",
        mechanism=ctx.mechanism,
        serialization=None,
    )


def b_code_d_ci_vs_pkg(ctx: RowCtx) -> dict[str, Any]:
    repo = _cpkg(ctx.seq)
    ci_script = _cphrase(ctx.seq, ["test:unit", "test:ci", "lint:strict", "build:prod", "e2e:smoke", "check:types"])
    defined = _cphrase(ctx.seq, ["test", "test:integration", "build", "lint"])
    other = _cphrase(ctx.seq + 1, ["test:e2e", "format", "typecheck", "bundle"])
    a = (
        f"# {repo}/.github/workflows/ci.yaml\n"
        f"    - name: tests\n      run: npm run {ci_script}"
    )
    b = (
        f'# {repo}/package.json\n{{ "scripts": {{ "{defined}": "vitest run", "{other}": "playwright test" }} }}\n'
        f"# Note: there is no '{ci_script}' script defined."
    )
    q = f"In the {repo} repo, does the CI step 'npm run {ci_script}' match a defined npm script?"
    return build_row(
        modality="code",
        case_id="",
        pattern=ctx.pattern,
        domain=ctx.domain,
        difficulty=ctx.difficulty,
        query=q,
        query_rewritten=None,
        contexts=[
            _make_context(1, a, authority_score=0.85, authority_signal="ci_workflow",
                          summary=f"CI invokes npm run {ci_script}."),
            _make_context(2, b, authority_score=0.9, authority_signal="package_json",
                          summary=f"package.json defines scripts but no {ci_script}."),
        ],
        required_elements=[],
        forbidden_claims=["the CI and package.json agree on the command"],
        forbidden_elements=[],
        near_miss_reason="CI config and package.json scripts give incompatible commands.",
        mechanism=ctx.mechanism,
        serialization=None,
    )


# ---------------------------------------------------------------------------
# Structured spec table -> count per (label, mechanism, pattern, serialization)
# ---------------------------------------------------------------------------
STRUCT_SERIALIZATIONS = [
    "markdown", "csv", "key_value", "sql_grid", "dashboard", "schema", "etl_status",
]


def _serial_cycle(i: int) -> str:
    return STRUCT_SERIALIZATIONS[i % len(STRUCT_SERIALIZATIONS)]


STRUCT_T_MECH = [
    ("exact_filtered_row", "direct_answer", b_struct_t_exact_row, 476),
    ("correct_aggregate", "single_authoritative", b_struct_t_aggregate, 476),
    ("correct_join_result", "consistent_chain", b_struct_t_join, 477),
    ("threshold_comparison", "quantitative_consensus", b_struct_t_threshold, 476),
    ("multi_table_corroboration", "multi_source_corroboration", b_struct_t_multi_corro, 476),
    ("schema_doc_result_grid", "resolved_candidate_selection", b_struct_t_schema_resolve, 476),
    ("dashboard_export_direct", "expert_consensus", b_struct_t_dashboard, 476),
]
STRUCT_A_MECH = [
    ("wrong_date_partition", "temporal_mismatch", b_struct_a_wrong_date, 304),
    ("wrong_entity", "wrong_entity", b_struct_a_wrong_entity, 303),
    ("wrong_region_filter", "wrong_entity", b_struct_a_wrong_region, 303),
    ("wrong_metric_column", "wrong_specificity", b_struct_a_wrong_metric, 303),
    ("missing_result_grid", "missing_execution_result", b_struct_a_missing_grid, 303),
    ("empty_result", "evidence_absent", b_struct_a_empty_result, 303),
    ("stale_snapshot", "version_build_mismatch", b_struct_a_stale_snapshot, 303),
    ("aggregate_grain_mismatch", "wrong_specificity", b_struct_a_grain_mismatch, 303),
    ("sql_without_execution", "missing_execution_result", b_struct_a_sql_no_grid, 303),
    ("schema_no_values", "too_general", b_struct_a_schema_no_values, 303),
    ("partial_table_slice", "partial_overlap", b_struct_a_partial_slice, 303),
]
STRUCT_D_MECH = [
    ("same_metric_diff_values", "numerical_conflict", b_struct_d_same_metric_diff, 417),
    ("source_table_vs_dashboard", "authority_conflict", b_struct_d_table_dashboard, 417),
    ("cohort_definition_conflict", "definitional_conflict", b_struct_d_cohort_def, 417),
    ("job_status_conflict", "authority_status_conflict", b_struct_d_job_status, 417),
    ("pass_fail_contradiction", "verdict_conflict", b_struct_d_pass_fail, 417),
    ("same_id_incompatible_state", "factual_contradiction", b_struct_d_same_id_states, 416),
    ("stale_vs_current_snapshot", "temporal_conflict", b_struct_d_stale_vs_current, 416),
    ("agg_total_vs_rows", "scope_conflict", b_struct_d_total_vs_rows, 416),
]

# ---------------------------------------------------------------------------
# Code spec tables
# ---------------------------------------------------------------------------
CODE_T_MECH = [
    ("exact_function_answer", "direct_answer", b_code_t_exact_function, 476),
    ("test_proves_behavior", "multi_source_corroboration", b_code_t_test_proves, 476),
    ("config_sets_behavior", "quantitative_consensus", b_code_t_config_sets, 477),
    ("stack_trace_resolves_line", "resolved_candidate_selection", b_code_t_stack_trace_line, 476),
    ("docs_and_impl_agree", "expert_consensus", b_code_t_docs_impl_agree, 476),
    ("api_route_direct", "single_authoritative", b_code_t_api_route, 476),
    ("type_iface_resolves", "consistent_chain", b_code_t_type_iface, 476),
]
CODE_A_MECH = [
    ("missing_relevant_file", "evidence_absent", b_code_a_missing_file, 334),
    ("wrong_version_api", "version_build_mismatch", b_code_a_wrong_version, 334),
    ("incomplete_snippet", "partial_overlap", b_code_a_incomplete_snippet, 334),
    ("impl_no_test", "missing_execution_result", b_code_a_impl_no_test, 334),
    ("docs_no_code", "too_general", b_code_a_docs_no_code, 333),
    ("ambiguous_name_collision", "wrong_entity", b_code_a_ambiguous_name, 333),
    ("config_wrong_env", "temporal_mismatch", b_code_a_wrong_env_config, 333),
    ("trace_no_root_line", "missing_execution_result", b_code_a_trace_no_root, 333),
    ("dep_docs_too_general", "partial_overlap", b_code_a_dep_docs_insuff, 333),
    ("client_present_server_missing", "wrong_specificity", b_code_a_client_no_server, 333),
]
CODE_D_MECH = [
    ("code_vs_docs", "factual_contradiction", b_code_d_doc_vs_code, 371),
    ("test_vs_impl", "verdict_conflict", b_code_d_test_vs_impl, 371),
    ("two_files_defaults", "numerical_conflict", b_code_d_two_files_defaults, 371),
    ("changelog_vs_code", "temporal_conflict", b_code_d_changelog_vs_code, 370),
    ("type_vs_runtime", "definitional_conflict", b_code_d_types_vs_runtime, 370),
    ("stale_client_vs_server", "authority_conflict", b_code_d_stale_client_vs_server, 370),
    ("config_vs_runtime_guard", "authority_status_conflict", b_code_d_config_runtime_guard, 370),
    ("security_vs_middleware", "scope_conflict", b_code_d_security_vs_middleware, 370),
    ("ci_vs_pkg_script", "factual_contradiction", b_code_d_ci_vs_pkg, 370),
]


def _domain_cycle(domains: list[str], idx: int) -> str:
    return domains[idx % len(domains)]


def _difficulty_cycle(idx: int) -> str:
    return DIFFICULTY_CYCLE[idx % len(DIFFICULTY_CYCLE)]


def _gen_modality(modality: str, mech_table: list[tuple], domains: list[str], with_serialization: bool, start_idx: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    g = start_idx
    for mech, pattern, builder, count in mech_table:
        for i in range(count):
            domain = _domain_cycle(domains, g + i * 3 + 1)
            difficulty = _difficulty_cycle(g + i)
            serialization = _serial_cycle(g + i) if with_serialization else None
            ctx = RowCtx(
                seq=i,
                domain=domain,
                difficulty=difficulty,
                serialization=serialization or "n/a",
                label=PATTERN_CLASS[pattern],
                mechanism=mech,
                pattern=pattern,
            )
            row = builder(ctx)
            row["id"] = f"sdgp_v8_modality_{modality}_{g:05d}"
            rows.append(row)
            g += 1
    return rows


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_batches(workspace: Path, rows: list[dict[str, Any]]) -> list[Path]:
    bdir = workspace / "batches"
    bdir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    n_batches = (len(rows) + BATCH_SIZE - 1) // BATCH_SIZE
    for b in range(n_batches):
        batch = rows[b * BATCH_SIZE : (b + 1) * BATCH_SIZE]
        p = bdir / f"batch_{b + 1:04d}.jsonl"
        with p.open("w", encoding="utf-8", newline="\n") as fh:
            for row in batch:
                fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        paths.append(p)
    return paths


def coverage_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_label: dict[str, int] = {}
    by_pattern: dict[str, int] = {}
    by_domain: dict[str, int] = {}
    by_difficulty: dict[str, int] = {}
    by_mechanism: dict[str, int] = {}
    by_serialization: dict[str, int] = {}
    by_pattern_label: dict[str, dict[str, int]] = {}
    for r in rows:
        cls = r["governance"]["classification"]
        pat = r["taxonomy"]["pattern"]
        dom = r["routing"]["expert_fired"]
        dif = r["meta"]["difficulty"]
        mech = r["meta"].get("mechanism", "?")
        ser = r["meta"].get("serialization")
        by_label[cls] = by_label.get(cls, 0) + 1
        by_pattern[pat] = by_pattern.get(pat, 0) + 1
        by_domain[dom] = by_domain.get(dom, 0) + 1
        by_difficulty[dif] = by_difficulty.get(dif, 0) + 1
        by_mechanism[mech] = by_mechanism.get(mech, 0) + 1
        if ser is not None:
            by_serialization[ser] = by_serialization.get(ser, 0) + 1
        by_pattern_label.setdefault(pat, {}).setdefault(cls, 0)
        by_pattern_label[pat][cls] += 1
    return {
        "total_rows": len(rows),
        "by_label": by_label,
        "by_pattern": by_pattern,
        "by_pattern_and_label": by_pattern_label,
        "by_domain": by_domain,
        "by_difficulty": by_difficulty,
        "by_mechanism": by_mechanism,
        "by_serialization": by_serialization,
    }


def write_workspace(
    workspace: Path,
    rows: list[dict[str, Any]],
    *,
    modality: str,
    description: str,
) -> dict[str, Any]:
    workspace.mkdir(parents=True, exist_ok=True)
    write_jsonl(workspace / "cases.jsonl", rows)
    batch_paths = write_batches(workspace, rows)
    cov = coverage_report(rows)
    manifest = {
        "name": f"fitz-gov-modality-{modality}-candidate-v1",
        "version": VERSION,
        "modality": modality,
        "dataset_version": DATASET_VERSION,
        "row_shape": "sdgp_v8",
        "rows": len(rows),
        "label_counts": cov["by_label"],
        "batches": [str(p.relative_to(workspace).as_posix()) for p in batch_paths],
        "description": description,
        "files": ["cases.jsonl", "manifest.json", "coverage_report.json",
                  "validation_report.json", "candidate_taxonomy_gaps.json", "README.md"],
        "build_ts": BUILD_TS,
        "provider": PROVIDER,
    }
    (workspace / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (workspace / "coverage_report.json").write_text(
        json.dumps(cov, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> int:
    # structured: TRUSTWORTHY 3333 + ABSTAIN 3334 + DISPUTED 3333
    s_rows: list[dict[str, Any]] = []
    s_rows += _gen_modality("structured", STRUCT_T_MECH, STRUCTURED_DOMAINS, with_serialization=True, start_idx=0)
    s_rows += _gen_modality("structured", STRUCT_A_MECH, STRUCTURED_DOMAINS, with_serialization=True, start_idx=len(s_rows))
    s_rows += _gen_modality("structured", STRUCT_D_MECH, STRUCTURED_DOMAINS, with_serialization=True, start_idx=len(s_rows))

    c_rows: list[dict[str, Any]] = []
    c_rows += _gen_modality("code", CODE_T_MECH, CODE_DOMAINS, with_serialization=False, start_idx=0)
    c_rows += _gen_modality("code", CODE_A_MECH, CODE_DOMAINS, with_serialization=False, start_idx=len(c_rows))
    c_rows += _gen_modality("code", CODE_D_MECH, CODE_DOMAINS, with_serialization=False, start_idx=len(c_rows))

    assert len(s_rows) == 10000, f"structured row count {len(s_rows)} != 10000"
    assert len(c_rows) == 10000, f"code row count {len(c_rows)} != 10000"

    write_workspace(
        STRUCTURED_WORKSPACE, s_rows, modality="structured",
        description=(
            "Candidate SDGP V8 rows on structured-data evidence. "
            "Not merged into the active vault; not published. Each row keeps the current "
            "V8 SDGP shape and the canonical V8 taxonomy.pattern set."
        ),
    )
    write_workspace(
        CODE_WORKSPACE, c_rows, modality="code",
        description=(
            "Candidate SDGP V8 rows on code evidence. Not merged into the active vault; "
            "not published. Each row keeps the current V8 SDGP shape and the canonical V8 "
            "taxonomy.pattern set."
        ),
    )
    print(f"Wrote {len(s_rows)} structured candidate rows to {STRUCTURED_WORKSPACE}")
    print(f"Wrote {len(c_rows)} code candidate rows to {CODE_WORKSPACE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
