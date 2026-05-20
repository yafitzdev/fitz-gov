"""V6-completion enrichment — adds the 4 fields that MoE multi-task training needs.

After Phase 0b (`llm_enrich.py`), V6 cases carry the core governance schema
but four MoE output heads still have no labels:

  - **Chunk Boundary Detection**       → per-chunk `boundary_quality` (0–1)
  - **Evidence Bias Detection**        → per-case `evidence_bias_score` (0–1)
  - **Evidence Chain Construction**    → per-case `evidence_chain` (order + reasoning),
                                           multi-context cases only
  - **Answer Grounding Verification**  → per-case `grounding_targets`
                                           (gold answer + sentence→chunk attributions),
                                           TRUSTWORTHY cases only

A single LLM call per case emits all applicable fields. The prompt
conditionally requests `evidence_chain` (only if ≥2 chunks) and
`grounding_targets` (only if TRUSTWORTHY) so single-chunk and non-trustworthy
cases stay cheap.

Locked: every existing field from Phase 0a/0b. We only *add* — never modify.
"""

from __future__ import annotations

import json
import re
import textwrap
from dataclasses import dataclass, field
from typing import Any, Iterable

from .llm_enrich import _strip_thinking, _clamp01
from .providers import GenerateRequest, Provider


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------


V6_COMPLETION_SYSTEM = (
    "You annotate already-classified RAG governance cases with four ground-"
    "truth signals needed for multi-task MoE training: per-chunk boundary "
    "quality, per-case evidence bias, multi-chunk reasoning order, and (for "
    "TRUSTWORTHY cases) a gold answer with per-sentence source attributions. "
    "The case's classification, taxonomy, and existing signals are LOCKED — "
    "do not propose changes. Output a single JSON object — no fences, no "
    "commentary."
)


_PROMPT_TEMPLATE = textwrap.dedent("""\
    ## Case to annotate

    ```json
    {case_json}
    ```

    ## Locked context

    - Classification is **{classification}** ({pattern}).
    - Number of chunks: **{n_chunks}**.
    - {trustworthy_note}
    {grounding_hints}

    ## Output JSON — fill exactly these top-level keys

    ```
    {{
      "boundary_quality": [
        {{"id": "<chunk id>", "score": <0.0–1.0>}}
        // ONE entry per chunk, in the original chunk order
      ],

      "evidence_bias_score": <0.0–1.0>,
      // 0 = balanced (multiple independent sources / perspectives / source-types)
      // 1 = fully one-sided (single perspective dominates, or all chunks share an obvious common origin)

      {evidence_chain_block}

      {grounding_block}
    }}
    ```

    ## Field definitions

    **`boundary_quality.score`** (per chunk):
    1.0 = clean cut — chunk starts/ends at natural sentence/paragraph boundary, complete thoughts.
    0.7 = soft cut — chunk starts/ends slightly mid-thought but content is coherent.
    0.3 = hard cut — chunk visibly truncates a sentence or splits a list/table mid-row.
    0.0 = unusable — meaning is destroyed by the cut.
    Judge by inspecting the chunk text directly.

    **`evidence_bias_score`** (per case): 0 if the case has multiple independent sources / perspectives represented; 1 if the evidence base is one-sided (single source-type, single author, single perspective). Consider source diversity, authority signals, and whether contradicting viewpoints could plausibly exist but are absent.

    **`evidence_chain.order`** (multi-chunk only): the chunk ids ordered as a reader should consume them to construct the answer or governance verdict. For ABSTAIN/DISPUTED, the order should expose *why* the case is ABSTAIN/DISPUTED (e.g. ctx defining metric → ctx with conflicting value → ctx with caveat). For TRUSTWORTHY, the order should mirror how a good answer would be assembled.

    **`evidence_chain.reasoning`** (multi-chunk only): one sentence — why this is the right order.

    **`grounding_targets.gold_answer`** (TRUSTWORTHY only): a concise, well-formed answer to the query that uses ONLY facts present in the contexts. Should hedge if the contexts hedge. Do NOT introduce information not in the contexts. 2–6 sentences.

    **`grounding_targets.sentences`** (TRUSTWORTHY only): the gold_answer split into sentences. For each sentence, list the chunk ids that support it. A sentence may have multiple attributions; an inference-only sentence with no direct chunk support should list `[]`.

    Output the JSON object only. No prose around it.
""")


_REGEX_HINT = re.compile(r"[\\(){}|\[\]^$?+*]|\\d|\\s|\\b|\\w")


def _grounding_hints(case: dict[str, Any]) -> str:
    """V5.1 legacy required_elements as plain-string hints for TRUSTWORTHY cases.
    forbidden_claims is dropped (it's regex patterns used by the evaluator, not
    human-readable claims) — the generic "use only facts in the contexts" rule
    captures the same constraint."""
    legacy = case.get("meta", {}).get("v51_legacy", {})
    req = legacy.get("required_elements") or []
    if not isinstance(req, list):
        return ""
    plain = [r for r in req if isinstance(r, str) and not _REGEX_HINT.search(r)][:8]
    if not plain:
        return ""
    return f"  - The gold answer SHOULD reference: {json.dumps(plain, ensure_ascii=False)}"


def build_v6_completion_prompt(case: dict[str, Any]) -> str:
    classification = case.get("governance", {}).get("classification", "?")
    pattern = case.get("taxonomy", {}).get("pattern", "?")
    contexts = case.get("input", {}).get("contexts", []) or []
    n_chunks = len(contexts)
    is_trustworthy = classification == "TRUSTWORTHY"
    is_multi = n_chunks >= 2

    compact = {
        "id": case.get("id"),
        "input": {
            "query": case.get("input", {}).get("query"),
            "contexts": [
                {"id": c.get("id"), "text": c.get("text", "")}
                for c in contexts if isinstance(c, dict)
            ],
        },
        "governance": {"classification": classification},
        "taxonomy": {
            "pattern": pattern,
            "governance_class": case.get("taxonomy", {}).get("governance_class"),
        },
    }

    trustworthy_note = (
        f"TRUSTWORTHY case — also emit `grounding_targets`."
        if is_trustworthy
        else f"NOT TRUSTWORTHY (`{classification}`) — omit `grounding_targets` entirely."
    )
    if is_multi:
        evidence_chain_block = textwrap.dedent("""\
              "evidence_chain": {
                "order": ["<chunk_id>", "<chunk_id>", ...],   // all chunk ids, ordered
                "reasoning": "<one sentence: why this order>"
              },""").strip()
    else:
        evidence_chain_block = "// SINGLE-CHUNK CASE — omit `evidence_chain` entirely"

    if is_trustworthy:
        grounding_block = textwrap.dedent("""\
              "grounding_targets": {
                "gold_answer": "<2–6 sentence answer using only facts in the contexts>",
                "sentences": [
                  {"text": "<one sentence>", "attributions": ["<chunk_id>", ...]}
                ]
              }""").strip()
        grounding_hints = _grounding_hints(case)
    else:
        grounding_block = "// NOT TRUSTWORTHY — omit `grounding_targets` entirely"
        grounding_hints = ""

    return _PROMPT_TEMPLATE.format(
        case_json=json.dumps(compact, indent=2, ensure_ascii=False),
        classification=classification,
        pattern=pattern,
        n_chunks=n_chunks,
        trustworthy_note=trustworthy_note,
        grounding_hints=grounding_hints,
        evidence_chain_block=evidence_chain_block,
        grounding_block=grounding_block,
    )


# ---------------------------------------------------------------------------
# Parse + merge
# ---------------------------------------------------------------------------


_FENCED = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)
_FIRST = re.compile(r"\{.*\}", re.DOTALL)


def parse_v6_completion_response(raw: str) -> dict[str, Any]:
    if not raw or not raw.strip():
        raise ValueError("empty v6-completion response")
    text = _strip_thinking(raw.strip())
    if not text:
        raise ValueError("v6-completion response contained only thinking blocks")
    for candidate in (text, *(m.group(1) if m and m.lastindex else m.group(0)
                              for m in (_FENCED.search(text), _FIRST.search(text)) if m)):
        try:
            obj = json.loads(candidate)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            continue
    raise ValueError(f"could not extract JSON from v6-completion response (len={len(raw)})")


@dataclass(slots=True)
class V6CompletionResult:
    case_id: str
    fields_filled: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return bool(self.fields_filled)


def _chunk_ids(case: dict[str, Any]) -> list[str]:
    return [c.get("id") for c in case.get("input", {}).get("contexts", []) if isinstance(c, dict) and c.get("id")]


def merge_v6_completion(case: dict[str, Any], payload: dict[str, Any]) -> V6CompletionResult:
    res = V6CompletionResult(case_id=str(case.get("id", "<no id>")))
    valid_ids = set(_chunk_ids(case))
    contexts = case.setdefault("input", {}).setdefault("contexts", [])

    # boundary_quality (per chunk)
    bq_list = payload.get("boundary_quality") or []
    if isinstance(bq_list, list):
        by_id = {}
        for entry in bq_list:
            if not isinstance(entry, dict):
                continue
            cid, score = entry.get("id"), _clamp01(entry.get("score"))
            if cid and score is not None:
                by_id[cid] = round(score, 3)
        for idx, chunk in enumerate(contexts):
            if not isinstance(chunk, dict):
                continue
            cid = chunk.get("id")
            if cid in by_id:
                chunk["boundary_quality"] = by_id[cid]
                res.fields_filled.append(f"contexts[{idx}].boundary_quality")
            else:
                res.warnings.append(f"no boundary_quality for chunk {cid}")

    # evidence_bias_score (per case)
    bias = _clamp01(payload.get("evidence_bias_score"))
    if bias is not None:
        case.setdefault("governance", {})["evidence_bias_score"] = round(bias, 3)
        res.fields_filled.append("governance.evidence_bias_score")

    # evidence_chain (multi-chunk only)
    ec = payload.get("evidence_chain")
    if isinstance(ec, dict) and len(contexts) >= 2:
        order = ec.get("order")
        reasoning = ec.get("reasoning")
        if isinstance(order, list) and all(isinstance(x, str) for x in order):
            filtered = [x for x in order if x in valid_ids]
            if filtered:
                case["input"]["evidence_chain"] = {
                    "order": filtered,
                    "reasoning": reasoning.strip() if isinstance(reasoning, str) else None,
                }
                res.fields_filled.append("input.evidence_chain")
                if len(filtered) != len(valid_ids):
                    res.warnings.append(
                        f"evidence_chain.order has {len(filtered)}/{len(valid_ids)} valid chunk ids"
                    )

    # grounding_targets (TRUSTWORTHY only)
    if case.get("governance", {}).get("classification") == "TRUSTWORTHY":
        gt = payload.get("grounding_targets")
        if isinstance(gt, dict):
            gold = gt.get("gold_answer")
            sentences_in = gt.get("sentences") or []
            clean_sentences = []
            if isinstance(sentences_in, list):
                for s in sentences_in:
                    if not isinstance(s, dict):
                        continue
                    text = s.get("text")
                    attr = s.get("attributions") or []
                    if isinstance(text, str) and text.strip() and isinstance(attr, list):
                        valid_attr = [a for a in attr if isinstance(a, str) and a in valid_ids]
                        clean_sentences.append({"text": text.strip(), "attributions": valid_attr})
            if isinstance(gold, str) and gold.strip() and clean_sentences:
                case.setdefault("meta", {})["grounding_targets"] = {
                    "gold_answer": gold.strip(),
                    "sentences": clean_sentences,
                }
                res.fields_filled.append("meta.grounding_targets")

    return res


# ---------------------------------------------------------------------------
# Single-case enricher
# ---------------------------------------------------------------------------


def complete_case_with_provider(
    case: dict[str, Any],
    provider: Provider,
    *,
    max_tokens: int = 4000,
    temperature: float = 0.2,
) -> V6CompletionResult:
    prompt = build_v6_completion_prompt(case)
    raw = provider.generate(
        GenerateRequest(
            prompt=prompt,
            system=V6_COMPLETION_SYSTEM,
            max_tokens=max_tokens,
            temperature=temperature,
            metadata={"case_id": case.get("id"), "phase": "v6-completion"},
        )
    )
    payload = parse_v6_completion_response(raw)
    return merge_v6_completion(case, payload)


# ---------------------------------------------------------------------------
# Detect which cases still need completion
# ---------------------------------------------------------------------------


def case_needs_v6_completion(case: dict[str, Any]) -> bool:
    """True if any of the 4 new V6 fields is missing (for the cases where it applies)."""
    contexts = case.get("input", {}).get("contexts", []) or []
    n = len(contexts)
    # per-chunk boundary_quality
    for c in contexts:
        if isinstance(c, dict) and "boundary_quality" not in c:
            return True
    # per-case evidence_bias_score
    if "evidence_bias_score" not in case.get("governance", {}):
        return True
    # evidence_chain (multi-chunk only)
    if n >= 2 and "evidence_chain" not in case.get("input", {}):
        return True
    # grounding_targets (TRUSTWORTHY only)
    if (
        case.get("governance", {}).get("classification") == "TRUSTWORTHY"
        and "grounding_targets" not in case.get("meta", {})
    ):
        return True
    return False


def cases_needing_v6_completion(cases: Iterable[dict[str, Any]]) -> list[str]:
    return [c["id"] for c in cases if "id" in c and case_needs_v6_completion(c)]
