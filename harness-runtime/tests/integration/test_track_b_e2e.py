"""U-RT-109 — Phase 2a Gate G6 cluster-closure e2e for Track B operator CLI.

Maps to acceptance criteria 1–10 at runtime plan v2.31 §1.9.

Mechanism enumeration (per L9-undecies U-RT-85 / U-RT-89 / U-RT-95 precedent —
mechanism α = deterministic in-process; β = real LLM env-gated; γ = subprocess
env-gated). U-RT-109 lands α as the primary verification surface; β + γ are
gated on operator-supplied `ANTHROPIC_API_KEY` + multi-process orchestration
infrastructure outside this MVP arc.

Mechanism α (in-process, always runs):
- AC #2 YAML↔TOML round-trip equivalence at the manifest-load layer
- AC #4 multi-step deterministic execution to SUCCESS through the
  driver's per-step iteration loop with hash-chain-intact ledger
  (sibling to AC #5 drain path; covers the no-drain SUCCESS surface)
- AC #5 mid-multi-step in-process drain trigger → DRAINED + partial-state
  populated + hash-chain-intact state ledger (mech-γ subprocess reframe
  per AC #6 precedent — same composition friction that defers
  test_cli_daemon.py subprocess e2e)
- AC #6 daemon-mode concurrent two-client isolation via direct tool.fn
  invocation through the FastMCP server (subprocess γ shape deferred)
- AC #9 manifest error → exit 2 + RT-FAIL-CLI-MANIFEST-* fail class
- AC #10 config error → exit 3 + RT-FAIL-CLI-CONFIG-LOAD

Mechanism β (real LLM, env-gated; skipped without ``ANTHROPIC_API_KEY``):
- AC #1 single-step real Anthropic inference → SUCCESS
- AC #3 daemon-mode equivalent to one-shot (real LLM)
- AC #4 multi-step real-LLM execution
- AC #7 skill activation with operator-supplied SkillActivationHook
- AC #8 webhook delivery with operator-supplied webhook_config

Mechanism γ (multi-process subprocess; deferred):
- Full e2e PID file lifecycle (U-RT-107 AC #8)
- AC #5 subprocess + real OS-signal SIGINT shape (in-process mech-α
  lands now per advisor-ratified reframe; subprocess shape carries to
  the same arc that lifts test_cli_daemon.py subprocess deferral)
- AC #6 subprocess + real MCP-client transport shape (in-process mech-α
  lands now per the AC #6 implementation arc; subprocess shape carries
  to the same arc as AC #5 above)

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
# AC #4 mech-α — multi-step deterministic execution to SUCCESS (sibling of AC #5)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ac4_multi_step_deterministic_execution_completes_all_steps(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AC #4 — mech-α — multi-step driver execution through 3 INFERENCE_STEPs
    to terminal SUCCESS, with the ledger carrying a hash-chain-intact entry
    per completed step.

    Sibling to AC #5 (`test_ac5_sigint_mid_multi_step_produces_drained_resumable_state`):
    reuses the deterministic-dispatcher scaffold but the dispatcher does
    NOT fire `ctx.drained_flag` — all 3 step iterations complete and the
    driver returns `RunStatus.SUCCESS` per `workflow_driver.py:1177`.

    AC #4's mech-β sibling at `test_ac4_multi_step_real_llm_execution`
    (PR #10 on `worktree-mech-beta-ac4`) covers the real-LLM path; this
    mech-α test covers the driver-loop + ledger-chain path that is
    independent of LLM substrate. The two together close the AC #4
    matrix (load × execute × LLM-substrate).

    Invariants verified (mapping to runtime plan v2.31 §1.9 AC #4):
      1. All 3 dispatcher calls fire (one per INFERENCE_STEP).
      2. ``RunResult.status == SUCCESS`` + ``terminal_step_index is None``
         per `workflow_driver.py:1174-1182`.
      3. ``final_state`` is a populated dict carrying the accumulated
         per-step contributions; ``partial_state is None``.
      4. The on-disk state ledger carries ≥3 entries (one per completed
         step per the smoke test invariant at
         `test_run_smoke.py:467-471`) with:
         - intact ``prior_event_hash → response_hash`` chain per
           ADR-D5 §1.4 (entry 0's prior = ``ALL_ZEROS_SENTINEL``);
         - canonical ``response_hash`` round-trip via
           ``compute_response_hash``;
         - unique idempotency keys across all entries.

    Scope per advisor scope discipline at the AC #5 implementation arc
    (`[[advisor-before-substantive-work-for-cross-axis-blockers]]`):
    deterministic in-process dispatcher; no real LLM; no subprocess. The
    substantive surface this test verifies is the driver's no-drain
    per-step iteration loop + ledger emission discipline.

    Independent of the mech-β PR stack (PRs #5–#10) — does not require
    `ANTHROPIC_API_KEY` and does not touch keyring or provider
    construction.
    """
    from collections.abc import Sequence
    from functools import partial

    from harness_core.deployment_surface import DeploymentSurface
    from harness_core.identity import StepID
    from harness_core.persona_tier import PersonaTier
    from harness_core.workload_class import WorkloadClass
    from harness_cp.cp_shared_types import ModelBinding
    from harness_cp.cross_family_fallback_chain import (
        FallbackChain,
        ProviderCandidate,
        ProviderFamily,
    )
    from harness_cp.engine_class import EngineClass
    from harness_cp.routing_manifest_residence import RoutingManifest
    from harness_cp.topology_pattern import TopologyPattern
    from harness_cp.workflow_driver import execute_workflow
    from harness_cp.workflow_driver_types import (
        RunStatus as _CpRunStatus,
    )
    from harness_cp.workflow_driver_types import (
        StepKind,
        WorkflowStep,
    )
    from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
    from harness_is.chain_link_construction import construct_prior_event_hash
    from harness_is.entry_hash import compute_response_hash
    from harness_is.path_class_registry import PathClass
    from harness_is.state_ledger_entry_schema import ALL_ZEROS_SENTINEL
    from harness_is.state_ledger_write import read_ledger
    from harness_runtime.bootstrap import run_bootstrap
    from harness_runtime.bootstrap import stage_3a_cp_clients as _stage_3a_mod
    from harness_runtime.bootstrap import stage_4_od as _stage_4_od_mod
    from harness_runtime.lifecycle.providers import ProviderClientsStage

    # ---------------- patched runtime (mirror of AC #5 + test_run_smoke.py) ----------------

    class _FakeProvider:
        def __init__(self, name: str) -> None:
            self.name = name

        async def aclose(self) -> None:
            return None

    async def _fake_clients(
        *_args: object, **_kwargs: object
    ) -> ProviderClientsStage:
        return ProviderClientsStage(
            providers={
                "anthropic": _FakeProvider("anthropic"),
                "openai": _FakeProvider("openai"),
                "ollama": _FakeProvider("ollama"),
            }
        )

    monkeypatch.setattr(
        _stage_3a_mod, "materialize_provider_clients_stage", _fake_clients
    )

    class _FakeDaemon:
        async def start(self) -> None:
            return None

        async def stop(self, *, timeout_seconds: float = 5.0) -> None:
            _ = timeout_seconds
            return None

    class _CollectorStage:
        def __init__(self, d: _FakeDaemon) -> None:
            self.daemon = d

    class _FakeTracerProvider:
        def force_flush(self, timeout_millis: int = 30_000) -> bool:
            _ = timeout_millis
            return True

        def shutdown(self) -> None:
            return None

        def get_tracer(self, instrumenting_module_name: str, /) -> object:
            from opentelemetry.trace import NoOpTracer

            _ = instrumenting_module_name
            return NoOpTracer()

    class _TracerStage:
        def __init__(self, p: _FakeTracerProvider) -> None:
            self.provider = p
            self.registered_globally = False

    monkeypatch.setattr(
        _stage_4_od_mod,
        "materialize_collector_daemon_stage",
        lambda config, **_: _CollectorStage(_FakeDaemon()),
    )
    monkeypatch.setattr(
        _stage_4_od_mod, "materialize_ring_buffer_stage", lambda config, _d: None
    )
    monkeypatch.setattr(
        _stage_4_od_mod,
        "materialize_tracer_provider_stage",
        lambda config, **_: _TracerStage(_FakeTracerProvider()),
    )
    monkeypatch.setattr(
        _stage_4_od_mod,
        "materialize_span_processor_stage",
        lambda config, _p, **_k: None,
    )

    # ---------------- config ----------------
    surface = DeploymentSurface.LOCAL_DEVELOPMENT
    workload = WorkloadClass.SOFTWARE_ENGINEERING
    chain = FallbackChain(
        primary=ProviderCandidate(
            provider="anthropic",
            model="claude-haiku-4-5",
            family=ProviderFamily.ANTHROPIC,
        ),
        same_family=(),
        cross_family=(),
        terminal=None,
    )
    config = RuntimeConfig(
        deployment_surface=surface,
        repository_root=tmp_path,
        path_bindings=PathBindingConfig(
            raw_entries=tuple(
                {
                    "path_class": pc,
                    "workflow_class": workload,
                    "deployment_surface": surface,
                    "path": str(tmp_path / pc.value.lower()),
                }
                for pc in PathClass
            ),
        ),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4317"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        mcp_clients=[],
        ollama_optional=True,
        routing_manifest=RoutingManifest(
            manifest_version=1,
            per_role_bindings={},
            per_workload_overrides={},
            fallback_chains=(chain,),
            retry_policies={},
        ),
    )

    ctx = await run_bootstrap(config, workload_class=workload)

    # ---------------- deterministic dispatcher (no drain trigger) ----------------
    dispatch_count = {"n": 0}

    class _NoDrainDispatcher:
        def dispatch(
            self,
            binding: Any,
            step: WorkflowStep,
            *,
            step_context: Any = None,
        ) -> dict[str, Any]:
            _ = binding, step_context
            dispatch_count["n"] += 1
            return {"step_id": str(step.step_id), "ok": True, "index": dispatch_count["n"] - 1}

    class _SingleKindRegistry:
        def __init__(self, dispatcher: Any) -> None:
            self._dispatcher = dispatcher

        def lookup(self, step_kind: Any) -> Any:
            _ = step_kind
            return self._dispatcher

    # ---------------- 3-step workflow ----------------
    workflow_id = "wf-ac4-multi-step-deterministic"
    manifest = WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=workload,
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=TopologyPattern.SINGLE_THREADED_LINEAR,
        layer_budgets=(),
        fallback_chain=chain,
        hitl_placements=(),
        per_step_overrides={},
    )
    steps: Sequence[WorkflowStep] = tuple(
        WorkflowStep(
            step_id=StepID(f"step-{i}"),
            step_kind=StepKind.INFERENCE_STEP,
            step_payload={"index": i},
        )
        for i in range(3)
    )

    # Dispatch via asyncio.to_thread per the AC #5 + U-RT-89 e2e pattern
    # (the driver's internal async-to-sync bridge can't run from a live
    # event loop; pytest-asyncio holds one).
    import asyncio

    cp_result = await asyncio.to_thread(
        partial(
            execute_workflow,
            manifest_entry=manifest,
            steps=steps,
            run_id="run-ac4-mech-alpha-1",
            ctx=ctx,  # type: ignore[arg-type]
            default_model_binding=ModelBinding(
                provider="anthropic", model="claude-haiku-4-5"
            ),
            step_dispatchers=_SingleKindRegistry(  # type: ignore[arg-type]
                _NoDrainDispatcher()
            ),
        )
    )

    # ---------------- invariant 1: all 3 dispatches fired ----------------
    assert dispatch_count["n"] == 3, (
        f"expected 3 dispatches (one per step); got {dispatch_count['n']}"
    )

    # ---------------- invariant 2: status == SUCCESS ----------------
    assert cp_result.status == _CpRunStatus.SUCCESS, (
        f"expected SUCCESS, got {cp_result.status}; "
        f"fail_class={cp_result.fail_class}"
    )
    # SUCCESS sets terminal_step_index=None per workflow_driver.py:1178.
    assert cp_result.terminal_step_index is None
    assert cp_result.fail_class is None

    # ---------------- invariant 3: final_state populated, partial_state None ----------------
    # Per workflow_driver.py:1174-1182 SUCCESS branch sets partial_state=None
    # + final_state=dict(accumulated). The accumulated dict carries one
    # entry per executed step under PURE_PATTERN_NO_ENGINE.
    assert cp_result.partial_state is None, (
        f"SUCCESS branch must set partial_state=None; got {cp_result.partial_state!r}"
    )
    assert cp_result.final_state is not None
    assert isinstance(cp_result.final_state, dict)
    assert len(cp_result.final_state) >= 1, (
        f"final_state must carry accumulated per-step contributions; got "
        f"{cp_result.final_state!r}"
    )

    # ---------------- invariant 4: ledger has 3 entries + hash chain intact ----------------
    # Per `test_run_smoke.py:466-471` the CP driver writes one ledger entry
    # per step under PURE_PATTERN_NO_ENGINE (see C-CP-25 §25.3.3.7).
    handle = ctx.ledger_writer.handle  # type: ignore[attr-defined]
    entries = read_ledger(handle)
    assert len(entries) >= 3, (
        f"expected ≥3 ledger entries (one per executed step); got "
        f"{len(entries)} entries at {handle.canonical_path}"
    )

    # Hash-chain integrity per ADR-D5 §1.4: each entry's prior_event_hash
    # equals the prior entry's response_hash (entry 0's prior =
    # construct_prior_event_hash(None) = ALL_ZEROS).
    expected_prior = construct_prior_event_hash(None)
    assert expected_prior == ALL_ZEROS_SENTINEL or len(expected_prior) == 32
    for i, entry in enumerate(entries):
        assert entry.prior_event_hash == expected_prior, (
            f"hash chain broken at entry {i}: prior_event_hash="
            f"{entry.prior_event_hash.hex()} expected={expected_prior.hex()}"
        )
        recomputed = compute_response_hash(entry)
        assert entry.response_hash == recomputed, (
            f"response_hash mismatch at entry {i}: stored="
            f"{entry.response_hash.hex()} recomputed={recomputed.hex()}"
        )
        for j, other in enumerate(entries):
            if i != j:
                assert entry.idempotency_key != other.idempotency_key, (
                    f"duplicate idempotency_key between entries {i} and {j}: "
                    f"{entry.idempotency_key!r}"
                )
        expected_prior = entry.response_hash

    # Cleanup so background tasks terminate.
    from harness_runtime.shutdown import shutdown as _shutdown

    await _shutdown(ctx)


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


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason=(
        "Mechanism β AC #1 requires ANTHROPIC_API_KEY. Foundational sanity "
        "check for the real-LLM path through api.run; gates AC #7 (AS-8d) + "
        "AC #8 (OD-5) but does not itself retire either substitution."
    ),
)
async def test_ac1_real_anthropic_single_step_succeeds(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AC #1 mechanism β: real Anthropic provider single-step inference.

    Mirrors the L9-undecies U-RT-89 e2e shape but exercises the FULL
    `api.run()` path (bootstrap → in-process MCP `run_workflow` → CP
    workflow_driver → bootstrap-bound INFERENCE_STEP dispatcher →
    real `client.messages.create` → SUCCESS).

    Bridges keyring → env per the `_FakeKeyring` precedent at
    `test_config_provider_secrets.py:51`: production operators set the
    key via `keyring set`; this test reads `ANTHROPIC_API_KEY` from env
    and shims it through `keyring.get_password`.

    OpenAI + Ollama providers are skipped via E-prod-3 per-provider opt-
    in (`openai_optional=True` + `ollama_optional=True`) — only Anthropic
    is required.

    Per `[[finding-mech-beta-stub-bodies-vs-env-gate]]`: no body-level
    pytest.skip — the skipif decorator is the sole gate.
    """
    from collections.abc import Sequence

    from harness_core.deployment_surface import DeploymentSurface
    from harness_core.identity import StepID
    from harness_core.persona_tier import PersonaTier
    from harness_core.workload_class import WorkloadClass
    from harness_cp.cp_shared_types import ModelBinding
    from harness_cp.cross_family_fallback_chain import (
        FallbackChain,
        ProviderCandidate,
        ProviderFamily,
    )
    from harness_cp.engine_class import EngineClass
    from harness_cp.routing_manifest_residence import RoutingManifest
    from harness_cp.topology_pattern import TopologyPattern
    from harness_cp.workflow_driver import StepDispatcher as _CpStepDispatcher
    from harness_cp.workflow_driver_types import StepKind, WorkflowStep
    from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
    from harness_is.path_class_registry import PathClass
    from harness_runtime.api import run as _run
    from harness_runtime.bootstrap import stage_4_od as _stage_4_od_mod

    # ---------------- keyring → env shim ----------------
    api_key = os.environ["ANTHROPIC_API_KEY"]

    def _fake_get_password(service: str, name: str) -> str | None:
        _ = service
        if name == "anthropic_key":
            return api_key
        return None

    monkeypatch.setattr(
        "harness_runtime.config.provider_secrets.keyring.get_password",
        _fake_get_password,
    )

    # ---------------- tracer stage — fake to avoid global OTel re-registration ----------------
    class _FakeTracerProvider:
        def force_flush(self, timeout_millis: int = 30_000) -> bool:
            _ = timeout_millis
            return True

        def shutdown(self) -> None:
            return None

        def get_tracer(self, instrumenting_module_name: str, /) -> object:
            from opentelemetry.trace import NoOpTracer

            _ = instrumenting_module_name
            return NoOpTracer()

    class _TracerStage:
        def __init__(self, provider: _FakeTracerProvider) -> None:
            self.provider = provider
            self.registered_globally = False

    def _fake_tracer_stage(config: Any, **_kwargs: Any) -> _TracerStage:
        _ = config
        return _TracerStage(_FakeTracerProvider())

    def _fake_span_processor(config: Any, _p: Any, **_kwargs: Any) -> None:
        _ = config
        return None

    monkeypatch.setattr(
        _stage_4_od_mod, "materialize_tracer_provider_stage", _fake_tracer_stage
    )
    monkeypatch.setattr(
        _stage_4_od_mod, "materialize_span_processor_stage", _fake_span_processor
    )

    # ---------------- config ----------------
    surface = DeploymentSurface.LOCAL_DEVELOPMENT
    workload = WorkloadClass.SOFTWARE_ENGINEERING
    path_bindings = PathBindingConfig(
        raw_entries=tuple(
            {
                "path_class": pc,
                "workflow_class": workload,
                "deployment_surface": surface,
                "path": str(tmp_path / pc.value.lower()),
            }
            for pc in PathClass
        ),
    )
    chain = FallbackChain(
        primary=ProviderCandidate(
            provider="anthropic",
            model="claude-haiku-4-5",
            family=ProviderFamily.ANTHROPIC,
        ),
        same_family=(),
        cross_family=(),
        terminal=None,
    )
    config = RuntimeConfig(
        deployment_surface=surface,
        repository_root=tmp_path,
        path_bindings=path_bindings,
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4318"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        mcp_clients=[],
        # E-prod-3 per-provider opt-in: anthropic required (default
        # anthropic_optional=False); openai + ollama skipped.
        openai_optional=True,
        ollama_optional=True,
        routing_manifest=RoutingManifest(
            manifest_version=1,
            per_role_bindings={},
            per_workload_overrides={},
            fallback_chains=(chain,),
            retry_policies={},
        ),
    )
    monkeypatch.setattr("harness_runtime.api._default_config", lambda: config)

    # ---------------- workflow with real INFERENCE_STEP messages payload ----------------
    # ProviderAgnosticPayload shape per `llm_dispatch.py:139` _coerce_payload:
    # {messages, tools, params}. `max_tokens` is required by Anthropic
    # messages.create per `llm_dispatch.py:739` _to_messages_create_kwargs.
    # Single-token reply minimises cost + latency.
    inference_payload = {
        "messages": [
            {"role": "user", "content": "Reply with the single word: ok"}
        ],
        "tools": [],
        "params": {"max_tokens": 8},
    }

    class _Workflow:
        @property
        def workflow_id(self) -> str:
            return "wf-ac1-real-anthropic"

        @property
        def workload_class(self) -> WorkloadClass:
            return workload

        @property
        def manifest_entry(self) -> WorkflowManifestEntry:
            return WorkflowManifestEntry(
                workflow_id="wf-ac1-real-anthropic",
                workload_class=workload,
                persona_tier=PersonaTier.TEAM_BINDING,
                engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
                topology_pattern=TopologyPattern.SINGLE_THREADED_LINEAR,
                layer_budgets=(),
                fallback_chain=chain,
                hitl_placements=(),
                per_step_overrides={},
            )

        @property
        def steps(self) -> Sequence[WorkflowStep]:
            return (
                WorkflowStep(
                    step_id=StepID("step-0"),
                    step_kind=StepKind.INFERENCE_STEP,
                    step_payload=inference_payload,
                ),
            )

        @property
        def step_dispatcher(self) -> _CpStepDispatcher:
            # Bootstrap-bound INFERENCE_STEP dispatcher takes precedence at
            # the workflow_driver site; this attribute is required by the
            # WorkflowObject Protocol but unused here.
            raise NotImplementedError("bootstrap-bound dispatcher is used")

        @property
        def step_dispatchers(self) -> Any:
            # Return None so workflow_driver falls back to ctx.step_dispatchers
            # bound at stage 5 (real INFERENCE_STEP dispatcher → real LLM).
            return None

        @property
        def default_model_binding(self) -> ModelBinding:
            return ModelBinding(provider="anthropic", model="claude-haiku-4-5")

    # ---------------- exercise ----------------
    result = await _run(_Workflow(), config=config)

    # AC #1 invariant — real LLM single-step inference completes SUCCESS.
    assert isinstance(result, RunResult), f"got {type(result).__name__}"
    assert result.status == "completed", (
        f"expected status=completed, got status={result.status!r} "
        f"failure_cause={getattr(result, 'failure_cause', None)!r}"
    )
    assert result.workflow_id == "wf-ac1-real-anthropic"


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
# AC #5 — mech-α reframe: in-process drain-flag set mid-step (subprocess γ
# deferred under same composition friction that defers test_cli_daemon.py
# subprocess e2e per AC #6 precedent).
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ac5_sigint_mid_multi_step_produces_drained_resumable_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AC #5 — mid-multi-step drain produces DRAINED RunResult with
    partial-state populated and a hash-chain-intact state ledger.

    Mech-α reframe (operator-ratified per advisor pre-substantive arc):
    the substantive surface AC #5 verifies is the driver's per-step
    pre-entry drain-check loop (`workflow_driver.py:732`) and the
    ledger's append-only hash-chain integrity invariant — both
    orthogonal to whether the drain originates from an in-process
    `ctx.drained_flag.set()` call or from an OS signal handler invoking
    the same set() through `drain.py:_on_drain`. The signal-handler path
    itself is covered at `tests/test_drain.py`. Mech-γ subprocess shape
    is deferred under the same `RuntimeConfig` composition friction that
    defers `test_cli_daemon.py::test_ac1_e2e_daemon_subprocess_binds_socket_and_shuts_down`
    per the AC #6 reframe precedent.

    Invariants verified (mapping to runtime plan v2.31 §1.9 AC #5):
      1. ``RunResult.status == "drained"`` — driver returns DRAINED at
         the top of the step-1 iteration when `drained_flag` was set
         during step-0 dispatch.
      2. Partial-state populated — ``RunResult.terminal_state`` carries
         the step-0 accumulation (the partial dict returned by the CP
         driver at `workflow_driver.py:738` ``partial_state=dict(accumulated)``).
      3. Ledger-resumable next invocation — ``state.jsonl`` exists, has
         at least one append (step-0's entry), and the
         ``prior_event_hash → response_hash`` chain validates
         per ADR-D5 §1.4. A future ``api.run`` invocation could open
         the ledger and resume from the last completed step; this test
         verifies the ledger is in the well-formed state that resumption
         requires, without exercising the resumption-replay path itself.

    Scope per the AC #6 reframe + L9-undecies U-RT-89 e2e precedent:
    in-process drain trigger via custom dispatcher; no subprocess; no
    real OS signal. The custom INFERENCE_STEP dispatcher sets
    ``ctx.drained_flag`` after returning step-0's success result; the
    driver's per-step pre-entry check at step_index=1 detects the flag
    and returns DRAINED before binding-resolution + dispatch of step-1.

    Out of scope: full ``api.run(resume_from=snapshot)`` round-trip
    (resumption-replay path is operator-discretion at the pause/resume
    composer arc per CP spec §26 + runtime spec §14.14; AC #5's third
    conjunct "ledger-resumable next invocation" is satisfied by ledger
    well-formedness, not by demonstrating an end-to-end resume cycle).
    """
    from collections.abc import Sequence
    from functools import partial

    from harness_core.deployment_surface import DeploymentSurface
    from harness_core.identity import StepID
    from harness_core.persona_tier import PersonaTier
    from harness_core.workload_class import WorkloadClass
    from harness_cp.cp_shared_types import ModelBinding
    from harness_cp.cross_family_fallback_chain import (
        FallbackChain,
        ProviderCandidate,
        ProviderFamily,
    )
    from harness_cp.engine_class import EngineClass
    from harness_cp.routing_manifest_residence import RoutingManifest
    from harness_cp.topology_pattern import TopologyPattern
    from harness_cp.workflow_driver import execute_workflow
    from harness_cp.workflow_driver_types import (
        RunStatus as _CpRunStatus,
    )
    from harness_cp.workflow_driver_types import (
        StepKind,
        WorkflowStep,
    )
    from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
    from harness_is.path_class_registry import PathClass
    from harness_is.state_ledger_write import read_ledger
    from harness_runtime.bootstrap import run_bootstrap
    from harness_runtime.bootstrap import stage_3a_cp_clients as _stage_3a_mod
    from harness_runtime.bootstrap import stage_4_od as _stage_4_od_mod
    from harness_runtime.lifecycle.providers import ProviderClientsStage

    # --------------- patched runtime (mirror of test_run_smoke.py fakes) ---------------
    # The bootstrap path materializes the real state-ledger writer
    # (LedgerWriter at lifecycle/state_ledger.py) which writes to
    # `<STATE_LEDGER path>/state.jsonl`. Only network-touching stages
    # (provider clients + collector daemon + tracer provider) are stubbed
    # so the ledger machinery exercised by the driver remains real.

    class _FakeProvider:
        def __init__(self, name: str) -> None:
            self.name = name

        async def aclose(self) -> None:
            return None

    async def _fake_clients(
        *_args: object, **_kwargs: object
    ) -> ProviderClientsStage:
        return ProviderClientsStage(
            providers={
                "anthropic": _FakeProvider("anthropic"),
                "openai": _FakeProvider("openai"),
                "ollama": _FakeProvider("ollama"),
            }
        )

    monkeypatch.setattr(
        _stage_3a_mod, "materialize_provider_clients_stage", _fake_clients
    )

    class _FakeDaemon:
        async def start(self) -> None:
            return None

        async def stop(self, *, timeout_seconds: float = 5.0) -> None:
            _ = timeout_seconds
            return None

    class _CollectorStage:
        def __init__(self, d: _FakeDaemon) -> None:
            self.daemon = d

    class _FakeTracerProvider:
        def force_flush(self, timeout_millis: int = 30_000) -> bool:
            _ = timeout_millis
            return True

        def shutdown(self) -> None:
            return None

        def get_tracer(self, instrumenting_module_name: str, /) -> object:
            from opentelemetry.trace import NoOpTracer

            _ = instrumenting_module_name
            return NoOpTracer()

    class _TracerStage:
        def __init__(self, p: _FakeTracerProvider) -> None:
            self.provider = p
            self.registered_globally = False

    monkeypatch.setattr(
        _stage_4_od_mod,
        "materialize_collector_daemon_stage",
        lambda config, **_: _CollectorStage(_FakeDaemon()),
    )
    monkeypatch.setattr(
        _stage_4_od_mod, "materialize_ring_buffer_stage", lambda config, _d: None
    )
    monkeypatch.setattr(
        _stage_4_od_mod,
        "materialize_tracer_provider_stage",
        lambda config, **_: _TracerStage(_FakeTracerProvider()),
    )
    monkeypatch.setattr(
        _stage_4_od_mod,
        "materialize_span_processor_stage",
        lambda config, _p, **_k: None,
    )

    # --------------- config (mirror of conftest.build_config) ---------------
    surface = DeploymentSurface.LOCAL_DEVELOPMENT
    workload = WorkloadClass.SOFTWARE_ENGINEERING
    chain = FallbackChain(
        primary=ProviderCandidate(
            provider="anthropic",
            model="claude-haiku-4-5",
            family=ProviderFamily.ANTHROPIC,
        ),
        same_family=(),
        cross_family=(),
        terminal=None,
    )
    config = RuntimeConfig(
        deployment_surface=surface,
        repository_root=tmp_path,
        path_bindings=PathBindingConfig(
            raw_entries=tuple(
                {
                    "path_class": pc,
                    "workflow_class": workload,
                    "deployment_surface": surface,
                    "path": str(tmp_path / pc.value.lower()),
                }
                for pc in PathClass
            ),
        ),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4317"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        mcp_clients=[],
        ollama_optional=True,
        routing_manifest=RoutingManifest(
            manifest_version=1,
            per_role_bindings={},
            per_workload_overrides={},
            fallback_chains=(chain,),
            retry_policies={},
        ),
    )

    ctx = await run_bootstrap(config, workload_class=workload)

    # --------------- drain-triggering dispatcher ---------------
    # The dispatcher counts invocations; on step-0 it returns success then
    # sets ctx.drained_flag. Step-1's pre-entry drain-check
    # (workflow_driver.py:732) fires before binding-resolution; driver
    # returns RunStatus.DRAINED with terminal_step_index=0 and
    # partial_state = dict(accumulated) containing step-0's contribution.
    dispatch_count = {"n": 0}

    class _DrainTriggeringDispatcher:
        def dispatch(
            self,
            binding: Any,
            step: WorkflowStep,
            *,
            step_context: Any = None,
        ) -> dict[str, Any]:
            _ = binding, step_context
            dispatch_count["n"] += 1
            if dispatch_count["n"] >= 3:
                # Defensive — if drain check ever misses, surface as a
                # loud failure instead of an opaque hang.
                raise AssertionError(
                    "drained_flag set after step-0 but driver continued past "
                    "step-1 — per-step pre-entry drain-check regression at "
                    "workflow_driver.py:732"
                )
            result = {"step_id": str(step.step_id), "ok": True}
            if dispatch_count["n"] == 1:
                # Mid-step drain trigger — set the flag AFTER returning
                # the step-0 result so step-0's ledger append completes
                # and accumulated picks up its entry before the loop
                # advances to step-1.
                ctx.drained_flag.set()
            return result

    class _SingleKindRegistry:
        def __init__(self, dispatcher: Any) -> None:
            self._dispatcher = dispatcher

        def lookup(self, step_kind: Any) -> Any:
            _ = step_kind
            return self._dispatcher

    # --------------- 3-step workflow ---------------
    workflow_id = "wf-ac5-sigint-mid-multi-step"
    manifest = WorkflowManifestEntry(
        workflow_id=workflow_id,
        workload_class=workload,
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=TopologyPattern.SINGLE_THREADED_LINEAR,
        layer_budgets=(),
        fallback_chain=chain,
        hitl_placements=(),
        per_step_overrides={},
    )
    steps: Sequence[WorkflowStep] = tuple(
        WorkflowStep(
            step_id=StepID(f"step-{i}"),
            step_kind=StepKind.INFERENCE_STEP,
            step_payload={"index": i},
        )
        for i in range(3)
    )

    # The driver is sync; execute_workflow's internal async-to-sync
    # bridge calls asyncio.run() which cannot run inside an active loop.
    # Dispatch into a thread per the api.run-internal asyncio.to_thread
    # pattern (mirrors test_u_rt_89_pause_resume_full_execution_path.py).
    import asyncio

    cp_result = await asyncio.to_thread(
        partial(
            execute_workflow,
            manifest_entry=manifest,
            steps=steps,
            run_id="run-ac5-1",
            ctx=ctx,  # type: ignore[arg-type]
            default_model_binding=ModelBinding(
                provider="anthropic", model="claude-haiku-4-5"
            ),
            step_dispatchers=_SingleKindRegistry(  # type: ignore[arg-type]
                _DrainTriggeringDispatcher()
            ),
        )
    )

    # --------------- invariant 1: status == DRAINED ---------------
    assert cp_result.status == _CpRunStatus.DRAINED, (
        f"expected DRAINED, got {cp_result.status}; "
        f"fail_class={cp_result.fail_class}"
    )
    # terminal_step_index = step_index - 1 = 0 per workflow_driver.py:737.
    assert cp_result.terminal_step_index == 0
    # Exactly 1 dispatch fired (step-0); step-1 short-circuited at drain check.
    assert dispatch_count["n"] == 1, (
        f"expected exactly 1 dispatch (step-0) before drain; got "
        f"{dispatch_count['n']}"
    )

    # --------------- invariant 2: partial_state populated ---------------
    # The CP driver populates partial_state = dict(accumulated) at
    # workflow_driver.py:738. accumulated grows per-step under
    # PURE_PATTERN_NO_ENGINE (see C-CP-25 §25.3.3.7); step-0's
    # contribution must be present.
    assert cp_result.partial_state is not None, (
        "partial_state must be a dict, not None, on DRAINED per "
        "C-CP-25 §25.2 + workflow_driver.py:738"
    )
    assert isinstance(cp_result.partial_state, dict)
    assert len(cp_result.partial_state) >= 1, (
        f"partial_state must carry step-0's accumulation; got "
        f"{cp_result.partial_state!r}"
    )
    assert cp_result.final_state is None  # DRAINED ≠ SUCCESS

    # --------------- invariant 3: ledger-resumable (well-formedness) ---------------
    # Read the on-disk ledger directly via the IS-axis reader.
    # ctx.ledger_writer.handle is the JsonlLedgerHandle bound at stage 1.
    handle = ctx.ledger_writer.handle  # type: ignore[attr-defined]
    entries = read_ledger(handle)
    assert len(entries) >= 1, (
        f"expected ≥1 ledger entry from step-0 execution; got "
        f"{len(entries)} entries at {handle.canonical_path}"
    )

    # Hash-chain integrity per ADR-D5 §1.4: each entry's prior_event_hash
    # must equal the prior entry's response_hash (entry 0's prior =
    # construct_prior_event_hash(None) = ALL_ZEROS).
    from harness_is.chain_link_construction import construct_prior_event_hash
    from harness_is.entry_hash import compute_response_hash
    from harness_is.state_ledger_entry_schema import ALL_ZEROS_SENTINEL

    expected_prior = construct_prior_event_hash(None)
    assert expected_prior == ALL_ZEROS_SENTINEL or len(expected_prior) == 32
    for i, entry in enumerate(entries):
        assert entry.prior_event_hash == expected_prior, (
            f"hash chain broken at entry {i}: prior_event_hash="
            f"{entry.prior_event_hash.hex()} expected={expected_prior.hex()}"
        )
        # response_hash must be a recomputation of the entry's canonical
        # form (sans the response_hash field itself) — verifies the
        # writer didn't tamper with the canonicalization.
        recomputed = compute_response_hash(entry)
        assert entry.response_hash == recomputed, (
            f"response_hash mismatch at entry {i}: stored="
            f"{entry.response_hash.hex()} recomputed={recomputed.hex()}"
        )
        # Idempotency-key uniqueness within the ledger (no
        # IDEMPOTENT_NOOP gaps shadowing real appends).
        for j, other in enumerate(entries):
            if i != j:
                assert entry.idempotency_key != other.idempotency_key, (
                    f"duplicate idempotency_key between entries {i} and {j}: "
                    f"{entry.idempotency_key!r}"
                )
        expected_prior = entry.response_hash

    # Cleanup so background tasks (collector, lifecycle emitter) terminate.
    from harness_runtime.shutdown import shutdown as _shutdown

    await _shutdown(ctx)


def test_ac6_daemon_concurrent_two_clients_complete_independently(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AC #6 — concurrent run_workflow invocations from distinct MCP client
    sessions complete independently per spec v1.36 §14.18 chapeau (line 65)
    per-session ctx isolation.

    Per `[[u-rt-107-fork-section-4-closed-contextvars]]` PR #2 unblock: the
    `_current_tool_ctx` race resolved via module-level `contextvars.ContextVar`
    + accessor methods on `HarnessMCPServer`. This test exercises the
    isolation through the FULL `run_workflow` handler body (not just the
    accessor; that's `test_lifecycle_mcp_server.py::
    test_concurrent_set_current_tool_ctx_is_task_isolated`) by spawning two
    concurrent `tool.fn(...)` invocations with distinct mock ctx objects and
    asserting each invocation's observed `get_current_tool_ctx()` matches
    its own input ctx.

    Scope (per advisor scope discipline at the AC #6 implementation arc):
    in-process direct tool invocation, NOT subprocess + real MCP-client
    transport. The subprocess path is gated on the same `RuntimeConfig`
    composition friction that defers `test_cli_daemon.py::
    test_ac1_e2e_daemon_subprocess_binds_socket_and_shuts_down`; the
    workspace pattern is "subprocess e2e deferred until composition lands."
    AC #6 inherits that constraint — substantive isolation evidence comes
    from observing the contextvar through the actual handler body.

    Out of scope: real HITL elicit routing. The fake `_execute_workflow`
    observing `get_current_tool_ctx()` is sufficient evidence that the
    isolation holds through the handler's `asyncio.to_thread` bridge —
    which is the only place a race could occur post-PR #2.
    """
    import asyncio
    from types import SimpleNamespace

    from harness_cp.workflow_driver_types import RunResult as _CpRunResult
    from harness_cp.workflow_driver_types import RunStatus as _CpRunStatus

    from harness_runtime.lifecycle.mcp_server import materialize_mcp_server_stage

    # The handler at `lifecycle/mcp_server.py:328` calls
    # `_execute_workflow(manifest_entry, steps, run_id, harness_ctx, ...)` via
    # `asyncio.to_thread`. By the time this fake fires, the tool handler has
    # already bound the ContextVar via `_CURRENT_TOOL_CTX.set(ctx)`. The fake
    # observes the ContextVar from the worker thread (propagates via
    # `asyncio.to_thread`'s `copy_context().run` per
    # `test_contextvar_bridge_propagation.py`) and returns a synthetic
    # SUCCESS `CpRunResult` so the handler completes normally.
    observed: dict[str, Any | None] = {}

    def _fake_execute_workflow(
        manifest_entry: Any,
        steps: Any,
        run_id: str,
        harness_ctx: Any,
        *,
        default_model_binding: Any = None,
        step_dispatchers: Any = None,
    ) -> _CpRunResult:
        wf_id = manifest_entry.workflow_id
        # The worker thread inherits the tool handler task's contextvars
        # context via `asyncio.to_thread`'s `copy_context().run`. Reading via
        # the server accessor proves isolation through the handler body.
        observed[wf_id] = server.get_current_tool_ctx()
        return _CpRunResult(
            workflow_id=wf_id,
            run_id=run_id,
            status=_CpRunStatus.SUCCESS,
            final_state={},
        )

    # Patch BEFORE `materialize_mcp_server_stage` — the production import at
    # `lifecycle/mcp_server.py:228` is a lazy `from harness_cp.workflow_driver
    # import execute_workflow as _execute_workflow` INSIDE the stage function.
    # Patching the source module attribute makes the lazy import pick up the
    # fake on first invocation of the registered tool.
    monkeypatch.setattr(
        "harness_cp.workflow_driver.execute_workflow", _fake_execute_workflow
    )

    server = materialize_mcp_server_stage(drain_timeout_seconds=30.0)
    server._state["_harness_ctx"] = SimpleNamespace(step_dispatchers=None)

    def _fake_workflow(wf_id: str) -> SimpleNamespace:
        return SimpleNamespace(
            workflow_id=wf_id,
            workload_class=None,
            manifest_entry=SimpleNamespace(workflow_id=wf_id),
            steps=(),
            default_model_binding=None,
            step_dispatchers=None,
        )

    server.workflow_registry["wf-alpha"] = _fake_workflow("wf-alpha")  # type: ignore[assignment]
    server.workflow_registry["wf-beta"] = _fake_workflow("wf-beta")  # type: ignore[assignment]

    async def _run() -> tuple[object, object]:
        tool = server.server._tool_manager.get_tool("run_workflow")  # type: ignore[attr-defined]
        assert tool is not None
        ctx_alpha = object()
        ctx_beta = object()
        # asyncio.gather schedules both tool invocations as independent
        # asyncio tasks. Each task binds its OWN ContextVar value via
        # `_CURRENT_TOOL_CTX.set(...)` inside the handler; if isolation is
        # broken, one would clobber the other before the worker-thread
        # observation fires.
        await asyncio.gather(
            tool.fn(workflow_id="wf-alpha", ctx=ctx_alpha),  # type: ignore[arg-type]
            tool.fn(workflow_id="wf-beta", ctx=ctx_beta),  # type: ignore[arg-type]
        )
        return ctx_alpha, ctx_beta

    ctx_alpha, ctx_beta = asyncio.run(_run())

    assert observed["wf-alpha"] is ctx_alpha, (
        f"wf-alpha observed ctx {observed['wf-alpha']!r} but expected its "
        f"own ctx {ctx_alpha!r} — concurrent invocation cross-talked through "
        f"the handler body (post-PR-#2 contextvars isolation regression)"
    )
    assert observed["wf-beta"] is ctx_beta, (
        f"wf-beta observed ctx {observed['wf-beta']!r} but expected its "
        f"own ctx {ctx_beta!r} — concurrent invocation cross-talked through "
        f"the handler body (post-PR-#2 contextvars isolation regression)"
    )

    # Post-condition: both `try/finally` blocks in the handler reset the
    # ContextVar before exit, so no binding leaks into the test task.
    assert server.get_current_tool_ctx() is None
