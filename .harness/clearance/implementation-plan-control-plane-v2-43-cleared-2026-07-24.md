---
artifact: design-substrate/Implementation_Plan_Control_Plane_v2_43.md
version: v2.43
cleared_at: 2026-07-24T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_2_fork_b70_effect_fence_resolution_uniform_fallback.md
  - design-substrate/Spec_Control_Plane_v1_107.md
merge_commit: pending (direct-to-main commit at authoring time)
reviewer_chain:
  - operator AskUserQuestion ratification (2026-07-24)
  - out-of-family codex review to convergence (recorded at this marker's supersession if findings land)
supersedes: null
---

# Clearance — `Implementation_Plan_Control_Plane_v2_43` (B-70 spec leg, plan absorption)

Coverage-matrix-only delta absorbing `Spec_Control_Plane_v1_107.md` §1 (the B-70 multi-branch effect-fence-resolution fallback-safety invariant). ZERO existing unit is amended — the new property constrains a resolver that does not yet exist, so it is recorded as a DEFERRED coverage-matrix row (no unit owned at this spec leg), mirroring exactly how `Implementation_Plan_Control_Plane_v2_42.md` §5 deferred the parallel `hitl_responses` property 4/5 invariants rather than assigning them to U-CP-64. ZERO new units, ZERO amended unit bodies, ZERO DAG topology change, ZERO cross-axis cascade.

Impl leg (the resolver's scope-discovery + build, mirroring the B-39 impl-leg pattern) is a separate follow-on arc, not built by this clearance.

## Notes

- Phase 7 consumers may rely on `Implementation_Plan_Control_Plane_v2_43.md` as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
