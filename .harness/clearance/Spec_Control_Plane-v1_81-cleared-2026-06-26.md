---
artifact: design-substrate/Spec_Control_Plane_v1_81.md
version: v1.81
cleared_at: 2026-06-26T23:30:00-06:00
clearance_type: phase-7-bundled-absorption
back_reference:
  - .harness/arc-ledger.yaml
  - .harness/arc-open-b-child-crash-resume-final-state-reconstruct-save-point.md
merge_commit: (pending — co-landed in this arc's PR)
reviewer_chain:
  - advisor full-transcript (BEFORE substantive work — GO on the decompose [close SAVE_POINT / register RECONCILER] + five sharpenings: the EFFECT-level crux witness [confirm resume_at>0, mind the no-cached-output-replay difference], carrier-segregation grep before touching _FANOUT_REPLAY_ENGINE_CLASSES, the RECONCILER→False contrasting baseline + agreement-test extension, the §25.15-body fail-closed-default confirmation, don't-over-excavate-RECONCILER)
  - by-execution witnesses (the predicate verdict flip SAVE_POINT→True [RED-without-fix, confirmed by source-stash] + the new RECONCILER→False control; the extended CP↔runtime agreement witness [SAVE_POINT True / RECONCILER False, predicates agree]; the EFFECT-level recursive-child SAVE_POINT crash-resume reconstruct [full final_state + only step-2 re-dispatched → committed prefix not re-fired]; the CP full-chain orchestrator SAVE_POINT-child RECOVERS [RED-without-fix] + the repurposed RECONCILER negative-control fail-closed)
  - out-of-family Codex on the diff (pending pre-merge — `just codex-review`)
supersedes:
superseded_by:
---

# Clearance — `Spec_Control_Plane v1.81`

v1.81 records the CP half of the R-FS-1 standalone arc `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT-SAVE-POINT-CHILD` — the **SAVE_POINT slice** of the maybe-ran SUB_AGENT re-dispatch recoverability extension (C-CP-25 §25.15). The `_subagent_child_recoverable` child-engine-class conjunct widens from `{EVENT_SOURCED_REPLAY, WAL_SEGMENT}` to `{EVENT_SOURCED_REPLAY, WAL_SEGMENT, SAVE_POINT_CHECKPOINT}` (the dedicated `_SUBAGENT_RECOVERABLE_CHILD_ENGINE_CLASSES` set). A maybe-ran fan-out / orchestrator `SUB_AGENT_DISPATCH` whose child is a `SINGLE_THREADED_LINEAR` SAVE_POINT_CHECKPOINT leaf now RECOVERS by re-dispatch instead of failing the run closed. Paired with runtime spec change-note v1.86 → v1.87 (the typed mirror predicate).

What was reviewed: the grounding that resolved the open at-most-once probe for SAVE_POINT. The CP driver computes `resume_at` for a SAVE_POINT_CHECKPOINT run via `_determine_resume_at` — the engine-class-agnostic F2-prefix join (the reference impl ESR/WAL/RECONCILER delegate to), so a maybe-ran SAVE_POINT child re-dispatched under the deterministic child run_id computes `resume_at>0` from its durable F2 prefix → the committed prefix is auto-resumed, NOT re-dispatched (at-most-once for committed effects) → and its final_state reconstructs (the CP v1.79 class-agnostic EngineOutputStore seed). Crucially a SAVE_POINT resume fires NEITHER the ESR/WAL-only inter-step cached-output rehydrate NOR the RECONCILER engine-layer recovery loop (U-CP-97 `attempt_resume`) — so a SAVE_POINT leaf carries no CAS lease and no F-1 ABORT window: the cleanest auto-resume. The decomposition cut holds because a maybe-ran RECONCILER child re-dispatch DOES fire the U-CP-97 reconverge, whose F-1 limit ABORTs a won-CAS-claim retry → §22.1 HITL — registered as `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT-RECONCILER-CHILD`.

Carrier segregation (advisor): the recoverability predicate's engine-class set is DEDICATED (`_SUBAGENT_RECOVERABLE_CHILD_ENGINE_CLASSES`), distinct from `_FANOUT_REPLAY_ENGINE_CLASSES` which the separate B-FANOUT-OUTPUT-REPLAY `_fanout_replay_store` branch-capture gate also consumes and must NOT admit SAVE_POINT. Both worker (fan-out) and orchestrator dispatch share the single `_subagent_child_recoverable` predicate, so the one conjunct change covers both surfaces.

Spec-vs-fork: bundled-absorption amendment, NOT X-AL-3. §25.15 v1.77 §3 framed `{ESR,WAL}` as the *witnessed* slice and explicitly named the SAVE_POINT/RECONCILER child case as already covered by a registered follow-on (a fail-closed gap pending the blocker, NOT a committed closed set); v1.77 §3 set the precedent that additive recovery for a previously-fail-closed surface sacrifices no committed decision → no operator gate. The blocker (suffix-only final_state for SAVE_POINT children) was retired at v1.79. No §5.2 IS-hash change; no new contract / ADR / enum / fail-class. `closure_gate.py` G1.1 was `4 + 0`; after this close-1-register-1 it is `4 + 0` (net-zero) → R-FS-1 stays ACTIVE.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
