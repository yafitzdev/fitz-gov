"""Merge V9 answerability generated JSONL rows into the SDGP vault.

Rows must have shape:

    {"case_id": "...", "case": {...}}

Use `--dry-run` first. Generated rows are candidate-only until this script
accepts them structurally and blind-label QA passes.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.checker import Checker, Severity, case_dedup_hash, hashes_from
from fitz_gov.sdgp.completeness import get_path
from fitz_gov.sdgp.modality import validate_modality
from fitz_gov.sdgp.retrieval_control_gap_detector import collapse_answerability_shape
from fitz_gov.sdgp.vault import Provenance, Vault, new_batch_id


FORBIDDEN_PATHS = (
    ("taxonomy", "subpattern"),
    ("taxonomy", "subpattern_cell_id"),
    ("taxonomy", "subpattern_description"),
    ("meta", "introduced_in"),
    ("meta", "domain"),
    ("meta", "subcategory"),
    ("meta", "reasoning_type"),
    ("meta", "query_type"),
    ("meta", "evidence_pattern"),
)

RETRIEVAL_ACTIONS = {
    "answer_now",
    "retrieve_more",
    "broaden_search",
    "resolve_conflict",
    "ask_clarifying_question",
    "structured_lookup",
}
GAP_TYPES = {
    "none",
    "missing_specific_fact",
    "missing_timeframe",
    "missing_comparison_side",
    "missing_source_authority",
    "conflicting_values",
    "wrong_entity",
    "wrong_version_or_scope",
    "too_broad",
    "incomplete_enumeration",
    "unsupported_inference",
    "ambiguous_query",
}
ANSWERABILITY_SHAPES = {
    "single_fact",
    "explanation",
    "list",
    "exhaustive_list",
    "comparison",
    "timeline",
    "calculation",
    "yes_no",
    "summary",
    "citation_required",
    "exact_lookup",
}
RETRIEVAL_MODALITIES = {
    "unstructured_text",
    "structured_table",
    "code",
    "configuration",
    "log_trace",
    "pdf_layout",
    "mixed",
}

CATEGORICAL_FIELDS = (
    ("retrieval_action", RETRIEVAL_ACTIONS),
    ("gap_type", GAP_TYPES),
    ("answerability_shape", ANSWERABILITY_SHAPES),
    ("preferred_retrieval_modality", RETRIEVAL_MODALITIES),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", type=Path, default=Path("data/fitz-gov"))
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/_workspaces/handoff/v9_answerability/subagent_outputs"),
    )
    parser.add_argument(
        "--batch-dir",
        type=Path,
        default=Path("data/_workspaces/handoff/v9_answerability/subagent_batches"),
    )
    parser.add_argument("--glob", type=str, default="batch_*.jsonl")
    parser.add_argument("--provider", type=str, default="codex_subagent")
    parser.add_argument("--provider-version", type=str, default="gpt-5.4")
    parser.add_argument("--batch-id", type=str, default=None)
    parser.add_argument(
        "--case-id-allowlist",
        type=Path,
        default=None,
        help=(
            "Optional JSONL/text allowlist. When set, only matching case_id rows are "
            "validated and merged. JSONL rows may contain a case_id field."
        ),
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            try:
                row = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: row must be a JSON object")
            rows.append(row)
    return rows


def _read_batch_spec(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: batch spec must be a JSON object")
    return data


def _read_case_id_allowlist(path: Path) -> set[str]:
    case_ids: set[str] = set()
    with path.open(encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            line = raw.strip()
            if not line:
                continue
            case_id: str | None = None
            if line.startswith("{"):
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
                if isinstance(row, dict):
                    value = row.get("case_id")
                    if isinstance(value, str) and value:
                        case_id = value
            else:
                case_id = line
            if not case_id:
                raise ValueError(f"{path}:{line_no}: no case_id found")
            case_ids.add(case_id)
    return case_ids


def _batch_spec_for_output(batch_dir: Path, output_path: Path) -> dict[str, Any] | None:
    return _read_batch_spec(batch_dir / f"{output_path.stem}.json")


def _slot_map(batch_dir: Path) -> dict[str, dict[str, Any]]:
    slots: dict[str, dict[str, Any]] = {}
    for path in sorted(batch_dir.glob("batch_*.json")):
        data = _read_batch_spec(path)
        if data is None:
            continue
        for slot in data.get("slots", []):
            if not isinstance(slot, dict):
                continue
            case_id = slot.get("case_id")
            if isinstance(case_id, str):
                slots[case_id] = slot
    return slots


def _expected_ids(batch_dir: Path, output_path: Path) -> set[str] | None:
    data = _batch_spec_for_output(batch_dir, output_path)
    if data is None:
        return None
    return {str(slot["case_id"]) for slot in data.get("slots", [])}


def _filter_expected_ids(
    expected: set[str] | None, case_id_allowlist: set[str] | None
) -> set[str] | None:
    if expected is None or case_id_allowlist is None:
        return expected
    return expected & case_id_allowlist


def _validate_id_set(path: Path, rows: list[dict[str, Any]], expected: set[str] | None) -> int:
    bad = 0
    ids = [row.get("case_id") for row in rows]
    counter = Counter(ids)
    duplicates = sorted(str(case_id) for case_id, count in counter.items() if count > 1)
    if duplicates:
        print(f"DUPLICATE IDS {path}: {duplicates[:10]}", file=sys.stderr)
        bad += len(duplicates)
    if expected is not None:
        got = {str(case_id) for case_id in ids if isinstance(case_id, str)}
        missing = sorted(expected - got)
        extra = sorted(got - expected)
        if missing:
            print(f"MISSING IDS {path}: {missing[:10]}", file=sys.stderr)
            bad += len(missing)
        if extra:
            print(f"EXTRA IDS {path}: {extra[:10]}", file=sys.stderr)
            bad += len(extra)
    return bad


def _get_nested(row: dict[str, Any], path: tuple[str, str]) -> Any:
    head, key = path
    block = row.get(head)
    if not isinstance(block, dict):
        return None
    return block.get(key)


def _forbidden_present(case: dict[str, Any]) -> list[str]:
    return [".".join(path) for path in FORBIDDEN_PATHS if _get_nested(case, path) is not None]


def _retrieval_block(case: dict[str, Any]) -> dict[str, Any] | None:
    routing = case.get("routing")
    if not isinstance(routing, dict):
        return None
    control = routing.get("retrieval_control")
    return control if isinstance(control, dict) else None


def _validate_label_object(
    *,
    case_id: str,
    control: dict[str, Any],
    field: str,
    allowed: set[str],
    errors: list[str],
) -> str | None:
    block = control.get(field)
    if not isinstance(block, dict):
        errors.append(f"{case_id}: routing.retrieval_control.{field} must be an object")
        return None
    kind = block.get("kind")
    if kind not in allowed:
        errors.append(f"{case_id}: routing.retrieval_control.{field}.kind={kind!r} is not allowed")
        return None
    for key in ("confidence", "rationale", "signals"):
        if key not in block:
            errors.append(f"{case_id}: routing.retrieval_control.{field}.{key} is missing")
    return str(kind)


def _validate_retrieval_control(
    case_id: str, case: dict[str, Any]
) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    kinds: dict[str, str] = {}
    control = _retrieval_block(case)
    if control is None:
        return kinds, [f"{case_id}: routing.retrieval_control must be an object"]
    for field, allowed in CATEGORICAL_FIELDS:
        kind = _validate_label_object(
            case_id=case_id,
            control=control,
            field=field,
            allowed=allowed,
            errors=errors,
        )
        if kind is not None:
            kinds[field] = kind

    severity = control.get("evidence_failure_severity")
    if not isinstance(severity, dict):
        errors.append(f"{case_id}: routing.retrieval_control.evidence_failure_severity missing")
    else:
        score = severity.get("score")
        if not isinstance(score, int | float) or isinstance(score, bool):
            errors.append(f"{case_id}: evidence_failure_severity.score must be numeric")
        elif not 0.0 <= float(score) <= 1.0:
            errors.append(f"{case_id}: evidence_failure_severity.score outside 0..1")
        for key in ("confidence", "rationale", "signals"):
            if key not in severity:
                errors.append(
                    f"{case_id}: routing.retrieval_control.evidence_failure_severity.{key} missing"
                )

    if "labeler" not in control:
        errors.append(f"{case_id}: routing.retrieval_control.labeler is missing")
    return kinds, errors


def _validate_query_contract(case_id: str, case: dict[str, Any]) -> list[str]:
    contract = get_path(case, "routing.query_contract")
    if not isinstance(contract, dict):
        return [f"{case_id}: routing.query_contract must be an object"]
    if not isinstance(contract.get("kind"), str) or not contract.get("kind"):
        return [f"{case_id}: routing.query_contract.kind is missing"]
    return []


def _normalize_case(case_id: str, case: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    original_id = case.get("id")
    if original_id is None:
        errors.append(f"{case_id}: case.id is missing")
    elif original_id != case_id:
        errors.append(f"{case_id}: case.id={original_id!r} does not match wrapper case_id")
    case["id"] = case_id

    version = case.get("version")
    if version is None:
        errors.append(f"{case_id}: version is missing")
    elif version != "fitz-gov-9.0":
        errors.append(f"{case_id}: version must be fitz-gov-9.0, got {version!r}")
    case["version"] = "fitz-gov-9.0"

    meta = case.get("meta")
    if not isinstance(meta, dict):
        errors.append(f"{case_id}: meta must be an object")
        meta = {}
        case["meta"] = meta
    dataset_version = meta.get("dataset_version")
    if dataset_version is None:
        errors.append(f"{case_id}: meta.dataset_version is missing")
    elif dataset_version != "v9":
        errors.append(f"{case_id}: meta.dataset_version must be v9, got {dataset_version!r}")
    meta["dataset_version"] = "v9"
    try:
        validate_modality(meta.get("modality"))
    except ValueError as exc:
        errors.append(f"{case_id}: {exc}")
    return errors


def _validate_slot_target(
    *,
    case_id: str,
    case: dict[str, Any],
    slot: dict[str, Any] | None,
    answerability_kind: str | None,
) -> list[str]:
    if slot is None:
        return [f"{case_id}: no matching batch slot"]
    errors: list[str] = []
    expected = {
        "governance_class": get_path(case, "governance.classification"),
        "domain": get_path(case, "routing.expert_fired"),
        "difficulty": get_path(case, "meta.difficulty"),
    }
    for key, actual in expected.items():
        if actual != slot.get(key):
            errors.append(f"{case_id}: {key}={actual!r}, expected {slot.get(key)!r}")
    if answerability_kind is not None:
        allowed = set(slot.get("allowed_detailed_answerability_shapes") or [])
        if answerability_kind not in allowed:
            errors.append(
                f"{case_id}: answerability_shape.kind={answerability_kind!r}, "
                f"expected one of {sorted(allowed)}"
            )
        try:
            collapsed = collapse_answerability_shape(answerability_kind).value
        except ValueError as exc:
            errors.append(f"{case_id}: {exc}")
        else:
            if collapsed != slot.get("collapsed_answerability_shape"):
                errors.append(
                    f"{case_id}: collapsed answerability={collapsed!r}, "
                    f"expected {slot.get('collapsed_answerability_shape')!r}"
                )
    return errors


def main() -> int:
    args = parse_args()
    vault = Vault.open(args.vault)
    files = sorted(args.out_dir.glob(args.glob))
    checker = Checker(require_training_schema=True)
    seen_hashes = hashes_from(vault.iter_cases())
    slots = _slot_map(args.batch_dir)
    batch_id = args.batch_id or new_batch_id()
    case_id_allowlist = (
        _read_case_id_allowlist(args.case_id_allowlist)
        if args.case_id_allowlist is not None
        else None
    )

    print("=== Merge V9 answerability JSONL ===")
    print(f"Vault    : {args.vault}")
    print(f"Out dir  : {args.out_dir}")
    print(f"Batch dir: {args.batch_dir}")
    print(f"Files    : {len(files)}")
    print(f"Slots    : {len(slots)}")
    print(f"Allowlist: {len(case_id_allowlist) if case_id_allowlist is not None else 'none'}")
    print(f"Dry run  : {args.dry_run}")
    print(f"Batch    : {batch_id}")
    print()

    n_rows = 0
    n_ok = 0
    n_bad = 0
    n_exists = 0
    n_skipped_allowlist = 0
    accepted: list[dict[str, Any]] = []

    for path in files:
        try:
            rows = _read_jsonl(path)
        except ValueError as exc:
            print(f"READ FAIL {exc}", file=sys.stderr)
            n_bad += 1
            continue
        if case_id_allowlist is not None:
            before = len(rows)
            rows = [
                row
                for row in rows
                if isinstance(row.get("case_id"), str) and row["case_id"] in case_id_allowlist
            ]
            n_skipped_allowlist += before - len(rows)
        expected_ids = _filter_expected_ids(_expected_ids(args.batch_dir, path), case_id_allowlist)
        n_bad += _validate_id_set(path, rows, expected_ids)

        for row in rows:
            n_rows += 1
            case_id = row.get("case_id")
            case = row.get("case")
            if not isinstance(case_id, str) or not isinstance(case, dict):
                print(f"BAD ROW {path}: expected string case_id + object case", file=sys.stderr)
                n_bad += 1
                continue
            if case_id in vault:
                n_exists += 1
                continue

            errors = _normalize_case(case_id, case)
            errors.extend(_validate_query_contract(case_id, case))
            kinds, control_errors = _validate_retrieval_control(case_id, case)
            errors.extend(control_errors)
            errors.extend(
                _validate_slot_target(
                    case_id=case_id,
                    case=case,
                    slot=slots.get(case_id),
                    answerability_kind=kinds.get("answerability_shape"),
                )
            )
            forbidden = _forbidden_present(case)
            if forbidden:
                errors.append(f"{case_id}: forbidden fields {forbidden}")
            if errors:
                for error in errors[:8]:
                    print(f"CHECK FAIL {error}", file=sys.stderr)
                n_bad += 1
                continue

            result = checker.check(case, seen_hashes=seen_hashes)
            has_errors = any(issue.severity == Severity.ERROR for issue in result.issues)
            if has_errors:
                reasons = "; ".join(f"{issue.rule}: {issue.message}" for issue in result.issues[:8])
                print(f"CHECK FAIL {case_id}: {reasons}", file=sys.stderr)
                n_bad += 1
                continue
            h = case_dedup_hash(case)
            if h:
                seen_hashes.add(h)
            accepted.append(case)
            n_ok += 1

    print(f"Rows read : {n_rows}")
    print(f"Accepted  : {n_ok}")
    print(f"Existing  : {n_exists}")
    print(f"Skipped   : {n_skipped_allowlist} (allowlist)")
    print(f"Rejected  : {n_bad}")

    if args.dry_run:
        print("Dry run: no vault updates written.")
        return 0 if n_bad == 0 else 1
    if n_bad:
        print("No vault updates written because rejected rows were found.", file=sys.stderr)
        return 1

    provenance = Provenance(
        provider=args.provider,
        provider_version=args.provider_version,
        prompt_version="v9-answerability-matrix",
        batch_id=batch_id,
    )
    result = vault.add_many(accepted, provenance=provenance)
    print(f"Added     : {result['added']}")
    print(f"Duplicate : {result['duplicate']}")
    print(f"Vault size: {len(vault)}")
    return 0 if n_bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
