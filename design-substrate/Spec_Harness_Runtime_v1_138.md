# Spec: Harness Runtime — v1.138 (delta over v1.137)

*Delta-only file. One contract amended: C-RT-23 (§14.13, text current at v1.132) keeps one CP async
`ValidatorFramework` instance per bootstrap on the context and gains NEW §14.13.8, which binds the
run-owned validator evaluation binding of CP v1.129 §28.11 to the Runtime execution ingresses. Every
other v1.137 and earlier term remains in force. Proposed v1.135/v1.136 deltas are not amended.*

**Status: PROPOSED — contract text for independent review and integration-lead ratification. Not
cleared; no source, CI, landing or installed claim.**

**Filed:** 2026-11-05

**Authority:** fork `.harness/class_1_fork_validator_run_binding.md`; Option A selected at LIT
`arhugula-harness-trial-193.4h4` `cmt-f47c682d-6ea5-4d9d-97c1-8d5b5f35531a`.

**Predecessor:** `Spec_Harness_Runtime_v1_137.md` (cleared). **Paired CP delta:**
`Spec_Control_Plane_v1_129.md`.

## §0 Change-note (v1.137 → v1.138)

| Site | Change |
|---|---|
| §14.13.2 inv 2–3, §14.13.5 inv 1 and 3 | Unchanged in substance. Clarified: the stage-4 factory returns the CP async Protocol instance itself (never a synchronous adapter); `HarnessContext.validator_framework` is typed `ValidatorFramework \| None`; the instance holds no per-run state |
| §14.13.3 "Stage-5 driver-hook fires" | The driver no longer invokes `ctx.validator_framework.evaluate`. It invokes the explicit run binding's synchronous `evaluate`, which runs the framework's async `evaluate` on the ingress event loop (CP v1.129 §28.11.2) |
| NEW §14.13.8 | Run binding lifetime, ingress coverage, nested and resume propagation |

## §14.13.8 Run-owned validator evaluation binding (NEW at v1.138)

1. **Single bootstrap resolution stays.** Stage 4 resolves the framework class bindings once per
   bootstrap. Opening a run binding performs no class resolution, registry construction or config
   read; it captures the existing instance.
2. **Root ingress opens exactly one binding per invocation.** The MCP `run_workflow` handler is the
   only root execution ingress: `api.run` and the CLI reach it through in-process MCP, and a resume
   re-enters it with `pause_snapshot_input`. On its event loop, before handing the driver to the
   worker thread, the handler opens
   `open_validator_run(ctx.validator_framework, result_timeout_seconds=...)` when the framework is
   not `None`, else passes `None`, and supplies it as `execute_workflow(..., validator_run=...)`.
3. **Child executions.** The driver passes its `validator_run` to sub-agent dispatch, which passes it
   to the child workflow runner; the runner calls `execute_workflow_at_depth(...,
   validator_run=parent.open_child())`, or `None` when the parent's is `None`. No other driver call
   site exists at base `41d98222`; a new one MUST take `validator_run` explicitly (the parameter has
   no default).
4. **Resume.** A resumed execution is a new `run_workflow` invocation and opens a fresh binding at
   zero. The burden count is not carried across a pause.
5. **Concurrency.** Concurrent invocations on one bootstrapped daemon each hold their own binding;
   one invocation's validator outcomes never change another's `burden_count`.
6. **No other carrier.** No run identity is added to `StepExecutionContext`; no binding is stored on
   `HarnessContext`, a module global or a `ContextVar`.
7. **Failure propagation unchanged.** Cost-hook and audit-signing failures reach the driver exactly
   as CP v1.124 and earlier specify. No new Runtime fail class.

## §14.13.9 Acceptance witnesses for the source correction

The correction implementing this delta MUST include behavioral witnesses for: sequential and
concurrent `run_workflow` invocations sharing one bootstrapped daemon, each starting at burden zero;
a child execution starting at zero without changing its parent; a real TOML-configured binding
reaching the driver with PASS, PERMANENT_FAIL and ESCALATE_HITL outcomes; the stage-4 factory return
satisfying the async Protocol while the driver receives the synchronous binding; cost-hook and
audit-signing failure propagation; `None` opt-out; and the prior 4h4 mutants staying red.

## Status

PROPOSED. Clears only by independent review GREEN of the exact head and integration-lead
ratification, followed by a clearance marker. The cross-trust palette gap at `workflow_driver.py:6047`
stays explicitly unaccepted. Source landing, CI and installed acceptance remain owed.
