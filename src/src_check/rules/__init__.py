"""
Quality checker rules for src-check.
"""

from src_check.rules.architecture import ArchitectureChecker
from src_check.rules.code_quality import CodeQualityChecker
from src_check.rules.dependency import DependencyChecker
from src_check.rules.deprecation import DeprecationChecker
from src_check.rules.documentation import DocumentationChecker
from src_check.rules.license import LicenseChecker
from src_check.rules.performance import PerformanceChecker
from src_check.rules.security import SecurityChecker
from src_check.rules.test_quality import TestQualityChecker
from src_check.rules.type_hints import TypeHintChecker

__all__ = [
    "ArchitectureChecker",
    "CodeQualityChecker",
    "DependencyChecker",
    "DeprecationChecker",
    "DocumentationChecker",
    "LicenseChecker",
    "PerformanceChecker",
    "SecurityChecker",
    "TestQualityChecker",
    "TypeHintChecker",
]
