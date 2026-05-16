# Implementation Plan — Operational Discipline (OD axis) — v2.7

**Status: Proposed.**

**Revision:** v2.7 — Phase 7 sub-phase 7b in-CLI micro-revision. Resolves three **Class 1 defects** in the v2.6 §3.0 U-OD-00 unit body, surfaced at U-OD-00 execution-time. v2.7 is a delta over v2.6: **only §3.0 U-OD-00 and the §3.7.4 U-OD-30 `SignatureAlgorithm` note are revised**; every other §0–§11 section is preserved verbatim from v2.6. Predecessor: v2.6 (R5 materializability conformance).

**Authority chain:** `Project_Workflow_v1_8.md` §7.4 fidelity-grammar; `CLAUDE.md` §4.3 back-flow routing (Class 1 fork resolution); `harness-od/CLAUDE.md` §5.1 (OD plan atomic-unit signature defect → Phase 6 plan revision); `implementation-planner` SKILL.md §8 revision-pass sub-mode.

**Entry authorization:** Operator ratification 2026-05-15 of the U-OD-00 v2.7 micro-revision (`.harness/class_1_tension_u_od_00_carrier_defects.md`).

---

## §0 Change-note

### §0.1 Trigger

At U-OD-00 execution-time (Phase 7 7b), the v2.6 §3.0 U-OD-00 unit body — the new OD audit-ledger composition-type carrier — was found to carry three Class 1 defects. U-OD-00 cannot be landed as written at v2.6.

### §0.2 The three defects + resolution

| # | Defect | Resolution (operator-ratified 2026-05-15) |
|---|---|---|
| D-1 | `AuditSignatureAttributes.audit_signature_algorithm : SignatureAlgorithm` requires `SignatureAlgorithm`, which v2.6 leaves declared at **U-OD-30** (v2.5-preserved). But Q-R5-3 moved `AuditSignatureAttributes` to U-OD-00, and U-OD-30 already depends on U-OD-00 (`[U-OD-00]` edge). U-OD-00 importing `SignatureAlgorithm` back from U-OD-30 is a **dependency cycle**. | **`SignatureAlgorithm` moves to U-OD-00**, co-located with `AuditSignatureAttributes` (the record that consumes it). U-OD-30 imports it via its existing `[U-OD-00]` edge. The cycle is dissolved. |
| D-2 | `AuditLedger.cell_id : CellID` requires `CellID`, declared in-unit at **U-OD-01**. v2.6 declares U-OD-00 `Depends on: (none)` and Q-R5-5 ratifies U-OD-00 as a strict L0 anchor. The v2.6 §4.6 dependency table's `CellID`-consumer row omits U-OD-00. | **U-OD-00 takes a `[U-OD-01]` edge** for `CellID`. U-OD-00 is **L1**, not L0 — Q-R5-5's narrative is amended (§0.3). Acyclic: U-OD-01 depends only on `[U-CORE-01]`; U-OD-01 does not reach U-OD-00. |
| D-3 | The v2.6 §3.0 signature block declares `AuditSignatureAttributes` with fields `{algo, key_id, signature_value, signed_at_unix_ns}` — diverging from the v2.5-canonical record Q-R5-3 claims to *move* (`{audit_signature_value, audit_signature_algorithm, audit_signature_key_id, audit_signature_key_period}` — the 4-attribute `audit.signature.*` set per OD spec §21.2 / ADR-D5 v1.3 §1.4.1). The v2.6 rewrite introduced `signed_at_unix_ns` (**not** in the `audit.signature.*` namespace — an un-spec'd field, X-AL-3) and dropped `audit_signature_key_period`. | **`AuditSignatureAttributes` is corrected to the v2.5-canonical 4-attribute `audit.signature.*` set** (`audit_signature_value`, `audit_signature_algorithm`, `audit_signature_key_id`, `audit_signature_key_period`). A "move" per Q-R5-3 is a verbatim relocation, not a redesign; `signed_at_unix_ns` is struck. This is the determinate fix — OD spec §21.2 + ADR-D5 §1.4.1 dictate the 4-attribute set; no operator choice. |

### §0.3 Q-R5-5 amendment (D-2 consequence)

v2.6 Q-R5-5 ratified the OD-axis-internal L0 set as `{U-OD-00, U-OD-01, U-OD-04}`. **v2.7 amends this:** the L0 set is `{U-OD-01, U-OD-04}`; **U-OD-00 is L1** (`Depends on: [U-OD-01]`). Q-R5-5 was ratified on the incorrect premise that U-OD-00 declared all its composition types in-unit; in fact `AuditLedger.cell_id` composes U-OD-01's `CellID`. The premise is corrected, not the design. U-OD-00 remains the OD audit-ledger-type carrier and a near-root anchor — its only OD-internal dependency is U-OD-01.

### §0.4 Scope

Only §3.0 (U-OD-00) and the §3.7.4 U-OD-30 `SignatureAlgorithm` note are revised. No contract re-decomposed; no value set changed; unit count unchanged (35). The `harness-od/CLAUDE.md` §3 L0-set / unit-count follow-up already owed from v2.6 §0.9 is **extended** by the Q-R5-5 amendment (L0 set drops U-OD-00) — recorded as the same operator-applied follow-up, not performed here (HARD WALL).

### §0.5 Sections preserved verbatim from v2.6

All of §0 (v2.6 change-note), §1, §2, §3 except §3.0, §4 except the §4.6 edge delta below, §5–§11. The 16 v2.6-revised units (U-OD-01, U-OD-04, U-OD-09, …, U-OD-34) and U-OD-00's surrounding cluster structure are unchanged except as enumerated above.

---

## §3.0 U-OD-00 — Declare the OD-local audit-ledger composition types (`AuditPayload`, `AuditLedger`, `SignatureAlgorithm`) [REVISED — v2.7]

[v2.6-introduced unit. v2.7 delta: D-1 — `SignatureAlgorithm` enum **added** to U-OD-00 (moved from U-OD-30); D-2 — `Depends on` changed `(none)` → `[U-OD-01]` for `CellID`, U-OD-00 re-leveled L0 → L1; D-3 — `AuditSignatureAttributes` field set corrected to the v2.5-canonical 4-attribute `audit.signature.*` set. All other v2.6 §3.0 surfaces — `AuditPayload`, `AuditLedgerEntry`, `AuditLedger`, `StateLedgerEntryRef`, the spec-traceability note, the OD-local/not-IS-exported note — preserved verbatim from v2.6 §3.0.]

**Implements:** [C-OD-14 §14.5] (audit-ledger schema + 8-field SHA-256 composition surface); [ADR-D5 v1.3 §1.4] + [ADR-D5 v1.3 §1.4.1] (audit-ledger cryptographic shape — the `audit.*` / `audit.signature.*` namespaces); [C-OD-21 §21.2] (the 3-value `audit.signature.algorithm` set — `SignatureAlgorithm`, added at v2.7 per D-1). *(v2.7: C-OD-21 §21.2 citation added — `SignatureAlgorithm` traces to it.)*

> **Spec-traceability note.** `AuditPayload`, `AuditLedger`, `SignatureAlgorithm` are FACTOR-OUTs (T2 verdict, decided): the OD spec C-OD-14 §14.5 audit-ledger schema + ADR-D5 §1.4 cryptographic shape + C-OD-21 §21.2 signature-algorithm set commit the audit-ledger *concept* and its field composition. The record shapes are a faithful operationalization — not a spec extension. `SignatureAlgorithm`'s 3-value set is byte-exact with the v2.5-conformed U-OD-30 declaration (`ed25519 | ecdsa-p256 | rsa-pss-2048` per §21.2 / ADR-D5 §1.4.1).

> **OD-local, NOT IS-exported (Q4-verified).** `AuditPayload`/`AuditLedger` are OD-axis-owned. The IS axis exports `StateLedgerEntry` (C-IS-10 §10.1) + the hash-chain discipline (C-IS-13 §13.5); there is no `AuditLedger`/`AuditPayload` record in any IS unit. The OD audit ledger *composes against* the IS export. No cross-axis edge is required for `AuditPayload`/`AuditLedger`; they are within-OD-axis types.

**Depends on:** [U-OD-01] — **v2.7: changed from `(none)` to `[U-OD-01]`** (D-2). `AuditLedger.cell_id : CellID` consumes `CellID`, declared in-unit at U-OD-01. The edge is a within-axis OD edge. Acyclic — U-OD-01 `Depends on: [U-CORE-01]` only; U-OD-01 does not reach U-OD-00. U-OD-00 is **L1** (re-leveled from L0; Q-R5-5 amended at §0.3).

**Inputs:** OD spec v1.2 §14.5 audit-ledger 8-field SHA-256 composition + field-ordering; ADR-D5 v1.3 §1.4 / §1.4.1 audit-ledger cryptographic shape (`audit.signature.*` 4-attribute set); OD spec §21.2 (`SignatureAlgorithm` 3-value set); `CellID` from U-OD-01.

**Files affected:** OD-local audit-ledger composition type declaration (logical name: `od-audit-ledger-composition-types`).

**Persona linkage.** Persona §10.4 (compliance-readiness — tamper-evident audit ledger at multi-tenant cells).

**Signatures:**

```
// SignatureAlgorithm — the 3-value audit.signature.algorithm set (v2.7 — moved
// from U-OD-30 per D-1; byte-exact with the v2.5-conformed U-OD-30 declaration).
// §21.2 verbatim — audit.signature.algorithm ∈ {ed25519, ecdsa-p256, rsa-pss-2048}
// (Ed25519 default; operator-tunable audit_signature_algorithm axis).
enum SignatureAlgorithm {
  ED25519,                                            // "ed25519"
  ECDSA_P256,                                         // "ecdsa-p256"
  RSA_PSS_2048                                        // "rsa-pss-2048"
}

// AuditPayload — the signable core of one audit-ledger entry. Composes against
// the IS-exported StateLedgerEntry shape (C-IS-10 §10.1) and adds the audit.*
// namespace per ADR-D5 v1.3 §1.4.
record AuditPayload {
  entry_core            : StateLedgerEntryRef   // F2 6-field entry shape, IS-exported (C-IS-10 §10.1)
  audit_namespace_attrs : Map<string, string>   // audit.* attributes per C-OD-14 §14.5
  prior_entry_hash      : string                // SHA-256 hash-chain link per C-IS-13 §13.5 discipline
}

// AuditSignatureAttributes — the 4-attribute audit.signature.* set per ADR-D5
// v1.3 §1.4.1 / OD spec §21.2. MOVED to U-OD-00 from U-OD-30 per Q-R5-3.
// v2.7 (D-3): field set corrected to the v2.5-canonical audit.signature.* set —
// a Q-R5-3 "move" is a verbatim relocation, not a redesign.
record AuditSignatureAttributes {
  audit_signature_value      : string               // audit.signature.value
  audit_signature_algorithm  : SignatureAlgorithm    // audit.signature.algorithm
  audit_signature_key_id     : string               // audit.signature.key_id
  audit_signature_key_period : string               // audit.signature.key_period
}

// AuditLedgerEntry — one signed, hash-chained audit entry.
record AuditLedgerEntry {
  payload               : AuditPayload
  signature_attrs       : AuditSignatureAttributes   // 4-attribute audit.signature.* set
  entry_hash            : string                     // SHA-256 over payload, per C-OD-14 §14.5 field-ordering
}

// AuditLedger — an ordered, hash-chained sequence of signed audit entries.
// verify_hash_chain_integrity (U-OD-30) walks this sequence.
record AuditLedger {
  entries               : List<AuditLedgerEntry>     // ordered; entries[i].payload.prior_entry_hash == entries[i-1].entry_hash
  cell_id               : CellID                     // U-OD-01 — ∈ {cell-7, cell-8} multi-tenant cells only
}

// StateLedgerEntryRef — a thin opaque reference to the IS-exported F2 entry
// shape. The concrete IS StateLedgerEntry resolves at the U-OD-30 cross-axis IS
// edge (C-IS-10 §10.1); this carrier names the position.
opaque StateLedgerEntryRef : Reference
```

**Acceptance criteria:**

1. `AuditPayload` declares exactly three fields — `entry_core` (`StateLedgerEntryRef`), `audit_namespace_attrs` (the `audit.*` namespace map per C-OD-14 §14.5), `prior_entry_hash` (SHA-256 hash-chain link per the C-IS-13 §13.5 discipline).
2. `AuditLedgerEntry` declares exactly three fields — `payload : AuditPayload`, `signature_attrs : AuditSignatureAttributes`, `entry_hash` (SHA-256 over `payload` per the C-OD-14 §14.5 field-ordering).
3. `AuditLedger` declares exactly two fields — `entries : List<AuditLedgerEntry>` and `cell_id : CellID`; the ledger is well-formed iff `entries[i].payload.prior_entry_hash == entries[i-1].entry_hash` for all `i > 0`. (Verification is U-OD-30's `verify_hash_chain_integrity`; U-OD-00 declares the shape and documents the invariant.)
4. `AuditPayload` / `AuditLedger` / `AuditLedgerEntry` / `AuditSignatureAttributes` / `SignatureAlgorithm` are OD-axis-local types — they reside in the OD-axis package, NOT in `harness-core` and NOT imported from the IS axis. The IS composition surface is the `StateLedgerEntryRef` opaque marker.
5. No spec extension: every field is a faithful operationalization of C-OD-14 §14.5 + ADR-D5 v1.3 §1.4 / §1.4.1 + C-OD-21 §21.2. **(v2.7 D-3:** `AuditSignatureAttributes` carries exactly the 4-attribute `audit.signature.*` set — no `signed_at_unix_ns` or other un-committed field.**)**
6. `AuditSignatureAttributes` (4-attribute `audit.signature.*` record per ADR-D5 v1.3 §1.4.1) is declared in U-OD-00 — moved from U-OD-30 per Q-R5-3. U-OD-30 consumes it via the `[U-OD-00]` edge.
7. **(v2.7 D-1.)** `SignatureAlgorithm` declares exactly three values — `ED25519`, `ECDSA_P256`, `RSA_PSS_2048` (string values `ed25519 | ecdsa-p256 | rsa-pss-2048`, byte-exact with OD spec §21.2 / ADR-D5 v1.3 §1.4.1 and the v2.5-conformed U-OD-30 declaration). Declared in U-OD-00; U-OD-30 imports it via the `[U-OD-00]` edge. Closed at cardinality 3.
8. **(v2.7 D-2.)** U-OD-00 declares `Depends on: [U-OD-01]`; `AuditLedger.cell_id` resolves to U-OD-01's `CellID`. U-OD-00 is an L1 unit.

**Tests:** `test_audit_payload_three_fields`, `test_audit_ledger_entry_three_fields`, `test_audit_ledger_two_fields`, `test_audit_ledger_hash_chain_link_invariant`, `test_audit_types_od_local_not_harness_core`, `test_audit_types_not_imported_from_is_axis`, `test_state_ledger_entry_ref_is_opaque_marker`, `test_audit_payload_no_field_beyond_c_od_14_section_14_5`, `test_audit_signature_attributes_declared_at_u_od_00`, `test_audit_signature_attributes_four_canonical_attributes` (v2.7 D-3), `test_signature_algorithm_three_values_byte_exact` (v2.7 D-1), `test_audit_ledger_cell_id_resolves_to_u_od_01` (v2.7 D-2).

**Rollback boundary:** Revert the OD-local audit-ledger composition type declarations. U-OD-30 `sign_audit_entry` / `verify_hash_chain_integrity` lose their typed parameter carriers, `AuditSignatureAttributes` return carrier, and `SignatureAlgorithm` carrier; the M-1 undeclared-type defect at U-OD-30 reopens. A single coherent revert; downstream U-OD-30's `[U-OD-00]` edge loses its carrier.

---

## §3.7.4 U-OD-30 — `SignatureAlgorithm` note delta [REVISED — v2.7]

[U-OD-30 body preserved verbatim from v2.6 §3.7.4 **except**: per v2.7 D-1, `SignatureAlgorithm` is **no longer declared at U-OD-30** — it is moved to U-OD-00 (§3.0) and U-OD-30 imports it via its existing `[U-OD-00]` edge. The v2.6 note "All other v2.5 surfaces — … `SignatureAlgorithm` … preserved verbatim" is amended: `SignatureAlgorithm` is struck from U-OD-30's preserved-surface list. U-OD-30's `sign_audit_entry(payload, key_id, algo : SignatureAlgorithm)` signature is unchanged — `SignatureAlgorithm` now resolves to the U-OD-00 carrier (same `[U-OD-00]` edge that already resolves `AuditPayload` / `AuditSignatureAttributes`). No new edge; no body rewrite beyond the carrier-resolution note. The v2.6 acc #6/#7 `SignatureAlgorithm` value-set surfaces are unchanged — the value set is identical, only its declaring carrier moves.]

---

## §4.6 Dependency-graph delta (v2.7)

| Edge | Direction | Acyclicity |
|---|---|---|
| `U-OD-00 → U-OD-01` (NEW) | U-OD-00 consumes `CellID` (U-OD-01) | Acyclic — U-OD-01 `Depends on: [U-CORE-01]` only; U-OD-01 does not transitively reach U-OD-00. U-OD-00 moves L0 → L1. |

All v2.6 §4 within-axis + cross-axis edges otherwise preserved verbatim. The `SignatureAlgorithm` move (D-1) adds **no** edge — U-OD-30→U-OD-00 already exists; the move *removes* the latent U-OD-00→U-OD-30 cycle the v2.6 §3.0 body would have required. OD plan level depth and the Kahn topological sort are re-verified: U-OD-00 at L1 (single inbound dep U-OD-01 at L0) introduces no cycle; all 35 units still consume.

---

## §5 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Operational_Discipline_v2_7.md` |
| Authored at | Phase 7 sub-phase 7b, 2026-05-15 — v2.7 Class 1 micro-revision (U-OD-00 carrier defects D-1/D-2/D-3) |
| Authoring authority | Operator ratification 2026-05-15 (`.harness/class_1_tension_u_od_00_carrier_defects.md`) |
| Predecessor | `Implementation_Plan_Operational_Discipline_v2_6.md` (R5 materializability conformance) |
| Successor consumption | U-OD-00 lands against this file; U-OD-30 consumes `SignatureAlgorithm` / `AuditSignatureAttributes` / `AuditPayload` / `AuditLedger` from the U-OD-00 carrier |
| Revision policy | Canonical for the OD axis plan; revisions in-CLI per workspace discipline |

*End of Implementation Plan — Operational Discipline v2.7. Delta over v2.6 — only §3.0 U-OD-00 + the §3.7.4 U-OD-30 note revised. All other sections preserved verbatim from v2.6.*
