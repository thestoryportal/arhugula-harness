# Fork record — validator burden state moves to a run-owned evaluation binding

**Class:** 1 (design-substrate amendment), absorbed through the bundled back-flow of the 4h4
validator-binding slice (CLAUDE.md §4.3). Integration lead selected Option A as engineering
direction under the accepted release campaign (LIT `arhugula-harness-trial-193.4h4`,
`cmt-f47c682d-6ea5-4d9d-97c1-8d5b5f35531a`); that selection is not independent ratification.
Findings: `cmt-920364bd-adb4-4328-9335-b54cccbb1291` (F1, F2); normative-review finding F3
`cmt-c8295223-8d1d-4de0-acaf-d07c5b9ac67d` (no explicit driver-to-child route). Author grounding:
`cmt-b9802d8d-255a-41e4-bd59-6e32c20ff9ec`. No new H_T primitive and no new cross-axis edge: the
Runtime→CP dependency already exists through `ValidatorFramework` and the driver entry.

## Fork

- **What the contract requires.** C-CP-28 (v1.10 §25.4 invariant 5, renumbered §28 at v1.13) counts
  operator burden per workflow and resets it only at the workflow boundary, naming a field,
  `ctx.operator_burden_counter`, that no source defines. C-RT-23 (Runtime v1.132 §14.13.2 inv 2–3,
  §14.13.5 inv 1 and 3) binds one CP async `ValidatorFramework` Protocol instance per bootstrap to
  `ctx.validator_framework`, and §14.13.3 says the driver invokes that instance's async `evaluate`.
- **Why current source cannot meet it.** `ConcreteValidatorFramework` keeps `_burden_count` on the
  instance. One bootstrapped daemon serves every `run_workflow` call, so a second workflow starts at
  the first one's count (reviewer probe: PERMANENT_FAIL, then a later workflow's first PASS reports
  burden 1). The CP driver is synchronous and runs in a worker thread, so it already casts the context
  field to `SyncValidatorFrameworkFacade` (`workflow_driver.py` ~5901–5912 at base `41d98222`), which
  is not the async Protocol C-RT-23 requires.
- **What the existing seams provide.** Every driver execution enters through exactly two source call
  sites at base `41d98222`: the MCP `run_workflow` handler calls `execute_workflow` (root, fresh or
  resumed; `api.run` and the CLI reach it through in-process MCP), and the child workflow runner calls
  `execute_workflow_at_depth`. Run-tree values (`hitl_uniform_fallback_eligible_run_id`,
  effect-fence keys) and the opaque `child_resume_authority` already travel from the parent driver
  to the child runner on driver-composed `StepExecutionContext` fields, because
  `StepDispatcher.dispatch(binding, step, *, step_context)` has no other per-run channel.

## Disposition (Option A)

The bootstrap instance stays the one async Protocol-conforming framework on the context and holds
no run state. Burden state lives in a run-owned `ValidatorBurdenLedger` inside a CP
`ValidatorRunBinding`, opened by the root ingress on its event loop and passed to the driver as an
explicit argument. The binding is the driver's synchronous adapter. The driver hands it to sub-agent
dispatch on a hash-inert `StepExecutionContext.validator_run` field, and sub-agent dispatch opens
each child's own binding with `open_child()` for the child runner. Contract text: CP v1.129 §28.11
(§28.11.5 for the pass-through) and Runtime v1.138 §14.13.8.

**Rejected.** Resetting the shared instance at a boundary: concurrent runs on one daemon would still
share one counter. Option B (sync facade on the context plus run identity on `StepExecutionContext`)
was not selected. A `ContextVar` carrier was not selected: the binding is an explicit driver input,
not ambient state. Adding `validator_run` to `StepDispatcher.dispatch` was not selected: every
dispatcher and wrapper would change signature to forward a value only sub-agent dispatch reads,
while `StepExecutionContext` is the existing seam for driver-composed run-tree values.

## Retained gaps

- Burden is not carried across a pause. A resumed execution opens a fresh binding at zero; persisting
  the count would change the pause-snapshot schema, which this fork does not do.
- The cross-trust palette gap at `workflow_driver.py:6047` (`CrossTrustBoundaryState.NONE`) stays
  explicitly unaccepted and outside this fork.
- No source GREEN, CI, landing or installed acceptance is claimed. Source correction follows only
  after independent normative GREEN and integration-lead ratification of the exact contract head.
