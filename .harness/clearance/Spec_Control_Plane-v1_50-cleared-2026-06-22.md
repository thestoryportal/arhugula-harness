---
artifact: design-substrate/Spec_Control_Plane_v1_50.md
version: v1.50
cleared_at: 2026-06-22T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-spine-ledger (operator-RATIFIED precedence, additive CP signal — the CP half of B-MODEL-RESOLUTION-CONSOLIDATION. Adds the per-step MODEL-override SIGNAL `StepEffectiveBinding.model_binding_override: ModelBinding | None` at C-CP-06 §6.2, the `None`-or-override precedent of v1.37 `prompt_version_sha` / v1.38 `agent_role`. `model_binding` semantics byte-unchanged for every existing reader. The OPERATOR GATE — the model-resolution PRECEDENCE ORDERING `per-step > per-workload > per-role > routed > default` consumed by the runtime half — was ANSWERED by AskUserQuestion 2026-06-22 [operator chose "Model-resolution consolidation" over a per-workload sliver]. Additive field rides the per-step override state-ledger entry's outcome-hash for live provenance, NOT the run-level §5.2 hash → no IS-spec change.)
back_reference:
  - .harness/class_1_fork_model_resolution_consolidation.md (the design proposal the operator ratified; this CP delta + the runtime v1.71 delta execute it)
  - .harness/beyond-mvp-capability-boundary-ledger.md (B-MODEL-RESOLUTION-CONSOLIDATION spine BUILT note; subsumes the narrower B-ROUTING-MANIFEST-MODEL-FOLD)
  - design-substrate/Spec_Harness_Runtime_v1.md (the paired runtime v1.71 delta — §14.6.2 the precedence authority + the §14.6.2 decline-mirror invariant + the workload_class thread; the CONSUMER of this signal)
  - design-substrate/Spec_Control_Plane_v1_38.md (the per-step `agent_role` `None`-or-override + composition precedent; PRESERVED VERBATIM)
  - design-substrate/Spec_Control_Plane_v1_37.md (the per-step `prompt_version_sha` `None`-or-override + §6.6 provenance precedent; PRESERVED VERBATIM)
  - design-substrate/Spec_Control_Plane_v1_49.md (the immediately-prior head — B-HITL-PLACEMENT-PER-STEP-OVERRIDE-FOLD; §6.2 `hitl_placement` fold PRESERVED VERBATIM)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - advisor (full-transcript) — vetted the 7-step plan BEFORE code; sharpened the load-bearing invariant (the decline predicate ⊆ the `_effective_chain` authority); caught the workload-None asymmetry (mirror `self.workload_class or _MVP_DEFAULT_WORKLOAD_CLASS`) + the default-role decline asymmetry; flagged the point-7 + per-workload-routing-off witness gaps + the StepEffectiveBinding frozen/extra=forbid field-add ripple
  - out-of-family Codex (decorrelated) — pre-merge on the diff (pending)
  - operator AskUserQuestion 2026-06-22 — RATIFIED the precedence ordering (the one genuine gate) by choosing "Model-resolution consolidation" over the per-workload sliver
  - standing FULL-SPEC operator directive 2026-06-12 (design back-flow pre-authorized)
supersedes:
superseded_by:
---

# Clearance — `Spec_Control_Plane v1.50`

v1.50 is an additive delta over v1.49 absorbing the **CP half** of the R-FS-1 standalone arc **`B-MODEL-RESOLUTION-CONSOLIDATION`** (subsumes the narrower registered `B-ROUTING-MANIFEST-MODEL-FOLD`). It adds the per-step MODEL-override SIGNAL `StepEffectiveBinding.model_binding_override: ModelBinding | None = None` at **C-CP-06 §6.2** (+ §6.6 provenance), the `None`-or-override precedent of v1.37 `prompt_version_sha` / v1.38 `agent_role`.

**Why the signal is needed.** `resolve_step_binding` resolves `StepEffectiveBinding.model_binding = override.model_binding or default_model_binding` — ALWAYS concrete, so nothing downstream could distinguish a per-step model *override* from the manifest default. The C-RT-16 fallback wrapper (runtime §14.6.2) needs that signal to honour a per-step model override at the head of the operator-ratified model-resolution precedence. `model_binding` semantics are byte-unchanged for every existing reader; `model_binding_override` equals `override.model_binding` (`None` when no per-step model dimension).

**Operator-ratified precedence; additive CP signal — gate posture.** The signal field itself is additive (the v1.37/v1.38 shape) and sacrifices no committed invariant; it rides the per-step override state-ledger entry's outcome-hash for live step-level provenance (§6.6), NOT the run-level §5.2 procedural hash → no IS-spec change. The genuine operator gate — the model-resolution PRECEDENCE ORDERING `per-step > per-workload > per-role > routed > default` consumed by the runtime half — was ANSWERED by the operator's AskUserQuestion choice 2026-06-22. It mints **no** new contract / ADR / enum / fail-class / manifest field / §5.2 hash-recipe / §16.5.4 key / CXA edge.

Reviewed during clearance (verified by execution): the CP per-step override tests (a `StepOverride.model_binding` sets BOTH the concrete `model_binding` AND the `model_binding_override` signal; a non-model override → `model_binding_override` None while `model_binding` stays the default; the signal rides `binding.model_dump` for provenance). harness-cp 1165 passed / 1 xfailed; pyright 0/0/0. The cross-axis suites (harness-runtime non-e2e 2025, harness-od 950, harness-cxa 28, harness-is 171) confirm the frozen/extra=forbid field-add did not ripple to any cardinality or golden-hash assertion.

## Notes

- Phase 7 consumers may rely on this version as canonical after the bundled harness-cp + harness-runtime impl + tests land together (`merge_commit` pinned at the post-merge refresh).
- Paired runtime clearance: `.harness/clearance/Spec_Harness_Runtime-v1_71-cleared-2026-06-22.md`.
