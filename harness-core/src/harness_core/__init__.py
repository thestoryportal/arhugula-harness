"""`harness-core` — H_T shared types + cross-axis utilities.

Public API surface for the cross-axis shared types. Per `CLAUDE.md` §3.3,
`harness-core` hosts the types consumed by ≥2 axes; every consuming axis
imports them from this one path so `pyright` resolves a single nominal type.

Members:

- `WorkloadClass` — U-CP-00 (C-CP-07 §7.3 workload-class taxonomy).
- `DeploymentSurface`, `PersonaTier`, `WorkflowEventClass` — U-CORE-01
  cross-cutting enums.
- The nine identity-alias `str`-newtypes — U-CORE-01 identity module.
"""

from __future__ import annotations

from harness_core.deployment_surface import DeploymentSurface
from harness_core.identity import (
    ActionID,
    ContractID,
    EntryID,
    ReferenceToUnit,
    StageID,
    StepID,
    ThreadID,
    UnitId,
    WorkflowID,
)
from harness_core.persona_tier import PersonaTier
from harness_core.workflow_event_class import WorkflowEventClass
from harness_core.workload_class import WorkloadClass

__all__ = [
    "ActionID",
    "ContractID",
    "DeploymentSurface",
    "EntryID",
    "PersonaTier",
    "ReferenceToUnit",
    "StageID",
    "StepID",
    "ThreadID",
    "UnitId",
    "WorkflowEventClass",
    "WorkflowID",
    "WorkloadClass",
]
