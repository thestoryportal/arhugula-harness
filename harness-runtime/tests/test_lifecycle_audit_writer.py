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

import json
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

    `entry_hash` is a SEED that disambiguates entries (folded into the
    payload as `audit.seed`); the stored
    `entry_hash` is the GENUINE `compute_entry_hash(payload)` — the B-47
    item-(e) sidecar fold recomputes content integrity (codex round-17), so
    fabricated hashes would fail every fold, exactly as a tampered
    production row should.
    """
    from harness_od.audit_ledger_types import compute_entry_hash

    payload = AuditPayload(
        entry_core=StateLedgerEntryRef(f"entry-ref-{entry_hash[:8]}"),
        audit_namespace_attrs={"audit.actor": "test-emission-site", "audit.seed": entry_hash},
        prior_entry_hash=prior_hash,
    )
    return AuditLedgerEntry(
        payload=payload,
        signature_attrs=AuditSignatureAttributes(
            audit_signature_value=f"sig:{entry_hash[:8]}",
            audit_signature_algorithm=SignatureAlgorithm.ED25519,
            audit_signature_key_id="test-key",
            audit_signature_key_period="2026-Q2",
        ),
        entry_hash=compute_entry_hash(payload),
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
    assert tenant_view[0].action_id.endswith(":" + entry.entry_hash)


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
        assert entry_a.payload.audit_namespace_attrs["audit.seed"] == "c" * 64
        assert entry_b.payload.audit_namespace_attrs["audit.seed"] == "d" * 64


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


def test_crash_between_sidecar_write_and_is_append_heals_on_retry(tmp_path: Path) -> None:
    """Codex P1 chain (PR B1, rounds 1+3) — two-run crash-resume witness for
    the SIDECAR-FIRST ordering: the first append lands the sidecar row but
    dies before the IS append (simulated by a raising ledger writer); the
    signed entry is already durable. The caller's retry gets APPENDED (the IS
    chain never committed) and the membership check writes no duplicate row —
    one row, one chain ref, fully consistent."""
    import unittest.mock as mock

    writer = _writer(tmp_path)
    entry = _make_audit_entry("f" * 64)

    original_is_append = type(writer.ledger_writer).append
    calls = {"n": 0}

    def _dies_once(self: object, payload: object, write_key: object) -> object:
        calls["n"] += 1
        if calls["n"] == 1:
            raise OSError("simulated crash after sidecar write, before IS append")
        return original_is_append(self, payload, write_key)  # type: ignore[arg-type]

    with mock.patch.object(type(writer.ledger_writer), "append", _dies_once):
        with pytest.raises(OSError, match="simulated crash"):
            writer.append("tenant-A", entry)

        # The signed entry is ALREADY durable (sidecar-first) — nothing lost.
        [durable] = writer.read_full_entries_for_tenant("tenant-A")
        assert durable == entry

        # Retry: IS append commits (APPENDED — it never landed the first
        # time); the membership check writes no duplicate sidecar row.
        assert writer.append("tenant-A", entry) is WriteResult.APPENDED

    assert len(writer.read_full_entries_for_tenant("tenant-A")) == 1
    # A later replay is a NOOP and still writes nothing.
    assert writer.append("tenant-A", entry) is WriteResult.IDEMPOTENT_NOOP
    assert len(writer.read_full_entries_for_tenant("tenant-A")) == 1


def test_unreplayed_orphan_row_keeps_chain_continuity(tmp_path: Path) -> None:
    """Codex round-3 scenario (PR B1) — an entry whose sidecar row landed but
    whose IS append never did, and which is NEVER replayed (span-redaction
    side effects do not replay): the next NEW event must seed its chain from
    the durable tail (the orphan), keeping the rehydrated per-tenant sequence
    verifying — the IS-first ordering forked the chain here."""
    import unittest.mock as mock

    from harness_core import PersonaTier
    from harness_od.audit_ledger_types import AuditLedger
    from harness_od.multi_tenant_trace_separation_and_audit_ledger import (
        verify_hash_chain_integrity,
    )
    from harness_od.observability_matrix import CellID
    from harness_od.redaction_tokenizer import RedactionTokenRecord
    from harness_runtime.lifecycle.redaction_token_audit_map import (
        AuditLedgerRedactionTokenMap,
    )

    writer = _writer(tmp_path)

    def _record(token: str) -> RedactionTokenRecord:
        return RedactionTokenRecord(
            token=token,
            raw_value=f"raw for {token}",
            semantic_category="PII",
            attribute_key="gen_ai.input.messages",
            trace_id="trace-1",
            span_id=f"span-{token}",
        )

    token_map = AuditLedgerRedactionTokenMap(
        audit_writer=writer,
        tenant_id="tenant-orphan",
        signing_key_id="chain-key",
    )
    token_map.append(_record("[REDACTED:PII:1]"))

    # Entry 2's sidecar row lands; its IS append dies; it is NEVER replayed.
    with mock.patch.object(
        type(writer.ledger_writer),
        "append",
        side_effect=OSError("simulated crash before IS append"),
    ):
        with pytest.raises(OSError):
            token_map.append(_record("[REDACTED:PII:2]"))

    # A FRESH map (restart) appends a brand-new event — no replay of entry 2.
    fresh_map = AuditLedgerRedactionTokenMap(
        audit_writer=writer,
        tenant_id="tenant-orphan",
        signing_key_id="chain-key",
    )
    fresh_map.append(_record("[REDACTED:PII:3]"))

    entries = writer.read_full_entries_for_tenant("tenant-orphan")
    assert len(entries) == 3  # incl. the orphan — durable, never lost
    cell_7 = CellID(
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        deployment_surface=DeploymentSurface.SELF_HOSTED_SERVER,
    )
    verify_hash_chain_integrity(
        AuditLedger(entries=tuple(entries), cell_id=cell_7)
    )  # raises on breach — the orphan does NOT fork the chain


def test_token_map_chain_advances_and_reseeds_across_restart(tmp_path: Path) -> None:
    """Codex round-2 finding (PR B1) — the token map reused its genesis
    `prior_entry_hash` verbatim on every append, so a rehydrated per-tenant
    sequence failed `verify_hash_chain_integrity` from entry 2 — the sidecar
    reader could not serve the verifier it exists for. The chain now advances
    per append and RESEEDS from the durable tail on restart: a second map
    instance (same writer) continues the chain, and the full rehydrated
    sequence verifies."""
    from harness_core import PersonaTier
    from harness_od.audit_ledger_types import AuditLedger
    from harness_od.multi_tenant_trace_separation_and_audit_ledger import (
        verify_hash_chain_integrity,
    )
    from harness_od.observability_matrix import CellID
    from harness_od.redaction_tokenizer import RedactionTokenRecord
    from harness_runtime.lifecycle.redaction_token_audit_map import (
        AuditLedgerRedactionTokenMap,
    )

    writer = _writer(tmp_path)

    def _record(token: str) -> RedactionTokenRecord:
        return RedactionTokenRecord(
            token=token,
            raw_value=f"raw for {token}",
            semantic_category="PII",
            attribute_key="gen_ai.input.messages",
            trace_id="trace-1",
            span_id=f"span-{token}",
        )

    map_run_1 = AuditLedgerRedactionTokenMap(
        audit_writer=writer,
        tenant_id="tenant-chain",
        signing_key_id="chain-key",
    )
    map_run_1.append(_record("[REDACTED:PII:1]"))
    map_run_1.append(_record("[REDACTED:PII:2]"))

    # Simulated restart: a FRESH map instance over the same durable writer.
    map_run_2 = AuditLedgerRedactionTokenMap(
        audit_writer=writer,
        tenant_id="tenant-chain",
        signing_key_id="chain-key",
    )
    map_run_2.append(_record("[REDACTED:PII:3]"))

    entries = writer.read_full_entries_for_tenant("tenant-chain")
    assert len(entries) == 3
    assert entries[1].payload.prior_entry_hash == entries[0].entry_hash
    assert entries[2].payload.prior_entry_hash == entries[1].entry_hash
    cell_7 = CellID(
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        deployment_surface=DeploymentSurface.SELF_HOSTED_SERVER,
    )
    verify_hash_chain_integrity(
        AuditLedger(entries=tuple(entries), cell_id=cell_7)
    )  # raises on breach


def test_torn_sidecar_tail_is_skipped_on_read_and_healed_on_write(tmp_path: Path) -> None:
    """Codex round-2 P2 + round-40 (PR B1) — a crash mid-write leaves an
    unterminated JSON fragment at the sidecar tail. A read while the torn
    entry's IS ref survives now fails LOUD (round-40: that is a partial
    history, not a skippable artifact); the next write-path call truncates
    the fragment under the lock and the NOOP repair re-lands the lost entry
    whole, after which reads succeed complete."""
    writer = _writer(tmp_path)
    first = _make_audit_entry("1" * 64)
    lost = _make_audit_entry("2" * 64)
    assert writer.append("tenant-A", first) is WriteResult.APPENDED
    assert writer.append("tenant-A", lost) is WriteResult.APPENDED

    # Simulate the crash: the LAST record was only partially flushed.
    raw = writer._sidecar_path.read_bytes()
    lines = raw.splitlines(keepends=True)
    torn = lines[-1][: len(lines[-1]) // 2].rstrip(b"\n")
    writer._sidecar_path.write_bytes(b"".join(lines[:-1]) + torn)

    # (a) Reading a partial history (torn row whose IS ref survives) fails
    # loud — a verifier must never silently see fewer entries than the
    # chain references (round-40).
    with pytest.raises(ValueError, match="truncated or lost"):
        writer.read_full_entries_for_tenant("tenant-A")

    # (b) The NOOP replay of the lost entry truncates the fragment and
    # re-lands the record whole.
    assert writer.append("tenant-A", lost) is WriteResult.IDEMPOTENT_NOOP
    entries = writer.read_full_entries_for_tenant("tenant-A")
    assert [e.entry_hash for e in entries] == [first.entry_hash, lost.entry_hash]

    # (c) The healed file is fully well-formed — every line parses.
    for line in writer._sidecar_path.read_text().splitlines():
        json.loads(line)


def test_concurrent_in_process_appends_never_duplicate_rows(tmp_path: Path) -> None:
    """Codex round-4 P2 (PR B1) — the B-40 cross-process lock degrades to a
    no-op on Windows and its contract expects callers to hold their own
    threading.Lock. With the cross-process lock forced to a no-op, two
    threads racing the SAME entries through append must still produce exactly
    one sidecar row per entry (membership scan + append serialize on the
    writer's in-process lock)."""
    import contextlib
    import threading
    import unittest.mock as mock

    from harness_runtime.lifecycle import audit_writer as audit_writer_module

    writer = _writer(tmp_path)
    entries = [_make_audit_entry(f"{i:02d}" * 32) for i in range(20)]
    barrier = threading.Barrier(2)
    errors: list[BaseException] = []

    @contextlib.contextmanager
    def _noop_lock(path: object):  # type: ignore[no-untyped-def]
        del path
        yield

    def _race() -> None:
        try:
            barrier.wait(timeout=10)
            for entry in entries:
                writer.append("tenant-race", entry)
        except BaseException as exc:  # pragma: no cover - surfaced below
            errors.append(exc)

    with mock.patch.object(audit_writer_module, "cross_process_write_lock", _noop_lock):
        threads = [threading.Thread(target=_race) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)

    assert errors == []
    rows = writer.read_full_entries_for_tenant("tenant-race")
    assert len(rows) == len(entries)
    assert len({e.entry_hash for e in rows}) == len(entries)


def test_membership_index_never_refolds_own_appends(tmp_path: Path) -> None:
    """Codex round-12 P2 (PR B1) — membership checking must not re-parse the
    whole growing sidecar on every append (O(N²) on the span-finalization hot
    path). Own-process appends advance the index directly: across N appends
    through one writer, the index refresh folds ZERO delta bytes (each byte
    of the sidecar is parsed at most once per process; own bytes never)."""
    import unittest.mock as mock

    writer = _writer(tmp_path)
    folded_deltas: list[int] = []
    original = RuntimeAuditLedgerWriter._refresh_sidecar_index_locked

    def _spy(self: RuntimeAuditLedgerWriter) -> None:
        before = self._sidecar_index.offset
        original(self)
        folded_deltas.append(self._sidecar_index.offset - before)

    with mock.patch.object(RuntimeAuditLedgerWriter, "_refresh_sidecar_index_locked", _spy):
        for i in range(10):
            writer.append("tenant-idx", _make_audit_entry(f"{i:02d}" * 32))

    assert folded_deltas == [0] * 10
    assert len(writer.read_full_entries_for_tenant("tenant-idx")) == 10


def test_membership_index_folds_foreign_appends_exactly_once(tmp_path: Path) -> None:
    """Cross-process reconciliation — bytes another process appended are
    folded ONCE (the delta scan), then never again; membership over them
    still deduplicates correctly (no duplicate row on replay)."""
    import unittest.mock as mock

    writer_a = _writer(tmp_path)
    foreign_entry = _make_audit_entry("a" * 64)
    own_entry = _make_audit_entry("b" * 64)
    writer_a.append("tenant-x", foreign_entry)
    foreign_bytes = writer_a.sidecar_path.stat().st_size

    # A second writer over the SAME sidecar (fresh index) simulates another
    # process: its first append folds exactly the foreign bytes, once.
    writer_b = RuntimeAuditLedgerWriter(
        ledger_writer=writer_a.ledger_writer,
        time_source=writer_a.time_source,
    )
    folded_deltas: list[int] = []
    original = RuntimeAuditLedgerWriter._refresh_sidecar_index_locked

    def _spy(self: RuntimeAuditLedgerWriter) -> None:
        before = self._sidecar_index.offset
        original(self)
        folded_deltas.append(self._sidecar_index.offset - before)

    with mock.patch.object(RuntimeAuditLedgerWriter, "_refresh_sidecar_index_locked", _spy):
        writer_b.append("tenant-x", own_entry)
        # Replaying the foreign entry dedups via the index — zero refold,
        # no duplicate row.
        writer_b.append("tenant-x", foreign_entry)

    assert folded_deltas == [foreign_bytes, 0]
    assert len(writer_b.read_full_entries_for_tenant("tenant-x")) == 2


def test_same_map_instance_reconciles_chain_after_partial_failure(tmp_path: Path) -> None:
    """Codex round-13 (PR B1) — same-instance continuation after a PARTIAL
    failure (sidecar landed, IS append raised): the live map must reconcile
    against the durable tail before signing the next DISTINCT record, or that
    record links to the pre-orphan predecessor and the rehydrated sequence
    breaks chain verification. (The restart case was already witnessed; this
    is the no-restart case.)"""
    import unittest.mock as mock

    from harness_core import PersonaTier
    from harness_od.audit_ledger_types import AuditLedger
    from harness_od.multi_tenant_trace_separation_and_audit_ledger import (
        verify_hash_chain_integrity,
    )
    from harness_od.observability_matrix import CellID
    from harness_od.redaction_tokenizer import RedactionTokenRecord
    from harness_runtime.lifecycle.redaction_token_audit_map import (
        AuditLedgerRedactionTokenMap,
    )

    writer = _writer(tmp_path)

    def _record(token: str) -> RedactionTokenRecord:
        return RedactionTokenRecord(
            token=token,
            raw_value=f"raw for {token}",
            semantic_category="PII",
            attribute_key="gen_ai.input.messages",
            trace_id="trace-1",
            span_id=f"span-{token}",
        )

    token_map = AuditLedgerRedactionTokenMap(
        audit_writer=writer,
        tenant_id="tenant-partial",
        signing_key_id="chain-key",
    )
    token_map.append(_record("[REDACTED:PII:1]"))

    # Entry 2: sidecar lands, IS append raises — SAME map instance survives.
    original_is_append = type(writer.ledger_writer).append
    calls = {"n": 0}

    def _dies_once(self: object, payload: object, write_key: object) -> object:
        calls["n"] += 1
        if calls["n"] == 1:
            raise OSError("simulated IS-append failure after sidecar write")
        return original_is_append(self, payload, write_key)  # type: ignore[arg-type]

    with mock.patch.object(type(writer.ledger_writer), "append", _dies_once):
        with pytest.raises(OSError):
            token_map.append(_record("[REDACTED:PII:2]"))

        # Processing continues on the SAME instance with a DIFFERENT record.
        token_map.append(_record("[REDACTED:PII:3]"))

    entries = writer.read_full_entries_for_tenant("tenant-partial")
    assert len(entries) == 3  # incl. the durable orphan
    assert entries[2].payload.prior_entry_hash == entries[1].entry_hash
    cell_7 = CellID(
        persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
        deployment_surface=DeploymentSurface.SELF_HOSTED_SERVER,
    )
    verify_hash_chain_integrity(
        AuditLedger(entries=tuple(entries), cell_id=cell_7)
    )  # raises on breach


def test_corrupt_keyed_sidecar_row_fails_appends_loud_not_silent(tmp_path: Path) -> None:
    """Codex round-15 (PR B1) — a newline-terminated row carrying valid
    identity keys but a corrupt entry body must not silently count as
    membership (which would suppress the legitimate signed entry while the
    IS ref still lands). Folding validates the whole entry and fails LOUD —
    matching the reader's corrupt-row posture and preserving the row as
    evidence (auto-repair could destroy tampering traces)."""
    import json as json_module

    import pydantic

    writer = _writer(tmp_path)
    good = _make_audit_entry("1" * 64)
    writer.append("tenant-A", good)

    corrupt_row = json_module.dumps(
        {"tenant_tag": "tenant-A", "entry": {"entry_hash": "2" * 64}},
        separators=(",", ":"),
    )
    with writer.sidecar_path.open("a", encoding="utf-8") as fh:
        fh.write(corrupt_row + "\n")

    fresh_writer = RuntimeAuditLedgerWriter(
        ledger_writer=writer.ledger_writer,
        time_source=writer.time_source,
    )
    with pytest.raises(pydantic.ValidationError):
        fresh_writer.append("tenant-A", _make_audit_entry("3" * 64))


def test_tampered_payload_with_stale_hash_fails_appends_loud(tmp_path: Path) -> None:
    """Codex round-17 (PR B1) — a schema-valid sidecar row whose payload was
    altered with the stale entry_hash left in place must fail the fold's
    content-integrity recompute, not silently enter the membership index
    (where a legitimate replay would NOOP and leave the tampered payload as
    the only full copy)."""
    import json as json_module

    writer = _writer(tmp_path)
    good = _make_audit_entry("1" * 64)
    writer.append("tenant-A", good)

    tampered = good.model_copy(
        update={"payload": good.payload.model_copy(update={"prior_entry_hash": "f" * 64})}
    )  # entry_hash left stale on purpose
    with writer.sidecar_path.open("a", encoding="utf-8") as fh:
        fh.write(
            json_module.dumps(
                {"tenant_tag": "tenant-B", "entry": tampered.model_dump(mode="json")},
                separators=(",", ":"),
            )
            + "\n"
        )

    fresh_writer = RuntimeAuditLedgerWriter(
        ledger_writer=writer.ledger_writer,
        time_source=writer.time_source,
    )
    with pytest.raises(ValueError, match="content-integrity"):
        fresh_writer.append("tenant-A", _make_audit_entry("3" * 64))


def test_signature_mutated_row_fails_replay_loud_not_silent_noop(tmp_path: Path) -> None:
    """Codex round-19 (PR B1) — a durable row whose signature_attrs were
    mutated (payload + entry_hash intact) passed payload-only integrity and
    silently satisfied membership on replay, leaving the corrupted signature
    as the only durable copy. Membership now compares the COMPLETE signed
    entry and fails loud on divergence."""
    import json as json_module

    writer = _writer(tmp_path)
    entry = _make_audit_entry("1" * 64)
    writer.append("tenant-A", entry)

    # Mutate the durable row's signature value only.
    raw_rows = [
        json_module.loads(line)
        for line in writer.sidecar_path.read_text().splitlines()
        if line.strip()
    ]
    raw_rows[0]["entry"]["signature_attrs"]["audit_signature_value"] = "sig:EVIL"
    writer.sidecar_path.write_text(
        "\n".join(json_module.dumps(r, separators=(",", ":")) for r in raw_rows) + "\n"
    )

    fresh_writer = RuntimeAuditLedgerWriter(
        ledger_writer=writer.ledger_writer,
        time_source=writer.time_source,
    )
    with pytest.raises(ValueError, match="diverges from"):
        fresh_writer.append("tenant-A", entry)


def test_same_size_in_place_mutation_detected_by_live_writer(tmp_path: Path) -> None:
    """Codex round-21 (PR B1) — an in-place SAME-SIZE mutation of a durable
    row while this writer stays alive left file size == index offset, so the
    stale in-memory digest silently accepted the replay. File identity
    (inode + mtime_ns) now forces a rescan, and the round-19 divergence
    check fires against the actual bytes."""
    writer = _writer(tmp_path)
    entry = _make_audit_entry("1" * 64)
    writer.append("tenant-A", entry)

    raw = writer.sidecar_path.read_text()
    assert "sig:11111111" in raw
    mutated = raw.replace("sig:11111111", "sig:TAMPERED")  # same byte length
    assert len(mutated) == len(raw)
    writer.sidecar_path.write_text(mutated)

    with pytest.raises(ValueError, match="diverges from"):
        writer.append("tenant-A", entry)


def test_alternating_writers_stay_incremental_never_full_rescan(tmp_path: Path) -> None:
    """Codex round-22 (PR B1) — a foreign append changes size AND mtime;
    clearing the index on any mtime change made alternating same-host
    writers reparse the whole growing file per append (the O(N²) this index
    exists to remove). Growth on the same inode must fold ONLY the suffix:
    a sentinel planted in the index survives every alternation — the index
    is never reset — and membership stays correct."""
    writer_a = _writer(tmp_path)
    writer_b = RuntimeAuditLedgerWriter(
        ledger_writer=writer_a.ledger_writer,
        time_source=writer_a.time_source,
    )

    sentinel = ("__witness__", "never-a-real-entry")
    for i in range(3):
        writer_a.append("tenant-alt", _make_audit_entry(f"a{i}" * 32))
        if i > 0:
            # Planted AFTER writer_b's first append built its index; a full
            # rescan (digests.clear) would evict it.
            writer_b._sidecar_index.digests[sentinel] = "sentinel"
        writer_b.append("tenant-alt", _make_audit_entry(f"b{i}" * 32))
        if i > 0:
            assert sentinel in writer_b._sidecar_index.digests, (
                f"index was fully rescanned on alternation {i} — foreign "
                f"growth on the same inode must fold only the suffix"
            )

    assert len(writer_b.read_full_entries_for_tenant("tenant-alt")) == 6


def test_sidecar_fsynced_before_is_reference_lands(tmp_path: Path) -> None:
    """Codex round-23 (PR B1) — write+close reaches only the page cache; the
    sidecar row must be fsync'd BEFORE the IS reference is appended, or power
    loss could keep the ref while the signature row was never durable."""
    import os as os_module
    import stat as stat_module
    import unittest.mock as mock

    writer = _writer(tmp_path)
    events: list[str] = []
    real_fsync = os_module.fsync

    def _spy_fsync(fd: int) -> None:
        st = os_module.fstat(fd)
        # Distinguish the sidecar FILE fsync from the creation-time parent
        # DIRECTORY fsync — a dropped file-fsync must not be masked by the
        # dir-fsync satisfying a naive "some fsync happened" check.
        events.append("fsync_dir" if stat_module.S_ISDIR(st.st_mode) else "fsync_file")
        real_fsync(fd)

    original_is_append = type(writer.ledger_writer).append

    def _spy_is_append(self: object, payload: object, write_key: object) -> object:
        events.append("is_append")
        return original_is_append(self, payload, write_key)  # type: ignore[arg-type]

    with (
        mock.patch("harness_runtime.lifecycle.audit_writer.os.fsync", _spy_fsync),
        mock.patch.object(type(writer.ledger_writer), "append", _spy_is_append),
    ):
        writer.append("tenant-A", _make_audit_entry("1" * 64))
        writer.append("tenant-A", _make_audit_entry("2" * 64))

    # Every IS append is preceded by a sidecar FILE fsync in its own append
    # cycle (the second append has no dir-fsync to hide behind).
    is_append_positions = [i for i, e in enumerate(events) if e == "is_append"]
    assert len(is_append_positions) == 2
    prev = -1
    for pos in is_append_positions:
        assert "fsync_file" in events[prev + 1 : pos], events
        prev = pos


def test_writer_instances_over_one_sidecar_share_the_in_process_lock(tmp_path: Path) -> None:
    """Codex round-25 (PR B1) — a per-INSTANCE fallback lock left two writer
    instances over one sidecar unserialized where the cross-process lock is
    a no-op (Windows). The in-process lock is keyed on the resolved sidecar
    path: same path ⇒ the SAME lock object; different path ⇒ different."""
    writer_a = _writer(tmp_path)
    writer_b = RuntimeAuditLedgerWriter(
        ledger_writer=writer_a.ledger_writer,
        time_source=writer_a.time_source,
    )
    assert writer_a._sidecar_thread_lock is writer_b._sidecar_thread_lock

    import tempfile

    with tempfile.TemporaryDirectory() as other:
        writer_c = _writer(Path(other))
        assert writer_c._sidecar_thread_lock is not writer_a._sidecar_thread_lock


def test_reader_holds_the_shared_in_process_lock(tmp_path: Path) -> None:
    """Codex round-26 (PR B1) — on Windows the cross-process read lock is a
    no-op, so the reader must hold the same per-path thread lock the writers
    use or a same-process verifier can race a writer thread. Witness: a read
    attempted while the lock is held blocks until release."""
    import threading

    writer = _writer(tmp_path)
    writer.append("tenant-A", _make_audit_entry("1" * 64))

    results: list[int] = []
    started = threading.Event()

    def _read() -> None:
        started.set()
        results.append(len(writer.read_full_entries_for_tenant("tenant-A")))

    lock = writer._sidecar_thread_lock
    lock.acquire()
    try:
        t = threading.Thread(target=_read)
        t.start()
        started.wait(timeout=5)
        t.join(timeout=0.3)
        assert t.is_alive(), "reader did not block on the shared in-process lock"
    finally:
        lock.release()
    t.join(timeout=5)
    assert results == [1]


def test_inconsistent_entry_hash_rejected_before_any_write(tmp_path: Path) -> None:
    """Codex round-27 (PR B1) — a schema-valid entry whose stored entry_hash
    does not match its payload persisted fine, then wedged every
    post-restart append at the fold's integrity check. Rejected up front:
    nothing (sidecar row or IS ref) is written."""
    writer = _writer(tmp_path)
    good = _make_audit_entry("1" * 64)
    bad = good.model_copy(update={"entry_hash": "f" * 64})

    with pytest.raises(ValueError, match="before write"):
        writer.append("tenant-A", bad)

    assert not writer.sidecar_path.exists()
    assert writer.read_for_tenant("tenant-A") == []


def test_membership_hit_retry_refsyncs_before_is_reference(tmp_path: Path) -> None:
    """Codex round-28 (PR B1) — if the initial fsync raised after the row was
    written, the retry hits the membership path; it must re-fsync the file
    before the IS reference commits, or power loss keeps the ref while the
    row was only page-cached."""
    import os as os_module
    import stat as stat_module
    import unittest.mock as mock

    writer = _writer(tmp_path)
    entry = _make_audit_entry("1" * 64)
    real_fsync = os_module.fsync
    state = {"raised": False}
    events: list[str] = []

    def _fsync_dies_once(fd: int) -> None:
        st = os_module.fstat(fd)
        kind = "fsync_dir" if stat_module.S_ISDIR(st.st_mode) else "fsync_file"
        if kind == "fsync_file" and not state["raised"]:
            state["raised"] = True
            raise OSError("simulated fsync failure after row write")
        events.append(kind)
        real_fsync(fd)

    original_is_append = type(writer.ledger_writer).append

    def _spy_is_append(self: object, payload: object, write_key: object) -> object:
        events.append("is_append")
        return original_is_append(self, payload, write_key)  # type: ignore[arg-type]

    with (
        mock.patch("harness_runtime.lifecycle.audit_writer.os.fsync", _fsync_dies_once),
        mock.patch.object(type(writer.ledger_writer), "append", _spy_is_append),
    ):
        with pytest.raises(OSError, match="simulated fsync failure"):
            writer.append("tenant-A", entry)
        events.clear()
        # Retry: membership hit — must re-fsync the FILE before is_append.
        assert writer.append("tenant-A", entry) is WriteResult.APPENDED

    assert "is_append" in events
    assert "fsync_file" in events[: events.index("is_append")], events


def test_symlinked_sidecar_target_refused(tmp_path: Path) -> None:
    """Codex round-31 P1 (PR B1) — on a shared state directory another
    account can pre-create a symlink where the sidecar will land; a plain
    open would follow it and append raw PII to an attacker-chosen target.
    O_NOFOLLOW makes the append fail loud."""
    import os as os_module

    writer = _writer(tmp_path)
    lure = tmp_path / "attacker-target.jsonl"
    lure.write_text("")
    os_module.symlink(lure, writer.sidecar_path)

    with pytest.raises(OSError):
        writer.append("tenant-A", _make_audit_entry("1" * 64))


def test_permissive_preexisting_sidecar_refused(tmp_path: Path) -> None:
    """Codex round-31 P1 (PR B1) — O_CREAT does not change an existing file's
    mode: a pre-created group/other-readable sidecar would silently receive
    raw values. Verified via fstat and refused loud with an explicit remedy."""
    writer = _writer(tmp_path)
    writer.sidecar_path.touch(mode=0o644)

    with pytest.raises(ValueError, match="group/other-accessible"):
        writer.append("tenant-A", _make_audit_entry("1" * 64))

    # Operator remedy works: tighten the mode and the append proceeds.
    writer.sidecar_path.chmod(0o600)
    assert writer.append("tenant-A", _make_audit_entry("1" * 64)) is WriteResult.APPENDED


def test_heal_never_truncates_through_a_symlink(tmp_path: Path) -> None:
    """Codex round-32 P1 (PR B1) — the path-based heal followed a pre-created
    symlink and os.truncate'd an ATTACKER-CHOSEN writable target (any file
    without a trailing newline) before append-time validation ran. Heal now
    goes through the O_NOFOLLOW-validated descriptor: the append fails loud
    and the lure file is byte-untouched."""
    import os as os_module

    writer = _writer(tmp_path)
    lure = tmp_path / "victim-file"
    lure.write_bytes(b"precious bytes with no trailing newline")
    os_module.symlink(lure, writer.sidecar_path)

    with pytest.raises(OSError):
        writer.append("tenant-A", _make_audit_entry("1" * 64))

    assert lure.read_bytes() == b"precious bytes with no trailing newline"


def test_fifo_sidecar_rejected_on_read_without_hanging(tmp_path: Path) -> None:
    """Codex round-33 P1 (PR B1) — the token map's SEEDING read runs before
    its first append: a pre-created FIFO at the sidecar path made a plain
    open block forever (hanging span completion), and a symlink supplied
    attacker rows. The read path now opens O_NONBLOCK through the validated
    helper: a FIFO returns immediately and is rejected as not-a-regular-file."""
    import os as os_module

    writer = _writer(tmp_path)
    os_module.mkfifo(writer.sidecar_path)

    with pytest.raises(ValueError, match="not a regular file"):
        writer.read_full_entries_for_tenant("tenant-A")


def test_reader_snapshots_is_refs_before_sidecar(tmp_path: Path) -> None:
    """Codex round-44 (PR B1) — scanning the IS refs AFTER releasing the
    sidecar lock let a concurrent append land row+ref between the two reads
    and falsely report history loss. The refs snapshot must happen FIRST
    (sidecar-first writes make that order race-free): a row+ref appended
    right after the refs snapshot must NOT trip the coverage check."""
    import unittest.mock as mock

    writer = _writer(tmp_path)
    writer.append("tenant-A", _make_audit_entry("1" * 64))

    concurrent = _make_audit_entry("2" * 64)
    original_read_for_tenant = RuntimeAuditLedgerWriter.read_for_tenant
    state = {"calls": 0}

    def _concurrent_append_before_second_scan(
        self: RuntimeAuditLedgerWriter, tenant_id: str | None
    ) -> object:
        state["calls"] += 1
        if state["calls"] >= 2:
            # A ref-scan AFTER the sidecar read (the buggy order) sees this
            # just-landed ref whose row the stale sidecar snapshot missed.
            other = RuntimeAuditLedgerWriter(
                ledger_writer=self.ledger_writer,
                time_source=self.time_source,
            )
            with mock.patch.object(
                RuntimeAuditLedgerWriter, "read_for_tenant", original_read_for_tenant
            ):
                other.append("tenant-A", concurrent)
        return original_read_for_tenant(self, tenant_id)

    with mock.patch.object(
        RuntimeAuditLedgerWriter, "read_for_tenant", _concurrent_append_before_second_scan
    ):
        entries = writer.read_full_entries_for_tenant("tenant-A")

    # Exactly ONE refs scan (the pre-sidecar snapshot) — a second scan is
    # the buggy post-read order, and with it the concurrent append above
    # produces a false loss report.
    assert state["calls"] == 1
    hashes = {e.entry_hash for e in entries}
    assert _make_audit_entry("1" * 64).entry_hash in hashes


def test_reader_rejects_tampered_payload_with_stale_hash(tmp_path: Path) -> None:
    """Codex round-42 P1 (PR B1) — a payload modified with its stale
    entry_hash retained passed schema validation AND the coverage check (the
    unchanged hash matches the IS ref), silently feeding tampered content to
    verifiers. The reader now recomputes content integrity like the
    append-side fold."""
    import json as json_module

    writer = _writer(tmp_path)
    writer.append("tenant-A", _make_audit_entry("1" * 64))

    rows = [
        json_module.loads(line)
        for line in writer.sidecar_path.read_text().splitlines()
        if line.strip()
    ]
    rows[0]["entry"]["payload"]["prior_entry_hash"] = "f" * 64  # stale hash kept
    writer.sidecar_path.write_text(
        "\n".join(json_module.dumps(r, separators=(",", ":")) for r in rows) + "\n"
    )

    with pytest.raises(ValueError, match="content-integrity on read"):
        writer.read_full_entries_for_tenant("tenant-A")


def test_colon_bearing_tenant_id_round_trips_all_guards(tmp_path: Path) -> None:
    """Codex round-41 (PR B1) — a tenant id containing ':' (action_id
    'audit:tenant:west:<hash>') made the left-split coverage parse report
    valid history as missing. Hashes parse from the right: append, fresh
    fold, and full-entry read all round-trip."""
    writer = _writer(tmp_path)
    entry = _make_audit_entry("1" * 64)
    assert writer.append("tenant:west", entry) is WriteResult.APPENDED

    fresh = RuntimeAuditLedgerWriter(
        ledger_writer=writer.ledger_writer,
        time_source=writer.time_source,
    )
    assert fresh.append("tenant:west", _make_audit_entry("2" * 64)) is WriteResult.APPENDED
    assert len(fresh.read_full_entries_for_tenant("tenant:west")) == 2


def test_boundary_truncation_fails_loud_on_read_and_append(tmp_path: Path) -> None:
    """Codex round-40 P1 (PR B1) — truncation to a NEWLINE BOUNDARY leaves
    only valid-looking rows: the torn-tail heal sees nothing and the
    absence check never fires, so signed history silently vanished while
    its IS refs survived. Both the reader and a fresh writer's append now
    cross-check IS refs against sidecar membership and fail loud."""
    writer = _writer(tmp_path)
    first = _make_audit_entry("1" * 64)
    second = _make_audit_entry("2" * 64)
    writer.append("tenant-A", first)
    writer.append("tenant-A", second)

    # Truncate to the first record's boundary — a fully well-formed file.
    raw = writer.sidecar_path.read_bytes()
    lines = raw.splitlines(keepends=True)
    writer.sidecar_path.write_bytes(lines[0])

    fresh = RuntimeAuditLedgerWriter(
        ledger_writer=writer.ledger_writer,
        time_source=writer.time_source,
    )
    with pytest.raises(ValueError, match="truncated or lost"):
        fresh.read_full_entries_for_tenant("tenant-A")
    with pytest.raises(ValueError, match="truncated or lost"):
        fresh.append("tenant-A", _make_audit_entry("3" * 64))


def test_map_with_custom_entry_core_still_reseeds_from_its_family(tmp_path: Path) -> None:
    """Codex round-39 (PR B1) — rows written with a caller-supplied
    entry_core lack the redaction-token: ref prefix; the earlier filter
    missed them and a restarted map reseeded from genesis despite an
    existing predecessor. The namespace-key discriminator is entry-core-
    independent: the restarted map must chain onto the custom-core row."""
    from harness_od.audit_ledger_types import StateLedgerEntryRef
    from harness_od.redaction_tokenizer import RedactionTokenRecord
    from harness_runtime.lifecycle.redaction_token_audit_map import (
        AuditLedgerRedactionTokenMap,
    )

    writer = _writer(tmp_path)

    def _record(token: str) -> RedactionTokenRecord:
        return RedactionTokenRecord(
            token=token,
            raw_value=f"raw for {token}",
            semantic_category="PII",
            attribute_key="gen_ai.input.messages",
            trace_id="trace-1",
            span_id=f"span-{token}",
        )

    map_run_1 = AuditLedgerRedactionTokenMap(
        audit_writer=writer,
        tenant_id="tenant-core",
        signing_key_id="chain-key",
        entry_core=StateLedgerEntryRef("custom-core-ref"),
    )
    map_run_1.append(_record("[REDACTED:PII:c1]"))

    map_run_2 = AuditLedgerRedactionTokenMap(
        audit_writer=writer,
        tenant_id="tenant-core",
        signing_key_id="chain-key",
        entry_core=StateLedgerEntryRef("custom-core-ref"),
    )
    map_run_2.append(_record("[REDACTED:PII:c2]"))

    entries = writer.read_full_entries_for_tenant("tenant-core")
    assert len(entries) == 2
    assert entries[1].payload.prior_entry_hash == entries[0].entry_hash


def test_short_reads_never_mark_unread_suffix_as_folded(tmp_path: Path) -> None:
    """Codex round-37 (PR B1) — a short os.read with the offset advanced to
    the snapshot size marked the unread suffix as folded; a replay whose
    identity sat there duplicated its sidecar row. With reads capped to 7
    bytes per call, membership over foreign rows must stay exact (no
    duplicate on replay)."""
    import unittest.mock as mock

    from harness_runtime.lifecycle import audit_writer as audit_writer_module

    writer_a = _writer(tmp_path)
    foreign = _make_audit_entry("a" * 64)
    writer_a.append("tenant-s", foreign)

    writer_b = RuntimeAuditLedgerWriter(
        ledger_writer=writer_a.ledger_writer,
        time_source=writer_a.time_source,
    )
    real_read = audit_writer_module.os.read

    def _short_read(fd: int, n: int) -> bytes:
        return real_read(fd, min(n, 7))

    with mock.patch.object(audit_writer_module.os, "read", _short_read):
        # Replaying the foreign entry through writer_b must dedup (its
        # identity lives in the suffix a short-read-broken fold would miss).
        assert writer_b.append("tenant-s", foreign) is WriteResult.IDEMPOTENT_NOOP

    assert len(writer_b.read_full_entries_for_tenant("tenant-s")) == 1


def test_heal_with_short_reads_never_truncates_valid_records(tmp_path: Path) -> None:
    """Codex round-38 P1 (PR B1) — a short os.read during the torn-tail heal
    made rfind search only a prefix, and ftruncate destroyed every valid
    signed record after it. With reads capped to 7 bytes/call, healing a
    multi-record file with a torn fragment must keep every complete record."""
    import unittest.mock as mock

    from harness_runtime.lifecycle import audit_writer as audit_writer_module

    writer = _writer(tmp_path)
    first = _make_audit_entry("1" * 64)
    second = _make_audit_entry("2" * 64)
    lost = _make_audit_entry("3" * 64)
    writer.append("tenant-A", first)
    writer.append("tenant-A", second)
    writer.append("tenant-A", lost)

    # Tear the final record.
    raw = writer.sidecar_path.read_bytes()
    lines = raw.splitlines(keepends=True)
    writer.sidecar_path.write_bytes(b"".join(lines[:-1]) + lines[-1][: len(lines[-1]) // 2])

    real_read = audit_writer_module.os.read

    def _short_read(fd: int, n: int) -> bytes:
        return real_read(fd, min(n, 7))

    with mock.patch.object(audit_writer_module.os, "read", _short_read):
        # NOOP replay heals the torn tail then re-lands the lost record.
        assert writer.append("tenant-A", lost) is WriteResult.IDEMPOTENT_NOOP

    hashes = [e.entry_hash for e in writer.read_full_entries_for_tenant("tenant-A")]
    assert hashes == [first.entry_hash, second.entry_hash, lost.entry_hash]


def test_deleted_sidecar_with_surviving_is_refs_fails_loud(tmp_path: Path) -> None:
    """Codex round-36 P1 (PR B1) — after entries exist, a deleted sidecar
    silently presented an empty history, and the next append minted a
    REPLACEMENT (old IS refs unrecoverable — the exact loss the sidecar
    prevents). Absence is only legitimate at genuine first use, judged
    against the hash-chained IS refs: both the reader and the append path
    now fail loud, and a genuine first use stays clean."""
    writer = _writer(tmp_path)

    # Genuine first use: absent sidecar + no IS refs = clean empty read.
    assert writer.read_full_entries_for_tenant("tenant-A") == []

    writer.append("tenant-A", _make_audit_entry("1" * 64))
    writer.sidecar_path.unlink()  # cleanup/corruption/tampering

    with pytest.raises(ValueError, match="MISSING"):
        writer.read_full_entries_for_tenant("tenant-A")
    with pytest.raises(ValueError, match="MISSING"):
        writer.append("tenant-A", _make_audit_entry("2" * 64))


def test_symlinked_sidecar_rejected_on_read(tmp_path: Path) -> None:
    """Codex round-33 P1 (PR B1) — a symlinked sidecar must not feed
    attacker-controlled rows through the reader (the seeding path consumes
    them before any validated append runs)."""
    import os as os_module

    writer = _writer(tmp_path)
    lure = tmp_path / "attacker-rows.jsonl"
    lure.write_text('{"tenant_tag":"tenant-A","entry":{}}\n')
    os_module.symlink(lure, writer.sidecar_path)

    with pytest.raises(OSError):
        writer.read_full_entries_for_tenant("tenant-A")


def test_map_reseeds_from_its_own_family_tail_not_foreign(tmp_path: Path) -> None:
    """Codex round-32 P1 (PR B1) — after a foreign family (cost/HITL/...)
    writes the tenant's LATEST sidecar row, a restarted map must reseed from
    the redaction-token family's own tail, not the foreign hash — or the next
    redaction entry fails its own per-family chain check (item (h))."""
    from harness_od.redaction_tokenizer import RedactionTokenRecord
    from harness_runtime.lifecycle.redaction_token_audit_map import (
        AuditLedgerRedactionTokenMap,
    )

    writer = _writer(tmp_path)

    def _record(token: str) -> RedactionTokenRecord:
        return RedactionTokenRecord(
            token=token,
            raw_value=f"raw for {token}",
            semantic_category="PII",
            attribute_key="gen_ai.input.messages",
            trace_id="trace-1",
            span_id=f"span-{token}",
        )

    map_run_1 = AuditLedgerRedactionTokenMap(
        audit_writer=writer,
        tenant_id="tenant-mix",
        signing_key_id="chain-key",
    )
    map_run_1.append(_record("[REDACTED:PII:r1]"))

    # A FOREIGN family entry lands last (entry_core "entry-ref-...", not
    # "redaction-token:...").
    writer.append("tenant-mix", _make_audit_entry("f" * 64))

    # Restart: a fresh map must chain onto R1, not the foreign tail.
    map_run_2 = AuditLedgerRedactionTokenMap(
        audit_writer=writer,
        tenant_id="tenant-mix",
        signing_key_id="chain-key",
    )
    map_run_2.append(_record("[REDACTED:PII:r2]"))

    entries = writer.read_full_entries_for_tenant("tenant-mix")
    family = [e for e in entries if str(e.payload.entry_core).startswith("redaction-token:")]
    assert len(family) == 2
    assert family[1].payload.prior_entry_hash == family[0].entry_hash
