"""Codex CLI login-status diagnostic: the CLI's raw output is untrusted and never re-emitted.

Provider-free: a fake runner scripts the `codex login status` result. Only classification and
fixed text survive; a credential in stdout or stderr must not reach the error or its detail.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest
from harness_runtime.lifecycle.external_cli_provider import (
    CLIProcessResult,
    ExternalCLINotAuthenticatedError,
    construct_codex_cli_adapter,
)
from harness_runtime.types import ExternalCLIProviderConfig


@dataclass
class _FakeRunner:
    results: list[CLIProcessResult]

    async def run(self, argv: tuple[str, ...], **_kwargs: Any) -> CLIProcessResult:
        return self.results.pop(0)


_AUTH_SECRET = "sk-SECRET-TOKEN-0123456789"


def _auth_config() -> ExternalCLIProviderConfig:
    return ExternalCLIProviderConfig(
        provider="codex",
        kind="codex",
        command="codex",
        timeout_seconds=42.0,
        auth_check=True,
    )


async def _construct_with_login_status(result: CLIProcessResult) -> object:
    return await construct_codex_cli_adapter(_auth_config(), runner=_FakeRunner([result]))


def _assert_no_secret(error: ExternalCLINotAuthenticatedError) -> None:
    assert _AUTH_SECRET not in str(error)
    assert _AUTH_SECRET not in error.detail
    assert _AUTH_SECRET.lower() not in str(error).lower()


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", ["stdout", "stderr", "both"])
async def test_a_nonzero_login_status_never_echoes_cli_output(stream: str) -> None:
    text = f"token={_AUTH_SECRET} not logged in"
    result = CLIProcessResult(
        exit_code=3,
        stdout=text if stream in ("stdout", "both") else "",
        stderr=text if stream in ("stderr", "both") else "",
    )

    with pytest.raises(ExternalCLINotAuthenticatedError) as caught:
        await _construct_with_login_status(result)

    _assert_no_secret(caught.value)
    assert caught.value.provider == "codex" and "3" in caught.value.detail


@pytest.mark.asyncio
@pytest.mark.parametrize("phrase", ["Not logged in", "LOGGED OUT", "not authenticated"])
@pytest.mark.parametrize("stream", ["stdout", "stderr", "both"])
async def test_a_zero_exit_logged_out_response_never_echoes_cli_output(
    stream: str, phrase: str
) -> None:
    text = f"{phrase}: key {_AUTH_SECRET}"
    result = CLIProcessResult(
        exit_code=0,
        stdout=text if stream in ("stdout", "both") else "",
        stderr=text if stream in ("stderr", "both") else "",
    )

    with pytest.raises(ExternalCLINotAuthenticatedError) as caught:
        await _construct_with_login_status(result)

    _assert_no_secret(caught.value)
    assert "not logged in" in caught.value.detail.lower()


@pytest.mark.asyncio
async def test_an_ambiguous_login_status_stays_typed_and_echoes_nothing() -> None:
    result = CLIProcessResult(exit_code=0, stdout=f"status {_AUTH_SECRET}", stderr="")

    with pytest.raises(ExternalCLINotAuthenticatedError) as caught:
        await _construct_with_login_status(result)

    _assert_no_secret(caught.value)
    assert "could not confirm" in caught.value.detail


@pytest.mark.asyncio
@pytest.mark.parametrize("text", ["Logged in using ChatGPT", "authenticated"])
async def test_a_logged_in_status_constructs_the_adapter(text: str) -> None:
    adapter = await _construct_with_login_status(
        CLIProcessResult(exit_code=0, stdout=text, stderr="")
    )

    assert adapter is not None
