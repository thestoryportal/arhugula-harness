# Implementation Plan — Control Plane (CP axis) — v2.14

## §0 Change-note (v2.13 → v2.14)

**Revision:** v2.14 — Phase 7 implementation arc absorption (U-RT-59 Fork 2
close), in-CLI. Absorbs the CP spec v1.7 §13.5.1 `cp_audit_to_od_audit`
converter contract + v1.8 Form A NOTE-reference reconciliation at U-CP-28's
`Implements:` citation. Co-published with the U-RT-59 implementation landing
commit + runtime spec v1.7 §14.7.2 step 8 4-substep sequence + workspace
CLAUDE.md §2.3 OD contract-count update (23 → 24) + OD plan v2.11 → v2.12.

**Predecessor:** v2.13 (CP spec v1.5 §25.9 cost-attribution emission
absorption).

**Spec stability invariant preserved.** No new atomic unit at v2.14. The
§13.5.1 converter contract materializes at the implementation arc via
`harness_cxa.cp_audit_conversion.cp_audit_to_od_audit` (moved from prototype
location at `harness-runtime/src/harness_runtime/lifecycle/cp_audit_conversion.py`
per Q5 ratification); the runtime composer at
`harness_runtime.lifecycle.sub_agent_dispatch.RuntimeSubAgentDispatcher`
invokes the converter at step 8c per runtime spec v1.7 §14.7.2 step 8.
U-CP-28 (sub-agent handoff context + audit-trail-link composition) gains
the §13.5.1 citation at its `Implements:` line; no signature change.

### §0.1 Net delta from v2.13

1. **U-CP-28 `Implements:` line gains `C-CP-13 §13.5.1` citation.** The unit
   now traces to both §13.5 (LedgerEntryRef + audit-trail-link composition,
   preserved verbatim from v1.2) AND §13.5.1 (NEW at v1.7; v1.8 Form A
   NOTE-reference resolution). The converter implementation lives at
   `harness-cxa/` per Q5 ratification — U-CP-28's body owes no new code
   at v2.14 (the converter is a CXA-axis-instantiated seam; CP authority
   over the field-projection table + namespace + entry_core semantic is
   declarative).

2. **No atomic unit signature changed.** U-CP-28's acceptance criteria
   (HandoffContext payload composition + audit-trail-link composition)
   remain materialized at HEAD; the §13.5.1 converter contract is a
   companion declarative surface co-resident under C-CP-13.

3. **No within-axis DAG change.** §3 topology preserved verbatim from
   v2.13; U-CP-28's dependency graph unchanged.

### §0.2 Cross-axis edge added

Per `Cross_Axis_Composition_Document_v2_4.md` §2.3.7 (new bucket; co-published
with CP spec v1.7): new typed cross-axis edge **U-CP-28 → U-OD-00** (class G,
genuine typed seam, Pattern P1). This is the **first** CP→OD typed-seam edge
in project history; CXA v2.4 §2.3.7 declares the edge enumeration; v2.14
preserves the §5 cross-axis edge inventory invariant by acknowledging the
edge at U-CP-28's traceability surface.

### §0.3 Sections preserved verbatim from v2.13

All v2.13 content outside §0 change-note + the U-CP-28 `Implements:` line
addition preserved unchanged. §25.9 cost-attribution absorption from v2.13
stands. §3 within-axis DAG topology preserved. §4 coverage matrix preserved.
§5 cross-axis edge inventory preserved + extended at §0.2. §6 / §7 / §0.6 /
§0.7 carry-forwards preserved.

### §0.4 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_14.md` |
| Status | Proposed — Phase 7 7b/7c in-CLI U-RT-59 Fork 2 implementation arc absorption |
| Predecessor | `Implementation_Plan_Control_Plane_v2_13.md` (v1.5 §25.9 absorption) — preserved verbatim except for U-CP-28 `Implements:` citation extension |
| Co-published with | runtime spec v1.7 implementation commit + OD plan v2.12 + workspace CLAUDE.md §2.3 contract-count update |
| Substrate consumed | `Spec_Control_Plane_v1_7.md` §13.5.1 + `Spec_Control_Plane_v1_8.md` Form A patch; `Cross_Axis_Composition_Document_v2_4.md` §2.3.7; runtime spec v1.7 §14.7.2 step 8 |
| Successor | future CP plan revision incorporating any §13.5.1 NOTE follow-ups |
| Revision policy | In-CLI per workspace discipline (`CLAUDE.md` §4.3) |
| Date | 2026-05-20 |

*v2.14 absorbs the U-RT-59 Fork 2 spec arc into the CP plan substrate. No
new atomic unit; U-CP-28 trace surface extended with the §13.5.1 converter
contract citation + the new CP→OD CXA edge at §2.3.7. Spec authority for
the converter contract lives in CP spec v1.7 + v1.8; implementation lives
at `harness-cxa/cp_audit_conversion.py` per Q5 ratification.*
