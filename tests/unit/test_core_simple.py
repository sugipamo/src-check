"""
Simple unit tests for core modules to improve coverage.
"""

import tempfile
from pathlib import Path
from unittest import mock

import pytest
import yaml

from src_check.core.config_loader import ConfigLoader, SrcCheckConfig
from src_check.core.engine import AnalysisEngine
from src_check.core.kpi_calculator import KPICalculator
from src_check.core.registry import PluginRegistry as CheckerRegistry, registry
from src_check.models import CheckResult


class TestConfigLoader:
    """Test ConfigLoader."""

    def test_load_default_config(self):
        """Test loading default configuration."""
        loader = ConfigLoader()
        config = loader.load_default_config()
        
        assert isinstance(config, SrcCheckConfig)
        assert config.version == "1.0"
        assert "**/__pycache__/**" in config.exclude

    def test_load_from_yaml_file(self):
        """Test loading from YAML file."""
        config_data = {
            "version": "1.0",
            "exclude": ["test/"],
            "checkers": {"SecurityChecker": {"enabled": False}},
        }
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            loader = ConfigLoader()
            config = loader.load_from_file(config_path)
            
            assert config.checkers["SecurityChecker"]["enabled"] is False
        finally:
            config_path.unlink()

    def test_find_config_file(self):
        """Test finding config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / ".src-check.yaml"
            config_file.write_text("version: '1.0'")
            
            loader = ConfigLoader()
            found = loader.find_config_file(Path(tmpdir))
            
            assert found == config_file


class TestAnalysisEngine:
    """Test AnalysisEngine."""

    def test_init_engine(self):
        """Test engine initialization."""
        engine = AnalysisEngine(["security", "code_quality"])
        assert len(engine.checkers) == 2

    def test_should_ignore_file(self):
        """Test file ignore logic."""
        engine = AnalysisEngine([])
        
        assert engine._should_ignore_file(Path("__pycache__/test.pyc"))
        assert engine._should_ignore_file(Path(".git/config"))
        assert not engine._should_ignore_file(Path("main.py"))

    @mock.patch("src_check.core.engine.registry")
    def test_analyze_file(self, mock_registry):
        """Test analyzing a file."""
        mock_checker = mock.Mock()
        mock_checker.check_file.return_value = [
            CheckResult(
                checker_name="test",
                severity="info",
                category="test",
                rule="test_rule",
                message="Test",
                file_path="test.py",
                line_number=1,
            )
        ]
        
        mock_registry.get_checker.return_value = mock_checker
        
        engine = AnalysisEngine(["test"])
        engine.checkers = [mock_checker]
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py") as f:
            f.write("print('test')")
            f.flush()
            
            results = engine.analyze_file(Path(f.name))
            assert len(results) == 1


class TestKPICalculator:
    """Test KPICalculator."""

    def test_calculate_empty_project(self):
        """Test calculating KPI for empty project."""
        calculator = KPICalculator()
        score = calculator.calculate_project_score({})
        
        assert score.overall_score == 100.0
        assert score.critical_issues == 0

    def test_calculate_with_issues(self):
        """Test calculating KPI with issues."""
        results = {
            "test.py": [
                CheckResult(
                    checker_name="security",
                    severity="critical",
                    category="security",
                    rule="test",
                    message="Test",
                    file_path="test.py",
                    line_number=1,
                )
            ]
        }
        
        calculator = KPICalculator()
        score = calculator.calculate_project_score(results)
        
        assert score.critical_issues == 1
        assert score.overall_score < 100.0


class TestRegistry:
    """Test CheckerRegistry."""

    def test_global_registry_has_checkers(self):
        """Test that global registry has checkers."""
        checkers = registry.list_checkers()
        
        assert "security" in checkers
        assert "code_quality" in checkers
        assert len(checkers) >= 10

    def test_get_checker(self):
        """Test getting a checker."""
        checker = registry.get_checker("security")
        assert checker is not None

    def test_register_checker(self):
        """Test registering a new checker."""
        test_registry = CheckerRegistry()
        mock_checker = mock.Mock()
        
        test_registry.register("test_checker", mock_checker)
        assert "test_checker" in test_registry.list_checkers()