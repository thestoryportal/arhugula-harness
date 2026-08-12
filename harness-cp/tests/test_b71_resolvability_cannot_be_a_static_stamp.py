"""B-71 precondition-3 witness — why `resolvability` cannot be a static stamp.

`.harness/council-b71-hitl-external-correlation-2026-08-12/DELIVERABLE.md` §5
precondition 3 requires `resolvability` be re-derived so it **cannot assert a false
negative**: a sole pre-dispatch owner IS answerable
(`workflow_driver.py:2895-2897`), so a static `held-for-sole-resolution` stamp would
tell the operator not to reply to the one request whose reply resolves the run.

This module runs the two facts that decide the field's shape, against the real
resolver and the real public projection.

**Fact 1 — resolvability is TIME-VARYING, so no mint-time stamp can carry it.**
`compute_hitl_uniform_fallback_eligible_run_id(root_snapshot, resume_context)` takes
the resume context, and its verdict for one unchanged branch flips with what else has
been addressed. A value minted at escalation time, before the operator has answered
anything, cannot be right at resume time except by luck.

**Fact 2 — the pause view CANNOT answer it either, so "route to the pause view for
live status" is only half an affordance at HEAD.** `project_pause_locations` takes
`root_snapshot` **alone** (`pause_state_projection.py:816`) and `PausedWorkflowState`
(`:403-435`) carries `workflow_id` / `created_at` / `staleness_token` / `locations`
and no resume context at all. The view is *structurally* incapable of computing
eligibility. What it CAN state is the **resolution channel** — the closed 4-value
`PauseLocationVariant` (`:98-116`, CP spec v1.112 §2.1) — which is time-invariant.

Together these say: `resolvability` should carry the **channel**, which is
structurally true and can never become a false negative, and must NOT carry the
**outcome**, which no minter and no reader can know ahead of resume.
"""

from __future__ import annotations

from harness_core.identity import EntryID
from harness_cp.handoff_context import StateSummary
from harness_cp.hitl_placement import HITLResult
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.pause_resume_protocol_types import (
    FanOutBranchResumeState,
    PausedChildBranchResumeState,
    PauseSnapshot,
    PeerFanOutResumeState,
    PreDispatchGateOwningBranchResumeState,
    ResumeContext,
    WorkflowPauseReason,
)
from harness_cp.pause_state_projection import (
    PauseLocationVariant,
    PreDispatchUniformFallbackOnlyLocation,
    project_pause_locations,
)
from harness_cp.workflow_driver import (
    _pre_dispatch_gate_owning_branch_identity,
    compute_hitl_uniform_fallback_eligible_run_id,
)
from harness_is.state_ledger_entry_schema import Identifier

_WF = "wf-b71-resolvability"
_ANCHOR = "0" * 64


def _summary() -> StateSummary:
    return StateSummary(
        relevant_entries=(),
        summary_text="",
        summary_hash="0" * 64,
        idempotency_key=Identifier(""),
        external_references=(),
    )


def _snapshot(
    *,
    run_id: str,
    pause_reason: WorkflowPauseReason = WorkflowPauseReason.HITL_PENDING,
    peer_fan_out_resume: PeerFanOutResumeState | None = None,
) -> PauseSnapshot:
    return PauseSnapshot(
        workflow_id=_WF,
        run_id=run_id,
        step_index=0,
        pause_reason=pause_reason,
        state_summary=_summary(),
        snapshot_hash="f" * 64,
        created_at=0,
        state_ledger_anchor=_ANCHOR,
        peer_fan_out_resume=peer_fan_out_resume,
    )


_ADDRESSABLE_CHILD_RUN_ID = "run-addressable-peer"


def _mixed_tree() -> PauseSnapshot:
    """One PRE-DISPATCH gate-owning branch + one HITL-ADDRESSABLE paused child.

    This mix is what makes the flip observable. Two pre-dispatch peers could not
    show it: a pre-dispatch identity is `never_keyable`, so it counts as unaddressed
    unconditionally (`workflow_driver.py:2890-2894`) and two of them are never
    resolvable. The realistic operator scenario is exactly this mix — "I answered
    the other one; am I now the sole owner?"
    """
    return _snapshot(
        run_id="run-root",
        pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(),
            branch_count=2,
            pre_dispatch_gate_owning_branches=(
                PreDispatchGateOwningBranchResumeState(
                    branch_index=0,
                    step_id="branch-0",
                    step_kind="sub-agent-dispatch",
                    hitl_gate_config_hash="test-hitl-gate-config-hash",
                ),
            ),
            paused_child_branches=(
                PausedChildBranchResumeState(
                    branch_index=1,
                    step_id="worker-1",
                    child_snapshot=_snapshot(run_id=_ADDRESSABLE_CHILD_RUN_ID),
                ),
            ),
        ),
    )


def _result() -> HITLResult:
    return HITLResult(
        response=HITLResponse.APPROVE,
        timestamp="2026-08-12T00:00:00Z",
        audit_ledger_entry_id=EntryID("entry-b71-precondition-3"),
        response_summary_hash="a" * 64,
    )


def _answered(*run_ids: str) -> ResumeContext:
    result = HITLResult(
        response=HITLResponse.APPROVE,
        timestamp="2026-08-12T00:00:00Z",
        audit_ledger_entry_id=EntryID("entry-b71-precondition-3"),
        response_summary_hash="a" * 64,
    )
    return ResumeContext(hitl_responses={rid: result for rid in run_ids})


def test_the_same_branch_flips_from_not_resolvable_to_resolvable() -> None:
    """**Fact 1 — resolvability is time-varying.**

    One unchanged pre-dispatch branch, one unchanged tree, two resume contexts. With
    the peer unanswered there are 2 unaddressed gate-owners, so nobody is eligible.
    Answer the peer and the SAME branch becomes the sole unaddressed owner and IS
    resolvable. A stamp minted at escalation time — before either answer exists —
    would have had to guess which of these is true.
    """
    tree = _mixed_tree()
    pre_dispatch_identity = _pre_dispatch_gate_owning_branch_identity("run-root", 0)

    nothing_answered = compute_hitl_uniform_fallback_eligible_run_id(tree, ResumeContext())
    assert nothing_answered is None, "2 unaddressed gate-owners — the safety rule must refuse"

    peer_answered = compute_hitl_uniform_fallback_eligible_run_id(
        tree, _answered(_ADDRESSABLE_CHILD_RUN_ID)
    )
    assert peer_answered == pre_dispatch_identity, (
        "with its only peer addressed, the pre-dispatch branch IS the sole unaddressed "
        "gate-owner and is NOMINATED as the uniform fallback's target — a static "
        "'held-for-sole-resolution' stamp would be a FALSE NEGATIVE here"
    )


def test_delivery_needs_a_uniform_response_too_which_is_also_unknowable_at_mint() -> None:
    """The claim is ELIGIBILITY, not delivery — and the gap makes the case stronger.

    Out-of-family Codex [P2] was right that an earlier draft overstated this:
    `compute_hitl_uniform_fallback_eligible_run_id` NOMINATES the target, but the
    driver then builds `HITLDeliveryCell(resume_context.hitl_response)`
    (`workflow_driver.py:8350`, `:12674`), so a context carrying only `hitl_responses`
    and no uniform `hitl_response` delivers `None` and the branch re-pauses.

    That is a SECOND input unknowable at escalation time, not a hole in the argument:
    a mint-time stamp would have to predict both which peers get answered AND whether
    the operator supplies a uniform response. Both are witnessed here to vary
    independently of anything the minter can see.
    """
    tree = _mixed_tree()
    identity = _pre_dispatch_gate_owning_branch_identity("run-root", 0)

    keyed_only = _answered(_ADDRESSABLE_CHILD_RUN_ID)
    assert keyed_only.hitl_response is None, (
        "nominated but not deliverable — this context resolves nothing"
    )
    assert compute_hitl_uniform_fallback_eligible_run_id(tree, keyed_only) == identity

    with_uniform = ResumeContext(hitl_responses=keyed_only.hitl_responses, hitl_response=_result())
    assert with_uniform.hitl_response is not None
    assert compute_hitl_uniform_fallback_eligible_run_id(tree, with_uniform) == identity


def test_eligibility_varies_on_an_input_the_projection_has_no_parameter_for() -> None:
    """**Fact 2 — for one journaled record, the view cannot see staged responses.**

    Stated as two independent facts rather than an `x == x` comparison (an earlier
    draft asserted `project_pause_locations(tree) == project_pause_locations(tree)`,
    which is tautological and witnessed nothing — out-of-family Codex [P1]):

    1. eligibility genuinely differs between the two resume contexts, and
    2. the projection's ENTIRE input is the snapshot, which is the same object in
       both — so nothing that changed can reach it.

    Together: no reading of the projection for a given journaled record can
    distinguish "your peer has been answered" from "it has not".
    """
    import inspect

    tree = _mixed_tree()
    without = compute_hitl_uniform_fallback_eligible_run_id(tree, ResumeContext())
    with_peer_answered = compute_hitl_uniform_fallback_eligible_run_id(
        tree, _answered(_ADDRESSABLE_CHILD_RUN_ID)
    )
    assert without != with_peer_answered, "the two scenarios must actually differ"
    assert list(inspect.signature(project_pause_locations).parameters) == ["root_snapshot"], (
        "the projection's sole input is the snapshot — the ResumeContext that "
        "distinguishes the two scenarios above cannot reach it"
    )


def test_a_later_snapshot_would_show_sole_but_is_not_a_liveness_claim() -> None:
    """The counter-hypothesis, evaluated rather than waved off.

    Out-of-family Codex [P1] proposed that Fact 2 fails in production because a
    partial resume journals a NEWER snapshot excluding the resolved peer, so reading
    *that* record would show the pre-dispatch branch as the lone gate-owner. The
    STRUCTURAL half of that is real and is pinned here: a snapshot carrying only the
    pre-dispatch branch projects exactly one gate-owning location.

    What defeats it is the accessor's own ratified contract, not the projection.
    **That contract is CITED here, not executed** (out-of-family Codex): this module
    never invokes `read_paused_workflow_state` or the journal, so a Runtime change that
    began recording resolution would leave these tests green while the ground expired.
    A Runtime round-trip is named as owed at DELIVERABLE §4-ter.4.
    `read_paused_workflow_state` (`harness_runtime/api.py:925`) declares — Runtime
    spec v1.110 §14.14.9.1, the RATIFIED `B-104` Reading D Component 1 — that the
    journal is append-only, writes NO pause-resolved marker, and so returns a record
    that is BYTE-INDISTINGUISHABLE whether or not it has already been resolved. It is
    explicitly "NOT authority for *the workflow is paused right now*, and must not be
    presented to an operator ... as an outstanding-pause assertion". An operator
    reading one gate-owning location therefore cannot conclude they are *currently*
    sole — the record may be stale, and nothing in it says which.
    """
    resolved_peer_tree = _snapshot(
        run_id="run-root",
        pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        peer_fan_out_resume=PeerFanOutResumeState(
            branch_count=2,
            pre_dispatch_gate_owning_branches=(
                PreDispatchGateOwningBranchResumeState(
                    branch_index=0,
                    step_id="branch-0",
                    step_kind="sub-agent-dispatch",
                    hitl_gate_config_hash="test-hitl-gate-config-hash",
                ),
            ),
            # The peer is encoded TERMINAL, not merely absent: an ordinal absent
            # from `branches` is left RE-DISPATCHABLE (`pause_resume_protocol_types
            # .py:592-600`), which would model "branch 1 will run again", not
            # "branch 1 resolved" — out-of-family Codex [P2].
            branches=(
                FanOutBranchResumeState(
                    branch_index=1, step_id="worker-1", terminal_status="completed"
                ),
            ),
            paused_child_branches=(),
        ),
    )
    gate_owning = [
        loc
        for loc in project_pause_locations(resolved_peer_tree)
        if isinstance(loc, PreDispatchUniformFallbackOnlyLocation)
    ]
    assert len(gate_owning) == 1

    # ...and the ORIGINAL record still projects the peer, so the two records are
    # distinguishable from each other — the gap is that the reader cannot know which
    # of them is current.
    assert project_pause_locations(resolved_peer_tree) != project_pause_locations(_mixed_tree())


def test_the_projection_signature_admits_no_resume_context() -> None:
    """The blindness is STRUCTURAL, not an omission at one call site.

    Pinned against the signature so a future arc that wires eligibility into the view
    must come back and re-read precondition 3's disposition rather than silently
    invalidating it.
    """
    import inspect

    params = inspect.signature(project_pause_locations).parameters
    assert list(params) == ["root_snapshot"], (
        "project_pause_locations grew a parameter — if it now takes a ResumeContext, "
        "the pause view may finally be able to report live eligibility, and B-71 "
        "precondition 3's residual sub-fork should be revisited"
    )


def test_the_channel_the_field_should_carry_is_time_invariant_and_already_closed() -> None:
    """The derived shape: carry the CHANNEL, not the OUTCOME.

    `PauseLocationVariant` is a closed 4-value resolution-channel enum (CP spec
    v1.112 §2.1) and the pre-dispatch location already carries
    `UNIFORM_FALLBACK_ONLY`. That value is true at mint and still true at resume, in
    every eligibility state — which is exactly the property precondition 3 demands
    and which no outcome-bearing stamp can have.
    """
    locations = project_pause_locations(_mixed_tree())
    pre_dispatch = [
        loc for loc in locations if isinstance(loc, PreDispatchUniformFallbackOnlyLocation)
    ]
    assert len(pre_dispatch) == 1
    assert pre_dispatch[0].variant is PauseLocationVariant.UNIFORM_FALLBACK_ONLY

    # Invariant across the eligibility flip witnessed above — the whole point.
    assert project_pause_locations(_mixed_tree()) == locations
