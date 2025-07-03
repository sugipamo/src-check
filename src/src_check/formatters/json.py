"""JSON formatter for machine-readable output."""

import json
from typing import Any, Dict, List

from src_check.formatters import BaseFormatter
from src_check.models.check_result import CheckResult
from src_check.models.simple_kpi_score import KpiScore


class JsonFormatter(BaseFormatter):
    """Formatter for JSON output."""

    def format(self, results: Dict[str, List[CheckResult]], kpi: KpiScore) -> str:
        """Format results as JSON.

        Args:
            results: Dictionary mapping file paths to their check results
            kpi: Overall KPI score

        Returns:
            JSON string
        """
        from datetime import datetime

        # Convert results to serializable format
        output_data: Dict[str, Any] = {
            "metadata": {
                "version": "0.2.0",
                "timestamp": datetime.now().isoformat(),
            },
            "kpi_score": {
                "overall_score": kpi.overall_score,
                "category_scores": kpi.category_scores,
                "total_issues": kpi.total_issues,
                "critical_issues": kpi.critical_issues,
                "high_issues": kpi.high_issues,
                "medium_issues": kpi.medium_issues,
                "low_issues": kpi.low_issues,
            },
            "results": {},  # For backwards compatibility
            "files": {},
        }

        # Add file results to both 'results' and 'files' for compatibility
        for file_path, file_results in results.items():
            file_data = [
                {
                    "rule_id": result.rule_id or result.checker_name,
                    "severity": result.severity.value,
                    "category": result.category,
                    "failure_count": result.failure_count,
                    "fix_policy": result.fix_policy,
                    "failures": [
                        {
                            "line": loc.line,
                            "column": loc.column,
                            "message": loc.message,
                            "code_snippet": loc.code_snippet,
                        }
                        for loc in result.failure_locations
                    ],
                }
                for result in file_results
            ]
            output_data["files"][file_path] = file_data
            output_data["results"][file_path] = file_data  # Duplicate for compatibility

        return json.dumps(output_data, indent=2)
