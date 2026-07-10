---
artifact: design-substrate/Spec_Control_Plane_v1_86.md
version: v1.86
cleared_at: 2026-07-10T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-architect-recommendation
back_reference:
  - design-substrate/Spec_Harness_Runtime_v1.md (paired runtime change-note v1.95 → v1.96 — the consuming behavior)
  - .harness/u1-slice3-findings-and-f1-c10-gap.md (F1 finding)
  - .harness/u1-slice3a-c10-reconfirmation.md (C10 re-confirmation)
  - PR (U-1 slice 3a, branch u1-slice3a-child-frozen-tool-superset-f1)
merge_commit: (squash-merge of the U-1 slice-3a PR)
reviewer_chain:
  - decorrelated advisor (transcript-aware) — carrier-home discipline (StepExecutionContext, not a cloned dispatcher stack)
  - out-of-family just codex-review (gpt-5.5, subscription) on the diff
  - main-agent artifact review (threading across execute_workflow → body → 5 strategy composers; model_copy inheritance verified)
---

# Clearance — `Spec Control Plane v1.86`

v1.86 records the **CP carrier half of U-1 slice 3a**: an additive `StepExecutionContext.sub_agent_descent: bool = False` field under **C-CP-25 §25.2** (the per-step execution-context the driver composes and passes to the `StepDispatcher` Protocol), threaded by a new `execute_workflow(..., sub_agent_descent: bool = False)` keyword. It is the descent signal the runtime `RuntimeLLMDispatcher.dispatch` reads to emit the child-scoped (downgraded) frozen tool superset per **ADR-D4 §1.5** — closing the F1 latent C10 condition-2 gap. Paired with **runtime spec change-note v1.95 → v1.96** (the consuming behavior).

**Carrier discipline.** The field rides `StepExecutionContext` (hash-inert, per-step-transient, NOT persisted, NOT in the §5.2 IS hash nor the §16.5.4 per-step-override outcome-hash) — the exact `hitl_placements` (v1.49 §6.2) / `run_engine_class` / `effect_fence_resolution` producer precedent. The driver sets it at every fresh construction site (SINGLE_THREADED_LINEAR loop + the 5 non-linear strategy composers); fan-out branch children inherit it via `compose_branch_child_context`'s `model_copy` (not re-listed in the `update` dict). `child_workflow_runner` passes `True`; top-level `api.run` uses the `False` default (byte-identical to pre-slice-3a).

**Spec-vs-fork.** Bundled-absorption amendment materializing a COMMITTED contract (ADR-D4 §1.5's `sub_agent_tool_registry` REMOVE disposition — a committed-but-unbuilt unit), NOT an X-AL-3 design extension. No committed decision sacrificed → no operator gate.

**Verification.** NO §5.2 IS-hash change; NO new contract/enum/fail-class/CXA edge/`StepDispatcher` Protocol widening. Full `harness-cp/tests/` non-e2e = **1474 passed** (789 topology tests regression-clean across the 5 threaded strategy composers); no `StepExecutionContext.model_fields` cardinality test asserts a field count (verified). pyright 0/0/0 on `workflow_driver.py` + `workflow_driver_types.py`.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
