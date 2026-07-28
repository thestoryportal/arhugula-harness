"""Tests for automatic local memory runtime wiring."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
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
from harness_is.memory_operation_ledger import MemoryOperationKind
from harness_is.memory_path_registry import MemoryRootBinding
from harness_is.memory_record_envelope import (
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
from harness_is.memory_retrieval import MemoryPacketAccessMode, MemoryRetrievalRequest
from harness_is.memory_retrieval_index import (
    DerivedRetrievalIndexQuery,
    DerivedRetrievalIndexStore,
)
from harness_is.memory_store import CanonicalMemoryStore, MemoryStoreRecord
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_runtime.automatic_memory import materialize_automatic_memory_runtime
from harness_runtime.lifecycle.llm_dispatch import RuntimeLLMDispatcher
from harness_runtime.types import OTelConfig, RuntimeConfig
from opentelemetry.sdk.trace import TracerProvider

_NOW = datetime(2026, 7, 4, 12, 0, 0, tzinfo=UTC)


@dataclass(frozen=True)
class _Usage:
    prompt_tokens: int
    completion_tokens: int


@dataclass(frozen=True)
class _ProviderResponse:
    id: str
    usage: _Usage
    _dump: dict[str, Any]

    def model_dump(self) -> dict[str, Any]:
        return self._dump


class _OpenAICompletions:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self.responses: list[_ProviderResponse] = []

    async def create(self, **kwargs: Any) -> _ProviderResponse:
        self.calls.append(kwargs)
        response = self.responses.pop(0)
        _fill_memory_tool_call_refs(response._dump, kwargs.get("tools"))
        return response


class _OpenAIChat:
    def __init__(self) -> None:
        self.completions = _OpenAICompletions()


class _OpenAIClient:
    def __init__(self) -> None:
        self.chat = _OpenAIChat()


@dataclass
class _OpenAIFakeAdapter:
    client: _OpenAIClient


# The OpenAI wire encoding of the C-MEM-14 provider-neutral `memory.search`
# identity (OpenAI rejects a dotted `tools[].function.name` with an HTTP 400).
_MEMORY_SEARCH_WIRE_NAME = "memory_search"


def _fill_memory_tool_call_refs(response: dict[str, Any], tools: object) -> None:
    scope_ref = _memory_tool_schema_const(tools, _MEMORY_SEARCH_WIRE_NAME, "scope_ref")
    policy_ref = _memory_tool_schema_const(tools, _MEMORY_SEARCH_WIRE_NAME, "policy_ref")
    if scope_ref is None or policy_ref is None:
        return
    for choice in response.get("choices", []):
        if not isinstance(choice, dict):
            continue
        message = choice.get("message")
        if not isinstance(message, dict):
            continue
        for tool_call in message.get("tool_calls", []):
            if not isinstance(tool_call, dict):
                continue
            function = tool_call.get("function")
            if not isinstance(function, dict) or function.get("name") != _MEMORY_SEARCH_WIRE_NAME:
                continue
            raw_arguments = function.get("arguments")
            if not isinstance(raw_arguments, str):
                continue
            arguments = json.loads(raw_arguments)
            if arguments.get("scope_ref") == "scope-filled-by-schema":
                arguments["scope_ref"] = scope_ref
            if arguments.get("policy_ref") == "policy-filled-by-schema":
                arguments["policy_ref"] = policy_ref
            function["arguments"] = json.dumps(arguments, sort_keys=True)


def _memory_tool_schema_const(
    tools: object,
    tool_name: str,
    property_name: str,
) -> str | None:
    if not isinstance(tools, list):
        return None
    for tool in tools:
        if not isinstance(tool, dict):
            continue
        function = tool.get("function")
        if not isinstance(function, dict) or function.get("name") != tool_name:
            continue
        parameters = function.get("parameters")
        if not isinstance(parameters, dict):
            continue
        properties = parameters.get("properties")
        if not isinstance(properties, dict):
            continue
        prop_schema = properties.get(property_name)
        if not isinstance(prop_schema, dict):
            continue
        value = prop_schema.get("const")
        if isinstance(value, str):
            return value
        enum_values = prop_schema.get("enum")
        if (
            isinstance(enum_values, list)
            and len(enum_values) == 1
            and isinstance(enum_values[0], str)
        ):
            return enum_values[0]
    return None


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        repository_root=tmp_path,
        otel=OTelConfig(otlp_endpoint="http://localhost:4318"),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
    )


def _memory_store(root: Path) -> CanonicalMemoryStore:
    return CanonicalMemoryStore(
        root_binding=MemoryRootBinding(default_root=root / ".harness" / "memory"),
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
    )


def _seed_preference(
    root: Path,
    *,
    provider_family: str = ProviderFamily.OPENAI.value,
    statement: str = "Use concise operator-facing memory summaries.",
    rebuild_index: bool = True,
) -> MemoryStoreRecord:
    """Seed one active preference record and (by default) rebuild the index.

    `provider_family` is a raw string rather than a `ProviderFamily` so a
    U-MEM-26 witness can seed a LEGACY record persisted with a provider KEY —
    the pre-v1.1 shape the forward-only residual leaves in place.
    """
    content: dict[str, object] = {
        "semantic_kind": "preference",
        "statement": statement,
        "confidence": "high",
        "source_authority": "operator_direct",
        "status": "active",
        "injection_policy": "tool_allowed",
        "preference_subject": "operator_workflow",
        "preference_strength": "strong",
        "confirmation_required": False,
        "tags": ["memory", "summary"],
    }
    content_hash = compute_memory_content_hash(content)
    record = MemoryStoreRecord(
        envelope=MemoryRecordEnvelope(
            memory_id=derive_memory_id(
                MemoryTier.SEMANTIC,
                MemoryRecordKind.PREFERENCE,
                content_hash,
            ),
            schema_version="memory-store-record/v1",
            tier=MemoryTier.SEMANTIC,
            kind=MemoryRecordKind.PREFERENCE,
            created_at=_NOW,
            scope=MemoryScope(
                project=root.name,
                workflow="workflow-memory",
                workload_class=WorkloadClass.PIPELINE_AUTOMATION.value,
                provider_family=provider_family,
                cli_profile="profile:generic",
                visibility=MemoryVisibility.PROJECT,
            ),
            source_refs=(SourceRef(ref_type=SourceRefType.OPERATOR, ref="operator:test"),),
            content_hash=content_hash,
            redaction_state=RedactionState.ACTIVE,
        ),
        content=content,
    )
    store = _memory_store(root)
    store.write_record(record)
    if rebuild_index:
        _rebuild_index(root)
    return record


def _rebuild_index(root: Path) -> None:
    DerivedRetrievalIndexStore(
        root_binding=MemoryRootBinding(default_root=root / ".harness" / "memory"),
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
    ).rebuild(indexed_at=_NOW)


def _binding(provider: str = "openai", model: str = "gpt-5") -> StepEffectiveBinding:
    return StepEffectiveBinding(
        step_id="memory-step",
        model_binding=ModelBinding(provider=provider, model=model),
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        override_applied=False,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
    )


def _fallback_chain(provider: str = "openai", model: str = "gpt-5") -> FallbackChain:
    return FallbackChain(
        primary=ProviderCandidate(provider=provider, model=model, family=ProviderFamily.OPENAI),
        same_family=(),
        cross_family=(),
    )


def _step(payload: dict[str, object] | None = None) -> WorkflowStep:
    return WorkflowStep(
        step_id="memory-step",
        step_kind=StepKind.INFERENCE_STEP,
        step_payload=payload
        or {
            "messages": [{"role": "user", "content": "What memory applies here?"}],
            "tools": None,
            "params": {"max_tokens": 100},
        },
    )


def _step_context() -> StepExecutionContext:
    return StepExecutionContext(
        workflow_id="workflow-memory",
        parent_action_id="workflow:workflow-memory:step:0",
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=Actor(actor_class=ActorClass.AGENT, actor_id="codex"),
        parent_entry_hash="",
        parent_idempotency_key="run-memory-step-0",
        tenant_id=None,
        step_index=0,
        run_engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
    )


def test_first_use_initializes_local_memory_root_and_prompt_packet(tmp_path: Path) -> None:
    runtime = materialize_automatic_memory_runtime(_config(tmp_path))

    assert runtime is not None
    assert (tmp_path / ".harness" / "memory" / "semantic" / "index.jsonl").is_file()

    context = runtime.compose_for_dispatch(
        binding=StepEffectiveBinding(
            step_id="memory-step",
            model_binding=ModelBinding(provider="anthropic", model="claude-opus-4-7"),
            engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
            override_applied=False,
            persona_tier=PersonaTier.SOLO_DEVELOPER,
        ),
        fallback_chain=FallbackChain(
            primary=ProviderCandidate(
                provider="anthropic",
                model="claude-opus-4-7",
                family=ProviderFamily.ANTHROPIC,
            ),
            same_family=(),
            cross_family=(),
        ),
        step=WorkflowStep(
            step_id="memory-step",
            step_kind=StepKind.INFERENCE_STEP,
            step_payload={"messages": [{"role": "user", "content": "remember repo rules"}]},
        ),
        step_context=StepExecutionContext(
            workflow_id="workflow-memory",
            parent_action_id="workflow:workflow-memory:step:0",
            parent_gate_level=GateLevel.AUTO,
            parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
            parent_actor=Actor(actor_class=ActorClass.AGENT, actor_id="codex"),
            parent_entry_hash="",
            parent_idempotency_key="run-memory-step-0",
            tenant_id=None,
            step_index=0,
            run_engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        ),
    )

    assert context.access_mode.value == "prompt_extension_packet"
    assert context.packet is not None
    assert context.packet.sections == ()


def test_external_cli_binding_composes_prompt_packet_not_standard_tools(
    tmp_path: Path,
) -> None:
    """F2 wiring: a CLI-routed binding selects the prompt packet, not standard tools.

    `_config` enables standard memory tools and defaults `external_cli_providers` to the
    claude_code/codex/antigravity set. A `claude_code` binding is NOT anthropic, so
    without the `is_external_cli` wiring it would (wrongly) select STANDARD_MEMORY_TOOLS
    — a mode the CLI subprocess dispatch cannot serve. This exercises the real
    `LocalAutomaticMemoryRuntime` path (`self._external_cli_provider_names`), not just
    the capability helper.
    """
    runtime = materialize_automatic_memory_runtime(_config(tmp_path))

    context = runtime.compose_for_dispatch(
        binding=StepEffectiveBinding(
            step_id="cli-memory-step",
            model_binding=ModelBinding(provider="claude_code", model="sonnet"),
            engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
            override_applied=False,
            persona_tier=PersonaTier.SOLO_DEVELOPER,
        ),
        fallback_chain=FallbackChain(
            primary=ProviderCandidate(
                provider="claude_code",
                model="sonnet",
                family=ProviderFamily.ANTHROPIC,
            ),
            same_family=(),
            cross_family=(),
        ),
        step=WorkflowStep(
            step_id="cli-memory-step",
            step_kind=StepKind.INFERENCE_STEP,
            step_payload={"messages": [{"role": "user", "content": "remember repo rules"}]},
        ),
        step_context=StepExecutionContext(
            workflow_id="workflow-memory",
            parent_action_id="workflow:workflow-memory:step:0",
            parent_gate_level=GateLevel.AUTO,
            parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
            parent_actor=Actor(actor_class=ActorClass.AGENT, actor_id="codex"),
            parent_entry_hash="",
            parent_idempotency_key="run-cli-memory-step-0",
            tenant_id=None,
            step_index=0,
            run_engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        ),
    )

    assert context.access_mode.value == "prompt_extension_packet"


@pytest.mark.asyncio
async def test_default_local_init_normal_inference_exposes_and_persists_memory(
    tmp_path: Path,
) -> None:
    runtime = materialize_automatic_memory_runtime(
        _config(tmp_path),
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
    )
    assert runtime is not None
    assert (tmp_path / ".harness" / "memory" / "semantic" / "index.jsonl").is_file()
    seed = _seed_preference(tmp_path)

    client = _OpenAIClient()
    client.chat.completions.responses = [
        _ProviderResponse(
            id="cmpl-memory-tool",
            usage=_Usage(prompt_tokens=10, completion_tokens=3),
            _dump={
                "id": "cmpl-memory-tool",
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": "call_memory_search",
                                    "type": "function",
                                    "function": {
                                        # The provider echoes the WIRE name it
                                        # was advertised, not the dotted identity.
                                        "name": _MEMORY_SEARCH_WIRE_NAME,
                                        "arguments": json.dumps(
                                            {
                                                "query": "operator memory summary preference",
                                                "scope_ref": "scope-filled-by-schema",
                                                "policy_ref": "policy-filled-by-schema",
                                            },
                                            sort_keys=True,
                                        ),
                                    },
                                }
                            ],
                        }
                    }
                ],
            },
        ),
        _ProviderResponse(
            id="cmpl-memory-final",
            usage=_Usage(prompt_tokens=16, completion_tokens=5),
            _dump={
                "id": "cmpl-memory-final",
                "choices": [{"message": {"role": "assistant", "content": "done"}}],
            },
        ),
    ]
    dispatcher = RuntimeLLMDispatcher(
        providers={"openai": _OpenAIFakeAdapter(client)},
        tracer_provider=TracerProvider(),
        memory_runtime=runtime,
        fallback_chain=_fallback_chain(),
    )

    await dispatcher.dispatch(_binding(), _step(), step_context=_step_context())

    first_call = client.chat.completions.calls[0]
    assert "tools" in first_call
    assert {tool["function"]["name"] for tool in first_call["tools"]} >= {
        "memory_search",
        "memory_read",
    }
    tool_content = json.loads(client.chat.completions.calls[1]["messages"][-1]["content"])
    assert tool_content["results"][0]["memory_ref"] == str(seed.envelope.memory_id)
    assert tool_content["results"][0]["text"] == "Use concise operator-facing memory summaries."
    store = _memory_store(tmp_path)
    operations = store.read_memory_operations()
    assert MemoryOperationKind.CAPTURE in {entry.operation_kind for entry in operations}
    captured_refs = [
        ref
        for entry in operations
        if entry.operation_kind is MemoryOperationKind.CAPTURE
        for ref in entry.memory_refs
    ]
    assert captured_refs
    captured = store.read_record(
        captured_refs[-1],
        MemoryRecordKind.EPISODIC_TURN,
        run_id="run-memory-step-0",
    )
    assert captured.content["capture_mode"] == "summarized"


# ---------------------------------------------------------------------------
# U-MEM-26 — the two obligations that only bind through the PRODUCTION wiring.
#
# `LocalAutomaticMemoryRuntime` is the composition root that injects
# `canonical_scope_family` into the retriever and the derived-index store
# (`automatic_memory.py:146-158`). `harness-is` declares that authority as an
# OPTIONAL seam because the IS axis has zero outbound cross-axis edges, so a
# unit test constructing its own retriever proves nothing about whether the
# real run wires it. These two witnesses drive the real runtime.
# ---------------------------------------------------------------------------


def _cross_family_chain() -> FallbackChain:
    """An ANTHROPIC-family primary for an OPENAI-family dispatch candidate.

    `compose_for_dispatch` derives `record_scope.provider_family` from
    `fallback_chain.primary.family` (`automatic_memory.py:205`), so this is the
    real shape of a cross-family fallback: the access-mode selection recomposes
    for the CURRENT candidate (openai, tool-capable → `standard_memory_tools`)
    while the retrieval scope stays on the chain primary's family.
    """
    return FallbackChain(
        primary=ProviderCandidate(
            provider="anthropic",
            model="claude-opus-4-7",
            family=ProviderFamily.ANTHROPIC,
        ),
        same_family=(),
        cross_family=(),
    )


@pytest.mark.asyncio
async def test_u_mem_26_capture_is_unaffected_by_the_cross_family_withholding(
    tmp_path: Path,
) -> None:
    """U-MEM-26 (:891 / :907) — harness-authored capture survives the withhold.

    C-MEM-13 (`Spec_Memory_Substrate_v1.md:509`): "Harness-authored memory
    capture is unaffected: capture is a different authorship class and crosses
    no boundary the harness does not already hold." The dispatch here is
    cross-family, so the tool schemas and the scope reference are withheld — and
    the capture must still write, under the run's COMPOSED scope.

    The captured `provider_family` is the discriminating assertion: it must be
    the chain primary's `anthropic` (the composed `record_scope`, `B-89`), NOT
    the dispatched candidate's `openai` provider key. Both halves fail on the
    pre-repair writer, and the first half additionally fails on any guard that
    short-circuits the dispatch instead of merely withholding memory access.
    """
    runtime = materialize_automatic_memory_runtime(
        _config(tmp_path),
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
    )
    assert runtime is not None
    _seed_preference(tmp_path)

    client = _OpenAIClient()
    client.chat.completions.responses = [
        _ProviderResponse(
            id="cmpl-withheld",
            usage=_Usage(prompt_tokens=11, completion_tokens=4),
            _dump={
                "id": "cmpl-withheld",
                "choices": [{"message": {"role": "assistant", "content": "answered"}}],
            },
        )
    ]
    dispatcher = RuntimeLLMDispatcher(
        providers={"openai": _OpenAIFakeAdapter(client)},
        tracer_provider=TracerProvider(),
        memory_runtime=runtime,
        fallback_chain=_cross_family_chain(),
    )

    await dispatcher.dispatch(_binding(), _step(), step_context=_step_context())

    # The withholding itself, end-to-end through the real composer.
    assert len(client.chat.completions.calls) == 1, "no tool loop — nothing to serve"
    assert "tools" not in client.chat.completions.calls[0], (
        "an anthropic-family-scoped context must not arm the tools for an openai dispatch"
    )

    # ...and the capture ran anyway, on the same dispatch.
    store = _memory_store(tmp_path)
    captured_refs = [
        ref
        for entry in store.read_memory_operations()
        if entry.operation_kind is MemoryOperationKind.CAPTURE
        for ref in entry.memory_refs
    ]
    assert captured_refs, "capture is a different authorship class and is NOT withheld (:891)"
    captured = store.read_record(
        captured_refs[-1],
        MemoryRecordKind.EPISODIC_TURN,
        run_id="run-memory-step-0",
    )
    assert captured.envelope.scope.provider_family == ProviderFamily.ANTHROPIC.value, (
        "the captured record carries the run's COMPOSED family value, not the "
        "dispatched candidate's provider key (`B-89`)"
    )
    assert captured.envelope.scope.workload_class == WorkloadClass.PIPELINE_AUTOMATION.value


def _crafted_scope(root: Path, provider_family: str) -> MemoryScope:
    """The seeded records' scope with `provider_family` swapped VERBATIM.

    Every other field mirrors the record so the C-MEM-09 policy leg (which
    denies a request BROADER than the record) cannot mask the family decision:
    `provider_family` is then the only dimension in play.

    `compose_for_dispatch` can only ever emit a `ProviderFamily` VALUE here (it
    reads `fallback_chain.primary.family.value`), so a raw-key request is by
    construction a CRAFTED one — which is exactly why the value domain has to
    bind at the read layer rather than at the composer.
    """
    return MemoryScope(
        project=root.name,
        workflow="workflow-memory",
        workload_class=WorkloadClass.PIPELINE_AUTOMATION.value,
        provider_family=provider_family,
        cli_profile="profile:generic",
        visibility=MemoryVisibility.PROJECT,
    )


def _retrieval_request(root: Path, provider_family: str) -> MemoryRetrievalRequest:
    return MemoryRetrievalRequest(
        run_id="run-memory-step-0",
        workflow_id="workflow-memory",
        workload_class=WorkloadClass.PIPELINE_AUTOMATION.value,
        cli_profile="profile:generic",
        provider="openai",
        model="gpt-5",
        query_summary="operator memory summary preference",
        scope=_crafted_scope(root, provider_family),
        token_budget=400,
        allowed_kinds=(MemoryRecordKind.PREFERENCE,),
    )


def test_u_mem_26_request_boundary_binds_through_the_production_wiring(
    tmp_path: Path,
) -> None:
    """U-MEM-26 (:897 / :916) — both halves, end-to-end, at BOTH read layers.

    `codex` is a REGISTERED provider key whose family is `openai`
    (`cross_family_cost_tag.py:65`), and it is NOT value-equal to that family —
    so a request naming it discriminates canonicalization from a no-op, which a
    request naming `openai` (key and value at once) could not.

    Positive half: the crafted `codex` request canonicalizes to `openai` and
    reaches the `openai`-VALUE record.

    Negative half, asserted at both layers because a single composite witness
    passes OVER whichever layer is still leaking: the LEGACY record persisted
    with the raw key `codex` stays unreachable by that same request. The request
    side canonicalizes; the record side does not (forward-only, no rewrite, no
    migration, `:885` / `:900`), so `openai != codex` denies it. Without the
    production injection at `automatic_memory.py:146-158` the raw strings would
    compare EQUAL and the crafted request would resurrect it.
    """
    runtime = materialize_automatic_memory_runtime(
        _config(tmp_path),
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
    )
    assert runtime is not None
    canonical = _seed_preference(tmp_path, rebuild_index=False)
    legacy = _seed_preference(
        tmp_path,
        provider_family="codex",
        statement="Legacy record persisted under a raw provider key.",
        rebuild_index=False,
    )
    _rebuild_index(tmp_path)
    assert canonical.envelope.memory_id != legacy.envelope.memory_id

    # The PRODUCTION-wired collaborators, reached through the runtime rather
    # than reconstructed — the whole point is that this run injects the
    # canonicalizer. Reconstructing them locally would assert the seam works,
    # never that the composition root binds it.
    retriever = runtime._composer._retriever
    index_store = retriever._index_store

    result = retriever.retrieve(
        _retrieval_request(tmp_path, "codex"),
        timestamp=_NOW,
        actor=Actor(actor_class=ActorClass.AGENT, actor_id="codex"),
        access_mode=MemoryPacketAccessMode.STANDARD_MEMORY_TOOLS,
    )
    assert canonical.envelope.memory_id in result.selected_refs, (
        "a registered raw provider key canonicalizes to its family value and "
        "reaches the family-value records (:916 positive half)"
    )
    assert legacy.envelope.memory_id not in result.selected_refs, (
        "the crafted raw-key request must NOT resurrect the legacy raw-key "
        "record through the retriever (:916 negative half, layer 1)"
    )

    index_result = index_store.retrieve(
        DerivedRetrievalIndexQuery(
            query_summary="operator memory summary preference",
            allowed_kinds=(MemoryRecordKind.PREFERENCE,),
            scope=_crafted_scope(tmp_path, "codex"),
        )
    )
    assert canonical.envelope.memory_id in index_result.selected_refs
    assert legacy.envelope.memory_id not in index_result.selected_refs, (
        "nor through the derived index (:916 negative half, layer 2)"
    )
    assert all(entry.memory_id != legacy.envelope.memory_id for entry in index_result.entries), (
        "neither the ref NOR the entry metadata may leak"
    )
