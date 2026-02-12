#!/usr/bin/env python3
"""Backfill classification attributes on all tier0 + tier1 cases.

Adds 6 fields to every case:
  domain, query_type, source_type, context_count, reasoning_type, evidence_pattern
"""

import json
import re
from pathlib import Path

# ── Domain classification ──────────────────────────────────────────────────

DOMAIN_KEYWORDS = {
    "technology": [
        "software", "algorithm", "API", "database", "cloud", "kubernetes", "docker",
        "React", "Python", "server", "AWS", "machine learning", "GPU", "CPU",
        "microservices", "cybersecurity", "encryption", "programming", "TLS", "HTTP",
        "javascript", "SaaS", "DevOps", "deployment", "Nginx", "PostgreSQL", "Git",
        "Lambda", "ERP", "component", "lifecycle", "Node.js", "SHA-1", "cipher",
        "Rust", "compiler", "REST", "GraphQL", "OAuth", "SSO", "CI/CD", "pipeline",
        "container", "virtualization", "firewall", "malware", "phishing", "blockchain",
        "NFT", "smart contract", "deep learning", "neural network", "LLM", "GPT",
        "chatbot", "NLP", "computer vision", "robotics", "IoT", "5G", "WiFi",
        "bandwidth", "latency", "cache", "CDN", "DNS", "TCP", "UDP", "SSH",
        "Linux", "Windows", "macOS", "Android", "iOS", "app", "frontend", "backend",
        "framework", "library", "SDK", "IDE", "debug", "unit test", "agile", "scrum",
        "sprint", "repository", "branch", "commit", "microservice", "monolith",
    ],
    "finance": [
        "revenue", "stock", "market", "investment", "profit", "quarterly", "IPO",
        "valuation", "ROI", "budget", "cost", "financial", "bank", "startup", "CEO",
        "acquisition", "merger", "pricing", "shareholder", "fiscal", "earnings", "TCO",
        "venture capital", "interest rate", "inflation", "GDP", "mortgage", "portfolio",
        "bond", "dividend", "FDIC", "retirement", "401k", "tax credit", "churn",
        "warranty", "enterprise", "compensation", "bonus", "equity", "hedge fund",
        "derivatives", "forex", "cryptocurrency", "bitcoin", "ethereum", "S&P",
        "Dow Jones", "NASDAQ", "mutual fund", "index fund", "ETF", "credit score",
        "loan", "debt", "bankruptcy", "audit", "accounting", "balance sheet",
        "cash flow", "EBITDA", "P/E ratio", "market cap", "bear market", "bull market",
    ],
    "medicine": [
        "patient", "treatment", "drug", "hospital", "clinical", "disease", "symptom",
        "medical", "health", "doctor", "therapy", "diagnosis", "pharmaceutical", "FDA",
        "dosage", "cancer", "blood", "surgery", "vaccine", "medication", "HIPAA",
        "cholesterol", "diabetes", "depression", "anxiety", "melatonin", "aspirin",
        "alzheimer", "dementia", "fasting", "BMI", "obesity", "sickle cell", "CRISPR",
        "H. pylori", "lung cancer", "immunotherapy", "celiac", "dental implant",
        "MRI", "CT scan", "X-ray", "ultrasound", "biopsy", "pathology", "oncology",
        "cardiology", "neurology", "pediatrics", "pharmacy", "prescription",
        "antibiotic", "antiviral", "anesthesia", "organ transplant", "dialysis",
    ],
    "science": [
        "quantum", "physics", "chemistry", "molecule", "experiment", "hypothesis",
        "laboratory", "photon", "electron", "atom", "particle", "gravity", "evolution",
        "geological", "astronomy", "telescope", "planet", "mars", "orbit",
        "boiling point", "melting point", "carbon-14", "speed of light", "microplastic",
        "coral", "marine", "ecosystem", "biodiversity", "correlation",
        "replication", "peer review", "Everest", "genome", "DNA", "RNA",
        "protein", "cell", "mitosis", "photosynthesis", "entropy", "thermodynamics",
        "velocity", "acceleration", "wavelength", "frequency", "spectrum",
    ],
    "law": [
        "court", "legal", "regulation", "compliance", "lawsuit", "constitutional",
        "legislation", "statute", "amendment", "GDPR", "patent", "copyright",
        "liability", "jurisdiction", "miranda", "prosecution", "defendant", "judge",
        "contract", "non-compete", "EEOC", "BAC", "zoning", "ordinance", "antitrust",
        "attorney", "lawyer", "sentencing", "parole", "verdict", "plaintiff",
        "arbitration", "mediation", "injunction", "subpoena", "deposition",
    ],
    "education": [
        "student", "school", "university", "curriculum", "teacher", "classroom",
        "academic", "degree", "enrollment", "standardized test", "GPA", "tutor",
        "college", "professor", "lecture", "STEM", "literacy", "homework",
        "scholarship", "campus", "syllabus", "semester", "graduate", "undergraduate",
    ],
    "environment": [
        "climate", "carbon", "emission", "renewable", "solar", "wind energy",
        "nuclear power", "fossil fuel", "deforestation", "pollution", "sustainability",
        "electric vehicle", "battery", "lithium", "desalination", "recycling",
        "coal", "natural gas", "air quality", "sea level", "greenhouse",
        "ozone", "conservation", "wetland", "endangered species",
    ],
    "sports": [
        "game", "championship", "league", "player", "coach", "season", "score",
        "tournament", "FIFA", "NFL", "NBA", "Olympics", "World Cup", "marathon",
        "soccer", "football", "baseball", "basketball", "creatine", "athletic",
        "doping", "medal", "referee", "stadium", "team", "roster", "draft",
        "playoffs", "MVP", "batting", "pitching", "goalkeeper", "tennis",
    ],
    "food": [
        "food", "diet", "calorie", "organic", "gluten", "vitamin", "nutrition",
        "recipe", "sodium", "cooking", "restaurant", "meat", "vegetable", "GMO",
        "coffee", "sugar", "protein shake", "Mediterranean", "aspartame", "burger",
        "ingredient", "cuisine", "chef", "baking", "fermentation", "preservative",
    ],
    "social_media": [
        "social media", "instagram", "twitter", "facebook", "tiktok", "influencer",
        "viral", "streaming", "content creator", "podcast", "youtube", "follower",
        "hashtag", "engagement", "algorithm feed", "misinformation",
    ],
    "real_estate": [
        "real estate", "property", "housing", "rent", "construction", "building",
        "square feet", "occupancy", "LEED", "residential", "commercial property",
        "mortgage rate", "appraisal", "landlord", "tenant", "lease",
    ],
    "hr_workplace": [
        "employee", "workplace", "hiring", "salary", "remote work", "human resources",
        "onboarding", "PTO", "retention", "diversity", "parental leave",
        "performance review", "promotion", "termination", "benefits", "payroll",
    ],
    "transportation": [
        "vehicle", "automotive", "traffic", "transit", "shipping", "logistics",
        "freight", "aviation", "airline", "railroad", "Boeing", "Dreamliner",
        "fleet", "cargo", "route", "commute", "highway", "bridge", "tunnel",
    ],
    "agriculture": [
        "agriculture", "farming", "crop", "livestock", "harvest", "irrigation",
        "soil", "pesticide", "fertilizer", "organic farm", "yield", "grain",
        "dairy", "poultry", "vineyard", "orchard", "greenhouse farming",
    ],
    "history": [
        "century", "ancient", "empire", "colonial", "revolution", "medieval",
        "dynasty", "historical", "civilization", "Roman", "Renaissance", "World War",
        "founding father", "archaeological", "artifact", "pharaoh", "monarchy",
    ],
    "psychology": [
        "psychology", "cognitive", "behavioral", "screen time", "child development",
        "attachment", "mindfulness", "meditation", "ADHD", "autism", "memory",
        "placebo", "priming", "therapy session", "counseling", "psychologist",
        "mental health", "trauma", "IQ", "personality", "Freud", "Jung",
    ],
    "government": [
        "government", "municipal", "federal agency", "public service", "census",
        "immigration", "welfare", "social security", "public housing", "voting",
        "election", "democracy", "legislation", "congress", "senate", "parliament",
        "mayor", "governor", "president", "policy", "bureaucracy", "public sector",
    ],
}


def classify_domain(case: dict) -> str:
    """Classify case into a domain using keyword matching."""
    text = (case.get("query", "") + " " + " ".join(case.get("contexts", []))).lower()
    scores: dict[str, int] = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in text)
        if score > 0:
            scores[domain] = score
    if scores:
        return max(scores, key=scores.get)
    return "general"


# ── Query type classification ──────────────────────────────────────────────

def classify_query_type(query: str) -> str:
    """Classify query by its first interrogative word."""
    q = query.strip().lower()
    # Check for compare pattern first
    if any(w in q for w in ["compare", "versus", " vs ", " vs.", "difference between", "differ from"]):
        return "compare"
    # Check first word
    first_word = re.split(r"\s+", q)[0] if q else ""
    mapping = {
        "what": "what", "how": "how", "why": "why",
        "is": "is", "are": "is", "was": "is",
        "does": "does", "do": "does", "did": "does",
        "should": "should", "can": "should", "could": "should", "would": "should",
        "when": "when", "who": "who", "whose": "who",
        "which": "which", "where": "which",
    }
    return mapping.get(first_word, "what")


# ── Source type classification ─────────────────────────────────────────────

def classify_source_type(case: dict) -> str:
    """Determine source configuration."""
    if case.get("context_sources"):
        return "multi_source"
    return "single"


# ── Reasoning type classification ──────────────────────────────────────────

def classify_reasoning_type(case: dict) -> str:
    """Infer reasoning type from subcategory and query."""
    subcat = case.get("subcategory", "").lower()
    query = case.get("query", "").lower()

    # Subcategory-based rules
    if any(k in subcat for k in ["causal", "explicit_causal"]):
        return "causal"
    if any(k in subcat for k in ["compar", "opposing", "binary_conflict"]):
        return "comparative"
    if any(k in subcat for k in ["process", "procedural", "step"]):
        return "procedural"
    if any(k in subcat for k in ["temporal", "time", "date", "chronolog"]):
        return "temporal"
    if any(k in subcat for k in ["evaluat", "assess", "should", "recommend"]):
        return "evaluative"

    # Query-based fallback
    first_word = re.split(r"\s+", query)[0] if query else ""
    if first_word == "why":
        return "causal"
    if "compare" in query or " vs " in query or "difference" in query:
        return "comparative"
    if first_word == "how" and ("step" in query or "process" in query or "procedure" in query):
        return "procedural"
    if first_word in ("when", "what time", "what date"):
        return "temporal"
    if first_word in ("should", "is", "are", "does", "do", "can", "could"):
        return "evaluative"

    return "factual"


# ── Evidence pattern classification ────────────────────────────────────────

EVIDENCE_PATTERN_MAP = {
    # Category-level defaults
    "dispute": "conflicting",
    "abstention": "absent",
    "grounding": "direct",
    "relevance": "indirect",
    # Subcategory overrides
    "trustworthy_direct": "direct",
    "trustworthy_hedged": "partial",
}

SUBCAT_EVIDENCE_OVERRIDES = {
    "wrong_entity": "absent",
    "missing_data": "absent",
    "temporal_mismatch": "absent",
    "wrong_specificity": "absent",
    "no_context": "absent",
    "out_of_scope": "absent",
    "numerical_conflict": "conflicting",
    "opposing_conclusions": "conflicting",
    "binary_conflict": "conflicting",
    "implicit_contradiction": "conflicting",
    "different_aspects": "mixed",
    "entity_ambiguity": "mixed",
    "evidence_quality": "partial",
    "temporal_uncertainty": "partial",
    "partial_answer": "partial",
    "tangent_drift": "indirect",
    "wrong_entity_focus": "indirect",
    "cherry_picking": "mixed",
}


def classify_evidence_pattern(case: dict) -> str:
    """Classify evidence relationship to query."""
    category = case.get("category", "")
    subcat = case.get("subcategory", "").lower()

    # Check subcategory overrides first
    for key, pattern in SUBCAT_EVIDENCE_OVERRIDES.items():
        if key in subcat:
            return pattern

    # Fall back to category default
    return EVIDENCE_PATTERN_MAP.get(category, "direct")


# ── Main backfill logic ────────────────────────────────────────────────────

def backfill_file(filepath: Path) -> int:
    """Backfill classifications on all cases in a file. Returns count of updated cases."""
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    cases = data.get("cases", [])
    updated = 0

    for case in cases:
        changed = False

        # domain
        if not case.get("domain"):
            case["domain"] = classify_domain(case)
            changed = True

        # query_type
        if not case.get("query_type"):
            case["query_type"] = classify_query_type(case.get("query", ""))
            changed = True

        # source_type
        if not case.get("source_type"):
            case["source_type"] = classify_source_type(case)
            changed = True

        # context_count
        if not case.get("context_count"):
            case["context_count"] = len(case.get("contexts", []))
            changed = True

        # reasoning_type
        if not case.get("reasoning_type"):
            case["reasoning_type"] = classify_reasoning_type(case)
            changed = True

        # evidence_pattern
        if not case.get("evidence_pattern"):
            case["evidence_pattern"] = classify_evidence_pattern(case)
            changed = True

        if changed:
            updated += 1

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return updated


def main():
    root = Path("data")
    total_updated = 0

    for tier_dir in ["tier0_sanity", "tier1_core"]:
        tier_path = root / tier_dir
        if not tier_path.exists():
            continue
        for filepath in sorted(tier_path.glob("*.json")):
            count = backfill_file(filepath)
            total_updated += count
            print(f"  {tier_dir}/{filepath.name}: {count} cases updated")

    print(f"\nTotal: {total_updated} cases backfilled")

    # Validate
    valid_domains = {
        "technology", "finance", "medicine", "science", "law", "education",
        "environment", "sports", "food", "social_media", "real_estate",
        "hr_workplace", "transportation", "agriculture", "history",
        "psychology", "government", "general",
    }
    valid_query_types = {"what", "how", "why", "is", "does", "should", "when", "who", "which", "compare"}
    valid_source_types = {"single", "multi_source"}
    valid_reasoning = {"factual", "causal", "comparative", "procedural", "evaluative", "temporal"}
    valid_evidence = {"direct", "indirect", "conflicting", "absent", "partial", "mixed"}

    errors = 0
    for tier_dir in ["tier0_sanity", "tier1_core"]:
        tier_path = root / tier_dir
        if not tier_path.exists():
            continue
        for filepath in sorted(tier_path.glob("*.json")):
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
            for case in data.get("cases", []):
                cid = case.get("id", "?")
                if case.get("domain", "") not in valid_domains:
                    print(f"  ERROR: {cid} invalid domain: {case.get('domain')}")
                    errors += 1
                if case.get("query_type", "") not in valid_query_types:
                    print(f"  ERROR: {cid} invalid query_type: {case.get('query_type')}")
                    errors += 1
                if case.get("source_type", "single") not in valid_source_types:
                    print(f"  ERROR: {cid} invalid source_type: {case.get('source_type')}")
                    errors += 1
                if case.get("reasoning_type", "") not in valid_reasoning:
                    print(f"  ERROR: {cid} invalid reasoning_type: {case.get('reasoning_type')}")
                    errors += 1
                if case.get("evidence_pattern", "") not in valid_evidence:
                    print(f"  ERROR: {cid} invalid evidence_pattern: {case.get('evidence_pattern')}")
                    errors += 1

    if errors:
        print(f"\n{errors} validation errors!")
    else:
        print("\nAll classifications valid!")


if __name__ == "__main__":
    main()
