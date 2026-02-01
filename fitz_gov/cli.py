# fitz_gov/cli.py
"""
CLI for FITZ-GOV benchmark.

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
    """Validate benchmark data."""
    from .loader import load_cases, validate_cases

    data_dir = Path(args.data_dir) if args.data_dir else None

    try:
        cases = load_cases(data_dir=data_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1

    errors = validate_cases(cases)

    if errors:
        print(f"Validation FAILED with {len(errors)} errors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"Validation PASSED: {len(cases)} cases are valid")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    """Show benchmark statistics."""
    from .loader import load_cases
    from .schema import FitzGovCategory

    data_dir = Path(args.data_dir) if args.data_dir else None

    try:
        cases = load_cases(data_dir=data_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1

    print(f"FITZ-GOV Benchmark Statistics")
    print("=" * 40)
    print(f"Total cases: {len(cases)}")
    print()

    # Count by category
    by_category: dict[str, int] = {}
    by_subcategory: dict[str, dict[str, int]] = {}

    for case in cases:
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

        # Show subcategories
        if cat.value in by_subcategory:
            for subcat, subcount in by_subcategory[cat.value].items():
                print(f"    - {subcat}: {subcount}")

    return 0


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
    elif category == "qualification":
        cases = generator.generate_qualification_cases(chunks, num_cases)
    elif category == "confidence":
        cases = generator.generate_confidence_cases(chunks, num_cases)
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


def cmd_package(args: argparse.Namespace) -> int:
    """Package data for GitHub release."""
    import shutil
    import zipfile

    data_dir = Path(args.data_dir) if args.data_dir else Path(__file__).parent.parent / "data"
    output_file = Path(args.output) if args.output else Path("fitz_gov_data.zip")

    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        return 1

    # Create zip file
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in data_dir.rglob("*.json"):
            arcname = file_path.relative_to(data_dir.parent)
            zf.write(file_path, arcname)
            print(f"  Added: {arcname}")

    print(f"Created: {output_file}")
    return 0


def _create_llm_client(args: argparse.Namespace):
    """Create LLM client based on args."""
    import os

    provider = args.llm_provider

    if provider == "openai":
        try:
            from openai import OpenAI

            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

            class OpenAIWrapper:
                def complete(self, prompt: str) -> str:
                    response = client.chat.completions.create(
                        model=args.llm_model or "gpt-4o",
                        messages=[{"role": "user", "content": prompt}],
                    )
                    return response.choices[0].message.content or ""

            return OpenAIWrapper()
        except ImportError:
            print("Error: openai package not installed")
            return None

    elif provider == "anthropic":
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

            class AnthropicWrapper:
                def complete(self, prompt: str) -> str:
                    response = client.messages.create(
                        model=args.llm_model or "claude-sonnet-4-20250514",
                        max_tokens=4096,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    return response.content[0].text

            return AnthropicWrapper()
        except ImportError:
            print("Error: anthropic package not installed")
            return None

    else:
        print(f"Error: Unknown LLM provider: {provider}")
        return None


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="fitz-gov",
        description="FITZ-GOV: Comprehensive RAG Governance Benchmark",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate benchmark data")
    validate_parser.add_argument("--data-dir", help="Data directory to validate")

    # stats command
    stats_parser = subparsers.add_parser("stats", help="Show benchmark statistics")
    stats_parser.add_argument("--data-dir", help="Data directory")

    # generate command
    gen_parser = subparsers.add_parser("generate", help="Generate test cases from corpus")
    gen_parser.add_argument("category", choices=["all", "abstention", "dispute", "qualification", "confidence", "grounding", "relevance"], help="Category to generate")
    gen_parser.add_argument("--corpus", required=True, help="Directory containing corpus text files")
    gen_parser.add_argument("--output", default="./generated_data", help="Output directory")
    gen_parser.add_argument("--num-cases", type=int, default=20, help="Cases per category")
    gen_parser.add_argument("--llm-provider", choices=["openai", "anthropic"], default="openai", help="LLM provider")
    gen_parser.add_argument("--llm-model", help="LLM model name")

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
    elif args.command == "package":
        return cmd_package(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
