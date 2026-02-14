# tests/test_cli.py
"""
Tests for fitz_gov/cli.py - CLI commands.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


def run_cli(*args, timeout=120):
    """Run fitz-gov CLI command and return the CompletedProcess."""
    result = subprocess.run(
        [sys.executable, "-m", "fitz_gov.cli", *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result


class TestCLIStats:
    """Tests for the stats command."""

    def test_cli_stats_runs(self):
        """stats command exits 0."""
        result = run_cli("stats", "--data-dir", "data")
        assert result.returncode == 0, f"stats failed with stderr: {result.stderr}"

    def test_cli_stats_output(self):
        """Output contains 'Total cases:'."""
        result = run_cli("stats", "--data-dir", "data")
        assert "Total cases:" in result.stdout, f"Expected 'Total cases:' in output: {result.stdout}"

    def test_cli_stats_verbose(self):
        """-v flag shows more detail (tiered structure shows tier info)."""
        result = run_cli("stats", "--data-dir", "data", "-v")
        assert result.returncode == 0, f"stats -v failed with stderr: {result.stderr}"
        # Verbose mode should still show total cases and the tiered structure
        assert "Total cases:" in result.stdout


class TestCLIValidate:
    """Tests for the validate command."""

    def test_cli_validate_runs(self, tmp_path):
        """validate exits (may be 0 or 1) when run against a small data set.

        Uses a tiny temporary data directory with just a few cases so the
        validation (including Ollama-based semantic duplicate detection)
        completes quickly regardless of whether Ollama is running.
        """
        # Build a minimal tiered data directory with 2 cases
        tier0_dir = tmp_path / "tier0_sanity"
        tier0_dir.mkdir()

        minimal_data = {
            "tier": "sanity",
            "category": "abstention",
            "cases": [
                {
                    "id": "test_001",
                    "query": "What is the revenue for Q4 2024?",
                    "contexts": ["Biology context about cells."],
                    "expected_mode": "abstain",
                    "description": "Test case 1",
                    "rationale": "Irrelevant context",
                    "category": "abstention",
                    "evaluation_config": {"mode": "governance"},
                },
                {
                    "id": "test_002",
                    "query": "Who won the 2024 Super Bowl?",
                    "contexts": ["History of the French Revolution."],
                    "expected_mode": "abstain",
                    "description": "Test case 2",
                    "rationale": "Wrong domain",
                    "category": "abstention",
                    "evaluation_config": {"mode": "governance"},
                },
            ],
        }

        with open(tier0_dir / "abstention.json", "w", encoding="utf-8") as f:
            json.dump(minimal_data, f)

        result = run_cli("validate", "--data-dir", str(tmp_path), timeout=120)

        # validate may exit 0 (all clean) or 1 (issues found), both are valid runs
        assert result.returncode in (0, 1), (
            f"validate exited with unexpected code {result.returncode}. "
            f"stderr: {result.stderr}"
        )
        # Should produce some output about case loading
        combined = result.stdout + result.stderr
        assert "Loaded" in combined or "cases" in combined.lower(), (
            f"Expected validation output, got: {combined}"
        )


class TestCLINoCommand:
    """Tests for running CLI with no arguments."""

    def test_cli_no_command(self):
        """No args shows help text."""
        result = run_cli()
        combined = result.stdout + result.stderr
        # argparse prints help to stdout or stderr depending on version
        assert "fitz-gov" in combined.lower() or "usage" in combined.lower(), (
            f"Expected help text, got: {combined}"
        )
