---
artifact: design-substrate/Spec_Control_Plane_v1_97.md
version: v1.97
cleared_at: 2026-07-13T22:00:00-06:00
clearance_type: Phase-7-absorbed-via-architect-recommendation
back_reference:
  - .harness/post-phase-8-forward-register.md (B-21 entry, surfaced at PR #964's preflight review HIGH #6)
  - design-substrate/Spec_Control_Plane_v1_45.md (B-HIERARCHICAL-PAUSE prerequisite mechanism, reused verbatim)
  - design-substrate/Spec_Control_Plane_v1_44.md (PeerFanOutResumeState carrier this delta extends)
merge_commit: pending (pre-merge at filing time)
reviewer_chain:
  - advisor() pre-build grounding (confirmed the gap is reachable — a failing witness test before any fix)
  - impl-to-cleared-spec disposition (§25.15.1 already commits pause -> PAUSED; v1.45 already materialized the child-pause mechanism generally; this delta is a carrier-completeness extension, not new design surface)
  - just codex-review pre-merge (§13.1 out-of-family review), 3 rounds — round 1 caught a nested-carrier hash byte-compat gap + a step-kind-changed resume hole (both fixed); round 2 caught a broader nested byte-compat scoping regression against the ALREADY-SHIPPED v1.45 mechanism (fixed via per-carrier-kind-scoped strip); rounds 2-3 surfaced 3 pre-existing, symmetric-with-v1.45 gaps registered as forward work, not fixed inline (child-workflow-identity validation, cross-branch HITL resume-context routing, nested pause-reason propagation)
  - advisor() pre-done review (flagged the spec-delta/clearance obligation per the #679/#680 bundled-absorption precedent — this marker discharges it)
supersedes: null
superseded_by: null
---

# Clearance — `Spec_Control_Plane v1.97`

v1.97 is the `B-21` absorption arc: `PeerFanOutResumeState` (v1.44, PARALLELIZATION's peer-fan-out pause carrier) gains a `paused_child_branches` field, reusing the `PausedChildBranchResumeState` carrier v1.45 introduced for `FanOutResumeState` (ORCHESTRATOR_WORKERS/HIERARCHICAL_DELEGATION). Before this arc, a PARALLELIZATION peer branch whose own dispatch was a `SUB_AGENT_DISPATCH` step recursing into a child sub-workflow that itself PAUSED had nowhere to record it — the runtime dispatcher's typed `SubAgentChildPausedError` (topology-agnostic since v1.45) fell into the generic branch-failure handler, the branch was recorded terminal `completed` with no output, and the child's suspended `PauseSnapshot` was silently dropped. This is exactly the strategy×capability cell PR #964's preflight review flagged as HIGH #6, registered as `B-21` at `.harness/post-phase-8-forward-register.md`.

No new carrier type, no new CP-importable exception, no runtime-side change: the per-branch row shape (`branch_index` + `step_id` + `child_snapshot`) is topology-agnostic and the runtime `SUB_AGENT_DISPATCH` dispatcher already raised the shared `SubAgentChildPausedError` regardless of parent topology. The one genuinely load-bearing correctness issue this delta had to resolve (out-of-family Codex, round 2) was byte-compat scoping: `FanOutResumeState.paused_child_branches`'s nested occurrences have serialized with an unstripped empty `[]` since v1.45 shipped, so a blanket "strip whenever empty" fix (as first drafted) would have changed the recomputed hash of pre-existing durable HIERARCHICAL_DELEGATION snapshots. The shipped fix scopes the strip per carrier-kind (`peer_fan_out_resume` opts in; `fan_out_resume` keeps its v1.45 behavior unchanged), verified by a dedicated pinning test in each direction.

Three findings surfaced during the out-of-family review (rounds 2-3) are registered as forward work, NOT fixed in this delta: a resume material-diff guard that validates branch identity + kind but not the re-supplied `SUB_AGENT_DISPATCH` payload's `child_workflow_id`; two concurrent paused-child branches sharing the single run-level `resume_context_holder` with no per-branch HITL-response routing; and a parent `_pause_reason` derivation that does not propagate a nested child's own pause reason. All three are PRE-EXISTING on the v1.45 mechanism this delta ports (verified symmetric by direct read of `_execute_orchestrator_workers`'s equivalent code, not merely asserted) — not introduced by or unique to this PARALLELIZATION extension, and (b)+(c) are coupled (propagating a reason without response routing is a false affordance), so they travel together as one future arc.

## Notes

- Phase 7 consumers may rely on this version (v1.97) as canonical for the `PeerFanOutResumeState.paused_child_branches` capability.
- The three registered forward-work gaps apply equally to the pre-existing v1.45 `FanOutResumeState.paused_child_branches` mechanism — a future arc addressing them should scope to both carriers, not just the peer side.
- See `.harness/clearance/README.md` for marker discipline.
