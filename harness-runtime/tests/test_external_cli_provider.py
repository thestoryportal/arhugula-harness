"""Tests for subscription-backed external CLI provider adapters (R-CLI-1)."""

from __future__ import annotations

import sys
from collections.abc import Callable
from dataclasses import dataclass

import pytest
from harness_runtime.lifecycle.external_cli_provider import (
    AsyncioSubprocessRunner,
    CLIProcessResult,
    ExternalCLICommandError,
    ExternalCLINotAuthenticatedError,
    ExternalCLIOutputError,
    ExternalCLIProcessTimeout,
    RecordingSubprocessRunner,
    construct_antigravity_cli_adapter,
    construct_claude_code_cli_adapter,
    construct_codex_cli_adapter,
    construct_gemini_cli_adapter,
    construct_generic_command_cli_adapter,
)
from harness_runtime.types import ExternalCLIProviderConfig


@dataclass
class _FakeRunner:
    results: list[CLIProcessResult]
    calls: list[tuple[tuple[str, ...], str, float]]

    async def run(
        self,
        argv: tuple[str, ...],
        *,
        stdin: str,
        timeout_seconds: float,
        on_wire: Callable[[], None] | None = None,
    ) -> CLIProcessResult:
        # Models a successful spawn: the wire notification precedes the
        # recorded payload handover, as in `AsyncioSubprocessRunner` (B-87).
        if on_wire is not None:
            on_wire()
        self.calls.append((argv, stdin, timeout_seconds))
        return self.results.pop(0)


def _config(**overrides: object) -> ExternalCLIProviderConfig:
    return ExternalCLIProviderConfig(
        provider="claude_code",
        kind="claude-code",
        command="claude",
        timeout_seconds=42.0,
        **overrides,
    )


def _provider_config(
    provider: str,
    kind: str,
    command: str,
    **overrides: object,
) -> ExternalCLIProviderConfig:
    return ExternalCLIProviderConfig(
        provider=provider,
        kind=kind,
        command=command,
        timeout_seconds=42.0,
        **overrides,
    )


@pytest.mark.asyncio
async def test_construct_claude_adapter_checks_auth_without_token_access() -> None:
    runner = _FakeRunner(
        results=[CLIProcessResult(exit_code=0, stdout='{"loggedIn": true}', stderr="")],
        calls=[],
    )

    adapter = await construct_claude_code_cli_adapter(_config(), runner=runner)

    assert adapter.provider_name == "claude_code"
    assert runner.calls == [
        (("claude", "auth", "status", "--json"), "", 42.0),
    ]


@pytest.mark.asyncio
async def test_construct_claude_adapter_rejects_unauthenticated_cli() -> None:
    runner = _FakeRunner(
        results=[CLIProcessResult(exit_code=0, stdout='{"loggedIn": false}', stderr="")],
        calls=[],
    )

    with pytest.raises(ExternalCLINotAuthenticatedError):
        await construct_claude_code_cli_adapter(_config(), runner=runner)


@pytest.mark.asyncio
async def test_claude_dispatch_uses_argv_and_stdin_for_text_only_prompt() -> None:
    runner = _FakeRunner(
        results=[
            CLIProcessResult(exit_code=0, stdout='{"loggedIn": true}', stderr=""),
            CLIProcessResult(exit_code=0, stdout='{"result": "OK"}', stderr=""),
        ],
        calls=[],
    )
    adapter = await construct_claude_code_cli_adapter(_config(), runner=runner)

    result = await adapter.dispatch_text(model="sonnet", prompt="Reply OK")

    assert result.text == "OK"
    argv, stdin, timeout = runner.calls[1]
    assert argv == (
        "claude",
        "--print",
        "--output-format",
        "json",
        "--input-format",
        "text",
        "--no-session-persistence",
        "--tools",
        "",
        "--permission-mode",
        "dontAsk",
        "--model",
        "sonnet",
    )
    assert stdin == "Reply OK"
    assert timeout == 42.0


@pytest.mark.asyncio
async def test_claude_dispatch_surfaces_nonzero_exit_with_stderr() -> None:
    runner = _FakeRunner(
        results=[
            CLIProcessResult(exit_code=0, stdout='{"loggedIn": true}', stderr=""),
            CLIProcessResult(exit_code=2, stdout="", stderr="boom"),
        ],
        calls=[],
    )
    adapter = await construct_claude_code_cli_adapter(_config(), runner=runner)

    with pytest.raises(ExternalCLICommandError, match="boom"):
        await adapter.dispatch_text(model="sonnet", prompt="Reply OK")


@pytest.mark.asyncio
async def test_recording_runner_never_accepts_shell_execution() -> None:
    runner = RecordingSubprocessRunner(
        [CLIProcessResult(exit_code=0, stdout='{"loggedIn": true}', stderr="")]
    )

    await runner.run(("claude", "auth", "status", "--json"), stdin="", timeout_seconds=1.0)

    assert runner.calls == [(("claude", "auth", "status", "--json"), "", 1.0)]


@pytest.mark.asyncio
async def test_claude_dispatch_timeout_is_typed() -> None:
    class _TimeoutRunner:
        async def run(
            self,
            argv: tuple[str, ...],
            *,
            stdin: str,
            timeout_seconds: float,
            on_wire: Callable[[], None] | None = None,
        ) -> CLIProcessResult:
            _ = argv, stdin, timeout_seconds
            # A timeout is POST-wire — the process existed and may have read
            # the payload — so the notification fires before the raise (B-87).
            if on_wire is not None:
                on_wire()
            raise ExternalCLIProcessTimeout("claude", 1.0)

    adapter = await construct_claude_code_cli_adapter(
        _config(auth_check=False),
        runner=_TimeoutRunner(),
    )

    with pytest.raises(ExternalCLIProcessTimeout):
        await adapter.dispatch_text(model="sonnet", prompt="Reply OK")


@pytest.mark.asyncio
async def test_construct_codex_adapter_checks_login_status_without_token_access() -> None:
    runner = _FakeRunner(
        results=[CLIProcessResult(exit_code=0, stdout="Logged in using ChatGPT\n", stderr="")],
        calls=[],
    )

    adapter = await construct_codex_cli_adapter(
        _provider_config("codex", "codex", "codex"),
        runner=runner,
    )

    assert adapter.provider_name == "codex"
    assert runner.calls == [(("codex", "login", "status"), "", 42.0)]


@pytest.mark.asyncio
async def test_codex_dispatch_uses_ephemeral_jsonl_stdin_and_extracts_agent_message() -> None:
    runner = _FakeRunner(
        results=[
            CLIProcessResult(exit_code=0, stdout="Logged in using ChatGPT\n", stderr=""),
            CLIProcessResult(
                exit_code=0,
                stdout=(
                    '{"type":"thread.started","thread_id":"t"}\n'
                    '{"type":"item.completed","item":{"type":"agent_message","text":"OK"}}\n'
                    '{"type":"turn.completed","usage":{"input_tokens":1}}\n'
                ),
                stderr="",
            ),
        ],
        calls=[],
    )
    adapter = await construct_codex_cli_adapter(
        _provider_config("codex", "codex", "codex"),
        runner=runner,
    )

    result = await adapter.dispatch_text(model="gpt-5", prompt="Reply OK")

    assert result.text == "OK"
    argv, stdin, timeout = runner.calls[1]
    assert argv == (
        "codex",
        "exec",
        "--json",
        "--ephemeral",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "-m",
        "gpt-5",
        "-",
    )
    assert stdin == "Reply OK"
    assert timeout == 42.0


@pytest.mark.asyncio
async def test_construct_antigravity_adapter_checks_models_without_token_access() -> None:
    runner = _FakeRunner(
        results=[
            CLIProcessResult(
                exit_code=0,
                stdout="Gemini 3.5 Flash (Low)\nClaude Sonnet 4.6 (Thinking)\n",
                stderr="",
            )
        ],
        calls=[],
    )

    adapter = await construct_antigravity_cli_adapter(
        _provider_config("antigravity", "antigravity", "agy"),
        runner=runner,
    )

    assert adapter.provider_name == "antigravity"
    assert runner.calls == [(("agy", "models"), "", 42.0)]


@pytest.mark.asyncio
async def test_antigravity_dispatch_uses_print_mode_and_extracts_stdout() -> None:
    runner = _FakeRunner(
        results=[
            CLIProcessResult(exit_code=0, stdout="Gemini 3.5 Flash (Low)\n", stderr=""),
            CLIProcessResult(exit_code=0, stdout="OK\n", stderr=""),
        ],
        calls=[],
    )
    adapter = await construct_antigravity_cli_adapter(
        _provider_config("antigravity", "antigravity", "agy"),
        runner=runner,
    )

    result = await adapter.dispatch_text(
        model="Gemini 3.5 Flash (Low)",
        prompt="Reply OK",
    )

    assert result.text == "OK"
    argv, stdin, timeout = runner.calls[1]
    assert argv == (
        "agy",
        "--print",
        "Reply OK",
        "--model",
        "Gemini 3.5 Flash (Low)",
        "--print-timeout",
        "42s",
        "--sandbox",
    )
    assert stdin == ""
    assert timeout == 42.0


@pytest.mark.asyncio
async def test_gemini_dispatch_uses_headless_text_prompt_skip_trust_and_extracts_stdout() -> None:
    runner = _FakeRunner(
        results=[CLIProcessResult(exit_code=0, stdout="OK\n", stderr="")],
        calls=[],
    )
    adapter = await construct_gemini_cli_adapter(
        _provider_config("gemini", "gemini", "gemini", auth_check=False),
        runner=runner,
    )

    result = await adapter.dispatch_text(model="gemini-2.5-flash", prompt="Reply OK")

    assert result.text == "OK"
    assert runner.calls == [
        (
            (
                "gemini",
                "--skip-trust",
                "-m",
                "gemini-2.5-flash",
                "-p",
                "Reply OK",
            ),
            "",
            42.0,
        )
    ]


@pytest.mark.asyncio
async def test_generic_command_adapter_uses_configured_templates_and_stdin() -> None:
    runner = _FakeRunner(
        results=[
            CLIProcessResult(exit_code=0, stdout="authenticated\n", stderr=""),
            CLIProcessResult(exit_code=0, stdout='{"response": "OK"}', stderr=""),
        ],
        calls=[],
    )
    adapter = await construct_generic_command_cli_adapter(
        _provider_config(
            "local_llm",
            "generic-command",
            "my-llm",
            args=("--model", "{model}", "--json"),
            auth_args=("auth", "status"),
            response_format="json",
        ),
        runner=runner,
    )

    result = await adapter.dispatch_text(model="demo-model", prompt="Reply OK")

    assert result.text == "OK"
    assert runner.calls == [
        (("my-llm", "auth", "status"), "", 42.0),
        (("my-llm", "--model", "demo-model", "--json"), "Reply OK", 42.0),
    ]


@pytest.mark.asyncio
async def test_generic_command_notifies_the_wire_only_after_argv_validation() -> None:
    """B-87 (codex R2 [P2]) — `on_wire` is the caller's "did anything leave the
    process?" boundary, so it must fire AFTER `_render_argv_templates` and
    BEFORE `runner.run`. A `{prompt}` template under the default stdin
    transport is a config the constructor accepts and the adapter rejects at
    dispatch, with zero subprocess calls: the notification must not have fired.
    """
    runner = _FakeRunner(
        results=[CLIProcessResult(exit_code=0, stdout="OK\n", stderr="")],
        calls=[],
    )
    adapter = await construct_generic_command_cli_adapter(
        _provider_config(
            "local_llm",
            "generic-command",
            "my-llm",
            args=("--prompt", "{prompt}"),
            auth_check=False,
        ),
        runner=runner,
    )
    notified: list[int] = []

    with pytest.raises(ExternalCLIOutputError, match="prompt_transport"):
        await adapter.dispatch_text(
            model="demo-model",
            prompt="Reply OK",
            on_wire=lambda: notified.append(len(runner.calls)),
        )

    assert notified == [], "the argv template was rejected before any subprocess ran"
    assert runner.calls == []


@pytest.mark.asyncio
async def test_generic_command_notifies_the_wire_before_the_subprocess_runs() -> None:
    """B-87 ordering guard's other half — a notification placed after the
    payload handover would demote a real subprocess failure to a pre-wire one,
    so the callback must fire with the handover still ahead of it. The adapter
    now delegates the firing to the runner (codex R3 [P2-1]); `_FakeRunner`
    keeps the real runner's ordering (spawn, notify, hand over)."""
    runner = _FakeRunner(
        results=[CLIProcessResult(exit_code=0, stdout="OK\n", stderr="")],
        calls=[],
    )
    adapter = await construct_generic_command_cli_adapter(
        _provider_config(
            "local_llm",
            "generic-command",
            "my-llm",
            args=("--model", "{model}"),
            auth_check=False,
        ),
        runner=runner,
    )
    notified: list[int] = []

    result = await adapter.dispatch_text(
        model="demo-model",
        prompt="Reply OK",
        on_wire=lambda: notified.append(len(runner.calls)),
    )

    assert result.text == "OK"
    assert notified == [0], "fired exactly once, with the payload handover still ahead of it"
    assert runner.calls == [(("my-llm", "--model", "demo-model"), "Reply OK", 42.0)]


@pytest.mark.asyncio
async def test_asyncio_runner_does_not_notify_the_wire_when_the_spawn_fails() -> None:
    """B-87 (codex R3 [P2-1]) — "reached the wire" means a CHILD PROCESS EXISTS
    that can observe the payload. A command that cannot be spawned never
    reaches it: nothing left the runtime, so a notification fired before
    `create_subprocess_exec` would claim the prompt was seen by a process that
    was never created. The REAL runner is under test here because the ordering
    in question is `create_subprocess_exec`'s own."""
    runner = AsyncioSubprocessRunner()
    notified: list[str] = []

    with pytest.raises(ExternalCLICommandError, match="127"):
        await runner.run(
            ("harness-b87-command-that-does-not-exist",),
            stdin="Reply OK",
            timeout_seconds=30.0,
            on_wire=lambda: notified.append("fired"),
        )

    assert notified == [], "no child process existed, so nothing could have seen the prompt"


@pytest.mark.asyncio
async def test_asyncio_runner_notifies_the_wire_once_the_process_exists() -> None:
    """The positive control for the boundary above — a spawn that SUCCEEDS
    fires the notification exactly once, and everything from the stdin write
    onward is post-wire."""
    runner = AsyncioSubprocessRunner()
    notified: list[str] = []

    result = await runner.run(
        (sys.executable, "-c", "import sys; sys.stdout.write(sys.stdin.read())"),
        stdin="Reply OK",
        timeout_seconds=30.0,
        on_wire=lambda: notified.append("fired"),
    )

    assert result.exit_code == 0
    assert result.stdout == "Reply OK"
    assert notified == ["fired"]


@pytest.mark.asyncio
async def test_gemini_auth_probe_nonzero_exit_rejects_construction() -> None:
    """G4 (PR #1137 follow-up) — the configured-auth-command probe's
    nonzero-exit branch had no CI witness, so both live auth gates were
    falsely-green-capable."""
    runner = _FakeRunner(
        results=[CLIProcessResult(exit_code=1, stdout="", stderr="gemini probe refused: no creds")],
        calls=[],
    )

    with pytest.raises(ExternalCLINotAuthenticatedError, match="gemini probe refused: no creds"):
        await construct_gemini_cli_adapter(
            _provider_config(
                "gemini",
                "gemini",
                "gemini",
                auth_check=True,
                auth_args=("--skip-trust", "-p", "Reply with the single word OK."),
            ),
            runner=runner,
        )

    assert runner.calls == [
        (("gemini", "--skip-trust", "-p", "Reply with the single word OK."), "", 42.0),
    ]


@pytest.mark.asyncio
async def test_gemini_auth_check_without_auth_args_raises_before_any_spawn() -> None:
    """G4 — ``auth_check=true`` with no declared ``auth_args`` must raise
    before the probe is ever spawned."""
    runner = _FakeRunner(results=[], calls=[])

    with pytest.raises(
        ExternalCLINotAuthenticatedError,
        match="Gemini CLI auth_check=true requires auth_args",
    ):
        await construct_gemini_cli_adapter(
            _provider_config("gemini", "gemini", "gemini", auth_check=True),
            runner=runner,
        )

    assert runner.calls == []


@pytest.mark.asyncio
async def test_generic_command_auth_probe_nonzero_exit_rejects_construction() -> None:
    """G4 — the generic-command standing probe's nonzero-exit branch; only the
    exit-0 happy path was covered."""
    runner = _FakeRunner(
        results=[CLIProcessResult(exit_code=3, stdout="", stderr="local llm login required")],
        calls=[],
    )

    with pytest.raises(ExternalCLINotAuthenticatedError, match="local llm login required"):
        await construct_generic_command_cli_adapter(
            _provider_config(
                "local_llm",
                "generic-command",
                "my-llm",
                auth_args=("auth", "status"),
            ),
            runner=runner,
        )

    assert runner.calls == [(("my-llm", "auth", "status"), "", 42.0)]


@pytest.mark.asyncio
async def test_generic_command_auth_check_without_auth_args_raises_before_any_spawn() -> None:
    """G4 — the generic-command half of the ``requires auth_args`` branch,
    carrying its own provider label."""
    runner = _FakeRunner(results=[], calls=[])

    with pytest.raises(
        ExternalCLINotAuthenticatedError,
        match="generic external CLI auth_check=true requires auth_args",
    ):
        await construct_generic_command_cli_adapter(
            _provider_config("local_llm", "generic-command", "my-llm"),
            runner=runner,
        )

    assert runner.calls == []
