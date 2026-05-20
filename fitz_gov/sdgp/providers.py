"""SDGP provider abstraction — pluggable LLM backends for case generation.

The generator never talks to an LLM API directly. It calls `Provider.generate(prompt)`
and gets a string back. Three concrete providers are shipped:

  - **`LocalLlmProvider`** — Ollama HTTP backend. Fastest for bulk enrichment;
    runs locally; no per-token cost. Default endpoint `http://localhost:11434`.
  - **`FileHandoffProvider`** — file-based handoff for Claude Code / Codex
    subagents. The pipeline writes a request file to `handoff_dir/in/`,
    a subagent (manual or scripted) reads it, generates, and writes the
    response to `handoff_dir/out/`. Polls until the response appears or
    timeout. The "no API!" path.
  - **`RoundRobinProvider`** — wraps a list of providers and rotates between
    them per request. The "switch between AI provider" knob.

Plus a `StubProvider` for tests / dry-runs (deterministic, no I/O).

All providers are synchronous. Concurrency lives in the orchestrator (spawn
multiple workers, each holding its own Provider). Designed so the orchestrator
treats Claude Code subagents, Codex subagents, and a local model identically.
"""

from __future__ import annotations

import abc
import json
import os
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Sequence


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class ProviderError(Exception):
    """Base class for provider failures."""


class ProviderTimeoutError(ProviderError):
    """Raised when a provider doesn't respond within its budget."""


class ProviderHTTPError(ProviderError):
    """Raised on HTTP failures from a network-backed provider."""


# ---------------------------------------------------------------------------
# Provider ABC + request shape
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class GenerateRequest:
    """One generation request. Shared shape across providers."""

    prompt: str
    max_tokens: int = 2048
    temperature: float = 0.7
    system: str | None = None
    stop: Sequence[str] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class Provider(abc.ABC):
    """Abstract LLM backend. `name` and `version` go into `Provenance`."""

    name: str = "abstract"
    version: str = "0"

    @abc.abstractmethod
    def generate(self, req: GenerateRequest) -> str:
        """Return the generated string. Implementations may block."""
        ...

    def healthcheck(self) -> bool:
        """Best-effort: return True if the provider is reachable. Default = True."""
        return True

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.name!r}, version={self.version!r})"


# ---------------------------------------------------------------------------
# StubProvider — deterministic, for tests + dry-runs
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class StubProvider(Provider):
    """A provider that returns canned text. Useful for tests and
    --dry-run pipelines. Either give it a fixed `response` or a callable
    that takes the request and returns a string."""

    response: str | Callable[[GenerateRequest], str] = ""
    name: str = "stub"
    version: str = "0"

    def generate(self, req: GenerateRequest) -> str:
        if callable(self.response):
            return self.response(req)
        return self.response


# ---------------------------------------------------------------------------
# LocalLlmProvider — Ollama HTTP backend
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class LocalLlmProvider(Provider):
    """Ollama HTTP backend. Talks to `POST /api/generate` synchronously.

    Defaults assume a locally-running Ollama (e.g. `ollama serve`). The
    `model_id` must be already pulled (e.g. `ollama pull qwen3.5:0.8b`).
    """

    model_id: str = "qwen3.5:0.8b"
    base_url: str = "http://localhost:11434"
    request_timeout_s: float = 120.0
    name: str = ""
    version: str = ""

    def __post_init__(self) -> None:
        if not self.name:
            self.name = "local_llm"
        if not self.version:
            self.version = self.model_id

    def healthcheck(self) -> bool:
        import urllib.error
        import urllib.request

        try:
            req = urllib.request.Request(self.base_url + "/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                return resp.status == 200
        except (urllib.error.URLError, TimeoutError, OSError):
            return False

    def generate(self, req: GenerateRequest) -> str:
        import urllib.error
        import urllib.request

        payload: dict[str, Any] = {
            "model": self.model_id,
            "prompt": req.prompt,
            "stream": False,
            "options": {
                "temperature": req.temperature,
                "num_predict": req.max_tokens,
            },
        }
        if req.system:
            payload["system"] = req.system
        if req.stop:
            payload["options"]["stop"] = list(req.stop)

        body = json.dumps(payload).encode("utf-8")
        http_req = urllib.request.Request(
            self.base_url + "/api/generate",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(http_req, timeout=self.request_timeout_s) as resp:
                if resp.status != 200:
                    raise ProviderHTTPError(
                        f"ollama returned HTTP {resp.status}: {resp.read()!r:.200}"
                    )
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise ProviderHTTPError(f"ollama HTTPError: {exc}") from exc
        except urllib.error.URLError as exc:
            raise ProviderError(f"ollama unreachable at {self.base_url}: {exc}") from exc
        except TimeoutError as exc:
            raise ProviderTimeoutError(
                f"ollama did not respond within {self.request_timeout_s}s"
            ) from exc

        text = data.get("response")
        if not isinstance(text, str):
            raise ProviderError(f"ollama response had no 'response' string: {data!r:.200}")
        return text


# ---------------------------------------------------------------------------
# FileHandoffProvider — Claude Code / Codex subagent integration
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class FileHandoffProvider(Provider):
    """File-based handoff for subagent providers (Claude Code / Codex / human).

    Workflow:
      1. `.generate(req)` writes `handoff_dir/in/{request_id}.json` with the
         prompt + metadata, then polls `handoff_dir/out/{request_id}.txt`.
      2. A subagent (spawned via Claude Code Agent / Codex / by hand) reads
         the in-file, generates, and writes the response text to out-file.
      3. `.generate` returns the response and moves both files to
         `handoff_dir/done/{request_id}/`.

    This is intentionally simple: the subagent could be a Claude Code Agent
    invocation in a parent session, a Codex CLI loop, or a human typing
    responses. The pipeline doesn't care.

    Pass `poll_interval_s=0.0` + `timeout_s=0` for tests that pre-stage the
    response file.
    """

    handoff_dir: Path = Path("data/sdgp_handoff")
    timeout_s: float = 600.0
    poll_interval_s: float = 1.0
    name: str = "file_handoff"
    version: str = "v1"

    def __post_init__(self) -> None:
        self.handoff_dir = Path(self.handoff_dir)
        (self.handoff_dir / "in").mkdir(parents=True, exist_ok=True)
        (self.handoff_dir / "out").mkdir(parents=True, exist_ok=True)
        (self.handoff_dir / "done").mkdir(parents=True, exist_ok=True)

    def healthcheck(self) -> bool:
        return self.handoff_dir.exists() and os.access(self.handoff_dir, os.W_OK)

    def _next_request_id(self) -> str:
        return f"{int(time.time() * 1000):013d}_{uuid.uuid4().hex[:8]}"

    def generate(self, req: GenerateRequest) -> str:
        request_id = self._next_request_id()
        in_path = self.handoff_dir / "in" / f"{request_id}.json"
        out_path = self.handoff_dir / "out" / f"{request_id}.txt"

        payload = {
            "request_id": request_id,
            "prompt": req.prompt,
            "system": req.system,
            "max_tokens": req.max_tokens,
            "temperature": req.temperature,
            "stop": list(req.stop) if req.stop else None,
            "metadata": req.metadata,
        }
        in_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

        deadline = time.time() + max(self.timeout_s, 0.0)
        # Allow immediate-fire polling for tests that pre-stage the response.
        while True:
            if out_path.exists():
                text = out_path.read_text(encoding="utf-8")
                self._archive(request_id, in_path, out_path)
                return text
            if time.time() >= deadline:
                # Best-effort cleanup of the pending in-file.
                try:
                    in_path.unlink(missing_ok=True)
                except OSError:
                    pass
                raise ProviderTimeoutError(
                    f"no response at {out_path} within {self.timeout_s}s"
                )
            time.sleep(max(self.poll_interval_s, 0.05))

    def _archive(self, request_id: str, in_path: Path, out_path: Path) -> None:
        done_dir = self.handoff_dir / "done" / request_id
        done_dir.mkdir(parents=True, exist_ok=True)
        try:
            in_path.replace(done_dir / "request.json")
        except OSError:
            pass
        try:
            out_path.replace(done_dir / "response.txt")
        except OSError:
            pass


# ---------------------------------------------------------------------------
# RoundRobinProvider — switch between providers per request
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class RoundRobinProvider(Provider):
    """Rotates through a list of providers per `.generate()` call.

    Useful for:
      - Splitting load between Claude Code subagents and a local Qwen
        (alternating providers for the same task).
      - Generator ↔ validator separation: never use the same provider
        for the same case twice (see `BlindLabelProvider` below).
    """

    providers: list[Provider] = field(default_factory=list)
    name: str = "round_robin"
    version: str = "v1"
    _counter: int = field(default=0, init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.providers:
            raise ValueError("RoundRobinProvider requires at least one provider")

    @property
    def current(self) -> Provider:
        return self.providers[self._counter % len(self.providers)]

    def healthcheck(self) -> bool:
        return any(p.healthcheck() for p in self.providers)

    def generate(self, req: GenerateRequest) -> str:
        p = self.current
        self._counter += 1
        return p.generate(req)


# ---------------------------------------------------------------------------
# BlindLabelProvider — sibling pair where the labeler is always a different
# concrete provider than the generator
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class BlindLabelPair:
    """A (generator, validator) pair that's guaranteed to use different
    provider instances. The orchestrator's blind-label step picks the
    validator from `.validator_for(generator)` so the generator-validator
    invariant from ROADMAP §4 ("must never be the same model") is enforced
    by construction.

    Provide a pool of providers; `validator_for(g)` returns any provider
    in the pool other than g. Falls back gracefully when only one is left.
    """

    pool: list[Provider]

    def __post_init__(self) -> None:
        if len(self.pool) < 2:
            raise ValueError(
                "BlindLabelPair needs at least 2 providers; "
                "see ROADMAP §4 'generator and validator must never be the same model'"
            )

    def validator_for(self, generator: Provider) -> Provider:
        """Return any provider in the pool that is not the generator's instance."""
        for p in self.pool:
            if p is not generator:
                return p
        raise ValueError("no validator available — pool exhausted")


# ---------------------------------------------------------------------------
# Convenience factories
# ---------------------------------------------------------------------------


def make_default_local() -> LocalLlmProvider:
    """Local Ollama with sane defaults: qwen3.5:0.8b at localhost:11434."""
    return LocalLlmProvider(model_id="qwen3.5:0.8b")


def providers_from_env() -> list[Provider]:
    """Read provider config from env vars. Useful for the orchestrator CLI.

    Recognized vars:
      - `SDGP_LOCAL_MODEL` — Ollama model id (default: qwen3.5:0.8b).
      - `SDGP_LOCAL_URL` — Ollama base URL (default: http://localhost:11434).
      - `SDGP_HANDOFF_DIR` — file-handoff path (enables FileHandoffProvider).
      - `SDGP_HANDOFF_TIMEOUT` — handoff timeout seconds (default: 600).
    """
    out: list[Provider] = []
    if os.environ.get("SDGP_LOCAL_MODEL") or os.environ.get("SDGP_LOCAL_URL"):
        out.append(
            LocalLlmProvider(
                model_id=os.environ.get("SDGP_LOCAL_MODEL", "qwen3.5:0.8b"),
                base_url=os.environ.get("SDGP_LOCAL_URL", "http://localhost:11434"),
            )
        )
    if handoff := os.environ.get("SDGP_HANDOFF_DIR"):
        out.append(
            FileHandoffProvider(
                handoff_dir=Path(handoff),
                timeout_s=float(os.environ.get("SDGP_HANDOFF_TIMEOUT", "600")),
            )
        )
    return out
