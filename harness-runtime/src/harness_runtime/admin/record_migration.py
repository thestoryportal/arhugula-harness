"""`U-RT-139` — `migrate-audit-sidecar` record modes (authoring / retag).

Runtime plan v2.49 §1.7: the migration subcommand's record-driven halves —

- **Authoring** (`author_cutover_record`): compose the signed cutover
  record from EVERY observed pre-cutover identity (baseline pairs,
  `"_single"` full-entry rows, already-tenant-tagged v1.33-era full rows)
  given the operator's tenant-binding input, run full carrier validation,
  sign under the pinned record key through the configured backend, emit
  the 2-line record file.
- **Retag** (`retag_sidecar`): AUTHENTICATE the record first (typed
  rejection, ZERO tags changed — never treated as absent, never partial),
  then rewrite ONLY `"_single"`-tagged sidecar rows the record
  dispositions TENANT-READABLE (`placeholder_exempt`/`four_tuple_real`;
  never `quarantined`) to their attested `tenant_scope` — entry content
  and `entry_hash` byte-unchanged (the tag lives in the sidecar wrapper
  outside the hash). All-or-nothing: temp file + fsync + `os.replace`
  under the B-46 `cross_process_replace_lock`, with the membership-index
  snapshot removed in the same pass (the next fold rebuilds from the
  rewritten sidecar — a stale snapshot over a replaced inode is exactly
  the derived-cache case whose correct lifecycle is discard-and-refold).

Authentication + record-trust checks REUSE the U-RT-134 bootstrap
component (`_verify_existing_record` + `_reject_record_key_used_by_
persisted_rows`) — one implementation of the trust anchor, never a
re-derivation (plan: "the shared record-authentication component lands
with U-RT-138 and U-RT-139 consumes it whole").

Rewriting the paired IS-reference identity is PROHIBITED (the
`audit:<tag>:<hash>` action id participates in the entry response hash and
every later ledger entry chains to it) — the record-derived ALIAS consulted
by the writer's coverage join (part A of this unit) is the only
append-only-compatible mechanism.
"""

from __future__ import annotations

import contextlib
import json
import os
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, cast

from harness_is.cross_process_ledger_lock import cross_process_replace_lock
from harness_od.audit_cutover_record import (
    AuditCutoverRecord,
    AuditCutoverRecordRow,
    CutoverRecordValidationError,
    VerificationDisposition,
    sign_cutover_record,
    verify_cutover_record_signature,
)
from harness_od.audit_ledger_types import AuditLedgerEntry, compute_entry_hash

from harness_runtime.lifecycle.audit_signing_fail_closed_validation import (
    AuditSigningConfigInvalidError,
    _reject_record_key_used_by_persisted_rows,  # pyright: ignore[reportPrivateUsage]  # shared trust-anchor component
    _verify_existing_record,  # pyright: ignore[reportPrivateUsage]  # shared trust-anchor component
)
from harness_runtime.lifecycle.audit_writer import (
    AUDIT_SNAPSHOT_FILENAME,
    AUDIT_WRITER_RESERVED_FILENAMES,
)

if TYPE_CHECKING:
    from harness_cp.f5_signing_key_resolution import SigningBackend

    from harness_runtime.types import RuntimeConfig

__all__ = [
    "RecordMigrationError",
    "RetagOutcome",
    "author_cutover_record",
    "retag_sidecar",
]

_SINGLE_TAG = "_single"
_PLACEHOLDER_SIGNATURE_PREFIX = "unsigned:"

_TENANT_READABLE = (
    VerificationDisposition.PLACEHOLDER_EXEMPT,
    VerificationDisposition.FOUR_TUPLE_REAL,
)


class RecordMigrationError(Exception):
    """Typed refusal — authoring/retag stopped with ZERO changes on disk."""


@dataclass(frozen=True)
class RetagOutcome:
    retagged: int
    quarantined_left: int
    already_tagged_left: int
    baseline_aliased: int


@dataclass(frozen=True)
class _SidecarRows:
    """Raw parsed sidecar lines, order-preserving."""

    lines: tuple[dict[str, object], ...]

    def single_full_identities(self) -> list[tuple[str, AuditLedgerEntry]]:
        out: list[tuple[str, AuditLedgerEntry]] = []
        for row in self.lines:
            if "legacy_baseline" in row:
                continue
            tag = cast("str", row["tenant_tag"])
            entry = AuditLedgerEntry.model_validate(row["entry"])
            out.append((tag, entry))
        return out

    def baseline_pairs(self) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []
        for row in self.lines:
            if "legacy_baseline" not in row:
                continue
            for pair in cast("list[list[str]]", row["legacy_baseline"]):
                out.append((pair[0], pair[1]))
        return out


def _read_sidecar_rows(sidecar_path: Path) -> _SidecarRows:
    """Read-only, fail-loud parse of every sidecar line.

    Opens the sidecar with the WRITER's regular-file/no-follow posture
    (codex round-4 P1: a symlinked sidecar would let author/retag sign or
    import attacker-selected history the writer itself refuses), refuses a
    torn tail (an unterminated final line is an UNCOMMITTED fragment the
    writer's heal contract discards — migration must never promote it),
    and applies the writer's content-recompute + duplicate-identity checks
    so a sidecar the next fold would reject is refused BEFORE anything is
    signed or replaced.
    """
    if sidecar_path.is_symlink():
        raise RecordMigrationError(
            f"sidecar {sidecar_path} is a symlink — migration reads only the "
            f"writer-owned regular file, never a redirection"
        )
    try:
        nofollow = getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(str(sidecar_path), os.O_RDONLY | nofollow)
    except OSError as exc:
        raise RecordMigrationError(f"sidecar {sidecar_path} unreadable: {exc}") from exc
    try:
        stat_result = os.fstat(fd)
        import stat as _stat

        if not _stat.S_ISREG(stat_result.st_mode):
            raise RecordMigrationError(f"sidecar {sidecar_path} is not a regular file — refusing")
        with os.fdopen(fd, encoding="utf-8") as handle:
            fd = -1
            text = handle.read()
    except OSError as exc:
        raise RecordMigrationError(f"sidecar {sidecar_path} unreadable: {exc}") from exc
    finally:
        if fd >= 0:
            os.close(fd)
    if text and not text.endswith("\n"):
        raise RecordMigrationError(
            f"sidecar {sidecar_path} ends in an unterminated line — a torn "
            f"tail is an uncommitted fragment (the writer's heal contract "
            f"discards it); run the harness once to heal, then re-run the "
            f"migration"
        )
    lines: list[dict[str, object]] = []
    seen_full_identities: set[tuple[str, str]] = set()
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            parsed: object = json.loads(line)
        except ValueError as exc:
            raise RecordMigrationError(
                f"sidecar line {line_number} is not valid JSON: {exc} — refusing "
                f"to migrate unprovable history"
            ) from exc
        if not isinstance(parsed, dict):
            raise RecordMigrationError(f"sidecar line {line_number} is not a JSON object")
        row = cast("dict[str, object]", parsed)
        if "legacy_baseline" in row:
            if "entry" in row or "tenant_tag" in row:
                raise RecordMigrationError(
                    f"sidecar line {line_number}: mixed baseline/full-entry row "
                    f"shapes — external mutation; refusing"
                )
        elif not isinstance(row.get("tenant_tag"), str) or not isinstance(row.get("entry"), dict):
            raise RecordMigrationError(
                f"sidecar line {line_number} lacks tenant_tag/entry — refusing"
            )
        else:
            # Writer-equivalent integrity at parse (codex round-4 P2): a
            # stale-hash payload or duplicate identity would let the retag
            # report success and replace the file the next fold rejects.
            entry = AuditLedgerEntry.model_validate(row["entry"])
            recomputed = compute_entry_hash(entry.payload)
            if recomputed != entry.entry_hash:
                raise RecordMigrationError(
                    f"sidecar line {line_number} fails content-integrity: "
                    f"stored entry_hash={entry.entry_hash!r} but recomputed "
                    f"{recomputed!r} — tampered or corrupt row; refusing"
                )
            identity = (cast("str", row["tenant_tag"]), entry.entry_hash)
            if identity in seen_full_identities:
                raise RecordMigrationError(
                    f"sidecar line {line_number}: duplicate identity "
                    f"{identity!r} — external mutation; refusing"
                )
            seen_full_identities.add(identity)
        lines.append(row)
    return _SidecarRows(lines=tuple(lines))


def _record_trust_inputs(config: RuntimeConfig) -> tuple[Path, str, str]:
    """The C-RT-03 record-trust triple, all REQUIRED for record modes."""
    missing = [
        name
        for name, value in (
            ("audit_cutover_record_path", config.audit_cutover_record_path),
            ("audit_cutover_record_key_id", config.audit_cutover_record_key_id),
            ("audit_ledger_binding_id", config.audit_ledger_binding_id),
        )
        if value is None or not str(value).strip()
    ]
    if missing:
        raise RecordMigrationError(
            f"record modes require the config record-trust inputs; missing: {', '.join(missing)}"
        )
    return (
        Path(cast("str", config.audit_cutover_record_path)),
        cast("str", config.audit_cutover_record_key_id),
        cast("str", config.audit_ledger_binding_id),
    )


_MIGRATION_TEMP_SUFFIXES = (".retag.tmp", ".author.tmp")


def _reject_reserved_record_path(record_path: Path, *, sidecar_path: Path) -> None:
    """The record path must never alias a writer- or migration-owned file
    (codex round-3 P1: `audit-entries.jsonl.retag.tmp` as the record path
    let the retag's stale-temp cleanup DELETE the trust anchor it had just
    authenticated). Mirrors bootstrap's own reserved-filename rejection,
    extended with this module's temp names."""
    reserved = set(AUDIT_WRITER_RESERVED_FILENAMES)
    for suffix in _MIGRATION_TEMP_SUFFIXES:
        reserved.add(sidecar_path.name + suffix)
    reserved.add(sidecar_path.name)
    try:
        resolved = record_path.resolve()
        reserved_dir = sidecar_path.resolve().parent
        collides = any(resolved == reserved_dir / name for name in reserved)
    except OSError:
        collides = False
    if collides:
        raise RecordMigrationError(
            f"audit_cutover_record_path={str(record_path)!r} resolves to a "
            f"writer- or migration-owned file — the trust anchor must be a "
            f"distinct file nothing here truncates, replaces, or unlinks"
        )


def _validate_signing_config(config: RuntimeConfig, *, signing_backend: SigningBackend) -> None:
    """Run the FULL bootstrap config-shape validation before any record-mode
    side effect (codex round-1 P1: a config normal bootstrap would reject —
    e.g. record key sharing a row key's backing material — must not author
    or retag first and brick the deployment after)."""
    from harness_runtime.lifecycle.audit_signing_fail_closed_validation import (
        IncompatibleConfigVersion,
        validate_mtc_audit_signing_config,
    )
    from harness_runtime.lifecycle.span_processor import (
        SpanProcessorBindError,
        validate_audit_signing_for_span_stage,
    )

    try:
        validate_mtc_audit_signing_config(config)
        validate_audit_signing_for_span_stage(
            config,
            signing_backend=signing_backend,
            tokenizer_will_bind=True,
            additional_key_ids=("harness-runtime-dev", "harness-cost-attribution-v1"),
        )
    except (
        AuditSigningConfigInvalidError,
        IncompatibleConfigVersion,
        SpanProcessorBindError,
    ) as exc:
        raise RecordMigrationError(
            f"signing config would be rejected at bootstrap — refusing record "
            f"modes against it: {exc}"
        ) from exc


def _authenticate_record(
    config: RuntimeConfig,
    *,
    sidecar_path: Path,
    signing_backend: SigningBackend,
) -> AuditCutoverRecord:
    """Authenticate the configured record via the SHARED U-RT-134 component.

    Typed refusal on any trust failure — a record failing authentication is
    REJECTED, never treated as absent (absent-record fallback would silently
    downgrade exemption/era decisions), and ZERO tags are changed.
    """
    record_path, record_key_id, binding_id = _record_trust_inputs(config)
    _reject_reserved_record_path(record_path, sidecar_path=sidecar_path)
    if not record_path.is_file():
        raise RecordMigrationError(
            f"cutover record not found at {record_path} — the retag mode "
            f"requires an existing AUTHENTICATED record (author one first)"
        )
    try:
        _reject_record_key_used_by_persisted_rows(
            config, sidecar_path=sidecar_path, record_key_id=record_key_id
        )
        return _verify_existing_record(
            record_path,
            expected_key_id=record_key_id,
            expected_ledger_binding_id=binding_id,
            signing_backend=signing_backend,
        )
    except AuditSigningConfigInvalidError as exc:
        raise RecordMigrationError(f"cutover record REJECTED (zero tags changed): {exc}") from exc


# ---------------------------------------------------------------------------
# Retag mode.
# ---------------------------------------------------------------------------


def retag_sidecar(
    config: RuntimeConfig,
    *,
    sidecar_path: Path,
    signing_backend: SigningBackend,
) -> RetagOutcome:
    """OD v1.34 §21.2.1 row-6 retag, driven by the authenticated record."""
    _validate_signing_config(config, signing_backend=signing_backend)
    record = _authenticate_record(
        config, sidecar_path=sidecar_path, signing_backend=signing_backend
    )
    if not sidecar_path.is_file():
        raise RecordMigrationError(f"sidecar not found at {sidecar_path} — nothing to retag")
    # The B-46 exclusion spans the ENTIRE read→validate→compose→replace
    # section (codex round-2 P1): a writer appending between an unlocked
    # read and the replacement would have its row silently deleted by the
    # stale snapshot while its IS reference survives.
    with cross_process_replace_lock(sidecar_path):
        return _retag_locked(record, sidecar_path=sidecar_path)


def _retag_locked(record: AuditCutoverRecord, *, sidecar_path: Path) -> RetagOutcome:
    rows = _read_sidecar_rows(sidecar_path)

    single_rows = {(row.source_tag, row.entry_hash): row for row in record.rows}

    # RECORD COMPLETENESS: every observed leftover "_single" identity —
    # full-entry rows AND baseline pairs (compared in the record's
    # (tenant_scope, entry_hash) space via the alias projection) — must be
    # dispositioned, or the retag REFUSES with zero changes.
    undispositioned: list[tuple[str, str]] = []
    for tag, entry in rows.single_full_identities():
        if tag == _SINGLE_TAG and (_SINGLE_TAG, entry.entry_hash) not in single_rows:
            undispositioned.append((tag, entry.entry_hash))
    for tag, entry_hash in rows.baseline_pairs():
        if tag == _SINGLE_TAG and (_SINGLE_TAG, entry_hash) not in single_rows:
            undispositioned.append((tag, entry_hash))
    if undispositioned:
        raise RecordMigrationError(
            f"{len(undispositioned)} observed '_single' identity(ies) the "
            f"record does not disposition — refusing to retag (era is never "
            f"observation-inferred): " + ", ".join(f"({t!r}, {h!r})" for t, h in undispositioned)
        )

    # Destination-collision refusal (codex round-2 P1): a retag target
    # `(tenant_scope, H)` colliding with an OBSERVED sidecar identity would
    # mint duplicate destination rows the next fold rejects — refuse with
    # zero changes instead of reporting a success that bricks the ledger.
    observed_identities: set[tuple[str, str]] = set()
    for tag, entry in rows.single_full_identities():
        observed_identities.add((tag, entry.entry_hash))
    for tag, entry_hash in rows.baseline_pairs():
        observed_identities.add((tag, entry_hash))
    collisions: list[tuple[str, str]] = []
    for tag, entry in rows.single_full_identities():
        if tag != _SINGLE_TAG:
            continue
        record_row = single_rows.get((_SINGLE_TAG, entry.entry_hash))
        if record_row is None or record_row.verification_disposition not in _TENANT_READABLE:
            continue
        destination = (record_row.tenant_scope, entry.entry_hash)
        if destination in observed_identities:
            collisions.append(destination)
    # Baseline alias DESTINATIONS collide too (codex round-4 P1): a
    # baseline pair aliasing onto an occupied tenant identity omitted from
    # the record would conflate the baseline with an unrelated full row.
    for tag, entry_hash in rows.baseline_pairs():
        if tag != _SINGLE_TAG:
            continue
        record_row = single_rows.get((_SINGLE_TAG, entry_hash))
        if record_row is None or record_row.verification_disposition not in _TENANT_READABLE:
            continue
        destination = (record_row.tenant_scope, entry_hash)
        if destination in observed_identities:
            collisions.append(destination)
    if collisions:
        raise RecordMigrationError(
            f"{len(collisions)} retag destination(s) collide with observed "
            f"sidecar identity(ies) — refusing to retag (a duplicate "
            f"destination row would fail the next fold): "
            + ", ".join(f"({t!r}, {h!r})" for t, h in collisions)
        )

    # Compose the rewritten lines (entry content + entry_hash byte-unchanged;
    # ONLY the wrapper tenant_tag moves, and only for TENANT-READABLE
    # dispositions — QUARANTINED "_single" rows are NEVER retagged).
    retagged = 0
    quarantined_left = 0
    already_tagged_left = 0
    new_lines: list[str] = []
    for row in rows.lines:
        if "legacy_baseline" in row:
            new_lines.append(json.dumps(row))
            continue
        tag = cast("str", row["tenant_tag"])
        entry_obj = cast("dict[str, object]", row["entry"])
        entry_hash = cast("str", entry_obj["entry_hash"])
        if tag != _SINGLE_TAG:
            already_tagged_left += 1
            new_lines.append(json.dumps(row))
            continue
        record_row = single_rows.get((_SINGLE_TAG, entry_hash))
        assert record_row is not None  # completeness enforced above
        if record_row.verification_disposition in _TENANT_READABLE:
            rewritten = dict(row)
            rewritten["tenant_tag"] = record_row.tenant_scope
            new_lines.append(json.dumps(rewritten))
            retagged += 1
        else:
            quarantined_left += 1
            new_lines.append(json.dumps(row))

    baseline_aliased = sum(
        1
        for tag, entry_hash in rows.baseline_pairs()
        if tag == _SINGLE_TAG
        and single_rows[(_SINGLE_TAG, entry_hash)].verification_disposition in _TENANT_READABLE
    )

    _atomic_replace_sidecar(sidecar_path, "\n".join(new_lines) + ("\n" if new_lines else ""))
    return RetagOutcome(
        retagged=retagged,
        quarantined_left=quarantined_left,
        already_tagged_left=already_tagged_left,
        baseline_aliased=baseline_aliased,
    )


def _atomic_replace_sidecar(sidecar_path: Path, content: str) -> None:
    """All-or-nothing sidecar rewrite under the B-46 cross-process exclusion.

    Temp file in the same directory + fsync + `os.replace` + dir fsync — an
    interruption after N of M rows leaves the ORIGINAL sidecar byte-intact
    (the temp file is unpublished); after the replace, the file is fully
    retagged. Never mixed. The membership-index snapshot is removed inside
    the same exclusion so the next fold rebuilds from the rewritten sidecar.
    """
    # Caller (`retag_sidecar`) holds the B-46 replace lock across the whole
    # read+compose+replace section.
    tmp_path = sidecar_path.with_name(sidecar_path.name + ".retag.tmp")
    # A stale tmp from a prior crash is removed, then the file is created
    # EXCLUSIVELY (never truncate-in-place: a pre-created hard link to
    # the ledger or sidecar would be destroyed by O_TRUNC — codex
    # round-1 P1) with O_NOFOLLOW guarded for Windows.
    with contextlib.suppress(OSError):
        os.unlink(tmp_path)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(str(tmp_path), os.O_WRONLY | os.O_CREAT | os.O_EXCL | nofollow, 0o600)
    stat_result = os.fstat(fd)
    import stat as _stat

    if not _stat.S_ISREG(stat_result.st_mode) or stat_result.st_nlink != 1:
        os.close(fd)
        with contextlib.suppress(OSError):
            os.unlink(tmp_path)
        raise RecordMigrationError(
            f"retag temp file {tmp_path} is not a fresh regular file "
            f"(mode={stat_result.st_mode:o}, nlink={stat_result.st_nlink}) "
            f"— refusing to write through it"
        )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp_path)
        raise
    os.replace(tmp_path, sidecar_path)
    snapshot = sidecar_path.parent / AUDIT_SNAPSHOT_FILENAME
    with contextlib.suppress(OSError):
        snapshot.unlink()
    if sys.platform != "win32":
        dir_fd = os.open(str(sidecar_path.parent), os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)


# ---------------------------------------------------------------------------
# Authoring mode.
# ---------------------------------------------------------------------------


def author_cutover_record(
    config: RuntimeConfig,
    *,
    sidecar_path: Path,
    signing_backend: SigningBackend,
    attestation: dict[str, str],
    tofu_quarantine_tenant: str | None = None,
) -> AuditCutoverRecord:
    """Compose + validate + sign + EMIT the cutover record.

    Tenant-binding input (OD v1.34 §21.2.2 row 5; the concrete carrier is
    plan-granted implementation discretion): `attestation` maps
    `entry_hash` → attested tenant for `"_single"` identities;
    `tofu_quarantine_tenant` — the operator's declared-TOFU decision —
    QUARANTINES every unattested `"_single"` identity under that scope.
    Identities covered by neither → typed refusal, nothing emitted.

    Observed pre-cutover identities composed (plan codex round-25):
    baseline pairs (`placeholder_exempt` — no full entry exists to verify,
    so `four_tuple_real` would only ever report unverifiable);
    `"_single"` full rows (`placeholder_exempt` for `unsigned:*`
    placeholder-era values, else `four_tuple_real` — an AUTHORING-time
    discrimination the operator attests, distinct from the forbidden
    VERIFICATION-time era inference); already-tenant-tagged v1.33-era full
    rows (`four_tuple_real` under their existing `source_tag` — era cannot
    be inferred from mutable signature values afterward).
    """
    _validate_signing_config(config, signing_backend=signing_backend)
    record_path, record_key_id, binding_id = _record_trust_inputs(config)
    _reject_reserved_record_path(record_path, sidecar_path=sidecar_path)
    if record_path.exists():
        raise RecordMigrationError(
            f"cutover record already exists at {record_path} — refusing to "
            f"overwrite a trust anchor (remove it deliberately first if "
            f"re-authoring is intended)"
        )
    _reject_record_key_used_by_persisted_rows(
        config, sidecar_path=sidecar_path, record_key_id=record_key_id
    )
    if not sidecar_path.is_file():
        raise RecordMigrationError(
            f"sidecar not found at {sidecar_path} — a deployment with no "
            f"observed history authors its EMPTY record at bootstrap "
            f"initialization, not here"
        )
    rows = _read_sidecar_rows(sidecar_path)

    composed: list[AuditCutoverRecordRow] = []
    unattested: list[str] = []

    if tofu_quarantine_tenant is not None and not tofu_quarantine_tenant.strip():
        raise RecordMigrationError(
            "--tofu-quarantine tenant must be non-blank — an empty scope "
            "would silently omit every unattested identity from the record"
        )

    def _tenant_for(entry_hash: str) -> tuple[str, bool]:
        """(tenant_scope, quarantined) for a `\"_single\"` identity."""
        attested = attestation.get(entry_hash)
        if attested is not None:
            if not attested.strip():
                raise RecordMigrationError(
                    f"attestation for {entry_hash!r} maps to a blank tenant "
                    f"— rejected (a blank binding would silently omit the "
                    f"identity from the signed record)"
                )
            return attested, False
        if tofu_quarantine_tenant is not None:
            return tofu_quarantine_tenant, True
        unattested.append(entry_hash)
        return "", False

    seen_single: set[str] = set()
    for tag, entry in rows.single_full_identities():
        if tag == _SINGLE_TAG:
            if entry.entry_hash in seen_single:
                continue
            seen_single.add(entry.entry_hash)
            tenant, quarantined = _tenant_for(entry.entry_hash)
            if not tenant:
                continue
            if quarantined:
                disposition = VerificationDisposition.QUARANTINED
            elif entry.signature_attrs.audit_signature_value.startswith(
                _PLACEHOLDER_SIGNATURE_PREFIX
            ):
                disposition = VerificationDisposition.PLACEHOLDER_EXEMPT
            else:
                disposition = VerificationDisposition.FOUR_TUPLE_REAL
            composed.append(
                AuditCutoverRecordRow(
                    source_tag=_SINGLE_TAG,
                    tenant_scope=tenant,
                    entry_hash=entry.entry_hash,
                    verification_disposition=disposition,
                )
            )
        else:
            # Already-tenant-tagged v1.33-era row: genuine FOUR-tuple
            # signature under its existing source_tag.
            composed.append(
                AuditCutoverRecordRow(
                    source_tag=tag,
                    tenant_scope=tag,
                    entry_hash=entry.entry_hash,
                    verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
                )
            )
    for tag, entry_hash in rows.baseline_pairs():
        if tag != _SINGLE_TAG:
            composed.append(
                AuditCutoverRecordRow(
                    source_tag=tag,
                    tenant_scope=tag,
                    entry_hash=entry_hash,
                    verification_disposition=VerificationDisposition.PLACEHOLDER_EXEMPT,
                )
            )
            continue
        if entry_hash in seen_single:
            continue
        seen_single.add(entry_hash)
        tenant, quarantined = _tenant_for(entry_hash)
        if not tenant:
            continue
        composed.append(
            AuditCutoverRecordRow(
                source_tag=_SINGLE_TAG,
                tenant_scope=tenant,
                entry_hash=entry_hash,
                verification_disposition=(
                    VerificationDisposition.QUARANTINED
                    if quarantined
                    else VerificationDisposition.PLACEHOLDER_EXEMPT
                ),
            )
        )

    if unattested:
        raise RecordMigrationError(
            f"{len(unattested)} observed '_single' identity(ies) with no "
            f"attestation and no declared-TOFU quarantine decision — refusing "
            f"to author an incomplete record: {', '.join(sorted(unattested))}"
        )

    algorithm = signing_backend.algorithm
    try:
        from harness_od.audit_ledger_types import SignatureAlgorithm

        record = AuditCutoverRecord(
            schema_version=1,
            authored_at=datetime.now(UTC),
            algorithm=SignatureAlgorithm(algorithm),
            key_id=record_key_id,
            ledger_binding_id=binding_id,
            rows=tuple(composed),
        )
        signature = sign_cutover_record(record, backend=signing_backend)
    except (CutoverRecordValidationError, ValueError) as exc:
        raise RecordMigrationError(f"record composition/signing failed: {exc}") from exc

    # Round-trip the fresh signature through VERIFICATION before publishing
    # (codex round-3 P1, mirroring the greenfield mint): a backend that can
    # sign but not verify — or emits an invalid same-width signature — must
    # fail HERE, not at every subsequent bootstrap/retag.
    try:
        round_trip_ok = verify_cutover_record_signature(record, signature, backend=signing_backend)
    except Exception as exc:
        raise RecordMigrationError(
            f"authored-record verification round-trip RAISED "
            f"({type(exc).__name__}: {exc}) — refusing to publish an "
            f"unverifiable trust anchor"
        ) from exc
    if not round_trip_ok:
        raise RecordMigrationError(
            "authored-record signature failed its verification round-trip — "
            "refusing to publish an unverifiable trust anchor"
        )
    record_path.parent.mkdir(parents=True, exist_ok=True)
    _publish_record_exclusively(
        record_path, record.model_dump_json() + "\n" + signature.hex() + "\n"
    )
    return record


def _publish_record_exclusively(record_path: Path, content: str) -> None:
    """Crash-safe, exclusive trust-anchor publication (codex round-1 P1s):
    temp file + fsync + `os.link` (fails on ANY existing path entry,
    including a dangling symlink — never follows) + directory fsync.
    Mirrors the greenfield mint's own publication discipline."""
    if record_path.is_symlink():
        raise RecordMigrationError(
            f"configured record path {record_path} is a symlink — the trust "
            f"anchor must be a regular file path, never a redirection"
        )
    tmp_path = record_path.with_name(record_path.name + ".author.tmp")
    with contextlib.suppress(OSError):
        os.unlink(tmp_path)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(str(tmp_path), os.O_WRONLY | os.O_CREAT | os.O_EXCL | nofollow, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(tmp_path, record_path)
        except FileExistsError as exc:
            raise RecordMigrationError(
                f"record path {record_path} appeared during authoring — "
                f"refusing to overwrite (concurrent authoring or a path swap)"
            ) from exc
        if sys.platform != "win32":
            dir_fd = os.open(str(record_path.parent), os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
    finally:
        with contextlib.suppress(OSError):
            os.unlink(tmp_path)
