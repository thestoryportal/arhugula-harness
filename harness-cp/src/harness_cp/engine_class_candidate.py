"""Per-deployment-surface engine-class candidate mapping — U-CP-16.

Implements C-CP-07 §7.2 (per-deployment-surface candidate mapping). Declares
the `EngineClassCandidate` record and the 3-entry `ENGINE_CLASS_CANDIDATES`
constant — one candidate set per `DeploymentSurface`, with the structural
exclusion reasons per excluded `EngineClass`.

**Carrier note.** `DeploymentSurface` is the cross-axis foundational enum
declared at `harness_core.deployment_surface` (U-CORE-01) — consumed by the
IS / AS / CP / OD axes. It is imported from `harness-core`, not re-declared:
the plan U-CP-16 Signatures block displays a `DeploymentSurface` enum, but
`harness-core` already carries it byte-exact (3 values: `local-development`,
`self-hosted-server`, `managed-cloud`) per the single-carrier discipline
(`CLAUDE.md` §3.3). Re-declaring it would make `pyright` treat the per-unit
copies as distinct nominal types and break cross-unit composition.

`EngineClass` is the U-CP-15 5-value taxonomy (`harness_cp.engine_class`).

**Candidate sets.** The `candidate_set` per surface follows the U-CP-16
acceptance #2 table — the §7.2-grounded structural-exclusion reading: every
engine class is a candidate at a surface *unless* §7.2's cell-exclusion
discipline structurally rejects it. `RECONCILER_LOOP` is excluded at
`local-development` (requires a K8s control plane); `PURE_PATTERN_NO_ENGINE` is
excluded at `self-hosted-server` and `managed-cloud` (the durable pole at a
server/managed context requires a durability primitive — §7.2 "pure-pattern-
no-engine excluded for durable pole"). Specific recommended candidates *within*
each set are operator-discretion per the §7.2 deferred list.

Authority: Implementation_Plan_Control_Plane_v2_1.md §2 U-CP-16 (preserved
verbatim through v2.6 — no body rewrite); Spec_Control_Plane_v1_2.md §7
C-CP-07 §7.2 (preserved verbatim into v1.3); ADR-D1 v1.1 §1.2.
"""

from __future__ import annotations

from harness_core import DeploymentSurface
from pydantic import BaseModel, ConfigDict

from harness_cp.engine_class import EngineClass


class EngineClassCandidate(BaseModel):
    """The engine-class candidate set for one deployment surface (§7.2)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    deployment_surface: DeploymentSurface
    """The deployment surface this candidate set is bound to."""

    candidate_set: frozenset[EngineClass]
    """The engine classes admissible at this surface."""

    exclusion_reasons: dict[EngineClass, str]
    """The §7.2 cell-exclusion reason per structurally-excluded class —
    one entry per `EngineClass` absent from `candidate_set`."""


ENGINE_CLASS_CANDIDATES: tuple[EngineClassCandidate, ...] = (
    EngineClassCandidate(
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        candidate_set=frozenset(
            {
                EngineClass.EVENT_SOURCED_REPLAY,
                EngineClass.SAVE_POINT_CHECKPOINT,
                EngineClass.PURE_PATTERN_NO_ENGINE,
                EngineClass.WAL_SEGMENT,
            }
        ),
        exclusion_reasons={
            EngineClass.RECONCILER_LOOP: "requires K8s control plane",
        },
    ),
    EngineClassCandidate(
        deployment_surface=DeploymentSurface.SELF_HOSTED_SERVER,
        candidate_set=frozenset(
            {
                EngineClass.EVENT_SOURCED_REPLAY,
                EngineClass.SAVE_POINT_CHECKPOINT,
                EngineClass.RECONCILER_LOOP,
                EngineClass.WAL_SEGMENT,
            }
        ),
        exclusion_reasons={
            EngineClass.PURE_PATTERN_NO_ENGINE: (
                "server context requires durability primitive"
            ),
        },
    ),
    EngineClassCandidate(
        deployment_surface=DeploymentSurface.MANAGED_CLOUD,
        candidate_set=frozenset(
            {
                EngineClass.EVENT_SOURCED_REPLAY,
                EngineClass.SAVE_POINT_CHECKPOINT,
                EngineClass.RECONCILER_LOOP,
                EngineClass.WAL_SEGMENT,
            }
        ),
        exclusion_reasons={
            EngineClass.PURE_PATTERN_NO_ENGINE: (
                "managed context requires durability primitive"
            ),
        },
    ),
)
"""The 3 per-deployment-surface engine-class candidate sets (§7.2 verbatim) —
one entry per `DeploymentSurface`."""
