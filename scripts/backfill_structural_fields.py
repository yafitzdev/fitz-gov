#!/usr/bin/env python3
"""Backfill category and evaluation_config on all tier0 and tier1 cases."""

import json
import re
from pathlib import Path


def compute_allowed_phrases(case):
    """Find forbidden_claims patterns that match content already in contexts."""
    allowed = []
    contexts_text = " ".join(case.get("contexts", []))
    for pattern in case.get("forbidden_claims", []):
        try:
            matches = re.findall(pattern, contexts_text, re.IGNORECASE)
            if matches:
                for m in matches:
                    phrase = m if isinstance(m, str) else m[0] if isinstance(m, tuple) else str(m)
                    if phrase:
                        allowed.append(phrase)
        except re.error:
            pass
    return sorted(set(allowed))


def backfill_file(filepath, category):
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    updated = 0
    for case in data["cases"]:
        changed = False

        # Backfill category
        if case.get("category") != category:
            case["category"] = category
            changed = True

        # Backfill evaluation_config
        if "evaluation_config" not in case:
            if category == "grounding":
                allowed = compute_allowed_phrases(case)
                case["evaluation_config"] = {
                    "mode": "answer_quality",
                    "use_regex": True,
                    "case_insensitive": True,
                    "allowed_phrases": allowed,
                }
            elif category == "relevance":
                case["evaluation_config"] = {
                    "mode": "answer_quality",
                    "use_regex": False,
                    "case_insensitive": True,
                    "min_required": 1,
                }
            else:
                case["evaluation_config"] = {
                    "mode": "governance",
                    "check_mode_match": True,
                }
            changed = True

        if changed:
            updated += 1

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return updated, len(data["cases"])


def main():
    total_updated = 0
    total_cases = 0
    for tier_dir in ["tier0_sanity", "tier1_core"]:
        tier_path = Path(f"data/{tier_dir}")
        if not tier_path.exists():
            continue
        for filepath in sorted(tier_path.glob("*.json")):
            category = filepath.stem
            updated, count = backfill_file(filepath, category)
            total_updated += updated
            total_cases += count
            print(f"  {tier_dir}/{filepath.name}: {updated}/{count} updated")

    print(f"\nTotal: {total_updated}/{total_cases} cases updated")

    # Verify
    missing_cat = 0
    missing_eval = 0
    for tier_dir in ["tier0_sanity", "tier1_core"]:
        tier_path = Path(f"data/{tier_dir}")
        if not tier_path.exists():
            continue
        for filepath in sorted(tier_path.glob("*.json")):
            data = json.load(open(filepath, encoding="utf-8"))
            for c in data["cases"]:
                if not c.get("category"):
                    missing_cat += 1
                if not c.get("evaluation_config"):
                    missing_eval += 1

    print(f"\nVerification:")
    print(f"  Missing category: {missing_cat}")
    print(f"  Missing evaluation_config: {missing_eval}")


if __name__ == "__main__":
    main()
