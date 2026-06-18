---
artifact: design-substrate/Implementation_Plan_Operational_Discipline_v2_28.md
version: v2.28
cleared_at: 2026-06-18T06:05:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_b_cost_discriminator_taxonomy.md
  - design-substrate/Spec_Operational_Discipline_v1_30.md (the spec amendment this plan delta reconciles to)
merge_commit: pending (R-FS-1 B-COST-DISCRIMINATOR-TAXONOMY bundled-absorption PR)
reviewer_chain:
  - advisor (full-transcript) — flagged the count-coherence surface (the workspace's top defect class); the cross-spec drift grep surfaced the U-OD-21 plan-vs-spec/code coupling
  - out-of-family Codex (pre-merge, on the impl diff)
  - impl-time grounding pass (worktree off origin/main 655ff6b)
supersedes:
superseded_by:
---

# Clearance — `Implementation_Plan_Operational_Discipline v2.28`

v2.28 reconciles the **U-OD-21** acceptance criteria + `Tests:` field to the OD spec v1.30 §15.1 amendment (the new `RollupAxis.PER_DISPATCH_KIND` + `DispatchKind` vocabulary). The v2.1-baseline acc #2 ("`RollupAxis` enumerates exactly 3 values"), acc #3 (3-axis enumeration), and `Tests:` (`test_rollup_axis_cardinality_three`) were stale-as-described against the amended §15.1 (now 4 axes). v2.28 amends acc #2 (3→4), acc #3 (+PER_DISPATCH_KIND + the skip-`None` refinement), and the `Tests:` field (rename `_three`→`_four`, add `test_rollup_per_dispatch_kind` + `test_per_provider_discriminator_skips_none_records`).

**No operator gate — ADDITIVE plan reconciliation** downstream of the spec v1.30 amendment (itself additive/no-gate). ZERO new atomic unit; ZERO cross-axis cascade; all other U-OD-21 surface (acc #1/#4–#9, Inputs, Rollback boundary) + every other unit PRESERVED VERBATIM. Surfaced by the cross-spec drift grep (`[[spec-prose-plan-body-drift-pattern]]`) — the plan's `Tests:` field named a test that the impl renamed; reconciled in the same bundled-absorption PR rather than left as stale-carry-text.

**Phase 7 consumers:** the paired OD spec v1.30 + runtime spec v1.57 markers (`Spec_Operational_Discipline-v1_30-cleared-2026-06-18.md` + `Spec_Harness_Runtime-v1_57-cleared-2026-06-18.md`) land in the same PR.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
