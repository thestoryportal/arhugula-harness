"""Topology-pattern dispatcher binding — stage 5 LOOP_INIT (U-RT-40).

Per `Spec_Harness_Runtime_v1.md` v1.1 §C-RT-02 stage 5 invariants +
§C-RT-04 `HarnessContext.topology_dispatcher` field (`TopologyDispatcher`
(CP, runtime-bound) — stage 5). The runtime binds CP's `TopologyPattern`
enum + `is_admissible` predicate (C-CP-10 §10.1, §10.3) into a
runtime-time dispatcher that satisfies the `TopologyDispatcher`
Protocol (narrowed at `harness_runtime.types` at this landing).

**Risk-gate clearance at U-RT-40 landing.** Tension 002 (TopologyPattern
3-way divergence between CP plan / spec C-CP-10 / ADR-D4 §1.1) was
RESOLVED 2026-05-15 per operator decision (Set 2 — conformed to spec
C-CP-10 §10.1 verbatim at 4 loci; recorded at
`.harness/pipeline-fork-queue.md` line 99). The landed CP
`TopologyPattern` enum carries the spec-canonical 6-value taxonomy
(`single-threaded-linear` / `orchestrator-workers` / `decentralized-handoff`
/ `hierarchical-delegation` / `evaluator-optimizer` / `parallelization`).
No carry-forward; this landing lands cleanly against the conformed
enum.

**Stateless wrapper.** `dispatch` extracts the manifest's bound
`topology_pattern`; `is_admissible` delegates to CP's pure predicate.
The runtime adds no state between calls; per-call inputs drive the
result deterministically per C-CP-10's contract.

**Module convention.** One module per unit.
`materialize_topology_dispatcher_stage` composer returns a frozen
`TopologyDispatcherStage` dataclass with `slots=True`. Typed
`TopologyDispatcherBindError` for bootstrap-time failures. Mirrors the
L5 / L6 / L7 / U-RT-39 stage shape established at U-RT-21..39.
"""

from __future__ import annotations

from dataclasses import dataclass

from harness_core.workload_class import WorkloadClass
from harness_cp.topology_pattern import (
    TopologyPattern,
    is_admissible,
)
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry

from harness_runtime.types import RuntimeConfig


class TopologyDispatcherBindError(Exception):
    """Raised when topology-dispatcher stage materialization fails."""


@dataclass(frozen=True, slots=True)
class RuntimeTopologyDispatcher:
    """Topology-pattern dispatcher runtime surface (C-CP-10 §10.1, §10.3 binding).

    Stateless. `dispatch` reads the manifest's bound `topology_pattern`;
    `is_admissible` delegates to CP's pure `is_admissible` predicate.
    Satisfies the `harness_runtime.types.TopologyDispatcher` Protocol
    (narrowed at U-RT-40 landing).
    """

    def dispatch(self, manifest_entry: WorkflowManifestEntry) -> TopologyPattern:
        """Return the bound `TopologyPattern` for a workflow manifest entry.

        The manifest's `topology_pattern` field carries the operator-
        committed pattern per C-CP-06 §6.1; this method returns it
        directly. Admissibility validation is a separate concern —
        callers verify via `is_admissible(pattern, workload)` if a
        cross-pattern adoption gate is needed (C-CP-10 §10.3).
        """
        return manifest_entry.topology_pattern

    def is_admissible(
        self,
        pattern: TopologyPattern,
        workload: WorkloadClass,
    ) -> bool:
        """Cross-pattern admissibility per C-CP-10 §10.3 (delegates to CP).

        Answers: is `pattern` an admissible *non-primary* topology for
        `workload`? Returns `True` for the §10.3-annotated cells (per
        ADR-D4 v1.1 §1.2); `False` otherwise. Primary-pattern selection
        is committed separately at C-CP-11 §11.1 (U-CP-23) — a `False`
        result here means "not annotated as cross-pattern admissible at
        §10.3", not "inadmissible outright".
        """
        return is_admissible(pattern, workload)


@dataclass(frozen=True, slots=True)
class TopologyDispatcherStage:
    """Frozen result of stage 5 LOOP_INIT topology-dispatcher binding.

    The bootstrap orchestrator (U-RT-43) binds `dispatcher` to
    `HarnessContext.topology_dispatcher` (C-RT-04 stage 5 invariant).
    Mirrors the L5 / L6 / L7 / U-RT-39 stage shape.
    """

    dispatcher: RuntimeTopologyDispatcher


def materialize_topology_dispatcher_stage(
    config: RuntimeConfig,
) -> TopologyDispatcherStage:
    """Build the stage 5 LOOP_INIT topology dispatcher stage.

    The dispatcher is stateless — no construction-time fields consumed.
    `config` is read for API consistency with the L5..L7 + U-RT-39
    composers; no field is consumed at HEAD (the spec-default
    `config.default_topology` is a top-level fallback for workflows that
    don't supply their own manifest, but resolution lives at the
    workflow-execution layer per C-RT-04 — not at the dispatcher).
    """
    _ = config
    return TopologyDispatcherStage(dispatcher=RuntimeTopologyDispatcher())
