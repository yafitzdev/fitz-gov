"""Repair V7 blind-label triage rows with provider-authored text patches.

This is intentionally conservative: the target label, taxonomy, routing,
scores, and IDs stay fixed. The provider may only rewrite the query,
context text/summaries, evidence-chain prose, grounding-target prose, and
near-miss explanation so the existing target pattern is semantically clearer.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.checker import Checker
from fitz_gov.sdgp.completeness import audit_case_completeness
from fitz_gov.sdgp.providers import GenerateRequest, LmStudioProvider
from fitz_gov.sdgp.vault import Vault


SYSTEM = (
    "You repair fitz-gov benchmark rows. Output a single JSON object only. "
    "Do not include markdown. Do not change the case id, target label, taxonomy pattern, "
    "cell, domain, or difficulty."
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--vault", type=Path, default=Path("data/sdgp_vault_v51_enriched"))
    p.add_argument(
        "--assessments",
        type=Path,
        default=Path(
            "data/sdgp_v7_qa/triage_recheck_20260523/"
            "score_combined_512_1024/blind_label_assessments.jsonl"
        ),
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/sdgp_v7_qa/triage_repair_20260523"),
    )
    p.add_argument("--model", type=str, default="qwen3.6-35b-a3b@q5_k_s")
    p.add_argument("--base-url", type=str, default="http://localhost:1234")
    p.add_argument("--api-key", type=str, default="lm-studio")
    p.add_argument("--request-timeout-s", type=float, default=300.0)
    p.add_argument("--max-tokens", type=int, default=8192)
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument(
        "--base-cases-jsonl",
        type=Path,
        default=None,
        help='Optional JSONL with rows shaped {"case_id": "...", "case": {...}} to use as repair base.',
    )
    p.add_argument("--resume", action=argparse.BooleanOptionalAction, default=True)
    return p.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            row = json.loads(raw)
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_no}: expected JSON object")
            rows.append(row)
    return rows


def append_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            handle.flush()


def existing_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {str(row.get("case_id") or "") for row in read_jsonl(path)}


def load_case_overrides(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None or not path.exists():
        return {}
    out: dict[str, dict[str, Any]] = {}
    for row in read_jsonl(path):
        case_id = str(row.get("case_id") or "")
        case = row.get("case")
        if case_id and isinstance(case, dict):
            out[case_id] = case
    return out


def compact_case(case: Mapping[str, Any]) -> dict[str, Any]:
    input_block = case.get("input") if isinstance(case.get("input"), Mapping) else {}
    meta = case.get("meta") if isinstance(case.get("meta"), Mapping) else {}
    return {
        "case_id": case.get("id"),
        "target_label": (case.get("governance") or {}).get("classification"),
        "pattern": (case.get("taxonomy") or {}).get("pattern"),
        "cell_id": (case.get("taxonomy") or {}).get("cell_id"),
        "domain": meta.get("domain"),
        "difficulty": meta.get("difficulty"),
        "query": input_block.get("query"),
        "query_rewritten": input_block.get("query_rewritten"),
        "contexts": [
            {
                "id": ctx.get("id"),
                "text": ctx.get("text"),
                "summary": ctx.get("summary"),
                "authority_score": ctx.get("authority_score"),
                "authority_signal": ctx.get("authority_signal"),
                "anchor_period": (ctx.get("temporality") or {}).get("anchor_period"),
            }
            for ctx in input_block.get("contexts", [])
            if isinstance(ctx, Mapping)
        ],
        "evidence_chain_reasoning": (input_block.get("evidence_chain") or {}).get("reasoning"),
        "near_miss_reason": meta.get("near_miss_reason"),
        "grounding_targets": meta.get("grounding_targets"),
    }


def build_prompt(case: Mapping[str, Any], assessment: Mapping[str, Any]) -> str:
    payload = {
        "blind_label_failure": {
            "gold_label": assessment.get("gold_label"),
            "predicted_label": assessment.get("predicted_label"),
            "status": assessment.get("status"),
            "rationale": assessment.get("rationale"),
        },
        "case": compact_case(case),
    }
    return (
        "Repair this one V7 case so a blind labeler should choose gold_label.\n\n"
        "Allowed edits:\n"
        "- input.query and input.query_rewritten\n"
        "- input.contexts[].text and input.contexts[].summary\n"
        "- input.evidence_chain.reasoning\n"
        "- meta.near_miss_reason\n"
        "- meta.grounding_targets text/attributions for TRUSTWORTHY rows only\n\n"
        "Do not change the target label, taxonomy pattern, cell_id, domain, difficulty, "
        "context ids, or number of contexts.\n\n"
        "Pattern requirements:\n"
        "- DISPUTED rows must contain answer-relevant incompatible answer candidates. "
        "Do not make the conflict dismissible as irrelevant noise.\n"
        "- ABSTAIN rows must leave the queried answer genuinely unsupported, stale, "
        "too broad, or out of scope. Do not let a careful answer be fully grounded.\n"
        "- TRUSTWORTHY rows must fully support one grounded answer with no material "
        "scope/time/entity gap.\n\n"
        "Return exactly this JSON shape:\n"
        '{"case_id":"...","query":"...","query_rewritten":"...",'
        '"contexts":[{"id":"ctx_001","text":"...","summary":"..."}],'
        '"evidence_chain_reasoning":"...",'
        '"near_miss_reason":"...",'
        '"grounding_targets":{"gold_answer":"...","sentences":[{"text":"...",'
        '"attributions":["ctx_001"]}]}}\n'
        "Omit grounding_targets unless the gold label is TRUSTWORTHY.\n\n"
        f"INPUT:\n{json.dumps(payload, ensure_ascii=False)}"
    )


def last_json_object(text: str) -> dict[str, Any] | None:
    decoder = json.JSONDecoder()
    found: list[dict[str, Any]] = []
    for idx, char in enumerate(text):
        if char != "{":
            continue
        try:
            payload, _ = decoder.raw_decode(text[idx:])
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            found.append(payload)
    for payload in reversed(found):
        if "case_id" in payload:
            return payload
    return found[-1] if found else None


def apply_patch_to_case(case: dict[str, Any], patch: Mapping[str, Any]) -> dict[str, Any]:
    out = json.loads(json.dumps(case, ensure_ascii=False))
    input_block = out.setdefault("input", {})
    meta = out.setdefault("meta", {})

    if isinstance(patch.get("query"), str) and patch["query"].strip():
        input_block["query"] = patch["query"].strip()
    if isinstance(patch.get("query_rewritten"), str) and patch["query_rewritten"].strip():
        input_block["query_rewritten"] = patch["query_rewritten"].strip()

    patch_contexts = {
        str(ctx.get("id") or ""): ctx
        for ctx in patch.get("contexts", [])
        if isinstance(ctx, Mapping)
    }
    for ctx in input_block.get("contexts", []):
        if not isinstance(ctx, dict):
            continue
        patch_ctx = patch_contexts.get(str(ctx.get("id") or ""))
        if not patch_ctx:
            continue
        if isinstance(patch_ctx.get("text"), str) and patch_ctx["text"].strip():
            ctx["text"] = patch_ctx["text"].strip()
        if isinstance(patch_ctx.get("summary"), str) and patch_ctx["summary"].strip():
            ctx["summary"] = patch_ctx["summary"].strip()

    if isinstance(patch.get("evidence_chain_reasoning"), str):
        contexts = input_block.get("contexts") or []
        if len(contexts) >= 2:
            chain = input_block.setdefault("evidence_chain", {})
            chain.setdefault("order", [ctx.get("id") for ctx in contexts if isinstance(ctx, dict)])
            chain["reasoning"] = patch["evidence_chain_reasoning"].strip()

    if isinstance(patch.get("near_miss_reason"), str) and patch["near_miss_reason"].strip():
        meta["near_miss_reason"] = patch["near_miss_reason"].strip()

    if (out.get("governance") or {}).get("classification") == "TRUSTWORTHY":
        grounding_targets = patch.get("grounding_targets")
        if isinstance(grounding_targets, Mapping):
            meta["grounding_targets"] = grounding_targets

    vault_meta = out.setdefault("_vault", {})
    vault_meta["last_modified_at"] = (
        datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    )
    vault_meta["revisions"] = int(vault_meta.get("revisions") or 1) + 1
    return out


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    log_path = args.out_dir / "repair_log.jsonl"
    repaired_path = args.out_dir / "repaired_cases.jsonl"
    raw_path = args.out_dir / "raw_responses.jsonl"

    assessments = [
        row for row in read_jsonl(args.assessments) if row.get("status") != "agree"
    ]
    if args.limit is not None:
        assessments = assessments[: args.limit]
    done = existing_ids(log_path) if args.resume else set()
    pending = [row for row in assessments if str(row.get("case_id") or "") not in done]

    vault = Vault.open(args.vault)
    overrides = load_case_overrides(args.base_cases_jsonl)
    provider = LmStudioProvider(
        model_id=args.model,
        base_url=args.base_url,
        api_key=args.api_key,
        request_timeout_s=args.request_timeout_s,
    )
    checker = Checker(require_training_schema=True)

    print("=== V7 triage repair ===")
    print(f"Assessments: {args.assessments}")
    print(f"Pending    : {len(pending)} / {len(assessments)}")
    print(f"Out dir    : {args.out_dir}")
    print(f"Provider   : {provider.name} ({provider.version})")

    ok = 0
    bad = 0
    for idx, assessment in enumerate(pending, start=1):
        case_id = str(assessment.get("case_id") or "")
        case = overrides.get(case_id) or vault.get(case_id)
        if case is None:
            append_jsonl(log_path, [{"case_id": case_id, "status": "missing_case"}])
            bad += 1
            continue

        raw = provider.generate(
            GenerateRequest(
                prompt=build_prompt(case, assessment),
                system=SYSTEM,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
                metadata={"case_id": case_id, "task": "v7_triage_repair"},
            )
        )
        patch = last_json_object(raw)
        append_jsonl(raw_path, [{"case_id": case_id, "raw_response": raw}])
        if patch is None:
            append_jsonl(log_path, [{"case_id": case_id, "status": "parse_failed"}])
            bad += 1
            continue
        if str(patch.get("case_id") or "") != case_id:
            append_jsonl(
                log_path,
                [{"case_id": case_id, "status": "case_id_mismatch", "patch": patch}],
            )
            bad += 1
            continue

        repaired = apply_patch_to_case(case, patch)
        check = checker.check(repaired)
        completeness = audit_case_completeness(repaired)
        if check.errors or completeness:
            append_jsonl(
                log_path,
                [
                    {
                        "case_id": case_id,
                        "status": "validation_failed",
                        "checker_errors": [issue.message for issue in check.errors],
                        "completeness": [issue.path for issue in completeness],
                    }
                ],
            )
            bad += 1
            continue

        append_jsonl(repaired_path, [{"case_id": case_id, "case": repaired}])
        append_jsonl(log_path, [{"case_id": case_id, "status": "repaired"}])
        ok += 1
        if idx % 10 == 0:
            print(f"processed={idx} repaired={ok} bad={bad} last_case={case_id}", flush=True)

    print(f"Repaired: {ok}")
    print(f"Bad     : {bad}")
    print(f"Log     : {log_path}")
    print(f"Cases   : {repaired_path}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
