# Class 1 Tension: CP→OD audit-write composition gap (U-RT-59 AC #9 write half STRUCK)

**Class:** 1 — halt-route-split (partial-landing per `[[halt-route-split-AC-pattern]]`).
**Filed:** 2026-05-20, Phase 7 sub-phase 7b, U-RT-59 landing arc.
**Status:** OPEN — partial-landing absorbed at U-RT-59 (AC #9 write half STRUCK); root-cause resolution owed to Phase 6 CP-composer-authoring arc.

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
