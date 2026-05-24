# Implementation Plan — Harness Runtime v2.23

## Change-note (v2.22 → v2.23)

**Scope of revision.** Spec-revision-driven plan revision absorbing runtime spec v1.23 → v1.24 NEW §14.8.8 Durable-async cell HITL composition sub-section (commit `c73c25d` prior). Authors NEW L9-terdecies 3-unit linear-chain cluster (U-RT-93 + U-RT-94 + U-RT-95) decomposing the runtime-side composer-body extension at §14.8.2 step 4-bis insertion + full §14.8.8.1 6-step durable-async branch body + §14.8.8.2 `HITLPauseRequestedSignal` typed control-flow exception + §14.8.8.3 `_evaluate_cell_synchrony_tolerant` binding-tolerant helper + §14.8.8.5 resume-side one-shot delivery via `ResumeContext.hitl_response`. Co-published with CP spec v1.16 (commit `aa841b0` prior) + CP plan v2.21 (this session prior) authoring NEW `ResumeContext` carrier + `attempt_resume` async signature widening. ZERO new cross-axis CXA edges per scoping doc §3.3; cluster-boundary edges to already-landed substrate (C-RT-20 WebhookDeliveryComposer at U-RT-69; C-RT-24 PauseResumeProtocol stage at L9-undecies; CP-side `matrix_cell_for` + `SynchronyClass` at `harness-cp/.../persona_engine_hitl_matrix.py`; CP-side `StepEffectiveBinding` at `harness-cp/.../per_step_override_evaluator.py:117`; CP spec v1.16 §26.8 `ResumeContext` carrier at CP plan v2.21 U-CP-64 amendment site).

**Source of fix.** Runtime spec v1.23 → v1.24 NEW §14.8.8 publication (this session prior commit `c73c25d`) per ratified scoping doc `.harness/hitl_gate_as_pause_trigger_composition_scoping.md` Q1-Q5 + D8 cite-correction (operator-ratified 2026-05-24 same session at checkpoint `20260524-130230` item #1 ratify). The §14.14.7 deferred-discretion residual (i) "HITL-gate-as-pause-trigger composition" is resolved at spec v1.24 §14.8.8 authoring; v2.23 lands the implementation-planning shape consuming the new spec §14.8.8 contract.

**Authority basis for fix direction.** Mirrors L9-decies (validator-composer arc Reading A) + L9-undecies (pause/resume composer arc) + L9-duodecies (Reading B validator-composer arc) + L9-decies (Reading A) cluster-shape precedents: 3-unit linear-chain cluster decomposing a NEW §14.x runtime spec contract authoring into L0 carriers + helper + typed exception → L1 composer body amend → L2 driver-side integration + e2e real-bootstrap test. Per Q4 (b-revised) `StepEffectiveBinding` already carries `binding.persona_tier` + `binding.engine_class` (existing CP-side carrier at `harness-cp/.../per_step_override_evaluator.py:117`); NO new RuntimeConfig field; NO new HarnessContext field at §3+§4 layer; the runtime-internal `ctx.resume_context` mutable carrier binding-site is implementer-discretion at U-RT-94 landing arc per spec §14.8.8.8.

**Cluster shape — L9-terdecies (NEW at v2.23).**

| Unit | Layer | Implements | Files | Depends on |
|---|---|---|---|---|
| U-RT-93 | L0 | Runtime spec v1.24 §14.8.8.2 `HITLPauseRequestedSignal` typed control-flow exception + §14.8.8.3 `_evaluate_cell_synchrony_tolerant` binding-tolerant helper | `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py` (APPEND new helper sibling to `_evaluate_hitl_required_tolerant` + APPEND new `HITLPauseRequestedSignal` exception class) | within-axis: none new; consumes already-landed CP-side `persona_engine_hitl_matrix.py` + CP-side `StepEffectiveBinding` + already-landed `HITLEscalationBrief` per C-CP-28 §25.2 + `WebhookDeliveryResult` per C-RT-20 §14.10.1 (existing import patterns; no new edge declaration) |
| U-RT-94 | L1 | Runtime spec v1.24 §14.8.2 step 4-bis insertion + full §14.8.8.1 6-step durable-async composer body + §14.8.8.5 resume-side one-shot delivery via `ResumeContext.hitl_response` | `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py` (amend `RuntimeHITLGateComposer.dispatch(...)` body at §14.8.2 step 4-bis + add §14.8.8 durable-async branch + author resume-side `ctx.resume_context` consume-and-clear logic; specific binding-site for `ctx.resume_context` mutable carrier is implementer-discretion per §14.8.8.8) | within-axis: [U-RT-93] (helper + exception class); within-axis-cross-package: U-CP-64 (CP plan v2.21 — `ResumeContext` carrier + `attempt_resume` widened signature) per cross-axis-edge declaration-at-consumer-site convention |
| U-RT-95 | L2 | Runtime spec v1.24 §14.8.8.4 driver-side signal handling discipline + e2e real-bootstrap pause-on-durable-cell cycle per scoping doc D7 mechanism α | `harness-cp/src/harness_cp/workflow_driver.py` (amend per-step dispatch try-block to catch `HITLPauseRequestedSignal`); NEW `harness-runtime/tests/integration/test_u_rt_95_hitl_pause_trigger_durable_async_full_execution_path.py` (e2e test against real `run_bootstrap` substrate with mechanism α in-process emulator webhook endpoint) | within-axis: [U-RT-94] (composer body + flag-set + signal-raise); cluster-boundary to already-landed L9-undecies (U-RT-87/88/89 PauseResumeProtocol stage + driver per-step pre-entry detection at v1.21 §14.14.3); cluster-boundary to L9-quinquies (U-RT-60 HITL gate composer at v1.9 baseline) |

**Within-cluster edges:** U-RT-93 → U-RT-94 → U-RT-95 (linear chain).

**Cluster-boundary edges to already-landed substrate:**
- C-RT-20 `WebhookDeliveryComposer` at U-RT-69 (`harness-runtime/.../lifecycle/webhook_delivery_composer.py`)
- C-RT-24 PauseResumeProtocol stage at L9-undecies (U-RT-87 RuntimeConfig + HarnessContext fields + PauseResumeProtocolConfig empty-marker; U-RT-88 `materialize_pause_resume_protocol_stage` factory + stage-5 wiring; U-RT-89 workflow_driver per-step pre-entry pause-trigger detection); H_T-CP-22 RETIRED at batch-18
- CP plan v2.21 U-CP-64 (`ResumeContext` carrier + `attempt_resume` widened signature)
- CP-side `matrix_cell_for(persona_tier, engine_class) → HITLMatrixCell` + `SynchronyClass` StrEnum at `harness-cp/src/harness_cp/persona_engine_hitl_matrix.py` (15-entry HITL_MATRIX)
- CP-side `StepEffectiveBinding` at `harness-cp/src/harness_cp/per_step_override_evaluator.py:117` (already carries `binding.persona_tier` + `binding.engine_class`)
- L9-quinquies (U-RT-60 HITL gate composer body baseline)

**ZERO new CXA edges.** Composer-to-driver flag-signal flow is intra-runtime; CP-spec→runtime ResumeContext consumption is intra-axis pattern per scoping doc §3.3.

**Sections preserved verbatim from v2.22.** All v2.22 substantive content (L9-duodecies cluster U-RT-90/91/92 + Reading B Class 3 informational divergence retirement) preserved unchanged. All v2.21 L9-duodecies cluster bodies preserved. All v2.20 L9-undecies cluster (U-RT-87/88/89) preserved. All v2.19 / v2.18 / v2.17 / ... / v2 substantive content preserved.

**Status posture.** Proposed (v2.22) → **Proposed (v2.23)**. v2.23 is an additive cluster authoring — NEW L9-terdecies 3-unit linear-chain cluster (U-RT-93 + U-RT-94 + U-RT-95). Net unit count: +3 (90 → 93). Net cluster count: +1 (L9-terdecies). Net DAG within-cluster edges: +2 (U-RT-93 → U-RT-94 → U-RT-95). Net cluster-boundary edges: +6 (5 to already-landed substrate + 1 within-axis-cross-package to U-CP-64). Net CXA cross-axis edges: 0. Net coverage matrix rows: +3 (runtime spec v1.24 §14.8.8 → U-RT-93/94/95). NO new RuntimeConfig field; NO new HarnessContext field at §3+§4 layer per Q4 (b-revised); NO new sub-model carrier at runtime-spec layer; NO acceptance criterion removal at any preserved unit.

**Downstream absorption owed (post-v2.23).**

(a) Workspace `CLAUDE.md` §2.4 runtime plan row version bump (v2.22 → v2.23); co-published this arc.

(b) `harness-runtime` impl — `hitl_gate_composer.py` amend at §14.8.2 step 4-bis + NEW durable-async branch body per §14.8.8.1 + NEW `_evaluate_cell_synchrony_tolerant` helper sibling to `_evaluate_hitl_required_tolerant` + NEW `HITLPauseRequestedSignal` typed control-flow exception class. Co-published this arc OR sequential `phase-7-implementation` skill invocations (U-RT-93 → U-RT-94 → U-RT-95).

(c) `harness-cp` impl — `workflow_driver.py` per-step dispatch try-block amend to catch `HITLPauseRequestedSignal` (at U-RT-95 landing). Existing 677/677 harness-cp tests preserved unchanged.

(d) `harness-runtime` integration test — NEW `test_u_rt_95_hitl_pause_trigger_durable_async_full_execution_path.py` per scoping doc D7 mechanism α. Pattern mirrors U-RT-89 + U-RT-92 full-execution-path e2e tests.

(e) Retirement-batch implications — NO new retirement event filed at this arc close per scoping doc §3.3 (the arc does not gate any H_T-CP-* / H_T-AS-* substitution-mechanism retirement). Possible follow-on retirement at separate operator-discretion arc if a substitution row covers "durable-async HITL delivery primitive operational against real external webhook" (mechanism β) — no such row currently declared at `Phase_7_Meta_Architecture_v1.md` §5; mechanism α (in-process emulator at U-RT-95) does NOT satisfy a hypothetical β-gated retirement.

(f) OD spec / OD plan / OD impl / CXA / ADR — ZERO cascade per scoping doc §3.3 (verified empirically this session).

**Adjacent defects surfaced (NOT patched per FM-2 no-extension discipline).**

(i) **§14.8.8 step 4-bis sequencing under retry semantics (per runtime spec v1.24 adjacent defect (i)).** When C-RT-16 retry wraps INFERENCE_STEP and a retry attempt fires AFTER durable-async pause + resume cycle, retry semantics interaction with already-injected `ResumeContext.hitl_response` is implementer-discretion at U-RT-94 landing arc per FM-2. Canonical reading is one-shot delivery per §14.8.8.5 (response consumed exactly once; retry re-fires gate from scratch). Surfaced; codified at U-RT-94 AC #5 (clear-after-first-consumption discipline); detailed retry-vs-resume sequencing left to impl-arc per FM-2.

(ii) **`_evaluate_cell_synchrony_tolerant` None-handling at operator opt-out (per runtime spec v1.24 adjacent defect (ii)).** Helper returns None when binding is None (operator opt-out → fall back to sync-blocking). Composer body at §14.8.8.1 step 1 evaluates `synchrony = _evaluate_cell_synchrony_tolerant(binding); if synchrony is None or synchrony == SynchronyClass.SYNC_BLOCKING: fall_through_to_step_4f` (sync path). Surfaced; codified at U-RT-93 AC #2 (helper None-handling discipline).

(iii) **Inbound webhook endpoint construction operator-implemented (per runtime spec v1.24 adjacent defect (iii)).** Out of v1.24 / v2.23 scope. The endpoint contract: receive operator response → construct HITLResult from payload → invoke `attempt_resume(snapshot, material_diff_policy=..., resume_context=ResumeContext(hitl_response=HITLResult(...)))` per CP spec v1.16 §26.8.5. Endpoint deployment-surface choice (Flask / FastAPI / Lambda / K8s ingress) is implementer-discretion per `pause_requested_flag` caller-surface contract at v1.21 §14.14.7. Surfaced; NOT codified at any v2.23 unit AC per FM-2 no-extension.

(iv) **Mechanism α vs β e2e test substrate (Q5 D7 carry per runtime spec v1.24 adjacent defect (iv)).** U-RT-95 e2e test substrate at v2.23: mechanism α (in-process emulator webhook endpoint; recommended default per scoping doc D7). Mechanism β (real external HTTP endpoint with operator-implemented inbound handler) as follow-on retirement-batch arc gate. Operator selected α at scoping doc D7.

---

## §1 — U-RT-93 plan-body authoring

### U-RT-93 — `_evaluate_cell_synchrony_tolerant` binding-tolerant helper + `HITLPauseRequestedSignal` typed control-flow exception (NEW at v2.23, L9-terdecies L0)

- **Implements:** Runtime spec v1.24 §14.8.8.2 `HITLPauseRequestedSignal` typed control-flow exception class definition + §14.8.8.3 `_evaluate_cell_synchrony_tolerant` binding-tolerant runtime helper
- **Files:** `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py` (APPEND new helper sibling to existing `_evaluate_hitl_required_tolerant` at U-RT-91 site; APPEND new `HITLPauseRequestedSignal` exception class adjacent to existing `HITLCellExcludedError` / `HITLGateTimeoutError` / `HITLGateRejectedError` / `HITLGateAuditComposeError` class definitions)
- **Signatures:**
  ```python
  def _evaluate_cell_synchrony_tolerant(
      binding: StepEffectiveBinding | None,
  ) -> SynchronyClass | None:
      """Returns matrix_cell_for(binding.persona_tier, binding.engine_class).synchrony_class
      per CP spec v1.2 §18.1 (preserved through v1.16); None when binding is None."""

  class HITLPauseRequestedSignal(BaseException):
      """Typed control-flow signal raised by HITL gate composer body at §14.8.2 step 4-bis
      durable-async cell branch. NOT a fail class. Inherits BaseException for control-flow-signal
      pattern."""
      brief: HITLEscalationBrief
      delivery_result: WebhookDeliveryResult
  ```
- **Depends on:** (none new) — consumes already-landed CP-side `persona_engine_hitl_matrix.py` (`matrix_cell_for` + `SynchronyClass` + `HITLMatrixCell`) + already-landed CP-side `StepEffectiveBinding` at `per_step_override_evaluator.py:117` + already-landed `HITLEscalationBrief` per C-CP-28 §25.2 + already-landed `WebhookDeliveryResult` per C-RT-20 §14.10.1 (all existing import patterns at hitl_gate_composer.py — no new edge declaration).
- **ACs:**
  1. `_evaluate_cell_synchrony_tolerant(binding=None)` returns `None` (operator-opt-out arm; composer falls back to sync-blocking per §14.8.8.1 step 1 + adjacent defect (ii)).
  2. `_evaluate_cell_synchrony_tolerant(binding=non_None_with_valid_persona_tier_engine_class)` returns `matrix_cell_for(binding.persona_tier, binding.engine_class).synchrony_class` — thin-wrap delegation to landed CP-side `matrix_cell_for` per Q1 (α-revised); unit test verifies 3 cells from C-CP-18 §18.1 15-entry matrix (sync-blocking row, durable-async row, excluded row — excluded delegated to existing §14.8.2 step 4b `HITLCellExcludedError` raise per scoping doc §14.8.8.7 invariant 1 + spec §14.8.8.3 docstring).
  3. `HITLPauseRequestedSignal` class inherits `BaseException` (NOT `Exception`) per spec §14.8.8.2 inheritance-choice-rationale (control-flow-signal pattern; normal-path `try/except` blocks catching `Exception` MUST NOT suppress the signal — only explicit `except HITLPauseRequestedSignal` or `except BaseException` consumes it). Unit test verifies `issubclass(HITLPauseRequestedSignal, BaseException) and not issubclass(HITLPauseRequestedSignal, Exception)`.
  4. `HITLPauseRequestedSignal` carries 2 fields: `brief: HITLEscalationBrief` + `delivery_result: WebhookDeliveryResult` per spec §14.8.8.2 carrier definition. Unit test verifies constructor accepts both + attributes round-trip without modification.

**Rollback boundary.** Revert the 2-symbol module APPEND (one helper function + one exception class). U-RT-94 (within-cluster dependent) loses helper + exception substrate. No cross-axis impact.

---

## §2 — U-RT-94 plan-body authoring

### U-RT-94 — HITL gate composer body amend at §14.8.2 step 4-bis + §14.8.8 durable-async branch body + resume-side one-shot delivery (NEW at v2.23, L9-terdecies L1)

- **Implements:** Runtime spec v1.24 §14.8.2 step 4-bis insertion + §14.8.8.1 full 6-step durable-async composer body + §14.8.8.5 resume-side one-shot delivery via `ResumeContext.hitl_response`
- **Files:** `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py` (amend `RuntimeHITLGateComposer.dispatch(...)` body: INSERT step 4-bis synchrony-class branch between existing step 4e and step 4f; ADD §14.8.8 durable-async branch body — 6-step composition firing WebhookDeliveryComposer + flag-set + signal-raise; ADD resume-side consume-and-clear logic for `ResumeContext.hitl_response`). Specific binding-site for `ctx.resume_context` mutable carrier is implementer-discretion per spec §14.8.8.8 (options: HarnessContext field at C-RT-04 layer extension OR sidecar `ResumeContextHolder` carrier OR `ctx.resume_context_holder.current_context` indirect binding; implementer's call).
- **Signatures:** No new top-level signature (in-place amendment of existing `RuntimeHITLGateComposer.dispatch(...)` async method body). Internal helpers (composer-body sub-functions) per implementer-discretion.
- **Depends on:** [U-RT-93] (within-cluster L0 → L1); within-axis-cross-package: U-CP-64 at CP plan v2.21 (`ResumeContext` carrier + `attempt_resume` widened signature)
- **ACs:**
  1. §14.8.2 step 4-bis branch fires AFTER existing step 4e (gate-evaluated span open) and BEFORE existing step 4f (sync AskUserQuestion invocation). Branch evaluates `synchrony = _evaluate_cell_synchrony_tolerant(binding)`. On `synchrony is None or synchrony == SynchronyClass.SYNC_BLOCKING` → falls through to existing step 4f (preserved verbatim from v1.9-era baseline). On `synchrony == SynchronyClass.DURABLE_ASYNC` → routes to NEW §14.8.8 composition body. Unit test verifies branch dispatching for all 3 synchrony-class outcomes (None / SYNC_BLOCKING / DURABLE_ASYNC).
  2. §14.8.8.1 step 1 composes `HITLEscalationBrief` per C-CP-28 §25.2 shape — re-used from validator-escalation arc; fields populated `parent_step_id` + `parent_action_id` + `fail_class=None` + `fail_detail_hash=None` + `escalation_reason="durable_async_cell_synchrony"` + `proposed_response_palette=palette` (effective palette from existing step 4d). Unit test verifies brief construction shape.
  3. §14.8.8.1 step 2 computes idempotency key per `compose_hitl_action_id(step_context.parent_action_id, placement.position)` shape — mirrors existing §14.8.2 step 4h substep 8b-HITL discipline; key passed opaque to webhook composer. Unit test verifies key construction.
  4. §14.8.8.1 step 3 invokes `await ctx.webhook_delivery_composer.deliver_webhook(brief, idempotency_key)` per C-RT-20 §14.10.1; returns `WebhookDeliveryResult`. Unit test verifies invocation against in-process fixture WebhookDeliveryComposer mock.
  5. §14.8.8.1 step 4 — on `delivery_result.delivered is False` → raise typed `HITLWebhookDeliveryExhaustedError` (re-raise from `WebhookDeliveryExhaustedError` per C-RT-20 §14.10.4) mapping to NEW `RT-FAIL-HITL-WEBHOOK-DELIVERY-EXHAUSTED` per §14.8 fail-class taxonomy. Composer does NOT set `ctx.pause_requested_flag` + does NOT raise `HITLPauseRequestedSignal` (the durable-async pause was not initiated). Unit test verifies fail-path semantics.
  6. §14.8.8.1 step 5 — on `delivery_result.delivered is True` → `ctx.pause_requested_flag.set()` + raise `HITLPauseRequestedSignal(brief=..., delivery_result=...)`. Unit test verifies success-path flag-set + signal-raise + signal payload round-trip.
  7. §14.8.8.5 resume-side one-shot delivery: at resumed-step gate-evaluation, IF `ctx.resume_context is not None and ctx.resume_context.hitl_response is not None` → `gate_result = ctx.resume_context.hitl_response; clear_resume_context()`. The clear-after-first-consumption discipline preserves one-shot semantic per spec §14.8.8.7 invariant 3 (`ResumeContext.hitl_response` consumed at most once; subsequent gate-evaluations at the same step re-fire from scratch). Unit test verifies one-shot consume + clear + subsequent gate-evaluation re-fires.
  8. `ctx.resume_context` mutable carrier binding-site at HarnessContext or sidecar carrier per implementer-discretion at §14.8.8.8. Implementation MUST satisfy: (i) operator-supplied `ResumeContext` arrives via `attempt_resume(..., resume_context=ResumeContext(hitl_response=...))` at CP-side method body; (ii) driver-side propagates from `attempt_resume` parameter to runtime composer site at resumed-step gate-evaluation; (iii) clear-after-first-consumption discipline preserves one-shot semantic. Specific binding-site shape (HarnessContext field vs ResumeContextHolder sidecar vs ContextVar) implementer-discretion.

**Rollback boundary.** Revert `RuntimeHITLGateComposer.dispatch(...)` body amend (step 4-bis insertion + §14.8.8 durable-async branch + resume-side consume-and-clear logic). U-RT-95 (within-cluster L2 dependent) loses composer-side substrate. Sync-blocking path at step 4f preserved unchanged.

---

## §3 — U-RT-95 plan-body authoring

### U-RT-95 — Driver-side `HITLPauseRequestedSignal` catch + e2e real-bootstrap pause-on-durable-cell cycle (NEW at v2.23, L9-terdecies L2)

- **Implements:** Runtime spec v1.24 §14.8.8.4 driver-side signal handling discipline + e2e real-bootstrap pause-on-durable-cell cycle per scoping doc D7 mechanism α (in-process emulator webhook endpoint; recommended default)
- **Files:** `harness-cp/src/harness_cp/workflow_driver.py` (amend per-step dispatch try-block at C-CP-25 §25.3.3.4 step-dispatch try/except boundary to catch `HITLPauseRequestedSignal`; on catch: `continue` to next iteration — falls through to existing v1.21 §14.14.3 per-step pre-entry pause-trigger detection which fires `capture_pause_snapshot(...)` + returns `RunStatus.PAUSED`); NEW `harness-runtime/tests/integration/test_u_rt_95_hitl_pause_trigger_durable_async_full_execution_path.py` (e2e test against real `run_bootstrap` substrate with mechanism α in-process emulator webhook endpoint per scoping doc D7)
- **Signatures:** No new top-level signature (in-place amendment of existing driver try-block + NEW test module). Internal test fixture (`InProcessEmulatorWebhookEndpoint` or equivalent) implementer-discretion per spec §14.8.8.8.
- **Depends on:** [U-RT-94] (within-cluster L1 → L2); cluster-boundary to already-landed substrate per change-note above (L9-undecies U-RT-87/88/89 PauseResumeProtocol stage + driver per-step pre-entry detection; L9-quinquies U-RT-60 HITL gate composer baseline; U-CP-64 at CP plan v2.21 `ResumeContext` carrier + `attempt_resume` widened signature)
- **ACs:**
  1. `harness-cp/src/harness_cp/workflow_driver.py` per-step dispatch try-block catches `HITLPauseRequestedSignal` per spec §14.8.8.4. On catch: `continue` to next iteration (NOT a fail-class mapping; signal is normal-path control-flow). Existing 677/677 harness-cp tests preserved unchanged (no behavior change at non-durable-async paths). Unit test verifies driver-side catch + iteration-continuation + subsequent pre-entry detection firing.
  2. e2e test path (i) durable-async pause-trigger: operator-supplied `StepEffectiveBinding` with `(persona_tier, engine_class)` matrix cell == `DURABLE_ASYNC` per C-CP-18 §18.1 → composer fires `deliver_webhook(...)` against in-process fixture endpoint → endpoint returns `delivered=True` → `ctx.pause_requested_flag.set()` → `HITLPauseRequestedSignal` raised → driver catches → next iteration pre-entry detection fires → `capture_pause_snapshot(...)` invoked → `RunResult(status=RunStatus.PAUSED, pause_snapshot=PauseSnapshot(...))` returned to caller. Test verifies binding chain at all 4 stages empirically per `[[verification-shape-sharpened-grep-vs-e2e]]` discipline.
  3. e2e test path (ii) resume-consume-cycle: caller invokes `run_workflow(..., pause_snapshot=...)` with the snapshot from path (i) → driver entry-point resume branch fires → `attempt_resume(snapshot, material_diff_policy=STRICT, resume_context=ResumeContext(hitl_response=HITLResult(response=APPROVE, ...)))` per CP spec v1.16 §26.8.5 widened signature → resumed-step gate-evaluation at step cursor consumes `resume_context.hitl_response` per §14.8.8.5 one-shot delivery → workflow proceeds → `RunResult(status=RunStatus.SUCCESS, ...)` returned. Test verifies resume cycle + one-shot consume + clear + RunStatus.SUCCESS final state.
  4. e2e test path (iii) inverse-arm sync-blocking pass-through: operator-supplied `StepEffectiveBinding` with `(persona_tier, engine_class)` matrix cell == `SYNC_BLOCKING` per C-CP-18 §18.1 → composer falls through to existing AskUserQuestion sync path at step 4f (no flag-set; no signal raise; no webhook delivery). Test verifies inverse-arm preserves v1.9-era sync-blocking semantics unchanged.
  5. e2e test path (iv) webhook-exhausted failure: operator-supplied `StepEffectiveBinding` with cell == `DURABLE_ASYNC` + fixture endpoint configured to return `delivered=False` after exhausting retry attempts → composer raises `HITLWebhookDeliveryExhaustedError` mapping to `RT-FAIL-HITL-WEBHOOK-DELIVERY-EXHAUSTED` → flag NOT set + signal NOT raised → driver `try/except` maps to `step-failure: RT-FAIL-HITL-WEBHOOK-DELIVERY-EXHAUSTED: ...` per C-CP-25 §25.3.3.4. Test verifies fail-path semantics + RunResult fail-state.
  6. Test pattern mirrors `test_u_rt_89_pause_resume_full_execution_path.py` (L9-undecies pause-resume e2e precedent) + `test_u_rt_92_validator_escalation_full_execution_path.py` (Reading B validator-escalation e2e precedent). Mechanism α (in-process emulator endpoint) is the substrate per scoping doc D7 operator selection; mechanism β (real external HTTP endpoint) deferred per FM-2 to follow-on retirement-batch arc if a substitution row covers operational-against-external-webhook.

**Rollback boundary.** Revert `workflow_driver.py` try-block amend + revert NEW e2e test module. U-RT-94 composer-side substrate preserved (signal raise happens but driver does not catch — falls through to existing fail-class handling, which would mis-route the signal as `BaseException` propagation). Cluster 10-CP-B (already-landed pause-resume substrate) preserved unchanged.

---

## §4 — Coverage matrix delta

Coverage matrix delta at v2.23:

| Spec contract | Plan unit(s) |
|---|---|
| Runtime spec v1.24 §14.8.2 step 4-bis (NEW) | U-RT-94 |
| Runtime spec v1.24 §14.8.8.1 (durable-async composer body) | U-RT-94 |
| Runtime spec v1.24 §14.8.8.2 (`HITLPauseRequestedSignal` typed control-flow exception) | U-RT-93 |
| Runtime spec v1.24 §14.8.8.3 (`_evaluate_cell_synchrony_tolerant` helper) | U-RT-93 |
| Runtime spec v1.24 §14.8.8.4 (driver-side signal handling) | U-RT-95 |
| Runtime spec v1.24 §14.8.8.5 (resume-side one-shot delivery) | U-RT-94 |
| Runtime spec v1.24 §14.8.8.6 (composition with existing surfaces) | implicit (composes existing v1.23 surfaces; no new unit owed) |
| Runtime spec v1.24 §14.8.8.7 (6 invariants) | spread across U-RT-93/94/95 ACs |
| Runtime spec v1.24 §14.8.8.8 (5 deferred-to-impl-discretion) | implementer's call at U-RT-94 + U-RT-95 landing arcs |
| Runtime spec v1.24 NEW `RT-FAIL-HITL-WEBHOOK-DELIVERY-EXHAUSTED` fail class | U-RT-94 AC #5 (raise site) + U-RT-95 AC #5 (e2e fail-path verification) |
| Runtime spec v1.24 §14.14.7 deferral (i) RESOLVED status | covered by L9-terdecies cluster as a whole |
| Runtime spec v1.24 §14.8.3 v1.24 back-reference reconciliation note | informational; no AC owed |

Total coverage matrix rows added at v2.23: +10 (spec §14.8.8 sub-sections + NEW fail class + deferral (i) resolution + §14.8.2 step 4-bis insertion). Total plan unit columns added: +3 (U-RT-93/94/95). All coverage matrix cells populated; ZERO uncovered spec contracts.

---

## §5 — Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Harness_Runtime_v2_23.md` |
| Version | v2.23 |
| Filing event | Runtime spec v1.23 → v1.24 NEW §14.8.8 Durable-async cell HITL composition absorption per ratified scoping doc Q1-Q5 + D8 cite-correction |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_22.md` (substantive content preserved verbatim outside NEW L9-terdecies cluster addition) |
| Successor | (none — current canonical) |
| Co-published artifacts (this arc) | Workspace `CLAUDE.md` §2.4 runtime plan row bump v2.22 → v2.23; CP spec v1.16 (commit `aa841b0` prior); runtime spec v1.24 (commit `c73c25d` prior); CP plan v2.21 (this session prior); harness-cp impl (`pause_resume_protocol_types.py` ResumeContext + `pause_resume_protocol.py:295` signature widening + `workflow_driver.py` driver try-block catch at U-RT-95); harness-runtime impl (hitl_gate_composer.py amend at U-RT-93 + U-RT-94); NEW integration test at U-RT-95 |
| Operator authority | AskUserQuestion 2026-05-24 ("Ratified") at session opening checkpoint `20260524-130230` item #1; ratified scoping doc Q1-Q5 + D8 |
| Unit-count change | +3 (90 → 93) |
| Cluster-count change | +1 (NEW L9-terdecies) |
| DAG within-cluster edges added | +2 (U-RT-93 → U-RT-94 → U-RT-95 linear chain) |
| Cluster-boundary edges added | +6 (5 to already-landed substrate + 1 within-axis-cross-package to U-CP-64 at CP plan v2.21) |
| CXA cross-axis edges added | 0 (ZERO per scoping doc §3.3) |
| Coverage matrix rows added | +10 |
| Acceptance criterion count change | +18 (U-RT-93 ~4 ACs + U-RT-94 ~8 ACs + U-RT-95 ~6 ACs) |
| Cross-axis cascade | Within-axis-cross-package only (runtime plan v2.23 U-RT-94 depends on CP plan v2.21 U-CP-64); ZERO new CXA-level cross-axis edges |
| Skill discipline | `implementation-planner` Phase-7 revision-pass absorbing upstream runtime spec v1.24 §14.8.8 publication into NEW L9-terdecies cluster; fidelity-pure additive cluster authoring (3 NEW units + 2 within-cluster edges + 6 cluster-boundary edges + 10 coverage matrix rows); NO contract addition at spec level; NO acceptance criterion removal at any preserved unit; NO spec extension; 4 adjacent defects surfaced as findings per FM-2; preservation audit PASSED |
| Date | 2026-05-24 |
