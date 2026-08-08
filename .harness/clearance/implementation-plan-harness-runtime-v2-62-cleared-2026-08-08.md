---
artifact: design-substrate/Implementation_Plan_Harness_Runtime_v2_62.md
version: v2.62
cleared_at: 2026-08-08T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/forward-register.yaml row `B-118`
  - Spec_Harness_Runtime_v1.md v1.114 §14.6 step 4 + NEW §14.6.4
  - .harness/clearance/spec-harness-runtime-v1-114-cleared-2026-08-08.md
merge_commit: <pending — same PR as this marker>
reviewer_chain:
  - B-118 grounding + leg-design pass (read-only, at HEAD fb3dda44)
  - implementation-planner decomposition (this leg)
  - impl-time grounding pass (every AC witnessed by execution; fourteen PD-8 mutation probes, all seen RED)
supersedes: implementation-plan-harness-runtime-v2-61-cleared-2026-08-08.md
---

# Clearance — `Implementation Plan: Harness Runtime v2.62`

v2.62 carries **ONE new unit and ZERO amended units**: **U-RT-154**, the half-open latch wiring for Runtime spec v1.114 §14.6 step 4 + §14.6.4. A NEW unit rather than an amendment of U-RT-152/153, per the `B-97`(a) → U-RT-149, `B-111` → U-RT-151 and `B-115` → U-RT-153 precedent — both are LANDED and CLOSED, and amending a closed unit's acceptance criteria would falsify its closure criterion retroactively.

**Eleven acceptance criteria and fourteen PD-8 mutation probes** (ten and ten at first filing; AC #11 and P11–P14 were added at out-of-family review round 1), each probe naming the specific witness that must be seen RED. The load-bearing discipline is stated as a rule the unit is measured against: **a green state-machine unit test is NOT the witness** — the state machine was already green and the gap was reachability — so both recovery directions run end-to-end through the real `RetryBreakerFallbackDispatcher.dispatch` with an injected clock, and the concurrency witness GUARANTEES its interleaving with an `asyncio.Event` rather than hoping for it.

AC #8 carries the deliberate **`B-116` witness-strengthening roster** that C9's A1 recommendation 2 had forbidden while the recovery path was unreachable: seven witnesses gain their now-available assertions (including the Probe-C clock-advance form, which discriminates "never opened" from "opened and was reset", and the 401 / response-parsing **recovery-completion positive controls** that make the CHARGE mean something), three are named UNCHANGED, and `B-115`'s IS-side determinism witnesses are UNTOUCHED. AC #9 records why an existing witness had to be re-fixtured: it tripped its breaker by assigning `state` directly, and left as-was against a real `time.monotonic` it would have silently begun asserting a half-open trial instead of the skip it was written for.

**ONE new DAG edge (U-RT-153 → U-RT-154), ZERO cross-axis edges, ZERO CXA rows, ZERO clusters, ZERO contract numbers, ZERO Protocol widening, ZERO OD/CP delta.**

**Review round 1 absorbed at §0.7**: AC #11 (epoch-guarded trial ownership, witnessed at BOTH the state machine and end-to-end through the composer with the exact A/B interleaving) plus PD-8 probes **P11–P14**; and AC #6 reconciled against cell 4's VOID-BY-CONSTRUCTION status. **ELEVEN ACs / FOURTEEN probes.**

## Notes

`B-118` flips to `closed` at U-RT-154's merge. The `B-119` interaction is cross-noted at the register, not worked here.
