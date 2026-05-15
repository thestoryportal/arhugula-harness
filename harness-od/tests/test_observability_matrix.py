"""Tests for U-OD-01 — 9-cell observability matrix (C-OD-01).

Test set per the U-OD-01 `Tests:` field — 12 tests covering acceptance #1-#12.
"""

from __future__ import annotations

import pytest
from harness_od.observability_matrix import (
    ACTIVE_CELLS,
    EXCLUDED_CELL,
    EXCLUDED_CELL_RATIONALE,
    CellBindingViolation,
    CellID,
    CellStatus,
    DeploymentSurface,
    PersonaTier,
    cell_status,
    reject_excluded_cell,
)

# Verbatim from C-OD-01 §1.1.
_SPEC_PERSONA_TIERS = {"solo-developer", "team-binding", "multi-tenant-compliance"}
_SPEC_DEPLOYMENT_SURFACES = {"local-development", "self-hosted-server", "managed-cloud"}

# Acceptance #7 — EXCLUDED rationale per §1.4, byte-exact.
_SPEC_RATIONALE = (
    "compliance-readiness foundational primitives (tenant isolation, "
    "encryption-at-rest with vendor-managed key custody, retention controls) "
    "are incompatible with single-developer-machine deployment"
)


def test_persona_tier_cardinality_three() -> None:
    """Acceptance #1 — PersonaTier has 3 values matching §1.1 verbatim."""
    assert len(PersonaTier) == 3
    assert {t.value for t in PersonaTier} == _SPEC_PERSONA_TIERS


def test_deployment_surface_cardinality_three() -> None:
    """Acceptance #2 — DeploymentSurface has 3 values matching §1.1 verbatim."""
    assert len(DeploymentSurface) == 3
    assert {s.value for s in DeploymentSurface} == _SPEC_DEPLOYMENT_SURFACES


def test_cell_id_product_nine() -> None:
    """Acceptance #3 — CellID is the PersonaTier x DeploymentSurface 9-cell product."""
    cells = {
        CellID(persona_tier=pt, deployment_surface=ds)
        for pt in PersonaTier
        for ds in DeploymentSurface
    }
    assert len(cells) == 9


def test_active_cells_cardinality_eight() -> None:
    """Acceptance #4 — ACTIVE_CELLS has cardinality 8."""
    assert len(ACTIVE_CELLS) == 8


def test_excluded_cell_byte_exact() -> None:
    """Acceptance #4 — EXCLUDED_CELL is (MULTI_TENANT_COMPLIANCE, LOCAL_DEVELOPMENT)."""
    assert EXCLUDED_CELL == CellID(
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
    )
    assert EXCLUDED_CELL not in ACTIVE_CELLS


def test_cell_status_excluded() -> None:
    """Acceptance #5 — the excluded cell reports EXCLUDED."""
    assert cell_status(EXCLUDED_CELL) is CellStatus.EXCLUDED


def test_cell_status_active_others() -> None:
    """Acceptance #5 — all 8 other cells report ACTIVE."""
    for cell in ACTIVE_CELLS:
        assert cell_status(cell) is CellStatus.ACTIVE


def test_reject_excluded_cell_returns_err() -> None:
    """Acceptance #6 — reject_excluded_cell raises for the EXCLUDED cell."""
    with pytest.raises(CellBindingViolation):
        reject_excluded_cell(EXCLUDED_CELL)


def test_reject_active_cell_returns_ok() -> None:
    """Acceptance #6 — reject_excluded_cell returns None for any ACTIVE cell."""
    for cell in ACTIVE_CELLS:
        assert reject_excluded_cell(cell) is None


def test_cell_id_eq_and_hash_stable() -> None:
    """Acceptance #9 — CellID is Eq + Hash over its two fields."""
    a = CellID(
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        deployment_surface=DeploymentSurface.MANAGED_CLOUD,
    )
    b = CellID(
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        deployment_surface=DeploymentSurface.MANAGED_CLOUD,
    )
    assert a == b
    assert hash(a) == hash(b)
    assert len({a, b}) == 1


def test_excluded_rationale_byte_exact() -> None:
    """Acceptance #7 — EXCLUDED rationale matches §1.4 (acceptance #7) verbatim."""
    assert EXCLUDED_CELL_RATIONALE == _SPEC_RATIONALE


def test_cell_id_serialization_round_trip() -> None:
    """Acceptance #9 — CellID is stable under serialization."""
    cell = CellID(
        persona_tier=PersonaTier.TEAM_BINDING,
        deployment_surface=DeploymentSurface.SELF_HOSTED_SERVER,
    )
    assert CellID.model_validate_json(cell.model_dump_json()) == cell
