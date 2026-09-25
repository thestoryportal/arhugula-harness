"""External local CLI provider adapters for subscription-backed inference.

R-CLI-1 deliberately uses the official local CLI as the auth boundary. The
runtime passes text over stdin and reads JSON over stdout; it never reads or
stores OAuth/session tokens and never invokes a shell.

Authority: ADR-D7 §Decision places external CLI routing under the C-RT-05
provider-construction authority; the operator-supply surface is the C-RT-02
``RuntimeConfig`` external-CLI fields (per
``class_1_fork_provider_construction_allowlist_semantic.md``).
"""

from __future__ import annotations

import asyncio
import inspect
import json
import logging
import os
import shutil
import signal
import sys
import tempfile
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Protocol, cast

from harness_runtime.types import (
    ExternalCLIPromptTransport,
    ExternalCLIProviderConfig,
    ExternalCLIProviderKind,
    ExternalCLIResponseFormat,
)

__all__ = [
    "AntigravityCLIAdapter",
    "AsyncioSubprocessRunner",
    "CLIProcessResult",
    "ClaudeCodeCLIAdapter",
    "CodexCLIAdapter",
    "ExternalCLICommandError",
    "ExternalCLINotAuthenticatedError",
    "ExternalCLIOutputError",
    "ExternalCLIProcessTimeout",
    "ExternalCLIProviderError",
    "ExternalCLISubprocessRunner",
    "ExternalCLITextResult",
    "GeminiCLIAdapter",
    "GenericCommandCLIAdapter",
    "RecordingSubprocessRunner",
    "WireAwareExternalCLISubprocessRunner",
    "accepts_explicit_on_wire",
    "construct_antigravity_cli_adapter",
    "construct_claude_code_cli_adapter",
    "construct_codex_cli_adapter",
    "construct_external_cli_adapter",
    "construct_gemini_cli_adapter",
    "construct_generic_command_cli_adapter",
]


@dataclass(frozen=True, slots=True)
class CLIProcessResult:
    exit_code: int
    stdout: str
    stderr: str


@dataclass(frozen=True, slots=True)
class ExternalCLITextResult:
    text: str
    exit_code: int
    raw_response: Mapping[str, Any]


class ExternalCLIProviderError(Exception):
    """Base class for external CLI provider failures."""


class ExternalCLIProcessTimeout(ExternalCLIProviderError):  # noqa: N818
    """Raised when the CLI process exceeds its configured timeout."""

    def __init__(self, command: str, timeout_seconds: float) -> None:
        self.command = command
        self.timeout_seconds = timeout_seconds
        super().__init__(f"external CLI command {command!r} timed out after {timeout_seconds:.3g}s")


class ExternalCLICommandError(ExternalCLIProviderError):
    """Raised when the CLI process exits nonzero or cannot be spawned."""

    def __init__(
        self,
        command: str,
        exit_code: int,
        stderr: str,
        *,
        stdout: str = "",
        detail: str | None = None,
    ) -> None:
        self.command = command
        self.exit_code = exit_code
        self.stderr = stderr
        self.stdout = stdout
        if detail is None:
            detail = stderr.strip() or stdout.strip() or "no stderr/stdout"
        super().__init__(f"external CLI command {command!r} exited {exit_code}: {detail}")


class ExternalCLIOutputError(ExternalCLIProviderError):
    """Raised when the CLI exits successfully but returns an unexpected payload."""


class ExternalCLINotAuthenticatedError(ExternalCLIProviderError):
    """Raised when the official CLI reports no authenticated local session."""

    def __init__(self, provider: str, detail: str) -> None:
        self.provider = provider
        self.detail = detail
        super().__init__(f"external CLI provider {provider!r} is not authenticated: {detail}")


class ExternalCLISubprocessRunner(Protocol):
    """Subprocess boundary for external CLI calls — the PUBLIC ``runner=`` seam.

    The shape intentionally has no shell parameter; production uses argv-only
    `create_subprocess_exec`, and tests inject deterministic fakes.

    This is deliberately the pre-B-87 signature — no ``on_wire``. It is the
    seam every public constructor (`construct_*_cli_adapter`) and every adapter
    field is typed with, and it is the WIDER of B-87's two runner shapes: a
    legacy runner satisfies it, and so does a wire-aware one (the extra
    parameter is keyword-only WITH a default, so an implementation declaring it
    is still assignable here). Typing the seam with the NARROWER wire-aware
    shape would have made a typed pre-B-87 runner a pyright error at injection
    — runtime compatibility without static compatibility (codex R6 [P2]).

    `WireAwareExternalCLISubprocessRunner` is the opt-in extension; runners that
    want full-precision wire attribution declare ``on_wire`` and are still
    injectable HERE unchanged. `_run_with_wire_boundary` picks the tier per
    dispatch and never hands the keyword to a runner that did not declare it.
    """

    async def run(
        self,
        argv: tuple[str, ...],
        *,
        stdin: str,
        timeout_seconds: float,
    ) -> CLIProcessResult: ...


class WireAwareExternalCLISubprocessRunner(ExternalCLISubprocessRunner, Protocol):
    """A runner that OPTS IN to B-87's reached-the-wire notification.

    ``on_wire`` is the notification described at `_notify_wire`. It lives at the
    runner rather than in the adapters because the boundary it names — a child
    process exists — is only observable at this layer. An implementation of
    THIS Protocol MUST fire it once process creation has succeeded and before
    the payload is handed over, and never otherwise. ``None``, the default, is
    every caller not tracking the boundary (the auth probes, every non-degraded
    dispatch) and is a no-op.

    A wire-aware runner is assignable to the plain `ExternalCLISubprocessRunner`
    seam, so declaring the parameter is a pure opt-in: nothing about injection
    changes. `_run_with_wire_boundary` narrows to this shape only after
    `_runner_accepts_on_wire` confirms the parameter is genuinely declared.
    """

    async def run(
        self,
        argv: tuple[str, ...],
        *,
        stdin: str,
        timeout_seconds: float,
        on_wire: Callable[[], None] | None = None,
    ) -> CLIProcessResult: ...


# Provider inference credentials stripped from the environment handed to a spawned
# external CLI. OAuth/subscription CLI routing exists to use each CLI's own local
# auth/session store; the `claude`/`codex`/`gemini` CLIs prefer an inherited API key
# over their OAuth session when one is present, which would silently convert the
# subscription route into metered API-key billing AND export the harness's secrets
# into an agentic child process. This workspace loads such keys into the process
# environment (via `just` dotenv), so the risk is concrete rather than theoretical.
_SCRUBBED_PROVIDER_ENV_VARS: frozenset[str] = frozenset(
    {
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GOOGLE_APPLICATION_CREDENTIALS",
    }
)

_CLAUDE_ENV_KEYS = frozenset(
    {
        "PATH",
        "HOME",
        "USER",
        "LOGNAME",
        "LANG",
        "TZ",
        "TMPDIR",
        "XDG_CONFIG_HOME",
        "XDG_DATA_HOME",
        "XDG_STATE_HOME",
        "XDG_CACHE_HOME",
        "CLAUDE_CONFIG_DIR",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "NO_PROXY",
        "http_proxy",
        "https_proxy",
        "no_proxy",
        "SSL_CERT_FILE",
        "REQUESTS_CA_BUNDLE",
        "NODE_EXTRA_CA_CERTS",
    }
)


def _claude_child_env() -> dict[str, str]:
    # [LAW:single-enforcer] The Claude subscription subprocess has one env boundary.
    return {
        key: value
        for key, value in os.environ.items()
        if key in _CLAUDE_ENV_KEYS or key.startswith("LC_")
    }


def _notify_wire(on_wire: Callable[[], None] | None) -> None:
    """Announce that the payload has REACHED THE WIRE.

    B-87 defines "reached the wire" as: **a child process exists that can
    observe the payload.** That is the whole semantic anchor, and it fixes the
    boundary in both directions:

    * A **spawn failure** is PRE-wire — a missing or unexecutable command, an
      empty argv, a `PermissionError` out of `create_subprocess_exec`. Nothing
      left the runtime, so nothing can have read the prompt. (Adapter-local
      validation raises — `_render_argv_templates` rejecting a `{prompt}`
      template under `prompt_transport = "stdin"`, codex R2 — are pre-wire for
      the same reason, one layer further out.)
    * A failure **during or after the stdin write, or while awaiting output**,
      is POST-wire — the process existed and may have seen the packet. A
      timeout, a nonzero exit, an unparseable payload: all post-wire.

    This is the DEFINED stopping point (codex R3 [P2-1]). The boundary is NOT
    pushed further — a partial stdin write, an unread pipe, a child that exited
    before reading: all post-wire. The register's contract is "did the payload
    leave the process", not "did the peer read byte N"; refining past process
    existence is an endless regress with no observable answer.

    Fired by the RUNNER, immediately after process creation succeeds and before
    the payload is handed over (`AsyncioSubprocessRunner.run`), so every
    pre-spawn raise — whether the runner translates it or lets it propagate —
    lands on the pre-wire side automatically. ``None`` is every caller that is
    not tracking the boundary, and is a no-op.
    """
    if on_wire is not None:
        on_wire()


def accepts_explicit_on_wire(target: Callable[..., Any] | None) -> bool:
    """Does ``target`` DECLARE a named ``on_wire`` parameter? (B-87, codex R4 [P2])

    The single wire-awareness predicate for both B-87 capability seams — the
    dispatcher's adapter check (`llm_dispatch._adapter_accepts_on_wire`) and
    the adapters' runner check (`_runner_accepts_on_wire`). One definition so
    the two cannot drift.

    Wire-awareness must be **declared**, never inferred: a bare ``**kwargs``
    does NOT count, even though passing the keyword to such a callable would
    not raise. A forwarding implementation that swallows unknown keys would
    accept the callback and never fire it, while the caller — having handed
    the boundary off — skips its own fallback mark. A packet that genuinely
    reached a provider would then be reported ``pre_wire_failure`` with no
    ``packet_hash``: silent UNDER-reporting of a real disclosure, which is the
    worse error direction and the exact defect class B-87 exists to close.

    The opposite misclassification is cheap and self-correcting: a genuinely
    forwarding ``**kwargs`` implementation read as legacy merely takes the
    caller-side fallback mark — i.e. pre-B-87 reporting precision, no crash and
    no under-report. Declaring wire-awareness costs one keyword: name it.
    """
    if target is None:
        return False
    try:
        parameters = inspect.signature(target).parameters
    except (TypeError, ValueError):  # pragma: no cover - exotic non-introspectable callable
        return False
    parameter = parameters.get("on_wire")
    return parameter is not None and parameter.kind in (
        inspect.Parameter.KEYWORD_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
    )


def _runner_accepts_on_wire(runner: ExternalCLISubprocessRunner) -> bool:
    """Inspect THIS runner's bound `run`, per dispatch (B-87, codex R5 [P2-2]).

    Deliberately uncached. A verdict memoized per runner CLASS is wrong: `run`
    can be shadowed per instance, so two instances of one class can disagree,
    and whichever dispatched first would decide for both — handing ``on_wire=``
    to a legacy callable (`TypeError`, the inference dies) or withholding it
    from a wire-aware one (precision silently lost). One `inspect.signature`
    is microseconds against a subprocess spawn; the cache bought nothing and
    cost correctness.
    """
    return accepts_explicit_on_wire(getattr(runner, "run", None))


async def _run_with_wire_boundary(
    runner: ExternalCLISubprocessRunner,
    argv: tuple[str, ...],
    *,
    stdin: str,
    timeout_seconds: float,
    on_wire: Callable[[], None] | None,
) -> CLIProcessResult:
    """Hand argv to the runner under B-87's TWO-TIER wire-boundary ownership.

    * **Wire-aware runner** (declares ``on_wire`` — the shipped
      `AsyncioSubprocessRunner`, and any runner that opts in by naming the
      parameter). The keyword rides down and the RUNNER fires it past
      `create_subprocess_exec`, so a spawn failure stays PRE-wire. This is the
      full-precision tier.
    * **Legacy runner** (a pre-B-87 runner injected through the public
      ``runner=`` seam, which is typed with the wider, ``on_wire``-free
      `ExternalCLISubprocessRunner` precisely so this stays statically legal —
      codex R4 [P1] / R6 [P2]). The keyword is NOT passed: it would raise
      `TypeError` before any spawn, so every inference through such a runner
      would fail outright. Instead the ADAPTER fires the mark HERE — after all
      adapter-local argv validation, immediately before the handover (the
      commit-54419eb4 placement).

    The legacy tier's residual imprecision is bounded and truthful-by-
    degradation: a spawn failure under a legacy runner reports POST-wire, which
    is exactly the pre-R3 behavior — never a crash, and never an under-report
    of a real disclosure. Adapter-local validation raises (the
    `{prompt}`-template-under-stdin rejection) stay PRE-wire on both tiers,
    because both fire strictly after them.
    """
    if not _runner_accepts_on_wire(runner):
        _notify_wire(on_wire)
        return await runner.run(argv, stdin=stdin, timeout_seconds=timeout_seconds)
    # `_runner_accepts_on_wire` just proved THIS instance's bound `run` declares
    # the parameter, which is exactly `WireAwareExternalCLISubprocessRunner`
    # conformance. The narrowing cannot be expressed as an `isinstance` check
    # (a non-`runtime_checkable` Protocol, and `runtime_checkable` would only
    # test the member's presence, not its signature), so the runtime predicate
    # is the narrowing and the cast records it.
    wire_aware = cast(WireAwareExternalCLISubprocessRunner, runner)
    return await wire_aware.run(
        argv,
        stdin=stdin,
        timeout_seconds=timeout_seconds,
        on_wire=on_wire,
    )


def _scrubbed_child_env() -> dict[str, str]:
    """The current environment minus hosted-provider inference credentials."""
    return {
        key: value for key, value in os.environ.items() if key not in _SCRUBBED_PROVIDER_ENV_VARS
    }


_CLEANUP_WAIT_SECONDS = 5.0
_CLEANUP_UNCERTAIN = "External CLI process-group cleanup could not be confirmed"
_SCRATCH_UNCERTAIN = "Claude scratch directory removal failed"
_LOG = logging.getLogger(__name__)


async def _terminate_group(process: asyncio.subprocess.Process) -> str | None:
    """Signal the isolated process group, then bound direct-child reaping."""
    uncertain = False
    if os.name == "posix" and process.pid != os.getpgrp():
        try:
            # [LAW:single-enforcer] The runner owns the lifetime of every child in this group.
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        except OSError:
            uncertain = True
            try:
                process.kill()
            except ProcessLookupError:
                pass
    else:
        if os.name == "posix":
            uncertain = True  # Never signal the harness's own process group.
        try:
            process.kill()
        except ProcessLookupError:
            pass
    try:
        await asyncio.wait_for(process.wait(), timeout=_CLEANUP_WAIT_SECONDS)
    except (OSError, TimeoutError):
        uncertain = True
    return _CLEANUP_UNCERTAIN if uncertain else None


async def _settle_process(
    process: asyncio.subprocess.Process, original: BaseException | None = None
) -> None:
    """Finish cleanup despite repeated caller cancellation; preserve the first outcome."""
    # [LAW:no-ambient-temporal-coupling] The cleanup task owns the exit boundary.
    task = asyncio.create_task(_terminate_group(process))
    cancelled: asyncio.CancelledError | None = None
    while not task.done():
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError as exc:
            cancelled = exc
    try:
        note = task.result()
    except Exception:
        note = _CLEANUP_UNCERTAIN
    if note is not None:
        _LOG.warning("%s", note)
        if original is not None:
            original.add_note(note)
    if cancelled is not None and not isinstance(original, asyncio.CancelledError):
        raise cancelled


class AsyncioSubprocessRunner:
    """Production subprocess runner using argv-only execution."""

    async def run(
        self,
        argv: tuple[str, ...],
        *,
        stdin: str,
        timeout_seconds: float,
        on_wire: Callable[[], None] | None = None,
    ) -> CLIProcessResult:
        return await self._run_process(
            argv,
            stdin=stdin,
            timeout_seconds=timeout_seconds,
            on_wire=on_wire,
            env=_scrubbed_child_env(),
            cwd=None,
        )

    async def _run_process(
        self,
        argv: tuple[str, ...],
        *,
        stdin: str,
        timeout_seconds: float,
        on_wire: Callable[[], None] | None,
        env: Mapping[str, str],
        cwd: str | None,
    ) -> CLIProcessResult:
        if not argv:
            raise ExternalCLICommandError("", 127, "empty argv")
        try:
            process = await asyncio.create_subprocess_exec(
                *argv,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=cwd,
                start_new_session=os.name == "posix",
            )
        except FileNotFoundError as exc:
            raise ExternalCLICommandError(argv[0], 127, str(exc)) from exc

        # The child exists before the wire notification. Every post-spawn outcome
        # settles its group before the caller can observe completion.
        try:
            _notify_wire(on_wire)
        except BaseException as exc:
            await _settle_process(process, exc)
            raise

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(stdin.encode("utf-8")), timeout=timeout_seconds
            )
        except TimeoutError as exc:
            outcome = ExternalCLIProcessTimeout(argv[0], timeout_seconds)
            await _settle_process(process, outcome)
            raise outcome from exc
        except BaseException as exc:
            await _settle_process(process, exc)
            raise

        await _settle_process(process)
        return CLIProcessResult(
            exit_code=process.returncode or 0,
            stdout=stdout_bytes.decode("utf-8", errors="replace"),
            stderr=stderr_bytes.decode("utf-8", errors="replace"),
        )


class _PrivateCwdSubprocessRunner(AsyncioSubprocessRunner):
    """A production boundary that runs each child in its own fresh empty private cwd."""

    _cwd_prefix: str
    _scratch_uncertain: str
    _child_env: Callable[[], dict[str, str]]

    async def run(
        self,
        argv: tuple[str, ...],
        *,
        stdin: str,
        timeout_seconds: float,
        on_wire: Callable[[], None] | None = None,
    ) -> CLIProcessResult:
        # [LAW:no-ambient-temporal-coupling] The process group settles before cwd removal.
        cwd = tempfile.mkdtemp(prefix=self._cwd_prefix, dir="/tmp")
        try:
            return await self._run_process(
                argv,
                stdin=stdin,
                timeout_seconds=timeout_seconds,
                on_wire=on_wire,
                env=self._child_env(),
                cwd=cwd,
            )
        finally:
            outcome = sys.exc_info()[1]
            try:
                shutil.rmtree(cwd)
            except Exception:
                # [LAW:no-silent-failure] Removal cannot replace the call outcome.
                _LOG.warning("%s", self._scratch_uncertain)
                if outcome is not None:
                    outcome.add_note(self._scratch_uncertain)


class _ClaudeCodeSubprocessRunner(_PrivateCwdSubprocessRunner):
    """Production Claude boundary; one empty private cwd per child."""

    _cwd_prefix = "arhugula-claude-"
    _scratch_uncertain = _SCRATCH_UNCERTAIN
    _child_env = staticmethod(_claude_child_env)


class _CodexSubprocessRunner(_PrivateCwdSubprocessRunner):
    """Production Codex boundary; one empty private cwd per child, credentials scrubbed."""

    _cwd_prefix = "arhugula-codex-"
    _scratch_uncertain = "Codex scratch directory removal failed"
    _child_env = staticmethod(_scrubbed_child_env)


class RecordingSubprocessRunner:
    """Fake runner for tests that records argv/stdin/timeout calls."""

    def __init__(self, results: Sequence[CLIProcessResult]) -> None:
        self._results = list(results)
        self.calls: list[tuple[tuple[str, ...], str, float]] = []

    async def run(
        self,
        argv: tuple[str, ...],
        *,
        stdin: str,
        timeout_seconds: float,
        on_wire: Callable[[], None] | None = None,
    ) -> CLIProcessResult:
        # Models a successful spawn, so the wire notification precedes the
        # recorded handover — the real runner's ordering (B-87).
        _notify_wire(on_wire)
        self.calls.append((argv, stdin, timeout_seconds))
        if not self._results:
            raise AssertionError("RecordingSubprocessRunner has no remaining results")
        return self._results.pop(0)


@dataclass(slots=True)
class ClaudeCodeCLIAdapter:
    provider_name: str
    command: str
    timeout_seconds: float
    runner: ExternalCLISubprocessRunner
    kind: str = "claude-code"
    _closed: bool = False

    async def aclose(self) -> None:
        self._closed = True

    async def dispatch_text(
        self,
        *,
        model: str,
        prompt: str,
        on_wire: Callable[[], None] | None = None,
    ) -> ExternalCLITextResult:
        argv = _claude_inference_argv(self.command, model)
        result = await _run_with_wire_boundary(
            self.runner,
            argv,
            stdin=prompt,
            timeout_seconds=self.timeout_seconds,
            on_wire=on_wire,
        )
        _raise_for_nonzero(self.command, result)
        payload = _parse_json_object(result.stdout, "Claude Code inference response")
        text = _extract_text_result(payload)
        return ExternalCLITextResult(text=text, exit_code=result.exit_code, raw_response=payload)


@dataclass(slots=True)
class CodexCLIAdapter:
    provider_name: str
    command: str
    timeout_seconds: float
    runner: ExternalCLISubprocessRunner
    kind: str = "codex"
    _closed: bool = False

    async def aclose(self) -> None:
        self._closed = True

    async def dispatch_text(
        self,
        *,
        model: str,
        prompt: str,
        on_wire: Callable[[], None] | None = None,
    ) -> ExternalCLITextResult:
        argv = _codex_inference_argv(self.command, model)
        result = await _run_with_wire_boundary(
            self.runner,
            argv,
            stdin=prompt,
            timeout_seconds=self.timeout_seconds,
            on_wire=on_wire,
        )
        _raise_for_codex_nonzero(self.command, result)
        events = _parse_codex_json_lines(result.stdout, "Codex inference response")
        text = _codex_answer_text(events, "Codex inference response")
        return ExternalCLITextResult(
            text=text,
            exit_code=result.exit_code,
            raw_response={"events": events},
        )


@dataclass(slots=True)
class AntigravityCLIAdapter:
    provider_name: str
    command: str
    timeout_seconds: float
    runner: ExternalCLISubprocessRunner
    kind: str = "antigravity"
    _closed: bool = False

    async def aclose(self) -> None:
        self._closed = True

    async def dispatch_text(
        self,
        *,
        model: str,
        prompt: str,
        on_wire: Callable[[], None] | None = None,
    ) -> ExternalCLITextResult:
        argv = _antigravity_inference_argv(
            self.command,
            model,
            prompt,
            timeout_seconds=self.timeout_seconds,
        )
        result = await _run_with_wire_boundary(
            self.runner,
            argv,
            stdin="",
            timeout_seconds=self.timeout_seconds,
            on_wire=on_wire,
        )
        _raise_for_nonzero(self.command, result)
        text, raw_response = _parse_response_by_format(
            result.stdout,
            ExternalCLIResponseFormat.TEXT,
            "Antigravity inference response",
        )
        return ExternalCLITextResult(
            text=text,
            exit_code=result.exit_code,
            raw_response=raw_response,
        )


@dataclass(slots=True)
class GeminiCLIAdapter:
    provider_name: str
    command: str
    timeout_seconds: float
    runner: ExternalCLISubprocessRunner
    kind: str = "gemini"
    _closed: bool = False

    async def aclose(self) -> None:
        self._closed = True

    async def dispatch_text(
        self,
        *,
        model: str,
        prompt: str,
        on_wire: Callable[[], None] | None = None,
    ) -> ExternalCLITextResult:
        argv = _gemini_inference_argv(self.command, model, prompt)
        result = await _run_with_wire_boundary(
            self.runner,
            argv,
            stdin="",
            timeout_seconds=self.timeout_seconds,
            on_wire=on_wire,
        )
        _raise_for_nonzero(self.command, result)
        text, raw_response = _parse_response_by_format(
            result.stdout,
            ExternalCLIResponseFormat.TEXT,
            "Gemini inference response",
        )
        return ExternalCLITextResult(
            text=text,
            exit_code=result.exit_code,
            raw_response=raw_response,
        )


@dataclass(slots=True)
class GenericCommandCLIAdapter:
    provider_name: str
    command: str
    args: tuple[str, ...]
    response_format: ExternalCLIResponseFormat
    prompt_transport: ExternalCLIPromptTransport
    timeout_seconds: float
    runner: ExternalCLISubprocessRunner
    kind: str = "generic-command"
    _closed: bool = False

    async def aclose(self) -> None:
        self._closed = True

    async def dispatch_text(
        self,
        *,
        model: str,
        prompt: str,
        on_wire: Callable[[], None] | None = None,
    ) -> ExternalCLITextResult:
        prompt_in_argv = self.prompt_transport is ExternalCLIPromptTransport.ARG
        # `_render_argv_templates` REJECTS a `{prompt}` template under stdin
        # transport — an adapter-local validation raise with zero subprocess
        # calls. It stays pre-wire on BOTH `_run_with_wire_boundary` tiers,
        # because this raise never reaches that call at all (B-87 R2, boundary
        # relocated at R3 [P2-1], two-tiered at R4 [P1]).
        argv = (
            self.command,
            *_render_argv_templates(
                self.args,
                model=model,
                prompt=prompt,
                prompt_in_argv=prompt_in_argv,
            ),
        )
        result = await _run_with_wire_boundary(
            self.runner,
            argv,
            stdin="" if prompt_in_argv else prompt,
            timeout_seconds=self.timeout_seconds,
            on_wire=on_wire,
        )
        _raise_for_nonzero(self.command, result)
        text, raw_response = _parse_response_by_format(
            result.stdout,
            self.response_format,
            "generic external CLI inference response",
        )
        return ExternalCLITextResult(
            text=text,
            exit_code=result.exit_code,
            raw_response=raw_response,
        )


def _claude_auth_argv(command: str) -> tuple[str, ...]:
    return (command, "auth", "status", "--json")


def _claude_inference_argv(command: str, model: str) -> tuple[str, ...]:
    return (
        command,
        "--print",
        "--output-format",
        "json",
        "--input-format",
        "text",
        "--no-session-persistence",
        "--safe-mode",
        "--strict-mcp-config",
        "--tools",
        "",
        "--permission-mode",
        "dontAsk",
        "--permission-prompts",
        "none",
        "--model",
        model,
    )


def _codex_auth_argv(command: str) -> tuple[str, ...]:
    return (command, "login", "status")


def _codex_inference_argv(command: str, model: str) -> tuple[str, ...]:
    return (
        command,
        "exec",
        "--json",
        "--ephemeral",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "-m",
        model,
        "-",
    )


def _antigravity_auth_argv(command: str) -> tuple[str, ...]:
    return (command, "models")


def _antigravity_inference_argv(
    command: str,
    model: str,
    prompt: str,
    *,
    timeout_seconds: float,
) -> tuple[str, ...]:
    return (
        command,
        "--print",
        prompt,
        "--model",
        model,
        "--print-timeout",
        _go_seconds_duration(timeout_seconds),
        "--sandbox",
    )


def _gemini_inference_argv(command: str, model: str, prompt: str) -> tuple[str, ...]:
    return (
        command,
        "--skip-trust",
        "-m",
        model,
        "-p",
        prompt,
    )


def _go_seconds_duration(seconds: float) -> str:
    # Go's ParseDuration rejects scientific notation (`:.3g` yields e.g.
    # "1.2e+03s" for timeouts >= 1000s), so emit a plain decimal with any
    # trailing zeros trimmed ("120s", "0.5s", "1200s").
    return f"{seconds:.3f}".rstrip("0").rstrip(".") + "s"


def _raise_for_nonzero(command: str, result: CLIProcessResult) -> None:
    if result.exit_code != 0:
        raise ExternalCLICommandError(
            command,
            result.exit_code,
            result.stderr,
            stdout=result.stdout,
        )


def _raise_for_codex_nonzero(command: str, result: CLIProcessResult) -> None:
    """Nonzero exit still wins over parsing, but Codex stdout/stderr are untrusted output.

    The error keeps the command and exit code and stores neither stream: a tool item's text
    must not reach a message or a diagnostic field just because the CLI also exited nonzero.
    """
    if result.exit_code != 0:
        raise ExternalCLICommandError(
            command, result.exit_code, "", detail="CLI output withheld (untrusted Codex output)"
        )


def _parse_json_object(raw: str, label: str) -> Mapping[str, Any]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ExternalCLIOutputError(f"{label} was not valid JSON: {exc}") from exc
    if not isinstance(parsed, Mapping):
        raise ExternalCLIOutputError(f"{label} was not a JSON object")
    return dict(cast(Mapping[str, Any], parsed))


def _parse_json_lines(raw: str, label: str) -> tuple[Mapping[str, Any], ...]:
    events: list[Mapping[str, Any]] = []
    for line_number, line in enumerate(raw.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ExternalCLIOutputError(
                f"{label} line {line_number} was not valid JSON: {exc}"
            ) from exc
        if not isinstance(parsed, Mapping):
            raise ExternalCLIOutputError(f"{label} line {line_number} was not a JSON object")
        events.append(dict(cast(Mapping[str, Any], parsed)))
    if not events:
        raise ExternalCLIOutputError(f"{label} did not contain JSON events")
    return tuple(events)


class _CodexJSONBoundaryError(ValueError):
    """A Codex JSONL line broke the boundary; `reason` is a fixed label, never CLI output."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def _codex_object_without_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """`object_pairs_hook`: runs for every object at every depth, on ESCAPE-DECODED keys, so
    `"\\u0074ype"` and `"type"` collide. `json.loads` alone keeps the last duplicate."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _CodexJSONBoundaryError("contained a duplicate object key")
        result[key] = value
    return result


def _codex_reject_non_finite(_literal: str) -> Any:
    raise _CodexJSONBoundaryError("contained a non-finite number")


def _codex_finite_float(literal: str) -> float:
    """`parse_float`: `1e999` overflows to infinity without ever reaching `parse_constant`."""
    value = float(literal)
    if value != value or value in (float("inf"), float("-inf")):
        raise _CodexJSONBoundaryError("contained a non-finite number")
    return value


def _parse_codex_json_lines(raw: str, label: str) -> tuple[Mapping[str, Any], ...]:
    """Parse the WHOLE Codex JSONL stream before anything is classified or answered.

    Codex-only: the shared `_parse_json_lines` (last duplicate key wins) still serves every
    other provider. Every line must be one JSON object with no duplicate key at any depth
    (compared after escape decoding) and no non-finite number. A failing line refuses the
    entire stream with a fixed diagnostic naming only the line number: no exception text and
    no raw content is echoed, because the line is untrusted CLI output. Lines split on `\\n`
    only (JSONL), so a raw U+2028 inside a string is text, not a break.
    [LAW:parse-dont-validate] [LAW:no-silent-failure]
    """
    events: list[Mapping[str, Any]] = []
    for line_number, line in enumerate(raw.split("\n"), start=1):
        if not line.strip(" \t\r"):
            continue
        try:
            parsed = json.loads(
                line,
                object_pairs_hook=_codex_object_without_duplicate_keys,
                parse_constant=_codex_reject_non_finite,
                parse_float=_codex_finite_float,
            )
        except _CodexJSONBoundaryError as exc:
            raise ExternalCLIOutputError(f"{label} line {line_number} {exc.reason}") from None
        except (ValueError, RecursionError):
            raise ExternalCLIOutputError(f"{label} line {line_number} was not valid JSON") from None
        if not isinstance(parsed, dict):
            raise ExternalCLIOutputError(f"{label} line {line_number} was not a JSON object")
        events.append(cast(dict[str, Any], parsed))
    if not events:
        raise ExternalCLIOutputError(f"{label} did not contain JSON events")
    return tuple(events)


def _extract_text_result(payload: Mapping[str, Any]) -> str:
    for key in ("result", "text", "response"):
        value = payload.get(key)
        if isinstance(value, str):
            return value
    raise ExternalCLIOutputError("external CLI JSON response did not contain a text result")


def _extract_jsonl_text_result(events: Sequence[Mapping[str, Any]], label: str) -> str:
    for event in reversed(events):
        event_type = event.get("type")
        if event_type == "agent_message":
            text = event.get("text")
            if isinstance(text, str):
                return text
        item = event.get("item")
        if isinstance(item, Mapping):
            item_payload = cast(Mapping[str, Any], item)
            text = item_payload.get("text")
            if item_payload.get("type") != "agent_message":
                text = None
            if isinstance(text, str):
                return text
        text = event.get("text")
        if isinstance(text, str) and event_type in {"message", "response"}:
            return text
    raise ExternalCLIOutputError(f"{label} did not contain an agent text result")


_CODEX_LIFECYCLE_TYPES = frozenset({"thread.started", "turn.started", "turn.completed"})
"""The only no-item Codex envelopes. Anything else, including `turn.failed` and `error`, is
unverified output on a successful exit and refuses; this grammar is closed, not a denylist."""

_CODEX_ITEM_PHASES = frozenset({"item.started", "item.updated", "item.completed"})
"""The only outer types that may carry an `item`."""

_CODEX_NON_TOOL_ITEM_TYPES = frozenset({"agent_message", "reasoning"})
"""The only Codex JSONL item types that are model output rather than tool activity."""

_CODEX_NAMED_TOOL_ITEM_TYPES = frozenset(
    {"command_execution", "mcp_tool_call", "file_change", "web_search"}
)
"""Tool item types a refusal may name. The name comes from this fixed set, never from the
untrusted output: any other type is reported only as unrecognised."""


def _codex_event_refusal(event: Mapping[str, Any]) -> str | None:
    """The fixed label for an event outside the closed Codex grammar, else `None`.

    The outer `type` must be a string in exactly one of two sets: a lifecycle type, which
    carries no `item` key, or an item phase, which carries a mapping item of a recognised
    non-tool type. Every label is a constant or a name from `_CODEX_NAMED_TOOL_ITEM_TYPES`.
    """
    event_type = event.get("type")
    if not isinstance(event_type, str):
        return "malformed event envelope"
    if event_type in _CODEX_LIFECYCLE_TYPES:
        return "malformed event envelope" if "item" in event else None
    if event_type not in _CODEX_ITEM_PHASES:
        return "unrecognised event type"
    item = event.get("item")
    item_type = cast(Mapping[str, Any], item).get("type") if isinstance(item, Mapping) else None
    if not isinstance(item_type, str):
        return "malformed item event"
    if item_type in _CODEX_NON_TOOL_ITEM_TYPES:
        return None
    if item_type in _CODEX_NAMED_TOOL_ITEM_TYPES:
        return item_type
    return "unrecognised item type"


def _codex_answer_text(events: Sequence[Mapping[str, Any]], label: str) -> str:
    """Parse a Codex stream: refuse anything outside the grammar, then take the answer.

    Detection after the fact, not prevention. The answer is the last COMPLETED agent-message
    item of a fully validated stream; no top-level text shape is ever an answer.
    [LAW:parse-dont-validate]
    """
    for event in events:
        refusal = _codex_event_refusal(event)
        if refusal is not None:
            raise ExternalCLIOutputError(
                f"{label} contained a tool item or unverifiable event ({refusal}); "
                "tool use is not supported on this route"
            )
    for event in reversed(events):
        if event["type"] != "item.completed":
            continue
        item = cast(Mapping[str, Any], event["item"])
        text = item.get("text")
        if item["type"] == "agent_message" and isinstance(text, str):
            return text
    raise ExternalCLIOutputError(f"{label} did not contain an agent text result")


def _render_argv_templates(
    args: Sequence[str],
    *,
    model: str,
    prompt: str,
    prompt_in_argv: bool,
) -> tuple[str, ...]:
    rendered: list[str] = []
    for arg in args:
        if "{prompt}" in arg and not prompt_in_argv:
            raise ExternalCLIOutputError('{prompt} template requires prompt_transport = "arg"')
        rendered.append(arg.replace("{model}", model).replace("{prompt}", prompt))
    return tuple(rendered)


def _parse_response_by_format(
    raw: str,
    response_format: ExternalCLIResponseFormat,
    label: str,
) -> tuple[str, Mapping[str, Any]]:
    if response_format is ExternalCLIResponseFormat.TEXT:
        text = raw.strip()
        if not text:
            raise ExternalCLIOutputError(f"{label} was empty")
        return text, {"text": text}
    if response_format is ExternalCLIResponseFormat.JSON:
        payload = _parse_json_object(raw, label)
        return _extract_text_result(payload), payload
    if response_format is ExternalCLIResponseFormat.JSONL:
        events = _parse_json_lines(raw, label)
        return _extract_jsonl_text_result(events, label), {"events": events}
    raise ExternalCLIOutputError(f"unsupported external CLI response format {response_format!r}")


async def _assert_claude_authenticated(
    config: ExternalCLIProviderConfig,
    runner: ExternalCLISubprocessRunner,
) -> None:
    result = await runner.run(
        _claude_auth_argv(config.command),
        stdin="",
        timeout_seconds=config.timeout_seconds,
    )
    if result.exit_code != 0:
        raise ExternalCLINotAuthenticatedError(
            config.provider,
            result.stderr.strip() or result.stdout.strip() or f"exit={result.exit_code}",
        )
    payload = _parse_json_object(result.stdout, "Claude Code auth status response")
    if payload.get("loggedIn") is not True:
        raise ExternalCLINotAuthenticatedError(config.provider, "loggedIn=false")


async def _assert_codex_authenticated(
    config: ExternalCLIProviderConfig,
    runner: ExternalCLISubprocessRunner,
) -> None:
    result = await runner.run(
        _codex_auth_argv(config.command),
        stdin="",
        timeout_seconds=config.timeout_seconds,
    )
    # [LAW:no-silent-failure] The login-status output is untrusted CLI output and may carry
    # credentials: it selects the classification below but is never copied into an error.
    # Only fixed text and the integer exit code reach `detail`.
    if result.exit_code != 0:
        raise ExternalCLINotAuthenticatedError(
            config.provider,
            f"Codex login status exited {result.exit_code}",
        )
    output = f"{result.stdout}\n{result.stderr}".lower()
    if "not logged" in output or "logged out" in output or "not authenticated" in output:
        raise ExternalCLINotAuthenticatedError(
            config.provider,
            "Codex reported it is not logged in",
        )
    if "logged in" not in output and "authenticated" not in output:
        raise ExternalCLINotAuthenticatedError(
            config.provider,
            "could not confirm Codex login status",
        )


async def _assert_antigravity_authenticated(
    config: ExternalCLIProviderConfig,
    runner: ExternalCLISubprocessRunner,
) -> None:
    result = await runner.run(
        _antigravity_auth_argv(config.command),
        stdin="",
        timeout_seconds=config.timeout_seconds,
    )
    if result.exit_code != 0:
        raise ExternalCLINotAuthenticatedError(
            config.provider,
            result.stderr.strip() or result.stdout.strip() or f"exit={result.exit_code}",
        )
    if not result.stdout.strip():
        raise ExternalCLINotAuthenticatedError(
            config.provider,
            "could not confirm Antigravity models/auth status",
        )


async def _assert_configured_auth_command_succeeds(
    config: ExternalCLIProviderConfig,
    runner: ExternalCLISubprocessRunner,
    *,
    provider_label: str,
) -> None:
    if not config.auth_args:
        raise ExternalCLINotAuthenticatedError(
            config.provider,
            f"{provider_label} auth_check=true requires auth_args",
        )
    result = await runner.run(
        (config.command, *config.auth_args),
        stdin="",
        timeout_seconds=config.timeout_seconds,
    )
    if result.exit_code != 0:
        raise ExternalCLINotAuthenticatedError(
            config.provider,
            result.stderr.strip() or result.stdout.strip() or f"exit={result.exit_code}",
        )


async def construct_claude_code_cli_adapter(
    config: ExternalCLIProviderConfig,
    *,
    runner: ExternalCLISubprocessRunner | None = None,
) -> ClaudeCodeCLIAdapter:
    if config.kind is not ExternalCLIProviderKind.CLAUDE_CODE:
        raise ValueError(f"unsupported Claude Code adapter kind: {config.kind}")
    process_runner = runner if runner is not None else _ClaudeCodeSubprocessRunner()
    if config.auth_check:
        await _assert_claude_authenticated(config, process_runner)
    return ClaudeCodeCLIAdapter(
        provider_name=config.provider,
        command=config.command,
        timeout_seconds=config.timeout_seconds,
        runner=process_runner,
    )


async def construct_codex_cli_adapter(
    config: ExternalCLIProviderConfig,
    *,
    runner: ExternalCLISubprocessRunner | None = None,
) -> CodexCLIAdapter:
    if config.kind is not ExternalCLIProviderKind.CODEX:
        raise ValueError(f"unsupported Codex adapter kind: {config.kind}")
    process_runner = runner if runner is not None else _CodexSubprocessRunner()
    if config.auth_check:
        await _assert_codex_authenticated(config, process_runner)
    return CodexCLIAdapter(
        provider_name=config.provider,
        command=config.command,
        timeout_seconds=config.timeout_seconds,
        runner=process_runner,
    )


async def construct_antigravity_cli_adapter(
    config: ExternalCLIProviderConfig,
    *,
    runner: ExternalCLISubprocessRunner | None = None,
) -> AntigravityCLIAdapter:
    if config.kind is not ExternalCLIProviderKind.ANTIGRAVITY:
        raise ValueError(f"unsupported Antigravity adapter kind: {config.kind}")
    process_runner = runner if runner is not None else AsyncioSubprocessRunner()
    if config.auth_check:
        await _assert_antigravity_authenticated(config, process_runner)
    return AntigravityCLIAdapter(
        provider_name=config.provider,
        command=config.command,
        timeout_seconds=config.timeout_seconds,
        runner=process_runner,
    )


async def construct_gemini_cli_adapter(
    config: ExternalCLIProviderConfig,
    *,
    runner: ExternalCLISubprocessRunner | None = None,
) -> GeminiCLIAdapter:
    if config.kind is not ExternalCLIProviderKind.GEMINI:
        raise ValueError(f"unsupported Gemini adapter kind: {config.kind}")
    process_runner = runner if runner is not None else AsyncioSubprocessRunner()
    if config.auth_check:
        await _assert_configured_auth_command_succeeds(
            config,
            process_runner,
            provider_label="Gemini CLI",
        )
    return GeminiCLIAdapter(
        provider_name=config.provider,
        command=config.command,
        timeout_seconds=config.timeout_seconds,
        runner=process_runner,
    )


async def construct_generic_command_cli_adapter(
    config: ExternalCLIProviderConfig,
    *,
    runner: ExternalCLISubprocessRunner | None = None,
) -> GenericCommandCLIAdapter:
    if config.kind is not ExternalCLIProviderKind.GENERIC_COMMAND:
        raise ValueError(f"unsupported generic command adapter kind: {config.kind}")
    process_runner = runner if runner is not None else AsyncioSubprocessRunner()
    if config.auth_check:
        await _assert_configured_auth_command_succeeds(
            config,
            process_runner,
            provider_label="generic external CLI",
        )
    return GenericCommandCLIAdapter(
        provider_name=config.provider,
        command=config.command,
        args=config.args,
        response_format=config.response_format,
        prompt_transport=config.prompt_transport,
        timeout_seconds=config.timeout_seconds,
        runner=process_runner,
    )


async def construct_external_cli_adapter(
    config: ExternalCLIProviderConfig,
    *,
    runner: ExternalCLISubprocessRunner | None = None,
) -> (
    ClaudeCodeCLIAdapter
    | CodexCLIAdapter
    | AntigravityCLIAdapter
    | GeminiCLIAdapter
    | GenericCommandCLIAdapter
):
    if config.kind is ExternalCLIProviderKind.CLAUDE_CODE:
        return await construct_claude_code_cli_adapter(config, runner=runner)
    if config.kind is ExternalCLIProviderKind.CODEX:
        return await construct_codex_cli_adapter(config, runner=runner)
    if config.kind is ExternalCLIProviderKind.ANTIGRAVITY:
        return await construct_antigravity_cli_adapter(config, runner=runner)
    if config.kind is ExternalCLIProviderKind.GEMINI:
        return await construct_gemini_cli_adapter(config, runner=runner)
    if config.kind is ExternalCLIProviderKind.GENERIC_COMMAND:
        return await construct_generic_command_cli_adapter(config, runner=runner)
    raise ValueError(f"unsupported external CLI provider kind: {config.kind}")
