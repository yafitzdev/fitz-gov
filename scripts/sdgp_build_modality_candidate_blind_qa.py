"""Build blind-label QA files from modality candidate case packs.

This is for candidate-only structured/code packs that are stored as direct
SDGP case JSONL files, not generation rows shaped as {"case_id", "case"}.
It can build either a full queue or a deterministic stratified pilot sample.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.qa import (  # noqa: E402
    blind_label_manifest_rows,
    blind_label_queue_rows,
    jsonl_text,
    rows_from_cases,
    summarize_rows,
)


DEFAULT_INPUTS = [
    Path("data/_workspaces/handoff/modality_structured_v1_20260527/cases.jsonl"),
    Path("data/_workspaces/handoff/modality_code_v1_20260527/cases.jsonl"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, action="append", default=None)
    parser.add_argument(
        "--qa-dir",
        type=Path,
        default=Path("data/_workspaces/qa/modality_v1_codex_blind_pilot_20260528"),
    )
    parser.add_argument(
        "--sample-per-modality",
        type=int,
        default=0,
        help="If >0, take a deterministic stratified sample per modality instead of all rows.",
    )
    parser.add_argument(
        "--include-mechanism",
        action="append",
        default=None,
        help="Restrict the queue to this meta.mechanism value. Can be passed multiple times.",
    )
    parser.add_argument("--seed", type=int, default=20260528)
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: row must be a JSON object")
            rows.append(row)
    return rows


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def modality_of(case: Mapping[str, Any]) -> str:
    meta = case.get("meta") if isinstance(case.get("meta"), Mapping) else {}
    return str(meta.get("modality") or "unknown")


def label_of(case: Mapping[str, Any]) -> str:
    gov = case.get("governance") if isinstance(case.get("governance"), Mapping) else {}
    return str(gov.get("classification") or "UNKNOWN").upper()


def pattern_of(case: Mapping[str, Any]) -> str:
    tax = case.get("taxonomy") if isinstance(case.get("taxonomy"), Mapping) else {}
    return str(tax.get("pattern") or "unknown")


def mechanism_of(case: Mapping[str, Any]) -> str:
    meta = case.get("meta") if isinstance(case.get("meta"), Mapping) else {}
    return str(meta.get("mechanism") or meta.get("category") or "unknown")


def stratified_sample(
    cases: list[dict[str, Any]],
    *,
    sample_per_modality: int,
    seed: int,
) -> list[dict[str, Any]]:
    if sample_per_modality <= 0:
        return cases

    rng = random.Random(seed)
    by_modality: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in cases:
        by_modality[modality_of(case)].append(case)

    sampled: list[dict[str, Any]] = []
    for modality, modality_cases in sorted(by_modality.items()):
        by_label: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for case in modality_cases:
            by_label[label_of(case)].append(case)

        labels = sorted(by_label)
        base, remainder = divmod(sample_per_modality, len(labels))
        for label_idx, label in enumerate(labels):
            target = base + (1 if label_idx < remainder else 0)
            label_cases = list(by_label[label])
            rng.shuffle(label_cases)
            by_key: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
            for case in label_cases:
                by_key[(pattern_of(case), mechanism_of(case))].append(case)
            keys = sorted(by_key)
            chosen: list[dict[str, Any]] = []
            while len(chosen) < target and keys:
                next_keys = []
                for key in keys:
                    bucket = by_key[key]
                    if bucket and len(chosen) < target:
                        chosen.append(bucket.pop())
                    if bucket:
                        next_keys.append(key)
                keys = next_keys
            sampled.extend(chosen)

    return sampled


def filter_by_mechanism(
    cases: list[dict[str, Any]],
    include_mechanisms: list[str] | None,
) -> list[dict[str, Any]]:
    if not include_mechanisms:
        return cases
    allowed = set(include_mechanisms)
    return [case for case in cases if mechanism_of(case) in allowed]


def main() -> int:
    args = parse_args()
    inputs = args.input or DEFAULT_INPUTS
    cases: list[dict[str, Any]] = []
    for path in inputs:
        cases.extend(read_jsonl(path))

    filtered = filter_by_mechanism(cases, args.include_mechanism)
    selected = stratified_sample(
        filtered,
        sample_per_modality=args.sample_per_modality,
        seed=args.seed,
    )
    if not selected:
        raise ValueError("No cases selected for blind-label QA.")
    selected.sort(key=lambda case: (modality_of(case), label_of(case), pattern_of(case), case["id"]))

    case_rows = rows_from_cases(selected)
    assignments = {row.case_id: "candidate" for row in case_rows}

    args.qa_dir.mkdir(parents=True, exist_ok=True)
    (args.qa_dir / "blind_label_queue.jsonl").write_text(
        jsonl_text(blind_label_queue_rows(selected)),
        encoding="utf-8",
    )
    (args.qa_dir / "blind_label_manifest.jsonl").write_text(
        jsonl_text(blind_label_manifest_rows(case_rows, assignments)),
        encoding="utf-8",
    )
    write_json(
        args.qa_dir / "candidate_summary.json",
        {
            "source_files": [str(path) for path in inputs],
            "source_rows": len(cases),
            "filtered_rows": len(filtered),
            "include_mechanism": args.include_mechanism or [],
            "sample_per_modality": args.sample_per_modality,
            "seed": args.seed,
            "summary": summarize_rows(case_rows),
            "modality_counts": dict(sorted(Counter(modality_of(case) for case in selected).items())),
            "label_counts": dict(sorted(Counter(label_of(case) for case in selected).items())),
            "pattern_counts": dict(sorted(Counter(pattern_of(case) for case in selected).items())),
            "mechanism_counts": dict(sorted(Counter(mechanism_of(case) for case in selected).items())),
        },
    )

    print("=== Build modality candidate blind-label QA ===")
    print(f"Source files : {len(inputs)}")
    print(f"Rows         : {len(selected)}")
    print(f"QA dir       : {args.qa_dir}")
    print(f"Queue        : {args.qa_dir / 'blind_label_queue.jsonl'}")
    print(f"Manifest     : {args.qa_dir / 'blind_label_manifest.jsonl'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
