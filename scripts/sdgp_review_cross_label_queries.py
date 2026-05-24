"""Review exact-query cross-label groups for incoherent evidence reuse.

The QA audit intentionally flags repeated raw queries across labels because
they are a leakage risk for naive splits. In fitz-gov they are not automatically
bad: the governed input is (query, contexts), so the same user query can be
TRUSTWORTHY, DISPUTED, or ABSTAIN depending on retrieved evidence.

This script checks the narrower release-blocking condition: same exact query
and materially reused evidence across different labels. It emits a small
review packet and can consume manual adjudications for shared-context pairs.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.qa import normalize_text
from fitz_gov.sdgp.vault import Vault


SPLIT = "||"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--vault", type=Path, default=Path("data/sdgp_vault_v51_enriched"))
    p.add_argument("--out-dir", type=Path, default=Path("data/sdgp_v7_qa"))
    p.add_argument(
        "--cohort",
        default="all",
        choices=("all", "v6", "v7"),
        help="Rows to review. Use all for the full V7 release-candidate vault.",
    )
    p.add_argument(
        "--jaccard-threshold",
        type=float,
        default=0.5,
        help="Context-set overlap threshold that requires review.",
    )
    p.add_argument(
        "--adjudications",
        type=Path,
        default=None,
        help="Optional JSON/JSONL manual adjudications keyed by pair_key.",
    )
    return p.parse_args()


def _dataset_version(case: Mapping[str, Any]) -> str:
    meta = case.get("meta") if isinstance(case.get("meta"), Mapping) else {}
    return str(meta.get("dataset_version") or "unknown")


def _label(case: Mapping[str, Any]) -> str:
    gov = case.get("governance") if isinstance(case.get("governance"), Mapping) else {}
    return str(gov.get("classification") or case.get("label") or "UNKNOWN").upper()


def _query(case: Mapping[str, Any]) -> str:
    input_block = case.get("input") if isinstance(case.get("input"), Mapping) else {}
    return str(input_block.get("query") or case.get("query") or "")


def _query_rewritten(case: Mapping[str, Any]) -> str:
    input_block = case.get("input") if isinstance(case.get("input"), Mapping) else {}
    return str(input_block.get("query_rewritten") or "")


def _contexts(case: Mapping[str, Any]) -> list[str]:
    input_block = case.get("input") if isinstance(case.get("input"), Mapping) else {}
    raw_contexts = input_block.get("contexts") or case.get("contexts") or []
    if not isinstance(raw_contexts, list):
        return []
    out: list[str] = []
    for item in raw_contexts:
        if isinstance(item, Mapping):
            text = item.get("text")
        else:
            text = item
        normalized = normalize_text(text)
        if normalized:
            out.append(normalized)
    return out


def _pattern(case: Mapping[str, Any]) -> str:
    taxonomy = case.get("taxonomy") if isinstance(case.get("taxonomy"), Mapping) else {}
    return str(taxonomy.get("pattern") or "")


def _case_id(case: Mapping[str, Any]) -> str:
    return str(case.get("id") or "")


def _cohort_cases(cases: Iterable[dict[str, Any]], cohort: str) -> list[dict[str, Any]]:
    if cohort == "all":
        return list(cases)
    return [case for case in cases if _dataset_version(case) == cohort]


def _pair_key(left_id: str, right_id: str) -> str:
    return SPLIT.join(sorted((left_id, right_id)))


def _load_adjudications(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None or not path.exists():
        return {}

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return {}

    rows: list[dict[str, Any]]
    if text.startswith("["):
        rows = json.loads(text)
    else:
        rows = [json.loads(line) for line in text.splitlines() if line.strip()]

    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = str(row.get("pair_key") or "")
        if not key:
            ids = row.get("case_ids")
            if isinstance(ids, list) and len(ids) == 2:
                key = _pair_key(str(ids[0]), str(ids[1]))
        if key:
            out[key] = row
    return out


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def _jsonl(rows: Iterable[Mapping[str, Any]]) -> str:
    return "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n"


def _markdown(summary: Mapping[str, Any], candidates: list[Mapping[str, Any]]) -> str:
    lines = [
        "# Cross-Label Query Semantic Review",
        "",
        f"Vault rows reviewed: **{summary['rows_reviewed']}**",
        f"Cohort: **{summary['cohort']}**",
        "",
        "## Result",
        "",
        f"Status: **{summary['status']}**",
        f"Cross-label exact-query groups: **{summary['cross_label_query_groups']}**",
        f"Rows in those groups: **{summary['cross_label_query_rows']}**",
        f"Exact same context-set cross-label pairs: **{summary['exact_same_context_set_pairs']}**",
        f"Shared-context cross-label pairs: **{summary['shared_context_pairs']}**",
        f"High-overlap review pairs: **{summary['high_overlap_pairs']}**",
        f"Adjudicated valid pairs: **{summary['adjudicated_valid_pairs']}**",
        f"Unresolved review pairs: **{summary['unresolved_review_pairs']}**",
        "",
        "## Decision Rule",
        "",
        (
            "Repeated raw queries are allowed when retrieved contexts differ; the release blocker is "
            "a cross-label pair with the same query and materially equivalent evidence."
        ),
        "",
    ]
    if candidates:
        lines.extend(["## Reviewed Pairs", ""])
        for item in candidates:
            lines.append(
                "- "
                + f"`{item['pair_key']}`: {item['left']['label']} vs {item['right']['label']}; "
                + f"jaccard={item['context_jaccard']:.3f}; "
                + f"adjudication={item.get('adjudication', {}).get('status', 'unresolved')}"
            )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    vault = Vault.open(args.vault)
    cases = _cohort_cases(vault.iter_cases(), args.cohort)
    adjudications = _load_adjudications(args.adjudications)

    by_query: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in cases:
        key = normalize_text(_query(case))
        if key:
            by_query[key].append(case)

    cross_groups: list[tuple[str, list[dict[str, Any]]]] = []
    for query_key, group in by_query.items():
        labels = {_label(case) for case in group}
        if len(group) > 1 and len(labels) > 1:
            cross_groups.append((query_key, group))

    candidates: list[dict[str, Any]] = []
    exact_same_context_set_pairs = 0
    shared_context_pairs = 0
    high_overlap_pairs = 0
    for query_key, group in cross_groups:
        context_sets = [(case, set(_contexts(case))) for case in group]
        for idx, (left, left_contexts) in enumerate(context_sets):
            for right, right_contexts in context_sets[idx + 1 :]:
                left_label = _label(left)
                right_label = _label(right)
                if left_label == right_label:
                    continue
                intersection = left_contexts & right_contexts
                union = left_contexts | right_contexts
                jaccard = len(intersection) / len(union) if union else 0.0
                same_context_set = bool(left_contexts) and left_contexts == right_contexts
                shared_context = bool(intersection)
                high_overlap = jaccard >= args.jaccard_threshold
                if same_context_set:
                    exact_same_context_set_pairs += 1
                if shared_context:
                    shared_context_pairs += 1
                if high_overlap:
                    high_overlap_pairs += 1
                if not (same_context_set or shared_context or high_overlap):
                    continue

                key = _pair_key(_case_id(left), _case_id(right))
                candidates.append(
                    {
                        "pair_key": key,
                        "query": query_key,
                        "same_context_set": same_context_set,
                        "shared_context_count": len(intersection),
                        "context_jaccard": jaccard,
                        "left": {
                            "case_id": _case_id(left),
                            "label": left_label,
                            "pattern": _pattern(left),
                            "query_rewritten": _query_rewritten(left),
                        },
                        "right": {
                            "case_id": _case_id(right),
                            "label": right_label,
                            "pattern": _pattern(right),
                            "query_rewritten": _query_rewritten(right),
                        },
                        "adjudication": adjudications.get(key, {}),
                    }
                )

    review_candidates = [item for item in candidates if item["shared_context_count"] or item["context_jaccard"] >= args.jaccard_threshold]
    adjudicated_valid = [
        item
        for item in review_candidates
        if str(item.get("adjudication", {}).get("status") or "").lower() == "valid"
    ]
    unresolved = [
        item
        for item in review_candidates
        if str(item.get("adjudication", {}).get("status") or "").lower() not in {"valid", "fixed", "accepted"}
    ]
    blocking = [
        item
        for item in candidates
        if item["same_context_set"]
        and str(item.get("adjudication", {}).get("status") or "").lower() not in {"fixed", "accepted"}
    ]

    label_mix = Counter()
    for _, group in cross_groups:
        labels = tuple(sorted({_label(case) for case in group}))
        label_mix[" + ".join(labels)] += 1

    summary = {
        "status": "passed" if not blocking and not unresolved else "needs_review",
        "vault": str(args.vault),
        "cohort": args.cohort,
        "rows_reviewed": len(cases),
        "cross_label_query_groups": len(cross_groups),
        "cross_label_query_rows": sum(len(group) for _, group in cross_groups),
        "label_mix": dict(sorted(label_mix.items())),
        "exact_same_context_set_pairs": exact_same_context_set_pairs,
        "shared_context_pairs": shared_context_pairs,
        "high_overlap_pairs": high_overlap_pairs,
        "adjudicated_valid_pairs": len(adjudicated_valid),
        "unresolved_review_pairs": len(unresolved),
        "blocking_pairs": len(blocking),
        "jaccard_threshold": args.jaccard_threshold,
        "adjudications": str(args.adjudications) if args.adjudications else None,
        "artifacts": {
            "summary": "cross_label_query_semantic_review_summary.json",
            "candidates": "cross_label_query_semantic_review_candidates.jsonl",
            "report": "cross_label_query_semantic_review.md",
        },
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    _write_json(args.out_dir / "cross_label_query_semantic_review_summary.json", summary)
    (args.out_dir / "cross_label_query_semantic_review_candidates.jsonl").write_text(
        _jsonl(candidates), encoding="utf-8"
    )
    (args.out_dir / "cross_label_query_semantic_review.md").write_text(
        _markdown(summary, candidates), encoding="utf-8"
    )

    print("=== Cross-label query semantic review ===")
    print(f"Status       : {summary['status']}")
    print(f"Rows reviewed: {summary['rows_reviewed']}")
    print(f"Groups       : {summary['cross_label_query_groups']}")
    print(f"Rows in groups: {summary['cross_label_query_rows']}")
    print(f"Same ctx set : {summary['exact_same_context_set_pairs']}")
    print(f"Shared ctx   : {summary['shared_context_pairs']}")
    print(f"Unresolved   : {summary['unresolved_review_pairs']}")
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
