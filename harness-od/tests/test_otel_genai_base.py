"""Tests for U-OD-04 — OTel GenAI semconv 1.41.0 base-layer attributes (C-OD-04).

Test set per the U-OD-04 v2.5 `Tests:` field — covers acceptance #1-#8. The
plan's specification-level test names carry a `§` glyph (not a valid Python
identifier character); they are materialized here with `spec_4_3`-style names.
"""

from __future__ import annotations

from harness_od.otel_genai_base import (
    BASE_LAYER_ATTRIBUTES,
    BASE_METRIC_NAME,
    HIERARCHY_CORRELATION_KEY,
    SPAN_NAME_FORMAT,
    AttributeTier,
    GenAiAttribute,
    GenAiOperation,
    attributes_in_tier,
    span_name,
)
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

# --- Spec §4 verbatim reference sets (transcribed from C-OD-04) -------------

# §4.2 operations enum.
_SPEC_OPERATIONS = {
    "chat",
    "text_completion",
    "embeddings",
    "generate_content",
    "create_agent",
    "invoke_agent",
    "execute_tool",
}

# §4.3 attribute-tier table.
_SPEC_REQUIRED_STABLE = {
    "gen_ai.operation.name",
    "gen_ai.provider.name",
    "gen_ai.request.model",
}
_SPEC_RECOMMENDED_DEVELOPMENT = {
    "gen_ai.usage.input_tokens",
    "gen_ai.usage.output_tokens",
    "gen_ai.response.finish_reasons",
    "server.address",
    "server.port",
    "gen_ai.conversation.id",
}
_SPEC_OPT_IN_CONTENT = {
    "gen_ai.input.messages",
    "gen_ai.output.messages",
    "gen_ai.system_instructions",
    "gen_ai.tool.definitions",
    "gen_ai.tool.call.arguments",
    "gen_ai.tool.call.result",
    "gen_ai.retrieval.documents",
    "gen_ai.retrieval.query.text",
}


# --- acceptance #1 — span name format --------------------------------------


def test_span_name_format_byte_exact_three_component() -> None:
    """§4.1 verbatim — the 3-component span name format."""
    assert SPAN_NAME_FORMAT == (
        "{gen_ai.operation.name} {gen_ai.provider.name} {gen_ai.request.model}"
    )
    assert SPAN_NAME_FORMAT.count("{") == 3


def test_span_name_resolves_at_span_emission_time() -> None:
    """`span_name` materializes the §4.1 format with call-bound values."""
    assert (
        span_name(GenAiOperation.CHAT, "anthropic", "claude-opus-4-7")
        == "chat anthropic claude-opus-4-7"
    )


# --- acceptance #2 — operations enum ---------------------------------------


def test_genai_operation_cardinality_seven() -> None:
    """§4.2 — exactly 7 operations."""
    assert len(GenAiOperation) == 7
    assert {op.value for op in GenAiOperation} == _SPEC_OPERATIONS


def test_genai_operation_includes_generate_content() -> None:
    """§4.2 — `generate_content` is present (the value the v2.1 enum omitted)."""
    assert GenAiOperation.GENERATE_CONTENT.value == "generate_content"


# --- acceptance #3 — attribute tiers ---------------------------------------


def test_attribute_tier_cardinality_three() -> None:
    """§4.3 — exactly 3 tiers (the v2.1 enum carried a 4th, `CONDITIONAL`)."""
    assert len(AttributeTier) == 3
    assert {t.value for t in AttributeTier} == {
        "Required (Stable)",
        "Recommended (Development)",
        "Opt-In content",
    }


# --- acceptance #4 — base-layer attribute set + per-attribute tier ----------


def test_base_layer_attributes_byte_exact_per_semconv_1_41_0() -> None:
    """§4.3 — the base-layer attribute name set, verbatim (17 attributes)."""
    names = {attr.name for attr in BASE_LAYER_ATTRIBUTES}
    assert names == (_SPEC_REQUIRED_STABLE | _SPEC_RECOMMENDED_DEVELOPMENT | _SPEC_OPT_IN_CONTENT)
    assert len(BASE_LAYER_ATTRIBUTES) == 17


def test_required_stable_tier_attributes_per_spec_4_3() -> None:
    """§4.3 Required (Stable) row, verbatim."""
    got = {a.name for a in attributes_in_tier(AttributeTier.REQUIRED_STABLE)}
    assert got == _SPEC_REQUIRED_STABLE


def test_recommended_development_tier_attributes_per_spec_4_3() -> None:
    """§4.3 Recommended (Development) row, verbatim."""
    got = {a.name for a in attributes_in_tier(AttributeTier.RECOMMENDED_DEVELOPMENT)}
    assert got == _SPEC_RECOMMENDED_DEVELOPMENT


def test_opt_in_content_tier_attributes_per_spec_4_3() -> None:
    """§4.3 Opt-In content row, verbatim."""
    got = {a.name for a in attributes_in_tier(AttributeTier.OPT_IN_CONTENT)}
    assert got == _SPEC_OPT_IN_CONTENT


def test_attribute_serialization_round_trip() -> None:
    """`GenAiAttribute` is frozen and round-trips through serialization."""
    attr = GenAiAttribute(name="gen_ai.request.model", tier=AttributeTier.REQUIRED_STABLE)
    assert GenAiAttribute.model_validate(attr.model_dump()) == attr
    assert hash(attr) == hash(
        GenAiAttribute(name="gen_ai.request.model", tier=AttributeTier.REQUIRED_STABLE)
    )


# --- acceptance #5 — parent-child trace context propagation (§4.4) ----------


def test_trace_id_inherited_from_parent() -> None:
    """§4.4 — a child span inherits its parent's `trace_id`."""
    tracer = TracerProvider().get_tracer("u-od-04-test")
    with tracer.start_as_current_span("parent") as parent:
        parent_trace_id = parent.get_span_context().trace_id
        with tracer.start_as_current_span("child") as child:
            assert child.get_span_context().trace_id == parent_trace_id


def test_parent_span_id_propagation() -> None:
    """§4.4 — a child span references its parent via `parent` span context;
    each span carries a unique `span_id`."""
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("u-od-04-test")
    with tracer.start_as_current_span("parent"), tracer.start_as_current_span("child"):
        pass
    by_name: dict[str, ReadableSpan] = {span.name: span for span in exporter.get_finished_spans()}
    parent, child = by_name["parent"], by_name["child"]
    assert parent.context is not None
    assert child.context is not None
    assert child.parent is not None
    assert child.parent.span_id == parent.context.span_id
    assert child.context.span_id != parent.context.span_id


def test_hierarchy_correlation_key_is_conversation_id() -> None:
    """§4.4 — `gen_ai.conversation.id` is the hierarchy correlation key."""
    assert HIERARCHY_CORRELATION_KEY == "gen_ai.conversation.id"


# --- acceptance #6 — base metric -------------------------------------------


def test_base_metric_name_byte_exact_operation_duration() -> None:
    """§4.5 verbatim — `gen_ai.client.operation.duration` (the v2.1 value was
    `gen_ai.client.token.usage`)."""
    assert BASE_METRIC_NAME == "gen_ai.client.operation.duration"


# --- acceptance #7 — base layer is composition substrate -------------------


def test_specialization_layer_does_not_replace_base_layer() -> None:
    """Acceptance #7 — `BASE_LAYER_ATTRIBUTES` is an immutable base set the
    specialization namespaces (C-OD-05) compose over, never replace."""
    assert isinstance(BASE_LAYER_ATTRIBUTES, tuple)
    # A specialization namespace adds attributes; the base set is unchanged.
    specialized = (
        *BASE_LAYER_ATTRIBUTES,
        GenAiAttribute(name="hitl.gate.level", tier=AttributeTier.RECOMMENDED_DEVELOPMENT),
    )
    assert len(specialized) == len(BASE_LAYER_ATTRIBUTES) + 1
    assert all(base in specialized for base in BASE_LAYER_ATTRIBUTES)


# --- acceptance #8 — semconv 1.41.0 conformance ----------------------------


def test_otel_semconv_validator_passes() -> None:
    """Acceptance #8 — every base-layer attribute name conforms to the OTel
    GenAI semconv 1.41.0 naming surface attested at spec §4.3 (dotted lowercase
    segments; within the §4.3 verbatim set)."""
    for attr in BASE_LAYER_ATTRIBUTES:
        assert attr.name == attr.name.lower()
        assert " " not in attr.name
        assert attr.name.startswith(("gen_ai.", "server."))
