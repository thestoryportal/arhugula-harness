# Spec: Control Plane — v1.41 (delta over v1.40)

---

## Change-note (v1.40 → v1.41)

**Scope of revision.** A single additive field on **C-CP-25 §25.3 `StepExecutionContext`**: `hitl_placements: tuple[HITLPlacement, ...] = ()` — the workflow's declared C-CP-17 §17.3 `WorkflowManifestEntry.hitl_placements`, surfaced by the CP driver onto the per-step execution context at workflow-binding time so the runtime wrap-time HITL gate composer (runtime spec §14.8.2 step 1) can read the workflow's placements per-step. This is the **R-FS-1 standalone arc `B-HITL-PLACEMENT-PER-STEP-PRODUCER`** (registered at `.harness/beyond-mvp-capability-boundary-ledger.md`; design authority `.harness/class_1_fork_b_hitl_placement_per_step_producer.md`), the cross-cutting producer that lights up the wrap-time HITL gates (inference / sub-agent / tool — incl. the B-TOOL-GATE #653 tool gate) **in production**.

**No contract change of substance; this is a binding fix + impl-to-cleared-spec — NO operator gate.** The HITL placement *declaration* surface (`WorkflowManifestEntry.hitl_placements`, C-CP-17 §17.3) and the per-step execution context (`StepExecutionContext`, C-CP-25 §25.3) **already exist**. The runtime composer body (runtime §14.8.2 step 1) already expects the workflow's placements to be readable per-step "populated at workflow-binding time per U-CP-13 + U-CP-38"; nothing populated them because the frozen 3-field `WorkflowStep` (workflow *body* per §25.2, NOT config) cannot carry config. Wiring an **existing** manifest value onto the per-step `StepExecutionContext` is a **binding fix** — the same shape as the `tenant_id` lift (the StepExecutionContext docstring: "lifted as a binding fix … NOT a `WorkflowManifestEntry` schema extension") and the `parent_gate_level` v1.20 manifest→context surfacing. It mints **no** new contract, enum, fail-class, or manifest field, and **sacrifices no committed invariant** — an absent placement (`hitl_placements = ()`, the default) → the composer short-circuits → byte-identical to pre-arc. Because nothing committed is sacrificed, there is **no operator gate** (`[[feedback-gate-only-on-meaningful-architecture-change]]`); FULL-SPEC (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`) pre-authorizes the build + back-flow.

**Workflow-scoped, on the execution context — NOT the override binding.** `hitl_placements` is workflow-scoped (identical for every step of a workflow; the §17.1 trigger table applies each placement to "all cells"), so it rides `StepExecutionContext` (the per-step *execution metadata*), **NOT** `StepEffectiveBinding` (the per-step *override resolution*). This is a deliberate carrier choice: `StepEffectiveBinding.model_dump(...)` feeds the per-step override outcome-hash (`compose_override_entry_payload` at `workflow_driver.py`), so carrying placements there would shift the §16.5.4 override-entry hash for override-bearing steps — semantically wrong (a workflow placement is not a per-step override) and a hash-coherence regression. `StepExecutionContext` is not hashed into any ledger entry, so the field is inert to the §5.2 procedural-tier hash and the §16.5.4 idempotency key.

**Producer covers all topologies.** The CP driver sets `hitl_placements=manifest_entry.hitl_placements` at every per-step `StepExecutionContext` construction (the `SINGLE_THREADED_LINEAR` per-step site + the 5 non-linear strategy root contexts); branch children inherit it via `compose_branch_child_context`'s `model_copy` (the mechanism shared by every branch-based topology). Proven by-execution through the real `execute_workflow` on the linear path (direct construction) AND DECENTRALIZED_HANDOFF (inherited).

**Scope — wrap-time gates only; per-step override fold is a registered follow-on.** VALIDATOR_ESCALATION fires via the §14.15 mid-step re-entry path on validator outcome, NOT a step-read placement → out of scope. The per-step `StepOverride.hitl_placement` override fold (composing the singular per-step override with the workflow tuple) is **silent at C-CP-06 §6.2** (which specifies only `f3_invocation` per-step overrides) → registered as the follow-on `B-HITL-PLACEMENT-PER-STEP-OVERRIDE-FOLD` (carries its own under-specified add-vs-replace semantic decision). `StepEffectiveBinding.hitl_placement` stays dead this arc (no regression).

**v1.40 + prior body PRESERVED VERBATIM.** All v1.40 content — the §6.6 topology-scope note + §5.x + the entire C-CP-01 … C-CP-29 body incl. §25.x — is PRESERVED VERBATIM per the delta-only-spec-file convention; the **only** change is the additive §25.3 field below.

---

## §1 — Amended C-CP-25 §25.3 `StepExecutionContext` (additive field)

The §25.3 `StepExecutionContext` field set is extended by **one additive, defaulted field** (preserving the existing field semantics verbatim):

> **`hitl_placements: tuple[HITLPlacement, ...] = ()` (NEW at v1.41).** The workflow's declared HITL placements (C-CP-17 §17.3 `WorkflowManifestEntry.hitl_placements`), surfaced onto the per-step execution context at workflow-binding time. The CP driver composes it from `manifest_entry.hitl_placements` at every per-step `StepExecutionContext` construction (the linear per-step site + the 5 non-linear strategy root contexts; branch children inherit via `compose_branch_child_context`'s `model_copy`). The runtime wrap-time HITL gate composer reads it per-step at runtime §14.8.2 step 1 and filters by the composer's `applicable_placements` set (runtime §14.8.1). Default `()` → no placement declared → the composer short-circuits to the inner dispatcher (byte-identical to pre-arc). Workflow-scoped (identical for every step; the §17.1 "all cells" applicability), NOT a per-step override — placements are workflow config per §25.2, so the field rides `StepExecutionContext` (per-step execution metadata), NOT `StepEffectiveBinding` (whose `model_dump` feeds the §16.5.4 override outcome-hash). The per-step `StepOverride.hitl_placement` override fold is the separate follow-on `B-HITL-PLACEMENT-PER-STEP-OVERRIDE-FOLD`.

The existing `StepExecutionContext` fields (`workflow_id`, `parent_action_id`, `parent_gate_level`, `parent_sandbox_tier`, `parent_actor`, `parent_entry_hash`, `parent_idempotency_key`, `tenant_id`, `step_index`, `branch_index`, `agent_role`) and their MVP-default discipline are PRESERVED VERBATIM. The new field is additive and defaulted (`()`), so existing construction sites compose deterministically without modification — the additive-optional discipline of the v1.32 `branch_index` / `agent_role` extension.

---

## §2 — Status

Additive `StepExecutionContext.hitl_placements` field (§25.3), absorbing the FULL-SPEC-pre-authorized R-FS-1 standalone arc `B-HITL-PLACEMENT-PER-STEP-PRODUCER` — the CP-driver producer that surfaces the workflow's declared HITL placements onto the per-step execution context so the runtime wrap-time HITL gates fire in production. Impl-to-cleared-spec on the C-CP-17 §17.3 declaration + runtime §14.8.2 composer contracts; a binding fix in the `tenant_id` / `parent_gate_level` precedent shape.

**No operator gate.** Additive + opt-in; no committed invariant sacrificed; no new contract / ADR / enum / fail-class / hash-recipe / CXA edge / manifest field (the declaration surface already exists). An absent placement → byte-identical pre-arc behavior.

Apply pass: this delta co-published with the runtime spec v1.61 §14.8.2-step-1 reconciliation (the composer read surface `step` → `step_context`) + harness-cp impl (the `StepExecutionContext.hitl_placements` field + the producer wired at all 5 per-step context construction sites) + harness-runtime impl (the composer reads `step_context.hitl_placements`) + by-execution tests (`test_workflow_driver.py` per-topology producer assertions + `test_lifecycle_hitl_gate_composer.py` composer-reads-step_context + negative control) + fork doc + clearance markers + spine-ledger registration, per workspace `CLAUDE.md` §11.4 bundled-absorption.

v1.40 + earlier PRESERVED VERBATIM per delta-only-spec-file convention. The entire C-CP-01 … C-CP-29 body + §5.x + §6.x + §16.5.x + §25.x (except the additive §25.3 field) PRESERVED VERBATIM. IS spec UNCHANGED (no §5.2 hash-recipe / §16.5.4 key change — `StepExecutionContext` is not hashed). CXA v2.20 UNCHANGED (no new typed edge). ADR-F1/F2/F3/D1–D6 UNCHANGED. ADD v1.3 + PRD v1.1 UNCHANGED.

Clearance marker filed at `.harness/clearance/Spec_Control_Plane-v1_41-cleared-2026-06-18.md`.

2026-06-18.
