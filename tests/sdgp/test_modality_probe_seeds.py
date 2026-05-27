from __future__ import annotations

import json
from pathlib import Path

from fitz_gov.sdgp.checker import Checker
from fitz_gov.sdgp.completeness import audit_case_completeness

ROOT = Path(__file__).resolve().parents[2]
PROBE_ROOT = ROOT / "data" / "modality_probes"


def _load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def test_structured_and_code_probe_datasets_have_10_rows_each() -> None:
    for modality in ("structured", "code"):
        rows = _load_jsonl(PROBE_ROOT / modality / "cases.jsonl")
        assert len(rows) == 10
        assert len({row["id"] for row in rows}) == len(rows)


def test_modality_probe_rows_pass_sdgp_checker_and_training_schema() -> None:
    checker = Checker(require_training_schema=True)
    for modality in ("structured", "code"):
        rows = _load_jsonl(PROBE_ROOT / modality / "cases.jsonl")
        for row in rows:
            result = checker.check(row)
            assert result.errors == []
            assert audit_case_completeness(row) == []
            assert row["meta"]["modality"] == modality
            assert "source_type" not in row
            assert "domain" not in row.get("meta", {})


def test_unstructured_probe_manifest_points_to_canonical_v8() -> None:
    manifest = json.loads((PROBE_ROOT / "unstructured" / "manifest.json").read_text())

    assert manifest["modality"] == "unstructured"
    assert manifest["huggingface"]["repo_id"] == "yafitzdev/fitz-gov"
    assert manifest["huggingface"]["config"] == "v8"
    assert manifest["huggingface"]["revision"] == "v8.0.0"
