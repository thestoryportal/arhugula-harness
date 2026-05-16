"""Per-workload-class topology commitment table — U-CP-23.

Implements C-CP-11 §11.1 (per-workload-class topology commitment). Declares the
`PerWorkloadClassTopologyCommitment` record and the 4-entry
`PER_WORKLOAD_CLASS_TOPOLOGY` constant — one commitment per `WorkloadClass`.

**Canonical body.** CP plan v2.4 U-CP-23 (the v2.4 amendment conformed the
`default_pattern` values to the U-CP-22 v2.4-conformed `TopologyPattern`
vocabulary — the v2.1/v2.3 invented values `SEQUENTIAL_HANDOFF` /
`PARENT_FANOUT_AGGREGATE` / `PIPELINE_STAGES` / `ROUTER_DELEGATE` are NOT used).

**Carried Class-2 — `default_pattern` single-vs-dual structural mismatch.**
`PerWorkloadClassTopologyCommitment.default_pattern` is a *single*
`TopologyPattern`, but CP spec §11.1 row 1 (`software-engineering`) commits
*two* primary patterns — `evaluator-optimizer` (writes) and
`orchestrator-workers` (reads/review/eval). The single-valued field cannot hold
both. This is a pre-existing v2.1 structural defect surfaced by the v2.4
conformance pass and recorded at CP plan v2.4 §0.8; classified **Class 2
(non-halting)** in `.harness/pipeline-fork-queue.md` item 4 — "operator picks
the structural reading; non-blocking for landing". Materializable resolution
applied here: `software-engineering.default_pattern = EVALUATOR_OPTIMIZER` (the
first-listed primary — the writes pattern); `ORCHESTRATOR_WORKERS` (the
reads/review/eval primary) is carried in `permitted_patterns`. The operator's
structural-restructure decision (multi-valued `default_pattern`) remains a
Class-2 carry; it does not block this landing.

**`permitted_patterns`.** Per U-CP-23 acceptance #3, `permitted_patterns`
composes with `is_admissible` (U-CP-22 §10.3 cross-pattern predicate) — no
permitted pattern violates admissibility. CP spec §11.1 commits only the
"Primary topology pattern" column; `permitted_patterns` is built as the
workload's primary pattern(s) plus every `TopologyPattern` admissible for that
workload per `is_admissible`. The set is thus admissibility-closed by
construction.

`WorkloadClass` is the cross-axis enum from `harness-core` (U-CP-00);
`TopologyPattern` / `is_admissible` are from U-CP-22 (`harness_cp.topology_pattern`).

Authority: Implementation_Plan_Control_Plane_v2_4.md §2.4 U-CP-23 (v2.4
amendment — `PER_WORKLOAD_CLASS_TOPOLOGY` default-pattern values conformed to
U-CP-22 v2.4-conformed `TopologyPattern`); Spec_Control_Plane_v1_2.md §11
C-CP-11 §11.1 (preserved verbatim into v1.3); ADR-D4 v1.1 §1.2.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from harness_core import WorkloadClass
from harness_cp.topology_pattern import TopologyPattern, is_admissible


class PerWorkloadClassTopologyCommitment(BaseModel):
    """One workload class's topology commitment (C-CP-11 §11.1 row)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    workload_class: WorkloadClass
    """The workload class this commitment binds."""

    default_pattern: TopologyPattern
    """The §11.1 "Primary topology pattern" (default). For
    `software-engineering` this is the first-listed primary
    (`EVALUATOR_OPTIMIZER`, writes) — see the module docstring's carried
    Class-2 single-vs-dual note."""

    permitted_patterns: frozenset[TopologyPattern]
    """The patterns admissible for this workload class — contains
    `default_pattern` and is closed under `is_admissible` (U-CP-22 §10.3)."""

    rationale: str
    """C-CP-11 §11.1 commitment narrative."""


def _permitted(
    workload: WorkloadClass, primaries: frozenset[TopologyPattern]
) -> frozenset[TopologyPattern]:
    """Build the admissibility-closed permitted set for a workload class.

    The set is the primary pattern(s) plus every `TopologyPattern` that
    `is_admissible` admits for this workload — guaranteeing U-CP-23 acc#3
    (no permitted pattern violates admissibility) by construction.
    """
    admissible = {p for p in TopologyPattern if is_admissible(p, workload)}
    return primaries | frozenset(admissible)


PER_WORKLOAD_CLASS_TOPOLOGY: tuple[PerWorkloadClassTopologyCommitment, ...] = (
    PerWorkloadClassTopologyCommitment(
        workload_class=WorkloadClass.SOFTWARE_ENGINEERING,
        default_pattern=TopologyPattern.EVALUATOR_OPTIMIZER,
        permitted_patterns=_permitted(
            WorkloadClass.SOFTWARE_ENGINEERING,
            frozenset(
                {
                    TopologyPattern.EVALUATOR_OPTIMIZER,
                    TopologyPattern.ORCHESTRATOR_WORKERS,
                }
            ),
        ),
        rationale=(
            "§11.1 row 1 — evaluator-optimizer (writes); orchestrator-workers "
            "(reads/review/eval); strict single-threaded writer per Cognition "
            "strong-convergence."
        ),
    ),
    PerWorkloadClassTopologyCommitment(
        workload_class=WorkloadClass.CONTENT_CREATION,
        default_pattern=TopologyPattern.EVALUATOR_OPTIMIZER,
        permitted_patterns=_permitted(
            WorkloadClass.CONTENT_CREATION,
            frozenset({TopologyPattern.EVALUATOR_OPTIMIZER}),
        ),
        rationale=(
            "§11.1 row 2 — evaluator-optimizer (operator-as-reviewer dominant "
            "at design-time); strict single-threaded author."
        ),
    ),
    PerWorkloadClassTopologyCommitment(
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        default_pattern=TopologyPattern.SINGLE_THREADED_LINEAR,
        permitted_patterns=_permitted(
            WorkloadClass.PIPELINE_AUTOMATION,
            frozenset(
                {
                    TopologyPattern.SINGLE_THREADED_LINEAR,
                    TopologyPattern.ORCHESTRATOR_WORKERS,
                }
            ),
        ),
        rationale=(
            "§11.1 row 3 — sequential default (single-threaded-linear); "
            "orchestrator-workers for idempotent parallel stages only; strict "
            "sequential durable spine."
        ),
    ),
    PerWorkloadClassTopologyCommitment(
        workload_class=WorkloadClass.RESEARCH,
        default_pattern=TopologyPattern.ORCHESTRATOR_WORKERS,
        permitted_patterns=_permitted(
            WorkloadClass.RESEARCH,
            frozenset({TopologyPattern.ORCHESTRATOR_WORKERS}),
        ),
        rationale=(
            "§11.1 row 4 — orchestrator-workers (Anthropic research system "
            "canonical); relaxed parallel breadth-search; lead synthesizes."
        ),
    ),
)
"""The 4 per-workload-class topology commitments (C-CP-11 §11.1) — one entry
per `WorkloadClass`."""
