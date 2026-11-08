# Spec: Control Plane — v1.129 (delta over v1.124)

*Delta-only file. Two amendment sites in C-CP-28: the per-workflow burden counter moves from the
shared framework instance into a run-owned ledger (amending v1.10 §25.4 invariant 5, renumbered §28 at
v1.13), and NEW §28.11 defines the run-owned evaluation binding that is the driver's synchronous
adapter and its explicit driver-to-child pass-through on `StepExecutionContext` (C-CP-25 §25.3.3.4). Every other v1.124 and earlier C-CP-01 … C-CP-29 term remains in force, including §28.10
post-evaluate hook semantics. Proposed v1.125–v1.128 are not heads and are not amended here.*

**Status: PROPOSED — contract text for independent review and integration-lead ratification. Not
cleared; no source, CI, landing or installed claim.**

**Filed:** 2026-11-05

**Authority:** fork `.harness/class_1_fork_validator_run_binding.md`; Option A selected at LIT
`arhugula-harness-trial-193.4h4` `cmt-f47c682d-6ea5-4d9d-97c1-8d5b5f35531a`.

**Predecessor:** `Spec_Control_Plane_v1_124.md` (cleared). **Paired Runtime delta:**
`Spec_Harness_Runtime_v1_138.md`.

## §0 Change-note (v1.124 → v1.129)

| Site | Before | After |
|---|---|---|
| C-CP-28 burden invariant (v1.10 §25.4 inv 5) | Tracked on `ctx.operator_burden_counter` (no such field exists); landed source kept it on the framework instance | Tracked on the run-owned `ValidatorBurdenLedger` of §28.11; the framework instance holds no run state |
| §28.1 `ValidatorFramework.evaluate` | `evaluate(step, step_result, *, step_context)` | `evaluate(step, step_result, *, step_context, burden: ValidatorBurdenLedger)` |
| NEW §28.11 | — | `ValidatorBurdenLedger`, `ValidatorRunBinding`, `open_validator_run`, `ValidatorRunBinding.open_child` |
| Driver input | Driver reads `ctx.validator_framework` and casts it to `SyncValidatorFrameworkFacade` | Driver takes `validator_run: ValidatorRunBinding \| None` as an explicit argument of `execute_workflow` and `execute_workflow_at_depth`; the driver context Protocol no longer declares `validator_framework` |
| Sync bridge | `SyncValidatorFrameworkFacade`, `materialize_sync_validator_framework_facade` | Retired; `ValidatorRunBinding` is the only synchronous adapter |
| `StepExecutionContext` (C-CP-25 §25.3.3.4) | No validator field | Gains hash-inert, non-persistent `validator_run: ValidatorRunBinding \| None`, composed by the driver from its `validator_run` argument (§28.11.5). `StepDispatcher.dispatch` is unchanged |

## §1 Amended invariant — burden count per workflow execution

Invariant 5 now reads: **Burden count is monotonic within one workflow execution.** It is held by the
`ValidatorBurdenLedger` of that execution's `ValidatorRunBinding`, starts at zero when the binding is
opened, and is never reset. A workflow boundary is the opening of a new binding (§28.11.3). The
framework instance MUST NOT store a burden count or any other per-execution state.

`evaluate` increments `burden.count` on each non-PASS outcome and copies the post-increment value to
`ValidatorEvaluation.burden_count` and `validator.burden_count_cumulative`. The increment and the
copy happen with no intervening `await`, on the binding's event loop.

## §2 NEW §28.11 — Run-owned evaluation binding

### §28.11.1 Types

- `ValidatorBurdenLedger` — run-owned mutable cell, `count: int`, constructed only by
  `open_validator_run` and `open_child` with `count = 0`. Mutated only by `ValidatorFramework.evaluate`.
- `ValidatorRunBinding` — frozen: `framework: ValidatorFramework` (the shared bootstrap instance),
  `burden: ValidatorBurdenLedger`, `loop: asyncio.AbstractEventLoop`, `result_timeout_seconds: float`.
  It does not satisfy and does not claim the async `ValidatorFramework` Protocol.
- `open_validator_run(framework, *, result_timeout_seconds) -> ValidatorRunBinding` — MUST be called
  from a coroutine on the loop that will serve the run's evaluations; captures that running loop.
- `ValidatorRunBinding.open_child() -> ValidatorRunBinding` — same framework, loop and timeout; new
  ledger at zero. Callable from any dispatch worker thread: it constructs a new ledger and mutates no
  existing state.

### §28.11.2 Synchronous evaluation

`ValidatorRunBinding.evaluate(step, step_result, *, step_context) -> ValidatorEvaluation` schedules
`framework.evaluate(step, step_result, step_context=step_context, burden=self.burden)` on `loop`
with `asyncio.run_coroutine_threadsafe` and blocks on the result with `result_timeout_seconds`.
Exceptions raised by the coroutine, including post-evaluate hook and audit-signing failures that
§28.10 already lets escape, propagate verbatim. Concurrent evaluations within one execution
(parallel branches) share that execution's ledger; increments are serialized by the single loop.

### §28.11.3 Lifetime

1. One binding per workflow execution. A binding is never stored on `HarnessContext`, a module
   global or a `ContextVar`. It travels as the explicit `validator_run` argument of the driver entry
   points, and from the driver to sub-agent dispatch only as the driver-composed
   `StepExecutionContext.validator_run` field of §28.11.5.
2. `validator_run is None` exactly when the bootstrap framework is `None` (operator opt-out). The
   driver's post-dispatch hook (§28.3.3.4) runs when `validator_run is not None` and calls
   `validator_run.evaluate(...)`; 5-class outcome routing is unchanged.
3. A child workflow execution receives `parent.open_child()`, opened by sub-agent dispatch once per
   child execution (Runtime v1.138 §14.13.8(3)): each child is its own workflow boundary and starts
   at zero, at every depth. The parent's ledger is not changed by the child, and sibling children
   never share a ledger.
4. No reset operation exists. Two executions never share a ledger unless they are the same execution.

### §28.11.4 Failure modes

No new fail class. A timeout on the blocking result surfaces as the existing
`CP-FAIL-VALIDATOR-EXECUTION`; a missing registry entry stays `CP-FAIL-VALIDATOR-CATALOG-MISSING`.

### §28.11.5 Driver-to-child pass-through

1. **Field.** `StepExecutionContext` (`harness_cp/workflow_driver_types.py`) gains
   `validator_run: ValidatorRunBinding | None = Field(default=None, exclude=True, repr=False)`, the
   same carrier shape as the existing `child_resume_authority`. It is absent from every `model_dump`,
   so it never enters a hash, audit entry, ledger row or pause snapshot.
2. **Single composer.** The driver sets `validator_run=<the execution's validator_run argument>` at
   every `StepExecutionContext` it constructs, beside `child_resume_authority`. At the frozen source
   head `4a5ce5e2` these are the five `workflow_driver.py` sites at lines 5618 (linear step), 8562
   (fan-out parent), 11458 (step dispatch), 12804 (orchestrator) and 16128 (spawning stage). Branch
   and worker contexts inherit the value through `compose_branch_child_context`'s `model_copy`; they
   belong to the same execution and share its ledger (§28.11.2). A new driver construction site sets
   the field explicitly.
3. **Readers.** Runtime sub-agent dispatch is the only reader (Runtime v1.138 §14.13.8(3)).
   `ValidatorFramework.evaluate` MUST NOT read `step_context.validator_run`; it receives the ledger
   only as its `burden` argument. Inner LLM, retry/fallback and sandbox dispatchers ignore the field.
4. **Capability, not identity.** The field holds the execution's binding object. It carries no run
   identifier, and no shared map is keyed by it. Option B (a run identity on `StepExecutionContext`
   resolved against shared framework state) remains not selected.
5. **Default.** `[LAW:types-are-the-program] exception`: the field defaults to `None`, as
   `child_resume_authority` does, because making it required would change 60 test constructions in
   53 files outside this slice. Non-driver constructions keep `None`; at base the only one is the
   Runtime model-tool loop (`r_cxa_2_producer_loop_factory.py`), which dispatches model tool calls
   to `ctx.tool_dispatcher` and cannot reach sub-agent dispatch. The Runtime v1.138 §14.13.9 nested
   witnesses and their drop-the-field mutants are the enforcement for every driver site.

## §3 Status

PROPOSED. Clears only by independent review GREEN of the exact head and integration-lead
ratification, followed by a clearance marker. Source landing, CI and installed acceptance remain owed.
