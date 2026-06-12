"""Prepare compact semantic-plan batches for a V9 generation pilot.

This is a speed/quality experiment. Subagents generate compact semantic plans
for V9 rows; `sdgp_expand_v9_compact_plans.py` expands those plans into the
canonical SDGP JSON row shape. The active vault is never mutated here.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.retrieval_control_gap_detector import (  # noqa: E402
    detailed_answerability_shapes_for,
    parse_retrieval_control_cell_id,
)
from fitz_gov.sdgp.taxonomy import (  # noqa: E402
    PATTERN_DESCRIPTIONS,
    GovernanceClass,
    patterns_of,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-batch-dir",
        type=Path,
        default=Path("data/_workspaces/handoff/v9_answerability/subagent_batches"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/_workspaces/handoff/v9_answerability_compact_pilot/batch_specs"),
    )
    parser.add_argument(
        "--outputs-dir",
        type=Path,
        default=Path(
            "data/_workspaces/handoff/v9_answerability_compact_pilot/semantic_plan_outputs"
        ),
    )
    parser.add_argument("--start-source-batch", type=int, default=100)
    parser.add_argument("--total-slots", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=25)
    parser.add_argument("--start-output-batch", type=int, default=100)
    return parser.parse_args()


def _batch_num(path: Path) -> int | None:
    match = re.fullmatch(r"batch_(\d+)", path.stem)
    return int(match.group(1)) if match else None


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected JSON object")
    return data


def _source_slots(
    source_batch_dir: Path, *, start_batch: int, total_slots: int
) -> list[dict[str, Any]]:
    slots: list[dict[str, Any]] = []
    numbered = []
    for path in source_batch_dir.glob("batch_*.json"):
        num = _batch_num(path)
        if num is not None and num >= start_batch:
            numbered.append((num, path))
    for _, path in sorted(numbered):
        payload = _read_json(path)
        for slot in payload.get("slots", []):
            if isinstance(slot, dict):
                clean = {k: v for k, v in slot.items() if k != "prompt"}
                slots.append(clean)
                if len(slots) >= total_slots:
                    return slots
    return slots


def _allowed_patterns_text(governance_class: str) -> str:
    cls = GovernanceClass(governance_class)
    return "\n".join(
        f"- {pattern.value}: {PATTERN_DESCRIPTIONS[pattern]}" for pattern in patterns_of(cls)
    )


def _compact_prompt(slot: dict[str, Any]) -> str:
    cell = parse_retrieval_control_cell_id(str(slot["v9_cell_id"]))
    allowed_shapes = detailed_answerability_shapes_for(cell.answerability_shape)
    return f"""Generate one compact semantic plan for a fitz-gov V9 row.

Return exactly one JSON object. Do not use markdown fences or prose.

The wrapper row will be built by a script. You must generate the meaning:
query, retrieved evidence, semantic labels, answer/abstain/conflict rationale,
grounding/evaluation hints, and score signals. Do not generate the full SDGP
wrapper.

Hard target:
- case_id: {slot["case_id"]}
- governance_class: {slot["governance_class"]}
- domain: {slot["domain"]}
- difficulty: {slot["difficulty"]}
- collapsed_answerability_shape: {slot["collapsed_answerability_shape"]}
- allowed answerability_shape values: {", ".join(allowed_shapes)}

Allowed taxonomy patterns for this governance class:
{_allowed_patterns_text(str(slot["governance_class"]))}

Output shape:
{{
  "case_id": "{slot["case_id"]}",
  "plan": {{
    "query": "...",
    "query_rewritten": "...",
    "contexts": [
      {{
        "text": "...",
        "summary": "...",
        "authority_signal": "official_primary|domain_expert|scholarly_reference|documentation|news_report|user_supplied|low_authority|unknown",
        "authority_score": 0.0,
        "relevance_to_query": 0.0,
        "boundary_quality": 0.0,
        "temporality": {{
          "is_time_sensitive": true,
          "anchor_period": "...",
          "staleness_risk": "none|low|medium|high"
        }}
      }}
    ],
    "evidence_chain_reasoning": "...",
    "taxonomy_pattern": "...",
    "query_contract": {{
      "kind": "evidence_sufficiency|structured_lookup|temporal_grounding|exhaustive_coverage|comparison_coverage|representative_overview",
      "rationale": "...",
      "signals": ["...", "..."]
    }},
    "retrieval_control": {{
      "retrieval_action": "answer_now|retrieve_more|broaden_search|resolve_conflict|ask_clarifying_question|structured_lookup",
      "gap_type": "none|missing_specific_fact|missing_timeframe|missing_comparison_side|missing_source_authority|conflicting_values|wrong_entity|wrong_version_or_scope|too_broad|incomplete_enumeration|unsupported_inference|ambiguous_query",
      "answerability_shape": "{next(iter(allowed_shapes))}",
      "preferred_retrieval_modality": "unstructured_text|structured_table|code|configuration|log_trace|pdf_layout|mixed",
      "evidence_failure_severity": 0.0,
      "rationale": "...",
      "signals": ["...", "..."]
    }},
    "scores": {{
      "evidence_sufficiency": 0.0,
      "conflict_density": 0.0,
      "query_evidence_alignment": 0.0,
      "answer_coverage": 0.0,
      "false_trustworthy_risk": 0.0,
      "retrieval_retry_value": 0.0,
      "hallucination_pressure": 0.0,
      "evidence_bias_score": 0.0
    }},
    "near_miss_class": "ABSTAIN|DISPUTED|TRUSTWORTHY",
    "near_miss_reason": "...",
    "gold_answer": "Only for TRUSTWORTHY; otherwise omit or leave empty.",
    "grounding_sentences": [
      {{"text": "Only for TRUSTWORTHY.", "attributions": ["ctx_001"]}}
    ],
    "evaluation": {{
      "required_elements": ["..."],
      "forbidden_claims": ["..."],
      "forbidden_elements": []
    }}
  }}
}}

Quality rules:
- Contexts must make the target governance class genuinely true.
- DISPUTED evidence must contain unresolved material incompatibility. Do not
  ask the user to explain why sources differ; ask for the single disputed answer.
- ABSTAIN evidence must be relevant but insufficient, wrong-scope, missing, or
  otherwise unable to support the requested answer.
- TRUSTWORTHY evidence must be sufficient and non-conflicting, with a grounded
  gold answer and sentence attributions.
- Use two contexts unless the target genuinely needs three. Keep text concise.
"""


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.outputs_dir.mkdir(parents=True, exist_ok=True)
    slots = _source_slots(
        args.source_batch_dir,
        start_batch=args.start_source_batch,
        total_slots=args.total_slots,
    )
    if len(slots) != args.total_slots:
        raise SystemExit(f"wanted {args.total_slots} slots, found {len(slots)}")

    print("=== Prepare V9 compact semantic-plan pilot ===")
    print(f"Source batch dir: {args.source_batch_dir}")
    print(f"Slots           : {len(slots)}")
    print(f"Batch size      : {args.batch_size}")
    print(f"Spec dir        : {args.out_dir}")
    print(f"Plan output dir : {args.outputs_dir}")

    for idx in range(0, len(slots), args.batch_size):
        batch_no = args.start_output_batch + idx // args.batch_size
        chunk = slots[idx : idx + args.batch_size]
        for slot in chunk:
            slot["prompt"] = _compact_prompt(slot)
        path = args.out_dir / f"batch_{batch_no:03d}.json"
        payload = {
            "batch_id": f"v9_compact_plan_{batch_no:03d}",
            "expected_count": len(chunk),
            "output_path": str(args.outputs_dir / f"batch_{batch_no:03d}.jsonl"),
            "instructions": (
                "Generate compact semantic plans only. Write JSONL rows with shape "
                '{"case_id":"...","plan":{...}}. Do not write full SDGP cases.'
            ),
            "slots": chunk,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  {path}: {len(chunk)} slots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
