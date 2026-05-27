# Modality Probe Seed Datasets

Tiny local seed datasets for comparing governance behavior across fitz-sage
retrieval modalities without changing the published V8 contract.

The hierarchy is:

| Modality | Path | Status |
|---|---|---|
| Unstructured text | `data/modality_probes/unstructured/manifest.json` | Pointer to the canonical Hugging Face `yafitzdev/fitz-gov` V8 dataset |
| Structured data | `data/modality_probes/structured/cases.jsonl` | 10 SDGP-shaped seed rows |
| Code | `data/modality_probes/code/cases.jsonl` | 10 SDGP-shaped seed rows |

The structured and code files keep the current SDGP V8 row shape:
`id`, `version`, `input`, `governance`, `taxonomy`, `routing`, `meta`,
`evaluation`, plus local `_vault` provenance. They are not merged into
`data/sdgp_vault_v51_enriched/cases.jsonl` and are not part of the public
Hugging Face export.

Regenerate them with:

```powershell
python scripts/sdgp_generate_modality_probe_seeds.py
```
