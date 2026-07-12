---
artifact: design-substrate/Spec_Operational_Discipline_v1_31.md
version: v1.31
cleared_at: 2026-07-12T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/r-fs-2-final-closure-implementation-plan-v1.md (§2 B-AUDIT-KEY-ROTATION-RUNTIME)
  - design-substrate/ADR-D5.md v1.4 Change-note (v1.3 → v1.4) — "§1.4 sqlite schema extension table carry-forward" Class-3 flag (self-admitted reconciliation gap this delta closes)
merge_commit: pending (R-FS-2 B-AUDIT-KEY-ROTATION-RUNTIME bundled-absorption PR)
reviewer_chain:
  - advisor (full-transcript) — flagged that the change-note-only read was insufficient and directed grounding against the ADR-D5 §1.4/§1.4.1 body text before any spec delta was authored; confirmed the body text (not just the change-note) as the correct tie-breaker on canonical-vs-deferred and on carrier placement
  - impl-time grounding pass — read ADR-D5.md §1.4 body (lines 177-244) directly, confirmed the SQLite table (not the rotation PROSE) was the only thing demoted to deferred status at v1.4, and confirmed the 7 declared audit.* attributes at §1.4.1 do not include a rotation-correlation attribute
supersedes:
superseded_by:
---

# Clearance — `Spec_Operational_Discipline v1.31`

v1.31 closes a reconciliation gap that ADR-D5 v1.4's own Change-note admitted was left open: the v1.3-committed two-row rotation pattern (`rotation_correlation_id`, F2-iter2-03 Option (a)) was authored only into the SQLite schema table, and that table was explicitly demoted to a non-canonical, deferred persistence model at v1.4 (JSONL via IS composition is v1.4-canonical) — with no corresponding field ported into the JSONL-canonical shape. The ADR's own rotation-mechanism PROSE (key-period model + external-auditor verification semantics) was **not** demoted — it remains canonical verbatim — only its structural carrier (`rotation_correlation_id`) had nowhere to live. v1.31 adds **§24.7**: an eighth declared `audit.*` namespace attribute, `audit.rotation_correlation_id`, carried inside the existing open `AuditPayload.audit_namespace_attrs` dict (C-OD-24.1) — the same extensibility mechanism §24.6 already established for the `audit.cp.*` sub-namespace. No field is added to `AuditPayload`, `AuditLedgerEntry`, `AuditLedger`, or `AuditSignatureAttributes` — all four Pydantic shapes are preserved byte-exact, so the acceptance-pinned field-count tests are untouched.

**No operator gate — additive namespace-attribute registration following an established precedent (§24.6), closing a self-flagged non-blocking gap.** No nameable cross-domain tension; single-voice grounding + advisor, not council (`[[feedback-gate-only-on-meaningful-architecture-change]]`). No ADR revision — the ADR's rotation prose is unchanged; only the OD-spec-level storage-form carrier decision needed resolution, and C-OD-24 is where that decision already lives (per §24.6 precedent).

**Phase 7 consumers.** The companion code lands in the same PR: `harness_od.multi_tenant_trace_separation_and_audit_ledger` gains a rotation-pair writer (producing the co-signed sibling pair sharing `audit.rotation_correlation_id`) and an extended verification pass implementing the §24.7 5-step external-auditor walk. `AuditSignatureAttributes`'s 4-attribute set is unchanged — `rotation_correlation_id` is deliberately not a signature attribute. Solo-tier is a structural no-op (the key is never populated, not merely NULL).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
