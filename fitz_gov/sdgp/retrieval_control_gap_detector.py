"""V9 retrieval-control gap detector.

The original SDGP gap detector targets taxonomy coverage:
`taxonomy_pattern x domain x difficulty`.

V9 needs a second generation queue for retrieval-control coverage. The first
approved V9 target is collapsed answerability shape, distributed across:

    governance_class x domain x difficulty x collapsed_answerability_shape

This module is mechanical only. It reads existing labels, collapses the
V8.2 detailed answerability labels, and ranks coverage gaps. It does not assign
semantic labels and does not mutate the vault.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Mapping

from .taxonomy import Difficulty, Domain, GovernanceClass, PRIMARY_DOMAINS


_CELL_SEP = "__"


class CollapsedAnswerabilityShape(str, Enum):
    """V9 answerability-shape buckets used for targeted generation."""

    DIRECT_ANSWER = "direct_answer"
    SYNTHESIS_ANSWER = "synthesis_answer"
    SET_ANSWER = "set_answer"
    STRUCTURED_REASONING = "structured_reasoning"


V9_ANSWERABILITY_COLLAPSE: dict[str, CollapsedAnswerabilityShape] = {
    "single_fact": CollapsedAnswerabilityShape.DIRECT_ANSWER,
    "exact_lookup": CollapsedAnswerabilityShape.DIRECT_ANSWER,
    "yes_no": CollapsedAnswerabilityShape.DIRECT_ANSWER,
    "citation_required": CollapsedAnswerabilityShape.DIRECT_ANSWER,
    "explanation": CollapsedAnswerabilityShape.SYNTHESIS_ANSWER,
    "summary": CollapsedAnswerabilityShape.SYNTHESIS_ANSWER,
    "list": CollapsedAnswerabilityShape.SET_ANSWER,
    "exhaustive_list": CollapsedAnswerabilityShape.SET_ANSWER,
    "comparison": CollapsedAnswerabilityShape.STRUCTURED_REASONING,
    "timeline": CollapsedAnswerabilityShape.STRUCTURED_REASONING,
    "calculation": CollapsedAnswerabilityShape.STRUCTURED_REASONING,
}

V9_MINORITY_ANSWERABILITY_SHAPES: tuple[CollapsedAnswerabilityShape, ...] = (
    CollapsedAnswerabilityShape.SYNTHESIS_ANSWER,
    CollapsedAnswerabilityShape.SET_ANSWER,
    CollapsedAnswerabilityShape.STRUCTURED_REASONING,
)

V9_ALL_COLLAPSED_ANSWERABILITY_SHAPES: tuple[CollapsedAnswerabilityShape, ...] = (
    CollapsedAnswerabilityShape.DIRECT_ANSWER,
    *V9_MINORITY_ANSWERABILITY_SHAPES,
)


def detailed_answerability_shapes_for(
    shape: CollapsedAnswerabilityShape | str,
) -> tuple[str, ...]:
    """Return V8.2 detailed answerability labels for a V9 collapsed bucket."""

    shape = CollapsedAnswerabilityShape(shape)
    return tuple(
        detailed for detailed, collapsed in V9_ANSWERABILITY_COLLAPSE.items() if collapsed == shape
    )


def collapse_answerability_shape(kind: str) -> CollapsedAnswerabilityShape:
    """Collapse a V8.2 detailed answerability label into a V9 bucket."""

    try:
        return V9_ANSWERABILITY_COLLAPSE[kind]
    except KeyError as exc:
        raise ValueError(f"unknown answerability_shape kind {kind!r}") from exc


@dataclass(frozen=True, slots=True)
class RetrievalControlCell:
    """One V9 answerability generation cell.

    Cell ID format:
    `{governance_class_lower}__{domain}__{difficulty}__{answerability_shape}`.
    """

    governance_class: GovernanceClass
    domain: Domain
    difficulty: Difficulty
    answerability_shape: CollapsedAnswerabilityShape

    @property
    def cell_id(self) -> str:
        return _CELL_SEP.join(
            (
                self.governance_class.value.lower(),
                self.domain.value,
                self.difficulty.value,
                self.answerability_shape.value,
            )
        )

    def __str__(self) -> str:
        return self.cell_id


def parse_retrieval_control_cell_id(cell_id: str) -> RetrievalControlCell:
    """Parse a V9 retrieval-control cell ID."""

    parts = cell_id.split(_CELL_SEP)
    if len(parts) != 4:
        raise ValueError(
            "retrieval-control cell_id must be "
            f"'class{_CELL_SEP}domain{_CELL_SEP}difficulty{_CELL_SEP}shape', "
            f"got {cell_id!r}"
        )
    class_s, domain_s, difficulty_s, shape_s = parts
    try:
        return RetrievalControlCell(
            governance_class=GovernanceClass(class_s.upper()),
            domain=Domain(domain_s),
            difficulty=Difficulty(difficulty_s),
            answerability_shape=CollapsedAnswerabilityShape(shape_s),
        )
    except ValueError as exc:
        raise ValueError(f"unknown enum value in retrieval-control cell_id {cell_id!r}") from exc


def _shape_space(
    *,
    include_direct_answer: bool,
    answerability_shapes: set[CollapsedAnswerabilityShape] | None,
) -> tuple[CollapsedAnswerabilityShape, ...]:
    if answerability_shapes is not None:
        return tuple(sorted(answerability_shapes, key=lambda shape: shape.value))
    if include_direct_answer:
        return V9_ALL_COLLAPSED_ANSWERABILITY_SHAPES
    return V9_MINORITY_ANSWERABILITY_SHAPES


def all_retrieval_control_cells(
    *,
    include_direct_answer: bool = False,
    answerability_shapes: set[CollapsedAnswerabilityShape] | None = None,
    governance_classes: set[GovernanceClass] | None = None,
    domains: set[Domain] | None = None,
    difficulties: set[Difficulty] | None = None,
) -> list[RetrievalControlCell]:
    """Enumerate the V9 answerability cell space."""

    classes = governance_classes or set(GovernanceClass)
    domain_space = domains or set(PRIMARY_DOMAINS)
    difficulty_space = difficulties or set(Difficulty)
    shape_space = _shape_space(
        include_direct_answer=include_direct_answer,
        answerability_shapes=answerability_shapes,
    )
    cells = [
        RetrievalControlCell(
            governance_class=governance_class,
            domain=domain,
            difficulty=difficulty,
            answerability_shape=shape,
        )
        for shape in shape_space
        for governance_class in classes
        for domain in domain_space
        for difficulty in difficulty_space
    ]
    return sorted(cells, key=lambda cell: cell.cell_id)


@dataclass(slots=True)
class RetrievalControlCellTarget:
    """Per-cell target for V9 retrieval-control coverage."""

    default: int = 100
    overrides: dict[str, int] = field(default_factory=dict)

    def for_cell(self, cell: RetrievalControlCell | str) -> int:
        key = cell.cell_id if isinstance(cell, RetrievalControlCell) else cell
        return self.overrides.get(key, self.default)


@dataclass(slots=True)
class RetrievalControlGap:
    """One row in the V9 retrieval-control gap queue."""

    priority: float
    cell: RetrievalControlCell
    current: int
    target: int

    @property
    def gap(self) -> int:
        return max(self.target - self.current, 0)

    @property
    def coverage_ratio(self) -> float:
        return self.current / max(self.target, 1)


@dataclass(slots=True)
class RetrievalControlPriorityWeights:
    """Multiplicative priority weights for V9 retrieval-control gaps."""

    by_answerability_shape: dict[CollapsedAnswerabilityShape, float] = field(default_factory=dict)
    by_domain: dict[Domain, float] = field(default_factory=dict)
    by_difficulty: dict[Difficulty, float] = field(default_factory=dict)
    by_class: dict[GovernanceClass, float] = field(default_factory=dict)

    def weight_for(self, cell: RetrievalControlCell) -> float:
        return (
            self.by_answerability_shape.get(cell.answerability_shape, 1.0)
            * self.by_domain.get(cell.domain, 1.0)
            * self.by_difficulty.get(cell.difficulty, 1.0)
            * self.by_class.get(cell.governance_class, 1.0)
        )


@dataclass(slots=True)
class RetrievalControlCellFilter:
    """Restrict which V9 retrieval-control cells are considered."""

    answerability_shapes: set[CollapsedAnswerabilityShape] | None = None
    domains: set[Domain] | None = None
    difficulties: set[Difficulty] | None = None
    classes: set[GovernanceClass] | None = None
    include_direct_answer: bool = False

    def matches(self, cell: RetrievalControlCell) -> bool:
        if self.answerability_shapes is not None and (
            cell.answerability_shape not in self.answerability_shapes
        ):
            return False
        if not self.include_direct_answer and (
            cell.answerability_shape == CollapsedAnswerabilityShape.DIRECT_ANSWER
        ):
            return False
        if self.domains is not None and cell.domain not in self.domains:
            return False
        if self.difficulties is not None and cell.difficulty not in self.difficulties:
            return False
        if self.classes is not None and cell.governance_class not in self.classes:
            return False
        return True


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _case_governance_class(case: Mapping[str, Any]) -> GovernanceClass | None:
    raw = _dict(case.get("governance")).get("classification")
    if raw is None:
        raw = case.get("label")
    if raw is None:
        raw = _dict(case.get("taxonomy")).get("governance_class")
    if not isinstance(raw, str):
        return None
    try:
        return GovernanceClass(raw.upper())
    except ValueError:
        return None


def _case_domain(case: Mapping[str, Any]) -> Domain | None:
    raw = _dict(case.get("routing")).get("expert_fired")
    if raw is None:
        raw = case.get("route")
    if not isinstance(raw, str):
        return None
    try:
        domain = Domain(raw)
    except ValueError:
        return None
    if domain not in PRIMARY_DOMAINS:
        return None
    return domain


def _case_difficulty(case: Mapping[str, Any]) -> Difficulty | None:
    raw = _dict(case.get("meta")).get("difficulty")
    if raw is None:
        raw = case.get("difficulty")
    if not isinstance(raw, str):
        return None
    try:
        return Difficulty(raw)
    except ValueError:
        return None


def _case_answerability_shape(case: Mapping[str, Any]) -> CollapsedAnswerabilityShape | None:
    raw = case.get("answerability_shape")
    if raw is None:
        retrieval_control = _dict(_dict(case.get("routing")).get("retrieval_control"))
        raw = _dict(retrieval_control.get("answerability_shape")).get("kind")
    if not isinstance(raw, str):
        return None
    try:
        return collapse_answerability_shape(raw)
    except ValueError:
        return None


def cell_for_case(case: Mapping[str, Any]) -> RetrievalControlCell | None:
    """Return the V9 retrieval-control cell for a case, or None if incomplete."""

    governance_class = _case_governance_class(case)
    domain = _case_domain(case)
    difficulty = _case_difficulty(case)
    answerability_shape = _case_answerability_shape(case)
    if (
        governance_class is None
        or domain is None
        or difficulty is None
        or answerability_shape is None
    ):
        return None
    return RetrievalControlCell(
        governance_class=governance_class,
        domain=domain,
        difficulty=difficulty,
        answerability_shape=answerability_shape,
    )


def retrieval_control_cell_counts(cases: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    """Count V9 retrieval-control cells from canonical or flattened rows."""

    counts: dict[str, int] = {}
    for case in cases:
        cell = cell_for_case(case)
        if cell is None:
            continue
        counts[cell.cell_id] = counts.get(cell.cell_id, 0) + 1
    return counts


@dataclass(slots=True)
class RetrievalControlGapDetector:
    """Stateless V9 retrieval-control gap analyser."""

    def rank(
        self,
        cell_counts: Mapping[str, int],
        target: RetrievalControlCellTarget | int = 100,
        *,
        weights: RetrievalControlPriorityWeights | None = None,
        filter: RetrievalControlCellFilter | None = None,
    ) -> list[RetrievalControlGap]:
        if isinstance(target, int):
            target = RetrievalControlCellTarget(default=target)
        weights = weights or RetrievalControlPriorityWeights()
        flt = filter or RetrievalControlCellFilter()

        gaps: list[RetrievalControlGap] = []
        cells = all_retrieval_control_cells(
            include_direct_answer=flt.include_direct_answer,
            answerability_shapes=flt.answerability_shapes,
            governance_classes=flt.classes,
            domains=flt.domains,
            difficulties=flt.difficulties,
        )
        for cell in cells:
            if not flt.matches(cell):
                continue
            current = int(cell_counts.get(cell.cell_id, 0))
            t = target.for_cell(cell)
            if current >= t:
                continue
            gap_size = t - current
            priority = gap_size * weights.weight_for(cell)
            gaps.append(
                RetrievalControlGap(
                    priority=priority,
                    cell=cell,
                    current=current,
                    target=t,
                )
            )
        gaps.sort(key=lambda gap: (-gap.priority, gap.cell.cell_id))
        return gaps

    def coverage_summary(
        self,
        cell_counts: Mapping[str, int],
        target: RetrievalControlCellTarget | int = 100,
        *,
        filter: RetrievalControlCellFilter | None = None,
    ) -> dict[str, Any]:
        if isinstance(target, int):
            target = RetrievalControlCellTarget(default=target)
        flt = filter or RetrievalControlCellFilter()
        cells = all_retrieval_control_cells(
            include_direct_answer=flt.include_direct_answer,
            answerability_shapes=flt.answerability_shapes,
            governance_classes=flt.classes,
            domains=flt.domains,
            difficulties=flt.difficulties,
        )
        n_cells = 0
        n_at_target = 0
        n_with_some = 0
        n_empty = 0
        total_cases = 0
        total_gap = 0
        by_shape: dict[str, dict[str, int]] = {}
        for cell in cells:
            if not flt.matches(cell):
                continue
            n_cells += 1
            current = int(cell_counts.get(cell.cell_id, 0))
            t = target.for_cell(cell)
            gap = max(t - current, 0)
            total_cases += current
            total_gap += gap
            if current == 0:
                n_empty += 1
            else:
                n_with_some += 1
            if current >= t:
                n_at_target += 1
            bucket = by_shape.setdefault(
                cell.answerability_shape.value,
                {
                    "cells_considered": 0,
                    "cells_at_target": 0,
                    "cells_empty": 0,
                    "total_cases": 0,
                    "total_gap_to_fill": 0,
                },
            )
            bucket["cells_considered"] += 1
            bucket["total_cases"] += current
            bucket["total_gap_to_fill"] += gap
            if current == 0:
                bucket["cells_empty"] += 1
            if current >= t:
                bucket["cells_at_target"] += 1
        return {
            "cells_considered": n_cells,
            "cells_at_target": n_at_target,
            "cells_with_some_cases": n_with_some,
            "cells_empty": n_empty,
            "total_cases": total_cases,
            "total_gap_to_fill": total_gap,
            "by_answerability_shape": by_shape,
        }
