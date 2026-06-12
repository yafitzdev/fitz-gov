"""Upload the fitz-gov V9 vault to Hugging Face.

V9 publishes the full local vault as one canonical `v9` config. V6/V7/V8 rows
keep the published V8.2 split assignments; new V9 rows are assigned by exact
query group so the public benchmark has zero exact-query split leakage.

Run from the fitz-gov project root:
    python scripts/sdgp_upload_v9_hf.py --dry-run --staging-dir data/hf_v9_staging
    python scripts/sdgp_upload_v9_hf.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(SCRIPT_DIR))

from fitz_gov.sdgp.completeness import audit_case_completeness
from fitz_gov.sdgp.public_schema import find_legacy_public_fields
from fitz_gov.sdgp.retrieval_control_gap_detector import (
    RetrievalControlCellFilter,
    RetrievalControlGapDetector,
    all_retrieval_control_cells,
    retrieval_control_cell_counts,
)
from sdgp_upload_v7_hf import (
    _class_counts,
    _version_counts,
    load_cases,
    load_split_assignments,
    normalize_cases_for_json_loader,
    write_parquet,
)
from sdgp_validate_retrieval_control_v8_2 import validate_retrieval_control


CANONICAL_QUERY_CONTRACT_LABELS: tuple[str, ...] = (
    "evidence_sufficiency",
    "structured_lookup",
    "temporal_grounding",
    "exhaustive_coverage",
    "comparison_coverage",
    "representative_overview",
)

DETAILED_TO_COLLAPSED_ANSWERABILITY: dict[str, str] = {
    "single_fact": "direct_answer",
    "exact_lookup": "direct_answer",
    "yes_no": "direct_answer",
    "citation_required": "direct_answer",
    "direct_answer": "direct_answer",
    "explanation": "synthesis_answer",
    "summary": "synthesis_answer",
    "synthesis_answer": "synthesis_answer",
    "list": "set_answer",
    "exhaustive_list": "set_answer",
    "set_answer": "set_answer",
    "comparison": "structured_reasoning",
    "timeline": "structured_reasoning",
    "calculation": "structured_reasoning",
    "structured_reasoning": "structured_reasoning",
}

EXPECTED_VERSION_COUNTS = {"v6": 2980, "v7": 7520, "v8": 14092, "v9": 16163}
EXPECTED_TOTAL_ROWS = 40755
EXPECTED_MATRIX_CELLS = 189


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--repo-id", type=str, default="yafitzdev/fitz-gov")
    parser.add_argument("--vault", type=Path, default=Path("data/fitz-gov"))
    parser.add_argument(
        "--v8-qa-dir",
        type=Path,
        default=Path("data/_workspaces/qa/sdgp_v8_qa"),
    )
    parser.add_argument(
        "--v9-gap-report",
        type=Path,
        default=Path(
            "data/_workspaces/qa/v9_answerability_closure_buffer_20260612/"
            "gap_after_closure_buffer_validated_merge.json"
        ),
    )
    parser.add_argument("--version", type=str, default="9.0.0")
    parser.add_argument("--target-per-cell", type=int, default=100)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--staging-dir", type=Path, default=None)
    parser.add_argument("--commit-message", type=str, default=None)
    parser.add_argument("--no-tag", action="store_true")
    return parser.parse_args()


def _nested(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    cur: Any = data
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def _case_id(case: dict[str, Any]) -> str:
    return str(case.get("id") or "")


def _norm_query(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def _case_query(case: dict[str, Any]) -> str:
    return _norm_query(_nested(case, "input", "query", default=""))


def _split_for_query(query: str) -> str:
    bucket = int(hashlib.sha1(query.encode("utf-8")).hexdigest()[:8], 16) % 100
    if bucket < 80:
        return "train"
    if bucket < 90:
        return "validation"
    return "test"


def assign_v9_splits(
    cases: list[dict[str, Any]],
    previous_assignments: dict[str, str],
) -> tuple[dict[str, str], dict[str, Any]]:
    query_to_ids: dict[str, list[str]] = defaultdict(list)
    old_query_splits: dict[str, set[str]] = defaultdict(set)
    for case in cases:
        case_id = _case_id(case)
        query = _case_query(case)
        query_to_ids[query].append(case_id)
        if case_id in previous_assignments:
            old_query_splits[query].add(previous_assignments[case_id])

    conflicts = {
        query: sorted(splits)
        for query, splits in old_query_splits.items()
        if len(splits) > 1
    }
    if conflicts:
        first_query, first_splits = next(iter(conflicts.items()))
        raise ValueError(f"old split assignments leak query group {first_query!r}: {first_splits}")

    assignments: dict[str, str] = {}
    inherited_groups = 0
    hashed_groups = 0
    for query, case_ids in query_to_ids.items():
        if old_query_splits.get(query):
            split = next(iter(old_query_splits[query]))
            inherited_groups += 1
        else:
            split = _split_for_query(query)
            hashed_groups += 1
        for case_id in case_ids:
            assignments[case_id] = split

    leak_groups = 0
    leak_rows = 0
    for case_ids in query_to_ids.values():
        splits = {assignments[case_id] for case_id in case_ids}
        if len(splits) > 1:
            leak_groups += 1
            leak_rows += len(case_ids)
    if leak_groups:
        raise ValueError(f"new split assignments leak {leak_groups} query groups")

    return assignments, {
        "query_groups": len(query_to_ids),
        "inherited_query_groups": inherited_groups,
        "hashed_query_groups": hashed_groups,
        "query_group_leakage": {"groups": leak_groups, "rows": leak_rows},
        "split_counts": dict(sorted(Counter(assignments.values()).items())),
    }


def _retrieval_control(case: dict[str, Any]) -> dict[str, Any]:
    control = _nested(case, "routing", "retrieval_control", default={})
    return control if isinstance(control, dict) else {}


def _answerability_shape(case: dict[str, Any]) -> str:
    kind = _nested(_retrieval_control(case), "answerability_shape", "kind", default="")
    if not isinstance(kind, str) or not kind:
        raise ValueError(f"{case.get('id')}: missing retrieval_control.answerability_shape.kind")
    try:
        return DETAILED_TO_COLLAPSED_ANSWERABILITY[kind]
    except KeyError as exc:
        raise ValueError(f"{case.get('id')}: unknown answerability_shape.kind={kind!r}") from exc


def _canonical_query_contract(kind: str, *, collapsed_shape: str) -> str:
    raw = str(kind or "").strip()
    if raw in CANONICAL_QUERY_CONTRACT_LABELS:
        return raw
    lowered = raw.lower()
    if any(
        token in lowered
        for token in ("timeline", "temporal", "date", "deadline", "timeframe", "chronolog")
    ):
        return "temporal_grounding"
    if any(
        token in lowered
        for token in (
            "comparison",
            "comparative",
            "compare",
            "benchmark",
            "threshold",
            "ranked",
            "candidate",
        )
    ):
        return "comparison_coverage"
    if any(
        token in lowered
        for token in ("set", "list", "enumeration", "membership", "coverage", "exhaustive")
    ):
        return "exhaustive_coverage"
    if any(
        token in lowered
        for token in (
            "calculation",
            "compute",
            "computation",
            "arithmetic",
            "numeric",
            "quantitative",
            "metric",
            "trace",
            "lookup",
            "structured",
            "configuration",
        )
    ):
        return "structured_lookup"
    if any(
        token in lowered
        for token in (
            "summary",
            "synthesis",
            "explanation",
            "causal",
            "rationale",
            "interpretation",
            "policy",
            "legal",
            "rule",
            "mechanism",
        )
    ):
        return "representative_overview"
    if collapsed_shape == "set_answer":
        return "exhaustive_coverage"
    if collapsed_shape == "structured_reasoning":
        return "structured_lookup"
    if collapsed_shape == "synthesis_answer":
        return "representative_overview"
    return "evidence_sufficiency"


def normalize_public_query_contracts(cases: list[dict[str, Any]]) -> dict[str, Any]:
    changed = 0
    raw_counts: Counter[str] = Counter()
    canonical_counts: Counter[str] = Counter()
    for case in cases:
        query_contract = _nested(case, "routing", "query_contract", default={})
        if not isinstance(query_contract, dict):
            raise ValueError(f"{case.get('id')}: missing routing.query_contract")
        raw = str(query_contract.get("kind") or "")
        canonical = _canonical_query_contract(raw, collapsed_shape=_answerability_shape(case))
        raw_counts[raw] += 1
        canonical_counts[canonical] += 1
        if raw != canonical:
            query_contract["kind"] = canonical
            changed += 1
    return {
        "changed_rows": changed,
        "raw_unique": len(raw_counts),
        "canonical_counts": dict(sorted(canonical_counts.items())),
    }


def normalize_public_retrieval_control_row_indexes(cases: list[dict[str, Any]]) -> dict[str, int]:
    changed = 0
    missing = 0
    for row_index, case in enumerate(cases, start=1):
        control = _nested(case, "routing", "retrieval_control", default={})
        if not isinstance(control, dict):
            missing += 1
            continue
        if control.get("row_index") != row_index:
            control["row_index"] = row_index
            changed += 1
    return {"changed_rows": changed, "missing_rows": missing}


def normalize_public_retrieval_control_signals(cases: list[dict[str, Any]]) -> dict[str, int]:
    changed = 0
    for case in cases:
        control = _retrieval_control(case)
        for field in (
            "retrieval_action",
            "gap_type",
            "answerability_shape",
            "preferred_retrieval_modality",
        ):
            block = control.get(field)
            if not isinstance(block, dict):
                continue
            signals = block.get("signals")
            if not isinstance(signals, list) or not signals:
                block["signals"] = [f"{field}={block.get('kind')}"]
                changed += 1
        severity = control.get("evidence_failure_severity")
        if isinstance(severity, dict):
            signals = severity.get("signals")
            if not isinstance(signals, list) or not signals:
                severity["signals"] = [f"severity_score={severity.get('score')}"]
                changed += 1
    return {"changed_signal_lists": changed}


def _normalize_grounding_target_item(item: Any) -> dict[str, Any]:
    if isinstance(item, dict):
        out = dict(item)
        claim = out.get("claim") or out.get("text") or out.get("target") or ""
        support_ids = (
            out.get("supporting_context_ids")
            or out.get("support_context_ids")
            or out.get("attributions")
            or []
        )
        if not isinstance(support_ids, list):
            support_ids = []
        out["claim"] = str(claim)
        out["supporting_context_ids"] = [str(value) for value in support_ids]
        return out
    return {"claim": str(item), "supporting_context_ids": []}


def normalize_public_grounding_target_lists(cases: list[dict[str, Any]]) -> dict[str, int]:
    changed = 0
    for case in cases:
        for path in (("input", "grounding_targets"), ("evaluation", "grounding_targets")):
            container = case.get(path[0])
            if not isinstance(container, dict):
                continue
            value = container.get(path[1])
            if not isinstance(value, list):
                continue
            normalized = [_normalize_grounding_target_item(item) for item in value]
            if normalized != value:
                container[path[1]] = normalized
                changed += 1
    return {"changed_lists": changed}


def validate_query_contracts(cases: Iterable[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    bad: list[tuple[str, str]] = []
    allowed = set(CANONICAL_QUERY_CONTRACT_LABELS)
    for case in cases:
        kind = _nested(case, "routing", "query_contract", "kind", default="")
        counts[str(kind)] += 1
        if kind not in allowed:
            bad.append((_case_id(case), str(kind)))
    if bad:
        raise ValueError(f"non-canonical query_contract labels remain: {bad[:20]}")
    return dict(sorted(counts.items()))


def require_training_schema(cases: Iterable[dict[str, Any]]) -> dict[str, Any]:
    by_version: Counter[str] = Counter()
    failures: list[dict[str, Any]] = []
    rows = 0
    for case in cases:
        rows += 1
        version = str(_nested(case, "meta", "dataset_version", default="<missing>"))
        by_version[version] += 1
        issues = audit_case_completeness(case)
        if issues:
            failures.append({"id": case.get("id"), "issues": issues})
    if failures:
        raise ValueError(f"training schema incomplete for {len(failures)} rows: {failures[:5]}")
    return {"rows": rows, "by_version": dict(sorted(by_version.items()))}


def require_retrieval_control(cases: list[dict[str, Any]]) -> dict[str, Any]:
    labels = {
        row_index: {
            "row_index": row_index,
            "case_id": case.get("id"),
            "retrieval_control": _nested(case, "routing", "retrieval_control", default={}),
            "_source_file": "cases.jsonl",
            "_source_line": row_index,
        }
        for row_index, case in enumerate(cases, start=1)
    }
    errors, counts, high_risk = validate_retrieval_control(labels=labels, cases=cases)
    if errors:
        raise ValueError(
            f"retrieval-control validation failed on {len(errors)} fields: {errors[:20]}"
        )
    return {
        "rows_labeled": len(labels),
        "counts": dict(sorted(counts.items())),
        "high_risk": dict(sorted(high_risk.items())),
    }


def require_saved_gap_report(path: Path, *, target_per_cell: int, rows_read: int) -> dict[str, Any]:
    report = json.loads(path.read_text(encoding="utf-8"))
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    failures: list[str] = []
    if report.get("target_per_cell") != target_per_cell:
        failures.append(f"target_per_cell={report.get('target_per_cell')}")
    if report.get("rows_read") != rows_read:
        failures.append(f"rows_read={report.get('rows_read')}")
    if summary.get("cells_considered") != EXPECTED_MATRIX_CELLS:
        failures.append(f"cells_considered={summary.get('cells_considered')}")
    if summary.get("cells_at_target") != EXPECTED_MATRIX_CELLS:
        failures.append(f"cells_at_target={summary.get('cells_at_target')}")
    if summary.get("total_gap_to_fill") != 0:
        failures.append(f"total_gap_to_fill={summary.get('total_gap_to_fill')}")
    if failures:
        raise ValueError(f"saved V9 gap report failed release gates: {', '.join(failures)}")
    return {"rows_read": report.get("rows_read"), "summary": summary}


def require_v9_target_matrix(cases: list[dict[str, Any]], target_per_cell: int) -> dict[str, Any]:
    counts = retrieval_control_cell_counts(cases)
    detector = RetrievalControlGapDetector()
    flt = RetrievalControlCellFilter(include_direct_answer=False)
    summary = detector.coverage_summary(counts, target=target_per_cell, filter=flt)
    gaps = detector.rank(counts, target=target_per_cell, filter=flt)
    cells = all_retrieval_control_cells(include_direct_answer=False)
    cell_counts = [counts.get(cell.cell_id, 0) for cell in cells if flt.matches(cell)]
    if summary["cells_considered"] != EXPECTED_MATRIX_CELLS:
        raise ValueError(f"V9 target matrix should have 189 cells, got {summary['cells_considered']}")
    if summary["cells_at_target"] != summary["cells_considered"]:
        raise ValueError(f"V9 target matrix has cells below target: {summary}")
    if summary["total_gap_to_fill"] != 0:
        raise ValueError(f"V9 target matrix still has gap: {summary['total_gap_to_fill']}")
    return {
        "summary": summary,
        "min_cell_count": min(cell_counts),
        "max_cell_count": max(cell_counts),
        "gaps": [
            {"cell_id": gap.cell.cell_id, "current": gap.current, "target": gap.target, "gap": gap.gap}
            for gap in gaps[:20]
        ],
    }


def require_release_gates(
    *,
    cases: list[dict[str, Any]],
    assignments: dict[str, str],
    split_summary: dict[str, Any],
    target_per_cell: int,
    gap_report_path: Path,
) -> dict[str, Any]:
    version_counts = _version_counts(cases)
    failures: list[str] = []
    if version_counts != EXPECTED_VERSION_COUNTS:
        failures.append(f"version counts {version_counts} != {EXPECTED_VERSION_COUNTS}")
    if len(cases) != EXPECTED_TOTAL_ROWS:
        failures.append(f"row count {len(cases)} != {EXPECTED_TOTAL_ROWS}")
    if len(assignments) != len(cases):
        failures.append(f"split assignments {len(assignments)} != rows {len(cases)}")
    duplicate_ids = len(cases) - len({_case_id(case) for case in cases})
    if duplicate_ids:
        failures.append(f"duplicate IDs: {duplicate_ids}")
    if split_summary["query_group_leakage"]["groups"] != 0:
        failures.append(f"query-group leakage: {split_summary['query_group_leakage']}")
    legacy_hits = [
        (case.get("id", "<no id>"), paths)
        for case in cases
        if (paths := find_legacy_public_fields(case))
    ]
    if legacy_hits:
        failures.append(f"legacy public schema fields remain in {len(legacy_hits)} rows")
    if failures:
        raise ValueError("V9 release gates failed: " + "; ".join(failures))

    return {
        "version_counts": version_counts,
        "saved_gap_report": require_saved_gap_report(
            gap_report_path,
            target_per_cell=target_per_cell,
            rows_read=len(cases),
        ),
        "training_schema": require_training_schema(cases),
        "query_contract": validate_query_contracts(cases),
        "retrieval_control": require_retrieval_control(cases),
        "target_matrix": require_v9_target_matrix(cases, target_per_cell),
        "split_summary": split_summary,
    }


def _answerability_counts(cases: Iterable[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for case in cases:
        counts[_answerability_shape(case)] += 1
    return dict(sorted(counts.items()))


def _modality_counts(cases: Iterable[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for case in cases:
        modality = _nested(
            case,
            "routing",
            "retrieval_control",
            "preferred_retrieval_modality",
            "kind",
            default="<missing>",
        )
        counts[str(modality)] += 1
    return dict(sorted(counts.items()))


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_dataset_card(
    staging: Path,
    *,
    version: str,
    split_counts: dict[str, int],
    split_class_counts: dict[str, dict[str, int]],
    n_all: int,
    gates: dict[str, Any],
    answerability_counts: dict[str, int],
    modality_counts: dict[str, int],
) -> None:
    def class_row(split: str) -> str:
        counts = split_class_counts[split]
        return (
            f"| `{split}` | {split_counts[split]:,} | "
            f"{counts.get('abstain', 0):,} | {counts.get('disputed', 0):,} | "
            f"{counts.get('trustworthy', 0):,} |"
        )

    version_counts = gates["version_counts"]
    matrix = gates["target_matrix"]
    split_summary = gates["split_summary"]
    modality_rows = "\n".join(
        f"| `{key}` | {value:,} |" for key, value in modality_counts.items()
    )

    card = f"""---
license: cc-by-nc-4.0
task_categories:
  - text-classification
language:
  - en
size_categories:
  - 10K<n<100K
tags:
  - rag
  - governance
  - hallucination-detection
  - epistemic-honesty
  - abstention
  - benchmark
configs:
  - config_name: v9
    default: true
    data_files:
      - split: train
        path: "v9/train.parquet"
      - split: validation
        path: "v9/validation.parquet"
      - split: test
        path: "v9/test.parquet"
---

# fitz-gov

fitz-gov is a {n_all:,}-case benchmark for RAG governance. Each row is a `(query, retrieved contexts)` pair labeled `ABSTAIN`, `DISPUTED`, or `TRUSTWORTHY`.

Version: **{version}**. License: **CC BY-NC 4.0**.

## What's New In V9.0.0

V9.0.0 adds **{version_counts.get('v9', 0):,}** QA-gated V9 rows and closes the target-100 retrieval-control answerability matrix:

`governance_class x domain x difficulty x collapsed_answerability_shape`

| Answerability bucket | Rows |
|---|---:|
| `direct_answer` | {answerability_counts.get('direct_answer', 0):,} |
| `synthesis_answer` | {answerability_counts.get('synthesis_answer', 0):,} |
| `set_answer` | {answerability_counts.get('set_answer', 0):,} |
| `structured_reasoning` | {answerability_counts.get('structured_reasoning', 0):,} |

Release gates:

- Matrix cells: **{matrix['summary']['cells_at_target']:,}/{matrix['summary']['cells_considered']:,}** at target.
- Target per cell: **100** rows.
- Cell count range: **{matrix['min_cell_count']} - {matrix['max_cell_count']}**.
- Remaining V9 target gap: **{matrix['summary']['total_gap_to_fill']}**.
- Exact-query split leakage: **{split_summary['query_group_leakage']['groups']}** groups.

Dataset composition:

| Cohort | Rows |
|---|---:|
| V6 | {version_counts.get('v6', 0):,} |
| V7 | {version_counts.get('v7', 0):,} |
| V8 | {version_counts.get('v8', 0):,} |
| V9 | {version_counts.get('v9', 0):,} |
| Total | {n_all:,} |

Retrieval modality coverage:

| Retrieval modality | Rows |
|---|---:|
{modality_rows}

## Loading

| Split | Rows | ABSTAIN | DISPUTED | TRUSTWORTHY |
|---|---:|---:|---:|---:|
{class_row('train')}
{class_row('validation')}
{class_row('test')}

```python
from datasets import load_dataset

ds = load_dataset("yafitzdev/fitz-gov")
print(ds)
```

Rows expose `id`, `label`, `tier`, `input`, `governance`, `evaluation`, `routing`, `taxonomy`, and `meta`. The `routing` block includes canonical `query_contract` plus retrieval-control labels.

## Citation

```bibtex
@misc{{fitz_gov_v9_2026,
  title  = {{ fitz-gov V9: Retrieval-control answerability coverage for RAG governance }},
  author = {{ Yan Fitzner }},
  year   = {{ 2026 }},
  url    = {{ https://huggingface.co/datasets/yafitzdev/fitz-gov }},
}}
```
"""
    (staging / "README.md").write_text(card, encoding="utf-8")


def main() -> int:
    args = parse_args()
    vault_jsonl = (args.vault / "cases.jsonl").resolve()
    previous_assignments_path = (args.v8_qa_dir / "split_assignments.jsonl").resolve()
    if not vault_jsonl.exists():
        print(f"ERROR: vault not found: {vault_jsonl}", file=sys.stderr)
        return 1
    if not previous_assignments_path.exists():
        print(f"ERROR: split assignments not found: {previous_assignments_path}", file=sys.stderr)
        return 1
    if not args.v9_gap_report.exists():
        print(f"ERROR: V9 gap report not found: {args.v9_gap_report}", file=sys.stderr)
        return 1

    if args.staging_dir is None:
        staging = Path(tempfile.mkdtemp(prefix="fitz_gov_v9_hf_"))
    else:
        staging = args.staging_dir.resolve()
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True)

    print(f"Vault          : {vault_jsonl}")
    print(f"V8 split file  : {previous_assignments_path}")
    print(f"V9 gap report  : {args.v9_gap_report.resolve()}")
    print(f"Staging dir    : {staging}")
    print(f"Repo id        : {args.repo_id}")
    print(f"Version        : {args.version}\n")

    print("[1/6] Loading vault and normalizing public labels ...")
    cases = load_cases(vault_jsonl)
    query_contract_summary = normalize_public_query_contracts(cases)
    row_index_summary = normalize_public_retrieval_control_row_indexes(cases)
    signal_summary = normalize_public_retrieval_control_signals(cases)
    grounding_target_summary = normalize_public_grounding_target_lists(cases)
    print(f"      cases: {len(cases):,}")
    print(f"      cohorts: {_version_counts(cases)}")
    print(f"      query_contract normalization: {query_contract_summary}")
    print(f"      retrieval_control row_index normalization: {row_index_summary}")
    print(f"      retrieval_control signal normalization: {signal_summary}")
    print(f"      grounding target normalization: {grounding_target_summary}")

    print("\n[2/6] Building query-grouped split assignments ...")
    previous_assignments = load_split_assignments(previous_assignments_path)
    assignments, split_summary = assign_v9_splits(cases, previous_assignments)
    print(f"      split summary: {split_summary}")

    print("\n[3/6] Checking V9 release gates ...")
    gates = require_release_gates(
        cases=cases,
        assignments=assignments,
        split_summary=split_summary,
        target_per_cell=args.target_per_cell,
        gap_report_path=args.v9_gap_report,
    )
    print("      release gates: clean")
    print(f"      target matrix: {gates['target_matrix']}")

    print("\n[4/6] Writing V9 query-grouped splits ...")
    normalized_cases = normalize_cases_for_json_loader(cases)
    by_split = {"train": [], "validation": [], "test": []}
    for case in normalized_cases:
        by_split[assignments[_case_id(case)]].append(case)
    split_counts = {
        split: write_parquet(rows, staging / "v9" / f"{split}.parquet")
        for split, rows in by_split.items()
    }
    split_class_counts = {split: _class_counts(rows) for split, rows in by_split.items()}
    for split in ("train", "validation", "test"):
        print(f"      {split:10s}: {split_counts[split]:,} rows {split_class_counts[split]}")

    write_jsonl(
        staging / "v9" / "split_assignments.jsonl",
        ({"case_id": case_id, "split": split} for case_id, split in sorted(assignments.items())),
    )

    print("\n[5/6] Writing dataset card ...")
    write_dataset_card(
        staging,
        version=args.version,
        split_counts=split_counts,
        split_class_counts=split_class_counts,
        n_all=len(cases),
        gates=gates,
        answerability_counts=_answerability_counts(cases),
        modality_counts=_modality_counts(cases),
    )

    files = sorted(file for file in staging.rglob("*") if file.is_file())
    total_mb = sum(file.stat().st_size for file in files) / 1e6
    print(f"\n[6/6] Staging ({total_mb:.2f} MB total):")
    for file in files:
        print(f"      {file.stat().st_size / 1e6:>7.2f} MB  {file.relative_to(staging)}")

    if args.dry_run:
        print(f"\n--dry-run: not uploading. Staging dir: {staging}")
        return 0

    print("\nImporting huggingface_hub ...")
    from huggingface_hub import HfApi, create_repo

    create_repo(repo_id=args.repo_id, repo_type="dataset", exist_ok=True)
    commit_msg = args.commit_message or f"fitz-gov v{args.version}: publish V9 target-100 vault"
    print(f"Uploading with commit: {commit_msg!r}")
    api = HfApi()
    commit = api.upload_folder(
        folder_path=str(staging),
        repo_id=args.repo_id,
        repo_type="dataset",
        commit_message=commit_msg,
        delete_patterns=[
            "*.jsonl",
            "*.parquet",
            "tier0_sanity.*",
            "tier1_core.*",
            "validation.*",
            "v6/*",
            "v7/*",
            "v8/*",
            "v9/*",
            "README.md",
        ],
    )
    print(f"Commit: {commit.oid}")

    if not args.no_tag:
        tag = f"v{args.version}"
        print(f"Creating tag: {tag}")
        api.create_tag(
            repo_id=args.repo_id,
            repo_type="dataset",
            tag=tag,
            tag_message=f"fitz-gov {tag}",
            revision=commit.oid,
            exist_ok=True,
        )

    print(f"\nDONE. https://huggingface.co/datasets/{args.repo_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
