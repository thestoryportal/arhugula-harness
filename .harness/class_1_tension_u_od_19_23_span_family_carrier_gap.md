# Class 1 Tension — U-OD-19 / U-OD-23 `Span*` family carrier gap at landed U-OD-04

**Filed:** 2026-05-16
**Sub-phase:** 7b — OD axis-stream, Level 2 batch
**Units:** U-OD-19 (Compose sandbox-tier overhead + per-sibling rollup at fan-out
close), U-OD-23 (Declare five operator-burden eval primitives + separate-child-
span emission commitment)
**Fork class:** Class 1 (halt-execution)
**Routing target:** Phase 6 plan revision / operator ratification —
`Implementation_Plan_Operational_Discipline_v2_6.md` §3.2.1 (U-OD-04 carrier-
growth) vs. the landed U-OD-04 source.

## Defect

Both units consume the OTel-handle alias family at typed signature positions:

- **U-OD-19** — `rollup_fanout_at_close(parent_span_ref : SpanRef, …)` consumes
  `SpanRef` (v2.1 §3.5.2 signature; v2.6 §3.5.2 M-1 re-point).
- **U-OD-23** — `emit_eval_as_child_span(…) -> Result<ChildSpanRef, …>` consumes
  `ChildSpanRef`, and `parent_span_ref : SpanRef` (v2.1 §3.6.1 signature; v2.6
  §3.6.1 M-1 re-point).

Per `Implementation_Plan_Operational_Discipline_v2_6.md` §3.5.2 / §3.6.1 (the R5
M-1 materializability re-points), `SpanRef` and `ChildSpanRef` are **re-pointed
to the U-OD-04 carrier**: v2.6 §3.2.1 grows U-OD-04 to declare the OTel-handle
alias family `SpanRef` / `ChildSpanRef` / `SpanAttributes` / `EventEmission`
(v2.6 §3.2.1 acceptance criterion #9; signature sub-block at v2.6 §3.2.1 lines
327–351). The materializability audit (`.harness/materializability_audit_od_plan.md`)
records U-OD-19/23 as resolved-by-R5 *on the assumption that the U-OD-04 carrier-
growth is in place*.

**It is not in place.** U-OD-04 is a landed L0 unit. Its landed source —
`harness-od/src/harness_od/otel_genai_base.py` — was authored against the
*v2.5* U-OD-04 body (the file's own authority docstring cites
`Implementation_Plan_Operational_Discipline_v2_5.md §3.2.1`). The v2.5 body has
no `Span*` alias family. The landed `otel_genai_base.py` declares only
`GenAiOperation`, `AttributeTier`, `GenAiAttribute`, `BASE_LAYER_ATTRIBUTES`,
`SPAN_NAME_FORMAT`, `BASE_METRIC_NAME`, `HIERARCHY_CORRELATION_KEY`,
`span_name`, `attributes_in_tier`. It does **not** export `SpanRef`,
`ChildSpanRef`, `SpanAttributes`, or `EventEmission`.

The v2.6 carrier-growth delta to U-OD-04 was never applied to the landed source.
U-OD-19 and U-OD-23 therefore have no reachable carrier for `SpanRef` /
`ChildSpanRef` — they cannot be materialized pyright-strict-clean.

This is exactly the retrospective concern the materializability audit raised at
its "Retrospective concern — landed units U-OD-01 and U-OD-04" section: *"U-OD-04
is the candidate M-1 alias-carrier and a landed unit … U-OD-04's landed
materialization must be re-checked before/at the revision-pass."*

## Why this is a halt, not an absorb

The fix is not a free-hand call:

1. **U-OD-04 is landed.** Adding the four `Span*` aliases re-opens an already-
   cleared L0 unit. Re-visiting a landed unit's materialization is an operator-
   ratified action, not an execution-time absorption.
2. **The alias targets are OTel-SDK design choices.** v2.6 §3.2.1 specifies
   `type SpanRef = OTelSpanHandle`, `type SpanAttributes = OTelAttributeMap` —
   the concrete Python materialization (`opentelemetry.trace.Span`? a
   `NewType`? a `Mapping[str, AttributeValue]` alias? a frozen Pydantic model
   for `EventEmission`) is a `Target_Stack_Commitment` OTel-adoption decision
   that wants operator ratification, consistent with the audit's §4A.7
   "Classify each M-1 open type" operator action.
3. Silently materializing `Span*` inside U-OD-19/23 would re-introduce the M-1
   undeclared-type defect the R5 re-point exists to close (each unit would carry
   its own divergent `SpanRef`).

## Recommended resolution (operator decides)

Per the materializability audit §4A.4 M-1 sub-pass + §4A.7:

- **Option A (audit's primary recommendation) — apply the v2.6 carrier-growth to
  U-OD-04.** Re-visit the landed `otel_genai_base.py`: add the `SpanRef` /
  `ChildSpanRef` / `SpanAttributes` / `EventEmission` declarations per v2.6
  §3.2.1 lines 327–351, plus the v2.6 acc #9 tests
  (`test_span_ref_aliases_otel_sdk_span_handle`, etc.). On re-clear of U-OD-04,
  U-OD-19/23 (and the other `Span*` consumers U-OD-09/10/20/25/26/30/31)
  resolve their carrier edge and can land.
- **Option B — inline-at-consumer.** Re-classify the `Span*` family as inline-
  auxiliary-types materialized at the first-consuming unit with a plan audit
  table (the AS Pattern-B option). Less aligned with the v2.6 R5 disposition,
  which explicitly chose the U-OD-04 carrier.

Option A is the v2.6-canonical direction; it requires the operator to (i)
authorize re-visiting landed U-OD-04 and (ii) ratify the concrete Python
materialization of the four OTel aliases.

## Disposition

U-OD-19 and U-OD-23 **skipped** in the L2 batch. U-OD-06, U-OD-07, U-OD-16 of
the same batch proceed (no `Span*` dependency). U-OD-13 separately halted for an
unrelated topological-misplacement defect — see
`class_1_tension_u_od_13_topological_misplacement.md`.
