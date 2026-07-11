---
artifact: design-substrate/Spec_Control_Plane_v1_96.md
version: v1.96
cleared_at: 2026-07-11T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-bundled-arc
back_reference:
  - .harness/b18-prewarm-ow-design-decision-record.md (pre-build DDR, review-cleared)
  - .harness/arc-ledger.yaml (B-18-PREWARM-OW close — the registered B-* queue empties)
  - design-substrate/Spec_Control_Plane_v1_95.md (§25.19 partition contract + the B-18-PREWARM-OW registration this arc discharges)
  - design-substrate/Spec_Control_Plane_v1_89.md (the "warmup is irrelevant outside PARALLELIZATION" characterization EXPLICITLY superseded at item 1)
  - design-substrate/ADR-D4.md (§1.8 lines 228-242 "all cells where fan-out cap > 1" + Consequences (f) default-on)
merge_commit: pending (pre-merge at filing time)
reviewer_chain:
  - ADR-D4 v1.1 §1.8 authority ("orchestrator-workers" named at line 242)
  - Fable-5 pre-build adversarial DESIGN review (AMEND-THEN-BUILD; 0 blocking + 4 concern —
    C1 rarity-leg inversion (cohort_key hashes binding.agent_role, which non-overridden
    bindings omit → orchestrator/worker key equality is the COMMON case), C2 phantom
    "§1.8(f)" label (the (f) item lives under ADR-D4 Consequences), C3 v1.89 supersession
    owed, C4 fence×partition witness gap — + 2 cosmetic, ALL folded pre-build; advisor +
    Codex down — double-outage fallback per the validated reviewer ladder)
  - Reviewer empirical probes P1-P4 on the project interpreter (the task.result() resurface
    TRANSFERS to _cancel_worker's record-then-reraise handler; outer-watchdog cut resurfaces
    the NAKED CancelledError — the nested-HD vehicle)
  - Fail-on-main verification BY EXECUTION (10/13 witnesses fail against main's driver at a
    throwaway main worktree; OWP3/OWP4/OWP10 controls pass)
  - Post-build decorrelated diff review per the arc PR
---

# Clearance: CP spec v1.96 — B-18-PREWARM-OW (warm-up + cohort partition for ORCHESTRATOR_WORKERS)

**What changed.** §25.19 extended to the O-W worker fan-out — the second committed ADR-D4
§1.8 "fan-out cap > 1" cell, landed in the partition form directly. The O-W cascade-policy
site captures the full `d4_tunable` (v1.89's "warmup is irrelevant outside PARALLELIZATION"
superseded EXPLICITLY; docstring refreshed in-arc). The split adapts to O-W's no-prebuilt-
dispatcher-map shape: inline `lookup()` per worker, `StepKindDispatcherNotBoundError` →
non-capable, preserving the committed per-worker failure surface byte-exact. PROCEED = two
sequential gathers under the one deadline (no new carve-out — O-W's baseline IS the gather);
strict tiers = engine-local inline two-phase (one deadline + one watchdog registry, Phase-1
TaskGroup + the NORMATIVE post-group `task.result()` resurface, Phase-2 TaskGroup). The
orchestrator is NOT a cohort member (named rejection; resume-staleness + bounded cache-hit
cost + sibling-set reading — key equality with workers is the common case and is fine).
Obligation-4 scan family untouched at all EIGHT O-W exits; PAUSED boundary stays scan-free
(withheld followers re-dispatchable by snapshot omission; the resume re-partitions the
remainder). HD inherits per level (zero HD-specific code). The evaluator-optimizer
multi-evaluator half is CONTINGENT — discharged forward via the item-9 tripwire (any future
multi-evaluator cell MUST carry the warm-up + partition in its own registration). ZERO
store-write changes; ZERO new crash-visible additions; statuses / fail_classes / step
counts / §5.2 hash byte-unchanged; gate=False byte-identical (existing O-W suites = the
regression net, zero capable stubs repo-wide).

**What was reviewed.** The pre-build DDR (10 design decisions + failure-semantics +
degenerate-reduction tables + witness plan) against ADR-D4 §1.8, CP v1.95 §25.19, and the
engine code at HEAD 8213a681 — every cite re-verified byte-exact by the reviewer, the
asyncio semantics verified by execution (probes P1-P4), and the witness plan's fails-on-main
claims re-verified by execution post-build (10/13 at the designed assertions). 13 new
witnesses OWP1-OWP12 (OWP2 ×2) at
`harness-cp/tests/test_workflow_driver_orchestrator_workers_warmup.py`; prior-suite
containment green (both O-W suites 33 + parallelization warm-up/cohort 43+1).
