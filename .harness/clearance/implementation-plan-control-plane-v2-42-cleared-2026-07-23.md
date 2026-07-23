---
artifact: design-substrate/Implementation_Plan_Control_Plane_v2_42.md
version: v2.42
cleared_at: 2026-07-23T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_b39_nested_hitl_response_threading.md (RATIFIED 2026-07-23)
  - design-substrate/Spec_Control_Plane_v1_106.md
merge_commit: pending (pre-merge at filing time; B-39 spec-leg PR)
reviewer_chain:
  - operator ratification (2026-07-23) — Q1=(A); Q2 revised via AskUserQuestion reconcile
  - just codex-review-uncommitted (2026-07-23, round 1) — out-of-family, found 4 P1 wiring defects in a first draft
  - Explore grounding pass (2026-07-23, round 1) — confirmed all 4 P1s against the real production call graph
  - advisor() (2026-07-23, round 1) — recommended the CONTRACT-altitude correction (state guarantees, not wiring)
  - just codex-review-uncommitted (2026-07-23, round 2) — out-of-family, found the hitl_responses key shape (branch_path) collides on repeated same-child_workflow_id dispatch
  - advisor() (2026-07-23, round 2) — verified via grep that run_id is genuinely recursion-stable before endorsing the re-key
---

# Clearance — Implementation_Plan_Control_Plane_v2_42 (B-39 arc, spec leg; TWO same-day correction passes)

v2.41→v2.42: ONE existing unit amended, ZERO new units. U-CP-64 (the
`ResumeContext` carrier-owning unit) carries the `hitl_responses`/
`hitl_response_for` field addition (keyed by the paused child's own
`run_id`, round-2-corrected) + the CONTRACT-level `DriverContext.
resume_context_holder` Protocol-field retirement (field removal only — the
replacement delivery mechanism is impl discretion). `PausedChildBranchResumeState`
is UNAMENDED — no new field needed once keying moved off `branch_path`.

**Round-1 correction (same-day).** A first draft additionally amended U-CP-86
(`PARALLELIZATION`), U-CP-88 (`ORCHESTRATOR_WORKERS`), and U-CP-89
(`HIERARCHICAL_DELEGATION`) with ACs asserting a direct intra-CP recursive
`execute_workflow` call at their worker re-dispatch sites. Out-of-family
review (`just codex-review-uncommitted`) plus an `Explore` grounding pass
found this call graph false — these functions stamp
`StepExecutionContext.child_resume_snapshot` and hand off to
`harness-runtime`'s `RuntimeSubAgentDispatcher`/`child_workflow_runner.py`,
which re-enters `execute_workflow` from the Runtime side, not a direct CP
recursion. §2-§4 (the three amendments) were REMOVED rather than re-authored
against a fourth unverified mechanism; the propagation-mechanism wiring is
deferred to impl-leg scope-discovery (§5's deferred-scope row), which may
touch U-CP-86/88/89, Runtime-owned units, or both. Round 1 ALSO added a NEW
`PausedChildBranchResumeState.branch_path` field (byte-compat, B-31
`child_workflow_id` pattern) so `hitl_responses` would be operator-
addressable.

**Round-2 correction (same-day, second out-of-family pass).** A second
`just codex-review-uncommitted` pass found round 1's `hitl_responses` key
shape — `branch_path` — collides when two peer branches dispatch the SAME
`child_workflow_id`, since `branch_path` derives from a workflow_id-scoped
identifier with no run-instance component. Traced (per advisor's blocking
gate) that `child_run_id` — via `compose_child_run_id_seed`'s
`run_idempotency_key = sha256(run_id, workflow_id, ...)` folding — genuinely
propagates run-instance distinctness through arbitrary recursion depth.
Fix: `hitl_responses` now keys by the paused child's own `run_id`
(`PausedChildBranchResumeState.child_snapshot.run_id`, an EXISTING field) —
the round-1 `branch_path` field addition is REMOVED as unnecessary.

This is the spec leg's plan absorption only — impl (code + tests) is a
separate follow-on arc per the B-33/B-59 precedent.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
