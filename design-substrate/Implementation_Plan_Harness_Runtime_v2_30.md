# Implementation Plan — Harness Runtime (v2.30)

*Delta over v2.29. v2.30 is a single-unit-body canonical-reading amendment at U-RT-94 absorbing the runtime spec v1.34 Reading (H) signature-divergence resolution per `.harness/class_1_fork_webhook_composer_per_workflow_context_threading.md` operator-ratified 2026-05-28. Unit count 99 → 99 (unchanged); ZERO new units; ZERO new cluster; ZERO DAG topology change; ZERO U-RT-97 factory amendment; ZERO cross-axis cascade.*

## §0 Change note (v2.29 → v2.30)

### §0.1 Revision context — Reading (H) absorption at U-RT-94

Per `.harness/class_1_fork_webhook_composer_per_workflow_context_threading.md` Reading (H) operator-ratified 2026-05-28 + runtime spec v1.34 absorption. The original fork doc Q-set (Q1=A per-call params + Q2 mirror validator factory mechanism (a)) was retracted at empirical-orientation discovery 2026-05-28 — the underlying defect is signature-divergence (spec 2-arg `deliver_webhook(brief, idempotency_key)` vs production 3-arg `deliver_webhook(webhook_config, payload, idempotency_key)`), not per-workflow context threading. Operator re-routed via NEW AskUserQuestion 2026-05-28: Reading (H) hybrid-with-adapter + single-session apply ratified.

U-RT-94 (the `WebhookDeliveryComposer` carrier class body unit landed at runtime spec v1.26 §14.10.1) accepts an ADDITIVE refactor shape:

- NEW optional ctor kw-only param: `webhook_config: WebhookConfig | None = None` (required when brief surface used)
- NEW public method `deliver_webhook_for_brief(brief: HITLEscalationBrief, idempotency_key: str) -> WebhookDeliveryResult` — spec-canonical 2-arg surface; internally projects brief → `WebhookPayload` via `webhook_brief_adapter.project_brief_to_payload(...)` adapter (NEW module); dispatches via existing raw 3-arg `deliver_webhook(...)` surface using ctor-supplied `webhook_config`; raises `RuntimeError` when `webhook_config is None`
- NEW adapter module reference at `harness-runtime/src/harness_runtime/lifecycle/webhook_brief_adapter.py` with single function `project_brief_to_payload(brief, idempotency_key) -> WebhookPayload`
- Existing raw 3-arg `deliver_webhook(webhook_config, payload, idempotency_key)` public surface PRESERVED VERBATIM; existing ctor field-set PRESERVED VERBATIM (additive new param only); existing cost-attribution `_attribute_webhook_cost_best_effort` PRESERVED VERBATIM
- Caller at `hitl_gate_composer.py:1002` updates from `await self.webhook_delivery_composer.deliver_webhook(durable_brief, idempotency_key)` to `await self.webhook_delivery_composer.deliver_webhook_for_brief(durable_brief, idempotency_key)` — pre-v1.34 the caller passed 2 args to the 3-arg signature (dead code); post-v1.34 the caller is coherent against the NEW brief surface

ZERO U-RT-97 factory amendment — factory does NOT thread cost-attribution substrates at this arc per fork doc §0.2 final paragraph (cost-attribution per-workflow concern remains orthogonal to signature-divergence resolution).

### §0.2 Sections revised

§0 (this change note); U-RT-94 canonical-reading amendment table for additive surface + AC + Tests-line refresh. All other unit bodies preserved verbatim from v2.29 per delta-only-plan-chain convention. U-RT-97 PRESERVED VERBATIM.

### §0.3 Audit-trail preservation

v2.30 was initially drafted as a paired single-unit-body amendment at U-RT-94 + U-RT-97 absorbing the original Reading (A) per-call params framing. That initial framing is RETRACTED-AT-DISCOVERY per fork doc §0 (commit `e378c9b` reframe-retraction); v2.30 final content reflects Reading (H) per fork doc §0.1 ratification (this commit). The original retraction record is preserved at git history (`e378c9b`); the v2.30 file body reflects the final Reading (H) absorption.

### §0.4 ZERO cross-axis cascade

Per fork doc §0.1 reading: intra-runtime-spec interface contract change. NO CP spec amendment owed (CP-axis types `HITLEscalationBrief` + `WebhookConfig` + `WebhookPayload` consumed as-is at adapter module + composer ctor; no CP-axis surface change). NO OD spec amendment owed. NO AS spec amendment owed. NO CXA amendment owed. NO ADR / ADD / PRD amendment owed.

---

## §1 U-RT-94 canonical-reading amendment

| Field | v2.29 | v2.30 amendment |
|---|---|---|
| Implements | C-RT-20 §14.10.1 WebhookDeliveryComposer carrier | C-RT-20 §14.10.1 WebhookDeliveryComposer carrier (with v1.34 Reading H additive brief surface) |
| Signatures (`__init__`) | 13-param ctor (5 retry/HTTP + 3 cost + 4 workflow-context + 1 sleep_fn) | **14-param ctor** — additive NEW kw-only `webhook_config: WebhookConfig \| None = None`; existing 13 params PRESERVED VERBATIM |
| Signatures (`deliver_webhook` raw 3-arg) | `deliver_webhook(webhook_config, payload, idempotency_key) -> WebhookDeliveryResult` | **PRESERVED VERBATIM** |
| Signatures (NEW `deliver_webhook_for_brief`) | — | **`deliver_webhook_for_brief(brief: HITLEscalationBrief, idempotency_key: str) -> WebhookDeliveryResult`** — spec-canonical 2-arg surface; projects via adapter + dispatches via raw surface; raises RuntimeError when ctor `webhook_config` is None |
| Signatures (NEW adapter module) | — | **`webhook_brief_adapter.project_brief_to_payload(brief, idempotency_key) -> WebhookPayload`** — faithful field projector at new module `harness-runtime/src/harness_runtime/lifecycle/webhook_brief_adapter.py` |
| AC #N — NEW additive ctor param | — | **NEW AC:** ctor accepts optional `webhook_config: WebhookConfig \| None = None`; pre-existing ctor field-set preserved |
| AC #N — NEW brief surface | — | **NEW AC:** `deliver_webhook_for_brief(brief, idempotency_key)` projects via adapter + dispatches via raw `deliver_webhook(self._webhook_config, payload, idempotency_key)` |
| AC #N — NEW adapter projection | — | **NEW AC:** `project_brief_to_payload` maps `approval_id ← brief.parent_action_id`, `idempotency_key ← per-call`, `gate_evaluation_ref ← brief.parent_action_id`, `payload_body ← {escalation_reason, parent_step_id, fail_class, fail_detail_hash, proposed_response_palette}` |
| AC #N — NEW raise on missing webhook_config | — | **NEW AC:** `deliver_webhook_for_brief` raises `RuntimeError` when `self._webhook_config is None` |
| Tests-line NEW | — | 5 NEW adapter tests (`test_lifecycle_webhook_brief_adapter.py`) + 3 NEW composer brief-surface tests appended to `test_lifecycle_webhook_delivery_composer.py` (`test_deliver_webhook_for_brief_raises_when_webhook_config_missing` + `test_deliver_webhook_for_brief_dispatches_via_raw_surface` + `test_deliver_webhook_for_brief_propagates_exhausted_error`) |
| Files | `webhook_delivery_composer.py` | + NEW `webhook_brief_adapter.py` |

## §2 U-RT-97 PRESERVED VERBATIM

ZERO amendment at U-RT-97 per Reading (H) — factory does NOT thread cost-attribution substrates at this arc. Original v2.29 U-RT-97 body preserved.

---

## §3 Adjacent observations (carry-forward)

(a) **OD-5 RETIRE-READY status preserved.** v2.30 does NOT advance OD-5 to RETIRED; deployment-time gate per AS-8d batch-25 precedent unchanged.

(b) **Cost-attribution per-workflow concern remains orthogonal.** The composer's existing ctor params (`workflow_id` / `parent_action_id` / `parent_idempotency_key` / `tenant_id`) + cost substrate params (`rate_table` / `cost_chain` / `audit_writer`) remain operative for cost-attribution at both raw and brief surfaces. Bootstrap-singleton default path stays cost-attribution-off (workflow_id=None → skip per existing guard). Operator construction per-workflow (with workflow context + cost substrates + webhook_config supplied) gets cost-attribution at brief surface. Same behavioral split as pre-v1.34; not amended at this arc.

(c) **Caller at `:1002` now LIVE.** Pre-v1.34 the caller passed 2 args to a 3-arg signature — dead code (would TypeError if reached). v1.34 makes the call coherent. Bootstrap-singleton WITHOUT webhook_config still raises RuntimeError at brief surface — opt-in via operator-supplied webhook_config is the activation path.

---

## §4 Filing footer

| Field | Value |
|---|---|
| Filed at | 2026-05-28 |
| Filer | Class 1 fork apply pass per `.harness/class_1_fork_webhook_composer_per_workflow_context_threading.md` Reading (H) ratification |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_29.md` (2026-05-28, U-RT-84 v1.24 absorption) |
| Co-publication | runtime spec v1.34 + harness-runtime impl (webhook_brief_adapter.py NEW + composer ctor + brief surface + caller update) + 8 NEW tests + workspace `CLAUDE.md` row bumps |
| Cross-axis cascade | ZERO per fork doc §0.1 + §0.4 |
| Status | ✅ FILED |
