"""Smoke tests for the three RIG pattern engines.

Each engine must load sample cards, produce numeric scores, and generate a
human-readable brief without any LLM calls.
"""

from __future__ import annotations

import importlib
import json
import os
import shutil
from pathlib import Path
from typing import Any

import pytest

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def _topic_strategy_from_cards(cards: list[dict[str, Any]]) -> dict[str, Any]:
    strategies: dict[str, dict[str, Any]] = {}
    for card in cards:
        strategy = card.get("strategy") or {}
        sid = strategy.get("strategy_id")
        if not sid:
            continue
        if sid not in strategies:
            strategies[sid] = {
                "strategy_id": sid,
                "label": strategy.get("label") or sid,
                "tier": strategy.get("tier", "T3"),
                "adjacent": [],
            }
    return {"version": "test", "strategies": strategies}


@pytest.fixture
def control_dir(tmp_path: Path) -> Path:
    """Build a temporary OmniScout control tree with fixtures + topic strategy."""
    cards_dir = tmp_path / "build-cards" / "cards"
    cards_dir.mkdir(parents=True)
    for fixture in sorted(FIXTURES_DIR.glob("l2-*.json")):
        shutil.copy(fixture, cards_dir / fixture.name)

    cards = [json.loads(p.read_text()) for p in sorted(cards_dir.glob("l2-*.json"))]
    topic_path = tmp_path / "build-cards" / "TOPIC_STRATEGY.json"
    topic_path.write_text(json.dumps(_topic_strategy_from_cards(cards), indent=2))

    old = os.environ.get("OMNISCOUT_CONTROL")
    os.environ["OMNISCOUT_CONTROL"] = str(tmp_path)
    # Reload modules that compute L2_* at import time.
    from rig_pattern_engines import omniscout_build_cards as obc
    from rig_pattern_engines import pattern_anticrowd

    importlib.reload(obc)
    importlib.reload(pattern_anticrowd)

    yield tmp_path

    if old is None:
        os.environ.pop("OMNISCOUT_CONTROL", None)
    else:
        os.environ["OMNISCOUT_CONTROL"] = old


def _all_fixture_cards() -> list[dict[str, Any]]:
    return [json.loads(p.read_text()) for p in sorted(FIXTURES_DIR.glob("l2-*.json"))]


# ---------------------------------------------------------------------------
# Anti-Crowd
# ---------------------------------------------------------------------------


def test_anticrowd_imports() -> None:
    from rig_pattern_engines import anticrowd_score, anticrowd_brief, anticrowd_compute

    assert callable(anticrowd_score)
    assert callable(anticrowd_brief)
    assert callable(anticrowd_compute)


def test_anticrowd_scores_strategies(control_dir: Path) -> None:
    from rig_pattern_engines.pattern_anticrowd import score_all_strategies

    result = score_all_strategies(cards_dir=control_dir / "build-cards" / "cards")
    assert result["schema"].startswith("rig.omniscout.pattern-anticrowd")
    assert result["total_strategies_scored"] > 0
    strategies = result["strategies"]
    assert strategies

    top = strategies[0]
    assert "acs" in top
    assert "risk_adjusted_opportunity_score" in top
    assert "market_size" in top
    assert "regulatory_barrier" in top
    assert "regulatory_taxonomy" in top
    assert "competitor_density" in top
    assert "competitor_hhi" in top
    assert "rig_advantage" in top
    assert "rig_coverage_ratio" in top
    assert "recommendation" in top
    assert top["recommendation"] in ("DOMINATE", "ENTER", "WATCH", "IGNORE")


def test_anticrowd_brief(control_dir: Path) -> None:
    from rig_pattern_engines.pattern_anticrowd import score_all_strategies, generate_brief

    summary = score_all_strategies(cards_dir=control_dir / "build-cards" / "cards")
    brief = generate_brief(summary)
    assert "top_opportunities" in brief
    assert "synergies" in brief


# ---------------------------------------------------------------------------
# Contradiction
# ---------------------------------------------------------------------------


def test_contradiction_imports() -> None:
    from rig_pattern_engines import (
        contradiction_compute,
        contradiction_score,
        contradiction_brief,
    )

    assert callable(contradiction_compute)
    assert callable(contradiction_score)
    assert callable(contradiction_brief)


def test_contradiction_graph_and_scores() -> None:
    from rig_pattern_engines.pattern_contradiction import (
        load_cards,
        compute_car,
        score_all_contradictions,
    )

    cards = load_cards(FIXTURES_DIR)
    assert cards

    car_result = compute_car(cards)
    assert car_result["schema"].startswith("rig.foundry.pattern-contradiction")
    # The entity graph is always reported, even when no contradictions exist.
    assert "entity_graph" in car_result
    assert "pagerank" in car_result["entity_graph"]

    entries = score_all_contradictions(cards)
    assert entries["schema"].startswith("rig.foundry.pattern-contradiction")
    assert "contradictions" in entries

    # If contradictions exist, verify score dimensions.
    if entries["contradictions"]:
        first = entries["contradictions"][0]
        assert "car" in first
        assert "components" in first
        assert "breakthrough" in first
        assert "confidence" in first["breakthrough"]
        assert "confidence_interval" in first["breakthrough"]
        assert "lower" in first["breakthrough"]["confidence_interval"]
        assert "time_to_resolution_weeks" in first["breakthrough"]


def test_contradiction_brief() -> None:
    from rig_pattern_engines.pattern_contradiction import (
        load_cards,
        compute_car,
        score_all_contradictions,
        generate_brief,
    )

    cards = load_cards(FIXTURES_DIR)
    car_result = compute_car(cards)
    entries = score_all_contradictions(cards)
    brief = generate_brief(car_result, entries)
    assert brief["schema"].startswith("rig.foundry.pattern-contradiction")
    assert brief["top"]
    assert brief["summary"]["total_pairs"] == car_result["metadata"]["count"]
    assert "date" in brief


# ---------------------------------------------------------------------------
# Epistemic Drift
# ---------------------------------------------------------------------------


def test_drift_imports() -> None:
    from rig_pattern_engines import drift_compute, drift_score, drift_brief

    assert callable(drift_compute)
    assert callable(drift_score)
    assert callable(drift_brief)


def test_drift_report() -> None:
    from rig_pattern_engines.pattern_drift import compute_drift

    report = compute_drift(cards_dir=FIXTURES_DIR)
    assert report["schema"].startswith("rig.omniscout.pattern-drift")
    assert "strategies" in report
    assert report["strategies"]
    assert "concept_velocity_timeseries" in report

    scores = report["strategies"]
    first = scores[0]
    assert "frontier_ratio" in first
    assert "cross_domain_ratio" in first
    assert "bridge_ratio" in first
    assert "composite_drift_score" in first
    assert "leading_indicator" in first


def test_drift_brief() -> None:
    from rig_pattern_engines.pattern_drift import compute_drift, generate_brief

    report = compute_drift(cards_dir=FIXTURES_DIR)
    brief = generate_brief(report, top_n=3)
    assert "brief_strategies" in brief
    assert "bridge_concepts_highlight" in brief


def test_drift_vocabulary_and_migration() -> None:
    from rig_pattern_engines.pattern_drift import compute_drift, load_cards

    cards = load_cards(FIXTURES_DIR)
    report = compute_drift(cards=cards)
    vocab = report["vocabulary_summary"]
    assert "unique_token_count" in vocab
    assert "top_tokens" in vocab
    assert isinstance(report["cross_domain_migration_candidates"], list)


# ---------------------------------------------------------------------------
# Package-level helpers
# ---------------------------------------------------------------------------


def test_load_build_card_helpers() -> None:
    from rig_pattern_engines import score_build_card, stable_json, sha256_text

    assert callable(score_build_card)
    assert callable(stable_json)
    assert callable(sha256_text)
