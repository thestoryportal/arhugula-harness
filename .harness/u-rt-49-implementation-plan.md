# U-RT-49 — E2E bootstrap → shutdown smoke (PARTIAL-LAND)

**Status:** in-progress
**Spec source:** session-3 atomic decomposition L11 + spec §10 / §11
**Decomposition:** `.harness/phase-2-session-3-track-a-atomic-decomposition.md` L11 U-RT-49
**Predecessors:** U-RT-43 (bootstrap), U-RT-46 (shutdown) at commits `bf8d838` / `10a6bca`

---

## Halt-route-split-AC applied

Session-3 U-RT-49 scope ("minimal no-op workflow exercising all 9 bootstrap
stages") presupposes a workflow execution loop that doesn't exist at HEAD.
`api.run()` raises `WorkflowExecutionNotYetLandedError` post-bootstrap;
`TopologyDispatcher.dispatch()` returns the `TopologyPattern` enum value
but does not invoke anything. No CP-axis primitive lands a workflow loop;
no runtime-axis unit either.

Operator decision (2026-05-20): Path A — partial-land bootstrap+shutdown
round-trip smoke; strike workflow-execution ACs; extend
`[[fork-u-rt-44-workflow-loop-drain]]` to cover U-RT-49 too. Re-land target:
the future-phase unit (Track B or a follow-up) that introduces a CP
workflow loop primitive.

## ACs

| AC | Status | Materialization |
|---|---|---|
| Green run touches each of the 9 `BootstrapStage` enum members | LAND | assert via `BootstrapStageCompleteEvent` capture across all 9 stages |
| Clean shutdown leaves no resources open | LAND | `shutdown(ctx)` returns clean `ShutdownReport` (no failures, pidfile removed, tracer + collector + providers closed) |
| State ledger has workflow entries | STRIKE | no execution loop |
| Collector sqlite has spans per stage + workflow step | STRIKE | no execution loop; OTel stage-level instrumentation also a future surface |
| Cost attribution chain produced an entry | STRIKE | no execution loop |

## What lands

E2E integration test `tests/integration/test_run_smoke.py`:

1. Build a minimal `RuntimeConfig` against a tmp_path repository_root.
2. Real `materialize_runtime_config()` path through stage 0..7. Fake the
   provider clients + collector daemon + tracer at the fixture layer (same
   pattern as U-RT-43 + U-RT-46 tests) so the test doesn't hit network.
3. Call `harness_runtime.run(workflow)` with a minimal `WorkflowObject`.
4. Expect the call to raise `WorkflowExecutionNotYetLandedError` post-bootstrap.
5. Independently assert:
   - All 9 `BootstrapStage` members appear in
     `ctx.emitted_bootstrap_events` (capture via mocked emitter).
   - Pidfile exists at `tmp_path/.harness/runtime.pid`.
6. Then `await shutdown(ctx, timeout=5.0)` → assert `ShutdownReport`:
   - `failures == ()`.
   - `flush.tracer_flushed is True`.
   - `flush.ledger_fsynced is True`.
   - `audit_ledger_head_hash is None` (no workflow entries — genesis).
   - Pidfile removed.

Because `api.run()` raises NotYetLanded mid-call, we can't easily capture
the post-bootstrap `HarnessContext` via that surface. Test invokes
`run_bootstrap(config, workload_class=...)` directly to get the ctx, then
exercises `shutdown(ctx)` on the result. The `api.run()` execution stub is
exercised separately via existing `test_api.py` tests.

## Files

- `.harness/fork_u_rt_49_workflow_execution_extends_u_rt_44.md` — extension
  record (NEW; cross-references the carrier).
- `.harness/u-rt-49-implementation-plan.md` (this file).
- `harness-runtime/tests/integration/__init__.py` (NEW marker).
- `harness-runtime/tests/integration/test_run_smoke.py` (NEW, ~150 LOC).

## Test discipline

- Reuses provider-fake + collector-fake fixtures from `test_bootstrap.py`
  (factor out shared helpers into a new `tests/integration/conftest.py` if
  they multiply).
- Marker `@pytest.mark.integration` (not gated yet; tier-2 separation
  per session-3 §7 is a future-phase concern).
- The test asserts all 9 stages emit. Bootstrap stages 0–4 emit through
  the in-memory buffer; stages 5–7 emit through the live emitter (per
  U-RT-43 design). Both surfaces feed `ctx.emitted_bootstrap_events`.

## Out-of-scope (deferred to fork resolution)

- Workflow-step execution (no CP loop).
- Per-stage OTel span emission (bootstrap stages don't emit OTel spans
  at HEAD; only the in-memory BootstrapStageCompleteEvent capture).
- Cost-attribution entry from a workflow step (stateless chain; no entries
  produced unless workflow executes).
- Real provider call (deferred until execution loop lands).
