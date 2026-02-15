#!/usr/bin/env python3
"""
Add quality annotations (forbidden_claims, required_elements) to trustworthy cases
that currently lack them.

For trustworthy_hedged cases:
  - forbidden_claims: patterns for hallucinated specifics not in context
  - required_elements: hedging language indicators

For trustworthy_direct cases:
  - forbidden_claims: patterns for unsupported embellishments
  - required_elements: key factual terms from the context
"""

import json
import re
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def extract_numbers(text: str) -> list[str]:
    """Extract specific numbers from text that could be hallucinated."""
    # Match dollar amounts, percentages, plain numbers with context
    patterns = [
        r'\$[\d,]+(?:\.\d+)?(?:\s*(?:million|billion|trillion|k|m|b))?',
        r'[\d,]+(?:\.\d+)?\s*%',
        r'[\d,]+(?:\.\d+)?\s*(?:million|billion|trillion)',
        r'(?:r=|r =)\s*[\d.]+',
    ]
    numbers = set()
    for p in patterns:
        for m in re.finditer(p, text, re.IGNORECASE):
            numbers.add(m.group().strip())
    return list(numbers)


def extract_key_terms(text: str, min_len: int = 4) -> list[str]:
    """Extract key domain-specific terms from text."""
    # Remove common words and extract meaningful terms
    stop_words = {
        'the', 'and', 'for', 'that', 'this', 'with', 'from', 'are', 'was', 'were',
        'been', 'have', 'has', 'had', 'but', 'not', 'they', 'them', 'their', 'its',
        'more', 'also', 'than', 'most', 'some', 'such', 'can', 'may', 'will',
        'into', 'over', 'only', 'other', 'which', 'when', 'what', 'how', 'who',
        'each', 'about', 'between', 'through', 'after', 'before', 'while',
        'both', 'during', 'these', 'those', 'does', 'did', 'should', 'would',
        'could', 'being', 'because', 'very', 'just', 'your', 'there',
    }

    # Find multi-word phrases (2-3 words) that appear to be domain terms
    terms = set()

    # Single significant words
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    for w in words:
        if len(w) >= min_len and w.lower() not in stop_words:
            terms.add(w.lower())

    return list(terms)


def generate_hedged_annotations(case: dict) -> tuple[list[str], list[str]]:
    """Generate forbidden_claims and required_elements for a hedged case."""
    query = case["query"]
    contexts = case.get("contexts", [])
    all_context = " ".join(contexts)
    subcategory = case.get("subcategory", "")
    rationale = case.get("rationale", "")

    forbidden_claims = []
    required_elements = []

    # --- FORBIDDEN CLAIMS ---
    # These should catch hallucinated specifics NOT in the context

    # 1. Generic number hallucination patterns based on query type
    query_lower = query.lower()

    if any(w in query_lower for w in ["price", "cost", "revenue", "salary", "budget", "fee"]):
        # Check if context has specific dollar amounts
        context_dollars = re.findall(r'\$[\d,]+', all_context)
        if not context_dollars:
            forbidden_claims.append(r'\$\d')

    if any(w in query_lower for w in ["when", "date", "deadline", "year", "timeline"]):
        # If query asks about dates not in context
        context_years = re.findall(r'\b20[0-9]{2}\b', all_context)
        if not context_years:
            forbidden_claims.append(r'\b20[0-9]{2}\b')

    if "how many" in query_lower or "how much" in query_lower:
        # If asking for quantity not clearly stated
        forbidden_claims.append(r'(?:approximately|about|around|exactly|precisely)\s+\d{3,}')

    # 2. Causal certainty patterns for correlation/uncertainty subcategories
    if subcategory in ("causal_uncertainty", "hedged_evidence", "mixed_evidence"):
        forbidden_claims.extend([
            r'(?:clearly|definitely|certainly|undoubtedly|proven)\s+(?:cause|show|demonstrate)',
            r'(?:direct|clear|proven)\s+(?:causal|cause)',
        ])

    # 3. Invented study/source attribution
    forbidden_claims.append(
        r'(?:according to|published in|reported by)\s+(?:the\s+)?(?:New York Times|Washington Post|Nature|Science|Lancet|BMJ|JAMA)'
    )

    # 4. Fabricated percentages if context has no percentages
    context_pcts = re.findall(r'\d+(?:\.\d+)?%', all_context)
    if not context_pcts:
        # Only forbid specific percentage claims, not general ones
        forbidden_claims.append(r'\d{2,}(?:\.\d+)?%\s+(?:of|increase|decrease|growth|decline|reduction)')

    # Ensure at least 2 forbidden claims
    if len(forbidden_claims) < 2:
        # Add generic anti-hallucination patterns
        forbidden_claims.append(
            r'(?:specifically|exactly|precisely)\s+\d+\s+(?:people|users|customers|employees|patients|students)'
        )

    # --- REQUIRED ELEMENTS ---
    # For hedged cases, the response should contain hedging/uncertainty language

    # Base hedging patterns that should appear in any hedged response
    hedging_patterns = [
        "however",
        "although",
        "while",
        "but",
        "may",
        "might",
        "could",
        "possibly",
        "potentially",
        "uncertain",
        "unclear",
        "limited",
        "partial",
        "not clear",
        "not certain",
        "not conclusive",
        "correlation",
        "not necessarily",
        "insufficient",
        "caution",
        "caveat",
        "note that",
        "important to note",
        "keep in mind",
        "it's worth noting",
        "suggests",
        "appears",
        "seems",
        "likely",
    ]

    # Subcategory-specific required elements
    if subcategory == "causal_uncertainty":
        required_elements = ["correlation", "cause", "confound", "variable", "not necessarily"]
    elif subcategory == "hedged_evidence":
        required_elements = ["limited", "evidence", "however", "suggests", "may"]
    elif subcategory == "mixed_evidence":
        required_elements = ["however", "while", "on the other hand", "but", "mixed"]
    elif subcategory == "temporal_uncertainty":
        required_elements = ["may change", "at the time", "current", "evolving", "outdated"]
    elif subcategory == "methodology_difference":
        required_elements = ["methodology", "approach", "different", "method", "varies"]
    elif subcategory == "evidence_quality":
        required_elements = ["quality", "evidence", "limited", "however", "note"]
    elif subcategory == "partial_answer":
        required_elements = ["not mentioned", "not specified", "not provided", "missing", "unavailable"]
    elif subcategory == "scope_condition":
        required_elements = ["depends", "condition", "specific", "context", "varies"]
    elif subcategory == "entity_ambiguity":
        required_elements = ["unclear", "which", "ambiguous", "specify", "multiple"]
    elif subcategory == "different_aspects":
        required_elements = ["aspect", "however", "while", "different", "on the other hand"]
    elif subcategory == "stale_source":
        required_elements = ["outdated", "may have changed", "at the time", "current", "since"]
    elif subcategory == "evolving_facts":
        required_elements = ["evolving", "changing", "current", "may change", "updated"]
    elif subcategory == "version_overlap":
        required_elements = ["version", "varies", "depends", "specific", "which"]
    elif subcategory == "numerical_near_miss":
        required_elements = ["approximately", "close to", "nearly", "about", "roughly"]
    elif subcategory == "implicit_assumptions":
        required_elements = ["assumes", "assumption", "if", "provided that", "depending"]
    elif subcategory == "adjacent_entity":
        required_elements = ["different", "not the same", "similar", "however", "specifically"]
    elif subcategory == "cross_domain_transfer":
        required_elements = ["different context", "may not apply", "however", "specific", "domain"]
    elif subcategory == "cross_source_partial":
        required_elements = ["source", "limited", "partial", "incomplete", "additional"]
    elif subcategory == "different_framing":
        required_elements = ["perspective", "framing", "however", "different", "alternatively"]
    elif subcategory == "hedged_contradiction_corroborated":
        required_elements = ["contradiction", "however", "disagree", "conflict", "noted"]
    else:
        # Generic hedging for unknown subcategories
        required_elements = ["however", "may", "suggests", "note", "while"]

    # Set min_required to 1 — just need at least one hedging indicator
    return forbidden_claims, required_elements


def generate_direct_annotations(case: dict) -> tuple[list[str], list[str]]:
    """Generate forbidden_claims and required_elements for a direct case."""
    query = case["query"]
    contexts = case.get("contexts", [])
    all_context = " ".join(contexts)
    subcategory = case.get("subcategory", "")

    forbidden_claims = []
    required_elements = []

    # --- FORBIDDEN CLAIMS ---
    # For direct cases, forbid unsupported embellishments beyond what context says

    # 1. Invented attribution
    forbidden_claims.append(
        r'(?:according to|published in|reported by)\s+(?:the\s+)?(?:New York Times|Washington Post|Nature|Science|Lancet|BMJ|JAMA)'
    )

    # 2. Fabricated numbers not in context
    context_numbers = set(re.findall(r'\b\d+(?:\.\d+)?(?:%|\s*(?:million|billion|trillion|k|m|percent))?\b', all_context, re.IGNORECASE))
    if not context_numbers:
        forbidden_claims.append(r'(?:approximately|about|around|exactly)\s+\d{3,}')

    # 3. Invented names/entities not in context
    # Match capitalized multi-word names that aren't in context
    context_upper = all_context.upper()
    forbidden_claims.append(
        r'(?:Dr\.|Prof\.|CEO|CTO|Director)\s+[A-Z][a-z]+\s+[A-Z][a-z]+'
    )

    # 4. Dates not in context
    context_years = set(re.findall(r'\b(?:19|20)\d{2}\b', all_context))
    if len(context_years) <= 1:
        # If context has 0-1 years, forbid specific date ranges
        forbidden_claims.append(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}')

    # Ensure at least 2
    if len(forbidden_claims) < 2:
        forbidden_claims.append(
            r'(?:specifically|exactly|precisely)\s+\d+\s+(?:people|users|customers|employees|patients|students)'
        )

    # --- REQUIRED ELEMENTS ---
    # For direct cases, the response should contain key facts from the context

    # Extract key terms from context that should appear in a correct answer
    key_terms = extract_key_terms(all_context, min_len=5)

    # Extract numbers from context — these are important facts to preserve
    context_nums = extract_numbers(all_context)

    # Build required elements from a mix of key terms and numbers
    if context_nums:
        # Include at least one number from context
        for num in context_nums[:2]:
            # Clean the number for substring matching
            clean_num = num.strip().replace(',', '')
            if len(clean_num) >= 2:
                required_elements.append(clean_num)

    # Add key domain terms from context
    # Prioritize terms that appear in the query too (likely the answer)
    query_terms = set(extract_key_terms(query, min_len=4))
    context_terms = set(key_terms)
    overlap_terms = query_terms & context_terms

    # Add overlapping terms first (most relevant)
    for term in list(overlap_terms)[:3]:
        if term not in required_elements:
            required_elements.append(term)

    # Then add unique context terms
    remaining = context_terms - overlap_terms
    for term in sorted(remaining, key=lambda t: len(t), reverse=True)[:5]:
        if len(required_elements) >= 5:
            break
        if term not in required_elements:
            required_elements.append(term)

    # Ensure at least 2 required elements
    if len(required_elements) < 2:
        # Fall back to using first significant words from query
        query_words = [w for w in re.findall(r'\b[a-zA-Z]{4,}\b', query.lower())
                      if w not in {'what', 'does', 'when', 'where', 'which', 'that', 'this', 'with', 'from', 'have', 'about'}]
        for w in query_words[:3]:
            if w not in required_elements:
                required_elements.append(w)

    return forbidden_claims, required_elements[:5]  # Cap at 5


def annotate_file(filepath: str, category_type: str) -> int:
    """Add annotations to cases in a file that lack them.

    Returns number of cases annotated.
    """
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    annotated = 0
    for case in data["cases"]:
        has_fc = bool(case.get("forbidden_claims"))
        has_re = bool(case.get("required_elements"))

        if has_fc and has_re:
            continue  # Already fully annotated

        if category_type == "hedged":
            fc, re_list = generate_hedged_annotations(case)
        else:
            fc, re_list = generate_direct_annotations(case)

        if not has_fc:
            case["forbidden_claims"] = fc
        if not has_re:
            case["required_elements"] = re_list

        # Ensure evaluation_config has the right settings for quality checks
        ec = case.get("evaluation_config", {})
        if "use_regex" not in ec:
            ec["use_regex"] = True if not has_fc else ec.get("use_regex", True)
        if "case_insensitive" not in ec:
            ec["case_insensitive"] = True
        if not has_re and "min_required" not in ec:
            ec["min_required"] = 1
        case["evaluation_config"] = ec

        annotated += 1

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return annotated


def main():
    print("=== Adding quality annotations to trustworthy cases ===\n")

    # Process tier1 hedged
    hedged_path = DATA_DIR / "tier1_core" / "trustworthy_hedged.json"
    count = annotate_file(str(hedged_path), "hedged")
    print(f"Annotated {count} hedged cases in tier1")

    # Process tier1 direct
    direct_path = DATA_DIR / "tier1_core" / "trustworthy_direct.json"
    count = annotate_file(str(direct_path), "direct")
    print(f"Annotated {count} direct cases in tier1")

    # Process tier0 hedged
    hedged_t0 = DATA_DIR / "tier0_sanity" / "trustworthy_hedged.json"
    count = annotate_file(str(hedged_t0), "hedged")
    print(f"Annotated {count} hedged cases in tier0")

    # Process tier0 direct
    direct_t0 = DATA_DIR / "tier0_sanity" / "trustworthy_direct.json"
    count = annotate_file(str(direct_t0), "direct")
    print(f"Annotated {count} direct cases in tier0")

    # Verify
    print("\n=== Verification ===")
    for path, name in [
        (hedged_path, "tier1 hedged"),
        (direct_path, "tier1 direct"),
        (hedged_t0, "tier0 hedged"),
        (direct_t0, "tier0 direct"),
    ]:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        total = len(d["cases"])
        has_fc = sum(1 for c in d["cases"] if c.get("forbidden_claims"))
        has_re = sum(1 for c in d["cases"] if c.get("required_elements"))
        has_both = sum(1 for c in d["cases"] if c.get("forbidden_claims") and c.get("required_elements"))
        print(f"{name}: {total} total, {has_fc} with FC, {has_re} with RE, {has_both} with both")

    print("\nDone!")


if __name__ == "__main__":
    main()
