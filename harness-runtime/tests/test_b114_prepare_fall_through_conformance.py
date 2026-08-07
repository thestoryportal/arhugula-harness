"""B-114 - the executor `_prepare` exhaustiveness fall-through's C-MEM-19 type boundary.

Authority: `Spec_Memory_Substrate_v1.md` **v1.3**, C-MEM-19
`### Input validation failure`, the type-boundary paragraph and its Invariants
line - *"Where the failure class is determined from the raised exception type,
the type carrying input validation failure is raised only for those argument
refusals, and a harness-internal fault is not raised as that type; separating
such a fault out does not change its retry disposition."*

That rule is stated over the KIND of fault, not over an enumeration of sites, so
this is a conformance repair against ALREADY-CLEARED spec text rather than an
extension of `B-88`'s ratified A-ii site list (which named six sites, all in
`lifecycle/llm_dispatch.py`, because that filing never surveyed the executor).
U-MEM-28 left the site on the input type on AUTHORITY grounds - a spec leg
applies operator-decided fixes and may not widen a ratified enumeration on its
own reading - and recorded the resulting non-conformance for this row to own
(fork `class_2_fork_b88_...` §11.6 item 4; plan v1.3 U-MEM-28 Out-of-scope).

Three obligations, and they are INDEPENDENT - a suite that could not tell them
apart would let one of them regress green:

1. The RAISED TYPE at the real site is the internal-fault type and is not the
   input type (nor a subclass of it - the declaration is read through the MRO,
   so an inheriting subtype would carry `input_validation_failure` straight back
   into the internal population).
2. The EMITTED `memory.failure_class`. Unlike the six dispatch sites, this site
   sits on a classify-routed path, so the repair MOVES an emission rather than
   creating or withdrawing one. C-MEM-19 v1.3's coverage paragraph forbids
   withdrawing an emission by relocating a check onto an unclassified path, so
   the emission's survival is asserted on the span, on BOTH routed paths.
3. The RETRY disposition, which telemetry alone cannot see: the family BASE
   classifies to the same residual but is NOT in
   `_classify_provider_exception`'s fail-fast tuple, so a site that accidentally
   raised the base would look identical on the span while silently falling
   through to transient retry.

Reaching the branch requires a validation-bypassed construction, and that is the
POINT rather than a weakness of the witness: `MemoryToolExecutionRequest.tool_name`
is typed `MemoryToolName` on an `extra="forbid"` model, and every shipped member
has a `_prepare_*` arm, so no caller- or model-supplied input can reach the
branch. `test_every_shipped_tool_name_reaches_its_own_prepare_arm` pins that
premise - and doubles as the tripwire if a later arc adds a member without an
arm, which is the exact fault this branch guards.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, cast

import pytest
from harness_as.memory_tool_contracts import MemoryToolName
from harness_core import DeploymentSurface
from harness_is.memory_observability import MemoryTelemetryFailureClass, classify_memory_failure
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
from harness_is.memory_retrieval import MemoryRetriever
from harness_is.memory_retrieval_index import DerivedRetrievalIndexStore
from harness_is.memory_store import CanonicalMemoryStore
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_runtime import memory_tool_executor as memory_tool_executor_module
from harness_runtime.lifecycle.retry_breaker_fallback import _classify_provider_exception
from harness_runtime.memory_tool_executor import (
    MemoryToolExecutionContext,
    MemoryToolExecutionError,
    MemoryToolExecutionInputError,
    MemoryToolExecutionInternalError,
    MemoryToolExecutionRequest,
    StandardMemoryToolExecutor,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

_NOW = datetime(2026, 8, 7, 12, 0, 0, tzinfo=UTC)
_POLICY_REF = "policy:b-114"
_SCOPE_REF = "scope:b-114"
_INPUT_VALIDATION = MemoryTelemetryFailureClass.INPUT_VALIDATION_FAILURE
_PROVIDER_ADAPTER = MemoryTelemetryFailureClass.PROVIDER_ADAPTER_FAILURE


class _FutureMemoryToolName(StrEnum):
    """Stands in for a `MemoryToolName` member the executor has no arm for.

    The real enum cannot be extended at test time, and every one of its five
    members HAS an arm - which is precisely why the branch is otherwise
    unreachable. This member simulates the one fault the branch guards: a valid
    tool name that reaches `_prepare` and finds no `_prepare_*` to dispatch to.
    """

    CONSOLIDATE = "memory.consolidate"


def _scope() -> MemoryScope:
    return MemoryScope(
        project="arhugula-v2",
        workflow="memory-substrate",
        workload_class="coding-arc",
        provider_family="openai",
        cli_profile="codex",
        visibility=MemoryVisibility.WORKFLOW,
    )


def _context() -> MemoryToolExecutionContext:
    return MemoryToolExecutionContext(
        run_id="run-b-114",
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
    )


def _executor(
    tmp_path: Path,
    *,
    tracer_provider: TracerProvider | None = None,
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


def _unarmed_request() -> MemoryToolExecutionRequest:
    """A request whose `tool_name` has no `_prepare_*` arm.

    `model_construct` bypasses validation deliberately: the field's declared type
    is what makes the branch unreachable from real input, so a validated
    construction cannot express the harness-internal fault under test.
    """

    return MemoryToolExecutionRequest.model_construct(
        tool_name=cast(MemoryToolName, _FutureMemoryToolName.CONSOLIDATE),
        arguments={"query": "q", "scope_ref": _SCOPE_REF, "policy_ref": _POLICY_REF},
        context=_context(),
    )


def _tool_call_spans(exporter: InMemorySpanExporter) -> list[dict[str, Any]]:
    return [
        dict(span.attributes or {})
        for span in exporter.get_finished_spans()
        if span.name == "memory.tool_call"
    ]


# ---------------------------------------------------------------------------
# 1 + 3. The raised type at the real site, and its retry exit.
# ---------------------------------------------------------------------------


def test_the_fall_through_raises_the_internal_type_and_keeps_fail_fast(tmp_path: Path) -> None:
    """The production `_prepare` is the thing under test; only its caller stands in."""

    executor = _executor(tmp_path)

    with pytest.raises(MemoryToolExecutionInternalError) as excinfo:
        executor._prepare(_unarmed_request())

    exc = excinfo.value
    assert "unsupported memory tool" in str(exc)
    # The type boundary itself: not the input type, and not a subtype of it -
    # `getattr` walks the MRO, so an inheriting subtype would re-declare
    # `input_validation_failure` for this population.
    assert not isinstance(exc, MemoryToolExecutionInputError)
    assert classify_memory_failure(exc) is not _INPUT_VALIDATION
    # Positively, not merely "not the forbidden one": the inherited residual,
    # which C-MEM-19 v1.3 states is conforming for a harness-internal fault
    # where no dedicated unclassified value is declared.
    assert classify_memory_failure(exc) is _PROVIDER_ADAPTER
    # Retry disposition PRESERVED. `_classify_provider_exception` returns a
    # `ValidatorRetryExitClass` for RETRYABLE and `None` for fail-fast, so `is
    # None` is the assertion that the type IS in the fail-fast tuple. The base
    # would classify to the same residual above but is NOT in that tuple, which
    # is why this half cannot be inferred from the span.
    assert _classify_provider_exception(exc) is None
    assert _classify_provider_exception(MemoryToolExecutionError("x")) is not None


def test_every_shipped_tool_name_reaches_its_own_prepare_arm(tmp_path: Path) -> None:
    """Why the fall-through is unreachable, pinned rather than asserted in prose.

    Each real member is driven with EMPTY arguments: reaching its own arm means
    the arm's own argument check refuses them with the INPUT type - which is
    both the proof that the member is armed and a re-assertion that the input
    type still serves the argument-refusal population it exists for. A member
    added without an arm would raise the internal type here instead, and this
    witness would fail rather than the defect shipping silently.
    """

    executor = _executor(tmp_path)

    for tool_name in MemoryToolName:
        request = MemoryToolExecutionRequest(
            tool_name=tool_name,
            arguments={},
            context=_context(),
        )
        with pytest.raises(MemoryToolExecutionInputError):
            executor._prepare(request)


# ---------------------------------------------------------------------------
# 2. The emitted class, on both classify-routed paths.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("path", ["execute", "validate"])
def test_the_fall_through_emits_the_residual_not_input_validation_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, path: str
) -> None:
    """Both routed paths, asserted on the EMITTED span.

    `execute()`'s catch and the B-84 `validate()` pre-pass are separate emission
    sites that can regress independently. The contract-table lookup both paths
    run BEFORE `_prepare` is stood in for, because a stand-in tool name has no
    contract entry and the lookup would refuse it first; `_prepare`'s branch and
    the span the caller emits around it are still the real ones under test.
    """

    monkeypatch.setattr(
        memory_tool_executor_module,
        "memory_tool_contract",
        lambda tool: None,
    )
    exporter = InMemorySpanExporter()
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))
    executor = _executor(tmp_path, tracer_provider=tracer_provider)

    with pytest.raises(MemoryToolExecutionInternalError):
        getattr(executor, path)(_unarmed_request())

    # The emission is MOVED, not withdrawn - C-MEM-19 v1.3's coverage paragraph
    # forbids withdrawing an emission by relocating a check onto an unclassified
    # path, so the span's presence is as load-bearing as its value.
    [span] = _tool_call_spans(exporter)
    assert span["memory.failure_class"] == "provider_adapter_failure"
    assert span["memory.policy.decision"] == "failed"
