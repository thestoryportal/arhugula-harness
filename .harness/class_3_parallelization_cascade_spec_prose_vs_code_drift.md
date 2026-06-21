# Class 3 (informational) — CP v1.42 line-23 spec-prose-vs-code drift, RESOLVED by B-PARALLELIZATION-CASCADE

**Filed:** 2026-06-21 · R-FS-1 standalone arc **B-PARALLELIZATION-CASCADE** (closed; arc-ledger). Class 3 = informational, non-blocking; the drift is **resolved by the same arc that surfaced it** (no separate back-flow owed). Surfaced during grounding for the PARALLELIZATION cascade build; mirrors the workspace's biggest defect class (`[[spec-prose-plan-body-drift-pattern]]`).

---

## The drift

`Spec_Control_Plane_v1_42.md` §1 line 23 (the B-FANOUT-PAUSE / ORCHESTRATOR_WORKERS-only scope note) states:

> `EVALUATOR_OPTIMIZER` + `PARALLELIZATION` (sibling fan-out-barrier strategies) and `DECENTRALIZED_HANDOFF` … and `HIERARCHICAL_DELEGATION` each carry their own `*-pause-resume-not-yet-materialized` FAILED branch → registered as forward arcs …

At HEAD (`25cce5c` parent) the claim was **true for ORCHESTRATOR_WORKERS / HIERARCHICAL_DELEGATION / DECENTRALIZED_HANDOFF** (each has a `…-pause-resume-not-yet-materialized` fail_class in `workflow_driver.py`), but **FALSE for PARALLELIZATION**: `_execute_parallelization` (U-CP-86) was built happy-path-only ("U-CP-85 non-dep") — it had **no cascade_policy resolution at all**, so ANY branch failure fail-fasted to a generic `parallelization-branch-failure` FAILED via the `bounded_barrier`/`except Exception` path. There was no `pause` branch, hence no `…-not-yet-materialized` fail_class. The spec prose described a code surface that did not exist.

## Resolution

**B-PARALLELIZATION-CASCADE** (impl-to-cleared-spec on §25.15 + §25.18) materializes the §25.15.1 cascade_policy for PARALLELIZATION:

- `proceed` (SOLO) → harvest survivors → PARTIAL
- `cascade-cancel` (MTC) → cancel siblings → FAILED + cancelled-terminals
- `pause` (TEAM) → FAILED + **`parallelization-pause-resume-not-yet-materialized`** ← the branch the spec claimed now genuinely exists

So the drift is **closed by construction**: PARALLELIZATION now carries the `…-pause-resume-not-yet-materialized` FAILED branch CP v1.42 line 23 always described. The resumable PARALLELIZATION pause (turning that honest-fail into a genuine resumable PAUSED) is the registered follow-on `B-FANOUT-PAUSE-PARALLELIZATION`.

## Why no spec amendment

No design-substrate edit is owed: line 23 was *aspirationally correct* (it described the intended end-state); the code lagged it. This arc makes the code match the prose, which is the direction that needs no spec change (the spec was already cleared at §25.15 + §25.18). The note is filed for traceability only.
