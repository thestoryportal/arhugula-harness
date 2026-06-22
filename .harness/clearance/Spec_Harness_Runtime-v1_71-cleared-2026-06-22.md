---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.71
cleared_at: 2026-06-22T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-spine-ledger (operator-RATIFIED precedence — the runtime half of B-MODEL-RESOLUTION-CONSOLIDATION. New §14.6.2: the C-RT-16 wrapper resolves the dispatched model from ALL 5 sources at the single `_effective_chain` authority in the operator-ratified precedence `per-step > per-workload > per-role > routed > default`; before v1.71 per-step + per-workload MODEL overrides were SILENTLY DROPPED. Adds the wrapper `workload_class` field + the §14.6.2 decline-mirror invariant [the `resolve_routed_binding` decline must never be STRICTER than the authority, else a model that should route is dropped to default]. The precedence ORDERING was ANSWERED by AskUserQuestion 2026-06-22. No new contract / fail-class / §5.2-hash / Protocol-widening / CXA edge.)
back_reference:
  - .harness/class_1_fork_model_resolution_consolidation.md (the design proposal the operator ratified; this runtime delta + the CP v1.50 delta execute it)
  - .harness/beyond-mvp-capability-boundary-ledger.md (B-MODEL-RESOLUTION-CONSOLIDATION spine BUILT note; subsumes the narrower B-ROUTING-MANIFEST-MODEL-FOLD)
  - design-substrate/Spec_Control_Plane_v1_50.md (the paired CP half — the per-step MODEL-override SIGNAL `StepEffectiveBinding.model_binding_override` this §14.6.2 precedence reads at its head)
  - design-substrate/Spec_Harness_Runtime_v1.md (§14.6.1 B-L2-FALLBACK-COMPOSITION — the routed-tier composition this consolidation slots between per-workload and default; PRESERVED VERBATIM, with a decline-condition-refinement NOTE; §14.5.3 per-role dispatch-read PRESERVED VERBATIM)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - advisor (full-transcript) — vetted the plan BEFORE code; sharpened the §14.6.2 invariant (decline predicate ⊆ `_effective_chain` authority, one-directional: lenient-harmless / stricter-drops); caught the workload-None asymmetry (`self.workload_class or _MVP_DEFAULT_WORKLOAD_CLASS` must mirror at both sites) + the default-role decline asymmetry; flagged the point-7 (non-model per-step) + per-workload-routing-off witness gaps + the StepEffectiveBinding frozen field-add ripple
  - out-of-family Codex (decorrelated) — pre-merge on the diff (pending)
  - operator AskUserQuestion 2026-06-22 — RATIFIED the precedence ordering (the one genuine gate)
  - standing FULL-SPEC operator directive 2026-06-12 (design back-flow pre-authorized)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.71`

v1.71 is a delta over v1.70 absorbing the **runtime half** of the R-FS-1 standalone arc **`B-MODEL-RESOLUTION-CONSOLIDATION`** (subsumes the narrower registered `B-ROUTING-MANIFEST-MODEL-FOLD`). New **§14.6.2**: the C-RT-16 fallback wrapper resolves the dispatched model from ALL FIVE sources at the SINGLE `_effective_chain` authority in the operator-ratified precedence **per-step > per-workload > per-role > routed > default**.

**The gap closed.** Before v1.71 only per-role + routed + default were consumed; **per-step (`StepOverride.model_binding`) and per-workload (`per_workload_overrides[workload].model_binding_override`) MODEL overrides were SILENTLY DROPPED** — the wrapper never read `binding.model_binding` and had `routing_manifest` but no `workload_class`. The §14.6.1 step-2 "DECLARATIVE echoes `binding.model_binding`" was aspirational for those tiers (only `resolve_routed_binding` *declined* on them; the wrapper then fell through to per-role/default).

**The build.** (1) The CP half (paired CP v1.50) adds the per-step MODEL SIGNAL `StepEffectiveBinding.model_binding_override`. (2) The wrapper gains an explicit `workload_class` field (stage-5-bound from the run workload; NOT `self.inner.workload_class`). (3) `_effective_chain(binding, agent_role, *, routed)` resolves the 5-tier precedence (first non-`None`; each non-default winner through `_augment_primary`). (4) `resolve_routed_binding`'s decline expression is aligned to MIRROR `_effective_chain` EXACTLY.

**The §14.6.2 invariant (the advisor's load-bearing catch).** The decline predicate ⊆ the precedence authority. One-directional: a more-LENIENT decline (produces a routed candidate `_effective_chain` ignores) is a harmless wasted call; a STRICTER decline (returns `None` while `_effective_chain` also skips the source) silently drops the model that should have routed to `default`. v1.71 aligns all three conjuncts: per-step tightens `override_applied` → `binding.model_binding_override is not None` (a non-model per-step override no longer over-suppresses routing); per-role gains the default-role exclusion (a default-role binding is dead config at both sites); per-workload mirrors `self.workload_class or _MVP_DEFAULT_WORKLOAD_CLASS` (the wrapper-None + default-workload-override case no longer drops).

**Reliability-primitive invariants preserved.** PRIMARY selection only; the §4.2 fallback traversal + `_augment_primary` dedup are unaffected; the §14.5.3 single dispatch-read + the §14.6 route-once hold (precedence resolved at composition-time; routing resolved once at the wrapper). Operator-ratified precedence; otherwise impl-to-cleared / runtime-internal — **no new contract / fail-class / §5.2-hash / `StepDispatcher` Protocol widening / CXA edge**. The per-step + per-workload MODEL tiers are LIVE present-tense (single provider, routing off); the routed tier stays production-dormant until a second provider.

Reviewed during clearance (verified by execution): full-chain wrapper by-execution witnesses (per-step model dispatched — the broken case; per-workload model dispatched routing-OFF; the default-workload-class mirror; precedence pairs per-step>per-role / per-workload>per-role / per-workload>default / per-step>routed / per-workload>routed; negative control no-override → stage chain unchanged) + inner-decline alignment (model-specific per-step pins DECLARATIVE; non-model per-step + default-role bindings do NOT block embedding). pyright 0/0/0; harness-runtime non-e2e 2025 passed / 13 skipped; harness-cp 1165 / 1 xfailed; harness-od 950 / harness-cxa 28 / harness-is 171 (cross-axis ripple clean).

## Notes

- Phase 7 consumers may rely on this version as canonical after the bundled harness-cp + harness-runtime impl + tests land together (`merge_commit` pinned at the post-merge refresh).
- Paired CP clearance: `.harness/clearance/Spec_Control_Plane-v1_50-cleared-2026-06-22.md`.
