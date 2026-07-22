---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.104
cleared_at: 2026-07-22T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-Class-2-fork-ratification (B-59 apply arc; spec-writer apply pass per CLAUDE.md §4.3 + §4.5)
back_reference:
  - .harness/class_2_fork_b59_capacity_authority_across_bootstraps.md (RATIFIED 2026-07-21 — option A AS RECOMMENDED: process-scoped capacity-authority singleton, adopt-new-budget-carry-occupied reconciliation, every-admission-surface rider)
merge_commit: pending (pre-merge at filing time; B-59-A apply PR)
reviewer_chain:
  - operator ratification (2026-07-21) — option A as recommended
  - out-of-family codex review owed pre-merge (spec leg)
---

# Clearance — Spec_Harness_Runtime_v1 v1.104 (B-59 apply arc)

v1.103→v1.104: NEW §14.8.10.6 — cross-bootstrap capacity-authority continuity. The composition root ADOPTS a process-lifetime FRAME LEDGER (budget/available/occupied accounting) across sequential `api.run()` invocations within one process, instead of reconstructing it fresh at every bootstrap (the fork §1 defect: a still-draining worker's occupied frame from a prior bootstrap was invisible to the next bootstrap's fresh accounting, permitting a transient over-cap breach of the C-RT-03 single-shared-cap promise). **The `SubAgentDispatchExecutor` object itself (its worker-thread pool and `_draining` flag) is NEVER the thing that survives — it is REBUILT fresh every bootstrap around the adopted ledger and bound into the existing C-RT-04 `capacity_authority` field** (`drain()` permanently flips `begin_draining()`, after which the object rejects all admission forever — persisting the executor object itself, not just its ledger, would zero out every subsequent bootstrap's admission). Contract terms: the executor's `_draining` check and the ledger's capacity decision execute under ONE shared lock as a single atomic operation (the pre-existing single-critical-section invariant is preserved across the ledger split, never weakened into two separately-locked steps); adopt-new-budget-carry-occupied reconciliation under that same lock (grow honored immediately, shrink to at-or-above occupied honored immediately, shrink below occupied → NEW `RT-FAIL-CAPACITY-AUTHORITY-BUDGET-SHRINK` typed bootstrap refusal); every-admission-surface rider (both `reserve_fanout` and direct `reserve(1)` back onto the same adopted ledger); per-run isolation preserved (only the ledger object is process-lifetime); interpreter-exit posture unchanged; test-isolation reset seam required. Mechanism (module-global vs. composition-root-held registry) is implementation-discretion. CP admission-guarantee span clarification cross-referenced to the same-arc CP v1.104 §1 (no CP plan delta owed — the witness lives at Runtime's U-RT-146). Witnesses ride the same-arc plan delta (Runtime v2.52 U-RT-146), each PD-8 mutation-probed.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
