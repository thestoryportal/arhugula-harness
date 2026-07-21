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
                key_arns={_ROW_KEY: _ARN_ROW, _RECORD_KEY: _ARN_RECORD},
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
    dep: _Deployment, monkeypatch: pytest.MonkeyPatch
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
            placeholder_entry.entry_hash: _TENANT,
            real_entry.entry_hash: _TENANT,
            baseline_hash: _TENANT,
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
            attestation={entry.entry_hash: _TENANT},
        )
