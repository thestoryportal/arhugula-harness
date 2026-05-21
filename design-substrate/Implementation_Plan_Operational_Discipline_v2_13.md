# Implementation Plan — Operational Discipline (OD axis) — v2.13

## §0 Change-note (v2.12 → v2.13)

**Revision:** v2.13 — Phase 7 F2-04 follow-on arc closure (post-U-RT-59
adversarial-review path (i) drift-risk closure), in-CLI. Absorbs OD spec
v1.6 → v1.7 (the §24.5 helper-materialization NOTE transitions from
"deferred" → "RESOLVED"). U-OD-00 unit body gains the materialized
`compute_entry_hash` helper at `harness-od/src/harness_od/audit_ledger_types.py`;
the production CP→OD converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py`
now imports the helper (no local inline duplicate). 4 new tests at
`harness-od/tests/test_audit_ledger_types.py` (byte-equivalence anchor +
determinism + output shape + collision-resistance smoke). 2287 workspace
tests green.

**Predecessor:** v2.12 (Phase 7 U-RT-59 Fork 2 implementation arc absorption;
U-OD-00 `Implements:` C-OD-24 citation landed; `compute_entry_hash` helper
provided by converter at `harness-cxa/`).

**Spec stability invariant.** v2.13 absorbs an OD spec bump (v1.6 → v1.7
Form A NOTE state-transition); no contract count change (24 preserved);
no atomic unit signature change. v2.13 is a plan-side citation absorption
of the helper-materialization state-transition; no within-axis DAG change.

### §0.1 Net delta from v2.12

1. **U-OD-00 unit body gains the materialized `compute_entry_hash` helper.**
   At v2.12 the §24.5 canonical helper was declared in spec only (NOTE filed
   at v1.6 deferring materialization; production callsite at
   `harness-cxa/src/harness_cxa/cp_audit_conversion.py:_compute_entry_hash`
   inlined the recipe under byte-equivalence constraint). At v2.13 the
   helper materializes at `harness-od/src/harness_od/audit_ledger_types.py:compute_entry_hash`
   per the §24.5 spec recipe (SHA-256 over `payload.model_dump_json()`).
   The converter at `harness-cxa/` is refactored to import the helper from
   `harness_od.audit_ledger_types` and delegate; the local `_compute_entry_hash`
   duplicate is removed. F2-04 inline-drift-risk carry-forward closed.

2. **No atomic unit signature changed.** U-OD-00's acceptance criteria
   stand. v2.13 adds the materialized helper at the same package as the
   other C-OD-24 typed surfaces (`AuditPayload`, `AuditLedgerEntry`,
   `AuditLedger`, `StateLedgerEntryRef`); no new ACs are owed (the recipe
   was already spec-anchored at OD spec v1.5 §24.5; v2.13 just relocates
   the materialization from the converter call-site to the OD axis package
   per the v1.7 NOTE state-transition).

3. **No within-axis DAG change.** §3 topology preserved verbatim from
   v2.12; U-OD-00's dependency graph unchanged.

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
| Artifact | `Implementation_Plan_Operational_Discipline_v2_13.md` |
| Status | Proposed — Phase 7 7b/7c in-CLI F2-04 follow-on arc closure |
| Predecessor | `Implementation_Plan_Operational_Discipline_v2_12.md` (U-RT-59 Fork 2 implementation arc absorption) — preserved verbatim except §0 change-note + §0.1 helper-materialization statement |
| Co-published with | OD spec v1.7 (§24.5 NOTE state-transition deferred → RESOLVED); workspace CLAUDE.md §2.3 OD row v1.6 → v1.7 + §2.4 OD plan row v2.12 → v2.13 |
| Substrate consumed | `Spec_Operational_Discipline_v1_7.md` §24.5 (RESOLVED NOTE); landed code at `harness-od/src/harness_od/audit_ledger_types.py:compute_entry_hash` + refactored converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py`; 4 new tests at `harness-od/tests/test_audit_ledger_types.py`; 2287 workspace tests green |
| Successor | future OD plan revision incorporating any §24.6 namespace-registration follow-ups (operator-side `audit.cp.*` row at C-OD-05) |
| Revision policy | In-CLI per workspace discipline (`CLAUDE.md` §4.3) |
| Date | 2026-05-20 |

*v2.13 absorbs the F2-04 follow-on arc closure into the OD plan substrate. No
new atomic unit; U-OD-00 trace surface extended with the materialized
`compute_entry_hash` helper at the OD package per OD spec v1.7 §24.5 RESOLVED.
Closes the only path-(i) drift-risk carry-forward filed at OD spec v1.6 +
adversarial review.*
