---
artifact: design-substrate/Spec_Operational_Discipline_v1_35.md
version: v1.35
cleared_at: 2026-07-23T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_b33_rotation_correlation_carrier.md (RATIFIED 2026-07-21 — Option A)
merge_commit: pending (pre-merge at filing time; B-33-A spec+plan leg PR)
reviewer_chain:
  - operator ratification (2026-07-21) — Option A, fork §2 item 4 injected-evidence-DTO shape
  - out-of-family codex review to convergence on the landing PR (recorded at the PR thread)
---

# Clearance — Spec_Operational_Discipline_v1_35 (B-33 arc, spec leg)

v1.34→v1.35: NEW §24.8 (C-OD-24) — a per-correlation-id rotation-pair evidence
accessor (`find_rotation_pair_evidence`) sitting alongside the existing §24.7
whole-ledger `verify_rotation_pairs` walk, reusing its crypto/structural checks
via an extracted shared helper. §24.7 itself is unchanged. Absence of a
matching pair (EXACTLY 0 entries — out-of-family review round-2 [P2]
correction: a LONE matching entry is NOT absence, see next) is explicitly
distinguished from a `RotationPairIntegrityBreach` (3+ entries, 2 entries
failing the crypto checks, OR exactly 1 matching entry — a torn write/deleted
sibling, structural corruption rather than benign absence) — absence is
reported as evidence, not raised as tamper. `RotationPairEvidence` also
carries a `signatures_verified: bool` field, always `False` in this delta (no
rotation-period-aware cryptographic verifier exists yet — round-2 [P1]):
structural evidence is necessary but not sufficient for a genuine rotation
pass. Plan delta `Implementation_Plan_Operational_Discipline_v2_30.md` (NEW
U-OD-56) carries the acceptance criteria, including a retroactive backfill of
§24.7's own coverage (previously uncovered by any canonical `U-OD-NN` unit).

CP-owned and Runtime-owned contract text for this same arc live at the
sibling `Spec_Control_Plane_v1_105.md` and the Runtime v1.104→v1.105 rider —
cross-referenced, not restated here.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
