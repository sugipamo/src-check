"""License compliance checker for Python projects."""

import ast
import importlib.metadata
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import toml

from src_check.core.base import BaseChecker
from src_check.models.check_result import CheckResult, Severity


class LicenseChecker(BaseChecker):
    """Check for license compliance and consistency issues."""

    @property
    def name(self) -> str:
        return "license"

    @property
    def description(self) -> str:
        return "License compliance and consistency checks"

    @property
    def category(self) -> str:
        return "compliance"

    def __init__(self):
        """Initialize the license checker."""
        super().__init__()
        # Common license patterns for detection
        self.license_patterns = {
            "MIT": r"MIT License|Permission is hereby granted, free of charge",
            "Apache-2.0": r"Apache License.*Version 2\.0|apache.*2\.0",
            "GPL-3.0": r"GNU GENERAL PUBLIC LICENSE.*Version 3",
            "GPL-2.0": r"GNU GENERAL PUBLIC LICENSE.*Version 2",
            "BSD-3-Clause": r"BSD 3-Clause License|Redistribution and use in source and binary forms",
            "BSD-2-Clause": r"BSD 2-Clause License",
            "ISC": r"ISC License",
            "LGPL-3.0": r"GNU LESSER GENERAL PUBLIC LICENSE.*Version 3",
            "LGPL-2.1": r"GNU LESSER GENERAL PUBLIC LICENSE.*Version 2\.1",
            "MPL-2.0": r"Mozilla Public License.*Version 2\.0",
            "Unlicense": r"This is free and unencumbered software released into the public domain",
        }
        
        # License compatibility matrix (simplified)
        self.compatibility_matrix = {
            "MIT": ["MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause", "ISC", "Unlicense"],
            "Apache-2.0": ["MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause", "ISC", "Unlicense"],
            "BSD-3-Clause": ["MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause", "ISC", "Unlicense"],
            "BSD-2-Clause": ["MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause", "ISC", "Unlicense"],
            "ISC": ["MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause", "ISC", "Unlicense"],
            "GPL-3.0": ["GPL-3.0", "GPL-2.0", "LGPL-3.0", "LGPL-2.1"],
            "GPL-2.0": ["GPL-2.0", "LGPL-2.1"],
            "LGPL-3.0": ["LGPL-3.0", "LGPL-2.1", "MIT", "Apache-2.0", "BSD-3-Clause"],
            "LGPL-2.1": ["LGPL-2.1", "MIT", "Apache-2.0", "BSD-3-Clause"],
            "Unlicense": ["MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause", "ISC", "Unlicense"],
        }
        
        # Copyleft licenses
        self.copyleft_licenses = {"GPL-3.0", "GPL-2.0", "LGPL-3.0", "LGPL-2.1", "AGPL-3.0", "MPL-2.0"}
        
        # Track if we've already checked project-level stuff
        self._project_checked = False
        self._project_license = None

    def check(self, ast_tree: ast.AST, file_path: str) -> Optional[CheckResult]:
        """Check license compliance for the file."""
        result = self.create_result("License Compliance Check")
        
        # Find project root
        path = Path(file_path)
        root_path = path.parent
        while root_path.parent != root_path:
            if any((root_path / name).exists() for name in ["pyproject.toml", "setup.py", ".git"]):
                break
            root_path = root_path.parent
        
        # Check project-level license only once
        if not self._project_checked:
            self._project_checked = True
            self._project_license = self._find_project_license(root_path, result)
            
            # Check pyproject.toml for license info
            pyproject_license = self._check_pyproject_license(root_path, result)
            
            # Check for license mismatch
            if self._project_license and pyproject_license and self._project_license != pyproject_license:
                result.metadata["LIC007"] = True
                result.add_failure(
                    file_path=str(root_path / "pyproject.toml"),
                    line=0,
                    column=0,
                    message=f"License mismatch: LICENSE file ({self._project_license}) vs pyproject.toml ({pyproject_license})",
                )
                result.severity = Severity.HIGH
            
            # Use the found license (prefer LICENSE file)
            detected_license = self._project_license or pyproject_license
            
            # Check dependency licenses
            if detected_license:
                self._check_dependency_licenses(detected_license, result)
        
        # Check copyright header in this specific file
        self._check_copyright_header(file_path, result)
        
        return result if result.failure_locations else None

    def _find_project_license(self, root_path: Path, result: CheckResult) -> Optional[str]:
        """Find and identify the project's LICENSE file."""
        license_files = []
        for pattern in ["LICENSE", "LICENSE.txt", "LICENSE.md", "LICENCE", "LICENCE.txt", "LICENCE.md"]:
            license_file = root_path / pattern
            if license_file.exists() and license_file.is_file():
                license_files.append(license_file)
        
        if not license_files:
            result.metadata["LIC001"] = True
            result.add_failure(
                file_path=str(root_path),
                line=0,
                column=0,
                message="LICENSE file not found in project root",
            )
            result.severity = Severity.HIGH
            return None
        
        # Read and identify license type from the first LICENSE file
        license_file = license_files[0]
        try:
            with open(license_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Try to identify the license
            for license_name, pattern in self.license_patterns.items():
                if re.search(pattern, content, re.IGNORECASE):
                    return license_name
            
            # Unrecognized license
            result.metadata["LIC002"] = True
            result.add_failure(
                file_path=str(license_file),
                line=0,
                column=0,
                message="Unrecognized license format",
            )
            result.severity = Severity.MEDIUM
            return "UNKNOWN"
            
        except Exception as e:
            result.metadata["LIC002"] = True
            result.add_failure(
                file_path=str(license_file),
                line=0,
                column=0,
                message=f"Error reading LICENSE file: {e}",
            )
            result.severity = Severity.MEDIUM
            return None

    def _check_pyproject_license(self, root_path: Path, result: CheckResult) -> Optional[str]:
        """Check license information in pyproject.toml."""
        pyproject_path = root_path / "pyproject.toml"
        if not pyproject_path.exists():
            return None
        
        try:
            with open(pyproject_path, "r", encoding="utf-8") as f:
                data = toml.load(f)
            
            # Check for license in project metadata
            if "project" in data and "license" in data["project"]:
                license_info = data["project"]["license"]
                if isinstance(license_info, str):
                    return license_info
                elif isinstance(license_info, dict) and "text" in license_info:
                    # Try to identify from text
                    for license_name, pattern in self.license_patterns.items():
                        if re.search(pattern, license_info["text"], re.IGNORECASE):
                            return license_name
                    return license_info["text"]
            
        except Exception:
            pass
        
        return None

    def _check_dependency_licenses(self, project_license: str, result: CheckResult) -> None:
        """Check licenses of installed dependencies."""
        try:
            for dist in importlib.metadata.distributions():
                pkg_name = dist.metadata.get("Name", "Unknown")
                pkg_license = dist.metadata.get("License", None)
                
                if not pkg_license:
                    result.metadata.setdefault("LIC008", []).append(pkg_name)
                    result.add_failure(
                        file_path="requirements",
                        line=0,
                        column=0,
                        message=f"Package '{pkg_name}' has no license information",
                    )
                    if result.severity.value < Severity.LOW.value:
                        result.severity = Severity.LOW
                    continue
                
                # Check for copyleft licenses
                if any(copyleft in pkg_license for copyleft in self.copyleft_licenses):
                    result.metadata.setdefault("LIC004", []).append(pkg_name)
                    result.add_failure(
                        file_path="requirements",
                        line=0,
                        column=0,
                        message=f"Copyleft license detected in dependency '{pkg_name}': {pkg_license}",
                    )
                    # Set severity to MEDIUM if it's lower
                    result.severity = Severity.MEDIUM
                
                # Check compatibility
                if project_license in self.compatibility_matrix:
                    compatible_licenses = self.compatibility_matrix[project_license]
                    # Try to match the package license with known licenses
                    pkg_license_type = None
                    for license_name, pattern in self.license_patterns.items():
                        if re.search(pattern, pkg_license, re.IGNORECASE):
                            pkg_license_type = license_name
                            break
                    
                    if pkg_license_type and pkg_license_type not in compatible_licenses:
                        result.metadata.setdefault("LIC003", []).append(pkg_name)
                        result.add_failure(
                            file_path="requirements",
                            line=0,
                            column=0,
                            message=f"License compatibility issue: package '{pkg_name}' has license '{pkg_license}' which may be incompatible with project license '{project_license}'",
                        )
                        result.severity = Severity.HIGH
                        
        except Exception:
            pass

    def _check_copyright_header(self, file_path: str, result: CheckResult) -> None:
        """Check for copyright headers in source files."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Look for copyright in the first 1000 characters
            header = content[:1000]
            
            # Check for copyright mention
            copyright_match = re.search(r"Copyright\s*\(c\)\s*(\d{4})", header, re.IGNORECASE)
            if not copyright_match:
                result.metadata["LIC005"] = True
                result.add_failure(
                    file_path=file_path,
                    line=1,
                    column=0,
                    message="Missing copyright header",
                )
                if result.severity == Severity.MEDIUM:
                    result.severity = Severity.LOW
                return
            
            # Check copyright year
            year = int(copyright_match.group(1))
            current_year = datetime.now().year
            if year < current_year - 5:  # More than 5 years old
                result.metadata["LIC006"] = True
                result.add_failure(
                    file_path=file_path,
                    line=1,
                    column=0,
                    message=f"Old copyright year ({year}) - consider updating to {current_year}",
                )
                # Set to INFO severity
                result.severity = Severity.INFO
                
        except Exception:
            pass