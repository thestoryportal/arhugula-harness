"""Per-family audit verification — `B-49` (split from the B-47 close-out),
extended by `U-OD-55` with the backend-aware signature-verification API
(OD spec v1.34 §21.2.2, closing v1.33's explicit verification out-of-scope).

A tenant's persisted audit entries interleave INDEPENDENT producer families,
and most families do not chain at all: cost projection, HITL gate audits, and
sub-agent dispatch deliberately emit constant non-chained `prior_entry_hash`
values on every entry (zero-hash genesis for cost/dispatch; `sha256(b"")` for
HITL — constant either way, never a predecessor link), so running
`verify_hash_chain_integrity` over a raw per-tenant sequence — or even over a
naive per-prefix partition — reports false tampering on the second untouched
entry.

Producer-aware policy (per `.harness/b-47-pr-b2-design-disposition-v1.md`,
codex rounds 3/5/7/9 of that leg):

- **Every entry, every family**: per-entry CONTENT-HASH verification
  (`compute_entry_hash(payload) == entry_hash`) — a payload mutated in place
  with its stored hash left untouched is caught regardless of family.
- **Chain verification ONLY for the redaction-token family** — the one
  producer with real chain-position wiring today
  (`AuditLedgerRedactionTokenMap` seeds `prior_entry_hash` from its durable
  tail). The family is discriminated by the `audit.redaction_token.*`
  NAMESPACE KEYS the composer stamps on every redaction row — NOT by
  `entry_core` prefix, which misses rows composed with a caller-supplied
  `entry_core` (the map's own `_seed_chain_from_durable_tail` documents this;
  PR B1 codex round-39).
- **Backend signature verification is OPTIONAL** (`U-OD-55`, OD spec v1.34
  §21.2.2) — an absent `backend_resolver` PRESERVES the B-49 hash/chain-only
  behavior VERBATIM; a present resolver additionally verifies every entry's
  `signature_attrs` against the reconstructed canonical message, applying
  the message-format cutover + legacy-exemption rules an authenticated
  `AuditCutoverRecord` (`harness_od.audit_cutover_record`) carries.

Raises `HashChainBreach` (the existing U-OD-30 error arm) on content/linkage
tampering; raises the NEW `AuditSignatureInvalid` on a signature that fails
backend verification or is malformed; raises the NEW
`AuditVerificationBackendUnavailableError` when a resolver cannot supply a
backend for a `(algorithm, key_id)` pair (an infrastructure/availability gap,
never a verdict). Returns a frozen per-family + per-signature report on
success.
"""

from __future__ import annotations

import base64
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType

from harness_cp.f5_signing_key_resolution import SIGNATURE_LENGTH_BY_ALGORITHM, SigningBackend

from harness_od.audit_cutover_record import (
    AuditCutoverRecord,
    CutoverRecordValidationError,
    VerificationDisposition,
)
from harness_od.audit_ledger_types import (
    AuditLedgerEntry,
    SignatureAlgorithm,
    compute_entry_hash,
)
from harness_od.multi_tenant_trace_separation_and_audit_ledger import (
    HashChainBreach,
    canonical_od_signing_message,
    signing_token,
)

__all__ = [
    "REDACTION_TOKEN_FAMILY",
    "REDACTION_TOKEN_NAMESPACE_PREFIX",
    "AuditSignatureInvalid",
    "AuditVerificationBackendUnavailableError",
    "FamilyVerificationReport",
    "verify_per_family_chains",
]

REDACTION_TOKEN_NAMESPACE_PREFIX = "audit.redaction_token."
"""Namespace-key prefix the redaction-token composer stamps on every row —
the family discriminator (caller-supplied `entry_core` rows carry no
reliable `entry_core` prefix)."""

REDACTION_TOKEN_FAMILY = "redaction-token"
"""Report key for the one chain-verified family."""

#: The §21.2.1 `"DEPLOYMENT_BOUND"` fixed key-period token — the only value
#: this arc's verifier can reconstruct a message for (rotation-aware
#: key-period selection is `B-33` scope; OD spec v1.34 §21.2.2 row 1).
_DEPLOYMENT_BOUND_TOKEN = "DEPLOYMENT_BOUND"
_DEPLOYMENT_BOUND_KEY_PERIOD = 0


class AuditSignatureInvalid(Exception):  # noqa: N818 — mirrors HashChainBreach naming
    """Raised when a backend rejects an entry's signature, or the signature
    value is malformed against its declared algorithm's fixed width (OD spec
    v1.34 §21.2.2 row 7, branches (a) + (c)).

    Distinct from `HashChainBreach` (content/linkage tampering) — a row can
    have byte-perfect content and chain linkage yet carry a signature that
    was never produced over its canonical message (a different trust
    property). Callers key on the TYPE to distinguish "content tampered"
    from "signature invalid".
    """


class AuditVerificationBackendUnavailableError(Exception):
    """Raised when a `backend_resolver` cannot supply a verification backend
    for an entry's stored `(algorithm, key_id)` — including a `key_id`
    unknown to the resolver's mapping (OD spec v1.34 §21.2.2 row 7, branch
    (b)).

    An infrastructure/availability failure, retryable by the caller — NEVER
    a verdict on the entry's trustworthiness (an unresolvable key proves
    nothing about the signature it can't check). A `backend.verify` call
    that itself raises is also routed here (verify-side backend errors are
    caller-retryable per §21.2.2 row 9's breaker-asymmetry rationale — this
    module never breaker-couples the read path itself; see
    `test_verify_path_not_breaker_instrumented`). Raises that indicate a
    genuine PROGRAMMING defect (e.g. a resolver raising `TypeError`) are
    NOT wrapped here — they propagate unwrapped so a defect is never mistaken
    for a retryable outage.
    """


BackendResolver = Callable[[SignatureAlgorithm, str], SigningBackend]
"""Per-row verification-backend resolver keyed on an entry's STORED
`(audit_signature_algorithm, audit_signature_key_id)` — NOT a single
`SigningBackend | None` (OD spec v1.34 §21.2.2 row 1): one backend exposes
one `.algorithm` and cannot verify mixed multi-algorithm history."""


@dataclass(frozen=True, slots=True)
class FamilyVerificationReport:
    """Deeply immutable result of a successful `verify_per_family_chains` run.

    `chained` maps each CHAIN-VERIFIED family to its entry count;
    `per_entry` maps each content-hash-only family (keyed by `entry_core`
    prefix, or `"(unprefixed)"`) to its entry count. Counts exist so a
    caller can assert coverage — a verifier that silently classified every
    row into an empty family would otherwise look identical to success.

    `signature_dispositions` (NEW, U-OD-55) maps each signature-verification
    outcome — `"verified"` / `"exempt"` / `"quarantined"` — to its entry
    count; EMPTY when `backend_resolver` was absent (row 1: absent resolver
    preserves hash-only behavior verbatim — no signature bookkeeping at
    all, not a zero-filled dict, so a caller can distinguish "didn't check"
    from "checked, zero of a category"). `baseline_divergences` (NEW,
    U-OD-55) reports every legacy-baseline identity cross-check mismatch,
    BOTH directions (§21.2.2 row 6) — never silently omitted.

    The mappings are `MappingProxyType` views (codex round-1 on the B-49
    landing): a frozen carrier over MUTABLE dicts would still allow
    `report.chained[...] = ...` to alter verification evidence after the
    fact.
    """

    chained: Mapping[str, int]
    per_entry: Mapping[str, int]
    signature_dispositions: Mapping[str, int] = field(default_factory=dict[str, int])
    baseline_divergences: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        # The invariant belongs to the TYPE (codex round-2 on the B-49
        # landing): a direct constructor caller passing a mutable dict must
        # not retain a mutation handle into the report — copy then wrap.
        object.__setattr__(self, "chained", MappingProxyType(dict(self.chained)))
        object.__setattr__(self, "per_entry", MappingProxyType(dict(self.per_entry)))
        object.__setattr__(
            self, "signature_dispositions", MappingProxyType(dict(self.signature_dispositions))
        )


def _is_redaction_row(entry: AuditLedgerEntry) -> bool:
    return any(
        key.startswith(REDACTION_TOKEN_NAMESPACE_PREFIX)
        for key in entry.payload.audit_namespace_attrs
    )


def _per_entry_family_key(entry: AuditLedgerEntry) -> str:
    core = str(entry.payload.entry_core)
    prefix, sep, _rest = core.partition(":")
    return prefix if sep else "(unprefixed)"


def _resolve_cutover_disposition(
    entry: AuditLedgerEntry, cutover_record: AuditCutoverRecord | None, normalized_scope: str | None
) -> VerificationDisposition | None:
    """The cutover-record row governing `entry`, if any (OD spec v1.34
    §21.2.2 row 4 — the verifier compares each recorded scope against its
    row-2 tenant input). A cutover record only disposition rows for a REAL
    tenant scope (the untenanted/single-tenant case has no legacy-migration
    story to exempt); absent a match, the entry is treated as post-cutover
    per row 3.
    """
    if cutover_record is None or normalized_scope is None:
        return None
    for row in cutover_record.rows:
        if row.tenant_scope == normalized_scope and row.entry_hash == entry.entry_hash:
            return row.verification_disposition
    return None


def _verify_entry_signature(
    entry: AuditLedgerEntry,
    *,
    disposition: VerificationDisposition | None,
    normalized_scope: str | None,
    backend_resolver: BackendResolver,
) -> None:
    """Verify one entry's signature, raising the typed taxonomy on failure.

    `disposition is FOUR_TUPLE_REAL` selects the four-tuple (tenant-less)
    message shape regardless of the current `normalized_scope` — a genuine
    pre-v1.34 signature was produced over the four-tuple and reconstructing
    a five-tuple for it would fail honest history (§21.2.2 row 3). Absent a
    cutover-record match, the entry is POST-cutover and verifies against
    whatever `normalized_scope` implies (five-tuple under a real tenant;
    the preserved four-tuple under `None`) — era membership is NEVER
    inferred from the signature value itself.
    """
    sig_attrs = entry.signature_attrs
    algo = sig_attrs.audit_signature_algorithm
    expected_length = SIGNATURE_LENGTH_BY_ALGORITHM[algo.value]
    try:
        signature_bytes = base64.b64decode(sig_attrs.audit_signature_value, validate=True)
    except Exception as exc:
        raise AuditSignatureInvalid(
            f"entry entry_hash={entry.entry_hash!r} has an undecodable "
            "audit_signature_value (not valid base64) — malformed per OD "
            "spec v1.34 §21.2.2 row 7(c)"
        ) from exc
    if len(signature_bytes) != expected_length:
        raise AuditSignatureInvalid(
            f"entry entry_hash={entry.entry_hash!r} has a "
            f"{len(signature_bytes)}-byte signature; algorithm {algo.value!r} "
            f"requires exactly {expected_length} bytes (OD spec v1.34 "
            "§21.2.2 row 7(c) / C-CP-20 §20.4)"
        )
    if sig_attrs.audit_signature_key_period != _DEPLOYMENT_BOUND_TOKEN:
        raise AuditSignatureInvalid(
            f"entry entry_hash={entry.entry_hash!r} has audit_signature_"
            f"key_period={sig_attrs.audit_signature_key_period!r}; only "
            f"{_DEPLOYMENT_BOUND_TOKEN!r} is verifiable at this arc "
            "(rotation-aware key-period selection is B-33 scope)"
        )

    try:
        backend = backend_resolver(algo, sig_attrs.audit_signature_key_id)
    except KeyError as exc:
        raise AuditVerificationBackendUnavailableError(
            "no verification backend available for (algorithm="
            f"{algo.value!r}, key_id={sig_attrs.audit_signature_key_id!r}) "
            "— an unresolvable key_id at verify-time is an availability "
            "gap, not a verdict (OD spec v1.34 §21.2.2 row 7(b))"
        ) from exc

    tenant_tag_for_message = (
        None if disposition is VerificationDisposition.FOUR_TUPLE_REAL else normalized_scope
    )
    message = canonical_od_signing_message(
        entry.entry_hash,
        key_id=sig_attrs.audit_signature_key_id,
        algo_value=algo.value,
        key_period_token=_DEPLOYMENT_BOUND_TOKEN,
        tenant_tag=tenant_tag_for_message,
    )
    try:
        is_valid = backend.verify(
            message=message,
            signature=signature_bytes,
            key_id=sig_attrs.audit_signature_key_id,
            key_period=_DEPLOYMENT_BOUND_KEY_PERIOD,
        )
    except Exception as exc:
        raise AuditVerificationBackendUnavailableError(
            f"backend.verify raised {exc!r} while verifying entry "
            f"entry_hash={entry.entry_hash!r} — verify-side backend errors "
            "are caller-retryable infrastructure failures, never a verdict "
            "(OD spec v1.34 §21.2.2 row 7(b) / row 9)"
        ) from exc
    if not is_valid:
        raise AuditSignatureInvalid(
            f"entry entry_hash={entry.entry_hash!r} failed backend signature "
            "verification against the reconstructed canonical message (OD "
            "spec v1.34 §21.2.2 row 7(a))"
        )


def verify_per_family_chains(
    entries: Sequence[AuditLedgerEntry],
    *,
    tenant_scope: str | None = None,
    backend_resolver: BackendResolver | None = None,
    cutover_record: AuditCutoverRecord | None = None,
    ledger_binding_id: str | None = None,
    observed_baseline_identities: Sequence[tuple[str, str]] = (),
) -> FamilyVerificationReport:
    """Producer-aware verification over an interleaved audit-entry sequence.

    See the module docstring for the policy. Content check runs FIRST over
    every entry (mirroring `verify_hash_chain_integrity`'s
    content-before-linkage order), then linkage over the redaction-token
    subsequence only, then — when `backend_resolver` is supplied (U-OD-55,
    OD spec v1.34 §21.2.2) — per-entry backend signature verification and
    the legacy-baseline cross-check. Absent `backend_resolver`, this
    function's behavior is BYTE-IDENTICAL to the pre-U-OD-55 B-49 surface
    (row 1: "current behavior PRESERVED VERBATIM").

    `tenant_scope` is normalized via the SAME §21.2.1 tag rule-set signing
    uses (`signing_token`) — one source of truth at both ends (row 2).
    `cutover_record` + `ledger_binding_id` gate legacy exemption (rows 3-5):
    when both are supplied, a record whose signed `ledger_binding_id`
    disagrees with the deployment's configured binding is REJECTED before
    any row is dispositioned — a record authored for a different sidecar
    must never authorize exemptions here (row 4's cross-ledger guard).
    `observed_baseline_identities` are cross-checked against the cutover
    record's own `(tenant_scope, entry_hash)` rows in BOTH directions and
    reported explicitly via `FamilyVerificationReport.baseline_divergences`
    (row 6) — never silently omitted.
    """
    for i, entry in enumerate(entries):
        recomputed = compute_entry_hash(entry.payload)
        if recomputed != entry.entry_hash:
            raise HashChainBreach(
                f"audit entry {i} content integrity violated: stored "
                f"entry_hash={entry.entry_hash!r} does not match recomputed "
                f"hash={recomputed!r} over the entry's payload — payload "
                f"tampered without recomputing entry_hash (C-OD-21 §21.2)"
            )

    chained: dict[str, int] = {}
    per_entry: dict[str, int] = {}
    redaction_rows: list[AuditLedgerEntry] = []
    for entry in entries:
        if _is_redaction_row(entry):
            redaction_rows.append(entry)
        else:
            key = _per_entry_family_key(entry)
            per_entry[key] = per_entry.get(key, 0) + 1

    if redaction_rows:
        # Content was already verified above; the LINKAGE check is what the
        # redaction family's real chain-position wiring makes meaningful.
        # Inlined (mirroring verify_hash_chain_integrity's linkage loop)
        # rather than wrapped in AuditLedger, whose carrier requires a
        # CellID this pure verification surface has no business inventing.
        for i in range(1, len(redaction_rows)):
            prior_hash = redaction_rows[i].payload.prior_entry_hash
            predecessor_hash = redaction_rows[i - 1].entry_hash
            if prior_hash != predecessor_hash:
                raise HashChainBreach(
                    f"redaction-token family hash chain broken at family "
                    f"index {i}: prior_entry_hash={prior_hash!r} != "
                    f"predecessor entry_hash={predecessor_hash!r} "
                    f"(C-OD-21 §21.2 / B-49 per-family policy)"
                )
        chained[REDACTION_TOKEN_FAMILY] = len(redaction_rows)

    signature_dispositions: dict[str, int] = {}
    baseline_divergences: list[str] = []

    if backend_resolver is not None:
        if (
            cutover_record is not None
            and ledger_binding_id is not None
            and cutover_record.ledger_binding_id != ledger_binding_id
        ):
            raise CutoverRecordValidationError(
                "cutover record's signed ledger_binding_id="
                f"{cutover_record.ledger_binding_id!r} does not match the "
                f"configured deployment binding {ledger_binding_id!r} — a "
                "record authored for a different sidecar must not authorize "
                "exemptions here (OD spec v1.34 §21.2.2 row 4)"
            )

        normalized_scope = signing_token(tenant_scope)

        for entry in entries:
            disposition = _resolve_cutover_disposition(entry, cutover_record, normalized_scope)
            if disposition is VerificationDisposition.QUARANTINED:
                signature_dispositions["quarantined"] = (
                    signature_dispositions.get("quarantined", 0) + 1
                )
                continue
            if disposition is VerificationDisposition.PLACEHOLDER_EXEMPT:
                signature_dispositions["exempt"] = signature_dispositions.get("exempt", 0) + 1
                continue
            _verify_entry_signature(
                entry,
                disposition=disposition,
                normalized_scope=normalized_scope,
                backend_resolver=backend_resolver,
            )
            signature_dispositions["verified"] = signature_dispositions.get("verified", 0) + 1

        if cutover_record is not None or observed_baseline_identities:
            recorded_identities = {
                (row.tenant_scope, row.entry_hash)
                for row in (cutover_record.rows if cutover_record is not None else ())
            }
            observed_identities = set(observed_baseline_identities)
            for identity in sorted(recorded_identities - observed_identities):
                baseline_divergences.append(
                    f"recorded cutover identity {identity!r} is missing from "
                    "the observed baseline (OD spec v1.34 §21.2.2 row 6)"
                )
            for identity in sorted(observed_identities - recorded_identities):
                baseline_divergences.append(
                    f"observed baseline identity {identity!r} is missing "
                    "from the cutover record (OD spec v1.34 §21.2.2 row 6)"
                )

    return FamilyVerificationReport(
        chained=chained,
        per_entry=per_entry,
        signature_dispositions=signature_dispositions,
        baseline_divergences=tuple(baseline_divergences),
    )
