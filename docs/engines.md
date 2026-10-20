# The three engines, with worked examples

Every example below was run against the five sample cards shipped in `tests/fixtures/`.
The outputs are real, copied from those runs.

## 1. Anti-Crowd Score (ACS): is this opportunity worth entering?

ACS scores every strategy zone on one question: how attractive is this zone relative
to how many competitors already sit in it? It combines market size, competitor
concentration, regulatory burden, revenue potential, build time, and an internal
coverage ratio into a single score plus an ENTER / WATCH / IGNORE recommendation.

```bash
rig-anticrowd all --cards-dir tests/fixtures
```

Real output (top rows):

```
Rank Strategy                       Cards      ACS  RiskAdj        Rec
------------------------------------------------------------------------------------------
   1 pricing-finance                    0    12.05     6.65      WATCH
   2 strategy-decision-routing          0    12.05     6.65      WATCH
   3 local-inference-fleet              0     9.64     5.32      WATCH
```

Read it like this: `pricing-finance` ranks first on the raw score (ACS 12.05) but the
risk-adjusted score (6.65) keeps it at WATCH rather than ENTER. The `Cards` column
shows how many cards in the corpus carry that strategy tag.

## 2. Contradiction Arbitrage Rank (CAR): which claims disagree?

CAR compares every pair of cards and finds direct contradictions: two cards that make
opposing claims about the same thing. Each contradiction gets a score that reflects how
central the disagreement is and how close it looks to being resolved.

```bash
rig-contradiction brief --cards-dir tests/fixtures
```

Real output:

```
Summary:
  total pairs:        1
  breakthrough cand.: 0
  active:             0
  tilting:            0
  resolved:           0

Top 5 contradictions:
  #1 CAR=0.0000 state=dormant Pbreak=0.50 conf=low direction=l2-43a48363baea9d97 gaining ~8w
      pair: ['l2-40510b211793548d', 'l2-43a48363baea9d97']
      strategies: ['determinism-gates']
      reasons: negation overlap + same strategy, token_overlap=0.16
```

One contradiction found in this small corpus. It is dormant (both sides currently
standing) and the engine predicts it needs roughly 8 weeks to tilt one way.

## 3. Epistemic Drift: which vocabulary is on the move?

Drift watches language. For each strategy zone it measures how much of the vocabulary
is frontier (new terms), how much crosses domain boundaries, and how fast terms are
appearing. Zones with high frontier and bridge activity are flagged as leading
indicators: the language is moving before the market does.

```bash
rig-drift brief --cards-dir tests/fixtures
```

Real output (top strategy):

```
#1 operations (composite=0.3750)
  tier=T2  cards=2
  prediction: category edge
  frontier=0.62 emerging=0.12 established=0.25
  bridge_concepts=1 bridge_ratio=0.12
  drift_velocity=0.50 cross_domain=0.25
  frontier entities: case study, causal, content, systematic review, team
```

`frontier=0.62` means 62% of this zone's vocabulary is new, and `drift_velocity=0.50`
says the new terms are arriving fast. That is what "category edge" means here.
