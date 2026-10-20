"""RIG Pattern Engines — public API.

Three deterministic analysis engines for research-card corpora:

* Anti-Crowd Score (ACS): how attractive is a strategy zone relative to how
  crowded it is, with an ENTER / WATCH / IGNORE recommendation.
* Contradiction Arbitrage Rank (CAR): which pairs of cards disagree, and how
  close each disagreement is to resolving.
* Epistemic Drift: which vocabulary is new, crossing domains, and arriving
  fastest, per strategy zone.

Each engine is pure Python, makes no network or LLM calls, and produces JSON
reports and human-readable briefs from a directory of `l2-*.json` build cards.
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
)
from .pattern_anticrowd import (
    detect_synergies as anticrowd_synergies,
)
from .pattern_anticrowd import (
    generate_brief as anticrowd_brief,
)
from .pattern_anticrowd import (
    score_all_strategies as anticrowd_score,
)
from .pattern_contradiction import (
    build_contradiction_graph,
)
from .pattern_contradiction import (
    compute_car as contradiction_compute,
)
from .pattern_contradiction import (
    generate_brief as contradiction_brief,
)
from .pattern_contradiction import (
    score_all_contradictions as contradiction_score,
)
from .pattern_dashboard import generate_dashboard
from .pattern_drift import (
    build_cooccurrence_matrix,
    build_ego_vectors,
)
from .pattern_drift import (
    compute_drift as drift_compute,
)
from .pattern_drift import (
    generate_brief as drift_brief,
)
from .pattern_drift import (
    score_all_strategies as drift_score,
)
from .pattern_generate import generate_pattern_cards

__version__ = "0.2.0"

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
