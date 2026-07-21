"""MTC audit-signing bootstrap config-validation invariant — U-RT-134.

Implements `Spec_Harness_Runtime_v1.md` v1.101 §3 C-RT-03 Invariants
("Audit-signing config validation") — the Runtime-owned ENFORCEMENT site for
the OD-owned `audit_signing_fail_closed` policy (`Spec_Operational_
Discipline_v1_34.md` §21.2.3 rows 1-4) and the MTC tenant-bootstrap invariant
(OD v1.34 §21.2.1 row 6). Also greenfield-initializes the OD v1.34 §21.2.2
row-4 cutover record when `audit_cutover_record_path` is configured but the
file does not yet exist.

Called from bootstrap stage 4 OD, AFTER the audit-signing backend is
constructed (`make_audit_signing_backend`) — the record-key resolution +
greenfield-signing steps need `backend.algorithm` / `backend.sign()` — and
BEFORE the one-shot global tracer registration (mirrors the round-18
rationale that already gates the sibling `validate_audit_signing_for_span_
stage` call at the same site: a KMS config failure surfacing after
`set_tracer_provider` poisons same-process bootstrap retry).

**Scope boundary (deliberately narrow).** This module owns config-shape
validation + greenfield record initialization ONLY. It does NOT touch the
ten `except AUDIT_SIGNING_HARD_FAILURES` runtime call sites
(`hitl_gate_composer.py`, `sub_agent_dispatch.py`, etc.) — those currently
swallow unconditionally regardless of `audit_signing_fail_closed` (confirmed
by direct read), and wiring them to consult the resolved flag is the
co-land-pinned U-RT-136/U-RT-137 siblings' scope (Runtime plan v2.49 §0.4),
not this unit's.

**Two-class failure partition (spec-mandated).** MISSING v1-required-at-MTC
inputs (absent backend, at every tier when the flag resolves ON; absent
tenant/record inputs, at MTC only) surface as `IncompatibleConfigVersion`
(`RT-FAIL-CONFIG-VERSION`) — the config predates the v1.101 contract,
upgrade it. INVALID v2 VALUES (explicit `false` at MTC, a normalizer-refused
tenant token, a record-key sharing row material or mismatching the mapping
algorithm, a non-MTC opt-in missing its co-required record fields) surface
as `AuditSigningConfigInvalidError` (`RT-FAIL-CONFIG`) — the config speaks v2 and
is wrong. Each raise names every violation in its own class, not just the
first found.
"""

from __future__ import annotations

import contextlib
import json
import os
import sys
import tempfile
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from harness_core import PersonaTier
from harness_cp.f5_signing_key_resolution import SigningBackend
from harness_is.cross_process_ledger_lock import (
    cross_process_read_lock,
    cross_process_write_lock,
)
from harness_od.audit_cutover_record import (
    AuditCutoverRecord,
    CutoverRecordValidationError,
    sign_cutover_record,
    verify_cutover_record_signature,
)
from harness_od.audit_ledger_types import SignatureAlgorithm
from harness_od.multi_tenant_trace_separation_and_audit_ledger import signing_token
from pydantic import ValidationError

from harness_runtime.lifecycle.audit_writer import AUDIT_WRITER_RESERVED_FILENAMES
from harness_runtime.lifecycle.span_processor import REDACTION_TOKEN_SIGNING_KEY_ID
from harness_runtime.types import AuditSigningBackendKind, RuntimeConfig

__all__ = [
    "AuditSigningConfigInvalidError",
    "IncompatibleConfigVersion",
    "initialize_mtc_audit_signing_record",
    "mtc_audit_prewarm_disabled",
    "resolve_audit_signing_fail_closed",
    "validate_and_initialize_mtc_audit_signing",
    "validate_mtc_audit_signing_config",
]


class IncompatibleConfigVersion(Exception):  # noqa: N818 — spec-named identifier (Runtime spec v1.101 §3)
    """`RT-FAIL-CONFIG-VERSION` — a v1-shaped config is missing an input the
    C-RT-03 v1→v2 contract (Runtime spec v1.101) now requires.

    Per the spec's version-evolution clause: an absent backend/tenant/record
    input is a version incompatibility, not a generic config error — the
    config predates the contract and must be upgraded (configure a
    `SigningBackend` + `tenant_id` + the cutover-record inputs), not merely
    corrected in place.
    """

    FAIL_CLASS = "RT-FAIL-CONFIG-VERSION"

    def __init__(self, missing: tuple[str, ...]) -> None:
        self.missing = missing
        super().__init__(
            f"{self.FAIL_CLASS}: configuration predates the C-RT-03 v1.101 "
            f"contract — missing required input(s): {', '.join(missing)}"
        )


class AuditSigningConfigInvalidError(ValueError):
    """`RT-FAIL-CONFIG` — an audit-signing-related config value is invalid,
    per Runtime spec v1.101 Invariants (or a non-MTC record opt-in missing
    its co-required fields, per the general C-RT-03 "required field missing"
    taxonomy row).
    """

    FAIL_CLASS = "RT-FAIL-CONFIG"

    def __init__(self, invalid: tuple[str, ...]) -> None:
        self.invalid = invalid
        super().__init__(f"{self.FAIL_CLASS}: {'; '.join(invalid)}")


def resolve_audit_signing_fail_closed(config: RuntimeConfig) -> bool:
    """Resolve the tri-state `audit_signing_fail_closed` field to a bool.

    OD-owned per-persona default (`Spec_Operational_Discipline_v1_34.md`
    §21.2.3 row 2): unset → `True` at `MULTI_TENANT_COMPLIANCE`, `False`
    elsewhere. Explicit values pass through unchanged. This is the single
    resolution point — reuse it rather than re-deriving the per-persona
    default independently (the sibling U-RT-135/U-RT-136/U-RT-137 units
    consult the same resolved value at their own call sites).
    """
    if config.audit_signing_fail_closed is not None:
        return config.audit_signing_fail_closed
    return config.persona_tier == PersonaTier.MULTI_TENANT_COMPLIANCE


def mtc_audit_prewarm_disabled(config: RuntimeConfig) -> bool:
    """U-RT-135 (Runtime spec v1.101 surface C; fork gate item 8) — True iff
    BOTH B-18-KEEPALIVE surfaces (the stage-5 boot prewarm ping AND the
    daemon `_keepalive_loop` spawn) are disabled as contract terms:
    `persona_tier == MULTI_TENANT_COMPLIANCE` AND the resolved
    `audit_signing_fail_closed` is ON.

    Deliberately MTC-SCOPED per the ratified gate-item-8 letter (plan v2.49
    §1.2 criterion 3): a lower-tier explicit `fail_closed=true` keeps the
    v1.99 prewarm/keepalive posture — the `B-55` register row HOLDS the
    extend/propagate/ratify-as-is disposition, and this predicate must not
    pre-decide it. One source of truth for both call sites (the stage-5
    dispatcher binding and the daemon spawn guard).
    """
    return config.persona_tier is PersonaTier.MULTI_TENANT_COMPLIANCE and (
        resolve_audit_signing_fail_closed(config)
    )


def _resolve_record_key_arn(config: RuntimeConfig, key_id: str) -> str | None:
    return config.audit_signing.key_arns.get(key_id)


def _is_blank(value: str | None) -> bool:
    return value is None or not value.strip()


#: The row-signing consumer key ids every audit write signs under once a
#: backend is threaded (mirrors `stage_4_od.py`'s `additional_key_ids`
#: tuple passed to `validate_audit_signing_for_span_stage` — kept in sync
#: manually; matches the existing scattered-literal convention across
#: `cost_attribution_*.py`'s own `_DEFAULT_SIGNING_KEY_ID`) PLUS the
#: redaction-token map's signing key (imported from its canonical home —
#: out-of-family Codex [P1] round-3 finding: the redaction key is equally a
#: row-signing consumer at MTC, and omitting it here let a compromised
#: redaction key double as the cutover-record trust anchor).
_ROW_SIGNING_CONSUMER_KEY_IDS: frozenset[str] = frozenset(
    {
        "harness-runtime-dev",
        "harness-cost-attribution-v1",
        REDACTION_TOKEN_SIGNING_KEY_ID,
    }
)


def _canonical_kms_key_identity(arn_or_key_id: str) -> str:
    """Normalize an AWS KMS key ARN or bare key id to a comparable tail.

    A full ARN is `arn:aws:kms:<region>:<account>:key/<uuid>`; a bare key
    id is just `<uuid>`. Taking the segment after the last `/` (or the
    whole string if there is none) makes both spellings of the SAME
    physical key compare equal. Does not resolve KMS aliases or genuine
    cross-account/region equivalence — that needs a live KMS `DescribeKey`
    call this module does not make (matching `AwsKmsSigningBackend`'s own
    no-DescribeKey posture, see its module docstring).
    """
    return arn_or_key_id.rsplit("/", 1)[-1]


def validate_and_initialize_mtc_audit_signing(
    config: RuntimeConfig,
    *,
    signing_backend: SigningBackend | None,
    audit_sidecar_path: Path | None = None,
    ledger_has_audit_refs: Callable[[], bool] | None = None,
) -> None:
    """Enforce the C-RT-03 v1.101 audit-signing config-validation invariant,
    then (on success) initialize/verify the cutover record.

    Convenience wrapper composing `validate_mtc_audit_signing_config` +
    `initialize_mtc_audit_signing_record` — see each for the split
    rationale. Prefer calling them separately (as stage 4 OD does) so the
    pure config-shape checks can run BEFORE other backend-dependent
    validation (e.g. `validate_audit_signing_for_span_stage`) without
    triggering this function's side-effecting record I/O first.
    """
    validate_mtc_audit_signing_config(config)
    initialize_mtc_audit_signing_record(
        config,
        signing_backend=signing_backend,
        audit_sidecar_path=audit_sidecar_path,
        ledger_has_audit_refs=ledger_has_audit_refs,
    )


def validate_mtc_audit_signing_config(config: RuntimeConfig) -> None:
    """Pure config-shape checks — no backend I/O, no side effects.

    Raises `IncompatibleConfigVersion` for missing v1-required-at-MTC
    inputs, `AuditSigningConfigInvalidError` for invalid v2 values (see
    module docstring for the exact partition). Deliberately does NOT touch
    a constructed `SigningBackend` — every check here reads `config` alone
    — so it can run BEFORE backend-dependent validation (e.g.
    `validate_audit_signing_for_span_stage`) and before any record file is
    touched.
    """
    resolved_fail_closed = resolve_audit_signing_fail_closed(config)
    backend_configured = config.audit_signing.backend is not AuditSigningBackendKind.NONE
    is_mtc = config.persona_tier is PersonaTier.MULTI_TENANT_COMPLIANCE

    # Treat an empty/whitespace-only string as equivalent to `None` for
    # these three `str | None` fields (out-of-family Codex probe: an empty
    # `audit_ledger_binding_id=""` passed every `is None` check below, then
    # crashed `AuditCutoverRecord`'s OWN non-empty validator inside Pass 3
    # as a raw, unwrapped `ValidationError` instead of a typed rejection
    # here). `RuntimeConfig.tenant_id` already has its own field validator
    # rejecting "" — no equivalent guard exists for the record trio.
    record_path = (
        None if _is_blank(config.audit_cutover_record_path) else config.audit_cutover_record_path
    )
    record_key_id = (
        None
        if _is_blank(config.audit_cutover_record_key_id)
        else config.audit_cutover_record_key_id
    )
    record_binding_id = (
        None if _is_blank(config.audit_ledger_binding_id) else config.audit_ledger_binding_id
    )

    # --- Pass 1: MISSING v1-required-at-MTC inputs (collected, raised LAST —
    # see the precedence note above the raises below).
    missing: list[str] = []
    if resolved_fail_closed and not backend_configured:
        missing.append(
            "audit_signing.backend (audit_signing_fail_closed resolved ON at "
            f"persona_tier={config.persona_tier.value!r} but no SigningBackend "
            "is configured)"
        )
    if is_mtc:
        if config.tenant_id is None:
            missing.append("tenant_id (required at MULTI_TENANT_COMPLIANCE)")
        if record_path is None:
            missing.append("audit_cutover_record_path (required at MULTI_TENANT_COMPLIANCE)")
        if record_key_id is None:
            missing.append("audit_cutover_record_key_id (required at MULTI_TENANT_COMPLIANCE)")
        if record_binding_id is None:
            missing.append("audit_ledger_binding_id (required at MULTI_TENANT_COMPLIANCE)")

    # --- Pass 2: INVALID v2 values -> AuditSigningConfigInvalidError.
    invalid: list[str] = []
    if is_mtc and config.audit_signing_fail_closed is False:
        invalid.append(
            "audit_signing_fail_closed=false is invalid at "
            "MULTI_TENANT_COMPLIANCE — it is a non-MTC opt-in knob only"
        )
    if is_mtc and config.tenant_id is not None:
        try:
            signing_token(config.tenant_id)
        except ValueError as exc:
            # Defense in depth: `RuntimeConfig`'s own `tenant_id` field
            # validator already rejects "" / "_single" at construction time,
            # so this branch is unreachable for those two literals today —
            # kept so a future normalizer-refused token is still caught here
            # rather than only at the first tenant-bearing signature.
            invalid.append(
                f"tenant_id={config.tenant_id!r} refused by the OD tenant normalizer: {exc}"
            )

    if record_path is not None and not is_mtc:
        # Below MTC the record trio is not spec-required by default, but
        # OPTING IN (setting the path) makes key_id/binding_id required —
        # an ordinary field co-requirement, not a version-compat concern
        # (the general RT-FAIL-CONFIG "required field missing" taxonomy row).
        if record_key_id is None:
            invalid.append(
                "audit_cutover_record_key_id is required whenever audit_cutover_record_path is set"
            )
        if record_binding_id is None:
            invalid.append(
                "audit_ledger_binding_id is required whenever audit_cutover_record_path is set"
            )

    if record_path is not None and not backend_configured:
        # A record needs a real backend to be signed/verified regardless of
        # tier or the fail-closed resolution — at MTC this is already
        # implied by the resolved-ON-without-backend check above, but a
        # non-MTC opt-in (fail_closed unset/False) reaches here with no
        # other check requiring a backend (out-of-family Codex probe: this
        # combination previously hit an uncaught `AssertionError` in Pass 3
        # instead of a typed rejection here).
        invalid.append(
            "audit_signing.backend is required whenever audit_cutover_record_path is "
            "set — a record needs a real SigningBackend to be signed/verified"
        )

    if record_path is not None and record_key_id is not None:
        # Out-of-family Codex [P1] finding: the record key_id LITERALLY
        # equaling one of the known row-signing consumer key_ids (the
        # stage-5 HITL/sub-agent composers' + cost builders' shared ids —
        # mirrors `stage_4_od.py`'s `additional_key_ids` tuple; kept in
        # sync manually, matching the existing scattered-literal
        # convention across `cost_attribution_*.py`) is the SAME-entry
        # case the distinctness check below cannot see — there is no
        # "other" id to compare against when the pinned id IS the
        # row-signing id.
        if record_key_id in _ROW_SIGNING_CONSUMER_KEY_IDS:
            invalid.append(
                f"audit_cutover_record_key_id={record_key_id!r} is one of the "
                f"known row-signing consumer key ids {sorted(_ROW_SIGNING_CONSUMER_KEY_IDS)!r} "
                "— the record key must be physically distinct from every "
                "row-signing key, including this deployment's own"
            )
        resolved_arn = _resolve_record_key_arn(config, record_key_id)
        if resolved_arn is None:
            invalid.append(
                f"audit_cutover_record_key_id={record_key_id!r} does not "
                "resolve to any entry in audit_signing.key_arns"
            )
        else:
            # Out-of-family Codex [P1] finding: compare CANONICAL key
            # identities, not raw ARN strings — AWS KMS accepts both a
            # full ARN and its bare key UUID for the SAME physical key;
            # two differently-spelled logical ids for one key must not
            # pass distinctness. `_canonical_kms_key_identity` does not
            # resolve aliases or cross-account/region equivalence (that
            # needs a live KMS `DescribeKey` call this module does not
            # make, matching `AwsKmsSigningBackend`'s own no-DescribeKey
            # posture) — it closes the common ARN-vs-bare-UUID spelling gap.
            canonical_resolved = _canonical_kms_key_identity(resolved_arn)
            sharing = [
                other_id
                for other_id, other_arn in config.audit_signing.key_arns.items()
                if other_id != record_key_id
                and _canonical_kms_key_identity(other_arn) == canonical_resolved
            ]
            if sharing:
                invalid.append(
                    f"audit_cutover_record_key_id={record_key_id!r} resolves to "
                    f"the SAME backing key material as row-signing key(s) "
                    f"{sorted(sharing)!r} — the record key must be physically "
                    "distinct from every row-signing key"
                )

    # Precedence (out-of-family Codex [P2] round-6): INVALID v2 VALUES win
    # over MISSING inputs. An explicit `audit_signing_fail_closed=false` (or
    # any other v2-field misuse) PROVES the config is v2-aware — classifying
    # it as "predates the contract" (`RT-FAIL-CONFIG-VERSION`) would be
    # semantically wrong and would hide the decisive policy violation. Both
    # passes are collected before either raises so the discriminator is
    # deterministic, not first-check-wins.
    if invalid:
        raise AuditSigningConfigInvalidError(tuple(invalid))
    if missing:
        raise IncompatibleConfigVersion(tuple(missing))


def initialize_mtc_audit_signing_record(
    config: RuntimeConfig,
    *,
    signing_backend: SigningBackend | None,
    audit_sidecar_path: Path | None = None,
    ledger_has_audit_refs: Callable[[], bool] | None = None,
) -> AuditCutoverRecord | None:
    """Pass 3 — side-effecting cutover-record load-or-greenfield-init.

    Returns the AUTHENTICATED record (loaded, or the freshly-minted
    greenfield empty record) so the caller can thread it into the audit
    writer's coverage join (U-RT-139 live wiring) — `None` when no record
    path is configured.

    Split from `validate_mtc_audit_signing_config` (which MUST run first —
    it guarantees the record inputs are present and valid) so callers can
    interleave OTHER backend-dependent validation (e.g.
    `validate_audit_signing_for_span_stage`) BEFORE any record file is
    touched — avoiding a signed greenfield record being written to disk
    only for an unrelated signing-config gap to fail bootstrap moments
    later.

    `audit_sidecar_path` (the deployment's `audit-entries.jsonl` full-entry
    sidecar location, derived from the stage-1 IS ledger handle) and
    `ledger_has_audit_refs` (a lazy probe of the hash-chained IS ledger for
    `audit:` references — stage 4 passes `audit_writer.ledger_holds_audit_
    refs` over `ctx.ledger_writer`) together gate the GREENFIELD branch: the
    spec permits minting a signed EMPTY record only "when the ledger is
    fresh" (C-RT-03 v1.101 Invariants) — a missing record on a ledger that
    ALREADY HAS audit rows is trust-anchor LOSS, and silently re-minting an
    empty record would hide it while orphaning every legacy disposition
    (out-of-family Codex [P1] round-4 finding). The IS-refs probe is the
    AUTHORITY half (round-5 sharpening): a deleted/truncated sidecar
    alongside surviving hash-chained IS refs must still read NOT-fresh —
    the sidecar check alone would pass exactly the loss case the gate
    exists for. `None` skips the respective half (the production stage-4
    wiring always supplies both); a probe that RAISES reads as not-fresh
    (fail closed).
    """
    # Out-of-family Codex [P2] finding: re-apply the SAME `_is_blank`
    # normalization `validate_mtc_audit_signing_config` uses — reading
    # `config` fields raw here would let a whitespace-only
    # `audit_cutover_record_path="   "` (already normalized to "absent"
    # for validation purposes, at a non-MTC tier where nothing else
    # required it) slip through and create a record file literally named
    # `"   "` on disk.
    record_path = (
        None if _is_blank(config.audit_cutover_record_path) else config.audit_cutover_record_path
    )
    if record_path is None:
        return None
    record_key_id = (
        None
        if _is_blank(config.audit_cutover_record_key_id)
        else config.audit_cutover_record_key_id
    )
    record_binding_id = (
        None if _is_blank(config.audit_ledger_binding_id) else config.audit_ledger_binding_id
    )
    assert record_key_id is not None and record_binding_id is not None  # config validated first
    assert signing_backend is not None  # config validated first (resolved_fail_closed at MTC)

    path = Path(record_path)
    if audit_sidecar_path is not None:
        # Out-of-family Codex [P2] rounds 6+9: a record path resolving to
        # ANY audit-writer-owned file is rejected before any branch — the
        # sidecar itself (a fresh-deployment mint would corrupt
        # `audit-entries.jsonl` for the writer's first fold) AND the
        # membership-index snapshot + its `.tmp` sibling (the writer's next
        # `_write_index_snapshot_locked` replace would DESTROY the
        # authenticated record, bricking every subsequent MTC bootstrap).
        try:
            resolved = path.resolve()
            reserved_dir = audit_sidecar_path.resolve().parent
            collides = any(
                resolved == reserved_dir / name for name in AUDIT_WRITER_RESERVED_FILENAMES
            )
        except OSError:
            collides = False  # unresolvable paths cannot be proven colliding
        if collides:
            raise AuditSigningConfigInvalidError(
                (
                    f"audit_cutover_record_path={record_path!r} resolves to an "
                    "audit-writer-owned file (the audit-entries sidecar or its "
                    "index snapshot) — the cutover record must be a distinct "
                    "file the audit writer never truncates or replaces",
                )
            )
        # Out-of-family Codex [P1] round-6 finding: the spec requires the
        # pinned record key be distinct from "every key id appearing on
        # ledger rows" — the config-mapping checks in
        # `validate_mtc_audit_signing_config` cover CURRENT consumers, but a
        # HISTORICAL/custom key id persisted on existing sidecar rows (no
        # longer in `key_arns`, not in the hard-coded consumer set) would
        # otherwise pass, letting that row key's holder sign a malicious
        # exemption record. Applies to BOTH the verify and greenfield
        # branches (an existing record pinned to a row key is equally wrong).
    # B-64 close-out: hold the sidecar WRITE lock across the persisted-row
    # key scan, BOTH freshness probes, and the no-clobber publication — the
    # probes previously released their short-lived locks before
    # `_greenfield_sign_empty_record` published, so a concurrent audit
    # append landing in the probe->publish window could let an empty
    # cutover record be minted over just-written history. A sidecar
    # appender holds this same write lock for its append, so nothing can
    # land inside the window. Same-path inner reads run LOCK-FREE under
    # this hold (the `_locked` helper variants) — a nested
    # `cross_process_read_lock` on the SAME path self-deadlocks (POSIX
    # `flock` contends between fds within one process). The nested
    # `ledger_has_audit_refs` probe locks the IS STATE-LEDGER path (a
    # different inode; the dir lock's per-thread reentrant face makes the
    # same-parent nesting legal — the documented B-50 composition).
    with contextlib.ExitStack() as stack:
        if audit_sidecar_path is not None:
            try:
                stack.enter_context(cross_process_write_lock(audit_sidecar_path))
            except (OSError, ValueError) as exc:
                # Out-of-family Codex [P2] B-64 rounds 1+2: acquisition can
                # raise raw — OSError (a directory at the sidecar path,
                # permission denied) or ValueError (the lock module's
                # legacy `<sidecar>.lock` validation: FIFO / non-regular /
                # canonical-alias artifacts). Before B-64 the OSError half
                # surfaced inside the helpers' own try/except and was
                # translated; keep the RT-FAIL-CONFIG taxonomy instead of
                # leaking an unclassified bootstrap exception. (No
                # double-wrap risk: `AuditSigningConfigInvalidError` IS a
                # ValueError subclass but cannot originate from the
                # harness-is lock module.)
                raise AuditSigningConfigInvalidError(
                    (
                        f"audit sidecar {str(audit_sidecar_path)!r} could not be "
                        f"locked for the record probe->publish window ({exc}) — "
                        "cannot serialize against concurrent audit appends",
                    )
                ) from exc
            _reject_record_key_used_by_persisted_rows_locked(
                config, sidecar_path=audit_sidecar_path, record_key_id=record_key_id
            )
        if path.is_file():
            return _verify_existing_record(
                path,
                expected_key_id=record_key_id,
                expected_ledger_binding_id=record_binding_id,
                signing_backend=signing_backend,
            )
        # Out-of-family Codex [P2] round-3 finding: `not is_file()` alone
        # conflates "nothing there yet" (genuine greenfield) with "something
        # there that is NOT a regular file" — a directory (untyped
        # `IsADirectoryError` at the rename, temp file left behind), a
        # FIFO/special file, or a broken symlink (which `os.replace` would
        # silently overwrite). Only a genuinely-absent path is greenfield;
        # anything else is a typed configuration rejection, never overwritten.
        if path.exists() or path.is_symlink():
            raise AuditSigningConfigInvalidError(
                (
                    f"audit_cutover_record_path={record_path!r} exists but is not a "
                    "regular file (directory, special file, or broken symlink) — "
                    "refusing to treat it as a greenfield record or overwrite it",
                )
            )
        # Ledger-freshness gate (out-of-family Codex [P1] round-4 + round-5):
        # greenfield empty-record minting is permitted ONLY for a fresh ledger.
        # Two halves — the sidecar rows check AND the hash-chained IS ledger's
        # `audit:` refs (the AUTHORITY: a plain sidecar file can be deleted or
        # truncated, the IS chain cannot be silently emptied). Either half
        # firing means the missing record is trust-anchor LOSS — surface it,
        # never paper over it.
        not_fresh = audit_sidecar_path is not None and _sidecar_has_rows_locked(audit_sidecar_path)
        if not not_fresh and ledger_has_audit_refs is not None:
            try:
                not_fresh = ledger_has_audit_refs()
            except Exception:
                # Fail closed: an IS ledger that cannot be read cannot PROVE
                # freshness, and minting a trust anchor over unknown history is
                # the exact hazard this gate forecloses.
                not_fresh = True
        if not_fresh:
            raise AuditSigningConfigInvalidError(
                (
                    f"audit_cutover_record_path={record_path!r} does not exist but "
                    "the deployment's audit history is NOT fresh (the sidecar "
                    "carries rows and/or the hash-chained IS ledger holds audit "
                    "references) — the missing record is trust-anchor loss; "
                    "refusing to mint a fresh empty record over it (the spec "
                    "permits empty-record initialization only when the ledger is "
                    "fresh)",
                )
            )
        return _greenfield_sign_empty_record(
            path,
            key_id=record_key_id,
            ledger_binding_id=record_binding_id,
            signing_backend=signing_backend,
        )


def _sidecar_has_rows_locked(sidecar_path: Path) -> bool:
    """True iff the `audit-entries.jsonl` sidecar exists and carries at
    least one non-blank row. Read-only; an unreadable sidecar is treated as
    HAVING rows (fail closed — refusing a greenfield mint is the safe
    direction when freshness cannot be proven).

    CALLER-HELD-LOCK INVARIANT (B-64): the sole caller
    (`initialize_mtc_audit_signing_record`) holds
    `cross_process_write_lock(sidecar_path)` across this probe and the
    greenfield publication — a stronger exclusion than the shared read
    lock this helper used to take itself (writers hold the same write
    lock, so no partially flushed row is observable). Taking a nested
    read lock here would self-deadlock: POSIX `flock` contends between
    fds within one process."""
    if not sidecar_path.is_file():
        return False
    try:
        with sidecar_path.open("r", encoding="utf-8") as handle:
            return any(line.strip() for line in handle)
    except OSError:
        return True


def _reject_record_key_used_by_persisted_rows(  # pyright: ignore[reportUnusedFunction] — consumed cross-module by admin/record_migration.py (shared trust-anchor component)
    config: RuntimeConfig, *, sidecar_path: Path, record_key_id: str
) -> None:
    """Reject a record key that any PERSISTED sidecar row already signed
    under (out-of-family Codex [P1] round-6; spec text: the pinned id "MUST
    be DISTINCT from every key id appearing on ledger rows").

    LOCKING WRAPPER (B-64 split): holds the IS-shared READ lock for the
    complete scan ([P2] round-7 — sidecar writers hold the matching write
    lock, so an unlocked read could parse a partially flushed final row
    and report a permanent RT-FAIL-CONFIG for an otherwise valid ledger).
    For callers that already hold a lock on `sidecar_path` (the B-64
    bootstrap window in `initialize_mtc_audit_signing_record`), use the
    `_locked` core directly — calling THIS wrapper under a held same-path
    lock self-deadlocks (POSIX `flock` contends between fds within one
    process; the `record_migration.py` retag ordering comment depends on
    the same fact).
    """
    if not sidecar_path.is_file():
        return
    try:
        with cross_process_read_lock(sidecar_path):
            _reject_record_key_used_by_persisted_rows_locked(
                config, sidecar_path=sidecar_path, record_key_id=record_key_id
            )
    except OSError as exc:
        # Lock acquisition itself failed — same typed fail-closed surface
        # as an unreadable sidecar (separation cannot be proven).
        raise AuditSigningConfigInvalidError(
            (
                f"audit sidecar {str(sidecar_path)!r} could not be read ({exc}) "
                "— cannot prove the record key is distinct from every persisted "
                "row-signing key",
            )
        ) from exc


def _reject_record_key_used_by_persisted_rows_locked(
    config: RuntimeConfig, *, sidecar_path: Path, record_key_id: str
) -> None:
    """Lock-free scan core of `_reject_record_key_used_by_persisted_rows`.

    Compares logical key ids directly, plus canonical backing material when
    the row's id resolves through `config.audit_signing.key_arns`. A
    sidecar row that cannot be parsed is fail-closed: separation cannot be
    PROVEN over unreadable history, so the record key is refused.

    CALLER-HELD-LOCK INVARIANT (B-64): the caller holds a
    `cross_process_read_lock` (the wrapper above) or
    `cross_process_write_lock` (`initialize_mtc_audit_signing_record`'s
    probe->publish window) on `sidecar_path` for the complete scan.
    """
    if not sidecar_path.is_file():
        return
    record_arn = _resolve_record_key_arn(config, record_key_id)
    record_material = _canonical_kms_key_identity(record_arn) if record_arn is not None else None
    try:
        with sidecar_path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    row: object = json.loads(line)
                    if isinstance(row, dict) and "legacy_baseline" in row:
                        # `adopt_legacy_is_refs()` baseline rows (out-of-family
                        # Codex [P1] round-8) — pre-sidecar IS refs whose full
                        # entries the old runtime dropped. Legitimate, carry NO
                        # `entry` and therefore no row-signing key to compare;
                        # the audit writer's own fold path skips them the same
                        # way (`audit_writer.py` `"legacy_baseline" in row`).
                        continue
                    row_key_id: object = row["entry"]["signature_attrs"][  # type: ignore[index]
                        "audit_signature_key_id"
                    ]
                except (ValueError, KeyError, TypeError) as exc:
                    raise AuditSigningConfigInvalidError(
                        (
                            f"audit sidecar {str(sidecar_path)!r} line {line_number} "
                            f"is unparseable ({type(exc).__name__}) — cannot prove "
                            "the record key is distinct from every persisted "
                            "row-signing key; refusing the pinned "
                            f"audit_cutover_record_key_id={record_key_id!r}",
                        )
                    ) from exc
                if not isinstance(row_key_id, str):
                    # Out-of-family Codex [P1] round-7: a null/int key id is
                    # equally unprovable history — fail closed, never skip.
                    bad_type_name = type(row_key_id).__name__  # type: ignore[reportUnknownVariableType]
                    raise AuditSigningConfigInvalidError(
                        (
                            f"audit sidecar {str(sidecar_path)!r} line {line_number} "
                            f"carries a non-string audit_signature_key_id "
                            f"({bad_type_name}) — cannot prove the "
                            "record key is distinct from every persisted "
                            "row-signing key; refusing the pinned "
                            f"audit_cutover_record_key_id={record_key_id!r}",
                        )
                    )
                same_logical = row_key_id == record_key_id
                row_arn = _resolve_record_key_arn(config, row_key_id)
                if row_arn is None:
                    # Out-of-family Codex [P1] round-8: an unmapped historical
                    # row key makes PHYSICAL distinctness unprovable — a
                    # deployment could map the record key to the same KMS key
                    # a since-removed logical row id used and pass. Fail
                    # closed; the operator remedy is adding the historical
                    # id's ARN to `audit_signing.key_arns` (a documentation
                    # mapping — nothing signs under it). (Placeholder-era rows
                    # carry `unsigned:*` only in the signature VALUE — their
                    # key_id field is a real id, so no carve-out is needed.)
                    raise AuditSigningConfigInvalidError(
                        (
                            f"persisted audit row (sidecar line {line_number}) was "
                            f"signed under key id {row_key_id!r}, which has no "
                            "entry in audit_signing.key_arns — physical "
                            "distinctness from the pinned "
                            f"audit_cutover_record_key_id={record_key_id!r} cannot "
                            "be proven; add the historical key's ARN to key_arns "
                            "so separation is verifiable",
                        )
                    )
                same_material = (
                    record_material is not None
                    and _canonical_kms_key_identity(row_arn) == record_material
                )
                if same_logical or same_material:
                    raise AuditSigningConfigInvalidError(
                        (
                            f"audit_cutover_record_key_id={record_key_id!r} was "
                            f"already used to sign persisted audit row(s) (e.g. "
                            f"sidecar line {line_number}, key id {row_key_id!r}) "
                            "— the record key must be distinct from every key id "
                            "appearing on ledger rows",
                        )
                    )
    except OSError as exc:
        raise AuditSigningConfigInvalidError(
            (
                f"audit sidecar {str(sidecar_path)!r} could not be read ({exc}) "
                "— cannot prove the record key is distinct from every persisted "
                "row-signing key",
            )
        ) from exc


def _greenfield_sign_empty_record(
    path: Path,
    *,
    key_id: str,
    ledger_binding_id: str,
    signing_backend: SigningBackend,
) -> AuditCutoverRecord:
    """Sign + write a fresh, empty `AuditCutoverRecord` (codex round-30/51).

    Returns the minted record for the caller's live-writer wiring."""
    try:
        algorithm = SignatureAlgorithm(signing_backend.algorithm)
    except ValueError as exc:
        raise AuditSigningConfigInvalidError(
            (
                f"signing_backend.algorithm={signing_backend.algorithm!r} is not a "
                "recognized SignatureAlgorithm",
            )
        ) from exc
    try:
        record = AuditCutoverRecord(
            schema_version=1,
            authored_at=datetime.now(UTC),
            algorithm=algorithm,
            key_id=key_id,
            ledger_binding_id=ledger_binding_id,
            rows=(),
        )
    except ValidationError as exc:
        # Defense in depth: `validate_mtc_audit_signing_config`'s own
        # `_is_blank` checks already reject an empty `key_id`/
        # `ledger_binding_id` before this function is ever reached — this
        # catch guards against `AuditCutoverRecord`'s OWN invariants
        # (out-of-family Codex probe: an unwrapped `ValidationError` from
        # this construction previously leaked past the typed taxonomy).
        raise AuditSigningConfigInvalidError(
            (f"greenfield cutover-record construction failed: {exc}",)
        ) from exc
    try:
        signature = sign_cutover_record(record, backend=signing_backend)
    except CutoverRecordValidationError as exc:
        raise AuditSigningConfigInvalidError(
            (f"greenfield cutover-record signing failed: {exc}",)
        ) from exc
    # Out-of-family Codex [P1] round-5 finding: round-trip the fresh
    # signature through the VERIFIER before publishing — a backend that can
    # sign but not verify (AWS KMS `Sign` and `Verify` are separate IAM
    # permissions), or a faulty backend emitting a wrong-but-correctly-sized
    # signature, would otherwise persist a record that THIS bootstrap
    # accepts and every SUBSEQUENT bootstrap rejects.
    try:
        round_trip_ok = verify_cutover_record_signature(record, signature, backend=signing_backend)
    except Exception as exc:
        raise AuditSigningConfigInvalidError(
            (
                f"greenfield cutover-record verification round-trip RAISED "
                f"({type(exc).__name__}: {exc}) — a backend that can sign but "
                "not verify (e.g. missing the KMS Verify permission) must fail "
                "THIS bootstrap, not every subsequent one",
            )
        ) from exc
    if not round_trip_ok:
        raise AuditSigningConfigInvalidError(
            (
                "greenfield cutover-record signature failed its own "
                "verification round-trip — refusing to publish a trust anchor "
                "this deployment cannot verify",
            )
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = record.model_dump_json() + "\n" + signature.hex() + "\n"
    # Out-of-family Codex [P2] round-2 finding: write-then-atomic-rename,
    # not a direct `write_text` — a crash or a concurrent reader mid-write
    # would otherwise leave a partial/truncated trust-anchor file that every
    # later bootstrap rejects as unparseable. Out-of-family Codex [P1]
    # round-4 sharpening: the temp file is created via `tempfile.mkstemp`
    # (randomized name, O_CREAT|O_EXCL, mode 0600) rather than a
    # PREDICTABLE `.{name}.tmp-{pid}` sibling — a co-located local
    # principal could pre-create the predictable name as a symlink, have
    # the runtime's `write_text` follow it (overwriting the symlink's
    # target with runtime privileges), then have `os.replace` move the
    # symlink itself into the trusted record path. `mkstemp` never follows
    # an existing entry; the fd is fsynced before the atomic rename so the
    # renamed file's CONTENT is durable, not just its directory entry.
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.tmp-")
    lost_publication_race = False
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        # Out-of-family Codex [P1] round-7 finding: NO-CLOBBER publication
        # via `os.link` (fails with FileExistsError when the target exists)
        # instead of an unconditional `os.replace` — two concurrent first
        # bootstraps could both observe the record absent, both sign, and
        # the second replace would silently swap the trust anchor out from
        # under the first winner. The loser keeps the WINNER's record and
        # verifies it below instead (both processes converge on ONE anchor).
        try:
            os.link(tmp_name, path)
        except FileExistsError:
            lost_publication_race = True
        # Out-of-family Codex [P2] round-5 finding: fsync the PARENT
        # DIRECTORY after publication (mirrors the audit-writer's own
        # snapshot persistence) — fsyncing only the file's content leaves
        # the new directory entry non-durable; a power loss after LATER
        # sidecar writes became durable could vanish the record while audit
        # rows survive, making every subsequent bootstrap reject the ledger
        # as non-fresh.
        if not lost_publication_race and sys.platform != "win32":
            dir_fd = os.open(str(path.parent), os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
    finally:
        with contextlib.suppress(OSError):
            os.unlink(tmp_name)
    if lost_publication_race:
        # The winner's record must still be one THIS config + backend
        # accepts — a lost race converges, it never silently diverges.
        return _verify_existing_record(
            path,
            expected_key_id=key_id,
            expected_ledger_binding_id=ledger_binding_id,
            signing_backend=signing_backend,
        )
    return record


def _verify_existing_record(
    path: Path,
    *,
    expected_key_id: str,
    expected_ledger_binding_id: str,
    signing_backend: SigningBackend,
) -> AuditCutoverRecord:
    """Load + fail-closed-verify an on-disk cutover record against config.

    Returns the VERIFIED record (U-RT-139 live-writer wiring — the
    coverage join consults its `_single`→tenant aliases; the signed record
    is the alias AUTHORITY, never a free-standing mapping file)."""
    try:
        raw = path.read_text(encoding="utf-8")
        lines = raw.splitlines()
        # Out-of-family Codex [P2] round-6 finding: require EXACTLY one
        # record line + one signature line (aside from the final newline) —
        # a starred unpack would silently discard trailing lines, letting
        # arbitrary unsigned content ride along in an accepted trust-anchor
        # file despite the fail-closed tamper contract.
        if len(lines) != 2:
            raise ValueError(f"expected exactly 2 lines (record + signature), found {len(lines)}")
        record_line, signature_line = lines
        record = AuditCutoverRecord.model_validate_json(record_line)
        signature = bytes.fromhex(signature_line)
    except (OSError, ValueError, ValidationError) as exc:
        raise AuditSigningConfigInvalidError(
            (f"audit_cutover_record_path={str(path)!r} is unparseable: {exc}",)
        ) from exc

    invalid: list[str] = []
    if record.key_id != expected_key_id:
        invalid.append(
            f"cutover record key_id={record.key_id!r} disagrees with the "
            f"pinned audit_cutover_record_key_id={expected_key_id!r}"
        )
    if record.algorithm.value != signing_backend.algorithm:
        invalid.append(
            f"cutover record algorithm={record.algorithm.value!r} disagrees "
            f"with the configured backend's algorithm={signing_backend.algorithm!r} "
            "— the algorithm authority is the mapping/backend, never the "
            "record's own metadata"
        )
    if record.ledger_binding_id != expected_ledger_binding_id:
        invalid.append(
            f"cutover record ledger_binding_id={record.ledger_binding_id!r} "
            f"disagrees with the configured audit_ledger_binding_id="
            f"{expected_ledger_binding_id!r}"
        )
    if invalid:
        raise AuditSigningConfigInvalidError(tuple(invalid))

    if not verify_cutover_record_signature(record, signature, backend=signing_backend):
        raise AuditSigningConfigInvalidError(
            (
                f"audit_cutover_record_path={str(path)!r} failed signature "
                "verification against its trust anchor — tampered, forged, or "
                "signed under different key material",
            )
        )
    return record
