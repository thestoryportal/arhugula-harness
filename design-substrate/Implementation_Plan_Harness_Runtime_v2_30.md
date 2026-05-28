# Implementation Plan — Harness Runtime (v2.30)

*Delta over v2.29. v2.30 is a paired single-unit-body canonical-reading amendment at U-RT-94 (the `WebhookDeliveryComposer` carrier class — runtime spec v1.26 §14.10.1 / now v1.34 §14.10.1) + U-RT-97 (the `materialize_webhook_delivery_composer_stage` factory unit — runtime spec v1.26 §14.16.2 / now v1.34 §14.16.2) absorbing the v1.34 ratified Class 1 fork resolution Reading A per `.harness/class_1_fork_webhook_composer_per_workflow_context_threading.md` Q-set 2026-05-28. Unit count 99 → 99 (unchanged); ZERO new units; ZERO new cluster; ZERO DAG topology change; ZERO cross-axis cascade per Q4 ratification.*

## §0 Change note (v2.29 → v2.30)

### §0.1 Revision context — U-RT-94 + U-RT-97 absorbing runtime spec v1.34 §14.10.1 + §14.16.2 signature widening

Per `.harness/class_1_fork_webhook_composer_per_workflow_context_threading.md` Reading (A) operator-ratified 2026-05-28 Q-set + co-publication at this arc with runtime spec v1.33 → v1.34 NEW §14.10.1 `WebhookDeliveryComposer` ctor strip + `deliver_webhook` signature widening + §14.16.2 factory signature widening + harness-runtime impl + batch-29 retirement event filing (OD-5 surface-coverage doc-hygiene refresh; RETIRE-READY status preserved; deployment-time gate per AS-8d precedent unchanged).

U-RT-94 (the `WebhookDeliveryComposer` carrier class body unit landed at runtime spec v1.26 §14.10.1 + impl at `harness-runtime/src/harness_runtime/lifecycle/webhook_delivery_composer.py:94`) accepts a refactored signature shape:

- **Ctor strip:** 4 fields REMOVED from `__init__`: `workflow_id` / `parent_action_id` / `parent_idempotency_key` / `tenant_id`. Composer becomes stateless w.r.t. workflow scope. Retains 5 retry/HTTP/test-injection params (`retry_max_attempts` / `retry_base_delay_seconds` / `tracer_provider` / `http_client_factory` / `sleep_fn`) + 3 cost-attribution substrate kw-only params (`rate_table` / `cost_chain` / `audit_writer` — bootstrap-singleton lifetime preserved).
- **`deliver_webhook(...)` signature widening:** `deliver_webhook(brief, idempotency_key)` → `deliver_webhook(brief, idempotency_key, *, workflow_id, parent_action_id, parent_idempotency_key, tenant_id=None)`. 4 NEW kw-only per-call params (`tenant_id` defaults `None` for single-tenant deployments per CP spec v1.22 binding-fix precedent; other 3 required).
- **`_attribute_webhook_cost_best_effort(...)`:** Method signature refactored to consume per-call values not instance state. Per-call params flow from `deliver_webhook` down to `attribute_webhook_dispatch_cost(...)` invocation.

U-RT-97 (the `materialize_webhook_delivery_composer_stage` factory unit landed at runtime spec v1.26 §14.16.2) accepts the cost-attribution threading shape:

- NEW optional kw-only params: `rate_table: RateTable | None = None`, `cost_chain: CostAttributionChain | None = None`, `audit_writer: AuditLedgerWriter | None = None`
- When ALL 3 substrates bound: factory threads them through `WebhookDeliveryComposer(rate_table=..., cost_chain=..., audit_writer=...)` ctor on opt-in branch
- When any substrate is `None`: cost-attribution disabled (composer constructed without cost substrates; preserves pre-v1.34 default-off behavior)
- Mirror validator factory mechanism (a) per runtime spec v1.18 §14.13.7 ratification at U-OD-40

Stage-5 LOOP_INIT invocation at `bootstrap/stage_5_loop_init.py` passes `ctx.rate_table` (NOTE: see §0.4 sub-axis on where rate_table is bound) + `ctx.cost_chain` + `ctx.audit_writer` to the factory (analogous to `stage_4_od.py:89` validator factory invocation post-U-OD-40).

### §0.2 Sections revised

§0 (this change note); U-RT-94 + U-RT-97 canonical-reading amendment tables for signature + AC + Tests-line refresh. All other unit bodies preserved verbatim from v2.29 per delta-only-plan-chain convention.

### §0.3 Production caller update site (cross-cluster awareness)

Per Q3 ratification: production caller at `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py:1002` updates to pass per-call workflow context kwargs sourced from `step_context.*`:

- `workflow_id=step_context.workflow_id` (per CP spec v1.12 §25.2.1 9th-field absorption)
- `parent_action_id=step_context.parent_action_id` (precedent at lines 488/876 within `dispatch` method scope)
- `parent_idempotency_key=step_context.parent_idempotency_key` (precedent at lines 465/508 within sibling code paths)
- `tenant_id=step_context.tenant_id` (precedent at line 792)

All 4 axes empirically verified in scope at the call site via `step_context` kw-param at `dispatch` method (line 810). This is intra-runtime-spec (the call site is at the `HITLGateComposer.dispatch` method body; not a separate atomic unit). Out-of-AC change at U-RT-94 implementation-discretion scope per FM-2 single-focus arc.

### §0.4 Sub-axis — `rate_table` source

`RATE_TABLE_V1` is the canonical rate-table constant at `harness_runtime.lifecycle.cost_attribution_validator_dispatch` (imported in `bootstrap/stage_4_od.py:89` per U-OD-40 precedent). For webhook factory threading at stage 5: `RATE_TABLE_V1` is passed directly (NOT via `ctx.rate_table` — there is no `ctx.rate_table` field; the constant is module-level). Implementer discretion: import in `stage_5_loop_init.py` + thread to factory call.

### §0.5 ZERO cross-axis cascade

Per Q4 ratification: intra-runtime-spec interface contract change. NO CP spec amendment owed. NO OD spec amendment owed. NO AS spec amendment owed. NO CXA amendment owed. NO ADR / ADD / PRD amendment owed. The 4 per-workflow params consumed from `step_context.*` per CP spec v1.12 §25.2.1 9th-field landing — that absorption already canonical.

---

## §1 U-RT-94 canonical-reading amendment

| Field | v2.29 | v2.30 amendment |
|---|---|---|
| Implements | C-RT-20 §14.10.1 WebhookDeliveryComposer carrier | C-RT-20 §14.10.1 WebhookDeliveryComposer carrier (with v1.34 signature shape) |
| Signatures (`__init__`) | 12-param ctor (5 retry/HTTP + 3 cost + 4 workflow-context) | **9-param ctor** (5 retry/HTTP + 3 cost + 1 webhook-config marker — workflow-context REMOVED) |
| Signatures (`deliver_webhook`) | `deliver_webhook(brief, idempotency_key) -> WebhookDeliveryResult` | **`deliver_webhook(brief, idempotency_key, *, workflow_id, parent_action_id, parent_idempotency_key, tenant_id=None) -> WebhookDeliveryResult`** |
| Signatures (`_attribute_webhook_cost_best_effort`) | reads `self._workflow_id` / `self._parent_action_id` / `self._parent_idempotency_key` / `self._tenant_id` | **accepts 4 per-call params** (signature refactor; instance-state reads → param reads) |
| AC #1 (ctor field-set) | 12 fields | **9 fields** (4 workflow-context fields REMOVED) |
| AC #N — NEW per-call kw-only at `deliver_webhook` | — | **NEW AC:** `deliver_webhook(...)` signature includes 4 NEW kw-only params (`workflow_id` / `parent_action_id` / `parent_idempotency_key` / `tenant_id`) per v1.34 §14.10.1 |
| AC #N — NEW per-call cost-attribution invocation | — | **NEW AC:** `_attribute_webhook_cost_best_effort` invocation consumes per-call values from `deliver_webhook` scope, NOT instance state |
| Tests-line rename | `test_composer_ctor_workflow_context_fields_bound` | **STRUCK** at v2.30 — workflow-context fields no longer on ctor. NEW tests cover `deliver_webhook` per-call param surface |
| Tests-line NEW | — | `test_deliver_webhook_accepts_per_call_workflow_context_kwargs` + `test_deliver_webhook_passes_per_call_to_cost_attribution_helper` |

## §2 U-RT-97 canonical-reading amendment

| Field | v2.29 | v2.30 amendment |
|---|---|---|
| Implements | C-RT-26 §14.16.2 materialize_webhook_delivery_composer_stage factory | C-RT-26 §14.16.2 materialize_webhook_delivery_composer_stage factory (with v1.34 signature shape) |
| Signatures | `async def materialize_webhook_delivery_composer_stage(config: RuntimeConfig, ctx: _MutableHarnessContext) -> WebhookDeliveryComposer \| None` | **`async def materialize_webhook_delivery_composer_stage(config: RuntimeConfig, ctx: _MutableHarnessContext, *, rate_table: RateTable \| None = None, cost_chain: CostAttributionChain \| None = None, audit_writer: AuditLedgerWriter \| None = None) -> WebhookDeliveryComposer \| None`** |
| AC #N — NEW cost-attribution threading | — | **NEW AC:** When all 3 substrates bound, factory passes them through `WebhookDeliveryComposer(rate_table=..., cost_chain=..., audit_writer=...)` ctor; mirror validator factory mechanism (a) per v1.18 §14.13.7 |
| AC #N — NEW opt-out preservation | — | **NEW AC:** When any of 3 substrates is `None`, composer constructed without cost substrates; preserves pre-v1.34 default-off behavior |
| Stage-5 invocation site (`bootstrap/stage_5_loop_init.py`) | passes `(config, ctx)` | **passes `(config, ctx, rate_table=RATE_TABLE_V1, cost_chain=ctx.cost_chain, audit_writer=ctx.audit_writer)`** per §0.4 source enumeration |
| Tests-line NEW | — | `test_factory_threads_cost_substrates_when_bound` + `test_factory_skips_cost_substrates_when_any_none` |

---

## §3 Adjacent observations (carry-forward)

(a) **OD-5 RETIRE-READY status preserved.** v2.30 does NOT advance OD-5 to RETIRED; deployment-time gate per AS-8d batch-25 precedent unchanged. Batch-29 filing documents factory-side surface-coverage doc-hygiene refresh ("all 4 surfaces factory-threaded" at bootstrap default path).

(b) **Bootstrap-singleton design preserved.** §14.8.8.1 step 0 OR-form precondition AND-arm at `ctx.webhook_delivery_composer is None` PRESERVED VERBATIM. The composer remains a bootstrap-singleton per §14.16; only the per-workflow scoping concern moves from instance state to call surface.

(c) **U-RT-95 driver-side catch unaffected.** The v1.26 §14.8.8.1 step 4 webhook delivery exhausted typed exception propagation path PRESERVED VERBATIM — exception class + raise site + driver-side handler at U-RT-95 unchanged.

---

## §4 Filing footer

| Field | Value |
|---|---|
| Filed at | 2026-05-28 |
| Filer | Class 1 fork apply pass per `.harness/class_1_fork_webhook_composer_per_workflow_context_threading.md` Q-set ratification |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_29.md` (2026-05-28, U-RT-84 v1.24 absorption) |
| Co-publication | runtime spec v1.34 + harness-runtime impl + harness-cp impl (none — ZERO cross-axis) + batch-29 retirement event + workspace `CLAUDE.md` row bumps |
| Cross-axis cascade | ZERO per Q4 ratification |
| Status | ✅ FILED |
