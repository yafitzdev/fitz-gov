"""Tests for fitz_gov.sdgp.orchestrator."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fitz_gov.sdgp.orchestrator import (
    Orchestrator,
    Outcome,
    _patch_cell_metadata,
    parse_case_json,
)
from fitz_gov.sdgp.providers import (
    BlindLabelPair,
    GenerateRequest,
    StubProvider,
)
from fitz_gov.sdgp.taxonomy import (
    Cell,
    Difficulty,
    Domain,
    TaxonomyPattern,
)
from fitz_gov.sdgp.vault import Vault


# ---------------------------------------------------------------------------
# parse_case_json — robust extraction
# ---------------------------------------------------------------------------


def test_parse_plain_json() -> None:
    out = parse_case_json('{"a": 1}')
    assert out == {"a": 1}


def test_parse_fenced_json() -> None:
    raw = '```json\n{"a": 1}\n```'
    assert parse_case_json(raw) == {"a": 1}


def test_parse_json_with_prose_before_and_after() -> None:
    raw = 'Here is your case:\n{"a": 1, "b": "x"}\nLet me know if you need more.'
    assert parse_case_json(raw) == {"a": 1, "b": "x"}


def test_parse_empty_raises() -> None:
    with pytest.raises(ValueError):
        parse_case_json("")


def test_parse_no_json_raises() -> None:
    with pytest.raises(ValueError):
        parse_case_json("just words no braces here")


# ---------------------------------------------------------------------------
# Fixtures: stub a valid case + vault
# ---------------------------------------------------------------------------


def _good_case(cell: Cell, case_id: str = "gen_001", query: str = "test query") -> dict:
    return {
        "id": case_id,
        "input": {
            "query": query,
            "contexts": [
                {"text": f"context {i} for {case_id}", "authority_score": 0.6}
                for i in range(2)
            ],
        },
        "governance": {"classification": cell.governance_class.value},
        "taxonomy": {
            "governance_class": cell.governance_class.value,
            "pattern": cell.pattern.value,
            "cell_id": cell.cell_id,
        },
        "routing": {"expert_fired": cell.domain.value},
        "meta": {"difficulty": cell.difficulty.value},
    }


def _good_case_response(cell: Cell, case_id: str = "gen_001", query: str = "test query") -> str:
    return json.dumps(_good_case(cell, case_id, query))


@pytest.fixture
def cell() -> Cell:
    return Cell(
        pattern=TaxonomyPattern.WRONG_ENTITY,
        domain=Domain.HISTORY_GEOGRAPHY,
        difficulty=Difficulty.HARD,
    )


@pytest.fixture
def vault(tmp_path: Path) -> Vault:
    return Vault.open(tmp_path / "v")


# ---------------------------------------------------------------------------
# generate_one_cell — happy path
# ---------------------------------------------------------------------------


def test_generate_accepts_and_vaults(vault: Vault, cell: Cell) -> None:
    response = _good_case_response(cell, case_id="happy_001")
    orch = Orchestrator(
        vault=vault,
        provider=StubProvider(response=response, name="stub"),
        max_attempts_per_cell=1,
    )
    r = orch.generate_one_cell(cell)
    assert r.outcome == Outcome.ACCEPTED, r.error or "no error"
    assert r.attempts == 1
    assert len(vault) == 1
    # Stored case has _vault provenance
    stored = vault.get("happy_001")
    assert stored is not None
    assert stored["_vault"]["provider"] == "stub"


def test_generate_accepts_works_without_blind_label(vault: Vault, cell: Cell) -> None:
    orch = Orchestrator(
        vault=vault,
        provider=StubProvider(response=_good_case_response(cell, "no_bl_1")),
        blind_label_pair=None,
        max_attempts_per_cell=1,
    )
    r = orch.generate_one_cell(cell)
    assert r.outcome == Outcome.ACCEPTED
    assert r.validator_label is None


# ---------------------------------------------------------------------------
# Rejection paths
# ---------------------------------------------------------------------------


def test_generate_rejects_on_parse_failure(vault: Vault, cell: Cell) -> None:
    orch = Orchestrator(
        vault=vault,
        provider=StubProvider(response="no JSON here at all"),
        max_attempts_per_cell=2,
    )
    r = orch.generate_one_cell(cell)
    assert r.outcome == Outcome.REJECTED_PARSE
    assert r.attempts == 2  # used up both retries
    assert len(vault) == 0


def test_generate_rejects_on_checker_failure(vault: Vault, cell: Cell) -> None:
    # Build a structurally-wrong case: classification is TRUSTWORTHY but
    # pattern is wrong_entity (ABSTAIN). Checker → class_mismatch_pattern.
    bad = _good_case(cell, "bad_001")
    bad["governance"]["classification"] = "TRUSTWORTHY"
    bad["taxonomy"]["governance_class"] = "TRUSTWORTHY"
    orch = Orchestrator(
        vault=vault,
        provider=StubProvider(response=json.dumps(bad)),
        max_attempts_per_cell=2,
    )
    r = orch.generate_one_cell(cell)
    assert r.outcome == Outcome.REJECTED_CHECKER
    assert r.check_result is not None and not r.check_result.passed


def test_generate_rejects_on_provider_failure(vault: Vault, cell: Cell) -> None:
    from fitz_gov.sdgp.providers import Provider, ProviderError

    class BrokenProvider(Provider):
        name = "broken"
        version = "0"

        def generate(self, req: GenerateRequest) -> str:
            raise ProviderError("unreachable")

    orch = Orchestrator(
        vault=vault, provider=BrokenProvider(), max_attempts_per_cell=3
    )
    r = orch.generate_one_cell(cell)
    assert r.outcome == Outcome.REJECTED_PROVIDER
    assert r.attempts == 1  # doesn't retry on provider failures


# ---------------------------------------------------------------------------
# Retry on parse failure — succeed on second try
# ---------------------------------------------------------------------------


def test_generate_retries_then_succeeds(vault: Vault, cell: Cell) -> None:
    responses = iter(["not JSON", _good_case_response(cell, "retry_ok")])

    def callable_response(req: GenerateRequest) -> str:
        return next(responses)

    orch = Orchestrator(
        vault=vault,
        provider=StubProvider(response=callable_response),
        max_attempts_per_cell=3,
    )
    r = orch.generate_one_cell(cell)
    assert r.outcome == Outcome.ACCEPTED
    assert r.attempts == 2


# ---------------------------------------------------------------------------
# Blind labeling
# ---------------------------------------------------------------------------


def test_blind_label_agreement_accepts(vault: Vault, cell: Cell) -> None:
    gen = StubProvider(response=_good_case_response(cell, "agree_1"), name="gen")
    val = StubProvider(
        response=lambda req: cell.governance_class.value, name="val"
    )
    orch = Orchestrator(
        vault=vault,
        provider=gen,
        blind_label_pair=BlindLabelPair(pool=[gen, val]),
        max_attempts_per_cell=1,
    )
    r = orch.generate_one_cell(cell)
    assert r.outcome == Outcome.ACCEPTED
    assert r.generator_label == cell.governance_class.value
    assert r.validator_label == cell.governance_class.value


def test_blind_label_disagreement_marks_conflict(vault: Vault, cell: Cell) -> None:
    """Generator says ABSTAIN, validator says DISPUTED → conflict file."""
    gen = StubProvider(response=_good_case_response(cell, "conflict_1"), name="gen")
    val = StubProvider(response="DISPUTED", name="val")
    orch = Orchestrator(
        vault=vault,
        provider=gen,
        blind_label_pair=BlindLabelPair(pool=[gen, val]),
        max_attempts_per_cell=1,
    )
    r = orch.generate_one_cell(cell, batch_id="bid_test")
    assert r.outcome == Outcome.CONFLICT
    assert r.generator_label == "ABSTAIN"
    assert r.validator_label == "DISPUTED"
    # Case not vaulted
    assert len(vault) == 0
    # Conflict file written under vault/conflicts/<batch_id>/
    conflict_files = list((vault.root / "conflicts" / "bid_test").iterdir())
    assert len(conflict_files) == 1
    payload = json.loads(conflict_files[0].read_text(encoding="utf-8"))
    assert payload["generator_label"] == "ABSTAIN"
    assert payload["validator_label"] == "DISPUTED"
    assert payload["case"]["id"] == "conflict_1"


def test_blind_label_skipped_if_pair_missing_validator(vault: Vault, cell: Cell) -> None:
    """If the pool has only the generator (edge case), blind labeling is skipped
    silently rather than crashing."""
    gen = StubProvider(response=_good_case_response(cell, "no_val"), name="gen")
    # Construct a pool with two refs to the same provider — validator_for() raises ValueError
    # but the orchestrator catches and returns None.
    pair = BlindLabelPair(pool=[gen, StubProvider(name="other")])
    pair.pool = [gen]  # bypass the validation in __post_init__
    orch = Orchestrator(
        vault=vault,
        provider=gen,
        blind_label_pair=pair,
        max_attempts_per_cell=1,
    )
    r = orch.generate_one_cell(cell)
    assert r.outcome == Outcome.ACCEPTED  # no validator → no disagreement to flag


# ---------------------------------------------------------------------------
# Cell metadata patching
# ---------------------------------------------------------------------------


def test_patch_cell_metadata_fills_missing_fields() -> None:
    cell = Cell(
        pattern=TaxonomyPattern.NUMERICAL_CONFLICT,
        domain=Domain.SCIENCE_MEDICINE,
        difficulty=Difficulty.HARD,
    )
    minimal: dict = {
        "id": "x",
        "input": {"query": "q", "contexts": []},
    }
    patched = _patch_cell_metadata(minimal, cell)
    assert patched["taxonomy"]["pattern"] == "numerical_conflict"
    assert patched["taxonomy"]["cell_id"] == cell.cell_id
    assert patched["routing"]["expert_fired"] == "science_medicine"
    assert patched["meta"]["difficulty"] == "hard"
    assert patched["meta"]["modality"] == "unstructured"
    assert patched["governance"]["classification"] == "DISPUTED"


def test_patch_cell_metadata_does_not_overwrite_existing() -> None:
    cell = Cell(
        pattern=TaxonomyPattern.WRONG_ENTITY,
        domain=Domain.HISTORY_GEOGRAPHY,
        difficulty=Difficulty.HARD,
    )
    case: dict = {
        "id": "y",
        "input": {"query": "q", "contexts": []},
        "taxonomy": {"pattern": "wrong_entity", "cell_id": "custom_cell_id"},
    }
    patched = _patch_cell_metadata(case, cell)
    assert patched["taxonomy"]["cell_id"] == "custom_cell_id"  # not overwritten


# ---------------------------------------------------------------------------
# fill_gaps
# ---------------------------------------------------------------------------


def test_fill_gaps_walks_queue_and_reports(vault: Vault) -> None:
    cell_a = Cell(TaxonomyPattern.WRONG_ENTITY, Domain.HISTORY_GEOGRAPHY, Difficulty.HARD)
    cell_b = Cell(TaxonomyPattern.NUMERICAL_CONFLICT, Domain.SCIENCE_MEDICINE, Difficulty.HARD)

    # Stub returns different responses based on cell hint in metadata
    def respond(req: GenerateRequest) -> str:
        cid = req.metadata.get("cell_id", "")
        if "wrong_entity" in cid:
            return _good_case_response(cell_a, "we_1")
        return _good_case_response(cell_b, "nc_1")

    gen = StubProvider(response=respond, name="gen")
    orch = Orchestrator(vault=vault, provider=gen, max_attempts_per_cell=1)

    # Manually craft two gaps
    from fitz_gov.sdgp.gap_detector import Gap

    gaps = [
        Gap(priority=20.0, cell=cell_a, current=0, target=20),
        Gap(priority=20.0, cell=cell_b, current=0, target=20),
    ]
    report = orch.fill_gaps(gaps, n_per_cell=1)
    assert report.n_total == 2
    assert report.counts.get("accepted") == 2
    assert len(vault) == 2


def test_fill_gaps_aborts_on_provider_failure(vault: Vault) -> None:
    from fitz_gov.sdgp.gap_detector import Gap
    from fitz_gov.sdgp.providers import Provider, ProviderError

    cell_a = Cell(TaxonomyPattern.WRONG_ENTITY, Domain.HISTORY_GEOGRAPHY, Difficulty.HARD)
    cell_b = Cell(TaxonomyPattern.NUMERICAL_CONFLICT, Domain.SCIENCE_MEDICINE, Difficulty.HARD)

    class BrokenProvider(Provider):
        name = "broken"
        version = "0"

        def generate(self, req: GenerateRequest) -> str:
            raise ProviderError("everything is on fire")

    orch = Orchestrator(vault=vault, provider=BrokenProvider(), max_attempts_per_cell=1)
    gaps = [
        Gap(priority=20.0, cell=cell_a, current=0, target=20),
        Gap(priority=20.0, cell=cell_b, current=0, target=20),
    ]
    report = orch.fill_gaps(gaps, n_per_cell=1)
    # Only the first attempt happened — batch aborted after provider failure
    assert report.n_total == 1
    assert report.counts.get("rejected_provider") == 1
