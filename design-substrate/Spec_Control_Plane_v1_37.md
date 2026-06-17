# Spec: Control Plane — v1.37 (delta over v1.36)

---

## Change-note (v1.36 → v1.37)

**Scope of revision.** A single additive field on the **C-CP-06 §6.1 `StepOverride`** per-step override record — NEW **`prompt_version_sha: str | None = None`** — plus its propagation through **§6.2** (`StepEffectiveBinding.prompt_version_sha` + `resolve_step_binding` field-by-field application) and a **§6.6 (NEW) provenance-scope** sub-section. This is the **R-FS-1 arc B4 Slice 3** leg (per-step prompt override): an operator annotates a specific workflow step with a prompt `version_sha`, and that step's LLM dispatch injects the corresponding store-resolved content as the provider system prompt (§14.5.2 translate seam), taking precedence over the per-role (Slice 1, #616) and run-level-default prompts. Design authority: `.harness/class_1_fork_b4_per_step_prompt_override_stepoverride_extension.md` (filed + resolved this arc) + R-FS-1 arc-B4 grounding sweep. The per-step **model** override already exists (`StepOverride.model_binding`); per-step **prompt** is the Slice-3 increment.

**Why a spec amendment (the X-AL-3 fork).** Extending the cleared `StepOverride` schema is governed by the **v1.27 §2(d) "X-AL-3 explicit-extension discipline"** — the canonical-long-term path for `StepOverride` / `WorkflowManifestEntry` field growth, with **mirror precedents v1.20 `default_gate_level` + v1.22 `tenant_id` + v1.34 webhook-ctor binding-lift arcs**. The v1.2 baseline `// ... additional per-workload fields` extension clause sits inside the `WorkflowManifestEntry {}` block (it authorized `entry_version` at plan v2.12 with no spec bump) — it does **not** cover the `StepOverride` sub-record. So the field add is owed an explicit §6.1 amendment, not impl-discretion. Under the standing FULL-SPEC directive (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`, 2026-06-12) the design back-flow is **pre-authorized**, authored here as this delta + the paired fork doc + clearance + bundled-absorption impl.

**Surface choice — `StepOverride`, not `PromptSelectionManifest` (probe-resolved, no operator gate).** A per-step prompt could live in the run-level `PromptSelectionManifest` (C-CP-29; coherence-free since `prompt_selection_manifest_sha` already hashes the whole manifest). **Rejected:** `PromptSelectionManifest.per_role_bindings`/`per_workload_overrides` key on **categories** (role, workload — cross-workflow, correctly run-level); a `step_id` is an **instance inside a specific workflow**. Putting `step_id`s in a run-level selection manifest breaks the abstraction level and is a Track-B reuse hazard (step-id collision across workflows sharing one manifest). The per-step override surface is the one §14.5.3 names as the B4 deliverable and is `step_id`-correctly workflow-scoped (`StepOverride` belongs to one `WorkflowManifestEntry`).

**Provenance scope — the WIRED per-step override state-ledger entry, NOT the run-level §5.2 hash (no IS-spec change).** §14.5.2 holds the coherence invariant ("the §5.2 procedural-tier hash cannot report 'unchanged' while injected content changes"). Slice 1 (#616) brought the per-**role** catalog into §5.2 because `per_role_bindings` is **run-level config**. A per-**step** override is a different provenance **scope**: it lives on the per-workflow `WorkflowManifestEntry.per_step_overrides`, which is **not** on the runtime `HarnessContext` the §5.2 resolver reads (`run_bootstrap` does not receive `manifest_entry`). Per-step coherence is satisfied at the **already-WIRED per-step override state-ledger entry** — `emit_override_state_ledger_entry` is invoked at the driver per-step site (`workflow_driver.py:1913-1930`, gated on `binding.override_applied`) and its idempotency_key hashes `post_override_step_config = binding.model_dump(mode="json")`, i.e. the **whole `StepEffectiveBinding`**. So the NEW `StepEffectiveBinding.prompt_version_sha` is **automatically** captured (a per-step prompt flip ⟹ different `binding.model_dump` ⟹ different override-entry idempotency_key ⟹ a distinct hash-chained ledger entry that *also* carries `procedural_tier_snapshot_ref`: run-level base + step-level delta together fully pin the step's effective prompt). This follows the per-step **MODEL** override precedent (model override → override-ledger entry, never §5.2). The §14.5.2 line-3078 invariant remains satisfied at the run-level scope; per-step deviation is recorded one layer down at the correct scope. The earlier v1.27 §16.5.6 "`emit_override_state_ledger_entry` has no production caller" note is **stale vs HEAD** — the composer is wired.

**Per-step ROLE is OUT of scope (Slice-4 gate).** This delta adds only per-step **prompt**. A per-step *role* carrier would be "a second per-step role carrier" the runtime spec §14.5.3 **"Single role source"** invariant forecloses (branch role flows **only** via `step_context.agent_role`); it is the Slice-4 gate, surfaced at Slice-4 arc-open — neither built nor dropped here. Per-step **prompt** sacrifices no committed invariant (additive optional field, symmetric with the existing per-step `model_binding`) → **no operator gate**.

**Runtime dispatch mechanism = impl-discretion (per §14.5.3).** §14.5.3 defers "the per-step override surface" to implementation discretion, so the runtime dispatch precedence (**per-step `binding.prompt_version_sha` > per-role > run-level default**), the content resolution (bootstrap `prompt_versions_by_sha` map over `ctx.prompt_manifest.versions`), the **fail-loud** unauthored-sha guard (`RT-FAIL-PROMPT-SELECTION-UNAUTHORED`, mirroring the per-role path), and the **binding-tier governance parity** (`RT-FAIL-PROMPT-VERSION-UNAPPROVED` when `binding.persona_tier` requires approval and the sha is unapproved) are impl-discretion and co-land in the same PR. The §14.5.2 `RT-FAIL-PROMPT-INJECTION-CONFLICT` precedence applies to the per-step-injected prompt unchanged.

**No new contract ID; no new ADR; no enum change; no new fail class; no six-field / §5.2-hash / §16.5 idempotency-formula change.** `prompt_version_sha` is an additive optional field on the existing **C-CP-06** contract. It mints no primitive — the per-step override evaluator with field-by-field application is committed at C-CP-06 §6.2; v1.37 adds the prompt dimension to it. The §16.5.4 row U-CP-14 idempotency-key formula is **PRESERVED VERBATIM** (the prompt sha rides `post_override_step_config`'s outcome-hash, not the key formula). The runtime fail-classes `RT-FAIL-PROMPT-SELECTION-UNAUTHORED` / `RT-FAIL-PROMPT-VERSION-UNAPPROVED` are pre-existing (CP §29.4 / OD C-OD-34), reused — not new.

**v1.36 + prior body PRESERVED VERBATIM.** All v1.36 content — §2.5 (Layer-3 LLM_AS_ROUTER resolution surface) + §19.1.2 + §27.8 + §7.4 + §25.10–§25.18 + §29 + the entire C-CP-01 … C-CP-29 body — is PRESERVED VERBATIM per the delta-only-spec-file convention. Within C-CP-06: §6.3 (per-step opt-in scope) / §6.4 (audit-surface composition) / §6.5 (persona-tier resolution) / §16.5.x (the §16.5 composer family) are **PRESERVED VERBATIM**; the **only** changes are the additive field at §6.1, its propagation at §6.2, and the NEW §6.6 below.

---

## §1 — Amended §6.1 `StepOverride` schema (ADDS `prompt_version_sha`)

The `StepOverride` record at C-CP-06 §6.1 gains one additive optional field. The v1.6 field set (`step_id`, `model_binding`, `engine_class`, `hitl_placement`) is PRESERVED VERBATIM; `prompt_version_sha` joins per the v1.27 §2(d) explicit-extension discipline:

```
StepOverride {
    step_id            : StepID
    model_binding      : ModelBinding | None = None
    engine_class       : EngineClass  | None = None
    hitl_placement     : HITLPlacement | None = None
    prompt_version_sha : str | None = None   // NEW v1.37 — per-step prompt override (R-FS-1 B4 Slice 3)
}
```

`prompt_version_sha` (when not `None`) is a **content-addressed reference** into the IS `PromptManifest.versions` store (IS spec v1.7 §5.3): the `version_sha` of the prompt version whose `content` is injected as the provider system prompt for **this step**, overriding the per-role and run-level-default prompts. `None` (the default) preserves v1.6 MVP behavior verbatim — the step inherits the per-role (if its branch role binds one) or run-level-default prompt. `extra="forbid"` + `frozen=True` are unchanged. The field is symmetric with the existing per-step `model_binding` (a per-step selection of a resource the run otherwise resolves at a coarser scope).

## §2 — Amended §6.2 per-step override evaluator (propagation)

`StepEffectiveBinding` (C-CP-06 §6.2) gains the matching effective field; `resolve_step_binding` applies the override field-by-field per the existing §6.2 discipline (an absent override field inherits the coarser-scope default; here the "default" is `None` — the per-step layer simply declines to override, and the per-role/run-level resolution downstream applies):

```
StepEffectiveBinding {
    ... (v1.17 fields PRESERVED VERBATIM: step_id, model_binding, engine_class,
         hitl_placement, override_applied, override_audit_ref, persona_tier)
    prompt_version_sha : str | None = None   // NEW v1.37 — the resolved per-step prompt sha (override value, else None)
}
```

`resolve_step_binding` sets `prompt_version_sha = override.prompt_version_sha` when an override is present for the step (else `None`). Unlike `model_binding`/`engine_class` — which resolve to a concrete value (override-or-manifest-default) — the prompt field is **`None`-or-override**: there is no manifest-entry-level prompt default to fall back to (the run-level default + per-role prompts are resolved downstream at the runtime dispatch, not at the CP manifest entry). A `None` here means "no per-step prompt override" → the runtime dispatch falls through to per-role then run-level default. The field-by-field-no-field-set-substitution discipline (§6.2) is unchanged. **CP stays IS-pure**: `resolve_step_binding` passes the sha through; the store-membership resolution + content injection are the runtime consumer's responsibility (the §14.5.2 dispatch seam), mirroring how the per-role mechanism resolves shas to content at the runtime, not in CP.

## §3 — NEW §6.6 Per-step prompt override provenance scope

The per-step prompt override's provenance is the **per-step override state-ledger entry** (the §16.5 (S) sibling composer `emit_override_state_ledger_entry`), **not** the run-level C-IS-05 §5.2 procedural-tier hash. The driver per-step site emits the override state-ledger entry when `binding.override_applied` is true, hashing `post_override_step_config = StepEffectiveBinding.model_dump(...)` into the §16.5.4 row U-CP-14 idempotency-key's outcome-hash. Because `prompt_version_sha` is a `StepEffectiveBinding` field, a per-step prompt change is captured in that hash → a distinct hash-chained ledger entry whose `procedural_tier_snapshot_ref` pins the run-level procedural base and whose outcome-hash pins the step-level prompt delta. The `version_sha` is content-derived (`== prompt_version_sha(content)`, IS §5.2 v1.6 derive-invariant) over a content-addressed store, so the recorded sha pins exact injected content.

This is the **per-step scope** analogue of the §14.5.2 coherence invariant: a *run-level* injected-content change (active prompt / run-level selection catalog) must change the §5.2 hash (satisfied by C-IS-05 §5.2 v1.9 incl. `prompt_selection_manifest_sha`); a *per-step* injected-content change must change the per-step override ledger entry (satisfied here). The two scopes compose — they do not collide. No C-IS-05 §5.2 recipe change is owed for the per-step dimension (folding step-level per-workflow data into the run-level hash would force `manifest_entry` onto `HarnessContext` for zero provenance gain over the wired override entry). This follows the per-step **model** override precedent, which has always recorded its provenance at the override ledger entry, never the §5.2 hash.

---

## §4 — Status

Additive C-CP-06 §6.1 field (`prompt_version_sha`) + §6.2 propagation + NEW §6.6 provenance-scope, absorbing the operator-pre-authorized (FULL-SPEC directive) R-FS-1 B4 Slice 3 per-step prompt override. Per the v1.27 §2(d) X-AL-3 explicit-extension discipline (mirror precedents v1.20/v1.22/v1.34). **No operator gate** — additive optional field, no committed invariant sacrificed (per-step *role* — which would collide with the §14.5.3 single-role-source invariant — is the distinct Slice-4 gate, OUT of scope here). Apply pass: this delta co-published with harness-cp impl (`StepOverride` + `StepEffectiveBinding` + `resolve_step_binding`) + harness-runtime impl (dispatch precedence + fail-loud + governance parity) + tests + fork doc closure + clearance marker per workspace `CLAUDE.md` §11.4 bundled-absorption.

v1.36 + v1.35 + earlier PRESERVED VERBATIM per delta-only-spec-file convention. C-CP-06 §6.3/§6.4/§6.5 + §16.5.x + the entire C-CP-01 … C-CP-29 body PRESERVED VERBATIM. CXA UNCHANGED (intra-CP-axis + a runtime-mediated per-step injection; no new typed cross-axis edge — the per-step prompt rides the existing CP→IS store-consultation + CP→runtime dispatch seams). IS spec UNCHANGED (provenance at the per-step override ledger entry; §5.2 recipe unchanged). ADR-F1/F2/F3/D1–D6 UNCHANGED. ADD v1.3 + PRD v1.1 UNCHANGED.

Clearance marker filed at `.harness/clearance/Spec_Control_Plane-v1_37-cleared-2026-06-17.md`.

2026-06-17.
