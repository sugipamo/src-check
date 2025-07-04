"""Unit tests for context-aware rule management."""

from src_check.context import FileType
from src_check.context.rules import ContextAwareRuleManager, RuleContext


class TestRuleContext:
    """Test cases for RuleContext."""

    def test_adjust_severity_reduction(self):
        """Test severity reduction based on context."""
        context = RuleContext(
            file_type=FileType.EXAMPLE,
            file_path="examples/demo.py",
            severity_multiplier=0.3,
            rule_adjustments={},
        )

        assert context.adjust_severity("error") == "warning"
        assert context.adjust_severity("warning") == "info"
        assert context.adjust_severity("info") == "info"  # Can't go lower

    def test_adjust_severity_increase(self):
        """Test severity increase based on context."""
        context = RuleContext(
            file_type=FileType.PRODUCTION,
            file_path="src/main.py",
            severity_multiplier=1.5,
            rule_adjustments={},
        )

        assert context.adjust_severity("info") == "warning"
        assert context.adjust_severity("warning") == "error"
        assert context.adjust_severity("critical") == "critical"  # Can't go higher

    def test_adjust_severity_zero_multiplier(self):
        """Test severity with zero multiplier."""
        context = RuleContext(
            file_type=FileType.GENERATED,
            file_path="build/output.py",
            severity_multiplier=0.0,
            rule_adjustments={},
        )

        # All severities become info
        assert context.adjust_severity("critical") == "info"
        assert context.adjust_severity("error") == "info"
        assert context.adjust_severity("warning") == "info"

    def test_should_apply_rule(self):
        """Test rule application decisions."""
        context = RuleContext(
            file_type=FileType.TEST,
            file_path="tests/test_main.py",
            severity_multiplier=0.7,
            rule_adjustments={
                "print_statements": {"enabled": False},
                "test_quality": {"enabled": True},
            },
        )

        assert context.should_apply_rule("print_statements") is False
        assert context.should_apply_rule("test_quality") is True
        assert context.should_apply_rule("other_rule") is True  # Default

    def test_should_apply_rule_with_all_disabled(self):
        """Test rule application with 'all' rules disabled."""
        context = RuleContext(
            file_type=FileType.DOCUMENTATION,
            file_path="README.md",
            severity_multiplier=0.2,
            rule_adjustments={
                "all": {"enabled": False},
                "specific_rule": {"enabled": True},  # Specific overrides 'all'
            },
        )

        assert context.should_apply_rule("random_rule") is False
        assert context.should_apply_rule("specific_rule") is True

    def test_get_threshold_multiplier(self):
        """Test threshold multiplier retrieval."""
        context = RuleContext(
            file_type=FileType.EXAMPLE,
            file_path="examples/demo.py",
            severity_multiplier=0.3,
            rule_adjustments={
                "complexity": {"threshold_multiplier": 2.0},
                "coupling": {"threshold_multiplier": 1.5},
            },
        )

        assert context.get_threshold_multiplier("complexity") == 2.0
        assert context.get_threshold_multiplier("coupling") == 1.5
        assert context.get_threshold_multiplier("other_metric") == 1.0  # Default

    def test_get_rule_config(self):
        """Test rule configuration retrieval."""
        config_data = {
            "enabled": True,
            "severity": "warning",
            "custom_param": 42,
        }

        context = RuleContext(
            file_type=FileType.PRODUCTION,
            file_path="src/main.py",
            severity_multiplier=1.0,
            rule_adjustments={"my_rule": config_data},
        )

        assert context.get_rule_config("my_rule") == config_data
        assert context.get_rule_config("non_existent") == {}


class TestContextAwareRuleManager:
    """Test cases for ContextAwareRuleManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ContextAwareRuleManager()

    def test_get_adjusted_threshold(self):
        """Test threshold adjustment based on context."""
        context = RuleContext(
            file_type=FileType.EXAMPLE,
            file_path="examples/demo.py",
            severity_multiplier=0.3,
            rule_adjustments={
                "complexity": {"threshold_multiplier": 2.0},
            },
        )

        # Base cyclomatic complexity threshold is 10
        adjusted = self.manager.get_adjusted_threshold(
            "complexity", "cyclomatic", context
        )
        assert adjusted == 20.0  # 10 * 2.0

        # Base cognitive complexity threshold is 15
        adjusted = self.manager.get_adjusted_threshold(
            "complexity", "cognitive", context
        )
        assert adjusted == 30.0  # 15 * 2.0

    def test_filter_issues(self):
        """Test issue filtering based on context."""
        issues = [
            {
                "rule": "print_statements",
                "severity": "error",
                "message": "Print statement found",
            },
            {
                "rule": "complexity",
                "severity": "warning",
                "message": "High complexity",
            },
            {
                "rule": "disabled_rule",
                "severity": "error",
                "message": "This should be filtered",
            },
        ]

        context = RuleContext(
            file_type=FileType.EXAMPLE,
            file_path="examples/demo.py",
            severity_multiplier=0.3,
            rule_adjustments={
                "disabled_rule": {"enabled": False},
            },
        )

        filtered = self.manager.filter_issues(issues, context)

        # Should have 2 issues (disabled_rule filtered out)
        assert len(filtered) == 2

        # Check severity adjustments
        print_issue = next(i for i in filtered if i["rule"] == "print_statements")
        assert print_issue["severity"] == "warning"  # Reduced from error
        assert print_issue["context"]["original_severity"] == "error"
        assert print_issue["context"]["adjusted"] is True

    def test_filter_issues_generated_files(self):
        """Test that generated files have minimal issues."""
        issues = [
            {"rule": "any_rule", "severity": "error"},
            {"rule": "another_rule", "severity": "critical"},
        ]

        context = RuleContext(
            file_type=FileType.GENERATED,
            file_path="build/output.py",
            severity_multiplier=0.0,
            rule_adjustments={},
        )

        filtered = self.manager.filter_issues(issues, context)

        # All issues should be filtered for generated files
        assert len(filtered) == 0

    def test_get_rule_explanation(self):
        """Test rule explanation retrieval."""
        context = RuleContext(
            file_type=FileType.EXAMPLE,
            file_path="examples/demo.py",
            severity_multiplier=0.3,
            rule_adjustments={},
        )

        explanation = self.manager.get_rule_explanation("print_statements", context)

        assert "importance" in explanation
        assert "fix" in explanation
        assert "best_practice" in explanation
        assert explanation["context_note"] == "Rules are relaxed for example code"

        # Test for production context
        prod_context = RuleContext(
            file_type=FileType.PRODUCTION,
            file_path="src/main.py",
            severity_multiplier=1.0,
            rule_adjustments={},
        )

        prod_explanation = self.manager.get_rule_explanation("complexity", prod_context)
        assert (
            prod_explanation["context_note"]
            == "Production code requires strict quality standards"
        )
