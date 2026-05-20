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
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from harness_runtime.shutdown import (
    FlushReport,
    FlushTimeoutError,
    flush_observability,
)
from pydantic import ValidationError

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

    assert len(to_thread_calls) == 1
    fn, args = to_thread_calls[0]
    # Bound-method identity isn't stable across attribute accesses; compare
    # by __func__ (the underlying function) instead.
    assert getattr(fn, "__func__", None) is _FakeTracerProvider.force_flush
    assert args == (1_000,)


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
