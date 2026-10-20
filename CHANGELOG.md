# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- This commit makes the smoke workflow install the `dev` extra (the `test` extra no longer exists, so CI had no pytest) and adds `tests/test_workflow_extras.py`, which fails when a workflow installs an extra that pyproject.toml does not define.

### Added

- This commit adds tests/test_generate_fallbacks.py covering the card generator helpers and the fallback readers, raising test coverage from 77 to 81 percent.
- This commit rewrites tests/test_repo_hygiene.py without the yaml import so all five hygiene checks run on a plain dev install.
- This commit adds tests/test_repo_hygiene.py, which checks the code owner file, the agent instructions file, the README badge and footer, and the workflow timeouts from the files on disk.
- This commit switches the README CI badge to the shields.io workflow status URL and adds a 15 minute timeout to both workflow jobs.
- This commit adds .github/copilot-instructions.md describing the repo layout, the pytest and ruff commands, and the truth rule for numbers in docs.
- This commit adds .github/CODEOWNERS, which assigns @mrodgersjs-web as the code owner for every file in the repo.

## [0.2.0] - 2026-10-19

### Changed

- Documentation rewritten in plain English with runnable worked examples and real output.
- Removed superlative claims from code, docs, and CLI descriptions.
- Packaging completed: dev extras (pytest, pytest-cov, ruff), ruff configuration, coverage configuration.

### Added

- CI workflow that runs lint and the test suite with coverage on push and pull request.
- Community files: security policy, code of conduct, contributing guide, issue and pull request templates.
- `docs/architecture.md` design notes and a runnable example under `examples/`.
