"""R-008 OD-4 redaction-token audit-map persistence tests."""

from __future__ import annotations

from harness_od.redaction_tokenizer import OpaqueRedactionTokenizer
from harness_runtime.lifecycle.redaction_token_audit_map import AuditLedgerRedactionTokenMap


class _RecordingAuditWriter:
    def __init__(self) -> None:
        self.appended: list[tuple[str | None, object]] = []

    def append(self, tenant_id: str | None, audit_entry: object) -> object:
        self.appended.append((tenant_id, audit_entry))
        return "appended"


def test_audit_ledger_redaction_token_map_writes_signed_audit_entry() -> None:
    audit_writer = _RecordingAuditWriter()
    token_map = AuditLedgerRedactionTokenMap(
        audit_writer=audit_writer,
        tenant_id="tenant-r008",
        signing_key_id="redaction-token-test-key",
    )
    tokenizer = OpaqueRedactionTokenizer(token_map=token_map)

    token = tokenizer.tokenize(
        attribute_key="mcp.tool.call.arguments",
        raw_value='{"secret":"value"}',
        trace_id="trace-r008",
        span_id="span-r008",
    )

    assert len(audit_writer.appended) == 1
    tenant_id, audit_entry = audit_writer.appended[0]
    assert tenant_id == "tenant-r008"
    attrs = audit_entry.payload.audit_namespace_attrs
    assert attrs["audit.redaction_token.token"] == token
    assert attrs["audit.redaction_token.attribute_key"] == "mcp.tool.call.arguments"
    assert attrs["audit.redaction_token.raw_value"] == '{"secret":"value"}'
    assert attrs["audit.redaction_token.trace_id"] == "trace-r008"
    assert attrs["audit.redaction_token.span_id"] == "span-r008"
    assert audit_entry.signature_attrs.audit_signature_key_id == "redaction-token-test-key"


class _Ed25519Backend:
    """TEST-ONLY C-CP-20 §20.2.1 `SigningBackend` double (real Ed25519)."""

    algorithm = "ed25519"

    def __init__(self) -> None:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

        self._private_key = Ed25519PrivateKey.generate()
        self.sign_calls = 0

    def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
        del key_id, key_period
        self.sign_calls += 1
        return self._private_key.sign(message)

    def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
        del message, signature, key_id, key_period
        return True


def test_token_map_threads_signing_backend_to_real_signature() -> None:
    """OD spec v1.33 §21.2.1 (out-of-family Codex P1 on the B-47 PR-A landing)
    — a composition-root-injected `signing_backend` reaches the redaction-token
    audit writer: the persisted entry carries a genuine base64 signature, not
    the `unsigned:` placeholder, and the backend was consulted once per
    append."""
    import base64

    audit_writer = _RecordingAuditWriter()
    backend = _Ed25519Backend()
    token_map = AuditLedgerRedactionTokenMap(
        audit_writer=audit_writer,
        tenant_id="tenant-r008",
        signing_key_id="redaction-token-test-key",
        signing_backend=backend,
    )
    tokenizer = OpaqueRedactionTokenizer(token_map=token_map)

    tokenizer.tokenize(
        attribute_key="mcp.tool.call.arguments",
        raw_value='{"secret":"value"}',
        trace_id="trace-r008",
        span_id="span-r008",
    )

    assert backend.sign_calls == 1
    _tenant_id, audit_entry = audit_writer.appended[0]
    value = audit_entry.signature_attrs.audit_signature_value
    assert not value.startswith("unsigned:")
    assert len(base64.b64decode(value, validate=True)) == 64


def test_token_map_without_backend_preserves_placeholder() -> None:
    """§21.2.1 item 2 at this writer — absent `signing_backend` (every existing
    caller), the placeholder signing path is byte-identical to pre-seam
    behavior."""
    audit_writer = _RecordingAuditWriter()
    token_map = AuditLedgerRedactionTokenMap(
        audit_writer=audit_writer,
        tenant_id="tenant-r008",
        signing_key_id="redaction-token-test-key",
    )
    OpaqueRedactionTokenizer(token_map=token_map).tokenize(
        attribute_key="k",
        raw_value="v",
        trace_id=None,
        span_id=None,
    )
    _tenant_id, audit_entry = audit_writer.appended[0]
    value = audit_entry.signature_attrs.audit_signature_value
    assert value.startswith("unsigned:redaction-token-test-key:")
