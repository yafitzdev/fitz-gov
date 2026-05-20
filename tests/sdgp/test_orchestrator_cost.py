"""Integration tests: Orchestrator + CostTracker."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fitz_gov.sdgp.cost import CostTracker
from fitz_gov.sdgp.orchestrator import Orchestrator, Outcome
from fitz_gov.sdgp.providers import StubProvider
from fitz_gov.sdgp.taxonomy import Cell, Difficulty, Domain, TaxonomyPattern
from fitz_gov.sdgp.vault import Vault


def _good_case(cell: Cell, case_id: str = "x") -> dict:
    return {
        "id": case_id,
        "input": {"query": "q", "contexts": [{"text": "c1"}, {"text": "c2"}]},
        "governance": {"classification": cell.governance_class.value},
        "taxonomy": {
            "governance_class": cell.governance_class.value,
            "pattern": cell.pattern.value,
            "cell_id": cell.cell_id,
        },
        "routing": {"expert_fired": cell.domain.value},
        "meta": {"difficulty": cell.difficulty.value},
    }


def test_cost_tracker_records_on_accepted(tmp_path: Path) -> None:
    vault = Vault.open(tmp_path / "v")
    cell = Cell(TaxonomyPattern.WRONG_ENTITY, Domain.HISTORY_GEOGRAPHY, Difficulty.HARD)
    tracker = CostTracker()
    orch = Orchestrator(
        vault=vault,
        provider=StubProvider(response=json.dumps(_good_case(cell, "ok_1")), name="stub"),
        cost_tracker=tracker,
        max_attempts_per_cell=1,
    )
    r = orch.generate_one_cell(cell)
    assert r.outcome == Outcome.ACCEPTED
    assert tracker.total_calls == 1
    assert tracker.calls[0].outcome == "accepted"
    assert tracker.calls[0].provider == "stub"
    assert tracker.calls[0].cell_id == cell.cell_id


def test_cost_tracker_records_on_parse_failure(tmp_path: Path) -> None:
    vault = Vault.open(tmp_path / "v")
    cell = Cell(TaxonomyPattern.WRONG_ENTITY, Domain.HISTORY_GEOGRAPHY, Difficulty.HARD)
    tracker = CostTracker()
    orch = Orchestrator(
        vault=vault,
        provider=StubProvider(response="not JSON"),
        cost_tracker=tracker,
        max_attempts_per_cell=2,
    )
    r = orch.generate_one_cell(cell)
    assert r.outcome == Outcome.REJECTED_PARSE
    # Both retries recorded
    assert tracker.total_calls == 2
    assert all(c.outcome == "rejected_parse" for c in tracker.calls)


def test_cost_tracker_records_on_provider_failure(tmp_path: Path) -> None:
    from fitz_gov.sdgp.providers import GenerateRequest, Provider, ProviderError

    class Broken(Provider):
        name = "broken"
        version = "0"

        def generate(self, req: GenerateRequest) -> str:
            raise ProviderError("nope")

    vault = Vault.open(tmp_path / "v")
    cell = Cell(TaxonomyPattern.WRONG_ENTITY, Domain.HISTORY_GEOGRAPHY, Difficulty.HARD)
    tracker = CostTracker()
    orch = Orchestrator(
        vault=vault,
        provider=Broken(),
        cost_tracker=tracker,
        max_attempts_per_cell=3,
    )
    r = orch.generate_one_cell(cell)
    assert r.outcome == Outcome.REJECTED_PROVIDER
    # Only one call attempt — provider failures don't retry
    assert tracker.total_calls == 1
    assert tracker.calls[0].outcome == "rejected_provider"
    # Output tokens = 0 because no response
    assert tracker.calls[0].output_tokens == 0
