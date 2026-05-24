"""QA utilities for V7 release-candidate audits.

The checks here are intentionally data-only. They do not relabel cases; they
identify leakage risks, exact duplicates, and blind-label work queues so a
separate model or human pass can make quality decisions.
"""

from __future__ import annotations

import hashlib
import json
import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from .checker import case_dedup_hash


SPLITS = ("train", "validation", "test")


def normalize_text(value: Any) -> str:
    """Normalize text for exact duplicate/leakage grouping."""
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def short_hash(value: Any, *, length: int = 16) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:length]


def case_id(case: Mapping[str, Any]) -> str:
    return str(case.get("id") or "")


def dataset_version(case: Mapping[str, Any]) -> str:
    meta = case.get("meta") if isinstance(case.get("meta"), Mapping) else {}
    return str(meta.get("dataset_version") or "unknown")


def label(case: Mapping[str, Any]) -> str:
    gov = case.get("governance") if isinstance(case.get("governance"), Mapping) else {}
    raw = gov.get("classification") or case.get("label") or case.get("expected_mode") or "UNKNOWN"
    return str(raw).upper()


def query(case: Mapping[str, Any]) -> str:
    input_block = case.get("input") if isinstance(case.get("input"), Mapping) else {}
    return str(input_block.get("query") or case.get("query") or "")


def query_key(case: Mapping[str, Any]) -> str:
    return normalize_text(query(case))


def contexts(case: Mapping[str, Any]) -> list[dict[str, str]]:
    input_block = case.get("input") if isinstance(case.get("input"), Mapping) else {}
    raw_contexts = input_block.get("contexts") or case.get("contexts") or []
    out: list[dict[str, str]] = []
    if not isinstance(raw_contexts, Sequence) or isinstance(raw_contexts, (str, bytes)):
        return out
    for idx, item in enumerate(raw_contexts, start=1):
        if isinstance(item, Mapping):
            cid = str(item.get("id") or f"ctx_{idx:03d}")
            text = str(item.get("text") or "")
        else:
            cid = f"ctx_{idx:03d}"
            text = str(item)
        out.append({"id": cid, "text": text})
    return out


def context_key(case: Mapping[str, Any]) -> list[str]:
    return [normalize_text(ctx["text"]) for ctx in contexts(case)]


def exact_input_hash(case: Mapping[str, Any]) -> str:
    return short_hash({"query": query_key(case), "contexts": context_key(case)}, length=32)


def exact_input_label_hash(case: Mapping[str, Any]) -> str:
    return short_hash(
        {"query": query_key(case), "contexts": context_key(case), "label": label(case)},
        length=32,
    )


def taxonomy_cell(case: Mapping[str, Any]) -> str:
    taxonomy = case.get("taxonomy") if isinstance(case.get("taxonomy"), Mapping) else {}
    return str(taxonomy.get("cell_id") or "")


def taxonomy_pattern(case: Mapping[str, Any]) -> str:
    taxonomy = case.get("taxonomy") if isinstance(case.get("taxonomy"), Mapping) else {}
    return str(taxonomy.get("pattern") or "")


def domain(case: Mapping[str, Any]) -> str:
    meta = case.get("meta") if isinstance(case.get("meta"), Mapping) else {}
    routing = case.get("routing") if isinstance(case.get("routing"), Mapping) else {}
    cell = taxonomy_cell(case)
    if cell:
        parts = cell.split("__")
        if len(parts) >= 3:
            return parts[1]
    return str(meta.get("domain") or routing.get("expert_fired") or "unknown")


def difficulty(case: Mapping[str, Any]) -> str:
    meta = case.get("meta") if isinstance(case.get("meta"), Mapping) else {}
    cell = taxonomy_cell(case)
    if cell:
        parts = cell.split("__")
        if len(parts) >= 3:
            return parts[2]
    return str(meta.get("difficulty") or "unknown")


@dataclass(frozen=True, slots=True)
class CaseRow:
    case_id: str
    dataset_version: str
    label: str
    query_key: str
    query_hash: str
    exact_input_hash: str
    exact_input_label_hash: str
    checker_hash: str
    cell_id: str
    pattern: str
    domain: str
    difficulty: str


def rows_from_cases(cases: Iterable[Mapping[str, Any]]) -> list[CaseRow]:
    rows: list[CaseRow] = []
    for case in cases:
        q_key = query_key(case)
        rows.append(
            CaseRow(
                case_id=case_id(case),
                dataset_version=dataset_version(case),
                label=label(case),
                query_key=q_key,
                query_hash=short_hash(q_key),
                exact_input_hash=exact_input_hash(case),
                exact_input_label_hash=exact_input_label_hash(case),
                checker_hash=case_dedup_hash(dict(case)),
                cell_id=taxonomy_cell(case),
                pattern=taxonomy_pattern(case),
                domain=domain(case),
                difficulty=difficulty(case),
            )
        )
    return rows


def duplicate_groups(
    rows: Iterable[CaseRow],
    key_name: str,
    *,
    min_size: int = 2,
) -> list[dict[str, Any]]:
    buckets: dict[str, list[CaseRow]] = defaultdict(list)
    for row in rows:
        key = getattr(row, key_name)
        if key:
            buckets[str(key)].append(row)

    groups: list[dict[str, Any]] = []
    for key, items in buckets.items():
        if len(items) < min_size:
            continue
        labels = Counter(row.label for row in items)
        groups.append(
            {
                "key": key,
                "size": len(items),
                "labels": dict(sorted(labels.items())),
                "case_ids": [row.case_id for row in items],
            }
        )
    return sorted(groups, key=lambda g: (-int(g["size"]), str(g["key"])))


def query_duplicate_groups(rows: Iterable[CaseRow]) -> list[dict[str, Any]]:
    groups = duplicate_groups(rows, "query_key")
    for group in groups:
        group["query_hash"] = short_hash(group["key"])
        group["query"] = group.pop("key")
    return groups


def cross_label_query_groups(rows: Iterable[CaseRow]) -> list[dict[str, Any]]:
    return [g for g in query_duplicate_groups(rows) if len(g["labels"]) > 1]


def summarize_rows(rows: Sequence[CaseRow]) -> dict[str, Any]:
    return {
        "rows": len(rows),
        "dataset_versions": dict(sorted(Counter(r.dataset_version for r in rows).items())),
        "labels": dict(sorted(Counter(r.label for r in rows).items())),
        "domains": dict(sorted(Counter(r.domain for r in rows).items())),
        "difficulties": dict(sorted(Counter(r.difficulty for r in rows).items())),
        "cells": len({r.cell_id for r in rows if r.cell_id}),
    }


def duplicate_summary(rows: Sequence[CaseRow]) -> dict[str, Any]:
    id_groups = duplicate_groups(rows, "case_id")
    exact_input_groups = duplicate_groups(rows, "exact_input_hash")
    exact_input_label_groups = duplicate_groups(rows, "exact_input_label_hash")
    checker_hash_groups = duplicate_groups(rows, "checker_hash")
    query_groups = query_duplicate_groups(rows)
    cross_label_groups = [g for g in query_groups if len(g["labels"]) > 1]
    return {
        "duplicate_ids": {
            "groups": len(id_groups),
            "rows": sum(int(g["size"]) for g in id_groups),
        },
        "duplicate_exact_input": {
            "groups": len(exact_input_groups),
            "rows": sum(int(g["size"]) for g in exact_input_groups),
        },
        "duplicate_exact_input_with_label": {
            "groups": len(exact_input_label_groups),
            "rows": sum(int(g["size"]) for g in exact_input_label_groups),
        },
        "duplicate_checker_hash": {
            "groups": len(checker_hash_groups),
            "rows": sum(int(g["size"]) for g in checker_hash_groups),
        },
        "exact_query_duplicates": {
            "groups": len(query_groups),
            "rows": sum(int(g["size"]) for g in query_groups),
        },
        "cross_label_query_duplicates": {
            "groups": len(cross_label_groups),
            "rows": sum(int(g["size"]) for g in cross_label_groups),
        },
    }


def assign_query_grouped_splits(
    rows: Sequence[CaseRow],
    *,
    seed: int = 20260522,
    ratios: Mapping[str, float] | None = None,
) -> dict[str, str]:
    """Assign case IDs to train/validation/test without splitting query groups."""
    ratios = dict(ratios or {"train": 0.8, "validation": 0.1, "test": 0.1})
    total_ratio = sum(float(ratios.get(split, 0.0)) for split in SPLITS)
    if total_ratio <= 0:
        raise ValueError("split ratios must sum to a positive value")
    ratios = {split: float(ratios.get(split, 0.0)) / total_ratio for split in SPLITS}

    grouped: dict[str, list[CaseRow]] = defaultdict(list)
    for row in rows:
        grouped[row.query_key].append(row)

    rng = random.Random(seed)
    groups = list(grouped.values())
    groups.sort(key=lambda g: (-len(g), rng.random()))

    targets = {split: ratios[split] * len(rows) for split in SPLITS}
    counts = {split: 0 for split in SPLITS}
    assignments: dict[str, str] = {}
    for group in groups:
        size = len(group)

        def score(split: str) -> tuple[float, int, str]:
            target = max(targets[split], 1.0)
            after = counts[split] + size
            overflow = max(0.0, after - target) / target
            fill = after / target
            return (overflow, fill, split)

        chosen = min(SPLITS, key=score)
        for row in group:
            assignments[row.case_id] = chosen
        counts[chosen] += size
    return assignments


def split_summary(rows: Sequence[CaseRow], assignments: Mapping[str, str]) -> dict[str, Any]:
    by_split: dict[str, list[CaseRow]] = {split: [] for split in SPLITS}
    for row in rows:
        by_split.setdefault(assignments[row.case_id], []).append(row)

    query_to_splits: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        query_to_splits[row.query_key].add(assignments[row.case_id])
    leaked = {q: sorted(splits) for q, splits in query_to_splits.items() if len(splits) > 1}

    return {
        "splits": {split: summarize_rows(split_rows) for split, split_rows in by_split.items()},
        "query_group_leakage": {
            "groups": len(leaked),
            "queries": leaked,
        },
    }


def split_assignment_rows(
    rows: Sequence[CaseRow], assignments: Mapping[str, str]
) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        out.append(
            {
                "case_id": row.case_id,
                "split": assignments[row.case_id],
                "dataset_version": row.dataset_version,
                "label": row.label,
                "query_hash": row.query_hash,
                "cell_id": row.cell_id,
                "pattern": row.pattern,
                "domain": row.domain,
                "difficulty": row.difficulty,
            }
        )
    return sorted(out, key=lambda item: item["case_id"])


def blind_label_queue_rows(cases: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in cases:
        rows.append(
            {
                "case_id": case_id(case),
                "task": (
                    "Classify the RAG governance decision from query and retrieved contexts only. "
                    "Return ABSTAIN, DISPUTED, or TRUSTWORTHY with a short rationale."
                ),
                "input": {
                    "query": query(case),
                    "contexts": contexts(case),
                },
            }
        )
    return rows


def blind_label_manifest_rows(
    rows: Sequence[CaseRow], assignments: Mapping[str, str]
) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        out.append(
            {
                "case_id": row.case_id,
                "gold_label": row.label,
                "split": assignments.get(row.case_id),
                "dataset_version": row.dataset_version,
                "query_hash": row.query_hash,
                "cell_id": row.cell_id,
                "pattern": row.pattern,
                "domain": row.domain,
                "difficulty": row.difficulty,
            }
        )
    return sorted(out, key=lambda item: item["case_id"])


def jsonl_text(rows: Iterable[Mapping[str, Any]]) -> str:
    return "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n"


def markdown_report(summary: Mapping[str, Any]) -> str:
    dup = summary["duplicates"]
    split = summary["split_summary"]
    lines = [
        "# V7 QA Audit",
        "",
        f"Vault rows: **{summary['all_rows']['rows']}**",
        f"Cohort rows: **{summary['cohort_rows']['rows']}** (`{summary['cohort']}`)",
        "",
        "## Duplicate And Leakage Risk",
        "",
        "| Check | Groups | Rows |",
        "|---|---:|---:|",
    ]
    for key, label_ in [
        ("duplicate_ids", "Duplicate IDs"),
        ("duplicate_exact_input", "Duplicate exact inputs"),
        ("duplicate_exact_input_with_label", "Duplicate exact inputs + labels"),
        ("duplicate_checker_hash", "Duplicate checker hashes"),
        ("exact_query_duplicates", "Exact query duplicate groups"),
        ("cross_label_query_duplicates", "Cross-label exact query groups"),
    ]:
        row = dup[key]
        lines.append(f"| {label_} | {row['groups']} | {row['rows']} |")

    lines.extend(
        [
            "",
            "## Query-Grouped Split",
            "",
            f"Query group leakage groups: **{split['query_group_leakage']['groups']}**",
            "",
            "| Split | Rows | ABSTAIN | DISPUTED | TRUSTWORTHY |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for split_name in SPLITS:
        split_row = split["splits"][split_name]
        labels = split_row["labels"]
        lines.append(
            "| "
            + f"{split_name} | {split_row['rows']} | "
            + f"{labels.get('ABSTAIN', 0)} | {labels.get('DISPUTED', 0)} | "
            + f"{labels.get('TRUSTWORTHY', 0)} |"
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "- `summary.json`",
            "- `report.md`",
            "- `query_duplicate_groups.jsonl`",
            "- `cross_label_query_groups.jsonl`",
            "- `split_assignments.jsonl`",
            "- `blind_label_queue.jsonl`",
            "- `blind_label_manifest.jsonl`",
        ]
    )
    return "\n".join(lines) + "\n"
