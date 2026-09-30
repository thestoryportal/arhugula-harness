"""A configured audit cutover record must live inside the verified external state root.

Human decision (ticket arhugula-harness-trial-193, 2026-09-24): when `state_placement` is
declared and `audit_cutover_record_path` is configured, the record must resolve inside the
verified root BEFORE bootstrap, migration author/retag, or inspect's config-derived default
touches it. No placement keeps legacy behavior; a non-MTC absent record stays valid; explicit
`inspect --cutover-record` stays a read-only diagnostic override.

Provider-free. Bootstrap witnesses call the real initializer; CLI witnesses drive the real
`main(argv)` entry points with only the config loader and KMS backend factory substituted.
"""

# ruff: noqa: F811  (pytest fixtures are imported, then named as test parameters)
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

import pytest
from harness_core import PersonaTier
from harness_runtime.admin import inspect as inspect_cli
from harness_runtime.admin import migrate_audit_sidecar as migrate_cli
from harness_runtime.config.state_placement import (
    StatePlacementRefusal,
    StateRootPlacementError,
)
from harness_runtime.lifecycle.audit_signing_fail_closed_validation import (
    AuditSigningConfigInvalidError,
    initialize_mtc_audit_signing_record,
)
from harness_runtime.types import (
    AuditSigningBackendKind,
    AuditSigningConfig,
    RuntimeConfig,
    StatePlacementConfig,
    VerifiedStateRoot,
)

from .test_state_placement import world  # noqa: F401  (fixture)
from .test_state_placement_bootstrap import (  # noqa: F401
    Site,
    _durable_filesystem,  # autouse fixture: scratch dirs may be tmpfs
    site,  # fixture
)
from .test_u_rt_138_inspect_verification import (  # noqa: F401
    _greenfield_passing,
    fx,  # fixture
)
from .test_u_rt_139_record_modes import (  # noqa: F401
    _ARN_RECORD,
    _ARN_ROW,
    _BINDING,
    _RECORD_KEY,
    _ROW_KEY,
    _Deployment,
    _FakeBackend,
    _protected_result_store_key,  # autouse fixture
    _row,
)

Refusal = StatePlacementRefusal
_OUTSIDE = Refusal.PATH_OUTSIDE_ROOT.value


def _mtc(site: Site, record_path: str | None, *, placement: bool) -> RuntimeConfig:
    return site.config(
        placement=placement,
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        tenant_id="tenant-a",
        audit_signing=AuditSigningConfig(
            backend=AuditSigningBackendKind.AWS_KMS,
            key_arns={
                _ROW_KEY: _ARN_ROW,
                _RECORD_KEY: _ARN_RECORD,
                "harness-runtime-redaction-token": _ARN_ROW + "-redaction",
                "harness-runtime-dev": _ARN_ROW + "-dev",
                "harness-cost-attribution-v1": _ARN_ROW + "-cost",
            },
        ),
        audit_cutover_record_path=record_path,
        audit_cutover_record_key_id=_RECORD_KEY,
        audit_ledger_binding_id=_BINDING,
    )


def _init(
    config: RuntimeConfig,
    verified: VerifiedStateRoot | None,
    sidecar: Path,
    *,
    fresh: bool = True,
) -> Any:
    return initialize_mtc_audit_signing_record(
        config,
        signing_backend=_FakeBackend(),
        verified_state_root=verified,
        audit_sidecar_path=sidecar,
        ledger_has_audit_refs=lambda: not fresh,
    )


# --- bootstrap: stage-4 initializer ---------------------------------------------------


def test_an_outside_root_record_refuses_before_any_io(site: Site) -> None:
    config = _mtc(site, str(site.repo / ".harness" / "cutover.json"), placement=True)
    verified = site.stamp(config)
    before = site.snapshot()

    with pytest.raises(StateRootPlacementError) as refused:
        _init(config, verified, site.root / "audit-entries.jsonl")

    assert refused.value.reason is Refusal.PATH_OUTSIDE_ROOT
    # No record minted, no sidecar lock file, nothing else created anywhere.
    assert site.snapshot() == before


def test_a_relative_record_path_refuses_and_writes_nothing(
    site: Site, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = _mtc(site, "cutover.json", placement=True)
    verified = site.stamp(config)
    monkeypatch.chdir(site.repo)
    before = site.snapshot()

    with pytest.raises(StateRootPlacementError) as refused:
        _init(config, verified, site.root / "audit-entries.jsonl")

    assert refused.value.reason is Refusal.PATH_OUTSIDE_ROOT
    assert site.snapshot() == before


def test_an_in_root_symlink_to_a_record_outside_the_root_refuses(site: Site) -> None:
    outside = site.repo / ".harness" / "legacy-record.json"
    legacy = _mtc(site, str(outside), placement=False)
    _init(legacy, None, site.base / "legacy-sidecar.jsonl")  # a legacy record exists outside
    assert outside.is_file()

    config = _mtc(site, str(site.root / "cutover.json"), placement=True)
    verified = site.stamp(config)
    (site.root / "cutover.json").symlink_to(outside)

    with pytest.raises(StateRootPlacementError) as refused:
        _init(config, verified, site.root / "audit-entries.jsonl")
    assert refused.value.reason is Refusal.PATH_OUTSIDE_ROOT


def test_a_fresh_in_root_record_mints_inside_the_root_and_then_verifies(site: Site) -> None:
    record = site.root / "audit-cutover-record.json"
    config = _mtc(site, str(record), placement=True)
    verified = site.stamp(config)

    minted = _init(config, verified, site.root / "audit-entries.jsonl")
    assert record.is_file()
    assert minted is not None and minted.rows == ()

    written = record.stat().st_mtime_ns
    assert _init(config, verified, site.root / "audit-entries.jsonl") is not None
    assert record.stat().st_mtime_ns == written  # verified, never re-minted


def test_a_missing_in_root_record_on_a_nonfresh_ledger_is_still_trust_anchor_loss(
    site: Site,
) -> None:
    record = site.root / "audit-cutover-record.json"
    config = _mtc(site, str(record), placement=True)
    verified = site.stamp(config)

    with pytest.raises(AuditSigningConfigInvalidError, match="NOT fresh"):
        _init(config, verified, site.root / "audit-entries.jsonl", fresh=False)
    assert not record.exists()


def test_a_declared_placement_without_a_stamp_refuses_unverified(site: Site) -> None:
    config = _mtc(site, str(site.root / "audit-cutover-record.json"), placement=True)
    with pytest.raises(StateRootPlacementError) as refused:
        _init(config, None, site.root / "audit-entries.jsonl")
    assert refused.value.reason is Refusal.UNVERIFIED_PLACEMENT


def test_without_placement_an_outside_path_keeps_its_legacy_behavior(site: Site) -> None:
    record = site.repo / ".harness" / "legacy-record.json"
    config = _mtc(site, str(record), placement=False)
    assert _init(config, None, site.base / "legacy-sidecar.jsonl") is not None
    assert record.is_file()


def test_a_non_mtc_config_with_placement_and_no_record_stays_valid(site: Site) -> None:
    config = site.config(placement=True)
    verified = site.stamp(config)
    assert (
        initialize_mtc_audit_signing_record(
            config, signing_backend=None, verified_state_root=verified
        )
        is None
    )


def test_the_original_signed_bytes_verify_unchanged_after_a_copy_into_the_root(
    site: Site,
) -> None:
    """The stopped copy-to-root migration: no re-sign, the path is not a signed field."""
    outside = site.repo / ".harness" / "legacy-record.json"
    _init(_mtc(site, str(outside), placement=False), None, site.base / "legacy-sidecar.jsonl")

    inside = site.root / "audit-cutover-record.json"
    config = _mtc(site, str(inside), placement=True)
    verified = site.stamp(config)
    shutil.copyfile(outside, inside)

    assert _init(config, verified, site.root / "audit-entries.jsonl") is not None
    assert inside.read_bytes() == outside.read_bytes()


# --- migration CLI: author / retag prewrite refusal ----------------------------------


def _install_migration_config(
    monkeypatch: pytest.MonkeyPatch, dep: _Deployment, site: Site, record_path: Path
) -> RuntimeConfig:
    config = dep.config().model_copy(
        update={
            "repository_root": site.repo,
            "path_bindings": site.config(placement=True).path_bindings,
            "state_placement": StatePlacementConfig(state_root=site.root),
            "audit_cutover_record_path": str(record_path),
        }
    )
    monkeypatch.setattr(
        "harness_runtime.config_source.RuntimeConfigSource.load",
        classmethod(lambda cls, **_kw: config),
    )
    monkeypatch.setattr(
        "harness_runtime.config.audit_signing.make_audit_signing_backend",
        lambda _config: dep.record_backend,
    )
    return config


def _seed_history(dep: _Deployment) -> str:
    """One observed placeholder-era row, so the record modes have history to act on."""
    entry = dep.signed_entry("ref-1", placeholder=True)
    dep.writer().append(None, entry)
    return entry.entry_hash


_AUTHOR = ["--author", "--tofu-quarantine", "tenant-tofu"]


@pytest.mark.parametrize("mode", [_AUTHOR, ["--retag"]], ids=["author", "retag"])
def test_migration_refuses_an_outside_root_record_before_any_write(
    site: Site,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    mode: list[str],
) -> None:
    dep = _Deployment(tmp_path)
    entry_hash = _seed_history(dep)
    site.stamp(site.config(placement=True))  # the root exists and is marked
    outside = dep.record_path
    if mode == ["--retag"]:
        dep.write_record(_row(entry_hash))  # a valid record already exists outside the root
    _install_migration_config(monkeypatch, dep, site, outside)
    before = sorted(os.listdir(tmp_path))
    ledger_bytes = dep.ledger_path.read_bytes()
    sidecar_bytes = dep.sidecar_path.read_bytes()

    exit_code = migrate_cli.main([str(dep.ledger_path), *mode, "--runtime-config", "unused.toml"])

    captured = capsys.readouterr()
    assert exit_code != 0
    assert f"RT-FAIL-STATE-ROOT-PLACEMENT:{_OUTSIDE}" in captured.err
    assert "Traceback" not in captured.err
    assert ("--retag" in mode) == outside.exists()  # never created; a seeded one never touched
    assert sorted(os.listdir(tmp_path)) == before
    assert dep.ledger_path.read_bytes() == ledger_bytes
    assert dep.sidecar_path.read_bytes() == sidecar_bytes


@pytest.mark.parametrize("mode", [_AUTHOR, ["--retag"]], ids=["author", "retag"])
def test_migration_refuses_an_outside_root_record_before_backend_or_ledger_access(
    site: Site,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    mode: list[str],
) -> None:
    """The placement refusal must not be maskable: with the signing backend unavailable and
    the ledger read lock contended, an outside-root path still reports the placement class,
    and neither the backend factory nor the ledger read is ever reached."""
    from harness_core.cross_process_lock_deadline import CrossProcessLockTimeoutError
    from harness_runtime.config.audit_signing import SigningBackendSdkUnavailableError

    dep = _Deployment(tmp_path)
    entry_hash = _seed_history(dep)
    site.stamp(site.config(placement=True))
    outside = dep.record_path
    if mode == ["--retag"]:
        dep.write_record(_row(entry_hash))
    _install_migration_config(monkeypatch, dep, site, outside)
    reached: list[str] = []

    def _backend_unavailable(_config: object) -> object:
        reached.append("backend")
        raise SigningBackendSdkUnavailableError("backend down")

    def _ledger_contended(*_args: object, **_kwargs: object) -> object:
        reached.append("ledger")
        raise CrossProcessLockTimeoutError("ledger read lock contended")

    monkeypatch.setattr(
        "harness_runtime.config.audit_signing.make_audit_signing_backend", _backend_unavailable
    )
    monkeypatch.setattr("harness_is.state_ledger_write.read_ledger", _ledger_contended)
    before = sorted(os.listdir(tmp_path))
    sidecar_bytes = dep.sidecar_path.read_bytes()
    record_bytes = outside.read_bytes() if outside.exists() else None

    exit_code = migrate_cli.main([str(dep.ledger_path), *mode, "--runtime-config", "unused.toml"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert f"RT-FAIL-STATE-ROOT-PLACEMENT:{_OUTSIDE}" in captured.err
    assert reached == []
    assert sorted(os.listdir(tmp_path)) == before
    assert dep.sidecar_path.read_bytes() == sidecar_bytes
    assert (outside.read_bytes() if outside.exists() else None) == record_bytes


def test_migration_authors_a_record_inside_the_verified_root(
    site: Site,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    dep = _Deployment(tmp_path)
    _seed_history(dep)
    site.stamp(site.config(placement=True))
    inside = site.root / "audit-cutover-record.json"
    _install_migration_config(monkeypatch, dep, site, inside)

    exit_code = migrate_cli.main(
        [str(dep.ledger_path), *_AUTHOR, "--runtime-config", "unused.toml"]
    )

    assert exit_code == 0, capsys.readouterr().err
    assert inside.is_file()


def test_migration_refuses_when_the_declared_root_cannot_be_verified(
    site: Site,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    dep = _Deployment(tmp_path)  # the root was never bootstrapped: a probe never creates it
    _seed_history(dep)
    inside = site.root / "audit-cutover-record.json"
    _install_migration_config(monkeypatch, dep, site, inside)

    exit_code = migrate_cli.main(
        [str(dep.ledger_path), *_AUTHOR, "--runtime-config", "unused.toml"]
    )

    assert exit_code != 0
    assert "RT-FAIL-STATE-ROOT-PLACEMENT:" in capsys.readouterr().err
    assert not site.root.exists()


# --- inspect: config-derived default vs explicit diagnostic override ------------------


def _install_inspect_config(
    monkeypatch: pytest.MonkeyPatch,
    site: Site,
    record_path: Path | None,
    *,
    placement: bool = True,
) -> None:
    from harness_runtime.config_source import RuntimeConfigSource

    real_load = RuntimeConfigSource.load
    placement_fields = {
        "repository_root": site.repo,
        "path_bindings": site.config(placement=True).path_bindings,
        "state_placement": StatePlacementConfig(state_root=site.root),
    }

    def _load(cls: type, **kw: Any) -> RuntimeConfig:
        config = real_load(**kw)
        update: dict[str, Any] = dict(placement_fields) if placement else {}
        if record_path is not None:
            update["audit_cutover_record_path"] = str(record_path)
        return config.model_copy(update=update)

    monkeypatch.setattr(RuntimeConfigSource, "load", classmethod(_load))


def test_inspect_refuses_a_config_default_record_outside_the_root(
    fx: Any, site: Site, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _greenfield_passing(fx)
    site.stamp(site.config(placement=True))
    _install_inspect_config(monkeypatch, site, fx.record_path)  # outside the root

    exit_code = inspect_cli.main(fx.argv("--signing-key-map", str(fx.key_map_path)))

    captured = capsys.readouterr()
    assert exit_code == 2
    assert f"RT-FAIL-STATE-ROOT-PLACEMENT:{_OUTSIDE}" in captured.err
    assert "UNVERIFIED" not in captured.out  # never downgraded to the absent-record report


def test_inspect_accepts_a_config_default_record_inside_the_root(
    fx: Any, site: Site, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _greenfield_passing(fx)
    site.stamp(site.config(placement=True))
    inside = site.root / "audit-cutover-record.json"
    shutil.copyfile(fx.record_path, inside)
    _install_inspect_config(monkeypatch, site, inside)

    exit_code = inspect_cli.main(fx.argv("--signing-key-map", str(fx.key_map_path)))

    assert exit_code == 0, capsys.readouterr()


def test_an_explicit_cutover_record_override_stays_a_read_only_diagnostic(
    fx: Any, site: Site, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _greenfield_passing(fx)
    site.stamp(site.config(placement=True))
    _install_inspect_config(monkeypatch, site, None)  # config path left as the loader gave it

    exit_code = inspect_cli.main(fx.full_verification_argv())  # --cutover-record outside root

    assert exit_code == 0, capsys.readouterr()


def test_inspect_without_placement_keeps_the_legacy_config_default(
    fx: Any, site: Site, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _greenfield_passing(fx)
    _install_inspect_config(monkeypatch, site, fx.record_path, placement=False)

    exit_code = inspect_cli.main(fx.argv("--signing-key-map", str(fx.key_map_path)))

    assert exit_code == 0, capsys.readouterr()
