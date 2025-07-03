"""
Simple unit tests for formatter modules to improve coverage.
"""

import json

import pytest

from src_check.formatters.json import JsonFormatter
from src_check.formatters.markdown import MarkdownFormatter
from src_check.formatters.text import TextFormatter
from src_check.models import CheckResult, Severity
from src_check.models.simple_kpi_score import KpiScore as SimpleKPIScore


@pytest.fixture
def sample_results():
    """Create sample check results."""
    result = CheckResult(
        title="Hardcoded Secret",
        checker_name="security",
        severity=Severity.CRITICAL,
        category="security",
        rule_id="hardcoded_secret",
        fix_policy="Use environment variables for secrets",
    )
    result.add_failure(
        file_path="test.py",
        line=10,
        column=5,
        message="Secret found: password = 'secret'",
    )
    return {"test.py": [result]}


@pytest.fixture
def sample_kpi():
    """Create sample KPI score."""
    return SimpleKPIScore(
        overall_score=75.0,
        category_scores={"security": 60.0},
        total_issues=1,
        critical_issues=1,
        high_issues=0,
        medium_issues=0,
        low_issues=0,
        warning_issues=0,
        info_issues=0,
    )


class TestTextFormatter:
    """Test TextFormatter."""

    def test_format(self, sample_results, sample_kpi):
        """Test text formatting."""
        formatter = TextFormatter()
        output = formatter.format(sample_results, sample_kpi)

        assert "SRC-CHECK ANALYSIS RESULTS" in output
        assert "test.py" in output
        assert "Secret found" in output
        assert "75.0/100" in output

    def test_format_empty(self):
        """Test formatting empty results."""
        formatter = TextFormatter()
        kpi = SimpleKPIScore(
            overall_score=100.0,
            category_scores={},
            total_issues=0,
            critical_issues=0,
            high_issues=0,
            medium_issues=0,
            low_issues=0,
        )
        output = formatter.format({}, kpi)
        assert "No issues found" in output


class TestJsonFormatter:
    """Test JsonFormatter."""

    def test_format(self, sample_results, sample_kpi):
        """Test JSON formatting."""
        formatter = JsonFormatter()
        output = formatter.format(sample_results, sample_kpi)

        data = json.loads(output)
        assert "metadata" in data
        assert "results" in data
        assert "kpi_score" in data
        assert data["kpi_score"]["overall_score"] == 75.0

    def test_format_empty(self):
        """Test formatting empty results."""
        formatter = JsonFormatter()
        kpi = SimpleKPIScore(
            overall_score=100.0,
            category_scores={},
            total_issues=0,
            critical_issues=0,
            high_issues=0,
            medium_issues=0,
            low_issues=0,
        )
        output = formatter.format({}, kpi)
        data = json.loads(output)
        assert data["results"] == {}


class TestMarkdownFormatter:
    """Test MarkdownFormatter."""

    def test_format(self, sample_results, sample_kpi):
        """Test Markdown formatting."""
        formatter = MarkdownFormatter()
        output = formatter.format(sample_results, sample_kpi)

        assert "# src-check Analysis Report" in output
        assert "## Executive Summary" in output
        assert "**Overall Score**: 75.0/100" in output
        assert "`test.py`" in output

    def test_format_empty(self):
        """Test formatting empty results."""
        formatter = MarkdownFormatter()
        kpi = SimpleKPIScore(
            overall_score=100.0,
            category_scores={},
            total_issues=0,
            critical_issues=0,
            high_issues=0,
            medium_issues=0,
            low_issues=0,
        )
        output = formatter.format({}, kpi)
        assert "100.0/100" in output
