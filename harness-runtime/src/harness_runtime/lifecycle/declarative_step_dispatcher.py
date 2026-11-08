"""Runtime `DECLARATIVE_STEP` step dispatcher — a step whose payload declares its output.

A declarative step does no work: its `step_payload` is exactly `{"output": {...}}` and
dispatch returns that mapping as the step's output. It reaches no provider, tool, file,
clock or process, so it is bound at stage 5 unconditionally (it never makes a workflow
inference-bearing; `api._workflow_requires_inference`) and is re-fire-safe. An
orchestrator declared this way hands its constant `worker_plan` to the CP driver's
`LEAD_PLAN` selection through the ordinary orchestrator-output path; nothing here reads
or interprets the output.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.workflow_driver_types import StepExecutionContext, WorkflowStep
from pydantic import BaseModel, ConfigDict, JsonValue, ValidationError

__all__ = [
    "DeclarativeStepDispatcher",
    "DeclarativeStepPayload",
    "DeclarativeStepPayloadShapeError",
]


class DeclarativeStepPayload(BaseModel):
    """The whole `DECLARATIVE_STEP` payload: the step's declared output, nothing else."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    # [LAW:types-are-the-program] JSON values only: the output is recorded and joined as data.
    output: dict[str, JsonValue]


class DeclarativeStepPayloadShapeError(Exception):
    """`step.step_payload` is not a `DeclarativeStepPayload` (`RT-FAIL-PAYLOAD-SHAPE`)."""

    def __init__(self, step_id: str, reason: str) -> None:
        super().__init__(
            f"RT-FAIL-PAYLOAD-SHAPE: DECLARATIVE_STEP {step_id!r} step_payload "
            f"failed DeclarativeStepPayload validation: {reason}"
        )


class DeclarativeStepDispatcher:
    """`StepDispatcher` for `DECLARATIVE_STEP`: parse the payload, return its output."""

    def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: StepExecutionContext,
    ) -> Mapping[str, Any]:
        # [LAW:parse-dont-validate] the one checkpoint; a mis-shaped payload fails the step loudly.
        try:
            payload = DeclarativeStepPayload.model_validate(dict(step.step_payload))
        except ValidationError as exc:
            raise DeclarativeStepPayloadShapeError(str(step.step_id), str(exc)) from exc
        return payload.output
