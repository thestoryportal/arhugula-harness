---
artifact: design-substrate/Spec_Operational_Discipline_v1_33.md
version: v1.33
cleared_at: 2026-07-16T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-forward-register-arc (B-47 grounding, bundled-absorption per CLAUDE.md §11.4)
back_reference:
  - .harness/post-phase-8-forward-register.md (B-47 entry — AwsKmsSigningBackend has no production composition-root call site)
  - design-substrate/ADR-D8_audit_signing_backend.md (§Decision item 5 — the composition-root wiring named as a separate deployment-time arc; §Consequences — "can be composition-root-wired into sign_audit_entry")
  - design-substrate/ADR-D5.md (§1.4.1 — "live signing backend ... wired at a deployment-time composition root"; v1.5 §1.4 row 3 B-36 cross-reference)
  - design-substrate/Spec_Control_Plane_v1_98.md (§20.2.1 — the SigningBackend Protocol + the B-22 cleared seam precedent this delta mirrors)
  - design-substrate/Spec_Operational_Discipline_v1_2.md (§21.2 C-OD-21 last-substantive-definition — the committed cryptographic-signature contract this seam makes reachable)
merge_commit: pending (pre-merge at filing time; B-47 PR A)
reviewer_chain:
  - empirical grounding sweep (Explore subagent, 2026-07-16) — traced the REAL production audit-signing path to harness_od.multi_tenant_trace_separation_and_audit_ledger.sign_audit_entry (hash-only placeholder "unsigned:{key_id}:{prior_entry_hash}") invoked via harness_cxa.cp_audit_conversion.cp_audit_to_od_audit at every runtime audit write; confirmed the CP-side B-22 seam has zero production callers, so the OD-side mirror is the only path by which §21.2's committed signature reaches persisted entries
  - precedent alignment — the seam shape (optional backend keyword, absent-path preserved verbatim, canonical message binding, per-algorithm length enforcement, base64 value representation) is a byte-faithful mirror of two already-cleared decisions: C-CP-20 §20.2.1 (B-22, operator chose build-the-seam-now 2026-07-14) and the B-34 representation enforcement (PR #1032, merge-gate 3-lens all-APPROVE)
  - out-of-family `just codex-review` to convergence + merge-gate 3-lens review at the landing PR (recorded at .harness/merge-gate-log.md)
notes: |
  Purely additive delta — §21.2's table/prose preserved verbatim; the 4-attribute
  AuditSignatureAttributes carrier is shape-unchanged. The delta commits the seam
  only; backend selection/construction/config (RuntimeConfig surface, bootstrap
  factory, C9 breaker on the signing call) remain B-47's registered remainder.
  Rotation-aware key-period selection remains B-33.
---

# Clearance — `Spec_Operational_Discipline_v1_33.md` (v1.33)

v1.33 adds C-OD-21 §21.2.1: the OPTIONAL `SigningBackend` composition-root
injection seam on the U-OD-30 `sign_audit_entry` surface — the OD-side mirror
of the cleared C-CP-20 §20.2.1 (B-22) seam. Grounding for B-47 found the
production audit-signing path runs through this OD function (placeholder
signatures today), not the CP-side function the B-22 seam landed on; without
this seam the §20.1/§21.2 MULTI_TENANT_COMPLIANCE cryptographic-signature
commitment is structurally unreachable from any composition root. Absent
backend → placeholder attributes preserved byte-for-byte (zero regression,
purely additive). Present backend → real signature over a metadata-bound
canonical message, base64 value, per-algorithm length enforcement (B-34
discipline applied at birth). Landing PR carries the implementation, the CXA
converter passthrough, and mutation-probed witnesses.
