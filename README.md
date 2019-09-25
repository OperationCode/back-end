<div align="center">
  <br />
  <a href="https://operationcode.org">
    <img
      alt="Operation Code Hacktoberfest Banner"
      src="https://operation-code-assets.s3.us-east-2.amazonaws.com/operation_code_hacktoberfest_2019.jpg"
    >
  </a>
  <br />
  <br />
</div>

# 🎃 Hacktoberfest 🎃

[All the details you need](https://github.com/OperationCode/START_HERE/blob/master/README.md#-hacktoberfest-) before participating with us.

<br />

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Twitter Follow](https://img.shields.io/twitter/follow/operation_code.svg?style=social&label=Follow&style=social)](https://twitter.com/operation_code)
[![Code-style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)


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
- `python@3.7` or greater (in some environments, you may need to specify version of python i.e. `python test.py` vs `python3 test.py`))
- `git@2.17.1` or greater
- `poetry@0.12.11` or greater
    - [Poetry](https://poetry.eustace.io/) is a packaging and dependency manager, similar to pip or pipenv
    - Poetry provides a custom installer that can be ran via `curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python`
    - Alternatively, poetry can be installed via pip/pip3 with `pip install --user poetry` or `pip3 install --user poetry`
    - See https://poetry.eustace.io/docs/


```bash
# Install dependencies (ensure poetry is already installed)
# if you are encountering an error with psycopg2 during poetry installation, ensure postgreqsql is installed (macOS: brew install postgresql)
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
poetry run pytest

# Run formatting and linting
poetry run black .
# the next line shouldn't output anything to the terminal if it passes
poetry run flake8
poetry run isort -rc .
```

## Running [Bandit](https://github.com/PyCQA/bandit)
Bandit is a tool designed to find common security issues in Python code. 

From within the `back-end/` directory you can run the following Bandit command: 

- `bandit -r .` runs all bandit tests recursively with only filters defined in the `.bandit` file.
