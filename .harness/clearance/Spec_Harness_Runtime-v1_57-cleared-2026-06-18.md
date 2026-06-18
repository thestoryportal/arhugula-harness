---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.57
cleared_at: 2026-06-18T05:40:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_b_cost_discriminator_taxonomy.md
  - .harness/beyond-mvp-capability-boundary-ledger.md (line 118 — B-COST-DISCRIMINATOR-TAXONOMY)
merge_commit: pending (R-FS-1 B-COST-DISCRIMINATOR-TAXONOMY bundled-absorption PR)
reviewer_chain:
  - advisor (full-transcript) — confirmed additive/no-gate; sum-invariant preserved by separate single-axis fields
  - out-of-family Codex (pre-merge, on the diff)
  - impl-time grounding pass (worktree off origin/main 655ff6b)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.57`

v1.57 adds a second per-run cost-rollup field to **§9 C-RT-09 `RunResult`** — **`cost_attribution_by_dispatch_kind: tuple[CrossFamilyCostRollup, ...]`** — the dispatch-type (llm/tool/validator/webhook) cost breakdown, computed at `_build_run_result` via `rollup_costs_by_axis(records, RollupAxis.PER_DISPATCH_KIND)` (the new OD spec v1.30 §15.1 axis). R-FS-1 standalone `B-*` arc `B-COST-DISCRIMINATOR-TAXONOMY`, surfaced + registered at arc CA (v1.53 §9 named the dispatch-type breakdown "the most operator-meaningful rollup and exactly the one this latent defect blocks").

**No operator gate — additive, minor bump.** The new field is optional with default `()` — a minor bump per the §9 version-evolution invariant, mirroring v1.45's `pause_snapshot` + v1.53's axis-naming. The existing `cost_attribution` field (PER_PROVIDER_AND_MODEL) is PRESERVED VERBATIM. No committed invariant sacrificed. **Sum-invariant preserved:** `cost_attribution` and `cost_attribution_by_dispatch_kind` are two separate single-axis tuples (each record has exactly one `(provider, model)` and exactly one `dispatch_kind`), so each independently satisfies `sum(e.total_cost) == total run cost` — orthogonal partitions, no double-count.

**Phase 7 consumers:** the paired OD amendment (OD spec v1.30 — the `PER_DISPATCH_KIND` axis + `DispatchKind` vocabulary + `provider_discriminator` per-dispatch-optional correction) lands in the same PR (marker `Spec_Operational_Discipline-v1_30-cleared-2026-06-18.md`). Scope: ONLY §9 C-RT-09 gains the one field + the one invariant; all other §9 / §14.x / §14.20 PRESERVED VERBATIM. No new C-RT-NN, no new fail class, no IS-spec/§5.2-hash change (ephemeral run-OUTPUT, identical to v1.53 §9 scope discipline), no ADR change.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
