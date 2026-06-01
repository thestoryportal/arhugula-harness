"""C-OD-12 + C-OD-13 RedactionSpanProcessor tests.

Closes H_T-OD-4 retirement gate "pre-collector redaction SpanProcessor at SDK
boundary BEFORE BatchSpanProcessor buffer". Tests verify §12.1 default-off
content-attribute strip discipline, §12.2 default-on structure-attribute
preservation, OTel SpanProcessor lifecycle no-ops, MultiSpanProcessor
ordering (redaction fires before BSP-equivalent observer), and operator-
injected custom strip-set surface.
"""

from __future__ import annotations

import pytest
from harness_od.content_structure_discipline import DEFAULT_OFF_CONTENT_ATTRIBUTES
from harness_od.redaction_span_processor import RedactionSpanProcessor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
)
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

# --- §12.1 default-off content keys ----------------------------------------


def test_default_redacted_attributes_is_spec_canonical_set() -> None:
    """AC #1: default strip-set matches C-OD-12 §12.1 13-attribute set."""
    processor = RedactionSpanProcessor()
    assert processor.redacted_attributes is DEFAULT_OFF_CONTENT_ATTRIBUTES
    assert len(processor.redacted_attributes) == 13


def test_redacted_attribute_keys_match_otel_genai_semconv_141_opt_in_subset() -> None:
    """AC #2: §12.1 includes OTel GenAI semconv 1.41.0 8-attribute Opt-In set."""
    expected_opt_in_subset = frozenset(
        {
            "gen_ai.input.messages",
            "gen_ai.output.messages",
            "gen_ai.system_instructions",
            "gen_ai.tool.definitions",
            "gen_ai.tool.call.arguments",
            "gen_ai.tool.call.result",
            "gen_ai.retrieval.documents",
            "gen_ai.retrieval.query.text",
        }
    )
    processor = RedactionSpanProcessor()
    assert expected_opt_in_subset.issubset(processor.redacted_attributes)


def test_redacted_attributes_includes_cross_namespace_content_surfaces() -> None:
    """AC #3: §12.1 extends OTel Opt-In with 5 cross-namespace content surfaces."""
    expected_cross_namespace = frozenset(
        {
            "mcp.tool.call.arguments",
            "mcp.tool.call.result",
            "skill.body_content",
            "memory.content",
            "files.content",
        }
    )
    processor = RedactionSpanProcessor()
    assert expected_cross_namespace.issubset(processor.redacted_attributes)


# --- on_end strip discipline ------------------------------------------------


@pytest.fixture()
def exporter_and_provider() -> tuple[InMemorySpanExporter, TracerProvider]:
    """TracerProvider with RedactionSpanProcessor BEFORE InMemorySpanExporter.

    Mirrors production composition: redaction processor fires first; the
    exporter (here `SimpleSpanProcessor(InMemorySpanExporter)`, standing in
    for BSP+OTLP at HEAD) sees the redacted span.
    """
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(RedactionSpanProcessor())
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    return exporter, provider


def test_on_end_strips_gen_ai_input_messages(
    exporter_and_provider: tuple[InMemorySpanExporter, TracerProvider],
) -> None:
    """AC #4: gen_ai.input.messages key removed from exported span."""
    exporter, provider = exporter_and_provider
    tracer = provider.get_tracer("test")
    span = tracer.start_span("anthropic.messages.create")
    span.set_attribute("gen_ai.input.messages", "PII content")
    span.set_attribute("gen_ai.operation.name", "chat")
    span.end()
    [exported] = exporter.get_finished_spans()
    assert "gen_ai.input.messages" not in exported.attributes
    assert exported.attributes["gen_ai.operation.name"] == "chat"


def test_on_end_strips_all_13_content_attributes(
    exporter_and_provider: tuple[InMemorySpanExporter, TracerProvider],
) -> None:
    """AC #5: full §12.1 13-attribute set stripped at on_end."""
    exporter, provider = exporter_and_provider
    tracer = provider.get_tracer("test")
    span = tracer.start_span("s")
    for key in DEFAULT_OFF_CONTENT_ATTRIBUTES:
        span.set_attribute(key, f"content for {key}")
    span.set_attribute("gen_ai.operation.name", "preserved")
    span.end()
    [exported] = exporter.get_finished_spans()
    for key in DEFAULT_OFF_CONTENT_ATTRIBUTES:
        assert key not in exported.attributes, f"redaction failed to strip {key}"
    assert exported.attributes["gen_ai.operation.name"] == "preserved"


def test_on_end_preserves_structure_attributes(
    exporter_and_provider: tuple[InMemorySpanExporter, TracerProvider],
) -> None:
    """AC #6: §12.2 default-on structure attributes survive redaction."""
    exporter, provider = exporter_and_provider
    tracer = provider.get_tracer("test")
    span = tracer.start_span("s")
    span.set_attribute("gen_ai.operation.name", "chat")
    span.set_attribute("gen_ai.provider.name", "anthropic")
    span.set_attribute("gen_ai.request.model", "claude-opus-4-7")
    span.set_attribute("sandbox.tier", "tier_1_process")
    span.set_attribute("hitl.gate.evaluated", True)
    span.end()
    [exported] = exporter.get_finished_spans()
    assert exported.attributes["gen_ai.operation.name"] == "chat"
    assert exported.attributes["gen_ai.provider.name"] == "anthropic"
    assert exported.attributes["gen_ai.request.model"] == "claude-opus-4-7"
    assert exported.attributes["sandbox.tier"] == "tier_1_process"
    assert exported.attributes["hitl.gate.evaluated"] is True


def test_on_end_handles_span_with_no_redacted_keys(
    exporter_and_provider: tuple[InMemorySpanExporter, TracerProvider],
) -> None:
    """AC #7: span carrying zero redacted keys passes through unchanged."""
    exporter, provider = exporter_and_provider
    tracer = provider.get_tracer("test")
    span = tracer.start_span("structure_only")
    span.set_attribute("gen_ai.operation.name", "chat")
    span.set_attribute("gen_ai.usage.input_tokens", 100)
    span.end()
    [exported] = exporter.get_finished_spans()
    assert exported.attributes["gen_ai.operation.name"] == "chat"
    assert exported.attributes["gen_ai.usage.input_tokens"] == 100


def test_on_end_handles_span_with_zero_attributes(
    exporter_and_provider: tuple[InMemorySpanExporter, TracerProvider],
) -> None:
    """AC #8: empty-attribute span (no set_attribute calls) handled."""
    exporter, provider = exporter_and_provider
    tracer = provider.get_tracer("test")
    span = tracer.start_span("empty")
    span.end()
    [exported] = exporter.get_finished_spans()
    # OTel may carry an empty BoundedAttributes; redaction never raises.
    assert dict(exported.attributes) == {}


# --- ordering invariant -----------------------------------------------------


def test_redaction_observable_at_exporter_retrieval_time() -> None:
    """AC #9: span retrieved post-end carries no redacted keys.

    `InMemorySpanExporter` stores `ReadableSpan` references at on_end, not
    snapshots — so the retrieved attribute bag reflects mutations from any
    processor in the chain regardless of registration order. The load-
    bearing invariant for production is that, by the time the SpanData is
    serialized for export, redaction has fired. For synchronous OTLP
    serialization this requires redaction to be registered BEFORE the BSP
    on the TracerProvider (enforced at `materialize_span_processor_stage`).
    """
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(RedactionSpanProcessor())
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("test")
    span = tracer.start_span("s")
    span.set_attribute("gen_ai.input.messages", "PII")
    span.set_attribute("gen_ai.operation.name", "chat")
    span.end()
    [exported] = exporter.get_finished_spans()
    assert "gen_ai.input.messages" not in exported.attributes


# --- lifecycle no-ops -------------------------------------------------------


def test_on_start_is_no_op() -> None:
    """AC #11: on_start returns None and mutates nothing.

    Verified indirectly — on_start is invoked at start_span; if it raised,
    span construction would fail.
    """
    provider = TracerProvider()
    provider.add_span_processor(RedactionSpanProcessor())
    tracer = provider.get_tracer("test")
    span = tracer.start_span("s")
    # Pre-end attribute set after start: no crash from on_start.
    span.set_attribute("gen_ai.input.messages", "PII")
    span.end()


def test_force_flush_returns_true() -> None:
    """AC #12: force_flush no-op returns True."""
    processor = RedactionSpanProcessor()
    assert processor.force_flush() is True
    assert processor.force_flush(timeout_millis=5_000) is True


def test_shutdown_is_no_op() -> None:
    """AC #13: shutdown returns None; idempotent."""
    processor = RedactionSpanProcessor()
    assert processor.shutdown() is None
    assert processor.shutdown() is None  # idempotent


# --- operator-injected strip-set -------------------------------------------


def test_operator_injected_custom_strip_set() -> None:
    """AC #14: operator can construct with a custom redacted_attributes set."""
    custom = frozenset({"custom.secret.attr", "another.private"})
    processor = RedactionSpanProcessor(redacted_attributes=custom)
    assert processor.redacted_attributes == custom


def test_custom_strip_set_actually_strips() -> None:
    """AC #15: custom strip-set applied at on_end (not just exposed)."""
    custom = frozenset({"x.custom.private"})
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(RedactionSpanProcessor(redacted_attributes=custom))
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("test")
    span = tracer.start_span("s")
    span.set_attribute("x.custom.private", "secret")
    span.set_attribute("gen_ai.input.messages", "NOT in custom set")
    span.end()
    [exported] = exporter.get_finished_spans()
    assert "x.custom.private" not in exported.attributes
    # gen_ai.input.messages is in DEFAULT_OFF but NOT in the custom set:
    assert exported.attributes["gen_ai.input.messages"] == "NOT in custom set"
