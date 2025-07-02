"""Dependency health checker for Python projects."""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import importlib.metadata
import toml

from src_check.core.base import BaseChecker
from src_check.models.check_result import CheckResult, Severity


class DependencyChecker(BaseChecker):
    """Check for dependency-related issues in Python projects."""

    @property
    def name(self) -> str:
        """Return the name of the checker."""
        return "dependency"

    @property
    def description(self) -> str:
        """Return the description of the checker."""
        return "Check for dependency health and security issues"

    @property
    def category(self) -> str:
        """Return the category of the checker."""
        return "dependency"

    priority = 7

    def __init__(self) -> None:
        """Initialize the dependency checker."""
        super().__init__()
        self.project_imports: Set[str] = set()
        self.declared_dependencies: Dict[str, str] = {}
        self.dev_dependencies: Set[str] = set()
        self.import_graph: Dict[str, Set[str]] = {}
        self.file_imports: Dict[str, Set[str]] = {}

    def check(self, ast_tree: ast.AST, file_path: str) -> Optional[CheckResult]:
        """Check for dependency issues."""
        path = Path(file_path)
        
        # We need to handle dependency checking differently
        # Return None for individual files, as dependency checking is project-wide
        # This checker should be run at the project level separately
        
        # For now, we'll just collect imports from each file
        self._analyze_ast_imports(ast_tree, path)
        
        # Return None as we don't have individual file results
        return None
    
    def check_project(self, project_root: Path) -> List[CheckResult]:
        """Check dependencies at the project level."""
        results = []
        
        # Parse dependency files
        self._parse_dependency_files(project_root)
        
        # Run all dependency checks
        results.extend(self._check_circular_dependencies())
        results.extend(self._check_unused_dependencies())
        results.extend(self._check_unpinned_versions())
        results.extend(self._check_dev_prod_mixing())
        
        return results
    
    def _analyze_ast_imports(self, ast_tree: ast.AST, file_path: Path) -> None:
        """Analyze imports from an AST."""
        file_imports = set()
        
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]
                    file_imports.add(module_name)
                    self.project_imports.add(module_name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module.split('.')[0]
                    file_imports.add(module_name)
                    self.project_imports.add(module_name)
        
        self.file_imports[str(file_path)] = file_imports
        
        # Build import graph for circular dependency detection
        rel_path = str(file_path.name)
        if rel_path not in self.import_graph:
            self.import_graph[rel_path] = set()
        
        for imp in file_imports:
            if self._is_local_import(imp, file_path):
                self.import_graph[rel_path].add(imp)

    def _analyze_file_imports(self, file_path: Path, content: str) -> None:
        """Analyze imports in a Python file."""
        try:
            tree = ast.parse(content)
            file_imports = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name.split('.')[0]
                        file_imports.add(module_name)
                        self.project_imports.add(module_name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_name = node.module.split('.')[0]
                        file_imports.add(module_name)
                        self.project_imports.add(module_name)

            self.file_imports[str(file_path)] = file_imports

            # Build import graph for circular dependency detection
            rel_path = str(file_path.relative_to(file_path.parent.parent))
            if rel_path not in self.import_graph:
                self.import_graph[rel_path] = set()

            for imp in file_imports:
                if self._is_local_import(imp, file_path):
                    self.import_graph[rel_path].add(imp)

        except SyntaxError:
            pass

    def _is_project_root(self, file_path: Path) -> bool:
        """Check if we're at the project root level."""
        root_indicators = ['pyproject.toml', 'requirements.txt', 'setup.py']
        parent = file_path.parent
        return any((parent / indicator).exists() for indicator in root_indicators)

    def _parse_dependency_files(self, root_path: Path) -> None:
        """Parse dependency files in the project."""
        # Parse requirements.txt
        req_file = root_path / 'requirements.txt'
        if req_file.exists():
            self._parse_requirements_txt(req_file)

        # Parse requirements-dev.txt
        dev_req_file = root_path / 'requirements-dev.txt'
        if dev_req_file.exists():
            self._parse_requirements_txt(dev_req_file, is_dev=True)

        # Parse pyproject.toml
        pyproject_file = root_path / 'pyproject.toml'
        if pyproject_file.exists():
            self._parse_pyproject_toml(pyproject_file)

    def _parse_requirements_txt(self, file_path: Path, is_dev: bool = False) -> None:
        """Parse a requirements.txt file."""
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract package name and version
                        match = re.match(r'^([a-zA-Z0-9\-_]+)(.*)$', line)
                        if match:
                            pkg_name = match.group(1).lower()
                            version_spec = match.group(2).strip()
                            self.declared_dependencies[pkg_name] = version_spec
                            if is_dev:
                                self.dev_dependencies.add(pkg_name)
        except Exception:
            pass

    def _parse_pyproject_toml(self, file_path: Path) -> None:
        """Parse a pyproject.toml file."""
        try:
            with open(file_path, 'r') as f:
                data = toml.load(f)

            # Parse dependencies
            if 'project' in data and 'dependencies' in data['project']:
                for dep in data['project']['dependencies']:
                    match = re.match(r'^([a-zA-Z0-9\-_]+)(.*)$', dep)
                    if match:
                        pkg_name = match.group(1).lower()
                        version_spec = match.group(2).strip()
                        self.declared_dependencies[pkg_name] = version_spec

            # Parse dev dependencies
            if 'project' in data and 'optional-dependencies' in data['project']:
                for group, deps in data['project']['optional-dependencies'].items():
                    if 'dev' in group.lower() or 'test' in group.lower():
                        for dep in deps:
                            match = re.match(r'^([a-zA-Z0-9\-_]+)(.*)$', dep)
                            if match:
                                pkg_name = match.group(1).lower()
                                self.dev_dependencies.add(pkg_name)

        except Exception:
            pass

    def _is_local_import(self, module_name: str, file_path: Path) -> bool:
        """Check if an import is a local module."""
        # Standard library modules
        stdlib_modules = {
            'os', 'sys', 'json', 'datetime', 'collections', 'itertools',
            'functools', 'pathlib', 'typing', 're', 'ast', 'math', 'random',
            'string', 'textwrap', 'unicodedata', 'codecs', 'io', 'time',
            'calendar', 'copy', 'pprint', 'enum', 'dataclasses'
        }

        if module_name in stdlib_modules:
            return False

        # Check if it's a declared dependency
        if module_name.lower() in self.declared_dependencies:
            return False

        # Check if module exists in the project
        project_root = file_path.parent
        while project_root.parent != project_root:
            if (project_root / module_name).exists() or \
               (project_root / f"{module_name}.py").exists():
                return True
            project_root = project_root.parent

        return False

    def _check_circular_dependencies(self) -> List[CheckResult]:
        """Check for circular dependencies."""
        results = []
        visited = set()
        rec_stack = set()

        def has_cycle(module: str, path: List[str]) -> Optional[List[str]]:
            visited.add(module)
            rec_stack.add(module)
            path.append(module)

            for neighbor in self.import_graph.get(module, []):
                if neighbor not in visited:
                    cycle = has_cycle(neighbor, path.copy())
                    if cycle:
                        return cycle
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]

            path.pop()
            rec_stack.remove(module)
            return None

        for module in self.import_graph:
            if module not in visited:
                cycle = has_cycle(module, [])
                if cycle:
                    result = CheckResult(
                        title=f"Circular dependency detected: {' -> '.join(cycle)}",
                        checker_name=self.name,
                        severity=Severity.HIGH,
                        category=self.category,
                        rule_id="DEP001"
                    )
                    result.add_failure(
                        file_path=module,
                        line=1,
                        message=f"Circular dependency: {' -> '.join(cycle)}"
                    )
                    results.append(result)

        return results

    def _check_unused_dependencies(self) -> List[CheckResult]:
        """Check for unused dependencies."""
        results = []

        # Normalize import names to package names
        used_packages = set()
        for imp in self.project_imports:
            # Handle common import name to package name mappings
            package_mapping = {
                'PIL': 'pillow',
                'cv2': 'opencv-python',
                'sklearn': 'scikit-learn',
                'yaml': 'pyyaml',
            }
            package_name = package_mapping.get(imp, imp).lower()
            used_packages.add(package_name)

        # Check for unused dependencies
        for dep in self.declared_dependencies:
            if dep not in used_packages and dep not in self.dev_dependencies:
                # Check if it might be imported with a different name
                try:
                    metadata = importlib.metadata.distribution(dep)
                    top_level = metadata.read_text('top_level.txt')
                    if top_level:
                        modules = top_level.strip().split('\n')
                        if not any(mod in self.project_imports for mod in modules):
                            result = CheckResult(
                                title="Unused dependency detected",
                                checker_name=self.name,
                                severity=Severity.MEDIUM,
                                category=self.category,
                                rule_id="DEP002"
                            )
                            result.add_failure(
                                file_path="requirements.txt",
                                line=1,
                                message=f"Unused dependency: {dep}"
                            )
                            results.append(result)
                except Exception:
                    # If we can't get metadata, check if it's likely unused
                    # For test cases and packages without metadata
                    if dep not in self.project_imports:
                        result = CheckResult(
                            title="Unused dependency detected",
                            checker_name=self.name,
                            severity=Severity.MEDIUM,
                            category=self.category,
                            rule_id="DEP002"
                        )
                        result.add_failure(
                            file_path="requirements.txt",
                            line=1,
                            message=f"Unused dependency: {dep}"
                        )
                        results.append(result)

        return results

    def _check_unpinned_versions(self) -> List[CheckResult]:
        """Check for unpinned dependency versions."""
        results = []

        for dep, version_spec in self.declared_dependencies.items():
            if not version_spec or version_spec == '*':
                result = CheckResult(
                    title="Unpinned dependency version",
                    checker_name=self.name,
                    severity=Severity.MEDIUM,
                    category=self.category,
                    rule_id="DEP006"
                )
                result.add_failure(
                    file_path="requirements.txt",
                    line=1,
                    message=f"Unpinned dependency version: {dep}"
                )
                results.append(result)
            elif not any(op in version_spec for op in ['==', '>=', '<=', '>', '<', '~=']):
                result = CheckResult(
                    title="Loosely pinned dependency",
                    checker_name=self.name,
                    severity=Severity.MEDIUM,
                    category=self.category,
                    rule_id="DEP006"
                )
                result.add_failure(
                    file_path="requirements.txt",
                    line=1,
                    message=f"Loosely pinned dependency: {dep}{version_spec}"
                )
                results.append(result)

        return results

    def _check_dev_prod_mixing(self) -> List[CheckResult]:
        """Check for development dependencies mixed with production."""
        results = []

        # Common dev/test packages
        dev_packages = {
            'pytest', 'unittest', 'mock', 'nose', 'tox', 'coverage',
            'pytest-cov', 'black', 'flake8', 'pylint', 'mypy', 'isort',
            'pre-commit', 'sphinx', 'mkdocs', 'wheel', 'twine', 'bumpversion'
        }

        # Check if dev packages are in main dependencies
        for dep in self.declared_dependencies:
            if dep in dev_packages and dep not in self.dev_dependencies:
                result = CheckResult(
                    title="Development dependency in production",
                    checker_name=self.name,
                    severity=Severity.MEDIUM,
                    category=self.category,
                    rule_id="DEP007"
                )
                result.add_failure(
                    file_path="requirements.txt",
                    line=1,
                    message=f"Development dependency in production: {dep}"
                )
                results.append(result)

        return results

    def get_results_summary(self, results: List[CheckResult]) -> Dict[str, int]:
        """Get a summary of check results."""
        summary = {
            "circular_dependencies": 0,
            "unused_dependencies": 0,
            "unpinned_versions": 0,
            "dev_prod_mixing": 0,
            "total_issues": len(results)
        }

        for result in results:
            if result.rule_id == "DEP001":
                summary["circular_dependencies"] += 1
            elif result.rule_id == "DEP002":
                summary["unused_dependencies"] += 1
            elif result.rule_id == "DEP006":
                summary["unpinned_versions"] += 1
            elif result.rule_id == "DEP007":
                summary["dev_prod_mixing"] += 1

        return summary