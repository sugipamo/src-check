"""
Tests for core modules: config_loader, engine, kpi_calculator, and registry.
"""

import tempfile
from pathlib import Path
from unittest import mock

import pytest
import yaml

from src_check.core.config_loader import ConfigLoader, SrcCheckConfig as Config
from src_check.core.engine import AnalysisEngine
from src_check.core.kpi_calculator import KPICalculator
from src_check.core.registry import CheckerRegistry, registry
from src_check.models import CheckResult, SimpleKPIScore
from src_check.rules.base import BaseChecker


class TestConfigLoader:
    """Test ConfigLoader functionality."""

    def test_load_default_config(self):
        """Test loading default configuration."""
        loader = ConfigLoader()
        config = loader.load()

        assert isinstance(config, Config)
        assert config.file_patterns == ["*.py"]
        assert config.ignore_patterns == [
            "__pycache__",
            "*.pyc",
            ".git",
            ".venv",
            "venv",
            "env",
            ".env",
            "build",
            "dist",
            ".eggs",
            "*.egg-info",
            ".mypy_cache",
            ".pytest_cache",
            ".ruff_cache",
            ".coverage",
            "htmlcov",
            ".tox",
        ]
        assert len(config.checkers) > 0
        assert config.fail_on_issues is False
        assert config.max_file_size == 1048576
        assert config.parallel is False
        assert config.cache_enabled is False
        assert config.output_format == "text"

    def test_load_yaml_config(self):
        """Test loading YAML configuration."""
        config_data = {
            "file_patterns": ["*.py", "*.pyi"],
            "ignore_patterns": ["tests/", "docs/"],
            "checkers": ["security", "code_quality"],
            "fail_on_issues": True,
            "output_format": "json",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            loader = ConfigLoader()
            config = loader.load(config_path)

            assert config.file_patterns == ["*.py", "*.pyi"]
            assert config.ignore_patterns == ["tests/", "docs/"]
            assert config.checkers == ["security", "code_quality"]
            assert config.fail_on_issues is True
            assert config.output_format == "json"
        finally:
            Path(config_path).unlink()

    def test_load_json_config(self):
        """Test loading JSON configuration."""
        import json

        config_data = {
            "checkers": ["type_hints", "documentation"],
            "max_file_size": 2097152,
            "parallel": True,
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            loader = ConfigLoader()
            config = loader.load(config_path)

            assert config.checkers == ["type_hints", "documentation"]
            assert config.max_file_size == 2097152
            assert config.parallel is True
        finally:
            Path(config_path).unlink()

    def test_load_src_check_yaml(self):
        """Test loading .src-check.yaml from current directory."""
        config_data = {
            "checkers": ["security"],
            "cache_enabled": True,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".src-check.yaml"
            with open(config_file, "w") as f:
                yaml.dump(config_data, f)

            # Change to temp directory
            original_cwd = Path.cwd()
            try:
                import os

                os.chdir(tmpdir)
                loader = ConfigLoader()
                config = loader.load()

                assert config.checkers == ["security"]
                assert config.cache_enabled is True
            finally:
                os.chdir(original_cwd)

    def test_load_invalid_config_file(self):
        """Test loading non-existent config file."""
        loader = ConfigLoader()
        with pytest.raises(FileNotFoundError):
            loader.load("non_existent_config.yaml")


class TestAnalysisEngine:
    """Test AnalysisEngine functionality."""

    @mock.patch("src_check.core.engine.registry")
    def test_init_with_checkers(self, mock_registry):
        """Test engine initialization with specific checkers."""
        # Setup mock checkers
        mock_checker1 = mock.Mock(spec=BaseChecker)
        mock_checker2 = mock.Mock(spec=BaseChecker)
        mock_registry.get_checker.side_effect = lambda name: {
            "security": mock_checker1,
            "code_quality": mock_checker2,
        }.get(name)

        engine = AnalysisEngine(["security", "code_quality"])

        assert len(engine.checkers) == 2
        assert mock_checker1 in engine.checkers
        assert mock_checker2 in engine.checkers

    def test_analyze_file(self):
        """Test analyzing a single file."""
        # Create a mock checker
        mock_checker = mock.Mock(spec=BaseChecker)
        mock_result = CheckResult(
            checker_name="test_checker",
            severity="warning",
            category="test",
            rule="test_rule",
            message="Test issue",
            file_path="test.py",
            line_number=1,
        )
        mock_checker.check_file.return_value = [mock_result]

        engine = AnalysisEngine([])
        engine.checkers = [mock_checker]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("print('test')")
            test_file = Path(f.name)

        try:
            results = engine.analyze_file(test_file)
            assert len(results) == 1
            assert results[0] == mock_result
            mock_checker.check_file.assert_called_once()
        finally:
            test_file.unlink()

    def test_analyze_directory(self):
        """Test analyzing a directory."""
        mock_checker = mock.Mock(spec=BaseChecker)
        mock_result = CheckResult(
            checker_name="test_checker",
            severity="info",
            category="test",
            rule="test_rule",
            message="Test issue",
            file_path="test.py",
            line_number=1,
        )
        mock_checker.check_file.return_value = [mock_result]

        engine = AnalysisEngine([])
        engine.checkers = [mock_checker]

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            test_file1 = Path(tmpdir) / "test1.py"
            test_file1.write_text("print('test1')")
            test_file2 = Path(tmpdir) / "test2.py"
            test_file2.write_text("print('test2')")

            # Create a file to ignore
            Path(tmpdir) / "__pycache__" / "test.pyc"

            results = engine.analyze_directory(Path(tmpdir))

            assert len(results) == 2
            assert str(test_file1) in results
            assert str(test_file2) in results
            assert len(results[str(test_file1)]) == 1
            assert len(results[str(test_file2)]) == 1

    def test_should_ignore_file(self):
        """Test file ignore logic."""
        engine = AnalysisEngine([])

        # Test ignore patterns
        assert engine._should_ignore_file(Path("__pycache__/test.pyc"))
        assert engine._should_ignore_file(Path(".git/config"))
        assert engine._should_ignore_file(Path("venv/lib/python3.9/site.py"))
        assert engine._should_ignore_file(Path("build/lib/module.py"))

        # Test files that should not be ignored
        assert not engine._should_ignore_file(Path("src/main.py"))
        assert not engine._should_ignore_file(Path("tests/test_main.py"))


class TestKPICalculator:
    """Test KPICalculator functionality."""

    def test_calculate_empty_project(self):
        """Test KPI calculation for empty project."""
        calculator = KPICalculator()
        score = calculator.calculate_project_score({})

        assert isinstance(score, SimpleKPIScore)
        assert score.overall_score == 100.0
        assert score.critical_issues == 0
        assert score.warning_issues == 0
        assert score.info_issues == 0
        assert len(score.category_scores) == 0

    def test_calculate_with_issues(self):
        """Test KPI calculation with various issues."""
        results = {
            "file1.py": [
                CheckResult(
                    checker_name="security",
                    severity="critical",
                    category="security",
                    rule="hardcoded_secret",
                    message="Secret found",
                    file_path="file1.py",
                    line_number=10,
                ),
                CheckResult(
                    checker_name="code_quality",
                    severity="warning",
                    category="code_quality",
                    rule="complexity",
                    message="High complexity",
                    file_path="file1.py",
                    line_number=20,
                ),
            ],
            "file2.py": [
                CheckResult(
                    checker_name="type_hints",
                    severity="info",
                    category="type_hints",
                    rule="missing_hint",
                    message="Missing type hint",
                    file_path="file2.py",
                    line_number=5,
                ),
            ],
        }

        calculator = KPICalculator()
        score = calculator.calculate_project_score(results)

        assert score.critical_issues == 1
        assert score.warning_issues == 1
        assert score.info_issues == 1
        assert score.overall_score < 100.0
        assert "security" in score.category_scores
        assert "code_quality" in score.category_scores
        assert "type_hints" in score.category_scores

    def test_calculate_category_scores(self):
        """Test category score calculation."""
        results = {
            "test.py": [
                CheckResult(
                    checker_name="security",
                    severity="critical",
                    category="security",
                    rule="rule1",
                    message="Issue 1",
                    file_path="test.py",
                    line_number=1,
                ),
                CheckResult(
                    checker_name="security",
                    severity="critical",
                    category="security",
                    rule="rule2",
                    message="Issue 2",
                    file_path="test.py",
                    line_number=2,
                ),
            ]
        }

        calculator = KPICalculator()
        score = calculator.calculate_project_score(results)

        # With 2 critical security issues, score should be significantly reduced
        assert score.category_scores["security"] < 50.0
        assert score.overall_score < 50.0


class TestCheckerRegistry:
    """Test CheckerRegistry functionality."""

    def test_register_and_get_checker(self):
        """Test registering and retrieving a checker."""
        test_registry = CheckerRegistry()

        # Create a mock checker class
        mock_checker_class = mock.Mock()
        mock_checker_class.return_value = mock.Mock(spec=BaseChecker)

        # Register checker
        test_registry.register("test_checker", mock_checker_class)

        # Get checker
        checker = test_registry.get_checker("test_checker")
        assert checker is not None
        mock_checker_class.assert_called_once()

    def test_get_nonexistent_checker(self):
        """Test getting a non-existent checker."""
        test_registry = CheckerRegistry()

        with pytest.raises(ValueError, match="Unknown checker: nonexistent"):
            test_registry.get_checker("nonexistent")

    def test_list_checkers(self):
        """Test listing all registered checkers."""
        test_registry = CheckerRegistry()

        # Register some checkers
        test_registry.register("checker1", mock.Mock())
        test_registry.register("checker2", mock.Mock())
        test_registry.register("checker3", mock.Mock())

        checkers = test_registry.list_checkers()
        assert len(checkers) == 3
        assert "checker1" in checkers
        assert "checker2" in checkers
        assert "checker3" in checkers

    def test_global_registry(self):
        """Test that global registry has checkers registered."""
        checkers = registry.list_checkers()

        # Should have all our checkers registered
        expected_checkers = [
            "security",
            "code_quality",
            "architecture",
            "test_quality",
            "documentation",
            "type_hints",
            "performance",
            "dependency",
            "license",
            "deprecation",
        ]

        for checker_name in expected_checkers:
            assert checker_name in checkers