---
artifact: design-substrate/Spec_Control_Plane_v1_79.md
version: v1.79
cleared_at: 2026-06-26T20:30:00-06:00
clearance_type: phase-7-bundled-absorption
back_reference:
  - .harness/arc-ledger.yaml
  - .harness/arc-open-b-child-crash-resume-final-state-reconstruct-save-point.md
merge_commit: (pending — co-landed in this arc's PR)
reviewer_chain:
  - advisor full-transcript (BEFORE substantive work — the GO on Reading A [reuse the class-agnostic EngineOutputStore + relax the two CP gates] over the registered "new substrate" anticipation, with the BLOCKING producer-half full-chain witness criterion + the RECONCILER two-authorities split)
  - by-execution witnesses (the producer→crash→consumer SAVE_POINT round-trip through the real execute_workflow [RED-without-fix] + the RECONCILER out-of-scope degrade + the preserved v1.75/v1.76 ESR/WAL reconstruct / skew-fail-closed / no-journal-degrade / DRAINED partial_state / #680 override-path witnesses)
  - out-of-family Codex on the diff (pending pre-merge — `just codex-review`)
supersedes:
superseded_by:
---

# Clearance — `Spec_Control_Plane v1.79`

v1.79 records the CP half of the R-FS-1 standalone arc `B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT-SAVE-POINT` — the **SAVE_POINT slice** of the registered `B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT-SAVE-POINT-RECONCILER`. A crash-resumed `SINGLE_THREADED_LINEAR` `SAVE_POINT_CHECKPOINT` run (child or top-level) over a committed prefix now reconstructs its COMPLETE `final_state`/`partial_state` instead of a silently SUFFIX-ONLY one. The delta extends the v1.76 §25.2/§25.6 resume-transparency invariant's durable-output-class set from `{EVENT_SOURCED_REPLAY, WAL_SEGMENT}` to `{EVENT_SOURCED_REPLAY, WAL_SEGMENT, SAVE_POINT_CHECKPOINT}`.

What was reviewed: the grounding that overturns the registered "needs an entirely new output substrate" anticipation — the `EngineOutputStore` (runtime C-RT-32) is mechanically engine-class-AGNOSTIC (a per-run JSONL keyed by `run_idempotency_key`; stage-5 binding gated ONLY on `RuntimeConfig.engine_output_replay`, never on engine class), and a real `SAVE_POINT_CHECKPOINT` run flows through the SAME `SINGLE_THREADED_LINEAR` dispatch loop where the producer (`_record_durable_step_output` call site) and the `final_state` seed sit (its `resume_at` is the same F2-prefix join ESR/WAL use). So the close is a CP-side gate extension reusing the existing class-agnostic store, NOT a new substrate. The two gates were unified onto a SINGLE `_FINAL_STATE_RECONSTRUCT_ENGINE_CLASSES` constant so the documented "never record-only / never seed-only" discipline is structural. CP-ONLY — no runtime SPEC delta, no runtime src behavior change (the store was always class-agnostic; the `engine_output_replay` docstring is clarified impl-side only).

The blocking review criterion (advisor): a producer-half full-chain witness driving a REAL SAVE_POINT forward run (NOT a hand-seeded store) — the gate between an honest light close and a vacuous one. Confirmed RED on HEAD (phase 1 recorded NOTHING — the producer excluded SAVE_POINT) → GREEN with the gate extensions. The producer is therefore non-vacuous for SAVE_POINT.

Caveat for Phase 7 consumers: this is the LINEAR SAVE_POINT slice. `RECONCILER_LOOP` stays fail-closed (suffix-only degrade) → the registered follow-on `B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT-RECONCILER`, because RECONCILER is an ENGINE-OWNS-SUBSTRATE class (its authoritative state lives in the U-RT-123 reconciler substrate `partial_state`) so store-reuse would be a second output authority — the follow-on grounds store-reuse-vs-derive before wiring. A FAN-OUT SAVE_POINT's aggregate is the separate B-FANOUT-OUTPUT-REPLAY family, not this arc. Net-zero: close 1 + register 1. No operator gate (additive; the spec NOT-YET-PROVIDED reconstruction for SAVE_POINT — a registered boundary — it did not FORBID it; no committed-invariant sacrifice). No §5.2 IS-hash arc.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
