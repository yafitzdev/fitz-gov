#!/usr/bin/env python3
"""
Phase 6: Corpus Document Generation and Validation for fitz-gov 4.0

This script handles three tasks:
1. Generate new corpus documents for newly added/converted tier1_core cases
2. Update query mappings for the new cases
3. Update the corpus manifest with new counts

New case ID ranges:
  - Dispute:           t1_dispute_hard_568  .. t1_dispute_hard_717   (150 cases)
  - Abstention:        t1_abstain_hard_951  .. t1_abstain_hard_1100  (150 cases)
  - Trustworthy direct: t1_confident_hard_901 .. t1_confident_hard_915 (15 cases)
  - Trustworthy hedged: t1_qualify_hard_915  .. t1_qualify_hard_929   (15 cases)

Idempotent: uses deterministic document IDs derived from case IDs so re-runs
detect already-added documents and skip them.
"""

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

# --------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------- #
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CORPUS_DIR = DATA_DIR / "corpus"
DOCUMENTS_PATH = CORPUS_DIR / "documents.jsonl"
MANIFEST_PATH = CORPUS_DIR / "manifest.json"
QUERY_MAPPINGS_PATH = DATA_DIR / "queries" / "query_mappings.json"
TIER1_DIR = DATA_DIR / "tier1_core"

# --------------------------------------------------------------------- #
# New case ID ranges
# --------------------------------------------------------------------- #
NEW_CASE_RANGES: dict[str, dict[str, Any]] = {
    "dispute": {
        "file": "dispute.json",
        "prefix": "t1_dispute_hard_",
        "range": range(568, 718),
        "category_key": "dispute",
        "doc_prefix": "dispute",
    },
    "abstention": {
        "file": "abstention.json",
        "prefix": "t1_abstain_hard_",
        "range": range(951, 1101),
        "category_key": "abstention",
        "doc_prefix": "abstain",
    },
    "trustworthy_direct": {
        "file": "trustworthy_direct.json",
        "prefix": "t1_confident_hard_",
        "range": range(901, 916),
        "category_key": "trustworthy_direct",
        "doc_prefix": "direct",
    },
    "trustworthy_hedged": {
        "file": "trustworthy_hedged.json",
        "prefix": "t1_qualify_hard_",
        "range": range(915, 930),
        "category_key": "trustworthy_hedged",
        "doc_prefix": "hedged",
    },
}


# --------------------------------------------------------------------- #
# Deterministic document ID generation
# --------------------------------------------------------------------- #

def case_id_to_doc_id(case_id: str, doc_prefix: str, source_idx: int | None = None) -> str:
    """
    Generate a deterministic document ID from a case ID.

    Examples:
        t1_dispute_hard_568  -> dispute_doc_568
        t1_abstain_hard_951  -> abstain_doc_951
        t1_confident_hard_901 (source 0) -> direct_doc_901a
        t1_confident_hard_901 (source 1) -> direct_doc_901b
    """
    # Extract the numeric suffix from the case ID
    num = case_id.rsplit("_", 1)[-1]
    if source_idx is not None:
        suffix = chr(ord("a") + source_idx)
        return f"{doc_prefix}_doc_{num}{suffix}"
    return f"{doc_prefix}_doc_{num}"


# --------------------------------------------------------------------- #
# Domain inference
# --------------------------------------------------------------------- #
DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "biology": [
        "cell", "dna", "gene", "protein", "organism", "species", "evolution",
        "mitochondri", "chloroplast", "enzyme", "bacteria", "virus", "genome",
        "coral", "marine", "isopod", "tubeworm", "invertebrate",
    ],
    "medical": [
        "patient", "hospital", "surgery", "treatment", "diagnosis", "clinical",
        "symptom", "drug", "therapy", "dosage", "physician", "disease", "cancer",
        "tumor", "chemotherapy", "transplant", "anesthesia", "radiology",
    ],
    "pharmaceutical": [
        "fda", "pharmaceutical", "medication", "prescription", "trial", "dosing",
        "pharmacokinetic", "bioavailability", "compound", "veralixib",
        "arthritis", "rheumatoid",
    ],
    "health": [
        "health", "nutrition", "diet", "exercise", "wellness", "fitness",
        "obesity", "vitamin", "hydration", "water intake", "mental health",
        "sleep", "stress", "immune", "microplastic", "contamination",
    ],
    "technology": [
        "software", "algorithm", "cloud", "server", "database", "api",
        "kubernetes", "docker", "deployment", "machine learning", "ai ",
        "artificial intelligence", "neural network", "computing", "data center",
        "cybersecurity", "encryption", "blockchain", "saas", "microservice",
        "autonomous", "satellite", "gps",
    ],
    "science": [
        "physics", "chemistry", "quantum", "atom", "molecule", "experiment",
        "hypothesis", "laboratory", "research", "particle", "electron",
        "electromagnetic", "speed of light", "vacuum", "gravity", "tidal",
        "tide", "moon", "carbon capture", "co2", "emission",
    ],
    "finance": [
        "stock", "investment", "revenue", "earnings", "profit", "market",
        "trading", "dividend", "portfolio", "bond", "interest rate", "banking",
        "asset", "fund", "valuation", "ipo", "inflation", "gdp",
    ],
    "economics": [
        "economy", "economic", "gdp", "unemployment", "inflation", "trade",
        "tariff", "fiscal", "monetary", "recession", "supply chain",
        "labor market",
    ],
    "legal": [
        "law", "court", "judge", "legal", "statute", "regulation", "attorney",
        "plaintiff", "defendant", "contract", "liability", "compliance",
        "copyright", "patent", "amendment", "constitution", "legislation",
        "judicial", "verdict", "lawsuit",
    ],
    "education": [
        "school", "student", "teacher", "university", "college", "curriculum",
        "education", "learning", "academic", "classroom", "enrollment",
        "scholarship", "degree", "campus",
    ],
    "history": [
        "century", "ancient", "medieval", "war", "empire", "revolution",
        "historical", "dynasty", "colony", "civilization", "archaeological",
        "renaissance", "ottoman", "roman", "victorian",
    ],
    "environment": [
        "climate", "deforestation", "rainforest", "ecosystem", "carbon",
        "emission", "pollution", "renewable", "solar", "wind energy",
        "biodiversity", "conservation", "endangered", "habitat", "glacier",
        "ocean", "reef", "amazon",
    ],
    "sports": [
        "game", "team", "player", "season", "coach", "championship",
        "tournament", "score", "athlete", "medal", "olympic", "league",
        "stadium", "match", "race", "marathon",
    ],
    "business": [
        "company", "ceo", "startup", "revenue", "customer", "employee",
        "management", "strategy", "acquisition", "merger", "enterprise",
        "product launch", "marketing", "brand", "supply chain", "retail",
        "warranty", "manufacturer",
    ],
    "programming": [
        "python", "javascript", "java ", "rust", "code", "programming",
        "function", "class", "framework", "library", "debugging", "compiler",
        "repository", "github", "open source",
    ],
    "geography": [
        "continent", "ocean", "mountain", "river", "island", "desert",
        "population", "capital city", "latitude", "longitude", "elevation",
        "region", "province", "territory",
    ],
    "energy": [
        "solar panel", "wind turbine", "nuclear", "fossil fuel", "natural gas",
        "petroleum", "renewable energy", "power plant", "electricity",
        "battery", "grid",
    ],
    "agriculture": [
        "farm", "crop", "harvest", "soil", "irrigation", "livestock",
        "agriculture", "organic", "pesticide", "fertilizer", "olive",
        "grain", "wheat",
    ],
    "politics": [
        "election", "president", "congress", "senate", "vote", "policy",
        "government", "political", "democrat", "republican", "legislation",
        "referendum",
    ],
    "crypto": [
        "bitcoin", "ethereum", "cryptocurrency", "blockchain", "token",
        "wallet", "mining", "defi",
    ],
    "automotive": [
        "car", "vehicle", "engine", "electric vehicle", " ev ", "ford",
        "tesla", "toyota", "automotive", "driving", "motor",
    ],
    "real_estate": [
        "real estate", "property", "mortgage", "housing", "rent", "landlord",
        "tenant", "apartment", "commercial property",
    ],
    "nutrition": [
        "calorie", "protein intake", "carbohydrate", "food safety",
        "dietary", "supplement", "meal",
    ],
    "psychology": [
        "psychology", "cognitive", "behavior", "mental", "anxiety",
        "depression", "therapy", "mindfulness", "iq",
    ],
    "statistics": [
        "standard deviation", "regression", "statistical", "p-value",
        "confidence interval", "sample size", "hypothesis test",
    ],
}


def infer_domain(query: str, contexts: list[str]) -> str:
    """Infer the most likely domain from query + contexts text."""
    combined = (query + " " + " ".join(contexts)).lower()
    scores: dict[str, int] = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = 0
        for kw in keywords:
            occurrences = combined.count(kw.lower())
            if occurrences > 0:
                score += occurrences
        if score > 0:
            scores[domain] = score
    if not scores:
        return "general"
    return max(scores, key=lambda d: scores[d])


def generate_tags(query: str, contexts: list[str], domain: str) -> list[str]:
    """Generate 2-3 relevant tags from the content."""
    combined = (query + " " + " ".join(contexts)).lower()
    tag_candidates: list[str] = []

    # Domain-specific tag extraction
    tag_patterns: dict[str, list[str]] = {
        "science": ["physics", "chemistry", "research", "experiment", "light", "gravity", "tides", "carbon"],
        "technology": ["ai", "cloud", "security", "data", "software", "network", "automation"],
        "medical": ["treatment", "diagnosis", "surgery", "clinical", "patients"],
        "health": ["wellness", "nutrition", "hydration", "mental-health", "microplastics"],
        "finance": ["stocks", "earnings", "investment", "banking", "markets"],
        "legal": ["regulation", "compliance", "court", "legislation", "rights"],
        "environment": ["climate", "deforestation", "conservation", "biodiversity", "emissions"],
        "biology": ["marine", "genetics", "species", "ecology", "cellular"],
        "business": ["strategy", "management", "product", "warranty", "operations"],
        "education": ["learning", "curriculum", "assessment", "academic"],
        "history": ["ancient", "modern", "revolution", "civilization"],
        "economics": ["gdp", "trade", "inflation", "labor", "fiscal"],
        "energy": ["renewable", "solar", "nuclear", "grid", "fossil-fuels"],
        "programming": ["code", "framework", "open-source", "debugging"],
        "sports": ["competition", "teams", "athletes", "championship"],
        "agriculture": ["farming", "crops", "organic", "sustainability"],
        "pharmaceutical": ["drug", "trial", "fda", "dosing"],
        "geography": ["regions", "population", "territory"],
        "automotive": ["ev", "vehicles", "manufacturing"],
        "psychology": ["cognitive", "behavior", "mental-health"],
        "politics": ["policy", "governance", "elections"],
    }

    if domain in tag_patterns:
        for tag in tag_patterns[domain]:
            if tag.replace("-", " ") in combined or tag.replace("-", "") in combined:
                tag_candidates.append(tag)

    # Always include domain as a tag if we have fewer than 2
    if len(tag_candidates) < 2:
        tag_candidates.insert(0, domain)

    # Deduplicate and limit
    seen: set[str] = set()
    unique_tags: list[str] = []
    for t in tag_candidates:
        if t not in seen:
            seen.add(t)
            unique_tags.append(t)
    return unique_tags[:3]


def synthesize_document_content(query: str, contexts: list[str]) -> str:
    """
    Synthesize case contexts into a coherent 2-4 sentence corpus document.
    Takes the factual content from contexts and rephrases as a standalone passage.
    """
    if not contexts:
        return ""

    # For a single short context, just clean it up
    if len(contexts) == 1:
        ctx = contexts[0].strip()
        if len(ctx) < 600:
            return ctx
        # Truncate very long contexts to 2-4 sentences
        sentences = re.split(r'(?<=[.!?])\s+', ctx)
        return " ".join(sentences[:4])

    # Multiple contexts: combine key information
    # Take representative sentences (first from each context, then fill)
    selected: list[str] = []
    for ctx in contexts[:3]:  # Max 3 contexts
        sentences = re.split(r'(?<=[.!?])\s+', ctx.strip())
        if sentences:
            selected.append(sentences[0])

    # Add one more sentence from the second context if available
    if len(contexts) > 1:
        extra_sentences = re.split(r'(?<=[.!?])\s+', contexts[1].strip())
        if len(extra_sentences) > 1:
            selected.append(extra_sentences[1])

    # Limit to 4 sentences
    result = " ".join(selected[:4])

    # Safety: if result is too short, use raw first context
    if len(result) < 50:
        return contexts[0].strip()

    return result


def synthesize_document_for_source(
    query: str,
    contexts: list[str],
    source_idx: int,
) -> str:
    """
    For multi-source cases, synthesize a document from a single source's perspective.
    """
    if source_idx < len(contexts):
        ctx = contexts[source_idx].strip()
        sentences = re.split(r'(?<=[.!?])\s+', ctx)
        return " ".join(sentences[:4])
    return contexts[0].strip() if contexts else ""


def generate_title(query: str, contexts: list[str], domain: str) -> str:
    """Generate a descriptive title for the corpus document."""
    q = query.strip().rstrip("?").strip()

    # Remove common question prefixes
    for prefix in [
        "What is ", "What are ", "How does ", "How do ", "Why do ", "Why does ",
        "Is ", "Are ", "Should ", "Can ", "Does ", "Do ", "How effective ",
        "What percentage ", "How long ", "What caused ", "Based on ",
        "How much ", "What was ", "When did ", "Where is ", "Who ",
    ]:
        if q.lower().startswith(prefix.lower()):
            q = q[len(prefix):]
            break

    # Capitalize first letter
    if q:
        q = q[0].upper() + q[1:]

    # Add domain context if title is too generic
    if len(q) < 15:
        q = f"{domain.replace('_', ' ').title()}: {q}"

    return q


# --------------------------------------------------------------------- #
# Main processing functions
# --------------------------------------------------------------------- #


def load_existing_doc_ids() -> set[str]:
    """Load all existing document IDs from documents.jsonl."""
    ids: set[str] = set()
    if DOCUMENTS_PATH.exists():
        with open(DOCUMENTS_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    doc = json.loads(line)
                    ids.add(doc["id"])
    return ids


def load_existing_query_mapping_ids() -> set[str]:
    """Load all existing case IDs from query mappings."""
    ids: set[str] = set()
    if QUERY_MAPPINGS_PATH.exists():
        with open(QUERY_MAPPINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for category in data.get("mappings", {}).values():
            for case_id in category:
                ids.add(case_id)
    return ids


def load_new_cases(
    filename: str, prefix: str, id_range: range
) -> list[dict[str, Any]]:
    """Load new cases from a tier1_core JSON file by ID range."""
    filepath = TIER1_DIR / filename
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    target_ids = {f"{prefix}{n}" for n in id_range}
    return [c for c in data["cases"] if c["id"] in target_ids]


def process_category(
    cat_name: str,
    cat_config: dict[str, Any],
    existing_doc_ids: set[str],
    existing_mapping_ids: set[str],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """
    Process one category of new cases.

    Returns:
        (new_documents, new_query_mappings)
    """
    cases = load_new_cases(
        cat_config["file"],
        cat_config["prefix"],
        cat_config["range"],
    )

    doc_prefix = cat_config["doc_prefix"]
    new_docs: list[dict[str, Any]] = []
    new_mappings: dict[str, dict[str, Any]] = {}

    for case in cases:
        case_id = case["id"]
        query = case["query"]
        contexts = case.get("contexts", [])
        has_multi_source = "context_sources" in case

        if has_multi_source:
            # Generate 2 documents per case, one per source perspective
            source_count = min(2, len(contexts))
            doc_ids_for_case: list[str] = []

            for src_idx in range(source_count):
                doc_id = case_id_to_doc_id(case_id, doc_prefix, source_idx=src_idx)
                doc_ids_for_case.append(doc_id)

                # Skip if already exists (idempotency)
                if doc_id in existing_doc_ids:
                    continue

                ctx_slice = [contexts[src_idx]] if src_idx < len(contexts) else contexts
                domain = infer_domain(query, ctx_slice)
                content = synthesize_document_for_source(query, contexts, src_idx)
                title = generate_title(query, contexts, domain)

                # Make titles distinct for multi-source
                source_info = (
                    case["context_sources"][src_idx]
                    if src_idx < len(case.get("context_sources", []))
                    else {}
                )
                source_type = source_info.get("source_type", "")
                if source_type:
                    title = f"{title} ({source_type.title()} Perspective)"

                tags = generate_tags(query, ctx_slice, domain)

                doc = {
                    "id": doc_id,
                    "title": title,
                    "content": content,
                    "domain": domain,
                    "tags": tags,
                }
                new_docs.append(doc)
                existing_doc_ids.add(doc_id)

            # Query mapping entry
            if case_id not in existing_mapping_ids:
                is_converted = "metadata" in case and "converted_from" in case.get("metadata", {})
                notes = case.get("description", "")
                if is_converted:
                    notes = f"Converted case. {notes}"
                notes += " (multi-source)"

                new_mappings[case_id] = {
                    "query": query,
                    "relevant_docs": doc_ids_for_case,
                    "decoy_docs": [],
                    "notes": notes,
                }
        else:
            # Single document per case
            doc_id = case_id_to_doc_id(case_id, doc_prefix)

            if doc_id not in existing_doc_ids:
                domain = infer_domain(query, contexts)
                content = synthesize_document_content(query, contexts)
                title = generate_title(query, contexts, domain)
                tags = generate_tags(query, contexts, domain)

                doc = {
                    "id": doc_id,
                    "title": title,
                    "content": content,
                    "domain": domain,
                    "tags": tags,
                }
                new_docs.append(doc)
                existing_doc_ids.add(doc_id)

            # Query mapping entry
            if case_id not in existing_mapping_ids:
                is_converted = "metadata" in case and "converted_from" in case.get("metadata", {})
                notes = case.get("description", "")
                if is_converted:
                    notes = f"Converted case. {notes}"

                new_mappings[case_id] = {
                    "query": query,
                    "relevant_docs": [doc_id],
                    "decoy_docs": [],
                    "notes": notes,
                }

    return new_docs, new_mappings


def update_manifest(new_docs: list[dict[str, Any]]) -> dict[str, Any]:
    """Update manifest.json with new document counts."""
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Count domains from ALL documents (existing + new)
    domain_counts: Counter[str] = Counter()
    with open(DOCUMENTS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                doc = json.loads(line)
                domain_counts[doc["domain"]] += 1

    total_docs = sum(domain_counts.values())

    manifest["version"] = "4.0.0"
    manifest["document_count"] = total_docs
    manifest["domains"] = dict(sorted(domain_counts.items()))
    manifest["updated_at"] = "2026-02-12"
    manifest["notes"] = (
        "Curated mix of synthetic documents designed to match the expanded 4.0 benchmark. "
        "Includes documents for 330 new/converted test cases across dispute, abstention, "
        "trustworthy direct, and trustworthy hedged categories. Enhanced with multi-source "
        "perspectives, structured data formats, and domain expansion."
    )

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return manifest


def main() -> None:
    """Main entry point."""
    print("=" * 70)
    print("Phase 6: Corpus Document Generation and Validation")
    print("=" * 70)
    print()

    # Load existing state
    existing_doc_ids = load_existing_doc_ids()
    existing_mapping_ids = load_existing_query_mapping_ids()
    initial_doc_count = len(existing_doc_ids)
    initial_mapping_count = len(existing_mapping_ids)

    print(f"Existing corpus documents: {initial_doc_count}")
    print(f"Existing query mappings:   {initial_mapping_count}")
    print()

    # Process each category
    all_new_docs: list[dict[str, Any]] = []
    all_new_mappings: dict[str, dict[str, dict[str, Any]]] = {}

    for cat_name, cat_config in NEW_CASE_RANGES.items():
        print(f"Processing {cat_name}...")
        new_docs, new_mappings = process_category(
            cat_name, cat_config, existing_doc_ids, existing_mapping_ids,
        )
        all_new_docs.extend(new_docs)
        all_new_mappings[cat_config["category_key"]] = new_mappings

        cases_count = len(cat_config["range"])
        print(f"  Cases in range: {cases_count}")
        print(f"  New documents generated: {len(new_docs)}")
        print(f"  New query mappings: {len(new_mappings)}")
        print()

    # ----------------------------------------------------------------- #
    # 1. Append new documents to documents.jsonl
    # ----------------------------------------------------------------- #
    if all_new_docs:
        print(f"Appending {len(all_new_docs)} new documents to {DOCUMENTS_PATH}")
        with open(DOCUMENTS_PATH, "a", encoding="utf-8") as f:
            for doc in all_new_docs:
                f.write(json.dumps(doc, ensure_ascii=False) + "\n")
    else:
        print("No new documents to append (all already exist).")

    # ----------------------------------------------------------------- #
    # 2. Update query mappings
    # ----------------------------------------------------------------- #
    with open(QUERY_MAPPINGS_PATH, "r", encoding="utf-8") as f:
        query_data = json.load(f)

    total_new_mappings = 0
    for category_key, mappings in all_new_mappings.items():
        if mappings:
            if category_key not in query_data["mappings"]:
                query_data["mappings"][category_key] = {}
            for case_id, mapping in mappings.items():
                if case_id not in query_data["mappings"][category_key]:
                    query_data["mappings"][category_key][case_id] = mapping
                    total_new_mappings += 1

    if total_new_mappings > 0:
        query_data["version"] = "4.0.0"
        print(f"Adding {total_new_mappings} new query mappings to {QUERY_MAPPINGS_PATH}")
        with open(QUERY_MAPPINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(query_data, f, indent=2, ensure_ascii=False)
            f.write("\n")
    else:
        print("No new query mappings to add (all already exist).")

    # ----------------------------------------------------------------- #
    # 3. Update manifest
    # ----------------------------------------------------------------- #
    print(f"\nUpdating manifest at {MANIFEST_PATH}")
    manifest = update_manifest(all_new_docs)

    # ----------------------------------------------------------------- #
    # Summary
    # ----------------------------------------------------------------- #
    final_doc_count = manifest["document_count"]
    final_mapping_count = sum(
        len(cat) for cat in query_data["mappings"].values()
    )

    # Count documents by domain for the new ones
    new_domain_counts: Counter[str] = Counter()
    for doc in all_new_docs:
        new_domain_counts[doc["domain"]] += 1

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Corpus documents:  {initial_doc_count} -> {final_doc_count} (+{final_doc_count - initial_doc_count})")
    print(f"Query mappings:    {initial_mapping_count} -> {final_mapping_count} (+{total_new_mappings})")
    print(f"Manifest version:  {manifest['version']}")
    print(f"Manifest updated:  {manifest['updated_at']}")
    print()

    if all_new_docs:
        print("New documents by domain:")
        for domain, count in sorted(new_domain_counts.items(), key=lambda x: -x[1]):
            print(f"  {domain:20s} {count:4d}")
        print()

    print("New documents by category:")
    for cat_name, cat_config in NEW_CASE_RANGES.items():
        cat_docs = [d for d in all_new_docs if d["id"].startswith(cat_config["doc_prefix"] + "_")]
        print(f"  {cat_name:25s} {len(cat_docs):4d} documents")

    print()
    print("Query mappings by category:")
    for category_key, mappings in all_new_mappings.items():
        print(f"  {category_key:25s} {len(mappings):4d} mappings")

    multi_source_docs = sum(
        1 for d in all_new_docs if "Perspective)" in d.get("title", "")
    )
    if multi_source_docs:
        print(f"\nMulti-source documents (2 per case): {multi_source_docs}")

    print()
    print("Done.")


if __name__ == "__main__":
    main()
