"""B-71 precondition-5 witness — the escalation token is already a span attribute.

`.harness/council-b71-hitl-external-correlation-2026-08-12/DELIVERABLE.md` §5
precondition 5 asks to *"resolve the charter's 'not a span attribute' premise against
C1's `hitl.escalation.instance_id` proposal, and extend C10's leak-bar analysis from the
webhook channel to the tracing-export channel."*

The charter (`00-CHARTER.md:32`) declined to convene C7 on the ground that *"the identity
is not a span attribute (C7's adjacent interest is noted…)"*. **That premise is false in
effect**, and this module runs the parts of that which can be run.

**The mechanism, in one line:** §3 of the design puts the widening *inside*
`compose_hitl_action_id` — and that function's output is what BOTH named tracing
carriers already export.

- `hitl.invocation.audit_ledger_entry_id` is set to
  ``str(compose_hitl_action_id(parent_action_id, placement.position))``
  (`hitl_gate_composer.py:2238-2242`) — and is a member of OD's **DEFAULT-ON** exported
  structure set (`content_structure_discipline.py:81+`, C-OD-12 §12.2). Asserted below.
- `webhook.idempotency_key` is the same composed value threaded through
  `deliver_webhook_for_brief` onto the outer delivery span
  (`webhook_delivery_composer.py:270`), and is OD-canonical at C-OD-32
  (`HITL_WEBHOOK_SPAN_NAMESPACE_SCHEMA`). Asserted below.

So the token reaches the tracing exporter **without anyone adding a dedicated
attribute** — a different trust boundary from the webhook, and one the charter's premise
assumed was not in play.

**What that costs the raw identity.** Basis (B) derives from
``pre_dispatch_gate_owning_branch_identity`` = ``f"{snapshot_run_id}:pre-dispatch-gate:
{branch_index}"``, which contains the run_id **verbatim** (asserted below). Exported raw
on a default-on attribute, that is internal identity crossing an egress boundary — the
thing §3's leak bar and CP spec v1.112 §2.2 constraint 2 forbid elsewhere. The design's
existing "opaque, one-way, ≥128 bits" rule is therefore **load-bearing for the tracing
channel too**, not only the webhook.

**Executed here, end to end:** the last two tests drive the real
`_escalate_to_secondary_channel` and the real `WebhookDeliveryComposer` against an
`InMemorySpanExporter`, and read the emitted `webhook.idempotency_key` back off the
exported span — the producer composes the value, nothing in the test supplies it. Both
links are individually mutation-pinned. (Earlier drafts asserted only constants and the
pure composer; out-of-family review showed that was insufficient, twice.)
"""

from __future__ import annotations

from typing import Any, NoReturn, cast

import pytest
from harness_cp.hitl_placement import HITLPlacement, HITLPlacementKind
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.hitl_timeout_degradation import WebhookConfig, WebhookPayload
from harness_cp.pause_state_projection import pre_dispatch_gate_owning_branch_identity
from harness_is.state_ledger_entry_schema import Identifier
from harness_od.audit_ledger_types import SignatureAlgorithm
from harness_od.content_structure_discipline import DEFAULT_ON_STRUCTURE_ATTRIBUTES
from harness_od.hitl_webhook_namespace import (
    HITL_WEBHOOK_SPAN_NAMESPACE_SCHEMA,
    SPAN_SITE_HITL_WEBHOOK_DELIVER,
)
from harness_runtime.lifecycle.hitl_gate_composer import (
    HITLPauseRequestedSignal,
    RuntimeHITLGateComposer,
    compose_hitl_action_id,
)
from harness_runtime.lifecycle.webhook_delivery_composer import (
    ATTR_WEBHOOK_IDEMPOTENCY_KEY,
    WebhookDeliveryComposer,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

_AUDIT_ATTR = "hitl.invocation.audit_ledger_entry_id"


class _OkResponse:
    status_code = 200
    text = ""

    def json(self) -> dict[str, Any]:
        return {}


class _OkClient:
    """Minimal httpx.AsyncClient double — one 200, no retries needed."""

    async def __aenter__(self) -> _OkClient:
        return self

    async def __aexit__(self, *_: Any) -> None:
        return None

    async def post(self, *_: Any, **__: Any) -> _OkResponse:
        return _OkResponse()


class _Step:
    """Minimal WorkflowStep stand-in — the helper reads only `step_id`."""

    step_id = "branch-0"


def test_the_audit_attribute_is_default_on_but_not_on_the_escalation_path() -> None:
    """The audit attribute is exported by default — and is NOT a carrier here.

    Both halves matter, and an earlier draft asserted only the first and drew the wrong
    conclusion from it (out-of-family Codex).

    It IS a member of the DEFAULT-ON structure set (C-OD-12 §12.2). But the B-71
    escalation never reaches it: `_escalate_to_secondary_channel` is declared `NoReturn`
    and always raises `HITLPauseRequestedSignal`, while the `hitl.invocation.opened`
    span that carries this attribute is opened only on the FALL-THROUGH path
    (`hitl_gate_composer.py:2033-2044` — the call, then the span). The timeout-secondary
    branch exits the same way before `:2238`.

    Unreachable in BOTH venues: the durable-async call at `:2033-2040` precedes the span
    entirely (no `hitl.invocation.*` span opens there at all), and the timeout venue at
    `:2165` sits inside step 4f — so those spans DO open — but still raises before
    `:2238`. Either way the attribute is never set.

    So for this population the token has exactly ONE tracing carrier, not two.
    """
    assert _AUDIT_ATTR in DEFAULT_ON_STRUCTURE_ATTRIBUTES

    import harness_runtime.lifecycle.hitl_gate_composer as _hgc

    fn = _hgc.RuntimeHITLGateComposer._escalate_to_secondary_channel
    assert fn.__annotations__.get("return") in ("NoReturn", NoReturn), (
        "the escalation helper is what makes the audit span unreachable on this path; "
        "if it stopped being NoReturn the carrier analysis in DELIVERABLE §4-quater "
        "must be re-derived"
    )


def test_the_webhook_idempotency_key_is_an_od_canonical_span_attribute() -> None:
    """The second carrier is a declared span attribute, not an incidental log line.

    OD-canonical at C-OD-32 on the outer `hitl.webhook.deliver` span, and the runtime
    emits under exactly that name.
    """
    spec = HITL_WEBHOOK_SPAN_NAMESPACE_SCHEMA["webhook.idempotency_key"]
    assert spec.span_site == SPAN_SITE_HITL_WEBHOOK_DELIVER
    assert ATTR_WEBHOOK_IDEMPOTENCY_KEY == spec.attribute_name, (
        "the runtime emitter and the OD canonical schema must agree byte-exactly "
        "(Pattern-P1 alignment) — if they diverge, this witness is reading the wrong "
        "attribute and the leak analysis below is mis-scoped"
    )


def test_the_reachable_carrier_derives_from_the_composer_the_widening_lands_in() -> None:
    """The ONE reachable carrier is fed by the function §3 widens.

    `compose_hitl_action_id` produces the value (`:1302`), which is threaded to
    `deliver_webhook_for_brief` and set on the outer delivery span as
    `webhook.idempotency_key` (`webhook_delivery_composer.py:270`). Executed here: the
    composer is pure and deterministic, so widening it widens what that span exports.
    """
    parent = "workflow:wf-x:fanout"
    composed = compose_hitl_action_id(parent, HITLPlacementKind.SUB_AGENT_BOUNDARY)
    assert str(composed) == str(
        compose_hitl_action_id(parent, HITLPlacementKind.SUB_AGENT_BOUNDARY)
    )
    assert str(composed).startswith("hitl:"), (
        "the `hitl:` prefix is the OD audit-trace source discriminator; if it moved, "
        "re-read which namespace consumes this value before trusting the leak scope"
    )


def test_the_raw_internal_identity_carries_the_run_id_verbatim() -> None:
    """Why the token MUST be hashed before it reaches the composer.

    Basis (B)'s raw form embeds `snapshot_run_id` literally. Folded un-hashed into
    `compose_hitl_action_id`, it would place a run_id on a DEFAULT-ON exported span
    attribute — internal identity across an egress boundary, which CP spec v1.112 §2.2
    constraint 2 and §3's leak bar forbid on the operator-facing surfaces. The design's
    "opaque, one-way, ≥128 bits" rule is what prevents it, and this is the evidence that
    the rule is load-bearing for tracing and not only for the webhook.
    """
    raw = pre_dispatch_gate_owning_branch_identity("run-abc123", 0)
    assert "run-abc123" in raw
    assert raw == "run-abc123:pre-dispatch-gate:0"


def test_a_dedicated_escalation_attribute_has_no_span_to_hang_on() -> None:
    """Why C1's `hitl.escalation.instance_id` is declined — reachability, not just redundancy.

    The value is already exported by the one reachable carrier, so a dedicated attribute
    is a SECOND carrier of one value. It is also homeless: the escalation path opens no
    `hitl.invocation.*` span at all (see the reachability test above), so the attribute
    would need either a new span site or a C-OD-32 amendment to ride the webhook span —
    a cleared-contract change for zero information. Pinned as absence, so declining stays
    cheap to reverse.
    """
    assert not [a for a in DEFAULT_ON_STRUCTURE_ATTRIBUTES if a.startswith("hitl.escalation")]
    assert not [k for k in HITL_WEBHOOK_SPAN_NAMESPACE_SCHEMA if k.startswith("hitl.escalation")]


# --- the export round-trip: emit, export, assert the emitted value ------------------
#
# Out-of-family Codex round 2 [P1] demonstrated the gap: it removed the production
# `_set(outer_span, ATTR_WEBHOOK_IDEMPOTENCY_KEY, ...)` call and all five tests above
# stayed green, because they only read constants and the pure composer. This test runs
# the real `WebhookDeliveryComposer.deliver_webhook` against an `InMemorySpanExporter`
# and asserts the value that actually leaves the process.


@pytest.mark.asyncio
async def test_the_composed_action_id_is_emitted_on_the_exported_span() -> None:
    """END-TO-END for the export half: the value `compose_hitl_action_id` produces is
    what `webhook.idempotency_key` carries on the exported `hitl.webhook.deliver` span.

    This is the link §4-quater.4 recorded as CITED; it is now executed. Deleting the
    production `_set` call turns this RED.
    """
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))

    # The value the escalation would thread — composed by the real function the
    # widening lands in (§3), so a widened token flows through this same argument.
    idempotency_key = str(
        compose_hitl_action_id("workflow:wf-export:fanout", HITLPlacementKind.SUB_AGENT_BOUNDARY)
    )

    composer = WebhookDeliveryComposer(
        retry_max_attempts=1,
        http_client_factory=lambda: _OkClient(),
        tracer_provider=provider,
    )
    result = await composer.deliver_webhook(
        WebhookConfig(
            webhook_id="wh-b71",
            endpoint_url="https://example.test/hook",
            timeout=5,
            degradation_mode="fail-closed",
        ),
        WebhookPayload(
            approval_id="approve-b71",
            idempotency_key=idempotency_key,
            gate_evaluation_ref="entry-b71",
            payload_body={"escalation_reason": "durable_async_cell_synchrony"},
        ),
        idempotency_key,
    )
    assert result.delivered is True

    spans = exporter.get_finished_spans()
    deliver = [s for s in spans if s.name == SPAN_SITE_HITL_WEBHOOK_DELIVER]
    assert deliver, (
        f"no {SPAN_SITE_HITL_WEBHOOK_DELIVER} span was exported; got {[s.name for s in spans]}"
    )
    emitted = deliver[0].attributes or {}
    assert emitted.get(ATTR_WEBHOOK_IDEMPOTENCY_KEY) == idempotency_key, (
        "the composed hitl action_id did not reach the exported span attribute — the "
        "tracing-export leak path DELIVERABLE §4-quater rests on is not live"
    )
    # And it really is the composer's output that left the process, not a coincidence.
    assert str(emitted[ATTR_WEBHOOK_IDEMPOTENCY_KEY]).startswith("hitl:")


@pytest.mark.asyncio
async def test_the_real_escalation_helper_puts_its_own_composed_id_on_the_span() -> None:
    """PRODUCER → adapter → exporter, end to end.

    The test above proves the delivery composer exports a caller-supplied key; it does
    not prove the ESCALATION supplies that key — out-of-family Codex round 3 showed the
    gap by replacing `_escalate_to_secondary_channel` with a mutant that never invokes
    the webhook path, leaving every other test green.

    This drives the real helper. It composes its own `idempotency_key` at
    `hitl_gate_composer.py:1302` via `compose_hitl_action_id` and threads it to
    `deliver_webhook_for_brief`; the value is then read back off the exported
    `hitl.webhook.deliver` span. Nothing here supplies the key — the production code
    does, which is the whole point.
    """
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))

    webhook = WebhookDeliveryComposer(
        retry_max_attempts=1,
        http_client_factory=lambda: _OkClient(),
        tracer_provider=provider,
        webhook_config=WebhookConfig(
            webhook_id="wh-b71-producer",
            endpoint_url="https://example.test/hook",
            timeout=5,
            degradation_mode="fail-closed",
        ),
    )
    composer = RuntimeHITLGateComposer(
        inner=cast(Any, object()),
        applicable_placements=frozenset({HITLPlacementKind.SUB_AGENT_BOUNDARY}),
        ask_user_question_surface=cast(Any, object()),
        ledger_writer=cast(Any, object()),
        audit_writer=cast(Any, object()),
        tracer_provider=provider,
        audit_signing_key_id="harness-runtime-b71-test",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        procedural_tier_snapshot_resolver=lambda: Identifier("b" * 64),
        webhook_delivery_composer=webhook,
    )

    parent_action_id = "workflow:wf-producer:fanout"
    placement = HITLPlacement(position=HITLPlacementKind.SUB_AGENT_BOUNDARY)

    # The helper is NoReturn — it always raises the typed pause signal.
    with pytest.raises(HITLPauseRequestedSignal):
        await composer._escalate_to_secondary_channel(
            parent_action_id=cast(Any, parent_action_id),
            step=cast(Any, _Step()),
            placement=placement,
            palette=frozenset({HITLResponse.APPROVE}),
            escalation_reason="durable_async_cell_synchrony",
            tenant_id=None,
        )

    deliver = [s for s in exporter.get_finished_spans() if s.name == SPAN_SITE_HITL_WEBHOOK_DELIVER]
    assert deliver, "the escalation did not reach the webhook delivery span at all"
    emitted = (deliver[0].attributes or {}).get(ATTR_WEBHOOK_IDEMPOTENCY_KEY)
    assert emitted == str(compose_hitl_action_id(parent_action_id, placement.position)), (
        "the escalation's own composed action_id is not what reached the exported span "
        "— the producer→exporter chain DELIVERABLE §4-quater rests on is broken"
    )
