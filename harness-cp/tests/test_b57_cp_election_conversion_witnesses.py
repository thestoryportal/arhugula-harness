"""Per-site conversion witnesses for the CP half of IS plan v2.9 §2.1 —
C-IS-07 §7.6.1 per-call-site writer-owned ELECTION (IS spec v1.13, `B-57`).

Rows 2-9 live in `harness-cp`. Each witness drives the real composer and
captures the `EntryPayload` it produces at a stub ledger writer, asserting that
THIS site expresses the election — it stamps `WRITER_OWNED_TIMESTAMP` rather
than a locally-captured `datetime.now(UTC)`.

**PD-8 for every test in this file** is the same single reversion: restore
`timestamp=datetime.now(UTC)` at the site under test and its witness FAILS —
the captured payload carries a real instant instead of the sentinel. Each was
run RED under that reversion before being accepted.

The end-to-end CONSEQUENCE of these elections (that the sentinel actually
yields writer-owned, append-ordered sampling under real two-process contention)
is witnessed once, at `harness-is/tests/test_b57_direct_append_election.py`,
rather than restated per site — the sentinel's meaning is IS-owned and
identical at every site. Fixtures below mirror each composer's own existing
emission-test module so the witnesses exercise the shapes those tests already
pin.
"""

from __future__ import annotations

import asyncio
import hashlib
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any, cast

from harness_cp.cp_shared_types import ActorIdentity
from harness_cp.engine_class import EngineClass
from harness_cp.handoff_context import ExternalReference, ReferenceClass, StateSummary
from harness_cp.hitl_as_tool_call_rewriting import (
    HITLSemanticVariant,
    RewrittenToolCall,
    emit_hitl_tool_call_rewriting_state_ledger_entry,
)
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.pause_resume_protocol import (
    PauseEvent,
    PauseReason,
    PauseResumeProtocolEventKind,
    ResumeOutcome,
    ResumeOutcomeKind,
    emit_pause_captured_state_ledger_entry,
    emit_pause_resume_state_ledger_entry,
    emit_resume_attempted_state_ledger_entry,
)
from harness_cp.per_step_override_evaluator import (
    compose_override_entry_payload,
    emit_override_state_ledger_entry,
)
from harness_cp.workflow_driver import (
    _append_step_ledger_entry,
    _append_synthesis_ledger_entry,
)
from harness_cp.workload_binding_engine_class_selection import (
    WorkloadBindingSelectionResult,
    emit_workload_class_selection_state_ledger_entry,
)
from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier
from harness_is.state_ledger_write import (
    WRITER_OWNED_TIMESTAMP,
    EntryPayload,
    WriteResult,
)

_PROCEDURAL_TIER_SNAPSHOT_FIXTURE = Identifier("a" * 64)


def _pt_resolver() -> Identifier:
    return _PROCEDURAL_TIER_SNAPSHOT_FIXTURE


class _CapturingLedgerWriter:
    """Async `ledger_writer` stub — records the composed payload verbatim."""

    def __init__(self) -> None:
        self.captured: list[EntryPayload] = []

    async def __call__(self, payload: EntryPayload) -> WriteResult:
        self.captured.append(payload)
        return WriteResult.APPENDED


def _run(coro: Any) -> Any:
    return asyncio.run(coro)


def _assert_elects(writer: _CapturingLedgerWriter, row: int) -> None:
    [payload] = writer.captured
    assert payload.timestamp == WRITER_OWNED_TIMESTAMP, (
        f"IS plan v2.9 §2.1 row {row} must ELECT writer-owned sampling "
        f"(C-IS-07 §7.6.1), got {payload.timestamp!r}"
    )
    # The election changes ONLY which instant is recorded — the rest of the
    # composed shape is untouched, which is what makes it a one-line change.
    assert payload.procedural_tier_snapshot_ref == _PROCEDURAL_TIER_SNAPSHOT_FIXTURE


# ---------------------------------------------------------------------------
# Rows 2, 3, 4 — `pause_resume_protocol` §16.5 composers.
# ---------------------------------------------------------------------------


def test_row_2_pause_resume_protocol_entry_elects() -> None:
    writer = _CapturingLedgerWriter()
    _run(
        emit_pause_resume_state_ledger_entry(
            workflow_id="wf-1",
            step_id="step-2",
            protocol_event_kind=PauseResumeProtocolEventKind.PAUSE_CAPTURED,
            event_sequence_id=42,
            protocol_state_snapshot={"step_index": 7, "snapshot_hash": "deadbeef" * 8},
            actor=ActorIdentity("control-plane"),
            ledger_writer=writer,
            procedural_tier_snapshot_resolver=_pt_resolver,
        )
    )
    _assert_elects(writer, 2)


def _state_summary(version: str = "v1") -> StateSummary:
    return StateSummary(
        relevant_entries=(),
        summary_text=version,
        summary_hash=hashlib.sha256(version.encode()).hexdigest(),
        idempotency_key=Identifier("idem-" + version),
        external_references=(
            ExternalReference(
                reference_class=ReferenceClass.FILESYSTEM_STATE,
                reference_id="state-" + version,
                snapshot_capture_at_pause=b"snapshot-" + version.encode("utf-8"),
            ),
        ),
    )


def test_row_3_pause_captured_entry_elects() -> None:
    summary = _state_summary()
    writer = _CapturingLedgerWriter()
    _run(
        emit_pause_captured_state_ledger_entry(
            workflow_id="wf-1",
            step_id="step-7",
            pause_event=PauseEvent(
                paused_at="2023-11-14T22:13:20+00:00",
                pause_reason=PauseReason.OPERATOR_INITIATED_PAUSE,
                state_summary_snapshot=summary,
                external_refs_captured=summary.external_references,
                pause_audit_entry_id=Identifier("pause-audit-001"),
            ),
            actor=ActorIdentity("control-plane"),
            ledger_writer=writer,
            procedural_tier_snapshot_resolver=_pt_resolver,
        )
    )
    _assert_elects(writer, 3)
    # The pause EVENT's own instant is untouched by the election — it lives on
    # `PauseEvent.paused_at`, not on the ledger `timestamp` field. That is the
    # §7.6.1 eligibility rule holding at this site: the ledger timestamp means
    # *when the entry was appended*, so nothing event-time is displaced.


def test_row_4_resume_attempted_entry_elects() -> None:
    writer = _CapturingLedgerWriter()
    _run(
        emit_resume_attempted_state_ledger_entry(
            workflow_id="wf-1",
            step_id="step-7",
            resume_event_id="resume-evt-001",
            resume_attempt_count=1,
            resume_outcome=ResumeOutcome(
                outcome_kind=ResumeOutcomeKind.RESUME_CLEAN,
                material_diff=(),
                context_revalidated=False,
                resume_audit_entry_id=None,
            ),
            actor=ActorIdentity("engine-layer"),
            ledger_writer=writer,
            procedural_tier_snapshot_resolver=_pt_resolver,
        )
    )
    _assert_elects(writer, 4)


# ---------------------------------------------------------------------------
# Row 7 — `workload_binding_engine_class_selection` §16.5 composer.
# ---------------------------------------------------------------------------


def test_row_7_workload_class_selection_entry_elects() -> None:
    writer = _CapturingLedgerWriter()
    _run(
        emit_workload_class_selection_state_ledger_entry(
            workflow_id="wf-1",
            step_id="step-2",
            selection_result=WorkloadBindingSelectionResult(
                selected_class=EngineClass.SAVE_POINT_CHECKPOINT,
                candidate_set=frozenset(
                    {
                        EngineClass.SAVE_POINT_CHECKPOINT,
                        EngineClass.PURE_PATTERN_NO_ENGINE,
                    }
                ),
                selection_rationale="§7.3 step 2",
            ),
            actor=ActorIdentity("control-plane"),
            ledger_writer=writer,
            procedural_tier_snapshot_resolver=_pt_resolver,
        )
    )
    _assert_elects(writer, 7)


# ---------------------------------------------------------------------------
# Row 8 — `hitl_as_tool_call_rewriting` §16.5 composer.
# ---------------------------------------------------------------------------


def test_row_8_hitl_tool_call_rewriting_entry_elects() -> None:
    writer = _CapturingLedgerWriter()
    _run(
        emit_hitl_tool_call_rewriting_state_ledger_entry(
            workflow_id="wf-1",
            step_id="step-2",
            tool_call_id="call-9001",
            semantic_variant_binding_id="row-2-await-human-approval",
            rewritten_tool_call=RewrittenToolCall(
                tool="send_email",
                server="mcp-mail",
                hitl_required=True,
                variant=HITLSemanticVariant.AWAIT_HUMAN_APPROVAL,
                response_palette=frozenset(HITLResponse),
            ),
            actor=ActorIdentity("control-plane"),
            ledger_writer=writer,
            procedural_tier_snapshot_resolver=_pt_resolver,
        )
    )
    _assert_elects(writer, 8)


# ---------------------------------------------------------------------------
# Row 9 — `per_step_override_evaluator`: the election is at the SAMPLING
# caller, NOT at the shared composer the buffered-branch path also uses.
# ---------------------------------------------------------------------------


def test_row_9_override_emitter_elects_at_the_sampling_caller() -> None:
    writer = _CapturingLedgerWriter()
    _run(
        emit_override_state_ledger_entry(
            workflow_id="wf-1",
            step_id="step-2",
            post_override_step_config={"model": "m"},
            actor=ActorIdentity("control-plane"),
            ledger_writer=writer,
            procedural_tier_snapshot_resolver=_pt_resolver,
        )
    )
    _assert_elects(writer, 9)


def test_row_9_shared_composer_still_passes_its_caller_supplied_timestamp() -> None:
    """The other half of row 9, and the reason the election is NOT expressed at
    `compose_override_entry_payload`: that function is the SHARED shape
    authority the CP-driver buffered-branch path also composes through, with a
    buffer-time placeholder the barrier drain re-stamps (§7.6). Electing inside
    the composer would silently convert that second path too — a conversion at
    a site IS plan v2.9 §2.1 does not classify ELECT, i.e. an AC #17 failure.

    PD-8: move the election into `compose_override_entry_payload` and this
    FAILS — the branch path's placeholder stops surviving composition.
    """
    placeholder = datetime(2026, 5, 19, 12, 0, 0, tzinfo=UTC)
    payload = compose_override_entry_payload(
        workflow_id="wf-1",
        step_id="step-2",
        post_override_step_config={"model": "m"},
        actor=ActorIdentity("control-plane"),
        procedural_tier_snapshot_ref=_PROCEDURAL_TIER_SNAPSHOT_FIXTURE,
        timestamp=placeholder,
    )
    assert payload.timestamp == placeholder


# ---------------------------------------------------------------------------
# Rows 5, 6 — the two genuine DIRECT appends at `workflow_driver`.
# ---------------------------------------------------------------------------


class _CapturingSyncLedgerWriter:
    """Sync `ctx.ledger_writer` stub — the driver's own writer surface."""

    def __init__(self) -> None:
        self.actor = Actor(actor_class=ActorClass.AGENT, actor_id="driver")
        self.captured: list[EntryPayload] = []

    def append(self, payload: EntryPayload, write_key: object) -> WriteResult:
        self.captured.append(payload)
        return WriteResult.APPENDED


def _driver_ctx() -> SimpleNamespace:
    return SimpleNamespace(
        ledger_writer=_CapturingSyncLedgerWriter(),
        procedural_tier_snapshot_resolver=_pt_resolver,
    )


def test_row_5_per_step_ledger_entry_elects() -> None:
    ctx = _driver_ctx()
    _append_step_ledger_entry(
        ctx=cast(Any, ctx),
        workflow_id="wf-1",
        step_index=3,
        step_idempotency_key="idem-step-3",
        step_output={"ok": True},
    )
    [payload] = ctx.ledger_writer.captured
    assert payload.timestamp == WRITER_OWNED_TIMESTAMP, (
        "IS plan v2.9 §2.1 row 5 must ELECT writer-owned sampling"
    )
    assert payload.procedural_tier_snapshot_ref == _PROCEDURAL_TIER_SNAPSHOT_FIXTURE


def test_row_6_post_join_synthesis_ledger_entry_elects() -> None:
    ctx = _driver_ctx()
    _append_synthesis_ledger_entry(
        ctx=cast(Any, ctx),
        workflow_id="wf-1",
        synthesis_index=0,
        synthesis_idempotency_key="idem-synth-0",
    )
    [payload] = ctx.ledger_writer.captured
    assert payload.timestamp == WRITER_OWNED_TIMESTAMP, (
        "IS plan v2.9 §2.1 row 6 must ELECT writer-owned sampling"
    )
    assert payload.action_id == "workflow:wf-1:post-join-synthesis:0"
