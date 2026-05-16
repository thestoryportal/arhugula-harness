# Class 1 Tension — U-OD-09 acc #2 Required/Conditional tier classification has no spec basis (FF-1)

**Filed:** 2026-05-16 (Phase 7 sub-phase 7b, OD axis-stream, L3 batch)
**Unit:** U-OD-09 — Declare `harness.breaker.*` 7-attribute canonical schema
**Plan body:** `Implementation_Plan_Operational_Discipline_v2_5.md` §3.3.1 (full body; v2.6 §3.3.1 is an M-1 delta over it)
**Spec contract:** `Spec_Operational_Discipline_v1_3.md` C-OD-07 §7.1 (§1–§13 preserved verbatim from v1.2; canonical §7.1 table at `Spec_Operational_Discipline_v1_2.md` lines 423–433)
**Class:** 1 (halt-execution) — design gap; this is the pre-identified **FF-1** carry-forward, NOT a newly surfaced fork.

## Defect (FF-1 — already known, carried unresolved)

U-OD-09 AC #2 asserts: "Required vs Conditional tier classification per §7.1: 4 Required (scope / from_state / to_state / trigger_count); 3 Conditional (permanent_fail_repeats / tool_id / model_version)."

The plan `HARNESS_BREAKER_ATTRIBUTES : List<GenAiAttribute>` signature annotates each of the 7 attributes with `tier: REQUIRED` or `tier: CONDITIONAL`.

**Spec C-OD-07 §7.1 declares no tier classification at all.** The §7.1 seven-attribute schema table has columns `Attribute | Type | Source | Definition` — there is no Required/Conditional split, and no tier column. AC #2 and the `tier:` annotations are a plan-introduced H_T structure with no spec basis. Per `CLAUDE.md` I-2 / X-AL-3 (no silent H_T design extension at Phase 7), there is nothing to conform AC #2 *to*.

This was identified by `verbatim_audit_od_plan.md` §4A.7 and carried as **FF-1** at OD plan v2.5 §0.6. v2.5 explicitly did NOT conform AC #2 — the `tier:` annotations, AC #2 prose, and `test_required_tier_attributes_count_four` / `test_conditional_tier_attributes_count_three` tests are preserved verbatim from v2.1 and flagged "carried — pending operator decision per §4A.7 / §0.6 FF-1". v2.6 §3.3.1 preserves the FF-1 carry verbatim. The plan body itself states acc #2 "has no spec basis and is a §2.7.6 Class 1 fork of design-gap shape carried for operator disposition."

## Signature-vs-acceptance-criterion contradiction (materialization-blocking)

Beyond the design-gap: the plan signature **cannot be materialized** against the landed carrier.

- `HARNESS_BREAKER_ATTRIBUTES` is typed `List<GenAiAttribute>`. `GenAiAttribute` is carried at the landed U-OD-04 (`harness-od/src/harness_od/otel_genai_base.py`).
- Landed `GenAiAttribute` has field `tier : AttributeTier`. `AttributeTier` is a 3-member `StrEnum`: `REQUIRED_STABLE` ("Required (Stable)") / `RECOMMENDED_DEVELOPMENT` ("Recommended (Development)") / `OPT_IN_CONTENT` ("Opt-In content") — the OTel GenAI semconv 1.41.0 §4.3 tier vocabulary.
- The plan U-OD-09 `tier:` values are `REQUIRED` and `CONDITIONAL`. Neither is an `AttributeTier` member. The plan's `HARNESS_BREAKER_ATTRIBUTES : List<GenAiAttribute>` annotation is un-materializable against the U-OD-04 carrier as landed.

Materializing AC #2 would require either (a) inventing a new `BreakerTier` enum (`REQUIRED`/`CONDITIONAL`) — a silent H_T design extension foreclosed by X-AL-3 — or (b) widening `AttributeTier` on the landed U-OD-04 to add `REQUIRED`/`CONDITIONAL` — a spec-divergent edit to a landed L0 carrier. Neither is permissible at 7b execution-time.

## Disposition required (operator)

Same disposition FF-1 has awaited since v2.5 §0.6 / §4A.7 action 2:

- **Option A — spec extension.** `spec-writer` extends C-OD-07 §7.1 to commit a Required/Conditional tier classification for `harness.breaker.*`, with the tier vocabulary spelled out. Phase 5 spec revision-pass. Then the plan + a `BreakerTier`-or-equivalent carrier conform to the extended spec.
- **Option B — strike AC #2.** The operator rules the tier split a plan artifact with no contract intent; AC #2 prose, the `tier:` annotations in `HARNESS_BREAKER_ATTRIBUTES`, and the `test_required_tier_*` / `test_conditional_tier_*` tests are struck. `HARNESS_BREAKER_ATTRIBUTES` re-typed to a tier-less record (e.g. `List<str>` of the 7 §7.1 attribute names, or a `HarnessBreakerAttribute` record carrying only `name`). Phase 6 OD plan revision-pass. No spec change. The remaining U-OD-09 surface (`BreakerScope`/`BreakerState`/`HarnessBreakerEvent`/`emit_breaker_trip_span_event`/§7.2/§7.3) is materializable and lands once AC #2 is struck.

Option B is the lower-cost fix and consistent with the spec being the senior artifact; recommended absent a contract intent for the tier split.

## Status

🛑 OPEN — U-OD-09 HALTED. Not landed. Skipped in the L3 batch. Downstream U-OD-10 (consumes U-OD-09) inherits the block. No code written for U-OD-09.

This is the same FF-1 the §4A verbatim audit and v2.5/v2.6 plan bodies have carried; this file records the Phase-7 execution-time surfacing and the additional signature-un-materializability finding (the `AttributeTier`-vs-`REQUIRED/CONDITIONAL` mismatch against the landed U-OD-04 carrier).
