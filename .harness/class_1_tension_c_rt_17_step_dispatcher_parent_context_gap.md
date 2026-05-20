# Class 1 Tension Record — C-RT-17 StepDispatcher Protocol lacks per-step parent context surface

**Filed:** 2026-05-20 (during U-RT-59 spec authoring + implementation pre-survey arc)
**Class:** 1 (halt-execution; design-phase artifact requires revision)
**Status:** RESOLVED-STAGE-1 — Protocol-surface gap closed; Stage 2 (U-RT-59 implementation per L9-ter ACs) owed next session. Stage 1 plumbing landed 2026-05-20 same arc. CP spec v1.6 §25.2.1 declares `StepDispatcher` Protocol + `StepExecutionContext` 8-field schema; runtime spec v1.6 §14.7 narrative cites `step_context.X` (HALT marker dropped); CP-side `StepExecutionContext` Pydantic v2 type at `harness-cp/src/harness_cp/workflow_driver_types.py`; `StepDispatcher` Protocol amended at `harness-cp/src/harness_cp/workflow_driver.py:151` with keyword-only `step_context` parameter; `execute_workflow` driver loop composes per step from 4 deterministic-source fields + 4 MVP-default-bounded fields; `RetryBreakerFallbackDispatcher` + `RuntimeLLMDispatcher` accept via Protocol conformance (neither consumes at v1.6). 2231 tests green at Stage 1 landing. Stage 2 (U-RT-59 implementation per L9-ter ACs) owed next session.
**Surfaced by:** `phase-7-implementation` skill pre-implementation survey + advisor cross-check against code-side `StepEffectiveBinding` field surface

---

## 1. The defect

`Spec_Harness_Runtime_v1.md` v1.6 §14.7 C-RT-17 specifies the sub-agent dispatch composer surface. The composer body per §14.7.2 step 2 (HandoffContext composition) + step 3 (gate-level descent invocation) + step 8 (audit-entry composition) requires per-step parent context fields:

- `parent_action_id` (passed to `RuntimeHandoffRegistry.dispatch(parent_action_id=..., ...)` per C-CP-12 + to `compose_dispatch_audit(parent_action_id=..., ...)`)
- `parent_gate_level` (passed to `RuntimeHandoffRegistry.dispatch(parent_gate_level=..., ...)` per C-CP-12)
- `parent_sandbox_tier` (passed to `RuntimeHandoffRegistry.dispatch(parent_sandbox_tier=..., ...)` per C-CP-12)
- `parent_actor` (used in `LedgerEntryRef(actor=...)` composition per C-CP-13 §13.5)
- `parent_entry_hash` (used in `LedgerEntryRef(entry_hash=...)` composition per C-CP-13 §13.5)
- `parent_idempotency_key` (used in `StateSummary(idempotency_key=...)` composition per C-CP-13 §13.4)
- `tenant_id` (passed to `RuntimeAuditLedgerWriter.append(tenant_id=..., audit_entry=...)` per U-RT-32)

The v1.6 spec narrative assumed these would be accessible via the `binding: StepEffectiveBinding` parameter that the `StepDispatcher` Protocol passes to the dispatcher. **They are not.**

### Code-side reality (verified 2026-05-20)

`harness-cp/src/harness_cp/per_step_override_evaluator.py`:

```python
class StepEffectiveBinding(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    step_id: str
    model_binding: ModelBinding
    engine_class: EngineClass
    hitl_placement: HITLPlacement | None = None
    override_applied: bool
    override_audit_ref: LedgerEntryRef | None = None
```

`harness-cp/src/harness_cp/workflow_driver.py:151`:

```python
@runtime_checkable
class StepDispatcher(Protocol):
    def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
    ) -> Mapping[str, Any]:
        ...
```

**None of the required parent context fields exist on `StepEffectiveBinding`**, and the `StepDispatcher` Protocol surfaces no other per-call mechanism for the dispatcher to receive them.

### Driver loop surfaces (verified 2026-05-20)

`harness-cp/src/harness_cp/workflow_driver.py:execute_workflow` tracks per-step state internally:

- `run_id` — the harness-unique run identifier (parameter; carried for the workflow lifetime)
- `step_index` — the per-iteration loop variable
- `manifest_entry` — workflow manifest (carries `engine_class`, `workload_class`, per-step overrides, fallback chain; does NOT carry parent gate_level / sandbox_tier as runtime values — those are derived per-step or per-axis-binding)
- `accumulated` — running step output dictionary
- `binding` — re-computed per step via `resolve_step_binding(manifest_entry, step_id, default_model_binding=...)`

The driver does NOT compute or surface `parent_action_id` per step (the per-step action_id derives from `run_id + step_index + workflow_id` per C-IS-10 §10.2 + C-CP-25 §25.3.2 conventions but the composition is not done in the driver loop — it would be done at the per-step ledger-entry composition site, which is the dispatcher's job).

The driver does NOT compute or surface `parent_gate_level` / `parent_sandbox_tier` per step (these are AS-axis-bound concepts; the driver is engine-agnostic).

### Existing pattern: handoff_registry.dispatch caller convention

The existing `RuntimeHandoffRegistry.dispatch(...)` per `harness-runtime/src/harness_runtime/lifecycle/handoff.py` accepts these fields as **explicit kwargs** from the caller. The existing tests + the CP→IS wiring callback at `cp_is_wiring.py:200-250` also accept `parent_action_id` as an explicit kwarg from above (the runtime composition layer supplies them, not the driver).

Consistent with the existing pattern: **the dispatcher caller supplies these as kwargs.** The question is HOW the dispatcher gets them from the driver loop.

---

## 2. Cross-cutting impact

Per X-AL-3 (Meta-Architecture §7.7): no silent H_T design extension at Phase 7 execution. The v1.6 §14.7 narrative as written assumed `binding.parent_action_id` etc. exist, which they do not. Implementing against that assumption silently extends `StepEffectiveBinding` (Class-1 extension to CP-axis canonical type) OR silently introduces a side-channel (`ContextVar`, current-span introspection) without spec authorization.

This contaminates retirement criteria for three CP-axis substitutions:

- **H_T-CP-10 RETIRE-READY criterion**: "topology dispatcher operational at production execution path" — production execution path requires the dispatcher to be invoked from a driver step. If the driver can't surface parent context, the dispatcher can't compute the C-CP-10 §10.3 admissibility predicate against the parent's workload_class (which it needs to know about).
- **H_T-CP-13 RETIRE-READY criterion**: "HandoffContext typed schemas enforced at production callsite" — production callsite is the composer body §14.7.2 step 2. If the composer can't access parent context, it can't compose HandoffContext.
- **H_T-CP-14 RETIRE-READY criterion**: "subagent.* + topology.* namespaces emitted at production span hierarchy" — emission depends on the composer running, which depends on parent context access.

Per workspace `CLAUDE.md` §4.3: **silent absorption of design-phase defects is the worst failure mode.** Halting now is cheaper than three retirements downstream + a CP-axis-canonical-type silent extension.

---

## 3. Routing options (4-path candidate set)

### Path A — Extend StepDispatcher Protocol with per-call StepExecutionContext (recommended)

1. Amend `Spec_Control_Plane_v1_5.md` §25.2 (or v1.6 amendment): driver signature extended to surface per-step parent context to the dispatcher.
2. New CP-side type at `harness-cp/src/harness_cp/workflow_driver_types.py`:
   ```python
   class StepExecutionContext(BaseModel):
       model_config = ConfigDict(extra="forbid", frozen=True)
       parent_action_id: str
       parent_gate_level: GateLevel
       parent_sandbox_tier: SandboxTier
       parent_actor: ActorIdentity
       parent_entry_hash: str
       parent_idempotency_key: str
       tenant_id: str | None
       step_index: int
   ```
3. Amend `StepDispatcher` Protocol at `harness-cp/src/harness_cp/workflow_driver.py:151`:
   ```python
   class StepDispatcher(Protocol):
       def dispatch(
           self,
           binding: StepEffectiveBinding,
           step: WorkflowStep,
           *,
           step_context: StepExecutionContext,
       ) -> Mapping[str, Any]:
           ...
   ```
4. Amend `execute_workflow()` per-step iteration: compose `StepExecutionContext` from driver-tracked state per step; pass to dispatcher.
5. Amend U-RT-58 `RetryBreakerFallbackDispatcher` to accept the new param (pass-through to inner C-RT-15 dispatcher; the LLM dispatcher doesn't need parent context at v1.6).
6. Amend C-RT-17 §14.7 narrative to read parent context from `step_context` instead of `binding`.

**Pros:** Cleanest architecturally; explicit per-call parameter; type-safe; consistent with the existing `RuntimeHandoffRegistry.dispatch(...)` kwargs convention; preserves "step body opaque to driver" invariant (`StepExecutionContext` is driver-composed metadata, not body content); allows future dispatchers (HITL, tool-invocation, validator) to consume per-step parent context as needed.

**Cons:** Cross-axis amendment (CP-side type + Protocol + driver + U-RT-58 wrapper signature + C-RT-17 spec); ~4 file edits. Modest plumbing burden but precedent exists (the U-RT-58 wrapper signature accepts CP-Protocol-shape via duck-typing).

**Effort:** Moderate. CP spec v1.5 → v1.6 amendment (1 contract addition); CP-side type + Protocol amendment; runtime spec v1.6 amendment (§14.7 updates); driver loop amendment (~10 lines); U-RT-58 wrapper signature pass-through (~5 lines).

### Path B — ContextVar-based implicit propagation

1. New runtime-internal `ContextVar[StepExecutionContext]` defined at runtime layer.
2. `execute_workflow()` per-step iteration sets the ContextVar before `step_dispatcher.dispatch(binding, step)` invocation; unsets after.
3. `RuntimeSubAgentDispatcher` reads parent context from `ctx_var.get()` at body entry.
4. C-RT-17 §14.7 narrative reads parent context from the ContextVar.

**Pros:** No Protocol change; no driver signature change; no cross-axis amendment to `StepDispatcher` Protocol; minimal plumbing.

**Cons:** Implicit propagation is hard to reason about; ContextVar lifecycle bugs are subtle; breaks per-dispatcher composability (a wrapper that runs the inner dispatcher in a different async context loses the ContextVar); violates least-surprise (the dispatcher's input surface looks complete but actually has a hidden dependency); test fixtures become harder (must set ContextVar before invocation). The CP spec C-CP-25 §25.3.3.4 "step body opaque to driver" invariant is preserved syntactically but violated in spirit (the dispatcher reads driver-private state via side channel).

**Effort:** Low. ~20-line runtime addition.

### Path C — Composite source: OTel span + ledger writer + manifest

1. `RuntimeSubAgentDispatcher` derives parent context from a composite of sources at body entry:
   - `parent_action_id` from OTel current span's attributes (driver's `step.boundary` span attached `idempotency_key` per C-CP-25 §25.3.3.5)
   - `parent_entry_hash` from `ctx.ledger_writer.last_entry_hash()` (new property on `LedgerWriter` — would need to add)
   - `parent_gate_level` / `parent_sandbox_tier` from `manifest_entry.gate_level` / `manifest_entry.sandbox_tier` (if those fields exist; verification owed)
   - `parent_actor` from `ctx.ledger_writer.actor` (already exposed on `LedgerWriter`)
   - `parent_idempotency_key` from current span attribute (driver attaches)
   - `tenant_id` from `ctx.tenant_id` (verification owed: does HarnessContext carry tenant_id?)

**Pros:** No Protocol change; no driver signature change; all sources are already runtime substrate.

**Cons:** Distributed sources of truth; brittle (depends on driver's span attributes being exactly the right shape); requires LedgerWriter API extension (`last_entry_hash` property) which is itself a substrate change; OTel span attribute introspection is non-idiomatic + fragile; doesn't compose well with future dispatchers (each one re-derives parent context independently from disparate sources).

**Effort:** Medium-high. Requires LedgerWriter API extension + OTel span introspection helper + composite derivation logic + significant additional test surface.

### Path D — Step payload carries parent context (rejected at framing)

Operator authors `step.step_payload` to surface parent context.

**Rejected:** parent context is runtime-derived per-execution, not authoring-time-known. `parent_action_id` depends on `run_id` which is supplied at runtime invocation. `parent_entry_hash` depends on the runtime ledger chain state. This path is structurally non-viable.

---

## 4. Recommendation

**Path A.** Clean architectural shape; explicit per-call parameter; consistent with existing `RuntimeHandoffRegistry.dispatch(...)` kwargs convention; preserves the spec-pinned "step body opaque to driver" invariant in both letter and spirit (the new `StepExecutionContext` is driver-composed metadata about the step's execution environment, not step body content); future-proofs for HITL / tool-invocation / validator composer arcs.

Modest plumbing cost (~4 file edits) buys structural clarity and future-arc velocity.

Path B (ContextVar) is the next-best option if Path A's cross-axis amendment is judged too heavy for current cadence. Path C is not recommended (brittle, distributed source-of-truth, harder to test). Path D is not viable.

---

## 5. Routing target

Per workspace `CLAUDE.md` §5.1 + design-substrate-divergence memory:

- **Path A**: in-CLI CP spec v1.5 → v1.6 amendment + in-CLI runtime spec v1.6 amendment (§14.7 fixes) + CP-side type addition + Protocol signature change + driver loop change + U-RT-58 wrapper signature pass-through.
- **Path B**: in-CLI runtime spec v1.6 amendment (§14.7 fixes + new internal ContextVar mechanism documented) only. No CP-axis change.
- **Path C**: in-CLI runtime spec v1.6 amendment + IS LedgerWriter API extension (likely IS spec amendment too) + OD spec verification (tenant_id surface).

---

## 6. Operator decision (2026-05-20)

**RATIFIED — Path A.** Operator ratified Path A 2026-05-20 (this session, via AskUserQuestion at halt-commit time). Path A rationale per operator selection: cleanest architectural shape, type-safe per-call parameter, consistent with the existing `RuntimeHandoffRegistry.dispatch(...)` kwargs convention, preserves the C-CP-25 §25.3.3.4 "step body opaque to driver" invariant in both letter and spirit (the new `StepExecutionContext` is driver-composed metadata about the step's execution environment, not step body content), future-proofs the HITL / tool-invocation / validator composer arcs that will all need per-step parent context.

### Resolution arc (owed; next session)

1. **CP spec amendment** `Spec_Control_Plane_v1_5.md` v1.5 → v1.6: §25.2 Protocol shape extended with new `StepExecutionContext` keyword param; new sub-section §25.2.1 (or equivalent) declaring `StepExecutionContext` 8-field schema.
2. **CP-side type addition** `harness-cp/src/harness_cp/workflow_driver_types.py`: new `StepExecutionContext` Pydantic v2 frozen model with the 8 fields (`parent_action_id`, `parent_gate_level`, `parent_sandbox_tier`, `parent_actor`, `parent_entry_hash`, `parent_idempotency_key`, `tenant_id`, `step_index`).
3. **CP-side Protocol amendment** `harness-cp/src/harness_cp/workflow_driver.py:151`: `StepDispatcher.dispatch` signature gains keyword param `step_context: StepExecutionContext`.
4. **Driver loop amendment** `harness-cp/src/harness_cp/workflow_driver.py:execute_workflow`: per-step iteration composes `StepExecutionContext` from driver-tracked state (`run_id` + `step_index` + `manifest_entry` + per-step idempotency-key derivation + last-emitted ledger entry hash); passes to dispatcher invocation at line 379.
5. **U-RT-58 wrapper pass-through** `harness-runtime/src/harness_runtime/lifecycle/retry_breaker_fallback.py:RetryBreakerFallbackDispatcher.dispatch`: signature accepts new `step_context` keyword + passes through to inner C-RT-15 dispatcher (which does not use it at v1.6 but accepts it via Protocol conformance).
6. **C-RT-15 inner dispatcher** `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:RuntimeLLMDispatcher.dispatch`: signature accepts new `step_context` keyword (unused at v1.6; reserved for future v1.7+ surfaces that may bind step_context to llm.inference span attributes).
7. **Runtime spec amendment** `Spec_Harness_Runtime_v1.md` v1.6 §14.7 fix-up: drop "TBD per fork resolution" markers; replace with concrete `step_context.parent_action_id` / `step_context.parent_gate_level` / etc. references; remove the HALT marker at §14.7 head (or replace with a "RESOLVED at v1.6 — Path A" note); update Status posture in v1.5 → v1.6 change-note.
8. **U-RT-59 plan body amendment**: AC #4 (HandoffContext composition) + AC #5 (gate-descent invocation) updated to reference `step_context` parameter. Drop the L9-ter HALT marker.
9. **U-RT-59 implementation entry**: per `phase-7-implementation` skill discipline; follows the same arc shape as U-RT-58 (impl → tests → retirement events for CP-10/13/14).

Estimated effort: CP spec amendment + Protocol + driver + U-RT-58 pass-through + U-RT-15 pass-through (~30-45 min CC time; 1-2 operator ratifications on amendment specifics if any surfaces). Then U-RT-59 implementation per the plan body ACs.

### X-AL-2 retirement implications (re-state at Path A resolution)

H_T-CP-10 + H_T-CP-13 + H_T-CP-14 (PARTIAL-or-RETIRED) remain candidate retirements at U-RT-59 landing. The Path A resolution does NOT alter the retirement criteria; it only resolves the production-callsite blocking gap so U-RT-59 implementation can satisfy them.

---

## 7. Filing footer

| Field | Value |
|---|---|
| Filed by | `phase-7-implementation` pre-implementation survey + advisor cross-check |
| Filed during | U-RT-59 spec authoring arc (sub-agent dispatch composer; in-CLI spec growth v1.5 → v1.6) |
| Authorities consumed | `Spec_Control_Plane_v1_5.md` §25.2 + §25.3.3.4 (driver signature + step-opaque invariant); `harness-cp/src/harness_cp/per_step_override_evaluator.py` (StepEffectiveBinding field surface); `harness-cp/src/harness_cp/workflow_driver.py:151` (StepDispatcher Protocol); `harness-runtime/src/harness_runtime/lifecycle/handoff.py` (RuntimeHandoffRegistry.dispatch signature); `Phase_7_Meta_Architecture_v1.md` X-AL-3; `Spec_Harness_Runtime_v1.md` v1.6 §14.7 C-RT-17 (the contract whose authoring surfaced the defect) |
| Pattern reference | `.harness/class_1_tension_c_rt_16_retry_attribute_drift.md` (same arc structure — runtime spec authoring surfaced gap at impl pre-survey; halt-and-resolve via operator ratification) |
| Memory pointer | `[[fork-c-rt-17-step-dispatcher-parent-context-gap]]` (to be added to MEMORY.md at filing) |
