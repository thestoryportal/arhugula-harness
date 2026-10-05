"""Tests for U-RT-108 — daemon-client mode (``harness run <file> --daemon``).

Maps to acceptance criteria 1–7 at runtime plan v2.31 §1.8. The daemon-client
mode connects to a running ``harness daemon`` via Unix-socket transport
(MCP streamable-HTTP over uds via httpx.AsyncHTTPTransport) and invokes the
``run_workflow`` MCP tool with the workflow_id-as-path semantics ratified at
``.harness/class_1_fork_u_rt_107_daemon_run_workflow_signature_underspec.md``
Reading (A) 2026-05-28.

Strategy:
- AC #1/#4 — mocked ``_daemon_client_dispatch`` returning synthetic CP RunResult
  dicts; verify exit-code mapping (SUCCESS → 0; DRAINED/FAILED → 1).
- AC #2 — verify ``--socket-path`` flag override + presence in help.
- AC #3 — socket path absent → exit 4 + RT-FAIL-CLI-DAEMON-CONNECTION.
- AC #5/#6/#7 — semantic equivalence + SIGINT graceful disconnect + concurrent
  clients — deferred to U-RT-109 e2e per the L9-undecies precedent (real
  daemon + real MCP client + real workflow execution at cluster terminus).
"""

from __future__ import annotations

import asyncio
import re
import sys
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import harness_runtime.cli.app as _ensure_import
import pytest
from typer.testing import CliRunner

_cli_app_mod = sys.modules["harness_runtime.cli.app"]
assert _ensure_import is not None

from harness_runtime.cli.app import (
    EXIT_BOOTSTRAP_ERROR,
    EXIT_PAUSED,
    EXIT_SUCCESS,
    EXIT_WORKFLOW_FAIL,
    app,
)

runner = CliRunner()
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def _plain(text: str) -> str:
    return _ANSI_RE.sub("", text)


def _reset_test_sse_state(monkeypatch: pytest.MonkeyPatch) -> None:
    from sse_starlette.sse import AppStatus

    # [LAW:no-ambient-temporal-coupling] The prior test server's shutdown
    # watcher can leave this process-wide flag set for the next SSE response.
    monkeypatch.setattr(AppStatus, "should_exit", False)


_VALID_YAML = """\
version: 1
workflow:
  workflow_id: "wf-cli-daemon-client"
  workload_class: "software-engineering"
  persona_tier: "solo-developer"
  engine_class: "pure-pattern-no-engine"
  topology_pattern: "evaluator-optimizer"
default_model_binding:
  provider: "anthropic"
  model: "claude-opus-4-7"
steps:
  - step_id: "s1"
    step_kind: "inference-step"
    step_payload: {}
"""


def _write_yaml(tmp_path: Path) -> Path:
    path = tmp_path / "wf.yaml"
    path.write_text(_VALID_YAML, encoding="utf-8")
    return path


def _stub_dispatch(
    monkeypatch: pytest.MonkeyPatch,
    *,
    payload: dict[str, Any] | None = None,
    raises: BaseException | None = None,
) -> dict[str, Any]:
    """Install a fake ``_daemon_client_dispatch`` that returns ``payload``."""
    captured: dict[str, Any] = {}

    async def _fake(
        *, workflow_file: Path, socket_path: Path, result_timeout_seconds: float
    ) -> dict[str, Any]:
        captured["workflow_file"] = workflow_file
        captured["socket_path"] = socket_path
        captured["result_timeout_seconds"] = result_timeout_seconds
        if raises is not None:
            raise raises
        return (
            payload
            if payload is not None
            else {
                "status": "success",
                "workflow_id": "wf-cli-daemon-client",
                "run_id": "abc123",
            }
        )

    monkeypatch.setattr(_cli_app_mod, "_daemon_client_dispatch", _fake)
    return captured


# ---------------------------------------------------------------------------
# AC #1 — happy path SUCCESS → exit 0
# ---------------------------------------------------------------------------


def test_ac1_daemon_client_success_exits_zero(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    socket_path = tmp_path / "daemon.sock"
    socket_path.touch()  # CLI presence-check requires socket to exist
    captured = _stub_dispatch(monkeypatch, payload={"status": "success"})
    manifest = _write_yaml(tmp_path)
    result = runner.invoke(
        app,
        ["run", str(manifest), "--daemon", "--socket-path", str(socket_path)],
    )
    assert result.exit_code == EXIT_SUCCESS, result.stdout + result.stderr
    assert captured["workflow_file"] == manifest
    assert captured["socket_path"] == socket_path
    out = _plain(result.stdout)
    assert "success" in out


# ---------------------------------------------------------------------------
# AC #2 — --socket-path override + help
# ---------------------------------------------------------------------------


def test_ac2_socket_path_flag_appears_in_run_help() -> None:
    result = runner.invoke(app, ["run", "--help"])
    assert result.exit_code == 0
    out = _plain(result.stdout)
    assert "--socket-path" in out


def test_ac2_socket_path_override_threads_through(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    socket_path = tmp_path / "custom.sock"
    socket_path.touch()
    captured = _stub_dispatch(monkeypatch, payload={"status": "success"})
    manifest = _write_yaml(tmp_path)
    result = runner.invoke(
        app,
        ["run", str(manifest), "--daemon", "--socket-path", str(socket_path)],
    )
    assert result.exit_code == EXIT_SUCCESS
    assert captured["socket_path"] == socket_path
    assert captured["result_timeout_seconds"] == 3600.0


@pytest.mark.parametrize("value", ["0", "-1", "nan", "inf", "-inf", "invalid"])
def test_daemon_result_timeout_rejects_invalid_values(tmp_path: Path, value: str) -> None:
    manifest = _write_yaml(tmp_path)
    result = runner.invoke(
        app,
        ["run", str(manifest), "--daemon", "--daemon-result-timeout-seconds", value],
    )
    assert result.exit_code == 2
    assert "--daemon-result-timeout-seconds" in _plain(result.output)


def test_daemon_result_timeout_rejects_one_shot_use(tmp_path: Path) -> None:
    manifest = _write_yaml(tmp_path)
    result = runner.invoke(app, ["run", str(manifest), "--daemon-result-timeout-seconds", "1"])
    assert result.exit_code == 2
    assert "requires --daemon" in _plain(result.output)


def test_daemon_result_timeout_override_reaches_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    socket_path = tmp_path / "daemon.sock"
    socket_path.touch()
    captured = _stub_dispatch(monkeypatch)
    manifest = _write_yaml(tmp_path)
    result = runner.invoke(
        app,
        [
            "run",
            str(manifest),
            "--daemon",
            "--socket-path",
            str(socket_path),
            "--daemon-result-timeout-seconds",
            "12.5",
        ],
    )
    assert result.exit_code == EXIT_SUCCESS
    assert captured["result_timeout_seconds"] == 12.5


def test_daemon_result_failure_exits_four_without_json_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from harness_runtime.cli.app import DaemonResultError

    socket_path = tmp_path / "daemon.sock"
    socket_path.touch()
    _stub_dispatch(monkeypatch, raises=DaemonResultError("synthetic MCP timeout"))
    manifest = _write_yaml(tmp_path)
    result = runner.invoke(
        app,
        ["run", str(manifest), "--daemon", "--socket-path", str(socket_path), "--output", "json"],
    )
    assert result.exit_code == EXIT_BOOTSTRAP_ERROR
    assert result.stdout == ""
    assert "RT-FAIL-CLI-DAEMON-RESULT: synthetic MCP timeout" in result.stderr


@pytest.mark.asyncio
async def test_dispatch_uses_loopback_nominal_url_for_uds_transport(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The UDS transport is the real connection path; the URL must still carry
    an ASGI-accepted Host header to avoid HTTP 421 from the daemon app."""
    import mcp
    import mcp.client.streamable_http as streamable_http_mod

    captured: dict[str, Any] = {}

    class _FakeStreamableHTTPClient:
        async def __aenter__(self) -> tuple[object, object, Any]:
            return object(), object(), lambda: None

        async def __aexit__(self, *args: object) -> None:
            return None

    def _fake_streamable_http_client(
        url: str,
        *,
        http_client: Any = None,
        terminate_on_close: bool = True,
    ) -> _FakeStreamableHTTPClient:
        captured["url"] = url
        captured["http_client"] = http_client
        captured["terminate_on_close"] = terminate_on_close
        return _FakeStreamableHTTPClient()

    class _FakeClientSession:
        def __init__(
            self,
            read_stream: object,
            write_stream: object,
            read_timeout_seconds: timedelta,
        ) -> None:
            captured["session_streams"] = (read_stream, write_stream)
            captured["session_timeout"] = read_timeout_seconds

        async def __aenter__(self) -> _FakeClientSession:
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def initialize(self) -> None:
            captured["initialized"] = True

        async def call_tool(
            self,
            name: str,
            arguments: dict[str, str],
            read_timeout_seconds: timedelta,
        ) -> Any:
            captured["tool_name"] = name
            captured["tool_arguments"] = arguments
            captured["result_timeout"] = read_timeout_seconds
            return SimpleNamespace(
                isError=False,
                content=[SimpleNamespace(text='{"status":"success","workflow_id":"wf"}')],
            )

    monkeypatch.setattr(
        streamable_http_mod,
        "streamable_http_client",
        _fake_streamable_http_client,
    )
    monkeypatch.setattr(mcp, "ClientSession", _FakeClientSession)

    workflow = _write_yaml(tmp_path)
    socket_path = tmp_path / "daemon.sock"
    payload = await _cli_app_mod._daemon_client_dispatch(
        workflow_file=workflow,
        socket_path=socket_path,
        result_timeout_seconds=120.0,
    )

    assert payload["status"] == "success"
    assert captured["url"] == _cli_app_mod._DAEMON_CLIENT_STREAMABLE_HTTP_URL
    assert captured["url"] == "http://127.0.0.1/mcp"
    assert captured["http_client"] is not None
    assert captured["tool_name"] == "run_workflow"
    assert captured["tool_arguments"] == {"workflow_id": str(workflow)}
    assert captured["session_timeout"] == timedelta(seconds=30)
    assert captured["result_timeout"] == timedelta(seconds=120)
    assert captured["http_client"].timeout.read is None
    assert captured["http_client"].timeout.connect == 30
    assert captured["http_client"].timeout.write == 30
    assert captured["http_client"].timeout.pool == 30


# ---------------------------------------------------------------------------
# AC #3 — daemon not running → RT-FAIL-CLI-DAEMON-CONNECTION → exit 4
# ---------------------------------------------------------------------------


def test_ac3_socket_absent_exits_four_with_daemon_connection_fail_class(
    tmp_path: Path,
) -> None:
    nonexistent = tmp_path / "no-such.sock"
    manifest = _write_yaml(tmp_path)
    result = runner.invoke(
        app, ["run", str(manifest), "--daemon", "--socket-path", str(nonexistent)]
    )
    assert result.exit_code == EXIT_BOOTSTRAP_ERROR, result.stdout + result.stderr
    assert "RT-FAIL-CLI-DAEMON-CONNECTION" in result.stderr


def test_ac3_connection_error_during_dispatch_exits_four(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    socket_path = tmp_path / "daemon.sock"
    socket_path.touch()
    from harness_runtime.cli.app import DaemonStartupError

    _stub_dispatch(
        monkeypatch,
        raises=DaemonStartupError("synthetic mid-dispatch connection failure"),
    )
    manifest = _write_yaml(tmp_path)
    result = runner.invoke(
        app, ["run", str(manifest), "--daemon", "--socket-path", str(socket_path)]
    )
    assert result.exit_code == EXIT_BOOTSTRAP_ERROR, result.stdout + result.stderr
    assert "RT-FAIL-CLI-DAEMON-CONNECTION" in result.stderr


def test_ac3_refused_unix_socket_stays_connection_failure(tmp_path: Path) -> None:
    import socket

    socket_path = tmp_path / "refused.sock"
    with socket.socket(socket.AF_UNIX) as listener:
        listener.bind(str(socket_path))
    manifest = _write_yaml(tmp_path)
    result = runner.invoke(
        app, ["run", str(manifest), "--daemon", "--socket-path", str(socket_path)]
    )
    assert result.exit_code == EXIT_BOOTSTRAP_ERROR
    assert "RT-FAIL-CLI-DAEMON-CONNECTION" in result.stderr
    assert "refused" in result.stderr.lower()
    assert result.stdout == ""


@pytest.mark.asyncio
async def test_mixed_mcp_error_group_keeps_connection_detail(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import httpx
    import mcp.client.streamable_http as streamable_http_mod
    from harness_runtime.cli.app import DaemonStartupError
    from mcp.shared.exceptions import McpError
    from mcp.types import ErrorData

    class _BrokenStream:
        async def __aenter__(self) -> None:
            raise ExceptionGroup(
                "transport cleanup",
                [
                    httpx.ConnectError("refused by test peer"),
                    McpError(ErrorData(code=408, message="response also failed")),
                ],
            )

        async def __aexit__(self, *args: object) -> None:
            return None

    def _fake_stream(*args: object, **kwargs: object) -> _BrokenStream:
        return _BrokenStream()

    monkeypatch.setattr(streamable_http_mod, "streamable_http_client", _fake_stream)
    with pytest.raises(DaemonStartupError, match="refused by test peer"):
        await _cli_app_mod._daemon_client_dispatch(
            workflow_file=Path("workflow.toml"),
            socket_path=tmp_path / "daemon.sock",
            result_timeout_seconds=0.1,
        )


@pytest.mark.asyncio
async def test_initialize_failure_reports_its_own_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import mcp
    import mcp.client.streamable_http as streamable_http_mod
    from harness_runtime.cli.app import DaemonResultError
    from mcp.shared.exceptions import McpError
    from mcp.types import ErrorData

    class _FakeStream:
        async def __aenter__(self) -> tuple[object, object, Any]:
            return object(), object(), lambda: None

        async def __aexit__(self, *args: object) -> None:
            return None

    class _FailingSession:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        async def __aenter__(self) -> _FailingSession:
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def initialize(self) -> None:
            raise McpError(ErrorData(code=408, message="initialize timed out"))

    def _fake_stream(*args: object, **kwargs: object) -> _FakeStream:
        return _FakeStream()

    monkeypatch.setattr(streamable_http_mod, "streamable_http_client", _fake_stream)
    monkeypatch.setattr(mcp, "ClientSession", _FailingSession)
    with pytest.raises(DaemonResultError, match="initialize response failed \\(budget 30s\\)"):
        await _cli_app_mod._daemon_client_dispatch(
            workflow_file=Path("workflow.toml"),
            socket_path=tmp_path / "daemon.sock",
            result_timeout_seconds=0.1,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("failure_kind", ["connection", "result", "generic"])
async def test_primary_daemon_failure_survives_teardown_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure_kind: str
) -> None:
    """A secondary teardown expiry cannot replace the primary CLI failure."""
    import httpx
    import mcp.client.streamable_http as streamable_http_mod
    from harness_runtime.cli.app import DaemonResultError, DaemonStartupError
    from mcp.shared.exceptions import McpError
    from mcp.types import ErrorData

    class _FailingStream:
        async def __aenter__(self) -> None:
            if failure_kind == "connection":
                raise httpx.ConnectError("primary connection refused")
            if failure_kind == "result":
                raise McpError(ErrorData(code=408, message="primary result unavailable"))
            raise ValueError("primary unclassified failure")

        async def __aexit__(self, *args: object) -> None:
            return None

    def _failing_stream(*args: object, **kwargs: object) -> _FailingStream:
        return _FailingStream()

    async def _failing_teardown(stack: Any, client: httpx.AsyncClient) -> None:
        await stack.aclose()
        await client.aclose()
        raise DaemonResultError("secondary teardown expired")

    monkeypatch.setattr(streamable_http_mod, "streamable_http_client", _failing_stream)
    monkeypatch.setattr(_cli_app_mod, "_close_daemon_client", _failing_teardown)
    expected: type[Exception] = {
        "connection": DaemonStartupError,
        "result": DaemonResultError,
        "generic": ValueError,
    }[failure_kind]
    message = {
        "connection": "primary connection refused",
        "result": "primary result unavailable",
        "generic": "primary unclassified failure",
    }[failure_kind]
    with pytest.raises(expected, match=message) as primary:
        await _cli_app_mod._daemon_client_dispatch(
            workflow_file=Path("workflow.toml"),
            socket_path=tmp_path / "daemon.sock",
            result_timeout_seconds=1.0,
        )
    if failure_kind == "connection":
        assert isinstance(primary.value.__cause__, httpx.ConnectError)
    elif failure_kind == "result":
        assert isinstance(primary.value.__cause__, McpError)
    assert any("secondary teardown expired" in note for note in primary.value.__notes__)


# ---------------------------------------------------------------------------
# AC #4 — RunResult propagation: SUCCESS → 0, FAILED → 1, DRAINED → 1
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("status", "expected_exit"),
    [
        ("success", EXIT_SUCCESS),
        ("drained", EXIT_WORKFLOW_FAIL),
        ("failed", EXIT_WORKFLOW_FAIL),
        ("partial", EXIT_WORKFLOW_FAIL),
        ("pending", EXIT_WORKFLOW_FAIL),
        ("paused", EXIT_PAUSED),
    ],
)
def test_ac4_cp_status_to_exit_code_mapping(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    status: str,
    expected_exit: int,
) -> None:
    socket_path = tmp_path / "daemon.sock"
    socket_path.touch()
    _stub_dispatch(monkeypatch, payload={"status": status, "workflow_id": "wf"})
    manifest = _write_yaml(tmp_path)
    result = runner.invoke(
        app, ["run", str(manifest), "--daemon", "--socket-path", str(socket_path)]
    )
    assert result.exit_code == expected_exit, f"status={status!r}: {result.stdout + result.stderr}"


# ---------------------------------------------------------------------------
# Adjacent — --output=json emits raw JSON from daemon payload
# ---------------------------------------------------------------------------


def test_output_json_emits_raw_payload(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import json

    socket_path = tmp_path / "daemon.sock"
    socket_path.touch()
    payload = {"status": "success", "workflow_id": "wf-json", "run_id": "xyz"}
    _stub_dispatch(monkeypatch, payload=payload)
    manifest = _write_yaml(tmp_path)
    result = runner.invoke(
        app,
        [
            "run",
            str(manifest),
            "--daemon",
            "--socket-path",
            str(socket_path),
            "--output",
            "json",
        ],
    )
    assert result.exit_code == EXIT_SUCCESS, result.stdout + result.stderr
    parsed = json.loads(result.stdout)
    assert parsed == payload


# ---------------------------------------------------------------------------
# Adjacent — workflow_id-as-path discriminator threaded correctly
# ---------------------------------------------------------------------------


def test_dispatch_invoked_with_full_manifest_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """U-RT-107 fork Reading (A): workflow_id passed to daemon is the
    full manifest path (path-input branch triggers handler-side load)."""
    socket_path = tmp_path / "daemon.sock"
    socket_path.touch()
    captured = _stub_dispatch(monkeypatch, payload={"status": "success"})
    manifest = _write_yaml(tmp_path)
    result = runner.invoke(
        app, ["run", str(manifest), "--daemon", "--socket-path", str(socket_path)]
    )
    assert result.exit_code == EXIT_SUCCESS
    # The dispatch helper receives the workflow_file as a Path; the helper
    # body stringifies it for the tool call. Verify the path round-trips.
    assert captured["workflow_file"] == manifest
    from harness_runtime.lifecycle.mcp_server import (
        _looks_like_manifest_path,  # pyright: ignore[reportPrivateUsage]
    )

    assert _looks_like_manifest_path(str(manifest))


@pytest.mark.asyncio
async def test_real_mcp_result_deadline_and_received_status(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """One local MCP server exercises three ClientSession outcomes over a real UDS."""
    import httpx
    import uvicorn
    from harness_runtime.cli.app import DaemonResultError
    from mcp.server.fastmcp import FastMCP
    from mcp.server.transport_security import TransportSecuritySettings

    _reset_test_sse_state(monkeypatch)
    real_async_client = httpx.AsyncClient

    def _short_idle_client(*args: Any, timeout: httpx.Timeout, **kwargs: Any) -> httpx.AsyncClient:
        # A quiet response crosses this 20ms read-idle interval before the MCP
        # result deadline. The production client must explicitly disable it.
        if timeout.read is not None:
            timeout = httpx.Timeout(
                0.02, connect=timeout.connect, write=timeout.write, pool=timeout.pool
            )
        return real_async_client(*args, timeout=timeout, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", _short_idle_client)

    server = FastMCP(
        "deadline-test",
        transport_security=TransportSecuritySettings(allowed_hosts=["127.0.0.1"]),
    )

    cases = [
        (1.0, "success", True),
        (0.08, "success", False),
        (0.0, "failed", False),
    ]
    workflows = {
        f"workflow-{index}.toml": (delay, status) for index, (delay, status, _) in enumerate(cases)
    }

    @server.tool()
    async def run_workflow(workflow_id: str) -> str:
        delay, status = workflows[workflow_id]
        await asyncio.sleep(delay)
        return f'{{"status":"{status}","workflow_id":"{workflow_id}"}}'

    socket_path = tmp_path / "mcp.sock"
    uv_server = uvicorn.Server(
        uvicorn.Config(server.streamable_http_app(), uds=str(socket_path), log_level="error")
    )
    serve_task = asyncio.create_task(uv_server.serve())
    try:
        async with asyncio.timeout(8):
            while not uv_server.started:
                await asyncio.sleep(0.01)
            # [LAW:no-ambient-temporal-coupling] Separate client sessions
            # exercise re-entry after a result timeout on one running server.
            for index, (_, status, expected_error) in enumerate(cases):
                workflow = Path(f"workflow-{index}.toml")
                if expected_error:
                    with pytest.raises(DaemonResultError, match="Timed out"):
                        await _cli_app_mod._daemon_client_dispatch(
                            workflow_file=workflow,
                            socket_path=socket_path,
                            result_timeout_seconds=0.1,
                        )
                else:
                    payload = await _cli_app_mod._daemon_client_dispatch(
                        workflow_file=workflow,
                        socket_path=socket_path,
                        result_timeout_seconds=0.8,
                    )
                    assert payload == {"status": status, "workflow_id": str(workflow)}
    finally:
        uv_server.should_exit = True
        async with asyncio.timeout(3):
            await serve_task


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "cancel_during_tool", [False, True], ids=["after-result", "external-cancel"]
)
async def test_real_mcp_teardown_deadline_after_received_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, cancel_during_tool: bool
) -> None:
    """Bound DELETE after a result and preserve cancellation during a tool call."""
    import httpx
    import uvicorn
    from harness_runtime.cli.app import DaemonResultError
    from mcp.server.fastmcp import FastMCP
    from mcp.server.transport_security import TransportSecuritySettings

    _reset_test_sse_state(monkeypatch)
    real_async_client = httpx.AsyncClient
    clients: list[httpx.AsyncClient] = []

    def _tracked_client(*args: Any, **kwargs: Any) -> httpx.AsyncClient:
        client = real_async_client(*args, **kwargs)
        clients.append(client)
        return client

    monkeypatch.setattr(httpx, "AsyncClient", _tracked_client)
    # Cancellation still has to start session DELETE under a loaded host. Keep
    # the short deadline in the after-result case, checked by its typed error.
    teardown_budget = 5.0 if cancel_during_tool else 0.2
    monkeypatch.setattr(
        _cli_app_mod, "_DAEMON_CLIENT_TEARDOWN_TIMEOUT_SECONDS", teardown_budget, raising=False
    )
    tool_started = asyncio.Event()
    mcp_server = FastMCP(
        "teardown-deadline-test",
        transport_security=TransportSecuritySettings(allowed_hosts=["127.0.0.1"]),
    )

    @mcp_server.tool()
    async def run_workflow(workflow_id: str) -> str:
        tool_started.set()
        if cancel_during_tool:
            await asyncio.Event().wait()
        return f'{{"status":"success","workflow_id":"{workflow_id}"}}'

    mcp_app = mcp_server.streamable_http_app()
    delete_seen = asyncio.Event()
    delete_cancelled = asyncio.Event()

    async def stalled_delete_app(scope: dict[str, Any], receive: Any, send: Any) -> None:
        if scope["type"] != "http" or scope["method"] != "DELETE":
            await mcp_app(scope, receive, send)
            return
        delete_seen.set()
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [(b"content-type", b"text/event-stream")],
            }
        )
        try:
            while True:
                await send(
                    {"type": "http.response.body", "body": b": heartbeat\n\n", "more_body": True}
                )
                try:
                    message = await asyncio.wait_for(receive(), timeout=0.01)
                except TimeoutError:
                    continue
                if message["type"] == "http.disconnect":
                    break
        finally:
            delete_cancelled.set()

    socket_path = tmp_path / "mcp.sock"
    uv_server = uvicorn.Server(
        uvicorn.Config(stalled_delete_app, uds=str(socket_path), log_level="error")
    )
    serve_task = asyncio.create_task(uv_server.serve())
    try:
        async with asyncio.timeout(10 if cancel_during_tool else 15):
            while not uv_server.started:
                await asyncio.sleep(0.01)
            dispatch = asyncio.create_task(
                _cli_app_mod._daemon_client_dispatch(
                    workflow_file=Path("workflow.toml"),
                    socket_path=socket_path,
                    result_timeout_seconds=1.5 if cancel_during_tool else 10.0,
                )
            )
            if cancel_during_tool:
                await tool_started.wait()
                dispatch.cancel()
                # [LAW:behavior-not-structure] Caller expiry must fail rather than
                # satisfy the witness for dispatch cancellation.
                await asyncio.wait({dispatch})
                assert dispatch.cancelled(), dispatch.exception()
            else:
                with pytest.raises(
                    DaemonResultError, match=r"teardown exceeded the 0\.2s client budget"
                ) as teardown:
                    await dispatch
                assert tool_started.is_set()
                # A missing tool result would be the primary exception in this
                # finally path. Prove the result arrived before teardown failed.
                assert teardown.value.__context__ is None
            assert delete_seen.is_set()
            await asyncio.wait_for(delete_cancelled.wait(), timeout=5 if cancel_during_tool else 1)
            assert clients and clients[0].is_closed
    finally:
        uv_server.should_exit = True
        async with asyncio.timeout(3):
            await serve_task
