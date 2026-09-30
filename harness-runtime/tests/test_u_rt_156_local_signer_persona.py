"""C-RT-03 v1.133: local audit private keys are a solo/team backend only.

A future MTC deployment may use delegated KMS, but it cannot load a local
private signer as its signing backend. The refusal must precede backend I/O.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from harness_core import PersonaTier
from harness_runtime.types import AuditSigningConfig, RuntimeConfig

from .test_u_rt_134_audit_signing_fail_closed import _config, _mtc_ready_kwargs


def _local_config(tmp_path: Path, *, persona_tier: PersonaTier, mtc_ready: bool) -> RuntimeConfig:
    kwargs = _mtc_ready_kwargs(tmp_path) if mtc_ready else {"persona_tier": persona_tier}
    kwargs["persona_tier"] = persona_tier
    base = _config(tmp_path, **kwargs)
    return base.model_copy(
        update={
            "audit_signing": AuditSigningConfig(
                backend="local-ed25519",
                local_key_paths={"cutover-key": str(tmp_path / "cutover.pem")},
            )
        }
    )


def test_mtc_local_backend_is_invalid_value_even_when_required_inputs_are_missing(
    tmp_path: Path,
) -> None:
    from harness_runtime.lifecycle.audit_signing_fail_closed_validation import (
        AuditSigningConfigInvalidError,
        validate_mtc_audit_signing_config,
    )

    config = _local_config(
        tmp_path, persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE, mtc_ready=False
    )
    with pytest.raises(AuditSigningConfigInvalidError) as caught:
        validate_mtc_audit_signing_config(config)
    assert "RT-FAIL-CONFIG" in str(caught.value)
    assert "persona_tier" in str(caught.value)
    assert "local-ed25519" in str(caught.value)


@pytest.mark.parametrize("persona", [PersonaTier.SOLO_DEVELOPER, PersonaTier.TEAM_BINDING])
def test_lower_tier_local_backend_keeps_existing_config_admission(
    tmp_path: Path, persona: PersonaTier
) -> None:
    from harness_runtime.lifecycle.audit_signing_fail_closed_validation import (
        validate_mtc_audit_signing_config,
    )

    validate_mtc_audit_signing_config(
        _local_config(tmp_path, persona_tier=persona, mtc_ready=False)
    )


@pytest.mark.asyncio
async def test_stage4_rejects_mtc_local_before_backend_construction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from cryptography.fernet import Fernet
    from harness_core.workload_class import WorkloadClass
    from harness_runtime.bootstrap import stage_4_od
    from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
    from harness_runtime.lifecycle.audit_signing_fail_closed_validation import (
        AuditSigningConfigInvalidError,
    )

    monkeypatch.setenv("HARNESS_PROTECTED_RESULT_STORE_KEY", Fernet.generate_key().decode())
    config = _local_config(
        tmp_path, persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE, mtc_ready=True
    )
    ctx = _MutableHarnessContext()
    ctx.ledger_writer = object()  # type: ignore[assignment] -- stage-1 presence; no use before refusal
    calls: list[str] = []

    def forbidden_backend(_config: AuditSigningConfig) -> None:
        calls.append("factory")
        raise AssertionError("backend construction must not begin")

    monkeypatch.setattr(stage_4_od, "make_audit_signing_backend", forbidden_backend)
    with pytest.raises(AuditSigningConfigInvalidError, match="local-ed25519"):
        await stage_4_od.execute(ctx, config, WorkloadClass.SOFTWARE_ENGINEERING)
    assert calls == []


def test_record_migration_rejects_mtc_local_before_backend_construction(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from cryptography.fernet import Fernet
    from harness_runtime.admin.migrate_audit_sidecar import main
    from harness_runtime.config import audit_signing
    from harness_runtime.config_source import RuntimeConfigSource

    monkeypatch.setenv("HARNESS_PROTECTED_RESULT_STORE_KEY", Fernet.generate_key().decode())
    config = _local_config(
        tmp_path, persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE, mtc_ready=True
    )
    monkeypatch.setattr(RuntimeConfigSource, "load", lambda **_kw: config)
    calls: list[str] = []

    def forbidden_backend(_config: AuditSigningConfig) -> None:
        calls.append("factory")
        raise AssertionError("backend construction must not begin")

    monkeypatch.setattr(audit_signing, "make_audit_signing_backend", forbidden_backend)
    ledger = tmp_path / "state.jsonl"
    ledger.write_text("")
    assert main([str(ledger), "--author", "--runtime-config", str(tmp_path / "config.toml")]) == 1
    stderr = capsys.readouterr().err
    assert "RT-FAIL-CONFIG" in stderr
    assert "local-ed25519" in stderr
    assert calls == []
    assert not (tmp_path / "record.json").exists()
