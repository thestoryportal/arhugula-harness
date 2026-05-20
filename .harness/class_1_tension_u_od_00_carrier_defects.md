# Class 1 Tension — U-OD-00 carrier-unit defects (D-1 / D-2 / D-3)

*Phase 7 sub-phase 7b. Fork detected at U-OD-00 execution-time. Routed per
`CLAUDE.md` §4.3 + `harness-od/CLAUDE.md` §5.1. RESOLVED — operator ruling
2026-05-15.*

---

## 1. Identification

| Field | Value |
|---|---|
| Tension ID | Class-1 / U-OD-00 / carrier-defects |
| Sub-phase | 7b (per-axis-stream implementation — carrier-unit cluster) |
| Surfaced at | Landing U-OD-00 (OD audit-ledger composition-type carrier) |
| Class | **1** — architectural defect; plan unit body internally inconsistent + dependency-graph contradictory |
| Routing target | Phase 6 plan revision — `Implementation_Plan_Operational_Discipline` v2.6 → v2.7 (in-CLI) |
| Status | **RESOLVED** 2026-05-15 — micro-revision ratified by operator |

## 2. The three defects

The v2.6 §3.0 U-OD-00 unit body (new at R5) carries three Class 1 defects.

**D-1 — dependency cycle on `SignatureAlgorithm`.** `AuditSignatureAttributes`
(moved to U-OD-00 by Q-R5-3) has a field typed `SignatureAlgorithm`. v2.6 leaves
`SignatureAlgorithm` declared at U-OD-30. But U-OD-30 already depends on U-OD-00
(`[U-OD-00]` edge, for `AuditPayload`/`AuditLedger`/`AuditSignatureAttributes`).
U-OD-00 importing `SignatureAlgorithm` from U-OD-30 → **U-OD-00 ↔ U-OD-30 cycle.**

**D-2 — missing `[U-OD-01]` edge / false L0 status.** `AuditLedger.cell_id` is
typed `CellID`, declared in-unit at U-OD-01. v2.6 declares U-OD-00
`Depends on: (none)` and Q-R5-5 ratifies U-OD-00 as a strict L0 anchor. The v2.6
§4.6 `CellID`-consumer table omits U-OD-00. The edge is missing and the L0
classification is false.

**D-3 — `AuditSignatureAttributes` field-set divergence (X-AL-3).** The v2.6 §3.0
signature block declares `AuditSignatureAttributes` as
`{algo, key_id, signature_value, signed_at_unix_ns}`. The v2.5-canonical record
Q-R5-3 claims to *move* is `{audit_signature_value, audit_signature_algorithm,
audit_signature_key_id, audit_signature_key_period}` — the 4-attribute
`audit.signature.*` set per OD spec §21.2 / ADR-D5 v1.3 §1.4.1. The v2.6 rewrite
introduced `signed_at_unix_ns` (**not** in the `audit.signature.*` namespace — an
un-spec'd field; X-AL-3 silent design extension) and dropped
`audit_signature_key_period`. A Q-R5-3 "move" is a verbatim relocation, not a
redesign.

## 3. Halt + routing

Per `phase-7-implementation` SKILL.md §6 ("Acceptance criterion incompatible …"
+ "Plan signature cannot be materialized"), U-OD-00 landing halted. D-1 + D-2 are
dependency-graph contradictions; D-3 is an un-spec'd field. Surfaced to operator.

## 4. Operator ruling — 2026-05-15

**Micro-revise OD plan v2.6 → v2.7, then land.** D-1: `SignatureAlgorithm` moves
to U-OD-00 (co-located with `AuditSignatureAttributes`); U-OD-30 imports it via
its existing `[U-OD-00]` edge — cycle dissolved. D-2: U-OD-00 takes a `[U-OD-01]`
edge for `CellID`; U-OD-00 is re-leveled L0 → **L1**; Q-R5-5's L0-set narrative
amended to `{U-OD-01, U-OD-04}`. D-3: `AuditSignatureAttributes` corrected to the
v2.5-canonical 4-attribute `audit.signature.*` set — `signed_at_unix_ns` struck,
`audit_signature_key_period` restored. D-3 is determinate (the spec dictates the
4-attribute set; no operator choice).

## 5. Resolution applied

- `Implementation_Plan_Operational_Discipline_v2_7.md` filed — §3.0 U-OD-00
  re-revised (D-1/D-2/D-3); §3.7.4 U-OD-30 `SignatureAlgorithm` note delta; §4.6
  dependency-graph delta (U-OD-00 → U-OD-01); §0.3 Q-R5-5 amendment.
- `CLAUDE.md` §2.4 OD plan pointer updated v2_6 → v2_7.
- U-OD-00 landed against v2.7.

## 6. Flagged follow-ups

| ID | Item | Owed at |
|---|---|---|
| F-1 | `harness-od/CLAUDE.md` §3 L0-set / unit-count follow-up (already owed from v2.6 §0.9) is **extended**: the L0 set drops U-OD-00 (now L1) — `{U-OD-01, U-OD-04}`. Operator-applied `harness-od/CLAUDE.md` edit. | Next operator `harness-od/CLAUDE.md` touch |

## 7. Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/class_1_tension_u_od_00_carrier_defects.md` |
| Authored | Phase 7 7b, 2026-05-15 |
| Resolution authority | Operator ruling 2026-05-15 (micro-revise + land) |
| Status | RESOLVED — cleared for U-OD-00 landing against OD plan v2.7 |

---

## Audit reconciliation (2026-05-20)

**Verified status:** RESOLVED

**Resolving artifact / evidence:** Already labeled RESOLVED 2026-05-15 (OD plan v2.7 — D-1/D-2/D-3 carrier defects addressed). Audit confirms.

**Audit context:** Workspace-wide tension-record audit 2026-05-20 (post-U-RT-52 merge to main at 2b945ab). 33 records reviewed against current code + spec state. Result: 28 RESOLVED, 5 DEFERRED-PARTITION, 0 STILL-OPEN. The 'Status' line earlier in this record predates the audit; this section is the current verified state.
