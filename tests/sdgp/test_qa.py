"""Tests for V7 QA audit helpers."""

from __future__ import annotations

from typing import Any

from fitz_gov.sdgp.qa import (
    assign_query_grouped_splits,
    blind_label_queue_rows,
    duplicate_summary,
    rows_from_cases,
    split_summary,
)


def _case(
    case_id: str,
    query: str,
    label: str,
    *,
    context: str = "shared context",
    version: str = "v7",
) -> dict[str, Any]:
    return {
        "id": case_id,
        "input": {
            "query": query,
            "contexts": [{"id": "ctx_001", "text": context}],
        },
        "governance": {"classification": label},
        "taxonomy": {
            "cell_id": "direct_answer__science_medicine__easy",
            "pattern": "direct_answer",
        },
        "meta": {"dataset_version": version, "difficulty": "easy"},
    }


def test_duplicate_summary_counts_exact_query_and_cross_label_groups() -> None:
    rows = rows_from_cases(
        [
            _case("a", "Same query?", "TRUSTWORTHY", context="ctx a"),
            _case("b", "  same   query? ", "ABSTAIN", context="ctx b"),
            _case("c", "Different query?", "ABSTAIN", context="ctx c"),
        ]
    )

    summary = duplicate_summary(rows)

    assert summary["duplicate_ids"]["groups"] == 0
    assert summary["duplicate_exact_input"]["groups"] == 0
    assert summary["exact_query_duplicates"]["groups"] == 1
    assert summary["exact_query_duplicates"]["rows"] == 2
    assert summary["cross_label_query_duplicates"]["groups"] == 1
    assert summary["cross_label_query_duplicates"]["rows"] == 2


def test_query_grouped_split_assignments_have_zero_query_leakage() -> None:
    cases = []
    for idx in range(20):
        # Ten duplicate-query groups, two rows per group.
        cases.append(_case(f"a{idx}", f"Query {idx // 2}", "ABSTAIN", context=f"a {idx}"))
    rows = rows_from_cases(cases)

    assignments = assign_query_grouped_splits(rows, seed=7)
    summary = split_summary(rows, assignments)

    assert set(assignments) == {case["id"] for case in cases}
    assert summary["query_group_leakage"]["groups"] == 0


def test_blind_label_queue_omits_gold_label_and_taxonomy() -> None:
    case = _case("a", "Can this be answered?", "TRUSTWORTHY")

    [row] = blind_label_queue_rows([case])

    assert row["case_id"] == "a"
    assert "gold_label" not in row
    assert "label" not in row
    assert "taxonomy" not in row
    assert row["input"]["query"] == "Can this be answered?"
    assert row["input"]["contexts"][0]["text"] == "shared context"
