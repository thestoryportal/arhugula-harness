"""U-RT-138 — composition-root adapter: the real U-OD-55 verifier behind the
CP-owned `AuditWalkVerifier` Protocol (CP plan v2.38 §3 row 1's runtime-owned
mediation half; Runtime plan v2.49 §1.5 CP-WALK ADAPTER criterion).

`harness-cp` cannot import `harness-od` (the OD→CP canonical direction plus
the `SigningBackend` import cycle), so the §20.3.1 blocking walk takes its
per-entry verification mechanics as an injected batch verifier. THIS module
is the composition root's side of that seam — `harness-runtime` imports both
packages, wraps `harness_od.per_family_audit_verification.
verify_per_family_chains` (OD v1.34 §21.2.2) in the CP result boundary, and
injects it wherever the walk is invoked (the `harness-inspect` §13.5 wiring
is the first production injection site).

The taxonomy mapping (CP plan v2.38 §3, codex rounds 3/4/27/45):

- OD `AuditSignatureInvalid`   → CP invalid signal, `SIGNATURE_INVALID`.
- OD `HashChainBreach`         → CP invalid signal, `HASH_CHAIN_BREACH`
  (content/linkage tampering is an audit-FAIL routed to §4.1.28 escalation,
  never an internal error).
- OD `AuditVerificationBackendUnavailableError` /
  `VerificationBackendKeyUnknownError` (taxonomy branch (b)) →
  `AuditWalkVerifierUnavailableError` — availability is never a verdict.
- ANY OTHER raise propagates UNWRAPPED as a defect, never misclassified as
  rerunnable infrastructure.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import cast

from harness_cp.audit_walk_verification import (
    AuditWalkVerifierUnavailableError,
    WalkInvalidDiscriminator,
    WalkInvalidSignal,
    WalkVerificationOutcome,
)
from harness_od.audit_cutover_record import AuditCutoverRecord
from harness_od.audit_ledger_types import AuditLedgerEntry
from harness_od.multi_tenant_trace_separation_and_audit_ledger import HashChainBreach
from harness_od.per_family_audit_verification import (
    AuditSignatureInvalid,
    AuditVerificationBackendUnavailableError,
    BackendResolver,
    VerificationBackendKeyUnknownError,
    verify_per_family_chains,
)

__all__ = ["OdVerifierWalkAdapter"]


@dataclass(frozen=True, slots=True)
class OdVerifierWalkAdapter:
    """`AuditWalkVerifier` Protocol conformer over the real U-OD-55 verifier.

    All record-trust inputs are captured at construction (the composition
    root resolves them from the operator's §13.5 inputs); the walk supplies
    the entry batch + tenant scope + observed identities per invocation.
    """

    backend_resolver: BackendResolver
    cutover_record: AuditCutoverRecord | None = None
    cutover_record_signature: bytes | None = None
    expected_cutover_record_key_id: str | None = None
    ledger_binding_id: str | None = None

    def verify(
        self,
        audit_entries: Sequence[object],
        *,
        tenant_scope: str | None,
        observed_baseline_identities: Sequence[tuple[str, str]],
    ) -> WalkVerificationOutcome:
        entries = cast("Sequence[AuditLedgerEntry]", audit_entries)
        try:
            report = verify_per_family_chains(
                entries,
                tenant_scope=tenant_scope,
                backend_resolver=self.backend_resolver,
                cutover_record=self.cutover_record,
                cutover_record_signature=self.cutover_record_signature,
                expected_cutover_record_key_id=self.expected_cutover_record_key_id,
                ledger_binding_id=self.ledger_binding_id,
                observed_baseline_identities=observed_baseline_identities,
            )
        except AuditSignatureInvalid as exc:
            return WalkVerificationOutcome(
                invalid=WalkInvalidSignal(
                    discriminator=WalkInvalidDiscriminator.SIGNATURE_INVALID,
                    reason=str(exc),
                )
            )
        except HashChainBreach as exc:
            return WalkVerificationOutcome(
                invalid=WalkInvalidSignal(
                    discriminator=WalkInvalidDiscriminator.HASH_CHAIN_BREACH,
                    reason=str(exc),
                )
            )
        except (
            AuditVerificationBackendUnavailableError,
            VerificationBackendKeyUnknownError,
        ) as exc:
            raise AuditWalkVerifierUnavailableError(str(exc)) from exc
        # Any other raise (TypeError/KeyError/programming error) propagates
        # unwrapped as a defect — the CP result-boundary contract.

        return WalkVerificationOutcome(
            signature_dispositions=dict(report.signature_dispositions),
            baseline_divergences=tuple(report.baseline_divergences),
        )
