---
artifact: design-substrate/Spec_Operational_Discipline_v1_30.md
version: v1.30
cleared_at: 2026-06-18T05:40:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_b_cost_discriminator_taxonomy.md
  - .harness/beyond-mvp-capability-boundary-ledger.md (line 118 — B-COST-DISCRIMINATOR-TAXONOMY)
merge_commit: pending (R-FS-1 B-COST-DISCRIMINATOR-TAXONOMY bundled-absorption PR)
reviewer_chain:
  - advisor (full-transcript) — affirmed the C-OD-15 §15.1 spec reading as the load-bearing finding (production write is the bug, CrossFamilyTag validation is correct); sharpened the forced provider_discriminator-for-non-LLM sub-decision; confirmed autonomous/no-council/additive
  - out-of-family Codex (pre-merge, on the diff)
  - impl-time grounding pass (worktree off origin/main 655ff6b; reads NOT against the diverged local main checkout cc55a43)
supersedes:
superseded_by:
---

# Clearance — `Spec_Operational_Discipline v1.30`

v1.30 amends **C-OD-15 §15.1** ADDITIVELY: a fourth cross-cost rollup axis **`PER_DISPATCH_KIND`** + the bounded **`DispatchKind`** dispatch-type vocabulary (`{LLM, TOOL, VALIDATOR, WEBHOOK}`) it keys on — the operator-meaningful dispatch-type (llm/tool/validator/webhook) cost breakdown registered as the forward arc `B-COST-DISCRIMINATOR-TAXONOMY` at arc CA. It also corrects a **latent contract-vs-production defect**: production cost helpers wrote dispatch-type strings into `SpanCostRecord.provider_discriminator` (a field the §15.1 contract reserves for the cross-family `CrossFamilyTag` family tag), so `rollup_costs_by_axis(PER_PROVIDER_DISCRIMINATOR)` would raise on every production record (dormant — only synthetic-record tests exercised it). The fix moves the dispatch type to the new typed `dispatch_kind` carrier; `provider_discriminator` becomes per-dispatch-optional (`str | None`, `None` until §15.3 chain composition populates it) and the `PER_PROVIDER_DISCRIMINATOR` axis skips `None` records.

**No operator gate — additive + bug-fix toward the cleared spec.** The new axis + vocabulary are purely additive; the `provider_discriminator` required→optional + axis error→skip-on-`None` is a bug-fix toward the spec authority (C-OD-15 §15.1 defines `provider_discriminator` = the family tag, so the production dispatch-type write was the bug). No committed invariant sacrificed. No nameable cross-domain tension (OD-internal cost-taxonomy type design) → single-voice C7 + advisor, not council (§10.9). Adopt-and-note per workspace `CLAUDE.md` §12.4.1 + `[[feedback-gate-only-on-meaningful-architecture-change]]`.

**Phase 7 consumers:** the paired runtime amendment (runtime spec v1.57 — `RunResult.cost_attribution_by_dispatch_kind` surfaces this axis) lands in the same PR (marker `Spec_Harness_Runtime-v1_57-cleared-2026-06-18.md`). §15.2 + §15.3 PRESERVED VERBATIM. The §15.3 production population of `provider_discriminator` (cross-family rollup non-vacuous-in-production via the CP→OD fallback-chain seam) is registered as the forward arc `B-FALLBACK-CHAIN-FAMILY-COST-COMPOSITION` (fork §4) — the `PER_PROVIDER_DISCRIMINATOR` axis stays defined + admissible (synthetic-record tests). No §5.2-hash / audit-projection change (`dispatch_kind` is not in the §C-OD-26.6 audit projection).

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
