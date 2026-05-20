"""sdgp_merge_v6_outputs.py — merge Sonnet subagent V6-completion outputs into the vault.

Walks `data/sdgp_handoff_v6/out/*.json`, loads each, finds the corresponding
case in the vault, merges via `merge_v6_completion`, and rewrites the vault
atomically. Idempotent — re-running on the same out/ dir is a no-op.

By default, moves merged out/*.json files to out/merged/ so subsequent runs
skip already-applied outputs. Use --no-archive to skip the move.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.llm_enrich_v6 import merge_v6_completion
from fitz_gov.sdgp.vault import Vault


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--vault", type=Path, default=Path("data/sdgp_vault_v51_enriched"))
    p.add_argument("--out-dir", type=Path, default=Path("data/sdgp_handoff_v6/out"))
    p.add_argument("--no-archive", action="store_true",
                   help="Don't move processed out/*.json to out/merged/")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    vault = Vault.open(args.vault)
    print(f"Vault: {len(vault)} cases")

    # Scan both out/ and out/merged/ — some Sonnet subagents wrote directly to
    # merged/ after the first flush created that directory.
    files = sorted(args.out_dir.glob("*.json"))
    merged_dir = args.out_dir / "merged"
    if merged_dir.exists():
        # Only include merged/*.json whose case still needs v6 completion
        from fitz_gov.sdgp.llm_enrich_v6 import case_needs_v6_completion
        for f in sorted(merged_dir.glob("*.json")):
            case = vault.get(f.stem)
            if case is not None and case_needs_v6_completion(case):
                files.append(f)
    print(f"Out files: {len(files)} (incl. unmerged from merged/)")
    if not files:
        return 0

    updates: dict[str, dict] = {}
    n_changed = 0
    n_no_change = 0
    n_unknown = 0
    n_parse_fail = 0

    for f in files:
        cid = f.stem
        case = vault.get(cid)
        if case is None:
            print(f"  UNKNOWN  {cid}")
            n_unknown += 1
            continue
        try:
            payload = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"  PARSE    {cid}: {exc}")
            n_parse_fail += 1
            continue
        res = merge_v6_completion(case, payload)
        if res.changed:
            updates[cid] = case
            n_changed += 1
        else:
            n_no_change += 1
        if res.warnings:
            for w in res.warnings:
                print(f"  WARN     {cid}: {w}")

    print(f"\nMerge stats: changed={n_changed} no_change={n_no_change} "
          f"unknown={n_unknown} parse_fail={n_parse_fail}")

    if not updates:
        print("Nothing to flush.")
        return 0

    print(f"\nFlushing {len(updates)} updates to vault ...")
    res = vault.update_cases(updates)
    print(f"  {res}")

    if not args.no_archive:
        merged_dir = args.out_dir / "merged"
        merged_dir.mkdir(exist_ok=True)
        for f in files:
            if f.stem in updates or (vault.get(f.stem) is not None):
                shutil.move(str(f), str(merged_dir / f.name))
        print(f"  Archived to {merged_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
