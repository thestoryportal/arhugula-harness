# Class 1 Fork — WebhookDeliveryComposer per-workflow context threading

**Filed:** 2026-05-28 (post-U-OD-40 RETIRE-READY transit at batch-28; closure-event lineage for batch-28 §3 (i) Class 3 informational gap)
**Status:** PROPOSING (awaiting operator AskUserQuestion ratification)
**Authority anchor:** Workspace `CLAUDE.md` §4.4 X-AL-3 (no silent H_T design extension at Phase 7 execution-time) + Phase 7 back-flow routing per `Project_Workflow_v1_10.md` §2.7.6
**Mirror precedent:** `.harness/class_1_fork_u_od_40_validator_post_evaluate_hook.md` (sibling U-OD-40 surface — validator) + `.harness/class_1_fork_u_rt_94_webhook_delivery_composer_binding_chain_absence.md` (predecessor binding-chain absence arc — original `WebhookDeliveryComposer` factory authoring)

---

## §1 — Trigger

Batch-28 §3 (i) catalogued an informational follow-on: `materialize_webhook_delivery_composer_stage` does NOT thread cost-attribution substrates (`rate_table` + `cost_chain` + `audit_writer`) through to `WebhookDeliveryComposer` ctor, unlike the parallel `materialize_validator_framework_stage` amendment landed at U-OD-40. The framing presumed factory-amendment analogy.

**Empirical orientation surfaces the analogy break.** Pre-substantive grep at U-OD-40 closure arc reveals:

1. `WebhookDeliveryComposer.__init__(...)` at `harness-runtime/src/harness_runtime/lifecycle/webhook_delivery_composer.py:104-119` accepts `workflow_id` / `parent_action_id` / `parent_idempotency_key` / `tenant_id` as **ctor params** stored as instance state. The integration test at `tests/test_u_od_40_validator_webhook_integration.py:159-170` confirms: composer is constructed PER-WORKFLOW-EXECUTION with workflow context bound at ctor.
2. The bootstrap-singleton factory at stage 5 LOOP_INIT cannot know these per-workflow params — they don't exist until a workflow is running.
3. Production caller exists at `hitl_gate_composer.py:1002`: `await self.webhook_delivery_composer.deliver_webhook(durable_brief, idempotency_key)` invokes the bootstrap-singleton (threaded through `HITLGateComposer.webhook_delivery_composer`). At this call site, `parent_action_id` is in scope (line 995); `step_context.workflow_id` is in scope per CP spec v1.12 §25.2.1; `ctx.tenant_id` is available.

**Dep-graph constraint:** ZERO — `harness-runtime` already imports `harness_od` cost-attribution helpers per U-OD-39 + U-OD-40 precedent. This fork is intra-runtime-spec interface contract change.

**Sibling-shape divergence from validator hook (B):** Validator hook is stateless w.r.t. workflow scope — per-invocation context arrives via the hook's `on_post_evaluate(...)` call surface (`step` + `step_context` + `evaluation` + `execution_time_ms`). `SkillActivationHook` (U-RT-101) follows the same pattern. WebhookDeliveryComposer stores workflow context as instance state, which is structurally incompatible with bootstrap-singleton scope.

---

## §2 — Three readings

**(A) Per-call params on `deliver_webhook(...)`.** Refactor:
- `WebhookDeliveryComposer.__init__` strips `workflow_id` / `parent_action_id` / `parent_idempotency_key` / `tenant_id` fields. Retains: `retry_max_attempts` / `retry_base_delay_seconds` / `tracer_provider` / `http_client_factory` / `sleep_fn` / `rate_table` / `cost_chain` / `audit_writer` (cost substrates remain bootstrap-singleton; per-workflow params move to call surface).
- `deliver_webhook(brief, idempotency_key)` signature widens to `deliver_webhook(brief, idempotency_key, *, workflow_id, parent_action_id, parent_idempotency_key, tenant_id=None)` (workflow context as per-call kw-only params).
- Production caller at `hitl_gate_composer.py:1002` passes the in-scope values per-call.
- Factory amendment: now a clean cost-attribution thread-through (`rate_table` + `cost_chain` + `audit_writer` kw-only, mirror validator-factory shape).
- Bootstrap-singleton design preserved; composer becomes stateless w.r.t. workflow scope.

**(B) Per-workflow construction (builder pattern).** Factory returns a builder/factory-of-composer; HITLGateComposer (or workflow-driver-side composer) calls `builder.build(workflow_id=..., parent_action_id=..., ...)` to construct a per-workflow composer instance. Heavier refactor:
- `WebhookDeliveryComposerBuilder` NEW class at carrier surface.
- `materialize_webhook_delivery_composer_stage` returns builder, not composer.
- `ctx.webhook_delivery_composer` field type changes; §14.8.8.1 step 0 precondition references builder existence.
- Step 3 call site constructs the composer per-workflow before `deliver_webhook(...)`.

**(C) Phantom — keep current shape.** REJECTED. Grep evidence: real production caller at `hitl_gate_composer.py:1002` consumes the bootstrap-singleton. Current shape has the singleton with workflow params that can never be populated at bootstrap — the cost-attribution substrate is unreachable from the bootstrap path.

---

## §3 — Recommendation

**(A) per-call params.** Reasoning:
1. Mirror validator-hook + skill-activation-hook posture: stateless w.r.t. workflow scope, per-invocation context arrives at call surface.
2. Smaller surface change (1 ctor param-set strip + 1 method signature widen + 1 production caller line refresh + 1 factory clean amendment) vs (B)'s builder-class introduction + composer-field-type change + step-3 call-site composer construction.
3. Bootstrap-singleton preserved — `ctx.webhook_delivery_composer is None` precondition at §14.8.8.1 step 0 retains canonical shape.
4. Factory cleanly mirrors validator factory mechanism (a): rate_table + cost_chain + audit_writer threaded at bootstrap; workflow context per-call.

(B) is structurally clean but introduces a builder type + per-workflow instantiation cost at every HITL gate firing. (A) preserves the architecture and pays the surface cost only at the interface boundary.

---

## §4 — Q-set (awaiting operator ratification)

**Q1 — Reading selection:** (A) per-call params vs (B) per-workflow construction.

**Q2 — Factory signature shape:** mirror validator factory mechanism (a) — `materialize_webhook_delivery_composer_stage(config, ctx, *, rate_table=None, cost_chain=None, audit_writer=None) -> WebhookDeliveryComposer | None`. Cost substrates default `None`; non-None construction binds the composer with cost-attribution active. ↔ alternative: positional/required.

**Q3 — Production caller update site:** `hitl_gate_composer.py:1002` — pass `workflow_id=step_context.workflow_id` + `parent_action_id=parent_action_id` + `parent_idempotency_key=durable_brief.idempotency_key (or upstream)` + `tenant_id=ctx.tenant_id`. Confirm parent_idempotency_key source — `durable_brief` field vs upstream caller context.

**Q4 — Cross-axis cascade:** ZERO expected (intra-runtime-spec interface change; no CP / OD / AS / CXA / ADR / ADD / PRD edge owed). Confirm.

**Q5 — Co-publication shape:** Single-session apply arc — runtime spec v1.33 → v1.34 (§14.10 `deliver_webhook` signature widening + §14.16 factory signature widening) + runtime plan v2.29 → v2.30 (U-RT-94 + U-RT-97 AC refresh) + production impl + test refresh + retirement batch-29 filing H_T-OD-5 surface-coverage view → "factory-threaded for all 4 surfaces" doc-hygiene note (RETIRE-READY status preserved; deployment-time gate unchanged). Alternative: split arc — spec/plan first, impl follow-on.

---

## §5 — Scope estimate (Reading A assumed)

| Artifact | Change |
|---|---|
| `design-substrate/Spec_Harness_Runtime_v1.md` | NEW v1.34 delta — §14.10 `deliver_webhook` signature widening (4 NEW kw-only params); §14.16 factory signature widening (3 NEW kw-only cost substrate params); §14.16 amendment text per X-AL-3 fork doc ratification cite |
| `design-substrate/Implementation_Plan_Harness_Runtime_v2_29.md` | NEW v2.30 delta — single-unit-body amendments at U-RT-94 (composer ctor + deliver_webhook signature) + U-RT-97 (factory signature widening); AC refresh; ZERO new unit |
| `harness-runtime/src/harness_runtime/lifecycle/webhook_delivery_composer.py` | `__init__` strips 4 workflow-context params (`workflow_id` / `parent_action_id` / `parent_idempotency_key` / `tenant_id`); `deliver_webhook(...)` accepts them as kw-only per-call params; `_attribute_webhook_cost_best_effort(...)` consumes per-call values not instance state |
| `harness-runtime/src/harness_runtime/bootstrap/factories/webhook_delivery_composer_factory.py` | Factory accepts kw-only cost substrate params; threads them through composer ctor on opt-in branch (mirror validator factory shape) |
| `harness-runtime/src/harness_runtime/bootstrap/stage_5_loop_init.py` | Stage-5 invocation passes `rate_table` + `cost_chain` + `audit_writer` from `ctx` (analogous to `stage_4_od.py:89` validator factory call) |
| `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py:1002` | Call site passes workflow context per-call kwargs |
| `harness-runtime/tests/test_u_od_40_validator_webhook_integration.py` | Composer construction strips ctor workflow params; `deliver_webhook` call passes them per-call |
| `harness-runtime/tests/lifecycle/test_cost_attribution_webhook_dispatch.py` | If applicable — composer-shape test updates |
| `harness-runtime/tests/bootstrap/factories/test_webhook_delivery_composer_factory.py` | Cost substrate threading verification |
| `.harness/phase-7d-retirement-events-batch-29.md` | NEW retirement event filing — OD-5 surface-coverage doc-hygiene refresh ("all 4 surfaces factory-threaded"); RETIRE-READY status preserved; full RETIRED gate unchanged (operator deployment-time opt-in per AS-8d precedent) |
| `CLAUDE.md` (workspace) §2.3 + §2.4 | Runtime spec + plan row bumps |
| `harness-runtime/CLAUDE.md` (if applicable) | C-RT-20 + C-RT-26 row refresh |
| Memory | NEW entry `fork-webhook-composer-per-workflow-context-threading.md` + index pointer |

**Estimated commits:** 3–4 (spec + plan; impl + tests; retirement event + workspace CLAUDE.md row bumps; merge).

**Test impact estimate:** ~15-25 tests (composer ctor/method shape + factory + integration + hitl-gate caller-shape). 2200/2200 baseline at HEAD `dcb0017`.

---

## §6 — Filing footer

| Field | Value |
|---|---|
| Filed at | 2026-05-28 |
| Filer | Phase 7 execution session post-batch-28 closure analysis |
| Classification | Class 1 (X-AL-3 spec extension — runtime spec v1.33 §14.10 + §14.16 signature widening) |
| Source of detection | Empirical grep at `hitl_gate_composer.py:1002` production caller + advisor pre-substantive consultation (sibling-shape break from validator hook surface) |
| Predecessor lineage | `.harness/class_1_fork_u_rt_94_webhook_delivery_composer_binding_chain_absence.md` (v1.26 §14.16 factory authoring; this fork extends that arc); `.harness/phase-7d-retirement-events-batch-28.md` §3 (i) (Class 3 informational gap surfaced; this fork promotes to Class 1) |
| Cross-axis cascade | ZERO expected (intra-runtime-spec interface contract change; pending Q4 confirmation) |
| Status | PROPOSING — awaiting operator AskUserQuestion Q-set ratification |
