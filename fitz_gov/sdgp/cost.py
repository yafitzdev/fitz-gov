"""SDGP cost tracking — token estimates + per-batch / per-cell rollup.

A `CostTracker` is a tiny accumulator the orchestrator can pass to providers
to record approximate input + output token counts (using a 4 chars/token
heuristic when no tokenizer is at hand). It exposes:

  - `record(provider, cell_id, request, response)` — call once per
    provider invocation
  - `summary()` — totals + per-provider + per-cell breakdown
  - `rollup_to_vault(vault)` — persist a JSON summary under
    `<vault>/cost_reports/<batch_id>.json`

This is intentionally approximate. The point is signal not precision —
cells with a high reject rate (lots of input tokens, no accepted cases)
show up loudly; runaway provider costs are visible per batch.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHARS_PER_TOKEN = 4  # rough English approximation


def estimate_tokens(text: str | None) -> int:
    if not text:
        return 0
    return max(1, len(text) // CHARS_PER_TOKEN)


@dataclass(slots=True)
class CallRecord:
    """One provider invocation."""

    provider: str
    cell_id: str
    input_tokens: int
    output_tokens: int
    timestamp: str
    outcome: str | None = None  # "accepted" / "rejected_*" / "conflict" — filled in by orchestrator


@dataclass(slots=True)
class CostTracker:
    """Append-only call log + on-demand rollups. Pass to multiple orchestrator
    runs to keep a running tab; reset by constructing a new instance."""

    calls: list[CallRecord] = field(default_factory=list)

    def record(
        self,
        *,
        provider: str,
        cell_id: str,
        request_text: str,
        response_text: str | None,
        outcome: str | None = None,
    ) -> CallRecord:
        rec = CallRecord(
            provider=provider,
            cell_id=cell_id,
            input_tokens=estimate_tokens(request_text),
            output_tokens=estimate_tokens(response_text),
            timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            outcome=outcome,
        )
        self.calls.append(rec)
        return rec

    # ---- Rollups -------------------------------------------------------

    @property
    def total_calls(self) -> int:
        return len(self.calls)

    @property
    def total_input_tokens(self) -> int:
        return sum(c.input_tokens for c in self.calls)

    @property
    def total_output_tokens(self) -> int:
        return sum(c.output_tokens for c in self.calls)

    @property
    def total_tokens(self) -> int:
        return self.total_input_tokens + self.total_output_tokens

    def per_provider(self) -> dict[str, dict[str, int]]:
        out: dict[str, dict[str, int]] = defaultdict(lambda: {"calls": 0, "in": 0, "out": 0})
        for c in self.calls:
            d = out[c.provider]
            d["calls"] += 1
            d["in"] += c.input_tokens
            d["out"] += c.output_tokens
        return dict(out)

    def per_cell(self, top_n: int | None = None) -> list[dict[str, Any]]:
        bucket: dict[str, dict[str, int]] = defaultdict(
            lambda: {"calls": 0, "in": 0, "out": 0, "accepted": 0, "rejected": 0}
        )
        for c in self.calls:
            d = bucket[c.cell_id]
            d["calls"] += 1
            d["in"] += c.input_tokens
            d["out"] += c.output_tokens
            if c.outcome == "accepted":
                d["accepted"] += 1
            elif c.outcome and c.outcome.startswith("rejected"):
                d["rejected"] += 1
        rows = [{"cell_id": cid, **stats} for cid, stats in bucket.items()]
        rows.sort(key=lambda r: -r["calls"])
        if top_n:
            rows = rows[:top_n]
        return rows

    def reject_rate_alerts(self, *, min_calls: int = 3, threshold: float = 0.7) -> list[str]:
        """Surface cells where ≥`threshold` of attempts were rejected. These
        cells likely have a prompt-fit problem, not a generator problem."""
        alerts = []
        for row in self.per_cell():
            if row["calls"] < min_calls:
                continue
            rate = row["rejected"] / max(row["calls"], 1)
            if rate >= threshold:
                alerts.append(
                    f"{row['cell_id']}: {row['rejected']}/{row['calls']} rejected ({rate:.0%})"
                )
        return alerts

    def summary(self) -> dict[str, Any]:
        return {
            "total_calls": self.total_calls,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_tokens,
            "per_provider": self.per_provider(),
            "per_cell_top10": self.per_cell(top_n=10),
            "reject_rate_alerts": self.reject_rate_alerts(),
        }

    # ---- Persistence ---------------------------------------------------

    def write_report(self, out_path: Path) -> Path:
        """Write the full summary + raw call log to a JSON file."""
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "summary": self.summary(),
            "calls": [
                {
                    "provider": c.provider,
                    "cell_id": c.cell_id,
                    "input_tokens": c.input_tokens,
                    "output_tokens": c.output_tokens,
                    "timestamp": c.timestamp,
                    "outcome": c.outcome,
                }
                for c in self.calls
            ],
        }
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return out_path
