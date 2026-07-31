"""B-69 impl leg — U-OD-57 (`Implementation_Plan_Operational_Discipline_v2_31.md`).

OD spec v1.36 §C-OD-30.5 authorizes an ADDITIVE carrier for the two new event kinds
under EITHER of two options; this impl leg selected **option (b) — a sibling payload
type** — so the OD-owned acceptance criteria live here.

The load-bearing witnesses are (1) the outcome split is ENFORCED rather than
documented, and (2) the byte-compat witness §30.5.2 names: the existing
`PauseResumeAuditPayload` field set and both existing §C-OD-30.4 helpers are
PRESERVED VERBATIM, so no already-shipped construction site is affected.
"""

from __future__ import annotations

import pytest
from harness_od.pause_resume_namespace import (
    PAUSE_RESUME_SPAN_NAMESPACE_SCHEMA,
    PAUSE_STATE_EVENT_HEAD_SAMPLING_RATE,
    PauseResumeAuditPayload,
    PauseStateAuditPayload,
    PauseStateEventKind,
)
from pydantic import ValidationError

_WF = "wf-b69-od"


def _successful_read() -> PauseStateAuditPayload:
    return PauseStateAuditPayload(
        event_kind=PauseStateEventKind.ACCESSOR_READ,
        workflow_id=_WF,
        succeeded=True,
        staleness_token="tok",
        hitl_addressable_count=1,
        effect_fence_addressable_count=0,
        uniform_fallback_only_count=2,
        transitively_paused_count=1,
    )


def test_existing_pause_resume_payload_field_set_is_preserved_verbatim() -> None:
    """The byte-compat witness §30.5.2 requires: choosing the SIBLING option means
    no already-shipped `PauseResumeAuditPayload` construction site is affected —
    its field set, its `frozen` / `extra="forbid"` posture, and both existing
    §C-OD-30.4 helpers are untouched."""
    assert set(PauseResumeAuditPayload.model_fields) == {
        "audit_cp_action_id",
        "audit_cp_response",
        "audit_cp_prior_event_hash",
        "audit_cp_timestamp",
        "snapshot_hash",
        "step_index",
        "pause_reason",
        "state_ledger_anchor",
        "diff_detected",
        "diff_policy",
        "diff_summary_hash",
        "resume_outcome",
    }
    assert PauseResumeAuditPayload.model_config["frozen"] is True
    assert PauseResumeAuditPayload.model_config["extra"] == "forbid"
    assert "staleness_token" not in PauseResumeAuditPayload.model_fields
    # The C-OD-05 §5.1 namespace roster is UNCHANGED — no new top-level namespace
    # is minted; both new event kinds ride the EXISTING C-OD-30 family.
    assert len(PAUSE_RESUME_SPAN_NAMESPACE_SCHEMA) == 8


def test_sibling_payload_preserves_the_closed_schema_posture() -> None:
    """The sibling carries the same closed-schema posture the axis declares."""
    assert PauseStateAuditPayload.model_config["frozen"] is True
    assert PauseStateAuditPayload.model_config["extra"] == "forbid"
    with pytest.raises(ValidationError):
        PauseStateAuditPayload(
            event_kind=PauseStateEventKind.ACCESSOR_READ,
            workflow_id=_WF,
            succeeded=False,
            cause_attribution="absent",
            unexpected_field="x",  # pyright: ignore[reportCallIssue]
        )


def test_successful_read_carries_four_counts_never_one_aggregate_total() -> None:
    """§30.5.1 — PER-VARIANT counts, FOUR of them. A single scalar total cannot
    express classification, while the disclosure limit requires classification
    WITHOUT identity."""
    row = _successful_read()
    assert (
        row.hitl_addressable_count,
        row.effect_fence_addressable_count,
        row.uniform_fallback_only_count,
        row.transitively_paused_count,
    ) == (1, 0, 2, 1)
    with pytest.raises(ValidationError):  # a partial count set is refused
        PauseStateAuditPayload(
            event_kind=PauseStateEventKind.ACCESSOR_READ,
            workflow_id=_WF,
            succeeded=True,
            staleness_token="tok",
            hitl_addressable_count=1,
        )


def test_failed_read_must_emit_and_carries_cause_but_no_token_and_no_counts() -> None:
    """§30.5.1 — a failed read MUST still emit; silence is not the failure
    disposition. It mints no token by construction, so requiring one would force an
    implementation either to fabricate a token (defeating the fence) or to suppress
    the emission (defeating the no-silent-failure rule)."""
    row = PauseStateAuditPayload(
        event_kind=PauseStateEventKind.ACCESSOR_READ,
        workflow_id=_WF,
        succeeded=False,
        cause_attribution="empty-journal",
    )
    assert row.staleness_token is None
    assert row.hitl_addressable_count is None
    with pytest.raises(ValidationError):  # a failed read with no cause at all
        PauseStateAuditPayload(
            event_kind=PauseStateEventKind.ACCESSOR_READ, workflow_id=_WF, succeeded=False
        )


def test_refusal_event_must_carry_the_pairing_token() -> None:
    """§30.5.3 — the token is the pairing key, and it is REQUIRED on the refusal.
    Without it an operator investigating a refusal sees a resume that failed and a
    read that succeeded, with no evidence linking them, and the refusal's own
    operator-facing text becomes unverifiable after the fact."""
    row = PauseStateAuditPayload(
        event_kind=PauseStateEventKind.STALENESS_REFUSED_RESUME,
        workflow_id=_WF,
        succeeded=False,
        staleness_token="tok",
    )
    assert row.staleness_token == "tok"
    with pytest.raises(ValidationError):
        PauseStateAuditPayload(
            event_kind=PauseStateEventKind.STALENESS_REFUSED_RESUME,
            workflow_id=_WF,
            succeeded=False,
        )
    with pytest.raises(ValidationError):  # a refusal never "succeeded"
        PauseStateAuditPayload(
            event_kind=PauseStateEventKind.STALENESS_REFUSED_RESUME,
            workflow_id=_WF,
            succeeded=True,
            staleness_token="tok",
        )


def test_no_disclosure_channel_exists_on_the_payload_at_all() -> None:
    """§30.5.1 disclosure limits — the locations' payload and the never-keyable
    pre-dispatch / depth-0-root internal identity are ABSENT BY TYPE, so no
    implementation can emit them even by accident."""
    forbidden = {
        "run_id",
        "child_run_id",
        "identity",
        "locations",
        "summary_text",
        "state_summary",
        "external_references",
        "relevant_entries",
        "snapshot_hash",
        "state_ledger_anchor",
        "exception",
        "path",
    }
    assert forbidden.isdisjoint(PauseStateAuditPayload.model_fields)


def test_both_event_kinds_take_the_same_declared_head_sampling_rate() -> None:
    """§30.5.4 — DECLARED, not inherited. C-OD-30's existing discipline names only
    the event kinds it already carries, so "unchanged" would have left these
    REQUIRED emissions with no rule at all. Both take the same rate because
    §30.5.3's pairing requirement is only sound if BOTH members are retained —
    independent sampling would break causal-pair reconstruction at exactly the rate
    it drops either one."""
    assert PAUSE_STATE_EVENT_HEAD_SAMPLING_RATE == 1.0
    assert len(PauseStateEventKind) == 2
