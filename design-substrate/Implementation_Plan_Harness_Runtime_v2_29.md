# Implementation Plan — Harness Runtime (v2.29)

*Delta over v2.28. v2.29 is a single-unit-body canonical-reading amendment at U-RT-84 (the `materialize_validator_framework_stage` factory unit) absorbing the v1.24-widened signature per CP spec v1.24 §28.10.5 mechanism (a) cost-attribution hook construction. Unit count 99 → 99 (unchanged); ZERO new units; ZERO new cluster; ZERO DAG topology change; ZERO cross-axis cascade per Class 1 fork Q5=β ratification.*

## §0 Change note (v2.28 → v2.29)

### §0.1 Revision context — U-RT-84 absorbing CP spec v1.24 §28.10.5 mechanism (a)

Per `.harness/class_1_fork_u_od_40_validator_post_evaluate_hook.md` Reading (B) operator-ratified 2026-05-28 Q-set + co-publication at this arc with CP spec v1.24 NEW §28.10 ValidatorPostEvaluateHook Protocol + CP plan v2.27 NEW U-CP-73 unit + OD plan v2.23 U-OD-40 LANDED status + harness-cp/harness-runtime impl + batch-28 retirement event H_T-OD-5 PARTIAL → RETIRE-READY transit.

U-RT-84 (the runtime spec v1.18 §14.13 stage-4 factory for ValidatorFramework) accepts a widened signature per the factory's role as the canonical cross-axis adapter seam for cost-attribution hook construction:

- NEW optional kw-only params: `rate_table: RateTable | None = None`, `cost_chain: CostAttributionChain | None = None`, `audit_writer: AuditLedgerWriter | None = None`
- When ALL 3 substrates bound: factory constructs `CostAttributingValidatorHook(rate_table=..., cost_chain=..., audit_writer=...)` (from `harness_runtime.lifecycle.cost_attribution_validator_dispatch`) and injects via `ConcreteValidatorFramework(post_evaluate_hook=...)` ctor optional param
- When any substrate is None: hook=None passed; preserves pre-v1.24 behavior (cost-attribution disabled)
- Substrate threading at `bootstrap/stage_4_od.py:89` updated to pass `RATE_TABLE_V1 + ctx.cost_chain + ctx.audit_writer` through (stage 4 ordering at steps 6 + 7 binds cost_chain + audit_writer BEFORE step 8 validator framework)

### §0.2 Sections revised

§0 (this change note); U-RT-84 canonical-reading amendment table for the factory signature + AC + Tests-line refresh. All other unit bodies preserved verbatim from v2.28 per delta-only-plan-chain convention.

### §0.3 U-RT-84 canonical-reading amendment (NEW v2.29)

Per delta-only convention, U-RT-84 unit body at v2.17 authoring file (L9-decies cluster) is NOT edited byte-exact; v2.29 publishes a canonical-reading amendment table that downstream readers apply when interpreting U-RT-84.

**Signature amendment:**

| Pre-v2.29 reading (v2.17 + prior) | v2.29 canonical reading | Cite |
|---|---|---|
| `async def materialize_validator_framework_stage(config: RuntimeConfig) -> ValidatorFramework | None` | `async def materialize_validator_framework_stage(config: RuntimeConfig, *, rate_table: RateTable | None = None, cost_chain: CostAttributionChain | None = None, audit_writer: AuditLedgerWriter | None = None) -> ValidatorFramework | None` | CP spec v1.24 §28.10.5 mechanism (a) + this arc |
| Behavior: opt-in branch constructs empty-registry ConcreteValidatorFramework | NEW: opt-in branch additionally constructs `CostAttributingValidatorHook` when all 3 substrates bound + passes via post_evaluate_hook ctor; preserved-behavior at any substrate=None (hook=None passed; pre-v1.24 byte-identical) | Same |
| Stage 4 OD step 8 invocation: `ctx.validator_framework = await materialize_validator_framework_stage(config)` | `ctx.validator_framework = await materialize_validator_framework_stage(config, rate_table=RATE_TABLE_V1, cost_chain=ctx.cost_chain, audit_writer=ctx.audit_writer)` per `bootstrap/stage_4_od.py:89` | Same |

**AC amendment:** NEW AC #6 (cost-attribution hook construction).

| AC | Description |
|---|---|
| #1-#5 | Preserved verbatim from v2.17 L9-decies authoring |
| **#6 NEW** | When `(rate_table, cost_chain, audit_writer)` all bound at factory invocation + `config.validator_framework_config` is not None → ConcreteValidatorFramework is constructed with `post_evaluate_hook=CostAttributingValidatorHook(...)`. Verified empirically via integration test `test_u_od_40_validator_webhook_integration.py::test_one_validator_plus_one_webhook_produces_two_cost_records` exercising the full bootstrap stage 4 OD wire-up + validator framework evaluate() invocation + cost-attribution audit-ledger write. Per CP spec v1.24 §28.10.5 mechanism (a). |

**Tests-line delta:** +1 new integration test (`test_one_validator_plus_one_webhook_produces_two_cost_records` at `test_u_od_40_validator_webhook_integration.py`) + 2 in-place test updates (`test_factory_signature_accepts_config_returns_framework_or_none` widened for v1.24 signature; `test_stage_4_od_invokes_factory_after_audit_writer` relaxed for multi-line factory invocation shape).

### §0.4 Cross-axis dependency edges — preserved + 1 NEW intra-axis import

U-RT-84 cross-axis edges preserved from L9-decies authoring. NEW intra-axis import: `harness_runtime.lifecycle.cost_attribution_validator_dispatch.CostAttributingValidatorHook` (at the factory level). NO new cross-axis edge per CP spec v1.24 §28.10 fork Q5=β ratification (NO new CXA typed edge; factory binding is intra-axis runtime composition).

### §0.5 DAG topology — preserved

U-RT-84 sits at L9-decies per runtime plan v2.17 §3.1. v2.29 preserves the level placement — the new intra-axis import dependency on `cost_attribution_validator_dispatch` (L9-quindecies-equivalent runtime substrate, depends on RuntimeCostAttributionChain at L7-equivalent) does NOT inversion-create a level violation per the cost-attribution module's L7-equivalent placement.

### §0.6 Status posture

Proposed (v2.28) → **Proposed (v2.29)**. v2.29 is a single-unit-body canonical-reading amendment at U-RT-84. No prior unit body change; no DAG topology change; no cluster reorganization; no coverage matrix structural delta.

### §0.7 Adjacent defects surfaced (not patched per FM-2)

(i) **WebhookDeliveryComposer factory cost-attribution thread-through deferred.** The composer ctor at this arc accepts cost-attribution substrates as optional kwargs but `materialize_webhook_delivery_composer_stage` factory at `bootstrap/factories/webhook_delivery_composer_factory.py` does NOT yet thread them through from `ctx`. Future doc-hygiene arc may extend the factory signature analogous to U-RT-84 amendment at this arc; NOT patched at v2.29 per FM-2 (out-of-scope: would require runtime spec v1.26 §14.16 amendment for factory signature widening; OUT-OF-SCOPE at single-focus single-session arc). Reflects the structural-asymmetry between hook-Protocol pattern (validator side) and inline-wrap pattern (webhook side).

### §0.8 Downstream absorption owed (post-v2.29)

(a) Workspace `CLAUDE.md` §2.4 runtime plan row bump (v2.28 → v2.29). **Patched at v2.29 co-publication.**
(b) Co-published at v2.29 arc (CP spec v1.24 + CP plan v2.27 + harness-cp impl + harness-runtime impl + factory + composer + integration test + OD plan v2.23 + batch-28 retirement event). **Patched at v2.29 co-publication.**

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Harness_Runtime_v2_29.md` |
| Version | v2.29 |
| Filing event | Single-unit-body canonical-reading amendment at U-RT-84 absorbing CP spec v1.24 §28.10.5 mechanism (a) cost-attribution hook construction. 2026-05-28 |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_28.md` (preserved verbatim outside the §0.3 amendment at v2.29) |
| Successor | (none — current canonical) |
| Unit count | 99 (unchanged from v2.28) |
| DAG topology | Preserved per v2.17 §3.1 (U-RT-84 L9-decies placement unchanged) |
| AC count delta | +1 (NEW AC #6 at U-RT-84) |
| Cross-axis cascade | ZERO per Class 1 fork Q5=β ratification |
| H_T-OD-5 status | Validator surface wired at this arc; PARTIAL → RETIRE-READY transit at batch-28 retirement event filing co-published at this arc |
| Operator authority | `.harness/class_1_fork_u_od_40_validator_post_evaluate_hook.md` Q-set ratification 2026-05-28 |
| Date | 2026-05-28 |
