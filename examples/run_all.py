"""Run all three engines over the sample cards and print one worked example each.

Usage:
    python examples/run_all.py [cards_dir]

Defaults to the fixture cards shipped in tests/fixtures/.
"""

from __future__ import annotations

import sys
from pathlib import Path

from rig_pattern_engines import (
    anticrowd_score,
    contradiction_compute,
    drift_compute,
)


def main() -> int:
    cards_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else (
        Path(__file__).resolve().parent.parent / "tests" / "fixtures"
    )
    if not cards_dir.is_dir():
        print(f"cards directory not found: {cards_dir}")
        return 1

    acs = anticrowd_score(cards_dir=cards_dir)
    rows = acs.get("rows") or acs.get("strategies") or []
    print("Anti-Crowd Score: top zone ->", rows[0] if rows else acs.get("top_strategy"))

    cards = [__import__("json").loads(p.read_text()) for p in sorted(cards_dir.glob("l2-*.json"))]
    car = contradiction_compute(cards)
    meta = car.get("metadata", {})
    print("Contradictions found:", meta.get("count", 0))

    drift = drift_compute(cards_dir=cards_dir)
    print("Leading-indicator strategies:", drift.get("leading_indicator_count", 0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
