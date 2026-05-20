# Class 1 Tension: async/sync StepDispatcher Protocol mismatch (U-RT-59 surfaced)

**Class:** 1 — halt-route-split (partial-landing per `[[halt-route-split-AC-pattern]]`).
**Filed:** 2026-05-20, Phase 7 sub-phase 7b, U-RT-59 landing arc.
**Status:** OPEN — partial-landing absorbed at U-RT-59 (INFERENCE_STEP binding STRUCK from plan AC #11); root-cause resolution owed.

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
