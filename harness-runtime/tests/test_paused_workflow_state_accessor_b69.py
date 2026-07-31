"""B-69 impl leg — U-RT-148 (`Implementation_Plan_Harness_Runtime_v2_55.md` §1).

Witnesses AC #1 … #16 for the two ratified Runtime surfaces: the §14.14.9
durable-pause-state read accessor and the §30 refusal-only staleness precondition.

**The distinction the whole arc turns on**, stated here so a future reader does not
have to reconstruct it: `resume()` re-derives the SNAPSHOT from the durable journal
on every call, but it never re-derives the operator's RESPONSE MAP. Two different
objects; only one is re-derived. A response composed against a superseded read,
delivered through CP §1.2 property 4's sole-member carve-out, lands on a gate the
operator never saw.

Every criterion is BY EXECUTION against a REAL `JournalWorkflowPauseStore` and the
REAL `DurablePauseResumeProtocol.capture_pause_snapshot` write path — never a
synthesized journal record — and every refusal is asserted, never inferred from an
absence.
"""

from __future__ import annotations

import errno
import os
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest
from harness_core.deployment_surface import DeploymentSurface
from harness_core.identity import EntryID, StepID
from harness_core.persona_tier import PersonaTier
from harness_core.workload_class import WorkloadClass
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.handoff_context import StateSummary
from harness_cp.hitl_placement import HITLResult
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.pause_resume_protocol_types import (
    EffectFencePausedBranchResumeState,
    PausedChildBranchResumeState,
    PauseSnapshot,
    PeerFanOutResumeState,
    PreDispatchGateOwningBranchResumeState,
    ResumeContext,
    WorkflowPauseReason,
)
from harness_cp.pause_state_projection import (
    AccessorDerivedResumeContext,
    CrashReconstructionEffectFenceAddressableLocation,
    DepthZeroRootUniformFallbackOnlyLocation,
    PauseLocationVariant,
)
from harness_cp.routing_manifest_residence import RoutingManifest
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import compute_hitl_uniform_fallback_eligible_run_id
from harness_cp.workflow_driver_types import StepKind, WorkflowStep
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_is.path_class_registry import PathClass
from harness_is.state_ledger_entry_schema import Identifier
from harness_od.pause_resume_namespace import (
    PAUSE_STATE_EVENT_HEAD_SAMPLING_RATE,
    PauseStateAuditPayload,
    PauseStateEventKind,
)
from harness_runtime.api import (
    PausedWorkflowStateUnavailableError,
    ResumeArgsError,
    ResumeHandleUnknownError,
    ResumePauseStateStaleError,
    read_paused_workflow_state,
    resume,
)
from harness_runtime.lifecycle.durable_pause_resume_protocol import DurablePauseResumeProtocol
from harness_runtime.lifecycle.journal_workflow_pause_store import (
    JournalWorkflowPauseStore,
    PauseJournalReadCause,
    pause_journal_dir_for,
)
from harness_runtime.lifecycle.pause_resume_protocol_types import PauseResumeProtocolConfig
from harness_runtime.lifecycle.pause_state_staleness import mint_staleness_token
from harness_runtime.lifecycle.pre_bootstrap_pause_state_sink import pause_state_sink_for
from harness_runtime.types import (
    CollectorConfig,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
)
from pydantic import ValidationError

_WORKLOAD = WorkloadClass.SOFTWARE_ENGINEERING
_SURFACE = DeploymentSurface.LOCAL_DEVELOPMENT
_WORKFLOW_ID = "wf-b69-accessor"
_ANCHOR = "0" * 64

_CHAIN = FallbackChain(
    primary=ProviderCandidate(
        provider="anthropic", model="claude-haiku-4-5", family=ProviderFamily.ANTHROPIC
    ),
    same_family=(),
    cross_family=(),
    terminal=None,
)


# --------------------------------------------------------------------------
# Substrate — a REAL store, a REAL capture path, a REAL config resolution.
# --------------------------------------------------------------------------


def _path_bindings(tmp_path: Path) -> PathBindingConfig:
    return PathBindingConfig(
        raw_entries=tuple(
            {
                "path_class": pc,
                "workflow_class": _WORKLOAD,
                "deployment_surface": _SURFACE,
                "path": str(tmp_path / pc.value.lower()),
            }
            for pc in PathClass
        ),
    )


def _config(tmp_path: Path, *, durable: bool = True) -> RuntimeConfig:
    return RuntimeConfig(
        deployment_surface=_SURFACE,
        repository_root=tmp_path,
        path_bindings=_path_bindings(tmp_path),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4317"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        mcp_clients=[],
        ollama_optional=True,
        pause_resume_protocol_config=PauseResumeProtocolConfig(durable=durable),
        routing_manifest=RoutingManifest(
            manifest_version=1,
            per_role_bindings={},
            per_workload_overrides={},
            fallback_chains=(_CHAIN,),
            retry_policies={},
        ),
    )


class _Workflow:
    """The minimal structural `WorkflowObject` the accessor + `resume()` require."""

    workflow_id = _WORKFLOW_ID
    workload_class = _WORKLOAD
    default_model_binding = ModelBinding(provider="anthropic", model="claude-haiku-4-5")

    def __init__(self, *, step_count: int = 2) -> None:
        self.steps: Sequence[WorkflowStep] = tuple(
            WorkflowStep(
                step_id=StepID(f"step-{i}"),
                step_kind=StepKind.DECLARATIVE_STEP,
                step_payload={},
            )
            for i in range(step_count)
        )
        self.manifest_entry = WorkflowManifestEntry(
            workflow_id=_WORKFLOW_ID,
            workload_class=_WORKLOAD,
            persona_tier=PersonaTier.TEAM_BINDING,
            engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
            topology_pattern=TopologyPattern.SINGLE_THREADED_LINEAR,
            layer_budgets=(),
            fallback_chain=_CHAIN,
            hitl_placements=(),
            per_step_overrides={},
        )


def _summary() -> StateSummary:
    """The MVP placeholder `pause_context_reader`'s constant output.

    Injected explicitly here rather than depending on the default binding, per
    AC #5's own instruction.
    """
    return StateSummary(
        relevant_entries=(),
        summary_text="",
        summary_hash="0" * 64,
        idempotency_key=Identifier(""),
        external_references=(),
    )


def _store(tmp_path: Path) -> JournalWorkflowPauseStore:
    resolved = tmp_path / PathClass.STATE_LEDGER.value.lower()
    return JournalWorkflowPauseStore(journal_dir=pause_journal_dir_for(resolved))


def _protocol(tmp_path: Path) -> DurablePauseResumeProtocol:
    """The REAL durable capture path — composes via the CP parent, then journals."""
    return DurablePauseResumeProtocol(
        state_ledger_writer=object(),
        state_ledger_reader=object(),
        pause_context_reader=lambda: (_summary(), _ANCHOR),
        store=_store(tmp_path),
    )


async def _capture(
    tmp_path: Path,
    *,
    run_id: str,
    step_index: int = 0,
    pause_reason: WorkflowPauseReason = WorkflowPauseReason.HITL_PENDING,
    **carriers: Any,
) -> PauseSnapshot:
    """A GENUINE re-pause through `capture_pause_snapshot`, never a synthesized record."""
    return await _protocol(tmp_path).capture_pause_snapshot(
        _WORKFLOW_ID, run_id, step_index, pause_reason, **carriers
    )


def _hitl(response: HITLResponse = HITLResponse.APPROVE) -> HITLResult:
    return HITLResult(
        response=response,
        timestamp="2026-07-31T00:00:00Z",
        audit_ledger_entry_id=EntryID("entry-b69"),
        response_summary_hash="0" * 64,
    )


def _sink_rows(tmp_path: Path) -> tuple[PauseStateAuditPayload, ...]:
    return pause_state_sink_for(_config(tmp_path), _WORKLOAD).read_all()


# --------------------------------------------------------------------------
# AC #1 — W2, the PRIMARY witness: the sole-member misattribution, 1→1 shape
# --------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ac1_w2_sole_member_misattribution_is_refused_under_the_fence(
    tmp_path: Path,
) -> None:
    """AC #1 / W2 (PRIMARY) — the 1→1 shape, both halves.

    The read enumerates EXACTLY ONE location (A). The operator composes a uniform
    `hitl_response` against it. The live cycle's SOLE gate-owning member is D ∉ {A}.

    - **Under the fence:** `resume()` refuses pre-bootstrap, so D never reaches the
      resolver at all — the uniform response is not delivered to anything.
    - **Without the fence:** the very same live snapshot resolves the uniform
      response FOR D — the misattribution, reproduced.

    This is the most common HITL shape at the `solo-developer` tier: one location,
    one uniform answer, the single-location happy path. **Falsifier on the record:**
    if D turned out to be refused by some path not yet found, the arc's core finding
    would collapse and MUST be re-surfaced, not worked around. The second half of
    this test is what keeps that falsifier live.
    """
    config = _config(tmp_path)
    workflow = _Workflow()

    await _capture(tmp_path, run_id="run-A")
    read_a = await read_paused_workflow_state(workflow, resume_handle=_WORKFLOW_ID, config=config)
    assert len(read_a.locations) == 1
    assert isinstance(read_a.locations[0], DepthZeroRootUniformFallbackOnlyLocation)

    composed = AccessorDerivedResumeContext.from_pause_state(read_a, hitl_response=_hitl())

    # The live cycle re-pauses under a DIFFERENT sole gate-owning member.
    live = await _capture(tmp_path, run_id="run-D")

    # (i) WITHOUT the fence — the misattribution is real and reproducible: the
    # uniform response composed against A resolves FOR D.
    unfenced = ResumeContext(hitl_response=_hitl())
    assert compute_hitl_uniform_fallback_eligible_run_id(live, unfenced) == "run-D"
    assert unfenced.hitl_response_for("run-D") is not None

    # (ii) UNDER the fence — refused pre-bootstrap; D is never resolved.
    with pytest.raises(ResumePauseStateStaleError) as excinfo:
        await resume(
            workflow,  # pyright: ignore[reportArgumentType]
            resume_handle=_WORKFLOW_ID,
            resume_context=composed,
            config=config,
        )
    assert excinfo.value.claimed_token == read_a.staleness_token
    assert "re-read" in str(excinfo.value)


@pytest.mark.asyncio
async def test_ac1_w2_secondary_3_to_1_variant(tmp_path: Path) -> None:
    """AC #1 — the 3→1 shape is a SECONDARY variant of the same witness. It does
    not substitute for 1→1; it is added because a multi-location read narrowing to
    a single live gate-owning member is the shape an operator most easily
    misreads."""
    config = _config(tmp_path)
    workflow = _Workflow()
    await _capture(
        tmp_path,
        run_id="run-multi",
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(),
            branch_count=3,
            pre_dispatch_gate_owning_branches=(
                PreDispatchGateOwningBranchResumeState(
                    branch_index=0, step_id="p0", step_kind=StepKind.SUB_AGENT_DISPATCH.value
                ),
                PreDispatchGateOwningBranchResumeState(
                    branch_index=1, step_id="p1", step_kind=StepKind.SUB_AGENT_DISPATCH.value
                ),
                PreDispatchGateOwningBranchResumeState(
                    branch_index=2, step_id="p2", step_kind=StepKind.SUB_AGENT_DISPATCH.value
                ),
            ),
        ),
    )
    read = await read_paused_workflow_state(workflow, resume_handle=_WORKFLOW_ID, config=config)
    gate_owning = [
        loc for loc in read.locations if loc.variant is PauseLocationVariant.UNIFORM_FALLBACK_ONLY
    ]
    assert len(gate_owning) == 3

    composed = AccessorDerivedResumeContext.from_pause_state(read, hitl_response=_hitl())
    await _capture(tmp_path, run_id="run-D")
    with pytest.raises(ResumePauseStateStaleError):
        await resume(
            workflow,  # pyright: ignore[reportArgumentType]
            resume_handle=_WORKFLOW_ID,
            resume_context=composed,
            config=config,
        )


# --------------------------------------------------------------------------
# AC #2 — W1: the 2+-member clause
# --------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ac2_w1_two_plus_unaddressed_gate_owning_branches_re_pause_inert(
    tmp_path: Path,
) -> None:
    """AC #2 / W1 — a wrong-key case with 2+ unaddressed gate-owning branches
    asserts INERT re-pause (CP §1.2 property 4's 2+-member clause).

    A one-branch witness proves nothing about this clause: the sole-member carve-out
    is the OTHER branch of the rule, and it is the unsafe one.
    """
    config = _config(tmp_path)
    workflow = _Workflow()
    live = await _capture(
        tmp_path,
        run_id="run-two",
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(),
            branch_count=2,
            paused_child_branches=(
                PausedChildBranchResumeState(
                    branch_index=0,
                    step_id="w0",
                    child_snapshot=await _child_snapshot(tmp_path, run_id="child-A"),
                ),
                PausedChildBranchResumeState(
                    branch_index=1,
                    step_id="w1",
                    child_snapshot=await _child_snapshot(tmp_path, run_id="child-B"),
                ),
            ),
        ),
    )
    read = await read_paused_workflow_state(workflow, resume_handle=_WORKFLOW_ID, config=config)
    addressable = [
        loc for loc in read.locations if loc.variant is PauseLocationVariant.HITL_ADDRESSABLE
    ]
    assert len(addressable) == 2

    # A WRONG key: the operator addressed a child that is not paused this cycle, so
    # BOTH real members stay unaddressed → the uniform fallback is INERT.
    wrong_key = ResumeContext(
        hitl_response=_hitl(), hitl_responses={"child-NOT-PAUSED": _hitl(HITLResponse.REJECT)}
    )
    assert compute_hitl_uniform_fallback_eligible_run_id(live, wrong_key) is None


async def _child_snapshot(tmp_path: Path, *, run_id: str) -> PauseSnapshot:
    """A nested child pause, composed through the real protocol but NOT journaled as
    the workflow's own latest record (it is embedded in the parent's carrier)."""
    protocol = DurablePauseResumeProtocol(
        state_ledger_writer=object(),
        state_ledger_reader=object(),
        pause_context_reader=lambda: (_summary(), _ANCHOR),
        store=JournalWorkflowPauseStore(journal_dir=tmp_path / "throwaway-journal"),
    )
    return await protocol.capture_pause_snapshot(
        _WORKFLOW_ID, run_id, 1, WorkflowPauseReason.HITL_PENDING
    )


# --------------------------------------------------------------------------
# AC #3 / AC #5 — W2′ and W4: the conceded carrier, executed
# --------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ac3_w2_prime_snapshot_hash_fence_still_misattributes(tmp_path: Path) -> None:
    """AC #3 / W2′ — the CONCEDED carrier, EXECUTED.

    Two successive LINEAR pauses at the same `step_index` under the same reused
    `run_id` (`run_id` IS reused across resume, §30) hash IDENTICALLY, so a
    `snapshot_hash`-based fence ADMITS the second — the operator's answer to the
    first gate lands on the second. The shipped token REFUSES it.

    This converts the council's P4 from a reasoned finding into an executed one and
    forecloses a later session re-nominating the carrier this arc conceded.
    """
    config = _config(tmp_path)
    workflow = _Workflow()
    first = await _capture(tmp_path, run_id="run-reused", step_index=1)
    read = await read_paused_workflow_state(workflow, resume_handle=_WORKFLOW_ID, config=config)
    second = await _capture(tmp_path, run_id="run-reused", step_index=1)

    # A snapshot_hash-based fence would see NO change → admit → misattribute.
    assert first.snapshot_hash == second.snapshot_hash

    # The shipped token DOES change → refuse.
    composed = AccessorDerivedResumeContext.from_pause_state(read, hitl_response=_hitl())
    with pytest.raises(ResumePauseStateStaleError):
        await resume(
            workflow,  # pyright: ignore[reportArgumentType]
            resume_handle=_WORKFLOW_ID,
            resume_context=composed,
            config=config,
        )


@pytest.mark.asyncio
async def test_ac5_w4_characterization_successive_linear_pauses_hash_equally(
    tmp_path: Path,
) -> None:
    """AC #5 / W4 (CHARACTERIZATION, secondary).

    **MANDATORY ANNOTATION, carried in the test itself:** this asserts a
    PLACEHOLDER property. The `pause_context_reader` injected below is the MVP
    constant-sentinel placeholder (Runtime spec §14.14.7's explicitly deferred
    binding). When a REAL reader lands and `state_summary` varies, this test will
    FAIL FOR A GOOD REASON, and its correct disposition is then **DELETION or
    INVERSION — never repair.** Repairing it would re-assert a property the system
    no longer has.

    AC #3 above is the load-bearing empirical form of the same finding and is
    unaffected by the placeholder's replacement.

    The placeholder reader is injected here explicitly rather than depended on via
    the default binding, so the test's own premise is visible in its body.
    """
    first = await _capture(tmp_path, run_id="run-w4", step_index=0)
    second = await _capture(tmp_path, run_id="run-w4", step_index=0)
    assert first.snapshot_hash == second.snapshot_hash


# --------------------------------------------------------------------------
# AC #4 — W3: the fence by MUTATION-PROBE
# --------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ac4_w3_fence_refuses_after_a_real_second_capture(tmp_path: Path) -> None:
    """AC #4 / W3 — capture → read → a REAL second `capture()` → resume with the
    stale token → TYPED refusal.

    **This AC is one half of B-69's conjunctive closure criterion.** The second
    capture is a genuine re-pause through `DurablePauseResumeProtocol
    .capture_pause_snapshot`, NOT a synthesized journal record — a synthesized
    record would test the token's arithmetic, not the guard's reach.

    **Mutation-probe (Workflow v1.18 PD-8), performed manually at the impl leg and
    recorded in the PR:** deleting the
    `_enforce_pause_state_staleness_precondition(...)` call from `resume()` makes
    this test FAIL (the resume proceeds past the fence to bootstrap instead of
    raising), which is what proves the guard is load-bearing rather than green by
    coincidence.
    """
    config = _config(tmp_path)
    workflow = _Workflow()
    await _capture(tmp_path, run_id="run-1")
    read = await read_paused_workflow_state(workflow, resume_handle=_WORKFLOW_ID, config=config)
    composed = AccessorDerivedResumeContext.from_pause_state(read, hitl_response=_hitl())

    await _capture(tmp_path, run_id="run-2")  # the REAL second capture

    with pytest.raises(ResumePauseStateStaleError):
        await resume(
            workflow,  # pyright: ignore[reportArgumentType]
            resume_handle=_WORKFLOW_ID,
            resume_context=composed,
            config=config,
        )


@pytest.mark.asyncio
async def test_ac4_fresh_token_is_admitted_by_the_fence(tmp_path: Path) -> None:
    """AC #4, the liveness half — the fence is a PRECONDITION, not a wall. A token
    that still matches passes it, so the refusal above is discriminating rather than
    unconditional."""
    from harness_runtime import api as api_module

    config = _config(tmp_path)
    workflow = _Workflow()
    await _capture(tmp_path, run_id="run-1")
    read = await read_paused_workflow_state(workflow, resume_handle=_WORKFLOW_ID, config=config)
    composed = AccessorDerivedResumeContext.from_pause_state(read, hitl_response=_hitl())
    # No second capture — the precondition must NOT raise.
    api_module._enforce_pause_state_staleness_precondition(config, workflow, composed)  # pyright: ignore[reportPrivateUsage, reportArgumentType]


# --------------------------------------------------------------------------
# AC #6 / #14 / #16(b) — the carrier
# --------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ac6_read_then_omitted_is_unrepresentable(tmp_path: Path) -> None:
    """AC #6 — detect-then-refuse on the carrier's non-downgradability, and the
    absence of any read-then-omitted construction path."""
    config = _config(tmp_path)
    await _capture(tmp_path, run_id="run-1")
    read = await read_paused_workflow_state(
        _Workflow(),  # pyright: ignore[reportArgumentType]
        resume_handle=_WORKFLOW_ID,
        config=config,
    )
    composed = AccessorDerivedResumeContext.from_pause_state(read, hitl_response=_hitl())
    with pytest.raises(ValidationError):
        ResumeContext.model_validate(composed.model_dump())
    with pytest.raises(ValidationError):
        composed.pause_state = read  # pyright: ignore[reportAttributeAccessIssue]
    with pytest.raises(ValidationError):
        AccessorDerivedResumeContext(hitl_response=_hitl())  # pyright: ignore[reportCallIssue]


@pytest.mark.asyncio
async def test_ac16b_the_scalar_fields_are_bound_not_only_the_maps(tmp_path: Path) -> None:
    """AC #16(b) — the staleness carrier binds a SCALAR `hitl_response` /
    `effect_fence_resolution` composed from an accessor read, not only the map
    fields.

    **This is the W2 path itself**: a `uniform-fallback-only` location is answered
    by the SCALAR field, never by a map entry, so a map-only binding would leave the
    arc's PRIMARY witness entirely unfenced — the mitigation absent from the one
    path it was built for.
    """
    config = _config(tmp_path)
    workflow = _Workflow()
    await _capture(tmp_path, run_id="run-scalar")
    read = await read_paused_workflow_state(workflow, resume_handle=_WORKFLOW_ID, config=config)
    scalar_only = AccessorDerivedResumeContext.from_pause_state(read, hitl_response=_hitl())
    assert scalar_only.hitl_responses is None
    assert scalar_only.hitl_response is not None

    await _capture(tmp_path, run_id="run-scalar-2")
    with pytest.raises(ResumePauseStateStaleError):
        await resume(
            workflow,  # pyright: ignore[reportArgumentType]
            resume_handle=_WORKFLOW_ID,
            resume_context=scalar_only,
            config=config,
        )


@pytest.mark.asyncio
async def test_ac14_no_read_path_is_byte_compatible(tmp_path: Path) -> None:
    """AC #14 — an existing `resume()` caller constructing the LEGACY variant
    observes behavior byte-identical to pre-v1.107. The precondition narrows a
    window for COMPOSED CLAIMS; it does not deprecate unfenced resume.

    Witnessed at the precondition itself: a legacy context is INERT through it even
    when the journal has moved on twice.
    """
    from harness_runtime import api as api_module

    config = _config(tmp_path)
    workflow = _Workflow()
    await _capture(tmp_path, run_id="run-1")
    await _capture(tmp_path, run_id="run-2")
    api_module._enforce_pause_state_staleness_precondition(  # pyright: ignore[reportPrivateUsage]
        config,
        workflow,  # pyright: ignore[reportArgumentType]
        ResumeContext(hitl_response=_hitl()),
    )
    api_module._enforce_pause_state_staleness_precondition(  # pyright: ignore[reportPrivateUsage]
        config,
        workflow,  # pyright: ignore[reportArgumentType]
        None,
    )


# --------------------------------------------------------------------------
# AC #7 / #8 — fail-closed, and the five causes
# --------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ac7_fail_closed_when_no_token_can_be_minted(tmp_path: Path) -> None:
    """AC #7 — force the token computation to fail and assert NO projection is
    returned. Never a projection carrying an absent token that a subsequent
    `resume()` would read as "no claim"."""
    config = _config(tmp_path)
    store = _store(tmp_path)
    journal = store._journal_file(_WORKFLOW_ID)  # pyright: ignore[reportPrivateUsage]
    journal.parent.mkdir(parents=True, exist_ok=True)
    journal.write_text("", encoding="utf-8")  # exists, holds no record → no token mintable
    with pytest.raises(PausedWorkflowStateUnavailableError) as excinfo:
        await read_paused_workflow_state(
            _Workflow(),  # pyright: ignore[reportArgumentType]
            resume_handle=_WORKFLOW_ID,
            config=config,
        )
    assert excinfo.value.cause is PauseJournalReadCause.EMPTY_JOURNAL


@pytest.mark.asyncio
async def test_ac8_five_causes_are_distinct_and_empty_journal_is_not_absent(
    tmp_path: Path,
) -> None:
    """AC #8 — each of the five `None` branches yields a DISTINCT stable identifier.

    Specifically asserted: `empty-journal` is NOT folded into `absent`. Collapsing
    on shared routing is the exact defect this refinement exists to undo, and the
    two carry different operator repairs.
    """
    config = _config(tmp_path)
    workflow = _Workflow()
    store = _store(tmp_path)
    journal = store._journal_file(_WORKFLOW_ID)  # pyright: ignore[reportPrivateUsage]

    async def _cause() -> PauseJournalReadCause:
        with pytest.raises(PausedWorkflowStateUnavailableError) as excinfo:
            await read_paused_workflow_state(
                workflow,  # pyright: ignore[reportArgumentType]
                resume_handle=_WORKFLOW_ID,
                config=config,
            )
        return excinfo.value.cause

    # absent — no journal file at all.
    assert await _cause() is PauseJournalReadCause.ABSENT

    # empty-journal — the file EXISTS but holds no record. NOT `absent`.
    journal.parent.mkdir(parents=True, exist_ok=True)
    journal.write_text("\n", encoding="utf-8")
    assert await _cause() is PauseJournalReadCause.EMPTY_JOURNAL

    # corrupt-latest — undecodable bytes, and separately an unparseable record.
    journal.write_bytes(b"\xff\xfe not utf-8\n")
    assert await _cause() is PauseJournalReadCause.CORRUPT_LATEST
    journal.write_text("{not json\n", encoding="utf-8")
    assert await _cause() is PauseJournalReadCause.CORRUPT_LATEST

    # workflow-mismatch — the record names a different workflow.
    journal.write_text('{"workflow_id": "other-wf", "pause_snapshot": {}}\n', encoding="utf-8")
    assert await _cause() is PauseJournalReadCause.WORKFLOW_MISMATCH

    # read-error — a genuine I/O failure on the read.
    journal.write_text("{}\n", encoding="utf-8")
    os.chmod(journal, 0o000)
    try:
        if os.access(journal, os.R_OK):  # pragma: no cover — running as root
            pytest.skip("cannot make the journal unreadable as this user")
        with pytest.raises(PausedWorkflowStateUnavailableError) as excinfo:
            await read_paused_workflow_state(
                workflow,  # pyright: ignore[reportArgumentType]
                resume_handle=_WORKFLOW_ID,
                config=config,
            )
    finally:
        os.chmod(journal, 0o600)
    assert excinfo.value.cause is PauseJournalReadCause.READ_ERROR
    # ... and a PERMANENTLY-failing shape is NOT asserted retryable: routing every
    # `read-error` as blindly retryable would encode futile retries into the
    # contract.
    assert excinfo.value.retryable is False


def test_ac8_read_error_retryability_follows_the_underlying_errno() -> None:
    """AC #8 — `read-error` is transient ONLY for a retryable underlying I/O error."""
    from harness_runtime.lifecycle.journal_workflow_pause_store import _read_error_is_retryable

    for permanent in (errno.EACCES, errno.EPERM, errno.EROFS, errno.EISDIR, errno.ENAMETOOLONG):
        assert _read_error_is_retryable(OSError(permanent, "x")) is False
    for transient in (errno.EIO, errno.EAGAIN, errno.EBUSY, errno.EINTR):
        assert _read_error_is_retryable(OSError(transient, "x")) is True


@pytest.mark.asyncio
async def test_ac8_failure_is_typed_and_discloses_no_path_or_exception_text(
    tmp_path: Path,
) -> None:
    """AC #8 — the failure channel is a TYPED raise carrying the cause; NEVER a bare
    `None`, and NEVER a re-raise of `resume()`'s own `ResumeHandleUnknownError`
    (which would conflate a read failure with a resume refusal on a surface whose
    whole justification is that it is weaker than resume).

    The attribution names the CAUSE CLASS ONLY — no exception text, no resolved
    filesystem path.
    """
    config = _config(tmp_path)
    with pytest.raises(PausedWorkflowStateUnavailableError) as excinfo:
        await read_paused_workflow_state(
            _Workflow(),  # pyright: ignore[reportArgumentType]
            resume_handle=_WORKFLOW_ID,
            config=config,
        )
    assert not isinstance(excinfo.value, ResumeHandleUnknownError)
    message = str(excinfo.value)
    assert str(tmp_path) not in message
    assert "Errno" not in message
    assert "Traceback" not in message
    assert excinfo.value.cause.value == "absent"


@pytest.mark.asyncio
async def test_ac8_resume_side_cause_attribution_uses_the_same_vocabulary(
    tmp_path: Path,
) -> None:
    """AC #8 — the SAME five identifiers are carried by BOTH surfaces, so the
    operator never receives two names for one state. `resume()`'s EXISTING fail
    class is refined, not replaced by a peer class."""
    config = _config(tmp_path)
    with pytest.raises(ResumeHandleUnknownError) as excinfo:
        await resume(
            _Workflow(),  # pyright: ignore[reportArgumentType]
            resume_handle=_WORKFLOW_ID,
            config=config,
        )
    assert excinfo.value.cause is PauseJournalReadCause.ABSENT
    assert excinfo.value.retryable is False


# --------------------------------------------------------------------------
# AC #9 — the one-authority criterion, statically checkable
# --------------------------------------------------------------------------


def test_ac9_accessor_contains_no_recursion_and_reads_no_nested_carrier_field() -> None:
    """AC #9 — the one-authority criterion, carried VERBATIM from CP spec v1.112
    §2.3: *the Runtime accessor contains NO recursion over `PauseSnapshot` and reads
    NO nested resume-carrier field.* Every classification comes from CP's projection
    surface.

    "Must not re-walk" as prose is not verifiable; this is.
    """
    import ast
    import inspect

    source = inspect.getsource(read_paused_workflow_state)
    tree = ast.parse(source.lstrip())
    nested_carrier_fields = {
        "fan_out_resume",
        "peer_fan_out_resume",
        "paused_child_branches",
        "pre_dispatch_gate_owning_branches",
        "effect_fence_paused_branches",
        "effect_fence_resume",
        "orchestrator_effect_fence_resume",
        "child_snapshot",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            assert node.attr not in nested_carrier_fields, node.attr
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id != "read_paused_workflow_state"


# --------------------------------------------------------------------------
# AC #11 / #12 — the projection's exclusions + total enumeration
# --------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ac11_projection_excludes_every_named_field(tmp_path: Path) -> None:
    """AC #11 — the projection carries NONE of: `summary_text`; orchestrator or
    branch outputs; `external_references` / `relevant_entries`; `snapshot_hash` /
    `state_ledger_anchor` / `hitl_gate_config_hash`; the raw `PauseSnapshot` — and,
    the LOAD-BEARING one, no identity value whatsoever on `UniformFallbackOnly` /
    `TransitivelyPaused` (ABSENT, not empty, not opaque, not redacted)."""
    config = _config(tmp_path)
    snapshot = await _capture(tmp_path, run_id="run-excl")
    read = await read_paused_workflow_state(
        _Workflow(),  # pyright: ignore[reportArgumentType]
        resume_handle=_WORKFLOW_ID,
        config=config,
    )
    dumped = read.model_dump(mode="json")
    for excluded in (
        "summary_text",
        "state_summary",
        "orchestrator_output",
        "output",
        "external_references",
        "relevant_entries",
        "snapshot_hash",
        "state_ledger_anchor",
        "hitl_gate_config_hash",
        "run_id",
    ):
        assert excluded not in repr(dumped), excluded
    assert snapshot.run_id not in repr(dumped)
    assert snapshot.snapshot_hash not in repr(dumped)


@pytest.mark.asyncio
async def test_ac12_total_enumeration_across_both_uniform_fallback_source_shapes(
    tmp_path: Path,
) -> None:
    """AC #12 — (a) a pre-dispatch gate-owning location appears ALONGSIDE an
    addressable one; (b) a top-level LINEAR HITL pause with no fan-out carrier
    appears as `uniform-fallback-only`.

    Omitting either INVERTS the operator's safety judgment ("one location, uniform
    is safe" when the true set has two); rendering (b) as addressable hands the
    operator a key the resolver SILENTLY IGNORES rather than refuses.
    """
    config = _config(tmp_path)
    workflow = _Workflow()

    # (a)
    await _capture(
        tmp_path,
        run_id="run-mixed",
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(),
            branch_count=2,
            pre_dispatch_gate_owning_branches=(
                PreDispatchGateOwningBranchResumeState(
                    branch_index=0, step_id="p0", step_kind=StepKind.SUB_AGENT_DISPATCH.value
                ),
            ),
            paused_child_branches=(
                PausedChildBranchResumeState(
                    branch_index=1,
                    step_id="w1",
                    child_snapshot=await _child_snapshot(tmp_path, run_id="child-X"),
                ),
            ),
        ),
    )
    mixed = await read_paused_workflow_state(workflow, resume_handle=_WORKFLOW_ID, config=config)
    variants = [loc.variant for loc in mixed.locations]
    assert PauseLocationVariant.UNIFORM_FALLBACK_ONLY in variants
    assert PauseLocationVariant.HITL_ADDRESSABLE in variants

    # (b)
    await _capture(tmp_path, run_id="run-root-only")
    root_only = await read_paused_workflow_state(
        workflow, resume_handle=_WORKFLOW_ID, config=config
    )
    assert len(root_only.locations) == 1
    assert isinstance(root_only.locations[0], DepthZeroRootUniformFallbackOnlyLocation)


# --------------------------------------------------------------------------
# AC #13 — the emission pair
# --------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ac13a_successful_read_emits_token_and_four_per_variant_counts(
    tmp_path: Path,
) -> None:
    """AC #13(a) — FOUR counts, not one aggregate total. A single scalar cannot
    express classification, and an aggregate-only assertion would let an
    implementation pass this execution-authority AC while violating the canonical
    OD contract. Never the locations' payload; never the never-keyable identity."""
    config = _config(tmp_path)
    await _capture(tmp_path, run_id="run-emit")
    read = await read_paused_workflow_state(
        _Workflow(),  # pyright: ignore[reportArgumentType]
        resume_handle=_WORKFLOW_ID,
        config=config,
    )
    rows = _sink_rows(tmp_path)
    assert len(rows) == 1
    row = rows[0]
    assert row.event_kind is PauseStateEventKind.ACCESSOR_READ
    assert row.succeeded is True
    assert row.staleness_token == read.staleness_token
    assert row.cause_attribution is None
    assert (row.hitl_addressable_count, row.effect_fence_addressable_count) == (0, 0)
    assert (row.uniform_fallback_only_count, row.transitively_paused_count) == (1, 0)
    assert "run-emit" not in repr(row.model_dump())


@pytest.mark.asyncio
async def test_ac13b_failed_read_still_emits_with_cause_and_no_token(tmp_path: Path) -> None:
    """AC #13(b) — a failed read MUST still emit; silence is not the failure
    disposition. It carries `workflow_id` + the cause, and NO token and NO count,
    because §14.14.9.4 returns no projection and mints no token on this path."""
    config = _config(tmp_path)
    with pytest.raises(PausedWorkflowStateUnavailableError):
        await read_paused_workflow_state(
            _Workflow(),  # pyright: ignore[reportArgumentType]
            resume_handle=_WORKFLOW_ID,
            config=config,
        )
    rows = _sink_rows(tmp_path)
    assert len(rows) == 1
    row = rows[0]
    assert row.succeeded is False
    assert row.cause_attribution == "absent"
    assert row.staleness_token is None
    assert row.hitl_addressable_count is None
    assert row.transitively_paused_count is None


@pytest.mark.asyncio
async def test_ac13a_prime_events_are_retrievable_from_a_real_fresh_process_sink(
    tmp_path: Path,
) -> None:
    """AC #13(a′) — the FRESH-PROCESS sink, by RETRIEVAL not by emit-call.

    Both events fire PRE-BOOTSTRAP, before the SDK `TracerProvider` and the audit
    writers exist, so a default proxy provider records nothing. An "the emit fired"
    assertion against a proxy provider is precisely the false green this AC exists
    to foreclose — so this asserts the events are **retrievable from a real sink**
    after a first-call-in-a-new-process read and a first-call refusal.

    "Fresh process" is modelled faithfully by resolving the sink from `config`
    alone, exactly as a restarted process would: nothing in this test shares state
    with the emitting call except the filesystem.
    """
    config = _config(tmp_path)
    workflow = _Workflow()
    await _capture(tmp_path, run_id="run-fresh")
    read = await read_paused_workflow_state(workflow, resume_handle=_WORKFLOW_ID, config=config)
    composed = AccessorDerivedResumeContext.from_pause_state(read, hitl_response=_hitl())
    await _capture(tmp_path, run_id="run-fresh-2")
    with pytest.raises(ResumePauseStateStaleError):
        await resume(
            workflow,  # pyright: ignore[reportArgumentType]
            resume_handle=_WORKFLOW_ID,
            resume_context=composed,
            config=config,
        )

    # A sink resolved from config alone — the fresh-process view.
    rows = pause_state_sink_for(_config(tmp_path), _WORKLOAD).read_all()
    kinds = [row.event_kind for row in rows]
    assert PauseStateEventKind.ACCESSOR_READ in kinds
    assert PauseStateEventKind.STALENESS_REFUSED_RESUME in kinds


@pytest.mark.asyncio
async def test_ac13c_the_pair_shares_one_staleness_token(tmp_path: Path) -> None:
    """AC #13(c) — the refusing `resume()` emits the SAME staleness token as the
    successful read that produced it, so the two are reconstructable as ONE causal
    pair from telemetry alone.

    Also asserts the refusal event is REPRESENTABLE AT ALL: it is raised
    pre-bootstrap, before any `(ResumeAttempt, ResumeOutcome)` exists, so it rides
    the additive OD §30.5.2 carrier — NOT the unchanged frozen
    `PauseResumeAuditPayload`, which has no field for the token.
    """
    config = _config(tmp_path)
    workflow = _Workflow()
    await _capture(tmp_path, run_id="run-pair")
    read = await read_paused_workflow_state(workflow, resume_handle=_WORKFLOW_ID, config=config)
    composed = AccessorDerivedResumeContext.from_pause_state(read, hitl_response=_hitl())
    await _capture(tmp_path, run_id="run-pair-2")
    with pytest.raises(ResumePauseStateStaleError):
        await resume(
            workflow,  # pyright: ignore[reportArgumentType]
            resume_handle=_WORKFLOW_ID,
            resume_context=composed,
            config=config,
        )
    rows = _sink_rows(tmp_path)
    read_row = next(r for r in rows if r.event_kind is PauseStateEventKind.ACCESSOR_READ)
    refusal_row = next(
        r for r in rows if r.event_kind is PauseStateEventKind.STALENESS_REFUSED_RESUME
    )
    assert read_row.staleness_token == refusal_row.staleness_token == read.staleness_token
    assert refusal_row.succeeded is False
    assert refusal_row.cause_attribution is None


def test_ac13_payload_enforces_the_outcome_split_and_shares_one_sampling_rate() -> None:
    """AC #13 — the outcome split is ENFORCED by the OD carrier, not merely
    documented; and §30.5.4's sampling ruling gives BOTH event kinds the SAME head
    rate, because §30.5.3's pairing requirement is only sound if BOTH members of a
    pair are retained."""
    assert PAUSE_STATE_EVENT_HEAD_SAMPLING_RATE == 1.0
    with pytest.raises(ValidationError):  # a successful read with no token
        PauseStateAuditPayload(
            event_kind=PauseStateEventKind.ACCESSOR_READ,
            workflow_id=_WORKFLOW_ID,
            succeeded=True,
            hitl_addressable_count=0,
            effect_fence_addressable_count=0,
            uniform_fallback_only_count=1,
            transitively_paused_count=0,
        )
    with pytest.raises(ValidationError):  # a successful read with a single total only
        PauseStateAuditPayload(
            event_kind=PauseStateEventKind.ACCESSOR_READ,
            workflow_id=_WORKFLOW_ID,
            succeeded=True,
            staleness_token="tok",
            hitl_addressable_count=1,
        )
    with pytest.raises(ValidationError):  # a failed read carrying a token
        PauseStateAuditPayload(
            event_kind=PauseStateEventKind.ACCESSOR_READ,
            workflow_id=_WORKFLOW_ID,
            succeeded=False,
            cause_attribution="absent",
            staleness_token="tok",
        )
    with pytest.raises(ValidationError):  # a refusal with no token
        PauseStateAuditPayload(
            event_kind=PauseStateEventKind.STALENESS_REFUSED_RESUME,
            workflow_id=_WORKFLOW_ID,
            succeeded=False,
        )


# --------------------------------------------------------------------------
# AC #15 / #16(a) — the source-shape sub-discriminator, detect-then-refuse
# --------------------------------------------------------------------------


def test_ac15a_step_kind_is_unrepresentable_where_the_source_shape_lacks_it() -> None:
    """AC #15(a) — for `EffectFenceAddressable` and `UniformFallbackOnly`, a
    projection sourced from a shape WITHOUT `step_kind` cannot be constructed
    carrying one, and one sourced from a shape WITH it cannot be constructed
    without one.

    Modelling `step_kind` as a plain optional field on a flat per-variant type would
    readmit exactly the illegal state the closed union exists to close, one level
    down. Assert the REFUSALS, not merely that the happy paths work.
    """
    from harness_cp.pause_state_projection import (
        BranchEffectFenceAddressableLocation,
    )
    from harness_cp.pause_state_projection import (
        DepthZeroRootUniformFallbackOnlyLocation as _Root,
    )
    from harness_cp.pause_state_projection import (
        LinearEffectFenceAddressableLocation as _Linear,
    )
    from harness_cp.pause_state_projection import (
        PreDispatchUniformFallbackOnlyLocation as _PreDispatch,
    )

    with pytest.raises(ValidationError):  # LINEAR shape cannot carry a step_kind
        _Linear(
            pause_reason=WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS,
            step_index=0,
            idempotency_key="k",
            step_kind=StepKind.TOOL_STEP,  # pyright: ignore[reportCallIssue]
        )
    with pytest.raises(ValidationError):  # depth-0 root shape cannot carry a step_kind
        _Root(
            pause_reason=WorkflowPauseReason.HITL_PENDING,
            step_index=0,
            step_kind=StepKind.TOOL_STEP,  # pyright: ignore[reportCallIssue]
        )
    with pytest.raises(ValidationError):  # branch shape cannot omit its step_kind
        BranchEffectFenceAddressableLocation(  # pyright: ignore[reportCallIssue]
            pause_reason=WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS,
            step_index=0,
            idempotency_key="k",
            step_id="s",
            branch_index=0,
        )
    with pytest.raises(ValidationError):  # pre-dispatch shape cannot omit its step_kind
        _PreDispatch(  # pyright: ignore[reportCallIssue]
            pause_reason=WorkflowPauseReason.HITL_PENDING, step_index=0, step_id="s", branch_index=0
        )


def test_ac15b_the_key_field_is_unrepresentable_on_the_crash_reconstruction_shape() -> None:
    """AC #15(b) — the HARDER half, and the one a single optional-field model would
    silently pass.

    The empty-`idempotency_key` crash-reconstruction source shape cannot be
    constructed carrying a key AT ALL, and — symmetrically — a normal branch source
    shape cannot be constructed WITHOUT one. Without this, an implementation using
    ONE `EffectFenceAddressable` model with an optional key satisfies AC #16 by
    simply omitting the key for crash reconstruction, while still permitting a
    normal projection with no key and a crash-reconstruction projection with one —
    both illegal states, both representable.
    """
    from harness_cp.pause_state_projection import BranchEffectFenceAddressableLocation

    with pytest.raises(ValidationError):  # crash-reconstruction shape cannot carry a key
        CrashReconstructionEffectFenceAddressableLocation(
            pause_reason=WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS,
            step_index=0,
            step_id="s",
            step_kind=StepKind.TOOL_STEP,
            branch_index=0,
            idempotency_key="k",  # pyright: ignore[reportCallIssue]
        )
    with pytest.raises(ValidationError):  # normal branch shape cannot omit its key
        BranchEffectFenceAddressableLocation(  # pyright: ignore[reportCallIssue]
            pause_reason=WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS,
            step_index=0,
            step_id="s",
            step_kind=StepKind.TOOL_STEP,
            branch_index=0,
        )
    with pytest.raises(ValidationError):  # ... and never an EMPTY key either
        BranchEffectFenceAddressableLocation(
            pause_reason=WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS,
            step_index=0,
            step_id="s",
            step_kind=StepKind.TOOL_STEP,
            branch_index=0,
            idempotency_key="",
        )


@pytest.mark.asyncio
async def test_ac16a_empty_fence_key_projects_with_the_key_absent(tmp_path: Path) -> None:
    """AC #16(a) — a fan-out crash-reconstruction pause whose fence carrier holds an
    EMPTY `idempotency_key` projects as `EffectFenceAddressable` with the key field
    ABSENT (its own source shape), never carrying a `""` key value.

    Advertising it as addressable would hand the operator a `""` key both resume
    sites ignore on their truthiness check — the response is silently DROPPED, not
    refused.
    """
    config = _config(tmp_path)
    await _capture(
        tmp_path,
        run_id="run-crash-reconstruct",
        pause_reason=WorkflowPauseReason.EFFECT_FENCE_AMBIGUOUS,
        peer_fan_out_resume=PeerFanOutResumeState(
            branches=(),
            branch_count=1,
            effect_fence_paused_branches=(
                EffectFencePausedBranchResumeState(
                    branch_index=0,
                    step_id="p0",
                    step_kind=StepKind.TOOL_STEP.value,
                    idempotency_key="",
                ),
            ),
        ),
    )
    read = await read_paused_workflow_state(
        _Workflow(),  # pyright: ignore[reportArgumentType]
        resume_handle=_WORKFLOW_ID,
        config=config,
    )
    fence = next(
        loc
        for loc in read.locations
        if loc.variant is PauseLocationVariant.EFFECT_FENCE_ADDRESSABLE
    )
    assert isinstance(fence, CrashReconstructionEffectFenceAddressableLocation)
    assert "idempotency_key" not in fence.model_dump()


# --------------------------------------------------------------------------
# Input-triple identity + declared postures
# --------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_accessor_requires_the_same_durable_opt_in_resume_requires(
    tmp_path: Path,
) -> None:
    """§14.14.9.1 — the input triple is IDENTICAL to `resume()`'s `resume_handle`
    mode, including the durable opt-in. A pre-flight read that demanded information
    the operator does not yet possess would be worthless."""
    with pytest.raises(ResumeArgsError):
        await read_paused_workflow_state(
            _Workflow(),  # pyright: ignore[reportArgumentType]
            resume_handle=_WORKFLOW_ID,
            config=_config(tmp_path, durable=False),
        )


@pytest.mark.asyncio
async def test_workflow_match_guard_runs_before_any_projection_is_returned(
    tmp_path: Path,
) -> None:
    """§14.14.9.4 — the accessor MUST NOT hand back a projection that the IDENTICAL
    inputs would then be refused for at `resume()`. Returning one would make the
    promised `workflow-mismatch` cause unreachable and invite the operator to
    compose a response map for a state they cannot resume."""
    config = _config(tmp_path)
    store = _store(tmp_path)
    other = await DurablePauseResumeProtocol(
        state_ledger_writer=object(),
        state_ledger_reader=object(),
        pause_context_reader=lambda: (_summary(), _ANCHOR),
        store=store,
    ).capture_pause_snapshot("some-other-wf", "run-x", 0, WorkflowPauseReason.HITL_PENDING)
    assert other.workflow_id == "some-other-wf"
    # The record is journaled under the OTHER workflow's key, so reading OUR handle
    # is `absent`; the mismatch branch is exercised by planting the foreign record
    # under our own key.
    journal = store._journal_file(_WORKFLOW_ID)  # pyright: ignore[reportPrivateUsage]
    foreign = store._journal_file("some-other-wf")  # pyright: ignore[reportPrivateUsage]
    journal.write_text(
        foreign.read_text(encoding="utf-8").replace("some-other-wf", _WORKFLOW_ID, 1),
        encoding="utf-8",
    )
    with pytest.raises(PausedWorkflowStateUnavailableError) as excinfo:
        await read_paused_workflow_state(
            _Workflow(),  # pyright: ignore[reportArgumentType]
            resume_handle=_WORKFLOW_ID,
            config=config,
        )
    assert excinfo.value.cause is PauseJournalReadCause.WORKFLOW_MISMATCH


@pytest.mark.asyncio
async def test_step_index_range_guard_is_not_re_implemented_at_the_read(
    tmp_path: Path,
) -> None:
    """§14.14.9.4 — the STEP-INDEX-RANGE asymmetry is DELIBERATE. A read may
    legitimately surface a pause whose step index a CHANGED workflow can no longer
    accept; refusing that read would hide from the operator the very state they need
    to diagnose. The guard stays `resume()`'s."""
    config = _config(tmp_path)
    await _capture(tmp_path, run_id="run-oob", step_index=1)
    narrowed = _Workflow(step_count=1)  # step_index 1 is now out of range
    read = await read_paused_workflow_state(
        narrowed,  # pyright: ignore[reportArgumentType]
        resume_handle=_WORKFLOW_ID,
        config=config,
    )
    assert read.locations  # the read SUCCEEDS


def test_token_property_holds_by_construction_over_journal_growth(tmp_path: Path) -> None:
    """§30 term 1 — the token MUST differ between any two durably-journaled pause
    records of the same workflow a caller could successively observe.

    Verified by execution over the substrate invariant it rests on (§14.14.8:
    append-only, NEVER truncated): the record count strictly increases per capture,
    so successive observations differ even when the two snapshots hash identically.
    """
    store = _store(tmp_path)
    journal = store._journal_file(_WORKFLOW_ID)  # pyright: ignore[reportPrivateUsage]
    journal.parent.mkdir(parents=True, exist_ok=True)
    line = f'{{"workflow_id": "{_WORKFLOW_ID}", "pause_snapshot": {{}}}}'
    tokens: list[str | None] = []
    for _ in range(3):
        with journal.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
        tokens.append(mint_staleness_token(store.read_latest_attributed(_WORKFLOW_ID)))
    assert all(t is not None for t in tokens)
    assert len(set(tokens)) == 3  # identical bytes, three DISTINCT tokens
