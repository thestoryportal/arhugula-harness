---
artifact: design-substrate/Spec_Control_Plane_v1_95.md
version: v1.95
cleared_at: 2026-07-11T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-bundled-arc
back_reference:
  - .harness/b18-epoch-partition-design-decision-record.md (pre-build DDR, review-cleared)
  - .harness/arc-ledger.yaml (B-18-EPOCH-PARTITION close + B-18-PREWARM-OW registration)
  - design-substrate/Spec_Control_Plane_v1_87.md (B-18-EPOCH-PARTITION registration)
  - design-substrate/Spec_Control_Plane_v1_88.md (CohortKeyCapable oracle prerequisite)
  - design-substrate/Spec_Control_Plane_v1_90.md (item 3 superseded; item 4 invariant preserved)
  - .harness/u1-slice3b-epoch-partition-design.md (§4.1 epoch key + §6 arc reshape)
merge_commit: pending (pre-merge at filing time)
reviewer_chain:
  - ADR-D4 v1.1 §1.8 authority (steps 2-4 committed; "all cells where fan-out cap > 1" scope)
  - Fable-5 pre-build adversarial DESIGN review (AMEND-THEN-BUILD; B1 §25.18-shadow + B2
    TaskGroup-swallow + C1-C5 + 4 cosmetic ALL folded pre-build; advisor + Codex down —
    double-outage fallback per the validated reviewer ladder)
  - Session-independent empirical probe (TaskGroup child-CancelledError semantics on system
    3.14.5 + project uv 3.12.13) — CONVERGENT with the reviewer's independent probe
  - Fail-on-main verification BY EXECUTION (8/8 claimed witnesses fail against main's driver
    at the designed assertions; EP3 control passes)
  - Post-build decorrelated diff review per the arc PR
---

# Clearance: CP spec v1.95 — B-18-EPOCH-PARTITION (heterogeneous cohort partition)

**What changed.** NEW §25.19: the v1.88 binary all-same-cohort warm-up predicate is superseded
by a K-cohort partition — branches group by dispatcher-attested `(step_kind, cohort_key)`;
Phase 1 dispatches one leader per multi-member cohort plus every non-beneficiary branch
(None-key / non-capable / singleton — they keep baseline immediacy); Phase 2 releases the
followers. Degenerate reductions are exact: all-same-key = the v1.87/v1.90
serialize-branch[0] schedule; no multi-member cohort = the gate-False all-concurrent baseline.
PROCEED phases via two `gather(return_exceptions=True)` calls (H1 generalized; named C1
carve-out: spontaneous branch CancelledError now captured → PARTIAL, aligning with the
gate-False baseline). Strict-tier Phase 1 via TaskGroup + NORMATIVE post-group
`task.result()` collection (v1.90 item 3 superseded; the collection closes the CPython
TaskGroup child-cancellation swallow that would otherwise dispatch followers after a
watchdog cut — the review-B2 / session-convergent empirical finding). Obligation-4 scan
family untouched (disposition-keyed, phase-free); ZERO store-write changes; statuses /
fail_classes byte-unchanged.

**What was reviewed.** The pre-build DDR (10 decisions D1–D10 + failure-semantics +
degenerate-reduction tables + witness plan) was adversarially reviewed by the Fable-5
fallback reviewer with per-decision dispositions (9 AGREE / 1 DISPUTE-in-part resolved by
amendment); the two blocking findings (§25.18 shadow → §25.19; TaskGroup swallow →
normative result-collection + EP9) plus C1–C5 and 4 cosmetics were ALL folded before any
code was written. The CK-3 witness-contract supersession is explicit (reshaped CK-3′ pins
the surviving contract half; EP1–EP9 pin the partition).

**O-W disposition.** ADR-D4 §1.8 commits the protocol for orchestrator-workers +
evaluator-optimizer-multi-evaluator as well; extending is REGISTERED (`B-18-PREWARM-OW`),
not silently widened — the FENCE-LEDGER-FIDELITY-OW precedent.
