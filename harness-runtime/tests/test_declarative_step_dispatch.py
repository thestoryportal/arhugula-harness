"""`DECLARATIVE_STEP` through the production bootstrap: a lead plan selects nested workers.

Each run loads a manifest file the way `harness run` does and drives it through `api.run`,
whose stage 5 builds the real step-dispatcher registry; no dispatcher is injected. The
orchestrator is a declarative step whose declared output is the `worker_plan`; each worker
is a sub-agent dispatch whose child is one declarative leaf. Only the Ollama client and the
OD collector/tracer stages are stand-ins, and no step may call the model.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from harness_core import WorkloadClass
from harness_cp.topology_pattern import TopologyPattern, WorkerSelection
from harness_cp.workflow_driver_types import StepKind
from harness_runtime.api import RunResult
from harness_runtime.lifecycle.handoff import RuntimeHandoffRegistry

from .test_manifest_worker_selection_driver import _brief, _plan_entry, _toml
from .test_omarchy_offline_examples import SHARED_CONFIG, _Client, _Example, _run_as_the_cli_does

_FALLBACK = {
    "primary": {"provider": "ollama", "model": "llama3.2:3b", "family": "local_open_weight"},
    "same_family": [],
    "cross_family": [],
}
_WORKERS = ("a", "b", "c")


def _entry(workflow_id: str, **extra: Any) -> dict[str, Any]:
    return {
        "workflow_id": workflow_id,
        "workload_class": WorkloadClass.RESEARCH.value,
        "persona_tier": "solo-developer",
        "engine_class": "pure-pattern-no-engine",
        "topology_pattern": TopologyPattern.ORCHESTRATOR_WORKERS.value,
        "layer_budgets": [],
        "hitl_placements": [],
        "per_step_overrides": {},
        "fallback_chain": _FALLBACK,
        **extra,
    }


def _declarative(step_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "step_id": step_id,
        "step_kind": StepKind.DECLARATIVE_STEP.value,
        "step_payload": payload,
    }


def _worker(name: str) -> dict[str, Any]:
    """A sub-agent worker whose child workflow is one declarative leaf."""
    child_id = f"wf-child-{name}"
    return {
        "step_id": name,
        "step_kind": StepKind.SUB_AGENT_DISPATCH.value,
        "step_payload": {
            "child_workflow_id": child_id,
            "child_manifest_entry": _entry(child_id),
            "child_steps": [_declarative(f"{name}-leaf", {"output": {"leaf": name}})],
            "brief": _brief(f"declared {name}").model_dump(mode="json", exclude_none=True),
        },
    }


def _write(tmp_path: Path, steps: list[dict[str, Any]], **workflow: Any) -> Path:
    document = {
        "version": 1,
        "workflow": _entry("wf-declarative-lead-plan", **workflow),
        "default_model_binding": {"provider": "ollama", "model": "llama3.2:3b"},
        "steps": steps,
    }
    path = tmp_path / "manifest.toml"
    path.write_text("\n".join(f"{k} = {_toml(v)}" for k, v in document.items()) + "\n")
    return path


def _lead_plan_manifest(tmp_path: Path, plan: list[dict[str, Any]]) -> Path:
    return _write(
        tmp_path,
        [_declarative("orch", {"output": {"worker_plan": plan}}), *map(_worker, _WORKERS)],
        worker_selection=WorkerSelection.LEAD_PLAN.value,
    )


def _no_model_call(messages: list[dict[str, Any]]) -> str:
    raise AssertionError(f"a declarative workflow called the model: {messages!r}")


def _run(manifest: Path, placed_root: Path, monkeypatch: pytest.MonkeyPatch) -> RunResult:
    # An absolute manifest path survives `_run_as_the_cli_does`'s repository-root join.
    example = _Example(
        str(manifest),
        "wf-declarative-lead-plan",
        WorkloadClass.RESEARCH,
        TopologyPattern.ORCHESTRATOR_WORKERS,
        (),
        SHARED_CONFIG,
        False,
    )
    return _run_as_the_cli_does(example, _Client(_no_model_call), placed_root, monkeypatch)


@pytest.fixture
def hashed_briefs(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Objectives of the briefs the production sub-agent dispatcher hashes into its audit
    entry, one per dispatched worker; the hash itself is computed as before."""
    objectives: list[str] = []
    original = RuntimeHandoffRegistry.dispatch_response_hash

    def record(self: RuntimeHandoffRegistry, brief: Any) -> str:
        objectives.append(brief.objective)
        return original(self, brief)

    monkeypatch.setattr(RuntimeHandoffRegistry, "dispatch_response_hash", record)
    return objectives


@pytest.mark.parametrize("order", [("c", "a"), ("b",)], ids=["c-a", "b"])
def test_a_declarative_lead_plan_selects_orders_briefs_and_joins_nested_workers(
    order: tuple[str, ...],
    tmp_path: Path,
    placed_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    hashed_briefs: list[str],
) -> None:
    plan = [_plan_entry(worker, f"lead {worker}") for worker in order]
    result = _run(_lead_plan_manifest(tmp_path, plan), placed_root, monkeypatch)

    assert result.status == "completed", result.failure_cause
    assert result.terminal_state["orchestrator"] == {"worker_plan": plan}
    joined = result.terminal_state["worker_outputs"]
    assert list(joined) == list(order)
    assert joined == {w: {"orchestrator": {"leaf": w}, "worker_outputs": {}} for w in order}
    assert sorted(hashed_briefs) == sorted(f"lead {worker}" for worker in order)


@pytest.mark.parametrize(
    ("plan", "reason"),
    [
        ([_plan_entry("z", "lead z")], "unknown-worker:z"),
        ([_plan_entry("a", None)], "missing-brief:a"),
        ([_plan_entry("a", "lead a"), _plan_entry("a", "lead a")], "duplicate-worker:a"),
        ("a", "not-a-sequence"),
    ],
    ids=["unknown", "missing-brief", "duplicate", "not-a-sequence"],
)
def test_an_invalid_declarative_lead_plan_dispatches_no_worker(
    plan: Any,
    reason: str,
    tmp_path: Path,
    placed_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    hashed_briefs: list[str],
) -> None:
    result = _run(_lead_plan_manifest(tmp_path, plan), placed_root, monkeypatch)

    assert result.status == "failed"
    assert result.failure_cause is not None
    assert (
        result.failure_cause.validator_fail_class == f"orchestrator-workers-plan-invalid: {reason}"
    )
    assert result.terminal_state == {}
    assert hashed_briefs == []


@pytest.mark.parametrize(
    "payload",
    [
        {"out": {"worker_plan": []}},
        {"output": "worker_plan"},
        {"output": {"worker_plan": []}, "note": "x"},
        {},
    ],
    ids=["wrong-key", "not-a-table", "extra-key", "empty"],
)
def test_a_mis_shaped_declarative_payload_fails_its_step_before_any_worker(
    payload: dict[str, Any],
    tmp_path: Path,
    placed_root: Path,
    monkeypatch: pytest.MonkeyPatch,
    hashed_briefs: list[str],
) -> None:
    manifest = _write(
        tmp_path,
        [_declarative("orch", payload), *map(_worker, _WORKERS)],
        worker_selection=WorkerSelection.LEAD_PLAN.value,
    )
    result = _run(manifest, placed_root, monkeypatch)

    assert result.status == "failed"
    assert result.failure_cause is not None
    assert str(result.failure_cause.validator_fail_class).startswith(
        "orchestrator-workers-orchestrator-failure: DeclarativeStepPayloadShapeError: "
        "RT-FAIL-PAYLOAD-SHAPE: DECLARATIVE_STEP 'orch'"
    )
    assert hashed_briefs == []


def test_a_declarative_only_workflow_runs_provider_free(
    tmp_path: Path, placed_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Before stage 5 bound `DECLARATIVE_STEP`, this run failed at the orchestrator with
    `RT-FAIL-STEP-KIND-DISPATCHER-NOT-BOUND`; with no inference step it now completes
    without a provider."""
    plan = [{"worker": "y"}]
    manifest = _write(
        tmp_path,
        [
            _declarative("orch", {"output": {"worker_plan": plan}}),
            *(_declarative(w, {"output": {"leaf": w}}) for w in ("x", "y")),
        ],
        worker_selection=WorkerSelection.LEAD_PLAN.value,
    )
    result = _run(manifest, placed_root, monkeypatch)

    assert result.status == "completed", result.failure_cause
    assert result.terminal_state == {
        "orchestrator": {"worker_plan": plan},
        "worker_outputs": {"y": {"leaf": "y"}},
    }
