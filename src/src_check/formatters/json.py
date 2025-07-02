"""JSON formatter for machine-readable output."""
import json
from typing import Dict, List

from src_check.formatters import BaseFormatter
from src_check.models.check_result import CheckResult
from src_check.models.kpi_score import KpiScore


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
        # Convert results to serializable format
        output_data = {
            "kpi_score": {
                "overall_score": kpi.overall_score,
                "category_scores": kpi.category_scores,
                "total_issues": kpi.total_issues,
                "critical_issues": kpi.critical_issues,
                "high_issues": kpi.high_issues,
                "medium_issues": kpi.medium_issues,
                "low_issues": kpi.low_issues
            },
            "files": {}
        }
        
        # Add file results
        for file_path, file_results in results.items():
            output_data["files"][file_path] = [
                {
                    "rule_id": result.rule_id,
                    "message": result.message,
                    "severity": result.severity.value,
                    "category": result.category,
                    "line": result.line,
                    "column": result.column,
                    "end_line": result.end_line,
                    "end_column": result.end_column,
                    "suggestion": result.suggestion,
                    "additional_info": result.additional_info
                }
                for result in file_results
            ]
            
        return json.dumps(output_data, indent=2)