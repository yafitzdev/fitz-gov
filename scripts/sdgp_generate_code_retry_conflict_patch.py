"""Generate a candidate-only code retry-limit conflict patch.

This second targeted patch focuses on the remaining pyrrho code OOD failure:
same-query retry-limit code/config numerical conflicts serialized as
code excerpts, review packets, and diff contexts.

It does not merge rows into the active vault or publish anything.

Run from the fitz-gov repo root:
    python scripts/sdgp_generate_code_retry_conflict_patch.py
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


VERSION = "fitz-gov-modality-code-retry-conflict-patch-0.1"
BUILD_TS = "2026-05-29T08:30:00Z"
PROVIDER = "codex"
PROVIDER_VERSION = "gpt-5-codex"
PROMPT_VERSION = "code-retry-conflict-patch-0.1"
BATCH_ID = "code_retry_conflict_patch_v1_20260529"
DEFAULT_OUT = Path("data/_workspaces/handoff/modality_code_retry_conflict_patch_v1_20260529")
BATCH_SIZE = 60
ROWS_PER_LABEL = 120

SERIALIZATIONS = ("code_excerpt", "review_packet", "diff_context")
DIFFICULTIES = ("easy", "medium", "hard")
DOMAINS = (
    "technology_computing",
    "technology_computing",
    "technology_computing",
    "economics_finance",
    "science_medicine",
)
FEATURES = (
    "customer",
    "invoice",
    "payment",
    "refund",
    "order",
    "subscription",
    "ledger",
    "payout",
    "claims",
    "enrollment",
    "shipment",
    "notification",
    "report",
    "profile",
    "session",
    "catalog",
)


@dataclass(frozen=True)
class Source:
    path: str
    language: str
    content: str
    summary: str
    authority_signal: str
    authority_score: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--rows-per-label", type=int, default=ROWS_PER_LABEL)
    return parser.parse_args()


def feature(seq: int) -> str:
    root = FEATURES[seq % len(FEATURES)]
    suffix = seq // len(FEATURES)
    return root if suffix == 0 else f"{root}_{suffix}"


def retry_values(seq: int) -> tuple[int, int]:
    code_limit = 2 + (seq % 5)
    offset = (seq % 3) + 1
    config_limit = code_limit + offset
    if config_limit > 8:
        config_limit = code_limit - offset
    return code_limit, config_limit


def constant_name(service: str) -> str:
    return f"MAX_{service.upper()}_SYNC_RETRIES"


def function_name(service: str) -> str:
    return f"sync_{service}"


def render_source(source: Source, serialization: str) -> str:
    content = source.content.strip("\n")
    if serialization == "code_excerpt":
        return (
            f"Retrieved file: {source.path}\n"
            f"Language: {source.language}\n"
            f"```{source.language}\n{content}\n```\n"
            f"Note: {source.summary}"
        )
    if serialization == "review_packet":
        numbered = "\n".join(
            f"{idx:03d}: {line}" for idx, line in enumerate(content.splitlines(), start=1)
        )
        return (
            "Code review evidence packet\n"
            f"path={source.path}\n"
            f"language={source.language}\n"
            f"note={source.summary}\n"
            "numbered_excerpt:\n"
            f"{numbered}"
        )
    if serialization == "diff_context":
        diff = "\n".join(f"+ {line}" if line else "+" for line in content.splitlines())
        return (
            "Retrieved diff context\n"
            f"+++ b/{source.path}\n"
            "@@ relevant excerpt @@\n"
            f"{diff}\n"
            f"review_note={source.summary}"
        )
    raise ValueError(f"unknown serialization: {serialization}")


def contexts(sources: list[Source], serialization: str) -> list[dict[str, Any]]:
    return [
        base._make_context(
            idx,
            render_source(source, serialization),
            authority_score=source.authority_score,
            authority_signal=source.authority_signal,
            summary=source.summary,
            relevance=0.92,
            boundary=0.88,
            anchor="code retry conflict patch",
        )
        for idx, source in enumerate(sources, start=1)
    ]


def row_base(
    *,
    pattern: str,
    domain: str,
    difficulty: str,
    query: str,
    sources: list[Source],
    required_elements: list[str],
    forbidden_claims: list[str],
    near_miss_reason: str,
    mechanism: str,
    serialization: str,
    gold_answer: str | None = None,
    direct: bool = False,
) -> dict[str, Any]:
    return base.build_row(
        modality="code",
        case_id="",
        pattern=pattern,
        domain=domain,
        difficulty=difficulty,
        query=query,
        query_rewritten=None,
        contexts=contexts(sources, serialization),
        required_elements=required_elements,
        forbidden_claims=forbidden_claims,
        forbidden_elements=[],
        near_miss_reason=near_miss_reason,
        mechanism=mechanism,
        serialization=serialization,
        gold_answer=gold_answer,
        grounding_attributions=["ctx_001", "ctx_002"] if gold_answer and len(sources) > 1 else None,
        direct=direct,
    )


def code_source(service: str, limit: int) -> Source:
    const = constant_name(service)
    fn = function_name(service)
    content = f"""
{const} = {limit}

def {fn}(customer_id: str) -> None:
    for attempt in range(1, {const} + 1):
        try:
            push_{service}(customer_id)
            return
        except TemporarySyncError:
            if attempt == {const}:
                raise
"""
    return Source(
        path=f"jobs/{service}_sync.py",
        language="python",
        content=content,
        summary=f"Application code sets {const} to {limit} for {fn}.",
        authority_signal="source_code",
        authority_score=0.94,
    )


def config_source(service: str, limit: int, *, environment: str = "production") -> Source:
    const = constant_name(service)
    content = f"""
env:
  {const}: "{limit}"
  SYNC_QUEUE: "{service}-sync-{environment}"
  ENVIRONMENT: "{environment}"
"""
    return Source(
        path=f"deploy/{environment}/{service}-sync.yaml",
        language="yaml",
        content=content,
        summary=f"The {environment} deployment config sets {const} to {limit}.",
        authority_signal="environment_config",
        authority_score=0.91,
    )


def conflict_row(seq: int, serialization: str) -> dict[str, Any]:
    service = feature(seq)
    code_limit, config_limit = retry_values(seq)
    fn = function_name(service)
    const = constant_name(service)
    query = f"What retry limit is configured for `{fn}` in production?"
    sources = [code_source(service, code_limit), config_source(service, config_limit)]
    return row_base(
        pattern="numerical_conflict",
        domain=DOMAINS[seq % len(DOMAINS)],
        difficulty=DIFFICULTIES[seq % len(DIFFICULTIES)],
        query=query,
        sources=sources,
        required_elements=[str(code_limit), str(config_limit), const],
        forbidden_claims=[
            f"`{fn}` is unambiguously configured for {code_limit} retries",
            f"`{fn}` is unambiguously configured for {config_limit} retries",
        ],
        near_miss_reason=(
            "The code constant and production deployment config answer the same retry-limit "
            "question with different numbers, so the evidence is disputed."
        ),
        mechanism="retry_limit_code_config_conflict",
        serialization=serialization,
    )


def agreement_row(seq: int, serialization: str) -> dict[str, Any]:
    service = feature(seq)
    limit, _ = retry_values(seq)
    fn = function_name(service)
    const = constant_name(service)
    query = f"What retry limit is configured for `{fn}` in production?"
    sources = [code_source(service, limit), config_source(service, limit)]
    return row_base(
        pattern="quantitative_consensus",
        domain=DOMAINS[seq % len(DOMAINS)],
        difficulty=DIFFICULTIES[seq % len(DIFFICULTIES)],
        query=query,
        sources=sources,
        required_elements=[str(limit), const],
        forbidden_claims=[
            f"`{fn}` uses a retry limit other than {limit}",
            "the code and production config disagree",
        ],
        near_miss_reason=(
            "Both the source constant and production deployment config name the same retry limit."
        ),
        mechanism="retry_limit_code_config_agreement",
        serialization=serialization,
        gold_answer=f"`{fn}` is configured for {limit} retries in production.",
        direct=True,
    )


def wrong_service_row(seq: int, serialization: str) -> dict[str, Any]:
    service = feature(seq)
    other = feature(seq + 5)
    limit, _ = retry_values(seq)
    fn = function_name(service)
    other_fn = function_name(other)
    query = f"What retry limit is configured for `{fn}` in production?"
    sources = [code_source(other, limit), config_source(other, limit)]
    return row_base(
        pattern="wrong_entity",
        domain=DOMAINS[seq % len(DOMAINS)],
        difficulty=DIFFICULTIES[seq % len(DIFFICULTIES)],
        query=query,
        sources=sources,
        required_elements=[],
        forbidden_claims=[
            f"the retrieved `{other_fn}` evidence answers the `{fn}` retry-limit question",
            f"`{fn}` is configured for {limit} retries",
        ],
        near_miss_reason=(
            "The retrieved code and config are internally consistent, but they are for a different "
            "sync job than the one named in the query."
        ),
        mechanism="retry_limit_wrong_service",
        serialization=serialization,
    )


def finalize(row: dict[str, Any], idx: int, serialization: str) -> dict[str, Any]:
    row["id"] = f"sdgp_v8_modality_code_retry_patch1_{idx:05d}"
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


def build_rows(rows_per_label: int) -> list[dict[str, Any]]:
    if rows_per_label % len(SERIALIZATIONS) != 0:
        raise ValueError("--rows-per-label must be divisible by 3")
    rows: list[dict[str, Any]] = []
    builders = (conflict_row, agreement_row, wrong_service_row)
    for builder in builders:
        scenarios = rows_per_label // len(SERIALIZATIONS)
        for seq in range(scenarios):
            for serialization in SERIALIZATIONS:
                row = builder(seq, serialization)
                rows.append(finalize(row, len(rows), serialization))
    return rows


def load_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    ids: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            if raw.strip():
                ids.add(json.loads(raw)["id"])
    return ids


def validate_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    checker = Checker(require_training_schema=True)
    errors: list[str] = []
    seen: set[str] = set()
    existing_ids = set()
    existing_ids |= load_ids(Path("data/fitz-gov/cases.jsonl"))
    existing_ids |= load_ids(Path("data/_workspaces/handoff/modality_structured_v1_20260527/cases.jsonl"))
    existing_ids |= load_ids(Path("data/_workspaces/handoff/modality_code_v1_20260527/cases.jsonl"))
    existing_ids |= load_ids(Path("data/_workspaces/handoff/modality_code_patch_v1_20260528/cases.jsonl"))

    for row in rows:
        row_id = row["id"]
        if row_id in seen:
            errors.append(f"{row_id}: duplicate ID within patch")
        seen.add(row_id)
        if row_id in existing_ids:
            errors.append(f"{row_id}: ID collides with existing/candidate row")
        if row.get("meta", {}).get("modality") != "code":
            errors.append(f"{row_id}: meta.modality is not code")
        if row.get("meta", {}).get("dataset_version") != "v8":
            errors.append(f"{row_id}: meta.dataset_version is not v8")
        result = checker.check(row)
        if not result.passed:
            for issue in result.errors:
                errors.append(f"{row_id}: checker.{issue.rule}: {issue.message}")

    return {
        "ok": not errors,
        "rows": len(rows),
        "errors": errors,
        "label_counts": dict(Counter(row["governance"]["classification"] for row in rows)),
        "mechanism_counts": dict(Counter(row["meta"]["mechanism"] for row in rows)),
    }


def coverage_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counters: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        counters["by_label"][row["governance"]["classification"]] += 1
        counters["by_pattern"][row["taxonomy"]["pattern"]] += 1
        counters["by_domain"][row["routing"]["expert_fired"]] += 1
        counters["by_difficulty"][row["meta"]["difficulty"]] += 1
        counters["by_mechanism"][row["meta"]["mechanism"]] += 1
        counters["by_serialization"][row["meta"]["serialization"]] += 1
    return {"total_rows": len(rows), **{key: dict(value) for key, value in counters.items()}}


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_batches(out_dir: Path, rows: list[dict[str, Any]]) -> list[str]:
    batch_dir = out_dir / "batches"
    batch_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for idx in range(0, len(rows), BATCH_SIZE):
        path = batch_dir / f"batch_{idx // BATCH_SIZE + 1:04d}.jsonl"
        write_jsonl(path, rows[idx : idx + BATCH_SIZE])
        written.append(str(path.relative_to(out_dir).as_posix()))
    return written


def write_readme(out_dir: Path, coverage: dict[str, Any], validation: dict[str, Any]) -> None:
    lines = [
        "# Code Retry Conflict Patch v1 - 2026-05-29",
        "",
        "Candidate-only SDGP V8 rows for retry-limit code/config evidence. This patch",
        "targets the remaining pyrrho code OOD miss and is not merged or published.",
        "",
        "## Status",
        "",
        "| Item | Value |",
        "|---|---:|",
        f"| Total rows | {coverage['total_rows']} |",
        f"| TRUSTWORTHY | {coverage['by_label'].get('TRUSTWORTHY', 0)} |",
        f"| ABSTAIN | {coverage['by_label'].get('ABSTAIN', 0)} |",
        f"| DISPUTED | {coverage['by_label'].get('DISPUTED', 0)} |",
        f"| Structural validation errors | {len(validation['errors'])} |",
        "",
        "## Mechanisms",
        "",
        "| Mechanism | Rows |",
        "|---|---:|",
    ]
    for name, count in sorted(coverage["by_mechanism"].items()):
        lines.append(f"| `{name}` | {count} |")
    lines.extend(
        [
            "",
            "## Files",
            "",
            "| Path | Purpose |",
            "|---|---|",
            "| `cases.jsonl` | All candidate rows |",
            "| `manifest.json` | Candidate manifest |",
            "| `coverage_report.json` | Label/pattern/domain/mechanism coverage |",
            "| `validation_report.json` | Structural checker result |",
            "| `batches/` | 60-row shards for later blind QA |",
        ]
    )
    (out_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_workspace(out_dir: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(out_dir / "cases.jsonl", rows)
    batches = write_batches(out_dir, rows)
    coverage = coverage_report(rows)
    validation = validate_rows(rows)
    manifest = {
        "name": "fitz-gov-modality-code-retry-conflict-patch-v1",
        "version": VERSION,
        "modality": "code",
        "dataset_version": "v8",
        "row_shape": "sdgp_v8",
        "rows": len(rows),
        "label_counts": coverage["by_label"],
        "mechanism_counts": coverage["by_mechanism"],
        "batches": batches,
        "description": (
            "Targeted candidate-only code retry-limit patch for same-query code/config "
            "numerical conflicts and adjacent agreement/wrong-service controls."
        ),
        "build_ts": BUILD_TS,
        "provider": PROVIDER,
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out_dir / "coverage_report.json").write_text(
        json.dumps(coverage, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out_dir / "validation_report.json").write_text(
        json.dumps(validation, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_readme(out_dir, coverage, validation)
    return validation


def main() -> int:
    args = parse_args()
    rows = build_rows(args.rows_per_label)
    validation = write_workspace(args.out_dir, rows)

    print("=== Code retry conflict patch ===")
    print(f"Rows       : {len(rows)}")
    print(f"Output     : {args.out_dir}")
    print(f"Labels     : {validation['label_counts']}")
    print(f"Mechanisms : {validation['mechanism_counts']}")
    print(f"Valid      : {validation['ok']} ({len(validation['errors'])} errors)")
    if validation["errors"]:
        for error in validation["errors"][:20]:
            print(f"  - {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
