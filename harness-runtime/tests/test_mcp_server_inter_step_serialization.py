"""B-INTERSTEP — `run_workflow` inter-step single-flight serialization
(runtime spec §14.21 C-RT-29 invariant 7; Codex review r4 [P1]).

Daemon-client mode (U-RT-108) reuses ONE bootstrapped `HarnessContext` across
many `run_workflow` invocations, so its single `inter_step_output_channel` is
SHARED by every concurrent invocation. The per-run `reset()` the handler does
at each run's start would then wipe a *concurrent* run's in-flight channel
state — run B's reset/records corrupting run A's upstream reads. The fix: when
the channel is bound, the handler runs `[reset + execute]` under a per-loop
single-flight lock (`_inter_step_run_lock()`), so concurrent inter-step runs
queue instead of interleaving.

These tests exercise the REAL `_inter_step_run_lock()` + the REAL
`InterStepOutputChannel`, reproducing the handler's exact guard structure
(`guard = lock if channel else nullcontext; async with guard: reset(); …read`).
A negative control proves the lock is load-bearing — the SAME overlap WITHOUT
the lock corrupts, so the guard is not vacuous.

Scope: these cover the NORMAL-completion concurrent case (spec §14.21.5
invariant 7b). They do NOT cover the `drain_timeout_seconds` timeout-zombie
(invariant 7c) — a timed-out run's non-cancellable `asyncio.to_thread` worker
keeps recording after the lock releases, which a lock cannot fence; that
SYSTEMIC reused-ctx residual (shared by every bootstrap-ctx holder, e.g.
`cost_record_accumulator`) is the registered `B-INTERSTEP-PERRUN-ISOLATION`
follow-on, NOT asserted closed here.
"""

from __future__ import annotations

import asyncio
import contextlib
from typing import Any

import pytest
from harness_runtime.lifecycle.inter_step_output_channel import InterStepOutputChannel
from harness_runtime.lifecycle.mcp_server import _inter_step_run_lock


def test_inter_step_run_lock_is_same_object_within_a_loop() -> None:
    """Two acquisitions in one running loop resolve to the SAME lock — concurrent
    tasks on that loop genuinely contend (a fresh lock per call would serialize
    nothing)."""

    async def _probe() -> tuple[asyncio.Lock, asyncio.Lock]:
        return _inter_step_run_lock(), _inter_step_run_lock()

    a, b = asyncio.run(_probe())
    assert a is b


def test_inter_step_run_lock_is_loop_safe_across_separate_runs() -> None:
    """A single module-level `asyncio.Lock` binds to the first loop that awaits
    it and raises "bound to a different event loop" under a later `asyncio.run`.
    The per-loop keying must survive two independent loops without raising."""

    async def _acquire_and_release() -> None:
        lock = _inter_step_run_lock()
        async with lock:
            await asyncio.sleep(0)

    asyncio.run(_acquire_and_release())
    # Second independent loop — would raise RuntimeError("bound to a different
    # event loop") if the lock were a single shared module-level object.
    asyncio.run(_acquire_and_release())


async def _run_under_guard(
    channel: InterStepOutputChannel,
    *,
    guarded: bool,
    token: str,
) -> Any:
    """Faithful reproduction of the `run_workflow` handler's inter-step section:

        guard = _inter_step_run_lock() if channel is not None else nullcontext()
        async with guard:
            channel.reset()                 # per-run boundary
            channel.record(...)             # a step completes (driver records)
            await <execute yields>          # `asyncio.to_thread(_execute_workflow)`
            return channel.most_recent_output()   # a later dispatch reads upstream

    `guarded=False` is the negative control (channel present, but `nullcontext`),
    proving the lock — not some accidental scheduling — is what prevents the
    cross-run wipe.
    """
    guard: contextlib.AbstractAsyncContextManager[Any] = (
        _inter_step_run_lock() if guarded else contextlib.nullcontext()
    )
    async with guard:
        channel.reset()
        channel.record(token, {"owner": token})
        # Yield mid-run so a concurrent run gets a scheduling opportunity to
        # interleave its own reset/record (the exact corruption window).
        await asyncio.sleep(0)
        return channel.most_recent_output()


@pytest.mark.asyncio
async def test_guard_serializes_overlapping_runs_each_sees_only_its_own() -> None:
    """Two overlapping inter-step runs SHARE one channel (daemon-client reuse).
    Under the single-flight guard each run reads back ONLY its own recorded
    output — the concurrent run cannot reset/overwrite mid-flight."""
    shared = InterStepOutputChannel()
    results = await asyncio.gather(
        _run_under_guard(shared, guarded=True, token="run-A"),
        _run_under_guard(shared, guarded=True, token="run-B"),
    )
    assert results[0] == {"owner": "run-A"}
    assert results[1] == {"owner": "run-B"}


@pytest.mark.asyncio
async def test_negative_control_unguarded_overlap_corrupts() -> None:
    """The load-bearing control: WITHOUT the guard, the same overlap on the
    shared channel corrupts — at least one run reads the OTHER run's output
    (the bug Codex r4 flagged). This proves the guard in the passing test above
    is doing real work, not riding on incidental scheduling."""
    shared = InterStepOutputChannel()
    results = await asyncio.gather(
        _run_under_guard(shared, guarded=False, token="run-A"),
        _run_under_guard(shared, guarded=False, token="run-B"),
    )
    # The first-scheduled run records its token, yields, the second-scheduled
    # run then resets + records its own token; when the first resumes its read
    # sees the second's output — cross-run leak.
    assert {results[0]["owner"], results[1]["owner"]} == {"run-B"}, (
        f"expected the unguarded overlap to corrupt to a single (latest) owner, "
        f"got {results!r} — if this no longer corrupts, the serialization test "
        f"above may be vacuous (re-derive the overlap window)."
    )
