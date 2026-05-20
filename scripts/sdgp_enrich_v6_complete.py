"""sdgp_enrich_v6_complete.py — fill the 4 MoE-training fields missing in V6.

Adds per-chunk `boundary_quality`, per-case `evidence_bias_score`, per-case
`evidence_chain` (multi-chunk only), and per-case `grounding_targets`
(TRUSTWORTHY only). Idempotent: skips cases already complete.

Usage:
    # Local Ollama / LM Studio:
    SDGP_LOCAL_MODEL=qwen3.6-35b-a3b@q5_k_s \\
    SDGP_LOCAL_URL=http://localhost:1234 \\
    python scripts/sdgp_enrich_v6_complete.py --provider local

    # Specific id list:
    python scripts/sdgp_enrich_v6_complete.py --provider local --ids-file todo.txt

    # Subagent loop:
    python scripts/sdgp_enrich_v6_complete.py --provider handoff --handoff-dir data/sdgp_handoff_v6
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.cost import CostTracker
from fitz_gov.sdgp.llm_enrich_v6 import (
    case_needs_v6_completion,
    complete_case_with_provider,
)
from fitz_gov.sdgp.providers import (
    FileHandoffProvider,
    LmStudioProvider,
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
    p.add_argument("--provider", choices=["local", "lmstudio", "handoff", "env", "stub"], default="env")
    p.add_argument("--handoff-dir", type=Path, default=None)
    p.add_argument("--local-model", type=str, default=None)
    p.add_argument("--local-url", type=str, default=None)
    p.add_argument("--lmstudio-url", type=str, default="http://localhost:1234")
    p.add_argument("--lmstudio-model", type=str, default="qwen3.6-35b-a3b@q5_k_s")
    p.add_argument("--timeout", type=float, default=300.0)
    p.add_argument("--ids-file", type=Path, default=None,
                   help="One case_id per line — process only these")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--force", action="store_true", help="Re-process even if already complete")
    p.add_argument("--max-tokens", type=int, default=4000)
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--flush-every", type=int, default=25,
                   help="Atomic JSONL rewrite every N successful cases")
    p.add_argument("--max-failures", type=int, default=15)
    p.add_argument("--dry-run", action="store_true")
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
    if args.provider == "lmstudio":
        return LmStudioProvider(
            model_id=args.lmstudio_model,
            base_url=args.lmstudio_url,
            request_timeout_s=args.timeout,
        )
    if args.provider == "handoff":
        return FileHandoffProvider(
            handoff_dir=args.handoff_dir or Path(os.environ.get("SDGP_HANDOFF_DIR", "data/sdgp_handoff_v6")),
            timeout_s=float(os.environ.get("SDGP_HANDOFF_TIMEOUT", "900")),
        )
    if args.provider == "stub":
        return StubProvider(response='{"boundary_quality":[],"evidence_bias_score":0.5}', name="stub", version="0")
    raise SystemExit(f"unknown provider: {args.provider}")


def main() -> int:
    args = parse_args()
    print(f"=== V6 completion enrichment ===")
    print(f"Vault    : {args.vault}")
    print(f"Provider : {args.provider}")
    print(f"Force    : {args.force}")
    print(f"Limit    : {args.limit}")
    print()

    vault = Vault.open(args.vault)
    print(f"Vault size: {len(vault)} cases")

    # Filter
    if args.ids_file:
        wanted = {l.strip() for l in args.ids_file.read_text(encoding="utf-8").splitlines() if l.strip()}
        todo = [vault.get(cid) for cid in wanted if vault.get(cid)]
        todo = [c for c in todo if c is not None]
    else:
        todo = [c for c in vault.iter_cases() if args.force or case_needs_v6_completion(c)]

    print(f"Cases needing completion: {len(todo)}")
    if args.limit:
        todo = todo[: args.limit]
        print(f"--limit applied: processing {len(todo)}")

    if args.dry_run:
        print("\nSample case ids:")
        for c in todo[:20]:
            print(f"  {c['id']}")
        return 0

    if not todo:
        print("Nothing to do. Exiting.")
        return 0

    provider = build_provider(args)
    print(f"\nProvider : {provider}")
    healthy = provider.healthcheck()
    print(f"Healthy  : {healthy}")

    tracker = CostTracker()
    pending: dict[str, dict] = {}
    n_done = 0
    n_failed = 0
    consecutive_failures = 0
    t0 = time.time()

    for i, case in enumerate(todo, start=1):
        cid = case["id"]
        try:
            res = complete_case_with_provider(
                case, provider,
                max_tokens=args.max_tokens, temperature=args.temperature,
            )
            tracker.record(
                provider=provider.name,
                cell_id=case.get("taxonomy", {}).get("cell_id", "?"),
                request_text="<built>", response_text="<received>",
                outcome="accepted" if res.changed else "no_change",
            )
            if res.changed:
                pending[cid] = case
                n_done += 1
            consecutive_failures = 0
        except ProviderError as exc:
            n_failed += 1
            consecutive_failures += 1
            print(f"  [{i}/{len(todo)}] {cid}: PROVIDER FAIL {exc}", flush=True, file=sys.stderr)
            if consecutive_failures >= args.max_failures:
                print(f"ABORT: {consecutive_failures} consecutive failures", file=sys.stderr)
                break
            continue
        except ValueError as exc:
            n_failed += 1
            print(f"  [{i}/{len(todo)}] {cid}: PARSE FAIL {exc}", flush=True, file=sys.stderr)
            consecutive_failures = 0
            continue

        if i % 10 == 0 or i == len(todo):
            rate = i / max(time.time() - t0, 1e-6)
            eta = (len(todo) - i) / max(rate, 1e-6)
            print(f"  [{i}/{len(todo)}] done={n_done} fail={n_failed} "
                  f"rate={rate*60:.1f}/min ETA={eta/60:.1f}min", flush=True)
        if len(pending) >= args.flush_every:
            r = vault.update_cases(pending)
            print(f"  [flush] {r}", flush=True)
            pending.clear()

    if pending:
        r = vault.update_cases(pending)
        print(f"[final flush] {r}", flush=True)

    report_path = vault.root / "cost_reports" / f"v6_complete_{int(time.time())}.json"
    tracker.write_report(report_path)
    print(f"\nCost report: {report_path}")
    print(f"Done — succeeded={n_done} failed={n_failed} wall={time.time()-t0:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
