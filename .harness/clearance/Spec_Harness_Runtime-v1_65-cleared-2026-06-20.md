---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.65
cleared_at: 2026-06-20T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_2_fork_b_l2_fallback_composition.md
  - .harness/beyond-mvp-capability-boundary-ledger.md (B-L2-FALLBACK-COMPOSITION BUILT)
merge_commit: (bundled-absorption PR — B-L2-FALLBACK-COMPOSITION)
reviewer_chain:
  - advisor (full-transcript pre-build — the inner-is-HITL-composer catch, the two-primary-source precedence, the dual non-vacuity properties, the spec-leg classification)
  - out-of-family Codex on the diff (pre-merge)
  - impl-time grounding pass against §14.5.3 + §14.6 cleared invariants
supersedes: Spec_Harness_Runtime-v1_64-cleared-2026-06-20.md
---

# Clearance — `Spec_Harness_Runtime v1.65`

v1.65 adds **§14.6.1** — the layered-routing (`routing_activation`, C-CP-02 §2.2) composition with the C-RT-16 retry/breaker/fallback chain — and marks the registered R-FS-1 follow-on **`B-L2-FALLBACK-COMPOSITION` BUILT**. B-L2-EMBEDDING-ACTIVATION had made the inner C-RT-15 dispatcher able to override `binding.model_binding` under `routing_activation`, but the C-RT-16 wrapper re-binds + re-invokes the inner per fallback attempt, so the inner re-routed every attempt and the chain never advanced (a silent fallback-defeat — the §14.5.3 two-authority-at-dispatch anti-pattern). §14.6.1 documents the fix: the layered-routing decision is resolved ONCE at the wrapper (via the inner's new `resolve_routed_binding` SELECTION surface) and seeds the chain PRIMARY (the U-RT-114 §14.5.3 chain-augmentation pattern); the inner reverts to faithful per §14.6.

This is **impl-to-cleared-invariant** — it RESTORES the §14.6 "the wrapper invokes the inner dispatcher exactly once per attempt with a rebound binding" contract that `routing_activation` had broken, governed by the §14.5.3 "the wrapper owns model-candidate selection" invariant. **NO operator gate** (additive correctness, no committed-invariant sacrifice, opt-out `routing_activation=False` byte-identical). **NO council** (the routing-home-vs-reliability-composition tension is foreclosed by the cleared §14.5.3 / §14.6 invariants → probe-resolved; advisor + Codex per the §10.9 discriminator). The interim B-L2-EMBEDDING-ACTIVATION detect-then-refuse factory guard is RETIRED.

**Caveats for Phase 7 consumers.** v1.65 is purely additive (§14.6.1); §14.5 / §14.5.3 / §14.6 step bodies / §9 / §14.20–§14.23 + all `RuntimeConfig` / `HarnessContext` / `RunResult` fields are PRESERVED VERBATIM. No §5.2-hash change; CP / IS / OD / ADR specs UNCHANGED (`resolve_routing_trace` is a CP-pure additive factoring of `infer`). One registered scope-boundary follow-on: `B-L2-ROUTING-SPAN-LAYER-ATTRIBUTION` (under wrapper-routing the inner `gen_ai` span carries the DECLARATIVE-echo `routing.layer`, not the real EMBEDDING/L3 layer — production-dormant fidelity gap; the routed model is faithfully dispatched).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
