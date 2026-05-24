"""sdgp_complete_v7_schema.py — complete thin V7 rows to full training schema.

The original V7 generation pass produced valid cell-targeted cases, but many
rows lack the full V6/MoE training signal suite. This runner sends those rows
through one completion prompt per case and writes the enriched rows back to the
vault atomically in batches.

Examples:
    # Audit only
    python scripts/sdgp_complete_v7_schema.py --dry-run

    # LM Studio
    python scripts/sdgp_complete_v7_schema.py --provider lmstudio

    # File handoff for subagents
    python scripts/sdgp_complete_v7_schema.py --provider handoff --handoff-dir data/sdgp_handoff_v7_complete
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.completeness import audit_case_completeness
from fitz_gov.sdgp.cost import CostTracker
from fitz_gov.sdgp.providers import (
    FileHandoffProvider,
    LmStudioProvider,
    LocalLlmProvider,
    Provider,
    ProviderError,
    StubProvider,
    providers_from_env,
)
from fitz_gov.sdgp.v7_completion import complete_case_with_provider
from fitz_gov.sdgp.vault import Vault


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--vault", type=Path, default=Path("data/sdgp_vault_v51_enriched"))
    p.add_argument(
        "--provider", choices=["local", "lmstudio", "handoff", "env", "stub"], default="env"
    )
    p.add_argument("--handoff-dir", type=Path, default=Path("data/sdgp_handoff_v7_complete"))
    p.add_argument("--local-model", type=str, default=None)
    p.add_argument("--local-url", type=str, default=None)
    p.add_argument("--lmstudio-url", type=str, default="http://localhost:1234")
    p.add_argument("--lmstudio-model", type=str, default="qwen3.6-35b-a3b@q5_k_s")
    p.add_argument("--timeout", type=float, default=300.0)
    p.add_argument("--ids-file", type=Path, default=None)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--force", action="store_true", help="Refresh complete rows too")
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing rich fields")
    p.add_argument("--max-tokens", type=int, default=5000)
    p.add_argument("--temperature", type=float, default=0.2)
    p.add_argument("--flush-every", type=int, default=25)
    p.add_argument("--max-failures", type=int, default=15)
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def build_provider(args: argparse.Namespace) -> Provider:
    if args.provider == "env":
        ps = providers_from_env()
        if not ps:
            raise SystemExit("--provider env: no provider env vars set")
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
        return FileHandoffProvider(handoff_dir=args.handoff_dir, timeout_s=args.timeout)
    if args.provider == "stub":
        return StubProvider(
            response='{"input":{"query_rewritten":"stub","contexts":[]},'
            '"governance":{},"routing":{},"meta":{}}',
            name="stub",
            version="0",
        )
    raise SystemExit(f"unknown provider: {args.provider}")


def _v7_cases(vault: Vault, *, ids_file: Path | None, force: bool) -> list[dict]:
    if ids_file:
        wanted = [line.strip() for line in ids_file.read_text(encoding="utf-8").splitlines()]
        return [case for cid in wanted if cid and (case := vault.get(cid)) is not None]

    out = []
    for case in vault.iter_cases():
        meta = case.get("meta") if isinstance(case.get("meta"), dict) else {}
        if meta.get("dataset_version") != "v7":
            continue
        if force or audit_case_completeness(case):
            out.append(case)
    return out


def main() -> int:
    args = parse_args()
    print("=== V7 training-schema completion ===")
    print(f"Vault    : {args.vault}")
    print(f"Provider : {args.provider}")
    print(f"Force    : {args.force}")
    print(f"Overwrite: {args.overwrite}")
    print(f"Limit    : {args.limit}")
    print()

    vault = Vault.open(args.vault)
    todo = _v7_cases(vault, ids_file=args.ids_file, force=args.force)
    print(f"Vault size: {len(vault)} cases")
    print(f"V7 cases needing completion: {len(todo)}")

    if args.limit is not None:
        todo = todo[: args.limit]
        print(f"--limit applied: processing {len(todo)}")

    if args.dry_run:
        print("\nSample case ids:")
        for case in todo[:20]:
            issues = audit_case_completeness(case)
            print(f"  {case['id']} ({len(issues)} missing fields)")
        return 0

    if not todo:
        print("Nothing to do. Exiting.")
        return 0

    provider = build_provider(args)
    print(f"\nProvider : {provider}")
    print(f"Healthy  : {provider.healthcheck()}")

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
                case,
                provider,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
                overwrite=args.overwrite,
            )
            tracker.record(
                provider=provider.name,
                cell_id=case.get("taxonomy", {}).get("cell_id", "?"),
                request_text="<built per-case>",
                response_text="<received>",
                outcome="accepted" if res.changed else "no_change",
            )
            remaining = audit_case_completeness(case)
            if remaining:
                n_failed += 1
                print(
                    f"  [{i}/{len(todo)}] {cid}: INCOMPLETE after merge "
                    f"({len(remaining)} fields)",
                    flush=True,
                    file=sys.stderr,
                )
                consecutive_failures = 0
                continue
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
            consecutive_failures = 0
            print(f"  [{i}/{len(todo)}] {cid}: PARSE FAIL {exc}", flush=True, file=sys.stderr)
            continue

        if i % 10 == 0 or i == len(todo):
            rate = i / max(time.time() - t0, 1e-6)
            eta = (len(todo) - i) / max(rate, 1e-6)
            print(
                f"  [{i}/{len(todo)}] done={n_done} fail={n_failed} "
                f"rate={rate*60:.1f}/min ETA={eta/60:.1f}min",
                flush=True,
            )
        if len(pending) >= args.flush_every:
            print(f"  [flush] {vault.update_cases(pending)}", flush=True)
            pending.clear()

    if pending:
        print(f"[final flush] {vault.update_cases(pending)}", flush=True)

    report_path = vault.root / "cost_reports" / f"v7_complete_{int(time.time())}.json"
    tracker.write_report(report_path)
    print(f"\nCost report: {report_path}")
    print(f"Done — succeeded={n_done} failed={n_failed} wall={time.time()-t0:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
