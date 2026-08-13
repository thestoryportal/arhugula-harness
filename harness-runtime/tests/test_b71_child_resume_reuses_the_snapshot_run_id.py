"""B-71 precondition-4 witness — the child resume REUSES `snapshot.run_id`.

`.harness/council-b71-hitl-external-correlation-2026-08-12/DELIVERABLE.md` §5
precondition 4 asks to close or explicitly scope the `entry_version` crash window. Its
scope rests on one fact the record has carried as **CITED** since v2, at §4-bis.5 and
§4-ter.4: that a resume reuses the paused child's ORIGINAL `run_id` rather than
re-deriving it (`child_workflow_runner.py:230-234`). Everything about how far the window
reaches follows from it:

- reuse ⇒ basis (B) reproduces its token on the ordinary resume path, and the window is
  the narrow mint→persist one the design already declares;
- re-derivation ⇒ the token would rotate on every resume, and the window would be
  unbounded — which is what the record says candidate (C) would have suffered.

No test covered it. Every existing child-resume witness passes `pause_snapshot_input=None`
(the CRASH-resume shape), which takes the *other* branch of the very selection at issue.
This module runs the pause-resume branch.

**How it witnesses, and what that is worth.** `_runner` selects the child run_id and
hands it to `execute_workflow`. These tests compose the real runner via
`compose_child_workflow_runner` and capture that call, so the assertion is over the value
production actually passes — not a re-implementation of the selection. All three arms of
the real expression are exercised: snapshot → `snapshot.run_id`; no snapshot + seed →
the deterministic seed; neither → a fresh uuid.

**Scope, stated:** this pins the runner's selection, which is the cited claim. It stops
at `execute_workflow`'s boundary — it does not run the child workflow, so it does not
show what the resumed run then does with that id. That downstream half is covered for
the crash-resume shape by `test_recursive_child_crash_resume_final_state_witness.py`.
"""

from __future__ import annotations

from typing import Any, cast

import pytest
from harness_cp.handoff_context import StateSummary
from harness_cp.pause_resume_protocol_types import PauseSnapshot, WorkflowPauseReason
from harness_is.state_ledger_entry_schema import Identifier
from harness_runtime.lifecycle import child_workflow_runner as _cwr

_WF = "wf-child-b71"
_ANCHOR = "0" * 64


class _Ctx:
    """Minimal parent context — the runner reads only `step_dispatchers` before it
    delegates, and `execute_workflow` is captured rather than run."""

    step_dispatchers: dict[str, Any] = {}


def _snapshot(run_id: str, workflow_id: str = _WF) -> PauseSnapshot:
    return PauseSnapshot(
        workflow_id=workflow_id,
        run_id=run_id,
        step_index=0,
        pause_reason=WorkflowPauseReason.HITL_PENDING,
        state_summary=StateSummary(
            relevant_entries=(),
            summary_text="",
            summary_hash="0" * 64,
            idempotency_key=Identifier(""),
            external_references=(),
        ),
        snapshot_hash="f" * 64,
        created_at=0,
        state_ledger_anchor=_ANCHOR,
    )


def _capture_child_run_id(
    monkeypatch: pytest.MonkeyPatch,
    *,
    pause_snapshot_input: PauseSnapshot | None,
    child_run_id_seed: str | None,
) -> str:
    """Drive the REAL runner and return the child run_id it hands to the driver."""
    seen: list[str] = []

    def _fake_execute_workflow(
        _manifest: Any, _steps: Any, child_run_id: str, _ctx: Any, **_: Any
    ) -> Any:
        seen.append(child_run_id)
        return cast(Any, object())

    monkeypatch.setattr(_cwr, "execute_workflow", _fake_execute_workflow)

    runner = _cwr.compose_child_workflow_runner(cast(Any, _Ctx()))
    runner(
        workflow_id=_WF,
        manifest_entry=cast(Any, object()),
        steps=cast(Any, ()),
        handoff_context=cast(Any, object()),
        descent=cast(Any, object()),
        default_model_binding=cast(Any, object()),
        pause_snapshot_input=pause_snapshot_input,
        child_run_id_seed=child_run_id_seed,
    )
    assert len(seen) == 1, "the runner did not reach execute_workflow exactly once"
    return seen[0]


def test_a_pause_resume_reuses_the_snapshots_own_run_id() -> None:
    """**The cited fact, executed.** Snapshot present ⇒ its `run_id` is what runs.

    This is the branch precondition 4's scope depends on, and the branch no existing
    child-resume test takes (they all pass `pause_snapshot_input=None`).
    """
    with pytest.MonkeyPatch.context() as mp:
        used = _capture_child_run_id(
            mp,
            pause_snapshot_input=_snapshot("run-child-original"),
            child_run_id_seed="a-seed-that-must-be-ignored",
        )
    assert used == "run-child-original", (
        "the resumed child did NOT reuse the paused snapshot's run_id — B-71's "
        "precondition-4 scope, and basis (B)'s stability on the ordinary resume path, "
        "both rest on this reuse"
    )


def test_the_snapshot_wins_over_the_deterministic_seed() -> None:
    """Ordering matters, not just presence.

    The seed is supplied on the same call above. If the arms were ordered the other way
    a resumed child would silently re-key onto the first-dispatch identity — the exact
    rotation the window is meant to bound.
    """
    with pytest.MonkeyPatch.context() as mp:
        used = _capture_child_run_id(
            mp,
            pause_snapshot_input=_snapshot("run-child-original"),
            child_run_id_seed="a-seed-that-must-be-ignored",
        )
    assert used != "a-seed-that-must-be-ignored"


def test_a_first_dispatch_prefers_the_deterministic_seed() -> None:
    """No snapshot + seed ⇒ the seed. (The crash-resume recoverability arm.)"""
    with pytest.MonkeyPatch.context() as mp:
        used = _capture_child_run_id(
            mp, pause_snapshot_input=None, child_run_id_seed="deterministic-seed-1"
        )
    assert used == "deterministic-seed-1"


def test_a_first_dispatch_without_a_seed_gets_a_fresh_id() -> None:
    """No snapshot, no seed ⇒ a fresh uuid — distinct on each call.

    Included so the two arms above are shown to be *selections*, not a constant.
    """
    with pytest.MonkeyPatch.context() as mp:
        first = _capture_child_run_id(mp, pause_snapshot_input=None, child_run_id_seed=None)
        second = _capture_child_run_id(mp, pause_snapshot_input=None, child_run_id_seed=None)
    assert first != second
    assert first not in {"run-child-original", "deterministic-seed-1"}
