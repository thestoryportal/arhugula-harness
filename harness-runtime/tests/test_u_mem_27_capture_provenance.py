"""U-MEM-27 slices 1+2 - C-MEM-03 v1.2 write-side cross-family capture provenance.

Witnesses for the WRITE half of U-MEM-27
(`Implementation_Plan_Memory_Substrate_v1.md` U-MEM-27 verification bullets
:1062-:1069):

* the per-arm write-side matrix (:1062) - five cells, one test each, with the
  three `unknown` inputs kept SEPARATE because each reaches the sentinel
  through a different authority
* the pre-dispatch witness (:1063) - run-start through the production
  composition path lands `unknown` even same-family
* the harness-authored-content witness (:1064) - run-close after a completed
  same-family dispatch lands `unknown`
* the harness-summarized-but-dispatch-derived PAIR (:1065) - the production
  turn path lands a real determination despite its `SummarySource.HARNESS_RULE`
  label; this is the pair that kills any `summary_source`-keyed implementation
* the registered-key canonicalization witness (:1067)
* the `EPISODIC_RUN` multi-writer witness (:1069)

The hash-inertness witness (:1068) lives beside the store's own consistency
check, at `harness-is/tests/test_memory_store.py`.

`ollama` is the divergent provider used throughout for the canonicalization
arms: its provider KEY is not value-equal to its `ProviderFamily`
(`local_open_weight`), so a raw-key-vs-value comparison would false-positive
the gate on it.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from harness_as.sandbox_tier import SandboxTier
from harness_core import DeploymentSurface, WorkloadClass
from harness_core.persona_tier import PersonaTier
from harness_cp.cp_shared_types import ModelBinding, ProviderAgnosticPayload
from harness_cp.cross_family_fallback_chain import FallbackChain, ProviderCandidate, ProviderFamily
from harness_cp.engine_class import EngineClass
from harness_cp.gate_level_rule import GateLevel
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver_types import StepExecutionContext, StepKind, WorkflowStep
from harness_is.memory_operation_ledger import MemoryOperationKind
from harness_is.memory_path_registry import MemoryRootBinding
from harness_is.memory_record_envelope import (
    CapturedCrossFamily,
    MemoryRecordKind,
    MemoryScope,
    MemoryVisibility,
)
from harness_is.memory_store import CanonicalMemoryStore, MemoryStoreRecord
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_runtime.automatic_memory import materialize_automatic_memory_runtime
from harness_runtime.memory_capture import (
    EpisodicMemoryCapture,
    MemoryCaptureStatus,
    SummaryProvenance,
    SummarySource,
)
from harness_runtime.memory_scope_family import canonical_scope_family
from harness_runtime.types import OTelConfig, RuntimeConfig

_NOW = datetime(2026, 7, 29, 9, 0, 0, tzinfo=UTC)
_LATER = _NOW + timedelta(minutes=5)
_RUN_ID = "run-u-mem-27"
_POLICY_REF = "policy:u-mem-27"
_TENANT = "tenant-a"

_OLLAMA_KEY = "ollama"
_OLLAMA_FAMILY = ProviderFamily.LOCAL_OPEN_WEIGHT.value
_OPENAI_KEY = "openai"
_OPENAI_FAMILY = ProviderFamily.OPENAI.value
_UNREGISTERED_KEY = "mystery-provider"

# `_run_id` folds the step context's `parent_idempotency_key`, so the production
# composition path writes its run record under this id.
_PRODUCTION_RUN_ID = "run-memory-step-0"


def _actor() -> Actor:
    return Actor(actor_class=ActorClass.AGENT, actor_id="u-mem-27")


def _scope(provider_family: str | None) -> MemoryScope:
    return MemoryScope(
        project="arhugula-v2",
        workflow="memory-substrate",
        workload_class=WorkloadClass.PIPELINE_AUTOMATION.value,
        provider_family=provider_family,
        cli_profile="generic",
        tenant=_TENANT,
        visibility=MemoryVisibility.WORKFLOW,
    )


def _direct_capture(
    tmp_path: Path, *, scope_family: str | None
) -> tuple[
    CanonicalMemoryStore,
    EpisodicMemoryCapture,
]:
    store = CanonicalMemoryStore(
        root_binding=MemoryRootBinding(default_root=tmp_path / "memory"),
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
    )
    return store, EpisodicMemoryCapture(
        store=store,
        actor=_actor(),
        project="arhugula-v2",
        record_scope=_scope(scope_family),
    )


def _tool_event_provenance(
    tmp_path: Path,
    *,
    scope_family: str | None,
    provider: str | None,
) -> CapturedCrossFamily:
    """Capture one CONTENT-BEARING, dispatch-derived record and read its value.

    `tool_event` is the arm matrix's content-bearing carrier: its sole
    production caller (`StandardMemoryToolExecutor._write_note`) stores the note
    the model produced on the dispatch whose provider it passes, so the origin
    condition is satisfied and only the family comparison is under test here.
    """
    store, capture = _direct_capture(tmp_path, scope_family=scope_family)
    result = capture.capture_tool_event(
        run_id=_RUN_ID,
        tool_event_id="tool-1",
        tool_name="memory_write_note",
        summary_text="the note the model produced on this dispatch",
        summary=SummaryProvenance(source=SummarySource.MODEL_GENERATED, model="llama3.1"),
        step_id="step-1",
        timestamp=_NOW,
        provider=provider,
        model="llama3.1",
        cli_profile="generic",
        engine_class=None,
        policy_ref=_POLICY_REF,
        procedural_snapshot_ref=None,
    )
    assert result.status is MemoryCaptureStatus.CAPTURED
    assert result.memory_id is not None
    record = store.read_record(result.memory_id, MemoryRecordKind.TOOL_EVENT, run_id=_RUN_ID)
    return record.envelope.captured_cross_family


# ---------------------------------------------------------------------------
# :1062 - per-arm write-side witness matrix, one test per cell
# ---------------------------------------------------------------------------


def test_cross_family_dispatch_on_content_bearing_capture_lands_true(tmp_path: Path) -> None:
    """Arm 1 - canonicalized dispatch family DIFFERS from the record's family."""
    assert (
        _tool_event_provenance(tmp_path, scope_family=_OLLAMA_FAMILY, provider=_OPENAI_KEY)
        is CapturedCrossFamily.TRUE
    )


def test_same_family_dispatch_on_content_bearing_capture_lands_false(tmp_path: Path) -> None:
    """Arm 2 - canonicalized dispatch family EQUALS the record's family."""
    assert (
        _tool_event_provenance(tmp_path, scope_family=_OPENAI_FAMILY, provider=_OPENAI_KEY)
        is CapturedCrossFamily.FALSE
    )


def test_absent_provider_lands_unknown(tmp_path: Path) -> None:
    """Arm 3 - `provider is None`; `str | None` at every capture signature.

    Kept separate from the other two `unknown` arms deliberately: this one
    short-circuits before the canonicalization authority is consulted at all.
    """
    assert (
        _tool_event_provenance(tmp_path, scope_family=_OLLAMA_FAMILY, provider=None)
        is CapturedCrossFamily.UNKNOWN
    )


def test_unregistered_provider_key_lands_unknown(tmp_path: Path) -> None:
    """Arm 4 - the fail-closed authority returns `None` for an unregistered key.

    Reaches the sentinel through `provider_family_for_scope_check`, a different
    authority from arms 3 and 5, which is why the plan forbids collapsing the
    three into one parametrized case.
    """
    assert canonical_scope_family(_UNREGISTERED_KEY) is None
    assert (
        _tool_event_provenance(tmp_path, scope_family=_OLLAMA_FAMILY, provider=_UNREGISTERED_KEY)
        is CapturedCrossFamily.UNKNOWN
    )


def test_null_composed_provider_family_lands_unknown(tmp_path: Path) -> None:
    """Arm 5 - a `null` `scope.provider_family`, C-MEM-03's unpartitioned wildcard.

    `resolve_scope_family` passes `null` through untouched, and cross-family is
    undefined against it - so this arm must not land `false` even though the
    dispatch provider itself resolves perfectly well.
    """
    assert canonical_scope_family(_OPENAI_KEY) == _OPENAI_FAMILY
    assert (
        _tool_event_provenance(tmp_path, scope_family=None, provider=_OPENAI_KEY)
        is CapturedCrossFamily.UNKNOWN
    )


# ---------------------------------------------------------------------------
# :1067 - registered-key canonicalization
# ---------------------------------------------------------------------------


def test_registered_provider_key_canonicalizes_before_the_comparison(tmp_path: Path) -> None:
    """:1067 - a registered KEY whose canonical family equals the scope's lands `false`.

    `ollama` is not value-equal to `local_open_weight`, so a raw-key-vs-value
    comparison would report `true` here - the same key-vs-value defect
    `_family_escapes_source` documents on the promotion side.
    """
    assert _OLLAMA_KEY != _OLLAMA_FAMILY
    assert canonical_scope_family(_OLLAMA_KEY) == _OLLAMA_FAMILY
    assert (
        _tool_event_provenance(tmp_path, scope_family=_OLLAMA_FAMILY, provider=_OLLAMA_KEY)
        is CapturedCrossFamily.FALSE
    )


# ---------------------------------------------------------------------------
# :1063 / :1065 - the production paths
# ---------------------------------------------------------------------------


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        repository_root=tmp_path,
        otel=OTelConfig(otlp_endpoint="http://localhost:4318"),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        tenant_id=_TENANT,
    )


def _ollama_chain() -> FallbackChain:
    return FallbackChain(
        primary=ProviderCandidate(
            provider=_OLLAMA_KEY,
            model="llama3.1",
            family=ProviderFamily.LOCAL_OPEN_WEIGHT,
        ),
        same_family=(),
        cross_family=(),
    )


def _ollama_binding() -> StepEffectiveBinding:
    return StepEffectiveBinding(
        step_id="memory-step",
        model_binding=ModelBinding(provider=_OLLAMA_KEY, model="llama3.1"),
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        override_applied=False,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
    )


def _step_context() -> StepExecutionContext:
    return StepExecutionContext(
        workflow_id="workflow-memory",
        parent_action_id="workflow:workflow-memory:step:0",
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=_actor(),
        parent_entry_hash="",
        parent_idempotency_key=_PRODUCTION_RUN_ID,
        tenant_id=_TENANT,
        step_index=0,
        run_engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
    )


def _step() -> WorkflowStep:
    return WorkflowStep(
        step_id="memory-step",
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={"messages": [{"role": "user", "content": "what applies here?"}]},
    )


def _production_store(tmp_path: Path) -> CanonicalMemoryStore:
    return CanonicalMemoryStore(
        root_binding=MemoryRootBinding(default_root=tmp_path / ".harness" / "memory"),
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
    )


def test_run_start_through_production_composition_lands_unknown_even_same_family(
    tmp_path: Path,
) -> None:
    """:1063 pre-dispatch witness - and the SAME-family case is the point.

    `compose_for_dispatch` writes the run-start record before it returns the
    context, so no dispatch has run: the provider it holds is a SELECTION, not
    a producer. An implementation that derived from the selected provider would
    land `false` here and still pass a cross-family-only witness.
    """
    runtime = materialize_automatic_memory_runtime(
        _config(tmp_path),
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
    )
    assert runtime is not None

    runtime.compose_for_dispatch(
        binding=_ollama_binding(),
        fallback_chain=_ollama_chain(),
        step=_step(),
        step_context=_step_context(),
    )

    record = _production_store(tmp_path).read_run_record(_PRODUCTION_RUN_ID)
    # The selection and the composed scope are the SAME family - the comparison
    # this record declines to make would have returned `false`.
    assert record.envelope.scope.provider_family == _OLLAMA_FAMILY
    assert canonical_scope_family(_OLLAMA_KEY) == _OLLAMA_FAMILY
    assert record.envelope.captured_cross_family is CapturedCrossFamily.UNKNOWN


def _production_turn_record(tmp_path: Path, *, dispatch_provider: str) -> MemoryStoreRecord:
    runtime = materialize_automatic_memory_runtime(
        _config(tmp_path),
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
    )
    assert runtime is not None
    context = runtime.compose_for_dispatch(
        binding=_ollama_binding(),
        fallback_chain=_ollama_chain(),
        step=_step(),
        step_context=_step_context(),
    )
    runtime.capture_turn_completion(
        memory_context=context,
        payload=ProviderAgnosticPayload(
            messages=({"role": "user", "content": "what applies here?"},),
            tools=None,
            params={},
        ),
        step_context=_step_context(),
        step_id="memory-step",
        provider=dispatch_provider,
        model="llama3.1",
        response={"choices": [{"message": {"content": "the provider's own completed answer"}}]},
        input_tokens=11,
        output_tokens=22,
    )
    store = _production_store(tmp_path)
    turn_captures = [
        entry
        for entry in store.read_memory_operations()
        if entry.operation_kind is MemoryOperationKind.CAPTURE
        and str(entry.action_id).startswith("capture:turn_completion:")
    ]
    [entry] = turn_captures
    [memory_ref] = entry.memory_refs
    return store.read_record(memory_ref, MemoryRecordKind.EPISODIC_TURN, run_id=entry.run_id)


def test_production_turn_path_same_family_lands_false_despite_harness_rule_summary(
    tmp_path: Path,
) -> None:
    """:1065 arm (a) - dispatch-derived content carries a determination.

    Driven through `LocalAutomaticMemoryRuntime.capture_turn_completion`, whose
    summarizer label is `SummarySource.HARNESS_RULE` while its
    `response_summary` derives from the ACTUAL provider response. An
    implementation keyed on `summary_source` lands `unknown` here and passes
    every other witness in this file.
    """
    record = _production_turn_record(tmp_path, dispatch_provider=_OLLAMA_KEY)

    assert record.content["summary_source"] == SummarySource.HARNESS_RULE.value
    assert record.envelope.scope.provider_family == _OLLAMA_FAMILY
    assert record.envelope.captured_cross_family is CapturedCrossFamily.FALSE


def test_production_turn_path_cross_family_lands_true_despite_harness_rule_summary(
    tmp_path: Path,
) -> None:
    """:1065 arm (b) - the same path, a cross-family completed dispatch."""
    record = _production_turn_record(tmp_path, dispatch_provider=_OPENAI_KEY)

    assert record.content["summary_source"] == SummarySource.HARNESS_RULE.value
    assert record.envelope.scope.provider_family == _OLLAMA_FAMILY
    assert record.envelope.captured_cross_family is CapturedCrossFamily.TRUE


# ---------------------------------------------------------------------------
# :1064 / :1069 - the run kinds
# ---------------------------------------------------------------------------


def _run_start(capture: EpisodicMemoryCapture, *, provider: str, timestamp: datetime) -> None:
    result = capture.capture_run_start(
        run_id=_RUN_ID,
        workflow_id="memory-substrate",
        thread_id=None,
        provider_route=(provider,),
        timestamp=timestamp,
        provider=provider,
        model="llama3.1",
        cli_profile="generic",
        engine_class=None,
        policy_ref=_POLICY_REF,
        procedural_snapshot_ref=None,
    )
    assert result.status is MemoryCaptureStatus.CAPTURED


def _run_close(capture: EpisodicMemoryCapture, *, provider: str, timestamp: datetime) -> None:
    result = capture.capture_run_close(
        run_id=_RUN_ID,
        workflow_id="memory-substrate",
        thread_id=None,
        provider_route=(provider,),
        close_status="completed",
        started_at=_NOW,
        timestamp=timestamp,
        provider=provider,
        model="llama3.1",
        cli_profile="generic",
        engine_class=None,
        policy_ref=_POLICY_REF,
        procedural_snapshot_ref=None,
    )
    assert result.status is MemoryCaptureStatus.CAPTURED


def test_run_close_after_a_completed_same_family_dispatch_lands_unknown(tmp_path: Path) -> None:
    """:1064 harness-authored-content witness - the class an event-TIMING rule misses.

    Run-close is written AFTER a completed dispatch, so a rule keyed on "has a
    dispatch happened yet" would land a determination. Its content is run
    metadata - it derives from no dispatch output - so the honest value is
    `unknown`. The turn capture in the same run is the positive control: the
    dispatch really was same-family and really was determinable.
    """
    store, capture = _direct_capture(tmp_path, scope_family=_OLLAMA_FAMILY)

    turn = capture.capture_turn_completion(
        run_id=_RUN_ID,
        turn_id="turn-1",
        step_id="step-1",
        prompt_summary="asked a question",
        response_summary="the provider's own completed answer",
        summary=SummaryProvenance(source=SummarySource.HARNESS_RULE),
        tool_event_refs=(),
        failure_observations=(),
        promotion_candidates=(),
        token_usage=None,
        timestamp=_NOW,
        provider=_OLLAMA_KEY,
        model="llama3.1",
        cli_profile="generic",
        engine_class=None,
        policy_ref=_POLICY_REF,
        procedural_snapshot_ref=None,
    )
    assert turn.memory_id is not None
    turn_record = store.read_record(turn.memory_id, MemoryRecordKind.EPISODIC_TURN, run_id=_RUN_ID)
    assert turn_record.envelope.captured_cross_family is CapturedCrossFamily.FALSE

    _run_close(capture, provider=_OLLAMA_KEY, timestamp=_LATER)

    run_record = store.read_run_record(_RUN_ID)
    assert run_record.content["event_type"] == "run_close"
    assert run_record.envelope.captured_cross_family is CapturedCrossFamily.UNKNOWN


def test_episodic_run_overwrite_keeps_the_envelope_co_written_with_its_content(
    tmp_path: Path,
) -> None:
    """:1069 multi-writer witness - `unknown` is what SURVIVES the overwrite.

    A run whose `capture_run_start` ran same-family and whose
    `capture_run_close` ran cross-family stores one record, keyed on `run_id`
    alone. Two claims are asserted: the MECHANISM (the surviving envelope is
    the one co-written with the surviving content - witnessed by `created_at`,
    which differs between the two writers), and the RULE (its value is
    `unknown`, not a determination inherited from either writer).
    """
    store, capture = _direct_capture(tmp_path, scope_family=_OLLAMA_FAMILY)

    _run_start(capture, provider=_OLLAMA_KEY, timestamp=_NOW)
    assert store.read_run_record(_RUN_ID).content["event_type"] == "run_start"

    _run_close(capture, provider=_OPENAI_KEY, timestamp=_LATER)

    record = store.read_run_record(_RUN_ID)
    # Mechanism: content and envelope both come from the run-close call.
    assert record.content["event_type"] == "run_close"
    assert record.envelope.created_at == _LATER
    # Rule: run metadata derives from no dispatch output, whenever written.
    assert record.envelope.captured_cross_family is CapturedCrossFamily.UNKNOWN
