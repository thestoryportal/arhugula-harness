# U-RT-46 — shutdown() orchestrator (closes L10)

**Status:** in-progress
**Spec:** `Spec_Harness_Runtime_v1.md` v1.1 §10 (C-RT-10) — full shutdown sequence
**Decomposition:** L10 U-RT-46
**Predecessor:** U-RT-45 (`flush_observability`) at commit `5c73a02`

---

## Scope

Land `async def shutdown(ctx, *, timeout=30.0) -> ShutdownReport` — the full
C-RT-10 reverse-stage close sequence. Wraps U-RT-45's `flush_observability`
as step 2. Closes L10. Closes 5 of 6 C-RT-10 steps (in-flight wait at step 1
remains STRUCK per U-RT-44 fork).

## ACs

| AC | Status | Materialization |
|---|---|---|
| Reverse-stage close order | LAND | linear sequence; per-step status in report |
| Idempotency (second call safe) | LAND | `WeakValueDictionary[int, HarnessContext]` + cached report; `ShutdownReport.already_shutdown` field |
| Bounded by `timeout` parameter | LAND | budgeted-remaining pattern per step; surface `timed_out` in report |
| Per-resource fail-isolation | LAND | each step in own try/except; failures listed in `ShutdownReport.failures` |
| Audit-ledger head hash consistent post-shutdown | LAND | verification step reads ledger head + records in report |
| In-flight workflow step drain | **STRUCK** | covered by `[[fork-u-rt-44-workflow-loop-drain]]`; ctx.drained_flag is set but no loop polls it |

## Close-surface map (verified by grep)

| Component | At HEAD | Close at U-RT-46 |
|---|---|---|
| `lifecycle_emitter` | in-memory ring | NO-OP |
| `topology_dispatcher` | data structure | NO-OP |
| `override_evaluator` | data structure | NO-OP |
| `collector_daemon` | supervised subprocess | `await daemon.stop(timeout_seconds=N)` |
| `tracer_provider` | OTel SDK TracerProvider | `await asyncio.to_thread(provider.shutdown)` (sync API) |
| `audit_writer` | append-through to ledger | NO-OP |
| `cost_chain` | stateless composer | NO-OP |
| `routing_manifest` / `engine_selector` / `fallback_chain` | in-memory data | NO-OP |
| `retry_breaker` / `hitl_registry` / `handoff_registry` | caller-driven state | NO-OP (verified: no background tasks, no open files) |
| `providers` | per-provider clients | `await each.aclose()` |
| `mcp_clients` | placeholder dataclasses (U-RT-22) | NO-OP at HEAD |
| `mcp_host` | placeholder | NO-OP at HEAD |
| `ledger_writer` | per-append file open/close | implicit fsync via flush_observability (defensive re-fsync optional) |
| `index` / `cache` | JSON-file + in-memory | NO-OP (no close surface) |
| `worktree_manager` | reclaim_worktree per allocation | NO-OP at HEAD (no allocations until U-RT-49+ workloads) |

## Sequence

```python
async def shutdown(ctx, *, timeout=30.0) -> ShutdownReport:
    # Idempotency: second call returns cached report.
    if id(ctx) in _shutdown_registry:
        return _shutdown_registry[id(ctx)]._cached_report

    deadline = time.monotonic() + timeout
    failures: list[str] = []
    timed_out = False

    # Step 1 — drain. drained_flag is already set by signal in U-RT-44; we
    # programmatically set here for the no-signal path. AC #2 (in-flight
    # bounded wait) is STRUCK per fork.
    ctx.drained_flag.set()

    # Step 2 — flush observability (delegates to U-RT-45 primitive).
    remaining = max(0.0, deadline - time.monotonic())
    flush_report = await flush_observability(ctx, timeout_millis=int(remaining * 1000))
    if flush_report.failures or flush_report.timed_out:
        failures.extend(f"flush:{tag}" for tag in flush_report.failures)
        if flush_report.timed_out:
            timed_out = True

    # Step 3 — close stage-5/4/3b/3a in reverse:
    #   (5 emitter/dispatch — no-op)
    #   collector daemon
    remaining = max(0.0, deadline - time.monotonic())
    try:
        await ctx.collector_daemon.stop(timeout_seconds=remaining)
    except Exception:
        failures.append("collector_daemon")

    #   tracer provider (sync — to_thread)
    try:
        await asyncio.to_thread(ctx.tracer_provider.shutdown)
    except Exception:
        failures.append("tracer_provider")

    #   audit/cost/routing — no-op
    #   providers
    for name, provider in ctx.providers.items():
        try:
            await provider.aclose()
        except Exception:
            failures.append(f"provider:{name}")

    # Step 4 — MCP clients + host: no-op at HEAD.
    # Step 5 — ledger/index/cache/worktree: no-op at HEAD.

    # Step 6 — verify audit-ledger head hash consistency.
    audit_head = _read_audit_ledger_head(ctx)  # via ctx.audit_writer.read_all()[-1]

    # Final timing check.
    if time.monotonic() > deadline:
        timed_out = True

    report = ShutdownReport(
        flush=flush_report,
        already_shutdown=False,
        timed_out=timed_out,
        failures=tuple(failures),
        audit_ledger_head_hash=audit_head,
    )
    _shutdown_registry[id(ctx)] = ctx  # WeakValueDictionary
    _cached_reports[id(ctx)] = report
    weakref.finalize(ctx, _discard_cached_report, id(ctx))
    return report
```

## Types

```python
class ShutdownReport(BaseModel):
    model_config = ConfigDict(frozen=True)
    flush: FlushReport
    already_shutdown: bool
    timed_out: bool
    failures: tuple[str, ...]
    audit_ledger_head_hash: str | None  # None if ledger empty / unreadable

class ShutdownTimeout(Exception):
    """RT-FAIL-SHUTDOWN-TIMEOUT — caller-escalated when ShutdownReport.timed_out."""

class AlreadyShutDown(Exception):
    """RT-FAIL-ALREADY-SHUTDOWN — caller-escalated when ShutdownReport.already_shutdown."""
```

Neither typed error is raised by `shutdown()` — both are escalation primitives
for callers who want to convert a report flag to a raise. Mirrors U-RT-45's
`FlushTimeoutError` discipline.

## Test plan (~17 tests)

1. `test_shutdown_report_frozen` — schema invariant.
2. `test_shutdown_happy_path` — all closes succeed; flush succeeds; report
   clean.
3. `test_shutdown_sets_drained_flag` — step 1 verification.
4. `test_shutdown_delegates_step_2_to_flush_observability` — flush called
   with budgeted timeout.
5. `test_shutdown_stops_collector_daemon` — daemon.stop awaited.
6. `test_shutdown_invokes_tracer_provider_shutdown_in_thread` — to_thread
   dispatch verified.
7. `test_shutdown_acloses_each_provider` — every provider.aclose awaited.
8. `test_shutdown_continues_past_collector_failure` — daemon.stop raises;
   tracer + providers still close; report lists collector_daemon failure.
9. `test_shutdown_continues_past_tracer_failure` — same shape.
10. `test_shutdown_continues_past_provider_failure` — same shape; per-provider
    granularity in report.
11. `test_shutdown_idempotent_returns_cached_report` — second call with
    same ctx returns identical report; close primitives NOT re-invoked.
12. `test_shutdown_cached_report_freed_on_gc` — gc the ctx, cached report
    discarded by `weakref.finalize`.
13. `test_shutdown_timed_out_when_collector_exhausts_budget` — slow daemon;
    `timed_out=True`.
14. `test_shutdown_records_audit_ledger_head_hash` — verify hash present
    and matches last ledger entry.
15. `test_shutdown_audit_head_none_on_empty_ledger` — genesis case.
16. `test_shutdown_already_shutdown_typed_error_subclass` — surface check.
17. `test_shutdown_package_root_re_export`.

## Files

- `harness-runtime/src/harness_runtime/shutdown.py` — extend (add types
  + orchestrator function + idempotency registry). Net ~250 LOC.
- `harness-runtime/tests/test_shutdown.py` — extend with 17 new tests.
- `harness-runtime/src/harness_runtime/__init__.py` — re-export
  `shutdown`, `ShutdownReport`, `ShutdownTimeout`, `AlreadyShutDown`.

## Risks

- **R1 (idempotency id-collision):** `set[int]` keyed by `id()` has gc'd-id
  reuse risk. Mitigated via `WeakValueDictionary` + `weakref.finalize`.
- **R2 (budgeted-timeout cascading):** if step 2 burns the whole budget,
  subsequent steps run with `timeout=0`. Per spec invariant "shutdown does
  not abort on first failure" — closes still attempted with 0 budget; they
  may quick-fail and that surfaces in failures tuple.
- **R3 (cached frozen ctx in registry):** WeakValueDictionary holds ctx
  weakly; doesn't prevent gc.

## Out-of-scope

- In-flight workflow step drain (AC #2 STRUCK — `[[fork-u-rt-44-workflow-loop-drain]]`).
- MCP real-disconnect (placeholder per U-RT-22).
- Worktree lease reclamation (no allocations until U-RT-49+).
- Provider close re-entrancy semantics beyond per-provider try/except.
