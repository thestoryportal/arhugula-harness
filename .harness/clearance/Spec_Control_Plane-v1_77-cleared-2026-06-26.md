---
artifact: design-substrate/Spec_Control_Plane_v1_77.md
version: v1.77
cleared_at: 2026-06-26T17:23:36-06:00
clearance_type: spec-writer-apply-pass
back_reference:
  - .harness/arc-open-b-fanout-maybe-ran-subagent-v2.md
  - .harness/b-fanout-crash-resume-maybe-ran-subagent-design-finding-v2.md
  - .harness/b-fanout-crash-resume-maybe-ran-subagent-design-finding-v1.md
merge_commit: a7704abe
reviewer_chain:
  - advisor full-transcript (BEFORE substantive work — the GO + five pre-build checks; reconcile on the seed-gating correction)
  - out-of-family Codex on the diff (caught a real [P1]: child run_id seed collision across fan-out siblings + the sequential-loop hazard)
  - by-execution witnesses (E1-live full-chain reconstruction + recoverability-predicate negative controls + classifier [P1-b] dual-gate + fan-out sibling distinctness)
  - empirical loop-suppression confirmation at workflow_driver.py:2040
supersedes:
superseded_by:
---

# Clearance — `Spec_Control_Plane v1.77`

v1.77 records the CP half of the R-FS-1 standalone arc `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT` — a maybe-ran fan-out `SUB_AGENT_DISPATCH` worker on a strict-tier crash-resume is now RECOVERABLE-by-re-dispatch (its child auto-resumes under the deterministic child run_id, result-faithfully). The delta adds a SECOND recovery mechanism to the C-CP-25 §25.15 maybe-ran classifier (`_fence_unrecoverable_maybe_ran_indices`) alongside the v1.65/v1.67 TOOL_STEP/MANAGED_AGENTS fence-recovery: a same-kind SUB_AGENT_DISPATCH branch whose child was recoverable BOTH at dispatch (the `child_recoverable` marker — the CP-side defensive opaque-payload read mirroring the runtime typed predicate) AND in the resumed manifest (the [P1-b] dual gate). Paired with runtime spec v1.85 (the `child_run_id_seed` E1 mechanism + the `subagent_child_recoverable` predicate + seed-gating).

What was reviewed: the recoverability predicate keys on the reconstruction-capable `{ESR,WAL}` engine set (NOT the broader 4 auto-fence classes — the [P1-a] fix), narrowed to a `SINGLE_THREADED_LINEAR` leaf child (the #770-witnessed scope); the [P1-b] dual gate (dispatch-marker AND resumed-manifest recoverable); the at-most-once invariants (range + changed-step_id + same-kind guards inherited; child-workflow-id swap = accepted parity). The out-of-family Codex pass caught a genuine [P1] — the deterministic child run_id seed collided across fan-out siblings (and the sequential-loop hazard) — fixed by folding the §25.16 `branch_path` into the seed + scoping it to fan-out workers.

Caveat for Phase 7 consumers: this is the WITNESSED LINEAR-`{ESR,WAL}`-leaf slice. The non-leaf-child residual (fan-out child / nested SUB_AGENT grandchild) is the registered follow-on `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT-NONLEAF-CHILD`; the SAVE_POINT/RECONCILER child case is the registered `B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT-SAVE-POINT-RECONCILER`. Both stay fail-closed.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
