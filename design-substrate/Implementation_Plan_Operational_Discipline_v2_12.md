# Implementation Plan — Operational Discipline (OD axis) — v2.12

## §0 Change-note (v2.11 → v2.12)

**Revision:** v2.12 — Phase 7 implementation arc absorption (U-RT-59 Fork 2
close), in-CLI. Absorbs the OD spec v1.5 C-OD-24 contract (audit-ledger
payload + entry composition; canonical entry_hash helper; CP-sourced audit-
entry recognition) at U-OD-00's `Implements:` citation. Co-published with
the U-RT-59 implementation landing commit + runtime spec v1.7 §14.7.2 step 8
4-substep sequence + workspace CLAUDE.md §2.3 OD contract-count update
(23 → 24) + CP plan v2.13 → v2.14.

**Predecessor:** v2.11 (CP-outbound cross-axis placeholder carrier IDs
resolved at §4.5.2 / §4.5.3 + 8 unit bodies per 7c-prereq Form A).

**Spec stability invariant inverts at v2.12.** Unlike v2.11 (which closed a
plan-side 7c-prereq with NO spec bump), v2.12 absorbs a spec amendment (OD
spec v1.4 → v1.5 new C-OD-24 contract). v2.12 carries the spec change
downstream into the plan; no further spec amendment required at v2.12 close.

### §0.1 Net delta from v2.11

1. **U-OD-00 `Implements:` line gains `C-OD-24` citation.** The unit was
   previously authored against C-OD-21 §21.2 (audit-signature-attributes
   surface placement); C-OD-24 lifts the broader audit-ledger payload +
   entry composition shapes (`AuditPayload`, `AuditLedgerEntry`,
   `AuditLedger`, `StateLedgerEntryRef`, `compute_entry_hash`,
   CP-sourced audit-entry recognition at §24.6) into spec authority.
   The unit's body owes no new code at v2.12 — the shapes were already
   materialized at HEAD (`harness-od/src/harness_od/audit_ledger_types.py`);
   v2.12 ratifies them as spec-anchored per the Path B-revised-a
   "code-canonical" framing.

2. **No atomic unit signature changed.** U-OD-00's acceptance criteria
   stand. The new C-OD-24 citation broadens the unit's contract trace
   surface to the now-canonical audit-ledger schema; no new ACs are
   owed (the shapes are already implemented; the canonical
   `compute_entry_hash` helper at §24.5 is provided by the converter at
   `harness-cxa/cp_audit_conversion.py`).

3. **No within-axis DAG change.** §3 topology preserved verbatim from
   v2.11; U-OD-00's dependency graph unchanged.

### §0.2 X-AL-3 drift retirement (closed at v1.5 / v2.12 co-publication)

The pre-existing X-AL-3 drift surfaced at U-RT-59 Fork 2 discovery report §9
+ §10 — OD audit-ledger Pydantic types specified in code only without
canonical spec contract — is RETIRED at OD spec v1.5 §24. v2.12 acknowledges
the retirement at the plan substrate; future code changes to the audit-ledger
types MUST conform to C-OD-24 or route to an OD spec v1.6 revision pass.

### §0.3 Cross-axis edge inbound

Per `Cross_Axis_Composition_Document_v2_4.md` §2.3.7: new typed cross-axis
edge **U-CP-28 → U-OD-00** (class G, genuine typed seam, Pattern P1). v2.12
acknowledges U-OD-00 as the inbound terminus of this first CP→OD typed seam
in project history; OD outbound invariant ("0 outbound cross-axis edges"
per `harness-od/CLAUDE.md` §2.2) preserved unchanged — the edge is OD-
inbound.

### §0.4 Sections preserved verbatim from v2.11

All v2.11 content outside §0 change-note + the U-OD-00 `Implements:` line
addition preserved unchanged. §4.5 cross-axis edge inventory preserved
(extended via §0.3 acknowledgment). §3 within-axis DAG topology preserved.
§6 / §7 carry-forwards preserved.

### §0.5 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Operational_Discipline_v2_12.md` |
| Status | Proposed — Phase 7 7b/7c in-CLI U-RT-59 Fork 2 implementation arc absorption |
| Predecessor | `Implementation_Plan_Operational_Discipline_v2_11.md` (CP-outbound placeholder carrier resolution) — preserved verbatim except for U-OD-00 `Implements:` citation extension |
| Co-published with | runtime spec v1.7 implementation commit + CP plan v2.14 + workspace CLAUDE.md §2.3 contract-count update + OD spec v1.5 C-OD-24 |
| Substrate consumed | `Spec_Operational_Discipline_v1_5.md` C-OD-24; `ADR-D5.md` v1.4 §1.4 + §1.4.1; `Cross_Axis_Composition_Document_v2_4.md` §2.3.7; runtime spec v1.7 §14.7.2 step 8 |
| Successor | future OD plan revision incorporating any §24.6 namespace-registration follow-ups (operator-side `audit.cp.*` row at C-OD-05) |
| Revision policy | In-CLI per workspace discipline (`CLAUDE.md` §4.3) |
| Date | 2026-05-20 |

*v2.12 absorbs the U-RT-59 Fork 2 spec arc into the OD plan substrate. No
new atomic unit; U-OD-00 trace surface extended with the C-OD-24 audit-
ledger schema citation. X-AL-3 drift retired at the OD spec v1.5 / plan
v2.12 co-publication. CP→OD typed seam edge acknowledged at U-OD-00 inbound
terminus; OD outbound invariant preserved.*
