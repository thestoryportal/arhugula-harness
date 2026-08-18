# E1 A2 — C8 eval engineer (consultant, reacting to C9/C10/C7/C5/C1)

## Reactions to prior voices

| finding | reaction | evidence | resulting fix |
|---|---|---|---|
| C7-F3 (`no_finding` marker) | REFINE | `unique_catch: bool` never defined; `disposition` independent of it — a `unique_catch=true` row can later be `rejected` | "`unique_catch=true` MUST mean (a) the finding's `location`+`finding_type` appears in no row from the blocking reviewers for the same `head_sha`, AND (b) last-row `disposition = accepted`. A `unique_catch=true` row later `rejected` MUST NOT count toward the `≥2` threshold." |
| C7-F4 / C5 (`disposition_actor`) | REFINE | one adjudication event yields both facts | "`disposition_actor` MUST record the identity that resolved both the neither-family adjudication and the accepted/rejected disposition in the same write." |
| C7-F5 (`concurrent_lanes` key) | REFINE | `by_levers` keys on the declared `levers_active`; `concurrent_lanes` is derived and driven by operator scheduling, plausibly correlated with `arc_type` | C-HE-28 §1: "The cohort split MUST be joint on `(concurrent_lanes, arc_type)` once `arc_type` is uncontaminated (C-HE-26); until joint cells populate, AC#10 claims MUST report the joint breakdown or caveat that `arc_type` was not controlled." |
| C5-F5 (state-machine test) | REFINE | P(0 FP in 20 replayed arcs | p=0.05) = 0.95²⁰ ≈ 0.358 | "The §8.1 unit test asserts the mechanism; it MUST NOT be cited as evidence the threshold is calibrated; C-HE-31 §4 MUST state the target FP rate the bar excludes (C8-F3)." |
| C10 T7 wording (demotion row) | TENSION | at p=0.03, P(≥2 in a 20-window) ≈ 0.12 → rolling flap; logging a flap ≠ preventing it | Pair with a hysteresis rule (C8-F3). |
| C1-F2 / C7-T10 (S2 hand-off) | REFINE | "shape resolved" ≠ "cohort design defensible" | Extend the S2/S6 hand-off: "C-HE-28's split MUST be verified joint-stratified on `(concurrent_lanes, arc_type)` before any AC#10 value claim." |

## Own findings

| id | class | contract | quote | defect | fix |
|---|---|---|---|---|---|
| C8-F1 | 1 | C-HE-29 §2 | "fewer than 2 unique catches across the 15 scored rounds ⇒ kill" | No operating characteristics. P(kill | p=0.10, n=15) = 0.9¹⁵ + 15·0.1·0.9¹⁴ ≈ 0.549; p=0.15 ≈ 0.32; p=0.20 ≈ 0.17. Reliable only for lenses catching ≥ ~25% of rounds. | "C-HE-29 §2 MUST state the OC table (P(kill) at p ∈ {0, .05, .10, .15, .20, .25}); the plan SHOULD either (a) widen (n=30, kill if < 3 → p=0.10 false-kill ≈ 0.18) or (b) adopt an SPRT between H0 p≈0.02 and H1 p≈0.15 with stated α/β. A policy call the spec MUST name." |
| C8-F2 | 1 | C-HE-29 §3 Verification | "kill/keep decision reproducible from rows alone" | Reducer correctness ≠ operational definition; without the accepted gate a hallucinating lens survives | "Add a fixture where a `unique_catch=true` row is later `rejected`; assert the reducer excludes it — the actual falsifier." |
| C8-F3 | 2 | C-HE-31 §4 | "zero false positives across … 20 merged arcs … ≥ 2 rejected findings in 20 arcs is demoted" | No target FP rate; fixed-vs-rolling unstated; if rolling, flap at p≈0.03 (P≈0.12/window) | "State (a) fixed-at-promotion vs rolling; (b) if rolling, hysteresis — demotion only on a second independent 20-arc window (two strikes), or raise promotion to n=40/0 FP." |
| C8-F4 | 2 | C-HE-26 §3 | "may be built or evaluated until … round-log→arc mapping exceeds 3 of 18" | "Build" and "evaluate" need different n; ~4-5 labeled arcs cannot evaluate a routing rule | "Split into a BUILD gate (>3/18) and an EVALUATE gate (≥20 uncontaminated open-labeled arcs) before any routing-accuracy claim." |
| C8-F5 | 2 | C-HE-24 §1 | "N6 'problems prevented per hour'" | Undefined | "N6 = COUNT(DISTINCT `finding_id` whose last row has `disposition = accepted`) in the window ÷ Σ(`phases.verify` + `phases.edit`) hours across the window's arcs from the durable `phases` map — never an inter-row delta (C-HE-27 §2)." |
| C8-F6 | 1 | C-HE-28 §1/§3 | "`concurrent_lanes` is the cohort key" / "Behavioral endogeneity …" | Assignment to N is operator-chosen, not randomized — selection bias; the historical N=1 set is not a counterfactual for whichever arcs get batched | "§3 MUST name the mechanism (operator-chosen assignment; simpler `applying` arcs likely batched); joint stratification is the minimum; AC#10 results are correlational unless a forward-register item adds randomized/quasi-randomized assignment on a controlled subset." |
| C8-F7 | 1 | C-HE-22 Verification | "2 and 4 concurrent … invocations against a fixed diff; record …" | Single-shot, no pass/fail rule; `arc_metrics.py:780-793` `fmt_span` docstring: "Measured round variance is ~5x" — one trial cannot separate throttling from noise, yet the probe gates pilots | "≥5 repetitions at each of {1, 2, 4}; GREEN iff median per-call wall-clock at N ≤ 2× the N=1 median AND zero C-HE-15 validity failures; else RED (throttling assumed)." |
| C8-F8 | 3 | C-HE-13 §3 | "any named recurring friction is recorded" | "recurring" undefined at n=3 (P(≥2 of 3 | p=0.4) ≈ 0.35) | "recurring = a `cause_signature` in ≥2 of the ≥3 pilots, OR one occurrence the operator rates independently severe." |
| C8-F9 | 2 | §0.3, §8.1 | mutation-probe rule vs manifest columns | `tools/mutation_probe.py` is a genuine RED-first falsifier (flock, clean-tree gate, baseline check, `compile()` gate, byte-verified restore), but §8.1 has no `mutation-probe` column; the discipline is enforced by manual cross-reading | "Add a `mutation-probe` column to §8.1 populated from every inline annotation; add `just mutation-probe-coverage-check` (or extend `lanes-verify`) asserting every tagged row has been probed before the contract closes." |

## Position on T9 / T7 / T10

T9 RECONCILE (sharper than C7): numerator undefined in a way that keeps unreliable lenses (F2); power against plausible catch rates unstated and poor (F1). T7 RECONCILE building on C10/C5: window semantics + hysteresis (F3); state-machine test is mechanism-only. T10 ACCEPT shape; RECONCILE via the S2/S6 hand-off extended with confound control (F6).

## Verified at HEAD

`arc_metrics.py:780-793` (`fmt_span` ~5x variance), `:812-832` (`by_levers` declared key; `concurrent_lanes` 0 occurrences) · `.harness/arc-metrics.jsonl` 18 rows, row-1 fields · `test_arc_metrics.py:531` mutation-probe annotation for the lever-set discipline · `tools/mutation_probe.py:1-60` mechanism · `justfile:259-260` `mutation-probe` recipe · spec §8.1 no `mutation-probe` column.

## Voice self-check

Stayed out of C9's retry mechanics and C10's wrapper arity. C8 cannot judge mechanism correctness (C9), only the soundness of measurements built on them. F1/F3 alternatives offered as options per "not a tradeoff-resolver"; the plan picks the operating point.
