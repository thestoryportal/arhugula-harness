"""Rotation-correlation window read-side invariants — U-IS-20 (C-IS-07 §7.7).

Declares `verify_rotation_window` — the single public composed validator over
a claimed rotation window (a caller-derived `Sequence[StateLedgerEntry]`),
sequencing non-emptiness → presence → uniqueness and returning one typed
result naming which invariant failed, if any.

**Why one composed function, not three independently-callable helpers**
(spec §7.7; IS plan v2.8 U-IS-20 AC #5). Presence and uniqueness are both
universally-quantified checks over a window's entries and therefore pass
vacuously on an empty sequence. A caller invoking only a presence-or-
uniqueness sub-check directly against `[]`, bypassing a non-emptiness guard,
would recreate the exact vacuous-pass defect this delta exists to prevent
(round-5 out-of-family Codex finding cited at the plan). Non-emptiness,
presence, and uniqueness are therefore internal stages of one public
function, not separately public helpers a caller could compose incorrectly.

**Scope boundary (spec §7.7 join-key note).** This validator operates purely
against the IS chain — no OD ledger, no signing backend. It is the IS-side
evidence a CP-owned consumer (`verify_rotation_6_steps`'s extension) composes
with OD-anchored window-boundary authentication at the separate CP-axis impl
leg; it is NOT the authentication itself, and passing this check alone does
not constitute a verified rotation boundary (see the spec's own "JOIN KEY,
not a trust anchor" framing).

Authority: Implementation_Plan_Information_Substrate_v2_8.md §2.2 U-IS-20
(acceptance #5-#8); Spec_Information_Substrate_v1.md C-IS-07 §7.7.
"""

from __future__ import annotations

from collections.abc import Sequence
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from harness_is.state_ledger_entry_schema import StateLedgerEntry


class RotationWindowCheckStatus(StrEnum):
    """Overall outcome of a `verify_rotation_window` check (C-IS-07 §7.7)."""

    VALID = "valid"
    INVALID = "invalid"


class RotationWindowFailureType(StrEnum):
    """Which §7.7 invariant failed (C-IS-07 §7.7 (a)/(b)/(c))."""

    EMPTY_WINDOW = "empty_window"
    PRESENCE_FAILURE = "presence_failure"
    UNIQUENESS_FAILURE = "uniqueness_failure"


class RotationWindowCheckResult(BaseModel):
    """The result of a `verify_rotation_window` inspection (C-IS-07 §7.7)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    status: RotationWindowCheckStatus
    failure_type: RotationWindowFailureType | None


def verify_rotation_window(
    window: Sequence[StateLedgerEntry],
) -> RotationWindowCheckResult:
    """Verify a claimed rotation window's IS-side invariants (C-IS-07 §7.7).

    `window` is a caller-derived sub-sequence of entries asserted to belong to
    one rotation event — NOT the full genesis-anchored chain `verify_chain`
    requires, and its boundaries must be derived independently of
    `rotation_correlation_id` itself (a CP-owned, OD-anchored concern out of
    this function's scope; see the module docstring).

    Sequenced non-emptiness (c) → presence (a) → uniqueness (b), per AC #6/#7/#8:

    (c) An empty `window` fails at `EMPTY_WINDOW` before any per-entry
        predicate runs — an empty claimed window is an absence of evidence,
        not a vacuous pass.
    (a) Given a non-empty `window`, fails at `PRESENCE_FAILURE` if any entry
        carries `rotation_correlation_id = None`.
    (b) Given a `window` that passed presence, fails at `UNIQUENESS_FAILURE`
        if the set of non-`None` `rotation_correlation_id` values has
        cardinality ≥ 2 (a torn/mixed window).

    Returns `VALID` (with `failure_type=None`) only when all three pass.
    """
    if not window:
        return RotationWindowCheckResult(
            status=RotationWindowCheckStatus.INVALID,
            failure_type=RotationWindowFailureType.EMPTY_WINDOW,
        )
    if any(entry.rotation_correlation_id is None for entry in window):
        return RotationWindowCheckResult(
            status=RotationWindowCheckStatus.INVALID,
            failure_type=RotationWindowFailureType.PRESENCE_FAILURE,
        )
    distinct_ids = {entry.rotation_correlation_id for entry in window}
    if len(distinct_ids) >= 2:
        return RotationWindowCheckResult(
            status=RotationWindowCheckStatus.INVALID,
            failure_type=RotationWindowFailureType.UNIQUENESS_FAILURE,
        )
    return RotationWindowCheckResult(
        status=RotationWindowCheckStatus.VALID,
        failure_type=None,
    )
