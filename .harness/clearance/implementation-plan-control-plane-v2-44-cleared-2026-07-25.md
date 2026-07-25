---
artifact: design-substrate/Implementation_Plan_Control_Plane_v2_44.md
version: v2.44
cleared_at: 2026-07-25T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-tension-record
back_reference:
  - .harness/class_1_tension_b72_pre_dispatch_gate_owning_branch_identity.md
  - design-substrate/Spec_Control_Plane_v1_108.md
merge_commit: pending (direct-to-main commit at authoring time)
reviewer_chain:
  - operator AskUserQuestion ratification (2026-07-25)
  - out-of-family codex review, 5 rounds to convergence (`just codex-review` base=main) — round 1: [P1] this row's first draft understated its own scope, naming only the counting/carrier side and omitting the delivery-cell construction required to actually consume the resolved response at the fan-out dispatch sites; fixed before merge. round 2: [P2] a stale close-out recipe + pointer-table rows elsewhere in the canonicalization bundle (not this file's own body); fixed. round 3: [P2] this row's cited spec text lagged the applied delivery-requirement correction; fixed. round 4: no finding against this file. round 5: [P1] this row scoped its scope-discovery pass to the fan-out dispatch sites only, silently matching a spec (v1.108 §1) that at the time read as topology-agnostic — `EVALUATOR_OPTIMIZER`/`DECENTRALIZED_HANDOFF`'s sequential carriers were neither covered nor excluded; fixed by explicitly naming the exclusion (mirrors the spec's own new §1.2b)
supersedes: null
---

# Clearance — `Implementation_Plan_Control_Plane_v2_44` (B-72 item (1) spec leg, plan absorption)

Coverage-matrix-only delta absorbing `Spec_Control_Plane_v1_108.md` §1 (property 6 — pre-dispatch gate-owning branch counting, closes `B-72` net-position item (1)). ZERO existing unit is amended — the new property constrains a resolver that does not yet exist, so it is recorded as a DEFERRED coverage-matrix row (no unit owned at this spec leg), mirroring exactly how `Implementation_Plan_Control_Plane_v2_42.md` §5 deferred the parallel `hitl_responses` property 1-5 invariants and `v2.43` §5 deferred `B-70`'s effect-fence analogue, rather than assigning either to U-CP-64.

The deferred row explicitly names FOUR scope-discovery items after the codex [P1] correction: (i) the new carrier, (ii) the internal identity's shape, (iii) the `_collect_gate_owning_run_ids` tree-walk amendment, and (iv) the actual `HITLDeliveryCell` construction at the fan-out dispatch sites (`_execute_parallelization`/`_execute_orchestrator_workers`) — item (iv) was missing from a first draft of this row, which out-of-family review correctly flagged as leaving `B-72` item (1) unfixed even after (i)-(iii) landed (counting a branch as eligible does not by itself deliver the response to it). The row is explicitly bound to the `PARALLELIZATION`/`ORCHESTRATOR_WORKERS` fan-out topologies (round 5's correction, mirroring spec v1.108 §1.2b) — `EVALUATOR_OPTIMIZER`/`DECENTRALIZED_HANDOFF`'s sequential `EvaluatorOptimizerResumeState`/`HandoffResumeState` carriers are a distinct, ungrounded, out-of-scope gap this row does NOT own.

ZERO new units, ZERO amended unit bodies, ZERO DAG topology change, ZERO cross-axis cascade.

Impl leg (the resolver's scope-discovery + build, mirroring the B-39/B-70 impl-leg pattern) is a separate follow-on arc, not built by this clearance.

## Notes

- Phase 7 consumers may rely on `Implementation_Plan_Control_Plane_v2_44.md` as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
