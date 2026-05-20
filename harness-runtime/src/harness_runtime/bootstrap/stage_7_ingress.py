"""Stage 7 INGRESS_ACCEPT — freeze `_MutableHarnessContext` → `HarnessContext`.

Per `Spec_Harness_Runtime_v1.md` v1.1 §2 stage 7 post-conditions:
`ctx` frozen; `harness_runtime.run` accepts a `WorkflowObject` and dispatches.

The freeze itself happens via `_MutableHarnessContext.freeze()`; this stage
shim simply calls it and publishes the result back onto the builder for the
orchestrator to retrieve. `freeze()` raises `IncompleteBootstrapError` if
any required field is None — a guard against an orchestrator or stage-
implementation defect.
"""

from __future__ import annotations

from harness_core.workload_class import WorkloadClass

from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.types import RuntimeConfig

__all__ = ["execute"]


async def execute(
    ctx: _MutableHarnessContext,
    config: RuntimeConfig,
    workload_class: WorkloadClass,
) -> None:
    """Freeze the mutable context into `HarnessContext`; publish on `ctx.frozen`."""
    _ = config, workload_class
    ctx.freeze()
