"""`B-97` half (a) — §14.14.9.1 BOTH-SURFACES-OR-NEITHER keying parity (U-RT-149).

Runtime spec v1.108 §14.14.9.1: *"Keying is the §14.14.8 TENANT-COMPOSITE key —
`(normalized_tenant_scope, workflow_id)` — **matching `resume()` exactly**, per
key on what you can act on; fence on what you read ... leaving it unamended while
§14.14.8 moved would put the two surfaces on different keys, which is exactly
what the rule below forbids."*

Plan U-RT-149 AC #1 (both surfaces), AC #12 (the accessor's input triple and
projection unchanged).

**Two witnesses, deliberately of different shapes.** The BEHAVIOURAL one asserts
both public surfaces see a tenant-scoped record and neither sees a wrong-tenant
one. The STRUCTURAL one pins that both route through ONE read authority — which
is what makes de-pairing them require adding a second read path rather than
merely editing one. The de-pairing MUTATION PROBE fails the structural witness.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pytest
from harness_core.deployment_surface import DeploymentSurface
from harness_core.identity import StepID
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
from harness_cp.pause_resume_protocol_types import PauseSnapshot, WorkflowPauseReason
from harness_cp.routing_manifest_residence import RoutingManifest
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver_types import StepKind, WorkflowStep
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_is.path_class_registry import PathClass
from harness_is.state_ledger_entry_schema import Identifier
from harness_runtime import api as api_module
from harness_runtime.api import (
    PausedWorkflowStateUnavailableError,
    read_paused_workflow_state,
)
from harness_runtime.lifecycle.journal_workflow_pause_store import (
    JournalWorkflowPauseStore,
    PauseJournalReadCause,
    pause_journal_dir_for,
)
from harness_runtime.lifecycle.pause_resume_protocol_types import PauseResumeProtocolConfig
from harness_runtime.types import (
    CollectorConfig,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
)

_WORKLOAD = WorkloadClass.SOFTWARE_ENGINEERING
_SURFACE = DeploymentSurface.LOCAL_DEVELOPMENT
_WORKFLOW_ID = "wf-b97a-parity"
_TENANT_A = "tenant-a"
_TENANT_B = "tenant-b"

_CHAIN = FallbackChain(
    primary=ProviderCandidate(
        provider="anthropic", model="claude-haiku-4-5", family=ProviderFamily.ANTHROPIC
    ),
    same_family=(),
    cross_family=(),
    terminal=None,
)


def _config(tmp_path: Path, *, tenant_id: str | None) -> RuntimeConfig:
    return RuntimeConfig(
        deployment_surface=_SURFACE,
        repository_root=tmp_path,
        tenant_id=tenant_id,
        path_bindings=PathBindingConfig(
            raw_entries=tuple(
                {
                    "path_class": pc,
                    "workflow_class": _WORKLOAD,
                    "deployment_surface": _SURFACE,
                    "path": str(tmp_path / pc.value.lower()),
                }
                for pc in PathClass
            ),
        ),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4317"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        mcp_clients=[],
        ollama_optional=True,
        pause_resume_protocol_config=PauseResumeProtocolConfig(durable=True),
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

    def __init__(self) -> None:
        self.steps: Sequence[WorkflowStep] = (
            WorkflowStep(
                step_id=StepID("step-0"), step_kind=StepKind.DECLARATIVE_STEP, step_payload={}
            ),
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


def _journal_dir(tmp_path: Path) -> Path:
    return pause_journal_dir_for(tmp_path / PathClass.STATE_LEDGER.value.lower())


def _snapshot(run_id: str) -> PauseSnapshot:
    return PauseSnapshot(
        workflow_id=_WORKFLOW_ID,
        run_id=run_id,
        step_index=0,
        pause_reason=WorkflowPauseReason.HITL_PENDING,
        state_summary=StateSummary(
            relevant_entries=(),
            summary_text="",
            summary_hash="0" * 64,
            idempotency_key=Identifier(""),
            external_references=(),
        ),
        snapshot_hash="0" * 64,
        created_at=0,
        state_ledger_anchor="0" * 64,
    )


# ---------------------------------------------------------------------------
# The BEHAVIOURAL parity witness.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_accessor_reads_the_tenant_scoped_record_and_not_a_co_tenants(
    tmp_path: Path,
) -> None:
    """The §14.14.9 accessor keys on the TENANT-COMPOSITE key, matching `resume()`.

    Tenant A journals; the accessor under tenant A's config finds it, and the
    accessor under tenant B's config reports the ordinary `absent` — resolving
    ITS OWN path, never opening A's file.
    """
    journal_dir = _journal_dir(tmp_path)
    JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=_TENANT_A).capture(
        _snapshot("run-a")
    )

    state = await read_paused_workflow_state(
        _Workflow(), resume_handle=_WORKFLOW_ID, config=_config(tmp_path, tenant_id=_TENANT_A)
    )
    assert state.workflow_id == _WORKFLOW_ID

    with pytest.raises(PausedWorkflowStateUnavailableError) as excinfo:
        await read_paused_workflow_state(
            _Workflow(), resume_handle=_WORKFLOW_ID, config=_config(tmp_path, tenant_id=_TENANT_B)
        )
    assert excinfo.value.cause is PauseJournalReadCause.ABSENT


@pytest.mark.asyncio
async def test_the_untenanted_accessor_does_not_see_a_tenanted_record(tmp_path: Path) -> None:
    """And symmetrically: the untenanted branch is a DISTINCT address, not a
    superset. `None` is its own segment-count form, so it collides with nothing."""
    journal_dir = _journal_dir(tmp_path)
    JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=_TENANT_A).capture(
        _snapshot("run-a")
    )
    with pytest.raises(PausedWorkflowStateUnavailableError):
        await read_paused_workflow_state(
            _Workflow(), resume_handle=_WORKFLOW_ID, config=_config(tmp_path, tenant_id=None)
        )


# ---------------------------------------------------------------------------
# The STRUCTURAL parity witness + its de-pairing mutation probe.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_both_surfaces_read_through_one_authority(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """**Both surfaces or neither** — pinned STRUCTURALLY.

    `resume()` and the §14.14.9 accessor both resolve the durable read through
    the SINGLE `_read_durable_pause_snapshot`, which composes the store from
    `config.tenant_id`. De-pairing them therefore requires adding a SECOND read
    path — it cannot be done by editing one call site — and this witness is what
    fails when someone does. *(The runner-up shape, asserting each surface's
    behaviour separately, passes happily while a second de-tenanted read path
    sits beside the first.)*
    """
    journal_dir = _journal_dir(tmp_path)
    config = _config(tmp_path, tenant_id=_TENANT_A)
    JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=_TENANT_A).capture(
        _snapshot("run-a")
    )

    calls: list[tuple[str | None, str]] = []
    real = api_module._read_durable_pause_snapshot

    def _spy(cfg: RuntimeConfig, workflow: object, resume_handle: str) -> object:
        calls.append((cfg.tenant_id, resume_handle))
        return real(cfg, workflow, resume_handle)  # type: ignore[arg-type]

    monkeypatch.setattr(api_module, "_read_durable_pause_snapshot", _spy)

    await read_paused_workflow_state(_Workflow(), resume_handle=_WORKFLOW_ID, config=config)
    accessor_calls = list(calls)

    calls.clear()
    # `resume()` reaches the SAME read PRE-BOOTSTRAP. Whether the run then
    # succeeds or fails downstream is irrelevant to what this witness pins, so
    # the outcome is deliberately not asserted — only that the read was routed.
    try:
        await api_module.resume(_Workflow(), resume_handle=_WORKFLOW_ID, config=config)
    except Exception:
        pass
    resume_calls = list(calls)

    assert accessor_calls, "the accessor did not route through the shared read authority"
    assert resume_calls, "resume() did not route through the shared read authority"
    assert {call[0] for call in accessor_calls} == {_TENANT_A}
    assert {call[0] for call in resume_calls} == {_TENANT_A}


def test_mutation_probe_de_pairing_the_accessor_fails_the_parity_witness(
    tmp_path: Path,
) -> None:
    """The DE-PAIRING mutation probe (AC #6's shape, applied to §14.14.9.1).

    Simulate the forbidden state — a second, de-tenanted read path used by ONE
    surface — and assert it produces the divergence the parity witness exists to
    catch: the accessor would resolve a DIFFERENT path than `resume()` for the
    same `(config, workflow_id)`.
    """
    config = _config(tmp_path, tenant_id=_TENANT_A)

    def _de_paired_read_path(cfg: RuntimeConfig) -> str:
        """The de-paired accessor: keys on `workflow_id` alone (pre-v1.108)."""
        from harness_runtime.lifecycle.journal_workflow_pause_store import (
            legacy_pause_journal_filename,
        )

        return legacy_pause_journal_filename(_WORKFLOW_ID)

    def _shipped_read_path(cfg: RuntimeConfig) -> str:
        from harness_runtime.lifecycle.journal_workflow_pause_store import pause_journal_filename

        return pause_journal_filename(cfg.tenant_id, _WORKFLOW_ID)

    assert _de_paired_read_path(config) != _shipped_read_path(config), (
        "the de-pairing probe is VACUOUS — the two derivations agree, so the "
        "parity witness would pass under the forbidden state"
    )


def _durable_ctx(tmp_path: Path) -> object:
    """The minimal stage-5 ctx the durable factory branch actually touches.

    The factory reads `ctx.ledger_writer.handle.canonical_path.parent` to resolve
    the STATE_LEDGER dir and passes both ledger refs straight through to the
    protocol constructor, so a real path plus two sentinels is the whole
    prerequisite (the U-RT-88 factory tests already use bare sentinels; the
    durable branch needs the one real path they lack).
    """
    from types import SimpleNamespace

    from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext

    ledger = tmp_path / PathClass.STATE_LEDGER.value.lower() / "state.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ctx = _MutableHarnessContext()
    ctx.ledger_writer = SimpleNamespace(handle=SimpleNamespace(canonical_path=ledger))  # type: ignore[assignment]
    ctx.ledger_reader = object()  # type: ignore[assignment]
    return ctx


@pytest.mark.asyncio
async def test_the_factory_keys_the_capture_side_store_by_the_configured_tenant(
    tmp_path: Path,
) -> None:
    """**The CAPTURE-side production wiring of the tenant key.**

    Every other witness in this arc constructs `JournalWorkflowPauseStore`
    DIRECTLY, so none of them touches the one line that puts the tenant into a
    real deployment's capture path — the stage-5 factory's
    `tenant_id=config.tenant_id`. The read half was already witnessed; mutating
    the capture half to `None` passed the entire suite. That is the
    wired-handler-unreachable class: two halves of one mechanism, only one of
    them held by a test.

    Asserted as a ROUND TRIP through both production surfaces — capture through
    the factory-built protocol, read through the public accessor, under ONE
    tenanted config — so the two halves are pinned to the same key by
    construction rather than by two independent path assertions that could drift
    apart.
    """
    from harness_runtime.bootstrap.factories.pause_resume_protocol_factory import (
        materialize_pause_resume_protocol_stage,
    )
    from harness_runtime.lifecycle.durable_pause_resume_protocol import (
        DurablePauseResumeProtocol,
    )
    from harness_runtime.lifecycle.journal_workflow_pause_store import pause_journal_filename

    config = _config(tmp_path, tenant_id=_TENANT_A)
    protocol = await materialize_pause_resume_protocol_stage(
        config,
        _durable_ctx(tmp_path),  # type: ignore[arg-type]
        pause_context_reader=lambda: (_snapshot("run-capture").state_summary, "0" * 64),
    )
    assert isinstance(protocol, DurablePauseResumeProtocol), (
        "the durable branch was not taken — the probe would be vacuous"
    )

    await protocol.capture_pause_snapshot(
        workflow_id=_WORKFLOW_ID,
        run_id="run-capture",
        step_index=0,
        pause_reason=WorkflowPauseReason.HITL_PENDING,
    )

    # The capture landed at the TENANT-COMPOSITE key, and NOT at the untenanted
    # one a `tenant_id=None` factory would have produced.
    journal_dir = _journal_dir(tmp_path)
    assert (journal_dir / pause_journal_filename(_TENANT_A, _WORKFLOW_ID)).is_file()
    assert not (journal_dir / pause_journal_filename(None, _WORKFLOW_ID)).exists()

    # ... and the READ half resolves it under the SAME config — the round trip
    # that makes capture-side and read-side one mechanism rather than two.
    state = await read_paused_workflow_state(_Workflow(), resume_handle=_WORKFLOW_ID, config=config)
    assert state.workflow_id == _WORKFLOW_ID


def test_the_store_requires_its_tenant_scope_explicitly(tmp_path: Path) -> None:
    """The `tenant_id` REQUIRED-KEYWORD contract, pinned at the signature.

    `None` is a legitimate domain value (untenanted), so a default would
    conflate *"unspecified"* with *"untenanted"* — and every call site that
    forgot to pass one would silently key untenanted instead of failing. The
    contract is what makes the ~35 call-site updates load-bearing rather than
    churn, so it is pinned here, in the same shape as the AC #7(a) / AC #12
    signature pins.
    """
    import inspect

    _ = tmp_path
    parameter = inspect.signature(JournalWorkflowPauseStore.__init__).parameters["tenant_id"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is inspect.Parameter.empty, (
        "tenant_id gained a default — an omitted scope now silently means "
        "UNTENANTED instead of failing at construction"
    )


@pytest.mark.asyncio
async def test_ac12_the_accessor_input_triple_is_byte_unchanged(tmp_path: Path) -> None:
    """AC #12 — the accessor's INPUT TRIPLE is unchanged: `(workflow,
    resume_handle, config)`, with `config=None` still permitted.

    *"The tenant scope has always lived inside `config` ... no new config field,
    no operator data entry, and no new caller burden is introduced."* Asserted
    over the shipped signature, not read off the docstring.
    """
    import inspect

    signature = inspect.signature(read_paused_workflow_state)
    assert list(signature.parameters) == ["workflow", "resume_handle", "config"]
    assert signature.parameters["config"].default is None
    assert signature.parameters["resume_handle"].kind is inspect.Parameter.KEYWORD_ONLY
