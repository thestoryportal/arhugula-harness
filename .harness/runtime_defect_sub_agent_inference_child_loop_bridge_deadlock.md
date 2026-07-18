# Runtime defect — `SUB_AGENT_DISPATCH` of an INFERENCE child deadlocks the sync/async bridge

| Field | Value |
|---|---|
| Class | HISTORICAL (2026-06-14 classification): Runtime implementation defect, no spec/plan revision. **Superseded 2026-07-18 — the B-48 filing routes the fix and carries Class 1 back-flow riders** (C-RT-03 cap field; C-IS-07 drain-timestamp) — see the Status row. The original contract-soundness claim (C-CP-25 §25.11 + C-RT-59 + C-RT-15) stands for the DEADLOCK face; the executor-capacity and timestamp-authority surfaces the resolution touches were not in its scope. |
| Locus | `harness-runtime` sync/async bridge: `lifecycle/sync_dispatcher_facade.py` (`SyncDispatcherFacade.dispatch`) ⨯ `lifecycle/hitl_gate_composer.py` (async `dispatch`) ⨯ `lifecycle/sub_agent_dispatch.py` + `lifecycle/child_workflow_runner.py` (sync child re-entry). |
| Status | OPEN — **routing superseded 2026-07-18 by the B-48 Class 2 filing** (`.harness/class_2_fork_b48_sync_subagent_dispatch_offload.md`): the executor-offload revision is the resolution path for BOTH the loop-blocking and this deadlock face; this record's fix directions are historical, its xfail anchor is carried into the filing's §4 as an acceptance signal. Blocks a genuine real-provider sub-agent recursion e2e. xfail-anchored (NOT silently skipped). |
| Discovered | 2026-06-14, during R-FS-1 arc #15 (U-CP-89 `HIERARCHICAL_DELEGATION`), by the first live depth-2 sub-agent e2e against a real provider (Ollama). |
| Caused by | **Pre-existing.** Exposed — NOT caused — by U-CP-89. U-CP-89 is a thin wrapper over `_execute_orchestrator_workers` (U-CP-88); the facade, HITL-gate bridge, and sub-agent recursion are all U-RT-59 / U-RT HITL-composer surface that predate it. A `SUB_AGENT_DISPATCH` worker dispatching an INFERENCE child was reachable before U-CP-89 (U-CP-88 + any such manifest hits it). It was latent because **no test ever exercised a sub-agent INFERENCE child against a real provider** — `test_topology_fixture_suite.py` uses faked providers + deterministic dispatch (it never drives the facade's real `run_coroutine_threadsafe` bridge). |
| Anchored test | `harness-runtime/tests/integration/test_u_cp_89_hierarchical_delegation_live_e2e.py::test_u_cp_89_hierarchical_delegation_depth2_live_ollama` — `@pytest.mark.xfail(strict=False)`. Flips to **XPASS** when this defect is fixed (the signal the fix landed). |

---

## 1. Symptom

A depth-2 run — root `HIERARCHICAL_DELEGATION` `[INFERENCE root-orch, SUB_AGENT_DISPATCH sub]` whose child runs an INFERENCE step against real Ollama — returns `RunStatus.PARTIAL` (not `completed`). The root orchestrator INFERENCE step succeeds (one `chat` span, ~327 ms). The child's first INFERENCE step **hangs for 30 s** and fails with:

```
child workflow … terminated with RunStatus.FAILED;
fail_class='step-failure: RT-FAIL-STEP-DISPATCH-TIMEOUT: step dispatch exceeded 30.0s bound'
```

The 30 s bound is `SyncDispatcherFacade.result_timeout_seconds`'s `future.result(timeout=…)`. It is a **hard deadlock**, not slowness — a `num_predict=4` Ollama call returns in <1 s when the loop is free (proven by the succeeding root-orch).

## 2. Topology-independence (isolation experiment)

The deadlock is **not** specific to a nested-fan-out (HIERARCHICAL) child. An isolation experiment with the child set to `SINGLE_THREADED_LINEAR` (admissible pairing `single-threaded-linear × pipeline-automation`) — i.e. **no** nested `_run_fanout_to_completion`/`loop_R` — deadlocks **identically** (`RT-FAIL-STEP-DISPATCH-TIMEOUT` at the child's first INFERENCE step). The defect is therefore **`SUB_AGENT_DISPATCH`-of-an-INFERENCE-child in general**, independent of the child's topology pattern.

(First isolation attempt used `single-threaded-linear × software-engineering`, which is **inadmissible** per `per_workload_class_topology` — it failed fast at the step-4 admissibility gate, a confound; the corrected `pipeline-automation` pairing is the valid experiment.)

## 3. Mechanism (root cause)

Captured from an unfiltered MainThread stack at the wedged `SyncDispatcherFacade.dispatch`:

```
asyncio/base_events.py _run_once
  → hitl_gate_composer.py:860 dispatch          (ASYNC — `return await self._dispatch_inner(...)`)
    → sub_agent_dispatch.py:623 dispatch         (SYNC)
      → child_workflow_runner.py:129 _runner     (SYNC — re-enters the driver)
        → workflow_driver.py execute_workflow     (CHILD; SYNC)
          → … → sync_dispatcher_facade.py:~205 dispatch   (child INFERENCE step)
                  → asyncio.run_coroutine_threadsafe(coro, self.loop)   ← WEDGES
```

Step by step:

1. Provider httpx clients are bound to the **outer event loop** (`self.loop`, captured at bootstrap stage 5). Per the facade's own design (`sync_dispatcher_facade.py` docstring D1), every INFERENCE coroutine **must** run on that loop — `asyncio.run` on a fresh loop is "dead on arrival" because the loop-bound httpx client fails.
2. The `SUB_AGENT_DISPATCH` worker's dispatcher is the **async** `hitl_gate_composer.dispatch`. A sync→async bridge schedules it onto the outer loop via `run_coroutine_threadsafe(...)` + `future.result()`. The outer loop begins executing that coroutine **on its own thread** (`_run_once`).
3. Inside that coroutine step, `hitl_gate_composer` calls (synchronously, blocking the loop thread) the sync `sub_agent_dispatch` → `child_workflow_runner` → `execute_workflow(child)`.
4. The child's INFERENCE step reaches `SyncDispatcherFacade.dispatch`, which does **`run_coroutine_threadsafe(child_coro, self.loop)` to the SAME outer loop** and blocks on `future.result(30)`.
5. **Deadlock:** the outer loop is mid-step executing the step-2 coroutine (blocked synchronously down the stack at step 4's `future.result`). It cannot advance to run `child_coro`. `future.result` never resolves → 30 s timeout.

The essential knot: **nested `run_coroutine_threadsafe` to a single loop, where the outer bridge is mid-execution on that loop's thread when the inner bridge tries to schedule.** The single-loop constraint is forced by httpx-clients-bound-to-one-loop.

## 4. Why the top level works but recursion does not

The top-level run drives `execute_workflow` via `asyncio.to_thread` (an off-loop worker thread, `asyncio_0`), so its facade bridge runs from a **non-loop** thread → the loop is free → `run_coroutine_threadsafe` advances. The sub-agent recursion re-enters the driver **inside a coroutine already executing on the loop thread**, collapsing the off-loop guarantee.

## 5. Affected scope

Any workflow whose realized dispatch path is `SUB_AGENT_DISPATCH worker → child with an INFERENCE (or any facade-bridged) step → real provider`, regardless of child topology. This includes:
- `HIERARCHICAL_DELEGATION` (U-CP-89) with a real provider at depth (the genuine motivating case).
- `ORCHESTRATOR_WORKERS` (U-CP-88) with a `SUB_AGENT_DISPATCH` worker whose child does INFERENCE against a real provider.
- Any hand-authored manifest with the same shape.

Pure-CP unit coverage is unaffected (the CP unit suite proves the strategy logic with a faithful in-process dispatcher double; it was never meant to exercise the real runtime facade). Faked-provider integration coverage (`test_topology_fixture_suite.py`) is unaffected (no real bridge).

## 6. Fix direction (a runtime build arc — deep, NOT bounded)

This is **not** a bounded patch and must **not** be bundled into the U-CP-89 CP-strategy PR (scope-creep; surgical-changes discipline). Offloading only `child_workflow_runner`'s `execute_workflow(child)` to a fresh thread does **not** suffice — the sync `sub_agent_dispatch` still runs on the loop thread (step 3) and still blocks the loop while awaiting the child. The fix must break the single-loop nesting. Candidate directions (to be designed in the follow-on arc):

- **Dedicated provider loop per recursion depth / off-loop provider loop:** run provider coroutines on a loop that is never the one a sync bridge is blocking — decouples httpx binding from the workflow-driving loop.
- **Async-native sub-agent recursion:** make the sub-agent dispatch + child execution `async` end-to-end so the child INFERENCE awaits on the loop cooperatively instead of bridging back to it synchronously (removes the nested `run_coroutine_threadsafe`).
- **Consistent off-loop driver re-entry:** ensure the child driver always runs on a non-loop worker thread *and* the sub-agent dispatch does not block the loop while awaiting it (requires the dispatch itself to be loop-cooperative).

Each touches the C-RT-59 / facade / HITL-bridge concurrency model and is a **meaningful runtime-architecture change** — surfaced to the operator for prioritization (it is the natural next R-FS-1 runtime arc). Per the FULL-SPEC standing directive it is a **build** arc, not a deferral; this doc + the xfail anchor are the tracking, not a silent skip.

## 7. Honest scope of the anchored e2e

The xfail marker states "integration NOT verified past the sub-agent INFERENCE seam." This is deliberate: the deadlock is the **first** blocker reached on this path, and the path's correctness beyond it (audit composition 8b/8c/8d, child result fold, bottom-up aggregation under a real provider) is **unverified** — there may be further defects behind the deadlock. The marker must not claim "passes once the deadlock is fixed." When the fix lands, re-run; if XPASS, the seam is genuinely clear; if it surfaces a new failure, that is the next layer (do not assume the deadlock was the last one — cf. the timestamp → tenant_id → deadlock chain that surfaced this defect).

## 8. Second facet behind the deadlock — concurrent-append timestamp authority (`drain_branch_buffers` captures `drain_timestamp` outside `_WRITE_LOCK`)

The deadlock (§3) is the **first** blocker on the concurrent sub-agent recursion path; this section names the **next layer** behind it, foreseeable now and pinned by a strict-xfail CP test so it is not lost. Both decorrelated reviewers of the U-CP-89 arc (codex out-of-family review = "P1"; the genuine `harness-adversarial-reviewer` agent = "F1-01") independently found it — the strongest signal it is real.

### 8.1 The gap

`harness_cp.workflow_driver.drain_branch_buffers` re-stamps every buffered entry to a single `drain_timestamp = datetime.now(UTC)` captured ONCE at drain entry — **outside** the IS writer's `_WRITE_LOCK` (`harness_is.state_ledger_write`, the module-level lock that serializes the read-prior-then-append critical section, `state_ledger_write.py:62` + `:216`). For a **single** drain (the only path reachable today) physical-append-order == timestamp-order, so the shared ZERO-tolerance ledger (`_CLOCK_SKEW_TOLERANCE = timedelta(0)`) stays non-decreasing. But under **concurrent** drains the capture-outside-the-lock breaks:

- **(a) Sibling-drain inversion.** Two `SUB_AGENT_DISPATCH` sibling children draining on separate fan-out threads each capture their OWN `drain_timestamp` outside `_WRITE_LOCK`. The lock then serializes their physical appends; it can do so in **capture-opposite order**, so a drain that captured the EARLIER timestamp physically appends AFTER one that captured a later timestamp → the writer's monotonic check (`state_ledger_write.py:221-226`) rejects it with `NonMonotonicTimestampError`.
- **(b) Audit/cost interleave.** A runtime audit / cost DIRECT write (its own `datetime.now(UTC)` at its call site, also outside the drain's capture window) interleaving the lock *between* a drain's capture and its physical appends produces the same inversion class.

### 8.2 Why it is not a U-CP-89 regression, and why it is unreachable today

`_WRITE_LOCK` is the ONLY shared serialization point; the timestamp authority sits *above* it (at each caller's `now()`), so any two writers that don't coordinate a shared clock can invert. This was **equally broken under the prior fan-out-start-timestamp policy** (that policy also captured timestamps outside the lock) — drain-time re-stamping did not introduce it; it only narrowed the window. It is **unreachable today** because the §3 deadlock blocks concurrent sub-agent recursion end-to-end (no two sibling sub-agent INFERENCE children can both reach their drains against a real provider while the bridge wedges). So facet (a) sits strictly **behind** the deadlock: fixing the deadlock is what first makes concurrent sibling drains reachable, at which point this facet becomes live.

### 8.3 Fix direction (IS write-path; contract-touching; same arc as the deadlock)

The clean fix is **timestamp-authority INSIDE `_WRITE_LOCK`**: the IS writer assigns the entry timestamp itself, inside the critical section, in physical-append order — so physical-append-order == timestamp-order *by construction* regardless of how many uncoordinated concurrent drains/direct-writers feed it. This **touches the C-IS-07 §7.1 write contract** (today the timestamp is caller-supplied and merely *validated* non-decreasing; the fix makes the writer the timestamp *authority*) → it is an **IS write-path build arc routed via IS back-flow** (Phase 5 spec → Phase 6 plan), NOT a bounded patch and NOT bundlable into a CP-strategy PR. It belongs to the **same runtime/IS concurrency arc as the §3 deadlock** (both are "make concurrent sub-agent recursion correct end-to-end"); sequencing the deadlock fix first is natural since it gates reachability.

### 8.4 Anchors

- **CP-level strict-xfail pin:** `harness-cp/tests/test_workflow_driver_buffered_append.py::test_concurrent_sibling_drains_invert_timestamp` — a deterministic two-thread reproduction (`_SequencedClock` orders the two captures; `_InterleavingRealWriter` wraps the REAL `append_ledger_entry` and forces the capture-opposite physical-append order). `@pytest.mark.xfail(strict=True)`: it asserts the CORRECT behavior (no `NonMonotonicTimestampError`, both entries persisted), currently fails on the genuine monotonic error, and **flips to XPASS when the §8.3 fix lands** — `strict=True` then fails the suite, forcing removal of the xfail.
- **Code-site doc:** `drain_branch_buffers` docstring + the module-level timestamp-discipline note in `workflow_driver.py` both scope their monotonicity guarantee to **causally-ordered** drains and point here for the concurrent gap (the "by construction" claim is true only for causally-ordered drains + the interleaved DIRECT linear-inline writer, NOT for concurrent uncoordinated appends).
