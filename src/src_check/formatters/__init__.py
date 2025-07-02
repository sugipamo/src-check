"""Output formatters for src-check results."""
from abc import ABC, abstractmethod
from typing import Dict, List

from src_check.models.check_result import CheckResult
from src_check.models.simple_kpi_score import KpiScore


class BaseFormatter(ABC):
    """Abstract base class for output formatters."""
    
    @abstractmethod
    def format(self, results: Dict[str, List[CheckResult]], kpi: KpiScore) -> str:
        """Format check results and KPI score.
        
        Args:
            results: Dictionary mapping file paths to their check results
            kpi: Overall KPI score
            
        Returns:
            Formatted output string
        """
        pass