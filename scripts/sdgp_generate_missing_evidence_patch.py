"""Generate a candidate-only missing-evidence modality patch.

This targeted patch focuses on the two remaining local-control OOD weaknesses
after the retry-limit code patch:

- code diff-context rows that omit a requested specific field
- structured rows where query/setup metadata is present but the result value is
  missing

It also adds TRUSTWORTHY and DISPUTED controls for both surfaces so the patch is
label-balanced. It does not merge rows into the active vault or publish
anything.

Run from the fitz-gov repo root:
    python scripts/sdgp_generate_missing_evidence_patch.py
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fitz_gov.sdgp.checker import Checker

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sdgp_generate_modality_candidate_packs as base  # noqa: E402

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


VERSION = "fitz-gov-modality-missing-evidence-patch-0.1"
BUILD_TS = "2026-05-29T11:30:00Z"
PROVIDER = "codex"
PROVIDER_VERSION = "gpt-5-codex"
PROMPT_VERSION = "modality-missing-evidence-patch-0.1"
BATCH_ID = "modality_missing_evidence_patch_v1_20260529"
DEFAULT_OUT = Path("data/_workspaces/handoff/modality_missing_evidence_patch_v1_20260529")
BATCH_SIZE = 60
ROWS_PER_FAMILY = 60

CODE_SERIALIZATION = "diff_context"
STRUCT_SERIALIZATIONS = ("markdown_table", "csv_extract", "evidence_packet")
DIFFICULTIES = ("easy", "medium", "hard")
CODE_DOMAINS = (
    "technology_computing",
    "technology_computing",
    "technology_computing",
    "economics_finance",
    "science_medicine",
)
STRUCT_DOMAINS = (
    "economics_finance",
    "technology_computing",
    "science_medicine",
    "law_policy",
    "history_geography",
    "culture_society",
    "general_commonsense",
)
FEATURES = (
    "refund",
    "invoice",
    "payment",
    "shipment",
    "subscription",
    "claim",
    "enrollment",
    "payout",
    "settlement",
    "notification",
    "catalog",
    "profile",
    "session",
    "ledger",
    "report",
)
STRUCT_METRICS = (
    "average refund processing time",
    "net revenue",
    "approval latency",
    "failed payment count",
    "claim closure days",
    "shipment exception rate",
    "subscription churn rate",
    "invoice adjustment amount",
)


@dataclass(frozen=True)
class CodeSource:
    path: str
    language: str
    content: str
    summary: str
    authority_signal: str = "source_code"
    authority_score: float = 0.92


@dataclass(frozen=True)
class StructuredSource:
    title: str
    filters: str
    columns: list[str]
    rows: list[list[str]]
    notes: str
    authority_signal: str = "warehouse_result"
    authority_score: float = 0.9


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--rows-per-family", type=int, default=ROWS_PER_FAMILY)
    return parser.parse_args()


def code_feature(seq: int) -> str:
    root = FEATURES[seq % len(FEATURES)]
    suffix = seq // len(FEATURES)
    return root if suffix == 0 else f"{root}_{suffix}"


def fn_name(seq: int) -> str:
    return f"{code_feature(seq)}_order"


def audit_event(seq: int) -> str:
    return f"{code_feature(seq)}.completed.v{(seq % 4) + 1}"


def render_code_diff(source: CodeSource) -> str:
    content = source.content.strip("\n")
    diff = "\n".join(f"+ {line}" if line.strip() else "+" for line in content.splitlines())
    return (
        "Retrieved diff context\n"
        f"+++ b/{source.path}\n"
        "@@ relevant excerpt @@\n"
        f"{diff}\n"
        f"review_note={source.summary}"
    )


def code_contexts(sources: list[CodeSource]) -> list[dict[str, Any]]:
    return [
        base._make_context(
            idx,
            render_code_diff(source),
            authority_score=source.authority_score,
            authority_signal=source.authority_signal,
            summary=source.summary,
            relevance=0.9,
            boundary=0.86,
            anchor="code missing-evidence patch",
        )
        for idx, source in enumerate(sources, start=1)
    ]


def markdown_table(columns: list[str], rows: list[list[str]]) -> str:
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    body = ["| " + " | ".join(str(v) for v in row) + " |" for row in rows]
    return "\n".join([header, sep, *body])


def csv_table(columns: list[str], rows: list[list[str]]) -> str:
    return "\n".join([",".join(columns), *[",".join(str(v) for v in row) for row in rows]])


def packet_rows(columns: list[str], rows: list[list[str]]) -> str:
    rendered = []
    for idx, row in enumerate(rows, start=1):
        fields = "; ".join(f"{col}={value}" for col, value in zip(columns, row, strict=True))
        rendered.append(f"row_{idx}: {fields}")
    return "\n".join(rendered)


def render_structured(source: StructuredSource, serialization: str) -> str:
    if serialization == "markdown_table":
        return (
            f"Retrieved table: {source.title}\n"
            f"Applied filters: {source.filters}\n"
            f"{markdown_table(source.columns, source.rows)}\n"
            f"Note: {source.notes}"
        )
    if serialization == "csv_extract":
        return (
            f"CSV extract from {source.title}\n"
            f"# applied_filters: {source.filters}\n"
            f"{csv_table(source.columns, source.rows)}\n"
            f"# note: {source.notes}"
        )
    if serialization == "evidence_packet":
        return (
            "Structured evidence packet\n"
            f"table={source.title}\n"
            f"filters={source.filters}\n"
            f"columns={', '.join(source.columns)}\n"
            f"{packet_rows(source.columns, source.rows)}\n"
            f"interpretation_note={source.notes}"
        )
    raise ValueError(f"unknown structured serialization: {serialization}")


def structured_contexts(
    sources: list[StructuredSource],
    serialization: str,
) -> list[dict[str, Any]]:
    return [
        base._make_context(
            idx,
            render_structured(source, serialization),
            authority_score=source.authority_score,
            authority_signal=source.authority_signal,
            summary=source.notes,
            relevance=0.9,
            boundary=0.86,
            anchor="structured missing-evidence patch",
        )
        for idx, source in enumerate(sources, start=1)
    ]


def finalize_row(
    row: dict[str, Any],
    *,
    case_id: str,
    serialization: str,
) -> dict[str, Any]:
    row["id"] = case_id
    row["version"] = VERSION
    row["meta"]["serialization"] = serialization
    row["_vault"] = {
        "added_at": BUILD_TS,
        "provider": PROVIDER,
        "provider_version": PROVIDER_VERSION,
        "prompt_version": PROMPT_VERSION,
        "batch_id": BATCH_ID,
        "last_modified_at": BUILD_TS,
        "revisions": 1,
    }
    return row


def code_row_base(
    *,
    pattern: str,
    domain: str,
    difficulty: str,
    query: str,
    sources: list[CodeSource],
    required_elements: list[str],
    forbidden_claims: list[str],
    near_miss_reason: str,
    mechanism: str,
    gold_answer: str | None = None,
    grounding_attributions: list[str] | None = None,
) -> dict[str, Any]:
    return base.build_row(
        modality="code",
        case_id="",
        pattern=pattern,
        domain=domain,
        difficulty=difficulty,
        query=query,
        query_rewritten=None,
        contexts=code_contexts(sources),
        required_elements=required_elements,
        forbidden_claims=forbidden_claims,
        forbidden_elements=[],
        near_miss_reason=near_miss_reason,
        mechanism=mechanism,
        serialization=CODE_SERIALIZATION,
        gold_answer=gold_answer,
        grounding_attributions=grounding_attributions,
        direct=pattern == "direct_answer",
    )


def structured_row_base(
    *,
    pattern: str,
    domain: str,
    difficulty: str,
    serialization: str,
    query: str,
    sources: list[StructuredSource],
    required_elements: list[str],
    forbidden_claims: list[str],
    near_miss_reason: str,
    mechanism: str,
    gold_answer: str | None = None,
    grounding_attributions: list[str] | None = None,
) -> dict[str, Any]:
    return base.build_row(
        modality="structured",
        case_id="",
        pattern=pattern,
        domain=domain,
        difficulty=difficulty,
        query=query,
        query_rewritten=None,
        contexts=structured_contexts(sources, serialization),
        required_elements=required_elements,
        forbidden_claims=forbidden_claims,
        forbidden_elements=[],
        near_miss_reason=near_miss_reason,
        mechanism=mechanism,
        serialization=serialization,
        gold_answer=gold_answer,
        grounding_attributions=grounding_attributions,
        direct=pattern == "direct_answer",
    )


def build_code_abstain(seq: int, domain: str, difficulty: str) -> dict[str, Any]:
    fn = fn_name(seq)
    code = f"""
def {fn}(order_id: str, cents: int) -> Refund:
    order = Order.get(order_id)
    gateway.refund(payment_id=order.payment_id, amount_cents=cents)
    refund = Refund.create(order_id=order_id, amount_cents=cents)
    return refund
"""
    query = f"Which audit event name does `{fn}` write?"
    row = code_row_base(
        pattern="evidence_absent",
        domain=domain,
        difficulty=difficulty,
        query=query,
        sources=[
            CodeSource(
                path=f"services/{code_feature(seq)}/refunds.py",
                language="python",
                content=code,
                summary="The function body is present, but no audit event name is logged or emitted.",
            )
        ],
        required_elements=[],
        forbidden_claims=[f"`{fn}` writes a specific audit event name"],
        near_miss_reason="The retrieved diff shows the function but omits the requested audit event field.",
        mechanism="missing_specific_field",
    )
    return row


def build_code_trustworthy(seq: int, domain: str, difficulty: str) -> dict[str, Any]:
    fn = fn_name(seq)
    event = audit_event(seq)
    code = f"""
def {fn}(order_id: str, cents: int) -> Refund:
    order = Order.get(order_id)
    gateway.refund(payment_id=order.payment_id, amount_cents=cents)
    refund = Refund.create(order_id=order_id, amount_cents=cents)
    audit.write("{event}", order_id=order_id, refund_id=refund.id)
    return refund
"""
    query = f"Which audit event name does `{fn}` write?"
    row = code_row_base(
        pattern="direct_answer",
        domain=domain,
        difficulty=difficulty,
        query=query,
        sources=[
            CodeSource(
                path=f"services/{code_feature(seq)}/refunds.py",
                language="python",
                content=code,
                summary=f"The function explicitly writes audit event {event}.",
            )
        ],
        required_elements=[event],
        forbidden_claims=[f"`{fn}` omits audit logging"],
        near_miss_reason="The exact audit event appears in the retrieved diff.",
        mechanism="exact_symbol_support",
        gold_answer=event,
        grounding_attributions=["ctx_001"],
    )
    return row


def build_code_disputed(seq: int, domain: str, difficulty: str) -> dict[str, Any]:
    fn = fn_name(seq)
    code_event = audit_event(seq)
    registry_event = f"{code_feature(seq)}.audit.v{(seq % 3) + 7}"
    code = f"""
def {fn}(order_id: str, cents: int) -> Refund:
    refund = gateway.refund_order(order_id=order_id, amount_cents=cents)
    audit.write("{code_event}", order_id=order_id, refund_id=refund.id)
    return refund
"""
    registry = f"""
audit_events:
  {fn}: "{registry_event}"
  owner: governance-audit
"""
    query = f"Which audit event name does `{fn}` write?"
    row = code_row_base(
        pattern="factual_contradiction",
        domain=domain,
        difficulty=difficulty,
        query=query,
        sources=[
            CodeSource(
                path=f"services/{code_feature(seq)}/refunds.py",
                language="python",
                content=code,
                summary=f"Implementation writes {code_event}.",
            ),
            CodeSource(
                path=f"config/audit/{code_feature(seq)}.yaml",
                language="yaml",
                content=registry,
                summary=f"Audit registry maps the same function to {registry_event}.",
                authority_signal="audit_registry",
                authority_score=0.9,
            ),
        ],
        required_elements=[code_event, registry_event],
        forbidden_claims=[f"the evidence agrees on `{fn}` audit event"],
        near_miss_reason="Two retrieved artifacts name different audit events for the same function.",
        mechanism="docs_code_conflict",
    )
    return row


def metric(seq: int) -> str:
    return STRUCT_METRICS[seq % len(STRUCT_METRICS)]


def account(seq: int) -> str:
    return f"account_{1000 + seq}"


def value(seq: int) -> str:
    return f"{12 + (seq % 17)}.{seq % 10}"


def build_struct_abstain(
    seq: int,
    domain: str,
    difficulty: str,
    serialization: str,
) -> dict[str, Any]:
    metric_name = metric(seq)
    acct = account(seq)
    source = StructuredSource(
        title="warehouse.query_history.saved_sql",
        filters=f"account={acct}; month=2026-04; metric={metric_name}",
        columns=["query_id", "sql_text", "referenced_tables", "requested_metric"],
        rows=[
            [
                f"q_{seq:04d}",
                f"SELECT AVG(value) FROM metric_results WHERE account='{acct}' AND metric='{metric_name}'",
                "metric_results",
                metric_name,
            ]
        ],
        notes="Only the saved SQL text and referenced table are retrieved; no executed result grid or metric value is present.",
        authority_signal="query_history",
        authority_score=0.82,
    )
    query = f"What was {acct}'s {metric_name} in April 2026?"
    row = structured_row_base(
        pattern="missing_execution_result",
        domain=domain,
        difficulty=difficulty,
        serialization=serialization,
        query=query,
        sources=[source],
        required_elements=[],
        forbidden_claims=[f"{acct}'s {metric_name} was {value(seq)}"],
        near_miss_reason="The retrieved evidence contains query setup only, not the executed result value.",
        mechanism="missing_result_grid",
    )
    return row


def build_struct_trustworthy(
    seq: int,
    domain: str,
    difficulty: str,
    serialization: str,
) -> dict[str, Any]:
    metric_name = metric(seq)
    acct = account(seq)
    result = value(seq)
    source = StructuredSource(
        title="warehouse.metric_results",
        filters=f"account={acct}; month=2026-04; metric={metric_name}",
        columns=["account", "month", "metric", "value"],
        rows=[[acct, "2026-04", metric_name, result]],
        notes=f"The executed result grid contains the requested metric value {result}.",
    )
    query = f"What was {acct}'s {metric_name} in April 2026?"
    row = structured_row_base(
        pattern="direct_answer",
        domain=domain,
        difficulty=difficulty,
        serialization=serialization,
        query=query,
        sources=[source],
        required_elements=[result],
        forbidden_claims=[f"the result grid is missing for {acct}"],
        near_miss_reason="The executed result grid directly answers the requested metric.",
        mechanism="exact_filtered_row",
        gold_answer=result,
        grounding_attributions=["ctx_001"],
    )
    return row


def build_struct_disputed(
    seq: int,
    domain: str,
    difficulty: str,
    serialization: str,
) -> dict[str, Any]:
    metric_name = metric(seq)
    acct = account(seq)
    warehouse_value = value(seq)
    dashboard_value = value(seq + 5)
    query = f"What was {acct}'s {metric_name} in April 2026?"
    warehouse = StructuredSource(
        title="warehouse.metric_results",
        filters=f"account={acct}; month=2026-04; metric={metric_name}",
        columns=["account", "month", "metric", "value"],
        rows=[[acct, "2026-04", metric_name, warehouse_value]],
        notes=f"Warehouse result grid reports {warehouse_value}.",
        authority_signal="warehouse_result",
        authority_score=0.9,
    )
    dashboard = StructuredSource(
        title="dashboard.metric_export",
        filters=f"account={acct}; month=2026-04; metric={metric_name}",
        columns=["account", "month", "metric", "value"],
        rows=[[acct, "2026-04", metric_name, dashboard_value]],
        notes=f"Dashboard export reports {dashboard_value} for the same account, month, and metric.",
        authority_signal="dashboard_export",
        authority_score=0.88,
    )
    row = structured_row_base(
        pattern="numerical_conflict",
        domain=domain,
        difficulty=difficulty,
        serialization=serialization,
        query=query,
        sources=[warehouse, dashboard],
        required_elements=[warehouse_value, dashboard_value],
        forbidden_claims=[f"the evidence agrees that {acct}'s {metric_name} was {warehouse_value}"],
        near_miss_reason="Two retrieved result grids conflict on the same metric value.",
        mechanism="same_metric_diff_values",
    )
    return row


def build_rows(rows_per_family: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    builders = (
        ("code_missing_field", build_code_abstain, CODE_DOMAINS, None),
        ("code_field_present", build_code_trustworthy, CODE_DOMAINS, None),
        ("code_field_conflict", build_code_disputed, CODE_DOMAINS, None),
        ("structured_missing_result", build_struct_abstain, STRUCT_DOMAINS, STRUCT_SERIALIZATIONS),
        ("structured_result_present", build_struct_trustworthy, STRUCT_DOMAINS, STRUCT_SERIALIZATIONS),
        ("structured_result_conflict", build_struct_disputed, STRUCT_DOMAINS, STRUCT_SERIALIZATIONS),
    )
    next_id = 1
    for family, builder, domains, serializations in builders:
        for seq in range(rows_per_family):
            domain = domains[seq % len(domains)]
            difficulty = DIFFICULTIES[seq % len(DIFFICULTIES)]
            if serializations is None:
                row = builder(seq, domain, difficulty)
                serialization = CODE_SERIALIZATION
            else:
                serialization = serializations[seq % len(serializations)]
                row = builder(seq, domain, difficulty, serialization)
            row["meta"]["patch_family"] = family
            row["meta"]["generation_index"] = seq
            rows.append(
                finalize_row(
                    row,
                    case_id=f"sdgp_v8_modality_missing_evidence_patch1_{next_id:05d}",
                    serialization=serialization,
                )
            )
            next_id += 1
    return rows


def load_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    ids = set()
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                ids.add(json.loads(line)["id"])
    return ids


def validate_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    checker = Checker(require_training_schema=True)
    structural_errors: list[str] = []
    for row in rows:
        result = checker.check(row)
        if not result.passed:
            for issue in result.errors:
                structural_errors.append(f"{row['id']}: checker.{issue.rule}: {issue.message}")

    existing_ids = load_ids(Path("data/fitz-gov/cases.jsonl"))
    existing_ids |= load_ids(Path("data/_workspaces/handoff/modality_structured_v1_20260527/cases.jsonl"))
    existing_ids |= load_ids(Path("data/_workspaces/handoff/modality_code_v1_20260527/cases.jsonl"))
    existing_ids |= load_ids(Path("data/_workspaces/handoff/modality_code_patch_v1_20260528/cases.jsonl"))
    existing_ids |= load_ids(
        Path("data/_workspaces/handoff/modality_code_retry_conflict_patch_v1_20260529/cases.jsonl")
    )

    ids = [row["id"] for row in rows]
    duplicate_ids = sorted({row_id for row_id, count in Counter(ids).items() if count > 1})
    collisions = sorted(set(ids) & existing_ids)
    errors = [*structural_errors]
    if duplicate_ids:
        errors.append(f"duplicate patch ids: {duplicate_ids[:5]}")
    if collisions:
        errors.append(f"id collisions with existing rows: {collisions[:5]}")

    for row in rows:
        row_id = row["id"]
        modality = row.get("meta", {}).get("modality")
        if modality not in {"code", "structured"}:
            errors.append(f"{row_id}: unexpected meta.modality {modality!r}")
        if row.get("meta", {}).get("dataset_version") != "v8":
            errors.append(f"{row_id}: meta.dataset_version is not v8")

    return {
        "ok": not errors,
        "error_count": len(errors),
        "errors": errors[:50],
        "row_count": len(rows),
        "label_counts": dict(Counter(row["governance"]["classification"] for row in rows)),
        "modality_counts": dict(Counter(row["meta"]["modality"] for row in rows)),
        "mechanism_counts": dict(Counter(row["meta"]["mechanism"] for row in rows)),
        "serialization_counts": dict(Counter(row["meta"]["serialization"] for row in rows)),
    }


def coverage(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counters: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        counters["by_label"][row["governance"]["classification"]] += 1
        counters["by_modality"][row["meta"]["modality"]] += 1
        counters["by_pattern"][row["taxonomy"]["pattern"]] += 1
        counters["by_domain"][row["routing"]["expert_fired"]] += 1
        counters["by_difficulty"][row["meta"]["difficulty"]] += 1
        counters["by_mechanism"][row["meta"]["mechanism"]] += 1
        counters["by_serialization"][row["meta"]["serialization"]] += 1
        counters["by_patch_family"][row["meta"]["patch_family"]] += 1
    return {name: dict(counter) for name, counter in counters.items()}


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_batches(out_dir: Path, rows: list[dict[str, Any]]) -> list[str]:
    batch_dir = out_dir / "subagent_outputs"
    batch_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for batch_idx, start in enumerate(range(0, len(rows), BATCH_SIZE), start=1):
        path = batch_dir / f"batch_{batch_idx:03d}.jsonl"
        write_jsonl(path, rows[start : start + BATCH_SIZE])
        paths.append(str(path))
    return paths


def write_readme(out_dir: Path, cov: dict[str, Any], validation: dict[str, Any]) -> None:
    lines = [
        "# Modality Missing Evidence Patch v1",
        "",
        "Candidate-only patch. Do not merge or publish before full blind-label QA.",
        "",
        f"- Rows: **{validation['row_count']}**",
        f"- Structural validation errors: **{validation['error_count']}**",
        f"- Label counts: `{cov['by_label']}`",
        f"- Modality counts: `{cov['by_modality']}`",
        f"- Mechanism counts: `{cov['by_mechanism']}`",
        f"- Serialization counts: `{cov['by_serialization']}`",
        "",
        "Targeted surfaces:",
        "",
        "- Code `missing_specific_field` diff-context ABSTAIN rows.",
        "- Structured `missing_execution_result` rows across markdown table, CSV, and evidence packet serializations.",
        "- TRUSTWORTHY and DISPUTED controls for both surfaces.",
        "",
        "Outputs:",
        "",
        "- `cases.jsonl`",
        "- `manifest.json`",
        "- `coverage_report.json`",
        "- `validation_report.json`",
        "- `subagent_outputs/batch_*.jsonl`",
        "",
    ]
    (out_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def write_workspace(out_dir: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    validation = validate_rows(rows)
    cov = coverage(rows)
    write_jsonl(out_dir / "cases.jsonl", rows)
    batch_paths = write_batches(out_dir, rows)
    manifest = {
        "version": VERSION,
        "batch_id": BATCH_ID,
        "created_at": BUILD_TS,
        "row_count": len(rows),
        "cases": "cases.jsonl",
        "batches": batch_paths,
        "notes": "Candidate-only local-control patch; full blind-label QA required before merge/publish.",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (out_dir / "coverage_report.json").write_text(json.dumps(cov, indent=2) + "\n", encoding="utf-8")
    (out_dir / "validation_report.json").write_text(
        json.dumps(validation, indent=2) + "\n",
        encoding="utf-8",
    )
    write_readme(out_dir, cov, validation)
    return {"coverage": cov, "validation": validation, "manifest": manifest}


def main() -> int:
    args = parse_args()
    rows = build_rows(args.rows_per_family)
    result = write_workspace(args.out_dir, rows)
    validation = result["validation"]
    print(f"Wrote {len(rows)} rows to {args.out_dir}")
    print(f"Validation errors: {validation['error_count']}")
    print(json.dumps(result["coverage"], indent=2))
    return 0 if validation["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
