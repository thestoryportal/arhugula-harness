# Phase 7 sub-phase 7d — substitution retirement events, batch 5 (LLM-dispatch end-to-end wiring completion)

**Filed:** 2026-05-20, Phase 7 sub-phase 7d, U-RT-59 async/sync fork Path B wiring arc.
**Skill:** `phase-7-substitution-retirement` §8.1 (workspace progress ledger).
**Authority:** U-RT-59 async/sync StepDispatcher Class 1 fork **RESOLVED** via Path B wiring landing (`d64d8cf` — INFERENCE_STEP bound through `SyncDispatcherFacade(ctx.llm_dispatcher)` at bootstrap stage 5 per `Spec_Harness_Runtime_v1.md` v1.6 §14.7.7 — spec text unchanged, already correct at v1.6; facade adapter documentation owed to Class 3 drift batch item 6). Predecessor commit: `84edc30` (facade discovery landing).

---

## §0 Batch context

**Status type: criterion-B re-affirmation + carve-out closure (NO new RETIRED transitions in this batch).**

The U-RT-59 async/sync StepDispatcher Class 1 fork (`.harness/class_1_tension_u_rt_59_async_sync_step_dispatcher.md`) carved INFERENCE_STEP routing-registry binding OUT of bootstrap stage 5 at v1.6 MVP. Per fork text:

> v1.6 MVP binds only `SUB_AGENT_DISPATCH` in the registry per the Class 1 fork on U-RT-58 wrapper async/sync mismatch (the async `llm_dispatcher.dispatch` does not compose with the sync driver call site as a registry binding). `INFERENCE_STEP` binding deferred to follow-on arc.

The carve-out had a strict-X-AL-2 consequence: although CP-1 / CP-3 / CP-4 / CP-5 were filed RETIRED at batches 2-3 against **production composer presence** at `lifecycle/llm_dispatch.py` + `lifecycle/retry_breaker_fallback.py`, the **driver-invocation execution path** required workflow-supplied dispatcher override (via `workflow.step_dispatchers` attribute per api.py:390) — production workflows without an override would route INFERENCE_STEP steps to a `StepKindDispatcherNotBoundError` raise, not to the production LLM-dispatch chain. The retirements were "composer exists" not "composer invoked end-to-end by default".

Path B wiring landing at `d64d8cf` closes this gap: bootstrap stage 5 now binds `INFERENCE_STEP → SyncDispatcherFacade(ctx.llm_dispatcher)` by default. Any workflow with INFERENCE_STEP steps that does NOT supply a `workflow.step_dispatchers` override now flows through the production dispatcher chain (RetryBreakerFallbackDispatcher → RuntimeLLMDispatcher → ProviderClient adapter → AsyncAnthropic / AsyncOpenAI / AsyncOllamaClient) end-to-end at execution time.

**Substitutions affected (re-affirmed; NO status change):**

| Substitution | Prior retirement | Batch 5 effect |
|---|---|---|
| H_T-CP-1 (multi-LLM routing core) | RETIRED batch 2 (2026-05-20, lifecycle/llm_dispatch.py production callsite) | Criterion B re-affirmed at strict X-AL-2 reading: production callsite is now driver-reachable by default (not only via workflow override) |
| H_T-CP-3 (per-layer time-budget + `retry.*` 6-attribute namespace + dual-emission) | RETIRED batch 3 (2026-05-20, retry_breaker_fallback.py:`_run_per_candidate_attempts`) | Same as CP-1 |
| H_T-CP-4 (fallback chain composition + cross-family fallback) | RETIRED batch 3 (2026-05-20, retry_breaker_fallback.py:`_advance_or_exhaust`) | Same as CP-1 |
| H_T-CP-5 (routing attribute namespaces inheritance + per-class sampling) | RETIRED batch 3 (2026-05-20, three-level OTel span hierarchy preservation) | Same as CP-1 |
| H_T-CP-10 (TopologyPattern dispatcher + admissibility predicate) | RETIRED batch 4 §1 (2026-05-20, sub_agent_dispatch.py composer steps 3-4 — advisory-gate narrowing per `[[class_1_tension_u_rt_59_topology_admissibility_predicate]]`) | Unchanged; CP-10 retirement criterion B was already narrowed at batch 4 to "dispatcher operational + predicate callable advisorially" without dependence on INFERENCE_STEP wiring |

Cumulative retirement count: **21 / 49 (42.9%)** — unchanged from batch 4 cumulative.

---

## §1 H_T-CP-1 / CP-3 / CP-4 / CP-5 — LLM-dispatch end-to-end execution path completion

| Field | Content |
|---|---|
| Substitution IDs (re-affirmed) | H_T-CP-1 + H_T-CP-3 + H_T-CP-4 + H_T-CP-5 |
| Primitive | Multi-LLM routing core + per-layer time-budget retry namespace + fallback chain composition + routing attribute namespaces (per C-CP-01 / C-CP-03 / C-CP-04 / C-CP-05) |
| Spec contract | C-RT-15 + C-RT-16 + C-RT-17 §14.7.7 (registry binding) |
| Re-affirmation event timestamp | Phase 7 sub-phase 7d U-RT-59 async/sync fork Path B wiring arc, 2026-05-20 |
| Wiring landing commit | `d64d8cf` (follows `84edc30` discovery) |
| Pre-wiring posture (v1.6 MVP) | Production composer present at `lifecycle/llm_dispatch.py:RuntimeLLMDispatcher.dispatch` + `lifecycle/retry_breaker_fallback.py:RetryBreakerFallbackDispatcher.dispatch` (both async). Bootstrap stage 5 bound `ctx.llm_dispatcher = retry_breaker_fallback_wrapper`. Driver registry binding for INFERENCE_STEP STRUCK per Class 1 fork. Driver-reachable only via `workflow.step_dispatchers` workflow-override path at api.py:390 |
| Post-wiring posture (v1.7) | Bootstrap stage 5 wraps `ctx.llm_dispatcher` through `SyncDispatcherFacade` (via `materialize_sync_dispatcher_facade(result_timeout_seconds=config.drain_timeout_seconds)`) and binds `INFERENCE_STEP → facade(llm_dispatcher)` in `StepKindDispatcherRegistry` alongside `SUB_AGENT_DISPATCH`. Any workflow with INFERENCE_STEP steps that does NOT supply a `workflow.step_dispatchers` override now flows through the production dispatcher chain by default. The facade captures the api.py outer event loop at stage 5 construction (running loop = `await run_bootstrap(...)` loop = loop hosting eventual `asyncio.to_thread(execute_workflow, ...)` per api.py:399); from the worker thread, `dispatch(...)` schedules coroutines back via `asyncio.run_coroutine_threadsafe(...).result(timeout=...)` |
| Condition B (strict X-AL-2 re-reading) | The "H_E surface no longer invoked at substitution site" condition was met at batches 2-3 against composer presence. At this batch, strict X-AL-2 reading is further satisfied: the production composer is now invoked **by default** at execution time (no workflow-override required). The H_E `--model single-LLM` substitution surface (CP-AL-4) is no longer reachable from any non-override-supplying workflow path |
| Cross-axis cascade | None — wiring completion does not gate any unretired substitution. CP-axis 9/22 (40.9%) retired count unchanged |
| Evidence anchor | `harness-runtime/src/harness_runtime/bootstrap/stage_5_loop_init.py:148-167` (facade construction + registry binding); `harness-runtime/tests/test_bootstrap.py::test_bootstrap_stage_5_binds_inference_and_sub_agent_dispatchers` (full-bootstrap AC #11 verification); `harness-runtime/tests/test_lifecycle_sync_dispatcher_facade.py` D1-D8 (8 facade discovery + integration tests) |

---

## §2 H_T-CP-10 advisory-gate-narrowing carry-forward (NO change)

| Field | Content |
|---|---|
| Substitution ID | H_T-CP-10 |
| Prior retirement | RETIRED batch 4 §1 (advisory-gate narrowing per `[[class_1_tension_u_rt_59_topology_admissibility_predicate]]`) |
| Batch 5 effect | NO change. CP-10 retirement criterion B was narrowed at batch 4 to "dispatcher operational + predicate callable advisorially". The narrowing was independent of INFERENCE_STEP wiring (the sub-agent dispatch composer at `sub_agent_dispatch.py` is the substitution-site carrier, NOT the INFERENCE_STEP path). The strict-gate retirement criterion remains owed per `[[class_1_tension_u_rt_59_topology_admissibility_predicate]]` Path A (compose `is_primary_or_cross_pattern(topology, workload)` helper using C-CP-11 §11.1 primary-topology lookup) |
| Re-evaluation trigger | When `[[class_1_tension_u_rt_59_topology_admissibility_predicate]]` is resolved at the topology-admissibility fork follow-on arc |
| **2026-05-20 closure pointer** | The advisory-gate carry-forward from batch 4 §1 / this §2 fully closes at the U-RT-59 topology-admissibility fork Path A resolution, commit `e52c2da`. CP-10 retirement remains in place at the same status (still RETIRED); the strict gate strengthens condition B evidence from "predicate callable advisorially" to "primary-OR-cross-pattern strict gate at production callsite". No new retirement event opened (batch 6 not warranted); this pointer-close suffices per advisor cross-check |

---

## §3 Cumulative retirement ledger (post batch 5)

Per `.harness/phase-7d-retirement-ledger-v2.md` §5 (workspace progress ledger):

| Status | Count | Substitutions |
|---|---|---|
| RETIRED (post batch 5) | 21 / 49 (unchanged) | (15 from batches 1-2) + CP-3 / CP-4 / CP-5 / CXA-5 (batch 3) + CP-10 / CP-13 (batch 4) |
| PARTIAL (post batch 5) | 2 / 49 (unchanged) | AS-8 (batch 2) + CP-14 single-sub-agent slice (batch 4; gates on fan-out arc) |
| STILL-BOUNDED (post batch 5) | 10 / 49 (unchanged) | Per `harness-cp/CLAUDE.md` §4.1 + per-axis CLAUDE.md inventories |

CP-axis post-batch-5: **9 / 22 retired (40.9%, unchanged)**. Cumulative 21/49 (42.9%, unchanged).

---

## §4 Cross-axis cascade impact

§6.3.2 F-CP-01 Stage 3b inversion cascade: **FULLY DISCHARGED at batch 3** (preserved at this batch). No new inversion-seam activations.

§14.7.7 INFERENCE_STEP routing-registry binding Class 1 fork (`[[class_1_tension_u_rt_59_async_sync_step_dispatcher]]`): **RESOLVED** at this arc — wiring landing commit `d64d8cf`. Fork status flips OPEN → RESOLVED at the fork file's filing-footer update (companion commit, this arc).

Two other U-RT-59 sibling forks remain OPEN at this batch (not addressed here):

- `[[class_1_tension_u_rt_59_cp_to_od_audit_write_gap]]` — AC #9 write half STRUCK at v1.6 MVP; CPAuditLedgerEntry → AuditLedgerEntry converter owed at follow-on arc. Joins `[[fork-cp-is-wiring-gaps]]` family.
- `[[class_1_tension_u_rt_59_topology_admissibility_predicate]]` — strict admissibility gate dropped per predicate-semantic-mismatch; primary-or-cross-pattern helper owed at follow-on arc.

---

## §5 Filing footer

| Field | Value |
|---|---|
| Filed by | U-RT-59 async/sync StepDispatcher Class 1 fork wiring arc |
| Operator ratification | Operator-ratified discovery-first → wiring posture 2026-05-20 (this session) |
| Predecessor batch | `.harness/phase-7d-retirement-events-batch-4.md` (closed) |
| Successor batch | TBD (HITL / validator / tool-invocation / memory / files / mcp composer arcs) |
| Test posture at filing | 715 harness-runtime tests green (was 712 at facade discovery; +2 D7/D8 + 1 stage 5 AC #11 test); ruff clean; pyright pre-existing errors on stage_5_loop_init.py:113-114 (U-RT-58 wrapper section) unchanged |
| Class 3 drift items added | Items 6 (facade adapter documentation at spec §14.7.7) + 7 (step_dispatch_timeout_seconds config split) appended to `class_3_tension_u_rt_59_spec_prose_drift.md` (companion commit, this arc) |

---

*Batch 5 retirement re-affirmation events filed per X-AL-2 strict-reading clarification post Path B wiring landing. NO new RETIRED transitions; cumulative 21/49 (42.9%) unchanged. Re-affirms CP-1/CP-3/CP-4/CP-5 criterion B end-to-end execution path completion. CP-10 advisory-gate carry-forward preserved.*
