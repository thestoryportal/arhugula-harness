# Substitution Retirement Carry-Forward — `PRICE_TABLE_REF`

**Class:** Substitution retirement event (bounded H_E residual per X-AL-2)
**Status:** ✅ RETIRED (status-line refreshed 2026-05-28 Phase 1 status-cascade sweep per workflow v1.12 §7.4.7.3.B) — RETIRED 2026-05-21 at U-OD-38 landing `7104fd7` ("feat(U-OD-38 cluster 4-OD-D impl arc, commit 1/2 partial): cost-attribution at LLM dispatch site") via `resolve_for(RATE_TABLE_V1, provider, model)` per memory `[[fork-price-table-ref-substitution-retirement]]`. Species 3 stale-carry per workflow v1.12 §7.4.7.2.

**Status:** 🛑 OPEN — bounded residual; carried forward *(historical, predates 2026-05-21 retirement)*
**Filed:** 2026-05-20 alongside CP spec v1.5 §25.9 absorption (`.harness/fork_u_rt_49_cost_attribution_invocation_underspec.md` resolution arc)
**Substrate:** `harness-od/src/harness_od/cost_formula.py:69` — `PRICE_TABLE_REF: PriceTableRef = PriceTableRef("od-price-table-ref::deferred-to-U-OD-21")`

## The bounded residual

Per `Phase_7_Meta_Architecture_v1.md` X-AL-2 retirement criterion:

> Retirement = (cited unit IDs landed) ∧ (substituted H_E surface no longer invoked at substitution site). Both conditions required. Partial retirement is non-retirement.

**Status at HEAD `b7df032`:**

| Condition | State | Evidence |
|---|---|---|
| Cited unit IDs landed | ✅ MET | U-OD-21 landed at commit `e8fae9c` (`cross_family_rollup.py` materializes `rollup_costs_by_axis` + `CrossFamilyTag` + `RollupAxis` + `CrossFamilyCostRollup` + `TokenizerVersionAnchor` + `TOKENIZER_VERSION_ANCHOR_REQUIREMENT` + `FallbackChainCostComposition`). U-OD-20 12-field carrier landed at commit `600b902`. |
| Substituted H_E surface no longer invoked | ❌ UNMET | `harness-od/src/harness_od/cost_formula.py:175-188` `_lookup_rates(table_ref, key)` raises `RateLookupError` unconditionally at HEAD: "no resident rate table — PRICE_TABLE_REF resolves at U-OD-21; use compute_span_cost_with_rates with an explicit PriceRateEntry". The substitution string `"od-price-table-ref::deferred-to-U-OD-21"` is still resident at line 69. No rate table authored at U-OD-21 landing. |

**X-AL-2 net status: substitution NOT retired.** First criterion met; second criterion unmet. Partial retirement is non-retirement.

## What U-OD-21 was meant to land vs. what U-OD-21 actually landed

The substitution string at `cost_formula.py:69` was authored before U-OD-21 landed. The string asserts the rate table "resolves at U-OD-21." U-OD-21 ultimately landed the cross-family rollup machinery + tokenization-version anchor (acc #1–#9 at OD plan v2.8/v2.11 §3.5.4); it did NOT land a rate table.

Whether this is a U-OD-21 under-specification (the unit was meant to land the rate table but its acc set didn't enforce it) or whether `PRICE_TABLE_REF` was always intended to resolve at deployment-binding time (per `cost_formula.py:184` docstring: "the concrete rate table resides at U-OD-21 / deployment-binding-time refresh") is itself an ambiguity. The retirement criterion language is silent on this — it cites unit landing as the first condition, without distinguishing between landed-unit-completeness and authored-unit-completeness.

**For purposes of this record:** treat U-OD-21 as landed (acc set verified materialized at `cross_family_rollup.py`) and the rate-table-authoring as a separate concern that survives U-OD-21 close. The X-AL-2 second condition is the operative gap.

## Why this isn't blocking U-RT-49 AC closure

The `compute_span_cost_with_rates(inputs, rates_explicit)` bypass at `cost_formula.py:175-188` allows callers to supply an explicit `PriceRateEntry` snapshot, fully bypassing `_lookup_rates`. The U-RT-49 smoke test step body uses this bypass with a mock `PriceRateEntry`; emission produces a `SpanCostRecord` with mock-value cost; AC text ("cost attribution chain produced an entry") is satisfied verbatim. **This does NOT retire `PRICE_TABLE_REF` — the substitution string remains resident and `_lookup_rates` still raises for any caller that doesn't have a rate snapshot.**

Per CP spec v1.5 §25.9 "Rate substitution carry-forward (v1.5 informational; not patched at v1.5)" — the bounded residual is explicitly named in the spec amendment and referred to this record.

## Resolution path (future)

Three resolution options surfaced at the U-RT-49 fork-resolution session 2026-05-20 (Q3a/Q3b/Q3c). Operator selected Q3c for U-RT-49 close; rate-table authoring (Q3a) is the in-place resolution for this substitution residual:

**Q3a — author the rate table inside OD.** Land per-provider rate tables (Anthropic / OpenAI / Ollama per ADR-F1 v1.2 committed-providers list) at `harness-od/src/harness_od/` — likely a new module `rate_table.py` or extension of `cost_formula.py`. Per-model pricing + refresh contract per OD spec C-OD-14 §14.1 (per-span cost formula) + §14.3 (deployment-binding-time refresh cadence implied at acc #8). Scope estimate: ~100–200 LOC.

Required substrate verifications before authoring:
- C-OD-14 §14.1 + §14.3 actual contract text — what shape does the spec demand of the rate table? (Probably a per-(provider, model) snapshot record with token-pricing fields.)
- ADR-F1 v1.2 §Decision — confirms the committed-providers list at this phase.
- `cost_formula.py` `PriceTableRef` + `PriceRateEntry` + `PriceRateKey` shapes — what the lookup function consumes.

**Q3b — defer indefinitely.** Carry the substitution as permanent bounded residual; rely on caller-supplied `PriceRateEntry` snapshots throughout. Possible if all real (non-test) callers can always supply an explicit rate snapshot from their own substrate (e.g., a config file). Less likely correct — most callers will not have a rate snapshot resident.

**Recommended path: Q3a, scheduled into Phase 7 sub-phase 7d substitution-retirement events** (per `phase-7-substitution-retirement` skill triggers). The retirement event verifies (1) cited unit IDs landed [already met], (2) H_E surface no longer invoked [authored rate table replaces the deferred string], and (3) no caller routes through the bypass surface without an explicit operator-supplied rate snapshot (X-AL-2 ∧ X-AL-3 composition check).

## Routing

Bounded residual; carries forward. NOT halt-execution. The U-RT-49 cost-attribution AC un-strikes at this arc's close via Q3c bypass; this substitution remains open as a documented X-AL-2 residual carried to sub-phase 7d.

## Cross-references

- `.harness/fork_u_rt_49_cost_attribution_invocation_underspec.md` — parent fork; cites this record at Q3c resolution
- `.harness/class_1_tension_u_od_21_span_cost_record_missing_rollup_keys.md` — U-OD-21 source-landing record; cites U-OD-21's actual landed scope (no rate table)
- `Spec_Control_Plane_v1_5.md` §25.9 "Rate substitution carry-forward" paragraph
- `harness-od/src/harness_od/cost_formula.py:69` — substitution site
- `Phase_7_Meta_Architecture_v1.md` X-AL-2 — retirement criterion governing this record

## Provenance

- Filing event: 2026-05-20 at CP spec v1.5 §25.9 absorption pass, alongside `.harness/fork_u_rt_49_cost_attribution_invocation_underspec.md` Q3c resolution.
- Substitution string predates U-OD-21 landing (commit `e8fae9c`); first appeared at OD axis scaffolding under Phase 7 sub-phase 7b execution.
