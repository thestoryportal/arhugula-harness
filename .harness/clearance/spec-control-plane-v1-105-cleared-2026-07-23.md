---
artifact: design-substrate/Spec_Control_Plane_v1_105.md
version: v1.105
cleared_at: 2026-07-23T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_b33_rotation_correlation_carrier.md (RATIFIED 2026-07-21 — Option A)
merge_commit: pending (pre-merge at filing time; B-33-A spec+plan leg PR)
reviewer_chain:
  - operator ratification (2026-07-21) — Option A, fork §2 item 4 injected-verifier/typed-evidence-DTO shape
  - out-of-family codex review to convergence on the landing PR (recorded at the PR thread)
---

# Clearance — Spec_Control_Plane_v1_105 (B-33 arc, spec leg)

v1.104→v1.105: AMENDED §20.3.1 (C-CP-20) row 7 — retires the "remains B-33's
scope" deferral carried since `Spec_Control_Plane_v1_98.md` by actually
extending `verify_rotation_6_steps`: `WRITE_DUAL_VERIFY_ENTRY` gains a real
IS-owned presence/uniqueness check (`harness_is.rotation_window_verification.
verify_rotation_window`), and `PROBE_VERIFY_AT_READ` gains a real OD-anchored
evidence check via an injected `RotationPairEvidenceProvider`. NEW §20.3.2
declares that Protocol + its typed `RotationPairEvidence` DTO + two exception
types (`RotationPairIntegrityBreach`, `RotationPairEvidenceUnavailableError`)
+ an optional physical-key-distinctness boundary attestation against a
signing backend's key-identity mapping. Deliberately NOT byte-compatible for
absent-parameter callers (justified: zero production callers exist today).
Plan delta `Implementation_Plan_Control_Plane_v2_41.md` (U-CP-44 + U-CP-45
amendment) carries the acceptance criteria.

OD-owned and Runtime-owned contract text for this same arc live at the
sibling `Spec_Operational_Discipline_v1_35.md` and the Runtime v1.104→v1.105
rider — cross-referenced, not restated here. Per the fork's explicit scope
fence, this delta does NOT build a real production caller of
`verify_rotation_6_steps`/`execute_key_rotation` — that remains a later arc.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
