---
artifact: design-substrate/Implementation_Plan_Control_Plane_v2_37.md
version: v2.37
cleared_at: 2026-06-16T00:00:00-06:00
clearance_type: Phase-6-plan-amendment (atomic-unit decomposition of the R Layer-3 LLM_AS_ROUTER resolution surface — impl-against-cleared-spec post-CP-spec-v1.36 §2.5; R-FS-1 R-plan-1; CP-axis leg)
back_reference:
  - .harness/r-fs-1-r-plan-decomposition.md (the R-plan-1 decomposition summary + coverage matrix + DAG + the load-bearing `ProviderDispatchFn` type-ripple co-land finding + the production-`router=None` inertness reconciliation)
  - design-substrate/Spec_Control_Plane_v1_36.md §2.5 (R-spec-1 — the Layer-3 LLM_AS_ROUTER resolution surface, Reading B; cleared #598)
  - .harness/clearance/Spec_Control_Plane-v1_36-cleared-2026-06-16.md (the R-spec-1 clearance marker)
  - .harness/r-fs-1-r-routing-intelligence-design-v1.md D1 (the R-DESIGN Reading-B decision, probe-resolved by ADD §5.3.3 + §2.2 "Probabilistic"; merged #596)
  - design-substrate/Implementation_Plan_Control_Plane_v2_36.md (the delta base — preserved verbatim per delta-only-plan-chain; 0 prior unit-body lines changed, full-file diff verified)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - implementation-planner discipline (grounded at HEAD 79ddde6) — produced 2 NEW CP units: U-CP-99 (R-routing contract types — `RouterResolutionFn` + `RouterResolution` + the `ProviderDispatchFn` Protocol-ization with the additive optional `binding_rationale` kwarg) + U-CP-100 (the `infer()` Layer-3 router-resolution branch — optional `router` param + sentinel→router branch + L3-budget `wait_for` timeout wrap + 4-field trace rebuild + the rationale threaded on the router path only + the four no-regress preserved-raise paths). +§2.7 units + §3.8 R aggregate cross-axis home + §4.6 coverage + §6 O-CP-7. ZERO spec amendment, ZERO new contract ID (§2.5 additively refines C-CP-02; the frozen 4-field `RoutingDecisionTrace` is NOT widened — the rationale rides the dispatch-seam carrier to the C-CP-01 §1.4 span attr).
  - pyright spike (load-bearing co-land verification) — confirmed a legacy 4-arg dispatch closure is NOT assignable to the Protocol-ized `ProviderDispatchFn` once it gains the optional `binding_rationale` kwarg (`error: Missing keyword parameter "binding_rationale"`, reportAssignmentType); the closure WITH the defaulted param is clean → the CP seam change + the runtime `_provider_dispatch` update MUST co-land in one R-impl-1 arc.
  - harness-adversarial-reviewer Phase-7 pre-merge review (dedicated agent adopting the SKILL) — (recorded at the PR)
  - out-of-family Codex review (just codex-review, $0 subscription, decorrelated) — caught (2 rounds → converged) the runtime-sibling mock-router e2e buildability [P2] (runtime v2.48 U-RT-133): the dispatcher's hardcoded `_declarative_echo` always resolves → the spec-§2.5.5 runtime proof needs a test-only `layer_decisions` injection seam (default = production); non-test production L3 reachability registered forward (R-300-second-provider). U-CP-100's direct `infer()` test is the CP-unit behavioral proof (unaffected).
  - advisor (transcript-aware) — pre-substantive: endorsed the 4-unit split as sound + proportionate; surfaced the `ProviderDispatchFn` Protocol-ization cross-package type ripple → the R-impl-1 co-land (verify-don't-assume → the pyright spike); the production-`router=None` inertness reconciliation (mock = test fixture); the carrier-module placement in already-runtime-imported modules (no new cross-axis module edge). Verified against the code (`routing_core_surface.py:117-120` ProviderDispatchFn Callable alias + `:129-192` infer; `cp_shared_types.py:110-130` frozen 4-field trace; `layer_budget.py:72` 200ms L3 budget; `layered_routing_strategy.py:96-98` sentinel).
supersedes: design-substrate/Implementation_Plan_Control_Plane_v2_36.md
superseded_by:
---

# Clearance — `Implementation Plan: Control Plane v2.37`

v2.37 is the **CP-axis leg of R-FS-1 — R-plan-1** — the atomic-unit decomposition of the routing-intelligence **R** sub-program's Layer-3 LLM_AS_ROUTER resolution surface, impl-against-cleared-spec post-CP-spec-v1.36 §2.5 (Reading B). **2 NEW CP units:**

- **U-CP-99** — R-routing contract types + `ProviderDispatchFn` Protocol-ization (`routing_core_surface.py` + `cp_shared_types.py`): the injected async `RouterResolutionFn` resolver + the frozen `RouterResolution` result (`candidate`, `rationale`) + convert `ProviderDispatchFn` from a `Callable` alias to a `Protocol` with the additive keyword-only optional `binding_rationale: str | None = None` (the §2.5.4 rationale carrier). Carrier modules already runtime-imported (no new cross-axis module edge). `(none)` deps.
- **U-CP-100** — the `infer()` Layer-3 router-resolution branch (`routing_core_surface.py`): the optional `router` param + the `route()`-sentinel→router branch + the L3-budget `wait_for` timeout wrap + the rebuilt 4-field trace + the rationale threaded through `dispatch` on the router path ONLY + the four no-regress preserved-raise paths (no-router / L3-budget-exhausted-on-entry / timeout / malformed). `[U-CP-99]`.

ZERO spec amendment, ZERO new contract ID, X-AL-3-clean (§2.5 additively refines C-CP-02; no `RoutingDecisionTrace`/`RoutingLayer` member change; the frozen 4-field trace is NOT widened). All prior units (U-CP-01..98) byte-identical; v2.36 untouched.

**The load-bearing finding for R-impl consumers — the U-CP-99/100 ⊕ U-RT-132 TYPE-RIPPLE CO-LAND (§3.8.3 / §6 O-CP-7).** Protocol-izing `ProviderDispatchFn` with the optional `binding_rationale` kwarg makes every legacy 4-arg dispatch closure pyright-**unassignable** until it adds the defaulted param — **verified by a pyright spike**. So U-CP-99 + U-CP-100 + the runtime `_provider_dispatch` update (U-RT-132) + the `router=` binding (U-RT-133) MUST land in the **same R-impl-1 arc**; a CP-only Protocol-ization PR breaks `just check` on harness-runtime. This is a cross-package type ripple (same shape as B2's co-land pin, different cause — `[[shared-is-shape-change-ripples-cross-axis-field-asserts]]`), NOT a DAG edge (the package direction stays runtime→CP) and NOT a fork (the §2.5 contract is cleared).

**Registered-forward (per FULL-SPEC, nothing dropped; §6 O-CP-7).** The router-call cost-bucket attribution → the CA arc (CP spec §2.5.4 deferral); the R-impl-2 vendor gate (real router model + prompt + gated live e2e — surface, don't auto-fire); Layer 2 EMBEDDING → R-L2-gate (R-DESIGN D2; §2.5.6 silent on L2 by design).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- The CP-package surfaces (U-CP-99/100) co-publish with the runtime binding site + span emitter (runtime plan v2.48 U-RT-132/133). See the runtime v2.48 clearance marker for the shared R-plan-1 decomposition verifications.
- See `.harness/clearance/README.md` for marker discipline.
