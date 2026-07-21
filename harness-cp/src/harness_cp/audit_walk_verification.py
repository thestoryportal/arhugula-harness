"""C-CP-20 §20.3.1 backend-aware blocking audit-walk (U-CP-44/U-CP-45 v2.38
amendment; CP spec v1.101 §3 + §4).

The §20.3.1 walk is the READ-PATH external-auditor protocol (spec §3 row 3:
zero dispatch-path invocation sites): its per-entry verification mechanics
(spec walk step 2) are OD-DEFINED at OD v1.34 §21.2.2 — this module BINDS the
walk to them without restating them, via an INJECTED batch-oriented verifier.

**Mediation (spec §3 row 1).** `harness-cp` MUST NOT import `harness-od`
(`harness-od` already imports `harness-cp` for `SigningBackend` — a direct
call cycles; the OD→CP canonical direction per CXA §2.3.3 also forbids it).
The walk therefore takes the verifier as an injected callable satisfying the
CP-OWNED `AuditWalkVerifier` Protocol (the §20.2.1 `SigningBackend`
injection-seam precedent: opaque entries in, CP-typed outcome out, no OD
import anywhere in this package). The verifier is BATCH-ORIENTED — the
§21.2.2 record completeness/exemption comparisons run over the WHOLE
observed set in both directions, so a per-entry callback would either report
every other recorded identity missing per row or silently drop the
completeness checks. The composition root in `harness-runtime` (which
imports both packages; U-RT-138's inspect wiring is the production injection
site) supplies the adapter over the real U-OD-55 verifier.

**Result boundary (spec §3 rows 4-6; CP plan v2.38 §3).** The injected
callable returns/raises through CP-owned types only:

- `WalkVerificationOutcome` — per-entry verdicts (as available), the
  signature-disposition sections (verified / exempt / quarantined), the
  baseline-divergence section, and an optional `invalid` signal carrying the
  typed discriminator (`SIGNATURE_INVALID` ≠ `HASH_CHAIN_BREACH` — the
  operator sees WHICH trust property failed; both are audit-FAIL).
- `AuditWalkVerifierUnavailableError` — the EXPLICIT availability
  discriminator (spec §3 row 5): the adapter wraps exactly the OD taxonomy
  branch-(b) availability errors (backend unavailability, unknown `key_id`)
  in it; availability is never a verdict. ANY OTHER raise from the injected
  callable (a `TypeError`/`KeyError`/programming error) PROPAGATES UNWRAPPED
  as a defect, never misclassified as rerunnable infrastructure.

**Blocking semantics (spec §3 rows 1b-2).** The walk is the BLOCKING
compliance protocol: invoked without a verifier it returns an EXPLICIT
INCOMPLETE/UNVERIFIED result, NEVER a hash-only pass (a passing audit over
unchecked mutable signature metadata is exactly the fabricate-VERIFIED
failure the preserved CP v1.98 disposition rejects). Hash-chain-only
behavior remains available only on the OD API's own non-walk library default
(OD v1.34 §21.2.2 rows 1/8). Failure recovery routes through the §4.1.28
operator-escalation protocol, exactly as at v1.2.

**§20.1.1 historical exception (spec §4; U-CP-42 v2.38 amendment).** At the
walk, record MEMBERSHIP alone never satisfies §20.1 row 3 — the attested
DISPOSITION gates: `placeholder_exempt` rows pass WITHOUT a verifiable
signature (the exception proper, REPORTED explicitly, never silently
passed); `four_tuple_real` rows are an era marker and still cryptographically
verify inside the injected verifier (an invalid one surfaces as the
`SIGNATURE_INVALID` signal and FAILS the audit); `quarantined` rows NEVER
pass. Membership is NEVER keyed on signature-value shape: an `unsigned:*`-
shaped value on a row ABSENT from the record is a verification FAILURE
(surfaced by the verifier as invalid), not a legacy row — this module
contains NO signature-shape inspection at all (the mutation the witness
forecloses). The record's AUTHENTICATED / CONTENT-BOUND / TENANT-BOUND
requirements are OD-defined (OD plan v2.29 U-OD-55 acc #4) — cross-
referenced, not restated.

Rotation-pair steps 3-6 of the §20.3.1 six-step protocol are PRESERVED
VERBATIM at `five_axis_composition.verify_rotation_6_steps`; their
backend-aware implementation remains `B-33`'s scope (spec §3 row 7).
"""

from __future__ import annotations

from collections.abc import Sequence
from enum import StrEnum
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "AuditWalkVerifier",
    "AuditWalkVerifierUnavailableError",
    "BlockingAuditWalkResult",
    "WalkEntryVerdict",
    "WalkEntryVerdictKind",
    "WalkInvalidDiscriminator",
    "WalkInvalidSignal",
    "WalkResultKind",
    "WalkVerificationOutcome",
    "run_blocking_audit_walk",
]


class AuditWalkVerifierUnavailableError(Exception):
    """Verification INFRASTRUCTURE was unavailable — never a verdict.

    The CP-owned availability discriminator (spec §3 row 5): backend
    unavailability and a `key_id` unknown to the supplied resolver/mapping
    are re-runnable infrastructure conditions — the walk run is INCOMPLETE,
    neither passed nor failed-as-tampered; a re-run after availability is
    restored completes the walk. The runtime composition-root adapter wraps
    EXACTLY the OD taxonomy branch-(b) availability errors in this type;
    `harness-cp` never names an OD type.
    """


class WalkInvalidDiscriminator(StrEnum):
    """WHICH trust property failed (spec §3 row 4 — preserved through the
    walk's failure report; both are audit-FAIL)."""

    SIGNATURE_INVALID = "signature-invalid"
    HASH_CHAIN_BREACH = "hash-chain-breach"


class WalkInvalidSignal(BaseModel):
    """The CP-side invalid outcome of the injected verifier."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    discriminator: WalkInvalidDiscriminator
    reason: str


class WalkEntryVerdictKind(StrEnum):
    """Per-entry walk verdicts (spec §3 rows 4-6, §4 rows 1-2)."""

    VALID = "valid"
    INVALID = "invalid"
    EXEMPT_PLACEHOLDER = "exempt-placeholder"
    QUARANTINED = "quarantined"
    UNVERIFIED = "unverified"


class WalkEntryVerdict(BaseModel):
    """One entry's verdict, as available from the injected verifier.

    The real U-OD-55 verifier raises on the first invalid row (aggregate
    report on success), so per-entry granularity may be PARTIAL from the
    production adapter; fake verifiers in tests may populate fully. The
    aggregate `signature_dispositions` mapping is the always-populated
    section.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    entry_ref: str
    kind: WalkEntryVerdictKind
    reason: str = ""


class WalkVerificationOutcome(BaseModel):
    """What the injected batch verifier returns — the CP-owned report.

    `invalid` non-`None` → the batch contained an invalid row (signature or
    hash-chain, discriminated). Otherwise the aggregate sections describe
    the successful verification: `signature_dispositions` maps
    `"verified"` / `"exempt"` / `"quarantined"` to entry counts;
    `baseline_divergences` reports every legacy-baseline cross-check
    mismatch in both directions (never silently omitted).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    invalid: WalkInvalidSignal | None = None
    entry_verdicts: tuple[WalkEntryVerdict, ...] = ()
    # ACCEPTED RESIDUAL (codex round-8 P2 on the U-RT-138 leg): `dict` is
    # not deeply frozen — a same-process caller could mutate it between
    # verification and reporting. `MappingProxyType` here breaks pydantic
    # deep-copy ("cannot pickle 'mappingproxy'", hit on this very field in
    # part 1); report paths copy via `dict(...)`, and the consumers are
    # construct-then-immediately-report CLI surfaces.
    signature_dispositions: dict[str, int] = Field(default_factory=dict)
    baseline_divergences: tuple[str, ...] = ()


@runtime_checkable
class AuditWalkVerifier(Protocol):
    """The injected batch-oriented per-entry verification seam (spec §3 row 1).

    `audit_entries` is an OPAQUE sequence — the composition root supplies
    both the entries and the verifier from the same (OD-typed) world, so
    this package never names the entry type. `tenant_scope` is passed RAW;
    normalization is OD-owned inside the verifier (§21.2.1 row 2).
    `observed_baseline_identities` carries the sidecar-observed
    `(source_tag, entry_hash)` identities for the record's both-direction
    baseline cross-check.

    Raises `AuditWalkVerifierUnavailableError` for availability (never a
    verdict); any other raise is a defect and propagates unwrapped.
    """

    def verify(
        self,
        audit_entries: Sequence[object],
        *,
        tenant_scope: str | None,
        observed_baseline_identities: Sequence[tuple[str, str]],
    ) -> WalkVerificationOutcome: ...


class WalkResultKind(StrEnum):
    """The blocking walk's terminal disposition."""

    PASSED = "passed"
    FAILED = "failed"
    INCOMPLETE_UNVERIFIED = "incomplete-unverified"


class BlockingAuditWalkResult(BaseModel):
    """The §20.3.1 blocking walk's result — never a silent anything.

    `exempt_entries` / `quarantined_entries` / `unverified_entries` are the
    spec §3 row 6 explicit report sections (exempt / quarantined /
    UNVERIFIED, never silently passed). `failure_discriminator` preserves
    WHICH trust property failed on the FAILED kind (row 4).
    `rerunnable` marks the availability-INCOMPLETE case (row 5): a re-run
    after availability is restored completes the walk; the no-verifier
    INCOMPLETE is NOT rerunnable-as-is (the injection is missing, not the
    infrastructure).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: WalkResultKind
    detail: str
    failure_discriminator: WalkInvalidDiscriminator | None = None
    signature_dispositions: dict[str, int] = Field(default_factory=dict)
    exempt_entries: tuple[WalkEntryVerdict, ...] = ()
    quarantined_entries: tuple[WalkEntryVerdict, ...] = ()
    unverified_entries: tuple[WalkEntryVerdict, ...] = ()
    baseline_divergences: tuple[str, ...] = ()
    rerunnable: bool = False


def run_blocking_audit_walk(
    audit_entries: Sequence[object],
    *,
    verifier: AuditWalkVerifier | None,
    tenant_scope: str | None = None,
    observed_baseline_identities: Sequence[tuple[str, str]] = (),
) -> BlockingAuditWalkResult:
    """Run the §20.3.1 blocking audit-walk over `audit_entries`.

    Dispositions (in precedence order):

    1. `verifier is None` → `INCOMPLETE_UNVERIFIED` (spec §3 row 1b — the
       walk NEVER produces a hash-only pass; the pre-v1.98 fabricate-
       VERIFIED disposition stays rejected). Not rerunnable-as-is.
    2. `AuditWalkVerifierUnavailableError` from the verifier →
       `INCOMPLETE_UNVERIFIED` with `rerunnable=True` (row 5 — neither
       passed nor failed-as-tampered). Any OTHER raise propagates unwrapped
       as a defect.
    3. An `invalid` signal → `FAILED` with the typed discriminator preserved
       (row 4 — `SIGNATURE_INVALID` ≠ `HASH_CHAIN_BREACH`, both audit-FAIL;
       §4.1.28 operator-escalation recovery governs).
    4. Quarantined rows → `FAILED` (§4 rows 1-2: quarantined NEVER passes),
       reported explicitly.
    5. Baseline divergences → `FAILED` (row 6 — a record/observed mismatch
       in either direction is an audit failure, reported explicitly).
    6. `unverified` disposition rows → `INCOMPLETE_UNVERIFIED` (row 6 —
       never silently passed).
    7. Otherwise → `PASSED`, with `placeholder_exempt` rows passing
       signatureless AND reported (§4 — the exception proper; `exempt`
       counts surface in `signature_dispositions` + `exempt_entries`).
    """
    if verifier is None:
        return BlockingAuditWalkResult(
            kind=WalkResultKind.INCOMPLETE_UNVERIFIED,
            detail=(
                "no backend-aware verifier injected — §20.3.1 step 2 requires "
                "per-entry signature verification; a pass over unchecked "
                "mutable signature_attrs would fabricate VERIFIED (CP v1.101 "
                "§3 row 1b). The composition root must supply the OD v1.34 "
                "§21.2.2 verifier adapter."
            ),
            rerunnable=False,
        )

    try:
        outcome = verifier.verify(
            audit_entries,
            tenant_scope=tenant_scope,
            observed_baseline_identities=observed_baseline_identities,
        )
    except AuditWalkVerifierUnavailableError as exc:
        return BlockingAuditWalkResult(
            kind=WalkResultKind.INCOMPLETE_UNVERIFIED,
            detail=(
                f"verification infrastructure unavailable — the walk run is "
                f"INCOMPLETE, neither passed nor failed-as-tampered; re-run "
                f"after availability is restored (CP v1.101 §3 row 5): {exc}"
            ),
            rerunnable=True,
        )
    # NO except Exception arm — a TypeError/KeyError/programming error from
    # the injected callable is a defect and propagates unwrapped (spec §3
    # row 1's result-boundary contract), never misclassified as rerunnable
    # infrastructure.

    # An INVALID per-entry verdict fails the walk even when the verifier
    # did not ALSO populate `outcome.invalid` — the public outcome type
    # admits that state, so it must be gated, not assumed away (codex
    # round-5 P1 on the U-RT-138 leg).
    invalid_verdicts = tuple(
        v for v in outcome.entry_verdicts if v.kind is WalkEntryVerdictKind.INVALID
    )
    if outcome.invalid is None and invalid_verdicts:
        first = invalid_verdicts[0]
        return BlockingAuditWalkResult(
            kind=WalkResultKind.FAILED,
            detail=(
                f"audit FAILED: {len(invalid_verdicts)} INVALID entry "
                f"verdict(s) (first: {first.entry_ref}: {first.reason}) — a "
                f"verifier-reported invalid entry never falls through to "
                f"PASSED (C-CP-20 §20.3.1)"
            ),
            failure_discriminator=WalkInvalidDiscriminator.SIGNATURE_INVALID,
            signature_dispositions=outcome.signature_dispositions,
            baseline_divergences=outcome.baseline_divergences,
        )

    exempt = tuple(
        v for v in outcome.entry_verdicts if v.kind is WalkEntryVerdictKind.EXEMPT_PLACEHOLDER
    )
    quarantined = tuple(
        v for v in outcome.entry_verdicts if v.kind is WalkEntryVerdictKind.QUARANTINED
    )
    unverified = tuple(
        v for v in outcome.entry_verdicts if v.kind is WalkEntryVerdictKind.UNVERIFIED
    )

    if outcome.invalid is not None:
        return BlockingAuditWalkResult(
            kind=WalkResultKind.FAILED,
            detail=(
                f"audit FAILED ({outcome.invalid.discriminator.value}): "
                f"{outcome.invalid.reason} — recovery routes through the "
                f"§4.1.28 operator-escalation protocol"
            ),
            failure_discriminator=outcome.invalid.discriminator,
            signature_dispositions=outcome.signature_dispositions,
            exempt_entries=exempt,
            quarantined_entries=quarantined,
            unverified_entries=unverified,
            baseline_divergences=outcome.baseline_divergences,
        )

    quarantined_count = outcome.signature_dispositions.get("quarantined", 0) or len(quarantined)
    if quarantined_count:
        return BlockingAuditWalkResult(
            kind=WalkResultKind.FAILED,
            detail=(
                f"audit FAILED: {quarantined_count} quarantined row(s) — a "
                f"quarantined disposition NEVER passes (C-CP-20 §20.1.1); "
                f"reported explicitly, recovery per §4.1.28"
            ),
            failure_discriminator=WalkInvalidDiscriminator.SIGNATURE_INVALID,
            signature_dispositions=outcome.signature_dispositions,
            exempt_entries=exempt,
            quarantined_entries=quarantined,
            unverified_entries=unverified,
            baseline_divergences=outcome.baseline_divergences,
        )

    if outcome.baseline_divergences:
        return BlockingAuditWalkResult(
            kind=WalkResultKind.FAILED,
            detail=(
                f"audit FAILED: {len(outcome.baseline_divergences)} "
                f"legacy-baseline divergence(s) between the authenticated "
                f"cutover record and the observed set (CP v1.101 §3 row 6 — "
                f"reported explicitly, never silently passed)"
            ),
            # No row-4 discriminator: signatures and hash chains are VALID
            # here — the failed trust property is row-6 baseline
            # completeness, and labeling it SIGNATURE_INVALID misstates it
            # to result consumers (codex round-6 P2).
            failure_discriminator=None,
            signature_dispositions=outcome.signature_dispositions,
            exempt_entries=exempt,
            quarantined_entries=quarantined,
            unverified_entries=unverified,
            baseline_divergences=outcome.baseline_divergences,
        )

    if unverified:
        return BlockingAuditWalkResult(
            kind=WalkResultKind.INCOMPLETE_UNVERIFIED,
            detail=(
                f"{len(unverified)} row(s) UNVERIFIED — reported explicitly, "
                f"never silently passed (CP v1.101 §3 row 6); the walk is "
                f"INCOMPLETE"
            ),
            signature_dispositions=outcome.signature_dispositions,
            exempt_entries=exempt,
            quarantined_entries=quarantined,
            unverified_entries=unverified,
            baseline_divergences=outcome.baseline_divergences,
            rerunnable=True,
        )

    return BlockingAuditWalkResult(
        kind=WalkResultKind.PASSED,
        detail=(
            "audit PASSED — per-entry signatures verified via the injected "
            "backend-aware verifier"
            + (
                f"; {len(exempt)} §20.1.1 placeholder_exempt row(s) passed "
                f"signatureless and are reported explicitly"
                if exempt
                else ""
            )
        ),
        signature_dispositions=outcome.signature_dispositions,
        exempt_entries=exempt,
        quarantined_entries=quarantined,
        unverified_entries=unverified,
        baseline_divergences=outcome.baseline_divergences,
    )
