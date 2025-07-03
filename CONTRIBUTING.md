# Contributing to src-check

Thank you for your interest in contributing to src-check! This document provides guidelines and instructions for contributing.

## 🤝 Code of Conduct

By participating in this project, you agree to abide by our code of conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Respect differing viewpoints and experiences

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, virtualenv, etc.)

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/sugipamo/src-check.git
cd src-check

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests to verify setup
pytest
```

## 📝 Development Process

### 1. Find or Create an Issue

- Check existing issues for something you'd like to work on
- If you have a new idea, create an issue first to discuss it
- Comment on the issue to let others know you're working on it

### 2. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 3. Make Your Changes

Follow these guidelines:
- Write clean, readable code following PEP 8
- Add type hints to all functions
- Include docstrings for modules, classes, and functions
- Keep commits focused and atomic

### 4. Write Tests

- Add tests for new functionality
- Ensure all tests pass: `pytest`
- Maintain test coverage above 85%: `pytest --cov=src_check`

### 5. Code Quality Checks

Run these before submitting:

```bash
# Format code
black src tests

# Check with ruff
ruff check src tests

# Type checking
mypy src

# Run all tests
pytest -v --cov=src_check
```

### 6. Update Documentation

- Update README.md if adding new features
- Update docstrings
- Add examples if applicable

### 7. Submit Pull Request

- Push your branch: `git push origin feature/your-feature-name`
- Create a pull request on GitHub
- Fill out the PR template completely
- Link related issues

## 🏗️ Architecture Overview

```
src/
├── check/
│   ├── checkers/        # Individual checker implementations
│   ├── base_checker.py  # Base class for all checkers
│   └── engine.py        # Main checking engine
├── cli/                 # Command-line interface
├── config/             # Configuration handling
├── formatters/         # Output formatters
└── models/             # Data models
```

## 📚 Adding a New Checker

1. Create a new file in `src/check/checkers/`
2. Inherit from `BaseChecker`
3. Implement required methods:
   - `check_project()`
   - `check_file()`
   - `get_issue_types()`
4. Add tests in `tests/checkers/`
5. Register in `CHECKER_REGISTRY`

Example:

```python
from src.check.base_checker import BaseChecker

class MyChecker(BaseChecker):
    """Description of what this checker does."""
    
    def get_issue_types(self):
        return {
            "MY001": "Description of this issue type"
        }
    
    def check_file(self, file_path, content, ast_tree, lines):
        issues = []
        # Implement checking logic
        return issues
```

## 🧪 Testing Guidelines

- Use pytest for all tests
- Follow AAA pattern: Arrange, Act, Assert
- Use fixtures for common test data
- Mock external dependencies
- Test edge cases and error conditions

## 📦 Release Process

1. Update version in `pyproject.toml` and `src/__init__.py`
2. Update CHANGELOG.md
3. Create release notes
4. Tag the release: `git tag v0.X.Y`
5. Push tags: `git push --tags`

## 💡 Tips for Contributors

- Start small - pick "good first issue" labeled issues
- Ask questions in issue comments or discussions
- Review other PRs to learn the codebase
- Run `src-check` on your own code!

## 🙏 Recognition

Contributors will be recognized in:
- The project README
- Release notes
- GitHub contributors page

Thank you for helping make src-check better!