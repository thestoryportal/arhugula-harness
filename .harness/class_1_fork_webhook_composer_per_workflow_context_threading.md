# Class 1 Fork — WebhookDeliveryComposer signature divergence (reframed from per-workflow context threading)

**Filed:** 2026-05-28 (post-U-OD-40 RETIRE-READY transit at batch-28; closure-event lineage for batch-28 §3 (i) Class 3 informational gap)
**Status:** ✅ APPLIED-AS-READING-H 2026-05-28 (status-line refreshed 2026-05-30 per workspace `[[stale-carry-text-disposition]]` discipline) — operator AskUserQuestion 2026-05-28 ratified Reading H (hybrid-with-adapter) over original Reading A. Applied at runtime spec v1.33 → v1.34 (NEW adapter module `webhook_brief_adapter.py` + ctor kw-only `webhook_config: WebhookConfig | None = None` + public method `deliver_webhook_for_brief(brief: HITLEscalationBrief, idempotency_key: str) -> WebhookDeliveryResult` projecting brief → WebhookPayload via NEW adapter + dispatching via existing raw 3-arg surface) + runtime plan v2.29 → v2.30 single-unit-body amendment at U-RT-94 + harness-runtime impl + 5 NEW adapter tests + 3 NEW composer brief-surface tests; 1158/1158 harness-runtime tests pass + 4 skipped. Existing raw 3-arg surface PRESERVED VERBATIM. ZERO cross-axis cascade. Audit-trail at git history: `5c16dfb` fork filing → `c249ee3` initial Reading-A draft → `e378c9b` reframe-retract → Reading-H apply at runtime spec v1.34 commit. NO retirement event filing — H_T-OD-5 RETIRE-READY preserved at batch-28 disposition (deployment-time gate per AS-8d precedent unchanged). Original PROPOSING-REFRAMED framing preserved at §0 reframe note + §0.1 Reading set + §2 readings + §4 Q-set as historical record per workflow v1.12 §7.4.7.3.B session-resumption audit discipline. Workspace canonical cite: workspace `CLAUDE.md` §2.3 Runtime spec v1.34 row entry + §2.4 runtime plan v2.30 row entry document the Reading H apply pass.

---

## §0 — Reframe note (2026-05-28, post-Q-set ratification, pre-impl)

**Trigger:** Pre-substantive empirical orientation at impl arc start (`harness-runtime/src/harness_runtime/lifecycle/webhook_delivery_composer.py:166-171` read) surfaced that **the spec contract at §14.10.1 declares a 2-arg signature `deliver_webhook(brief, idempotency_key)` against `HITLEscalationBrief` (CP-axis), but production code declares a 3-arg signature `deliver_webhook(webhook_config: WebhookConfig, payload: WebhookPayload, idempotency_key: str)` against TWO different CP-axis types from `harness_cp.hitl_timeout_degradation`**. The two contracts are NOT signature-compatible — they describe different abstractions of the webhook surface.

**Empirical findings (verification-shape):**
1. **Spec signature** (§14.10.1 + §14.8.8.1 step 3 + §14.16 cites; 5+ recurrences across v1.20–v1.34 lineage): `deliver_webhook(brief, idempotency_key) -> WebhookDeliveryResult` against `HITLEscalationBrief`.
2. **Production carrier signature** at `webhook_delivery_composer.py:166-171`: `deliver_webhook(self, webhook_config: WebhookConfig, payload: WebhookPayload, idempotency_key: str) -> WebhookDeliveryResult`.
3. **Production caller** at `hitl_gate_composer.py:1002-1004` passes `(durable_brief, idempotency_key)` — 2 args matching spec, NOT production carrier. **This call is structurally unreachable at runtime — would raise TypeError if invoked.**
4. **All 5 production webhook composer tests** use the 3-arg signature against `WebhookConfig` + `WebhookPayload` (`test_lifecycle_webhook_delivery_composer.py` + `test_u_od_40_validator_webhook_integration.py:184-186`).
5. **U-RT-98 integration test docstring** at `test_u_rt_98_webhook_delivery_composer_binding_chain.py:37` explicitly states: "The `.deliver_webhook(...)` invocation path is NOT exercised at α scope" — confirming the caller is dead code in tests.
6. **2200/2200 baseline passes** because the broken call site is never reached.

**Domain entities (not signature-compatible):**
- `HITLEscalationBrief` (`harness_cp/validator_framework_types.py:133`): per-validator-failure escalation context — `parent_step_id` / `parent_action_id` / `fail_class` / `fail_detail_hash` / `escalation_reason` / `proposed_response_palette`. Authored at v1.18 §25.2 (V-validator-context).
- `WebhookConfig` (`harness_cp/hitl_timeout_degradation.py:91`): outbound endpoint config — `webhook_id` / `endpoint_url` / `timeout` / `degradation_mode`. Authored at U-CP-* HITL-timeout-degradation arc (pre-§14.8.8 lineage).
- `WebhookPayload` (`harness_cp/hitl_timeout_degradation.py:110`): outbound HTTP body — `approval_id` / `idempotency_key` / `gate_evaluation_ref` / `payload_body`.

**Reframe verdict:** The "per-workflow context threading" framing at §1–§5 below described a real symptom (composer stores `workflow_id` etc. as instance state) but **misidentified the underlying defect**. The real Class 1 fork is **carrier-consumer signature divergence at §14.10.1** — a long-carried spec-vs-production drift never reconciled, with a dead-code consumer at `hitl_gate_composer.py:1002` that satisfies the spec contract but cannot execute against the production carrier.

**Original Q-set ratification — RETRACTED-AT-DISCOVERY 2026-05-28:** Q1=A per-call params + Q2 factory mechanism (a) + Q3 step_context.* + Q4 ZERO + Q5 single-session were ratified at operator AskUserQuestion 2026-05-28 BUT against a framing that did not match the empirical defect. Ratification is RETRACTED at this reframe; a NEW Q-set under the signature-divergence framing is required before substantive work resumes.

**State at reframe filing:**
- `.harness/class_1_fork_webhook_composer_per_workflow_context_threading.md` — Status PROPOSING-REFRAMED at this edit
- `design-substrate/Spec_Harness_Runtime_v1.md` v1.34 change-note — content RETRACTED-IN-PLACE at this commit (replaced with reframe acknowledgement)
- `design-substrate/Implementation_Plan_Harness_Runtime_v2_30.md` — content RETRACTED-IN-PLACE at this commit (replaced with reframe acknowledgement)
- ZERO impl change at production source files
- 2200/2200 baseline preserved

---

## §0.1 — Reading set for the signature-divergence resolution (NEW Q-set)

**Reading (P) — Production-conforms-to-spec.** Refactor production `deliver_webhook` to spec-canonical 2-arg `(brief: HITLEscalationBrief, idempotency_key: str)` shape. `WebhookConfig` + `WebhookPayload` either (i) projection-deferred to internal helper consuming `brief.escalation_reason` + composer-internal endpoint config OR (ii) declared internal to composer construction. Production tests refactored. Caller at `:1002` becomes coherent. Scope: ~5–10 file changes; integration-test heavy.

**Reading (S) — Spec-conforms-to-production.** Amend spec §14.10.1 + §14.8.8.1 step 3 + §14.16 cites to declare 3-arg `(webhook_config: WebhookConfig, payload: WebhookPayload, idempotency_key: str)` signature. Caller at `:1002` needs full rewrite to construct `WebhookConfig` + `WebhookPayload` from in-scope context. ZERO production carrier change. Scope: ~2 file changes (spec + caller); doc-heavy.

**Reading (H) — Hybrid with adapter.** Spec ratifies the 2-arg conceptual surface; declare a NEW adapter/projector that transforms `HITLEscalationBrief` → `(WebhookConfig, WebhookPayload)` at the composer's body boundary. Caller stays 2-arg; production carrier stays 3-arg internally; adapter mediates. Scope: ~3 file changes (composer body + caller + spec adapter declaration).

**Reading (D) — Defer.** Leave the divergence as Class 3 informational; mark `hitl_gate_composer.py:1002` as dead-code with a structured "WONT-FIX-PENDING-{P|S|H}-RATIFICATION" comment; revisit at a future arc. Preserves current state; no impl/spec change.

---

## §0.2 — Recommended reading (assistant)

**(H) Hybrid with adapter.** Reasoning: (i) preserves both spec-conceptual surface (the brief is the natural authoring shape at validator-escalation site per CP spec v1.18 §25.2) AND production HTTP shape (the existing `WebhookPayload` JSON-serialization at `webhook_delivery_composer.py:204-209` is purpose-built for the outbound HTTP wire); (ii) localizes the divergence at a single adapter site rather than rippling through 5 production tests (P) or 5+ spec cite sites (S); (iii) the cost-attribution per-workflow context threading concern (the original v1.34 framing) collapses naturally — workflow context becomes part of the adapter's projection input.

**Reframe cost-attribution sub-arc:** Under Reading (H), the original "per-workflow context threading" defect dissolves because the brief carries `parent_action_id` (per `HITLEscalationBrief.parent_action_id`) and workflow context flows through the adapter as additional projection params. The bootstrap-singleton concern remains valid but addressed by the adapter, not by signature widening.

---

## §0.3 — State preservation

Original fork doc body (§1–§6 below) **preserved verbatim** as historical record. The §1–§6 framing is RETRACTED at reframe-filing per §0; do not act on the original Q-set ratification. New Q-set ratification at §0.1 supersedes; awaiting operator routing.

---

(Original fork doc body preserved verbatim — reframe-retracted; do not act:)

**Q-set ratification (2026-05-28):**

| Q | Ratification |
|---|---|
| Q1 — Reading selection | **(A) per-call params** |
| Q2 — Factory signature shape | mirror validator factory mechanism (a): `materialize_webhook_delivery_composer_stage(config, ctx, *, rate_table=None, cost_chain=None, audit_writer=None) -> WebhookDeliveryComposer \| None` |
| Q3 — Production caller update site | `hitl_gate_composer.py:1002` — `step_context.workflow_id` / `step_context.parent_action_id` (precedent at line 488/876) / `step_context.parent_idempotency_key` (precedent at lines 465/508) / `step_context.tenant_id` (precedent at line 792). All 4 per-workflow params sourced via `step_context.*` empirically confirmed in scope at the call site. |
| Q4 — Cross-axis cascade | **ZERO** — intra-runtime-spec interface contract change |
| Q5 — Co-publication shape | **Single-session full arc** — runtime spec v1.34 + plan v2.30 + impl + tests + retirement batch-29 + workspace `CLAUDE.md` row bumps |
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
