"""B-104 Task 5a F2: the lease capability is store-owned, and store operations borrow it.

Deterministic, provider-free witnesses of the two independent Codex counterexamples (a forged
subclass; a public `close` racing admission) and the Opus minimum scenarios. The schedule of
each race is fixed by a hook on the store's own `parse_claim` call, which runs inside the
borrowed durable window of `mark_started` and of parent-carried `claim`.
"""

from __future__ import annotations

import copy
import os
import pickle
import sys
import threading
from collections.abc import Callable
from typing import Any

import harness_runtime.lifecycle.resume_claim_store as store_module
import pytest
from harness_core import JournalRecordRef
from harness_runtime.lifecycle.resume_claim_store import (
    ClaimRefusedError,
    LeaseCapability,
    ParentCarriedAdmission,
    StartedClaim,
    started_frame,
)

from .test_b104_resume_claim_started import (
    Family,
    _claim_bytes,  # pyright: ignore[reportPrivateUsage]
    _held,  # pyright: ignore[reportPrivateUsage]
    _started_parent,  # pyright: ignore[reportPrivateUsage]
)
from .test_b104_resume_claim_started import family as family
from .test_b104_resume_claim_started import placed as placed
from .test_state_placement import world  # noqa: F401  (fixture: scratch dir with no .git above)

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="claim leases require POSIX flock")

WINDOW_SECONDS = 0.5
"""How long a hook watches a concurrent `close()`: long enough that an unserialised close, which
returns in microseconds, has certainly returned, and never a condition the code waits on."""


# --- unforgeable: minted by the store, never copied, never subclassed --------------------------


def test_a_lease_capability_cannot_be_subclassed() -> None:
    with pytest.raises(TypeError):
        type("Forged", (LeaseCapability,), {})  # subclass creation itself must fail


def test_a_lease_capability_cannot_be_constructed_outside_the_store() -> None:
    with pytest.raises(TypeError):
        LeaseCapability(object(), 0)  # pyright: ignore
    with pytest.raises(TypeError):
        LeaseCapability.__new__(LeaseCapability, object(), 0)  # pyright: ignore


@pytest.mark.parametrize("duplicate", [copy.copy, copy.deepcopy, pickle.dumps])
def test_a_lease_capability_cannot_be_copied_or_pickled(
    placed: Any, duplicate: Callable[..., Any]
) -> None:
    _store, _ref, held = _held(placed)
    with held:
        with pytest.raises(TypeError):
            duplicate(held.lease)


def test_no_public_lease_descriptor_exists_on_a_capability_or_either_claim(placed: Any) -> None:
    store, _ref, held = _held(placed)
    with held:
        started = store.mark_started(held)
        for owner in (held.lease, held, started):
            assert not hasattr(owner, "fd") and not hasattr(owner, "lease_fd")
        assert started.closed is False and held.closed is False
    assert held.closed is True and started.closed is True


def test_a_stand_in_for_the_capability_is_refused_as_a_lease(placed: Any) -> None:
    class StandIn:
        closed = False

        def close(self) -> None:
            return None

    store, ref, held = _held(placed)
    claimed = _claim_bytes(store, ref)
    stand_in: Any = StandIn()
    forged = store_module.HeldClaim(held.token, held.record_ref, stand_in)

    with held, pytest.raises(ClaimRefusedError):
        store.mark_started(forged)

    assert _claim_bytes(store, ref) == claimed


# --- Codex counterexample 2: `close` during the durable window ---------------------------------


def _hook_parse_claim(
    monkeypatch: pytest.MonkeyPatch,
    ref: JournalRecordRef,
    nth: int,
    action: Callable[[], None],
) -> None:
    """Run `action` inside the nth `parse_claim` of `ref`, i.e. inside the borrowed window."""
    original = store_module.parse_claim
    calls = 0

    def hooked(data: bytes, record_ref: JournalRecordRef) -> Any:
        nonlocal calls
        if record_ref == ref:
            calls += 1
            if calls == nth:
                action()
        return original(data, record_ref)

    monkeypatch.setattr(store_module, "parse_claim", hooked)


def test_closing_from_inside_mark_started_raises_and_appends_nothing(
    placed: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    store, ref, held = _held(placed)
    claimed = _claim_bytes(store, ref)
    _hook_parse_claim(monkeypatch, ref, 1, held.close)  # the borrowing thread closes

    with pytest.raises(RuntimeError):
        store.mark_started(held)
    monkeypatch.undo()

    assert _claim_bytes(store, ref) == claimed and held.closed is False
    with held:  # the capability is intact: the failed close changed nothing
        store.mark_started(held)


@pytest.mark.parametrize("nth", [1, 2])
def test_closing_the_parent_from_inside_child_admission_raises_and_creates_no_child(
    placed: Any, family: Family, monkeypatch: pytest.MonkeyPatch, nth: int
) -> None:
    store = placed.store()
    parent = _started_parent(store, family)
    child_ref = family.child_refs[0]
    _hook_parse_claim(monkeypatch, family.parent_ref, nth, parent.close)

    with pytest.raises(RuntimeError):
        store.claim(child_ref, ParentCarriedAdmission(parent))
    monkeypatch.undo()

    assert not store.paths_for(child_ref).claim.exists() and parent.closed is False
    parent.close()


class _ConcurrentClose:
    """`close()` on another thread, started inside the hook, and how it behaved meanwhile."""

    def __init__(self, target: Any) -> None:
        self.returned = threading.Event()
        self.failure: list[BaseException] = []
        self._thread = threading.Thread(target=self._run, args=(target,))
        self.returned_inside_window = False

    def _run(self, target: Any) -> None:
        try:
            target.close()
        except BaseException as exc:  # reported to the test thread
            self.failure.append(exc)
        finally:
            self.returned.set()

    def start_and_observe(self) -> None:
        self._thread.start()
        self.returned_inside_window = self.returned.wait(WINDOW_SECONDS)

    def finish(self) -> None:
        self._thread.join(10)
        assert not self._thread.is_alive() and self.failure == []


def test_another_threads_close_waits_for_mark_started_to_finish(
    placed: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    store, ref, held = _held(placed)
    claimed = _claim_bytes(store, ref)
    closer = _ConcurrentClose(held)
    _hook_parse_claim(monkeypatch, ref, 1, closer.start_and_observe)

    started = store.mark_started(held)
    monkeypatch.undo()
    closer.finish()

    assert closer.returned_inside_window is False  # close was held back by the borrow
    assert isinstance(started, StartedClaim)
    assert _claim_bytes(store, ref) == claimed + started_frame(held)  # the start completed
    assert held.closed is True  # and the close ran once the operation ended


def test_another_threads_close_of_the_parent_waits_for_child_admission_to_finish(
    placed: Any, family: Family, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = placed.store()
    parent = _started_parent(store, family)
    child_ref = family.child_refs[0]
    closer = _ConcurrentClose(parent)
    _hook_parse_claim(monkeypatch, family.parent_ref, 2, closer.start_and_observe)

    child = store.claim(child_ref, ParentCarriedAdmission(parent))
    monkeypatch.undo()
    closer.finish()

    assert closer.returned_inside_window is False
    assert child.record_ref == child_ref and store.paths_for(child_ref).claim.exists()
    assert parent.closed is True
    child.close()


def test_two_threads_starting_one_claim_append_exactly_one_started_frame(
    placed: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    store, ref, held = _held(placed)
    claimed = _claim_bytes(store, ref)
    outcomes: list[object] = []
    second_done = threading.Event()

    def second() -> None:
        try:
            outcomes.append(store.mark_started(held))
        except ClaimRefusedError as exc:
            outcomes.append(exc)
        finally:
            second_done.set()

    thread = threading.Thread(target=second)
    seen_inside_window: list[bool] = []

    def start_second_and_watch() -> None:
        thread.start()
        seen_inside_window.append(second_done.wait(WINDOW_SECONDS))

    _hook_parse_claim(monkeypatch, ref, 1, start_second_and_watch)
    first = store.mark_started(held)
    monkeypatch.undo()
    thread.join(10)

    assert seen_inside_window == [False]  # the second operation waited for the first's borrow
    assert isinstance(first, StartedClaim)
    assert len(outcomes) == 1 and isinstance(outcomes[0], ClaimRefusedError)
    assert _claim_bytes(store, ref) == claimed + started_frame(held)  # one started frame
    held.close()


# --- a forked copy of the capability is not the holder -----------------------------------------


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_a_capability_inherited_by_a_forked_child_is_refused_there(placed: Any) -> None:
    store, ref, held = _held(placed)
    claimed = _claim_bytes(store, ref)
    pid = os.fork()
    if pid == 0:  # the child: same descriptor, different process
        try:
            store.mark_started(held)
            os._exit(3)
        except ClaimRefusedError:
            os._exit(0)
        except BaseException:
            os._exit(4)
    _, status = os.waitpid(pid, 0)

    assert os.waitstatus_to_exitcode(status) == 0
    assert _claim_bytes(store, ref) == claimed  # the child appended nothing
    store.mark_started(held)  # the real holder is unaffected
    held.close()
