# Copilot instructions for rig-pattern-engines

## What this repo is

Three offline analysis engines that read a folder of research cards (JSON files
named `l2-*.json`) and print ranked strategic signals:

- `pattern_anticrowd.py` scores strategy zones on opportunity versus crowding.
- `pattern_contradiction.py` finds pairs of cards whose claims disagree.
- `pattern_drift.py` measures which vocabulary is new and moving between fields.

`pattern_dashboard.py` combines the engine outputs into one report and
`pattern_generate.py` turns a top opportunity into a build card. There are no
network calls and no LLM calls anywhere in the package, and tests must not add
any.

## Layout

- `rig_pattern_engines/` the package: one module per engine plus dashboard and
  card generator. `py.typed` marks it as typed.
- `tests/` pytest suite plus `tests/fixtures/` sample cards used by tests and
  examples. Fixtures are real card shapes; keep them small and deterministic.
- `examples/run_all.py` runnable walkthrough of all three engines.
- `docs/` architecture notes and worked engine examples.
- `.github/workflows/ci.yml` runs lint and the test suite with coverage.

## Setup and test commands

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
pytest -q --cov
```

Lint before every commit: `ruff check .`. Run the whole suite, not a single
file: `pytest -q`. Smoke path used by CI for a fast sanity check:
`pytest -q tests/test_engines.py`.

## Conventions

- Conventional commit prefixes: feat, fix, test, docs, ci, build, chore.
- Every behavior change lands with a test in the same commit. Tests assert on
  numbers and text the code actually produced; no snapshot-of-nothing tests.
- Determinism is a feature: the same cards must always produce the same scores,
  so no timestamps, randomness, or dict-ordering dependence in scoring paths.
- No secrets, no API keys, no machine paths such as `/Users/...` or `~/...` in
  tracked files. Use `Path` and environment variables for anything location
  specific.
- Public functions stay typed and keep their docstrings in plain English.

## Truth rule

Any number that appears in a README, docstring, or comment must come from a
command you actually ran in this repo (for example `pytest -q`, `wc -l`, or a
run of one of the CLI entry points). If a count changes, update the sentence in
the same commit. Never round up, and never keep a number from an older run.
