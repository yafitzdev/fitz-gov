# fitz_gov/bootstrap.py
"""
Bootstrap FITZ-GOV benchmark data from BEIR corpus.

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
    max_docs_per_dataset: int = 500,
    data_dir: Path | str | None = None,
    output_dir: Path | str | None = None,
) -> list:
    """
    Bootstrap FITZ-GOV benchmark from BEIR corpus.

    Args:
        datasets: BEIR datasets to use. Defaults to recommended set.
        llm_client: LLM client for generation.
        cases_per_category: Number of cases per governance category.
        max_docs_per_dataset: Max docs to sample from each dataset.
        data_dir: Directory for BEIR data cache.
        output_dir: Directory to save generated cases.

    Returns:
        List of generated FitzGovCase objects.
    """
    from .generator import FitzGovGenerator, save_cases

    if llm_client is None:
        raise ValueError("llm_client is required for generation")

    datasets = datasets or RECOMMENDED_DATASETS

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

    # Convert to chunk-like format for generator
    chunks = [{"text": doc["text"], "source": doc["source"]} for doc in all_docs]

    # Generate cases
    print(f"\nGenerating FITZ-GOV cases ({cases_per_category} per category)...")
    generator = FitzGovGenerator(llm_client=llm_client)
    cases = generator.generate_all(chunks, cases_per_category=cases_per_category)

    print(f"Generated {len(cases)} total cases")

    # Save if output_dir specified
    if output_dir:
        save_cases(cases, output_dir)

    return cases


def list_available_datasets() -> dict[str, dict]:
    """List available BEIR datasets for bootstrapping."""
    return BEIR_DATASETS


def get_recommended_datasets() -> list[str]:
    """Get recommended datasets for bootstrapping."""
    return RECOMMENDED_DATASETS.copy()
