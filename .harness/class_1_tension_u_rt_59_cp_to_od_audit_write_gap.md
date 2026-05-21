# Class 1 Tension: CP→OD audit-write composition gap (U-RT-59 AC #9 write half STRUCK)

**Class:** 1 — halt-route-split (partial-landing per `[[halt-route-split-AC-pattern]]`).
**Filed:** 2026-05-20, Phase 7 sub-phase 7b, U-RT-59 landing arc.
**Status:** OPEN-PARTIAL (updated 2026-05-20) — partial-landing absorbed at U-RT-59 (AC #9 write half STRUCK); Path D CP-side spec landed at `ee5ae21` (CXA v2.4 + CP spec v1.7 §13.5.1 converter contract); OD-side drift resolution arc owed (Path B-revised-a / Path B-revised-b / Path A-revised — operator selection pending); runtime spec amendment + composer wiring + AC #9 un-strike + converter code-move to `harness-cxa/` owed to implementation arc.

**Discovery filed 2026-05-20:** scoping report + prototype converter + round-trip-through-OD-signing test at `.harness/u_rt_59_fork_2_cp_to_od_audit_discovery.md` (+ `harness-runtime/src/harness_runtime/lifecycle/cp_audit_conversion.py` + `harness-runtime/tests/test_cp_audit_conversion.py`). DISCOVERY-GRADE; not wired. 5 open spec-level sub-questions (Q1–Q5) surfaced for operator ratification before spec amendments / runtime wiring proceed.

**Path D landed 2026-05-20** — CP-side spec-anchored surfaces only: `Cross_Axis_Composition_Document_v2_4.md` (new §2.3.7 CP→OD bucket; U-CP-28 → U-OD-00 typed-seam edge) + `Spec_Control_Plane_v1_7.md` (new §13.5.1 `cp_audit_to_od_audit` converter contract).

**Path B-revised-a (OD-side drift resolution) landed 2026-05-20** — co-published `ADR-D5.md` v1.4 (§1.4 storage-form prose retargeted from SQLite to JSONL via IS composition + §1.4.1 entry_hash recipe tightened to SHA-256 over AuditPayload.model_dump_json) + `Spec_Operational_Discipline_v1_5.md` (new C-OD-24 contract lifting code-canonical AuditPayload + AuditLedgerEntry + AuditLedger + StateLedgerEntryRef + compute_entry_hash + §24.6 CP-source recognition). Pre-existing X-AL-3 drift surfaced at discovery report §9 + §10 RETIRED at v1.5 §24. Citation chain finding (c11-operator-local SKILL.md missing) flagged as Class 3 at ADR-D5 v1.4 change-note.

**Runtime spec v1.7 + CP spec v1.8 Form A patch landed 2026-05-20** (this turn) — `Spec_Harness_Runtime_v1.md` v1.7 §14.7.2 step 8 replaced with Path D + B-revised-a 4-substep sequence (8a CP audit compose + 8b F2-write of dispatch action + 8c CP→OD convert + 8d audit_writer.append); `Spec_Control_Plane_v1_8.md` Form A patch resolves v1.7 §13.5.1 NOTE 1 + NOTE 2 references. Class 3 drift item 1 (`ctx.audit_ledger_writer` → `ctx.audit_writer`) RESOLVED at step 8d rewrite (residual at §14.7.6 carried).

**Still owed (implementation arc — code wiring + plan absorptions only; all spec authority now landed):** un-strike U-RT-59 AC #9 write half at `.harness/phase-2-session-3-track-a-atomic-decomposition.md` v2.6; composer wiring at `RuntimeSubAgentDispatcher` (constructor extension + step 8a–8d body); F2-write site (new); converter code-move from `harness-runtime/lifecycle/cp_audit_conversion.py` → `harness-cxa/src/harness_cxa/cp_audit_conversion.py` per Q5; integration test (parent + 3-step child + audit-chain `verify_hash_chain_integrity`); CP plan v2.13 → v2.14 absorption at U-CP-28; OD plan v2.11 → v2.12 absorption at U-OD-00; workspace CLAUDE.md §2.3 contract count update (OD 23 → 24).

---

## Surfacing event

U-RT-59 plan AC #9 (Implementation_Plan_Harness_Runtime_v2.5 L9-ter): "audit-entry composition + emission verified — composer calls `ctx.handoff_registry.compose_dispatch_audit(...)` per spec §14.7.6; resulting `CPAuditLedgerEntry` is **appended to `ctx.audit_writer`**; verify entry contains the dispatch-response-hash join key per C-CP-13 §13.5; verify entry's `child_result_status` matches the §14.7.2 step 7 mapping result."

Spec §14.7.2 step 8 reinforces: "v1.6 emits via `ctx.audit_writer.append(tenant_id=step_context.tenant_id, audit_entry=audit_entry) -> WriteResult` (real 2-param signature per `harness_runtime.lifecycle.audit_writer.RuntimeAuditLedgerWriter.append`; `step_context.tenant_id` is `None` at v1.6 MVP per `Spec_Control_Plane_v1_6.md` §25.2.1)."

**Structural mismatch surfaced at AC #9 implementation:**

- `compose_dispatch_audit(parent_action_id, descent, brief_hash) → CPAuditLedgerEntry` (CP-shape; from `harness-cp/src/harness_cp/per_step_override_evaluator.py:48`):
  - 6 fields: `action_id`, `gate_level`, `response`, `edited_proposal_hash | None`, `rejection_reason_hash | None`, `response_text_hash | None`
  - Per-response-conditional hash fields (factor-out of C-CP-16 §16.2 per-response audit-ledger entry table)
- `ctx.audit_writer.append(tenant_id, audit_entry: AuditLedgerEntry)` (from `harness-runtime/src/harness_runtime/lifecycle/audit_writer.py:107`):
  - Takes **OD-shaped** `AuditLedgerEntry` (from `harness-od/src/harness_od/audit_ledger_types.py:108`)
  - 3 fields: `payload: AuditPayload`, `signature_attrs: AuditSignatureAttributes`, `entry_hash: str`
  - Pre-signed via `sign_audit_entry` at OD emission site (`harness-od/src/harness_od/multi_tenant_trace_separation_and_audit_ledger.py`)

**The two types are structurally distinct.** No CP→OD audit-shape converter exists at HEAD. Calling `ctx.audit_writer.append(tenant_id, cp_audit_entry)` would fail with a Pydantic ValidationError at runtime + a pyright type error at static analysis.

This is the **same family** as `[[fork-cp-is-wiring-gaps]]` (DEFERRED 2026-05-20 Path D): "needs CP composer authoring — Phase 6 work, not runtime". The CP→OD audit-write composition is one of the unwired cross-axis composition seams owed to a future Phase 6 CP-plan / OD-plan / CXA arc.

---

## Routing per `Project_Workflow_v1_8.md` §2.7.6

**Class 1.** Architectural defect at the CP→OD cross-axis composition seam: the CP-side audit composer (`compose_dispatch_audit`) produces a CP-shaped record; the OD-side audit writer (`audit_writer.append`) consumes an OD-shaped record; no converter is specified at any design-phase artifact (CP spec v1.6 / OD spec v1.4 / CXA v2.3 / ADD v1.3).

**Halt-route-split absorbed at landing.** Per `[[halt-route-split-AC-pattern]]` discipline + operator ratification 2026-05-20:
- AC #9 **compose half** LANDS at U-RT-59: composer calls `handoff_registry.compose_dispatch_audit(...)` and produces `CPAuditLedgerEntry` (verified in `test_lifecycle_sub_agent_dispatch.py::test_audit_entry_composed_via_handoff_registry`).
- AC #9 **write half** STRUCK at v1.6 MVP: composer does NOT call `ctx.audit_writer.append(...)`. The `CPAuditLedgerEntry` is composed inline (for retirement-criterion-B evidence on H_T-CP-13 schema enforcement) but discarded after composition (no write site to consume it at v1.6).
- `RuntimeSubAgentDispatcher.__init__` deliberately does NOT take an `audit_writer` parameter — structurally foreclosed at v1.6 MVP per the partial-landing scope.

**Resolution surface (Phase 6 design-phase authoring arc owed):**

| Path | Description | Cost surface |
|---|---|---|
| **A — CP→OD audit converter** | Author `cp_audit_to_od_audit(cp_entry, *, tenant_id, signing_backend) → AuditLedgerEntry` at `harness-od/src/harness_od/cp_audit_conversion.py` (or analogous). Specifies the field-by-field projection (CP `action_id` → OD `AuditPayload.action_id`; CP `gate_level` / `response` / hash fields → OD `AuditPayload` body) + signing via existing OD `sign_audit_entry`. Add converter call at the U-RT-59 composer step 8. | Medium — requires CP spec v1.7 §13.5 amendment ("CP→OD audit-write composition"), OD spec v1.4 amendment ("CP-sourced audit entries"), CXA v2.4 new edge (CP §13.5 → OD `audit_writer`) |
| **B — CP-side audit writer** | Author a CP-side audit writer (`harness-cp/.../cp_audit_writer.py`) that persists `CPAuditLedgerEntry` to a separate ledger (no IS chain join via OD `audit_writer`). Spec-revision: split audit ledger into CP-side + OD-side substrate. | Large — touches ADR-D5 + ADD + multiple spec revisions; recommended NOT preferred (loses OD substrate join) |
| **C — typed-union audit writer** | Revise `audit_writer.append` to accept `Union[CPAuditLedgerEntry, AuditLedgerEntry]`; converter inside the writer dispatches based on type. | Medium — OD spec amendment only |

Recommended at follow-on arc: **Path A** (most consistent with the existing OD-substrate-anchored audit-ledger architecture; CXA edge cleanly specifies the cross-axis seam).

---

## Workspace progress impact

**U-RT-59 lands** (partial — AC #9 write half STRUCK):
- `RuntimeSubAgentDispatcher.dispatch` composes `CPAuditLedgerEntry` at step 8 via `self.handoff_registry.compose_dispatch_audit(...)`.
- The composed entry is bound to `_ = audit_entry` (discarded) — no write site.
- Failed-path branches also compose the entry before raising (preserves dispatch-fact record at the point of failure even though it's not persisted).
- Test verification: `test_audit_entry_composed_via_handoff_registry` confirms composer reaches the composition site without raising; `test_audit_entry_not_written_via_ctx_audit_writer_v1_6_mvp` confirms structural foreclosure of the write side (audit_writer NOT a constructor parameter).

**Retirement events at AC #12** (filed in `phase-7d-retirement-events-batch-4.md`):
- H_T-CP-13 RETIRED for **typed-schema enforcement** at production callsite (Pydantic v2 validation at `SubAgentDispatchPayload` + at `HandoffContext` construction + at `CPAuditLedgerEntry` composition).
- H_T-CP-13 retirement does NOT include the audit-write end-to-end criterion — that surface is owed.
- Downstream `audit.*` namespace retirement events at the next Phase 6 CP-composer-authoring arc will close the OD-side write path.

---

## Related forks

- `[[fork-cp-is-wiring-gaps]]` — DEFERRED Path D (Phase 6 CP-composer authoring work). This U-RT-59 audit-write fork joins that DEFERRED family — both are CP-composer-authoring residuals at the cross-axis composition seam.
- `[[fork-cost-record-audit-ledger-wiring-residual]]` — OPEN Class 3 bounded residual (SpanCostRecord audit-ledger wiring). Same shape: CP-side produces typed record, OD-side audit-ledger consumes a different shape, converter not specified at design phase.

---

## Filing footer

| Field | Value |
|---|---|
| Filed by | sub-agent dispatch composer landing arc (U-RT-59 implementation session) |
| Operator ratification | 2026-05-20 (halt-route-split selection per AskUserQuestion: "Halt-route-split AC #9; land compose-only; file Class 1") |
| Resolution target | Phase 6 CP-composer-authoring arc; recommended Path A (CP→OD audit converter at `harness-od/` with CXA edge specification) |
| Re-evaluation trigger | When the Phase 6 CP-composer-authoring arc opens OR when the next `[[fork-cp-is-wiring-gaps]]` Path D resolution arc is opened (paired resolution recommended) |
