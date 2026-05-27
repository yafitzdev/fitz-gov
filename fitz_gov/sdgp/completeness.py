"""Training-schema completeness checks for V7+ SDGP rows.

The structural checker answers "is this a valid cell-targeted case?" This
module answers the stricter question needed before training: "does this row
carry the full rich V6/MoE signal suite?"
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Iterable

from .modality import MODALITY_SET

MISSING = "<missing>"

GOVERNANCE_CLASSES = {"ABSTAIN", "DISPUTED", "TRUSTWORTHY"}
DATASET_VERSIONS = {"v6", "v7", "v8"}
CATEGORIES = {"abstention", "dispute", "trustworthy_hedged", "trustworthy_direct"}
CONFIDENCE_LEVELS = {"high", "medium", "borderline"}
STALENESS_RISKS = {"none", "low", "medium", "high"}


@dataclass(frozen=True, slots=True)
class CompletenessIssue:
    """One missing or malformed field in a training row."""

    path: str
    message: str


CASE_REQUIRED_PATHS: tuple[str, ...] = (
    "id",
    "version",
    "input.query",
    "input.query_rewritten",
    "governance.classification",
    "governance.abstain",
    "governance.disputed",
    "governance.trustworthy",
    "governance.confidence",
    "governance.grounding",
    "governance.conflict_density",
    "governance.evidence_sufficiency",
    "governance.boundary_proximity.nearest_class",
    "governance.boundary_proximity.distance",
    "governance.domain_familiarity",
    "governance.false_trustworthy_risk",
    "governance.hallucination_pressure",
    "governance.retrieval_retry_value",
    "governance.human_escalation_score",
    "governance.query_evidence_alignment",
    "governance.answer_coverage",
    "governance.evidence_bias_score",
    "routing.expert_fired",
    "routing.routing_confidence",
    "taxonomy.governance_class",
    "taxonomy.pattern",
    "taxonomy.pattern_description",
    "taxonomy.cell_id",
    "evaluation.mode",
    "evaluation.check_mode_match",
    "evaluation.required_elements",
    "evaluation.forbidden_claims",
    "evaluation.forbidden_elements",
    "meta.dataset_version",
    "meta.modality",
    "meta.difficulty",
    "meta.category",
    "meta.confidence_level",
    "meta.near_miss_class",
    "meta.near_miss_reason",
)


CONTEXT_REQUIRED_PATHS: tuple[str, ...] = (
    "id",
    "text",
    "authority_score",
    "authority_signal",
    "temporality.is_time_sensitive",
    "temporality.anchor_period",
    "temporality.staleness_risk",
    "summary",
    "relevance_to_query",
    "boundary_quality",
)


CASE_SCORE_PATHS = {
    "governance.abstain",
    "governance.disputed",
    "governance.trustworthy",
    "governance.confidence",
    "governance.grounding",
    "governance.conflict_density",
    "governance.evidence_sufficiency",
    "governance.boundary_proximity.distance",
    "governance.domain_familiarity",
    "governance.false_trustworthy_risk",
    "governance.hallucination_pressure",
    "governance.retrieval_retry_value",
    "governance.human_escalation_score",
    "governance.query_evidence_alignment",
    "governance.answer_coverage",
    "governance.evidence_bias_score",
    "routing.routing_confidence",
}

CONTEXT_SCORE_PATHS = {"authority_score", "relevance_to_query", "boundary_quality"}


def get_path(obj: dict[str, Any], path: str) -> Any:
    """Return a nested value by dotted path, or MISSING."""
    cur: Any = obj
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return MISSING
        cur = cur[part]
    return cur


def _missing_value(value: Any) -> bool:
    if value is MISSING or value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if value == "<TODO_LLM>":
        return True
    return False


def _add_path_issue(
    issues: list[CompletenessIssue],
    obj: dict[str, Any],
    path: str,
) -> None:
    value = get_path(obj, path)
    if _missing_value(value):
        issues.append(CompletenessIssue(path, f"{path} is missing or empty"))


def _add_score_issue(issues: list[CompletenessIssue], path: str, value: Any) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        issues.append(CompletenessIssue(path, f"{path} must be numeric 0.0-1.0"))
        return
    if not 0.0 <= float(value) <= 1.0:
        issues.append(CompletenessIssue(path, f"{path} must be in [0.0, 1.0]"))


def _add_enum_issue(
    issues: list[CompletenessIssue],
    path: str,
    value: Any,
    allowed: set[str],
) -> None:
    if value not in allowed:
        issues.append(
            CompletenessIssue(
                path,
                f"{path} must be one of {sorted(allowed)}, got {value!r}",
            )
        )


def audit_case_completeness(case: dict[str, Any]) -> list[CompletenessIssue]:
    """Return missing/malformed fields for a V7+ training row.

    Conditional rules:
    - `input.evidence_chain` is required only for multi-context cases.
    - `meta.grounding_targets` is required only for TRUSTWORTHY cases.
    """
    issues: list[CompletenessIssue] = []

    for path in CASE_REQUIRED_PATHS:
        _add_path_issue(issues, case, path)

    for path in CASE_SCORE_PATHS:
        value = get_path(case, path)
        if not _missing_value(value):
            _add_score_issue(issues, path, value)

    actual_class = get_path(case, "governance.classification")
    for path in ("governance.classification", "taxonomy.governance_class"):
        value = get_path(case, path)
        if not _missing_value(value):
            _add_enum_issue(issues, path, value, GOVERNANCE_CLASSES)
    for path in ("governance.boundary_proximity.nearest_class", "meta.near_miss_class"):
        value = get_path(case, path)
        if not _missing_value(value):
            _add_enum_issue(issues, path, value, GOVERNANCE_CLASSES)
            if value == actual_class:
                issues.append(CompletenessIssue(path, f"{path} must differ from actual class"))

    enum_checks = {
        "meta.dataset_version": DATASET_VERSIONS,
        "meta.modality": MODALITY_SET,
        "meta.category": CATEGORIES,
        "meta.confidence_level": CONFIDENCE_LEVELS,
    }
    for path, allowed in enum_checks.items():
        value = get_path(case, path)
        if not _missing_value(value):
            _add_enum_issue(issues, path, value, allowed)

    contexts = get_path(case, "input.contexts")
    if not isinstance(contexts, list) or not contexts:
        issues.append(
            CompletenessIssue("input.contexts", "input.contexts must be a non-empty list")
        )
        contexts = []

    for idx, context in enumerate(contexts):
        if not isinstance(context, dict):
            issues.append(
                CompletenessIssue(
                    f"input.contexts[{idx}]",
                    f"context must be an object, got {type(context).__name__}",
                )
            )
            continue
        for rel_path in CONTEXT_REQUIRED_PATHS:
            value = get_path(context, rel_path)
            if _missing_value(value):
                issues.append(
                    CompletenessIssue(
                        f"input.contexts[{idx}].{rel_path}",
                        f"context field {rel_path} is missing or empty",
                    )
                )
            elif rel_path in CONTEXT_SCORE_PATHS:
                _add_score_issue(issues, f"input.contexts[{idx}].{rel_path}", value)
            elif rel_path == "temporality.is_time_sensitive" and not isinstance(value, bool):
                issues.append(
                    CompletenessIssue(
                        f"input.contexts[{idx}].{rel_path}",
                        "temporality.is_time_sensitive must be boolean",
                    )
                )
            elif rel_path == "temporality.staleness_risk":
                _add_enum_issue(
                    issues,
                    f"input.contexts[{idx}].{rel_path}",
                    value,
                    STALENESS_RISKS,
                )

    if len(contexts) >= 2:
        chain = get_path(case, "input.evidence_chain")
        if not isinstance(chain, dict):
            issues.append(
                CompletenessIssue(
                    "input.evidence_chain",
                    "multi-context cases require input.evidence_chain",
                )
            )
        else:
            order = chain.get("order")
            reasoning = chain.get("reasoning")
            if not isinstance(order, list) or not order:
                issues.append(
                    CompletenessIssue(
                        "input.evidence_chain.order",
                        "evidence_chain.order must be a non-empty list",
                    )
                )
            else:
                valid_ids = {
                    c.get("id")
                    for c in contexts
                    if isinstance(c, dict) and isinstance(c.get("id"), str)
                }
                bad_ids = [x for x in order if x not in valid_ids]
                if bad_ids:
                    issues.append(
                        CompletenessIssue(
                            "input.evidence_chain.order",
                            f"evidence_chain.order has unknown chunk ids: {bad_ids}",
                        )
                    )
            if _missing_value(reasoning):
                issues.append(
                    CompletenessIssue(
                        "input.evidence_chain.reasoning",
                        "evidence_chain.reasoning is missing or empty",
                    )
                )

    if get_path(case, "governance.classification") == "TRUSTWORTHY":
        targets = get_path(case, "meta.grounding_targets")
        if not isinstance(targets, dict):
            issues.append(
                CompletenessIssue(
                    "meta.grounding_targets",
                    "TRUSTWORTHY cases require meta.grounding_targets",
                )
            )
        else:
            if _missing_value(targets.get("gold_answer")):
                issues.append(
                    CompletenessIssue(
                        "meta.grounding_targets.gold_answer",
                        "grounding_targets.gold_answer is missing or empty",
                    )
                )
            sentences = targets.get("sentences")
            if not isinstance(sentences, list) or not sentences:
                issues.append(
                    CompletenessIssue(
                        "meta.grounding_targets.sentences",
                        "grounding_targets.sentences must be a non-empty list",
                    )
                )
            else:
                valid_ids = {
                    c.get("id")
                    for c in contexts
                    if isinstance(c, dict) and isinstance(c.get("id"), str)
                }
                for idx, sentence in enumerate(sentences):
                    if not isinstance(sentence, dict):
                        issues.append(
                            CompletenessIssue(
                                f"meta.grounding_targets.sentences[{idx}]",
                                "grounding target sentence must be an object",
                            )
                        )
                        continue
                    if _missing_value(sentence.get("text")):
                        issues.append(
                            CompletenessIssue(
                                f"meta.grounding_targets.sentences[{idx}].text",
                                "grounding target sentence text is missing",
                            )
                        )
                    attrs = sentence.get("attributions")
                    if not isinstance(attrs, list):
                        issues.append(
                            CompletenessIssue(
                                f"meta.grounding_targets.sentences[{idx}].attributions",
                                "attributions must be a list",
                            )
                        )
                    else:
                        bad_attrs = [a for a in attrs if a not in valid_ids]
                        if bad_attrs:
                            issues.append(
                                CompletenessIssue(
                                    f"meta.grounding_targets.sentences[{idx}].attributions",
                                    f"unknown attribution chunk ids: {bad_attrs}",
                                )
                            )

    return issues


def is_training_complete(case: dict[str, Any]) -> bool:
    """True when `audit_case_completeness` finds no issues."""
    return not audit_case_completeness(case)


def cases_needing_training_completion(cases: Iterable[dict[str, Any]]) -> list[str]:
    """Return ids for cases missing one or more training-schema fields."""
    return [str(case["id"]) for case in cases if "id" in case and audit_case_completeness(case)]


def summarize_completeness(cases: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate training-schema completeness by dataset cohort and field path."""
    by_cohort: dict[str, Counter[str]] = defaultdict(Counter)
    totals: Counter[str] = Counter()
    complete: Counter[str] = Counter()
    issue_paths: dict[str, Counter[str]] = defaultdict(Counter)

    for case in cases:
        meta = case.get("meta") if isinstance(case.get("meta"), dict) else {}
        cohort = str(meta.get("dataset_version") or "unknown")
        totals[cohort] += 1
        issues = audit_case_completeness(case)
        if not issues:
            complete[cohort] += 1
        by_cohort[cohort]["issues"] += len(issues)
        for issue in issues:
            issue_paths[cohort][issue.path] += 1

    return {
        "totals": dict(totals),
        "complete": dict(complete),
        "issue_counts": {k: dict(v) for k, v in by_cohort.items()},
        "missing_by_path": {k: dict(v) for k, v in issue_paths.items()},
    }
