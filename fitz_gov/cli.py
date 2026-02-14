# fitz_gov/cli.py
"""
CLI for fitz-gov benchmark.

Commands:
    fitz-gov validate           Validate benchmark data
    fitz-gov stats              Show benchmark statistics
    fitz-gov generate           Generate test cases from corpus
    fitz-gov package            Package data for release
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate and clean benchmark data."""
    from .validate import validate_and_clean

    result = validate_and_clean(
        args.data_dir,
        similarity_threshold=args.threshold,
        dry_run=not args.apply,
    )

    if args.show_issues and result.issues:
        print("\n=== All Issues ===")
        for issue in result.issues:
            print(f"  - {issue}")

    if result.duplicates_removed or result.low_quality_removed:
        return 1 if not args.apply else 0

    print("Validation PASSED - no issues found")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    """Show benchmark statistics."""
    from .loader import Tier, get_tier_info, load_cases, load_tier
    from .models import FitzGovCategory

    data_dir = Path(args.data_dir) if args.data_dir else None

    try:
        all_cases = load_cases(data_dir=data_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1

    print("fitz-gov Benchmark Statistics")
    print("=" * 40)
    print(f"Total cases: {len(all_cases)}")
    print()

    # Get tier info
    tier_info = get_tier_info(data_dir)

    if tier_info:
        # Tiered structure
        print("Tiered Structure:")
        print("-" * 40)

        for tier in Tier:
            if tier.value in tier_info:
                info = tier_info[tier.value]
                tier_label = "Tier 0 (Sanity)" if tier == Tier.SANITY else "Tier 1 (Core)"
                threshold = info.get("passing_threshold")
                threshold_str = f" | Threshold: {threshold:.0%}" if threshold else ""
                print(f"\n{tier_label}: {info['total_cases']} cases{threshold_str}")

                # Show by category
                tier_cases = load_tier(tier, data_dir=data_dir)
                by_category: dict[str, int] = {}
                by_difficulty: dict[str, int] = {}

                for case in tier_cases:
                    cat = case.category.value
                    by_category[cat] = by_category.get(cat, 0) + 1
                    diff = case.difficulty
                    by_difficulty[diff] = by_difficulty.get(diff, 0) + 1

                for cat in FitzGovCategory:
                    count = by_category.get(cat.value, 0)
                    if count > 0:
                        print(f"    {cat.value}: {count}")

                if tier == Tier.CORE and by_difficulty:
                    print(f"  By Difficulty:")
                    for diff in ["medium", "hard"]:
                        if diff in by_difficulty:
                            print(f"    {diff}: {by_difficulty[diff]}")

                if tier == Tier.CORE and args.breakdown:
                    _print_classification_breakdown(tier_cases)

        print()
        print("-" * 40)
        print(f"Combined: {len(all_cases)} cases")

    else:
        # Legacy flat structure
        by_category: dict[str, int] = {}
        by_subcategory: dict[str, dict[str, int]] = {}

        for case in all_cases:
            cat = case.category.value
            by_category[cat] = by_category.get(cat, 0) + 1

            if cat not in by_subcategory:
                by_subcategory[cat] = {}
            subcat = case.subcategory
            by_subcategory[cat][subcat] = by_subcategory[cat].get(subcat, 0) + 1

        print("By Category:")
        for cat in FitzGovCategory:
            count = by_category.get(cat.value, 0)
            print(f"  {cat.value}: {count}")

            # Show subcategories if verbose
            if args.verbose and cat.value in by_subcategory:
                for subcat, subcount in sorted(by_subcategory[cat.value].items()):
                    print(f"    - {subcat}: {subcount}")

    return 0


def _print_classification_breakdown(cases: list) -> None:
    """Print classification attribute distributions for a set of cases."""
    dimensions = [
        ("Domain", "domain"),
        ("Query Type", "query_type"),
        ("Source Type", "source_type"),
        ("Reasoning Type", "reasoning_type"),
        ("Evidence Pattern", "evidence_pattern"),
    ]
    for label, attr in dimensions:
        counts: dict[str, int] = {}
        for case in cases:
            val = getattr(case, attr, "") or "unknown"
            counts[val] = counts.get(val, 0) + 1
        if counts:
            print(f"\n  {label} Distribution:")
            total = sum(counts.values())
            for val, count in sorted(counts.items(), key=lambda x: -x[1]):
                pct = count / total * 100
                print(f"    {val:25s} {count:5d} ({pct:.1f}%)")


def cmd_generate(args: argparse.Namespace) -> int:
    """Generate test cases from corpus."""
    try:
        from .generator import FitzGovGenerator, save_cases
    except ImportError:
        print("Error: Generator requires [generator] extra.")
        print("Install with: pip install fitz-gov[generator]")
        return 1

    corpus_dir = Path(args.corpus)
    if not corpus_dir.exists():
        print(f"Error: Corpus directory not found: {corpus_dir}")
        return 1

    # Load corpus chunks (simple text file loading)
    chunks = []
    for txt_file in corpus_dir.glob("**/*.txt"):
        with open(txt_file, encoding="utf-8") as f:
            text = f.read()
            # Split into chunks of ~500 chars
            for i in range(0, len(text), 500):
                chunk_text = text[i : i + 500]
                if chunk_text.strip():
                    chunks.append({"text": chunk_text, "source": str(txt_file)})

    if not chunks:
        print(f"Error: No text files found in {corpus_dir}")
        return 1

    print(f"Loaded {len(chunks)} chunks from {corpus_dir}")

    # Create LLM client based on args
    llm_client = _create_llm_client(args)
    if not llm_client:
        return 1

    generator = FitzGovGenerator(llm_client=llm_client)

    # Generate cases
    category = args.category
    num_cases = args.num_cases

    if category == "all":
        cases = generator.generate_all(chunks, cases_per_category=num_cases)
    elif category == "abstention":
        cases = generator.generate_abstention_cases(chunks, num_cases)
    elif category == "dispute":
        cases = generator.generate_dispute_cases(chunks, num_cases)
    elif category == "trustworthy_hedged":
        cases = generator.generate_trustworthy_hedged_cases(chunks, num_cases)
    elif category == "trustworthy_direct":
        cases = generator.generate_trustworthy_direct_cases(chunks, num_cases)
    elif category == "grounding":
        cases = generator.generate_grounding_cases(chunks, num_cases)
    elif category == "relevance":
        cases = generator.generate_relevance_cases(chunks, num_cases)
    else:
        print(f"Error: Unknown category: {category}")
        return 1

    # Save cases
    save_cases(cases, args.output)
    print(f"Generated {len(cases)} cases")

    return 0


def cmd_build(args: argparse.Namespace) -> int:
    """Build fitz-gov benchmark from BEIR corpus."""
    try:
        from .bootstrap import bootstrap_from_beir, list_available_datasets
    except ImportError as e:
        print(f"Error: {e}")
        print("Install with: pip install fitz-gov[generator]")
        return 1

    # Show available datasets if requested
    if args.list_datasets:
        datasets = list_available_datasets()
        print("Available BEIR datasets:")
        for name, info in datasets.items():
            print(f"  {name}: {info['description']} ({info['corpus_size']})")
        return 0

    # Create LLM client
    llm_client = _create_llm_client(args)
    if not llm_client:
        return 1

    # Parse datasets
    datasets = args.datasets.split(",") if args.datasets else None

    print("=" * 50)
    print("fitz-gov Benchmark Builder")
    print("=" * 50)

    # Single category mode (for retries)
    if args.category:
        from .generator import FitzGovGenerator
        from pathlib import Path
        import json

        output_path = Path(args.output)
        corpus_file = output_path / "corpus" / "documents.jsonl"

        if not corpus_file.exists():
            print(f"Error: Corpus not found at {corpus_file}")
            print("Run full build first to download corpus.")
            return 1

        print(f"Loading corpus from {corpus_file}...")
        chunks = []
        with open(corpus_file, encoding="utf-8") as f:
            for line in f:
                chunks.append(json.loads(line))
        print(f"Loaded {len(chunks)} documents")

        print(f"\nGenerating {args.category} cases only...")
        generator = FitzGovGenerator(llm_client=llm_client)
        cases = generator.generate_category(
            args.category,
            chunks,
            args.num_cases,
            str(output_path),
        )
        print(f"\nGenerated {len(cases)} {args.category} cases")
        return 0

    result = bootstrap_from_beir(
        datasets=datasets,
        llm_client=llm_client,
        cases_per_category=args.num_cases,
        max_docs_per_dataset=args.max_docs,
        output_dir=args.output,
    )

    print(f"\nBuild complete!")
    print(f"  Corpus: {len(result['corpus'])} documents")
    print(f"  Cases: {len(result['cases'])} test cases")
    print(f"  Output: {args.output}")

    return 0


def cmd_package(args: argparse.Namespace) -> int:
    """Package data for GitHub release."""
    import zipfile

    data_dir = Path(args.data_dir) if args.data_dir else Path(__file__).parent.parent / "data"
    output_file = Path(args.output) if args.output else Path("fitz_gov_data.zip")

    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        return 1

    # Verify expected structure
    expected_dirs = ["corpus", "cases", "queries"]
    missing = [d for d in expected_dirs if not (data_dir / d).exists()]
    if missing:
        print(f"Warning: Missing directories: {missing}")
        print("Run 'fitz-gov bootstrap' first to generate data.")

    # Create zip file
    file_count = 0
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in data_dir.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith("."):
                # Archive path: data/corpus/..., data/cases/..., etc.
                arcname = Path("data") / file_path.relative_to(data_dir)
                zf.write(file_path, arcname)
                file_count += 1

    print(f"Packaged {file_count} files into: {output_file}")

    # Show structure
    print("\nPackage structure:")
    print("  data/")
    print("    corpus/documents.jsonl    # Full corpus for Mode B")
    print("    corpus/manifest.json      # Corpus metadata")
    print("    cases/<category>/*.json   # Test cases for Mode A")
    print("    queries/all_queries.jsonl # Queries for Mode B")

    return 0


def _create_llm_client(args: argparse.Namespace):
    """Create LLM client based on args. Uses direct HTTP - no SDK packages needed."""
    import os

    import requests

    provider = args.llm_provider

    if provider == "ollama":
        base_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        model = args.llm_model or "llama3.1"

        class OllamaClient:
            def complete(self, prompt: str) -> str:
                resp = requests.post(
                    f"{base_url}/api/generate",
                    json={"model": model, "prompt": prompt, "stream": False},
                    timeout=1800,  # 30 min - local LLMs can be slow
                )
                resp.raise_for_status()
                return resp.json().get("response", "")

        # Test connection
        try:
            requests.get(f"{base_url}/api/tags", timeout=5)
            print(f"Using Ollama ({model}) at {base_url}")
            return OllamaClient()
        except requests.exceptions.ConnectionError:
            print(f"Error: Cannot connect to Ollama at {base_url}")
            print("Make sure Ollama is running: ollama serve")
            return None

    elif provider == "cohere":
        api_key = os.environ.get("COHERE_API_KEY")
        if not api_key:
            print("Error: COHERE_API_KEY not set")
            return None

        model = args.llm_model or "command-r-08-2024"

        class CohereClient:
            def complete(self, prompt: str) -> str:
                resp = requests.post(
                    "https://api.cohere.com/v1/chat",
                    headers={
                        "Authorization": f"bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={"model": model, "message": prompt},
                    timeout=600,  # 10 min for complex prompts
                )
                resp.raise_for_status()
                return resp.json().get("text", "")

        print(f"Using Cohere ({model})")
        return CohereClient()

    elif provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("Error: OPENAI_API_KEY not set")
            return None

        model = args.llm_model or "gpt-4o"

        class OpenAIClient:
            def complete(self, prompt: str) -> str:
                resp = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                    timeout=120,
                )
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"]

        print(f"Using OpenAI ({model})")
        return OpenAIClient()

    elif provider == "anthropic":
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("Error: ANTHROPIC_API_KEY not set")
            return None

        model = args.llm_model or "claude-sonnet-4-20250514"

        class AnthropicClient:
            def complete(self, prompt: str) -> str:
                resp = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": api_key,
                        "Content-Type": "application/json",
                        "anthropic-version": "2023-06-01",
                    },
                    json={
                        "model": model,
                        "max_tokens": 4096,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                    timeout=120,
                )
                resp.raise_for_status()
                return resp.json()["content"][0]["text"]

        print(f"Using Anthropic ({model})")
        return AnthropicClient()

    else:
        print(f"Error: Unknown LLM provider: {provider}")
        print("Available: ollama, cohere, openai, anthropic")
        return None


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="fitz-gov",
        description="fitz-gov: Comprehensive RAG Governance Benchmark",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate and clean benchmark data")
    validate_parser.add_argument("--data-dir", default="./data", help="Data directory to validate")
    validate_parser.add_argument("--threshold", type=float, default=0.9, help="Similarity threshold for duplicates")
    validate_parser.add_argument("--apply", action="store_true", help="Apply changes (remove duplicates/low quality)")
    validate_parser.add_argument("--show-issues", action="store_true", help="Show all issues found")

    # stats command
    stats_parser = subparsers.add_parser("stats", help="Show benchmark statistics")
    stats_parser.add_argument("--data-dir", help="Data directory")
    stats_parser.add_argument("-v", "--verbose", action="store_true", help="Show subcategory breakdown")
    stats_parser.add_argument("--breakdown", action="store_true", help="Show classification attribute distributions")

    # generate command
    gen_parser = subparsers.add_parser("generate", help="Generate test cases from corpus")
    gen_parser.add_argument("category", choices=["all", "abstention", "dispute", "trustworthy_hedged", "trustworthy_direct", "grounding", "relevance"], help="Category to generate")
    gen_parser.add_argument("--corpus", required=True, help="Directory containing corpus text files")
    gen_parser.add_argument("--output", default="./generated_data", help="Output directory")
    gen_parser.add_argument("--num-cases", type=int, default=20, help="Cases per category")
    gen_parser.add_argument("--llm-provider", choices=["openai", "anthropic"], default="openai", help="LLM provider")
    gen_parser.add_argument("--llm-model", help="LLM model name")

    # build command (was "bootstrap")
    build_parser = subparsers.add_parser("build", help="Build benchmark from BEIR corpus")
    build_parser.add_argument("--datasets", help="Comma-separated BEIR datasets (default: scifact,nfcorpus,fiqa)")
    build_parser.add_argument("--list-datasets", action="store_true", help="List available datasets")
    build_parser.add_argument("--output", default="./data", help="Output directory")
    build_parser.add_argument("--num-cases", type=int, default=30, help="Cases per category")
    build_parser.add_argument("--max-docs", type=int, default=None, help="Max docs per dataset (default: all)")
    build_parser.add_argument(
        "--llm-provider",
        choices=["ollama", "cohere", "openai", "anthropic"],
        default="ollama",
        help="LLM provider (default: ollama for free local generation)",
    )
    build_parser.add_argument("--llm-model", help="LLM model name (default depends on provider)")
    build_parser.add_argument(
        "--category",
        choices=["abstention", "dispute", "trustworthy_hedged", "trustworthy_direct", "grounding", "relevance"],
        help="Generate only this category (for retries)",
    )

    # package command
    pkg_parser = subparsers.add_parser("package", help="Package data for release")
    pkg_parser.add_argument("--data-dir", help="Data directory to package")
    pkg_parser.add_argument("--output", default="fitz_gov_data.zip", help="Output zip file")

    args = parser.parse_args()

    if args.command == "validate":
        return cmd_validate(args)
    elif args.command == "stats":
        return cmd_stats(args)
    elif args.command == "generate":
        return cmd_generate(args)
    elif args.command == "build":
        return cmd_build(args)
    elif args.command == "package":
        return cmd_package(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
