"""
Tests for formatter modules.
"""

import json
from datetime import datetime
from unittest import mock

import pytest

# Import get_formatter from the main CLI module where it's defined
from src_check.cli.main import get_formatter
from src_check.formatters.json import JsonFormatter
from src_check.formatters.markdown import MarkdownFormatter
from src_check.formatters.text import TextFormatter
from src_check.models import CheckResult, FileResults, KPIScore, SimpleKPIScore


@pytest.fixture
def sample_check_results():
    """Create sample check results for testing."""
    return {
        "test.py": [
            CheckResult(
                checker_name="security",
                severity="critical",
                category="security",
                rule="hardcoded_secret",
                message="Hardcoded secret found",
                file_path="test.py",
                line_number=10,
                column_number=5,
                context="password = '12345'",
                fix_suggestion="Use environment variables for secrets",
            ),
            CheckResult(
                checker_name="code_quality",
                severity="warning",
                category="code_quality",
                rule="unused_variable",
                message="Unused variable 'x'",
                file_path="test.py",
                line_number=20,
                column_number=1,
                context="x = 5",
                fix_suggestion="Remove unused variable",
            ),
        ],
        "utils.py": [
            CheckResult(
                checker_name="type_hints",
                severity="info",
                category="type_hints",
                rule="missing_type_hint",
                message="Missing type hint for parameter 'data'",
                file_path="utils.py",
                line_number=5,
                column_number=10,
                context="def process(data):",
                fix_suggestion="Add type hint: data: Any",
            )
        ],
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
        critical_issues=1,
        warning_issues=1,
        info_issues=1,
    )


class TestTextFormatter:
    """Test TextFormatter functionality."""

    def test_format_basic(self, sample_check_results, sample_kpi_score):
        """Test basic text formatting."""
        formatter = TextFormatter()
        output = formatter.format(sample_check_results, sample_kpi_score)

        # Check basic structure
        assert "src-check Results" in output
        assert "KPI Score Summary" in output
        assert "Overall Score: 75.5/100" in output
        assert "Critical Issues: 1" in output
        assert "Warning Issues: 1" in output
        assert "Info Issues: 1" in output

        # Check category scores
        assert "Security: 60.0/100" in output
        assert "Code Quality: 80.0/100" in output
        assert "Type Hints: 85.0/100" in output

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
            critical_issues=0,
            warning_issues=0,
            info_issues=0,
        )
        output = formatter.format({}, kpi_score)

        assert "No issues found" in output
        assert "Overall Score: 100.0/100" in output

    def test_format_single_result(self, sample_check_results, sample_kpi_score):
        """Test formatting a single result."""
        formatter = TextFormatter()
        result = sample_check_results["test.py"][0]
        output = formatter.format_result(result)

        assert "[CRITICAL]" in output
        assert "security:hardcoded_secret" in output
        assert "Hardcoded secret found" in output
        assert "Line 10, Column 5" in output
        assert "password = '12345'" in output
        assert "Fix: Use environment variables for secrets" in output


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
        assert "summary" in data

        # Check metadata
        assert data["metadata"]["tool"] == "src-check"
        assert "timestamp" in data["metadata"]

        # Check KPI score
        assert data["kpi_score"]["overall_score"] == 75.5
        assert data["kpi_score"]["critical_issues"] == 1
        assert data["kpi_score"]["warning_issues"] == 1
        assert data["kpi_score"]["info_issues"] == 1

        # Check results
        assert "test.py" in data["results"]
        assert len(data["results"]["test.py"]) == 2
        assert "utils.py" in data["results"]
        assert len(data["results"]["utils.py"]) == 1

        # Check summary
        assert data["summary"]["total_files"] == 2
        assert data["summary"]["total_issues"] == 3

    def test_format_empty_results(self):
        """Test JSON formatting with no issues."""
        formatter = JsonFormatter()
        kpi_score = SimpleKPIScore(
            overall_score=100.0,
            category_scores={},
            critical_issues=0,
            warning_issues=0,
            info_issues=0,
        )
        output = formatter.format({}, kpi_score)

        data = json.loads(output)
        assert data["results"] == {}
        assert data["summary"]["total_files"] == 0
        assert data["summary"]["total_issues"] == 0


class TestMarkdownFormatter:
    """Test MarkdownFormatter functionality."""

    def test_format_basic(self, sample_check_results, sample_kpi_score):
        """Test basic Markdown formatting."""
        formatter = MarkdownFormatter()
        output = formatter.format(sample_check_results, sample_kpi_score)

        # Check headers
        assert "# src-check Analysis Report" in output
        assert "## KPI Score Summary" in output
        assert "## Category Scores" in output
        assert "## Issues by File" in output

        # Check KPI info
        assert "**Overall Score:** 75.5/100" in output
        assert "- **Critical Issues:** 1" in output
        assert "- **Warning Issues:** 1" in output
        assert "- **Info Issues:** 1" in output

        # Check tables
        assert "| Category | Score |" in output
        assert "| Security | 60.0/100 |" in output
        assert "| Code Quality | 80.0/100 |" in output
        assert "| Type Hints | 85.0/100 |" in output

        # Check file sections
        assert "### test.py" in output
        assert "### utils.py" in output

        # Check issue formatting
        assert "#### 🔴 CRITICAL" in output
        assert "**Rule:** `security:hardcoded_secret`" in output
        assert "**Location:** Line 10, Column 5" in output

    def test_format_empty_results(self):
        """Test Markdown formatting with no issues."""
        formatter = MarkdownFormatter()
        kpi_score = SimpleKPIScore(
            overall_score=100.0,
            category_scores={},
            critical_issues=0,
            warning_issues=0,
            info_issues=0,
        )
        output = formatter.format({}, kpi_score)

        assert "✅ No issues found!" in output
        assert "**Overall Score:** 100.0/100" in output

    def test_severity_emoji_mapping(self):
        """Test severity to emoji mapping."""
        formatter = MarkdownFormatter()
        assert formatter._get_severity_emoji("critical") == "🔴"
        assert formatter._get_severity_emoji("warning") == "🟡"
        assert formatter._get_severity_emoji("info") == "🔵"
        assert formatter._get_severity_emoji("unknown") == "⚪"


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