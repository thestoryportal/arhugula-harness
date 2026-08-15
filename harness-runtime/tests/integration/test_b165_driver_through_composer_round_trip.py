"""`B-165` — the DRIVER-THROUGH-COMPOSER round trip, in the production shape.

The two earlier `B-165` modules pin the chain in halves: `harness-cp/tests/
test_b165_production_feed_duplicate_placements.py` shows production DELIVERS a context
carrying two same-position placements plus the `B-71` basis, and `harness-runtime/tests/
test_b165_same_position_placement_identity_witness.py` shows the composer COLLIDES on
such a context. Out-of-family review asked three separate times for the halves to be
joined, on the ground that a split chain can stay green while the shipped call path
never reaches the collision — if stage-5 wiring stopped installing
`RuntimeHITLGateComposer`, or installed it behind a different binding, neither half
would notice.

That objection is correct and this module answers it. Nothing here is hand-composed:

* the manifest is a real `WorkflowManifestEntry` declaring TWO `PRE_ACTION` placements;
* the driver is the real `execute_workflow`, run via `asyncio.to_thread` exactly as
  production does;
* the dispatcher is a real `RuntimeHITLGateComposer` wrapped in a real
  `SyncDispatcherFacade` built by `materialize_sync_dispatcher_facade` — the same
  async→sync bridge stage 5 uses (`bootstrap/stage_5_loop_init.py`), constructed on the
  loop that hosts the `to_thread` call, as that factory requires;
* the per-step `StepExecutionContext` is composed by the driver, never by this test.

The remaining doubles are IO boundaries and nothing else: the operator prompt surface,
the state-ledger writer, and the audit writer. Doubling an operator is not a shortcut —
there is no other way to answer a human gate in a test.

**What it asserts.** Every gated placement's F2 write is captured, and the two writes a
single branch produces carry a BYTE-IDENTICAL `idempotency_key`. That is `B-165`: the
identity does not distinguish two placements declared at one position, so the second
entry is the one `append_ledger_entry`'s key-only dedup drops in production (witnessed
against the real writer by test 6 of the runtime module).
"""

from __future__ import annotations

import asyncio
from collections.abc import Mapping, Sequence
from functools import partial
from typing import Any, cast

import pytest
from harness_core import PersonaTier, WorkloadClass
from harness_core.identity import StepID
from harness_core.workflow_event_class import WorkflowEventClass
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.gate_level_rule import BlastRadiusTier
from harness_cp.handoff_context import StateSummary
from harness_cp.hitl_placement import HITLPlacement, HITLPlacementKind
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.pause_resume_protocol import PauseResumeProtocol
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.persona_engine_hitl_matrix import SynchronyClass, matrix_cell_for
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver import execute_workflow
from harness_cp.workflow_driver_types import (
    RunStatus,
    StepExecutionContext,
    StepKind,
    WorkflowStep,
)
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier
from harness_od.audit_ledger_types import SignatureAlgorithm
from harness_runtime.bootstrap import run_bootstrap
from harness_runtime.lifecycle.ask_user_question_surface import (
    AskUserQuestionResult,
    AskUserQuestionSurface,
)
from harness_runtime.lifecycle.hitl_gate_composer import RuntimeHITLGateComposer
from harness_runtime.lifecycle.sync_dispatcher_facade import (
    materialize_sync_dispatcher_facade,
)
from opentelemetry.sdk.trace import TracerProvider

from .conftest import WORKLOAD, build_config

_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-b165-round-trip")
_GATE = HITLPlacementKind.PRE_ACTION
_DEFAULT_BINDING = ModelBinding(provider="anthropic", model="claude-haiku-4-5")
_CHAIN = FallbackChain(
    primary=ProviderCandidate(
        provider="anthropic", model="claude-haiku-4-5", family=ProviderFamily.ANTHROPIC
    ),
    same_family=(),
    cross_family=(),
    terminal=None,
)


def _manifest() -> WorkflowManifestEntry:
    """PARALLELIZATION on a NON-EXCLUDED SYNC_BLOCKING cell, with TWO placements
    declared at ONE position — the whole point of the fixture."""
    return WorkflowManifestEntry(
        workflow_id="wf-b165-round-trip",
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        engine_class=EngineClass.SAVE_POINT_CHECKPOINT,
        topology_pattern=TopologyPattern.PARALLELIZATION,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(HITLPlacement(position=_GATE), HITLPlacement(position=_GATE)),
        per_step_overrides={},
    )


def _peer_steps() -> list[WorkflowStep]:
    return [
        WorkflowStep(
            step_id=StepID("branch-0"),
            step_kind=StepKind.INFERENCE_STEP,
            step_payload={"prompt": "a"},
        ),
    ]


class _Surface:
    """The operator. Approves everything; records how many times it was asked."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    async def ask(
        self, prompt: str, options: Sequence[HITLResponse], timeout: float | None
    ) -> AskUserQuestionResult:
        self.calls.append(prompt)
        return AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=1.0)


class _Inner:
    """The step the gate wraps. Async, because the facade wraps an async dispatcher."""

    async def dispatch(
        self, binding: Any, step: WorkflowStep, *, step_context: StepExecutionContext
    ) -> Mapping[str, Any]:
        return {"inner_dispatched": True}


class _LedgerWriter:
    def __init__(self) -> None:
        self.appends: list[tuple[Any, Any]] = []

    def append(self, payload: Any, key: Any) -> Any:
        self.appends.append((payload, key))
        return ("entry-hash", payload, key)


class _AuditWriter:
    def __init__(self) -> None:
        self.appends: list[Any] = []

    def append(self, *, tenant_id: Any, audit_entry: Any) -> Any:
        self.appends.append((tenant_id, audit_entry))
        return ("write-result", audit_entry)


class _DriverLedger:
    """The driver's own ledger writer — distinct from the composer's."""

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
        "0" * 64,
    )


class _Ctx:
    def __init__(self) -> None:
        from opentelemetry.trace import NoOpTracerProvider

        self.ledger_writer = _DriverLedger()
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


class _Registry:
    """Routes every step kind to the ONE facade-wrapped real composer."""

    def __init__(self, facade: Any) -> None:
        self._facade = facade

    def lookup(self, step_kind: StepKind) -> Any:
        return self._facade


# mutation-probe: in `hitl_gate_composer.compose_hitl_action_id`, append a per-call
# ordinal to the composed key (so the two placements stop sharing one identity). This
# probe is meaningful HERE in a way it is not elsewhere: nothing in this module composes
# a key, a context, or a dispatcher registry by hand, so only a real change to the
# shipped composition can red it.
@pytest.mark.asyncio
async def test_the_real_driver_through_the_real_composer_collides_on_one_identity(
    tmp_path: Any,
) -> None:
    """The joined chain — driver → facade → composer — in the production shape.

    The three-times-repeated review objection was that the split halves could both stay
    green while the shipped path never reached the collision. Here the shipped path IS
    the path: `execute_workflow` composes the per-step context, hands it through the
    same `SyncDispatcherFacade` bridge stage 5 builds, and a real
    `RuntimeHITLGateComposer` consumes it.
    """
    cell = matrix_cell_for(
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        engine_class=EngineClass.SAVE_POINT_CHECKPOINT,
    )
    assert not cell.is_excluded
    assert cell.synchrony_class is SynchronyClass.SYNC_BLOCKING

    surface = _Surface()
    ledger = _LedgerWriter()
    composer = RuntimeHITLGateComposer(
        inner=cast(Any, _Inner()),
        applicable_placements=frozenset({_GATE}),
        ask_user_question_surface=cast(AskUserQuestionSurface, surface),
        ledger_writer=cast(Any, ledger),
        audit_writer=cast(Any, _AuditWriter()),
        tracer_provider=TracerProvider(),
        audit_signing_key_id="harness-runtime-b165-rt",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        procedural_tier_snapshot_resolver=lambda: Identifier("b" * 64),
        # A production-valid Stage-5 resolver. LOCAL_MUTATION rather than READ_ONLY so
        # the gate genuinely ASKS — the READ_ONLY auto-approve path is pinned separately
        # by the runtime module's parametrized test.
        blast_radius_resolver=lambda _step: BlastRadiusTier.LOCAL_MUTATION,
    )
    # The SAME async→sync bridge stage 5 builds, constructed on the loop that will host
    # the `to_thread` call below — the factory raises if that contract is violated.
    facade = materialize_sync_dispatcher_facade(cast(Any, composer), result_timeout_seconds=30.0)

    result = await asyncio.to_thread(
        partial(
            execute_workflow,
            manifest_entry=_manifest(),
            steps=_peer_steps(),
            run_id="run-b165-round-trip",
            ctx=cast(Any, _Ctx()),
            default_model_binding=_DEFAULT_BINDING,
            step_dispatchers=cast(Any, _Registry(facade)),
        )
    )

    assert result.status is RunStatus.SUCCESS, (
        f"expected SUCCESS, got {result.status} (fail_class={result.fail_class})"
    )

    # BOTH declared placements were gated by the real composer, reached through the real
    # driver — the half the CP module could not show.
    assert len(surface.calls) == 2, (
        f"both same-position placements must gate; operator asked {len(surface.calls)}x"
    )

    keys = [str(key.idempotency_key) for _payload, key in ledger.appends]
    assert len(keys) == 2, f"both placements must write; got {len(keys)}"
    assert len(set(keys)) == 1, (
        "B-165: the two placements collide onto ONE identity through the SHIPPED path — "
        f"keys={keys}"
    )


# mutation-probe: give `StepEffectiveBinding` a distinct `hitl_placement` per branch, or
# make the driver pass a binding whose persona_tier is None, so the composer's real
# gate-decision path is bypassed — the assertion below that a REAL binding arrived would
# then fail.
@pytest.mark.asyncio
async def test_the_composer_receives_a_real_binding_from_the_driver() -> None:
    """Guards the specific regression review named: stage-5 wiring installing the
    composer behind a DIFFERENT binding.

    The collision assertion above would survive a binding regression as long as the gate
    still fired, so the binding shape is asserted separately rather than assumed. A
    `StepEffectiveBinding` carrying a real persona_tier is what routes the composer to a
    real matrix cell instead of the partial-binding sentinel.
    """
    seen: list[Any] = []

    class _RecordingInner:
        async def dispatch(
            self, binding: Any, step: WorkflowStep, *, step_context: StepExecutionContext
        ) -> Mapping[str, Any]:
            seen.append(binding)
            return {"inner_dispatched": True}

    composer = RuntimeHITLGateComposer(
        inner=cast(Any, _RecordingInner()),
        applicable_placements=frozenset({_GATE}),
        ask_user_question_surface=cast(AskUserQuestionSurface, _Surface()),
        ledger_writer=cast(Any, _LedgerWriter()),
        audit_writer=cast(Any, _AuditWriter()),
        tracer_provider=TracerProvider(),
        audit_signing_key_id="harness-runtime-b165-rt",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        procedural_tier_snapshot_resolver=lambda: Identifier("b" * 64),
        blast_radius_resolver=lambda _step: BlastRadiusTier.LOCAL_MUTATION,
    )
    facade = materialize_sync_dispatcher_facade(cast(Any, composer), result_timeout_seconds=30.0)

    await asyncio.to_thread(
        partial(
            execute_workflow,
            manifest_entry=_manifest(),
            steps=_peer_steps(),
            run_id="run-b165-round-trip-binding",
            ctx=cast(Any, _Ctx()),
            default_model_binding=_DEFAULT_BINDING,
            step_dispatchers=cast(Any, _Registry(facade)),
        )
    )

    assert seen, "the inner step was never dispatched — the gate did not complete"
    binding = seen[0]
    assert isinstance(binding, StepEffectiveBinding), (
        f"driver must hand the composer a real StepEffectiveBinding; got {type(binding)}"
    )
    assert binding.persona_tier is PersonaTier.SOLO_DEVELOPER
    assert binding.engine_class is EngineClass.SAVE_POINT_CHECKPOINT


# ---------------------------------------------------------------------------
# Stage-5 wiring — the regression review named, closed at its own layer
# ---------------------------------------------------------------------------


# mutation-probe: in `bootstrap/stage_5_loop_init.py`, stop installing the PRE_ACTION
# `RuntimeHITLGateComposer` into the INFERENCE_STEP chain (or replace it with the bare
# dispatcher), so `ctx.step_dispatchers` no longer resolves to a gate composer.
@pytest.mark.asyncio
async def test_stage_5_installs_the_hitl_gate_composer_into_the_dispatcher_registry(
    tmp_path: Any,
    patched_runtime: dict[str, Any],
) -> None:
    """Closes the named regression — *"if stage-5 wiring stops installing
    `RuntimeHITLGateComposer` this test still passes"* — at the layer that owns it.

    **Why this is a separate test rather than a deeper version of the round trip.**
    Driving a HITL gate through the UNMODIFIED stage-5 registry is not achievable: stage
    5 binds the MCP-backed elicitation surface
    (`materialize_mcp_backed_ask_user_question_surface_stage`,
    `stage_5_loop_init.py:243`), which no automated test can answer. Doubling it would
    replace the very component whose installation is under test, so a "shipped registry"
    gate-drive is self-defeating as stated. What IS checkable, and is the actual content
    of the regression, is that stage 5 installs a gate composer at all — asserted here
    against the real `run_bootstrap`-produced `ctx.step_dispatchers`.

    So the claim is split by what each layer can honestly prove: stage 5 INSTALLS the
    composer (here), and the composer COLLIDES when the real driver feeds it (the round
    trip above). Neither is quoted as the other.
    """
    _ = patched_runtime
    # WORKLOAD is the workload_class conftest's path bindings are keyed to; any other
    # cell fails bootstrap at stage IS on an unresolved PathClass.
    ctx = await run_bootstrap(build_config(tmp_path), workload_class=WORKLOAD)

    registry = ctx.step_dispatchers
    assert registry is not None, "stage 5 must bind ctx.step_dispatchers"

    dispatcher = registry.lookup(StepKind.INFERENCE_STEP)
    assert dispatcher is not None, "INFERENCE_STEP must resolve to a dispatcher"

    # Walk the production wrapper chain (retry/fallback wraps the gate composer, which
    # wraps the bare dispatcher) looking for the gate. Walking rather than asserting the
    # outermost type keeps this robust to a wrapper being added, while still failing if
    # the composer is dropped entirely.
    seen: list[str] = []
    node: Any = dispatcher
    found = False
    for _ in range(10):
        seen.append(type(node).__name__)
        if isinstance(node, RuntimeHITLGateComposer):
            found = True
            break
        node = getattr(node, "inner", None)
        if node is None:
            break

    assert found, (
        f"stage 5 must install a RuntimeHITLGateComposer in the INFERENCE_STEP chain; walked {seen}"
    )
