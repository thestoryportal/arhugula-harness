---
artifact: design-substrate/Implementation_Plan_Control_Plane_v2_31.md
version: v2.31
cleared_at: 2026-05-31T13:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_pr_2_workflow_layer_ctx_access_recipe_underspecified.md
  - PR #105 (fork-doc filing)
  - PR #<this PR> (Reading C apply pass)
merge_commit: pending
reviewer_chain:
  - implementation-planner apply-pass discipline (canonical-reading amendment at U-CP-74..U-CP-79 absorbing CP spec v1.30 §1.1–§1.6)
  - impl-time grounding pass verifying composer signatures + runtime wiring layer + bootstrap stage 6 binding at HEAD `c8918b3`
  - test pass verifying 3533/3533 passing + 10 skipped post-apply (+11 NEW v1.30 sanity tests at `harness-cp/tests/test_procedural_tier_resolver_v1_30_apply.py`)
supersedes:
superseded_by:
---

# Clearance — `Implementation_Plan_Control_Plane v2.31`

CP plan v2.31 absorbs CP spec v1.29 → v1.30 §1.1–§1.6 canonical-reading collapse of the workflow/engine composer signature split per `.harness/class_1_fork_pr_2_workflow_layer_ctx_access_recipe_underspecified.md` Reading (C) operator-ratified 2026-05-31 (Q1=C / Q2=v1.30 amendment / Q3=ZERO cross-axis cascade / Q4=PR-2+PR-3 collapse single PR). Single-arc canonical-reading amendment at U-CP-74..U-CP-79: each composer atomic unit gains a uniform `procedural_tier_snapshot_resolver: Callable[[], Identifier]` kw-only param + 2 NEW acceptance criteria (AC v2.31-NEW-α resolver invocation + AC v2.31-NEW-β HALT-on-resolver-failure). U-CP-78 + U-CP-79 (engine-layer) preserve the v1.29 §16.5.12.3 signature shape verbatim; U-CP-74 + U-CP-75 + U-CP-76 + U-CP-77 (workflow-layer + 1 class method) catch up to the same shape at v2.31.

Clearance covers: v2.30 unit bodies PRESERVED VERBATIM at file text; v2.31 §1.1 + §1.2 canonical-reading layer applies signature extension + AC additions; ZERO new atomic units; ZERO removed units; ZERO DAG topology change; ZERO coverage matrix structural delta; ZERO cross-axis cascade. PR-stack collapse per fork doc §5 Q4 — all 6 composers ship at the uniform shape in a single PR.

Caveats: caching-scope mode at v2.31 acceptance-criterion-α defaults to per-emission re-resolve per CP spec v1.30 §1.6 mode 1; per-composer-construction factory-closure (mode 2) remains admissible at implementer-discretion. Typed-exception surface at HALT (AC v2.31-NEW-β) tests against generic Exception subclass per CP spec v1.30 §1.5 discretion clause.

## Notes

- Phase 7 consumers may rely on v2.31 as canonical for U-CP-74..U-CP-79 signature + AC text reading until a successor marker is filed.
- Co-published with CP spec v1.30 (separate clearance marker; same back-flow doc anchor); impl arc lands at 6 composer signatures + 6 EntryPayload sidecar populations + cp_is_wiring runtime layer field + 6 wiring methods + materialize_cp_is_wiring_stage factory + bootstrap stage 6 resolver binding + 11 NEW sanity tests + 8 sibling test-module adaptations + 2 stale-carry refreshes (harness-as secret-fetch-audit + harness-cp sibling-ledger composition, from PR #89 IS spec v1.3 absorption).
- See `.harness/clearance/README.md` for marker discipline.
