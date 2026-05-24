"""Public V7 schema helpers.

The local vault may carry historical generation/reporting hints, but the
published V7 contract is SDGP-native. These helpers strip pre-SDGP diagnostic
axes before Hugging Face export and provide a fail-fast audit so they cannot
re-enter the public dataset silently.
"""

from __future__ import annotations

import copy
from typing import Any


LEGACY_META_FIELDS: tuple[str, ...] = (
    "domain",
    "subcategory",
    "reasoning_type",
    "query_type",
    "evidence_pattern",
)


def strip_legacy_public_fields(case: dict[str, Any]) -> dict[str, Any]:
    """Return a public-row copy with pre-SDGP metadata removed."""
    row = copy.deepcopy(case)

    meta = row.get("meta")
    if isinstance(meta, dict):
        for key in LEGACY_META_FIELDS:
            meta.pop(key, None)

    for key in LEGACY_META_FIELDS:
        row.pop(key, None)

    return row


def find_legacy_public_fields(case: dict[str, Any]) -> list[str]:
    """Return legacy field paths still present in a would-be public row."""
    found: list[str] = []
    meta = case.get("meta")
    if isinstance(meta, dict):
        found.extend(f"meta.{key}" for key in LEGACY_META_FIELDS if key in meta)
    found.extend(key for key in LEGACY_META_FIELDS if key in case)
    return found
