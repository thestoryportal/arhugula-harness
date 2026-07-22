"""B-58 — validator-escalation gate-error carriers re-homed to harness-core.

The three `ValidatorEscalationGate*Error` carriers moved here from
`harness_runtime.lifecycle.validator_escalation_composer` per the U-CORE-03
precedent (cross-axis exception types consumed by `harness_cp.workflow_driver`'s
escalation arms must not require a CP→runtime function-level import). The
cross-package identity half lives runtime-side (needs sibling packages
installed; mirror of the U-CORE-03 split noted at `test_u_core_03.py`).
"""

from __future__ import annotations

import pytest
from harness_core import (
    ValidatorEscalationGateAuditComposeError,
    ValidatorEscalationGateRejectedError,
    ValidatorEscalationGateTimeoutError,
)


def test_carriers_are_plain_exception_subclasses() -> None:
    """Verbatim re-home: same bases as the pre-B-58 runtime definitions —
    plain `Exception` subclasses, no added state."""
    for cls in (
        ValidatorEscalationGateAuditComposeError,
        ValidatorEscalationGateRejectedError,
        ValidatorEscalationGateTimeoutError,
    ):
        assert cls.__mro__[1] is Exception


def test_direct_import_matches_package_export() -> None:
    """The package-level re-export is the same object as the direct
    carrier-module import (no shadowing/copy) — the U-CORE-03 AC #2 shape."""
    from harness_core.validator_escalation_errors import (
        ValidatorEscalationGateRejectedError as DirectImport,
    )

    assert DirectImport is ValidatorEscalationGateRejectedError


def test_carriers_raise_and_catch_by_type() -> None:
    with pytest.raises(ValidatorEscalationGateTimeoutError):
        raise ValidatorEscalationGateTimeoutError("gate timed out (test)")
