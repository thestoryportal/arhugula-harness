# Class 1 (design) — Model-resolution consolidation (B-MODEL-RESOLUTION-CONSOLIDATION)

**Status:** PROPOSED 2026-06-22 — operator chose "Model-resolution consolidation" (AskUserQuestion, this session) over a per-workload sliver. The **precedence is operator-ratified by that choice**; this doc is the design proposal for the fresh-context BUILD to execute + ratify the impl sub-decisions. Supersedes/subsumes the registered `B-ROUTING-MANIFEST-MODEL-FOLD` (per-workload was the sliver; this is the whole-problem fix).

**Posture:** design-phase back-flow (a committed-behavior change to the C-RT-16 fallback wrapper's model-selection + a CP `StepEffectiveBinding` contract signal). FULL-SPEC pre-authorizes the back-flow; the **precedence ordering** is the operator's call (ratified) because it reorganizes committed wrapper behavior with real degrees of freedom (not an invariant-preserving impl). Cross-axis: CP spec C-CP-06 §6.2 + runtime spec §14.5.3/§14.6.

---

## 1. Verified current state — the 5 model-determining surfaces

The dispatched model is resolvable at FIVE sites; only TWO are consumed today:

| Surface | Where | Consumed today? |
|---|---|---|
| **per-step** `StepOverride.model_binding` | resolves into `StepEffectiveBinding.model_binding` (`per_step_override_evaluator.py:234` `override.model_binding or default`) | **NO** — the wrapper never reads `binding.model_binding`; no e2e test exercises a per-step model override reaching dispatch. |
| **per-role** `RoutingManifest.per_role_bindings[role].preferred_model_binding` | C-RT-16 wrapper `retry_breaker_fallback.py:_effective_chain` (`:582-590`) → augments PRIMARY | **YES** (B1 / U-RT-114). |
| **per-workload** `per_workload_overrides[workload].model_binding_override` | detected by `resolve_routed_binding` (`llm_dispatch.py:701-715`, declines routing for it) but **never applied** | **NO** — the routing-decline assumes `binding.model_binding` carries it; it doesn't. (Contrast: per-workload ENGINE [`engine_selector.py:182`] + PROMPT [`prompt_selection_manifest.py:147`] overrides ARE consumed, UNCONDITIONALLY / routing-off → present-tense gap.) |
| **routed** (EMBEDDING/L3) | wrapper `routing_resolver` → `_effective_chain(routed=…)` (`:571-578`) | **YES** (routing_activation only). |
| **default** | `config.routing_manifest.fallback_chains[0].primary` (`fallback_chain.py:137-145`, per-run, manifest-derived) | **YES** (the wrapper's base chain). |

**Root cause:** the wrapper composes the dispatched model from the **manifest-derived per-run `fallback_chain`** + `routed` + per-role — it never reads `binding.model_binding`, and it has `routing_manifest` but **no `workload_class`**. So per-step + per-workload model overrides are silently dropped.

**Design-critical gap:** `StepEffectiveBinding.model_binding` is ALWAYS set (`override.model_binding or default`) — there is **no None-or-override signal** (unlike `prompt_version_sha: str | None` / `agent_role: AgentRole | None`). So nothing downstream can tell a per-step model *override* from the default. The consolidation must add that signal.

---

## 2. Proposed design — one precedence, one site

**Ratified precedence (operator choice):** `per-step > per-role > per-workload > routed > default`.

**Single resolution site:** the wrapper `_effective_chain` (it already composes routed + per-role + chain; it is the ONE place model-candidate selection composes with C-RT-16 fallback — the existing "one source of truth — the chain" invariant). Resolve the PRIMARY by the precedence, then `_augment_primary` (existing) for the deduped fallback tail.

**Impl approach (sub-decisions for the build context to ratify):**
1. **CP signal (C-CP-06 §6.2):** add a per-step-model-override signal to `StepEffectiveBinding` so the wrapper can honor per-step > per-role. Two options — (a) NEW `model_binding_override: ModelBinding | None = None` (None-or-override, mirroring `prompt_version_sha`/`agent_role`; `model_binding` stays the concrete resolved value for back-compat), or (b) a `bool model_binding_override_applied`. **Recommend (a)** — symmetric with the prompt/role precedent, carries the override value explicitly. Additive; bundled-absorption CP spec delta.
2. **workload_class → wrapper:** thread `workload_class` to `RetryBreakerFallbackDispatcher` (new field, set at the stage-5 factory from the manifest/config — the `routing_manifest` is already threaded there) so `_effective_chain` can read `per_workload_overrides[workload].model_binding_override`. (Do NOT reach into `self.inner.workload_class` — explicit field.)
3. **`_effective_chain` precedence:** PRIMARY = first non-None of: per-step (`binding.model_binding_override`) → per-role (`per_role_bindings[role].preferred_model_binding`) → per-workload (`per_workload_overrides[workload].model_binding_override`) → routed (`routed`) → default (`self.fallback_chain.primary` unchanged). Each non-default winner goes through `_augment_primary`.
4. **routed mutual-exclusivity preserved:** `resolve_routed_binding` already declines (returns None) when a per-step/per-role/per-workload deterministic binding governs (`llm_dispatch.py:702-708`), so `routed` only fills the no-deterministic-binding gap — consistent with routed being LAST-before-default. (Verify the per-step branch: `resolve_routed_binding`'s `_has_deterministic_binding` includes `binding.override_applied`, which is true for ANY override; once the per-step-MODEL signal exists, tighten/confirm it keys on the model override specifically.)

---

## 3. Risk + invariants to preserve (the seam — the #699/#700/this-arc trap)

- **Reliability primitive:** this changes the C-RT-16 fallback wrapper's PRIMARY selection. Verify the §4.2 fallback traversal + `_augment_primary` dedup are unaffected for each new PRIMARY source.
- **§14.5.3 single dispatch-read source:** the inner still reads ONE rebound `binding.model_binding` per candidate — the precedence is resolved at the wrapper (composition-time), dispatch read unchanged. Preserve.
- **§14.6 route-once:** routing resolved ONCE at the wrapper, not per-attempt. Preserve.
- **Cross-site composition (verify, don't assume):** per-step must beat per-role (needs the signal — without it, per-role wrongly wins); per-role must beat per-workload; routed must NOT override a deterministic binding (the decline already enforces this); default unchanged when no override. Map each pair.

---

## 4. Build plan + witnesses (fresh context)

Bundled-absorption: CP spec C-CP-06 §6.2 delta (the per-step-model signal) + runtime spec §14.5.3/§14.6 delta (the wrapper precedence + workload_class) + clearance markers + harness-cp + harness-runtime impl + by-execution tests.

**By-execution witnesses (present-tense — single provider, routing OFF):**
- per-step model override → dispatched model is the override (the currently-broken case).
- per-workload model override → dispatched model is the override (ROUTING's case).
- precedence pairs: per-step beats per-role; per-role beats per-workload; per-workload beats default; routed fills only the no-override gap.
- negative control: no override → the manifest chain primary unchanged (byte-identical).
- advisor (the multi-site seam) + out-of-family Codex pre-merge.

---

## 5. Ratification points for the build context

1. **The per-step-model signal mechanism** (§2 sub-decision 1): recommend (a) `model_binding_override: ModelBinding | None`.
2. **Confirm the precedence** `per-step > per-role > per-workload > routed > default` (ratified by the option choice; re-confirm at build-open).
3. **Scope:** fix per-step AND per-workload together (the consolidation) — NOT a per-workload sliver.

**Authority chain:** operator AskUserQuestion 2026-06-22 (consolidation chosen) + FULL-SPEC directive (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`) + `[[disposition-label-is-a-claim-verify-against-spec]]` (the depth/seam discipline that surfaced this). Grounding leads in this doc §1 are verified at HEAD `eba7cfa`.
