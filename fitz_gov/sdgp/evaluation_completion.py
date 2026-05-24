"""LLM prompts and merge helpers for canonical evaluation fields."""

from __future__ import annotations

import json
import re
import textwrap
from typing import Any, Mapping

from .evaluation_fields import merge_evaluation_overlay
from .llm_enrich import _strip_thinking
from .providers import GenerateRequest, Provider


EVALUATION_COMPLETION_SYSTEM = (
    "You write evaluator constraints for fitz-gov RAG governance test cases. "
    "The query, contexts, and gold governance label are locked. Do not relabel "
    "the case. Output compact JSON only."
)

_PROMPT_TEMPLATE = textwrap.dedent("""\
    ## Locked case

    ```json
    {case_json}
    ```

    ## Task

    Fill the canonical `evaluation` block. These fields are used to test whether
    a generated answer stayed inside the retrieved evidence.

    Return exactly this JSON shape:

    {{
      "evaluation": {{
        "mode": "governance",
        "check_mode_match": true,
        "required_elements": ["..."],
        "forbidden_claims": ["..."],
        "forbidden_elements": ["..."],
        "config": {{
          "use_regex": true,
          "case_insensitive": true,
          "min_required": 1,
          "allowed_phrases": []
        }}
      }}
    }}

    Rules:
    - Do not change the case label, query, contexts, taxonomy, or governance signals.
    - `required_elements` are short strings/regexes that a good supported answer
      should contain. Prefer concrete answer facts from the contexts.
    - `forbidden_claims` are regexes for plausible hallucinated answer claims not
      supported by the contexts. Use them mainly for missing numeric/date/entity
      details, over-specific claims, and unsupported causal claims.
    - `forbidden_elements` are strings/regexes that would make the answer falsely
      overconfident while still mentioning relevant material.
    - For TRUSTWORTHY cases, provide at least 2 required elements and at least 1
      forbidden claim or forbidden element.
    - For ABSTAIN and DISPUTED cases, empty lists are acceptable because the mode
      check is the primary evaluator.
    - Keep entries concise. Do not include prose outside JSON.
""")

_FENCED = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)
_FIRST = re.compile(r"\{.*\}", re.DOTALL)


def build_evaluation_completion_prompt(case: Mapping[str, Any]) -> str:
    """Build a compact prompt for evaluator-field completion."""
    input_block = case.get("input") if isinstance(case.get("input"), Mapping) else {}
    contexts = input_block.get("contexts") if isinstance(input_block.get("contexts"), list) else []
    compact = {
        "id": case.get("id"),
        "input": {
            "query": input_block.get("query"),
            "contexts": [
                {
                    "id": c.get("id"),
                    "text": c.get("text"),
                    "summary": c.get("summary"),
                    "relevance_to_query": c.get("relevance_to_query"),
                }
                for c in contexts
                if isinstance(c, Mapping)
            ],
        },
        "governance": {
            "classification": (case.get("governance") or {}).get("classification")
            if isinstance(case.get("governance"), Mapping)
            else None
        },
        "taxonomy": case.get("taxonomy"),
        "meta": {
            "difficulty": (case.get("meta") or {}).get("difficulty")
            if isinstance(case.get("meta"), Mapping)
            else None,
            "near_miss_reason": (case.get("meta") or {}).get("near_miss_reason")
            if isinstance(case.get("meta"), Mapping)
            else None,
            "grounding_targets": (case.get("meta") or {}).get("grounding_targets")
            if isinstance(case.get("meta"), Mapping)
            else None,
        },
    }
    return _PROMPT_TEMPLATE.format(
        case_json=json.dumps(compact, indent=2, ensure_ascii=False)
    )


def parse_evaluation_completion_response(raw: str) -> dict[str, Any]:
    """Parse a provider response into an overlay dict."""
    text = _strip_thinking(str(raw or "").strip())
    if not text:
        raise ValueError("empty evaluation-completion response")
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
    raise ValueError(f"could not extract JSON from response (len={len(raw)})")


def complete_evaluation_with_provider(
    case: dict[str, Any],
    provider: Provider,
    *,
    max_tokens: int = 1024,
    temperature: float = 0.1,
    overwrite: bool = False,
):
    raw = provider.generate(
        GenerateRequest(
            prompt=build_evaluation_completion_prompt(case),
            system=EVALUATION_COMPLETION_SYSTEM,
            max_tokens=max_tokens,
            temperature=temperature,
            metadata={"case_id": case.get("id"), "phase": "evaluation-completion"},
        )
    )
    overlay = parse_evaluation_completion_response(raw)
    return merge_evaluation_overlay(case, overlay, overwrite=overwrite)
