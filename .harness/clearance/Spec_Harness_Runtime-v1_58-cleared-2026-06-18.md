---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.58
cleared_at: 2026-06-18T18:30:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_b_fallback_chain_family_cost_composition.md
  - .harness/beyond-mvp-capability-boundary-ledger.md (line 120 — B-FALLBACK-CHAIN-FAMILY-COST-COMPOSITION)
merge_commit: pending (R-FS-1 B-FALLBACK-CHAIN-FAMILY-COST-COMPOSITION bundled-absorption PR)
reviewer_chain:
  - advisor (full-transcript) — resolved the §15.3-span vs §15.1.2-record false dichotomy; flagged the LLM-subtotal invariant + the hollow-FallbackChainCostComposition trap
  - out-of-family Codex (pre-merge, on the diff)
  - impl-time grounding pass (worktree off origin/main 2630847)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.58`

v1.58 adds a **third** per-run cost-rollup field to **§9 C-RT-09 `RunResult`** — **`cost_attribution_by_provider_discriminator: tuple[CrossFamilyCostRollup, ...]`** — the cross-family family-tag (`frontier_managed` / `frontier_managed_alt` / `local_ollama`) breakdown, computed at `_build_run_result` via `rollup_costs_by_axis(records, RollupAxis.PER_PROVIDER_DISCRIMINATOR)`, **and populates it in production** by tagging each LLM-dispatch `SpanCostRecord.provider_discriminator` with the dispatched provider's family. R-FS-1 standalone `B-*` arc `B-FALLBACK-CHAIN-FAMILY-COST-COMPOSITION`, surfaced + registered at arc B-COST-DISCRIMINATOR-TAXONOMY (OD v1.30 §15.1.2 reserved the field for *this* arc to populate). Makes `RollupAxis.PER_PROVIDER_DISCRIMINATOR` non-vacuous in production.

**No operator gate — additive, minor bump, impl-to-cleared-spec.** The new field is optional with default `()` (the v1.45 `pause_snapshot` / v1.57 `dispatch_kind` precedent); the existing `cost_attribution` + `cost_attribution_by_dispatch_kind` fields are PRESERVED VERBATIM. No committed invariant sacrificed; OD v1.30 §15.1.2 already defines the field + assigns population to this arc → **no OD spec change** (runtime-only).

**LLM-subtotal partition (NOT a full-run partition).** `PER_PROVIDER_DISCRIMINATOR` skips `None`-tag records (tool / validator / webhook have no provider family), so `Σ total_cost` = the LLM-dispatch subtotal, NOT the total run cost — the other two axes carry the full-run invariant. The mapping is provider-fixed per the §15.1 example (`ANTHROPIC → frontier_managed`, `{OPENAI, GOOGLE} → frontier_managed_alt`, `LOCAL_OPEN_WEIGHT → local_ollama`); `CrossFamilyTag` not extended.

**Bundled doc-hygiene reconcile.** v1.58 also adds the `cost_attribution_by_dispatch_kind` row + invariant to the §9 body table that v1.57's change-note declared but did not apply (the field was code-landed + change-note-declared but missing from the canonical §9 body — `[[spec-prose-plan-body-drift-pattern]]`).

## Notes

- Scope: ONLY §9 C-RT-09 (the one new field + invariant + the v1.57 body reconcile); all other §9 / §14.x / §14.20 PRESERVED VERBATIM. No new C-RT-NN, no new fail class, no IS-spec/§5.2-hash change (ephemeral run-OUTPUT), no ADR change, no OD spec change.
- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
