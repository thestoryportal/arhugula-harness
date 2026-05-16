"""9-cell observability matrix — U-OD-01.

Implements C-OD-01 §1.1 (matrix shape), §1.3 (per-cell entries — cell identity
only; the six-field per-cell tuple is C-OD-02's contract), §1.4 (EXCLUDED-cell
rationale), §1.5 (cell-identification invariant).

The matrix is the `PersonaTier x DeploymentSurface` 3x3 product — 9 logical
cells, 8 ACTIVE and 1 structurally EXCLUDED
(`multi-tenant-compliance x local-development`). `CellID` is the canonical key
for all downstream per-cell bindings.

Authority: Implementation_Plan_Operational_Discipline_v2_6.md §3.1.1 U-OD-01
(v2.6 declaration-site conversion; Cluster 1 body preserved verbatim from v2.1
through v2.5 otherwise); Spec_Operational_Discipline_v1_2.md §1 C-OD-01
(preserved verbatim into v1.3); ADR-D6 v1.1 §1.1.

v2.6 declaration-site conversion (R1 §3.4 hand-off): the in-unit `PersonaTier`
and `DeploymentSurface` enum declarations are stripped and imported from
`harness-core` U-CORE-01 via the `[U-CORE-01 (cross-axis: core)]` edge. The
landed enum values matched U-CORE-01 byte-exact before deletion. `CellID` and
the 9-cell matrix are unaffected as types — only the enums `CellID` composes
move to `harness-core`. The `harness-core` import is shared-substrate, not an
outbound CXA edge (OD→IS/AS/CP cross-axis edge count unchanged).
"""

from __future__ import annotations

from enum import StrEnum

from harness_core import DeploymentSurface, PersonaTier
from pydantic import BaseModel, ConfigDict

__all__ = [
    "ACTIVE_CELLS",
    "EXCLUDED_CELL",
    "EXCLUDED_CELL_RATIONALE",
    "CellBindingViolation",
    "CellID",
    "CellStatus",
    "DeploymentSurface",
    "PersonaTier",
    "cell_status",
    "reject_excluded_cell",
]


class CellStatus(StrEnum):
    """Status of a matrix cell (C-OD-01 §1.1 / §1.4)."""

    ACTIVE = "ACTIVE"
    EXCLUDED = "EXCLUDED"


class CellID(BaseModel):
    """A matrix cell — the `PersonaTier x DeploymentSurface` product key.

    Frozen → `Eq` + `Hash` over its two fields, stable under serialization
    (acceptance #9 / #12). The canonical key for all downstream per-cell
    bindings (acceptance #8).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    persona_tier: PersonaTier
    deployment_surface: DeploymentSurface

    def __hash__(self) -> int:
        # `frozen=True` already yields a hash; declared explicitly so the
        # static checker treats `CellID` as hashable where it keys sets/maps.
        return hash((self.persona_tier, self.deployment_surface))


class CellBindingViolation(Exception):  # noqa: N818 — name is the U-OD-01 plan signature verbatim (no spec extension)
    """Raised when a deployment-binding attempt targets the EXCLUDED cell.

    The Python materialization of the `Result<(), CellBindingViolation>` error
    arm in the U-OD-01 `reject_excluded_cell` signature — stack is Pydantic v2
    + stdlib, no `Result` framework pull (CLAUDE.md §3.2 / I-6).
    """


# --- Matrix population (C-OD-01 §1.1 / §1.3 / §1.4) -------------------------

#: The structurally-excluded cell (C-OD-01 §1.4).
EXCLUDED_CELL: CellID = CellID(
    persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
    deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
)

#: The 8 active cells — the 3x3 product minus `EXCLUDED_CELL` (C-OD-01 §1.3).
ACTIVE_CELLS: frozenset[CellID] = frozenset(
    CellID(persona_tier=pt, deployment_surface=ds)
    for pt in PersonaTier
    for ds in DeploymentSurface
    if not (
        pt is PersonaTier.MULTI_TENANT_COMPLIANCE
        and ds is DeploymentSurface.LOCAL_DEVELOPMENT
    )
)

#: EXCLUDED-cell rationale per C-OD-01 §1.4 (acceptance #7 verbatim).
EXCLUDED_CELL_RATIONALE: str = (
    "compliance-readiness foundational primitives (tenant isolation, "
    "encryption-at-rest with vendor-managed key custody, retention controls) "
    "are incompatible with single-developer-machine deployment"
)


def cell_status(cell: CellID) -> CellStatus:
    """Return the status of `cell` (C-OD-01 §1.1 / §1.4).

    `EXCLUDED` for the `multi-tenant-compliance x local-development` cell;
    `ACTIVE` for all other 8 cells.
    """
    return CellStatus.EXCLUDED if cell == EXCLUDED_CELL else CellStatus.ACTIVE


def reject_excluded_cell(cell: CellID) -> None:
    """Structurally reject a deployment-binding attempt on the EXCLUDED cell.

    Returns `None` (the `Ok(())` arm) for any ACTIVE cell; raises
    `CellBindingViolation` (the `Err` arm) for the EXCLUDED cell — C-OD-01
    §1.5 excluded-cell binding rejection.
    """
    if cell == EXCLUDED_CELL:
        raise CellBindingViolation(
            f"deployment-binding rejected: {cell.persona_tier} x "
            f"{cell.deployment_surface} is structurally excluded (C-OD-01 §1.4)"
        )
    return None
