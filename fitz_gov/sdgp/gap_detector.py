"""SDGP gap detector — read cell coverage, rank gaps, emit generation queue.

The 3D-gap-detection step from the user spec. Takes a `Vault` (or any
dict-like `{cell_id: count}`), a per-cell minimum threshold, and produces
a ranked list of cells that need more cases. The orchestrator pops cells
off this queue and hands them to the generator.

Default ranking is *biggest absolute gap first* — fills the most-empty
cells first. `priority_weights` overrides this so the user can boost
specific patterns / classes / difficulties (e.g. weight hard cases higher,
or weight ABSTAIN patterns higher because they're underrepresented).

Includes filters so the queue can be scoped to one pattern, one class, etc.,
which is how the orchestrator runs targeted batches.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping

from .taxonomy import (
    Cell,
    Difficulty,
    Domain,
    GovernanceClass,
    TaxonomyPattern,
    all_cells,
    governance_class_of,
)


# ---------------------------------------------------------------------------
# Per-cell target
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class CellTarget:
    """How many cases a cell should hold to count as 'covered'."""

    default: int = 20  # ROADMAP §3: 20-25 examples per cell for V6 coverage
    overrides: dict[str, int] = field(default_factory=dict)  # cell_id → target

    def for_cell(self, cell: Cell | str) -> int:
        key = cell.cell_id if isinstance(cell, Cell) else cell
        return self.overrides.get(key, self.default)


# ---------------------------------------------------------------------------
# Gap row
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class Gap:
    """One row in the gap queue.

    `priority` is the rank key (highest priority first). For the default
    unweighted ranking, `priority == gap`. With weights applied,
    `priority = gap * weight`. `GapDetector.rank()` sorts on this descending.
    """

    priority: float
    cell: Cell
    current: int
    target: int

    @property
    def gap(self) -> int:
        return max(self.target - self.current, 0)

    @property
    def coverage_ratio(self) -> float:
        return self.current / max(self.target, 1)


# ---------------------------------------------------------------------------
# Priority weights
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class PriorityWeights:
    """Multiplicative weights applied to each cell's gap before ranking.

    The final priority for a cell is:

        priority = gap * pattern_weight * domain_weight * difficulty_weight * class_weight

    Unspecified categories default to 1.0 (no boost). Use this to push the
    orchestrator toward, e.g., hard cases first or under-represented patterns.
    """

    by_pattern: dict[TaxonomyPattern, float] = field(default_factory=dict)
    by_domain: dict[Domain, float] = field(default_factory=dict)
    by_difficulty: dict[Difficulty, float] = field(default_factory=dict)
    by_class: dict[GovernanceClass, float] = field(default_factory=dict)

    def weight_for(self, cell: Cell) -> float:
        return (
            self.by_pattern.get(cell.pattern, 1.0)
            * self.by_domain.get(cell.domain, 1.0)
            * self.by_difficulty.get(cell.difficulty, 1.0)
            * self.by_class.get(governance_class_of(cell.pattern), 1.0)
        )


# ---------------------------------------------------------------------------
# Filter
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class CellFilter:
    """Restrict which cells the gap detector considers. None = no restriction."""

    patterns: set[TaxonomyPattern] | None = None
    domains: set[Domain] | None = None
    difficulties: set[Difficulty] | None = None
    classes: set[GovernanceClass] | None = None
    include_meta_domain: bool = False  # whether `conflict_detection` is a valid generation target

    def matches(self, cell: Cell) -> bool:
        if not self.include_meta_domain and cell.domain == Domain.CONFLICT_DETECTION:
            return False
        if self.patterns is not None and cell.pattern not in self.patterns:
            return False
        if self.domains is not None and cell.domain not in self.domains:
            return False
        if self.difficulties is not None and cell.difficulty not in self.difficulties:
            return False
        if self.classes is not None and governance_class_of(cell.pattern) not in self.classes:
            return False
        return True


# ---------------------------------------------------------------------------
# Gap detector
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class GapDetector:
    """Stateless gap analyser.

    Single entry point: `rank(cell_counts, target, weights=None, filter=None)`.
    Returns a list of `Gap` rows sorted highest-priority first. Cells already
    at or above their target are excluded.
    """

    def rank(
        self,
        cell_counts: Mapping[str, int],
        target: CellTarget | int = 20,
        *,
        weights: PriorityWeights | None = None,
        filter: CellFilter | None = None,
    ) -> list[Gap]:
        if isinstance(target, int):
            target = CellTarget(default=target)
        weights = weights or PriorityWeights()
        flt = filter or CellFilter()

        gaps: list[Gap] = []
        for cell in all_cells(include_meta_domain=flt.include_meta_domain):
            if not flt.matches(cell):
                continue
            current = int(cell_counts.get(cell.cell_id, 0))
            t = target.for_cell(cell)
            if current >= t:
                continue
            gap_size = t - current
            priority = gap_size * weights.weight_for(cell)
            gaps.append(Gap(priority=priority, cell=cell, current=current, target=t))
        # Highest priority first; tie-break on cell_id for stable ordering.
        gaps.sort(key=lambda g: (-g.priority, g.cell.cell_id))
        return gaps

    def coverage_summary(
        self,
        cell_counts: Mapping[str, int],
        target: CellTarget | int = 20,
        *,
        filter: CellFilter | None = None,
    ) -> dict[str, int]:
        """High-level counts of how the corpus stacks up vs target."""
        if isinstance(target, int):
            target = CellTarget(default=target)
        flt = filter or CellFilter()
        n_cells = 0
        n_at_target = 0
        n_with_some = 0
        n_empty = 0
        total_cases = 0
        total_gap = 0
        for cell in all_cells(include_meta_domain=flt.include_meta_domain):
            if not flt.matches(cell):
                continue
            n_cells += 1
            current = int(cell_counts.get(cell.cell_id, 0))
            t = target.for_cell(cell)
            total_cases += current
            if current == 0:
                n_empty += 1
            else:
                n_with_some += 1
            if current >= t:
                n_at_target += 1
            else:
                total_gap += t - current
        return {
            "cells_considered": n_cells,
            "cells_at_target": n_at_target,
            "cells_with_some_cases": n_with_some,
            "cells_empty": n_empty,
            "total_cases": total_cases,
            "total_gap_to_fill": total_gap,
        }


# ---------------------------------------------------------------------------
# Convenience
# ---------------------------------------------------------------------------


def rank_from_vault(
    vault: "Vault",  # noqa: F821 — fwd ref; importing Vault would cycle
    target: CellTarget | int = 20,
    *,
    weights: PriorityWeights | None = None,
    filter: CellFilter | None = None,
) -> list[Gap]:
    """Shortcut: read counts straight off a `Vault` and rank."""
    return GapDetector().rank(
        vault.cell_counts(), target, weights=weights, filter=filter
    )
