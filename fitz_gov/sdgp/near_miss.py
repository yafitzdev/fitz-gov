"""SDGP near-miss generation — boundary cases between two adjacent patterns.

ROADMAP §3 requires 20–25% of every expert's data to be near-miss / borderline
cases. These are the cases that teach calibrated uncertainty: cases that sit
on the boundary between two taxonomy patterns and could plausibly be argued
either way.

The orchestrator's normal generation path takes a single cell spec. Near-miss
generation takes TWO adjacent cells (same difficulty, related patterns) and
asks the generator for a case that sits between them — labeled as the
*primary* cell but with `meta.near_miss_class` and `meta.near_miss_reason`
pointing at the runner-up.

This module:
  - Defines `PATTERN_NEIGHBORS` — pairs of taxonomy patterns that are
    structurally close enough that a borderline case is plausible.
  - `build_near_miss_prompt(primary, secondary)` — extends the standard
    prompt with explicit boundary-walking instructions.
  - `NearMissOrchestrator.fill_boundary(primary, secondary, n)` — wraps
    `Orchestrator` to drive boundary generation.
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass, field
from typing import Any, Iterable

from .orchestrator import GenerationResult, Orchestrator, Outcome
from .prompts import (
    BASE_TEMPLATE,
    DIFFICULTY_HINTS,
    DOMAIN_HINTS,
    OUTPUT_SCHEMA_HINT,
    PATTERN_GUIDANCE,
    GeneratorPrompt,
    _format_few_shot_block,
    few_shot_for_cell,
)
from .providers import GenerateRequest
from .taxonomy import (
    Cell,
    Difficulty,
    Domain,
    GovernanceClass,
    PATTERN_DESCRIPTIONS,
    TaxonomyPattern,
    governance_class_of,
)


# ---------------------------------------------------------------------------
# Pattern neighbours — which pairs are "boundary-plausible"
# ---------------------------------------------------------------------------
#
# Each entry is a bidirectional pair (a, b) meaning: a case can plausibly
# sit on the boundary between a and b, where a is the gold label and b is
# the runner-up the model might be tempted toward. Pairs are chosen for
# structural similarity, NOT for being in the same governance class — many
# of the most valuable near-miss cases CROSS class (e.g. an ABSTAIN
# `partial_overlap` that could be misread as a DISPUTED case).


PATTERN_NEIGHBORS: list[tuple[TaxonomyPattern, TaxonomyPattern]] = [
    # ABSTAIN intra-class neighbours
    (TaxonomyPattern.WRONG_SPECIFICITY, TaxonomyPattern.WRONG_ENTITY),
    (TaxonomyPattern.WRONG_SPECIFICITY, TaxonomyPattern.PARTIAL_OVERLAP),
    (TaxonomyPattern.WRONG_ENTITY, TaxonomyPattern.EVIDENCE_ABSENT),
    (TaxonomyPattern.PARTIAL_OVERLAP, TaxonomyPattern.TOO_GENERAL),
    (TaxonomyPattern.TEMPORAL_MISMATCH, TaxonomyPattern.WRONG_SPECIFICITY),
    (TaxonomyPattern.VERSION_BUILD_MISMATCH, TaxonomyPattern.WRONG_ENTITY),
    (TaxonomyPattern.VERSION_BUILD_MISMATCH, TaxonomyPattern.TEMPORAL_MISMATCH),
    (TaxonomyPattern.MISSING_EXECUTION_RESULT, TaxonomyPattern.PARTIAL_OVERLAP),
    # DISPUTED intra-class neighbours
    (TaxonomyPattern.NUMERICAL_CONFLICT, TaxonomyPattern.FACTUAL_CONTRADICTION),
    (TaxonomyPattern.TEMPORAL_CONFLICT, TaxonomyPattern.FACTUAL_CONTRADICTION),
    (TaxonomyPattern.DEFINITIONAL_CONFLICT, TaxonomyPattern.FACTUAL_CONTRADICTION),
    (TaxonomyPattern.AUTHORITY_CONFLICT, TaxonomyPattern.FACTUAL_CONTRADICTION),
    (TaxonomyPattern.SCOPE_CONFLICT, TaxonomyPattern.DEFINITIONAL_CONFLICT),
    (TaxonomyPattern.VERDICT_CONFLICT, TaxonomyPattern.FACTUAL_CONTRADICTION),
    (TaxonomyPattern.AUTHORITY_STATUS_CONFLICT, TaxonomyPattern.AUTHORITY_CONFLICT),
    (TaxonomyPattern.AUTHORITY_STATUS_CONFLICT, TaxonomyPattern.VERDICT_CONFLICT),
    # TRUSTWORTHY intra-class neighbours
    (TaxonomyPattern.MULTI_SOURCE_CORROBORATION, TaxonomyPattern.EXPERT_CONSENSUS),
    (TaxonomyPattern.MULTI_SOURCE_CORROBORATION, TaxonomyPattern.QUANTITATIVE_CONSENSUS),
    (TaxonomyPattern.SINGLE_AUTHORITATIVE, TaxonomyPattern.DIRECT_ANSWER),
    (TaxonomyPattern.CONSISTENT_CHAIN, TaxonomyPattern.MULTI_SOURCE_CORROBORATION),
    (TaxonomyPattern.RESOLVED_CANDIDATE_SELECTION, TaxonomyPattern.CONSISTENT_CHAIN),
    (TaxonomyPattern.RESOLVED_CANDIDATE_SELECTION, TaxonomyPattern.MULTI_SOURCE_CORROBORATION),
    # CROSS-CLASS — the dangerous near-misses (false_trustworthy traps)
    (TaxonomyPattern.QUANTITATIVE_CONSENSUS, TaxonomyPattern.NUMERICAL_CONFLICT),
    (TaxonomyPattern.MULTI_SOURCE_CORROBORATION, TaxonomyPattern.FACTUAL_CONTRADICTION),
    (TaxonomyPattern.DIRECT_ANSWER, TaxonomyPattern.WRONG_SPECIFICITY),
    (TaxonomyPattern.SINGLE_AUTHORITATIVE, TaxonomyPattern.AUTHORITY_CONFLICT),
    (TaxonomyPattern.PARTIAL_OVERLAP, TaxonomyPattern.DEFINITIONAL_CONFLICT),
    (TaxonomyPattern.WRONG_SPECIFICITY, TaxonomyPattern.NUMERICAL_CONFLICT),
    (TaxonomyPattern.EVIDENCE_ABSENT, TaxonomyPattern.PARTIAL_OVERLAP),
    (TaxonomyPattern.TEMPORAL_MISMATCH, TaxonomyPattern.TEMPORAL_CONFLICT),
    (TaxonomyPattern.MISSING_EXECUTION_RESULT, TaxonomyPattern.DIRECT_ANSWER),
    (TaxonomyPattern.RESOLVED_CANDIDATE_SELECTION, TaxonomyPattern.FACTUAL_CONTRADICTION),
    (TaxonomyPattern.VERSION_BUILD_MISMATCH, TaxonomyPattern.SCOPE_CONFLICT),
]


def neighbors_of(p: TaxonomyPattern) -> list[TaxonomyPattern]:
    """All patterns paired with `p` in `PATTERN_NEIGHBORS` (either direction)."""
    out: set[TaxonomyPattern] = set()
    for a, b in PATTERN_NEIGHBORS:
        if a == p:
            out.add(b)
        elif b == p:
            out.add(a)
    return sorted(out, key=lambda x: x.value)


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------


_NEAR_MISS_INSTRUCTIONS = textwrap.dedent("""\
    ## Near-miss directive

    This case must sit at the BOUNDARY between two patterns:

    - **Primary (gold label)**: {primary_name} — {primary_description}
    - **Runner-up (near miss)**: {secondary_name} — {secondary_description}

    The case must satisfy the PRIMARY pattern (that's the correct label),
    but be written so a careless or surface-reading model would plausibly
    pick the runner-up. The two patterns differ in {differ_in} — make THAT
    difference subtle but real.

    Concretely:

    - The structural test for the primary pattern must still hold (so the
      checker accepts it).
    - The case should LOOK like it could be the runner-up at first glance.
    - `meta.near_miss_class` MUST be set to the runner-up's governance class
      ({secondary_class}).
    - `meta.near_miss_reason` MUST be a one-sentence explanation of WHY a
      naive reader would be tempted toward the runner-up but the primary
      is correct.

    Difficulty is locked to {difficulty} — boundary cases are HARD by
    design, but the requested difficulty still controls how subtle the
    distinction is.
""")


def _differ_in(primary: TaxonomyPattern, secondary: TaxonomyPattern) -> str:
    """One-liner describing what axis the two patterns differ on, used in
    the prompt to focus the generator's attention."""
    cls_p = governance_class_of(primary)
    cls_s = governance_class_of(secondary)
    if cls_p != cls_s:
        return f"governance class itself ({cls_p.value} vs {cls_s.value})"
    return "fine-grained structural pattern within the same class"


def build_near_miss_prompt(
    primary_cell: Cell,
    secondary_pattern: TaxonomyPattern,
    *,
    few_shot_examples: Iterable[dict[str, Any]] = (),
) -> GeneratorPrompt:
    """Render a near-miss prompt: instantiate `primary_cell.pattern` but sit
    on the boundary with `secondary_pattern`."""
    examples = list(few_shot_examples)
    base = BASE_TEMPLATE.format(
        pattern_name=primary_cell.pattern.value,
        governance_class=governance_class_of(primary_cell.pattern).value,
        domain=primary_cell.domain.value,
        difficulty=primary_cell.difficulty.value,
        cell_id=primary_cell.cell_id,
        pattern_description=PATTERN_DESCRIPTIONS[primary_cell.pattern],
        pattern_guidance=PATTERN_GUIDANCE[primary_cell.pattern],
        domain_hints=DOMAIN_HINTS[primary_cell.domain],
        difficulty_hints=DIFFICULTY_HINTS[primary_cell.difficulty],
        few_shot_block=_format_few_shot_block(examples),
        output_schema=OUTPUT_SCHEMA_HINT,
    )
    nm_block = _NEAR_MISS_INSTRUCTIONS.format(
        primary_name=primary_cell.pattern.value,
        primary_description=PATTERN_DESCRIPTIONS[primary_cell.pattern],
        secondary_name=secondary_pattern.value,
        secondary_description=PATTERN_DESCRIPTIONS[secondary_pattern],
        differ_in=_differ_in(primary_cell.pattern, secondary_pattern),
        secondary_class=governance_class_of(secondary_pattern).value,
        difficulty=primary_cell.difficulty.value,
    )
    text = base + "\n\n" + nm_block
    return GeneratorPrompt(cell=primary_cell, text=text, n_few_shots=len(examples))


# ---------------------------------------------------------------------------
# Wrapper orchestrator
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class NearMissOrchestrator:
    """Thin wrapper that swaps the prompt builder for the near-miss variant.

    `base` is a fully-configured `Orchestrator`. `fill_boundary(primary, secondary, n)`
    drives n cases against that boundary; everything else (checker, vault,
    blind labeler) flows through `base`.
    """

    base: Orchestrator

    def fill_boundary(
        self,
        primary_cell: Cell,
        secondary_pattern: TaxonomyPattern,
        *,
        n: int = 1,
        batch_id: str | None = None,
    ) -> list[GenerationResult]:
        results: list[GenerationResult] = []
        for _ in range(n):
            r = self._generate_one(primary_cell, secondary_pattern, batch_id=batch_id)
            results.append(r)
            if r.outcome == Outcome.REJECTED_PROVIDER:
                # Provider issue is global; stop.
                break
        return results

    def _generate_one(
        self,
        primary: Cell,
        secondary: TaxonomyPattern,
        *,
        batch_id: str | None,
    ) -> GenerationResult:
        # Build the near-miss prompt with vault-pulled few-shots from the primary.
        from .prompts import few_shot_for_cell as _few_shot
        from .orchestrator import _patch_cell_metadata, parse_case_json
        from .checker import case_dedup_hash, hashes_from
        from .providers import ProviderError
        from .vault import Provenance

        seen = hashes_from(self.base.vault.iter_cases())
        last: GenerationResult | None = None
        for attempt in range(1, self.base.max_attempts_per_cell + 1):
            examples = _few_shot(
                self.base.vault,
                primary,
                n=self.base.n_few_shots,
                seed=attempt,
            )
            prompt = build_near_miss_prompt(primary, secondary, few_shot_examples=examples)
            req = GenerateRequest(
                prompt=prompt.text,
                system="You generate fitz-gov benchmark cases as JSON only.",
                max_tokens=self.base.max_new_tokens,
                temperature=self.base.generator_temperature,
                metadata={"cell_id": primary.cell_id, "near_miss": secondary.value},
            )
            try:
                raw = self.base.provider.generate(req)
            except ProviderError as exc:
                return GenerationResult(
                    cell=primary, outcome=Outcome.REJECTED_PROVIDER, attempts=attempt,
                    error=f"provider failed: {exc}",
                )
            try:
                case = parse_case_json(raw)
            except ValueError as exc:
                last = GenerationResult(
                    cell=primary, outcome=Outcome.REJECTED_PARSE, attempts=attempt,
                    error=str(exc),
                )
                continue
            case = _patch_cell_metadata(case, primary)
            # Stamp near_miss fields if the generator forgot.
            case.setdefault("meta", {})
            case["meta"].setdefault("near_miss_class", governance_class_of(secondary).value)
            case["meta"].setdefault(
                "near_miss_reason",
                f"Surface reading might suggest {secondary.value}; primary is {primary.pattern.value}.",
            )
            result = self.base.checker.check(case, seen_hashes=seen)
            if not result.passed:
                last = GenerationResult(
                    cell=primary, outcome=Outcome.REJECTED_CHECKER, attempts=attempt,
                    case=case, check_result=result,
                )
                continue
            # Optional blind label
            gen_label = case.get("governance", {}).get("classification")
            val_label = self.base._blind_label(case)
            if val_label is not None and val_label != gen_label:
                self.base._record_conflict(case, gen_label, val_label, batch_id=batch_id or "near-miss")
                return GenerationResult(
                    cell=primary, outcome=Outcome.CONFLICT, attempts=attempt,
                    case=case, check_result=result,
                    generator_label=gen_label, validator_label=val_label,
                )
            self.base.vault.add(
                case,
                provenance=Provenance(
                    provider=self.base.provider.name,
                    provider_version=self.base.provider.version,
                    prompt_version="sdgp-prompts-v1-near-miss",
                    batch_id=batch_id or "near-miss",
                ),
            )
            h = case_dedup_hash(case)
            if h:
                seen.add(h)
            return GenerationResult(
                cell=primary, outcome=Outcome.ACCEPTED, attempts=attempt,
                case=case, check_result=result,
                generator_label=gen_label, validator_label=val_label,
            )
        assert last is not None
        return last
