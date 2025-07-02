.PHONY: test test-unit test-integration test-all coverage lint format type-check clean

# Test commands
test:
	python -m pytest tests/ -v

test-unit:
	python -m pytest tests/ -v -m unit

test-integration:
	python -m pytest tests/ -v -m integration

test-all:
	python -m pytest tests/ -v --tb=short

coverage:
	python -m pytest tests/ --cov=src_check --cov-report=html --cov-report=term-missing

coverage-html:
	python -m pytest tests/ --cov=src_check --cov-report=html
	open htmlcov/index.html || xdg-open htmlcov/index.html

# Code quality
lint:
	python -m ruff check src/ tests/

format:
	python -m black src/ tests/

format-check:
	python -m black --check src/ tests/

type-check:
	python -m mypy src/

# Clean up
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf .mypy_cache
	rm -rf .ruff_cache

# Development workflow
check: format-check lint type-check test

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"