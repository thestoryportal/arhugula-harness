# Specification — Operational Discipline v1.6

## Status block

| Field | Value |
|---|---|
| Artifact | `Spec_Operational_Discipline_v1_6.md` |
| Status | **Proposed** — Phase 7 sub-phase 7b/7c in-CLI Form A patch (U-RT-59 Fork 2 adversarial-review path (i) NOTE-form absorption) |
| Revision | v1 → v1.1 → v1.2 → v1.3 (F2-12 cascade Step 5b) → v1.4 (FF-2 collector-placement enum formalization, 2026-05-16) → v1.5 (U-RT-59 Fork 2 drift-resolution Path B-revised-a; new C-OD-24 audit-ledger payload + entry composition contract; 2026-05-20) → **v1.6 (Form A — adversarial-review path (i) NOTE absorption — §24.4 example format correction + §24.5 helper materialization NOTE, 2026-05-20)** |
| Revision date | 2026-05-20 (v1.6 — Form A patch, same day as v1.5 adversarial review) |
| Phase | 7 — sub-phase 7b/7c; in-CLI per workspace `CLAUDE.md` §4.3 |
| Predecessor | `Spec_Operational_Discipline_v1_5.md` (U-RT-59 Fork 2 Path B-revised-a — new C-OD-24 contract) |
| Entry authorization | Operator ratification 2026-05-20 of `.harness/adversarial_review_u_rt_59_fork_2_spec_bundle.md` path (i) NOTE-form patch disposition |
| Co-published with | `Spec_Control_Plane_v1_9.md` (path (i) CP-side NOTE absorption at §13.5.1); `Spec_Harness_Runtime_v1.md` v1.8 (path (i) runtime-side NOTE absorption at §14.7.2 step 8a) |
| Exit gate | Workspace `CLAUDE.md` §2.3 OD row version bump (v1.5 → v1.6) |

## Change-note (v1.5 → v1.6)

**Scope of revision.** Form A NOTE-reference patch over v1.5 absorbing the operator-ratified path (i) disposition from `.harness/adversarial_review_u_rt_59_fork_2_spec_bundle.md` (2026-05-20). v1.6 lands two amendments at the OD-side audit-ledger contract surface:

| Site | Amendment shape | Substrate source |
|---|---|---|
| **§24.4 `StateLedgerEntryRef` example format (F1-02 inline drift fix)** | v1.5 prose says: "At v1.5 the marker holds a string reference (typically the F2 entry hash or a constructed action_id like `cp-audit:<cp_action_id>` per the CP-sourced sub-namespace recognition at §24.6)." v1.6 amends to: "At v1.6 the marker holds a string reference (typically the F2 entry hash or a constructed action_id like `dispatch:<parent_action_id>:<child_index>` per the runtime spec §14.7.2 step 8b canonical pattern for sub-agent dispatch F2-write composition)." | Adversarial-review F1-02 (OD spec §24.4 example diverged from runtime spec §14.7.2 step 8b canonical pattern); runtime spec v1.7 §14.7.2 step 8b (canonical `dispatch:<parent_action_id>:<child_index>` format); landed code at `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py:468-470` (`_compose_and_persist_audit` 8b helper) |
| **§24.5 `compute_entry_hash` canonical helper — NEW NOTE (F2-04 absorption)** | v1.5 §24.5 declares the canonical helper signature + recipe; v1.6 adds NEW NOTE clarifying that **helper materialization at the OD axis package is deferred to a follow-on arc**. Converters MAY inline the recipe in the interim under the spec-canonical recipe constraint — the recipe is byte-equivalent to the canonical helper. The current production callsite (`harness-cxa/src/harness_cxa/cp_audit_conversion.py:_compute_entry_hash`) inlines the recipe; future OD-package helper materialization closes the inline drift risk. | Adversarial-review F2-04 (OD spec §24.5 canonical helper declared in spec only; not materialized at `harness-od/src/`; converter at `harness-cxa/` duplicates the recipe locally); spec-anchored recipe per ADR-D5 v1.4 §1.4.1 + this v1.5 §24.5 unchanged |

**Sections preserved verbatim from v1.5.** All v1.5 content outside the §24.4 example-format sentence + §24.5 NEW NOTE preserved unchanged. §24.1 + §24.2 + §24.3 + §24.5 helper signature + §24.6 CP-sourced audit-entry recognition + filing footer all stand. The §24.5 helper signature + recipe + Authority block preserved verbatim from v1.5; only the NEW NOTE appended.

**Contract count.** OD axis contract count preserved at **24** at v1.6 (C-OD-24 unchanged — only NOTE absorption + example-format correction).

**Status posture.** `Status: Proposed` preserved per workspace discipline. v1.6 is a Form A citation-precision + NOTE-absorption patch — no signature change, no contract re-decomposition, no acceptance criterion change.

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

### §24.5 `compute_entry_hash` canonical helper (v1.6 NEW NOTE)

[Helper signature + recipe + Authority block preserved verbatim from v1.5.]

**NOTE — helper materialization at the OD axis package (v1.6 added).** The §24.5 canonical helper signature + recipe is spec-anchored at v1.5; **materialization at the `harness-od` axis package is deferred to a follow-on arc.** As of v1.6, no `def compute_entry_hash` function exists at `harness-od/src/harness_od/`; the canonical recipe is materialized only inline at the production CP→OD converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py:_compute_entry_hash`. Converters MAY inline the recipe in the interim under the constraint that the inlined implementation IS byte-equivalent to the canonical helper recipe (SHA-256 over `payload.model_dump_json()`). Future drift risk: if the OD-axis recipe is amended (e.g., to a different canonicalization), inlined call-site duplicates would silently diverge — this is the substantive cost of the deferred materialization. The follow-on arc closes the drift risk by (a) materializing `compute_entry_hash` at the OD package + (b) refactoring `harness-cxa/src/harness_cxa/cp_audit_conversion.py` to import from `harness_od`.

Adversarial-review F2-04 absorbed at this NOTE. The path (i) disposition (operator-ratified 2026-05-20) preserves the current implementation behavior + documents the gap.

[§24.6 CP-sourced audit-entry recognition preserved verbatim from v1.5.]

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Operational_Discipline_v1_6.md` |
| Status | Proposed — Phase 7 7b/7c in-CLI Form A NOTE-absorption patch (path (i) of adversarial-review disposition) |
| Predecessor | `Spec_Operational_Discipline_v1_5.md` — preserved verbatim except §24.4 example sentence + §24.5 NEW NOTE |
| Substrate consumed | `.harness/adversarial_review_u_rt_59_fork_2_spec_bundle.md` (F1-02 + F2-04 findings); runtime spec v1.7 §14.7.2 step 8b (canonical action_id format); landed converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` (inlined recipe verified byte-equivalent) |
| Co-published with | `Spec_Control_Plane_v1_9.md` (path (i) CP-side NOTE absorption at §13.5.1) + `Spec_Harness_Runtime_v1.md` v1.8 (path (i) runtime-side NOTE absorption at §14.7.2 step 8a + step 8b actor-field inline fix) |
| Successor | Workspace `CLAUDE.md` §2.3 OD row version bump (v1.5 → v1.6); follow-on OD-package helper materialization arc (closes F2-04 drift risk) |
| Revision policy | In-CLI per workspace discipline (`CLAUDE.md` §4.3) |
| Date | 2026-05-20 |

*Filed at Phase 7 sub-phase 7b/7c as the OD-side Form A patch absorbing adversarial-review path (i) NOTE-form disposition. §24.4 example format corrected to canonical `dispatch:<parent_action_id>:<child_index>` (F1-02 closed); §24.5 NEW NOTE documents helper materialization deferral (F2-04 absorbed). Co-published with CP spec v1.9 + runtime spec v1.8 as the single-arc path (i) ratification landing.*
