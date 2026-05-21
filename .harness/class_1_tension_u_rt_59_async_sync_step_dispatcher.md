# Class 1 Tension: async/sync StepDispatcher Protocol mismatch (U-RT-59 surfaced)

**Class:** 1 — halt-route-split (partial-landing per `[[halt-route-split-AC-pattern]]`).
**Filed:** 2026-05-20, Phase 7 sub-phase 7b, U-RT-59 landing arc.
**Status:** **RESOLVED 2026-05-20** at Path B wiring landing `d64d8cf` (follows discovery landing `84edc30`). INFERENCE_STEP routing-registry binding restored at bootstrap stage 5 via `SyncDispatcherFacade(ctx.llm_dispatcher)` — plan v2.5 L9-ter AC #11 fully met. **Spec text unchanged — already correct at v1.6 §14.7.7;** the facade is a transport-adapter detail invisible at the contract level. Facade adapter documentation owed to Class 3 drift batch item 6 (next runtime spec revision pass to v1.7+). Wiring-arc criterion B re-affirmation event filed at `.harness/phase-7d-retirement-events-batch-5.md` (NO new retirements; CP-1 / CP-3 / CP-4 / CP-5 strict-X-AL-2 re-affirmed for end-to-end execution path).

---

## Surfacing event

U-RT-59 plan AC #11 (Spec_Harness_Runtime_v1.md v1.6 §14.7.7 + Implementation_Plan_Harness_Runtime_v2.5 L9-ter) asks the bootstrap stage 5 wiring to construct `ctx.step_dispatchers: StepKindDispatcherRegistry` with 2 bindings:

- `INFERENCE_STEP → ctx.llm_dispatcher` (U-RT-58 `RetryBreakerFallbackDispatcher` wrapper)
- `SUB_AGENT_DISPATCH → ctx.sub_agent_dispatcher` (U-RT-59 new composer)

**Pre-existing structural defect surfaced at AC #11 implementation:**

- `harness-runtime/src/harness_runtime/lifecycle/retry_breaker_fallback.py:RetryBreakerFallbackDispatcher.dispatch` is declared `async def dispatch(...) -> Mapping[str, Any]` (U-RT-58 landing).
- `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py:RuntimeLLMDispatcher.dispatch` is declared `async def dispatch(...) -> Mapping[str, Any]` (U-RT-52 landing).
- `harness-cp/src/harness_cp/workflow_driver.py:175` declares `StepDispatcher` Protocol with **sync** `def dispatch(...) -> Mapping[str, Any]` (Stage 1 plumbing landing).
- `harness-cp/src/harness_cp/workflow_driver.py:execute_workflow` is **sync**; called via `asyncio.to_thread` from `harness-runtime/src/harness_runtime/api.py:run` (Lane 6 / U-RT-44 composition).

If the bootstrap stage 5 wiring binds `INFERENCE_STEP → ctx.llm_dispatcher` per AC #11 strict reading, the sync driver calls `step_dispatchers.lookup(INFERENCE_STEP).dispatch(binding, step, step_context=step_context)` and receives a **coroutine** rather than a `Mapping[str, Any]` — the next line (`accumulated[step.step_id] = dict(step_output)`) would fail with `TypeError: 'coroutine' object is not iterable` (or, before reaching that line, the dispatcher receives no `await` and the coroutine is silently dropped without execution).

**Sleeping defect.** U-RT-58 wired `ctx.llm_dispatcher` at bootstrap stage 5 but no integration test drives the wrapper through the sync driver — the async/sync mismatch was undetected at U-RT-58 landing (2231 tests green). The `@runtime_checkable` Protocol satisfaction check uses attribute-presence only, not signature shape: `isinstance(wrapper, StepDispatcher)` returns True because `wrapper.dispatch` is callable, regardless of its async-ness. The integration smoke tests at `harness-runtime/tests/integration/test_run_smoke.py` use workflow-supplied sync test dispatchers (`_NoopDispatcher`, `_CostFiringDispatcher`, `_SlowDispatcher`) at the `workflow.step_dispatcher` indirection, not `ctx.llm_dispatcher`.

---

## Routing per `Project_Workflow_v1_8.md` §2.7.6

**Class 1.** Architectural defect at the cross-axis composition seam between:
- CP-side `StepDispatcher` Protocol declaration (sync).
- Runtime-side concrete dispatcher implementations (`RuntimeLLMDispatcher`, `RetryBreakerFallbackDispatcher` — async).

**Halt-route-split absorbed at landing.** Per `[[halt-route-split-AC-pattern]]` discipline: AC #11's INFERENCE_STEP binding clause STRUCK at v1.6 MVP. U-RT-59 partial-lands the registry with 1 entry (SUB_AGENT_DISPATCH only). The async/sync resolution arc is owed.

**Resolution surface (operator decision required at follow-on arc):**

| Path | Description | Cost surface |
|---|---|---|
| **A — async driver** | Refactor `execute_workflow` to async; remove `asyncio.to_thread` indirection from api.py; the driver becomes an async loop with `await step_dispatcher.dispatch(...)`. Breaks: sync test fixtures need rewrite; CP-axis driver becomes async-tainted. | Large surface (refactors api.py + driver + all test fixtures) |
| **B — sync facade adapter** | Add `SyncDispatcherFacade` wrapping the async wrapper; facade's `dispatch` calls `asyncio.run(self._async.dispatch(...))` from within sync (which runs inside `asyncio.to_thread` worker thread per Lane 6 — no live event loop). Risk: provider clients constructed in api.py's outer event loop may error on cross-loop use ("Future attached to different loop"); needs verification. | Medium (one new module + integration test) |
| **C — Protocol revision** | Revise `StepDispatcher` Protocol at CP spec v1.7 to be async; rebuild Stage 1 plumbing; all dispatcher impls become async; driver becomes async. Combines A + spec amendment. | Large (spec revision + plumbing + driver) |
| **D — split Protocol** | Two Protocols: `SyncStepDispatcher` + `AsyncStepDispatcher`; registry holds tagged union; driver branches on tag. Adds Protocol multiplexing complexity to the driver. | Medium-large |

Recommended discovery: validate **Path B** experimentally at the follow-on arc (test that async provider clients survive cross-loop invocation via `asyncio.run` inside `to_thread`). If B works empirically, it's the lowest-cost resolution. If not, Path A or C.

---

## Workspace progress impact

**U-RT-59 lands** (partial — AC #11 INFERENCE_STEP clause STRUCK):
- `StepKindDispatcherRegistry` constructed at stage 5 with **1 entry** (`SUB_AGENT_DISPATCH → sub_agent_dispatcher`).
- INFERENCE_STEP routes to "not bound" → driver maps to `RT-FAIL-STEP-KIND-DISPATCHER-NOT-BOUND` per spec §14.7.
- Workflow-supplied `step_dispatchers` override (via `WorkflowObject.step_dispatchers` optional attribute at `api.py:run`) preserves the lane-6 workflow-supplied dispatch path; tests and specialized workflows can still drive INFERENCE_STEP steps by supplying their own sync registry.

**Retirement events at AC #12** (filed in `phase-7d-retirement-events-batch-4.md`):
- H_T-CP-10 RETIRED (topology dispatcher + admissibility predicate; SUB_AGENT_DISPATCH-path bound at production).
- H_T-CP-13 RETIRED (typed sub-agent dispatch schemas at production composer).
- H_T-CP-14 PARTIAL (single-sub-agent slice; fan-out arc deferred).
- INFERENCE_STEP-path retirement criteria for any LLM-dispatch-related substitutions remain GATED on this fork's resolution.

---

## Related forks

- `[[fork-c-rt-17-step-dispatcher-parent-context-gap]]` — RESOLVED-STAGE-1 at U-RT-59 same arc; this fork was discovered DURING that resolution arc.
- `[[fork-cp-3-retry-breaker-composer-underspec]]` — RESOLVED at U-RT-58; the async wrapper landed there without integration-driving through the sync driver, which is the root sleeping-defect source.

---

## Filing footer

| Field | Value |
|---|---|
| Filed by | sub-agent dispatch composer landing arc (U-RT-59 implementation session) |
| Operator ratification | 2026-05-20 (partial-land selection per AskUserQuestion: "Partial-land: bind SUB_AGENT_DISPATCH only; file Class 1 for INFERENCE_STEP wiring") |
| Resolution target | Follow-on arc; recommended discovery via Path B experimental validation |
| Re-evaluation trigger | When the next LLM-dispatch-path retirement event is filed OR when an INFERENCE_STEP-path integration test is owed |

---

## Discovery landing (2026-05-20, commit `84edc30`)

Path B variant — sync facade scheduling coroutines back to the captured outer loop via `asyncio.run_coroutine_threadsafe(...).result(timeout=...)` — **validated** for loop-bound asyncio primitives at `harness-runtime/src/harness_runtime/lifecycle/sync_dispatcher_facade.py` + `harness-runtime/tests/test_lifecycle_sync_dispatcher_facade.py` (6 D1–D6 tests green).

The literal fork-text Path B reading (`asyncio.run(...)` inside `to_thread`) is **non-viable**: D1 demonstrates `RuntimeError: ... attached to a different loop` against a pending future created on the outer loop (the same pathology production httpx `ConnectionPool` exhibits via its anyio-backed `Semaphore`).

**Two constraints absorbed into the implementation:**

1. **Loop-capture timing.** `materialize_sync_dispatcher_facade(...)` calls `asyncio.get_running_loop()`; must be invoked from an async context on the loop that hosts the eventual `to_thread`. Stage 5 bootstrap satisfies this (`async def execute(...)` awaited from `await run_bootstrap(...)` at `harness_runtime/api.py:349`).
2. **Cancellation interaction.** `future.result(timeout=result_timeout_seconds)` prevents worker-thread leak when drain timeout fires before inner coroutine completes. Caller chooses the bound; drain-timeout alignment is the natural choice.

**Owed at wiring arc (NOT this discovery landing):**

1. Real-SDK integration test driving an `anthropic.AsyncAnthropic` (or `AsyncOpenAI`) constructed + ping-opened on the outer loop through the facade from a `to_thread` worker via `respx` or a local httpx route handler. Catches SDK-specific loop-bound primitives layered above httpx + interaction with `RetryBreakerFallbackDispatcher` tracer + `sleep_fn` defaults.
2. `CancelledError` propagation test (outer loop cancels future during drain shutdown → worker `future.result()` raises CancelledError).
3. Stage 5 bootstrap wiring: wrap `ctx.llm_dispatcher` in `SyncDispatcherFacade` via `materialize_sync_dispatcher_facade(...)`; bind `INFERENCE_STEP → facade(llm_dispatcher)` in `StepKindDispatcherRegistry`.
4. Spec amendment: un-strike `Spec_Harness_Runtime_v1.md` v1.6 §14.7.7 AC #11 INFERENCE_STEP clause + plan v2.5 L9-ter; bump to v1.7.
5. Retirement event for H_T-CP-10 INFERENCE_STEP-path gate + any LLM-dispatch-path substitutions that were gated on this fork.
6. Status flip OPEN → RESOLVED at the wiring arc's commit landing.

**D2 framing caveat (advisor cross-check):** D2 uses `httpx.MockTransport` which is loop-agnostic — it does NOT empirically prove `AsyncHTTPTransport.ConnectionPool` survives the facade's pattern, only that `run_coroutine_threadsafe` works through *some* httpx surface. The production pathology proof is D1's pending-future test (proxy for httpx's loop-bound anyio.Semaphore). Real-SDK integration test (above) is the wiring-arc empirical proof.

---

## Resolution landing (2026-05-20, commit `d64d8cf`)

**Path B wiring** landed on top of discovery commit `84edc30`. Operator ratified discovery-first → wiring posture at this session; six-item wiring arc collapsed into a single landing (integration tests + cancellation test + stage 5 wiring + retirement event + Class 3 drift items + fork flip + memory updates).

### Stage 5 wiring (production change)

`harness-runtime/src/harness_runtime/bootstrap/stage_5_loop_init.py:148-167` now:

```python
inference_step_dispatcher = materialize_sync_dispatcher_facade(
    cast(Any, ctx.llm_dispatcher),
    result_timeout_seconds=config.drain_timeout_seconds,
)

ctx.step_dispatchers = StepKindDispatcherRegistry(
    dispatchers={
        StepKind.INFERENCE_STEP: inference_step_dispatcher,
        StepKind.SUB_AGENT_DISPATCH: sub_agent_dispatcher,
    },
)
```

Loop-capture timing satisfied: stage 5 is `async def execute(...)` awaited from `await run_bootstrap(...)` at api.py:349 — the running loop here IS the loop that subsequently hosts `asyncio.to_thread(execute_workflow, ...)` per api.py:399. `materialize_sync_dispatcher_facade` calls `asyncio.get_running_loop()` at construction.

### Wiring-arc tests (2 added at this commit, on top of D1-D6 discovery)

- **D7** — full dispatcher chain through facade preserves loop affinity (`_LoopAffinityCapturingDispatcher` asserts `asyncio.get_running_loop() is construction_loop` at every `dispatch` call; also exercises real `asyncio.sleep(0)` driven by outer loop via `run_coroutine_threadsafe`). Proxy for httpx anyio.Semaphore pathology that we don't exercise directly.
- **D8** — `asyncio.CancelledError` raised on outer loop surfaces verbatim at worker thread's `facade.dispatch` (drain-shutdown propagation contract). Documented limit: cancellation of the `to_thread` future does NOT propagate through the facade to the inner coroutine; `result_timeout_seconds` (covered by D4) is the upper bound on the leak window.

### Bootstrap end-to-end AC #11 verification

`harness-runtime/tests/test_bootstrap.py::test_bootstrap_stage_5_binds_inference_and_sub_agent_dispatchers` runs full `run_bootstrap(...)` and asserts:
- `ctx.step_dispatchers.lookup(StepKind.INFERENCE_STEP)` is a `SyncDispatcherFacade` wrapping `ctx.llm_dispatcher` with `result_timeout_seconds == config.drain_timeout_seconds`.
- `ctx.step_dispatchers.lookup(StepKind.SUB_AGENT_DISPATCH)` is a `RuntimeSubAgentDispatcher`.
- TOOL / HITL / DECLARATIVE step kinds raise `StepKindDispatcherNotBoundError` on lookup.

### Class 3 drift items added at this arc

- **Item 6** — `SyncDispatcherFacade` adapter at INFERENCE_STEP binding site. Documents the transport-adapter at a new §14.7.8 subsection (transport-adapter detail, invisible at §14.7.7 contract level).
- **Item 7** — per-step-vs-whole-workflow timeout-budget conflation at v1.7 wiring. Documents the `config.drain_timeout_seconds` reuse + future `step_dispatch_timeout_seconds` RuntimeConfig split.

### Spec text status

§14.7.7 (binding declaration) is **unchanged at v1.6** — already correct (`step_dispatchers = StepKindDispatcherRegistry(dispatchers={StepKind.INFERENCE_STEP: ctx.llm_dispatcher, ...})`). The "AC #11 strike" was an implementation deviation captured at this fork file, not a spec edit. No spec bump at this arc; facade documentation absorbed at next runtime spec revision pass per Class 3 drift items 6+7.

### Retirement-event filing

`.harness/phase-7d-retirement-events-batch-5.md` (criterion-B re-affirmation event; NO new RETIRED transitions; cumulative 21/49 (42.9%) unchanged). Documents end-to-end LLM-dispatch execution path completion for CP-1 / CP-3 / CP-4 / CP-5 at strict X-AL-2 reading. CP-10 advisory-gate narrowing from batch 4 §1 preserved unchanged.

### Sibling forks remaining OPEN

- `[[class_1_tension_u_rt_59_cp_to_od_audit_write_gap]]` — AC #9 write half STRUCK; CPAuditLedgerEntry → AuditLedgerEntry converter owed.
- `[[class_1_tension_u_rt_59_topology_admissibility_predicate]]` — strict admissibility gate dropped; primary-or-cross-pattern helper owed.

### Test posture at resolution

715 harness-runtime tests green (was 712 at facade discovery; +2 D7/D8 + 1 stage 5 AC #11 test). Ruff clean. Pre-existing pyright errors on stage_5_loop_init.py:113-114 (U-RT-58 wrapper section, predates this arc) unchanged.
