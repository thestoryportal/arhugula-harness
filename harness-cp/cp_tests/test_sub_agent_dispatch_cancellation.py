"""Direct unit witnesses for `DispatchCancelToken` (B-48; U-RT-143).

PD-8 mutation-probed. Focused on the concurrent-`trip()` cascade-ordering
race (out-of-family Codex round-8 [P1]) — a defect in the CP-owned carrier
itself, not any of its call sites.
"""

from __future__ import annotations

import threading

import pytest
from harness_cp.sub_agent_dispatch_cancellation import DispatchCancelToken


def test_concurrent_trip_waits_for_winners_cascade_before_reporting_inflight(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Codex round-8 [P1] "complete concurrent fence cascades before
    classifying": when two callers trip the SAME token concurrently (e.g. a
    barrier cascade and a facade timeout both tripping a shared nested
    token), the LOSER's read of `_inflight_at_trip` must not race ahead of
    the WINNER's own cascade to its children.

    Reproduces the exact race: token `t` has a child `c` whose `trip()` is
    wrapped to block mid-cascade (after `t` has already set its own
    `_tripped_event` and released its lock, but before `c.trip()` — and
    therefore `t`'s bubble-up of `c`'s in-flight effect — has returned). A
    second ("loser") thread calls `t.trip()` while the winner is still
    blocked inside that wrapped call.

    Mutation probe: reverting `trip()`'s early-return path to immediately
    read+return `_inflight_at_trip` (removing the `_cascade_done_event.wait()`
    gate) makes the loser's call return `False` BEFORE the gate below is
    ever released — this test's `assert loser_result[0] is True` would then
    fail, because the loser observed a stale pre-bubble-up snapshot.
    """
    t = DispatchCancelToken()
    c = DispatchCancelToken(parent=t)
    # Hold a real in-flight effect on the child so c.trip() reports True.
    c_effect_cm = c.effect_entry()
    c_effect_cm.__enter__()

    cascade_started = threading.Event()
    proceed_gate = threading.Event()
    real_trip = DispatchCancelToken.trip

    def _patched_trip(self: DispatchCancelToken) -> bool:
        # Only the CHILD's own trip() (invoked from inside the winner's
        # cascade loop) is slowed; t.trip() itself (called by both the
        # winner and loser threads below) always runs at full speed through
        # the real implementation.
        if self is c:
            cascade_started.set()
            proceed_gate.wait(timeout=5)
        return real_trip(self)

    monkeypatch.setattr(DispatchCancelToken, "trip", _patched_trip)

    winner_result: list[bool] = []
    loser_result: list[bool] = []

    def _winner() -> None:
        winner_result.append(t.trip())

    winner_thread = threading.Thread(target=_winner)
    winner_thread.start()
    assert cascade_started.wait(timeout=5), "winner never reached the child cascade"

    # At this point t._tripped_event IS set (the winner set it before
    # releasing the lock and calling c.trip()), but the winner's cascade —
    # and therefore any bubble-up of c's in-flight effect into
    # t._inflight_at_trip — has NOT finished (blocked on proceed_gate).
    def _loser() -> None:
        loser_result.append(t.trip())

    loser_thread = threading.Thread(target=_loser)
    loser_thread.start()
    # Give the loser a real chance to take (and, on the buggy code, return
    # from) the early-return path before the gate is released.
    loser_thread.join(timeout=0.2)

    proceed_gate.set()
    winner_thread.join(timeout=5)
    loser_thread.join(timeout=5)
    c_effect_cm.__exit__(None, None, None)

    assert not winner_thread.is_alive()
    assert not loser_thread.is_alive()
    assert winner_result == [True], "the winner must observe the bubbled-up in-flight effect"
    assert loser_result == [True], (
        "the loser observed the classification before the winner's cascade "
        "bubbled up the child's in-flight effect — a false-clean race"
    )


def test_trip_is_idempotent_and_returns_the_same_value_after_cascade_completes() -> None:
    """Control: a THIRD call to `trip()` after the cascade has genuinely
    finished must return the same (correct) value immediately, not block."""
    t = DispatchCancelToken()
    c = DispatchCancelToken(parent=t)
    with c.effect_entry():
        assert t.trip() is True
    # Cascade is long done; a fresh call must return promptly.
    assert t.trip() is True
