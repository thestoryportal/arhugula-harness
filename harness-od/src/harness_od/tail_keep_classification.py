"""§10.2 tail-keep-on-classification trigger predicate.

Closes H_T-OD-3 PARTIAL → RETIRE-READY gate (a) per OD spec v1.2 §9.1
production-time tail-based-sampling mandate + §10.2 3-trigger preservation
table + §9.3 implementer-discretion clause on the algorithm.

**The §10.2 classification triggers** (canonical at
`harness-od/src/harness_od/base_rate_set_and_envelope.py:TAIL_KEEP_RULES`):

| Trigger ID | Concrete carrier | Source |
|---|---|---|
| `validator.fail.permanent` | span attribute `validator.fail.permanence` == `"permanent"` | C-CP-21 §21.6 + `validator_fail_taxonomy.py:149` |
| `sandbox.violation` | span name == `"sandbox.violation"` OR any span EVENT name == `"sandbox.violation"` | C-AS-15 §15.4 + `sandbox_attribute_schema.py:_VIOLATION` |
| `breaker.tripped` | span name == `"breaker.tripped"` OR any span EVENT name == `"breaker.tripped"` | C-CP-03 §3.5 + `lifecycle_event_span_map.py:91` |

The trigger-ID strings at `TAIL_KEEP_RULES` are the conceptual classification
labels (per §10.2 row 1 column "Classification trigger"); the actual carriers
at the OTel span are heterogeneous — one is an attribute value match
(`validator.fail.permanence=permanent`), the other two are span-name OR
span-EVENT-name matches. This helper unifies the three under a single
predicate over `ReadableSpan`.

**Event-name arm (register row `B-123`; primary authority OD spec v1.2
§C-OD-10 §10.2, lines 582-584, PRESERVED VERBATIM through the current head —
the contract table reads "Parent + sibling spans of any `sandbox.violation`
EVENT preserved" / "...`breaker.tripped` EVENT preserved," i.e. the contract
already says event, not span name).** The real `breaker.tripped` producer
(`harness_breaker_schema.py:282`) emits it as a span EVENT on a carrier span
named `harness.runtime.retry_breaker_fallback`, which is itself neither a
§9.2 nor a §10.2 member — so the pre-`B-123` name-only predicate returned
False on that carrier, the per-trace keep flag was never set, and the trip's
entire sibling tree dropped at root close (`B-133` positive control,
2026-08-08). `SECTION_10_2_EVENT_TRIGGER_NAMES` closes that gap by scanning
`span.events` for either trigger name after the existing name/attribute
checks fail. This is a conformance repair to already-cleared contract text,
not a design extension; the `sandbox.violation` producer
(`runtime_tool_dispatcher.py:725`) emits a real span (not an event) on every
live path, so the widening is inert-but-harmless for that row today and
exists for contract completeness + future-producer safety. OD spec v1.39
§1 AMENDS §C-OD-09 §9.2.1 term 3 in the SAME PR as this module, retracting
v1.38 term 3's explicit decline to widen ("the trigger predicate is NOT
widened to events — that half is `B-123`") and requiring the predicate to
resolve both shapes; `B-123` CLOSES at this leg's implementation.

`is_classification_trigger(span)` returns True iff the span carries any of
the three §10.2 triggers, by span name/attribute OR (for the two event-
shaped triggers) by span EVENT name. Pure function; no side effects;
tolerant of missing attribute bag AND of zero/absent events (returns False
rather than raising).

Pairs with `TailKeepSpanProcessor` at `tail_keep_span_processor.py` (the
consumer — buffers per-trace and forwards-or-drops on root close).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from opentelemetry.sdk.trace import Event, ReadableSpan

__all__ = [
    "BREAKER_TRIPPED_SPAN_NAME",
    "SANDBOX_VIOLATION_SPAN_NAME",
    "SECTION_10_2_EVENT_TRIGGER_NAMES",
    "SUBAGENT_RESULT_STATUS_ATTR",
    "SUBAGENT_RESULT_STATUS_FAILED_VALUE",
    "SUBAGENT_SPAN_NAME",
    "VALIDATOR_FAIL_PERMANENCE_ATTR",
    "VALIDATOR_FAIL_PERMANENCE_PERMANENT_VALUE",
    "is_classification_trigger",
]


#: Span name carrying the §10.2 trigger row 2 (`sandbox.violation`).
SANDBOX_VIOLATION_SPAN_NAME: str = "sandbox.violation"

#: Span name carrying the §10.2 trigger row 3 (`breaker.tripped`).
BREAKER_TRIPPED_SPAN_NAME: str = "breaker.tripped"

#: The two §10.2 trigger names as they may ALSO appear as a span EVENT name
#: rather than a span name (register row `B-123`). Derived from the two
#: name constants above — not re-literalled — so a future rename of either
#: reaches the event arm by construction; see `test_ac8_...` for the
#: structural witness pinning this.
SECTION_10_2_EVENT_TRIGGER_NAMES: frozenset[str] = frozenset(
    {SANDBOX_VIOLATION_SPAN_NAME, BREAKER_TRIPPED_SPAN_NAME}
)

#: Span attribute key carrying the §10.2 trigger row 1
#: (`validator.fail.permanent` classification ↔ `validator.fail.permanence`
#: attribute name per CP spec C-CP-21 §21.6 + `validator_fail_taxonomy.py`).
VALIDATOR_FAIL_PERMANENCE_ATTR: str = "validator.fail.permanence"

#: Attribute value flagging the row-1 trigger (per validator_fail_permanence()
#: derivation function at harness-cp/src/harness_cp/validator_fail_taxonomy.py).
VALIDATOR_FAIL_PERMANENCE_PERMANENT_VALUE: str = "permanent"

#: Span name carrying the §14.3 subagent tail-keep-on-failure row (`subagent.span`,
#: the real producer-emitted name per harness-runtime sub_agent_dispatch.py).
SUBAGENT_SPAN_NAME: str = "subagent.span"

#: Span attribute key carrying the subagent result status (CP C-CP-14 §14.2/§14.3;
#: ingested verbatim per the D6 namespace-ingestion pattern, like the validator attr above).
SUBAGENT_RESULT_STATUS_ATTR: str = "subagent.result_status"

#: Attribute value flagging the §14.3 subagent-failure tail-keep
#: (`SubAgentResultStatus.FAILED` value per CP topology_subagent_namespace.py; the runtime
#: producer emits the lowercase `"failed"` at sub_agent_dispatch.py).
SUBAGENT_RESULT_STATUS_FAILED_VALUE: str = "failed"


def is_classification_trigger(span: ReadableSpan, *, events: Sequence[Event] | None = None) -> bool:
    """Return True iff `span` carries a tail-keep classification trigger: the 3
    §10.2 triggers (sandbox.violation / breaker.tripped / validator.fail-permanent)
    OR the §14.3 subagent-failure tail-keep.

    Pure predicate over an OTel `ReadableSpan`. Tolerant of missing
    attribute bag AND of zero/absent span events (returns False instead of
    raising). Used at the `TailKeepSpanProcessor` per-span inspection step
    to flag a trace for preservation on root close.

    Order of checks: span-name matches first (cheapest — single
    string-equality), then attribute lookup, then — only if none of those
    fired — a scan for either §10.2 event-shaped trigger name (register row
    `B-123`) over `events` if supplied, else over a freshly-read
    `span.events`. The event scan is LAST because it is the most expensive
    check (`span.events` is an OTel property that takes a lock and copies a
    deque on every access, per `_carries_always_sampled_event`'s docstring at
    `tail_keep_span_processor.py`) and because every existing name-matching
    span (the common case for the two event-shaped triggers' name-carried
    siblings) must never pay for it. This ordering is a NORMATIVE term (OD
    spec v1.39 §1 term 3), not a preference.

    `events` — an OPTIONAL pre-read snapshot (out-of-family Codex [P2],
    register row `B-123` fix-forward). `TailKeepSpanProcessor.on_end` calls
    this function AND `_carries_always_sampled_event` against the SAME span
    in the SAME `on_end` invocation; without a shared snapshot each function
    would independently pay `span.events`'s lock-acquire + deque-copy cost,
    doubling it for every ordinary (non-name-matched) span reaching the event
    checks, including zero-event ones. `on_end` reads `span.events` exactly
    ONCE and threads that snapshot into both call sites via this parameter.
    `events=None` (the default) means "read it yourself" — every OTHER
    caller, and every pre-existing test, sees byte-identical behaviour to a
    fresh `span.events` read; when a snapshot IS supplied, this function
    performs ZERO reads of the property. Total either way: an empty or
    absent (`None`-defaulted but genuinely empty) snapshot returns False
    rather than raising, mirroring the `attrs is None` tolerance above.
    """
    name = span.name
    if name == SANDBOX_VIOLATION_SPAN_NAME:
        return True
    if name == BREAKER_TRIPPED_SPAN_NAME:
        return True
    attrs = span.attributes
    if attrs is not None:
        if attrs.get(VALIDATOR_FAIL_PERMANENCE_ATTR) == VALIDATOR_FAIL_PERMANENCE_PERMANENT_VALUE:
            return True
        # §14.3 (CP C-CP-14 `MULTI_AGENT_SPAN_SAMPLING`): a `subagent.span` is BASE_RATE
        # head-sampled with TAIL-KEEP ON FAILURE. Before B-TAIL this was crudely over-satisfied
        # by name-only always-sampling of every `subagent.span`; with the §9.2-root-only
        # refinement a non-root `subagent.span` now buffers, so its failure must trigger trace
        # preservation here (out-of-family Codex — else a failed nested subagent span drops,
        # regressing the §14.3 observability contract).
        if (
            name == SUBAGENT_SPAN_NAME
            and attrs.get(SUBAGENT_RESULT_STATUS_ATTR) == SUBAGENT_RESULT_STATUS_FAILED_VALUE
        ):
            return True

    # `B-123` event-name arm. The name/attribute checks above can never see
    # `sandbox.violation` / `breaker.tripped` when the trigger rides as a
    # span EVENT rather than a span of its own — the real `breaker.tripped`
    # producer does exactly that (`harness_breaker_schema.py:282`, event on
    # a `harness.runtime.retry_breaker_fallback` carrier). Use the supplied
    # snapshot if the caller pre-read one (single-read discipline, see the
    # docstring above); else read `span.events` ONCE here — it is an OTel
    # PROPERTY that takes a lock and copies a deque on every access, not a
    # field. Return False tolerantly when there are none, mirroring the
    # `attrs is None` tolerance above so this predicate never raises.
    resolved_events = span.events if events is None else events
    if not resolved_events:
        return False
    return any(event.name in SECTION_10_2_EVENT_TRIGGER_NAMES for event in resolved_events)
