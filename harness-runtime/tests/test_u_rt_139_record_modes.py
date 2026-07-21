"""`U-RT-139` — `migrate-audit-sidecar` record-mode witnesses.

The plan-named Tests block (Runtime plan v2.49 §1.7): record-driven retag,
record authoring, authentication-before-retag, IS-identity coherence via
the record-derived alias (live writer wiring), atomicity, and completeness
refusal. Sidecar rows and IS refs are produced by the REAL
`RuntimeAuditLedgerWriter.append` (never hand-rolled), so every witness
exercises the production identity join.

`test_tampered_alias_or_record_fails_typed_at_bootstrap`'s bootstrap half
is already pinned by the U-RT-134 suite
(`test_existing_record_tampered_signature_rejected` — the alias IS
record-derived, so record tampering covers the alias-tamper case by
construction); this file adds the retag-side and live-join halves.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from harness_core import PersonaTier
from harness_core.deployment_surface import DeploymentSurface
from harness_cp.topology_pattern import TopologyPattern
from harness_is.jsonl_event_ledger_lifecycle import JsonlLedgerHandle
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_od.audit_cutover_record import (
    AuditCutoverRecord,
    AuditCutoverRecordRow,
    VerificationDisposition,
    sign_cutover_record,
    verify_cutover_record_signature,
)
from harness_od.audit_ledger_types import (
    AuditLedgerEntry,
    AuditPayload,
    AuditSignatureAttributes,
    SignatureAlgorithm,
    StateLedgerEntryRef,
    compute_entry_hash,
)
from harness_od.multi_tenant_trace_separation_and_audit_ledger import sign_audit_entry
from harness_runtime.admin.record_migration import (
    RecordMigrationError,
    TenantAttestation,
    author_cutover_record,
    retag_sidecar,
)
from harness_runtime.lifecycle.audit_writer import (
    AUDIT_SIDECAR_FILENAME,
    RuntimeAuditLedgerWriter,
)
from harness_runtime.lifecycle.state_ledger import LedgerWriter
from harness_runtime.types import (
    AuditSigningBackendKind,
    AuditSigningConfig,
    CollectorConfig,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
)

_GENESIS = "0" * 64
_ROW_KEY = "row-key"
_RECORD_KEY = "record-key"
_BINDING = "sidecar-1"
_TENANT = "tenant-a"
_ARN_ROW = "arn:aws:kms:us-east-1:111122223333:key/row-signing-key"
_ARN_RECORD = "arn:aws:kms:us-east-1:111122223333:key/cutover-record-key"


class _FakeBackend:
    """Deterministic HMAC `SigningBackend` double (U-RT-134 pattern)."""

    def __init__(self, algorithm: str = "ed25519", secret: bytes = b"record-secret") -> None:
        self.algorithm = algorithm
        self._secret = secret

    def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
        del key_id, key_period
        return hmac.new(self._secret, message, hashlib.sha512).digest()

    def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
        del key_id, key_period
        expected = hmac.new(self._secret, message, hashlib.sha512).digest()
        return hmac.compare_digest(expected, signature)


class _Deployment:
    """One deployment: real IS ledger + real audit writer + record inputs."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.ledger_path = root / "state.jsonl"
        self.ledger_path.touch()
        self.sidecar_path = root / AUDIT_SIDECAR_FILENAME
        self.record_path = root / "cutover-record"
        self.row_backend = _FakeBackend(secret=b"row-secret")
        self.record_backend = _FakeBackend(secret=b"record-secret")

    def config(self) -> RuntimeConfig:
        return RuntimeConfig(
            deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
            repository_root=self.root,
            path_bindings=PathBindingConfig(),
            provider_secrets=ProviderSecretsConfig(),
            otel=OTelConfig(otlp_endpoint="http://localhost:4317"),
            collector=CollectorConfig(),
            default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
            mcp_clients=[],
            persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
            tenant_id=_TENANT,
            audit_signing=AuditSigningConfig(
                backend=AuditSigningBackendKind.AWS_KMS,
                # Every composition-root signing consumer must be mapped for
                # the stage-4 validation the record modes now run up front.
                key_arns={
                    _ROW_KEY: _ARN_ROW,
                    _RECORD_KEY: _ARN_RECORD,
                    "harness-runtime-redaction-token": _ARN_ROW + "-redaction",
                    "harness-runtime-dev": _ARN_ROW + "-dev",
                    "harness-cost-attribution-v1": _ARN_ROW + "-cost",
                },
            ),
            audit_cutover_record_path=str(self.record_path),
            audit_cutover_record_key_id=_RECORD_KEY,
            audit_ledger_binding_id=_BINDING,
        )

    def writer(
        self, *, cutover_record: AuditCutoverRecord | None = None
    ) -> RuntimeAuditLedgerWriter:
        """A FRESH writer over the same ledger (a process restart)."""
        text = self.ledger_path.read_text()
        count = sum(1 for line in text.splitlines() if line.strip())
        return RuntimeAuditLedgerWriter(
            ledger_writer=LedgerWriter(
                handle=JsonlLedgerHandle(
                    canonical_path=self.ledger_path, exists=True, entry_count=count
                ),
                actor=Actor(actor_class=ActorClass.AGENT, actor_id="test"),
            ),
            time_source=lambda: datetime.now(UTC),
            cutover_record=cutover_record,
        )

    def signed_entry(self, core: str, *, placeholder: bool = False) -> AuditLedgerEntry:
        payload = AuditPayload(
            entry_core=StateLedgerEntryRef(core),
            audit_namespace_attrs={"audit.actor": "x"},
            prior_entry_hash=_GENESIS,
        )
        if placeholder:
            sig_attrs = AuditSignatureAttributes(
                audit_signature_value="unsigned:placeholder",
                audit_signature_algorithm=SignatureAlgorithm.ED25519,
                audit_signature_key_id=_ROW_KEY,
                audit_signature_key_period="deployment-bound",
            )
        else:
            sig_attrs = sign_audit_entry(
                payload,
                _ROW_KEY,
                SignatureAlgorithm.ED25519,
                backend=self.row_backend,
                tenant_id=None,
            )
        return AuditLedgerEntry(
            payload=payload, signature_attrs=sig_attrs, entry_hash=compute_entry_hash(payload)
        )

    def write_record(
        self, *rows: AuditCutoverRecordRow, binding: str = _BINDING, tamper: bool = False
    ) -> AuditCutoverRecord:
        record = AuditCutoverRecord(
            schema_version=1,
            authored_at=datetime(2026, 7, 21, tzinfo=UTC),
            algorithm=SignatureAlgorithm.ED25519,
            key_id=_RECORD_KEY,
            ledger_binding_id=binding,
            rows=rows,
        )
        signature = sign_cutover_record(record, backend=self.record_backend)
        if tamper:
            signature = bytes([signature[0] ^ 0xFF]) + signature[1:]
        self.record_path.write_text(
            record.model_dump_json() + "\n" + signature.hex() + "\n", encoding="utf-8"
        )
        return record

    def append_baseline_line(self, pairs: list[tuple[str, str]]) -> None:
        with self.sidecar_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"legacy_baseline": [[t, h] for t, h in pairs]}) + "\n")


@pytest.fixture
def dep(tmp_path: Path) -> _Deployment:
    return _Deployment(tmp_path)


def _row(
    entry_hash: str,
    *,
    disposition: VerificationDisposition = VerificationDisposition.PLACEHOLDER_EXEMPT,
    tenant: str = _TENANT,
    source: str = "_single",
) -> AuditCutoverRecordRow:
    return AuditCutoverRecordRow(
        source_tag=source,
        tenant_scope=tenant,
        entry_hash=entry_hash,
        verification_disposition=disposition,
    )


# ---------------------------------------------------------------------------
# Retag semantics.
# ---------------------------------------------------------------------------


def test_retag_named_rows_reachable_by_tenant_read_content_and_hash_unchanged(
    dep: _Deployment,
) -> None:
    """Witness (f): post-retag, record-named rows are returned by
    `read_full_entries_for_tenant(attested_tenant)` with byte-identical
    entry content + entry_hash; a QUARANTINED row is NOT retagged and is
    absent from that read (an UNDISPOSITIONED leftover would trigger the
    completeness refusal instead — codex round-11 on the plan)."""
    exempt_entry = dep.signed_entry("ref-exempt", placeholder=True)
    quarantined_entry = dep.signed_entry("ref-quarantined")
    writer = dep.writer()
    writer.append(None, exempt_entry)
    writer.append(None, quarantined_entry)
    dep.write_record(
        _row(exempt_entry.entry_hash),
        _row(quarantined_entry.entry_hash, disposition=VerificationDisposition.QUARANTINED),
    )

    outcome = retag_sidecar(
        dep.config(), sidecar_path=dep.sidecar_path, signing_backend=dep.record_backend
    )
    assert outcome.retagged == 1
    assert outcome.quarantined_left == 1

    record = dep.write_record(  # re-emit unchanged record for the fresh writer
        _row(exempt_entry.entry_hash),
        _row(quarantined_entry.entry_hash, disposition=VerificationDisposition.QUARANTINED),
    )
    fresh = dep.writer(cutover_record=record)
    tenant_entries = fresh.read_full_entries_for_tenant(_TENANT)
    assert [entry.entry_hash for entry in tenant_entries] == [exempt_entry.entry_hash]
    assert tenant_entries[0].payload == exempt_entry.payload  # content byte-unchanged
    assert tenant_entries[0].signature_attrs == exempt_entry.signature_attrs

    single_entries = fresh.read_full_entries_for_tenant(None)
    assert [entry.entry_hash for entry in single_entries] == [quarantined_entry.entry_hash]


def test_post_retag_restart_and_append_pass_coverage(dep: _Deployment) -> None:
    """LIVE WRITER WIRING (plan codex round-12): after a retag, a process
    RESTART's full index fold and a FRESH append both pass the coverage
    join — the immutable `audit:_single:<hash>` IS refs are covered through
    the record-derived alias consulted at `_assert_is_refs_covered_locked`."""
    entry = dep.signed_entry("ref-1", placeholder=True)
    dep.writer().append(None, entry)
    record = dep.write_record(_row(entry.entry_hash))
    retag_sidecar(dep.config(), sidecar_path=dep.sidecar_path, signing_backend=dep.record_backend)

    fresh = dep.writer(cutover_record=record)
    appended = dep.signed_entry("ref-2")
    result = fresh.append(_TENANT, appended)  # append triggers the full fold + coverage
    assert result is not None
    assert {e.entry_hash for e in fresh.read_full_entries_for_tenant(_TENANT)} == {
        entry.entry_hash,
        appended.entry_hash,
    }


def test_post_retag_refold_and_append_report_full_history(dep: _Deployment) -> None:
    """The negative half that makes the alias LOAD-BEARING (plan witness +
    mutation probe in one): retagging the sidecar ALONE — a fresh writer
    WITHOUT the record — makes every `("_single", hash)` IS reference
    report truncated history; WITH the record the same fold passes."""
    entry = dep.signed_entry("ref-1", placeholder=True)
    dep.writer().append(None, entry)
    record = dep.write_record(_row(entry.entry_hash))
    retag_sidecar(dep.config(), sidecar_path=dep.sidecar_path, signing_backend=dep.record_backend)

    # The `"_single"`-scope read is where the immutable IS refs live —
    # without the record the retagged row is invisible to it.
    without_record = dep.writer(cutover_record=None)
    with pytest.raises(ValueError, match="truncated or lost"):
        without_record.read_full_entries_for_tenant(None)

    with_record = dep.writer(cutover_record=record)
    assert with_record.read_full_entries_for_tenant(None) == []  # aliased away, no raise
    entries = with_record.read_full_entries_for_tenant(_TENANT)
    assert [e.entry_hash for e in entries] == [entry.entry_hash]


def test_retag_interrupted_midway_leaves_all_or_nothing(
    dep: _Deployment, monkeypatch: pytest.MonkeyPatch
) -> None:
    """ATOMICITY (plan codex round-11): a crash after the temp write but
    BEFORE publication leaves the sidecar byte-identical to pre-retag; the
    re-run completes to fully-retagged. Never mixed visibility."""
    entry_a = dep.signed_entry("ref-a", placeholder=True)
    entry_b = dep.signed_entry("ref-b", placeholder=True)
    writer = dep.writer()
    writer.append(None, entry_a)
    writer.append(None, entry_b)
    dep.write_record(_row(entry_a.entry_hash), _row(entry_b.entry_hash))
    before = dep.sidecar_path.read_bytes()

    import harness_runtime.admin.record_migration as rm

    real_replace = rm.os.replace

    def crash_replace(src: object, dst: object) -> None:
        raise OSError("simulated crash before publication")

    monkeypatch.setattr(rm.os, "replace", crash_replace)
    with pytest.raises(OSError, match="simulated crash"):
        retag_sidecar(
            dep.config(), sidecar_path=dep.sidecar_path, signing_backend=dep.record_backend
        )
    assert dep.sidecar_path.read_bytes() == before  # byte-identical — nothing mixed

    monkeypatch.setattr(rm.os, "replace", real_replace)
    outcome = retag_sidecar(
        dep.config(), sidecar_path=dep.sidecar_path, signing_backend=dep.record_backend
    )
    assert outcome.retagged == 2
    tags = [
        json.loads(line)["tenant_tag"]
        for line in dep.sidecar_path.read_text().splitlines()
        if line.strip()
    ]
    assert tags == [_TENANT, _TENANT]  # fully retagged, never partial


def test_retag_refuses_on_undispositioned_single_leftovers(dep: _Deployment) -> None:
    """RECORD COMPLETENESS (plan codex round-10): one full-entry `_single`
    row absent from the record → typed refusal, NO tag changed."""
    entry_a = dep.signed_entry("ref-a", placeholder=True)
    entry_b = dep.signed_entry("ref-b", placeholder=True)
    writer = dep.writer()
    writer.append(None, entry_a)
    writer.append(None, entry_b)
    dep.write_record(_row(entry_a.entry_hash))  # entry_b undispositioned
    before = dep.sidecar_path.read_bytes()

    with pytest.raises(RecordMigrationError, match="does not disposition"):
        retag_sidecar(
            dep.config(), sidecar_path=dep.sidecar_path, signing_backend=dep.record_backend
        )
    assert dep.sidecar_path.read_bytes() == before


def test_baseline_pairs_project_through_alias_no_divergence(dep: _Deployment) -> None:
    """BASELINE-PAIR REPROJECTION (plan codex round-14): a record-
    dispositioned baseline pair compares clean (the alias IS the migration
    — the on-disk baseline line is byte-unchanged); an undispositioned
    baseline pair triggers the completeness refusal."""
    entry = dep.signed_entry("ref-full", placeholder=True)
    dep.writer().append(None, entry)
    baseline_hash = "b" * 64
    dep.append_baseline_line([("_single", baseline_hash)])
    dep.write_record(_row(entry.entry_hash), _row(baseline_hash))
    before_lines = dep.sidecar_path.read_text().splitlines()

    outcome = retag_sidecar(
        dep.config(), sidecar_path=dep.sidecar_path, signing_backend=dep.record_backend
    )
    assert outcome.baseline_aliased == 1
    after_lines = dep.sidecar_path.read_text().splitlines()
    assert after_lines[-1] == before_lines[-1]  # baseline line byte-unchanged

    # Undispositioned baseline pair → refusal (fresh deployment).
    second_root = dep.root / "second"
    second_root.mkdir()
    dep2 = _Deployment(second_root)
    entry2 = dep2.signed_entry("ref-2", placeholder=True)
    dep2.writer().append(None, entry2)
    dep2.append_baseline_line([("_single", "c" * 64)])
    dep2.write_record(_row(entry2.entry_hash))  # baseline pair undispositioned
    with pytest.raises(RecordMigrationError, match="does not disposition"):
        retag_sidecar(
            dep2.config(), sidecar_path=dep2.sidecar_path, signing_backend=dep2.record_backend
        )


# ---------------------------------------------------------------------------
# Record trust at retag.
# ---------------------------------------------------------------------------


def test_record_from_other_deployment_rejected_by_binding_compare(dep: _Deployment) -> None:
    """LEDGER-BINDING CONSUMPTION (plan codex rounds 44/47): the record's
    SIGNED binding is compared against the CONFIG value — a record authored
    for a different deployment's sidecar is rejected, zero tags changed."""
    entry = dep.signed_entry("ref-1", placeholder=True)
    dep.writer().append(None, entry)
    dep.write_record(_row(entry.entry_hash), binding="some-other-deployment")
    before = dep.sidecar_path.read_bytes()

    with pytest.raises(RecordMigrationError, match="ledger_binding_id"):
        retag_sidecar(
            dep.config(), sidecar_path=dep.sidecar_path, signing_backend=dep.record_backend
        )
    assert dep.sidecar_path.read_bytes() == before


def test_forged_cutover_record_rejected_typed_never_treated_as_absent(
    dep: _Deployment, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """AUTHENTICATION IS U-RT-139's OWN OBLIGATION (plan codex round-5):
    a tampered record is REJECTED with a typed error through the REAL CLI
    (`--retag`), exit 1, ZERO tags changed — never treated as absent,
    never partial. (The inspect half lives at U-RT-138.)"""
    from harness_runtime.admin.migrate_audit_sidecar import main

    entry = dep.signed_entry("ref-1", placeholder=True)
    dep.writer().append(None, entry)
    dep.write_record(_row(entry.entry_hash), tamper=True)
    before = dep.sidecar_path.read_bytes()

    config_path = dep.root / "harness.toml"
    config_path.write_text(
        "\n".join(
            [
                "[runtime]",
                'deployment_surface = "local-development"',
                f'repository_root = "{dep.root}"',
                'default_topology = "single-threaded-linear"',
                'persona_tier = "multi-tenant-compliance"',
                f'tenant_id = "{_TENANT}"',
                f'audit_cutover_record_path = "{dep.record_path}"',
                f'audit_cutover_record_key_id = "{_RECORD_KEY}"',
                f'audit_ledger_binding_id = "{_BINDING}"',
                "",
                "[runtime.audit_signing]",
                'backend = "aws-kms"',
                "[runtime.audit_signing.key_arns]",
                f'"{_ROW_KEY}" = "{_ARN_ROW}"',
                f'"{_RECORD_KEY}" = "{_ARN_RECORD}"',
                f'"harness-runtime-redaction-token" = "{_ARN_ROW}-redaction"',
                f'"harness-runtime-dev" = "{_ARN_ROW}-dev"',
                f'"harness-cost-attribution-v1" = "{_ARN_ROW}-cost"',
                "",
                "[runtime.otel]",
                'otlp_endpoint = "http://localhost:4318"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "harness_runtime.config.audit_signing.make_audit_signing_backend",
        lambda config: dep.record_backend,
    )
    exit_code = main([str(dep.ledger_path), "--retag", "--runtime-config", str(config_path)])
    assert exit_code == 1
    assert dep.sidecar_path.read_bytes() == before
    captured = capsys.readouterr()
    # Pins the AUTHENTICATION branch specifically (not a config rejection).
    assert "REJECTED" in captured.err


# ---------------------------------------------------------------------------
# Authoring.
# ---------------------------------------------------------------------------


def test_authoring_round_trip_record_verifies_and_drives_retag(dep: _Deployment) -> None:
    """AUTHORING (plan codex round-23): compose from EVERY observed
    pre-cutover identity — a placeholder-valued `_single` row
    (placeholder_exempt), a real-signed `_single` row (four_tuple_real), an
    already-tenant-tagged v1.33 row (four_tuple_real under its OWN
    source_tag — plan codex round-25), and a baseline pair — sign under the
    pinned key, verify, then the retag step CONSUMES the emitted record."""
    placeholder_entry = dep.signed_entry("ref-placeholder", placeholder=True)
    real_entry = dep.signed_entry("ref-real")
    tagged_entry = dep.signed_entry("ref-tagged")
    writer = dep.writer()
    writer.append(None, placeholder_entry)
    writer.append(None, real_entry)
    writer.append("tenant-b", tagged_entry)
    baseline_hash = "d" * 64
    dep.append_baseline_line([("_single", baseline_hash)])

    record = author_cutover_record(
        dep.config(),
        sidecar_path=dep.sidecar_path,
        signing_backend=dep.record_backend,
        attestation={
            # Exemption is an EXPLICIT operator decision (codex round-5 P1)
            # — never inferred from the mutable signature-value shape.
            placeholder_entry.entry_hash: TenantAttestation(
                tenant=_TENANT, placeholder_exempt=True
            ),
            real_entry.entry_hash: TenantAttestation(tenant=_TENANT),
            baseline_hash: TenantAttestation(tenant=_TENANT),
            # Already-tagged rows need an external binding MATCHING the
            # observed tag.
            tagged_entry.entry_hash: TenantAttestation(tenant="tenant-b"),
        },
    )
    assert dep.record_path.is_file()
    record_line, signature_line = dep.record_path.read_text().splitlines()
    assert AuditCutoverRecord.model_validate_json(record_line) == record
    assert verify_cutover_record_signature(
        record, bytes.fromhex(signature_line), backend=dep.record_backend
    )
    by_source = {
        (row.source_tag, row.entry_hash): row.verification_disposition for row in record.rows
    }
    assert by_source[("_single", placeholder_entry.entry_hash)] is (
        VerificationDisposition.PLACEHOLDER_EXEMPT
    )
    assert by_source[("_single", real_entry.entry_hash)] is (
        VerificationDisposition.FOUR_TUPLE_REAL
    )
    assert by_source[("tenant-b", tagged_entry.entry_hash)] is (
        VerificationDisposition.FOUR_TUPLE_REAL
    )
    assert by_source[("_single", baseline_hash)] is VerificationDisposition.PLACEHOLDER_EXEMPT

    outcome = retag_sidecar(
        dep.config(), sidecar_path=dep.sidecar_path, signing_backend=dep.record_backend
    )
    assert outcome.retagged == 2  # both _single full rows; tagged row untouched
    assert outcome.already_tagged_left == 1


def test_authoring_refuses_unattested_without_tofu_and_quarantines_with(
    dep: _Deployment,
) -> None:
    """Tenant-binding input coverage: an unattested `_single` identity with
    no declared-TOFU decision → typed refusal, nothing emitted; WITH
    `tofu_quarantine_tenant` the identity is QUARANTINED (and the record
    then leaves it un-retagged)."""
    entry = dep.signed_entry("ref-1", placeholder=True)
    dep.writer().append(None, entry)

    with pytest.raises(RecordMigrationError, match="no attestation"):
        author_cutover_record(
            dep.config(),
            sidecar_path=dep.sidecar_path,
            signing_backend=dep.record_backend,
            attestation={},
        )
    assert not dep.record_path.exists()

    record = author_cutover_record(
        dep.config(),
        sidecar_path=dep.sidecar_path,
        signing_backend=dep.record_backend,
        attestation={},
        tofu_quarantine_tenant=_TENANT,
    )
    assert record.rows[0].verification_disposition is VerificationDisposition.QUARANTINED
    outcome = retag_sidecar(
        dep.config(), sidecar_path=dep.sidecar_path, signing_backend=dep.record_backend
    )
    assert outcome.retagged == 0
    assert outcome.quarantined_left == 1


def test_authoring_refuses_to_overwrite_existing_record(dep: _Deployment) -> None:
    """A trust anchor is never silently overwritten."""
    entry = dep.signed_entry("ref-1", placeholder=True)
    dep.writer().append(None, entry)
    dep.write_record(_row(entry.entry_hash))

    with pytest.raises(RecordMigrationError, match="already exists"):
        author_cutover_record(
            dep.config(),
            sidecar_path=dep.sidecar_path,
            signing_backend=dep.record_backend,
            attestation={entry.entry_hash: TenantAttestation(tenant=_TENANT)},
        )


# ---------------------------------------------------------------------------
# Codex round-1 hardenings (this leg).
# ---------------------------------------------------------------------------


def test_retag_tmp_hardlink_to_ledger_never_destroys_it(dep: _Deployment) -> None:
    """A pre-created `.retag.tmp` HARD LINK to the state ledger must never
    let the temp write destroy the linked file (the old truncate-in-place
    open would have) — the stale tmp is unlinked and re-created
    exclusively; the ledger survives byte-identical and the retag
    completes."""
    entry = dep.signed_entry("ref-1", placeholder=True)
    dep.writer().append(None, entry)
    dep.write_record(_row(entry.entry_hash))
    ledger_before = dep.ledger_path.read_bytes()
    tmp = dep.sidecar_path.with_name(dep.sidecar_path.name + ".retag.tmp")
    import os as _os

    _os.link(dep.ledger_path, tmp)  # the attacker's planted hard link

    outcome = retag_sidecar(
        dep.config(), sidecar_path=dep.sidecar_path, signing_backend=dep.record_backend
    )
    assert outcome.retagged == 1
    assert dep.ledger_path.read_bytes() == ledger_before  # never truncated


def test_record_modes_refuse_config_bootstrap_would_reject(dep: _Deployment) -> None:
    """A config normal bootstrap rejects (record key sharing a row key's
    backing material) must refuse record modes BEFORE any side effect —
    never author/retag first and brick the deployment after."""
    entry = dep.signed_entry("ref-1", placeholder=True)
    dep.writer().append(None, entry)
    config = dep.config().model_copy(
        update={
            "audit_signing": AuditSigningConfig(
                backend=AuditSigningBackendKind.AWS_KMS,
                key_arns={_ROW_KEY: _ARN_ROW, _RECORD_KEY: _ARN_ROW},  # shared material
            )
        }
    )

    with pytest.raises(RecordMigrationError, match="rejected at bootstrap"):
        author_cutover_record(
            config,
            sidecar_path=dep.sidecar_path,
            signing_backend=dep.record_backend,
            attestation={entry.entry_hash: TenantAttestation(tenant=_TENANT)},
        )
    assert not dep.record_path.exists()


def test_author_record_path_symlink_refused(dep: _Deployment) -> None:
    """A (dangling) symlink at the configured record path must never be
    followed — the trust anchor is a regular file, not a redirection."""
    entry = dep.signed_entry("ref-1", placeholder=True)
    dep.writer().append(None, entry)
    target = dep.root / "attacker-chosen-target"
    dep.record_path.symlink_to(target)  # dangling — exists() is False

    with pytest.raises(RecordMigrationError, match="symlink"):
        author_cutover_record(
            dep.config(),
            sidecar_path=dep.sidecar_path,
            signing_backend=dep.record_backend,
            attestation={entry.entry_hash: TenantAttestation(tenant=_TENANT)},
        )
    assert not target.exists()  # nothing was created through the link


def test_author_crash_before_publication_leaves_no_partial_record(
    dep: _Deployment, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Crash-safe publication: a failure at the exclusive-link step leaves
    NO record file and NO temp residue — never a torn trust anchor beside
    an (about-to-be) retagged sidecar."""
    entry = dep.signed_entry("ref-1", placeholder=True)
    dep.writer().append(None, entry)

    import harness_runtime.admin.record_migration as rm

    def crash_link(src: object, dst: object) -> None:
        raise OSError("simulated crash at publication")

    monkeypatch.setattr(rm.os, "link", crash_link)
    with pytest.raises(OSError, match="simulated crash"):
        author_cutover_record(
            dep.config(),
            sidecar_path=dep.sidecar_path,
            signing_backend=dep.record_backend,
            attestation={entry.entry_hash: TenantAttestation(tenant=_TENANT)},
        )
    assert not dep.record_path.exists()
    assert not dep.record_path.with_name(dep.record_path.name + ".author.tmp").exists()


# ---------------------------------------------------------------------------
# Codex round-2 findings (this leg).
# ---------------------------------------------------------------------------


def test_retag_refuses_on_destination_collision(dep: _Deployment) -> None:
    """A retag destination colliding with an OBSERVED sidecar identity
    (the same entry already tenant-tagged, omitted from the record) would
    mint duplicate destination rows — typed refusal, zero changes."""
    entry = dep.signed_entry("ref-1", placeholder=True)
    writer = dep.writer()
    writer.append(None, entry)  # ("_single", H)
    writer.append(_TENANT, entry)  # ("tenant-a", H) — the collision target
    dep.write_record(_row(entry.entry_hash))  # maps ("_single", H) -> ("tenant-a", H)
    before = dep.sidecar_path.read_bytes()

    with pytest.raises(RecordMigrationError, match="collide"):
        retag_sidecar(
            dep.config(), sidecar_path=dep.sidecar_path, signing_backend=dep.record_backend
        )
    assert dep.sidecar_path.read_bytes() == before


def test_retag_read_happens_inside_replace_lock(
    dep: _Deployment, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The B-46 exclusion spans read→compose→replace: the sidecar READ runs
    while the replace lock is held — a concurrent append can never land
    between an unlocked snapshot and the replacement."""
    entry = dep.signed_entry("ref-1", placeholder=True)
    dep.writer().append(None, entry)
    dep.write_record(_row(entry.entry_hash))

    import contextlib as _contextlib

    import harness_runtime.admin.record_migration as rm

    lock_held = {"value": False}
    reads_under_lock: list[bool] = []

    @_contextlib.contextmanager
    def tracking_lock(path: object):
        lock_held["value"] = True
        try:
            yield
        finally:
            lock_held["value"] = False

    real_read = rm._read_sidecar_rows

    def tracking_read(path: object):
        reads_under_lock.append(lock_held["value"])
        return real_read(path)  # type: ignore[arg-type]

    monkeypatch.setattr(rm, "cross_process_replace_lock", tracking_lock)
    monkeypatch.setattr(rm, "_read_sidecar_rows", tracking_read)
    retag_sidecar(dep.config(), sidecar_path=dep.sidecar_path, signing_backend=dep.record_backend)
    assert reads_under_lock == [True]


def test_tampered_alias_target_row_detected_on_single_read(dep: _Deployment) -> None:
    """A retagged destination row tampered in content (raw entry_hash
    retained) must FAIL the `_single`-scope read — never silently satisfy
    the alias coverage."""
    entry = dep.signed_entry("ref-1", placeholder=True)
    dep.writer().append(None, entry)
    record = dep.write_record(_row(entry.entry_hash))
    retag_sidecar(dep.config(), sidecar_path=dep.sidecar_path, signing_backend=dep.record_backend)

    rows = [json.loads(line) for line in dep.sidecar_path.read_text().splitlines() if line.strip()]
    rows[0]["entry"]["payload"]["audit_namespace_attrs"] = {"audit.actor": "TAMPERED"}
    dep.sidecar_path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

    fresh = dep.writer(cutover_record=record)
    with pytest.raises(ValueError, match="content-integrity"):
        fresh.read_full_entries_for_tenant(None)


# ---------------------------------------------------------------------------
# Codex round-3 findings (this leg).
# ---------------------------------------------------------------------------


def test_record_path_aliasing_migration_temp_refused(dep: _Deployment) -> None:
    """A record path aliasing a writer- or migration-owned file (here the
    retag temp name) is refused — the retag's stale-temp cleanup would
    otherwise DELETE the trust anchor it had just authenticated."""
    entry = dep.signed_entry("ref-1", placeholder=True)
    dep.writer().append(None, entry)
    config = dep.config().model_copy(
        update={
            "audit_cutover_record_path": str(
                dep.sidecar_path.with_name(dep.sidecar_path.name + ".retag.tmp")
            )
        }
    )
    with pytest.raises(RecordMigrationError, match="migration-owned"):
        author_cutover_record(
            config,
            sidecar_path=dep.sidecar_path,
            signing_backend=dep.record_backend,
            attestation={entry.entry_hash: TenantAttestation(tenant=_TENANT)},
        )


def test_author_unverifiable_signature_refused(dep: _Deployment) -> None:
    """A backend that signs but cannot verify (split KMS permissions, or a
    faulty same-width signature) fails AT AUTHORING — never publishing a
    record every later bootstrap/retag rejects."""

    class _SignOnlyBackend(_FakeBackend):
        def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
            return False

    entry = dep.signed_entry("ref-1", placeholder=True)
    dep.writer().append(None, entry)
    with pytest.raises(RecordMigrationError, match="round-trip"):
        author_cutover_record(
            dep.config(),
            sidecar_path=dep.sidecar_path,
            signing_backend=_SignOnlyBackend(secret=b"record-secret"),
            attestation={entry.entry_hash: TenantAttestation(tenant=_TENANT)},
        )
    assert not dep.record_path.exists()


def test_blank_tenant_bindings_rejected(dep: _Deployment) -> None:
    """A blank attested tenant or a blank --tofu-quarantine scope is
    rejected explicitly — never a silently-incomplete signed record that
    retag then refuses while re-authoring refuses the existing file."""
    entry = dep.signed_entry("ref-1", placeholder=True)
    dep.writer().append(None, entry)

    with pytest.raises(RecordMigrationError, match="blank tenant"):
        author_cutover_record(
            dep.config(),
            sidecar_path=dep.sidecar_path,
            signing_backend=dep.record_backend,
            attestation={entry.entry_hash: TenantAttestation(tenant="")},
        )
    with pytest.raises(RecordMigrationError, match="non-blank"):
        author_cutover_record(
            dep.config(),
            sidecar_path=dep.sidecar_path,
            signing_backend=dep.record_backend,
            attestation={},
            tofu_quarantine_tenant="  ",
        )
    assert not dep.record_path.exists()


def test_stage4_consumer_mapping_gap_refused(dep: _Deployment) -> None:
    """A config the stage-4 span-stage validation would reject (missing a
    composition-root consumer key mapping) refuses record modes up front."""
    entry = dep.signed_entry("ref-1", placeholder=True)
    dep.writer().append(None, entry)
    thin_map = {
        _ROW_KEY: _ARN_ROW,
        _RECORD_KEY: _ARN_RECORD,
        "harness-runtime-redaction-token": _ARN_ROW + "-redaction",
        # "harness-runtime-dev" + cost key MISSING
    }
    config = dep.config().model_copy(
        update={
            "audit_signing": AuditSigningConfig(
                backend=AuditSigningBackendKind.AWS_KMS, key_arns=thin_map
            )
        }
    )
    with pytest.raises(RecordMigrationError, match="rejected at bootstrap"):
        author_cutover_record(
            config,
            sidecar_path=dep.sidecar_path,
            signing_backend=dep.record_backend,
            attestation={entry.entry_hash: TenantAttestation(tenant=_TENANT)},
        )
    assert not dep.record_path.exists()


# ---------------------------------------------------------------------------
# Codex round-4 findings (this leg).
# ---------------------------------------------------------------------------


def test_symlinked_sidecar_refused(dep: _Deployment) -> None:
    """A symlinked sidecar must never be read/replaced through the link —
    the migration mirrors the writer's no-follow posture."""
    entry = dep.signed_entry("ref-1", placeholder=True)
    dep.writer().append(None, entry)
    real = dep.root / "moved-sidecar.jsonl"
    dep.sidecar_path.rename(real)
    dep.sidecar_path.symlink_to(real)
    dep.write_record(_row(entry.entry_hash))

    # Pins the EXPLICIT pre-open refusal (the O_NOFOLLOW open would also
    # refuse, but via a wrapped-OSError shape — the explicit branch gives
    # the operator the actionable diagnosis).
    with pytest.raises(RecordMigrationError, match="migration reads only"):
        retag_sidecar(
            dep.config(), sidecar_path=dep.sidecar_path, signing_backend=dep.record_backend
        )
    assert real.read_bytes()  # untouched through the link


def test_torn_tail_sidecar_refused(dep: _Deployment) -> None:
    """An unterminated final sidecar line is an UNCOMMITTED fragment — the
    migration refuses rather than promote data the writer's heal contract
    would discard."""
    entry = dep.signed_entry("ref-1", placeholder=True)
    dep.writer().append(None, entry)
    dep.write_record(_row(entry.entry_hash))
    raw = dep.sidecar_path.read_text(encoding="utf-8")
    dep.sidecar_path.write_text(raw.rstrip("\n"), encoding="utf-8")  # strip the terminator

    with pytest.raises(RecordMigrationError, match="unterminated"):
        retag_sidecar(
            dep.config(), sidecar_path=dep.sidecar_path, signing_backend=dep.record_backend
        )


def test_baseline_alias_destination_collision_refused(dep: _Deployment) -> None:
    """A baseline pair aliasing onto an OCCUPIED tenant identity (an
    existing full row omitted from the record) refuses — the alias would
    conflate the baseline with an unrelated full row."""
    entry = dep.signed_entry("ref-1", placeholder=True)
    writer = dep.writer()
    writer.append(_TENANT, entry)  # occupies ("tenant-a", H)
    dep.append_baseline_line([("_single", entry.entry_hash)])
    dep.write_record(_row(entry.entry_hash))  # aliases baseline onto ("tenant-a", H)
    before = dep.sidecar_path.read_bytes()

    with pytest.raises(RecordMigrationError, match="collide"):
        retag_sidecar(
            dep.config(), sidecar_path=dep.sidecar_path, signing_backend=dep.record_backend
        )
    assert dep.sidecar_path.read_bytes() == before


def test_corrupt_sidecar_row_refused_before_any_signing(dep: _Deployment) -> None:
    """A stale-hash payload the next fold would reject refuses the
    migration up front — never sign/replace first and brick after."""
    entry = dep.signed_entry("ref-1", placeholder=True)
    dep.writer().append(None, entry)
    rows = [json.loads(line) for line in dep.sidecar_path.read_text().splitlines() if line.strip()]
    rows[0]["entry"]["payload"]["audit_namespace_attrs"] = {"audit.actor": "TAMPERED"}
    dep.sidecar_path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    dep.write_record(_row(entry.entry_hash))

    with pytest.raises(RecordMigrationError, match="content-integrity"):
        retag_sidecar(
            dep.config(), sidecar_path=dep.sidecar_path, signing_backend=dep.record_backend
        )


def test_cli_config_refusal_precedes_backend_construction(
    dep: _Deployment, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The pure config-shape refusal fires BEFORE backend construction —
    an invalid MTC config surfaces the deterministic typed message, never
    an SDK/credential failure (and never external setup)."""
    from harness_runtime.admin.migrate_audit_sidecar import main

    entry = dep.signed_entry("ref-1", placeholder=True)
    dep.writer().append(None, entry)
    config_path = dep.root / "harness.toml"
    # MTC config MISSING the record inputs — bootstrap rejects it purely.
    config_path.write_text(
        "\n".join(
            [
                "[runtime]",
                'deployment_surface = "local-development"',
                f'repository_root = "{dep.root}"',
                'default_topology = "single-threaded-linear"',
                'persona_tier = "multi-tenant-compliance"',
                f'tenant_id = "{_TENANT}"',
                "",
                "[runtime.otel]",
                'otlp_endpoint = "http://localhost:4318"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    def exploding_backend(config: object) -> object:
        raise RuntimeError("SDK/credential discovery must not run first")

    monkeypatch.setattr(
        "harness_runtime.config.audit_signing.make_audit_signing_backend", exploding_backend
    )
    exit_code = main([str(dep.ledger_path), "--retag", "--runtime-config", str(config_path)])
    assert exit_code == 1  # typed refusal, the exploding backend never ran


# ---------------------------------------------------------------------------
# Codex round-5 findings (terminal round, this leg).
# ---------------------------------------------------------------------------


def test_placeholder_shape_never_infers_exemption(dep: _Deployment) -> None:
    """The `unsigned:*` signature-value shape is attacker-writable (outside
    entry_hash) — a PLAIN tenant attestation dispositions the row
    four_tuple_real, so a downgraded signature FAILS verification loudly
    instead of earning a signed exemption. Exemption requires the EXPLICIT
    operator attestation."""
    entry = dep.signed_entry("ref-1", placeholder=True)  # unsigned:* value
    dep.writer().append(None, entry)

    record = author_cutover_record(
        dep.config(),
        sidecar_path=dep.sidecar_path,
        signing_backend=dep.record_backend,
        attestation={entry.entry_hash: TenantAttestation(tenant=_TENANT)},  # plain
    )
    assert record.rows[0].verification_disposition is VerificationDisposition.FOUR_TUPLE_REAL

    # The explicit operator decision still grants exemption.
    dep.record_path.unlink()
    record = author_cutover_record(
        dep.config(),
        sidecar_path=dep.sidecar_path,
        signing_backend=dep.record_backend,
        attestation={entry.entry_hash: TenantAttestation(tenant=_TENANT, placeholder_exempt=True)},
    )
    assert record.rows[0].verification_disposition is (VerificationDisposition.PLACEHOLDER_EXEMPT)


def test_already_tagged_rows_require_external_binding(dep: _Deployment) -> None:
    """The wrapper tag is mutable — an already-tagged row authenticates
    ONLY through an external binding: a MISMATCHED attestation (relabel
    evidence) refuses; absent attestation the declared-TOFU decision
    QUARANTINES under the observed tag; neither → unattested refusal."""
    entry = dep.signed_entry("ref-1")
    dep.writer().append("tenant-b", entry)

    # Mismatch — refuse.
    with pytest.raises(RecordMigrationError, match="relabeled wrapper"):
        author_cutover_record(
            dep.config(),
            sidecar_path=dep.sidecar_path,
            signing_backend=dep.record_backend,
            attestation={entry.entry_hash: TenantAttestation(tenant="tenant-c")},
        )
    assert not dep.record_path.exists()

    # No attestation, no TOFU — unattested refusal.
    with pytest.raises(RecordMigrationError, match="no attestation"):
        author_cutover_record(
            dep.config(),
            sidecar_path=dep.sidecar_path,
            signing_backend=dep.record_backend,
            attestation={},
        )

    # Declared TOFU — quarantined under the OBSERVED tag.
    record = author_cutover_record(
        dep.config(),
        sidecar_path=dep.sidecar_path,
        signing_backend=dep.record_backend,
        attestation={},
        tofu_quarantine_tenant=_TENANT,
    )
    row = record.rows[0]
    assert row.source_tag == "tenant-b"
    assert row.tenant_scope == "tenant-b"
    assert row.verification_disposition is VerificationDisposition.QUARANTINED


# ---------------------------------------------------------------------------
# Merge-gate test-witness lens (PR #1069) — alias-guard + CLI-author gaps.
# ---------------------------------------------------------------------------


def test_deleted_retagged_destination_still_fails_coverage(dep: _Deployment) -> None:
    """Alias-target MEMBERSHIP is load-bearing: post-retag, deleting the
    tenant-tagged destination row must still fail coverage — the record
    vouches for the alias TARGET's presence, never for absence."""
    entry = dep.signed_entry("ref-1", placeholder=True)
    dep.writer().append(None, entry)
    record = dep.write_record(_row(entry.entry_hash))
    retag_sidecar(dep.config(), sidecar_path=dep.sidecar_path, signing_backend=dep.record_backend)
    dep.sidecar_path.write_text("", encoding="utf-8")  # destination row deleted

    fresh = dep.writer(cutover_record=record)
    with pytest.raises(ValueError, match="truncated or lost"):
        fresh.read_full_entries_for_tenant(None)

    # The APPEND-time join (`_assert_is_refs_covered_locked`, the fold-path
    # `alias in digests` term) must fail the same truncation — round-2
    # merge-gate lens: the read-path term alone left the append path free
    # to extend a silently-truncated history.
    appender = dep.writer(cutover_record=record)
    with pytest.raises(ValueError, match="truncated or lost"):
        appender.append(_TENANT, dep.signed_entry("ref-new"))


def test_rewrapped_quarantined_row_never_alias_covered(dep: _Deployment) -> None:
    """The QUARANTINE exclusion in the alias derivation is load-bearing: an
    externally-rewrapped quarantined row (`_single` -> tenant tag — the
    wrapper is attacker-writable) must FAIL coverage, never be silently
    alias-covered into tenant readability."""
    entry = dep.signed_entry("ref-q")
    dep.writer().append(None, entry)
    record = dep.write_record(
        _row(entry.entry_hash, disposition=VerificationDisposition.QUARANTINED)
    )
    retag_sidecar(dep.config(), sidecar_path=dep.sidecar_path, signing_backend=dep.record_backend)
    rows = [json.loads(line) for line in dep.sidecar_path.read_text().splitlines() if line.strip()]
    assert rows[0]["tenant_tag"] == "_single"  # quarantined stayed
    rows[0]["tenant_tag"] = _TENANT  # the attacker's rewrap
    dep.sidecar_path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

    fresh = dep.writer(cutover_record=record)
    with pytest.raises(ValueError, match="truncated or lost"):
        fresh.read_full_entries_for_tenant(None)


def test_cli_author_then_retag_end_to_end(
    dep: _Deployment, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The `--author --retag` CLI path through the real `main(argv)`: both
    attestation value shapes parse (plain tenant -> four_tuple_real;
    explicit object -> placeholder_exempt), `--tofu-quarantine` reaches the
    library (unattested row quarantined), authoring precedes retag, and the
    invocation exits 0 with the sidecar retagged."""
    from harness_runtime.admin.migrate_audit_sidecar import main

    exempt_entry = dep.signed_entry("ref-exempt", placeholder=True)
    real_entry = dep.signed_entry("ref-real")
    tofu_entry = dep.signed_entry("ref-tofu", placeholder=True)
    writer = dep.writer()
    writer.append(None, exempt_entry)
    writer.append(None, real_entry)
    writer.append(None, tofu_entry)

    attestation_path = dep.root / "attestation.json"
    attestation_path.write_text(
        json.dumps(
            {
                exempt_entry.entry_hash: {"tenant": _TENANT, "placeholder_exempt": True},
                real_entry.entry_hash: _TENANT,
            }
        ),
        encoding="utf-8",
    )
    config_path = dep.root / "harness.toml"
    config_path.write_text(
        "\n".join(
            [
                "[runtime]",
                'deployment_surface = "local-development"',
                f'repository_root = "{dep.root}"',
                'default_topology = "single-threaded-linear"',
                'persona_tier = "multi-tenant-compliance"',
                f'tenant_id = "{_TENANT}"',
                f'audit_cutover_record_path = "{dep.record_path}"',
                f'audit_cutover_record_key_id = "{_RECORD_KEY}"',
                f'audit_ledger_binding_id = "{_BINDING}"',
                "",
                "[runtime.audit_signing]",
                'backend = "aws-kms"',
                "[runtime.audit_signing.key_arns]",
                f'"{_ROW_KEY}" = "{_ARN_ROW}"',
                f'"{_RECORD_KEY}" = "{_ARN_RECORD}"',
                f'"harness-runtime-redaction-token" = "{_ARN_ROW}-redaction"',
                f'"harness-runtime-dev" = "{_ARN_ROW}-dev"',
                f'"harness-cost-attribution-v1" = "{_ARN_ROW}-cost"',
                "",
                "[runtime.otel]",
                'otlp_endpoint = "http://localhost:4318"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "harness_runtime.config.audit_signing.make_audit_signing_backend",
        lambda config: dep.record_backend,
    )
    exit_code = main(
        [
            str(dep.ledger_path),
            "--author",
            "--retag",
            "--runtime-config",
            str(config_path),
            "--attestation",
            str(attestation_path),
            "--tofu-quarantine",
            "tenant-tofu",
        ]
    )
    assert exit_code == 0, capsys.readouterr().err
    record_line = dep.record_path.read_text().splitlines()[0]
    record = AuditCutoverRecord.model_validate_json(record_line)
    dispositions = {row.entry_hash: row.verification_disposition for row in record.rows}
    assert dispositions[exempt_entry.entry_hash] is VerificationDisposition.PLACEHOLDER_EXEMPT
    assert dispositions[real_entry.entry_hash] is VerificationDisposition.FOUR_TUPLE_REAL
    assert dispositions[tofu_entry.entry_hash] is VerificationDisposition.QUARANTINED
    tags = {
        json.loads(line)["tenant_tag"]
        for line in dep.sidecar_path.read_text().splitlines()
        if line.strip()
    }
    assert tags == {_TENANT, "_single"}  # readable rows retagged; quarantined stayed

    # Malformed attestation value shape → usage exit 2, nothing changed.
    attestation_path.write_text(json.dumps({exempt_entry.entry_hash: 7}), encoding="utf-8")
    exit_code = main(
        [
            str(dep.ledger_path),
            "--author",
            "--runtime-config",
            str(config_path),
            "--attestation",
            str(attestation_path),
        ]
    )
    assert exit_code == 2


# ---------------------------------------------------------------------------
# Post-gate-fix codex findings (this leg).
# ---------------------------------------------------------------------------


def test_tagged_baseline_pair_requires_external_binding(dep: _Deployment) -> None:
    """A tagged baseline pair's tag is mutable sidecar data — it needs the
    same external binding as already-tagged full rows: matching attestation
    → exempt; TOFU → quarantined under the observed tag; mismatch/absent →
    refusal."""
    entry = dep.signed_entry("ref-full", placeholder=True)
    dep.writer().append(None, entry)
    baseline_hash = "e" * 64
    dep.append_baseline_line([("tenant-b", baseline_hash)])

    base_attestation = {entry.entry_hash: TenantAttestation(tenant=_TENANT)}
    with pytest.raises(RecordMigrationError, match="no attestation"):
        author_cutover_record(
            dep.config(),
            sidecar_path=dep.sidecar_path,
            signing_backend=dep.record_backend,
            attestation=dict(base_attestation),
        )
    with pytest.raises(RecordMigrationError, match="relabeled wrapper"):
        author_cutover_record(
            dep.config(),
            sidecar_path=dep.sidecar_path,
            signing_backend=dep.record_backend,
            attestation={
                **base_attestation,
                baseline_hash: TenantAttestation(tenant="tenant-c"),
            },
        )
    record = author_cutover_record(
        dep.config(),
        sidecar_path=dep.sidecar_path,
        signing_backend=dep.record_backend,
        attestation={
            **base_attestation,
            baseline_hash: TenantAttestation(tenant="tenant-b"),
        },
    )
    by_hash = {row.entry_hash: row for row in record.rows}
    assert by_hash[baseline_hash].verification_disposition is (
        VerificationDisposition.PLACEHOLDER_EXEMPT
    )
    assert by_hash[baseline_hash].source_tag == "tenant-b"


def test_source_keyed_attestation_disambiguates_shared_hash(dep: _Deployment) -> None:
    """Two already-tagged rows legitimately sharing a legacy entry_hash
    across tenants attest independently through the source-keyed form
    `"<source_tag>:<entry_hash>"` — hash-only keying refused the second as
    relabeled."""
    entry = dep.signed_entry("ref-shared")
    writer = dep.writer()
    writer.append("tenant-b", entry)
    writer.append("tenant-c", entry)  # same hash, different tenant scope

    record = author_cutover_record(
        dep.config(),
        sidecar_path=dep.sidecar_path,
        signing_backend=dep.record_backend,
        attestation={
            f"tenant-b:{entry.entry_hash}": TenantAttestation(tenant="tenant-b"),
            f"tenant-c:{entry.entry_hash}": TenantAttestation(tenant="tenant-c"),
        },
    )
    scopes = {row.source_tag for row in record.rows}
    assert scopes == {"tenant-b", "tenant-c"}


def test_lower_tier_config_without_redaction_key_accepted(dep: _Deployment) -> None:
    """The tokenizer predicate mirrors bootstrap: at a sub-MTC tier the
    redaction-token key is NOT required — record modes accept the same
    config normal bootstrap accepts."""
    entry = dep.signed_entry("ref-1", placeholder=True)
    dep.writer().append(None, entry)
    solo_map = {
        _ROW_KEY: _ARN_ROW,
        _RECORD_KEY: _ARN_RECORD,
        "harness-runtime-dev": _ARN_ROW + "-dev",
        "harness-cost-attribution-v1": _ARN_ROW + "-cost",
        # redaction-token key ABSENT — valid sub-MTC
    }
    config = dep.config().model_copy(
        update={
            "persona_tier": PersonaTier.SOLO_DEVELOPER,
            "tenant_id": None,
            "audit_signing": AuditSigningConfig(
                backend=AuditSigningBackendKind.AWS_KMS, key_arns=solo_map
            ),
        }
    )
    record = author_cutover_record(
        config,
        sidecar_path=dep.sidecar_path,
        signing_backend=dep.record_backend,
        attestation={entry.entry_hash: TenantAttestation(tenant=_TENANT)},
    )
    assert record.rows
