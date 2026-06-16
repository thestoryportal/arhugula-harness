---
artifact: design-substrate/Implementation_Plan_Harness_Runtime_v2_48.md
version: v2.48
cleared_at: 2026-06-16T00:00:00-06:00
clearance_type: Phase-6-plan-amendment (atomic-unit decomposition of the R Layer-3 LLM_AS_ROUTER runtime surfaces — impl-against-cleared-spec post-CP-spec-v1.36 §2.5; R-FS-1 R-plan-1; runtime-axis leg)
back_reference:
  - .harness/r-fs-1-r-plan-decomposition.md (the R-plan-1 decomposition summary + coverage matrix + DAG + the load-bearing `ProviderDispatchFn` type-ripple co-land finding + the production-`router=None` inertness reconciliation)
  - design-substrate/Spec_Control_Plane_v1_36.md §2.5.4 (the span-owning dispatch-seam `binding_rationale` carrier) + §2.5.5 (the R-impl-1 runtime binding) + §2.5.1 (the terminal-leaf invariant)
  - .harness/clearance/Spec_Control_Plane-v1_36-cleared-2026-06-16.md (the R-spec-1 clearance marker)
  - design-substrate/Implementation_Plan_Control_Plane_v2_37.md (the sibling CP leg — U-CP-99/100; the R aggregate cross-axis DAG home at §3.8)
  - design-substrate/Implementation_Plan_Harness_Runtime_v2_47.md (the delta base — preserved verbatim per delta-only-plan-chain; 0 prior unit-body lines changed, full-file diff verified)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - implementation-planner discipline (grounded at HEAD 79ddde6) — produced 2 NEW runtime units: U-RT-132 (rationale-consume + span emission — `_provider_dispatch`/`_invoke_provider` additively accept the `binding_rationale` carrier [the Protocol-match]; the `llm.inference` span emitter at `llm_dispatch.py:649-655` sets `routing.binding_rationale` from the threaded rationale when present, else the existing `f"{layer}:{candidate}"` derivation) + U-RT-133 (router-injection binding — thread an injected `RouterResolutionFn` into `infer(router=…)` at `llm_dispatch.py:547-553`; production `router=None`; mock = test fixture; the real router binds at R-impl-2). +§2.7 units + §3.1e R DAG delta + §4.1e coverage + §6 O-RT-8. ZERO spec amendment, X-AL-3-clean (the §2.5 contract cleared at CP v1.36; the carrier is an additive optional param; the cross-axis edges run runtime→CP).
  - pyright spike (load-bearing co-land verification) — confirmed the runtime `_provider_dispatch` closure (`llm_dispatch.py:521`) goes pyright-unassignable to the Protocol-ized `ProviderDispatchFn` until it adds the defaulted `binding_rationale` param → U-RT-132 co-lands with CP U-CP-99/100 in the R-impl-1 arc.
  - harness-adversarial-reviewer Phase-7 pre-merge review (dedicated agent adopting the SKILL) — (recorded at the PR)
  - out-of-family Codex review (just codex-review, $0 subscription, decorrelated) — caught (2 rounds → converged) the runtime mock-router e2e buildability [P2]: the binding site's hardcoded `_declarative_echo` (`llm_dispatch.py:496-499`) always resolves, so the spec-§2.5.5 runtime proof needs a **test-only `layer_decisions` injection seam** on `RuntimeLLMDispatcher` (defaulting to production values → production byte-identical). Round 1 flagged the unbuildable through-dispatcher e2e; round 2 flagged that punting the proof entirely to CP under-satisfies the spec's runtime-binding requirement → the seam reconciles both. Non-test production L3 reachability registered forward (R-300-second-provider, §6 O-RT-8 item 2).
  - advisor (transcript-aware) — pre-substantive: surfaced the production-`router=None` inertness reconciliation (§2.5.5 "bind a mock at the binding site" vs "inert in production" reconcile only because DECLARATIVE always resolves today → wire `router=None` in production, the mock is a test fixture); verified against the code (`llm_dispatch.py:521-545` `_provider_dispatch` 4-arg closure; `:547-553` infer call; `:649-655` `routing.binding_rationale` = `f"{layer}:{candidate}"` derivation).
supersedes: design-substrate/Implementation_Plan_Harness_Runtime_v2_47.md
superseded_by:
---

# Clearance — `Implementation Plan — Harness Runtime v2.48`

v2.48 is the **runtime-axis leg of R-FS-1 — R-plan-1** — the atomic-unit decomposition of the routing-intelligence **R** sub-program's Layer-3 LLM_AS_ROUTER runtime surfaces, impl-against-cleared-spec post-CP-spec-v1.36 §2.5 (Reading B). **2 NEW runtime units:**

- **U-RT-132** — rationale-consume + span emission (`lifecycle/llm_dispatch.py`): `_provider_dispatch` (`:521-545`) + `_invoke_provider` (`:556+`) additively accept the keyword-only `binding_rationale: str | None = None` carrier (the Protocol-match to the U-CP-99 `ProviderDispatchFn`); the span emitter (`:649-655`) sets `routing.binding_rationale` from the threaded rationale when present, else the existing `f"{routing_trace.layer}:{routing_trace.candidate}"` derivation (the non-router path byte-identical). `[U-CP-100]` cross-axis.
- **U-RT-133** — router-injection binding (`lifecycle/llm_dispatch.py:547-553`): thread an injected `RouterResolutionFn` into the `infer(router=…)` call (**production `router=None`** — the Layer-3 surface stays literally inert in production) + a **test-only `layer_decisions` (+ `router`) injection seam** on `RuntimeLLMDispatcher` (defaulting to the production hardcoded values → production byte-identical) that makes the spec-§2.5.5 runtime mock-router e2e buildable (force-fall-through `layer_decisions` + a mock router → the runtime span shows the router-supplied `routing.binding_rationale`); the bound router is a terminal leaf (direct-dispatch, no re-entry); the real router model + prompt bind at R-impl-2 under the vendor gate. `[U-CP-99, U-CP-100]` cross-axis.

ZERO spec amendment, X-AL-3-clean (the §2.5 contract cleared at CP v1.36; the `binding_rationale` carrier is an additive optional param; the 3 cross-axis edges run runtime→CP — no new primitive). All prior units (U-RT-01..131) byte-identical; v2.47 untouched.

**The load-bearing finding for R-impl consumers — the U-RT-132 ⊕ CP U-CP-99/100 TYPE-RIPPLE CO-LAND (§3.1e / §6 O-RT-8).** Protocol-izing `ProviderDispatchFn` (U-CP-99) with the optional `binding_rationale` kwarg makes the runtime `_provider_dispatch` closure pyright-**unassignable** until it adds the defaulted param — **verified by a pyright spike**. So U-RT-132 + U-RT-133 + CP U-CP-99 + U-CP-100 MUST land in the **same R-impl-1 arc**; a CP-only Protocol-ization PR breaks `just check` on harness-runtime, a runtime-only PR references a Protocol param that does not yet exist. A cross-package type ripple (same shape as B2's co-land pin, different cause — `[[shared-is-shape-change-ripples-cross-axis-field-asserts]]`), NOT a DAG edge (the package direction stays runtime→CP), NOT a fork (the §2.5 contract cleared).

**Production inertness is literal (advisor reconciliation; Class-3, NOT a spec change; §6 O-RT-8 item 2).** §2.5.5's "bind a mock at the binding site" + "inert in production" reconcile only because DECLARATIVE always resolves today. U-RT-133 wires `router=None` in production (literal inertness); the mock is a test fixture; R-impl-2 binds the real router.

**Registered-forward (per FULL-SPEC; §6 O-RT-8).** R-impl-2 vendor gate (real router model + prompt + gated live e2e — surface, don't auto-fire); the router-call's own child `llm.inference` span + cost-bucket → the CA arc.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- The runtime surfaces (U-RT-132/133) co-publish with the CP routing-core surface (CP plan v2.37 U-CP-99/100). See the CP v2.37 clearance marker for the shared R-plan-1 decomposition verifications.
- See `.harness/clearance/README.md` for marker discipline.
