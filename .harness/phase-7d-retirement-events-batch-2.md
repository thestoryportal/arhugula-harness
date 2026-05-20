# Phase 7 sub-phase 7d — substitution retirement events, batch 2 (3 retired + 2 PARTIAL)

**Filed:** 2026-05-20, Phase 7 sub-phase 7d, U-RT-52 close arc.
**Skill:** `phase-7-substitution-retirement` §8.1 (workspace progress ledger).
**Authority:** U-RT-52 close arc per `.harness/fork_llm_dispatch_composer_scope.md` (Q1a + Q2a + Q3a + Q4a ratified 2026-05-20) + `.harness/fork_u_rt_52_step_payload_shape.md` (Class 3 resolved 2026-05-20); v2 ledger §9.2.3 §9.2.5 multi-composer gating discharged for the 5 cited primitives by the LLM-dispatch composer landing.

---

## §0 Batch context

**3 substitutions retire + 2 transition to PARTIAL** in this batch. Per X-AL-2 strictness ("partial retirement is non-retirement"), two primitives only partially meet condition B and are recorded as PARTIAL transitions, not retirements:

- **H_T-CP-5** (§3): the LLM-dispatch site is present but the fallback orchestration itself (retry/breaker wrappers) remains Q2a-deferred — fallback chain orchestration is not at runtime.
- **H_T-AS-8** (§5): the 4-attribute `anthropic.cache_*` subset emits at runtime, but the remaining 6 `anthropic.*` attrs (thinking / batch / tokenizer / inference_geo) + entire `mcp.*` namespace remain unemitted.

3 H_T substitutions transition **STILL-BOUNDED** / **PARTIAL** (batch-1) → **RETIRED** (this batch) under condition A ∧ condition B per X-AL-2:

- Condition A (cited unit IDs landed): U-RT-52 landed at U-RT-52 close arc (this commit); cited carriers U-CP-01 / U-CP-02 / U-OD-02 landed at 7b/7c (per `[[phase-7-bootstrap-status]]`).
- Condition B (H_E surface no longer invoked at substitution site): evaluated per substitution against H_T runtime at U-RT-52 close head under runtime-only substitution-site reading. The LLM-dispatch composer at `harness-runtime/.../lifecycle/llm_dispatch.py` is the production LLM call site previously absent; its existence discharges the multi-composer gate for the three cited retirement primitives.

Cumulative retirement count: **12 / 49 (batch 1)** + **3 / 49 (this batch RETIRED)** = **15 / 49 (30.6%)**. Plus 2 PARTIAL transitions (CP-5 + AS-8 — STILL-BOUNDED → PARTIAL under condition-B-not-yet-fully-met).

§9 Class 2 multi-LLM commitment surface: **CLOSED** at U-RT-52 close (per v2 ledger §9.2.3 closure criterion: "the H_T runtime ships ≥1 production LLM call site"). ADR-F1 v1.2 multi-LLM commitment now met at design + library code + runtime.

---

## §1 H_T-CP-1 — Multi-LLM routing core

| Field | Content |
|---|---|
| Substitution ID | H_T-CP-1 |
| Primitive | Multi-LLM routing core (per-step provider dispatch + capability-aware abstraction per ADR-F1 v1.2 + C-CP-01 §1) |
| Spec contract | C-CP-01 + C-RT-15 (new at Runtime spec v1.3) |
| Retirement event timestamp | Phase 7 sub-phase 7d U-RT-52 close arc, 2026-05-20; verified against runtime closure at U-RT-52 close head |
| Condition A verification | Cited carriers U-CP-01 (`routing.*` namespace + ProviderCapabilities) + U-CP-02 (layered routing strategy) landed at 7b (CP 58/58 complete per `[[phase-7-bootstrap-status]]`); new carrier U-RT-52 landed this arc (Runtime spec v1.3 §14.5 C-RT-15 contract + plan body + impl + 13 tests green) |
| Condition B verification | `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:RuntimeLLMDispatcher.dispatch` is the production multi-LLM dispatch site. Provider resolution at `binding.model_binding.provider` (line 226); per-provider branches at lines 257-274 (`_dispatch_anthropic` / `_dispatch_openai` / `_dispatch_ollama`). Substitution mechanism (H_E-direct: `--model` single-LLM CLI flag) no longer invoked at runtime substitution site — runtime dispatches per-step against the operator-supplied `RoutingManifest` provider binding. `--model` is operator-authoring discipline only, not a runtime path |
| Cross-axis dependency cascade | §6.3.1 CP-1 → AS-8 cascade now LIVE: with CP-1 RETIRED and runtime LLM call site emitting `anthropic.*` cache attributes per provider, H_T-AS-8 anthropic.* namespace emission criterion satisfied (this batch §5 below). §6.3.2 OD-2 + CP-24 → CXA-5 cascade partially closes (OD-2 RETIRED this batch §4; CXA-5 still blocked on CP-3 retirement which is deferred per Q2a) |
| Evidence anchor | `llm_dispatch.py` per-provider dispatch + 13-test mock suite at `tests/test_lifecycle_llm_dispatch.py` (all green); v2 ledger §9.2.3 closure criterion satisfied; ADR-F1 v1.2 multi-LLM commitment now met at design + library + runtime |

---

## §2 H_T-CP-2 — Layered routing strategy at runtime

| Field | Content |
|---|---|
| Substitution ID | H_T-CP-2 |
| Primitive | Layered routing strategy (declarative → embedding → LLM-as-router) at runtime — invocation surface per C-CP-02 §2 |
| Spec contract | C-CP-02 + C-RT-15 |
| Retirement event timestamp | Phase 7 sub-phase 7d U-RT-52 close arc, 2026-05-20 |
| Condition A verification | Cited carriers U-CP-02 (layered routing strategy) + U-CP-04 (`RoutingManifest`) landed at 7b; U-RT-52 LLM-dispatch composer landed this arc, providing the runtime invocation surface that consumes the manifest-resolved binding |
| Condition B verification | `harness-cp/src/harness_cp/per_step_override_evaluator.py:resolve_step_binding` returns `StepEffectiveBinding` carrying the layered-strategy-resolved provider+model. `RuntimeLLMDispatcher.dispatch` (line 217) accepts the resolved binding and dispatches against `binding.model_binding.provider`. No H_E layering substitution at runtime: H_E's binary `--model` flag does not carry layered strategy; runtime carries it via typed binding |
| Cross-axis dependency cascade | None at retirement event |
| Evidence anchor | `llm_dispatch.py` Step 1 provider resolution honors the layered binding from `per_step_override_evaluator`; v2 ledger §9.2.3 |

---

## §3 H_T-CP-5 — Fallback chain composition (STILL-BOUNDED → PARTIAL transition, NOT RETIRED)

| Field | Content |
|---|---|
| Substitution ID | H_T-CP-5 |
| Primitive | Fallback chain composition — multi-step chain orchestration with cross-family fallback per C-CP-04 §4 |
| Spec contract | C-CP-04 (orchestration), C-RT-15 (dispatch-site presence only) |
| Transition timestamp | Phase 7 sub-phase 7d U-RT-52 close arc, 2026-05-20 |
| Prior status | STILL-BOUNDED (batch 1) |
| New status | **PARTIAL** (batch 2) |
| What landed | The LLM dispatch site that fallback wrappers will compose around is now present at `RuntimeLLMDispatcher.dispatch`. The async non-retrying composer (per Q2a scope discipline) is the substrate that future retry/breaker wrappers will instantiate around. `FallbackChain` registry materialized at stage 3b (`ctx.fallback_chain`) |
| What remains bounded | The fallback orchestration itself — chain composition over (provider, model) candidates + cross-family fallback selection + breaker integration — does NOT exist at runtime. Per Q2a scope discipline, the wrappers are explicitly out of scope for U-RT-52; they remain bounded on a follow-on CP-3 / CP-4 unit landing |
| X-AL-2 evaluation | Condition A met (U-CP-05 landed); condition B **NOT met** — while H_E's `--fallback-model` substitution is no longer reachable from runtime composers, the H_T primitive (chain composition) is not present at runtime either. Per X-AL-2 "partial retirement is non-retirement", this is recorded as PARTIAL, not RETIRED |
| Cross-axis dependency cascade | §6.3.2 CXA-5 still blocked on full CP-5 retirement (which is itself gated on CP-3 retry/breaker landing, Q2a-deferred). PARTIAL transition does not propagate cascade |
| Evidence anchor | `llm_dispatch.py` async dispatch site + `FallbackChain` registry materialized at stage 3b; v2 ledger §9.2.3 partial-discharge note. Follow-on CP-3 / CP-4 unit will full-retire CP-5 when retry/breaker wrappers land |

---

## §4 H_T-OD-2 — GenAI semconv 1.41.0 attribution at runtime

| Field | Content |
|---|---|
| Substitution ID | H_T-OD-2 |
| Primitive | GenAI semconv 1.41.0 attribution at runtime — `gen_ai.system` + `gen_ai.request.model` + `gen_ai.usage.input_tokens` + `gen_ai.usage.output_tokens` + `gen_ai.response.id` per OD spec C-OD-04..08 |
| Spec contract | C-OD-04..08 + C-RT-06 + C-RT-15 |
| Retirement event timestamp | Phase 7 sub-phase 7d U-RT-52 close arc, 2026-05-20 |
| Condition A verification | Cited carriers U-OD-02 (`gen_ai.*` namespace canonical schema) + U-RT-27 (`materialize_tracer_provider_stage` — TracerProvider materialized at stage 4 OD) all landed; U-RT-52 binds GenAI semconv attributes to the actual LLM call site at this arc landing |
| Condition B verification | `RuntimeLLMDispatcher.dispatch` Step 2 opens `with tracer.start_as_current_span(f"gen_ai.{provider_name}.{operation}")`; Steps 4-5 set `gen_ai.system` / `gen_ai.request.model` / `gen_ai.usage.input_tokens` / `gen_ai.usage.output_tokens` / `gen_ai.response.id` per provider-specific extraction. Tests at `tests/test_lifecycle_llm_dispatch.py::test_genai_span_emits_required_attributes_for_openai` + `test_genai_span_handles_ollama_usage_shape` verify attribute emission across all 3 providers. Substitution mechanism (Authoring + manual: GenAI binding mentioned in spec, no runtime emitter present) no longer applies — the runtime emits GenAI semconv attributes at the LLM call site as required |
| Cross-axis dependency cascade | None at retirement event (OD-2 retirement is the precondition for §5 below — AS-8 anthropic.* namespace emission depends on the GenAI semconv substrate being live at runtime) |
| Evidence anchor | `llm_dispatch.py` Step 2 span + Step 4 attribute set; 2 of 13 tests directly verify span attribute emission; v2 ledger §9.2.3 OD-2 cited gating discharged |

---

## §5 H_T-AS-8 — Anthropic + MCP observability (STILL-BOUNDED → PARTIAL transition, NOT RETIRED)

| Field | Content |
|---|---|
| Substitution ID | H_T-AS-8 |
| Primitive | Anthropic + MCP primitive observability — 7-namespace exports per C-AS-13 + C-AS-14 (full `anthropic.*` 10-attribute set + `mcp.*` 5-attribute set + 5 supporting namespaces) |
| Spec contract | C-AS-13 + C-AS-14 + C-RT-15 (cache subset only) |
| Transition timestamp | Phase 7 sub-phase 7d U-RT-52 close arc, 2026-05-20 |
| Prior status | STILL-BOUNDED (batch 1) |
| New status | **PARTIAL** (batch 2) |
| What landed | The `anthropic.cache_*` 4-attribute subset of C-AS-14 §14.2 (`cache_creation_input_tokens` + `cache_read_input_tokens` + `cache_breakpoint_id` + `cache_ttl_seconds`) emits at `RuntimeLLMDispatcher.dispatch` conditional on `provider_name == "anthropic"`. Tests verify (a) presence under anthropic, (b) absence under openai/ollama, (c) request-side breakpoint_id + ttl_seconds extraction from `cache_control` directives. AS-AL-3 per-provider scope correctly enforced |
| What remains bounded | Remaining 6 `anthropic.*` attributes (`thinking_mode` / `thinking_budget_tokens` / `thinking_effort` / `batch_id` / `tokenizer_version` / `inference_geo`) require either separate SDK-feature adoption (thinking) or operator-level config (geo / batch / tokenizer) not present at v1.3. Entire `mcp.*` namespace (5 attrs) + 5 supporting namespaces bounded on the tool-invocation runtime composer (Phase-3+, per v2 §9.2.2) |
| X-AL-2 evaluation | Condition A met (U-AS-08 landed); condition B **NOT met** — `Authoring`-mechanism substitution is no longer the only carrier for the cache subset, but the broader 7-namespace surface remains unemitted at runtime. Per X-AL-2 "partial retirement is non-retirement", this is recorded as PARTIAL with bounded scope. **Cache subset is the live surface; the rest is the bounded residual** |
| Cross-axis dependency cascade | §6.3.1 CP-1 → AS-8 cascade partially discharged for the cache subset; remaining 6 anthropic.* attrs + mcp.* namespace still bounded on tool-invocation composer |
| Evidence anchor | `llm_dispatch.py` lines 287-318 + `_extract_anthropic_cache_request_attrs` helper (lines 175-198); 2 of 13 tests directly verify the conditional cache emission + cache_control extraction |

---

## §6 §9 Class 2 multi-LLM commitment surface closure

Per `Phase_7_Meta_Architecture_v1.md` §9.2.3 closure criterion: "the H_T runtime ships ≥1 production LLM call site". This criterion is satisfied at `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:RuntimeLLMDispatcher.dispatch`.

| Field | Status |
|---|---|
| ADR-F1 v1.2 multi-LLM commitment | **MET** at design + library code + runtime (was: met at design + library code only) |
| Substitution surface | **CLOSED** with operator visibility preserved per `Project_Workflow_v1_8.md` §2.7.7 + `Phase_6_5_Session_4_Close_Handoff.md` §5.2 |
| §9 Class 2 surface posture | **CLOSED** (was: OPEN per batch-1 + v2 §9 statement) |
| Residual | None at the §9 surface; per-provider attribute set bounded to 4 anthropic.cache_* attrs per C-AS-14 §14.2; the remaining 6 anthropic.* attributes (thinking modes / batch_id / tokenizer / inference_geo) are out of scope until their respective SDK-feature-surface landing events |

---

## §7 Filing footer

| Field | Value |
|---|---|
| Filer | Phase 7 sub-phase 7d U-RT-52 close arc, 2026-05-20 |
| Authority chain | `.harness/fork_llm_dispatch_composer_scope.md` (Q1a+Q2a+Q3a+Q4a ratified) + `.harness/fork_u_rt_52_step_payload_shape.md` (Class 3 resolved) + spec v1.3 §14.5 + plan U-RT-52 + 13 tests green |
| Predecessor | `.harness/phase-7d-retirement-events-batch-1.md` (8 events, 2026-05-20 earlier-same-day) |
| Successor consumption | Per-axis subdirectory `CLAUDE.md` §4.1 substitution-table updates for the 5 RETIRED entries (this same arc) + §9 Class 2 surface status update at root `CLAUDE.md` |
| Cumulative status | 15 / 49 retired (30.6%) post this batch. CP-axis: 4 / 22 (18.2%, includes CP-24 authoring-retired + CP-6 batch-1 + CP-1 + CP-2 this batch; CP-5 transitions STILL-BOUNDED → PARTIAL not RETIRED per X-AL-2). OD-axis: 2 / 8 (25%, OD-8 authoring-close + OD-2 this batch). AS-axis: 2 / 6 (33.3%, AS-1 batch-1 + AS-9 authoring-close; AS-8 transitions STILL-BOUNDED → PARTIAL — cache subset live, broader namespace bounded). IS-axis: 9 / 9 (100%, all batch-1). CXA-axis: 1 / 5 (20%, CXA-1 batch-1) |
