"""Normalize a V8 candidate handoff into checker-ready JSONL batches.

This is for candidate-row repair only. It does not touch the active vault.

The normalizer preserves usable generated query/context text, repairs canonical
SDGP fields from the batch slot spec, and falls back to the deterministic V8
template generator for missing, malformed, duplicate, or still-invalid rows.
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.checker import Checker, Severity, case_dedup_hash, hashes_from
from fitz_gov.sdgp.taxonomy import (
    PATTERN_DESCRIPTIONS,
    Difficulty,
    Domain,
    GovernanceClass,
    TaxonomyPattern,
)
from fitz_gov.sdgp.vault import Vault


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
    ("source_type",),
    ("_vault",),
)

CATEGORY_BY_CLASS = {
    "ABSTAIN": "abstention",
    "DISPUTED": "dispute",
    "TRUSTWORTHY": "trustworthy_direct",
}

CONFIDENCE_BY_DIFFICULTY = {
    "easy": "high",
    "medium": "medium",
    "hard": "borderline",
}

ALLOWED_STALENESS = {"none", "low", "medium", "high"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--vault",
        type=Path,
        default=Path("data/fitz-gov"),
        help="Active vault used only for duplicate-content checks.",
    )
    p.add_argument(
        "--batch-dir",
        type=Path,
        required=True,
        help="Directory containing batch_*.json specs.",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Directory containing original generated batch_*.jsonl outputs.",
    )
    p.add_argument(
        "--normalized-dir",
        type=Path,
        required=True,
        help="Directory to write normalized batch_*.jsonl outputs.",
    )
    p.add_argument("--glob", type=str, default="batch_*.jsonl")
    return p.parse_args()


def _load_template_module() -> Any:
    path = Path(__file__).with_name("sdgp_generate_v8_template_outputs.py")
    spec = importlib.util.spec_from_file_location("sdgp_generate_v8_template_outputs", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load template generator at {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TEMPLATE = _load_template_module()


def _read_text_lossy(path: Path, stats: Counter[str]) -> str | None:
    raw = path.read_bytes()
    for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            text = raw.decode(encoding)
        except UnicodeDecodeError:
            continue
        if encoding != "utf-8":
            stats[f"decoded_{encoding}"] += 1
        return text
    stats["decode_failed"] += 1
    return None


def _parse_json_objects(text: str, path: Path, stats: Counter[str]) -> list[dict[str, Any]]:
    decoder = json.JSONDecoder()
    out: list[dict[str, Any]] = []
    for line_no, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            pos = 0
            parsed_any = False
            while pos < len(line):
                while pos < len(line) and line[pos].isspace():
                    pos += 1
                if pos >= len(line):
                    break
                try:
                    row, end = decoder.raw_decode(line, pos)
                except json.JSONDecodeError:
                    stats["json_parse_failed"] += 1
                    stats[f"json_parse_failed:{path.name}:{line_no}"] += 1
                    break
                parsed_any = True
                if isinstance(row, dict):
                    out.append(row)
                else:
                    stats["json_non_object"] += 1
                pos = end
            if parsed_any:
                stats["split_concatenated_json"] += 1
            continue
        if isinstance(row, dict):
            out.append(row)
        else:
            stats["json_non_object"] += 1
    return out


def _load_candidate_rows(out_dir: Path, glob: str, stats: Counter[str]) -> dict[str, dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    duplicates: Counter[str] = Counter()
    for path in sorted(out_dir.glob(glob)):
        text = _read_text_lossy(path, stats)
        if text is None:
            continue
        rows = _parse_json_objects(text, path, stats)
        stats["input_files"] += 1
        stats["input_rows"] += len(rows)
        for row in rows:
            case_id = row.get("case_id")
            case = row.get("case")
            if not isinstance(case_id, str) and isinstance(case, dict):
                raw_id = case.get("id")
                if isinstance(raw_id, str):
                    case_id = raw_id
            if not isinstance(case_id, str):
                stats["row_missing_case_id"] += 1
                continue
            if not isinstance(case, dict):
                stats["row_missing_case_object"] += 1
                continue
            if case_id in by_id:
                duplicates[case_id] += 1
                continue
            by_id[case_id] = row
    stats["duplicate_case_ids"] = sum(duplicates.values())
    return by_id


def _load_batches(batch_dir: Path) -> list[tuple[Path, list[dict[str, Any]]]]:
    batches: list[tuple[Path, list[dict[str, Any]]]] = []
    for path in sorted(batch_dir.glob("batch_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        slots = [slot for slot in data.get("slots", []) if isinstance(slot, dict)]
        batches.append((path, slots))
    return batches


def _delete_path(obj: dict[str, Any], path: tuple[str, ...]) -> None:
    cur: Any = obj
    for key in path[:-1]:
        if not isinstance(cur, dict):
            return
        cur = cur.get(key)
    if isinstance(cur, dict):
        cur.pop(path[-1], None)


def _as_score(value: Any, default: float) -> float:
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return max(0.0, min(1.0, float(value)))
    return default


def _first_sentence(text: str, max_len: int = 180) -> str:
    compact = " ".join(str(text).split())
    if not compact:
        return "The context provides retrieved evidence for the case."
    stops = [compact.find(mark) for mark in (". ", "? ", "! ") if compact.find(mark) != -1]
    if stops:
        compact = compact[: min(stops) + 1]
    return compact[:max_len].rstrip()


def _slot_class(slot: dict[str, Any]) -> str:
    return str(slot["governance_class"])


def _slot_difficulty(slot: dict[str, Any]) -> str:
    return str(slot["difficulty"])


def _normalize_contexts(
    candidate: dict[str, Any],
    fallback: dict[str, Any],
    slot: dict[str, Any],
) -> list[dict[str, Any]]:
    raw_contexts = []
    input_block = candidate.get("input") if isinstance(candidate.get("input"), dict) else {}
    if isinstance(input_block, dict) and isinstance(input_block.get("contexts"), list):
        raw_contexts = input_block["contexts"]
    elif isinstance(candidate.get("contexts"), list):
        raw_contexts = candidate["contexts"]

    if not raw_contexts:
        return copy.deepcopy(fallback["input"]["contexts"])

    out: list[dict[str, Any]] = []
    fallback_contexts = fallback["input"]["contexts"]
    for idx, raw in enumerate(raw_contexts, start=1):
        fb = fallback_contexts[min(idx - 1, len(fallback_contexts) - 1)]
        if isinstance(raw, str):
            ctx: dict[str, Any] = {"text": raw}
        elif isinstance(raw, dict):
            ctx = dict(raw)
        else:
            continue
        ctx_id = ctx.get("id")
        if not isinstance(ctx_id, str) or not ctx_id.strip():
            ctx_id = f"ctx_{idx:03d}"
        text = ctx.get("text")
        if not isinstance(text, str) or not text.strip():
            continue
        temporality = ctx.get("temporality") if isinstance(ctx.get("temporality"), dict) else {}
        stale = temporality.get("staleness_risk")
        if stale not in ALLOWED_STALENESS:
            stale = fb.get("temporality", {}).get("staleness_risk", "low")
        out.append(
            {
                "id": ctx_id,
                "text": text,
                "authority_score": _as_score(ctx.get("authority_score"), fb["authority_score"]),
                "authority_signal": str(ctx.get("authority_signal") or fb["authority_signal"]),
                "temporality": {
                    "is_time_sensitive": bool(
                        temporality.get(
                            "is_time_sensitive",
                            fb.get("temporality", {}).get("is_time_sensitive", True),
                        )
                    ),
                    "anchor_period": str(
                        temporality.get("anchor_period")
                        or fb.get("temporality", {}).get("anchor_period")
                        or f"{slot['cell_id']} candidate"
                    ),
                    "staleness_risk": stale,
                },
                "summary": str(ctx.get("summary") or _first_sentence(text)),
                "relevance_to_query": _as_score(ctx.get("relevance_to_query"), fb["relevance_to_query"]),
                "boundary_quality": _as_score(ctx.get("boundary_quality"), fb["boundary_quality"]),
            }
        )
    return out or copy.deepcopy(fallback["input"]["contexts"])


def _valid_non_actual_class(value: Any, actual: str, default: str) -> str:
    if isinstance(value, str) and value != actual:
        try:
            GovernanceClass(value)
            return value
        except ValueError:
            pass
    return default


def _normalize_evaluation(candidate: dict[str, Any], fallback: dict[str, Any], actual: str) -> dict[str, Any]:
    raw = candidate.get("evaluation") if isinstance(candidate.get("evaluation"), dict) else {}
    fb = fallback["evaluation"]
    out = {
        "mode": "governance",
        "check_mode_match": True,
        "required_elements": raw.get("required_elements")
        if isinstance(raw.get("required_elements"), list)
        else copy.deepcopy(fb["required_elements"]),
        "forbidden_claims": raw.get("forbidden_claims")
        if isinstance(raw.get("forbidden_claims"), list)
        else copy.deepcopy(fb["forbidden_claims"]),
        "forbidden_elements": raw.get("forbidden_elements")
        if isinstance(raw.get("forbidden_elements"), list)
        else copy.deepcopy(fb["forbidden_elements"]),
    }
    if actual == "TRUSTWORTHY" and not out["required_elements"]:
        out["required_elements"] = copy.deepcopy(fb["required_elements"]) or ["resolved final answer"]
    return out


def _normalize_grounding_targets(
    candidate: dict[str, Any],
    fallback: dict[str, Any],
    contexts: list[dict[str, Any]],
    query: str,
) -> dict[str, Any]:
    meta = candidate.get("meta") if isinstance(candidate.get("meta"), dict) else {}
    raw = meta.get("grounding_targets") if isinstance(meta.get("grounding_targets"), dict) else {}
    valid_ids = [ctx["id"] for ctx in contexts]
    fallback_targets = fallback.get("meta", {}).get("grounding_targets", {})

    gold = raw.get("gold_answer")
    if not isinstance(gold, str) or not gold.strip():
        gold = fallback_targets.get("gold_answer")
    if not isinstance(gold, str) or not gold.strip():
        gold = f"The retrieved source-of-record evidence supports the requested answer for: {query}"

    sentences: list[dict[str, Any]] = []
    raw_sentences = raw.get("sentences")
    if isinstance(raw_sentences, list):
        for item in raw_sentences:
            if not isinstance(item, dict):
                continue
            text = item.get("text")
            attrs = item.get("attributions")
            if not isinstance(text, str) or not text.strip():
                continue
            if not isinstance(attrs, list):
                attrs = []
            good_attrs = [attr for attr in attrs if attr in valid_ids]
            sentences.append({"text": text, "attributions": good_attrs or valid_ids[-1:]})
    if not sentences:
        sentences = [{"text": gold, "attributions": valid_ids[-1:] or ["ctx_001"]}]
    return {"gold_answer": gold, "sentences": sentences}


def _normalize_candidate(slot: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    fallback = TEMPLATE.build_case(slot)
    candidate = copy.deepcopy(row.get("case") if isinstance(row.get("case"), dict) else {})
    for path in FORBIDDEN_PATHS:
        _delete_path(candidate, path)

    actual = _slot_class(slot)
    difficulty = _slot_difficulty(slot)
    pattern = TaxonomyPattern(str(slot["pattern"]))
    domain = Domain(str(slot["domain"]))
    diff_enum = Difficulty(difficulty)

    input_block = candidate.get("input") if isinstance(candidate.get("input"), dict) else {}
    query = input_block.get("query") if isinstance(input_block.get("query"), str) else None
    query = query.strip() if query and query.strip() else fallback["input"]["query"]
    query_rewritten = (
        input_block.get("query_rewritten")
        if isinstance(input_block.get("query_rewritten"), str)
        else None
    )
    query_rewritten = (
        query_rewritten.strip()
        if query_rewritten and query_rewritten.strip()
        else fallback["input"]["query_rewritten"]
    )
    contexts = _normalize_contexts(candidate, fallback, slot)
    context_ids = [ctx["id"] for ctx in contexts]

    case = {
        "id": slot["case_id"],
        "version": "fitz-gov-8.0",
        "input": {
            "query": query,
            "query_rewritten": query_rewritten,
            "contexts": contexts,
        },
        "governance": copy.deepcopy(fallback["governance"]),
        "taxonomy": {
            "governance_class": actual,
            "pattern": pattern.value,
            "pattern_description": PATTERN_DESCRIPTIONS[pattern],
            "cell_id": str(slot["cell_id"]),
        },
        "evaluation": _normalize_evaluation(candidate, fallback, actual),
        "routing": {
            "expert_fired": domain.value,
            "secondary_expert": "conflict_detection" if actual == "DISPUTED" else None,
            "routing_confidence": fallback["routing"]["routing_confidence"],
        },
        "meta": {
            "dataset_version": "v8",
            "difficulty": diff_enum.value,
            "category": CATEGORY_BY_CLASS[actual],
            "confidence_level": CONFIDENCE_BY_DIFFICULTY[diff_enum.value],
            "near_miss_class": _valid_non_actual_class(
                (candidate.get("meta") or {}).get("near_miss_class")
                if isinstance(candidate.get("meta"), dict)
                else None,
                actual,
                fallback["meta"]["near_miss_class"],
            ),
            "near_miss_reason": (
                (candidate.get("meta") or {}).get("near_miss_reason")
                if isinstance(candidate.get("meta"), dict)
                and isinstance((candidate.get("meta") or {}).get("near_miss_reason"), str)
                and (candidate.get("meta") or {}).get("near_miss_reason").strip()
                else fallback["meta"]["near_miss_reason"]
            ),
        },
    }
    if len(context_ids) >= 2:
        raw_chain = input_block.get("evidence_chain") if isinstance(input_block, dict) else None
        reasoning = raw_chain.get("reasoning") if isinstance(raw_chain, dict) else None
        case["input"]["evidence_chain"] = {
            "order": context_ids,
            "reasoning": reasoning
            if isinstance(reasoning, str) and reasoning.strip()
            else fallback["input"]["evidence_chain"]["reasoning"],
        }

    if actual == "TRUSTWORTHY":
        case["meta"]["grounding_targets"] = _normalize_grounding_targets(
            candidate,
            fallback,
            contexts,
            query,
        )
    return case


def _check_case(case: dict[str, Any], checker: Checker, seen_hashes: set[str]) -> list[str]:
    result = checker.check(case, seen_hashes=seen_hashes)
    return [
        f"{issue.rule}: {issue.message}"
        for issue in result.issues
        if issue.severity == Severity.ERROR
    ]


def main() -> int:
    args = parse_args()
    stats: Counter[str] = Counter()
    candidate_rows = _load_candidate_rows(args.out_dir, args.glob, stats)
    batches = _load_batches(args.batch_dir)
    checker = Checker(require_training_schema=True)
    seen_hashes = hashes_from(Vault.open(args.vault).iter_cases())
    args.normalized_dir.mkdir(parents=True, exist_ok=True)

    error_samples: dict[str, list[str]] = defaultdict(list)
    source_counts: Counter[str] = Counter()
    batch_count = 0
    row_count = 0

    for batch_path, slots in batches:
        out_rows: list[dict[str, Any]] = []
        for slot in slots:
            case_id = str(slot["case_id"])
            row = candidate_rows.get(case_id)
            source = "candidate_normalized"
            if row is None:
                case = TEMPLATE.build_case(slot)
                source = "fallback_missing"
            else:
                case = _normalize_candidate(slot, row)
                errors = _check_case(case, checker, seen_hashes)
                if errors:
                    source = "fallback_invalid_candidate"
                    for msg in errors[:3]:
                        error_samples[msg].append(case_id)
                    case = TEMPLATE.build_case(slot)
            fallback_errors = _check_case(case, checker, seen_hashes)
            if fallback_errors:
                source = "unresolved"
                for msg in fallback_errors[:3]:
                    error_samples[msg].append(case_id)
            else:
                h = case_dedup_hash(case)
                if h:
                    seen_hashes.add(h)
            source_counts[source] += 1
            out_rows.append({"case_id": case_id, "case": case})
            row_count += 1
        out_path = args.normalized_dir / f"{batch_path.stem}.jsonl"
        out_path.write_text(
            "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in out_rows),
            encoding="utf-8",
        )
        batch_count += 1

    summary = {
        "batch_dir": str(args.batch_dir),
        "source_dir": str(args.out_dir),
        "normalized_dir": str(args.normalized_dir),
        "batches": batch_count,
        "rows": row_count,
        "candidate_rows_by_id": len(candidate_rows),
        "input_stats": dict(stats),
        "source_counts": dict(source_counts),
        "error_samples": {k: v[:10] for k, v in sorted(error_samples.items())},
    }
    (args.normalized_dir / "normalization_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )

    print("=== Normalize V8 candidate handoff ===")
    print(f"Source files       : {stats.get('input_files', 0)}")
    print(f"Parsed input rows  : {stats.get('input_rows', 0)}")
    print(f"Unique candidates  : {len(candidate_rows)}")
    print(f"Output batches     : {batch_count}")
    print(f"Output rows        : {row_count}")
    for key, count in source_counts.most_common():
        print(f"{key:24}: {count}")
    if error_samples:
        print(f"Candidate rows falling back due to checker errors: {source_counts.get('fallback_invalid_candidate', 0)}")
    print(f"Summary            : {args.normalized_dir / 'normalization_summary.json'}")
    return 0 if source_counts.get("unresolved", 0) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
