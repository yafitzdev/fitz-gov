#!/usr/bin/env python3
"""Merge rewritten batch files back into the main grounding.json and relevance.json."""

import json
from pathlib import Path


def merge_batches(main_file: str, batch_prefix: str, num_batches: int, id_threshold: str):
    """Replace template-generated cases in main_file with rewritten batch cases."""
    main_path = Path(main_file)
    with open(main_path, encoding="utf-8") as f:
        data = json.load(f)

    # Load all batch cases into a dict keyed by ID
    rewritten = {}
    for i in range(1, num_batches + 1):
        batch_path = Path(f"scripts/{batch_prefix}_batch{i}.json")
        with open(batch_path, encoding="utf-8") as f:
            batch_cases = json.load(f)
        for case in batch_cases:
            rewritten[case["id"]] = case
        print(f"  Loaded {len(batch_cases)} cases from {batch_path.name}")

    # Replace cases in the main file
    replaced = 0
    for i, case in enumerate(data["cases"]):
        if case["id"] in rewritten:
            data["cases"][i] = rewritten[case["id"]]
            replaced += 1

    with open(main_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"  Replaced {replaced} / {len(rewritten)} cases in {main_path.name}")
    return replaced


def validate_file(filepath: str):
    """Run quality checks on merged file."""
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    cases = data["cases"]
    issues = []

    # Check context word counts
    for c in cases:
        ctx_words = sum(len(x.split()) for x in c["contexts"])
        if ctx_words < 40:
            issues.append(f"{c['id']}: only {ctx_words} context words")

    # Check query uniqueness
    queries = [c["query"] for c in cases]
    prefixes = [" ".join(q.split()[:6]) for q in queries]
    seen = {}
    for i, p in enumerate(prefixes):
        if p in seen:
            issues.append(f"Duplicate 6-word prefix: '{p}' in {cases[seen[p]]['id']} and {cases[i]['id']}")
        seen[p] = i

    # Check required fields
    for c in cases:
        if "grounding" in filepath:
            if not c.get("forbidden_claims"):
                issues.append(f"{c['id']}: missing forbidden_claims")
        elif "relevance" in filepath:
            if not c.get("required_elements"):
                issues.append(f"{c['id']}: missing required_elements")

    # Check IDs are unique
    ids = [c["id"] for c in cases]
    if len(ids) != len(set(ids)):
        dupes = [x for x in ids if ids.count(x) > 1]
        issues.append(f"Duplicate IDs: {set(dupes)}")

    if issues:
        print(f"\n  ISSUES in {filepath}:")
        for issue in issues[:20]:
            print(f"    - {issue}")
        if len(issues) > 20:
            print(f"    ... and {len(issues) - 20} more")
    else:
        print(f"  {filepath}: ALL CHECKS PASSED")

    # Stats
    ctx_words = [sum(len(x.split()) for x in c["contexts"]) for c in cases]
    ctx_words.sort()
    print(f"  Context words: min={ctx_words[0]} median={ctx_words[len(ctx_words)//2]} max={ctx_words[-1]}")
    print(f"  Total cases: {len(cases)}")

    return len(issues) == 0


def main():
    print("Merging grounding batches...")
    merge_batches("data/tier1_core/grounding.json", "grounding", 4, "t1_grounding_hard_025")

    print("\nMerging relevance batches...")
    merge_batches("data/tier1_core/relevance.json", "relevance", 4, "t1_relevance_hard_024")

    print("\n--- Validation ---")
    g_ok = validate_file("data/tier1_core/grounding.json")
    r_ok = validate_file("data/tier1_core/relevance.json")

    if g_ok and r_ok:
        print("\nAll checks passed! Ready to commit.")
    else:
        print("\nSome issues found. Review above.")


if __name__ == "__main__":
    main()
