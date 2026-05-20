"""sdgp_enrich_v51_llm.py — Phase 0b: LLM-enrich the V5.1-enriched vault.

Replaces `<TODO_LLM>` markers and Phase 0a heuristic stubs with real LLM-
generated values for the fields that require reasoning:

  - input.query_rewritten
  - input.contexts[].{summary, relevance_to_query, temporality.anchor_period}
  - governance.{hallucination_pressure, retrieval_retry_value,
                query_evidence_alignment, answer_coverage,
                boundary_proximity.distance}
  - meta.near_miss_reason

Driver provider is picked via --provider:
  - `local`   LocalLlmProvider (Ollama at $SDGP_LOCAL_URL, default
              http://localhost:11434, model from $SDGP_LOCAL_MODEL).
  - `handoff` FileHandoffProvider (subagent loop via files at
              $SDGP_HANDOFF_DIR or --handoff-dir).
  - `env`     Auto-detect from env vars.

Resumable: skips cases that already have all the LLM fields populated
(no `<TODO_LLM>` markers remain). Pass --force to re-enrich.

Usage:
    # Local Ollama:
    SDGP_LOCAL_MODEL=qwen3.5:0.8b python scripts/sdgp_enrich_v51_llm.py --provider local

    # Subagent loop (Claude Code / Codex pulls from handoff dir):
    python scripts/sdgp_enrich_v51_llm.py --provider handoff --handoff-dir data/sdgp_handoff
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.cost import CostTracker
from fitz_gov.sdgp.llm_enrich import (
    case_needs_enrichment,
    enrich_case_with_provider,
)
from fitz_gov.sdgp.providers import (
    FileHandoffProvider,
    LocalLlmProvider,
    Provider,
    ProviderError,
    StubProvider,
    providers_from_env,
)
from fitz_gov.sdgp.vault import Vault


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--vault", type=Path, default=Path("data/sdgp_vault_v51_enriched"))
    p.add_argument("--provider", choices=["local", "handoff", "env", "stub"], default="env")
    p.add_argument("--handoff-dir", type=Path, default=None)
    p.add_argument("--local-model", type=str, default=None)
    p.add_argument("--local-url", type=str, default=None)
    p.add_argument("--limit", type=int, default=None, help="Process at most N cases this run")
    p.add_argument("--force", action="store_true", help="Re-enrich cases even if no TODO markers remain")
    p.add_argument("--max-tokens", type=int, default=1500)
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--cost-report", type=Path, default=None)
    p.add_argument("--dry-run", action="store_true", help="List cases needing enrichment and exit")
    p.add_argument("--max-failures", type=int, default=10,
                   help="Abort after this many consecutive provider failures")
    return p.parse_args()


def build_provider(args: argparse.Namespace) -> Provider:
    if args.provider == "env":
        ps = providers_from_env()
        if not ps:
            raise SystemExit("--provider env: no SDGP_LOCAL_MODEL or SDGP_HANDOFF_DIR set")
        return ps[0]
    if args.provider == "local":
        return LocalLlmProvider(
            model_id=args.local_model or os.environ.get("SDGP_LOCAL_MODEL", "qwen3.5:0.8b"),
            base_url=args.local_url or os.environ.get("SDGP_LOCAL_URL", "http://localhost:11434"),
        )
    if args.provider == "handoff":
        return FileHandoffProvider(
            handoff_dir=args.handoff_dir or Path(os.environ.get("SDGP_HANDOFF_DIR", "data/sdgp_handoff")),
            timeout_s=float(os.environ.get("SDGP_HANDOFF_TIMEOUT", "900")),
        )
    if args.provider == "stub":
        return StubProvider(response='{"query_rewritten":"stub"}', name="stub", version="0")
    raise SystemExit(f"unknown provider: {args.provider}")


def main() -> int:
    args = parse_args()
    print(f"=== SDGP Phase 0b LLM enrichment ===")
    print(f"Vault    : {args.vault}")
    print(f"Provider : {args.provider}")
    print(f"Force    : {args.force}")
    print(f"Limit    : {args.limit}")
    print()

    vault = Vault.open(args.vault)
    print(f"Vault size: {len(vault)} cases")

    # Find cases needing enrichment
    todo_cases: list[dict] = []
    for case in vault.iter_cases():
        if args.force or case_needs_enrichment(case):
            todo_cases.append(case)
    print(f"Cases needing enrichment: {len(todo_cases)}")
    if args.limit:
        todo_cases = todo_cases[: args.limit]
        print(f"--limit applied: processing {len(todo_cases)}")

    if args.dry_run:
        print("\nSample case ids needing enrichment:")
        for case in todo_cases[:20]:
            print(f"  {case['id']}")
        return 0

    if not todo_cases:
        print("Nothing to enrich. Exiting.")
        return 0

    provider = build_provider(args)
    print(f"\nProvider : {provider}")
    healthy = provider.healthcheck()
    print(f"Healthy  : {healthy}")
    if not healthy:
        print(f"WARN: provider healthcheck failed — calls may fail", file=sys.stderr)

    tracker = CostTracker()
    updates: dict[str, dict] = {}
    n_changed = 0
    consecutive_failures = 0
    t0 = time.time()

    for i, case in enumerate(todo_cases, start=1):
        cid = case["id"]
        try:
            res = enrich_case_with_provider(
                case, provider,
                max_tokens=args.max_tokens, temperature=args.temperature,
            )
            tracker.record(
                provider=provider.name, cell_id=case.get("taxonomy", {}).get("cell_id", "?"),
                request_text="<built per-case>", response_text="<received>",
                outcome="accepted" if res.changed else "no_change",
            )
            if res.changed:
                updates[cid] = case
                n_changed += 1
            consecutive_failures = 0
        except ProviderError as exc:
            consecutive_failures += 1
            print(f"  [{i}/{len(todo_cases)}] {cid}: PROVIDER FAIL {exc}", file=sys.stderr)
            if consecutive_failures >= args.max_failures:
                print(f"\nABORT: {consecutive_failures} consecutive provider failures", file=sys.stderr)
                break
            continue
        except ValueError as exc:
            print(f"  [{i}/{len(todo_cases)}] {cid}: parse fail {exc}", file=sys.stderr)
            consecutive_failures = 0
            continue
        if i % 25 == 0 or i == len(todo_cases):
            rate = i / max(time.time() - t0, 1e-6)
            print(f"  [{i}/{len(todo_cases)}] changed={n_changed} rate={rate:.2f}/s")

    # Persist updates in one atomic JSONL rewrite
    if updates:
        print(f"\nWriting {len(updates)} updated cases back to vault...")
        res = vault.update_cases(updates)
        print(f"  updated      : {res['updated']}")
        print(f"  passthrough  : {res['passthrough']}")
        print(f"  unknown_ids  : {res['unknown']}")
    else:
        print("\nNo updates to persist.")

    # Cost report
    if args.cost_report is None:
        args.cost_report = vault.root / "cost_reports" / f"phase_0b_{int(time.time())}.json"
    args.cost_report = Path(args.cost_report)
    tracker.write_report(args.cost_report)
    print(f"Cost report: {args.cost_report}")
    print(f"Total calls : {tracker.total_calls}")
    print(f"Total tokens: {tracker.total_tokens}")
    alerts = tracker.reject_rate_alerts()
    if alerts:
        print(f"Reject alerts ({len(alerts)}):")
        for a in alerts[:10]:
            print(f"  {a}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
