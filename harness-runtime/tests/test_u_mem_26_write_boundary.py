"""U-MEM-26 slice 2 - `B-89` writer repair + C-MEM-03 write-boundary value domain.

Witnesses for the WRITE half of U-MEM-26 (`Implementation_Plan_Memory_Substrate_v1.md`
U-MEM-26 verification bullets) plus the two direct-reader negatives:

* capture-scope composition and its round trip (:908, :909)
* the four write-boundary sub-cases (:911) and the `write_note` by-rule case
* compaction (:912), promotion ORDERING on the derived candidate (:913),
  native adapter (:914), and the LEGACY-REDACTION exception (:915)
* direct-reader negatives at the native backend (:917) and at the
  standard-tool-executor by-reference paths (:918)

`ollama` is the divergent provider used throughout: its provider KEY is not
value-equal to its `ProviderFamily` (`local_open_weight`), so a test that
passes with `anthropic` or `openai` proves nothing about canonicalization.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from harness_as.memory_tool_contracts import MemoryToolName
from harness_as.sandbox_tier import SandboxTier
from harness_core import DeploymentSurface, WorkloadClass
from harness_core.persona_tier import PersonaTier
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import FallbackChain, ProviderCandidate, ProviderFamily
from harness_cp.engine_class import EngineClass
from harness_cp.gate_level_rule import GateLevel
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver_types import StepExecutionContext, StepKind, WorkflowStep
from harness_is.memory_operation_ledger import MemoryOperationEntry, MemoryOperationKind
from harness_is.memory_path_registry import MemoryRootBinding
from harness_is.memory_policy import (
    AccessDecision,
    CaptureDecision,
    MemoryPolicyDocument,
    MemoryPolicyResolver,
    PromotionDecision,
    ReviewMode,
)
from harness_is.memory_record_envelope import (
    MemoryID,
    MemoryRecordEnvelope,
    MemoryRecordKind,
    MemoryScope,
    MemoryTier,
    MemoryVisibility,
    RedactionState,
    SourceRef,
    SourceRefType,
    compute_memory_content_hash,
    derive_memory_id,
)
from harness_is.memory_redaction import MemoryRedactionActor, MemoryRedactionService
from harness_is.memory_retrieval import (
    MemoryPacketAccessMode,
    MemoryRetrievalRequest,
    MemoryRetriever,
)
from harness_is.memory_retrieval_index import DerivedRetrievalIndexStore
from harness_is.memory_store import CanonicalMemoryStore, MemoryStoreRecord
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_runtime.automatic_memory import materialize_automatic_memory_runtime
from harness_runtime.lifecycle.memory_tool_types import MemoryCallbackIOError
from harness_runtime.lifecycle.native_memory_adapter import CanonicalNativeMemoryToolBackend
from harness_runtime.memory_capture import (
    EpisodicMemoryCapture,
    MemoryCaptureResult,
    MemoryCaptureScopeValueDomainError,
    MemoryCaptureStatus,
)
from harness_runtime.memory_compaction_safety import (
    CompactionCandidateDisposition,
    CompactionCandidateDispositionRecord,
    CompactionSafetyHook,
    CompactionScopeValueDomainError,
)
from harness_runtime.memory_promotion import (
    PromotionCandidate,
    PromotionCandidateConfidence,
    PromotionCandidateExtractor,
    PromotionCandidateKind,
    PromotionRiskFlag,
    PromotionScopeValueDomainError,
)
from harness_runtime.memory_scope_family import canonical_scope_family
from harness_runtime.memory_tool_executor import (
    MemoryToolExecutionContext,
    MemoryToolExecutionDeniedError,
    MemoryToolExecutionRequest,
    StandardMemoryToolExecutor,
)
from harness_runtime.types import OTelConfig, RuntimeConfig

_NOW = datetime(2026, 7, 28, 12, 0, 0, tzinfo=UTC)
_POLICY_REF = "policy:u-mem-26"
_SCOPE_REF = "scope:u-mem-26"
_TENANT = "tenant-a"

# The divergent pair the whole slice turns on: a REGISTERED provider key whose
# string is NOT value-equal to the `ProviderFamily` it belongs to.
_OLLAMA_KEY = "ollama"
_OLLAMA_FAMILY = ProviderFamily.LOCAL_OPEN_WEIGHT.value
_UNREGISTERED_KEY = "mystery-provider"


def _actor() -> Actor:
    return Actor(actor_class=ActorClass.AGENT, actor_id="u-mem-26")


def _binding_root(tmp_path: Path) -> MemoryRootBinding:
    return MemoryRootBinding(default_root=tmp_path / "memory")


def _store(binding: MemoryRootBinding) -> CanonicalMemoryStore:
    return CanonicalMemoryStore(
        root_binding=binding,
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
    )


def _index_store(binding: MemoryRootBinding) -> DerivedRetrievalIndexStore:
    return DerivedRetrievalIndexStore(
        root_binding=binding,
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        family_canonicalizer=canonical_scope_family,
    )


def _policy(**overrides: object) -> MemoryPolicyDocument:
    fields: dict[str, object] = {
        "policy_id": _POLICY_REF,
        "enabled": True,
        "capture_decision": CaptureDecision.CAPTURE_FULL,
        "promotion_decision": PromotionDecision.PROPOSE_SEMANTIC,
        "retrieval_access": AccessDecision.RETRIEVAL_ONLY,
        "standard_tool_access": AccessDecision.STANDARD_TOOLS,
        "native_memory_access": AccessDecision.NATIVE_PROVIDER,
        "review_mode": ReviewMode.OPERATOR_REQUIRED,
    }
    fields.update(overrides)
    return MemoryPolicyDocument(**fields)


def _scope(provider_family: str | None) -> MemoryScope:
    return MemoryScope(
        project="arhugula-v2",
        workflow="memory-substrate",
        workload_class="coding-arc",
        provider_family=provider_family,
        cli_profile="generic",
        tenant=_TENANT,
        visibility=MemoryVisibility.WORKFLOW,
    )


def _semantic_record(
    scope: MemoryScope,
    *,
    statement: str = "The harness partitions memory by provider family.",
) -> MemoryStoreRecord:
    content: dict[str, object] = {
        "semantic_kind": MemoryRecordKind.SEMANTIC_FACT.value,
        "statement": statement,
        "confidence": "high",
        "source_authority": "operator_direct",
        "status": "active",
        "injection_policy": "tool_allowed",
        "tags": ["memory", "scope"],
    }
    content_hash = compute_memory_content_hash(content)
    return MemoryStoreRecord(
        envelope=MemoryRecordEnvelope(
            memory_id=derive_memory_id(
                MemoryTier.SEMANTIC, MemoryRecordKind.SEMANTIC_FACT, content_hash
            ),
            schema_version="memory-store-record/v1",
            tier=MemoryTier.SEMANTIC,
            kind=MemoryRecordKind.SEMANTIC_FACT,
            created_at=_NOW,
            source_refs=(SourceRef(ref_type=SourceRefType.OPERATOR, ref="operator:u-mem-26"),),
            scope=scope,
            content_hash=content_hash,
            redaction_state=RedactionState.ACTIVE,
        ),
        content=content,
    )


# ---------------------------------------------------------------------------
# (a) automatic capture - the `B-89` writer repair
# ---------------------------------------------------------------------------


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        repository_root=tmp_path,
        otel=OTelConfig(otlp_endpoint="http://localhost:4318"),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        tenant_id=_TENANT,
    )


def _ollama_chain(provider: str = _OLLAMA_KEY) -> FallbackChain:
    return FallbackChain(
        primary=ProviderCandidate(
            provider=provider,
            model="llama3.1",
            family=ProviderFamily.LOCAL_OPEN_WEIGHT,
        ),
        same_family=(),
        cross_family=(),
    )


def _ollama_binding(provider: str = _OLLAMA_KEY) -> StepEffectiveBinding:
    return StepEffectiveBinding(
        step_id="memory-step",
        model_binding=ModelBinding(provider=provider, model="llama3.1"),
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
        parent_idempotency_key="run-memory-step-0",
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


def _captured_run_scope(tmp_path: Path, *, provider: str = _OLLAMA_KEY) -> MemoryScope:
    """Drive a real dispatch composition and return the scope the capture WROTE."""

    runtime = materialize_automatic_memory_runtime(
        _config(tmp_path),
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
    )
    assert runtime is not None
    runtime.compose_for_dispatch(
        binding=_ollama_binding(provider),
        fallback_chain=_ollama_chain(provider),
        step=_step(),
        step_context=_step_context(),
    )
    store = CanonicalMemoryStore(
        root_binding=MemoryRootBinding(default_root=tmp_path / ".harness" / "memory"),
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
    )
    captures = [
        entry
        for entry in store.read_memory_operations()
        if entry.operation_kind is MemoryOperationKind.CAPTURE
    ]
    [capture] = captures
    [memory_ref] = capture.memory_refs
    record = store.read_record(memory_ref, MemoryRecordKind.EPISODIC_RUN, run_id=capture.run_id)
    return record.envelope.scope


def test_capture_writes_the_runs_composed_scope_not_the_provider_key(tmp_path: Path) -> None:
    """:908 - `B-89` + `B-90`.

    The dispatch's provider KEY is `ollama`; the run's composed family VALUE is
    `local_open_weight`. Pre-repair the capture path stored the key and omitted
    `tenant` / `workload_class` entirely.
    """
    scope = _captured_run_scope(tmp_path)

    assert scope.provider_family == _OLLAMA_FAMILY
    assert scope.provider_family != _OLLAMA_KEY  # never the raw per-dispatch key
    assert scope.tenant == _TENANT  # `B-90`: was omitted pre-repair
    assert scope.workload_class == WorkloadClass.PIPELINE_AUTOMATION.value


def test_capture_under_unregistered_candidate_key_still_lands_the_composed_family(
    tmp_path: Path,
) -> None:
    """:911 sub-case 4 - never the raw key, and emphatically never `null`.

    `null` is not a fail-safe: per C-MEM-03 a stored `null` is the
    UNPARTITIONED WILDCARD matching every requested family, so degrading an
    unknown key to `null` would WIDEN the record's reach.
    """
    scope = _captured_run_scope(tmp_path, provider=_UNREGISTERED_KEY)

    assert scope.provider_family == _OLLAMA_FAMILY
    assert scope.provider_family is not None
    assert scope.provider_family != _UNREGISTERED_KEY


def _supplied_scope_capture(
    tmp_path: Path, *, provider_family: str
) -> tuple[CanonicalMemoryStore, EpisodicMemoryCapture]:
    """A capture bound to a HAND-SUPPLIED `record_scope`.

    The composed production path (`_captured_run_scope` above) always hands in
    an already-canonical scope, so it cannot witness what the write boundary
    does with one that is not. This builds that case directly.
    """
    store = _store(_binding_root(tmp_path))
    return store, EpisodicMemoryCapture(
        store=store,
        actor=_actor(),
        project="arhugula-v2",
        record_scope=MemoryScope(
            project="arhugula-v2",
            workflow="memory-substrate",
            workload_class=WorkloadClass.PIPELINE_AUTOMATION.value,
            tenant=_TENANT,
            provider_family=provider_family,
            cli_profile="generic",
            visibility=MemoryVisibility.WORKFLOW,
        ),
    )


def _run_start(capture: EpisodicMemoryCapture) -> MemoryCaptureResult:
    return capture.capture_run_start(
        run_id="run-u-mem-26",
        workflow_id="memory-substrate",
        thread_id=None,
        provider_route=(_OLLAMA_KEY,),
        timestamp=_NOW,
        provider=_OLLAMA_KEY,
        model="llama3.1",
        cli_profile="generic",
        engine_class=None,
        policy_ref=_POLICY_REF,
        procedural_snapshot_ref=None,
    )


def test_supplied_record_scope_with_a_raw_key_is_canonicalized_before_it_persists(
    tmp_path: Path,
) -> None:
    """Codex R2 [P2-a] - the supplied scope is NOT trusted past the value domain.

    `_scope_for_record` returned `self._record_scope` VERBATIM, so a caller
    handing in a registered provider KEY (`ollama`) rather than its
    `ProviderFamily` VALUE persisted that key straight into the record - the
    exact raw-key partition the residual path was hardened against, reachable
    through the other branch. Both branches now share one canonicalize-or-deny.
    """
    store, capture = _supplied_scope_capture(tmp_path, provider_family=_OLLAMA_KEY)

    result = _run_start(capture)

    assert result.status is MemoryCaptureStatus.CAPTURED
    [entry] = [
        operation
        for operation in store.read_memory_operations()
        if operation.operation_kind is MemoryOperationKind.CAPTURE
    ]
    [memory_ref] = entry.memory_refs
    record = store.read_record(memory_ref, MemoryRecordKind.EPISODIC_RUN, run_id=entry.run_id)
    scope = record.envelope.scope
    assert scope.provider_family == _OLLAMA_FAMILY
    assert scope.provider_family != _OLLAMA_KEY
    # The rest of the SUPPLIED scope survives - canonicalization replaces one
    # field, it does not fall back to the residual construction (`B-90`).
    assert scope.tenant == _TENANT
    assert scope.workload_class == WorkloadClass.PIPELINE_AUTOMATION.value


def test_supplied_record_scope_out_of_domain_is_refused_and_writes_nothing(
    tmp_path: Path,
) -> None:
    """Codex R2 [P2-a] - the deny half, and it must deny BEFORE any write.

    `null` is not the fallback (it is C-MEM-03's unpartitioned wildcard, which
    would WIDEN reach), and neither is storing the identifier verbatim. The
    refusal must also leave no record and no C-MEM-08 row behind - a denied
    write that still landed a row would be the worst of both.
    """
    store, capture = _supplied_scope_capture(tmp_path, provider_family=_UNREGISTERED_KEY)

    with pytest.raises(MemoryCaptureScopeValueDomainError) as excinfo:
        _run_start(capture)

    assert _UNREGISTERED_KEY in str(excinfo.value)
    assert list(store.read_memory_operations()) == []
    assert not (tmp_path / "memory" / "episodic").exists()


def test_captured_scope_round_trips_where_the_pre_repair_scope_does_not(tmp_path: Path) -> None:
    """:909 / acceptance :894 - retrievable under a family-scoped request.

    The derived retrieval index covers the semantic/procedural record
    directories only, so the round trip is asserted by writing records that
    carry (i) the scope the capture path ACTUALLY wrote and (ii) the scope it
    wrote PRE-repair, and issuing one family-scoped request against both. The
    scope under test is the writer's real output, not a hand-built stand-in.
    """
    written_scope = _captured_run_scope(tmp_path)
    # Anchor the precondition: both sides of the comparison below are DERIVED
    # from the writer's output, so without this the test stays green against a
    # writer that never repaired anything - it would simply compare a raw-key
    # scope with itself. Mutation-probed.
    assert written_scope.provider_family == _OLLAMA_FAMILY
    assert written_scope.tenant == _TENANT
    pre_repair_scope = written_scope.model_copy(
        # Exactly what `memory_capture._record` constructed before the repair:
        # the raw per-turn provider key, and no tenant / workload_class.
        update={"provider_family": _OLLAMA_KEY, "tenant": None, "workload_class": None}
    )

    binding = _binding_root(tmp_path)
    store = _store(binding)
    # Same query terms on both, so the only thing separating them is scope.
    repaired = _semantic_record(
        written_scope,
        statement="Provider family partition scope, composed at run start.",
    )
    legacy = _semantic_record(
        pre_repair_scope,
        statement="Provider family partition scope, written from the raw key.",
    )
    store.write_record(repaired)
    store.write_record(legacy)
    index_store = _index_store(binding)
    index_store.rebuild(indexed_at=_NOW)
    resolver = MemoryPolicyResolver(_policy())
    retriever = MemoryRetriever(
        store=store,
        index_store=index_store,
        policy_resolver=resolver,
        policy_ref=_POLICY_REF,
        family_canonicalizer=canonical_scope_family,
    )

    result = retriever.retrieve(
        MemoryRetrievalRequest(
            run_id="run-u-mem-26",
            workflow_id="memory-substrate",
            workload_class="coding-arc",
            cli_profile="generic",
            provider=_OLLAMA_KEY,
            model="llama3.1",
            query_summary="provider family partition scope",
            scope=written_scope,
            token_budget=400,
        ),
        timestamp=_NOW,
        actor=_actor(),
        access_mode=MemoryPacketAccessMode.PROMPT_EXTENSION_PACKET,
    )

    excluded = {ref.memory_ref: ref.reason for ref in result.excluded_refs}
    assert repaired.envelope.memory_id in result.selected_refs, excluded
    assert legacy.envelope.memory_id not in result.selected_refs


# ---------------------------------------------------------------------------
# (b) promotion - canonicalized AHEAD of risk-flag and identity derivation
# ---------------------------------------------------------------------------


def _hint(provider_family: str | None) -> dict[str, object]:
    return {
        "proposed_kind": PromotionCandidateKind.FACT.value,
        "statement": "Memory partitions follow the run's provider family.",
        "confidence": PromotionCandidateConfidence.HIGH.value,
        "suggested_scope": _scope(provider_family).model_dump(mode="json"),
    }


def _source_record(scope: MemoryScope, hints: list[dict[str, object]]) -> MemoryStoreRecord:
    content: dict[str, object] = {
        "event_type": "turn_completion",
        "summary": "a turn that proposed a promotion candidate",
        "promotion_candidates": hints,
    }
    content_hash = compute_memory_content_hash(content)
    return MemoryStoreRecord(
        envelope=MemoryRecordEnvelope(
            memory_id=derive_memory_id(
                MemoryTier.EPISODIC, MemoryRecordKind.EPISODIC_TURN, content_hash
            ),
            schema_version="memory-store-record/v1",
            tier=MemoryTier.EPISODIC,
            kind=MemoryRecordKind.EPISODIC_TURN,
            created_at=_NOW,
            source_refs=(SourceRef(ref_type=SourceRefType.TURN, ref="turn-1"),),
            scope=scope,
            content_hash=content_hash,
            redaction_state=RedactionState.ACTIVE,
        ),
        content=content,
    )


def _extract(source: MemoryStoreRecord) -> list[PromotionCandidate]:
    extractor = PromotionCandidateExtractor(MemoryPolicyResolver(_policy()))
    return extractor.extract_from_records([source])


def test_promotion_hint_with_registered_key_is_canonicalized(tmp_path: Path) -> None:
    """:911 sub-case 1 - the registered key never reaches the persisted scope."""
    source = _source_record(_scope(_OLLAMA_FAMILY), [_hint(_OLLAMA_KEY)])

    [candidate] = _extract(source)

    assert candidate.suggested_scope.provider_family == _OLLAMA_FAMILY
    assert candidate.suggested_scope.provider_family != _OLLAMA_KEY
    assert tmp_path.exists()  # no durable write is needed to observe the derivation


def test_promotion_hint_with_unregistered_identifier_is_denied() -> None:
    """:911 sub-case 2 - denied per C-MEM-09 rather than persisted."""
    source = _source_record(_scope(_OLLAMA_FAMILY), [_hint(_UNREGISTERED_KEY)])

    with pytest.raises(PromotionScopeValueDomainError) as excinfo:
        _extract(source)

    assert _UNREGISTERED_KEY in str(excinfo.value)


def test_key_and_value_equivalent_hints_derive_the_same_candidate_id() -> None:
    """:913 ordering witness (i) - fails if canonicalization sits at the write.

    `_candidate_id` hashes the whole `suggested_scope`, so a raw key and its
    family value produce DIFFERENT identities unless canonicalization runs
    first.
    """
    # Both hints ride ONE source record: `_candidate_id` folds in the source
    # memory_id, so a second record would differ for a reason other than scope.
    source = _source_record(
        _scope(_OLLAMA_FAMILY),
        [_hint(_OLLAMA_KEY), _hint(_OLLAMA_FAMILY)],
    )

    from_key, from_value = _extract(source)

    assert from_key.suggested_scope == from_value.suggested_scope
    assert from_key.candidate_id == from_value.candidate_id


def test_registered_alias_of_the_source_family_is_not_flagged_cross_scope() -> None:
    """:913 - a registered alias of the source family is not an escape.

    This was the second ORDERING witness while `_scope_escapes_source`
    compared `provider_family` as a raw string. Codex R3 [P2-b] moved that
    comparison onto canonical values on BOTH sides, so the property now holds
    independently of where canonicalization runs - `_candidate_id` (witness (i)
    above) is what still pins the ordering. Kept as the defence-in-depth half:
    the alias must not read as an escape by either route.
    """
    source = _source_record(_scope(_OLLAMA_FAMILY), [_hint(_OLLAMA_KEY)])

    [candidate] = _extract(source)

    assert PromotionRiskFlag.CROSS_SCOPE not in candidate.risk_flags


# ---------------------------------------------------------------------------
# (b2) / (c) the tool executor under a statically-supplied context
# ---------------------------------------------------------------------------


def _context(scope: MemoryScope, *, provider: str = _OLLAMA_KEY) -> MemoryToolExecutionContext:
    return MemoryToolExecutionContext(
        run_id="run-u-mem-26",
        workflow_id="memory-substrate",
        workload_class="coding-arc",
        step_id="step-memory-tools",
        provider=provider,
        model="llama3.1",
        cli_profile="generic",
        scope=scope,
        scope_ref=_SCOPE_REF,
        policy_ref=_POLICY_REF,
        token_budget=120,
        timestamp=_NOW,
        actor=_actor(),
    )


def _executor(
    tmp_path: Path,
    *,
    records: tuple[MemoryStoreRecord, ...] = (),
) -> tuple[CanonicalMemoryStore, StandardMemoryToolExecutor]:
    binding = _binding_root(tmp_path)
    store = _store(binding)
    for record in records:
        store.write_record(record)
    index_store = _index_store(binding)
    index_store.rebuild(indexed_at=_NOW)
    resolver = MemoryPolicyResolver(_policy())
    retriever = MemoryRetriever(
        store=store,
        index_store=index_store,
        policy_resolver=resolver,
        policy_ref=_POLICY_REF,
        family_canonicalizer=canonical_scope_family,
    )
    return store, StandardMemoryToolExecutor(
        store=store,
        index_store=index_store,
        retriever=retriever,
        policy_resolver=resolver,
    )


def _promoted_record(store: CanonicalMemoryStore, promotion_ref: str) -> MemoryStoreRecord:
    return store.read_record(MemoryID(promotion_ref), MemoryRecordKind.SEMANTIC_FACT)


def test_tool_executor_promotion_under_static_context_lands_a_canonical_family(
    tmp_path: Path,
) -> None:
    """:911 sub-case 3 - the statically-supplied context scope is canonicalized."""
    source = _semantic_record(_scope(_OLLAMA_FAMILY))
    store, executor = _executor(tmp_path, records=(source,))

    result = executor.execute(
        MemoryToolExecutionRequest(
            tool_name=MemoryToolName.PROPOSE_PROMOTION,
            arguments={
                "memory_ref": str(source.envelope.memory_id),
                "target_kind": PromotionCandidateKind.FACT.value,
                "policy_ref": _POLICY_REF,
            },
            context=_context(_scope(_OLLAMA_KEY)),
        )
    )

    promoted = _promoted_record(store, str(result["promotion_ref"]))
    assert promoted.envelope.scope.provider_family == _OLLAMA_FAMILY
    assert promoted.envelope.scope.provider_family != _OLLAMA_KEY


def test_write_note_lands_the_context_record_scope_not_a_provider_derived_one(
    tmp_path: Path,
) -> None:
    """`_write_note` by-rule witness - the same `B-89` / `B-90` obligation.

    The context's provider KEY (`ollama`) differs from its record scope's
    family (`anthropic`) on purpose: pre-repair the note landed under a scope
    built from the KEY, with no tenant and no workload_class.
    """
    store, executor = _executor(tmp_path)
    context = _context(_scope(ProviderFamily.ANTHROPIC.value))

    result = executor.execute(
        MemoryToolExecutionRequest(
            tool_name=MemoryToolName.WRITE_NOTE,
            arguments={
                "note": "Memory scope is a run-level partition.",
                "scope_ref": _SCOPE_REF,
                "policy_ref": _POLICY_REF,
            },
            context=context,
        )
    )

    record = store.read_record(
        MemoryID(str(result["memory_ref"])),
        MemoryRecordKind.TOOL_EVENT,
        run_id=context.run_id,
    )
    assert record.envelope.scope == context.scope
    assert record.envelope.scope.provider_family == ProviderFamily.ANTHROPIC.value
    assert record.envelope.scope.tenant == _TENANT
    assert record.envelope.scope.workload_class == "coding-arc"


def test_tool_executor_denies_an_out_of_domain_context_scope(tmp_path: Path) -> None:
    """The unregistered half of the same executor boundary."""
    _store_unused, executor = _executor(tmp_path)

    with pytest.raises(MemoryToolExecutionDeniedError):
        executor.execute(
            MemoryToolExecutionRequest(
                tool_name=MemoryToolName.WRITE_NOTE,
                arguments={
                    "note": "A note under an out-of-domain scope.",
                    "scope_ref": _SCOPE_REF,
                    "policy_ref": _POLICY_REF,
                },
                context=_context(_scope(_UNREGISTERED_KEY)),
            )
        )


# ---------------------------------------------------------------------------
# (d) compaction
# ---------------------------------------------------------------------------


def _compaction_candidate(
    provider_family: str,
    *,
    candidate_id: str = "promocand:u-mem-26",
) -> PromotionCandidate:
    return PromotionCandidate(
        candidate_id=candidate_id,
        source_refs=(SourceRef(ref_type=SourceRefType.TURN, ref="turn-1"),),
        proposed_kind=PromotionCandidateKind.FACT,
        statement="A candidate carried into compaction.",
        confidence=PromotionCandidateConfidence.HIGH,
        suggested_scope=_scope(provider_family),
        policy_decision=PromotionDecision.PROPOSE_SEMANTIC,
        review_mode=ReviewMode.OPERATOR_REQUIRED,
        review_required=True,
        auto_promote_allowed=False,
    )


def _complete_compaction(
    tmp_path: Path,
    *candidates: PromotionCandidate,
) -> MemoryStoreRecord:
    store = _store(_binding_root(tmp_path))
    hook = CompactionSafetyHook(store=store, actor=_actor(), run_id="run-u-mem-26")
    result = hook.complete_compaction(
        compaction_id="compaction-1",
        candidates=candidates,
        dispositions=tuple(
            CompactionCandidateDispositionRecord(
                candidate_id=candidate.candidate_id,
                disposition=CompactionCandidateDisposition.KEEP_EPISODIC,
                rationale="retained for the witness",
            )
            for candidate in candidates
        ),
        timestamp=_NOW,
        summary="compaction under a candidate-derived scope",
    )
    return result.record


def _written_files(binding: MemoryRootBinding) -> list[Path]:
    root = binding.default_root
    return sorted(path for path in root.rglob("*") if path.is_file()) if root.exists() else []


def _persisted_candidate_families(record: MemoryStoreRecord) -> list[object]:
    dispositions = record.content["candidate_dispositions"]
    assert isinstance(dispositions, list)
    families: list[object] = []
    for entry in dispositions:
        assert isinstance(entry, dict)
        scope = entry["suggested_scope"]
        assert isinstance(scope, dict)
        families.append(scope["provider_family"])
    return families


def test_compaction_canonicalizes_a_candidate_derived_registered_key(tmp_path: Path) -> None:
    """:912 registered half - asserted on the written compaction-decision record."""
    record = _complete_compaction(tmp_path, _compaction_candidate(_OLLAMA_KEY))

    assert record.envelope.scope.provider_family == _OLLAMA_FAMILY
    assert record.envelope.scope.provider_family != _OLLAMA_KEY


def test_compaction_canonicalizes_the_persisted_candidate_content(tmp_path: Path) -> None:
    """:912 registered half at the CONTENT - the envelope alone is not enough.

    The durable record persists every candidate's `suggested_scope` verbatim and
    hashes it, so an envelope-only canonicalization leaves the record
    self-inconsistent (envelope `local_open_weight`, content `ollama`) and the
    content hash - hence `memory_id` - derived from the raw key.
    """
    record = _complete_compaction(
        tmp_path,
        _compaction_candidate(_OLLAMA_KEY),
        _compaction_candidate(_OLLAMA_KEY, candidate_id="promocand:u-mem-26-second"),
    )

    assert _persisted_candidate_families(record) == [_OLLAMA_FAMILY, _OLLAMA_FAMILY]
    assert _OLLAMA_KEY not in _persisted_candidate_families(record)
    # The envelope agrees with the content it summarizes.
    assert record.envelope.scope.provider_family == _OLLAMA_FAMILY
    assert record.envelope.content_hash == compute_memory_content_hash(record.content)
    # Positive control for the deny-side "nothing written" assertion below.
    assert _written_files(_binding_root(tmp_path))


def test_compaction_denies_a_candidate_derived_unregistered_identifier(tmp_path: Path) -> None:
    """:912 unregistered half."""
    with pytest.raises(CompactionScopeValueDomainError):
        _complete_compaction(tmp_path, _compaction_candidate(_UNREGISTERED_KEY))


def test_compaction_denies_an_out_of_domain_candidate_past_the_first(tmp_path: Path) -> None:
    """A non-scope-selecting candidate is checked too, and nothing is written."""
    binding = _binding_root(tmp_path)
    store = _store(binding)
    hook = CompactionSafetyHook(store=store, actor=_actor(), run_id="run-u-mem-26")
    candidates = (
        _compaction_candidate(_OLLAMA_KEY),
        _compaction_candidate(_UNREGISTERED_KEY, candidate_id="promocand:u-mem-26-second"),
    )

    with pytest.raises(CompactionScopeValueDomainError):
        hook.complete_compaction(
            compaction_id="compaction-1",
            candidates=candidates,
            dispositions=tuple(
                CompactionCandidateDispositionRecord(
                    candidate_id=candidate.candidate_id,
                    disposition=CompactionCandidateDisposition.KEEP_EPISODIC,
                    rationale="retained for the witness",
                )
                for candidate in candidates
            ),
            timestamp=_NOW,
            summary="compaction under a candidate-derived scope",
        )

    assert _written_files(binding) == []


# ---------------------------------------------------------------------------
# (e) native adapter tool events
# ---------------------------------------------------------------------------


def _native_backend(
    tmp_path: Path,
    scope: MemoryScope,
) -> tuple[CanonicalMemoryStore, CanonicalNativeMemoryToolBackend]:
    store = _store(_binding_root(tmp_path))
    backend = CanonicalNativeMemoryToolBackend(
        store=store,
        policy_resolver=MemoryPolicyResolver(_policy()),
        scope=scope,
        actor=_actor(),
        run_id="run-u-mem-26",
        policy_ref=_POLICY_REF,
        clock=lambda: _NOW,
    )
    return store, backend


def _persisted_json_files(tmp_path: Path) -> list[str]:
    return sorted(path.as_posix() for path in (tmp_path / "memory").rglob("*.json"))


@pytest.mark.asyncio
async def test_native_adapter_canonicalizes_a_registered_constructor_key(tmp_path: Path) -> None:
    """:914 registered half - asserted on the written tool-event record."""
    store, backend = _native_backend(tmp_path, _scope(_OLLAMA_KEY))

    await backend.create("/memories/notes.md", b"native memory content")

    [entry] = [
        item
        for item in store.read_memory_operations()
        if item.operation_kind is MemoryOperationKind.NATIVE_ADAPTER_CALL
    ]
    [memory_ref] = entry.memory_refs
    record = store.read_record(memory_ref, MemoryRecordKind.TOOL_EVENT, run_id=entry.run_id)
    assert record.envelope.scope.provider_family == _OLLAMA_FAMILY
    assert record.envelope.scope.provider_family != _OLLAMA_KEY


@pytest.mark.asyncio
async def test_native_adapter_denial_leaves_store_and_ledger_untouched(tmp_path: Path) -> None:
    """:914 unregistered half - the ORDERING requirement for this surface.

    The denial must fire before `_append_native_adapter_call`; at the record
    write it would strand a durable, hash-chained `native_adapter_call` entry
    referencing a record that was never persisted.
    """
    store, backend = _native_backend(tmp_path, _scope(_UNREGISTERED_KEY))
    before = _persisted_json_files(tmp_path)

    with pytest.raises(MemoryCallbackIOError):
        await backend.create("/memories/notes.md", b"native memory content")

    assert list(store.read_memory_operations()) == []
    assert _persisted_json_files(tmp_path) == before


def test_native_adapter_direct_reader_denies_a_crafted_raw_key_scope(tmp_path: Path) -> None:
    """:917 - the canonicalize step fires before `_scope_not_broader` sees either side.

    Asserted against `_require_retrieval_allowed` directly: `view()` would stop
    earlier, at `_latest_state`'s whole-scope equality, and would therefore
    pass over the predicate under test.
    """
    legacy = _semantic_record(_scope(_OLLAMA_KEY))
    _store_unused, backend = _native_backend(tmp_path, _scope(_OLLAMA_KEY))
    validated = backend._validate_observed_path("/memories/notes.md")  # pyright: ignore[reportPrivateUsage]

    with pytest.raises(MemoryCallbackIOError):
        backend._require_retrieval_allowed(legacy, validated)  # pyright: ignore[reportPrivateUsage]


def test_native_adapter_direct_reader_serves_a_canonical_record(tmp_path: Path) -> None:
    """The positive control for :917 - the denial above is about the RAW KEY."""
    canonical = _semantic_record(_scope(_OLLAMA_FAMILY))
    _store_unused, backend = _native_backend(tmp_path, _scope(_OLLAMA_KEY))
    validated = backend._validate_observed_path("/memories/notes.md")  # pyright: ignore[reportPrivateUsage]

    backend._require_retrieval_allowed(canonical, validated)  # pyright: ignore[reportPrivateUsage]


# ---------------------------------------------------------------------------
# (:918) standard-tool-executor by-reference direct readers
# ---------------------------------------------------------------------------


def test_executor_by_reference_readers_deny_a_crafted_raw_key_context(tmp_path: Path) -> None:
    """:918 - asserted on BOTH the index-entry lookup and the record-by-ref lookup.

    Without the canonicalize step the crafted request (`provider_family` =
    `ollama`) matches the legacy record's raw stored identifier verbatim and
    the "not retrievable under a family-scoped request" guarantee is
    bypassable.
    """
    legacy = _semantic_record(_scope(_OLLAMA_KEY))
    _store_unused, executor = _executor(tmp_path, records=(legacy,))
    context = _context(_scope(_OLLAMA_KEY))

    with pytest.raises(MemoryToolExecutionDeniedError):
        executor._allowed_index_entry(legacy.envelope.memory_id, context)  # pyright: ignore[reportPrivateUsage]

    with pytest.raises(MemoryToolExecutionDeniedError):
        executor._read_retrievable_record_by_ref(legacy.envelope.memory_id, context)  # pyright: ignore[reportPrivateUsage]

    # End to end through the public surface, for the same crafted context.
    with pytest.raises(MemoryToolExecutionDeniedError):
        executor.execute(
            MemoryToolExecutionRequest(
                tool_name=MemoryToolName.READ,
                arguments={
                    "memory_ref": str(legacy.envelope.memory_id),
                    "policy_ref": _POLICY_REF,
                },
                context=context,
            )
        )


def test_executor_by_reference_readers_serve_a_canonical_record(tmp_path: Path) -> None:
    """The positive control for :918 - the denial above is about the RAW KEY."""
    canonical = _semantic_record(_scope(_OLLAMA_FAMILY))
    _store_unused, executor = _executor(tmp_path, records=(canonical,))
    context = _context(_scope(_OLLAMA_KEY))

    entry = executor._allowed_index_entry(canonical.envelope.memory_id, context)  # pyright: ignore[reportPrivateUsage]
    record = executor._read_retrievable_record_by_ref(canonical.envelope.memory_id, context)  # pyright: ignore[reportPrivateUsage]

    assert entry.memory_id == canonical.envelope.memory_id
    assert record.envelope.memory_id == canonical.envelope.memory_id


# ---------------------------------------------------------------------------
# (f) the LEGACY-REDACTION exception
# ---------------------------------------------------------------------------


def _redaction_service(store: CanonicalMemoryStore) -> MemoryRedactionService:
    return MemoryRedactionService(
        store=store,
        operation_actor=_actor(),
        event_actor=MemoryRedactionActor.OPERATOR,
        policy_ref=_POLICY_REF,
        run_id="run-u-mem-26",
    )


@pytest.mark.parametrize("transition", ["redact", "tombstone"])
def test_legacy_raw_key_record_stays_redactable_with_its_scope_intact(
    tmp_path: Path,
    transition: str,
) -> None:
    """:915 - the compliance witness.

    A redaction is a STATE TRANSITION of an already-persisted record, not the
    authoring of a new scope. Applying the value domain here would make a
    pre-v1.1 record carrying a raw provider key impossible to redact or
    tombstone - an un-redactable legacy sensitive record. Exempting it launders
    nothing: a redaction cannot create a record that did not already exist and
    cannot introduce a value the record did not already carry.
    """
    legacy = _semantic_record(_scope(_OLLAMA_KEY))
    store = _store(_binding_root(tmp_path))
    store.write_record(legacy)
    service = _redaction_service(store)

    if transition == "redact":
        result = service.redact_content(
            legacy.envelope.memory_id,
            MemoryRecordKind.SEMANTIC_FACT,
            timestamp=_NOW,
            reason="operator redaction request",
            replacement_summary="[redacted]",
        )
    else:
        result = service.tombstone(
            legacy.envelope.memory_id,
            MemoryRecordKind.SEMANTIC_FACT,
            timestamp=_NOW,
            reason="operator tombstone request",
        )

    assert result.record.envelope.scope.provider_family == _OLLAMA_KEY
    # Byte-for-byte through the transition, not merely field-equal.
    assert json.dumps(
        result.record.envelope.scope.model_dump(mode="json"), sort_keys=True
    ) == json.dumps(legacy.envelope.scope.model_dump(mode="json"), sort_keys=True)


# ---------------------------------------------------------------------------
# Codex R3 - one posture, both sides canonical, forward-only means no rewrite
# ---------------------------------------------------------------------------


def test_native_adapter_direct_reader_rejects_an_out_of_domain_scope(tmp_path: Path) -> None:
    """Codex R3 [P2-a] ripple - the third posture also lived at this reader.

    The adapter refused an out-of-domain scope at its WRITE path
    (`_require_scope_family_in_domain`) but, on the read path, excluded only
    partition-scoped records - so an unpartitioned record was still served to a
    scope this substrate could not resolve. The record here carries `null`;
    under the old partition-only filter this call returned normally.
    """
    unpartitioned = _semantic_record(_scope(None))
    _store_unused, backend = _native_backend(tmp_path, _scope(_UNREGISTERED_KEY))
    validated = backend._validate_observed_path("/memories/notes.md")  # pyright: ignore[reportPrivateUsage]

    with pytest.raises(MemoryCallbackIOError):
        backend._require_retrieval_allowed(unpartitioned, validated)  # pyright: ignore[reportPrivateUsage]


def test_legacy_raw_key_source_is_not_flagged_cross_scope() -> None:
    """Codex R3 [P2-b] - the SOURCE side is a stored value, not a fresh input.

    `ollama` and `local_open_weight` name ONE partition. The hint side was
    canonicalized by the U-MEM-26 ordering rule, but the source record's stored
    family was compared raw, so a legacy same-family record read as an escape:
    `CROSS_SCOPE`, review forced, auto-promotion blocked.
    """
    source = _source_record(_scope(_OLLAMA_KEY), [_hint(_OLLAMA_FAMILY)])

    [candidate] = _extract(source)

    assert PromotionRiskFlag.CROSS_SCOPE not in candidate.risk_flags


def test_genuinely_cross_family_legacy_source_is_still_flagged_cross_scope() -> None:
    """Codex R3 [P2-b] negative - canonicalizing must not blunt the real flag.

    `claude_code` canonicalizes to `anthropic`, which is NOT the candidate's
    `local_open_weight`. A legacy raw key on the source side is still a real
    cross-family escape once resolved.
    """
    source = _source_record(_scope("claude_code"), [_hint(_OLLAMA_FAMILY)])

    [candidate] = _extract(source)

    assert PromotionRiskFlag.CROSS_SCOPE in candidate.risk_flags


def test_out_of_domain_source_family_is_still_flagged_cross_scope() -> None:
    """Codex R3 [P2-b] fail-closed - an unresolvable SOURCE family is an escape.

    The source names a partition this substrate cannot resolve, so the
    candidate cannot be shown to stay inside it. `CROSS_SCOPE` is the
    conservative answer - a review, not a disclosure. (The write boundary bites
    only on the CANDIDATE scope, so nothing else refuses this case.)
    """
    source = _source_record(_scope(_UNREGISTERED_KEY), [_hint(_OLLAMA_FAMILY)])

    [candidate] = _extract(source)

    assert PromotionRiskFlag.CROSS_SCOPE in candidate.risk_flags


# The run_id `LocalAutomaticMemoryRuntime` derives from `_step_context()` - the
# resumed run whose stored envelope must survive a fresh bootstrap.
_RESUMED_RUN_ID = "run-memory-step-0"


def _memory_root_store(tmp_path: Path) -> CanonicalMemoryStore:
    """A store bound to the root `materialize_automatic_memory_runtime` uses."""
    return CanonicalMemoryStore(
        root_binding=MemoryRootBinding(default_root=tmp_path / ".harness" / "memory"),
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
    )


def _seed_legacy_run_record(tmp_path: Path, *, run_id: str) -> Path:
    """Persist a pre-v1.1 EPISODIC_RUN envelope scoped by the RAW provider key."""
    store = _memory_root_store(tmp_path)
    content: dict[str, object] = {
        "event_type": "run_start",
        "run_id": run_id,
        "workflow_id": "workflow-memory",
        "thread_id": None,
        "engine_class": None,
        "cli_profile": "generic",
        "provider_route": [_OLLAMA_KEY],
        "close_status": "open",
    }
    content_hash = compute_memory_content_hash(content)
    record = MemoryStoreRecord(
        envelope=MemoryRecordEnvelope(
            memory_id=derive_memory_id(
                MemoryTier.EPISODIC, MemoryRecordKind.EPISODIC_RUN, content_hash
            ),
            schema_version="episodic-capture/v1",
            tier=MemoryTier.EPISODIC,
            kind=MemoryRecordKind.EPISODIC_RUN,
            created_at=_NOW,
            source_refs=(SourceRef(ref_type=SourceRefType.RUN, ref=run_id),),
            scope=_scope(_OLLAMA_KEY),
            content_hash=content_hash,
            redaction_state=RedactionState.ACTIVE,
        ),
        content=content,
    )
    store.write_record(record)
    return store.record_path(record)


def _compose_one_dispatch(tmp_path: Path) -> None:
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


def _capture_entries(store: CanonicalMemoryStore) -> list[MemoryOperationEntry]:
    return [
        entry
        for entry in store.read_memory_operations()
        if entry.operation_kind is MemoryOperationKind.CAPTURE
    ]


def test_run_start_capture_preserves_a_pre_existing_run_envelope(tmp_path: Path) -> None:
    """Codex R3 [P2-c] - forward-only: a resumed run's history is not re-scoped.

    `_started_runs` is in-process, so a FRESH bootstrap resuming an older run
    saw an empty set and captured run-start again - and EPISODIC_RUN is one
    `run.json` per run_id, so `write_record` REPLACED the stored envelope under
    today's canonical scope. Byte-equality is the assertion, not field
    equality: the defect was a silent rewrite, so anything that re-authored the
    file at all is the defect.
    """
    assert _step_context().parent_idempotency_key == _RESUMED_RUN_ID  # no silent drift
    run_path = _seed_legacy_run_record(tmp_path, run_id=_RESUMED_RUN_ID)
    before = run_path.read_bytes()

    _compose_one_dispatch(tmp_path)

    assert run_path.read_bytes() == before
    stored_scope = json.loads(run_path.read_text())["envelope"]["scope"]
    assert stored_scope["provider_family"] == _OLLAMA_KEY  # still the legacy key
    assert _capture_entries(_memory_root_store(tmp_path)) == []  # and no duplicate row


def test_run_start_capture_still_lands_a_new_run_id(tmp_path: Path) -> None:
    """Codex R3 [P2-c] positive control - presence is keyed per RUN, not global.

    Another run's stored envelope must not suppress this run's first capture;
    the skip is a durable-presence check on THIS run_id, not a "some history
    exists" check.
    """
    _seed_legacy_run_record(tmp_path, run_id="run-an-unrelated-earlier-run")

    _compose_one_dispatch(tmp_path)

    store = _memory_root_store(tmp_path)
    [capture] = _capture_entries(store)
    [memory_ref] = capture.memory_refs
    record = store.read_record(
        memory_ref,
        MemoryRecordKind.EPISODIC_RUN,
        run_id=_RESUMED_RUN_ID,
    )
    assert record.envelope.scope.provider_family == _OLLAMA_FAMILY
