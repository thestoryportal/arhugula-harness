---
artifact: design-substrate/Spec_Control_Plane_v1_104.md
version: v1.104
cleared_at: 2026-07-22T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-Class-2-fork-ratification (B-59 apply arc; spec-writer apply pass per CLAUDE.md §4.3 + §4.5)
back_reference:
  - .harness/class_2_fork_b59_capacity_authority_across_bootstraps.md (RATIFIED 2026-07-21 — option A AS RECOMMENDED)
merge_commit: pending (pre-merge at filing time; B-59-A apply PR)
reviewer_chain:
  - operator ratification (2026-07-21) — option A as recommended
  - out-of-family codex review owed pre-merge (spec leg)
---

# Clearance — Spec_Control_Plane_v1_104 v1.104 (B-59 apply arc)

v1.103→v1.104: delta-only file amending ONE row (row 2, "the admission guarantee") of the §25.11 pattern-table extension last substantively defined at `Spec_Control_Plane_v1_102.md` §1. The row's existing `occupied + N + S ≤ cap` formula and "the budget is SHARED" clause are extended to state explicitly that the shared budget, and the `occupied` count it is evaluated against, span sequential `api.run()` bootstraps within one process — not only concurrent activity within a single bootstrap. No new admission formula, no new `RunStatus` value, no new cascade row. The process-lifetime capacity-authority mechanism itself (what survives teardown, the adopt-new-budget-carry-occupied reconciliation, the budget-shrink typed refusal, the every-admission-surface rider) is Runtime-owned, defined at the same-arc Runtime v1.104 §14.8.10.6 — cross-referenced, never restated. No CP plan unit owed for this arc (cross-reference only; the fork's verification obligations are entirely Runtime-owned per Runtime plan v2.52 U-RT-146).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
