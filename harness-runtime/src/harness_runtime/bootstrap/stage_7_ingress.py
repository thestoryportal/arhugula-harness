"""Stage 7 INGRESS_ACCEPT — freeze `_MutableHarnessContext` + install drain handlers.

Per `Spec_Harness_Runtime_v1.md` v1.1 §2 stage 7 post-conditions:
`ctx` frozen; `harness_runtime.run` accepts a `WorkflowObject` and dispatches.

Per §11 C-RT-11 (U-RT-44 landing): signal handlers installed here so that
SIGTERM/SIGINT set `ctx.drained_flag` + the process-level drain flag. The
spec marks stage 7 as the suggested install site (§11 "Deferred to
implementation discretion"); this landing commits to that suggestion.

`freeze()` raises `IncompleteBootstrapError` if any required field is None
— a guard against an orchestrator or stage-implementation defect. Freeze
runs first; signal-handler install runs second. The handlers reference
the same `asyncio.Event` carried by the frozen `HarnessContext` (the
builder and the frozen value share the event by-reference), so the
post-freeze drain pathway is intact.
"""

from __future__ import annotations

import asyncio

from harness_core.workload_class import WorkloadClass

from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.drain import install_signal_handlers
from harness_runtime.types import RuntimeConfig

__all__ = ["execute"]


async def execute(
    ctx: _MutableHarnessContext,
    config: RuntimeConfig,
    workload_class: WorkloadClass,
) -> None:
    """Freeze the mutable context; install drain signal handlers."""
    _ = config, workload_class
    ctx.freeze()
    install_signal_handlers(ctx, asyncio.get_running_loop())
