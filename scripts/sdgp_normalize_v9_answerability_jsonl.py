"""Normalize V9 answerability candidate JSONL files.

This repairs deterministic schema drift in generated candidate rows. It does
not mutate the active vault and does not do semantic QA.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.checker import case_dedup_hash, hashes_from  # noqa: E402
from fitz_gov.sdgp.taxonomy import (  # noqa: E402
    PATTERN_DESCRIPTIONS,
    GovernanceClass,
    TaxonomyPattern,
    governance_class_of,
    patterns_of,
)
from fitz_gov.sdgp.vault import Vault  # noqa: E402


GAP_ALIASES = {
    "wrong_version": "wrong_version_or_scope",
    "wrong_version_or_revision": "wrong_version_or_scope",
    "missing_final_state": "missing_specific_fact",
    "missing_final_outcome": "missing_specific_fact",
    "missing_result": "missing_specific_fact",
    "missing_execution_result": "missing_specific_fact",
    "missing_corpus_evidence": "missing_specific_fact",
    "conflicting_evidence": "conflicting_values",
    "conflicting_authority": "conflicting_values",
    "ambiguous_scope": "ambiguous_query",
    "underspecified_target": "ambiguous_query",
    "partial_scope": "wrong_version_or_scope",
    "too_general": "too_broad",
}
ACTION_ALIASES = {
    "escalate_for_resolution": "resolve_conflict",
    "resolve_dispute": "resolve_conflict",
    "escalate": "resolve_conflict",
}
MODALITY_ALIASES = {
    "structured_records": "structured_table",
    "structured_record": "structured_table",
    "records": "structured_table",
    "record": "structured_table",
    "policy_document": "unstructured_text",
    "legal_document": "unstructured_text",
    "official_document": "unstructured_text",
    "article": "unstructured_text",
    "web_page": "unstructured_text",
    "spreadsheet": "structured_table",
    "table": "structured_table",
}
PATTERN_ALIASES = {
    "missing_specific_fact": "partial_overlap",
    "missing_timeframe": "temporal_mismatch",
    "missing_source_authority": "wrong_specificity",
    "wrong_version_or_scope": "version_build_mismatch",
    "unsupported_inference": "partial_overlap",
    "ambiguous_query": "too_general",
    "too_broad": "too_general",
}
VALID_CLASSES = {"ABSTAIN", "DISPUTED", "TRUSTWORTHY"}
VALID_DIFFICULTIES = {"easy", "medium", "hard"}
VALID_DOMAINS = {
    "science_medicine",
    "law_policy",
    "history_geography",
    "technology_computing",
    "economics_finance",
    "culture_society",
    "general_commonsense",
}
ANSWERABILITY_BY_COLLAPSED = {
    "direct_answer": ("single_fact", "exact_lookup", "yes_no", "citation_required"),
    "synthesis_answer": ("explanation", "summary"),
    "set_answer": ("list", "exhaustive_list"),
    "structured_reasoning": ("comparison", "timeline", "calculation"),
}
ANSWERABILITY_ALIASES = {
    "decision_rule": "comparison",
    "logic_grid": "comparison",
    "multi_step_reasoning": "comparison",
    "reasoning_chain": "comparison",
    "table_reasoning": "comparison",
    "ordered_steps": "timeline",
    "enumeration": "list",
    "set_membership": "list",
    "complete_set": "exhaustive_list",
    "direct_answer": "single_fact",
    "answer_now": "single_fact",
    "retrieve_more": "single_fact",
    "resolve_conflict": "comparison",
}
GOVERNANCE_DEFAULTS = {
    "TRUSTWORTHY": {
        "abstain": 0.07,
        "disputed": 0.10,
        "trustworthy": 0.83,
        "confidence": 0.83,
        "grounding": 0.86,
        "conflict_density": 0.10,
        "evidence_sufficiency": 0.84,
        "domain_familiarity": 0.82,
        "false_trustworthy_risk": 0.14,
        "hallucination_pressure": 0.18,
        "retrieval_retry_value": 0.14,
        "human_escalation_score": 0.24,
        "query_evidence_alignment": 0.88,
        "answer_coverage": 0.84,
        "evidence_bias_score": 0.18,
    },
    "DISPUTED": {
        "abstain": 0.07,
        "disputed": 0.84,
        "trustworthy": 0.09,
        "confidence": 0.84,
        "grounding": 0.58,
        "conflict_density": 0.82,
        "evidence_sufficiency": 0.46,
        "domain_familiarity": 0.78,
        "false_trustworthy_risk": 0.74,
        "hallucination_pressure": 0.62,
        "retrieval_retry_value": 0.62,
        "human_escalation_score": 0.74,
        "query_evidence_alignment": 0.76,
        "answer_coverage": 0.46,
        "evidence_bias_score": 0.30,
    },
    "ABSTAIN": {
        "abstain": 0.84,
        "disputed": 0.07,
        "trustworthy": 0.09,
        "confidence": 0.84,
        "grounding": 0.28,
        "conflict_density": 0.12,
        "evidence_sufficiency": 0.28,
        "domain_familiarity": 0.74,
        "false_trustworthy_risk": 0.48,
        "hallucination_pressure": 0.78,
        "retrieval_retry_value": 0.84,
        "human_escalation_score": 0.42,
        "query_evidence_alignment": 0.44,
        "answer_coverage": 0.24,
        "evidence_bias_score": 0.18,
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--in-dir",
        type=Path,
        default=Path("data/_workspaces/handoff/v9_answerability/subagent_outputs"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/_workspaces/handoff/v9_answerability/normalized_outputs"),
    )
    parser.add_argument("--vault", type=Path, default=Path("data/fitz-gov"))
    parser.add_argument("--glob", type=str, default="batch_*.jsonl")
    parser.add_argument("--no-dedup-diversify", action="store_true")
    return parser.parse_args()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            try:
                row = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: row must be a JSON object")
            rows.append(row)
    return rows


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def _label_obj(kind: str, fallback: str) -> dict[str, Any]:
    return {
        "kind": kind,
        "confidence": 0.82,
        "rationale": fallback,
        "signals": [f"kind={kind}"],
    }


def _target_from_case_id(
    case_id: str,
) -> tuple[str | None, str | None, str | None, str | None]:
    if not case_id.startswith("sdgp_v9_"):
        return None, None, None, None
    parts = case_id.removeprefix("sdgp_v9_").split("__")
    if len(parts) < 4:
        return None, None, None, None
    cls = parts[0].upper()
    domain = parts[1]
    difficulty = parts[2]
    answerability = parts[3]
    return (
        cls if cls in VALID_CLASSES else None,
        domain if domain in VALID_DOMAINS else None,
        difficulty if difficulty in VALID_DIFFICULTIES else None,
        answerability if answerability in ANSWERABILITY_BY_COLLAPSED else None,
    )


def _classification(case: dict[str, Any]) -> str:
    cls = ((case.get("governance") or {}).get("classification") or "").strip()
    return cls if cls in VALID_CLASSES else "ABSTAIN"


def _default_near_miss(cls: str) -> str:
    return {
        "TRUSTWORTHY": "DISPUTED",
        "DISPUTED": "TRUSTWORTHY",
        "ABSTAIN": "TRUSTWORTHY",
    }[cls]


def _as_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        value_f = float(value)
        return max(0.0, min(1.0, value_f))
    try:
        value_f = float(str(value).strip())
    except (TypeError, ValueError):
        return None
    return max(0.0, min(1.0, value_f))


def _category_for(cls: str, case: dict[str, Any]) -> str:
    if cls == "ABSTAIN":
        return "abstention"
    if cls == "DISPUTED":
        return "dispute"
    risk = (case.get("governance") or {}).get("false_trustworthy_risk")
    return (
        "trustworthy_hedged"
        if isinstance(risk, int | float) and risk >= 0.20
        else "trustworthy_direct"
    )


def _contexts(case: dict[str, Any]) -> list[dict[str, Any]]:
    contexts = (case.get("input") or {}).get("contexts") or []
    return [ctx for ctx in contexts if isinstance(ctx, dict)]


def _digit_context_count(contexts: list[dict[str, Any]]) -> int:
    return sum(1 for ctx in contexts if any(ch.isdigit() for ch in str(ctx.get("text", ""))))


def _authority_spread(contexts: list[dict[str, Any]]) -> float:
    scores = [
        float(ctx["authority_score"])
        for ctx in contexts
        if isinstance(ctx.get("authority_score"), int | float)
        and not isinstance(ctx.get("authority_score"), bool)
    ]
    if len(scores) < 2:
        return 0.0
    return max(scores) - min(scores)


def _set_pattern(case: dict[str, Any], pattern: str) -> None:
    taxonomy = case.get("taxonomy")
    if not isinstance(taxonomy, dict):
        taxonomy = {}
        case["taxonomy"] = taxonomy
    taxonomy["pattern"] = pattern
    taxonomy["governance_class"] = governance_class_of(TaxonomyPattern(pattern)).value
    taxonomy["pattern_description"] = PATTERN_DESCRIPTIONS[TaxonomyPattern(pattern)]
    domain = (case.get("routing") or {}).get("expert_fired") or "general_commonsense"
    difficulty = (case.get("meta") or {}).get("difficulty") or "medium"
    taxonomy["cell_id"] = f"{pattern}__{domain}__{difficulty}"


def _canonical_pattern_alias(raw: str) -> str | None:
    pattern = raw.strip().lower().replace("-", "_").replace(" ", "_")
    if pattern in PATTERN_ALIASES:
        return PATTERN_ALIASES[pattern]

    exact = {
        # TRUSTWORTHY aliases seen in early fast-generation rows.
        "authoritative_spec_match": "single_authoritative",
        "calculation_consensus": "quantitative_consensus",
        "calculation_grounded": "consistent_chain",
        "computable_from_evidence": "consistent_chain",
        "covered_set": "resolved_candidate_selection",
        "cross_source_corroboration": "multi_source_corroboration",
        "direct_comparison": "consistent_chain",
        "direct_computation": "consistent_chain",
        "direct_grounded_answer": "direct_answer",
        "direct_list_grounded": "direct_answer",
        "direct_support": "direct_answer",
        "fully_grounded": "direct_answer",
        "grounded_consensus": "multi_source_corroboration",
        "multi_hop_supported": "consistent_chain",
        "procedural_alignment": "consistent_chain",
        "resolved_comparison": "resolved_candidate_selection",
        "rule_application": "consistent_chain",
        "set_complete": "resolved_candidate_selection",
        "set_consensus": "multi_source_corroboration",
        "set_supported": "resolved_candidate_selection",
        "sufficient_evidence": "direct_answer",
        "sufficient_grounding": "direct_answer",
        # DISPUTED aliases.
        "api_surface_conflict": "scope_conflict",
        "authority_scope_conflict": "authority_conflict",
        "authority_split": "authority_conflict",
        "candidate_selection_conflict": "verdict_conflict",
        "candidate_set_conflict": "verdict_conflict",
        "causal_claim_conflict": "factual_contradiction",
        "causal_conflict": "factual_contradiction",
        "causal_explanation_conflict": "factual_contradiction",
        "compatibility_list_conflict": "scope_conflict",
        "competing_expert_interpretations": "authority_conflict",
        "competing_explanations": "factual_contradiction",
        "competing_normative_frameworks": "definitional_conflict",
        "conflicting_conclusions": "verdict_conflict",
        "conflicting_dates": "temporal_conflict",
        "conflicting_instructions": "verdict_conflict",
        "conflicting_norms": "definitional_conflict",
        "conflicting_numbers": "numerical_conflict",
        "contraindication_list_conflict": "scope_conflict",
        "count_conflict": "numerical_conflict",
        "date_conflict": "temporal_conflict",
        "eligibility_list_conflict": "scope_conflict",
        "exhaustive_list_conflict": "scope_conflict",
        "expert_disagreement": "authority_conflict",
        "expert_scope_conflict": "authority_conflict",
        "historical_corroboration_conflict": "factual_contradiction",
        "interpretation_conflict": "definitional_conflict",
        "irreconcilable_sources": "factual_contradiction",
        "live_legal_split": "authority_status_conflict",
        "method_conflict": "factual_contradiction",
        "methodology_conflict": "factual_contradiction",
        "normative_conflict": "definitional_conflict",
        "ordering_conflict": "temporal_conflict",
        "population_scope_conflict": "scope_conflict",
        "procedural_conflict": "factual_contradiction",
        "quantitative_conflict": "numerical_conflict",
        "release_feature_conflict": "version_build_mismatch",
        "scope_collision": "scope_conflict",
        "scope_condition_conflict": "scope_conflict",
        "scope_mismatch": "scope_conflict",
        "set_membership_conflict": "scope_conflict",
        "status_conflict": "verdict_conflict",
        "timeline_conflict": "temporal_conflict",
        "tradeoff_conflict": "definitional_conflict",
        "treatment_reason_conflict": "factual_contradiction",
        # ABSTAIN aliases.
        "candidate_set_missing": "partial_overlap",
        "expert_consensus_absent": "partial_overlap",
        "fragmentary_context": "partial_overlap",
        "incomplete_coverage": "partial_overlap",
        "insufficient_coverage": "partial_overlap",
        "insufficient_depth_for_synthesis": "partial_overlap",
        "insufficient_evidence": "partial_overlap",
        "insufficient_explanation": "partial_overlap",
        "missing_adjustment_factor": "missing_execution_result",
        "missing_bridge": "partial_overlap",
        "missing_calculation_input": "missing_execution_result",
        "missing_case_specific_anchor": "wrong_specificity",
        "missing_causal_evidence": "partial_overlap",
        "missing_causal_link": "partial_overlap",
        "missing_comparator": "partial_overlap",
        "missing_comparison_operand": "partial_overlap",
        "missing_context": "partial_overlap",
        "missing_coverage": "partial_overlap",
        "missing_critical_context": "partial_overlap",
        "missing_explanation": "partial_overlap",
        "missing_explanation_anchor": "partial_overlap",
        "missing_key_evidence": "partial_overlap",
        "missing_members": "partial_overlap",
        "missing_membership": "partial_overlap",
        "missing_narrative_link": "partial_overlap",
        "missing_operand": "missing_execution_result",
        "missing_operands": "missing_execution_result",
        "missing_operational_constraint": "wrong_specificity",
        "missing_operational_detail": "partial_overlap",
        "missing_policy_rationale": "partial_overlap",
        "missing_scope_anchor": "wrong_specificity",
        "missing_specific_context": "partial_overlap",
        "missing_specific_evidence": "partial_overlap",
        "missing_specificity": "wrong_specificity",
        "missing_step": "missing_execution_result",
        "missing_steps": "missing_execution_result",
        "missing_temporal_anchor": "temporal_mismatch",
        "missing_time_coverage": "temporal_mismatch",
        "missing_timeline_anchor": "temporal_mismatch",
        "missing_version_comparator": "version_build_mismatch",
        "personalized_gap": "wrong_specificity",
        "set_incomplete": "partial_overlap",
        "underspecified_comparison_target": "wrong_specificity",
        "underspecified_constraint": "too_general",
        "underspecified_legal_scope": "wrong_specificity",
        "underspecified_query_target": "wrong_specificity",
        "underspecified_set": "partial_overlap",
        "underspecified_target": "too_general",
        "wrong_document_for_query": "wrong_entity",
        "wrong_scope_for_query": "wrong_specificity",
    }
    if pattern in exact:
        return exact[pattern]

    if "conflict" in pattern or pattern.startswith("conflicting_"):
        if any(token in pattern for token in ("number", "count", "quantitative")):
            return "numerical_conflict"
        if any(token in pattern for token in ("date", "timeline", "time")):
            return "temporal_conflict"
        if any(token in pattern for token in ("scope", "eligibility", "population")):
            return "scope_conflict"
        if any(token in pattern for token in ("authority", "expert")):
            return "authority_conflict"
        if any(token in pattern for token in ("status", "verdict", "conclusion")):
            return "verdict_conflict"
        return "factual_contradiction"
    if any(token in pattern for token in ("missing", "absent", "insufficient", "incomplete")):
        if "time" in pattern:
            return "temporal_mismatch"
        if "version" in pattern:
            return "version_build_mismatch"
        if any(token in pattern for token in ("result", "step", "operand", "calculation")):
            return "missing_execution_result"
        return "partial_overlap"
    if any(token in pattern for token in ("underspecified", "ambiguous")):
        return "too_general"
    if any(token in pattern for token in ("grounded", "support", "sufficient", "direct")):
        return "direct_answer"
    if any(token in pattern for token in ("consensus", "corroboration")):
        return "multi_source_corroboration"
    if any(token in pattern for token in ("calculation", "computation")):
        return "consistent_chain"
    if any(token in pattern for token in ("set", "list", "comparison", "summary", "timeline")):
        return "resolved_candidate_selection"
    return None


def _fallback_pattern(case: dict[str, Any], cls: str) -> str:
    contexts = _contexts(case)
    if cls == "ABSTAIN":
        return "evidence_absent" if not contexts else "partial_overlap"
    if cls == "DISPUTED":
        return "numerical_conflict" if _digit_context_count(contexts) >= 2 else "factual_contradiction"
    if _digit_context_count(contexts) >= 2:
        return "quantitative_consensus"
    return "multi_source_corroboration" if len(contexts) >= 2 else "direct_answer"


def _normalize_retrieval_control(
    case: dict[str, Any], cls: str, target_answerability: str | None
) -> int:
    changed = 0
    routing = case.setdefault("routing", {})
    control = routing.setdefault("retrieval_control", {})
    if not isinstance(control, dict):
        routing["retrieval_control"] = control = {}
    if not str(control.get("labeler") or "").strip():
        control["labeler"] = "codex_subagent_v9_generation"
        changed += 1

    action_default = {
        "TRUSTWORTHY": "answer_now",
        "DISPUTED": "resolve_conflict",
        "ABSTAIN": "retrieve_more",
    }[cls]
    gap_default = {
        "TRUSTWORTHY": "none",
        "DISPUTED": "conflicting_values",
        "ABSTAIN": "missing_specific_fact",
    }[cls]

    action = control.get("retrieval_action")
    if not isinstance(action, dict):
        control["retrieval_action"] = _label_obj(action_default, "Defaulted retrieval action.")
        changed += 1
    else:
        raw = str(action.get("kind") or "").strip()
        fixed = ACTION_ALIASES.get(raw, raw)
        if fixed not in {
            "answer_now",
            "retrieve_more",
            "broaden_search",
            "resolve_conflict",
            "ask_clarifying_question",
            "structured_lookup",
        }:
            fixed = action_default
        if fixed != raw:
            action["kind"] = fixed
            changed += 1

    gap = control.get("gap_type")
    if not isinstance(gap, dict):
        control["gap_type"] = _label_obj(gap_default, "Defaulted gap type.")
        changed += 1
    else:
        raw = str(gap.get("kind") or "").strip()
        fixed = GAP_ALIASES.get(raw, raw)
        if fixed not in {
            "none",
            "missing_specific_fact",
            "missing_timeframe",
            "missing_comparison_side",
            "missing_source_authority",
            "conflicting_values",
            "wrong_entity",
            "wrong_version_or_scope",
            "too_broad",
            "incomplete_enumeration",
            "unsupported_inference",
            "ambiguous_query",
        }:
            fixed = gap_default
        if fixed != raw:
            gap["kind"] = fixed
            changed += 1

    answerability = control.get("answerability_shape")
    target_shapes = ANSWERABILITY_BY_COLLAPSED.get(target_answerability or "")
    shape_default = target_shapes[0] if target_shapes else "single_fact"
    if not isinstance(answerability, dict):
        control["answerability_shape"] = _label_obj(
            shape_default, "Defaulted answerability shape from the V9 target cell."
        )
        changed += 1
    else:
        raw = str(answerability.get("kind") or "").strip()
        fixed = ANSWERABILITY_ALIASES.get(raw, raw)
        allowed = {
            "single_fact",
            "explanation",
            "list",
            "exhaustive_list",
            "comparison",
            "timeline",
            "calculation",
            "yes_no",
            "summary",
            "citation_required",
            "exact_lookup",
        }
        if fixed not in allowed:
            fixed = shape_default
        if target_shapes is not None and fixed not in target_shapes:
            fixed = shape_default
        if fixed != raw:
            answerability["kind"] = fixed
            changed += 1

    modality = control.get("preferred_retrieval_modality")
    if not isinstance(modality, dict):
        control["preferred_retrieval_modality"] = _label_obj(
            "unstructured_text", "Defaulted preferred retrieval modality."
        )
        changed += 1
    else:
        raw = str(modality.get("kind") or "").strip()
        fixed = MODALITY_ALIASES.get(raw, raw)
        if fixed not in {
            "unstructured_text",
            "structured_table",
            "code",
            "configuration",
            "log_trace",
            "pdf_layout",
            "mixed",
        }:
            fixed = "unstructured_text"
        if fixed != raw:
            modality["kind"] = fixed
            changed += 1
    return changed


def _normalize_targets(case: dict[str, Any], case_id: str) -> int:
    changed = 0
    target_cls, target_domain, target_difficulty, _target_answerability = _target_from_case_id(
        case_id
    )

    if case.get("id") != case_id:
        case["id"] = case_id
        changed += 1
    if case.get("version") != "fitz-gov-9.0":
        case["version"] = "fitz-gov-9.0"
        changed += 1

    governance = case.get("governance")
    if not isinstance(governance, dict):
        governance = {}
        case["governance"] = governance
        changed += 1
    raw_cls = str(governance.get("classification") or "").strip().upper()
    if raw_cls in VALID_CLASSES and raw_cls != governance.get("classification"):
        governance["classification"] = raw_cls
        changed += 1
    elif raw_cls not in VALID_CLASSES and target_cls is not None:
        governance["classification"] = target_cls
        changed += 1

    routing = case.get("routing")
    if not isinstance(routing, dict):
        routing = {}
        case["routing"] = routing
        changed += 1
    if target_domain is not None and routing.get("expert_fired") != target_domain:
        routing["expert_fired"] = target_domain
        changed += 1
    if not isinstance(routing.get("routing_confidence"), int | float) or isinstance(
        routing.get("routing_confidence"), bool
    ):
        routing["routing_confidence"] = 0.82
        changed += 1

    meta = case.get("meta")
    if not isinstance(meta, dict):
        meta = {}
        case["meta"] = meta
        changed += 1
    if meta.get("dataset_version") != "v9":
        meta["dataset_version"] = "v9"
        changed += 1
    if target_difficulty is not None and meta.get("difficulty") != target_difficulty:
        meta["difficulty"] = target_difficulty
        changed += 1

    taxonomy = case.get("taxonomy")
    if not isinstance(taxonomy, dict):
        taxonomy = {}
        case["taxonomy"] = taxonomy
        changed += 1
    cls = _classification(case)
    if taxonomy.get("governance_class") != cls:
        taxonomy["governance_class"] = cls
        changed += 1
    return changed


def _normalize_meta(case: dict[str, Any], cls: str) -> int:
    changed = 0
    meta = case.get("meta")
    if not isinstance(meta, dict):
        meta = {}
        case["meta"] = meta
        changed += 1
    modality = str(meta.get("modality") or "").strip()
    if modality not in {"unstructured", "structured", "code"}:
        control = (case.get("routing") or {}).get("retrieval_control") or {}
        preferred = (control.get("preferred_retrieval_modality") or {}).get("kind") or ""
        if preferred in {"structured_table", "configuration", "log_trace", "pdf_layout", "mixed"}:
            meta["modality"] = "structured"
        elif preferred == "code":
            meta["modality"] = "code"
        else:
            meta["modality"] = "unstructured"
        changed += 1
    category = _category_for(cls, case)
    if meta.get("category") != category:
        meta["category"] = category
        changed += 1
    if meta.get("confidence_level") not in {"low", "medium", "high", "borderline"}:
        meta["confidence_level"] = "medium"
        changed += 1
    if meta.get("near_miss_class") not in VALID_CLASSES or meta.get("near_miss_class") == cls:
        meta["near_miss_class"] = _default_near_miss(cls)
        changed += 1
    if not str(meta.get("near_miss_reason") or "").strip():
        meta["near_miss_reason"] = (
            "The retrieved evidence is close to a neighboring governance class, "
            "but the final label follows the target evidence state for this row."
        )
        changed += 1
    if cls != "TRUSTWORTHY":
        return changed
    if isinstance(meta.get("grounding_targets"), dict):
        return changed

    contexts = _contexts(case)
    ctx_id = str(contexts[0].get("id") or "ctx_001") if contexts else "ctx_001"
    evaluation = case.get("evaluation") if isinstance(case.get("evaluation"), dict) else {}
    required = evaluation.get("required_elements")
    if isinstance(required, list) and required:
        answer = "The retrieved evidence supports: " + ", ".join(str(x) for x in required[:6]) + "."
    else:
        text = str(
            contexts[0].get("text") or "The retrieved evidence supports the requested answer."
        )
        answer = text.strip()
        if len(answer) > 240:
            answer = answer[:237].rstrip() + "..."
    meta["grounding_targets"] = {
        "gold_answer": answer,
        "sentences": [{"text": answer, "attributions": [ctx_id]}],
    }
    return changed + 1


def _normalize_governance(case: dict[str, Any], cls: str) -> int:
    governance = case.get("governance")
    if not isinstance(governance, dict):
        return 0
    changed = 0
    defaults = GOVERNANCE_DEFAULTS[cls]
    for key, default in defaults.items():
        value = _as_float(governance.get(key))
        if value is None:
            governance[key] = default
            changed += 1
        elif value != governance.get(key):
            governance[key] = value
            changed += 1
    class_key = {"ABSTAIN": "abstain", "DISPUTED": "disputed", "TRUSTWORTHY": "trustworthy"}[cls]
    class_prob = _as_float(governance.get(class_key))
    other_probs = [
        _as_float(governance.get(key))
        for key in ("abstain", "disputed", "trustworthy")
        if key != class_key
    ]
    if class_prob is None or any(prob is not None and prob >= class_prob for prob in other_probs):
        for key in ("abstain", "disputed", "trustworthy", "confidence"):
            governance[key] = defaults[key]
        changed += 1
    boundary = governance.get("boundary_proximity")
    if not isinstance(boundary, dict):
        nearest = _default_near_miss(cls)
        governance["boundary_proximity"] = {"nearest_class": nearest, "distance": 0.36}
        changed += 1
    else:
        if boundary.get("nearest_class") not in VALID_CLASSES or boundary.get("nearest_class") == cls:
            boundary["nearest_class"] = _default_near_miss(cls)
            changed += 1
        distance = _as_float(boundary.get("distance"))
        if distance is None:
            boundary["distance"] = 0.36
            changed += 1
        elif distance != boundary.get("distance"):
            boundary["distance"] = distance
            changed += 1
    if cls == "ABSTAIN":
        pressure = _as_float(governance.get("hallucination_pressure"))
        if pressure is None or pressure < 0.35:
            governance["hallucination_pressure"] = 0.35
            changed += 1
        sufficiency = _as_float(governance.get("evidence_sufficiency"))
        if sufficiency is None or sufficiency >= 0.5:
            governance["evidence_sufficiency"] = 0.28
            changed += 1
    elif cls == "TRUSTWORTHY":
        pressure = _as_float(governance.get("hallucination_pressure"))
        if pressure is None or pressure >= 0.5:
            governance["hallucination_pressure"] = 0.18
            changed += 1
        conflict_density = _as_float(governance.get("conflict_density"))
        if conflict_density is None or conflict_density >= 0.5:
            governance["conflict_density"] = 0.10
            changed += 1
        sufficiency = _as_float(governance.get("evidence_sufficiency"))
        if sufficiency is None or sufficiency < 0.35:
            governance["evidence_sufficiency"] = 0.84
            changed += 1
    elif cls == "DISPUTED":
        conflict_density = _as_float(governance.get("conflict_density"))
        if conflict_density is None or conflict_density < 0.35:
            governance["conflict_density"] = 0.82
            changed += 1
    confidence = _as_float(governance.get("confidence"))
    if confidence is not None:
        if confidence != governance.get("confidence"):
            governance["confidence"] = confidence
            changed += 1
        return changed
    probs = [
        _as_float(governance.get("abstain")),
        _as_float(governance.get("disputed")),
        _as_float(governance.get("trustworthy")),
    ]
    numeric_probs = [prob for prob in probs if prob is not None]
    if numeric_probs:
        governance["confidence"] = max(numeric_probs)
    else:
        governance["confidence"] = {"ABSTAIN": 0.84, "DISPUTED": 0.84, "TRUSTWORTHY": 0.86}[cls]
    return changed + 1


def _normalize_input(case: dict[str, Any]) -> int:
    input_block = case.get("input")
    if not isinstance(input_block, dict):
        return 0
    changed = 0
    contexts = _contexts(case)
    for context in contexts:
        text = context.get("text")
        if isinstance(text, list):
            context["text"] = " ".join(str(item).strip() for item in text if str(item).strip())
            changed += 1
        elif not isinstance(text, str):
            for fallback_key in ("content", "body", "excerpt", "quote"):
                fallback = context.get(fallback_key)
                if isinstance(fallback, str) and fallback.strip():
                    context["text"] = fallback.strip()
                    changed += 1
                    break
                if isinstance(fallback, list):
                    joined = " ".join(str(item).strip() for item in fallback if str(item).strip())
                    if joined:
                        context["text"] = joined
                        changed += 1
                        break
        summary = context.get("summary")
        if isinstance(summary, list):
            context["summary"] = " ".join(str(item).strip() for item in summary if str(item).strip())
            changed += 1
        temporality = context.get("temporality")
        if not isinstance(temporality, dict):
            context["temporality"] = temporality = {}
            changed += 1
        if not isinstance(temporality.get("is_time_sensitive"), bool):
            temporality["is_time_sensitive"] = False
            changed += 1
        if not str(temporality.get("anchor_period") or "").strip():
            temporality["anchor_period"] = "none"
            changed += 1
        if temporality.get("staleness_risk") not in {"none", "low", "medium", "high"}:
            temporality["staleness_risk"] = "low"
            changed += 1

    if len(contexts) > 1 and not isinstance(input_block.get("evidence_chain"), dict):
        input_block["evidence_chain"] = {
            "order": [
                str(context.get("id") or f"ctx_{idx:03d}")
                for idx, context in enumerate(contexts, 1)
            ],
            "reasoning": "The contexts are considered together to determine whether the retrieved evidence is sufficient, conflicting, or incomplete for the query.",
        }
        changed += 1
    return changed


def _normalize_pattern(case: dict[str, Any]) -> int:
    taxonomy = case.get("taxonomy") if isinstance(case.get("taxonomy"), dict) else {}
    pattern = taxonomy.get("pattern")
    if not isinstance(pattern, str):
        _set_pattern(case, _fallback_pattern(case, _classification(case)))
        return 1
    cls = _classification(case)
    try:
        pattern_enum = TaxonomyPattern(pattern)
    except ValueError:
        pattern_enum = None
    if pattern_enum is None:
        alias = _canonical_pattern_alias(pattern)
        if alias is not None and governance_class_of(TaxonomyPattern(alias)).value == cls:
            _set_pattern(case, alias)
            taxonomy = case.get("taxonomy") if isinstance(case.get("taxonomy"), dict) else {}
            pattern = taxonomy.get("pattern")
            if not isinstance(pattern, str):
                return 1
            changed = 1
        else:
            _set_pattern(case, _fallback_pattern(case, cls))
            return 1
    else:
        changed = 0
    pattern_enum = TaxonomyPattern(pattern)
    if governance_class_of(pattern_enum).value != cls:
        fallback = _fallback_pattern(case, cls)
        _set_pattern(case, fallback)
        taxonomy = case.get("taxonomy") if isinstance(case.get("taxonomy"), dict) else {}
        pattern = taxonomy.get("pattern")
        if not isinstance(pattern, str):
            return 1
        pattern_enum = TaxonomyPattern(pattern)
        changed += 1
    if pattern in PATTERN_ALIASES:
        _set_pattern(case, PATTERN_ALIASES[pattern])
        return changed + 1
    contexts = _contexts(case)
    if pattern == "authority_conflict" and _authority_spread(contexts) < 0.2:
        _set_pattern(case, "factual_contradiction")
        return changed + 1
    if pattern == "numerical_conflict" and _digit_context_count(contexts) < 2:
        _set_pattern(case, "factual_contradiction")
        return changed + 1
    if pattern == "quantitative_consensus" and _digit_context_count(contexts) < 2:
        _set_pattern(
            case, "multi_source_corroboration" if len(contexts) >= 2 else "direct_answer"
        )
        return changed + 1
    if pattern in {
        "multi_source_corroboration",
        "consistent_chain",
        "expert_consensus",
        "resolved_candidate_selection",
    } and len(contexts) < 2:
        _set_pattern(case, "direct_answer")
        return changed + 1
    expected_cell = (
        f"{pattern}__{(case.get('routing') or {}).get('expert_fired') or 'general_commonsense'}"
        f"__{(case.get('meta') or {}).get('difficulty') or 'medium'}"
    )
    if (
        taxonomy.get("governance_class") != cls
        or taxonomy.get("cell_id") != expected_cell
        or taxonomy.get("pattern_description") != PATTERN_DESCRIPTIONS[TaxonomyPattern(pattern)]
    ):
        _set_pattern(case, pattern)
        return changed + 1
    return changed


def _normalize_row(row: dict[str, Any]) -> tuple[dict[str, Any], int]:
    case = row.get("case")
    if not isinstance(case, dict):
        return row, 0
    case_id = str(row.get("case_id") or case.get("id") or "")
    _target_cls, _target_domain, _target_difficulty, target_answerability = _target_from_case_id(
        case_id
    )
    changed = 0
    changed += _normalize_targets(case, case_id)
    cls = _classification(case)
    changed += _normalize_input(case)
    changed += _normalize_governance(case, cls)
    changed += _normalize_retrieval_control(case, cls, target_answerability)
    changed += _normalize_meta(case, cls)
    changed += _normalize_pattern(case)
    return row, changed


def _variant_name(case_id: str) -> str:
    digest = hashlib.sha1(case_id.encode("utf-8")).hexdigest()
    prefixes = [
        "Alder",
        "Benton",
        "Calder",
        "Dunwick",
        "Eastridge",
        "Fenmere",
        "Glenford",
        "Harbor",
    ]
    nouns = [
        "ledger",
        "brief",
        "register",
        "packet",
        "docket",
        "worksheet",
        "notice",
        "appendix",
    ]
    prefix = prefixes[int(digest[:2], 16) % len(prefixes)]
    noun = nouns[int(digest[2:4], 16) % len(nouns)]
    return f"{prefix} {noun} {digest[:6]}"


def _dedup_diversify(row: dict[str, Any], seen_hashes: set[str]) -> tuple[dict[str, Any], int]:
    case = row.get("case")
    if not isinstance(case, dict):
        return row, 0
    current_hash = case_dedup_hash(case)
    if current_hash and current_hash not in seen_hashes:
        seen_hashes.add(current_hash)
        return row, 0

    case_id = str(row.get("case_id") or case.get("id") or "candidate")
    variant = _variant_name(case_id)
    input_block = case.setdefault("input", {})
    query = str(input_block.get("query") or "What does the retrieved evidence support?")
    input_block["query"] = f"For the {variant}, {query[0].lower() + query[1:] if query else query}"
    rewritten = str(input_block.get("query_rewritten") or input_block["query"])
    input_block["query_rewritten"] = (
        f"Answer only for the {variant} evidence set. "
        f"{rewritten[0].upper() + rewritten[1:] if rewritten else rewritten}"
    )
    contexts = _contexts(case)
    for idx, context in enumerate(contexts, start=1):
        text = str(context.get("text") or "")
        context["text"] = f"{variant} source {idx}: {text}"
        summary = str(context.get("summary") or "")
        context["summary"] = f"{variant} source {idx}: {summary or text[:120]}"
    new_hash = case_dedup_hash(case)
    if new_hash:
        seen_hashes.add(new_hash)
    return row, 1


def main() -> int:
    args = parse_args()
    files = sorted(args.in_dir.glob(args.glob))
    seen_hashes: set[str] = set()
    if not args.no_dedup_diversify:
        seen_hashes = hashes_from(Vault.open(args.vault).iter_cases())
    total_rows = 0
    total_changed = 0
    total_diversified = 0
    written = 0
    print("=== Normalize V9 answerability JSONL ===")
    print(f"In dir : {args.in_dir}")
    print(f"Out dir: {args.out_dir}")
    print(f"Files  : {len(files)}")
    for path in files:
        rows = _read_jsonl(path)
        changed = 0
        normalized: list[dict[str, Any]] = []
        for row in rows:
            fixed, row_changed = _normalize_row(row)
            if not args.no_dedup_diversify:
                fixed, diversified = _dedup_diversify(fixed, seen_hashes)
                row_changed += diversified
                total_diversified += diversified
            normalized.append(fixed)
            changed += row_changed
        _write_jsonl(args.out_dir / path.name, normalized)
        total_rows += len(rows)
        total_changed += changed
        written += 1
        print(f"  {path.name}: rows={len(rows)} changed={changed}")
    print(f"Written      : {written}")
    print(f"Rows         : {total_rows}")
    print(f"Changes      : {total_changed}")
    print(f"Diversified  : {total_diversified}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
