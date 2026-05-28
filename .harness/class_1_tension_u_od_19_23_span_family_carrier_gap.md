# Class 1 Tension — U-OD-19 / U-OD-23 `Span*` family carrier gap at landed U-OD-04

**Status:** ✅ CLOSED-via-OD-plan-v2.6 (resolved 2026-05-16; verified workspace-wide audit 2026-05-20; status-line refreshed 2026-05-27) — carrier-growth applied to U-OD-04: `SpanRef` family added; 7 consumers cleared. Species 3 stale-carry per workflow v1.9 §7.4.7.2.

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

U-OD-19 and U-OD-23 **skipped** in the first L2 batch; resolved below.

## RESOLUTION (2026-05-16) — not a fork; ratified plan content not yet applied

This is **not a Class 1 design decision** — it is ratified plan content that
was never applied to source. The U-OD-04 carrier-growth (`Span*` family) is:

- **Specified** — `Implementation_Plan_Operational_Discipline_v2_6.md` §3.2.1,
  full-revised U-OD-04 body, acceptance criterion #9, purely additive ("all
  v2.5 surfaces preserved verbatim").
- **Operator-ratified** — R5 Q-R5-2 (Span* folds into U-OD-04 carrier-growth)
  and Q-R5-6 (authority = ADR-F5 + ADR-D6 v1.2 + Target_Stack OTel adoption),
  ratified in full 2026-05-15.
- **X-AL-3-cleared** — T2 ruled the `Span*` family FACTOR-OUT (faithful
  factor-out of the OTel-SDK substrate / OD emission contracts; 0 design
  extensions). v2.6 §3.2.1 acc #9 states it explicitly.

U-OD-04 landed against the *v2.5* body, before v2.6 added the carrier-growth.
Applying the v2.6 §3.2.1 additive delta to `otel_genai_base.py` is routine
implementation of ratified plan content — `type SpanRef = OTelSpanHandle`
materializes as a type-alias of the OTel-SDK span; `EventEmission` as a 4-field
frozen Pydantic record. No operator decision is owed; the concrete OTel-SDK
binding is normal stack materialization (Target_Stack §5.2 OTel adoption).

The original halt followed an over-conservative dispatch instruction. Correct
disposition: **apply the v2.6 §3.2.1 carrier-growth to landed U-OD-04** (acc #9
+ its 6 new tests, additive), re-clear U-OD-04, then U-OD-19/23 (and
U-OD-09/10/20/25/26/30/31) resolve their `[U-OD-04]` carrier edge and land.

**Status:** RESOLVED — apply ratified U-OD-04 carrier-growth; U-OD-19/23 + the
7 other `Span*` consumers cleared to land against it.

---

## Audit reconciliation (2026-05-20)

**Verified status:** RESOLVED

**Resolving artifact / evidence:** Already labeled RESOLVED 2026-05-16 (OD plan v2.6 carrier-growth applied to U-OD-04 — SpanRef family added; 7 consumers cleared). Audit confirms.

**Audit context:** Workspace-wide tension-record audit 2026-05-20 (post-U-RT-52 merge to main at 2b945ab). 33 records reviewed against current code + spec state. Result: 28 RESOLVED, 5 DEFERRED-PARTITION, 0 STILL-OPEN. The 'Status' line earlier in this record predates the audit; this section is the current verified state.
