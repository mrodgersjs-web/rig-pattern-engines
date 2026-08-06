# Contributing to RIG Pattern Engines

Thanks for helping make the engines sharper. This repo is intentionally small and deterministic: no LLM calls, no external secrets, no cloud dependencies.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
```

## Project layout

```
rig_pattern_engines/
  __init__.py              # public API
  omniscout_build_cards.py # card loading + shared primitives
  pattern_anticrowd.py     # Anti-Crowd Score engine
  pattern_contradiction.py # Contradiction Arbitrage Rank engine
  pattern_drift.py         # Epistemic Drift engine
  pattern_dashboard.py     # HTML dashboard generator
  pattern_generate.py      # opportunity-to-card generator
tests/
  fixtures/                # 5 scrubbed sample cards
  test_engines.py          # smoke tests for all three engines
```

## Adding a new pattern dimension

1. Open the engine file (e.g. `pattern_anticrowd.py`).
2. Add a private helper that takes the relevant card slice and returns a dict.
3. Wire the result into the main compute function (`compute_acs`, `compute_car`, or `score_all_strategies`).
4. Add a smoke-test assertion in `tests/test_engines.py`.
5. Update `README.md` with the new field and its meaning.

Keep all scoring deterministic (no `random`, no network calls, no LLM). Prefer counts, graph metrics, and ratios over heuristics that need human judgment.

## Running tests

```bash
pytest tests/
```

The tests should stay fast enough to run on every edit (a few seconds on the sample fixtures).

## Pull-request checklist

- [ ] No internal paths, emails, tokens, or hostnames are introduced.
- [ ] All imports stay inside the `rig_pattern_engines` package.
- [ ] `python -m rig_pattern_engines.pattern_anticrowd all --cards-dir tests/fixtures` runs.
- [ ] `python -m rig_pattern_engines.pattern_contradiction all --cards-dir tests/fixtures` runs.
- [ ] `python -m rig_pattern_engines.pattern_drift all --cards-dir tests/fixtures` runs.
- [ ] `pytest tests/` passes.

## Code style

- Type hints for public functions.
- `from __future__ import annotations` at the top of each module.
- Keep functions small and testable.
- No emojis in source files.

## Questions?

Open an issue with the engine name and a minimal card snippet that reproduces the behavior.
