"""U-CP-86/U-CP-88 — fan-out capacity admission integration witnesses (B-48).

Tests per Implementation_Plan_Control_Plane_v2_39.md §1/§2 (PD-8
mutation-probed), exercised through the REAL `execute_workflow` →
`_execute_parallelization` path (not the U-CP-101 authority unit level):
occupied+N+S boundary admission, past-boundary fail-fast, admission under
CONTENTION from a concurrent workflow holding frames, and admission-rejection
composing as the EXISTING §25.15 cascade_policy outcome (PROCEED→PARTIAL /
CASCADE_CANCEL→FAILED with the SAME generic fail_class as any ordinary
branch failure — apply-note 2: no new control-transfer mode).

CP spec v1.102 §1 rows 1/2/4 (occupied+N+S admission); row 6 (cancel-policy
sites gated identically — `test_cancel_policy_initial_admission_gated_over_cap`).
"""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any, cast

from harness_core import PersonaTier, StepID, WorkloadClass
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.sub_agent_dispatch_capacity_authority import (
    CapacityLease,
    DefaultCapacityAuthority,
)
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import (
    DriverContext,
    StepDispatcher,
    StepDispatcherRegistry,
    StepKindDispatcherNotBoundError,
    _admit_fanout_branch_plan,
    _release_unconsumed_fanout_admissions,
    execute_workflow,
)
from harness_cp.workflow_driver_types import RunStatus, StepKind, WorkflowStep
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry

_DEFAULT_BINDING = ModelBinding(provider="anthropic", model="claude-haiku-4-5")
_CHAIN = FallbackChain(
    primary=ProviderCandidate(
        provider="anthropic", model="claude-haiku-4-5", family=ProviderFamily.ANTHROPIC
    ),
    same_family=(),
    cross_family=(),
    terminal=None,
)


def _manifest(
    *, workflow_id: str = "wf-cap", persona_tier: PersonaTier = PersonaTier.SOLO_DEVELOPER
) -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=persona_tier,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=TopologyPattern.PARALLELIZATION,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


def _branch_step(index: int) -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID(f"branch-{index}"),
        step_kind=StepKind.DECLARATIVE_STEP,
        step_payload={"index": index},
    )


class _RecordingLedger:
    actor: Any

    def __init__(self) -> None:
        from harness_is.state_ledger_entry_schema import Actor, ActorClass

        self.actor = Actor(actor_class=ActorClass.AGENT, actor_id="test-cap")
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
    def emit(self, event_class: Any) -> None:
        pass


class _Ctx:
    """Minimal fake `DriverContext` with an INJECTED capacity_authority."""

    def __init__(self, *, ledger: Any, capacity_authority: Any) -> None:
        from opentelemetry.trace import NoOpTracerProvider

        self.ledger_writer = ledger
        self.lifecycle_emitter = _Emitter()
        self.drained_flag = asyncio.Event()
        self.pause_resume_protocol = None
        self.pause_requested_flag = asyncio.Event()
        self.ledger_reader = None
        self.tracer_provider = NoOpTracerProvider()
        self.validator_framework = None
        self.tenant_id = None
        self.capacity_authority = capacity_authority


class _Registry:
    def __init__(self, dispatcher: StepDispatcher) -> None:
        self._dispatcher = dispatcher

    def lookup(self, step_kind: StepKind) -> StepDispatcher:
        if step_kind is not StepKind.DECLARATIVE_STEP:
            raise StepKindDispatcherNotBoundError(step_kind)
        return self._dispatcher


class _EchoDispatcher:
    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        return {"branch": int(step.step_payload["index"])}


def _run(
    *,
    n_branches: int,
    capacity_authority: Any,
    persona_tier: PersonaTier = PersonaTier.SOLO_DEVELOPER,
    workflow_id: str = "wf-cap",
) -> Any:
    ledger = _RecordingLedger()
    ctx = cast(DriverContext, _Ctx(ledger=ledger, capacity_authority=capacity_authority))
    steps = [_branch_step(i) for i in range(n_branches)]
    registry = cast(StepDispatcherRegistry, _Registry(_EchoDispatcher()))
    return execute_workflow(  # returns RunResult directly
        _manifest(workflow_id=workflow_id, persona_tier=persona_tier),
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=registry,
    )


def test_fanout_at_boundary_occupied_plus_n_plus_s_equals_cap_fully_concurrent() -> None:
    """occupied(0) + N(4) + S(0, all DECLARATIVE_STEP — async-shaped, uncharged
    inner) == cap(4): every branch admitted, run SUCCESS."""
    authority = DefaultCapacityAuthority(frame_budget=4)
    result = _run(n_branches=4, capacity_authority=authority)
    assert result.status == RunStatus.SUCCESS
    assert authority.available == 4  # every frame released post-run


def test_fanout_past_boundary_next_branch_fail_fasts_typed_step_attributable() -> None:
    """PROCEED tier: occupied(0) + N(4) > cap(3) — the excess branch(es) are
    admission-rejected; the rejection composes as an ORDINARY branch failure
    (any_failed → PARTIAL, per the existing §25.15 PROCEED mapping)."""
    authority = DefaultCapacityAuthority(frame_budget=3)
    result = _run(
        n_branches=4, capacity_authority=authority, persona_tier=PersonaTier.SOLO_DEVELOPER
    )
    assert result.status == RunStatus.PARTIAL
    assert authority.available == 3  # all leases released post-run


def test_fanout_past_boundary_rejected_branch_recorded_cancelled_not_completed() -> None:
    """B-48 (codex round-4 [P2] "avoid recording rejected branches as
    executed"): the SAME over-cap PROCEED scenario as the sibling test above
    — the rejected branch's dispatcher was NEVER called, so its ledger
    terminal must be `cancelled` (the never-dispatched disposition), NEVER
    `completed` (which would falsely claim the dispatcher ran and count it
    as executed in the durable ledger + step count)."""
    authority = DefaultCapacityAuthority(frame_budget=3)
    ledger = _RecordingLedger()
    ctx = cast(DriverContext, _Ctx(ledger=ledger, capacity_authority=authority))
    steps = [_branch_step(i) for i in range(4)]
    registry = cast(StepDispatcherRegistry, _Registry(_EchoDispatcher()))
    result = execute_workflow(
        _manifest(workflow_id="wf-cap-rejected-terminal", persona_tier=PersonaTier.SOLO_DEVELOPER),
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=registry,
    )
    assert result.status == RunStatus.PARTIAL
    branch3_statuses = [
        payload.branch_metadata.terminal_status
        for payload, _wk in ledger.appends
        if payload.branch_metadata is not None and payload.branch_metadata.branch_index == 3
    ]
    # Branch 3 is the rejected excess (frame_budget=3, 4 branches, 1 frame
    # each) — exactly ONE ledger entry (the synthesized `cancelled`
    # terminal), never `completed`, and never a step entry (`None`) at all —
    # a step entry would itself be evidence the (never-called) dispatcher's
    # attempt was being recorded.
    assert branch3_statuses == ["cancelled"]


def test_cancel_policy_initial_admission_gated_over_cap() -> None:
    """CASCADE_CANCEL tier: an over-cap fan-out's admission-rejected branch
    cascades the barrier — FAILED with the SAME generic fail_class ANY
    ordinary branch failure produces under this tier (apply-note 2: no new
    control-transfer mode)."""
    authority = DefaultCapacityAuthority(frame_budget=2)
    result = _run(
        n_branches=4,
        capacity_authority=authority,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    )
    assert result.status == RunStatus.FAILED
    assert result.fail_class == "parallelization-cascade-cancel"
    assert authority.available == 2  # all leases released post-run (no leak)


def test_fanout_admission_under_contention_second_workflow_holding_frames_counted() -> None:
    """Admission is against AVAILABLE capacity, never the local fan-out alone:
    a SECOND workflow's fan-out that would fit ALONE is rejected because a
    FIRST workflow's branches still hold frames (mutation probe: computing
    admission against the local fan-out alone passes this wrongly)."""
    authority = DefaultCapacityAuthority(frame_budget=4)
    # First workflow holds 3 frames externally (simulating a concurrent
    # workflow's in-flight branches) via a direct reservation.
    held = authority.reserve(3, step_id="external-hold", descent_chain=("external-hold",))
    try:
        # Second workflow's fan-out needs 4 (fits ALONE at cap=4, but only 1
        # is available under contention) — PARTIAL under PROCEED.
        result = _run(n_branches=4, capacity_authority=authority)
        assert result.status == RunStatus.PARTIAL
    finally:
        held.release()
    assert authority.available == 4


def test_cap_rejected_branch_drives_existing_cascade_policy_outcomes() -> None:
    """Parametrized over PROCEED/CASCADE_CANCEL: the SAME over-cap scenario
    drives the SAME outcome an ordinary branch failure would (mutation
    probe: introducing a distinct control-transfer path for capacity
    rejections would diverge from these established mappings)."""
    for persona, expected_status in (
        (PersonaTier.SOLO_DEVELOPER, RunStatus.PARTIAL),
        (PersonaTier.MULTI_TENANT_COMPLIANCE, RunStatus.FAILED),
    ):
        authority = DefaultCapacityAuthority(frame_budget=2)
        result = _run(n_branches=3, capacity_authority=authority, persona_tier=persona)
        assert result.status == expected_status


def test_default_authority_used_when_no_capacity_authority_injected() -> None:
    """Absent-injection fallback (CP spec v1.102 §1 row 7b): `ctx` with no
    `capacity_authority` attribute still gates identically via the module
    default (never ungated) — a small fan-out under the 256 default admits
    cleanly."""
    ledger = _RecordingLedger()

    class _CtxNoAuthority:
        def __init__(self) -> None:
            from opentelemetry.trace import NoOpTracerProvider

            self.ledger_writer = ledger
            self.lifecycle_emitter = _Emitter()
            self.drained_flag = asyncio.Event()
            self.pause_resume_protocol = None
            self.pause_requested_flag = asyncio.Event()
            self.ledger_reader = None
            self.tracer_provider = NoOpTracerProvider()
            self.validator_framework = None
            self.tenant_id = None
            # deliberately no `capacity_authority` attribute

    ctx = cast(DriverContext, _CtxNoAuthority())
    steps = [_branch_step(i) for i in range(3)]
    registry = cast(StepDispatcherRegistry, _Registry(_EchoDispatcher()))
    result = execute_workflow(
        _manifest(),
        steps,
        run_id="run-1",
        ctx=ctx,
        default_model_binding=_DEFAULT_BINDING,
        step_dispatchers=registry,
    )
    assert result.status == RunStatus.SUCCESS


def test_release_unconsumed_fanout_admissions_returns_leases_skips_errors() -> None:
    """`_release_unconsumed_fanout_admissions` (B-48 lease-leak fix,
    out-of-family Codex [P1]) releases every admitted lease in an admission
    map and safely skips rejected-branch entries.

    Mutation probe: dropping the `isinstance(admission, CapacityLease)`
    guard and calling `.release_unless_job_bound()` unconditionally would
    raise `AttributeError` on a `SubAgentDispatchCapacityError` entry (no
    such method); dropping the call to the helper entirely leaves
    `authority.available` short by every admitted branch's frames — the
    exact permanent-short-by-fan-out-width leak the post-admission
    early-return sites (reconciler validation, effect-fence strict-tier
    guard, B-39 Phase-0 abort) would otherwise cause.
    """
    authority = DefaultCapacityAuthority(frame_budget=3)
    ctx = cast(DriverContext, SimpleNamespace(capacity_authority=authority))
    branch_plan = [(i, _branch_step(i), None, None, None) for i in range(3)]
    admissions = _admit_fanout_branch_plan(ctx, branch_plan, workflow_id="wf")
    assert authority.available == 0  # all 3 admitted (1 frame each, DECLARATIVE_STEP)
    assert all(isinstance(a, CapacityLease) for a in admissions.values())

    _release_unconsumed_fanout_admissions(admissions)
    assert authority.available == 3

    # Exactly-once at the CapacityLease level: a second call is a no-op, not
    # a double-credit.
    _release_unconsumed_fanout_admissions(admissions)
    assert authority.available == 3


def test_release_unconsumed_fanout_admissions_skips_rejected_branches() -> None:
    """A `SubAgentDispatchCapacityError` (rejected branch) entry carries no
    lease and must never reach `.release_unless_job_bound()`."""
    authority = DefaultCapacityAuthority(frame_budget=1)
    ctx = cast(DriverContext, SimpleNamespace(capacity_authority=authority))
    branch_plan = [(i, _branch_step(i), None, None, None) for i in range(2)]
    admissions = _admit_fanout_branch_plan(ctx, branch_plan, workflow_id="wf")
    assert authority.available == 0  # branch 0 admitted (1 frame); branch 1 rejected
    assert isinstance(admissions[0], CapacityLease)
    assert not isinstance(admissions[1], CapacityLease)

    _release_unconsumed_fanout_admissions(admissions)
    assert authority.available == 1  # only the admitted branch-0 lease returns frames
