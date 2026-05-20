"""Tests for fitz_gov.sdgp.near_miss."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fitz_gov.sdgp.near_miss import (
    PATTERN_NEIGHBORS,
    NearMissOrchestrator,
    build_near_miss_prompt,
    neighbors_of,
)
from fitz_gov.sdgp.orchestrator import Orchestrator, Outcome
from fitz_gov.sdgp.providers import GenerateRequest, StubProvider
from fitz_gov.sdgp.taxonomy import (
    Cell,
    Difficulty,
    Domain,
    GovernanceClass,
    TaxonomyPattern,
    governance_class_of,
)
from fitz_gov.sdgp.vault import Vault


# ---------------------------------------------------------------------------
# Neighbours
# ---------------------------------------------------------------------------


def test_pattern_neighbors_only_known_patterns() -> None:
    for a, b in PATTERN_NEIGHBORS:
        assert isinstance(a, TaxonomyPattern)
        assert isinstance(b, TaxonomyPattern)
        assert a != b


def test_neighbors_of_symmetric() -> None:
    for a, b in PATTERN_NEIGHBORS:
        assert b in neighbors_of(a)
        assert a in neighbors_of(b)


def test_neighbors_of_every_pattern_has_at_least_one() -> None:
    """Every pattern should have at least one near-miss buddy — otherwise it
    can't be exercised in boundary generation."""
    missing = [p for p in TaxonomyPattern if not neighbors_of(p)]
    assert not missing, f"patterns without neighbours: {missing}"


def test_cross_class_neighbors_exist() -> None:
    """The most valuable near-misses cross governance class (false-trustworthy
    traps). Make sure at least a few pairs are cross-class."""
    cross = [
        (a, b) for a, b in PATTERN_NEIGHBORS
        if governance_class_of(a) != governance_class_of(b)
    ]
    assert len(cross) >= 3


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------


def test_near_miss_prompt_mentions_both_patterns() -> None:
    cell = Cell(TaxonomyPattern.NUMERICAL_CONFLICT, Domain.SCIENCE_MEDICINE, Difficulty.HARD)
    p = build_near_miss_prompt(cell, TaxonomyPattern.QUANTITATIVE_CONSENSUS)
    assert "numerical_conflict" in p.text
    assert "quantitative_consensus" in p.text
    assert "Near-miss directive" in p.text
    assert "near_miss_class" in p.text


def test_near_miss_prompt_cross_class_mentions_class_axis() -> None:
    cell = Cell(TaxonomyPattern.NUMERICAL_CONFLICT, Domain.SCIENCE_MEDICINE, Difficulty.HARD)
    p = build_near_miss_prompt(cell, TaxonomyPattern.QUANTITATIVE_CONSENSUS)
    # NC is DISPUTED, QC is TRUSTWORTHY → prompt should highlight class axis
    assert "governance class" in p.text.lower()


# ---------------------------------------------------------------------------
# NearMissOrchestrator wiring
# ---------------------------------------------------------------------------


def _good_near_miss_response(
    cell: Cell,
    secondary: TaxonomyPattern,
    case_id: str = "nm_001",
) -> str:
    cls = cell.governance_class.value
    case = {
        "id": case_id,
        "input": {
            "query": "boundary query",
            "contexts": [
                {"text": f"context {i} with 5 and 3", "authority_score": 0.6}
                for i in range(2)
            ],
        },
        "governance": {
            "classification": cls,
            "conflict_density": 0.8 if cls == "DISPUTED" else 0.2,
            "evidence_sufficiency": 0.7 if cls == "TRUSTWORTHY" else 0.5,
            "hallucination_pressure": 0.2 if cls == "TRUSTWORTHY" else 0.55,
        },
        "taxonomy": {
            "governance_class": cls,
            "pattern": cell.pattern.value,
            "cell_id": cell.cell_id,
        },
        "routing": {"expert_fired": cell.domain.value},
        "meta": {
            "difficulty": cell.difficulty.value,
            "near_miss_class": governance_class_of(secondary).value,
            "near_miss_reason": "could look like the runner-up at a glance",
        },
    }
    return json.dumps(case)


def test_near_miss_orchestrator_accepts_valid_case(tmp_path: Path) -> None:
    vault = Vault.open(tmp_path / "v")
    cell = Cell(
        TaxonomyPattern.NUMERICAL_CONFLICT,
        Domain.SCIENCE_MEDICINE,
        Difficulty.HARD,
    )
    secondary = TaxonomyPattern.QUANTITATIVE_CONSENSUS
    response = _good_near_miss_response(cell, secondary, "nm_a")
    base = Orchestrator(
        vault=vault,
        provider=StubProvider(response=response, name="stub"),
        max_attempts_per_cell=1,
    )
    nm = NearMissOrchestrator(base=base)
    results = nm.fill_boundary(cell, secondary, n=1, batch_id="b1")
    assert len(results) == 1
    assert results[0].outcome == Outcome.ACCEPTED, results[0].error or "no error"
    assert len(vault) == 1
    # Vaulted case carries the near_miss_class set by the orchestrator
    stored = vault.get("nm_a")
    assert stored is not None
    assert stored["meta"]["near_miss_class"] == governance_class_of(secondary).value


def test_near_miss_orchestrator_patches_missing_near_miss_fields(tmp_path: Path) -> None:
    """If the generator forgets near_miss_class / near_miss_reason, the
    orchestrator backfills them so the case still passes."""
    vault = Vault.open(tmp_path / "v")
    cell = Cell(TaxonomyPattern.WRONG_SPECIFICITY, Domain.HISTORY_GEOGRAPHY, Difficulty.HARD)
    secondary = TaxonomyPattern.WRONG_ENTITY

    case_without_nm = {
        "id": "no_nm_1",
        "input": {"query": "q", "contexts": [{"text": "c"}]},
        "governance": {"classification": "ABSTAIN"},
        "taxonomy": {
            "governance_class": "ABSTAIN",
            "pattern": cell.pattern.value,
            "cell_id": cell.cell_id,
        },
        "routing": {"expert_fired": cell.domain.value},
        "meta": {"difficulty": cell.difficulty.value},
        # NO near_miss_class, NO near_miss_reason
    }
    base = Orchestrator(
        vault=vault,
        provider=StubProvider(response=json.dumps(case_without_nm)),
        max_attempts_per_cell=1,
    )
    nm = NearMissOrchestrator(base=base)
    results = nm.fill_boundary(cell, secondary, n=1)
    assert results[0].outcome == Outcome.ACCEPTED
    stored = vault.get("no_nm_1")
    assert stored is not None
    assert stored["meta"]["near_miss_class"] == "ABSTAIN"  # both are ABSTAIN in this pair
    assert stored["meta"]["near_miss_reason"]  # backfilled, non-empty
