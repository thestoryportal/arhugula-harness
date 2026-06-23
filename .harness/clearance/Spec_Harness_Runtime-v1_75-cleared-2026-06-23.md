---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.75
cleared_at: 2026-06-23T00:30:00-06:00
clearance_type: Phase-7-absorbed-via-operator-ratified-amendment
back_reference:
  - .harness/r-fs-1-final-closure-plan.md (arc-a)
  - .harness/r-fs-1-arc-a-postjoin-14.23-hollow-finding.md
  - .harness/r-fs-1-b-fanout-output-replay-impl-design.md
  - design-substrate/Spec_Control_Plane_v1_54.md (the paired primary contract)
  - PR for the arc-a bundle (this branch arc-a-postjoin-llm-synthesis)
merge_commit: <filled at merge>
reviewer_chain:
  - C1⊥C9 dyadic council (PR #711) + advisor (two-layer hollow-trap surfacing + coherent-A scope)
  - Operator AskUserQuestion 2026-06-23 — chose A (synthesis + loud disclosure now)
  - spec-writer apply pass (this arc; the runtime half paired with CP v1.54)
supersedes: <none>
superseded_by: <none>
---

# Clearance — `Spec_Harness_Runtime v1.75`

v1.75 marks the v1.74-registered gated arc `B-POSTJOIN-LLM-SYNTHESIS` BUILT — the RUNTIME consumer half, paired with CP spec v1.54 (the primary contract). It adds ONLY the NEW **§14.24 C-RT-33** (`PostJoinSynthesisStepDispatcher`); all of §9 / §14.1–§14.23 + the v1.59–v1.74 narrative are PRESERVED VERBATIM.

**§14.24 C-RT-33.** The runtime dispatcher bound to `StepKind.POST_JOIN_SYNTHESIS` in the stage-5 `StepKindDispatcherRegistry` (under `requires_inference`). It wraps the inner LLM dispatcher (the C-RT-16 `RetryBreakerFallbackDispatcher` chain in the stage-5 `SyncDispatcherFacade` — so the synthesis dispatcher is itself sync); on dispatch it reads the branch-index-ordered `StepExecutionContext.sibling_outputs`, composes them into ONE trailing context `user` message appended AFTER the synthesis step's declared messages (minimal dispatch), and dispatches the composed step through the inner LLM dispatcher. Read-only / effect-free. An unbound dispatcher (provider-free workflow) fails closed via the existing `StepKindDispatcherNotBoundError`.

NO new fail-class, NO §5.2-hash change (the `sibling_outputs` carrier is hash-inert; disclosure rides the CP driver's synthesis step entry), NO `StepDispatcher` Protocol widening (the existing sync signature), NO new CXA edge (reuses the C-RT-16 LLM-dispatch seam). CP spec C-CP-25 §5.2/§25.2/§25.12 v1.54 is the paired primary contract. IS / OD / AS / ADR specs UNCHANGED; CXA v2.20 UNCHANGED.

Phase 7 consumers may treat runtime spec v1.75 §14.24 C-RT-33 as canonical for the `PostJoinSynthesisStepDispatcher` contract. The reproducible cached-replay extension is the registered `B-FANOUT-OUTPUT-REPLAY` follow-on (§14.24.7), NOT this arc.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- The full-chain real-provider e2e witness (a fan-out workflow with a synthesis step run through the real bootstrap) is the integration proof co-landing in the arc bundle; the CP-side per-strategy witnesses + the runtime dispatcher unit witnesses prove the halves.
- See `.harness/clearance/README.md` for marker discipline.
