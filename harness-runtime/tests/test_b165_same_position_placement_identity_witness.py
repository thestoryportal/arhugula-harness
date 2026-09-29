"""B-165 placement-identity boundaries after CP v1.120 first-match selection.

Manifests and the CP fold may retain two PRE_ACTION declarations at one position.
The Runtime composer selects one governing PRE_ACTION placement, including in
the real branch context and across all blast-radius tiers. SUB_AGENT_BOUNDARY
still loops per declaration: duplicate positions can produce two same-key writes.
That remains the open Class 1 B-165 residual at
`.harness/class_1_fork_b165_same_position_placement_identity_collision.md`.
The raw key function uses branch and position; its duplicate-key behavior is
also tested separately as a state-ledger invariant.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, cast

import pytest
from harness_core import PersonaTier, WorkloadClass
from harness_core.identity import StepID
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.gate_level_rule import BlastRadiusTier
from harness_cp.hitl_placement import HITLPlacement, HITLPlacementKind
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.hitl_timeout_degradation import WebhookConfig
from harness_cp.pause_state_projection import pre_dispatch_gate_owning_branch_identity
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.persona_engine_hitl_matrix import SynchronyClass, matrix_cell_for
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver_types import (
    StepExecutionContext,
    StepKind,
    WorkflowStep,
    compose_branch_child_context,
    fold_step_hitl_placements,
)
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_is.state_ledger_entry_schema import Identifier as _Identifier
from harness_od.audit_ledger_types import SignatureAlgorithm
from harness_runtime.lifecycle.ask_user_question_surface import (
    AskUserQuestionResult,
    AskUserQuestionSurface,
)
from harness_runtime.lifecycle.hitl_gate_composer import (
    HITLPauseRequestedSignal,
    RuntimeHITLGateComposer,
    compose_hitl_action_id,
    resolve_escalation_instance_id,
)
from harness_runtime.lifecycle.webhook_delivery_composer import WebhookDeliveryComposer
from opentelemetry.sdk.trace import TracerProvider

_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-b165")
_RUN_ID = "run-b165-1"
_PARENT_ACTION_ID = "workflow:wf-b165:step:0"
_GATE = HITLPlacementKind.PRE_ACTION


# ---------------------------------------------------------------------------
# Fixtures — self-contained (sibling records use the same shapes; duplicating
# them here keeps this module importable on its own, per the axis-isolation
# witness-homing convention).
# ---------------------------------------------------------------------------


def _context(*, branch_index: int | None = 0, basis: str | None = None) -> StepExecutionContext:
    from harness_as.sandbox_tier import SandboxTier
    from harness_core import ActionID
    from harness_cp.gate_level_rule import GateLevel

    return StepExecutionContext(
        workflow_id="wf-b165",
        parent_action_id=ActionID(_PARENT_ACTION_ID),
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=_ACTOR,
        parent_entry_hash="",
        parent_idempotency_key=_Identifier("b165-idempotency-key"),
        tenant_id=None,
        step_index=0,
        branch_index=branch_index,
        pre_dispatch_escalation_basis=basis,
    )


def _gate_owning_context(branch_index: int) -> StepExecutionContext:
    """A fan-out branch context whose basis is derived the way PRODUCTION derives
    it — UNCONDITIONALLY at both fan-out branch-composition sites, not only on
    resume (CP spec v1.119 §0.4.1)."""
    return _context(
        branch_index=branch_index,
        basis=pre_dispatch_gate_owning_branch_identity(_RUN_ID, branch_index),
    )


def _step(placements: tuple[HITLPlacement, ...]) -> WorkflowStep:
    step = WorkflowStep(
        step_id=StepID("step-0"), step_kind=StepKind.INFERENCE_STEP, step_payload={}
    )

    class _StepWithPlacements:
        def __init__(self, inner: WorkflowStep) -> None:
            self._inner = inner
            self.hitl_placements = placements

        def __getattr__(self, name: str) -> Any:
            return getattr(self._inner, name)

    return cast(WorkflowStep, _StepWithPlacements(step))


class _Surface:
    def __init__(self, results: list[AskUserQuestionResult]) -> None:
        self._results = list(results)
        self.calls: list[str] = []

    async def ask(
        self, prompt: str, options: Sequence[HITLResponse], timeout: float | None
    ) -> AskUserQuestionResult:
        self.calls.append(prompt)
        if not self._results:
            raise RuntimeError("surface queue empty")
        return self._results.pop(0)


class _Inner:
    def dispatch(
        self, binding: Any, step: WorkflowStep, *, step_context: StepExecutionContext
    ) -> Mapping[str, Any]:
        return {"inner_dispatched": True}


class _LedgerWriter:
    def __init__(self) -> None:
        self.appends: list[Any] = []

    def append(self, payload: Any, key: Any) -> Any:
        self.appends.append((payload, key))
        return ("dummy-entry-hash", payload, key)


class _AuditWriter:
    def __init__(self) -> None:
        self.appends: list[Any] = []

    def append(self, *, tenant_id: Any, audit_entry: Any) -> Any:
        self.appends.append((tenant_id, audit_entry))
        return ("dummy-write-result", audit_entry)


class _OkResponse:
    status_code = 200
    text = "ok"

    def json(self) -> dict[str, Any]:
        return {}


class _OkHTTPClient:
    async def __aenter__(self) -> _OkHTTPClient:
        return self

    async def __aexit__(self, *_: Any) -> None:
        return None

    async def post(self, *_: Any, **__: Any) -> _OkResponse:
        return _OkResponse()


def _webhook(provider: TracerProvider) -> WebhookDeliveryComposer:
    return WebhookDeliveryComposer(
        retry_max_attempts=1,
        http_client_factory=lambda: _OkHTTPClient(),
        tracer_provider=provider,
        webhook_config=WebhookConfig(
            webhook_id="wh-b165",
            endpoint_url="https://example.test/hook",
            timeout=5,
            degradation_mode="fail-closed",
        ),
    )


def _composer(
    provider: TracerProvider,
    *,
    surface: _Surface,
    ledger_writer: _LedgerWriter,
    audit_writer: _AuditWriter,
    webhook: WebhookDeliveryComposer | None = None,
    pause_resume_protocol: Any = None,
) -> RuntimeHITLGateComposer:
    return RuntimeHITLGateComposer(
        inner=cast(Any, _Inner()),
        applicable_placements=frozenset({_GATE}),
        ask_user_question_surface=cast(AskUserQuestionSurface, surface),
        ledger_writer=cast(Any, ledger_writer),
        audit_writer=cast(Any, audit_writer),
        tracer_provider=provider,
        audit_signing_key_id="harness-runtime-b165",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        procedural_tier_snapshot_resolver=lambda: _Identifier("b" * 64),
        webhook_delivery_composer=webhook,
        pause_resume_protocol=pause_resume_protocol,
    )


# ---------------------------------------------------------------------------
# 1 — the DECLARATION is admissible: nothing rejects two same-position placements
# ---------------------------------------------------------------------------


# mutation-probe: add a field_validator to `WorkflowManifestEntry.hitl_placements`
# rejecting a tuple with two entries at the same `position`.
def test_the_manifest_admits_two_placements_at_the_same_position() -> None:
    """The premise's FIRST conjunct — the shape must be declarable at all.

    Asserted through a full `model_validate` (not `model_copy`, which bypasses
    validation) so a validator added anywhere in the model would red this.
    """
    candidate = ProviderCandidate(
        provider="anthropic", model="claude-opus-5", family=ProviderFamily.ANTHROPIC
    )
    entry = WorkflowManifestEntry(
        workflow_id="wf-b165",
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        engine_class=EngineClass.SAVE_POINT_CHECKPOINT,
        topology_pattern=TopologyPattern.SINGLE_THREADED_LINEAR,
        layer_budgets=(),
        fallback_chain=FallbackChain(primary=candidate, same_family=(), cross_family=()),
        hitl_placements=(
            HITLPlacement(position=_GATE),
            HITLPlacement(position=_GATE),
        ),
        per_step_overrides={},
    )
    revalidated = WorkflowManifestEntry.model_validate(entry.model_dump())

    assert len(revalidated.hitl_placements) == 2
    assert [p.position for p in revalidated.hitl_placements] == [_GATE, _GATE]


# ---------------------------------------------------------------------------
# 2 — the FOLD preserves both (it disclaims de-duplication in its own docstring)
# ---------------------------------------------------------------------------


# mutation-probe: make `fold_step_hitl_placements` de-duplicate the workflow tuple
# by `position` before returning it.
def test_the_add_only_fold_preserves_both_same_position_placements() -> None:
    """`fold_step_hitl_placements` forecloses the OVERRIDE introducing a duplicate
    position, and says so — but explicitly does NOT de-duplicate a workflow that
    itself declares two, calling that "a workflow-validation concern, out of scope
    here". Test 1 shows that workflow-validation does not exist, so the pair
    survives to the composer."""
    a = HITLPlacement(position=_GATE)
    b = HITLPlacement(position=_GATE)

    folded = fold_step_hitl_placements((a, b), None)

    assert len(folded) == 2
    assert [p.position for p in folded] == [_GATE, _GATE]


# ---------------------------------------------------------------------------
# 2-bis — the INTEGRATION link: does PRODUCTION hand the composer this shape?
# ---------------------------------------------------------------------------


# mutation-probe: in `hitl_gate_composer.dispatch`, drop the `step_context` arm of the
# placement lookup — i.e. make it read `getattr(step, "hitl_placements", ())` ONLY,
# instead of `getattr(step_context, ...) or getattr(step, ...)`.
#
# NAMED THIS WAY BECAUSE IT IS WHAT THIS TEST CAN ACTUALLY DETECT, and finding that out
# took two wrong answers. The obvious annotation — mutate `compose_branch_child_context`
# — is UNDETECTABLE here: this test's own `model_copy` below unconditionally overwrites
# `hitl_placements` and `pre_dispatch_escalation_basis` after calling it, so a mutation
# to that function is masked before either assertion reads the result. Worse, the probe
# driver initially reported that mutation as KILLED; it was a SyntaxError producing a
# collection failure, a vacuous kill indistinguishable from detection until the driver
# was taught to refuse syntax-breaking mutations. (Found by the merge gate's
# test-witness lens — the SIXTH annotation in this arc to name a site its test could not
# kill on, and the second whose "kill" was an artifact.)
#
# What this test uniquely pins is the PRODUCER SURFACE: the step it passes is PLAIN, so
# the gate can only fire if the composer reads placements off `step_context`. Deleting
# that arm makes both placements invisible and the gate never fires.
@pytest.mark.asyncio
async def test_the_production_branch_composition_selects_one_governing_placement() -> None:
    """A real branch context carries both declarations; Runtime gates once.

    The plain step has no test-only placements. The real manifest fold, branch
    context, and effective binding supply the pair through the production carrier.
    The separate driver-through-composer test witnesses the full round trip.
    """
    candidate = ProviderCandidate(
        provider="anthropic", model="claude-opus-5", family=ProviderFamily.ANTHROPIC
    )
    manifest = WorkflowManifestEntry(
        workflow_id="wf-b165",
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        engine_class=EngineClass.SAVE_POINT_CHECKPOINT,
        topology_pattern=TopologyPattern.PARALLELIZATION,
        layer_budgets=(),
        fallback_chain=FallbackChain(primary=candidate, same_family=(), cross_family=()),
        hitl_placements=(HITLPlacement(position=_GATE), HITLPlacement(position=_GATE)),
        per_step_overrides={},
    )
    binding = StepEffectiveBinding(
        step_id="step-0",
        model_binding=ModelBinding(provider="anthropic", model="claude-opus-5"),
        engine_class=EngineClass.SAVE_POINT_CHECKPOINT,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        override_applied=False,
        hitl_placement=None,
    )
    # SOLO_DEVELOPER × SAVE_POINT_CHECKPOINT must be a REAL, non-excluded,
    # SYNC_BLOCKING cell — asserted, not assumed, so a matrix change that moved this
    # pair to DURABLE_ASYNC would red here instead of silently re-routing the test.
    cell = matrix_cell_for(persona_tier=binding.persona_tier, engine_class=binding.engine_class)
    assert not cell.is_excluded
    assert cell.synchrony_class is SynchronyClass.SYNC_BLOCKING

    # The production composition, mirroring workflow_driver.py:8580-8606.
    child = compose_branch_child_context(
        _context(branch_index=None), branch_index=0, agent_role=cast(Any, "worker")
    ).model_copy(
        update={
            "hitl_placements": fold_step_hitl_placements(
                manifest.hitl_placements, binding.hitl_placement
            ),
            "pre_dispatch_escalation_basis": pre_dispatch_gate_owning_branch_identity(_RUN_ID, 0),
        }
    )
    assert len(child.hitl_placements) == 2, "production carries BOTH placements"
    assert child.pre_dispatch_escalation_basis is not None, "and the B-71 basis"

    provider = TracerProvider()
    surface = _Surface(
        [
            AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=1.0),
            AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=2.0),
        ]
    )
    ledger = _LedgerWriter()
    composer = _composer(
        provider, surface=surface, ledger_writer=ledger, audit_writer=_AuditWriter()
    )

    # A PLAIN step — no placements attached, so the test-only `getattr(step, ...)`
    # fallback finds nothing and the gate can only fire off `step_context`.
    plain_step = WorkflowStep(
        step_id=StepID("step-0"), step_kind=StepKind.INFERENCE_STEP, step_payload={}
    )

    await composer.dispatch(cast(Any, binding), plain_step, step_context=child)

    assert len(surface.calls) == 1, "first match gates once off the production carrier"
    keys = [str(key.idempotency_key) for _payload, key in ledger.appends]
    assert len(keys) == 1


# ---------------------------------------------------------------------------
# 3 — the synchronous venue selects one governing placement
# ---------------------------------------------------------------------------


# mutation-probe: bypass first-match selection so both declarations gate.
@pytest.mark.asyncio
async def test_two_same_position_placements_select_once_on_the_sync_venue() -> None:
    """Two declarations select one governing placement on the synchronous path.

    On a gate-owning fan-out branch the token IS resolved on the sync venue (the
    basis rides `StepExecutionContext` unconditionally), so this is not the
    token-free path the falsified first draft of `B-165` accidentally described.
    The composer selects one placement, so only one write carries the tokenized key.
    """
    provider = TracerProvider()
    surface = _Surface(
        [
            AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=1.0),
            AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=2.0),
        ]
    )
    ledger = _LedgerWriter()
    composer = _composer(
        provider, surface=surface, ledger_writer=ledger, audit_writer=_AuditWriter()
    )
    ctx = _gate_owning_context(0)

    # The governing write keeps the branch token; selection must not erase it.
    token = resolve_escalation_instance_id(ctx, _GATE)
    assert token is not None

    await composer.dispatch(
        cast(Any, object()),
        _step((HITLPlacement(position=_GATE), HITLPlacement(position=_GATE))),
        step_context=ctx,
    )

    assert len(surface.calls) == 1, "only the governing placement is gated"
    keys = [str(key.idempotency_key) for _payload, key in ledger.appends]
    expected = f"hitl:{_PARENT_ACTION_ID}:{_GATE.value}:{token}"
    assert keys == [expected], "one governing placement reaches the F2 write"


# ---------------------------------------------------------------------------
# 3-bis — first-match selection also governs the AUTO-APPROVE path
# ---------------------------------------------------------------------------


# mutation-probe: delete the AUTO-APPROVE audit write — the
# `_compose_and_persist_audit_off_loop(..., auto_approved=True)` call inside the
# `if not hitl_required:` skip block (~`hitl_gate_composer.py:2091`).
#
# READ_ONLY skips the prompt but still emits exactly one audit write for the
# governing placement. The second declaration must not reach either path.
@pytest.mark.parametrize("tier", list(BlastRadiusTier))
@pytest.mark.asyncio
async def test_one_governing_placement_on_every_blast_radius_including_auto_approve(
    tier: BlastRadiusTier,
) -> None:
    """One selected placement writes on every tier, including auto-approval.

    READ_ONLY asks no operator; the other tiers ask once. The production-valid
    blast-radius resolver keeps this distinct from the partial-binding sentinel.
    """
    provider = TracerProvider()
    surface = _Surface(
        [
            AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=1.0),
            AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=2.0),
        ]
    )
    ledger = _LedgerWriter()
    composer = RuntimeHITLGateComposer(
        inner=cast(Any, _Inner()),
        applicable_placements=frozenset({_GATE}),
        ask_user_question_surface=cast(AskUserQuestionSurface, surface),
        ledger_writer=cast(Any, ledger),
        audit_writer=cast(Any, _AuditWriter()),
        tracer_provider=provider,
        audit_signing_key_id="harness-runtime-b165",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        procedural_tier_snapshot_resolver=lambda: _Identifier("b" * 64),
        blast_radius_resolver=lambda _step: tier,
    )

    class _RealCellBinding:
        persona_tier = PersonaTier.SOLO_DEVELOPER
        engine_class = EngineClass.SAVE_POINT_CHECKPOINT

    ctx = _gate_owning_context(0).model_copy(
        update={
            "hitl_placements": (
                HITLPlacement(position=_GATE),
                HITLPlacement(position=_GATE),
            )
        }
    )
    plain_step = WorkflowStep(
        step_id=StepID("step-0"), step_kind=StepKind.INFERENCE_STEP, step_payload={}
    )

    await composer.dispatch(cast(Any, _RealCellBinding()), plain_step, step_context=ctx)

    keys = [str(key.idempotency_key) for _payload, key in ledger.appends]
    assert len(keys) == 1, f"one governing placement must write on {tier.name}"

    # The prompt count is the part that DOES vary — pinned so the auto-approve path is
    # a stated property of this test rather than an unnoticed side effect.
    expected_prompts = 0 if tier is BlastRadiusTier.READ_ONLY else 1
    assert len(surface.calls) == expected_prompts, (
        f"{tier.name}: expected {expected_prompts} prompts, got {len(surface.calls)}"
    )


# ---------------------------------------------------------------------------
# 4 — the DISCRIMINATOR: the token separates peer BRANCHES, not peer PLACEMENTS
# ---------------------------------------------------------------------------


# mutation-probe: make `pre_dispatch_gate_owning_branch_identity` ignore its
# `branch_index` argument (so peer branches stop being separable).
def test_the_b71_token_separates_peer_branches_but_not_peer_placements() -> None:
    """Keeps two facts apart that are easy to conflate.

    `B-71` is NOT broken: two PEER BRANCHES at the same position receive different
    keys, which is exactly the aliasing the arc closed. `B-165` is a different
    axis: within ONE branch, two placements at one position share both hashed
    inputs, so no token value can separate them. Asserting only the second half
    would read as a `B-71` regression report, which the evidence does not support.
    """
    branch_0 = _gate_owning_context(0)
    branch_1 = _gate_owning_context(1)

    token_0 = resolve_escalation_instance_id(branch_0, _GATE)
    token_1 = resolve_escalation_instance_id(branch_1, _GATE)

    # B-71 WORKS across peer branches.
    assert token_0 is not None and token_1 is not None
    assert token_0 != token_1
    assert compose_hitl_action_id(
        cast(Any, _PARENT_ACTION_ID), _GATE, token_0
    ) != compose_hitl_action_id(cast(Any, _PARENT_ACTION_ID), _GATE, token_1)

    # B-165: within ONE branch, two placements share every hashed input.
    placement_a = compose_hitl_action_id(cast(Any, _PARENT_ACTION_ID), _GATE, token_0)
    placement_b = compose_hitl_action_id(cast(Any, _PARENT_ACTION_ID), _GATE, token_0)
    assert placement_a == placement_b


# ---------------------------------------------------------------------------
# 5 — (a): the durable-async venue enters EXACTLY ONE escalation per pass
# ---------------------------------------------------------------------------


# mutation-probe: delete the `raise` that terminates `_escalate_to_secondary_channel`
# (making it fall through instead of `NoReturn`), so the loop reaches placement 2.
@pytest.mark.asyncio
async def test_the_durable_async_venue_enters_exactly_one_escalation_per_pass(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """(a) answered with a POSITIVE CONTROL, not an absence.

    The durable-async path does not write through this record's ledger writer, so
    "0 writes observed" is indistinguishable from "looked in the wrong place". The
    assertion is therefore on a COUNTER wrapping the real escalation: it must read
    exactly 1 — a number an unlooked probe cannot produce.
    """
    provider = TracerProvider()
    ledger = _LedgerWriter()

    class _PauseResumeProtocolDouble:
        """Non-`None` solely so `joint_binding_present` is True — the durable-async
        branch's precondition. It is never reached for anything else: the escalation
        raises first."""

        def __getattr__(self, name: str) -> Any:
            def _noop(*_a: Any, **_k: Any) -> None:
                return None

            return _noop

    composer = _composer(
        provider,
        surface=_Surface([]),
        ledger_writer=ledger,
        audit_writer=_AuditWriter(),
        webhook=_webhook(provider),
        pause_resume_protocol=cast(Any, _PauseResumeProtocolDouble()),
    )

    entered: list[str] = []
    real_escalate = RuntimeHITLGateComposer._escalate_to_secondary_channel

    async def _counting(self: Any, **kwargs: Any) -> Any:
        entered.append(str(kwargs["placement"].position.value))
        return await real_escalate(self, **kwargs)

    monkeypatch.setattr(RuntimeHITLGateComposer, "_escalate_to_secondary_channel", _counting)

    class _DurableAsyncBinding:
        """SOLO_DEVELOPER × RECONCILER_LOOP is a DURABLE_ASYNC, non-excluded cell."""

        persona_tier = PersonaTier.SOLO_DEVELOPER
        engine_class = EngineClass.RECONCILER_LOOP

    with pytest.raises(HITLPauseRequestedSignal):
        await composer.dispatch(
            cast(Any, _DurableAsyncBinding()),
            _step((HITLPlacement(position=_GATE), HITLPlacement(position=_GATE))),
            step_context=_gate_owning_context(0),
        )

    assert entered == [_GATE.value], (
        "TWO same-position placements were declared; the NoReturn escalation must "
        "make the second unreachable within one pass"
    )


# ---------------------------------------------------------------------------
# 5-bis — duplicate SUB_AGENT_BOUNDARY declarations still collide
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_duplicate_sub_agent_boundary_gates_still_share_one_key() -> None:
    """PRE_ACTION first-match does not silently close the boundary half of B-165."""
    boundary = HITLPlacement(position=HITLPlacementKind.SUB_AGENT_BOUNDARY)
    ctx = _gate_owning_context(0).model_copy(update={"hitl_placements": (boundary, boundary)})
    binding = StepEffectiveBinding(
        step_id="step-0",
        model_binding=ModelBinding(provider="anthropic", model="claude-opus-5"),
        engine_class=EngineClass.SAVE_POINT_CHECKPOINT,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        override_applied=False,
        hitl_placement=None,
    )
    surface = _Surface(
        [
            AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=1.0),
            AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=2.0),
        ]
    )
    ledger = _LedgerWriter()
    composer = RuntimeHITLGateComposer(
        inner=cast(Any, _Inner()),
        applicable_placements=frozenset({HITLPlacementKind.SUB_AGENT_BOUNDARY}),
        ask_user_question_surface=cast(AskUserQuestionSurface, surface),
        ledger_writer=cast(Any, ledger),
        audit_writer=cast(Any, _AuditWriter()),
        tracer_provider=TracerProvider(),
        audit_signing_key_id="harness-runtime-b165-boundary",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        procedural_tier_snapshot_resolver=lambda: _Identifier("b" * 64),
    )
    step = WorkflowStep(
        step_id=StepID("step-0"),
        step_kind=StepKind.SUB_AGENT_DISPATCH,
        step_payload={},
    )

    await composer.dispatch(cast(Any, binding), step, step_context=ctx)

    assert len(surface.calls) == 2
    keys = [str(key.idempotency_key) for _payload, key in ledger.appends]
    assert len(keys) == 2
    assert keys[0] == keys[1]


# ---------------------------------------------------------------------------
# 6 — the CONSEQUENCE, at the REAL writer: the second entry is DROPPED
# ---------------------------------------------------------------------------


# mutation-probe: widen the dedup predicate in `append_ledger_entry` to compare
# more than `idempotency_key` (e.g. also `timestamp`), so the second write lands.
def test_the_second_same_position_f2_entry_is_dropped_by_key_only_dedup(
    tmp_path: Path,
) -> None:
    """The real ledger deduplicates a repeated position key.

    This is a key-only writer invariant. PRE_ACTION first-match prevents a
    second write within one dispatch; duplicate SUB_AGENT_BOUNDARY declarations
    still reach the same key and remain the open B-165 residual.
    """
    from harness_is.jsonl_event_ledger_lifecycle import JsonlLedgerHandle
    from harness_is.state_ledger_write import (
        WRITER_OWNED_TIMESTAMP,
        EntryPayload,
        WriteKey,
        WriteResult,
        append_ledger_entry,
        read_ledger,
    )

    ledger_path = tmp_path / "state.jsonl"
    ledger_path.write_text("")
    handle = JsonlLedgerHandle(canonical_path=ledger_path, exists=True, entry_count=0)

    # Use the same boundary position whose two writer calls remain reachable.
    boundary = HITLPlacementKind.SUB_AGENT_BOUNDARY
    token = resolve_escalation_instance_id(_gate_owning_context(0), boundary)
    colliding = str(compose_hitl_action_id(cast(Any, _PARENT_ACTION_ID), boundary, token))

    def _write() -> WriteResult:
        payload = EntryPayload(
            action_id=_Identifier(colliding),
            idempotency_key=_Identifier(colliding),
            actor=_ACTOR,
            # The same sentinel the composer's own 8b-HITL write elects
            # (C-IS-07 §7.6.1) — so the two writes differ in NOTHING the
            # dedup could legitimately use to tell them apart.
            timestamp=WRITER_OWNED_TIMESTAMP,
            procedural_tier_snapshot_ref=_Identifier("b" * 64),
        )
        key = WriteKey(
            thread_id=_Identifier(f"hitl:{_PARENT_ACTION_ID}"),
            step_id=_Identifier(colliding),
            idempotency_key=_Identifier(colliding),
        )
        return append_ledger_entry(handle, payload, key)

    assert _write() is WriteResult.APPENDED
    assert _write() is WriteResult.IDEMPOTENT_NOOP
    assert len(read_ledger(handle)) == 1
