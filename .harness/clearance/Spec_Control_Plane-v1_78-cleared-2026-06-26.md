---
artifact: design-substrate/Spec_Control_Plane_v1_78.md
version: v1.78
cleared_at: 2026-06-26T18:40:00-06:00
clearance_type: phase-7-bundled-absorption
back_reference:
  - .harness/arc-ledger.yaml
  - .harness/b-fanout-crash-resume-maybe-ran-subagent-design-finding-v2.md
merge_commit: (pending — co-landed in this arc's PR)
reviewer_chain:
  - advisor full-transcript (BEFORE substantive work — the GO + the convergence-value selection criterion ranking forward arcs by unblock/avoid-spawn over code-freshness + the close-≥-register tripwire; grounding-confirmed net-zero)
  - by-execution witnesses (orchestrator seed-wiring through the real dispatcher + orchestrator↔worker seed-distinctness + classifier [P1-b] dual-gate + same-step_id + negative controls + full-chain production-marker recovery/fail-closed pair)
  - out-of-family Codex on the diff (pending pre-merge — `just codex-review`)
supersedes:
superseded_by:
---

# Clearance — `Spec_Control_Plane v1.78`

v1.78 records the CP half of the R-FS-1 standalone arc `B-FANOUT-CRASH-RESUME-ORCHESTRATOR-MAYBE-RAN-SUBAGENT` — the ORCHESTRATOR analogue of the v1.77 worker arc. A maybe-ran fan-out `SUB_AGENT_DISPATCH` ORCHESTRATOR (`steps[0]`) on a strict-tier crash-resume is now RECOVERABLE-by-re-dispatch: re-running the whole fan-out fresh re-dispatches the orchestrator, whose child auto-resumes under the deterministic child run_id (result-faithfully). The delta adds a SUB_AGENT recovery disjunct to the C-CP-25 §25.15 orchestrator maybe-ran block in `_determine_fanout_resume` alongside the v1.64 re-fire-safe + TOOL_STEP/MANAGED_AGENTS fence-recovery. Paired with runtime spec v1.86 (the `is_orchestrator_dispatch` seed-discriminator extending `child_run_id_seed` to the orchestrator dispatch).

What was reviewed: the dual gate (the orchestrator's child recoverable BOTH at dispatch via the new `record_orchestrator_dispatched(child_recoverable=...)` marker + `orchestrator_subagent_child_recoverable` reader, AND in the resumed manifest via `_subagent_child_recoverable(steps[0])` — the [P1-b] changed-manifest guard); the same-step_id guard (manifest-stability parity with the worker SUB_AGENT path); the same-kind requirement (marker ∧ resumed both SUB_AGENT_DISPATCH); the pristine-window check (no downstream artifact); and the seed no-leak discriminator — `is_orchestrator_dispatch` reaches the orchestrator dispatch WITHOUT reaching the sequential-loop iterated steps (which keep `branch_index is None` ∧ `is_orchestrator_dispatch False` → no deterministic seed → the loop-suppression hazard stays foreclosed). Workers RESET the flag (`compose_branch_child_context` + `fanout_parent`), and the orchestrator seeds with `branch_path=None` (distinct from worker `branch_path` seeds → no orchestrator↔worker child aliasing).

Caveat for Phase 7 consumers: this is the WITNESSED LINEAR-`{ESR,WAL}`-leaf slice. The non-leaf-child residual (fan-out orchestrator-child / nested SUB_AGENT grandchild) is the registered follow-on `B-FANOUT-CRASH-RESUME-ORCHESTRATOR-MAYBE-RAN-SUBAGENT-NONLEAF-CHILD`; the SAVE_POINT/RECONCILER orchestrator-child case is the registered `B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT-SAVE-POINT-RECONCILER`. Both stay fail-closed. Net-zero: close 1 + register 1 (the SAME profile as the just-accepted worker #774).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
