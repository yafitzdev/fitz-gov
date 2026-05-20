"""SDGP orchestrator — ties gap detector + provider + prompts + checker + vault.

One entry point: `Orchestrator(vault, provider, ...).fill_gaps(gaps, n_per_cell=1)`.
For each (cell, n) it builds a prompt, calls the provider, parses the JSON
output, runs the checker, optionally blind-labels with a second provider,
and either:

  - **accepts** → adds to vault
  - **rejects** → logs the failure, retries up to `max_attempts_per_cell`
  - **conflicts** → blind labeler disagreed with the generator's label →
    writes the case to `<vault>/conflicts/<batch_id>/<case_id>.json` for
    triage and skips the vault

Designed to be re-entrant and crash-safe: vault append is atomic, the
gap detector is rebuilt from vault state on each call, so a re-run resumes
from where the last left off.
"""

from __future__ import annotations

import json
import re
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Iterable

from .checker import CheckResult, Checker, case_dedup_hash, hashes_from
from .gap_detector import Gap, GapDetector
from .prompts import (
    SYSTEM_MESSAGE,
    GeneratorPrompt,
    build_prompt_for_cell,
)
from .providers import (
    BlindLabelPair,
    GenerateRequest,
    Provider,
    ProviderError,
)
from .taxonomy import (
    Cell,
    GovernanceClass,
    TaxonomyPattern,
    governance_class_of,
)
from .vault import Provenance, Vault, new_batch_id


# ---------------------------------------------------------------------------
# Outcome shape
# ---------------------------------------------------------------------------


class Outcome(str, Enum):
    ACCEPTED = "accepted"
    REJECTED_PARSE = "rejected_parse"
    REJECTED_CHECKER = "rejected_checker"
    REJECTED_PROVIDER = "rejected_provider"
    CONFLICT = "conflict"


@dataclass(slots=True)
class GenerationResult:
    cell: Cell
    outcome: Outcome
    attempts: int
    case: dict[str, Any] | None = None
    check_result: CheckResult | None = None
    generator_label: str | None = None
    validator_label: str | None = None
    error: str | None = None


@dataclass(slots=True)
class BatchReport:
    """Aggregate stats from a single `fill_gaps()` call."""

    started_at: str
    finished_at: str = ""
    batch_id: str = ""
    counts: dict[str, int] = field(default_factory=dict)
    results: list[GenerationResult] = field(default_factory=list)

    def add(self, r: GenerationResult) -> None:
        self.results.append(r)
        self.counts[r.outcome.value] = self.counts.get(r.outcome.value, 0) + 1

    @property
    def n_total(self) -> int:
        return sum(self.counts.values())

    def summary(self) -> str:
        lines = [
            f"BatchReport batch_id={self.batch_id} n_total={self.n_total}",
            *(f"  {k}: {v}" for k, v in sorted(self.counts.items())),
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# JSON parsing — robust to common LLM wrappings
# ---------------------------------------------------------------------------


_FENCED_JSON = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)
_FIRST_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


def parse_case_json(raw: str) -> dict[str, Any]:
    """Best-effort JSON extraction from an LLM response.

    Handles:
      - Plain JSON
      - JSON inside ```json...``` fences
      - JSON with prose before/after (picks the first top-level object)

    Raises ValueError if nothing parses.
    """
    if not raw or not raw.strip():
        raise ValueError("empty response")
    text = raw.strip()
    # Try plain
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    # Try fenced
    m = _FENCED_JSON.search(text)
    if m:
        try:
            obj = json.loads(m.group(1))
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            pass
    # Try first object
    m = _FIRST_OBJECT.search(text)
    if m:
        try:
            obj = json.loads(m.group(0))
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            pass
    raise ValueError(f"could not extract JSON object from response (len={len(raw)})")


# ---------------------------------------------------------------------------
# Blind labeler
# ---------------------------------------------------------------------------


_BLIND_LABEL_SYSTEM = (
    "You are a strict label validator for the fitz-gov RAG governance benchmark. "
    "Given a (query, contexts) pair, output EXACTLY ONE word on its own line: "
    "ABSTAIN, DISPUTED, or TRUSTWORTHY. No explanation, no punctuation, no "
    "fences. Use ABSTAIN when the sources don't contain enough information to "
    "answer; DISPUTED when sources contradict each other on the answer; "
    "TRUSTWORTHY when sources consistently and sufficiently support an answer."
)


def _build_blind_label_prompt(case: dict[str, Any]) -> str:
    query = case.get("input", {}).get("query", case.get("query", ""))
    raw_ctxs = (
        case.get("input", {}).get("contexts")
        or case.get("contexts")
        or []
    )
    texts = []
    for i, c in enumerate(raw_ctxs, start=1):
        t = c.get("text", "") if isinstance(c, dict) else str(c)
        texts.append(f"[{i}] {t}")
    return (
        f"Question: {query}\n\n"
        f"Sources:\n" + "\n".join(texts) + "\n\n"
        "Reply with ABSTAIN, DISPUTED, or TRUSTWORTHY."
    )


def _parse_blind_label(raw: str) -> str | None:
    """Pull the first of ABSTAIN/DISPUTED/TRUSTWORTHY from the response."""
    if not raw:
        return None
    upper = raw.upper()
    for lab in ("ABSTAIN", "DISPUTED", "TRUSTWORTHY"):
        if lab in upper:
            return lab
    return None


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class Orchestrator:
    """SDGP orchestrator. Stateless across calls; safe to reuse.

    `provider` generates cases. `blind_label_pair` (optional, but ROADMAP §4
    requires it for any vault-bound generation: "generator and validator must
    never be the same model") supplies the second-pass labeler. `checker` is
    the structural validator from `sdgp.checker`. `vault` is the destination.

    `prompt_seed_offset` is added to the per-cell seed to perturb the few-shot
    selection across runs without losing reproducibility within a run.
    """

    vault: Vault
    provider: Provider
    blind_label_pair: BlindLabelPair | None = None
    checker: Checker = field(default_factory=Checker)
    max_new_tokens: int = 2048
    generator_temperature: float = 0.7
    validator_temperature: float = 0.0
    n_few_shots: int = 2
    max_attempts_per_cell: int = 3
    prompt_seed_offset: int = 0

    # ---- Generation ----------------------------------------------------

    def _generate_once(
        self,
        cell: Cell,
        *,
        seen_hashes: set[str],
        prompt_seed: int | None,
    ) -> tuple[Outcome, dict[str, Any] | None, CheckResult | None, str | None]:
        """Single attempt at a cell. Returns (outcome, case, check_result, error_message)."""
        prompt: GeneratorPrompt
        try:
            prompt = build_prompt_for_cell(
                cell, self.vault, n_few_shots=self.n_few_shots, seed=prompt_seed
            )
        except Exception as exc:
            return Outcome.REJECTED_PROVIDER, None, None, f"prompt build failed: {exc}"

        req = GenerateRequest(
            prompt=prompt.text,
            system=SYSTEM_MESSAGE,
            max_tokens=self.max_new_tokens,
            temperature=self.generator_temperature,
            metadata={"cell_id": cell.cell_id},
        )
        try:
            raw = self.provider.generate(req)
        except ProviderError as exc:
            return Outcome.REJECTED_PROVIDER, None, None, f"provider failed: {exc}"

        try:
            case = parse_case_json(raw)
        except ValueError as exc:
            return Outcome.REJECTED_PARSE, None, None, f"parse failed: {exc} | raw[:200]={raw[:200]!r}"

        # Make sure the case carries cell metadata even if the generator forgot.
        case = _patch_cell_metadata(case, cell)

        result = self.checker.check(case, seen_hashes=seen_hashes)
        if not result.passed:
            return Outcome.REJECTED_CHECKER, case, result, None
        return Outcome.ACCEPTED, case, result, None

    def _blind_label(self, case: dict[str, Any]) -> str | None:
        if self.blind_label_pair is None:
            return None
        try:
            validator = self.blind_label_pair.validator_for(self.provider)
        except ValueError:
            return None
        req = GenerateRequest(
            prompt=_build_blind_label_prompt(case),
            system=_BLIND_LABEL_SYSTEM,
            max_tokens=32,
            temperature=self.validator_temperature,
        )
        try:
            raw = validator.generate(req)
        except ProviderError:
            return None
        return _parse_blind_label(raw)

    # ---- Public API ----------------------------------------------------

    def generate_one_cell(
        self,
        cell: Cell,
        *,
        seen_hashes: set[str] | None = None,
        batch_id: str | None = None,
    ) -> GenerationResult:
        """Fill one case for one cell. Retries up to max_attempts_per_cell on
        parse/checker rejections (but not on provider errors — those usually
        mean a config problem, retrying won't help)."""
        seen = seen_hashes if seen_hashes is not None else set()
        batch = batch_id or "ad-hoc"
        last_failure: GenerationResult | None = None
        for attempt in range(1, self.max_attempts_per_cell + 1):
            seed = (self.prompt_seed_offset + attempt) if self.prompt_seed_offset else None
            outcome, case, check, err = self._generate_once(
                cell, seen_hashes=seen, prompt_seed=seed
            )

            if outcome == Outcome.REJECTED_PROVIDER:
                # Provider issue — don't burn retries.
                return GenerationResult(
                    cell=cell, outcome=outcome, attempts=attempt, error=err
                )

            if outcome == Outcome.ACCEPTED:
                gen_label = (case or {}).get("governance", {}).get("classification")
                val_label = self._blind_label(case) if case else None
                if val_label is not None and val_label != gen_label:
                    # Blind-label disagreement → conflict, NOT vaulted.
                    self._record_conflict(case, gen_label, val_label, batch_id=batch)
                    return GenerationResult(
                        cell=cell,
                        outcome=Outcome.CONFLICT,
                        attempts=attempt,
                        case=case,
                        check_result=check,
                        generator_label=gen_label,
                        validator_label=val_label,
                    )
                # Accept + vault.
                self.vault.add(
                    case,
                    provenance=Provenance(
                        provider=self.provider.name,
                        provider_version=self.provider.version,
                        prompt_version="sdgp-prompts-v1",
                        batch_id=batch,
                    ),
                )
                # Add hash so subsequent cases in the batch dedup against it.
                h = case_dedup_hash(case)
                if h:
                    seen.add(h)
                return GenerationResult(
                    cell=cell,
                    outcome=Outcome.ACCEPTED,
                    attempts=attempt,
                    case=case,
                    check_result=check,
                    generator_label=gen_label,
                    validator_label=val_label,
                )

            # REJECTED_PARSE or REJECTED_CHECKER — retry.
            last_failure = GenerationResult(
                cell=cell, outcome=outcome, attempts=attempt,
                case=case, check_result=check, error=err,
            )
        # Exhausted retries
        assert last_failure is not None
        return last_failure

    def fill_gaps(
        self,
        gaps: Iterable[Gap],
        *,
        n_per_cell: int = 1,
        batch_id: str | None = None,
        on_result: "callable | None" = None,  # type: ignore[name-defined]
    ) -> BatchReport:
        """Walk a gap queue and try to fill each cell up to n_per_cell times.

        `on_result` is called after each `GenerationResult` — useful for
        progress logging. Returns a `BatchReport` with per-outcome counts.
        """
        bid = batch_id or new_batch_id()
        report = BatchReport(
            started_at=_utcnow_iso(), batch_id=bid
        )
        # Seed dedup with what's already in the vault so we never re-emit.
        seen = hashes_from(self.vault.iter_cases())

        for gap in gaps:
            for _ in range(n_per_cell):
                r = self.generate_one_cell(gap.cell, seen_hashes=seen, batch_id=bid)
                report.add(r)
                if on_result is not None:
                    on_result(r)
                if r.outcome == Outcome.REJECTED_PROVIDER:
                    # Provider failure is global — abort the batch.
                    report.finished_at = _utcnow_iso()
                    return report

        report.finished_at = _utcnow_iso()
        return report

    # ---- Conflict queue ------------------------------------------------

    def _conflicts_dir(self, batch_id: str) -> Path:
        d = self.vault.root / "conflicts" / batch_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _record_conflict(
        self,
        case: dict[str, Any],
        generator_label: str | None,
        validator_label: str | None,
        *,
        batch_id: str,
    ) -> Path:
        d = self._conflicts_dir(batch_id)
        case_id = case.get("id") or f"conflict_{uuid.uuid4().hex[:8]}"
        path = d / f"{case_id}.json"
        payload = {
            "case": case,
            "generator_label": generator_label,
            "validator_label": validator_label,
            "generator_provider": self.provider.name,
            "validator_provider": (
                self.blind_label_pair.validator_for(self.provider).name
                if self.blind_label_pair
                else None
            ),
            "recorded_at": _utcnow_iso(),
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def list_conflicts(self) -> list[Path]:
        root = self.vault.root / "conflicts"
        if not root.exists():
            return []
        return sorted(root.rglob("*.json"))


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def _utcnow_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _patch_cell_metadata(case: dict[str, Any], cell: Cell) -> dict[str, Any]:
    """Ensure the case carries the cell's metadata even if the generator
    omitted or wrongly stated it. The checker would catch a mismatch as an
    error; here we'd rather force-align than burn a retry on a missing field."""
    case.setdefault("taxonomy", {})
    case["taxonomy"].setdefault("pattern", cell.pattern.value)
    case["taxonomy"].setdefault("governance_class", governance_class_of(cell.pattern).value)
    case["taxonomy"].setdefault("cell_id", cell.cell_id)
    case.setdefault("routing", {})
    case["routing"].setdefault("expert_fired", cell.domain.value)
    case.setdefault("meta", {})
    case["meta"].setdefault("difficulty", cell.difficulty.value)
    case.setdefault("governance", {})
    case["governance"].setdefault(
        "classification", governance_class_of(cell.pattern).value
    )
    return case
