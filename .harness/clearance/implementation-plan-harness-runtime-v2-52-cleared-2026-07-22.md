---
artifact: design-substrate/Implementation_Plan_Harness_Runtime_v2_52.md
version: v2.52
cleared_at: 2026-07-22T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-Class-2-fork-ratification (B-59 apply arc; implementation-planner absorption per CLAUDE.md §4.3 + §4.5)
back_reference:
  - .harness/class_2_fork_b59_capacity_authority_across_bootstraps.md (RATIFIED 2026-07-21 — option A AS RECOMMENDED)
  - design-substrate/Spec_Harness_Runtime_v1.md (the v1.104 §14.8.10.6 surface this plan delta absorbs)
merge_commit: pending (pre-merge at filing time; B-59-A apply PR)
reviewer_chain:
  - operator ratification (2026-07-21) — option A as recommended
---

# Clearance — Implementation_Plan_Harness_Runtime_v2_52 v2.52 (B-59 apply arc)

v2.51→v2.52: ONE NEW atomic unit U-RT-146 (unit count 145→146) — cross-bootstrap capacity-authority continuity (Runtime v1.104 §14.8.10.6 contract in full): adopt-not-reconstruct binding at stage 5, adopt-new-budget-carry-occupied reconciliation, budget-shrink-below-occupied typed refusal, every-admission-surface rider (fan-out + direct `reserve(1)`), lease-release path byte-unchanged, per-run isolation preserved, interpreter-exit posture unchanged, test-isolation reset seam. Depends on prior-landed U-RT-141 (the grow-on-demand executor + shared frame budget, Runtime plan v2.50 §1.2). All 5 fork §4 verification obligations (1, 1b, 2, 3, 4, 5) homed here, each PD-8 mutation-probed. No CP plan unit owed — the CP-side change (Spec_Control_Plane_v1_104.md §1) is a reading clarification of the existing admission formula, not a new contract.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
