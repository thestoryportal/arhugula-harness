# `Implementation_Plan_Operational_Discipline` v2.26 — delta over v2.25

**Filed:** 2026-05-28
**Authoring authority:** Phase 7 sub-phase 7b — H_T-OD-3 PARTIAL → RETIRE-READY gate (a) closure arc
**Predecessor:** `Implementation_Plan_Operational_Discipline_v2_25.md` (v2.25 canonical-reading amendment absorbing OD-3 + OD-4 RETIRE-READY persona_tier plumbing per Reading (α))
**Revision shape:** Delta-only plan file per workspace `CLAUDE.md` §2.4 OD plan row convention. v2.25 + earlier unit bodies PRESERVED VERBATIM. v2.26 carries change-note + §1 single-unit canonical-reading amendment at U-OD-11 only.

---

## Change-note (v2.25 → v2.26)

Single-unit-body canonical-reading amendment at U-OD-11 (per `§3.4.1` in `Implementation_Plan_Operational_Discipline_v2_5.md`) absorbing OD spec v1.26 → v1.27 §1.1 + §1.2 + §1.3 + §1.4 canonical-reading at the §C-OD-09 §9.3 implementer-discretion clause closure.

U-OD-11 covers C-OD-09 §9.1 + §9.2 + §9.3 (the per-deployment-surface sampling mode + always-sampled exception set + sampling-discipline invariants surface). v2.26 amends U-OD-11 at the canonical-reading layer to absorb the **tail-keep-on-classification consumer-site lift** at the runtime span-processor materializer.

ZERO new unit; ZERO new cluster; ZERO new acceptance criterion at the spec layer (§9.3 implementer-discretion clause closure is intra-spec; plan AC #N where N already covers `TAIL_KEEP_RULES` substrate at U-OD-12 is unchanged at v2.26); ZERO DAG topology change; ZERO coverage matrix structural delta; ZERO cross-axis cascade per OD spec v1.27 §3 (intra-OD-axis only).

Closes H_T-OD-3 PARTIAL → RETIRE-READY gate (a) §9.1 tail-keep-on-classification at OTLP collector boundary per OD spec v1.27 §1.1 (a)+(b)+(c) closure. Gate (b) §10.3 base_rate envelope CLOSED at PR #25 (v1.26 / v2.25). Both OD-3 gates closed at v2.26 publication → tier transit per X-AL-2.

---

## §1 Single-unit canonical-reading amendment at U-OD-11

### §1.1 U-OD-11 — `SamplingMode` + `PER_DEPLOYMENT_SURFACE_SAMPLING` + always-sampled set + tail-keep algorithm-lift

**v2.25 carrier surfaces (PRESERVED VERBATIM at v2.26 unit body):**

- `SamplingMode` 2-value StrEnum per §9.1 row mapping
- `PER_DEPLOYMENT_SURFACE_SAMPLING` dict[DeploymentSurface, SamplingMode]
- `ALWAYS_SAMPLED_EVENT_CLASSES` frozenset[str] per §9.2 18-entry table
- `is_always_sampled(event_name)` decomposed-prefix predicate

**v2.26 canonical-reading additions at the consumer-site lift (absorbed from OD spec v1.27 §1.1 + §1.2 + §1.3):**

| NEW carrier / consumer site | Module / class | OD spec authority |
|---|---|---|
| `is_classification_trigger(span)` per-span §10.2 trigger predicate | `harness-od/src/harness_od/tail_keep_classification.py` | v1.27 §1.3 trigger materialization table |
| 3 trigger-string constants (`SANDBOX_VIOLATION_SPAN_NAME`, `BREAKER_TRIPPED_SPAN_NAME`, `VALIDATOR_FAIL_PERMANENCE_ATTR` + `_PERMANENT_VALUE`) | `tail_keep_classification.py` module-level | v1.27 §1.3 row carrier-level reading |
| `TailKeepSpanProcessor(SpanProcessor)` wrap-BSP processor | `harness-od/src/harness_od/tail_keep_span_processor.py` | v1.27 §1.1 (a)+(b) algorithm-lift |
| Per-deployment-surface gate at `materialize_span_processor_stage` | `harness-runtime/src/harness_runtime/lifecycle/span_processor.py` | v1.27 §1.4 head-based-at-local-development invariant preservation |
| `SpanProcessorStage.tail_keep_processor: TailKeepSpanProcessor \| None` field | `lifecycle/span_processor.py:SpanProcessorStage` | v1.27 §1.2 row 4 type extension |
| `SpanProcessorStage.flush()` tail-keep-aware drain (force_flush keep-all on shutdown) | `lifecycle/span_processor.py:SpanProcessorStage.flush` | v1.27 §1.1 (a) algorithm — drain semantics on shutdown |

**NEW acceptance criteria at U-OD-11 (additive at v2.26; carrier-level):**

- AC #N.1 — `is_classification_trigger(span)` returns True for span name `sandbox.violation`
- AC #N.2 — `is_classification_trigger(span)` returns True for span name `breaker.tripped`
- AC #N.3 — `is_classification_trigger(span)` returns True for span attribute `validator.fail.permanence` == `permanent`
- AC #N.4 — `is_classification_trigger(span)` returns False for arbitrary span with no §10.2 trigger
- AC #N.5 — `TailKeepSpanProcessor` per-trace buffer drops traces without §10.2 trigger at root close
- AC #N.6 — `TailKeepSpanProcessor` forwards full trace to downstream when ANY span carries §10.2 trigger
- AC #N.7 — `TailKeepSpanProcessor` forwards always-sampled spans (§9.2) immediately at on_end (no buffer)
- AC #N.8 — `TailKeepSpanProcessor.force_flush` keep-all on shutdown (no silent loss)
- AC #N.9 — `materialize_span_processor_stage` does NOT wrap with `TailKeepSpanProcessor` at LOCAL_DEVELOPMENT (head-based per §9.1 row 1)
- AC #N.10 — `materialize_span_processor_stage` wraps with `TailKeepSpanProcessor` at SELF_HOSTED_SERVER + MANAGED_CLOUD (tail-based per §9.1 row 2)
- AC #N.11 — `SpanProcessorStage.tail_keep_processor` is `None` at LOCAL_DEVELOPMENT, non-None at production surfaces
- AC #N.12 — End-to-end via TracerProvider → TailKeep → SimpleSpanProcessor + InMemoryExporter preserves classified trace
- AC #N.13 — End-to-end via TracerProvider → TailKeep → SimpleSpanProcessor + InMemoryExporter drops unclassified trace

**Test files at v2.26 apply:**

- `harness-od/tests/test_tail_keep_span_processor.py` — 16 unit tests covering predicate + buffer + flush + isolation + InMemoryExporter integration
- `harness-runtime/tests/test_lifecycle_span_processor.py` — 5 NEW tests at materializer wiring (local-dev bypass + production wrap + drops + preserves + production end-to-end)

ZERO impact at U-OD-11 v2.5 verbatim-divergence conformance (the §3.4.1 conformed surfaces — `ALWAYS_SAMPLED_EVENT_CLASSES` member set + acc #3 — preserved verbatim at v2.26; this amendment is additive carrier+consumer-site lift, not member-set tightening).

---

## §2 Adjacent observations (NOT patched per FM-2 single-focus arc scope)

(a) **U-OD-12 `TAIL_KEEP_RULES` substrate — consumer-site lift acknowledged.** v2.5 §3.4.2 U-OD-12 AC #6 declared `TAIL_KEEP_RULES` substrate verbatim per §10.2; v2.26 lifts the consumer site at the runtime materializer + `TailKeepSpanProcessor` chain. NEW carrier `is_classification_trigger(span)` consumes the conceptual triggers but uses concrete OTel span-attribute / span-name carrier checks per OD spec v1.27 §1.3 carrier-level reading. The `TAIL_KEEP_RULES` substrate at U-OD-12 retains its declarative role; the consumer at U-OD-11 (this amendment) translates declarative rule-strings into concrete OTel carriers. ZERO U-OD-12 amendment owed.

(b) **§9.2 §10.2 overlap acknowledged at carrier.** `sandbox.violation` + `breaker.tripped` are in BOTH §9.2 always-sampled AND §10.2 classification-triggers. The `TailKeepSpanProcessor.on_end` handles overlap correctly: forwards always-sampled immediately AND sets per-trace keep flag so siblings benefit. Documented at processor module docstring + OD spec v1.27 §2 (b).

(c) **Workspace `CLAUDE.md` §2.3 + §2.4 row bumps.** Co-published at v2.26 apply commit per the cite-cascade discipline at OD spec v1.27 §3.

---

## §3 Sections preserved verbatim

All v2.25 + earlier unit bodies (U-OD-00 through U-OD-54) preserved VERBATIM. Coverage matrix unchanged. Within-axis DAG unchanged. Cross-axis edge enumerations unchanged.

---

## §4 Filing footer

| Field | Value |
|---|---|
| Artifact | `design-substrate/Implementation_Plan_Operational_Discipline_v2_26.md` |
| Filed at | 2026-05-28 |
| Phase | Phase 7 sub-phase 7b — H_T-OD-3 PARTIAL → RETIRE-READY closure arc |
| Predecessor | `Implementation_Plan_Operational_Discipline_v2_25.md` |
| Successor consumption | workspace + per-axis row bumps + retirement batch-36 |
| Revision policy | Delta-only plan file; v2.25 + earlier PRESERVED VERBATIM per workspace `CLAUDE.md` §2.4 convention |
| Cross-axis cascade | ZERO (intra-OD-axis only) |
| Net AC count | +13 at U-OD-11 (additive carrier+consumer-site lift) |
| Net unit count | 55 (unchanged: 55 at v2.25 = U-OD-00 + U-OD-01..U-OD-54) |
| Test posture | 3388/3388 tests pass + 10 skipped (was 3367 + 10 pre-arc; +21 NEW) |
