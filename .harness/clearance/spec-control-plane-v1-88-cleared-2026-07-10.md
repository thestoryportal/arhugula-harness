---
artifact: design-substrate/Spec_Control_Plane_v1_88.md
version: v1.88
cleared_at: 2026-07-10T00:00:00-00:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_2_fork_b18_cohortkey_fork_a_vs_b.md
  - design-substrate/Spec_Control_Plane_v1_87.md (predecessor, cleared 2026-07-10)
merge_commit: pending — in-flight PR
reviewer_chain:
  - Fork B ratification via .harness/class_2_fork_b18_cohortkey_fork_a_vs_b.md (Class 2 operator decision)
  - 16 acceptance-criterion witnesses (CK-1..3 + RK-1..13) all green
  - Pending just codex-review out-of-family decorrelated review (§13.1) pre-merge
---

# Clearance — `Spec_Control_Plane_v1_88.md`

This delta replaces the CP-visible per-attribute `_same_prefix_cohort()` predicate from v1.87 with a dispatcher-oracle approach via the new `@runtime_checkable CohortKeyCapable(Protocol)`. A dispatcher returning a non-None `cohort_key()` attests that the prompt-cache prefix is stable (frozen_tool_superset bound, memory_runtime absent) — the machine-checkable version of the v1.87 operator-asserted residual scope.

Scope: additive `CohortKeyCapable` Protocol exported from `harness_cp.workflow_driver`; `_same_prefix_cohort()` refactored to dispatcher-oracle; three delegation stubs on `RuntimeHITLGateComposer`, `RetryBreakerFallbackDispatcher`, `SyncDispatcherFacade` in `harness_runtime`. 16 new test witnesses confirm the contract end-to-end including RK-13 full production-chain test.

Phase 7 consumers: the `CohortKeyCapable` Protocol is the stable interface for the B-18-3C-PREWARM-DEFAULT-ON and B-18-EPOCH-PARTITION follow-on arcs. The MVP caveat (warmup does not fire when frozen_tool_superset is None) is correctly implemented and documented in §25.16. Both COHORTKEY and DEFAULT-ON are registered open arcs; the COHORTKEY prerequisite is now met by this delta.

## Notes

- Codex out-of-family review pending (§13.1); clearance marker filed pre-review per bundle convention; update merge_commit on PR merge.
- B-18-3C-PREWARM-DEFAULT-ON prerequisite (COHORTKEY landed) is now satisfied by this arc.
