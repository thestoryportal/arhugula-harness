---
artifact: design-substrate/Implementation_Plan_Control_Plane_v2_41.md
version: v2.41
cleared_at: 2026-07-23T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_b33_rotation_correlation_carrier.md (RATIFIED 2026-07-21 — Option A)
  - design-substrate/Spec_Control_Plane_v1_105.md
merge_commit: pending (pre-merge at filing time; B-33-A spec+plan leg PR)
reviewer_chain:
  - operator ratification (2026-07-21) — Option A
  - out-of-family codex review to convergence on the landing PR (recorded at the PR thread)
---

# Clearance — Implementation_Plan_Control_Plane_v2_41 (B-33 arc, plan leg)

v2.40→v2.41: amends the SAME §20.3.1 co-covering pair v2.38 already amended
for the sibling audit-walk arc — U-CP-45 (the `verify_rotation_6_steps`
extension: real presence/uniqueness + OD-anchored evidence checks on 2 of the
6 rotation steps) and U-CP-44 (the physical-key-distinctness comparator).
Zero new units. Explicit scope fence preserved: no real production caller of
`verify_rotation_6_steps` is wired at this leg.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
