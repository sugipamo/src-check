"""
src-check: Python code quality analysis and KPI scoring system.

A comprehensive tool for analyzing Python codebases with:
- Dynamic code quality checking
- KPI scoring (0-100 points)
- Automatic code correction
- Comprehensive import management
"""

__version__ = "0.2.0"
__author__ = "Development Team"
__email__ = "dev@example.com"

# Package metadata
__title__ = "src-check"
__description__ = "Python code quality analysis and KPI scoring system"
__url__ = "https://github.com/sugipamo/src-check"
__license__ = "MIT"

# Version info tuple
try:
    VERSION_INFO = tuple(map(int, __version__.split(".")))  # noqa: RUF048
except ValueError:
    # Handle non-numeric version components
    VERSION_INFO = (0, 2, 0)

# Placeholder for future imports
# from .core import CheckResult, KPIScore, FailureLocation

__all__ = [
    "VERSION_INFO",
    "__author__",
    "__email__",
    "__version__",
    # "CheckResult",
    # "KPIScore",
    # "FailureLocation",
]


def main() -> None:
    """Temporary main function for initial testing."""
    print("Hello from src-check!")
