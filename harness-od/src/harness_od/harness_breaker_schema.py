"""`harness.breaker.*` 9-attribute canonical schema — U-OD-09.

Implements C-OD-07 §7.1 (nine-attribute schema, v1.32 ADDITIVE amendment over
the v1-canonical seven), §7.2 (quality-of-emission invariants), §7.3 (C9↔C10
subscription contract reference).

`HARNESS_BREAKER_ATTRIBUTES` declares the nine `harness.breaker.*` attribute
names per §7.1. `BreakerScope` / `BreakerState` / `BreakerCause` enumerate the
§7.1 enum-typed attribute value sets. `HarnessBreakerEvent` is the breaker-trip
event record. `emit_breaker_trip_span_event` emits the event at the parent span.

v1.32 (B-19-BREAKER-AMBIENT-ATTRS): re-introduces `harness.breaker.cause` +
`harness.breaker.cooldown_ms` (CP v1.1's dropped ambient 4-attribute set,
re-landed as event attributes rather than ambient state — see
`Spec_Operational_Discipline_v1_32.md` §7.1 change-note). Both are optional,
populated only on a real trip (`to_state = open`). `cause` was originally a
typed slot that was vacuous-today by honest design (no call site in the
runtime could non-speculatively populate any of the four `BreakerCause`
values — see `.harness/b19-breaker-ambient-attrs-redundancy-analysis.md`
§3); `harness_runtime.lifecycle.retry_breaker_fallback._classify_breaker_cause`
(B-38) now populates `RATE_LIMIT`/`AUTH_FAILURE`/`FIVE_XX_STREAK` at all 3
real `record_failure()` call sites, duck-typed on the provider exception's
`.status_code`. `CAPABILITY_SHORTFALL` remains vacuous — it names a
separate, out-of-scope cross-family fallback-exhaustion path, not a
per-step dispatch failure. `cooldown_ms` is real and always populated at a
trip — `cooldown_seconds * 1000`, a static duration the breaker already
carries, not a live remaining-cooldown counter (no clock is introduced).

substrate-anchored-outside-CP: per F-CP-01 Stage 3b alignment, the
`harness.breaker.*` namespace is substrate-anchored at the OD axis rather than
the CP axis. The OD plan exports `harness.breaker.*` to the CP plan as a
CP-consuming seam — the OD → CP exporter direction; edge target = U-CP-54,
contract anchor = C-CP-24 §24.1.C; resolved at Phase 7 sub-phase 7c.

v2.8 (D-3): the v2.5/v2.6 acc #2 "4 Required / 3 Conditional tier
classification" is STRUCK — OD spec C-OD-07 §7.1 declares no tier
classification (the §7.1 table columns are Attribute | Type | Source |
Definition, with no tier column). `HARNESS_BREAKER_ATTRIBUTES` is re-typed
`List<GenAiAttribute>` → `tuple[str, ...]` (the seven §7.1 attribute names).
Per CLAUDE.md I-2 / X-AL-3 there is no spec basis to conform a tier split to.
Note: the U-OD-04 `AttributeTier` enum carries `REQUIRED` + `RECOMMENDED` +
`OPT_IN` members (v1.2-lineage DERIVATIVE names `REQUIRED_STABLE` /
`RECOMMENDED_DEVELOPMENT` / `OPT_IN_CONTENT` retired at OD spec v1.24 §1.2)
and gained `CONDITIONALLY_REQUIRED` at OD spec v1.16 §1.2 (populated with 3
attributes at v1.19 §1.1 per-attribute tier redistribution); the STRIKE
rationale is anchored at the §7.1 absence-of-tier-column at C-OD-07, NOT at
absence of enum members at C-OD-04.

Spec/plan typing nuance: spec §7.1 types `harness.breaker.permanent_fail_repeats`
as `bool`, while the plan signature (v2.1, preserved verbatim through v2.8)
types `HarnessBreakerEvent.permanent_fail_repeats` as `Option<int>`. The plan
signature is execution authority for the materialization and v2.8 explicitly
preserved `HarnessBreakerEvent` with three `Option`-typed fields; this module
follows the plan (`int | None`). Not a contradiction — the field carries the
repeat count; absence (`None`) reads as "not from repeated permanent-fails".

Authority: Implementation_Plan_Operational_Discipline_v2_8.md §3.3.1 U-OD-09
(v2.8 D-3 revision — acc #2 STRUCK, `HARNESS_BREAKER_ATTRIBUTES` re-typed to
`List<string>`, acc #9 re-worded; all other surfaces preserved verbatim from
the v2.5/v2.6 body); Spec_Operational_Discipline_v1_2.md §7 C-OD-07 §7.1 +
§7.2 + §7.3 (preserved verbatim into v1.3 per v1.3 §0.1); ADR-D6 v1.1 §1.2.1.

Depends on: [U-OD-07, U-OD-04] — `SpanRef` / `EventEmission` from
`otel_genai_base` (v2.6 M-1). `HARNESS_BREAKER_ATTRIBUTES` no longer consumes
`GenAiAttribute`, but the `[U-OD-04]` edge is independently justified by
`SpanRef` / `EventEmission` and is preserved.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from harness_od.otel_genai_base import EventEmission, SpanRef

__all__ = [
    "HARNESS_BREAKER_ATTRIBUTES",
    "BreakerCause",
    "BreakerEmissionError",
    "BreakerScope",
    "BreakerState",
    "HarnessBreakerEvent",
    "emit_breaker_trip_span_event",
]


#: The nine `harness.breaker.*` attribute names per §7.1 verbatim (acc #1;
#: v1.32 adds `cause` + `cooldown_ms`).
#: v2.8 (D-3): re-typed `List<GenAiAttribute>` → `tuple[str, ...]` — the §7.1
#: table declares no tier classification, so the attributes are plain names.
HARNESS_BREAKER_ATTRIBUTES: tuple[str, ...] = (
    "harness.breaker.scope",
    "harness.breaker.from_state",
    "harness.breaker.to_state",
    "harness.breaker.trigger_count",
    "harness.breaker.permanent_fail_repeats",
    "harness.breaker.tool_id",
    "harness.breaker.model_version",
    "harness.breaker.cause",
    "harness.breaker.cooldown_ms",
)


class BreakerScope(StrEnum):
    """The 2 `harness.breaker.scope` values (C-OD-07 §7.1).

    `harness.breaker.scope ∈ {per_model, per_provider}` per §7.1 verbatim.
    """

    PER_MODEL = "per_model"
    PER_PROVIDER = "per_provider"


class BreakerState(StrEnum):
    """The 3 breaker states (C-OD-07 §7.1).

    `harness.breaker.from_state` / `harness.breaker.to_state` ∈
    `{closed, open, half_open}` per §7.1 verbatim.
    """

    CLOSED = "closed"
    HALF_OPEN = "half_open"
    OPEN = "open"


class BreakerCause(StrEnum):
    """The 4 `harness.breaker.cause` values (C-OD-07 §7.1, v1.32 NEW).

    `harness.breaker.cause ∈ {rate_limit, auth_failure, 5xx_streak,
    capability_shortfall}` per `Spec_Control_Plane_v1_2.md` §"Attribute set
    reconciliation" line 72 verbatim (the original CP-side ambient-attribute
    domain, re-declared here as the OD-canonical event-attribute domain).

    Previously vacuous-today by honest design (no call site in the
    runtime could non-speculatively populate any of these four values —
    see `.harness/b19-breaker-ambient-attrs-redundancy-analysis.md` §3).
    `harness_runtime.lifecycle.retry_breaker_fallback._classify_breaker_cause`
    (B-38) now populates `RATE_LIMIT` / `AUTH_FAILURE` / `FIVE_XX_STREAK` at
    all 3 real `record_failure()` call sites, duck-typed on the provider
    exception's `.status_code`. `CAPABILITY_SHORTFALL` remains vacuous — it
    names a separate, out-of-scope cross-family fallback-exhaustion path,
    not a per-step dispatch failure.

    `FIVE_XX_STREAK` (B-42 clarification): the name implies a verified
    N-consecutive-5xx streak, but the classifier tags this value from a
    single terminal 5xx exception at the trip call site — there is no
    per-cause failure-history tracking in `BreakerStateMachine` today. A
    true consecutive-streak count is a follow-on refinement, not required
    for the attribute to be non-vacuous (C-OD-07 §7.1 only requires "the
    classified trip-cause, when known" — it does not mandate streak
    verification). The enum *value* (`"5xx_streak"`) is spec-committed at
    OD v1.32 §7.1 + CP v1.1 and is unchanged; only this docstring's
    description of how it's derived is being made precise.
    """

    RATE_LIMIT = "rate_limit"
    AUTH_FAILURE = "auth_failure"
    FIVE_XX_STREAK = "5xx_streak"
    CAPABILITY_SHORTFALL = "capability_shortfall"


class HarnessBreakerEvent(BaseModel):
    """The breaker-trip event record (C-OD-07 §7.1, v1.32 nine-attribute).

    Frozen → `Eq`. Carries the nine §7.1 attributes: four non-optional
    (`scope`, `from_state`, `to_state`, `trigger_count`) and five optional
    (`permanent_fail_repeats`, `tool_id`, `model_version`, `cause`,
    `cooldown_ms`) per the §7.1 Definition-column conditional reading.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    #: `harness.breaker.scope` — the breaker scope.
    scope: BreakerScope
    #: `harness.breaker.from_state` — source state.
    from_state: BreakerState
    #: `harness.breaker.to_state` — destination state.
    to_state: BreakerState
    #: `harness.breaker.trigger_count` — consecutive failures that tripped.
    trigger_count: int
    #: `harness.breaker.permanent_fail_repeats` — repeated-permanent-fail count;
    #: `None` when the trip is not from repeated C5 permanent-fail-exits.
    permanent_fail_repeats: int | None = None
    #: `harness.breaker.tool_id` — set when scope correlates with a tool (§7.1).
    tool_id: str | None = None
    #: `harness.breaker.model_version` — set when available (§7.1).
    model_version: str | None = None
    #: `harness.breaker.cause` — classified trip cause (v1.32 NEW). Vacuous
    #: today: no runtime call site can non-speculatively populate this; always
    #: `None` until a follow-on classifier arc supplies real signal.
    cause: BreakerCause | None = None
    #: `harness.breaker.cooldown_ms` — the cooldown *duration* set for this
    #: trip (v1.32 NEW), in milliseconds. `None` on non-trip transitions
    #: (`half_open -> closed`, `open -> half_open`).
    cooldown_ms: int | None = None


class BreakerEmissionError(Exception):
    """Raised when a breaker-trip event cannot be emitted (C-OD-07 §7.2).

    The Python materialization of the `Result<EventEmission, BreakerEmissionError>`
    error arm of `emit_breaker_trip_span_event` — stack is Pydantic v2 + stdlib,
    no `Result` framework pull (CLAUDE.md §3.2 / I-6).
    """


#: The four non-optional `HarnessBreakerEvent` attributes — the §7.2
#: presence-enforced set (acc #9, v2.8 D-3 re-worded).
_NON_OPTIONAL_ATTRIBUTES: tuple[str, ...] = (
    "scope",
    "from_state",
    "to_state",
    "trigger_count",
)


def emit_breaker_trip_span_event(
    parent_span_ref: SpanRef,
    event: HarnessBreakerEvent,
) -> EventEmission:
    """Emit a `breaker.tripped` event at the parent span (C-OD-07 §7.1 / §7.2).

    Returns an `EventEmission` recording the emission. Raises
    `BreakerEmissionError` (the `Err` arm) if any of the four non-optional
    `HarnessBreakerEvent` attributes — `scope`, `from_state`, `to_state`,
    `trigger_count` — is missing (acc #9, v2.8 D-3). The three optional
    attributes (`permanent_fail_repeats`, `tool_id`, `model_version`) are
    populated when applicable per the §7.1 Definition-column conditional
    language.

    `breaker.tripped` events are always-sampled at all cells per §7.2 — the
    emitted `EventEmission.sampled` is `True` (composes with the U-OD-11
    always-sampled set). `parent_span_ref` and the return resolve to the
    U-OD-04 OTel-handle alias family; no `Span*` type is materialized here —
    `parent_span_ref` is the real `opentelemetry.trace.Span` handle and this
    function calls its `.add_event(...)` directly (matching
    `alignment_floor_drift_detection.emit_drift_event`'s established
    pattern), so `EventEmission` is a bookkeeping return-record ON TOP OF a
    real emission, not a substitute for one (out-of-family Codex review at
    `B-38`'s PR caught that this call was previously missing).
    """
    for attribute_name in _NON_OPTIONAL_ATTRIBUTES:
        if getattr(event, attribute_name, None) is None:
            raise BreakerEmissionError(
                f"breaker.tripped emission rejected: required attribute "
                f"'{attribute_name}' is missing (C-OD-07 §7.2)"
            )
    populated_attribute_count = sum(
        1
        for attribute_name in (
            "scope",
            "from_state",
            "to_state",
            "trigger_count",
            "permanent_fail_repeats",
            "tool_id",
            "model_version",
            "cause",
            "cooldown_ms",
        )
        if getattr(event, attribute_name) is not None
    )
    attributes: dict[str, str | int] = {
        "harness.breaker.scope": event.scope.value,
        "harness.breaker.from_state": event.from_state.value,
        "harness.breaker.to_state": event.to_state.value,
        "harness.breaker.trigger_count": event.trigger_count,
    }
    if event.permanent_fail_repeats is not None:
        attributes["harness.breaker.permanent_fail_repeats"] = event.permanent_fail_repeats
    if event.tool_id is not None:
        attributes["harness.breaker.tool_id"] = event.tool_id
    if event.model_version is not None:
        attributes["harness.breaker.model_version"] = event.model_version
    if event.cause is not None:
        attributes["harness.breaker.cause"] = event.cause.value
    if event.cooldown_ms is not None:
        attributes["harness.breaker.cooldown_ms"] = event.cooldown_ms
    parent_span_ref.add_event(name="breaker.tripped", attributes=attributes)
    return EventEmission(
        emitted_at_span=parent_span_ref,
        event_name="breaker.tripped",
        attribute_count=populated_attribute_count,
        sampled=True,  # always-sampled per §7.2 / C-OD-09
    )
