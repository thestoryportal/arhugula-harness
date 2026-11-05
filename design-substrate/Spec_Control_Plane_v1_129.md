# Spec: Control Plane — v1.129 (delta over v1.124)

*Delta-only file. Two amendment sites in C-CP-28: the per-workflow burden counter moves from the
shared framework instance into a run-owned ledger (amending v1.10 §25.4 invariant 5, renumbered §28 at
v1.13), and NEW §28.11 defines the run-owned evaluation binding that is the driver's synchronous
adapter. Every other v1.124 and earlier C-CP-01 … C-CP-29 term remains in force, including §28.10
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
  ledger at zero. Callable from the driver's worker thread.

### §28.11.2 Synchronous evaluation

`ValidatorRunBinding.evaluate(step, step_result, *, step_context) -> ValidatorEvaluation` schedules
`framework.evaluate(step, step_result, step_context=step_context, burden=self.burden)` on `loop`
with `asyncio.run_coroutine_threadsafe` and blocks on the result with `result_timeout_seconds`.
Exceptions raised by the coroutine, including post-evaluate hook and audit-signing failures that
§28.10 already lets escape, propagate verbatim. Concurrent evaluations within one execution
(parallel branches) share that execution's ledger; increments are serialized by the single loop.

### §28.11.3 Lifetime

1. One binding per workflow execution. A binding is never stored on the context, a module global or
   a `ContextVar`; it travels only as the explicit `validator_run` argument.
2. `validator_run is None` exactly when the bootstrap framework is `None` (operator opt-out). The
   driver's post-dispatch hook (§28.3.3.4) runs when `validator_run is not None` and calls
   `validator_run.evaluate(...)`; 5-class outcome routing is unchanged.
3. A child workflow execution receives `parent.open_child()`: each child is its own workflow
   boundary and starts at zero. The parent's ledger is not changed by the child.
4. No reset operation exists. Two executions never share a ledger unless they are the same execution.

### §28.11.4 Failure modes

No new fail class. A timeout on the blocking result surfaces as the existing
`CP-FAIL-VALIDATOR-EXECUTION`; a missing registry entry stays `CP-FAIL-VALIDATOR-CATALOG-MISSING`.

## §3 Status

PROPOSED. Clears only by independent review GREEN of the exact head and integration-lead
ratification, followed by a clearance marker. Source landing, CI and installed acceptance remain owed.
