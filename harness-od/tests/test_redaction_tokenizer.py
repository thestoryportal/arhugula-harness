"""R-008 OD-4 gate (b) substrate — opaque redaction tokens.

These tests cover the provider-free OD substrate only: replacing content-bearing
span attributes with opaque tokens and keeping the raw value in a token-map
sink. The eval-grade semantic classifier and durable audit-ledger persistence
remain separate cross-axis work.
"""

from __future__ import annotations

import pytest
from harness_od.audit_signing_errors import AuditSigningFailedError
from harness_od.redaction_token_audit import compose_redaction_token_audit_entry
from harness_od.redaction_tokenizer import (
    DeterministicRedactionClassifier,
    EvalGradeSemanticRedactionClassifier,
    InMemoryRedactionTokenMap,
    OpaqueRedactionTokenizer,
    RedactionTokenRecord,
)


def test_opaque_tokenizer_replaces_value_without_leaking_raw_content() -> None:
    token_map = InMemoryRedactionTokenMap()
    tokenizer = OpaqueRedactionTokenizer(token_map=token_map)

    token = tokenizer.tokenize(
        attribute_key="gen_ai.input.messages",
        raw_value="customer ssn 123-45-6789",
        trace_id="trace-1",
        span_id="span-1",
    )

    assert token.startswith("[REDACTED:CONTENT:")
    assert token.endswith("]")
    assert "customer" not in token
    assert "123-45-6789" not in token

    [record] = token_map.records
    assert record.token == token
    assert record.attribute_key == "gen_ai.input.messages"
    assert record.raw_value == "customer ssn 123-45-6789"
    assert record.trace_id == "trace-1"
    assert record.span_id == "span-1"


def test_opaque_tokenizer_assigns_distinct_tokens_per_record() -> None:
    token_map = InMemoryRedactionTokenMap()
    tokenizer = OpaqueRedactionTokenizer(token_map=token_map)

    first = tokenizer.tokenize(
        attribute_key="gen_ai.input.messages",
        raw_value="same raw value",
        trace_id="trace-1",
        span_id="span-1",
    )
    second = tokenizer.tokenize(
        attribute_key="gen_ai.input.messages",
        raw_value="same raw value",
        trace_id="trace-1",
        span_id="span-1",
    )

    assert first != second
    assert [record.token for record in token_map.records] == [first, second]


def test_classifier_tokenizer_emits_category_specific_pii_token() -> None:
    token_map = InMemoryRedactionTokenMap()
    tokenizer = OpaqueRedactionTokenizer(
        token_map=token_map,
        classifier=DeterministicRedactionClassifier(),
    )

    token = tokenizer.tokenize(
        attribute_key="gen_ai.input.messages",
        raw_value="customer ssn 123-45-6789",
        trace_id="trace-1",
        span_id="span-1",
    )

    assert token.startswith("[REDACTED:PII:")
    assert "123-45-6789" not in token

    [record] = token_map.records
    assert record.semantic_category == "PII"
    assert record.raw_value == "customer ssn 123-45-6789"


def test_classifier_uses_attribute_shape_for_mcp_argument_tokens() -> None:
    token_map = InMemoryRedactionTokenMap()
    tokenizer = OpaqueRedactionTokenizer(
        token_map=token_map,
        classifier=DeterministicRedactionClassifier(),
    )

    token = tokenizer.tokenize(
        attribute_key="mcp.tool.call.arguments",
        raw_value='{"query":"plain tool argument"}',
        trace_id="trace-1",
        span_id="span-1",
    )

    assert token.startswith("[REDACTED:MCP_ARG:")

    [record] = token_map.records
    assert record.semantic_category == "MCP_ARG"


def test_eval_grade_classifier_preserves_genai_prompt_category_without_pii() -> None:
    classifier = EvalGradeSemanticRedactionClassifier()

    classification = classifier.classify(
        attribute_key="gen_ai.input.messages",
        raw_value="summarize the public changelog",
    )

    assert classification.category == "GENAI_PROMPT"


def test_eval_grade_classifier_uses_tool_result_category() -> None:
    classifier = EvalGradeSemanticRedactionClassifier()

    classification = classifier.classify(
        attribute_key="gen_ai.tool.call.result",
        raw_value='{"status":"ok"}',
    )

    assert classification.category == "TOOL_RESULT"


class _Ed25519Backend:
    """TEST-ONLY C-CP-20 §20.2.1 `SigningBackend` double (real Ed25519).

    OD spec v1.34 §21.2.3 row 6 — `compose_redaction_token_audit_entry`
    requires a configured backend at every persona tier; this test exercises
    the composer's attribute-shape contract, not signing correctness, so a
    minimal real-crypto double stands in.
    """

    algorithm = "ed25519"

    def __init__(self) -> None:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

        self._private_key = Ed25519PrivateKey.generate()

    def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
        del key_id, key_period
        return self._private_key.sign(message)

    def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
        del message, signature, key_id, key_period
        return True


def test_redaction_token_record_composes_signed_audit_entry() -> None:
    record = RedactionTokenRecord(
        token="[REDACTED:CONTENT:000000000001]",
        attribute_key="gen_ai.input.messages",
        raw_value="customer ssn 123-45-6789",
        trace_id="trace-1",
        span_id="span-1",
    )

    entry = compose_redaction_token_audit_entry(
        record, key_id="redaction-test-key", backend=_Ed25519Backend()
    )

    attrs = entry.payload.audit_namespace_attrs
    assert attrs["audit.redaction_token.action_id"].startswith("redaction_token:")
    assert attrs["audit.redaction_token.response"] == "token_mapped"
    assert attrs["audit.redaction_token.token"] == "[REDACTED:CONTENT:000000000001]"
    assert attrs["audit.redaction_token.semantic_category"] == "CONTENT"
    assert attrs["audit.redaction_token.attribute_key"] == "gen_ai.input.messages"
    assert attrs["audit.redaction_token.raw_value"] == "customer ssn 123-45-6789"
    assert attrs["audit.redaction_token.trace_id"] == "trace-1"
    assert attrs["audit.redaction_token.span_id"] == "span-1"
    assert len(attrs["audit.redaction_token.raw_value_sha256"]) == 64
    assert entry.signature_attrs.audit_signature_key_id == "redaction-test-key"


def test_redaction_token_absent_backend_raises_typed_every_tier() -> None:
    """Witness (f) — OD spec v1.34 §21.2.3 row 6 — the redaction-token
    signing path is UNCONDITIONALLY fail-closed at every persona tier: an
    absent `backend` is itself a typed `AuditSigningFailedError`, not the
    `unsigned:*` placeholder — raw redaction values must never persist
    against an unsigned row. Mutation probe: letting the placeholder through
    on this path (reverting the zeroth-site check) fails this test."""
    record = RedactionTokenRecord(
        token="[REDACTED:CONTENT:000000000002]",
        attribute_key="gen_ai.input.messages",
        raw_value="customer ssn 123-45-6789",
        trace_id="trace-1",
        span_id="span-1",
    )
    with pytest.raises(AuditSigningFailedError, match="REQUIRED"):
        compose_redaction_token_audit_entry(record, key_id="redaction-test-key")
