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
  - just codex-review (2026-07-23, round 3, branch-vs-main against open PR #1092) — out-of-family, found AC #8's standalone field-removal breaks 3 currently-working effect-fence readers if landed alone
  - advisor() (2026-07-23, round 3) — recommended folding field removal into the same deferred bucket as the delivery-mechanism contract, not asserting it as a standalone AC
  - just codex-review (2026-07-23, round 4, branch-vs-main against the round-3 fix commit) — out-of-family, found round 3's own AC #7 addition strands transitively-paused container branches and is unassignable to U-CP-64
  - advisor() (2026-07-23, round 4) — recommended converting the AC #7 mechanism to a black-box invariant deferred at §5, not a 5th mechanism attempt on U-CP-64
---

# Clearance — Implementation_Plan_Control_Plane_v2_42 (B-39 arc, spec leg; FOUR same-day correction passes)

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

**Round-3 correction (same-day, branch-vs-main `just codex-review` against open PR #1092).** Found AC #8 ("`DriverContext.resume_context_holder` field is REMOVED," standalone unit-testable) unsafe: landing field removal alone, before its 3 effect-fence peek-reader consumption sites (`workflow_driver.py`, `getattr(ctx, "resume_context_holder", None)`) are re-pointed, breaks the CURRENTLY-WORKING effect-fence SKIP/RE_FIRE/ABORT resume mechanism (readers silently receive `None`, re-pausing INERT even when the operator supplied a resolution). Fix: AC #8 WITHDRAWN as a standalone AC; folded into §5's deferred delivery-mechanism bucket — physical removal + re-pointing all 3 sites now MUST co-land atomically at the impl leg (never as two separately-sequenced units). AC #7 additionally extended with a NEW mutation-probe test requirement for the CP spec's new §1.2 property 4 (multi-child fallback-safety gate — see the sibling `Spec_Control_Plane_v1_106.md` clearance marker's round-3 section for the underlying finding, which is CP-owned and fixed at the spec level, with this plan's AC #7 carrying the corresponding test obligation). Two follow-ons registered (not solved) at §5: a `resume_handle`-path durable-pause-state read accessor; the pre-existing `effect_fence_resolution_for` uniform-fallback gap.

**Round-4 correction (same-day, branch-vs-main `just codex-review` against the round-3 fix commit).** Round 3's AC #7 addition (a resolver mechanism: count HITL-paused children, gate the uniform fallback, else force INERT re-pause) was found doubly wrong: strands a transitively-paused container/ancestor branch by forcing INERT re-pause instead of unconditional recursion toward the actually-addressed gate-owning descendant; and assigns the obligation to U-CP-64, which only owns the `ResumeContext` carrier, not the deferred resolver. Fix: CP spec v1.106 §1.2 property 4 CONVERTED from a mechanism to a black-box invariant, MOVED to §5's deferred bucket alongside properties 1-3; a NEW property 5 distinguishes gate-owning from transitively-paused container branches. AC #7 reverts to carrier-level-only tests; the multi-branch mutation-probe test is removed.

**Round-5 note (branch-vs-main `just codex-review` against the round-4 fix commit).** Findings were entirely Runtime-owned (a property-1 restatement drift in the sibling Runtime spec) or documentation hygiene (`harness-cp/CLAUDE.md` round-count staleness, a stale U-RT-95 cross-reference in the Runtime spec's own clearance marker) — see those files' own round-5 corrections. This file required no further content change.

**Round-6 note.** Findings were entirely Runtime-plan-owned (an atomicity-drift correction) or a genuinely new registration (`B-71`, operator-facing HITL escalation-request correlation gap) landing at the sibling CP spec, not this plan file. This file required no further content change.

This is the spec leg's plan absorption only — impl (code + tests) is a
separate follow-on arc per the B-33/B-59 precedent.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
