# `Spec_Operational_Discipline` v1.27 — delta over v1.26

**Filed:** 2026-05-28
**Authoring authority:** Phase 7 sub-phase 7b — H_T-OD-3 PARTIAL → RETIRE-READY gate (a) closure arc
**Predecessor:** `Spec_Operational_Discipline_v1_26.md` (v1.26 canonical-reading amendment closing OD-3 + OD-4 RETIRE-READY persona_tier plumbing per Reading (α))
**Revision shape:** Delta-only spec file per workspace `CLAUDE.md` §2.3 OD spec row convention. v1.26 + v1.25 + ... + v1 file bodies PRESERVED VERBATIM. v1.27 carries change-note + §1 canonical-reading amendment table only.

---

## Change-note (v1.26 → v1.27)

Fidelity-pure canonical-reading amendment closing v1.26 implied carry — the OD spec v1.2 §C-OD-09 §9.3 deferred-to-implementation-discretion clause on **tail-based sampling decision algorithm** + **tail-keep-on-classification filter implementation per OTel SDK** is **CLOSED at HEAD** by the consumer-side lift at the runtime span-processor materializer.

Per OD spec v1.2 §9.1 row 2: at self-hosted-server + managed-cloud deployment surfaces, the canonical sampling mode is **tail-based sampling with tail-keep-on-classification preserving failure-trees per C-OD-10**. Pre-v1.27 carrier landscape:

| Component | Status at HEAD pre-v1.27 |
|---|---|
| §9.1 head-vs-tail per-deployment-surface mode | Substrate `PER_DEPLOYMENT_SURFACE_SAMPLING` at `harness-od/src/harness_od/sampling_mode.py` (U-OD-11 landing) |
| §9.2 always-sampled exception set (18 entries) | Substrate `ALWAYS_SAMPLED_EVENT_CLASSES` + `is_always_sampled(event_name)` predicate at `sampling_mode.py` (U-OD-11 + PR #19 SDK-boundary lift at batch-34) |
| §10.2 tail-keep-on-classification triggers (3 entries) | Substrate `TAIL_KEEP_RULES` at `base_rate_set_and_envelope.py:171` (U-OD-12 landing) |
| §10.3 per-cell base-rate envelope (8 cells) | Substrate `PER_CELL_BASE_RATE_ENVELOPE` at `base_rate_set_and_envelope.py:154` (U-OD-12 landing + PR #25 sampler-side lift at materializer) |
| §9.1 production-time tail-based algorithm | **DEFERRED** per §9.3 implementer-discretion clause |
| §10.2 tail-keep-on-classification at OTel SDK boundary | **DEFERRED** per §9.3 implementer-discretion clause |

v1.27 declares the canonical reading at the deferred-algorithm + deferred-SDK-binding rows: the algorithm + binding **MATERIALIZE** at the runtime span-processor materializer via a NEW `TailKeepSpanProcessor` (homed at `harness-od/src/harness_od/tail_keep_span_processor.py`) wrapping the `BatchSpanProcessor` at production-time deployment surfaces; bypassed at local-development per §9.1 head-based mandate.

ZERO new contract; ZERO new field; ZERO new namespace; ZERO breaking change at any §C-OD-09 / §C-OD-10 surface declared at v1.2 baseline; ZERO cross-axis cascade (intra-OD-axis canonical-reading amendment closing the implementer-discretion clause without spec extension per X-AL-3).

H_T-OD-3 PARTIAL → RETIRE-READY transit: gate (b) §10.3 base_rate envelope CLOSED at PR #25 (v1.26); gate (a) §9.1 tail-keep-on-classification CLOSED at v1.27. Both OD-3 gates closed at v1.27 publication → tier transit per X-AL-2 retirement criterion (structural-criterion-B MET). Retirement event filing at `.harness/phase-7d-retirement-events-batch-36.md`.

---

## §1 Canonical-reading amendment

### §1.1 §C-OD-09 §9.3 "Deferred to implementation discretion" clause refresh

Pre-v1.27 §9.3 footer (preserved verbatim at v1.26):

> Deferred to implementation discretion. Specific tail-based sampling decision algorithm (per-trace-completion-replay vs. eager-batch-sampling); specific tail-keep-on-classification filter implementation per OTel SDK; specific always-sampled-event detection at SDK boundary (compile-time annotation vs. runtime hook); specific cross-SDK sampling-decision conformance test.

v1.27 canonical reading at the 4 deferred elements:

| Element | Pre-v1.27 status | v1.27 closure disposition |
|---|---|---|
| (a) tail-based sampling decision algorithm | DEFERRED | **CLOSED**: per-trace-completion-replay at `TailKeepSpanProcessor.on_end` (buffer non-always-sampled spans by `trace_id`; root-close detected by `span.parent is None`; flush-or-drop materialization at root close). Algorithm choice rationale + alternative consideration documented at the carrier module docstring. |
| (b) tail-keep-on-classification filter implementation per OTel SDK | DEFERRED | **CLOSED**: wrap-BSP pattern — `TailKeepSpanProcessor(downstream=BatchSpanProcessor(...))` registered on the `TracerProvider` instead of the BSP directly. Gating via `is_classification_trigger(span)` predicate at `harness-od/src/harness_od/tail_keep_classification.py` honoring the 3 §10.2 triggers exhaustively. |
| (c) always-sampled-event detection at SDK boundary (compile-time annotation vs. runtime hook) | DEFERRED at v1.2; CLOSED at PR #19 batch-34 | **CLOSED-as-runtime-hook** at `is_always_sampled(event_name)` decomposed-prefix lookup at `sampling_mode.py`. Pre-existing carry from v1.2 onward; ratified at v1.27. |
| (d) cross-SDK sampling-decision conformance test | DEFERRED | **PRESERVED** — single-SDK MVP at HEAD; cross-SDK conformance test deferred indefinitely (OTel-Python is the only SDK in scope per Target Stack Commitment v1 §5.2). |

§9.3 footer post-v1.27 canonical reading: elements (a) + (b) + (c) CLOSED at HEAD; element (d) PRESERVED verbatim as deferred-indefinitely per single-SDK scope.

### §1.2 §C-OD-09 §9.1 production-time tail-based algorithm — implementer-discretion lift site

v1.27 names the algorithm-lift site for production-time tail-based sampling per §9.1 row 2:

| Site | Module | Class / function |
|---|---|---|
| Per-span classification trigger predicate | `harness-od/src/harness_od/tail_keep_classification.py` | `is_classification_trigger(span: ReadableSpan) -> bool` |
| Per-trace buffer + flush-or-drop materialization | `harness-od/src/harness_od/tail_keep_span_processor.py` | `class TailKeepSpanProcessor(SpanProcessor)` |
| Runtime SDK binding (production-surface gate) | `harness-runtime/src/harness_runtime/lifecycle/span_processor.py` | `materialize_span_processor_stage` — wraps BSP iff `config.deployment_surface != LOCAL_DEVELOPMENT` |
| SpanProcessorStage type extension | `harness-runtime/src/harness_runtime/lifecycle/span_processor.py:SpanProcessorStage` | NEW `tail_keep_processor: TailKeepSpanProcessor \| None` field (None at LOCAL_DEVELOPMENT; non-None at production surfaces) |

### §1.3 §C-OD-10 §10.2 trigger materialization

The §10.2 row text per v1.2 baseline:

| Classification trigger | Span-tree preservation | Source declaration |
|---|---|---|
| `permanent-fail` span trees | Any span tree where classification == `permanent-fail` per ADR-D2 §1.8 fail-class taxonomy is preserved at tail-based sampling | C-AS-04 §4.1 + ADR-D6 v1.1 §1.3 |
| `sandbox-violation` propagation | Parent + sibling spans of any `sandbox.violation` event preserved | ADR-D6 v1.1 §1.3 |
| `breaker-trip` propagation | Parent + sibling spans of any `breaker.tripped` event preserved | ADR-D6 v1.1 §1.3 |

v1.27 canonical reading at carrier-level: the 3 triggers materialize at `is_classification_trigger` as:

| §10.2 row | Concrete carrier check |
|---|---|
| `permanent-fail` | `span.attributes.get("validator.fail.permanence") == "permanent"` (per CP spec C-CP-21 §21.6 + `validator_fail_taxonomy.py`) |
| `sandbox-violation` | `span.name == "sandbox.violation"` (per C-AS-15 §15.4 + `sandbox_attribute_schema.py:_VIOLATION`) |
| `breaker-trip` | `span.name == "breaker.tripped"` (per C-CP-03 §3.5 + `lifecycle_event_span_map.py:91`) |

Per-trace preservation semantics: a §10.2 trigger detected on ANY span in a trace sets the per-trace keep flag; on root close, all non-always-sampled spans buffered under that `trace_id` are forwarded to the downstream BSP. Always-sampled spans per §9.2 bypass the buffer entirely (forward immediately at `on_end`); their tree-siblings buffered separately benefit from the keep flag when set.

ZERO row-text amendment at §10.2; carrier-level reading documents the materialization shape.

### §1.4 §C-OD-09 §9.1 head-based-at-local-development invariant — preservation

v1.27 PRESERVES verbatim the §9.1 row 1 mandate: at LOCAL_DEVELOPMENT, sampling is head-based — the sampler at span creation is the binding decision; tail-keep semantics do NOT apply. The runtime materializer enforces this by NOT wrapping the BSP at LOCAL_DEVELOPMENT — the BSP receives spans directly per the `HarnessCompositeSampler` binding decision at span creation.

---

## §2 Adjacent observations (NOT patched per FM-2 single-focus arc scope)

(a) **Bounded-buffer carve-out (MVP scope-lock).** The MVP `TailKeepSpanProcessor` does NOT bound buffer size by trace count or by per-trace span count. A pathological producer that opens 10^6 traces without ever closing a root would accumulate without bound. Future operator-tunable bounds at `CollectorConfig` are a follow-on arc per §9.3 implementer-discretion. NOT patched at v1.27 per FM-2.

(b) **§9.2 §10.2 overlap.** `sandbox.violation` + `breaker.tripped` are present in BOTH §9.2 (always-sampled) AND §10.2 (classification-trigger). The processor handles the overlap correctly: always-sampled spans forward immediately AND set the trace's keep flag so tree-siblings buffered separately are preserved at root close. ZERO impact on either spec surface.

(c) **§10.3 base-rate gating at production cells.** Sampler-side base_rate per cell (PR #25 lift) applies BEFORE TailKeep — spans dropped at the sampler never reach the processor chain. TailKeep operates only on spans the sampler recorded. The §10.2 preservation semantic is intra-recorded-trace: classification triggers preserve sibling spans the sampler ALSO recorded. Spans dropped at sampler cannot be resurrected. Documented at processor module docstring as "trust-sampler-on-base-rate" posture.

(d) **OD-3 row transit per X-AL-2.** Both OD-3 PARTIAL → RETIRE-READY gates closed at v1.27 publication (gate (b) §10.3 closed at PR #25 v1.26; gate (a) §9.1 closed at v1.27). Workflow v1.12 §7.4.7.3.C audit-template applied at `harness-od/CLAUDE.md` §4.1; cumulative-counts line refreshed in same commit per audit-template trigger.

---

## §3 Cross-artifact cite-cascade

| Site | Action at v1.27 |
|---|---|
| OD plan v2.25 → v2.26 (`Implementation_Plan_Operational_Discipline_v2_26.md`) | Single-unit-body amendment at U-OD-11 absorbing v1.27 §1.1 + §1.2 + §1.3 + §1.4 canonical-reading at the consumer-site lift |
| `harness-od/CLAUDE.md` §4.1 OD-3 row | RETIRE-READY transit + cumulative-counts line refresh (PARTIAL → RETIRE-READY; 3/8 RETIRED + 2/8 RETIRE-READY) |
| workspace `CLAUDE.md` §2.3 OD spec row | v1.26 → v1.27 row bump with change-note absorption |
| workspace `CLAUDE.md` §2.4 OD plan row | v2.25 → v2.26 row bump |
| `.harness/phase-7d-retirement-events-batch-36.md` | NEW retirement event filing H_T-OD-3 PARTIAL → RETIRE-READY transit |

ZERO cross-axis cascade (intra-OD-axis only; CP spec / AS spec / runtime spec / CXA / ADR / ADD / PRD unchanged).

---

## §4 Sections preserved verbatim

All of §C-OD-01 through §C-OD-33 in v1.26 (and v1.25 + ... + v1.2 baseline) preserved VERBATIM. v1.27 carries only the change-note + §1 canonical-reading amendment table + §2 adjacent observations + §3 cite-cascade.

---

## §5 Filing footer

| Field | Value |
|---|---|
| Artifact | `design-substrate/Spec_Operational_Discipline_v1_27.md` |
| Filed at | 2026-05-28 |
| Phase | Phase 7 sub-phase 7b — H_T-OD-3 PARTIAL → RETIRE-READY closure arc |
| Predecessor | `Spec_Operational_Discipline_v1_26.md` (OD-3 + OD-4 RETIRE-READY persona_tier plumbing per Reading (α)) |
| Successor consumption | OD plan v2.26 + workspace + per-axis row bumps + retirement batch-36 |
| Revision policy | Delta-only spec file; v1.26 + earlier PRESERVED VERBATIM per workspace `CLAUDE.md` §2.3 convention |
| Cross-axis cascade | ZERO (intra-OD-axis canonical-reading amendment) |
| Production code at apply | NEW `tail_keep_classification.py` + NEW `tail_keep_span_processor.py` at `harness-od`; EXTEND `lifecycle/span_processor.py` at `harness-runtime` (NEW `tail_keep_processor` field + production-surface wrap gate) |
| Test posture | 3388/3388 tests pass + 10 skipped (was 3367 + 10 pre-arc; +21 NEW at `test_tail_keep_span_processor.py` + `test_lifecycle_span_processor.py`) |
