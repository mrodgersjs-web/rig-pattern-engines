# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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
