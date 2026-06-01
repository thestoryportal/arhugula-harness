"""R-100 AC #2 — TOOL_STEP dispatch via the operator `api.run` path (the proof).

The canonical end-to-end proof that the full bootstrap TOOL_STEP path is wired
(spec v1.41 §14.9.8 Reading B + Gaps B/C/D/E/F): one echo-MCP-via-`api.run`
workflow that dispatches a real `TOOL_STEP` against a real stdio MCP subprocess
and completes. Proves the chain BY EXECUTION:
    host.start() → list_tools → converter → registry → trust → resolver →
    floor → call_tool → result.

**This test is skipif-gated and live-green is the operator's run.** Gap D: the
bootstrap constructs + pings ≥1 provider regardless of step kind, so the e2e
needs a live provider. It accepts a live ollama daemon (local, zero-token) OR
`ANTHROPIC_API_KEY` (the Anthropic ping is `models.list()` — non-inference,
zero-token). Neither exists in CI → the test skips. The harness does NOT fire a
paid call autonomously; AC #2 is NOT marked closed until this goes green on an
operator's live run.

Tier-floor consistency (spec v1.41 §14.9.8): the echo server declares both
`default_minimum_tier` (the v1.40 converter stamp) AND `default_sandbox_tier`
(the Reading B resolver) as `TIER_1_PROCESS`, so the §14.9.4 floor
(resolved.tier >= contract.minimum_tier) passes.
"""

from __future__ import annotations

import os
import sys
import urllib.error
import urllib.request
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest

_ECHO_FIXTURE = (Path(__file__).parent / "fixtures" / "mcp_echo_server.py").resolve()


def _ollama_up() -> bool:
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=1.0):
            return True
    except (urllib.error.URLError, OSError):
        return False


def _anthropic() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


pytestmark = pytest.mark.skipif(
    not (_anthropic() or _ollama_up()),
    reason=(
        "AC #2 TOOL_STEP-via-api.run e2e needs a live provider for bootstrap "
        "(Gap D): a running ollama daemon OR ANTHROPIC_API_KEY. live-green is "
        "the operator's run."
    ),
)


def _read_ledger(state_ledger_root: Path) -> list[dict[str, Any]]:
    import json

    entries: list[dict[str, Any]] = []
    for jsonl in sorted(state_ledger_root.rglob("*.jsonl")):
        for line in jsonl.read_text().splitlines():
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


@pytest.mark.asyncio
async def test_r100_ac2_tool_step_via_api_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from harness_as.discriminators import MCPTransport
    from harness_as.sandbox_tier import BlastRadiusTier, SandboxTier
    from harness_as.sandbox_tier_floor import MCPServerTrustLevel
    from harness_core import ClientName
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
    from harness_cp.workflow_driver_types import StepKind, WorkflowStep
    from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
    from harness_is.path_class_registry import PathClass
    from harness_runtime.api import RunResult
    from harness_runtime.api import run as _run
    from harness_runtime.bootstrap import stage_4_od as _stage_4_od_mod
    from harness_runtime.types import (
        CollectorConfig,
        MCPClientConfig,
        OTelConfig,
        PathBindingConfig,
        ProviderSecretsConfig,
        RuntimeConfig,
    )

    surface = DeploymentSurface.LOCAL_DEVELOPMENT
    workload = WorkloadClass.PIPELINE_AUTOMATION  # permits SINGLE_THREADED_LINEAR
    state_ledger_root = tmp_path / "state_ledger"
    path_bindings = PathBindingConfig(
        raw_entries=tuple(
            {
                "path_class": pc,
                "workflow_class": workload,
                "deployment_surface": surface,
                "path": str(
                    state_ledger_root
                    if pc is PathClass.STATE_LEDGER
                    else tmp_path / pc.value.lower()
                ),
            }
            for pc in PathClass
        ),
    )

    # --- provider config (Gap D): prefer anthropic when keyed, else ollama. ---
    if _anthropic():
        api_key = os.environ["ANTHROPIC_API_KEY"]

        def _fake_get_password(service: str, name: str) -> str | None:
            _ = service
            return api_key if name == "anthropic_key" else None

        monkeypatch.setattr(
            "harness_runtime.config.provider_secrets.keyring.get_password",
            _fake_get_password,
        )
        chain = FallbackChain(
            primary=ProviderCandidate(
                provider="anthropic", model="claude-haiku-4-5", family=ProviderFamily.ANTHROPIC
            ),
            same_family=(),
            cross_family=(),
            terminal=None,
        )
        binding = ModelBinding(provider="anthropic", model="claude-haiku-4-5")
        provider_flags: dict[str, Any] = {"openai_optional": True, "ollama_optional": True}
    else:
        chain = FallbackChain(
            primary=ProviderCandidate(
                provider="ollama", model="llama3.2", family=ProviderFamily.OLLAMA
            ),
            same_family=(),
            cross_family=(),
            terminal=None,
        )
        binding = ModelBinding(provider="ollama", model="llama3.2")
        provider_flags = {
            "anthropic_optional": True,
            "openai_optional": True,
            "ollama_host": "http://localhost:11434",
        }

    # NoOp tracer (this AC asserts dispatch + ledger, not spans).
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

    monkeypatch.setattr(_stage_4_od_mod, "materialize_tracer_provider_stage", _fake_tracer_stage)
    monkeypatch.setattr(_stage_4_od_mod, "materialize_span_processor_stage", _fake_span_processor)

    config = RuntimeConfig(
        deployment_surface=surface,
        repository_root=tmp_path,
        path_bindings=path_bindings,
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4318"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        mcp_clients=[
            MCPClientConfig(
                client_name=ClientName("echo-server"),
                transport=MCPTransport.STDIO,
                trust_level=MCPServerTrustLevel.L1_SIGNED_PINNED,
                blast_radius=BlastRadiusTier.READ_ONLY,
                connection_url=f"stdio://{sys.executable} {_ECHO_FIXTURE}",
                # tier-floor consistency: resolver tier == converter minimum tier.
                default_minimum_tier=SandboxTier.TIER_1_PROCESS,
                default_sandbox_tier=SandboxTier.TIER_1_PROCESS,
                default_sandbox_tech="host-process",
                default_sandbox_provider="host",
            )
        ],
        routing_manifest=RoutingManifest(
            manifest_version=1,
            per_role_bindings={},
            per_workload_overrides={},
            fallback_chains=(chain,),
            retry_policies={},
        ),
        **provider_flags,
    )
    monkeypatch.setattr("harness_runtime.api._default_config", lambda: config)

    class _Workflow:
        @property
        def workflow_id(self) -> str:
            return "wf-r100-ac2-tool"

        @property
        def workload_class(self) -> WorkloadClass:
            return workload

        @property
        def manifest_entry(self) -> WorkflowManifestEntry:
            return WorkflowManifestEntry(
                workflow_id="wf-r100-ac2-tool",
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
                    step_kind=StepKind.TOOL_STEP,
                    step_payload={"tool_id": "echo", "tool_args": {"value": "hello-ac2"}},
                ),
            )

        @property
        def step_dispatchers(self) -> Any:
            return None

        @property
        def default_model_binding(self) -> ModelBinding:
            return binding

    # --- exercise: the operator api.run path with a TOOL_STEP. ---
    result = await _run(_Workflow(), config=config)

    # AC #2 — the TOOL_STEP dispatched through the full bootstrap and completed.
    assert isinstance(result, RunResult), f"got {type(result).__name__}"
    assert result.status == "completed", (
        f"expected status=completed; got status={result.status!r} "
        f"failure_cause={getattr(result, 'failure_cause', None)!r}"
    )

    # The echo tool returned the input verbatim (best-effort — terminal state shape).
    terminal = getattr(result, "terminal_state", None)
    if isinstance(terminal, dict) and "step-0" in terminal:
        assert "hello-ac2" in repr(terminal["step-0"])

    # A state-ledger entry was written for the dispatched step.
    entries = _read_ledger(state_ledger_root)
    assert entries, f"no ledger entries under {state_ledger_root}"
    assert any(
        str(e.get("action_id", "")).startswith("workflow:wf-r100-ac2-tool:step:") for e in entries
    ), "no per-step ledger entry for the TOOL_STEP dispatch"
