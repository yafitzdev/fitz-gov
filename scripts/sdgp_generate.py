"""sdgp_generate.py — End-to-end SDGP generation runner.

Reads cell coverage from the vault, ranks gaps, drives the orchestrator
to fill them via the configured provider, optionally blind-labels with a
second provider, and writes a markdown coverage report.

Provider selection:
  - `--provider local`     LocalLlmProvider (Ollama at $SDGP_LOCAL_URL).
  - `--provider handoff`   FileHandoffProvider (subagent loop via files).
  - `--provider stub`      StubProvider returning a fixed JSON (dev-only).
  - `--provider env`       Read from $SDGP_LOCAL_MODEL / $SDGP_HANDOFF_DIR.

If a second provider is available (e.g. local + handoff), it's used as
the blind-label validator. This enforces ROADMAP §4: generator and
validator must never be the same model.

Usage (from fitz-gov repo root):
    python scripts/sdgp_generate.py --vault data/sdgp_vault_v51_enriched \\
        --provider local --n-per-cell 1 --max-cells 5 --target 20 \\
        --report-path data/sdgp_reports/latest.md
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.checker import Checker
from fitz_gov.sdgp.gap_detector import (
    CellFilter,
    GapDetector,
    PriorityWeights,
)
from fitz_gov.sdgp.monitor import write_coverage_report
from fitz_gov.sdgp.orchestrator import Orchestrator, Outcome
from fitz_gov.sdgp.providers import (
    BlindLabelPair,
    FileHandoffProvider,
    LocalLlmProvider,
    Provider,
    StubProvider,
    providers_from_env,
)
from fitz_gov.sdgp.taxonomy import (
    Difficulty,
    Domain,
    GovernanceClass,
    TaxonomyPattern,
)
from fitz_gov.sdgp.vault import Vault


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--vault", type=Path, default=Path("data/sdgp_vault_v51_enriched"))
    p.add_argument("--target", type=int, default=20, help="Min cases per cell (ROADMAP §3: 20–25)")
    p.add_argument("--n-per-cell", type=int, default=1)
    p.add_argument("--max-cells", type=int, default=10, help="Cap how many cells to attempt in this run")
    p.add_argument(
        "--provider",
        choices=["local", "handoff", "stub", "env"],
        default="env",
    )
    p.add_argument("--no-blind-label", action="store_true", help="Skip the second-pass validator")
    p.add_argument("--report-path", type=Path, default=None, help="Markdown coverage report destination")
    p.add_argument("--max-attempts-per-cell", type=int, default=3)
    p.add_argument("--n-few-shots", type=int, default=2)
    p.add_argument("--temperature", type=float, default=0.7)
    # Filters
    p.add_argument("--filter-pattern", type=str, default=None,
                   help="Restrict to one TaxonomyPattern (slug, e.g. 'numerical_conflict')")
    p.add_argument("--filter-class", type=str, default=None,
                   help="Restrict to one GovernanceClass (ABSTAIN | DISPUTED | TRUSTWORTHY)")
    p.add_argument("--filter-difficulty", type=str, default=None,
                   help="Restrict to one Difficulty (easy | medium | hard)")
    p.add_argument("--filter-domain", type=str, default=None,
                   help="Restrict to one expert Domain (e.g. 'science_medicine')")
    p.add_argument("--dry-run", action="store_true",
                   help="Show what would happen but don't call providers or write to vault")
    return p.parse_args()


def build_providers(args: argparse.Namespace) -> list[Provider]:
    if args.provider == "env":
        return providers_from_env()
    if args.provider == "local":
        return [LocalLlmProvider(
            model_id=os.environ.get("SDGP_LOCAL_MODEL", "qwen3.5:0.8b"),
            base_url=os.environ.get("SDGP_LOCAL_URL", "http://localhost:11434"),
        )]
    if args.provider == "handoff":
        return [FileHandoffProvider(
            handoff_dir=Path(os.environ.get("SDGP_HANDOFF_DIR", "data/sdgp_handoff")),
            timeout_s=float(os.environ.get("SDGP_HANDOFF_TIMEOUT", "600")),
        )]
    if args.provider == "stub":
        return [StubProvider(response='{"id":"stub_001","input":{"query":"q","contexts":[]},"governance":{"classification":"ABSTAIN"}}')]
    raise SystemExit(f"unknown provider: {args.provider}")


def build_filter(args: argparse.Namespace) -> CellFilter:
    flt = CellFilter()
    if args.filter_pattern:
        flt.patterns = {TaxonomyPattern(args.filter_pattern)}
    if args.filter_class:
        flt.classes = {GovernanceClass(args.filter_class.upper())}
    if args.filter_difficulty:
        flt.difficulties = {Difficulty(args.filter_difficulty)}
    if args.filter_domain:
        flt.domains = {Domain(args.filter_domain)}
    return flt


def main() -> int:
    args = parse_args()
    print(f"=== SDGP generation ===")
    print(f"Vault       : {args.vault}")
    print(f"Target/cell : {args.target}")
    print(f"N/cell      : {args.n_per_cell}")
    print(f"Max cells   : {args.max_cells}")
    print(f"Provider    : {args.provider}")
    print(f"Blind label : {not args.no_blind_label}")
    print(f"Dry run     : {args.dry_run}")
    print()

    vault = Vault.open(args.vault)
    print(f"Vault size  : {len(vault)} cases, {len(vault.cell_counts())} cells covered")

    # Detect gaps
    detector = GapDetector()
    flt = build_filter(args)
    gaps = detector.rank(vault.cell_counts(), target=args.target, filter=flt)
    print(f"\nGaps after filter: {len(gaps)} cells need work")
    if not gaps:
        print("No gaps to fill — vault is at target for the filtered space.")
        return 0
    print(f"Top 5 gaps:")
    for g in gaps[:5]:
        print(f"  {g.cell.cell_id}: current={g.current} target={g.target} gap={g.gap}")

    # Cap
    gaps = gaps[: args.max_cells]
    print(f"\nAttempting {len(gaps)} cells × {args.n_per_cell} cases = "
          f"{len(gaps) * args.n_per_cell} cases max")

    if args.dry_run:
        print("\n--dry-run set, exiting before provider calls.")
        return 0

    # Build providers
    providers = build_providers(args)
    if not providers:
        print(
            "ERROR: no providers available. Set SDGP_LOCAL_MODEL / SDGP_HANDOFF_DIR "
            "or pass --provider explicitly.",
            file=sys.stderr,
        )
        return 1
    print(f"\nProviders ({len(providers)}):")
    for p in providers:
        healthy = "OK" if p.healthcheck() else "UNREACHABLE"
        print(f"  {p}  [{healthy}]")

    generator = providers[0]
    blind_pair = None
    if not args.no_blind_label and len(providers) >= 2:
        blind_pair = BlindLabelPair(pool=providers)
        print(f"  blind-label validator: {blind_pair.validator_for(generator)}")
    elif not args.no_blind_label:
        print(f"  WARN: only 1 provider available, blind labeling disabled")

    orch = Orchestrator(
        vault=vault,
        provider=generator,
        blind_label_pair=blind_pair,
        checker=Checker(),
        max_attempts_per_cell=args.max_attempts_per_cell,
        n_few_shots=args.n_few_shots,
        generator_temperature=args.temperature,
    )

    # Run
    def progress(r):
        symbol = {
            Outcome.ACCEPTED: ".",
            Outcome.REJECTED_PARSE: "P",
            Outcome.REJECTED_CHECKER: "C",
            Outcome.REJECTED_PROVIDER: "X",
            Outcome.CONFLICT: "!",
        }.get(r.outcome, "?")
        print(symbol, end="", flush=True)

    print("\nGenerating (.= accepted, P=parse-fail, C=check-fail, X=provider-fail, != conflict):")
    report = orch.fill_gaps(gaps, n_per_cell=args.n_per_cell, on_result=progress)
    print()
    print()
    print(report.summary())

    print(f"\nVault now : {len(vault)} cases, {len(vault.cell_counts())} cells covered")

    # Coverage report
    if args.report_path is None:
        args.report_path = vault.root / "coverage_report.md"
    args.report_path = Path(args.report_path)
    write_coverage_report(
        vault.cell_counts(),
        args.report_path,
        target=args.target,
        vault_path=vault.root,
    )
    print(f"Coverage report -> {args.report_path}")

    # Conflicts
    conflicts = orch.list_conflicts()
    if conflicts:
        print(f"\nConflict queue: {len(conflicts)} unresolved cases under {vault.root / 'conflicts'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
