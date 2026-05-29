# Implementation Plan: Operational Discipline — v2.25 (delta over v2.24)

---

## Change-note (v2.24 → v2.25)

**Scope of revision.** Canonical-reading amendment at U-OD-04 (telemetry primitive — sampler binding) + U-OD-12 (base-rate set + envelope substrate) + U-OD-16 (per-persona-tier redaction gradient substrate) absorbing the OD-3 + OD-4 RETIRE-READY persona_tier plumbing arc per `.harness/class_1_fork_od_3_od_4_retire_ready_persona_tier_plumbing.md` operator-ratified 2026-05-28 (Q1=A + Q2=A + Q3=a + Q4=i + Q5=α). Runtime spec v1.37 NEW `RuntimeConfig.persona_tier: PersonaTier = PersonaTier.SOLO_DEVELOPER` field at §3 C-RT-03 + OD spec v1.26 canonical-reading amendments at §C-OD-10 §10.3 + §C-OD-13 §13.1 co-published this arc. v2.24 + v2.14 unit bodies at §3 PRESERVED VERBATIM per delta-only-plan-chain convention; v2.25 publishes the canonical-reading amendment table that downstream readers apply when interpreting U-OD-04 + U-OD-12 + U-OD-16.

**Substrate posture.** ZERO new unit; ZERO new cluster; ZERO new acceptance criterion at U-OD-04 / U-OD-12 / U-OD-16. The substrate at OD axis is canonical at HEAD:
- `PER_CELL_BASE_RATE_ENVELOPE` (U-OD-12 at `harness-od/src/harness_od/base_rate_set_and_envelope.py`) — 8-row §10.3 table
- `PER_PERSONA_TIER_REDACTION` (U-OD-16 at `harness-od/src/harness_od/redaction_gradient.py`) — 3-row §13.1 gradient
- `CellID` (U-OD-01 at `harness-od/src/harness_od/observability_matrix.py`) — `(persona_tier × deployment_surface)` key
- `reject_excluded_cell` (U-OD-01) — typed exception for excluded cell

v2.25 lifts the consumer site at the runtime materializers (`materialize_tracer_provider_stage` + `materialize_span_processor_stage`) per runtime spec v1.37 §3 NEW field + OD spec v1.26 §1.1 + §1.2 canonical-reading materialization composition site declarations.

---

## §1. Canonical-reading amendment table

| Unit | Authoring site | Canonical reading at v2.25 |
|---|---|---|
| **U-OD-04** | `Implementation_Plan_Operational_Discipline_v2_5.md` §3.2.1 | Sampler binding at `materialize_tracer_provider_stage` now reads `(config.persona_tier, config.deployment_surface)` and resolves `base_rate` per OD spec v1.26 §1.2 canonical-reading materialization (`PER_CELL_BASE_RATE_ENVELOPE[CellID(persona_tier=..., deployment_surface=...)].default_rate`) instead of forcing `base_rate=1.0`. Pre-v2.25 module-level `_DEFAULT_SAMPLER: Final[Sampler] = build_default_sampler()` constant RETIRED. AC body PRESERVED VERBATIM; the canonical reading refines the binding-site behavior under the existing AC scope. Tests at `tests/test_persona_tier_plumbing.py::TestTracerProviderPersonaTierBaseRate` (5 tests) verify per-cell base_rate resolution + excluded-cell typed-error. |
| **U-OD-12** | `Implementation_Plan_Operational_Discipline_v2_8.md` §3.4.2 | `PER_CELL_BASE_RATE_ENVELOPE` substrate PRESERVED VERBATIM. v2.25 canonical-reading adds that the substrate is now consumed at the runtime sampler binding site (`materialize_tracer_provider_stage`) per runtime spec v1.37 + OD spec v1.26 §1.2. Pre-v2.25 the substrate was consumer-side-canonical only at `cost_attribution_dashboard_binding.base_rate_for(cell)`; v2.25 adds the runtime materializer consumer. Tests at `harness-od/tests/test_base_rate_set_and_envelope.py` PRESERVED VERBATIM (substrate-side); NEW runtime-side tests at `tests/test_persona_tier_plumbing.py` exercise the consumer. |
| **U-OD-16** | `Implementation_Plan_Operational_Discipline_v2_1.md` §3.4.6 | `PER_PERSONA_TIER_REDACTION` substrate PRESERVED VERBATIM. v2.25 canonical-reading adds that the substrate is now consumed at the runtime redaction binding site (`materialize_span_processor_stage` → `RedactionSpanProcessor(persona_tier=config.persona_tier, ...)`) per runtime spec v1.37 + OD spec v1.26 §1.1. NEW `MultiTenantOverrideRefusedError` typed exception class at `harness-od/src/harness_od/redaction_span_processor.py` enforces §13.1 row 3 non-toggleability at construction (empty `redacted_attributes` frozenset at multi-tenant raises). Tests at `harness-od/tests/test_redaction_gradient.py` PRESERVED VERBATIM (substrate-side); NEW runtime-side tests at `tests/test_persona_tier_plumbing.py::TestRedactionSpanProcessorPersonaTier` (8 tests) exercise the per-persona consumer. |

---

## §2. Production binding co-published this arc

| File | Change | Purpose |
|---|---|---|
| `harness-runtime/src/harness_runtime/types.py` | NEW `persona_tier: PersonaTier = PersonaTier.SOLO_DEVELOPER` field at `RuntimeConfig` | Per runtime spec v1.37 §3 C-RT-03 NEW field |
| `harness-runtime/src/harness_runtime/lifecycle/tracer_provider.py` | Module-level `_DEFAULT_SAMPLER` RETIRED; `materialize_tracer_provider_stage` constructs sampler at call-time via `PER_CELL_BASE_RATE_ENVELOPE` lookup | Per OD spec v1.26 §1.2 canonical-reading materialization |
| `harness-runtime/src/harness_runtime/lifecycle/span_processor.py` | `RedactionSpanProcessor(persona_tier=config.persona_tier)` invocation | Per OD spec v1.26 §1.1 canonical-reading materialization |
| `harness-od/src/harness_od/redaction_span_processor.py` | NEW `persona_tier` ctor kwarg + NEW `MultiTenantOverrideRefusedError` typed exception + NEW `persona_tier` property | Per OD spec v1.26 §1.1 + §13.1 row 3 non-toggleability enforcement |
| `tests/test_persona_tier_plumbing.py` | 16 NEW tests covering field landing + sampler per-persona base_rate + redactor per-persona toggle + excluded-cell typed-error | AC coverage for the binding-lift arc |

**Test posture.** 3367/3367 tests pass + 10 skipped (was 3351/3351 + 10 at v2.24 close; +16 NEW at v2.25 = 3367 — verifies all existing test coverage preserved + new persona_tier plumbing exercised). Pyright clean at modified files (1 pre-existing unrelated error at `types.py:1658` `Skill` class identity inherited from v2.24).

---

## §3. Sections preserved verbatim from v2.24

ALL v2.24 + v2.23 + ... + v2.1 unit bodies preserved verbatim per delta-only-plan-chain convention. ZERO acceptance-criterion change. ZERO test-name change. ZERO signature change. ZERO DAG topology change. ZERO new cluster. ZERO new edge. v2.24 §1 canonical-reading amendment table at U-OD-42 / U-OD-43 / U-OD-44 / U-OD-45 PRESERVED VERBATIM.

---

## §4. Cross-axis cascade analysis

ZERO cross-axis cascade per fork doc Q5=(α) operator-ratified scope discipline + OD spec v1.26 §2 cite-cascade table. Intra-OD + intra-Runtime + intra-harness-od substrate only.

- CP spec v1.17 §6.5 `StepEffectiveBinding.persona_tier` PRESERVED VERBATIM (per-step / per-workflow reading distinct from per-deployment OD-axis reading)
- CXA v2.15 PRESERVED VERBATIM (NO new typed-edge; NO convention-seam)
- AS spec v1.7 PRESERVED VERBATIM
- ADR-D5 v1.3 / ADR-D6 v1.2 PRESERVED VERBATIM
- ADD v1.3 PRESERVED VERBATIM
- PRD v1.1 PRESERVED VERBATIM
- IS spec PRESERVED VERBATIM

---

## §5. Retirement transit posture

**OD-3 (Composite Sampler) PARTIAL (refined) at apply-arc close — NO tier transit.** Gate (b) §10.3 persona-tier-aware base_rate envelope CLOSED at v2.25 apply (sampler base_rate envelope now materializes §10.3 8-row table via `PER_CELL_BASE_RATE_ENVELOPE` consumer at `materialize_tracer_provider_stage`). Gate (a) §9.1 tail-keep-on-classification at OTLP collector boundary remains deferred per §9.3 implementer-discretion clause. Per X-AL-2 partial-retirement-is-non-retirement at the tier-up direction: one-of-two-gates-closed does NOT transit to RETIRE-READY; row stays at PARTIAL (refined). Tier transit to RETIRE-READY requires gate (a) §9.1 close at a follow-on arc.

**OD-4 (Pre-Collector redaction SpanProcessor) PARTIAL (refined) at apply-arc close — NO tier transit.** Gate (a) §13.1 per-persona-tier override toggle PARTIALLY CLOSED at v2.25 apply (deployment-level persona_tier plumbed at `materialize_span_processor_stage` → `RedactionSpanProcessor(persona_tier=...)`; multi-tenant-compliance non-toggleability NEW-enforced via `MultiTenantOverrideRefusedError`). Solo-developer §13.1 "OPERATOR_SELF_REDACT" per-session toggle mechanism remains deferred (out-of-scope at deployment-binding-time per fork doc §2.4 (α); requires session-control-substrate arc). Gate (b) §13.2 opaque-token tokenization mode remains deferred (strip-not-tokenize MVP scope-lock per advisor 29th application). Per X-AL-2 partial-retirement-is-non-retirement at the tier-up direction: gate (a) partially-closed + gate (b) open does NOT transit to RETIRE-READY; row stays at PARTIAL (refined). Tier transit to RETIRE-READY requires per-session toggle close + §13.2 tokenization close at follow-on arcs.

**NO retirement event batch filing owed at this arc.** Per X-AL-2 + workflow v1.12 §7.4.7.3.C audit applied at `harness-od/CLAUDE.md` §4.1: this apply arc is within-PARTIAL refinement (one-and-a-half gates closed across two rows; both rows stay PARTIAL refined). Retirement-tier transit (PARTIAL → RETIRE-READY) requires gate-list closure: OD-3 §9.1 tail-keep + OD-4 per-session toggle + OD-4 §13.2 tokenization at follow-on arcs.

---

## §6. Adjacent observations

(a) **No DAG change at v2.25.** v2.25 is purely consumer-site canonical-reading amendment at U-OD-04 + U-OD-12 + U-OD-16. ZERO new edge between units; ZERO topology change; ZERO Kahn-acyclic re-verification owed.

(b) **Mirror-shape to OD-3 batch-34 + OD-4 batch-35 substrate-retirement precedents.** Substrate landed at one PR (composite_sampler.py at PR #19; redaction_span_processor.py at PR #22); consumer site lifts at subsequent PR when cross-axis prerequisite (RuntimeConfig.persona_tier field at v1.37 + canonical-reading amendments) is in place.

(c) **§10.3 envelope column deferred.** The "Base-rate envelope" column at §10.3 (operator-tunable ranges per cell like `0.1–1.0`) requires a `RuntimeConfig.otel` or sibling sub-config extension. v2.25 materializes the "Base-rate default" column only. Future arc owed at operator-discretion timing.

(d) **§13.1 solo-developer "OPERATOR_SELF_REDACT" mechanism column conformance deferred.** v2.25 enforces multi-tenant-compliance non-toggleability at construction. Solo-developer's full "OPERATOR_SELF_REDACT" mechanism (per-session toggle at in-process collector configuration) operates at runtime via operator-session control; per-session toggle wire-up requires a separate session-control-substrate arc. Out of scope at v2.25 per fork doc §2.4 (α) recommendation.

(e) **NEW species candidate `substrate-pre-landed-consumer-deferred-multi-arc-lift` at workflow v1.12 §7.4.7.2.** Mirror-shape to OD-3 batch-34 + OD-4 batch-35 substrate-retirement precedents. Substrate canonical at one arc; consumer site lifts at later arc when cross-axis prerequisite is in place. Distinct closure-event-class candidate at species-3 sub-species column.

---

## §7. Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Operational_Discipline_v2_25.md` |
| Status | **Proposed (v2.25)** — canonical-reading amendment at U-OD-04 + U-OD-12 + U-OD-16 absorbing OD-3 + OD-4 RETIRE-READY persona_tier plumbing arc |
| Predecessor | v2.24 (2026-05-28 4-OD-B cluster bundled absorption) |
| Substrate consumed | `.harness/class_1_fork_od_3_od_4_retire_ready_persona_tier_plumbing.md`; runtime spec v1.37 NEW `RuntimeConfig.persona_tier` field; OD spec v1.26 §1.1 + §1.2 canonical-reading amendments; production binding at `types.py` + `tracer_provider.py` + `span_processor.py` + `redaction_span_processor.py`; 16 NEW tests at `tests/test_persona_tier_plumbing.py` |
| Successor | H_T-OD-3 + H_T-OD-4 remain PARTIAL (refined); tier transit to RETIRE-READY requires follow-on arcs closing OD-3 §9.1 tail-keep + OD-4 per-session toggle + OD-4 §13.2 tokenization |
| Revision policy | In-CLI per workspace `CLAUDE.md` §4.3 (design-substrate/ canonical; back-flow deprecated 2026-05-15) |
| Date | 2026-05-28 |

---

*End of `Implementation_Plan_Operational_Discipline_v2_25.md` delta. Per delta-only convention, v2.24 + v2.23 + ... + v2.1 file bodies PRESERVED VERBATIM and remain canonical-at-authoring for their respective scopes. v2.25 is the operative canonical reading for U-OD-04 + U-OD-12 + U-OD-16 consumer-site behavior going forward.*
