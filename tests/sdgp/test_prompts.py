"""Tests for fitz_gov.sdgp.prompts."""

from __future__ import annotations

from pathlib import Path

import pytest

from fitz_gov.sdgp.prompts import (
    DIFFICULTY_HINTS,
    DOMAIN_HINTS,
    MODALITY_HINTS,
    PATTERN_GUIDANCE,
    SYSTEM_MESSAGE,
    GeneratorPrompt,
    build_prompt,
    build_prompt_for_cell,
    few_shot_for_cell,
)
from fitz_gov.sdgp.taxonomy import (
    Cell,
    Difficulty,
    Domain,
    TaxonomyPattern,
)
from fitz_gov.sdgp.vault import Provenance, Vault


# ---------------------------------------------------------------------------
# Coverage: every pattern + domain + difficulty has guidance
# ---------------------------------------------------------------------------


def test_every_pattern_has_guidance() -> None:
    assert set(PATTERN_GUIDANCE.keys()) == set(TaxonomyPattern)


def test_every_domain_has_hints() -> None:
    assert set(DOMAIN_HINTS.keys()) == set(Domain)


def test_every_difficulty_has_hints() -> None:
    assert set(DIFFICULTY_HINTS.keys()) == set(Difficulty)


def test_every_modality_has_hints() -> None:
    assert set(MODALITY_HINTS.keys()) == {"unstructured", "structured", "code"}


# ---------------------------------------------------------------------------
# build_prompt
# ---------------------------------------------------------------------------


def _cell() -> Cell:
    return Cell(
        pattern=TaxonomyPattern.NUMERICAL_CONFLICT,
        domain=Domain.SCIENCE_MEDICINE,
        difficulty=Difficulty.HARD,
    )


def test_build_prompt_returns_generator_prompt() -> None:
    p = build_prompt(_cell())
    assert isinstance(p, GeneratorPrompt)
    assert p.cell == _cell()
    assert p.n_few_shots == 0
    assert p.modality == "unstructured"


def test_prompt_contains_cell_id_and_pattern_name() -> None:
    cell = _cell()
    p = build_prompt(cell)
    assert cell.cell_id in p.text
    assert cell.pattern.value in p.text
    assert cell.domain.value in p.text
    assert cell.difficulty.value in p.text
    assert "unstructured" in p.text


def test_prompt_contains_governance_class() -> None:
    cell = _cell()
    p = build_prompt(cell)
    assert "DISPUTED" in p.text  # numerical_conflict is DISPUTED


def test_prompt_contains_pattern_guidance() -> None:
    cell = _cell()
    p = build_prompt(cell)
    assert "digit-bearing" in p.text.lower() or "numerical" in p.text.lower()


def test_prompt_contains_domain_hints() -> None:
    cell = _cell()
    p = build_prompt(cell)
    # science_medicine hint mentions peer-reviewed
    assert "peer-reviewed" in p.text.lower()


def test_prompt_contains_output_schema() -> None:
    p = build_prompt(_cell())
    assert "Output a single valid JSON object" in p.text
    assert "taxonomy.cell_id" in p.text or "cell_id" in p.text
    assert "evaluation" in p.text
    assert "meta.domain" not in p.text
    assert "meta.subcategory" not in p.text
    assert "introduced_in" not in p.text


def test_prompt_can_target_structured_modality() -> None:
    p = build_prompt(_cell(), modality="structured")

    assert p.modality == "structured"
    assert "`meta.modality` MUST equal 'structured'" in p.text
    assert "table rows" in p.text


def test_prompt_rejects_unknown_modality() -> None:
    with pytest.raises(ValueError):
        build_prompt(_cell(), modality="spreadsheet")


def test_prompt_constraints_hardcode_cell_values() -> None:
    """The prompt should pin the model to the exact cell_id/pattern/domain
    so the output is structurally aligned with the cell spec."""
    cell = _cell()
    p = build_prompt(cell)
    # Each constraint references the actual cell value
    assert f"{cell.cell_id!r}" in p.text
    assert f"{cell.pattern.value!r}" in p.text
    assert f"{cell.domain.value!r}" in p.text
    assert f"{cell.difficulty.value!r}" in p.text


def test_v8_gap_pattern_prompt_uses_primary_cell() -> None:
    cell = Cell(
        pattern=TaxonomyPattern.VERDICT_CONFLICT,
        domain=Domain.TECHNOLOGY_COMPUTING,
        difficulty=Difficulty.HARD,
    )
    p = build_prompt(cell)
    assert "verdict_conflict" in p.text
    assert cell.cell_id in p.text
    assert "subpattern" not in p.text


def test_prompt_with_few_shots_includes_them() -> None:
    cell = _cell()
    examples = [
        {
            "id": "demo_001",
            "input": {"query": "demo query", "contexts": [{"text": "demo ctx"}]},
            "taxonomy": {"pattern": "numerical_conflict", "cell_id": cell.cell_id},
            "governance": {"classification": "DISPUTED"},
        }
    ]
    p = build_prompt(cell, few_shot_examples=examples)
    assert "demo query" in p.text
    assert "Few-shot examples" in p.text
    assert p.n_few_shots == 1


def test_prompt_with_no_few_shots_omits_block() -> None:
    p = build_prompt(_cell())
    assert "Few-shot examples" not in p.text


# ---------------------------------------------------------------------------
# few_shot_for_cell — vault lookup
# ---------------------------------------------------------------------------


def _make_case(
    pattern: TaxonomyPattern,
    domain: Domain,
    case_id: str,
) -> dict:
    cell = Cell(pattern=pattern, domain=domain, difficulty=Difficulty.HARD)
    return {
        "id": case_id,
        "input": {"query": f"q for {case_id}", "contexts": [{"text": f"ctx for {case_id}"}]},
        "governance": {"classification": cell.governance_class.value},
        "taxonomy": {
            "governance_class": cell.governance_class.value,
            "pattern": pattern.value,
            "cell_id": cell.cell_id,
        },
        "meta": {"difficulty": "hard"},
    }


def test_few_shot_prefers_same_domain(tmp_path: Path) -> None:
    vault = Vault.open(tmp_path / "v")
    # Same pattern, same domain
    vault.add(_make_case(TaxonomyPattern.NUMERICAL_CONFLICT, Domain.SCIENCE_MEDICINE, "same_dom_1"))
    # Same pattern, different domain
    vault.add(_make_case(TaxonomyPattern.NUMERICAL_CONFLICT, Domain.LAW_POLICY, "other_dom_1"))
    # Different pattern, same class
    vault.add(_make_case(TaxonomyPattern.TEMPORAL_CONFLICT, Domain.SCIENCE_MEDICINE, "other_pat_1"))

    cell = Cell(TaxonomyPattern.NUMERICAL_CONFLICT, Domain.SCIENCE_MEDICINE, Difficulty.HARD)
    examples = few_shot_for_cell(vault, cell, n=1, seed=42)
    assert len(examples) == 1
    assert examples[0]["id"] == "same_dom_1"


def test_few_shot_falls_back_to_other_domain(tmp_path: Path) -> None:
    vault = Vault.open(tmp_path / "v")
    vault.add(_make_case(TaxonomyPattern.NUMERICAL_CONFLICT, Domain.LAW_POLICY, "only_other_dom"))
    cell = Cell(TaxonomyPattern.NUMERICAL_CONFLICT, Domain.SCIENCE_MEDICINE, Difficulty.HARD)
    examples = few_shot_for_cell(vault, cell, n=2)
    assert len(examples) == 1
    assert examples[0]["id"] == "only_other_dom"


def test_few_shot_falls_back_to_same_class(tmp_path: Path) -> None:
    vault = Vault.open(tmp_path / "v")
    # Different pattern but same governance class (DISPUTED)
    vault.add(_make_case(TaxonomyPattern.AUTHORITY_CONFLICT, Domain.SCIENCE_MEDICINE, "same_class_1"))
    cell = Cell(TaxonomyPattern.NUMERICAL_CONFLICT, Domain.SCIENCE_MEDICINE, Difficulty.HARD)
    examples = few_shot_for_cell(vault, cell, n=1)
    assert len(examples) == 1
    assert examples[0]["id"] == "same_class_1"


def test_few_shot_returns_empty_when_no_matches(tmp_path: Path) -> None:
    vault = Vault.open(tmp_path / "v")
    # Only TRUSTWORTHY cases in the vault
    vault.add(_make_case(TaxonomyPattern.DIRECT_ANSWER, Domain.SCIENCE_MEDICINE, "t1"))
    cell = Cell(TaxonomyPattern.NUMERICAL_CONFLICT, Domain.SCIENCE_MEDICINE, Difficulty.HARD)
    examples = few_shot_for_cell(vault, cell, n=2)
    assert examples == []


def test_few_shot_strips_vault_provenance(tmp_path: Path) -> None:
    vault = Vault.open(tmp_path / "v")
    vault.add(
        _make_case(TaxonomyPattern.NUMERICAL_CONFLICT, Domain.SCIENCE_MEDICINE, "x"),
        provenance=Provenance(provider="test"),
    )
    cell = Cell(TaxonomyPattern.NUMERICAL_CONFLICT, Domain.SCIENCE_MEDICINE, Difficulty.HARD)
    examples = few_shot_for_cell(vault, cell, n=1)
    assert "_vault" not in examples[0]


def test_few_shot_seed_is_reproducible(tmp_path: Path) -> None:
    vault = Vault.open(tmp_path / "v")
    for i in range(5):
        vault.add(_make_case(TaxonomyPattern.NUMERICAL_CONFLICT, Domain.SCIENCE_MEDICINE, f"x{i}"))
    cell = Cell(TaxonomyPattern.NUMERICAL_CONFLICT, Domain.SCIENCE_MEDICINE, Difficulty.HARD)
    a = few_shot_for_cell(vault, cell, n=2, seed=42)
    b = few_shot_for_cell(vault, cell, n=2, seed=42)
    assert [e["id"] for e in a] == [e["id"] for e in b]


# ---------------------------------------------------------------------------
# build_prompt_for_cell — end-to-end vault-driven build
# ---------------------------------------------------------------------------


def test_build_prompt_for_cell_pulls_few_shots(tmp_path: Path) -> None:
    vault = Vault.open(tmp_path / "v")
    for i in range(3):
        vault.add(_make_case(TaxonomyPattern.NUMERICAL_CONFLICT, Domain.SCIENCE_MEDICINE, f"fs_{i}"))
    cell = Cell(TaxonomyPattern.NUMERICAL_CONFLICT, Domain.SCIENCE_MEDICINE, Difficulty.HARD)
    p = build_prompt_for_cell(cell, vault, n_few_shots=2, seed=42)
    assert p.n_few_shots == 2
    assert "Few-shot examples" in p.text


# ---------------------------------------------------------------------------
# SYSTEM_MESSAGE sanity
# ---------------------------------------------------------------------------


def test_system_message_mentions_json_only() -> None:
    assert "JSON" in SYSTEM_MESSAGE
