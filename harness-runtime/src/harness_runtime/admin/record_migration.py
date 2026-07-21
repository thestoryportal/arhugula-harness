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
)
from harness_od.audit_ledger_types import AuditLedgerEntry

from harness_runtime.lifecycle.audit_signing_fail_closed_validation import (
    AuditSigningConfigInvalidError,
    _reject_record_key_used_by_persisted_rows,  # pyright: ignore[reportPrivateUsage]  # shared trust-anchor component
    _verify_existing_record,  # pyright: ignore[reportPrivateUsage]  # shared trust-anchor component
)
from harness_runtime.lifecycle.audit_writer import AUDIT_SNAPSHOT_FILENAME

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
    """Read-only, fail-loud parse of every sidecar line."""
    try:
        text = sidecar_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RecordMigrationError(f"sidecar {sidecar_path} unreadable: {exc}") from exc
    lines: list[dict[str, object]] = []
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
    record = _authenticate_record(
        config, sidecar_path=sidecar_path, signing_backend=signing_backend
    )
    if not sidecar_path.is_file():
        raise RecordMigrationError(f"sidecar not found at {sidecar_path} — nothing to retag")
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
    with cross_process_replace_lock(sidecar_path):
        tmp_path = sidecar_path.with_name(sidecar_path.name + ".retag.tmp")
        fd = os.open(str(tmp_path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
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
    record_path, record_key_id, binding_id = _record_trust_inputs(config)
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

    def _tenant_for(entry_hash: str) -> tuple[str, bool]:
        """(tenant_scope, quarantined) for a `\"_single\"` identity."""
        attested = attestation.get(entry_hash)
        if attested is not None:
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

    record_path.write_text(
        record.model_dump_json() + "\n" + signature.hex() + "\n", encoding="utf-8"
    )
    return record
