"""upload_to_hf.py — Publish fitz-gov to HuggingFace as a Dataset.

Converts the JSON tier files into JSONL, generates a dataset card,
and uploads to `yafitzdev/fitz-gov` (or whatever --repo-id is passed).

Three configs published:
  - tier1_core   (default, 2,920 cases)  → split: train
  - tier0_sanity (60 cases)              → split: test
  - validation   (human-validated subset)→ split: test

The corpus and query mappings are NOT uploaded in this pass — they can
ship as a v2 of the dataset later if there's demand.

Run from fitz-gov project root:
    python scripts/upload_to_hf.py --dry-run
    python scripts/upload_to_hf.py
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repo-id", type=str, default="yafitzdev/fitz-gov")
    p.add_argument("--data-dir", type=Path, default=Path("data"))
    p.add_argument("--version", type=str, default="5.1.0")
    p.add_argument("--dry-run", action="store_true", help="Build the staging dir but skip the actual HF upload")
    p.add_argument(
        "--staging-dir",
        type=Path,
        default=None,
        help="Where to assemble the upload tree (default: a tempdir; pass a fixed path to inspect afterwards)",
    )
    return p.parse_args()


def load_tier_to_jsonl(tier_dir: Path, out_path: Path) -> dict[str, int]:
    """Combine all category JSONs in a tier into a single JSONL. Returns per-category counts."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    counts: Counter = Counter()
    with out_path.open("w", encoding="utf-8") as out:
        for category_file in sorted(tier_dir.glob("*.json")):
            with category_file.open("r", encoding="utf-8") as f:
                payload = json.load(f)
            for case in payload.get("cases", []):
                out.write(json.dumps(case, ensure_ascii=False) + "\n")
                counts[case.get("category", category_file.stem)] += 1
    return dict(counts)


def load_validation_to_jsonl(val_file: Path, out_path: Path) -> int:
    """Convert the validation JSON (slightly different shape — top-level 'samples') to JSONL."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with val_file.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    samples = payload.get("samples") or payload.get("cases") or []
    with out_path.open("w", encoding="utf-8") as out:
        for s in samples:
            out.write(json.dumps(s, ensure_ascii=False) + "\n")
    return len(samples)


def write_dataset_card(staging: Path, version: str, t1_counts: dict, t0_counts: dict, n_val: int) -> Path:
    """Write README.md with the YAML frontmatter that HF Datasets needs."""
    card = f"""---
license: cc-by-nc-4.0
task_categories:
  - text-classification
language:
  - en
size_categories:
  - 1K<n<10K
tags:
  - rag
  - governance
  - hallucination-detection
  - epistemic-honesty
  - abstention
  - benchmark
configs:
  - config_name: tier1_core
    default: true
    data_files:
      - split: train
        path: "tier1_core.jsonl"
  - config_name: tier0_sanity
    data_files:
      - split: test
        path: "tier0_sanity.jsonl"
  - config_name: validation
    data_files:
      - split: test
        path: "validation.jsonl"
---

# fitz-gov

> A benchmark for measuring whether RAG systems know when to **answer**, when to **push back**, and when to **shut up**.

fitz-gov is a {sum(t1_counts.values()) + sum(t0_counts.values()):,}-case benchmark for **epistemic honesty in retrieval-augmented generation**. Each case is a `(query, retrieved contexts)` pair labeled with the *governance mode* a well-calibrated RAG system should adopt:

| Mode | Meaning |
|---|---|
| `ABSTAIN` | The retrieved contexts do not contain enough information to answer. |
| `DISPUTED` | Retrieved contexts disagree, and the disagreement is material. |
| `TRUSTWORTHY_HEDGED` | The contexts support an answer that requires explicit qualification (limitations, scope, uncertainty). |
| `TRUSTWORTHY_DIRECT` | The contexts support a confident direct answer. |

For 3-class evaluation, `TRUSTWORTHY_HEDGED` and `TRUSTWORTHY_DIRECT` collapse into a single `TRUSTWORTHY` class to remain directly comparable to typical 3-mode RAG governance benchmarks.

The benchmark is **purpose-built to stress-test governance**, not retrieval quality. 62.7% of `tier1_core` cases are marked hard difficulty: subtle conflicts, decoy data, temporal mismatch, methodological disagreement, causal-without-evidence, missing data, and more. Hand-curated subcategories (113+) make per-failure-mode analysis tractable.

Version: **{version}**. See [CHANGELOG.md](https://github.com/yafitzdev/fitz-gov/blob/main/CHANGELOG.md) on the source repo for history.

---

## Configs and splits

| Config | Split | Cases | Purpose |
|---|---|---|---|
| `tier1_core` (default) | `train` | **{sum(t1_counts.values()):,}** | Main benchmark. Stratified by category, difficulty, and domain. Typical eval protocol is 5-fold CV or an 80/20 stratified holdout. |
| `tier0_sanity` | `test` | {sum(t0_counts.values())} | Easier diagnostic set. Use for sanity checks; not statistically meaningful as a release gate (N=60 with some label noise). |
| `validation` | `test` | {n_val} | Stratified human-validation holdout. Reserved for inter-annotator-agreement work. |

Category distribution (`tier1_core` config):

| Category | Cases |
|---|---|
| `abstention` | {t1_counts.get('abstention', 0)} |
| `dispute` | {t1_counts.get('dispute', 0)} |
| `trustworthy_hedged` | {t1_counts.get('trustworthy_hedged', 0)} |
| `trustworthy_direct` | {t1_counts.get('trustworthy_direct', 0)} |

---

## Quickstart

```python
from datasets import load_dataset

# Main benchmark (default config, full 2,920 tier1_core cases)
ds = load_dataset("yafitzdev/fitz-gov", split="train")
print(ds[0])
# {{'id': 't1_abstain_hard_001', 'query': '...', 'contexts': [...], 'expected_mode': 'abstain', ...}}

# Sanity check set
sanity = load_dataset("yafitzdev/fitz-gov", "tier0_sanity", split="test")

# Human-validation subset
val = load_dataset("yafitzdev/fitz-gov", "validation", split="test")
```

For an example 3-class fine-tune that uses this dataset, see [**pyrrho**](https://huggingface.co/yafitzdev/pyrrho-nano-g1) — a CPU-friendly ModernBERT-base governance classifier with **86.13 ± 0.86%** accuracy on the tier1 eval hold-out (vs 78.7% for the sklearn baseline).

---

## Case schema

Each case carries the following fields (some are category-specific):

| Field | Type | Description |
|---|---|---|
| `id` | string | Stable case identifier (`t{{tier}}_{{category}}_{{difficulty}}_{{nnn}}`). |
| `query` | string | The user question routed into the RAG pipeline. |
| `contexts` | list[string] | Retrieved document chunks the model has access to. |
| `expected_mode` | string | Gold governance label: `abstain` / `disputed` / `trustworthy`. |
| `category` | string | One of: `abstention`, `dispute`, `trustworthy_hedged`, `trustworthy_direct`. |
| `subcategory` | string | Finer-grained failure pattern (113+ values; e.g. `wrong_entity`, `numerical_conflict`, `causal_uncertainty`). |
| `difficulty` | string | `easy`, `medium`, or `hard`. |
| `domain` | string | Topic domain (17 values; e.g. `technology`, `medicine`, `finance`). |
| `query_type` | string | Surface form of the query (`what`, `how`, `why`, `is`, ...). |
| `source_type` | string | `single` or `multi` source. |
| `context_count` | int | Number of contexts retrieved. |
| `reasoning_type` | string | `factual` / `causal` / `temporal` / `comparative` / `evaluative` / `procedural`. |
| `evidence_pattern` | string | `direct` / `partial` / `conflicting` / `absent` / `indirect` / `mixed`. |
| `rationale` | string | Hand-written justification for the gold label. |
| `evaluation_config` | object | Per-case overrides for the upstream `fitz-gov` library evaluator. |
| `metadata` | object | Auxiliary tracking fields (provenance, version history). |
| `original_id` | string | Pre-relabeling ID if the case was migrated from an earlier version. |
| `original_subcategory` | string | Pre-relabeling subcategory. |
| `description` | string | Optional human-readable summary. |

`TRUSTWORTHY_*` cases additionally typically carry `required_elements` (substring/string-match list a good answer must include) and `forbidden_claims` (assertions a good answer must *not* make).

---

## Background and motivation

Most RAG benchmarks measure retrieval quality (did we get the right document?) or answer correctness (is the generated text right?). They under-measure the *third* axis: did the system know when **not** to answer? RAG failures in production are dominated by confident hallucination on cases where the retrieved evidence is insufficient or contradictory — exactly the cases fitz-gov is built to surface.

The benchmark is used by [pyrrho](https://huggingface.co/yafitzdev/pyrrho-nano-g1) (CPU-friendly fine-tuned governance classifiers) and [fitz-sage](https://github.com/yafitzdev/fitz-sage) (a production RAG library that runs governance inline at inference time). All three projects are public.

---

## License

CC BY-NC 4.0 — see [LICENSE](https://github.com/yafitzdev/fitz-gov/blob/main/LICENSE). Free for research, evaluation, and personal use; commercial use of the benchmark or derivatives requires a separate license.

## Citation

```bibtex
@misc{{fitz_gov_v5_2026,
  title  = {{ fitz-gov: A benchmark for RAG governance }},
  author = {{ Yan Fitzner }},
  year   = {{ 2026 }},
  url    = {{ https://huggingface.co/datasets/yafitzdev/fitz-gov }},
}}
```

## Related projects

- [**pyrrho**](https://huggingface.co/yafitzdev/pyrrho-nano-g1) — fine-tuned classifiers trained against this benchmark.
- [**fitz-sage**](https://github.com/yafitzdev/fitz-sage) — production RAG library that uses pyrrho models for governance.
- [Source repository](https://github.com/yafitzdev/fitz-gov) with full schema docs and generation tooling.
"""
    readme_path = staging / "README.md"
    readme_path.write_text(card, encoding="utf-8")
    return readme_path


def main() -> int:
    args = parse_args()
    data_dir = args.data_dir.resolve()
    if not data_dir.exists():
        print(f"ERROR: data dir not found: {data_dir}", file=sys.stderr)
        return 1

    if args.staging_dir is None:
        staging_root = Path(tempfile.mkdtemp(prefix="fitz_gov_hf_"))
    else:
        staging_root = args.staging_dir.resolve()
        if staging_root.exists():
            shutil.rmtree(staging_root)
        staging_root.mkdir(parents=True)

    print(f"Source data : {data_dir}")
    print(f"Staging dir : {staging_root}")
    print(f"Repo id     : {args.repo_id}")
    print(f"Version     : {args.version}\n")

    print("[1/4] Converting tier1_core/*.json -> tier1_core.jsonl ...")
    t1_counts = load_tier_to_jsonl(data_dir / "tier1_core", staging_root / "tier1_core.jsonl")
    print(f"      {sum(t1_counts.values())} cases ({t1_counts})")

    print("\n[2/4] Converting tier0_sanity/*.json -> tier0_sanity.jsonl ...")
    t0_counts = load_tier_to_jsonl(data_dir / "tier0_sanity", staging_root / "tier0_sanity.jsonl")
    print(f"      {sum(t0_counts.values())} cases ({t0_counts})")

    print("\n[3/4] Converting validation/human_validation_sample.json -> validation.jsonl ...")
    val_file = data_dir / "validation" / "human_validation_sample.json"
    if val_file.exists():
        n_val = load_validation_to_jsonl(val_file, staging_root / "validation.jsonl")
        print(f"      {n_val} cases")
    else:
        print(f"      WARNING: {val_file} not found; skipping validation config")
        n_val = 0

    print("\n[4/4] Writing dataset card ...")
    card_path = write_dataset_card(staging_root, args.version, t1_counts, t0_counts, n_val)
    print(f"      Wrote {card_path}")

    files = sorted(staging_root.rglob("*"))
    files = [f for f in files if f.is_file()]
    total_mb = sum(f.stat().st_size for f in files) / 1e6
    print(f"\nStaging contents ({total_mb:.2f} MB total):")
    for f in files:
        size_mb = f.stat().st_size / 1e6
        rel = f.relative_to(staging_root)
        print(f"  {size_mb:>7.2f} MB  {rel}")

    if args.dry_run:
        print(f"\n--dry-run set, not uploading. Staging dir: {staging_root}")
        return 0

    print("\nImporting huggingface_hub...")
    from huggingface_hub import HfApi, create_repo

    print(f"Creating dataset repo (no-op if exists): {args.repo_id}")
    create_repo(repo_id=args.repo_id, repo_type="dataset", exist_ok=True)

    print("Uploading...")
    api = HfApi()
    api.upload_folder(
        folder_path=str(staging_root),
        repo_id=args.repo_id,
        repo_type="dataset",
        commit_message=f"fitz-gov v{args.version} initial upload",
    )

    print(f"\nDONE. Live at: https://huggingface.co/datasets/{args.repo_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
