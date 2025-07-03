"""
Tests for formatter modules.
"""

import json

import pytest

# Import get_formatter from the main CLI module where it's defined
from src_check.cli.main import get_formatter
from src_check.formatters.json import JsonFormatter
from src_check.formatters.markdown import MarkdownFormatter
from src_check.formatters.text import TextFormatter
from src_check.models import CheckResult, Severity
from src_check.models.simple_kpi_score import KpiScore as SimpleKPIScore


@pytest.fixture
def sample_check_results():
    """Create sample check results for testing."""
    result1 = CheckResult(
        title="Hardcoded secret found",
        checker_name="security",
        severity=Severity.CRITICAL,
        category="security",
        rule_id="hardcoded_secret",
        metadata={
            "context": "password = '12345'",
            "fix_suggestion": "Use environment variables for secrets",
        },
    )
    result1.add_failure(
        "test.py",
        10,
        "Hardcoded secret found",
        column=5,
        code_snippet="password = '12345'",
    )

    result2 = CheckResult(
        title="Unused variable 'x'",
        checker_name="code_quality",
        severity=Severity.MEDIUM,
        category="code_quality",
        rule_id="unused_variable",
        metadata={
            "context": "x = 5",
            "fix_suggestion": "Remove unused variable",
        },
    )
    result2.add_failure(
        "test.py", 20, "Unused variable 'x'", column=1, code_snippet="x = 5"
    )

    result3 = CheckResult(
        title="Missing type hint for parameter 'data'",
        checker_name="type_hints",
        severity=Severity.INFO,
        category="type_hints",
        rule_id="missing_type_hint",
        metadata={
            "context": "def process(data):",
            "fix_suggestion": "Add type hint: data: Any",
        },
    )
    result3.add_failure(
        "utils.py",
        5,
        "Missing type hint for parameter 'data'",
        column=10,
        code_snippet="def process(data):",
    )

    return {
        "test.py": [result1, result2],
        "utils.py": [result3],
    }


@pytest.fixture
def sample_kpi_score():
    """Create sample KPI score for testing."""
    return SimpleKPIScore(
        overall_score=75.5,
        category_scores={
            "security": 60.0,
            "code_quality": 80.0,
            "type_hints": 85.0,
        },
        total_issues=3,
        critical_issues=1,
        high_issues=0,
        medium_issues=1,
        low_issues=1,
    )


class TestTextFormatter:
    """Test TextFormatter functionality."""

    def test_format_basic(self, sample_check_results, sample_kpi_score):
        """Test basic text formatting."""
        formatter = TextFormatter()
        output = formatter.format(sample_check_results, sample_kpi_score)

        # Check basic structure
        assert "SRC-CHECK ANALYSIS RESULTS" in output
        assert "OVERALL SCORE: 75.5/100" in output
        assert "critical: 1" in output
        assert "medium: 1" in output

        # Check category scores
        assert "security" in output and "60.0/100" in output
        assert "code_quality" in output and "80.0/100" in output
        assert "type_hints" in output and "85.0/100" in output

        # Check issues
        assert "test.py" in output
        assert "Hardcoded secret found" in output
        assert "Unused variable 'x'" in output
        assert "utils.py" in output
        assert "Missing type hint for parameter 'data'" in output

    def test_format_empty_results(self):
        """Test formatting with no issues."""
        formatter = TextFormatter()
        kpi_score = SimpleKPIScore(
            overall_score=100.0,
            category_scores={},
            total_issues=0,
            critical_issues=0,
            high_issues=0,
            medium_issues=0,
            low_issues=0,
        )
        output = formatter.format({}, kpi_score)

        assert "No issues found" in output or "OVERALL SCORE: 100.0/100" in output

    def test_format_single_result(self, sample_check_results, sample_kpi_score):
        """Test formatting a single result."""
        formatter = TextFormatter()
        result = sample_check_results["test.py"][0]
        output = formatter._format_result(result)

        assert "critical" in output.lower()
        assert "Hardcoded secret found" in output
        assert "Line 10" in output


class TestJsonFormatter:
    """Test JsonFormatter functionality."""

    def test_format_basic(self, sample_check_results, sample_kpi_score):
        """Test basic JSON formatting."""
        formatter = JsonFormatter()
        output = formatter.format(sample_check_results, sample_kpi_score)

        # Parse JSON
        data = json.loads(output)

        # Check structure
        assert "metadata" in data
        assert "kpi_score" in data
        assert "results" in data
        assert "files" in data

        # Check metadata
        assert data["metadata"]["version"] == "0.2.0"
        assert "timestamp" in data["metadata"]

        # Check KPI score
        assert data["kpi_score"]["overall_score"] == 75.5
        assert data["kpi_score"]["critical_issues"] == 1
        assert data["kpi_score"]["medium_issues"] == 1
        assert data["kpi_score"]["low_issues"] == 1

        # Check results
        assert "test.py" in data["results"]
        assert len(data["results"]["test.py"]) == 2
        assert "utils.py" in data["results"]
        assert len(data["results"]["utils.py"]) == 1

        # Check KPI totals
        assert data["kpi_score"]["total_issues"] == 3

    def test_format_empty_results(self):
        """Test JSON formatting with no issues."""
        formatter = JsonFormatter()
        kpi_score = SimpleKPIScore(
            overall_score=100.0,
            category_scores={},
            total_issues=0,
            critical_issues=0,
            high_issues=0,
            medium_issues=0,
            low_issues=0,
        )
        output = formatter.format({}, kpi_score)

        data = json.loads(output)
        assert data["results"] == {}
        assert data["kpi_score"]["total_issues"] == 0


class TestMarkdownFormatter:
    """Test MarkdownFormatter functionality."""

    def test_format_basic(self, sample_check_results, sample_kpi_score):
        """Test basic Markdown formatting."""
        formatter = MarkdownFormatter()
        output = formatter.format(sample_check_results, sample_kpi_score)

        # Check headers
        assert "# src-check Analysis Report" in output
        assert "## Executive Summary" in output
        assert "## Detailed Findings" in output

        # Check KPI info
        assert "**Overall Score**: 75.5/100" in output
        assert "Total Issues | 3" in output

        # Check tables
        assert "| Category | Score | Grade |" in output
        assert "Security" in output
        assert "60.0" in output

        # Check file sections
        assert "`test.py`" in output
        assert "`utils.py`" in output

        # Check issue formatting
        assert "hardcoded_secret" in output
        assert "unused_variable" in output
        assert "missing_type_hint" in output

    def test_format_empty_results(self):
        """Test Markdown formatting with no issues."""
        formatter = MarkdownFormatter()
        kpi_score = SimpleKPIScore(
            overall_score=100.0,
            category_scores={},
            total_issues=0,
            critical_issues=0,
            high_issues=0,
            medium_issues=0,
            low_issues=0,
        )
        output = formatter.format({}, kpi_score)

        assert "100.0/100" in output
        assert "Total Issues | 0" in output

    def test_severity_emoji_mapping(self):
        """Test severity to emoji mapping."""
        formatter = MarkdownFormatter()
        assert formatter._get_severity_emoji(Severity.CRITICAL) == "🔴"
        assert formatter._get_severity_emoji(Severity.MEDIUM) == "🟡"
        assert formatter._get_severity_emoji(Severity.INFO) == "ℹ️"


class TestGetFormatter:
    """Test get_formatter function."""

    def test_get_formatter_text(self):
        """Test getting text formatter."""
        formatter = get_formatter("text")
        assert isinstance(formatter, TextFormatter)

    def test_get_formatter_json(self):
        """Test getting JSON formatter."""
        formatter = get_formatter("json")
        assert isinstance(formatter, JsonFormatter)

    def test_get_formatter_markdown(self):
        """Test getting Markdown formatter."""
        formatter = get_formatter("markdown")
        assert isinstance(formatter, MarkdownFormatter)

    def test_get_formatter_unknown(self):
        """Test getting formatter with unknown format defaults to text."""
        formatter = get_formatter("unknown")
        assert isinstance(formatter, TextFormatter)
