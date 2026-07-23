---
artifact: design-substrate/Implementation_Plan_Information_Substrate_v2_8.md
version: v2.8
cleared_at: 2026-07-22T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-Class-1-fork-ratification (B-33-A spec leg; implementation-planner absorption pass per CLAUDE.md §4.3 + §4.5)
back_reference:
  - .harness/class_1_fork_b33_rotation_correlation_carrier.md (RATIFIED 2026-07-21 — option A AS RECOMMENDED)
  - design-substrate/Spec_Information_Substrate_v1.md v1.12 (same-arc spec leg)
merge_commit: pending (pre-merge at filing time; B-33-A spec-leg apply PR)
reviewer_chain:
  - operator ratification (2026-07-21) — option A as recommended
  - out-of-family codex review owed pre-merge (spec leg)
---

# Clearance — Implementation_Plan_Information_Substrate v2.8 (B-33-A spec leg)

v2.7→v2.8: decomposes IS spec v1.12 §5.6 + §7.7 into ONE NEW foundational atomic unit, U-IS-20 — the `rotation_correlation_id` sidecar carrier + its canonicalization contribution + the presence/uniqueness read-side invariants, following the exact U-IS-19 (`branch_metadata`) decomposition template. `Depends on: (none)`; ZERO outbound cross-axis edge (IS 0-outbound preserved). SPEC-LEG ONLY: the unit's own AC #6 is an explicit non-goal fence against implementing `verify_rotation_6_steps`'s extension, the OD-join, or the B-36 backend boundary attestation — all CP-owned, decomposed at a separate, not-yet-opened impl leg. +2 coverage-matrix rows (C-IS-05 §5.6, C-IS-07 §7.7); no new auxiliary type (bare scalar field, unlike U-IS-19's `BranchMetadata`).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- The CP-axis impl leg (carrier population at `execute_key_rotation` + the verifier extension) is a separate, not-yet-opened arc; its CP plan delta will declare the cross-axis inbound edge into U-IS-20.
- See `.harness/clearance/README.md` for marker discipline.
