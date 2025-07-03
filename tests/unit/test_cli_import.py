"""
Import-based tests for CLI functionality to capture proper coverage.
"""

import json
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from src_check.cli.kpi import main as kpi_main
from src_check.cli.kpi import parse_args as parse_kpi_args
from src_check.cli.main import get_formatter, main, parse_args
from src_check.formatters.json import JsonFormatter
from src_check.formatters.markdown import MarkdownFormatter
from src_check.formatters.text import TextFormatter


class TestMainCLI:
    """Test main CLI functionality using imports."""

    def test_parse_args_defaults(self):
        """Test parse_args with default values."""
        with mock.patch("sys.argv", ["src-check"]):
            args = parse_args()
            assert args.paths == ["."]
            assert args.format == "text"
            assert args.config is None
            assert args.output is None
            assert not args.verbose
            assert args.threshold is None

    def test_parse_args_custom(self):
        """Test parse_args with custom values."""
        with mock.patch(
            "sys.argv",
            [
                "src-check",
                "src/",
                "tests/",
                "--format",
                "json",
                "--config",
                "config.yaml",
                "--output",
                "results.json",
                "--verbose",
                "--disable",
                "security",
                "documentation",
                "--threshold",
                "80.0",
            ],
        ):
            args = parse_args()
            assert args.paths == ["src/", "tests/"]
            assert args.format == "json"
            assert args.config == "config.yaml"
            assert args.output == "results.json"
            assert args.verbose is True
            assert args.threshold == 80.0

    def test_get_formatter(self):
        """Test formatter selection."""
        assert isinstance(get_formatter("text"), TextFormatter)
        assert isinstance(get_formatter("json"), JsonFormatter)
        assert isinstance(get_formatter("markdown"), MarkdownFormatter)

    @mock.patch("src_check.cli.main.AnalysisEngine")
    @mock.patch("src_check.cli.main.ConfigLoader")
    def test_main_basic_execution(self, mock_config_loader, mock_engine_class):
        """Test basic execution of main CLI."""
        # Setup mocks
        mock_config = mock.Mock()
        mock_config.checkers = ["security", "code_quality"]
        mock_config.file_patterns = ["*.py"]
        mock_config.ignore_patterns = []
        mock_config.fail_on_issues = False
        mock_config_loader.load.return_value = mock_config

        mock_engine = mock.Mock()
        mock_engine_class.return_value = mock_engine
        mock_engine.analyze_file.return_value = []
        mock_engine.analyze_directory.return_value = {}

        # Run with basic args
        with mock.patch("sys.argv", ["src-check", "."]):
            with mock.patch("builtins.print"):
                result = main()
                assert result is None  # Normal exit

        # Verify calls
        mock_config_loader.load.assert_called_once()
        mock_engine_class.assert_called_once()

    @mock.patch("src_check.cli.main.AnalysisEngine")
    @mock.patch("src_check.cli.main.ConfigLoader")
    def test_main_with_threshold_failure(self, mock_config_loader, mock_engine_class):
        """Test main CLI with threshold failure."""
        # Setup mocks
        mock_config = mock.Mock()
        mock_config.checkers = ["security"]
        mock_config.file_patterns = ["*.py"]
        mock_config.ignore_patterns = []
        mock_config.fail_on_issues = False
        mock_config_loader.load.return_value = mock_config

        mock_engine = mock.Mock()
        mock_engine_class.return_value = mock_engine
        mock_engine.analyze_directory.return_value = {
            "test.py": [
                mock.Mock(
                    severity="critical",
                    category="security",
                    rule="hardcoded_secret",
                )
            ]
        }

        # Run with threshold
        with mock.patch("sys.argv", ["src-check", ".", "--threshold", "90"]):
            with mock.patch("builtins.print"):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1

    @mock.patch("src_check.cli.main.AnalysisEngine")
    @mock.patch("src_check.cli.main.ConfigLoader")
    def test_main_with_output_file(self, mock_config_loader, mock_engine_class):
        """Test main CLI with output file."""
        # Setup mocks
        mock_config = mock.Mock()
        mock_config.checkers = ["security"]
        mock_config.file_patterns = ["*.py"]
        mock_config.ignore_patterns = []
        mock_config.fail_on_issues = False
        mock_config_loader.load.return_value = mock_config

        mock_engine = mock.Mock()
        mock_engine_class.return_value = mock_engine
        mock_engine.analyze_directory.return_value = {}

        # Run with output file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            output_file = f.name

        try:
            with mock.patch(
                "sys.argv", ["src-check", ".", "--format", "json", "--output", output_file]
            ):
                with mock.patch("builtins.print"):
                    main()

            # Check output file was created
            assert Path(output_file).exists()
            with open(output_file) as f:
                data = json.load(f)
                assert "results" in data
                assert "kpi_score" in data
        finally:
            Path(output_file).unlink(missing_ok=True)


class TestKPICLI:
    """Test KPI CLI functionality using imports."""

    def test_parse_kpi_args_defaults(self):
        """Test parse_kpi_args with default values."""
        with mock.patch("sys.argv", ["src-check-kpi"]):
            args = parse_kpi_args()
            assert args.paths == ["."]
            assert args.format == "text"
            assert args.config is None
            assert not args.verbose

    def test_parse_kpi_args_custom(self):
        """Test parse_kpi_args with custom values."""
        with mock.patch(
            "sys.argv",
            [
                "src-check-kpi",
                "src/",
                "--format",
                "json",
                "--config",
                "config.yaml",
                "--verbose",
                "--checkers",
                "security",
                "performance",
            ],
        ):
            args = parse_kpi_args()
            assert args.paths == ["src/"]
            assert args.format == "json"
            assert args.config == "config.yaml"
            assert args.verbose is True
            assert args.checkers == ["security", "performance"]

    @mock.patch("src_check.cli.kpi.AnalysisEngine")
    @mock.patch("src_check.cli.kpi.ConfigLoader")
    def test_kpi_main_basic_execution(self, mock_config_loader, mock_engine_class):
        """Test basic execution of KPI CLI."""
        # Setup mocks
        mock_config = mock.Mock()
        mock_config.checkers = ["security", "code_quality"]
        mock_config.file_patterns = ["*.py"]
        mock_config.ignore_patterns = []
        mock_config_loader.load.return_value = mock_config

        mock_engine = mock.Mock()
        mock_engine_class.return_value = mock_engine
        mock_engine.analyze_directory.return_value = {}

        # Run with basic args
        with mock.patch("sys.argv", ["src-check-kpi", "."]):
            with mock.patch("builtins.print"):
                result = kpi_main()
                assert result is None  # Normal exit

        # Verify calls
        mock_config_loader.load.assert_called_once()
        mock_engine_class.assert_called_once()

    @mock.patch("src_check.cli.kpi.AnalysisEngine")
    @mock.patch("src_check.cli.kpi.ConfigLoader")
    def test_kpi_main_with_checkers_filter(self, mock_config_loader, mock_engine_class):
        """Test KPI CLI with specific checkers."""
        # Setup mocks
        mock_config = mock.Mock()
        mock_config.checkers = ["security", "code_quality", "performance"]
        mock_config.file_patterns = ["*.py"]
        mock_config.ignore_patterns = []
        mock_config_loader.load.return_value = mock_config

        mock_engine = mock.Mock()
        mock_engine_class.return_value = mock_engine
        mock_engine.analyze_directory.return_value = {}

        # Run with specific checkers
        with mock.patch(
            "sys.argv", ["src-check-kpi", ".", "--checkers", "security", "performance"]
        ):
            with mock.patch("builtins.print"):
                kpi_main()

        # Verify engine was created with filtered checkers
        call_args = mock_engine_class.call_args
        assert set(call_args[0][0]) == {"security", "performance"}