![Operation Code Logo](https://operation-code-assets.s3.us-east-2.amazonaws.com/branding/logos/large-blue-logo.png)


[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Twitter Follow](https://img.shields.io/twitter/follow/operation_code.svg?style=social&label=Follow&style=social)](https://twitter.com/operation_code)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)


[![CircleCI](https://circleci.com/gh/OperationCode/back-end.svg?style=svg)](https://circleci.com/gh/OperationCode/back-end)
[![Maintainability](https://api.codeclimate.com/v1/badges/8d4513bb1b0d14fa9436/maintainability)](https://codeclimate.com/github/OperationCode/back-end/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/8d4513bb1b0d14fa9436/test_coverage)](https://codeclimate.com/github/OperationCode/back-end/test_coverage)
[![Dependabot Status](https://api.dependabot.com/badges/status?host=github&repo=OperationCode/back-end)](https://dependabot.com)


# Welcome!
This is the back-end application for [OperationCode](https://operationcode.org).
We highly recommend [joining our organization](https://operationcode.org/join) to receive an invite to our Slack team. 
From there, you'll want to join the `#oc-python-projects` and `#oc-projects` channels.
You can get help from multiple professional developers, including people who have worked on the application since day 1!

Before contributing, please review our [Contributing Guide](CONTRIBUTING.md)

## Maintainers
For information about the maintainers of the project, check out [MAINTAINERS.md](MAINTAINERS.md).

## Quick Start
Recommended versions of tools used within the repo:
- `python@3.14` or greater
- `git@2.17.1` or greater
- `poetry@2.3.0` or greater
    - [Poetry](https://python-poetry.org/) is a packaging and dependency manager
    - Install via: `curl -sSL https://install.python-poetry.org | python3 -`
    - Or via pip: `pip install --user poetry`
    - See https://python-poetry.org/docs/


```bash
# Install dependencies (ensure poetry is already installed)
# If you are encountering an error with psycopg2 during poetry installation,
# ensure PostgreSQL is installed (macOS: brew install postgresql)
make install

# Create database
# By default this creates a local sqlite database and adds tables for each of the defined models
# See example.env for database configurations
make migrate

# Create a superuser to add to the new database
make createsuperuser

# Run local development server
make runserver
```

## Development Workflow

### Running Tests
```bash
# Run all tests
make test

# Run only unit tests
make test-unit

# Run only integration tests
make test-integration

# Run tests with coverage report
make test-cov
```

### Linting and Formatting
We use [Ruff](https://github.com/astral-sh/ruff) for both linting and code formatting.

```bash
# Check linting and formatting (doesn't modify files)
make lint

# Auto-fix linting issues and format code
make lint-fix

# Format code only
make format
```

### Security Scanning
[Bandit](https://github.com/PyCQA/bandit) is a tool designed to find common security issues in Python code.

```bash
# Run security scanner
make security
```

### CI Checks
Run all the same checks that CI will run:

```bash
# Run all CI checks (linting, tests with coverage, security)
make ci
```

### Other Commands
```bash
# Open Django shell
make shell

# Clean up Python cache files and test artifacts
make clean

# See all available commands
make help
```

## Background Tasks (Django Q)

This project uses Django Q2 for background task processing. The following tasks are defined but **currently disabled**:

- Welcome email on user registration
- Slack invite via PyBot API
- Mailchimp mailing list sync on email confirmation

**Status:** The `qcluster` worker is intentionally disabled in production (see Dockerfile:150). Tasks will queue in the database but won't be processed.

**To re-enable:**
1. Uncomment the qcluster command in `Dockerfile` CMD line
2. Ensure environment variables are configured: `PYBOT_URL`, `PYBOT_AUTH_TOKEN`, `MAILCHIMP_API_KEY`, `MAILCHIMP_LIST_ID`
3. Run worker locally: `python manage.py qcluster`

Task code is preserved in `src/core/tasks.py` and triggered via signals in `src/core/handlers.py`.
