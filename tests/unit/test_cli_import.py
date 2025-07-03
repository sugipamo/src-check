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
from src_check.models.check_result import Severity


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

    @mock.patch("src_check.cli.main.registry")
    @mock.patch("src_check.cli.main.AnalysisEngine")
    @mock.patch("src_check.cli.main.ConfigLoader")
    def test_main_basic_execution(
        self, mock_config_loader_class, mock_engine_class, mock_registry
    ):
        """Test basic execution of main CLI."""
        # Setup mocks
        mock_config = mock.Mock()
        mock_config.is_checker_enabled.return_value = True

        mock_config_instance = mock.Mock()
        mock_config_instance.find_config_file.return_value = None
        mock_config_instance.load_default_config.return_value = mock_config
        mock_config_loader_class.return_value = mock_config_instance

        mock_engine = mock.Mock()
        mock_engine_class.return_value = mock_engine
        mock_engine.analyze_file.return_value = []
        mock_engine.analyze_directory.return_value = {}

        # Mock registry
        mock_checker = mock.Mock()
        mock_checker.name = "SecurityChecker"
        mock_checker.__class__.__name__ = "SecurityChecker"
        mock_registry.get_all_checkers.return_value = [mock_checker]

        # Run with basic args
        with mock.patch("sys.argv", ["src-check", "."]), mock.patch(
            "builtins.print"
        ), mock.patch("src_check.cli.main.validate_paths", return_value=[Path(".")]):
            result = main()
            assert result is None  # Normal exit

        # Verify calls
        mock_config_instance.load_default_config.assert_called_once()
        mock_engine_class.assert_called_once()

    @mock.patch("src_check.cli.main.KPICalculator")
    @mock.patch("src_check.cli.main.registry")
    @mock.patch("src_check.cli.main.AnalysisEngine")
    @mock.patch("src_check.cli.main.ConfigLoader")
    def test_main_with_threshold_failure(
        self,
        mock_config_loader_class,
        mock_engine_class,
        mock_registry,
        mock_kpi_calc_class,
    ):
        """Test main CLI with threshold failure."""
        # Setup mocks
        mock_config = mock.Mock()
        mock_config.is_checker_enabled.return_value = True
        mock_config.fail_on_issues = False  # Add this attribute

        mock_config_instance = mock.Mock()
        mock_config_instance.find_config_file.return_value = None
        mock_config_instance.load_default_config.return_value = mock_config
        mock_config_loader_class.return_value = mock_config_instance

        mock_engine = mock.Mock()
        mock_engine_class.return_value = mock_engine
        mock_engine.analyze_directory.return_value = {
            "test.py": [
                mock.Mock(
                    severity=Severity.CRITICAL,
                    category="security",
                    rule_id="hardcoded_secret",
                    checker_name="SecurityChecker",
                    title="Hardcoded Secret Found",
                    failure_count=1,
                    fix_policy="Remove hardcoded secrets",
                    failure_locations=[],
                )
            ]
        }

        # Mock registry
        mock_checker = mock.Mock()
        mock_checker.name = "SecurityChecker"
        mock_checker.__class__.__name__ = "SecurityChecker"
        mock_registry.discover_plugins.return_value = None
        mock_registry.get_all_checkers.return_value = [mock_checker]

        # Mock KPI calculator to return low score
        mock_kpi_calc = mock.Mock()
        mock_kpi_score = mock.Mock()
        mock_kpi_score.overall_score = 60.0  # Below threshold of 90
        mock_kpi_score.critical_issues = 1
        mock_kpi_score.high_issues = 0
        mock_kpi_score.medium_issues = 0
        mock_kpi_score.low_issues = 0
        mock_kpi_score.total_issues = 1
        mock_kpi_score.category_scores = {"security": 40.0}
        mock_kpi_calc.calculate_project_score.return_value = mock_kpi_score
        mock_kpi_calc_class.return_value = mock_kpi_calc

        # Run with threshold
        with mock.patch(
            "sys.argv", ["src-check", ".", "--threshold", "90"]
        ), mock.patch("builtins.print"), mock.patch(
            "src_check.cli.main.validate_paths", return_value=[Path(".")]
        ), pytest.raises(
            SystemExit
        ) as exc_info:
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
                "sys.argv",
                ["src-check", ".", "--format", "json", "--output", output_file],
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

    def test_kpi_main_basic_execution(self):
        """Test basic execution of KPI CLI."""
        # Run with basic args - KPI main is currently a placeholder
        with mock.patch("sys.argv", ["src-check-kpi", "."]), mock.patch(
            "builtins.print"
        ):
            result = kpi_main()
            assert result is None  # Normal exit

    def test_kpi_main_with_checkers_filter(self):
        """Test KPI CLI with specific checkers."""
        # Run with specific checkers - KPI main is currently a placeholder
        with mock.patch(
            "sys.argv", ["src-check-kpi", ".", "--checkers", "security", "performance"]
        ), mock.patch("builtins.print"):
            result = kpi_main()
            assert result is None  # Normal exit
