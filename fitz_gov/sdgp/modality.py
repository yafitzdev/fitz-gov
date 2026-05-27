"""Evidence-modality helpers for SDGP rows."""

from __future__ import annotations

from typing import Any


MODALITIES: tuple[str, ...] = ("unstructured", "structured", "code")
MODALITY_SET: set[str] = set(MODALITIES)
DEFAULT_MODALITY = "unstructured"


def validate_modality(value: Any) -> str:
    """Return a validated modality string."""
    if value not in MODALITY_SET:
        raise ValueError(f"modality must be one of {sorted(MODALITY_SET)}, got {value!r}")
    return str(value)


def set_modality(
    case: dict[str, Any],
    modality: str = DEFAULT_MODALITY,
    *,
    overwrite: bool = False,
) -> bool:
    """Ensure ``case['meta']['modality']`` is set.

    Returns True when the row was changed.
    """
    modality = validate_modality(modality)
    meta = case.get("meta")
    if not isinstance(meta, dict):
        meta = {}
        case["meta"] = meta

    current = meta.get("modality")
    if current is None:
        meta["modality"] = modality
        return True
    validate_modality(current)
    if current != modality and overwrite:
        meta["modality"] = modality
        return True
    if current != modality:
        raise ValueError(f"row has modality {current!r}, expected {modality!r}")
    return False
