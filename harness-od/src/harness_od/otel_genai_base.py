"""OTel GenAI semconv 1.41.0 base-layer attributes — U-OD-04.

Implements C-OD-04 §4.1 (span name format), §4.2 (operations enum), §4.3
(attribute tiers), §4.4 (hierarchy correlation), §4.5 (base metric).

The base layer is the cross-vendor-stable substrate over which the 15 OD
specialization-layer namespaces (C-OD-05) compose — specialization namespaces
add attributes but never replace base-layer attributes (acceptance #7). Every
attribute name, operation value, tier name, the span-name format, and the base
metric name is the OTel GenAI semantic conventions 1.41.0 surface, transcribed
verbatim from the spec §4 tables.

Authority: Implementation_Plan_Operational_Discipline_v2_5.md §3.2.1 U-OD-04
(v2.5 conformance revision — absorbs Tension 004 / the §4A verbatim-divergence
cluster: 3-component span name, 7-operation enum, 3-tier `AttributeTier`,
`gen_ai.client.operation.duration` base metric); Spec_Operational_Discipline_v1_2.md
§4 C-OD-04 (preserved verbatim into v1.3 per v1.3 §0.1); ADR-D6 v1.1 §1.2
base-layer block (OTel GenAI semconv 1.41.0 [HIGH] cross-vendor floor).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class GenAiOperation(StrEnum):
    """The 7 `gen_ai.operation.name` values (C-OD-04 §4.2, verbatim).

    Member string values are the §4.2 enumeration verbatim:
    `{chat, text_completion, embeddings, generate_content, create_agent,
    invoke_agent, execute_tool}`.
    """

    CHAT = "chat"
    TEXT_COMPLETION = "text_completion"
    EMBEDDINGS = "embeddings"
    GENERATE_CONTENT = "generate_content"
    CREATE_AGENT = "create_agent"
    INVOKE_AGENT = "invoke_agent"
    EXECUTE_TOOL = "execute_tool"


class AttributeTier(StrEnum):
    """The 3 attribute tiers (C-OD-04 §4.3, verbatim).

    Member string values are the §4.3 table "Tier" column verbatim. Emission
    posture per tier: Required (Stable) always emitted; Recommended
    (Development) emitted unless cardinality-safe-attribute discipline excludes
    (C-OD-11); Opt-In content default-off per redaction discipline (C-OD-12).
    """

    REQUIRED_STABLE = "Required (Stable)"
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
SPAN_NAME_FORMAT: str = "{gen_ai.operation.name} {gen_ai.provider.name} {gen_ai.request.model}"

#: §4.5 base metric name, verbatim — a histogram with cardinality control per
#: C-OD-11 (acceptance #6).
BASE_METRIC_NAME: str = "gen_ai.client.operation.duration"

#: §4.4 hierarchy-correlation key — the correlation attribute for the
#: `invoke_agent` / `chat` / `execute_tool` span hierarchy. Span-attribute only,
#: never a metric dimension, per cardinality-safe discipline (C-OD-11).
HIERARCHY_CORRELATION_KEY: str = "gen_ai.conversation.id"

#: §4.3 base-layer attribute set with per-attribute tier classification,
#: transcribed verbatim from the §4.3 table (acceptance #4). 3 Required +
#: 6 Recommended + 8 Opt-In = 17 attributes.
BASE_LAYER_ATTRIBUTES: tuple[GenAiAttribute, ...] = (
    # Required (Stable) — always emitted.
    GenAiAttribute(name="gen_ai.operation.name", tier=AttributeTier.REQUIRED_STABLE),
    GenAiAttribute(name="gen_ai.provider.name", tier=AttributeTier.REQUIRED_STABLE),
    GenAiAttribute(name="gen_ai.request.model", tier=AttributeTier.REQUIRED_STABLE),
    # Recommended (Development) — emitted unless cardinality-safe discipline excludes.
    GenAiAttribute(name="gen_ai.usage.input_tokens", tier=AttributeTier.RECOMMENDED_DEVELOPMENT),
    GenAiAttribute(name="gen_ai.usage.output_tokens", tier=AttributeTier.RECOMMENDED_DEVELOPMENT),
    GenAiAttribute(
        name="gen_ai.response.finish_reasons",
        tier=AttributeTier.RECOMMENDED_DEVELOPMENT,
    ),
    GenAiAttribute(name="server.address", tier=AttributeTier.RECOMMENDED_DEVELOPMENT),
    GenAiAttribute(name="server.port", tier=AttributeTier.RECOMMENDED_DEVELOPMENT),
    GenAiAttribute(name="gen_ai.conversation.id", tier=AttributeTier.RECOMMENDED_DEVELOPMENT),
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


def span_name(operation: GenAiOperation, provider: str, model: str) -> str:
    """Resolve the §4.1 span name for a GenAI call at span-emission time.

    Materializes `SPAN_NAME_FORMAT` — the 3-component
    `{gen_ai.operation.name} {gen_ai.provider.name} {gen_ai.request.model}`
    (acceptance #1). The operation is constrained to the §4.2 enum; provider and
    model are the call-bound `gen_ai.provider.name` / `gen_ai.request.model`
    values.
    """
    return f"{operation.value} {provider} {model}"


def attributes_in_tier(tier: AttributeTier) -> tuple[GenAiAttribute, ...]:
    """Return the base-layer attributes classified in `tier` (C-OD-04 §4.3)."""
    return tuple(attr for attr in BASE_LAYER_ATTRIBUTES if attr.tier is tier)
