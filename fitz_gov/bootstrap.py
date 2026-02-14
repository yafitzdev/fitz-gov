# fitz_gov/bootstrap.py
"""
Bootstrap fitz-gov benchmark data from BEIR corpus.

Downloads BEIR dataset(s), extracts corpus documents, and generates
governance test cases using the synthetic generator.

Usage:
    from fitz_gov.bootstrap import bootstrap_from_beir

    # Generate from SciFact corpus
    cases = bootstrap_from_beir(
        datasets=["scifact"],
        llm_client=your_client,
        cases_per_category=50,
    )
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .generator import LLMClient

# BEIR datasets and their characteristics
BEIR_DATASETS = {
    # Small, good for testing
    "scifact": {
        "description": "Scientific fact verification",
        "corpus_size": "~5K docs",
        "domain": "scientific",
    },
    "nfcorpus": {
        "description": "Nutrition and medical",
        "corpus_size": "~3.6K docs",
        "domain": "medical",
    },
    "fiqa": {
        "description": "Financial opinion QA",
        "corpus_size": "~57K docs",
        "domain": "financial",
    },
    # Medium
    "hotpotqa": {
        "description": "Multi-hop reasoning (Wikipedia)",
        "corpus_size": "~5.2M docs",
        "domain": "general",
    },
    "fever": {
        "description": "Fact extraction and verification",
        "corpus_size": "~5.4M docs",
        "domain": "general",
    },
    # Large
    "msmarco": {
        "description": "Web search passages",
        "corpus_size": "~8.8M docs",
        "domain": "general",
    },
    "nq": {
        "description": "Natural Questions (Wikipedia)",
        "corpus_size": "~2.6M docs",
        "domain": "general",
    },
}

# Recommended for bootstrapping (small, diverse)
RECOMMENDED_DATASETS = ["scifact", "nfcorpus", "fiqa"]


def download_beir_corpus(
    dataset: str,
    data_dir: Path | str | None = None,
) -> Path:
    """
    Download BEIR dataset corpus.

    Args:
        dataset: BEIR dataset name (e.g., "scifact")
        data_dir: Directory to store data. Defaults to ~/.fitz/beir_data/

    Returns:
        Path to corpus directory
    """
    try:
        from beir import util
        from beir.datasets.data_loader import GenericDataLoader
    except ImportError:
        raise ImportError(
            "BEIR package required for bootstrapping. "
            "Install with: pip install beir"
        )

    if data_dir is None:
        data_dir = Path.home() / ".fitz" / "beir_data"
    else:
        data_dir = Path(data_dir)

    data_dir.mkdir(parents=True, exist_ok=True)

    # Download dataset
    url = f"https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{dataset}.zip"
    dataset_path = util.download_and_unzip(url, str(data_dir))

    return Path(dataset_path)


def load_beir_corpus(
    dataset_path: Path,
    max_docs: int | None = None,
) -> list[dict[str, Any]]:
    """
    Load corpus documents from BEIR dataset.

    Args:
        dataset_path: Path to downloaded BEIR dataset
        max_docs: Maximum number of documents to load (for testing)

    Returns:
        List of document dicts with 'text', 'title', 'id' keys
    """
    try:
        from beir.datasets.data_loader import GenericDataLoader
    except ImportError:
        raise ImportError("BEIR package required. Install with: pip install beir")

    # Load corpus
    corpus, _, _ = GenericDataLoader(str(dataset_path)).load(split="test")

    docs = []
    for doc_id, doc_data in corpus.items():
        text = doc_data.get("text", "")
        title = doc_data.get("title", "")

        # Combine title and text
        full_text = f"{title}\n\n{text}" if title else text

        if full_text.strip():
            docs.append({
                "id": doc_id,
                "text": full_text,
                "title": title,
                "source": f"beir:{dataset_path.name}",
            })

        if max_docs and len(docs) >= max_docs:
            break

    return docs


def bootstrap_from_beir(
    datasets: list[str] | None = None,
    llm_client: "LLMClient" = None,
    cases_per_category: int = 30,
    max_docs_per_dataset: int | None = None,
    data_dir: Path | str | None = None,
    output_dir: Path | str | None = None,
) -> dict[str, Any]:
    """
    Bootstrap fitz-gov benchmark from BEIR corpus.

    Produces:
    - corpus/: Full document corpus for Mode B (full pipeline evaluation)
    - cases/: Test cases with injected contexts for Mode A
    - queries/: Query + expected_mode pairs for Mode B

    Args:
        datasets: BEIR datasets to use. Defaults to recommended set.
        llm_client: LLM client for generation.
        cases_per_category: Number of cases per governance category.
        max_docs_per_dataset: Max docs to sample from each dataset. None = all docs.
        data_dir: Directory for BEIR data cache.
        output_dir: Directory to save generated benchmark.

    Returns:
        Dict with 'corpus', 'cases', 'queries' lists.
    """
    from .generator import FitzGovGenerator

    if llm_client is None:
        raise ValueError("llm_client is required for generation")

    datasets = datasets or RECOMMENDED_DATASETS
    output_path = Path(output_dir) if output_dir else Path("./data")

    # Collect corpus documents from all datasets
    all_docs = []
    for dataset in datasets:
        print(f"Downloading BEIR dataset: {dataset}...")
        dataset_path = download_beir_corpus(dataset, data_dir)

        print(f"Loading corpus from {dataset}...")
        docs = load_beir_corpus(dataset_path, max_docs=max_docs_per_dataset)
        all_docs.extend(docs)
        print(f"  Loaded {len(docs)} documents from {dataset}")

    print(f"\nTotal corpus: {len(all_docs)} documents")

    # Save corpus for Mode B
    save_corpus(all_docs, output_path / "corpus", datasets)

    # Convert to chunk-like format for generator
    chunks = [{"text": doc["text"], "source": doc["source"], "id": doc["id"]} for doc in all_docs]

    # Generate cases (saves incrementally per category)
    print(f"\nGenerating fitz-gov cases ({cases_per_category} per category)...", flush=True)
    generator = FitzGovGenerator(llm_client=llm_client)
    cases = generator.generate_all(
        chunks,
        cases_per_category=cases_per_category,
        output_dir=str(output_path),  # Save incrementally
    )

    print(f"\nGenerated {len(cases)} total cases", flush=True)

    # Save cases (Mode A) and queries (Mode B)
    save_cases_and_queries(cases, output_path)

    return {
        "corpus": all_docs,
        "cases": cases,
        "datasets": datasets,
    }


def save_corpus(
    docs: list[dict[str, Any]],
    output_dir: Path,
    datasets: list[str],
) -> None:
    """Save corpus documents for Mode B evaluation."""
    import json
    from datetime import datetime, timezone

    output_dir.mkdir(parents=True, exist_ok=True)

    # Save documents as JSONL
    docs_file = output_dir / "documents.jsonl"
    with open(docs_file, "w", encoding="utf-8") as f:
        for doc in docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    print(f"Saved {len(docs)} documents to {docs_file}")

    # Save manifest
    manifest = {
        "version": "1.0.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_datasets": datasets,
        "document_count": len(docs),
        "description": "fitz-gov evaluation corpus derived from BEIR datasets",
    }
    manifest_file = output_dir / "manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Saved manifest to {manifest_file}")


def save_cases_and_queries(cases: list, output_dir: Path) -> None:
    """Save test cases (Mode A) and queries (Mode B)."""
    import json

    from .models import FitzGovCategory

    # Save cases organized by category (Mode A)
    cases_dir = output_dir / "cases"
    by_category: dict[str, list] = {}

    for case in cases:
        cat = case.category.value
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(case)

    for cat, cat_cases in by_category.items():
        cat_dir = cases_dir / cat
        cat_dir.mkdir(parents=True, exist_ok=True)

        # Group by subcategory
        by_subcat: dict[str, list] = {}
        for case in cat_cases:
            subcat = case.subcategory
            if subcat not in by_subcat:
                by_subcat[subcat] = []
            by_subcat[subcat].append(case)

        for subcat, subcat_cases in by_subcat.items():
            output_file = cat_dir / f"{subcat}.json"
            data = {
                "category": cat,
                "subcategory": subcat,
                "description": f"fitz-gov {cat} cases - {subcat}",
                "cases": [c.to_dict() for c in subcat_cases],
            }
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(cases)} cases to {cases_dir}")

    # Save queries for Mode B (query + expected + relevant_doc_ids, no contexts)
    queries_dir = output_dir / "queries"
    queries_dir.mkdir(parents=True, exist_ok=True)

    queries_file = queries_dir / "all_queries.jsonl"
    with open(queries_file, "w", encoding="utf-8") as f:
        for case in cases:
            query_record = {
                "id": case.id,
                "query": case.query,
                "category": case.category.value,
                "subcategory": case.subcategory,
                "expected_mode": case.expected_mode.value,
                "description": case.description,
                "rationale": case.rationale,
            }
            # Include answer quality fields if present
            if case.forbidden_claims:
                query_record["forbidden_claims"] = case.forbidden_claims
            if case.required_elements:
                query_record["required_elements"] = case.required_elements
            # Include relevant doc IDs for Mode B retrieval evaluation
            if case.relevant_doc_ids:
                query_record["relevant_doc_ids"] = case.relevant_doc_ids

            f.write(json.dumps(query_record, ensure_ascii=False) + "\n")

    print(f"Saved {len(cases)} queries to {queries_file}")


def list_available_datasets() -> dict[str, dict]:
    """List available BEIR datasets for bootstrapping."""
    return BEIR_DATASETS


def get_recommended_datasets() -> list[str]:
    """Get recommended datasets for bootstrapping."""
    return RECOMMENDED_DATASETS.copy()
