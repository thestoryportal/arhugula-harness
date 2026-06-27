---
artifact: design-substrate/Spec_Control_Plane_v1_80.md
version: v1.80
cleared_at: 2026-06-26T22:00:00-06:00
clearance_type: phase-7-bundled-absorption
back_reference:
  - .harness/arc-ledger.yaml
  - .harness/arc-open-b-child-crash-resume-final-state-reconstruct-save-point.md
merge_commit: (pending — co-landed in this arc's PR)
reviewer_chain:
  - advisor full-transcript (BEFORE substantive work — discharged the registered two-authorities probe by BODY-reading the reconciler substrate; GO on store-reuse over the "second authority" anticipation, with the BLOCKING producer-half full-chain witness criterion + the resolving owner_axis CP-only check + the CAS-ordering witness)
  - by-execution witnesses (the producer→crash→consumer RECONCILER round-trip through the real execute_workflow [RED-without-fix], the engine-class gate-load-bearing guard, the CAS-abort-short-circuit + CAS-clean-falls-through ordering witnesses, and the preserved ESR/WAL/SAVE_POINT reconstruct / skew-fail-closed / no-journal-degrade / DRAINED partial_state / #680 override-path witnesses)
  - out-of-family Codex on the diff (pending pre-merge — `just codex-review`)
supersedes:
superseded_by:
---

# Clearance — `Spec_Control_Plane v1.80`

v1.80 records the CP half of the R-FS-1 standalone arc `B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT-RECONCILER` — the **RECONCILER slice**, completing the final_state-reconstruction family. A crash-resumed `SINGLE_THREADED_LINEAR` `RECONCILER_LOOP` run (child or top-level) over a committed prefix now reconstructs its COMPLETE `final_state`/`partial_state` instead of a silently SUFFIX-ONLY one. The delta extends the v1.79 §25.2/§25.6 resume-transparency invariant's durable-output-class set from `{EVENT_SOURCED_REPLAY, WAL_SEGMENT, SAVE_POINT_CHECKPOINT}` to ALL FOUR durable resumable classes `{EVENT_SOURCED_REPLAY, WAL_SEGMENT, SAVE_POINT_CHECKPOINT, RECONCILER_LOOP}` (the lone non-member, `PURE_PATTERN_NO_ENGINE`, is non-durable and not resumable).

What was reviewed: the grounding that **resolved the registered two-authorities probe** in favor of store-reuse, overturning the "second authority" anticipation as a stale mischaracterization. The `ReconcilerEnginePauseResumeSubstrate` (U-RT-123) does NOT persist the per-step `accumulated` output map — its `PauseEvent` carries a `StateSummary` DIGEST (`relevant_entries` / `summary_text` / `summary_hash` / `idempotency_key` / `external_references`) for the etcd-style CAS-lease + revalidation. (The `PauseEvent`'s five fields are `paused_at` / `pause_reason` / `state_summary_snapshot` / `external_refs_captured` / `pause_audit_entry_id` — there is no `partial_state` field; the v1.79 §3 + the prior code comment's "`partial_state` carried in its `PauseEvent`" was a mischaracterization, corrected in this arc.) The reconciler substrate is the authority for engine-layer CONVERGENCE state; the `EngineOutputStore` is the authority for the CP per-step OUTPUT map that builds `final_state` — they measure different things, so store-reuse adds no second authority, and `derive-from-the-reconciler-substrate` is non-viable (the per-step outputs are not in the digest). A real `RECONCILER_LOOP` run flows through the SAME `SINGLE_THREADED_LINEAR` dispatch loop where the producer + seed sit. So the close is a CP-side gate extension reusing the existing class-agnostic store, NOT a new substrate. CP-ONLY — no runtime SPEC delta, no runtime src behavior change (the store binds class-agnostically on `engine_output_replay`; the `owner_axis: "CP + runtime"` anticipation resolved to CP-only; the `engine_output_replay` docstring is clarified impl-side only).

The blocking review criterion (advisor): a producer-half full-chain witness driving a REAL RECONCILER forward run (NOT a hand-seeded store) — the gate between an honest light close and a vacuous one. Confirmed RED on HEAD (phase 1 recorded NOTHING — the producer excluded RECONCILER, `assert set() == {0,1,2}`) → GREEN with the gate extension. The producer is therefore non-vacuous for RECONCILER. RECONCILER-specific CAS ordering verified by execution: an aborting CAS reconverge (lost claim) returns FAILED with `final_state=None` upstream of the seed (no reconstruction on a lost claim); a won/no-pause resume falls through to the seed and reconstructs.

Caveat for Phase 7 consumers: this is the LINEAR RECONCILER slice — RECONCILER is the LAST durable resumable engine class, so this completes the final_state-reconstruction family across `{ESR, WAL, SAVE_POINT, RECONCILER}` (a FAN-OUT RECONCILER's aggregate is the separate B-FANOUT-OUTPUT-REPLAY family). It is **close-1-register-1** (net-zero): out-of-family Codex surfaced that the maybe-ran SUB_AGENT recoverability predicates (CP `_subagent_child_recoverable` + the runtime mirror, both gating `{ESR,WAL}`) cited this arc as their exclusion blocker — final_state now reconstructs for SAVE_POINT/RECONCILER children, retiring that "no store → suffix-only" reason, but re-dispatch recoverability stays fail-closed pending the newly-registered `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT-SAVE-POINT-RECONCILER-CHILD` (the RECONCILER F-1 CAS-claim at-most-once window; a SAVE_POINT leaf has no CAS lease → likely the cleaner decomposed slice). The two stale docstrings were corrected in this PR. `closure_gate.py` G1.1 was `4 + 0`; after this close-1-register-1 it is `4 + 0` (net-zero) → R-FS-1 stays ACTIVE. No operator gate (additive; the spec NOT-YET-PROVIDED reconstruction for RECONCILER — a registered boundary — it did not FORBID it; no committed-invariant sacrifice). No §5.2 IS-hash arc.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
