"""Production ingestion into the sqlite span store, on the runtime's span-export path.

OD spec §C-OD-27 defines a local sqlite span store that `harness-inspect --browse`
(§C-OD-19 §19.3), the holdout sampler (§C-OD-17 §17.3) and the alignment-floor drift
algorithm (§C-OD-18) read. This module is its production writer: when the operator sets
`[runtime.collector] span_store_path`, every batch the `BatchSpanProcessor` exports is
written to that store and then handed, unchanged, to the OTLP exporter.

[LAW:single-enforcer] The exporter is the one layer every finished, sampled, redacted span
already passes through, so the store sees exactly what the OTLP endpoint is sent. The store
is written first: an unreachable OTLP endpoint retries for seconds and must not delay or
drop the local copy.

[LAW:no-silent-failure] A store write that fails never fails the export: the failure is
logged, counted on `failed_span_count`, and the batch still reaches the OTLP exporter,
whose result is the one returned.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import time
from collections.abc import Callable, Mapping, Sequence
from typing import Final

from harness_od.sqlite_span_store import (
    SpanInsertRow,
    initialize_span_store,
    insert_spans,
    retention_cleanup_lazy,
)
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

from harness_runtime.types import CollectorConfig

__all__ = ["SpanStoreMirror", "mirror_to_span_store", "span_insert_row"]

_LOGGER: Final = logging.getLogger("harness.runtime.span_store")

_OTLP_SPAN_KIND_OFFSET: Final = 1
"""The SDK numbers `SpanKind` from INTERNAL = 0; OTLP numbers it from UNSPECIFIED = 0,
INTERNAL = 1. The store keeps the OTLP value, the one the same span carries on the wire."""

_WORKFLOW_ID: Final = "workflow.id"
_WORKFLOW_RUN_ID: Final = "workflow.run_id"
_WORKFLOW_IDEMPOTENCY_KEY: Final = "workflow.idempotency_key"


def _text(attributes: Mapping[str, object], key: str) -> str | None:
    """The attribute as the store's nullable text column: absent stays NULL."""
    value = attributes.get(key)
    return None if value is None else str(value)


def span_insert_row(span: ReadableSpan) -> SpanInsertRow:
    """Project one finished span onto the 14-column row of OD spec §C-OD-27.1.

    The three workflow columns are filled from the `workflow.*` attributes the workflow
    envelope span carries and stay NULL on every other span, as the schema states.
    """
    context = span.get_span_context()
    # A span reaches an exporter only after `end()`, which sets both timestamps.
    assert context is not None and span.start_time is not None and span.end_time is not None
    attributes: dict[str, object] = dict(span.attributes or {})
    return SpanInsertRow(
        span_id=format(context.span_id, "016x"),
        trace_id=format(context.trace_id, "032x"),
        parent_span_id=None if span.parent is None else format(span.parent.span_id, "016x"),
        name=span.name,
        kind=span.kind.value + _OTLP_SPAN_KIND_OFFSET,
        start_time_ns=span.start_time,
        end_time_ns=span.end_time,
        status_code=span.status.status_code.value,
        status_message=span.status.description,
        attributes_json=json.dumps(attributes, sort_keys=True, default=str),
        events_json=json.dumps(
            [
                {
                    "name": event.name,
                    "timestamp_ns": event.timestamp,
                    "attributes": dict(event.attributes or {}),
                }
                for event in span.events
            ],
            sort_keys=True,
            default=str,
        ),
        workflow_id=_text(attributes, _WORKFLOW_ID),
        workflow_run_id=_text(attributes, _WORKFLOW_RUN_ID),
        workflow_idempotency_key=_text(attributes, _WORKFLOW_IDEMPOTENCY_KEY),
    )


class SpanStoreMirror(SpanExporter):
    """A `SpanExporter` that writes each batch to the sqlite span store, then exports it.

    `stored_span_count` and `failed_span_count` are the mirror's own instruments: rows the
    store accepted (a re-exported span id is ignored by the store and not counted) and
    spans in batches the store refused.
    """

    def __init__(
        self,
        *,
        downstream: SpanExporter,
        connection: sqlite3.Connection,
        retention_days: int,
        clock_ns: Callable[[], int] = time.time_ns,
    ) -> None:
        self._downstream: Final = downstream
        self._connection: Final = connection
        self._retention_days: Final = retention_days
        self._clock_ns: Final = clock_ns
        self.stored_span_count: int = 0
        self.failed_span_count: int = 0

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        try:
            self.stored_span_count += insert_spans(
                self._connection, (span_insert_row(span) for span in spans)
            )
            retention_cleanup_lazy(self._connection, self._retention_days, self._clock_ns())
        except sqlite3.Error:
            self.failed_span_count += len(spans)
            _LOGGER.error(
                "span store write failed for a batch of %d spans (%d failed in total); "
                "the batch is still exported",
                len(spans),
                self.failed_span_count,
                exc_info=True,
            )
        return self._downstream.export(spans)

    def shutdown(self) -> None:
        self._connection.close()
        self._downstream.shutdown()

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        return self._downstream.force_flush(timeout_millis)


def mirror_to_span_store(downstream: SpanExporter, collector: CollectorConfig) -> SpanExporter:
    """`downstream` itself when no span store is configured, else a mirror in front of it.

    Opening the store here makes an unusable `span_store_path` a bootstrap failure.
    """
    match collector.span_store_path:
        case None:
            return downstream
        case path:
            return SpanStoreMirror(
                downstream=downstream,
                connection=initialize_span_store(path),
                retention_days=collector.sqlite_retention_days,
            )
