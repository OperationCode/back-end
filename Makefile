.PHONY: help install lint lint-fix format test test-unit test-integration test-cov security ci migrate createsuperuser runserver shell clean

# Default target
help:
	@echo "Available commands:"
	@echo "  make install          - Install dependencies with poetry"
	@echo "  make lint             - Run ruff linter and formatter check"
	@echo "  make lint-fix         - Auto-fix linting and formatting issues"
	@echo "  make format           - Format code with ruff"
	@echo "  make test             - Run all tests"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-cov         - Run tests with coverage report"
	@echo "  make security         - Run bandit security scanner"
	@echo "  make ci               - Run all CI checks (lint, test-cov, security)"
	@echo "  make migrate          - Run Django migrations"
	@echo "  make createsuperuser  - Create Django superuser"
	@echo "  make runserver        - Run Django development server"
	@echo "  make shell            - Open Django shell"
	@echo "  make clean            - Remove Python cache files and test artifacts"

# Install dependencies
install:
	poetry install

# Linting and formatting
lint:
	poetry run ruff check .
	poetry run ruff format --check .

lint-fix:
	poetry run ruff check --fix .
	poetry run ruff format .

format:
	poetry run ruff format .

# Testing
test:
	cd src && poetry run pytest

test-unit:
	cd src && poetry run pytest tests/unit/

test-integration:
	cd src && poetry run pytest tests/integration/

test-cov:
	cd src && DJANGO_ENV=testing ENVIRONMENT=TEST SECRET_KEY=test-secret-key poetry run pytest --cov=. --cov-report=xml --cov-report=term-missing -v

# Security
security:
	poetry run bandit -r src --skip B101 --severity-level high -f txt

# CI - runs all checks that CI will run
ci: lint test-cov security
	@echo ""
	@echo "✓ All CI checks passed!"

# Django commands
migrate:
	poetry run python src/manage.py migrate

createsuperuser:
	poetry run python src/manage.py createsuperuser

runserver:
	poetry run python src/manage.py runserver

shell:
	poetry run python src/manage.py shell

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	rm -rf .ruff_cache htmlcov
	@echo "✓ Cleaned up Python cache files and test artifacts"
