"""Stage 6 CXA_WIRING — terminal manifest import + 5 cross-axis wiring composers.

Per `Spec_Harness_Runtime_v1.md` v1.1 §2 stage 6 post-conditions: all 5
terminal exporter manifests imported; all 24 phase-2-runtime edges wired
(test fixture exercises each).

Composer call order:
1. `materialize_cxa_terminal_imports_stage` — realizes the 5 manifest imports
   (side-effect import; Pattern P1 typed-seam binding).
2. `materialize_as_is_wiring_stage(config, ledger_writer)` — AS→IS (1 edge).
3. `materialize_cp_is_wiring_stage(config, ledger_writer)` — CP→IS (1 of 17
   edges per U-RT-35 PARTIAL-LAND; `[[fork-cp-is-wiring-gaps]]` Class 1 open).
4. `materialize_od_is_wiring_stage(config, audit_writer, od_manifest)` — OD→IS
   (2 edges).
5. `materialize_od_as_wiring_stage(config, od_manifest)` — OD→AS (1 edge).
6. `materialize_od_cp_wiring_stage(config, od_manifest)` — OD→CP (3 edges,
   includes F-CP-01 Stage 3b inversion verification).

The 5 wiring composers' returned `*Stage` records are stashed on
`ctx.cxa_stages` for verification + test introspection; they are not lifted
to `HarnessContext` (the wiring side-effects + the runtime registries
populated at earlier stages are what matters).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from harness_core.workload_class import WorkloadClass
from harness_od.substrate_seam_exports_aggregate_manifest import (
    OD_SUBSTRATE_SEAM_EXPORTS_MANIFEST,
)

from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.lifecycle.as_is_wiring import materialize_as_is_wiring_stage
from harness_runtime.lifecycle.cp_is_wiring import materialize_cp_is_wiring_stage
from harness_runtime.lifecycle.cxa_terminal_imports import (
    materialize_cxa_terminal_imports_stage,
)
from harness_runtime.lifecycle.od_as_wiring import materialize_od_as_wiring_stage
from harness_runtime.lifecycle.od_cp_wiring import materialize_od_cp_wiring_stage
from harness_runtime.lifecycle.od_is_wiring import materialize_od_is_wiring_stage
from harness_runtime.lifecycle.procedural_tier_snapshot import (
    make_procedural_tier_snapshot_resolver,
)
from harness_runtime.types import RuntimeConfig

if TYPE_CHECKING:
    from harness_runtime.types import HarnessContext

__all__ = ["execute"]


async def execute(
    ctx: _MutableHarnessContext,
    config: RuntimeConfig,
    workload_class: WorkloadClass,
) -> None:
    """Populate stage 6 CXA_WIRING `cxa_stages` on `ctx`."""
    _ = workload_class
    assert ctx.ledger_writer is not None, "stage 1 IS must precede stage 6 CXA_WIRING"
    assert ctx.audit_writer is not None, "stage 4 OD must precede stage 6 CXA_WIRING"

    od_manifest = OD_SUBSTRATE_SEAM_EXPORTS_MANIFEST

    ctx.cxa_stages["cxa_terminal_imports"] = materialize_cxa_terminal_imports_stage(
        config,
    )
    ctx.cxa_stages["as_is_wiring"] = materialize_as_is_wiring_stage(
        config,
        ctx.ledger_writer,
    )
    # CP spec v1.30 §1.4: build the procedural-tier-snapshot resolver-closure
    # at stage 6 entry where ctx.skills (stage 2) + ctx.routing_manifest
    # (stage 3b) are populated. The resolver captures `ctx` (the mutable
    # context being finalized at stage 6); at composer invocation time the
    # closure re-resolves against the same captured ctx per U-RT-112 AC #8
    # direct-compute discipline. The _MutableHarnessContext exposes the same
    # `.skills` + `.routing_manifest` attribute surfaces as HarnessContext;
    # cast is structural per the resolver's narrow consumption.
    procedural_tier_snapshot_resolver = make_procedural_tier_snapshot_resolver(
        cast("HarnessContext", ctx),
    )
    ctx.cxa_stages["cp_is_wiring"] = materialize_cp_is_wiring_stage(
        config,
        ctx.ledger_writer,
        procedural_tier_snapshot_resolver,
    )
    ctx.cxa_stages["od_is_wiring"] = materialize_od_is_wiring_stage(
        config,
        ctx.audit_writer,
        od_manifest,
    )
    ctx.cxa_stages["od_as_wiring"] = materialize_od_as_wiring_stage(
        config,
        od_manifest,
    )
    ctx.cxa_stages["od_cp_wiring"] = materialize_od_cp_wiring_stage(
        config,
        od_manifest,
    )
