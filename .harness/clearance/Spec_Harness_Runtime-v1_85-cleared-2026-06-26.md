---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.85
cleared_at: 2026-06-26T17:23:36-06:00
clearance_type: spec-writer-apply-pass
back_reference:
  - .harness/arc-open-b-fanout-maybe-ran-subagent-v2.md
  - .harness/b-fanout-crash-resume-maybe-ran-subagent-design-finding-v1.md
merge_commit: a7704abe
reviewer_chain:
  - advisor full-transcript (BEFORE substantive work — the GO + the corrected predicate + the seed-gating correction over the #746 reverted branch)
  - out-of-family Codex on the diff (caught the [P1] sibling-collision — branch_path + fan-out-worker scope added in response)
  - by-execution witnesses (E1-live full-chain reconstruction + recoverability-predicate negative controls + fan-out sibling distinctness)
  - empirical loop-suppression confirmation at workflow_driver.py:2040
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.85`

v1.85 records the RUNTIME half of the R-FS-1 standalone arc `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT` (paired with CP spec v1.77). Two §14.7.4 C-RT-17 mechanism additions: (1) **E1** — `ChildWorkflowRunner.__call__` gains an additive `child_run_id_seed` kwarg; on a first dispatch the runner prefers the composer-supplied deterministic seed (`compose_child_run_id_seed`) over a fresh `uuid`, so a parent-crash re-dispatch re-derives the SAME child run_id → the child's durable store + fence reserves are recoverable → the child's own crash-resume auto-resumes with result-faithful `final_state` reconstruction (B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT, v1.75). (2) The **recoverability predicate** (`subagent_child_recoverable`) + **seed-gating** — the composer threads the seed ONLY for a recoverable fan-out worker (`branch_index is not None` ∧ child engine ∈ `{ESR,WAL}` ∧ topology `SINGLE_THREADED_LINEAR` ∧ leaf).

What was reviewed: the corrected predicate over the #746 reverted branch (LINEAR-narrowing — the [P1-a] fix; seed-gating — the deterministic seed scoped to recoverable children so a SAVE_POINT/RECONCILER child never auto-resumes into a suffix-only fold corruption); the out-of-family Codex pass caught a real [P1] — the seed `compose_child_run_id_seed(parent_idempotency_key, child_workflow_id)` collided across fan-out siblings because `compose_branch_child_context` inherits `parent_idempotency_key` verbatim from the fan-out parent. Fixed by folding the §25.16 `branch_path` ({parent_action_id}:{branch_index}) into the seed and scoping it to fan-out workers — the latter also excludes the sequential-loop topologies (EVALUATOR_OPTIMIZER/RECONCILER_LOOP) whose steps reuse `step_index` across iterations (empirically confirmed at workflow_driver.py:2040).

Caveat for Phase 7 consumers: the seed/recovery is the WITNESSED LINEAR-`{ESR,WAL}`-leaf fan-out-worker slice; non-leaf-child + non-fan-out + sequential-loop dispatches keep the legacy fresh-`uuid` (no auto-resume, pre-arc behavior).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
