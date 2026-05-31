---
artifact: design-substrate/Spec_Control_Plane_v1_30.md
version: v1.30
cleared_at: 2026-05-31T13:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_pr_2_workflow_layer_ctx_access_recipe_underspecified.md
  - PR #105 (fork-doc filing)
  - PR #<this PR> (Reading C apply pass)
merge_commit: pending
reviewer_chain:
  - probe-first discipline at PR-2 impl-arc opening 2026-05-31 (workspace CLAUDE.md §10.9 standing posture amendment 5)
  - 3-Reading enumeration at fork doc §3 (A ctx-passthrough / B caller-resolves / C uniform resolver-closure)
  - operator AskUserQuestion ratification 2026-05-31 (Q1=C uniform resolver-closure / Q2=v1.30 canonical-reading amendment / Q3=ZERO cross-axis cascade / Q4=PR-2+PR-3 collapse to single PR)
  - spec-writer apply pass authoring CP spec v1.30
  - impl-time grounding pass verifying composer signatures + caller-site bindings at HEAD `c8918b3`
supersedes:
superseded_by:
---

# Clearance — `Spec_Control_Plane v1.30`

CP spec v1.30 collapses the workflow/engine composer signature split at v1.29 §16.5.12.2 into a single uniform pattern across all 6 §16.5.2 composers per `.harness/class_1_fork_pr_2_workflow_layer_ctx_access_recipe_underspecified.md` Reading (C) operator-ratified 2026-05-31. The v1.29 §16.5.12.2 workflow-layer recipe column read `procedural_tier_snapshot_ref = resolve_procedural_tier_snapshot(harness_context)`, but `harness_context` was not in the composer body's lexical scope at HEAD — probe-first discipline at PR-2 impl-arc opening surfaced the structural ambiguity. Reading C extends the §16.5.12.3 engine-layer `procedural_tier_snapshot_resolver: Callable[[], Identifier]` kw-only-param pattern uniformly to all 6 composers (4 workflow-layer + 2 engine-layer).

Clearance covers: §1.1 uniform signature shape + §1.2 per-composer recipe (SUPERSEDES v1.29 §16.5.12.2 6-row table) + §1.3 §16.5.12.3 signature-extension widening + §1.4 §16.5.12.4 runtime wiring uniform across all 6 + §1.5 §16.5.12.5 failure-mode HALT posture uniform across all 6 + §1.6 §16.5.12.7 invariants preservation. v1.29 §16.5.12.1 + §16.5.12.6 + §16.5.3 chapeau + §16.5.1–§16.5.11 PRESERVED VERBATIM. ZERO cross-axis cascade per Q3 operator ratification (verified at design-substrate/ grep — AS / OD / IS / runtime spec / ADR / ADD / PRD / CXA all unchanged at v2.17).

Caveats: caching scope at v1.29 §16.5.12.6 + v1.30 §1.6 remains implementer-discretion (per-emission re-resolve vs per-composer-construction factory closure; the v2.31 plan-side acceptance criterion defaults to per-emission). Typed-exception surface at composer-site HALT (CP spec v1.29 §16.5.12.5 + v1.30 §1.5) remains implementer-discretion; no `ProceduralTierResolutionError` typed shape committed at v1.30. PR-2 + PR-3 stack collapse per fork doc §5 Q4 ratification — all 6 composers ship at the uniform shape in a single PR.

## Notes

- Phase 7 consumers may rely on v1.30 as canonical for §16.5.12.2 + §16.5.12.3 + §16.5.12.4 + §16.5.12.5 + §16.5.12.7 reading until a successor marker is filed.
- Co-published with CP plan v2.31 (separate clearance marker; same back-flow doc anchor); impl arc lands at 6 composers + cp_is_wiring runtime layer + stage 6 bootstrap; 3533/3533 tests pass + 10 skipped (was 3522 pre-arc; +11 NEW v1.30 sanity tests at `harness-cp/tests/test_procedural_tier_resolver_v1_30_apply.py`).
- See `.harness/clearance/README.md` for marker discipline.
