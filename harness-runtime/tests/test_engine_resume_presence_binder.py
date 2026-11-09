"""B-314 fork §3.1: the engine stores the pre-claim admission probes are the stores the
factory binds, and presence is keyed by the original run (T05)."""

from __future__ import annotations

from pathlib import Path

from harness_core.deployment_surface import DeploymentSurface
from harness_cp.engine_class import EngineClass
from harness_cp.pause_resume_protocol import PauseReason
from harness_cp.topology_pattern import TopologyPattern
from harness_runtime.config.state_placement import StateKind, resolve_state_path
from harness_runtime.lifecycle.engine_recovery_loop import (
    bind_engine_substrates,
    has_engine_pause_record,
    run_scoped_substrate_key,
)
from harness_runtime.types import (
    CollectorConfig,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
)


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        repository_root=tmp_path,
        path_bindings=PathBindingConfig(),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4317"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
    )


def test_binding_creates_no_store_and_reports_absence(tmp_path: Path) -> None:
    substrates = bind_engine_substrates(_config(tmp_path), None)

    assert set(substrates) == {EngineClass.WAL_SEGMENT, EngineClass.RECONCILER_LOOP}
    for substrate in substrates.values():
        assert not has_engine_pause_record(substrate, workflow_id="wf", run_id="r1")
    assert not (tmp_path / ".harness").exists()


def test_a_pause_captured_through_one_binding_is_present_through_a_fresh_one(
    tmp_path: Path,
) -> None:
    config = _config(tmp_path)
    for engine_class, kind in (
        (EngineClass.WAL_SEGMENT, StateKind.ENGINE_RECOVERY_SEGMENTS),
        (EngineClass.RECONCILER_LOOP, StateKind.ENGINE_RECOVERY_RECONCILER),
    ):
        workflow_id = f"wf-{engine_class.value}"
        bind_engine_substrates(config, None)[engine_class].capture_pause_snapshot(
            run_scoped_substrate_key(workflow_id, "r1"), PauseReason.ENGINE_NATIVE_PAUSE
        )

        fresh = bind_engine_substrates(config, None)
        assert has_engine_pause_record(fresh[engine_class], workflow_id=workflow_id, run_id="r1")
        # A different run of the same workflow is a new execution, never this pause.
        assert not has_engine_pause_record(
            fresh[engine_class], workflow_id=workflow_id, run_id="r2"
        )
        assert any(resolve_state_path(kind, config, None).iterdir())

    # No cross-contamination: each class's pause is absent from the other class's store.
    fresh = bind_engine_substrates(config, None)
    assert not has_engine_pause_record(
        fresh[EngineClass.RECONCILER_LOOP], workflow_id="wf-WAL-segment", run_id="r1"
    )
    assert not has_engine_pause_record(
        fresh[EngineClass.WAL_SEGMENT], workflow_id="wf-reconciler-loop", run_id="r1"
    )
