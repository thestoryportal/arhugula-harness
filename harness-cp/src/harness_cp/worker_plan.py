"""Lead-directed worker plan for orchestrator fan-outs (CP v1.130 §25.11.1).

The **pool** is an orchestrator fan-out's declared worker sequence (`steps[1:]` after any
terminal `POST_JOIN_SYNTHESIS` is carved off). A plan selects, orders and briefs pool members;
it never creates a worker or changes a member's identity, kind, payload or bindings.

`derive_worker_plan` is pure and is the only unit that reads a plan from an orchestrator
output [LAW:single-enforcer]. Its `WorkerPlan` is the parsed proof every fan-out consumer
reads [LAW:parse-dont-validate]: a worker's branch ordinal is its plan position, and its
`declared_index` is fixed by the declaration, never by the plan.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, cast

from pydantic import BaseModel, ConfigDict, ValidationError

from harness_cp.sub_agent_brief import SubAgentBrief, compute_brief_summary_hash
from harness_cp.topology_pattern import WorkerSelection
from harness_cp.workflow_driver_types import StepKind, WorkflowStep

__all__ = [
    "WORKER_PLAN_KEY",
    "WorkerAssignment",
    "WorkerPlan",
    "WorkerPlanInvalid",
    "WorkerSelection",
    "derive_worker_plan",
]

#: The orchestrator-output key a `LEAD_PLAN` fan-out reads its plan from.
WORKER_PLAN_KEY = "worker_plan"

_ASSIGNMENT_KEYS = frozenset({"worker", "brief"})


class WorkerAssignment(BaseModel):
    """One planned worker: a pool member, its declared ordinal and its lead brief."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    step: WorkflowStep
    declared_index: int
    """The step's ordinal in the workflow `steps` (orchestrator = 0)."""

    brief: SubAgentBrief | None
    """Set iff `LEAD_PLAN` and the step is `SUB_AGENT_DISPATCH`."""


class WorkerPlan(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    assignments: tuple[WorkerAssignment, ...]


class WorkerPlanInvalid(Exception):  # noqa: N818 — spec-named (CP v1.130 §25.11.1.1)
    """The orchestrator output's plan fails §25.11.1.3(4); `reason` is the named reason."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def derive_worker_plan(
    selection: WorkerSelection,
    orchestrator_output: Mapping[str, Any],
    pool: Sequence[WorkflowStep],
) -> WorkerPlan:
    """Return the fan-out's worker plan (§25.11.1.3); raise `WorkerPlanInvalid` on a bad plan."""
    declared = {str(step.step_id): (index + 1, step) for index, step in enumerate(pool)}
    match selection:
        case WorkerSelection.DECLARED_POOL:
            # The output is not read: a `worker_plan` key has no effect here.
            return WorkerPlan(
                assignments=tuple(
                    WorkerAssignment(step=step, declared_index=index, brief=None)
                    for index, step in declared.values()
                )
            )
        case WorkerSelection.LEAD_PLAN:
            return WorkerPlan(assignments=_parse_lead_plan(orchestrator_output, declared))


def _parse_lead_plan(
    orchestrator_output: Mapping[str, Any],
    declared: Mapping[str, tuple[int, WorkflowStep]],
) -> tuple[WorkerAssignment, ...]:
    if WORKER_PLAN_KEY not in orchestrator_output:
        raise WorkerPlanInvalid("missing-worker-plan")
    raw: object = orchestrator_output[WORKER_PLAN_KEY]
    if not isinstance(raw, Sequence) or isinstance(raw, str | bytes):
        raise WorkerPlanInvalid("not-a-sequence")
    entries: list[object] = list(cast("Sequence[object]", raw))
    if not all(isinstance(entry, Mapping) for entry in entries):
        raise WorkerPlanInvalid("not-a-sequence")
    seen: set[str] = set()
    return tuple(
        _parse_assignment(cast("Mapping[Any, Any]", entry), declared, seen) for entry in entries
    )


def _parse_assignment(
    entry: Mapping[Any, Any],
    declared: Mapping[str, tuple[int, WorkflowStep]],
    seen: set[str],
) -> WorkerAssignment:
    worker = entry.get("worker")
    if not set(entry) <= _ASSIGNMENT_KEYS or not isinstance(worker, str):
        raise WorkerPlanInvalid("malformed-assignment")
    if worker not in declared:
        raise WorkerPlanInvalid(f"unknown-worker:{worker}")
    if worker in seen:
        raise WorkerPlanInvalid(f"duplicate-worker:{worker}")
    seen.add(worker)
    declared_index, step = declared[worker]
    is_sub_agent = step.step_kind is StepKind.SUB_AGENT_DISPATCH
    has_brief = "brief" in entry
    if is_sub_agent and not has_brief:
        raise WorkerPlanInvalid(f"missing-brief:{worker}")
    if has_brief and not is_sub_agent:
        raise WorkerPlanInvalid(f"brief-on-non-subagent:{worker}")
    brief = _parse_brief(worker, entry["brief"]) if has_brief else None
    return WorkerAssignment(step=step, declared_index=declared_index, brief=brief)


def _parse_brief(worker: str, raw: Any) -> SubAgentBrief:
    # The hash is computed here, never read from the plan [LAW:one-source-of-truth]: a
    # supplied `summary_hash` is an extra key and rejected.
    if not isinstance(raw, Mapping) or "summary_hash" in raw:
        raise WorkerPlanInvalid(f"malformed-brief:{worker}")
    try:
        unhashed = SubAgentBrief.model_validate({**raw, "summary_hash": ""})
    except ValidationError as exc:
        raise WorkerPlanInvalid(f"malformed-brief:{worker}") from exc
    return unhashed.model_copy(update={"summary_hash": compute_brief_summary_hash(unhashed)})
