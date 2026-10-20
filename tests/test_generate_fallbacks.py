"""Tests for the card generator's helpers and its no-report fallback paths.

The fallback readers matter because they are what runs when a pattern engine
has not produced a report yet; every one of them must still return ranked rows
from the card corpus alone.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from rig_pattern_engines import pattern_generate as pg


def _card(card_id: str, sid: str = "gtm-sales", **extra) -> dict:
    card = {
        "card_id": card_id,
        "title": f"Card {card_id}",
        "strategy": {"strategy_id": sid},
        "temporal_validity": {"age_years": 0.5},
        "entities": {"entity_count": 6},
        "business_intelligence": {},
        "semantic_links": {"contradictions": []},
    }
    card.update(extra)
    return card


class TestHelpers:
    def test_load_json_missing_and_invalid(self, tmp_path: Path) -> None:
        assert pg._load_json(tmp_path / "nope.json") is None
        bad = tmp_path / "bad.json"
        bad.write_text("{not json")
        assert pg._load_json(bad) is None
        good = tmp_path / "good.json"
        good.write_text(json.dumps({"a": 1}))
        assert pg._load_json(good) == {"a": 1}

    @pytest.mark.parametrize(
        ("total", "expected"),
        [(100, "EXCELLENT"), (94, "EXCELLENT"), (85, "STRONG"), (70, "GOOD"), (55, "WEAK"), (0, "REJECT")],
    )
    def test_rank_bands(self, total: int, expected: str) -> None:
        assert pg._rank(total) == expected

    def test_median_str_prefers_real_values(self) -> None:
        assert pg._median_str([]) == "TBD"
        assert pg._median_str(["N/A", "TBD", ""]) == "N/A"
        assert pg._median_str(["$1K", "$3K", "$2K"]) == "$2K"

    def test_strategy_question_known_and_unknown(self) -> None:
        assert "run" in pg._strategy_question("automation-runtime").lower()
        assert "shippable" in pg._strategy_question("made-up-strategy").lower()

    def test_doctrine_domains_fallback(self) -> None:
        assert pg._doctrine_domains_for("zzz-no-match") == ["engineering-capability"]
        domain, markers = next(iter(pg.DOCTRINE_DOMAINS.items()))
        assert domain in pg._doctrine_domains_for(markers[0])

    def test_load_corpus_skips_bad_files(self, tmp_path: Path, monkeypatch) -> None:
        (tmp_path / "l2-1.json").write_text(json.dumps(_card("l2-1")))
        (tmp_path / "l2-bad.json").write_text("{oops")
        (tmp_path / "unrelated.json").write_text(json.dumps(_card("x")))
        monkeypatch.setattr(pg, "L2_CARDS", tmp_path)
        corpus = pg._load_corpus()
        assert [c["card_id"] for c in corpus] == ["l2-1"]

    def test_load_corpus_without_directory(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.setattr(pg, "L2_CARDS", tmp_path / "missing")
        assert pg._load_corpus() == []

    def test_cards_for_strategy_filters(self) -> None:
        cards = [_card("a", "gtm-sales"), _card("b", "cybersecurity")]
        assert [c["card_id"] for c in pg._cards_for_strategy(cards, "gtm-sales")] == ["a"]


class TestAdjacentBusinessIntelligence:
    def test_picks_medians_and_dedupes_lists(self) -> None:
        cards = [
            _card(
                "a",
                "gtm-sales",
                business_intelligence={
                    "revenue_model": "Retainer",
                    "price_range": "$2K",
                    "estimated_cac": "$1K",
                    "estimated_ltv": "$50K",
                    "revenue_ideas": ["Retainer product", "Audit product"],
                },
            ),
            _card(
                "b",
                "gtm-sales",
                business_intelligence={
                    "revenue_model": "Project",
                    "price_range": "$8K",
                    "revenue_ideas": ["Audit product", "Retainer product"],
                },
            ),
        ]
        out = pg._derive_adjacent_business_intelligence(cards, "gtm-sales")
        assert out["revenue_model"] in {"Retainer", "Project"}
        assert out["price_range"] in {"$2K", "$8K"}
        assert out["revenue_ideas"] == ["Retainer product", "Audit product"]

    def test_falls_back_to_defaults_without_cards(self) -> None:
        out = pg._derive_adjacent_business_intelligence([], "gtm-sales")
        assert out["revenue_model"] == "Consulting + custom build"
        assert out["price_range"] == "$5K-20K/mo"


class TestFallbackReaders:
    def test_anticrowd_fallback_ranks_empty_strategies(self) -> None:
        rows = pg._read_anticrowd(Path("/nonexistent/pattern-anticrowd.json"), [_card("a")])
        assert rows, "fallback must return rows from empty strategies"
        assert all(r["details"].get("fallback") for r in rows)
        assert [r["rank"] for r in rows] == [1, 2, 3]

    def test_anticrowd_primary_reads_report(self, tmp_path: Path) -> None:
        report = tmp_path / "pattern-anticrowd.json"
        report.write_text(
            json.dumps(
                {"strategies": [{"strategy_id": "gtm-sales", "acs": 81.5, "action": "BUILD"}]}
            )
        )
        rows = pg._read_anticrowd(report, [])
        assert rows[0]["strategy_id"] == "gtm-sales"
        assert rows[0]["score"] == 81.5
        assert "fallback" not in rows[0]["details"]

    def test_contradiction_fallback_uses_semantic_links(self) -> None:
        a = _card("a", "gtm-sales")
        b = _card("b", "gtm-sales")
        a["semantic_links"] = {
            "contradictions": [{"card_id": "b", "similarity": 0.8, "reason": "claims disagree"}]
        }
        rows = pg._read_contradiction(Path("/nonexistent/pattern-contradiction.json"), [a, b])
        assert len(rows) == 1
        assert rows[0]["strategy_id"] == "gtm-sales"
        assert rows[0]["details"]["fallback"] is True
        assert rows[0]["score"] == pytest.approx(min(95.0, 0.8 * 100.0 + 30))

    def test_contradiction_fallback_skips_unknown_pairs(self) -> None:
        a = _card("a", "unknown")
        b = _card("b", "unknown")
        a["semantic_links"] = {"contradictions": [{"card_id": "b", "similarity": 0.9}]}
        rows = pg._read_contradiction(Path("/nonexistent/pattern-contradiction.json"), [a, b])
        assert rows == []

    def test_contradiction_primary_skips_unknown_only_pairs(self, tmp_path: Path) -> None:
        report = tmp_path / "pattern-contradiction.json"
        report.write_text(
            json.dumps(
                {
                    "pairs": [
                        {"strategy_ids": ["unknown"], "car": 0.5, "card_a": "x", "card_b": "y"},
                        {
                            "strategy_ids": ["gtm-sales"],
                            "car": 0.72,
                            "card_a": "a",
                            "card_b": "b",
                            "state": "resolving",
                        },
                    ]
                }
            )
        )
        rows = pg._read_contradiction(report, [])
        assert len(rows) == 1
        assert rows[0]["score"] == pytest.approx(72.0)

    def test_drift_fallback_scores_groups(self) -> None:
        cards = [
            _card("a", "gtm-sales"),
            _card("b", "gtm-sales"),
            _card("c", "cybersecurity"),
            _card("d", "cybersecurity"),
        ]
        rows = pg._read_drift(Path("/nonexistent/pattern-drift.json"), cards)
        assert {r["strategy_id"] for r in rows} == {"gtm-sales", "cybersecurity"}
        assert all(r["details"].get("fallback") for r in rows)

    def test_drift_fallback_ignores_single_card_strategies(self) -> None:
        rows = pg._read_drift(Path("/nonexistent/pattern-drift.json"), [_card("a", "gtm-sales")])
        assert rows == []

    def test_drift_primary_normalizes_fractional_scores(self, tmp_path: Path) -> None:
        report = tmp_path / "pattern-drift.json"
        report.write_text(
            json.dumps(
                {
                    "strategies": [
                        {"strategy_id": "gtm-sales", "drift_score": 0.42, "frontier_entities": 7},
                        {"strategy_id": "unknown", "drift_score": 0.9, "frontier_entities": 1},
                    ]
                }
            )
        )
        rows = pg._read_drift(report, [])
        assert len(rows) == 1
        assert rows[0]["score"] == pytest.approx(42.0)
        assert "fallback" not in rows[0]["details"]
