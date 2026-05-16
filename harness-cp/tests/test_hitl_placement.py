"""Tests for U-CP-38 — 3-placement HITL enum + `hitl_gate` + `HITLPlacement`.

Acceptance-criterion coverage:
  #1 HITLPlacementKind 3 values   -> test_placement_kind_cardinality_three
  #2 HITL_PLACEMENT_TRIGGERS 3    -> test_placement_triggers_match_spec
  #3 hitl_gate 5 params           -> test_hitl_gate_signature_five_parameters
  #3 HITLResult 6 fields          -> test_hitl_result_six_fields
  #4 response palette / EDIT/RESPOND -> test_hitl_result_edit_and_respond_fields
  #5 response_palette is Set      -> test_response_palette_is_set
  #6 HITLPlacement 4 fields       -> test_hitl_placement_four_fields
  #6 multiple placements          -> test_multiple_placements_permitted
"""

from __future__ import annotations

import inspect

import pytest
from harness_core.identity import EntryID

from harness_cp.handoff_context import (
    ActionKind,
    HandoffContext,
    LedgerEntryRef,
    ProposedAction,
    RetryHistory,
    StateSummary,
)
from harness_cp.hitl_placement import (
    HITL_PLACEMENT_TRIGGERS,
    HITLPlacement,
    HITLPlacementKind,
    HITLResult,
    hitl_gate,
)
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.topology_pattern import CascadePolicy

_PROPOSED = ProposedAction(action_kind=ActionKind.TOOL_CALL, payload={})
_LEDGER_REF = LedgerEntryRef(
    action_id="a0",  # type: ignore[arg-type]
    entry_hash="0" * 64,
    actor="lead",  # type: ignore[arg-type]
)
_STATE = StateSummary(
    relevant_entries=(),
    summary_text="s",
    summary_hash="0" * 64,
    idempotency_key="k0",  # type: ignore[arg-type]
    external_references=(),
)
_HANDOFF = HandoffContext(
    proposed_action=_PROPOSED,
    failed_attempts=(),
    alternatives_considered=(),
    state_summary=_STATE,
    audit_trail_link=_LEDGER_REF,
    retry_history=RetryHistory(attempts=(), retry_count=0),
)


def test_placement_kind_cardinality_three() -> None:
    assert len(list(HITLPlacementKind)) == 3
    assert {p.value for p in HITLPlacementKind} == {
        "pre-action",
        "sub-agent-boundary",
        "validator-escalation",
    }


def test_placement_triggers_match_spec() -> None:
    assert len(HITL_PLACEMENT_TRIGGERS) == 3
    assert {t.placement_kind for t in HITL_PLACEMENT_TRIGGERS} == set(
        HITLPlacementKind
    )


def test_hitl_gate_signature_five_parameters() -> None:
    sig = inspect.signature(hitl_gate)
    assert list(sig.parameters) == [
        "placement",
        "handoff_context",
        "response_palette",
        "timeout",
        "cascade_policy",
    ]
    assert sig.return_annotation == "HITLResult"


def test_hitl_result_six_fields() -> None:
    assert set(HITLResult.model_fields) == {
        "response",
        "edited_proposal",
        "response_text",
        "timestamp",
        "audit_ledger_entry_id",
        "response_summary_hash",
    }


def test_hitl_result_edit_and_respond_fields() -> None:
    edit = HITLResult(
        response=HITLResponse.EDIT,
        edited_proposal=_PROPOSED,
        timestamp="2026-05-16T00:00:00Z",
        audit_ledger_entry_id=EntryID("e0"),
        response_summary_hash="0" * 64,
    )
    assert edit.edited_proposal is _PROPOSED
    respond = HITLResult(
        response=HITLResponse.RESPOND,
        response_text="continue",
        timestamp="2026-05-16T00:00:00Z",
        audit_ledger_entry_id=EntryID("e1"),
        response_summary_hash="0" * 64,
    )
    assert respond.response_text == "continue"


def test_response_palette_is_set() -> None:
    sig = inspect.signature(hitl_gate)
    assert sig.parameters["response_palette"].annotation == "set[HITLResponse]"


def test_hitl_placement_four_fields() -> None:
    assert set(HITLPlacement.model_fields) == {
        "position",
        "tool_filter",
        "cascade_policy",
        "timeout",
    }


def test_multiple_placements_permitted() -> None:
    placements = [
        HITLPlacement(position=HITLPlacementKind.PRE_ACTION),
        HITLPlacement(
            position=HITLPlacementKind.VALIDATOR_ESCALATION,
            cascade_policy=CascadePolicy.PAUSE,
        ),
    ]
    assert len(placements) == 2


def test_hitl_gate_is_interface_signature() -> None:
    with pytest.raises(NotImplementedError):
        hitl_gate(
            HITLPlacementKind.PRE_ACTION,
            _HANDOFF,
            {HITLResponse.APPROVE},
            None,
            CascadePolicy.PAUSE,
        )
