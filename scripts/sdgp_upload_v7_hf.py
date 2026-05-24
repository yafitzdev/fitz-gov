"""Upload the schema-clean SDGP V7 vault to Hugging Face.

V7 publishes the full 10,500-row local vault as Parquet with query-grouped
splits from `data/sdgp_v7_qa/split_assignments.jsonl`. The default HF config
is `v7`.
V7.0.1 is a schema-clean republish of the same rows/splits/labels as V7.0.0:
pre-SDGP report axes are stripped from public rows before upload.

Run from the fitz-gov project root:
    python scripts/sdgp_upload_v7_hf.py --dry-run --staging-dir data/hf_v7_staging
    python scripts/sdgp_upload_v7_hf.py
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.public_schema import (
    find_legacy_public_fields,
    strip_legacy_public_fields,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repo-id", type=str, default="yafitzdev/fitz-gov")
    p.add_argument("--vault", type=Path, default=Path("data/sdgp_vault_v51_enriched"))
    p.add_argument("--qa-dir", type=Path, default=Path("data/sdgp_v7_qa"))
    p.add_argument("--version", type=str, default="7.0.1")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--staging-dir", type=Path, default=None)
    p.add_argument("--commit-message", type=str, default=None)
    p.add_argument(
        "--no-tag",
        action="store_true",
        help="Upload without creating/updating the vX.Y.Z dataset tag.",
    )
    return p.parse_args()


def _label(case: dict[str, Any]) -> str:
    cls = case.get("governance", {}).get("classification", "")
    return str(cls).lower().replace("_hedged", "").replace("_direct", "")


def _dataset_version(case: dict[str, Any]) -> str:
    meta = case.get("meta") if isinstance(case.get("meta"), dict) else {}
    return str(meta.get("dataset_version") or "unknown")


def _with_convenience_fields(case: dict[str, Any]) -> dict[str, Any]:
    tier = 0 if str(case.get("id", "")).startswith("t0_") else 1
    public_row = {**case, "label": _label(case), "tier": tier}
    # Internal vault provenance contains sparse repair metadata and ISO
    # timestamps that make HF JSON feature inference brittle. The source repo
    # remains the provenance record; the published dataset is the case contract.
    public_row.pop("_vault", None)
    return strip_legacy_public_fields(public_row)


def load_cases(vault_jsonl: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with vault_jsonl.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(_with_convenience_fields(json.loads(line)))
    return rows


def _child_path(path: str, key: str) -> str:
    return f"{path}.{key}" if path else key


def _list_item_path(path: str) -> str:
    return f"{path}[]"


def _collect_schema(
    value: Any,
    path: str,
    dict_keys: dict[str, set[str]],
    list_paths: set[str],
) -> None:
    if isinstance(value, dict):
        dict_keys[path].update(str(key) for key in value)
        for key, child in value.items():
            _collect_schema(child, _child_path(path, str(key)), dict_keys, list_paths)
    elif isinstance(value, list):
        list_paths.add(path)
        item_path = _list_item_path(path)
        for item in value:
            _collect_schema(item, item_path, dict_keys, list_paths)


def _empty_for_path(path: str, dict_keys: dict[str, set[str]], list_paths: set[str]) -> Any:
    if path in list_paths:
        return []
    if path in dict_keys:
        return {
            key: _empty_for_path(_child_path(path, key), dict_keys, list_paths)
            for key in sorted(dict_keys[path])
        }
    return None


def _normalize_value(
    value: Any,
    path: str,
    dict_keys: dict[str, set[str]],
    list_paths: set[str],
) -> Any:
    if path in list_paths:
        if not isinstance(value, list):
            return []
        item_path = _list_item_path(path)
        return [
            _normalize_value(item, item_path, dict_keys, list_paths)
            if isinstance(item, dict)
            else item
            for item in value
        ]

    if path in dict_keys:
        source = value if isinstance(value, dict) else {}
        out: dict[str, Any] = {}
        for key in sorted(dict_keys[path]):
            child_path = _child_path(path, key)
            if key in source:
                out[key] = _normalize_value(source[key], child_path, dict_keys, list_paths)
            else:
                out[key] = _empty_for_path(child_path, dict_keys, list_paths)
        return out

    return value


def normalize_cases_for_json_loader(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Make nested JSONL rows schema-stable for Hugging Face's JSON loader.

    `datasets` infers features in chunks. If a later row adds a nested struct
    key that did not appear in the first chunk, generation fails. The vault is
    still the source of truth; this only makes optional nested fields explicit
    as null/empty values in the upload artifacts.
    """
    dict_keys: dict[str, set[str]] = defaultdict(set)
    list_paths: set[str] = set()
    for case in cases:
        _collect_schema(case, "", dict_keys, list_paths)
    return [_normalize_value(case, "", dict_keys, list_paths) for case in cases]


def load_split_assignments(path: Path) -> dict[str, str]:
    assignments: dict[str, str] = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            case_id = str(row.get("case_id") or "")
            split = str(row.get("split") or "")
            if case_id and split:
                assignments[case_id] = split
    return assignments


def write_parquet(cases: Iterable[dict[str, Any]], path: Path) -> int:
    from datasets import Dataset

    rows = list(cases)
    path.parent.mkdir(parents=True, exist_ok=True)
    Dataset.from_list(rows).to_parquet(str(path))
    return len(rows)


def _class_counts(cases: Iterable[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(_label(case) for case in cases).items()))


def _version_counts(cases: Iterable[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(_dataset_version(case) for case in cases).items()))


def write_dataset_card(
    staging: Path,
    *,
    version: str,
    split_counts: dict[str, int],
    split_class_counts: dict[str, dict[str, int]],
    n_all: int,
    version_counts: dict[str, int],
) -> None:
    def class_row(split: str) -> str:
        counts = split_class_counts[split]
        return (
            f"| `{split}` | {split_counts[split]:,} | "
            f"{counts.get('abstain', 0):,} | {counts.get('disputed', 0):,} | "
            f"{counts.get('trustworthy', 0):,} |"
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
  - config_name: v7
    default: true
    data_files:
      - split: train
        path: "v7/train.parquet"
      - split: validation
        path: "v7/validation.parquet"
      - split: test
        path: "v7/test.parquet"
---

# fitz-gov

> A benchmark for measuring whether RAG systems know when to answer, when to push back, and when to abstain.

fitz-gov is a {n_all:,}-case benchmark for epistemic honesty in retrieval-augmented generation. Each row is a `(query, retrieved contexts)` pair labeled with one governance mode:

| Mode | Meaning |
|---|---|
| `ABSTAIN` | The retrieved contexts do not contain enough information to answer. |
| `DISPUTED` | Retrieved contexts disagree, and the disagreement is material. |
| `TRUSTWORTHY` | The contexts support an answer. |

Top-level `label` is the 3-class convenience label: `abstain / disputed / trustworthy`.

Version: **{version}**. License: **CC BY-NC 4.0**. See the [source changelog](https://github.com/yafitzdev/fitz-gov/blob/main/CHANGELOG.md) for full history.

---

## What's new in V7.0.1

V7.0.1 is a schema-clean republish of V7.0.0: same **{n_all:,} rows**, same query-grouped splits, same labels, with the public contract reduced to the SDGP schema. Pre-SDGP diagnostic axes (`meta.domain`, `meta.subcategory`, `meta.reasoning_type`, `meta.query_type`, `meta.evidence_pattern`) are not present in public rows.

V7 contains **{version_counts.get('v6', 0):,} V6** rows plus **{version_counts.get('v7', 0):,} V7** rows.

Release-gate status:

- Target 25/cell is complete across all 378 primary taxonomy cells.
- The full rich V6/MoE training schema is complete for V6 and V7.
- Every row has canonical `evaluation` fields.
- Full independent blind-label coverage is clean: 7,520 / 7,520 V7 rows validated, 0 triage.
- Query-grouped splits have 0 query-group leakage.
- Exact dedup is clean: 0 duplicate IDs, 0 duplicate exact inputs, 0 duplicate checker hashes.
- Cross-label exact-query semantic review passed: 0 same-context-set cross-label pairs, 1 shared-context pair adjudicated valid, 0 unresolved.

---

## Default config: `v7`

The default `v7` config exposes query-grouped splits across the full 10,500-row vault.

| Split | Rows | ABSTAIN | DISPUTED | TRUSTWORTHY |
|---|---:|---:|---:|---:|
{class_row('train')}
{class_row('validation')}
{class_row('test')}

```python
from datasets import load_dataset

ds = load_dataset("yafitzdev/fitz-gov")
print(ds)
print(ds["train"][0]["label"])
```

---

## Schema

Rows are full SDGP vault records with these top-level blocks:

| Field | Description |
|---|---|
| `id` | Stable case ID. |
| `label` | Convenience 3-class label: `abstain`, `disputed`, or `trustworthy`. |
| `tier` | `0` for tier0 sanity, `1` for core rows. |
| `input` | Query, rewritten query, retrieved contexts, and evidence chain when applicable. |
| `governance` | Gold class, confidence/scores, hallucination/retrieval/evidence signals. |
| `evaluation` | Canonical evaluator constraints and config. |
| `routing` | Expert routing metadata. |
| `taxonomy` | Governance class, SDGP pattern, and taxonomy cell. |
| `meta` | Dataset version, difficulty, confidence level, near-miss reason, and grounding targets for TRUSTWORTHY rows. |

For a CPU-friendly governance classifier trained against fitz-gov, see [pyrrho-nano-g2](https://huggingface.co/yafitzdev/pyrrho-nano-g2).

---

## Citation

```bibtex
@misc{{fitz_gov_v7_2026,
  title  = {{ fitz-gov V7: A benchmark for RAG governance }},
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
    assignments_path = (args.qa_dir / "split_assignments.jsonl").resolve()
    if not vault_jsonl.exists():
        print(f"ERROR: vault not found: {vault_jsonl}", file=sys.stderr)
        return 1
    if not assignments_path.exists():
        print(f"ERROR: split assignments not found: {assignments_path}", file=sys.stderr)
        return 1

    if args.staging_dir is None:
        staging = Path(tempfile.mkdtemp(prefix="fitz_gov_v7_hf_"))
    else:
        staging = args.staging_dir.resolve()
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True)

    print(f"Vault       : {vault_jsonl}")
    print(f"QA dir      : {args.qa_dir.resolve()}")
    print(f"Staging dir : {staging}")
    print(f"Repo id     : {args.repo_id}")
    print(f"Version     : {args.version}\n")

    print("[1/4] Loading vault and split assignments ...")
    cases = load_cases(vault_jsonl)
    assignments = load_split_assignments(assignments_path)
    case_ids = {case["id"] for case in cases}
    missing = sorted(case_ids - set(assignments))
    extra = sorted(set(assignments) - case_ids)
    if missing or extra:
        print(
            f"ERROR: split assignment mismatch: missing={len(missing)} extra={len(extra)}",
            file=sys.stderr,
        )
        if missing[:5]:
            print(f"  missing examples: {missing[:5]}", file=sys.stderr)
        if extra[:5]:
            print(f"  extra examples: {extra[:5]}", file=sys.stderr)
        return 1
    legacy_hits = [
        (case.get("id", "<no id>"), paths)
        for case in cases
        if (paths := find_legacy_public_fields(case))
    ]
    if legacy_hits:
        print(
            f"ERROR: public schema still contains legacy fields in {len(legacy_hits)} rows",
            file=sys.stderr,
        )
        for case_id, paths in legacy_hits[:10]:
            print(f"  {case_id}: {paths}", file=sys.stderr)
        return 1

    cases = normalize_cases_for_json_loader(cases)
    print(f"      cases: {len(cases):,}")

    print("\n[2/4] Writing V7 query-grouped splits ...")
    by_split = {"train": [], "validation": [], "test": []}
    for case in cases:
        split = assignments[case["id"]]
        if split not in by_split:
            print(f"ERROR: unknown split {split!r} for {case['id']}", file=sys.stderr)
            return 1
        by_split[split].append(case)
    split_counts = {
        split: write_parquet(rows, staging / "v7" / f"{split}.parquet")
        for split, rows in by_split.items()
    }
    split_class_counts = {split: _class_counts(rows) for split, rows in by_split.items()}
    for split in ("train", "validation", "test"):
        print(f"      {split:10s}: {split_counts[split]:,} rows {split_class_counts[split]}")

    print("\n[3/4] Writing dataset card ...")
    write_dataset_card(
        staging,
        version=args.version,
        split_counts=split_counts,
        split_class_counts=split_class_counts,
        n_all=len(cases),
        version_counts=_version_counts(cases),
    )

    files = sorted(f for f in staging.rglob("*") if f.is_file())
    total_mb = sum(f.stat().st_size for f in files) / 1e6
    print(f"\n[4/4] Staging ({total_mb:.2f} MB total):")
    for f in files:
        print(f"      {f.stat().st_size / 1e6:>7.2f} MB  {f.relative_to(staging)}")

    if args.dry_run:
        print(f"\n--dry-run: not uploading. Staging dir: {staging}")
        return 0

    print("\nImporting huggingface_hub ...")
    from huggingface_hub import HfApi, create_repo

    create_repo(repo_id=args.repo_id, repo_type="dataset", exist_ok=True)
    commit_msg = args.commit_message or f"fitz-gov v{args.version}: publish schema-clean V7 SDGP vault"
    print(f"Uploading with commit: {commit_msg!r}")
    api = HfApi()
    commit = api.upload_folder(
        folder_path=str(staging),
        repo_id=args.repo_id,
        repo_type="dataset",
        commit_message=commit_msg,
        delete_patterns=["*.jsonl", "*.parquet", "v7/*.jsonl", "v7/*.parquet", "README.md"],
    )
    print(f"Commit: {commit.oid}")

    if not args.no_tag:
        tag = f"v{args.version}"
        print(f"Creating/updating tag: {tag}")
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
