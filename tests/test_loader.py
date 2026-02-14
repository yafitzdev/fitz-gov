"""Tests for fitz_gov.loader."""

import pytest
from pathlib import Path

from fitz_gov.loader import (
    Tier,
    load_tier,
    load_cases,
    load_case_by_id,
    get_tier_info,
    get_category_info,
)
from fitz_gov.models import FitzGovCategory


# ---------------------------------------------------------------------------
# Tier enum
# ---------------------------------------------------------------------------


class TestTierEnum:
    def test_tier_enum(self):
        """Tier.SANITY.value == 'tier0_sanity', Tier.CORE.value == 'tier1_core'."""
        assert Tier.SANITY.value == "tier0_sanity"
        assert Tier.CORE.value == "tier1_core"
        assert len(Tier) == 2


# ---------------------------------------------------------------------------
# load_tier
# ---------------------------------------------------------------------------


class TestLoadTier:
    def test_load_tier0(self, data_dir):
        """load_tier(Tier.SANITY) returns 60 cases."""
        cases = load_tier(Tier.SANITY, data_dir=data_dir)
        assert len(cases) == 60

    def test_load_tier1(self, data_dir):
        """load_tier(Tier.CORE) returns 2083 cases."""
        cases = load_tier(Tier.CORE, data_dir=data_dir)
        assert len(cases) == 2428

    def test_load_tier0_categories(self, data_dir):
        """All 6 categories present in tier0."""
        cases = load_tier(Tier.SANITY, data_dir=data_dir)
        categories = {c.category for c in cases}
        assert categories == set(FitzGovCategory)

    def test_load_tier1_categories(self, data_dir):
        """All 6 categories present in tier1."""
        cases = load_tier(Tier.CORE, data_dir=data_dir)
        categories = {c.category for c in cases}
        assert categories == set(FitzGovCategory)

    def test_load_tier_filter_category(self, data_dir):
        """Filtering by single category works."""
        cases = load_tier(
            Tier.SANITY,
            categories=[FitzGovCategory.ABSTENTION],
            data_dir=data_dir,
        )
        assert len(cases) > 0
        assert all(c.category == FitzGovCategory.ABSTENTION for c in cases)


# ---------------------------------------------------------------------------
# load_cases
# ---------------------------------------------------------------------------


class TestLoadCases:
    def test_load_cases_all(self, data_dir):
        """load_cases() returns tier0+tier1 combined."""
        cases = load_cases(data_dir=data_dir)
        assert len(cases) == 60 + 2428

    def test_load_cases_tier_filter(self, data_dir):
        """load_cases(tiers=[Tier.SANITY]) only returns tier0."""
        cases = load_cases(tiers=[Tier.SANITY], data_dir=data_dir)
        assert len(cases) == 60


# ---------------------------------------------------------------------------
# load_case_by_id
# ---------------------------------------------------------------------------


class TestLoadCaseById:
    def test_load_case_by_id_tier0(self, data_dir):
        """Finds a t0_ case by ID."""
        case = load_case_by_id("t0_abstain_easy_001", data_dir=data_dir)
        assert case is not None
        assert case.id == "t0_abstain_easy_001"
        assert case.category == FitzGovCategory.ABSTENTION

    def test_load_case_by_id_tier1(self, data_dir):
        """Finds a t1_ case by ID."""
        case = load_case_by_id("t1_abstain_hard_001", data_dir=data_dir)
        assert case is not None
        assert case.id == "t1_abstain_hard_001"
        assert case.category == FitzGovCategory.ABSTENTION

    def test_load_case_by_id_missing(self, data_dir):
        """Returns None for nonexistent ID."""
        case = load_case_by_id("nonexistent_id_999", data_dir=data_dir)
        assert case is None


# ---------------------------------------------------------------------------
# Case field integrity
# ---------------------------------------------------------------------------


class TestCaseIntegrity:
    def test_case_has_category(self, data_dir):
        """Every loaded case has category field set."""
        cases = load_tier(Tier.SANITY, data_dir=data_dir)
        for case in cases:
            assert case.category is not None
            assert isinstance(case.category, FitzGovCategory)

    def test_case_has_classification(self, data_dir):
        """Every case has domain, query_type, etc."""
        cases = load_tier(Tier.SANITY, data_dir=data_dir)
        for case in cases:
            assert case.domain, f"Case {case.id} missing domain"
            assert case.query_type, f"Case {case.id} missing query_type"
            assert case.source_type, f"Case {case.id} missing source_type"
            assert case.context_count > 0, f"Case {case.id} missing context_count"
            assert case.reasoning_type, f"Case {case.id} missing reasoning_type"
            assert case.evidence_pattern, f"Case {case.id} missing evidence_pattern"


# ---------------------------------------------------------------------------
# Metadata / info functions
# ---------------------------------------------------------------------------


class TestInfoFunctions:
    def test_get_tier_info(self, data_dir):
        """Returns info for both tiers."""
        info = get_tier_info(data_dir=data_dir)

        assert Tier.SANITY.value in info
        assert Tier.CORE.value in info
        assert info[Tier.SANITY.value]["total_cases"] == 60
        assert info[Tier.CORE.value]["total_cases"] == 2428

    def test_get_category_info(self, data_dir):
        """Returns info for all 6 categories."""
        info = get_category_info(data_dir=data_dir)

        assert len(info) == 6
        for cat in FitzGovCategory:
            assert cat.value in info, f"Missing category: {cat.value}"
            assert info[cat.value]["case_count"] > 0
