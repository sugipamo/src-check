"""
Tests specifically designed to improve test coverage to 70%+.
Focus on modules with 0% coverage.
"""

from pathlib import Path
from unittest import mock

import pytest


# Test simple_kpi_score module
def test_simple_kpi_score():
    """Test the SimpleKPIScore model."""
    from src_check.models.simple_kpi_score import KpiScore

    score = KpiScore(
        overall_score=85.5,
        category_scores={"security": 90.0, "code_quality": 80.0},
        total_issues=10,
        critical_issues=1,
        high_issues=2,
        medium_issues=3,
        low_issues=4,
    )

    assert score.overall_score == 85.5
    assert score.category_scores["security"] == 90.0
    assert score.total_issues == 10


# Test formatters __init__
def test_base_formatter():
    """Test the BaseFormatter ABC."""
    from src_check.formatters import BaseFormatter

    # Test that it's abstract
    with pytest.raises(TypeError, match="abstract"):
        BaseFormatter()  # type: ignore[abstract]

    # Create a concrete implementation
    class TestFormatter(BaseFormatter):
        def format(self, results, kpi):
            return "test"

    formatter = TestFormatter()
    assert formatter.format({}, None) == "test"


# Test text formatter basics
def test_text_formatter_basic():
    """Test basic TextFormatter functionality."""
    from src_check.formatters.text import TextFormatter
    from src_check.models.simple_kpi_score import KpiScore

    formatter = TextFormatter()
    kpi = KpiScore(
        overall_score=100.0,
        category_scores={},
        total_issues=0,
        critical_issues=0,
        high_issues=0,
        medium_issues=0,
        low_issues=0,
    )

    # Just test that it doesn't crash
    output = formatter.format({}, kpi)
    assert isinstance(output, str)
    assert "SRC-CHECK" in output


# Test json formatter basics
def test_json_formatter_basic():
    """Test basic JsonFormatter functionality."""
    import json

    from src_check.formatters.json import JsonFormatter
    from src_check.models.simple_kpi_score import KpiScore

    formatter = JsonFormatter()
    kpi = KpiScore(
        overall_score=100.0,
        category_scores={},
        total_issues=0,
        critical_issues=0,
        high_issues=0,
        medium_issues=0,
        low_issues=0,
    )

    output = formatter.format({}, kpi)
    # Should be valid JSON
    data = json.loads(output)
    assert "kpi_score" in data


# Test markdown formatter basics
def test_markdown_formatter_basic():
    """Test basic MarkdownFormatter functionality."""
    from src_check.formatters.markdown import MarkdownFormatter
    from src_check.models.simple_kpi_score import KpiScore

    formatter = MarkdownFormatter()
    kpi = KpiScore(
        overall_score=100.0,
        category_scores={},
        total_issues=0,
        critical_issues=0,
        high_issues=0,
        medium_issues=0,
        low_issues=0,
    )

    output = formatter.format({}, kpi)
    assert isinstance(output, str)
    assert "# src-check" in output


# Test config loader basics
def test_config_loader_basic():
    """Test basic ConfigLoader functionality."""
    from src_check.core.config_loader import ConfigLoader

    loader = ConfigLoader()
    # Test loading default config
    config = loader.load_default_config()
    assert config is not None
    assert hasattr(config, "version")


# Test engine initialization
def test_engine_basic():
    """Test basic AnalysisEngine functionality."""
    from src_check.core.engine import AnalysisEngine

    # Test with empty checkers
    engine = AnalysisEngine([])
    assert engine.checkers == []

    # Test file ignore logic
    assert engine._should_ignore_file(Path("__pycache__/test.pyc"))
    assert not engine._should_ignore_file(Path("main.py"))


# Test KPI calculator basics
def test_kpi_calculator_basic():
    """Test basic KPICalculator functionality."""
    from src_check.core.kpi_calculator import KPICalculator

    calculator = KPICalculator()
    # Test empty project
    score = calculator.calculate_project_score({})
    assert score.overall_score == 100.0


# Test registry basics
def test_registry_basic():
    """Test basic registry functionality."""
    from src_check.core.registry import registry

    # Test that registry has checkers
    registry.discover_plugins()
    checkers = registry.list_checkers()
    assert len(checkers) > 0
    assert "SecurityChecker" in checkers


# Test CLI parse_args
def test_cli_parse_args_basic():
    """Test CLI argument parsing."""
    from src_check.cli.main import parse_args

    with mock.patch("sys.argv", ["src-check"]):
        args = parse_args()
        assert args.paths == ["."]
        assert args.format == "text"


# Test KPI CLI parse_args
def test_kpi_cli_parse_args_basic():
    """Test KPI CLI argument parsing."""
    from src_check.cli.kpi import parse_args

    with mock.patch("sys.argv", ["src-check-kpi"]):
        args = parse_args()
        assert args.paths == ["."]
        assert args.format == "text"
