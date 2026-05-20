# Fork — U-RT-49 cost-attribution invocation underspec (sub-fork of [[fork_u_rt_44_workflow_loop_drain]])

**Class:** 1 (halt-execution; spec gap blocks un-strike)
**Status:** 🛑 OPEN — filed 2026-05-20 during U-RT-49 residual-closure orientation
**Parent fork:** `.harness/class_1_tension_u_rt_44_workflow_loop_drain.md` (CLOSED-PARTIAL); this sub-fork carries the sole cost-attribution residual that the parent's CLOSED-PARTIAL footer cites.
**Predecessor reference:** `.harness/class_1_tension_u_od_21_span_cost_record_missing_rollup_keys.md` (RESOLVED 2026-05-16 at OD plan v2.8 D-5; U-OD-20 grew to 12 fields at commit `600b902`; U-OD-21 `rollup_costs_by_axis` landed at commit `e8fae9c`). **The OD-side residual the U-RT-49 fork-extension record cited as the blocker is source-resolved; the actual residual lives at the CP driver + spec layer, not at OD. This sub-fork relocates the residual to its correct home.**

## Defect

`Implementation_Plan_Operational_Discipline_v2_11.md` U-OD-20 (`SpanCostRecord` 12 fields) and U-OD-21 (`rollup_costs_by_axis` + `CrossFamilyCostRollup` + `RollupAxis`) are both landed in `harness-od/src/harness_od/` at HEAD `9f7556c`. The cost-attribution chain is wired at bootstrap stage 4 (`harness-runtime/src/harness_runtime/bootstrap/stage_4_od.py:75-76` — `ctx.cost_chain = materialize_cost_attribution_stage(config).chain`). The Lane 6 commit `819c721` landed CP-driver workflow execution at C-CP-25.

Despite all three of these landing events, **the U-RT-49 acceptance criterion "cost attribution chain produced an entry" remains structurally un-satisfiable** because:

**Gap 1 — CP workflow driver does not invoke cost-attribution chain.**
`harness-cp/src/harness_cp/workflow_driver.py` contains zero references to `cost_chain`, `compute_per_attempt_cost`, `SpanCostRecord`, or any cost-attribution surface. The driver iterates workflow steps, dispatches via topology, emits ledger entries + lifecycle events (per C-CP-25 §25.3.3 + §25.5), and returns. No step in this loop fires the cost-attribution chain. The `DriverContext` Protocol (line 174) declares `ledger_writer` + `lifecycle_event_emitter` field obligations; it does NOT declare a `cost_chain` obligation, so the driver could not invoke cost-attribution even if it tried.

**Gap 2 — No spec authority states when cost-attribution fires during workflow step lifecycle.**
- `Spec_Harness_Runtime_v1.md` §10 / §11: names `ctx.cost_chain` only as a *bootstrap-materialized* slot; gives no lifecycle invocation contract. §10 step 2 mentions "flush cost-attribution chain in-memory state to audit ledger" — but per `.harness/class_3_drift_u_rt_45_cost_chain_stateless.md` the chain is stateless and this flush is a documented no-op. The spec is silent on per-step cost-attribution invocation.
- `Spec_Control_Plane_v1_3.md` C-CP-25 (workflow driver): no `cost_chain` term anywhere; §25.3.3 (ledger-entry emission) + §25.5 (lifecycle-event emission) are the only per-step emission contracts. Cost-attribution emission is unmentioned.
- `Spec_Operational_Discipline_v1_4.md` C-OD-14 / C-OD-15 (cost-attribution surfaces): specifies what `compute_per_attempt_cost` does, what `SpanCostRecord` shape is, what rollup axes exist. Does not specify which axis (CP driver? runtime stage handler? lifecycle emitter? some new component?) invokes the chain per workflow step.

No implementation-discretion clause survives reading: the three specs each leave the invocation surface unaddressed, not "discretion to choose." This is a contract gap, not a discretion latitude (compare to U-CP-56 resumption, where CP §6.1 "additional fields" + IS §7.4 "specific navigation primitives" discretion clauses absorbed the entire resolution).

**Gap 3 — `PRICE_TABLE_REF` substitution still deferred.**
`harness-od/src/harness_od/cost_formula.py:69` has:

```python
PRICE_TABLE_REF: PriceTableRef = PriceTableRef("od-price-table-ref::deferred-to-U-OD-21")
```

`_lookup_rates(table_ref, key)` (line 174) raises `RateLookupError` unconditionally: "no resident rate table — PRICE_TABLE_REF resolves at U-OD-21." Callers that hold an explicit `PriceRateEntry` can use `compute_span_cost_with_rates` to bypass the lookup, but no rate-snapshot story exists at HEAD — nothing else in the workspace constructs `PriceRateEntry` values. So even if the CP driver invoked the chain with full input attribution, the chain cannot produce a `SpanCostRecord` unless someone supplies the rate snapshot first.

This is a substitution-mechanism gap, not a defect at U-OD-21 itself. U-OD-21 landed `CrossFamilyTag` / `RollupAxis` / `CrossFamilyCostRollup` / `rollup_costs_by_axis` / `TokenizerVersionAnchor` / `TOKENIZER_VERSION_ANCHOR_REQUIREMENT` / `FallbackChainCostComposition`. **It did not author a rate table.** The deferred substitution string in `cost_formula.py:69` was authored before U-OD-21 landed; whether U-OD-21 was *meant* to land the rate table (and the unit definition under-specified) or whether `PRICE_TABLE_REF` was always intended to resolve at deployment-binding time (per `cost_formula.py:184` "the concrete rate table resides at U-OD-21 / deployment-binding-time refresh") is itself an ambiguity worth recording.

## Why these are Class 1, not Class 3

Class 3 would mean: documentable drift, no AC failure at HEAD. But the U-RT-49 cost-attribution AC is STRUCK precisely because the chain cannot produce an entry along the workflow execution path. The struck AC is the directly observable AC failure, and three independent gaps must close before it un-strikes. Each gap requires a design-substrate-level decision (where in the lifecycle; what spec; what substitution). This matches the U-CP-56 resumption fork shape exactly.

## Design questions for operator ratification

The fork halts. Operator decisions needed before any implementation:

**Q1 — Lifecycle invocation site.** Where does the cost-attribution chain fire per workflow step?
- **Q1a:** Inside the CP workflow driver `_execute_step` loop (driver gains a `cost_chain` `DriverContext` field obligation).
- **Q1b:** Inside the runtime lifecycle emitter (lifecycle event consumer wires cost-attribution as a side-effect of step-completed events).
- **Q1c:** Inside a new per-step OD-axis consumer that subscribes to lifecycle events (analogous to the LedgerWriterLike / LifecycleEventEmitterLike separation).
- **Q1d:** Some other surface (operator-specified).

Each option implies a different spec amendment: Q1a → CP spec C-CP-25 amendment + a new field on `DriverContext`; Q1b → runtime spec §10 amendment naming cost-attribution as a lifecycle-emitter side effect; Q1c → OD spec amendment adding a per-step consumer surface; Q1d → operator authoring.

**Q2 — Input attribution.** Where does the CP driver (or whoever fires the chain) source the `SpanCostInputs` fields?
- `model` (which provider/model the step invoked) — currently the CP driver doesn't know this, because per-step provider selection happens inside the role-routing layer and the driver receives a topology dispatch result, not a provider identity.
- `input_tokens` / `output_tokens` — currently nowhere in the CP driver result; would need provider clients to surface token counts on completion.
- `rate_key` — synthesized from `(model, provider)` per OD §14.1; trivial once `model` + `provider` are known.

Q2 likely requires a new shared type (e.g., `StepExecutionResult` carrying token counts + provider/model attribution) shared between provider clients → CP driver → cost-attribution consumer. This is a CXA-style cross-axis composition seam.

**Q3 — Rate substitution at this phase.**
- **Q3a:** Land a minimal hard-coded rate table inside OD (Anthropic / OpenAI / Ollama) for the 3 committed providers. Authoring task; closes the `PRICE_TABLE_REF` substitution.
- **Q3b:** Carry the deferred substitution forward; require the workflow-step execution path to construct an explicit `PriceRateEntry` and route through `compute_span_cost_with_rates`. (Punts the rate-table authoring to a later phase.)
- **Q3c:** File a separate fork for the rate-table substitution; resolve Q1 + Q2 first and let the chain produce a `SpanCostRecord` with a placeholder rate; un-strike the U-RT-49 AC as "chain *produced an entry*" without requiring real-cost computation. The AC text supports this literal reading.

**Q4 — Scope.** Is this fork in scope for the next session, or does it carry forward as a bounded-residual until Phase 7 sub-phase 7c (cross-axis composition) opens? It is the **sole remaining residual** on the parent `fork_u_rt_44_workflow_loop_drain` (which is CLOSED-PARTIAL); deferring it leaves the parent fork's CLOSED-PARTIAL footer accurate but uncloses U-RT-49 AC indefinitely.

## Materializable surface (if Q3c chosen)

If operator selects Q3c (literal "chain produced an entry" reading), the un-strike path is roughly:
1. Spec amendment per Q1 choice (a single section addition, ~20-40 lines).
2. New shared type per Q2 (`StepExecutionResult` or equivalent) at `harness-core` (since both CP driver and OD consumer touch it).
3. CP driver wires cost-attribution invocation per Q1 choice (~50-100 LOC).
4. `harness-runtime/tests/integration/test_run_smoke.py` extends to invoke a workflow step, capture the emitted `SpanCostRecord`, un-strike U-RT-49 AC #5.

If operator selects Q3a or Q3b (real-cost computation), add the rate-snapshot authoring (~100-200 LOC, OD-axis).

## Routing

**Halt-execution.** No implementation begins until operator selects Q1 / Q2 / Q3 / Q4 paths. After ratification:
- Per Q1 choice: surface a runtime-spec amendment OR a CP-spec amendment OR an OD-spec amendment. Use the existing in-CLI spec-revision-pass discipline (per memory `[[design-substrate-divergence]]`).
- Per Q2 / Q3 choices: surface the corresponding plan amendments at `Implementation_Plan_Control_Plane_v2_NN.md` and/or `Implementation_Plan_Operational_Discipline_v2_NN.md`.

## Files touched by this filing

- `.harness/fork_u_rt_49_cost_attribution_invocation_underspec.md` (this file, NEW)
- `.harness/fork_u_rt_49_workflow_execution_extends_u_rt_44.md` — STRIKE-row footnote updated to point at this sub-fork instead of the (resolved) `fork-u-od-21`
- `.harness/class_1_tension_u_rt_44_workflow_loop_drain.md` — residual line updated
- `.harness/class_1_tension_u_od_21_span_cost_record_missing_rollup_keys.md` — footer extended noting source-landing event (commits `600b902` + `e8fae9c`) and pointer to this sub-fork

## Provenance

- Resumption from checkpoint `20260520-060615-cp-56-resumption-fork-closed-v2-12-merged.md` (operator selection: option A — resolve `fork-u-od-21` to close U-RT-44 parent).
- Orientation surfaced: OD-side already source-resolved (commits cited above); actual residual is CP-driver + spec gap. AskUserQuestion (operator response: file the sub-fork; gather questions; halt).
- Pattern: same shape as `[[fork-u-cp-56-resumption-underspec]]` — landed unit chain reveals downstream spec gap; surface to operator before implementation.
