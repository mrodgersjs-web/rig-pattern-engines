"""Tests for the dashboard and card-generator modules."""

from __future__ import annotations

import importlib
import json
import os
import shutil
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def control_tree(tmp_path: Path):
    """A full control tree: cards, topic strategy, and engine reports."""
    cards_dir = tmp_path / "cards"
    cards_dir.mkdir()
    for fixture in sorted(FIXTURES_DIR.glob("l2-*.json")):
        shutil.copy(fixture, cards_dir / fixture.name)

    cards = [json.loads(p.read_text()) for p in sorted(cards_dir.glob("l2-*.json"))]
    strategies: dict[str, dict] = {}
    for card in cards:
        strategy = card.get("strategy") or {}
        sid = strategy.get("strategy_id")
        if sid and sid not in strategies:
            strategies[sid] = {
                "strategy_id": sid,
                "label": strategy.get("label") or sid,
                "tier": strategy.get("tier", "T3"),
                "adjacent": [],
            }
    (tmp_path / "TOPIC_STRATEGY.json").write_text(
        json.dumps({"version": "test", "strategies": strategies}, indent=2)
    )

    old = os.environ.get("OMNISCOUT_CONTROL")
    os.environ["OMNISCOUT_CONTROL"] = str(tmp_path)
    modules = [
        "rig_pattern_engines.omniscout_build_cards",
        "rig_pattern_engines.pattern_anticrowd",
        "rig_pattern_engines.pattern_contradiction",
        "rig_pattern_engines.pattern_drift",
        "rig_pattern_engines.pattern_dashboard",
        "rig_pattern_engines.pattern_generate",
    ]
    for name in modules:
        importlib.reload(importlib.import_module(name))

    yield tmp_path

    if old is None:
        os.environ.pop("OMNISCOUT_CONTROL", None)
    else:
        os.environ["OMNISCOUT_CONTROL"] = old


def test_generate_dashboard_writes_html(control_tree: Path) -> None:
    from rig_pattern_engines.pattern_dashboard import generate_dashboard

    out = control_tree / "out" / "dash.html"
    digest = generate_dashboard(l2_root=control_tree, output_path=out)
    assert out.exists()
    assert digest["cards_count"] >= 5
    assert out.read_text().lstrip().startswith("<")


def test_dashboard_cli_runs(control_tree: Path) -> None:
    from rig_pattern_engines.pattern_dashboard import main

    out = control_tree / "out" / "cli.html"
    rc = main(["generate", "--l2-root", str(control_tree), "--output", str(out), "--no-open"])
    assert rc == 0
    assert out.exists()


def test_generate_pattern_cards_runs(control_tree: Path) -> None:
    from rig_pattern_engines.pattern_generate import generate_pattern_cards

    result = generate_pattern_cards(l2_root=control_tree)
    assert result["generated"] >= 0
    assert "by_engine" in result
    assert len(result["written_paths"]) == result["generated"]


def test_generate_cli_status(control_tree: Path) -> None:
    from rig_pattern_engines.pattern_generate import main

    assert main(["status"]) == 0


def test_generate_cli_all(control_tree: Path) -> None:
    from rig_pattern_engines.pattern_generate import main

    rc = main(["all"])
    assert rc in (0, 1)


def test_dashboard_helpers() -> None:
    from rig_pattern_engines.pattern_dashboard import (
        _build_status,
        _card_display_id,
        _safe_float,
        _safe_int,
    )

    assert _safe_int("7") == 7
    assert _safe_int(None) == 0
    assert _safe_float("1.5") == 1.5
    assert _safe_float(None, 2.0) == 2.0
    assert _build_status({}) in {"pending", "unknown", "built", "sealed", "planned"}
    assert isinstance(_card_display_id({"card_id": "l2-abc"}), str)


def test_generate_helpers() -> None:
    from rig_pattern_engines.pattern_generate import _median_str, _rank, _strategy_question

    assert _rank(0) == _rank(0)
    assert isinstance(_median_str(["a", "b"]), str)
    assert isinstance(_strategy_question("agent-identity"), str)
    assert isinstance(_strategy_question("no-such-strategy"), str)


def test_contradiction_graph_and_brief(control_tree: Path) -> None:
    import json as _json

    from rig_pattern_engines import build_contradiction_graph
    from rig_pattern_engines.pattern_contradiction import generate_brief

    cards = [_json.loads(p.read_text()) for p in sorted((control_tree / "cards").glob("l2-*.json"))]
    graph = build_contradiction_graph(cards)
    assert isinstance(graph, dict)
    brief = generate_brief()
    assert isinstance(brief, dict)


def test_drift_helpers(control_tree: Path) -> None:
    import json as _json

    from rig_pattern_engines import build_cooccurrence_matrix, build_ego_vectors

    cards = [_json.loads(p.read_text()) for p in sorted((control_tree / "cards").glob("l2-*.json"))]
    matrix = build_cooccurrence_matrix(cards)
    assert isinstance(matrix, dict)
    vectors = build_ego_vectors(cards, matrix)
    assert isinstance(vectors, dict)


def test_generate_card_from_opportunity(control_tree: Path) -> None:
    from rig_pattern_engines.pattern_generate import generate_card_from_opportunity

    opp = {
        "engine": "anticrowd",
        "rank": 1,
        "strategy_id": "agent-identity",
        "score": 80,
        "score_label": "80",
        "title": "Test opportunity",
        "claim": "Test claim for the generated card.",
    }
    card = generate_card_from_opportunity(opp, [])
    assert card["card_id"] == "pattern-anticrowd-1"
    assert "score" in card
