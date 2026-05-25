"""Tests for fitz_gov.sdgp.monitor."""

from __future__ import annotations

from pathlib import Path

import pytest

from fitz_gov.sdgp.monitor import (
    by_class,
    by_difficulty,
    by_domain,
    by_pattern,
    format_coverage_report,
    report_for_vault,
    write_coverage_report,
)
from fitz_gov.sdgp.taxonomy import (
    Cell,
    Difficulty,
    Domain,
    GovernanceClass,
    PRIMARY_DOMAINS,
    TaxonomyPattern,
)
from fitz_gov.sdgp.vault import Vault


# ---------------------------------------------------------------------------
# Axis breakdowns
# ---------------------------------------------------------------------------


def test_by_class_returns_three_rows() -> None:
    rows = by_class({}, target=20)
    assert len(rows) == 3
    labels = {r.label for r in rows}
    assert labels == {"ABSTAIN", "DISPUTED", "TRUSTWORTHY"}


def test_by_class_cells_total_is_consistent() -> None:
    rows = by_class({}, target=20)
    totals = {r.label: r.cells_total for r in rows}
    assert totals == {
        "ABSTAIN": 8 * 7 * 3,
        "DISPUTED": 8 * 7 * 3,
        "TRUSTWORTHY": 7 * 7 * 3,
    }


def test_by_pattern_returns_23_rows() -> None:
    rows = by_pattern({}, target=20)
    assert len(rows) == 23


def test_by_domain_returns_7_rows() -> None:
    rows = by_domain({}, target=20)
    assert len(rows) == 7
    assert all(r.cells_total == 23 * 3 for r in rows)


def test_by_difficulty_returns_3_rows() -> None:
    rows = by_difficulty({}, target=20)
    assert len(rows) == 3
    assert all(r.cells_total == 23 * 7 for r in rows)


def test_axis_percentages() -> None:
    cell = Cell(TaxonomyPattern.WRONG_ENTITY, Domain.HISTORY_GEOGRAPHY, Difficulty.HARD)
    counts = {cell.cell_id: 25}  # over target
    rows = by_pattern(counts, target=20)
    wrong_entity_row = next(r for r in rows if r.label == "wrong_entity")
    # 1 / 21 cells at target = 4.76%
    assert wrong_entity_row.cells_at_target == 1
    assert abs(wrong_entity_row.percent_filled - 100.0 / 21) < 1e-6


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------


def test_format_coverage_report_has_all_sections() -> None:
    text = format_coverage_report({}, target=20)
    for header in [
        "# SDGP coverage report",
        "### By governance class",
        "### By difficulty",
        "### By expert domain",
        "### By taxonomy pattern",
        "### Top 10 most-filled cells",
        "### Top 10 gaps (most-empty cells)",
    ]:
        assert header in text


def test_format_coverage_report_includes_target_and_totals() -> None:
    text = format_coverage_report({}, target=25)
    assert "**Target per cell**: 25" in text
    assert "**Total cells (primary 23 × 7 × 3)**: 483" in text
    assert "**Cells at target**: 0 (0.0%)" in text


def test_format_coverage_report_with_some_cases() -> None:
    cell = Cell(TaxonomyPattern.WRONG_ENTITY, Domain.HISTORY_GEOGRAPHY, Difficulty.HARD)
    text = format_coverage_report({cell.cell_id: 20}, target=20)
    assert "**Cells at target**: 1" in text
    assert "**Cells empty**: 482" in text
    assert cell.cell_id in text  # appears in the top-filled table


def test_format_coverage_report_vault_path_in_header() -> None:
    text = format_coverage_report({}, vault_path=Path("/some/path"))
    assert "/some/path" in text or "\\some\\path" in text


# ---------------------------------------------------------------------------
# Write to disk
# ---------------------------------------------------------------------------


def test_write_coverage_report(tmp_path: Path) -> None:
    out = tmp_path / "subdir" / "report.md"
    written = write_coverage_report({}, out, target=20)
    assert written == out
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "# SDGP coverage report" in text


# ---------------------------------------------------------------------------
# Vault integration
# ---------------------------------------------------------------------------


def test_report_for_vault_includes_vault_path(tmp_path: Path) -> None:
    vault = Vault.open(tmp_path / "vault")
    text = report_for_vault(vault, target=20)
    assert str(vault.root) in text or str(vault.root).replace("\\", "/") in text


def test_report_for_vault_writes_when_out_path_given(tmp_path: Path) -> None:
    vault = Vault.open(tmp_path / "vault")
    out = tmp_path / "report.md"
    text = report_for_vault(vault, out_path=out, target=20)
    assert out.exists()
    assert out.read_text(encoding="utf-8") == text
