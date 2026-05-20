"""SDGP data vault — append-only JSONL store with cell coverage index.

The vault is the single source of truth for generated V6+ cases. It owns:

  - **Storage**: `cases.jsonl` (one case per line, append-only). Crash-safe by
    construction — partial writes are lost, complete writes are kept.
  - **Index**: `index.json` is a derived cache mapping `cell_id → [case_id, ...]`
    so coverage queries don't require re-reading the JSONL. The index is
    rebuilt from JSONL on demand (e.g. after a crash) via `Vault.rebuild_index`.
  - **Idempotency**: adding a case with an id that already exists is a no-op
    (returns `False`). Cases generated twice by independent subagents land
    once. Strict mode raises instead.
  - **Provenance**: every added case is stamped with `_vault` metadata —
    timestamp, provider, prompt version, batch id, seed — so we can attribute
    every row and reproduce generation.

Designed for single-process use. Subagents (Claude Code / Codex spawns / local
LLM calls) emit cases to handoff files; the parent process harvests them and
calls `vault.add(...)` sequentially. No file locking, no concurrent writes.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import uuid
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator

from .taxonomy import Cell, parse_cell_id


CASES_FILE = "cases.jsonl"
INDEX_FILE = "index.json"
VAULT_KEY = "_vault"


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class Provenance:
    """Per-case generation context. Stamped under `case[_vault]` on add."""

    provider: str  # e.g. "claude_code", "codex_subagent", "local_llm", "human", "migrated_v51"
    provider_version: str = ""  # e.g. model id "claude-sonnet-4-5" or "Qwen3.5-0.8B"
    prompt_version: str = ""  # e.g. "abstain_wrong_specificity_v1"
    batch_id: str = ""  # UUID grouping cases generated together
    run_seed: int | None = None
    added_at: str = ""  # set by Vault.add

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        # Don't write the seed key at all if unset (cleaner JSON)
        if d.get("run_seed") is None:
            d.pop("run_seed", None)
        return d


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class VaultError(Exception):
    """Base class for vault errors."""


class DuplicateCaseError(VaultError):
    """Raised in strict mode when an id already exists."""


class CorruptVaultError(VaultError):
    """Raised when the JSONL has a row that can't be parsed."""


# ---------------------------------------------------------------------------
# Vault
# ---------------------------------------------------------------------------


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _atomic_write_json(path: Path, payload: Any) -> None:
    """Write JSON atomically by way of a temp file in the same directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=str(path.parent),
        prefix=path.name + ".",
        suffix=".tmp",
        delete=False,
    )
    try:
        json.dump(payload, tmp, indent=2, ensure_ascii=False)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp.close()
        os.replace(tmp.name, str(path))
    except Exception:
        tmp.close()
        try:
            os.unlink(tmp.name)
        except OSError:
            pass
        raise


def _read_jsonl(path: Path) -> Iterator[tuple[int, dict[str, Any]]]:
    """Yield (line_number, parsed_dict) for each non-blank line."""
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as fh:
        for i, raw in enumerate(fh, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                yield i, json.loads(line)
            except json.JSONDecodeError as exc:
                raise CorruptVaultError(
                    f"{path}: line {i} is not valid JSON: {exc}"
                ) from exc


@dataclass(slots=True)
class _IndexState:
    """Derived state held in memory + persisted to index.json."""

    case_ids: set[str] = field(default_factory=set)
    cell_to_case_ids: dict[str, list[str]] = field(default_factory=dict)
    n_cases: int = 0
    # Per-cell counter used to mint new ids ("seq" so two cases in the same
    # cell don't collide when the caller doesn't supply an id).
    cell_seq: dict[str, int] = field(default_factory=dict)


class Vault:
    """Append-only JSONL store for SDGP cases, with a derived cell index.

    Usage:

        v = Vault.open(Path("data/sdgp_vault"))
        case = build_a_case(...)
        was_new = v.add(case, provenance=Provenance(provider="claude_code"))
        coverage = v.cell_counts()           # cell_id -> int
        for case in v.iter_cases(): ...
    """

    def __init__(self, root: Path, *, _state: _IndexState | None = None) -> None:
        self.root = Path(root)
        self.cases_path = self.root / CASES_FILE
        self.index_path = self.root / INDEX_FILE
        self._state: _IndexState = _state or _IndexState()

    # ---- Construction --------------------------------------------------

    @classmethod
    def open(cls, root: Path) -> "Vault":
        """Open an existing vault directory or create a fresh one.

        If `index.json` is missing or stale (case count != JSONL line count),
        the index is rebuilt from the JSONL.
        """
        root = Path(root)
        root.mkdir(parents=True, exist_ok=True)
        v = cls(root)
        v._load_or_rebuild_index()
        return v

    def _load_or_rebuild_index(self) -> None:
        if not self.cases_path.exists():
            # Brand-new vault
            self._state = _IndexState()
            self._persist_index()
            return
        # Count lines to detect index drift cheaply.
        with self.cases_path.open("r", encoding="utf-8") as fh:
            n_lines = sum(1 for line in fh if line.strip())
        if self.index_path.exists():
            try:
                with self.index_path.open("r", encoding="utf-8") as fh:
                    raw = json.load(fh)
                if raw.get("n_cases") == n_lines:
                    self._state = _IndexState(
                        case_ids=set(raw.get("case_ids", [])),
                        cell_to_case_ids={
                            k: list(v) for k, v in raw.get("cell_to_case_ids", {}).items()
                        },
                        n_cases=int(raw.get("n_cases", 0)),
                        cell_seq=dict(raw.get("cell_seq", {})),
                    )
                    return
            except (json.JSONDecodeError, OSError):
                pass  # fall through to rebuild
        self.rebuild_index()

    def rebuild_index(self) -> None:
        """Re-derive the index from the JSONL. Always safe to call."""
        s = _IndexState()
        for _, case in _read_jsonl(self.cases_path):
            cid = self._require_case_id(case)
            s.case_ids.add(cid)
            s.n_cases += 1
            cell_id = self._extract_cell_id(case)
            if cell_id:
                s.cell_to_case_ids.setdefault(cell_id, []).append(cid)
                s.cell_seq[cell_id] = max(
                    s.cell_seq.get(cell_id, 0),
                    self._extract_seq_from_id(cid),
                )
        self._state = s
        self._persist_index()

    def _persist_index(self) -> None:
        payload = {
            "n_cases": self._state.n_cases,
            "case_ids": sorted(self._state.case_ids),
            "cell_to_case_ids": {
                k: list(v) for k, v in sorted(self._state.cell_to_case_ids.items())
            },
            "cell_seq": dict(self._state.cell_seq),
            "updated_at": _utcnow_iso(),
        }
        _atomic_write_json(self.index_path, payload)

    # ---- Reads ---------------------------------------------------------

    def __len__(self) -> int:
        return self._state.n_cases

    def __contains__(self, case_id: str) -> bool:
        return case_id in self._state.case_ids

    def iter_cases(self) -> Iterator[dict[str, Any]]:
        """Stream every case in insertion order. Yields fresh dicts (callers may mutate)."""
        for _, case in _read_jsonl(self.cases_path):
            yield case

    def case_ids(self) -> list[str]:
        return sorted(self._state.case_ids)

    def cell_counts(self) -> dict[str, int]:
        """`cell_id` → number of cases currently filling that cell."""
        return {k: len(v) for k, v in self._state.cell_to_case_ids.items()}

    def cell_count(self, cell: Cell | str) -> int:
        key = cell.cell_id if isinstance(cell, Cell) else cell
        return len(self._state.cell_to_case_ids.get(key, ()))

    def get(self, case_id: str) -> dict[str, Any] | None:
        """O(n) lookup — fine for one-offs; use `iter_cases` for bulk reads."""
        for case in self.iter_cases():
            if case.get("id") == case_id:
                return case
        return None

    # ---- Writes --------------------------------------------------------

    def add(
        self,
        case: dict[str, Any],
        *,
        provenance: Provenance | None = None,
        strict: bool = False,
    ) -> bool:
        """Append a case to the vault. Returns True if newly added, False if it was a duplicate.

        - If `case["id"]` is missing or empty, an id is minted from the case's
          cell_id (`{cell_id}_{seq:03d}`).
        - Duplicate ids are a no-op (or raise DuplicateCaseError in `strict`).
        - `provenance` is stamped onto the case under `_vault`; `added_at` is
          filled in automatically.
        """
        case = dict(case)  # don't mutate caller's dict in-place

        # Mint id if missing.
        if not case.get("id"):
            cell_id = self._extract_cell_id(case)
            if cell_id is None:
                raise VaultError(
                    "case is missing both `id` and a parseable taxonomy.cell_id; "
                    "set one explicitly"
                )
            seq = self._state.cell_seq.get(cell_id, 0) + 1
            case["id"] = f"{cell_id}_{seq:03d}"

        cid = self._require_case_id(case)

        if cid in self._state.case_ids:
            if strict:
                raise DuplicateCaseError(f"case_id already present: {cid}")
            return False

        # Stamp provenance.
        prov_dict: dict[str, Any] = {"added_at": _utcnow_iso()}
        if provenance is not None:
            prov_dict.update(provenance.to_dict())
            prov_dict["added_at"] = _utcnow_iso()  # always set ours, ignore caller's
        case[VAULT_KEY] = prov_dict

        # Append to JSONL (atomic by line).
        self.cases_path.parent.mkdir(parents=True, exist_ok=True)
        with self.cases_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(case, ensure_ascii=False))
            fh.write("\n")

        # Update in-memory index.
        self._state.case_ids.add(cid)
        self._state.n_cases += 1
        cell_id = self._extract_cell_id(case)
        if cell_id:
            self._state.cell_to_case_ids.setdefault(cell_id, []).append(cid)
            self._state.cell_seq[cell_id] = max(
                self._state.cell_seq.get(cell_id, 0),
                self._extract_seq_from_id(cid),
            )

        self._persist_index()
        return True

    def add_many(
        self,
        cases: Iterable[dict[str, Any]],
        *,
        provenance: Provenance | None = None,
        strict: bool = False,
    ) -> dict[str, int]:
        """Bulk add. Returns {"added": n, "duplicate": n}. One index persist at the end."""
        added = 0
        duplicate = 0
        # Append all to JSONL first, then update index once.
        new_rows: list[tuple[str, str | None, dict[str, Any]]] = []  # (id, cell_id, dict)
        for case in cases:
            case = dict(case)
            if not case.get("id"):
                cell_id_for_mint = self._extract_cell_id(case)
                if cell_id_for_mint is None:
                    raise VaultError(
                        "case missing both id and taxonomy.cell_id in add_many"
                    )
                seq = self._state.cell_seq.get(cell_id_for_mint, 0) + 1
                # Pre-bump so the next mint within this batch doesn't collide
                self._state.cell_seq[cell_id_for_mint] = seq
                case["id"] = f"{cell_id_for_mint}_{seq:03d}"

            cid = self._require_case_id(case)
            if cid in self._state.case_ids:
                if strict:
                    raise DuplicateCaseError(f"case_id already present: {cid}")
                duplicate += 1
                continue
            prov_dict: dict[str, Any] = {"added_at": _utcnow_iso()}
            if provenance is not None:
                prov_dict.update(provenance.to_dict())
                prov_dict["added_at"] = _utcnow_iso()
            case[VAULT_KEY] = prov_dict

            new_rows.append((cid, self._extract_cell_id(case), case))
            # Reserve in the in-memory set so a duplicate within the same batch
            # only lands once.
            self._state.case_ids.add(cid)

        if new_rows:
            self.cases_path.parent.mkdir(parents=True, exist_ok=True)
            with self.cases_path.open("a", encoding="utf-8") as fh:
                for cid, cell_id, case in new_rows:
                    fh.write(json.dumps(case, ensure_ascii=False))
                    fh.write("\n")
                    self._state.n_cases += 1
                    if cell_id:
                        self._state.cell_to_case_ids.setdefault(cell_id, []).append(cid)
                        self._state.cell_seq[cell_id] = max(
                            self._state.cell_seq.get(cell_id, 0),
                            self._extract_seq_from_id(cid),
                        )
                    added += 1
            self._persist_index()
        return {"added": added, "duplicate": duplicate}

    # ---- Helpers -------------------------------------------------------

    @staticmethod
    def _require_case_id(case: dict[str, Any]) -> str:
        cid = case.get("id")
        if not isinstance(cid, str) or not cid:
            raise VaultError(f"case is missing a string `id`: {case!r:.200}")
        return cid

    @staticmethod
    def _extract_cell_id(case: dict[str, Any]) -> str | None:
        """Get the taxonomy.cell_id if present. Returns None if the case is
        missing taxonomy metadata (legacy V5.1-shaped rows, for example).
        """
        tax = case.get("taxonomy")
        if isinstance(tax, dict):
            cid = tax.get("cell_id")
            if isinstance(cid, str) and cid:
                # Validate it parses (so a malformed cell_id surfaces here, not later).
                try:
                    parse_cell_id(cid)
                except ValueError:
                    return None
                return cid
        return None

    @staticmethod
    def _extract_seq_from_id(case_id: str) -> int:
        """Recover the integer suffix from `cell_id_NNN`; 0 if not present."""
        tail = case_id.rsplit("_", 1)[-1]
        try:
            return int(tail)
        except ValueError:
            return 0


# ---------------------------------------------------------------------------
# Convenience
# ---------------------------------------------------------------------------


def new_batch_id() -> str:
    """Stable opaque id for grouping cases produced in the same generation run."""
    return uuid.uuid4().hex[:12]


def drop_vault_fields(case: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of `case` with `_vault` stripped — for publishing to HF."""
    out = {k: v for k, v in case.items() if k != VAULT_KEY}
    return out
