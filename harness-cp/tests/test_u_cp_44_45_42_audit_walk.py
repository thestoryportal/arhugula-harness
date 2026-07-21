"""`U-CP-44`/`U-CP-45`/`U-CP-42` (v2.38 amendments) — §20.3.1 blocking
audit-walk + §20.1.1 disposition-gated historical exception.

Implements CP plan v2.38 §3 witnesses (walk-blocking) + §4 witnesses
(historical-exception bounded-set) per CP spec v1.101 §3 + §4, with a
test-local FAKE batch verifier driving the CP-owned result boundary — the
real U-OD-55 verifier through the runtime composition-root adapter is
witnessed runtime-side (`test_rt138_adapter_real_od_verifier_through_walk`,
the co-land pin's other half).
"""

from __future__ import annotations

from collections.abc import Sequence

import pytest
from harness_cp.audit_walk_verification import (
    AuditWalkVerifierUnavailableError,
    WalkEntryVerdict,
    WalkEntryVerdictKind,
    WalkInvalidDiscriminator,
    WalkInvalidSignal,
    WalkResultKind,
    WalkVerificationOutcome,
    run_blocking_audit_walk,
)

_ENTRIES: tuple[object, ...] = (object(), object())


class _FakeVerifier:
    """Test-local batch verifier returning a canned outcome (or raising)."""

    def __init__(
        self,
        outcome: WalkVerificationOutcome | None = None,
        raise_exc: BaseException | None = None,
    ) -> None:
        self.outcome = outcome
        self.raise_exc = raise_exc
        self.calls: list[dict[str, object]] = []

    def verify(
        self,
        audit_entries: Sequence[object],
        *,
        tenant_scope: str | None,
        observed_baseline_identities: Sequence[tuple[str, str]],
    ) -> WalkVerificationOutcome:
        self.calls.append(
            {
                "entries": tuple(audit_entries),
                "tenant_scope": tenant_scope,
                "observed": tuple(observed_baseline_identities),
            }
        )
        if self.raise_exc is not None:
            raise self.raise_exc
        assert self.outcome is not None
        return self.outcome


# ---------------------------------------------------------------------------
# §3 row 1b — verifier REQUIRED at the walk (never a hash-only pass).
# ---------------------------------------------------------------------------


def test_walk_without_verifier_reports_incomplete_never_pass() -> None:
    """§3 row 1b: the walk invoked WITHOUT a verifier returns an EXPLICIT
    INCOMPLETE/UNVERIFIED result — never a passing audit (a pass over
    unchecked mutable signature metadata is the fabricate-VERIFIED failure
    the preserved v1.98 disposition rejects). Not rerunnable-as-is (the
    injection is missing, not the infrastructure).

    Mutation probe: defaulting the no-verifier branch to PASSED (the
    hash-only pass) FAILS both assertions."""
    result = run_blocking_audit_walk(_ENTRIES, verifier=None)
    assert result.kind is WalkResultKind.INCOMPLETE_UNVERIFIED
    assert result.kind is not WalkResultKind.PASSED
    assert result.rerunnable is False
    assert "fabricate" in result.detail


def test_walk_verifier_injected_no_od_import() -> None:
    """§3 row 1 (mediation): the `harness-cp` package graph contains no
    `harness_od` import — the Protocol + result boundary are CP-OWNED, and
    the injected fake verifier's CP-boundary outcomes drive walk verdicts.

    Mutation probe: adding a `harness_od` import anywhere under
    `harness_cp` fails the package-graph scan."""
    import pathlib

    import harness_cp

    pkg_root = pathlib.Path(next(iter(harness_cp.__path__)))
    offenders: list[str] = []
    for py in pkg_root.rglob("*.py"):
        text = py.read_text(encoding="utf-8")
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith(("import harness_od", "from harness_od")):
                offenders.append(f"{py.name}: {stripped}")
    assert offenders == [], f"harness-cp must never import harness-od: {offenders}"

    # The injected fake's CP-boundary outcome drives the walk verdict.
    verifier = _FakeVerifier(
        outcome=WalkVerificationOutcome(signature_dispositions={"verified": 2})
    )
    result = run_blocking_audit_walk(
        _ENTRIES, verifier=verifier, tenant_scope="tenant-a", observed_baseline_identities=()
    )
    assert result.kind is WalkResultKind.PASSED
    assert verifier.calls[0]["tenant_scope"] == "tenant-a"  # RAW passthrough


# ---------------------------------------------------------------------------
# §3 rows 4-5 — witness (c): walk-blocking.
# ---------------------------------------------------------------------------


def test_walk_audit_signature_invalid_fails_audit_as_hash_chain_breach_does() -> None:
    """§3 row 4: an invalid-signature verdict FAILS the audit exactly as a
    hash-chain breach does, with the typed discriminator PRESERVED through
    the failure report (`SIGNATURE_INVALID` ≠ `HASH_CHAIN_BREACH` — the
    operator sees WHICH trust property failed; both are audit-FAIL).

    Mutation probe: collapsing the two discriminators onto one value (or
    mapping invalid to INCOMPLETE) fails the pairwise assertions."""
    sig_result = run_blocking_audit_walk(
        _ENTRIES,
        verifier=_FakeVerifier(
            outcome=WalkVerificationOutcome(
                invalid=WalkInvalidSignal(
                    discriminator=WalkInvalidDiscriminator.SIGNATURE_INVALID,
                    reason="signature does not match the reconstructed canonical message",
                )
            )
        ),
    )
    chain_result = run_blocking_audit_walk(
        _ENTRIES,
        verifier=_FakeVerifier(
            outcome=WalkVerificationOutcome(
                invalid=WalkInvalidSignal(
                    discriminator=WalkInvalidDiscriminator.HASH_CHAIN_BREACH,
                    reason="prior_entry_hash does not link to the predecessor",
                )
            )
        ),
    )
    assert sig_result.kind is WalkResultKind.FAILED
    assert chain_result.kind is WalkResultKind.FAILED
    assert sig_result.failure_discriminator is WalkInvalidDiscriminator.SIGNATURE_INVALID
    assert chain_result.failure_discriminator is WalkInvalidDiscriminator.HASH_CHAIN_BREACH
    assert sig_result.failure_discriminator != chain_result.failure_discriminator
    assert "§4.1.28" in sig_result.detail  # recovery routing preserved


def test_walk_availability_error_is_incomplete_not_pass_not_tamper_and_rerun_completes() -> None:
    """§3 row 5: a backend availability error (incl. unknown key_id) is NOT
    a verdict — the run is INCOMPLETE (neither passed nor failed-as-
    tampered) and RERUNNABLE; a re-run after availability is restored
    completes the walk. A non-availability raise from the injected callable
    PROPAGATES UNWRAPPED as a defect.

    Mutation probe: mapping availability to FAILED (tamper) or PASSED, or
    swallowing the defect raise into INCOMPLETE, fails the arms."""
    unavailable = _FakeVerifier(
        raise_exc=AuditWalkVerifierUnavailableError("kms unreachable (test)")
    )
    result = run_blocking_audit_walk(_ENTRIES, verifier=unavailable)
    assert result.kind is WalkResultKind.INCOMPLETE_UNVERIFIED
    assert result.failure_discriminator is None
    assert result.rerunnable is True

    # Re-run after restoration completes the walk.
    restored = _FakeVerifier(
        outcome=WalkVerificationOutcome(signature_dispositions={"verified": 2})
    )
    rerun = run_blocking_audit_walk(_ENTRIES, verifier=restored)
    assert rerun.kind is WalkResultKind.PASSED

    # Defect raises propagate unwrapped — never rerunnable infrastructure.
    defect = _FakeVerifier(raise_exc=TypeError("programming error (test)"))
    with pytest.raises(TypeError, match="programming error"):
        run_blocking_audit_walk(_ENTRIES, verifier=defect)


# ---------------------------------------------------------------------------
# §4 rows 1-3 — witness (d): historical-exception bounded-set (U-CP-42).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("disposition", "expected_kind"),
    [
        ("placeholder_exempt", WalkResultKind.PASSED),
        ("four_tuple_real_broken", WalkResultKind.FAILED),
        ("quarantined", WalkResultKind.FAILED),
    ],
)
def test_exception_gates_on_disposition(disposition: str, expected_kind: WalkResultKind) -> None:
    """§4 rows 1-2 (disposition-gated): record MEMBERSHIP alone never
    satisfies §20.1 row 3 — the attested DISPOSITION gates. A
    `placeholder_exempt` row passes WITHOUT a verifiable signature (the
    exception proper); a `four_tuple_real` row is an era marker and still
    cryptographically verifies inside the verifier (a broken one surfaces
    as the invalid signal and FAILS); a `quarantined` row NEVER passes.

    Mutation probe: collapsing to membership-only (treating every recorded
    row as exempt) passes the quarantined case and fails this test."""
    if disposition == "placeholder_exempt":
        outcome = WalkVerificationOutcome(
            entry_verdicts=(
                WalkEntryVerdict(
                    entry_ref="row-1",
                    kind=WalkEntryVerdictKind.EXEMPT_PLACEHOLDER,
                    reason="recorded placeholder_exempt disposition",
                ),
            ),
            signature_dispositions={"verified": 1, "exempt": 1},
        )
    elif disposition == "four_tuple_real_broken":
        # The verifier itself verified the four-tuple era row and found the
        # signature broken — the invalid signal, not an exemption.
        outcome = WalkVerificationOutcome(
            invalid=WalkInvalidSignal(
                discriminator=WalkInvalidDiscriminator.SIGNATURE_INVALID,
                reason="four_tuple_real era row failed cryptographic verification",
            )
        )
    else:
        outcome = WalkVerificationOutcome(
            entry_verdicts=(
                WalkEntryVerdict(
                    entry_ref="row-1",
                    kind=WalkEntryVerdictKind.QUARANTINED,
                    reason="recorded quarantined disposition",
                ),
            ),
            signature_dispositions={"verified": 1, "quarantined": 1},
        )
    result = run_blocking_audit_walk(_ENTRIES, verifier=_FakeVerifier(outcome=outcome))
    assert result.kind is expected_kind
    if disposition == "quarantined":
        assert result.quarantined_entries, "quarantined rows must be reported explicitly"


def test_row_absent_from_cutover_record_not_exempted_including_unsigned_shaped_value() -> None:
    """§4 row 3 (CP result boundary): an entry the record does NOT exempt
    fails when the verifier reports it invalid — the walk never invents an
    exemption of its own. (The `unsigned:*`-VALUE-shape half of row 3 —
    membership decided by the record, never by signature-value shape — is
    enforced INSIDE the OD verifier and witnessed there; the CP walk holds
    no signature-shape logic at all, which the module's import surface and
    this file's no-OD-import scan pin structurally.)"""
    result = run_blocking_audit_walk(
        _ENTRIES,
        verifier=_FakeVerifier(
            outcome=WalkVerificationOutcome(
                invalid=WalkInvalidSignal(
                    discriminator=WalkInvalidDiscriminator.SIGNATURE_INVALID,
                    reason=(
                        "row carries unsigned:key-1:... shaped value but is "
                        "ABSENT from the authenticated cutover record"
                    ),
                )
            )
        ),
    )
    assert result.kind is WalkResultKind.FAILED
    assert result.failure_discriminator is WalkInvalidDiscriminator.SIGNATURE_INVALID


def test_exempted_row_reported_explicitly_never_silent() -> None:
    """§4 rows 4-5 + §3 row 6: exempt rows are REPORTED explicitly with
    their recorded disposition, never silently passed — the PASSED result
    carries the exemption section and the disposition counts.

    Mutation probe: dropping the exempt section from the PASSED result (a
    silent pass) fails the report assertions."""
    result = run_blocking_audit_walk(
        _ENTRIES,
        verifier=_FakeVerifier(
            outcome=WalkVerificationOutcome(
                entry_verdicts=(
                    WalkEntryVerdict(
                        entry_ref="row-legacy-1",
                        kind=WalkEntryVerdictKind.EXEMPT_PLACEHOLDER,
                        reason="recorded placeholder_exempt disposition",
                    ),
                ),
                signature_dispositions={"verified": 1, "exempt": 1},
            )
        ),
    )
    assert result.kind is WalkResultKind.PASSED
    assert len(result.exempt_entries) == 1
    assert result.exempt_entries[0].entry_ref == "row-legacy-1"
    assert result.signature_dispositions.get("exempt") == 1
    assert "reported explicitly" in result.detail


def test_walk_baseline_divergence_fails_explicitly() -> None:
    """§3 row 6: a legacy-baseline cross-check mismatch (either direction)
    between the authenticated cutover record and the observed set FAILS the
    walk with the divergences reported — never silently omitted."""
    result = run_blocking_audit_walk(
        _ENTRIES,
        verifier=_FakeVerifier(
            outcome=WalkVerificationOutcome(
                signature_dispositions={"verified": 2},
                baseline_divergences=(
                    "recorded baseline identity ('_single', 'ab'*32) not observed",
                ),
            )
        ),
    )
    assert result.kind is WalkResultKind.FAILED
    assert result.baseline_divergences


def test_invalid_entry_verdict_fails_walk_without_invalid_signal() -> None:
    """Codex round-5 (U-RT-138 leg): a verifier returning a type-valid
    `WalkEntryVerdict(kind=INVALID)` WITHOUT also populating
    `outcome.invalid` must still FAIL the walk — the public outcome type
    admits that state, so the walk gates it explicitly rather than falling
    through to PASSED.

    Mutation probe: dropping the invalid-verdict gate lets this outcome
    reach the final PASSED branch → FAILS."""

    class _InvalidVerdictVerifier:
        def verify(
            self,
            audit_entries: Sequence[object],
            *,
            tenant_scope: str | None,
            observed_baseline_identities: Sequence[tuple[str, str]],
        ) -> WalkVerificationOutcome:
            del audit_entries, tenant_scope, observed_baseline_identities
            return WalkVerificationOutcome(
                entry_verdicts=(
                    WalkEntryVerdict(
                        entry_ref="entry-0",
                        kind=WalkEntryVerdictKind.INVALID,
                        reason="signature mismatch (verifier-reported)",
                    ),
                ),
                signature_dispositions={"verified": 0},
            )

    result = run_blocking_audit_walk([object()], verifier=_InvalidVerdictVerifier())
    assert result.kind is WalkResultKind.FAILED
    assert result.failure_discriminator is WalkInvalidDiscriminator.SIGNATURE_INVALID
    assert "INVALID entry verdict" in result.detail


def test_baseline_divergence_failure_has_no_row4_discriminator() -> None:
    """Codex round-6 (U-RT-138 leg): a baseline-divergence failure is a
    row-6 completeness failure — signatures and hash chains are VALID, so
    the row-4 `SIGNATURE_INVALID` discriminator must not be attached.

    Mutation probe: restoring `SIGNATURE_INVALID` on that branch → FAILS."""

    class _DivergenceVerifier:
        def verify(
            self,
            audit_entries: Sequence[object],
            *,
            tenant_scope: str | None,
            observed_baseline_identities: Sequence[tuple[str, str]],
        ) -> WalkVerificationOutcome:
            del audit_entries, tenant_scope, observed_baseline_identities
            return WalkVerificationOutcome(
                baseline_divergences=("recorded identity missing from observed baseline",),
            )

    result = run_blocking_audit_walk([], verifier=_DivergenceVerifier())
    assert result.kind is WalkResultKind.FAILED
    assert result.failure_discriminator is None
    assert "legacy-baseline divergence" in result.detail
