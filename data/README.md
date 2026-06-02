# fitz-gov Data Directory

Use `data/fitz-gov/` as the human entry point for the actual dataset.

Most other directories under `data/` are local build artifacts from generating,
repairing, QA-scoring, or publishing SDGP rows. They are intentionally ignored
by git and are not the public dataset contract.

## Actual Data

| Purpose | Path |
|---|---|
| Canonical local access point | `data/fitz-gov/` |
| Active local data | `data/fitz-gov/cases.jsonl` |
| Current training-schema summary | `data/fitz-gov/training_schema_summary.json` |
| Published dataset | Hugging Face `yafitzdev/fitz-gov`, config `v8`, revision `v8.1.0` |

All current rows are unstructured-text governance rows and should carry
`meta.modality: "unstructured"` locally. All current rows also carry
`routing.query_contract` for V8.1 pre-retrieval routing/governance work. Future
structured-data and code rows use the same SDGP hierarchy with
`meta.modality: "structured"` or `meta.modality: "code"` and stay outside the
active vault until structural and blind-label QA pass.

For normal consumers, prefer Hugging Face:

```python
from datasets import load_dataset

ds = load_dataset("yafitzdev/fitz-gov", "v8", revision="v8.1.0")
```

For local generation, QA, or pyrrho prep, start from `data/fitz-gov/cases.jsonl`
and use `data/fitz-gov/manifest.json` for bundle metadata.

## What The Other Directories Are

| Directory pattern | Meaning | Canonical data? |
|---|---|---|
| `data/_workspaces/handoff/` | Candidate generation handoff workspaces: batch specs, subagent outputs, normalized rows, patched rows | No |
| `data/_workspaces/qa/` | Offline blind-label QA workspaces and cohort QA outputs | No |
| `data/_workspaces/hf_staging/` | Hugging Face packaging/export staging dirs | No |
| `data/_workspaces/reports/` | Historical reports | No |
| `data/_workspaces/vault_source/` | Pre-cleanup local vault directory with backups and cost reports | Historical source material |
| `data/_workspaces/legacy/` | Legacy tiers, bootstrap corpus, query maps | Historical |
| `modality_probes` | Tiny local structured/code/code-vs-unstructured comparison seed datasets | Experimental |

## Rule

Do not point model training, fitz-sage integration, or public export code at a
random `sdgp_handoff*` or `sdgp_qa*` directory. Those are intermediate
workspaces. Use `data/fitz-gov/cases.jsonl` as the canonical local row source.
