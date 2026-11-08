"""CP v1.130 §25.11.1.1 — a manifest's `worker_selection` reaches the driver's fan-out.

The loader tests prove the selector projects onto `WorkflowManifestEntry`; these prove the
behavior it buys an operator: a manifest FILE loaded by `WorkflowManifestLoader` and run
through the real CP `execute_workflow` lets the orchestrator's `worker_plan` choose, order
and brief the workers, and a changed plan changes the workers, briefs and joined result.
A recording dispatcher stands in for every step, so no provider is touched.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.sub_agent_brief import (
    ClearTaskBoundaries,
    OutputSchema,
    OutputSchemaKind,
    SubAgentBrief,
    compute_brief_summary_hash,
)
from harness_cp.topology_pattern import TopologyPattern, WorkerSelection
from harness_cp.workflow_driver import DriverContext, StepDispatcherRegistry, execute_workflow
from harness_cp.workflow_driver_types import RunStatus, StepExecutionContext, StepKind, WorkflowStep
from harness_runtime.lifecycle.workflow_manifest_loader import WorkflowManifestLoader

from .test_local_ollama_examples import _EmitterDouble, _LedgerDouble

_DECLARED_WORKERS = ("a", "b", "s")  # within the hierarchical fan-out cap of 3


def _toml(value: Any) -> str:
    """One-line TOML for the manifest's values: inline tables, arrays, JSON-escaped scalars."""
    if isinstance(value, dict):
        return "{ " + ", ".join(f"{k} = {_toml(v)}" for k, v in value.items()) + " }"
    if isinstance(value, list):
        return "[" + ", ".join(_toml(v) for v in value) + "]"
    return json.dumps(value)


def _brief(objective: str) -> SubAgentBrief:
    unhashed = SubAgentBrief(
        objective=objective,
        output_format=OutputSchema(schema_kind=OutputSchemaKind.FREE_TEXT),
        guidance="g",
        task_boundaries=ClearTaskBoundaries(
            in_scope=("a",), out_of_scope=("b",), termination_criteria=("c",)
        ),
        summary_hash="",
    )
    return unhashed.model_copy(update={"summary_hash": compute_brief_summary_hash(unhashed)})


def _plan_entry(worker: str, objective: str | None) -> dict[str, Any]:
    """A `worker_plan` entry; a lead brief carries the four §13.2 fields, no `summary_hash`."""
    if objective is None:
        return {"worker": worker}
    # TOML has no null: absent optional fields take the model default on parse.
    brief = _brief(objective).model_dump(mode="json", exclude={"summary_hash"}, exclude_none=True)
    return {"worker": worker, "brief": brief}


def _write_manifest(
    tmp_path: Path,
    plan: list[dict[str, Any]],
    *,
    selection: WorkerSelection | None,
    topology: TopologyPattern = TopologyPattern.ORCHESTRATOR_WORKERS,
) -> Path:
    """An operator-shaped manifest: an orchestrator whose output carries `plan`, then the
    declared pool (two declarative leaves and one sub-agent worker). `selection=None`
    omits the key, exercising the manifest default."""
    workflow: dict[str, Any] = {
        "workflow_id": "wf-lead-plan",
        "workload_class": "pipeline-automation",
        "persona_tier": "solo-developer",
        "engine_class": "pure-pattern-no-engine",
        "topology_pattern": topology.value,
        "layer_budgets": [],
        "hitl_placements": [],
        "per_step_overrides": {},
        "fallback_chain": {
            "primary": {
                "provider": "anthropic",
                "model": "claude-haiku-4-5",
                "family": "anthropic",
            },
            "same_family": [],
            "cross_family": [],
        },
    }
    if selection is not None:
        workflow["worker_selection"] = selection.value
    steps: list[dict[str, Any]] = [
        {
            "step_id": "orch",
            "step_kind": StepKind.DECLARATIVE_STEP.value,
            "step_payload": {"out": {"worker_plan": plan}},
        },
        *(
            {"step_id": n, "step_kind": StepKind.DECLARATIVE_STEP.value, "step_payload": {"n": n}}
            for n in ("a", "b")
        ),
        {
            "step_id": "s",
            "step_kind": StepKind.SUB_AGENT_DISPATCH.value,
            "step_payload": {
                "child_workflow_id": "wf-s",
                "brief": _brief("declared").model_dump(mode="json", exclude_none=True),
            },
        },
    ]
    document = {
        "version": 1,
        "workflow": workflow,
        "default_model_binding": {"provider": "anthropic", "model": "claude-haiku-4-5"},
        "steps": steps,
    }
    path = tmp_path / "manifest.toml"
    path.write_text("\n".join(f"{k} = {_toml(v)}" for k, v in document.items()) + "\n")
    return path


class _RecordingDispatcher:
    """The orchestrator returns its `out` payload; each worker echoes its id and records the
    `StepExecutionContext` the driver handed it."""

    def __init__(self) -> None:
        self.contexts: dict[str, StepExecutionContext] = {}

    def dispatch(
        self, binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: Any = None
    ) -> dict[str, Any]:
        self.contexts[str(step.step_id)] = step_context
        if "out" in step.step_payload:
            return dict(step.step_payload["out"])
        return {"worker": str(step.step_id)}

    def workers(self) -> set[str]:
        return set(self.contexts) - {"orch"}


class _Registry:
    def __init__(self, dispatcher: _RecordingDispatcher) -> None:
        self._dispatcher = dispatcher

    def lookup(self, step_kind: StepKind) -> Any:
        assert step_kind in (StepKind.DECLARATIVE_STEP, StepKind.SUB_AGENT_DISPATCH)
        return self._dispatcher


def _run(path: Path) -> tuple[Any, _RecordingDispatcher]:
    """Load `path` exactly as the CLI does and drive it through the real CP driver."""
    from opentelemetry.trace import NoOpTracerProvider

    loaded = WorkflowManifestLoader.load_workflow(path)
    dispatcher = _RecordingDispatcher()
    ctx = SimpleNamespace(
        ledger_writer=_LedgerDouble(),
        lifecycle_emitter=_EmitterDouble(),
        drained_flag=asyncio.Event(),
        pause_requested_flag=asyncio.Event(),
        pause_resume_protocol=None,
        ledger_reader=None,
        tracer_provider=NoOpTracerProvider(),
        validator_framework=None,
        tenant_id=None,
    )
    result = execute_workflow(
        loaded.manifest_entry,
        list(loaded.steps),
        run_id="run-lead-plan",
        ctx=cast(DriverContext, ctx),
        default_model_binding=loaded.default_model_binding,
        step_dispatchers=cast(StepDispatcherRegistry, _Registry(dispatcher)),
    )
    return result, dispatcher


def test_lead_plan_manifest_lets_the_plan_choose_order_and_join_the_workers(
    tmp_path: Path,
) -> None:
    first, first_dispatch = _run(
        _write_manifest(
            tmp_path,
            [_plan_entry("b", None), _plan_entry("a", None)],
            selection=WorkerSelection.LEAD_PLAN,
        )
    )
    assert first.status is RunStatus.SUCCESS
    assert first_dispatch.workers() == {"b", "a"}
    assert list(first.final_state["worker_outputs"]) == ["b", "a"]
    assert first.final_state["worker_outputs"] == {"b": {"worker": "b"}, "a": {"worker": "a"}}

    # The same manifest with only the plan changed: different workers, different join.
    second, second_dispatch = _run(
        _write_manifest(tmp_path, [_plan_entry("a", None)], selection=WorkerSelection.LEAD_PLAN)
    )
    assert second.status is RunStatus.SUCCESS
    assert second_dispatch.workers() == {"a"}
    assert second.final_state["worker_outputs"] == {"a": {"worker": "a"}}
    assert second.final_state != first.final_state


def test_lead_plan_manifest_carries_the_lead_brief_to_the_sub_agent_worker(
    tmp_path: Path,
) -> None:
    briefs = {}
    for objective in ("summarize the costs", "summarize the benefits"):
        result, dispatch = _run(
            _write_manifest(
                tmp_path,
                [_plan_entry("s", objective)],
                selection=WorkerSelection.LEAD_PLAN,
                topology=TopologyPattern.HIERARCHICAL_DELEGATION,
            )
        )
        assert result.status is RunStatus.SUCCESS
        assert dispatch.workers() == {"s"}
        briefs[objective] = dispatch.contexts["s"].lead_brief
    assert briefs == {objective: _brief(objective) for objective in briefs}


def test_manifest_without_worker_selection_keeps_the_declared_pool(tmp_path: Path) -> None:
    result, dispatch = _run(
        _write_manifest(tmp_path, [_plan_entry("s", "ignored")], selection=None)
    )
    assert result.status is RunStatus.SUCCESS
    assert dispatch.workers() == set(_DECLARED_WORKERS)
    assert list(result.final_state["worker_outputs"]) == list(_DECLARED_WORKERS)
    assert all(dispatch.contexts[w].lead_brief is None for w in _DECLARED_WORKERS)
