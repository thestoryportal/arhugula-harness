# Class 2 Fork — LLM_AS_ROUTER (routing Layer 3): build now (which contract shape) vs confirm-defer

**Status:** ✅ RESOLVED-AS-CONFIRM-DEFER (operator chose **Option C — confirm-defer**, 2026-06-11, AskUserQuestion). LLM_AS_ROUTER (routing Layer 3) is a **documented bounded-residual** — the Layer-3 twin of the Gate-B-deferred Layer-2 EMBEDDING. No CP-spec amendment; `route()` + `LayerDecisionFn` stay byte-unchanged; no router-model bound. **Re-open trigger:** real routing-intelligence traffic + an operator router-model + hot-path-cost decision (then build via **Reading B** — resolve at the already-async `infer()` layer; see §4/§6). The original framing was a Class 2 scoping decision (`Project_Workflow_v1_8.md` §2.7.6 / root `CLAUDE.md` §4.3); a "build" choice would have cascaded to a Class 1 CP-spec amendment, but defer needs none. See §8.
**Filed:** 2026-06-11 · **Posture:** mode-agnostic (back-flow documentation; no `harness-*/src` or `design-substrate/**` edit — those wait on the decision).
**Arc:** R-CC-1 capability-completion program, **arc #6** (`.harness/capability-completion-inventory-v1.md` item #3).
**Authority in tension:** operator **"land all units"** directive (capability inventory §0, 2026-06-11) ⊥ operator **Gate B EMBEDDING-defer** precedent (capability inventory §3, 2026-06-11) — LLM_AS_ROUTER is the Layer-3 structural twin of the Gate-B-deferred Layer-2 EMBEDDING.
**Prior art:** `.harness/r-cl-p1-routing-intelligence-plan.md` (the original DEFER for both EMBEDDING + LLM_AS_ROUTER); `.harness/class_2_fork_engine_durable_resume_no_production_producer.md` (arc #3, same build-vs-defer shape).
**Grounded at HEAD `643f4a8` by direct read this session** (cites resolved, not recalled).

---

## 1. What the arc framed it as, and the assumption it rested on

> Capability inventory item #3: *"A faithful router-model layer makes an **async** call, but `infer()`/`route()` (U-CP-03/U-CP-05) are **cleared sync contracts**. Widening them = Class 1 fork → design back-flow (X-AL-3). Then bind a router model (impl-discretion)."* — Disposition: *"BUILD (design-fork first) if pursuing full routing intelligence."*

That framing is inherited verbatim from `.harness/r-cl-p1-routing-intelligence-plan.md` §2 (2026-06-10), which dispositioned LLM_AS_ROUTER as **DEFER — documented** on the premise that *both* `route()` (U-CP-05) **and** `infer()` (U-CP-03) are sync cleared contracts a faithful router would have to widen.

**Grounding at HEAD falsifies one load-bearing half of that premise** (the re-grounding discipline, `[[subagent-landscape-reports-need-regrounding]]`): `infer()` is **already async**.

## 2. Grounded state of the world (verified by direct read at HEAD)

| Surface | At HEAD | Cite |
|---|---|---|
| `infer()` | **`async def`** — already async; composes `route()` + an injected async `dispatch` callable + response materialization (R-300 activation lifted the v1.6 stub) | `harness-cp/src/harness_cp/routing_core_surface.py:129` |
| `route()` | **sync** — `def route(...) -> RoutingDecisionTrace`; docstring: *"Deterministic given inputs."* | `harness-cp/src/harness_cp/layered_routing_strategy.py:62` |
| `LayerDecisionFn` | **sync** — `Callable[[InferenceRequest, RoutingManifest], "str | None"]`; called synchronously at `decision_fn(request, manifest)` | `layered_routing_strategy.py:51` + `:87` |
| Bound decision-fns (runtime) | **only `{RoutingLayer.DECLARATIVE: _declarative_echo}`** — EMBEDDING + LLM_AS_ROUTER have **no** decision-fn, so `route()` skips them (`layer_decisions.get(layer) is None → continue`) and falls through | `harness-runtime/.../lifecycle/llm_dispatch.py:533` + `layered_routing_strategy.py:84-86` |
| LLM_AS_ROUTER budget | `LayerBudget(layer=RoutingLayer.LLM_AS_ROUTER, time_budget_ms=200)` — a 200 ms hot-path budget already reserved | `harness-cp/src/harness_cp/layer_budget.py:72` |

**Consequence: no behavior is missing today.** DECLARATIVE manifest routing resolves all production traffic; EMBEDDING + LLM_AS_ROUTER cleanly fall through (the §2.2 spec invariant — each call resolves at the cheapest layer that can resolve it). This is the same "clean fall-through, nothing missing" state the operator accepted for EMBEDDING at Gate B.

## 3. What the spec actually mandates (the discriminator for Reading B)

C-CP-02 §2.1 (full text in `Spec_Control_Plane_v1_2.md` base, preserved verbatim through v1.3 → head `Spec_Control_Plane_v1_31.md` per the delta-only chain) defines routing as a **single resolution function**:

```
on_llm_call(call_site_context) -> RoutingBinding:
  Layer 1 — Declarative manifest binding ... else fall through to Layer 2.
  Layer 2 — Embedding-classifier dispatch ... else fall through to Layer 3.
  Layer 3 — LLM-as-router: Invoke router model with call_site_context + candidate-set
            summary. Router emits provider + model selection plus rationale.
```

§2.2 classifies `llm_as_router` as **"Probabilistic (router-internal LLM call); 50–200 ms latency."** §2.4 binds each layer to a per-layer time budget. *Deferred to implementation discretion:* "specific router model binding (Haiku-class typical per cost discipline)" + the router prompt content.

**The spec puts the router LLM call *inside* the layered resolution function.** The Phase-7 impl decomposed `on_llm_call` into sync `route()` (deterministic layer selection) + async `infer()` (route + dispatch) — faithful *while Layer 3 is unbound*, because the only bound layer (DECLARATIVE) is deterministic. Binding a faithful Layer 3 forces a contract-shape decision, because a router LLM call cannot live inside today's sync `route()`.

## 4. The three readings (corrected by the grounding above)

| Reading | Where the router LLM call lives | Cleared-contract blast radius | Determinism boundary (ADD §5.3.3) | Verdict |
|---|---|---|---|---|
| **A — widen `route()`** | Make `LayerDecisionFn` + `route()` **async**; Layer 3 resolves inside `route()` exactly as §2.1 draws it | **Large** — every `LayerDecisionFn`, every `route()` caller, the U-CP-05 cleared contract | **Eroded** — a probabilistic LLM call moves *into* `route()`, which the docstring + ADD §5.3.3 designate the deterministic outer layer (`infer()` is "the probabilistic core") | Faithful to §2.1 literal shape, but breaks the determinism property `route()` advertises. **Class 1 spec amendment.** |
| **B — resolve at `infer()`** | `route()` stays sync and returns the existing LLM_AS_ROUTER fall-through sentinel (empty candidate, `layered_routing_strategy.py:96-101`); the **already-async `infer()`** detects "no deterministic candidate" and makes the async router call via a new injected async router callable (mirroring `dispatch`), producing the `routing.layer = "llm_as_router"` trace there | **Smaller** — additive async branch in the already-async `infer()` + one new injected callable; `route()` + `LayerDecisionFn` byte-unchanged | **Preserved** — the LLM call stays at `infer()`, the boundary already designated probabilistic | **Does NOT dissolve the gate** (advisor): it *relocates* §2.1's layered-resolution boundary (Layer 3 leaves the resolution function; the trace is produced at `infer()`, not `route()`). Still a **Class 1 spec amendment** — smaller blast radius, but a structural re-decomposition of C-CP-02 §2.1. |
| **C — confirm-defer** | Nowhere — Layer 3 stays unbound, falls through | **Zero** | **Intact** | The Layer-3 twin of the Gate-B-deferred EMBEDDING (#7). No behavior missing; honors `[[grounding-reveals-claude-closeable-slice-close-honestly]]` (ratified-DEFER sibling → confirm-don't-rescue). Re-open trigger = real routing-intelligence traffic + an operator router-model + cost-on-hot-path decision. |

## 5. The genuine cross-domain tension (why this is the operator's call, not a mechanical pick)

- **C1 routing-intelligence / "land all units"** (*wants* a faithful Layer 3 built — the capability-completion directive) ⊥ **C11 operator-loop / local-first + cost** (*wants* no live LLM call added to the 200 ms routing hot path, no new paid-call / latency boundary for zero present behavior) ⊥ **C9 reliability / determinism boundary** (Reading A erodes the ADD §5.3.3 deterministic-outer property; Reading B preserves it).
- **The EMBEDDING precedent is the decisive prior.** LLM_AS_ROUTER differs from EMBEDDING in one way that *helps* (a router model already exists among the bound providers — no corpus to author, unlike EMBEDDING's missing trained corpus) and one way that's *identical* (no behavior missing today; clean fall-through). The operator already faced this exact "no behavior missing, needs a model + config" question for the Layer-2 sibling and chose **defer with a re-open trigger**. Whether the "land all units" directive is intended to override that precedent for the Layer-3 sibling is genuinely the operator's to decide — it is not derivable from the code or the committed constraints.

## 6. Options

| # | Option | What it builds | Cost / honesty |
|---|---|---|---|
| **C (honest default)** | **Confirm-defer** — LLM_AS_ROUTER stays a documented bounded-residual, the Layer-3 twin of EMBEDDING (#7). | No build. Re-open trigger = real routing-intelligence traffic + operator router-model + hot-path-cost decision. | Honest given no-behavior-missing + the Gate-B sibling precedent; zero blast radius. Advances arc #6 to the next forward item. |
| **B** | **Build at the `infer()` layer** (if building). `route()` returns the LLM_AS_ROUTER sentinel; `infer()` makes the async router call via an injected async router callable; trace produced at `infer()`. | Class 1 design-fork-first: CP-spec amendment re-decomposing C-CP-02 §2.1 (Layer 3 resolves at the call surface, not inside `route()`) + clearance, then impl + a router-model binding + router prompt (impl-discretion) + tests. Smaller blast radius; preserves the determinism boundary. | The recommended **build** path if the directive intends build. |
| **A** | **Build by widening `route()`** to async (literal §2.1 shape). | Class 1 design-fork-first: widen the cleared U-CP-05 `route()` + `LayerDecisionFn` to async + clearance, then impl + router-model + tests. | Faithful to §2.1's literal drawing but breaks `route()`'s deterministic property + ADD §5.3.3 boundary; largest blast radius. **Not recommended** even if building. |

## 7. Recommendation

This is a genuine scoping decision and is surfaced to the operator via `AskUserQuestion`. **Recommended lead: Option C (confirm-defer)** — it is the honest default given (a) no behavior is missing today, (b) the operator's own Gate-B defer of the Layer-2 EMBEDDING sibling on the same "no behavior missing, needs a model + config" reasoning, and (c) a router-model binding adds a live LLM call + latency/cost on the 200 ms routing hot path for a capability with no present consumer. **If the "land all units" directive is intended to override that precedent and build routing intelligence now, the recommended build path is Option B** (resolve at the already-async `infer()` layer: smaller cleared-contract blast radius than Reading A and it preserves the ADD §5.3.3 determinism boundary), executed design-fork-first as a Class 1 CP-spec amendment.

**Process note (CLAUDE.md §12.4.1, no-parking):** surfacing this gate is not session-done. After the gate is recorded, the parallel lane (`.harness/capability-completion-inventory-v1.md` items #9/#10/#11) is **grounded**, not assumed Claude-closeable. ⚠️ Grounding this session reclassified two of the three (see §8): **#10 `RunResult.cost_attribution` and #11 HITL OQ-6 are confirm-deferred** (#10 ratified-bounded by R-CL-P5; #11 producer-gated — `on_timeout` has zero non-test callers), and the inventory's "#10 closes an R-CL-P3 sub-part" is **corrected** (that sub-part is bounded, not closeable). **The surviving genuine `[C-now]` is #9** P3 redaction collector-boundary proof (Phase-7 e2e; infra at `deploy/self-hosted-local/`) — driven as the next arc.

---

## 8. Resolution (2026-06-11)

**Operator chose Option C — confirm-defer** (AskUserQuestion, recommended option). Rationale ratified: no behavior is missing today (DECLARATIVE resolves all production traffic; Layer 3 cleanly falls through), the decision mirrors the operator's own Gate-B defer of the Layer-2 EMBEDDING sibling on identical reasoning, and a faithful Layer 3 would add a live router-model LLM call + latency/cost on the 200 ms routing hot path for a capability with no present consumer.

**Disposition:**
- LLM_AS_ROUTER stays a **documented bounded-residual** (Layer-3 twin of EMBEDDING #7). No build; no design-substrate edit; `route()` / `LayerDecisionFn` / U-CP-05 byte-unchanged.
- **Re-open trigger:** real routing-intelligence traffic **and** an operator decision to bind a router model + accept the hot-path cost/latency. On re-open, build via **Reading B** (resolve at the already-async `infer()` layer — smaller cleared-contract blast radius than Reading A; preserves the ADD §5.3.3 determinism boundary).
- **Durable stale-carry correction recorded** (independent of the defer): `infer()` is async at HEAD; any future re-open must NOT re-inherit the r-cl-p1 doc's "infer() is sync" premise. Propagated to `.harness/r-cl-p1-routing-intelligence-plan.md` (LLM_AS_ROUTER row) + `.harness/capability-completion-inventory-v1.md` (item #3).
- **Arc #6 advances** to the parallel Claude-closeable lane (inventory #9/#10/#11) per the §7 process note — not session-done at this gate.
