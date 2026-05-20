"""sdgp_lm_studio_worker.py — enrich a specific list of cases via LM Studio.

Reads case_ids (one per line) from --ids-file, looks them up in the vault,
runs each through LmStudioProvider, batches updates and rewrites the vault
in one atomic JSONL replace at the end. Designed to run in background
parallel to a Sonnet-subagent enrichment wave.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.cost import CostTracker
from fitz_gov.sdgp.llm_enrich import enrich_case_with_provider
from fitz_gov.sdgp.providers import LmStudioProvider, ProviderError
from fitz_gov.sdgp.vault import Vault


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--vault", type=Path, default=Path("data/sdgp_vault_v51_enriched"))
    p.add_argument("--ids-file", type=Path, required=True)
    p.add_argument("--model", type=str, default="qwen3.6-35b-a3b@q5_k_s")
    p.add_argument("--url", type=str, default="http://localhost:1234")
    p.add_argument("--timeout", type=float, default=300.0)
    p.add_argument("--max-tokens", type=int, default=2048)
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--flush-every", type=int, default=20,
                   help="Atomic JSONL rewrite every N successful cases (default: 20)")
    p.add_argument("--max-failures", type=int, default=15)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    case_ids = [line.strip() for line in args.ids_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"[lm-studio-worker] {len(case_ids)} cases assigned, model={args.model}", flush=True)

    vault = Vault.open(args.vault)
    provider = LmStudioProvider(
        model_id=args.model, base_url=args.url, request_timeout_s=args.timeout
    )
    print(f"[lm-studio-worker] healthcheck: {provider.healthcheck()}", flush=True)

    tracker = CostTracker()
    pending_updates: dict[str, dict] = {}
    consecutive_failures = 0
    n_done = 0
    n_failed = 0
    t0 = time.time()

    for i, cid in enumerate(case_ids, start=1):
        case = vault.get(cid)
        if case is None:
            print(f"  [{i}/{len(case_ids)}] {cid}: NOT IN VAULT — skip", flush=True)
            continue
        try:
            res = enrich_case_with_provider(
                case, provider,
                max_tokens=args.max_tokens, temperature=args.temperature,
            )
            tracker.record(
                provider=provider.name, cell_id=case.get("taxonomy", {}).get("cell_id", "?"),
                request_text="<built>", response_text="<received>",
                outcome="accepted" if res.changed else "no_change",
            )
            if res.changed:
                pending_updates[cid] = case
                n_done += 1
            consecutive_failures = 0
        except ProviderError as exc:
            n_failed += 1
            consecutive_failures += 1
            print(f"  [{i}/{len(case_ids)}] {cid}: PROVIDER FAIL {exc}", flush=True)
            if consecutive_failures >= args.max_failures:
                print(f"[lm-studio-worker] ABORT: {consecutive_failures} consecutive failures", flush=True)
                break
            continue
        except ValueError as exc:
            n_failed += 1
            print(f"  [{i}/{len(case_ids)}] {cid}: PARSE FAIL {exc}", flush=True)
            consecutive_failures = 0
            continue
        # Progress + periodic flush
        if i % 5 == 0 or i == len(case_ids):
            rate = i / max(time.time() - t0, 1e-6)
            eta_s = (len(case_ids) - i) / max(rate, 1e-6)
            print(f"  [{i}/{len(case_ids)}] done={n_done} fail={n_failed} rate={rate*60:.1f}/min ETA={eta_s/60:.1f}min", flush=True)
        if len(pending_updates) >= args.flush_every:
            res = vault.update_cases(pending_updates)
            print(f"  [flush] vault.update_cases: {res}", flush=True)
            pending_updates.clear()

    # Final flush
    if pending_updates:
        res = vault.update_cases(pending_updates)
        print(f"[lm-studio-worker] final flush: {res}", flush=True)

    # Cost report
    report_path = vault.root / "cost_reports" / f"lm_studio_{int(time.time())}.json"
    tracker.write_report(report_path)
    print(f"[lm-studio-worker] cost report: {report_path}", flush=True)
    print(f"[lm-studio-worker] done — {n_done} succeeded, {n_failed} failed, "
          f"wall={time.time()-t0:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
