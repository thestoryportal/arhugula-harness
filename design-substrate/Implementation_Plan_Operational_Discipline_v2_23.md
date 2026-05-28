# Implementation Plan: Operational Discipline — v2.23 (delta over v2.22)

---

## Change-note (v2.22 → v2.23)

**Scope of revision.** Substantive single-unit-body amendment at U-OD-40 (cost-attribution invocation at `validator.evaluate` + `hitl.webhook.deliver` sites) absorbing the production-binding lifecycle per the U-OD-40 bundled atomic-unit arc landing 2026-05-28. U-OD-40 status transits from `Implementation_Plan_Operational_Discipline_v2_14.md` §3.4 PENDING to **LANDED** at v2.23; carrier modules + production bindings + integration test verified empirically. ZERO new units; ZERO DAG topology change; ZERO coverage matrix structural delta; ZERO cross-axis cascade per fork-doc Q5=β ratification.

**Closure event.** U-OD-40 production binding empirically MET via single-session full arc per operator AskUserQuestion 2026-05-28 (Q1=single-session full arc). Co-published with:
- CP spec v1.23 → v1.24 NEW §28.10 `ValidatorPostEvaluateHook` Protocol authoring (X-AL-3 spec extension per `.harness/class_1_fork_u_od_40_validator_post_evaluate_hook.md` Reading (B) operator-ratified Q-set)
- CP plan v2.26 → v2.27 NEW U-CP-73 singleton-extension unit decomposing the Protocol surface authoring
- harness-cp impl extending `ConcreteValidatorFramework` ctor + `evaluate()` firing site with 13 NEW unit tests at `test_validator_framework_post_evaluate_hook.py`
- harness-runtime impl: NEW `lifecycle/cost_attribution_validator_dispatch.py` (CPU-meter formula per Decision 2.D5 RATIFIED) + NEW `lifecycle/cost_attribution_webhook_dispatch.py` (WebhookRate.flat_per_attempt + optional egress) + CostAttributingValidatorHook impl class + 18 NEW unit tests
- Validator factory `materialize_validator_framework_stage` signature widening per CP spec v1.24 §28.10.5 mechanism (a); stage_4_od.py:89 binding update
- WebhookDeliveryComposer ctor extension + inline best-effort wrap at `deliver_webhook` per U-OD-39 precedent
- NEW integration test `test_u_od_40_validator_webhook_integration.py` exercising AC #5 (1 validator + 1 webhook → 2 cost-records)
- Runtime plan v2.28 → v2.29 single-unit-body amendment at U-RT-84 absorbing the cost-attribution hook construction AC
- Batch-28 retirement event filing H_T-OD-5 PARTIAL → RETIRE-READY transit (surface coverage 2/4 → 4/4)

**v2.22 substantive content preserved verbatim.** All v2.22 content (fidelity-pure citation-correction patch closing v2.21 (c) docstring drift) preserved unchanged. U-OD-40 authoring site at `Implementation_Plan_Operational_Discipline_v2_14.md` §3.4 preserved verbatim per delta-only-plan-chain convention; v2.23 publishes a canonical-reading amendment table that downstream readers apply when interpreting U-OD-40 status.

**X-AL-3 + workspace `CLAUDE.md` §4.4 compliance.** Hook Protocol pattern (B) required spec extension at harness-cp ValidatorFramework Protocol surface — H_T design extension at Phase 7 execution-time → Class 1 fork filed + ratified before impl per workspace discipline. Fork doc anchor at `.harness/class_1_fork_u_od_40_validator_post_evaluate_hook.md`.

---

## §1 — U-OD-40 canonical-reading amendment

Per delta-only convention, U-OD-40 unit body at the v2.14 authoring file (`Implementation_Plan_Operational_Discipline_v2_14.md` §3.4) is NOT edited byte-exact; v2.23 publishes a canonical-reading amendment table that downstream readers apply when interpreting U-OD-40.

### §1.1 Status amendment

| Pre-v2.23 reading (v2.14 authoring + v2.15..v2.22 preserved) | v2.23 canonical reading |
|---|---|
| U-OD-40 status: PENDING (Depends on: U-CP-60 + U-RT-69 + U-OD-46) | **U-OD-40 status: LANDED 2026-05-28** at single-session bundled arc. All 3 cross-axis dependencies CLEARED at HEAD: U-CP-60 LANDED at Cluster 10-CP-A `b70e9a6`; U-RT-69 (WebhookDeliveryComposer carrier) LANDED at L9-quaterdecies `e394074`; U-OD-46 (RuntimeCostAttributionChain) LANDED at U-OD-38 lineage. Validator binding via NEW ValidatorPostEvaluateHook Protocol per CP spec v1.24 §28.10 + X-AL-3 fork ratification. Webhook binding via inline best-effort wrap per U-OD-39 precedent. |

### §1.2 ACs status

| AC | Pre-v2.23 status | v2.23 canonical reading |
|---|---|---|
| AC #1 — Validator CPU-meter cost (`execution_time_ms × cpu_rate_per_ms`) per Decision 2.D5 RATIFIED | PENDING | **LANDED** at `cost_attribution_validator_dispatch.py:_compute_validator_cost`; 5 unit tests cover integer ms / fractional ms / zero elapsed / zero rate / 17-sig-digit Decimal precision |
| AC #2 — Webhook cost = `WebhookRate.flat_per_attempt` + (optional egress) | PENDING | **LANDED** at `cost_attribution_webhook_dispatch.py:_compute_webhook_cost`; 5 unit tests cover flat-only / flat+egress / zero bytes with egress / zero flat with egress / Decimal precision |
| AC #3 — Cost-record attached at span exit | PENDING | **LANDED** at both `attribute_validator_dispatch_cost` + `attribute_webhook_dispatch_cost` substep 3 (build SpanCostRecord + attach idempotency-key via cost_chain.attach_idempotency_key); verified via test_attribute_*_returns_attached_record |
| AC #4 — Audit-ledger entry written | PENDING | **LANDED** at both helpers substep 4 + 5 (project to CostRecordAuditPayload + convert via cp_audit_to_od_audit `cost:` action_id prefix + audit_writer.append); verified via test_attribute_*_writes_audit_entry + multi-dispatch cardinality tests |
| AC #5 — Integration test: 1 validator + 1 webhook → 2 cost-records | PENDING | **LANDED** at `test_u_od_40_validator_webhook_integration.py::test_one_validator_plus_one_webhook_produces_two_cost_records`. Shared `_RecordingAuditWriter`; mock httpx 200 OK response; CostAttributingValidatorHook bound via Protocol; WebhookDeliveryComposer with cost-attribution substrates bound via ctor. Asserts 2 audit-ledger entries with per-surface action_id-prefix discrimination (workflow: vs hitl:). |

**AC count delta:** +0 (5 ACs preserved verbatim at v2.14 authoring; v2.23 amends status from PENDING to LANDED for each).

### §1.3 Files line amendment

| Pre-v2.23 reading | v2.23 canonical reading |
|---|---|
| `harness-cp/src/harness_cp/validator_framework.py` + `harness-runtime/src/harness_runtime/lifecycle/webhook_delivery_composer.py` (EXTEND) | EXTENDED per actual landing: `harness-cp/src/harness_cp/validator_framework_types.py` (NEW ValidatorPostEvaluateHook Protocol) + `harness-cp/src/harness_cp/validator_framework.py` (EXTEND ctor + evaluate firing) + `harness-runtime/src/harness_runtime/lifecycle/cost_attribution_validator_dispatch.py` (NEW module + CostAttributingValidatorHook) + `harness-runtime/src/harness_runtime/lifecycle/cost_attribution_webhook_dispatch.py` (NEW module) + `harness-runtime/src/harness_runtime/lifecycle/webhook_delivery_composer.py` (EXTEND ctor + inline-wrap) + `harness-runtime/src/harness_runtime/bootstrap/factories/validator_framework_factory.py` (EXTEND signature) + `harness-runtime/src/harness_runtime/bootstrap/stage_4_od.py` (EXTEND step 8 substrate threading) |

### §1.4 Signatures amendment

| Pre-v2.23 reading | v2.23 canonical reading |
|---|---|
| Cost-attribution hook at span exit | NEW `ValidatorPostEvaluateHook` Protocol (CP spec v1.24 §28.10.1) async on_post_evaluate(*, step, step_context, evaluation, execution_time_ms) → None; NEW `CostAttributingValidatorHook(rate_table, cost_chain, audit_writer)` impl class; NEW `attribute_validator_dispatch_cost(...)` + `attribute_webhook_dispatch_cost(...)` 5-substep helper functions; WebhookDeliveryComposer ctor extended with 7 optional cost-attribution substrate kwargs |

---

## §2 — Cross-axis cascade disposition

| Artifact | Status at v2.23 |
|---|---|
| CP spec v1.23 → v1.24 NEW §28.10 ValidatorPostEvaluateHook Protocol | **CO-PUBLISHED this arc** |
| CP plan v2.26 → v2.27 NEW U-CP-73 singleton-extension unit | **CO-PUBLISHED this arc** |
| Runtime spec | ZERO change (intra-axis CP Protocol; harness-runtime supplies impl via existing C-RT-23 factory) |
| Runtime plan v2.28 → v2.29 single-unit-body amendment at U-RT-84 cost-attribution hook AC | **CO-PUBLISHED this arc** |
| AS spec / OD spec / ADR / ADD / PRD / CXA | ZERO change per Q5=β ratification |
| harness-cp impl (Protocol + ctor + evaluate firing) | **CO-PUBLISHED this arc** at commit `9e502b0` |
| harness-runtime impl (modules + factory + composer) | **CO-PUBLISHED this arc** at commits `1c9ce1c` + `7247b1f` + `94f0333` |
| harness-od/CLAUDE.md H_T-OD-5 row refresh + batch-28 reference | **CO-PUBLISHED this arc** |
| Workspace CLAUDE.md §2.3 + §2.4 row bumps | **CO-PUBLISHED this arc** |
| batch-28 retirement event filing H_T-OD-5 PARTIAL → RETIRE-READY | **CO-PUBLISHED this arc** at `phase-7d-retirement-events-batch-28.md` |

---

## §3 — Sections preserved verbatim at v2.23

- All v2.22 content (fidelity-pure citation-correction patch closing v2.21 (c) docstring drift) PRESERVED VERBATIM.
- All v2.14..v2.22 substantive amendments PRESERVED VERBATIM.
- U-OD-40 unit body at v2.14 §3.4 PRESERVED VERBATIM (v2.23 §1 publishes canonical-reading amendment per delta-only-plan-chain convention).
- All other units (U-OD-00 through U-OD-39 + U-OD-41 through U-OD-54) PRESERVED VERBATIM.
- DAG topology v2.14 §3.1 + coverage matrix v2.14 §3.2 PRESERVED VERBATIM at structure (U-OD-40 status amendment is per-AC narrative-layer, not structural).

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Operational_Discipline_v2_23.md` |
| Version | v2.23 |
| Filing event | Substantive single-unit-body amendment at U-OD-40 absorbing production-binding lifecycle (PENDING → LANDED) per U-OD-40 bundled atomic-unit arc 2026-05-28 |
| Predecessor | `Implementation_Plan_Operational_Discipline_v2_22.md` (preserved verbatim outside the §1 amendment at v2.23) |
| Successor | (none — current canonical) |
| Unit count | 55 (unchanged from v2.22) |
| DAG topology | Preserved per v2.14 §3.1 + §3.2 (U-OD-40 status amendment is narrative-layer; no structural delta) |
| AC count delta | +0 (5 ACs preserved; status transit per-AC PENDING → LANDED at canonical-reading layer) |
| Cross-axis cascade | ZERO per fork-doc Q5=β ratification (NO new CXA typed edge; NO AS/OD spec/ADR/ADD/PRD amendment owed) |
| H_T-OD-5 status | Surface coverage 2/4 → 4/4 at this arc (validator + webhook surfaces wire); PARTIAL → RETIRE-READY transit at batch-28 retirement event filing co-published at this arc |
| Operator authority | `.harness/class_1_fork_u_od_40_validator_post_evaluate_hook.md` Q-set ratification 2026-05-28 + AskUserQuestion 2026-05-28 single-session full arc shape |
| Date | 2026-05-28 |
