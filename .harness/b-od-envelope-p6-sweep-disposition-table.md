# B-OD-ENVELOPE-P6-SWEEP — OD deferral-envelope phase-6 disposition sweep

**Status:** CLOSED. Disposition table for the 11 remaining `closure_target=phase_6_implementation` deferral-envelope entries (C-OD-17/18/19 already dispositioned by their own Wave-2 arcs) + the 4 post-v1.2 discretion blocks. No spec/code change — this is a grounding-only classification sweep; 3 genuine forward gaps are registered, not built.

**Method.** For each entry: read the exact `Spec_Operational_Discipline_v1_2.md` "Deferred to implementation discretion" sentence, grep+read the codebase for realizing code, classify `already-realized` (cite the consumer-visible surface) / `scoped-build` (register a follow-on) / `genuinely-discretionary-no-op` (cite the discretion sentence directly). An Explore agent did the first-pass code search; every "NOT FOUND" (negative) claim it returned was independently re-verified by direct grep/read before being trusted, per the standing discipline that sweep negatives are the unreliable half of a delegated search. One agent false-negative was caught and corrected in this pass (§1 below).

---

## 1. C-OD-01 §1.5 — cell-identification / cell-transition / cell-binding persistence

**Deferred sentence.** "Specific cell-identification API surface (the manifest declaration shape, the configuration file format, the runtime cell-binding handshake); specific cell-transition state-machine implementation; specific cell-binding persistence mechanism beyond the harness manifest residence per `Spec_Information_Substrate_v1.md` C-IS-10 §10.4."

§1.5's three named invariants disposition **separately**:

- **Active-cell identifiability** — **ALREADY-REALIZED.** `RuntimeConfig.persona_tier` + `RuntimeConfig.deployment_surface` (`harness-runtime/src/harness_runtime/types.py`), loaded via the 3-source `harness.toml` / env / CLI precedence loader (`config_source.py`), IS the cell-identification API surface (manifest/config-file format + runtime handshake). `CellID(persona_tier=..., deployment_surface=...)` (`harness-od/src/harness_od/observability_matrix.py`) is the canonical frozen product-key built from it.
- **Excluded-cell binding rejection** — **ALREADY-REALIZED, verified independently** (an initial agent-drafted sweep incorrectly reported no call site for this — corrected here by direct grep+read). `materialize_tracer_provider_stage` (`harness-runtime/src/harness_runtime/lifecycle/tracer_provider.py:230-236`) constructs the `CellID` from the bound config and calls `reject_excluded_cell(cell)` before resolving the per-cell sampler base rate — the excluded cell (multi-tenant-compliance × local-development) is structurally rejected at bootstrap, not silently accepted.
- **Cell-transition observable (before/after tuple recording)** — **genuinely NOT built.** Independently grepped for `before_cell`/`after_cell`/`prior_cell`/`transition_observed` and equivalents across `harness-runtime/src`, `harness-od/src`, `harness-cp/src`, `harness-is/src`: zero hits. `RuntimeConfig` is read fresh at each process start; nothing persists or compares against a prior binding, so no cell-transition event is ever emitted.

**Disposition: scoped-build (narrow).** Register only the cell-transition-observable sub-invariant (not the whole §1.5 contract, which is 2/3 already realized) — a before/after cell-binding record emitted when the operator changes persona_tier/deployment_surface across process restarts. No dedicated persistence path class exists at `harness-is/src/harness_is/path_class_registry.py` (`PathClass` is a closed 4-value enum with no cell-binding member) — a future build would need either a 5th `PathClass` or reuse of the existing `STATE_LEDGER` class.

---

## 2. C-OD-04 — Unified span schema base layer (OTel GenAI semconv 1.41.0)

**Deferred sentence.** Specific OTel SDK binding per language ecosystem; specific span exporter wiring; specific instrumentation library version pinning per language; specific cross-SDK conformance test harness.

**Disposition: already-realized** for the single (Python) ecosystem this codebase targets. `otel_genai_base.py` binds the real `opentelemetry.trace.Span` type directly (not a harness abstraction); `span_processor.py:216-218` wires `BatchSpanProcessor(OTLPSpanExporter(...))`; `harness-od/pyproject.toml` + `harness-runtime/pyproject.toml` pin `opentelemetry-{api,sdk,exporter-otlp}>=1.30`.

**Cross-SDK conformance harness — genuinely-discretionary-no-op.** The codebase is single-language (Python 3.12+ per `Target_Stack_Commitment_v1.md`); there is no second SDK to conform against. A "cross-SDK" harness is not applicable until/unless a second-language SDK is ever adopted — not a build gap today.

---

## 3. C-OD-05 — 15 specialization-layer namespace ingestion contract

**Deferred sentence.** Specific cross-SDK namespace conformance test harness; specific namespace-version-migration protocol (spec itself: "deemed out of scope at v1; assumed additive at source D-ADR revisions"); specific runtime namespace-presence validation mechanism.

**Disposition: already-realized.** `namespace_map.py:219` `assert_source_authoritative_declarer` is a real runtime-probe-style namespace-presence validator (raises `AuthorityViolation`); `as_source_namespace_verification.py` runs cross-axis (OD-vs-AS) conformance checks against the declared namespace set. Namespace-version-migration protocol is explicitly out-of-scope-at-v1 per the spec's own text — genuinely-discretionary-no-op, not a gap. Cross-SDK conformance: same not-applicable reasoning as item 2.

---

## 4. C-OD-06 — F3 capability-floor (iv) lifecycle event-to-span-event mapping

**Deferred sentence.** Specific span-event emission API per OTel SDK; specific sibling-span parent-correlation mechanism; specific retry-span lifecycle; specific replay-trace-emission semantics under engine replay.

**Disposition: already-realized.** `retry_breaker_fallback.py:510-511,548,768` use the real `Span.add_event(...)` API for `fallback.triggered`/`retry.skipped`. Retry-span lifecycle is a concrete open-on-attempt/close-on-resolution `with tracer.start_as_current_span("harness.runtime.retry_attempt")` block (lines 816-826); sibling-span correlation is resolved via both W3C trace-context nesting AND an explicit `retry.original_span_id` attribute. `harness_breaker_schema.py:152-195` `emit_breaker_trip_span_event` enforces the 4 non-optional attributes and always sets `sampled=True`. Replay-trace-emission semantics thread `engine.replay_disposition` from a real mapping table, with the spec's own F2-12 forward-reference honestly still marked open at the composing D1 layer (not this contract's gap).

---

## 5. C-OD-07 — `harness.breaker.*` seven-attribute breaker-trip event schema

**Deferred sentence.** Specific OTel/OTLP span emission implementation; specific attribute-validation mechanism at emission time; specific breaker-state-machine implementation; specific subscription wiring between C10 gate policy and C7 span emission ("composes at Phase 6+ implementation").

**Disposition: three of four sub-items already-realized; the fourth is a genuine, verified gap.**
- Span emission + runtime attribute validation: `harness_breaker_schema.py:152-195` `emit_breaker_trip_span_event`, called from production at `retry_breaker.py:434`.
- Breaker-state-machine: `retry_breaker.py:179-285` `class BreakerStateMachine` — hand-rolled per the workspace's framework-pull discipline (no `pybreaker`), 3-state (`record_failure`/`record_success`/`attempt_half_open`), registry-backed.
- **C10-gate ↔ C7-span subscription wiring — genuinely NOT built, independently verified.** Grepped `harness-cp/src/harness_cp/gate_level_rule.py` and `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py` directly for any `breaker` reference: the only hit is an unrelated docstring cross-reference, not a data dependency. `GateLevelInput`'s composition (per the separately-landed B2-spec-2 `mcp_trust_tier` axis) has no breaker-state input. A breaker trip today emits its own span but never feeds the HITL `gate_level()` `max()` composition — no dynamic gate-tightening on repeated breaker trips.

**Register (scoped-build, not built here):** wiring a breaker-trip-frequency or breaker-state signal into the `gate_level()` composition (a new axis or an existing-axis input) would need a Class 1 fork to CP spec §19.1 first — this is a genuinely new committed behavior, and the spec's own text defers it explicitly ("composes at Phase 6+ implementation").

---

## 6. C-OD-08 — Namespace collision discipline

**Deferred sentence.** Specific runtime cross-namespace validation mechanism; specific attribute-namespace prefix enforcement at OTel SDK boundary; specific OTel-attribute-set version-pinning convention per language ecosystem.

**Disposition: already-realized via an alternate (call-site) mechanism, which the spec permits.** `namespace_collision_discipline.py:140` `enforce_otel_canonical_value` raises `CanonicalValueViolation` on the `anthropic.cache_*` vs `gen_ai.usage.input_tokens` cross-namespace invariant; `namespace_map.assert_source_authoritative_declarer` is a second cross-namespace authority check. The spec defers the "specific mechanism" (SDK-boundary hook vs. call-site check) — call-site validation is a spec-conformant choice, not a shortfall. Version-pinning: same single-ecosystem reasoning as item 2.

---

## 7. C-OD-09 — Tail-based sampling decision algorithm

**Deferred sentence.** Specific tail-based sampling decision algorithm; specific tail-keep-on-classification filter implementation per OTel SDK; specific always-sampled-event detection at SDK boundary; specific cross-SDK sampling-decision conformance test.

**Disposition: already-realized.** `composite_sampler.py:81-129` `HarnessCompositeSampler(Sampler)` (real OTel `Sampler` subclass) + `tail_keep_span_processor.py:140-169` `TailKeepSpanProcessor(SpanProcessor)` (real per-trace-completion buffering with documented eviction bounds) + `sampling_mode.py:239-263` `is_always_sampled` (runtime hook, 3 resolved regimes). Cross-SDK conformance: not-applicable, same as items 2/3.

---

## 8. C-OD-12 — Redaction discipline: default-off content + default-on structure

**Deferred sentence.** Specific OTLP-collector default-off filter implementation per cell; specific content-attribute encryption-in-flight mechanism *if content capture is enabled at operator override*; specific structure-attribute serialization format; specific hash-digest algorithm at attribute level (SHA-256 baseline).

**Disposition: default-off filter + hash-digest already-realized; encryption-in-flight is a live, reachable conditional gap — not discretionary-no-op.** `content_structure_discipline.py:212` `classify_attribute` + `redaction_span_processor.py:192-307` `RedactionSpanProcessor.on_end` strip `DEFAULT_OFF_CONTENT_ATTRIBUTES` per span; `redaction_token_audit.py` uses `hashlib.sha256(...).hexdigest()` matching the spec's cited baseline. **However**, `redaction_span_processor.py:138-169` `session_content_capture()` is a real, callable context manager an operator/caller can invoke *today* (`with session_content_capture(): api.run(workflow)`) at the solo-developer tier to enable raw content capture — at which point spans carry unredacted content to whatever exporter is configured, with **no attribute-level encryption**, only whatever transport-level TLS the exporter endpoint happens to use. This is not a hypothetical trigger; the toggle exists and is reachable in production code today.

**Register (conditional forward item, not built here):** an attribute-level encryption-in-flight mechanism for the `session_content_capture()`-enabled path. Not gating this arc's closure (no spec-committed default enables content capture; the exposure is operator-opt-in), but should not be filed as "not applicable" — it is a live gap the moment the toggle is used.

---

## 9. C-OD-13 — Per-persona-tier content-capture override gradient

**Deferred sentence.** Specific eval-grade redaction pipeline implementation; specific redaction-token format; specific per-session content-capture toggle UX; specific audit-ledger-entry emission API at the redaction boundary; specific SDK/wrapper boundary for pre-collector redaction injection.

**Disposition: already-realized**, the most fully-built of the 11 entries. `RedactionSpanProcessor` (`redaction_span_processor.py:192`) registered before `BatchSpanProcessor` (`span_processor.py:233`) is the pre-collector injection boundary; `OpaqueRedactionTokenizer` (`redaction_tokenizer.py:186`) produces `[REDACTED:{category}:{ordinal}]`-format tokens; `EvalGradeSemanticRedactionClassifier` (pattern-based, `redaction_tokenizer.py:94-141`) is wired specifically at multi-tenant-compliance (`span_processor.py:224-231`); `redaction_token_audit.py` + `AuditLedgerRedactionTokenMap` compose the audit-ledger-entry emission API. The toggle-**UX** surfacing (CLI vs config-file) is explicitly still marked deferred in the code's own docstring (`redaction_span_processor.py:45`) — consistent with the spec's own deferral, not a gap.

---

## 10. C-OD-22 — Bridging-arc traversal preservation

**Deferred sentence.** Specific transition-planning UX; specific cross-cell observability-config migration mechanism; specific transition-validation enforcement; specific bridging-arc-binding state machine.

**Disposition: the verification surface is already-realized but dormant; the state-machine/migration/UX pieces are genuinely NOT built, independently verified.** `bridging_arc_table.py` implements a real 8-transition table + `verify_transition` (3 in-cone dimensions with real PASS/FAIL logic; 3 out-of-cone dimensions structurally return PASS per the module's own honestly-documented "Class 3 informational disposition"). Grepped for callers of `verify_transition`/`reject_excluded_transition` outside `bridging_arc_table.py` itself: zero hits in `harness-runtime/src`, `harness-cp/src`, `harness-od/src` — the verification surface exists and is tested, but nothing in production ever *calls* it at an actual transition event, because nothing in production ever *records or triggers* a transition event (same root cause as item 1's cell-transition-observable gap). No config-migration mechanism, no transition-planning UX, and no stateful "bridging-arc-binding" object exist anywhere.

**Register (scoped-build, not built here):** this composes with item 1's registered gap — a real cell-transition event (persisted before/after `CellID` pair) is the prerequisite `verify_transition` needs a live caller for. Registering as one combined forward item rather than two: "cell-transition event emission + live `verify_transition` invocation at that event" is the natural single build.

---

## 11. C-OD-23 — Operational Discipline substrate seam exports surface

**Deferred sentence.** Specific cross-spec citation strings; specific seam-versioning convention if D6 ever revises beyond v1.2 closure of F2-12; specific Phase 6+ implementation-planning surface.

**Disposition: already-realized.** `substrate_seam_exports_aggregate_manifest.py` is the terminal aggregate exporter (`SubstrateSeamExportsManifest`, cross-axis edge counts, string-typed target identifiers to avoid cross-module import coupling). Seam-versioning convention: explicitly out-of-scope-at-v1 per the spec's own text ("D6 ever revises beyond v1.2 closure" — D6 has not) — genuinely-discretionary-no-op.

---

## 12-15. Four post-v1.2 discretion blocks (already pre-reviewed 2026-07-11; confirmed here)

Located at `design-substrate/Spec_Operational_Discipline_v1_8.md` (the v1.8 delta introducing C-OD-25..28).

| § | Contract | Deferred choice | Default chosen | Realized? |
|---|---|---|---|---|
| §25.5 | C-OD-25 workflow-envelope span emission | `workflow.step_count` granularity: terminal-close-only vs per-step counter | **terminal-close-only** (stated default) | Discretionary default, as-designed |
| §26.5 | C-OD-26 cost-attribution invocation | Per-billable-span cost-meter algorithm | **per-provider rate-table** at `C-OD-28 PRICE_TABLE_REF` | Realized — `rate_table_v1.py` |
| §27.5 | C-OD-27 sqlite write-path | Retention-policy implementation: cron background task vs lazy-on-write | **lazy-on-write** | Realized — confirmed at production per `Spec_Operational_Discipline_v1_25.md:65` ("PR #18 selects lazy-on-write... retention-after-INSERT in flush_to_sqlite") |
| §28.5 | C-OD-28 `PRICE_TABLE_REF` rate-table format | Default rate values | **placeholder values** at `rate_table_v1.py`, operator-updatable | Realized — `harness-od/src/harness_od/rate_table_v1.py` exists with operator-default rates for anthropic/openai/ollama |

All four: **genuinely-discretionary, already-realized-as-the-chosen-default.** No action.

---

## Summary

| Class | Count | Entries |
|---|---|---|
| Already-realized | 8 full + 2 partial (2/3 + verification-only) | C-OD-04, 05, 06, 08, 09, 12 (partial), 13, 23, + §25-28 (4) |
| Genuinely-discretionary-no-op | woven into the above | cross-SDK conformance (04/05/09), seam-versioning (23), namespace-version-migration (05) |
| Scoped-build — registered, not built | 3 combined items | (1) cell-transition-observable event + wiring `verify_transition` to it (C-OD-01 + C-OD-22, combined); (2) C10-gate ↔ breaker-trip subscription (C-OD-07); (3) attribute-level encryption-in-flight for the `session_content_capture()` path (C-OD-12, conditional) |

None of the 3 registered items block this arc's closure — each would be a genuinely new committed behavior requiring its own Class 1 fork (gate-composition axis, transition-event contract, or encryption mechanism) before implementation, per X-AL-3. Building any of them now, absent that fork, would be silent design extension.

## Verification note

An Explore agent performed the first-pass code search across all 15 items. Every "NOT FOUND" (negative) claim was independently re-verified by direct grep/read rather than trusted — this caught one false negative (C-OD-01's `reject_excluded_cell` call site, corrected in item 1 above) before it could have produced an overclaimed forward-item registration. The agent's positive (file:line) citations were spot-checked and held. `advisor()` consulted before finalizing; its guidance to scope item 1 narrowly (not overclaim the whole §1.5 contract as unbuilt) and to frame item 8's encryption-in-flight as a live conditional gap rather than not-applicable is incorporated above.

## Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/b-od-envelope-p6-sweep-disposition-table.md` |
| Arc | `B-OD-ENVELOPE-P6-SWEEP`, R-FS-2 Wave 3, third arc |
| Disposition | CLOSED — disposition table filed; 3 combined forward items registered, not built |
| No spec/code change | Grounding-only close |

*End of B-OD-ENVELOPE-P6-SWEEP disposition table.*
