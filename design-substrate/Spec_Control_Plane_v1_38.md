# Spec: Control Plane — v1.38 (delta over v1.37)

---

## Change-note (v1.37 → v1.38)

**Scope of revision.** A single additive field on the **C-CP-06 §6.1 `StepOverride`** per-step override record — NEW **`agent_role: AgentRole | None = None`** — plus its propagation through **§6.2** (`StepEffectiveBinding.agent_role` + `resolve_step_binding` field-by-field application) and the **§6.6 provenance-scope** sub-section extended to cover the role dimension. This is the **R-FS-1 arc B4 Slice 4** leg (per-step role override + linear-path role indexing): an operator annotates a specific workflow step with an `AgentRole`, and the CP driver folds that role onto the step's single `StepExecutionContext.agent_role` source — taking precedence over the B1 fan-out-derived role (`derive_agent_role(step_id)`, Slice 2) on a non-linear branch, or supplying a role at all on the `SINGLE_THREADED_LINEAR` path (which carries none today). Design authority: `.harness/class_1_fork_b4_per_step_role_override_stepoverride_extension.md` (filed + resolved this arc) + R-FS-1 arc-B4 grounding sweep. The per-step **model** (v1.6) and **prompt** (v1.37, Slice 3) overrides already exist; per-step **role** is the Slice-4 increment — the one Slice 3 explicitly foreclosed as "the distinct Slice-4 gate."

**Why a spec amendment (the X-AL-3 fork).** Extending the cleared `StepOverride` schema is governed by the **v1.27 §2(d) "X-AL-3 explicit-extension discipline"** — the canonical-long-term path for `StepOverride` / `WorkflowManifestEntry` field growth, with **mirror precedents v1.20 `default_gate_level` + v1.22 `tenant_id` + v1.34 webhook-ctor binding-lift + v1.37 `prompt_version_sha` arcs**. The field add is owed an explicit §6.1 amendment, not impl-discretion. Under the standing FULL-SPEC directive (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`, 2026-06-12) the design back-flow is **pre-authorized**, authored here as this delta + the paired fork doc + clearance + bundled-absorption impl.

**This delta DOES carry an operator gate — the §14.5.3 committed-invariant relaxation (UNLIKE v1.37).** Slice 3 (per-step prompt) sacrificed no committed invariant (prompt has multiple sources by design). Per-step **role** is categorically different: the runtime spec **§14.5.3** (the B1↔B4 role seam, cleared at v1.48) declares an explicit, role-specific committed invariant — **invariant 2 "Single role source": "The branch role flows only via `step_context.agent_role` … never a second per-step role carrier — one source of truth (the `StepExecutionContext`)"** — and **invariant 3 "Linear path untouched."** `StepOverride.agent_role` is literally **a second per-step role carrier** (a new role *origin* in the manifest), exactly what invariant 2 forecloses; and folding it onto the linear path's `step_context.agent_role` touches the path invariant 3 protects. Relaxing a committed invariant is the **operator's call** even when the mechanism is clean — FULL-SPEC pre-authorizes the *build* and the *back-flow*, not silently relaxing a committed invariant. **The CP-side field add (this §6.1/§6.2/§6.6 delta) is additive and bundled-absorbed like v1.37; the committed-invariant relaxation lives in the paired runtime spec §14.5.3 amendment (v1.52) and is what the operator ratifies before merge.** This delta is authored against that ratification; it is not canonical until the paired runtime amendment is cleared.

**Mechanism — Option B, composition-time fold (single dispatch-read role source PRESERVED).** Two readings were available: (A) read a second role source `binding.agent_role` at the **dispatch** seam (alongside `step_context.agent_role`), and (B) fold `binding.agent_role` onto the single `StepExecutionContext.agent_role` source at **CP-driver composition**, leaving the dispatch read unchanged. **Option B is adopted.** Reading A would create the same **two-authorities-at-dispatch** anti-pattern the runtime already warns against for the per-role *model* (the C-RT-16 wrapper owns model-candidate selection by reading `step_context.agent_role`; a second inner role-read would defeat fallback for role-routed branches) — and would require BOTH the wrapper (model) and inner (prompt) to grow a second role-read. Under Option B the CP driver composes `step_context.agent_role` with precedence **per-step `binding.agent_role` > fan-out-derived `derive_agent_role(step_id)` > linear-path default (None → runtime `_MVP_DEFAULT_AGENT_ROLE`)**, and the unchanged dispatch read (`step_context.agent_role`) feeds BOTH the wrapper (model) and the inner (prompt + attribution) from one source. **Zero runtime dispatch code change.** This is the same structural template as `default_gate_level → StepExecutionContext.parent_gate_level` (v1.20, `resolve_parent_gate_level`). The relaxation is therefore **composition-time only**: the dispatch still reads one role source of truth (the `StepExecutionContext`); what is relaxed is invariant 2's narrower clause ("no second per-step role *carrier*") + invariant 3 ("linear path untouched", now conditional). Invariant 1 (non-breaking default) is **fully preserved**: an absent override leaves the composed role unchanged → byte-identical to v1.37.

**Provenance scope — the WIRED per-step override state-ledger entry, NOT the run-level §5.2 hash (no IS-spec change).** Identical to the v1.37 per-step prompt reasoning. The per-step role is a per-workflow `WorkflowManifestEntry.per_step_overrides` datum, not on the runtime `HarnessContext` the §5.2 resolver reads. Because `agent_role` is a `StepEffectiveBinding` field, it is automatically captured at the already-WIRED per-step override state-ledger entry (`emit_override_state_ledger_entry` at `workflow_driver.py`, gated on `binding.override_applied`), whose idempotency_key hashes `post_override_step_config = binding.model_dump(mode="json")`: a per-step role flip ⟹ different `binding.model_dump` ⟹ a distinct hash-chained ledger entry. This follows the per-step **model** + **prompt** override provenance precedent — never the §5.2 hash. The per-**role** *catalog* (run-level `per_role_bindings`) remains hashed at §5.2 v1.9 (`routing_manifest_sha` / `prompt_selection_manifest_sha`); a per-**step** *override* is a different scope, recorded one layer down. The two scopes compose — they do not collide; no C-IS-05 §5.2 recipe change is owed.

**Linear-path role indexing (the §14.5.3 invariant-3 half) is IN scope.** Threading a role onto the `SINGLE_THREADED_LINEAR` (and evaluator-optimizer generate/evaluate) step contexts — which carry no derived role today — is the invariant-3 relaxation. Under Option B it is **near-free**: the linear per-step composition site sets `agent_role = binding.agent_role` (None when no override → unchanged). It is bundled into the **same** operator gate as the per-step-role carrier (invariant 2), not split — both are facets of the one "per-step role override" capability and the one §14.5.3 relaxation.

**No new contract ID; no new ADR; no enum change; no new fail class; no six-field / §5.2-hash / §16.5 idempotency-formula change.** `agent_role` is an additive optional field on the existing **C-CP-06** contract, reusing the committed `AgentRole` shared type (C-CP-00c, v2.8). The per-step override evaluator with field-by-field application is committed at C-CP-06 §6.2; v1.38 adds the role dimension to it. The §16.5.4 row U-CP-14 idempotency-key formula is **PRESERVED VERBATIM** (the role rides `post_override_step_config`'s outcome-hash, not the key formula). No new runtime fail class (the role read is unchanged; an unbound role falls through to default per the §14.5.3 lookup-miss policy).

**v1.37 + prior body PRESERVED VERBATIM.** All v1.37 content — §6.6 (per-step prompt provenance) + §2.5 + §19.1.2 + §27.8 + §7.4 + §25.10–§25.18 + §29 + the entire C-CP-01 … C-CP-29 body — is PRESERVED VERBATIM per the delta-only-spec-file convention. Within C-CP-06: §6.3 / §6.4 / §6.5 / §16.5.x are **PRESERVED VERBATIM**; the **only** changes are the additive field at §6.1, its propagation at §6.2, and the §6.6 extension below.

---

## §1 — Amended §6.1 `StepOverride` schema (ADDS `agent_role`)

The `StepOverride` record at C-CP-06 §6.1 gains one additive optional field. The v1.37 field set (`step_id`, `model_binding`, `engine_class`, `hitl_placement`, `prompt_version_sha`) is PRESERVED VERBATIM; `agent_role` joins per the v1.27 §2(d) explicit-extension discipline:

```
StepOverride {
    step_id            : StepID
    model_binding      : ModelBinding  | None = None
    engine_class       : EngineClass   | None = None
    hitl_placement     : HITLPlacement | None = None
    prompt_version_sha : str | None = None        // v1.37 — per-step prompt override (B4 Slice 3)
    agent_role         : AgentRole | None = None   // NEW v1.38 — per-step role override (B4 Slice 4)
}
```

`agent_role` (when not `None`) is the operator-assigned `AgentRole` for **this step**, folded by the CP driver onto the step's `StepExecutionContext.agent_role` source — overriding the B1 fan-out-derived role on a non-linear branch (precedence **per-step > derived**), or supplying a role on the `SINGLE_THREADED_LINEAR` path (which carries none today). `None` (the default) preserves v1.37 behavior verbatim — the step inherits the fan-out-derived role or the linear-path default. `extra="forbid"` + `frozen=True` are unchanged. The field reuses the committed `AgentRole` shared type (open-string newtype, C-CP-00c) and is symmetric with the existing per-step `model_binding`/`prompt_version_sha`.

## §2 — Amended §6.2 per-step override evaluator (propagation)

`StepEffectiveBinding` (C-CP-06 §6.2) gains the matching effective field; `resolve_step_binding` applies the override field-by-field per the existing §6.2 discipline:

```
StepEffectiveBinding {
    ... (v1.37 fields PRESERVED VERBATIM: step_id, model_binding, engine_class,
         hitl_placement, override_applied, override_audit_ref, persona_tier,
         prompt_version_sha)
    agent_role : AgentRole | None = None   // NEW v1.38 — the resolved per-step role (override value, else None)
}
```

`resolve_step_binding` sets `agent_role = override.agent_role` when an override is present for the step (else `None`). Like `prompt_version_sha`, this is **`None`-or-override**: there is no manifest-entry-level role default to fall back to at the CP layer (the fan-out-derived role + linear-path default are resolved downstream at CP-driver branch/step composition). A `None` here means "no per-step role override" → the driver composes the fan-out-derived role (non-linear) or leaves `step_context.agent_role` unset (linear → runtime `_MVP_DEFAULT_AGENT_ROLE`). The field-by-field-no-field-set-substitution discipline (§6.2) is unchanged.

**Driver composition (the Option-B fold; impl-discretion mechanism per §14.5.3).** The CP `execute_workflow` driver folds `binding.agent_role` onto the single `StepExecutionContext.agent_role` source at the per-step / per-branch composition sites, with precedence **per-step > fan-out-derived > default**:

- `SINGLE_THREADED_LINEAR` + evaluator-optimizer step contexts: `agent_role = binding.agent_role` (no derived role on these paths; None ⟹ unchanged).
- `ORCHESTRATOR_WORKERS` / `HIERARCHICAL_DELEGATION` / `DECENTRALIZED_HANDOFF` worker/stage contexts: `agent_role = binding.agent_role or derive_agent_role(step_id)`.
- `PARALLELIZATION` branch contexts: `agent_role = binding.agent_role or` the single parallelization-worker default.
- The orchestrator's own context + the decentralized handoff-record `next_role` preview honor the per-step override too (so the audit record matches the role the next stage will fold in).

The runtime **dispatch read is unchanged** (`step_context.agent_role` feeds the C-RT-16 wrapper for model + the C-RT-15 inner for prompt/attribution) — single dispatch-read role source of truth preserved (Option B).

## §3 — §6.6 Per-step override provenance scope (EXTENDED to the role dimension)

The §6.6 provenance reasoning (v1.37, per-step prompt) extends verbatim to the role dimension: the per-step role override's provenance is the **per-step override state-ledger entry** (`emit_override_state_ledger_entry`), **not** the run-level C-IS-05 §5.2 procedural-tier hash. Because `agent_role` is a `StepEffectiveBinding` field, a per-step role change is captured in `post_override_step_config = binding.model_dump(...)` → the §16.5.4 row U-CP-14 idempotency-key's outcome-hash → a distinct hash-chained ledger entry whose `procedural_tier_snapshot_ref` pins the run-level procedural base and whose outcome-hash pins the step-level role delta. The run-level per-**role** catalog stays hashed at §5.2 v1.9 (`routing_manifest_sha` / `prompt_selection_manifest_sha`); the per-**step** override is recorded at the override ledger entry. The two scopes compose; no C-IS-05 §5.2 recipe change is owed for the per-step role dimension.

---

## §4 — Status

Additive C-CP-06 §6.1 field (`agent_role`) + §6.2 propagation + §6.6 provenance extension, absorbing the operator-pre-authorized (FULL-SPEC directive) R-FS-1 B4 Slice 4 per-step role override + linear-path role indexing. Per the v1.27 §2(d) X-AL-3 explicit-extension discipline (mirror precedents v1.20/v1.22/v1.34/v1.37).

**Operator gate — the paired runtime §14.5.3 committed-invariant relaxation (UNLIKE v1.37).** This CP §6.1/§6.2/§6.6 delta is additive and bundled-absorbed; the **committed-invariant relaxation** (§14.5.3 invariant 2 "single role source" + invariant 3 "linear path untouched", relaxed at **composition-time** via Option B) lives in the paired **`Spec_Harness_Runtime_v1.md` §14.5.3 amendment (v1.52)** and is what the operator **ratifies before merge**. This delta is authored against that ratification — not canonical until the paired runtime amendment + this delta are jointly cleared.

Apply pass: this delta co-published with harness-cp impl (`StepOverride` + `StepEffectiveBinding` + `resolve_step_binding` + the driver Option-B fold across all 6 topology paths) + tests (CP unit + linear-path by-execution + fan-out override-replaces-derived by-execution) + fork doc + clearance markers (CP v1.38 + runtime v1.52) + spine-ledger registration, per workspace `CLAUDE.md` §11.4 bundled-absorption.

v1.37 + v1.36 + earlier PRESERVED VERBATIM per delta-only-spec-file convention. C-CP-06 §6.3/§6.4/§6.5 + §16.5.x + the entire C-CP-01 … C-CP-29 body PRESERVED VERBATIM. CXA UNCHANGED (intra-CP-axis fold + the unchanged runtime-mediated dispatch read; no new typed cross-axis edge). IS spec UNCHANGED (provenance at the per-step override ledger entry; §5.2 recipe unchanged). ADR-F1/F2/F3/D1–D6 UNCHANGED (the `AgentRole` shared type + the 6-class topology enum are reused, not changed). ADD v1.3 + PRD v1.1 UNCHANGED.

Clearance markers filed at `.harness/clearance/Spec_Control_Plane-v1_38-cleared-2026-06-17.md` + `.harness/clearance/Spec_Harness_Runtime-v1_52-cleared-2026-06-17.md`.

2026-06-17.
