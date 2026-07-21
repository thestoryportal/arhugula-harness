"""`U-RT-138` — `harness-inspect` §13.5 audit-verification witnesses.

The plan-named Tests block (Runtime plan v2.49 §1.5) driven through the real
CLI entry point (`inspect.main(argv)`) — never the helper in isolation — so
every witness exercises the engagement predicate, the config load, the IS
`audit:` ref resolution, AND the disposition, exactly as an operator's
invocation would.

The `--signing-key-map` backends are monkeypatched at
`harness_runtime.config.audit_signing.make_audit_signing_backend` (imported
INSIDE `_load_key_map`) to in-memory Ed25519 backends — real sign/verify
crypto, no AWS. The retag-mode half of the forged-record surface (a forged
record driving RETAGGING rather than inspection) belongs to `U-RT-139`
(`harness migrate-audit-sidecar`), not this file.
"""

from __future__ import annotations

import json
import os
import stat
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from harness_is.jsonl_event_ledger_lifecycle import JsonlLedgerHandle
from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier
from harness_is.state_ledger_write import EntryPayload, WriteKey, append_ledger_entry
from harness_od.audit_cutover_record import (
    AuditCutoverRecord,
    AuditCutoverRecordRow,
    VerificationDisposition,
    sign_cutover_record,
)
from harness_od.audit_ledger_types import (
    AuditLedgerEntry,
    AuditPayload,
    SignatureAlgorithm,
    StateLedgerEntryRef,
    compute_entry_hash,
)
from harness_od.multi_tenant_trace_separation_and_audit_ledger import sign_audit_entry
from harness_runtime.admin.inspect import main
from harness_runtime.types import AuditSigningBackendKind

if TYPE_CHECKING:
    from harness_runtime.types import AuditSigningConfig

_GENESIS = "0" * 64
_ROW_KEY = "row-key"
_RECORD_KEY = "record-key"
_BINDING = "sidecar-1"
_TENANT = "tenant-a"


class _Ed25519Backend:
    """TEST-ONLY `SigningBackend` double (real Ed25519 sign + verify)."""

    algorithm = "ed25519"

    def __init__(self) -> None:
        self._private_key = Ed25519PrivateKey.generate()

    def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
        del key_id, key_period
        return self._private_key.sign(message)

    def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
        del key_id, key_period
        try:
            self._private_key.public_key().verify(signature, message)
            return True
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Fixture builder.
# ---------------------------------------------------------------------------


class _Fixture:
    """One deployment's worth of §13.5 inputs under `root`."""

    def __init__(self, root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        self.root = root
        self.ledger_path = root / "state.jsonl"
        self.sidecar_path = root / "audit-entries.jsonl"
        self.key_map_path = root / "key-map.json"
        self.record_path = root / "cutover-record"
        self.config_path = root / "harness.toml"
        self.row_backend = _Ed25519Backend()
        self.record_backend = _Ed25519Backend()
        self._backends_by_key_id: dict[str, object] = {
            _ROW_KEY: self.row_backend,
            _RECORD_KEY: self.record_backend,
        }

        def fake_make_backend(config: AuditSigningConfig) -> object:
            key_id = next(iter(config.key_arns))
            return self._backends_by_key_id[key_id]

        monkeypatch.setattr(
            "harness_runtime.config.audit_signing.make_audit_signing_backend",
            fake_make_backend,
        )

    # -- inputs ------------------------------------------------------------

    def write_config(
        self,
        *,
        tier: str = "multi-tenant-compliance",
        pinned_key: str | None = _RECORD_KEY,
        binding: str | None = _BINDING,
    ) -> None:
        lines = [
            "[runtime]",
            'deployment_surface = "local-development"',
            f'repository_root = "{self.root}"',
            'default_topology = "single-threaded-linear"',
            f'persona_tier = "{tier}"',
        ]
        if pinned_key is not None:
            lines.append(f'audit_cutover_record_key_id = "{pinned_key}"')
        if binding is not None:
            lines.append(f'audit_ledger_binding_id = "{binding}"')
        lines += ["", "[runtime.otel]", 'otlp_endpoint = "http://localhost:4318"']
        self.config_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def write_key_map(self, *entries: tuple[str, str]) -> None:
        """Each entry is `(algorithm_value, key_id)`."""
        payload = {
            f"{algo}:{key_id}": {
                "backend": AuditSigningBackendKind.AWS_KMS.value,
                "key_arns": {key_id: f"arn:aws:kms:us-east-1:000000000000:key/{key_id}"},
            }
            for algo, key_id in entries
        }
        self.key_map_path.write_text(json.dumps(payload), encoding="utf-8")

    def signed_entry(self, core: str, *, tenant_id: str | None) -> AuditLedgerEntry:
        payload = AuditPayload(
            entry_core=StateLedgerEntryRef(core),
            audit_namespace_attrs={"audit.actor": "x"},
            prior_entry_hash=_GENESIS,
        )
        sig_attrs = sign_audit_entry(
            payload,
            _ROW_KEY,
            SignatureAlgorithm.ED25519,
            backend=self.row_backend,
            tenant_id=tenant_id,
        )
        return AuditLedgerEntry(
            payload=payload, signature_attrs=sig_attrs, entry_hash=compute_entry_hash(payload)
        )

    def write_sidecar(
        self,
        rows: list[tuple[str, AuditLedgerEntry]],
        *,
        baseline: list[tuple[str, str]] | None = None,
    ) -> None:
        lines = [
            json.dumps({"tenant_tag": tag, "entry": entry.model_dump(mode="json")})
            for tag, entry in rows
        ]
        if baseline is not None:
            # The writer's real `adopt_legacy_is_refs` shape: ONE row with
            # an ARRAY of [tag, hash] pairs.
            lines.append(json.dumps({"legacy_baseline": [[t, h] for t, h in baseline]}))
        self.sidecar_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def write_record(
        self,
        *rows: AuditCutoverRecordRow,
        algorithm: SignatureAlgorithm = SignatureAlgorithm.ED25519,
        key_id: str = _RECORD_KEY,
        binding: str = _BINDING,
        signer: object | None = None,
        tamper: bool = False,
    ) -> None:
        record = AuditCutoverRecord(
            schema_version=1,
            authored_at=datetime(2026, 7, 20, tzinfo=UTC),
            algorithm=algorithm,
            key_id=key_id,
            ledger_binding_id=binding,
            rows=rows,
        )
        backend = signer if signer is not None else self.record_backend
        signature = sign_cutover_record(record, backend=backend)  # type: ignore[arg-type]
        if tamper:
            signature = bytes([signature[0] ^ 0xFF]) + signature[1:]
        self.record_path.write_text(
            record.model_dump_json() + "\n" + signature.hex() + "\n", encoding="utf-8"
        )

    def write_ledger(self, audit_refs: list[str]) -> None:
        """IS state ledger whose entries carry the given `action_id`s (the
        `audit:` refs the inspector cross-checks the sidecar against).
        Truncates any prior ledger (callers re-write the whole ref set)."""
        self.ledger_path.unlink(missing_ok=True)
        self.ledger_path.touch()
        handle = JsonlLedgerHandle(canonical_path=self.ledger_path, exists=True, entry_count=0)
        actor = Actor(actor_class=ActorClass.AGENT, actor_id="harness-runtime")
        for i, ref in enumerate(audit_refs or ["action-0"]):
            payload = EntryPayload(
                action_id=Identifier(ref),
                idempotency_key=Identifier(f"idem-{i}"),
                actor=actor,
                timestamp=datetime(2026, 7, 20, 12, 0, i, tzinfo=UTC),
            )
            write_key = WriteKey(
                thread_id=Identifier(f"thread-{i}"),
                step_id=Identifier(f"step-{i}"),
                idempotency_key=Identifier(f"idem-{i}"),
            )
            append_ledger_entry(handle, payload, write_key)
            count = sum(1 for line in self.ledger_path.read_text().splitlines() if line.strip())
            handle = JsonlLedgerHandle(
                canonical_path=self.ledger_path, exists=True, entry_count=count
            )

    # -- invocation --------------------------------------------------------

    def argv(self, *extra: str, config: bool = True) -> list[str]:
        args = ["--ledger-path", str(self.ledger_path), "--audit-sidecar", str(self.sidecar_path)]
        if config:
            args += ["--runtime-config", str(self.config_path)]
        return [*args, *extra]

    def full_verification_argv(self, *extra: str) -> list[str]:
        return self.argv(
            "--signing-key-map",
            str(self.key_map_path),
            "--cutover-record",
            str(self.record_path),
            *extra,
        )


@pytest.fixture
def fx(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> _Fixture:
    return _Fixture(tmp_path, monkeypatch)


def _greenfield_passing(fx: _Fixture) -> None:
    """Greenfield v1.101+ shape: five-tuple tenant rows + authenticated
    EMPTY record + matching IS `audit:` refs."""
    entry = fx.signed_entry("ref-1", tenant_id=_TENANT)
    fx.write_sidecar([(_TENANT, entry)])
    fx.write_ledger([f"audit:{_TENANT}:{entry.entry_hash}"])
    fx.write_config()
    fx.write_key_map(("ed25519", _ROW_KEY), ("ed25519", _RECORD_KEY))
    fx.write_record()


# ---------------------------------------------------------------------------
# Disposition witnesses (plan-named).
# ---------------------------------------------------------------------------


def test_mtc_inspection_without_backend_inputs_exits_nonzero_with_explicit_unverified_disposition(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """OD v1.34 §21.2.2 row 8: at MULTI_TENANT_COMPLIANCE, backend inputs
    are REQUIRED — no silent hash-only success. Mutation probe: dropping the
    `is_mtc` branch would fall through to hash-only exit 0 → FAILS."""
    entry = fx.signed_entry("ref-1", tenant_id=_TENANT)
    fx.write_sidecar([(_TENANT, entry)])
    fx.write_ledger([f"audit:{_TENANT}:{entry.entry_hash}"])
    fx.write_config(tier="multi-tenant-compliance")

    exit_code = main(fx.argv())
    out = capsys.readouterr().out
    assert exit_code == 3
    assert "UNVERIFIED" in out
    assert "RT-FAIL-AUDIT-UNVERIFIED" in out
    assert "--signing-key-map" in out and "--cutover-record" in out


def test_lower_tier_with_authoritative_config_no_inputs_preserves_hash_only_verbatim(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """Sub-MTC tier + authoritative config + NO verification inputs — the
    pre-v1.101 hash-only summary byte-verbatim (same stdout as a run that
    never engaged the audit surface), exit 0."""
    fx.write_ledger(["action-0", "action-1"])
    fx.write_config(tier="solo-developer", pinned_key=None, binding=None)

    # Baseline: NOT engaged (no sidecar file, no audit args, no config arg).
    baseline_code = main(["--ledger-path", str(fx.ledger_path)])
    baseline_out = capsys.readouterr().out
    assert baseline_code == 0

    # Engaged via an existing sidecar; sub-MTC config; no verification inputs.
    entry = fx.signed_entry("ref-1", tenant_id=None)
    fx.write_sidecar([("_single", entry)])
    exit_code = main(fx.argv())
    out = capsys.readouterr().out
    assert exit_code == 0
    assert out == baseline_out


def test_absent_authoritative_config_reports_unverified_nonzero(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """Engaged without `--runtime-config` → explicit UNVERIFIED, nonzero
    exit: the config DEFAULT tier is SOLO_DEVELOPER and is never assumed
    (an unconfigured MTC inspection must never silently pass)."""
    entry = fx.signed_entry("ref-1", tenant_id=None)
    fx.write_sidecar([("_single", entry)])
    fx.write_ledger([f"audit:_single:{entry.entry_hash}"])

    exit_code = main(fx.argv(config=False))
    out = capsys.readouterr().out
    assert exit_code == 3
    assert "UNVERIFIED" in out
    assert "--runtime-config" in out


@pytest.mark.parametrize("tier", ["multi-tenant-compliance", "solo-developer"])
def test_rows_present_without_record_unverified_nonzero(
    fx: _Fixture, capsys: pytest.CaptureFixture[str], tier: str
) -> None:
    """The cutover record is required whenever verification is requested —
    era is NEVER observation-inferred. A key-map WITHOUT a record never
    degrades to hash-only, at MTC (row-8 posture) or below (the partial-
    input branch: verification was requested, the set is incomplete)."""
    entry = fx.signed_entry("ref-1", tenant_id=_TENANT)
    fx.write_sidecar([(_TENANT, entry)])
    fx.write_ledger([f"audit:{_TENANT}:{entry.entry_hash}"])
    fx.write_config(tier=tier)
    fx.write_key_map(("ed25519", _ROW_KEY))

    exit_code = main(fx.argv("--signing-key-map", str(fx.key_map_path)))
    out = capsys.readouterr().out
    assert exit_code == 3
    assert "UNVERIFIED" in out
    assert "--cutover-record" in out


def test_greenfield_empty_record_then_five_tuple_rows_pass(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """A greenfield v1.101+ deployment: authenticated EMPTY cutover record +
    five-tuple tenant-scoped rows + matching IS `audit:` refs → VERIFIED,
    exit 0. Mutation probe: tampering the row signature flips this to
    FAILED/exit 4 (`test_forged_...` covers the record half)."""
    _greenfield_passing(fx)

    exit_code = main(fx.full_verification_argv("--expected-tenant", _TENANT))
    out = capsys.readouterr().out
    assert exit_code == 0, out
    assert "VERIFIED" in out


def test_surplus_sidecar_row_fails_mtc_inspection(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """Reverse coverage: a sidecar row absent from the IS ledger's `audit:`
    refs is SURPLUS — a copied/planted row fails the MTC audit (exit 4),
    never silently passes."""
    _greenfield_passing(fx)
    fx.write_ledger(["action-0"])  # no audit: ref for the sidecar row

    exit_code = main(fx.full_verification_argv("--expected-tenant", _TENANT))
    out = capsys.readouterr().out
    assert exit_code == 4
    assert "FAILED" in out
    assert "SURPLUS" in out


def test_retagged_rows_not_surplus_through_alias_projection(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """Migrated history: the sidecar row is tenant-tagged but the IS action
    id still reads `audit:_single:<hash>` — the record-derived alias
    projection (`source_tag`) matches it, so it is NOT surplus, and its
    FOUR_TUPLE_REAL disposition verifies. (The retag-mode WRITE half — the
    record actually driving a sidecar rewrite — belongs to `U-RT-139`.)"""
    entry = fx.signed_entry("ref-1", tenant_id=None)  # genuine four-tuple sig
    fx.write_sidecar([(_TENANT, entry)])
    fx.write_ledger([f"audit:_single:{entry.entry_hash}"])
    fx.write_config()
    fx.write_key_map(("ed25519", _ROW_KEY), ("ed25519", _RECORD_KEY))
    fx.write_record(
        AuditCutoverRecordRow(
            source_tag="_single",
            tenant_scope=_TENANT,
            entry_hash=entry.entry_hash,
            verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
        )
    )

    exit_code = main(fx.full_verification_argv("--expected-tenant", _TENANT))
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "VERIFIED" in out


# ---------------------------------------------------------------------------
# Record-trust witnesses.
# ---------------------------------------------------------------------------


def test_forged_cutover_record_rejected_typed_never_treated_as_absent(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """A record failing signature verification against the pinned key is a
    TYPED rejection (exit 3, forged/untrusted on stderr) — never downgraded
    to absent-record fallback, never a hash-only pass."""
    _greenfield_passing(fx)
    fx.write_record(tamper=True)

    exit_code = main(fx.full_verification_argv("--expected-tenant", _TENANT))
    captured = capsys.readouterr()
    assert exit_code == 3
    assert "forged/untrusted cutover record" in captured.err
    # The summary still prints (it COMPOSES, round-4 P2) — the no-fallback
    # guard is the nonzero exit + the explicit UNVERIFIED audit section.
    assert "audit verification: UNVERIFIED" in captured.out


def test_inspect_rejects_record_signed_by_row_key(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """Pinned-key physical distinctness at inspect: a record whose key_id
    also signs ordinary sidecar rows is rejected even when its signature
    verifies — the record key must be physically distinct."""
    entry = fx.signed_entry("ref-1", tenant_id=_TENANT)
    fx.write_sidecar([(_TENANT, entry)])
    fx.write_ledger([f"audit:{_TENANT}:{entry.entry_hash}"])
    fx.write_config(pinned_key=_ROW_KEY)
    fx.write_key_map(("ed25519", _ROW_KEY))
    fx.write_record(key_id=_ROW_KEY, signer=fx.row_backend)

    # Re-sign the sidecar row under the SAME key_id the record claims.
    exit_code = main(fx.full_verification_argv("--expected-tenant", _TENANT))
    captured = capsys.readouterr()
    assert exit_code == 3
    assert "also signs ordinary" in captured.err


def test_inspect_algorithm_authority_is_the_mapping(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """The algorithm authority is the key-map, never the record's own
    metadata: a record claiming an algorithm with no mapping entry for
    `(algorithm, key_id)` is rejected, not trusted on its self-claim."""

    class _EcdsaClaimBackend(_Ed25519Backend):
        algorithm = "ecdsa-p256"

    _greenfield_passing(fx)
    signer = _EcdsaClaimBackend()
    fx.write_record(algorithm=SignatureAlgorithm.ECDSA_P256, signer=signer)

    exit_code = main(fx.full_verification_argv("--expected-tenant", _TENANT))
    captured = capsys.readouterr()
    assert exit_code == 3
    assert "no key-map entry" in captured.err
    assert "mapping" in captured.err


def test_record_without_pinned_binding_rejected_typed(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """A config lacking `audit_ledger_binding_id` cannot bind a record to
    this deployment's sidecar — typed rejection (the §21.2.2 row-4 cross-
    ledger guard is REQUIRED), never an unwrapped verifier defect."""
    _greenfield_passing(fx)
    fx.write_config(binding=None)

    exit_code = main(fx.full_verification_argv("--expected-tenant", _TENANT))
    captured = capsys.readouterr()
    assert exit_code == 3
    # The MISSING-config diagnosis specifically — not the (different)
    # record-vs-config disagreement message a bare `!=` comparison against
    # `None` would produce.
    assert "no audit_ledger_binding_id in the supplied runtime config" in captured.err


# ---------------------------------------------------------------------------
# Read-only invariant.
# ---------------------------------------------------------------------------


def test_inspect_verification_writes_nothing_readonly_fixture(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """C-RT-13 read-only invariant extends to the §13.5 verification path:
    the full verification run succeeds against a read-only directory tree
    (any write attempt would EACCES)."""
    _greenfield_passing(fx)

    ro_file = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
    ro_dir = ro_file | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    for child in fx.root.iterdir():
        os.chmod(child, ro_file)
    os.chmod(fx.root, ro_dir)
    try:
        exit_code = main(fx.full_verification_argv("--expected-tenant", _TENANT))
        out = capsys.readouterr().out
        assert exit_code == 0
        assert "VERIFIED" in out
    finally:
        os.chmod(fx.root, stat.S_IRWXU)
        for child in fx.root.iterdir():
            os.chmod(child, stat.S_IRUSR | stat.S_IWUSR)


# ---------------------------------------------------------------------------
# Codex round-1 findings (this leg) — coverage, grouping, baseline shapes.
# ---------------------------------------------------------------------------


def test_deleted_sidecar_row_with_ledger_ref_fails_forward_coverage(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """FORWARD coverage: an IS `audit:` ref whose sidecar row was DELETED
    fails the MTC audit (exit 4) — an authenticated empty record must never
    report VERIFIED over truncated audit history."""
    _greenfield_passing(fx)
    fx.write_sidecar([])  # the row is gone; the ledger ref survives

    exit_code = main(fx.full_verification_argv("--expected-tenant", _TENANT))
    out = capsys.readouterr().out
    assert exit_code == 4
    assert "FAILED" in out
    assert "forward coverage" in out


def test_baseline_only_four_tuple_real_is_unverified_not_passed(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """A FOUR_TUPLE_REAL record disposition on a BASELINE-ONLY identity (the
    writer\'s `{"legacy_baseline": [[tag, hash], ...]}` array shape) has no
    full entry to cryptographically verify — explicit UNVERIFIED nonzero,
    never PASSED (and never a parse-drop that reports a false divergence)."""
    entry = fx.signed_entry("ref-1", tenant_id=None)
    fx.write_sidecar([], baseline=[("_single", entry.entry_hash)])
    fx.write_ledger([f"audit:_single:{entry.entry_hash}"])
    fx.write_config()
    fx.write_key_map(("ed25519", _ROW_KEY), ("ed25519", _RECORD_KEY))
    fx.write_record(
        AuditCutoverRecordRow(
            source_tag="_single",
            tenant_scope=_TENANT,
            entry_hash=entry.entry_hash,
            verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
        )
    )

    exit_code = main(fx.full_verification_argv("--expected-tenant", _TENANT))
    out = capsys.readouterr().out
    assert exit_code == 3, out
    assert "UNVERIFIED" in out


def test_multi_tenant_sidecar_verifies_per_scope(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """The OD verifier is single-scope — a shared sidecar with two tenants\'
    valid five-tuple rows must verify per tenant group, not falsely report
    SIGNATURE_INVALID by reconstructing B\'s message under A\'s segment."""
    entry_a = fx.signed_entry("ref-a", tenant_id="tenant-a")
    entry_b = fx.signed_entry("ref-b", tenant_id="tenant-b")
    fx.write_sidecar([("tenant-a", entry_a), ("tenant-b", entry_b)])
    fx.write_ledger(
        [f"audit:tenant-a:{entry_a.entry_hash}", f"audit:tenant-b:{entry_b.entry_hash}"]
    )
    fx.write_config()
    fx.write_key_map(("ed25519", _ROW_KEY), ("ed25519", _RECORD_KEY))
    fx.write_record()

    # Full audit (no --expected-tenant): both groups verify.
    exit_code = main(fx.full_verification_argv())
    out = capsys.readouterr().out
    assert exit_code == 0, out
    assert "VERIFIED" in out

    # Scoped audit: tenant-a alone verifies; B\'s rows are out of scope,
    # their ledger coverage still satisfied globally.
    exit_code = main(fx.full_verification_argv("--expected-tenant", "tenant-a"))
    out = capsys.readouterr().out
    assert exit_code == 0, out
    assert "VERIFIED" in out


def test_alias_collision_across_tenants_order_independent(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """Aliases are keyed by DESTINATION identity `(tenant_scope,
    entry_hash)` — two record rows legitimately sharing a pre-v1.34 entry
    hash across tenants must not overwrite each other (hash-only keying made
    reverse coverage row-order-dependent: the LATER row\'s source tag won,
    falsely marking the migrated row surplus)."""
    entry = fx.signed_entry("ref-1", tenant_id=None)  # four-tuple era
    h = entry.entry_hash
    fx.write_sidecar([(_TENANT, entry)], baseline=[("tenant-b", h)])
    fx.write_ledger([f"audit:_single:{h}", f"audit:tenant-b:{h}"])
    fx.write_config()
    fx.write_key_map(("ed25519", _ROW_KEY), ("ed25519", _RECORD_KEY))
    fx.write_record(
        # The _single→tenant-a migrated row FIRST; the same-hash tenant-b
        # row SECOND (the order that poisons a hash-only alias dict).
        AuditCutoverRecordRow(
            source_tag="_single",
            tenant_scope=_TENANT,
            entry_hash=h,
            verification_disposition=VerificationDisposition.FOUR_TUPLE_REAL,
        ),
        AuditCutoverRecordRow(
            source_tag="tenant-b",
            tenant_scope="tenant-b",
            entry_hash=h,
            verification_disposition=VerificationDisposition.PLACEHOLDER_EXEMPT,
        ),
    )

    exit_code = main(fx.full_verification_argv("--expected-tenant", _TENANT))
    out = capsys.readouterr().out
    assert exit_code == 0, out
    assert "VERIFIED" in out


def test_missing_cutover_record_file_unverified_not_traceback(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """A missing/unreadable `--cutover-record` FILE is an input failure —
    explicit UNVERIFIED nonzero, never a raw traceback and never treated as
    forged or absent."""
    _greenfield_passing(fx)
    fx.record_path.unlink()

    exit_code = main(fx.full_verification_argv("--expected-tenant", _TENANT))
    out = capsys.readouterr().out
    assert exit_code == 3
    assert "UNVERIFIED" in out
    assert "--cutover-record unreadable" in out


# ---------------------------------------------------------------------------
# Codex round-2 findings (this leg).
# ---------------------------------------------------------------------------


def test_config_only_mtc_inspection_engages_unverified(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """`--runtime-config` is §13.5 input (v) — it ENGAGES the audit surface
    by itself. An MTC config with no sidecar and no other audit inputs must
    produce the explicit UNVERIFIED nonzero result, never the legacy
    summary; a sub-MTC config alone still preserves the plain summary."""
    fx.write_ledger(["action-0"])
    fx.write_config(tier="multi-tenant-compliance")

    # ONLY --runtime-config — no --audit-sidecar (whose mere presence
    # already engages); the default sidecar path does not exist.
    config_only = ["--ledger-path", str(fx.ledger_path), "--runtime-config", str(fx.config_path)]
    exit_code = main(config_only)
    out = capsys.readouterr().out
    assert exit_code == 3
    assert "UNVERIFIED" in out

    fx.write_config(tier="solo-developer", pinned_key=None, binding=None)
    exit_code = main(config_only)
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "read-only summary" in out


def test_unrecorded_baseline_identity_fails(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """Observed-vs-recorded completeness: a legacy-baseline identity the
    authenticated record does NOT claim (by source identity, any scope)
    must fail the audit — the scope grouping must never silently drop it
    (an empty signed record + a matching IS ref is not a pass)."""
    entry = fx.signed_entry("ref-1", tenant_id=None)
    fx.write_sidecar([], baseline=[("_single", entry.entry_hash)])
    fx.write_ledger([f"audit:_single:{entry.entry_hash}"])
    fx.write_config()
    fx.write_key_map(("ed25519", _ROW_KEY), ("ed25519", _RECORD_KEY))
    fx.write_record()  # authenticated EMPTY — claims nothing

    exit_code = main(fx.full_verification_argv("--expected-tenant", _TENANT))
    out = capsys.readouterr().out
    assert exit_code == 4, out
    assert "absent from the authenticated cutover record" in out


def test_record_key_sharing_row_material_rejected(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """Backing-material distinctness: a record key whose key-map entry
    aliases the SAME KMS ARN as a row-signing key is rejected even though
    the logical key_ids differ — logical distinctness is not physical
    independence."""
    _greenfield_passing(fx)
    shared_arn = "arn:aws:kms:us-east-1:000000000000:key/shared"
    payload = {
        f"ed25519:{_ROW_KEY}": {
            "backend": AuditSigningBackendKind.AWS_KMS.value,
            "key_arns": {_ROW_KEY: shared_arn},
        },
        f"ed25519:{_RECORD_KEY}": {
            "backend": AuditSigningBackendKind.AWS_KMS.value,
            "key_arns": {_RECORD_KEY: shared_arn},
        },
    }
    fx.key_map_path.write_text(json.dumps(payload), encoding="utf-8")

    exit_code = main(fx.full_verification_argv("--expected-tenant", _TENANT))
    captured = capsys.readouterr()
    assert exit_code == 3
    assert "shares backing key material" in captured.err


# ---------------------------------------------------------------------------
# Codex round-3 findings (this leg).
# ---------------------------------------------------------------------------


def test_duplicate_sidecar_identity_fails_closed(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """The writer never appends a duplicate `(tenant_tag, entry_hash)` —
    a duplicated row is external mutation and must fail closed at read,
    never verify (coverage sets and independent signatures would both
    still pass a byte-identical duplicate)."""
    _greenfield_passing(fx)
    line = fx.sidecar_path.read_text(encoding="utf-8").splitlines()[0]
    fx.sidecar_path.write_text(line + "\n" + line + "\n", encoding="utf-8")

    exit_code = main(fx.full_verification_argv("--expected-tenant", _TENANT))
    out = capsys.readouterr().out
    assert exit_code == 3, out
    assert "duplicate identity" in out


def test_unmapped_row_key_fails_closed(fx: _Fixture, capsys: pytest.CaptureFixture[str]) -> None:
    """A persisted row-signing key with no key-map entry makes record/row
    physical separation UNPROVABLE — rejected, even though an exempt
    disposition would have skipped its signature resolution entirely."""
    _greenfield_passing(fx)
    fx.write_key_map(("ed25519", _RECORD_KEY))  # row key mapping removed

    exit_code = main(fx.full_verification_argv("--expected-tenant", _TENANT))
    captured = capsys.readouterr()
    assert exit_code == 3
    assert "cannot be proven for unmapped persisted keys" in captured.err


def test_config_resident_cutover_record_path_is_inspect_default(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """A fully configured MTC deployment (config carries
    `audit_cutover_record_path`) verifies without duplicating the record
    path on the CLI — the config field is the inspect-time default for
    input (iv), with an explicit `--cutover-record` still overriding."""
    _greenfield_passing(fx)
    config_text = fx.config_path.read_text(encoding="utf-8")
    config_text = config_text.replace(
        "[runtime.otel]",
        f'audit_cutover_record_path = "{fx.record_path}"\n\n[runtime.otel]',
    )
    fx.config_path.write_text(config_text, encoding="utf-8")

    argv = fx.argv(
        "--signing-key-map", str(fx.key_map_path), "--expected-tenant", _TENANT
    )  # NO --cutover-record
    exit_code = main(argv)
    out = capsys.readouterr().out
    assert exit_code == 0, out
    assert "VERIFIED" in out


def test_reserved_or_empty_expected_tenant_is_input_disposition(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """`--expected-tenant _single` (reserved) or an empty string is an
    INPUT error — the explicit nonzero UNVERIFIED disposition, never an
    unwrapped OD-normalizer ValueError traceback mid-walk."""
    _greenfield_passing(fx)
    for bad_tenant in ("_single", ""):
        exit_code = main(fx.full_verification_argv("--expected-tenant", bad_tenant))
        out = capsys.readouterr().out
        assert exit_code == 3, (bad_tenant, out)
        assert "--expected-tenant invalid" in out


# ---------------------------------------------------------------------------
# Codex round-4 findings (this leg).
# ---------------------------------------------------------------------------


def test_undispositioned_single_row_fails_mtc(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """At MTC every legacy `_single` identity must be cutover-dispositioned
    — a full `_single` row the record omits must NOT verify through the
    untenanted fallback walk (exit 4). A sub-MTC single-tenant deployment
    with the same inputs legitimately verifies its `_single` history."""
    entry = fx.signed_entry("ref-1", tenant_id=None)
    fx.write_sidecar([("_single", entry)])
    fx.write_ledger([f"audit:_single:{entry.entry_hash}"])
    fx.write_config()  # MTC
    fx.write_key_map(("ed25519", _ROW_KEY), ("ed25519", _RECORD_KEY))
    fx.write_record()  # authenticated EMPTY — no disposition for the row

    exit_code = main(fx.full_verification_argv())
    out = capsys.readouterr().out
    assert exit_code == 4, out
    assert "NO cutover-record disposition" in out

    fx.write_config(tier="solo-developer")
    exit_code = main(fx.full_verification_argv())
    out = capsys.readouterr().out
    assert exit_code == 0, out
    assert "VERIFIED" in out


def test_row_key_algorithm_mismatch_rejected(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """Row keys are mapped by exact `(algorithm, key_id)` pair — an
    `ed25519:row-key` row is NOT covered by an `ecdsa-p256:row-key`
    mapping entry (key_id-only matching would prove nothing)."""
    _greenfield_passing(fx)
    fx.write_key_map(("ecdsa-p256", _ROW_KEY), ("ed25519", _RECORD_KEY))

    exit_code = main(fx.full_verification_argv("--expected-tenant", _TENANT))
    captured = capsys.readouterr()
    assert exit_code == 3
    assert "no exact" in captured.err
    assert "ed25519:row-key" in captured.err


def test_summary_composes_with_audit_disposition(
    fx: _Fixture, capsys: pytest.CaptureFixture[str]
) -> None:
    """The §13.5 audit report COMPOSES with the established C-RT-13 summary
    (ledger head, recent entries, spans, cost rollup) — it never replaces
    it, in either output mode."""
    _greenfield_passing(fx)

    exit_code = main(fx.full_verification_argv("--expected-tenant", _TENANT))
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "harness-inspect — read-only summary" in out
    assert "head_hash:" in out
    assert "Spans: N/A" in out
    assert "audit verification: VERIFIED" in out

    exit_code = main(fx.full_verification_argv("--expected-tenant", _TENANT, "--json"))
    out = capsys.readouterr().out
    assert exit_code == 0
    payload = json.loads(out)
    assert "head_hash" in payload
    assert payload["audit_verification"]["disposition"] == "verified"
