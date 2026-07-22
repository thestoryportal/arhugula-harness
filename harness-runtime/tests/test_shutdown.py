"""U-RT-45 — flush_observability primitive tests.

Acceptance criteria per Phase 2 Session 3 atomic decomposition L10 U-RT-45 +
spec §10 C-RT-10 step 2:

- AC #1: all spans visible in collector sqlite post-flush.
- AC #2: ledger chain head consistent post-flush.

Test surfaces:
- FlushReport schema invariants
- tracer force_flush dispatched via asyncio.to_thread (sync OTel call doesn't block loop)
- ledger fsync executed on canonical_path
- cost-chain no-op (stateless-by-design per U-RT-31)
- per-resource failure isolation (one fails, others still run)
- timeout surfaced when force_flush returns False
- idempotent re-flush
- typed FlushTimeoutError surface available for callers that want to escalate
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from harness_runtime.shutdown import (
    AlreadyShutDown,
    FlushReport,
    FlushTimeoutError,
    ShutdownReport,
    ShutdownTimeout,
    flush_observability,
    shutdown,
)
from pydantic import ValidationError

# `harness_runtime.shutdown` attribute is shadowed by the `shutdown` function
# re-exported in `harness_runtime/__init__.py`. Go through sys.modules to
# reach the actual submodule for registry introspection.
shutdown_mod = sys.modules["harness_runtime.shutdown"]

# ---------------------------------------------------------------------------
# Fixtures.
# ---------------------------------------------------------------------------


class _FakeTracerProvider:
    """OTel-shaped tracer provider stub — records the timeout passed."""

    def __init__(self, *, returns: bool = True, raises: Exception | None = None) -> None:
        self.calls: list[int] = []
        self._returns = returns
        self._raises = raises

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        self.calls.append(timeout_millis)
        if self._raises is not None:
            raise self._raises
        return self._returns


def _ctx_with(
    tmp_path: Path,
    *,
    tracer: object,
    ledger_path: Path | None = None,
) -> Any:
    """Build a duck-typed `HarnessContext` good enough for flush_observability.

    The flush primitive uses two attributes only — `tracer_provider` and
    `ledger_writer.handle.canonical_path`. We don't need the full bootstrap.
    """
    path = ledger_path if ledger_path is not None else tmp_path / "state.jsonl"
    path.write_text("")  # ensure file exists for fsync
    handle = SimpleNamespace(canonical_path=path)
    ledger_writer = SimpleNamespace(handle=handle)
    return SimpleNamespace(tracer_provider=tracer, ledger_writer=ledger_writer)


# ---------------------------------------------------------------------------
# FlushReport schema.
# ---------------------------------------------------------------------------


def test_flush_report_is_frozen() -> None:
    report = FlushReport(
        tracer_flushed=True,
        ledger_fsynced=True,
        cost_chain_noop=True,
        timed_out=False,
        failures=(),
    )
    with pytest.raises(ValidationError):
        report.tracer_flushed = False  # type: ignore[misc]


def test_flush_report_failures_must_be_tuple() -> None:
    report = FlushReport(
        tracer_flushed=False,
        ledger_fsynced=True,
        cost_chain_noop=True,
        timed_out=False,
        failures=("tracer",),
    )
    assert report.failures == ("tracer",)
    assert isinstance(report.failures, tuple)


# ---------------------------------------------------------------------------
# Happy path.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_flush_observability_happy_path(tmp_path: Path) -> None:
    """Both surfaces succeed; cost-chain reports no-op."""
    tracer = _FakeTracerProvider(returns=True)
    ctx = _ctx_with(tmp_path, tracer=tracer)

    report = await flush_observability(ctx, timeout_millis=5_000)

    assert report.tracer_flushed is True
    assert report.ledger_fsynced is True
    assert report.cost_chain_noop is True
    assert report.timed_out is False
    assert report.failures == ()
    assert tracer.calls == [5_000]


@pytest.mark.asyncio
async def test_flush_observability_uses_default_timeout(tmp_path: Path) -> None:
    tracer = _FakeTracerProvider()
    ctx = _ctx_with(tmp_path, tracer=tracer)

    await flush_observability(ctx)

    assert tracer.calls == [30_000]


# ---------------------------------------------------------------------------
# Per-surface execution.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_flush_bounded_when_fsync_stalls(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Codex round-47 P2 — an fsync against a stalled filesystem (network
    mount, dying disk) must not hang shutdown past the advertised timeout:
    both fsync surfaces dispatch to a bounded worker; the stall is recorded
    as a per-surface failure + timed_out and shutdown proceeds."""
    import time as time_module

    ledger_path = tmp_path / "state.jsonl"
    ledger_path.write_text("entry-1\n")
    sidecar_path = tmp_path / "audit-entries.jsonl"
    sidecar_path.write_text('{"tenant_tag":"_single","entry":{}}\n')

    def _stalled_fsync(fd: int) -> None:
        time_module.sleep(1.5)

    monkeypatch.setattr(os, "fsync", _stalled_fsync)
    tracer = _FakeTracerProvider(returns=True)
    ctx = _ctx_with(tmp_path, tracer=tracer, ledger_path=ledger_path)
    ctx.audit_writer = SimpleNamespace(
        sidecar_path=sidecar_path,
        sidecar_expected=lambda: True,
    )

    start = time_module.monotonic()
    report = await flush_observability(ctx, timeout_millis=200)
    elapsed = time_module.monotonic() - start

    # Two bounded 200ms waits — far under the 1.5s a single synchronous
    # stalled fsync would take on the loop.
    assert elapsed < 1.2
    assert "audit_sidecar" in report.failures
    assert "ledger" in report.failures
    assert report.timed_out is True
    assert report.ledger_fsynced is False


def test_asyncio_run_teardown_not_blocked_by_stalled_fsync(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Codex round-48 P1 — `asyncio.to_thread` workers live in the loop's
    default executor, which `asyncio.run`'s teardown JOINS: a genuinely
    stalled fsync hung process exit even after the timeout report was
    returned. The daemon-thread worker is never joined — the WHOLE
    `asyncio.run` (teardown included) must return within the bound."""
    import time as time_module

    ledger_path = tmp_path / "state.jsonl"
    ledger_path.write_text("entry-1\n")

    def _stalled_fsync(fd: int) -> None:
        time_module.sleep(1.5)

    monkeypatch.setattr(os, "fsync", _stalled_fsync)
    tracer = _FakeTracerProvider(returns=True)
    ctx = _ctx_with(tmp_path, tracer=tracer, ledger_path=ledger_path)

    start = time_module.monotonic()
    report = asyncio.run(flush_observability(ctx, timeout_millis=200))
    elapsed = time_module.monotonic() - start

    assert elapsed < 1.2
    assert "ledger" in report.failures
    assert report.timed_out is True


@pytest.mark.asyncio
async def test_flush_surfaces_share_one_timeout_budget(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Codex round-48 P2 — per-surface full timeouts let flush consume ~2x
    the caller's budget sequentially (sidecar 600ms + ledger 600ms). With
    one shared monotonic deadline the ledger surface gets only the
    remainder, so total wall time stays ~one budget."""
    import time as time_module

    ledger_path = tmp_path / "state.jsonl"
    ledger_path.write_text("entry-1\n")
    sidecar_path = tmp_path / "audit-entries.jsonl"
    sidecar_path.write_text('{"tenant_tag":"_single","entry":{}}\n')

    def _stalled_fsync(fd: int) -> None:
        time_module.sleep(1.5)

    monkeypatch.setattr(os, "fsync", _stalled_fsync)
    tracer = _FakeTracerProvider(returns=True)
    ctx = _ctx_with(tmp_path, tracer=tracer, ledger_path=ledger_path)
    ctx.audit_writer = SimpleNamespace(
        sidecar_path=sidecar_path,
        sidecar_expected=lambda: True,
    )

    start = time_module.monotonic()
    report = await flush_observability(ctx, timeout_millis=600)
    elapsed = time_module.monotonic() - start

    # Shared budget: sidecar consumes ~600ms, ledger gets ~0 remaining.
    # Per-surface budgets would take ~1.2s.
    assert elapsed < 0.9
    assert "audit_sidecar" in report.failures
    assert "ledger" in report.failures
    assert report.timed_out is True


@pytest.mark.asyncio
async def test_flush_observability_runs_tracer_in_thread(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sync `force_flush` must be dispatched off the event loop."""
    to_thread_calls: list[tuple[object, tuple[object, ...]]] = []

    async def _spy_to_thread(fn: object, *args: object) -> object:
        to_thread_calls.append((fn, args))
        return fn(*args)  # type: ignore[operator]

    monkeypatch.setattr(asyncio, "to_thread", _spy_to_thread)
    tracer = _FakeTracerProvider(returns=True)
    ctx = _ctx_with(tmp_path, tracer=tracer)

    await flush_observability(ctx, timeout_millis=1_000)

    # The ledger fsync ALSO dispatches via to_thread (codex round-47 P2);
    # assert the tracer call specifically rather than an exact count.
    tracer_calls = [
        (fn, args)
        for fn, args in to_thread_calls
        # Bound-method identity isn't stable across attribute accesses;
        # compare by __func__ (the underlying function) instead.
        if getattr(fn, "__func__", None) is _FakeTracerProvider.force_flush
    ]
    assert len(tracer_calls) == 1
    assert tracer_calls[0][1] == (1_000,)


@pytest.mark.asyncio
async def test_flush_observability_fsyncs_ledger_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`os.fsync` is called with the open fd of the ledger canonical_path."""
    ledger_path = tmp_path / "state.jsonl"
    ledger_path.write_text("entry-1\n")

    fsynced_fds: list[int] = []
    real_fsync = os.fsync

    def _spy_fsync(fd: int) -> None:
        fsynced_fds.append(fd)
        real_fsync(fd)

    monkeypatch.setattr(os, "fsync", _spy_fsync)
    tracer = _FakeTracerProvider(returns=True)
    ctx = _ctx_with(tmp_path, tracer=tracer, ledger_path=ledger_path)

    report = await flush_observability(ctx)

    assert report.ledger_fsynced is True
    assert len(fsynced_fds) == 1
    # fd is process-local; can't assert exact value but it must be valid.
    assert fsynced_fds[0] >= 0


# ---------------------------------------------------------------------------
# Failure isolation.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_tracer_failure_does_not_block_ledger_flush(tmp_path: Path) -> None:
    tracer = _FakeTracerProvider(raises=RuntimeError("BSP broken"))
    ctx = _ctx_with(tmp_path, tracer=tracer)

    report = await flush_observability(ctx)

    assert report.tracer_flushed is False
    assert report.ledger_fsynced is True
    assert report.failures == ("tracer",)


@pytest.mark.asyncio
async def test_ledger_failure_does_not_block_tracer_flush(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _broken_fsync(fd: int) -> None:
        raise OSError("fsync failed")

    monkeypatch.setattr(os, "fsync", _broken_fsync)
    tracer = _FakeTracerProvider(returns=True)
    ctx = _ctx_with(tmp_path, tracer=tracer)

    report = await flush_observability(ctx)

    assert report.tracer_flushed is True
    assert report.ledger_fsynced is False
    assert report.failures == ("ledger",)


@pytest.mark.asyncio
async def test_both_surfaces_fail_both_recorded(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _broken_fsync(fd: int) -> None:
        raise OSError("fsync failed")

    monkeypatch.setattr(os, "fsync", _broken_fsync)
    tracer = _FakeTracerProvider(raises=RuntimeError("BSP broken"))
    ctx = _ctx_with(tmp_path, tracer=tracer)

    report = await flush_observability(ctx)

    assert report.tracer_flushed is False
    assert report.ledger_fsynced is False
    assert set(report.failures) == {"tracer", "ledger"}


# ---------------------------------------------------------------------------
# Timeout surfacing.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_force_flush_returning_false_surfaces_timed_out(tmp_path: Path) -> None:
    """OTel BSP returns False on internal timeout — propagate to FlushReport."""
    tracer = _FakeTracerProvider(returns=False)
    ctx = _ctx_with(tmp_path, tracer=tracer)

    report = await flush_observability(ctx, timeout_millis=100)

    assert report.tracer_flushed is False
    assert report.timed_out is True
    assert report.failures == ()  # not a failure — it's a timeout result


# ---------------------------------------------------------------------------
# Idempotency.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_flush_observability_is_idempotent(tmp_path: Path) -> None:
    """Calling flush twice surfaces identical reports."""
    tracer = _FakeTracerProvider(returns=True)
    ctx = _ctx_with(tmp_path, tracer=tracer)

    r1 = await flush_observability(ctx)
    r2 = await flush_observability(ctx)

    assert r1 == r2
    assert tracer.calls == [30_000, 30_000]


# ---------------------------------------------------------------------------
# Typed surfaces.
# ---------------------------------------------------------------------------


def test_flush_timeout_error_is_timeout_subclass() -> None:
    assert issubclass(FlushTimeoutError, TimeoutError)


def test_flush_observability_package_root_re_export() -> None:
    import harness_runtime

    assert harness_runtime.flush_observability is flush_observability
    assert harness_runtime.FlushReport is FlushReport
    assert harness_runtime.FlushTimeoutError is FlushTimeoutError


# ===========================================================================
# U-RT-46 — shutdown() orchestrator tests.
# ===========================================================================


class _FakeCollectorDaemon:
    def __init__(self, *, raises: Exception | None = None, sleep: float = 0.0) -> None:
        self.stopped = False
        self._raises = raises
        self._sleep = sleep
        self.last_timeout: float | None = None

    async def stop(self, *, timeout_seconds: float = 5.0) -> None:
        self.last_timeout = timeout_seconds
        if self._sleep:
            await asyncio.sleep(self._sleep)
        if self._raises is not None:
            raise self._raises
        self.stopped = True


class _FakeTracerWithShutdown(_FakeTracerProvider):
    def __init__(
        self,
        *,
        returns: bool = True,
        raises: Exception | None = None,
        shutdown_raises: Exception | None = None,
        shutdown_sleep: float = 0.0,
    ) -> None:
        super().__init__(returns=returns, raises=raises)
        self.shutdown_called = False
        self._shutdown_raises = shutdown_raises
        self._shutdown_sleep = shutdown_sleep

    def shutdown(self) -> None:
        if self._shutdown_sleep:
            import time as _time

            _time.sleep(self._shutdown_sleep)
        self.shutdown_called = True
        if self._shutdown_raises is not None:
            raise self._shutdown_raises


class _FakeProvider:
    def __init__(self, *, raises: Exception | None = None, aclose_sleep: float = 0.0) -> None:
        self.closed = False
        self._raises = raises
        self._aclose_sleep = aclose_sleep

    async def aclose(self) -> None:
        if self._aclose_sleep:
            await asyncio.sleep(self._aclose_sleep)
        if self._raises is not None:
            raise self._raises
        self.closed = True


class _FakeMcpHost:
    def __init__(self, *, started: bool = True, shutdown_sleep: float = 0.0) -> None:
        self.started = started
        self.shutdown_called = False
        self._shutdown_sleep = shutdown_sleep

    async def shutdown(self) -> None:
        if self._shutdown_sleep:
            await asyncio.sleep(self._shutdown_sleep)
        self.shutdown_called = True


class _FakeAuditWriter:
    """`response_hash` matches the real StateLedgerEntry schema (bytes per C-IS-05).

    Earlier fixture used `chain_hash=` against the (now-fixed) defect in
    `shutdown._read_audit_head_hash`; this aligns with the real schema.
    """

    def __init__(self, head_hash: str | None = "deadbeef") -> None:
        self._head = head_hash

    def read_all(self) -> list[object]:
        if self._head is None:
            return []
        return [SimpleNamespace(response_hash=bytes.fromhex(self._head))]


class _FakeDispatchExecutor:
    """Spy for the B-48 stage-5 sub-agent-dispatch executor's `drain()`."""

    def __init__(self, *, still_outstanding: int = 0, drain_sleep_seconds: float = 0.0) -> None:
        self.drain_called_with: float | None = None
        self.begin_draining_called = False
        self._still_outstanding = still_outstanding
        self._drain_sleep_seconds = drain_sleep_seconds

    def begin_draining(self) -> None:
        self.begin_draining_called = True

    def drain(self, *, deadline_seconds: float) -> tuple[int, int]:
        self.drain_called_with = deadline_seconds
        if self._drain_sleep_seconds:
            import time as _time

            _time.sleep(self._drain_sleep_seconds)
        return (0, self._still_outstanding)


class _FakeCtx:
    """Plain class so weakref + WeakValueDictionary work (SimpleNamespace doesn't)."""


def _shutdown_ctx(
    tmp_path: Path,
    *,
    tracer: _FakeTracerWithShutdown,
    daemon: _FakeCollectorDaemon,
    providers: dict[str, _FakeProvider],
    audit: _FakeAuditWriter | None = None,
    ledger_path: Path | None = None,
) -> Any:
    path = ledger_path if ledger_path is not None else tmp_path / "state.jsonl"
    path.write_text("")
    handle = SimpleNamespace(canonical_path=path)
    ledger_writer = SimpleNamespace(handle=handle)
    ctx = _FakeCtx()
    ctx.tracer_provider = tracer  # type: ignore[attr-defined]
    ctx.ledger_writer = ledger_writer  # type: ignore[attr-defined]
    ctx.drained_flag = asyncio.Event()  # type: ignore[attr-defined]
    ctx.collector_daemon = daemon  # type: ignore[attr-defined]
    ctx.providers = providers  # type: ignore[attr-defined]
    ctx.audit_writer = audit if audit is not None else _FakeAuditWriter()  # type: ignore[attr-defined]
    return ctx


@pytest.fixture(autouse=True)
def _isolate_shutdown_registry() -> Any:  # pyright: ignore[reportUnusedFunction]
    """Reset module-level registries between tests."""
    shutdown_mod._shutdown_registry.clear()  # type: ignore[attr-defined]
    shutdown_mod._cached_reports.clear()  # type: ignore[attr-defined]
    yield
    shutdown_mod._shutdown_registry.clear()  # type: ignore[attr-defined]
    shutdown_mod._cached_reports.clear()  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Schema.
# ---------------------------------------------------------------------------


def test_shutdown_report_is_frozen() -> None:
    flush = FlushReport(
        tracer_flushed=True,
        ledger_fsynced=True,
        cost_chain_noop=True,
        timed_out=False,
        failures=(),
    )
    report = ShutdownReport(
        flush=flush,
        already_shutdown=False,
        timed_out=False,
        failures=(),
        audit_ledger_head_hash="deadbeef",
    )
    with pytest.raises(ValidationError):
        report.already_shutdown = True  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Happy path + per-step verification.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_shutdown_happy_path(tmp_path: Path) -> None:
    tracer = _FakeTracerWithShutdown(returns=True)
    daemon = _FakeCollectorDaemon()
    providers = {"anthropic": _FakeProvider(), "openai": _FakeProvider()}
    ctx = _shutdown_ctx(tmp_path, tracer=tracer, daemon=daemon, providers=providers)

    report = await shutdown(ctx)

    assert report.already_shutdown is False
    assert report.timed_out is False
    assert report.failures == ()
    assert report.audit_ledger_head_hash == "deadbeef"
    assert report.flush.tracer_flushed is True
    assert report.flush.ledger_fsynced is True
    assert daemon.stopped is True
    assert tracer.shutdown_called is True
    assert all(p.closed for p in providers.values())


@pytest.mark.asyncio
async def test_shutdown_step_1_sets_drained_flag(tmp_path: Path) -> None:
    tracer = _FakeTracerWithShutdown()
    ctx = _shutdown_ctx(tmp_path, tracer=tracer, daemon=_FakeCollectorDaemon(), providers={})
    assert ctx.drained_flag.is_set() is False

    await shutdown(ctx)

    assert ctx.drained_flag.is_set() is True


@pytest.mark.asyncio
async def test_shutdown_delegates_step_2_to_flush(tmp_path: Path) -> None:
    """The report's inner `flush` field is populated by flush_observability."""
    tracer = _FakeTracerWithShutdown(returns=True)
    ctx = _shutdown_ctx(tmp_path, tracer=tracer, daemon=_FakeCollectorDaemon(), providers={})
    await shutdown(ctx, timeout=2.0)
    # force_flush should have been called with ~2000ms budget (allow drift).
    assert len(tracer.calls) == 1
    assert 0 < tracer.calls[0] <= 2_000


@pytest.mark.asyncio
async def test_shutdown_drains_stage_5_dispatch_executor(tmp_path: Path) -> None:
    """Step 3 must drain the B-48 stage-5 sub-agent-dispatch executor.

    Mutation probe: removing the `_drain_dispatch_executor` wiring from
    `shutdown()` leaves `drain_called_with` at None — the executor's daemon
    worker threads and their held frame leases would go undrained at
    shutdown, silently (the "stateless-by-design no-op" framing this
    docstring corrected).
    """
    dispatch_executor = _FakeDispatchExecutor(still_outstanding=0)
    ctx = _shutdown_ctx(
        tmp_path, tracer=_FakeTracerWithShutdown(), daemon=_FakeCollectorDaemon(), providers={}
    )
    ctx.sub_agent_dispatch_executor = dispatch_executor
    report = await shutdown(ctx, timeout=5.0)
    assert dispatch_executor.drain_called_with is not None
    assert "sub_agent_dispatch_executor" not in report.failures
    assert report.timed_out is False


class _FakeProtectedResultStore:
    """Spy for `ProtectedResultStore.gc_sweep` — records calls, optionally raises."""

    def __init__(self, *, raises: Exception | None = None) -> None:
        self.swept = False
        self._raises = raises

    def gc_sweep(self, *, now: float | None = None) -> list[str]:
        self.swept = True
        if self._raises is not None:
            raise self._raises
        return []


@pytest.mark.asyncio
async def test_shutdown_step_5b_sweeps_protected_result_store(tmp_path: Path) -> None:
    """B-65-A codex round-4 [P2] — this is the SHUTDOWN half of the
    "GC sweep at bootstrap/shutdown" fallback (spec v1.103 §14.8.11 AC 7);
    the row this closes previously claimed no graceful-teardown chain
    existed to hook it into. Mutation probe: removing step 5b from
    `shutdown()` leaves `store.swept` False — a long-lived daemon that
    never restarts would then never reap its OWN expired entries at exit,
    only a NEXT process's bootstrap sweep would (which never arrives if it
    never restarts).
    """
    store = _FakeProtectedResultStore()
    ctx = _shutdown_ctx(
        tmp_path, tracer=_FakeTracerWithShutdown(), daemon=_FakeCollectorDaemon(), providers={}
    )
    ctx.protected_result_store = store
    report = await shutdown(ctx, timeout=5.0)
    assert store.swept is True
    assert "protected_result_store" not in report.failures
    assert report.timed_out is False


@pytest.mark.asyncio
async def test_shutdown_isolates_protected_result_store_sweep_failure(tmp_path: Path) -> None:
    """B-65-A codex round-4 [P2] — per-resource exception isolation must
    cover the new step 5b like every other step: a raising sweep must not
    abort the rest of shutdown. Mutation probe: an unguarded call would
    propagate the exception out of `shutdown()`, failing this test with the
    stub's `RuntimeError` instead of a clean `ShutdownReport`.
    """
    store = _FakeProtectedResultStore(raises=RuntimeError("disk full"))
    tracer = _FakeTracerWithShutdown(returns=True)
    ctx = _shutdown_ctx(tmp_path, tracer=tracer, daemon=_FakeCollectorDaemon(), providers={})
    ctx.protected_result_store = store
    report = await shutdown(ctx, timeout=5.0)
    assert store.swept is True
    assert "protected_result_store" in report.failures
    assert report.audit_ledger_head_hash == "deadbeef"
    assert tracer.shutdown_called is True


@pytest.mark.asyncio
async def test_shutdown_skips_protected_result_store_sweep_when_absent(tmp_path: Path) -> None:
    """`None` store (fail-closed=OFF composition) must not be swept or
    recorded as a failure — mirrors the bootstrap-stage guard verbatim."""
    ctx = _shutdown_ctx(
        tmp_path, tracer=_FakeTracerWithShutdown(), daemon=_FakeCollectorDaemon(), providers={}
    )
    ctx.protected_result_store = None
    report = await shutdown(ctx, timeout=5.0)
    assert "protected_result_store" not in report.failures


@pytest.mark.asyncio
async def test_shutdown_flips_draining_even_at_zero_remaining_budget(tmp_path: Path) -> None:
    """Codex round-8 [P2] "enter draining state before scheduling the bounded
    wait": at `timeout=0.0` the bounded `asyncio.wait_for(...)` around
    `_drain_dispatch_executor` can cancel the whole coroutine before
    `dispatch_executor.drain(...)` (which flips `_draining` as its own first
    step) ever gets scheduled off-loop. The executor's admission surface
    must still close — `shutdown()` must call `begin_draining()` directly,
    independent of that bounded wait's own scheduling.

    Mutation probe: removing the eager `_pre_drain_executor.begin_draining()`
    call in `shutdown()` (leaving only `drain()`'s own internal call) makes
    `dispatch_executor.begin_draining_called` false here — at `timeout=0.0`
    `drain()` never runs at all (this test's `drain_called_with` stays
    `None`, confirming the bounded-wait cancellation actually happened).
    """
    dispatch_executor = _FakeDispatchExecutor(still_outstanding=0)
    ctx = _shutdown_ctx(
        tmp_path, tracer=_FakeTracerWithShutdown(), daemon=_FakeCollectorDaemon(), providers={}
    )
    ctx.sub_agent_dispatch_executor = dispatch_executor
    await shutdown(ctx, timeout=0.0)
    assert dispatch_executor.begin_draining_called is True


@pytest.mark.asyncio
async def test_shutdown_drains_dispatch_executor_before_flushing_observability(
    tmp_path: Path,
) -> None:
    """codex round-4 [P1] "drain dispatch jobs before flushing observability":
    a job still running when the observability flush fires can emit spans/
    audit entries THROUGH the flush window and past the tracer/exporter
    close that follows — draining the stage-5 executor first means any such
    write lands while the tracer is still open. Mutation probe: swapping the
    drain and flush steps back to flush-then-drain would record
    `["flush", "drain"]` here instead."""
    call_order: list[str] = []

    class _OrderRecordingDispatchExecutor:
        def begin_draining(self) -> None:
            pass

        def drain(self, *, deadline_seconds: float) -> tuple[int, int]:
            call_order.append("drain")
            return (0, 0)

    class _OrderRecordingTracer(_FakeTracerWithShutdown):
        def force_flush(self, timeout_millis: int = 30_000) -> bool:
            call_order.append("flush")
            return super().force_flush(timeout_millis)

    ctx = _shutdown_ctx(
        tmp_path,
        tracer=_OrderRecordingTracer(returns=True),
        daemon=_FakeCollectorDaemon(),
        providers={},
    )
    ctx.sub_agent_dispatch_executor = _OrderRecordingDispatchExecutor()
    report = await shutdown(ctx, timeout=5.0)
    assert call_order == ["drain", "flush"]
    assert "sub_agent_dispatch_executor" not in report.failures


@pytest.mark.asyncio
async def test_shutdown_bounded_by_timeout_when_dispatch_executor_drain_hangs(
    tmp_path: Path,
) -> None:
    """codex round-4 [P2] "include drain scheduling in the shutdown deadline":
    a hanging (or scheduling-delayed) dispatch-executor drain must not block
    the rest of the shutdown sequence indefinitely — mirrors
    `test_shutdown_bounded_by_timeout_when_tracer_shutdown_hangs`. Previously
    `await _drain_dispatch_executor(ctx, remaining)` had no `asyncio.wait_for`
    wrapper of its own, so a slow-to-schedule-or-run drain (e.g. the loop's
    default thread pool saturated by other `to_thread` work) could push the
    whole shutdown sequence past its overall deadline.

    Mutation probe: removing the `asyncio.wait_for(...)` wrapper around this
    step reverts to waiting out the full 0.3s sleep instead of bounding to
    ~0.02s — this test's elapsed-time assertion would then fail."""
    dispatch_executor = _FakeDispatchExecutor(drain_sleep_seconds=0.3)
    ctx = _shutdown_ctx(
        tmp_path, tracer=_FakeTracerWithShutdown(), daemon=_FakeCollectorDaemon(), providers={}
    )
    ctx.sub_agent_dispatch_executor = dispatch_executor
    start = asyncio.get_event_loop().time()
    report = await asyncio.wait_for(shutdown(ctx, timeout=0.02), timeout=1.0)
    elapsed = asyncio.get_event_loop().time() - start
    assert elapsed < 0.3, "shutdown() waited out the full hang instead of bounding it"
    assert "sub_agent_dispatch_executor" in report.failures
    assert report.timed_out is True


@pytest.mark.asyncio
async def test_shutdown_reports_failure_when_dispatch_executor_cannot_drain(
    tmp_path: Path,
) -> None:
    dispatch_executor = _FakeDispatchExecutor(still_outstanding=2)
    ctx = _shutdown_ctx(
        tmp_path, tracer=_FakeTracerWithShutdown(), daemon=_FakeCollectorDaemon(), providers={}
    )
    ctx.sub_agent_dispatch_executor = dispatch_executor
    report = await shutdown(ctx, timeout=5.0)
    assert "sub_agent_dispatch_executor" in report.failures
    assert report.timed_out is True


@pytest.mark.asyncio
async def test_shutdown_missing_dispatch_executor_attr_is_a_noop(tmp_path: Path) -> None:
    """No `sub_agent_dispatch_executor` attr (pre-B-48 ctx shape) — no-op, no failure."""
    ctx = _shutdown_ctx(
        tmp_path, tracer=_FakeTracerWithShutdown(), daemon=_FakeCollectorDaemon(), providers={}
    )
    assert not hasattr(ctx, "sub_agent_dispatch_executor")
    report = await shutdown(ctx, timeout=5.0)
    assert "sub_agent_dispatch_executor" not in report.failures


@pytest.mark.asyncio
async def test_shutdown_stops_collector_daemon(tmp_path: Path) -> None:
    daemon = _FakeCollectorDaemon()
    ctx = _shutdown_ctx(
        tmp_path,
        tracer=_FakeTracerWithShutdown(),
        daemon=daemon,
        providers={},
    )
    await shutdown(ctx, timeout=5.0)
    assert daemon.stopped is True
    assert daemon.last_timeout is not None
    assert daemon.last_timeout >= 0


@pytest.mark.asyncio
async def test_shutdown_invokes_tracer_shutdown_via_to_thread(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sync OTel `shutdown()` must be dispatched off the event loop."""
    to_thread_targets: list[object] = []

    real_to_thread = asyncio.to_thread

    async def _spy(fn: object, *args: object) -> object:
        to_thread_targets.append(fn)
        return await real_to_thread(fn, *args)  # type: ignore[arg-type]

    monkeypatch.setattr(asyncio, "to_thread", _spy)
    tracer = _FakeTracerWithShutdown(returns=True)
    ctx = _shutdown_ctx(tmp_path, tracer=tracer, daemon=_FakeCollectorDaemon(), providers={})

    await shutdown(ctx)

    # to_thread was used for both flush (force_flush) AND shutdown.
    assert tracer.shutdown_called is True
    assert len(to_thread_targets) >= 2  # force_flush + shutdown


@pytest.mark.asyncio
async def test_shutdown_acloses_each_provider(tmp_path: Path) -> None:
    providers = {
        "anthropic": _FakeProvider(),
        "openai": _FakeProvider(),
        "ollama": _FakeProvider(),
    }
    ctx = _shutdown_ctx(
        tmp_path,
        tracer=_FakeTracerWithShutdown(),
        daemon=_FakeCollectorDaemon(),
        providers=providers,
    )
    await shutdown(ctx)
    assert all(p.closed for p in providers.values())


# ---------------------------------------------------------------------------
# Per-resource failure isolation.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_shutdown_continues_past_collector_failure(tmp_path: Path) -> None:
    tracer = _FakeTracerWithShutdown()
    providers = {"anthropic": _FakeProvider()}
    ctx = _shutdown_ctx(
        tmp_path,
        tracer=tracer,
        daemon=_FakeCollectorDaemon(raises=RuntimeError("daemon broken")),
        providers=providers,
    )

    report = await shutdown(ctx)

    assert "collector_daemon" in report.failures
    assert tracer.shutdown_called is True  # tracer still closed
    assert providers["anthropic"].closed is True  # provider still closed


@pytest.mark.asyncio
async def test_shutdown_continues_past_tracer_shutdown_failure(tmp_path: Path) -> None:
    daemon = _FakeCollectorDaemon()
    providers = {"anthropic": _FakeProvider()}
    ctx = _shutdown_ctx(
        tmp_path,
        tracer=_FakeTracerWithShutdown(shutdown_raises=RuntimeError("tracer broken")),
        daemon=daemon,
        providers=providers,
    )

    report = await shutdown(ctx)

    assert "tracer_provider" in report.failures
    assert daemon.stopped is True
    assert providers["anthropic"].closed is True


@pytest.mark.asyncio
async def test_shutdown_per_provider_failure_granularity(tmp_path: Path) -> None:
    providers = {
        "anthropic": _FakeProvider(),
        "openai": _FakeProvider(raises=RuntimeError("openai broken")),
        "ollama": _FakeProvider(),
    }
    ctx = _shutdown_ctx(
        tmp_path,
        tracer=_FakeTracerWithShutdown(),
        daemon=_FakeCollectorDaemon(),
        providers=providers,
    )

    report = await shutdown(ctx)

    assert "provider:openai" in report.failures
    assert "provider:anthropic" not in report.failures
    assert "provider:ollama" not in report.failures
    assert providers["anthropic"].closed is True
    assert providers["ollama"].closed is True


# ---------------------------------------------------------------------------
# Idempotency.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_shutdown_idempotent_second_call_returns_cached(tmp_path: Path) -> None:
    daemon = _FakeCollectorDaemon()
    tracer = _FakeTracerWithShutdown()
    providers = {"anthropic": _FakeProvider()}
    ctx = _shutdown_ctx(tmp_path, tracer=tracer, daemon=daemon, providers=providers)

    r1 = await shutdown(ctx)
    # Reset side-effect markers; second call must NOT re-invoke closes.
    daemon.stopped = False
    tracer.shutdown_called = False
    providers["anthropic"].closed = False

    r2 = await shutdown(ctx)

    assert r1.already_shutdown is False
    assert r2.already_shutdown is True
    # Apart from the flag, the body is identical.
    assert r2.flush == r1.flush
    assert r2.failures == r1.failures
    assert r2.audit_ledger_head_hash == r1.audit_ledger_head_hash
    # Close primitives NOT re-invoked.
    assert daemon.stopped is False
    assert tracer.shutdown_called is False
    assert providers["anthropic"].closed is False


@pytest.mark.asyncio
async def test_shutdown_cached_report_freed_on_ctx_gc(tmp_path: Path) -> None:
    """weakref.finalize discards the cached report when ctx is gc'd."""
    import gc

    ctx = _shutdown_ctx(
        tmp_path,
        tracer=_FakeTracerWithShutdown(),
        daemon=_FakeCollectorDaemon(),
        providers={},
    )
    ctx_id = id(ctx)
    await shutdown(ctx)
    assert ctx_id in shutdown_mod._cached_reports  # type: ignore[attr-defined]

    del ctx
    gc.collect()

    assert ctx_id not in shutdown_mod._cached_reports  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Timeout / audit head / typed errors.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_shutdown_records_audit_ledger_head(tmp_path: Path) -> None:
    audit = _FakeAuditWriter(head_hash="cafef00d")
    ctx = _shutdown_ctx(
        tmp_path,
        tracer=_FakeTracerWithShutdown(),
        daemon=_FakeCollectorDaemon(),
        providers={},
        audit=audit,
    )
    report = await shutdown(ctx)
    assert report.audit_ledger_head_hash == "cafef00d"


@pytest.mark.asyncio
async def test_shutdown_audit_head_none_on_empty_ledger(tmp_path: Path) -> None:
    audit = _FakeAuditWriter(head_hash=None)
    ctx = _shutdown_ctx(
        tmp_path,
        tracer=_FakeTracerWithShutdown(),
        daemon=_FakeCollectorDaemon(),
        providers={},
        audit=audit,
    )
    report = await shutdown(ctx)
    assert report.audit_ledger_head_hash is None


@pytest.mark.asyncio
async def test_shutdown_audit_head_from_real_state_ledger_entry(tmp_path: Path) -> None:
    """Regression test for the 2026-05-20 U-RT-46 chain_hash fix.

    Earlier `_read_audit_head_hash` read `entry.chain_hash` — an attribute
    `StateLedgerEntry` doesn't expose. Real entries have `response_hash:
    Bytes32` per C-IS-05 / C-IS-06. The fake fixture masked this. This
    test builds an entry with the real schema and asserts the helper
    returns the lowercase hex of `response_hash`.
    """
    from harness_is.entry_hash import compute_response_hash
    from harness_is.state_ledger_entry_schema import (
        Actor,
        ActorClass,
        Identifier,
        StateLedgerEntry,
    )

    actor = Actor(actor_class=ActorClass.AGENT, actor_id="harness-runtime")
    # Build a draft to compute response_hash, then a real entry.
    draft = StateLedgerEntry(
        action_id=Identifier("action-1"),
        idempotency_key=Identifier("idem-1"),
        actor=actor,
        response_hash=b"\x00" * 32,  # placeholder; recomputed below
        timestamp=0,
        prior_event_hash=b"\x00" * 32,
    )
    entry = draft.model_copy(update={"response_hash": compute_response_hash(draft)})

    class _RealishAudit:
        def read_all(self) -> list[object]:
            return [entry]

    ctx = _shutdown_ctx(
        tmp_path,
        tracer=_FakeTracerWithShutdown(),
        daemon=_FakeCollectorDaemon(),
        providers={},
        audit=_RealishAudit(),  # type: ignore[arg-type]
    )
    report = await shutdown(ctx)

    assert report.audit_ledger_head_hash == entry.response_hash.hex()
    assert len(report.audit_ledger_head_hash) == 64  # SHA-256 hex


# ---------------------------------------------------------------------------
# U-RT-48 — pidfile removal at end of shutdown().
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_shutdown_removes_pidfile(tmp_path: Path) -> None:
    """U-RT-48: shutdown() removes the pidfile written by stage 7 per spec §13."""
    from harness_runtime.admin.pidfile import write_pidfile

    pidfile = tmp_path / ".harness/runtime.pid"
    write_pidfile(pidfile, 12345)
    assert pidfile.exists()

    class _ConfigStub:
        repository_root = tmp_path
        pidfile_path = None

    ctx = _shutdown_ctx(
        tmp_path,
        tracer=_FakeTracerWithShutdown(),
        daemon=_FakeCollectorDaemon(),
        providers={},
    )
    ctx.config = _ConfigStub()  # type: ignore[attr-defined]

    report = await shutdown(ctx)

    assert not pidfile.exists()
    assert "pidfile" not in report.failures


@pytest.mark.asyncio
async def test_shutdown_pidfile_removal_idempotent_on_missing(
    tmp_path: Path,
) -> None:
    """Removing an already-gone pidfile is a clean no-op (no failure recorded)."""

    class _ConfigStub:
        repository_root = tmp_path
        pidfile_path = None

    ctx = _shutdown_ctx(
        tmp_path,
        tracer=_FakeTracerWithShutdown(),
        daemon=_FakeCollectorDaemon(),
        providers={},
    )
    ctx.config = _ConfigStub()  # type: ignore[attr-defined]

    # No pidfile written; shutdown should still succeed.
    report = await shutdown(ctx)
    assert "pidfile" not in report.failures


@pytest.mark.asyncio
async def test_shutdown_timed_out_when_collector_slow(tmp_path: Path) -> None:
    """Collector exhausts budget — `timed_out=True` after deadline check."""
    daemon = _FakeCollectorDaemon(sleep=0.05)
    ctx = _shutdown_ctx(
        tmp_path,
        tracer=_FakeTracerWithShutdown(),
        daemon=daemon,
        providers={},
    )
    # Tight budget — collector sleeps 50ms, budget is 20ms.
    report = await shutdown(ctx, timeout=0.02)
    assert report.timed_out is True


@pytest.mark.asyncio
async def test_shutdown_bounded_by_timeout_when_tracer_shutdown_hangs(tmp_path: Path) -> None:
    """Regression — a hanging `tracer_provider.shutdown()` must not block the
    rest of the shutdown sequence indefinitely. Previously this call had no
    `asyncio.wait_for`/deadline wrapper at all, despite the docstring's
    "bounded by timeout: each step is allotted the remaining budget"
    invariant."""
    tracer = _FakeTracerWithShutdown(shutdown_sleep=0.3)
    ctx = _shutdown_ctx(
        tmp_path,
        tracer=tracer,
        daemon=_FakeCollectorDaemon(),
        providers={},
    )
    start = asyncio.get_event_loop().time()
    report = await asyncio.wait_for(shutdown(ctx, timeout=0.02), timeout=1.0)
    elapsed = asyncio.get_event_loop().time() - start
    assert elapsed < 0.3, "shutdown() waited out the full hang instead of bounding it"
    assert "tracer_provider" in report.failures
    assert report.timed_out is True


@pytest.mark.asyncio
async def test_shutdown_bounded_by_timeout_when_provider_aclose_hangs(tmp_path: Path) -> None:
    """Regression — a hanging provider `aclose()` must not block shutdown."""
    providers = {"anthropic": _FakeProvider(aclose_sleep=0.3)}
    ctx = _shutdown_ctx(
        tmp_path,
        tracer=_FakeTracerWithShutdown(),
        daemon=_FakeCollectorDaemon(),
        providers=providers,
    )
    start = asyncio.get_event_loop().time()
    report = await asyncio.wait_for(shutdown(ctx, timeout=0.02), timeout=1.0)
    elapsed = asyncio.get_event_loop().time() - start
    assert elapsed < 0.3, "shutdown() waited out the full hang instead of bounding it"
    assert "provider:anthropic" in report.failures
    assert report.timed_out is True


@pytest.mark.asyncio
async def test_shutdown_recomputes_budget_across_multiple_slow_providers(
    tmp_path: Path,
) -> None:
    """Regression guard — the per-provider shutdown budget must shrink across
    iterations, not stay pinned at the pre-loop value. Previously `remaining`
    was computed once before the provider loop, so N slow providers each got
    re-allotted the SAME stale budget instead of what was actually left —
    each provider here individually finishes within a single provider's
    worth of budget, so under the bug all 3 complete successfully (no
    per-provider timeout failure) but the AGGREGATE elapsed time triples;
    with the fix, only the first provider gets its full slice and the rest
    are bounded by what's actually left (out-of-family Codex [P2])."""
    providers = {
        "anthropic": _FakeProvider(aclose_sleep=0.15),
        "openai": _FakeProvider(aclose_sleep=0.15),
        "ollama": _FakeProvider(aclose_sleep=0.15),
    }
    ctx = _shutdown_ctx(
        tmp_path,
        tracer=_FakeTracerWithShutdown(),
        daemon=_FakeCollectorDaemon(),
        providers=providers,
    )
    start = asyncio.get_event_loop().time()
    await asyncio.wait_for(shutdown(ctx, timeout=0.3), timeout=2.0)
    elapsed = asyncio.get_event_loop().time() - start
    assert elapsed < 0.38, (
        f"shutdown() took {elapsed:.3f}s across 3x 0.15s-slow providers with a "
        "0.3s overall budget — a stale re-allotted budget lets every provider "
        "use its full 0.15s (~0.45s total) instead of the aggregate shrinking "
        "toward the 0.3s deadline (~0.3s total)"
    )


@pytest.mark.asyncio
async def test_shutdown_bounded_by_timeout_when_mcp_host_shutdown_hangs(tmp_path: Path) -> None:
    """Regression — a hanging MCP client host `shutdown()` must not block
    shutdown."""
    host = _FakeMcpHost(shutdown_sleep=0.3)
    ctx = _shutdown_ctx(
        tmp_path,
        tracer=_FakeTracerWithShutdown(),
        daemon=_FakeCollectorDaemon(),
        providers={},
    )
    ctx.mcp_client_hosts = {"server-a": host}  # type: ignore[attr-defined]
    start = asyncio.get_event_loop().time()
    report = await asyncio.wait_for(shutdown(ctx, timeout=0.02), timeout=1.0)
    elapsed = asyncio.get_event_loop().time() - start
    assert elapsed < 0.3, "shutdown() waited out the full hang instead of bounding it"
    assert "mcp_client_host" in report.failures
    assert report.timed_out is True


def test_shutdown_timeout_is_timeout_subclass() -> None:
    assert issubclass(ShutdownTimeout, TimeoutError)


def test_already_shutdown_is_exception_subclass() -> None:
    assert issubclass(AlreadyShutDown, Exception)
    assert not issubclass(AlreadyShutDown, NotImplementedError)


def test_shutdown_package_root_re_export() -> None:
    import harness_runtime

    assert harness_runtime.shutdown is shutdown
    assert harness_runtime.ShutdownReport is ShutdownReport
    assert harness_runtime.ShutdownTimeout is ShutdownTimeout
    assert harness_runtime.AlreadyShutDown is AlreadyShutDown


@pytest.mark.asyncio
async def test_flush_observability_fsyncs_audit_sidecar_when_present(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """B-47 PR B1 (codex round-4) — the item-(e) sidecar is a SECOND durable
    file the ledger fsync does not touch; a clean shutdown must flush it too
    or a power loss keeps the IS ref and loses the signature."""
    ledger_path = tmp_path / "state.jsonl"
    ledger_path.write_text("entry-1\n")
    sidecar_path = tmp_path / "audit-entries.jsonl"
    sidecar_path.write_text('{"tenant_tag":"_single","entry":{}}\n')

    fsynced_inodes: list[int] = []
    real_fsync = os.fsync

    def _spy_fsync(fd: int) -> None:
        fsynced_inodes.append(os.fstat(fd).st_ino)
        real_fsync(fd)

    monkeypatch.setattr(os, "fsync", _spy_fsync)
    tracer = _FakeTracerProvider(returns=True)
    ctx = _ctx_with(tmp_path, tracer=tracer, ledger_path=ledger_path)
    ctx.audit_writer = SimpleNamespace(sidecar_path=sidecar_path)

    report = await flush_observability(ctx)

    assert report.failures == ()
    # BOTH files flushed, sidecar FIRST (mirrors sidecar-first writes —
    # power loss between the fsyncs must not leave a flushed ref whose
    # signature was still buffered).
    assert fsynced_inodes == [
        os.stat(sidecar_path).st_ino,
        os.stat(sidecar_path.parent).st_ino,  # directory-entry durability
        os.stat(ledger_path).st_ino,
    ]


@pytest.mark.asyncio
async def test_flush_records_failure_for_fifo_sidecar_without_hanging(tmp_path: Path) -> None:
    """Codex round-35 (PR B1) — a pre-created FIFO at the sidecar path made
    shutdown's blocking O_RDONLY open hang the entire flush. The open is now
    non-blocking + regular-file-checked: the flush completes and records an
    audit_sidecar failure instead of hanging."""
    ledger_path = tmp_path / "state.jsonl"
    ledger_path.write_text("entry-1\n")
    fifo_path = tmp_path / "audit-entries.jsonl"
    os.mkfifo(fifo_path)

    tracer = _FakeTracerProvider(returns=True)
    ctx = _ctx_with(tmp_path, tracer=tracer, ledger_path=ledger_path)
    ctx.audit_writer = SimpleNamespace(sidecar_path=fifo_path)

    report = await flush_observability(ctx)
    assert "audit_sidecar" in report.failures


@pytest.mark.asyncio
async def test_flush_observability_absent_sidecar_is_clean_noop(tmp_path: Path) -> None:
    """No sidecar (nothing ever appended) and no audit_writer attribute are
    both clean no-ops — never a flush failure. Deletion-after-use (IS refs
    exist, file missing — codex round-43) IS a failure."""
    tracer = _FakeTracerProvider(returns=True)
    ctx = _ctx_with(tmp_path, tracer=tracer)

    report = await flush_observability(ctx)
    assert report.failures == ()

    ctx.audit_writer = SimpleNamespace(
        sidecar_path=tmp_path / "never-created.jsonl",
        sidecar_expected=lambda: False,  # genuine first use
    )
    report = await flush_observability(ctx)
    assert report.failures == ()

    ctx.audit_writer = SimpleNamespace(
        sidecar_path=tmp_path / "deleted-after-use.jsonl",
        sidecar_expected=lambda: True,  # IS refs exist, file gone
    )
    report = await flush_observability(ctx)
    assert "audit_sidecar" in report.failures


@pytest.mark.asyncio
async def test_flush_first_ever_append_race_not_reported_as_loss(tmp_path: Path) -> None:
    """Merge-gate round-1 concurrency lens (B-47 item (k)) — the flush
    guard's exists()-then-refs order recorded a spurious audit_sidecar loss
    failure when the deployment's FIRST-EVER audit append landed file+ref
    between the two samples. Refs are sampled first now."""
    sidecar_path = tmp_path / "audit-entries.jsonl"

    def _expected_and_first_append_lands() -> bool:
        # Simulate the racing first append: by the time the refs predicate
        # answers True, the sidecar file exists (sidecar-first ordering).
        sidecar_path.write_text('{"tenant_tag":"_single","entry":{}}\n')
        return True

    tracer = _FakeTracerProvider(returns=True)
    ctx = _ctx_with(tmp_path, tracer=tracer)
    ctx.audit_writer = SimpleNamespace(
        sidecar_path=sidecar_path,
        sidecar_expected=_expected_and_first_append_lands,
    )

    report = await flush_observability(ctx, timeout_millis=5_000)
    assert "audit_sidecar" not in report.failures


@pytest.mark.asyncio
async def test_sidecar_timeout_sets_timed_out_independently(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """B-47 item (k) — the sidecar surface's own TimeoutError branch must set
    timed_out; in the shared-stall witnesses the ledger surface also times
    out and masks a deleted sidecar-side flag. Here the ledger surface fails
    NON-timeout (missing file), so timed_out can only come from the sidecar
    branch."""
    import time as time_module

    sidecar_path = tmp_path / "audit-entries.jsonl"
    sidecar_path.write_text('{"tenant_tag":"_single","entry":{}}\n')
    sidecar_ino = os.stat(sidecar_path).st_ino
    real_fsync = os.fsync

    def _stall_sidecar_only(fd: int) -> None:
        if os.fstat(fd).st_ino == sidecar_ino:
            time_module.sleep(1.5)
        else:
            real_fsync(fd)

    monkeypatch.setattr(os, "fsync", _stall_sidecar_only)
    tracer = _FakeTracerProvider(returns=True)
    # NO ledger_writer attribute at all: that surface fails with an
    # AttributeError through the generic except (which never sets
    # timed_out), and the stalled sidecar consumes the whole shared budget
    # anyway — so timed_out=True can ONLY come from the sidecar branch.
    ctx = SimpleNamespace(
        tracer_provider=tracer,
        audit_writer=SimpleNamespace(
            sidecar_path=sidecar_path,
            sidecar_expected=lambda: True,
        ),
    )

    report = await flush_observability(ctx, timeout_millis=200)
    assert "audit_sidecar" in report.failures
    assert "ledger" in report.failures
    assert report.timed_out is True


@pytest.mark.asyncio
async def test_flush_with_real_audit_writer_end_to_end(tmp_path: Path) -> None:
    """B-47 item (k) — every other sidecar-flush witness fabricates the
    writer via SimpleNamespace, so renaming the REAL writer's duck-typed
    surface (sidecar_path / sidecar_expected) silently disabled the
    deletion-after-use guard without any test noticing. Wire a real
    RuntimeAuditLedgerWriter through flush_observability: clean flush while
    the sidecar exists; deleting the sidecar records the audit_sidecar
    failure through the writer's REAL first-use authority."""
    from datetime import UTC, datetime, timedelta

    from harness_core.deployment_surface import DeploymentSurface
    from harness_core.workload_class import WorkloadClass
    from harness_is.path_class_registry import PathClass
    from harness_is.path_resolver import PathResolver
    from harness_is.state_ledger_entry_schema import Actor, ActorClass
    from harness_od.audit_ledger_types import (
        AuditLedgerEntry,
        AuditPayload,
        AuditSignatureAttributes,
        SignatureAlgorithm,
        StateLedgerEntryRef,
        compute_entry_hash,
    )
    from harness_runtime.config.path_bindings import build_path_binding
    from harness_runtime.lifecycle.audit_writer import RuntimeAuditLedgerWriter
    from harness_runtime.lifecycle.state_ledger import materialize_state_ledger
    from harness_runtime.types import PathBindingConfig

    ledger = materialize_state_ledger(
        PathResolver(
            build_path_binding(
                PathBindingConfig(
                    raw_entries=(
                        {
                            "path_class": PathClass.STATE_LEDGER,
                            "workflow_class": WorkloadClass.SOFTWARE_ENGINEERING,
                            "deployment_surface": DeploymentSurface.LOCAL_DEVELOPMENT,
                            "path": str(tmp_path / "state.jsonl"),
                        },
                    ),
                )
            )
        ),
        workflow_class=WorkloadClass.SOFTWARE_ENGINEERING,
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        actor=Actor(actor_class=ActorClass.AGENT, actor_id="test-runtime"),
    )
    clock = {"now": datetime(2026, 5, 19, 12, 0, 0, tzinfo=UTC)}

    def _tick() -> datetime:
        clock["now"] = clock["now"] + timedelta(microseconds=1)
        return clock["now"]

    writer = RuntimeAuditLedgerWriter(ledger_writer=ledger, time_source=_tick)
    payload = AuditPayload(
        entry_core=StateLedgerEntryRef("entry-ref-e2e"),
        audit_namespace_attrs={"audit.actor": "e2e"},
        prior_entry_hash="0" * 64,
    )
    writer.append(
        "tenant-A",
        AuditLedgerEntry(
            payload=payload,
            signature_attrs=AuditSignatureAttributes(
                audit_signature_value="sig:e2e",
                audit_signature_algorithm=SignatureAlgorithm.ED25519,
                audit_signature_key_id="test-key",
                audit_signature_key_period="2026-Q2",
            ),
            entry_hash=compute_entry_hash(payload),
        ),
    )

    tracer = _FakeTracerProvider(returns=True)
    # NOT _ctx_with: its `path.write_text("")` convenience would TRUNCATE the
    # real ledger, wiping the IS refs the guard consults.
    ctx = SimpleNamespace(tracer_provider=tracer, ledger_writer=ledger, audit_writer=writer)

    clean = await flush_observability(ctx, timeout_millis=5_000)
    assert clean.failures == ()
    assert clean.ledger_fsynced is True

    writer.sidecar_path.unlink()
    lossy = await flush_observability(ctx, timeout_millis=5_000)
    assert "audit_sidecar" in lossy.failures


@pytest.mark.asyncio
async def test_flush_bounded_when_refs_scan_stalls(tmp_path: Path) -> None:
    """Codex round-3 P2 (B-47 PR B2a) — `sidecar_expected()` deserializes
    the ENTIRE IS ledger; run on the event loop it blocked shutdown outside
    every bound. The whole guard (refs scan + exists + fsync) now runs in
    the bounded worker."""
    import time as time_module

    sidecar_path = tmp_path / "audit-entries.jsonl"
    sidecar_path.write_text('{"tenant_tag":"_single","entry":{}}\n')

    def _slow_refs_scan() -> bool:
        time_module.sleep(1.5)
        return True

    tracer = _FakeTracerProvider(returns=True)
    ctx = _ctx_with(tmp_path, tracer=tracer)
    ctx.audit_writer = SimpleNamespace(
        sidecar_path=sidecar_path,
        sidecar_expected=_slow_refs_scan,
    )

    start = time_module.monotonic()
    report = await flush_observability(ctx, timeout_millis=200)
    elapsed = time_module.monotonic() - start

    assert elapsed < 1.2
    assert "audit_sidecar" in report.failures
    assert report.timed_out is True
