---
artifact: design-substrate/Spec_Control_Plane_v1_85.md
version: v1.85
cleared_at: 2026-06-27T22:30:00-06:00
clearance_type: phase-7-bundled-absorption
back_reference:
  - .harness/arc-ledger.yaml
merge_commit: (pending — co-landed in this arc's PR)
reviewer_chain:
  - advisor full-transcript (BEFORE substantive work — the DECOMPOSE discriminator [close SAVE_POINT as the #779 fan-out analogue; ground RECONCILER separately per the arc's own decompose_at_open + the #779→#781 LINEAR precedent]; the CAN-vs-DOES capture-producer requirement [substrate-agnosticism proves the producer CAN fire, not that it DOES — require a by-execution RED-without-fix witness, not a predicate unit test]; the #788 swap-fold check [does the existing `topology:engine` fold discriminate SAVE_POINT, or does the widen reopen the swap]; the RECONCILER representability tie-breaker [does any (workload,topology) resolution pair RECONCILER_LOOP with a fan-out topology])
  - by-execution witness (RED-without-fix EMPIRICALLY CONFIRMED — reverting `_FANOUT_REPLAY_ENGINE_CLASSES` to {ESR,WAL} made `test_fanout_child_save_point_reconstructs_aggregate_under_deterministic_seed` fail at `present_branch_indexes == {0,1,2}` [Phase-1 captured NOTHING because `_fanout_replay_store` returned None for SAVE_POINT]; GREEN with the widen [the class-agnostic store captures the SAVE_POINT branches, `_crash_fan_out_resume` reconstructs, committed branches 0+2 recovered fire-once, only in-flight branch 1 re-dispatched, result-faithful])
  - representability grounding (the §11.2 overlay is fault-handling [total over EngineClass], NOT admissibility; the §11.3 20-cell matrix admits every (workload, engine) pair except (PIPELINE_AUTOMATION, PURE_PATTERN); RESEARCH/SOFTWARE_ENGINEERING/PIPELINE_AUTOMATION permit ORCHESTRATOR_WORKERS → fan-out + {SAVE_POINT,RECONCILER} is representable → neither leg is a trivial resolve-invalid)
  - out-of-family Codex on the diff (`just codex-review` --base)
supersedes:
superseded_by:
---

# Clearance — `Spec_Control_Plane v1.85`

v1.85 records the CP half of the R-FS-1 standalone arc `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT-FANOUT-CHILD-SAVE-POINT` — the **SAVE_POINT slice** of the `…-FANOUT-CHILD-SAVE-POINT-RECONCILER` follow-on the v1.84 carrier-segregation registered (C-CP-25 §25.15). The shared `_FANOUT_REPLAY_ENGINE_CLASSES` constant is widened {ESR,WAL} → {ESR,WAL,SAVE_POINT}, moving the branch-capture producer gate `_fanout_replay_store` AND the conjunct-2 fan-out recoverability predicate `_fanout_recoverable` in lockstep. Paired with runtime spec change-note v1.90 → v1.91.

Grounding overturn (the load-bearing reversal, SAVE_POINT only): the v1.84 registration anticipated "a SAVE_POINT/RECONCILER fan-out child has NO fan-out replay store." Grounding shows that is over-cautious for SAVE_POINT — the same overturn shape as #779. Three facts: (1) the branch-capture store is the engine-class-AGNOSTIC `EngineOutputStore` (the {ESR,WAL} gating was a CP-side under-extension, not a substrate gap); (2) the fan-out aggregate reconstruction `_determine_fanout_resume` consumes ONLY that class-agnostic store ("the STORE is the SOLE which-branches-completed authority"), NOT the ESR/WAL-only §8.1 cached-output-replay channel; (3) the §14.22 effect fence is auto-active for SAVE_POINT (`_DURABLE_AUTO_FENCE_ENGINE_CLASSES` includes all four durable classes → in-flight branch re-dispatch is fenced).

Why SAVE_POINT closes but RECONCILER does not (the decompose, advisor-directed, mirroring #779→#781): SAVE_POINT is the §11.2 ABOVE_ENGINE reading — the harness branch store is the SOLE aggregate authority, no engine-owned competing substrate, NO CAS-claim / F-1 window. RECONCILER is the §11.2 RECONCILER reading — engine owns reconvergence via CRD-resource-version → whether the U-RT-123 reconciler substrate COMPETES with the branch store for the fan-out AGGREGATE authority (the two-authorities question #781 grounded for LINEAR), plus its CAS/F-1 window under a fan-out of branches, is UNGROUNDED → its own registered build arc (`…-FANOUT-CHILD-RECONCILER`).

CAN vs DOES (the honest-vs-vacuous gate): substrate-agnosticism proves the producer CAN fire, not that it DOES. Today `_fanout_replay_store` returned None for SAVE_POINT → `_capture_branch_terminal` no-op'd → no branch records. The by-execution witness drives the REAL `compose_child_workflow_runner` → `execute_workflow` for a SAVE_POINT PARALLELIZATION child and was empirically confirmed RED before the widen (Phase-1 `present_branch_indexes == set()`), GREEN after — blocking the green-over-dead-producer failure.

Scope honesty (the capture gate is RUN-scoped): `_fanout_replay_store` gates on the RUN's `engine_class` and the capture sites fire in the run-scoped concurrent-strategy path reached by EVERY SAVE_POINT fan-out run, so this widen ALSO activates TOP-LEVEL SAVE_POINT fan-out crash-resume recovery (capture + `_determine_fanout_resume`), not only the sub-agent-child case. This is intrinsic to a run-engine-class gate (it cannot be scoped to "only when child") and is a strict improvement — the same engine-class-agnostic B-FANOUT-OUTPUT-REPLAY machinery the {ESR,WAL} top-level feature (#723/#724) uses, extended to SAVE_POINT. The sub-agent-child case is the arc's named surface; the top-level activation is a beneficial co-effect closing a latent gap.

Cross-topology at-most-once — already covered by the #788 fold (no new hole): the `_payload_engine_signature` dual-gate marker already folds `f"{topology}:{engine}"`, so a fan-out SAVE_POINT signature `parallelization:save-point-checkpoint` is distinct from the bare LINEAR-SAVE_POINT marker and every other combo → a LINEAR↔fan-out or fan-out↔fan-out SAVE_POINT swap fails the dual gate closed (witnessed at `test_recursive_signature_catches_save_point_topology_swap`). `{engine_class, topology_pattern}` stays the complete recovery-selecting pair; SAVE_POINT only adds a member to the already-folded engine axis.

At-most-once scope (the honest claim): the widen introduces NO new at-most-once window versus the {ESR,WAL} fan-out-child slice. SAVE_POINT fires NO CAS-claim → no F-1 window; the in-flight-branch disposition is the EXISTING B-FANOUT-CRASH-RESUME-MAYBE-RAN family. The PROCEED in-flight-effect-bearing re-fire window is the SEPARATELY-registered operator-gated `…-ORCHESTRATOR-PROCEED-RESIDUAL` arc.

Spec-vs-fork: bundled-absorption amendment, NOT X-AL-3. v1.84 explicitly named the SAVE_POINT/RECONCILER fan-out-child case as a registered follow-on (a fail-closed gap, NOT a committed closed predicate). Additive recovery for a previously-fail-closed surface using the EXISTING substrate, sacrificing no committed decision → no operator gate (v1.77 §3 precedent). NO §5.2 IS-hash change (the topology fold is on the non-attested `child_engine_class` marker, unchanged); NO new contract / ADR / enum / fail-class / Protocol widening / CXA edge. `closure_gate.py` G1.1 was `2 + 0`; after close 1 + register 1, `standalone_registered` stays `2` (net-zero), `standalone_closed` 66 → 67 → R-FS-1 stays ACTIVE.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
