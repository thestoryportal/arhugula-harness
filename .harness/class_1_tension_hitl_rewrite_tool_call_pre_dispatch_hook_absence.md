# Class 1 Tension — HITL `rewrite_tool_call` pre-dispatch hook firing-site absence

| Field | Value |
|---|---|
| Status | PROPOSING |
| Filed | 2026-05-29 |
| Filed by | Operator + Claude (post-PR-#63 close, design-phase posture) |
| Class | 1 (architectural; firing-site-absence at LANDED substrate; same structural shape as U-CP-34 v2.37 AC #11 — sibling to `[[class_1_tension_sibling_ledger_child_agent_recursion_boundary]]` co-published this arc) |
| Triggers | Upstream blocker (5) for H_T-RT-35 RETIRE-READY per checkpoint 2026-05-29; U-RT-111 v2.39 AC #4 STRIKE refinement empirical anchor at PR #62 merged `ac802a6` |
| Halt scope | None at execution-time (composer LANDED + bound at `ctx.hitl_registry`; ZERO production reads); back-flow scope for design-phase decision on insertion-point |

---

## §1 Finding

`RuntimeHITLPlacementRegistry.rewrite_tool_call(proposed_action, persona_tier)` at `harness-runtime/src/harness_runtime/lifecycle/hitl_placement.py:187` is a concrete production implementation that composes `harness_cp.hitl_as_tool_call_rewriting.rewrite_tool_call_to_hitl(...)` per C-CP-17 §17.2. The registry is bound to `ctx.hitl_registry` at `harness-runtime/src/harness_runtime/bootstrap/stage_3b_cp_routing.py:57` and is reachable from every production lifecycle stage. 6 test callers exercise the method; ZERO production callers anywhere in `harness-*/src/`.

Downstream, `emit_hitl_tool_call_rewriting_state_ledger_entry` (CP composer at `harness-cp/src/harness_cp/hitl_as_tool_call_rewriting.py:249-291`) is also LANDED, takes `semantic_variant_binding_id: str` derived per Reading B from `rewritten_call.variant.value` (catalogued at Project Workflow v1.13 §1.1 species-2 sub-species). Its firing-site is gated on the upstream `rewrite_tool_call` firing-site.

The pre-tool-dispatch interception loop where LLM-produced tool calls would be intercepted, classified, and conditionally rewritten to HITL gates does NOT exist at MVP. `RuntimeToolDispatcher.dispatch(binding, step, *, step_context)` at `runtime_tool_dispatcher.py:385` operates on `WorkflowStep` (step-level pre-declared `tool_id + tool_args` from manifest payload), NOT on LLM-produced `ProposedAction` from inference output. `RuntimeLLMDispatcher.dispatch(...)` at `llm_dispatch.py:289` is single-shot provider-agnostic chat completion + cost attribution; it does NOT loop on LLM-emitted tool calls.

---

## §2 Empirical orientation (HEAD `9ddb9ba`)

| Surface | Path | State |
|---|---|---|
| `RuntimeHITLPlacementRegistry.rewrite_tool_call` | `harness-runtime/src/harness_runtime/lifecycle/hitl_placement.py:187` | LANDED concrete impl |
| Composer `rewrite_tool_call_to_hitl` | `harness-cp/src/harness_cp/hitl_as_tool_call_rewriting.py:156` | LANDED |
| `emit_hitl_tool_call_rewriting_state_ledger_entry` | `harness-cp/.../hitl_as_tool_call_rewriting.py:249-291` | LANDED (U-CP-77) |
| U-RT-110 wiring `emit_hitl_tool_call_rewriting_state_ledger_entry` | `harness-runtime/src/harness_runtime/lifecycle/cp_is_wiring.py:265,286` | LANDED |
| `ctx.hitl_registry` binding | `harness-runtime/src/harness_runtime/bootstrap/stage_3b_cp_routing.py:57` | LANDED |
| Production callers of `ctx.hitl_registry.rewrite_tool_call(...)` | (none) | **ABSENT** |
| Production callers of `rewrite_tool_call_to_hitl(...)` directly | (none) | **ABSENT** |
| ProposedAction construction sites | `sub_agent_dispatch.py:322`; `hitl_gate_composer.py:496` | LANDED but neither flows to `rewrite_tool_call` |
| `RuntimeToolDispatcher.dispatch` | operates on `WorkflowStep` (pre-declared `tool_id`), not LLM `ProposedAction` | structurally-distinct surface |
| LLM inner tool-call loop | `RuntimeLLMDispatcher.dispatch` is single-shot completion | **NOT BUILT** at MVP |

---

## §3 Readings

### Reading A — Extend `hitl_gate_composer` to invoke `rewrite_tool_call` before brief construction

Treat HITL gating as the canonical interception point. Extend `RuntimeHITLGateComposer.gate(...)` to invoke `ctx.hitl_registry.rewrite_tool_call(proposed_action, persona_tier)` before constructing the escalation brief. If the rewritten call differs from the proposed, emit the §16.5 ledger entry via `ctx.cp_is_wiring.emit_hitl_tool_call_rewriting_state_ledger_entry(...)`; then proceed with brief construction using the rewritten call.

**Pros:** smallest surface change; reuses existing composer; firing site is at an established HITL flow point.

**Cons:** semantically conflates two distinct contracts (gate composition is post-decision-to-HITL; rewrite is the decision-to-HITL itself); rewrite_tool_call's natural surface is BEFORE the harness decides to invoke a HITL gate at all (the rewrite decides whether HITL applies). Risks coupling at the wrong layer.

### Reading B — NEW pre-dispatch-hook stage at runtime spec §1 BootstrapStage

Author a new `materialize_tool_call_interceptor_stage` at stage 5 (LOOP_INIT). Bind a `ToolCallInterceptorHook` Protocol surface (mirror pattern from `SkillActivationHook` at runtime spec v1.32 §14.17 + `ValidatorPostEvaluateHook` at CP spec v1.24 §28.10). Hook fires at the LLM-tool-call boundary (does not yet exist) OR at step-level pre-dispatch (extending `RuntimeStepDispatcher` semantics).

**Pros:** clean architectural surface; matches established hook-Protocol pattern; operator-opt-in RETIRE-READY (mirror CP-18 / CP-21 / RT-94 precedent).

**Cons:** introduces NEW Protocol + NEW spec section + NEW factory + NEW HarnessContext field (largest surface); requires runtime spec amendment (X-AL-3 silent-absorption guard applies — needs back-flow); the natural firing-site (LLM inner tool-call loop) is itself NOT BUILT at MVP, so the hook would have no callsite even after authoring.

### Reading C — Invoke at `RuntimeStepDispatcher` per-step pre-dispatch hook

Add a pre-dispatch hook within the existing step dispatcher: before `step_dispatchers.lookup(step.step_kind).dispatch(...)` at `workflow_driver.py:893`, project `WorkflowStep` to `ProposedAction` and invoke `ctx.hitl_registry.rewrite_tool_call(...)`. If rewrite applies, route through HITL flow.

**Pros:** firing-site lives at an established control-flow point; touches workflow_driver narrowly.

**Cons:** step-level rewriting is awkward — `WorkflowStep` is pre-declared in manifest; rewriting at step level second-guesses operator-authored step kinds; rewrite_tool_call's design intent is LLM-emitted tool calls (dynamic), not manifest-declared steps (static). Semantic mismatch.

### Reading D — Bounded-defer per X-AL-2; structurally-unfireable-at-MVP

Acknowledge that `rewrite_tool_call` is structurally unfireable at the current MVP boundary because the LLM inner tool-call interception loop does NOT exist. Defer the firing-site arc until the inner-loop arc is authored. Maintain U-RT-111 AC #4 STRIKE on the firing-site-absence reason (already preserved at v2.39 per `[[2.strike-revision-on-refined-second-tier-reason]]`).

**Pros:** preserves architectural coherence; avoids premature firing-site decision that may be reversed by inner-loop arc design; matches v2.37 U-CP-34 STRIKE precedent (declared structurally-unfireable, no premature wiring).

**Cons:** does not advance H_T-RT-35 toward RETIRE-READY at this arc; carries one of the 5 upstream blockers without closure.

---

## §4 Q-set for operator ratification

| Q | Decision space |
|---|---|
| Q1 | Reading: A (hitl_gate extension) / B (NEW pre-dispatch hook stage) / C (StepDispatcher hook) / D (bounded-defer) |
| Q2 (if A) | Scope: (i) HITL gate ONLY invokes rewrite check; (ii) HITL gate invokes rewrite AND emits §16.5 ledger from gate site; (iii) HITL gate invokes rewrite AND delegates ledger emission to a separate post-rewrite hook |
| Q3 (if B) | Hook Protocol: (i) NEW `ToolCallInterceptorHook` with `pre_dispatch(proposed_action, persona_tier) -> ProposedAction \| None` (None = no rewrite); (ii) reuse existing `SkillActivationHook` pattern at runtime spec v1.32 §14.17 verbatim |
| Q4 (if B) | Firing site: (i) wait for LLM inner-loop arc (no callsite at this arc; hook surface only); (ii) wire at step-level pre-dispatch (semantic mismatch flagged); (iii) wire at hitl_gate_composer + step-level (dual surface) |
| Q5 (any) | Cross-axis cascade: (α) no spec change; (β) CP spec §17.2 clarification on consumer-side firing-site; (γ) runtime spec §14.X NEW C-RT-NN binding contract |

---

## §5 Cross-axis cascade analysis

| Axis | Touch |
|---|---|
| IS | NONE (composer + ledger writer + cp_is_wiring all LANDED; this arc decides firing-site only) |
| AS | NONE |
| CP | spec §17.2 OR §C-CP-17 may need consumer-side firing-site clarification (Reading B Q5=β); no contract change at MVP |
| OD | NONE (cost-attribution + audit-ledger receive emission downstream; firing-site is upstream of OD) |
| CXA | NONE (no new typed edge; existing U-CP-77 → U-RT-110 → U-RT-111 chain unchanged) |
| Runtime spec | Reading B requires NEW §14.X C-RT-NN + NEW field at C-RT-04 + NEW fail class (largest surface). Reading A + C are intra-composer / intra-driver respectively (no spec change). Reading D no change. |

---

## §6 Recommendation

**Pre-substantive recommendation:** Reading D (bounded-defer) is the structurally-coherent disposition at MVP scope. The LLM inner tool-call interception loop does NOT exist; authoring a firing-site for `rewrite_tool_call` before the inner-loop arc risks the same pattern as v2.37 U-CP-34 (premature wiring against not-yet-built downstream substrate). The U-RT-111 AC #4 STRIKE is already preserved at v2.39 per `[[2.strike-revision-on-refined-second-tier-reason]]`; bounded-defer maintains catalogue coherence without forcing premature architecture.

If operator prefers immediate closure: Reading B (NEW pre-dispatch hook stage) is cleanest architecturally but requires runtime spec amendment (X-AL-3 back-flow) AND has no natural callsite at MVP (would land hook-Protocol without firing). Reading A (hitl_gate extension) is the lowest-surface ratification path but conflates rewrite-decision and gate-composition contracts at the wrong layer.

Reading C is NOT recommended — semantic mismatch with `rewrite_tool_call`'s LLM-dynamic-tool-call design intent.

---

## §7 Status posture

| Element | Status |
|---|---|
| Composer LANDED | ✅ |
| Wiring LANDED | ✅ |
| Production callsite | ❌ ABSENT |
| LLM inner tool-call loop substrate | ❌ NOT BUILT at MVP |
| H_T-RT-35 RETIRE-READY transit | GATED on this arc + 4 sibling upstream arcs |
| Recommended Q1 | (D) bounded-defer unless operator prefers immediate closure |
| Sibling arc | `[[class_1_tension_sibling_ledger_child_agent_recursion_boundary]]` co-published this arc (DISTINCT structural shape per advisor 44th application) |

---

*End of fork doc.*
