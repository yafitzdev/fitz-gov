"""Tests for fitz_gov.sdgp.vault."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fitz_gov.sdgp.taxonomy import Cell, Difficulty, Domain, TaxonomyPattern
from fitz_gov.sdgp.vault import (
    CASES_FILE,
    INDEX_FILE,
    VAULT_KEY,
    DuplicateCaseError,
    Provenance,
    Vault,
    VaultError,
    drop_vault_fields,
    new_batch_id,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def make_case(
    *,
    pattern: TaxonomyPattern = TaxonomyPattern.WRONG_SPECIFICITY,
    domain: Domain = Domain.HISTORY_GEOGRAPHY,
    difficulty: Difficulty = Difficulty.HARD,
    id: str | None = None,
    contexts: list[dict] | None = None,
    extra: dict | None = None,
) -> dict:
    cell = Cell(pattern=pattern, domain=domain, difficulty=difficulty)
    case: dict = {
        "taxonomy": {
            "governance_class": cell.governance_class.value,
            "pattern": pattern.value,
            "cell_id": cell.cell_id,
        },
        "input": {
            "query": "test",
            "contexts": contexts or [{"text": "ctx"}],
        },
    }
    if id is not None:
        case["id"] = id
    if extra:
        case.update(extra)
    return case


# ---------------------------------------------------------------------------
# Open / round-trip
# ---------------------------------------------------------------------------


def test_open_creates_empty_vault(tmp_path: Path) -> None:
    v = Vault.open(tmp_path / "vault")
    assert len(v) == 0
    assert (tmp_path / "vault" / INDEX_FILE).exists()
    # cases.jsonl is created lazily on first add — empty vault has none.


def test_add_one_and_read_back(tmp_path: Path) -> None:
    v = Vault.open(tmp_path / "vault")
    case = make_case()
    was_new = v.add(case, provenance=Provenance(provider="local_llm"))
    assert was_new is True
    assert len(v) == 1

    cases = list(v.iter_cases())
    assert len(cases) == 1
    written = cases[0]
    assert written["id"].startswith(case["taxonomy"]["cell_id"])
    assert VAULT_KEY in written
    assert written[VAULT_KEY]["provider"] == "local_llm"
    assert written[VAULT_KEY]["added_at"]  # set


def test_add_with_explicit_id(tmp_path: Path) -> None:
    v = Vault.open(tmp_path / "vault")
    v.add(make_case(id="my_custom_id"))
    assert "my_custom_id" in v
    assert v.get("my_custom_id") is not None


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------


def test_duplicate_add_is_noop_by_default(tmp_path: Path) -> None:
    v = Vault.open(tmp_path / "vault")
    case = make_case(id="dup_id")
    assert v.add(case) is True
    assert v.add(case) is False  # second add returns False
    assert len(v) == 1


def test_duplicate_add_raises_in_strict_mode(tmp_path: Path) -> None:
    v = Vault.open(tmp_path / "vault")
    v.add(make_case(id="strict_id"))
    with pytest.raises(DuplicateCaseError):
        v.add(make_case(id="strict_id"), strict=True)
    assert len(v) == 1


def test_add_missing_id_and_missing_cell_id_raises(tmp_path: Path) -> None:
    v = Vault.open(tmp_path / "vault")
    case = {"input": {"query": "q", "contexts": []}}
    with pytest.raises(VaultError):
        v.add(case)


# ---------------------------------------------------------------------------
# ID minting
# ---------------------------------------------------------------------------


def test_auto_id_uses_cell_id_and_counter(tmp_path: Path) -> None:
    v = Vault.open(tmp_path / "vault")
    cell = Cell(
        pattern=TaxonomyPattern.NUMERICAL_CONFLICT,
        domain=Domain.SCIENCE_MEDICINE,
        difficulty=Difficulty.MEDIUM,
    )
    for i in range(1, 4):
        v.add(
            make_case(
                pattern=cell.pattern,
                domain=cell.domain,
                difficulty=cell.difficulty,
                contexts=[{"text": "A 1"}, {"text": "B 2"}],
            )
        )
    ids = v.case_ids()
    assert len(ids) == 3
    assert any(i.endswith("_001") for i in ids)
    assert any(i.endswith("_002") for i in ids)
    assert any(i.endswith("_003") for i in ids)
    for i in ids:
        assert i.startswith(cell.cell_id)


# ---------------------------------------------------------------------------
# Cell coverage
# ---------------------------------------------------------------------------


def test_cell_counts_track_adds(tmp_path: Path) -> None:
    v = Vault.open(tmp_path / "vault")
    v.add(make_case(pattern=TaxonomyPattern.WRONG_SPECIFICITY, difficulty=Difficulty.HARD))
    v.add(make_case(pattern=TaxonomyPattern.WRONG_SPECIFICITY, difficulty=Difficulty.HARD))
    v.add(make_case(pattern=TaxonomyPattern.WRONG_SPECIFICITY, difficulty=Difficulty.EASY))

    counts = v.cell_counts()
    assert counts["wrong_specificity__history_geography__hard"] == 2
    assert counts["wrong_specificity__history_geography__easy"] == 1


def test_cell_count_accepts_cell_object_or_string(tmp_path: Path) -> None:
    v = Vault.open(tmp_path / "vault")
    cell = Cell(
        pattern=TaxonomyPattern.WRONG_SPECIFICITY,
        domain=Domain.HISTORY_GEOGRAPHY,
        difficulty=Difficulty.HARD,
    )
    v.add(make_case())
    assert v.cell_count(cell) == 1
    assert v.cell_count(cell.cell_id) == 1


# ---------------------------------------------------------------------------
# Crash recovery — rebuild index from JSONL
# ---------------------------------------------------------------------------


def test_index_rebuilt_after_index_file_deleted(tmp_path: Path) -> None:
    root = tmp_path / "vault"
    v = Vault.open(root)
    v.add(make_case(id="r1"))
    v.add(make_case(id="r2"))
    assert len(v) == 2

    # Delete the index (simulate a crash that left JSONL intact)
    (root / INDEX_FILE).unlink()

    v2 = Vault.open(root)
    assert len(v2) == 2
    assert v2.cell_counts()["wrong_specificity__history_geography__hard"] == 2
    assert (root / INDEX_FILE).exists()  # rebuilt


def test_index_rebuilt_when_stale(tmp_path: Path) -> None:
    """If a writer appended to JSONL without persisting the index, the next
    open() detects the drift via line-count mismatch and rebuilds."""
    root = tmp_path / "vault"
    v = Vault.open(root)
    v.add(make_case(id="s1"))

    # Manually append a row to JSONL without going through Vault.add().
    direct_row = make_case(id="s2_direct")
    with (root / CASES_FILE).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(direct_row) + "\n")

    v2 = Vault.open(root)
    assert len(v2) == 2
    assert "s2_direct" in v2


# ---------------------------------------------------------------------------
# Bulk add
# ---------------------------------------------------------------------------


def test_add_many_writes_all_and_dedupes(tmp_path: Path) -> None:
    v = Vault.open(tmp_path / "vault")
    batch = [
        make_case(id="b1"),
        make_case(id="b2"),
        make_case(id="b1"),  # duplicate within batch
        make_case(id="b3"),
    ]
    res = v.add_many(batch)
    assert res == {"added": 3, "duplicate": 1}
    assert len(v) == 3


def test_add_many_auto_ids_dont_collide_in_batch(tmp_path: Path) -> None:
    v = Vault.open(tmp_path / "vault")
    batch = [make_case() for _ in range(5)]
    res = v.add_many(batch)
    assert res["added"] == 5
    assert len(v) == 5
    assert len(set(v.case_ids())) == 5  # all unique


# ---------------------------------------------------------------------------
# Provenance + drop_vault_fields
# ---------------------------------------------------------------------------


def test_provenance_is_stamped_with_all_fields(tmp_path: Path) -> None:
    v = Vault.open(tmp_path / "vault")
    prov = Provenance(
        provider="claude_code",
        provider_version="claude-sonnet-4-5",
        prompt_version="numerical_conflict_v1",
        batch_id=new_batch_id(),
        run_seed=42,
    )
    v.add(make_case(id="p1"), provenance=prov)

    case = v.get("p1")
    assert case is not None
    vault_meta = case[VAULT_KEY]
    assert vault_meta["provider"] == "claude_code"
    assert vault_meta["provider_version"] == "claude-sonnet-4-5"
    assert vault_meta["prompt_version"] == "numerical_conflict_v1"
    assert vault_meta["batch_id"] == prov.batch_id
    assert vault_meta["run_seed"] == 42
    assert vault_meta["added_at"]


def test_provenance_omits_run_seed_when_none(tmp_path: Path) -> None:
    v = Vault.open(tmp_path / "vault")
    v.add(make_case(id="p2"), provenance=Provenance(provider="local_llm"))
    case = v.get("p2")
    assert case is not None
    assert "run_seed" not in case[VAULT_KEY]


def test_drop_vault_fields_strips_provenance() -> None:
    case = {"id": "x", "_vault": {"provider": "claude_code"}, "input": {}}
    out = drop_vault_fields(case)
    assert "_vault" not in out
    assert out["id"] == "x"
    # original untouched
    assert "_vault" in case


# ---------------------------------------------------------------------------
# Containment + len
# ---------------------------------------------------------------------------


def test_contains_and_len(tmp_path: Path) -> None:
    v = Vault.open(tmp_path / "vault")
    v.add(make_case(id="c1"))
    assert "c1" in v
    assert "not_there" not in v
    assert len(v) == 1


# ---------------------------------------------------------------------------
# Legacy V5.1-shaped rows (no taxonomy) — add with explicit id
# ---------------------------------------------------------------------------


def test_legacy_v51_row_adds_with_explicit_id_but_no_cell_index(tmp_path: Path) -> None:
    v = Vault.open(tmp_path / "vault")
    v51 = {"id": "v51_legacy_1", "category": "abstention", "query": "q", "contexts": ["c"]}
    assert v.add(v51) is True
    assert "v51_legacy_1" in v
    # Not indexed under any cell.
    assert v.cell_counts() == {}
