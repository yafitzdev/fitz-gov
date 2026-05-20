"""Tests for fitz_gov.sdgp.providers."""

from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest

from fitz_gov.sdgp.providers import (
    BlindLabelPair,
    FileHandoffProvider,
    GenerateRequest,
    LocalLlmProvider,
    ProviderError,
    ProviderTimeoutError,
    RoundRobinProvider,
    StubProvider,
    providers_from_env,
)


# ---------------------------------------------------------------------------
# StubProvider
# ---------------------------------------------------------------------------


def test_stub_provider_fixed_response() -> None:
    p = StubProvider(response="hello world")
    assert p.generate(GenerateRequest(prompt="anything")) == "hello world"


def test_stub_provider_callable_response() -> None:
    p = StubProvider(response=lambda r: r.prompt.upper())
    assert p.generate(GenerateRequest(prompt="hi")) == "HI"


def test_stub_provider_healthcheck_default_true() -> None:
    assert StubProvider().healthcheck() is True


# ---------------------------------------------------------------------------
# RoundRobinProvider
# ---------------------------------------------------------------------------


def test_round_robin_rotates() -> None:
    a = StubProvider(response="A", name="a")
    b = StubProvider(response="B", name="b")
    rr = RoundRobinProvider(providers=[a, b])
    assert rr.generate(GenerateRequest(prompt="x")) == "A"
    assert rr.generate(GenerateRequest(prompt="x")) == "B"
    assert rr.generate(GenerateRequest(prompt="x")) == "A"


def test_round_robin_requires_at_least_one_provider() -> None:
    with pytest.raises(ValueError):
        RoundRobinProvider(providers=[])


def test_round_robin_healthcheck_any() -> None:
    class Dead(StubProvider):
        def healthcheck(self) -> bool:
            return False

    rr = RoundRobinProvider(providers=[Dead(), StubProvider()])
    assert rr.healthcheck() is True
    rr2 = RoundRobinProvider(providers=[Dead(), Dead()])
    assert rr2.healthcheck() is False


# ---------------------------------------------------------------------------
# BlindLabelPair
# ---------------------------------------------------------------------------


def test_blind_label_pair_returns_a_different_provider() -> None:
    a = StubProvider(response="A", name="a")
    b = StubProvider(response="B", name="b")
    pair = BlindLabelPair(pool=[a, b])
    assert pair.validator_for(a) is b
    assert pair.validator_for(b) is a


def test_blind_label_pair_requires_at_least_two_providers() -> None:
    with pytest.raises(ValueError):
        BlindLabelPair(pool=[StubProvider()])


def test_blind_label_pair_picks_third_when_pool_has_three() -> None:
    a = StubProvider(name="a")
    b = StubProvider(name="b")
    c = StubProvider(name="c")
    pair = BlindLabelPair(pool=[a, b, c])
    validator = pair.validator_for(b)
    assert validator is not b
    assert validator in (a, c)


# ---------------------------------------------------------------------------
# FileHandoffProvider
# ---------------------------------------------------------------------------


def test_file_handoff_writes_request_and_reads_response(tmp_path: Path) -> None:
    """Stage a response file on a background thread and verify the
    provider picks it up + archives both halves."""
    provider = FileHandoffProvider(handoff_dir=tmp_path / "h", timeout_s=5.0, poll_interval_s=0.05)
    req = GenerateRequest(prompt="generate a numerical_conflict case", metadata={"cell_id": "test"})

    def stage_response_after(delay_s: float) -> None:
        time.sleep(delay_s)
        # Find the just-written request file (most recent in/)
        in_files = sorted((tmp_path / "h" / "in").glob("*.json"))
        assert in_files, "no request file appeared in handoff/in/"
        request_id = in_files[-1].stem
        (tmp_path / "h" / "out" / f"{request_id}.txt").write_text("HERE IS YOUR CASE", encoding="utf-8")

    t = threading.Thread(target=stage_response_after, args=(0.2,))
    t.start()
    try:
        result = provider.generate(req)
        assert result == "HERE IS YOUR CASE"
    finally:
        t.join()

    # Both in and out files moved to done/
    done = list((tmp_path / "h" / "done").iterdir())
    assert len(done) == 1
    assert (done[0] / "request.json").exists()
    assert (done[0] / "response.txt").exists()


def test_file_handoff_times_out_cleanly(tmp_path: Path) -> None:
    provider = FileHandoffProvider(
        handoff_dir=tmp_path / "h", timeout_s=0.3, poll_interval_s=0.05
    )
    with pytest.raises(ProviderTimeoutError):
        provider.generate(GenerateRequest(prompt="never answered"))
    # Pending in-file cleaned up
    assert list((tmp_path / "h" / "in").iterdir()) == []


def test_file_handoff_writes_metadata_in_request(tmp_path: Path) -> None:
    """The request file should carry prompt, system, metadata, etc., so the
    subagent has full context."""
    provider = FileHandoffProvider(
        handoff_dir=tmp_path / "h", timeout_s=0.5, poll_interval_s=0.05
    )
    req = GenerateRequest(
        prompt="prompt body",
        system="be terse",
        max_tokens=512,
        temperature=0.2,
        stop=["</end>"],
        metadata={"cell_id": "wrong_entity__history_geography__hard"},
    )
    # Stage response then call generate
    def respond() -> None:
        time.sleep(0.1)
        in_files = sorted((tmp_path / "h" / "in").glob("*.json"))
        request_id = in_files[-1].stem
        (tmp_path / "h" / "out" / f"{request_id}.txt").write_text("ok", encoding="utf-8")

    t = threading.Thread(target=respond)
    t.start()
    try:
        result = provider.generate(req)
        assert result == "ok"
    finally:
        t.join()

    done = list((tmp_path / "h" / "done").iterdir())[0]
    import json
    written = json.loads((done / "request.json").read_text(encoding="utf-8"))
    assert written["prompt"] == "prompt body"
    assert written["system"] == "be terse"
    assert written["max_tokens"] == 512
    assert written["temperature"] == 0.2
    assert written["stop"] == ["</end>"]
    assert written["metadata"]["cell_id"] == "wrong_entity__history_geography__hard"


def test_file_handoff_healthcheck(tmp_path: Path) -> None:
    p = FileHandoffProvider(handoff_dir=tmp_path / "h")
    assert p.healthcheck() is True


# ---------------------------------------------------------------------------
# LocalLlmProvider — smoke test (without a running Ollama, healthcheck fails)
# ---------------------------------------------------------------------------


def test_local_llm_unreachable_healthcheck() -> None:
    """If Ollama isn't running on this port, healthcheck reports False
    rather than raising."""
    p = LocalLlmProvider(model_id="x", base_url="http://localhost:1")
    assert p.healthcheck() is False


def test_local_llm_unreachable_raises_on_generate() -> None:
    p = LocalLlmProvider(model_id="x", base_url="http://localhost:1", request_timeout_s=1.0)
    with pytest.raises(ProviderError):
        p.generate(GenerateRequest(prompt="x"))


def test_local_llm_default_name_and_version() -> None:
    p = LocalLlmProvider(model_id="qwen3.5:0.8b")
    assert p.name == "local_llm"
    assert p.version == "qwen3.5:0.8b"


# ---------------------------------------------------------------------------
# providers_from_env
# ---------------------------------------------------------------------------


def test_providers_from_env_empty_by_default(monkeypatch) -> None:
    for k in ("SDGP_LOCAL_MODEL", "SDGP_LOCAL_URL", "SDGP_HANDOFF_DIR"):
        monkeypatch.delenv(k, raising=False)
    assert providers_from_env() == []


def test_providers_from_env_local(monkeypatch) -> None:
    monkeypatch.setenv("SDGP_LOCAL_MODEL", "qwen3.5:0.8b")
    monkeypatch.delenv("SDGP_HANDOFF_DIR", raising=False)
    out = providers_from_env()
    assert len(out) == 1
    assert isinstance(out[0], LocalLlmProvider)
    assert out[0].model_id == "qwen3.5:0.8b"


def test_providers_from_env_local_plus_handoff(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("SDGP_LOCAL_MODEL", "qwen3.5:0.8b")
    monkeypatch.setenv("SDGP_HANDOFF_DIR", str(tmp_path / "h"))
    out = providers_from_env()
    assert len(out) == 2
    assert any(isinstance(p, LocalLlmProvider) for p in out)
    assert any(isinstance(p, FileHandoffProvider) for p in out)
