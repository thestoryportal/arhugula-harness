"""Tests for U-RT-160b — ``harness resume WORKFLOW_FILE`` (spec v1.137 §D.3, §E, §F, §I.8, §I.10).

The subcommand names the handle and hands it to ``api.resume`` once; every refusal leaves as the
closed ``harness.resume-refusal.v1`` value with exit 6, or 7 for a claim refusal. The refusal
arms are raised from a stubbed ``api.resume`` carrying path, secret and tenant canaries; one
``protocol-not-bound`` runs through the real API against a shipped offline config.
"""

from __future__ import annotations

from collections.abc import Callable
from itertools import product
from pathlib import Path
from typing import Any, get_args

import pytest
from harness_runtime.api import ResumeDirectChildHandleError
from harness_runtime.cli.app import (
    EXIT_BOOTSTRAP_ERROR,
    EXIT_CONFIG_ERROR,
    EXIT_MANIFEST_ERROR,
    EXIT_PAUSED,
    EXIT_RESUME_CLAIM_REFUSED,
    EXIT_RESUME_REFUSED,
    EXIT_SUCCESS,
    EXIT_WORKFLOW_FAIL,
    app,
)
from harness_runtime.lifecycle.journal_workflow_pause_store import HandleUnknownCause
from harness_runtime.lifecycle.root_resume_admission import RootResumeRefusal
from harness_runtime.resume_refusal import (
    HandleCause,
    ResumeRefusalError,
    parse,
    project,
    to_json,
)

from .test_cli_one_shot import _RECONCILER_YAML, _run_result, _write_yaml, runner
from .test_cli_one_shot import mock_config_load as mock_config_load  # fixture
from .test_omarchy_offline_examples import _EXAMPLES, ROOT, SHARED_CONFIG, _load_config
from .test_omarchy_offline_examples import _no_harness_env as _no_harness_env  # autouse fixture
from .test_resume_refusal import SPEC_CASES, _claim, _handle

_CANARIES = ("CANARY", "/srv", "tenant-acme", "secret", "tok-")

# The §D.1 table rows, every root claim reason, every handle cause under both values of each
# flag, and the unknown depth: each reachable refusal value the CLI can be handed.
_REFUSALS: list[ResumeRefusalError] = [
    *(error for error, _ in SPEC_CASES),
    *(_claim(reason) for reason in RootResumeRefusal),
    *(
        _handle(cause, retryable=retryable, indeterminate=indeterminate)
        for cause, (retryable, indeterminate) in product(
            get_args(HandleUnknownCause), [(True, False), (False, True)]
        )
    ),
    ResumeDirectChildHandleError(depth=None),
]

# [LAW:one-source-of-truth] exception: transcribed from §F, not derived from the CLI, so that
# remapping any refusal kind to another exit fails here.
_EXIT_BY_KIND = {
    "arguments": 6,
    "handle": 6,
    "depth": 6,
    "protocol-not-bound": 6,
    "pause-state-stale": 6,
    "workflow-mismatch": 6,
    "step-index-out-of-range": 6,
    "pause-record-superseded": 6,
    "engine-pause-record-absent": 6,
    "engine-class-mismatch": 6,
    "claim": 7,
}


def test_the_refusal_cases_cover_every_kind_reason_cause_and_flag() -> None:
    refusals = [project(error) for error in _REFUSALS]
    assert {refusal.kind.value for refusal in refusals} == set(_EXIT_BY_KIND)
    assert {getattr(r, "reason", None) for r in refusals} >= set(RootResumeRefusal)
    assert {getattr(r, "cause", None) for r in refusals} >= set(HandleCause)
    assert {getattr(r, "retryable", None) for r in refusals} >= {True, False}
    assert {getattr(r, "indeterminate", None) for r in refusals} >= {True, False}
    assert {EXIT_RESUME_REFUSED, EXIT_RESUME_CLAIM_REFUSED} == set(_EXIT_BY_KIND.values())


@pytest.fixture
def mock_api_resume(monkeypatch: pytest.MonkeyPatch) -> Callable[..., list[dict[str, Any]]]:
    """Install a fake ``harness_runtime.api.resume``; returns the list of recorded calls."""

    def _install(
        *, result: Any = None, raises: BaseException | None = None
    ) -> list[dict[str, Any]]:
        calls: list[dict[str, Any]] = []

        async def _fake_resume(workflow: Any, **kwargs: Any) -> Any:
            calls.append({"workflow": workflow, **kwargs})
            if raises is not None:
                raise raises
            return result if result is not None else _run_result()

        monkeypatch.setattr("harness_runtime.api.resume", _fake_resume)
        return calls

    return _install


def test_resume_calls_api_resume_once_with_only_the_manifest_handle(
    tmp_path: Path,
    mock_config_load: Callable[..., None],
    mock_api_resume: Callable[..., list[dict[str, Any]]],
) -> None:
    mock_config_load()
    calls = mock_api_resume()
    result = runner.invoke(app, ["resume", str(_write_yaml(tmp_path))])

    assert result.exit_code == EXIT_SUCCESS, result.stdout + result.stderr
    [call] = calls
    assert call["resume_handle"] == call["workflow"].workflow_id == "wf-cli-one-shot"
    assert set(call) == {"workflow", "resume_handle", "config", "operator_decision"}
    assert call["operator_decision"] is None


@pytest.mark.parametrize(
    "flag",
    [
        ["--daemon"],
        ["--model", "m"],
        ["--provider", "p"],
        ["--socket-path", "/tmp/s"],
        ["--daemon-result-timeout-seconds", "5"],
    ],
)
def test_resume_offers_no_daemon_or_model_override(
    tmp_path: Path,
    flag: list[str],
    mock_config_load: Callable[..., None],
    mock_api_resume: Callable[..., list[dict[str, Any]]],
) -> None:
    mock_config_load()
    calls = mock_api_resume()
    result = runner.invoke(app, ["resume", str(_write_yaml(tmp_path)), *flag])

    assert result.exit_code == 2, result.stdout + result.stderr
    assert calls == []


@pytest.mark.parametrize("error", _REFUSALS, ids=lambda e: type(e).__name__)
def test_json_refusal_is_the_closed_value_once_on_stdout(
    tmp_path: Path,
    error: ResumeRefusalError,
    mock_config_load: Callable[..., None],
    mock_api_resume: Callable[..., list[dict[str, Any]]],
) -> None:
    mock_config_load()
    mock_api_resume(raises=error)
    result = runner.invoke(app, ["resume", str(_write_yaml(tmp_path)), "--output", "json"])

    refusal = project(error)
    assert result.exit_code == _EXIT_BY_KIND[refusal.kind.value]
    assert result.stdout == to_json(refusal) + "\n"
    assert parse(result.stdout.strip()) == refusal
    for canary in _CANARIES:
        assert canary not in result.stdout + result.stderr


@pytest.mark.parametrize("error", _REFUSALS, ids=lambda e: type(e).__name__)
def test_text_refusal_reports_kind_fail_class_and_facts_on_stderr(
    tmp_path: Path,
    error: ResumeRefusalError,
    mock_config_load: Callable[..., None],
    mock_api_resume: Callable[..., list[dict[str, Any]]],
) -> None:
    mock_config_load()
    mock_api_resume(raises=error)
    result = runner.invoke(app, ["resume", str(_write_yaml(tmp_path))])

    refusal = project(error)
    assert result.exit_code == _EXIT_BY_KIND[refusal.kind.value]
    assert result.stdout == ""
    [line] = result.stderr.splitlines()
    assert line.startswith("resume refused: ")
    assert f'kind="{refusal.kind.value}"' in line
    assert "fail_class=" in line
    for canary in _CANARIES:
        assert canary not in result.stderr


@pytest.mark.parametrize("output", ["text", "json"])
def test_a_real_config_without_the_pause_protocol_refuses_protocol_not_bound(
    tmp_path: Path, output: str
) -> None:
    _load_config(SHARED_CONFIG, tmp_path)
    manifest = ROOT / _EXAMPLES[0].path
    config_file = tmp_path / "harness.toml"
    result = runner.invoke(
        app, ["resume", str(manifest), "--config", str(config_file), "--output", output]
    )

    assert result.exit_code == EXIT_RESUME_REFUSED, result.stdout + result.stderr
    if output == "json":
        assert parse(result.stdout.strip()).kind.value == "protocol-not-bound"
    else:
        assert 'kind="protocol-not-bound"' in result.stderr


def test_a_missing_config_file_keeps_exit_three(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["resume", str(ROOT / _EXAMPLES[0].path), "--config", str(tmp_path / "absent.toml")],
    )

    assert result.exit_code == EXIT_CONFIG_ERROR, result.stdout + result.stderr
    assert "RT-FAIL-CLI-CONFIG-LOAD" in result.stderr


@pytest.mark.parametrize(
    ("status", "exit_code"),
    [("completed", EXIT_SUCCESS), ("paused", EXIT_PAUSED), ("failed", EXIT_WORKFLOW_FAIL)],
)
def test_resume_result_status_keeps_the_run_exit_codes(
    tmp_path: Path,
    status: str,
    exit_code: int,
    mock_config_load: Callable[..., None],
    mock_api_resume: Callable[..., list[dict[str, Any]]],
) -> None:
    mock_config_load()
    mock_api_resume(result=_run_result(status=status))
    result = runner.invoke(app, ["resume", str(_write_yaml(tmp_path))])

    assert result.exit_code == exit_code, result.stdout + result.stderr


def test_an_inadmissible_manifest_keeps_exit_two(
    tmp_path: Path,
    mock_config_load: Callable[..., None],
    mock_api_resume: Callable[..., list[dict[str, Any]]],
) -> None:
    mock_config_load()
    calls = mock_api_resume()
    result = runner.invoke(app, ["resume", str(_write_yaml(tmp_path, body=_RECONCILER_YAML))])

    assert result.exit_code == EXIT_MANIFEST_ERROR, result.stdout + result.stderr
    assert calls == []


def test_a_bootstrap_failure_keeps_exit_four(
    tmp_path: Path,
    mock_config_load: Callable[..., None],
    mock_api_resume: Callable[..., list[dict[str, Any]]],
) -> None:
    from harness_runtime.bootstrap import BootstrapFailure
    from harness_runtime.types import BootstrapStage

    mock_config_load()
    mock_api_resume(raises=BootstrapFailure(BootstrapStage.LOOP_INIT, RuntimeError("boom")))
    result = runner.invoke(app, ["resume", str(_write_yaml(tmp_path))])

    assert result.exit_code == EXIT_BOOTSTRAP_ERROR, result.stdout + result.stderr
    assert "RT-FAIL-BOOTSTRAP" in result.stderr
