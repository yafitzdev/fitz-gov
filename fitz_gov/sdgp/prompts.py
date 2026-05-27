"""SDGP prompt library — per-pattern × per-domain × per-difficulty templates.

Builds the generator prompt for a cell specification. The prompt is the
*implementation* of each taxonomy pattern (per ROADMAP §3): if a pattern's
prompt is vague, the generator produces vague cases. Most of the
engineering effort actually lives here.

Three composition layers:

  - **`BASE_TEMPLATE`** — universal frame: role, task, governance class,
    output format spec.
  - **`PATTERN_GUIDANCE[pattern]`** — per-pattern instructions that explain
    what makes this pattern distinct from its siblings (e.g.
    `numerical_conflict` vs `factual_contradiction`) and which structural
    properties must hold for the checker to accept it.
  - **`DOMAIN_HINTS[domain]`** — per-domain flavour: examples of what
    "evidence" looks like in this domain (peer-reviewed papers for
    `science_medicine`, regulations for `law_policy`, official docs for
    `technology_computing`, etc.).

Difficulty controls how subtle the case is: `easy` cases are unambiguous,
`hard` cases sit close to a taxonomy boundary and require careful reading.

Few-shot examples are drawn from the vault: `few_shot_for_cell(vault, cell, n)`
returns up to n existing cases matching the same pattern (preferring the
same domain) that the prompt embeds verbatim so the generator sees concrete
shape.

The output spec asks the generator for JSON in the V6+ schema. The checker
will reject anything malformed or signal-incoherent; the blind labeler
will then second-pass the label.
"""

from __future__ import annotations

import json
import random
import textwrap
from dataclasses import dataclass
from typing import Any, Iterable

from .modality import DEFAULT_MODALITY, validate_modality
from .taxonomy import (
    PATTERN_DESCRIPTIONS,
    Cell,
    Difficulty,
    Domain,
    TaxonomyPattern,
    governance_class_of,
)
from .vault import Vault, drop_vault_fields

# ---------------------------------------------------------------------------
# Per-pattern guidance
# ---------------------------------------------------------------------------


PATTERN_GUIDANCE: dict[TaxonomyPattern, str] = {
    # --- ABSTAIN ---
    TaxonomyPattern.WRONG_SPECIFICITY: (
        "The retrieved sources discuss the RIGHT entity but cover a different "
        "aspect, sub-topic, or attribute than the query is asking about. "
        "Sources should be authoritative on the entity in general but say "
        "nothing about the specific aspect queried. A confident answer is "
        "impossible because the precise question is unaddressed, NOT because "
        "the topic is wrong."
    ),
    TaxonomyPattern.WRONG_ENTITY: (
        "The retrieved sources cover a DIFFERENT entity than the one the "
        "query is about. Surface-level overlap (shared name, similar topic, "
        "same domain) is fine — but the entity is the wrong one. The model "
        "should abstain because the sources literally do not discuss the "
        "subject of the query."
    ),
    TaxonomyPattern.PARTIAL_OVERLAP: (
        "Evidence touches the topic but doesn't contain the specific facts "
        "needed to answer. The sources gesture at the right area without "
        "providing the actual answer. Different from `evidence_absent` "
        "(some relevant text exists) and from `wrong_specificity` (the right "
        "entity is even addressed, just not the queried aspect)."
    ),
    TaxonomyPattern.EVIDENCE_ABSENT: (
        "Nothing in the retrieved sources is even remotely relevant to the "
        "query. Complete topic mismatch — the sources are about unrelated "
        "subjects entirely. Sources may be high-quality and authoritative "
        "for THEIR topic, but useless here."
    ),
    TaxonomyPattern.TOO_GENERAL: (
        "Evidence is TRUE but too broad to answer the SPECIFIC query. "
        "E.g. query asks for a specific GDP figure; sources say only "
        "'Germany has a market economy.' The answer requires specificity "
        "the sources don't provide."
    ),
    TaxonomyPattern.TEMPORAL_MISMATCH: (
        "Evidence exists but is anchored to the WRONG time period. Sources "
        "describe an earlier (or later) state than the query is asking "
        "about. Different from `temporal_conflict` (DISPUTED) where multiple "
        "sources disagree on the time — here a single coherent time anchor "
        "just doesn't match the query."
    ),
    TaxonomyPattern.VERSION_BUILD_MISMATCH: (
        "The sources concern the right product/entity family but the wrong "
        "concrete variant: version, build, release, platform, jurisdiction, "
        "cohort, quarter, or other identity-bearing slice. Surface overlap "
        "should be high, but the requested exact variant is not answered. "
        "The correct outcome is ABSTAIN, not DISPUTED, because the sources "
        "are not incompatible; they answer a neighboring target."
    ),
    TaxonomyPattern.MISSING_EXECUTION_RESULT: (
        "The sources are clearly about the right topic and may include setup, "
        "requirements, protocol, traceability, a plan, or a scheduled run, "
        "but they never provide the final outcome/verdict/value/answer asked "
        "for. Do not explicitly state that no final outcome was recorded; "
        "that can become a grounded negative answer. The model must not infer "
        "execution success or a final result from preparation evidence alone."
    ),
    # --- DISPUTED ---
    TaxonomyPattern.NUMERICAL_CONFLICT: (
        "Multiple sources provide DIFFERENT NUMERICAL VALUES for the same "
        "entity and attribute. The values must clearly disagree (not just "
        "fall within measurement tolerance — that's `quantitative_consensus` "
        "from the TRUSTWORTHY family). Both digit-bearing values must "
        "appear in the contexts. Generate AT LEAST TWO contexts each with "
        "explicit numbers that conflict."
    ),
    TaxonomyPattern.TEMPORAL_CONFLICT: (
        "Sources describe different STATES at different TIMES, presented "
        "side-by-side WITHOUT temporal framing — so a reader can't tell "
        "which is current. 'X was true in 2020 / Y is true now' without "
        "the time annotations would read as a contradiction."
    ),
    TaxonomyPattern.DEFINITIONAL_CONFLICT: (
        "Sources disagree on what something IS — different definitions of "
        "the same term, different methodologies producing categorically "
        "different conclusions, competing theoretical frames presented as "
        "factual."
    ),
    TaxonomyPattern.FACTUAL_CONTRADICTION: (
        "Direct LOGICAL INCOMPATIBILITY between sources. Source A says X is "
        "the case; Source B says NOT X (or some Y that excludes X). Not "
        "about numbers or definitions specifically — about flat-out "
        "incompatible factual claims."
    ),
    TaxonomyPattern.AUTHORITY_CONFLICT: (
        "One HIGH-AUTHORITY source (peer-reviewed paper, official "
        "regulation, primary data) contradicts one LOW-AUTHORITY source "
        "(blog post, forum, anonymous user content). The contexts must "
        "include both — the authority asymmetry is the point. Per-context "
        "`authority_score` should be ≥0.8 for the high source and ≤0.4 for "
        "the low."
    ),
    TaxonomyPattern.SCOPE_CONFLICT: (
        "Sources are EACH CORRECT but apply to different SCOPES presented "
        "as equivalent. E.g. EU regulation says X; German national "
        "regulation says Y; they're not contradicting — they apply to "
        "different jurisdictions. The query doesn't specify scope; the "
        "answer depends on which scope."
    ),
    TaxonomyPattern.VERDICT_CONFLICT: (
        "Two or more sources give incompatible final verdicts or statuses "
        "for the same target under the same scope and time/version/build. "
        "Examples include pass/fail, approved/rejected, active/inactive, "
        "compliant/non-compliant, profitable/unprofitable, or equivalent "
        "binary/mutually exclusive statuses. Keep entity and scope aligned "
        "so the conflict cannot be resolved as a version or scope mismatch."
    ),
    TaxonomyPattern.AUTHORITY_STATUS_CONFLICT: (
        "A lower-authority, raw, intermediate, or secondary status conflicts "
        "with the source of record or governing authority. The point is not "
        "generic contradiction; it is that an authoritative system, regulator, "
        "official filing, approval register, or governing document disagrees "
        "with raw/intermediate evidence about the same target. Do not phrase "
        "the query as asking specifically for the source-of-record status, and "
        "do not let the authoritative context explicitly reconcile or invalidate "
        "the lower-authority status."
    ),
    # --- TRUSTWORTHY ---
    TaxonomyPattern.MULTI_SOURCE_CORROBORATION: (
        "MULTIPLE INDEPENDENT sources agree on the SAME claim. The agreement "
        "is the signal — generate ≥2 contexts that converge on the same "
        "answer. Sources can be different types (Wikipedia + cited paper + "
        "official site) as long as they corroborate."
    ),
    TaxonomyPattern.SINGLE_AUTHORITATIVE: (
        "ONE HIGH-AUTHORITY source directly answers the query, with no "
        "contradictions. The source should be one a reasonable RAG system "
        "would weight heavily: an official document, primary data, "
        "peer-reviewed publication. `authority_score` for the answering "
        "chunk should be ≥0.8."
    ),
    TaxonomyPattern.CONSISTENT_CHAIN: (
        "Multiple chunks from SAME OR RELATED sources form a coherent "
        "evidence chain that builds toward the answer. Each chunk adds a "
        "piece; together they justify the answer. Different from "
        "`multi_source_corroboration` — here the chunks complement rather "
        "than independently confirm."
    ),
    TaxonomyPattern.QUANTITATIVE_CONSENSUS: (
        "Multiple sources provide the SAME or CONSISTENT numerical values "
        "(within measurement tolerance) for the same entity and attribute. "
        "Generate ≥2 digit-bearing contexts that agree — explicitly NOT "
        "the `numerical_conflict` case."
    ),
    TaxonomyPattern.EXPERT_CONSENSUS: (
        "Multiple DOMAIN-EXPERT sources converge on the same conclusion. "
        "All contexts must read as high-authority expert content (research "
        "papers, peer-reviewed studies, official expert bodies). "
        "Per-context `authority_score` should be ≥0.7 across the board."
    ),
    TaxonomyPattern.DIRECT_ANSWER: (
        "A SINGLE CHUNK directly and completely answers the query, with no "
        "ambiguity. Could be a definitional source for a definition query, "
        "an official spec for a specification query, etc. No need for "
        "synthesis across multiple chunks."
    ),
    TaxonomyPattern.RESOLVED_CANDIDATE_SELECTION: (
        "The retrieved sources contain apparent candidate alternatives, but "
        "they explicitly identify which candidate/run/record is valid and "
        "which candidates are invalid, superseded, rejected, deprecated, or "
        "out of scope. The correct outcome is TRUSTWORTHY because the sources "
        "resolve the apparent competition themselves."
    ),
}


# ---------------------------------------------------------------------------
# Per-domain hints
# ---------------------------------------------------------------------------


DOMAIN_HINTS: dict[Domain, str] = {
    Domain.SCIENCE_MEDICINE: (
        "Sources typical of this domain: peer-reviewed journal articles, "
        "meta-analyses, clinical-trial reports, WHO/CDC/NIH guidelines, "
        "Cochrane reviews, agency datasets. Authority skews on study design "
        "(RCT > observational > case report) and replication status."
    ),
    Domain.LAW_POLICY: (
        "Sources typical of this domain: statute text, official regulatory "
        "documents (CFR, EUR-Lex), court opinions, agency interpretive "
        "guidance. Jurisdiction and version matter — note which jurisdiction "
        "/ effective date when relevant."
    ),
    Domain.HISTORY_GEOGRAPHY: (
        "Sources typical of this domain: encyclopedic references, academic "
        "history books, primary historical documents, geographic atlases. "
        "Temporal precision (which year / period) and named entities (which "
        "specific battle, treaty, region) are common failure modes."
    ),
    Domain.TECHNOLOGY_COMPUTING: (
        "Sources typical of this domain: official product documentation, "
        "API reference, release notes, RFCs, technical specifications, "
        "developer blog posts. Version is critical — same product can "
        "behave differently across major versions."
    ),
    Domain.ECONOMICS_FINANCE: (
        "Sources typical of this domain: central bank statements, BLS/Fed/ECB "
        "data releases, audited financial filings, IMF/OECD reports, "
        "market data services. Temporal anchoring (which quarter / fiscal "
        "year) matters; numbers go stale quickly."
    ),
    Domain.CULTURE_SOCIETY: (
        "Sources typical of this domain: news reporting, survey data, "
        "sociological studies, official statistics on social trends, "
        "encyclopedic entries on cultural figures and events. Often mixes "
        "factual claims with subjective framings."
    ),
    Domain.GENERAL_COMMONSENSE: (
        "Catch-all for queries that don't fit a specialist. Sources: "
        "general-purpose references (Wikipedia, almanacs), how-to guides, "
        "consumer-product info, everyday-knowledge content."
    ),
    Domain.CONFLICT_DETECTION: (
        "Meta-expert — only fires alongside a primary domain when the "
        "primary signal is cross-source disagreement. Don't pick this as a "
        "generation target on its own."
    ),
}


MODALITY_HINTS: dict[str, str] = {
    "unstructured": (
        "Use retrieved prose evidence: documents, PDFs, policy pages, articles, "
        "manual excerpts, reports, or other natural-language chunks."
    ),
    "structured": (
        "Use retrieved structured evidence: table rows, CSV extracts, SQL query "
        "results, schema excerpts, BI exports, reconciliation tables, or database "
        "snapshots. The evidence should require row/column/scope/version care."
    ),
    "code": (
        "Use retrieved code evidence: source files, tests, CI logs, configs, "
        "versioned docs, migration logs, or release manifests. The evidence "
        "should require code-aware source/test/doc/log reasoning."
    ),
}


# ---------------------------------------------------------------------------
# Difficulty hints
# ---------------------------------------------------------------------------


DIFFICULTY_HINTS: dict[Difficulty, str] = {
    Difficulty.EASY: (
        "Make the pattern OBVIOUS. The case should be easily identifiable as "
        "this pattern by any careful reader — strong, clear instances of the "
        "structural property. Useful as tier0-style sanity checks."
    ),
    Difficulty.MEDIUM: (
        "Make the pattern PRESENT BUT NOT SCREAMING. The signal is there if "
        "you look for it but doesn't overpower the rest of the content."
    ),
    Difficulty.HARD: (
        "Make the pattern SUBTLE — sit close to a taxonomy boundary so a "
        "naive model might mis-classify. Should require careful reading to "
        "pin down. The near-miss class should feel plausible. These are the "
        "cases that teach calibrated uncertainty."
    ),
}


# ---------------------------------------------------------------------------
# Output spec
# ---------------------------------------------------------------------------


OUTPUT_SCHEMA_HINT = textwrap.dedent("""\
    Output a single valid JSON object (no markdown fences, no commentary).
    The JSON must be a COMPLETE canonical SDGP training row, not a thin structural row.
    Every field below is required unless marked conditional:

    {
      "id": "<short stable id you choose — alphanumeric + underscores>",
      "version": "fitz-gov-8.0",
      "input": {
        "query": "<the user query>",
        "query_rewritten": "<semantically equivalent query sharpened for retrieval>",
        "contexts": [
          { "id": "ctx_001", "text": "<context body>", "authority_score": 0.7,
            "authority_signal": "<one of: peer_reviewed | official_primary |
              domain_expert | encyclopedic_general | news_secondary |
              blog_or_user_content | multi_source_diverse>",
            "temporality": {
              "is_time_sensitive": true,
              "anchor_period": "<current | none | explicit year/quarter/date range>",
              "staleness_risk": "<none | low | medium | high>"
            },
            "summary": "<one-sentence semantic summary, not a truncation>",
            "relevance_to_query": 0.0,
            "boundary_quality": 0.0 }
        ],
        "evidence_chain": {
          "order": ["ctx_001", "ctx_002"],
          "reasoning": "<required only when there are 2+ contexts>"
        }
      },
      "governance": {
        "classification": "<ABSTAIN|DISPUTED|TRUSTWORTHY>",
        "abstain": 0.0,
        "disputed": 0.0,
        "trustworthy": 0.0,
        "confidence": 0.0,
        "grounding": 0.0,
        "conflict_density": 0.0,
        "evidence_sufficiency": 0.0,
        "boundary_proximity": {
          "nearest_class": "<nearest non-actual class>",
          "distance": 0.0
        },
        "domain_familiarity": 0.0,
        "false_trustworthy_risk": 0.0,
        "hallucination_pressure": 0.0,
        "retrieval_retry_value": 0.0,
        "human_escalation_score": 0.0,
        "query_evidence_alignment": 0.0,
        "answer_coverage": 0.0,
        "evidence_bias_score": 0.0
      },
      "taxonomy": {
        "governance_class": "<same as classification>",
        "pattern": "<the pattern slug — see cell spec>",
        "pattern_description": "<canonical pattern description>",
        "cell_id": "<the cell_id from the cell spec, verbatim>"
      },
      "evaluation": {
        "mode": "governance",
        "check_mode_match": true,
        "required_elements": [
          "<answer-quality requirement; TRUSTWORTHY rows should have at least one>"
        ],
        "forbidden_claims": [
          "<claim the governed answer must not make if unsupported>"
        ],
        "forbidden_elements": [
          "<unsupported answer element to avoid>"
        ]
      },
      "routing": {
        "expert_fired": "<the expert domain from the cell spec>",
        "secondary_expert": null,
        "routing_confidence": 0.0
      },
      "meta": {
        "dataset_version": "v8",
        "modality": "<unstructured|structured|code>",
        "difficulty": "<easy|medium|hard, matching the cell spec>",
        "category": "<abstention | dispute | trustworthy_hedged | trustworthy_direct>",
        "confidence_level": "<high | medium | borderline>",
        "near_miss_class": "<nearest non-actual class>",
        "near_miss_reason": "<specific one-sentence boundary explanation>",
        "grounding_targets": {
          "gold_answer": "<TRUSTWORTHY only: grounded 2-6 sentence answer>",
          "sentences": [
            { "text": "<sentence>", "attributions": ["ctx_001"] }
          ]
        }
      }
    }

    Conditional omissions:
    - Omit `input.evidence_chain` only for single-context cases.
    - Omit `meta.grounding_targets` unless `governance.classification` is TRUSTWORTHY.
    - For non-TRUSTWORTHY rows, use empty arrays for `evaluation.required_elements`,
      `evaluation.forbidden_claims`, and `evaluation.forbidden_elements` only when
      no useful quality constraint applies.
    - All numeric scores must be in [0.0, 1.0].
""")


# ---------------------------------------------------------------------------
# Base template
# ---------------------------------------------------------------------------


BASE_TEMPLATE = textwrap.dedent("""\
    You are generating a single test case for the fitz-gov RAG governance
    benchmark. Each case is a (query, retrieved contexts) pair that
    instantiates ONE canonical evidence pattern.

    ## Cell specification

    - Pattern         : {pattern_name}
    - Governance class: {governance_class}
    - Expert domain   : {domain}
    - Evidence modality: {modality}
    - Difficulty      : {difficulty}
    - cell_id         : {cell_id}

    Pattern description: {pattern_description}

    ## What this pattern means

    {pattern_guidance}

    ## Domain flavour

    {domain_hints}

    ## Evidence modality

    {modality_hints}

    ## Difficulty

    {difficulty_hints}

    {few_shot_block}
    ## Your task

    Generate ONE new case that instantiates the pattern above in the
    specified domain at the specified difficulty. Do NOT reuse any of the
    few-shot example queries or contexts. The case must be plausible —
    write contexts that read like real retrieved chunks.

    Constraints:
    - The `taxonomy.cell_id` field in your output MUST equal {cell_id!r} verbatim.
    - `governance.classification` MUST equal {governance_class!r}.
    - `taxonomy.pattern` MUST equal {pattern_name!r}.
    - `routing.expert_fired` MUST equal {domain!r}.
    - `meta.modality` MUST equal {modality!r}.
    - `meta.difficulty` MUST equal {difficulty!r}.

    ## Output format

    {output_schema}
""")


# ---------------------------------------------------------------------------
# Few-shot lookup
# ---------------------------------------------------------------------------


def few_shot_for_cell(
    vault: Vault,
    cell: Cell,
    *,
    n: int = 2,
    prefer_same_domain: bool = True,
    seed: int | None = None,
) -> list[dict[str, Any]]:
    """Pick up to `n` example cases from the vault matching this cell's pattern.

    Preference order:
      1. Same pattern + same domain (any difficulty)
      2. Same pattern, any domain
      3. Same governance_class, any pattern

    Returns at most `n` examples; may return fewer if the vault doesn't have
    enough. Stable across calls when `seed` is provided.
    """
    rng = random.Random(seed)
    pattern = cell.pattern
    cls = governance_class_of(pattern)

    # Walk the vault once, bucketing
    same_pattern_same_domain: list[dict[str, Any]] = []
    same_pattern_other_domain: list[dict[str, Any]] = []
    same_class: list[dict[str, Any]] = []
    for case in vault.iter_cases():
        tax = case.get("taxonomy") or {}
        pat = tax.get("pattern")
        case_cell_id = tax.get("cell_id", "")
        try:
            case_pattern = TaxonomyPattern(pat) if pat else None
        except ValueError:
            case_pattern = None
        if case_pattern == pattern:
            # Check if it's the same domain
            if cell.domain.value in case_cell_id:
                same_pattern_same_domain.append(case)
            else:
                same_pattern_other_domain.append(case)
        elif case_pattern is not None and governance_class_of(case_pattern) == cls:
            same_class.append(case)

    pool: list[dict[str, Any]] = []
    if prefer_same_domain:
        pool.extend(same_pattern_same_domain)
        if len(pool) < n:
            pool.extend(same_pattern_other_domain)
        if len(pool) < n:
            pool.extend(same_class)
    else:
        pool.extend(same_pattern_same_domain + same_pattern_other_domain)
        if len(pool) < n:
            pool.extend(same_class)

    if not pool:
        return []

    if len(pool) <= n:
        return [drop_vault_fields(c) for c in pool]
    return [drop_vault_fields(c) for c in rng.sample(pool, n)]


def _format_few_shot_block(examples: list[dict[str, Any]]) -> str:
    if not examples:
        return ""
    parts = ["## Few-shot examples (existing cases with this pattern)", ""]
    for i, ex in enumerate(examples, start=1):
        compact = {
            "id": ex.get("id"),
            "input": ex.get("input", {"query": ex.get("query"), "contexts": ex.get("contexts")}),
            "taxonomy": ex.get("taxonomy"),
            "governance": {
                "classification": (ex.get("governance") or {}).get("classification")
                or (ex.get("expected_mode") or "").upper()
            },
        }
        # Trim long contexts to keep prompts tight
        if "contexts" in compact["input"]:
            trimmed = []
            for c in compact["input"]["contexts"][:3]:
                if isinstance(c, dict):
                    t = c.get("text", "")
                    trimmed.append(
                        {
                            "id": c.get("id"),
                            "text": t[:400] + ("..." if len(t) > 400 else ""),
                        }
                    )
                elif isinstance(c, str):
                    trimmed.append(c[:400] + ("..." if len(c) > 400 else ""))
            compact["input"]["contexts"] = trimmed
        parts.append(f"### Example {i}")
        parts.append("```json")
        parts.append(json.dumps(compact, indent=2, ensure_ascii=False))
        parts.append("```")
        parts.append("")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class GeneratorPrompt:
    """A built prompt ready to hand to a Provider."""

    cell: Cell
    text: str
    n_few_shots: int
    modality: str = DEFAULT_MODALITY

    def __str__(self) -> str:
        return self.text


def build_prompt(
    cell: Cell,
    *,
    few_shot_examples: Iterable[dict[str, Any]] = (),
    modality: str = DEFAULT_MODALITY,
) -> GeneratorPrompt:
    """Render the full generator prompt for a cell + (optional) few-shots."""
    modality = validate_modality(modality)
    examples = list(few_shot_examples)
    text = BASE_TEMPLATE.format(
        pattern_name=cell.pattern.value,
        governance_class=governance_class_of(cell.pattern).value,
        domain=cell.domain.value,
        modality=modality,
        difficulty=cell.difficulty.value,
        cell_id=cell.cell_id,
        pattern_description=PATTERN_DESCRIPTIONS[cell.pattern],
        pattern_guidance=PATTERN_GUIDANCE[cell.pattern],
        domain_hints=DOMAIN_HINTS[cell.domain],
        modality_hints=MODALITY_HINTS[modality],
        difficulty_hints=DIFFICULTY_HINTS[cell.difficulty],
        few_shot_block=_format_few_shot_block(examples),
        output_schema=OUTPUT_SCHEMA_HINT,
    )
    return GeneratorPrompt(
        cell=cell,
        text=text,
        n_few_shots=len(examples),
        modality=modality,
    )


def build_prompt_for_cell(
    cell: Cell,
    vault: Vault,
    *,
    n_few_shots: int = 2,
    seed: int | None = None,
    modality: str = DEFAULT_MODALITY,
) -> GeneratorPrompt:
    """Convenience: build the prompt + auto-pull few-shots from the vault."""
    examples = few_shot_for_cell(vault, cell, n=n_few_shots, seed=seed)
    return build_prompt(cell, few_shot_examples=examples, modality=modality)


SYSTEM_MESSAGE = (
    "You generate single fitz-gov benchmark cases as JSON. Output only the "
    "JSON object — no markdown fences, no commentary. Each case instantiates "
    "exactly one taxonomy pattern in one expert domain at one difficulty."
)
