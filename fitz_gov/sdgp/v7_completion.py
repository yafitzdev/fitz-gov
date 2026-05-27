"""V7 training-schema completion.

V7 generation originally accepted "cell-valid" rows where the query,
contexts, label, taxonomy, and routing were correct, but many rich V6/MoE
training fields were optional. This module turns those rows into complete
training rows without changing the locked case semantics.
"""

from __future__ import annotations

import json
import re
import textwrap
from dataclasses import dataclass, field
from typing import Any, Iterable

from .completeness import audit_case_completeness
from .llm_enrich import _clamp01, _strip_thinking
from .modality import set_modality
from .providers import GenerateRequest, Provider
from .taxonomy import PATTERN_DESCRIPTIONS, GovernanceClass, TaxonomyPattern

_CLASS_PROBS: dict[GovernanceClass, dict[str, float]] = {
    GovernanceClass.ABSTAIN: {"abstain": 0.85, "disputed": 0.08, "trustworthy": 0.07},
    GovernanceClass.DISPUTED: {"abstain": 0.10, "disputed": 0.80, "trustworthy": 0.10},
    GovernanceClass.TRUSTWORTHY: {"abstain": 0.06, "disputed": 0.09, "trustworthy": 0.85},
}

V7_COMPLETION_SYSTEM = (
    "You complete already-generated fitz-gov V7 RAG governance cases so they "
    "match the full V6/MoE training schema. The query, contexts, classification, "
    "taxonomy pattern, cell_id, and expert domain are LOCKED. Do not relabel, "
    "rewrite evidence, or invent new contexts. Fill only metadata, per-context "
    "annotations, governance scores, routing confidence, evidence chains, and "
    "TRUSTWORTHY grounding targets. Output one JSON object only."
)


_PROMPT_TEMPLATE = textwrap.dedent("""\
    ## Existing V7 case

    ```json
    {case_json}
    ```

    ## Missing / incomplete fields

    {missing_fields}

    ## Locked facts

    - Classification: **{classification}**
    - Taxonomy pattern: **{pattern}**
    - Cell id: **{cell_id}**
    - Expert domain: **{expert_domain}**
    - Difficulty: **{difficulty}**

    Do not change those fields or the query/context text.

    ## Output JSON

    Return a single JSON object with this overlay shape:

    {{
      "input": {{
        "query_rewritten": "<same meaning, sharpened for retrieval>",
        "contexts": [
          {{
            "id": "<chunk id>",
            "summary": "<one-sentence semantic summary, not a truncation>",
            "relevance_to_query": <0.0-1.0>,
            "temporality": {{
              "is_time_sensitive": <true|false>,
              "anchor_period": "<current | none | explicit year/quarter/date range>",
              "staleness_risk": "<none | low | medium | high>"
            }},
            "boundary_quality": <0.0-1.0>
          }}
        ],
        "evidence_chain": {{
          "order": ["<chunk id>", "..."],
          "reasoning": "<one sentence explaining the reading order>"
        }}
      }},

      "governance": {{
        "abstain": <0.0-1.0>,
        "disputed": <0.0-1.0>,
        "trustworthy": <0.0-1.0>,
        "confidence": <0.0-1.0>,
        "grounding": <0.0-1.0>,
        "conflict_density": <0.0-1.0>,
        "evidence_sufficiency": <0.0-1.0>,
        "boundary_proximity": {{
          "nearest_class": "<ABSTAIN|DISPUTED|TRUSTWORTHY, but not the actual class>",
          "distance": <0.0-1.0>
        }},
        "domain_familiarity": <0.0-1.0>,
        "false_trustworthy_risk": <0.0-1.0>,
        "hallucination_pressure": <0.0-1.0>,
        "retrieval_retry_value": <0.0-1.0>,
        "human_escalation_score": <0.0-1.0>,
        "query_evidence_alignment": <0.0-1.0>,
        "answer_coverage": <0.0-1.0>,
        "evidence_bias_score": <0.0-1.0>
      }},

      "routing": {{
        "secondary_expert": null,
        "routing_confidence": <0.0-1.0>
      }},

      "evaluation": {{
        "mode": "governance",
        "check_mode_match": true,
        "required_elements": ["<answer-quality requirements, if useful>"],
        "forbidden_claims": ["<unsupported claims to forbid, if useful>"],
        "forbidden_elements": ["<unsupported answer elements to forbid, if useful>"]
      }},

      "meta": {{
        "modality": "unstructured",
        "category": "<abstention | dispute | trustworthy_hedged | trustworthy_direct>",
        "confidence_level": "<high | medium | borderline>",
        "near_miss_class": "<ABSTAIN|DISPUTED|TRUSTWORTHY, but not the actual class>",
        "near_miss_reason": "<specific one-sentence boundary explanation>",
        "grounding_targets": {{
          "gold_answer": "<TRUSTWORTHY only: 2-6 sentence grounded answer>",
          "sentences": [
            {{"text": "<sentence>", "attributions": ["<chunk id>", "..."]}}
          ]
        }}
      }}
    }}

    Conditional rules:
    - Omit `input.evidence_chain` for single-context cases only.
    - Omit `meta.grounding_targets` unless classification is TRUSTWORTHY.
    - All scores must be calibrated to the actual query/context relationship.
    - For ABSTAIN, hallucination_pressure and retrieval_retry_value are usually high.
    - For DISPUTED, conflict_density is high and evidence_sufficiency is moderate.
    - For TRUSTWORTHY, conflict_density and false_trustworthy_risk are low.

    Output the JSON object only. No prose around it.
""")


_FENCED = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)
_FIRST = re.compile(r"\{.*\}", re.DOTALL)


@dataclass(slots=True)
class V7CompletionResult:
    case_id: str
    fields_filled: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return bool(self.fields_filled)


def case_needs_v7_completion(case: dict[str, Any]) -> bool:
    """True if this row is missing any full training-schema field."""
    return bool(audit_case_completeness(case))


def cases_needing_v7_completion(cases: Iterable[dict[str, Any]]) -> list[str]:
    return [str(c["id"]) for c in cases if "id" in c and case_needs_v7_completion(c)]


def build_v7_completion_prompt(case: dict[str, Any]) -> str:
    """Build a prompt that asks for a full V7 training-schema overlay."""
    missing = audit_case_completeness(case)
    missing_lines = "\n".join(f"- `{i.path}` — {i.message}" for i in missing[:80])
    if len(missing) > 80:
        missing_lines += f"\n- ... {len(missing) - 80} more"
    if not missing_lines:
        missing_lines = "- None detected; refresh the schema values consistently."

    compact = {
        "id": case.get("id"),
        "input": {
            "query": case.get("input", {}).get("query"),
            "contexts": [
                {
                    "id": c.get("id"),
                    "text": c.get("text", ""),
                    "authority_score": c.get("authority_score"),
                    "authority_signal": c.get("authority_signal"),
                }
                for c in case.get("input", {}).get("contexts", [])
                if isinstance(c, dict)
            ],
        },
        "governance": {
            "classification": case.get("governance", {}).get("classification"),
            "abstain": case.get("governance", {}).get("abstain"),
            "disputed": case.get("governance", {}).get("disputed"),
            "trustworthy": case.get("governance", {}).get("trustworthy"),
        },
        "taxonomy": case.get("taxonomy", {}),
        "routing": case.get("routing", {}),
        "meta": {
            "difficulty": case.get("meta", {}).get("difficulty"),
            "dataset_version": case.get("meta", {}).get("dataset_version"),
        },
    }
    taxonomy = case.get("taxonomy", {}) if isinstance(case.get("taxonomy"), dict) else {}
    routing = case.get("routing", {}) if isinstance(case.get("routing"), dict) else {}
    meta = case.get("meta", {}) if isinstance(case.get("meta"), dict) else {}
    return _PROMPT_TEMPLATE.format(
        case_json=json.dumps(compact, indent=2, ensure_ascii=False),
        missing_fields=missing_lines,
        classification=case.get("governance", {}).get("classification", "?"),
        pattern=taxonomy.get("pattern", "?"),
        cell_id=taxonomy.get("cell_id", "?"),
        expert_domain=routing.get("expert_fired", "?"),
        difficulty=meta.get("difficulty", "?"),
    )


def parse_v7_completion_response(raw: str) -> dict[str, Any]:
    if not raw or not raw.strip():
        raise ValueError("empty v7-completion response")
    text = _strip_thinking(raw.strip())
    if not text:
        raise ValueError("v7-completion response contained only thinking blocks")
    candidates = (
        text,
        *(
            m.group(1) if m and m.lastindex else m.group(0)
            for m in (_FENCED.search(text), _FIRST.search(text))
            if m
        ),
    )
    for candidate in candidates:
        try:
            obj = json.loads(candidate)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            continue
    raise ValueError(f"could not extract JSON from v7-completion response (len={len(raw)})")


def _set_if_present(
    target: dict[str, Any],
    key: str,
    value: Any,
    res: V7CompletionResult,
    path: str,
    *,
    overwrite: bool,
) -> None:
    if value is None:
        return
    if key in target and target[key] not in (None, "", "<TODO_LLM>") and not overwrite:
        return
    target[key] = value
    res.fields_filled.append(path)


def _set_score(
    target: dict[str, Any],
    key: str,
    value: Any,
    res: V7CompletionResult,
    path: str,
    *,
    overwrite: bool,
) -> None:
    score = _clamp01(value)
    if score is None:
        return
    _set_if_present(target, key, round(score, 3), res, path, overwrite=overwrite)


def _context_ids(case: dict[str, Any]) -> set[str]:
    return {
        c.get("id")
        for c in case.get("input", {}).get("contexts", [])
        if isinstance(c, dict) and c.get("id")
    }


def _fill_probability_triplet(gov: dict[str, Any], res: V7CompletionResult) -> None:
    for key in ("abstain", "disputed", "trustworthy"):
        if gov.get(key) not in (None, "", "<TODO_LLM>"):
            continue
        alias = _clamp01(gov.get(f"{key}_score"))
        if alias is not None:
            gov[key] = round(alias, 3)
            res.fields_filled.append(f"governance.{key}")

    try:
        cls = GovernanceClass(gov.get("classification"))
    except (TypeError, ValueError):
        return
    defaults = _CLASS_PROBS[cls]
    for key, value in defaults.items():
        if gov.get(key) in (None, "", "<TODO_LLM>"):
            gov[key] = value
            res.fields_filled.append(f"governance.{key}")


def _locked_defaults(case: dict[str, Any], res: V7CompletionResult) -> None:
    case["version"] = "fitz-gov-7.0"
    case.setdefault("meta", {})["dataset_version"] = "v7"
    set_modality(case)
    _fill_probability_triplet(case.setdefault("governance", {}), res)

    evaluation = case.setdefault("evaluation", {})
    defaults = {
        "mode": "governance",
        "check_mode_match": True,
        "required_elements": [],
        "forbidden_claims": [],
        "forbidden_elements": [],
    }
    for key, value in defaults.items():
        if key not in evaluation or evaluation[key] in (None, "", "<TODO_LLM>"):
            evaluation[key] = value.copy() if isinstance(value, list) else value
            res.fields_filled.append(f"evaluation.{key}")

    taxonomy = case.setdefault("taxonomy", {})
    pattern_s = taxonomy.get("pattern")
    try:
        pattern = TaxonomyPattern(pattern_s)
    except ValueError:
        pattern = None
    if pattern is not None and not taxonomy.get("pattern_description"):
        taxonomy["pattern_description"] = PATTERN_DESCRIPTIONS[pattern]
        res.fields_filled.append("taxonomy.pattern_description")


def _merge_contexts(
    case: dict[str, Any],
    payload: dict[str, Any],
    res: V7CompletionResult,
    *,
    overwrite: bool,
) -> None:
    payload_contexts = payload.get("input", {}).get("contexts") or payload.get("contexts") or []
    if not isinstance(payload_contexts, list):
        return
    by_id = {
        c.get("id"): c
        for c in payload_contexts
        if isinstance(c, dict) and isinstance(c.get("id"), str)
    }
    contexts = case.setdefault("input", {}).setdefault("contexts", [])
    for idx, chunk in enumerate(contexts):
        if not isinstance(chunk, dict):
            continue
        source = by_id.get(chunk.get("id"))
        if not isinstance(source, dict):
            continue
        prefix = f"input.contexts[{idx}]"
        _set_if_present(
            chunk,
            "summary",
            source.get("summary"),
            res,
            f"{prefix}.summary",
            overwrite=overwrite,
        )
        _set_score(
            chunk,
            "relevance_to_query",
            source.get("relevance_to_query"),
            res,
            f"{prefix}.relevance_to_query",
            overwrite=overwrite,
        )
        _set_score(
            chunk,
            "boundary_quality",
            source.get("boundary_quality"),
            res,
            f"{prefix}.boundary_quality",
            overwrite=overwrite,
        )
        temporality = source.get("temporality")
        if isinstance(temporality, dict):
            target_temp = chunk.setdefault("temporality", {})
            for key in ("is_time_sensitive", "anchor_period", "staleness_risk"):
                _set_if_present(
                    target_temp,
                    key,
                    temporality.get(key),
                    res,
                    f"{prefix}.temporality.{key}",
                    overwrite=overwrite,
                )


def _merge_governance(
    case: dict[str, Any],
    payload: dict[str, Any],
    res: V7CompletionResult,
    *,
    overwrite: bool,
) -> None:
    gov_in = payload.get("governance") if isinstance(payload.get("governance"), dict) else {}
    gov = case.setdefault("governance", {})
    for key in (
        "abstain",
        "disputed",
        "trustworthy",
        "confidence",
        "grounding",
        "conflict_density",
        "evidence_sufficiency",
        "domain_familiarity",
        "false_trustworthy_risk",
        "hallucination_pressure",
        "retrieval_retry_value",
        "human_escalation_score",
        "query_evidence_alignment",
        "answer_coverage",
        "evidence_bias_score",
    ):
        _set_score(gov, key, gov_in.get(key), res, f"governance.{key}", overwrite=overwrite)

    bp_in = gov_in.get("boundary_proximity")
    if isinstance(bp_in, dict):
        bp = gov.setdefault("boundary_proximity", {})
        _set_if_present(
            bp,
            "nearest_class",
            bp_in.get("nearest_class"),
            res,
            "governance.boundary_proximity.nearest_class",
            overwrite=overwrite,
        )
        _set_score(
            bp,
            "distance",
            bp_in.get("distance"),
            res,
            "governance.boundary_proximity.distance",
            overwrite=overwrite,
        )


def _merge_evidence_chain(
    case: dict[str, Any],
    payload: dict[str, Any],
    res: V7CompletionResult,
    *,
    overwrite: bool,
) -> None:
    contexts = case.get("input", {}).get("contexts", []) or []
    if len(contexts) < 2:
        return
    input_in = payload.get("input") if isinstance(payload.get("input"), dict) else {}
    chain = input_in.get("evidence_chain")
    if not isinstance(chain, dict):
        return
    valid_ids = _context_ids(case)
    order = chain.get("order")
    reasoning = chain.get("reasoning")
    if not isinstance(order, list):
        return
    clean_order = [x for x in order if isinstance(x, str) and x in valid_ids]
    if not clean_order:
        return
    target = case.setdefault("input", {})
    if "evidence_chain" in target and not overwrite:
        return
    target["evidence_chain"] = {
        "order": clean_order,
        "reasoning": reasoning.strip() if isinstance(reasoning, str) else "",
    }
    res.fields_filled.append("input.evidence_chain")


def _merge_meta(
    case: dict[str, Any],
    payload: dict[str, Any],
    res: V7CompletionResult,
    *,
    overwrite: bool,
) -> None:
    meta_in = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
    meta = case.setdefault("meta", {})
    for key in (
        "category",
        "confidence_level",
        "near_miss_class",
        "near_miss_reason",
    ):
        _set_if_present(meta, key, meta_in.get(key), res, f"meta.{key}", overwrite=overwrite)

    if case.get("governance", {}).get("classification") == GovernanceClass.TRUSTWORTHY.value:
        targets = meta_in.get("grounding_targets")
        if not isinstance(targets, dict):
            return
        gold = targets.get("gold_answer")
        sentences = targets.get("sentences")
        if not isinstance(gold, str) or not gold.strip() or not isinstance(sentences, list):
            return
        valid_ids = _context_ids(case)
        clean = []
        for sentence in sentences:
            if not isinstance(sentence, dict):
                continue
            text = sentence.get("text")
            attrs = sentence.get("attributions") or []
            if not isinstance(text, str) or not text.strip() or not isinstance(attrs, list):
                continue
            clean_attrs = [a for a in attrs if isinstance(a, str) and a in valid_ids]
            clean.append({"text": text.strip(), "attributions": clean_attrs})
        if clean and ("grounding_targets" not in meta or overwrite):
            meta["grounding_targets"] = {"gold_answer": gold.strip(), "sentences": clean}
            res.fields_filled.append("meta.grounding_targets")


def _merge_routing(
    case: dict[str, Any],
    payload: dict[str, Any],
    res: V7CompletionResult,
    *,
    overwrite: bool,
) -> None:
    routing_in = payload.get("routing") if isinstance(payload.get("routing"), dict) else {}
    routing = case.setdefault("routing", {})
    _set_if_present(
        routing,
        "secondary_expert",
        routing_in.get("secondary_expert"),
        res,
        "routing.secondary_expert",
        overwrite=overwrite,
    )
    _set_score(
        routing,
        "routing_confidence",
        routing_in.get("routing_confidence"),
        res,
        "routing.routing_confidence",
        overwrite=overwrite,
    )


def _list_str(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            out.append(item.strip())
    return out


def _merge_evaluation(
    case: dict[str, Any],
    payload: dict[str, Any],
    res: V7CompletionResult,
    *,
    overwrite: bool,
) -> None:
    evaluation_in = payload.get("evaluation") if isinstance(payload.get("evaluation"), dict) else {}
    evaluation = case.setdefault("evaluation", {})
    _set_if_present(
        evaluation,
        "mode",
        evaluation_in.get("mode"),
        res,
        "evaluation.mode",
        overwrite=overwrite,
    )
    _set_if_present(
        evaluation,
        "check_mode_match",
        evaluation_in.get("check_mode_match"),
        res,
        "evaluation.check_mode_match",
        overwrite=overwrite,
    )
    for key in ("required_elements", "forbidden_claims", "forbidden_elements"):
        values = _list_str(evaluation_in.get(key))
        if values and (overwrite or not _list_str(evaluation.get(key))):
            evaluation[key] = values
            res.fields_filled.append(f"evaluation.{key}")


def merge_v7_completion(
    case: dict[str, Any],
    payload: dict[str, Any],
    *,
    overwrite: bool = False,
) -> V7CompletionResult:
    """Merge a completion overlay into `case` in place."""
    res = V7CompletionResult(case_id=str(case.get("id", "<no id>")))
    _locked_defaults(case, res)

    input_in = payload.get("input") if isinstance(payload.get("input"), dict) else {}
    _set_if_present(
        case.setdefault("input", {}),
        "query_rewritten",
        input_in.get("query_rewritten") or payload.get("query_rewritten"),
        res,
        "input.query_rewritten",
        overwrite=overwrite,
    )
    _merge_contexts(case, payload, res, overwrite=overwrite)
    _merge_governance(case, payload, res, overwrite=overwrite)
    _merge_evidence_chain(case, payload, res, overwrite=overwrite)
    _merge_routing(case, payload, res, overwrite=overwrite)
    _merge_evaluation(case, payload, res, overwrite=overwrite)
    _merge_meta(case, payload, res, overwrite=overwrite)
    return res


def complete_case_with_provider(
    case: dict[str, Any],
    provider: Provider,
    *,
    max_tokens: int = 5000,
    temperature: float = 0.2,
    overwrite: bool = False,
) -> V7CompletionResult:
    prompt = build_v7_completion_prompt(case)
    raw = provider.generate(
        GenerateRequest(
            prompt=prompt,
            system=V7_COMPLETION_SYSTEM,
            max_tokens=max_tokens,
            temperature=temperature,
            metadata={"case_id": case.get("id"), "phase": "v7-training-completion"},
        )
    )
    payload = parse_v7_completion_response(raw)
    return merge_v7_completion(case, payload, overwrite=overwrite)
