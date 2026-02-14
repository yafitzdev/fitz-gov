#!/usr/bin/env python3
"""
Phase 6 v4.1 Corpus Sync for fitz-gov expansion.

Discovers ALL cases in tier0_sanity and tier1_core that are not yet
represented in the corpus (documents.jsonl) or query mappings
(query_mappings.json), generates corpus documents from their contexts,
updates query mappings, and updates the manifest.

Idempotent: skips already-existing entries on re-run.
"""

import json
import os
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
TIER_DIRS = [DATA_DIR / "tier0_sanity", DATA_DIR / "tier1_core"]

# Category from JSON file -> query mapping section key
CATEGORY_TO_SECTION: dict[str, str] = {
    "abstention": "abstention",
    "dispute": "dispute",
    "trustworthy_hedged": "trustworthy_hedged",
    "trustworthy_direct": "trustworthy_direct",
    "grounding": "grounding",
    "relevance": "relevance",
}

# Category -> doc ID prefix used in corpus
# Matches conventions established by phase6_corpus_and_validation.py
CATEGORY_TO_DOC_PREFIX: dict[str, str] = {
    "abstention": "abstain",
    "dispute": "dispute",
    "trustworthy_hedged": "hedged",
    "trustworthy_direct": "direct",
    "grounding": "grounding",
    "relevance": "relevance",
}

# --------------------------------------------------------------------- #
# Domain inference (reused from phase6_corpus_and_validation.py)
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
    "food": [
        "food", "cooking", "recipe", "ingredient", "restaurant", "cuisine",
        "flavor", "dish",
    ],
    "hr": [
        "hr", "human resources", "hiring", "interview", "onboarding",
        "performance review", "workplace",
    ],
    "hr_workplace": [
        "remote work", "productivity", "office", "hybrid work", "commute",
        "workspace",
    ],
    "government": [
        "agency", "federal", "regulation", "compliance", "bureau",
        "department", "municipal", "public service",
    ],
    "social_media": [
        "tiktok", "instagram", "facebook", "twitter", "social media",
        "influencer", "engagement", "followers",
    ],
    "transportation": [
        "train", "airline", "flight", "airport", "transit", "shipping",
        "logistics", "freight",
    ],
    "medicine": [
        "aspirin", "ibuprofen", "antibiotic", "vaccine", "insulin",
        "cholesterol", "blood pressure", "diabetes",
    ],
    "law": [
        "attorney", "prosecution", "defense", "civil rights", "supreme court",
        "jury", "bail",
    ],
}


def infer_domain(query: str, contexts: list[str], case_domain: str | None = None) -> str:
    """Infer the most likely domain from query + contexts text.

    If the case already has a domain field, prefer it (normalized).
    Falls back to keyword inference.
    """
    if case_domain:
        return _normalize_domain(case_domain)

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


def _normalize_domain(domain: str) -> str:
    """Normalize domain names for corpus compatibility."""
    mapping = {
        "real-estate": "real_estate",
        "hr_workplace": "hr_workplace",
        "social media": "social_media",
    }
    return mapping.get(domain, domain)


# --------------------------------------------------------------------- #
# Tag generation
# --------------------------------------------------------------------- #
TAG_PATTERNS: dict[str, list[str]] = {
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
    "food": ["cooking", "cuisine", "recipe", "ingredients"],
    "hr": ["hiring", "interview", "workplace"],
    "hr_workplace": ["remote-work", "productivity", "collaboration"],
    "government": ["regulation", "policy", "agency"],
    "social_media": ["engagement", "content", "platform"],
    "transportation": ["transit", "logistics", "shipping"],
    "medicine": ["medication", "dosage", "treatment"],
    "law": ["court", "defense", "prosecution"],
    "real_estate": ["property", "housing", "mortgage"],
    "crypto": ["blockchain", "trading", "defi"],
    "nutrition": ["dietary", "supplement", "calories"],
    "statistics": ["regression", "sampling", "analysis"],
}


def generate_tags(query: str, contexts: list[str], domain: str) -> list[str]:
    """Generate 2-3 relevant tags from the content."""
    combined = (query + " " + " ".join(contexts)).lower()
    tag_candidates: list[str] = []

    if domain in TAG_PATTERNS:
        for tag in TAG_PATTERNS[domain]:
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


# --------------------------------------------------------------------- #
# Document ID generation
# --------------------------------------------------------------------- #

def case_id_to_doc_id(case_id: str, doc_prefix: str, source_idx: int | None = None) -> str:
    """
    Generate a deterministic document ID from a case ID.

    Convention follows phase6_corpus_and_validation.py:
      t1_dispute_hard_568    -> dispute_doc_568
      t0_abstain_easy_001    -> abstain_doc_e001
      t1_abstain_hard_951    -> abstain_doc_951
      t1_confident_hard_901  (source 0) -> direct_doc_901a
      t1_confident_hard_901  (source 1) -> direct_doc_901b

    For tier-0 (easy) cases we prefix the number with 'e' to avoid
    collisions with existing tier-1 doc IDs that use the same numbers.
    """
    # Extract numeric suffix
    num = case_id.rsplit("_", 1)[-1]

    # Determine tier to add 'e' prefix for t0 easy cases
    is_t0 = case_id.startswith("t0_")
    if is_t0:
        num = f"e{num}"

    if source_idx is not None:
        suffix = chr(ord("a") + source_idx)
        return f"{doc_prefix}_doc_{num}{suffix}"
    return f"{doc_prefix}_doc_{num}"


# --------------------------------------------------------------------- #
# Title generation
# --------------------------------------------------------------------- #

def generate_title(query: str, domain: str, ctx_idx: int = 0) -> str:
    """Generate a descriptive title for a corpus document."""
    q = query.strip().rstrip("?").strip()

    # Remove common question prefixes
    for prefix in [
        "What is ", "What are ", "How does ", "How do ", "Why do ", "Why does ",
        "Is ", "Are ", "Should ", "Can ", "Could ", "Does ", "Do ",
        "How effective ", "What percentage ", "How long ", "What caused ",
        "Based on ", "How much ", "What was ", "When did ", "Where is ",
        "Who ", "Which ", "What ", "How ", "Is is ",
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

    # Add context indicator for multi-context docs
    if ctx_idx > 0:
        q += f" (Source {ctx_idx + 1})"

    # Truncate if too long
    if len(q) > 80:
        q = q[:77] + "..."

    return q


# --------------------------------------------------------------------- #
# Core logic
# --------------------------------------------------------------------- #

def load_all_cases() -> list[dict[str, Any]]:
    """Load all cases from tier0_sanity and tier1_core."""
    cases: list[dict[str, Any]] = []
    for tier_dir in TIER_DIRS:
        if not tier_dir.exists():
            continue
        for fname in sorted(os.listdir(tier_dir)):
            if not fname.endswith(".json"):
                continue
            filepath = tier_dir / fname
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            category = data["category"]
            for case in data["cases"]:
                # Attach file-level category to each case for mapping
                case["_file_category"] = category
                cases.append(case)
    return cases


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


def load_existing_mapping_keys() -> set[str]:
    """Load all existing mapping keys across all sections."""
    ids: set[str] = set()
    if QUERY_MAPPINGS_PATH.exists():
        with open(QUERY_MAPPINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for section in data.get("mappings", {}).values():
            for key in section:
                ids.add(key)
    return ids


def is_case_mapped(case_id: str, existing_keys: set[str]) -> bool:
    """Check if a case is already mapped (by direct ID or stripped ID)."""
    if case_id in existing_keys:
        return True
    # Also check stripped form (without t0_/t1_ prefix)
    if case_id.startswith("t0_") or case_id.startswith("t1_"):
        stripped = case_id[3:]
        if stripped in existing_keys:
            return True
    return False


def main() -> None:
    print("=" * 70)
    print("Phase 6 v4.1 Corpus Sync")
    print("=" * 70)
    print()

    # ----------------------------------------------------------------- #
    # 1. Load existing state
    # ----------------------------------------------------------------- #
    existing_doc_ids = load_existing_doc_ids()
    existing_mapping_keys = load_existing_mapping_keys()
    initial_doc_count = len(existing_doc_ids)
    initial_mapping_count = len(existing_mapping_keys)

    print(f"Existing corpus documents: {initial_doc_count}")
    print(f"Existing query mappings:   {initial_mapping_count}")
    print()

    # ----------------------------------------------------------------- #
    # 2. Load all cases and find which are new
    # ----------------------------------------------------------------- #
    all_cases = load_all_cases()
    print(f"Total cases in tier0+tier1: {len(all_cases)}")

    new_cases = [c for c in all_cases if not is_case_mapped(c["id"], existing_mapping_keys)]
    print(f"Cases NOT in query mappings: {len(new_cases)}")

    # Breakdown by category
    from collections import defaultdict
    new_by_cat: dict[str, int] = defaultdict(int)
    for c in new_cases:
        new_by_cat[c["_file_category"]] += 1
    for cat in sorted(new_by_cat):
        print(f"  {cat}: {new_by_cat[cat]}")
    print()

    if not new_cases:
        print("All cases are already synced. Nothing to do.")
        return

    # ----------------------------------------------------------------- #
    # 3. Generate corpus documents for new cases
    # ----------------------------------------------------------------- #
    new_docs: list[dict[str, Any]] = []
    # Track new mappings per section
    new_mappings_per_section: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)

    for case in new_cases:
        case_id = case["id"]
        query = case.get("query", "")
        contexts = case.get("contexts", [])
        file_category = case["_file_category"]
        case_domain = case.get("domain", None)
        doc_prefix = CATEGORY_TO_DOC_PREFIX.get(file_category, file_category)
        section_key = CATEGORY_TO_SECTION.get(file_category, file_category)
        has_multi_source = "context_sources" in case

        # Use the mapping key as-is (the full case ID including t0_/t1_ prefix)
        mapping_key = case_id

        if has_multi_source:
            # Multi-source: generate one doc per source perspective (up to 2)
            source_count = min(2, len(contexts))
            doc_ids_for_case: list[str] = []

            for src_idx in range(source_count):
                doc_id = case_id_to_doc_id(case_id, doc_prefix, source_idx=src_idx)
                doc_ids_for_case.append(doc_id)

                if doc_id in existing_doc_ids:
                    continue

                ctx_slice = [contexts[src_idx]] if src_idx < len(contexts) else contexts
                domain = infer_domain(query, ctx_slice, case_domain)
                content = contexts[src_idx].strip() if src_idx < len(contexts) else contexts[0].strip()
                # Truncate to ~4 sentences if very long
                sentences = re.split(r'(?<=[.!?])\s+', content)
                if len(sentences) > 4:
                    content = " ".join(sentences[:4])

                title = generate_title(query, domain, ctx_idx=src_idx)

                # Distinct title for multi-source
                source_info = case.get("context_sources", [])
                if src_idx < len(source_info):
                    si = source_info[src_idx]
                    if isinstance(si, dict):
                        st = si.get("source_type", "")
                        if st:
                            title = f"{title} ({st.title()} Perspective)"
                    elif isinstance(si, str):
                        # Some cases have context_sources as list of strings
                        title = f"{title} (Source {src_idx + 1})"

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

            # For abstention cases with multi-source, docs are decoys
            is_abstention = file_category == "abstention"
            notes = case.get("description", "")
            notes += " (multi-source)"

            new_mappings_per_section[section_key][mapping_key] = {
                "query": query,
                "relevant_docs": [] if is_abstention else doc_ids_for_case,
                "decoy_docs": doc_ids_for_case if is_abstention else [],
                "notes": notes,
            }

        else:
            # Single or multi-context case: one doc per context
            is_abstention = file_category == "abstention"

            if len(contexts) <= 1:
                # Single context -> single document
                doc_id = case_id_to_doc_id(case_id, doc_prefix)
                doc_ids_for_case = [doc_id]

                if doc_id not in existing_doc_ids:
                    domain = infer_domain(query, contexts, case_domain)
                    content = contexts[0].strip() if contexts else ""
                    title = generate_title(query, domain)
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
            else:
                # Multiple contexts -> one doc per context with letter suffix
                doc_ids_for_case = []
                domain = infer_domain(query, contexts, case_domain)

                for ctx_idx, ctx in enumerate(contexts):
                    doc_id = case_id_to_doc_id(case_id, doc_prefix, source_idx=ctx_idx)
                    doc_ids_for_case.append(doc_id)

                    if doc_id in existing_doc_ids:
                        continue

                    content = ctx.strip()
                    sentences = re.split(r'(?<=[.!?])\s+', content)
                    if len(sentences) > 4:
                        content = " ".join(sentences[:4])

                    title = generate_title(query, domain, ctx_idx=ctx_idx)
                    tags = generate_tags(query, [ctx], domain)

                    doc = {
                        "id": doc_id,
                        "title": title,
                        "content": content,
                        "domain": domain,
                        "tags": tags,
                    }
                    new_docs.append(doc)
                    existing_doc_ids.add(doc_id)

            notes = case.get("description", "")

            new_mappings_per_section[section_key][mapping_key] = {
                "query": query,
                "relevant_docs": [] if is_abstention else doc_ids_for_case,
                "decoy_docs": doc_ids_for_case if is_abstention else [],
                "notes": notes,
            }

    print(f"New corpus documents generated: {len(new_docs)}")
    total_new_mappings = sum(len(m) for m in new_mappings_per_section.values())
    print(f"New query mappings generated: {total_new_mappings}")
    print()

    # ----------------------------------------------------------------- #
    # 4. Append new documents to documents.jsonl
    # ----------------------------------------------------------------- #
    if new_docs:
        print(f"Appending {len(new_docs)} new documents to {DOCUMENTS_PATH}")
        with open(DOCUMENTS_PATH, "a", encoding="utf-8") as f:
            for doc in new_docs:
                f.write(json.dumps(doc, ensure_ascii=False) + "\n")
    else:
        print("No new documents to append (all already exist).")

    # ----------------------------------------------------------------- #
    # 5. Update query mappings
    # ----------------------------------------------------------------- #
    with open(QUERY_MAPPINGS_PATH, "r", encoding="utf-8") as f:
        query_data = json.load(f)

    added_mappings = 0
    for section_key, mappings in new_mappings_per_section.items():
        if not mappings:
            continue
        if section_key not in query_data["mappings"]:
            query_data["mappings"][section_key] = {}
        for mapping_key, mapping_value in mappings.items():
            if mapping_key not in query_data["mappings"][section_key]:
                query_data["mappings"][section_key][mapping_key] = mapping_value
                added_mappings += 1

    if added_mappings > 0:
        query_data["version"] = "4.1.0"
        print(f"Adding {added_mappings} new query mappings")
        with open(QUERY_MAPPINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(query_data, f, indent=2, ensure_ascii=False)
            f.write("\n")
    else:
        print("No new query mappings to add (all already exist).")

    # ----------------------------------------------------------------- #
    # 6. Update manifest
    # ----------------------------------------------------------------- #
    print(f"\nUpdating manifest at {MANIFEST_PATH}")

    # Recount all documents from the file
    domain_counts: Counter[str] = Counter()
    with open(DOCUMENTS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                doc = json.loads(line)
                domain_counts[doc["domain"]] += 1

    total_docs = sum(domain_counts.values())

    # Recount all mappings
    total_mappings = sum(len(cat) for cat in query_data["mappings"].values())

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    manifest["version"] = "4.1.0"
    manifest["document_count"] = total_docs
    manifest["domains"] = dict(sorted(domain_counts.items()))
    manifest["updated_at"] = "2026-02-14"
    manifest["notes"] = (
        f"v4.1.0: {total_docs} corpus documents, {total_mappings} query mappings. "
        "Full tier0_sanity + tier1_core coverage. "
        "3-class classifier training coverage: 500+ per class (TRUSTWORTHY/ABSTAIN/DISPUTED)."
    )

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # ----------------------------------------------------------------- #
    # 7. Summary
    # ----------------------------------------------------------------- #
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"New documents added:    {len(new_docs)}")
    print(f"New query mappings:     {added_mappings}")
    print(f"Total documents now:    {total_docs}")
    print(f"Total mappings now:     {total_mappings}")
    print(f"Manifest version:       {manifest['version']}")
    print()

    # Breakdown
    new_domain_counts: Counter[str] = Counter()
    for doc in new_docs:
        new_domain_counts[doc["domain"]] += 1

    if new_docs:
        print("New documents by domain:")
        for domain, count in sorted(new_domain_counts.items(), key=lambda x: -x[1]):
            print(f"  {domain:25s} {count:4d}")
        print()

    print("New mappings by section:")
    for section_key, mappings in sorted(new_mappings_per_section.items()):
        print(f"  {section_key:25s} {len(mappings):4d}")

    print()
    print("Done.")


if __name__ == "__main__":
    main()
