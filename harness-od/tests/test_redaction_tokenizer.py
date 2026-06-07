"""R-008 OD-4 gate (b) substrate — opaque redaction tokens.

These tests cover the provider-free OD substrate only: replacing content-bearing
span attributes with opaque tokens and keeping the raw value in a token-map
sink. The eval-grade semantic classifier and durable audit-ledger persistence
remain separate cross-axis work.
"""

from __future__ import annotations

from harness_od.redaction_tokenizer import InMemoryRedactionTokenMap, OpaqueRedactionTokenizer


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
