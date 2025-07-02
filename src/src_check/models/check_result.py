"""
Data models for check results and failure locations.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Severity(Enum):
    """Severity levels for issues."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class FailureLocation:
    """Represents a location where a check failed."""

    file_path: str
    line: int
    column: Optional[int] = None
    end_line: Optional[int] = None
    end_column: Optional[int] = None
    message: str = ""
    code_snippet: Optional[str] = None

    def __str__(self) -> str:
        """String representation of failure location."""
        location = f"{self.file_path}:{self.line}"
        if self.column is not None:
            location += f":{self.column}"
        if self.message:
            location += f" - {self.message}"
        return location

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "file_path": self.file_path,
            "line": self.line,
            "column": self.column,
            "end_line": self.end_line,
            "end_column": self.end_column,
            "message": self.message,
            "code_snippet": self.code_snippet,
        }


@dataclass
class CheckResult:
    """Result of a quality check."""

    title: str
    checker_name: str
    failure_locations: List[FailureLocation] = field(default_factory=list)
    fix_policy: str = ""
    fix_example_code: Optional[str] = None
    severity: Severity = Severity.MEDIUM
    category: str = "general"
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        """Check if the test passed (no failures)."""
        return len(self.failure_locations) == 0

    @property
    def failure_count(self) -> int:
        """Number of failures found."""
        return len(self.failure_locations)

    def add_failure(
        self,
        file_path: str,
        line: int,
        message: str,
        column: Optional[int] = None,
        **kwargs,
    ) -> None:
        """Add a failure location."""
        failure = FailureLocation(
            file_path=file_path, line=line, column=column, message=message, **kwargs
        )
        self.failure_locations.append(failure)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "checker_name": self.checker_name,
            "passed": self.passed,
            "failure_count": self.failure_count,
            "failures": [loc.to_dict() for loc in self.failure_locations],
            "fix_policy": self.fix_policy,
            "fix_example_code": self.fix_example_code,
            "severity": self.severity.value,
            "category": self.category,
            "metadata": self.metadata,
        }

    def format_report(self, verbose: bool = False) -> str:
        """Format the result as a human-readable report."""
        lines = []

        # Header
        status = (
            "✅ PASSED" if self.passed else f"❌ FAILED ({self.failure_count} issues)"
        )
        lines.append(f"\n{self.title} - {status}")
        lines.append("=" * 60)

        if not self.passed:
            # Show failures
            lines.append(f"\nSeverity: {self.severity.value.upper()}")
            lines.append(f"Category: {self.category}")
            lines.append("\nFailures found:")

            for i, loc in enumerate(self.failure_locations, 1):
                lines.append(f"{i}. {loc}")
                if verbose and loc.code_snippet:
                    lines.append(f"   Code: {loc.code_snippet}")

            # Fix policy
            if self.fix_policy:
                lines.append("\nFix Policy:")
                lines.append(self.fix_policy)

            # Example fix
            if self.fix_example_code:
                lines.append("\nExample Fix:")
                lines.append("```python")
                lines.append(self.fix_example_code)
                lines.append("```")

        return "\n".join(lines)
