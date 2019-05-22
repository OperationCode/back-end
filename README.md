<div align="center">
  <br />
  <a href="https://operationcode.org">
    <img
      alt="Operation Code Hacktoberfest Banner"
      src="https://s3.amazonaws.com/operationcode-assets/branding/logos/large-blue-logo.png"
    >
  </a>
  <br />
  <br />
</div>

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Twitter Follow](https://img.shields.io/twitter/follow/operation_code.svg?style=social&label=Follow&style=social)](https://twitter.com/operation_code)
[![Code-style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)



[![CircleCI](https://circleci.com/gh/OperationCode/back-end.svg?style=svg)](https://circleci.com/gh/OperationCode/back-end)
[![Maintainability](https://api.codeclimate.com/v1/badges/8d4513bb1b0d14fa9436/maintainability)](https://codeclimate.com/github/OperationCode/back-end/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/8d4513bb1b0d14fa9436/test_coverage)](https://codeclimate.com/github/OperationCode/back-end/test_coverage)


# Welcome!

This is a work in progress rewrite of the current [OperationCode](https://operationcode.org) backend. 
We highly recommend [joining our organization](https://operationcode.org/join) to receive an invite to our Slack team. 
From there, you'll want to join the `#oc-python-projects` and `#oc-projects` channels.
You can get help from multiple professional developers, including people who have worked on the application since day 1!
Our website is currently served by code located [here](https://github.com/OperationCode/operationcode_backend), 
but that repository is no longer being actively developed.

This documentation is bad, and yes I feel bad.

## Maintainers
For information about the maintainers of the project, check out [MAINTAINERS.md](MAINTAINERS.md).

## Quick Start

Recommended versions of tools used within the repo:
- `python@3.7` or greater
- `git@2.17.1` or greater
- `poetry@0.12.11` or greater
    - [Poetry](https://poetry.eustace.io/) is a packaging and dependency manager, similar to pip or pipenv
    - Poetry provides a custom installer that can be ran via `curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python`
    - Alternatively, poetry can be installed via pip with `pip install --user poetry`
    - See https://poetry.eustace.io/docs/


```bash
# Install dependencies (ensure poetry is already installed)
poetry install

# Create database
# By default this creates a local sqlite database and adds tables for each of the defined models
# see example.env for database configurations
poetry run python src/manage.py migrate

# Create a superuser to add to the new database
poetry run python src/manage.py createsuperuser 

# Run local development
poetry run python src/manage.py runserver

# Run testing suite
poetry run test

# Run formatting and linting
poetry run black .
poetry run flake8
poetry run isort -rc .
```

## Running [Bandit](https://github.com/PyCQA/bandit)
Bandit is a tool designed to find common security issues in Python code. 

From within the `back-end/` directory you can run the following Bandit commands: 

- `bandit -r -b 20190522-banditBaseline.json .` runs the all Bandit tests recursively and compares to a pre-established baseline (see below for more detail)
- `bandit -r .` runs all bandit tests recursively without a filter (may result in false positives on the `src/test/` folder)

The `20190522-banditBaseline.json` file includes output from an initial Bandit run (dated appropriately) and lists several false positives. Running against the baseline will filter out these results.