"""KPI score calculator for analyzing check results."""

from collections import defaultdict
from typing import Dict, List

from src_check.models.check_result import CheckResult, Severity
from src_check.models.simple_kpi_score import KpiScore


class KPICalculator:
    """Calculator for computing KPI scores from check results."""

    # Severity weights for score calculation
    SEVERITY_WEIGHTS = {
        Severity.CRITICAL: 10.0,
        Severity.HIGH: 5.0,
        Severity.MEDIUM: 2.0,
        Severity.LOW: 1.0,
        Severity.INFO: 0.5,
    }

    # Category weights for overall score
    CATEGORY_WEIGHTS = {
        "security": 1.5,  # Security is most important
        "code_quality": 1.0,
        "architecture": 1.0,
        "test_quality": 1.2,  # Tests are also important
        "documentation": 0.8,
        "performance": 0.9,
    }

    def calculate_file_score(self, results: List[CheckResult]) -> KpiScore:
        """Calculate KPI score for a single file.

        Args:
            results: List of check results for the file

        Returns:
            KPI score for the file
        """
        if not results:
            return KpiScore(
                overall_score=100.0,
                category_scores={},
                total_issues=0,
                critical_issues=0,
                high_issues=0,
                medium_issues=0,
                low_issues=0,
            )

        # Count issues by severity
        severity_counts = defaultdict(int)
        category_issues = defaultdict(list)

        for result in results:
            severity_counts[result.severity] += 1
            category_issues[result.category].append(result)

        # Calculate category scores
        category_scores = {}
        for category, issues in category_issues.items():
            category_scores[category] = self._calculate_category_score(issues)

        # Calculate overall score
        overall_score = self._calculate_overall_score(category_scores, severity_counts)

        return KpiScore(
            overall_score=overall_score,
            category_scores=category_scores,
            total_issues=len(results),
            critical_issues=severity_counts[Severity.CRITICAL],
            high_issues=severity_counts[Severity.HIGH],
            medium_issues=severity_counts[Severity.MEDIUM],
            low_issues=severity_counts[Severity.LOW],
        )

    def calculate_project_score(
        self, all_results: Dict[str, List[CheckResult]]
    ) -> KpiScore:
        """Calculate KPI score for an entire project.

        Args:
            all_results: Dictionary mapping file paths to their check results

        Returns:
            Overall KPI score for the project
        """
        if not all_results:
            return KpiScore(
                overall_score=100.0,
                category_scores={},
                total_issues=0,
                critical_issues=0,
                high_issues=0,
                medium_issues=0,
                low_issues=0,
            )

        # Aggregate all results
        all_issues = []
        for file_results in all_results.values():
            all_issues.extend(file_results)

        # Calculate aggregate score
        return self.calculate_file_score(all_issues)

    def _calculate_category_score(self, issues: List[CheckResult]) -> float:
        """Calculate score for a specific category.

        Args:
            issues: List of issues in the category

        Returns:
            Score for the category (0-100)
        """
        if not issues:
            return 100.0

        # Calculate penalty based on issue severity
        total_penalty = 0.0
        for issue in issues:
            penalty = self.SEVERITY_WEIGHTS.get(issue.severity, 1.0)
            total_penalty += penalty

        # Convert penalty to score (max penalty of 100)
        score = max(0.0, 100.0 - min(total_penalty, 100.0))
        return round(score, 2)

    def _calculate_overall_score(
        self, category_scores: Dict[str, float], severity_counts: Dict[Severity, int]
    ) -> float:
        """Calculate overall score from category scores and severity counts.

        Args:
            category_scores: Scores for each category
            severity_counts: Count of issues by severity

        Returns:
            Overall score (0-100)
        """
        if not category_scores:
            return 100.0

        # Calculate weighted average of category scores
        total_weight = 0.0
        weighted_sum = 0.0

        for category, score in category_scores.items():
            weight = self.CATEGORY_WEIGHTS.get(category, 1.0)
            weighted_sum += score * weight
            total_weight += weight

        if total_weight == 0:
            return 100.0

        base_score = weighted_sum / total_weight

        # Apply additional penalty for critical/high issues
        critical_penalty = severity_counts.get(Severity.CRITICAL, 0) * 5
        high_penalty = severity_counts.get(Severity.HIGH, 0) * 2

        final_score = max(0.0, base_score - critical_penalty - high_penalty)
        return round(final_score, 2)
