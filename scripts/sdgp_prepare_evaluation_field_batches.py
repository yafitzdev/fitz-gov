"""Prepare subagent batches for missing canonical SDGP evaluation fields."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.evaluation_completion import build_evaluation_completion_prompt
from fitz_gov.sdgp.evaluation_fields import needs_evaluation_enrichment
from fitz_gov.sdgp.vault import Vault


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--vault", type=Path, default=Path("data/sdgp_vault_v51_enriched"))
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/sdgp_handoff_evaluation_fields/subagent_batches"),
    )
    p.add_argument("--batch-size", type=int, default=25)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--start-batch", type=int, default=None)
    p.add_argument("--dataset-version", choices=("v6", "v7", "all"), default="v7")
    return p.parse_args()


def _next_batch_number(out_dir: Path) -> int:
    nums = []
    for path in out_dir.glob("batch_*.json"):
        match = re.match(r"batch_(\d+)$", path.stem)
        if match:
            nums.append(int(match.group(1)))
    return max(nums, default=0) + 1


def _cohort(case: dict[str, Any]) -> str:
    meta = case.get("meta") if isinstance(case.get("meta"), dict) else {}
    return str(meta.get("dataset_version") or "unknown")


def _select_cases(args: argparse.Namespace, vault: Vault) -> list[dict[str, Any]]:
    selected = []
    for case in vault.iter_cases():
        if args.dataset_version != "all" and _cohort(case) != args.dataset_version:
            continue
        if needs_evaluation_enrichment(case):
            selected.append(case)
            if args.limit is not None and len(selected) >= args.limit:
                break
    return selected


def main() -> int:
    args = parse_args()
    vault = Vault.open(args.vault)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    cases = _select_cases(args, vault)
    start = args.start_batch if args.start_batch is not None else _next_batch_number(args.out_dir)

    print("=== Prepare evaluation-field completion batches ===")
    print(f"Vault          : {args.vault} ({len(vault)} rows)")
    print(f"Dataset version: {args.dataset_version}")
    print(f"Cases selected : {len(cases)}")
    print(f"Batch size     : {args.batch_size}")
    print(f"Out dir        : {args.out_dir}")

    for i in range(0, len(cases), args.batch_size):
        batch_no = start + i // args.batch_size
        chunk = cases[i : i + args.batch_size]
        path = args.out_dir / f"batch_{batch_no:03d}.json"
        payload: dict[str, Any] = {
            "batch_id": f"evaluation_fields_{batch_no:03d}",
            "expected_count": len(chunk),
            "output_path": str(
                Path("data/sdgp_handoff_evaluation_fields/subagent_outputs")
                / f"batch_{batch_no:03d}.jsonl"
            ),
            "instructions": (
                "For each slot, produce one JSONL row with shape "
                '{"case_id":"...","evaluation":{...}}. '
                "Do not edit the vault. Do not change labels, queries, contexts, "
                "taxonomy, routing, or governance scores."
            ),
            "slots": [
                {
                    "case_id": case.get("id"),
                    "prompt": build_evaluation_completion_prompt(case),
                }
                for case in chunk
            ],
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  {path}: {len(chunk)} slots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
