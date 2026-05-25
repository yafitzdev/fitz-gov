"""SDGP taxonomy — canonical patterns and cell spaces.

The skeleton everything else hangs on. Three governance classes, primary
evidence patterns, all enumerated. Cells are `(pattern, domain, difficulty)`
triples that uniquely identify a generation slot; the distribution monitor
tracks coverage per cell, the gap detector reads the count vector, the
generator is prompted with the cell spec.

V8 expands the primary pattern enum for cross-domain taxonomy gaps while
keeping the public row shape unchanged. There is no compatibility/subpattern
shim layer.

See pyrrho ROADMAP.md §3 "Case Taxonomy" for the rationale.

This module is intentionally heavy on enums and light on logic. The structural
checks `check_pattern_structure(pattern, case)` are cheap heuristics designed
to catch obvious shape/schema failures (e.g. `numerical_conflict` requires
≥2 contexts) before the blind labeler runs. They are NOT a replacement for
semantic validation — they only enforce what's mechanically verifiable.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable


# ---------------------------------------------------------------------------
# Governance classes + difficulty levels
# ---------------------------------------------------------------------------


class GovernanceClass(str, Enum):
    """The three governance verdicts a pyrrho model emits."""

    ABSTAIN = "ABSTAIN"
    DISPUTED = "DISPUTED"
    TRUSTWORTHY = "TRUSTWORTHY"


class Difficulty(str, Enum):
    """Per-case difficulty rating. Matched against generator prompt complexity."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# ---------------------------------------------------------------------------
# Domains (MoE expert domains)
# ---------------------------------------------------------------------------


class Domain(str, Enum):
    """The seven primary expert domains + the meta-expert `conflict_detection`.

    `conflict_detection` is a reasoning-pattern expert (per ROADMAP §5), not
    a subject-matter domain — it can fire as a secondary expert alongside any
    primary. By default `all_cells()` excludes it from the cell enumeration
    because it's not a generation target.
    """

    SCIENCE_MEDICINE = "science_medicine"
    LAW_POLICY = "law_policy"
    HISTORY_GEOGRAPHY = "history_geography"
    TECHNOLOGY_COMPUTING = "technology_computing"
    ECONOMICS_FINANCE = "economics_finance"
    CULTURE_SOCIETY = "culture_society"
    GENERAL_COMMONSENSE = "general_commonsense"
    CONFLICT_DETECTION = "conflict_detection"


PRIMARY_DOMAINS: tuple[Domain, ...] = tuple(
    d for d in Domain if d != Domain.CONFLICT_DETECTION
)


# ---------------------------------------------------------------------------
# Taxonomy patterns
# ---------------------------------------------------------------------------


class TaxonomyPattern(str, Enum):
    """The canonical evidence patterns.

    See ROADMAP.md §3 for the design tables. Each pattern maps deterministically
    to a single governance class via `PATTERN_TO_CLASS`.
    """

    # ABSTAIN patterns
    WRONG_SPECIFICITY = "wrong_specificity"
    WRONG_ENTITY = "wrong_entity"
    PARTIAL_OVERLAP = "partial_overlap"
    EVIDENCE_ABSENT = "evidence_absent"
    TOO_GENERAL = "too_general"
    TEMPORAL_MISMATCH = "temporal_mismatch"
    VERSION_BUILD_MISMATCH = "version_build_mismatch"
    MISSING_EXECUTION_RESULT = "missing_execution_result"

    # DISPUTED patterns
    NUMERICAL_CONFLICT = "numerical_conflict"
    TEMPORAL_CONFLICT = "temporal_conflict"
    DEFINITIONAL_CONFLICT = "definitional_conflict"
    FACTUAL_CONTRADICTION = "factual_contradiction"
    AUTHORITY_CONFLICT = "authority_conflict"
    SCOPE_CONFLICT = "scope_conflict"
    VERDICT_CONFLICT = "verdict_conflict"
    AUTHORITY_STATUS_CONFLICT = "authority_status_conflict"

    # TRUSTWORTHY patterns
    MULTI_SOURCE_CORROBORATION = "multi_source_corroboration"
    SINGLE_AUTHORITATIVE = "single_authoritative"
    CONSISTENT_CHAIN = "consistent_chain"
    QUANTITATIVE_CONSENSUS = "quantitative_consensus"
    EXPERT_CONSENSUS = "expert_consensus"
    DIRECT_ANSWER = "direct_answer"
    RESOLVED_CANDIDATE_SELECTION = "resolved_candidate_selection"


PATTERN_TO_CLASS: dict[TaxonomyPattern, GovernanceClass] = {
    # ABSTAIN
    TaxonomyPattern.WRONG_SPECIFICITY: GovernanceClass.ABSTAIN,
    TaxonomyPattern.WRONG_ENTITY: GovernanceClass.ABSTAIN,
    TaxonomyPattern.PARTIAL_OVERLAP: GovernanceClass.ABSTAIN,
    TaxonomyPattern.EVIDENCE_ABSENT: GovernanceClass.ABSTAIN,
    TaxonomyPattern.TOO_GENERAL: GovernanceClass.ABSTAIN,
    TaxonomyPattern.TEMPORAL_MISMATCH: GovernanceClass.ABSTAIN,
    TaxonomyPattern.VERSION_BUILD_MISMATCH: GovernanceClass.ABSTAIN,
    TaxonomyPattern.MISSING_EXECUTION_RESULT: GovernanceClass.ABSTAIN,
    # DISPUTED
    TaxonomyPattern.NUMERICAL_CONFLICT: GovernanceClass.DISPUTED,
    TaxonomyPattern.TEMPORAL_CONFLICT: GovernanceClass.DISPUTED,
    TaxonomyPattern.DEFINITIONAL_CONFLICT: GovernanceClass.DISPUTED,
    TaxonomyPattern.FACTUAL_CONTRADICTION: GovernanceClass.DISPUTED,
    TaxonomyPattern.AUTHORITY_CONFLICT: GovernanceClass.DISPUTED,
    TaxonomyPattern.SCOPE_CONFLICT: GovernanceClass.DISPUTED,
    TaxonomyPattern.VERDICT_CONFLICT: GovernanceClass.DISPUTED,
    TaxonomyPattern.AUTHORITY_STATUS_CONFLICT: GovernanceClass.DISPUTED,
    # TRUSTWORTHY
    TaxonomyPattern.MULTI_SOURCE_CORROBORATION: GovernanceClass.TRUSTWORTHY,
    TaxonomyPattern.SINGLE_AUTHORITATIVE: GovernanceClass.TRUSTWORTHY,
    TaxonomyPattern.CONSISTENT_CHAIN: GovernanceClass.TRUSTWORTHY,
    TaxonomyPattern.QUANTITATIVE_CONSENSUS: GovernanceClass.TRUSTWORTHY,
    TaxonomyPattern.EXPERT_CONSENSUS: GovernanceClass.TRUSTWORTHY,
    TaxonomyPattern.DIRECT_ANSWER: GovernanceClass.TRUSTWORTHY,
    TaxonomyPattern.RESOLVED_CANDIDATE_SELECTION: GovernanceClass.TRUSTWORTHY,
}


PATTERN_DESCRIPTIONS: dict[TaxonomyPattern, str] = {
    # ABSTAIN
    TaxonomyPattern.WRONG_SPECIFICITY: "Right entity, wrong aspect or sub-topic",
    TaxonomyPattern.WRONG_ENTITY: "Evidence covers a different entity entirely",
    TaxonomyPattern.PARTIAL_OVERLAP: "Evidence touches the topic but cannot answer the specific question",
    TaxonomyPattern.EVIDENCE_ABSENT: "Nothing retrieved is remotely relevant",
    TaxonomyPattern.TOO_GENERAL: "Evidence is true but too broad to answer the specific query",
    TaxonomyPattern.TEMPORAL_MISMATCH: "Evidence exists but is anchored to the wrong time period",
    TaxonomyPattern.VERSION_BUILD_MISMATCH: "Evidence covers the right family but the wrong concrete version, build, release, platform, jurisdiction, cohort, or period",
    TaxonomyPattern.MISSING_EXECUTION_RESULT: "Evidence provides setup, plan, protocol, or traceability but omits the requested final result",
    # DISPUTED
    TaxonomyPattern.NUMERICAL_CONFLICT: "Multiple sources provide different numerical values for the same entity and attribute",
    TaxonomyPattern.TEMPORAL_CONFLICT: "Sources describe different states at different times presented without temporal framing",
    TaxonomyPattern.DEFINITIONAL_CONFLICT: "Sources disagree on what something IS",
    TaxonomyPattern.FACTUAL_CONTRADICTION: "Direct logical incompatibility between sources",
    TaxonomyPattern.AUTHORITY_CONFLICT: "One high-authority source contradicts one low-authority source",
    TaxonomyPattern.SCOPE_CONFLICT: "Sources are both correct but apply to different scopes presented as equivalent",
    TaxonomyPattern.VERDICT_CONFLICT: "Sources give incompatible final verdicts or statuses for the same entity, scope, and check",
    TaxonomyPattern.AUTHORITY_STATUS_CONFLICT: "A lower-authority or intermediate status conflicts with the source of record or governing authority",
    # TRUSTWORTHY
    TaxonomyPattern.MULTI_SOURCE_CORROBORATION: "Multiple independent sources agree on the same claim",
    TaxonomyPattern.SINGLE_AUTHORITATIVE: "One high-authority source, no contradictions, directly answers query",
    TaxonomyPattern.CONSISTENT_CHAIN: "Multiple chunks from same or related sources form a coherent evidence chain",
    TaxonomyPattern.QUANTITATIVE_CONSENSUS: "Multiple sources provide same or consistent numerical values",
    TaxonomyPattern.EXPERT_CONSENSUS: "Multiple domain-expert sources converge on same conclusion",
    TaxonomyPattern.DIRECT_ANSWER: "Single chunk directly and completely answers the query with no ambiguity",
    TaxonomyPattern.RESOLVED_CANDIDATE_SELECTION: "Evidence includes apparent candidate alternatives, but sources explicitly identify the valid answer and invalidate the others",
}


# Sanity: every pattern has a class + description.
assert set(PATTERN_TO_CLASS.keys()) == set(TaxonomyPattern)
assert set(PATTERN_DESCRIPTIONS.keys()) == set(TaxonomyPattern)


V8_GAP_PATTERNS: tuple[TaxonomyPattern, ...] = (
    TaxonomyPattern.RESOLVED_CANDIDATE_SELECTION,
    TaxonomyPattern.VERDICT_CONFLICT,
    TaxonomyPattern.AUTHORITY_STATUS_CONFLICT,
    TaxonomyPattern.VERSION_BUILD_MISMATCH,
    TaxonomyPattern.MISSING_EXECUTION_RESULT,
)


def patterns_of(cls: GovernanceClass) -> tuple[TaxonomyPattern, ...]:
    """All patterns belonging to a governance class."""
    return tuple(p for p, c in PATTERN_TO_CLASS.items() if c == cls)


def governance_class_of(pattern: TaxonomyPattern) -> GovernanceClass:
    """Inverse of `patterns_of` — the governance class implied by a pattern."""
    return PATTERN_TO_CLASS[pattern]


# ---------------------------------------------------------------------------
# Cells — the 3D coordinate that identifies a generation slot
# ---------------------------------------------------------------------------


_CELL_SEP = "__"


@dataclass(frozen=True, slots=True)
class Cell:
    """A single (pattern, domain, difficulty) cell.

    `cell_id` is the canonical string form used in storage, prompts, and the
    distribution monitor. Format: `{pattern}__{domain}__{difficulty}`.
    """

    pattern: TaxonomyPattern
    domain: Domain
    difficulty: Difficulty

    @property
    def cell_id(self) -> str:
        return f"{self.pattern.value}{_CELL_SEP}{self.domain.value}{_CELL_SEP}{self.difficulty.value}"

    @property
    def governance_class(self) -> GovernanceClass:
        return governance_class_of(self.pattern)

    def __str__(self) -> str:
        return self.cell_id


def parse_cell_id(s: str) -> Cell:
    """Inverse of `Cell.cell_id`. Raises ValueError on a malformed id."""
    parts = s.split(_CELL_SEP)
    if len(parts) != 3:
        raise ValueError(
            f"cell_id must be 'pattern{_CELL_SEP}domain{_CELL_SEP}difficulty', got {s!r}"
        )
    pattern_s, domain_s, difficulty_s = parts
    try:
        return Cell(
            pattern=TaxonomyPattern(pattern_s),
            domain=Domain(domain_s),
            difficulty=Difficulty(difficulty_s),
        )
    except ValueError as exc:
        raise ValueError(f"unknown enum value in cell_id {s!r}: {exc}") from exc


def all_cells(*, include_meta_domain: bool = False) -> list[Cell]:
    """Enumerate the cell space.

    V7 contained 18 patterns. V8 adds five primary patterns for taxonomy gaps,
    so default V8 enumeration is 23 patterns × 7 primary domains × 3
    difficulties = **483 cells**.

    With `include_meta_domain=True`: 23 × 8 × 3 = **552 cells**. The extra
    `conflict_detection` domain is a meta-expert routing target, not a normal
    subject-matter generation target.
    """
    domains = list(Domain) if include_meta_domain else list(PRIMARY_DOMAINS)
    return [
        Cell(pattern=p, domain=d, difficulty=diff)
        for p in TaxonomyPattern
        for d in domains
        for diff in Difficulty
    ]


# ---------------------------------------------------------------------------
# Structural pattern checks
# ---------------------------------------------------------------------------
#
# Cheap heuristic validators. Each takes a case dict (V6+ shape per ROADMAP §3)
# and returns whether the case structurally exhibits its claimed pattern.
# These are NOT semantic checks — they enforce minimum-context counts, presence
# of digit-bearing claims, authority-signal mix, etc. Semantic validation
# (does the wording actually instantiate the pattern?) is the blind labeler's
# job, not this module's.


@dataclass(frozen=True, slots=True)
class PatternCheckResult:
    """Outcome of a structural pattern check."""

    passed: bool
    reason: str

    def __bool__(self) -> bool:
        return self.passed


# Minimum number of contexts a pattern requires.
PATTERN_MIN_CONTEXTS: dict[TaxonomyPattern, int] = {
    # Patterns that require multi-source comparison need ≥2 contexts.
    TaxonomyPattern.NUMERICAL_CONFLICT: 2,
    TaxonomyPattern.TEMPORAL_CONFLICT: 2,
    TaxonomyPattern.DEFINITIONAL_CONFLICT: 2,
    TaxonomyPattern.FACTUAL_CONTRADICTION: 2,
    TaxonomyPattern.AUTHORITY_CONFLICT: 2,
    TaxonomyPattern.SCOPE_CONFLICT: 2,
    TaxonomyPattern.MULTI_SOURCE_CORROBORATION: 2,
    TaxonomyPattern.CONSISTENT_CHAIN: 2,
    TaxonomyPattern.QUANTITATIVE_CONSENSUS: 2,
    TaxonomyPattern.EXPERT_CONSENSUS: 2,
    # Single-source patterns: not strict, but conceptually a single chunk.
    TaxonomyPattern.SINGLE_AUTHORITATIVE: 1,
    TaxonomyPattern.DIRECT_ANSWER: 1,
    # ABSTAIN patterns: the count itself isn't diagnostic.
    TaxonomyPattern.WRONG_SPECIFICITY: 1,
    TaxonomyPattern.WRONG_ENTITY: 1,
    TaxonomyPattern.PARTIAL_OVERLAP: 1,
    TaxonomyPattern.EVIDENCE_ABSENT: 0,  # may legitimately have zero contexts
    TaxonomyPattern.TOO_GENERAL: 1,
    TaxonomyPattern.TEMPORAL_MISMATCH: 1,
    TaxonomyPattern.VERSION_BUILD_MISMATCH: 1,
    TaxonomyPattern.MISSING_EXECUTION_RESULT: 1,
    TaxonomyPattern.VERDICT_CONFLICT: 2,
    TaxonomyPattern.AUTHORITY_STATUS_CONFLICT: 2,
    TaxonomyPattern.RESOLVED_CANDIDATE_SELECTION: 2,
}


def _extract_context_texts(case: dict[str, Any]) -> list[str]:
    """Pull plain-text bodies from either the V5.1 (flat `contexts: [str]`)
    or V6+ (nested `input.contexts: [{text, ...}]`) schema. Returns []."""
    nested = case.get("input", {}).get("contexts")
    if nested is None:
        nested = case.get("contexts")
    if not nested:
        return []
    out: list[str] = []
    for c in nested:
        if isinstance(c, str):
            out.append(c)
        elif isinstance(c, dict):
            out.append(str(c.get("text", "")))
    return out


def _extract_context_dicts(case: dict[str, Any]) -> list[dict[str, Any]]:
    """V6+ contexts as dicts. Empty list for V5.1 flat shape."""
    nested = case.get("input", {}).get("contexts") or case.get("contexts")
    if not nested:
        return []
    return [c for c in nested if isinstance(c, dict)]


def _has_min_contexts(case: dict[str, Any], n: int) -> tuple[bool, int]:
    texts = _extract_context_texts(case)
    return (len(texts) >= n, len(texts))


def _count_digit_bearing(texts: list[str]) -> int:
    """Heuristic: how many context texts contain at least one digit."""
    return sum(1 for t in texts if any(ch.isdigit() for ch in t))


def _authority_scores(contexts: list[dict[str, Any]]) -> list[float]:
    """V6+ per-chunk authority_score values. Returns [] if not present."""
    out: list[float] = []
    for c in contexts:
        score = c.get("authority_score")
        if isinstance(score, (int, float)):
            out.append(float(score))
    return out


def _check_min_count(pattern: TaxonomyPattern, case: dict[str, Any]) -> PatternCheckResult:
    """Default check: enforce PATTERN_MIN_CONTEXTS."""
    n = PATTERN_MIN_CONTEXTS.get(pattern, 0)
    if n == 0:
        return PatternCheckResult(True, "no min-context constraint")
    ok, got = _has_min_contexts(case, n)
    if ok:
        return PatternCheckResult(True, f"≥{n} contexts (got {got})")
    return PatternCheckResult(False, f"{pattern.value} requires ≥{n} contexts, got {got}")


def _check_numerical_conflict(case: dict[str, Any]) -> PatternCheckResult:
    base = _check_min_count(TaxonomyPattern.NUMERICAL_CONFLICT, case)
    if not base:
        return base
    texts = _extract_context_texts(case)
    if _count_digit_bearing(texts) < 2:
        return PatternCheckResult(
            False,
            "numerical_conflict needs digit-bearing values in ≥2 contexts",
        )
    return PatternCheckResult(True, "ok (≥2 contexts, ≥2 digit-bearing)")


def _check_quantitative_consensus(case: dict[str, Any]) -> PatternCheckResult:
    base = _check_min_count(TaxonomyPattern.QUANTITATIVE_CONSENSUS, case)
    if not base:
        return base
    texts = _extract_context_texts(case)
    if _count_digit_bearing(texts) < 2:
        return PatternCheckResult(
            False,
            "quantitative_consensus needs numeric values in ≥2 contexts",
        )
    return PatternCheckResult(True, "ok (≥2 contexts, ≥2 digit-bearing)")


def _check_authority_conflict(case: dict[str, Any]) -> PatternCheckResult:
    base = _check_min_count(TaxonomyPattern.AUTHORITY_CONFLICT, case)
    if not base:
        return base
    ctxs = _extract_context_dicts(case)
    scores = _authority_scores(ctxs)
    if len(scores) < 2:
        # V5.1 cases without authority_score get a pass — schema-not-enforced
        return PatternCheckResult(True, "no authority_score fields (V5.1-shape)")
    if max(scores) - min(scores) < 0.2:
        return PatternCheckResult(
            False,
            f"authority_conflict expects spread in authority_score; got {scores!r}",
        )
    return PatternCheckResult(True, f"authority spread ok ({min(scores)}..{max(scores)})")


def _check_expert_consensus(case: dict[str, Any]) -> PatternCheckResult:
    base = _check_min_count(TaxonomyPattern.EXPERT_CONSENSUS, case)
    if not base:
        return base
    ctxs = _extract_context_dicts(case)
    scores = _authority_scores(ctxs)
    if len(scores) < 2:
        return PatternCheckResult(True, "no authority_score fields (V5.1-shape)")
    if min(scores) < 0.6:
        return PatternCheckResult(
            False,
            f"expert_consensus expects all authority_score ≥ 0.6; got min={min(scores)}",
        )
    return PatternCheckResult(True, f"all authority ≥ 0.6 (min={min(scores)})")


# Dispatch table. Patterns not listed here fall back to `_check_min_count`.
_PATTERN_CHECKS: dict[TaxonomyPattern, Callable[[dict[str, Any]], PatternCheckResult]] = {
    TaxonomyPattern.NUMERICAL_CONFLICT: _check_numerical_conflict,
    TaxonomyPattern.QUANTITATIVE_CONSENSUS: _check_quantitative_consensus,
    TaxonomyPattern.AUTHORITY_CONFLICT: _check_authority_conflict,
    TaxonomyPattern.EXPERT_CONSENSUS: _check_expert_consensus,
}


def check_pattern_structure(
    pattern: TaxonomyPattern, case: dict[str, Any]
) -> PatternCheckResult:
    """Run the structural check for `pattern` on `case`.

    Returns OK for any pattern whose check isn't specialised — that just means
    we don't have a cheap mechanical test and the blind labeler decides.
    """
    specialised = _PATTERN_CHECKS.get(pattern)
    if specialised is not None:
        return specialised(case)
    return _check_min_count(pattern, case)
