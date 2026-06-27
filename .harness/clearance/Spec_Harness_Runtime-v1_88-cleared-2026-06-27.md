---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.88
cleared_at: 2026-06-27T09:30:00-06:00
clearance_type: phase-7-bundled-absorption
back_reference:
  - .harness/arc-ledger.yaml
  - .harness/arc-open-b-child-crash-resume-final-state-reconstruct-save-point.md
merge_commit: (pending — co-landed in this arc's PR)
reviewer_chain:
  - advisor full-transcript (BEFORE substantive work — option-(a) GO + the two SAVE_POINT-didn't-need verifications: the vacuity / engine_recovery_loop-binding check + the parent-disposition full-chain witness per `[[recovery-effect-fidelity-vs-result-fidelity]]`)
  - by-execution witnesses (the runtime predicate verdict flip RECONCILER→True [RED-without-fix] + the new PURE_PATTERN→False control; the extended CP↔runtime agreement witness [all four durable True / PURE_PATTERN False]; the integration NON-VACUOUS clean-CAS auto-resume + the F-1 ABORT case-3 + the FULL-CHAIN F-1 parent-disposition witness; the CP full-chain orchestrator RECONCILER-recovers / PURE_PATTERN-fail-closed pair)
  - out-of-family Codex on the diff (pending pre-merge — `just codex-review`)
supersedes:
  - .harness/clearance/Spec_Harness_Runtime-v1_87-cleared-2026-06-26.md
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.88`

v1.88 records the RUNTIME half of the R-FS-1 standalone arc `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT-RECONCILER-CHILD` (paired with CP spec v1.81 → v1.82). The typed mirror predicate `subagent_child_recoverable` (`sub_agent_dispatch.py`) — which gates the composer's deterministic `child_run_id_seed` — has its child-engine-class conjunct extended from `{EVENT_SOURCED_REPLAY, WAL_SEGMENT, SAVE_POINT_CHECKPOINT}` to `{EVENT_SOURCED_REPLAY, WAL_SEGMENT, SAVE_POINT_CHECKPOINT, RECONCILER_LOOP}` (the `_SUBAGENT_RECOVERABLE_CHILD_ENGINE_CLASSES` set) — ALL FOUR durable resumable engine classes; `PURE_PATTERN_NO_ENGINE` (non-durable, no resume) is the sole non-member.

What was reviewed: the runtime predicate is the typed MIRROR of the CP `_subagent_child_recoverable` defensive read; the by-execution agreement witness enforces parity (a CP-True / runtime-False drift would admit re-dispatch with no seed → double-fire). The RECONCILER admission is at-most-once-safe AND result-faithful WITHOUT first building the F-1 engine-lock auto-recovery arc — the re-dispatched child runs its OWN crash-resume, the U-CP-97 reconverge gates at the CAS revision claim upstream of the step loop, so the F-1 window manifests as `RunStatus.FAILED` before any step re-executes (never a double-fire) and the parent fold raises `SubAgentChildFailedError` (never a SUCCESS aggregate). The F-1 engine-lock auto-recovery is a separate, pre-existing, broader capability (all RECONCILER resumes; the substrate F-1/F-2/F-CC honest-limits docstring, F-CC at O-E3-2) — not a prerequisite → WHOLE close.

Cross-engine-class swap guard (out-of-family Codex [P1] on the diff, absorbed in-arc — see CP v1.82 §3). Because the widened set now has >1 recoverable engine class and `compose_child_run_id_seed` is engine-class-AGNOSTIC, a same-`step_id` RECONCILER→SAVE_POINT swap would re-dispatch the child against the same durable store through a different recovery mechanism, bypassing the RECONCILER CAS at-most-once protection. The `EngineOutputStore` reserve-before-dispatch markers therefore gain ONE additive non-attested marker-record field — `child_engine_class` on `record_branch_dispatched` + `record_orchestrator_dispatched` (omitted when `None` → pre-arc markers byte-identical), read back by the new `dispatched_branch_child_engine_classes` + `orchestrator_dispatched_child_engine_class` readers — so the CP maybe-ran gate requires the marker engine == the resumed engine (fail closed on mismatch / `None`). The SAME non-attested marker-record category as the existing `child_recoverable` field; RED-without-fix witnesses at both worker + orchestrator surfaces.

No new contract (a value added to an existing frozenset); ONE additive non-attested marker-record field (`child_engine_class`, the same category as the existing `child_recoverable` marker field — NOT a §6-chain / §5.2-hash contract); no new fail-class; no §5.2-hash change (the seed-gating + recoverability + engine-class markers are non-attested, not in the §6 chain); no `StepDispatcher` Protocol widening; no new CXA edge. CP spec C-CP-25 §25.15 v1.81 → v1.82 is the paired primary contract. IS / OD / AS / ADR specs UNCHANGED. CXA v2.20 UNCHANGED. No operator gate (additive recovery for a previously-fail-closed surface, no committed-invariant sacrifice, at-most-once PRESERVED — the swap guard HARDENS at-most-once).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- Supersedes the v1.87 marker (the prior SAVE_POINT-slice runtime change-note); the v1.87 body is preserved verbatim in the runtime spec change-note chain.
- See `.harness/clearance/README.md` for marker discipline.
