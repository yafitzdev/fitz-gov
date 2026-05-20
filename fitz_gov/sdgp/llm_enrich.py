"""Phase 0b — LLM-based enrichment of `<TODO_LLM>` + heuristic stubs.

Phase 0a (`fitz_gov/sdgp/enrich.py`) wrote *structurally valid* cases onto
the V6+ schema using deterministic heuristics. The fields that genuinely
require reasoning landed as `<TODO_LLM>` markers or coarse stubs. This
module replaces them with real LLM-generated values.

Fields refreshed per case:

  - `input.query_rewritten`                        — actual rewriting
  - `input.contexts[].summary`                     — real summarization (not truncation)
  - `input.contexts[].relevance_to_query`          — real per-chunk scoring
  - `input.contexts[].temporality.anchor_period`   — extracted time anchor
  - `governance.hallucination_pressure`            — reasoned about evidence + query
  - `governance.retrieval_retry_value`             — reasoned about whether more retrieval helps
  - `governance.query_evidence_alignment`          — reasoned scoring
  - `governance.answer_coverage`                   — reasoned scoring
  - `governance.boundary_proximity.distance`       — reasoned distance to nearest_class
  - `meta.near_miss_reason`                        — one-sentence reasoning

Class labels (`classification`, `taxonomy.pattern`, `cell_id`, `governance_class`)
are NEVER touched — those came from human-validated V5.1 metadata. Same for
the structural signals derived from category (`conflict_density`,
`evidence_sufficiency`, `false_trustworthy_risk`) which are class-determined.

The driver is a `Provider` (Ollama, file-handoff, or any other). Each case
is sent as one provider call; the response is parsed as JSON and merged
back into the case. Designed to be resumable: re-running on an already-
enriched vault skips cases whose `_vault.last_modified_at` is newer than
their `_vault.added_at` (or pass `--force` to re-enrich).
"""

from __future__ import annotations

import json
import re
import textwrap
from dataclasses import dataclass, field
from typing import Any, Iterable

from .providers import GenerateRequest, Provider
from .vault import VAULT_KEY


LLM_TODO = "<TODO_LLM>"


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------


ENRICHMENT_SYSTEM = (
    "You enrich pre-classified RAG governance cases with reasoning-derived "
    "metadata. The case's governance class, taxonomy pattern, and cell_id are "
    "ALREADY CORRECT and locked — do NOT propose changes. Your job is to "
    "produce reasoned values for fields that require reading the query and "
    "contexts: query rewriting, per-chunk summaries and relevance scores, "
    "temporality extraction, and the governance signals that score how the "
    "evidence relates to the query (hallucination_pressure, "
    "retrieval_retry_value, query_evidence_alignment, answer_coverage, "
    "boundary_proximity.distance, near_miss_reason). "
    "Output a single JSON object — no fences, no commentary."
)


_ENRICHMENT_TEMPLATE = textwrap.dedent("""\
    ## Case to enrich

    ```json
    {case_json}
    ```

    ## Locked fields (do NOT change)

    - `id`, `version`, `governance.classification`, `governance.{{abstain,disputed,trustworthy}}`,
      `taxonomy.{{governance_class, pattern, cell_id, pattern_description}}`,
      `routing.expert_fired`, `meta.{{difficulty, category, subcategory, domain}}`.

    ## Fields to fill (your output)

    Output a JSON object with these top-level keys ONLY. Every value must
    reflect actual reasoning about the query + contexts above:

    {{
      "query_rewritten": "<rewritten query optimized for retrieval — keep the meaning, sharpen the phrasing>",

      "contexts": [
        {{
          "id": "<the chunk's id from input.contexts>",
          "summary": "<one-sentence semantic summary of the chunk's content, NOT a truncation>",
          "relevance_to_query": <float 0.0–1.0, how relevant this chunk actually is to the query>,
          "temporality": {{
            "anchor_period": "<the time period the chunk's content refers to — e.g. '2024-Q3', 'pre-1990', 'current', or 'none' if non-temporal>"
          }}
        }}
        // ... one entry per chunk, in order
      ],

      "governance": {{
        "hallucination_pressure":   <0.0–1.0 — how likely a model would hallucinate if forced to answer with this evidence>,
        "retrieval_retry_value":    <0.0–1.0 — would more / different retrieval substantially improve the answer>,
        "query_evidence_alignment": <0.0–1.0 — semantic alignment between the query and the contexts as a whole>,
        "answer_coverage":          <0.0–1.0 — fraction of the query that's actually addressed by the contexts>,
        "boundary_proximity_distance": <0.0–1.0 — distance to the nearest non-actual class (1.0 = clear case, 0.0 = right on the boundary)>
      }},

      "meta": {{
        "near_miss_reason": "<one sentence: why a naive reader could mistake this case for `meta.near_miss_class`, but the actual class is correct>"
      }}
    }}

    Ground every score in concrete observations about the query and the
    contexts. Don't write generic explanations. Be concise — short
    descriptions, no preamble.
""")


def build_enrichment_prompt(case: dict[str, Any]) -> str:
    # Trim case down to what the LLM actually needs to read, to keep prompts compact.
    compact = {
        "id": case.get("id"),
        "input": {
            "query": case.get("input", {}).get("query"),
            "contexts": [
                {"id": c.get("id"), "text": c.get("text", "")} if isinstance(c, dict) else {"text": str(c)}
                for c in case.get("input", {}).get("contexts", [])
            ],
        },
        "governance": {
            "classification": case.get("governance", {}).get("classification"),
        },
        "taxonomy": {
            "governance_class": case.get("taxonomy", {}).get("governance_class"),
            "pattern": case.get("taxonomy", {}).get("pattern"),
            "cell_id": case.get("taxonomy", {}).get("cell_id"),
        },
        "meta": {
            "category": case.get("meta", {}).get("category"),
            "subcategory": case.get("meta", {}).get("subcategory"),
            "domain": case.get("meta", {}).get("domain"),
            "difficulty": case.get("meta", {}).get("difficulty"),
            "near_miss_class": case.get("meta", {}).get("near_miss_class"),
        },
    }
    return _ENRICHMENT_TEMPLATE.format(case_json=json.dumps(compact, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------


_FENCED = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)
_FIRST = re.compile(r"\{.*\}", re.DOTALL)


def parse_enrichment_response(raw: str) -> dict[str, Any]:
    """Best-effort JSON extraction. Raises ValueError on nothing-parseable."""
    if not raw or not raw.strip():
        raise ValueError("empty enrichment response")
    text = raw.strip()
    for candidate in (text, *(m.group(1) if m and m.lastindex else m.group(0)
                              for m in (_FENCED.search(text), _FIRST.search(text)) if m)):
        try:
            obj = json.loads(candidate)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            continue
    raise ValueError(f"could not extract JSON object from enrichment response (len={len(raw)})")


# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class EnrichmentResult:
    """Stats on what fields actually changed for one case."""

    case_id: str
    fields_filled: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return bool(self.fields_filled)


def _clamp01(x: Any) -> float | None:
    try:
        f = float(x)
    except (TypeError, ValueError):
        return None
    return max(0.0, min(1.0, f))


def merge_enrichment(
    case: dict[str, Any], enrichment: dict[str, Any]
) -> EnrichmentResult:
    """Merge LLM enrichment back into a case. Mutates `case` in place and
    returns an EnrichmentResult listing which fields changed."""
    res = EnrichmentResult(case_id=str(case.get("id", "<no id>")))

    # input.query_rewritten
    qr = enrichment.get("query_rewritten")
    if isinstance(qr, str) and qr.strip():
        case.setdefault("input", {})
        case["input"]["query_rewritten"] = qr.strip()
        res.fields_filled.append("input.query_rewritten")

    # per-chunk
    chunks_in = enrichment.get("contexts") or []
    case.setdefault("input", {}).setdefault("contexts", [])
    target_chunks = case["input"]["contexts"]
    # Map by id if present, else align positionally.
    by_id = {c.get("id"): c for c in chunks_in if isinstance(c, dict) and c.get("id")}
    for idx, target in enumerate(target_chunks):
        if not isinstance(target, dict):
            continue
        source = by_id.get(target.get("id")) or (chunks_in[idx] if idx < len(chunks_in) else None)
        if not isinstance(source, dict):
            continue
        # summary
        if isinstance(source.get("summary"), str) and source["summary"].strip():
            target["summary"] = source["summary"].strip()
            res.fields_filled.append(f"contexts[{idx}].summary")
        # relevance_to_query
        rel = _clamp01(source.get("relevance_to_query"))
        if rel is not None:
            target["relevance_to_query"] = round(rel, 3)
            res.fields_filled.append(f"contexts[{idx}].relevance_to_query")
        # temporality.anchor_period
        src_temp = source.get("temporality")
        if isinstance(src_temp, dict) and isinstance(src_temp.get("anchor_period"), str):
            target.setdefault("temporality", {})
            target["temporality"]["anchor_period"] = src_temp["anchor_period"].strip()
            res.fields_filled.append(f"contexts[{idx}].temporality.anchor_period")

    # governance signals
    case.setdefault("governance", {})
    g_in = enrichment.get("governance") or {}
    for key in (
        "hallucination_pressure",
        "retrieval_retry_value",
        "query_evidence_alignment",
        "answer_coverage",
    ):
        v = _clamp01(g_in.get(key))
        if v is not None:
            case["governance"][key] = round(v, 3)
            res.fields_filled.append(f"governance.{key}")
    # boundary_proximity.distance — patch into existing dict
    dist = _clamp01(g_in.get("boundary_proximity_distance"))
    if dist is not None:
        bp = case["governance"].setdefault("boundary_proximity", {"nearest_class": None})
        bp["distance"] = round(dist, 3)
        res.fields_filled.append("governance.boundary_proximity.distance")

    # meta.near_miss_reason
    case.setdefault("meta", {})
    nm = enrichment.get("meta", {}).get("near_miss_reason") if isinstance(enrichment.get("meta"), dict) else None
    if isinstance(nm, str) and nm.strip():
        case["meta"]["near_miss_reason"] = nm.strip()
        res.fields_filled.append("meta.near_miss_reason")

    return res


# ---------------------------------------------------------------------------
# Single-case enricher
# ---------------------------------------------------------------------------


def enrich_case_with_provider(
    case: dict[str, Any],
    provider: Provider,
    *,
    max_tokens: int = 1500,
    temperature: float = 0.2,
) -> EnrichmentResult:
    """End-to-end: build prompt → call provider → parse → merge. Returns
    EnrichmentResult; case is mutated in place. Raises on provider error or
    unparseable response (caller decides whether to skip / retry / abort)."""
    prompt = build_enrichment_prompt(case)
    raw = provider.generate(
        GenerateRequest(
            prompt=prompt,
            system=ENRICHMENT_SYSTEM,
            max_tokens=max_tokens,
            temperature=temperature,
            metadata={"case_id": case.get("id"), "phase": "0b"},
        )
    )
    enrichment = parse_enrichment_response(raw)
    return merge_enrichment(case, enrichment)


# ---------------------------------------------------------------------------
# Detect which cases still need enrichment
# ---------------------------------------------------------------------------


def case_needs_enrichment(case: dict[str, Any]) -> bool:
    """True if any of the LLM-required fields is still a TODO_LLM placeholder
    or absent. False if all relevant fields are populated by something other
    than the marker."""
    if case.get("input", {}).get("query_rewritten") in (None, LLM_TODO):
        return True
    if case.get("meta", {}).get("near_miss_reason") in (None, LLM_TODO):
        return True
    for c in case.get("input", {}).get("contexts", []):
        if isinstance(c, dict):
            if c.get("temporality", {}).get("anchor_period") in (None, LLM_TODO):
                return True
    return False


def cases_needing_enrichment(cases: Iterable[dict[str, Any]]) -> list[str]:
    """List the case_ids that still have TODO_LLM markers."""
    return [c["id"] for c in cases if "id" in c and case_needs_enrichment(c)]
