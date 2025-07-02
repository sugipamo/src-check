# src-check

**Python Code Quality Analysis and KPI Scoring System**

src-check is a comprehensive Python code quality analysis tool that provides quantitative quality assessment through KPI scoring, automated code correction, and detailed reporting.

## Features

- **20+ Quality Checkers**: Security, architecture, code style, and infrastructure analysis
- **KPI Scoring System**: 4-axis evaluation with 0-100 point scoring
- **Auto-Correction**: Smart fixes and import reorganization
- **Modern Toolchain**: High performance with UV package management

## Installation

```bash
# Install from PyPI (future)
pip install src-check

# Development installation
git clone https://github.com/yourusername/src-check
cd src-check
uv sync --dev
```

## Quick Start

```bash
# Analyze current directory
src-check

# Analyze specific paths
src-check src/ tests/

# KPI-only analysis
src-check-kpi --format json
```

## License

MIT License - see LICENSE file for details.