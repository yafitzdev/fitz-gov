# tests/test_data_integrity.py
"""
Tests that verify the actual benchmark data files are well-formed.

These tests load the real JSON data files from the data/ directory
and validate their structure, field values, and consistency.
"""

import json
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).parent.parent / "data"
TIER0_DIR = DATA_DIR / "tier0_sanity"
TIER1_DIR = DATA_DIR / "tier1_core"

VALID_CATEGORIES = {
    "abstention",
    "dispute",
    "trustworthy_direct",
    "trustworthy_hedged",
}
VALID_MODES = {"trustworthy", "disputed", "abstain"}
VALID_DOMAINS = {
    "technology",
    "finance",
    "medicine",
    "science",
    "law",
    "education",
    "environment",
    "sports",
    "food",
    "social_media",
    "real_estate",
    "hr_workplace",
    "transportation",
    "agriculture",
    "history",
    "psychology",
    "government",
    "general",
}
VALID_QUERY_TYPES = {
    "what",
    "how",
    "why",
    "is",
    "does",
    "should",
    "when",
    "who",
    "which",
    "compare",
}
VALID_REASONING_TYPES = {
    "factual",
    "causal",
    "comparative",
    "procedural",
    "evaluative",
    "temporal",
}
VALID_EVIDENCE_PATTERNS = {
    "direct",
    "indirect",
    "conflicting",
    "absent",
    "partial",
    "mixed",
}


def load_all_cases():
    """Load all cases from both tier0 and tier1 data directories."""
    cases = []
    for tier_dir in [TIER0_DIR, TIER1_DIR]:
        for json_file in tier_dir.glob("*.json"):
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)
            category = json_file.stem
            for case in data.get("cases", []):
                case["_category_file"] = category
                case["_source_file"] = str(json_file)
                cases.append(case)
    return cases


# Load cases once at module level for efficiency
ALL_CASES = load_all_cases()


class TestDataFileParsing:
    """Tests that data files parse correctly."""

    def test_all_tier0_files_parse(self):
        """All 4 tier0 JSON files load without error."""
        tier0_files = list(TIER0_DIR.glob("*.json"))
        assert len(tier0_files) == 4, f"Expected 4 tier0 files, found {len(tier0_files)}"
        for json_file in tier0_files:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)
            assert "cases" in data, f"{json_file.name} missing 'cases' key"
            assert len(data["cases"]) > 0, f"{json_file.name} has empty cases array"

    def test_all_tier1_files_parse(self):
        """All 4 tier1 JSON files load without error."""
        tier1_files = list(TIER1_DIR.glob("*.json"))
        assert len(tier1_files) == 4, f"Expected 4 tier1 files, found {len(tier1_files)}"
        for json_file in tier1_files:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)
            assert "cases" in data, f"{json_file.name} missing 'cases' key"
            assert len(data["cases"]) > 0, f"{json_file.name} has empty cases array"


class TestCaseUniqueness:
    """Tests for ID uniqueness across all data."""

    def test_no_duplicate_ids(self):
        """No duplicate case IDs across ALL files (tier0+tier1)."""
        seen_ids = {}
        duplicates = []
        for case in ALL_CASES:
            case_id = case["id"]
            if case_id in seen_ids:
                duplicates.append(
                    f"Duplicate ID '{case_id}' in {case['_source_file']} "
                    f"(first seen in {seen_ids[case_id]})"
                )
            else:
                seen_ids[case_id] = case.get("_source_file", "unknown")
        assert duplicates == [], f"Found duplicate IDs:\n" + "\n".join(duplicates)


class TestRequiredFields:
    """Tests for required field presence."""

    def test_all_cases_have_required_fields(self):
        """Every case has id, query, contexts, expected_mode."""
        missing = []
        required = ["id", "query", "contexts", "expected_mode"]
        for case in ALL_CASES:
            for field in required:
                if field not in case:
                    missing.append(f"Case {case.get('id', 'UNKNOWN')}: missing '{field}'")
        assert missing == [], f"Missing required fields:\n" + "\n".join(missing)

    def test_all_cases_have_category(self):
        """Every case has category field."""
        missing = []
        for case in ALL_CASES:
            if "category" not in case:
                missing.append(f"Case {case.get('id', 'UNKNOWN')}: missing 'category'")
        assert missing == [], f"Missing category field:\n" + "\n".join(missing)

    def test_all_cases_have_evaluation_config(self):
        """Every case has evaluation_config field."""
        missing = []
        for case in ALL_CASES:
            if "evaluation_config" not in case:
                missing.append(f"Case {case.get('id', 'UNKNOWN')}: missing 'evaluation_config'")
        assert missing == [], f"Missing evaluation_config:\n" + "\n".join(missing)

    def test_all_cases_have_classification(self):
        """Every case has domain and query_type fields."""
        missing = []
        for case in ALL_CASES:
            if "domain" not in case:
                missing.append(f"Case {case.get('id', 'UNKNOWN')}: missing 'domain'")
            if "query_type" not in case:
                missing.append(f"Case {case.get('id', 'UNKNOWN')}: missing 'query_type'")
        assert missing == [], f"Missing classification fields:\n" + "\n".join(missing)


class TestFieldValues:
    """Tests for valid field values."""

    def test_valid_expected_modes(self):
        """All expected_mode values in VALID_MODES."""
        invalid = []
        for case in ALL_CASES:
            mode = case.get("expected_mode", "")
            if mode not in VALID_MODES:
                invalid.append(f"Case {case.get('id', 'UNKNOWN')}: invalid mode '{mode}'")
        assert invalid == [], f"Invalid expected_mode values:\n" + "\n".join(invalid)

    def test_valid_domains(self):
        """All domain values in VALID_DOMAINS."""
        invalid = []
        for case in ALL_CASES:
            domain = case.get("domain", "")
            if domain and domain not in VALID_DOMAINS:
                invalid.append(f"Case {case.get('id', 'UNKNOWN')}: invalid domain '{domain}'")
        assert invalid == [], f"Invalid domain values:\n" + "\n".join(invalid)

    def test_valid_query_types(self):
        """All query_type values in VALID_QUERY_TYPES."""
        invalid = []
        for case in ALL_CASES:
            qt = case.get("query_type", "")
            if qt and qt not in VALID_QUERY_TYPES:
                invalid.append(f"Case {case.get('id', 'UNKNOWN')}: invalid query_type '{qt}'")
        assert invalid == [], f"Invalid query_type values:\n" + "\n".join(invalid)

    def test_valid_reasoning_types(self):
        """All reasoning_type values in VALID_REASONING_TYPES."""
        invalid = []
        for case in ALL_CASES:
            rt = case.get("reasoning_type", "")
            if rt and rt not in VALID_REASONING_TYPES:
                invalid.append(
                    f"Case {case.get('id', 'UNKNOWN')}: invalid reasoning_type '{rt}'"
                )
        assert invalid == [], f"Invalid reasoning_type values:\n" + "\n".join(invalid)

    def test_valid_evidence_patterns(self):
        """All evidence_pattern values in VALID_EVIDENCE_PATTERNS."""
        invalid = []
        for case in ALL_CASES:
            ep = case.get("evidence_pattern", "")
            if ep and ep not in VALID_EVIDENCE_PATTERNS:
                invalid.append(
                    f"Case {case.get('id', 'UNKNOWN')}: invalid evidence_pattern '{ep}'"
                )
        assert invalid == [], f"Invalid evidence_pattern values:\n" + "\n".join(invalid)


class TestCategorySpecificFields:
    """Tests for category-specific required fields."""

    def test_trustworthy_cases_with_grounding_subcategory_have_forbidden_claims(self):
        """Cases with grounding_ subcategory prefix have non-empty forbidden_claims."""
        missing = []
        for case in ALL_CASES:
            subcat = case.get("subcategory", "")
            if subcat.startswith("grounding_"):
                fc = case.get("forbidden_claims", [])
                if not fc:
                    missing.append(f"Case {case.get('id', 'UNKNOWN')}: empty forbidden_claims")
        assert missing == [], f"Grounding subcategory cases missing forbidden_claims:\n" + "\n".join(missing)

    def test_trustworthy_cases_with_relevance_subcategory_have_required_elements(self):
        """Cases with relevance_ subcategory prefix have non-empty required_elements."""
        missing = []
        for case in ALL_CASES:
            subcat = case.get("subcategory", "")
            if subcat.startswith("relevance_"):
                re_list = case.get("required_elements", [])
                if not re_list:
                    missing.append(f"Case {case.get('id', 'UNKNOWN')}: empty required_elements")
        assert missing == [], f"Relevance subcategory cases missing required_elements:\n" + "\n".join(missing)


class TestContextConsistency:
    """Tests for context-related consistency."""

    def test_context_count_matches(self):
        """context_count matches len(contexts) where set and >0."""
        mismatches = []
        for case in ALL_CASES:
            context_count = case.get("context_count", 0)
            if context_count and context_count > 0:
                actual = len(case.get("contexts", []))
                if context_count != actual:
                    mismatches.append(
                        f"Case {case.get('id', 'UNKNOWN')}: "
                        f"context_count={context_count} but len(contexts)={actual}"
                    )
        assert mismatches == [], f"Context count mismatches:\n" + "\n".join(mismatches)
