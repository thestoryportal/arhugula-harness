# Specification — Control Plane v1.8

## Change-note (v1.7 → v1.8)

**Scope of revision.** Form A citation-precision patch over v1.7. Updates `Spec_Control_Plane_v1_7.md` §13.5.1 NOTE 1 + NOTE 2 references from "drift-resolution-arc-pending" status (the framing committed at v1.7 when the OD-side drift had not yet been resolved) to "drift-resolved-at-ADR-D5-v1.4 + OD-spec-v1.5 + runtime-spec-v1.7" closure status. No contract content changed; no signature changed; no field added or removed. Pure NOTE-reference reconciliation.

**Single amendment site.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **§13.5.1 NOTE 1 (entry_hash canonicalization)** | v1.7 NOTE 1 says: "The OD-side canonical recipe for `AuditLedgerEntry.entry_hash` is **not specified** at HEAD ... canonicalization to a spec-anchored recipe is owed to the **OD-side audit-ledger drift resolution arc** per discovery report §10." v1.8 amends to: "RESOLVED at ADR-D5 v1.4 §1.4.1 + OD spec v1.5 C-OD-24.5 — canonical recipe is SHA-256 over `AuditPayload.model_dump_json()` per the Pydantic v2 canonical JSON serialization. The converter at HEAD uses this recipe; the §24.5 `compute_entry_hash` helper materializes the canonical formula." | Operator-ratified Path B-revised-a landing (`b3d9368`, 2026-05-20); ADR-D5 v1.4 §1.4.1 tightening; OD spec v1.5 C-OD-24.5 canonical helper; landed code at `harness-runtime/src/harness_runtime/lifecycle/cp_audit_conversion.py` (HEAD `99982de`) — interim convention IS the canonical recipe per Path B-revised-a code-canonical framing |
| **§13.5.1 NOTE 2 (composer step F2-write specification)** | v1.7 NOTE 2 says: "The dispatch composer step amendment (steps 1–5 in the entry_core source semantic enumeration above) is **owed to runtime spec** ... not in CP spec v1.7 scope." v1.8 amends to: "RESOLVED at runtime spec v1.7 §14.7.2 step 8 (4-substep sequence 8a–8d) — composer step now specifies CP audit compose + F2-write of dispatch action + CP→OD convert + audit_writer.append per the Path D + B-revised-a resolution. Class 3 drift item 1 (`ctx.audit_ledger_writer` → `ctx.audit_writer` field name) RESOLVED at runtime spec v1.7 step 8d rewrite." | Operator-ratified U-RT-59 Fork 2 implementation arc spec amendments (`b3d9368` + this v1.8 patch + runtime spec v1.7 amendment co-published this turn) |

**Sections preserved verbatim from v1.7.** All v1.7 content outside §13.5.1 NOTE 1 + NOTE 2 paragraphs preserved unchanged. C-CP-13 §13.5 (LedgerEntryRef — preserved from v1.2) stands. §13.5.1 converter contract signature + field-projection table + namespace + Q1+Q2(a)+Q4+Q5 commitments + NOTE 3 (cryptographic-payload-mismatch foreclosure) all preserved verbatim. v1.6 §25.2 + §25.3.3.4 + §25.7 + §25.9 + the rest of v1.6 + v1.5 + v1.4 + v1.3 + v1.2 + v1.1 + v1 chain all preserved.

**Status posture.** Proposed (v1.7) → **Proposed (v1.8)**. v1.8 is a Form A citation-precision patch — no signature change, no contract re-decomposition, no acceptance criterion change; promotion to Accepted blocked until the broader U-RT-59 Fork 2 implementation arc closes per Phase 7 sub-phase 7b discipline.

**Downstream absorption owed (post-v1.8).** (a) `.harness/u_rt_59_fork_2_cp_to_od_audit_discovery.md` — append a final §11 noting all four planned resolution arcs (Path D + B-revised-a + runtime v1.7 + this CP spec v1.8 patch) landed; (b) CP plan v2.13 → v2.14 absorption at U-CP-28 (cite §13.5.1 v1.7 + v1.8); (c) OD plan v2.11 → v2.12 absorption at U-OD-00 (cite C-OD-24); (d) implementation landing commit (composer wiring + tests + AC #9 un-strike + converter code move per Q5).

---

## Status block

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_8.md` |
| Status | **Proposed** — Phase 7 sub-phase 7b/7c in-CLI Form A citation-precision patch |
| Revision | v1 → v1.1 → v1.2 → v1.3 → v1.4 → v1.5 → v1.6 → v1.7 (U-RT-59 Fork 2 Path D — §13.5.1 converter contract) → **v1.8 (Form A — v1.7 §13.5.1 NOTE 1 + NOTE 2 references resolved post Path B-revised-a + runtime v1.7 landings, 2026-05-20)** |
| Revision date | 2026-05-20 (v1.8 Form A patch, same day as v1.7) |
| Phase | 7 — sub-phase 7b/7c; in-CLI per workspace `CLAUDE.md` §4.3 |
| Skill | `spec-writer` (Form A citation-precision sub-mode) at v1.8 |
| Predecessor | `Spec_Control_Plane_v1_7.md` (§13.5.1 converter contract — preserved verbatim except for NOTE 1 + NOTE 2 paragraph amendments) |
| Co-published with | `Spec_Harness_Runtime_v1.md` v1.7 (§14.7.2 step 8 4-substep sequence) |
| Substrate consumed | All v1.7 inputs (preserved) + `ADR-D5.md` v1.4 + `Spec_Operational_Discipline_v1_5.md` (Path B-revised-a landings); `Spec_Harness_Runtime_v1.md` v1.7 (composer-step amendment co-published) |
| Exit gate | CP plan v2.13 → v2.14 + implementation landing commit (composer wiring + AC #9 un-strike) |

---

## §13 C-CP-13 — Sub-agent handoff context + audit-trail-link composition

[All content preserved verbatim from v1.7. §13.1 + §13.2 + §13.3 + §13.4 + §13.5 (LedgerEntryRef) unchanged from v1.2. §13.5.1 converter contract preserved verbatim from v1.7 EXCEPT NOTE 1 + NOTE 2 paragraphs revised at v1.8.]

### §13.5.1 CP→OD audit-write composition — `cp_audit_to_od_audit` converter contract (v1.7 NEW; v1.8 NOTE 1 + NOTE 2 revised)

[Signature + Field-projection table + Namespace commitment + Q1 commitment + Q2(a) commitment + Converter home + NOTE 3 + Cross-axis citation + Deferred-to-implementation-discretion all preserved verbatim from v1.7. NOTE 1 + NOTE 2 revised at v1.8 below.]

**NOTE 1 — `entry_hash` canonicalization (v1.8 RESOLVED).** RESOLVED at `ADR-D5.md` v1.4 §1.4.1 + `Spec_Operational_Discipline_v1_5.md` C-OD-24.5 per operator-ratified Path B-revised-a landing (2026-05-20, commit `b3d9368`). The OD-side canonical recipe is **SHA-256 over `AuditPayload.model_dump_json()`** — Pydantic v2 canonical JSON serialization under the OD-axis `ConfigDict(extra="forbid", frozen=True)` discipline (deterministic byte sequence for a given `AuditPayload` instance; field ordering = model declaration order). The C-OD-24.5 `compute_entry_hash(payload: AuditPayload) -> str` helper materializes this recipe at the OD axis. The converter at HEAD (`harness-runtime/src/harness_runtime/lifecycle/cp_audit_conversion.py`) uses this recipe; v1.8 marks the v1.7 NOTE 1 deferral as resolved.

**NOTE 2 — Composer step F2-write specification (v1.8 RESOLVED).** RESOLVED at `Spec_Harness_Runtime_v1.md` v1.7 §14.7.2 step 8 (4-substep sequence 8a–8d) per the U-RT-59 Fork 2 implementation arc co-published with this v1.8 patch. The dispatch composer now specifies: (8a) CP audit compose via existing `ctx.handoff_registry.compose_dispatch_audit(...)`; (8b) F2-write of dispatch action via `ctx.state_ledger_writer.append(...)` → capture `StateLedgerEntryRef`; (8c) CP→OD convert via `cp_audit_to_od_audit(cp_entry, key_id=..., algo=..., entry_core=<step-8b ref>)` per this §13.5.1 contract; (8d) OD audit append via `ctx.audit_writer.append(tenant_id, od_entry)` per C-RT-04. Class 3 drift item 1 (`.harness/class_3_tension_u_rt_59_spec_prose_drift.md` — the `ctx.audit_ledger_writer` field name drifted from C-RT-04 canonical `ctx.audit_writer`) ALSO RESOLVED at runtime spec v1.7 step 8d rewrite. v1.8 marks the v1.7 NOTE 2 deferral as resolved.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_8.md` |
| Status | Proposed — Phase 7 7b/7c in-CLI Form A citation-precision patch |
| Predecessor | `Spec_Control_Plane_v1_7.md` (U-RT-59 Fork 2 Path D converter contract) — preserved verbatim except NOTE 1 + NOTE 2 |
| Co-published with | `Spec_Harness_Runtime_v1.md` v1.7 (§14.7.2 step 8 4-substep sequence) |
| Substrate consumed | v1.7 inputs (preserved) + ADR-D5 v1.4 + OD spec v1.5 (Path B-revised-a landings at `b3d9368`); runtime spec v1.7 (co-published this turn) |
| Successor | CP plan v2.13 → v2.14 absorption at U-CP-28; implementation landing commit (composer wiring + AC #9 un-strike) |
| Revision policy | In-CLI per workspace discipline (`CLAUDE.md` §4.3) |
| Date | 2026-05-20 |

*Filed at Phase 7 sub-phase 7b/7c as the Form A patch closing v1.7 §13.5.1 NOTE 1 + NOTE 2 deferred-reference status. v1.7 substantive contract content preserved verbatim; only the two NOTE paragraphs amended to reflect post-landing resolution at ADR-D5 v1.4 + OD spec v1.5 + runtime spec v1.7. Pure citation-precision delta; no signature change.*
