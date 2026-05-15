"""7a substitution scaffolding — OTel emission (substitutes H_T-OD-2 + H_T-OD-4).

NOT H_T atomic-unit implementation. Bounded 7a substitution scaffolding
per Phase_7a_Substitution_Scaffolding.md §6 + Phase_7_Meta_Architecture_v1.md
§5.5 (H_T-OD-2 OTel SDK injection; H_T-OD-4 SpanProcessor injection).
Retired at U-OD-04..U-OD-08 (H_T-OD-2) and U-OD-13..U-OD-16 (H_T-OD-4).

All OTel emission happens at the MCP server boundary (H_T-authored code) —
H_E does not participate in OTel emission (OD-AL-3, the canonical
concretization of X-AL-1).

7a-PROVISIONAL notes:
  - GenAI semconv 1.41.0 (cited at the H_T-OD-2 substitution row) is
    deferred: the 12 representative tools are not LLM calls, so the
    `Resource` carries service identity only. GenAI semconv lands at
    U-OD-04..U-OD-08.
  - The OTel `SpanProcessor` ABC delivers an immutable `ReadableSpan` to
    `on_end`, so true structure-not-content redaction cannot mutate the
    span here — real OTel redaction is exporter-side. `RedactingSpanProcessor`
    below is a schema-faithful stub marking the H_T-OD-4 injection seam;
    real redaction lands at U-OD-13..U-OD-16.
"""

from __future__ import annotations

import functools
import os
import sys
from collections.abc import Callable
from typing import TypeVar

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan, Span, SpanProcessor, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

_SERVICE_NAME = "harness-7a-scaffold"
_SERVICE_VERSION = "0.0.0-7a"


class RedactingSpanProcessor(SpanProcessor):
    """H_T-OD-4 SpanProcessor-injection seam — 7a schema-faithful stub.

    Wraps a delegate `SpanProcessor`. `on_end` is the structure-not-content
    redaction seam. 7a-PROVISIONAL: the OTel `SpanProcessor` ABC delivers an
    immutable `ReadableSpan` to `on_end`, so the stub forwards spans
    unchanged — real redaction-before-export lands at U-OD-13..U-OD-16.
    """

    def __init__(self, delegate: SpanProcessor) -> None:
        self._delegate = delegate

    def on_start(self, span: Span, parent_context: object | None = None) -> None:
        self._delegate.on_start(span, parent_context)  # type: ignore[arg-type]

    def on_end(self, span: ReadableSpan) -> None:
        # [redaction seam — H_T-OD-4] no-op at 7a; see U-OD-13..U-OD-16.
        self._delegate.on_end(span)

    def shutdown(self) -> None:
        self._delegate.shutdown()

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return self._delegate.force_flush(timeout_millis)


def _build_tracer() -> trace.Tracer:
    """Configure the TracerProvider and return the scaffolding tracer.

    Console export goes to stderr — stdout is the stdio MCP JSON-RPC
    channel and must not be polluted. OTLP export to a user-launched
    Collector (H_T-OD-6) is enabled only when OTEL_EXPORTER_OTLP_ENDPOINT
    is set, so the default run stays clean when no Collector is up.
    """
    resource = Resource.create({"service.name": _SERVICE_NAME, "service.version": _SERVICE_VERSION})
    provider = TracerProvider(resource=resource)

    # Console exporter — emission visible at the MCP server boundary even
    # before a Collector is launched. stderr, NOT stdout.
    provider.add_span_processor(
        RedactingSpanProcessor(BatchSpanProcessor(ConsoleSpanExporter(out=sys.stderr)))
    )

    # OTLP exporter — to a user-launched Collector subprocess (H_T-OD-6).
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if endpoint:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )

        provider.add_span_processor(
            RedactingSpanProcessor(
                BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True))
            )
        )

    trace.set_tracer_provider(provider)
    return trace.get_tracer(_SERVICE_NAME, _SERVICE_VERSION)


tracer: trace.Tracer = _build_tracer()

_F = TypeVar("_F", bound=Callable[..., object])


def traced(span_name: str) -> Callable[[_F], _F]:
    """Wrap an MCP tool so each invocation emits one span at the boundary.

    Applied between `@mcp.tool()` and the tool function — `functools.wraps`
    preserves the signature so FastMCP schema generation is unaffected.
    """

    def decorator(fn: _F) -> _F:
        @functools.wraps(fn)
        def wrapper(*args: object, **kwargs: object) -> object:
            with tracer.start_as_current_span(span_name, kind=trace.SpanKind.SERVER) as span:
                try:
                    result = fn(*args, **kwargs)
                    span.set_status(trace.StatusCode.OK)
                    return result
                except Exception as exc:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(exc)))
                    raise

        return wrapper  # type: ignore[return-value]

    return decorator
