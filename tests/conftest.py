"""
pytest configuration and shared fixtures.
"""

import sys
from pathlib import Path
from typing import Callable

import pytest

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def temp_python_file(tmp_path: Path) -> Callable[[str, str], Path]:
    """Create a temporary Python file for testing."""

    def _create_file(content: str, name: str = "test_file.py") -> Path:
        file_path = tmp_path / name
        file_path.write_text(content)
        return file_path

    return _create_file


@pytest.fixture
def sample_ast_tree():
    """Provide a sample AST tree for testing."""
    import ast

    code = '''
def hello_world():
    """Sample function."""
    print("Hello, World!")
    return 42

class SampleClass:
    def __init__(self):
        self.value = 10
'''
    return ast.parse(code)


@pytest.fixture
def mock_config(tmp_path):
    """Create a mock configuration file."""
    config_content = """
base_score: 50.0
weights:
  code_quality: 0.25
  architecture_quality: 0.25
  test_quality: 0.25
  security_quality: 0.25
severity_impacts:
  critical: -10.0
  high: -5.0
  medium: -3.0
  low: -1.0
  info: -0.5
"""
    config_file = tmp_path / ".src-check.yaml"
    config_file.write_text(config_content)
    return config_file


@pytest.fixture
def project_structure(tmp_path):
    """Create a sample project structure for testing."""
    # Create directories
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "docs").mkdir()

    # Create Python files
    (tmp_path / "src" / "__init__.py").write_text("")
    (tmp_path / "src" / "main.py").write_text(
        '''
def main():
    """Main entry point."""
    print("Hello from main")

if __name__ == "__main__":
    main()
'''
    )

    (tmp_path / "src" / "utils.py").write_text(
        '''
import os

def get_path():
    """Get current path."""
    return os.getcwd()
'''
    )

    # Create test file
    (tmp_path / "tests" / "test_main.py").write_text(
        '''
def test_main():
    """Test main function."""
    assert True
'''
    )

    return tmp_path
