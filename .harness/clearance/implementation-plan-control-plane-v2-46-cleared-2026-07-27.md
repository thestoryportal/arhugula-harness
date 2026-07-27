---
artifact: design-substrate/Implementation_Plan_Control_Plane_v2_46.md
version: v2.46
cleared_at: 2026-07-27T00:00:00-07:00
clearance_type: Phase-7-absorbed-via-council-convening
back_reference:
  - .harness/clearance/spec-control-plane-v1-110-cleared-2026-07-27.md
  - .harness/forward-register.yaml B-79/B-80 rows
merge_commit: pending (direct-to-main commit at authoring time)
reviewer_chain:
  - dyadic council-orchestrator convenings for B-79 and B-80 (2026-07-27)
  - independent re-verification of load-bearing claims at plan-authoring time
  - out-of-family just codex-review-uncommitted, multiple rounds to convergence — 2 [P2] real findings on this artifact (a cross-axis scope claim; an omitted property 7 scope row for EO/DH), fixed before commit
supersedes: null
---

# Clearance — `Implementation_Plan_Control_Plane_v2_46` (co-designed B-79/B-80 plan absorption)

Absorbs `Spec_Control_Plane_v1_110`'s two new additive properties (7 and 8) into TWO new coverage-matrix rows, mirroring the v2.42/v2.43/v2.44 precedent of deferring a not-yet-existing resolver rather than assigning it to U-CP-64. ZERO existing unit is amended, ZERO new unit is added, ZERO DAG topology change. Property 7's carrier fields are entirely CP-native, zero cascade. Property 8's threaded parameter touches the Runtime-owned `ChildWorkflowRunner` Protocol (`child_workflow_runner.py`) — out-of-family `just codex-review-uncommitted` caught a first draft's false "zero cross-axis cascade" / "entirely CP-native" claim here (confirmed WRONG: that Protocol lives in `harness-runtime`, not `harness-cp`); corrected to state no NEW crossing point is introduced (the parameter reuses the SAME established CP→Runtime→CP boundary its two sibling parameters — `hitl_uniform_fallback_eligible_run_id`/`effect_fence_uniform_fallback_eligible_key` — already use), but the touch itself is real.

The two coverage-matrix rows name the impl leg's scope-discovery obligations precisely (per each convening's own recommendation, re-verified at authoring time): property 7's row names the exact carrier fields to add, the exact 4-field `HITLPlacement` hash scope, and the net-new carrier need at all 3 sequential sites (LINEAR/`EVALUATOR_OPTIMIZER`/`DECENTRALIZED_HANDOFF` — round-2 out-of-family codex review caught an initial draft's omission of the latter two, both landed later by the `B-78` impl leg and confirmed to mirror LINEAR's mechanism exactly); property 8's row names the exact existing utilities to reuse (`_collect_effect_fence_idempotency_keys`, `_resolve_effect_fence_gated`) and the exact two consume sites to widen (`workflow_driver.py:7999`/`8037` and `12257`/`12281`).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- Impl leg (code + tests) is a separate follow-on arc per the `B-33`/`B-39`/`B-59`/`B-70`/`B-72` precedent — not bundled with this spec-leg absorption.
