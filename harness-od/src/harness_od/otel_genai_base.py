"""OTel GenAI semconv 1.41.0 base-layer attributes — U-OD-04.

Implements C-OD-04 §4.1 (span name format), §4.2 (operations enum), §4.3
(attribute tiers), §4.4 (hierarchy correlation), §4.5 (base metric).

The base layer is the cross-vendor-stable substrate over which the 15 OD
specialization-layer namespaces (C-OD-05) compose — specialization namespaces
add attributes but never replace base-layer attributes (acceptance #7). Every
attribute name, operation value, tier name, the span-name format, and the base
metric name is the OTel GenAI semantic conventions 1.41.0 surface, transcribed
verbatim from the spec §4 tables.

Authority: Implementation_Plan_Operational_Discipline_v2_6.md §3.2.1 U-OD-04
(v2.6 carrier-growth revision — additive `Span*` OTel-handle alias family +
acceptance #9; over the v2.5 conformance revision that absorbed Tension 004 /
the §4A verbatim-divergence cluster: 3-component span name, 7-operation enum,
3-tier `AttributeTier`, `gen_ai.client.operation.duration` base metric);
Spec_Operational_Discipline_v1_2.md §4 C-OD-04 (preserved verbatim into v1.3
per v1.3 §0.1); ADR-D6 v1.2 §1.2 base-layer block (OTel GenAI semconv 1.41.0
[HIGH] cross-vendor floor); ADR-F5 (observability substrate primitive) — the
`Span*` family authority trace (Q-R5-6).
"""

from __future__ import annotations

from enum import StrEnum

from opentelemetry.trace import Span as _OTelSpan
from opentelemetry.util.types import Attributes as _OTelAttributes
from pydantic import BaseModel, ConfigDict

# --- v2.6 addition: OTel-handle alias family (M-1 carrier) ------------------
# Per T2 FACTOR-OUT verdict (acceptance #9): these are harness aliases for the
# OTel-SDK span data model (Target_Stack_Commitment §5.2 OTel-libraries
# adoption). ADR-F5 observability substrate + ADR-D6 v1.2 12-namespace OTel
# schema commit the span/attribute handle concept. NOT a harness design
# extension (X-AL-3 cleared by T2). This is the single declaration site for
# the Span* family consumed at U-OD-09 / U-OD-10 / U-OD-19 / U-OD-20 /
# U-OD-23 / U-OD-25 / U-OD-26 / U-OD-30 / U-OD-31.

#: An opaque handle to an OTel span — the parent-span handle the harness
#: threads through emission functions. Type-alias of the OTel-SDK span handle
#: (`opentelemetry.trace.Span`); the harness does not redefine the OTel span
#: data model.
type SpanRef = _OTelSpan

#: A `SpanRef` known to be a child span (eval child-span emission per
#: C-OD-17 §17.2). Same OTel-SDK substrate as `SpanRef`; a nominal distinction
#: marking child-span emission positions.
type ChildSpanRef = _OTelSpan

#: The OTel attribute bag — the typed attribute map a span carries. Type-alias
#: of the OTel-SDK attribute model (`opentelemetry.util.types.Attributes`,
#: i.e. `Mapping[str, AttributeValue]`).
type SpanAttributes = _OTelAttributes


class GenAiOperation(StrEnum):
    """The 9 `gen_ai.operation.name` values per OTel 1.41.0 archived text.

    v1.16 canonical-reading amendment per .harness/class_1_fork_tension_004_
    d2_d3_otel_141_relitigation.md §4.1 (A) (operator-ratified 2026-05-26).
    The v1.2-v1.15 7-value enumeration was a misreading of the cited OTel
    GenAI semconv 1.41.0 archived text; the actual 1.41.0 text at
    `github.com/open-telemetry/semantic-conventions/blob/v1.41.0/docs/gen-ai/
    gen-ai-spans.md` declares 9 values. `invoke_workflow` + `retrieval` are
    NEW at v1.16 per OD spec v1.16 §1.1.
    """

    CHAT = "chat"
    CREATE_AGENT = "create_agent"
    EMBEDDINGS = "embeddings"
    EXECUTE_TOOL = "execute_tool"
    GENERATE_CONTENT = "generate_content"
    INVOKE_AGENT = "invoke_agent"
    INVOKE_WORKFLOW = "invoke_workflow"
    RETRIEVAL = "retrieval"
    TEXT_COMPLETION = "text_completion"


class AttributeTier(StrEnum):
    """The 4 attribute tiers per OTel 1.41.0 archived text.

    v1.16 canonical-reading amendment per .harness/class_1_fork_tension_004_
    d2_d3_otel_141_relitigation.md §4.1 (A) (operator-ratified 2026-05-26).
    The v1.2-v1.15 3-tier enumeration was a misreading of the cited OTel
    GenAI semconv 1.41.0 archived text; the actual 1.41.0 text declares 4
    tiers. `CONDITIONALLY_REQUIRED` is NEW at v1.16 per OD spec v1.16 §1.2.
    Internal naming preserved (`REQUIRED_STABLE` / `RECOMMENDED_DEVELOPMENT`
    / `OPT_IN_CONTENT`) per v1.2-v1.15 lineage with OTel canonical names
    documented as derivative per OD spec v1.16 §1.2 mapping table.

    Emission posture per tier: Required (Stable) always emitted;
    Conditionally Required emitted per per-attribute conditional rule (NEW
    at v1.16 — per-attribute conditional rules owed at future tier-assignment
    audit per OD spec v1.16 §1.3 + §"Adjacent observations" (e));
    Recommended (Development) emitted unless cardinality-safe-attribute
    discipline excludes (C-OD-11); Opt-In content default-off per redaction
    discipline (C-OD-12).
    """

    REQUIRED_STABLE = "Required (Stable)"
    CONDITIONALLY_REQUIRED = "Conditionally Required"
    RECOMMENDED_DEVELOPMENT = "Recommended (Development)"
    OPT_IN_CONTENT = "Opt-In content"


class GenAiAttribute(BaseModel):
    """A base-layer attribute — its semconv name and its emission tier.

    Frozen → `Eq` + `Hash` over its two fields, stable under serialization
    (acceptance #4 / the round-trip test). The name is an OTel GenAI semconv
    1.41.0 attribute key transcribed verbatim from the §4.3 table.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    tier: AttributeTier


#: §4.1 span name format, verbatim (acceptance #1).
#:
#: v1.12 canonical-reading amendment per .harness/class_1_fork_genai_span_name_
#: four_way_drift.md §7.4.1 (operator-ratified 2026-05-26). The v1.2-v1.11
#: 3-token form was a misreading of the cited OTel GenAI semconv 1.41.0
#: archived text; the actual 1.41.0 text specifies 2-token. `gen_ai.provider.name`
#: is REMOVED from the span-name format but PRESERVED as a Required (Stable)
#: tier attribute at §4.3 (BASE_LAYER_ATTRIBUTES below).
SPAN_NAME_FORMAT: str = "{gen_ai.operation.name} {gen_ai.request.model}"

#: §4.5 base metric name, verbatim — a histogram with cardinality control per
#: C-OD-11 (acceptance #6).
BASE_METRIC_NAME: str = "gen_ai.client.operation.duration"

#: §4.4 hierarchy-correlation key — the correlation attribute for the
#: `invoke_agent` / `chat` operations per OD spec v1.20 §1.1 canonical reading
#: (narrowed from v1.2-v1.19 `invoke_agent` / `chat` / `execute_tool` claim;
#: OTel 1.41.0 execute_tool span attribute table does NOT declare
#: `gen_ai.conversation.id` — verified at gen-ai-spans.md lines 612-621).
#: Cross-span linkage from `execute_tool` to its parent `invoke_agent` or
#: `chat` span uses OTel-canonical trace context (trace_id + parent_span_id),
#: not `gen_ai.conversation.id`. Span-attribute only, never a metric dimension,
#: per cardinality-safe discipline (C-OD-11).
HIERARCHY_CORRELATION_KEY: str = "gen_ai.conversation.id"

#: §4.3 base-layer attribute set with per-attribute tier classification,
#: transcribed verbatim from the §4.3 table (acceptance #4). v1.19 canonical
#: reading per OD spec v1.19 §1.1 — per-attribute Requirement-Level audit
#: against OTel GenAI semconv 1.41.0 chat-span table redistributed 3
#: attributes to Conditionally Required tier (`gen_ai.request.model`,
#: `server.port`, `gen_ai.conversation.id`). 2 Required + 3 Conditionally
#: Required + 4 Recommended + 8 Opt-In = 17 attributes (attribute SET
#: preserved verbatim from v1.2; tier classification only redistributed).
BASE_LAYER_ATTRIBUTES: tuple[GenAiAttribute, ...] = (
    # Required (Stable) — always emitted (OTel 1.41.0: Required).
    GenAiAttribute(name="gen_ai.operation.name", tier=AttributeTier.REQUIRED_STABLE),
    GenAiAttribute(name="gen_ai.provider.name", tier=AttributeTier.REQUIRED_STABLE),
    # Conditionally Required — OTel 1.41.0 per-attribute condition; harness
    # may emit unconditionally where condition is harness-always-met (e.g.
    # `gen_ai.request.model` "If available" with harness always knowing
    # model). Tier classification at §4.3; emission policy at OD plan AC #4.
    GenAiAttribute(name="gen_ai.request.model", tier=AttributeTier.CONDITIONALLY_REQUIRED),
    GenAiAttribute(name="server.port", tier=AttributeTier.CONDITIONALLY_REQUIRED),
    GenAiAttribute(name="gen_ai.conversation.id", tier=AttributeTier.CONDITIONALLY_REQUIRED),
    # Recommended (Development) — emitted unless cardinality-safe discipline excludes.
    GenAiAttribute(name="gen_ai.usage.input_tokens", tier=AttributeTier.RECOMMENDED_DEVELOPMENT),
    GenAiAttribute(name="gen_ai.usage.output_tokens", tier=AttributeTier.RECOMMENDED_DEVELOPMENT),
    GenAiAttribute(
        name="gen_ai.response.finish_reasons",
        tier=AttributeTier.RECOMMENDED_DEVELOPMENT,
    ),
    GenAiAttribute(name="server.address", tier=AttributeTier.RECOMMENDED_DEVELOPMENT),
    # Opt-In content — default-off per redaction discipline (C-OD-12).
    GenAiAttribute(name="gen_ai.input.messages", tier=AttributeTier.OPT_IN_CONTENT),
    GenAiAttribute(name="gen_ai.output.messages", tier=AttributeTier.OPT_IN_CONTENT),
    GenAiAttribute(name="gen_ai.system_instructions", tier=AttributeTier.OPT_IN_CONTENT),
    GenAiAttribute(name="gen_ai.tool.definitions", tier=AttributeTier.OPT_IN_CONTENT),
    GenAiAttribute(name="gen_ai.tool.call.arguments", tier=AttributeTier.OPT_IN_CONTENT),
    GenAiAttribute(name="gen_ai.tool.call.result", tier=AttributeTier.OPT_IN_CONTENT),
    GenAiAttribute(name="gen_ai.retrieval.documents", tier=AttributeTier.OPT_IN_CONTENT),
    GenAiAttribute(name="gen_ai.retrieval.query.text", tier=AttributeTier.OPT_IN_CONTENT),
)


def span_name(operation: GenAiOperation, model: str) -> str:
    """Resolve the §4.1 span name for a GenAI call at span-emission time.

    Materializes `SPAN_NAME_FORMAT` — the 2-component
    `{gen_ai.operation.name} {gen_ai.request.model}` (acceptance #1). The
    operation is constrained to the §4.2 enum; model is the call-bound
    `gen_ai.request.model` value. `gen_ai.provider.name` is carried as a span
    attribute per §4.3 Required (Stable) tier — not as a span-name component
    per v1.12 canonical-reading amendment.
    """
    return f"{operation.value} {model}"


def attributes_in_tier(tier: AttributeTier) -> tuple[GenAiAttribute, ...]:
    """Return the base-layer attributes classified in `tier` (C-OD-04 §4.3)."""
    return tuple(attr for attr in BASE_LAYER_ATTRIBUTES if attr.tier is tier)


class EventEmission(BaseModel):
    """The harness return-record for a span-event emission (v2.6 acc #9).

    Per the T2 FACTOR-OUT verdict, the OD emission contracts (C-OD-09
    breaker-event, C-OD-25 drift-event) commit the event-emission concept;
    `EventEmission` is the faithful factor-out return-record — a harness
    record, NOT an OTel-SDK type. Frozen → `Eq` over its four fields.

    `emitted_at_span` is a `SpanRef` (an OTel-SDK span handle), so the model
    needs `arbitrary_types_allowed` — Pydantic cannot generate a schema for
    the OTel span handle, and it is carried opaquely.
    """

    model_config = ConfigDict(extra="forbid", frozen=True, arbitrary_types_allowed=True)

    emitted_at_span: SpanRef  #: the span the event was emitted at
    event_name: str  #: the OTel event name
    attribute_count: int  #: count of attributes on the emitted event
    sampled: bool  #: whether the event was sampled (head=1.0 for always-sampled classes)
