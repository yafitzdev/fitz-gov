from __future__ import annotations

import pytest

from fitz_gov.sdgp.modality import MODALITIES, set_modality, validate_modality


def test_allowed_modalities_are_explicit() -> None:
    assert MODALITIES == ("unstructured", "structured", "code")


def test_set_modality_backfills_meta() -> None:
    row = {"id": "x"}

    changed = set_modality(row)

    assert changed
    assert row["meta"]["modality"] == "unstructured"


def test_set_modality_rejects_mismatch_without_overwrite() -> None:
    row = {"meta": {"modality": "structured"}}

    with pytest.raises(ValueError):
        set_modality(row, "unstructured")


def test_validate_modality_rejects_unknown_value() -> None:
    with pytest.raises(ValueError):
        validate_modality("spreadsheet")
