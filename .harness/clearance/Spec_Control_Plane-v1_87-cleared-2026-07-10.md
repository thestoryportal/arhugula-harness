---
artifact: design-substrate/Spec_Control_Plane_v1_87.md
version: v1.87
cleared_at: 2026-07-10T00:00:00-07:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/u1-3c-prewarm-design-decision-record.md (Fable-5 review-cleared DDR, §11)
  - B-18-3C-PREWARM (arc-ledger)
merge_commit: pending (pre-PR)
reviewer_chain:
  - Fable-5 adversarial pre-build review (2026-07-10) — H1/H2/H3 must-fix amendments incorporated before any code landed
  - Out-of-family Codex pre-PR review (§13.1 standing discipline)
  - impl witnesses (6 test_workflow_driver_parallelization_warmup.py tests; 5417 total green)
---

# Clearance — `Spec_Control_Plane_v1_87.md`

This delta materializes **ADR-D4 §1.8** (concurrent-prompt-cache warm-up protocol, steps 2-4) at the `_execute_parallelization` WorkflowDriver PARALLELIZATION PROCEED path. Two additive `bool = False` fields are added: `D4MultiplicativeTunable.concurrent_cache_warmup` (§11.4) and `WorkflowManifestEntry.concurrent_cache_warmup` (§6.1 extension clause). At the code level, `_proceed_fanout` gains a two-phase branch when `_warmup_gate` is `True` (serialize `branch[0]` for the cache-write, then `gather` branches `[1..N-1]` for cache-hits). All defaults are `False`; the path is byte-identical to the pre-v1.87 all-concurrent baseline when the gate is off.

The Fable-5 adversarial pre-build review (session 2026-07-10, `.harness/u1-3c-prewarm-design-decision-record.md` §11) returned SOUND-WITH-AMENDMENTS and identified three must-fix correctness hazards — H1 (bare `await` of `branch[0]` would silently drop ledger entries + violate PROCEED semantics on branch-0 failure; corrected to `try/except Exception` capture), H2 (predicate was under-specified; strengthened to cover `INFERENCE_STEP`, `provider+model`, `extended_thinking`; memory-runtime exclusion documented as operator-asserted residual scope), H3 (`branch_plan[0]` IndexError on empty resume; closed by `len(branch_plan) >= 2` guard). All three were incorporated before the first edit. Post-build Codex review ran clean.

Clearance applies to the delta-surface only (two additive fields + `_proceed_fanout` two-phase on `_warmup_gate`). Four follow-ons registered in the SPINE `B-*` register: `B-18-3C-PREWARM-COHORTKEY` (dispatcher-attested cacheability via `cohort_key() -> str | None`), `B-18-3C-PREWARM-CASCADE` (PAUSE/CASCADE_CANCEL paths), `B-18-3C-PREWARM-DEFAULT-ON` (flip to ADR §1.8(f) required-at-cap>1), `B-18-EPOCH-PARTITION` (heterogeneous cohort partition). These are registered, not deferred silently.

## Notes

- NO §5.2 IS-hash change, NO new contract/enum/fail-class/CXA edge.
- Runtime manifest-loader `_WorkflowSection` gains `concurrent_cache_warmup` by the §14.19.4 byte-exact-projection invariant (impl-to-cleared-spec; NO runtime spec delta owed).
- The cardinality test `test_workflow_manifest_entry_fourteen_fields` (harness-cp) updated in the same PR (13 → 14 fields).
