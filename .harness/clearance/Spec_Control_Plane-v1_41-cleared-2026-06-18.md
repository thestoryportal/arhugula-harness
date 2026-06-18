---
artifact: design-substrate/Spec_Control_Plane_v1_41.md
version: v1.41
cleared_at: 2026-06-18T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc (NO operator gate — additive StepExecutionContext field, a binding fix in the tenant_id/parent_gate_level precedent; no committed-invariant sacrifice)
back_reference:
  - .harness/class_1_fork_b_hitl_placement_per_step_producer.md
  - .harness/beyond-mvp-capability-boundary-ledger.md (B-HITL-PLACEMENT-PER-STEP-PRODUCER spine BUILT note)
  - design-substrate/Spec_Harness_Runtime_v1.md (v1.61 — the paired §14.8.2-step-1 composer read reconciliation)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - advisor (full-transcript, 2 rounds) — confirmed StepExecutionContext (not StepEffectiveBinding) as the carrier (the model_dump→§16.5.4-hash regression avoided), the binding-fix-no-gate determination, and the scope split
  - standing FULL-SPEC operator directive 2026-06-12 (design back-flow pre-authorized; no operator gate owed)
  - out-of-family Codex review at the impl-diff PR (decorrelated; pending)
supersedes:
superseded_by:
---

# Clearance — `Spec_Control_Plane v1.41`

v1.41 is an additive-field delta over v1.40 absorbing the **R-FS-1 standalone arc `B-HITL-PLACEMENT-PER-STEP-PRODUCER`**. It adds one additive, defaulted field on **C-CP-25 §25.3 `StepExecutionContext`**: `hitl_placements: tuple[HITLPlacement, ...] = ()` — the workflow's declared C-CP-17 §17.3 `WorkflowManifestEntry.hitl_placements`, surfaced by the CP driver onto the per-step execution context at workflow-binding time so the runtime wrap-time HITL gate composer (runtime spec v1.61 §14.8.2 step 1) reads the workflow's placements per-step. This is the CP-side half of the producer that lights up the wrap-time HITL gates (inference / sub-agent / tool) in production.

**NO operator gate.** Wiring an EXISTING manifest value (`WorkflowManifestEntry.hitl_placements`) onto the per-step `StepExecutionContext` is a binding fix — the same shape as the `tenant_id` lift ("NOT a `WorkflowManifestEntry` schema extension") and the `parent_gate_level` v1.20 manifest→context surfacing. It mints no new contract / enum / fail-class / manifest field, and sacrifices no committed invariant (default `()` → byte-identical). Additive + defaulted, the v1.32 `branch_index`/`agent_role` extension discipline.

Reviewed during clearance: the carrier choice — `StepExecutionContext` (per-step execution metadata, NOT hashed into any ledger entry) over `StepEffectiveBinding` (whose `model_dump` feeds the §16.5.4 per-step override outcome-hash — carrying placements there would shift the override-entry hash for override-bearing steps, a hash-coherence regression, and is semantically wrong: a workflow placement is not a per-step override); the workflow-scoped semantics (identical for every step per §17.1 "all cells"); the producer covering all 6 topologies (5 construction sites + `compose_branch_child_context` inheritance); the per-step `StepOverride.hitl_placement` override fold deferred to the `B-HITL-PLACEMENT-PER-STEP-OVERRIDE-FOLD` follow-on (silent at C-CP-06 §6.2).

## Notes

- Phase 7 consumers may rely on this version as canonical after the bundled harness-cp + harness-runtime impl + tests land together (`merge_commit` pinned at the post-merge refresh).
- See `.harness/clearance/README.md` for marker discipline.
