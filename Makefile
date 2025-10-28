# AI Persona Card Catalog - Development Makefile

.PHONY: help install install-dev test test-cov test-cov-html clean lint format type-check quality-check

help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage report"
	@echo "  test-cov-html - Run tests with HTML coverage report"
	@echo "  lint         - Run linting (flake8)"
	@echo "  format       - Format code (black + isort)"
	@echo "  type-check   - Run type checking (mypy)"
	@echo "  quality-check - Run all quality checks"
	@echo "  clean        - Clean up generated files"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt -r dev-requirements.txt

test:
	pytest -v

test-cov:
	pytest --cov=. --cov-report=term-missing -v

test-cov-html:
	pytest --cov=. --cov-report=html --cov-report=term-missing -v
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	flake8 *.py

format:
	black *.py
	isort *.py

type-check:
	mypy *.py --ignore-missing-imports

quality-check: lint type-check test-cov

clean:
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf *.pyc