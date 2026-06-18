# `Spec_Operational_Discipline` v1.30 — delta over v1.29

**Filed:** 2026-06-18
**Authoring authority:** Phase 7 — R-FS-1 standalone `B-*` arc **B-COST-DISCRIMINATOR-TAXONOMY** (dispatch-type cost rollup taxonomy reconciliation; `.harness/class_1_fork_b_cost_discriminator_taxonomy.md`; spine ledger `.harness/beyond-mvp-capability-boundary-ledger.md` line 118)
**Predecessor:** `Spec_Operational_Discipline_v1_29.md` (v1.29 — §C-OD-34 per-persona-tier prompt-governance posture)
**Revision shape:** Delta-only spec file per workspace `CLAUDE.md` §2.3 OD spec row convention. v1.29 + v1.28 + ... + v1 file bodies PRESERVED VERBATIM. v1.30 carries this change-note + the C-OD-15 §15.1 ADDITIVE amendment only.

---

## Change-note (v1.29 → v1.30)

**Introduces (ADDITIVE).** A fourth cross-cost **rollup axis** at C-OD-15 §15.1 — **`PER_DISPATCH_KIND`** — and the bounded **`DispatchKind`** dispatch-type vocabulary it keys on (`{LLM, TOOL, VALIDATOR, WEBHOOK}`). The dispatch-type cost breakdown (llm-vs-tool-vs-validator-vs-webhook) is the most operator-meaningful per-run rollup; it was registered as the forward arc `B-COST-DISCRIMINATOR-TAXONOMY` by the arc-CA fork doc + runtime spec v1.53 §9 (line 51) and is built here.

**Why a new axis, not an extension of `provider_discriminator`.** §15.1 (preserved) defines `provider_discriminator` as the **cross-family fallback-chain family tag** (`frontier_managed`/`frontier_managed_alt`/`local_ollama`; §15.3 — a *chain-composition* concept). The dispatch type (which *kind* of dispatch incurred the cost) is an **orthogonal** dimension. Folding dispatch types into the `CrossFamilyTag` vocabulary would conflate two dimensions in one enum and corrupt the §15.3 cross-family composition's input (one-source-of-truth, CLAUDE.md §4). The two dimensions get **two carrier fields + two axes**.

**Corrects a latent contract-vs-production defect (bug-fix toward this spec).** Every production cost helper wrote a dispatch-type string (`"llm"`/`"tool"`/`"validator"`/`"webhook"`) into `SpanCostRecord.provider_discriminator` — none a `CrossFamilyTag` member — so `rollup_costs_by_axis(PER_PROVIDER_DISCRIMINATOR)` would have raised `CrossFamilyRollupError` on every production record (dormant: only synthetic-record unit tests exercised it; the production rollup uses `PER_PROVIDER_AND_MODEL`). The fix moves the dispatch type to the new `dispatch_kind` carrier; `provider_discriminator` becomes **per-dispatch-optional** (the per-dispatch helpers lack chain-level family context, so they write `None`; the field stays reserved for the §15.3 fallback-chain composition to populate). The `PER_PROVIDER_DISCRIMINATOR` axis **skips `None`-tag records** (a record with no family tag is not part of a cross-family rollup); records that carry a tag are still validated against `CrossFamilyTag` (semantics otherwise unchanged).

**No new ADR.** Additive OD cost-rollup axis composing the existing C-OD-15 §15.1 surface + the C-OD-05 §5.1 cost-attribution namespaces. ADR-D6 v1.1 §1.5 (cross-family pricing differential) is the anchor and is unchanged.

**No committed invariant sacrificed.** The new axis + the `provider_discriminator` optionality are additive/bug-fix; no operator gate (`[[feedback-gate-only-on-meaningful-architecture-change]]`; advisor-confirmed advisor-not-council). §15.2 (tokenization-version anchor) + §15.3 (fallback-chain composition reference) PRESERVED VERBATIM. The §15.3 production population of `provider_discriminator` (the cross-family rollup made non-vacuous-in-production) is registered as the forward arc `B-FALLBACK-CHAIN-FAMILY-COST-COMPOSITION` (fork §4).

**No §5.2-hash / audit-projection change.** The cost-record carrier feeds the run-scoped ephemeral accumulator + the explicit 5-field `CostRecordAuditPayload` projection (§C-OD-26.6); `dispatch_kind` (like `provider_discriminator`) is NOT in that audit projection, so the C-OD-14 §14.5 audit hash is deliberately unchanged.

---

## §15.1 amendment — `PER_DISPATCH_KIND` rollup axis (ADDITIVE)

The §15.1 rollup-axis table (v1.2 baseline, preserved) is extended with a fourth axis. The amended table reads:

| Rollup axis | Aggregation |
|---|---|
| Per-`provider_discriminator` | Σ per-family cost (per-family cost visibility under fallback). Keys on the cross-family family tag; **skips records whose `provider_discriminator` is `None`** (a per-dispatch record with no chain-level family context — see below); tag-bearing records validated against `CrossFamilyTag`. |
| Per-`(gen_ai.provider.name, gen_ai.request.model)` | Σ per-provider-and-model cost (per-model visibility). |
| Per-fallback-event | Each retry's span carries the actual `gen_ai.provider.name`; the parent span carries the `provider_discriminator` family tag for cross-family rollup. |
| **Per-`dispatch_kind` (NEW v1.30)** | Σ per-dispatch-type cost — the operator-meaningful breakdown of run cost across `DispatchKind` ∈ `{LLM, TOOL, VALIDATOR, WEBHOOK}`. Keys on `SpanCostRecord.dispatch_kind` (no `CrossFamilyTag` validation — `DispatchKind` is itself a bounded enum, illegal states unrepresentable). Single axis ⟹ `Σ total_cost` = total run cost (orthogonal partition of the same total as the per-(provider, model) axis). |

### §15.1.1 `DispatchKind` vocabulary + carrier (NEW v1.30)

`DispatchKind` is the bounded dispatch-type vocabulary, **homed in the U-OD-20 carrier module** (`harness_od.idempotency_join_dedup`) so `SpanCostRecord.dispatch_kind` types it **directly** (a typed enum field, not the `str`+validate discipline `provider_discriminator` uses):

| `DispatchKind` | Producer |
|---|---|
| `LLM` | LLM dispatch cost helper |
| `TOOL` | tool dispatch cost helper |
| `VALIDATOR` | validator dispatch cost helper |
| `WEBHOOK` | webhook dispatch cost helper |

**Carrier-homing rationale (distinct from `CrossFamilyTag`).** `CrossFamilyTag` is homed in the U-OD-21 **consumer** module (`cross_family_rollup`), so the U-OD-20 carrier `str`-types `provider_discriminator` to avoid a U-OD-20→U-OD-21 cycle. `DispatchKind` is the **producer's own attribute** of the cost record (the kind of dispatch that produced it), so it is naturally homed in the carrier and the field is enum-typed (CLAUDE.md §4 type-driven design — illegal states unrepresentable). The U-OD-21 `rollup_costs_by_axis` reads `record.dispatch_kind` for the new axis.

### §15.1.2 `provider_discriminator` is per-dispatch-optional (CLARIFYING)

`provider_discriminator` carries the cross-family fallback-chain family tag **when one exists**. Per §15.3, the family tag is a chain-composition concept ("parent span retains `provider_discriminator` family tag"). A **per-dispatch** cost record produced at the edge has **no chain-level family context** and carries `provider_discriminator = None`; the field is populated by the §15.3 fallback-chain composition (forward arc `B-FALLBACK-CHAIN-FAMILY-COST-COMPOSITION`). `SpanCostRecord.provider_discriminator` is therefore `str | None` (still `str`-typed, not `CrossFamilyTag`, to preserve the no-cycle property); the `PER_PROVIDER_DISCRIMINATOR` axis skips `None` records and validates the rest against `CrossFamilyTag`.

**Scope discipline.** v1.30 amends ONLY the §15.1 rollup-axis table + adds §15.1.1 + §15.1.2. §15 contract surface / PRD / ADR linkage, §15.2, §15.3, and all §C-OD-01..§C-OD-14 + §C-OD-16..§C-OD-34 surfaces are PRESERVED VERBATIM. v1.29 + earlier lineage PRESERVED VERBATIM per the delta-only-spec-file convention except the §15.1 additive amendment above.
