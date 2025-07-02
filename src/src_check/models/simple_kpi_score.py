"""Simple KPI score model for src-check."""

from dataclasses import dataclass
from typing import Dict


@dataclass
class KpiScore:
    """Simple KPI score with category breakdown."""

    overall_score: float
    category_scores: Dict[str, float]
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
