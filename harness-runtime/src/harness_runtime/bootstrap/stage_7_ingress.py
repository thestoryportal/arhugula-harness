"""Stage 7 INGRESS_ACCEPT — freeze + install drain handlers + write pidfile.

Per `Spec_Harness_Runtime_v1.md` v1.1 §2 stage 7 post-conditions:
`ctx` frozen; `harness_runtime.run` accepts a `WorkflowObject` and dispatches.

Per §11 C-RT-11 (U-RT-44): signal handlers installed here.
Per §13 C-RT-13 (U-RT-48): pidfile written here ("The harness writes its
pidfile at stage 7 INGRESS_ACCEPT"). Atomic write via tmp + os.replace.

Order: freeze → install signal handlers → write pidfile. The pidfile
write is the last act of stage 7; subsequent steps in the orchestrator
record stage 7 as completed only if all three succeed.
"""

from __future__ import annotations

import asyncio
import os

from harness_core.workload_class import WorkloadClass

from harness_runtime.admin.pidfile import claim_pidfile, resolve_pidfile_path
from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.drain import install_signal_handlers
from harness_runtime.types import RuntimeConfig

__all__ = ["execute"]


async def execute(
    ctx: _MutableHarnessContext,
    config: RuntimeConfig,
    workload_class: WorkloadClass,
) -> None:
    """Freeze the mutable context; install drain signal handlers; claim the pidfile.

    The pidfile names one live process per repository root: a run started beside a live
    daemon leaves the daemon's pidfile in place (`harness-shutdown` keeps targeting it)
    and releases nothing at shutdown.
    """
    _ = workload_class
    ctx.freeze()
    install_signal_handlers(ctx, asyncio.get_running_loop())
    claim_pidfile(resolve_pidfile_path(config), os.getpid())
