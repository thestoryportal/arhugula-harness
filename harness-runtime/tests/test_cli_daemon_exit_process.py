"""Opt-in shell exit witness for the installed daemon-client console script.

Run with HARNESS_CLI_EXIT_PROCESS=1 and an installed harness in the active venv.
The local MCP server supplies fixed results; no workflow or provider runs.
"""

from __future__ import annotations

import asyncio
import json
import os
import signal
import sys
import tempfile
import time
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("HARNESS_CLI_EXIT_PROCESS") != "1",
    reason="set HARNESS_CLI_EXIT_PROCESS=1 for the bounded installed-process witness",
)


@pytest.mark.asyncio
async def test_installed_daemon_client_status_exits(monkeypatch: pytest.MonkeyPatch) -> None:
    import uvicorn
    from mcp.server.fastmcp import FastMCP
    from mcp.server.transport_security import TransportSecuritySettings
    from sse_starlette.sse import AppStatus

    # [LAW:no-ambient-temporal-coupling] SSE state from another test server must
    # not change the readiness of this server in a shared pytest process.
    monkeypatch.setattr(AppStatus, "should_exit", False)

    script = Path(sys.executable).with_name("harness")
    assert script.is_file(), f"installed console script missing: {script}"
    payloads = {
        "wf-success.yaml": {
            "status": "success",
            "workflow_id": "wf-success.yaml",
            "run_id": "fx-1",
        },
        "wf-failed.yaml": {
            "status": "failed",
            "workflow_id": "wf-failed.yaml",
            "run_id": "fx-2",
            "fail_class": "FIXTURE-FAIL",
        },
        "wf-paused.yaml": {"status": "paused", "workflow_id": "wf-paused.yaml", "run_id": "fx-3"},
    }
    expected_exits = {"wf-success.yaml": 0, "wf-failed.yaml": 1, "wf-paused.yaml": 5}
    calls: list[str] = []
    server = FastMCP(
        "cli-exit-process-fixture",
        transport_security=TransportSecuritySettings(allowed_hosts=["127.0.0.1"]),
    )

    @server.tool()
    async def run_workflow(workflow_id: str) -> str:
        calls.append(workflow_id)
        return json.dumps(payloads[workflow_id])

    # [LAW:effects-at-boundaries] Child processes receive only an empty local
    # workspace and this local Unix socket; the fixture supplies all result data.
    with tempfile.TemporaryDirectory(prefix="hx") as temporary:
        base = Path(temporary)
        socket = base / "mcp.sock"
        assert len(os.fsencode(socket)) < 100
        home = base / "home"
        cwd = base / "cwd"
        home.mkdir()
        cwd.mkdir()
        environment = {
            "PATH": f"{script.parent}:/usr/bin",
            "HOME": str(home),
            "TMPDIR": str(base),
            "LANG": "C.UTF-8",
            "NO_COLOR": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1",
        }
        uv_server = uvicorn.Server(
            uvicorn.Config(server.streamable_http_app(), uds=str(socket), log_level="error")
        )
        serve_task = asyncio.create_task(uv_server.serve())
        children: list[asyncio.subprocess.Process] = []
        try:
            async with asyncio.timeout(110):
                async with asyncio.timeout(8):
                    while not uv_server.started:
                        if serve_task.done():
                            await serve_task
                            pytest.fail("fixture server exited before readiness")
                        await asyncio.sleep(0.01)
                assert socket.exists(), "fixture Unix socket was not bound"

                for workflow_id, expected_exit in expected_exits.items():
                    started = time.monotonic()
                    child = await asyncio.create_subprocess_exec(
                        str(script),
                        "run",
                        workflow_id,
                        "--daemon",
                        "--socket-path",
                        str(socket),
                        "--output",
                        "json",
                        stdin=asyncio.subprocess.DEVNULL,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=cwd,
                        env=environment,
                        start_new_session=True,
                    )
                    children.append(child)
                    try:
                        stdout, stderr = await asyncio.wait_for(child.communicate(), 30)
                    except TimeoutError:
                        try:
                            os.killpg(child.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass  # The child exited between the deadline and the signal.
                        await child.wait()
                        pytest.fail(
                            f"INCONCLUSIVE-TIMEOUT: {workflow_id} exceeded 30s; "
                            f"child pid={child.pid}, elapsed={time.monotonic() - started:.3f}s"
                        )
                    elapsed = time.monotonic() - started
                    print(
                        f"{workflow_id}: exit={child.returncode} elapsed={elapsed:.3f}s pid={child.pid}"
                    )
                    assert child.returncode == expected_exit, (workflow_id, stderr.decode())
                    assert json.loads(stdout) == payloads[workflow_id]
                    assert b"Traceback" not in stderr
                    assert stderr == b""
                    assert calls == list(expected_exits)[: len(children)]
        except TimeoutError:
            pytest.fail("INCONCLUSIVE-TIMEOUT: fixture exceeded its 110s parent cap")
        finally:
            # [LAW:no-ambient-temporal-coupling] The fixture owns every child
            # group and the server lifecycle, including assertion-failure cleanup.
            for child in children:
                if child.returncode is None:
                    try:
                        os.killpg(child.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass  # The group can vanish just before cleanup.
                    await child.wait()
            uv_server.should_exit = True
            async with asyncio.timeout(3):
                await serve_task
        assert all(child.returncode is not None for child in children)
