"""
Unit tests for CLI functionality.
"""

import subprocess
import sys


def test_main_cli_help():
    """Test that main CLI shows help."""
    result = subprocess.run(
        [sys.executable, "-m", "src_check.cli.main", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "src-check - Python code quality analysis" in result.stdout


def test_kpi_cli_help():
    """Test that KPI CLI shows help."""
    result = subprocess.run(
        [sys.executable, "-m", "src_check.cli.kpi", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "src-check KPI - Focused code quality scoring" in result.stdout


def test_main_cli_basic_execution():
    """Test basic execution of main CLI."""
    # Test with current directory
    result = subprocess.run(
        [sys.executable, "-m", "src_check.cli.main", "."],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Starting code quality analysis" in result.stdout


def test_kpi_cli_basic_execution():
    """Test basic execution of KPI CLI."""
    result = subprocess.run(
        [sys.executable, "-m", "src_check.cli.kpi", "."], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "KPI Analysis Mode" in result.stdout
