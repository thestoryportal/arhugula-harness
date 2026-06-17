---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.53
cleared_at: 2026-06-17T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc (additive/clarifying — NO operator gate; sacrifices no committed invariant; advisor-confirmed advisor-not-council/no-AUQ)
back_reference:
  - .harness/class_1_fork_ca_run_result_cost_aggregate_shape.md
  - .harness/beyond-mvp-capability-boundary-ledger.md (arc CA + B-COST-DISCRIMINATOR-TAXONOMY spine registration)
  - .harness/r-fs-1-remaining-arcs-grounding-sweep-v1.md (§"Arc CA" grounding lead)
merge_commit: <pending — co-published bundled-absorption PR; pinned at post-merge refresh>
reviewer_chain:
  - advisor (pre-substantive, full-transcript) — confirmed the forced PER_PROVIDER_AND_MODEL axis + the single-axis sum-invariant + the in-memory accumulator; flagged the 4-dispatcher-compose check (verified composes) + the taxonomy-as-real-build-arc + the dropped-required-field read-back rationale
  - out-of-family Codex review at PR (decorrelated diff review)
supersedes:
superseded_by:
---

# Clearance — `Spec_Harness_Runtime v1.53` (additive/clarifying — NO operator gate)

v1.53 authors the **run-result cost-aggregate shape** for the §9 C-RT-09 `cost_attribution` field (R-FS-1 arc CA). The field — one cleared line, hard-coded `()` at `_build_run_result` since landing (gated behind the now-CLOSED U-OD-21 HALTED tension) — is given a concrete aggregate shape so it can be populated:

- **Axis = `RollupAxis.PER_PROVIDER_AND_MODEL`** — empirically forced. `PER_PROVIDER_DISCRIMINATOR` (the grounding sweep's lead) **raises `CrossFamilyRollupError`** on every production record because production cost helpers tag `provider_discriminator` with a dispatch-type taxonomy (`"llm"`/`"tool"`/`"validator"`/`"webhook"`), none of which are `CrossFamilyTag` members. `PER_PROVIDER_AND_MODEL` keys on `(gen_ai_provider_name, gen_ai_request_model)` with no validation → safe + operator-meaningful.
- **Single axis** preserves the sum-invariant (`sum(total_cost)` = true run cost; a multi-axis flat tuple would double-count).
- **Type-name reconcile** `CostAttribution (OD type)` (phantom) → `tuple[CrossFamilyCostRollup, ...]` (the code type since landing). Pure spec-prose reconciliation; minor/clarifying bump.
- **Per-run aggregation** = a new INVOCATION of the existing C-OD-15 §15.1 `rollup_costs_by_axis` primitive, not a new contract.

**This is additive/clarifying and sacrifices NO committed invariant** (unlike the operator-gated v1.52 §14.5.3 relaxation) → **no operator gate** (adopt-and-note per `CLAUDE.md` §12.4.1 + `[[feedback-gate-only-on-meaningful-architecture-change]]`; advisor-confirmed). FULL-SPEC pre-authorizes the build + back-flow.

No new C-RT-NN, no new fail class, no IS-spec / §5.2-hash change, no ADR change. The latent contract-vs-production taxonomy mismatch (production helpers writing non-`CrossFamilyTag` discriminators into a field whose contract validates against `CrossFamilyTag`) is registered as the forward build arc `B-COST-DISCRIMINATOR-TAXONOMY` — NOT folded into a Class-3 throwaway. The accumulator + per-dispatch append + `_build_run_result` wiring are impl-discretion (the `harness-runtime` impl lands in this arc).

## Notes

- Phase 7 consumers may rely on this version as canonical after merge.
- See `.harness/clearance/README.md` for marker discipline.
