"""SDGP consistency checker — programmatic schema + coherence validation.

Distinct from the blind labeler. This module enforces what's mechanically
verifiable on a generated case dict before it ever reaches the second-pass
labeler:

  - **Schema**: required fields present and the right shape.
  - **Class consistency**: `taxonomy.pattern` belongs to `governance_class`,
    which matches `governance.classification`.
  - **Cell alignment**: `taxonomy.cell_id` parses, and its pattern/domain/
    difficulty agree with the row's other metadata.
  - **Pattern structure**: cheap heuristic per pattern (delegates to
    `taxonomy.check_pattern_structure` — e.g. `numerical_conflict` needs
    ≥2 digit-bearing contexts).
  - **Signal coherence**: when V6+ probability/score signals are present,
    they're internally consistent (e.g. `governance.abstain` is the largest
    when `classification == "ABSTAIN"`; `conflict_density` is high for
    DISPUTED patterns and low for TRUSTWORTHY patterns).
  - **Dedup**: optional — the checker compares a normalized hash of the
    case's `query` + `contexts` against a caller-supplied set of seen
    hashes (typically built once from the vault).

The checker is dataset-version-aware: V5.1-shaped cases (missing taxonomy /
signals / routing) produce warnings, not errors, for the fields they don't
carry. V6+ cases are held to the full standard.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Sequence

from .taxonomy import (
    PATTERN_TO_CLASS,
    Cell,
    Difficulty,
    Domain,
    GovernanceClass,
    PatternCheckResult,
    TaxonomyPattern,
    check_pattern_structure,
    parse_cell_id,
)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True, slots=True)
class CheckIssue:
    severity: Severity
    rule: str
    message: str


@dataclass(slots=True)
class CheckResult:
    case_id: str | None
    issues: list[CheckIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[CheckIssue]:
        return [i for i in self.issues if i.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[CheckIssue]:
        return [i for i in self.issues if i.severity == Severity.WARNING]

    @property
    def passed(self) -> bool:
        """A case passes the checker iff it has no errors. Warnings don't block."""
        return not self.errors

    def __bool__(self) -> bool:
        return self.passed


# ---------------------------------------------------------------------------
# Dedup hashing
# ---------------------------------------------------------------------------


_HASH_PREFIX_LEN = 240  # truncate long contexts for stable hashing


def _normalize_text(s: str) -> str:
    return " ".join(s.strip().lower().split())


def case_dedup_hash(case: dict[str, Any]) -> str:
    """Stable hash of (normalized query) + (sorted, normalized context prefixes).

    Designed to match near-duplicates that differ only in whitespace or
    ordering. Doesn't try to be a semantic dedup — that's the validator's
    job. Returns an empty string if the case lacks query + contexts.
    """
    query = _normalize_text(str(case.get("input", {}).get("query", case.get("query", ""))))
    raw_contexts: Sequence[Any] = (
        case.get("input", {}).get("contexts")
        or case.get("contexts")
        or []
    )
    norm_ctxs: list[str] = []
    for c in raw_contexts:
        if isinstance(c, dict):
            text = str(c.get("text", ""))
        else:
            text = str(c)
        norm_ctxs.append(_normalize_text(text)[:_HASH_PREFIX_LEN])
    if not query and not norm_ctxs:
        return ""
    payload = query + "||" + "##".join(sorted(norm_ctxs))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Checker
# ---------------------------------------------------------------------------


# Required top-level keys for V6+ rows. V5.1-shape rows lack `taxonomy` etc.
_V6_REQUIRED_TOP = ("id", "input", "governance", "taxonomy", "meta")

# Signals where pattern → class consistency rules apply
_DISPUTED_PATTERNS = frozenset(p for p, c in PATTERN_TO_CLASS.items() if c == GovernanceClass.DISPUTED)
_TRUSTWORTHY_PATTERNS = frozenset(p for p, c in PATTERN_TO_CLASS.items() if c == GovernanceClass.TRUSTWORTHY)
_ABSTAIN_PATTERNS = frozenset(p for p, c in PATTERN_TO_CLASS.items() if c == GovernanceClass.ABSTAIN)


@dataclass(slots=True)
class Checker:
    """Programmatic consistency checks for SDGP cases.

    Stateless — safe to share. Caller threads in `seen_hashes` for dedup.

    `pattern_structure_warning_only`: when True, structural pattern failures
    (e.g. AUTHORITY_CONFLICT needing authority-score spread) downgrade from
    errors to warnings. Use this for migrated V5.1 cases whose pattern label
    was inferred from a different taxonomy and may not match structurally
    even though the case is human-validated.
    """

    # Threshold for "imbalanced" warnings on conflict_density, etc.
    high_signal: float = 0.5
    low_signal: float = 0.3
    pattern_structure_warning_only: bool = False

    def check(
        self,
        case: dict[str, Any],
        *,
        seen_hashes: set[str] | None = None,
    ) -> CheckResult:
        result = CheckResult(case_id=_get(case, "id"))

        self._check_required_keys(case, result)
        version_v6 = self._looks_v6(case)

        self._check_classification(case, result, v6=version_v6)
        if version_v6:
            self._check_taxonomy(case, result)
            self._check_pattern_structure(case, result)
            self._check_signal_coherence(case, result)
            self._check_routing(case, result)
        self._check_contexts(case, result)
        if seen_hashes is not None:
            self._check_dedup(case, result, seen_hashes)

        return result

    def check_batch(
        self,
        cases: Iterable[dict[str, Any]],
        *,
        seen_hashes: set[str] | None = None,
    ) -> list[CheckResult]:
        """Convenience: run check() over a batch. Updates seen_hashes in-place
        as it goes so two cases in the same batch with identical content both
        get flagged (the first passes, the second errors)."""
        results: list[CheckResult] = []
        seen = set(seen_hashes) if seen_hashes is not None else set()
        for c in cases:
            r = self.check(c, seen_hashes=seen)
            results.append(r)
            h = case_dedup_hash(c)
            if h:
                seen.add(h)
        return results

    # -- Individual rules ------------------------------------------------

    def _check_required_keys(self, case: dict[str, Any], result: CheckResult) -> None:
        # `id` is always required (vault enforces too; we still warn-or-error here for visibility).
        if not isinstance(case.get("id"), str) or not case["id"]:
            result.issues.append(
                CheckIssue(Severity.ERROR, "missing_id", "case has no string `id`")
            )
        # Contexts and query are required regardless of version.
        q_v6 = case.get("input", {}).get("query")
        q_v51 = case.get("query")
        if not q_v6 and not q_v51:
            result.issues.append(
                CheckIssue(Severity.ERROR, "missing_query", "no input.query or query field")
            )

        # For V6, warn on missing top-level blocks (we'll error on the
        # specific fields downstream).
        if self._looks_v6(case):
            for key in _V6_REQUIRED_TOP:
                if key not in case:
                    result.issues.append(
                        CheckIssue(
                            Severity.ERROR,
                            "v6_missing_block",
                            f"V6 case missing top-level `{key}`",
                        )
                    )

    @staticmethod
    def _looks_v6(case: dict[str, Any]) -> bool:
        """Heuristic: any case with a `taxonomy` block is treated as V6+."""
        return isinstance(case.get("taxonomy"), dict)

    def _check_classification(self, case: dict[str, Any], result: CheckResult, *, v6: bool) -> None:
        gov = case.get("governance")
        cls_str = None
        if isinstance(gov, dict):
            cls_str = gov.get("classification")
        elif "expected_mode" in case:
            # V5.1 shape used `expected_mode` ("trustworthy" / "abstain" / "disputed")
            cls_str = str(case["expected_mode"]).upper()
        if cls_str is None:
            sev = Severity.ERROR if v6 else Severity.WARNING
            result.issues.append(
                CheckIssue(sev, "missing_classification", "no governance.classification or expected_mode")
            )
            return
        try:
            GovernanceClass(cls_str)
        except ValueError:
            result.issues.append(
                CheckIssue(
                    Severity.ERROR,
                    "invalid_classification",
                    f"classification {cls_str!r} is not one of {[c.value for c in GovernanceClass]}",
                )
            )

    def _check_taxonomy(self, case: dict[str, Any], result: CheckResult) -> None:
        tax = case.get("taxonomy", {})
        if not isinstance(tax, dict):
            result.issues.append(
                CheckIssue(Severity.ERROR, "taxonomy_not_object", "taxonomy must be an object")
            )
            return

        # Pattern present + valid?
        pattern_s = tax.get("pattern")
        try:
            pattern = TaxonomyPattern(pattern_s) if pattern_s else None
        except ValueError:
            pattern = None
            result.issues.append(
                CheckIssue(
                    Severity.ERROR,
                    "invalid_pattern",
                    f"taxonomy.pattern {pattern_s!r} is not a known TaxonomyPattern",
                )
            )
        if pattern is None and pattern_s is None:
            result.issues.append(
                CheckIssue(Severity.ERROR, "missing_pattern", "taxonomy.pattern is required")
            )

        # Class consistency: taxonomy.governance_class must match the pattern's class.
        gov_class_s = tax.get("governance_class")
        if pattern is not None and gov_class_s:
            expected_class = PATTERN_TO_CLASS[pattern]
            if gov_class_s != expected_class.value:
                result.issues.append(
                    CheckIssue(
                        Severity.ERROR,
                        "class_mismatch_taxonomy",
                        f"taxonomy.governance_class={gov_class_s!r} but pattern "
                        f"{pattern.value!r} implies {expected_class.value!r}",
                    )
                )

        # governance.classification must agree with the pattern's class.
        gov = case.get("governance", {})
        cls_s = gov.get("classification") if isinstance(gov, dict) else None
        if pattern is not None and cls_s:
            expected_class = PATTERN_TO_CLASS[pattern]
            if cls_s != expected_class.value:
                result.issues.append(
                    CheckIssue(
                        Severity.ERROR,
                        "class_mismatch_pattern",
                        f"governance.classification={cls_s!r} but pattern "
                        f"{pattern.value!r} implies {expected_class.value!r}",
                    )
                )

        # cell_id parses + agrees with pattern + difficulty + (optionally) routing.expert_fired.
        cell_id_s = tax.get("cell_id")
        if not cell_id_s:
            result.issues.append(
                CheckIssue(Severity.ERROR, "missing_cell_id", "taxonomy.cell_id is required")
            )
            return
        try:
            cell = parse_cell_id(cell_id_s)
        except ValueError as exc:
            result.issues.append(
                CheckIssue(Severity.ERROR, "invalid_cell_id", f"{cell_id_s!r}: {exc}")
            )
            return

        if pattern is not None and cell.pattern != pattern:
            result.issues.append(
                CheckIssue(
                    Severity.ERROR,
                    "cell_pattern_mismatch",
                    f"cell_id pattern {cell.pattern.value!r} != taxonomy.pattern {pattern.value!r}",
                )
            )

        meta = case.get("meta", {})
        meta_diff = meta.get("difficulty") if isinstance(meta, dict) else None
        if meta_diff is not None and meta_diff != cell.difficulty.value:
            result.issues.append(
                CheckIssue(
                    Severity.ERROR,
                    "cell_difficulty_mismatch",
                    f"cell_id difficulty {cell.difficulty.value!r} != meta.difficulty {meta_diff!r}",
                )
            )

        routing = case.get("routing", {})
        expert = routing.get("expert_fired") if isinstance(routing, dict) else None
        if expert is not None and expert != cell.domain.value:
            result.issues.append(
                CheckIssue(
                    Severity.ERROR,
                    "cell_domain_mismatch",
                    f"cell_id domain {cell.domain.value!r} != routing.expert_fired {expert!r}",
                )
            )

    def _check_pattern_structure(self, case: dict[str, Any], result: CheckResult) -> None:
        tax = case.get("taxonomy", {})
        pattern_s = tax.get("pattern") if isinstance(tax, dict) else None
        try:
            pattern = TaxonomyPattern(pattern_s) if pattern_s else None
        except ValueError:
            return  # already errored in _check_taxonomy
        if pattern is None:
            return
        struct: PatternCheckResult = check_pattern_structure(pattern, case)
        if not struct.passed:
            sev = (
                Severity.WARNING
                if self.pattern_structure_warning_only
                else Severity.ERROR
            )
            result.issues.append(CheckIssue(sev, "pattern_structure", struct.reason))

    def _check_signal_coherence(self, case: dict[str, Any], result: CheckResult) -> None:
        gov = case.get("governance", {})
        if not isinstance(gov, dict):
            return
        cls_s = gov.get("classification")
        try:
            cls = GovernanceClass(cls_s) if cls_s else None
        except ValueError:
            cls = None

        # Probabilities — if present, the predicted class's value should be the argmax.
        a = gov.get("abstain")
        d = gov.get("disputed")
        t = gov.get("trustworthy")
        if cls is not None and all(isinstance(x, (int, float)) for x in (a, d, t)):
            scores = {
                GovernanceClass.ABSTAIN: float(a),
                GovernanceClass.DISPUTED: float(d),
                GovernanceClass.TRUSTWORTHY: float(t),
            }
            argmax_cls = max(scores, key=lambda k: scores[k])
            if argmax_cls != cls:
                result.issues.append(
                    CheckIssue(
                        Severity.ERROR,
                        "argmax_mismatch",
                        f"classification={cls.value} but argmax over (a,d,t)={scores} is {argmax_cls.value}",
                    )
                )

        # Cross-signal: hallucination_pressure should track ABSTAIN/risky cases.
        hp = gov.get("hallucination_pressure")
        if cls is not None and isinstance(hp, (int, float)):
            if cls == GovernanceClass.TRUSTWORTHY and float(hp) >= self.high_signal:
                result.issues.append(
                    CheckIssue(
                        Severity.ERROR,
                        "hallucination_signal_inverted",
                        f"classification=TRUSTWORTHY but hallucination_pressure={hp:.2f} ≥ {self.high_signal}",
                    )
                )
            if cls == GovernanceClass.ABSTAIN and float(hp) < self.low_signal:
                result.issues.append(
                    CheckIssue(
                        Severity.WARNING,
                        "hallucination_signal_low_for_abstain",
                        f"classification=ABSTAIN but hallucination_pressure={hp:.2f} < {self.low_signal}",
                    )
                )

        # conflict_density: high for DISPUTED, low for TRUSTWORTHY.
        cd = gov.get("conflict_density")
        tax = case.get("taxonomy", {})
        try:
            pattern = TaxonomyPattern(tax.get("pattern")) if isinstance(tax, dict) else None
        except ValueError:
            pattern = None
        if isinstance(cd, (int, float)) and pattern is not None:
            cd_f = float(cd)
            if pattern in _DISPUTED_PATTERNS and cd_f < self.low_signal:
                result.issues.append(
                    CheckIssue(
                        Severity.ERROR,
                        "conflict_density_low_for_disputed",
                        f"DISPUTED pattern {pattern.value!r} but conflict_density={cd_f:.2f} < {self.low_signal}",
                    )
                )
            if pattern in _TRUSTWORTHY_PATTERNS and cd_f >= self.high_signal:
                result.issues.append(
                    CheckIssue(
                        Severity.ERROR,
                        "conflict_density_high_for_trustworthy",
                        f"TRUSTWORTHY pattern {pattern.value!r} but conflict_density={cd_f:.2f} ≥ {self.high_signal}",
                    )
                )

        # evidence_sufficiency: low for ABSTAIN, high for TRUSTWORTHY.
        es = gov.get("evidence_sufficiency")
        if cls is not None and isinstance(es, (int, float)):
            es_f = float(es)
            if cls == GovernanceClass.ABSTAIN and es_f >= self.high_signal:
                result.issues.append(
                    CheckIssue(
                        Severity.WARNING,
                        "evidence_sufficiency_high_for_abstain",
                        f"classification=ABSTAIN but evidence_sufficiency={es_f:.2f} ≥ {self.high_signal}",
                    )
                )
            if cls == GovernanceClass.TRUSTWORTHY and es_f < self.low_signal:
                result.issues.append(
                    CheckIssue(
                        Severity.ERROR,
                        "evidence_sufficiency_low_for_trustworthy",
                        f"classification=TRUSTWORTHY but evidence_sufficiency={es_f:.2f} < {self.low_signal}",
                    )
                )

    def _check_routing(self, case: dict[str, Any], result: CheckResult) -> None:
        routing = case.get("routing")
        if routing is None:
            result.issues.append(
                CheckIssue(Severity.WARNING, "missing_routing", "V6 case has no routing block")
            )
            return
        if not isinstance(routing, dict):
            result.issues.append(
                CheckIssue(Severity.ERROR, "routing_not_object", "routing must be an object")
            )
            return
        expert = routing.get("expert_fired")
        if expert is None:
            result.issues.append(
                CheckIssue(Severity.WARNING, "missing_expert_fired", "routing.expert_fired not set")
            )
            return
        try:
            Domain(expert)
        except ValueError:
            result.issues.append(
                CheckIssue(
                    Severity.ERROR,
                    "invalid_expert_fired",
                    f"routing.expert_fired={expert!r} is not a known Domain",
                )
            )

    def _check_contexts(self, case: dict[str, Any], result: CheckResult) -> None:
        nested = case.get("input", {}).get("contexts") if isinstance(case.get("input"), dict) else None
        flat = case.get("contexts")
        ctxs = nested if nested is not None else flat
        if ctxs is None:
            result.issues.append(
                CheckIssue(Severity.WARNING, "missing_contexts", "case has no contexts field at all")
            )
            return
        if not isinstance(ctxs, list):
            result.issues.append(
                CheckIssue(Severity.ERROR, "contexts_not_list", "contexts must be a list")
            )
            return
        for i, c in enumerate(ctxs):
            if isinstance(c, str):
                continue
            if isinstance(c, dict):
                text = c.get("text")
                if not isinstance(text, str):
                    result.issues.append(
                        CheckIssue(
                            Severity.ERROR,
                            "context_missing_text",
                            f"contexts[{i}] dict has no string `text`",
                        )
                    )
                continue
            result.issues.append(
                CheckIssue(
                    Severity.ERROR,
                    "context_bad_shape",
                    f"contexts[{i}] is neither a string nor an object: {type(c).__name__}",
                )
            )

    def _check_dedup(
        self,
        case: dict[str, Any],
        result: CheckResult,
        seen_hashes: set[str],
    ) -> None:
        h = case_dedup_hash(case)
        if not h:
            return  # empty hash means we couldn't compute one — silent skip
        if h in seen_hashes:
            result.issues.append(
                CheckIssue(
                    Severity.ERROR,
                    "duplicate_content",
                    f"case hash {h[:12]} matches a previously-seen case",
                )
            )


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------


def _get(case: dict[str, Any], key: str) -> Any:
    v = case.get(key)
    return v if isinstance(v, (str, int, float)) else None


def hashes_from(cases: Iterable[dict[str, Any]]) -> set[str]:
    """Build the seed `seen_hashes` set the checker takes for dedup,
    typically called once per pipeline run with `vault.iter_cases()`."""
    out: set[str] = set()
    for c in cases:
        h = case_dedup_hash(c)
        if h:
            out.add(h)
    return out
