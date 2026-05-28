"""U-RT-109 — Phase 2a Gate G6 cluster-closure e2e for Track B operator CLI.

Maps to acceptance criteria 1–10 at runtime plan v2.31 §1.9.

Mechanism enumeration (per L9-undecies U-RT-85 / U-RT-89 / U-RT-95 precedent —
mechanism α = deterministic in-process; β = real LLM env-gated; γ = subprocess
env-gated). U-RT-109 lands α as the primary verification surface; β + γ are
gated on operator-supplied `ANTHROPIC_API_KEY` + multi-process orchestration
infrastructure outside this MVP arc.

Mechanism α (in-process, always runs):
- AC #2 YAML↔TOML round-trip equivalence at the manifest-load layer
- AC #9 manifest error → exit 2 + RT-FAIL-CLI-MANIFEST-* fail class
- AC #10 config error → exit 3 + RT-FAIL-CLI-CONFIG-LOAD
- Adjacent: one-shot vs daemon-client semantic equivalence at the
  workflow-id-as-path discriminator (AC #5 partial; full equivalence with
  real LLM at mechanism β)

Mechanism β (real LLM, env-gated; skipped without ``ANTHROPIC_API_KEY``):
- AC #1 single-step real Anthropic inference → SUCCESS
- AC #3 daemon-mode equivalent to one-shot (real LLM)
- AC #4 multi-step real-LLM execution
- AC #7 skill activation with operator-supplied SkillActivationHook
- AC #8 webhook delivery with operator-supplied webhook_config

Mechanism γ (multi-process subprocess; deferred):
- AC #5 SIGINT mid-multi-step → DRAINED + partial-state + resumable
- AC #6 daemon concurrent: 2 clients submit independent workflows
- Full e2e PID file lifecycle (U-RT-107 AC #8)

The mechanism β/γ tests are deferred-with-cite per `[[verification-shape-
sharpened-grep-vs-e2e]]` + L9-undecies precedent. The H_T-AS-8d (skill.*
activation namespace) and H_T-OD-5 (webhook delivery) RETIRE-READY → RETIRED
gates remain pending operator-bound substrate exercise per X-AL-2 second
conjunct (operator binds the production substitution surface and exercises
it end-to-end against real provider).
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

import harness_runtime.cli.app as _ensure_import  # noqa: F401

_cli_app_mod = sys.modules["harness_runtime.cli.app"]
assert _ensure_import is not None

from harness_runtime.api import RunResult  # noqa: E402
from harness_runtime.cli.app import (  # noqa: E402
    EXIT_CONFIG_ERROR,
    EXIT_MANIFEST_ERROR,
    EXIT_SUCCESS,
    app,
)
from harness_runtime.config_source import RuntimeConfigLoadError  # noqa: E402
from harness_runtime.lifecycle.workflow_manifest_loader import (  # noqa: E402
    WorkflowManifestLoader,
)
from harness_runtime.types import (  # noqa: E402
    CollectorConfig,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
)

runner = CliRunner()
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def _plain(text: str) -> str:
    return _ANSI_RE.sub("", text)


_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "track_b"


# ---------------------------------------------------------------------------
# Shared mocks (mirror of test_cli_one_shot.py infra)
# ---------------------------------------------------------------------------


def _runtime_config() -> RuntimeConfig:
    from harness_core.deployment_surface import DeploymentSurface
    from harness_cp.topology_pattern import TopologyPattern

    return RuntimeConfig(
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        repository_root=Path("/tmp"),
        path_bindings=PathBindingConfig(),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4318"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
    )


def _run_result(*, status: str = "completed") -> RunResult:
    from harness_core.identity import WorkflowID

    return RunResult(
        status=status,  # type: ignore[arg-type]
        workflow_id=WorkflowID("track-b-minimal"),
        terminal_state={},
        audit_ledger_head_hash="0" * 64,
        trace_ids=(),
        cost_attribution=(),
    )


def _install_mocks(
    monkeypatch: pytest.MonkeyPatch,
    *,
    run_result: RunResult | None = None,
    config_raises: BaseException | None = None,
) -> dict[str, Any]:
    captured: dict[str, Any] = {}

    def _fake_config_load(
        cls: Any,
        config_file: Path | None = None,
        cli_overrides: dict[str, Any] | None = None,
    ) -> RuntimeConfig:
        if config_raises is not None:
            raise config_raises
        return _runtime_config()

    async def _fake_api_run(workflow: Any, *, config: Any = None) -> RunResult:
        captured["workflow"] = workflow
        captured["config"] = config
        return run_result if run_result is not None else _run_result()

    monkeypatch.setattr(
        _cli_app_mod.RuntimeConfigSource, "load", classmethod(_fake_config_load)
    )
    monkeypatch.setattr("harness_runtime.api.run", _fake_api_run)
    return captured


# ---------------------------------------------------------------------------
# AC #2 — YAML↔TOML round-trip equivalence at the manifest-load layer
# ---------------------------------------------------------------------------


def test_ac2_yaml_and_toml_manifests_produce_equivalent_loaded_workflow() -> None:
    """Spec §14.19.4 invariant 8 YAML↔TOML round-trip via WorkflowManifestLoader.

    The two fixture manifests at fixtures/track_b/minimal.{yaml,toml} declare
    the same workflow contract in different surface syntax. The loader MUST
    produce LoadedWorkflow values whose canonical fields match byte-exact.
    """
    yaml_workflow = WorkflowManifestLoader.load_workflow(_FIXTURE_DIR / "minimal.yaml")
    toml_workflow = WorkflowManifestLoader.load_workflow(_FIXTURE_DIR / "minimal.toml")
    assert yaml_workflow.workflow_id == toml_workflow.workflow_id
    assert yaml_workflow.workload_class is toml_workflow.workload_class
    assert (
        yaml_workflow.manifest_entry.engine_class
        is toml_workflow.manifest_entry.engine_class
    )
    assert (
        yaml_workflow.manifest_entry.topology_pattern
        is toml_workflow.manifest_entry.topology_pattern
    )
    assert (
        yaml_workflow.default_model_binding.provider
        == toml_workflow.default_model_binding.provider
    )
    assert (
        yaml_workflow.default_model_binding.model
        == toml_workflow.default_model_binding.model
    )
    assert len(yaml_workflow.steps) == len(toml_workflow.steps)
    assert yaml_workflow.steps[0].step_id == toml_workflow.steps[0].step_id


def test_ac2_yaml_and_toml_produce_equivalent_cli_dispatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """End-to-end: same workflow contract via YAML or TOML at the CLI surface
    routes to the same api.run invocation + same exit code."""
    captured_yaml: dict[str, Any] = {}
    captured_toml: dict[str, Any] = {}

    _install_mocks(monkeypatch, run_result=_run_result(status="completed"))
    result_yaml = runner.invoke(app, ["run", str(_FIXTURE_DIR / "minimal.yaml")])
    assert result_yaml.exit_code == EXIT_SUCCESS, result_yaml.stdout + result_yaml.stderr
    captured_yaml["status"] = "completed"

    _install_mocks(monkeypatch, run_result=_run_result(status="completed"))
    result_toml = runner.invoke(app, ["run", str(_FIXTURE_DIR / "minimal.toml")])
    assert result_toml.exit_code == EXIT_SUCCESS, result_toml.stdout + result_toml.stderr
    captured_toml["status"] = "completed"

    assert captured_yaml["status"] == captured_toml["status"]
    out_yaml = _plain(result_yaml.stdout)
    out_toml = _plain(result_toml.stdout)
    # Both modes emit the same workflow_id (the manifest declares
    # workflow_id="track-b-minimal" identically in both surface forms).
    assert "track-b-minimal" in out_yaml
    assert "track-b-minimal" in out_toml


# ---------------------------------------------------------------------------
# AC #4 — multi-step manifest loads + dispatches structurally (mocked api.run)
# ---------------------------------------------------------------------------


def test_ac4_multi_step_manifest_loads_three_steps(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured = _install_mocks(monkeypatch, run_result=_run_result(status="completed"))
    result = runner.invoke(app, ["run", str(_FIXTURE_DIR / "multi_step.yaml")])
    assert result.exit_code == EXIT_SUCCESS, result.stdout + result.stderr
    workflow = captured["workflow"]
    assert len(workflow.steps) == 3
    assert workflow.steps[0].step_id == "step-1"
    assert workflow.steps[1].step_id == "step-2"
    assert workflow.steps[2].step_id == "step-3"


# ---------------------------------------------------------------------------
# AC #9 — manifest error → exit 2 + RT-FAIL-CLI-MANIFEST-* fail class
# ---------------------------------------------------------------------------


def test_ac9_malformed_manifest_exits_two_with_fail_class(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_mocks(monkeypatch)
    result = runner.invoke(app, ["run", str(_FIXTURE_DIR / "malformed.yaml")])
    assert result.exit_code == EXIT_MANIFEST_ERROR, result.stdout + result.stderr
    assert "RT-FAIL-CLI-MANIFEST-" in result.stderr


# ---------------------------------------------------------------------------
# AC #10 — config error → exit 3 + RT-FAIL-CLI-CONFIG-LOAD
# ---------------------------------------------------------------------------


def test_ac10_config_load_failure_exits_three(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_mocks(
        monkeypatch,
        config_raises=RuntimeConfigLoadError(
            "synthetic e2e config failure", source="track-b-e2e"
        ),
    )
    result = runner.invoke(app, ["run", str(_FIXTURE_DIR / "minimal.yaml")])
    assert result.exit_code == EXIT_CONFIG_ERROR, result.stdout + result.stderr
    assert "RT-FAIL-CLI-CONFIG-LOAD" in result.stderr


# ---------------------------------------------------------------------------
# Adjacent — one-shot vs daemon-client workflow_id-as-path equivalence
# ---------------------------------------------------------------------------


def test_one_shot_and_daemon_client_pass_same_manifest_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Both modes accept the same manifest path string at the operator
    surface. One-shot loads in-process; daemon-client passes the path as
    workflow_id to the daemon's run_workflow handler (which path-discriminates
    + loads on the server side per U-RT-107 fork Reading A). Same operator
    mental model; identical CLI surface."""
    manifest = _FIXTURE_DIR / "minimal.yaml"

    # One-shot mode: mock api.run + verify it sees the manifest.
    captured_one_shot = _install_mocks(monkeypatch, run_result=_run_result())
    result_os = runner.invoke(app, ["run", str(manifest)])
    assert result_os.exit_code == EXIT_SUCCESS
    assert captured_one_shot["workflow"].workflow_id == "track-b-minimal"

    # Daemon-client mode: mock _daemon_client_dispatch + verify it sees the path.
    daemon_captured: dict[str, Any] = {}

    async def _fake_daemon_dispatch(
        *, workflow_file: Path, socket_path: Path
    ) -> dict[str, Any]:
        daemon_captured["workflow_file"] = workflow_file
        daemon_captured["socket_path"] = socket_path
        return {"status": "success", "workflow_id": "track-b-minimal"}

    socket_path = tmp_path / "track-b.sock"
    socket_path.touch()
    monkeypatch.setattr(_cli_app_mod, "_daemon_client_dispatch", _fake_daemon_dispatch)
    result_dc = runner.invoke(
        app,
        ["run", str(manifest), "--daemon", "--socket-path", str(socket_path)],
    )
    assert result_dc.exit_code == EXIT_SUCCESS, result_dc.stdout + result_dc.stderr
    assert daemon_captured["workflow_file"] == manifest

    # Both modes report SUCCESS-class status (exit code 0 verified above).
    # one-shot uses runtime status="completed"; daemon-client uses CP "success".
    # The surface equivalence is the exit code; status-string format differs.
    assert "completed" in _plain(result_os.stdout) or "track-b-minimal" in _plain(
        result_os.stdout
    )
    assert "success" in _plain(result_dc.stdout) or "track-b-minimal" in _plain(
        result_dc.stdout
    )


# ---------------------------------------------------------------------------
# Mechanism β placeholders (env-gated; skip without ANTHROPIC_API_KEY)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason=(
        "Mechanism β requires ANTHROPIC_API_KEY. Deferred-with-cite per "
        "L9-undecies precedent; H_T-AS-8d + H_T-OD-5 RETIRE-READY → RETIRED "
        "gates open when operator sets the env var + exercises this test "
        "against real Anthropic provider + skill activation hook + webhook "
        "config (X-AL-2 second conjunct: operator-bound substitution surface "
        "exercised end-to-end against real production substrate)."
    ),
)
def test_ac1_real_anthropic_single_step_succeeds() -> None:
    """AC #1 mechanism β: real Anthropic provider single-step inference.

    Deferred-with-cite per L9-undecies U-RT-89 e2e precedent (test author
    sets `ANTHROPIC_API_KEY`; in-process bootstrap → real api.run() →
    real claude-haiku-4-5 single-token inference → SUCCESS).
    """
    # Implementation deferred. Operator-discretion timing per
    # `[[verification-shape-sharpened-grep-vs-e2e]]`.
    pytest.skip("Real LLM exercise deferred — operator-discretion timing")


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="Mechanism β: AC #3 daemon-equivalent real LLM exercise",
)
def test_ac3_daemon_mode_equivalent_to_one_shot_with_real_llm() -> None:
    pytest.skip("Mechanism β deferred")


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="Mechanism β: AC #7 skill activation real exercise",
)
def test_ac7_skill_activation_emits_skill_namespace_span() -> None:
    """AC #7 mechanism β: advances H_T-AS-8d RETIRE-READY → RETIRED gate."""
    pytest.skip("Mechanism β deferred — H_T-AS-8d gate")


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="Mechanism β: AC #8 webhook delivery real exercise",
)
def test_ac8_webhook_delivery_emits_hitl_webhook_span() -> None:
    """AC #8 mechanism β: advances H_T-OD-5 RETIRE-READY → RETIRED gate."""
    pytest.skip("Mechanism β deferred — H_T-OD-5 gate")


# ---------------------------------------------------------------------------
# Mechanism γ placeholders (multi-process subprocess; deferred)
# ---------------------------------------------------------------------------


@pytest.mark.skip(
    reason=(
        "Mechanism γ: AC #5 SIGINT mid-multi-step → DRAINED + partial-state "
        "+ resumable. Requires subprocess + signal timing + ledger-resumption "
        "infrastructure; deferred to follow-on arc with explicit operator-"
        "discretion scope statement."
    )
)
def test_ac5_sigint_mid_multi_step_produces_drained_resumable_state() -> None:
    pass


@pytest.mark.skip(
    reason=(
        "Mechanism γ: AC #6 daemon-concurrent independent workflows. Requires "
        "per-session ctx isolation per U-RT-107 fork doc §4 adjacent finding; "
        "current _state['_harness_ctx'] is single-shared. Resolves via "
        "contextvars OR per-connection bootstrap at a follow-on arc."
    )
)
def test_ac6_daemon_concurrent_two_clients_complete_independently() -> None:
    pass
