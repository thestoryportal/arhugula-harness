"""B-FANOUT-OUTPUT-REPLAY — `_determine_fanout_resume` reconstruction unit tests.

R-FS-1 standalone arc B-FANOUT-OUTPUT-REPLAY (operator ratified A — non-attested
branch-index-keyed recovery sidecar). On a mid-fan-out crash the durable F2 ledger
is BINARY (branch terminals buffer + drain ATOMICALLY at the barrier per CP §25.12
D1.b), so the STORE is the SOLE which-branches-completed authority. These verify the
store → synthetic-resume-state reconstruction (net-add #2) in isolation:

- completed = the store's branch keys; the recovered `step_id` comes from the STORE
  (CAPTURE-time identity) so the existing strategy material-diff guard fails closed on
  a changed body;
- integrity = present-vs-readable: a present-but-unreadable branch (or a missing
  orchestrator when workers completed) FAILS CLOSED, never silently re-dispatched.

The strategy-side reuse (threading the reconstructed state through the existing pause-
resume path) is covered by the net-add #3 wiring tests; this isolates the helper.
"""

from __future__ import annotations

import pytest
from harness_core import StepID
from harness_cp.pause_resume_protocol_types import (
    FanOutResumeState,
    PeerFanOutResumeState,
)
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import (
    _determine_fanout_resume,
    _FanOutStoreCorruptError,
    _FanOutStoreTimeoutAmbiguousError,
)
from harness_cp.workflow_driver_types import StepKind, WorkflowStep

_RUN_KEY = "run-idem-key-fanout"


def _steps(n: int) -> list[WorkflowStep]:
    """`n` declarative steps — only `len(steps)` is read by the helper."""
    return [
        WorkflowStep(
            step_id=StepID(f"step-{i}"),
            step_kind=StepKind.DECLARATIVE_STEP,
            step_payload={"i": i},
        )
        for i in range(n)
    ]


class _FakeStore:
    """A minimal `engine_output_store`-shaped stub (the driver duck-types it)."""

    def __init__(
        self,
        *,
        branches: dict[int, tuple[str, dict[str, object] | None]],
        orchestrator: tuple[str, dict[str, object]] | None = None,
        corrupt_branches: tuple[int, ...] = (),
        orchestrator_corrupt: bool = False,
        dispositions: dict[int, str] | None = None,
        cardinality: int | None = None,
    ) -> None:
        self._branches = dict(branches)
        self._orchestrator = orchestrator
        self._corrupt = set(corrupt_branches)
        self._orchestrator_corrupt = orchestrator_corrupt
        self._cardinality = cardinality
        # Per-branch terminal disposition (default "completed"); set "timed_out" or a
        # "completed" with a None output to exercise the disposition-class recovery.
        self._dispositions = dict(dispositions) if dispositions else {}

    def read_branch_records(
        self, run_key: str
    ) -> dict[int, tuple[str, str, dict[str, object] | None]]:
        return {
            bi: (sid, self._dispositions.get(bi, "completed"), out)
            for bi, (sid, out) in self._branches.items()
        }

    def present_branch_indexes(self, run_key: str) -> set[int]:
        return set(self._branches) | self._corrupt

    def read_orchestrator_output(self, run_key: str) -> tuple[str, dict[str, object]] | None:
        return None if self._orchestrator_corrupt else self._orchestrator

    def orchestrator_present(self, run_key: str) -> bool:
        return self._orchestrator_corrupt or self._orchestrator is not None

    def read_fanout_cardinality(self, run_key: str) -> int | None:
        return self._cardinality


def test_parallelization_reconstructs_peer_resume_from_store() -> None:
    """2 of 3 peer branches completed → a PeerFanOutResumeState with branch_count=3;
    the missing ordinal (1) is absent → left re-dispatchable."""
    store = _FakeStore(branches={0: ("step-0", {"o": 0}), 2: ("step-2", {"o": 2})})
    result = _determine_fanout_resume(store, _RUN_KEY, _steps(3), TopologyPattern.PARALLELIZATION)
    assert isinstance(result, PeerFanOutResumeState)
    assert result.branch_count == 3
    assert {b.branch_index for b in result.branches} == {0, 2}
    assert all(b.terminal_status == "completed" for b in result.branches)
    by_index = {b.branch_index: b for b in result.branches}
    assert by_index[0].output == {"o": 0}
    assert by_index[2].step_id == "step-2"


def test_orchestrator_reconstructs_fan_out_resume_with_orchestrator_output() -> None:
    """2 of 3 workers + the orchestrator completed → a FanOutResumeState carrying the
    recovered orchestrator output + worker_count=3 (steps[1:])."""
    store = _FakeStore(
        branches={0: ("w-0", {"o": 0}), 1: ("w-1", {"o": 1})},
        orchestrator=("orch", {"plan": "delegate"}),
        cardinality=4,
    )
    result = _determine_fanout_resume(
        store, _RUN_KEY, _steps(4), TopologyPattern.ORCHESTRATOR_WORKERS
    )
    assert isinstance(result, FanOutResumeState)
    assert result.worker_count == 3  # len(steps) - 1
    assert result.orchestrator_output == {"plan": "delegate"}
    assert result.orchestrator_step_id == "orch"
    assert {b.branch_index for b in result.branches} == {0, 1}
    assert result.paused_child_branches == ()  # a crash has no paused children


def test_recovered_step_id_comes_from_store_not_current_body() -> None:
    """The store is the CAPTURE-time identity authority: the reconstructed branch
    step_id is the STORE's value (so the strategy material-diff guard can later detect
    a changed body), NOT re-derived from the current steps."""
    store = _FakeStore(branches={0: ("captured-step-id", {"o": 0})})
    result = _determine_fanout_resume(store, _RUN_KEY, _steps(1), TopologyPattern.PARALLELIZATION)
    assert isinstance(result, PeerFanOutResumeState)
    assert result.branches[0].step_id == "captured-step-id"


def test_no_completed_branch_returns_none_fresh_run() -> None:
    """No completed branch in the store → None (the strategy runs fresh, byte-identical)."""
    store = _FakeStore(branches={})
    assert (
        _determine_fanout_resume(store, _RUN_KEY, _steps(3), TopologyPattern.PARALLELIZATION)
        is None
    )


def test_present_but_unreadable_branch_fails_closed() -> None:
    """A branch file present but unreadable (corruption / tamper) → fail closed, NOT a
    silent re-dispatch (which would mask the corruption + re-fire a landed effect)."""
    store = _FakeStore(branches={0: ("w-0", {"o": 0})}, corrupt_branches=(1,))
    with pytest.raises(_FanOutStoreCorruptError, match="present but unreadable"):
        _determine_fanout_resume(store, _RUN_KEY, _steps(3), TopologyPattern.PARALLELIZATION)


def test_orchestrator_missing_when_workers_completed_fails_closed() -> None:
    """Workers completed but the orchestrator output is absent — an inconsistent store
    (the orchestrator completes before any worker dispatches) → fail closed."""
    store = _FakeStore(branches={0: ("w-0", {"o": 0})}, orchestrator=None)
    with pytest.raises(_FanOutStoreCorruptError, match="absent but workers completed"):
        _determine_fanout_resume(store, _RUN_KEY, _steps(3), TopologyPattern.ORCHESTRATOR_WORKERS)


def test_orchestrator_unreadable_when_workers_completed_fails_closed() -> None:
    """The orchestrator file present-but-unreadable is distinguished from absent in the
    fail-closed diagnostic (consumes the `orchestrator_present` discriminator)."""
    store = _FakeStore(branches={0: ("w-0", {"o": 0})}, orchestrator_corrupt=True)
    with pytest.raises(_FanOutStoreCorruptError, match="present but unreadable"):
        _determine_fanout_resume(store, _RUN_KEY, _steps(3), TopologyPattern.ORCHESTRATOR_WORKERS)


def test_orchestrator_recovered_with_zero_workers_completed() -> None:
    """A crash after the orchestrator (`steps[0]`) captured but BEFORE any worker
    completes must STILL recover the orchestrator (it dispatches first) — else
    re-dispatching `steps[0]` double-fires its effect (out-of-family Codex [P1]). The
    resume state carries an EMPTY branch set → every worker re-dispatches fresh."""
    store = _FakeStore(branches={}, orchestrator=("orch", {"plan": "delegate"}), cardinality=4)
    result = _determine_fanout_resume(
        store, _RUN_KEY, _steps(4), TopologyPattern.ORCHESTRATOR_WORKERS
    )
    assert isinstance(result, FanOutResumeState)
    assert result.branches == ()  # zero workers completed
    assert result.orchestrator_output == {"plan": "delegate"}
    assert result.worker_count == 3  # len(steps) - 1


def test_orchestrator_unreadable_with_zero_workers_fails_closed() -> None:
    """A present-but-unreadable orchestrator file fails closed EVEN with zero workers
    completed (corruption / tamper is never silently treated as a fresh run)."""
    store = _FakeStore(branches={}, orchestrator_corrupt=True)
    with pytest.raises(_FanOutStoreCorruptError, match="present but unreadable"):
        _determine_fanout_resume(store, _RUN_KEY, _steps(3), TopologyPattern.ORCHESTRATOR_WORKERS)


def test_orchestrator_absent_with_zero_workers_returns_none_fresh() -> None:
    """Nothing captured (orchestrator absent + no worker) → None (fresh run)."""
    store = _FakeStore(branches={}, orchestrator=None)
    assert (
        _determine_fanout_resume(store, _RUN_KEY, _steps(3), TopologyPattern.ORCHESTRATOR_WORKERS)
        is None
    )


# --- disposition class (the keystone): completed-with-output / completed-no-output /
#     timed-out, across topologies ------------------------------------------------------
def test_timed_out_branch_fails_closed() -> None:
    """A TIMED_OUT branch is irreducibly ambiguous (a deadline-cut in-flight dispatch may
    or may not have landed) → crash-resume FAILS CLOSED, never a silent re-dispatch."""
    store = _FakeStore(branches={0: ("w0", {"o": 0})}, dispositions={0: "timed_out"})
    with pytest.raises(_FanOutStoreTimeoutAmbiguousError, match="timed out"):
        _determine_fanout_resume(store, _RUN_KEY, _steps(3), TopologyPattern.PARALLELIZATION)


def test_errored_no_output_branch_recovered_as_terminal() -> None:
    """A COMPLETED branch with NO output (ran-and-errored, effect LANDED) is recovered as
    TERMINAL (output None → not re-dispatched, not folded), never re-firing the effect."""
    store = _FakeStore(
        branches={0: ("w0", {"o": 0}), 1: ("w1", None)},
        dispositions={1: "completed"},
    )
    result = _determine_fanout_resume(store, _RUN_KEY, _steps(3), TopologyPattern.PARALLELIZATION)
    assert isinstance(result, PeerFanOutResumeState)
    by_index = {b.branch_index: b for b in result.branches}
    assert by_index[1].terminal_status == "completed"
    assert by_index[1].output is None  # errored: terminal, recovered, NOT re-dispatched


def test_parallelization_with_orchestrator_record_fails_closed_changed_topology() -> None:
    """A PARALLELIZATION manifest resuming a run whose store holds an ORCHESTRATOR record
    is a changed-topology resume (the run key does not bind topology) → fail closed rather
    than reinterpret worker records as peers or drop the orchestrator effect (Codex [P2])."""
    store = _FakeStore(branches={0: ("w0", {"o": 0})}, orchestrator=("orch", {"plan": "x"}))
    with pytest.raises(_FanOutStoreCorruptError, match="topology mismatch"):
        _determine_fanout_resume(store, _RUN_KEY, _steps(3), TopologyPattern.PARALLELIZATION)


def test_changed_cardinality_fails_closed() -> None:
    """A store that recorded a 3-branch fan-out, resumed with a 1-branch manifest (a changed
    body the surviving-prefix material-diff cannot catch), FAILS CLOSED rather than silently
    dropping the original in-flight branches (out-of-family Codex [P2])."""
    store = _FakeStore(branches={0: ("w0", {"o": 0})}, cardinality=3)
    with pytest.raises(_FanOutStoreCorruptError, match="cardinality mismatch"):
        _determine_fanout_resume(store, _RUN_KEY, _steps(1), TopologyPattern.PARALLELIZATION)


def test_orchestrator_record_without_cardinality_marker_fails_closed() -> None:
    """The orchestrator record is fsynced BEFORE the cardinality marker — a crash between
    them leaves an orchestrator record with NO cardinality, so a changed worker set could
    reuse the old orchestrator output undetected. Fail closed (out-of-family Codex [P2])."""
    store = _FakeStore(
        branches={0: ("w-0", {"o": 0})},
        orchestrator=("orch", {"plan": "x"}),
        cardinality=None,
    )
    with pytest.raises(_FanOutStoreCorruptError, match="cardinality marker is absent"):
        _determine_fanout_resume(store, _RUN_KEY, _steps(3), TopologyPattern.ORCHESTRATOR_WORKERS)
