"""Tests for subscription-backed external CLI provider adapters (R-CLI-1)."""

from __future__ import annotations

import asyncio
import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

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
async def test_asyncio_runner_reaps_the_child_when_the_wire_callback_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """B-87 (codex R7 [P2-2]) — a raising observer must not leak the child.

    The notification fires after `create_subprocess_exec` succeeds, so an
    exception out of it unwinds past the `communicate` block whose timeout path
    is the only other place this process is reaped. Without the cleanup guard
    the long-lived child below survives the raise; repeated observer failures
    would leak one running CLI process each. A real child is used because the
    property under test — that it is actually dead — is only observable on one."""

    class _ObserverFailure(RuntimeError):
        pass

    spawned: list[asyncio.subprocess.Process] = []
    real_create = asyncio.create_subprocess_exec

    async def _recording_create(*argv: Any, **kwargs: Any) -> asyncio.subprocess.Process:
        process = await real_create(*argv, **kwargs)
        spawned.append(process)
        return process

    monkeypatch.setattr(asyncio, "create_subprocess_exec", _recording_create)

    runner = AsyncioSubprocessRunner()

    def _fail() -> None:
        raise _ObserverFailure("observer exploded")

    try:
        with pytest.raises(_ObserverFailure):
            await runner.run(
                (sys.executable, "-c", "import time; time.sleep(300)"),
                stdin="",
                timeout_seconds=30.0,
                on_wire=_fail,
            )

        assert len(spawned) == 1, "the spawn itself succeeded — the raise is the observer's"
        assert spawned[0].returncode is not None, (
            "the child outlived the failed notification: a leaked CLI process"
        )
    finally:
        # Belt-and-braces so a regression (or a mutation probe) cannot leave a
        # 300-second sleeper behind.
        for process in spawned:
            if process.returncode is None:  # pragma: no cover - only on regression
                process.kill()
                await process.wait()


@pytest.mark.asyncio
async def test_asyncio_runner_reaps_the_child_when_the_run_is_cancelled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """B-87 residual — a cancellation mid-`communicate` must not leak the child.

    The timeout path and the R7 observer guard are the only other reap sites, so
    a `CancelledError` delivered while awaiting the child unwinds past both and
    leaves the CLI running. Cancellation is not exotic here: every dispatch runs
    under a caller-owned task that a shutdown, a `wait_for` deadline one level
    up, or a task-group failure can cancel. As with the observer guard, a real
    child is used because the property under test — that it is actually dead —
    is only observable on one."""
    spawned: list[asyncio.subprocess.Process] = []
    real_create = asyncio.create_subprocess_exec

    async def _recording_create(*argv: Any, **kwargs: Any) -> asyncio.subprocess.Process:
        process = await real_create(*argv, **kwargs)
        spawned.append(process)
        return process

    monkeypatch.setattr(asyncio, "create_subprocess_exec", _recording_create)

    runner = AsyncioSubprocessRunner()

    try:
        task = asyncio.create_task(
            runner.run(
                (sys.executable, "-c", "import time; time.sleep(300)"),
                stdin="",
                timeout_seconds=300.0,
            )
        )
        # Yield until the spawn has happened and the run is parked on the
        # `communicate` await — the window the clause under test covers. The
        # wait is bounded so a spawn that never happens fails the test instead
        # of hanging it; a run that died on the way to the spawn ends the wait
        # early, and awaiting the task below surfaces that real error.
        for _ in range(10_000):
            if spawned or task.done():
                break
            await asyncio.sleep(0)
        else:  # pragma: no cover - only on regression
            pytest.fail("child never spawned")
        if task.done():  # pragma: no cover - only on regression
            await task
        await asyncio.sleep(0)

        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

        assert len(spawned) == 1, "the spawn itself succeeded — the cancellation is the caller's"
        assert spawned[0].returncode is not None, (
            "the child outlived the cancelled run: a leaked CLI process"
        )
    finally:
        # Belt-and-braces so a regression (or a mutation probe) cannot leave a
        # 300-second sleeper behind.
        for process in spawned:
            if process.returncode is None:  # pragma: no cover - only on regression
                process.kill()
                await process.wait()


class _AlreadyReapedFakeProcess:
    """A child asyncio's transport has ALREADY finished with.

    `Process.kill()` raises `ProcessLookupError` in exactly this state:
    `BaseSubprocessTransport._call_connection_lost` clears the `Popen`
    reference, and `Process.kill()` delegates to that same transport, whose own
    `kill()` calls `BaseSubprocessTransport._check_proc()` first, while
    `wait()` still resolves immediately from the recorded return code. Every reap site in
    `AsyncioSubprocessRunner.run` races into it — the child can exit and the
    transport can finish between the reap-triggering event and the `kill()`
    (codex R1 [P2]). A real child cannot be held in that window deterministically,
    so the state is modelled directly.
    """

    def __init__(self) -> None:
        self.returncode: int | None = 0
        self.kill_calls = 0
        self.wait_calls = 0
        self.parked_in_communicate = False

    async def communicate(self, payload: bytes | None = None) -> tuple[bytes, bytes]:
        self.parked_in_communicate = True
        # Never resolves: the run parks here until the deadline or the caller's
        # cancellation lands, which is the window under test.
        await asyncio.get_running_loop().create_future()
        raise AssertionError("unreachable")  # pragma: no cover - the future never resolves

    def kill(self) -> None:
        self.kill_calls += 1
        raise ProcessLookupError()

    async def wait(self) -> int:
        self.wait_calls += 1
        return 0


def _patch_spawn_with(monkeypatch: pytest.MonkeyPatch, process: _AlreadyReapedFakeProcess) -> None:
    async def _fake_create(*argv: Any, **kwargs: Any) -> Any:
        return process

    monkeypatch.setattr(asyncio, "create_subprocess_exec", _fake_create)


@pytest.mark.asyncio
async def test_cancelled_run_keeps_the_cancellation_when_the_child_already_exited(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """codex R1 [P2] — the reap must never REPLACE the cancellation.

    Without the `ProcessLookupError` suppression the reap's own `kill()` raises
    out of the `except asyncio.CancelledError` clause, so the caller sees a
    `ProcessLookupError` instead of the cancellation it requested — a shutdown
    or deadline would be misclassified as a provider failure.
    """
    process = _AlreadyReapedFakeProcess()
    _patch_spawn_with(monkeypatch, process)

    runner = AsyncioSubprocessRunner()
    task = asyncio.create_task(
        runner.run((sys.executable, "-c", "pass"), stdin="", timeout_seconds=300.0)
    )
    # Bounded so a run that never reaches `communicate` fails rather than hangs;
    # a task that died on the way there ends the wait, and the await surfaces it.
    for _ in range(10_000):
        if process.parked_in_communicate or task.done():
            break
        await asyncio.sleep(0)
    else:  # pragma: no cover - only on regression
        pytest.fail("child never spawned")
    if task.done():  # pragma: no cover - only on regression
        await task

    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert process.kill_calls == 1, "the reap still fires — the suppression is not a skip"
    assert process.wait_calls == 1, "and the wait still runs, so a live child is still reaped"


@pytest.mark.asyncio
async def test_timed_out_run_keeps_the_typed_timeout_when_the_child_already_exited(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The same race at the deadline reap site: a child exiting as `wait_for`
    fires must not turn the typed `ExternalCLIProcessTimeout` — which callers
    classify on — into a raw `ProcessLookupError`."""
    process = _AlreadyReapedFakeProcess()
    _patch_spawn_with(monkeypatch, process)

    runner = AsyncioSubprocessRunner()
    with pytest.raises(ExternalCLIProcessTimeout):
        await runner.run(("my-cli",), stdin="", timeout_seconds=0.01)

    assert process.kill_calls == 1
    assert process.wait_calls == 1


@pytest.mark.asyncio
async def test_raising_observer_keeps_its_own_error_when_the_child_already_exited(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """And at the R7 observer reap site: an instantly-exiting child whose
    transport finished before the notification raises must not mask the
    observer's exception with a `ProcessLookupError`."""

    class _ObserverFailure(RuntimeError):
        pass

    process = _AlreadyReapedFakeProcess()
    _patch_spawn_with(monkeypatch, process)

    def _fail() -> None:
        raise _ObserverFailure("observer exploded")

    runner = AsyncioSubprocessRunner()
    with pytest.raises(_ObserverFailure):
        await runner.run(("my-cli",), stdin="", timeout_seconds=30.0, on_wire=_fail)

    assert process.kill_calls == 1
    assert process.wait_calls == 1
    assert not process.parked_in_communicate, "the observer raised before the payload handover"


@dataclass
class _LegacyFakeRunner:
    """A runner on the PRE-B-87 `run(argv, *, stdin, timeout_seconds)` contract.

    `ExternalCLISubprocessRunner` conformance is STRUCTURAL, so such a runner is
    still injectable through the public ``runner=`` constructor seam. An
    unconditional ``on_wire=`` keyword breaks it with `TypeError` before any
    process is spawned — on EVERY inference, degraded memory or not (codex R4
    [P1]).

    This test is the RUNTIME half of that compatibility. The STATIC half — the
    public seam type admitting this shape under pyright strict — is witnessed at
    `test_b87_runner_seam_typing.py` (codex R6 [P2]).
    """

    results: list[CLIProcessResult]
    calls: list[tuple[tuple[str, ...], str, float]]

    async def run(
        self,
        argv: tuple[str, ...],
        *,
        stdin: str,
        timeout_seconds: float,
    ) -> CLIProcessResult:
        self.calls.append((argv, stdin, timeout_seconds))
        return self.results.pop(0)


@pytest.mark.asyncio
async def test_legacy_runner_injected_through_the_public_seam_still_dispatches() -> None:
    """B-87 (codex R4 [P1]) — tier 2 at the ADAPTER→RUNNER seam. Every adapter
    now forwards `on_wire` to its runner, so a pre-B-87 runner handed in through
    `runner=` constructs fine and then `TypeError`s on the first inference. The
    adapter detects the signature and omits the keyword instead."""
    runner = _LegacyFakeRunner(
        results=[
            CLIProcessResult(exit_code=0, stdout='{"loggedIn": true}', stderr=""),
            CLIProcessResult(exit_code=0, stdout='{"result": "OK"}', stderr=""),
        ],
        calls=[],
    )
    adapter = await construct_claude_code_cli_adapter(_config(), runner=runner)
    notified: list[int] = []

    result = await adapter.dispatch_text(
        model="sonnet",
        prompt="Reply OK",
        on_wire=lambda: notified.append(len(runner.calls)),
    )

    assert result.text == "OK", "the legacy runner was dispatched to, not TypeError'd"
    assert runner.calls[1][1] == "Reply OK"
    assert notified == [1], (
        "the ADAPTER fired the fallback mark, with the handover still ahead of it"
    )


@pytest.mark.asyncio
async def test_legacy_runner_post_spawn_failure_still_reports_post_wire() -> None:
    """The legacy tier's adapter-side fire is load-bearing, not decorative:
    without it a real post-wire failure through a legacy runner would report as
    pre-wire — an under-report of a packet that did reach the CLI. The tier
    trades spawn-failure precision (pre-R3 behavior) for never crashing and
    never under-reporting."""
    runner = _LegacyFakeRunner(
        results=[
            CLIProcessResult(exit_code=0, stdout='{"loggedIn": true}', stderr=""),
            CLIProcessResult(exit_code=2, stdout="", stderr="the CLI died after reading stdin"),
        ],
        calls=[],
    )
    adapter = await construct_claude_code_cli_adapter(_config(), runner=runner)
    notified: list[str] = []

    with pytest.raises(ExternalCLICommandError, match="died after reading stdin"):
        await adapter.dispatch_text(
            model="sonnet",
            prompt="Reply OK",
            on_wire=lambda: notified.append("fired"),
        )

    assert notified == ["fired"], "a failure past the handover must not classify as pre-wire"


def _per_instance_runner_class() -> type[Any]:
    """A FRESH runner class whose `run` is chosen per INSTANCE.

    Fresh per call so the two dispatch orderings below cannot contaminate each
    other through anything the implementation might memoize per class.
    """

    class _PerInstanceRunner:
        def __init__(self, *, wire_aware: bool, results: list[CLIProcessResult]) -> None:
            self.results = results
            self.calls: list[tuple[tuple[str, ...], str, float]] = []
            self.fired_in_runner: list[str] = []
            # The shadowing that makes wire-awareness an INSTANCE property.
            self.run = self._wire_aware_run if wire_aware else self._legacy_run

        async def _wire_aware_run(
            self,
            argv: tuple[str, ...],
            *,
            stdin: str,
            timeout_seconds: float,
            on_wire: Callable[[], None] | None = None,
        ) -> CLIProcessResult:
            if on_wire is not None:
                on_wire()
                self.fired_in_runner.append("runner")
            self.calls.append((argv, stdin, timeout_seconds))
            return self.results.pop(0)

        async def _legacy_run(
            self,
            argv: tuple[str, ...],
            *,
            stdin: str,
            timeout_seconds: float,
        ) -> CLIProcessResult:
            self.calls.append((argv, stdin, timeout_seconds))
            return self.results.pop(0)

    return _PerInstanceRunner


def _per_instance_results() -> list[CLIProcessResult]:
    return [
        CLIProcessResult(exit_code=0, stdout='{"loggedIn": true}', stderr=""),
        CLIProcessResult(exit_code=0, stdout='{"result": "OK"}', stderr=""),
    ]


@pytest.mark.asyncio
async def test_wire_awareness_is_judged_per_runner_instance_not_per_class() -> None:
    """B-87 (codex R5 [P2-2]) — `run` can be shadowed per instance, so two
    instances of ONE class can disagree about wire-awareness. A verdict cached
    by class lets whichever instance dispatched first decide for its siblings,
    and both directions of that are broken: a legacy instance then receives an
    `on_wire=` keyword it cannot accept (`TypeError`, the inference dies), or a
    wire-aware instance is denied the callback it declares (precision silently
    lost back to the adapter-side fallback). Both orderings are exercised
    because a class-keyed cache breaks whichever instance is second."""
    # (a) legacy first — a cache would then withhold the callback from the
    #     wire-aware sibling.
    runner_cls = _per_instance_runner_class()
    legacy = runner_cls(wire_aware=False, results=_per_instance_results())
    wire_aware = runner_cls(wire_aware=True, results=_per_instance_results())

    legacy_adapter = await construct_claude_code_cli_adapter(_config(), runner=legacy)
    wire_aware_adapter = await construct_claude_code_cli_adapter(_config(), runner=wire_aware)

    legacy_marks: list[int] = []
    result = await legacy_adapter.dispatch_text(
        model="sonnet",
        prompt="Reply OK",
        on_wire=lambda: legacy_marks.append(len(legacy.calls)),
    )
    assert result.text == "OK", "the legacy instance was dispatched to, not TypeError'd"
    assert legacy_marks == [1], "and it took the ADAPTER-side fallback mark"
    assert legacy.fired_in_runner == []

    wire_marks: list[int] = []
    result = await wire_aware_adapter.dispatch_text(
        model="sonnet",
        prompt="Reply OK",
        on_wire=lambda: wire_marks.append(len(wire_aware.calls)),
    )
    assert result.text == "OK"
    assert wire_aware.fired_in_runner == ["runner"], (
        "the wire-aware sibling keeps full precision — the RUNNER fires the mark"
    )
    assert wire_marks == [1], "past the auth probe, before the inference handover"

    # (b) wire-aware first — a cache would then hand `on_wire=` to the legacy
    #     sibling and kill the dispatch outright.
    runner_cls = _per_instance_runner_class()
    wire_aware = runner_cls(wire_aware=True, results=_per_instance_results())
    legacy = runner_cls(wire_aware=False, results=_per_instance_results())

    wire_aware_adapter = await construct_claude_code_cli_adapter(_config(), runner=wire_aware)
    legacy_adapter = await construct_claude_code_cli_adapter(_config(), runner=legacy)

    await wire_aware_adapter.dispatch_text(model="sonnet", prompt="Reply OK", on_wire=lambda: None)
    result = await legacy_adapter.dispatch_text(
        model="sonnet", prompt="Reply OK", on_wire=lambda: None
    )
    assert result.text == "OK", "the legacy sibling still dispatches after a wire-aware one"


@pytest.mark.asyncio
async def test_kwargs_swallowing_runner_is_not_trusted_with_the_wire_boundary() -> None:
    """B-87 (codex R4 [P2]) — a runner that accepts `**kwargs` and IGNORES
    unknown keys would take the callback and never fire it, while the adapter,
    having handed the boundary off, skips its own mark. The packet reaches the
    CLI and telemetry reports pre-wire with no hash: silent UNDER-reporting of a
    real disclosure. Only a DECLARED `on_wire` parameter counts as wire-aware,
    so this runner takes the adapter-side fallback instead."""
    handover: list[str] = []

    @dataclass
    class _KwargsSwallowingRunner:
        results: list[CLIProcessResult]

        async def run(
            self,
            argv: tuple[str, ...],
            *,
            stdin: str,
            timeout_seconds: float,
            **_ignored: object,
        ) -> CLIProcessResult:
            handover.append(stdin)  # the packet is gone — a provider can read it
            return self.results.pop(0)

    runner = _KwargsSwallowingRunner(
        results=[
            CLIProcessResult(exit_code=0, stdout='{"loggedIn": true}', stderr=""),
            CLIProcessResult(exit_code=2, stdout="", stderr="the CLI died after reading stdin"),
        ]
    )
    adapter = await construct_claude_code_cli_adapter(_config(), runner=runner)
    notified: list[str] = []

    with pytest.raises(ExternalCLICommandError, match="died after reading stdin"):
        await adapter.dispatch_text(
            model="sonnet",
            prompt="Reply OK",
            on_wire=lambda: notified.append("fired"),
        )

    assert handover[-1] == "Reply OK", "the packet really did reach the runner"
    assert notified == ["fired"], "the swallowed callback was replaced by the adapter's own mark"


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
