# R-FS-1 R-plan-1 — Layer-3 LLM_AS_ROUTER Resolution Surface Atomic-Unit Decomposition

**Authored:** 2026-06-16 · **Posture:** design-phase (authors `design-substrate/**` plan files + `.harness/**` companions; X-AL-3-clean — design-substrate edit + clearance markers present). · **Arc:** R-FS-1 child arc **R** (routing intelligence), leg **R-plan-1** (FROZEN order `B1✅→B3✅→E✅→B2✅→R→B4→CA→B5→B6→B7→M`; within R: `DESIGN✅→spec-1✅→plan-1→impl-1 mock→impl-2 vendor-gate→L2`).

**Authority:** CP spec **v1.36 §2.5** (the Layer-3 LLM_AS_ROUTER resolution surface — Reading B; cleared #598, marker `.harness/clearance/Spec_Control_Plane-v1_36-cleared-2026-06-16.md`) + `.harness/r-fs-1-r-routing-intelligence-design-v1.md` **D1** (Reading B probe-resolved, merged #596) + R-FS-1 §5.0 full-spec directive (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`).

**Companion to:** CP plan **v2.37** (U-CP-99/100) + runtime plan **v2.48** (U-RT-132/133).

---

## §0 — What R-plan-1 is

R-plan-1 decomposes CP spec v1.36 §2.5 (the Layer-3 LLM_AS_ROUTER resolution surface — Reading B: the router call resolves at the already-async `infer()`, not inside sync `route()`) into **4 atomic units across 2 packages** — the §2.5 "three additive seam refinements + one binding requirement" mapped to CP contract types + the `infer()` branch + the runtime consume/inject. **SPEC→PLAN only** — no `harness-*/src` edit; the impl lands at R-impl-1 (mock router, NO paid call) + R-impl-2 (vendor-gated real router).

## §1 — The keystone homing facts

- The **routing-core surface** — the `infer()` call surface, the `ProviderDispatchFn` seam, the new `RouterResolutionFn` type (`harness-cp/src/harness_cp/routing_core_surface.py`) + the `RouterResolution` result model (`cp_shared_types.py`) — is **`harness-cp`** (U-CP-99/100, CP plan v2.37). Both carrier modules are **already runtime-imported** (no new cross-axis module edge).
- The **runtime LLM-dispatch path** — the `RuntimeLLMDispatcher._provider_dispatch` closure, the `infer()` binding site, the `_invoke_provider` `llm.inference` span emitter (`harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py`) — is **`harness-runtime`** (U-RT-132/133, runtime plan v2.48).
- The aggregate R cross-axis DAG home is **CP plan v2.37 §3.8**.

## §2 — Unit list

### CP plan v2.37 (2 NEW units — U-CP-99/100)

- **U-CP-99** — R-routing contract types + `ProviderDispatchFn` Protocol-ization (`(none)` deps). `RouterResolutionFn` (async injected resolver, in `routing_core_surface.py` beside `ProviderDispatchFn`) + `RouterResolution` (frozen 2-field `candidate`/`rationale` model, in `cp_shared_types.py` beside `RoutingDecisionTrace`) + convert `ProviderDispatchFn` from a `Callable` alias to a `Protocol` with the additive keyword-only optional `binding_rationale: str | None = None`. §2.5.1 + §2.5.4. **The seam-encoding decision §2.5.4 delegated to R-plan-1** (optional kwarg on a Protocol, chosen over a carrier object / adapter).
- **U-CP-100** — the `infer()` Layer-3 router-resolution branch (`[U-CP-99]`). Optional `router` param + sentinel→router branch + the L3-budget `wait_for` timeout wrap + the rebuilt 4-field trace + the rationale threaded through `dispatch` on the router path only + the four no-regress preserved-raise paths. §2.5.2 + §2.5.3.

### Runtime plan v2.48 (2 NEW units — U-RT-132/133)

- **U-RT-132** — rationale-consume + span emission (`[U-CP-100]`, cross-axis). `_provider_dispatch`/`_invoke_provider` additively accept the `binding_rationale` carrier (the Protocol-match); the span emitter (`llm_dispatch.py:649-655`) sets `routing.binding_rationale` from the threaded rationale when present, else the existing `f"{layer}:{candidate}"` derivation. §2.5.4 RT-side.
- **U-RT-133** — router-injection binding (`[U-CP-99, U-CP-100]`, cross-axis). Thread an injected `RouterResolutionFn` into `infer(router=…)` at the binding site (`llm_dispatch.py:547-553`); **production wires `router=None`** (literal inertness); the mock router is a TEST fixture; the real router binds at R-impl-2. §2.5.5 + §2.5.1.

## §3 — Coverage matrix (every cleared §2.5 subsection → unit or disposition)

| CP spec v1.36 §2.5 subsection / surface | Disposition |
|---|---|
| §2.5.1 `RouterResolutionFn` + `RouterResolution` | U-CP-99 |
| §2.5.2 integration semantics at `infer()` | U-CP-100 |
| §2.5.3 budget + fall-through (L3 timeout wrap; terminal-layer exhaustion = preserved raise) | U-CP-100 (AC-level, the 4 no-regress paths) |
| §2.5.4 dispatch-seam `binding_rationale` carrier (CP-side Protocol) | U-CP-99 |
| §2.5.4 dispatch-seam `binding_rationale` carrier (RT-side consume + span) | U-RT-132 |
| §2.5.1 terminal-leaf / no-regress invariant (direct-dispatch, no re-entry) | U-CP-100 (AC-level) + U-RT-133 (binding) |
| §2.5.5 R-impl-1 runtime binding (mock router; production `router=None`) | U-RT-133 |
| §2.5.4 router-call cost-bucket + the router's own child span | REGISTERED forward → CA arc (CP O-CP-7 item 2 / RT O-RT-8 item 3) |
| §2.5.5 R-impl-2 vendor gate (real router model + prompt + gated live e2e) | REGISTERED forward → R-impl-2 (surface, don't auto-fire) |
| §2.5.6 Layer 2 EMBEDDING | OUT of scope (R-DESIGN D2; → R-L2-gate) |

**No silent gap.** Every cleared §2.5 subsection → a unit OR an explicit AC-level / registered-forward / out-of-scope disposition.

## §4 — Aggregate cross-axis DAG (R arc)

Nodes: `U-CP-99` (leaf) → `U-CP-100` → `{U-RT-132, U-RT-133}`. Cross-axis edges (3): U-RT-132 → U-CP-100; U-RT-133 → U-CP-99 + → U-CP-100 — **all runtime→CP** (allowed; harness-runtime imports harness-cp). No CP→RT edge → no CP↔RT cycle. Acyclic; topological order at CP plan v2.37 §3.8.2.

## §5 — The one load-bearing finding (the `ProviderDispatchFn` type ripple)

The §2.5.4 seam-encoding decision delegated to R-plan-1 is resolved here as **Protocol-izing `ProviderDispatchFn`** (a `Callable[[…], Awaitable[…]]` alias cannot express an optional keyword-only param). The consequence is a **cross-package type ripple** — **verified by a pyright spike at plan-authoring**:

```
error: Type "(provider, model, payload, trace) -> CoroutineType[…, int]" is not assignable
       to declared type "ProviderDispatchFn"
    Missing keyword parameter "binding_rationale" (reportAssignmentType)
```

A legacy 4-arg dispatch closure is **not** pyright-assignable to the Protocol once it gains the optional kwarg; the closure WITH the defaulted param is clean. **Consumer set (the ripple):** `infer()`'s `dispatch` param (CP, same package — U-CP-100); the runtime `_provider_dispatch` closure (`llm_dispatch.py:521`, **cross-package** — U-RT-132); 2 CP test closures (`test_routing_core_surface.py:74,77`). **So U-CP-99 + U-CP-100 + U-RT-132 + U-RT-133 MUST co-land in ONE R-impl-1 arc** — a CP-only Protocol-ization PR breaks `just check` on harness-runtime; a runtime-only PR references a Protocol param that does not yet exist. This is a **build-sequencing co-land** (NOT a DAG edge — the package direction stays runtime→CP; the constraint is "land together"), NOT a fork (the §2.5 contract is cleared). Same shape as B2's co-land pin, different cause (`[[shared-is-shape-change-ripples-cross-axis-field-asserts]]`). Full analysis at CP plan v2.37 §3.8.3.

### §5.1 — Production-inertness reconciliation (the U-RT-133 reading)

CP spec v1.36 §2.5.5 says both "bind a mock `RouterResolutionFn` at the runtime binding site" AND "inert in production until R-impl … no router is injected today." These reconcile cleanly only because DECLARATIVE always resolves production traffic today (the L3 sentinel is never reached). U-RT-133 makes "inert in production" **literally** true: production wires `router=None`; the mock router is a **TEST fixture** (the fall-through→router e2e); R-impl-2 binds the real router. This is impl-discretion (the mock model + prompt are the §2.4 vendor deferral), a Class-3 reconciliation — not a spec contract change, no back-flow owed.

## §6 — R-impl sequencing

- **R-impl-1 = ALL FOUR units co-landed (the type ripple) — U-CP-99 + U-CP-100 + U-RT-132 + U-RT-133 — with a MOCK `RouterResolutionFn` (NO paid call).** Three complementary proofs, each sited where the path is exercisable (Codex [P2], both rounds): **(1)** the CP-unit `infer()` branch — a **direct `infer()` test (U-CP-100)**: a DECLARATIVE fn returning `None` forces the `route()` sentinel + a mock router resolves it; **(2)** the runtime span-consume — a direct `_provider_dispatch(binding_rationale=…)` test (U-RT-132); **(3)** the **spec-§2.5.5 runtime mock-router e2e** (U-RT-133) — via a **test-only `layer_decisions` injection seam** on `RuntimeLLMDispatcher` (defaulting to production values, so production byte-identical): inject a force-fall-through `layer_decisions` + a mock router → the runtime `llm.inference` span shows `routing.layer="llm_as_router"` + the router-supplied `routing.binding_rationale`, proving the runtime binding *can* carry a router. The seam is **necessary** because the hardcoded `_declarative_echo` (`llm_dispatch.py:496-499`) always resolves — without it the spec-required runtime proof is unbuildable (Codex round 1) AND moving the proof entirely to CP would under-satisfy the spec (Codex round 2). Plus production `router=None` byte-identical + the four no-regress preserved-raise paths.
- **R-impl-2 = the vendor-gated real-router binding** over the same landed units (a real router model + prompt + a gated `@pytest.mark.e2e`; **surface, do NOT auto-fire** the paid call — free-local Ollama preferred where it suffices). The router-call's own child `llm.inference` span lands here.
- **CA arc** = the router-call cost-bucket attribution (CP §2.5.4 deferral).
- **R-L2-gate → R-spec-2/R-impl (L2)** = Layer 2 EMBEDDING (R-DESIGN D2; conditional on the gated embedding-model choice; sequenced after L3).
- **R-300-second-provider (reachability dependency; Codex [P2]).** R binds the L3 capability at `infer()` (CP-testable at U-CP-100), but production *activation through `RuntimeLLMDispatcher`* needs DECLARATIVE to fall through — at HEAD `_declarative_echo` (`llm_dispatch.py:496-499`) always resolves, so L3 is unreachable through the dispatcher regardless of `router`. Making DECLARATIVE manifest-driven/conditional is the **R-300-second-provider** work (the `:494-495` forward marker). Registered as the reachability forward dependency for L3 production activation — NOT silently assumed; the behavioral proof is sited at the direct `infer()` test per `[[test-bypass-as-runtime-truth-pattern]]`.

## §7 — Files written (this arc)

- `design-substrate/Implementation_Plan_Control_Plane_v2_37.md` (delta over v2.36; +§2.7 U-CP-99/100, +§3.8, +§4.6, +§6 O-CP-7, +§7 footer; v2.36 prior bodies preserved verbatim)
- `design-substrate/Implementation_Plan_Harness_Runtime_v2_48.md` (delta over v2.47; +§2.7 U-RT-132/133, +§3.1e, +§4.1e, +§6 O-RT-8, +§7 footer; v2.47 prior bodies preserved verbatim)
- `.harness/clearance/Implementation_Plan_Control_Plane-v2_37-cleared-2026-06-16.md` + `.harness/clearance/Implementation_Plan_Harness_Runtime-v2_48-cleared-2026-06-16.md`
- `.harness/r-fs-1-r-plan-decomposition.md` (this companion)
- Pointer bumps: root `CLAUDE.md` §2.4 + `.harness/claude-artifact-pointers.md` §2.4 (CP plan head v2_36→v2_37, runtime plan head v2_47→v2_48)
- SPINE ledger entry: the router-call cost-bucket → CA forward item (`.harness/beyond-mvp-capability-boundary-ledger.md`)

---

*Filing footer — Artifact: `.harness/r-fs-1-r-plan-decomposition.md`; Arc: R-FS-1 child arc R, leg R-plan-1; Posture: design-phase; X-AL-3: design-substrate plan edit + clearance markers present. Decorrelated review: implementation-planner discipline (grounded at HEAD, all code cites verified by direct read + a pyright spike for the type-ripple co-land) + advisor (pre-substantive — surfaced the Protocol-ization type ripple → co-land, the production-`router=None` inertness reconciliation, the carrier-module placement) + out-of-family Codex (pre-merge). Companion plans: CP v2.37 + runtime v2.48. Directive: `[[feedback-full-spec-beyond-mvp-nothing-deferred]]`.*
