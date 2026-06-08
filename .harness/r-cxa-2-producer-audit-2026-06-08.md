# R-CXA-2 Producer Audit — 2026-06-08

Audit HEAD: `4baefe0b` (`ops: roadmap status refresh after PR 422 (#423)`).

## Result

R-CXA-2 remains `STILL-BOUNDED`. No new production upstream producer exists for the three remaining CP→IS composer methods:

- `RuntimeCpIsWiring.emit_hitl_tool_call_rewriting_state_ledger_entry`
- `RuntimeCpIsWiring.emit_pause_captured_state_ledger_entry`
- `RuntimeCpIsWiring.emit_resume_attempted_state_ledger_entry`

Do not wire placeholder calls. At this HEAD, a direct call from static tool dispatch, workflow-layer pause/resume handling, or ledger-only scaffolding would still be the silent X-AL-3 extension the U-RT-111 bounded-defer record forbids.

## Grounding

- `harness-runtime/src/harness_runtime/lifecycle/cp_is_wiring.py` defines all six runtime CP→IS composer methods.
- Production callers exist for the already-materialized methods:
  - `emit_workload_class_selection_state_ledger_entry(...)` at `harness-runtime/src/harness_runtime/bootstrap/stage_3b_cp_routing.py`.
  - `emit_pause_resume_state_ledger_entry(...)` at `harness-cp/src/harness_cp/workflow_driver.py` for resume attempt, drain-flag pause capture, and HITL-signal pause capture.
  - `emit_override_state_ledger_entry(...)` at `harness-cp/src/harness_cp/workflow_driver.py`.
- `RuntimeHITLPlacementRegistry.rewrite_tool_call(...)` remains a runtime registry method over the pure CP `rewrite_tool_call_to_hitl(...)` algorithm, but no production LLM/tool inner-loop caller invokes it.
- `workflow_driver.py` invokes `PauseResumeProtocol.capture_pause_snapshot(...)` and `PauseResumeProtocol.attempt_resume(...)`, but those sites correctly emit the workflow-layer `cp.pause-resume-protocol` action via `emit_pause_resume_state_ledger_entry(...)`. They are not the engine-layer recovery-loop producers required for `cp.pause-captured` or `cp.resume-attempted`.
- The free-function engine-layer `capture_pause_snapshot(...)` / `attempt_resume(...)` surfaces remain substrate APIs, not production recovery-loop firing sites.

## Forward Gate

Re-open R-CXA-2 only when one of these appears:

- a real production HITL tool-call rewrite caller with a specified `semantic_variant_binding_id` derivation,
- a real engine-layer recovery loop that invokes `capture_pause_snapshot(...)` and can emit `cp.pause-captured`,
- a real engine-layer recovery loop that invokes `attempt_resume(...)` and can emit `cp.resume-attempted`,
- or a design/back-flow amendment that changes the R-CXA-2 close contract.

