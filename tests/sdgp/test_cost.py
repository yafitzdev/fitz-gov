"""Tests for fitz_gov.sdgp.cost."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fitz_gov.sdgp.cost import CostTracker, estimate_tokens


# ---------------------------------------------------------------------------
# estimate_tokens
# ---------------------------------------------------------------------------


def test_estimate_tokens_empty() -> None:
    assert estimate_tokens("") == 0
    assert estimate_tokens(None) == 0


def test_estimate_tokens_short_returns_one_min() -> None:
    assert estimate_tokens("a") == 1
    assert estimate_tokens("hi") == 1


def test_estimate_tokens_scales_with_length() -> None:
    short = estimate_tokens("a" * 4)  # ~1 token
    long = estimate_tokens("a" * 400)  # ~100 tokens
    assert long > short
    assert short == 1


# ---------------------------------------------------------------------------
# record + summary
# ---------------------------------------------------------------------------


def test_record_accumulates() -> None:
    t = CostTracker()
    t.record(provider="local_llm", cell_id="a", request_text="x" * 100, response_text="y" * 40, outcome="accepted")
    t.record(provider="local_llm", cell_id="b", request_text="x" * 200, response_text="y" * 80, outcome="accepted")
    assert t.total_calls == 2
    assert t.total_input_tokens > 0
    assert t.total_output_tokens > 0
    assert t.total_tokens == t.total_input_tokens + t.total_output_tokens


def test_per_provider_breakdown() -> None:
    t = CostTracker()
    t.record(provider="local_llm", cell_id="a", request_text="x" * 100, response_text="y" * 40)
    t.record(provider="local_llm", cell_id="a", request_text="x" * 100, response_text="y" * 40)
    t.record(provider="handoff", cell_id="b", request_text="x" * 200, response_text="y" * 80)
    by_p = t.per_provider()
    assert by_p["local_llm"]["calls"] == 2
    assert by_p["handoff"]["calls"] == 1


def test_per_cell_sorted_by_calls() -> None:
    t = CostTracker()
    for _ in range(3):
        t.record(provider="local_llm", cell_id="busy", request_text="x", response_text="y", outcome="accepted")
    t.record(provider="local_llm", cell_id="lonely", request_text="x", response_text="y", outcome="accepted")
    rows = t.per_cell()
    assert rows[0]["cell_id"] == "busy"
    assert rows[0]["calls"] == 3
    assert rows[1]["cell_id"] == "lonely"
    assert rows[1]["calls"] == 1


def test_per_cell_top_n() -> None:
    t = CostTracker()
    for cell in ("a", "b", "c"):
        for _ in range(2):
            t.record(provider="x", cell_id=cell, request_text="x", response_text="y", outcome="accepted")
    rows = t.per_cell(top_n=2)
    assert len(rows) == 2


def test_per_cell_tracks_accepted_vs_rejected() -> None:
    t = CostTracker()
    t.record(provider="x", cell_id="a", request_text="x", response_text="y", outcome="accepted")
    t.record(provider="x", cell_id="a", request_text="x", response_text="y", outcome="rejected_checker")
    t.record(provider="x", cell_id="a", request_text="x", response_text="y", outcome="rejected_parse")
    rows = t.per_cell()
    a = rows[0]
    assert a["accepted"] == 1
    assert a["rejected"] == 2


def test_reject_rate_alerts() -> None:
    t = CostTracker()
    # Bad cell: 4 rejections, 1 accept (80% reject rate)
    for _ in range(4):
        t.record(provider="x", cell_id="bad_cell", request_text="x", response_text="y", outcome="rejected_checker")
    t.record(provider="x", cell_id="bad_cell", request_text="x", response_text="y", outcome="accepted")
    # Good cell: 5 accepts
    for _ in range(5):
        t.record(provider="x", cell_id="good_cell", request_text="x", response_text="y", outcome="accepted")
    alerts = t.reject_rate_alerts(threshold=0.7)
    assert any("bad_cell" in a for a in alerts)
    assert all("good_cell" not in a for a in alerts)


def test_reject_rate_alerts_respects_min_calls() -> None:
    t = CostTracker()
    # Only 1 call, all rejected — should NOT alert (too few calls)
    t.record(provider="x", cell_id="rare", request_text="x", response_text="y", outcome="rejected_checker")
    assert t.reject_rate_alerts(min_calls=3) == []


def test_summary_shape() -> None:
    t = CostTracker()
    t.record(provider="x", cell_id="a", request_text="x" * 20, response_text="y" * 10, outcome="accepted")
    s = t.summary()
    for key in ("total_calls", "total_input_tokens", "total_output_tokens",
                "total_tokens", "per_provider", "per_cell_top10", "reject_rate_alerts"):
        assert key in s


# ---------------------------------------------------------------------------
# write_report
# ---------------------------------------------------------------------------


def test_write_report(tmp_path: Path) -> None:
    t = CostTracker()
    t.record(provider="x", cell_id="a", request_text="x" * 100, response_text="y" * 40, outcome="accepted")
    out = tmp_path / "cost.json"
    written = t.write_report(out)
    assert written == out
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["summary"]["total_calls"] == 1
    assert len(payload["calls"]) == 1
    assert payload["calls"][0]["provider"] == "x"
