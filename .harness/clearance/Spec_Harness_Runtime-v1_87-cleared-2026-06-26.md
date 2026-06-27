---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.87
cleared_at: 2026-06-26T23:30:00-06:00
clearance_type: phase-7-bundled-absorption
back_reference:
  - .harness/arc-ledger.yaml
  - design-substrate/Spec_Control_Plane_v1_81.md
merge_commit: (pending — co-landed in this arc's PR)
reviewer_chain:
  - advisor full-transcript (BEFORE substantive work — GO on the decompose + the EFFECT-level crux witness + carrier-segregation + the RECONCILER contrasting baseline)
  - by-execution witnesses (the runtime predicate verdict flip SAVE_POINT→True [RED-without-fix] + RECONCILER→False control; the CP↔runtime agreement witness; the EFFECT-level recursive-child SAVE_POINT reconstruct)
  - out-of-family Codex on the diff (pending pre-merge — `just codex-review`)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.87`

v1.87 records the RUNTIME half of the R-FS-1 standalone arc `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT-SAVE-POINT-CHILD` (paired with CP spec v1.80 → v1.81). The typed mirror predicate `subagent_child_recoverable` (`sub_agent_dispatch.py`) — which gates the composer's deterministic `child_run_id_seed` — has its child-engine-class conjunct extended from `{EVENT_SOURCED_REPLAY, WAL_SEGMENT}` to `{EVENT_SOURCED_REPLAY, WAL_SEGMENT, SAVE_POINT_CHECKPOINT}` (the `_SUBAGENT_RECOVERABLE_CHILD_ENGINE_CLASSES` set). A maybe-ran fan-out / orchestrator SUB_AGENT_DISPATCH whose child is a SINGLE_THREADED_LINEAR SAVE_POINT_CHECKPOINT leaf now gets the deterministic seed (so its OWN crash-resume auto-resumes from the durable store) and is admitted by the CP classifier dual gate.

What was reviewed: the typed mirror is the runtime counterpart of the CP `_subagent_child_recoverable` defensive read; the by-execution agreement witness enforces parity (a CP-True / runtime-False drift would admit re-dispatch with no seed → double-fire). `RECONCILER_LOOP` stays OUT pending the registered `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT-RECONCILER-CHILD` (the U-CP-97 reconverge F-1 won-CAS-claim-retry-ABORTs-to-HITL window). The at-most-once safety rests on the same compositional-recursive-child property as ESR/WAL, witnessed at the EFFECT level by `test_recursive_child_crash_resume_save_point_reconstructs_full_final_state` (full final_state + only step-2 re-dispatched → committed prefix not re-fired).

Scope: no new contract (a value added to an existing frozenset), no new field, no new fail-class, no §5.2-hash change (the seed-gating + recoverability marker are non-attested, not in the §6 chain), no `StepDispatcher` Protocol widening, no new CXA edge. IS / OD / AS / ADR specs UNCHANGED. CXA v2.20 UNCHANGED. No operator gate (additive recovery for a previously-fail-closed surface, no committed-invariant sacrifice, at-most-once preserved).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
