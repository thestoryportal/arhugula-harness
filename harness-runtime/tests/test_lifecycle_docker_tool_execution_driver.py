"""R-410 Docker tool execution driver tests."""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any, cast

import pytest
from harness_as.sandbox_tier import SandboxTier
from harness_runtime.lifecycle.docker_tool_execution_driver import (
    DockerToolRunnerExecutionDriver,
)
from harness_runtime.lifecycle.mcp_client_host import MCPClientHost
from harness_runtime.lifecycle.runtime_tool_dispatcher import (
    SandboxDispatchDecision,
    ToolInvocationProtocolError,
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
    assert calls[1][:7] == (
        "docker",
        "run",
        "--rm",
        "--network",
        "none",
        "-i",
        "sha256:resolved-local-image",
    )
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
    assert calls[2][6] == "python-id"


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
