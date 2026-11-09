"""U-RT-161: the daemon's `resume_workflow` tool resumes a durable root pause over MCP.

Provider-free, as the B-104 facade tests: the real bootstrap (providers and OD stages faked), a
verified external state root, the real durable journal, claim store and CP driver, reached
through a real in-memory MCP client session against the bootstrapped daemon server — what
`cli/app.py` binds. Overlap is forced, never timed: a step body issues the second tool call
from CP's worker thread and blocks until it completes, so the second request runs entirely
inside the first body. Nothing here is an installed-host, socket or multi-process witness.
"""

from __future__ import annotations

import asyncio
import json
import sys
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import pytest
from harness_cp import workflow_driver
from harness_cp.engine_class import EngineClass
from harness_cp.pause_resume_protocol_types import ResumeContext
from harness_cp.pause_state_projection import AccessorDerivedResumeContext
from harness_cp.workflow_driver_types import RunResult as CpRunResult
from harness_cp.workflow_driver_types import RunStatus
from harness_runtime import api as api_module
from harness_runtime import bootstrap as bootstrap_module
from harness_runtime.api import resume
from harness_runtime.lifecycle.claimed_child_admission import ClaimedChildAdmission
from harness_runtime.lifecycle.journal_workflow_pause_store import EnginePauseLocator
from harness_runtime.lifecycle.root_resume_admission import RootResumeRefusal
from harness_runtime.resume_refusal import (
    ClaimRefusal,
    RefusalKind,
    ResumeRefusal,
    ResumeRefusalProtocolError,
    parse,
    project,
)
from harness_runtime.shutdown import shutdown
from harness_runtime.types import RuntimeConfig
from mcp import ClientSession
from mcp.shared.memory import create_connected_server_and_client_session
from mcp.types import CallToolResult, TextContent

from .integration.test_r_cc_1_api_resume import (
    _patched_runtime,  # noqa: F401  # pyright: ignore[reportPrivateUsage, reportUnusedImport]
)
from .test_b104_5b1_runtime_handoff import Chain
from .test_b104_root_resume_facade import (
    _WORKFLOW_ID,  # pyright: ignore[reportPrivateUsage]
    _WORKLOAD,  # pyright: ignore[reportPrivateUsage]
    Harness,
    _Dispatcher,  # pyright: ignore[reportPrivateUsage]
    _durable_filesystem,  # noqa: F401  # pyright: ignore[reportPrivateUsage, reportUnusedImport]
    _Workflow,  # pyright: ignore[reportPrivateUsage]
)
from .test_resume_refusal import SPEC_CASES
from .test_state_placement import world  # noqa: F401  (fixture: scratch dir with no .git above)

pytestmark = [
    pytest.mark.skipif(sys.platform == "win32", reason="claim leases require POSIX flock"),
    pytest.mark.usefixtures("_patched_runtime"),
]

_CANARIES = ("CANARY", "/srv", "tenant-acme", "secret", "tok-")


@pytest.fixture
def harness(world: Path) -> Harness:  # noqa: F811
    return Harness(world)


# --- the daemon, its CP seam and the wire decoder -----------------------------------------------


@asynccontextmanager
async def _daemon(config: RuntimeConfig, *workflows: _Workflow) -> AsyncGenerator[ClientSession]:
    """A bootstrapped daemon server bound as `cli/app.py` binds it, behind an MCP client."""
    ctx = await bootstrap_module.run_bootstrap(config, workload_class=_WORKLOAD)
    try:
        server = cast(Any, ctx.mcp_server)
        server._state["_harness_ctx"] = ctx
        server.workflow_registry.update({wf.workflow_id: wf for wf in workflows})
        async with create_connected_server_and_client_session(server.server) as session:
            yield session
    finally:
        await shutdown(ctx)


@dataclass(frozen=True)
class _CpCall:
    """What one root body handed CP's driver."""

    workflow_id: str
    run_id: str
    resume_context: object
    pause_snapshot_input: object
    child_resume_authority: object


def _record_cp(
    monkeypatch: pytest.MonkeyPatch, execute: Callable[..., Any] | None = None
) -> list[_CpCall]:
    """Record every CP driver entry, then run `execute` (the real driver unless replaced).

    Installed before the daemon bootstraps: the server binds `execute_workflow` when it is
    materialized.
    """
    run = execute or workflow_driver.execute_workflow
    calls: list[_CpCall] = []

    def recording(manifest_entry: Any, steps: Any, run_id: str, ctx: Any, **kwargs: Any) -> Any:
        calls.append(
            _CpCall(
                workflow_id=manifest_entry.workflow_id,
                run_id=run_id,
                resume_context=kwargs.get("resume_context"),
                pause_snapshot_input=kwargs.get("pause_snapshot_input"),
                child_resume_authority=kwargs.get("child_resume_authority"),
            )
        )
        return run(manifest_entry, steps, run_id, ctx, **kwargs)

    monkeypatch.setattr(workflow_driver, "execute_workflow", recording)
    return calls


def _from_body(
    session: ClientSession, tool: str, arguments: dict[str, Any], replies: list[CallToolResult]
) -> Callable[[], None]:
    """A step observer that issues one tool call from CP's worker thread and waits for it."""
    loop = asyncio.get_running_loop()

    def call() -> None:
        replies.append(
            asyncio.run_coroutine_threadsafe(session.call_tool(tool, arguments), loop).result()
        )

    return call


def _refusal(reply: CallToolResult) -> ResumeRefusal:
    """The v1.137 §D.2 refusal reply decoded: `isError` and exactly one closed refusal object."""
    assert reply.isError is True, reply
    match reply.content:
        case [TextContent(text=text)]:
            return parse(text)
        case _:
            raise AssertionError(f"not exactly one text refusal: {reply.content!r}")


def _run_result(reply: CallToolResult) -> dict[str, Any]:
    assert reply.isError is False, reply
    match reply.content:
        case [TextContent(text=text)]:
            return json.loads(text)
        case _:
            raise AssertionError(f"not exactly one text result: {reply.content!r}")


async def _resume(session: ClientSession, workflow_id: str, **context: Any) -> CallToolResult:
    return await session.call_tool("resume_workflow", {"workflow_id": workflow_id} | context)


# --- W1: a fresh run beside a resume is fresh ---------------------------------------------------


@pytest.mark.asyncio
async def test_a_fresh_run_inside_a_resumed_body_gets_its_own_run_and_no_resume_inputs(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    await harness.capture_root()
    calls = _record_cp(monkeypatch)
    replies: list[CallToolResult] = []
    nested: list[Callable[[], None]] = []  # bound once the session exists
    root, other = _Dispatcher(lambda: nested[0]()), _Dispatcher()
    resumed, fresh = _Workflow(root), _Workflow(other, "wf-other")

    async with _daemon(harness.config, resumed, fresh) as session:
        nested.append(_from_body(session, "run_workflow", {"workflow_id": "wf-other"}, replies))
        reply = await _resume(session, _WORKFLOW_ID)

    assert _run_result(reply)["run_id"] == "run-root"
    assert _run_result(replies[0])["run_id"] != "run-root"
    assert (root.steps, other.steps) == (["step-0"], ["step-0"])
    by_workflow = {call.workflow_id: call for call in calls}
    assert type(by_workflow[_WORKFLOW_ID].child_resume_authority) is ClaimedChildAdmission
    assert by_workflow["wf-other"] == _CpCall(
        workflow_id="wf-other",
        run_id=by_workflow["wf-other"].run_id,
        resume_context=None,
        pause_snapshot_input=None,
        child_resume_authority=None,
    )


# --- W2: at most once, across overlapping daemon requests ---------------------------------------


@pytest.mark.asyncio
async def test_a_second_resume_inside_the_first_body_is_claim_refused_and_runs_nothing(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    ref = await harness.capture_root()
    calls = _record_cp(monkeypatch)
    replies: list[CallToolResult] = []
    nested: list[Callable[[], None]] = []  # bound once the session exists
    dispatcher = _Dispatcher(lambda: nested[0]())

    async with _daemon(harness.config, _Workflow(dispatcher)) as session:
        nested.append(
            _from_body(session, "resume_workflow", {"workflow_id": _WORKFLOW_ID}, replies)
        )
        first = await _resume(session, _WORKFLOW_ID)

    assert _run_result(first)["status"] == "success"
    assert _refusal(replies[0]) == ClaimRefusal(reason=RootResumeRefusal("claim-refused"))
    assert dispatcher.steps == ["step-0"] and len(calls) == 1
    assert (harness.phase(ref), harness.lease(ref)) == ("started", "free")


# --- W3: a fresh run admitted after the resume's reads supersedes its record --------------------


@pytest.mark.asyncio
async def test_a_fresh_run_after_the_resume_reads_leaves_the_resume_refused(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    ref = await harness.capture_root()
    dispatcher = _Dispatcher()
    real = api_module._enforce_pause_state_staleness_precondition  # pyright: ignore[reportPrivateUsage]
    fresh: list[CallToolResult] = []
    sessions: list[ClientSession] = []

    async def last_read_then_fresh_run(*args: Any, **kwargs: Any) -> None:
        await real(*args, **kwargs)
        fresh.append(await sessions[0].call_tool("run_workflow", {"workflow_id": _WORKFLOW_ID}))

    monkeypatch.setattr(
        api_module, "_enforce_pause_state_staleness_precondition", last_read_then_fresh_run
    )

    async with _daemon(harness.config, _Workflow(dispatcher)) as session:
        sessions.append(session)
        reply = await _resume(session, _WORKFLOW_ID)

    assert _run_result(fresh[0])["status"] == "success"
    assert _refusal(reply).kind is RefusalKind.CLAIM
    assert dispatcher.steps == ["step-0"] and harness.phase(ref) == "none"


# --- W4: every daemon-reachable refusal is the closed wire object, and nothing runs -------------


@dataclass(frozen=True)
class _Arranged:
    config: RuntimeConfig
    workflow: _Workflow
    context: dict[str, Any]


async def _no_capture(h: Harness) -> _Arranged:
    return _Arranged(h.config, _Workflow(_Dispatcher()), {})


async def _malformed_context(h: Harness) -> _Arranged:
    await h.capture_root()
    return _Arranged(h.config, _Workflow(_Dispatcher()), {"resume_context": {"not_a_field": 1}})


async def _child_handle(h: Harness) -> _Arranged:
    h.site.stamp(h.config)
    Chain(h.journal_dir)
    return _Arranged(h.config, _Workflow(_Dispatcher(), "wf-c"), {})


async def _protocol_unbound(h: Harness) -> _Arranged:
    await h.capture_root()
    config = h.config.model_copy(update={"pause_resume_protocol_config": None})
    return _Arranged(config, _Workflow(_Dispatcher()), {})


async def _stale_pause_state(h: Harness) -> _Arranged:
    await h.capture_root()
    workflow = _Workflow(_Dispatcher())
    state = await api_module.read_paused_workflow_state(
        workflow, resume_handle=_WORKFLOW_ID, config=h.config
    )
    latest = h.journal().read_latest(_WORKFLOW_ID)
    assert latest is not None
    h.journal().capture(latest, depth=0)
    return _Arranged(
        h.config, workflow, {"resume_context": {"pause_state": state.model_dump(mode="json")}}
    )


async def _workflow_without_steps(h: Harness) -> _Arranged:
    await h.capture_root()
    workflow = _Workflow(_Dispatcher())
    workflow.steps = ()
    return _Arranged(h.config, workflow, {})


async def _already_claimed(h: Harness) -> _Arranged:
    await h.capture_root()
    await resume(_Workflow(_Dispatcher()), resume_handle=_WORKFLOW_ID, config=h.config)
    return _Arranged(h.config, _Workflow(_Dispatcher()), {})


async def _superseded(h: Harness) -> _Arranged:
    await h.capture_root()
    h.journal().supersede(_WORKFLOW_ID, "run-fresh")
    return _Arranged(h.config, _Workflow(_Dispatcher()), {})


def _journal_locator(h: Harness, engine_class: EngineClass) -> None:
    h.site.stamp(h.config)
    h.journal().capture_locator(
        EnginePauseLocator(
            workflow_id=_WORKFLOW_ID,
            run_id="run-root",
            engine_class=engine_class,  # pyright: ignore[reportArgumentType]
            step_index=0,
        )
    )


async def _engine_record_absent(h: Harness) -> _Arranged:
    _journal_locator(h, EngineClass.WAL_SEGMENT)
    workflow = _Workflow(_Dispatcher())
    workflow.manifest_entry = workflow.manifest_entry.model_copy(
        update={"engine_class": EngineClass.WAL_SEGMENT}
    )
    return _Arranged(h.config, workflow, {})


async def _engine_class_changed(h: Harness) -> _Arranged:
    _journal_locator(h, EngineClass.RECONCILER_LOOP)
    return _Arranged(h.config, _Workflow(_Dispatcher()), {})


_ARRANGE: dict[RefusalKind, Callable[[Harness], Awaitable[_Arranged]]] = {
    RefusalKind.ARGUMENTS: _malformed_context,
    RefusalKind.HANDLE: _no_capture,
    RefusalKind.DEPTH: _child_handle,
    RefusalKind.PROTOCOL_NOT_BOUND: _protocol_unbound,
    RefusalKind.PAUSE_STATE_STALE: _stale_pause_state,
    RefusalKind.STEP_INDEX_OUT_OF_RANGE: _workflow_without_steps,
    RefusalKind.CLAIM: _already_claimed,
    RefusalKind.PAUSE_RECORD_SUPERSEDED: _superseded,
    RefusalKind.ENGINE_PAUSE_RECORD_ABSENT: _engine_record_absent,
    RefusalKind.ENGINE_CLASS_MISMATCH: _engine_class_changed,
}


def test_every_refusal_but_workflow_mismatch_is_reached_through_the_daemon() -> None:
    # The daemon resolves the handle from the workflow's own id, so the journal it reads is
    # that workflow's; the mismatch arm is exercised on the adapter (test_resume_refusal).
    assert set(_ARRANGE) == set(RefusalKind) - {RefusalKind.WORKFLOW_MISMATCH}


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", list(_ARRANGE), ids=str)
async def test_each_refusal_replies_as_its_closed_object_and_runs_nothing(
    harness: Harness, monkeypatch: pytest.MonkeyPatch, kind: RefusalKind
) -> None:
    arranged = await _ARRANGE[kind](harness)
    calls = _record_cp(monkeypatch)

    async with _daemon(arranged.config, arranged.workflow) as session:
        reply = await _resume(session, arranged.workflow.workflow_id, **arranged.context)

    assert _refusal(reply).kind is kind
    assert calls == [] and arranged.workflow.step_dispatchers.lookup(None).steps == []


@pytest.mark.asyncio
async def test_the_refusal_decoder_rejects_every_near_miss_of_the_reply(harness: Harness) -> None:
    async with _daemon(harness.config, _Workflow(_Dispatcher())) as session:
        reply = await _resume(session, _WORKFLOW_ID)
    text = cast(TextContent, reply.content[0]).text
    assert _refusal(reply).kind is RefusalKind.HANDLE

    # json.loads tolerates surrounding whitespace, so each mutant adds a non-whitespace byte.
    near_misses = [
        CallToolResult(isError=False, content=reply.content),
        CallToolResult(isError=True, content=[TextContent(type="text", text="x" + text)]),
        CallToolResult(isError=True, content=[TextContent(type="text", text=text + "x")]),
        CallToolResult(isError=True, content=[*reply.content, *reply.content]),
    ]
    for mutant in near_misses:
        with pytest.raises((AssertionError, ResumeRefusalProtocolError)):
            _refusal(mutant)


# --- W5: the tool's declared inputs, and what a refusal reply never carries ---------------------


@pytest.mark.asyncio
async def test_resume_workflow_takes_a_workflow_id_and_an_optional_resume_context(
    harness: Harness,
) -> None:
    async with _daemon(harness.config) as session:
        tools = {tool.name: tool for tool in (await session.list_tools()).tools}

    schema = tools["resume_workflow"].inputSchema
    assert set(schema["properties"]) == {"workflow_id", "resume_context"}
    assert schema["required"] == ["workflow_id"]


@pytest.mark.asyncio
async def test_each_typed_refusal_replies_as_its_projection_with_no_path_tenant_or_secret(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    pending = iter(error for error, _ in SPEC_CASES)

    async def refuse(*_args: Any, **_kwargs: Any) -> Any:
        raise next(pending)

    monkeypatch.setattr(api_module, "admit_root_resume", refuse)

    async with _daemon(harness.config, _Workflow(_Dispatcher())) as session:
        replies = [await _resume(session, _WORKFLOW_ID) for _ in SPEC_CASES]

    for (error, _), reply in zip(SPEC_CASES, replies, strict=True):
        assert _refusal(reply) == project(error)
        text = cast(TextContent, reply.content[0]).text
        assert not [canary for canary in _CANARIES if canary in text], text


# --- W6: the wire resume_context is parsed once into its closed variant -------------------------


@pytest.mark.asyncio
async def test_an_empty_resume_context_reaches_cp_as_the_base_variant(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    await harness.capture_root()
    calls = _record_cp(monkeypatch)

    async with _daemon(harness.config, _Workflow(_Dispatcher())) as session:
        reply = await _resume(session, _WORKFLOW_ID, resume_context={})

    assert _run_result(reply)["status"] == "success"
    assert [type(call.resume_context) for call in calls] == [ResumeContext]


@pytest.mark.asyncio
async def test_an_accessor_resume_context_reaches_cp_as_the_fenced_variant(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    await harness.capture_root()
    workflow = _Workflow(_Dispatcher())
    state = await api_module.read_paused_workflow_state(
        workflow, resume_handle=_WORKFLOW_ID, config=harness.config
    )
    calls = _record_cp(monkeypatch)

    async with _daemon(harness.config, workflow) as session:
        reply = await _resume(
            session, _WORKFLOW_ID, resume_context={"pause_state": state.model_dump(mode="json")}
        )

    assert _run_result(reply)["status"] == "success"
    assert [type(call.resume_context) for call in calls] == [AccessorDerivedResumeContext]


@pytest.mark.asyncio
async def test_a_malformed_resume_context_is_an_arguments_refusal_before_any_journal_read(
    harness: Harness, monkeypatch: pytest.MonkeyPatch
) -> None:
    await harness.capture_root()
    real = api_module._read_durable_pause_snapshot  # pyright: ignore[reportPrivateUsage]
    reads: list[object] = []

    def counting(*args: Any, **kwargs: Any) -> Any:
        reads.append(args)
        return real(*args, **kwargs)

    monkeypatch.setattr(api_module, "_read_durable_pause_snapshot", counting)

    async with _daemon(harness.config, _Workflow(_Dispatcher())) as session:
        reply = await _resume(session, _WORKFLOW_ID, resume_context={"pause_state": 7})

    assert _refusal(reply).kind is RefusalKind.ARGUMENTS
    assert reads == []


# --- W7: a resumed outcome is the same RunResult JSON a fresh run replies -----------------------


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [RunStatus.SUCCESS, RunStatus.PAUSED])
async def test_resume_and_run_reply_the_identical_run_result_json(
    harness: Harness, monkeypatch: pytest.MonkeyPatch, status: RunStatus
) -> None:
    await harness.capture_root()
    outcome = CpRunResult(
        workflow_id=_WORKFLOW_ID,
        run_id="run-fixed",
        status=status,
        terminal_step_index=0,
        pause_snapshot=(
            harness.journal().read_latest(_WORKFLOW_ID) if status is RunStatus.PAUSED else None
        ),
    )
    _record_cp(monkeypatch, lambda *_args, **_kwargs: outcome)

    async with _daemon(harness.config, _Workflow(_Dispatcher())) as session:
        resumed = await _resume(session, _WORKFLOW_ID)
        fresh = await session.call_tool("run_workflow", {"workflow_id": _WORKFLOW_ID})

    expected = outcome.model_dump(mode="json")
    assert _run_result(resumed) == _run_result(fresh) == expected
