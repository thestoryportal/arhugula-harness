"""Tests for C-MEM-01 - memory plane boundary (Spec_Memory_Substrate_v1.md).

C-MEM-01 is a cross-cutting architectural contract with no dedicated source
module of its own (§C-MEM-01: "Atomic implementation sequencing is allowed;
product completion requires the full contract family") - its invariants are
fulfilled collectively by the other C-MEM-* contracts. This file exercises the
two invariants no other test targets directly (B-35, .harness/forward-register.yaml):

  - "Native provider memory, standard tools, and prompt packet fallback operate
    against the same canonical store."
  - "Memory promotion and memory injection are distinct policy decisions."

(The other two C-MEM-01 invariants - provider-owned memory never canonical,
derived indexes never canonical - are already covered indirectly by
harness-runtime/tests/test_native_memory_adapter.py and
harness-is/tests/test_memory_retrieval_index.py::test_search_accelerator_is_non_authoritative.)
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from harness_as.memory_tool_contracts import MemoryToolName
from harness_core import DeploymentSurface
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import FallbackChain, ProviderCandidate, ProviderFamily
from harness_cp.memory_access_mode import MemoryAccessMode, MemoryProviderCapabilities
from harness_is.cli_profile import CliProfile, CliProfileKind
from harness_is.memory_operation_ledger import MemoryOperationKind
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
    MemoryRecordEnvelope,
    MemoryRecordKind,
    MemoryScope,
    MemoryTier,
    MemoryVisibility,
    SourceRef,
    SourceRefType,
    compute_memory_content_hash,
    derive_memory_id,
)
from harness_is.memory_retrieval import MemoryRetriever
from harness_is.memory_retrieval_index import DerivedRetrievalIndexStore
from harness_is.memory_store import CanonicalMemoryStore, MemoryStoreRecord
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_runtime.lifecycle.native_memory_adapter import CanonicalNativeMemoryToolBackend
from harness_runtime.memory_context import (
    MemoryContextCompositionRequest,
    RuntimeMemoryContextComposer,
)
from harness_runtime.memory_promotion import (
    PromotionCandidate,
    PromotionCandidateConfidence,
    PromotionCandidateKind,
    PromotionDecisionService,
    SemanticInjectionPolicy,
    SemanticRecordStatus,
)
from harness_runtime.memory_tool_executor import (
    MemoryToolExecutionContext,
    MemoryToolExecutionRequest,
    StandardMemoryToolExecutor,
)

_NOW = datetime(2026, 7, 15, 12, 0, 0, tzinfo=UTC)
_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="codex")
_POLICY_REF = "policy:c-mem-01-boundary"


def _binding(tmp_path: Path) -> MemoryRootBinding:
    return MemoryRootBinding(default_root=tmp_path / "memory")


def _store(binding: MemoryRootBinding) -> CanonicalMemoryStore:
    return CanonicalMemoryStore(
        root_binding=binding,
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
    )


def _scope() -> MemoryScope:
    return MemoryScope(
        project="arhugula-v2",
        workflow="memory-substrate",
        workload_class="coding-arc",
        provider_family="openai",
        cli_profile="codex",
        visibility=MemoryVisibility.WORKFLOW,
    )


def _seeded_record() -> MemoryStoreRecord:
    content: dict[str, object] = {
        "semantic_kind": MemoryRecordKind.PREFERENCE.value,
        "statement": "C-MEM-01 boundary probe: one record, three access paths.",
        "confidence": "high",
        "source_authority": "operator_direct",
        "status": "active",
        "injection_policy": "prompt_packet_allowed",
        "tags": ["c-mem-01"],
        "preference_subject": "operator_workflow",
        "preference_strength": "strong",
        "confirmation_required": False,
    }
    content_hash = compute_memory_content_hash(content)
    return MemoryStoreRecord(
        envelope=MemoryRecordEnvelope(
            memory_id=derive_memory_id(
                MemoryTier.SEMANTIC, MemoryRecordKind.PREFERENCE, content_hash
            ),
            schema_version="memory-store-record/v1",
            tier=MemoryTier.SEMANTIC,
            kind=MemoryRecordKind.PREFERENCE,
            created_at=_NOW,
            source_refs=(SourceRef(ref_type=SourceRefType.OPERATOR, ref="operator:c-mem-01"),),
            scope=_scope(),
            content_hash=content_hash,
        ),
        content=content,
    )


def _policy() -> MemoryPolicyDocument:
    return MemoryPolicyDocument(
        policy_id=_POLICY_REF,
        enabled=True,
        capture_decision=CaptureDecision.CAPTURE_FULL,
        promotion_decision=PromotionDecision.PROPOSE_SEMANTIC,
        retrieval_access=AccessDecision.RETRIEVAL_ONLY,
        standard_tool_access=AccessDecision.STANDARD_TOOLS,
        native_memory_access=AccessDecision.NATIVE_PROVIDER,
        injection_access=AccessDecision.PROMPT_PACKET,
        review_mode=ReviewMode.OPERATOR_REQUIRED,
        eligible_record_kinds=(MemoryRecordKind.PREFERENCE,),
    )


async def test_native_tools_and_packet_access_paths_share_one_canonical_ledger(
    tmp_path: Path,
) -> None:
    """C-MEM-01 invariant - native/standard-tools/prompt-packet all operate
    against the SAME canonical store. Proof: three independently-instantiated
    components (native adapter, standard-tool executor, prompt-context
    composer), each pointed at the SAME `MemoryRootBinding`, each write their
    OWN operation kind; a FOURTH, independently-constructed store then reads
    all three back from the ONE physical append-only ledger file. This is
    load-bearing, not an assumption from matching directory names - deleting
    any one component's write would drop that operation kind from the read-back
    set."""
    binding = _binding(tmp_path)
    policy = _policy()
    resolver = MemoryPolicyResolver(policy)

    # Seed one semantic record directly (bare store instance A).
    seed_store = _store(binding)
    seed_store.write_record(_seeded_record())
    index_store = DerivedRetrievalIndexStore(
        root_binding=binding, deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT
    )
    index_store.rebuild(indexed_at=_NOW)

    # Path 1 - standard memory tools (store instance B).
    tools_store = _store(binding)
    retriever = MemoryRetriever(
        store=tools_store, index_store=index_store, policy_resolver=resolver, policy_ref=_POLICY_REF
    )
    executor = StandardMemoryToolExecutor(
        store=tools_store, index_store=index_store, retriever=retriever, policy_resolver=resolver
    )
    search = executor.execute(
        MemoryToolExecutionRequest(
            tool_name=MemoryToolName.SEARCH,
            arguments={
                "query": "c-mem-01 boundary probe",
                "scope_ref": "scope:c-mem-01",
                "policy_ref": _POLICY_REF,
                "limit": 10,
                "allowed_kinds": ["preference"],
            },
            context=MemoryToolExecutionContext(
                run_id="run-c-mem-01",
                workflow_id="memory-substrate",
                workload_class="coding-arc",
                step_id="step-c-mem-01",
                provider="openai",
                model="gpt-5",
                cli_profile="codex",
                scope=_scope(),
                scope_ref="scope:c-mem-01",
                policy_ref=_POLICY_REF,
                token_budget=120,
                timestamp=_NOW,
                actor=_ACTOR,
            ),
        )
    )
    assert search["results"], "standard-tool path did not see the seeded record"

    # Path 2 - prompt-extension-packet fallback (store instance C, as the
    # composer's operation_store).
    packet_store = _store(binding)
    packet_retriever = MemoryRetriever(
        store=packet_store,
        index_store=index_store,
        policy_resolver=resolver,
        policy_ref=_POLICY_REF,
    )
    composer = RuntimeMemoryContextComposer(
        retriever=packet_retriever, operation_store=packet_store
    )
    context = composer.compose_run_start(
        MemoryContextCompositionRequest(
            run_id="run-c-mem-01",
            workflow_id="memory-substrate",
            workload_class="coding-arc",
            query_summary="c-mem-01 boundary probe",
            model_binding=ModelBinding(provider="openai", model="gpt-5"),
            fallback_chain=FallbackChain(
                primary=ProviderCandidate(
                    provider="openai", model="gpt-5", family=ProviderFamily.OPENAI
                ),
                same_family=(),
                cross_family=(),
            ),
            cli_profile=CliProfile(profile_id="codex", kind=CliProfileKind.CUSTOM),
            workflow_policy=policy,
            token_budget=120,
            record_scope=_scope(),
            allowed_kinds=(MemoryRecordKind.PREFERENCE,),
            timestamp=_NOW,
            actor=_ACTOR,
            policy_ref=_POLICY_REF,
            provider_capabilities=MemoryProviderCapabilities(
                provider="openai",
                model="gpt-5",
                supports_native_memory=False,
                supports_standard_memory_tools=False,
                supports_prompt_extension_packet=True,
            ),
        )
    )
    assert context.access_mode is MemoryAccessMode.PROMPT_EXTENSION_PACKET
    assert context.packet is not None

    # Path 3 - native provider adapter (store instance D).
    native_store = _store(binding)
    backend = CanonicalNativeMemoryToolBackend(
        store=native_store,
        policy_resolver=resolver,
        scope=_scope(),
        actor=_ACTOR,
        run_id="run-c-mem-01",
        step_id="step-c-mem-01-native",
        provider="anthropic",
        model="claude-test",
        cli_profile="claude",
        policy_ref=_POLICY_REF,
        clock=lambda: _NOW,
    )
    await backend.create("/memories/c-mem-01-probe.md", b"C-MEM-01 native probe.\n")

    # Read back from a FIFTH, independently-constructed store at the SAME
    # binding - proves all three writes landed in the one physical ledger.
    verify_store = _store(binding)
    operations = verify_store.read_memory_operations()
    kinds_seen = {op.operation_kind for op in operations}
    assert MemoryOperationKind.STANDARD_TOOL_CALL in kinds_seen, (
        "standard-tool op missing from ledger"
    )
    assert MemoryOperationKind.INJECT in kinds_seen, (
        "prompt-packet injection op missing from ledger"
    )
    assert MemoryOperationKind.NATIVE_ADAPTER_CALL in kinds_seen, (
        "native adapter op missing from ledger"
    )


def test_promotion_and_injection_are_independently_settable_policy_decisions(
    tmp_path: Path,
) -> None:
    """C-MEM-01 invariant - memory promotion and memory injection are DISTINCT
    policy decisions. Proof: a candidate can be PROMOTED to an active/canonical
    semantic record while its injection_policy is simultaneously NEVER -
    promotion (does this become canonical?) and injection (may this ever be
    surfaced to a prompt?) are settable to a deliberately dissonant
    combination, demonstrating neither implies the other."""
    store = _store(_binding(tmp_path))
    service = PromotionDecisionService(
        store=store,
        actor=_ACTOR,
        policy_ref=_POLICY_REF,
        run_id="run-c-mem-01",
        cli_profile="codex",
        provider="openai",
        model="gpt-5",
    )
    candidate = PromotionCandidate(
        candidate_id="candidate:fact",
        source_refs=(SourceRef(ref_type=SourceRefType.OPERATOR, ref="operator:c-mem-01"),),
        source_memory_refs=(),
        proposed_kind=PromotionCandidateKind.FACT,
        statement="Promote fact statement, forbid injection.",
        confidence=PromotionCandidateConfidence.HIGH,
        suggested_scope=_scope(),
        risk_flags=(),
        policy_decision=PromotionDecision.PROMOTE_SEMANTIC,
        review_mode=ReviewMode.AUTOMATIC,
        review_required=False,
        auto_promote_allowed=True,
    )

    result = service.approve(
        candidate,
        timestamp=_NOW,
        injection_policy=SemanticInjectionPolicy.NEVER,
    )

    assert result.status is SemanticRecordStatus.ACTIVE, (
        "promotion did not make the record canonical"
    )
    assert result.record.content["injection_policy"] == SemanticInjectionPolicy.NEVER.value, (
        "a promoted/active record must still be able to independently forbid injection - "
        "if this drifts to any other value, promotion and injection have been coupled"
    )
