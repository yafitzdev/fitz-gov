"""sdgp_triage.py — interactive triage for SDGP conflict-queue cases.

Lists pending conflicts under `<vault>/conflicts/**/*.json` and walks them
one at a time. For each, prints the case + both labels, accepts a
disposition, records the outcome.

Dispositions:

  - **a** — accept the generator's label → vault the case as-is
  - **v** — accept the validator's label → patch governance.classification
    + taxonomy.governance_class to the validator's call, vault
  - **e** — edit the case (drops you into $EDITOR; reloads on return), then
    re-classifies via the checker
  - **r** — reject (move to `<vault>/conflicts/<batch>/rejected/`)
  - **s** — skip (leave in place for next session)
  - **q** — quit (preserves remaining queue)

Usage (from fitz-gov repo root):
    python scripts/sdgp_triage.py --vault data/sdgp_vault_v51_enriched
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.checker import Checker
from fitz_gov.sdgp.vault import Provenance, Vault, new_batch_id


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--vault", type=Path, required=True)
    p.add_argument("--batch", type=str, default=None, help="Only triage a specific batch_id under conflicts/")
    p.add_argument("--non-interactive", action="store_true",
                   help="List conflicts and exit (no prompts)")
    return p.parse_args()


def list_conflict_files(conflicts_root: Path, batch: str | None) -> list[Path]:
    if not conflicts_root.exists():
        return []
    if batch:
        return sorted((conflicts_root / batch).rglob("*.json"))
    return sorted(conflicts_root.rglob("*.json"))


def truncate(text: str, n: int = 240) -> str:
    return text if len(text) <= n else text[:n] + "..."


def show_conflict(payload: dict[str, Any]) -> None:
    case = payload["case"]
    gen = payload.get("generator_label")
    val = payload.get("validator_label")
    print()
    print("=" * 78)
    print(f"id        : {case.get('id', '<no id>')}")
    print(f"cell_id   : {case.get('taxonomy', {}).get('cell_id', '<no cell_id>')}")
    print(f"generator : {gen}  ({payload.get('generator_provider', '?')})")
    print(f"validator : {val}  ({payload.get('validator_provider', '?')})")
    print(f"recorded  : {payload.get('recorded_at', '?')}")
    print()
    print("query     :")
    q = case.get("input", {}).get("query", case.get("query", "<no query>"))
    print(f"  {truncate(str(q), 400)}")
    print()
    print("contexts  :")
    raw_ctxs = case.get("input", {}).get("contexts") or case.get("contexts") or []
    for i, c in enumerate(raw_ctxs, start=1):
        t = c.get("text", "") if isinstance(c, dict) else str(c)
        print(f"  [{i}] {truncate(t, 300)}")
    print()


def open_in_editor(initial: str) -> str:
    editor = os.environ.get("EDITOR") or ("notepad" if os.name == "nt" else "vi")
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".json", delete=False, encoding="utf-8"
    ) as tf:
        tf.write(initial)
        tf.flush()
        path = tf.name
    try:
        subprocess.call([editor, path])
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def archive_path(conflict_path: Path, subdir: str) -> Path:
    """Move conflict file to `<conflict_dir>/<subdir>/<filename>`."""
    target_dir = conflict_path.parent / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / conflict_path.name


def main() -> int:
    args = parse_args()
    vault = Vault.open(args.vault)
    conflicts_root = vault.root / "conflicts"
    files = list_conflict_files(conflicts_root, args.batch)
    print(f"Found {len(files)} pending conflict(s) under {conflicts_root}")
    if not files:
        return 0
    if args.non_interactive:
        for f in files:
            print(f"  {f}")
        return 0

    checker = Checker(pattern_structure_warning_only=True)
    batch_id = new_batch_id()
    triaged = {"accepted_gen": 0, "accepted_val": 0, "edited": 0, "rejected": 0, "skipped": 0}

    for i, path in enumerate(files, start=1):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"  SKIP malformed conflict file {path}: {exc}", file=sys.stderr)
            continue
        print(f"\n[{i}/{len(files)}] {path.name}")
        show_conflict(payload)
        while True:
            try:
                choice = input("a=accept-gen v=accept-val e=edit r=reject s=skip q=quit > ").strip().lower()
            except EOFError:
                choice = "q"
            case = payload["case"]
            if choice == "q":
                print(f"\nQuitting. Triaged this session: {triaged}")
                return 0
            if choice == "s":
                triaged["skipped"] += 1
                break
            if choice == "r":
                archive_path(path, "rejected")
                path.replace(archive_path(path, "rejected"))
                triaged["rejected"] += 1
                break
            if choice in ("a", "v"):
                # Patch governance fields to the chosen label, then vault.
                label = (
                    payload.get("generator_label") if choice == "a"
                    else payload.get("validator_label")
                )
                if not label:
                    print(f"  ERROR: no {choice}-label recorded; falling back to skip")
                    triaged["skipped"] += 1
                    break
                case.setdefault("governance", {})
                case["governance"]["classification"] = label
                case.setdefault("taxonomy", {})
                case["taxonomy"]["governance_class"] = label
                result = checker.check(case)
                if not result.passed:
                    print("  ERROR: case still fails checker after patch:")
                    for err in result.errors:
                        print(f"    - [{err.rule}] {err.message}")
                    continue  # back to disposition prompt
                added = vault.add(
                    case,
                    provenance=Provenance(
                        provider="triage_cli",
                        provider_version="v1",
                        prompt_version=f"triage:{choice}",
                        batch_id=batch_id,
                    ),
                )
                if not added:
                    print(f"  (case id already in vault; not re-added)")
                archive_path(path, f"accepted_{choice}")
                path.replace(archive_path(path, f"accepted_{choice}"))
                triaged["accepted_gen" if choice == "a" else "accepted_val"] += 1
                break
            if choice == "e":
                edited = open_in_editor(json.dumps(case, indent=2, ensure_ascii=False))
                try:
                    new_case = json.loads(edited)
                except json.JSONDecodeError as exc:
                    print(f"  ERROR: edited JSON didn't parse: {exc} — try again")
                    continue
                result = checker.check(new_case)
                if not result.passed:
                    print("  ERROR: edited case fails the checker:")
                    for err in result.errors:
                        print(f"    - [{err.rule}] {err.message}")
                    continue
                vault.add(
                    new_case,
                    provenance=Provenance(
                        provider="triage_cli",
                        provider_version="v1",
                        prompt_version="triage:edit",
                        batch_id=batch_id,
                    ),
                )
                archive_path(path, "edited")
                path.replace(archive_path(path, "edited"))
                triaged["edited"] += 1
                break
            print(f"  unknown choice {choice!r}; valid: a v e r s q")

    print(f"\nDone. Triaged: {triaged}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
