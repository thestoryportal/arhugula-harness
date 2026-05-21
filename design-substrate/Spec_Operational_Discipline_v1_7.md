# Specification — Operational Discipline v1.7

## Status block

| Field | Value |
|---|---|
| Artifact | `Spec_Operational_Discipline_v1_7.md` |
| Status | **Proposed** — Phase 7 sub-phase 7b/7c in-CLI Form A patch (F2-04 follow-on arc closure — `compute_entry_hash` materialization at OD axis package) |
| Revision | v1 → v1.1 → v1.2 → v1.3 (F2-12 cascade Step 5b) → v1.4 (FF-2 collector-placement enum formalization, 2026-05-16) → v1.5 (U-RT-59 Fork 2 drift-resolution Path B-revised-a; new C-OD-24 audit-ledger payload + entry composition contract; 2026-05-20) → v1.6 (Form A — adversarial-review path (i) NOTE absorption — §24.4 example format correction + §24.5 helper materialization NOTE, 2026-05-20) → **v1.7 (Form A — F2-04 follow-on arc closure: §24.5 helper materialized at `harness-od/src/harness_od/audit_ledger_types.py`; converter at `harness-cxa/` refactored to import; deferral NOTE updated to RESOLVED, 2026-05-20)** |
| Revision date | 2026-05-20 (v1.7 — F2-04 follow-on closure, same day as v1.6 path (i) absorption) |
| Phase | 7 — sub-phase 7b/7c; in-CLI per workspace `CLAUDE.md` §4.3 |
| Predecessor | `Spec_Operational_Discipline_v1_6.md` (Form A path (i) NOTE absorption — F2-04 deferral filed) |
| Entry authorization | Operator front-(b) selection 2026-05-20 of post-U-RT-59 next-front menu (F2-04 follow-on arc: materialize `compute_entry_hash` at harness-od; refactor harness-cxa converter to import) |
| Co-published with | `Implementation_Plan_Operational_Discipline_v2_13.md` (OD plan absorption of v1.7 helper-materialization statement at §0.1 + line 38 update) |
| Exit gate | Workspace `CLAUDE.md` §2.3 OD row version bump (v1.6 → v1.7) + §2.4 OD plan row bump (v2.12 → v2.13) |

## Change-note (v1.6 → v1.7)

**Scope of revision.** Form A NOTE-state-transition patch over v1.6 absorbing the F2-04 follow-on arc closure (operator front-(b) selection 2026-05-20 of post-U-RT-59 next-front menu). v1.7 transitions the §24.5 helper-materialization deferral NOTE from `deferred` to `RESOLVED` and updates the §24.5 NOTE to reflect the materialization landing:

| Site | Amendment shape | Substrate source |
|---|---|---|
| **§24.5 `compute_entry_hash` canonical helper — NOTE STATE TRANSITION (F2-04 follow-on closure)** | v1.6 NOTE says: "materialization at the `harness-od` axis package is **deferred to a follow-on arc**. As of v1.6, no `def compute_entry_hash` function exists at `harness-od/src/harness_od/`; the canonical recipe is materialized only inline at the production CP→OD converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py:_compute_entry_hash`." v1.7 amends the NOTE to: "**RESOLVED at v1.7 (2026-05-20).** The canonical helper is materialized at `harness-od/src/harness_od/audit_ledger_types.py:compute_entry_hash` per the §24.5 spec recipe. The production CP→OD converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` imports the helper from `harness_od.audit_ledger_types` and delegates (no local inline duplicate). F2-04 inline-drift-risk carry-forward closed." Byte-equivalence anchor at `harness-od/tests/test_audit_ledger_types.py::test_compute_entry_hash_byte_equivalent_to_canonical_recipe` (literal expected hex from fixed input crystallizes the recipe at HEAD). | F2-04 follow-on arc (operator front-(b) selection 2026-05-20); landed code at `harness-od/src/harness_od/audit_ledger_types.py:compute_entry_hash` + refactored converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` (local `_compute_entry_hash` removed; `compute_entry_hash` imported from `harness_od.audit_ledger_types`); 4 new tests at `harness-od/tests/test_audit_ledger_types.py` (byte-equivalence + determinism + output shape + collision-resistance smoke); 2287 workspace tests green (prior 2283 + 4 new) |

**Sections preserved verbatim from v1.6.** All v1.6 content outside the §24.5 NOTE body preserved unchanged. §24.1 + §24.2 + §24.3 + §24.4 (v1.6 example-format fix) + §24.5 helper signature + recipe + Authority block + §24.6 CP-sourced audit-entry recognition + filing footer all stand. The §24.5 helper signature + recipe + Authority block preserved verbatim from v1.5/v1.6; only the v1.6 deferral NOTE body transitions to RESOLVED.

**Contract count.** OD axis contract count preserved at **24** at v1.7 (C-OD-24 unchanged — only NOTE state-transition; recipe text unchanged).

**Status posture.** `Status: Proposed` preserved per workspace discipline. v1.7 is a Form A NOTE-state-transition patch — no signature change, no contract re-decomposition, no acceptance criterion change. Closes the only path-(i) drift-risk carry-forward filed at v1.6 + adversarial review.

**Downstream absorption owed.** (a) Workspace `CLAUDE.md` §2.3 OD row version bump (v1.5 → v1.6); (b) `Spec_Control_Plane_v1_9.md` co-published this turn (CP-side NOTE absorption at §13.5.1); (c) `Spec_Harness_Runtime_v1.md` v1.8 co-published this turn (runtime-side NOTE absorption at §14.7.2 step 8a). Co-publication is single-arc per the path (i) ratification.

---

## §24 C-OD-24 — Audit-ledger payload + entry composition

[§24.1 + §24.2 + §24.3 preserved verbatim from v1.5.]

### §24.4 `StateLedgerEntryRef` opaque IS marker (v1.6 example-format inline fix)

```
StateLedgerEntryRef = NewType("StateLedgerEntryRef", str)
```

An opaque `str`-newtype marker referencing an IS-exported F2 state-ledger entry. C-OD-24 declares the type name; the concrete IS-side resolution (the actual entry the marker points to) is at U-OD-30's cross-axis IS edge per C-IS-10 §10.1 (IS state-ledger entry shape export). **At v1.6 the marker holds a string reference (typically the F2 entry hash or a constructed action_id like `dispatch:<parent_action_id>:<child_index>` per the runtime spec §14.7.2 step 8b canonical pattern for sub-agent dispatch F2-write composition).**

*v1.5 → v1.6 delta:* the example action_id format `cp-audit:<cp_action_id>` is replaced with the canonical `dispatch:<parent_action_id>:<child_index>` pattern per runtime spec §14.7.2 step 8b. Adversarial-review F1-02 drift item closed.

### §24.5 `compute_entry_hash` canonical helper (v1.7 NOTE — RESOLVED)

[Helper signature + recipe + Authority block preserved verbatim from v1.5/v1.6.]

**NOTE — helper materialization at the OD axis package (v1.7 RESOLVED).** The §24.5 canonical helper signature + recipe is materialized at `harness-od/src/harness_od/audit_ledger_types.py:compute_entry_hash` per the §24.5 spec recipe (SHA-256 over `payload.model_dump_json()`). The production CP→OD converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` imports `compute_entry_hash` from `harness_od.audit_ledger_types` and delegates — no local inline duplicate remains. Byte-equivalence anchor at `harness-od/tests/test_audit_ledger_types.py::test_compute_entry_hash_byte_equivalent_to_canonical_recipe` crystallizes the recipe with a literal expected SHA-256 hex output (`3567132e039dd0e6e47c9a3258ebddcdf56626ba5c0e06ef29256e6d25998490`) for a fixed `AuditPayload` — any future canonicalization drift breaks this test before the converter round-trip tests run.

**v1.6 → v1.7 history.** v1.6 NOTE filed the deferral ("materialization at the `harness-od` axis package is **deferred to a follow-on arc**") under adversarial-review path (i) disposition. v1.7 follow-on arc (operator front-(b) selection 2026-05-20) materialized the helper + refactored the converter + landed byte-equivalence test. F2-04 inline-drift-risk carry-forward closed.

[§24.6 CP-sourced audit-entry recognition preserved verbatim from v1.5.]

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Operational_Discipline_v1_7.md` |
| Status | Proposed — Phase 7 7b/7c in-CLI Form A NOTE-state-transition patch (F2-04 follow-on arc closure) |
| Predecessor | `Spec_Operational_Discipline_v1_6.md` — preserved verbatim except §24.5 NOTE body (deferred → RESOLVED) |
| Substrate consumed | OD spec v1.6 §24.5 deferral NOTE; landed code at `harness-od/src/harness_od/audit_ledger_types.py:compute_entry_hash` (canonical helper materialized) + refactored converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` (local `_compute_entry_hash` removed); 4 new tests at `harness-od/tests/test_audit_ledger_types.py` (byte-equivalence anchor + determinism + output shape + collision-resistance smoke); 2287 workspace tests green |
| Co-published with | `Implementation_Plan_Operational_Discipline_v2_13.md` (OD plan absorption of v1.7 helper-materialization statement at §0.1 + line 38 update) |
| Successor | Workspace `CLAUDE.md` §2.3 OD row version bump (v1.6 → v1.7); §2.4 OD plan row bump (v2.12 → v2.13); only path-(i) drift-risk carry-forward closed at this filing |
| Revision policy | In-CLI per workspace discipline (`CLAUDE.md` §4.3) |
| Date | 2026-05-20 |

*Filed at Phase 7 sub-phase 7b/7c as the OD-side Form A patch closing the F2-04 follow-on arc (operator front-(b) selection 2026-05-20). §24.5 NOTE transitions from "deferred" → "RESOLVED" with materialization at `harness-od/src/harness_od/audit_ledger_types.py:compute_entry_hash` + converter refactor at `harness-cxa/`. Closes the only path-(i) drift-risk carry-forward filed at v1.6 + adversarial review.*
