# Agent guide

## Maintenance mode
- Avoid major version updates of anything, unless a security fix needs them.
- Keep up with security updates.
- Prefer the smallest change that solves the task.

## Public repo
- Never commit or post secrets, tokens, user data, prod data or counts, internal hostnames that are not already public, or step-by-step attack-useful details.
- Account IDs and ARNs are not secrets, but do not add new sensitive detail.
- PR bodies, comments, and CI logs are public too.

## How to work here
```bash
make install          # setup: poetry install (Python 3.14, Poetry 2.3+)
make test             # pytest
make lint             # ruff check + ruff format --check, as CI does
make ci               # lint + tests with coverage + bandit
```
- PRs build only. Images push only from `main`, or with maintainer approval (`ecr-approval`).
- One PR per change.
- The org PR reviewer blocks dependencies that are less than 72 hours old.
- Deploy, migrations, rollback, secrets, and logs: [OPS.md](OPS.md). CI and AWS security setup: [.github/SETUP.md](.github/SETUP.md).
- Never deploy, run prod commands, or change AWS or GitHub settings without an explicit human OK.
