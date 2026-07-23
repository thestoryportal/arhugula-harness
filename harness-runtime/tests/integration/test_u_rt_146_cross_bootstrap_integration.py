"""U-RT-146 — cross-bootstrap capacity-authority continuity, integration tier.

The unit-level suite (`tests/test_u_rt_146_cross_bootstrap_capacity_authority.py`)
exercises `FrameLedger`/`SubAgentDispatchExecutor`/`adopt_or_create_process_
capacity_ledger` directly — it does NOT drive the actual composition-root
wiring at `bootstrap/stage_5_loop_init.py:620-622`, so a regression THERE
(e.g. reverting to unconditional `SubAgentDispatchExecutor(frame_budget=...)`
construction, bypassing the adopt-or-create ledger seam entirely) would not
be caught by those tests alone (codex out-of-family review finding). This
module drives two REAL sequential `run_bootstrap()` calls in one process —
exactly the `api.run()` boundary the fork describes — and asserts the
composition root's own wiring, not a manually-constructed stand-in.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from harness_core import SubAgentDispatchCapacityError
from harness_runtime.bootstrap import run_bootstrap
from harness_runtime.shutdown import shutdown

from tests.integration.conftest import WORKLOAD, build_config


@pytest.mark.asyncio
async def test_stage_5_adopts_ledger_across_sequential_bootstraps(
    tmp_path: Path,
    patched_runtime: dict[str, Any],
) -> None:
    """Drives the REAL `bootstrap/stage_5_loop_init.py` construction line
    twice in one process. A revert to unconditional fresh construction (the
    actual defect this unit fixes) would make this test's residual
    assertion fail — unlike the unit-level suite, which calls
    `adopt_or_create_process_capacity_ledger()` directly and so cannot
    observe a regression at the stage-5 CALL SITE itself.
    """
    _ = patched_runtime
    config = build_config(tmp_path).model_copy(update={"sub_agent_dispatch_max_workers": 4})

    # Bootstrap 1: occupy 2 of 4 frames via a lease that is never released
    # (simulates a worker still draining past its own bootstrap's shutdown
    # deadline — the lease releases only via its own done-callback, never
    # at bootstrap teardown).
    ctx1 = await run_bootstrap(config, workload_class=WORKLOAD)
    executor1 = ctx1.sub_agent_dispatch_executor
    assert executor1 is not None
    executor1.reserve(2, step_id="run1-straggler", descent_chain=("run1-straggler",))
    await shutdown(ctx1, timeout=5.0)

    # Bootstrap 2: a FRESH executor object bound to the SAME adopted ledger.
    ctx2 = await run_bootstrap(config, workload_class=WORKLOAD)
    executor2 = ctx2.sub_agent_dispatch_executor
    assert executor2 is not None
    assert executor2 is not executor1  # never the SAME executor object
    assert executor1._admission_lock is executor2._admission_lock  # SAME ledger lock

    assert executor2.available_frames == 2  # 4 - 2 occupied, never the full 4
    with pytest.raises(SubAgentDispatchCapacityError):
        executor2.reserve(3, step_id="run2-over", descent_chain=("run2-over",))

    await shutdown(ctx2, timeout=5.0)
