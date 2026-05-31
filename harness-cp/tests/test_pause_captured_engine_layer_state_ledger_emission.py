"""Tests for U-CP-78 emit_pause_captured_state_ledger_entry engine-layer composer.

CP spec v1.26 §16.5 row U-CP-49.
"""

from __future__ import annotations

import asyncio
import hashlib
from typing import Any

from harness_cp.cp_shared_types import ActorIdentity
from harness_cp.handoff_context import StateSummary
from harness_cp.pause_resume_protocol import emit_pause_captured_state_ledger_entry
from harness_cp.pause_resume_protocol_types import (
    PauseSnapshot,
    WorkflowPauseReason,
)
from harness_cp.state_ledger_canonicalization import _canonicalize_outcome_bytes
from harness_is.state_ledger_entry_schema import ActorClass, Identifier
from harness_is.state_ledger_write import EntryPayload, WriteResult

_PROCEDURAL_TIER_SNAPSHOT_FIXTURE = Identifier("a" * 64)


def _pt_resolver() -> Identifier:
    """CP spec v1.30 §1.4: zero-arg resolver closure returning the fixture."""
    return _PROCEDURAL_TIER_SNAPSHOT_FIXTURE


class _CapturingLedgerWriter:
    """Async ledger_writer stub capturing payloads for verification."""

    def __init__(self, returns: WriteResult = WriteResult.APPENDED) -> None:
        self.captured: list[EntryPayload] = []
        self._returns = returns

    async def __call__(self, payload: EntryPayload) -> WriteResult:
        self.captured.append(payload)
        return self._returns


def _state_summary(*, version: str = "v1") -> StateSummary:
    return StateSummary(
        relevant_entries=(),
        summary_text=version,
        summary_hash=hashlib.sha256(version.encode()).hexdigest(),
        idempotency_key=Identifier("idem-" + version),
        external_references=(),
    )


def _snapshot(
    *,
    workflow_id: str = "wf-1",
    run_id: str = "run-1",
    step_index: int = 7,
    snapshot_hash_seed: str = "alpha",
    state_summary_version: str = "v1",
) -> PauseSnapshot:
    return PauseSnapshot(
        workflow_id=workflow_id,
        run_id=run_id,
        step_index=step_index,
        pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        state_summary=_state_summary(version=state_summary_version),
        snapshot_hash=hashlib.sha256(snapshot_hash_seed.encode()).hexdigest(),
        created_at=1_700_000_000_000,
        state_ledger_anchor="entry-" + snapshot_hash_seed,
    )


def _kwargs(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "workflow_id": "wf-1",
        "step_id": "step-7",
        "pause_event_id": "pause-evt-001",
        "pause_snapshot": _snapshot(),
        "actor": ActorIdentity("control-plane"),
        "procedural_tier_snapshot_resolver": _pt_resolver,
    }
    base.update(overrides)
    return base


def _run(coro: Any) -> Any:
    return asyncio.run(coro)


# --- AC #1 ---


def test_emit_pause_captured_action_id() -> None:
    """action_id is the canonical kebab-case identifier per spec v1.26 §16.5.3 row U-CP-49."""
    writer = _CapturingLedgerWriter()
    _run(
        emit_pause_captured_state_ledger_entry(**_kwargs(), ledger_writer=writer)
    )
    assert writer.captured[0].action_id == "cp.pause-captured"


# --- AC #2 ---


def test_emit_pause_captured_idempotency_key_per_q_beta_i_1a() -> None:
    """idempotency_key bytes follow §16.5.4 row U-CP-49 5-tuple (v1.26 with outcome-hash suffix)."""
    snapshot = _snapshot()
    outcome_hash = hashlib.sha256(_canonicalize_outcome_bytes(snapshot)).hexdigest()
    expected = hashlib.sha256(
        b"\x1e".join(
            (
                b"wf-1",
                b"step-7",
                b"pause-evt-001",
                snapshot.snapshot_hash.encode("utf-8"),
                outcome_hash.encode("utf-8"),
            )
        )
    ).hexdigest()
    writer = _CapturingLedgerWriter()
    _run(
        emit_pause_captured_state_ledger_entry(
            **_kwargs(pause_snapshot=snapshot), ledger_writer=writer
        )
    )
    assert writer.captured[0].idempotency_key == expected


def test_emit_pause_captured_idempotency_key_includes_snapshot_hash() -> None:
    """Different snapshot_hash at otherwise-identical inputs → different keys."""
    writer_a = _CapturingLedgerWriter()
    writer_b = _CapturingLedgerWriter()
    _run(
        emit_pause_captured_state_ledger_entry(
            **_kwargs(pause_snapshot=_snapshot(snapshot_hash_seed="alpha")),
            ledger_writer=writer_a,
        )
    )
    _run(
        emit_pause_captured_state_ledger_entry(
            **_kwargs(pause_snapshot=_snapshot(snapshot_hash_seed="beta")),
            ledger_writer=writer_b,
        )
    )
    assert (
        writer_a.captured[0].idempotency_key
        != writer_b.captured[0].idempotency_key
    )


def test_emit_pause_captured_idempotency_key_includes_pause_event_id() -> None:
    """Different pause_event_id at otherwise-identical inputs → different keys."""
    writer_a = _CapturingLedgerWriter()
    writer_b = _CapturingLedgerWriter()
    _run(
        emit_pause_captured_state_ledger_entry(
            **_kwargs(pause_event_id="evt-A"), ledger_writer=writer_a
        )
    )
    _run(
        emit_pause_captured_state_ledger_entry(
            **_kwargs(pause_event_id="evt-B"), ledger_writer=writer_b
        )
    )
    assert (
        writer_a.captured[0].idempotency_key
        != writer_b.captured[0].idempotency_key
    )


def test_emit_pause_captured_idempotency_key_includes_outcome_hash_suffix() -> None:
    """Q-β.i-1(a): different outcome canonical bytes at SAME snapshot_hash → different keys.

    Demonstrates snapshot_hash (segment 4) and outcome-hash (segment 5) are
    DISTINCT discriminators — varying state_summary changes the outcome canonical
    bytes (and outcome-hash suffix) while we hold the snapshot_hash field fixed.
    """
    # Two snapshots with the same snapshot_hash field value but different
    # canonical bytes (different state_summary → different full-snapshot bytes).
    snap_a = _snapshot(snapshot_hash_seed="fixed", state_summary_version="v1")
    snap_b = _snapshot(snapshot_hash_seed="fixed", state_summary_version="v2")
    assert snap_a.snapshot_hash == snap_b.snapshot_hash  # invariant of fixture
    assert _canonicalize_outcome_bytes(snap_a) != _canonicalize_outcome_bytes(
        snap_b
    )

    writer_a = _CapturingLedgerWriter()
    writer_b = _CapturingLedgerWriter()
    _run(
        emit_pause_captured_state_ledger_entry(
            **_kwargs(pause_snapshot=snap_a), ledger_writer=writer_a
        )
    )
    _run(
        emit_pause_captured_state_ledger_entry(
            **_kwargs(pause_snapshot=snap_b), ledger_writer=writer_b
        )
    )
    assert (
        writer_a.captured[0].idempotency_key
        != writer_b.captured[0].idempotency_key
    )


def test_emit_pause_captured_snapshot_hash_and_outcome_hash_are_distinct() -> None:
    """snapshot_hash field (segment 4) and sha256(outcome_canonical_bytes) (segment 5) differ.

    Per CP plan v2.29 §1 U-CP-78 AC #2: snapshot_hash is the pre-computed
    PauseSnapshot.snapshot_hash field per `_compute_snapshot_hash` (restricted
    canonical bytes — workflow_id + run_id + step_index + state_summary); the
    outcome-hash suffix is INDEPENDENTLY computed over the FULL PauseSnapshot
    canonical JSON bytes via `_canonicalize_outcome_bytes`. Distinct values.
    """
    snapshot = _snapshot()
    outcome_hash = hashlib.sha256(_canonicalize_outcome_bytes(snapshot)).hexdigest()
    assert snapshot.snapshot_hash != outcome_hash


# --- AC #3 ---


def test_emit_pause_captured_fires_post_capture_pre_return() -> None:
    """AC #3: composer takes the PauseSnapshot and emits a single payload.

    Documents firing-site discipline per §16.5.7: invoked once AFTER engine-
    layer `capture_pause_snapshot(...)` returns the snapshot, BEFORE returning
    to caller. Single-invocation → single payload.
    """
    writer = _CapturingLedgerWriter()
    _run(
        emit_pause_captured_state_ledger_entry(**_kwargs(), ledger_writer=writer)
    )
    assert len(writer.captured) == 1
    assert writer.captured[0].action_id == "cp.pause-captured"


# --- AC #4 (renamed per plan v2.29) ---


def test_emit_pause_captured_response_hash_is_is_computed() -> None:
    """β.i Q-β.i-3(b): composer does NOT supply response_hash; EntryPayload has no such field."""
    assert "response_hash" not in EntryPayload.model_fields
    writer = _CapturingLedgerWriter()
    _run(
        emit_pause_captured_state_ledger_entry(**_kwargs(), ledger_writer=writer)
    )
    payload = writer.captured[0]
    assert set(payload.model_fields_set) <= {
        "action_id",
        "idempotency_key",
        "actor",
        "timestamp",
        "procedural_tier_snapshot_ref",
    }


# --- AC #5 ---


def test_emit_pause_captured_zero_cp_audit_emission() -> None:
    """AC #5: greenfield composer emits NO CPAuditLedgerEntry per §16.5.9 invariant 5."""
    writer = _CapturingLedgerWriter()
    result = _run(
        emit_pause_captured_state_ledger_entry(**_kwargs(), ledger_writer=writer)
    )
    assert isinstance(result, WriteResult)
    assert len(writer.captured) == 1


def test_emit_pause_captured_engine_layer_orthogonal_to_workflow_layer_at_u_cp_76() -> (
    None
):
    """AC #5: engine-layer action_id distinct from workflow-layer at U-CP-76.

    Per CP spec v1.11 §26 NEW NOTE 2-layer coexistence: engine-layer emits
    `cp.pause-captured` here; workflow-layer at U-CP-76 emits
    `cp.pause-resume-protocol`. Distinct action_id namespaces prevent
    ledger-level collision; downstream consumers discriminate via prefix.
    """
    writer = _CapturingLedgerWriter()
    _run(
        emit_pause_captured_state_ledger_entry(**_kwargs(), ledger_writer=writer)
    )
    engine_layer_action_id = writer.captured[0].action_id
    assert engine_layer_action_id == "cp.pause-captured"
    # Workflow-layer action_id at U-CP-76 is distinct.
    assert engine_layer_action_id != "cp.pause-resume-protocol"


# --- composer-await discipline (orthogonal to U-CP-74 AC #9) ---


def test_emit_pause_captured_orthogonal_to_writer_result_variant() -> None:
    """Composer awaits ledger_writer return; does not condition on WriteResult variant."""
    appended_writer = _CapturingLedgerWriter(returns=WriteResult.APPENDED)
    noop_writer = _CapturingLedgerWriter(returns=WriteResult.IDEMPOTENT_NOOP)

    result_a = _run(
        emit_pause_captured_state_ledger_entry(
            **_kwargs(), ledger_writer=appended_writer
        )
    )
    result_b = _run(
        emit_pause_captured_state_ledger_entry(
            **_kwargs(), ledger_writer=noop_writer
        )
    )

    assert result_a == WriteResult.APPENDED
    assert result_b == WriteResult.IDEMPOTENT_NOOP
    assert (
        appended_writer.captured[0].idempotency_key
        == noop_writer.captured[0].idempotency_key
    )


# --- Actor projection ---


def test_emit_pause_captured_actor_projects_to_agent_class() -> None:
    """actor_id is the ActorIdentity stringified; actor_class = AGENT."""
    writer = _CapturingLedgerWriter()
    _run(
        emit_pause_captured_state_ledger_entry(
            **_kwargs(actor=ActorIdentity("engine-layer")),
            ledger_writer=writer,
        )
    )
    actor = writer.captured[0].actor
    assert actor.actor_class == ActorClass.AGENT
    assert actor.actor_id == "engine-layer"
