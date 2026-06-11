# `Spec_Operational_Discipline` v1.28 — delta over v1.27

**Filed:** 2026-06-10
**Authoring authority:** Phase 7 — R-CL-P4 spec-completion deferrals (OD bounded-buffer follow-on; Category-1 Claude-closeable per `.harness/post-mvp-full-closure-plan-v1.md` line 45 + Phase P4 line 149)
**Predecessor:** `Spec_Operational_Discipline_v1_27.md` (v1.27 — H_T-OD-3 gate-(a) tail-keep-on-classification closure at the runtime span-processor materializer)
**Revision shape:** Delta-only spec file per workspace `CLAUDE.md` §2.3 OD spec row convention. v1.27 + v1.26 + ... + v1 file bodies PRESERVED VERBATIM. v1.28 carries change-note + §1 canonical-reading amendment only.

---

## Change-note (v1.27 → v1.28)

**Supersession (LEADS).** The v1.27 §2(a) adjacent observation — *"Bounded-buffer carve-out (MVP scope-lock): the MVP `TailKeepSpanProcessor` does NOT bound buffer size by trace count or by per-trace span count ... Future operator-tunable bounds at `CollectorConfig` are a follow-on arc per §9.3 implementer-discretion. NOT patched at v1.27 per FM-2."* — is **CLOSED at v1.28**. The follow-on arc is materialized: the production `TailKeepSpanProcessor` now enforces two operator-tunable ceilings supplied from `CollectorConfig`, per the §9.3 implementer-discretion grant.

The v1.27 §2(a) body is **PRESERVED VERBATIM** at `Spec_Operational_Discipline_v1_27.md` §2(a) as a frozen change-note describing the v1.27 MVP state (which did not bound); it is accurate about v1.27 and is NOT edited. v1.28 records the subsequent closure.

Per OD spec §C-OD-09 §9.3 the bounded-buffer parameters were always implementer-discretion (the v1.27 §2(a) observation explicitly named them "a follow-on arc per §9.3 implementer-discretion"). v1.28 is therefore a **canonical-reading reconciliation closing an implementer-discretion deferral** — the same delta shape v1.27 used to close §9.3 elements (a)/(b)/(c) — NOT a spec-extension-from-scratch.

ZERO new contract; ZERO new C-OD-NN field; ZERO new namespace; ZERO breaking change at any §C-OD-09 / §C-OD-10 surface; ZERO cross-axis cascade. The two ceilings are fields on the runtime impl config `CollectorConfig` (`harness-runtime/src/harness_runtime/types.py`), not contract fields on any C-OD-NN type — consistent with the v1.27 "ZERO new contract" framing for an implementer-discretion materialization.

---

## §1 Canonical-reading amendment

### §1.1 §C-OD-09 §9.3 bounded-buffer implementer-discretion clause — closure

v1.27 §9.3 footer element (a) closed the tail-based **algorithm** with the per-trace-completion-replay choice; the buffer was left **unbounded** (v1.27 §2(a) carve-out). v1.28 closes the bounded-buffer follow-on:

| Bounded axis (v1.27 §2(a) named both) | Pre-v1.28 status | v1.28 closure disposition |
|---|---|---|
| Buffer size by **trace count** | UNBOUNDED (MVP carve-out) | **CLOSED**: operator-tunable ceiling `CollectorConfig.tail_keep_max_buffered_traces` (default 4096, validated `> 0`). When a NEW trace that will REMAIN pending would exceed the ceiling, the **oldest buffered trace is evicted** (drop-oldest / dict-insertion-order FIFO) and counted at `TailKeepSpanProcessor.dropped_trace_count`. A new trace whose first observed span is already its root-close materializes + frees its slot in the same `on_end` (no steady-state pressure), so it does NOT evict. This contains the pathological case (a producer opening 10^6 roots without closing them): the stale never-closing traces are oldest, so they are shed first. |
| Buffer size by **per-trace span count** | UNBOUNDED (MVP carve-out) | **CLOSED**: operator-tunable ceiling `CollectorConfig.tail_keep_max_spans_per_trace` (default 4096, validated `> 0`). Overflow **non-root** spans are dropped and counted at `TailKeepSpanProcessor.dropped_span_count`; the root-close span ALWAYS processes so the trace materializes and frees its slot (no leak). |

**Eviction-policy rationale + alternative consideration** are documented at the carrier module docstring (`harness-od/src/harness_od/tail_keep_span_processor.py`), per the v1.27 §9.3 element-(a) "rationale in docstring" pattern. Summary: drop-oldest may evict a *keep-flagged* trace's buffered tree-context under pressure, but the §10.2 trigger span itself is in the §9.2 always-sampled set and was **forwarded immediately** at `on_end` (bypasses the buffer) — the failure *signal* survives; only buffered sibling *context* is shed. This is consistent with the v1.27 §2(c) "trust-sampler-on-base-rate, best-effort preservation" posture. Alternative considered and rejected: drop-NEW (reject the incoming trace) — it lets stale never-closing traces hog the buffer indefinitely, the opposite of the pathology the bound exists to contain. Keep-flag-preferential eviction is a documented future refinement (O(n) scan vs O(1) drop-oldest; not warranted because the failure signal is already preserved).

### §1.2 Production-default + backward-compat

The production materializer (`harness-runtime/src/harness_runtime/lifecycle/span_processor.py:materialize_span_processor_stage`) passes both `CollectorConfig` ceilings to the `TailKeepSpanProcessor` at the production-surface wrap site, so **production is bounded by default**. The processor's `__init__` ceilings default to `None` (unbounded) — preserving the v1.27 MVP behavior for direct construction (existing unit tests are unaffected). LOCAL_DEVELOPMENT is unchanged: §9.1 head-based mandate means no tail-keep wrap, so no buffer exists to bound.

### §1.3 §9.3 footer post-v1.28 canonical reading

§9.3 footer elements (a)+(b)+(c) CLOSED at v1.27; element (d) (cross-SDK conformance) PRESERVED as deferred-indefinitely per single-SDK scope. The v1.27 §2(a) bounded-buffer adjacent observation is CLOSED at v1.28 (this amendment). No §9.3 footer **row text** is amended; the carrier-level reading documents the bound-materialization shape.

---

## §2 Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Operational_Discipline_v1_28.md` |
| Supersedes | `Spec_Operational_Discipline_v1_27.md` as canonical HEAD (delta-only chain; v1.27 body preserved verbatim) |
| Carrier code | `harness-od/src/harness_od/tail_keep_span_processor.py` (bounds + counters + eviction); `harness-runtime/src/harness_runtime/types.py` (`CollectorConfig.tail_keep_max_buffered_traces` + `tail_keep_max_spans_per_trace`); `harness-runtime/src/harness_runtime/lifecycle/span_processor.py` (production threading) |
| Verification | `harness-od/tests/test_tail_keep_span_processor.py` (drop-oldest eviction + per-trace overflow + bounds-don't-affect-legitimate); `harness-runtime/tests/test_config_collector_config.py` (defaults + `> 0` validation); `harness-runtime/tests/test_lifecycle_span_processor.py::test_production_surface_threads_collector_buffer_bounds` (e2e config→materializer→enforced bound under a pathological producer) |
| Clearance | marker filed at `.harness/clearance/Spec_Operational_Discipline-v1_28-cleared-2026-06-10.md` |
| Revision policy | Canonical for this workspace; revisions route to design-phase back-flow per `harness-od/CLAUDE.md` §5.1 |
