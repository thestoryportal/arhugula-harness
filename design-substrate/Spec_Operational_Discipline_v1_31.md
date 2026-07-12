# `Spec_Operational_Discipline` v1.31 — delta over v1.30

**Filed:** 2026-07-12
**Authoring authority:** Phase 7 — R-FS-2 Wave 1 standalone `B-*` arc **B-AUDIT-KEY-ROTATION-RUNTIME** (`.harness/r-fs-2-final-closure-implementation-plan-v1.md` §2)
**Predecessor:** `Spec_Operational_Discipline_v1_30.md` (v1.30 — C-OD-15 §15.1 `PER_DISPATCH_KIND` rollup axis)
**Revision shape:** Delta-only spec file per workspace `CLAUDE.md` §2.3 OD spec row convention. v1.30 + v1.29 + ... + v1 file bodies PRESERVED VERBATIM. v1.31 carries this change-note + the C-OD-24 §24.1/§24.6-pattern ADDITIVE amendment only.

---

## Change-note (v1.30 → v1.31)

**Closes a Class-3-flagged reconciliation gap admitted at `ADR-D5.md` v1.4's own Change-note (v1.3 → v1.4).** That change-note's "§1.4 sqlite schema extension table carry-forward" paragraph reclassified the ADR's 4-column SQLite rotation schema (`signature_value` / `signature_key_id` / `signature_key_period` / `rotation_correlation_id`) as a **non-canonical, deferred C11-style persistence model** at v1.4 (JSONL via IS composition is v1.4-canonical — ADR-D5 §1.4 row table). It asserted "the equivalent column data lives as Pydantic fields on `AuditSignatureAttributes`" — true for the first three columns (`audit_signature_value` / `audit_signature_key_id` / `audit_signature_key_period`, all already declared at OD spec v1.5 C-OD-24.2), but **not** true for the fourth: `rotation_correlation_id` has no field on `AuditSignatureAttributes`, `AuditPayload`, or `AuditLedgerEntry` at any spec version through v1.30. The ADR change-note itself flagged this as unresolved ("future C11-style D-ADR authoring will need to either reconcile the table with v1.4 JSONL-canonical, OR commit the SQLite migration explicitly"). v1.31 performs that reconciliation now, at Phase 7 (R-FS-2 Wave 1 `B-AUDIT-KEY-ROTATION-RUNTIME`), under the JSONL-canonical branch of that fork — no SQLite migration, no new ADR.

**Why the JSONL-canonical branch, not a SQLite migration.** ADR-D5 v1.4 already committed JSONL-via-IS-composition as canonical storage at all three persona tiers (§1.4 row table); no operator or design-phase signal has proposed reopening that commitment. Porting the one still-unhomed column into the existing JSONL shape completes the v1.4 storage-form reconciliation the ADR itself called for, without touching the settled storage-form decision.

**Why `audit_namespace_attrs` (the existing open dict), not a new typed field on `AuditLedgerEntry`.** Two live options were weighed:

1. A new top-level `AuditLedgerEntry.rotation_correlation_id: str | None` field — a schema-shape change that breaks the acceptance-pinned field-count test (`test_audit_ledger_entry_three_fields`) and requires re-litigating `AuditLedgerEntry`'s closed shape.
2. A new named attribute inside `AuditPayload.audit_namespace_attrs: dict[str, str]` — the extensibility mechanism the shape **already provides** for exactly this kind of namespace growth. §24.6 (v1.5) established the precedent: the `audit.cp.*` sub-namespace was added to accommodate CP-sourced fields via this same open dict, with zero change to `AuditPayload`'s or `AuditLedgerEntry`'s declared field set.

Option 2 is adopted. `audit.rotation_correlation_id` joins the namespace as an eighth declared `audit.*` attribute name (alongside the seven at ADR-D5 §1.4.1), carried inside `audit_namespace_attrs` exactly like the existing seven. This is lower blast-radius (no Pydantic schema change; `test_audit_ledger_entry_three_fields` / `test_audit_payload_three_fields` remain valid unmodified), and it is automatically hash-covered: `audit_namespace_attrs` is a field of `AuditPayload`, and `entry_hash = compute_entry_hash(payload)` (§24.5) hashes the full payload — so a tampered `audit.rotation_correlation_id` value changes `entry_hash` exactly like tampering with any other `audit.*` attribute, giving "tamper either sibling → verify fails" for free at the same abstraction level the existing hash-chain / signature-placeholder discipline already operates at (no new cryptographic primitive introduced).

**No ADR revision.** ADR-D5 v1.4's rotation-mechanism prose (§1.4 "Key-period model for rotation" + the "External-auditor verification semantics for the two-row rotation pattern" paragraph) is unchanged and remains canonical verbatim — only the *storage-form carrier* for `rotation_correlation_id` needed resolution, and that resolution is OD-spec-level (C-OD-24 is where the JSONL-canonical shape and its extensibility convention are declared), not ADR-level. No operator gate: additive namespace-attribute registration following an established precedent, closing a self-flagged non-blocking gap (`[[feedback-gate-only-on-meaningful-architecture-change]]`).

**No committed invariant sacrificed.** `AuditPayload` / `AuditLedgerEntry` / `AuditLedger` field sets are unchanged (§24.1–§24.3 preserved verbatim). `AuditSignatureAttributes` (§24.2's 4-attribute set) is unchanged — `rotation_correlation_id` is deliberately **not** added there; it is not a signature attribute, it is a cross-entry structural correlation key, and its natural home is the payload's open namespace dict, not the closed signature-attribute record.

---

## §24.7 `audit.rotation_correlation_id` namespace attribute (NEW v1.31, ADDITIVE)

Extends the C-OD-24.1 `AuditPayload.audit_namespace_attrs` convention (preserved verbatim) with an eighth declared `audit.*` attribute name, materializing ADR-D5 §1.4's F2-iter2-03 Option (a) two-row rotation pattern inside the v1.4 JSONL-canonical shape.

**Declaration.**

| Attribute | Type | Population |
|---|---|---|
| `audit.rotation_correlation_id` | UUID string (36-char canonical form), or key absent | Absent from `audit_namespace_attrs` for all non-rotation ledger entries (the dominant case — byte-identical to every pre-v1.31 entry). Present with a shared UUID value on exactly two `AuditLedgerEntry` instances — the rotation-pair siblings — when a `secret_rotation_event` materializes and the rotating secret IS the audit-signing key (ADR-D5 §1.4 "Key-period model for rotation" discriminator `audit.signing_key_rotation: bool = true`). Sibling-1 carries `audit_signature_key_period` at the outgoing period `N`; sibling-2 carries the incoming period `N+1`. |

**Solo-tier no-op.** `solo-developer` (ADR-D5 §1.4 row 1) has no signing key and no rotation event; `audit.rotation_correlation_id` is never populated at that tier — consistent with the ADR's "all four columns NULL" solo-tier population rule, now expressed as "key absent" under the dict carrier (an absent dict key is the JSONL-canonical equivalent of a NULL column — no column exists to be non-NULL in the first place).

**Hash coverage (tamper-evidence).** `audit.rotation_correlation_id` lives inside `AuditPayload.audit_namespace_attrs`, which `compute_entry_hash` (§24.5) hashes as part of the full payload. A value tampered on either sibling changes that sibling's `entry_hash`, which in turn breaks `AuditLedgerEntry.entry_hash` and the hash-chain link the *next* entry in ledger order depends on (`prior_entry_hash`) — the same tamper-detection path every other `audit.*` attribute already relies on. No new cryptographic primitive is introduced.

**External-auditor verification (materializes ADR-D5 §1.4's "External-auditor verification semantics for the two-row rotation pattern" at the OD-axis code surface).** A ledger-level verification pass, given an `AuditLedger`:

1. Partition `ledger.entries` into rotation-tagged (non-empty `audit.rotation_correlation_id`) and non-rotation.
2. For each distinct `audit.rotation_correlation_id` value, require **exactly two** entries carrying it (a lone rotation-tagged entry — a missing sibling — is a verification failure; more than two is a verification failure — the pattern is a two-row pattern, not N-row).
3. **Recompute, don't trust stored hashes** — per the ADR's "recomputing hashes" instruction: for each of the two tagged entries, require `entry.entry_hash == compute_entry_hash(entry.payload)` (§24.5). A payload mutated in place with a stale `entry_hash` left behind is a verification failure at this step, independent of any cross-entry check below.
4. Order the pair by `audit_signature_key_period`; require the periods to be consecutive integers (`period(sibling_2) == period(sibling_1) + 1`) and the `audit_signature_key_id` values to differ (outgoing key ≠ incoming key — a rotation changes the key identity, not just the period counter).
5. Require chain-hash continuity across the pair per the ADR's ordering rule: `sibling_2.payload.prior_entry_hash == sibling_1.entry_hash` (sibling-2 is the rotation-anchor entry under the new key-period; this is the same `prior_entry_hash`/`entry_hash` link the standing hash-chain walk already verifies for every consecutive entry — the rotation check adds the sibling-pairing and key-period discipline on top, not a separate hash algorithm).
6. Non-rotation entries (`audit.rotation_correlation_id` absent) are verified one-at-a-time, unchanged from the v1.5 baseline — the addition is purely additive over entries that opt in to the namespace attribute.

**PRD requirement(s) satisfied.** R-OD-04 (audit-ledger schema — payload composition surface; extended to cover the rotation-pair correlation dimension) + R-OD-08 (bridging-arc traversal preservation — closes the multi-tenant-compliance-tier rotation-forensics gap ADR-D5 §1.4 commits and ADR-D5 v1.4 left unreconciled).

**ADR commitment(s) honored.** ADR-D5 v1.4 §1.4 "Key-period model for rotation" + "External-auditor verification semantics for the two-row rotation pattern" (both preserved verbatim, unchanged by this delta) + the v1.4 Change-note's Class-3-flagged reconciliation instruction (satisfied by this delta, JSONL-canonical branch).

**Cross-reference.** OD spec v1.5 §24.6 (`audit.cp.*` sub-namespace) is the direct precedent for extending `audit_namespace_attrs` with a new declared name without a schema-shape change; §24.7 follows the identical pattern for a rotation-scoped (rather than CP-source-scoped) attribute.

**Scope discipline.** v1.31 amends ONLY the C-OD-24 namespace-attribute declaration (adds §24.7) — §24.1 through §24.6 are PRESERVED VERBATIM (no field added or removed from any of `AuditPayload` / `AuditLedgerEntry` / `AuditLedger` / `AuditSignatureAttributes` / `StateLedgerEntryRef`). All other C-OD-01..C-OD-34 contract surfaces are PRESERVED VERBATIM. v1.30 + earlier lineage PRESERVED VERBATIM per the delta-only-spec-file convention except the §24.7 additive amendment above.
