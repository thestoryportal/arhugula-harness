# Phase 7 sub-phase 7d — substitution retirement events, batch 3 (4 retired)

**Filed:** 2026-05-20, Phase 7 sub-phase 7d, U-RT-58 landing arc.
**Skill:** `phase-7-substitution-retirement` §8.1 (workspace progress ledger).
**Authority:** U-RT-58 landing per `.harness/class_1_tension_cp_3_retry_breaker_composer_underspec.md` (Path A ratified 2026-05-20 at `7fe2c95`) + `Spec_Harness_Runtime_v1.md` v1.5 §14.6 C-RT-16 (in-Phase-7 amendment with canonical CP §3.5 attribute set per `.harness/class_1_tension_c_rt_16_retry_attribute_drift.md` Path A) + `Implementation_Plan_Harness_Runtime_v2_4.md` (`.harness/phase-2-session-3-track-a-atomic-decomposition.md`) U-RT-58 acceptance criteria all green.

---

## §0 Batch context

**4 substitutions retire** in this batch:

- **H_T-CP-3** (§1): per-layer time-budget + `retry.*` 6-attribute namespace + dual-emission — RETIRED at production retry-attempt-span emission site (the U-RT-58 wrapper).
- **H_T-CP-4** (§2): fallback chain composition + cross-family fallback — RETIRED at production candidate-iteration loop ownership.
- **H_T-CP-5** (§3): routing attribute namespaces + per-class sampling — PARTIAL (batch 2) → RETIRED (this batch) at production retry-attempt-span inheritance preservation.
- **H_T-CXA-5** (§4): OD → CP inversion (`harness.breaker.*` substrate-anchored-outside-CP) — RETIRED at production `harness.breaker.*` transition emission site via the U-RT-58 wrapper's `breaker.record_*` → `emit_breaker_transition_event` chain.

4 H_T substitutions transition **STILL-BOUNDED** / **PARTIAL** (prior batches) → **RETIRED** (this batch) under condition A ∧ condition B per X-AL-2:

- **Condition A** (cited unit IDs landed): CP axis 58/58 complete at 7b (per `[[phase-7-bootstrap-status]]`); U-RT-58 landed this arc (Runtime spec v1.5 §14.6 C-RT-16 contract + plan v2.4 body + 14 tests green + AC #9 smoke-test assertion at full bootstrap path); CXA-5 endpoint dependencies satisfied (H_T-OD-2 RETIRED batch 2 + H_T-CP-24 RETIRED authoring close v1 §1).
- **Condition B** (H_E surface no longer invoked at substitution site): evaluated per substitution against H_T runtime at U-RT-58 landing head under the U-RT-58-completes-Track-A-runtime-composition-surface reading. The retry/breaker/fallback wrapper at `harness-runtime/src/harness_runtime/lifecycle/retry_breaker_fallback.py:RetryBreakerFallbackDispatcher` is the production retry/breaker/fallback orchestration site previously absent (Q2a-deferred at U-RT-52, lifted by U-RT-58); its presence discharges the multi-composer gate for the three cited retirement primitives + the inversion-seam cascade.

Cumulative retirement count: **15 / 49 (batch 2)** + **4 / 49 (this batch RETIRED)** = **19 / 49 (38.8%)**.

PARTIAL count: 2 (CP-5 + AS-8 at batch 2) → 1 (AS-8 only — CP-5 transitions to RETIRED this batch).

§6.3.2 F-CP-01 Stage 3b inversion cascade: **FULLY DISCHARGED** at this batch. Both endpoints (OD-2 + CP-24) retired pre-batch; this batch lands the production `harness.breaker.*` emission site that activates the inversion seam end-to-end.

§9 Class 2 multi-LLM commitment surface: **CLOSED** (U-RT-52 close, preserved through this batch).

---

## §1 H_T-CP-3 — Per-layer time-budget + `retry.*` 6-attribute namespace + dual-emission

| Field | Content |
|---|---|
| Substitution ID | H_T-CP-3 |
| Primitive | Per-layer time-budget + `retry.*` 6-attribute namespace + dual-emission (per C-CP-03 §3 + §3.5 + ADR-D6 v1.2 §1.2.2.1 retry-attempt child span schema) |
| Spec contract | C-CP-03 + C-RT-16 (new at Runtime spec v1.4; canonical attribute set restated at v1.5) |
| Retirement event timestamp | Phase 7 sub-phase 7d U-RT-58 landing arc, 2026-05-20; verified against U-RT-58 head at commit `0190dc2` |
| Condition A verification | Cited carriers U-CP-03 (per-layer time-budget) → U-CP-07 (`fallback.*` + `harness.breaker.*` + `retry.*` namespaces; v2.3 amendment: retry.* extended to 6-attribute child span schema + parent-span event 3-field schema + dual-emission discipline) landed at 7b (CP 58/58 complete per `[[phase-7-bootstrap-status]]`). New runtime carrier U-RT-58 landed this arc (C-RT-16 contract + `RetryBreakerFallbackDispatcher` wrapper + 14 tests green); canonical `RETRY_ATTEMPT_CHILD_SPAN_SCHEMA` carrier already landed at `harness_cp.retry_fallback_namespace` (U-CP-07 §3.5 6-attribute carrier surface) |
| Condition B verification | `harness-runtime/src/harness_runtime/lifecycle/retry_breaker_fallback.py:RetryBreakerFallbackDispatcher._run_per_candidate_attempts` is the production retry-attempt span emission site. Per-attempt span (`harness.runtime.retry_attempt`) carries the canonical CP §3.5 6-attribute namespace: `retry.attempt_number` (1-indexed), `retry.original_span_id` (16-hex outer-span-id), `retry.delay_ms` (jittered backoff in ms), `retry.cause_attribution` (open-set string from C5 catalog), `retry.fail_class` (`ValidatorFailClass` enum value), `engine.replay_disposition` (via `REPLAY_DISPOSITION_MAPPING[binding.engine_class]`). Substitution mechanism (H_E-direct: SDK internal retries invisible + `Bash(retry-then-next)` shell-out) no longer invoked at runtime substitution site — runtime owns the per-candidate retry loop with full-jitter backoff via `compute_full_jitter_delay_seconds`. Hand-rolled per CLAUDE.md §3.2 framework-pull discipline (NO tenacity / pybreaker / circuitbreaker) |
| Cross-axis dependency cascade | §6.3.2 F-CP-01 Stage 3b inversion cascade activated: with CP-3 RETIRED and runtime emitting canonical `retry.*` namespace at every attempt, the precondition for CXA-5 retirement (production retry/breaker emission site) is satisfied. CXA-5 retires this batch (§4 below) |
| Evidence anchor | `retry_breaker_fallback.py` per-attempt span attribute emission (lines 365-471) + 14-test suite at `tests/test_lifecycle_retry_breaker_fallback.py` (all green; AC #4 verifies canonical 6-attribute namespace emission). Runtime spec v1.5 §14.6 step 4 cites the landed carrier `harness_cp.retry_fallback_namespace.RETRY_ATTEMPT_CHILD_SPAN_SCHEMA` as producer-side reference |

---

## §2 H_T-CP-4 — Fallback chain composition + cross-family fallback

| Field | Content |
|---|---|
| Substitution ID | H_T-CP-4 |
| Primitive | Fallback chain composition with cross-family fallback (multi-step chain orchestration over `(provider, model)` candidates per C-CP-04 §4 + §4.3 cross-family attribution flags) |
| Spec contract | C-CP-04 + C-RT-16 |
| Retirement event timestamp | Phase 7 sub-phase 7d U-RT-58 landing arc, 2026-05-20 |
| Condition A verification | Cited carriers U-CP-04 (`RoutingManifest`) + U-CP-05 (`fallback.exhausted` event semantics + chain composition per C-CP-04 §4.2) landed at 7b. U-RT-58 landed this arc; production candidate-iteration loop owns the chain composition over `FallbackChain` candidates |
| Condition B verification | `RetryBreakerFallbackDispatcher.dispatch` (lines 226-302) owns the per-step candidate-iteration loop. Iterates `ctx.fallback_chain` candidates starting with `chain.primary`; advances via `advance_or_raise(chain, candidate)` on per-candidate exhaustion (returns next candidate + `OnFailureResult` carrying the §4.3 cross-family attribution flags). On chain exhaustion emits `fallback.exhausted` event on outer span with attributes per C-CP-04 §4.2 (`fallback.chain_length`, `fallback.last_failure_class`, `fallback.exhaustion_cause`) and raises typed `RetryBreakerFallbackExhaustedError` mapping to new `RT-FAIL-FALLBACK-EXHAUSTED` fail class. Substitution mechanism (H_E-direct: `--fallback-model` single-target only + manual `Bash(retry-then-next)` shell-out) no longer reachable from runtime composers — `--fallback-model` does NOT carry multi-step chain + does NOT carry cross-family fallback selection; both surfaces are now runtime-owned |
| Cross-axis dependency cascade | §6.3.2 cascade discharged jointly with CP-3 (this batch §1); CXA-5 retires this batch (§4 below) |
| Evidence anchor | `retry_breaker_fallback.py:_advance_or_exhaust` (lines 304-328) + `fallback.exhausted` event emission + `RetryBreakerFallbackExhaustedError` typed-error path. Test coverage: `test_fallback_exhausted_emits_and_raises_typed` + `test_iterates_three_candidates_until_success` + `test_payload_shape_error_treated_as_fail_fast` + `test_single_candidate_chain_fail_fast_exhausts` |

---

## §3 H_T-CP-5 — Routing attribute namespaces + per-class sampling (PARTIAL → RETIRED)

| Field | Content |
|---|---|
| Substitution ID | H_T-CP-5 |
| Primitive | Routing attribute namespaces inheritance + per-class sampling (per C-CP-05 §5.1 inheritance composition from `llm.inference` parent span; C-CP-21 §21.5 retry-surface sampling dispositions) |
| Spec contract | C-CP-05 (inheritance composition), C-RT-16 (runtime span hierarchy preservation) |
| Retirement event timestamp | Phase 7 sub-phase 7d U-RT-58 landing arc, 2026-05-20 |
| Prior status | PARTIAL (batch 2 — LLM dispatch site present, retry/breaker wrappers Q2a-deferred) |
| New status | **RETIRED** (this batch — retry/breaker wrappers landed at U-RT-58) |
| Condition A verification | Cited carriers U-CP-11 (`lease.*` namespace) + U-CP-12 (engine event_history attribute) landed at 7b. U-RT-58 landed this arc; the three-level OTel span hierarchy (outer `harness.runtime.retry_breaker_fallback` → per-attempt `harness.runtime.retry_attempt` → inner `gen_ai.{provider}.{operation}`) is materialized at production execution path |
| Condition B verification | `RetryBreakerFallbackDispatcher.dispatch` opens the outer span as parent of per-attempt spans (verified via `test_nested_span_hierarchy_outer_parent_of_attempts`); per-attempt spans become parents of the inner C-RT-15 `gen_ai.*` span via OTel's `start_as_current_span` context propagation. The `routing.*` attribute namespace (per C-CP-05 §5.1 inheritance composition from `llm.inference` parent span) inherits naturally through the three-level hierarchy; the wrapper does not break inheritance. Per-class sampling discipline (head sampler picks outer; tail sampler picks per-attempt; inner GenAI always-sampled per OTel GenAI semconv) is operative at runtime. Substitution mechanism (per Meta-Architecture §5.4 "Depends on H_T-CP-1, H_T-CP-2") is no longer providing the substrate — CP-1 (batch 2) + CP-2 (batch 2) + CP-3 (this batch) + CP-4 (this batch) all RETIRED, so CP-5's dependency chain is fully discharged |
| Cross-axis dependency cascade | None at retirement event (CP-5 retirement does not gate other primitives per Meta-Architecture §6.3) |
| Evidence anchor | `retry_breaker_fallback.py` nested-span CM nesting (outer L235 → inner per-attempt L365) + smoke-test verification at `test_run_smoke.py::test_e2e_bootstrap_shutdown_round_trip` (AC #9 wrapper-type assertion). Test coverage: `test_nested_span_hierarchy_outer_parent_of_attempts` verifies parent-span-id linkage via `InMemorySpanExporter` |

---

## §4 H_T-CXA-5 — OD → CP inversion (`harness.breaker.*` substrate-anchored-outside-CP)

| Field | Content |
|---|---|
| Substitution ID | H_T-CXA-5 |
| Primitive | OD → CP inversion: `harness.breaker.*` 7-attribute namespace owned by OD spec (per C-OD-07 §7.1), emitted by CP-side breaker state machine, consumed at the CP `retry.*` span emission site. F-CP-01 Stage 3b inversion seam (CXA v2.1 §2.3.7) |
| Spec contract | C-OD-07 §7.1 (OD-side canonical schema), C-CP-21 §21.5 (CP-side breaker-event composition), C-RT-16 (runtime wrapper emits via registry delegation) |
| Retirement event timestamp | Phase 7 sub-phase 7d U-RT-58 landing arc, 2026-05-20 |
| Condition A verification | §6.3.2 cascade endpoints both retired: H_T-OD-2 RETIRED at batch 2 (per `.harness/phase-7d-retirement-events-batch-2.md` §4 — GenAI semconv 1.41.0 + tracer provider operational) + H_T-CP-24 RETIRED at authoring close (per Meta-Architecture §5.4 row + CP CLAUDE.md §4.1 — substrate seam exports + F2-12 closure manifest, authoring-only). Cited joint-landing U-OD-09 + U-CP-54 §24.1.C both landed at 7b. U-RT-58 landed this arc, providing the production `harness.breaker.*` emission site that activates the inversion seam end-to-end |
| Condition B verification | `RetryBreakerFallbackDispatcher._emit_breaker_transition` (lines 484-492) delegates to `RuntimeRetryBreaker.emit_breaker_transition_event` which composes the OD-canonical `HarnessBreakerEvent` and emits the `breaker.tripped` event per C-OD-07 §7.1 7-attribute schema. Production invocation path: on each candidate's breaker transition (`record_failure()` / `record_success()` returns a non-None `BreakerTransition`), the composer calls the registry's emission method passing the outer wrapper span as `parent_span_ref`. The inversion is operational: OD owns the schema declaration (`harness_od.harness_breaker_schema.HarnessBreakerEvent` 7-attribute Pydantic model); CP-side breaker state machine emits via `harness_runtime.lifecycle.retry_breaker.RuntimeRetryBreaker.emit_breaker_transition_event` (an L8 LOOP_INIT primitive); runtime wrapper is the production callsite. Substitution mechanism (per Meta-Architecture §5.6 "Breaker primitive absent both endpoints") no longer applies — both endpoints + production callsite are now runtime-grounded |
| Cross-axis dependency cascade | None onward — CXA-5 is a terminal cascade node per §6.3.2 |
| Evidence anchor | `retry_breaker_fallback.py:_emit_breaker_transition` + landed `harness_od.harness_breaker_schema.HarnessBreakerEvent` 7-attribute carrier + landed `harness_runtime.lifecycle.retry_breaker.RuntimeRetryBreaker.emit_breaker_transition_event`. Test coverage: `test_breaker_transition_emitted_via_registry` verifies the registry-delegation chain via spying-registry wrapper |

---

## §5 Bounded-residual carry-forward note

No new bounded-residual entries surfaced at this batch.

The PRICE_TABLE_REF substitution carry-forward per `[[fork-price-table-ref-substitution-retirement]]` remains the same operator-known residual (rate-table authoring ~100-200 LOC; deferred to sub-phase 7d closure pass per memory note). Not affected by this batch.

H_T-AS-8 PARTIAL (batch 2) — `anthropic.*` 4-attribute cache subset live, remaining 6 `anthropic.*` attrs + `mcp.*` namespace still bounded on Phase-3+ tool-invocation runtime composer per v2 ledger §9.2.2. Not affected by this batch.

---

## §6 Retirement gradient update

Per `Phase_7_Meta_Architecture_v1.md` §6 self-hosting milestone gradient + workspace root `CLAUDE.md` §4.2 X-AL-2 retirement criterion fidelity:

| Axis | Pre-batch (RETIRED + PARTIAL) | This batch | Post-batch (RETIRED + PARTIAL) |
|---|---|---|---|
| IS  | 0 RETIRED + 0 PARTIAL of 9 | — | 0 RETIRED + 0 PARTIAL of 9 |
| AS  | 2 RETIRED + 1 PARTIAL of 6 | — | 2 RETIRED + 1 PARTIAL of 6 |
| CP  | 4 RETIRED + 1 PARTIAL of 22 (incl. CP-24 authoring) | CP-3 + CP-4 + CP-5 RETIRED | 7 RETIRED + 0 PARTIAL of 22 |
| OD  | 2 RETIRED + 1 PARTIAL of 8 | — | 2 RETIRED + 1 PARTIAL of 8 |
| CXA | 0 RETIRED + 0 PARTIAL of 5 | CXA-5 RETIRED | 1 RETIRED + 0 PARTIAL of 5 |

Cumulative across all axes:
- **Pre-batch:** 15 / 49 RETIRED (30.6%) + 2 PARTIAL.
- **This batch:** +4 RETIRED (CP-3 + CP-4 + CP-5 + CXA-5); -1 PARTIAL (CP-5 transitions out).
- **Post-batch:** **19 / 49 RETIRED (38.8%)** + 1 PARTIAL (AS-8 only).

Per Workflow v1.8 §2.7.5 self-hosting milestone gradient as Phase 7 progress metric: 38.8% retired. Remaining 30 substitutions consist of (a) 14 STILL-BOUNDED CP-axis primitives gated on HITL/validator/sub-agent composers (per v2 ledger §9.2.5), (b) 5 STILL-BOUNDED OD-axis primitives (collector daemon + sampler + redaction + preservation invariants — per `harness-od/CLAUDE.md` §4.1 + `[[fork-cost-record-audit-ledger-wiring-residual]]`), (c) 9 IS-axis primitives (most awaiting Track B operator-facing surface), (d) 1 AS-axis PARTIAL (AS-8 anthropic.* remaining + mcp.*), (e) 4 CXA primitives (CXA-1..4 remaining), (f) various bounded-residual cases per the §5 carry-forward note above.

---

## §7 Cross-references

- `Phase_7_Meta_Architecture_v1.md` §5.4 (CP-axis substitution table) + §5.6 (CXA-axis substitution table) + §6.3.2 (F-CP-01 Stage 3b inversion ordering cascade) + §7.7 (X-AL-2 retirement criterion fidelity).
- `Spec_Harness_Runtime_v1.md` v1.5 §14.6 C-RT-16 + §15 traceability row for U-RT-58.
- `.harness/phase-2-session-3-track-a-atomic-decomposition.md` v2.4 L9-bis U-RT-58 + §6 7d substitution-retirement preview.
- `.harness/phase-7d-retirement-events-batch-1.md` (8 events; 2026-05-20 batch 1).
- `.harness/phase-7d-retirement-events-batch-2.md` (5 events incl. 3 RETIRED + 2 PARTIAL; 2026-05-20 batch 2; U-RT-52 close arc).
- `.harness/phase-7d-retirement-ledger-v2.md` §5 CP-row evidence framework + §9.2.3 / §9.2.5 multi-composer gating.
- `.harness/class_1_tension_cp_3_retry_breaker_composer_underspec.md` (filed + Path A ratified + RESOLVED 2026-05-20).
- `.harness/class_1_tension_c_rt_16_retry_attribute_drift.md` (filed + Path A ratified + RESOLVED 2026-05-20).
- `.harness/class_3_tension_c_rt_16_spec_internal_drift.md` (filed 2026-05-20, OPEN bounded; deferred to next runtime-spec amendment).
- Workspace root `CLAUDE.md` §4.1 H_T ↔ H_E substitution discipline + §4.2 substitution retirement discipline.
- `harness-cp/CLAUDE.md` §4.1 — CP-axis substitution table requires update at the post-this-batch session-close (CP-3 + CP-4 + CP-5 transitions; cumulative 7/22 retired).

---

## §8 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/phase-7d-retirement-events-batch-3.md` |
| Authored at | Phase 7 sub-phase 7d, U-RT-58 landing arc, 2026-05-20 |
| Authoring authority | `phase-7-substitution-retirement` skill §8.1 (workspace progress ledger) |
| Retirement event count | 4 RETIRED (CP-3 + CP-4 + CP-5 + CXA-5) |
| Cumulative post-batch | 19 / 49 RETIRED (38.8%) + 1 PARTIAL (AS-8) |
| Cross-axis cascades discharged | §6.3.2 F-CP-01 Stage 3b inversion (CP-3 endpoint + CP-24 endpoint + production emission site all live) — CXA-5 RETIRED |
| Successor work | Update `harness-cp/CLAUDE.md` §4.1 substitution-table status entries (CP-3/4/5 → RETIRED); update `.harness/phase-7d-retirement-ledger-v2.md` §5 CP rows superseded; CP plan v2.11 §0.6 carry-forward update (CP-3/4/5 retirement at v2.12 revision pass); next batch of retirement events likely gates on HITL/validator/sub-agent composers landing (per v2 ledger §9.2.5) |
| Revision policy | Workspace-internal log artifact; corrections via re-author + supersede-note at next batch event |
