---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.86
cleared_at: 2026-06-26T18:40:00-06:00
clearance_type: phase-7-bundled-absorption
back_reference:
  - .harness/arc-ledger.yaml
  - .harness/b-fanout-crash-resume-maybe-ran-subagent-design-finding-v2.md
merge_commit: (pending — co-landed in this arc's PR)
reviewer_chain:
  - advisor full-transcript (BEFORE substantive work — the GO + the convergence-value selection criterion + the close-≥-register tripwire; grounding-confirmed net-zero)
  - by-execution witnesses (orchestrator seed-wiring through the real dispatcher + orchestrator↔worker seed-distinctness + no-leak-to-loop-iterations regression guard + full-chain recovery/fail-closed pair)
  - out-of-family Codex on the diff (pending pre-merge — `just codex-review`)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.86`

v1.86 records the RUNTIME half of the R-FS-1 standalone arc `B-FANOUT-CRASH-RESUME-ORCHESTRATOR-MAYBE-RAN-SUBAGENT` (paired with CP spec v1.78) — the ORCHESTRATOR analogue of the v1.85 worker arc. The ONE mechanism addition: the deterministic `child_run_id_seed` now extends to the orchestrator dispatch, gated on a NEW hash-inert `StepExecutionContext.is_orchestrator_dispatch` flag. The v1.85 `subagent_child_recoverable` predicate + the `child_run_id_seed` / `ChildWorkflowRunner` E1 mechanism are REUSED VERBATIM (no new typed surface).

What was reviewed: the seed-discriminator safety — the orchestrator is a SINGLE, once-per-run step, so a deterministic seed is safe (no iteration-2 to alias iteration-1's store), and `is_orchestrator_dispatch` distinguishes it from the EVALUATOR_OPTIMIZER / RECONCILER_LOOP iterated steps (which keep `branch_index is None` ∧ `is_orchestrator_dispatch False` → no seed → the loop-suppression foreclosure preserved, regression-guarded by the unchanged `test_dispatch_seed_none_for_linear_non_fanout_recoverable_child`); the `branch_path=None` orchestrator seed staying DISTINCT from worker `branch_path` seeds (no orchestrator↔worker child aliasing); the seed re-deriving identically on a crash-resume re-dispatch (`orchestrator_idempotency_key` is the deterministic step_index-0 key). `is_orchestrator_dispatch=False` default ⟹ byte-identical to v1.85.

Caveat for Phase 7 consumers: this is the WITNESSED LINEAR-`{ESR,WAL}`-leaf slice (the non-leaf-child + SAVE_POINT/RECONCILER residuals are the registered follow-ons named in the CP v1.78 marker). The recursive-child RESULT-fidelity is the shared mechanism witnessed at `test_recursive_child_crash_resume_final_state_witness.py` (v1.85).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
