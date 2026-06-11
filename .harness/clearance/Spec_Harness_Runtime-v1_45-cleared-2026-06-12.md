---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.45
cleared_at: 2026-06-12T12:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc (bundled-absorption — spec + impl + tests)
back_reference:
  - .harness/class_2_fork_engine_durable_resume_no_production_producer.md (Class-2 scoping fork → operator Option 1)
  - .harness/r-cc-1-arc-3-workflow-durable-resume-design-v1.md (design doc, advisor-reviewed; §7a grounded impl plan)
  - PR #512 (R-CC-1 arc #3 re-aim — design-fork-first)
  - PR (cascade step 1 — this arc) — TBD at PR creation
merge_commit: TBD-at-PR-merge
reviewer_chain:
  - advisor (pre-approach) — "the producer is the discriminator, not the resume reader"; drove the Class-2 scoping fork (Gate A vs ratified line 181)
  - operator AskUserQuestion 2026-06-12 — Option 1 (re-aim to workflow-layer); then full-drive cascade-step-1 shape
  - advisor (design review) — caught (i) the resume-admission gate (resolved by grounding — MVP constant-sentinel pause_context_reader admits across a fresh bootstrap) + (ii) the state-vs-position assumption (resolved — data-stateless execution model, design §1.1)
  - empirical grounding passes — execute_workflow MCP-tool indirection; PAUSED-surfacing gap (_CP_TO_RT_STATUS had no PAUSED entry); attempt_resume admission gate; the full_execution_path pause/resume substrate
  - impl-time green — 3 new api.resume tests pass (incl. restart-proof round-trip e2e); pyright strict 0/0/0; 14 regression tests (api.run smoke + both pause/resume e2e) pass
  - out-of-family Codex (pre-merge, decorrelated; 2 rounds to convergence) — caught 3 genuine correctness gaps in the new public resume path → ALL FIXED before merge (detect-then-refuse pre-bootstrap): [P1] `resume()` without the pause/resume opt-in silently re-ran from step 0 (duplicate prefix side effects) → `ResumeProtocolNotBoundError`; [P2] a cross-workflow snapshot validated its own hash and applied the wrong run_id/step_index → `ResumeWorkflowMismatchError`; [P3, round 2] a snapshot with `step_index >= len(workflow.steps)` (changed workflow) sliced `steps[resume_at:]` empty → silent SUCCESS-that-ran-nothing → `ResumeStepIndexOutOfRangeError`. Each fix has a dedicated test.
---

# Clearance — `Spec_Harness_Runtime_v1.md v1.45`

v1.45 authors the **workflow-layer durable-resume public surface** (R-CC-1 arc #3 cascade step 1). Two amendments: **(1)** C-RT-09 §9 `RunResult` gains a `'paused'` status literal (type-widen, minor) + an optional `pause_snapshot: PauseSnapshot | None = None` field (optional-with-default, minor) — so `run()` surfaces a captured workflow-layer pause (closing a latent `_CP_TO_RT_STATUS` KeyError: there was no PAUSED→runtime mapping); **(2) NEW §30 C-RT-30** authors `resume(workflow, *, pause_snapshot, resume_context=None, config=None) -> RunResult`, the Track-A sibling of `run()` that continues a paused workflow from a caller-supplied `PauseSnapshot` after a fresh bootstrap. **C-RT-08 §8 `run()` is PRESERVED VERBATIM** (additive sibling, design D1-A — minimal cleared-contract blast radius). v1.44 + earlier lineage PRESERVED VERBATIM except the additive §9 extension.

**What was reviewed.** The arc began as a Class-2 scoping fork: operator Gate A (2026-06-11, "hand-roll engine-layer durable-resume, bind #475") could not be honestly built — the engine-layer recovery loop has no production producer, and the only candidate (the workflow-layer DURABLE_ASYNC pause) is forbidden by the ratified forward-register line 181 from being piped through the engine loop. advisor's discriminator — *the producer is the discriminator, not the resume reader* — drove the fork; the operator chose Option 1 (re-aim to the workflow-layer gap, whose producer fires today at `workflow_driver.py:793/948`). advisor's design review then caught two would-be-wrong assumptions, both resolved by grounding: the resume-admission gate (`attempt_resume` STRICT material-diff — the MVP `pause_context_reader` returns a constant sentinel at both capture and resume → no diff → admits the resume across a fresh bootstrap; real anchor-reachability is the deferred U-CP-22 arc) and the state-vs-position assumption (the MVP execution model is data-stateless between steps → position-only resume is faithful, no working-state rehydration). Impl landed + verified green: 3 new tests (incl. a restart-proof capture→JSON-round-trip→fresh-bootstrap-resume→SUCCESS e2e), pyright strict 0/0/0, 14 regression tests pass.

**Caveats for Phase 7 consumers.**
- **Resume-admission anchor-validation is DEFERRED.** v1.45 does NOT enforce cross-restart ledger-anchor reachability; STRICT admits because the MVP `pause_context_reader` reports no diff. A future arc wiring the real `_anchor_reachable_predicate` (U-CP-22) composes with harness-owned durable persistence.
- **Caller-supplied snapshot only (cascade step 1).** Harness-owned durable persistence — a `JournalWorkflowPauseStore` applying the engine-layer #475 substrate's crash-survivable journal *pattern* to the workflow-layer `PauseSnapshot` type (reused by pattern, NOT bound; the engine-layer recovery loop + #475 stay the line-181 bounded-residual) — is **cascade step 2**.
- **Pause/resume opt-in required.** `resume()` requires `config.pause_resume_protocol_config` (the same opt-in that produced the pause); without it the driver's resume detection is inert.
- **`resume()` reuses `pause_snapshot.run_id`** for audit/ledger coherence (position comes from `step_index`, not `run_id`).

## Notes

- Phase 7 consumers may rely on v1.45 as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
- `merge_commit` + the final PR back-reference are filled at PR merge.
