"""Trial193.4h4 — Runtime v1.138 §14.13.9 acceptance witnesses for run-owned validator bindings.

Every root here enters through the real `run_workflow` MCP tool on ONE bootstrapped daemon, so
each invocation opens its own `ValidatorRunBinding` exactly as ingress does (§14.13.8); every
child runs through the real `RuntimeSubAgentDispatcher` and `compose_child_workflow_runner`.
A recording post-evaluate hook reads the `burden_count` each evaluation reports, keyed by the
step that produced it, so "starts at zero" is the observed count of an execution's first
non-PASS outcome, not an inspected field.

The non-PASS outcome is REVALIDATE: it charges the ledger and the driver proceeds (the RETRY
next-action belongs to the caller's retry wrapper), so one run can record several counts
without a HITL round-trip.

Coverage, in §14.13.9 order: sequential and concurrent roots; nested (a) fan-out siblings,
(b) depth-2 grandchild, (c) a concurrent second root; linear child isolation; a TOML-configured
binding with PASS / PERMANENT_FAIL / ESCALATE_HITL reaching the driver through ingress, with
the factory return async and the driver-facing binding sync; post-evaluate hook and
audit-signing failures through the binding; and the `None` opt-out down to the child.
"""

from __future__ import annotations

import asyncio
import inspect
import json
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import pytest
from harness_core import StepID, WorkloadClass
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.validator_framework import ConcreteValidatorFramework
from harness_cp.validator_framework_types import (
    ValidatorEvaluation,
    ValidatorFailClass,
    ValidatorFramework,
    ValidatorOutcome,
    ValidatorResult,
    ValidatorRunBinding,
)
from harness_cp.workflow_driver_types import (
    RunStatus,
    StepExecutionContext,
    StepKind,
    WorkflowStep,
)
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_od.audit_signing_errors import AUDIT_SIGNING_HARD_FAILURES, AuditSigningFailedError
from harness_runtime.bootstrap import run_bootstrap
from harness_runtime.lifecycle.child_workflow_runner import compose_child_workflow_runner
from harness_runtime.lifecycle.durable_child_admission import RefuseDurableChildAdmission
from harness_runtime.lifecycle.sub_agent_dispatch import SubAgentDispatchPayload
from harness_runtime.types import HarnessContext
from mcp.shared.memory import create_connected_server_and_client_session
from opentelemetry.sdk.trace import TracerProvider

from ..pause_journal_roots import placed_config
from ..test_lifecycle_sub_agent_dispatch import (
    _brief,  # pyright: ignore[reportPrivateUsage]
    _child_manifest,  # pyright: ignore[reportPrivateUsage]
    _dispatcher,  # pyright: ignore[reportPrivateUsage]
)
from .conftest import WORKLOAD, build_config
from .test_u_rt_85_validator_framework_e2e import (
    _ESCALATION_PALETTE,  # pyright: ignore[reportPrivateUsage]
    _load_toml_config,  # pyright: ignore[reportPrivateUsage]
    _manifest,  # pyright: ignore[reportPrivateUsage]
    _RecordingSurface,  # pyright: ignore[reportPrivateUsage]
)

_MODEL = ModelBinding(provider="anthropic", model="claude-haiku-4-5")
_CHARGE = "revalidate"
"""A step whose id contains this word draws REVALIDATE; every other step PASSes."""


class _ChargeByStepId:
    """Operator validator: REVALIDATE for charging steps, PASS for the rest."""

    async def validate(
        self, step: WorkflowStep, step_result: Any, *, step_context: Any
    ) -> ValidatorResult:
        _ = step_result, step_context
        if _CHARGE in step.step_id:
            return ValidatorResult(
                outcome=ValidatorOutcome.REVALIDATE,
                fail_class=ValidatorFailClass.SCHEMA_VIOLATION,
            )
        return ValidatorResult(outcome=ValidatorOutcome.PASS)


class _EveryStep(Mapping[StepID, _ChargeByStepId]):
    """One validator covers every step id the framework is asked about."""

    _validator = _ChargeByStepId()

    def __getitem__(self, key: StepID) -> _ChargeByStepId:
        return self._validator

    def __iter__(self) -> Iterator[StepID]:
        return iter(())

    def __len__(self) -> int:
        return 0


@dataclass
class _BurdenRecorder:
    """Post-evaluate hook: (step id, post-increment burden_count), appended on the ingress loop."""

    seen: list[tuple[str, int]] = field(default_factory=list[tuple[str, int]])

    async def on_post_evaluate(
        self,
        *,
        step: WorkflowStep,
        step_context: StepExecutionContext,
        evaluation: ValidatorEvaluation,
        execution_time_ms: float,
    ) -> None:
        _ = step_context, execution_time_ms
        self.seen.append((str(step.step_id), evaluation.burden_count))

    def counts(self, prefix: str) -> list[int]:
        """Burden counts of one execution's charging steps, in evaluation order."""
        return [n for sid, n in self.seen if sid.startswith(f"{prefix}/") and _CHARGE in sid]


@dataclass(frozen=True)
class _RaisingHook:
    error: Exception

    async def on_post_evaluate(self, **_: Any) -> None:
        raise self.error


@dataclass
class _Body:
    """Every non-dispatch step: echoes, and records the binding its context carried."""

    carried: list[tuple[str, ValidatorRunBinding | None]] = field(
        default_factory=list[tuple[str, ValidatorRunBinding | None]]
    )

    def dispatch(
        self, binding: Any, step: WorkflowStep, *, step_context: StepExecutionContext
    ) -> dict[str, Any]:
        _ = binding
        self.carried.append((str(step.step_id), step_context.validator_run))
        return {"verdict": step.step_payload.get("verdict", "ok")}


@dataclass(frozen=True)
class _Registry:
    body: _Body
    sub_agent: Any

    def lookup(self, step_kind: StepKind) -> Any:
        return self.sub_agent if step_kind is StepKind.SUB_AGENT_DISPATCH else self.body


@dataclass(frozen=True)
class _Workflow:
    """The `WorkflowObject` surface the `run_workflow` tool reads from its registry."""

    manifest_entry: WorkflowManifestEntry
    steps: tuple[WorkflowStep, ...]
    step_dispatchers: Any = None
    workload_class: WorkloadClass = WORKLOAD
    default_model_binding: ModelBinding = _MODEL

    @property
    def workflow_id(self) -> str:
        return self.manifest_entry.workflow_id


def _step(step_id: str, **payload: Any) -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID(step_id), step_kind=StepKind.DECLARATIVE_STEP, step_payload=payload
    )


def _sub_agent(step_id: str, child_id: str, *child_steps: WorkflowStep) -> WorkflowStep:
    payload = SubAgentDispatchPayload(
        child_workflow_id=child_id,
        # The validator hook fires at the linear step site, and pipeline automation is the
        # workload that admits a linear child, so every child's steps are evaluated.
        child_manifest_entry=_child_manifest(
            workload_class=WorkloadClass.PIPELINE_AUTOMATION,
            topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        ).model_copy(update={"workflow_id": child_id}),
        child_steps=child_steps,
        brief=_brief(),
    )
    return WorkflowStep(
        step_id=StepID(step_id),
        step_kind=StepKind.SUB_AGENT_DISPATCH,
        step_payload=payload.model_dump(),
    )


def _workflow(
    workflow_id: str,
    *steps: WorkflowStep,
    topology: TopologyPattern = TopologyPattern.SINGLE_THREADED_LINEAR,
    step_dispatchers: Any = None,
) -> _Workflow:
    manifest = _manifest(workflow_id).model_copy(update={"topology_pattern": topology})
    return _Workflow(manifest_entry=manifest, steps=steps, step_dispatchers=step_dispatchers)


def _charging(prefix: str, n: int) -> tuple[WorkflowStep, ...]:
    return tuple(_step(f"{prefix}/{_CHARGE}-{i}") for i in range(n))


@dataclass(frozen=True)
class _Daemon:
    ctx: HarnessContext
    body: _Body
    recorder: _BurdenRecorder

    async def run(self, workflow: _Workflow) -> dict[str, Any]:
        """One `run_workflow` invocation over its own in-process MCP client session."""
        server = self.ctx.mcp_server
        assert server is not None
        server.workflow_registry[workflow.workflow_id] = workflow
        async with create_connected_server_and_client_session(
            server.server, raise_exceptions=True
        ) as session:
            result = await session.call_tool("run_workflow", {"workflow_id": workflow.workflow_id})
        assert result.isError is False, result.content
        return json.loads(cast(Any, result.content[0]).text)


async def _daemon(
    placed_root: Path,
    *,
    framework: ValidatorFramework | None,
    recorder: _BurdenRecorder | None = None,
    surface: Any = None,
    config: Any = None,
) -> _Daemon:
    """One bootstrapped daemon whose sub-agent steps run the real dispatcher and child runner.

    `framework` replaces the bootstrap's stage-4 value (`None` is the opt-out) unless a TOML
    `config` produced it, in which case it must be `ctx.validator_framework` itself.
    """
    bootstrapped = await run_bootstrap(
        placed_config(config or build_config(placed_root), placed_root), workload_class=WORKLOAD
    )
    body = _Body()
    dispatcher, _, _ = _dispatcher(placed_root)
    update: dict[str, Any] = {
        "step_dispatchers": _Registry(body, dispatcher),
        # The patched fake tracer provider has no `get_tracer`; the driver needs one.
        "tracer_provider": TracerProvider(),
        "ask_user_question_surface": surface,
    }
    if config is None:
        update["validator_framework"] = framework
    ctx = bootstrapped.model_copy(update=update)
    # The child runner closes over the SAME context, so children use the same registry and
    # recurse into the same dispatcher (stage 5's composition, with the test's step bodies).
    dispatcher.child_workflow_runner = compose_child_workflow_runner(
        cast(Any, ctx), durable_admission=RefuseDurableChildAdmission()
    )
    assert ctx.mcp_server is not None
    ctx.mcp_server._state["_harness_ctx"] = ctx  # pyright: ignore[reportPrivateUsage]
    return _Daemon(ctx=ctx, body=body, recorder=recorder or _BurdenRecorder())


async def _recording_daemon(placed_root: Path) -> _Daemon:
    recorder = _BurdenRecorder()
    framework = ConcreteValidatorFramework(
        validator_registry=_EveryStep(), post_evaluate_hook=recorder
    )
    return await _daemon(placed_root, framework=framework, recorder=recorder)


def _succeeded(result: dict[str, Any]) -> None:
    assert result["status"] == RunStatus.SUCCESS.value, result.get("fail_class")


# ---------------------------------------------------------------------------
# Roots: each run_workflow invocation is its own ledger.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_sequential_roots_on_one_daemon_each_start_at_zero(
    placed_root: Path, patched_runtime: dict[str, Any]
) -> None:
    _ = patched_runtime
    daemon = await _recording_daemon(placed_root)
    for run in ("first", "second"):
        _succeeded(await daemon.run(_workflow(f"wf-{run}", *_charging(run, 2))))

    assert daemon.recorder.counts("first") == [1, 2]
    assert daemon.recorder.counts("second") == [1, 2], (
        "a second sequential root must open a fresh ledger, not continue the first"
    )


@pytest.mark.asyncio
async def test_concurrent_roots_on_one_daemon_each_start_at_zero(
    placed_root: Path, patched_runtime: dict[str, Any]
) -> None:
    _ = patched_runtime
    daemon = await _recording_daemon(placed_root)
    roots = ("left", "right", "third")
    results = await asyncio.gather(
        *(daemon.run(_workflow(f"wf-{root}", *_charging(root, 3))) for root in roots)
    )
    for result in results:
        _succeeded(result)

    for root in roots:
        assert daemon.recorder.counts(root) == [1, 2, 3], (root, daemon.recorder.seen)


# ---------------------------------------------------------------------------
# Nested: real dispatcher + real child runner.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_linear_child_and_depth_two_grandchild_start_at_zero_without_touching_the_parent(
    placed_root: Path, patched_runtime: dict[str, Any]
) -> None:
    _ = patched_runtime
    daemon = await _recording_daemon(placed_root)
    grandchild = (_step(f"grand/{_CHARGE}-0"),)
    child = (
        _step(f"child/{_CHARGE}-0"),
        _sub_agent("child/dispatch-1", "grand-wf", *grandchild),
        _step(f"child/{_CHARGE}-2"),
    )
    root = _workflow(
        "wf-linear-parent",
        _step(f"parent/{_CHARGE}-0"),
        _sub_agent("parent/dispatch-1", "child-wf", *child),
        _step(f"parent/{_CHARGE}-2"),
    )

    _succeeded(await daemon.run(root))

    assert daemon.recorder.counts("grand") == [1], "the depth-2 grandchild opens from zero"
    assert daemon.recorder.counts("child") == [1, 2], (
        "the child opens from zero and its grandchild does not charge it"
    )
    assert daemon.recorder.counts("parent") == [1, 2], (
        "the parent's ledger is unchanged by its child and grandchild"
    )
    carried = dict(daemon.body.carried)
    bindings = [carried[f"{who}/{_CHARGE}-0"] for who in ("parent", "child", "grand")]
    assert len({id(b) for b in bindings}) == 3, "each execution evaluates through its own binding"
    assert [b.burden.count for b in bindings if b is not None] == [2, 2, 1]


@pytest.mark.asyncio
async def test_fan_out_siblings_are_isolated_and_a_concurrent_second_root_is_unaffected(
    placed_root: Path, patched_runtime: dict[str, Any]
) -> None:
    _ = patched_runtime
    daemon = await _recording_daemon(placed_root)
    siblings = ("kid0", "kid1", "kid2")
    fan_out = _workflow(
        "wf-fan-out",
        *(
            _sub_agent(f"fan/dispatch-{i}", f"{kid}-wf", *_charging(kid, 2))
            for i, kid in enumerate(siblings)
        ),
        # A body branch carries the fan-out root's own binding out for inspection.
        _step("fan/root-branch"),
        topology=TopologyPattern.PARALLELIZATION,
    )
    second_root = _workflow("wf-second-root", *_charging("second", 3))

    for result in await asyncio.gather(daemon.run(fan_out), daemon.run(second_root)):
        _succeeded(result)

    for kid in siblings:
        assert daemon.recorder.counts(kid) == [1, 2], (
            f"{kid}: each child's first non-PASS reports 1 and no sibling's count leaks in; "
            f"saw {daemon.recorder.seen}"
        )
    root_binding = dict(daemon.body.carried)["fan/root-branch"]
    assert root_binding is not None
    assert root_binding.burden.count == 0, "the fan-out root's ledger is unchanged by its children"
    assert daemon.recorder.counts("second") == [1, 2, 3], "the concurrent second root"


# ---------------------------------------------------------------------------
# TOML-configured binding through ingress; factory async, driver binding sync.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_toml_binding_reaches_the_driver_through_ingress_with_every_outcome(
    placed_root: Path, patched_runtime: dict[str, Any]
) -> None:
    _ = patched_runtime
    surface = _RecordingSurface()
    daemon = await _daemon(
        placed_root, framework=None, surface=surface, config=_load_toml_config(placed_root)
    )
    framework = daemon.ctx.validator_framework
    assert isinstance(framework, ValidatorFramework)
    assert inspect.iscoroutinefunction(framework.evaluate), "stage 4 returns the async Protocol"

    def single(step_id: str, verdict: str) -> _Workflow:
        return _workflow(f"wf-{step_id}", _step(step_id, verdict=verdict))

    accepted = await daemon.run(single("step-accepted", "ok"))
    rejected = await daemon.run(single("step-rejected", "wrong"))
    assert surface.options == []
    escalated = await daemon.run(single("step-escalated", "unsure"))

    _succeeded(accepted)
    assert {"verdict": "ok"} in accepted["final_state"].values()
    assert rejected["status"] == RunStatus.FAILED.value
    assert rejected["final_state"] is None
    assert rejected["fail_class"].startswith("CP-FAIL-VALIDATOR-PERMANENT")
    assert len(surface.options) == 1 and set(surface.options[0]) <= _ESCALATION_PALETTE
    assert surface.options[0], "the escalation offered a non-empty palette"
    _succeeded(escalated)  # the recording surface approves

    bindings = [binding for _, binding in daemon.body.carried]
    assert len(bindings) == 3
    for binding in bindings:
        assert isinstance(binding, ValidatorRunBinding)
        assert binding.framework is framework
        assert not inspect.iscoroutinefunction(binding.evaluate), "the driver's view is sync"
    assert len({id(b) for b in bindings}) == 3, "each invocation opened its own binding"


# ---------------------------------------------------------------------------
# Failures through the binding.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_an_audit_signing_failure_raises_through_the_binding_to_the_driver(
    placed_root: Path, patched_runtime: dict[str, Any]
) -> None:
    _ = patched_runtime
    framework = ConcreteValidatorFramework(
        validator_registry=_EveryStep(),
        post_evaluate_hook=_RaisingHook(AuditSigningFailedError("signing backend down")),
        audit_signing_raise_through=AUDIT_SIGNING_HARD_FAILURES,
    )
    daemon = await _daemon(placed_root, framework=framework)

    result = await daemon.run(_workflow("wf-signing", _step("signing/pass-0")))

    assert result["status"] == RunStatus.FAILED.value
    assert result["fail_class"] == (
        "validator-framework-failure: AuditSigningFailedError: signing backend down"
    ), "the hook's exception crossed the loop/worker boundary verbatim"


@pytest.mark.asyncio
async def test_a_best_effort_hook_failure_stays_swallowed_through_the_binding(
    placed_root: Path, patched_runtime: dict[str, Any]
) -> None:
    """§28.10 swallows a non-signing hook failure; the binding must not resurrect it."""
    _ = patched_runtime
    framework = ConcreteValidatorFramework(
        validator_registry=_EveryStep(),
        post_evaluate_hook=_RaisingHook(RuntimeError("cost sink down")),
        audit_signing_raise_through=AUDIT_SIGNING_HARD_FAILURES,
    )
    daemon = await _daemon(placed_root, framework=framework)

    _succeeded(await daemon.run(_workflow("wf-cost", _step("cost/pass-0"))))


# ---------------------------------------------------------------------------
# None opt-out: no binding at the root or in any child.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_opt_out_carries_no_binding_to_the_root_or_its_child(
    placed_root: Path, patched_runtime: dict[str, Any]
) -> None:
    _ = patched_runtime
    daemon = await _daemon(placed_root, framework=None)
    root = _workflow(
        "wf-opt-out",
        _step("root/pass-0"),
        _sub_agent("root/dispatch-1", "child-wf", _step("child/pass-0")),
    )

    _succeeded(await daemon.run(root))

    assert [sid for sid, _ in daemon.body.carried] == ["root/pass-0", "child/pass-0"]
    assert [binding for _, binding in daemon.body.carried] == [None, None]
