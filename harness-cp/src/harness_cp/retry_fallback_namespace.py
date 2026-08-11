"""`fallback.*` + `harness.breaker.*` + `retry.*` namespace schemas — U-CP-07.

Implements C-CP-03 §3.5 (the fallback / harness-breaker / retry span-attribute
namespace declarations + the v1.3 retry.* extension to a 6-attribute child-span
schema and a 3-field `retry.attempt` parent-event schema).

Declares `FallbackAttributeSchema` / `FALLBACK_NAMESPACE_SCHEMA` (9 entries),
`HarnessBreakerAttributeSchema` / `HARNESS_BREAKER_NAMESPACE_SCHEMA` (9),
`RetryAttributeSchema` / `RETRY_NAMESPACE_SCHEMA` (6), `RetryAttemptEventField`
/ `RETRY_ATTEMPT_EVENT_SCHEMA` (3), and the `RetryCause` enum (5).

Also declares `RetryWireRegisterEntry` / `RETRY_WIRE_REGISTER` (7) — the
`retry.*` wire keys declared at Runtime §14.6/§14.9 rather than at C-CP-03 §3.5
— and `RETRY_SPAN_AND_EVENT_NAMES` (3). Register row `B-126`.

**Substitution-mechanism note.** `harness.breaker.*` is substrate-anchored at
the `c9-reliability-recovery` skill; canonical schema at OD C-OD-07 §7.1 — this
unit emits the CP-side composition surface without claiming canonical
authorship. `retry.*` is substrate-anchored across `c9-reliability-recovery`,
`c5-validation-contract`, and ADR-D1 v1.2 §1.1.1 per ADR-D6 v1.2 §1.2.2.

**Partial-land — acceptance #7 struck.** U-CP-07 acceptance #7 (the runtime
dual-emission discipline — emit both the parent `retry.attempt` event and the
retry-attempt child span, with `parent_span_id`-linked child topology) is a
behavioural contract over an OTel span emitter, which does not exist at
sub-phase 7b L0. Per the halt-route-split-AC pattern, #7 + its 5 emission tests
are struck and routed to a downstream emitter unit. Defect record:
`.harness/class_1_tension_u_cp_07_dual_emission.md`. Acceptance #1–#6 — the
schema declarations — are landed in full below.

Authority: Implementation_Plan_Control_Plane_v2_3.md §2.1 U-CP-07 (v2.3
retry.* 6-attribute + 3-field extension; v2.6 §0.11 `[U-CP-00b]` edge-add);
Spec_Control_Plane_v1_3.md §3 C-CP-03 §3.5; ADR-D6 v1.2 §1.2.2.1 + §1.2.2.2;
OD C-OD-07 §7.1 (`harness.breaker.*` canonical schema).
"""

from __future__ import annotations

from enum import StrEnum

from harness_core import AttributeValueType, Cardinality
from pydantic import BaseModel, ConfigDict


class RetryCause(StrEnum):
    """The 5-value internal retry-decision branching enum (C-CP-03 §3.5).

    Distinct from the `retry.cause_attribution` span attribute (the broader
    open-set C5 catalog) — `RetryCause` governs internal retry control flow
    and is consumed at U-CP-48 cause-attribution-conditioned branching.
    """

    TRANSIENT_PROVIDER_ERROR = "transient_provider_error"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    CAPABILITY_SHORTFALL = "capability_shortfall"
    VALIDATOR_FAIL_TRANSIENT = "validator_fail_transient"


class FallbackAttributeSchema(BaseModel):
    """One `fallback.*` span attribute (C-CP-03 §3.5)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    attribute_name: str
    value_type: AttributeValueType
    cardinality: Cardinality


class HarnessBreakerAttributeSchema(BaseModel):
    """One `harness.breaker.*` span attribute (C-CP-03 §3.5 + OD C-OD-07 §7.1)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    attribute_name: str
    value_type: AttributeValueType
    cardinality: Cardinality
    source_authority: str
    """Per-attribute substrate-authority annotation — substrate-anchored
    outside CP at `c9-reliability-recovery`."""


class RetryAttributeSchema(BaseModel):
    """One `retry.*` child-span attribute (C-CP-03 §3.5 + ADR-D6 v1.2 §1.2.2.1)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    attribute_name: str
    value_type: AttributeValueType
    cardinality: Cardinality
    source_authority: str
    """Per-attribute substrate-authority annotation (v2.3 amendment)."""


class RetryAttemptEventField(BaseModel):
    """One field of the parent-span `retry.attempt` event (ADR-D6 v1.2 §1.2.2.2)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    field_name: str
    value_type: AttributeValueType
    optional: bool
    """`true` for `parent.next_delay_ms` — omitted at the retry-budget-exit
    boundary (`parent.attempts_remaining == 0`)."""


# --- fallback.* namespace (spec C-CP-03 §3.5 — 9 attributes) ----------------

_C = Cardinality

FALLBACK_NAMESPACE_SCHEMA: tuple[FallbackAttributeSchema, ...] = tuple(
    FallbackAttributeSchema(attribute_name=name, value_type=vt, cardinality=card)
    for name, vt, card in (
        ("fallback.layer", AttributeValueType.ENUM_REF, _C.LOW),
        ("fallback.candidate_chosen", AttributeValueType.STRING, _C.MEDIUM),
        ("fallback.candidates_skipped", AttributeValueType.STRING, _C.MEDIUM),
        ("fallback.cause", AttributeValueType.ENUM_REF, _C.LOW),
        ("fallback.cross_family", AttributeValueType.BOOL, _C.LOW),
        ("fallback.cross_family_triggered", AttributeValueType.BOOL, _C.LOW),
        ("fallback.exhausted", AttributeValueType.BOOL, _C.LOW),
        ("fallback.depth", AttributeValueType.INT, _C.MEDIUM),
        ("fallback.cache_state_lost", AttributeValueType.BOOL, _C.LOW),
    )
)
"""The 9 `fallback.*` attributes per C-CP-03 §3.5 verbatim."""


# --- harness.breaker.* namespace (spec C-CP-03 §3.5 + OD C-OD-07 §7.1 — 9) --
#
# B-20 (2026-07-14): the 7 pre-existing entries now carry OD's canonical §7.1
# names verbatim (`scope` / `from_state` / `to_state` / `trigger_count` /
# `permanent_fail_repeats` / `tool_id` / `model_version` —
# `harness_od.harness_breaker_schema.HARNESS_BREAKER_ATTRIBUTES`), fixing a
# pre-existing name drift that this module's own
# `verify_harness_breaker_namespace_inversion()` cardinality check could not
# catch (it compares COUNT only, not names). `harness.breaker.state` is split
# into `from_state` + `to_state`; `harness.breaker.id` /
# `trip_window_seconds` / `fail_count_in_window` / `fail_threshold` are
# dropped (no OD equivalent); `harness.breaker.trip_count` is renamed
# `trigger_count`; `tool_id` + `model_version` are newly added (OD attributes
# CP previously had no entry for at all). The 2 v1.32 entries (`cause` /
# `cooldown_ms`) were already correct and are unchanged.

_BREAKER_AUTHORITY = "c9-reliability-recovery SKILL.md"

HARNESS_BREAKER_NAMESPACE_SCHEMA: tuple[HarnessBreakerAttributeSchema, ...] = tuple(
    HarnessBreakerAttributeSchema(
        attribute_name=name,
        value_type=vt,
        cardinality=card,
        source_authority=_BREAKER_AUTHORITY,
    )
    for name, vt, card in (
        ("harness.breaker.scope", AttributeValueType.ENUM_REF, _C.LOW),
        ("harness.breaker.from_state", AttributeValueType.ENUM_REF, _C.LOW),
        ("harness.breaker.to_state", AttributeValueType.ENUM_REF, _C.LOW),
        ("harness.breaker.trigger_count", AttributeValueType.INT, _C.MEDIUM),
        ("harness.breaker.permanent_fail_repeats", AttributeValueType.INT, _C.LOW),
        ("harness.breaker.tool_id", AttributeValueType.STRING, _C.MEDIUM),
        ("harness.breaker.model_version", AttributeValueType.STRING, _C.MEDIUM),
        ("harness.breaker.cause", AttributeValueType.ENUM_REF, _C.LOW),
        ("harness.breaker.cooldown_ms", AttributeValueType.INT, _C.LOW),
    )
)
"""The 9 `harness.breaker.*` attributes per C-CP-03 §3.5 + OD C-OD-07 §7.1
canonical schema, byte-exact against `HARNESS_BREAKER_ATTRIBUTES` (B-20 fix,
2026-07-14) — each carrying `source_authority`."""


# --- retry.* namespace (spec C-CP-03 §3.5 + ADR-D6 v1.2 §1.2.2.1 — 6) -------

RETRY_NAMESPACE_SCHEMA: tuple[RetryAttributeSchema, ...] = (
    RetryAttributeSchema(
        attribute_name="retry.attempt_number",
        value_type=AttributeValueType.INT,
        cardinality=_C.MEDIUM,
        source_authority="c9-reliability-recovery SKILL.md",
    ),
    RetryAttributeSchema(
        attribute_name="retry.original_span_id",
        value_type=AttributeValueType.STRING,
        cardinality=_C.PER_REQUEST,
        source_authority="ADR-D1 v1.2 §1.1.2.2 (F2 state-ledger entry shape)",
    ),
    RetryAttributeSchema(
        attribute_name="retry.delay_ms",
        value_type=AttributeValueType.INT,
        cardinality=_C.MEDIUM,
        source_authority="c9-reliability-recovery SKILL.md",
    ),
    RetryAttributeSchema(
        attribute_name="retry.cause_attribution",
        value_type=AttributeValueType.STRING,
        cardinality=_C.MEDIUM,
        source_authority="c5-validation-contract SKILL.md s14 §7.5(a)",
    ),
    RetryAttributeSchema(
        attribute_name="retry.fail_class",
        value_type=AttributeValueType.ENUM_REF,
        cardinality=_C.LOW,
        source_authority="c5-validation-contract SKILL.md s14 §7.5(d)",
    ),
    RetryAttributeSchema(
        attribute_name="engine.replay_disposition",
        value_type=AttributeValueType.ENUM_REF,
        cardinality=_C.LOW,
        source_authority="ADR-D1 v1.2 §1.1.1 (inherits parent operation value)",
    ),
)
"""The 6 `retry.*` child-span attributes per C-CP-03 §3.5 + ADR-D6 v1.2
§1.2.2.1 verbatim (v2.3 amendment from 4)."""


# --- retry.attempt parent-event schema (ADR-D6 v1.2 §1.2.2.2 — 3 fields) ----

RETRY_ATTEMPT_EVENT_SCHEMA: tuple[RetryAttemptEventField, ...] = (
    RetryAttemptEventField(
        field_name="parent.attempt_count",
        value_type=AttributeValueType.INT,
        optional=False,
    ),
    RetryAttemptEventField(
        field_name="parent.attempts_remaining",
        value_type=AttributeValueType.INT,
        optional=False,
    ),
    RetryAttemptEventField(
        field_name="parent.next_delay_ms",
        value_type=AttributeValueType.INT,
        optional=True,
    ),
)
"""The 3 `retry.attempt` parent-event fields per ADR-D6 v1.2 §1.2.2.2 verbatim
— `parent.next_delay_ms` is optional (omitted at retry-budget-exit boundary)."""


# --- retry.* wire surface beyond C-CP-03 §3.5 (register, NOT a cap) — B-126 --


class RetryWireRegisterEntry(BaseModel):
    """One `retry.*`-prefixed span attribute NOT declared at C-CP-03 §3.5."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    attribute_name: str
    declaring_authority: str
    """The clause that authorizes the key — a Runtime-spec normative step, a
    binding term, or a telemetry-volume discretion bullet."""
    binding: bool
    """`True` when the authority names the key and MANDATES it; `False` for a
    key riding pure implementation discretion."""
    emitted: bool
    """`False` for a key its authority mandates that no producer sets."""


RETRY_WIRE_REGISTER: tuple[RetryWireRegisterEntry, ...] = (
    RetryWireRegisterEntry(
        attribute_name="retry.skipped.reason",
        declaring_authority="Runtime §14.6 step 4 (Spec_Harness_Runtime_v1.md:4217)",
        binding=True,
        emitted=True,
    ),
    RetryWireRegisterEntry(
        attribute_name="retry.skipped.candidate",
        declaring_authority="Runtime §14.6 discretion bullet (Spec_Harness_Runtime_v1.md:4279)",
        binding=False,
        emitted=True,
    ),
    RetryWireRegisterEntry(
        attribute_name="retry.breaker_waived.reason",
        declaring_authority="Runtime §14.6.3 term t1+t2 (Spec_Harness_Runtime_v1.md:4364)",
        binding=True,
        emitted=True,
    ),
    RetryWireRegisterEntry(
        attribute_name="retry.breaker_waived.candidate",
        declaring_authority="Runtime §14.6.3 term t1+t2 (Spec_Harness_Runtime_v1.md:4364)",
        binding=True,
        emitted=True,
    ),
    RetryWireRegisterEntry(
        attribute_name="retry.terminal",
        declaring_authority="Runtime §14.6 steps (Spec_Harness_Runtime_v1.md:4227-4230)"
        " + §14.9 steps (:5684-5687)",
        binding=True,
        emitted=True,
    ),
)
"""The `retry.*` wire keys that C-CP-03 §3.5 does NOT declare — register row
`B-126`.

**Why this exists.** `retry.*` is declared at TWO contract venues, not one.
C-CP-03 §3.5 declares the 6-attribute child-span schema above (5 of them
`retry.`-prefixed; `engine.replay_disposition` is the sixth). Runtime §14.6 and
§14.9 independently name five MORE `retry.`-prefixed keys at their own step
bullets and binding terms. The namespace's wire surface is therefore the union
of two contracts, and the C-CP-24 §24.1 export manifest counts only the first.

**This is a REGISTER, not a cap.** The Runtime discretion bullets at
`Spec_Harness_Runtime_v1.md:4279` and `:5729` state NO upper bound — the lane is
intentionally unbounded, so a future producer MAY add a key. What it may not do
is add one *invisibly*: the drift test over this tuple fails until the new key
is registered here with its authorizing clause. Four of the five rows are
`binding=True`, which is the finding B-126 was filed to surface — the surface is
mostly *mandated elsewhere*, not discretionary.

**Two rows retired at the B-145 GAP-1 spec leg (Runtime v1.115), not wired.**
`retry.backoff_ms` and `retry.cause_class` were carried here `emitted=False` as
mandated-but-unwired (`B-145`). Grounding found both are the RETIRED v1.2-era
names the CP §3.5 v1.3 amendment replaced (`retry.delay_ms` /
`retry.cause_attribution` — both emitted by both producers), and Runtime v1.115
aligned its four step-bullet mentions to the canonical names — so the two-venue
union no longer contains the aliases and the rows are REMOVED rather than
flipped `emitted=True`. Wiring them as-written would have put duplicate keys on
the wire for every retry attempt. The prior "do NOT drop these rows" guard
bound only while the Runtime bullets still named the keys.

**NOT ingested into the §24.1 count.** These keys are deliberately absent from
`CP_NAMESPACE_EXPORT_MANIFEST`'s `retry.*` `attribute_count`, which reports the
§24.1-declared subset. See that module's own note.
"""

RETRY_SPAN_AND_EVENT_NAMES: tuple[str, ...] = (
    "retry.attempt",
    "retry.attempt.first",
    "retry.skipped",
)
"""The `retry.`-prefixed SPAN / EVENT / sampling-key NAMES — deliberately kept
apart from the attribute registers above, because a name is not a wire attribute
and must not be counted as one.

`retry.attempt` is the ADR-D6 v1.2 §1.2.2.2 parent event + its dual-emission
child span; `retry.attempt.first` is the OD C-OD-10 §10.1 base-rate key;
`retry.skipped` is the Runtime §14.6 breaker-open skip event that CARRIES the
two `retry.skipped.*` attributes registered above.
"""
