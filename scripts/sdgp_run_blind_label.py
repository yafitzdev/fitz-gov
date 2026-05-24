"""Run blind labeling for a V7 QA queue using a local/provider backend."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.blind_label import case_ids_from_rows, label_queue_row, sample_queue_rows
from fitz_gov.sdgp.providers import (
    FileHandoffProvider,
    LmStudioProvider,
    LocalLlmProvider,
    Provider,
    StubProvider,
    providers_from_env,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--queue", type=Path, default=Path("data/sdgp_v7_qa/blind_label_queue.jsonl"))
    p.add_argument(
        "--out",
        type=Path,
        default=Path("data/sdgp_v7_qa/blind_label_predictions.jsonl"),
    )
    p.add_argument(
        "--provider",
        choices=("lmstudio", "ollama", "file", "stub", "env"),
        default="lmstudio",
    )
    p.add_argument("--model", type=str, default=None)
    p.add_argument("--base-url", type=str, default=None)
    p.add_argument("--api-key", type=str, default=os.environ.get("LMSTUDIO_API_KEY", "lm-studio"))
    p.add_argument("--handoff-dir", type=Path, default=Path("data/sdgp_blind_label_handoff"))
    p.add_argument("--handoff-timeout-s", type=float, default=600.0)
    p.add_argument("--request-timeout-s", type=float, default=180.0)
    p.add_argument(
        "--stub-label", choices=("ABSTAIN", "DISPUTED", "TRUSTWORTHY"), default="ABSTAIN"
    )
    p.add_argument("--max-rows", type=int, default=None)
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--sample-size", type=int, default=None)
    p.add_argument("--sample-seed", type=int, default=20260522)
    p.add_argument(
        "--exclude-ledger",
        type=Path,
        default=Path("data/sdgp_v7_qa/blind_label_second_pass_ledger.jsonl"),
        help="Rows already present here are excluded before random sampling.",
    )
    p.add_argument("--no-exclude-ledger", action="store_true")
    p.add_argument("--sample-out", type=Path, default=None)
    p.add_argument("--run-id", type=str, default=None)
    p.add_argument("--max-tokens", type=int, default=128)
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--healthcheck-only", action="store_true")
    p.add_argument("--no-healthcheck", action="store_true")
    p.add_argument("--resume", action=argparse.BooleanOptionalAction, default=True)
    return p.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line_no, raw in enumerate(fh, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}: line {line_no} is not valid JSON: {exc}") from exc
            if not isinstance(payload, dict):
                raise ValueError(f"{path}: line {line_no} is not a JSON object")
            rows.append(payload)
    return rows


def append_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            fh.flush()


def existing_case_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {str(row.get("case_id") or "") for row in read_jsonl(path) if row.get("case_id")}


def make_provider(args: argparse.Namespace) -> Provider:
    if args.provider == "lmstudio":
        return LmStudioProvider(
            model_id=args.model or os.environ.get("SDGP_LMSTUDIO_MODEL", "qwen/qwen3.6-35b-a3b"),
            base_url=args.base_url or os.environ.get("SDGP_LMSTUDIO_URL", "http://localhost:1234"),
            api_key=args.api_key,
            request_timeout_s=args.request_timeout_s,
        )
    if args.provider == "ollama":
        return LocalLlmProvider(
            model_id=args.model or os.environ.get("SDGP_LOCAL_MODEL", "qwen3.5:0.8b"),
            base_url=args.base_url or os.environ.get("SDGP_LOCAL_URL", "http://localhost:11434"),
            request_timeout_s=args.request_timeout_s,
        )
    if args.provider == "file":
        return FileHandoffProvider(
            handoff_dir=args.handoff_dir,
            timeout_s=args.handoff_timeout_s,
        )
    if args.provider == "stub":
        return StubProvider(
            response=(
                '{"label":"' + args.stub_label + '","rationale":"stub response for smoke testing"}'
            )
        )
    providers = providers_from_env()
    if not providers:
        raise ValueError("provider=env requires SDGP_LMSTUDIO_*, SDGP_LOCAL_*, or SDGP_HANDOFF_DIR")
    return providers[0]


def main() -> int:
    args = parse_args()
    provider = make_provider(args)

    if not args.no_healthcheck:
        ok = provider.healthcheck()
        if args.healthcheck_only:
            print(f"Provider {provider.name} ({provider.version}) healthcheck={ok}")
            return 0 if ok else 2
        if not ok:
            print(
                f"Provider {provider.name} ({provider.version}) failed healthcheck. "
                "Use --no-healthcheck only if this is expected.",
                file=sys.stderr,
            )
            return 2

    if args.healthcheck_only:
        print(f"Provider {provider.name} ({provider.version}) healthcheck skipped")
        return 0

    queue = read_jsonl(args.queue)
    if args.offset:
        queue = queue[args.offset :]
    if args.max_rows is not None:
        queue = queue[: args.max_rows]
    excluded_case_ids: set[str] = set()
    if not args.no_exclude_ledger and args.exclude_ledger.exists():
        excluded_case_ids = case_ids_from_rows(read_jsonl(args.exclude_ledger))
    if args.sample_size is not None:
        queue = sample_queue_rows(
            queue,
            sample_size=args.sample_size,
            seed=args.sample_seed,
            excluded_case_ids=excluded_case_ids,
        )
        if args.sample_out is not None:
            args.sample_out.parent.mkdir(parents=True, exist_ok=True)
            args.sample_out.write_text(
                "".join(
                    json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in queue
                ),
                encoding="utf-8",
            )

    if args.out.exists() and not args.resume:
        args.out.unlink()

    done = existing_case_ids(args.out) if args.resume else set()
    pending = [row for row in queue if str(row.get("case_id") or "") not in done]

    written = 0
    for row in pending:
        result = label_queue_row(
            row,
            provider,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
        )
        if args.run_id:
            result["run_id"] = args.run_id
        if args.sample_size is not None:
            result["sample_seed"] = args.sample_seed
        append_jsonl(args.out, [result])
        written += 1
        if written % 25 == 0:
            print(f"written={written} last_case={result['case_id']}")

    print("=== Blind label run ===")
    print(f"Queue     : {args.queue}")
    print(f"Output    : {args.out}")
    print(f"Provider  : {provider.name} ({provider.version})")
    print(f"Rows read : {len(queue)}")
    if args.sample_size is not None:
        print(f"Sample    : {args.sample_size} requested, seed={args.sample_seed}")
        print(f"Excluded  : {len(excluded_case_ids)} ledger case IDs")
        if args.sample_out is not None:
            print(f"Sample out: {args.sample_out}")
    print(f"Skipped   : {len(queue) - len(pending)}")
    print(f"Written   : {written}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
