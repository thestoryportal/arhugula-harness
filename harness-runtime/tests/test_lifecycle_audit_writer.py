"""U-RT-32 — `materialize_audit_writer_stage` + `RuntimeAuditLedgerWriter` tests.

ACs per Phase 2 Session 7 L6 stage 4 (closes L6 OD observability):

1. Round-trip: `append(tenant_id, audit_entry)` writes an IS entry; IS
   `verify_chain` returns VALID; `read_for_tenant` returns the wrapped
   entry.
2. Cross-tenant separation: entries appended under tenant A are not
   returned by `read_for_tenant("B")`; per-tenant readers are disjoint.
3. Chain integrity preserved across 100 sequential appends: the IS chain
   remains VALID after 100 audit entries.

Plus shape coverage: composer wiring, time-source injection, idempotent
replay, `read_all` cross-tenant aggregation surface, freeze invariants.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from harness_core.deployment_surface import DeploymentSurface
from harness_core.workload_class import WorkloadClass
from harness_cp.topology_pattern import TopologyPattern
from harness_is.chain_verification import VerificationStatus, verify_chain
from harness_is.path_class_registry import PathClass
from harness_is.path_resolver import PathResolver
from harness_is.state_ledger_entry_schema import (
    Actor,
    ActorClass,
    Timestamp,
)
from harness_is.state_ledger_write import WriteResult, read_ledger
from harness_od.audit_ledger_types import (
    AuditLedgerEntry,
    AuditPayload,
    AuditSignatureAttributes,
    SignatureAlgorithm,
    StateLedgerEntryRef,
)
from harness_runtime.config.path_bindings import build_path_binding
from harness_runtime.lifecycle.audit_writer import (
    AuditWriterBindError,
    AuditWriterStage,
    RuntimeAuditLedgerWriter,
    materialize_audit_writer_stage,
)
from harness_runtime.lifecycle.state_ledger import (
    LedgerWriter,
    materialize_state_ledger,
)
from harness_runtime.types import (
    CollectorConfig,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
)

# ---------------------------------------------------------------------------
# Fixtures + helpers.
# ---------------------------------------------------------------------------


def _resolver_for(tmp_path: Path) -> PathResolver:
    config = PathBindingConfig(
        raw_entries=(
            {
                "path_class": PathClass.STATE_LEDGER,
                "workflow_class": WorkloadClass.SOFTWARE_ENGINEERING,
                "deployment_surface": DeploymentSurface.LOCAL_DEVELOPMENT,
                "path": str(tmp_path / "state.jsonl"),
            },
        ),
    )
    return PathResolver(build_path_binding(config))


def _ledger_writer(tmp_path: Path) -> LedgerWriter:
    return materialize_state_ledger(
        _resolver_for(tmp_path),
        workflow_class=WorkloadClass.SOFTWARE_ENGINEERING,
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        actor=Actor(actor_class=ActorClass.AGENT, actor_id="test-runtime"),
    )


def _make_audit_entry(entry_hash: str, prior_hash: str = "0" * 64) -> AuditLedgerEntry:
    """Build a pre-signed `AuditLedgerEntry` for write-side tests.

    The audit chain (`prior_entry_hash` / `entry_hash`) is OD-axis discipline;
    the IS chain wraps each entry independently, so test inputs may use any
    unique `entry_hash` values.
    """
    return AuditLedgerEntry(
        payload=AuditPayload(
            entry_core=StateLedgerEntryRef(f"entry-ref-{entry_hash[:8]}"),
            audit_namespace_attrs={"audit.actor": "test-emission-site"},
            prior_entry_hash=prior_hash,
        ),
        signature_attrs=AuditSignatureAttributes(
            audit_signature_value=f"sig:{entry_hash[:8]}",
            audit_signature_algorithm=SignatureAlgorithm.ED25519,
            audit_signature_key_id="test-key",
            audit_signature_key_period="2026-Q2",
        ),
        entry_hash=entry_hash,
    )


def _ticking_clock(start: datetime) -> Callable[[], Timestamp]:
    """Return a strictly-monotonic time source (microsecond increments)."""
    state: dict[str, datetime] = {"now": start}

    def _tick() -> Timestamp:
        state["now"] = state["now"] + timedelta(microseconds=1)
        return state["now"]

    return _tick


def _writer(tmp_path: Path, start: datetime | None = None) -> RuntimeAuditLedgerWriter:
    ledger = _ledger_writer(tmp_path)
    start = start if start is not None else datetime(2026, 5, 19, 12, 0, 0, tzinfo=UTC)
    stage = materialize_audit_writer_stage(
        _config(tmp_path),
        ledger,
        time_source=_ticking_clock(start),
    )
    return stage.writer


def _config(tmp_path: Path) -> RuntimeConfig:
    """Default-shaped RuntimeConfig mirroring the L6 composer test fixtures."""
    return RuntimeConfig(
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        repository_root=tmp_path,
        path_bindings=PathBindingConfig(),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4317"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
    )


# ---------------------------------------------------------------------------
# Composer + shape.
# ---------------------------------------------------------------------------


def test_composer_returns_stage_with_writer(tmp_path: Path) -> None:
    stage = materialize_audit_writer_stage(_config(tmp_path), _ledger_writer(tmp_path))
    assert isinstance(stage, AuditWriterStage)
    assert isinstance(stage.writer, RuntimeAuditLedgerWriter)


def test_stage_is_frozen(tmp_path: Path) -> None:
    stage = materialize_audit_writer_stage(_config(tmp_path), _ledger_writer(tmp_path))
    with pytest.raises(AttributeError):
        stage.writer = stage.writer  # type: ignore[misc]


def test_writer_is_frozen(tmp_path: Path) -> None:
    writer = _writer(tmp_path)
    with pytest.raises(AttributeError):
        writer.ledger_writer = writer.ledger_writer  # type: ignore[misc]


def test_composer_default_time_source_is_utc_now(tmp_path: Path) -> None:
    """Default `time_source` produces a UTC-aware `datetime.now()` value."""
    stage = materialize_audit_writer_stage(_config(tmp_path), _ledger_writer(tmp_path))
    ts = stage.writer.time_source()
    assert ts.tzinfo is not None
    assert ts.utcoffset() == timedelta(0)


def test_bind_error_typed() -> None:
    """`AuditWriterBindError` is typed and exception-shaped."""
    err = AuditWriterBindError("test")
    assert isinstance(err, Exception)


# ---------------------------------------------------------------------------
# AC #1 — Round-trip: append → IS chain → verify_chain VALID → read returns.
# ---------------------------------------------------------------------------


def test_round_trip_single_entry_passes_chain_verification(tmp_path: Path) -> None:
    writer = _writer(tmp_path)
    entry = _make_audit_entry(entry_hash="a" * 64)

    result = writer.append(tenant_id=None, audit_entry=entry)
    assert result is WriteResult.APPENDED

    is_entries = read_ledger(writer.ledger_writer.handle)
    assert len(is_entries) == 1
    chain = verify_chain(is_entries)
    assert chain.status is VerificationStatus.VALID

    tenant_view = writer.read_for_tenant(None)
    assert len(tenant_view) == 1
    assert tenant_view[0].action_id.endswith(":" + "a" * 64)


def test_round_trip_with_tenant_id_passes_chain_verification(tmp_path: Path) -> None:
    writer = _writer(tmp_path)
    entry = _make_audit_entry(entry_hash="b" * 64)

    result = writer.append(tenant_id="tenant-x", audit_entry=entry)
    assert result is WriteResult.APPENDED

    is_entries = read_ledger(writer.ledger_writer.handle)
    chain = verify_chain(is_entries)
    assert chain.status is VerificationStatus.VALID

    tenant_view = writer.read_for_tenant("tenant-x")
    assert len(tenant_view) == 1
    assert "tenant-x" in tenant_view[0].action_id


# ---------------------------------------------------------------------------
# AC #2 — Cross-tenant separation: tenant A's chain unreachable from B.
# ---------------------------------------------------------------------------


def test_cross_tenant_read_returns_only_own_entries(tmp_path: Path) -> None:
    writer = _writer(tmp_path)

    writer.append("tenant-a", _make_audit_entry(entry_hash="1" * 64))
    writer.append("tenant-a", _make_audit_entry(entry_hash="2" * 64))
    writer.append("tenant-b", _make_audit_entry(entry_hash="3" * 64))

    a_view = writer.read_for_tenant("tenant-a")
    b_view = writer.read_for_tenant("tenant-b")

    assert len(a_view) == 2
    assert len(b_view) == 1
    assert all("tenant-a" in e.action_id for e in a_view)
    assert all("tenant-b" in e.action_id for e in b_view)
    assert not any("tenant-b" in e.action_id for e in a_view)
    assert not any("tenant-a" in e.action_id for e in b_view)


def test_unknown_tenant_read_returns_empty(tmp_path: Path) -> None:
    writer = _writer(tmp_path)
    writer.append("tenant-a", _make_audit_entry(entry_hash="4" * 64))

    assert writer.read_for_tenant("tenant-nonexistent") == []


def test_single_tenant_disjoint_from_named_tenants(tmp_path: Path) -> None:
    """`None` tenant is the `_single` tag — disjoint from named tenant scopes."""
    writer = _writer(tmp_path)

    writer.append(None, _make_audit_entry(entry_hash="5" * 64))
    writer.append("tenant-a", _make_audit_entry(entry_hash="6" * 64))

    single = writer.read_for_tenant(None)
    named = writer.read_for_tenant("tenant-a")

    assert len(single) == 1
    assert len(named) == 1
    assert single[0].action_id != named[0].action_id


def test_read_all_aggregates_across_tenants(tmp_path: Path) -> None:
    writer = _writer(tmp_path)
    writer.append("tenant-a", _make_audit_entry(entry_hash="7" * 64))
    writer.append("tenant-b", _make_audit_entry(entry_hash="8" * 64))
    writer.append(None, _make_audit_entry(entry_hash="9" * 64))

    all_entries = writer.read_all()
    assert len(all_entries) == 3


# ---------------------------------------------------------------------------
# AC #3 — Chain integrity preserved across 100 sequential appends.
# ---------------------------------------------------------------------------


def test_chain_integrity_across_100_sequential_appends(tmp_path: Path) -> None:
    writer = _writer(tmp_path)

    for i in range(100):
        entry_hash = f"{i:064x}"
        result = writer.append(
            tenant_id=f"tenant-{i % 3}",
            audit_entry=_make_audit_entry(entry_hash=entry_hash),
        )
        assert result is WriteResult.APPENDED, f"append {i} did not return APPENDED"

    is_entries = read_ledger(writer.ledger_writer.handle)
    assert len(is_entries) == 100
    chain = verify_chain(is_entries)
    assert chain.status is VerificationStatus.VALID


def test_chain_integrity_under_round_robin_tenants(tmp_path: Path) -> None:
    """Three tenants interleaved across 30 appends; each tenant's reader sees 10."""
    writer = _writer(tmp_path)

    for i in range(30):
        writer.append(
            tenant_id=f"tenant-{i % 3}",
            audit_entry=_make_audit_entry(entry_hash=f"{i:064x}"),
        )

    for t in range(3):
        assert len(writer.read_for_tenant(f"tenant-{t}")) == 10

    chain = verify_chain(read_ledger(writer.ledger_writer.handle))
    assert chain.status is VerificationStatus.VALID


# ---------------------------------------------------------------------------
# Idempotency — replay of the same audit entry under the same tenant is noop.
# ---------------------------------------------------------------------------


def test_replay_same_entry_same_tenant_is_idempotent_noop(tmp_path: Path) -> None:
    writer = _writer(tmp_path)
    entry = _make_audit_entry(entry_hash="d" * 64)

    first = writer.append("tenant-a", entry)
    second = writer.append("tenant-a", entry)

    assert first is WriteResult.APPENDED
    assert second is WriteResult.IDEMPOTENT_NOOP
    assert len(writer.read_for_tenant("tenant-a")) == 1


def test_same_entry_different_tenants_both_append(tmp_path: Path) -> None:
    """Tenant-scoped idempotency: A and B may both reference the same OD entry."""
    writer = _writer(tmp_path)
    entry = _make_audit_entry(entry_hash="e" * 64)

    a_result = writer.append("tenant-a", entry)
    b_result = writer.append("tenant-b", entry)

    assert a_result is WriteResult.APPENDED
    assert b_result is WriteResult.APPENDED
    assert len(writer.read_for_tenant("tenant-a")) == 1
    assert len(writer.read_for_tenant("tenant-b")) == 1


# ---------------------------------------------------------------------------
# Time-source injection — composer accepts a callable; default is now(UTC).
# ---------------------------------------------------------------------------


def test_time_source_injection_drives_entry_timestamps(tmp_path: Path) -> None:
    fixed = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)
    writer = _writer(tmp_path, start=fixed)

    writer.append("tenant-a", _make_audit_entry(entry_hash="f" * 64))

    [is_entry] = read_ledger(writer.ledger_writer.handle)
    # Ticking clock advances by 1 microsecond per call.
    assert is_entry.timestamp == fixed + timedelta(microseconds=1)


# --- B-47 item (e) — full-entry durable sidecar -----------------------------


def test_append_persists_full_entry_to_sidecar_and_rehydrates() -> None:
    """Item (e) round-trip — the full signed entry (payload + signature_attrs
    + entry_hash) survives durable persistence and rehydrates byte-equal via
    `read_full_entries_for_tenant`; before the sidecar, only the
    `audit:<tag>:<entry_hash>` reference survived and a real signature was
    produced then dropped (codex round-3 P1 on PR #1033, verified)."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        writer = _writer(Path(tmp))
        entry = _make_audit_entry("a" * 64)
        assert writer.append("tenant-A", entry) is WriteResult.APPENDED

        [rehydrated] = writer.read_full_entries_for_tenant("tenant-A")
        assert rehydrated == entry
        assert rehydrated.signature_attrs.audit_signature_value == "sig:aaaaaaaa"


def test_idempotent_replay_writes_no_duplicate_sidecar_line() -> None:
    """Item (e) dedup — the IS chain is the single dedup authority: a replay
    returning IDEMPOTENT_NOOP writes no second sidecar line."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        writer = _writer(Path(tmp))
        entry = _make_audit_entry("b" * 64)
        assert writer.append("tenant-A", entry) is WriteResult.APPENDED
        assert writer.append("tenant-A", entry) is WriteResult.IDEMPOTENT_NOOP

        assert len(writer.read_full_entries_for_tenant("tenant-A")) == 1


def test_sidecar_reader_is_tenant_scoped_and_empty_when_absent() -> None:
    """Item (e) separation — the full-entry reader honors the same C-OD-21
    §21.1 cross-tenant separation as the ref reader, and returns `[]` (not an
    error) before any entry was ever appended."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        writer = _writer(Path(tmp))
        assert writer.read_full_entries_for_tenant("tenant-A") == []

        writer.append("tenant-A", _make_audit_entry("c" * 64))
        writer.append("tenant-B", _make_audit_entry("d" * 64))

        [entry_a] = writer.read_full_entries_for_tenant("tenant-A")
        [entry_b] = writer.read_full_entries_for_tenant("tenant-B")
        assert entry_a.entry_hash == "c" * 64
        assert entry_b.entry_hash == "d" * 64


# --- B-47 PR B — full composition-root chain witness -------------------------


def test_full_chain_stage_to_real_signature_to_sidecar_rehydration(tmp_path: Path) -> None:
    """THE end-to-end composition-root witness (B-47 PR B; one witness through
    the real path, not seam halves): `materialize_span_processor_stage` at
    MULTI_TENANT_COMPLIANCE with a composition-root-constructed `SigningBackend`
    → a real span's PII attribute tokenizes → the redaction-token audit entry
    is signed by REAL cryptography (not the placeholder) → the runtime audit
    writer persists it → the item-(e) sidecar rehydrates the full entry with
    the signature intact and it verifies against the canonical message."""
    import base64

    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from harness_od.multi_tenant_trace_separation_and_audit_ledger import (
        _canonical_od_signing_message,
    )
    from harness_runtime.lifecycle.span_processor import materialize_span_processor_stage
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    class _Ed25519Backend:
        algorithm = "ed25519"

        def __init__(self) -> None:
            self._private_key = Ed25519PrivateKey.generate()
            self.public_key = self._private_key.public_key()

        def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
            del key_id, key_period
            return self._private_key.sign(message)

        def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
            del message, signature, key_id, key_period
            return True

    writer = _writer(tmp_path)
    backend = _Ed25519Backend()
    base = _config(tmp_path)
    config = base.model_copy(
        update={
            "persona_tier": base.persona_tier.__class__.MULTI_TENANT_COMPLIANCE,
            "tenant_id": "tenant-b47",
        }
    )

    provider = TracerProvider()
    stage = materialize_span_processor_stage(
        config,
        provider,
        exporter=InMemorySpanExporter(),
        audit_writer=writer,
        signing_backend=backend,
    )
    assert stage.redaction_processor.tokenizer_enabled is True

    tracer = provider.get_tracer("b47-composition-root-witness")
    with tracer.start_as_current_span("anthropic.messages.create") as span:
        span.set_attribute("gen_ai.input.messages", "customer ssn 123-45-6789")
    stage.flush(timeout_millis=5000)

    [entry] = writer.read_full_entries_for_tenant("tenant-b47")
    value = entry.signature_attrs.audit_signature_value
    assert not value.startswith("unsigned:")
    raw = base64.b64decode(value, validate=True)
    assert len(raw) == 64

    expected_message = _canonical_od_signing_message(
        entry.entry_hash,
        key_id="harness-runtime-redaction-token",
        algo_value="ed25519",
        key_period_token="DEPLOYMENT_BOUND",
    )
    backend.public_key.verify(raw, expected_message)  # raises on mismatch
