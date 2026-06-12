"""Expand compact V9 semantic plans into canonical SDGP rows.

Input rows have shape:

    {"case_id": "...", "plan": {...}}

Output rows have the normal V9 generated-row shape:

    {"case_id": "...", "case": {...}}

This is a pilot tool. It writes candidate files only and never mutates the
active vault.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.retrieval_control_gap_detector import collapse_answerability_shape
from fitz_gov.sdgp.taxonomy import (  # noqa: E402
    PATTERN_DESCRIPTIONS,
    GovernanceClass,
    TaxonomyPattern,
    patterns_of,
)


QUERY_CONTRACTS = {
    "evidence_sufficiency",
    "structured_lookup",
    "temporal_grounding",
    "exhaustive_coverage",
    "comparison_coverage",
    "representative_overview",
}
RETRIEVAL_ACTIONS = {
    "answer_now",
    "retrieve_more",
    "broaden_search",
    "resolve_conflict",
    "ask_clarifying_question",
    "structured_lookup",
}
GAP_TYPES = {
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
}
ANSWERABILITY_SHAPES = {
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
RETRIEVAL_MODALITIES = {
    "unstructured_text",
    "structured_table",
    "code",
    "configuration",
    "log_trace",
    "pdf_layout",
    "mixed",
}

DEFAULT_PROBS = {
    "TRUSTWORTHY": {"abstain": 0.07, "disputed": 0.10, "trustworthy": 0.83},
    "DISPUTED": {"abstain": 0.07, "disputed": 0.84, "trustworthy": 0.09},
    "ABSTAIN": {"abstain": 0.84, "disputed": 0.07, "trustworthy": 0.09},
}

DEFAULT_SCORES = {
    "TRUSTWORTHY": {
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
        "grounding": 0.28,
        "conflict_density": 0.12,
        "evidence_sufficiency": 0.22,
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
        "--plan-dir",
        type=Path,
        default=Path(
            "data/_workspaces/handoff/v9_answerability_compact_pilot/semantic_plan_outputs"
        ),
    )
    parser.add_argument(
        "--batch-dir",
        type=Path,
        default=Path("data/_workspaces/handoff/v9_answerability_compact_pilot/batch_specs"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/_workspaces/handoff/v9_answerability_compact_pilot/expanded_outputs"),
    )
    parser.add_argument("--glob", type=str, default="batch_*.jsonl")
    return parser.parse_args()


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected JSON object")
    return data


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
                raise ValueError(f"{path}:{line_no}: expected JSON object")
            rows.append(row)
    return rows


def _slot_map(batch_dir: Path) -> dict[str, dict[str, Any]]:
    slots: dict[str, dict[str, Any]] = {}
    for path in sorted(batch_dir.glob("batch_*.json")):
        payload = _read_json(path)
        for slot in payload.get("slots", []):
            if isinstance(slot, dict) and isinstance(slot.get("case_id"), str):
                slots[str(slot["case_id"])] = slot
    return slots


def _expected_ids(batch_dir: Path, output_path: Path) -> set[str]:
    payload = _read_json(batch_dir / f"{output_path.stem}.json")
    return {str(slot["case_id"]) for slot in payload.get("slots", [])}


def _clamp(value: Any, default: float) -> float:
    if isinstance(value, bool):
        return default
    if isinstance(value, int | float):
        return max(0.0, min(1.0, float(value)))
    return default


def _text(value: Any, default: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def _str_list(value: Any, default: list[str] | None = None) -> list[str]:
    if isinstance(value, list):
        clean = [str(item).strip() for item in value if str(item).strip()]
        if clean:
            return clean
    return list(default or [])


def _plan_block(row: dict[str, Any]) -> dict[str, Any]:
    plan = row.get("plan") or row.get("semantic_plan")
    if not isinstance(plan, dict):
        raise ValueError(f"{row.get('case_id')}: plan must be an object")
    return plan


def _digit_context_count(contexts: list[dict[str, Any]]) -> int:
    return sum(
        1 for context in contexts if any(ch.isdigit() for ch in str(context.get("text", "")))
    )


def _authority_spread(contexts: list[dict[str, Any]]) -> float:
    scores = [
        float(context["authority_score"])
        for context in contexts
        if isinstance(context.get("authority_score"), int | float)
        and not isinstance(context.get("authority_score"), bool)
    ]
    if len(scores) < 2:
        return 0.0
    return max(scores) - min(scores)


def _canonical_pattern_alias(raw: str) -> str:
    aliases = {
        "definition_boundary_dispute": "definitional_conflict",
        "definition_boundary_conflict": "definitional_conflict",
        "classification_conflict": "definitional_conflict",
        "candidate_conflict": "factual_contradiction",
        "value_conflict": "factual_contradiction",
        "source_authority_conflict": "authority_conflict",
        "authority_disagreement": "authority_conflict",
        "set_membership_conflict": "factual_contradiction",
        "list_conflict": "factual_contradiction",
    }
    return aliases.get(raw, raw)


def _pick_taxonomy_pattern(
    slot: dict[str, Any], plan: dict[str, Any], contexts: list[dict[str, Any]]
) -> str:
    cls = GovernanceClass(str(slot["governance_class"]))
    allowed = {pattern.value for pattern in patterns_of(cls)}
    raw = _canonical_pattern_alias(str(plan.get("taxonomy_pattern") or "").strip())
    if raw in allowed:
        if raw == "authority_conflict" and _authority_spread(contexts) < 0.2:
            return "factual_contradiction"
        if raw == "numerical_conflict" and _digit_context_count(contexts) < 2:
            return "factual_contradiction"
        if raw == "quantitative_consensus" and _digit_context_count(contexts) < 2:
            return "multi_source_corroboration"
        return raw
    if cls == GovernanceClass.DISPUTED:
        text = " ".join(
            [
                str(plan.get("query") or ""),
                str(plan.get("evidence_chain_reasoning") or ""),
                " ".join(str(context.get("text") or "") for context in contexts),
            ]
        ).lower()
        if "definition" in text or "classification" in text or "meaning" in text:
            return "definitional_conflict"
        if "scope" in text or "jurisdiction" in text or "cohort" in text:
            return "scope_conflict"
        if "authority" in text and _authority_spread(contexts) >= 0.2:
            return "authority_conflict"
        if _digit_context_count(contexts) >= 2:
            return "numerical_conflict"
        return "factual_contradiction"
    if cls == GovernanceClass.TRUSTWORTHY:
        return "multi_source_corroboration"
    return sorted(allowed)[0]


def _default_near_miss(governance_class: str) -> str:
    if governance_class == "TRUSTWORTHY":
        return "DISPUTED"
    return "TRUSTWORTHY"


def _category(governance_class: str, scores: dict[str, Any]) -> str:
    if governance_class == "ABSTAIN":
        return "abstention"
    if governance_class == "DISPUTED":
        return "dispute"
    risk = _clamp(scores.get("false_trustworthy_risk"), 0.14)
    return "trustworthy_hedged" if risk >= 0.20 else "trustworthy_direct"


def _confidence_level(governance_class: str, scores: dict[str, Any]) -> str:
    if governance_class == "TRUSTWORTHY":
        basis = _clamp(scores.get("evidence_sufficiency"), 0.84)
    elif governance_class == "DISPUTED":
        basis = _clamp(scores.get("conflict_density"), 0.82)
    else:
        basis = _clamp(scores.get("retrieval_retry_value"), 0.84)
    if basis >= 0.82:
        return "high"
    if basis >= 0.62:
        return "medium"
    return "borderline"


def _contexts(plan: dict[str, Any]) -> list[dict[str, Any]]:
    raw_contexts = plan.get("contexts")
    if not isinstance(raw_contexts, list) or not raw_contexts:
        raise ValueError("plan.contexts must be a non-empty list")
    contexts: list[dict[str, Any]] = []
    for idx, raw in enumerate(raw_contexts[:3], start=1):
        if not isinstance(raw, dict):
            raise ValueError("each context must be an object")
        cid = _text(raw.get("id"), f"ctx_{idx:03d}")
        temporality = raw.get("temporality")
        if not isinstance(temporality, dict):
            temporality = {}
        contexts.append(
            {
                "id": cid,
                "text": _text(raw.get("text"), f"Retrieved context {idx}."),
                "authority_score": _clamp(raw.get("authority_score"), 0.82),
                "authority_signal": _text(raw.get("authority_signal"), "domain_expert"),
                "temporality": {
                    "is_time_sensitive": bool(temporality.get("is_time_sensitive", False)),
                    "anchor_period": _text(
                        temporality.get("anchor_period"), "case-specific evidence"
                    ),
                    "staleness_risk": _text(temporality.get("staleness_risk"), "low"),
                },
                "summary": _text(raw.get("summary"), "Relevant retrieved evidence."),
                "relevance_to_query": _clamp(raw.get("relevance_to_query"), 0.88),
                "boundary_quality": _clamp(raw.get("boundary_quality"), 0.86),
            }
        )
    return contexts


def _label_object(
    kind: str, rationale: str, signals: list[str], *, confidence: float
) -> dict[str, Any]:
    return {
        "kind": kind,
        "confidence": confidence,
        "rationale": rationale,
        "signals": signals,
    }


def _retrieval_control(
    slot: dict[str, Any], plan: dict[str, Any], governance_class: str
) -> dict[str, Any]:
    raw = plan.get("retrieval_control")
    if not isinstance(raw, dict):
        raw = {}
    allowed_shapes = set(slot.get("allowed_detailed_answerability_shapes") or [])
    answer_shape = str(raw.get("answerability_shape") or "").strip()
    if answer_shape not in allowed_shapes:
        answer_shape = sorted(allowed_shapes)[0]
    if answer_shape not in ANSWERABILITY_SHAPES:
        answer_shape = sorted(allowed_shapes)[0]

    defaults = {
        "TRUSTWORTHY": ("answer_now", "none", 0.16),
        "DISPUTED": ("resolve_conflict", "conflicting_values", 0.72),
        "ABSTAIN": ("retrieve_more", "missing_specific_fact", 0.82),
    }
    action_default, gap_default, severity_default = defaults[governance_class]
    action = str(raw.get("retrieval_action") or action_default).strip()
    if action not in RETRIEVAL_ACTIONS:
        action = action_default
    gap = str(raw.get("gap_type") or gap_default).strip()
    if gap not in GAP_TYPES:
        gap = gap_default
    modality = str(raw.get("preferred_retrieval_modality") or "unstructured_text").strip()
    if modality not in RETRIEVAL_MODALITIES:
        modality = "unstructured_text"
    severity = _clamp(raw.get("evidence_failure_severity"), severity_default)
    rationale = _text(raw.get("rationale"), "Retrieval-control label follows the evidence state.")
    signals = _str_list(
        raw.get("signals"),
        [f"class={governance_class}", f"shape={answer_shape}", f"gap={gap}"],
    )
    confidence = _clamp(raw.get("confidence"), 0.82)
    return {
        "retrieval_action": _label_object(action, rationale, signals, confidence=confidence),
        "gap_type": _label_object(gap, rationale, signals, confidence=confidence),
        "answerability_shape": _label_object(
            answer_shape, rationale, signals, confidence=confidence
        ),
        "preferred_retrieval_modality": _label_object(
            modality,
            rationale,
            signals,
            confidence=confidence,
        ),
        "evidence_failure_severity": {
            "score": severity,
            "confidence": confidence,
            "rationale": rationale,
            "signals": signals,
        },
        "labeler": "codex_subagent_v9_compact_plan_expander",
    }


def _query_contract(plan: dict[str, Any]) -> dict[str, Any]:
    raw = plan.get("query_contract")
    if not isinstance(raw, dict):
        raw = {}
    kind = str(raw.get("kind") or "evidence_sufficiency").strip()
    if kind not in QUERY_CONTRACTS:
        kind = "evidence_sufficiency"
    return {
        "kind": kind,
        "confidence": _clamp(raw.get("confidence"), 0.84),
        "rationale": _text(
            raw.get("rationale"), "The query contract follows the requested answer form."
        ),
        "signals": _str_list(raw.get("signals"), [f"contract={kind}"]),
        "labeler": "codex_subagent_v9_compact_plan_expander",
    }


def _governance(governance_class: str, plan: dict[str, Any]) -> dict[str, Any]:
    scores = plan.get("scores")
    if not isinstance(scores, dict):
        scores = {}
    probs = DEFAULT_PROBS[governance_class].copy()
    raw_probs = plan.get("class_probabilities")
    if isinstance(raw_probs, dict):
        probs["abstain"] = _clamp(raw_probs.get("abstain"), probs["abstain"])
        probs["disputed"] = _clamp(raw_probs.get("disputed"), probs["disputed"])
        probs["trustworthy"] = _clamp(raw_probs.get("trustworthy"), probs["trustworthy"])
    total = sum(probs.values())
    if total > 0:
        probs = {key: value / total for key, value in probs.items()}
    defaults = DEFAULT_SCORES[governance_class]
    nearest = _text(plan.get("near_miss_class"), _default_near_miss(governance_class))
    if nearest == governance_class:
        nearest = _default_near_miss(governance_class)
    return {
        "classification": governance_class,
        "abstain": probs["abstain"],
        "disputed": probs["disputed"],
        "trustworthy": probs["trustworthy"],
        "confidence": max(probs.values()),
        "grounding": _clamp(scores.get("grounding"), defaults["grounding"]),
        "conflict_density": _clamp(scores.get("conflict_density"), defaults["conflict_density"]),
        "evidence_sufficiency": _clamp(
            scores.get("evidence_sufficiency"),
            defaults["evidence_sufficiency"],
        ),
        "boundary_proximity": {
            "nearest_class": nearest,
            "distance": _clamp(scores.get("boundary_distance"), 0.22),
        },
        "domain_familiarity": _clamp(
            scores.get("domain_familiarity"), defaults["domain_familiarity"]
        ),
        "false_trustworthy_risk": _clamp(
            scores.get("false_trustworthy_risk"),
            defaults["false_trustworthy_risk"],
        ),
        "hallucination_pressure": _clamp(
            scores.get("hallucination_pressure"),
            defaults["hallucination_pressure"],
        ),
        "retrieval_retry_value": _clamp(
            scores.get("retrieval_retry_value"),
            defaults["retrieval_retry_value"],
        ),
        "human_escalation_score": _clamp(
            scores.get("human_escalation_score"),
            defaults["human_escalation_score"],
        ),
        "query_evidence_alignment": _clamp(
            scores.get("query_evidence_alignment"),
            defaults["query_evidence_alignment"],
        ),
        "answer_coverage": _clamp(scores.get("answer_coverage"), defaults["answer_coverage"]),
        "evidence_bias_score": _clamp(
            scores.get("evidence_bias_score"),
            defaults["evidence_bias_score"],
        ),
    }


def _grounding_targets(plan: dict[str, Any], contexts: list[dict[str, Any]]) -> dict[str, Any]:
    context_ids = {str(context["id"]) for context in contexts}
    gold = _text(plan.get("gold_answer"), "The retrieved evidence supports the answer.")
    sentences = []
    raw_sentences = plan.get("grounding_sentences")
    if isinstance(raw_sentences, list):
        for raw in raw_sentences:
            if not isinstance(raw, dict):
                continue
            attributions = [
                item for item in _str_list(raw.get("attributions")) if item in context_ids
            ]
            sentences.append(
                {
                    "text": _text(raw.get("text"), gold),
                    "attributions": attributions or [next(iter(context_ids))],
                }
            )
    if not sentences:
        sentences = [{"text": gold, "attributions": [next(iter(context_ids))]}]
    return {"gold_answer": gold, "sentences": sentences}


def _evaluation(plan: dict[str, Any], governance_class: str) -> dict[str, Any]:
    raw = plan.get("evaluation")
    if not isinstance(raw, dict):
        raw = {}
    default_required = ["supported"] if governance_class == "TRUSTWORTHY" else []
    default_forbidden = (
        ["insufficient evidence", "cannot determine"]
        if governance_class == "TRUSTWORTHY"
        else ["unsupported answer", "pretend the evidence is sufficient"]
    )
    return {
        "mode": "governance",
        "check_mode_match": True,
        "required_elements": _str_list(raw.get("required_elements"), default_required),
        "forbidden_claims": _str_list(raw.get("forbidden_claims"), default_forbidden),
        "forbidden_elements": _str_list(raw.get("forbidden_elements"), []),
        "config": {
            "allowed_phrases": [],
            "case_insensitive": True,
            "min_required": 1,
            "use_regex": True,
        },
    }


def _expand_case(case_id: str, slot: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    governance_class = str(slot["governance_class"])
    contexts = _contexts(plan)
    pattern = _pick_taxonomy_pattern(slot, plan, contexts)
    pattern_enum = TaxonomyPattern(pattern)
    query = _text(plan.get("query"), "What answer is supported by the retrieved evidence?")
    rewritten = _text(plan.get("query_rewritten"), query)
    scores = plan.get("scores") if isinstance(plan.get("scores"), dict) else {}
    governance = _governance(governance_class, plan)
    retrieval_control = _retrieval_control(slot, plan, governance_class)
    # This protects against expander defaults drifting away from the target cell.
    collapsed = collapse_answerability_shape(retrieval_control["answerability_shape"]["kind"]).value
    if collapsed != slot["collapsed_answerability_shape"]:
        raise ValueError(f"{case_id}: answerability shape does not collapse to target")

    meta = {
        "dataset_version": "v9",
        "difficulty": slot["difficulty"],
        "category": _category(governance_class, scores),
        "confidence_level": _confidence_level(governance_class, scores),
        "near_miss_class": governance["boundary_proximity"]["nearest_class"],
        "near_miss_reason": _text(
            plan.get("near_miss_reason"),
            "This row is near a neighboring governance class but the evidence state fixes the target label.",
        ),
        "modality": _text(plan.get("modality"), "unstructured"),
    }
    if governance_class == "TRUSTWORTHY":
        meta["grounding_targets"] = _grounding_targets(plan, contexts)

    return {
        "id": case_id,
        "version": "fitz-gov-9.0",
        "input": {
            "query": query,
            "query_rewritten": rewritten,
            "contexts": contexts,
            "evidence_chain": {
                "order": [str(context["id"]) for context in contexts],
                "reasoning": _text(
                    plan.get("evidence_chain_reasoning"),
                    "Read the retrieved contexts together to judge the evidence state.",
                ),
            },
        },
        "governance": governance,
        "taxonomy": {
            "governance_class": governance_class,
            "pattern": pattern,
            "pattern_description": PATTERN_DESCRIPTIONS[pattern_enum],
            "cell_id": f"{pattern}__{slot['domain']}__{slot['difficulty']}",
        },
        "routing": {
            "expert_fired": slot["domain"],
            "secondary_expert": None,
            "routing_confidence": _clamp(plan.get("routing_confidence"), 0.86),
            "query_contract": _query_contract(plan),
            "retrieval_control": retrieval_control,
        },
        "meta": meta,
        "evaluation": _evaluation(plan, governance_class),
    }


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    slots = _slot_map(args.batch_dir)
    files = sorted(args.plan_dir.glob(args.glob))
    print("=== Expand V9 compact semantic plans ===")
    print(f"Plan dir : {args.plan_dir}")
    print(f"Batch dir: {args.batch_dir}")
    print(f"Out dir  : {args.out_dir}")
    print(f"Files    : {len(files)}")

    total = 0
    bad = 0
    for path in files:
        try:
            rows = _read_jsonl(path)
        except ValueError as exc:
            print(f"READ FAIL {exc}", file=sys.stderr)
            bad += 1
            continue
        expected = _expected_ids(args.batch_dir, path)
        ids = [row.get("case_id") for row in rows]
        got = {str(case_id) for case_id in ids if isinstance(case_id, str)}
        dupes = [case_id for case_id, count in Counter(ids).items() if count > 1]
        if dupes or got != expected:
            missing = sorted(expected - got)
            extra = sorted(got - expected)
            print(
                f"ID SET FAIL {path}: dupes={dupes[:5]} missing={missing[:5]} extra={extra[:5]}",
                file=sys.stderr,
            )
            bad += 1
            continue
        out_rows: list[dict[str, Any]] = []
        for row in rows:
            case_id = str(row["case_id"])
            try:
                plan = _plan_block(row)
                out_rows.append(
                    {"case_id": case_id, "case": _expand_case(case_id, slots[case_id], plan)}
                )
            except Exception as exc:  # noqa: BLE001 - report all row-level generation failures.
                print(f"EXPAND FAIL {case_id}: {exc}", file=sys.stderr)
                bad += 1
        out_path = args.out_dir / path.name
        with out_path.open("w", encoding="utf-8", newline="\n") as handle:
            for row in out_rows:
                handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
                handle.write("\n")
        total += len(out_rows)
        print(f"  {out_path}: {len(out_rows)} rows")

    print(f"Expanded : {total}")
    print(f"Rejected : {bad}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
