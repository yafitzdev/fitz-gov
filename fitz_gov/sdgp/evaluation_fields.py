"""Canonical evaluation-field promotion for SDGP V6+ rows.

The V5.1 evaluator carried several flat fields (`evaluation_config`,
`required_elements`, `forbidden_claims`, `forbidden_elements`) that were
preserved under `meta.v51_legacy` during V6 enrichment. V7 rows use the richer
governance/MoE schema and generally lack those flat evaluator fields.

This module defines the V7+ canonical home for the still-useful evaluator
signals:

    case["evaluation"] = {
        "mode": "governance",
        "check_mode_match": true,
        "required_elements": [...],
        "forbidden_claims": [...],
        "forbidden_elements": [...]
    }

Everything else from `meta.v51_legacy` is either provenance, duplicated by
V6/MoE fields, or derivable from the case itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping


DEFAULT_EVALUATION_MODE = "governance"

LEGACY_FIELD_NAMES = (
    "description",
    "rationale",
    "evaluation_config",
    "forbidden_claims",
    "required_elements",
    "forbidden_elements",
    "detection_labels",
    "context_sources",
    "metadata",
    "original_id",
    "original_subcategory",
    "original_category",
    "original_expected_mode",
    "relabel_reason",
)

ROOT_ALIAS_FIELDS = (
    "evaluation_config",
    "forbidden_claims",
    "required_elements",
    "forbidden_elements",
    "detection_labels",
    "conflict_density",
    "evidence_sufficiency",
    "near_miss_class",
)

META_ALIAS_FIELDS = (
    "annotator_agreement",
    "context_count",
    "evidence_pattern",
    "source_type",
    "jurisdiction",
    "source",
)

GOVERNANCE_ALIAS_FIELDS = (
    "abstain_score",
    "disputed_score",
    "trustworthy_score",
    "grounding_targets",
)


@dataclass(frozen=True, slots=True)
class EvaluationIssue:
    path: str
    message: str


@dataclass(slots=True)
class EvaluationPromotionResult:
    case_id: str
    changed_paths: list[str] = field(default_factory=list)
    stripped_paths: list[str] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return bool(self.changed_paths or self.stripped_paths)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _legacy(case: Mapping[str, Any]) -> Mapping[str, Any]:
    meta = _as_mapping(case.get("meta"))
    return _as_mapping(meta.get("v51_legacy"))


def _list_str(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            continue
        text = item.strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _first_list(*values: Any) -> list[str]:
    for value in values:
        items = _list_str(value)
        if items:
            return items
    return []


def _evaluation_source(case: Mapping[str, Any]) -> Mapping[str, Any]:
    return _as_mapping(case.get("evaluation"))


def _config_source(case: Mapping[str, Any]) -> Mapping[str, Any]:
    eval_block = _evaluation_source(case)
    legacy = _legacy(case)
    for value in (
        eval_block.get("config"),
        case.get("evaluation_config"),
        legacy.get("evaluation_config"),
    ):
        if isinstance(value, Mapping):
            return value
    return {}


def build_canonical_evaluation(case: Mapping[str, Any]) -> dict[str, Any]:
    """Return the canonical evaluation block for a case.

    Existing canonical values win, then flat root values, then V5.1 legacy
    values. Missing config defaults to governance-mode matching.
    """
    existing = _evaluation_source(case)
    legacy = _legacy(case)
    config = _config_source(case)

    mode = existing.get("mode") or config.get("mode") or DEFAULT_EVALUATION_MODE
    check_mode_match = existing.get("check_mode_match")
    if check_mode_match is None:
        check_mode_match = config.get("check_mode_match", True)

    out: dict[str, Any] = {
        "mode": str(mode or DEFAULT_EVALUATION_MODE),
        "check_mode_match": bool(check_mode_match),
        "required_elements": _first_list(
            existing.get("required_elements"),
            case.get("required_elements"),
            legacy.get("required_elements"),
        ),
        "forbidden_claims": _first_list(
            existing.get("forbidden_claims"),
            case.get("forbidden_claims"),
            legacy.get("forbidden_claims"),
        ),
        "forbidden_elements": _first_list(
            existing.get("forbidden_elements"),
            case.get("forbidden_elements"),
            legacy.get("forbidden_elements"),
        ),
    }

    passthrough_config = {
        k: v for k, v in config.items() if k not in {"mode", "check_mode_match"}
    }
    if passthrough_config:
        out["config"] = dict(sorted(passthrough_config.items()))
    return out


def audit_evaluation_fields(
    case: Mapping[str, Any],
    *,
    require_quality_lists: bool = False,
) -> list[EvaluationIssue]:
    """Return canonical evaluation-field issues.

    `require_quality_lists=True` is used for the enrichment pass: trustworthy
    cases should have at least one answer-quality constraint, not just the
    governance mode check.
    """
    issues: list[EvaluationIssue] = []
    evaluation = case.get("evaluation")
    if not isinstance(evaluation, Mapping):
        return [EvaluationIssue("evaluation", "evaluation must be an object")]

    mode = evaluation.get("mode")
    if not isinstance(mode, str) or not mode.strip():
        issues.append(EvaluationIssue("evaluation.mode", "mode must be a non-empty string"))
    if not isinstance(evaluation.get("check_mode_match"), bool):
        issues.append(
            EvaluationIssue(
                "evaluation.check_mode_match",
                "check_mode_match must be boolean",
            )
        )

    for key in ("required_elements", "forbidden_claims", "forbidden_elements"):
        value = evaluation.get(key)
        if value is None:
            issues.append(EvaluationIssue(f"evaluation.{key}", f"{key} must be a list"))
        elif not isinstance(value, list) or any(not isinstance(x, str) for x in value):
            issues.append(
                EvaluationIssue(
                    f"evaluation.{key}",
                    f"{key} must be a list of strings",
                )
            )

    if "config" in evaluation and not isinstance(evaluation["config"], Mapping):
        issues.append(EvaluationIssue("evaluation.config", "config must be an object"))

    if require_quality_lists:
        classification = _as_mapping(case.get("governance")).get("classification")
        if classification == "TRUSTWORTHY":
            required = _list_str(evaluation.get("required_elements"))
            forbidden = _list_str(evaluation.get("forbidden_claims"))
            forbidden_elements = _list_str(evaluation.get("forbidden_elements"))
            if not (required or forbidden or forbidden_elements):
                issues.append(
                    EvaluationIssue(
                        "evaluation.required_elements",
                        "TRUSTWORTHY rows need answer-quality constraints",
                    )
                )

    return issues


def needs_evaluation_enrichment(case: Mapping[str, Any]) -> bool:
    """True when a row needs model-authored evaluation quality constraints."""
    if audit_evaluation_fields(case):
        return True
    meta = _as_mapping(case.get("meta"))
    if meta.get("dataset_version") != "v7":
        return False
    classification = _as_mapping(case.get("governance")).get("classification")
    if classification != "TRUSTWORTHY":
        return False
    evaluation = _as_mapping(case.get("evaluation"))
    return not (
        _list_str(evaluation.get("required_elements"))
        or _list_str(evaluation.get("forbidden_claims"))
        or _list_str(evaluation.get("forbidden_elements"))
    )


def merge_evaluation_overlay(
    case: dict[str, Any],
    overlay: Mapping[str, Any],
    *,
    overwrite: bool = False,
) -> EvaluationPromotionResult:
    """Merge a model-produced canonical evaluation overlay into a case."""
    result = EvaluationPromotionResult(case_id=str(case.get("id") or ""))
    current = build_canonical_evaluation(case)
    source = overlay.get("evaluation") if isinstance(overlay.get("evaluation"), Mapping) else overlay
    if not isinstance(source, Mapping):
        return result

    merged = dict(current)
    for key in ("mode", "check_mode_match"):
        if key in source and (overwrite or not merged.get(key)):
            merged[key] = source[key]
            result.changed_paths.append(f"evaluation.{key}")
    for key in ("required_elements", "forbidden_claims", "forbidden_elements"):
        items = _list_str(source.get(key))
        if not items:
            continue
        if overwrite or not _list_str(merged.get(key)):
            merged[key] = items
            result.changed_paths.append(f"evaluation.{key}")
    config = source.get("config")
    if isinstance(config, Mapping):
        existing_config = dict(_as_mapping(merged.get("config")))
        for key, value in config.items():
            if overwrite or key not in existing_config:
                existing_config[key] = value
        if existing_config:
            merged["config"] = existing_config
            result.changed_paths.append("evaluation.config")

    case["evaluation"] = normalize_evaluation(merged)
    return result


def normalize_evaluation(evaluation: Mapping[str, Any]) -> dict[str, Any]:
    """Return a stable canonical evaluation object."""
    out = {
        "mode": str(evaluation.get("mode") or DEFAULT_EVALUATION_MODE),
        "check_mode_match": bool(evaluation.get("check_mode_match", True)),
        "required_elements": _list_str(evaluation.get("required_elements")),
        "forbidden_claims": _list_str(evaluation.get("forbidden_claims")),
        "forbidden_elements": _list_str(evaluation.get("forbidden_elements")),
    }
    config = evaluation.get("config")
    if isinstance(config, Mapping) and config:
        out["config"] = dict(sorted(config.items()))
    return out


def promote_evaluation_fields(
    case: dict[str, Any],
    *,
    strip_legacy: bool = True,
    strip_aliases: bool = True,
) -> EvaluationPromotionResult:
    """Promote useful legacy fields and optionally strip duplicate aliases."""
    result = EvaluationPromotionResult(case_id=str(case.get("id") or ""))
    canonical = normalize_evaluation(build_canonical_evaluation(case))
    if case.get("evaluation") != canonical:
        case["evaluation"] = canonical
        result.changed_paths.append("evaluation")

    if strip_aliases:
        for key in ROOT_ALIAS_FIELDS:
            if key in case:
                case.pop(key, None)
                result.stripped_paths.append(key)

        meta = case.get("meta")
        if isinstance(meta, dict):
            for key in META_ALIAS_FIELDS:
                if key in meta:
                    meta.pop(key, None)
                    result.stripped_paths.append(f"meta.{key}")

        governance = case.get("governance")
        if isinstance(governance, dict):
            for key in GOVERNANCE_ALIAS_FIELDS:
                if key in governance:
                    governance.pop(key, None)
                    result.stripped_paths.append(f"governance.{key}")

        input_block = case.get("input")
        if isinstance(input_block, dict) and "grounding_targets" in input_block:
            input_block.pop("grounding_targets", None)
            result.stripped_paths.append("input.grounding_targets")

        for idx, context in enumerate(_contexts(case)):
            if "grounding_targets" in context:
                context.pop("grounding_targets", None)
                result.stripped_paths.append(f"input.contexts[{idx}].grounding_targets")

    if strip_legacy:
        meta = case.get("meta")
        if isinstance(meta, dict) and "v51_legacy" in meta:
            meta.pop("v51_legacy", None)
            result.stripped_paths.append("meta.v51_legacy")

    return result


def _contexts(case: Mapping[str, Any]) -> Iterable[dict[str, Any]]:
    input_block = case.get("input")
    contexts = input_block.get("contexts") if isinstance(input_block, Mapping) else []
    if not isinstance(contexts, list):
        return []
    return [c for c in contexts if isinstance(c, dict)]
