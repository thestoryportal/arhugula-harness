# Spec: Control Plane — v1.50 (delta over v1.49)

---

## Change-note (v1.49 → v1.50)

**Scope of revision.** A single additive field at **C-CP-06 §6.2** plus its §6.6 provenance: a per-step MODEL-override **SIGNAL** `StepEffectiveBinding.model_binding_override: ModelBinding | None = None`. This is the **CP half** of the R-FS-1 standalone arc **`B-MODEL-RESOLUTION-CONSOLIDATION`** (registered at `.harness/beyond-mvp-capability-boundary-ledger.md`; subsumes the narrower registered `B-ROUTING-MANIFEST-MODEL-FOLD` — per-workload was the sliver, this is the whole model-resolution-precedence fix). The paired **runtime half** (the C-RT-16 wrapper resolving the full precedence per-step > per-workload > per-role > routed > default at the single `_effective_chain` site + the `workload_class` thread + the §14.6.2 decline-mirror invariant) lands in the co-published runtime spec v1.70 → v1.71 delta.

**The problem this signal solves.** `resolve_step_binding` resolves `StepEffectiveBinding.model_binding = override.model_binding or default_model_binding` — it is **ALWAYS** a concrete value, so nothing downstream can distinguish a per-step model *override* from the manifest default. The C-RT-16 fallback wrapper (runtime §14.5.3/§14.6) therefore could not honour a per-step model override (it never read `binding.model_binding`, and a coarse `override_applied` proxy could not tell a model override from an hitl/engine/prompt/role-only override). The fix mirrors the existing `prompt_version_sha` (v1.37) / `agent_role` (v1.38) precedent: a **`None`-or-override SIGNAL** distinct from the concrete `model_binding`.

**Additive, no committed invariant sacrificed — but the operator RATIFIED the precedence ordering.** The signal field itself is additive (a new `None`-or-override field on `StepEffectiveBinding`, exactly the v1.37/v1.38 shape) and sacrifices no committed invariant — like its precedents it mints no new contract, ADR, enum, fail-class, manifest field, or CXA edge, and it does **not** enter the run-level §5.2 procedural-tier hash (`StepEffectiveBinding` is not run-level-hashed; the field rides `binding.model_dump(...)` into the WIRED per-step override state-ledger entry's outcome-hash for live step-level provenance, §6.6 — the v1.37/v1.38 disposition, no IS-spec change). **What was operator-gated is the model-resolution PRECEDENCE ORDERING** consumed by the runtime half: `per-step > per-workload > per-role > routed > default`, operator-ratified by AskUserQuestion 2026-06-22 (the operator chose "Model-resolution consolidation" over a per-workload sliver). That choice reorganizes committed C-RT-16 wrapper PRIMARY-selection behavior with real degrees of freedom, so it is the operator's call — and it is recorded as ratified. This CP delta carries the signal the runtime precedence reads; FULL-SPEC (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`) pre-authorizes the back-flow.

**`model_binding` semantics UNCHANGED.** `StepEffectiveBinding.model_binding` continues to be the concrete resolved value (`override.model_binding or default_model_binding`) for back-compat — every existing reader sees the identical value. The new `model_binding_override` is purely the **provenance/precedence signal**: it equals `override.model_binding` (so `None` when the per-step override carries no model dimension, or when there is no override at all).

**v1.49 + prior body PRESERVED VERBATIM.** All v1.49 content — the §6.2 `hitl_placement` fold + the entire C-CP-01 … C-CP-29 body incl. §6.1 (`StepOverride` schema) / §6.3 / §6.4 / §6.5 / §6.6 / §16.5.x / §25.x / §26.x — is PRESERVED VERBATIM per the delta-only-spec-file convention. Within C-CP-06: §6.1 / §6.3 / §6.4 / §6.5 / §16.5.x are PRESERVED VERBATIM; the changes are (a) the additive `StepEffectiveBinding.model_binding_override` field at §6.2 and (b) the §6.6 provenance extension noted below. The §6.2 `hitl_placement` fold (v1.49) is PRESERVED VERBATIM.

---

## §1 — Amended C-CP-06 §6.2 `StepEffectiveBinding` — new per-step MODEL-override signal

`resolve_step_binding` gains one additive resolution, alongside the existing field-by-field discipline (the `None`-or-override precedent of `prompt_version_sha` v1.37 + `agent_role` v1.38):

> **`StepEffectiveBinding.model_binding_override: ModelBinding | None = None` (NEW at v1.50).** The resolved per-step MODEL override — `override.model_binding` when a `StepOverride` for this step carries a `model_binding`, else `None`.
>
> - **Distinct from `model_binding`.** `model_binding` (unchanged) is the concrete resolved value `override.model_binding or default_model_binding`, ALWAYS set; `model_binding_override` is the `None`-or-override SIGNAL — `None` means "no per-step model override" so a downstream consumer can tell a per-step override from the manifest default (which `model_binding` alone cannot express). Mirrors `prompt_version_sha` / `agent_role`.
> - **No override / non-model override → `None`.** A step with no `StepOverride`, or a `StepOverride` that carries only `engine_class` / `hitl_placement` / `prompt_version_sha` / `agent_role` (no `model_binding`), resolves `model_binding_override = None` (while `model_binding` still resolves to the manifest default). This is what lets the runtime half NOT over-suppress routing on a non-model per-step override (runtime §14.6.2).
> - **Consumed by the C-RT-16 wrapper.** The runtime fallback wrapper reads `binding.model_binding_override` as the HEAD of the model-resolution precedence `per-step > per-workload > per-role > routed > default` (runtime §14.5.3/§14.6). The CP layer only PRODUCES the signal; the precedence resolution is runtime-side.

The §6.2 field-by-field-no-field-set-substitution discipline is otherwise unchanged.

---

## §2 — Amended C-CP-06 §6.6 provenance scope

The §6.6 per-step-override provenance (v1.37/v1.38) extends to `model_binding_override`: because it is a `StepEffectiveBinding` field, it rides `binding.model_dump(...)` — which IS `post_override_step_config` at the WIRED per-step override state-ledger entry (`workflow_driver.py`) — so a per-step model flip is captured in that entry's outcome-hash (**live step-level provenance**, NOT the run-level §5.2 procedural-tier hash). Identical disposition to `prompt_version_sha` / `agent_role`; **no IS-spec change** (the run-level §5.2 hash recipe is untouched; `StepEffectiveBinding` is not run-level-hashed).

---

## §3 — Status

Additive `StepEffectiveBinding.model_binding_override` SIGNAL (the `None`-or-override precedent of v1.37 `prompt_version_sha` / v1.38 `agent_role`), absorbing the **CP half** of the FULL-SPEC-pre-authorized R-FS-1 standalone arc `B-MODEL-RESOLUTION-CONSOLIDATION` (subsumes `B-ROUTING-MANIFEST-MODEL-FOLD`). The signal lets the runtime C-RT-16 wrapper honour a per-step model override at the head of the operator-ratified model-resolution precedence `per-step > per-workload > per-role > routed > default`.

**Operator-ratified precedence; additive CP signal.** The PRECEDENCE ORDERING is operator-ratified (AskUserQuestion 2026-06-22 — consolidation chosen over the per-workload sliver). The CP signal field itself is additive and sacrifices no committed invariant: `model_binding` semantics are byte-unchanged for every existing reader; no new contract / ADR / enum / fail-class / manifest field / CXA edge; the field rides the per-step override state-ledger entry's outcome-hash for live provenance only (NOT the run-level §5.2 hash → no IS-spec change). An absent or non-model per-step override → `model_binding_override = None` → byte-identical downstream behaviour.

Apply pass: this delta co-published with harness-cp impl (`StepEffectiveBinding.model_binding_override` field + `resolve_step_binding` sets `model_binding_override=override.model_binding`) + the paired runtime spec v1.71 delta + harness-runtime impl (the `_effective_chain` precedence, `workload_class` thread, decline-mirror) + by-execution tests (CP: applies-model-override, none-without-model-override, provenance-rides-dump; runtime: full-chain wrapper witnesses + inner-decline alignment) + clearance markers + spine-ledger registration, per workspace `CLAUDE.md` §11.4 bundled-absorption.

v1.49 + earlier PRESERVED VERBATIM per delta-only-spec-file convention. The entire C-CP-01 … C-CP-29 body + §5.x + §6.1/§6.3–§6.5 + §6.2 `hitl_placement` fold + §16.5.x + §25.x + §26.x PRESERVED VERBATIM (the only changes: the additive §6.2 `model_binding_override` field + the §6.6 provenance extension). IS spec UNCHANGED (no §5.2 hash-recipe / §16.5.4 key change). CXA v2.20 UNCHANGED (no new typed edge). ADR-F1/F2/F3/D1–D6 UNCHANGED. ADD v1.3 + PRD v1.1 UNCHANGED. Paired runtime spec v1.70 → v1.71.

Clearance marker filed at `.harness/clearance/Spec_Control_Plane-v1_50-cleared-2026-06-22.md`.

2026-06-22.
