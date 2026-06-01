"""Tests for U-CP-62 — C-CP-26 PauseResumeProtocol type carriers.

ACs from CP plan v2.17 §1 U-CP-62 (v2.17 amendment — enum identifier renamed
`PauseReason` → `WorkflowPauseReason`; member values + cardinality preserved):
  AC #1 WorkflowPauseReason 5-class with all members per CP spec v1.11 §26.2
  AC #2 MaterialDiffPolicy default value = STRICT (per Decision 2.D7 RATIFIED)
  AC #3 PauseSnapshot.state_summary typed against existing CP plan v2.9 StateSummary
  AC #4 PauseSnapshot.snapshot_hash is sha256 hex string (64 chars)
  AC #5 ResumeResult.diff_summary_hash optional per spec §26.2

Regression-gate AC against path γ collision: WorkflowPauseReason distinct from
engine-layer PauseReason at harness_cp.pause_resume_protocol.
"""

from __future__ import annotations

import hashlib

import pytest
from harness_cp.handoff_context import StateSummary
from harness_cp.pause_resume_protocol_types import (
    MaterialDiffPolicy,
    PauseSnapshot,
    ResumeResult,
    WorkflowPauseReason,
)
from pydantic import ValidationError

# --- AC #1 — WorkflowPauseReason 5-class -----------------------------------


def test_workflow_pause_reason_has_exactly_five_members() -> None:
    """AC #1 — WorkflowPauseReason declares exactly five members."""
    assert len(WorkflowPauseReason) == 5


def test_workflow_pause_reason_member_values_verbatim() -> None:
    """AC #1 — member string values match CP spec v1.11 §26.2 verbatim."""
    assert {r.value for r in WorkflowPauseReason} == {
        "explicit_operator",
        "hitl_pending",
        "validator_escalation",
        "timeout_boundary",
        "external_dependency",
    }


def test_workflow_pause_reason_member_names() -> None:
    """AC #1 — member names EXPLICIT_OPERATOR / HITL_PENDING / VALIDATOR_ESCALATION
    / TIMEOUT_BOUNDARY / EXTERNAL_DEPENDENCY per spec §26.2."""
    assert {r.name for r in WorkflowPauseReason} == {
        "EXPLICIT_OPERATOR",
        "HITL_PENDING",
        "VALIDATOR_ESCALATION",
        "TIMEOUT_BOUNDARY",
        "EXTERNAL_DEPENDENCY",
    }


# --- AC #2 — MaterialDiffPolicy STRICT default -----------------------------


def test_material_diff_policy_has_exactly_three_members() -> None:
    """AC #2 — MaterialDiffPolicy declares exactly three members."""
    assert len(MaterialDiffPolicy) == 3


def test_material_diff_policy_strict_value() -> None:
    """AC #2 — STRICT member exists with value "strict"."""
    assert MaterialDiffPolicy.STRICT.value == "strict"


def test_material_diff_policy_member_values_verbatim() -> None:
    """AC #2 — member string values match spec §26.2 verbatim."""
    assert {p.value for p in MaterialDiffPolicy} == {
        "strict",
        "lenient",
        "operator_arbitrate",
    }


def test_material_diff_policy_default_is_strict_by_construction() -> None:
    """AC #2 — STRICT is the default per Decision 2.D7 RATIFIED. The default
    is enforced by call-site convention (Python enums have no class-level
    default). This test pins the STRICT member's identity for downstream
    callers that bind `policy = MaterialDiffPolicy.STRICT` as the default.
    """
    default = MaterialDiffPolicy.STRICT
    assert default is MaterialDiffPolicy.STRICT
    assert default.value == "strict"


# --- AC #3 — PauseSnapshot.state_summary typed against StateSummary --------


def _build_minimal_state_summary() -> StateSummary:
    """Construct a minimal StateSummary for snapshot tests."""
    from harness_is.state_ledger_entry_schema import Identifier

    return StateSummary(
        relevant_entries=(),
        summary_text="minimal",
        summary_hash="0" * 64,
        idempotency_key=Identifier("idem-1"),
        external_references=(),
    )


def test_pause_snapshot_state_summary_is_state_summary_typed() -> None:
    """AC #3 — PauseSnapshot.state_summary resolves to StateSummary type."""
    from typing import get_type_hints

    hints = get_type_hints(PauseSnapshot)
    assert hints["state_summary"] is StateSummary


def test_pause_snapshot_accepts_state_summary_instance() -> None:
    """AC #3 — PauseSnapshot constructs with a real StateSummary."""
    snapshot = PauseSnapshot(
        workflow_id="wf-1",
        run_id="run-1",
        step_index=0,
        pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        state_summary=_build_minimal_state_summary(),
        snapshot_hash="a" * 64,
        created_at=1_700_000_000_000,
        state_ledger_anchor="b" * 64,
    )
    assert isinstance(snapshot.state_summary, StateSummary)


# --- AC #4 — PauseSnapshot.snapshot_hash sha256 hex (64 chars) -------------


def test_pause_snapshot_snapshot_hash_accepts_64_char_hex() -> None:
    """AC #4 — snapshot_hash carries a 64-char sha256 hex value."""
    digest = hashlib.sha256(b"wf-1|run-1|0|state").hexdigest()
    snapshot = PauseSnapshot(
        workflow_id="wf-1",
        run_id="run-1",
        step_index=0,
        pause_reason=WorkflowPauseReason.HITL_PENDING,
        state_summary=_build_minimal_state_summary(),
        snapshot_hash=digest,
        created_at=1_700_000_000_000,
        state_ledger_anchor="b" * 64,
    )
    assert len(snapshot.snapshot_hash) == 64
    assert snapshot.snapshot_hash == digest


# --- AC #5 — ResumeResult.diff_summary_hash optional -----------------------


def test_resume_result_diff_summary_hash_optional() -> None:
    """AC #5 — diff_summary_hash optional per spec §26.2 (None default permitted)."""
    result = ResumeResult(resumed=True, diff_detected=False)
    assert result.diff_summary_hash is None


def test_resume_result_all_optional_fields_default_none() -> None:
    """AC #5 — diff_summary_hash + new_run_id + fail_class all optional."""
    result = ResumeResult(resumed=True, diff_detected=False)
    assert result.diff_summary_hash is None
    assert result.new_run_id is None
    assert result.fail_class is None


def test_resume_result_carries_diff_summary_hash_when_provided() -> None:
    """AC #5 — diff_summary_hash carries sha256 hex when present."""
    digest = hashlib.sha256(b"diff").hexdigest()
    result = ResumeResult(
        resumed=False,
        diff_detected=True,
        diff_summary_hash=digest,
        fail_class="CP-FAIL-RESUME-MATERIAL-DIFF-DETECTED",
    )
    assert result.diff_summary_hash == digest


# --- Frozen-model + extra="forbid" guards ----------------------------------


def test_pause_snapshot_is_frozen() -> None:
    """PauseSnapshot.model_config = frozen=True (§26.6 invariant 1: snapshot
    immutable after capture)."""
    snapshot = PauseSnapshot(
        workflow_id="wf-1",
        run_id="run-1",
        step_index=0,
        pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        state_summary=_build_minimal_state_summary(),
        snapshot_hash="a" * 64,
        created_at=1_700_000_000_000,
        state_ledger_anchor="b" * 64,
    )
    with pytest.raises(ValidationError):
        snapshot.workflow_id = "wf-2"  # type: ignore[misc]


def test_resume_result_is_frozen() -> None:
    """ResumeResult.model_config = frozen=True."""
    result = ResumeResult(resumed=True, diff_detected=False)
    with pytest.raises(ValidationError):
        result.resumed = False  # type: ignore[misc]


def test_pause_snapshot_forbids_extra_fields() -> None:
    """PauseSnapshot extra="forbid"."""
    with pytest.raises(ValidationError):
        PauseSnapshot(
            workflow_id="wf-1",
            run_id="run-1",
            step_index=0,
            pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
            state_summary=_build_minimal_state_summary(),
            snapshot_hash="a" * 64,
            created_at=1_700_000_000_000,
            state_ledger_anchor="b" * 64,
            extra_field="x",  # pyright: ignore[reportCallIssue]
        )


# --- Path γ regression gate: WorkflowPauseReason ≠ engine-layer PauseReason -


def test_workflow_pause_reason_distinct_from_engine_layer_pause_reason() -> None:
    """Regression gate: WorkflowPauseReason (workflow-layer C-CP-26) is distinct
    from PauseReason (engine-layer C-CP-22 / U-CP-49) per path γ disambiguation.
    The two enums must not share any member values (5-class vs 4-class with
    fully disjoint member sets per CP spec v1.11 §26 NEW NOTE coexistence).
    """
    from harness_cp.pause_resume_protocol import PauseReason as EngineLayerPauseReason

    workflow_layer_values = {r.value for r in WorkflowPauseReason}
    engine_layer_values = {r.value for r in EngineLayerPauseReason}
    assert workflow_layer_values.isdisjoint(engine_layer_values)
    assert len(workflow_layer_values) == 5
    assert len(engine_layer_values) == 4


def test_workflow_pause_reason_class_identity_distinct() -> None:
    """Regression gate: WorkflowPauseReason class object distinct from engine-layer
    PauseReason class object — both importable from their respective modules
    without identifier collision."""
    from harness_cp.pause_resume_protocol import PauseReason as EngineLayerPauseReason

    assert WorkflowPauseReason is not EngineLayerPauseReason


# --- §26.8 ResumeContext carrier (v2.21 AC #6) -----------------------------


def _build_hitl_result():  # type: ignore[no-untyped-def]
    """Construct a populated HITLResult for ResumeContext field-population tests."""
    from harness_core.identity import EntryID
    from harness_cp.hitl_placement import HITLResult
    from harness_cp.hitl_response_palette import HITLResponse

    return HITLResult(
        response=HITLResponse.RESPOND,
        response_text="approve",
        timestamp="2026-05-24T00:00:00Z",
        audit_ledger_entry_id=EntryID("e-rc-1"),
        response_summary_hash="a" * 64,
    )


def test_resume_context_default_hitl_response_is_none() -> None:
    """AC #6: ResumeContext defaults `hitl_response` to None (backward-compat).

    The default-None posture preserves identical control flow for existing
    callers (L9-undecies `workflow_driver.py:477` async-bridge invocation
    passes no `resume_context` → receives None at `attempt_resume`)."""
    # Import deferred until pause_resume_protocol is loaded so model_rebuild fires.
    from harness_cp.pause_resume_protocol import ResumeContext  # noqa: F401
    from harness_cp.pause_resume_protocol_types import ResumeContext as _RC

    rc = _RC()
    assert rc.hitl_response is None


def test_resume_context_accepts_populated_hitl_response() -> None:
    """AC #6: ResumeContext accepts a populated HITLResult per CP spec v1.16 §26.8.2."""
    from harness_cp.pause_resume_protocol import ResumeContext  # noqa: F401
    from harness_cp.pause_resume_protocol_types import ResumeContext as _RC

    hitl = _build_hitl_result()
    rc = _RC(hitl_response=hitl)
    assert rc.hitl_response is hitl


def test_resume_context_is_frozen() -> None:
    """AC #6: ResumeContext is a frozen Pydantic v2 BaseModel per §26.8.1."""
    from harness_cp.pause_resume_protocol import ResumeContext  # noqa: F401
    from harness_cp.pause_resume_protocol_types import ResumeContext as _RC

    rc = _RC()
    with pytest.raises(ValidationError):
        rc.hitl_response = _build_hitl_result()  # type: ignore[misc]


def test_resume_context_extra_forbid() -> None:
    """AC #6: ResumeContext forbids extra fields (extra='forbid' from ConfigDict)."""
    from harness_cp.pause_resume_protocol import ResumeContext  # noqa: F401
    from harness_cp.pause_resume_protocol_types import ResumeContext as _RC

    with pytest.raises(ValidationError):
        _RC(extra_field="x")  # pyright: ignore[reportCallIssue]


def test_resume_context_single_field_shape() -> None:
    """AC #6: ResumeContext has exactly one declared field at v1.16 per §26.8.2.

    Future arcs may extend (per §26.8.1 change-note adjacent defect (i)).
    This gate locks the v1.16 single-field shape so any future extension is
    a deliberate spec amendment, not a silent absorption.
    """
    from harness_cp.pause_resume_protocol import ResumeContext  # noqa: F401
    from harness_cp.pause_resume_protocol_types import ResumeContext as _RC

    assert set(_RC.model_fields.keys()) == {"hitl_response"}
