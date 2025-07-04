"""Context-aware analysis engine that extends the base engine with file context understanding."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from src_check.context.analyzer import FileContextAnalyzer
from src_check.context.rules import ContextAwareRuleManager, RuleContext
from src_check.core.base import BaseChecker
from src_check.core.engine import AnalysisEngine
from src_check.models.check_result import CheckResult
from src_check.models.config import SrcCheckConfig

logger = logging.getLogger(__name__)


class ContextAwareAnalysisEngine(AnalysisEngine):
    """Analysis engine with context awareness for intelligent rule application."""

    def __init__(
        self,
        checkers: Union[List[str], List[BaseChecker]],
        config: Optional[SrcCheckConfig] = None,
    ):
        """Initialize the context-aware analysis engine.

        Args:
            checkers: List of checker names or checker instances to run
            config: Optional configuration object
        """
        super().__init__(checkers, config)
        self.context_analyzer = FileContextAnalyzer(config)
        self.rule_manager = ContextAwareRuleManager()

    def analyze_file(self, file_path: Path) -> List[CheckResult]:
        """Analyze a single file with context-aware checking.

        Args:
            file_path: Path to the file to analyze

        Returns:
            List of check results from all checkers, adjusted for context
        """
        # First check if we should analyze this file
        if not self.context_analyzer.should_check_file(file_path):
            logger.debug(f"Skipping file based on context: {file_path}")
            return []

        # Get file context
        file_type = self.context_analyzer.classify_file(file_path)
        severity_multiplier = self.context_analyzer.get_severity_multiplier(file_type)
        rule_adjustments = self.context_analyzer.get_context_rules(file_type)

        # Create rule context
        context = RuleContext(
            file_type=file_type,
            file_path=str(file_path),
            severity_multiplier=severity_multiplier,
            rule_adjustments=rule_adjustments,
        )

        # Log context information
        logger.debug(
            f"Analyzing {file_path} as {file_type.name} "
            f"(severity multiplier: {severity_multiplier})"
        )

        # Get base results from parent class
        results = super().analyze_file(file_path)

        # Apply context-aware filtering and adjustments
        if results:
            # Convert CheckResult objects to dicts for filtering
            issues = []
            for result in results:
                if hasattr(result, "issues"):
                    issues.extend(result.issues)
                elif hasattr(result, "to_dict"):
                    issues.append(result.to_dict())

            # Filter and adjust issues based on context
            filtered_issues = self.rule_manager.filter_issues(issues, context)

            # Convert back to CheckResult objects
            # This is a simplified approach - in production, we'd preserve
            # the original CheckResult structure
            if filtered_issues:
                # Group by checker
                checker_results: Dict[str, list] = {}
                for issue in filtered_issues:
                    checker_name = issue.get("checker", "unknown")
                    if checker_name not in checker_results:
                        checker_results[checker_name] = []
                    checker_results[checker_name].append(issue)

                # Create CheckResult objects
                adjusted_results = []
                for checker_name, checker_issues in checker_results.items():
                    result = CheckResult(
                        title=f"{checker_name} Check",
                        checker_name=checker_name,
                    )
                    # Add failures from issues
                    for issue in checker_issues:
                        result.add_failure(
                            file_path=str(file_path),
                            line=issue.get("line", 0),
                            message=issue.get("message", ""),
                            column=issue.get("column"),
                        )
                    adjusted_results.append(result)

                return adjusted_results

        return results

    def get_adjusted_thresholds(self, file_path: Path) -> Dict[str, Dict[str, float]]:
        """Get context-adjusted thresholds for a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary of adjusted thresholds
        """
        file_type = self.context_analyzer.classify_file(file_path)
        rule_adjustments = self.context_analyzer.get_context_rules(file_type)

        context = RuleContext(
            file_type=file_type,
            file_path=str(file_path),
            severity_multiplier=self.context_analyzer.get_severity_multiplier(
                file_type
            ),
            rule_adjustments=rule_adjustments,
        )

        # Get adjusted thresholds for common metrics
        thresholds: Dict[str, Dict[str, float]] = {}
        for metric in ["complexity", "coupling", "line_length", "function_length"]:
            thresholds[metric] = {}
            if metric == "complexity":
                thresholds[metric]["cyclomatic"] = (
                    self.rule_manager.get_adjusted_threshold(
                        metric, "cyclomatic", context
                    )
                )
                thresholds[metric]["cognitive"] = (
                    self.rule_manager.get_adjusted_threshold(
                        metric, "cognitive", context
                    )
                )
            elif metric == "coupling":
                thresholds[metric]["max_dependencies"] = (
                    self.rule_manager.get_adjusted_threshold(
                        metric, "max_dependencies", context
                    )
                )
                thresholds[metric]["max_imports"] = (
                    self.rule_manager.get_adjusted_threshold(
                        metric, "max_imports", context
                    )
                )
            elif metric == "line_length":
                thresholds[metric]["max_length"] = (
                    self.rule_manager.get_adjusted_threshold(
                        metric, "max_length", context
                    )
                )
            elif metric == "function_length":
                thresholds[metric]["max_lines"] = (
                    self.rule_manager.get_adjusted_threshold(
                        metric, "max_lines", context
                    )
                )

        return thresholds

    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if a file should be ignored based on context and exclusion patterns.

        Args:
            file_path: Path to check

        Returns:
            True if file should be ignored, False otherwise
        """
        # First check parent class exclusions
        if super()._should_ignore_file(file_path):
            return True

        # Then check context-based exclusions
        return not self.context_analyzer.should_check_file(file_path)
