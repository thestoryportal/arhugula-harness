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
    AuditCutoverRecordRow,
    CutoverRecordValidationError,
    VerificationDisposition,
    verify_cutover_record_signature,
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
    "VerificationBackendKeyUnknownError",
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
    nothing about the signature it can't check). Raised ONLY when
    `backend_resolver` raises the dedicated `VerificationBackendKeyUnknownError`
    (see that type's docstring — a bare built-in `KeyError` from inside a
    resolver is NOT treated as "unknown key": it is indistinguishable from
    an accidental programming `KeyError`, so it propagates unwrapped as a
    defect; out-of-family Codex [P2] finding, round 2 on this arc). A
    `backend.verify` call that itself raises is deliberately left UNGUARDED
    (row 9's breaker-asymmetry rationale: this module never breaker-couples
    or reclassifies the read path itself, and there is no established typed
    "verify-side hard failures" family to key a narrow catch on; see
    `test_verify_path_not_breaker_instrumented`) — a well-behaved backend
    implementation is expected to raise THIS type itself for its own
    genuine infrastructure failures (e.g. a network timeout talking to a
    KMS); translating a specific vendor SDK's exceptions into this contract
    is that backend implementation's responsibility, not this module's (a
    concrete backend, e.g. ADR-D8's `AwsKmsSigningBackend`, is CP-axis
    scope, out of U-OD-55's reach).
    """


class VerificationBackendKeyUnknownError(Exception):
    """The CONTRACTUAL signal a `BackendResolver` raises to report "no
    backend is configured for this `(algorithm, key_id)`" — e.g. a key
    rotation the operator's key mapping hasn't caught up with, or a
    genuinely incomplete mapping.

    A resolver MUST raise this specific type (or a subclass) for that
    condition — NOT a bare built-in `KeyError` (out-of-family Codex [P2]
    finding, round 2: a resolver's own internal bug can ALSO raise
    `KeyError`, e.g. from a missing internal config field; treating every
    `KeyError` as "unknown key" would misclassify that bug as a retryable
    availability gap instead of the defect it is). `verify_per_family_chains`
    catches ONLY this type and wraps it into
    `AuditVerificationBackendUnavailableError`; any other exception from a
    resolver call propagates unwrapped.
    """


BackendResolver = Callable[[SignatureAlgorithm, str], SigningBackend]
"""Per-row verification-backend resolver keyed on an entry's STORED
`(audit_signature_algorithm, audit_signature_key_id)` — NOT a single
`SigningBackend | None` (OD spec v1.34 §21.2.2 row 1): one backend exposes
one `.algorithm` and cannot verify mixed multi-algorithm history. Must
raise `VerificationBackendKeyUnknownError` (not a bare `KeyError`) to report an
unresolvable `(algorithm, key_id)` pair."""


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


def _index_cutover_rows_by_entry_hash(
    cutover_record: AuditCutoverRecord | None, normalized_scope: str | None
) -> dict[str, list[AuditCutoverRecordRow]]:
    """Pre-index a cutover record's rows by `entry_hash`, scoped to the
    CURRENT `normalized_scope` — built ONCE per `verify_per_family_chains`
    call rather than re-scanning all M record rows for every one of N
    entries (out-of-family Codex [P2] finding, round 4: an O(N×M) full
    scan makes large-history verification prohibitively slow)."""
    index: dict[str, list[AuditCutoverRecordRow]] = {}
    if cutover_record is None or normalized_scope is None:
        return index
    for row in cutover_record.rows:
        if row.tenant_scope == normalized_scope:
            index.setdefault(row.entry_hash, []).append(row)
    return index


def _resolve_cutover_disposition(
    entry: AuditLedgerEntry,
    rows_by_entry_hash: dict[str, list[AuditCutoverRecordRow]],
    normalized_scope: str | None,
) -> AuditCutoverRecordRow | None:
    """The cutover-record ROW governing `entry`, if any (OD spec v1.34
    §21.2.2 row 4 — the verifier compares each recorded scope against its
    row-2 tenant input). Returns the ROW itself (not just its disposition)
    so the caller can track the exact `(source_tag, entry_hash)` SOURCE
    identity a full entry consumed — needed to correctly scope the
    baseline-only cross-check (see its call site). A cutover record only
    dispositions rows for a REAL tenant scope (the untenanted/single-tenant
    case has no legacy-migration story to exempt); absent a match, the
    entry is treated as post-cutover per row 3.

    Matches on `(tenant_scope, entry_hash)` — the DESTINATION identity —
    but the record's own uniqueness rule (`AuditCutoverRecord._validate_rows`)
    deliberately permits TWO rows sharing a destination when at most one is
    NON-quarantined (distinct SOURCE rows migrating to the same target; the
    `source_tag` disambiguates them in the SOURCE-uniqueness check).
    NON-quarantined rows (`placeholder_exempt` / `four_tuple_real`) DO
    legitimately govern a full entry regardless of `source_tag` — a
    `"_single"` migration row that was RETAGGED under this real tenant is
    exactly the primary use case. The record's own uniqueness rule
    guarantees AT MOST ONE non-quarantined row per destination, so a match
    there is NEVER ambiguous (out-of-family Codex [P2] finding, round 3:
    an earlier version rejected this legitimate collision shape outright
    as "ambiguous").

    A QUARANTINED row is different: BY THE MIGRATION CONTRACT it is NEVER
    retagged, so a `source_tag == "_single"` quarantined row can NEVER be
    the actual full entry — only an ALREADY-TAGGED quarantined row
    (`source_tag == normalized_scope`) can (out-of-family Codex [P2]
    finding, round 5: treating a `"_single"`-tagged quarantined row as
    governing a full entry silently skipped that entry's REAL signature
    verification and misreported a genuinely post-cutover row as
    "quarantined"). Only when ZERO non-quarantined rows match do
    already-tagged quarantined rows apply; source-identity uniqueness
    guarantees at most one such row per destination too, so this is also
    never genuinely ambiguous — the residual "more than one" raise is
    defense in depth against a record that bypassed normal construction.
    """
    matches = rows_by_entry_hash.get(entry.entry_hash, [])
    non_quarantined = [
        row
        for row in matches
        if row.verification_disposition is not VerificationDisposition.QUARANTINED
    ]
    if len(non_quarantined) == 1:
        return non_quarantined[0]
    if non_quarantined:
        # Structurally impossible per the record's own destination-
        # uniqueness rule — defense in depth, not a reachable production case.
        raise CutoverRecordValidationError(
            f"cutover record has {len(non_quarantined)} NON-quarantined rows "
            f"dispositioning the same destination identity (tenant_scope="
            f"{normalized_scope!r}, entry_hash={entry.entry_hash!r}) — "
            "the record's own uniqueness rule should have forbidden this "
            "(OD spec v1.34 §21.2.2 row 4)"
        )
    # A QUARANTINED row is, BY THE MIGRATION CONTRACT, NEVER retagged — so
    # only an ALREADY-TAGGED quarantined row (source_tag == normalized_scope,
    # meaning it was tagged under this real tenant independent of this
    # cutover record, and is merely flagged quarantined post-hoc) can
    # legitimately govern a FULL entry read under this tenant scope. A
    # `source_tag == "_single"` quarantined row can NEVER be the full entry
    # matching this hash — treating it as such would wrongly report a
    # genuinely post-cutover tenant row as "quarantined" and SKIP its real
    # signature verification entirely (out-of-family Codex [P2] finding,
    # round 5). Such a row remains a legitimate BASELINE-ONLY identity — the
    # caller's separate baseline cross-check still covers it; this function
    # only decides FULL-entry governance.
    quarantined_already_tagged = [
        row
        for row in matches
        if row.verification_disposition is VerificationDisposition.QUARANTINED
        and row.source_tag == normalized_scope
    ]
    if len(quarantined_already_tagged) > 1:
        # Structurally impossible per source-identity uniqueness (an
        # already-tagged row's source_tag is PINNED to normalized_scope, so
        # at most one such row can exist per entry_hash) — defense in depth
        # against a record that bypassed normal construction/validation.
        raise CutoverRecordValidationError(
            f"cutover record has {len(quarantined_already_tagged)} "
            "already-tagged QUARANTINED rows dispositioning the same "
            f"destination identity (tenant_scope={normalized_scope!r}, "
            f"entry_hash={entry.entry_hash!r}) — the record's own "
            "source-identity uniqueness rule should have forbidden this "
            "(OD spec v1.34 §21.2.2 row 4)"
        )
    return quarantined_already_tagged[0] if quarantined_already_tagged else None


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
    except VerificationBackendKeyUnknownError as exc:
        raise AuditVerificationBackendUnavailableError(
            "no verification backend available for (algorithm="
            f"{algo.value!r}, key_id={sig_attrs.audit_signature_key_id!r}) "
            "— an unresolvable key_id at verify-time is an availability "
            "gap, not a verdict (OD spec v1.34 §21.2.2 row 7(b))"
        ) from exc
    if backend.algorithm != algo.value:
        # ed25519 and ecdsa-p256 are BOTH 64 bytes (SIGNATURE_LENGTH_BY_
        # ALGORITHM), so the length check above cannot by itself catch a
        # misconfigured resolver returning a WRONG-algorithm backend for
        # this entry's stored algorithm (out-of-family Codex [P1] finding,
        # round 3) — a backend must not attest under an algorithm other
        # than the one the entry itself claims.
        raise AuditSignatureInvalid(
            f"entry entry_hash={entry.entry_hash!r} declares algorithm "
            f"{algo.value!r} but the resolved backend.algorithm="
            f"{backend.algorithm!r} disagrees — a backend must not attest "
            "under a different algorithm than the one the entry claims "
            "(OD spec v1.34 §21.2.2 row 7(a))"
        )

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
    # NOTE (out-of-family Codex [P2]): `backend.verify` is called UNGUARDED —
    # unlike the resolver's KeyError-specific catch above, there is no
    # established typed "verify-side hard failures" family (mirroring
    # AUDIT_SIGNING_HARD_FAILURES on the sign side) to key a narrow catch on,
    # and row 9 explicitly reserves breaker/availability handling for the
    # Runtime-owned wrapper — this module must not invent its own wrapping
    # policy for backend.verify. A raised exception here (programming defect
    # OR an already-typed availability error a production backend raises)
    # propagates UNWRAPPED to the caller, never silently reclassified.
    is_valid = backend.verify(
        message=message,
        signature=signature_bytes,
        key_id=sig_attrs.audit_signature_key_id,
        key_period=_DEPLOYMENT_BOUND_KEY_PERIOD,
    )
    # `is not True` (not `not is_valid`) — a duck-typed backend adapter
    # returning a truthy non-`bool` SDK value (e.g. `{"SignatureValid":
    # False}`) would satisfy `not is_valid` as falsy-ish in SOME shapes but
    # pass a bare truthiness check in others; requiring the LITERAL `True`
    # fails closed on anything that isn't exactly the expected boolean
    # verdict (out-of-family Codex [P1] finding, round 4).
    if is_valid is not True:
        raise AuditSignatureInvalid(
            f"entry entry_hash={entry.entry_hash!r} failed backend signature "
            "verification against the reconstructed canonical message — "
            f"backend.verify returned {is_valid!r} (OD spec v1.34 §21.2.2 "
            "row 7(a))"
        )


def verify_per_family_chains(
    entries: Sequence[AuditLedgerEntry],
    *,
    tenant_scope: str | None = None,
    backend_resolver: BackendResolver | None = None,
    cutover_record: AuditCutoverRecord | None = None,
    cutover_record_signature: bytes | None = None,
    expected_cutover_record_key_id: str | None = None,
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

    Supplying `cutover_record` REQUIRES `cutover_record_signature`,
    `expected_cutover_record_key_id`, and `ledger_binding_id` — a record is
    trusted ONLY once: (a) its `key_id` matches the operator-PINNED
    `expected_cutover_record_key_id` (row 4 — the record-signing key is
    NEVER a row-derived/self-claimed key; a record signed under an
    ordinary per-entry key in the resolver's mapping must not be trusted);
    (b) its OWN signature verifies against a backend resolved via
    `backend_resolver` for that pinned key (row 4: "AUTHENTICATED" — an
    unsigned or unverified record must never gate a live exemption); and
    (c) its signed `ledger_binding_id` matches the deployment's configured
    binding (row 4's cross-ledger guard — omitting `ledger_binding_id` must
    not silently skip this check, so it is REQUIRED, not merely compared
    when both happen to be present). `observed_baseline_identities` are
    cross-checked against the cutover record's BASELINE-ONLY rows FILTERED
    TO THE REQUESTED `tenant_scope` (SOURCE identity `(source_tag,
    entry_hash)` — the shape the sidecar reader observes; rows whose
    `entry_hash` already has a full entry in `entries` are excluded, since
    those were content/signature-verified above and are not baseline-only;
    a ledger-wide record's OTHER-tenant rows are excluded too, or every
    other tenant's baseline would report as a false divergence) in BOTH
    directions — reported explicitly via
    `FamilyVerificationReport.baseline_divergences` (row 6) — never
    silently omitted; MATCHED identities are ALSO reported, via
    `signature_dispositions`, never silently dropped either.
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
        if cutover_record is not None:
            # `not value` (not `value is None`) — an EMPTY-STRING trust
            # identifier is the classic "missing configuration represented
            # as an empty default" footgun: it would still satisfy an
            # `is None` check and a subsequent equality compare against an
            # equally-empty record field (out-of-family Codex [P1] finding,
            # round 3). Both REQUIRED-ness checks below reject empty too.
            if not ledger_binding_id:
                raise CutoverRecordValidationError(
                    "ledger_binding_id is REQUIRED (and non-empty) whenever "
                    "cutover_record is supplied — a caller that omits it, or "
                    "supplies the empty string, must not silently skip the "
                    "cross-ledger binding guard (OD spec v1.34 §21.2.2 row 4)"
                )
            if cutover_record.ledger_binding_id != ledger_binding_id:
                raise CutoverRecordValidationError(
                    "cutover record's signed ledger_binding_id="
                    f"{cutover_record.ledger_binding_id!r} does not match the "
                    f"configured deployment binding {ledger_binding_id!r} — a "
                    "record authored for a different sidecar must not "
                    "authorize exemptions here (OD spec v1.34 §21.2.2 row 4)"
                )
            if cutover_record_signature is None:
                raise CutoverRecordValidationError(
                    "cutover_record_signature is REQUIRED whenever "
                    "cutover_record is supplied — an unauthenticated record "
                    "must never gate a legacy exemption (OD spec v1.34 "
                    "§21.2.2 row 4: AUTHENTICATED)"
                )
            if not expected_cutover_record_key_id:
                raise CutoverRecordValidationError(
                    "expected_cutover_record_key_id is REQUIRED (and "
                    "non-empty) whenever cutover_record is supplied — the "
                    "record-signing key is the operator-PINNED "
                    "audit_cutover_record_key_id, never a row-derived key "
                    "(OD spec v1.34 §21.2.2 row 4); without this pin, a "
                    "record signed under ANY ordinary per-entry key in the "
                    "resolver's mapping would be trusted (out-of-family "
                    "Codex [P1] finding, round 2)"
                )
            if cutover_record.key_id != expected_cutover_record_key_id:
                raise CutoverRecordValidationError(
                    f"cutover record's key_id={cutover_record.key_id!r} does "
                    "not match the operator-pinned "
                    f"expected_cutover_record_key_id="
                    f"{expected_cutover_record_key_id!r} — the record-signing "
                    "key is never a row-derived/self-claimed key (OD spec "
                    "v1.34 §21.2.2 row 4)"
                )
            try:
                record_backend = backend_resolver(cutover_record.algorithm, cutover_record.key_id)
            except VerificationBackendKeyUnknownError as exc:
                raise AuditVerificationBackendUnavailableError(
                    "no verification backend available for the cutover "
                    f"record's (algorithm={cutover_record.algorithm.value!r}, "
                    f"key_id={cutover_record.key_id!r}) — an unresolvable "
                    "key_id is an availability gap, not a verdict (OD spec "
                    "v1.34 §21.2.2 row 7(b))"
                ) from exc
            # `verify_cutover_record_signature` is itself fully self-defending
            # (algorithm match + signature shape + literal-boolean verdict —
            # out-of-family Codex [P2] finding, round 6: it is a PUBLIC,
            # independently-exported function, so every guard lives there
            # rather than being duplicated at this one call site) — a
            # `False` result covers a backend-algorithm disagreement, a
            # malformed signature, AND a genuine verification failure alike.
            if not verify_cutover_record_signature(
                cutover_record, cutover_record_signature, backend=record_backend
            ):
                raise CutoverRecordValidationError(
                    "cutover_record_signature does not verify against the "
                    "record's canonical message — an unauthenticated or "
                    "tampered record must never gate a legacy exemption (OD "
                    "spec v1.34 §21.2.2 row 4: AUTHENTICATED)"
                )

        normalized_scope = signing_token(tenant_scope)
        rows_by_entry_hash = _index_cutover_rows_by_entry_hash(cutover_record, normalized_scope)
        # The exact SOURCE identity (source_tag, entry_hash) each FULL entry
        # consumed — used to scope the baseline-only cross-check below to
        # ONLY the row actually accounted for by a full entry, not every row
        # sharing that entry_hash (out-of-family Codex [P1] finding, round
        # 4: a hash-only exclusion silently dropped a DIFFERENT, still-
        # baseline-only quarantined source row that happens to collide on
        # entry_hash with a full entry's own destination row).
        consumed_source_identities: set[tuple[str, str]] = set()

        for entry in entries:
            matched_row = _resolve_cutover_disposition(entry, rows_by_entry_hash, normalized_scope)
            disposition = matched_row.verification_disposition if matched_row else None
            if matched_row is not None:
                consumed_source_identities.add((matched_row.source_tag, matched_row.entry_hash))
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
            # SOURCE identity (source_tag, entry_hash) — the shape the
            # sidecar reader observes (out-of-family Codex [P2] finding: a
            # DESTINATION-keyed (tenant_scope, entry_hash) comparison wrongly
            # reports divergence for a legitimate "_single" -> real-tenant
            # migration row, since the observed identity is source-tagged,
            # not destination-tagged). Only the row ACTUALLY consumed by a
            # full entry above is excluded — NOT every row sharing that
            # entry_hash (round 4 fix: a quarantined "_single" row colliding
            # on entry_hash with a full entry's own destination row is a
            # DIFFERENT, still baseline-only, source identity and must stay
            # in this cross-check). A ledger-wide record's rows are further
            # filtered to the CURRENT requested tenant scope (round 2 fix:
            # an unfiltered comparison reports every OTHER tenant's rows as
            # false divergence); the untenanted (`None` `normalized_scope`)
            # case has no baseline-cutover story, so no record rows apply.
            scoped_rows = (
                [
                    row
                    for rows in rows_by_entry_hash.values()
                    for row in rows
                    if (row.source_tag, row.entry_hash) not in consumed_source_identities
                ]
                if cutover_record is not None and normalized_scope is not None
                else []
            )
            recorded_by_identity = {(row.source_tag, row.entry_hash): row for row in scoped_rows}
            recorded_identities = set(recorded_by_identity)
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
            # MATCHED identities are reported EXPLICITLY too (row 6: "exempt
            # / quarantined / UNVERIFIED with the nonzero outcome, never
            # omitted") — out-of-family Codex [P1] finding, round 2: a
            # matched identity previously vanished from BOTH the divergence
            # report AND signature_dispositions, silently.
            for identity in sorted(recorded_identities & observed_identities):
                matched_row = recorded_by_identity[identity]
                if matched_row.verification_disposition is VerificationDisposition.QUARANTINED:
                    signature_dispositions["quarantined"] = (
                        signature_dispositions.get("quarantined", 0) + 1
                    )
                elif (
                    matched_row.verification_disposition
                    is VerificationDisposition.PLACEHOLDER_EXEMPT
                ):
                    signature_dispositions["exempt"] = signature_dispositions.get("exempt", 0) + 1
                else:
                    # FOUR_TUPLE_REAL on a baseline-only identity: there is
                    # no full entry to cryptographically verify against
                    # (that is what makes it baseline-only) — the disposition
                    # is recorded, but "verified" would overclaim.
                    signature_dispositions["baseline_real_unverifiable"] = (
                        signature_dispositions.get("baseline_real_unverifiable", 0) + 1
                    )

    return FamilyVerificationReport(
        chained=chained,
        per_entry=per_entry,
        signature_dispositions=signature_dispositions,
        baseline_divergences=tuple(baseline_divergences),
    )
