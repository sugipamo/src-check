"""
Simple unit tests for CLI modules to improve coverage.
"""

from unittest import mock

import pytest

from src_check.cli.kpi import parse_args as parse_kpi_args
from src_check.cli.main import get_formatter, parse_args, setup_logging, validate_paths
from src_check.formatters.json import JsonFormatter
from src_check.formatters.text import TextFormatter


class TestMainCLI:
    """Test main CLI functions."""

    def test_parse_args_defaults(self):
        """Test parse_args with defaults."""
        with mock.patch("sys.argv", ["src-check"]):
            args = parse_args()
            assert args.paths == ["."]
            assert args.format == "text"

    def test_parse_args_custom(self):
        """Test parse_args with custom values."""
        with mock.patch("sys.argv", ["src-check", "src/", "--format", "json"]):
            args = parse_args()
            assert args.paths == ["src/"]
            assert args.format == "json"

    def test_get_formatter_text(self):
        """Test getting text formatter."""
        formatter = get_formatter("text")
        assert isinstance(formatter, TextFormatter)

    def test_get_formatter_json(self):
        """Test getting JSON formatter."""
        formatter = get_formatter("json")
        assert isinstance(formatter, JsonFormatter)

    def test_setup_logging(self):
        """Test setup_logging function."""
        with mock.patch("logging.basicConfig") as mock_config:
            setup_logging(True)
            mock_config.assert_called_once()

    def test_validate_paths(self):
        """Test validate_paths function."""
        # Test with current directory
        paths = validate_paths(["."])
        assert len(paths) == 1
        assert paths[0].is_dir()

        # Test with non-existent path
        with pytest.raises(SystemExit):
            validate_paths(["non_existent_path"])


class TestKPICLI:
    """Test KPI CLI functions."""

    def test_parse_kpi_args_defaults(self):
        """Test parse_args with defaults."""
        with mock.patch("sys.argv", ["src-check-kpi"]):
            args = parse_kpi_args()
            assert args.paths == ["."]
            assert args.format == "text"

    def test_parse_kpi_args_custom(self):
        """Test parse_args with custom values."""
        with mock.patch(
            "sys.argv",
            ["src-check-kpi", "src/", "--checkers", "security", "performance"],
        ):
            args = parse_kpi_args()
            assert args.paths == ["src/"]
            assert args.checkers == ["security", "performance"]
