# Implementation Plan — Operational Discipline (v2.28)

*Delta over v2.27. v2.28 reconciles the **U-OD-21** acceptance-criteria + `Tests:` field to the **OD spec v1.30 §15.1** amendment (R-FS-1 standalone `B-*` arc `B-COST-DISCRIMINATOR-TAXONOMY`; `.harness/class_1_fork_b_cost_discriminator_taxonomy.md`). The spec amendment adds a fourth `RollupAxis` member — `PER_DISPATCH_KIND` — so U-OD-21 acc #2's "exactly 3 values" + acc #3's 3-axis enumeration + the `Tests:` field's `test_rollup_axis_cardinality_three` are stale-as-described against the amended §15.1. ADDITIVE; ZERO new atomic unit; ZERO cross-axis cascade; no other unit's surface changed. All sections except the U-OD-21 acc #2/#3 + `Tests:` amendments below are PRESERVED VERBATIM from v2.27 (which preserved verbatim from v2.26 + ... + v2.6 + the v2.1 baseline).*

## §0 Change note (v2.27 → v2.28)

### §0.1 Revision context — OD spec v1.30 §15.1 absorption

The OD spec v1.30 amendment (C-OD-15 §15.1) ADDS a fourth cross-cost rollup axis, `RollupAxis.PER_DISPATCH_KIND` (keyed on the NEW `DispatchKind` dispatch-type vocabulary), and corrects the latent contract-vs-production defect where production cost helpers wrote dispatch-type strings into `SpanCostRecord.provider_discriminator` (a field §15.1 reserves for the cross-family `CrossFamilyTag` family tag). The U-OD-21 acceptance criteria authored at the v2.1 baseline (preserved through v2.27) pin the rollup-axis count at **3**:

> §3.5.4 U-OD-21 acc #2 (v2.1 baseline): *"`RollupAxis` enumerates exactly 3 values per §15.1."*
> §3.5.4 U-OD-21 acc #3 (v2.1 baseline): enumerates `PER_PROVIDER_DISCRIMINATOR` / `PER_PROVIDER_AND_MODEL` / `PER_FALLBACK_EVENT`.
> §3.5.4 U-OD-21 `Tests:` (v2.1 baseline): names `test_rollup_axis_cardinality_three`.

These are stale-as-described against the amended §15.1 (now 4 axes). v2.28 reconciles them. Bundled-absorption arc (OD spec v1.30 + runtime spec v1.57 + this plan delta + impl + tests, all in one PR per the back-flow discipline).

### §0.2 Sections revised

§0 (this change note); §3.5.4 U-OD-21 acc #2 + acc #3 + `Tests:` (amended below). All other sections — including U-OD-21 acc #1 / #4–#9, the `Inputs` / `Rollback boundary`, and every other unit — PRESERVED VERBATIM from v2.27.

### §0.3 Scope discipline

The acc #2 count (3→4), the acc #3 axis enumeration (+PER_DISPATCH_KIND), and the `Tests:` field (rename + 2 new tests) are the ONLY changes. The `provider_discriminator` per-dispatch-optional correction + the `PER_PROVIDER_DISCRIMINATOR` skip-`None` refinement are spec-side (OD v1.30 §15.1.2) and impl-discretion; they do not change a U-OD-21 acceptance-criterion surface beyond the axis count. ZERO new contract; ZERO new atomic unit; ZERO cross-axis cascade.

---

## §1 §3.5.4 U-OD-21 — acceptance-criteria + `Tests:` amendment

The v2.1-baseline U-OD-21 acceptance criteria #2 and #3 are amended (the rest of the acc list — #1, #4–#9 — PRESERVED VERBATIM):

**Acc #2 (amended v2.28):**

> 2. `RollupAxis` enumerates exactly **4** values per §15.1 (`PER_DISPATCH_KIND` added at OD spec v1.30, `B-COST-DISCRIMINATOR-TAXONOMY`).

**Acc #3 (amended v2.28 — adds the fourth axis + the skip-`None` refinement):**

> 3. `rollup_costs_by_axis` returns aggregated rollups per axis: `PER_PROVIDER_DISCRIMINATOR` keys on the family tag and **skips records whose `provider_discriminator` is `None`** (a per-dispatch record with no chain-level family tag, §15.1.2); `PER_PROVIDER_AND_MODEL` keys on the (provider, model) tuple; `PER_FALLBACK_EVENT` preserves per-attempt provider identity; **`PER_DISPATCH_KIND` keys on the typed `SpanCostRecord.dispatch_kind` enum** (the operator-meaningful llm/tool/validator/webhook breakdown).

**`Tests:` field (amended v2.28):** `test_rollup_axis_cardinality_three` is renamed to **`test_rollup_axis_cardinality_four`**, and two tests are added: **`test_rollup_per_dispatch_kind`** + **`test_per_provider_discriminator_skips_none_records`**. The full amended `Tests:` list:

> **Tests:** `test_rollup_axis_cardinality_four`, `test_rollup_per_provider_discriminator`, `test_rollup_per_provider_and_model`, `test_rollup_per_fallback_event_preserves_provider`, `test_rollup_per_dispatch_kind`, `test_per_provider_discriminator_skips_none_records`, `test_tokenizer_anchor_two_options`, `test_tokenizer_anchor_requirement_byte_exact`, `test_fallback_chain_parent_family_tag_retained`, `test_fallback_chain_per_attempt_provider_updates`, `test_cache_state_loss_on_cross_family`, `test_provider_discriminator_source_authority_c7`, `test_cross_axis_edge_to_u_cp_nn_c_cp_04`.

The `Inputs`, acc #1 / #4–#9, and `Rollback boundary` are PRESERVED VERBATIM from the v2.1 baseline (per the v2.8 D-5 + v2.27 preservation chain).

---

## §2 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Operational_Discipline_v2_28.md` (delta over v2.27) |
| Authored at | Phase 7 — R-FS-1 `B-COST-DISCRIMINATOR-TAXONOMY` (2026-06-18) |
| Authoring authority | OD spec v1.30 §15.1 amendment + `.harness/class_1_fork_b_cost_discriminator_taxonomy.md` |
| Predecessor | `Implementation_Plan_Operational_Discipline_v2_27.md` (v2.27 — §4.6.OD-INTERNAL) |
| Revision policy | Delta-only per workspace `CLAUDE.md` §2.4; revisions route to design-phase back-flow |
