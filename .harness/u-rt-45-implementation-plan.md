# U-RT-45 — Flush observability (tracer BSP + ledger fsync)

**Status:** ✅ SUPERSEDED-BY-CANONICAL-PLAN (status-line refreshed 2026-05-28 Phase 1 status-cascade sweep per workflow v1.12 §7.4.7.3.B) — historical Phase 2 session-3 work-note pre-canonical-Phase-7-plan. Production flush/fsync at `harness-runtime/src/harness_runtime/shutdown.py`; canonical unit tracking at `design-substrate/Implementation_Plan_Harness_Runtime_v2_30.md`. Species 3 stale-carry per workflow v1.12 §7.4.7.2.

**Status:** in-progress *(historical; predates Phase 7 canonical plan)*
**Spec:** `design-substrate/Spec_Harness_Runtime_v1.md` §10 (C-RT-10) step 2
**Decomposition:** `.harness/phase-2-session-3-track-a-atomic-decomposition.md` L10 U-RT-45
**Predecessor:** U-RT-44 (drain) at commit `43acc9b`
**L-stage:** L10 — step 2 of C-RT-10 reverse-order shutdown sequence

---

## Scope

U-RT-45 lands the **flush primitive** (`harness_runtime.shutdown.flush_observability`).
NOT the full `shutdown()` orchestrator — that's U-RT-46. One-step-per-unit pattern
matches U-RT-43's 9 stage-module split.

C-RT-10 step 2 commits 4 flush surfaces:

| Surface | Landed | Materialization at U-RT-45 |
|---|---|---|
| `tracer_provider.force_flush(timeout_millis=N)` | ✅ OTel BSP via stage 4 | wrap sync `force_flush` in `asyncio.to_thread` |
| Ledger fsync (`.harness/state.jsonl`) | ✅ JsonlLedgerHandle.canonical_path | open path, `os.fsync(fd)`, close |
| Cost-attribution chain flush | ❌ **stateless by design** per U-RT-31 | NO-OP + Class 3 informational |
| Audit-writer flush | ❌ **immediate append-through** per U-RT-32 | implicit (writes go through ledger) |

## ACs

| AC | Status | Materialization |
|---|---|---|
| AC #1: all spans visible in collector sqlite post-flush | LAND | OTel BSP force_flush guarantees per OTel spec |
| AC #2: ledger chain head consistent post-flush | LAND | fsync forces OS-level durability of last-written entry |

## Class 3 informational (NEW)

`.harness/class_3_drift_u_rt_45_cost_chain_stateless.md` — spec §10 step 2
names "flush cost-attribution chain in-memory state to audit ledger" as a
shutdown action; U-RT-31 landed `RuntimeCostAttributionChain` as **stateless
by design** (every step is a pure OD function). The U-RT-45 cost flush is a
no-op against the landed shape. Non-blocking drift; spec revision pass owed
if a future cost-chain unit grows in-memory state (none planned).

## Implementation

### Files

- `harness_runtime/shutdown.py` (NEW, ~150 LOC) — `flush_observability(ctx, *,
  timeout_millis=30_000) -> FlushReport`, `FlushReport` frozen Pydantic,
  `FlushTimeoutError` typed.
- `harness-runtime/tests/test_shutdown.py` (NEW, ~10 tests).

### API surface

```python
class FlushReport(BaseModel):
    """Result of a flush_observability(ctx) call."""
    model_config = ConfigDict(frozen=True)
    tracer_flushed: bool                 # True iff force_flush returned True
    ledger_fsynced: bool                 # True iff fsync succeeded
    cost_chain_noop: bool                # always True at HEAD (stateless)
    timed_out: bool                      # True if any sub-flush exceeded timeout
    failures: tuple[str, ...]            # per-resource error tags

async def flush_observability(
    ctx: HarnessContext,
    *,
    timeout_millis: int = 30_000,
) -> FlushReport: ...
```

### Discipline

- **Wrap sync `force_flush` in `asyncio.to_thread`** — OTel SDK's
  `TracerProvider.force_flush(timeout_millis: int) -> bool` is synchronous;
  calling it directly on the event loop would block for up to N ms. `to_thread`
  preserves the bounded-wait discipline.
- **Per-resource exception isolation** — one failure doesn't abort the others;
  failed resources surface in `FlushReport.failures` (RT-FAIL-PARTIAL-SHUTDOWN
  per spec §10 fail-class).
- **fsync the file, not the dir** — Track A simplification. Note as deferred
  to implementation discretion; production-grade durability (dir fsync +
  F_FULLFSYNC on macOS) deferred until a real durability requirement surfaces.
- **No `shutdown()` orchestrator yet** — U-RT-46 wraps this primitive + adds
  the close-resources steps + the `AlreadyShutDown` idempotency guard.

### Test plan (~10 tests)

1. `test_flush_report_is_frozen` — Pydantic invariant.
2. `test_flush_observability_calls_tracer_force_flush` — monkeypatch
   tracer; verify call with timeout_millis.
3. `test_flush_observability_fsyncs_ledger_path` — write entry; flush;
   verify file contents flushed (poll fd via `fstat` + size).
4. `test_flush_observability_cost_chain_noop` — verify `cost_chain_noop=True`
   in report; chain isn't touched.
5. `test_flush_observability_reports_tracer_failure` — tracer raises;
   ledger still fsyncs; `failures=('tracer',)`.
6. `test_flush_observability_reports_fsync_failure` — patch fsync to raise;
   tracer still flushes; `failures=('ledger',)`.
7. `test_flush_observability_timeout_propagates` — slow tracer; surface
   `timed_out=True`.
8. `test_flush_uses_asyncio_to_thread_for_force_flush` — verify the OTel
   call is dispatched off the loop (count blocked-loop time).
9. `test_flush_report_failures_isolated_per_resource` — both fail; both
   in `failures` tuple.
10. `test_force_flush_returns_false_surfaces_in_report` — OTel returns
    False (timeout from inside OTel); `tracer_flushed=False`.

## Risks

- **R1: `ctx.tracer_provider: object` typed loosely.** Concrete is OTel
  `TracerProvider` per stage 4 (`ctx.tracer_provider = tracer.provider`).
  Cast at call site; document the runtime-type contract.
- **R2: fsync without dir-fsync.** File contents durable but dir entry
  could lag on crash. Track A acceptable; production-grade gate deferred.
- **R3: `asyncio.to_thread` overhead.** Per-flush extra thread switch.
  Acceptable for shutdown path.

## Out-of-scope (deferred)

- `shutdown()` orchestrator — U-RT-46.
- Resource-close steps (provider aclose, daemon stop, MCP disconnect, ledger
  close) — U-RT-46.
- `ShutdownReport` / `ShutdownTimeout` — U-RT-46.
- `AlreadyShutDown` idempotency guard — U-RT-46.
- Cost-chain in-memory state — would be a future spec revision.
