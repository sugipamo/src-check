"""Text formatter for human-readable output."""

from collections import defaultdict
from typing import Dict, List

from src_check.formatters import BaseFormatter
from src_check.models.check_result import CheckResult, Severity
from src_check.models.simple_kpi_score import KpiScore


class TextFormatter(BaseFormatter):
    """Formatter for human-readable text output."""

    # Severity icons
    SEVERITY_ICONS = {
        Severity.CRITICAL: "🔴",
        Severity.HIGH: "🟠",
        Severity.MEDIUM: "🟡",
        Severity.LOW: "🔵",
        Severity.INFO: "ℹ️",
    }

    def format(self, results: Dict[str, List[CheckResult]], kpi: KpiScore) -> str:
        """Format results as human-readable text.

        Args:
            results: Dictionary mapping file paths to their check results
            kpi: Overall KPI score

        Returns:
            Formatted text output
        """
        output = []

        # Header
        output.append("=" * 80)
        output.append("SRC-CHECK ANALYSIS RESULTS")
        output.append("=" * 80)
        output.append("")

        # Overall KPI Score
        output.append(self._format_kpi_score(kpi))
        output.append("")

        # Summary statistics
        output.append(self._format_summary(results))
        output.append("")

        # Detailed results by file
        if results:
            output.append("DETAILED FINDINGS")
            output.append("-" * 80)

            for file_path, file_results in sorted(results.items()):
                if file_results:
                    output.append(f"\n📄 {file_path}")
                    output.append("   " + "-" * 76)

                    # Group by severity
                    by_severity = defaultdict(list)
                    for result in file_results:
                        by_severity[result.severity].append(result)

                    # Display by severity (critical first)
                    for severity in [
                        Severity.CRITICAL,
                        Severity.HIGH,
                        Severity.MEDIUM,
                        Severity.LOW,
                        Severity.INFO,
                    ]:
                        if severity in by_severity:
                            for result in by_severity[severity]:
                                output.append(self._format_result(result))
        else:
            output.append("✅ No issues found! Great job!")

        output.append("")
        output.append("=" * 80)

        return "\n".join(output)

    def _format_kpi_score(self, kpi: KpiScore) -> str:
        """Format KPI score section."""
        lines = []

        # Overall score with visual indicator
        score_bar = self._create_score_bar(kpi.overall_score)
        lines.append(f"OVERALL SCORE: {kpi.overall_score:.1f}/100 {score_bar}")

        # Category scores
        if kpi.category_scores:
            lines.append("\nCategory Scores:")
            for category, score in sorted(kpi.category_scores.items()):
                mini_bar = self._create_mini_score_bar(score)
                lines.append(f"  {category.ljust(15)}: {score:5.1f}/100 {mini_bar}")

        return "\n".join(lines)

    def _format_summary(self, results: Dict[str, List[CheckResult]]) -> str:
        """Format summary statistics."""
        total_issues = sum(len(r) for r in results.values())
        files_with_issues = len([f for f, r in results.items() if r])
        total_files = len(results) if results else 0

        # Count by severity
        severity_counts = defaultdict(int)
        for file_results in results.values():
            for result in file_results:
                severity_counts[result.severity] += 1

        lines = []
        lines.append("SUMMARY")
        lines.append(f"Files analyzed: {total_files}")
        lines.append(f"Files with issues: {files_with_issues}")
        lines.append(f"Total issues: {total_issues}")

        if severity_counts:
            lines.append("\nIssues by severity:")
            for severity in [
                Severity.CRITICAL,
                Severity.HIGH,
                Severity.MEDIUM,
                Severity.LOW,
                Severity.INFO,
            ]:
                if severity in severity_counts:
                    icon = self.SEVERITY_ICONS[severity]
                    count = severity_counts[severity]
                    lines.append(f"  {icon} {severity.value}: {count}")

        return "\n".join(lines)

    def _format_result(self, result: CheckResult) -> str:
        """Format a single check result."""
        icon = self.SEVERITY_ICONS[result.severity]

        lines = []
        lines.append(f"   {icon} [{result.severity.value}] {result.title}")

        # Show each failure location
        for loc in result.failure_locations:
            location = f"Line {loc.line}" if loc.line else "File-level"
            message = loc.message if loc.message else result.title
            lines.append(f"      - {location}: {message}")

        return "\n".join(lines)

    def _create_score_bar(self, score: float) -> str:
        """Create a visual score bar."""
        filled = int(score / 5)  # 20 segments total
        empty = 20 - filled

        if score >= 90:
            color = "🟢"
        elif score >= 70:
            color = "🟡"
        elif score >= 50:
            color = "🟠"
        else:
            color = "🔴"

        return f"[{'█' * filled}{'░' * empty}] {color}"

    def _create_mini_score_bar(self, score: float) -> str:
        """Create a mini score bar for categories."""
        filled = int(score / 10)  # 10 segments
        empty = 10 - filled
        return f"[{'▪' * filled}{'·' * empty}]"
