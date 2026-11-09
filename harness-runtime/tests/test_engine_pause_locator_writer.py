"""B-314 fork §2 writer: the locator a root body owes the journal, and its append."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from harness_core.deployment_surface import DeploymentSurface
from harness_cp.engine_class import EngineClass
from harness_cp.pause_resume_protocol import PauseReason
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver_types import RunResult, RunStatus
from harness_runtime.lifecycle import root_resume_admission
from harness_runtime.lifecycle.engine_recovery_loop import (
    bind_engine_substrates,
    engine_pause_locator,
    run_scoped_substrate_key,
)
from harness_runtime.lifecycle.journal_workflow_pause_store import (
    EnginePauseLocator,
    JournalWorkflowPauseStore,
)
from harness_runtime.lifecycle.root_resume_admission import FreshRunAdmission
from harness_runtime.types import (
    CollectorConfig,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
)

from .pause_journal_roots import declare_pause_journal_root

_W = "wf"
_RUN = "r1"


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


def _paused(terminal_step_index: int | None) -> RunResult:
    return RunResult(
        workflow_id=_W,
        run_id=_RUN,
        status=RunStatus.PAUSED,
        terminal_step_index=terminal_step_index,
    )


def _locate(tmp_path: Path, result: RunResult, engine_class: EngineClass | None) -> Any:
    return engine_pause_locator(
        result,
        workflow_id=_W,
        run_id=_RUN,
        engine_class=engine_class,
        substrates=bind_engine_substrates(_config(tmp_path), None),
    )


def _capture(tmp_path: Path, engine_class: EngineClass) -> None:
    bind_engine_substrates(_config(tmp_path), None)[engine_class].capture_pause_snapshot(
        run_scoped_substrate_key(_W, _RUN), PauseReason.ENGINE_NATIVE_PAUSE
    )


@pytest.mark.parametrize("engine_class", [EngineClass.WAL_SEGMENT, EngineClass.RECONCILER_LOOP])
@pytest.mark.parametrize(("terminal", "step"), [(None, 0), (0, 1), (3, 4)])
def test_an_engine_pause_with_a_captured_record_owes_a_locator_at_its_pause_step(
    tmp_path: Path, engine_class: EngineClass, terminal: int | None, step: int
) -> None:
    _capture(tmp_path, engine_class)

    assert _locate(tmp_path, _paused(terminal), engine_class) == EnginePauseLocator(
        workflow_id=_W, run_id=_RUN, engine_class=engine_class, step_index=step
    )


def test_no_locator_without_the_engine_record_or_for_another_class(tmp_path: Path) -> None:
    # Presence is per class and per run: nothing captured, then a capture by the other class.
    assert _locate(tmp_path, _paused(0), EngineClass.WAL_SEGMENT) is None
    _capture(tmp_path, EngineClass.RECONCILER_LOOP)
    assert _locate(tmp_path, _paused(0), EngineClass.WAL_SEGMENT) is None


@pytest.mark.parametrize(
    "engine_class", [None, EngineClass.SAVE_POINT_CHECKPOINT, EngineClass.PURE_PATTERN_NO_ENGINE]
)
def test_no_locator_for_a_workflow_that_is_not_engine_native(
    tmp_path: Path, engine_class: EngineClass | None
) -> None:
    _capture(tmp_path, EngineClass.WAL_SEGMENT)
    assert _locate(tmp_path, _paused(0), engine_class) is None


@pytest.mark.parametrize("status", [RunStatus.SUCCESS, RunStatus.FAILED])
def test_no_locator_for_a_run_that_did_not_pause(tmp_path: Path, status: RunStatus) -> None:
    _capture(tmp_path, EngineClass.WAL_SEGMENT)
    result = RunResult(workflow_id=_W, run_id=_RUN, status=status)
    assert _locate(tmp_path, result, EngineClass.WAL_SEGMENT) is None


def _ctx(tmp_path: Path) -> Any:
    declare_pause_journal_root(tmp_path.resolve() / "pause-journal").mkdir()
    return SimpleNamespace(
        config=SimpleNamespace(
            tenant_id=None, path_bindings=PathBindingConfig(), state_placement=object()
        ),
        verified_state_root=SimpleNamespace(realpath=tmp_path.resolve()),
        pause_resume_protocol=None,
    )


def test_a_fresh_root_appends_the_owed_locator_after_its_body(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path)
    locator = EnginePauseLocator(
        workflow_id=_W, run_id=_RUN, engine_class=EngineClass.WAL_SEGMENT, step_index=1
    )

    result = FreshRunAdmission(workflow_id=_W, run_id=_RUN).run(
        ctx, lambda _: "body-result", lambda _: locator
    )

    journal_dir = root_resume_admission._run_journal_root(ctx)  # pyright: ignore[reportPrivateUsage]
    read = JournalWorkflowPauseStore(
        journal_dir=journal_dir, tenant_id=None
    ).read_latest_attributed(_W)
    assert result == "body-result"
    assert (read.cause, read.locator, read.depth, read.record_count) == (None, locator, 0, 1)


def test_a_fresh_root_that_owes_nothing_journals_nothing(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path)

    FreshRunAdmission(workflow_id=_W, run_id=_RUN).run(ctx, lambda _: None)

    journal_dir = root_resume_admission._run_journal_root(ctx)  # pyright: ignore[reportPrivateUsage]
    read = JournalWorkflowPauseStore(
        journal_dir=journal_dir, tenant_id=None
    ).read_latest_attributed(_W)
    assert (read.locator, read.record_count) == (None, 0)
