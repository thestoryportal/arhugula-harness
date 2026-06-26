"""B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT (R-FS-1) — CP-side classifier units.

`_fence_unrecoverable_maybe_ran_indices` gains a SECOND recovery mechanism alongside the
TOOL_STEP / MANAGED_AGENTS fence-recovery: a maybe-ran SUB_AGENT_DISPATCH worker recovers by
re-dispatching its child under the deterministic child run_id (the child's own crash-resume
auto-resumes, result-faithfully). It is recoverable ONLY when the child was RECOVERABLE
({ESR,WAL} ∧ LINEAR ∧ leaf) BOTH at dispatch (`subagent_recoverable_indexes`, the marker) AND
in the RESUMED manifest (`resumed_subagent_recoverable_indexes`) — the [P1-b] dual gate (the
#746 `6930e7ef` Codex [P1]). Requiring BOTH closes the changed-manifest hole (a child edited
recoverable→non-recoverable between dispatch + resume has durable records but the re-dispatch
runs the non-recoverable child fresh → double-fire / suffix-only corruption).
"""

from __future__ import annotations

from collections.abc import Collection

from harness_cp.workflow_driver import _fence_unrecoverable_maybe_ran_indices
from harness_cp.workflow_driver_types import StepKind

_SUB = StepKind.SUB_AGENT_DISPATCH.value
_TOOL = StepKind.TOOL_STEP.value
_DECL = StepKind.DECLARATIVE_STEP.value


def _classify(
    marker: str | None,
    resumed: str | None,
    *,
    marker_recoverable: bool,
    resumed_recoverable: bool,
    branch_count: int = 2,
    marker_step_id: str | None = "s0",
    resumed_step_id: str | None = "s0",
) -> set[int]:
    """UNRECOVERABLE subset of {0} for a single maybe-ran branch at ordinal 0 with the given
    dispatch-marker + resumed kinds and the dispatch-time / resumed-manifest child recoverability.
    Empty ⟹ recoverable."""
    subagent_dispatch: Collection[int] = {0} if marker_recoverable else set()
    subagent_resumed: Collection[int] = {0} if resumed_recoverable else set()
    resumed_map: dict[int, str] = {0: resumed} if resumed is not None else {}
    resumed_sids: dict[int, str] = {0: resumed_step_id} if resumed_step_id is not None else {}
    return _fence_unrecoverable_maybe_ran_indices(
        {0},
        {0: marker},
        resumed_map,
        branch_count,
        dispatched_step_ids={0: marker_step_id},
        resumed_step_ids=resumed_sids,
        subagent_recoverable_indexes=subagent_dispatch,
        resumed_subagent_recoverable_indexes=subagent_resumed,
    )


def test_subagent_recoverable_both_dispatch_and_resumed_is_recoverable() -> None:
    """marker SUB_AGENT + resumed SUB_AGENT, child recoverable BOTH at dispatch AND resume →
    RECOVERABLE (the new capability — re-dispatch auto-resumes the recoverable child)."""
    assert _classify(_SUB, _SUB, marker_recoverable=True, resumed_recoverable=True) == set()


def test_subagent_recoverable_at_dispatch_but_not_resumed_fails_closed() -> None:
    """[P1-b] — child recoverable at DISPATCH (durable records exist) but NON-recoverable in the
    RESUMED manifest (operator edited it {ESR}→SAVE_POINT / LINEAR→fan-out / added a nested
    sub-agent) → the re-dispatch runs the non-recoverable child FRESH → double-fire / suffix-only
    corruption. The resumed-side conjunct fails it closed."""
    assert _classify(_SUB, _SUB, marker_recoverable=True, resumed_recoverable=False) == {0}


def test_subagent_recoverable_at_resumed_but_not_dispatch_fails_closed() -> None:
    """The dispatch-time marker is the at-most-once changed-manifest authority: a child
    NON-recoverable at dispatch (no durable child records to auto-resume from) but recoverable in
    the resumed manifest STILL fails closed — there is no durable prefix to reconstruct from."""
    assert _classify(_SUB, _SUB, marker_recoverable=False, resumed_recoverable=True) == {0}


def test_subagent_non_recoverable_both_fails_closed() -> None:
    """A non-recoverable child (e.g. a SAVE_POINT / fan-out / non-leaf child) at BOTH dispatch and
    resume → fail closed (the `…-SAVE-POINT-RECONCILER` / fan-out-child / nested residuals)."""
    assert _classify(_SUB, _SUB, marker_recoverable=False, resumed_recoverable=False) == {0}


def test_subagent_marker_tool_resumed_cross_kind_fails_closed() -> None:
    """A maybe-ran SUB_AGENT branch re-supplied at the same ordinal as a TOOL_STEP — even with both
    recoverable flags set — fails closed: marker SUB_AGENT ≠ resumed TOOL → the SUB_AGENT recovery
    disjunct requires both kinds be SUB_AGENT, and the TOOL disjunct requires both be TOOL."""
    assert _classify(_SUB, _TOOL, marker_recoverable=True, resumed_recoverable=True) == {0}


def test_tool_marker_subagent_resumed_cross_kind_fails_closed() -> None:
    """The reverse cross-kind swap (marker TOOL_STEP + resumed SUB_AGENT_DISPATCH) also fails
    closed."""
    assert _classify(_TOOL, _SUB, marker_recoverable=True, resumed_recoverable=True) == {0}


def test_subagent_changed_to_non_recoverable_kind_fails_closed() -> None:
    """marker SUB_AGENT + resumed DECLARATIVE (a non-recovery kind) → fail closed even with the
    recoverability flags set (the changed-kind guard; resumed must be SUB_AGENT)."""
    assert _classify(_SUB, _DECL, marker_recoverable=True, resumed_recoverable=True) == {0}


def test_subagent_recoverable_changed_step_id_fails_closed() -> None:
    """The COMMON changed-step_id guard applies to the SUB_AGENT path too: same kind + recoverable
    both, but a RENAMED step_id at this ordinal → fail closed (a different branch was re-supplied)."""
    assert _classify(
        _SUB,
        _SUB,
        marker_recoverable=True,
        resumed_recoverable=True,
        marker_step_id="s0",
        resumed_step_id="s0-renamed",
    ) == {0}


def test_subagent_recoverable_out_of_range_ordinal_fails_closed() -> None:
    """A recoverable same-kind SUB_AGENT branch whose ordinal is OUTSIDE [0, branch_count) (a
    stale / corrupt extra marker) fails closed regardless of recoverability."""
    out = _fence_unrecoverable_maybe_ran_indices(
        {3},
        {3: _SUB},
        {3: _SUB},
        2,
        dispatched_step_ids={3: "s3"},
        resumed_step_ids={3: "s3"},
        subagent_recoverable_indexes={3},
        resumed_subagent_recoverable_indexes={3},
    )
    assert out == {3}


def test_subagent_default_empty_recoverable_sets_fail_closed() -> None:
    """Back-compat: callers that DON'T pass the two new sets (the default empty frozensets) leave
    every SUB_AGENT branch fail-closed — the pre-arc behavior (a store that can't answer
    recoverability never auto-recovers a sub-agent)."""
    out = _fence_unrecoverable_maybe_ran_indices(
        {0},
        {0: _SUB},
        {0: _SUB},
        2,
        dispatched_step_ids={0: "s0"},
        resumed_step_ids={0: "s0"},
    )
    assert out == {0}
