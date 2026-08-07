"""U-MEM-28 - the C-MEM-19 `input_validation_failure` class and the A-ii re-typing.

Back-flow authority: RATIFIED Class 2 fork
`.harness/class_2_fork_b88_memory_failure_input_validation_class.md` (reading A
with sub-decision A-ii = RE-TYPE; register row `B-88`), applied at
`Spec_Memory_Substrate_v1.md` v1.3 and decomposed at
`Implementation_Plan_Memory_Substrate_v1.md` v1.3 U-MEM-28.

Three obligations live here, and they are INDEPENDENT - a suite that could not
tell them apart would let one of them regress green:

1. The seventh vocabulary member is additive and
   `MemoryToolExecutionInputError` is the one declaration that moves.
2. The dispatch SIX/TWO split: six `lifecycle/llm_dispatch.py` raises report
   HARNESS-INTERNAL faults and must NOT carry `input_validation_failure`; two
   validate the MODEL-supplied `scope_ref` argument and must KEEP it. Asserted
   PER SITE - an aggregate over "the dispatch sites" is satisfied by an
   implementation that re-typed all eight, which is the exact error the
   ratification corrected.
3. The RETRY disposition: fail-fast is PRESERVED for the six. Asserted per site
   AND end-to-end, because telemetry alone cannot see a site that accidentally
   raises the family BASE - the base classifies to the same residual, but is not
   in the fail-fast set, so it would silently fall through to transient retry.

Every site below is resolved BY CONTENT (what the check reads), never by line
offset: every offset in `llm_dispatch.py` had already shifted once between the
ratification and the spec leg.
"""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from harness_as.memory_tool_contracts import MEMORY_TOOL_CONTRACTS, MemoryToolName
from harness_as.sandbox_tier import SandboxTier
from harness_core import DeploymentSurface, PersonaTier
from harness_core.identity import StepID
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.gate_level_rule import GateLevel
from harness_cp.memory_access_mode import MemoryAccessMode, MemoryAccessModeSelection
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.workflow_driver_types import StepExecutionContext, StepKind, WorkflowStep
from harness_is.memory_observability import (
    MemoryTelemetryFailureClass,
    classify_memory_failure,
)
from harness_is.memory_operation_ledger import MemoryOperationWriteResult
from harness_is.memory_path_registry import MemoryRootBinding
from harness_is.memory_policy import (
    AccessDecision,
    CaptureDecision,
    MemoryPolicyDocument,
    MemoryPolicyResolver,
    PromotionDecision,
    ReviewMode,
)
from harness_is.memory_record_envelope import MemoryScope, MemoryVisibility
from harness_is.memory_retrieval import MemoryPacket, MemoryPacketAccessMode, MemoryRetriever
from harness_is.memory_retrieval_index import DerivedRetrievalIndexStore
from harness_is.memory_store import CanonicalMemoryStore
from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier
from harness_runtime.lifecycle import llm_dispatch as llm_dispatch_module
from harness_runtime.lifecycle.llm_dispatch import RuntimeLLMDispatcher
from harness_runtime.lifecycle.retry_breaker import DEFAULT_RETRY_POLICY, RuntimeRetryBreaker
from harness_runtime.lifecycle.retry_breaker_fallback import (
    RESERVED_LLM_DISPATCH_KEY,
    RetryBreakerFallbackDispatcher,
    RetryBreakerFallbackExhaustedError,
    RetryPolicy,
    _classify_provider_exception,
)
from harness_runtime.memory_context import RuntimeMemoryContext
from harness_runtime.memory_tool_executor import (
    MemoryToolExecutionContext,
    MemoryToolExecutionDeniedError,
    MemoryToolExecutionError,
    MemoryToolExecutionInputError,
    MemoryToolExecutionInternalError,
    MemoryToolExecutionRequest,
    MemoryToolExecutionStoreError,
    StandardMemoryToolExecutor,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

_INPUT_VALIDATION = MemoryTelemetryFailureClass.INPUT_VALIDATION_FAILURE
_POLICY_REF = "policy:u-mem-16"
_SCOPE_REF = "scope:u-mem-16"
_NOW = datetime(2026, 8, 6, 12, 0, 0, tzinfo=UTC)


# ---------------------------------------------------------------------------
# Fakes + fixtures. Deliberately self-contained: the production objects under
# test are real, only the provider SDK clients are stood in for.
# ---------------------------------------------------------------------------


@dataclass
class _Response:
    """Duck-typed provider response - the happy path is never reached here."""

    id: str = "cmpl_u_mem_28"
    prompt_eval_count: int = 20
    eval_count: int = 8
    _dump: dict[str, Any] = field(
        default_factory=lambda: {
            "id": "cmpl_u_mem_28",
            "choices": [{"message": {"content": "ok"}}],
            "message": {"content": "ok"},
        }
    )

    def model_dump(self) -> dict[str, Any]:
        return self._dump


class _Completions:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self.responses: list[_Response] = []

    async def create(self, **kwargs: Any) -> _Response:
        self.calls.append(kwargs)
        if self.responses:
            return self.responses.pop(0)
        return _Response()


class _OpenAIChat:
    def __init__(self) -> None:
        self.completions = _Completions()


class _OpenAIClient:
    def __init__(self) -> None:
        self.chat = _OpenAIChat()


def _openai_memory_tool_call_response() -> _Response:
    """One assistant turn calling `memory.search` with a well-formed argument set.

    Well-formed on purpose: the witness that consumes it is about a HARNESS-side
    fault, so the model's own arguments must not be what fails.
    """

    return _Response(
        id="cmpl_u_mem_28_tool",
        _dump={
            "id": "cmpl_u_mem_28_tool",
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_search",
                                "type": "function",
                                "function": {
                                    "name": "memory_search",
                                    "arguments": json.dumps(
                                        {"query": "q", "scope_ref": _SCOPE_REF},
                                        sort_keys=True,
                                    ),
                                },
                            }
                        ],
                    }
                }
            ],
        },
    )


@dataclass
class _OpenAIFakeAdapter:
    client: _OpenAIClient


class _OllamaClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def chat(self, **kwargs: Any) -> _Response:
        self.calls.append(kwargs)
        return _Response()


@dataclass
class _OllamaFakeAdapter:
    client: _OllamaClient


class _NoOpStandardMemoryToolExecutor:
    """Validates nothing - every witness here fails BEFORE the executor runs."""

    def validate(self, request: Any) -> None:
        return None

    def execute(self, request: Any) -> dict[str, object]:  # pragma: no cover - never reached
        raise AssertionError("no U-MEM-28 witness reaches tool execution")


def _scope(family: ProviderFamily = ProviderFamily.OPENAI) -> MemoryScope:
    return MemoryScope(
        project="arhugula-v2",
        workflow="memory-substrate",
        workload_class="coding-arc",
        provider_family=family.value,
        cli_profile="codex",
        visibility=MemoryVisibility.WORKFLOW,
    )


def _memory_context(
    *,
    provider: str = "openai",
    model: str = "test-model-1",
    family: ProviderFamily = ProviderFamily.OPENAI,
) -> RuntimeMemoryContext:
    packet = MemoryPacket(
        packet_id="memory-packet:" + ("c" * 32),
        packet_hash="c" * 64,
        token_budget=80,
        access_mode=MemoryPacketAccessMode.STANDARD_MEMORY_TOOLS,
        sections=(),
        selected_refs=(),
        policy_ref=_POLICY_REF,
    )
    return RuntimeMemoryContext(
        run_id="run-u-mem-28",
        access_mode=MemoryAccessMode.STANDARD_MEMORY_TOOLS,
        selection=MemoryAccessModeSelection(
            access_mode=MemoryAccessMode.STANDARD_MEMORY_TOOLS,
            selected_provider=provider,
            selected_model=model,
            selected_family=family,
            fallback_primary=f"{provider}:{model}",
            cli_profile_ref="codex",
            decision_trace=("standard_tools_policy_allowed",),
        ),
        policy_ref=_POLICY_REF,
        selected_refs=(),
        packet=packet,
        packet_hash=packet.packet_hash,
        retrieval_request_hash="d" * 64,
        record_scope=_scope(family),
        scope_ref=_SCOPE_REF,
        external_cli_route_ref=None,
        denial_reason=None,
        ledgerable_denial=False,
        injection_action_id=Identifier("memory-injection:" + ("e" * 32)),
        injection_operation_result=MemoryOperationWriteResult.APPENDED,
        prompt_packet_fallback_denial=None,
    )


def _binding(provider: str, model: str = "test-model-1") -> StepEffectiveBinding:
    return StepEffectiveBinding(
        step_id="step-001",
        model_binding=ModelBinding(provider=provider, model=model),
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        override_applied=False,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
    )


def _step() -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID("step-001"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={
            "messages": [{"role": "user", "content": "hi"}],
            "tools": None,
            "params": {"max_tokens": 100},
        },
    )


def _step_context() -> StepExecutionContext:
    return StepExecutionContext(
        workflow_id="test-wf",
        parent_action_id="workflow:test-wf:step:0",
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=Actor(actor_class=ActorClass.AGENT, actor_id="test-runtime"),
        parent_entry_hash="",
        parent_idempotency_key="test-step-key",
        tenant_id=None,
        step_index=0,
    )


def _dispatcher(
    memory_context: RuntimeMemoryContext,
    *,
    provider: str = "openai",
) -> RuntimeLLMDispatcher:
    adapter: Any = (
        _OpenAIFakeAdapter(_OpenAIClient())
        if provider == "openai"
        else _OllamaFakeAdapter(_OllamaClient())
    )
    return RuntimeLLMDispatcher(
        providers={provider: adapter},
        tracer_provider=TracerProvider(),
        memory_context=memory_context,
        standard_memory_tool_executor=_NoOpStandardMemoryToolExecutor(),
    )


async def _raised_by_dispatch(
    memory_context: RuntimeMemoryContext,
    *,
    provider: str = "openai",
) -> BaseException:
    """Drive the REAL dispatch path and return the exception it actually raised."""

    dispatcher = _dispatcher(memory_context, provider=provider)
    with pytest.raises(MemoryToolExecutionError) as excinfo:
        await dispatcher.dispatch(_binding(provider), _step(), step_context=_step_context())
    return excinfo.value


def _contracts_without_schema_properties() -> tuple[Any, ...]:
    """One real contract entry whose input schema has no `properties` mapping.

    `model_copy` rather than a hand-built stand-in, so the entry is otherwise
    byte-identical to the shipped one and the guard under test is the only
    thing that can fire.
    """

    entry = MEMORY_TOOL_CONTRACTS[0]
    return (
        entry.model_copy(
            update={
                "contract": entry.contract.model_copy(update={"input_schema": {"type": "object"}})
            }
        ),
    )


# ---------------------------------------------------------------------------
# 1. The vocabulary member and the single declaration flip.
# ---------------------------------------------------------------------------


def test_the_input_error_type_is_the_one_declaration_that_moved() -> None:
    """The flip site, and the four declarations that must NOT have moved with it."""

    assert MemoryToolExecutionInputError.memory_failure_class is _INPUT_VALIDATION
    # The other three declarations in the family are untouched, and the family
    # base still carries the RESIDUAL.
    assert (
        MemoryToolExecutionError.memory_failure_class
        is MemoryTelemetryFailureClass.PROVIDER_ADAPTER_FAILURE
    )
    assert (
        MemoryToolExecutionDeniedError.memory_failure_class
        is MemoryTelemetryFailureClass.POLICY_DENIAL
    )
    assert (
        MemoryToolExecutionStoreError.memory_failure_class is MemoryTelemetryFailureClass.IO_FAILURE
    )


def test_the_internal_fault_type_satisfies_its_three_receiving_type_constraints() -> None:
    """The receiving type's shape is load-bearing on all three counts.

    (a) NOT a subclass of the input type - `getattr` walks the MRO, so an
    inheriting subtype would carry `input_validation_failure` straight back into
    the internal population. (b) NOT the family base - the fail-fast tuple uses
    `isinstance`, which is subclass-inclusive, so admitting the base would
    silently fail-fast the denied and store subtypes that stay retryable on
    purpose. (c) declares a class OTHER than `input_validation_failure`.
    """

    assert not issubclass(MemoryToolExecutionInternalError, MemoryToolExecutionInputError)
    assert issubclass(MemoryToolExecutionInternalError, MemoryToolExecutionError)
    assert MemoryToolExecutionInternalError is not MemoryToolExecutionError
    assert classify_memory_failure(MemoryToolExecutionInternalError("x")) is not _INPUT_VALIDATION
    # (b) restated as behaviour, not as a type relation: the sibling subtypes
    # the fail-fast admission must NOT have swept in.
    assert _classify_provider_exception(MemoryToolExecutionDeniedError("x")) is not None
    assert _classify_provider_exception(MemoryToolExecutionStoreError("x")) is not None
    assert _classify_provider_exception(MemoryToolExecutionError("x")) is not None


# ---------------------------------------------------------------------------
# 2 + 3. The dispatch SIX/TWO split, per site, each internal site PAIRED with
#        its retry-exit assertion.
# ---------------------------------------------------------------------------


def test_internal_site_1_context_composition_unset_record_scope() -> None:
    """`_standard_memory_tool_context`: `memory_context.record_scope is None`.

    CONSTRUCTED SHAPE, and the reason was GROUNDED rather than assumed: a whole
    dispatch cannot reach this check, because `_standard_memory_tools_context`'s
    C-MEM-13 withholding conjunct calls `_packet_scope_matches_dispatch_family`,
    which returns `UNVERIFIABLE` (hence withhold) for a `record_scope is None`
    context - so the standard-tools arm is never taken and the memory tool loop
    never runs. The production function is still the thing under test; only its
    caller is stood in for.
    """

    context = _memory_context().model_copy(update={"record_scope": None})
    with pytest.raises(MemoryToolExecutionInternalError) as excinfo:
        llm_dispatch_module._standard_memory_tool_context(
            {"query": "q", "scope_ref": _SCOPE_REF},
            tool_name=MemoryToolName.SEARCH,
            memory_context=context,
            step_context=_step_context(),
            step_id="step-001",
            provider="openai",
            model="test-model-1",
        )

    exc = excinfo.value
    assert "RuntimeMemoryContext.record_scope" in str(exc)
    assert classify_memory_failure(exc) is not _INPUT_VALIDATION
    assert _classify_provider_exception(exc) is None


def test_the_withholding_guard_is_why_the_context_sites_are_unreachable() -> None:
    """The grounding behind sites 1 and 2's constructed shape, pinned.

    Without this, "unreachable end-to-end" is a claim in a docstring. If a later
    arc relaxes the withholding guard, the two context checks become reachable
    through a whole dispatch and this witness fails, forcing the reachability
    claim above to be re-derived rather than silently inherited.
    """

    assert (
        llm_dispatch_module._standard_memory_tools_context(
            "openai",
            memory_context=_memory_context().model_copy(update={"record_scope": None}),
            standard_memory_tool_executor=_NoOpStandardMemoryToolExecutor(),
        )
        is None
    )
    # ... and the un-degraded context IS served, so the None above is the guard
    # firing rather than the fixture being unservable for some other reason.
    assert (
        llm_dispatch_module._standard_memory_tools_context(
            "openai",
            memory_context=_memory_context(),
            standard_memory_tool_executor=_NoOpStandardMemoryToolExecutor(),
        )
        is not None
    )


def test_internal_site_2_context_composition_unset_scope_ref() -> None:
    """`_standard_memory_tool_context`: `memory_context.scope_ref is None`.

    CONSTRUCTED SHAPE, and the reason is stated rather than assumed: this site
    is unreachable through a whole dispatch, because the sibling schema-injection
    guard reads the SAME frozen context and fires first (witnessed at internal
    sites 3 and 5). The production function is still the thing under test - only
    its caller is stood in for.
    """

    context = _memory_context().model_copy(update={"scope_ref": None})
    with pytest.raises(MemoryToolExecutionInternalError) as excinfo:
        llm_dispatch_module._standard_memory_tool_context(
            {"query": "q", "scope_ref": _SCOPE_REF},
            tool_name=MemoryToolName.SEARCH,
            memory_context=context,
            step_context=_step_context(),
            step_id="step-001",
            provider="openai",
            model="test-model-1",
        )

    exc = excinfo.value
    assert "RuntimeMemoryContext.scope_ref" in str(exc)
    assert classify_memory_failure(exc) is not _INPUT_VALIDATION
    assert _classify_provider_exception(exc) is None


@pytest.mark.asyncio
async def test_internal_site_3_openai_schema_injection_unset_scope_ref() -> None:
    """`_openai_standard_memory_tools`: `memory_context.scope_ref is None`."""

    context = _memory_context().model_copy(update={"scope_ref": None})
    exc = await _raised_by_dispatch(context, provider="openai")

    assert isinstance(exc, MemoryToolExecutionInternalError)
    assert "schema injection" in str(exc)
    assert classify_memory_failure(exc) is not _INPUT_VALIDATION
    assert _classify_provider_exception(exc) is None


@pytest.mark.asyncio
async def test_internal_site_4_openai_schema_injection_properties_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`_openai_standard_memory_tools`: contract input schema has no `properties`."""

    monkeypatch.setattr(
        llm_dispatch_module,
        "MEMORY_TOOL_CONTRACTS",
        _contracts_without_schema_properties(),
    )
    exc = await _raised_by_dispatch(_memory_context(), provider="openai")

    assert isinstance(exc, MemoryToolExecutionInternalError)
    assert "input schema properties missing" in str(exc)
    assert classify_memory_failure(exc) is not _INPUT_VALIDATION
    assert _classify_provider_exception(exc) is None


@pytest.mark.asyncio
async def test_internal_site_5_ollama_schema_injection_unset_scope_ref() -> None:
    """`_ollama_standard_memory_tools`: `memory_context.scope_ref is None`."""

    context = _memory_context(
        provider="ollama", model="llama3.2:3b", family=ProviderFamily.LOCAL_OPEN_WEIGHT
    ).model_copy(update={"scope_ref": None})
    exc = await _raised_by_dispatch(context, provider="ollama")

    assert isinstance(exc, MemoryToolExecutionInternalError)
    assert "schema injection" in str(exc)
    assert classify_memory_failure(exc) is not _INPUT_VALIDATION
    assert _classify_provider_exception(exc) is None


@pytest.mark.asyncio
async def test_internal_site_6_ollama_schema_injection_properties_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`_ollama_standard_memory_tools`: contract input schema has no `properties`."""

    monkeypatch.setattr(
        llm_dispatch_module,
        "MEMORY_TOOL_CONTRACTS",
        _contracts_without_schema_properties(),
    )
    context = _memory_context(
        provider="ollama", model="llama3.2:3b", family=ProviderFamily.LOCAL_OPEN_WEIGHT
    )
    exc = await _raised_by_dispatch(context, provider="ollama")

    assert isinstance(exc, MemoryToolExecutionInternalError)
    assert "input schema properties missing" in str(exc)
    assert classify_memory_failure(exc) is not _INPUT_VALIDATION
    assert _classify_provider_exception(exc) is None


def test_retained_site_1_model_supplied_scope_ref_missing_or_non_string() -> None:
    """`_standard_memory_tool_context`: `arguments.get("scope_ref")` missing.

    RETAINED on the input type - this is the malformed-model-argument case the
    new class exists for. Re-typing it would deny the class one of its two
    clearest dispatch-side raise sites.
    """

    with pytest.raises(MemoryToolExecutionInputError) as excinfo:
        llm_dispatch_module._standard_memory_tool_context(
            {"query": "q"},
            tool_name=MemoryToolName.SEARCH,
            memory_context=_memory_context(),
            step_context=_step_context(),
            step_id="step-001",
            provider="openai",
            model="test-model-1",
        )

    assert classify_memory_failure(excinfo.value) is _INPUT_VALIDATION


def test_retained_site_2_model_supplied_scope_ref_mismatches_context() -> None:
    """`_standard_memory_tool_context`: `scope_ref != memory_context.scope_ref`."""

    with pytest.raises(MemoryToolExecutionInputError) as excinfo:
        llm_dispatch_module._standard_memory_tool_context(
            {"query": "q", "scope_ref": "scope:someone-else"},
            tool_name=MemoryToolName.SEARCH,
            memory_context=_memory_context(),
            step_context=_step_context(),
            step_id="step-001",
            provider="openai",
            model="test-model-1",
        )

    assert classify_memory_failure(excinfo.value) is _INPUT_VALIDATION


def test_the_dispatch_module_raises_exactly_six_internal_and_two_input_errors() -> None:
    """The split is CLOSED at six/two, counted from the AST at this HEAD.

    Without this, an arc that adds a seventh internal-fault raise on the input
    type passes every per-site witness above (they name the sites they drive)
    while re-opening the boundary this unit closed.
    """

    source = Path(llm_dispatch_module.__file__).read_text()
    raised: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Raise) or node.exc is None:
            continue
        exc = node.exc
        callee = exc.func if isinstance(exc, ast.Call) else exc
        if isinstance(callee, ast.Name):
            raised.append(callee.id)
    assert raised.count("MemoryToolExecutionInternalError") == 6
    assert raised.count("MemoryToolExecutionInputError") == 2


# ---------------------------------------------------------------------------
# The classify-routed population: emission preserved, nothing new wired.
# ---------------------------------------------------------------------------


def _executor(
    tmp_path: Path, *, tracer_provider: TracerProvider | None = None
) -> StandardMemoryToolExecutor:
    binding = MemoryRootBinding(default_root=tmp_path / "memory")
    surface = DeploymentSurface.LOCAL_DEVELOPMENT
    store = CanonicalMemoryStore(root_binding=binding, deployment_surface=surface)
    index_store = DerivedRetrievalIndexStore(root_binding=binding, deployment_surface=surface)
    index_store.rebuild(indexed_at=_NOW)
    resolver = MemoryPolicyResolver(
        MemoryPolicyDocument(
            policy_id=_POLICY_REF,
            enabled=True,
            capture_decision=CaptureDecision.CAPTURE_FULL,
            promotion_decision=PromotionDecision.PROPOSE_SEMANTIC,
            retrieval_access=AccessDecision.RETRIEVAL_ONLY,
            standard_tool_access=AccessDecision.STANDARD_TOOLS,
            review_mode=ReviewMode.OPERATOR_REQUIRED,
        )
    )
    return StandardMemoryToolExecutor(
        store=store,
        index_store=index_store,
        retriever=MemoryRetriever(
            store=store,
            index_store=index_store,
            policy_resolver=resolver,
            policy_ref=_POLICY_REF,
        ),
        policy_resolver=resolver,
        tracer_provider=tracer_provider,
    )


def _malformed_request() -> MemoryToolExecutionRequest:
    return MemoryToolExecutionRequest(
        tool_name=MemoryToolName.SEARCH,
        arguments={
            "query": 17,  # not a string - a genuine model-supplied argument refusal
            "scope_ref": _SCOPE_REF,
            "policy_ref": _POLICY_REF,
        },
        context=MemoryToolExecutionContext(
            run_id="run-u-mem-28",
            workflow_id="memory-substrate",
            workload_class="coding-arc",
            step_id="step-memory-tools",
            provider="openai",
            model="gpt-5",
            cli_profile="codex",
            scope=_scope(),
            scope_ref=_SCOPE_REF,
            policy_ref=_POLICY_REF,
            token_budget=120,
            timestamp=_NOW,
            actor=Actor(actor_class=ActorClass.AGENT, actor_id="codex"),
        ),
    )


def _tool_call_spans(exporter: InMemorySpanExporter) -> list[dict[str, Any]]:
    return [
        dict(span.attributes or {})
        for span in exporter.get_finished_spans()
        if span.name == "memory.tool_call"
    ]


@pytest.mark.parametrize("path", ["execute", "validate"])
def test_argument_refusal_emits_input_validation_failure_on_both_routed_paths(
    tmp_path: Path, path: str
) -> None:
    """Both classify-routed paths, asserted on the EMITTED span.

    `execute()`'s catch and the `B-84` `validate()` pre-pass are separate
    emission sites that can regress independently, so both are asserted. On the
    emitted span rather than on the classifier in isolation - the `B-88` impl
    half's own lesson was that a unit-green classifier proves nothing about what
    the production span carries.
    """

    exporter = InMemorySpanExporter()
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))
    executor = _executor(tmp_path, tracer_provider=tracer_provider)

    with pytest.raises(MemoryToolExecutionInputError):
        getattr(executor, path)(_malformed_request())

    [span] = _tool_call_spans(exporter)
    assert span["memory.failure_class"] == "input_validation_failure"
    assert span["memory.policy.decision"] == "failed"


def test_the_classify_routed_population_is_still_exactly_five_call_sites() -> None:
    """COVERAGE, stated as the spec states it: nothing withdrawn, nothing added.

    C-MEM-19 v1.3 keeps `memory.failure_class` REQUIRED for every operation its
    `Contract` list covers, so an implementation may not withdraw an emission by
    relocating a check onto an unclassified path; and the same paragraph records
    - without closing - that the dispatch PREPARE path opens no memory telemetry
    span. This unit wires no new emission and withdraws none, which is a claim
    about the call-site SET, so the set is pinned rather than described.
    """

    expected = {
        "harness-is/src/harness_is/memory_redaction.py": 1,
        "harness-runtime/src/harness_runtime/memory_capture.py": 1,
        # `execute()`'s catch and the B-84 `validate()` pre-pass.
        "harness-runtime/src/harness_runtime/memory_tool_executor.py": 2,
        "harness-runtime/src/harness_runtime/lifecycle/native_memory_adapter.py": 1,
    }
    workspace = Path(__file__).resolve().parents[2]
    found: dict[str, int] = {}
    for package in ("harness-is/src", "harness-runtime/src"):
        for module in sorted((workspace / package).rglob("*.py")):
            source = module.read_text()
            if "classify_memory_failure" not in source:
                continue
            count = sum(
                1
                for node in ast.walk(ast.parse(source))
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "classify_memory_failure"
            )
            if count:
                found[module.relative_to(workspace).as_posix()] = count
    assert found == expected


@pytest.mark.asyncio
async def test_the_dispatch_prepare_path_still_emits_no_memory_failure_class() -> None:
    """The gap C-MEM-19 v1.3 RECORDS and this unit does not close.

    The re-typed internal faults raise on the dispatch prepare path, which opens
    no memory telemetry span. This unit must not assert or imply an emission it
    does not build, so the absence is pinned - if a later arc wires one, this
    witness fails and that arc's own coverage change is forced into view.
    """

    exporter = InMemorySpanExporter()
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))
    context = _memory_context().model_copy(update={"scope_ref": None})
    dispatcher = RuntimeLLMDispatcher(
        providers={"openai": _OpenAIFakeAdapter(_OpenAIClient())},
        tracer_provider=tracer_provider,
        memory_context=context,
        standard_memory_tool_executor=_NoOpStandardMemoryToolExecutor(),
    )

    with pytest.raises(MemoryToolExecutionInternalError):
        await dispatcher.dispatch(_binding("openai"), _step(), step_context=_step_context())

    assert _tool_call_spans(exporter) == []


# ---------------------------------------------------------------------------
# The end-to-end dispatch/retry witness the telemetry witnesses cannot reach.
# ---------------------------------------------------------------------------


@dataclass
class _CountingInner:
    """A pass-through spy over the REAL dispatcher - counts attempts only."""

    inner: RuntimeLLMDispatcher
    calls: list[StepEffectiveBinding] = field(default_factory=list)

    async def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: Any = None,
    ) -> Any:
        self.calls.append(binding)
        return await self.inner.dispatch(binding, step, step_context=step_context)


@pytest.mark.asyncio
async def test_a_re_typed_internal_fault_takes_the_fail_fast_exit_end_to_end() -> None:
    """Through the REAL retry path, not by inspecting the isinstance tuple.

    A single-candidate chain plus `max_attempts=3`: under `TRANSIENT_RETRY` this
    consumes three dispatches, under fail-fast exactly one. `fail_threshold=1` is
    a TEST-FIXTURE value - not a production posture and not a claim about one -
    chosen only so the single fail-fast failure surfaces an observable
    transition; the transition's existence is then asserted BEFORE its cause, so
    the cause assertion cannot go vacuous. See the annotated block at the end of
    this test for what each of those three assertions is and is not saying.
    """

    emissions: list[Any] = []
    breaker = RuntimeRetryBreaker(
        retry_policies={
            RESERVED_LLM_DISPATCH_KEY: RetryPolicy(
                max_attempts=3, backoff="full_jitter", jitter="full_jitter"
            )
        },
        default_policy=DEFAULT_RETRY_POLICY,
        fail_threshold=1,
        base_delay_seconds=0.0,
        delay_cap_seconds=0.01,
    )

    @dataclass
    class _SpyingRegistry:
        inner: RuntimeRetryBreaker

        def get_policy(self, tool_name: str) -> RetryPolicy:
            return self.inner.get_policy(tool_name)

        def get_breaker(self, scope: Any, identifier: str) -> Any:
            return self.inner.get_breaker(scope, identifier)

        def compute_delay_seconds(self, attempt: int, rng: Any | None = None) -> float:
            return self.inner.compute_delay_seconds(attempt, rng)

        def advance_staircase(self, current: Any, cause: Any, attempt: int) -> Any:
            return self.inner.advance_staircase(current, cause, attempt)

        def emit_breaker_transition_event(
            self, transition: Any, parent_span_ref: Any, **kwargs: Any
        ) -> Any:
            emissions.append(transition)
            return self.inner.emit_breaker_transition_event(transition, parent_span_ref, **kwargs)

    context = _memory_context().model_copy(update={"scope_ref": None})
    inner = _CountingInner(inner=_dispatcher(context))
    exporter = InMemorySpanExporter()
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))

    async def _noop_sleep(_seconds: float) -> None:
        return None

    wrapper = RetryBreakerFallbackDispatcher(
        inner=inner,
        retry_breaker=_SpyingRegistry(inner=breaker),
        fallback_chain=FallbackChain(
            primary=ProviderCandidate(
                provider="openai", model="test-model-1", family=ProviderFamily.OPENAI
            ),
            same_family=(),
            cross_family=(),
        ),
        tracer_provider=tracer_provider,
        sleep_fn=_noop_sleep,
    )

    with pytest.raises(RetryBreakerFallbackExhaustedError):
        await wrapper.dispatch(_binding("openai"), _step(), step_context=_step_context())

    # Exactly ONE attempt: no same-candidate retry staircase, and no candidate
    # to advance to on the default single-candidate chain.
    assert len(inner.calls) == 1

    attempts = [
        span
        for span in exporter.get_finished_spans()
        if span.name == "harness.runtime.retry_attempt"
    ]
    first = attempts[0].attributes
    assert first is not None
    assert first["retry.fail_class"] == "permanent-fail-exit"
    assert first["retry.cause_attribution"] == "MemoryToolExecutionInternalError"

    # The breaker bookkeeping, in the shape the existing sibling witness for
    # this family already pins
    # (`test_lifecycle_retry_breaker_fallback.py::test_memory_tool_input_error_fail_fast_trip_carries_no_breaker_cause`).
    # Three separate things are being said here, and the middle one is a
    # TEST-FIXTURE fact rather than a production semantic (gemini R2 [P1] read it
    # as the latter):
    #
    # 1. POSITIVE CONTROL - a transition was actually emitted. Without it, the
    #    `cause` assertion below would pass vacuously on silence, which is the
    #    exact vacuity `fail_threshold=1` exists to remove. Production does NOT
    #    run a threshold of 1; that value is set at the top of THIS test purely
    #    so one fail-fast failure is observable as a transition. The fail-fast
    #    branch calling `breaker.record_failure(...)` at all is PRE-EXISTING
    #    behaviour shared with `MemoryToolExecutionInputError`
    #    (`LLMDispatchPayloadShapeError` too) since B-84; this unit adds a type
    #    to the same tuple and changes none of it.
    # 2. The transition's terminal state, asserted so the positive control is
    #    about a real OPEN transition rather than any emission at all.
    # 3. `cause is None` is the CORRECT value, not a missing one - and this is
    #    the assertion, not a lead-in to a different one. `_classify_breaker_cause`
    #    duck-types on `.status_code`, which this exception does not carry, so
    #    the honest report is the ABSENCE of a classified cause; C-OD-07 §7.1
    #    populates `harness.breaker.cause` only on a real classified trip.
    #    Hardcoding a cause here was precisely the B-88 lens-3 defect.
    assert len(emissions) == 1
    assert emissions[0].to_state.value == "open"
    assert emissions[0].cause is None
