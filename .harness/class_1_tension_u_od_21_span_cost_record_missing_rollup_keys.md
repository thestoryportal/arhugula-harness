# Class 1 Tension — U-OD-21: `SpanCostRecord` carrier lacks the rollup keys acc #3 requires

**Status:** 🛑 OPEN — filed 2026-05-16 during Phase 7 sub-phase 7b OD axis-stream (L4 batch).
**Unit:** U-OD-21 — Compose cross-family `provider_discriminator` rollup + tokenization-version anchor.
**Plan body:** `Implementation_Plan_Operational_Discipline_v2_6.md` §3.5.4 (v2.6 M-2 revision) over `Implementation_Plan_Operational_Discipline_v2_1.md` §3.5.4 (v2.1 base body).
**Spec contract:** `Spec_Operational_Discipline_v1_3.md` C-OD-15 §15.1, §15.2, §15.3 (preserved verbatim from v1.2).
**Fork class:** Class 1 (halt-execution) — plan signature cannot be materialized at target stack.

## Defect

The plan signature (v2.1 §3.5.4, preserved verbatim at v2.6 §3.5.4) declares:

```
fn rollup_costs_by_axis(
  span_records : List<SpanCostRecord>,
  axis         : RollupAxis
) -> List<CrossFamilyCostRollup>
```

Two parameters: a list of `SpanCostRecord` and a `RollupAxis`. No auxiliary
span→attributes lookup parameter.

Acceptance criterion #3 requires:

> `rollup_costs_by_axis` returns aggregated rollups per axis:
> `PER_PROVIDER_DISCRIMINATOR` keys on **family tag**;
> `PER_PROVIDER_AND_MODEL` keys on **(provider, model) tuple**;
> `PER_FALLBACK_EVENT` preserves **per-attempt provider identity**.

The carrier `SpanCostRecord` is U-OD-20 (`idempotency_join_dedup.py`, landed).
Its 9 fields are:

| Field | Carries a rollup key? |
|---|---|
| `span_id` | no |
| `idempotency_key` | no |
| `total_cost` | no (the value being summed, not a key) |
| `total_latency_ms` | no |
| `derived_keys` | no |
| `engine_replay_disposition` | no |
| `retry_attempt_number` | no |
| `retry_cause_attribution` | no |
| `is_replay_derived` | no |

**`SpanCostRecord` carries no `provider_discriminator` / family tag, no
`gen_ai.provider.name`, and no `gen_ai.request.model` field.** None of the
three keys acc #3 demands — family tag, `(provider, model)`, per-attempt
provider — can be projected from the declared parameter type. `RollupAxis`
selects *which* key to group by; it does not *supply* the key values.

`rollup_costs_by_axis` is therefore un-materializable against its declared
signature: there is no expression over `List[SpanCostRecord]` that produces a
non-trivial `CrossFamilyCostRollup.group_key` for any of the three axes.

## Root cause — M-1 carrier-shape defect uncovered by the M-2 edge

The v2.6 M-2 revision (`Implementation_Plan_Operational_Discipline_v2_6.md`
§3.5.4) added the `[U-OD-20]` `Depends on` edge so `SpanCostRecord` resolves to
an in-cone carrier (acc #9). The edge fix is correct as far as it goes — but it
points at a carrier whose **field shape** does not carry the rollup keys. v2.6
M-2 repaired the edge; it did not re-verify the M-1 carrier shape against
acc #3. This is the same pattern flagged in `carrier-home-defect-pattern` /
`halt-route-split-ac-pattern`: a hidden-coupling edge added to a carrier that
was specified for a different consumer (U-OD-20's dedup/per-attempt-cost
surface) and never grew the fields a second consumer (U-OD-21's rollup) needs.

The v2.1 base body had the same latent defect — `SpanCostRecord` was never on a
dependency path *to* U-OD-21 at v2.1, so the un-materializable rollup was
unreachable and never surfaced. v2.6's edge made it reachable, and the defect
is now live.

## Spec position

C-OD-15 §15.1 is consistent — it describes the three rollup axes and says the
`provider_discriminator` attribute (C-OD-05 §5.1 row 15) carries the family
tag, the per-fallback-event span carries `gen_ai.provider.name`, etc. The spec
expects rollup over **spans bearing those attributes**. The defect is purely at
the plan layer: the plan chose `SpanCostRecord` as the rollup input carrier,
and `SpanCostRecord` is not a span-attributes-bearing record. The spec does not
under-specify; the plan mis-selected the carrier type (or under-specified the
carrier's field set).

## Materializable vs un-materializable surface

Per `halt-route-split-ac-pattern`, the unit splits:

| Surface | Acc | Status |
|---|---|---|
| `CrossFamilyTag` enum | #1, #8 | materializable (standalone declaration) |
| `RollupAxis` enum | #2 | materializable (standalone declaration) |
| `TokenizerVersionAnchor` enum | #4 | materializable (standalone declaration) |
| `TOKENIZER_VERSION_ANCHOR_REQUIREMENT` const | #5 | materializable (verbatim §15.2 text) |
| `FallbackChainCostComposition` record | #6 | materializable (standalone declaration) |
| Cross-axis edge to U-CP-NN (C-CP-04) | #7 | declarative; resolves at 7c |
| `CrossFamilyCostRollup` record + `rollup_costs_by_axis` fn | #3, #9 | **un-materializable** — carrier missing rollup keys |

This batch's operator directive is full-halt-and-skip on a sig-vs-AC
contradiction; U-OD-21 is **not partial-landed** here. The split is recorded so
the OD-plan revision pass can choose between (a) a partial-land + strike acc #3
and the `rollup_costs_by_axis` signature, or (b) a carrier-shape fix.

## Recommended fix (for the OD-plan implementation-planner revision pass)

**Option A — grow the carrier (preferred).** Add a span-attributes projection
to `SpanCostRecord` (or interpose a `SpanCostAttributedRecord` that pairs a
`SpanCostRecord` with its `provider_discriminator` / `gen_ai.provider.name` /
`gen_ai.request.model` attributes). Re-point `rollup_costs_by_axis`'s parameter
to the grown carrier. This is the cleanest read of C-OD-15 §15.1 and keeps
acc #3 verbatim. It is a plan-layer signature change (carrier field-set
growth), same review class as the U-OD-02 widen-signature disposition.

**Option B — second parameter.** Add a
`span_attributes : List<SpanAttributes>` (or a `Map<span_id, attributes>`)
parameter to `rollup_costs_by_axis`. Plan-layer signature change.

Both are FACTOR-OUT / plan-internal-conform; neither requires a spec change.
Option A is preferred — it makes `SpanCostRecord` (or its successor) a
self-sufficient rollup carrier, consistent with the v2.1 intent that
`rollup_costs_by_axis` take exactly `(span_records, axis)`.

## Routing

Phase 6 OD-plan revision-pass at `design-substrate/` (per `harness-od/CLAUDE.md`
§5.1 — "OD plan v2.6 atomic unit signature defect"). Joins the deferred cluster.
U-OD-21 skipped for this batch; no dependent in the L4/L5 batch consumes
U-OD-21's `rollup_costs_by_axis` (U-OD-22 at L6 cites it — not in this batch).

## Disposition

🛑 HALTED. Skipped. Deferred cluster grows to 8 units (was 7):
U-OD-02, U-OD-03, U-OD-08, U-OD-09, U-OD-10, U-OD-21, U-OD-28, U-OD-30.

---

## ✅ RESOLVED — OD plan v2.8 (2026-05-16); source-landed (2026-05-20)

Resolved by the `implementation-planner` OD-plan v2.8 revision pass (`design-substrate/Implementation_Plan_Operational_Discipline_v2_8.md`), operator-ratified 2026-05-16. See v2.8 §0.2 defect table.

**Source-landing event (2026-05-20):**
- U-OD-20 carrier growth (`SpanCostRecord` 9 → 12 fields) landed at commit `600b902` (`feat(7b): re-land U-OD-20 — grow SpanCostRecord 9->12 fields (v2.8 D-5)`). The three new string fields — `provider_discriminator`, `gen_ai_provider_name`, `gen_ai_request_model` — are now present at `harness-od/src/harness_od/idempotency_join_dedup.py:180-184`.
- U-OD-21 `rollup_costs_by_axis` landed at commit `e8fae9c` (`feat(7b): land U-OD-21 — cross-family rollup + tokenizer-version anchor`). All acc #1–#9 ACs materialized at `harness-od/src/harness_od/cross_family_rollup.py`.

This fork's defect (carrier missing rollup keys → `rollup_costs_by_axis` un-materializable) is fully closed at HEAD `9f7556c`. No residual.

**Note on the downstream U-RT-49 cost-attribution AC:** the U-RT-49 fork-extension record (`fork_u_rt_49_workflow_execution_extends_u_rt_44.md`) originally cited this fork as the blocker for U-RT-49's "cost-attribution chain produced an entry" AC. That attribution was inaccurate. U-RT-49's residual is **not** an OD-side gap; the actual gaps are CP-driver invocation site + spec authority for the invocation point + `PRICE_TABLE_REF` substitution. The corrected residual is filed at `[[fork_u_rt_49_cost_attribution_invocation_underspec]]` (2026-05-20).
