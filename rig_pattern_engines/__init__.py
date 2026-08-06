"""RIG Pattern Engines — public API.

Three deterministic pattern-recognition engines for V30 build-cards:

* Anti-Crowd Score (ACS)      — "Where is everyone wrong together?"
* Contradiction Arbitrage Rank (CAR) — "What are two experts saying that cancels out?"
* Epistemic Drift             — "What word no longer means what it meant?"

Each engine is pure Python, has no LLM dependency, and produces JSON reports
and human-readable briefs from a directory of `l2-*.json` build cards.
"""

from __future__ import annotations

from .omniscout_build_cards import (
    L2_CARDS,
    L2_ROOT,
    atomic_json,
    load_topic_strategy,
    score_build_card,
    sha256_text,
    stable_json,
    utc_now,
)
from .pattern_anticrowd import (
    compute_acs as anticrowd_compute,
    detect_synergies as anticrowd_synergies,
    generate_brief as anticrowd_brief,
    score_all_strategies as anticrowd_score,
)
from .pattern_contradiction import (
    build_contradiction_graph,
    compute_car as contradiction_compute,
    generate_brief as contradiction_brief,
    score_all_contradictions as contradiction_score,
)
from .pattern_dashboard import generate_dashboard
from .pattern_drift import (
    build_cooccurrence_matrix,
    build_ego_vectors,
    compute_drift as drift_compute,
    generate_brief as drift_brief,
    score_all_strategies as drift_score,
)
from .pattern_generate import generate_pattern_cards

__version__ = "0.1.0"

__all__ = [
    # package meta
    "__version__",
    # build-card primitives
    "L2_CARDS",
    "L2_ROOT",
    "atomic_json",
    "load_topic_strategy",
    "score_build_card",
    "sha256_text",
    "stable_json",
    "utc_now",
    # Anti-Crowd
    "anticrowd_compute",
    "anticrowd_score",
    "anticrowd_brief",
    "anticrowd_synergies",
    # Contradiction
    "contradiction_compute",
    "contradiction_score",
    "contradiction_brief",
    "build_contradiction_graph",
    # Drift
    "drift_compute",
    "drift_score",
    "drift_brief",
    "build_cooccurrence_matrix",
    "build_ego_vectors",
    # Dashboard / card generation
    "generate_dashboard",
    "generate_pattern_cards",
]
