"""
Unit tests for data models.
"""

import json
from datetime import datetime
from pathlib import Path

import pytest

from src_check.models import (
    CategoryScore,
    CheckResult,
    FailureLocation,
    KPIScore,
    OutputConfig,
    RuleConfig,
    Severity,
    SrcCheckConfig,
)


class TestFailureLocation:
    """Test FailureLocation model."""
    
    @pytest.mark.unit
    def test_creation(self):
        """Test creating a failure location."""
        loc = FailureLocation(
            file_path="test.py",
            line=10,
            column=5,
            message="Test failure"
        )
        
        assert loc.file_path == "test.py"
        assert loc.line == 10
        assert loc.column == 5
        assert loc.message == "Test failure"
    
    @pytest.mark.unit
    def test_string_representation(self):
        """Test string representation."""
        loc = FailureLocation(
            file_path="test.py",
            line=10,
            column=5,
            message="Test failure"
        )
        
        assert str(loc) == "test.py:10:5 - Test failure"
        
        # Without column
        loc2 = FailureLocation(file_path="test.py", line=10)
        assert str(loc2) == "test.py:10"
    
    @pytest.mark.unit
    def test_to_dict(self):
        """Test dictionary conversion."""
        loc = FailureLocation(
            file_path="test.py",
            line=10,
            column=5,
            message="Test failure",
            code_snippet="print('test')"
        )
        
        data = loc.to_dict()
        assert data["file_path"] == "test.py"
        assert data["line"] == 10
        assert data["column"] == 5
        assert data["message"] == "Test failure"
        assert data["code_snippet"] == "print('test')"


class TestCheckResult:
    """Test CheckResult model."""
    
    @pytest.mark.unit
    def test_creation(self):
        """Test creating a check result."""
        result = CheckResult(
            title="Test Check",
            checker_name="test_checker",
            severity=Severity.HIGH,
            category="security"
        )
        
        assert result.title == "Test Check"
        assert result.checker_name == "test_checker"
        assert result.severity == Severity.HIGH
        assert result.category == "security"
        assert result.passed is True
        assert result.failure_count == 0
    
    @pytest.mark.unit
    def test_add_failure(self):
        """Test adding failures."""
        result = CheckResult(
            title="Test Check",
            checker_name="test_checker"
        )
        
        result.add_failure(
            file_path="test.py",
            line=10,
            message="Test failure"
        )
        
        assert result.passed is False
        assert result.failure_count == 1
        assert len(result.failure_locations) == 1
        assert result.failure_locations[0].message == "Test failure"
    
    @pytest.mark.unit
    def test_to_dict(self):
        """Test dictionary conversion."""
        result = CheckResult(
            title="Test Check",
            checker_name="test_checker",
            severity=Severity.HIGH,
            fix_policy="Fix by doing X"
        )
        result.add_failure("test.py", 10, "Issue found")
        
        data = result.to_dict()
        assert data["title"] == "Test Check"
        assert data["checker_name"] == "test_checker"
        assert data["passed"] is False
        assert data["failure_count"] == 1
        assert data["severity"] == "high"
        assert len(data["failures"]) == 1
    
    @pytest.mark.unit
    def test_format_report(self):
        """Test report formatting."""
        result = CheckResult(
            title="Test Check",
            checker_name="test_checker",
            severity=Severity.HIGH,
            fix_policy="Fix by doing X"
        )
        
        # Passed check
        report = result.format_report()
        assert "✅ PASSED" in report
        
        # Failed check
        result.add_failure("test.py", 10, "Issue found")
        report = result.format_report()
        assert "❌ FAILED" in report
        assert "Fix by doing X" in report


class TestKPIScore:
    """Test KPIScore model."""
    
    @pytest.mark.unit
    def test_creation(self):
        """Test creating KPI score."""
        score = KPIScore(
            total_score=85.0,
            project_path="/test/project"
        )
        
        assert score.total_score == 85.0
        assert score.base_score == 100.0
        assert score.project_path == "/test/project"
    
    @pytest.mark.unit
    def test_calculate_from_results(self):
        """Test calculating score from check results."""
        results = [
            CheckResult(
                title="Security Check",
                checker_name="security",
                category="security",
                severity=Severity.HIGH
            ),
            CheckResult(
                title="Code Quality Check",
                checker_name="quality",
                category="code_quality",
                severity=Severity.MEDIUM
            )
        ]
        
        # Add failures
        results[0].add_failure("test.py", 10, "Security issue")
        results[1].add_failure("test.py", 20, "Quality issue")
        results[1].add_failure("test.py", 30, "Another issue")
        
        score = KPIScore.calculate_from_results(results)
        
        assert score.total_score < 100.0  # Should be reduced
        assert score.total_issues == 3
        assert score.total_files_analyzed == 1
        assert "security_quality" in score.categories
        assert "code_quality" in score.categories
    
    @pytest.mark.unit
    def test_grading(self):
        """Test grade calculation."""
        assert KPIScore(total_score=95.0).get_grade() == "A"
        assert KPIScore(total_score=85.0).get_grade() == "B"
        assert KPIScore(total_score=75.0).get_grade() == "C"
        assert KPIScore(total_score=65.0).get_grade() == "D"
        assert KPIScore(total_score=55.0).get_grade() == "F"
    
    @pytest.mark.unit
    def test_status(self):
        """Test status calculation."""
        assert KPIScore(total_score=85.0).get_status() == "優秀"
        assert KPIScore(total_score=75.0).get_status() == "良好"
        assert KPIScore(total_score=55.0).get_status() == "標準"
        assert KPIScore(total_score=35.0).get_status() == "要改善"
        assert KPIScore(total_score=25.0).get_status() == "危険"
    
    @pytest.mark.unit
    def test_format_report(self):
        """Test report formatting."""
        score = KPIScore(
            total_score=75.0,
            project_path="/test/project",
            total_files_analyzed=10,
            total_issues=5
        )
        
        report = score.format_report()
        assert "総合スコア: 75.0/100" in report
        assert "分析ファイル数: 10" in report
        assert "検出された問題: 5" in report


class TestSrcCheckConfig:
    """Test SrcCheckConfig model."""
    
    @pytest.mark.unit
    def test_default_config(self):
        """Test default configuration."""
        config = SrcCheckConfig()
        
        assert config.base_score == 100.0
        assert config.weights["code_quality"] == 0.25
        assert config.severity_impacts["high"] == -5.0
        assert config.max_file_size == 10 * 1024 * 1024
        assert config.parallel is True
    
    @pytest.mark.unit
    def test_from_dict(self):
        """Test creating config from dictionary."""
        data = {
            "base_score": 90.0,
            "weights": {
                "code_quality": 0.3,
                "security_quality": 0.4
            },
            "rules": [
                {"name": "test_rule", "enabled": False}
            ],
            "output": {
                "format": "json",
                "verbose": True
            }
        }
        
        config = SrcCheckConfig.from_dict(data)
        
        assert config.base_score == 90.0
        assert config.weights["code_quality"] == 0.3
        assert config.weights["security_quality"] == 0.4
        assert len(config.rules) == 1
        assert config.rules[0].name == "test_rule"
        assert config.rules[0].enabled is False
        assert config.output.format == "json"
        assert config.output.verbose is True
    
    @pytest.mark.unit
    def test_yaml_roundtrip(self, tmp_path):
        """Test saving and loading YAML config."""
        config = SrcCheckConfig()
        config.base_score = 95.0
        config.rules.append(
            RuleConfig(name="test_rule", enabled=True)
        )
        
        # Save
        yaml_path = tmp_path / "test_config.yaml"
        config.save(yaml_path)
        
        # Load
        loaded_config = SrcCheckConfig.from_yaml(yaml_path)
        
        assert loaded_config.base_score == 95.0
        assert len(loaded_config.rules) == 1
        assert loaded_config.rules[0].name == "test_rule"
    
    @pytest.mark.unit
    def test_get_enabled_rules(self):
        """Test getting enabled rules."""
        config = SrcCheckConfig()
        config.rules = [
            RuleConfig(name="rule1", enabled=True),
            RuleConfig(name="rule2", enabled=False),
            RuleConfig(name="rule3", enabled=True),
        ]
        
        enabled = config.get_enabled_rules()
        assert enabled == ["rule1", "rule3"]