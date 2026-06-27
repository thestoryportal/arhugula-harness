---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.89
cleared_at: 2026-06-27T14:30:00-06:00
clearance_type: phase-7-bundled-absorption
back_reference:
  - .harness/arc-ledger.yaml
  - .harness/clearance/Spec_Control_Plane-v1_83-cleared-2026-06-27.md
merge_commit: (pending — co-landed in this arc's PR)
reviewer_chain:
  - advisor full-transcript (the regression finding via the by-execution witness; the completeness argument for the identity tuple; the honest orchestrator-composition narrative)
  - by-execution witnesses (the depth-2 crash-resume RED→GREEN double-fire fix; the CP↔runtime agreement incl. partially-malformed-nested parity; the linear-seed step_id+engine binding + full-identity edit-detection)
  - out-of-family Codex on the diff (6 genuine at-most-once findings, converged round 7)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.89`

v1.89 records the RUNTIME half of the R-FS-1 standalone arcs `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT-NONLEAF-CHILD` (worker) + `…-ORCHESTRATOR-…-NONLEAF-CHILD` — the case-(b) [nested SUB_AGENT grandchild] slice (paired with CP spec v1.82 → v1.83). The typed mirror predicate `subagent_child_recoverable` is made RECURSIVE; the prior leaf-only condition fail-closed on ANY nested sub-agent.

What was reviewed: the two co-landed runtime changes (the predicate alone is a double-fire regression). (1) ONE SOURCE OF TRUTH — the runtime composer's nested recursion no longer `SubAgentDispatchPayload.model_validate`s the nested payload; it DELEGATES to the shared CP `payload_child_recoverable` (out-of-family Codex [P1]): a runtime-only model_validate would reject a partially-valid nested payload (missing child_workflow_id/brief) that the CP defensive mirror admits → CP-True/runtime-False → the outer child's marker admits re-dispatch with NO seed → the outer child re-runs fresh → double-fire. Recoverability depends only on engine+topology+child_steps; child_workflow_id/brief affect DISPATCHABILITY (fail closed at the dispatcher's own model_validate). (2) A THIRD deterministic-seed surface (`is_linear_sequential_dispatch`) — the recursive predicate admits a LINEAR child whose nested grandchild is dispatched at the SINGLE_THREADED_LINEAR inline loop, a surface the prior fan-out-worker/orchestrator seed gating did NOT cover; without a seed there the grandchild re-runs fresh on re-dispatch → double-fire. Gated on the NEW hash-inert `StepExecutionContext.is_linear_sequential_dispatch` flag.

The seed + the recursive CP marker bind the FULL at-most-once identity tuple {ordinal, step_id, child_workflow_id, engine_class} — complete by construction over (a) the run_id-deriving fields (the `compose_child_run_id_seed` disambiguator `branch_path = "linear-step:" + json([step_id, engine_class])`; `parent_idempotency_key` IS the child-step-index key → ordinal; child_workflow_id) + (b) the recovery-mechanism-selecting field (engine_class). Every out-of-tuple payload field (workload_class/persona_tier/layer_budgets/fallback_chain/per_step_overrides/hitl_placements/brief) changes only how REMAINING steps run (committed prefix auto-resumed, not re-fired). Any identity-changing edit changes BOTH the seed AND the marker → dual gate fails closed → no double-fire.

Case-(a) [the child is itself FAN-OUT] stays fail-closed → registered (`B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT-FANOUT-CHILD`): a separate LINEAR-excluded reconstruction mechanism. The case-(b) close is parent-agnostic (the new code is at the child→grandchild seam; the worker/orchestrator difference lives only in the unchanged outer seam #774/#777) — closing both with the shared mechanism + the parent-agnostic depth-2 witness (the orchestrator close rests on composition with #777, not a dedicated orchestrator e2e).

No new contract; ONE hash-inert per-step flag (`is_linear_sequential_dispatch`, same category as `is_orchestrator_dispatch`); no new fail-class / §5.2-hash change / Protocol widening / CXA edge. CP spec C-CP-25 §25.15 v1.82 → v1.83 is the paired primary contract. IS / OD / AS / ADR specs UNCHANGED. CXA v2.20 UNCHANGED.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
