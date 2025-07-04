"""Tests for the DependencyChecker."""

import ast
from pathlib import Path
from unittest.mock import mock_open, patch

from src_check.rules.dependency import DependencyChecker


class TestDependencyChecker:
    """Test suite for DependencyChecker."""

    def setup_method(self):
        """Set up test method."""
        self.checker = DependencyChecker()

    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies."""
        # Directly set up a circular dependency in the import graph
        self.checker.import_graph = {
            "module1": {"module2"},
            "module2": {"module3"},
            "module3": {"module1"},
        }

        results = self.checker._check_circular_dependencies()
        assert len(results) > 0
        assert any(r.rule_id == "DEP001" for r in results)
        assert any("Circular dependency" in r.title for r in results)

    def test_unused_dependency_detection(self):
        """Test detection of unused dependencies."""
        # Set up imports and dependencies
        self.checker.project_imports = {"requests", "numpy", "pandas"}
        self.checker.declared_dependencies = {
            "requests": ">=2.0.0",
            "numpy": ">=1.0.0",
            "pandas": ">=1.0.0",
            "unused-package": ">=1.0.0",
        }

        results = self.checker._check_unused_dependencies()
        assert len(results) > 0
        assert any(r.rule_id == "DEP002" for r in results)
        assert any(
            "unused-package" in failure.message
            for r in results
            for failure in r.failure_locations
        )

    def test_unpinned_version_detection(self):
        """Test detection of unpinned dependency versions."""
        self.checker.declared_dependencies = {
            "requests": "",  # No version spec
            "numpy": "*",  # Wildcard
            "pandas": ">=1.0.0",  # Properly pinned
            "pytest": "latest",  # Invalid spec
        }

        results = self.checker._check_unpinned_versions()
        assert len(results) >= 3
        assert any(r.rule_id == "DEP006" for r in results)
        assert any(
            "requests" in failure.message
            for r in results
            for failure in r.failure_locations
        )
        assert any(
            "numpy" in failure.message
            for r in results
            for failure in r.failure_locations
        )

    def test_dev_prod_mixing_detection(self):
        """Test detection of dev dependencies in production."""
        self.checker.declared_dependencies = {
            "requests": ">=2.0.0",
            "pytest": ">=6.0.0",  # Dev dependency
            "black": ">=20.0.0",  # Dev dependency
            "numpy": ">=1.0.0",
        }
        self.checker.dev_dependencies = set()  # No dev dependencies declared

        results = self.checker._check_dev_prod_mixing()
        assert len(results) >= 2
        assert any(r.rule_id == "DEP007" for r in results)
        assert any(
            "pytest" in failure.message
            for r in results
            for failure in r.failure_locations
        )
        assert any(
            "black" in failure.message
            for r in results
            for failure in r.failure_locations
        )

    def test_requirements_txt_parsing(self):
        """Test parsing of requirements.txt file."""
        requirements_content = """
# This is a comment
requests>=2.25.0
numpy==1.19.5
pandas>=1.2.0,<2.0.0

# Dev dependencies
pytest>=6.0.0
black>=20.8b1
"""

        with patch("builtins.open", mock_open(read_data=requirements_content)):
            self.checker._parse_requirements_txt(Path("requirements.txt"))

        assert "requests" in self.checker.declared_dependencies
        assert self.checker.declared_dependencies["requests"] == ">=2.25.0"
        assert "numpy" in self.checker.declared_dependencies
        assert self.checker.declared_dependencies["numpy"] == "==1.19.5"
        assert "pandas" in self.checker.declared_dependencies

    def test_pyproject_toml_parsing(self):
        """Test parsing of pyproject.toml file."""
        pyproject_content = """
[project]
dependencies = [
    "requests>=2.25.0",
    "numpy==1.19.5",
    "pandas>=1.2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=6.0.0",
    "black>=20.8b1",
]
test = [
    "coverage>=5.0",
]
"""

        with patch("builtins.open", mock_open(read_data=pyproject_content)), patch("toml.load") as mock_toml:
                mock_toml.return_value = {
                    "project": {
                        "dependencies": [
                            "requests>=2.25.0",
                            "numpy==1.19.5",
                            "pandas>=1.2.0",
                        ],
                        "optional-dependencies": {
                            "dev": ["pytest>=6.0.0", "black>=20.8b1"],
                            "test": ["coverage>=5.0"],
                        },
                    }
                }
                self.checker._parse_pyproject_toml(Path("pyproject.toml"))

        assert "requests" in self.checker.declared_dependencies
        assert "pytest" in self.checker.dev_dependencies
        assert "coverage" in self.checker.dev_dependencies

    def test_import_analysis(self):
        """Test import analysis in Python files."""
        content = """
import os
import sys
from pathlib import Path
import requests
from numpy import array
from .local_module import helper
import pkg.submodule
"""

        self.checker._analyze_file_imports(Path("test.py"), content)

        assert "os" in self.checker.project_imports
        assert "sys" in self.checker.project_imports
        assert "pathlib" in self.checker.project_imports
        assert "requests" in self.checker.project_imports
        assert "numpy" in self.checker.project_imports

    def test_local_import_detection(self):
        """Test detection of local vs external imports."""
        self.checker.declared_dependencies = {"requests": ">=2.0.0"}

        # Standard library
        assert not self.checker._is_local_import("os", Path("/project/file.py"))
        assert not self.checker._is_local_import("json", Path("/project/file.py"))

        # Declared dependency
        assert not self.checker._is_local_import("requests", Path("/project/file.py"))

        # Local import (would need filesystem check in real scenario)
        # This test assumes the module doesn't exist in dependencies or stdlib

    def test_check_method_integration(self):
        """Test the main check method integration."""
        content = """
import requests
import local_module

def main():
    response = requests.get("http://example.com")
    local_module.process(response)
"""

        # Test AST-based check method
        tree = ast.parse(content)
        result = self.checker.check(tree, "/project/main.py")

        # Should return None for individual files
        assert result is None

        # Should have analyzed imports
        assert "requests" in self.checker.project_imports
        assert "local_module" in self.checker.project_imports

    def test_check_project_method(self):
        """Test the project-level check method."""
        # Set up some test data
        self.checker.declared_dependencies = {"requests": ">=2.0.0", "unused": "1.0.0"}
        self.checker.project_imports = {"requests"}

        with patch.object(self.checker, "_parse_dependency_files"):
            results = self.checker.check_project(Path("/project"))

        # Should check for unused dependencies
        assert any(
            r.rule_id == "DEP002"
            and any("unused" in f.message for f in r.failure_locations)
            for r in results
        )

    def test_package_name_mapping(self):
        """Test common import name to package name mappings."""
        content = """
import PIL
import cv2
import sklearn
import yaml
"""

        self.checker._analyze_file_imports(Path("test.py"), content)
        self.checker.declared_dependencies = {
            "pillow": ">=8.0.0",
            "opencv-python": ">=4.0.0",
            "scikit-learn": ">=0.24.0",
            "pyyaml": ">=5.0.0",
        }

        # The checker should map these correctly
        results = self.checker._check_unused_dependencies()

        # These should not be marked as unused because of the mapping
        assert not any(
            "pillow" in f.message for r in results for f in r.failure_locations
        )
        assert not any(
            "opencv-python" in f.message for r in results for f in r.failure_locations
        )

    def test_results_summary(self):
        """Test the results summary generation."""
        from src_check.models.check_result import CheckResult, Severity

        results = []

        # Create test results with proper structure
        for rule_id, title in [
            ("DEP001", "Circular dependency"),
            ("DEP002", "Unused dependency"),
            ("DEP002", "Another unused"),
            ("DEP006", "Unpinned version"),
            ("DEP007", "Dev in prod"),
        ]:
            result = CheckResult(
                title=title,
                checker_name="dependency",
                severity=Severity.HIGH if rule_id == "DEP001" else Severity.MEDIUM,
                category="dependency",
                rule_id=rule_id,
            )
            result.add_failure(file_path="test.py", line=1, message=title)
            results.append(result)

        summary = self.checker.get_results_summary(results)

        assert summary["total_issues"] == 5
        assert summary["circular_dependencies"] == 1
        assert summary["unused_dependencies"] == 2
        assert summary["unpinned_versions"] == 1
        assert summary["dev_prod_mixing"] == 1
