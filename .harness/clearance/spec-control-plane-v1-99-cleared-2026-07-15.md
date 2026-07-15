---
artifact: design-substrate/Spec_Control_Plane_v1_99.md
version: v1.99
cleared_at: 2026-07-15T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-roadmap-continue
back_reference:
  - .harness/forward-register.yaml (B-31 entry — paused-child resume guard child_workflow_id identity)
  - design-substrate/Spec_Control_Plane_v1_97.md (§ change-note registered-forward-work item (a) — the exact gap this delta closes)
  - design-substrate/Spec_Control_Plane_v1_45.md (§1 last-substantive-definition of `PausedChildBranchResumeState` + `SubAgentChildPausedError`)
merge_commit: pending (pre-merge at filing time)
reviewer_chain:
  - advisor() pre-implementation grounding (2 rounds) — first pass surfaced that a bare field-compare undersold the fix (CP's own in-file comment claimed step_payload was unreadably opaque); second empirical grounding pass (Explore subagent) found the existing `_opaque_field` precedent at `workflow_driver.py:1164` already reading this exact key off the same opaque payload for a different purpose, resolving the concern without a new cross-axis Protocol; advisor also flagged the backcompat/optional-field concern (frozen+extra=forbid carrier; a required field would break deserialization of any already-paused, not-yet-resumed workflow across the deploy boundary) — resolved via `str | None = None` + the drop-when-None hash-strip discipline mirroring v1.97's own `paused_child_branches` precedent
  - full workspace `just check` (5790 passed, 0 skipped-beyond-baseline, 0 regressions vs the 5788-passed baseline recorded at PR #1007's refresh)
  - pyright strict (0 errors, 0 warnings, 0 informations) across all 3 touched harness-cp modules
  - 2 discriminating-witness tests added (`test_peer_resume_rejects_paused_child_workflow_id_swap`, `test_hierarchical_resume_rejects_paused_child_workflow_id_swap`) — both mutation-probed: disabling the guard's mismatch-return (forcing it unreachable) was confirmed to make BOTH tests fail before the fix was restored, proving the tests pin the identity check rather than passing vacuously
  - in-flight correction — the initial guard implementation fail-closed on an unreadable `child_workflow_id` key unconditionally, which broke 2 pre-existing tests in `test_workflow_driver_orchestrator_workers_fence_ledger.py` that legitimately swap a paused-child ordinal's step_kind away from `SUB_AGENT_DISPATCH` for unrelated test-scaffolding reasons; corrected by gating the read/compare on the resumed step still being `SUB_AGENT_DISPATCH` (the `ORCHESTRATOR_WORKERS`/`HIERARCHICAL_DELEGATION` closure has no pre-existing kind-changed check, unlike the `PARALLELIZATION` closure, so this gate was added explicitly rather than assumed)
supersedes: null
superseded_by: null
---

# Clearance — `Spec_Control_Plane v1.99`

v1.99 closes the `B-31` standalone arc: the resume material-diff guard (both the `PARALLELIZATION` and `ORCHESTRATOR_WORKERS`/`HIERARCHICAL_DELEGATION` closures of `_resume_body_mismatch`) validated a paused-child branch's bounds + `step_id` identity + (for `PARALLELIZATION` only) `step_kind`, but not that the re-supplied `SUB_AGENT_DISPATCH` branch's payload still targeted the SAME child workflow the snapshot was captured against. A same-`step_id`/same-`step_kind` edit that swapped the target `child_workflow_id` previously passed undetected — the exact gap v1.97's own change-note registered as forward work rather than fixing at the time.

This delta adds `PausedChildBranchResumeState.child_workflow_id: str | None = None` (threaded from `SubAgentChildPausedError.child_workflow_id`, a value CP already receives at the pause site but previously discarded at all 6 capture sites) and extends both resume-guard closures to compare it against the re-supplied branch's `step_payload["child_workflow_id"]` — read via the SAME `_opaque_field` opaque-mapping-key convention CP already applies elsewhere in `workflow_driver.py` (`_payload_engine_signature`, for grandchild recoverability). **No new cross-axis Protocol was required** — a pre-build grounding pass initially suspected one would be (mirroring the `CohortKeyCapable` dispatcher-oracle pattern from the B-18-3C-PREWARM-COHORTKEY arc), but a second empirical pass found CP already has an established, in-file precedent for reading this exact key off an opaque `SUB_AGENT_DISPATCH` payload.

The check is gated on the resumed branch's `step_kind` still being `SUB_AGENT_DISPATCH` (a kind-changed ordinal won't receive the child-resume thread regardless, and is not itself anomalous at a payload-shape level) and on the snapshot carrying a non-`None` `child_workflow_id` (byte-compat: every already-durable pause snapshot predates this field and is skipped, never rejected). An unreadable key on a still-`SUB_AGENT_DISPATCH` payload is treated as anomalous and fails closed, symmetric with the existing `step_id`/`step_kind` checks.

## Notes

- Phase 7 consumers may rely on this version (v1.99) as canonical for the `PausedChildBranchResumeState.child_workflow_id` field + the resume-guard identity check.
- `B-31`'s forward-register row (`.harness/forward-register.yaml`) should be marked closed in the same PR, citing this clearance marker.
- Root `CLAUDE.md` §2.3's CP spec pointer was corrected from a stale v1.97 to v1.99 in the same PR (it had not been refreshed at v1.98's landing).
- See `.harness/clearance/README.md` for marker discipline.
