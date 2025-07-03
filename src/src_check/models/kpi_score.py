"""
Data models for KPI scoring system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional

from src_check.models.check_result import CheckResult, Severity


@dataclass
class CategoryScore:
    """Score for a specific quality category."""

    name: str
    weight: float
    raw_score: float
    weighted_score: float
    issue_count: int
    issues_by_severity: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Calculate weighted score after initialization."""
        if not hasattr(self, "weighted_score") or self.weighted_score is None:
            self.weighted_score = self.raw_score * self.weight

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "weight": self.weight,
            "raw_score": round(self.raw_score, 2),
            "weighted_score": round(self.weighted_score, 2),
            "issue_count": self.issue_count,
            "issues_by_severity": self.issues_by_severity,
        }


@dataclass
class KPIScore:
    """Overall KPI score with breakdown by category."""

    total_score: float
    base_score: float = 100.0
    categories: Dict[str, CategoryScore] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    project_path: str = ""
    total_files_analyzed: int = 0
    total_issues: int = 0

    # Default weights for categories
    DEFAULT_WEIGHTS: ClassVar[Dict[str, float]] = {
        "code_quality": 0.25,
        "architecture_quality": 0.25,
        "test_quality": 0.25,
        "security_quality": 0.25,
    }

    # Severity impact on scores
    SEVERITY_IMPACTS: ClassVar[Dict[Severity, float]] = {
        Severity.CRITICAL: -10.0,
        Severity.HIGH: -5.0,
        Severity.MEDIUM: -3.0,
        Severity.LOW: -1.0,
        Severity.INFO: -0.5,
    }

    @classmethod
    def calculate_from_results(
        cls,
        check_results: List[CheckResult],
        weights: Optional[Dict[str, float]] = None,
        base_score: float = 100.0,
        project_path: str = "",
    ) -> "KPIScore":
        """Calculate KPI score from check results."""
        if weights is None:
            weights = cls.DEFAULT_WEIGHTS.copy()

        # Initialize category scores
        category_scores = {}
        for category, weight in weights.items():
            category_scores[category] = CategoryScore(
                name=category,
                weight=weight,
                raw_score=base_score,
                weighted_score=base_score * weight,
                issue_count=0,
            )

        # Count files analyzed (unique file paths)
        analyzed_files = set()

        # Process check results
        for result in check_results:
            category = cls._map_checker_to_category(result.category)
            if category not in category_scores:
                continue

            # Update file count
            for failure in result.failure_locations:
                analyzed_files.add(failure.file_path)

            # Deduct points based on severity
            severity_impact = cls.SEVERITY_IMPACTS.get(result.severity, 0)
            category_scores[category].raw_score += (
                severity_impact * result.failure_count
            )
            category_scores[category].issue_count += result.failure_count

            # Track issues by severity
            severity_key = result.severity.value
            if severity_key not in category_scores[category].issues_by_severity:
                category_scores[category].issues_by_severity[severity_key] = 0
            category_scores[category].issues_by_severity[
                severity_key
            ] += result.failure_count

        # Ensure scores don't go below 0
        for category_score in category_scores.values():
            category_score.raw_score = max(0, category_score.raw_score)
            category_score.weighted_score = (
                category_score.raw_score * category_score.weight
            )

        # Calculate total score
        total_score = sum(cat.weighted_score for cat in category_scores.values())
        total_issues = sum(cat.issue_count for cat in category_scores.values())

        return cls(
            total_score=total_score,
            base_score=base_score,
            categories=category_scores,
            project_path=project_path,
            total_files_analyzed=len(analyzed_files),
            total_issues=total_issues,
        )

    @staticmethod
    def _map_checker_to_category(checker_category: str) -> str:
        """Map checker categories to KPI categories."""
        mapping = {
            "security": "security_quality",
            "architecture": "architecture_quality",
            "code_quality": "code_quality",
            "test": "test_quality",
            "testing": "test_quality",
            "general": "code_quality",  # Default mapping
        }
        return mapping.get(checker_category, "code_quality")

    def get_grade(self) -> str:
        """Get letter grade based on score."""
        if self.total_score >= 90:
            return "A"
        elif self.total_score >= 80:
            return "B"
        elif self.total_score >= 70:
            return "C"
        elif self.total_score >= 60:
            return "D"
        else:
            return "F"

    def get_status(self) -> str:
        """Get status description based on score."""
        if self.total_score >= 80:
            return "優秀"
        elif self.total_score >= 70:
            return "良好"
        elif self.total_score >= 50:
            return "標準"
        elif self.total_score >= 30:
            return "要改善"
        else:
            return "危険"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_score": round(self.total_score, 2),
            "grade": self.get_grade(),
            "status": self.get_status(),
            "base_score": self.base_score,
            "categories": {
                name: cat.to_dict() for name, cat in self.categories.items()
            },
            "timestamp": self.timestamp.isoformat(),
            "project_path": self.project_path,
            "total_files_analyzed": self.total_files_analyzed,
            "total_issues": self.total_issues,
        }

    def format_report(self) -> str:
        """Format KPI score as a human-readable report."""
        lines = []

        # Header
        lines.append("\n" + "=" * 60)
        lines.append("📊 KPIスコア評価結果")
        lines.append("=" * 60)

        # Overall score
        lines.append(
            f"\n総合スコア: {self.total_score:.1f}/100 ({self.get_grade()}) - {self.get_status()}"
        )

        # Category breakdown
        lines.append("\nカテゴリ別スコア:")
        for name, cat in self.categories.items():
            display_name = name.replace("_", " ").title()
            lines.append(
                f"  - {display_name}: {cat.weighted_score:.1f} "
                f"(Raw: {cat.raw_score:.1f}, Weight: {cat.weight:.0%}, Issues: {cat.issue_count})"
            )

        # Summary statistics
        lines.append("\n統計情報:")
        lines.append(f"  - 分析ファイル数: {self.total_files_analyzed}")
        lines.append(f"  - 検出された問題: {self.total_issues}")
        lines.append(f"  - 分析日時: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

        # Status message
        if self.total_score >= 80:
            lines.append("\n✅ 優秀: コード品質は非常に高いレベルです。")
        elif self.total_score >= 70:
            lines.append("\n✅ 良好: コード品質は良好なレベルです。")
        elif self.total_score >= 50:
            lines.append("\n⚠️ 標準: コード品質は標準的ですが、改善の余地があります。")
        elif self.total_score >= 30:
            lines.append("\n⚠️ 要改善: コード品質に問題があります。改善が必要です。")
        else:
            lines.append(
                "\n❌ 危険: コード品質に深刻な問題があります。早急な対応が必要です。"
            )

        return "\n".join(lines)
