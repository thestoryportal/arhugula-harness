---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.105
cleared_at: 2026-07-23T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_b33_rotation_correlation_carrier.md (RATIFIED 2026-07-21 — Option A)
merge_commit: pending (pre-merge at filing time; B-33-A spec+plan leg PR)
reviewer_chain:
  - operator ratification (2026-07-21) — Option A
  - out-of-family codex review to convergence on the landing PR (recorded at the PR thread)
---

# Clearance — Spec_Harness_Runtime_v1 v1.105 (B-33 arc, spec leg)

v1.104→v1.105: NEW §13.6 — rotation-pair-evidence composition-root inputs,
mirroring §13.5's shape for a SECOND, independent injected verifier (the
CP-owned `RotationPairEvidenceProvider`, not `AuditWalkVerifier`). Declares
the one new operator-facing input (a signing-key identity mapping for the
CP-owned physical-key-distinctness attestation) and the wiring-site
declaration (the same composition-root surface §13.5 names, extended to
construct and inject a second, independently-configured adapter). Plan delta
`Implementation_Plan_Harness_Runtime_v2_53.md` (NEW U-RT-147) carries the
acceptance criteria.

CP-owned and OD-owned contract text for this same arc live at the sibling
`Spec_Control_Plane_v1_105.md` and `Spec_Operational_Discipline_v1_35.md` —
cross-referenced, not restated here.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
