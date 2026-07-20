"""`U-RT-134` — `audit_signing_fail_closed` RuntimeConfig field + dual
env-loader registration + MTC config-validation invariant witnesses.

Implements `Spec_Harness_Runtime_v1.md` v1.101 §3 C-RT-03 Invariants +
`Implementation_Plan_Harness_Runtime_v2_49.md` §1.1. Scope boundary: this
unit owns the RuntimeConfig carrier + dual env-loader registration + the
bootstrap config-validation site (missing/invalid input rejection +
greenfield cutover-record signing). It does NOT touch the ten
`except AUDIT_SIGNING_HARD_FAILURES` runtime call sites — those still
swallow unconditionally today (confirmed by direct read); wiring them to
consult the resolved flag is the co-land-pinned U-RT-136/U-RT-137 siblings'
scope, not this one's.
"""

from __future__ import annotations

import hashlib
import hmac
from pathlib import Path

import pytest
from harness_core import PersonaTier
from harness_core.deployment_surface import DeploymentSurface
from harness_cp.topology_pattern import TopologyPattern
from harness_od.audit_cutover_record import AuditCutoverRecord, sign_cutover_record
from harness_od.audit_ledger_types import SignatureAlgorithm
from harness_runtime.config.loader import _ENV_SCALAR_FIELDS, materialize_runtime_config
from harness_runtime.config_source import _RuntimeEnvSettings
from harness_runtime.lifecycle.audit_signing_fail_closed_validation import (
    AuditSigningConfigInvalidError,
    IncompatibleConfigVersion,
    resolve_audit_signing_fail_closed,
    validate_and_initialize_mtc_audit_signing,
)
from harness_runtime.types import (
    AuditSigningBackendKind,
    AuditSigningConfig,
    CollectorConfig,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
)

_ARN_A = "arn:aws:kms:us-east-1:111122223333:key/row-signing-key"
_ARN_B = "arn:aws:kms:us-east-1:111122223333:key/cutover-record-key"


class _FakeBackend:
    """TEST-ONLY `SigningBackend` double — deterministic HMAC-SHA512 (64
    bytes, matching the ed25519 width), not real asymmetric crypto. No
    `cryptography` dependency needed for this unit's stdlib-only checks."""

    def __init__(self, algorithm: str = "ed25519", secret: bytes = b"test-secret") -> None:
        self.algorithm = algorithm
        self._secret = secret

    def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
        del key_id, key_period
        return hmac.new(self._secret, message, hashlib.sha512).digest()

    def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
        del key_id, key_period
        expected = hmac.new(self._secret, message, hashlib.sha512).digest()
        return hmac.compare_digest(expected, signature)


def _config(
    tmp_path: Path,
    *,
    persona_tier: PersonaTier = PersonaTier.SOLO_DEVELOPER,
    tenant_id: str | None = None,
    audit_signing_fail_closed: bool | None = None,
    backend: AuditSigningBackendKind = AuditSigningBackendKind.NONE,
    key_arns: dict[str, str] | None = None,
    audit_cutover_record_path: str | None = None,
    audit_cutover_record_key_id: str | None = None,
    audit_ledger_binding_id: str | None = None,
) -> RuntimeConfig:
    """Minimal valid `RuntimeConfig` for U-RT-134 witnesses."""
    return RuntimeConfig(
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        repository_root=tmp_path,
        path_bindings=PathBindingConfig(),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4317"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        mcp_clients=[],
        persona_tier=persona_tier,
        tenant_id=tenant_id,
        audit_signing_fail_closed=audit_signing_fail_closed,
        audit_signing=AuditSigningConfig(backend=backend, key_arns=key_arns or {}),
        audit_cutover_record_path=audit_cutover_record_path,
        audit_cutover_record_key_id=audit_cutover_record_key_id,
        audit_ledger_binding_id=audit_ledger_binding_id,
    )


# ---------------------------------------------------------------------------
# resolve_audit_signing_fail_closed — per-persona default resolution.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("persona_tier", [PersonaTier.SOLO_DEVELOPER, PersonaTier.TEAM_BINDING])
def test_default_resolves_off_below_mtc(tmp_path: Path, persona_tier: PersonaTier) -> None:
    config = _config(tmp_path, persona_tier=persona_tier)
    assert resolve_audit_signing_fail_closed(config) is False


def test_default_resolves_on_at_mtc(tmp_path: Path) -> None:
    config = _config(
        tmp_path,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        tenant_id="acme",
        backend=AuditSigningBackendKind.AWS_KMS,
        key_arns={"cutover-key": _ARN_B},
        audit_cutover_record_path=str(tmp_path / "record.json"),
        audit_cutover_record_key_id="cutover-key",
        audit_ledger_binding_id="sidecar-1",
    )
    assert resolve_audit_signing_fail_closed(config) is True


def test_explicit_value_overrides_persona_default(tmp_path: Path) -> None:
    config = _config(
        tmp_path, persona_tier=PersonaTier.TEAM_BINDING, audit_signing_fail_closed=True
    )
    assert resolve_audit_signing_fail_closed(config) is True


# ---------------------------------------------------------------------------
# Witness (a) — flag config-validation.
# ---------------------------------------------------------------------------


def _mtc_ready_kwargs(tmp_path: Path) -> dict[str, object]:
    return dict(
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        tenant_id="acme",
        backend=AuditSigningBackendKind.AWS_KMS,
        key_arns={"cutover-key": _ARN_B},
        audit_cutover_record_path=str(tmp_path / "record.json"),
        audit_cutover_record_key_id="cutover-key",
        audit_ledger_binding_id="sidecar-1",
    )


def test_mtc_explicit_false_rejected_at_config_validation(tmp_path: Path) -> None:
    kwargs = _mtc_ready_kwargs(tmp_path)
    kwargs["audit_signing_fail_closed"] = False
    config = _config(tmp_path, **kwargs)
    with pytest.raises(AuditSigningConfigInvalidError, match="audit_signing_fail_closed=false"):
        validate_and_initialize_mtc_audit_signing(config, signing_backend=_FakeBackend())


@pytest.mark.parametrize(
    ("persona_tier", "explicit"),
    [
        (PersonaTier.SOLO_DEVELOPER, True),
        (PersonaTier.TEAM_BINDING, True),
        (PersonaTier.MULTI_TENANT_COMPLIANCE, None),
    ],
)
def test_fail_closed_on_without_backend_rejected_at_bootstrap_every_tier(
    tmp_path: Path, persona_tier: PersonaTier, explicit: bool | None
) -> None:
    """Resolved-ON without a configured backend is `RT-FAIL-CONFIG-VERSION`
    at EVERY persona tier — including below MTC via an explicit opt-in, and
    at MTC via the per-persona default (no explicit value needed there)."""
    tenant_id = "acme" if persona_tier is PersonaTier.MULTI_TENANT_COMPLIANCE else None
    config = _config(
        tmp_path,
        persona_tier=persona_tier,
        audit_signing_fail_closed=explicit,
        tenant_id=tenant_id,
        backend=AuditSigningBackendKind.NONE,
    )
    with pytest.raises(IncompatibleConfigVersion, match="audit_signing.backend"):
        validate_and_initialize_mtc_audit_signing(config, signing_backend=None)


def test_env_only_override_honored_through_both_loaders() -> None:
    """Mutation probe: removing EITHER loader registration fails this test."""
    assert "audit_signing_fail_closed" in _ENV_SCALAR_FIELDS
    env_key, coerce = _ENV_SCALAR_FIELDS["audit_signing_fail_closed"]
    assert env_key == "HARNESS_AUDIT_SIGNING_FAIL_CLOSED"
    assert coerce("true") is True

    config = materialize_runtime_config(
        env={
            "HARNESS_DEPLOYMENT_SURFACE": "local-development",
            "HARNESS_REPOSITORY_ROOT": "/tmp",
            "HARNESS_DEFAULT_TOPOLOGY": "single-threaded-linear",
            "HARNESS_AUDIT_SIGNING_FAIL_CLOSED": "true",
        },
        otel=OTelConfig(otlp_endpoint="http://localhost:4317"),
    )
    assert config.audit_signing_fail_closed is True

    assert "audit_signing_fail_closed" in _RuntimeEnvSettings.model_fields
    sidecar = _RuntimeEnvSettings.model_validate({"audit_signing_fail_closed": "true"})
    assert sidecar.audit_signing_fail_closed is True


def test_env_typo_rejected_not_silently_false() -> None:
    """Out-of-family Codex [P1] finding: `_parse_bool`'s lenient fallback
    silently resolved an unrecognized spelling (e.g. a typo'd `treu`) to
    `False` — fail-OPEN on a typo for a field whose entire purpose is
    enforcing fail-closed audit signing. The API `materialize_runtime_config`
    path now rejects it; the pydantic-settings `_RuntimeEnvSettings` path
    was ALREADY strict (confirmed directly) and is unaffected."""
    _env_key, coerce = _ENV_SCALAR_FIELDS["audit_signing_fail_closed"]
    with pytest.raises(ValueError, match="not a recognized boolean spelling"):
        coerce("treu")
    with pytest.raises(ValueError):
        materialize_runtime_config(
            env={
                "HARNESS_DEPLOYMENT_SURFACE": "local-development",
                "HARNESS_REPOSITORY_ROOT": "/tmp",
                "HARNESS_DEFAULT_TOPOLOGY": "single-threaded-linear",
                "HARNESS_AUDIT_SIGNING_FAIL_CLOSED": "treu",
            },
            otel=OTelConfig(otlp_endpoint="http://localhost:4317"),
        )


def test_lower_tier_explicit_true_with_backend_accepted(tmp_path: Path) -> None:
    """The U-RT-134 half of this witness: a lower-tier explicit opt-in WITH
    a backend is ACCEPTED at config validation (no raise) and resolves to
    fail-closed=True. The site-level "the ten sites honor it" half is the
    co-land-pinned U-RT-136/U-RT-137 siblings' scope — those sites currently
    swallow unconditionally (confirmed by direct read) and are not touched
    here."""
    config = _config(
        tmp_path,
        persona_tier=PersonaTier.TEAM_BINDING,
        audit_signing_fail_closed=True,
        backend=AuditSigningBackendKind.AWS_KMS,
        key_arns={"harness-runtime-dev": _ARN_A},
    )
    validate_and_initialize_mtc_audit_signing(config, signing_backend=_FakeBackend())
    assert resolve_audit_signing_fail_closed(config) is True


def test_non_mtc_record_opt_in_without_backend_rejected(tmp_path: Path) -> None:
    """Out-of-family Codex probe finding: opting into a cutover record at a
    non-MTC tier, with `audit_signing_fail_closed` unset/False (so nothing
    else requires a backend), previously reached Pass 3's greenfield-sign
    and hit a bare `AssertionError` — now a typed `RT-FAIL-CONFIG` rejection
    at config validation, before any backend I/O."""
    config = _config(
        tmp_path,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        backend=AuditSigningBackendKind.NONE,
        key_arns={"record-key": _ARN_A},
        audit_cutover_record_path=str(tmp_path / "record.json"),
        audit_cutover_record_key_id="record-key",
        audit_ledger_binding_id="sidecar-1",
    )
    with pytest.raises(AuditSigningConfigInvalidError, match="backend is required"):
        validate_and_initialize_mtc_audit_signing(config, signing_backend=None)


def test_blank_string_record_fields_treated_as_missing(tmp_path: Path) -> None:
    """Out-of-family Codex probe finding: an empty-string
    `audit_ledger_binding_id=""` at MTC passed every `is None` check and
    crashed `AuditCutoverRecord`'s own validator as a raw, unwrapped
    `ValidationError` inside greenfield signing — now caught at config
    validation, uniformly for all three record fields, exactly as if the
    field were `None`."""
    for blank_field in (
        "audit_cutover_record_path",
        "audit_cutover_record_key_id",
        "audit_ledger_binding_id",
    ):
        kwargs = _mtc_ready_kwargs(tmp_path)
        kwargs[blank_field] = "   "  # whitespace-only, not None
        config = _config(tmp_path, **kwargs)
        with pytest.raises(IncompatibleConfigVersion, match=blank_field):
            validate_and_initialize_mtc_audit_signing(config, signing_backend=_FakeBackend())


def test_blank_record_path_at_non_mtc_does_not_create_whitespace_named_file(
    tmp_path: Path,
) -> None:
    """Out-of-family Codex [P2] finding: `validate_mtc_audit_signing_config`
    normalizes a whitespace-only `audit_cutover_record_path` to "absent"
    (skipping the record checks entirely at a non-MTC tier where nothing
    else requires it) — `initialize_mtc_audit_signing_record` must apply
    the SAME normalization, or it would read the RAW blank value and
    attempt to create a record file literally named `"   "` on disk."""
    config = _config(
        tmp_path,
        persona_tier=PersonaTier.TEAM_BINDING,
        backend=AuditSigningBackendKind.AWS_KMS,
        key_arns={"harness-runtime-dev": _ARN_A},
        audit_cutover_record_path="   ",
        audit_cutover_record_key_id="   ",
        audit_ledger_binding_id="   ",
    )
    validate_and_initialize_mtc_audit_signing(config, signing_backend=_FakeBackend())
    assert not (tmp_path / "   ").exists()
    assert list(tmp_path.iterdir()) == []


# ---------------------------------------------------------------------------
# Witness (c) — MTC tenant-bootstrap invariant.
# ---------------------------------------------------------------------------


def test_mtc_invalid_tenant_rejected_at_config_validation(tmp_path: Path) -> None:
    """`tenant_id=None` at MTC is rejected at MY bootstrap-level check.
    `""` / `"_single"` are rejected EARLIER, at `RuntimeConfig` construction
    itself (the pre-existing `_tenant_id_not_reserved` field validator) —
    both are "rejected at config validation", via two different layers."""
    kwargs = _mtc_ready_kwargs(tmp_path)
    kwargs["tenant_id"] = None
    config = _config(tmp_path, **kwargs)
    with pytest.raises(IncompatibleConfigVersion, match="tenant_id"):
        validate_and_initialize_mtc_audit_signing(config, signing_backend=_FakeBackend())

    for reserved in ("", "_single"):
        kwargs2 = _mtc_ready_kwargs(tmp_path)
        kwargs2["tenant_id"] = reserved
        with pytest.raises(ValueError, match="reserved"):
            _config(tmp_path, **kwargs2)


# ---------------------------------------------------------------------------
# Record-key resolution + physical-distinctness + algorithm-authority.
# ---------------------------------------------------------------------------


def test_bootstrap_rejects_record_key_sharing_row_material(tmp_path: Path) -> None:
    kwargs = _mtc_ready_kwargs(tmp_path)
    kwargs["key_arns"] = {"cutover-key": _ARN_A, "row-key": _ARN_A}
    config = _config(tmp_path, **kwargs)
    with pytest.raises(AuditSigningConfigInvalidError, match="physically distinct"):
        validate_and_initialize_mtc_audit_signing(config, signing_backend=_FakeBackend())


def test_bootstrap_rejects_record_key_id_equal_to_row_signing_consumer_id(tmp_path: Path) -> None:
    """Out-of-family Codex [P1] finding: pinning the SAME literal key_id
    the stage-5 composers/cost builders already use as the row-signing key
    (`harness-runtime-dev` / `harness-cost-attribution-v1`) is the
    SAME-entry case the distinctness check cannot see (there is no
    "other" id to compare against when the pinned id equals one of them)."""
    kwargs = _mtc_ready_kwargs(tmp_path)
    kwargs["audit_cutover_record_key_id"] = "harness-runtime-dev"
    kwargs["key_arns"] = {"harness-runtime-dev": _ARN_A}
    config = _config(tmp_path, **kwargs)
    with pytest.raises(AuditSigningConfigInvalidError, match="row-signing consumer key ids"):
        validate_and_initialize_mtc_audit_signing(config, signing_backend=_FakeBackend())


def test_bootstrap_rejects_redaction_token_key_as_record_key(tmp_path: Path) -> None:
    """Out-of-family Codex [P1] round-3 finding: the redaction-token map's
    signing key (`harness-runtime-redaction-token`) is equally a row-signing
    consumer at MTC — pinning it as the record key must be rejected by the
    same same-entry check as the composer/cost-builder ids."""
    kwargs = _mtc_ready_kwargs(tmp_path)
    kwargs["audit_cutover_record_key_id"] = "harness-runtime-redaction-token"
    kwargs["key_arns"] = {"harness-runtime-redaction-token": _ARN_A}
    config = _config(tmp_path, **kwargs)
    with pytest.raises(AuditSigningConfigInvalidError, match="row-signing consumer key ids"):
        validate_and_initialize_mtc_audit_signing(config, signing_backend=_FakeBackend())


def test_existing_non_regular_record_path_rejected_not_overwritten(tmp_path: Path) -> None:
    """Out-of-family Codex [P2] round-3 finding: an existing DIRECTORY (or
    special file / broken symlink) at the record path must be a typed
    rejection — not treated as greenfield (untyped `IsADirectoryError` at
    the rename; a broken symlink would be silently overwritten)."""
    record_dir = tmp_path / "record.json"
    record_dir.mkdir()
    kwargs = _mtc_ready_kwargs(tmp_path)
    kwargs["audit_cutover_record_path"] = str(record_dir)
    config = _config(tmp_path, **kwargs)
    with pytest.raises(AuditSigningConfigInvalidError, match="not a regular file"):
        validate_and_initialize_mtc_audit_signing(config, signing_backend=_FakeBackend())
    assert record_dir.is_dir()  # untouched

    broken_symlink = tmp_path / "record2.json"
    broken_symlink.symlink_to(tmp_path / "does-not-exist")
    kwargs["audit_cutover_record_path"] = str(broken_symlink)
    config = _config(tmp_path, **kwargs)
    with pytest.raises(AuditSigningConfigInvalidError, match="not a regular file"):
        validate_and_initialize_mtc_audit_signing(config, signing_backend=_FakeBackend())
    assert broken_symlink.is_symlink()  # untouched, not replaced


def test_bootstrap_rejects_record_key_sharing_arn_spelled_as_bare_uuid(tmp_path: Path) -> None:
    """Out-of-family Codex [P1] finding: AWS KMS accepts both a full ARN
    and its bare key UUID for the SAME physical key — two logical ids
    spelled differently but resolving to the same key must still be caught
    by the physical-distinctness check."""
    kwargs = _mtc_ready_kwargs(tmp_path)
    kwargs["key_arns"] = {
        "cutover-key": "arn:aws:kms:us-east-1:111122223333:key/shared-uuid-123",
        "row-key": "shared-uuid-123",  # same physical key, bare-UUID spelling
    }
    config = _config(tmp_path, **kwargs)
    with pytest.raises(AuditSigningConfigInvalidError, match="physically distinct"):
        validate_and_initialize_mtc_audit_signing(config, signing_backend=_FakeBackend())


def test_bootstrap_rejects_unresolvable_record_key_id(tmp_path: Path) -> None:
    kwargs = _mtc_ready_kwargs(tmp_path)
    kwargs["audit_cutover_record_key_id"] = "does-not-exist"
    config = _config(tmp_path, **kwargs)
    with pytest.raises(AuditSigningConfigInvalidError, match="does not resolve"):
        validate_and_initialize_mtc_audit_signing(config, signing_backend=_FakeBackend())


def test_record_algorithm_authority_is_the_mapping(tmp_path: Path) -> None:
    """A record whose stored algorithm differs from the configured
    backend's algorithm is REJECTED even when its `key_id` matches — the
    algorithm authority is the backend/mapping, never the record's own
    (attacker-rewritable) metadata."""
    record_path = tmp_path / "record.json"
    ecdsa_backend = _FakeBackend(algorithm="ecdsa-p256")
    record = AuditCutoverRecord(
        schema_version=1,
        authored_at=__import__("datetime").datetime.now(__import__("datetime").UTC),
        algorithm=SignatureAlgorithm.ECDSA_P256,
        key_id="cutover-key",
        ledger_binding_id="sidecar-1",
        rows=(),
    )
    signature = sign_cutover_record(record, backend=ecdsa_backend)
    record_path.write_text(
        record.model_dump_json() + "\n" + signature.hex() + "\n", encoding="utf-8"
    )

    kwargs = _mtc_ready_kwargs(tmp_path)
    kwargs["audit_cutover_record_path"] = str(record_path)
    config = _config(tmp_path, **kwargs)
    with pytest.raises(AuditSigningConfigInvalidError, match="algorithm"):
        validate_and_initialize_mtc_audit_signing(config, signing_backend=_FakeBackend())


# ---------------------------------------------------------------------------
# MTC record-input requirement + greenfield initialization.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "missing_field",
    ["audit_cutover_record_path", "audit_cutover_record_key_id", "audit_ledger_binding_id"],
)
def test_mtc_bootstrap_without_record_inputs_rejected(tmp_path: Path, missing_field: str) -> None:
    kwargs = _mtc_ready_kwargs(tmp_path)
    kwargs[missing_field] = None
    config = _config(tmp_path, **kwargs)
    with pytest.raises(IncompatibleConfigVersion, match=missing_field):
        validate_and_initialize_mtc_audit_signing(config, signing_backend=_FakeBackend())


def test_greenfield_empty_record_signs_configured_binding(tmp_path: Path) -> None:
    record_path = tmp_path / "record.json"
    kwargs = _mtc_ready_kwargs(tmp_path)
    kwargs["audit_cutover_record_path"] = str(record_path)
    kwargs["audit_ledger_binding_id"] = "sidecar-configured"
    config = _config(tmp_path, **kwargs)
    backend = _FakeBackend()

    assert not record_path.is_file()
    validate_and_initialize_mtc_audit_signing(config, signing_backend=backend)
    assert record_path.is_file()

    lines = record_path.read_text(encoding="utf-8").splitlines()
    record = AuditCutoverRecord.model_validate_json(lines[0])
    signature = bytes.fromhex(lines[1])
    assert record.rows == ()
    assert record.ledger_binding_id == "sidecar-configured"
    assert record.key_id == "cutover-key"
    from harness_od.audit_cutover_record import verify_cutover_record_signature

    assert verify_cutover_record_signature(record, signature, backend=backend) is True

    # Re-running against the now-existing file takes the verify path, not
    # greenfield again — a second call must not raise or rewrite it.
    written_mtime = record_path.stat().st_mtime_ns
    validate_and_initialize_mtc_audit_signing(config, signing_backend=backend)
    assert record_path.stat().st_mtime_ns == written_mtime


def test_existing_record_with_wrong_binding_id_rejected(tmp_path: Path) -> None:
    """Fail-closed record↔config binding check (not record↔sidecar) — a
    record signed for a DIFFERENT deployment's binding id is rejected."""
    record_path = tmp_path / "record.json"
    backend = _FakeBackend()
    kwargs = _mtc_ready_kwargs(tmp_path)
    kwargs["audit_cutover_record_path"] = str(record_path)
    kwargs["audit_ledger_binding_id"] = "sidecar-original"
    original_config = _config(tmp_path, **kwargs)
    validate_and_initialize_mtc_audit_signing(original_config, signing_backend=backend)

    kwargs["audit_ledger_binding_id"] = "sidecar-different"
    mismatched_config = _config(tmp_path, **kwargs)
    with pytest.raises(AuditSigningConfigInvalidError, match="ledger_binding_id"):
        validate_and_initialize_mtc_audit_signing(mismatched_config, signing_backend=backend)


def test_greenfield_minting_rejected_when_sidecar_has_rows(tmp_path: Path) -> None:
    """Out-of-family Codex [P1] round-4 finding: the spec permits minting a
    signed EMPTY record only when the ledger is FRESH. An absent record
    alongside an audit sidecar that already carries rows is trust-anchor
    LOSS — a typed rejection, never a silent re-mint that would orphan
    every legacy disposition."""
    sidecar = tmp_path / "audit-entries.jsonl"
    # A well-formed row (the round-6 persisted-row key scan runs first and
    # must PASS — its key differs from the pinned record key) so the
    # freshness gate is the check that fires.
    sidecar.write_text(
        '{"tenant_tag": "_single", "entry": {"signature_attrs": '
        '{"audit_signature_key_id": "some-row-key"}}}\n',
        encoding="utf-8",
    )
    record_path = tmp_path / "record.json"
    kwargs = _mtc_ready_kwargs(tmp_path)
    kwargs["audit_cutover_record_path"] = str(record_path)
    config = _config(tmp_path, **kwargs)
    with pytest.raises(AuditSigningConfigInvalidError, match="NOT fresh"):
        validate_and_initialize_mtc_audit_signing(
            config, signing_backend=_FakeBackend(), audit_sidecar_path=sidecar
        )
    assert not record_path.exists()  # nothing minted

    # Control: an ABSENT (or empty) sidecar IS fresh — greenfield proceeds.
    fresh_sidecar = tmp_path / "no-such-sidecar.jsonl"
    validate_and_initialize_mtc_audit_signing(
        config, signing_backend=_FakeBackend(), audit_sidecar_path=fresh_sidecar
    )
    assert record_path.is_file()


def test_greenfield_minting_rejected_when_is_ledger_has_audit_refs(tmp_path: Path) -> None:
    """Out-of-family Codex [P1] round-5 finding: the hash-chained IS ledger
    is the freshness AUTHORITY — a deleted/truncated sidecar alongside
    surviving `audit:` IS refs must still read NOT-fresh (the sidecar-only
    check would pass exactly the loss case the gate exists for). A probe
    that RAISES also reads not-fresh (fail closed)."""
    record_path = tmp_path / "record.json"
    kwargs = _mtc_ready_kwargs(tmp_path)
    kwargs["audit_cutover_record_path"] = str(record_path)
    config = _config(tmp_path, **kwargs)
    absent_sidecar = tmp_path / "audit-entries.jsonl"  # deleted/never-written

    with pytest.raises(AuditSigningConfigInvalidError, match="NOT fresh"):
        validate_and_initialize_mtc_audit_signing(
            config,
            signing_backend=_FakeBackend(),
            audit_sidecar_path=absent_sidecar,
            ledger_has_audit_refs=lambda: True,
        )
    assert not record_path.exists()

    def _raising_probe() -> bool:
        raise OSError("simulated unreadable IS ledger")

    with pytest.raises(AuditSigningConfigInvalidError, match="NOT fresh"):
        validate_and_initialize_mtc_audit_signing(
            config,
            signing_backend=_FakeBackend(),
            audit_sidecar_path=absent_sidecar,
            ledger_has_audit_refs=_raising_probe,
        )
    assert not record_path.exists()

    # Control: no IS refs + no sidecar rows = genuinely fresh → mint proceeds.
    validate_and_initialize_mtc_audit_signing(
        config,
        signing_backend=_FakeBackend(),
        audit_sidecar_path=absent_sidecar,
        ledger_has_audit_refs=lambda: False,
    )
    assert record_path.is_file()


def test_greenfield_signature_verified_before_publication(tmp_path: Path) -> None:
    """Out-of-family Codex [P1] round-5 finding: a backend that can SIGN
    but not VERIFY (KMS Sign/Verify are separate IAM permissions), or one
    emitting a wrong-but-correctly-sized signature, must fail THIS
    bootstrap — not persist a record every subsequent bootstrap rejects."""

    class _SignOnlyBackend(_FakeBackend):
        def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
            raise PermissionError("simulated missing kms:Verify permission")

    class _WrongSignatureBackend(_FakeBackend):
        def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
            return b"\x00" * 64  # correctly sized, cryptographically wrong

    record_path = tmp_path / "record.json"
    kwargs = _mtc_ready_kwargs(tmp_path)
    kwargs["audit_cutover_record_path"] = str(record_path)
    config = _config(tmp_path, **kwargs)

    with pytest.raises(AuditSigningConfigInvalidError, match="round-trip RAISED"):
        validate_and_initialize_mtc_audit_signing(config, signing_backend=_SignOnlyBackend())
    assert not record_path.exists()

    with pytest.raises(AuditSigningConfigInvalidError, match="verification round-trip"):
        validate_and_initialize_mtc_audit_signing(config, signing_backend=_WrongSignatureBackend())
    assert not record_path.exists()


def test_greenfield_temp_file_symlink_planting_does_not_overwrite_target(tmp_path: Path) -> None:
    """Out-of-family Codex [P1] round-4 finding: the temp file must be
    created with randomized-name/exclusive semantics (`tempfile.mkstemp`)
    — a co-located principal pre-creating the OLD predictable
    `.{name}.tmp-{pid}` path as a symlink must neither get its target
    overwritten with runtime privileges nor have the symlink renamed into
    the trusted record path."""
    import os as _os

    record_path = tmp_path / "record.json"
    victim = tmp_path / "victim.txt"
    victim.write_text("precious", encoding="utf-8")
    planted = record_path.with_name(f".{record_path.name}.tmp-{_os.getpid()}")
    planted.symlink_to(victim)

    kwargs = _mtc_ready_kwargs(tmp_path)
    kwargs["audit_cutover_record_path"] = str(record_path)
    config = _config(tmp_path, **kwargs)
    validate_and_initialize_mtc_audit_signing(config, signing_backend=_FakeBackend())

    assert victim.read_text(encoding="utf-8") == "precious"  # never followed
    assert record_path.is_file() and not record_path.is_symlink()
    lines = record_path.read_text(encoding="utf-8").splitlines()
    assert AuditCutoverRecord.model_validate_json(lines[0]).rows == ()


def test_record_key_used_by_persisted_sidecar_rows_rejected(tmp_path: Path) -> None:
    """Out-of-family Codex [P1] round-6 finding: the spec requires the
    pinned record key be distinct from EVERY key id appearing on ledger
    rows — including a historical/custom id persisted on existing sidecar
    rows that is no longer in `key_arns` nor in the hard-coded consumer
    set. An unparseable sidecar row is fail-closed (separation cannot be
    proven)."""
    import json as _json

    sidecar = tmp_path / "audit-entries.jsonl"
    row = {
        "tenant_tag": "_single",
        "entry": {"signature_attrs": {"audit_signature_key_id": "historical-key"}},
    }
    sidecar.write_text(_json.dumps(row) + "\n", encoding="utf-8")

    kwargs = _mtc_ready_kwargs(tmp_path)
    kwargs["audit_cutover_record_key_id"] = "historical-key"
    kwargs["key_arns"] = {"historical-key": _ARN_B}
    config = _config(tmp_path, **kwargs)
    with pytest.raises(AuditSigningConfigInvalidError, match="already used to sign"):
        validate_and_initialize_mtc_audit_signing(
            config, signing_backend=_FakeBackend(), audit_sidecar_path=sidecar
        )

    # Unparseable row → fail closed.
    sidecar.write_text("not-json\n", encoding="utf-8")
    with pytest.raises(AuditSigningConfigInvalidError, match="unparseable"):
        validate_and_initialize_mtc_audit_signing(
            config, signing_backend=_FakeBackend(), audit_sidecar_path=sidecar
        )


def test_record_path_colliding_with_sidecar_rejected(tmp_path: Path) -> None:
    """Out-of-family Codex [P2] round-6 finding: a record path resolving to
    the sidecar itself would write the two-line record into
    `audit-entries.jsonl`, which the audit writer later fails to parse —
    rejected before any branch."""
    sidecar = tmp_path / "audit-entries.jsonl"
    kwargs = _mtc_ready_kwargs(tmp_path)
    kwargs["audit_cutover_record_path"] = str(sidecar)
    config = _config(tmp_path, **kwargs)
    with pytest.raises(AuditSigningConfigInvalidError, match="sidecar itself"):
        validate_and_initialize_mtc_audit_signing(
            config, signing_backend=_FakeBackend(), audit_sidecar_path=sidecar
        )
    assert not sidecar.exists()  # nothing written


def test_explicit_false_at_mtc_wins_over_missing_inputs(tmp_path: Path) -> None:
    """Out-of-family Codex [P2] round-6 finding: an explicit
    `audit_signing_fail_closed=false` PROVES the config is v2-aware, so the
    invalid-VALUE taxonomy (`RT-FAIL-CONFIG`) must win over the
    missing-input version-incompat reading even when required MTC inputs
    are ALSO absent."""
    config = _config(
        tmp_path,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        audit_signing_fail_closed=False,
        # tenant/record inputs all missing — Pass 1 would have plenty to say.
    )
    with pytest.raises(AuditSigningConfigInvalidError, match="audit_signing_fail_closed=false"):
        validate_and_initialize_mtc_audit_signing(config, signing_backend=None)


def test_existing_record_with_trailing_lines_rejected(tmp_path: Path) -> None:
    """Out-of-family Codex [P2] round-6 finding: unsigned trailing content
    appended to the record file must be rejected — exactly one record line
    + one signature line, aside from the final newline."""
    record_path = tmp_path / "record.json"
    backend = _FakeBackend()
    kwargs = _mtc_ready_kwargs(tmp_path)
    kwargs["audit_cutover_record_path"] = str(record_path)
    config = _config(tmp_path, **kwargs)
    validate_and_initialize_mtc_audit_signing(config, signing_backend=backend)

    original = record_path.read_text(encoding="utf-8")
    record_path.write_text(original + "unsigned trailing garbage\n", encoding="utf-8")
    with pytest.raises(AuditSigningConfigInvalidError, match="exactly 2 lines"):
        validate_and_initialize_mtc_audit_signing(config, signing_backend=backend)


def test_existing_record_tampered_signature_rejected(tmp_path: Path) -> None:
    record_path = tmp_path / "record.json"
    backend = _FakeBackend()
    kwargs = _mtc_ready_kwargs(tmp_path)
    kwargs["audit_cutover_record_path"] = str(record_path)
    config = _config(tmp_path, **kwargs)
    validate_and_initialize_mtc_audit_signing(config, signing_backend=backend)

    lines = record_path.read_text(encoding="utf-8").splitlines()
    original_sig = bytes.fromhex(lines[1])
    flipped_first_byte = original_sig[0] ^ 0xFF
    tampered_sig = bytes([flipped_first_byte]) + original_sig[1:]
    record_path.write_text(lines[0] + "\n" + tampered_sig.hex() + "\n")
    with pytest.raises(AuditSigningConfigInvalidError, match="signature verification"):
        validate_and_initialize_mtc_audit_signing(config, signing_backend=backend)
