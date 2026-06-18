---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.61
cleared_at: 2026-06-18T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc (NO operator gate — faithful-materialization reconciliation of the §14.8.2-step-1 read surface; impl-to-cleared-spec on the §14.8.1/§14.8.4 fold + PRE_ACTION coupling; no committed-invariant sacrifice)
back_reference:
  - .harness/class_1_fork_b_hitl_placement_per_step_producer.md
  - .harness/beyond-mvp-capability-boundary-ledger.md (B-HITL-PLACEMENT-PER-STEP-PRODUCER spine BUILT note + B-HITL-PLACEMENT-PER-STEP-OVERRIDE-FOLD follow-on)
  - design-substrate/Spec_Control_Plane_v1_41.md (the paired StepExecutionContext.hitl_placements field)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - advisor (full-transcript, 2 rounds) — round 1 forced the §14.8.1/§14.8.2 read that decomposed fork-vs-impl (fold + PRE_ACTION coupling SPEC'd → impl-to-cleared-spec, not a whole-arc fork); round 2 confirmed the no-operator-gate determination + the §6.2-silent → scope-split (per-step override fold = the follow-on) + the completeness/negative-control/broader-suite obligations
  - standing FULL-SPEC operator directive 2026-06-12 (design back-flow pre-authorized; no operator gate owed — nothing committed is sacrificed)
  - out-of-family Codex review at the impl-diff PR (decorrelated; pending)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.61`

v1.61 is a single-site reconciliation delta over v1.60 absorbing the **R-FS-1 standalone arc `B-HITL-PLACEMENT-PER-STEP-PRODUCER`**. It reconciles **§14.8.2 step 1** (the wrap-time HITL gate composer's placement-trigger read surface) from `step.hitl_placements` to `step_context.hitl_placements` — the per-step `StepExecutionContext` placement surface the CP driver composes from `WorkflowManifestEntry.hitl_placements` at workflow-binding time (CP spec v1.41 §25.3). This makes the wrap-time HITL gates (inference / sub-agent / tool — incl. the B-TOOL-GATE #653 tool gate) **fire in production**: §14.8.2 step-1's `step.hitl_placements` read was structurally unpopulatable (the frozen 3-field `WorkflowStep` is workflow body, not config), so no production producer ever populated it and no wrap-time gate fired for any step kind (the pre-existing B3-residual gap, surfaced as the B-TOOL-GATE #653 Codex [P1] finding).

**NO operator gate.** Additive + opt-in: a workflow declaring no placements → `step_context.hitl_placements = ()` → §14.8.2 step 1 short-circuits → byte-identical to pre-v1.61 (a gate fires only on a declared placement). No committed-invariant sacrifice; no new contract / fail-class / manifest field. The fold semantics (a workflow placement applies to all matching step kinds; the composer filters by `applicable_placements`) + the PRE_ACTION → {inference, tool} coupling are SPEC'd at §14.8.1 + §14.8.4 → impl-to-cleared-spec. The read-surface name change is a faithful materialization of the v1.9 "populated at workflow-binding time per U-CP-13" text (U-CP-13 = the override evaluator; `StepExecutionContext` = the per-step binding-time-composed context).

Reviewed during clearance: the read-surface choice (`StepExecutionContext` over widening `WorkflowStep` [violates §25.2 config/body] and over `StepEffectiveBinding` [whose `model_dump` feeds the §16.5.4 override hash — a hash-coherence regression]); the producer covering all 6 topologies (5 construction sites + `compose_branch_child_context` inheritance); non-vacuity proven by-execution with NO proxy (plain step + step_context → gate fires; negative control; producer via real `execute_workflow` on linear + DECENTRALIZED_HANDOFF); the wrap-time-only scope (VALIDATOR_ESCALATION is §14.15 validator-outcome-triggered, out of scope); the per-step override fold registered as the `B-HITL-PLACEMENT-PER-STEP-OVERRIDE-FOLD` follow-on (silent at C-CP-06 §6.2).

## Notes

- Phase 7 consumers may rely on this version as canonical after the bundled harness-cp + harness-runtime impl + tests land together (`merge_commit` pinned at the post-merge refresh).
- See `.harness/clearance/README.md` for marker discipline.
