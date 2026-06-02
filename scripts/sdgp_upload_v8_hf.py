"""Upload the target-50 SDGP V8 vault to Hugging Face.

V8 publishes the full local vault as Parquet with query-grouped splits from
`data/_workspaces/qa/sdgp_v8_qa/split_assignments.jsonl`. The public Hugging
Face dataset has one canonical config: `v8`.

Run from the fitz-gov project root:
    python scripts/sdgp_upload_v8_hf.py --dry-run --staging-dir data/hf_v8_staging
    python scripts/sdgp_upload_v8_hf.py
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.public_schema import find_legacy_public_fields
from sdgp_upload_v7_hf import (
    _class_counts,
    _version_counts,
    load_cases,
    load_split_assignments,
    normalize_cases_for_json_loader,
    write_parquet,
)


FINAL_BLIND_SCORE_DIR = "score_claude_full_repaired87_combined_20260526"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repo-id", type=str, default="yafitzdev/fitz-gov")
    p.add_argument("--vault", type=Path, default=Path("data/fitz-gov"))
    p.add_argument("--qa-dir", type=Path, default=Path("data/_workspaces/qa/sdgp_v8_qa"))
    p.add_argument("--blind-score-dir", type=Path, default=None)
    p.add_argument("--version", type=str, default="8.1.0")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--staging-dir", type=Path, default=None)
    p.add_argument("--commit-message", type=str, default=None)
    p.add_argument(
        "--no-tag",
        action="store_true",
        help="Upload without creating the vX.Y.Z dataset tag.",
    )
    return p.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _nested(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    cur: Any = data
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def require_release_gates(
    *,
    cases: list[dict[str, Any]],
    qa_dir: Path,
    blind_score_dir: Path,
    version_counts: dict[str, int],
) -> dict[str, Any]:
    failures: list[str] = []

    training = load_json(qa_dir / "training_schema_summary.json")
    gap = load_json(qa_dir / "full_dataset_gap_target50_after_merge.json")
    audit = load_json(qa_dir / "summary.json")
    blind = load_json(blind_score_dir / "blind_label_score_summary.json")

    v8_rows = version_counts.get("v8", 0)
    if _nested(training, "totals", "v8") != v8_rows:
        failures.append(
            f"training totals v8={_nested(training, 'totals', 'v8')} but vault has {v8_rows}"
        )
    if _nested(training, "complete", "v8") != v8_rows:
        failures.append(
            f"training complete v8={_nested(training, 'complete', 'v8')} but vault has {v8_rows}"
        )
    if _nested(training, "issue_counts", "v8", "issues") != 0:
        failures.append("training schema still reports V8 issues")

    if gap.get("target") != 50:
        failures.append(f"target gap report is for target={gap.get('target')}, expected 50")
    if gap.get("cells_at_target") != gap.get("cells_considered"):
        failures.append("not every V8 generation cell is at target")
    if gap.get("total_gap_to_fill") != 0:
        failures.append(f"target-50 gap remains: {gap.get('total_gap_to_fill')}")
    if gap.get("total_cases") != len(cases):
        failures.append(f"gap report total_cases={gap.get('total_cases')} but vault has {len(cases)}")

    if _nested(audit, "all_rows", "rows") != len(cases):
        failures.append(f"QA audit rows={_nested(audit, 'all_rows', 'rows')} but vault has {len(cases)}")
    if _nested(audit, "split_summary", "query_group_leakage", "groups") != 0:
        failures.append("query-group leakage is non-zero")
    for key in ("duplicate_ids", "duplicate_exact_input", "duplicate_exact_input_with_label", "duplicate_checker_hash"):
        if _nested(audit, "duplicates", key, "groups") != 0:
            failures.append(f"{key} groups are non-zero")

    if blind.get("total_manifest_rows") != v8_rows:
        failures.append(f"blind manifest rows={blind.get('total_manifest_rows')} but V8 rows={v8_rows}")
    for key in ("missing_rows", "invalid_rows", "error_rows", "disagree_rows", "duplicate_prediction_rows"):
        if blind.get(key) != 0:
            failures.append(f"blind-label {key}={blind.get(key)}")
    if blind.get("agree_rows") != v8_rows:
        failures.append(f"blind-label agree_rows={blind.get('agree_rows')} but V8 rows={v8_rows}")

    if failures:
        print("ERROR: V8 release gates failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        raise SystemExit(1)

    return {
        "training": training,
        "gap": gap,
        "audit": audit,
        "blind": blind,
    }


def write_dataset_card(
    staging: Path,
    *,
    version: str,
    split_counts: dict[str, int],
    split_class_counts: dict[str, dict[str, int]],
    n_all: int,
    version_counts: dict[str, int],
    gates: dict[str, Any],
) -> None:
    def class_row(split: str) -> str:
        counts = split_class_counts[split]
        return (
            f"| `{split}` | {split_counts[split]:,} | "
            f"{counts.get('abstain', 0):,} | {counts.get('disputed', 0):,} | "
            f"{counts.get('trustworthy', 0):,} |"
        )

    v8_rows = version_counts.get("v8", 0)
    v6_rows = version_counts.get("v6", 0)
    v7_rows = version_counts.get("v7", 0)
    cells = gates["gap"]["cells_considered"]
    blind_rows = gates["blind"]["agree_rows"]

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
  - config_name: v8
    default: true
    data_files:
      - split: train
        path: "v8/train.parquet"
      - split: validation
        path: "v8/validation.parquet"
      - split: test
        path: "v8/test.parquet"
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

## What's new in V8.1.0

V8.1.0 keeps the V8.0.1 row set, labels, and query-grouped splits. It adds `routing.query_contract` to every row: a query-text contract annotation for pre-retrieval routing and governance experiments. The current contract labels are `evidence_sufficiency`, `structured_lookup`, `temporal_grounding`, `exhaustive_coverage`, `comparison_coverage`, and `representative_overview`.

## V8.0.1 modality patch

V8.0.1 keeps the V8.0.0 row set, labels, and query-grouped splits. It adds explicit row-level evidence modality metadata: current rows are unstructured-text governance cases via `meta.modality: "unstructured"`. This prepares future structured-data and code slices without mixing them into the current unstructured release.

## V8.0.0 baseline

V8.0.0 more than doubles the benchmark, growing it from 10,500 to **{n_all:,}** examples. It adds **{v8_rows:,}** new query/context cases that stress the decisions production RAG systems get wrong: when evidence is enough to answer, when sources conflict, and when the retrieved text is for the wrong target or missing the final result.

The release also makes the benchmark much denser. Every combination of governance label, evidence pattern, domain, and difficulty now has at least 50 examples, so training and evaluation are less dependent on a few sparse edge cases.

Dataset composition:

| Cohort | Rows |
|---|---:|
| V6 | {v6_rows:,} |
| V7 | {v7_rows:,} |
| V8 | {v8_rows:,} |
| Total | {n_all:,} |

Quality checks:

- The coverage grid is complete across all **{cells:,}** label/pattern/domain/difficulty combinations.
- All **{v8_rows:,}/{v8_rows:,}** new V8 rows include the required training and evaluation fields.
- Independent blind-label QA is clean: **{blind_rows:,}/{v8_rows:,}** V8 rows validated, **0 triage**.
- Query-grouped splits have **0 query-group leakage**.
- Exact dedup is clean: **0 duplicate IDs**, **0 duplicate exact inputs**, **0 duplicate exact inputs with label**, **0 duplicate checker hashes**.
- The public dataset exposes one default config, `v8`, with `train`, `validation`, and `test` splits.
- Current rows are explicit unstructured-text governance rows via `meta.modality: "unstructured"`.
- Public rows do not expose old internal reporting fields: `meta.domain`, `meta.subcategory`, `meta.reasoning_type`, `meta.query_type`, `meta.evidence_pattern`, or `source_type`.

---

## Loading the dataset

The default config exposes query-grouped splits across the full {n_all:,}-row dataset.

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

## Row Format

Rows use a structured governance-evaluation format with these top-level blocks:

| Field | Description |
|---|---|
| `id` | Stable case ID. |
| `label` | Convenience 3-class label: `abstain`, `disputed`, or `trustworthy`. |
| `tier` | `0` for tier0 sanity, `1` for core rows. |
| `input` | Query, rewritten query, retrieved contexts, and evidence chain when applicable. |
| `governance` | Gold class, confidence/scores, hallucination/retrieval/evidence signals. |
| `evaluation` | Evaluator constraints and config. |
| `routing` | Expert routing metadata, including the V8.1 `query_contract` annotation. |
| `taxonomy` | Governance class, evidence pattern, and coverage-grid cell. |
| `meta` | Dataset version, evidence modality, difficulty, confidence level, near-miss reason, and grounding targets for TRUSTWORTHY rows. |

## Citation

```bibtex
@misc{{fitz_gov_v8_2026,
  title  = {{ fitz-gov V8: A dense benchmark for RAG governance }},
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
    blind_score_dir = (args.blind_score_dir or (args.qa_dir / FINAL_BLIND_SCORE_DIR)).resolve()
    if not vault_jsonl.exists():
        print(f"ERROR: vault not found: {vault_jsonl}", file=sys.stderr)
        return 1
    if not assignments_path.exists():
        print(f"ERROR: split assignments not found: {assignments_path}", file=sys.stderr)
        return 1
    if not blind_score_dir.exists():
        print(f"ERROR: blind score dir not found: {blind_score_dir}", file=sys.stderr)
        return 1

    if args.staging_dir is None:
        staging = Path(tempfile.mkdtemp(prefix="fitz_gov_v8_hf_"))
    else:
        staging = args.staging_dir.resolve()
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True)

    print(f"Vault          : {vault_jsonl}")
    print(f"QA dir         : {args.qa_dir.resolve()}")
    print(f"Blind score dir: {blind_score_dir}")
    print(f"Staging dir    : {staging}")
    print(f"Repo id        : {args.repo_id}")
    print(f"Version        : {args.version}\n")

    print("[1/5] Loading vault and split assignments ...")
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

    version_counts = _version_counts(cases)
    print(f"      cases: {len(cases):,}")
    print(f"      cohorts: {version_counts}")

    print("\n[2/5] Checking V8 release gates ...")
    gates = require_release_gates(
        cases=cases,
        qa_dir=args.qa_dir.resolve(),
        blind_score_dir=blind_score_dir,
        version_counts=version_counts,
    )
    print("      release gates: clean")

    cases = normalize_cases_for_json_loader(cases)

    print("\n[3/5] Writing V8 query-grouped splits ...")
    by_split = {"train": [], "validation": [], "test": []}
    for case in cases:
        split = assignments[case["id"]]
        if split not in by_split:
            print(f"ERROR: unknown split {split!r} for {case['id']}", file=sys.stderr)
            return 1
        by_split[split].append(case)
    split_counts = {
        split: write_parquet(rows, staging / "v8" / f"{split}.parquet")
        for split, rows in by_split.items()
    }
    split_class_counts = {split: _class_counts(rows) for split, rows in by_split.items()}
    for split in ("train", "validation", "test"):
        print(f"      {split:10s}: {split_counts[split]:,} rows {split_class_counts[split]}")

    print("\n[4/5] Writing dataset card ...")
    write_dataset_card(
        staging,
        version=args.version,
        split_counts=split_counts,
        split_class_counts=split_class_counts,
        n_all=len(cases),
        version_counts=version_counts,
        gates=gates,
    )

    files = sorted(f for f in staging.rglob("*") if f.is_file())
    total_mb = sum(f.stat().st_size for f in files) / 1e6
    print(f"\n[5/5] Staging ({total_mb:.2f} MB total):")
    for f in files:
        print(f"      {f.stat().st_size / 1e6:>7.2f} MB  {f.relative_to(staging)}")

    if args.dry_run:
        print(f"\n--dry-run: not uploading. Staging dir: {staging}")
        return 0

    print("\nImporting huggingface_hub ...")
    from huggingface_hub import HfApi, create_repo

    create_repo(repo_id=args.repo_id, repo_type="dataset", exist_ok=True)
    commit_msg = args.commit_message or f"fitz-gov v{args.version}: publish query-contract V8 SDGP vault"
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
            "v8/*.jsonl",
            "v8/*.parquet",
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
