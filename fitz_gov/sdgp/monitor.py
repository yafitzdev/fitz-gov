"""SDGP coverage monitor — markdown report of cell coverage + gap distribution.

Reads cell counts from a `Vault` (or any dict-like) and writes a markdown
report covering:

  - Header: vault size, target, % cells at target.
  - Breakdown by governance class (ABSTAIN / DISPUTED / TRUSTWORTHY).
  - Breakdown by taxonomy pattern.
  - Breakdown by expert domain (all 7 primary).
  - Breakdown by difficulty (easy / medium / hard).
  - Top-N most-filled cells and top-N most-empty cells.

`format_coverage_report()` returns a string. `write_coverage_report()` writes
to a file. The CLI calls one of these after every fill-gaps run so the
operator can see exactly what landed.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .gap_detector import CellTarget, GapDetector
from .taxonomy import (
    Cell,
    Difficulty,
    Domain,
    GovernanceClass,
    PRIMARY_DOMAINS,
    TaxonomyPattern,
    all_cells,
    governance_class_of,
)
from .vault import Vault


@dataclass(slots=True)
class CoverageAxis:
    """Counts + cells-at-target along one axis of the 3D space."""

    label: str
    cells_total: int
    cells_at_target: int
    cases_total: int
    gap_total: int

    @property
    def percent_filled(self) -> float:
        return 100.0 * self.cells_at_target / max(self.cells_total, 1)

    @property
    def avg_per_cell(self) -> float:
        return self.cases_total / max(self.cells_total, 1)


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------


def _as_target(target: CellTarget | int) -> CellTarget:
    return target if isinstance(target, CellTarget) else CellTarget(default=int(target))


def _axis(
    label: str,
    cells: list[Cell],
    cell_counts: Mapping[str, int],
    target: CellTarget,
) -> CoverageAxis:
    n_total = len(cells)
    n_at = 0
    cases = 0
    gap = 0
    for c in cells:
        t = target.for_cell(c)
        cur = int(cell_counts.get(c.cell_id, 0))
        cases += cur
        if cur >= t:
            n_at += 1
        else:
            gap += t - cur
    return CoverageAxis(
        label=label,
        cells_total=n_total,
        cells_at_target=n_at,
        cases_total=cases,
        gap_total=gap,
    )


def by_class(cell_counts: Mapping[str, int], target: CellTarget | int) -> list[CoverageAxis]:
    target = _as_target(target)
    cells = all_cells()  # primary domains only
    buckets: dict[GovernanceClass, list[Cell]] = defaultdict(list)
    for c in cells:
        buckets[governance_class_of(c.pattern)].append(c)
    return [_axis(cls.value, buckets[cls], cell_counts, target) for cls in GovernanceClass]


def by_pattern(cell_counts: Mapping[str, int], target: CellTarget | int) -> list[CoverageAxis]:
    target = _as_target(target)
    cells = all_cells()
    buckets: dict[TaxonomyPattern, list[Cell]] = defaultdict(list)
    for c in cells:
        buckets[c.pattern].append(c)
    # Group: ABSTAIN patterns, then DISPUTED, then TRUSTWORTHY (in enum order)
    return [_axis(p.value, buckets[p], cell_counts, target) for p in TaxonomyPattern]


def by_domain(cell_counts: Mapping[str, int], target: CellTarget | int) -> list[CoverageAxis]:
    target = _as_target(target)
    cells = all_cells()
    buckets: dict[Domain, list[Cell]] = defaultdict(list)
    for c in cells:
        buckets[c.domain].append(c)
    return [_axis(d.value, buckets[d], cell_counts, target) for d in PRIMARY_DOMAINS]


def by_difficulty(cell_counts: Mapping[str, int], target: CellTarget | int) -> list[CoverageAxis]:
    target = _as_target(target)
    cells = all_cells()
    buckets: dict[Difficulty, list[Cell]] = defaultdict(list)
    for c in cells:
        buckets[c.difficulty].append(c)
    return [_axis(d.value, buckets[d], cell_counts, target) for d in Difficulty]


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def _render_axis_table(rows: list[CoverageAxis], header: str) -> str:
    lines = [
        f"### {header}",
        "",
        "| Bucket | Cells | At target | % filled | Cases | Avg/cell | Gap |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r.label} | {r.cells_total} | {r.cells_at_target} | "
            f"{r.percent_filled:.1f}% | {r.cases_total} | "
            f"{r.avg_per_cell:.1f} | {r.gap_total} |"
        )
    return "\n".join(lines)


def _render_top_n(
    cell_counts: Mapping[str, int], target: CellTarget, n: int, *, empty_first: bool
) -> str:
    cells = all_cells()
    rows: list[tuple[Cell, int, int]] = [
        (c, int(cell_counts.get(c.cell_id, 0)), target.for_cell(c))
        for c in cells
    ]
    if empty_first:
        # Largest gap first (cells with 0 cases at the top)
        rows.sort(key=lambda r: (-(r[2] - r[1]), r[0].cell_id))
        rows = rows[:n]
        header = f"### Top {n} gaps (most-empty cells)"
    else:
        rows.sort(key=lambda r: (-r[1], r[0].cell_id))
        rows = rows[:n]
        header = f"### Top {n} most-filled cells"
    lines = [
        header,
        "",
        "| cell_id | Cases | Target | Gap |",
        "|---|---:|---:|---:|",
    ]
    for cell, cur, t in rows:
        lines.append(f"| `{cell.cell_id}` | {cur} | {t} | {max(t - cur, 0)} |")
    return "\n".join(lines)


def format_coverage_report(
    cell_counts: Mapping[str, int],
    *,
    target: CellTarget | int = 20,
    vault_path: Path | None = None,
    top_n: int = 10,
) -> str:
    """Build a markdown coverage report for the given cell counts."""
    if isinstance(target, int):
        target = CellTarget(default=target)

    detector = GapDetector()
    summary = detector.coverage_summary(cell_counts, target)
    total_cells = summary["cells_considered"]
    at_target = summary["cells_at_target"]
    empty = summary["cells_empty"]
    total_cases = summary["total_cases"]
    total_gap = summary["total_gap_to_fill"]

    header_lines = [
        "# SDGP coverage report",
        "",
    ]
    if vault_path is not None:
        header_lines.append(f"**Vault**: `{vault_path}`")
    header_lines.extend([
        f"**Target per cell**: {target.default}",
        (
            f"**Total cells (primary {len(TaxonomyPattern)} × "
            f"{len(PRIMARY_DOMAINS)} × {len(Difficulty)})**: {total_cells}"
        ),
        f"**Cells at target**: {at_target} ({100.0 * at_target / max(total_cells, 1):.1f}%)",
        f"**Cells empty**: {empty} ({100.0 * empty / max(total_cells, 1):.1f}%)",
        f"**Total cases**: {total_cases}",
        f"**Total gap to fill**: {total_gap}",
        "",
        "---",
        "",
    ])

    sections = [
        _render_axis_table(by_class(cell_counts, target), "By governance class"),
        "",
        "---",
        "",
        _render_axis_table(by_difficulty(cell_counts, target), "By difficulty"),
        "",
        "---",
        "",
        _render_axis_table(by_domain(cell_counts, target), "By expert domain"),
        "",
        "---",
        "",
        _render_axis_table(by_pattern(cell_counts, target), "By taxonomy pattern"),
        "",
        "---",
        "",
        _render_top_n(cell_counts, target, top_n, empty_first=False),
        "",
        "---",
        "",
        _render_top_n(cell_counts, target, top_n, empty_first=True),
        "",
    ]

    return "\n".join(header_lines + sections)


def write_coverage_report(
    cell_counts: Mapping[str, int],
    out_path: Path,
    *,
    target: CellTarget | int = 20,
    vault_path: Path | None = None,
    top_n: int = 10,
) -> Path:
    """Write the markdown report to disk and return the path."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    text = format_coverage_report(
        cell_counts, target=target, vault_path=vault_path, top_n=top_n
    )
    out_path.write_text(text, encoding="utf-8")
    return out_path


def report_for_vault(
    vault: Vault,
    *,
    target: CellTarget | int = 20,
    out_path: Path | None = None,
    top_n: int = 10,
) -> str:
    """Shortcut: build report directly from a `Vault`; optionally write to disk."""
    counts = vault.cell_counts()
    text = format_coverage_report(counts, target=target, vault_path=vault.root, top_n=top_n)
    if out_path is not None:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        Path(out_path).write_text(text, encoding="utf-8")
    return text
