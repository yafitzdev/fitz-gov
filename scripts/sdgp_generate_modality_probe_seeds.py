"""Generate tiny structured/code SDGP modality-probe seed datasets.

These are not merged into the active V8 vault and are not a Hugging Face export
contract. They are local comparison seeds that keep the current SDGP row shape
while probing whether future pyrrho variants need modality-specific governance.

Run from repo root:
    python scripts/sdgp_generate_modality_probe_seeds.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fitz_gov.sdgp.taxonomy import PATTERN_DESCRIPTIONS, TaxonomyPattern

OUT_ROOT = Path("data/modality_probes")
DATASET_VERSION = "v8"
VERSION = "fitz-gov-modality-probe-0.1"

CLASS_BY_PATTERN = {
    "direct_answer": "TRUSTWORTHY",
    "single_authoritative": "TRUSTWORTHY",
    "consistent_chain": "TRUSTWORTHY",
    "quantitative_consensus": "TRUSTWORTHY",
    "resolved_candidate_selection": "TRUSTWORTHY",
    "factual_contradiction": "DISPUTED",
    "numerical_conflict": "DISPUTED",
    "scope_conflict": "DISPUTED",
    "verdict_conflict": "DISPUTED",
    "authority_status_conflict": "DISPUTED",
    "evidence_absent": "ABSTAIN",
    "missing_execution_result": "ABSTAIN",
    "partial_overlap": "ABSTAIN",
    "version_build_mismatch": "ABSTAIN",
    "wrong_entity": "ABSTAIN",
    "wrong_specificity": "ABSTAIN",
}


def _scores(cls: str) -> dict[str, Any]:
    if cls == "TRUSTWORTHY":
        return {
            "abstain": 0.06,
            "disputed": 0.07,
            "trustworthy": 0.87,
            "confidence": 0.87,
            "grounding": 0.91,
            "conflict_density": 0.08,
            "evidence_sufficiency": 0.9,
            "nearest_class": "ABSTAIN",
            "distance": 0.78,
            "domain_familiarity": 0.86,
            "false_trustworthy_risk": 0.08,
            "hallucination_pressure": 0.14,
            "retrieval_retry_value": 0.18,
            "human_escalation_score": 0.16,
            "query_evidence_alignment": 0.93,
            "answer_coverage": 0.9,
            "evidence_bias_score": 0.12,
        }
    if cls == "DISPUTED":
        return {
            "abstain": 0.08,
            "disputed": 0.84,
            "trustworthy": 0.08,
            "confidence": 0.84,
            "grounding": 0.64,
            "conflict_density": 0.8,
            "evidence_sufficiency": 0.58,
            "nearest_class": "TRUSTWORTHY",
            "distance": 0.75,
            "domain_familiarity": 0.82,
            "false_trustworthy_risk": 0.58,
            "hallucination_pressure": 0.32,
            "retrieval_retry_value": 0.5,
            "human_escalation_score": 0.72,
            "query_evidence_alignment": 0.85,
            "answer_coverage": 0.56,
            "evidence_bias_score": 0.38,
        }
    return {
        "abstain": 0.84,
        "disputed": 0.08,
        "trustworthy": 0.08,
        "confidence": 0.84,
        "grounding": 0.46,
        "conflict_density": 0.12,
        "evidence_sufficiency": 0.2,
        "nearest_class": "TRUSTWORTHY",
        "distance": 0.76,
        "domain_familiarity": 0.8,
        "false_trustworthy_risk": 0.62,
        "hallucination_pressure": 0.74,
        "retrieval_retry_value": 0.82,
        "human_escalation_score": 0.54,
        "query_evidence_alignment": 0.34,
        "answer_coverage": 0.18,
        "evidence_bias_score": 0.22,
    }


def _category(cls: str, direct: bool = False) -> str:
    if cls == "TRUSTWORTHY":
        return "trustworthy_direct" if direct else "trustworthy_hedged"
    if cls == "DISPUTED":
        return "dispute"
    return "abstention"


def _context(
    idx: int,
    text: str,
    *,
    authority_score: float,
    authority_signal: str,
    summary: str,
    relevance: float = 0.92,
    boundary: float = 0.86,
    anchor: str = "modality probe seed",
    stale: str = "low",
) -> dict[str, Any]:
    return {
        "id": f"ctx_{idx:03d}",
        "text": text,
        "authority_score": authority_score,
        "authority_signal": authority_signal,
        "temporality": {
            "is_time_sensitive": True,
            "anchor_period": anchor,
            "staleness_risk": stale,
        },
        "summary": summary,
        "relevance_to_query": relevance,
        "boundary_quality": boundary,
    }


def _case(
    *,
    modality: str,
    slug: str,
    pattern: str,
    domain: str,
    difficulty: str,
    query: str,
    contexts: list[dict[str, Any]],
    required_elements: list[str],
    forbidden_claims: list[str],
    near_miss_reason: str,
    gold_answer: str | None = None,
    direct: bool = False,
) -> dict[str, Any]:
    cls = CLASS_BY_PATTERN[pattern]
    scores = _scores(cls)
    case: dict[str, Any] = {
        "id": f"sdgp_{modality}_seed_{slug}",
        "version": VERSION,
        "input": {
            "query": query,
            "query_rewritten": query,
            "contexts": contexts,
        },
        "governance": {
            "classification": cls,
            "abstain": scores["abstain"],
            "disputed": scores["disputed"],
            "trustworthy": scores["trustworthy"],
            "confidence": scores["confidence"],
            "grounding": scores["grounding"],
            "conflict_density": scores["conflict_density"],
            "evidence_sufficiency": scores["evidence_sufficiency"],
            "boundary_proximity": {
                "nearest_class": scores["nearest_class"],
                "distance": scores["distance"],
            },
            "domain_familiarity": scores["domain_familiarity"],
            "false_trustworthy_risk": scores["false_trustworthy_risk"],
            "hallucination_pressure": scores["hallucination_pressure"],
            "retrieval_retry_value": scores["retrieval_retry_value"],
            "human_escalation_score": scores["human_escalation_score"],
            "query_evidence_alignment": scores["query_evidence_alignment"],
            "answer_coverage": scores["answer_coverage"],
            "evidence_bias_score": scores["evidence_bias_score"],
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
            "forbidden_elements": [],
        },
        "routing": {
            "expert_fired": domain,
            "secondary_expert": "conflict_detection" if cls == "DISPUTED" else None,
            "routing_confidence": 0.88,
        },
        "meta": {
            "dataset_version": DATASET_VERSION,
            "difficulty": difficulty,
            "category": _category(cls, direct=direct),
            "confidence_level": "high" if difficulty == "easy" else "medium",
            "near_miss_class": scores["nearest_class"],
            "near_miss_reason": near_miss_reason,
        },
        "_vault": {
            "added_at": "2026-05-27T00:00:00Z",
            "provider": "codex",
            "provider_version": "gpt-5",
            "prompt_version": "modality-probe-seed-v0.1",
            "batch_id": f"{modality}_seed_10",
            "last_modified_at": "2026-05-27T00:00:00Z",
            "revisions": 1,
        },
    }
    if len(contexts) >= 2:
        case["input"]["evidence_chain"] = {
            "order": [c["id"] for c in contexts],
            "reasoning": "Read the retrieved records together because the governance decision depends on whether they answer, conflict, or omit the requested fact.",
        }
    if cls == "TRUSTWORTHY":
        answer = gold_answer or required_elements[0]
        case["meta"]["grounding_targets"] = {
            "gold_answer": answer,
            "sentences": [
                {
                    "text": answer,
                    "attributions": [contexts[0]["id"]],
                }
            ],
        }
    return case


def structured_cases() -> list[dict[str, Any]]:
    return [
        _case(
            modality="structured",
            slug="direct_returns_warehouse",
            pattern="direct_answer",
            domain="economics_finance",
            difficulty="easy",
            query="Which warehouse recorded 184 returns in the Q4 returns table?",
            contexts=[
                _context(
                    1,
                    "warehouse_returns_q4.csv rows: warehouse=North-7, returns=184; warehouse=South-2, returns=119; warehouse=West-4, returns=203.",
                    authority_score=0.94,
                    authority_signal="warehouse_ops_export",
                    summary="The Q4 table directly maps 184 returns to North-7.",
                )
            ],
            required_elements=["North-7"],
            forbidden_claims=["South-2 recorded 184 returns", "West-4 recorded 184 returns"],
            near_miss_reason="A model could pick an adjacent row instead of matching the exact return count.",
            gold_answer="North-7 recorded 184 returns.",
            direct=True,
        ),
        _case(
            modality="structured",
            slug="net_revenue_consensus",
            pattern="quantitative_consensus",
            domain="economics_finance",
            difficulty="medium",
            query="What was March net revenue after refunds?",
            contexts=[
                _context(
                    1,
                    "finance_daily_rollup table: month=2026-03, gross_revenue=136900, refunds=8500, net_revenue=128400.",
                    authority_score=0.91,
                    authority_signal="finance_primary_export",
                    summary="The finance rollup reports March net revenue as 128400.",
                ),
                _context(
                    2,
                    "BI reconciliation extract: period=2026-03, metric=net_revenue_after_refunds, value=128400, currency=USD.",
                    authority_score=0.88,
                    authority_signal="bi_reconciliation",
                    summary="The BI reconciliation independently reports 128400.",
                ),
            ],
            required_elements=["128400", "March"],
            forbidden_claims=["136900 was net revenue", "8500 was net revenue"],
            near_miss_reason="The table includes gross and refund values, but both sources agree on the net value.",
            gold_answer="March net revenue after refunds was 128400 USD.",
        ),
        _case(
            modality="structured",
            slug="active_paid_eu_accounts",
            pattern="consistent_chain",
            domain="technology_computing",
            difficulty="medium",
            query="How many active paid EU accounts are in the April account snapshot?",
            contexts=[
                _context(
                    1,
                    "account_snapshot schema: columns account_id, status, plan_type, region, snapshot_month. Valid paid plans are pro and enterprise.",
                    authority_score=0.86,
                    authority_signal="schema_registry",
                    summary="The schema defines status, plan, region, and snapshot fields.",
                ),
                _context(
                    2,
                    "Query result for snapshot_month=2026-04 where status='active', region='EU', plan_type in ('pro','enterprise'): count=342.",
                    authority_score=0.93,
                    authority_signal="warehouse_query_result",
                    summary="The filtered result returns 342 active paid EU accounts.",
                ),
            ],
            required_elements=["342"],
            forbidden_claims=["all EU accounts total 342", "free accounts were included"],
            near_miss_reason="The answer depends on chaining schema semantics with the filtered aggregate result.",
            gold_answer="There were 342 active paid EU accounts in the April snapshot.",
        ),
        _case(
            modality="structured",
            slug="gross_margin_conflict",
            pattern="numerical_conflict",
            domain="economics_finance",
            difficulty="medium",
            query="What was Q2 gross margin for the services segment?",
            contexts=[
                _context(
                    1,
                    "finance_export_services_q2: segment=services, gross_margin_pct=42.1, reporting_basis=management.",
                    authority_score=0.88,
                    authority_signal="finance_export",
                    summary="The finance export reports 42.1 percent.",
                ),
                _context(
                    2,
                    "board_pack_q2_services table: segment=services, gross_margin_pct=39.8, reporting_basis=management.",
                    authority_score=0.9,
                    authority_signal="board_pack",
                    summary="The board pack reports 39.8 percent for the same segment and basis.",
                ),
            ],
            required_elements=[],
            forbidden_claims=["Q2 gross margin was 42.1", "Q2 gross margin was 39.8"],
            near_miss_reason="Both rows appear authoritative and use the same segment and basis but disagree numerically.",
        ),
        _case(
            modality="structured",
            slug="reconciliation_verdict_conflict",
            pattern="verdict_conflict",
            domain="technology_computing",
            difficulty="medium",
            query="Did the May invoice reconciliation pass?",
            contexts=[
                _context(
                    1,
                    "recon_runs table row: run_id=may-invoice-2026, status=PASS, failed_rows=0, completed_at=2026-05-03T04:10Z.",
                    authority_score=0.82,
                    authority_signal="scheduler_status_table",
                    summary="The scheduler status says the reconciliation passed.",
                ),
                _context(
                    2,
                    "finance_recon_audit row: run_id=may-invoice-2026, final_verdict=FAIL, discrepancy_count=17, approved_for_close=false.",
                    authority_score=0.94,
                    authority_signal="audit_table",
                    summary="The audit table says the same run failed.",
                ),
            ],
            required_elements=[],
            forbidden_claims=["the reconciliation passed", "the reconciliation failed without noting the conflict"],
            near_miss_reason="The retrieved tables give incompatible final statuses for the same run.",
        ),
        _case(
            modality="structured",
            slug="regional_global_scope_conflict",
            pattern="scope_conflict",
            domain="economics_finance",
            difficulty="hard",
            query="What was global enterprise churn in April?",
            contexts=[
                _context(
                    1,
                    "enterprise_churn_april table: scope=EMEA, churn_rate=3.2%, account_tier=enterprise.",
                    authority_score=0.87,
                    authority_signal="regional_metric_table",
                    summary="One table reports EMEA enterprise churn.",
                ),
                _context(
                    2,
                    "enterprise_churn_april table: scope=AMER, churn_rate=2.4%, account_tier=enterprise. The global aggregate row is not present.",
                    authority_score=0.87,
                    authority_signal="regional_metric_table",
                    summary="Another row reports AMER churn and says the global aggregate is absent.",
                ),
            ],
            required_elements=[],
            forbidden_claims=["global churn was 3.2%", "global churn was 2.4%"],
            near_miss_reason="Regional rows are relevant but cannot be treated as a single global answer.",
        ),
        _case(
            modality="structured",
            slug="inventory_missing_result",
            pattern="missing_execution_result",
            domain="technology_computing",
            difficulty="easy",
            query="What was the final inventory count after the nightly count job?",
            contexts=[
                _context(
                    1,
                    "inventory_count_jobs row: job_id=nightly-2026-05-10, status=STARTED, expected_partitions=12, result_table=NULL.",
                    authority_score=0.9,
                    authority_signal="job_control_table",
                    summary="The job control row shows the count job started but no result table.",
                )
            ],
            required_elements=[],
            forbidden_claims=["final inventory count was 12", "the job produced a final count"],
            near_miss_reason="The retrieved table gives setup metadata but omits the final result.",
        ),
        _case(
            modality="structured",
            slug="snapshot_version_mismatch",
            pattern="version_build_mismatch",
            domain="economics_finance",
            difficulty="easy",
            query="What was customer 7781's balance in the April 2026 snapshot?",
            contexts=[
                _context(
                    1,
                    "customer_balance_snapshot row: customer_id=7781, snapshot_month=2026-03, balance=914.22, currency=USD.",
                    authority_score=0.9,
                    authority_signal="warehouse_snapshot",
                    summary="The row is for customer 7781 but the March snapshot.",
                )
            ],
            required_elements=[],
            forbidden_claims=["April balance was 914.22"],
            near_miss_reason="The entity matches, but the retrieved snapshot month is wrong.",
        ),
        _case(
            modality="structured",
            slug="channel_revenue_wrong_specificity",
            pattern="wrong_specificity",
            domain="economics_finance",
            difficulty="medium",
            query="What was Q1 revenue broken down by channel?",
            contexts=[
                _context(
                    1,
                    "quarterly_revenue table: quarter=2026-Q1, total_revenue=4820000, currency=USD. No channel column is present in this extract.",
                    authority_score=0.88,
                    authority_signal="finance_summary_table",
                    summary="The table provides total revenue but not channel-level revenue.",
                )
            ],
            required_elements=[],
            forbidden_claims=["channel breakdown is available", "online revenue was 4820000"],
            near_miss_reason="A total is not a breakdown by channel.",
        ),
        _case(
            modality="structured",
            slug="refund_reason_absent",
            pattern="evidence_absent",
            domain="economics_finance",
            difficulty="hard",
            query="What refund reason was recorded for customer 884?",
            contexts=[
                _context(
                    1,
                    "refunds schema excerpt: columns refund_id, customer_id, amount, created_at. The reason_code column is not included in this extract.",
                    authority_score=0.76,
                    authority_signal="schema_excerpt",
                    summary="The retrieved schema excerpt does not provide any row or reason code for customer 884.",
                    relevance=0.3,
                    boundary=0.44,
                )
            ],
            required_elements=[],
            forbidden_claims=["refund reason was duplicate charge", "refund reason was customer request"],
            near_miss_reason="The retrieved evidence is a schema excerpt, not the requested customer refund row.",
        ),
    ]


def code_cases() -> list[dict[str, Any]]:
    return [
        _case(
            modality="code",
            slug="auth_missing_bearer_direct",
            pattern="direct_answer",
            domain="technology_computing",
            difficulty="easy",
            query="Does the auth middleware reject requests without a Bearer token?",
            contexts=[
                _context(
                    1,
                    "auth/middleware.py: def require_auth(req): header=req.headers.get('Authorization',''); if not header.startswith('Bearer '): return Response(status=401); return verify_token(header[7:])",
                    authority_score=0.94,
                    authority_signal="source_code",
                    summary="The middleware returns 401 when Authorization does not start with Bearer.",
                )
            ],
            required_elements=["returns 401", "without Bearer"],
            forbidden_claims=["it allows missing Bearer tokens", "it returns 403"],
            near_miss_reason="A model could confuse token verification failure with the missing-header branch.",
            gold_answer="Yes. The middleware returns 401 when the Authorization header does not start with Bearer.",
            direct=True,
        ),
        _case(
            modality="code",
            slug="cache_ttl_chain",
            pattern="consistent_chain",
            domain="technology_computing",
            difficulty="medium",
            query="What default TTL does the product cache use?",
            contexts=[
                _context(
                    1,
                    "settings.py: PRODUCT_CACHE_TTL_SECONDS = int(os.getenv('PRODUCT_CACHE_TTL_SECONDS', '300'))",
                    authority_score=0.9,
                    authority_signal="source_code",
                    summary="The setting defaults the TTL environment variable to 300.",
                ),
                _context(
                    2,
                    "catalog/cache.py: cache = TTLCache(maxsize=2048, ttl=settings.PRODUCT_CACHE_TTL_SECONDS)",
                    authority_score=0.92,
                    authority_signal="source_code",
                    summary="The product cache uses PRODUCT_CACHE_TTL_SECONDS as its TTL.",
                ),
            ],
            required_elements=["300 seconds"],
            forbidden_claims=["TTL is 2048 seconds", "TTL has no default"],
            near_miss_reason="The answer requires chaining the setting default to the cache constructor.",
            gold_answer="The product cache defaults to a TTL of 300 seconds.",
        ),
        _case(
            modality="code",
            slug="validate_user_v2_resolved",
            pattern="resolved_candidate_selection",
            domain="technology_computing",
            difficulty="medium",
            query="Which user validation function is used by the signup flow?",
            contexts=[
                _context(
                    1,
                    "validators.py: def validate_user(payload): raise DeprecatedValidator('use validate_user_v2')\ndef validate_user_v2(payload): return UserSchemaV2().load(payload)",
                    authority_score=0.9,
                    authority_signal="source_code",
                    summary="The old validator explicitly redirects to validate_user_v2.",
                ),
                _context(
                    2,
                    "signup.py: from validators import validate_user_v2\nuser = validate_user_v2(request.json)",
                    authority_score=0.95,
                    authority_signal="source_code",
                    summary="The signup flow imports and calls validate_user_v2.",
                ),
            ],
            required_elements=["validate_user_v2"],
            forbidden_claims=["validate_user is used by signup"],
            near_miss_reason="There are two candidate functions, but the source identifies the valid one.",
            gold_answer="The signup flow uses validate_user_v2.",
        ),
        _case(
            modality="code",
            slug="retry_docs_code_contradiction",
            pattern="factual_contradiction",
            domain="technology_computing",
            difficulty="medium",
            query="Are HTTP retries disabled by default?",
            contexts=[
                _context(
                    1,
                    "README.md: By default the HTTP client does not retry failed requests. Set RETRIES to enable retries.",
                    authority_score=0.72,
                    authority_signal="repo_documentation",
                    summary="The README says retries are disabled by default.",
                ),
                _context(
                    2,
                    "client.py: DEFAULT_RETRIES = 3\ndef build_session(retries=DEFAULT_RETRIES): return Retry(total=retries)",
                    authority_score=0.95,
                    authority_signal="source_code",
                    summary="The code sets the default retries to 3.",
                ),
            ],
            required_elements=[],
            forbidden_claims=["retries are disabled by default", "retries default to 3 without noting the documentation conflict"],
            near_miss_reason="Documentation and implementation directly contradict the default behavior.",
        ),
        _case(
            modality="code",
            slug="ci_pytest_verdict_conflict",
            pattern="verdict_conflict",
            domain="technology_computing",
            difficulty="easy",
            query="Did test_invoice_rounding pass in build 812?",
            contexts=[
                _context(
                    1,
                    "ci_summary.json: build=812, test=test_invoice_rounding, status=passed, duration_ms=421.",
                    authority_score=0.78,
                    authority_signal="ci_summary",
                    summary="The CI summary marks the test as passed.",
                ),
                _context(
                    2,
                    "pytest.log for build 812: FAILED tests/test_invoice.py::test_invoice_rounding - AssertionError: Decimal('10.01') != Decimal('10.00')",
                    authority_score=0.93,
                    authority_signal="raw_test_log",
                    summary="The raw pytest log marks the same test as failed.",
                ),
            ],
            required_elements=[],
            forbidden_claims=["the test passed", "the test failed without noting the conflict"],
            near_miss_reason="Two retrieved build artifacts give incompatible verdicts for the same test.",
        ),
        _case(
            modality="code",
            slug="release_blocker_status_conflict",
            pattern="authority_status_conflict",
            domain="technology_computing",
            difficulty="medium",
            query="Is BUG-417 still blocking the 2.4.0 release?",
            contexts=[
                _context(
                    1,
                    "issue_tracker.json: BUG-417 status=closed, resolution=fixed, updated=2026-05-11.",
                    authority_score=0.74,
                    authority_signal="issue_tracker",
                    summary="The issue tracker says BUG-417 is closed.",
                ),
                _context(
                    2,
                    "release_gate_2_4_0.yaml: blockers: [BUG-417]; gate_status: blocked; source_of_record: release_management",
                    authority_score=0.96,
                    authority_signal="release_gate",
                    summary="The release gate still lists BUG-417 as a blocker.",
                ),
            ],
            required_elements=[],
            forbidden_claims=["BUG-417 is not blocking", "BUG-417 is blocking without noting the closed issue"],
            near_miss_reason="A lower-authority issue status conflicts with the release gate source of record.",
        ),
        _case(
            modality="code",
            slug="migration_missing_failure_result",
            pattern="missing_execution_result",
            domain="technology_computing",
            difficulty="easy",
            query="Which migration failed in the staging deploy?",
            contexts=[
                _context(
                    1,
                    "deploy.log: 2026-05-18T02:14Z starting migrations: 20260518_add_indexes, 20260518_backfill_status. No completion or failure lines are present in the retrieved excerpt.",
                    authority_score=0.87,
                    authority_signal="deploy_log_excerpt",
                    summary="The log excerpt names migrations that started but includes no failure result.",
                )
            ],
            required_elements=[],
            forbidden_claims=["20260518_add_indexes failed", "20260518_backfill_status failed"],
            near_miss_reason="The retrieved log provides setup but not the requested failure result.",
        ),
        _case(
            modality="code",
            slug="patch_endpoint_partial_overlap",
            pattern="partial_overlap",
            domain="technology_computing",
            difficulty="medium",
            query="Does the /orders endpoint support PATCH?",
            contexts=[
                _context(
                    1,
                    "routes/orders.py: router.get('/orders', list_orders); router.post('/orders', create_order). No PATCH route appears in this file excerpt.",
                    authority_score=0.85,
                    authority_signal="source_code_excerpt",
                    summary="The excerpt shows GET and POST routes for /orders but not PATCH.",
                )
            ],
            required_elements=[],
            forbidden_claims=["/orders supports PATCH", "PATCH is explicitly unsupported"],
            near_miss_reason="The evidence overlaps with the endpoint but does not establish PATCH support or absence globally.",
        ),
        _case(
            modality="code",
            slug="sdk_version_mismatch",
            pattern="version_build_mismatch",
            domain="technology_computing",
            difficulty="hard",
            query="Does SDK 3.2.1 use exponential backoff for upload retries?",
            contexts=[
                _context(
                    1,
                    "sdk-3.1.0/docs/uploads.md: Upload retries use fixed 2 second intervals. This page applies to SDK version 3.1.0.",
                    authority_score=0.82,
                    authority_signal="versioned_docs",
                    summary="The retrieved documentation is for SDK 3.1.0, not 3.2.1.",
                )
            ],
            required_elements=[],
            forbidden_claims=["SDK 3.2.1 uses fixed 2 second intervals", "SDK 3.2.1 does not use exponential backoff"],
            near_miss_reason="The retrieved docs cover the right feature but the wrong SDK version.",
        ),
        _case(
            modality="code",
            slug="billing_checkout_wrong_entity",
            pattern="wrong_entity",
            domain="technology_computing",
            difficulty="easy",
            query="What timeout does the billing service use for invoice posting?",
            contexts=[
                _context(
                    1,
                    "checkout/config.py: PAYMENT_TIMEOUT_SECONDS = 15 # timeout for checkout payment authorization calls.",
                    authority_score=0.84,
                    authority_signal="source_code",
                    summary="The retrieved file is checkout payment configuration, not billing invoice posting.",
                )
            ],
            required_elements=[],
            forbidden_claims=["billing invoice posting timeout is 15 seconds"],
            near_miss_reason="The context is code, but it is for the checkout service rather than the billing service.",
        ),
    ]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_manifest(path: Path, *, modality: str, rows: list[dict[str, Any]]) -> None:
    counts: dict[str, int] = {}
    for row in rows:
        cls = row["governance"]["classification"]
        counts[cls] = counts.get(cls, 0) + 1
    manifest = {
        "name": f"fitz-gov-{modality}-modality-probe",
        "version": VERSION,
        "modality": modality,
        "row_shape": "sdgp_v8",
        "rows": len(rows),
        "label_counts": counts,
        "description": (
            "Tiny local SDGP seed dataset for comparing pyrrho governance behavior "
            f"on {modality} evidence. Not merged into the active V8 vault."
        ),
        "files": ["cases.jsonl"],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    datasets = {
        "structured": structured_cases(),
        "code": code_cases(),
    }
    for modality, rows in datasets.items():
        out_dir = OUT_ROOT / modality
        write_jsonl(out_dir / "cases.jsonl", rows)
        write_manifest(out_dir / "manifest.json", modality=modality, rows=rows)
    (OUT_ROOT / "unstructured").mkdir(parents=True, exist_ok=True)
    (OUT_ROOT / "unstructured" / "manifest.json").write_text(
        json.dumps(
            {
                "name": "fitz-gov-unstructured-v8",
                "version": "fitz-gov-8.0",
                "modality": "unstructured",
                "row_shape": "sdgp_v8",
                "rows": 24592,
                "description": (
                    "Canonical unstructured-text governance dataset. Distributed on "
                    "Hugging Face as yafitzdev/fitz-gov, default config v8."
                ),
                "huggingface": {
                    "repo_id": "yafitzdev/fitz-gov",
                    "config": "v8",
                    "revision": "v8.0.0",
                    "splits": {
                        "train": 19674,
                        "validation": 2459,
                        "test": 2459,
                    },
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote modality probes under {OUT_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
