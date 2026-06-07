"""R-008 OD-4 opaque redaction token substrate.

This module provides the provider-free OD substrate for the tokenization arm of
C-OD-13 §13.2: content-bearing span attributes can be replaced with opaque
tokens while the raw value is held behind a token-map sink interface.

It intentionally does not classify semantic content as PII, MCP args, files,
etc. That eval-grade classifier and durable audit-ledger backend remain the
cross-axis follow-on. The substrate here only guarantees that exported span
attributes carry opaque placeholders, not raw content.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import count
from threading import Lock
from typing import Protocol

__all__ = [
    "InMemoryRedactionTokenMap",
    "OpaqueRedactionTokenizer",
    "RedactionAttributeTokenizer",
    "RedactionTokenMap",
    "RedactionTokenRecord",
]


@dataclass(frozen=True, slots=True)
class RedactionTokenRecord:
    """One token-to-raw-value mapping captured before span export."""

    token: str
    attribute_key: str
    raw_value: object
    trace_id: str | None
    span_id: str | None


class RedactionTokenMap(Protocol):
    """Sink for token-to-raw-value mappings.

    Production can back this with a durable audit-ledger writer. Tests and
    provider-free local flows can use `InMemoryRedactionTokenMap`.
    """

    def append(self, record: RedactionTokenRecord) -> None:
        """Persist one token mapping."""


class RedactionAttributeTokenizer(Protocol):
    """Protocol consumed by `RedactionSpanProcessor` token mode."""

    def tokenize(
        self,
        *,
        attribute_key: str,
        raw_value: object,
        trace_id: str | None,
        span_id: str | None,
    ) -> str:
        """Return an opaque replacement token for a content attribute."""
        ...


class InMemoryRedactionTokenMap:
    """Provider-free token-map sink for tests and local wiring probes."""

    def __init__(self) -> None:
        self._records: list[RedactionTokenRecord] = []

    @property
    def records(self) -> tuple[RedactionTokenRecord, ...]:
        """Captured token-map records in append order."""
        return tuple(self._records)

    def append(self, record: RedactionTokenRecord) -> None:
        """Capture one token-map record."""
        self._records.append(record)


class OpaqueRedactionTokenizer:
    """Replace raw content with opaque, non-semantic placeholders.

    Tokens are intentionally per-record unique. The placeholder does not encode
    the raw value, attribute key, trace id, or span id; those details live only
    in the configured `RedactionTokenMap`.
    """

    def __init__(self, *, token_map: RedactionTokenMap, token_prefix: str = "CONTENT") -> None:
        self._token_map = token_map
        self._token_prefix = token_prefix
        self._counter = count(1)
        self._lock = Lock()

    def tokenize(
        self,
        *,
        attribute_key: str,
        raw_value: object,
        trace_id: str | None,
        span_id: str | None,
    ) -> str:
        """Create an opaque token and append its raw mapping to the sink."""
        with self._lock:
            token_ordinal = next(self._counter)
        token = f"[REDACTED:{self._token_prefix}:{token_ordinal:012x}]"
        self._token_map.append(
            RedactionTokenRecord(
                token=token,
                attribute_key=attribute_key,
                raw_value=raw_value,
                trace_id=trace_id,
                span_id=span_id,
            )
        )
        return token
