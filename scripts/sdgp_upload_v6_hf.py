"""sdgp_upload_v6_hf.py — Upload the SDGP-enriched vault as fitz-gov V6 to HuggingFace.

Reads data/sdgp_vault_v51_enriched/cases.jsonl (2,980 cases), splits by ID prefix
(t0_* → tier0_sanity, t1_* → tier1_core), writes a V6 dataset card, and uploads to
yafitzdev/fitz-gov.

Each output row is the full vault JSON with a top-level `label` convenience field
(lowercase: abstain / disputed / trustworthy) and `tier` (0 or 1).

Run from fitz-gov project root:
    python scripts/sdgp_upload_v6_hf.py --dry-run
    python scripts/sdgp_upload_v6_hf.py
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
    p.add_argument("--vault", type=Path, default=Path("data/sdgp_vault_v51_enriched"))
    p.add_argument("--validation-file", type=Path, default=Path("data/validation/human_validation_sample.json"))
    p.add_argument("--version", type=str, default="6.0.0")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--staging-dir", type=Path, default=None)
    p.add_argument("--commit-message", type=str, default=None)
    return p.parse_args()


def _label(case: dict) -> str:
    cls = case.get("governance", {}).get("classification", "")
    return cls.lower().replace("_hedged", "").replace("_direct", "")


def split_vault(vault_jsonl: Path) -> tuple[list[dict], list[dict]]:
    """Return (t1_cases, t0_cases) in stable order."""
    t0, t1 = [], []
    for line in vault_jsonl.open(encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        case = json.loads(line)
        row = {**case, "label": _label(case), "tier": 0 if case["id"].startswith("t0_") else 1}
        if case["id"].startswith("t0_"):
            t0.append(row)
        else:
            t1.append(row)
    return t1, t0


def write_jsonl(cases: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for case in cases:
            f.write(json.dumps(case, ensure_ascii=False) + "\n")


def load_validation(val_file: Path, staging: Path) -> int:
    if not val_file.exists():
        return 0
    with val_file.open(encoding="utf-8") as f:
        payload = json.load(f)
    samples = payload.get("samples") or payload.get("cases") or []
    out = staging / "validation.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    return len(samples)


def write_dataset_card(staging: Path, version: str, n_t1: int, t1_class: dict, n_t0: int, n_val: int) -> None:
    val_config = ""
    if n_val:
        val_config = """  - config_name: validation
    data_files:
      - split: test
        path: "validation.jsonl"
"""

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
{val_config}---

# fitz-gov

> A benchmark for measuring whether RAG systems know when to **answer**, when to **push back**, and when to **shut up**.

fitz-gov is a {n_t1 + n_t0:,}-case benchmark for **epistemic honesty in retrieval-augmented generation**. Each case is a `(query, retrieved contexts)` pair labeled with the *governance mode* a well-calibrated RAG system should adopt:

| Mode | Meaning |
|---|---|
| `ABSTAIN` | The retrieved contexts do not contain enough information to answer. |
| `DISPUTED` | Retrieved contexts disagree, and the disagreement is material. |
| `TRUSTWORTHY_HEDGED` | The contexts support an answer that requires explicit qualification. |
| `TRUSTWORTHY_DIRECT` | The contexts support a confident direct answer. |

For 3-class evaluation, `TRUSTWORTHY_HEDGED` and `TRUSTWORTHY_DIRECT` collapse into `TRUSTWORTHY` — the top-level `label` field always contains one of `abstain / disputed / trustworthy`.

Version: **{version}**. See [CHANGELOG.md](https://github.com/yafitzdev/fitz-gov/blob/main/CHANGELOG.md) on the source repo for history.

---

## What's new in V6

V6 adds **LLM-enriched signals** to every case. A reasoning-capable model (Sonnet 3.7 / Qwen3-35B) annotated the following fields that were previously stubs or absent:

| New field | Location | Description |
|---|---|---|
| `query_rewritten` | `input` | Semantically equivalent query re-expressed for retrieval clarity |
| `summary` | `input.contexts[]` | One-sentence context summary |
| `relevance_to_query` | `input.contexts[]` | 0–1 float, how directly this chunk addresses the query |
| `anchor_period` | `input.contexts[].temporality` | Detected temporal anchor (e.g. "2023 Q4", "pre-2020") |
| `hallucination_pressure` | `governance` | 0–1: how much this query pattern invites confabulation |
| `retrieval_retry_value` | `governance` | 0–1: how much better retrieval would help |
| `query_evidence_alignment` | `governance` | 0–1: semantic overlap between query and retrieved chunks |
| `answer_coverage` | `governance` | 0–1: fraction of the query answerable from the chunks |
| `distance` | `governance.boundary_proximity` | 0–1 distance from the decision boundary to the nearest other class |
| `near_miss_reason` | `meta` | Plain-English explanation of why this case could fool a model |

These signals enable fine-grained training objectives (e.g. multi-task heads on `hallucination_pressure` and `answer_coverage`) and richer per-case diagnostics.

---

## Configs and splits

| Config | Split | Cases | Purpose |
|---|---|---|---|
| `tier1_core` (default) | `train` | **{n_t1:,}** | Main benchmark. Stratified by category, difficulty, and domain. |
| `tier0_sanity` | `test` | {n_t0} | Easier diagnostic set. Sanity checks only; N=60. |
{f'| `validation` | `test` | {n_val} | Human-validated holdout. |' if n_val else ''}

Class distribution (`tier1_core`):

| Class | Cases |
|---|---|
| `ABSTAIN` | {t1_class.get('abstain', 0)} |
| `DISPUTED` | {t1_class.get('disputed', 0)} |
| `TRUSTWORTHY` | {t1_class.get('trustworthy', 0)} |

---

## Quickstart

```python
from datasets import load_dataset

# 3-class label in top-level `label` field: abstain / disputed / trustworthy
ds = load_dataset("yafitzdev/fitz-gov", split="train")
print(ds[0]["label"])   # "abstain"

# V6 governance signals
row = ds[0]
print(row["input"]["query_rewritten"])
print(row["input"]["contexts"][0]["summary"])
print(row["governance"]["hallucination_pressure"])
print(row["meta"]["near_miss_reason"])
```

For a fine-tuned classifier trained against this benchmark, see [**pyrrho**](https://huggingface.co/yafitzdev/pyrrho-nano-g1) — a CPU-friendly ModernBERT-base governance classifier.

---

## Case schema (V6)

Top-level fields:

| Field | Type | Description |
|---|---|---|
| `id` | string | Stable identifier (`t{{tier}}_{{pattern}}_{{difficulty}}_{{nnn}}`). |
| `label` | string | Convenience label: `abstain` / `disputed` / `trustworthy`. |
| `tier` | int | 0 = tier0_sanity, 1 = tier1_core. |
| `version` | string | Schema version string. |
| `input` | object | Query + retrieved contexts (see below). |
| `governance` | object | Gold-label scores and V6 enrichment signals. |
| `routing` | object | Expert routing decisions. |
| `taxonomy` | object | `governance_class`, `pattern`, `cell_id`. |
| `meta` | object | Difficulty, domain, subcategory, V6 signals, V5.1 legacy fields. |
| `_vault` | object | Provenance: provider, batch, timestamps, revision count. |

`input` object:

| Field | Type | Description |
|---|---|---|
| `query` | string | Original user query. |
| `query_rewritten` | string | **[V6]** LLM-rewritten form of the query. |
| `contexts` | list[object] | Retrieved document chunks. |

`input.contexts[]` object:

| Field | Type | Description |
|---|---|---|
| `id` | string | Chunk identifier. |
| `text` | string | The retrieved chunk text. |
| `authority_score` | float | Heuristic source authority (0–1). |
| `authority_signal` | string | Signal type (e.g. `encyclopedic_general`). |
| `temporality` | object | `is_time_sensitive`, `anchor_period` **[V6]**, `staleness_risk`. |
| `summary` | string | **[V6]** One-sentence LLM summary of the chunk. |
| `relevance_to_query` | float | **[V6]** 0–1 relevance to the query. |

`governance` object (key fields):

| Field | Type | Description |
|---|---|---|
| `classification` | string | Gold label: `ABSTAIN` / `DISPUTED` / `TRUSTWORTHY`. |
| `abstain` / `disputed` / `trustworthy` | float | Per-class probability (sum ≈ 1). |
| `confidence` | float | Model confidence in the gold label. |
| `hallucination_pressure` | float | **[V6]** 0–1: how strongly this query pattern invites confabulation. |
| `retrieval_retry_value` | float | **[V6]** 0–1: expected gain from better retrieval. |
| `query_evidence_alignment` | float | **[V6]** 0–1: semantic overlap between query and contexts. |
| `answer_coverage` | float | **[V6]** 0–1: fraction of query answerable from contexts. |
| `boundary_proximity.distance` | float | **[V6]** Distance from decision boundary to nearest other class. |

---

## Background

Most RAG benchmarks measure retrieval quality or answer correctness. They under-measure the *third* axis: did the system know when **not** to answer? fitz-gov is built specifically to surface that failure mode.

Used by [pyrrho](https://huggingface.co/yafitzdev/pyrrho-nano-g1) (fine-tuned governance classifiers) and [fitz-sage](https://github.com/yafitzdev/fitz-sage) (production RAG library).

---

## License

CC BY-NC 4.0. Free for research, evaluation, and personal use. Commercial use requires a separate license.

## Citation

```bibtex
@misc{{fitz_gov_v6_2026,
  title  = {{ fitz-gov V6: A benchmark for RAG governance with LLM-enriched signals }},
  author = {{ Yan Fitzner }},
  year   = {{ 2026 }},
  url    = {{ https://huggingface.co/datasets/yafitzdev/fitz-gov }},
}}
```

## Related projects

- [**pyrrho**](https://huggingface.co/yafitzdev/pyrrho-nano-g1) — fine-tuned classifiers trained against this benchmark.
- [**fitz-sage**](https://github.com/yafitzdev/fitz-sage) — production RAG library that uses pyrrho models for governance.
"""
    (staging / "README.md").write_text(card, encoding="utf-8")


def main() -> int:
    args = parse_args()
    vault_jsonl = (args.vault / "cases.jsonl").resolve()
    if not vault_jsonl.exists():
        print(f"ERROR: vault not found: {vault_jsonl}", file=sys.stderr)
        return 1

    if args.staging_dir is None:
        staging = Path(tempfile.mkdtemp(prefix="fitz_gov_v6_hf_"))
    else:
        staging = args.staging_dir.resolve()
        if staging.exists():
            shutil.rmtree(staging)
        staging.mkdir(parents=True)

    print(f"Vault       : {vault_jsonl}")
    print(f"Staging dir : {staging}")
    print(f"Repo id     : {args.repo_id}")
    print(f"Version     : {args.version}\n")

    print("[1/4] Splitting vault by tier ...")
    t1_cases, t0_cases = split_vault(vault_jsonl)
    t1_class: Counter = Counter(_label(c) for c in t1_cases)
    print(f"      tier1_core : {len(t1_cases)} cases  {dict(t1_class)}")
    print(f"      tier0_sanity: {len(t0_cases)} cases")

    print("\n[2/4] Writing JSONL files ...")
    write_jsonl(t1_cases, staging / "tier1_core.jsonl")
    write_jsonl(t0_cases, staging / "tier0_sanity.jsonl")
    print(f"      tier1_core.jsonl  ({(staging / 'tier1_core.jsonl').stat().st_size / 1e6:.1f} MB)")
    print(f"      tier0_sanity.jsonl ({(staging / 'tier0_sanity.jsonl').stat().st_size / 1e6:.2f} MB)")

    print("\n[3/4] Loading validation set ...")
    n_val = load_validation(args.validation_file.resolve(), staging)
    if n_val:
        print(f"      {n_val} cases")
    else:
        print("      (not found — skipping validation config)")

    print("\n[4/4] Writing dataset card ...")
    write_dataset_card(staging, args.version, len(t1_cases), dict(t1_class), len(t0_cases), n_val)

    files = sorted(f for f in staging.rglob("*") if f.is_file())
    total_mb = sum(f.stat().st_size for f in files) / 1e6
    print(f"\nStaging ({total_mb:.2f} MB total):")
    for f in files:
        print(f"  {f.stat().st_size / 1e6:>7.2f} MB  {f.name}")

    if args.dry_run:
        print(f"\n--dry-run: not uploading. Staging dir: {staging}")
        return 0

    print("\nImporting huggingface_hub ...")
    from huggingface_hub import HfApi, create_repo

    create_repo(repo_id=args.repo_id, repo_type="dataset", exist_ok=True)
    commit_msg = args.commit_message or f"fitz-gov v{args.version}: LLM-enriched V6 upload (SDGP Phase 0b)"
    print(f"Uploading with commit: {commit_msg!r}")
    api = HfApi()
    api.upload_folder(
        folder_path=str(staging),
        repo_id=args.repo_id,
        repo_type="dataset",
        commit_message=commit_msg,
    )
    print(f"\nDONE. https://huggingface.co/datasets/{args.repo_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
