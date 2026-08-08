"""B-84 (Reading A) - the executor's side-effect-free `validate()` pre-pass.

Ratified 2026-08-05 at `.harness/class_2_fork_b84_memory_batch_partial_commit.md`
§12: the executor grows a pure `validate(request)` running exactly the checks
`_execute_authorized` runs, and BOTH provider batch pre-passes call it for every
call before any of them executes.

This module carries the witnesses §12.3 names - W-1, W-2, W-4, W-5, W-7 and W-8
in its INVERTED form - plus the §12.3 telemetry-preservation obligation, which
is MANDATORY rather than optional (dropping `memory.failure_class` for the
relocated checks would weaken `C-MEM-19` with no design-substrate change).
"""

from __future__ import annotations

import inspect
import json
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from harness_as.memory_tool_contracts import MemoryToolName
from harness_as.sandbox_tier import SandboxTier
from harness_core import DeploymentSurface
from harness_cp.cross_family_fallback_chain import ProviderFamily
from harness_cp.gate_level_rule import GateLevel
from harness_cp.memory_access_mode import MemoryAccessMode, MemoryAccessModeSelection
from harness_cp.validator_fail_taxonomy import ValidatorRetryExitClass
from harness_cp.workflow_driver_types import StepExecutionContext
from harness_is.memory_operation_ledger import (
    MemoryOperationKind,
    MemoryOperationWriteResult,
)
from harness_is.memory_path_registry import MemoryRootBinding
from harness_is.memory_policy import (
    AccessDecision,
    CaptureDecision,
    MemoryPolicyDocument,
    MemoryPolicyResolver,
    PromotionDecision,
    ReviewMode,
)
from harness_is.memory_record_envelope import MemoryID, MemoryScope, MemoryVisibility
from harness_is.memory_retrieval import (
    MemoryPacket,
    MemoryPacketAccessMode,
    MemoryRetriever,
)
from harness_is.memory_retrieval_index import DerivedRetrievalIndexStore
from harness_is.memory_store import CanonicalMemoryStore
from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier
from harness_runtime.lifecycle import llm_dispatch as llm_dispatch_module
from harness_runtime.lifecycle.retry_breaker_fallback import (
    _classify_provider_exception,  # pyright: ignore[reportPrivateUsage]
)
from harness_runtime.memory_context import RuntimeMemoryContext
from harness_runtime.memory_tool_executor import (
    MemoryToolExecutionContext,
    MemoryToolExecutionDeniedError,
    MemoryToolExecutionInputError,
    MemoryToolExecutionLedgerConflictError,
    MemoryToolExecutionRequest,
    MemoryToolExecutionStoreError,
    StandardMemoryToolExecutor,
    _PreparedPromotion,  # pyright: ignore[reportPrivateUsage]
    _PreparedRead,  # pyright: ignore[reportPrivateUsage]
    _PreparedRedaction,  # pyright: ignore[reportPrivateUsage]
    _PreparedSearch,  # pyright: ignore[reportPrivateUsage]
    _PreparedWriteNote,  # pyright: ignore[reportPrivateUsage]
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

_NOW = datetime(2026, 8, 5, 12, 0, 0, tzinfo=UTC)
_POLICY_REF = "policy:u-mem-16"
_SCOPE_REF = "scope:u-mem-16"


# ---------------------------------------------------------------------------
# Fixtures - a REAL executor over a real filesystem store, built the way
# `tests/test_memory_tool_executor.py::_executor` builds it. A fake executor
# cannot witness any of this: the checks under test ARE the executor's.
# ---------------------------------------------------------------------------


def _scope() -> MemoryScope:
    return MemoryScope(
        project="arhugula-v2",
        workflow="memory-substrate",
        workload_class="coding-arc",
        provider_family="openai",
        cli_profile="codex",
        visibility=MemoryVisibility.WORKFLOW,
    )


def _context(*, provider: str = "openai", model: str = "gpt-5") -> MemoryToolExecutionContext:
    return MemoryToolExecutionContext(
        run_id="run-b84",
        workflow_id="memory-substrate",
        workload_class="coding-arc",
        step_id="step-b84",
        provider=provider,
        model=model,
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
) -> tuple[CanonicalMemoryStore, StandardMemoryToolExecutor]:
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
    return store, StandardMemoryToolExecutor(
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


def _request(
    tool: MemoryToolName,
    arguments: Mapping[str, object],
    *,
    provider: str = "openai",
    model: str = "gpt-5",
) -> MemoryToolExecutionRequest:
    return MemoryToolExecutionRequest(
        tool_name=tool,
        arguments=dict(arguments),
        context=_context(provider=provider, model=model),
    )


def _durable_surface(tmp_path: Path) -> dict[str, bytes]:
    """Every byte the memory root holds, keyed by relative path.

    The closure witnesses assert on THIS rather than on a mock call count: a
    call-count assertion passes on a path the store never sees, which is exactly
    the failure mode W-2 exists to exclude.
    """

    root = tmp_path / "memory"
    if not root.exists():
        return {}
    return {
        str(path.relative_to(root)): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


# ---------------------------------------------------------------------------
# Dispatch-side fixtures (local copies of the shapes
# `tests/test_lifecycle_llm_dispatch.py` uses, so the two arms can be driven
# end to end without importing across test modules).
# ---------------------------------------------------------------------------


def _step_context() -> StepExecutionContext:
    return StepExecutionContext(
        workflow_id="test-wf",
        parent_action_id="workflow:test-wf:step:0",
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=Actor(actor_class=ActorClass.AGENT, actor_id="codex"),
        parent_entry_hash="",
        parent_idempotency_key="b84-step-key",
        tenant_id=None,
        step_index=0,
    )


def _memory_context(*, provider: str, family: ProviderFamily) -> RuntimeMemoryContext:
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
        run_id="run-b84",
        access_mode=MemoryAccessMode.STANDARD_MEMORY_TOOLS,
        selection=MemoryAccessModeSelection(
            access_mode=MemoryAccessMode.STANDARD_MEMORY_TOOLS,
            selected_provider=provider,
            selected_model="gpt-5",
            selected_family=family,
            fallback_primary=f"{provider}:gpt-5",
            cli_profile_ref="codex",
            decision_trace=("standard_tools_policy_allowed",),
        ),
        policy_ref=_POLICY_REF,
        selected_refs=(),
        packet=packet,
        packet_hash=packet.packet_hash,
        retrieval_request_hash="d" * 64,
        # The executor's own `_context()` scope, so a dispatch-composed request
        # and a hand-built one are the same request.
        record_scope=_scope(),
        scope_ref=_SCOPE_REF,
        external_cli_route_ref=None,
        denial_reason=None,
        ledgerable_denial=False,
        injection_action_id=Identifier("memory-injection:cccccccccccccccccccccccccccccccc"),
        injection_operation_result=MemoryOperationWriteResult.APPENDED,
    )


def _openai_call(tool: MemoryToolName, **arguments: Any) -> dict[str, Any]:
    return {
        "id": f"call_{tool.name.lower()}",
        "type": "function",
        "function": {
            "name": llm_dispatch_module._OPENAI_MEMORY_TOOL_WIRE_NAMES[tool],  # pyright: ignore[reportPrivateUsage]
            "arguments": json.dumps(arguments, sort_keys=True),
        },
    }


def _ollama_call(tool: MemoryToolName, **arguments: Any) -> dict[str, Any]:
    return {"function": {"name": tool.value, "arguments": arguments}}


def _openai_prepare(calls: Sequence[Mapping[str, Any]], executor: Any) -> tuple[Any, ...]:
    return llm_dispatch_module._openai_prepared_memory_tool_calls(  # pyright: ignore[reportPrivateUsage]
        calls,
        memory_context=_memory_context(provider="openai", family=ProviderFamily.OPENAI),
        step_context=_step_context(),
        step_id="step-b84",
        model="gpt-5",
        standard_memory_tool_executor=executor,
    )


def _ollama_prepare(calls: Sequence[Mapping[str, Any]], executor: Any) -> tuple[Any, ...]:
    return llm_dispatch_module._ollama_prepared_memory_tool_calls(  # pyright: ignore[reportPrivateUsage]
        calls,
        # `provider_family` on the record scope stays `openai` on purpose: the
        # scope is the RECORD's, and reusing the executor fixture's scope keeps
        # the two arms comparing the same request.
        memory_context=_memory_context(provider="ollama", family=ProviderFamily.OPENAI),
        step_context=_step_context(),
        step_id="step-b84",
        model="gpt-5",
        standard_memory_tool_executor=executor,
    )


_ARMS = (
    pytest.param(
        _openai_call,
        _openai_prepare,
        llm_dispatch_module._openai_memory_tool_result_messages,  # pyright: ignore[reportPrivateUsage]
        id="openai",
    ),
    pytest.param(
        _ollama_call,
        _ollama_prepare,
        llm_dispatch_module._ollama_memory_tool_result_messages,  # pyright: ignore[reportPrivateUsage]
        id="ollama",
    ),
)

_ArmCall = Callable[..., dict[str, Any]]
_ArmPrepare = Callable[[Sequence[Mapping[str, Any]], Any], tuple[Any, ...]]
_ArmExecute = Callable[..., list[dict[str, Any]]]


def _partial_commit_batch(make_call: _ArmCall) -> list[dict[str, Any]]:
    """`[write_note (valid), read (no `memory_ref`)]` - the ratified harm shape.

    Call 1 commits durable memory state; call 2 is dispatch-VALID (it resolves,
    its arguments decode, it declares no `scope_ref`) and executor-INVALID, so
    before B-84 nothing could see it until call 1 had already landed.
    """

    return [
        make_call(
            MemoryToolName.WRITE_NOTE,
            note="A durable note that must not survive its batch-mate's failure.",
            scope_ref=_SCOPE_REF,
            policy_ref=_POLICY_REF,
        ),
        make_call(MemoryToolName.READ, policy_ref=_POLICY_REF),
    ]


# ---------------------------------------------------------------------------
# W-1 - the harm, made visible, and the fix flipping it.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("make_call", "prepare", "run_batch"), _ARMS)
def test_w1_unvalidated_batch_still_partial_commits_pre_fix_baseline(
    tmp_path: Path,
    make_call: _ArmCall,
    prepare: _ArmPrepare,
    run_batch: _ArmExecute,
) -> None:
    """W-1, the PRE-FIX baseline, retained as a counterfactual.

    The pre-B-84 shape is the batch loop reached WITHOUT the `validate()`
    pre-pass. Driving `_*_memory_tool_result_messages` over a batch prepared
    against a non-validating executor reproduces it exactly: call 1's write
    commits, call 2 raises, and the durable surface has changed.

    This is the assertion the fix INVERTS (codex R9 [P2-a]) - it is evidence
    that the harm is real and that `validate()` is what removes it, not a final
    acceptance criterion. Without it the closure witnesses below could pass
    vacuously against a batch that never had a durable effect to prevent.
    """

    class _NonValidatingExecutor:
        """The executor with `validate` disabled - i.e. the pre-B-84 pre-pass."""

        def __init__(self, inner: StandardMemoryToolExecutor) -> None:
            self._inner = inner

        def validate(self, request: MemoryToolExecutionRequest) -> None:
            return None

        def execute(self, request: MemoryToolExecutionRequest) -> dict[str, object]:
            return self._inner.execute(request)

    store, executor = _executor(tmp_path)
    unvalidating = _NonValidatingExecutor(executor)
    before = _durable_surface(tmp_path)

    prepared = prepare(_partial_commit_batch(make_call), unvalidating)

    with pytest.raises(MemoryToolExecutionInputError, match="memory_ref"):
        run_batch(prepared, standard_memory_tool_executor=unvalidating)

    after = _durable_surface(tmp_path)
    assert after != before, "the pre-fix baseline must show a partial commit"
    kinds = [entry.operation_kind for entry in store.read_memory_operations()]
    assert MemoryOperationKind.CAPTURE in kinds, (
        "call 1's write_note capture must have landed before call 2 raised"
    )
    assert MemoryOperationKind.STANDARD_TOOL_CALL in kinds


@pytest.mark.parametrize(("make_call", "prepare", "run_batch"), _ARMS)
def test_w2_validate_prepass_refuses_the_batch_before_any_durable_write(
    tmp_path: Path,
    make_call: _ArmCall,
    prepare: _ArmPrepare,
    run_batch: _ArmExecute,
) -> None:
    """W-2 - A's closure, parameterized over BOTH provider arms.

    The same batch, with the real executor (so `validate()` runs): preparation
    raises call 2's error, `run_batch` is never reached, and the durable surface
    is BYTE-IDENTICAL to its pre-batch state. Asserted on the store's own bytes
    rather than on a call count - a count assertion passes on a path the store
    never sees.

    Parameterized because the two pre-passes are separate code paths: an
    OpenAI-only witness stays green when only the ollama `validate()` call is
    removed.
    """

    store, executor = _executor(tmp_path)
    before = _durable_surface(tmp_path)

    with pytest.raises(MemoryToolExecutionInputError, match="memory_ref"):
        prepared = prepare(_partial_commit_batch(make_call), executor)
        run_batch(prepared, standard_memory_tool_executor=executor)

    assert _durable_surface(tmp_path) == before
    assert list(store.read_memory_operations()) == []


@pytest.mark.parametrize(("make_call", "prepare", "run_batch"), _ARMS)
def test_w2_a_wholly_valid_batch_still_executes(
    tmp_path: Path,
    make_call: _ArmCall,
    prepare: _ArmPrepare,
    run_batch: _ArmExecute,
) -> None:
    """W-2's positive control - `validate()` refuses the invalid, not the valid.

    Without this arm a `validate()` that raised unconditionally would satisfy
    every closure assertion above.
    """

    store, executor = _executor(tmp_path)
    # `search` first: a `write_note` invalidates the derived retrieval index, so
    # the reverse order fails on index staleness rather than on anything B-84
    # governs. The batch still carries one read-like and one write-like call.
    batch = [
        make_call(
            MemoryToolName.SEARCH,
            query="codex memory tools",
            scope_ref=_SCOPE_REF,
            policy_ref=_POLICY_REF,
            limit=5,
        ),
        make_call(
            MemoryToolName.WRITE_NOTE,
            note="A valid note in a wholly valid batch.",
            scope_ref=_SCOPE_REF,
            policy_ref=_POLICY_REF,
        ),
    ]

    messages = run_batch(prepare(batch, executor), standard_memory_tool_executor=executor)

    assert len(messages) == 2
    kinds = [entry.operation_kind for entry in store.read_memory_operations()]
    assert kinds.count(MemoryOperationKind.STANDARD_TOOL_CALL) == 2


# ---------------------------------------------------------------------------
# W-4 - the parity pin.
# ---------------------------------------------------------------------------

_SEED = "<seed>"

#: (tool, arguments, expected exception class, message fragment).
#:
#: The coverage unit is (tool x ARGUMENT x branch), not raise sites: a single
#: helper (`_string_arg`) serves many fields, so a `validate()` could reach every
#: raise statement while omitting a whole field's path (codex R2 [P2-a]).
_ARGUMENT_MATRIX: tuple[
    tuple[str, MemoryToolName, dict[str, object], type[Exception], str], ...
] = (
    # memory.search
    (
        "search/policy_ref/absent",
        MemoryToolName.SEARCH,
        {"query": "q", "scope_ref": _SCOPE_REF},
        MemoryToolExecutionInputError,
        "policy_ref",
    ),
    (
        "search/policy_ref/mismatch",
        MemoryToolName.SEARCH,
        {"query": "q", "scope_ref": _SCOPE_REF, "policy_ref": "policy:other"},
        MemoryToolExecutionDeniedError,
        "policy_ref does not match",
    ),
    (
        "search/scope_ref/mismatch",
        MemoryToolName.SEARCH,
        {"query": "q", "scope_ref": "scope:other", "policy_ref": _POLICY_REF},
        MemoryToolExecutionDeniedError,
        "scope_ref does not match",
    ),
    (
        "search/query/absent",
        MemoryToolName.SEARCH,
        {"scope_ref": _SCOPE_REF, "policy_ref": _POLICY_REF},
        MemoryToolExecutionInputError,
        "query",
    ),
    (
        "search/query/wrong-type",
        MemoryToolName.SEARCH,
        {"query": 7, "scope_ref": _SCOPE_REF, "policy_ref": _POLICY_REF},
        MemoryToolExecutionInputError,
        "query",
    ),
    (
        "search/allowed_kinds/not-a-sequence",
        MemoryToolName.SEARCH,
        {
            "query": "q",
            "scope_ref": _SCOPE_REF,
            "policy_ref": _POLICY_REF,
            "allowed_kinds": "preference",
        },
        MemoryToolExecutionInputError,
        "allowed_kinds must be a sequence",
    ),
    (
        "search/allowed_kinds/entry-not-a-string",
        MemoryToolName.SEARCH,
        {"query": "q", "scope_ref": _SCOPE_REF, "policy_ref": _POLICY_REF, "allowed_kinds": [3]},
        MemoryToolExecutionInputError,
        "entries must be strings",
    ),
    (
        "search/allowed_kinds/unknown-value",
        MemoryToolName.SEARCH,
        {
            "query": "q",
            "scope_ref": _SCOPE_REF,
            "policy_ref": _POLICY_REF,
            "allowed_kinds": ["not_a_kind"],
        },
        MemoryToolExecutionInputError,
        "not_a_kind",
    ),
    (
        "search/limit/wrong-type",
        MemoryToolName.SEARCH,
        {"query": "q", "scope_ref": _SCOPE_REF, "policy_ref": _POLICY_REF, "limit": "ten"},
        MemoryToolExecutionInputError,
        "limit",
    ),
    (
        "search/limit/zero",
        MemoryToolName.SEARCH,
        {"query": "q", "scope_ref": _SCOPE_REF, "policy_ref": _POLICY_REF, "limit": 0},
        MemoryToolExecutionInputError,
        "limit",
    ),
    # memory.read
    (
        "read/policy_ref/mismatch",
        MemoryToolName.READ,
        {"memory_ref": _SEED, "policy_ref": "policy:other"},
        MemoryToolExecutionDeniedError,
        "policy_ref does not match",
    ),
    (
        "read/memory_ref/absent",
        MemoryToolName.READ,
        {"policy_ref": _POLICY_REF},
        MemoryToolExecutionInputError,
        "memory_ref",
    ),
    (
        "read/memory_ref/wrong-type",
        MemoryToolName.READ,
        {"memory_ref": 5, "policy_ref": _POLICY_REF},
        MemoryToolExecutionInputError,
        "memory_ref",
    ),
    (
        "read/packet_section_ref/wrong-type",
        MemoryToolName.READ,
        {"memory_ref": _SEED, "packet_section_ref": 5, "policy_ref": _POLICY_REF},
        MemoryToolExecutionInputError,
        "packet_section_ref",
    ),
    # memory.write_note
    (
        "write_note/policy_ref/mismatch",
        MemoryToolName.WRITE_NOTE,
        {"note": "n", "scope_ref": _SCOPE_REF, "policy_ref": "policy:other"},
        MemoryToolExecutionDeniedError,
        "policy_ref does not match",
    ),
    (
        "write_note/scope_ref/mismatch",
        MemoryToolName.WRITE_NOTE,
        {"note": "n", "scope_ref": "scope:other", "policy_ref": _POLICY_REF},
        MemoryToolExecutionDeniedError,
        "scope_ref does not match",
    ),
    (
        "write_note/note/absent",
        MemoryToolName.WRITE_NOTE,
        {"scope_ref": _SCOPE_REF, "policy_ref": _POLICY_REF},
        MemoryToolExecutionInputError,
        "note",
    ),
    (
        "write_note/note/empty",
        MemoryToolName.WRITE_NOTE,
        {"note": "", "scope_ref": _SCOPE_REF, "policy_ref": _POLICY_REF},
        MemoryToolExecutionInputError,
        "note",
    ),
    (
        "write_note/idempotency_key/wrong-type",
        MemoryToolName.WRITE_NOTE,
        {"note": "n", "scope_ref": _SCOPE_REF, "policy_ref": _POLICY_REF, "idempotency_key": 17},
        MemoryToolExecutionInputError,
        "idempotency_key",
    ),
    # memory.propose_promotion
    (
        "propose_promotion/policy_ref/mismatch",
        MemoryToolName.PROPOSE_PROMOTION,
        {"memory_ref": _SEED, "target_kind": "convention", "policy_ref": "policy:other"},
        MemoryToolExecutionDeniedError,
        "policy_ref does not match",
    ),
    (
        "propose_promotion/memory_ref/absent",
        MemoryToolName.PROPOSE_PROMOTION,
        {"target_kind": "convention", "policy_ref": _POLICY_REF},
        MemoryToolExecutionInputError,
        "memory_ref",
    ),
    (
        "propose_promotion/memory_ref/bad-grammar",
        MemoryToolName.PROPOSE_PROMOTION,
        {"memory_ref": "not-a-memory-ref", "target_kind": "convention", "policy_ref": _POLICY_REF},
        MemoryToolExecutionInputError,
        "invalid memory_ref",
    ),
    (
        "propose_promotion/memory_ref/unknown-kind",
        MemoryToolName.PROPOSE_PROMOTION,
        {
            "memory_ref": "mem:semantic:not_a_kind:" + ("a" * 64),
            "target_kind": "convention",
            "policy_ref": _POLICY_REF,
        },
        MemoryToolExecutionInputError,
        "unknown memory kind",
    ),
    (
        "propose_promotion/target_kind/absent",
        MemoryToolName.PROPOSE_PROMOTION,
        {"memory_ref": _SEED, "policy_ref": _POLICY_REF},
        MemoryToolExecutionInputError,
        "target_kind",
    ),
    (
        "propose_promotion/target_kind/unsupported",
        MemoryToolName.PROPOSE_PROMOTION,
        {"memory_ref": _SEED, "target_kind": "not_a_kind", "policy_ref": _POLICY_REF},
        MemoryToolExecutionInputError,
        "not_a_kind",
    ),
    (
        "propose_promotion/evidence_ref/wrong-type",
        MemoryToolName.PROPOSE_PROMOTION,
        {
            "memory_ref": _SEED,
            "target_kind": "convention",
            "evidence_ref": 9,
            "policy_ref": _POLICY_REF,
        },
        MemoryToolExecutionInputError,
        "evidence_ref",
    ),
    # memory.request_redaction
    (
        "request_redaction/policy_ref/mismatch",
        MemoryToolName.REQUEST_REDACTION,
        {"memory_ref": _SEED, "reason": "r", "policy_ref": "policy:other"},
        MemoryToolExecutionDeniedError,
        "policy_ref does not match",
    ),
    (
        "request_redaction/memory_ref/absent",
        MemoryToolName.REQUEST_REDACTION,
        {"reason": "r", "policy_ref": _POLICY_REF},
        MemoryToolExecutionInputError,
        "memory_ref",
    ),
    (
        "request_redaction/memory_ref/bad-grammar",
        MemoryToolName.REQUEST_REDACTION,
        {"memory_ref": "nope", "reason": "r", "policy_ref": _POLICY_REF},
        MemoryToolExecutionInputError,
        "invalid memory_ref",
    ),
    (
        "request_redaction/reason/absent",
        MemoryToolName.REQUEST_REDACTION,
        {"memory_ref": _SEED, "policy_ref": _POLICY_REF},
        MemoryToolExecutionInputError,
        "reason",
    ),
)


def _seeded(arguments: Mapping[str, object]) -> dict[str, object]:
    resolved = dict(arguments)
    if resolved.get("memory_ref") == _SEED:
        resolved["memory_ref"] = "mem:episodic:tool_event:" + ("a" * 64)
    return resolved


@pytest.mark.parametrize(
    ("case", "tool", "arguments", "expected", "fragment"),
    [pytest.param(*row, id=row[0]) for row in _ARGUMENT_MATRIX],
)
def test_w4_validate_and_execute_agree_on_every_argument_branch(
    tmp_path: Path,
    case: str,
    tool: MemoryToolName,
    arguments: dict[str, object],
    expected: type[Exception],
    fragment: str,
) -> None:
    """W-4 - the parity pin, over the (tool x argument x branch) matrix.

    The STRUCTURAL half of the discharge is that parity cannot be broken:
    `validate()` and `_execute_authorized` both obtain their checks by calling
    the same `_prepare`, and every tool body takes its prepared value as a
    REQUIRED parameter, so a body cannot run unprepared and a new check cannot
    land on one path only (asserted directly by the two structural witnesses
    below). This matrix is the behavioural half: for every argument branch, the
    two surfaces raise the SAME class with the SAME message, and `validate()`
    leaves the durable surface untouched while doing it.
    """

    _store, executor = _executor(tmp_path)
    request = _request(tool, _seeded(arguments))
    before = _durable_surface(tmp_path)

    with pytest.raises(expected) as validate_exc:
        executor.validate(request)
    assert fragment in str(validate_exc.value), case
    assert _durable_surface(tmp_path) == before, f"{case}: validate() touched the durable surface"

    with pytest.raises(expected) as execute_exc:
        executor.execute(request)
    assert fragment in str(execute_exc.value), case

    assert type(validate_exc.value) is type(execute_exc.value), case
    assert str(validate_exc.value) == str(execute_exc.value), case


def test_w4_prepare_is_total_over_the_tool_enum(tmp_path: Path) -> None:
    """W-4 structural half (1) - `_prepare` answers for EVERY `MemoryToolName`.

    `_execute_authorized` dispatches on the TYPE of `_prepare`'s result, so a
    tool `_prepare` does not answer for cannot execute at all. Totality is
    therefore what keeps the two paths in step, and it is asserted rather than
    assumed.
    """

    _store, executor = _executor(tmp_path)
    valid: dict[MemoryToolName, dict[str, object]] = {
        MemoryToolName.SEARCH: {
            "query": "q",
            "scope_ref": _SCOPE_REF,
            "policy_ref": _POLICY_REF,
        },
        MemoryToolName.READ: {"memory_ref": _SEED, "policy_ref": _POLICY_REF},
        MemoryToolName.WRITE_NOTE: {
            "note": "n",
            "scope_ref": _SCOPE_REF,
            "policy_ref": _POLICY_REF,
        },
        MemoryToolName.PROPOSE_PROMOTION: {
            "memory_ref": _SEED,
            "target_kind": "convention",
            "policy_ref": _POLICY_REF,
        },
        MemoryToolName.REQUEST_REDACTION: {
            "memory_ref": _SEED,
            "reason": "r",
            "policy_ref": _POLICY_REF,
        },
    }
    expected_types = {
        MemoryToolName.SEARCH: _PreparedSearch,
        MemoryToolName.READ: _PreparedRead,
        MemoryToolName.WRITE_NOTE: _PreparedWriteNote,
        MemoryToolName.PROPOSE_PROMOTION: _PreparedPromotion,
        MemoryToolName.REQUEST_REDACTION: _PreparedRedaction,
    }
    assert set(valid) == set(MemoryToolName), "a new tool must join this matrix"

    before = _durable_surface(tmp_path)
    for tool, arguments in valid.items():
        prepared = executor._prepare(_request(tool, _seeded(arguments)))  # pyright: ignore[reportPrivateUsage]
        assert isinstance(prepared, expected_types[tool]), tool
    assert _durable_surface(tmp_path) == before, (
        "a full sweep of `_prepare` over every tool must leave the store untouched"
    )


def test_w4_every_tool_body_requires_its_prepared_arguments() -> None:
    """W-4 structural half (2) - no tool body can run without being prepared.

    This is what makes parity unfalsifiable by construction rather than pinned
    by an enumeration a new argument could outgrow: the prepared value is a
    REQUIRED positional parameter of each body, and `_prepare` is its only
    producer, so `_execute_authorized` cannot reach a body without having run
    exactly the checks `validate()` runs.
    """

    bodies = {
        "_search": _PreparedSearch,
        "_read": _PreparedRead,
        "_write_note": _PreparedWriteNote,
        "_propose_promotion": _PreparedPromotion,
        "_request_redaction": _PreparedRedaction,
    }
    for name, prepared_type in bodies.items():
        signature = inspect.signature(getattr(StandardMemoryToolExecutor, name))
        parameters = list(signature.parameters.values())
        assert [p.name for p in parameters] == ["self", "request", "prepared"], name
        assert parameters[2].default is inspect.Parameter.empty, name
        assert parameters[2].annotation == prepared_type.__name__, name


# ---------------------------------------------------------------------------
# W-7 - A changes failure PRECEDENCE, and therefore retry disposition.
# ---------------------------------------------------------------------------


def _retry_precedence_batch(make_call: _ArmCall) -> list[dict[str, Any]]:
    """`[denied call, malformed call]`.

    Call 1 is a `request_redaction` whose `memory_ref` is well-formed (so it
    survives every argument check) but absent from the store, which
    `_read_record_by_ref` wraps into `MemoryToolExecutionDeniedError` - the
    class deliberately kept RETRYABLE because that site also wraps genuinely
    transient I/O. Call 2 is executor-invalid.
    """

    return [
        make_call(
            MemoryToolName.REQUEST_REDACTION,
            memory_ref="mem:episodic:tool_event:" + ("f" * 64),
            reason="operator requested review",
            policy_ref=_POLICY_REF,
        ),
        make_call(
            MemoryToolName.SEARCH,
            query="codex memory",
            scope_ref=_SCOPE_REF,
            policy_ref=_POLICY_REF,
            limit=0,
        ),
    ]


@pytest.mark.parametrize(("make_call", "prepare", "run_batch"), _ARMS)
def test_w7_validate_prepass_changes_which_failure_surfaces_and_its_retry_class(
    tmp_path: Path,
    make_call: _ArmCall,
    prepare: _ArmPrepare,
    run_batch: _ArmExecute,
) -> None:
    """W-7 - A's retry-precedence change, pinned in a test rather than found in
    production.

    BEFORE: the batch stops at call 1 with `MemoryToolExecutionDeniedError`,
    which `_classify_provider_exception` maps to `TRANSIENT_RETRY` - the
    dispatch retries. AFTER: the pre-pass raises call 2's
    `MemoryToolExecutionInputError` first, which is fail-fast (`None`), so that
    retry is SUPPRESSED. The batch was malformed either way; the point is that
    Reading A OWNS this change.
    """

    class _NonValidatingExecutor:
        def __init__(self, inner: StandardMemoryToolExecutor) -> None:
            self._inner = inner

        def validate(self, request: MemoryToolExecutionRequest) -> None:
            return None

        def execute(self, request: MemoryToolExecutionRequest) -> dict[str, object]:
            return self._inner.execute(request)

    _store, executor = _executor(tmp_path)
    batch = _retry_precedence_batch(make_call)

    unvalidating = _NonValidatingExecutor(executor)
    with pytest.raises(MemoryToolExecutionDeniedError) as before_exc:
        run_batch(
            prepare(batch, unvalidating),
            standard_memory_tool_executor=unvalidating,
        )
    assert _classify_provider_exception(before_exc.value) is ValidatorRetryExitClass.TRANSIENT_RETRY

    with pytest.raises(MemoryToolExecutionInputError) as after_exc:
        prepare(batch, executor)
    assert "limit" in str(after_exc.value)
    assert _classify_provider_exception(after_exc.value) is None


# ---------------------------------------------------------------------------
# W-8 (INVERTED) - the single-call read-only `memory.search` partial commit.
# ---------------------------------------------------------------------------


def test_w8_single_call_search_with_limit_zero_commits_nothing(tmp_path: Path) -> None:
    """W-8 in its INVERTED form (§12.3) - `limit=0` is rejected BEFORE retrieval.

    §3(vii): `_search` used to call `self._retriever.retrieve(...)` - which
    appends a durable retrieval event by contract - and only afterwards validate
    `limit`, so a single-call, read-only `memory.search` with a valid `query`
    and `limit=0` committed a durable operation and then raised. Under Reading A
    the check is part of `_prepare_search`, which runs first, so nothing is
    committed.

    Asserted through BOTH surfaces the ratified reading reaches: the dispatch
    pre-pass (where `validate()` runs) AND a direct `execute()` (where the same
    `_prepare` runs ahead of the retrieval). A witness that only covered the
    first would leave the direct-call ordering unpinned.
    """

    store, executor = _executor(tmp_path)
    arguments = {
        "query": "codex memory tools",
        "scope_ref": _SCOPE_REF,
        "policy_ref": _POLICY_REF,
        "limit": 0,
    }
    before = _durable_surface(tmp_path)

    with pytest.raises(MemoryToolExecutionInputError, match="limit"):
        executor.validate(_request(MemoryToolName.SEARCH, arguments))
    assert _durable_surface(tmp_path) == before

    with pytest.raises(MemoryToolExecutionInputError, match="limit"):
        executor.execute(_request(MemoryToolName.SEARCH, arguments))
    assert _durable_surface(tmp_path) == before
    assert list(store.read_memory_operations()) == []


def test_w8_positive_control_a_valid_search_does_append_a_retrieval_event(
    tmp_path: Path,
) -> None:
    """W-8's discriminator - the absence above is the FIX, not an inert path.

    The very same call with a valid `limit` DOES append a `RETRIEVE` operation,
    so the assertion that `limit=0` appends none is load-bearing rather than a
    statement about a retriever that never writes.
    """

    store, executor = _executor(tmp_path)
    executor.execute(
        _request(
            MemoryToolName.SEARCH,
            {
                "query": "codex memory tools",
                "scope_ref": _SCOPE_REF,
                "policy_ref": _POLICY_REF,
                "limit": 1,
            },
        )
    )

    kinds = [entry.operation_kind for entry in store.read_memory_operations()]
    assert MemoryOperationKind.RETRIEVE in kinds


# ---------------------------------------------------------------------------
# §12.3 telemetry obligation - `C-MEM-19`'s `memory.failure_class` must survive
# the relocation of a check off `execute()`'s catch.
# ---------------------------------------------------------------------------


def _spans(exporter: InMemorySpanExporter) -> list[dict[str, Any]]:
    return [
        dict(span.attributes or {})
        for span in exporter.get_finished_spans()
        if span.name == "memory.tool_call"
    ]


@pytest.mark.parametrize(
    ("arguments", "expected", "failure_class", "decision"),
    [
        pytest.param(
            {"query": "q", "scope_ref": _SCOPE_REF, "policy_ref": _POLICY_REF, "limit": 0},
            MemoryToolExecutionInputError,
            # U-MEM-28: was `provider_adapter_failure`, the B-88 impl half's
            # least-wrong stopgap. Memory spec v1.3 gives the class its own
            # value and this type is the single declaration flip site. The
            # PRESERVATION property this row exists for is unchanged - the
            # relocated check still emits `memory.failure_class`, and
            # `validate()` still classifies exactly as `execute()` would.
            "input_validation_failure",
            "failed",
            id="input-error",
        ),
        pytest.param(
            {"query": "q", "scope_ref": "scope:other", "policy_ref": _POLICY_REF},
            MemoryToolExecutionDeniedError,
            "policy_denial",
            "denied",
            id="policy-denial",
        ),
    ],
)
def test_validate_preserves_the_c_mem_19_failure_class_emission(
    tmp_path: Path,
    arguments: dict[str, object],
    expected: type[Exception],
    failure_class: str,
    decision: str,
) -> None:
    """§12.3, MANDATORY - a relocated check still emits `memory.failure_class`.

    The checks the pre-pass moves ahead of `execute()` were classified by
    `execute()`'s own catch (`classify_memory_failure`). Raising them from a
    dispatch pre-pass instead would have DROPPED that emission for exactly the
    population B-84 relocates - a `C-MEM-19` weakening no impl leg may elect on
    its own authority. `validate()` therefore emits the same
    `memory.tool_call` span, with the same attributes, and this asserts parity
    against what `execute()` emits for the identical request.
    """

    exporter = InMemorySpanExporter()
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))
    _store, executor = _executor(tmp_path, tracer_provider=tracer_provider)
    request = _request(MemoryToolName.SEARCH, arguments)

    with pytest.raises(expected):
        executor.validate(request)
    [validated] = _spans(exporter)
    assert validated["memory.failure_class"] == failure_class
    assert validated["memory.policy.decision"] == decision
    assert validated["memory.operation.name"] == "standard_tool_call"
    assert validated["memory.tool.name"] == MemoryToolName.SEARCH.value

    exporter.clear()
    with pytest.raises(expected):
        executor.execute(request)
    [executed] = _spans(exporter)
    assert executed == validated, "validate() must classify exactly as execute() would"


def test_validate_emits_no_span_when_the_call_is_valid(tmp_path: Path) -> None:
    """The success path stays silent - `execute()` emits that call's span.

    A `validate()` that also emitted on success would double-count every
    standard tool call in the `C-MEM-19` telemetry, which is a different
    corruption of the same contract.
    """

    exporter = InMemorySpanExporter()
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))
    _store, executor = _executor(tmp_path, tracer_provider=tracer_provider)

    executor.validate(
        _request(
            MemoryToolName.SEARCH,
            {"query": "q", "scope_ref": _SCOPE_REF, "policy_ref": _POLICY_REF, "limit": 1},
        )
    )

    assert _spans(exporter) == []


# ---------------------------------------------------------------------------
# W-5 - §3(iv)'s FOUR-CELL cross-candidate replay matrix, EXECUTED.
# ---------------------------------------------------------------------------

_NOTE = "A note replayed across fallback candidates."


def _write_note(
    executor: StandardMemoryToolExecutor,
    *,
    note: str = _NOTE,
    provider: str = "openai",
    model: str = "gpt-5",
    idempotency_key: str = "note:b84",
) -> dict[str, object]:
    return executor.execute(
        _request(
            MemoryToolName.WRITE_NOTE,
            {
                "note": note,
                "scope_ref": _SCOPE_REF,
                "policy_ref": _POLICY_REF,
                "idempotency_key": idempotency_key,
            },
            provider=provider,
            model=model,
        )
    )


def _tool_event_lines(tmp_path: Path, memory_ref: str) -> int:
    """Physical lines in the EPISODIC tool-events JSONL carrying `memory_ref`.

    Scoped to `episodic/**/tool_events.jsonl` deliberately: the ref also appears
    in the operation ledger and the derived index, and counting those would
    conflate the record-duplication question W-5 asks with the ledger's own
    idempotency answer, which the cells assert separately.
    """

    root = tmp_path / "memory" / "episodic"
    if not root.exists():
        return 0
    return sum(
        1
        for path in root.rglob("tool_events.jsonl")
        for line in path.read_text(encoding="utf-8").splitlines()
        if memory_ref in line
    )


def test_w5_case_1_resampled_text_yields_a_second_distinct_note(tmp_path: Path) -> None:
    """W-5 cell (1) - different text -> different `memory_id`, `APPENDED`.

    The ordinary cross-candidate case: sampling is stochastic, so the replay is
    not a duplicate at all but an EXTRA, distinct note the operator never asked
    for. That is the honest statement of the duplication harm.
    """

    store, executor = _executor(tmp_path)
    first = str(_write_note(executor)["memory_ref"])
    second = str(_write_note(executor, note="A DIFFERENT note after re-sampling.")["memory_ref"])

    assert first != second
    assert _tool_event_lines(tmp_path, first) == 1
    assert _tool_event_lines(tmp_path, second) == 1
    captures = [
        entry
        for entry in store.read_memory_operations()
        if entry.operation_kind is MemoryOperationKind.CAPTURE
    ]
    assert len(captures) == 2


def test_w5_case_2_same_text_different_model_yields_a_second_distinct_note(
    tmp_path: Path,
) -> None:
    """W-5 cell (2) - same text, different MODEL -> different `memory_id`.

    The ordinary FALLBACK shape (a chain advances to another model).
    `summary_model` participates in the hashed content, so the identity differs
    and the append is an ordinary one: again an extra distinct note, not a
    duplicate.
    """

    _store, executor = _executor(tmp_path)
    first = str(_write_note(executor, model="gpt-5")["memory_ref"])
    second = str(_write_note(executor, model="gpt-5-mini")["memory_ref"])

    assert first != second
    assert _tool_event_lines(tmp_path, first) == 1
    assert _tool_event_lines(tmp_path, second) == 1


def test_w5_case_3_same_model_name_different_provider_raises_a_ledger_conflict(
    tmp_path: Path,
) -> None:
    """W-5 cell (3), the ONLY cell carrying the duplicate-line + re-opened-
    staircase claim - EXECUTED rather than inferred.

    Same text, same model NAME, different PROVIDER: the content hash is
    unchanged (provider is not hashed) so the `memory_id` collides, the record
    line is appended a second time, and then the ledger's 18-field equivalence
    payload DIFFERS on `provider` - so `append_memory_operation` raises.

    INVERTED at `B-115` (b′), and the inversion is the whole point of that leg.
    The refusal used to be folded into a `FAILED` capture result and re-raised
    as `MemoryToolExecutionStoreError`, which is NOT in the fail-fast tuple and
    so classified `TRANSIENT_RETRY` - the measured re-enterability that answered
    `B-84`'s D-2 falsifier affirmatively. It now propagates out of the capture
    layer and is re-typed to `MemoryToolExecutionLedgerConflictError`, which IS
    admitted to fail-fast BY NAME. The staircase is therefore closed to this
    class: the assertion below flipped from `TRANSIENT_RETRY` to `None`.

    The duplicate-line assertion is PRESERVED VERBATIM and deliberately so.
    `B-115` (b′) addressed the STAIRCASE half, not the duplicate-record half -
    `write_record` still appends before the ledger append is attempted, so the
    second physical line still lands. Weakening this assertion would silently
    claim a closure the leg did not deliver. What the leg DID change is that
    the line is now appended ONCE rather than once per retry attempt, which is
    witnessed separately at `test_b115_ledger_conflict_split.py`.
    """

    _store, executor = _executor(tmp_path)
    first = str(_write_note(executor, provider="openai")["memory_ref"])

    with pytest.raises(MemoryToolExecutionLedgerConflictError) as exc:
        _write_note(executor, provider="azure-openai")

    assert _tool_event_lines(tmp_path, first) == 2, (
        "the record line is appended before the ledger append raises"
    )
    assert _classify_provider_exception(exc.value) is None, (
        "the ledger-conflict class fail-fasts; it must not re-enter the staircase"
    )
    # The store subtype it split OFF keeps its transient disposition - the
    # counterfactual that makes the flip above a SPLIT rather than a wholesale
    # reclassification of the memory family.
    assert (
        _classify_provider_exception(MemoryToolExecutionStoreError("OSError: disk full"))
        is ValidatorRetryExitClass.TRANSIENT_RETRY
    )


def test_w5_case_3_collapses_into_case_1_when_the_idempotency_key_is_resampled(
    tmp_path: Path,
) -> None:
    """W-5's FIFTH dimension - `idempotency_key` is not a constant.

    It feeds `_tool_event_id`, whose value lands in the hashed content, so a
    re-sampled key gives a different `memory_id` and an ordinary append: cell
    (3) collapses into cell (1). The four cells are exhaustive only under
    "identical everything-but-the-named-variable".
    """

    _store, executor = _executor(tmp_path)
    first = str(_write_note(executor, provider="openai", idempotency_key="note:a")["memory_ref"])
    second = str(
        _write_note(executor, provider="azure-openai", idempotency_key="note:b")["memory_ref"]
    )

    assert first != second
    assert _tool_event_lines(tmp_path, first) == 1
    assert _tool_event_lines(tmp_path, second) == 1


def test_w5_case_4_fully_identical_replay_is_an_idempotent_noop_with_a_duplicate_line(
    tmp_path: Path,
) -> None:
    """W-5 cell (4) - fully identical -> duplicate physical line, no raise.

    The ledger's equivalence payload matches, so the append is an
    `IDEMPOTENT_NOOP` and the call reports CAPTURED - but the record JSONL line
    was already appended unconditionally, so the physical duplicate survives.
    """

    store, executor = _executor(tmp_path)
    first = str(_write_note(executor)["memory_ref"])
    second = str(_write_note(executor)["memory_ref"])

    assert first == second
    assert _tool_event_lines(tmp_path, first) == 2
    captures = [
        entry
        for entry in store.read_memory_operations()
        if entry.operation_kind is MemoryOperationKind.CAPTURE
    ]
    assert len(captures) == 1, "the second append is an IDEMPOTENT_NOOP, not a second row"


def test_w5_memory_id_is_content_addressed_over_the_named_dimensions(tmp_path: Path) -> None:
    """W-5's identity summary, asserted directly rather than inferred from the
    cells: `memory_id` varies with TEXT, MODEL and `idempotency_key`, and NOT
    with `provider`."""

    _store, executor = _executor(tmp_path)
    base = MemoryID(str(_write_note(executor)["memory_ref"]))

    _store2, other = _executor(tmp_path / "b")
    assert MemoryID(str(_write_note(other, provider="azure-openai")["memory_ref"])) == base
    _store3, third = _executor(tmp_path / "c")
    assert MemoryID(str(_write_note(third, model="gpt-5-mini")["memory_ref"])) != base
    _store4, fourth = _executor(tmp_path / "d")
    assert MemoryID(str(_write_note(fourth, note="other text")["memory_ref"])) != base
    _store5, fifth = _executor(tmp_path / "e")
    assert MemoryID(str(_write_note(fifth, idempotency_key="note:other")["memory_ref"])) != base
