# Class 2 (in-execution, FULL-SPEC-pre-authorized) — `B-L2-FALLBACK-COMPOSITION`: layered routing composes with the C-RT-16 fallback chain (route-once-then-fallback)

**Status:** ✅ BUILT (2026-06-20) — the registered B-L2-EMBEDDING-ACTIVATION follow-on (surfaced by its Codex [P2] round-2). **Bundled-absorption: a SMALL spec leg (runtime §14.6.1, v1.64 → v1.65) + clearance marker + this build-record** — co-lands `harness-cp/src` (factor `resolve_routing_trace`) + `harness-runtime/src` (the inner `resolve_routed_binding` SELECTION + the faithful inner `dispatch` + the wrapper `routing_resolver` + stage-5 threading + the retired guard) + by-execution tests.
**Filed at:** R-FS-1 standalone arc `B-L2-FALLBACK-COMPOSITION` (the composition that makes `routing_activation` production-reachable alongside fallback chains).
**Locus:** `harness-cp/.../routing_core_surface.py` (`resolve_routing_trace` factored from `infer`) + `harness-runtime/.../lifecycle/llm_dispatch.py` (`resolve_routed_binding` + the faithful `_declarative_echo` + the retired factory guard) + `harness-runtime/.../lifecycle/retry_breaker_fallback.py` (`RoutedBindingResolver` Protocol + `routing_resolver` field + `_effective_chain(routed=)` + `_augment_primary`) + `bootstrap/stage_5_loop_init.py` (thread `routing_resolver=bare_dispatcher.resolve_routed_binding`) vs cleared `Spec_Harness_Runtime` **§14.5.3 + §14.6** + `.harness/beyond-mvp-capability-boundary-ledger.md`.
**Classification:** Class 2 (in-execution; FULL-SPEC directive 2026-06-12 pre-authorizes the build). **NO operator gate** (see below).
**Routing:** Bundled-absorption (the #667 B-LAYER-BUDGET-OVERRIDE shape — a small additive spec leg documenting a composition the cleared invariants prescribe; clearance marker filed).

## The gap (the silent fallback-defeat)

B-L2-EMBEDDING-ACTIVATION (#669) made the **inner** C-RT-15 dispatcher able to OVERRIDE `binding.model_binding`: under `routing_activation`, the inner's DECLARATIVE layer declines on a manifest-miss and `route()` falls through to the EMBEDDING classifier (then L3), picking a DIFFERENT model. But the C-RT-16 `RetryBreakerFallbackDispatcher` drives fallback by re-binding `binding.model_binding` to each successive chain candidate and re-invoking the inner per attempt (§14.6 step 4). So under `routing_activation` the inner **re-routed on every fallback re-invocation** and re-picked the SAME embedding/router candidate, IGNORING the wrapper's rebound fallback candidate → the chain never advanced. The #669 interim guard detect-then-refused (`LLMDispatchBindError`) a `routing_activation` + non-empty `fallback_chains` deployment until this arc.

This is exactly the **two-authority-at-dispatch** anti-pattern §14.5.3 forecloses: "indexing the per-role model at the inner too would create TWO authorities (wrapper candidate vs inner override) and silently defeat fallback for role-routed branches."

## What was built (route-once-then-fallback-the-chain)

The layered-routing decision is now made **ONCE at the C-RT-16 wrapper** (NOT re-run per attempt) and SEEDS the wrapper's PRIMARY candidate; the inner reverts to FAITHFUL. This is the U-RT-114 §14.5.3 chain-augmentation pattern (per-role MODEL primary) applied to the layered-routing selection:

1. **SELECTION factored** — `harness_cp.routing_core_surface.resolve_routing_trace`: the route()+L3 selection half of `infer` (returns `(RoutingDecisionTrace, binding_rationale)`, no dispatch). `infer` now = `resolve_routing_trace` + dispatch (behavior-preserving — the 19 routing_core_surface tests pass unchanged).
2. **`RuntimeLLMDispatcher.resolve_routed_binding`** — runs the layered routing (DECLARATIVE-decline → EMBEDDING → L3) and returns the routed `ModelBinding`, or **`None`** when (a) `routing_activation` is off (default → byte-identical), (b) a DETERMINISTIC binding governs (per-step `override_applied` / per-role `per_role_bindings` / model-bearing per-workload override — DECLARATIVE would echo `binding.model_binding` == the existing chain primary), or (c) no EMBEDDING classifier + no L3 router.
3. **The inner `dispatch` reverts to FAITHFUL** — `_declarative_echo` is a pure echo of `binding.model_binding`; the EMBEDDING classifier is consulted ONLY by `resolve_routed_binding`. So the inner dispatches the wrapper's rebound candidate exactly once per attempt (§14.6 restored).
4. **The wrapper seeds the routed primary** — stage-5 hands the wrapper a DIRECT handle to the bare dispatcher's `resolve_routed_binding` (NOT through the HITL `inner`, which is two layers above the routing-capable dispatcher — the advisor's load-bearing catch). The wrapper resolves it ONCE per step; a non-`None` routed model becomes the chain PRIMARY via the SAME `_augment_primary` augmentation U-RT-114 uses (routed primary + the original stage chain as the deduped §4.2 tail).
5. **The interim guard is RETIRED** — the factory now ADMITS `routing_activation` + non-empty `fallback_chains` (the composition landed).

**Precedence (mutual-exclusivity):** a per-role binding IS a deterministic binding, so `resolve_routed_binding` returns `None` when one is present → the per-role augmentation governs. Precedence = deterministic binding > layered routing > stage chain; routing fills ONLY the no-deterministic-binding gap.

## Why a spec leg (NOT no-leg) + NO operator gate + NO council (advisor-decomposed)

- **Spec leg (§14.6.1, the #667 shape — NOT the #653/#669 no-leg shape):** §14.6 step 2/4 says "the first candidate is `binding.model_binding`; the wrapper invokes the inner exactly once per attempt with a rebound binding". The *principle* (wrapper owns selection; inner faithful) is cleared, but **where the layered-routing decision composes** with that chain is a genuine composition detail §14.6 does not literally settle (routed-primary + original-chain-tail vs routed-set-as-chain). The advisor steered: land it as a small additive §14.6.1 + clearance marker, mirroring B-LAYER-BUDGET-OVERRIDE's §2.5.3.
- **NO operator gate** — additive correctness that SACRIFICES no committed invariant; it RESTORES the §14.6 inner-is-faithful contract that `routing_activation` had broken. Opt-out `routing_activation=False` is byte-identical (contrast B4-Slice-4's §14.5.3 inv 2, which DID gate because the invariant FORBADE the change — here the invariant PRESCRIBES it).
- **NO council** — the one nameable cross-domain tension (routing-layer-home vs reliability-composition: routing decision at the inner routing surface vs the fallback wrapper?) is FORECLOSED by the cleared §14.5.3 / §14.6 invariants (the wrapper owns selection; the inner faithfully dispatches the rebound candidate) → probe-resolved (`[[probe-resolves-fork-prescribed-council]]`); advisor + out-of-family Codex per the §10.9 discriminator.

## Non-vacuity (the two load-bearing properties, witnessed separately — advisor catch #3)

The deliverable is non-vacuity, and the two properties are witnessed SEPARATELY (a-without-b would not prove the re-route was killed):

- **(a) the chain ADVANCES under routing** — `test_b_l2_routed_primary_fails_then_fallback_advances`: a routed PRIMARY that fails → the wrapper dispatches the NEXT chain candidate (the exact bug). Plus the FULL-CHAIN witness `test_b_l2_full_chain_routed_primary_reaches_provider_and_chain_advances` (the REAL `resolve_routed_binding` + REAL wrapper + REAL inner + a recording provider: routed haiku tried first, fails, advances to stage-primary opus at the provider boundary — `[[full-chain-witness-not-half-proofs]]`).
- **(b) routing happens ONCE, not per attempt** — `test_b_l2_routing_resolved_once_not_per_attempt`: a counting resolver is called EXACTLY ONCE even though the wrapper advances through 3 inner dispatches (the §14.5.3 no-two-authority invariant).
- Plus: the precedence/collision (`test_b_l2_resolver_none_falls_back_to_per_role_augmentation`), the zero-blast-radius default (`test_b_l2_no_resolver_byte_identical_stage_chain`), and the relocated `resolve_routed_binding` SELECTION unit tests (manifest-miss → routed; off / deterministic → None) in `test_lifecycle_llm_dispatch.py`. The #669 guard test is FLIPPED into `test_factory_admits_routing_activation_with_fallback_chains`.

## Scope boundary (registered follow-on)

`B-L2-ROUTING-SPAN-LAYER-ATTRIBUTION` — under wrapper-routing the inner's `gen_ai` span carries the DECLARATIVE-echo `routing.layer`, not the real EMBEDDING/L3 layer the wrapper used (a minor observability fidelity gap; production-dormant until a second provider; the routed model itself is faithfully dispatched). `routing_activation` remains production-dormant behind the operator-creds second-provider deployment gate.

## Gates

whole-workspace pyright 0/0/0 · ruff (incl. format) · harness-cp 1093 passed + 1 xfailed · harness-runtime 1980 passed / 13 skipped (non-e2e) · harness-cxa 28 · harness-core 26 · semantic overlay 31/31 · CI blocking green (to confirm on PR) · X-AL-3 green (clearance marker present).
