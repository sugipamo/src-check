"""Tests for the LicenseChecker."""

import ast
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from src_check.models.check_result import Severity
from src_check.rules.license import LicenseChecker


class TestLicenseChecker:
    """Test suite for LicenseChecker."""

    def setup_method(self):
        """Set up test fixtures."""
        self.checker = LicenseChecker()

    def test_license_checker_initialization(self):
        """Test LicenseChecker initialization."""
        assert self.checker.name == "license"
        assert self.checker.description == "License compliance and consistency checks"
        assert self.checker.category == "compliance"

    def test_no_license_file(self):
        """Test detection of missing LICENSE file."""
        with patch.object(Path, "exists", return_value=False):
            ast_tree = ast.parse("")
            result = self.checker.check(ast_tree, "test.py")

        assert result is not None
        assert len(result.failure_locations) >= 1
        assert "LIC001" in result.metadata
        assert any(
            "LICENSE file not found" in loc.message for loc in result.failure_locations
        )

    def test_mit_license_detection(self):
        """Test MIT license detection."""
        mit_license = """MIT License

Copyright (c) 2025 Test Author

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
"""
        source_code = '''"""Module with copyright header.

Copyright (c) 2025 Test Author
Licensed under the MIT License.
"""

def foo():
    pass
'''

        # Create a side effect function that properly handles the Path instance
        def exists_side_effect(self):
            return "LICENSE" in str(self) or "test.py" in str(self)

        def is_file_side_effect(self):
            return True

        with patch.object(Path, "exists", exists_side_effect):
            with patch.object(Path, "is_file", is_file_side_effect):
                with patch("builtins.open", mock_open()) as mock_file:
                    mock_file.return_value.read.side_effect = [mit_license, source_code]
                    with patch.object(Path, "iterdir", return_value=[Path("LICENSE")]):
                        ast_tree = ast.parse(source_code)
                        result = self.checker.check(ast_tree, "test.py")

        # Should not have critical issues
        if result:
            assert "LIC001" not in result.metadata
            assert "LIC002" not in result.metadata

    def test_unrecognized_license(self):
        """Test detection of unrecognized license."""
        unknown_license = """This is my custom license.
You can do whatever you want."""

        # Create a side effect function that properly handles the Path instance
        def exists_side_effect(self):
            return "LICENSE" in str(self)

        def is_file_side_effect(self):
            return True

        with patch.object(Path, "exists", exists_side_effect):
            with patch.object(Path, "is_file", is_file_side_effect):
                with patch("builtins.open", mock_open(read_data=unknown_license)):
                    with patch.object(Path, "iterdir", return_value=[Path("LICENSE")]):
                        ast_tree = ast.parse("")
                        result = self.checker.check(ast_tree, "test.py")

        assert result is not None
        assert "LIC002" in result.metadata

    def test_license_compatibility_check(self):
        """Test license compatibility checking."""
        # Mock installed packages with licenses
        mock_dist1 = MagicMock()
        mock_dist1.metadata = {"Name": "package1", "License": "GPL-3.0"}

        mock_dist2 = MagicMock()
        mock_dist2.metadata = {"Name": "package2", "License": "MIT"}

        mit_license = """MIT License"""

        # Create a side effect function that properly handles the Path instance
        def exists_side_effect(self):
            return "LICENSE" in str(self)

        def is_file_side_effect(self):
            return True

        with patch.object(Path, "exists", exists_side_effect):
            with patch.object(Path, "is_file", is_file_side_effect):
                with patch("builtins.open", mock_open(read_data=mit_license)):
                    with patch.object(Path, "iterdir", return_value=[Path("LICENSE")]):
                        with patch(
                            "importlib.metadata.distributions",
                            return_value=[mock_dist1, mock_dist2],
                        ):
                            ast_tree = ast.parse("")
                            result = self.checker.check(ast_tree, "test.py")

        assert result is not None
        assert "LIC003" in result.metadata
        assert any("GPL-3.0" in loc.message for loc in result.failure_locations)

    def test_copyleft_license_warning(self):
        """Test copyleft license detection."""
        mock_dist = MagicMock()
        mock_dist.metadata = {"Name": "gpl-package", "License": "GPL-2.0"}

        mit_license = """MIT License"""

        # Create a side effect function that properly handles the Path instance
        def exists_side_effect(self):
            return "LICENSE" in str(self)

        def is_file_side_effect(self):
            return True

        with patch.object(Path, "exists", exists_side_effect):
            with patch.object(Path, "is_file", is_file_side_effect):
                with patch("builtins.open", mock_open(read_data=mit_license)):
                    with patch.object(Path, "iterdir", return_value=[Path("LICENSE")]):
                        with patch(
                            "importlib.metadata.distributions", return_value=[mock_dist]
                        ):
                            ast_tree = ast.parse("")
                            result = self.checker.check(ast_tree, "test.py")

        assert result is not None
        assert "LIC004" in result.metadata

    def test_missing_copyright_header(self):
        """Test detection of missing copyright headers."""
        source_code = '''"""Module without copyright header."""

def foo():
    pass
'''
        mit_license = """MIT License"""

        # Create a side effect function that properly handles the Path instance
        def exists_side_effect(self):
            return "LICENSE" in str(self) or "test.py" in str(self)

        def is_file_side_effect(self):
            return True

        with patch.object(Path, "exists", exists_side_effect):
            with patch.object(Path, "is_file", is_file_side_effect):
                with patch("builtins.open", mock_open()) as mock_file:
                    mock_file.return_value.read.side_effect = [mit_license, source_code]
                    with patch.object(Path, "iterdir", return_value=[Path("LICENSE")]):
                        ast_tree = ast.parse(source_code)
                        result = self.checker.check(ast_tree, "test.py")

        assert result is not None
        assert "LIC005" in result.metadata

    def test_valid_copyright_header(self):
        """Test valid copyright header detection."""
        source_code = '''"""Module with copyright header.

Copyright (c) 2025 Test Author
Licensed under the MIT License.
"""

def foo():
    pass
'''
        mit_license = """MIT License"""

        # Create a side effect function that properly handles the Path instance
        def exists_side_effect(self):
            return "LICENSE" in str(self) or "test.py" in str(self)

        def is_file_side_effect(self):
            return True

        with patch.object(Path, "exists", exists_side_effect):
            with patch.object(Path, "is_file", is_file_side_effect):
                with patch("builtins.open", mock_open()) as mock_file:
                    mock_file.return_value.read.side_effect = [mit_license, source_code]
                    with patch.object(Path, "iterdir", return_value=[Path("LICENSE")]):
                        ast_tree = ast.parse(source_code)
                        result = self.checker.check(ast_tree, "test.py")

        # Should not have LIC005 issue for this file
        if result:
            assert "LIC005" not in result.metadata

    def test_old_copyright_year(self):
        """Test detection of old copyright years."""
        source_code = '''"""Module with old copyright.

Copyright (c) 2018 Test Author
"""

def foo():
    pass
'''
        mit_license = """MIT License"""

        # Create a side effect function that properly handles the Path instance
        def exists_side_effect(self):
            return "LICENSE" in str(self) or "test.py" in str(self)

        def is_file_side_effect(self):
            return True

        with patch.object(Path, "exists", exists_side_effect):
            with patch.object(Path, "is_file", is_file_side_effect):
                with patch("builtins.open", mock_open()) as mock_file:
                    mock_file.return_value.read.side_effect = [mit_license, source_code]
                    with patch.object(Path, "iterdir", return_value=[Path("LICENSE")]):
                        ast_tree = ast.parse(source_code)
                        result = self.checker.check(ast_tree, "test.py")

        assert result is not None
        assert "LIC006" in result.metadata

    def test_license_mismatch_pyproject(self):
        """Test detection of license mismatch between pyproject.toml and LICENSE."""
        pyproject_content = """
[project]
name = "test-package"
license = {text = "Apache-2.0"}
"""
        mit_license = """MIT License"""

        # Create a side effect function that properly handles the Path instance
        def exists_side_effect(self):
            return "LICENSE" in str(self) or "pyproject.toml" in str(self)

        def is_file_side_effect(self):
            return True

        with patch.object(Path, "exists", exists_side_effect):
            with patch.object(Path, "is_file", is_file_side_effect):
                with patch("builtins.open", mock_open()) as mock_file:
                    # Configure different return values for different files
                    mock_file.return_value.read.side_effect = [
                        mit_license,
                        pyproject_content,
                    ]
                    with patch.object(Path, "iterdir", return_value=[Path("LICENSE")]):
                        with patch(
                            "toml.load",
                            return_value={
                                "project": {"license": {"text": "Apache-2.0"}}
                            },
                        ):
                            ast_tree = ast.parse("")
                            result = self.checker.check(ast_tree, "test.py")

        assert result is not None
        assert "LIC007" in result.metadata

    def test_package_without_license_info(self):
        """Test handling of packages without license information."""
        mock_dist = MagicMock()
        mock_dist.metadata = {"Name": "no-license-package"}

        mit_license = """MIT License"""

        # Create a side effect function that properly handles the Path instance
        def exists_side_effect(self):
            return "LICENSE" in str(self)

        def is_file_side_effect(self):
            return True

        with patch.object(Path, "exists", exists_side_effect):
            with patch.object(Path, "is_file", is_file_side_effect):
                with patch("builtins.open", mock_open(read_data=mit_license)):
                    with patch.object(Path, "iterdir", return_value=[Path("LICENSE")]):
                        with patch(
                            "importlib.metadata.distributions", return_value=[mock_dist]
                        ):
                            ast_tree = ast.parse("")
                            result = self.checker.check(ast_tree, "test.py")

        assert result is not None
        assert "LIC008" in result.metadata
        assert any(
            "no-license-package" in loc.message for loc in result.failure_locations
        )

    def test_apache_license_detection(self):
        """Test Apache 2.0 license detection."""
        apache_license = """
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION
"""

        # Create a side effect function that properly handles the Path instance
        def exists_side_effect(self):
            return "LICENSE" in str(self)

        def is_file_side_effect(self):
            return True

        with patch.object(Path, "exists", exists_side_effect):
            with patch.object(Path, "is_file", is_file_side_effect):
                with patch("builtins.open", mock_open(read_data=apache_license)):
                    with patch.object(Path, "iterdir", return_value=[Path("LICENSE")]):
                        ast_tree = ast.parse("")
                        result = self.checker.check(ast_tree, "test.py")

        # Should recognize Apache license
        if result:
            assert "LIC002" not in result.metadata

    def test_bsd_license_detection(self):
        """Test BSD license detection."""
        bsd_license = """BSD 3-Clause License

Copyright (c) 2025, Test Author

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
"""

        # Create a side effect function that properly handles the Path instance
        def exists_side_effect(self):
            return "LICENSE" in str(self)

        def is_file_side_effect(self):
            return True

        with patch.object(Path, "exists", exists_side_effect):
            with patch.object(Path, "is_file", is_file_side_effect):
                with patch("builtins.open", mock_open(read_data=bsd_license)):
                    with patch.object(Path, "iterdir", return_value=[Path("LICENSE")]):
                        ast_tree = ast.parse("")
                        result = self.checker.check(ast_tree, "test.py")

        # Should recognize BSD license
        if result:
            assert "LIC002" not in result.metadata

    def test_multiple_license_files(self):
        """Test handling of multiple license files."""
        mit_license = """MIT License"""

        # Create a side effect function that properly handles the Path instance
        def exists_side_effect(self):
            return any(
                lic in str(self) for lic in ["LICENSE", "LICENSE.txt", "LICENSE.md"]
            )

        def is_file_side_effect(self):
            return True

        with patch.object(Path, "exists", exists_side_effect):
            with patch.object(Path, "is_file", is_file_side_effect):
                with patch("builtins.open", mock_open(read_data=mit_license)):
                    with patch.object(
                        Path,
                        "iterdir",
                        return_value=[
                            Path("LICENSE"),
                            Path("LICENSE.txt"),
                            Path("LICENSE.md"),
                        ],
                    ):
                        ast_tree = ast.parse("")
                        result = self.checker.check(ast_tree, "test.py")

        # Should handle multiple license files without critical issues
        if result:
            assert (
                result.severity != Severity.CRITICAL
                and result.severity != Severity.HIGH
            )

    def test_pyproject_toml_license_field(self):
        """Test reading license from pyproject.toml license field."""
        pyproject_content = """
[project]
name = "test-package" 
license = "MIT"
"""
        # Reset the checker state
        self.checker._project_checked = False
        self.checker._project_license = None

        # Create a side effect function that properly handles the Path instance
        def exists_side_effect(self):
            return "pyproject.toml" in str(self)

        def is_file_side_effect(self):
            return True

        with patch.object(Path, "exists", exists_side_effect):
            with patch.object(Path, "is_file", is_file_side_effect):
                with patch("builtins.open", mock_open(read_data=pyproject_content)):
                    with patch(
                        "toml.load", return_value={"project": {"license": "MIT"}}
                    ):
                        ast_tree = ast.parse("")
                        result = self.checker.check(ast_tree, "test.py")

        # Should still report missing LICENSE file even if license is in pyproject.toml
        assert result is not None
        assert "LIC001" in result.metadata
        # But should have detected the license type from pyproject.toml for compatibility checks
        # (The checker uses pyproject license info even if LICENSE file is missing)
