"""Workflow execution driver types — U-CP-56.

Implements C-CP-25 §25.2 verbatim:
- `RunStatus` 4-value closed enum
- `RunResult` 7-field record
- `StepKind` 5-value enum (verbatim from CP spec v1.4 §5.2; materialized as a
  named enum at C-CP-25 §25.2 in-session amendment §E 2026-05-20)
- `WorkflowStep` record (in-session amendment §E — step-sequence source
  decoupled from `WorkflowManifestEntry` per operator Path A)

Authority:
- `Spec_Control_Plane_v1_4.md` §25.2 (signatures) + §25 in-session amendment §E
- `Implementation_Plan_Control_Plane_v2_11.md` U-CP-56 acceptance criterion #1
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import Any

from harness_core.identity import StepID
from pydantic import BaseModel, ConfigDict


class RunStatus(StrEnum):
    """The 4 terminal statuses of a driver run (C-CP-25 §25.2).

    Closed at cardinality 4 per the §25.2 enum declaration. Extension would
    require a Workflow §4.1.2 Class-2 revision of §25.2.

    `DRAINED` is the terminal-status observable that replaces a `DRAINED`
    lifecycle event class (no such event class exists in the §5.1 closed-at-8
    taxonomy per CP spec v1.4 §25 + Path B operator decision).
    """

    SUCCESS = "success"
    DRAINED = "drained"
    FAILED = "failed"
    PARTIAL = "partial"  # reserved for future multi-step error modes


class StepKind(StrEnum):
    """The 5 step kinds (CP spec v1.4 §5.2 verbatim; materialized at §25.2
    per in-session amendment §E 2026-05-20).

    Member string values match §5.2's verbatim listing:
    `declarative-step / inference-step / tool-step / HITL-step / sub-agent-dispatch`.

    Closed at cardinality 5 — extension is a Workflow §4.1.2 Class-2 revision
    of §5.2.
    """

    DECLARATIVE_STEP = "declarative-step"
    INFERENCE_STEP = "inference-step"
    TOOL_STEP = "tool-step"
    HITL_STEP = "HITL-step"
    SUB_AGENT_DISPATCH = "sub-agent-dispatch"


class WorkflowStep(BaseModel):
    """A single step in the workflow's step sequence (C-CP-25 §25.2
    in-session amendment §E).

    Step sequence is decoupled from `WorkflowManifestEntry`: the manifest
    carries config (engine class, topology, layer budgets, fallback chain,
    HITL placements, per-step overrides), the step sequence carries the
    declarative body steps.

    `step_payload` is opaque to the driver — consumed by the injected
    `step_dispatcher` per the per-axis composition pattern.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    step_id: StepID
    step_kind: StepKind
    step_payload: Mapping[str, Any]


class RunResult(BaseModel):
    """The terminal return shape of a driver run (C-CP-25 §25.2).

    Per-field semantics per §25.2 + §25.3:
    - `status == SUCCESS` → `final_state` populated; `partial_state` /
      `terminal_step_index` / `fail_class` null.
    - `status == DRAINED` → `partial_state` populated; `terminal_step_index`
      populated; `final_state` null; `fail_class` null.
    - `status == FAILED` → `fail_class` populated; one of `partial_state` /
      `terminal_step_index` populated per failure site; `final_state` null.
    - `status == PARTIAL` → reserved.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, arbitrary_types_allowed=True)

    workflow_id: str
    run_id: str
    status: RunStatus
    terminal_step_index: int | None = None
    partial_state: Mapping[str, Any] | None = None
    final_state: Mapping[str, Any] | None = None
    fail_class: str | None = None


__all__ = [
    "RunResult",
    "RunStatus",
    "StepKind",
    "WorkflowStep",
]
