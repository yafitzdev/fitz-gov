#!/usr/bin/env python3
"""Merge generated batch case files into the main tier1_core data files."""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "tier1_core"
SCRIPTS_DIR = Path(__file__).parent


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  Wrote {path.name}")


def get_existing_ids(cases: list[dict]) -> set[str]:
    return {c["id"] for c in cases}


def merge_into(target_file: Path, new_cases: list[dict], label: str) -> int:
    data = load_json(target_file)
    existing_ids = get_existing_ids(data["cases"])

    added = 0
    for case in new_cases:
        if case["id"] not in existing_ids:
            data["cases"].append(case)
            existing_ids.add(case["id"])
            added += 1

    if added > 0:
        save_json(target_file, data)

    print(f"  {label}: {added} new cases added ({len(data['cases'])} total)")
    return added


def main():
    print("=" * 60)
    print("Merging new cases into tier1_core data files")
    print("=" * 60)

    total_added = 0

    # Merge dispute batch 1
    print("\nDispute batch 1:")
    batch1 = load_json(SCRIPTS_DIR / "new_dispute_batch1.json")
    total_added += merge_into(
        DATA_DIR / "dispute.json", batch1["cases"], "dispute_batch1"
    )

    # Merge dispute batch 2
    print("\nDispute batch 2:")
    batch2 = load_json(SCRIPTS_DIR / "new_dispute_batch2.json")
    total_added += merge_into(
        DATA_DIR / "dispute.json", batch2["cases"], "dispute_batch2"
    )

    # Merge abstain batch 1
    print("\nAbstain batch 1:")
    abst1 = load_json(SCRIPTS_DIR / "new_abstain_batch1.json")
    total_added += merge_into(
        DATA_DIR / "abstention.json", abst1["cases"], "abstain_batch1"
    )

    # Merge abstain batch 2
    print("\nAbstain batch 2:")
    abst2 = load_json(SCRIPTS_DIR / "new_abstain_batch2.json")
    total_added += merge_into(
        DATA_DIR / "abstention.json", abst2["cases"], "abstain_batch2"
    )

    # Merge multi-source trustworthy
    print("\nMulti-source trustworthy:")
    ms = load_json(SCRIPTS_DIR / "new_trustworthy_multisource.json")
    total_added += merge_into(
        DATA_DIR / "trustworthy_direct.json",
        ms["direct_cases"],
        "trustworthy_direct (multi-source)",
    )
    total_added += merge_into(
        DATA_DIR / "trustworthy_hedged.json",
        ms["hedged_cases"],
        "trustworthy_hedged (multi-source)",
    )

    print(f"\n{'=' * 60}")
    print(f"Total new cases added: {total_added}")
    print(f"{'=' * 60}")

    # Final counts
    print("\nFinal case counts:")
    for fn in [
        "dispute.json",
        "abstention.json",
        "trustworthy_direct.json",
        "trustworthy_hedged.json",
    ]:
        data = load_json(DATA_DIR / fn)
        print(f"  {fn}: {len(data['cases'])} cases")

    # Check for duplicate IDs across all files
    print("\nChecking for duplicate IDs...")
    all_ids = []
    for fn in [
        "dispute.json",
        "abstention.json",
        "trustworthy_direct.json",
        "trustworthy_hedged.json",
        "grounding.json",
        "relevance.json",
    ]:
        fp = DATA_DIR / fn
        if fp.exists():
            data = load_json(fp)
            for c in data.get("cases", []):
                all_ids.append(c["id"])

    dupes = [id for id in all_ids if all_ids.count(id) > 1]
    if dupes:
        print(f"  WARNING: {len(set(dupes))} duplicate IDs found: {set(dupes)}")
    else:
        print(f"  No duplicates found across {len(all_ids)} cases")


if __name__ == "__main__":
    main()
