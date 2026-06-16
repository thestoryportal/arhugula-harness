# R-FS-1 Arc R — Routing Intelligence (LLM_AS_ROUTER L3 + EMBEDDING L2): Design

**Authored:** 2026-06-16 · **Posture:** mode-agnostic (process-substrate; grounds `harness-*/src` + canonical specs at HEAD `d4aa9de` by direct read; **authors only this `.harness/` file**. No `design-substrate/**` or `harness-*/src` edit — those wait on this design's spec/impl legs. The roadmap/dashboard `next_action` is re-derived by the separate **post-merge §12.2 terminating-refresh** step, not by this PR). · **X-AL-3:** trivially clean (zero `design-substrate/**` / `harness-*/src` edit).

**Precedent:** the design-first PR of the **R** sub-program, following the B1/B2/B3-DESIGN shape (each sub-program opens with a `.harness/` design doc, then design→spec→plan→impl legs each carrying a clearance marker).

**Arc:** R-FS-1, child arc **R** (FROZEN order `B1✅→B3✅→E✅→B2✅→R→B4→CA→B5→B6→B7→M`). **Directive:** `[[feedback-full-spec-beyond-mvp-nothing-deferred]]` (STANDING 2026-06-12) — the full routing-intelligence stack is built; the 2026-06-11 confirm-defer (`.harness/class_2_fork_llm_as_router_layer3_contract_shape_vs_defer.md` §8) is **reversed** by the standing directive, which postdates it. Design back-flow is PRE-AUTHORIZED.

**Spine:** `.harness/beyond-mvp-capability-boundary-ledger.md` · `.harness/r-fs-1-remaining-arcs-grounding-sweep-v1.md` §"Arc R".

---

## §0 What R is, and what this PR is

**R = bind the two probabilistic-or-corpus routing layers** that today fall through unbound — **Layer 2 EMBEDDING** (embedding-classifier dispatch) + **Layer 3 LLM_AS_ROUTER** (router-model dispatch) — completing the C-CP-02 §2.1 layered "cheapest-deterministic-first" routing strategy. Today only **Layer 1 DECLARATIVE** is bound; L2/L3 cleanly fall through (the §2.2 invariant — each call resolves at the cheapest layer that can resolve it).

**This PR is design only** — it grounds the current state, makes the two contract-shape decisions (D1 L3, D2 L2), enumerates the downstream spec/plan/impl legs + their vendor gates, and is mode-agnostic + X-AL-3-clean. **It builds nothing**; the readings it decides drive the R-spec / R-plan / R-impl legs (§7).

**Why R is not "already done."** R-300 (2026-06-01) activated `infer()` and wired the production path (every inference step routes through it). But that activation bound **only DECLARATIVE** — the embedding classifier + router model have no decision-fn. So routing intelligence is *infra-built + wired but capability-unbound*: not vacuous, not unbuilt — a `partially-built` arc whose remaining work is to bind L2 + L3 (grounding sweep §"Arc R").

---

## §1 Grounding (current state at HEAD `d4aa9de`, by direct read)

| Surface | At HEAD | Cite |
|---|---|---|
| `route()` | **sync** `def route(...) -> RoutingDecisionTrace`; iterates `LAYER_ORDER` (DECLARATIVE, EMBEDDING, LLM_AS_ROUTER); a layer with no bound `decision_fn` is skipped (`layer_decisions.get(layer) is None → continue`); docstring *"Deterministic given inputs."* | `harness-cp/.../layered_routing_strategy.py:62`, `:80-94` |
| Fall-through sentinel | when no layer decides, returns `RoutingDecisionTrace(layer=LLM_AS_ROUTER.value, candidate="")` — the **empty-candidate sentinel** | `layered_routing_strategy.py:96-101` |
| `LayerDecisionFn` | **sync** `Callable[[InferenceRequest, RoutingManifest], "str | None"]` | `layered_routing_strategy.py:51` |
| `infer()` | **`async def`** — the single LLM-inference entry-point; calls sync `route()`, parses the `"provider:model"` candidate, then `await dispatch(...)`; **raises `RoutingCandidateUnresolvedError` on an empty/malformed candidate** | `harness-cp/.../routing_core_surface.py:129`, `:170-183` |
| Determinism boundary | `infer()` docstring (acceptance #4): *"`infer` is the **probabilistic core** of the **deterministic outer harness** per ADD §5.3.3 … everything around it … is deterministic."* | `routing_core_surface.py:147-149` |
| Bound decision-fns (runtime) | **only `{RoutingLayer.DECLARATIVE: _declarative_echo}`** — EMBEDDING + LLM_AS_ROUTER have **no** decision-fn → `route()` skips them → fall-through | `harness-runtime/.../lifecycle/llm_dispatch.py:496`, `:547-553` |
| LLM_AS_ROUTER budget | `LayerBudget(layer=LLM_AS_ROUTER, time_budget_ms=200)` — a 200 ms hot-path budget already reserved | `harness-cp/.../layer_budget.py:72` |
| Production caller | `stage_5_loop_init.py:241` → `materialize_llm_dispatcher_stage` → `RuntimeLLMDispatcher.dispatch` → `infer` → `route`, **every inference step**. Reachable, not dormant. | `stage_5_loop_init.py:241` |

**Consequence: no behavior is missing today.** DECLARATIVE manifest routing resolves all production traffic; L2 + L3 cleanly fall through. The R arc *binds* them.

**What the spec mandates (the load-bearing per-layer classification, in-repo + resolvable):**

| Layer | §2.1 / §2.2 classification | Cite |
|---|---|---|
| **EMBEDDING (L2)** | "Embedding-classifier dispatch (cheap, **deterministic-modulo-classifier**)"; "Project … into embedding space. Run **k-nearest** classifier against trained corpus"; cost row: "k-nearest is **local**" · "**Deterministic** modulo classifier corpus version" | `Spec_Control_Plane_v1_2.md:294-299`, `:314` |
| **LLM_AS_ROUTER (L3)** | "LLM-as-router (expensive, last-resort)"; "Invoke router model"; cost row: "**One full LLM call** per dispatch; 50–200 ms latency" · "**Pro**[babilistic]" | `Spec_Control_Plane_v1_2.md:302-305`, `:315` |
| Deferred to impl discretion (§2.4) | "Specific **embedding model and dimensionality**; specific classifier **training-corpus** construction … specific **LLM-as-router prompt** content … specific **router model binding** (Haiku-class typical per cost discipline)" — one deferral row covers **both** L2 + L3 models | `Spec_Control_Plane_v1_2.md:327` |

The §2.1 pseudocode draws **both** L2 and L3 *inside* a single resolution function `on_llm_call`. The Phase-7 impl decomposed that into sync `route()` (deterministic layer selection) + async `infer()` (route + dispatch) — faithful *while only DECLARATIVE is bound*. Binding L2/L3 forces the contract-shape decisions below, because the §2.1 drawing predates the sync-`route()`/async-`infer()` decomposition.

---

## §2 DECISION D1 — Layer 3 LLM_AS_ROUTER resolves at the async `infer()` (Reading B); Reading A is foreclosed

**The discriminator is async-I/O, sharpened by the §5.3.3 determinism boundary.** A faithful Layer 3 makes **one full async LLM call** to a router model (§2.2 "One full LLM call; 50–200 ms"; **Probabilistic**). A probabilistic provider model call is, by ADD §5.3.3, the *probabilistic core* — it belongs at `infer()` (already async, already "the probabilistic core"), **not** inside sync, deterministic `route()`.

| Reading | Where the router call lives | Cleared-contract blast radius | §5.3.3 boundary | Verdict |
|---|---|---|---|---|
| **A — widen `route()`** | make `LayerDecisionFn` + `route()` **async**; L3 resolves inside `route()` (literal §2.1 shape) | **Large** — every `LayerDecisionFn`, every `route()` caller, the cleared U-CP-05 contract | **Eroded** — a probabilistic LLM call moves *into* the layer §5.3.3 designates deterministic | **FORECLOSED.** Breaks `route()`'s advertised determinism; largest blast. |
| **B — resolve at `infer()`** ✅ | `route()` stays sync + returns the existing `candidate=""` LLM_AS_ROUTER sentinel; the **already-async** `infer()` detects "no deterministic candidate" and makes the async router call via a **new injected async router callable** (mirroring the existing `dispatch`), producing the `routing.layer="llm_as_router"` trace there | **Smaller** — additive async branch in `infer()` + one injected callable; `route()` + `LayerDecisionFn` **byte-unchanged** | **Preserved** — the LLM call stays at the boundary already designated probabilistic | **RECOMMENDED + decided.** |

**Decision: Reading B.** This is **probe-resolved**, not an open operator gate: the committed ADD §5.3.3 determinism boundary + the §2.2 "Probabilistic" classification of `llm_as_router` together foreclose Reading A (`[[probe-resolves-fork-prescribed-council]]` — a committed invariant forecloses a branch). Reading B is still a **Class 1 CP-spec amendment** (a structural re-decomposition of C-CP-02 §2.1: L3 resolves at the call surface, not inside `route()`) — pre-authorized per the standing directive; it carries a clearance marker (§4.5).

**Integration point (precise).** `infer()` today raises `RoutingCandidateUnresolvedError` when `trace.candidate == ""` (`routing_core_surface.py:177-182`). Reading B replaces *only that raise path*: when `route()` returns the LLM_AS_ROUTER sentinel (`candidate == ""`, `layer == "llm_as_router"`), `infer()` invokes the injected async **router callable** → obtains a `"provider:model"` candidate → rebuilds the trace with `layer="llm_as_router"` + the resolved `candidate` → proceeds to the existing `await dispatch(...)`. The 200 ms `LayerBudget` (already reserved, `layer_budget.py:72`) bounds the router call. `route()` / `LayerDecisionFn` / the cleared U-CP-05 sync contract are untouched.

**Trace-carrier note (R-spec-1 owes this — do NOT presume it is free).** `RoutingDecisionTrace` is a **frozen, `extra="forbid"` four-field** model (`layer`, `candidate`, `decision_ms`, `budget_exhausted` — defined at `cp_shared_types.py:110-131`, `model_config = ConfigDict(extra="forbid", frozen=True)`, docstring "Exactly four fields (acc #6)"), so the rebuilt router trace uses **only those four fields** — the router's **rationale cannot be stuffed onto the trace as-is.** §2.2 already defines `routing.binding_rationale` as an **optional span attribute** (`Spec_Control_Plane_v1_2.md:261`) — the no-carrier-change path emits the rationale **there**, at the `llm.inference` span, not on the trace. If R-spec-1 instead chooses to carry the rationale on the trace, that is a **`RoutingDecisionTrace` carrier-shape amendment** (a 5th field on the frozen model + every `route()` constructor/test) — a real, named R-spec-1 / R-plan-1 deliverable, not a byte-free change. **Recommended: emit via the span attribute** (zero carrier change; faithful to §2.2's existing telemetry shape).

---

## §3 DECISION D2 — Layer 2 EMBEDDING contract shape is conditional on the (gated) embedding-model choice (sync in-process → no fork; async API → Reading B)

The grounding sweep flagged the L2 shape as the one genuinely-two-pathed open question ("sync local model may fit sync `LayerDecisionFn` (no fork) vs async like L3"). Grounding the spec settles the *discriminator* but **not** the path — the path is gated. **The discriminator is async-I/O vs sync-compute, NOT probabilistic-ness** (embedding is "Deterministic modulo classifier corpus version" per §2.2 — this corrects an earlier "embedding is probabilistic → must leave `route()`" mis-analysis; see §8). And the async/sync question turns on **step 1, the embedding *projection*** ("**one embedding call**" — project `call_site_context` into embedding space, §2.1 `:295`), **not** step 2, the k-NN search ("k-nearest is **local**", `:314` — the *search* is always in-process; that line says nothing about the projection):

- The **projection is the embedding model**, which §2.4 defers to impl-discretion / vendor (`:327`). **Sync iff that model is in-process** (e.g. a new `sentence-transformers`/ONNX dep — a stack decision); **async** if it is an API.
- **The stack-native local option — Ollama embeddings (`/api/embeddings`) — is an async HTTP call** (consistent with the committed stack: providers are async SDK clients; `providers.py` has no embedding surface at HEAD). So a *locally-hosted* embedding via the stack-native route is **async → Reading B**, *not* no-fork. The no-fork path is a *specific* choice (commit to an in-process sync embedding dep), not the default.

| Path | Precondition (the gated model choice) | Where L2 lives | Blast radius / spec |
|---|---|---|---|
| **L2-sync** | an **in-process sync** embedding model is chosen — a *new stack dep* (e.g. `sentence-transformers`/ONNX); NOT the stack-native route | a real k-nearest **sync `LayerDecisionFn`** bound at the `EMBEDDING` layer **inside `route()`** | **No fork, no spec amendment.** Faithful to §2.1's in-`route()` drawing; preserves §5.3.3 (deterministic-modulo-corpus → deterministic outer layer). Build = the decision-fn + a corpus + the sync embedding dep. |
| **L2-async** | a **remote/async** embedding model — **incl. the stack-native Ollama `/api/embeddings`** | resolve at `infer()`, mirroring L3 Reading B (a second injected async classifier callable) | Class 1 §2.1 re-decomposition (smaller, mirrors D1). |

**Decision: present both NEUTRALLY; the path is determined by the gated embedding-model choice (§6) — it is NOT pre-decided here, and given the committed async-SDK stack the L2-async/Reading-B path is at least as likely as L2-sync.** The local-vs-remote embedding-model + corpus selection is exactly the §2.4 impl-discretion / vendor decision — **not a design-time operator gate**; it is resolved at the L2 vendor sub-arc. Pre-committing L2 *either* way here would either (a) author an unnecessary Class-1 amendment if the model turns out sync, or (b) falsely promise "no-fork" if it turns out async (the stack-native case). **R-spec-1 and the post-merge `next_action` MUST NOT presume L2 is no-fork** — L2 spec/impl is sequenced *after* L3 and *after* the embedding-model gate (§7). The corpus (a *trained per-workload-class* artifact, §2.1) is an **authoring + vendor** deliverable either way (§6).

---

## §4 The cheapest-deterministic-first ordering + budgets are preserved

`LAYER_ORDER = (DECLARATIVE, EMBEDDING, LLM_AS_ROUTER)` and the per-layer `LayerBudget`s are **unchanged**. Resolution composes across the `route()`/`infer()` split without reordering:

1. `route()` resolves the **sync** layers in order — DECLARATIVE always, **+ EMBEDDING if L2-sync** (in-process model) — and short-circuits on the first hit (§2.2 acceptance #5: a manifest hit performs no embedding/router compute).
2. If `route()` yields the sentinel (no deterministic candidate), `infer()` resolves the **async** layers in `LAYER_ORDER` order — **EMBEDDING if L2-async, then LLM_AS_ROUTER** — each bounded by its `LayerBudget`; a budget-exhausted layer falls through (U-CP-08, already modeled by `budget_exhausted`).

This keeps the §2.2 cheapest-first invariant (each call resolves at the cheapest layer that can) while honoring §5.3.3 (deterministic layers in `route()`, the async/model-call layers in `infer()`).

---

## §5 Determinism boundary (ADD §5.3.3 — the decisive discriminator)

Production reliability lives in the **deterministic outer harness**; the probabilistic surface is the **model call inside a step** (the B1-DESIGN §7 restatement; the `infer()` docstring `:147-149`). The R design maps each layer onto this boundary by its §2.2 classification:

- **DECLARATIVE** — deterministic (manifest lookup) → `route()`. ✔ (unchanged)
- **EMBEDDING** — *deterministic*-modulo-corpus regardless of model location (the k-NN *search* is always local). Determinism does **not** force it out of `route()`; only the **embedding-projection model's I/O** does: **sync in-process model → `route()`** (L2-sync), **async API model (incl. Ollama) → `infer()`** (L2-async). The split here is an I/O constraint, not a determinism one. ✔
- **LLM_AS_ROUTER** — *probabilistic* (a full model call) → `infer()` (Reading B). ✔

This is the single principle that (a) forecloses Reading A for L3 and (b) lets L2-sync stay out of a fork. Reading A would move a probabilistic model call into the layer §5.3.3 names deterministic; L2-sync can stay in `route()` precisely because an in-process k-NN with an in-process projection is deterministic + sync — but L2-async (incl. the stack-native Ollama embedding) leaves for `infer()` on the I/O constraint, not a determinism one.

**Class-3 informational (cite-resolvability).** ADD §5.3.3's *verbatim body* is not physically present in `design-substrate/` — `Architectural_Design_Document_v1_3.md:150` records "[All sub-sections §5.3.1–§5.3.3 preserved verbatim from v1.2]" and no `_v1_2.md` is in-repo. The authoritative **in-repo** statements of the boundary are `routing_core_surface.py:147-149` + B1-DESIGN §7 + the §2.2 per-layer determinism classification (all resolvable + mutually consistent). The per-layer classification is decisive on its own, so this gap is **non-blocking**; it is noted for the back-flow ledger (a future ADD re-table should fold the §5.3.x bodies in-repo).

---

## §6 Vendor / paid-call gates (never auto-fire — surface at the impl legs)

Per the loop security constraints + `[[feedback-background-agent-no-unilateral-paid-calls-or-secret-relocation]]`: every R *build* slice up to the vendor gate is Claude-buildable with a mock/local fixture (no paid boundary); only the live binding is gated.

| Gate | What it needs | Where surfaced |
|---|---|---|
| **L3 router-model gate** | a bound **router model** (Haiku-class per §2.4 cost discipline) + the **router prompt** content + **paid-call auth** for the live e2e | R-impl-2 (L3 vendor) — drive to the dispatch boundary, surface, do not auto-fire. Free-local **Ollama** is the preferred non-paid live exercise where it suffices (`[[feedback-run-credential-gated-live-e2e-authorized]]`). |
| **L2 embedding gate** | the **embedding model** (local-sync vs remote-async — drives D2's path) + the **trained per-workload-class corpus** (does not exist; an authoring deliverable) + (if remote) **API auth** | R-impl (L2 vendor) — the corpus authoring + model selection is the genuine L2 operator/vendor decision. |

The **design + the L3 mock-router impl + the L2 k-NN-against-a-fixture-corpus impl with a mock/stub embedding callable** carry no paid boundary and are driven autonomously. The router/embedding *model bindings* + the real corpus are the only gated steps.

---

## §7 Cascade-leg enumeration (the sequencing deliverable)

Two tracks, design-fork-first; **L3 nearer** (a router model already exists among the bound providers — no corpus to author), **L2 larger** (needs a corpus). Sequence **L3 then L2**.

| Leg | Scope | Artifact(s) | Back-flow |
|---|---|---|---|
| **R-design (this PR)** | the design above (D1 L3 Reading B; D2 L2 conditional) | `.harness/r-fs-1-r-routing-intelligence-design-v1.md` | mode-agnostic; X-AL-3-clean |
| **R-spec-1 (L3)** | Class 1 CP-spec amendment re-decomposing **C-CP-02 §2.1**: Layer 3 resolves at the call surface (`infer()`), not inside `route()`; an injected **async router callable** contract + the `routing.layer="llm_as_router"` trace produced at `infer()`; `route()`/`LayerDecisionFn`/U-CP-05 **byte-unchanged**; the 200 ms `LayerBudget` binds the router call | CP spec amendment (`Spec_Control_Plane` vNext §2 / C-CP-02) + clearance marker | design-substrate edit → clearance marker |
| **R-plan-1 (L3)** | atomic-unit decomposition: the async router-callable injection point, the `infer()` sentinel→router branch, the router-decision trace + `binding_rationale`, budget/timeout composition | CP (+ runtime) plan amendment | design-substrate edit → clearance marker |
| **R-impl-1 (L3, NO paid call)** | `infer()` sentinel→router branch + a **mock/local router decision callable** bound at the runtime binding site (`llm_dispatch.py:547-553`); tests incl. a fall-through→router e2e via a mock or free-local Ollama (sentinel only resolvable at the router layer) | `harness-cp/src` + `harness-runtime/src` + tests | Phase 7 impl against cleared spec |
| **R-impl-2 (L3 VENDOR GATE)** | bind a **real router model + prompt** + a **gated live e2e**; **surface, do not auto-fire** the paid call | `harness-runtime/src` (binding) + gated `@pytest.mark.e2e` | Phase 7 impl; paid-call gate |
| **R-L2-gate (embedding-model + corpus)** | the §6 L2 vendor gate — choose the embedding model (in-process sync vs async API incl. Ollama) + author the trained per-workload-class corpus. **This gate is resolved BEFORE the L2 spec/impl shape is known.** | operator/vendor decision + corpus artifact | gate — surface, don't auto-fire |
| **R-spec-2 / R-impl (L2)** | **conditional on the gate (D2):** *L2-sync* (in-process model) → **no spec amendment** — bind a k-nearest sync `LayerDecisionFn` at `EMBEDDING` in `route()`; *L2-async* (API/Ollama) → Class 1 §2.1 re-decomposition mirroring L3 at `infer()`. | (conditional) CP spec amendment + clearance **or** impl-only | design-substrate edit → clearance marker (if async) / Phase-7 impl (if sync) |

**Design forks to file** (Class 1, at R-spec-1 authoring): (a) the C-CP-02 §2.1 re-decomposition shape (router resolves at `infer()`) — the contract-section vs new-sub-section choice; (b) **L2 local-vs-remote** is resolved at the L2 vendor gate, not a spec fork. No *defect* fork is owed — D1/D2 confirm no spec *contradiction* (the §2.1 pseudocode predates the `route()`/`infer()` decomposition; Reading B is a faithful re-expression of the same layered intent across that split, not a reversal).

---

## §8 Nameable tensions + disposition (§10.9)

The fork doc (`class_2_fork_llm_as_router_layer3_contract_shape_vs_defer.md` §5) named a genuine **C1 ⊥ C11 ⊥ C9** tension. Each leg of it is now resolved by a standing decision or a committed invariant — so **no design-time operator gate survives, and no council convening is warranted** (the §10.9 nameable-tension discriminator: a tension that a committed constraint already forecloses routes to probe-resolution, not convening):

- **C1 routing-intelligence ("land all units" — wants the layers built) ⊥ C11 operator-loop/cost (no live LLM call on the 200 ms hot path for zero present behavior).** → **Resolved by the standing FULL-SPEC directive** (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`, 2026-06-12), which postdates + reverses the 2026-06-11 confirm-defer. Build is directed; the cost/latency concern is honored by deferring the *live paid binding* to a vendor gate (§6) — the capability is built + mock-exercised without adding a hot-path paid call until the operator binds a model.
- **C9 reliability/determinism (Reading A erodes §5.3.3; Reading B preserves it).** → **Probe-resolved** by the committed ADD §5.3.3 boundary + §2.2's per-layer classification: Reading B for L3 (D1). The L2 *contract shape* is NOT pre-decided here — it is conditional on the gated embedding-model choice (sync→`route()`/no-fork, async→Reading B), determined at the L2 vendor gate (D2/§6). `[[probe-resolves-fork-prescribed-council]]`.

The one residual genuinely-operator decision — **which** router/embedding model to bind + whether to author the corpus + paid-call authorization — is a **downstream vendor/paid-call gate** (§6), surfaced at the R-impl legs, not a design-time gate.

---

## §9 Verification, confidence, open operator input

**Confidence:** `[HIGH]` on the grounded state (§1 — every row read at HEAD), the L3 Reading B decision (§2 — the fork doc + the `infer()` docstring + §2.2 converge), and the L2 *discriminator* (§3 — §2.2 classifies embedding deterministic-modulo-corpus; the sync/async split turns on the embedding-projection model's I/O). **No confidence is asserted on WHICH L2 path is taken — it is deliberately left conditional on the gated embedding-model choice (§6), and given the committed async-SDK stack the L2-async/Reading-B path is at least as likely as L2-sync/no-fork.** `[SPECULATIVE]` on nothing load-bearing.

**Open operator input (all downstream of this design — none blocks it):**
1. **L3 router-model + prompt + paid-call auth** (R-impl-2 vendor gate, §6) — surfaced at impl, never auto-fired.
2. **L2 embedding model (local-sync vs remote-async → drives D2's path) + the trained corpus + (if remote) API auth** (L2 vendor gate, §6).

**Decorrelated review:** advisor (pre-substantive: caught the L2 probabilistic-vs-async conflation → §3/§5/§8 corrected; pre-done: caught the L2-no-fork stack lean — the embedding *projection* (step 1) is the sync/async determinant, not the always-local k-NN search, and the stack-native Ollama embedding is async → recommendation made neutral, R-spec-1 barred from presuming no-fork) + out-of-family **Codex** (2 [P2], both applied: (1) the posture line no longer claims this PR authors the roadmap/dashboard — that is the post-merge §12.2 refresh; (2) `RoutingDecisionTrace` is a frozen `extra="forbid"` 4-field carrier → the router rationale emits via the §2.2 `routing.binding_rationale` span attr, or a carrier amendment is a named R-spec-1 deliverable — §2 trace-carrier note). **Class-3 informational** (§5): ADD §5.3.3 verbatim body not in-repo — noted for a future ADD re-table, non-blocking.

---

*Filing footer — Artifact: `.harness/r-fs-1-r-routing-intelligence-design-v1.md`; Arc: R-FS-1 child arc R (routing intelligence) design; Posture: mode-agnostic; X-AL-3: trivially clean (zero `design-substrate/**` or `harness-*/src` edit). Decisions: D1 (L3 LLM_AS_ROUTER → Reading B, resolve at the already-async `infer()`; Reading A foreclosed by ADD §5.3.3 + §2.2 "Probabilistic"; the router rationale emits via the §2.2 `routing.binding_rationale` span attr — the frozen 4-field `RoutingDecisionTrace` is NOT widened unless R-spec-1 elects a carrier amendment), D2 (L2 EMBEDDING — path NOT pre-decided: conditional on the gated embedding-model choice; discriminator is the embedding-projection model's I/O (sync in-process → `route()`/no-fork; async API incl. the stack-native Ollama → Reading B), NOT probabilistic-ness and NOT the always-local k-NN search; given the committed async-SDK stack, no-fork is not the default). Vendor gates (§6): L3 router-model + prompt + paid-call; L2 embedding-model + corpus. Decorrelated review: advisor (caught the L2 projection-vs-search conflation + the L2-no-fork stack lean → §3/§5/§8 corrected, recommendation made neutral; pre-done) + out-of-family Codex (2 [P2] applied: roadmap/dashboard not claimed as this PR's scope; the `RoutingDecisionTrace` frozen-4-field carrier note). Spine: `.harness/beyond-mvp-capability-boundary-ledger.md` + `.harness/r-fs-1-remaining-arcs-grounding-sweep-v1.md`. Directive: `[[feedback-full-spec-beyond-mvp-nothing-deferred]]`.*
