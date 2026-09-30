"""R-410 Docker tool execution driver tests."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Sequence
from typing import Any, cast

import pytest
from harness_as.sandbox_tier import SandboxTier
from harness_runtime.lifecycle.docker_tool_execution_driver import (
    DockerToolRunnerExecutionDriver,
    GVisorRunscToolRunnerExecutionDriver,
)
from harness_runtime.lifecycle.mcp_client_host import MCPClientHost
from harness_runtime.lifecycle.runtime_tool_dispatcher import (
    SandboxDispatchDecision,
    ToolInvocationProtocolError,
    ToolInvocationTimeoutError,
)


class _FakeProcess:
    def __init__(
        self,
        *,
        stdout: bytes,
        stderr: bytes = b"",
        returncode: int = 0,
    ) -> None:
        self._stdout = stdout
        self._stderr = stderr
        self.returncode = returncode
        self.stdin_payload: bytes | None = None

    async def communicate(self, stdin_payload: bytes) -> tuple[bytes, bytes]:
        self.stdin_payload = stdin_payload
        return self._stdout, self._stderr

    def kill(self) -> None:
        return None

    async def wait(self) -> int:
        return self.returncode


def _decision(tier: SandboxTier = SandboxTier.TIER_2_CONTAINER) -> SandboxDispatchDecision:
    return SandboxDispatchDecision(
        tier=tier,
        tech="docker",
        provider="local-docker",
        assigned_tier_reason="test",
        cost_tier_overhead_ms=0,
    )


def _gvisor_decision(tier: SandboxTier = SandboxTier.TIER_3_MICROVM) -> SandboxDispatchDecision:
    return SandboxDispatchDecision(
        tier=tier,
        tech="gvisor-runsc",
        provider="local-gvisor",
        assigned_tier_reason="test",
        cost_tier_overhead_ms=0,
    )


@pytest.mark.asyncio
async def test_docker_driver_runs_resolved_local_image_id(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[Sequence[str]] = []
    run_payloads: list[dict[str, Any]] = []

    async def fake_exec(*argv: str, **_kwargs: Any) -> _FakeProcess:
        calls.append(argv)
        if argv[:2] == ("docker", "inspect"):
            return _FakeProcess(stdout=b"sha256:resolved-local-image\n")
        assert argv[:2] == ("docker", "run")

        class _RunProcess(_FakeProcess):
            async def communicate(self, stdin_payload: bytes) -> tuple[bytes, bytes]:
                run_payloads.append(json.loads(stdin_payload.decode("utf-8")))
                return await super().communicate(stdin_payload)

        return _RunProcess(
            stdout=json.dumps(
                {
                    "content": [{"type": "text", "text": "container:ok"}],
                    "isError": False,
                }
            ).encode("utf-8")
        )

    monkeypatch.setattr(
        "harness_runtime.lifecycle.docker_tool_execution_driver.asyncio.create_subprocess_exec",
        fake_exec,
    )
    driver = DockerToolRunnerExecutionDriver(
        image="python:3.11-slim",
        command=("python", "-c", "runner"),
    )

    response = await driver.call_tool(
        mcp_client_host=cast(MCPClientHost, object()),
        sandbox_decision=_decision(),
        tool_id="echo",
        tool_args={"message": "hello"},
        idempotency_key="idem",
    )

    assert response["content"][0]["text"] == "container:ok"
    assert calls[0] == (
        "docker",
        "inspect",
        "--format",
        "{{.Id}}",
        "python:3.11-slim",
    )
    assert calls[1][:3] == ("docker", "run", "--rm")
    assert calls[1][calls[1].index("--network") + 1] == "none"
    assert calls[1][calls[1].index("-i") + 1] == "sha256:resolved-local-image"
    assert "python:3.11-slim" not in calls[1]
    assert run_payloads == [
        {
            "tool_id": "echo",
            "tool_args": {"message": "hello"},
            "idempotency_key": "idem",
            "sandbox": {
                "tier": "tier-2-container",
                "tech": "docker",
                "provider": "local-docker",
                "assigned_tier_reason": "test",
            },
        }
    ]


@pytest.mark.asyncio
async def test_cancellation_during_communicate_kills_and_reaps_process(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression guard — cancelling the CALLER while `_communicate` awaits
    the subprocess must kill + reap the process (mirroring the TimeoutError
    branch) and propagate `CancelledError`, not leave the Docker container
    running unsupervised. Cancelling the await alone does not kill the OS
    process — that's why the TimeoutError branch explicitly calls
    `proc.kill()` + `proc.wait()`; the CancelledError path needs the same."""
    kill_calls: list[str] = []
    wait_calls: list[str] = []

    class _HangingProcess(_FakeProcess):
        async def communicate(self, stdin_payload: bytes) -> tuple[bytes, bytes]:
            await asyncio.Event().wait()  # never resolves — cancelled from outside
            raise AssertionError("unreachable")

        def kill(self) -> None:
            kill_calls.append("killed")

        async def wait(self) -> int:
            wait_calls.append("waited")
            return 137

    async def fake_exec(*argv: str, **_kwargs: Any) -> _FakeProcess:
        if argv[:2] == ("docker", "inspect"):
            return _FakeProcess(stdout=b"sha256:resolved-local-image\n")
        if argv[:2] == ("docker", "rm"):
            return _FakeProcess(stdout=b"")
        assert argv[:2] == ("docker", "run")
        return _HangingProcess(stdout=b"")

    monkeypatch.setattr(
        "harness_runtime.lifecycle.docker_tool_execution_driver.asyncio.create_subprocess_exec",
        fake_exec,
    )
    driver = DockerToolRunnerExecutionDriver(
        image="python:3.11-slim",
        command=("python", "-c", "runner"),
    )

    task = asyncio.ensure_future(
        driver.call_tool(
            mcp_client_host=cast(MCPClientHost, object()),
            sandbox_decision=_decision(),
            tool_id="echo",
            tool_args={},
            idempotency_key="idem",
        )
    )
    await asyncio.sleep(0)  # let it reach the hanging communicate() await
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert kill_calls == ["killed"]
    assert wait_calls == ["waited"]


class _AlreadyReapedProcess(_FakeProcess):
    """A child asyncio's transport has already finished with.

    `Process.kill()` then raises `ProcessLookupError` (the transport's
    `_check_proc()` sees a cleared `Popen` reference); `wait()` still resolves
    immediately from the recorded return code. The `kill_calls` / `wait_calls`
    counters mirror the settled sibling `_AlreadyReapedFakeProcess` in
    `test_external_cli_provider.py`: without them a witness stays green when the
    reap call itself is deleted, since a never-entered reap path and a
    suppressed-lookup-error reap path are indistinguishable from the raised
    exception alone.
    """

    def __init__(
        self,
        *,
        stdout: bytes,
        stderr: bytes = b"",
        returncode: int = 0,
    ) -> None:
        super().__init__(stdout=stdout, stderr=stderr, returncode=returncode)
        self.kill_calls = 0
        self.wait_calls = 0

    async def communicate(self, stdin_payload: bytes) -> tuple[bytes, bytes]:
        await asyncio.Event().wait()  # never resolves
        raise AssertionError("unreachable")

    def kill(self) -> None:
        self.kill_calls += 1
        raise ProcessLookupError("child already reaped by the transport")

    async def wait(self) -> int:
        self.wait_calls += 1
        return 137


def _already_reaped_run_exec(spawned: list[_AlreadyReapedProcess]) -> Any:
    """`create_subprocess_exec` replacement that records the spawned `docker run`
    child, so a witness can assert on its reap counters afterwards."""

    async def fake_exec(*argv: str, **_kwargs: Any) -> _FakeProcess:
        if argv[:2] == ("docker", "inspect"):
            return _FakeProcess(stdout=b"sha256:resolved-local-image\n")
        if argv[:2] == ("docker", "rm"):
            return _FakeProcess(stdout=b"")
        assert argv[:2] == ("docker", "run")
        process = _AlreadyReapedProcess(stdout=b"")
        spawned.append(process)
        return process

    return fake_exec


@pytest.mark.asyncio
async def test_timeout_survives_already_reaped_child(monkeypatch: pytest.MonkeyPatch) -> None:
    """Race guard — the deadline reap must not replace the typed timeout.

    The `docker` child can exit (and its transport finish) in the window
    between the deadline firing and `proc.kill()`, at which point `kill()`
    raises `ProcessLookupError`. Unsuppressed, that would propagate instead of
    `ToolInvocationTimeoutError`, so the dispatcher's TOOL_STEP retry wrapper
    would see a raw OS error rather than a timeout.
    """
    spawned: list[_AlreadyReapedProcess] = []
    monkeypatch.setattr(
        "harness_runtime.lifecycle.docker_tool_execution_driver.asyncio.create_subprocess_exec",
        _already_reaped_run_exec(spawned),
    )
    driver = DockerToolRunnerExecutionDriver(
        image="python:3.11-slim",
        command=("python", "-c", "runner"),
        timeout_seconds=0.01,
    )

    with pytest.raises(ToolInvocationTimeoutError, match="Docker tool runner timed out"):
        await driver.call_tool(
            mcp_client_host=cast(MCPClientHost, object()),
            sandbox_decision=_decision(),
            tool_id="echo",
            tool_args={},
            idempotency_key="idem",
        )

    (process,) = spawned
    assert process.kill_calls == 1, "the reap still fires — the suppression is not a skip"
    assert process.wait_calls == 1, "and the wait still runs, so a live child is still reaped"


@pytest.mark.asyncio
async def test_cancellation_survives_already_reaped_child(monkeypatch: pytest.MonkeyPatch) -> None:
    """Race guard — the cancel-path reap must not replace the `CancelledError`.

    Same `kill()` race as the deadline path: an escaping `ProcessLookupError`
    would reclassify a shutdown cancellation as a provider failure.
    """
    spawned: list[_AlreadyReapedProcess] = []
    monkeypatch.setattr(
        "harness_runtime.lifecycle.docker_tool_execution_driver.asyncio.create_subprocess_exec",
        _already_reaped_run_exec(spawned),
    )
    driver = DockerToolRunnerExecutionDriver(
        image="python:3.11-slim",
        command=("python", "-c", "runner"),
    )

    task = asyncio.ensure_future(
        driver.call_tool(
            mcp_client_host=cast(MCPClientHost, object()),
            sandbox_decision=_decision(),
            tool_id="echo",
            tool_args={},
            idempotency_key="idem",
        )
    )
    await asyncio.sleep(0)  # let it reach the hanging communicate() await
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    (process,) = spawned
    assert process.kill_calls == 1, "the reap still fires — the suppression is not a skip"
    assert process.wait_calls == 1, "and the wait still runs, so a live child is still reaped"


@pytest.mark.asyncio
async def test_gvisor_driver_runs_with_runsc_runtime_and_tier3(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[Sequence[str]] = []
    run_payloads: list[dict[str, Any]] = []

    async def fake_exec(*argv: str, **_kwargs: Any) -> _FakeProcess:
        calls.append(argv)
        if argv[:3] == ("env", "LIMA_HOME=/tmp/lima", "limactl"):
            if argv[7] == "inspect":
                return _FakeProcess(stdout=b"sha256:gvisor-image\n")
            assert argv[7] == "run"

            class _RunProcess(_FakeProcess):
                async def communicate(self, stdin_payload: bytes) -> tuple[bytes, bytes]:
                    run_payloads.append(json.loads(stdin_payload.decode("utf-8")))
                    return await super().communicate(stdin_payload)

            return _RunProcess(
                stdout=json.dumps(
                    {
                        "content": [{"type": "text", "text": "gvisor:ok"}],
                        "isError": False,
                    }
                ).encode("utf-8")
            )
        raise AssertionError(f"unexpected argv: {argv!r}")

    monkeypatch.setattr(
        "harness_runtime.lifecycle.docker_tool_execution_driver.asyncio.create_subprocess_exec",
        fake_exec,
    )
    driver = GVisorRunscToolRunnerExecutionDriver(
        image="alpine:3.20",
        command=("sh", "-c", "runner"),
        docker_command=(
            "env",
            "LIMA_HOME=/tmp/lima",
            "limactl",
            "shell",
            "r411-gvisor",
            "sudo",
            "docker",
        ),
    )

    response = await driver.call_tool(
        mcp_client_host=cast(MCPClientHost, object()),
        sandbox_decision=_gvisor_decision(),
        tool_id="echo",
        tool_args={"message": "hello"},
        idempotency_key="idem",
    )

    assert response["content"][0]["text"] == "gvisor:ok"
    assert calls[0] == (
        "env",
        "LIMA_HOME=/tmp/lima",
        "limactl",
        "shell",
        "r411-gvisor",
        "sudo",
        "docker",
        "inspect",
        "--format",
        "{{.Id}}",
        "alpine:3.20",
    )
    assert calls[1][:9] == (
        "env",
        "LIMA_HOME=/tmp/lima",
        "limactl",
        "shell",
        "r411-gvisor",
        "sudo",
        "docker",
        "run",
        "--rm",
    )
    assert calls[1][calls[1].index("--network") + 1] == "none"
    assert calls[1][calls[1].index("--runtime") + 1] == "runsc"
    assert run_payloads[0]["sandbox"] == {
        "tier": "tier-3-microvm",
        "tech": "gvisor-runsc",
        "provider": "local-gvisor",
        "assigned_tier_reason": "test",
    }


@pytest.mark.asyncio
async def test_gvisor_driver_rejects_non_tier3_decision() -> None:
    driver = GVisorRunscToolRunnerExecutionDriver(
        image="alpine:3.20",
        command=("sh", "-c", "runner"),
    )

    with pytest.raises(ToolInvocationProtocolError, match="tier-3-microvm"):
        await driver.call_tool(
            mcp_client_host=cast(MCPClientHost, object()),
            sandbox_decision=_gvisor_decision(SandboxTier.TIER_2_CONTAINER),
            tool_id="echo",
            tool_args={},
            idempotency_key="idem",
        )


@pytest.mark.asyncio
async def test_docker_driver_resolves_tag_from_local_image_listing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[Sequence[str]] = []

    async def fake_exec(*argv: str, **_kwargs: Any) -> _FakeProcess:
        calls.append(argv)
        if argv[:2] == ("docker", "inspect"):
            return _FakeProcess(stdout=b"", stderr=b"no such object", returncode=1)
        if argv[:2] == ("docker", "images"):
            return _FakeProcess(stdout=b"alpine:latest alpine-id\npython:3.11-slim python-id\n")
        assert argv[:2] == ("docker", "run")
        return _FakeProcess(
            stdout=json.dumps(
                {
                    "content": [{"type": "text", "text": "container:fallback"}],
                    "isError": False,
                }
            ).encode("utf-8")
        )

    monkeypatch.setattr(
        "harness_runtime.lifecycle.docker_tool_execution_driver.asyncio.create_subprocess_exec",
        fake_exec,
    )
    driver = DockerToolRunnerExecutionDriver(
        image="python:3.11-slim",
        command=("python", "-c", "runner"),
    )

    response = await driver.call_tool(
        mcp_client_host=cast(MCPClientHost, object()),
        sandbox_decision=_decision(),
        tool_id="echo",
        tool_args={"message": "hello"},
        idempotency_key="idem",
    )

    assert response["content"][0]["text"] == "container:fallback"
    assert calls[1] == (
        "docker",
        "images",
        "--format",
        "{{.Repository}}:{{.Tag}} {{.ID}}",
    )
    assert calls[2][calls[2].index("-i") + 1] == "python-id"


@pytest.mark.asyncio
async def test_docker_driver_fails_when_image_is_not_local(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[Sequence[str]] = []

    async def fake_exec(*argv: str, **_kwargs: Any) -> _FakeProcess:
        calls.append(argv)
        if argv[:2] == ("docker", "images"):
            return _FakeProcess(stdout=b"alpine:latest alpine-id\n")
        return _FakeProcess(stdout=b"", stderr=b"No such image", returncode=1)

    monkeypatch.setattr(
        "harness_runtime.lifecycle.docker_tool_execution_driver.asyncio.create_subprocess_exec",
        fake_exec,
    )
    driver = DockerToolRunnerExecutionDriver(
        image="missing:latest",
        command=("python", "-c", "runner"),
    )

    with pytest.raises(ToolInvocationProtocolError, match="not available locally"):
        await driver.call_tool(
            mcp_client_host=cast(MCPClientHost, object()),
            sandbox_decision=_decision(),
            tool_id="echo",
            tool_args={},
            idempotency_key="idem",
        )

    assert len(calls) == 2
    assert calls[0][-1] == "missing:latest"
    assert calls[1][:2] == ("docker", "images")


@pytest.mark.asyncio
async def test_each_run_gets_a_distinct_non_user_derived_container_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import re

    runs: list[tuple[str, ...]] = []

    async def fake_exec(*argv: str, **_kwargs: Any) -> _FakeProcess:
        if argv[:2] == ("docker", "inspect"):
            return _FakeProcess(stdout=b"sha256:local\n")
        assert argv[:2] == ("docker", "run")
        runs.append(argv)
        return _FakeProcess(stdout=b"{}")

    monkeypatch.setattr(
        "harness_runtime.lifecycle.docker_tool_execution_driver.asyncio.create_subprocess_exec",
        fake_exec,
    )
    driver = DockerToolRunnerExecutionDriver(image="image:tag", command=("runner",))
    for _ in range(2):
        await driver.call_tool(
            mcp_client_host=cast(MCPClientHost, object()),
            sandbox_decision=_decision(),
            tool_id="echo",
            tool_args={},
            idempotency_key="user-supplied-secret",
        )
    names = [argv[argv.index("--name") + 1] for argv in runs]
    assert names[0] != names[1]
    assert all(re.fullmatch(r"harness-tool-[0-9a-f]{32}", name) for name in names)
    assert all("user-supplied-secret" not in name for name in names)
    assert all(argv[argv.index("--label") + 1] == "io.arhugula.harness.tool-run=1" for argv in runs)
    assert all("--rm" in argv and "sha256:local" in argv for argv in runs)


class _InterruptedRunProcess(_FakeProcess):
    def __init__(self, events: list[str], started: asyncio.Event) -> None:
        super().__init__(stdout=b"")
        self.events = events
        self.started = started

    async def communicate(self, stdin_payload: bytes) -> tuple[bytes, bytes]:
        self.started.set()
        await asyncio.Event().wait()
        raise AssertionError("unreachable")

    def kill(self) -> None:
        self.events.append("run-kill")

    async def wait(self) -> int:
        self.events.append("run-wait")
        return 137


async def _interrupted_case(
    monkeypatch: pytest.MonkeyPatch,
    *,
    cancel: bool,
    rm_result: _FakeProcess | BaseException,
    prefix: tuple[str, ...] = ("docker",),
) -> tuple[list[tuple[str, ...]], list[str], BaseException]:
    calls: list[tuple[str, ...]] = []
    events: list[str] = []
    started = asyncio.Event()

    async def fake_exec(*argv: str, **_kwargs: Any) -> _FakeProcess:
        calls.append(argv)
        operation = argv[len(prefix)]
        if operation == "inspect":
            return _FakeProcess(stdout=b"sha256:local\n")
        if operation == "run":
            return _InterruptedRunProcess(events, started)
        assert operation == "rm"
        events.append("rm-spawn")
        if isinstance(rm_result, BaseException):
            raise rm_result
        rm_result._stderr = rm_result._stderr.replace(b"NAME", argv[-1].encode())
        return rm_result

    monkeypatch.setattr(
        "harness_runtime.lifecycle.docker_tool_execution_driver.asyncio.create_subprocess_exec",
        fake_exec,
    )
    driver = DockerToolRunnerExecutionDriver(
        image="image:tag",
        command=("runner",),
        docker_command=prefix,
        timeout_seconds=0.01,
    )
    task = asyncio.create_task(
        driver.call_tool(
            mcp_client_host=cast(MCPClientHost, object()),
            sandbox_decision=_decision(),
            tool_id="echo",
            tool_args={},
            idempotency_key="idem",
        )
    )
    await started.wait()
    if cancel:
        task.cancel()
    try:
        await task
    except BaseException as exc:
        return calls, events, exc
    raise AssertionError("interrupted run unexpectedly succeeded")


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel", [False, True])
async def test_timeout_and_cancel_reap_then_remove_exact_container(
    monkeypatch: pytest.MonkeyPatch,
    cancel: bool,
) -> None:
    calls, events, exc = await _interrupted_case(
        monkeypatch,
        cancel=cancel,
        rm_result=_FakeProcess(stdout=b""),
        prefix=("env", "LIMA_HOME=/tmp/lima", "limactl", "docker"),
    )
    run = calls[1]
    name = run[run.index("--name") + 1]
    assert calls[2] == ("env", "LIMA_HOME=/tmp/lima", "limactl", "docker", "rm", "-f", name)
    assert events == ["run-kill", "run-wait", "rm-spawn"]
    assert isinstance(exc, asyncio.CancelledError if cancel else ToolInvocationTimeoutError)


@pytest.mark.asyncio
async def test_no_such_container_is_clean_after_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    calls, _events, exc = await _interrupted_case(
        monkeypatch,
        cancel=False,
        rm_result=_FakeProcess(
            stdout=b"",
            stderr=b"Error response from daemon: No such container: NAME",
            returncode=1,
        ),
    )
    assert len(calls) == 3
    assert isinstance(exc, ToolInvocationTimeoutError)


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["nonzero", "spawn", "timeout", "io"])
@pytest.mark.parametrize("cancel", [False, True])
async def test_uncertain_cleanup_preserves_cancellation_or_blocks_timeout_retry(
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
    cancel: bool,
) -> None:
    from harness_runtime.lifecycle.docker_tool_execution_driver import ToolContainerCleanupError

    if failure == "spawn":
        rm_result: _FakeProcess | BaseException = OSError("rm unavailable")
    elif failure == "timeout":
        monkeypatch.setattr(
            "harness_runtime.lifecycle.docker_tool_execution_driver.CONTAINER_CLEANUP_TIMEOUT_SECONDS",
            0.01,
        )

        class _HangingRm(_FakeProcess):
            async def communicate(self, stdin_payload: bytes) -> tuple[bytes, bytes]:
                await asyncio.Event().wait()
                raise AssertionError("unreachable")

        rm_result = _HangingRm(stdout=b"")
    elif failure == "io":

        class _BrokenRm(_FakeProcess):
            async def communicate(self, stdin_payload: bytes) -> tuple[bytes, bytes]:
                raise OSError("cleanup pipe broke")

        rm_result = _BrokenRm(stdout=b"")
    else:
        rm_result = _FakeProcess(stdout=b"", stderr=b"unexpected output\n" * 10000, returncode=2)
    calls, events, exc = await _interrupted_case(
        monkeypatch,
        cancel=cancel,
        rm_result=rm_result,
    )
    if cancel:
        assert isinstance(exc, asyncio.CancelledError)
        assert any("cleanup uncertain" in note for note in exc.__notes__)
        assert all("unexpected output" not in note for note in exc.__notes__)
    else:
        assert isinstance(exc, ToolContainerCleanupError)
        assert isinstance(exc, ToolInvocationProtocolError)
    assert len(calls) == 3
    assert events[:2] == ["run-kill", "run-wait"]
    assert len(str(exc)) <= 400
    name = calls[1][calls[1].index("--name") + 1]
    assert calls[2] == ("docker", "rm", "-f", name)


@pytest.mark.asyncio
async def test_second_cancellation_waits_for_container_cleanup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    run_started = asyncio.Event()
    rm_started = asyncio.Event()
    release_rm = asyncio.Event()
    events: list[str] = []
    calls: list[tuple[str, ...]] = []

    class _HoldingRm(_FakeProcess):
        async def communicate(self, stdin_payload: bytes) -> tuple[bytes, bytes]:
            rm_started.set()
            await release_rm.wait()
            events.append("rm-finished")
            return b"", b""

    async def fake_exec(*argv: str, **_kwargs: Any) -> _FakeProcess:
        calls.append(argv)
        if argv[:2] == ("docker", "inspect"):
            return _FakeProcess(stdout=b"sha256:local\n")
        if argv[:2] == ("docker", "run"):
            return _InterruptedRunProcess(events, run_started)
        assert argv[:2] == ("docker", "rm")
        return _HoldingRm(stdout=b"")

    monkeypatch.setattr(
        "harness_runtime.lifecycle.docker_tool_execution_driver.asyncio.create_subprocess_exec",
        fake_exec,
    )
    driver = DockerToolRunnerExecutionDriver(image="image:tag", command=("runner",))
    task = asyncio.create_task(
        driver.call_tool(
            mcp_client_host=cast(MCPClientHost, object()),
            sandbox_decision=_decision(),
            tool_id="echo",
            tool_args={},
            idempotency_key="idem",
        )
    )
    await run_started.wait()
    task.cancel()
    await rm_started.wait()
    task.cancel()
    await asyncio.sleep(0)
    assert not task.done(), "a second cancellation must wait for rm to finish"
    release_rm.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert events == ["run-kill", "run-wait", "rm-finished"]
    name = calls[1][calls[1].index("--name") + 1]
    assert calls[2] == ("docker", "rm", "-f", name)


@pytest.mark.asyncio
@pytest.mark.parametrize("rm_fails", [False, True])
async def test_timeout_then_cancellation_waits_for_rm_and_keeps_cancellation(
    monkeypatch: pytest.MonkeyPatch,
    rm_fails: bool,
) -> None:
    run_started = asyncio.Event()
    rm_started = asyncio.Event()
    release_rm = asyncio.Event()
    calls: list[tuple[str, ...]] = []

    class _HoldingRm(_FakeProcess):
        async def communicate(self, stdin_payload: bytes) -> tuple[bytes, bytes]:
            rm_started.set()
            await release_rm.wait()
            return b"", b"secret-looking stderr" if rm_fails else b""

    async def fake_exec(*argv: str, **_kwargs: Any) -> _FakeProcess:
        calls.append(argv)
        if argv[:2] == ("docker", "inspect"):
            return _FakeProcess(stdout=b"sha256:local\n")
        if argv[:2] == ("docker", "run"):
            return _InterruptedRunProcess([], run_started)
        assert argv[:2] == ("docker", "rm")
        return _HoldingRm(stdout=b"", returncode=2 if rm_fails else 0)

    monkeypatch.setattr(
        "harness_runtime.lifecycle.docker_tool_execution_driver.asyncio.create_subprocess_exec",
        fake_exec,
    )
    driver = DockerToolRunnerExecutionDriver(
        image="image:tag",
        command=("runner",),
        timeout_seconds=0.01,
    )
    task = asyncio.create_task(
        driver.call_tool(
            mcp_client_host=cast(MCPClientHost, object()),
            sandbox_decision=_decision(),
            tool_id="echo",
            tool_args={},
            idempotency_key="idem",
        )
    )
    await run_started.wait()
    await rm_started.wait()
    task.cancel()
    await asyncio.sleep(0)
    assert not task.done(), "cancellation must not abandon the in-flight rm"
    release_rm.set()
    with pytest.raises(asyncio.CancelledError) as raised:
        await task
    name = calls[1][calls[1].index("--name") + 1]
    assert calls[2] == ("docker", "rm", "-f", name)
    notes = getattr(raised.value, "__notes__", [])
    assert any("cleanup uncertain" in note for note in notes) is rm_fails
    assert all("secret-looking stderr" not in note for note in notes)


@pytest.mark.asyncio
async def test_cancel_during_run_spawn_removes_exact_name_then_propagates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    spawn_started = asyncio.Event()
    rm_started = asyncio.Event()
    release_rm = asyncio.Event()
    calls: list[tuple[str, ...]] = []

    class _HoldingRm(_FakeProcess):
        async def communicate(self, stdin_payload: bytes) -> tuple[bytes, bytes]:
            rm_started.set()
            await release_rm.wait()
            return b"", b""

    async def fake_exec(*argv: str, **_kwargs: Any) -> _FakeProcess:
        calls.append(argv)
        if argv[:2] == ("docker", "inspect"):
            return _FakeProcess(stdout=b"sha256:local\n")
        if argv[:2] == ("docker", "run"):
            spawn_started.set()
            await asyncio.Event().wait()
            raise AssertionError("unreachable")
        assert argv[:2] == ("docker", "rm")
        return _HoldingRm(stdout=b"")

    monkeypatch.setattr(
        "harness_runtime.lifecycle.docker_tool_execution_driver.asyncio.create_subprocess_exec",
        fake_exec,
    )
    driver = DockerToolRunnerExecutionDriver(image="image:tag", command=("runner",))
    task = asyncio.create_task(
        driver.call_tool(
            mcp_client_host=cast(MCPClientHost, object()),
            sandbox_decision=_decision(),
            tool_id="echo",
            tool_args={},
            idempotency_key="idem",
        )
    )
    await spawn_started.wait()
    task.cancel()
    await rm_started.wait()
    task.cancel()
    await asyncio.sleep(0)
    assert not task.done(), "second cancellation must wait for rm after spawn cancellation"
    release_rm.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    name = calls[1][calls[1].index("--name") + 1]
    assert calls[2] == ("docker", "rm", "-f", name)
