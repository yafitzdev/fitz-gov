# fitz_gov/validate.py
"""
Validate and clean fitz-gov benchmark data.

1. Semantic deduplication (similar queries)
2. Quality checks (missing fields, wrong modes)
3. Format validation
"""

from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ValidationResult:
    total_cases: int
    duplicates_removed: int
    low_quality_removed: int
    final_cases: int
    issues: list[str]


def load_all_cases(data_dir: Path) -> list[dict]:
    """Load all cases from data directory (supports both legacy and tiered structure)."""
    cases = []

    # Try tiered structure first
    tier_dirs = [data_dir / "tier0_sanity", data_dir / "tier1_core"]
    found_tiered = any(d.exists() for d in tier_dirs)

    if found_tiered:
        for tier_dir in tier_dirs:
            if not tier_dir.exists():
                continue
            for json_file in tier_dir.glob("*.json"):
                with open(json_file, encoding="utf-8") as f:
                    data = json.load(f)
                    for case in data.get("cases", []):
                        case["_source_file"] = str(json_file)
                        cases.append(case)
    else:
        # Legacy flat structure
        cases_dir = data_dir / "cases"
        if cases_dir.exists():
            for cat_dir in cases_dir.iterdir():
                if cat_dir.is_dir():
                    for json_file in cat_dir.glob("*.json"):
                        with open(json_file, encoding="utf-8") as f:
                            data = json.load(f)
                            for case in data.get("cases", []):
                                case["_source_file"] = str(json_file)
                                cases.append(case)

    return cases


def find_semantic_duplicates(
    cases: list[dict],
    similarity_threshold: float = 0.9,
) -> list[tuple[int, int, float]]:
    """Find semantically similar queries using embeddings."""
    try:
        import requests

        # Use Ollama for embeddings
        def get_embedding(text: str) -> list[float]:
            resp = requests.post(
                "http://localhost:11434/api/embeddings",
                json={"model": "nomic-embed-text", "prompt": text},
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()["embedding"]

        print("Computing embeddings for duplicate detection...")
        embeddings = []
        for i, case in enumerate(cases):
            emb = get_embedding(case["query"])
            embeddings.append(emb)
            if (i + 1) % 20 == 0:
                print(f"  {i + 1}/{len(cases)} embeddings computed")

        # Find similar pairs
        duplicates = []
        for i in range(len(cases)):
            for j in range(i + 1, len(cases)):
                sim = cosine_similarity(embeddings[i], embeddings[j])
                if sim >= similarity_threshold:
                    duplicates.append((i, j, sim))

        return duplicates

    except Exception as e:
        print(f"Warning: Could not compute embeddings: {e}")
        print("Falling back to exact match detection only")
        return find_exact_duplicates(cases)


def find_exact_duplicates(cases: list[dict]) -> list[tuple[int, int, float]]:
    """Find exact duplicate queries."""
    duplicates = []
    seen = {}

    for i, case in enumerate(cases):
        query_lower = case["query"].lower().strip()
        if query_lower in seen:
            duplicates.append((seen[query_lower], i, 1.0))
        else:
            seen[query_lower] = i

    return duplicates


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def check_quality(case: dict) -> list[str]:
    """Check a single case for quality issues."""
    issues = []

    # Required fields
    required = ["id", "query", "contexts", "expected_mode", "description", "rationale"]
    for field in required:
        if field not in case or not case[field]:
            issues.append(f"Missing or empty field: {field}")

    # Query length
    query = case.get("query", "")
    if len(query) < 10:
        issues.append(f"Query too short: {len(query)} chars")
    if len(query) > 500:
        issues.append(f"Query too long: {len(query)} chars")

    # Contexts
    contexts = case.get("contexts", [])
    if not contexts:
        issues.append("No contexts provided")
    elif len(contexts) > 10:
        issues.append(f"Too many contexts: {len(contexts)}")

    # Valid expected_mode
    valid_modes = ["trustworthy", "disputed", "abstain"]
    mode = case.get("expected_mode", "")
    if mode not in valid_modes:
        issues.append(f"Invalid expected_mode: {mode}")

    # context_sources validation
    context_sources = case.get("context_sources", [])
    if context_sources:
        contexts = case.get("contexts", [])
        if len(context_sources) != len(contexts):
            issues.append(
                f"context_sources length ({len(context_sources)}) != contexts length ({len(contexts)})"
            )
        valid_authorities = {"primary", "secondary", "tertiary", "official", "expert", "community"}
        valid_source_types = {"academic", "news", "government", "industry", "blog", "reference", "report"}
        for i, src in enumerate(context_sources):
            if "source_id" not in src:
                issues.append(f"context_sources[{i}] missing source_id")
            if "source_type" not in src:
                issues.append(f"context_sources[{i}] missing source_type")
            elif src["source_type"] not in valid_source_types:
                issues.append(f"context_sources[{i}] invalid source_type: {src['source_type']}")
            if "authority" not in src:
                issues.append(f"context_sources[{i}] missing authority")
            elif src["authority"] not in valid_authorities:
                issues.append(f"context_sources[{i}] invalid authority: {src['authority']}")

    # Category-specific checks: trustworthy cases with quality subcategories
    subcategory = case.get("subcategory", "")

    if subcategory.startswith("grounding_"):
        if not case.get("forbidden_claims"):
            issues.append("Grounding subcategory case missing forbidden_claims")

    if subcategory.startswith("relevance_"):
        if not case.get("required_elements"):
            issues.append("Relevance subcategory case missing required_elements")

    return issues


def validate_and_clean(
    data_dir: Path | str,
    similarity_threshold: float = 0.9,
    dry_run: bool = True,
) -> ValidationResult:
    """
    Validate and clean benchmark data.

    Args:
        data_dir: Path to data directory
        similarity_threshold: Threshold for semantic similarity (0.9 = 90% similar)
        dry_run: If True, don't modify files, just report issues

    Returns:
        ValidationResult with statistics
    """
    data_dir = Path(data_dir)
    cases = load_all_cases(data_dir)
    total = len(cases)
    issues = []

    print(f"Loaded {total} cases")

    # 1. Find duplicates
    print("\n1. Checking for duplicates...")
    duplicates = find_semantic_duplicates(cases, similarity_threshold)

    duplicate_indices = set()
    for i, j, sim in duplicates:
        issues.append(f"Duplicate: '{cases[i]['query'][:50]}...' ≈ '{cases[j]['query'][:50]}...' (sim={sim:.2f})")
        duplicate_indices.add(j)  # Remove the second one

    print(f"   Found {len(duplicates)} duplicate pairs")

    # 2. Quality checks
    print("\n2. Checking quality...")
    low_quality_indices = set()

    for i, case in enumerate(cases):
        case_issues = check_quality(case)
        if case_issues:
            issues.append(f"Quality issues in {case['id']}: {case_issues}")
            low_quality_indices.add(i)

    print(f"   Found {len(low_quality_indices)} cases with quality issues")

    # 3. Compute final set
    remove_indices = duplicate_indices | low_quality_indices
    clean_cases = [c for i, c in enumerate(cases) if i not in remove_indices]

    result = ValidationResult(
        total_cases=total,
        duplicates_removed=len(duplicate_indices),
        low_quality_removed=len(low_quality_indices - duplicate_indices),
        final_cases=len(clean_cases),
        issues=issues,
    )

    print(f"\n=== Summary ===")
    print(f"Total cases: {result.total_cases}")
    print(f"Duplicates removed: {result.duplicates_removed}")
    print(f"Low quality removed: {result.low_quality_removed}")
    print(f"Final cases: {result.final_cases}")

    if not dry_run and remove_indices:
        print("\nSaving cleaned data...")
        save_clean_cases(data_dir, cases, remove_indices)
        print("Done!")
    elif remove_indices:
        print("\nDry run - no files modified. Run with --apply to save changes.")

    return result


def save_clean_cases(data_dir: Path, cases: list[dict], remove_indices: set[int]) -> None:
    """Save cleaned cases back to files."""
    # Group by source file
    by_file: dict[str, list[dict]] = {}

    for i, case in enumerate(cases):
        if i in remove_indices:
            continue

        source = case.pop("_source_file", None)
        if source:
            if source not in by_file:
                by_file[source] = []
            by_file[source].append(case)

    # Write back
    for filepath, file_cases in by_file.items():
        path = Path(filepath)

        # Load original to preserve metadata
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        data["cases"] = file_cases

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"  Saved {len(file_cases)} cases to {path.name}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Validate fitz-gov benchmark data")
    parser.add_argument("--data-dir", default="./data", help="Data directory")
    parser.add_argument("--threshold", type=float, default=0.9, help="Similarity threshold")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry run)")
    parser.add_argument("--show-issues", action="store_true", help="Show all issues")

    args = parser.parse_args()

    result = validate_and_clean(
        args.data_dir,
        similarity_threshold=args.threshold,
        dry_run=not args.apply,
    )

    if args.show_issues and result.issues:
        print("\n=== All Issues ===")
        for issue in result.issues:
            print(f"  - {issue}")


if __name__ == "__main__":
    main()
