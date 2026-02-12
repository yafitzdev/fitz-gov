#!/usr/bin/env python3
"""Phase 5: Generate corpus documents, query mappings, and update manifest.

Reads all grounding and relevance cases, generates corpus docs from their contexts,
creates query mappings, and updates the manifest with new counts.
"""

import json
import hashlib
from pathlib import Path
from collections import Counter


def generate_corpus_docs():
    """Generate corpus documents from grounding and relevance case contexts."""
    docs = []
    doc_id_counter = Counter()

    for category in ["grounding", "relevance"]:
        filepath = Path(f"data/tier1_core/{category}.json")
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        for case in data["cases"]:
            case_id = case["id"]
            domain = case.get("domain", "general")
            contexts = case.get("contexts", [])
            query = case.get("query", "")

            for i, ctx in enumerate(contexts):
                # Generate a stable doc ID from the case ID and context index
                doc_id = f"{category}_doc_{case_id.replace('t1_', '').replace('_hard_', '_').replace('_medium_', '_')}_{i+1}"

                # Derive a title from the query
                title = _derive_title(query, domain, i)

                # Determine tags from domain and subcategory
                subcat = case.get("subcategory", "")
                tags = [domain]
                if subcat:
                    tags.append(subcat.replace("_", "-"))

                doc = {
                    "id": doc_id,
                    "title": title,
                    "content": ctx,
                    "domain": _normalize_domain(domain),
                    "tags": tags,
                }
                docs.append(doc)

    return docs


def _derive_title(query: str, domain: str, ctx_idx: int) -> str:
    """Create a document title from the query."""
    # Clean up the query into a title
    q = query.strip().rstrip("?").strip()
    # Remove leading question words
    for prefix in ["What is ", "What are ", "How does ", "How do ", "How is ",
                    "Why does ", "Why do ", "Why is ", "Is ", "Are ", "Does ",
                    "Do ", "Should ", "Can ", "Could ", "When did ", "When was ",
                    "Who ", "Which ", "What ", "How "]:
        if q.lower().startswith(prefix.lower()):
            q = q[len(prefix):]
            break
    # Capitalize first letter
    if q:
        q = q[0].upper() + q[1:]
    # Add context indicator for multi-context docs
    if ctx_idx > 0:
        q += f" (Source {ctx_idx + 1})"
    # Truncate if too long
    if len(q) > 80:
        q = q[:77] + "..."
    return q


def _normalize_domain(domain: str) -> str:
    """Normalize domain names for corpus compatibility."""
    mapping = {
        "medicine": "medical",
        "hr_workplace": "hr",
        "real_estate": "real_estate",
        "social_media": "technology",  # closest corpus domain
    }
    return mapping.get(domain, domain)


def generate_query_mappings():
    """Generate query mappings for grounding and relevance cases."""
    mappings = {}

    for category in ["grounding", "relevance"]:
        filepath = Path(f"data/tier1_core/{category}.json")
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        cat_mappings = {}
        for case in data["cases"]:
            case_id = case["id"]
            case_id_short = case_id.replace("t1_", "")
            query = case.get("query", "")
            contexts = case.get("contexts", [])

            # Generate doc IDs matching the corpus doc generation
            relevant_docs = []
            for i in range(len(contexts)):
                doc_id = f"{category}_doc_{case_id.replace('t1_', '').replace('_hard_', '_').replace('_medium_', '_')}_{i+1}"
                relevant_docs.append(doc_id)

            cat_mappings[case_id_short] = {
                "query": query,
                "relevant_docs": relevant_docs,
                "decoy_docs": [],
                "notes": f"{category} test case - {case.get('subcategory', 'unknown')} subcategory",
            }

        mappings[category] = cat_mappings

    return mappings


def update_manifest(new_doc_count: int):
    """Update manifest.json with new document counts."""
    manifest_path = Path("data/corpus/manifest.json")
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    # Count domains from the full corpus
    domain_counts = Counter()
    with open("data/corpus/documents.jsonl", encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            domain_counts[doc.get("domain", "general")] += 1

    manifest["version"] = "4.1.0"
    manifest["document_count"] = sum(domain_counts.values())
    manifest["domains"] = dict(sorted(domain_counts.items()))
    manifest["updated_at"] = "2026-02-12"
    manifest["notes"] = (
        "v4.1.0: Domain rebalancing (106 conversions), grounding expansion (34→200), "
        "relevance expansion (32→200), classification attributes on all cases, "
        "query type diversification."
    )

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return manifest["document_count"]


def main():
    # 1. Generate corpus documents
    print("Generating corpus documents from grounding/relevance cases...")
    new_docs = generate_corpus_docs()
    print(f"  Generated {len(new_docs)} new corpus documents")

    # Check for duplicate IDs against existing corpus
    existing_ids = set()
    corpus_path = Path("data/corpus/documents.jsonl")
    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            existing_ids.add(doc["id"])

    new_ids = {d["id"] for d in new_docs}
    dupes = existing_ids & new_ids
    if dupes:
        print(f"  WARNING: {len(dupes)} duplicate doc IDs found, will skip: {list(dupes)[:5]}...")
        new_docs = [d for d in new_docs if d["id"] not in existing_ids]

    # Append new docs to corpus
    with open(corpus_path, "a", encoding="utf-8") as f:
        for doc in new_docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")
    print(f"  Appended {len(new_docs)} documents to corpus")

    # 2. Generate query mappings
    print("\nGenerating query mappings...")
    new_mappings = generate_query_mappings()

    mappings_path = Path("data/queries/query_mappings.json")
    with open(mappings_path, encoding="utf-8") as f:
        all_mappings = json.load(f)

    for category, cat_mappings in new_mappings.items():
        if category not in all_mappings["mappings"]:
            all_mappings["mappings"][category] = {}
        all_mappings["mappings"][category].update(cat_mappings)
        print(f"  {category}: {len(cat_mappings)} mappings")

    all_mappings["version"] = "4.1.0"

    with open(mappings_path, "w", encoding="utf-8") as f:
        json.dump(all_mappings, f, indent=2, ensure_ascii=False)
        f.write("\n")

    total_mappings = sum(len(v) for v in all_mappings["mappings"].values())
    print(f"  Total query mappings: {total_mappings}")

    # 3. Update manifest
    print("\nUpdating manifest...")
    total_docs = update_manifest(len(new_docs))
    print(f"  Total corpus documents: {total_docs}")

    # 4. Validate - check for duplicate case IDs across all files
    print("\nValidating...")
    all_case_ids = []
    for tier_dir in ["tier0_sanity", "tier1_core"]:
        tier_path = Path(f"data/{tier_dir}")
        if not tier_path.exists():
            continue
        for filepath in sorted(tier_path.glob("*.json")):
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
            for case in data.get("cases", []):
                all_case_ids.append((case["id"], filepath.name))

    id_counts = Counter(cid for cid, _ in all_case_ids)
    dupes = {cid: cnt for cid, cnt in id_counts.items() if cnt > 1}
    if dupes:
        print(f"  WARNING: {len(dupes)} duplicate case IDs found!")
        for cid, cnt in list(dupes.items())[:10]:
            files = [f for i, f in all_case_ids if i == cid]
            print(f"    {cid} appears {cnt} times in: {files}")
    else:
        print(f"  No duplicate case IDs (checked {len(all_case_ids)} cases)")

    # 5. Summary statistics
    print("\nFinal statistics:")
    for tier_dir in ["tier0_sanity", "tier1_core"]:
        tier_path = Path(f"data/{tier_dir}")
        if not tier_path.exists():
            continue
        total = 0
        for filepath in sorted(tier_path.glob("*.json")):
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
            n = len(data.get("cases", []))
            total += n
            print(f"  {tier_dir}/{filepath.name}: {n} cases")
        print(f"  {tier_dir} total: {total}")


if __name__ == "__main__":
    main()
