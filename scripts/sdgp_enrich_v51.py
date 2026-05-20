"""sdgp_enrich_v51.py — Apply Phase 0 enrichment to all V5.1 cases.

Reads `data/{tier0_sanity,tier1_core}/*.json`, applies the deterministic
mapping in `fitz_gov.sdgp.enrich`, runs each enriched row through the
SDGP checker, and writes the survivors to a vault at
`data/sdgp_vault_v51_enriched/`.

Usage (from fitz-gov repo root):
    python scripts/sdgp_enrich_v51.py
    python scripts/sdgp_enrich_v51.py --dry-run                 # don't write
    python scripts/sdgp_enrich_v51.py --output-dir <path>
    python scripts/sdgp_enrich_v51.py --fail-on-errors          # exit non-zero if any case fails the checker

Idempotent — re-running on a populated vault no-ops on cases already present.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import sys
from pathlib import Path

# Make the repo's `fitz_gov` importable when running this script directly.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.checker import Checker, hashes_from
from fitz_gov.sdgp.enrich import V6_VERSION, count_subcategory_fallbacks, enrich_case
from fitz_gov.sdgp.vault import Provenance, Vault, new_batch_id


DEFAULT_VAULT = Path("data/sdgp_vault_v51_enriched")
DEFAULT_INPUT_DIRS = (Path("data/tier1_core"), Path("data/tier0_sanity"))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument(
        "--input-dirs",
        type=Path,
        nargs="+",
        default=list(DEFAULT_INPUT_DIRS),
        help="V5.1 input dirs containing *.json with `cases` arrays",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_VAULT,
        help=f"Vault destination (default: {DEFAULT_VAULT})",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Do all the work but don't write to the vault",
    )
    p.add_argument(
        "--fail-on-errors",
        action="store_true",
        help="Exit non-zero if any case fails the checker",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Process at most N cases (for quick smoke tests)",
    )
    return p.parse_args()


def load_v51_cases(input_dirs: list[Path]) -> list[dict]:
    cases: list[dict] = []
    for d in input_dirs:
        if not d.exists():
            print(f"  WARN: input dir not found: {d}", file=sys.stderr)
            continue
        for fp in sorted(d.glob("*.json")):
            with fp.open("r", encoding="utf-8") as fh:
                payload = json.load(fh)
            file_cases = payload.get("cases", [])
            print(f"  loaded {len(file_cases):>4} from {fp}")
            cases.extend(file_cases)
    return cases


def main() -> int:
    args = parse_args()
    print(f"=== SDGP Phase 0 enrichment ===")
    print(f"Input dirs : {[str(d) for d in args.input_dirs]}")
    print(f"Output     : {args.output_dir}")
    print(f"Dry run    : {args.dry_run}")
    print()

    print("Loading V5.1 cases...")
    v51_cases = load_v51_cases(list(args.input_dirs))
    print(f"  total loaded: {len(v51_cases)}")

    if args.limit:
        v51_cases = v51_cases[: args.limit]
        print(f"  --limit applied: processing {len(v51_cases)} cases")

    # Subcategory mapping audit (before enrichment, so we report on input)
    fb = count_subcategory_fallbacks(
        [c.get("subcategory", "") for c in v51_cases],
        [c["category"] for c in v51_cases],
    )
    print(f"\nSubcategory mapping coverage:")
    for k, n in fb.items():
        print(f"  {k:>20s}: {n:>4} ({n / max(len(v51_cases), 1):.1%})")

    print("\nEnriching...")
    enriched: list[dict] = []
    enrich_errors = 0
    for v51 in v51_cases:
        try:
            enriched.append(enrich_case(v51))
        except Exception as exc:
            enrich_errors += 1
            print(f"  ERROR enriching {v51.get('id', '<no id>')}: {exc}", file=sys.stderr)
    print(f"  enriched {len(enriched)} / {len(v51_cases)} cases ({enrich_errors} hard errors)")

    print("\nValidating with SDGP checker...")
    # Migrated V5.1 cases were labeled under a different taxonomy. Their inferred
    # pattern may not match structurally even though the case is human-validated.
    # Downgrade pattern_structure errors to warnings so we still vault them.
    checker = Checker(pattern_structure_warning_only=True)
    seen = set()  # dedup signal — but we're enriching V5.1 which is already validated, so this should be empty for clean V5.1
    n_pass = 0
    n_warn = 0
    n_err = 0
    error_rules: collections.Counter = collections.Counter()
    warning_rules: collections.Counter = collections.Counter()
    survivors: list[dict] = []
    for case in enriched:
        result = checker.check(case, seen_hashes=seen)
        if result.passed:
            n_pass += 1
            if result.warnings:
                n_warn += 1
                for w in result.warnings:
                    warning_rules[w.rule] += 1
            survivors.append(case)
        else:
            n_err += 1
            for e in result.errors:
                error_rules[e.rule] += 1
            # Don't add to seen; the failing case shouldn't dedup-block successors

    print(f"  passed : {n_pass:>4}  (with warnings: {n_warn})")
    print(f"  failed : {n_err:>4}")
    if error_rules:
        print(f"  top error rules:")
        for rule, n in error_rules.most_common(10):
            print(f"    {rule:>40s}: {n}")
    if warning_rules:
        print(f"  top warning rules:")
        for rule, n in warning_rules.most_common(10):
            print(f"    {rule:>40s}: {n}")

    # Cell coverage on the survivors
    cell_counts: collections.Counter = collections.Counter()
    for case in survivors:
        cell_counts[case["taxonomy"]["cell_id"]] += 1
    n_cells = len(cell_counts)
    n_empty_cells_in_378 = 378 - n_cells if n_cells <= 378 else 0
    avg_per_cell = (n_pass / n_cells) if n_cells else 0
    print(f"\nCell coverage (V5.1 only, of 378 primary-domain cells):")
    print(f"  cells with at least 1 case: {n_cells} / 378")
    print(f"  cells empty                : {n_empty_cells_in_378}")
    print(f"  avg cases / non-empty cell : {avg_per_cell:.1f}")
    print(f"  top 5 filled cells:")
    for cid, n in cell_counts.most_common(5):
        print(f"    {cid}: {n}")

    if args.dry_run:
        print("\n--dry-run set, not writing to vault.")
        if args.fail_on_errors and n_err > 0:
            return 1
        return 0

    print(f"\nWriting to vault at {args.output_dir}...")
    vault = Vault.open(args.output_dir)
    prov = Provenance(
        provider="migrated_v51",
        provider_version="enrich.py-phase-0a",
        prompt_version="deterministic-v1",
        batch_id=new_batch_id(),
    )
    result = vault.add_many(survivors, provenance=prov)
    print(f"  added      : {result['added']}")
    print(f"  duplicate  : {result['duplicate']}  (already in vault from a prior run)")
    print(f"  vault size : {len(vault)}")

    if args.fail_on_errors and n_err > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
