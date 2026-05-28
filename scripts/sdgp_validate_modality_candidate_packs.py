"""Deterministic validator for the modality candidate packs.

Validates the workspaces produced by ``sdgp_generate_modality_candidate_packs.py``::

    data/_workspaces/handoff/modality_structured_v1_20260527/cases.jsonl
    data/_workspaces/handoff/modality_code_v1_20260527/cases.jsonl

Writes a ``validation_report.json`` into each workspace and exits non-zero if
any check fails.

Checks performed:

- JSONL parses cleanly.
- Exactly 10,000 rows per modality.
- Unique IDs across all generated rows.
- No ID collisions with ``data/fitz-gov/cases.jsonl`` (canonical V8 vault).
- No ID collisions with ``data/modality_probes/*/cases.jsonl`` (probe seeds).
- Required top-level fields exist (id, version, input, governance, taxonomy,
  routing, meta, evaluation, _vault).
- No forbidden shim fields (``taxonomy.subpattern``, ``meta.introduced_in``,
  pre-SDGP report axes in ``meta``).
- ``meta.modality`` matches the workspace modality.
- ``meta.dataset_version == "v8"``.
- ``governance.classification == taxonomy.governance_class``.
- ``taxonomy.pattern`` is from the canonical V8 pattern set.
- Label counts: exactly 1,000 / 1,000 / 1,000 per modality.
- TRUSTWORTHY ``meta.grounding_targets`` attribution IDs exist in
  ``input.contexts``.
- Context IDs are unique within each row.
- ``evaluation.mode == "governance"`` and ``check_mode_match`` true.
- Probability scalars are coherent (in [0, 1] and argmax matches
  classification).
- Every row passes the canonical fitz-gov SDGP checker with
  ``require_training_schema=True``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from fitz_gov.sdgp.checker import Checker

CANONICAL = Path("data/fitz-gov/cases.jsonl")
PROBE_PATHS = [
    Path("data/modality_probes/structured/cases.jsonl"),
    Path("data/modality_probes/code/cases.jsonl"),
]

WORKSPACES = [
    ("structured", Path("data/_workspaces/handoff/modality_structured_v1_20260527")),
    ("code", Path("data/_workspaces/handoff/modality_code_v1_20260527")),
]

REQUIRED_TOP_LEVEL = ["id", "version", "input", "governance", "taxonomy", "routing", "meta", "evaluation", "_vault"]

FORBIDDEN_TAXONOMY = ["subpattern", "subpattern_cell_id", "subpattern_description"]
FORBIDDEN_META_KEYS = [
    "introduced_in",
    "domain",
    "subcategory",
    "reasoning_type",
    "query_type",
    "evidence_pattern",
]
FORBIDDEN_TOP_KEYS = ["source_type"]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise RuntimeError(f"{path}:{n}: bad json: {e}")
    return rows


def load_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    ids: set[str] = set()
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            ids.add(row["id"])
    return ids


def canonical_patterns() -> set[str]:
    pats: set[str] = set()
    if CANONICAL.exists():
        with CANONICAL.open("r", encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                row = json.loads(line)
                pats.add(row["taxonomy"]["pattern"])
    return pats


def validate_modality(
    modality: str,
    rows: list[dict[str, Any]],
    *,
    canonical_ids: set[str],
    probe_ids: set[str],
    cross_ids: set[str],
    allowed_patterns: set[str],
) -> dict[str, Any]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    label_counts: dict[str, int] = {}
    checker = Checker(require_training_schema=True)

    if len(rows) != 10000:
        errors.append(f"expected 10000 rows, got {len(rows)}")

    for row in rows:
        cid = row.get("id", "<missing-id>")
        # Required keys
        for k in REQUIRED_TOP_LEVEL:
            if k not in row:
                errors.append(f"{cid}: missing top-level key {k}")
        # ID uniqueness
        if cid in seen_ids:
            errors.append(f"{cid}: duplicate id within modality")
        seen_ids.add(cid)
        if cid in canonical_ids:
            errors.append(f"{cid}: id collides with canonical vault")
        if cid in probe_ids:
            errors.append(f"{cid}: id collides with probe seeds")
        if cid in cross_ids:
            errors.append(f"{cid}: id collides with sibling modality candidate")
        # Forbidden top keys
        for k in FORBIDDEN_TOP_KEYS:
            if k in row:
                errors.append(f"{cid}: forbidden top-level key {k}")
        # Taxonomy
        tax = row.get("taxonomy", {})
        for k in FORBIDDEN_TAXONOMY:
            if k in tax:
                errors.append(f"{cid}: forbidden taxonomy field taxonomy.{k}")
        pat = tax.get("pattern")
        if pat not in allowed_patterns:
            errors.append(f"{cid}: taxonomy.pattern '{pat}' not in canonical V8 pattern set")
        gc = tax.get("governance_class")
        cls = row.get("governance", {}).get("classification")
        if gc != cls:
            errors.append(f"{cid}: taxonomy.governance_class={gc} != governance.classification={cls}")
        # meta
        meta = row.get("meta", {})
        if meta.get("modality") != modality:
            errors.append(f"{cid}: meta.modality={meta.get('modality')} != {modality}")
        if meta.get("dataset_version") != "v8":
            errors.append(f"{cid}: meta.dataset_version must be 'v8'")
        for k in FORBIDDEN_META_KEYS:
            if k in meta:
                errors.append(f"{cid}: forbidden meta key meta.{k}")
        # evaluation
        ev = row.get("evaluation", {})
        if ev.get("mode") != "governance":
            errors.append(f"{cid}: evaluation.mode must be 'governance'")
        if ev.get("check_mode_match") is not True:
            errors.append(f"{cid}: evaluation.check_mode_match must be true")
        # governance probabilities
        gov = row.get("governance", {})
        for k in ("abstain", "disputed", "trustworthy"):
            v = gov.get(k)
            if not (isinstance(v, (int, float)) and 0.0 <= v <= 1.0):
                errors.append(f"{cid}: governance.{k} out of [0,1]: {v}")
        argmax_k = max(("abstain", "disputed", "trustworthy"), key=lambda kk: gov.get(kk, -1))
        if argmax_k.upper() != cls:
            errors.append(f"{cid}: argmax({argmax_k}) does not match classification {cls}")
        # contexts
        contexts = row.get("input", {}).get("contexts", [])
        if not contexts:
            errors.append(f"{cid}: input.contexts is empty")
        ctx_ids = [c.get("id") for c in contexts]
        if len(set(ctx_ids)) != len(ctx_ids):
            errors.append(f"{cid}: duplicate context ids: {ctx_ids}")
        # routing
        routing = row.get("routing", {})
        if not routing.get("expert_fired"):
            errors.append(f"{cid}: routing.expert_fired missing")
        rc = routing.get("routing_confidence")
        if not (isinstance(rc, (int, float)) and 0.0 <= rc <= 1.0):
            errors.append(f"{cid}: routing.routing_confidence out of [0,1]: {rc}")
        # trustworthy grounding_targets
        if cls == "TRUSTWORTHY":
            gt = meta.get("grounding_targets")
            if not gt:
                errors.append(f"{cid}: TRUSTWORTHY missing meta.grounding_targets")
            else:
                if not gt.get("gold_answer"):
                    errors.append(f"{cid}: TRUSTWORTHY missing gold_answer")
                ctx_id_set = set(ctx_ids)
                for sent in gt.get("sentences", []):
                    for att in sent.get("attributions", []):
                        if att not in ctx_id_set:
                            errors.append(f"{cid}: grounding attribution {att} not in context ids")
        # required_elements should exist (list)
        if not isinstance(ev.get("required_elements"), list):
            errors.append(f"{cid}: evaluation.required_elements must be a list")
        if not isinstance(ev.get("forbidden_claims"), list):
            errors.append(f"{cid}: evaluation.forbidden_claims must be a list")
        # labels
        label_counts[cls] = label_counts.get(cls, 0) + 1
        # canonical checker
        check = checker.check(row)
        if not check.passed:
            for issue in check.errors:
                errors.append(f"{cid}: checker.{issue.rule}: {issue.message}")

    expected = {"TRUSTWORTHY": 3333, "DISPUTED": 3333, "ABSTAIN": 3334}
    if label_counts != expected:
        errors.append(f"label counts not 3333/3333/3334: {label_counts}")

    return {
        "modality": modality,
        "rows": len(rows),
        "label_counts": label_counts,
        "errors": errors,
        "ok": len(errors) == 0,
    }


def main() -> int:
    canonical_ids = load_ids(CANONICAL)
    probe_ids: set[str] = set()
    for p in PROBE_PATHS:
        probe_ids |= load_ids(p)
    allowed_patterns = canonical_patterns()

    workspaces_loaded: list[tuple[str, Path, list[dict[str, Any]]]] = []
    for modality, ws in WORKSPACES:
        cases = ws / "cases.jsonl"
        rows = load_jsonl(cases)
        workspaces_loaded.append((modality, ws, rows))

    # cross-modality id set
    all_ids = set()
    cross_overlap = set()
    for _, _, rows in workspaces_loaded:
        for r in rows:
            cid = r["id"]
            if cid in all_ids:
                cross_overlap.add(cid)
            all_ids.add(cid)

    overall_ok = True
    for modality, ws, rows in workspaces_loaded:
        other_ids = set()
        for m2, _, r2 in workspaces_loaded:
            if m2 == modality:
                continue
            other_ids |= {r["id"] for r in r2}
        report = validate_modality(
            modality, rows,
            canonical_ids=canonical_ids,
            probe_ids=probe_ids,
            cross_ids=other_ids,
            allowed_patterns=allowed_patterns,
        )
        if cross_overlap:
            report["errors"].append(f"cross-modality id collisions: {sorted(cross_overlap)[:5]}")
            report["ok"] = False
        out = ws / "validation_report.json"
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[{modality}] rows={report['rows']} labels={report['label_counts']} ok={report['ok']} errors={len(report['errors'])}")
        if report["errors"]:
            for e in report["errors"][:10]:
                print("  -", e)
        overall_ok = overall_ok and report["ok"]
    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
