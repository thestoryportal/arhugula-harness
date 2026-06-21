---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.69
cleared_at: 2026-06-21T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-spine-ledger (NO operator gate — change-note-level amendment closing the §14.6.1 scope-boundary + marking B-L2-ROUTING-SPAN-LAYER-ATTRIBUTION BUILT: the routed-primary gen_ai span now reports the real EMBEDDING/L3 routing.layer instead of the DECLARATIVE echo, via a RoutedPrimaryResolution return + a ROUTED_PRIMARY_SPAN_TRACE ContextVar the wrapper publishes for the routed primary only; observability-additive, no selection/dispatch behavior change, no new contract/fail-class/hash)
back_reference:
  - .harness/beyond-mvp-capability-boundary-ledger.md (B-L2-ROUTING-SPAN-LAYER-ATTRIBUTION spine BUILT note)
  - design-substrate/Spec_Harness_Runtime_v1.md (v1.65 — the §14.6.1 scope-boundary this arc closes; B-L2-FALLBACK-COMPOSITION composition contract PRESERVED VERBATIM)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - advisor (full-transcript) — reframed the fork from the read-shape (impl-discretion) to the consumer-existence question; confirmed the §14.6.1 scope-boundary is the genuine consumer + the ContextVar (per-task, fan-out-safe) threading + the routed-primary-only scope
  - standing FULL-SPEC operator directive 2026-06-12 (design back-flow pre-authorized; no operator gate owed)
  - out-of-family Codex review at the impl-diff PR (decorrelated; <pending>)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.69`

v1.69 is a change-note-level additive amendment absorbing the **R-FS-1 standalone arc `B-L2-ROUTING-SPAN-LAYER-ATTRIBUTION`** — the forward arc the §14.6.1 scope-boundary (B-L2-FALLBACK-COMPOSITION, v1.65) explicitly registered. The inner C-RT-15 `gen_ai` span's `routing.layer` now reports the **real EMBEDDING/L3 layer** the C-RT-16 wrapper resolved for the routed PRIMARY, instead of the inner's faithful DECLARATIVE echo (`RoutingLayer.DECLARATIVE == "manifest"`).

**The mechanism (the §14.6.1-named "per-dispatch context").** Under `routing_activation`, the wrapper resolves the layered-routing decision ONCE (route-once-then-fallback) and reverts the inner to FAITHFUL — so the inner re-derived a DECLARATIVE-echo trace and stamped `routing.layer = "manifest"`. The fix: `resolve_routed_binding` now returns a `RoutedPrimaryResolution` carrying the routed `ModelBinding` (unchanged) PLUS the resolving `RoutingDecisionTrace` + binding rationale it previously discarded; the wrapper publishes `(routing_trace, binding_rationale)` on the module `ROUTED_PRIMARY_SPAN_TRACE` ContextVar for the routed-PRIMARY candidate ONLY, and `_invoke_provider` reads it for `routing.layer`/`routing.binding_rationale`. A **ContextVar** (per-task, fan-out-safe — the B-INTERSTEP-PERRUN-ISOLATION v1.64 precedent), NOT a `StepDispatcher` Protocol widening. `routing.provider`/`routing.model` still reflect the actually-dispatched candidate.

**Scope boundary held.** The ContextVar is published only for the routed primary; a chain-selected fallback candidate keeps the faithful DECLARATIVE echo (`"manifest"`), proven by execution.

**NO operator gate / observability-additive.** Selection/dispatch behavior is byte-unchanged (only the span attribution is corrected). No new contract, no new fail-class, no §5.2-hash change (the `RoutedPrimaryResolution` carrier + the ContextVar are `harness_runtime`-internal). **CP spec UNCHANGED** (the resolver + `RoutedBindingResolver` Protocol + `RoutedPrimaryResolution` + the ContextVar are all `harness_runtime`-internal; no `harness_cp` change, no Protocol widening). IS / OD / ADR specs UNCHANGED.

Reviewed during clearance (verified by execution through the REAL wrapper + REAL resolver + recording provider): a routed-primary dispatch → the `chat claude-haiku-4-5` span reports `routing.layer == "embedding"` (not `"manifest"`); routing-off → the span reports the `"manifest"` echo (byte-identical negative control); a failed routed primary → the haiku span reports `"embedding"` while the opus fallback span reports `"manifest"` (the scope-boundary held). pyright 0/0/0; harness-runtime non-e2e 2007 passed; harness-cp 1136 passed; ruff clean.

## Notes

- Phase 7 consumers may rely on this version as canonical after the bundled harness-runtime impl + tests land together (`merge_commit` pinned at the post-merge refresh).
- The capability is production-dormant until a second provider makes routing-among-candidates meaningful (the B-L2-EMBEDDING-ACTIVATION dormancy note is preserved); the v1.69 fix is observability-fidelity for that dormant-but-real capability.
