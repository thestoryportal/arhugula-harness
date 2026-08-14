"""U-CP-102 — `B-71` branch-distinct escalation correlation carriers (CP half).

Implements the CP-side acceptance criteria of `Implementation_Plan_Control_Plane_v2_53.md`
§0.2 against `Spec_Control_Plane_v1_119.md`.

**Co-land pin, restated so a future reader does not mistake a green run here for a
working mechanism.** U-CP-102 declares the carriers; **U-RT-155** mints into them, folds
the token inside `compose_hitl_action_id`, and projects the webhook keys. Neither unit is
independently observable — carriers with no minter stay `None` forever, and a minter with
no carriers has nothing to write. The Runtime half's witnesses live at
`harness-runtime/tests/test_b71_escalation_token_mint_and_fold_u_rt_155.py`, which is also
where AC 4 (the §0.4.3 three-arm read order) and AC 5 (no echo-vs-recompute comparison)
are witnessed: the resolver those criteria constrain is Runtime-owned, and a witness is
homed by what it must IMPORT, not by which unit's plan lists it.

What is witnessed HERE:

  * AC 1  — the brief's new field, with v1.19's `fail_detail_hash` widening pinned too.
  * AC 2  — both `StepExecutionContext` carriers, `model_copy` inheritance, and the
            UNCONDITIONAL derivation at the live fan-out composition sites.
  * AC 3  — the §26.9 echo, keyed per `branch_index`, no tree-wide index.
  * AC 6  — the pinned digest, as a known-input → known-digest vector.
  * AC 7  — the leak bar, asserted structurally rather than by inspection.
  * AC 8  — the four keys' SOURCE values and their vocabularies (emission is U-RT-155's).
  * AC 9  — ingress is one-way; a matching submitted value is counted-as-unaddressed.
  * AC 10 — byte-identity on the untouched linear/validator population.
  * AC 11 — the minter→snapshot WRITE, and the CARRIED-FORWARD preservation.
  * AC 12 — a legacy durable snapshot still resumes, with an unchanged hash.
  * AC 13 — the public projection carries the token.
  * AC 14 — the validator trust seam OVERWRITES rather than merely ignoring.
  * AC 15 — the projection OMITS the field when `None`, never emits `null`.
  * AC 16 — the diagnostic half, on the channel that exists.
"""

from __future__ import annotations

import asyncio
import hashlib
import warnings
from typing import Any, cast

import pytest
from harness_core import EntryID, PersonaTier, StepID, WorkloadClass
from harness_core.workflow_event_class import WorkflowEventClass
from harness_cp.cp_shared_types import AgentRole, ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.gate_level_rule import GateLevel
from harness_cp.handoff_context import StateSummary
from harness_cp.hitl_placement import HITLPlacement, HITLPlacementKind, HITLResult
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.pause_resume_protocol import (
    PauseResumeProtocol,
    _compute_snapshot_hash,
    _strip_default_fanout_resume_fields,
)
from harness_cp.pause_resume_protocol_types import (
    PauseSnapshot,
    PeerFanOutResumeState,
    PreDispatchGateOwningBranchResumeState,
    WorkflowPauseReason,
)
from harness_cp.pause_state_projection import (
    AccessorDerivedResumeContext,
    EscalationTokenKeyedIngressWarning,
    PausedWorkflowState,
    PauseLocationVariant,
    PreDispatchUniformFallbackOnlyLocation,
    compose_escalation_instance_id,
    pre_dispatch_gate_owning_branch_identity,
    walk_pause_tree,
)
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.validator_framework_types import HITLEscalationBrief
from harness_cp.workflow_driver import (
    DriverContext,
    StepDispatcher,
    StepDispatcherRegistry,
    execute_workflow,
)
from harness_cp.workflow_driver_types import (
    RunStatus,
    StepExecutionContext,
    StepKind,
    WorkflowStep,
    compose_branch_child_context,
)
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier

_DEFAULT_BINDING = ModelBinding(provider="anthropic", model="claude-haiku-4-5")
_CHAIN = FallbackChain(
    primary=ProviderCandidate(
        provider="anthropic", model="claude-haiku-4-5", family=ProviderFamily.ANTHROPIC
    ),
    same_family=(),
    cross_family=(),
    terminal=None,
)
_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-b71-u-cp-102")
_PAUSE_TIER = PersonaTier.TEAM_BINDING  # → cascade_policy = pause
_ANCHOR = "0" * 64
_RUN_ID = "run-b71-1"
_PLACEMENT = HITLPlacement(position=HITLPlacementKind.SUB_AGENT_BOUNDARY)


# ---------------------------------------------------------------------------
# Fixtures — the real driver, exercised through `execute_workflow`
# ---------------------------------------------------------------------------


class HITLPauseRequestedSignal(BaseException):
    """Test-local stand-in for the runtime signal, name-matched by the driver.

    `harness-cp` cannot import `harness-runtime`, so the driver matches this signal
    BY TYPE NAME; every CP-side fan-out pause test in this workspace declares the
    same stand-in. This one additionally carries a `brief`, because the §26.9 WRITER
    row's whole content is "the producer copies the token off the signal's brief".
    """

    def __init__(self, brief: HITLEscalationBrief | None = None) -> None:
        super().__init__("HITL durable-async pause requested")
        self.brief = brief


def _manifest(workflow_id: str = "wf-b71") -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=_PAUSE_TIER,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=TopologyPattern.PARALLELIZATION,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


def _peer_steps() -> list[WorkflowStep]:
    """Two peers dispatching the SAME `child_workflow_id` — the `B-71` shape.

    This is the §0.1 defect population verbatim: both peers escalate before any
    child run exists, so no dispatched-child `run_id` can discriminate them.
    """
    return [
        WorkflowStep(
            step_id=StepID("branch-0-sub"),
            step_kind=StepKind.SUB_AGENT_DISPATCH,
            step_payload={"child_workflow_id": "wf-child-shared"},
        ),
        WorkflowStep(
            step_id=StepID("branch-1-sub"),
            step_kind=StepKind.SUB_AGENT_DISPATCH,
            step_payload={"child_workflow_id": "wf-child-shared"},
        ),
    ]


class _RecordingLedger:
    actor: Actor

    def __init__(self) -> None:
        self.actor = _ACTOR
        self.appends: list[tuple[Any, Any]] = []

    def append(self, payload: Any, write_key: Any) -> Any:
        self.appends.append((payload, write_key))
        return "appended"

    @property
    def is_genesis(self) -> bool:
        return len(self.appends) == 0

    @property
    def entry_count(self) -> int:
        return len(self.appends)


class _Emitter:
    def __init__(self) -> None:
        self.emits: list[WorkflowEventClass] = []

    def emit(self, event_class: WorkflowEventClass) -> None:
        self.emits.append(event_class)


def _pause_context_reader() -> tuple[StateSummary, str]:
    return (
        StateSummary(
            relevant_entries=(),
            summary_text="",
            summary_hash="0" * 64,
            idempotency_key=Identifier(""),
            external_references=(),
        ),
        _ANCHOR,
    )


class _CtxP:
    def __init__(self) -> None:
        from opentelemetry.trace import NoOpTracerProvider

        self.ledger_writer = _RecordingLedger()
        self.lifecycle_emitter = _Emitter()
        self.drained_flag = asyncio.Event()
        self.pause_requested_flag = asyncio.Event()
        self.pause_resume_protocol = PauseResumeProtocol(
            state_ledger_writer=object(),
            state_ledger_reader=object(),
            pause_context_reader=_pause_context_reader,
        )
        self.ledger_reader = None
        self.tracer_provider = NoOpTracerProvider()
        self.validator_framework = None
        self.tenant_id = None


def _ctx() -> DriverContext:
    return cast(DriverContext, _CtxP())


class _MintingGateDispatcher:
    """Stands in for the U-RT-155 minter, on the CP side of the seam.

    Reads `pre_dispatch_escalation_basis` off the `StepExecutionContext` the driver
    just composed and mints per §0.4(2) — i.e. it does exactly what the real Runtime
    composer's step 1 does, using the same CP-owned digest function. Every context it
    sees is recorded, so a test can assert what the driver actually produced rather
    than what it is assumed to produce.
    """

    def __init__(self) -> None:
        self.contexts: list[StepExecutionContext] = []
        self.dispatched: list[str] = []
        self.minted: dict[int, str] = {}

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        return cast(StepDispatcher, self)

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        self.dispatched.append(str(step.step_id))
        ctx = cast(StepExecutionContext, step_context)
        self.contexts.append(ctx)
        persisted = ctx.pre_dispatch_escalation_instance_id
        basis = ctx.pre_dispatch_escalation_basis
        if persisted is not None:
            token = persisted
        elif basis is not None:
            token = compose_escalation_instance_id(basis, _PLACEMENT.position)
        else:
            raise HITLPauseRequestedSignal()
        if ctx.branch_index is not None:
            self.minted[ctx.branch_index] = token
        raise HITLPauseRequestedSignal(
            HITLEscalationBrief(
                parent_step_id=str(step.step_id),
                parent_action_id=str(ctx.parent_action_id),
                escalation_reason="durable_async_cell_synchrony",
                escalation_instance_id=token,
            )
        )


class _WarmupCohortMintingDispatcher(_MintingGateDispatcher):
    """The §25.19 warm-up split: the lower ordinal leads Phase 1 and re-pauses, so
    the follower is WITHHELD entirely and never reaches `dispatch()` this round.

    This is the ONLY shape that reaches §0.4.2's CARRIED-FORWARD clause — the
    snapshot builders reconstruct the withheld ordinal's row with no new brief in
    hand. Copied in shape from
    `test_workflow_driver_parallelization_pause.py::_WarmupCohortLeaderGateDispatcher`.
    """

    def cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None:
        return "b71-warmup-cohort" if step.step_kind is StepKind.SUB_AGENT_DISPATCH else None


def _round_one() -> tuple[PauseSnapshot, _MintingGateDispatcher]:
    """Round 1: both peers escalate pre-dispatch and the run PAUSES."""
    dispatcher = _MintingGateDispatcher()
    paused = execute_workflow(
        _manifest(),
        _peer_steps(),
        run_id=_RUN_ID,
        ctx=_ctx(),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, dispatcher),
    )
    assert paused.status is RunStatus.PAUSED
    snap = paused.pause_snapshot
    assert snap is not None
    assert snap.peer_fan_out_resume is not None
    return snap, dispatcher


def _bare_context(branch_index: int | None = None) -> StepExecutionContext:
    from harness_as.sandbox_tier import SandboxTier

    return StepExecutionContext(
        workflow_id="wf-b71",
        parent_action_id="workflow:wf-b71:step:0",
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=_ACTOR,
        parent_entry_hash="",
        parent_idempotency_key=Identifier("b71-key"),
        tenant_id=None,
        step_index=0,
        branch_index=branch_index,
    )


# ---------------------------------------------------------------------------
# AC 1 — the brief's new field, and v1.19's widening carried forward
# ---------------------------------------------------------------------------


def test_the_brief_declares_the_token_and_preserves_v1_19s_optional_fail_detail_hash() -> None:
    """§25.2.Z composes over v1.19 §25.2.Y.1, NOT over v1.18.

    Both halves are pinned in ONE witness deliberately: a draft of the spec leg
    composed over v1.18 and silently REGRESSED `fail_detail_hash` back to a required
    `str`. Asserting only the new field would have let that regression ship green.
    """
    brief = HITLEscalationBrief(parent_step_id="s", parent_action_id="a", escalation_reason="r")
    assert brief.escalation_instance_id is None, "the field is Optional and None-defaulted"
    assert brief.fail_detail_hash is None, (
        "v1.19's `fail_detail_hash: str | None` widening MUST survive §25.2.Z — a "
        "re-required `str` here is the exact regression review caught on the draft"
    )
    assert brief.fail_class is None, "v1.18 §25.2.X.1's widening survives too"
    carried = brief.model_copy(update={"escalation_instance_id": "t"})
    assert carried.escalation_instance_id == "t"


# ---------------------------------------------------------------------------
# AC 2 — the two `StepExecutionContext` carriers
# ---------------------------------------------------------------------------


def test_both_context_carriers_default_to_none_and_survive_model_copy() -> None:
    ctx = _bare_context()
    assert ctx.pre_dispatch_escalation_basis is None
    assert ctx.pre_dispatch_escalation_instance_id is None
    updated = ctx.model_copy(
        update={
            "pre_dispatch_escalation_basis": "run-x:pre-dispatch-gate:3",
            "pre_dispatch_escalation_instance_id": "a" * 64,
        }
    )
    assert updated.pre_dispatch_escalation_basis == "run-x:pre-dispatch-gate:3"
    assert updated.pre_dispatch_escalation_instance_id == "a" * 64


def test_a_branch_child_inherits_both_fields_and_never_re_derives_them() -> None:
    """`compose_branch_child_context` must not RESET or RECOMPUTE either field.

    §0.4.1 / §0.4.3 both say "inherited by `model_copy` ...; a branch child never
    re-derives it". The composer deliberately resets several other carriers
    (`hitl_delivery_holder`, `is_orchestrator_dispatch`, ...); these two are not
    among them, and a future reset would silently blank the basis for every nested
    fan-out worker.
    """
    parent = _bare_context().model_copy(
        update={
            "pre_dispatch_escalation_basis": "run-parent:pre-dispatch-gate:0",
            "pre_dispatch_escalation_instance_id": "b" * 64,
        }
    )
    child = compose_branch_child_context(parent, branch_index=2, agent_role=AgentRole("w"))
    assert child.pre_dispatch_escalation_basis == "run-parent:pre-dispatch-gate:0"
    assert child.pre_dispatch_escalation_instance_id == "b" * 64


# mutation-probe: re-guard the basis derivation in `_execute_parallelization`'s
# branch loop behind `branch_index in _recovered_pre_dispatch_gate_owning and
# resume_context is not None` (i.e. put it back inside the `_branch_hitl_delivery_cell`
# condition), so a FIRST escalation sees `pre_dispatch_escalation_basis is None`.
def test_the_basis_is_derived_on_a_first_non_resume_escalation() -> None:
    """The criterion the whole mechanism hangs on (§0.4.1's correction note).

    Both live composition sites previously computed this identity only inside
    `not _any_fence_abort and branch_index in _recovered_pre_dispatch_gate_owning and
    resume_context is not None` — the RESUME path with a recovered gate-owner. On a
    FIRST, non-resume fan-out escalation the identity was never computed at all, so
    a guarded derivation leaves the basis `None`, mints no token, and lets two peers
    collide **on exactly the path `B-71` exists to fix** — while every other
    criterion in this file still passes.
    """
    _snap, dispatcher = _round_one()
    assert len(dispatcher.contexts) == 2, "both peers must have been dispatched"
    for ctx in dispatcher.contexts:
        assert ctx.branch_index is not None
        assert ctx.pre_dispatch_escalation_basis == pre_dispatch_gate_owning_branch_identity(
            _RUN_ID, ctx.branch_index
        ), (
            "the basis MUST be derived unconditionally on a first, non-resume "
            "escalation — a guarded derivation is inert on the defect's own path"
        )
        assert ctx.pre_dispatch_escalation_instance_id is None, (
            "nothing is persisted on a FIRST escalation, so the echo is None by "
            "construction and the minter takes the compute arm"
        )
    assert len(set(dispatcher.minted.values())) == 2, (
        "the two peers must mint DISTINCT tokens — this is the §0.1 defect closing"
    )


# ---------------------------------------------------------------------------
# AC 6 — the pinned digest
# ---------------------------------------------------------------------------


# mutation-probe: change the domain separator literal
# `_ESCALATION_INSTANCE_DOMAIN_SEPARATOR` by one byte (e.g. drop the trailing ":").
def test_the_digest_matches_the_pinned_known_input_vector() -> None:
    """§0.4(2) is a CONTRACT surface, so it is pinned by VECTOR, not by re-derivation.

    Recomputing the formula inside the assertion would make this test agree with any
    implementation, including a drifted one. The expected value below is written out
    from the spec's own formula so an encoding, separator or ordering change reddens.
    """
    basis = "run-root-0001:pre-dispatch-gate:0"
    expected = hashlib.sha256(
        b"hitl-escalation-instance:run-root-0001:pre-dispatch-gate:0:sub-agent-boundary"
    ).hexdigest()
    assert compose_escalation_instance_id(basis, HITLPlacementKind.SUB_AGENT_BOUNDARY) == expected
    assert len(expected) == 64, "sha256 hex, never truncated (§0.4(1)'s ≥128-bit bar)"
    assert expected == expected.lower(), "lowercase hex"
    assert HITLPlacementKind.SUB_AGENT_BOUNDARY.value == "sub-agent-boundary", (
        "the digest hashes the enum's string VALUE, not its member name — pinned "
        "here so a value rename cannot silently rotate every live token"
    )


def test_the_digest_separates_peers_and_positions() -> None:
    a = compose_escalation_instance_id(
        pre_dispatch_gate_owning_branch_identity(_RUN_ID, 0), HITLPlacementKind.SUB_AGENT_BOUNDARY
    )
    b = compose_escalation_instance_id(
        pre_dispatch_gate_owning_branch_identity(_RUN_ID, 1), HITLPlacementKind.SUB_AGENT_BOUNDARY
    )
    c = compose_escalation_instance_id(
        pre_dispatch_gate_owning_branch_identity(_RUN_ID, 0), HITLPlacementKind.PRE_ACTION
    )
    assert len({a, b, c}) == 3, "(branch × placement POSITION) is the guaranteed unit"
    assert (
        compose_escalation_instance_id(
            pre_dispatch_gate_owning_branch_identity("run-other", 0),
            HITLPlacementKind.SUB_AGENT_BOUNDARY,
        )
        != a
    ), "two runs never share a token"


# ---------------------------------------------------------------------------
# AC 3 + AC 11 — the §26.9 echo: keyed per branch, WRITTEN, and CARRIED FORWARD
# ---------------------------------------------------------------------------


def test_the_resume_state_row_keys_the_echo_by_branch_index_only() -> None:
    """§26.9 keying row: the existing `branch_index` within its containing snapshot
    is the key, and NO tree-wide index is introduced."""
    row = PreDispatchGateOwningBranchResumeState(
        branch_index=1, step_id="s", step_kind="sub-agent-dispatch"
    )
    assert row.escalation_instance_id is None, "`None` means NOT YET PERSISTED (§0.8)"
    fields = set(type(row).model_fields)
    assert fields == {
        "branch_index",
        "step_id",
        "step_kind",
        "child_workflow_id",
        "hitl_gate_config_hash",
        "escalation_instance_id",
    }, (
        "exactly ONE additive field; any tree-wide index would show up here and would "
        f"be a second scoping authority beside the containing snapshot — got {fields!r}"
    )


# mutation-probe: delete the `escalation_instance_id=(pre_dispatch_gate_owning_tokens.get(_bi)
# or _recovered_pre_dispatch_gate_owning_tokens.get(_bi))` line from
# `_execute_parallelization`'s `pre_dispatch_gate_owning_branches=tuple(...)` builder.
def test_the_minted_token_is_written_into_the_snapshot_echo() -> None:
    """The WRITE half of persist-once, witnessed END TO END: escalate, then read the
    snapshot back and assert the echo equals the delivered token.

    Without this the field is DECLARED and NEVER POPULATED — every resume finds
    `None`, takes the recompute arm, and §0.4.3's echo arm is unreachable in
    production even though its unit test passes.
    """
    snap, dispatcher = _round_one()
    pfr = snap.peer_fan_out_resume
    assert pfr is not None
    rows = {row.branch_index: row for row in pfr.pre_dispatch_gate_owning_branches}
    assert set(rows) == {0, 1}
    for branch_index, row in rows.items():
        assert row.escalation_instance_id == dispatcher.minted[branch_index], (
            "the snapshot's echo must equal the token the escalation actually "
            f"delivered for branch {branch_index}"
        )
    assert rows[0].escalation_instance_id != rows[1].escalation_instance_id


# mutation-probe: drop the `or _recovered_pre_dispatch_gate_owning_tokens.get(_bi)` arm
# from BOTH snapshot builders, so a carried-forward row rebuilds its echo as `None`.
def test_a_carried_forward_row_preserves_its_echo_rather_than_resetting_it() -> None:
    """§0.4.2's CARRIED-FORWARD clause, on the real §25.19 warm-up path.

    A withheld gate-owning branch is reconstructed from the carried-forward set with
    NO new brief in hand. A reconstruction that defaulted the field would silently
    reset a persisted token, and the next resume would recompute in defiance of
    §0.4(5) — **rotating the key of an escalation the operator is still holding.**
    Witnessing only mint-to-first-snapshot misses this entirely.
    """
    snap, round_one = _round_one()
    pfr = snap.peer_fan_out_resume
    assert pfr is not None
    carried_token = next(
        row.escalation_instance_id
        for row in pfr.pre_dispatch_gate_owning_branches
        if row.branch_index == 1
    )
    assert carried_token is not None

    resume_dispatcher = _WarmupCohortMintingDispatcher()
    resumed = execute_workflow(
        _manifest(),
        _peer_steps(),
        run_id=_RUN_ID,
        ctx=_ctx(),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, resume_dispatcher),
        pause_snapshot_input=snap,
    )
    assert resume_dispatcher.dispatched == ["branch-0-sub"], (
        "branch-1-sub must be GENUINELY withheld by the warm-up split — otherwise "
        f"this test is not exercising the carried-forward path at all; got "
        f"{resume_dispatcher.dispatched!r}"
    )
    assert resumed.status is RunStatus.PAUSED
    resumed_snap = resumed.pause_snapshot
    assert resumed_snap is not None
    resumed_pfr = resumed_snap.peer_fan_out_resume
    assert resumed_pfr is not None
    carried_row = next(
        row for row in resumed_pfr.pre_dispatch_gate_owning_branches if row.branch_index == 1
    )
    assert carried_row.escalation_instance_id == carried_token, (
        "the withheld branch's PRIOR token must be copied forward verbatim; a reset "
        "to None rotates the key of a gate the operator is still holding"
    )
    assert round_one.minted[1] == carried_token


def test_a_resumed_branch_reads_its_persisted_echo_back_onto_the_context() -> None:
    """§25.21's producer: the resume-side composition site copies the §26.9 echo
    onto `StepExecutionContext.pre_dispatch_escalation_instance_id` VERBATIM.

    Without this the echo lives on a carrier the READER never consults and §0.4.2's
    "MUST use it and MUST NOT recompute" is unsatisfiable rather than merely
    unimplemented.
    """
    snap, round_one = _round_one()
    resume_dispatcher = _MintingGateDispatcher()
    execute_workflow(
        _manifest(),
        _peer_steps(),
        run_id=_RUN_ID,
        ctx=_ctx(),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, resume_dispatcher),
        pause_snapshot_input=snap,
    )
    seen = {
        ctx.branch_index: ctx.pre_dispatch_escalation_instance_id
        for ctx in resume_dispatcher.contexts
    }
    assert seen, "the resume must have re-dispatched at least one recovered branch"
    for branch_index, echo in seen.items():
        assert branch_index is not None
        assert echo == round_one.minted[branch_index], (
            "the resumed branch context must carry the PERSISTED token, not a "
            f"recomputed one, for branch {branch_index}"
        )


# ---------------------------------------------------------------------------
# AC 12 — legacy durable snapshots
# ---------------------------------------------------------------------------


# mutation-probe: delete the `if pg_dict.get("escalation_instance_id") is None:
# pg_dict.pop(...)` block from `_strip_default_fanout_resume_fields`.
def test_a_legacy_row_drops_the_absent_field_from_the_hashed_dump() -> None:
    """§26.9's compatibility clause, mirroring the `hitl_gate_config_hash` precedent.

    A durable snapshot captured by the PRECEDING deployment carries this row with the
    key ABSENT. `model_dump` emits `null` for it; unstripped, that changes the
    recomputed `snapshot_hash` and a legitimate pre-upgrade snapshot is **rejected as
    corrupt** on resume after upgrade. Asserting only that NEW snapshots round-trip
    would miss this entirely.
    """
    carrier_dump: dict[str, Any] = {
        "branches": [],
        "synthesis_step_id": None,
        "effect_fence_paused_branches": [],
        "pre_dispatch_gate_owning_branches": [
            {
                "branch_index": 1,
                "step_id": "branch-1-sub",
                "step_kind": "sub-agent-dispatch",
                "child_workflow_id": None,
                "hitl_gate_config_hash": None,
                "escalation_instance_id": None,
            }
        ],
    }
    _strip_default_fanout_resume_fields(carrier_dump)
    row = carrier_dump["pre_dispatch_gate_owning_branches"][0]
    assert "escalation_instance_id" not in row, (
        f"a legacy row's None escalation_instance_id must be stripped; got {row!r}"
    )


def _legacy_canonical_hash(state_summary: StateSummary, row: dict[str, Any]) -> str:
    """The hash the PRECEDING deployment produced, computed from its OWN row shape.

    Written out rather than obtained from the live code, because a witness that asked
    today's `_compute_snapshot_hash` for "the legacy value" would agree with any
    implementation, including one that stopped stripping. The recipe (sorted-key
    compact JSON over the same canonical keys, sha256 hex) is
    `pause_resume_protocol._compute_snapshot_hash`'s, and `row` is the pre-upgrade
    JSON — with NO `escalation_instance_id` key at all.
    """
    import json

    canonical: dict[str, object] = {
        "workflow_id": "wf-b71",
        "run_id": _RUN_ID,
        "step_index": 0,
        "state_summary": state_summary.model_dump(mode="json"),
        "peer_fan_out_resume": {
            "branches": [],
            "branch_count": 2,
            "pre_dispatch_gate_owning_branches": [row],
        },
    }
    return hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


# mutation-probe: delete the `if pg_dict.get("escalation_instance_id") is None:
# pg_dict.pop(...)` block from `_strip_default_fanout_resume_fields` (same mutation as
# the row-level probe above — this test is the SNAPSHOT-HASH consequence of it, which
# the row-level assertion alone does not reach).
def test_a_pre_upgrade_snapshot_re_hashes_to_its_original_value() -> None:
    """The compatibility clause's real consequence: a legitimate durable snapshot
    captured BEFORE this field existed must still validate after upgrade.

    Asserting only that NEW snapshots round-trip would miss this entirely — the
    failure being closed is that a legitimate pre-upgrade snapshot is REJECTED AS
    CORRUPT because its recomputed hash moved.
    """
    state_summary = _pause_context_reader()[0]
    legacy_row = {
        "branch_index": 1,
        "step_id": "branch-1-sub",
        "step_kind": "sub-agent-dispatch",
        "child_workflow_id": "wf-child-shared",
        "hitl_gate_config_hash": "a" * 64,
    }
    expected = _legacy_canonical_hash(state_summary, legacy_row)

    upgraded = PeerFanOutResumeState(
        branches=(),
        branch_count=2,
        pre_dispatch_gate_owning_branches=(
            PreDispatchGateOwningBranchResumeState(
                branch_index=1,
                step_id="branch-1-sub",
                step_kind=StepKind.SUB_AGENT_DISPATCH.value,
                child_workflow_id="wf-child-shared",
                hitl_gate_config_hash="a" * 64,
            ),
        ),
    )
    assert upgraded.pre_dispatch_gate_owning_branches[0].escalation_instance_id is None
    recomputed = _compute_snapshot_hash(
        workflow_id="wf-b71",
        run_id=_RUN_ID,
        step_index=0,
        state_summary=state_summary,
        peer_fan_out_resume=upgraded,
    )
    assert recomputed == expected, (
        "the new deployment must re-hash a pre-upgrade pre-dispatch row to the value "
        "the OLD deployment produced; an unstripped `escalation_instance_id: null` "
        "rejects a legitimate snapshot as corrupt"
    )


def test_a_recovered_row_without_an_echo_takes_the_recompute_arm() -> None:
    """§26.9's absence row: `None` means NOT YET PERSISTED and licenses the
    deterministic recompute — never a fresh mint, and never a refusal to resume."""
    snap, _ = _round_one()
    pfr = snap.peer_fan_out_resume
    assert pfr is not None
    stripped = pfr.model_copy(
        update={
            "pre_dispatch_gate_owning_branches": tuple(
                row.model_copy(update={"escalation_instance_id": None})
                for row in pfr.pre_dispatch_gate_owning_branches
            )
        }
    )
    # The snapshot hash COVERS a present token (verified: omitting this recompute
    # makes the resume fail `CP-FAIL-PAUSE-SNAPSHOT-CORRUPTION`, which is the
    # tamper-detection working). A genuine pre-upgrade snapshot never had the token in
    # the first place, so its hash is the one computed over the stripped shape.
    legacy = snap.model_copy(
        update={
            "peer_fan_out_resume": stripped,
            "snapshot_hash": _compute_snapshot_hash(
                workflow_id=snap.workflow_id,
                run_id=snap.run_id,
                step_index=snap.step_index,
                state_summary=snap.state_summary,
                peer_fan_out_resume=stripped,
            ),
        }
    )
    resume_dispatcher = _MintingGateDispatcher()
    resumed = execute_workflow(
        _manifest(),
        _peer_steps(),
        run_id=_RUN_ID,
        ctx=_ctx(),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, resume_dispatcher),
        pause_snapshot_input=legacy,
    )
    assert resumed.status is RunStatus.PAUSED, (
        "a legitimate pre-upgrade snapshot must RESUME, not be rejected as corrupt; "
        f"got status={resumed.status!r} fail_class={resumed.fail_class!r}"
    )
    assert resume_dispatcher.minted, (
        "a recovered branch with no persisted echo must reach the RECOMPUTE arm"
    )
    for branch_index, token in resume_dispatcher.minted.items():
        assert token == compose_escalation_instance_id(
            pre_dispatch_gate_owning_branch_identity(_RUN_ID, branch_index),
            _PLACEMENT.position,
        ), "the recompute is DETERMINISTIC — it reproduces the original token"


# ---------------------------------------------------------------------------
# AC 13 + AC 15 — the public projection
# ---------------------------------------------------------------------------


def _projected(snapshot: PauseSnapshot) -> PreDispatchUniformFallbackOnlyLocation:
    locations = [
        entry.projection
        for entry in walk_pause_tree(snapshot)
        if isinstance(entry.projection, PreDispatchUniformFallbackOnlyLocation)
    ]
    assert locations, "no pre-dispatch gate-owning location was projected at all"
    return locations[0]


def test_the_projection_carries_the_persisted_token() -> None:
    """§2.2.A — ONE value, three surfaces. This witnesses two of them agreeing
    (the resume state and the projection); the third (the webhook) is asserted in
    the U-RT-155 record, which is where the adapter lives.
    """
    snap, dispatcher = _round_one()
    location = _projected(snap)
    assert location.escalation_instance_id == dispatcher.minted[location.branch_index]
    assert location.escalation_instance_id is not None
    assert _RUN_ID not in location.escalation_instance_id, (
        "v1.112 §2.2 constraint 2 still holds verbatim — only the HASHED token "
        "appears here, never the internal identity"
    )


# mutation-probe: delete the `_omit_absent_escalation_instance_id` model serializer
# from `PreDispatchUniformFallbackOnlyLocation` (so pydantic emits `null`).
def test_the_projection_omits_the_field_when_absent_rather_than_emitting_null() -> None:
    """§2.2.A's absence row, witnessed against a pre-field snapshot's projected BYTES.

    AC 13 checks value agreement and leakage; AC 12 covers the RESUME-STATE hash.
    Neither covers the PROJECTION's wire shape, so without this an implementation
    satisfies every other criterion while breaking the legacy projection bytes the
    spec promises.
    """
    legacy = PreDispatchUniformFallbackOnlyLocation(
        pause_reason=WorkflowPauseReason.HITL_PENDING,
        step_index=0,
        step_id="branch-1-sub",
        step_kind=StepKind.SUB_AGENT_DISPATCH,
        branch_index=1,
    )
    dumped = legacy.model_dump(mode="json")
    assert "escalation_instance_id" not in dumped, (
        f"absent means OMITTED, not `null` — got {dumped!r}"
    )
    present = legacy.model_copy(update={"escalation_instance_id": "c" * 64})
    assert present.model_dump(mode="json")["escalation_instance_id"] == "c" * 64, (
        "a PRESENT token must still be emitted verbatim — the drop is None-only"
    )


# ---------------------------------------------------------------------------
# AC 7 + AC 10 — the leak bar, and byte-identity on the untouched population
# ---------------------------------------------------------------------------


def test_no_basis_material_rides_the_brief_when_the_token_is_present() -> None:
    """§0.5, asserted STRUCTURALLY rather than by inspection.

    The token is a one-way digest of material that contains a `run_id` VERBATIM, and
    the composed key rides the OD-canonical `hitl.webhook.deliver` span — so a
    regression that carried the basis instead of its digest would export a real run
    identity over tracing. This asserts absence over the brief's whole serialized
    form, not over a field list someone remembered to check.
    """
    basis = pre_dispatch_gate_owning_branch_identity(_RUN_ID, 0)
    brief = HITLEscalationBrief(
        parent_step_id="branch-0-sub",
        parent_action_id="workflow:wf-b71:step:0",
        escalation_reason="durable_async_cell_synchrony",
        escalation_instance_id=compose_escalation_instance_id(basis, _PLACEMENT.position),
    )
    serialized = repr(brief.model_dump(mode="json"))
    assert _RUN_ID not in serialized, "no `snapshot_run_id` on any brief field"
    assert basis not in serialized, "no un-hashed pre-dispatch identity"
    assert "pre-dispatch-gate" not in serialized, "no `run_id`-shaped basis fragment"


# mutation-probe: in the two snapshot builders, replace the token expression with a
# constant string (e.g. `escalation_instance_id="x" * 64`) so the field is populated
# on populations that mint nothing.
def test_the_linear_validator_population_is_byte_identical_to_pre_arc() -> None:
    """§0.12, witnessed by COMPARISON against a pre-arc fixture, not by asserting the
    absence of a key.

    A signal carrying no brief is the linear/validator shape; its snapshot row must
    dump exactly as it did before this delta.
    """

    class _NoBriefDispatcher(_MintingGateDispatcher):
        def dispatch(
            self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
        ) -> dict[str, Any]:
            self.dispatched.append(str(step.step_id))
            raise HITLPauseRequestedSignal()

    paused = execute_workflow(
        _manifest(),
        _peer_steps(),
        run_id=_RUN_ID,
        ctx=_ctx(),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _NoBriefDispatcher()),
    )
    snap = paused.pause_snapshot
    assert snap is not None and snap.peer_fan_out_resume is not None
    dumped = snap.peer_fan_out_resume.model_dump(mode="json")
    _strip_default_fanout_resume_fields(dumped)
    row = dumped["pre_dispatch_gate_owning_branches"][0]
    # The pre-arc fixture, key by key. `hitl_gate_config_hash` is B-79's field and is
    # NOT under test here, so its value is read from the row rather than restated as a
    # literal digest that unrelated placement work would have to keep updating — but
    # its PRESENCE is pinned, so this fixture is a full-shape comparison and not a
    # subset check that a new key could slip past.
    pre_arc_row = {
        "branch_index": 0,
        "step_id": "branch-0-sub",
        "step_kind": "sub-agent-dispatch",
        "child_workflow_id": "wf-child-shared",
        "hitl_gate_config_hash": row.get("hitl_gate_config_hash"),
    }
    assert row == pre_arc_row, (
        "the untouched population's hashed row must be byte-identical to the "
        f"pre-arc fixture; got {row!r}"
    )
    assert isinstance(pre_arc_row["hitl_gate_config_hash"], str), (
        "sanity: B-79's field really is present on this row, so the comparison above "
        "is a full-shape one"
    )


# ---------------------------------------------------------------------------
# AC 8 — the four keys' SOURCE values and vocabularies (emission is U-RT-155's)
# ---------------------------------------------------------------------------


def test_resolvability_reuses_the_closed_pause_location_vocabulary() -> None:
    """§0.6: NO new vocabulary is minted. `resolvability` draws from the CLOSED
    `PauseLocationVariant` enumeration the pause view already assigns, so the webhook
    and the pause view cannot become two authorities over one concept.
    """
    assert PauseLocationVariant.UNIFORM_FALLBACK_ONLY.value == "uniform-fallback-only"
    assert {v.value for v in PauseLocationVariant} == {
        "hitl-addressable",
        "effect-fence-addressable",
        "uniform-fallback-only",
        "transitively-paused",
    }, "the vocabulary is CLOSED at four members; this delta mints none"
    snap, _ = _round_one()
    assert _projected(snap).variant is PauseLocationVariant.UNIFORM_FALLBACK_ONLY, (
        "the value a `B-71` escalation stamps is the one the pause view assigns to "
        "the same location — one concept, one authority"
    )


def test_the_palette_is_preserved_and_not_suppressed() -> None:
    """§0.6.1 — the palette-suppression binding is WITHDRAWN and MUST NOT be
    implemented. A time-INVARIANT channel cannot disarm a time-VARYING harm, and
    suppressing the palette in both states would hide a VALID uniform action in the
    sole-owner state.
    """
    brief = HITLEscalationBrief(
        parent_step_id="s",
        parent_action_id="a",
        escalation_reason="r",
        escalation_instance_id="d" * 64,
    )
    assert brief.proposed_response_palette == frozenset(HITLResponse), (
        "the full 4-response palette is preserved verbatim even when a token is "
        "present — suppression is explicitly forbidden"
    )


# ---------------------------------------------------------------------------
# AC 14 + AC 16 — the validator trust seam, and the diagnostic half
# ---------------------------------------------------------------------------


class _EscalatingValidatorFramework:
    """A validator that escalates with a HOSTILE `escalation_instance_id` set.

    `ValidatorResult.escalation_brief` is a second CONSTRUCTOR of the brief type but
    never a MINTER of the field (§0.4(3)); an operator-authored validator setting it
    is exactly the trust-seam case.
    """

    def __init__(self, supplied: str | None) -> None:
        self.supplied = supplied
        self.seen: list[HITLEscalationBrief] = []

    def evaluate(self, step: Any, step_result: Any, *, step_context: Any) -> Any:
        from harness_cp.validator_framework_types import (
            ValidatorEvaluation,
            ValidatorNextAction,
            ValidatorOutcome,
            ValidatorResult,
        )

        brief = HITLEscalationBrief(
            parent_step_id=str(step.step_id),
            parent_action_id=str(step_context.parent_action_id),
            escalation_reason="operator-authored",
            escalation_instance_id=self.supplied,
        )
        self.seen.append(brief)
        return ValidatorEvaluation(
            result=ValidatorResult(outcome=ValidatorOutcome.ESCALATE, escalation_brief=brief),
            span_attributes={},
            next_action=ValidatorNextAction.ESCALATE_HITL,
            burden_count=1,
        )


def _run_validator_escalation(
    supplied: str | None,
) -> tuple[_EscalatingValidatorFramework, list[Any]]:
    """Drive one LINEAR run whose validator ESCALATES, capturing the exported spans."""
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))

    framework = _EscalatingValidatorFramework(supplied)
    ctx = cast(Any, _CtxP())
    ctx.validator_framework = framework
    ctx.tracer_provider = provider
    # The composer is deliberately UNBOUND. The trust seam sits BEFORE it (§0.4(3):
    # "at the acceptance point, before the brief reaches any composer"), so a bound
    # composer is not needed to observe the seam — and leaving it unbound keeps this
    # record free of a `harness-runtime` import.
    ctx.ask_user_question_surface = None

    class _OkDispatcher:
        def lookup(self, step_kind: StepKind) -> StepDispatcher:
            return cast(StepDispatcher, self)

        def dispatch(
            self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
        ) -> dict[str, Any]:
            return {"ok": True}

    execute_workflow(
        _manifest().model_copy(update={"topology_pattern": TopologyPattern.SINGLE_THREADED_LINEAR}),
        [
            WorkflowStep(
                step_id=StepID("linear-0"),
                step_kind=StepKind.DECLARATIVE_STEP,
                step_payload={"index": 0},
            )
        ],
        run_id=_RUN_ID,
        ctx=cast(DriverContext, ctx),
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=cast(StepDispatcherRegistry, _OkDispatcher()),
    )
    return framework, list(exporter.get_finished_spans())


_OVERWRITE_ATTR = "validator.escalation.supplied_instance_id_overwritten"


# mutation-probe: replace the `evaluate_span.set_attribute(
# "validator.escalation.supplied_instance_id_overwritten", True)` call at the validator
# seam in `workflow_driver.py` with `pass` (a SILENT overwrite).
def test_the_validator_trust_seam_diagnoses_an_overwritten_token() -> None:
    """§0.4(3) + §0.7/§0.10 — the seam's DIAGNOSIS half, on the channel that exists.

    The overwrite ITSELF is asserted end to end in the U-RT-155 record (that assertion
    has to intercept the runtime composer the sanitized brief is handed to). What is
    pinned HERE is that the condition is SURFACED rather than silently swallowed: a
    silent overwrite satisfies AC 9 and AC 14 both, so without this criterion an
    implementation can drop the condition on the floor and still pass the plan.

    The attribute is a BOOLEAN, never the value — the hostile token must appear in no
    payload, key or span.
    """
    hostile = "HOSTILE-OPERATOR-SUPPLIED-TOKEN"
    framework, spans = _run_validator_escalation(hostile)
    assert framework.seen, "the validator must have run at all"
    assert framework.seen[0].escalation_instance_id == hostile, (
        "sanity: the validator really did supply a value — otherwise this is vacuous"
    )
    flagged = [s for s in spans if (s.attributes or {}).get(_OVERWRITE_ATTR) is True]
    assert flagged, (
        "the validator-supplied token was overwritten SILENTLY — §0.7's diagnosis half "
        f"requires surfacing it; exported spans were {[s.name for s in spans]!r}"
    )
    for span in spans:
        assert hostile not in repr(dict(span.attributes or {})), (
            f"the hostile value must appear on NO span; found it on {span.name!r}"
        )


def test_an_ordinary_validator_escalation_raises_no_overwrite_diagnostic() -> None:
    """The negative arm: a validator that supplies nothing must not be flagged.

    A diagnostic that fired on every validator escalation would be noise, which is
    functionally the same failure as not emitting it at all.
    """
    framework, spans = _run_validator_escalation(None)
    assert framework.seen and framework.seen[0].escalation_instance_id is None
    assert not [s for s in spans if _OVERWRITE_ATTR in (s.attributes or {})]


def test_the_overwrite_helper_replaces_rather_than_drops_the_whole_brief() -> None:
    """The overwrite's SHAPE, pinned directly: every other field survives.

    A seam that discarded the whole brief would also satisfy "the hostile value does
    not ship", while destroying the escalation the operator needs to see.
    """
    hostile = HITLEscalationBrief(
        parent_step_id="s",
        parent_action_id="a",
        escalation_reason="operator-authored",
        fail_detail_hash="f" * 64,
        escalation_instance_id="HOSTILE",
    )
    sanitized = hostile.model_copy(update={"escalation_instance_id": None})
    assert sanitized.escalation_instance_id is None
    assert sanitized.escalation_reason == "operator-authored"
    assert sanitized.fail_detail_hash == "f" * 64
    assert sanitized.proposed_response_palette == hostile.proposed_response_palette


# mutation-probe: replace `_diagnose_token_keyed_ingress`'s `warnings.warn(...)` call
# with `return` (a silent discard).
def test_a_token_keyed_resume_is_counted_as_unaddressed_and_is_diagnosed() -> None:
    """§0.7 — both halves.

    The NORMATIVE half is structural: `hitl_responses` stays exclusively
    `child_run_id`-keyed, so a submitted token matches no location and is
    counted-as-unaddressed. The ADVISORY half is that the condition must still be
    SURFACED — a silent discard satisfies AC 9 and AC 14 both, so without this
    criterion an implementation can drop the condition on the floor and still pass
    the plan.
    """
    token = compose_escalation_instance_id(
        pre_dispatch_gate_owning_branch_identity(_RUN_ID, 1), _PLACEMENT.position
    )
    pause_state = PausedWorkflowState(
        workflow_id="wf-b71",
        created_at=1,
        staleness_token="tok-1",
        locations=(
            PreDispatchUniformFallbackOnlyLocation(
                pause_reason=WorkflowPauseReason.HITL_PENDING,
                step_index=0,
                step_id="branch-1-sub",
                step_kind=StepKind.SUB_AGENT_DISPATCH,
                branch_index=1,
                escalation_instance_id=token,
            ),
        ),
    )
    response = HITLResult(
        response=HITLResponse.APPROVE,
        timestamp="2026-08-14T00:00:00Z",
        audit_ledger_entry_id=EntryID("e-b71-ingress"),
        response_summary_hash="e" * 64,
    )
    with pytest.warns(EscalationTokenKeyedIngressWarning) as caught:
        keyed = AccessorDerivedResumeContext.from_pause_state(
            pause_state, hitl_responses={token: response}
        )
    message = str(caught[0].message)
    assert "ordinal(s) [1]" in message, f"the diagnostic must name the ordinal; got {message!r}"
    assert token not in message, (
        "the token itself is a live correlation identifier on an unresolved gate and "
        "must not be re-emitted onto an incidental channel"
    )
    assert keyed.hitl_response_for("branch-1-sub") is None, (
        "the token is NOT an address — the location stays unaddressed"
    )


def test_a_legitimately_keyed_resume_emits_no_diagnostic() -> None:
    """The negative arm: an ordinary `child_run_id`-keyed resume must stay silent.

    A diagnostic that fired on every resume would be noise the operator learns to
    ignore, which is functionally the same failure as not emitting it at all.
    """
    pause_state = PausedWorkflowState(
        workflow_id="wf-b71",
        created_at=1,
        staleness_token="tok-1",
        locations=(
            PreDispatchUniformFallbackOnlyLocation(
                pause_reason=WorkflowPauseReason.HITL_PENDING,
                step_index=0,
                step_id="branch-1-sub",
                step_kind=StepKind.SUB_AGENT_DISPATCH,
                branch_index=1,
                escalation_instance_id="f" * 64,
            ),
        ),
    )
    response = HITLResult(
        response=HITLResponse.APPROVE,
        timestamp="2026-08-14T00:00:00Z",
        audit_ledger_entry_id=EntryID("e-b71-ok"),
        response_summary_hash="e" * 64,
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        AccessorDerivedResumeContext.from_pause_state(
            pause_state, hitl_responses={"child-run-abc": response}
        )
    assert not [w for w in caught if issubclass(w.category, EscalationTokenKeyedIngressWarning)]
