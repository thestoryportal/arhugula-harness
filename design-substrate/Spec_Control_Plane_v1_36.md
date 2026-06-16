# Spec: Control Plane — v1.36 (delta over v1.35)

---

## Change-note (v1.35 → v1.36)

**Scope of revision.** A single additive sub-section at **C-CP-02 §2** — NEW **§2.5** committing the **Layer 3 LLM_AS_ROUTER resolution surface**: the **injected, optional** async router-resolution callable (`RouterResolutionFn`) that resolves the `llm_as_router` layer at the already-async `infer()` call surface when the deterministic layers fall through (`route()` returns the `candidate=""` / `layer="llm_as_router"` sentinel). This is the **R-spec-1 (L3) leg** of the R-FS-1 **R** sub-program (routing intelligence — the LLM_AS_ROUTER + EMBEDDING layer-binding arc), materializing the §2.1-named-but-unbound **Layer 3** across the sync-`route()` / async-`infer()` decomposition that **R-300** (2026-06-01) introduced. Design authority: `.harness/r-fs-1-r-routing-intelligence-design-v1.md` **D1** (merged #596). The amendment is **Reading B** (resolve at `infer()`); **Reading A** (widen `route()` async) is **foreclosed** by the committed **ADD §5.3.3** determinism boundary + §2.2's "Probabilistic" classification of `llm_as_router`.

**The amendment.** The §2.1 layered-routing pseudocode draws **all three** layers — DECLARATIVE, EMBEDDING, **and** the Layer-3 router call — *inside a single resolution function* `on_llm_call`. The R-300 activation (2026-06-01) decomposed that monolithic drawing into **sync `route()`** (deterministic layer selection → `RoutingDecisionTrace`) + **async `infer()`** (`route()` → provider dispatch → response) — a decomposition that was **faithful while only DECLARATIVE was bound** (the two unbound layers cleanly fall through; today's production traffic resolves entirely at DECLARATIVE). Binding Layer 3 now forces a contract-shape decision the §2.1 drawing could not anticipate, because the §2.1 drawing **predates** the `route()`/`infer()` split. v1.36 commits that decision: **the Layer-3 router call resolves at the async `infer()` call surface** — when `route()` yields the LLM_AS_ROUTER empty-candidate sentinel and a router callable is injected, `infer()` invokes the router (one bounded async LLM call), obtains a `"provider:model"` candidate, rebuilds the `routing.layer="llm_as_router"` trace, and proceeds to the existing `await dispatch(...)`. `route()` / `LayerDecisionFn` / the cleared U-CP-05 sync contract are **byte-unchanged**.

**Why Reading B — probe-resolved, NOT council-convened.** The 2026-06-11 confirm-defer fork (`class_2_fork_llm_as_router_layer3_contract_shape_vs_defer.md` §5) named a genuine **C1 ⊥ C11 ⊥ C9** tension. Each leg is now resolved by a committed constraint, so **no design-time operator gate survives** (per workspace `CLAUDE.md` §10.9 nameable-tension discriminator — a tension a committed invariant forecloses routes to probe-resolution, not convening): **(a)** the build-vs-defer leg (C1 ⊥ C11) is resolved by the **standing FULL-SPEC directive** (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`, 2026-06-12) which postdates + reverses the confirm-defer — routing intelligence is a directed BUILD arc, the cost/latency concern honored by deferring the *live paid binding* to a downstream vendor gate (§2.5 "Vendor / paid-call gate"); **(b)** the determinism leg (C9 — Reading A erodes §5.3.3, Reading B preserves it) is **probe-resolved** by the committed ADD §5.3.3 boundary + §2.2's per-layer classification. A probabilistic model call (§2.2 "One full LLM call; 50–200 ms"; "Probabilistic") cannot sit in the sync layer §5.3.3 designates the **deterministic outer harness**; it belongs at `infer()`, the "probabilistic core" (`routing_core_surface.py:147-149`, acceptance #4). Reading A — making `LayerDecisionFn` + `route()` async to host the router call literally inside `route()` — would move a probabilistic call into the deterministic layer **and** carry the largest blast radius (every `LayerDecisionFn`, every `route()` caller, the cleared U-CP-05 contract). FORECLOSED.

**§2.1 preservation precision — RE-DECOMPOSED, not "untouched-in-meaning".** v1.36 differs in kind from v1.35. v1.35 **resolved a flagged-silent table** (§19.1.1.1 row-3 named a deferred `Map<MCPTrustTier, GateLevel>` whose content was spec-silent; §19.1.2 supplied that content, leaving the §19.1 formula's *meaning* untouched). **§2.1 is NOT silent** — it draws the Layer-3 router call concretely inside `on_llm_call`. §2.5 therefore does **not** claim §2.1's resolution contract is meaning-untouched; it **genuinely re-decomposes** that contract: Layer 3 resolves at the `infer()` call surface, *not* inside the monolithic `on_llm_call` / its sync-`route()` successor. This is a **faithful re-expression of the same layered intent** across the R-300 split (the cheapest-deterministic-first ordering, the per-layer attribution, the 200 ms budget are all preserved) — **not a reordering, not a reversal, not a new layer**. The §2.1 pseudocode **text is PRESERVED VERBATIM** (not edited); §2.5 documents where its Layer-3 term binds across the pre-existing decomposition. No spec *contradiction* exists (the §2.1 drawing predates the decomposition); this is the structural re-decomposition R-DESIGN D1 named, pre-authorized by the standing directive.

**Additive / no-break — the router callable is OPTIONAL.** The injected router callable is an **optional** dependency of `infer()` (a new keyword-only parameter defaulting to absent). **When no router is injected** — DECLARATIVE-only deployments, and the entire pre-R-impl-1-binding state — `infer()`'s existing behavior on the sentinel is **PRESERVED VERBATIM**: it raises `RoutingCandidateUnresolvedError` (`routing_core_surface.py:177-182`). Likewise **when the Layer-3 budget is exhausted** (`LLM_AS_ROUTER ∈ budget_exhausted`), no router is invoked and the same preserved raise fires (Layer 3 is terminal — there is no further layer to fall through to, per U-CP-08 fall-through semantics). The router branch is reached **only** when a router *is* injected **and** the L3 budget is not exhausted. This is what makes v1.36 a genuinely **additive** Class-1 re-decomposition rather than a breaking change: every existing `infer()` caller (incl. the runtime binding site at `llm_dispatch.py` + all tests) is byte-for-byte unbroken.

**Trace-carrier — rationale via the §1.4 span attribute; `RoutingDecisionTrace` NOT widened.** `RoutingDecisionTrace` is a **frozen, `extra="forbid"`, exactly-four-field** model (`layer`, `candidate`, `decision_ms`, `budget_exhausted`; `cp_shared_types.py:110-131`, docstring "Exactly four fields (acc #6)"). The router's **rationale therefore cannot be stuffed onto the trace.** The router callable returns the rationale **separately** from the candidate (a small result object — §2.5 contract below); `infer()` rebuilds the trace from the four frozen fields only (`layer="llm_as_router"`, the resolved `candidate`, `decision_ms`, `budget_exhausted`) and emits the rationale to the **C-CP-01 §1.4 `routing.binding_rationale`** optional span attribute (`Spec_Control_Plane_v1_2.md:261` — "string (optional)") on the `llm.inference` span. The trace stays 4-field; the rationale rides the span attribute §1.4 already defines for exactly this purpose. (A 5th trace field would be a separate `RoutingDecisionTrace` carrier-shape amendment — a named, non-byte-free deliverable — and is **NOT taken** at v1.36.)

**Authoring choice + discharge of the R-DESIGN §7(a) fork-to-file.** R-DESIGN §7 named, as a Class-1 fork to file at R-spec-1 authoring, "(a) the C-CP-02 §2.1 re-decomposition shape (router resolves at `infer()`) — the contract-section vs new-sub-section choice." v1.36 **discharges that fork**: the re-decomposition *shape* was decided at R-DESIGN D1 (Reading B, probe-resolved — no operator gate survives, per §8/§9 of the design doc); the residual **authoring-mechanism choice is resolved here as a NEW additive sub-section §2.5** (preserving the §2.1 text verbatim), mirroring v1.35's additive-§19.1.2 pattern and the delta-only-spec-file convention — *not* an in-place edit of §2.1. The discharge is recorded greppably here + in the co-published clearance marker; no separate `class_1_fork_*.md` is owed (the genuine Reading-B-vs-A fork was decided + cleared at #596; this leg applies it).

**v1.35 + prior body PRESERVED VERBATIM.** All v1.35 content — §19.1.2 (`MCP_TRUST_GATE_LEVEL_FLOOR` gate-axis) + §27.8 (B2-spec-1 telemetry projection) + §7.4 + §25.10–§25.18 + §29 + the entire C-CP-01 … C-CP-29 body — is PRESERVED VERBATIM per the delta-only-spec-file convention. Within C-CP-02: §2.1 (the `on_llm_call` layer-ordering pseudocode) / §2.2 (per-layer cost discipline) / §2.3 (per-layer attribution) / §2.4 (per-layer time budget + impl-discretion deferral) are **PRESERVED VERBATIM**; the **only** change is the additive **§2.5** below. C-CP-01 §1.4 (`routing.*` attribute table, incl. `routing.binding_rationale`) is PRESERVED VERBATIM and cited unchanged.

**No new contract ID; no new ADR; no enum change; no new fail class; no `RoutingDecisionTrace` / `RoutingLayer` member change.** §2.5 is an additive sub-section of the existing **C-CP-02** contract (the layered routing strategy), materializing the resolution surface for the Layer-3 value the §2.1 pseudocode + the `RoutingLayer.LLM_AS_ROUTER` enum already name. It mints no new primitive — the layered cheapest-deterministic-first strategy with LLM-as-router as opt-in last-resort is committed at **ADR-F1 v1.2 §Decision** (X-AL-3-clean: §2.1 already names the router call + `layer="llm_as_router"`; v1.36 materializes *where* it resolves across the R-300 split). **SPEC-ONLY** — no `harness-*/src/**` edit; the Layer-3 resolution surface is inert in production until the impl legs (R-impl-1 mock router, R-impl-2 vendor-gated live router).

---

## §2.5 (NEW) C-CP-02 — Layer 3 LLM_AS_ROUTER resolution surface (re-decomposes §2.1 Layer 3 across the `route()` / `infer()` split)

**Contract.** When the deterministic routing layers fall through, **Layer 3 LLM_AS_ROUTER** resolves at the **async inference call surface** (`infer()`), via an **injected, optional** async **router-resolution callable**. This materializes the §2.1 Layer-3 term — "Invoke router model with call_site_context + candidate-set summary … Return RoutingBinding(provider, model, layer='llm_as_router', binding_rationale=router_rationale_summary)" — across the sync-`route()` / async-`infer()` decomposition (R-300). The deterministic layer-selection function `route()` and its `LayerDecisionFn` contract (U-CP-05) are unchanged.

### §2.5.1 The `RouterResolutionFn` contract

The Layer-3 resolver is an injected async callable, mirroring the existing injected `dispatch` (provider-SDK) and `LayerDecisionFn` (per-layer decision) seams:

```
RouterResolutionFn  (injected into infer(); OPTIONAL — absent by default):

    async (call_site_context, candidate_set_summary) -> RouterResolution

      call_site_context      : the inference request / routing context
                               (the same InferenceRequest infer() already holds)
      candidate_set_summary  : a summary of the eligible "provider:model"
                               candidate universe (derived from the routing
                               manifest / ProviderCapabilities surface, F1 §1.2)

    RouterResolution:
      candidate  : str   — the selected "provider:model" tuple (well-formed)
      rationale  : str   — short rationale token(s); the §2.1
                           `router_rationale_summary`. Returned SEPARATELY from
                           the candidate (NOT carried on RoutingDecisionTrace —
                           see §2.5.4).
```

- **Async.** A faithful Layer 3 makes **one full async LLM call** to a router model (§2.2 "One full LLM call per dispatch; 50–200 ms latency"; "Probabilistic"). It is therefore an `await`-shaped callable, resolvable only at the already-async `infer()` (§5.3.3 — the probabilistic core), never inside sync `route()`.
- **Injected.** The concrete router model + prompt are **not** named by the spec — they are the §2.4 impl-discretion / vendor deferral ("specific LLM-as-router prompt content … specific router model binding (Haiku-class typical)"). The callable is composed by the runtime at the binding site, exactly as `dispatch` is.
- **Leaf / direct-dispatch (no-regress invariant).** The router callable **dispatches DIRECTLY against its pre-bound router model** (a fixed `provider:model` bound at injection time). It **MUST NOT re-enter** `infer()`, `route()`, or the layered routing strategy. Re-entry would be an infinite-regress hazard: an unresolved router call recursing router → `infer()` → `route()` → sentinel → router → …. The router is a **terminal leaf** of the routing graph: `(call_site_context, candidate_set_summary)` in, `RouterResolution` out, via one direct provider dispatch.

### §2.5.2 Integration semantics at `infer()`

`infer()` gains an optional `router: RouterResolutionFn | None` keyword parameter. The resolution sequence (additive; the non-router path is preserved verbatim):

```
trace = route(request, manifest, layer_decisions, budgets, budget_exhausted)   # sync, UNCHANGED

if trace.candidate == "" and trace.layer == LLM_AS_ROUTER.value:               # the L3 sentinel
    if router is None or LLM_AS_ROUTER in budget_exhausted:
        raise RoutingCandidateUnresolvedError(...)                            # PRESERVED VERBATIM (:177-182)
    resolution = await router(request, candidate_set_summary)                  # the one bounded async router call
    trace = RoutingDecisionTrace(                                              # rebuilt — 4 frozen fields only
        layer = LLM_AS_ROUTER.value,
        candidate = resolution.candidate,
        decision_ms = <router-call latency>,
        budget_exhausted = trace.budget_exhausted,
    )
    emit routing.binding_rationale = resolution.rationale  on the llm.inference span   # §1.4 :261

# unchanged from here:
provider, model = parse(trace.candidate)                                       # :177
result = await dispatch(provider, model, request.request_payload, trace)       # :183
```

- The router branch is entered **only** when `route()` yields the LLM_AS_ROUTER sentinel **and** a router is injected **and** the L3 budget is not exhausted. In every other case `infer()` behaves byte-for-byte as at HEAD.
- The resolved `candidate` must be a well-formed `"provider:model"` string; a malformed router return re-raises `RoutingCandidateUnresolvedError` (the existing `:178` well-formedness guard is reused, unchanged).

### §2.5.3 Budget + fall-through composition (C-CP-03 / U-CP-08, preserved)

The Layer-3 router call is bounded by the **already-reserved 200 ms `LayerBudget`** (`LayerBudget(layer=LLM_AS_ROUTER, time_budget_ms=200)`; `layer_budget.py:72`). Because **LLM_AS_ROUTER is the terminal layer** (`LAYER_ORDER = (DECLARATIVE, EMBEDDING, LLM_AS_ROUTER)`), budget exhaustion at Layer 3 has **no further layer to fall through to** — it composes with the §2.5.2 preserved raise: `LLM_AS_ROUTER ∈ budget_exhausted` ⇒ no router invocation ⇒ `RoutingCandidateUnresolvedError`. This is the natural extension of the U-CP-08 fall-through semantics already modeled by `budget_exhausted` (a budget-exhausted non-terminal layer is skipped to the next; the terminal layer's exhaustion surfaces as unresolved). The cheapest-deterministic-first ordering (§2.2) and per-layer time-budget invariant (§2.4) are unchanged: `route()` resolves the sync layers in order and short-circuits on the first hit; only on full deterministic fall-through is the async router consulted.

### §2.5.4 Trace carriage + the router-call's own cost / observability

- **Trace carriage.** The rebuilt Layer-3 trace uses the **four frozen `RoutingDecisionTrace` fields only**. The router **rationale** rides the **C-CP-01 §1.4 `routing.binding_rationale`** optional span attribute (`:261`, "string (optional)") on the `llm.inference` span — the attribute §1.4 already defines as "Short token enumeration of which manifest entry / which classifier label / which fallback trigger drove the binding". `RoutingDecisionTrace` is **not** widened; `routing.layer="llm_as_router"` + `routing.binding_rationale=<router rationale>` are the per-§1.4 attribution for a router-resolved call.
- **The router call is itself a billable LLM call.** The router dispatch is a real provider call (§2.2 "One full LLM call"), distinct from the *workload* call it selects a binding for. It therefore (i) **emits its own observability span** (the router model's `llm.inference` span, child of the routing decision), and (ii) **is cost-attributed** — it is not free. The **precise cost-bucket discrimination** — whether the router-call's cost attributes to the same workflow step it routes, or to a distinct routing-overhead bucket (a `routing:` / router-meta attribution) — is a deliberate **named deferral to the CA (cross-axis cost-attribution) arc + R-impl** (it composes with the OD 5-step cost-attribution chain + the CXA cost-attribution audit-write seam, not authored at this CP-spec leg). v1.36 commits the **principle** (the router call is billable, observable, and attributed); the **attribution wiring** is downstream. This mirrors §2.4's standing impl-discretion deferral of the router model + prompt.

### §2.5.5 Scope — SPEC-ONLY (impl at R-impl-1 / R-impl-2)

v1.36 authors ONLY the §2.5 Layer-3 resolution-surface contract. The realizing impl lands across the **R** cascade legs (R-DESIGN §7):

- **R-impl-1 (L3, NO paid call)** — add the optional `router` parameter + the sentinel→router branch to `infer()` (`routing_core_surface.py`); bind a **mock / local-fixture** `RouterResolutionFn` at the runtime binding site (`llm_dispatch.py:547-553`); tests including a fall-through→router e2e via a mock (or free-local Ollama) router, asserting (a) the sentinel resolves to the router-supplied candidate, (b) the `routing.layer="llm_as_router"` + `routing.binding_rationale` span attribution, (c) **no-regress**: absent router ⇒ preserved `RoutingCandidateUnresolvedError`; L3-budget-exhausted ⇒ preserved raise.
- **R-impl-2 (L3 VENDOR GATE)** — bind a **real router model + prompt** + a **gated live e2e**; the live paid call is **surfaced, never auto-fired** (`[[feedback-background-agent-no-unilateral-paid-calls-or-secret-relocation]]`; free-local Ollama preferred where it suffices, `[[feedback-run-credential-gated-live-e2e-authorized]]`).

The Layer-3 resolution surface is **inert in production until R-impl** (no router is injected today; the preserved sentinel raise governs). Closure is demonstrated at R-impl-1 (the fall-through→mock-router e2e + the contrasting no-regress baseline).

### §2.5.6 Layer 2 EMBEDDING is NOT bound here

Per R-DESIGN **D2**, the Layer-2 EMBEDDING contract shape is **conditional on the (gated) embedding-model choice** and is **NOT decided at this leg**. The discriminator is async-I/O vs sync-compute (embedding is "deterministic-modulo-corpus" per §2.2, not probabilistic), turning on the embedding *projection* model: an **in-process sync** model → a sync `LayerDecisionFn` bound at `EMBEDDING` inside `route()` (no spec amendment); a **remote/async** model — including the stack-native Ollama `/api/embeddings` — → a Reading-B mirror at `infer()` (a second injected async classifier callable). Given the committed async-SDK stack, the no-fork path is **not** the default. L2 is sequenced **after** L3 and **after** the embedding-model + corpus vendor gate (R-L2-gate); **R-spec-2 / next_action MUST NOT presume L2 is no-fork.** v1.36 is silent on L2 by design.

---

## §-preserved-verbatim

| Section | Identity | v1.36 status |
|---|---|---|
| §1 — §18 (incl. C-CP-01 §1.4 `routing.*` attribute table) | — | PRESERVED VERBATIM (§1.4 `routing.binding_rationale` cited unchanged) |
| §2.1 (the `on_llm_call` layer-ordering pseudocode) | **C-CP-02 layered routing strategy** | **Text PRESERVED VERBATIM**; §2.5 **RE-DECOMPOSES** its Layer-3 resolution contract across the sync-`route()` / async-`infer()` split (a faithful re-expression of the same layered intent — the §2.1 drawing predates the R-300 decomposition; NOT a reordering or reversal) |
| §2.2 (per-layer cost discipline) / §2.3 (per-layer attribution) / §2.4 (per-layer time budget + impl-discretion deferral) | C-CP-02 | PRESERVED VERBATIM (the §2.2 "Probabilistic" classification + §2.4 router-model/prompt deferral are the load-bearing anchors §2.5 rests on, unedited) |
| §3 / C-CP-03 (per-layer time budget) | **per-layer budget + fall-through** | PRESERVED VERBATIM (§2.5.3 composes with it; the 200 ms L3 `LayerBudget` is unchanged) |
| §4 — §18 | — | PRESERVED VERBATIM |
| §19.1 / §19.1.1 / §19.1.2 (v1.35 `MCP_TRUST_GATE_LEVEL_FLOOR`) / §19.3 / §19.4 / §19.5 | C-CP-19 | PRESERVED VERBATIM |
| §20 — §24 | — | PRESERVED VERBATIM |
| §25 / C-CP-25 (incl. §25.10–§25.18) | **WorkflowDriver** | PRESERVED VERBATIM |
| §26 / C-CP-26 | **PauseResumeProtocol** | PRESERVED VERBATIM |
| §27.1 — §27.8 / C-CP-27 (incl. v1.34 §27.8 telemetry projection) | **PerServerTrustEvaluator + MCPClientNamespaceEmitter** | PRESERVED VERBATIM |
| §28 / C-CP-28 | **ValidatorFramework** | PRESERVED VERBATIM |
| §29 / C-CP-29 | **PromptSelectionManifest** | PRESERVED VERBATIM |

§2.5 is an additive sub-section to the existing C-CP-02 §2 contract; no prior section's **text** is amended. §2.1's Layer-3 **resolution contract** is re-decomposed (its drawing predated the R-300 `route()`/`infer()` split) — a faithful re-expression, explicitly recorded here rather than silently absorbed (the honest distinction from v1.35, which filled a spec-silent table without touching its formula's meaning).

---

## §-filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_36.md` |
| Authored at | Phase 7 / R-FS-1 **R** sub-program (R-spec-1 — Layer 3 LLM_AS_ROUTER resolution surface), 2026-06-16 |
| Authoring authority | `.harness/r-fs-1-r-routing-intelligence-design-v1.md` **D1** (merged #596) — the R-DESIGN doc is the design-authority fork that decided **Reading B** (probe-resolved by ADD §5.3.3 + §2.2 "Probabilistic"; **no design-time operator gate survives**, per design §8/§9). v1.36 **discharges the R-DESIGN §7(a) fork-to-file** (the §2.1 re-decomposition shape) via the new-additive-§2.5 authoring choice recorded in the change-note + clearance marker. Standing directive: `[[feedback-full-spec-beyond-mvp-nothing-deferred]]` (FULL-SPEC, 2026-06-12) reversing the 2026-06-11 confirm-defer. Adopt-and-note posture; this leg authored under the operator's standing **autonomous-loop grant** (no live AskUserQuestion — operator asleep) — authorization basis = the loop-autonomy grant + the FULL-SPEC directive + the R-DESIGN review chain. |
| Reviewer chain | Decorrelated, **non-human** (no live operator AUQ this leg): advisor (pre-substantive — surfaced the optional-router-fn / preserved-raise additivity invariant, the named `RouterResolutionFn` I/O contract + separate-rationale path, the §1.4-vs-§2.2 rationale-cite correction, the §7(a) fork-to-file discharge requirement, the L3-budget-terminal fall-through) + out-of-family Codex (pre-merge, per the R-DESIGN precedent). |
| Predecessor | `Spec_Control_Plane_v1_35.md` (v1.35) |
| Co-published (this PR) | clearance marker `.harness/clearance/Spec_Control_Plane-v1_36-cleared-2026-06-16.md` + pointer refreshes (root `CLAUDE.md` §2.3, `harness-cp/CLAUDE.md` §1.2, `.harness/claude-artifact-pointers.md` §2.3 — CP spec head v1_35 → v1_36). **Owed at post-merge:** the §12.2.1 roadmap fixed-point refresh (terminating refresh PR, separate from this substantive PR; `next_action` → R-plan-1). |
| Coordinated next arcs | **R-plan-1** (atomic-unit decomposition: the `infer()` optional-`router` parameter + sentinel→router branch; the `RouterResolutionFn` injection point at the runtime binding site; the router-decision trace + `routing.binding_rationale` span emission; budget/timeout composition) → **R-impl-1** (L3 mock router, NO paid call) → **R-impl-2** (L3 vendor gate — surface, don't auto-fire) → **R-L2-gate** (embedding model + corpus) → conditional **R-spec-2 / R-impl** (L2). Router-call cost-bucket attribution deferred to the **CA** arc + R-impl (§2.5.4). |
| Revision policy | Delta-only spec file per workspace `CLAUDE.md` §2.3 convention; v1.35 body + C-CP-02 §2.1/§2.2/§2.3/§2.4 + C-CP-01 §1.4 PRESERVED VERBATIM; the additive §2.5 only |

---

*End of `Spec_Control_Plane_v1_36.md`. Parent guidance at workspace root `CLAUDE.md`. C-CP-02 §2 layered routing strategy + §2.1 `on_llm_call` pseudocode + §2.2 per-layer classification at `Spec_Control_Plane_v1_2.md` §2; C-CP-01 §1.4 `routing.binding_rationale` span attribute at `Spec_Control_Plane_v1_2.md:261`. ADD §5.3.3 determinism boundary (in-repo restatements: `routing_core_surface.py:147-149` + B1-DESIGN §7 + §2.2 per-layer classification). R-DESIGN authority at `.harness/r-fs-1-r-routing-intelligence-design-v1.md` (merged #596). The L2 EMBEDDING leg is sequenced after the L3 legs + the embedding-model vendor gate (§2.5.6).*
