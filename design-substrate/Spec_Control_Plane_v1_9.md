# Specification — Control Plane v1.9

## Change-note (v1.8 → v1.9)

**Scope of revision.** Form A NOTE-absorption patch over v1.8 absorbing the operator-ratified path (i) disposition from `.harness/adversarial_review_u_rt_59_fork_2_spec_bundle.md` (2026-05-20). v1.9 lands three new NOTEs at §13.5.1 (NOTE 4 + NOTE 5 + NOTE 6) addressing adversarial-review findings F2-01 (cross-side join non-uniqueness) + F2-02 (HITL palette repurposing convention) + F2-05 (brief_hash discard). v1.8's §13.5.1 NOTE 1 + NOTE 2 + NOTE 3 preserved verbatim. No signature change; no field-projection table change; no contract content removed or modified.

**Three new NOTE sites.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **§13.5.1 NEW NOTE 4 (sibling distinguishability — F2-01)** | Documents that `audit.cp.action_id` projected from `CPAuditLedgerEntry.action_id` is **non-unique across sub-agent siblings** of the same parent (current shape: `<parent_action_id>\|\|sub-agent` per `harness-cp/src/harness_cp/sub_agent_gate_level_descent.py:199` — no `descent.child_index` and no `brief_hash` carried into the entry's identity). Sibling-distinguishable cross-side CP↔OD join is via `payload.entry_core: StateLedgerEntryRef` (per OD spec v1.6 C-OD-24.4) which resolves to the F2 dispatch-entry action_id pattern `dispatch:<parent_action_id>:<child_index>` (per runtime spec v1.8 §14.7.2 step 8b). Audit-trace consumers querying for siblings of a given parent MUST use `entry_core` as the discriminator. The field-projection table row 1 commitment ("Anchor for CP↔OD cross-side join — names the CP action this audit entry corresponds to") holds at the *parent* granularity; sibling granularity requires the IS-anchored entry_core. | Adversarial-review F2-01 (cross-side join non-uniqueness across siblings — verified at code); operator-ratified path (i) NOTE-form disposition 2026-05-20 |
| **§13.5.1 NEW NOTE 5 (dispatch repurposing convention — F2-02)** | Documents that the `CPAuditLedgerEntry` shape (declared at C-CP-16 §16.2 — the HITL per-response audit shape with `response ∈ {approve, edit, reject, respond}` per C-CP-16 §16.1 4-response palette) is **reused for sub-agent dispatch via the convention `response="approve"`** per `harness-cp/src/harness_cp/sub_agent_gate_level_descent.py:194-201` docstring + line 197 (`response="approve"`). Semantic discrimination at OD audit-trace consumers ("operator approved at HITL" vs "sub-agent dispatched") is by composite check: (a) `audit.cp.*` namespace presence indicates CP source; (b) `entry_core` resolves to a `dispatch:*` action_id pattern indicates dispatch source (per runtime spec v1.8 §14.7.2 step 8b); (c) HITL-source entries resolve to non-`dispatch:*` action_id patterns. The field-projection table row 3 (`response` → `audit.cp.response`) is a verbatim pass-through; the dispatch-vs-HITL discriminator lives at the action_id pattern, not at the `response` field value. Future structural extension (path (ii) of adversarial-review disposition — separate `CPDispatchAuditLedgerEntry` carrier) deferred per operator path-(i) ratification. | Adversarial-review F2-02 (HITL palette repurposed for dispatch via undocumented convention); operator-ratified path (i) NOTE-form disposition 2026-05-20 |
| **§13.5.1 NEW NOTE 6 (brief_hash not in field projection — F2-05)** | Documents that the `brief_hash` parameter at `compose_dispatch_audit(parent_action_id, descent, brief_hash)` (per runtime spec v1.8 §14.7.2 step 8a) is **consumed for in-memory dispatch-response-hash computation** (per `harness_cp.sub_agent_gate_level_descent.sub_agent_dispatch_response_hash`) but is **NOT persisted to the audit ledger at v1.7/v1.8 MVP**. The `_ = brief_hash` discard idiom at `emit_sub_agent_dispatch_audit:198` reflects the contract: brief_hash is a deduplication / response-correlation surface, not an audit-trail-keying surface. The CP §13.5.1 field-projection table intentionally does NOT include a `brief_hash → audit.cp.brief_hash` projection row at v1.9 — brief_hash persistence to the audit ledger is deferred to a fan-out arc landing where multi-sibling dispatch makes brief-vs-sibling-keying load-bearing. The runtime spec v1.7 dispatch-fact-key narrative claim (`(parent_action_id, descent, brief_hash)`) is amended at runtime spec v1.8 NOTE absorption to reflect the v1.7/v1.8 MVP reduced key shape. | Adversarial-review F2-05 (brief_hash discarded; spec dispatch-fact key claim unmoored); operator-ratified path (i) NOTE-form disposition 2026-05-20 |

**Sections preserved verbatim from v1.8.** All v1.8 content outside the three NEW NOTE paragraphs at §13.5.1 preserved unchanged. C-CP-13 §13.5 (LedgerEntryRef — preserved from v1.2) stands. §13.5.1 converter contract signature + field-projection table + namespace + Q1 + Q2(a) + Q4 + Q5 commitments + NOTE 1 (v1.8 entry_hash canonicalization RESOLVED) + NOTE 2 (v1.8 composer step F2-write specification RESOLVED) + NOTE 3 (cryptographic-payload-mismatch foreclosure) all preserved verbatim. v1.6 §25.2 + §25.3.3.4 + §25.7 + §25.9 + the rest of v1.6 + v1.5 + v1.4 + v1.3 + v1.2 + v1.1 + v1 chain all preserved.

**Status posture.** Proposed (v1.8) → **Proposed (v1.9)**. v1.9 is a Form A NOTE-absorption patch — no signature change, no contract re-decomposition, no acceptance criterion change.

**Downstream absorption owed (post-v1.9).** (a) Workspace `CLAUDE.md` §2.3 CP row version bump (v1.8 → v1.9); (b) `Spec_Operational_Discipline_v1_6.md` co-published this turn (OD-side NOTE absorption — F1-02 + F2-04); (c) `Spec_Harness_Runtime_v1.md` v1.8 co-published this turn (runtime-side NOTE absorption — F2-01 + F2-02 + F2-03 + F2-05 + F1-01 inline fix). Co-publication is single-arc per the path (i) ratification.

---

## Status block

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_9.md` |
| Status | **Proposed** — Phase 7 sub-phase 7b/7c in-CLI Form A NOTE-absorption patch |
| Revision | v1 → v1.1 → v1.2 → v1.3 → v1.4 → v1.5 → v1.6 → v1.7 (U-RT-59 Fork 2 Path D — §13.5.1 converter contract) → v1.8 (Form A — v1.7 §13.5.1 NOTE 1 + NOTE 2 references resolved post Path B-revised-a + runtime v1.7 landings) → **v1.9 (Form A — adversarial-review path (i) NOTE-form absorption: NOTE 4 sibling distinguishability + NOTE 5 dispatch repurposing convention + NOTE 6 brief_hash projection-table absence, 2026-05-20)** |
| Revision date | 2026-05-20 (v1.9 Form A patch, same day as v1.8 and the adversarial review) |
| Phase | 7 — sub-phase 7b/7c; in-CLI per workspace `CLAUDE.md` §4.3 |
| Skill | `spec-writer` (Form A NOTE-absorption sub-mode) at v1.9 |
| Predecessor | `Spec_Control_Plane_v1_8.md` (Form A — v1.7 §13.5.1 NOTE 1 + NOTE 2 references resolved) — preserved verbatim except for the three NEW NOTE 4/5/6 paragraphs at §13.5.1 |
| Co-published with | `Spec_Operational_Discipline_v1_6.md` (path (i) OD-side absorption); `Spec_Harness_Runtime_v1.md` v1.8 (path (i) runtime-side absorption) |
| Substrate consumed | All v1.8 inputs (preserved) + `.harness/adversarial_review_u_rt_59_fork_2_spec_bundle.md` (F2-01 + F2-02 + F2-05 findings); landed code at `harness-cp/src/harness_cp/sub_agent_gate_level_descent.py` (`emit_sub_agent_dispatch_audit` — implementation behavior documented by NOTEs); landed converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` (field-projection behavior preserved at v1.9) |
| Exit gate | Workspace `CLAUDE.md` §2.3 CP row version bump (v1.8 → v1.9) |

---

## §13 C-CP-13 — Sub-agent handoff context + audit-trail-link composition

[All content preserved verbatim from v1.8. §13.1 + §13.2 + §13.3 + §13.4 + §13.5 (LedgerEntryRef) unchanged from v1.2. §13.5.1 converter contract signature + field-projection table + commitments + NOTE 1 (v1.8 RESOLVED) + NOTE 2 (v1.8 RESOLVED) + NOTE 3 preserved verbatim from v1.8. NEW NOTE 4 + NOTE 5 + NOTE 6 appended at v1.9 below.]

### §13.5.1 CP→OD audit-write composition — `cp_audit_to_od_audit` converter contract (v1.7 NEW; v1.8 NOTE 1 + NOTE 2 RESOLVED; v1.9 NOTE 4 + NOTE 5 + NOTE 6 added)

[Signature + Field-projection table + Namespace commitment + Q1 + Q2(a) + Q4 commitments + Converter home + NOTE 1 (v1.8 RESOLVED) + NOTE 2 (v1.8 RESOLVED) + NOTE 3 (cryptographic-payload-mismatch foreclosure) + Cross-axis citation + Deferred-to-implementation-discretion all preserved verbatim from v1.8.]

**NOTE 4 — Sibling distinguishability across the cross-side CP↔OD join (v1.9 NEW; F2-01 absorption).** The field-projection table row 1 commitment (`action_id → audit.cp.action_id` — "Anchor for CP↔OD cross-side join — names the CP action this audit entry corresponds to") holds at the **parent granularity**: a query "find the CP audit entry corresponding to this parent action" via `audit.cp.action_id` resolves uniquely to the CP source. For **sub-agent dispatch with multiple siblings of the same parent**, `audit.cp.action_id` is non-unique — the current shape per `harness-cp/src/harness_cp/sub_agent_gate_level_descent.py:199` is `<parent_action_id>||sub-agent` with no `descent.child_index` discrimination. **Sibling-granular cross-side join MUST use `payload.entry_core: StateLedgerEntryRef`** (per `Spec_Operational_Discipline_v1_6.md` C-OD-24.4) which resolves to the F2 dispatch-entry action_id pattern `dispatch:<parent_action_id>:<child_index>` (per `Spec_Harness_Runtime_v1.md` v1.8 §14.7.2 step 8b). Operationally: audit-trace consumers querying for a specific sibling MUST go through `entry_core` → IS state-ledger F2 entry; `audit.cp.action_id` is the parent-granularity discriminator only.

At v1.7/v1.8 MVP scope (single-sub-agent per parent per spec §14.7 fan-out-emission foreclosure), the non-uniqueness is latent — at most one sibling per parent — and the implementation behavior is correct. The NOTE documents the v1.9 contract for future-load scenarios (fan-out arc landing). Path (ii) of the adversarial-review disposition (extend `CPAuditLedgerEntry` with `child_index` / `brief_hash` fields OR introduce `CPDispatchAuditLedgerEntry` carrier) is deferred per operator path-(i) ratification.

**NOTE 5 — Sub-agent dispatch repurposing of HITL response palette via `response="approve"` convention (v1.9 NEW; F2-02 absorption).** The `CPAuditLedgerEntry` shape is declared at C-CP-16 §16.2 as the HITL per-response audit shape — `response: str ∈ {approve, edit, reject, respond}` per the C-CP-16 §16.1 4-response palette (operator response to a HITL gate). For sub-agent dispatch, this carrier is **reused via the convention `response="approve"`** per `harness-cp/src/harness_cp/sub_agent_gate_level_descent.py:197` (docstring at lines 194-201: "A sub-agent dispatch is recorded as an `approve` response (no operator edit/reject/respond), so the three response-specific hash fields are absent").

The convention is a structural reuse, not a semantic claim — a sub-agent dispatch is NOT a HITL approve event. **Semantic discrimination at OD audit-trace consumers** between the two source events is by composite check:
1. **`audit.cp.*` namespace presence** identifies CP source (HITL or dispatch).
2. **`payload.entry_core` resolves to a `dispatch:*` action_id pattern** (per `Spec_Harness_Runtime_v1.md` v1.8 §14.7.2 step 8b) identifies **dispatch source**.
3. **`payload.entry_core` resolves to a non-`dispatch:*` action_id pattern** identifies **HITL source** (HITL F2-write composition is C-CP-16-owned; HITL F2 entries do not carry the `dispatch:` prefix).

The field-projection table row 3 (`response → audit.cp.response`) is a verbatim pass-through; the dispatch-vs-HITL discriminator lives at the F2 entry action_id pattern, not at the `audit.cp.response` field value. Path (ii) of the adversarial-review disposition (separate `CPDispatchAuditLedgerEntry` carrier sum-typed against HITL `CPAuditLedgerEntry`) is deferred per operator path-(i) ratification.

**NOTE 6 — `brief_hash` consumed in-memory; not in v1.7/v1.8/v1.9 field-projection table (v1.9 NEW; F2-05 absorption).** The `brief_hash` parameter at `compose_dispatch_audit(parent_action_id, descent, brief_hash)` (per `Spec_Harness_Runtime_v1.md` v1.8 §14.7.2 step 8a) is **consumed at the in-memory dispatch-response-hash computation** (per `harness_cp.sub_agent_gate_level_descent.sub_agent_dispatch_response_hash` — SHA-256 over canonicalized `SubAgentBrief` per C-CP-12 §12.5). The hash is used at runtime for dispatch deduplication / response-correlation purposes; it is **NOT persisted to the OD audit ledger at v1.7/v1.8/v1.9 MVP**.

The §13.5.1 field-projection table **intentionally does NOT include a `brief_hash → audit.cp.brief_hash` projection row** at v1.9 — brief_hash persistence to the audit ledger is deferred to a fan-out arc landing where multi-sibling dispatch makes brief-vs-sibling-keying load-bearing (the brief content determines which sibling-instance the dispatch corresponds to; at MVP single-sibling scope, parent-action-id + child-index suffices).

The discard idiom at `emit_sub_agent_dispatch_audit:198` (`_ = brief_hash`) reflects the v1.9 contract: brief_hash is a runtime deduplication surface, not an audit-persistence surface. The runtime spec v1.7 step 8a narrative claim "audit entries are dispatch-fact records keyed by `(parent_action_id, descent, brief_hash)` per C-CP-12 §12.5" is amended at `Spec_Harness_Runtime_v1.md` v1.8 to reflect the v1.7/v1.8/v1.9 MVP reduced key shape — the persistent audit-key is `(parent_action_id, "approve")` at the CP entry layer + IS-anchored `entry_core` for sibling distinguishability. Path (ii) of the adversarial-review disposition (extend CP entry shape with `brief_hash`) is deferred per operator path-(i) ratification.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_9.md` |
| Status | Proposed — Phase 7 7b/7c in-CLI Form A NOTE-absorption patch (path (i) of adversarial-review disposition) |
| Predecessor | `Spec_Control_Plane_v1_8.md` (Form A — v1.7 §13.5.1 NOTE 1 + NOTE 2 RESOLVED) — preserved verbatim except for the three NEW NOTE 4/5/6 paragraphs at §13.5.1 |
| Co-published with | `Spec_Operational_Discipline_v1_6.md` (path (i) OD-side absorption: §24.4 example format + §24.5 helper materialization NOTE) + `Spec_Harness_Runtime_v1.md` v1.8 (path (i) runtime-side absorption: §14.7.2 step 8a NOTE absorption + step 8b F1-01 inline fix) |
| Substrate consumed | v1.8 inputs (preserved) + adversarial-review report (F2-01 + F2-02 + F2-05 findings); landed code at `harness-cp/src/harness_cp/sub_agent_gate_level_descent.py` (`emit_sub_agent_dispatch_audit`) + converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` (field-projection behavior preserved at v1.9) |
| Successor | Workspace `CLAUDE.md` §2.3 CP row version bump (v1.8 → v1.9); future fan-out arc absorbs the NOTE 4/5/6 deferred-to-fan-out commitments (sibling-distinguishable join via entry_core; dispatch carrier separation per path (ii); brief_hash persistence) |
| Revision policy | In-CLI per workspace discipline (`CLAUDE.md` §4.3) |
| Date | 2026-05-20 |

*Filed at Phase 7 sub-phase 7b/7c as the CP-side Form A NOTE-absorption patch closing adversarial-review findings F2-01 + F2-02 + F2-05 under operator-ratified path (i). v1.8 substantive content + NOTE 1 + NOTE 2 + NOTE 3 preserved verbatim; only three NEW NOTE 4/5/6 paragraphs appended at §13.5.1. Pure citation-precision + NOTE-absorption delta; no signature change; no field-projection table change. Co-published with OD spec v1.6 + runtime spec v1.8 as single-arc path (i) ratification landing.*
