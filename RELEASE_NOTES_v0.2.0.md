# src-check v0.2.0 Release Notes

## 🎉 Overview

We are excited to announce the release of src-check v0.2.0 - a comprehensive Python code quality management tool that makes it easy to maintain high-quality Python projects. This release marks a significant milestone with full functionality and 10 different quality checkers.

## ✨ Key Features

### 10 Comprehensive Checkers

1. **SecurityChecker** - Detects security vulnerabilities and potential risks
   - Hardcoded credentials detection
   - SQL injection risks
   - Insecure random number usage
   - Command injection vulnerabilities

2. **CodeQualityChecker** - Ensures clean and maintainable code
   - Cyclomatic complexity analysis
   - Function length checks
   - Duplicate code detection
   - Dead code identification

3. **ArchitectureChecker** - Validates architectural patterns
   - Circular dependency detection
   - Layer violation checks
   - Module cohesion analysis

4. **TestQualityChecker** - Evaluates test suite quality
   - Test coverage analysis
   - Test naming conventions
   - Assert statement quality
   - Test isolation checks

5. **DocumentationChecker** - Ensures comprehensive documentation
   - Docstring presence and quality
   - Parameter documentation
   - Return value documentation
   - Module-level documentation

6. **TypeHintChecker** - Validates type annotations
   - Function signature type hints
   - Variable annotations
   - Generic type usage
   - Type consistency

7. **PerformanceChecker** - Identifies performance issues
   - Inefficient loops
   - Memory leaks
   - Unnecessary list comprehensions
   - Suboptimal data structures

8. **DependencyChecker** - Manages dependencies
   - Unused imports detection
   - Circular dependencies
   - Version compatibility
   - License compliance

9. **LicenseChecker** - Ensures license compliance
   - License header validation
   - Third-party license compatibility
   - License file presence

10. **DeprecationChecker** - Tracks deprecated code
    - Deprecated function usage
    - Obsolete patterns
    - Migration guidance

### CLI Integration

Two powerful command-line interfaces:

```bash
# Run comprehensive code quality checks
src-check /path/to/project

# Calculate and display KPI scores
src-check-kpi /path/to/project
```

### Output Formats

Support for multiple output formats:
- **Text** (default) - Human-readable console output
- **JSON** - Machine-readable format for CI/CD integration
- **Markdown** - Perfect for documentation and reports

## 📊 Quality Metrics

- **Test Coverage**: 84.19% (exceeding our 70% target)
- **Total Tests**: 106 (all passing)
- **Type Safety**: 100% (0 mypy errors)
- **Python Compatibility**: 3.8+
- **Code Format**: Black-compliant

## 🚀 Installation

```bash
pip install src-check
```

## 📖 Quick Start

### Basic Usage

```bash
# Check current directory
src-check .

# Check specific directory
src-check /path/to/your/project

# Generate JSON report
src-check /path/to/project --format json > report.json

# Calculate KPI scores
src-check-kpi /path/to/project
```

### Example Output

```
src-check Results
================

SecurityChecker
  ✗ Hardcoded password found (Line 42)
  ✗ SQL injection risk detected (Line 156)
  
CodeQualityChecker
  ✓ All functions within complexity limits
  ✗ Function 'process_data' too long (150 lines)

Overall Score: 75/100
```

## 🔧 Configuration

Create a `.src-check.yaml` file in your project root:

```yaml
# Enable/disable specific checkers
checkers:
  security: true
  code_quality: true
  architecture: true
  test_quality: true
  documentation: true
  type_hints: true
  performance: true
  dependencies: true
  license: true
  deprecation: true

# Exclude patterns
exclude:
  - "tests/*"
  - "build/*"
  - ".venv/*"

# Custom thresholds
thresholds:
  max_complexity: 10
  max_function_length: 50
  min_coverage: 80
```

## 🤝 Integration

### GitHub Actions

```yaml
name: Code Quality Check
on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      - run: pip install src-check
      - run: src-check . --format json
```

### Pre-commit Hook

```yaml
repos:
  - repo: local
    hooks:
      - id: src-check
        name: src-check
        entry: src-check
        language: system
        pass_filenames: false
```

## 📝 Known Limitations

- Large projects (>10,000 files) may experience slower analysis times
- Some advanced Python 3.11+ features may not be fully supported
- Custom checker plugins are planned for v0.3.0

## 🔄 What's Next

### v0.3.0 (Coming in 4 weeks)
- 5 additional checkers (ComplexityChecker, NamingConventionChecker, etc.)
- Basic auto-fix functionality
- Enhanced configuration options
- Performance optimizations

### v0.4.0 (Coming in 6 weeks)
- Parallel processing for faster analysis
- Caching system for incremental checks
- Large-scale project support

## 🙏 Acknowledgments

Special thanks to all contributors and early testers who helped shape this release.

## 📚 Documentation

Full documentation is available at:
- [Installation Guide](docs/installation.md)
- [User Guide](docs/user-guide.md)
- [API Reference](docs/api-reference.md)
- [Contributing Guide](CONTRIBUTING.md)

## 🐛 Bug Reports

Please report issues at: https://github.com/sugipamo/src-check/issues

---

**src-check v0.2.0** - Making Python code quality management as easy as pytest!