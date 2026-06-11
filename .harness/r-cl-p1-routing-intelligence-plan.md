# R-CL-P1 — Routing intelligence: grounded scope + partial-land plan

*Phase-7 implementation arc against cleared CP spec/plan. Branch `r-cl-p1-routing-intelligence`. Authored 2026-06-10 after a ground-first entry pass (CLAUDE.md §13.1 / per-phase template). This doc is the durable plan + the documented-deferral record for the two P1 deliverables grounding showed are substrate-blocked (X-AL-3: deferral must be **documented**, not silently absorbed).*

---

## 1. What the closure plan / roadmap framed P1 as

Per `.harness/post-mvp-full-closure-plan-v1.md` + roadmap §5.15: "Build `EMBEDDING` + `LLM_AS_ROUTER` decision-fns + capability-shortfall fallback (C-CP-02/03/04), replacing today's `DECLARATIVE`-echo." Flagged `⚖️ council-eligible (cost ⊥ reliability ⊥ capability-preservation)`.

## 2. What grounding found (the checkpoint's "pure impl, no fork" was overambitious)

The canonical routing policy is **already spec-pinned** — the `⚖️` flag was optimistic and is falsified:

- **Layer ordering** (manifest → embedding → llm_as_router, cheapest-deterministic-first): **LOCKED** at C-CP-02 §2.1/§2.2 + ADR-F1 v1.2; already realized in `harness_cp.layered_routing_strategy.LAYER_ORDER`.
- **Fall-through** (budget exceedance → unconditional advance): **PINNED** at C-CP-03 §3.2.
- **Capability-shortfall** (advance to next provider *before* the error path): **PINNED** at C-CP-03 §3.3.
- Remaining choices (`Spec_Control_Plane_v1_2.md` §2.4 + §3.27) are **impl-discretion tuning defaults** (embedding model, corpus, `k`, threshold, router model, budget values) — no cross-domain architectural tension survives. Council = over-machinery (operator chose **build-direct** 2026-06-10).

Grounding the **code substrate** then showed two of the three named deliverables are **substrate-blocked**, and the third is cleanly buildable:

| P1 deliverable | Disposition | Rationale |
|---|---|---|
| **capability-shortfall fallback** (C-CP-03 §3.3) | **BUILD — this PR** | All substrate exists: `reflect_provider_capabilities`/`provider_supports` (U-CP-02), `FallThroughCause.CAPABILITY_SHORTFALL` (U-CP-08), the C-CP-04 fallback chain wired into the dispatch path (`RetryBreakerFallbackDispatcher`, U-RT-58). The §3.3 *pre-dispatch* check (advance-before-error) is the one missing wire. This is the **capability-preservation axis** the operator named ("don't route a thinking-step to a non-thinking model"). |
| **`EMBEDDING` decision-fn** (C-CP-02 §2.1 Layer 2) | **DEFER — documented** | §2.1 Layer 2 requires a *trained corpus per workload class* + an embedding model; **neither exists**, and §2.4/§3.27 explicitly defer corpus + embedding-model to impl-discretion. Per §2.2, the embedding layer resolves *only* when "classifier confidence exceeds threshold" — with no corpus, confidence never exceeds, so the layer correctly **falls through** today. Building a no-op-until-corpus closure adds no behavior; building a real classifier is a separate corpus-authoring arc. Re-open trigger: an operator-supplied embedding model + per-workload corpus. |
| **`LLM_AS_ROUTER` decision-fn** (C-CP-02 §2.1 Layer 3) | **DEFER — documented** | A faithful router-model layer makes an **async** LLM call, but `LayerDecisionFn` + `route()` (U-CP-05) + `infer()` (U-CP-03) are **sync** cleared contracts. A faithful impl would widen those to async — a **contract change to cleared U-CP-03/U-CP-05** (CP §5.1 Class-1 routing), which is *not* silently absorbable (X-AL-3). Router-model binding is also undecided impl-discretion (§2.4: "Haiku-class typical"). Re-open trigger: a directed follow-up that ratifies the async routing-core contract widening. |

The **discriminator-threading** sub-question (decision-fns receive only `(ProviderAgnosticPayload, RoutingManifest)`, not the §2.1 `call_site_context`) is **pure impl** — runtime closures capture `workload_class`/`persona_tier`/`agent_role` exactly as `_declarative_echo` closes over `binding`; the locked signatures stay intact. Not needed for the capability-shortfall slice (it lives at the fallback-chain/provider layer, not the routing-layer selection).

## 3. The build (this PR) — capability-shortfall pre-dispatch check

**Locus:** `harness_runtime.lifecycle.retry_breaker_fallback.RetryBreakerFallbackDispatcher.dispatch` — top of the `while True` candidate loop, *before* the breaker pre-check / inner provider call (= "before the error path" per §3.3).

**Behavior:**
1. Derive `capability_required` from the step payload (runtime-owned payload convention; CP keeps `params` opaque per C-CP-01 §1.4): non-empty `tools` → `TOOLS`; `params["thinking"]` set → `THINKING`.
2. Reflect the current candidate's capabilities (`reflect_provider_capabilities`) and check support (`provider_supports`).
3. On shortfall: emit `fallback.triggered` (`fallback.from_provider` / `fallback.from_model` / `fallback.cause = "capability_shortfall"` / `fallback.required_capability`) per §3.3, then advance the fallback chain (`_advance_or_exhaust`) — *before* any provider call.
4. All candidates short → chain exhausts → `RetryBreakerFallbackExhaustedError` (§3.2 step 3 fail-closed; a thinking step with no thinking-capable provider fails rather than silently getting a non-thinking response — the capability-preservation guarantee).

**Live axis = THINKING.** `reflect_provider_capabilities` sets `supports_tools=True` universally, so a TOOLS requirement never shortfalls today (derived for faithfulness/future-proofing). `supports_thinking` is true only for the Anthropic extended-thinking tier (sonnet-4-6 / opus-4-6 / opus-4-7), so a thinking step correctly routes away from openai / ollama / Haiku.

**Codex-caught root fix (U-CP-02).** Out-of-family review (`just codex-review-uncommitted`) found a P1: `reflect_provider_capabilities` matched the §13.4 short tier tokens (`opus-4-7`) by *exact equality*, but runtime `ModelBinding.model` carries the full Anthropic API IDs (`claude-opus-4-7`, `claude-opus-4-7-20250101`, `claude-haiku-4-5` — verified across the runtime tests/e2e). Making the reflector load-bearing in the dispatch path would have **false-rejected real thinking-capable models** (the original tests masked it by using the bare token). Fixed at the root: `_is_anthropic_thinking_model` strips the `claude-` prefix and matches a tier exactly or as a `{tier}-` snapshot prefix; pinned by `test_supports_thinking_real_runtime_model_ids` (CP) + real-ID candidates in the runtime tests. Decorrelation validated (`[[hooks-codex-pilots-decorrelation-validated]]` / `[[test-bypass-as-runtime-truth]]`).

**Behavior-change note:** a workflow that previously sent `params["thinking"]` to a non-thinking provider (which silently ignored it) now advances/exhausts instead. This is the spec-mandated §3.3 behavior, gated on the (rare) `params["thinking"]` presence. Existing fixtures use `params:{max_tokens:…}` → empty `capability_required` → no-op pre-check → no regression.

## 4. Verification

Tests-first in `test_lifecycle_retry_breaker_fallback.py`: (a) thinking step skips a non-thinking primary *without an inner call* and lands on a thinking-capable cross-family candidate; (b) `fallback.triggered`/`capability_shortfall` event emitted on the outer span; (c) all-incapable chain → `RetryBreakerFallbackExhaustedError`; (d) no-requirement step (empty derivation) is behavior-neutral. Then full suite + `just codex-review` + advisor before PR.
