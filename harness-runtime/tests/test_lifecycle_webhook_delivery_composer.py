"""U-RT-69 — `WebhookDeliveryComposer` + `WebhookDeliveryResult`.

Per `Implementation_Plan_Harness_Runtime_v2_11.md` §1 U-RT-69 (5 ACs).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import httpx
import pytest
from harness_cp.hitl_timeout_degradation import (
    WebhookConfig,
    WebhookPayload,
)
from harness_runtime.lifecycle.webhook_delivery_composer import (
    ATTR_RETRY_ATTEMPT_NUMBER,
    ATTR_WEBHOOK_DELIVERY_ATTEMPTS,
    ATTR_WEBHOOK_IDEMPOTENCY_KEY,
    ATTR_WEBHOOK_STATUS_CODE,
    ATTR_WEBHOOK_URL_HASH,
    WebhookDeliveryComposer,
    WebhookDeliveryExhaustedError,
    WebhookDeliveryResult,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

# ---------- helpers --------------------------------------------------------


def _make_webhook_config(url: str = "https://example.test/hook") -> WebhookConfig:
    return WebhookConfig(
        webhook_id="wh-1",
        endpoint_url=url,
        timeout=5,
        degradation_mode="fail-closed",
    )


def _make_payload() -> WebhookPayload:
    return WebhookPayload(
        approval_id="approve-123",
        idempotency_key="idem-payload-1",
        gate_evaluation_ref="entry-1",
        payload_body={"prompt": "Approve?"},
    )


class _RecordingClient:
    """Test double for httpx.AsyncClient that returns scripted responses."""

    def __init__(self, responses: list[Any]) -> None:
        self._responses = list(responses)
        self.requests: list[tuple[str, dict[str, Any], dict[str, str]]] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args: Any):
        return None

    async def post(self, url: str, *, json: dict, headers: dict, timeout: float) -> Any:
        _ = timeout
        self.requests.append((url, json, headers))
        if not self._responses:
            raise RuntimeError("test exhausted scripted responses")
        outcome = self._responses.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome  # already a Response-shaped object


class _MockResponse:
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code


def _async_noop_sleep_factory() -> tuple[Any, list[float]]:
    calls: list[float] = []

    async def noop(delay: float) -> None:
        calls.append(delay)

    return noop, calls


# ---------- AC #1 — delivers + retries -------------------------------------


@pytest.mark.asyncio
async def test_deliver_succeeds_first_attempt() -> None:
    client = _RecordingClient([_MockResponse(200)])
    composer = WebhookDeliveryComposer(
        retry_max_attempts=3,
        http_client_factory=lambda: client,
    )
    result = await composer.deliver_webhook(
        _make_webhook_config(),
        _make_payload(),
        "idem-1",
    )
    assert isinstance(result, WebhookDeliveryResult)
    assert result.delivered is True
    assert result.status_code == 200
    assert result.delivery_attempts == 1
    assert result.response_idempotency_key == "idem-1"
    assert client.requests[0][2]["Idempotency-Key"] == "idem-1"


@pytest.mark.asyncio
async def test_deliver_succeeds_after_retry() -> None:
    """AC #5: 3 attempts, 2 failures + 1 success → delivered=True attempts=3."""
    sleep_fn, sleep_calls = _async_noop_sleep_factory()
    # First two fail with 500; third returns 200.
    responses = [_MockResponse(500), _MockResponse(503), _MockResponse(200)]
    client = _RecordingClient(responses)
    composer = WebhookDeliveryComposer(
        retry_max_attempts=3,
        http_client_factory=lambda: client,
        sleep_fn=sleep_fn,
    )
    result = await composer.deliver_webhook(
        _make_webhook_config(),
        _make_payload(),
        "idem-retry",
    )
    assert result.delivered is True
    assert result.status_code == 200
    assert result.delivery_attempts == 3
    assert len(sleep_calls) == 2  # sleep between attempts 1→2, 2→3


# ---------- AC #4 — all retries failed raises EXHAUSTED --------------------


@pytest.mark.asyncio
async def test_deliver_all_attempts_fail_raises_exhausted() -> None:
    sleep_fn, _ = _async_noop_sleep_factory()
    client = _RecordingClient([_MockResponse(500), _MockResponse(500), _MockResponse(503)])
    composer = WebhookDeliveryComposer(
        retry_max_attempts=3,
        http_client_factory=lambda: client,
        sleep_fn=sleep_fn,
    )
    with pytest.raises(
        WebhookDeliveryExhaustedError,
        match="RT-FAIL-HITL-WEBHOOK-DELIVERY-EXHAUSTED",
    ):
        await composer.deliver_webhook(
            _make_webhook_config(),
            _make_payload(),
            "idem-fail",
        )


@pytest.mark.asyncio
async def test_deliver_transport_exception_treated_as_failure() -> None:
    """Connection errors count as failed attempts."""
    sleep_fn, _ = _async_noop_sleep_factory()
    client = _RecordingClient(
        [
            httpx.ConnectError("simulated connection refused"),
            _MockResponse(204),  # success
        ]
    )
    composer = WebhookDeliveryComposer(
        retry_max_attempts=3,
        http_client_factory=lambda: client,
        sleep_fn=sleep_fn,
    )
    result = await composer.deliver_webhook(
        _make_webhook_config(),
        _make_payload(),
        "idem-transport",
    )
    assert result.delivered is True
    assert result.status_code == 204
    assert result.delivery_attempts == 2


# ---------- AC #2 + #3 — span emission -------------------------------------


@pytest.mark.asyncio
async def test_deliver_emits_outer_and_attempt_spans() -> None:
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))

    sleep_fn, _ = _async_noop_sleep_factory()
    client = _RecordingClient([_MockResponse(429), _MockResponse(200)])
    composer = WebhookDeliveryComposer(
        retry_max_attempts=3,
        http_client_factory=lambda: client,
        sleep_fn=sleep_fn,
        tracer_provider=provider,
    )
    await composer.deliver_webhook(
        _make_webhook_config(),
        _make_payload(),
        "idem-spans",
    )

    spans = exporter.get_finished_spans()
    names = [s.name for s in spans]
    assert "hitl.webhook.deliver" in names
    # 2 attempt spans for 2 attempts.
    assert names.count("hitl.webhook.attempt") == 2

    outer = next(s for s in spans if s.name == "hitl.webhook.deliver")
    outer_attrs = dict(outer.attributes or {})
    assert ATTR_WEBHOOK_URL_HASH in outer_attrs
    assert outer_attrs[ATTR_WEBHOOK_IDEMPOTENCY_KEY] == "idem-spans"
    assert outer_attrs[ATTR_WEBHOOK_DELIVERY_ATTEMPTS] == 2

    attempt_spans = [s for s in spans if s.name == "hitl.webhook.attempt"]
    for span in attempt_spans:
        attrs = dict(span.attributes or {})
        assert ATTR_RETRY_ATTEMPT_NUMBER in attrs
        assert ATTR_WEBHOOK_STATUS_CODE in attrs


# ---------- factory --------------------------------------------------------


def test_factory_returns_composer_with_tracer_bound() -> None:
    # v1.26 §14.16.2 factory landed at bootstrap/factories/
    # webhook_delivery_composer_factory.py; this test verifies the carrier
    # construction shape against TracerProvider. The bootstrap factory unit
    # tests live at test_u_rt_97_webhook_delivery_composer_factory.py.
    provider = TracerProvider()
    composer = WebhookDeliveryComposer(tracer_provider=provider)
    assert isinstance(composer, WebhookDeliveryComposer)


# ---------- WebhookDeliveryResult carrier ----------------------------------


def test_webhook_delivery_result_frozen() -> None:
    result = WebhookDeliveryResult(
        delivered=True,
        status_code=200,
        response_idempotency_key="x",
        delivery_attempts=1,
        final_attempt_at=1234567890,
    )
    with pytest.raises(Exception):
        result.delivered = False  # type: ignore[misc]


# ---------- deliver_webhook_for_brief (Reading H) --------------------------
# Per runtime spec v1.34 §14.10.1 brief-surface absorption + fork doc
# `.harness/class_1_fork_webhook_composer_per_workflow_context_threading.md`
# Reading (H) operator-ratified 2026-05-28.


def _make_brief_for_composer_tests():
    from harness_cp.hitl_response_palette import HITLResponse
    from harness_cp.validator_framework_types import HITLEscalationBrief

    return HITLEscalationBrief(
        parent_step_id="step-1",
        parent_action_id="workflow:wf-test:step:0",
        fail_class=None,
        fail_detail_hash=None,
        escalation_reason="durable_async_cell_synchrony",
        proposed_response_palette=frozenset({HITLResponse.APPROVE}),
    )


@pytest.mark.asyncio
async def test_deliver_webhook_for_brief_raises_when_webhook_config_missing() -> None:
    """Reading H invariant: brief surface requires ctor-supplied webhook_config."""
    composer = WebhookDeliveryComposer(retry_max_attempts=1)  # no webhook_config
    brief = _make_brief_for_composer_tests()
    with pytest.raises(RuntimeError, match="webhook_config"):
        await composer.deliver_webhook_for_brief(brief, "idem-1")


@pytest.mark.asyncio
async def test_deliver_webhook_for_brief_dispatches_via_raw_surface() -> None:
    """Reading H projection: brief → payload → raw deliver_webhook."""
    client = _RecordingClient([_MockResponse(200)])
    composer = WebhookDeliveryComposer(
        retry_max_attempts=1,
        http_client_factory=lambda: client,
        webhook_config=_make_webhook_config("https://example.test/brief-surface"),
    )
    brief = _make_brief_for_composer_tests()
    result = await composer.deliver_webhook_for_brief(brief, "idem-brief-1")
    assert result.delivered is True
    assert result.status_code == 200
    # Verify the raw HTTP layer received the projected payload
    assert len(client.requests) == 1
    url, body, headers = client.requests[0]
    assert url == "https://example.test/brief-surface"
    assert headers["Idempotency-Key"] == "idem-brief-1"
    assert body["approval_id"] == "workflow:wf-test:step:0"
    assert body["gate_evaluation_ref"] == "workflow:wf-test:step:0"
    assert body["payload_body"]["escalation_reason"] == "durable_async_cell_synchrony"


@pytest.mark.asyncio
async def test_deliver_webhook_for_brief_propagates_exhausted_error() -> None:
    """Reading H exhaustion path: brief surface propagates raw surface exhaustion."""
    sleep_fn, _ = _async_noop_sleep_factory()
    client = _RecordingClient([_MockResponse(500), _MockResponse(500), _MockResponse(500)])
    composer = WebhookDeliveryComposer(
        retry_max_attempts=3,
        http_client_factory=lambda: client,
        sleep_fn=sleep_fn,
        webhook_config=_make_webhook_config(),
    )
    brief = _make_brief_for_composer_tests()
    with pytest.raises(WebhookDeliveryExhaustedError):
        await composer.deliver_webhook_for_brief(brief, "idem-exhaust-1")


@pytest.mark.asyncio
async def test_repeat_deliver_webhook_same_idempotency_key_gets_distinct_f2_entries(
    tmp_path: Any,
) -> None:
    """Regression guard (out-of-family Codex [P2], round 5) — this
    composer's cost-attribution wrapper fires unconditionally on EVERY
    `deliver_webhook()` call (no idempotent skip at that layer). Codex's
    own probe showed 2 calls with the SAME `idempotency_key` produced 2
    audit entries but only 1 F2 entry before the fix (both audit entries
    referenced the same anchor) — because the composer's own `span_id` is
    `f"webhook-deliver-{idempotency_key}"`, which repeats identically
    across such calls. The production wiring now passes a fresh
    per-invocation `dispatch_disambiguator` (a UUID) specifically to
    prevent this."""
    from decimal import Decimal

    from harness_is.jsonl_event_ledger_lifecycle import JsonlLedgerHandle
    from harness_is.state_ledger_entry_schema import Actor, ActorClass
    from harness_is.state_ledger_write import read_ledger
    from harness_od.rate_table_types import RateTable, WebhookRate
    from harness_runtime.lifecycle.cost_attribution import RuntimeCostAttributionChain
    from harness_runtime.lifecycle.state_ledger import LedgerWriter

    class _RecordingAuditWriter:
        def __init__(self) -> None:
            self.appended: list[tuple[str | None, object]] = []

        def append(self, tenant_id: str | None, audit_entry: object) -> object:
            self.appended.append((tenant_id, audit_entry))
            return "appended"

    rate_table = RateTable(
        version="2026-07-13-test",
        providers={},
        tool_rates={},
        webhook_rate=WebhookRate(flat_per_attempt=Decimal("0.01"), plus_egress=False),
        cpu_rate_per_ms=Decimal("0"),
        egress_rate_per_byte=Decimal("0"),
    )
    audit_writer = _RecordingAuditWriter()
    ledger_path = tmp_path / "state.jsonl"
    ledger_path.touch()
    ledger_writer = LedgerWriter(
        handle=JsonlLedgerHandle(canonical_path=ledger_path, exists=True, entry_count=0),
        actor=Actor(actor_class=ActorClass.AGENT, actor_id="test-webhook-composer"),
    )
    client = _RecordingClient([_MockResponse(200), _MockResponse(200)])
    composer = WebhookDeliveryComposer(
        retry_max_attempts=1,
        http_client_factory=lambda: client,
        rate_table=rate_table,
        cost_chain=RuntimeCostAttributionChain(),
        audit_writer=audit_writer,
        workflow_id="wf-repeat",
        parent_action_id="hitl:wf-repeat:gate:0",
        parent_idempotency_key="parent-1",
        ledger_writer=ledger_writer,
    )
    # Two SEPARATE deliver_webhook() calls sharing the SAME idempotency_key —
    # a legitimate caller-side pattern (outer-level retry of the whole call,
    # not just the composer's own internal HTTP-attempt loop).
    await composer.deliver_webhook(_make_webhook_config(), _make_payload(), "idem-shared")
    await composer.deliver_webhook(_make_webhook_config(), _make_payload(), "idem-shared")

    assert len(audit_writer.appended) == 2
    entries = read_ledger(ledger_writer.handle)
    cost_entries = [e for e in entries if str(e.action_id).startswith("cost:")]
    assert len(cost_entries) == 2, (
        f"2 deliver_webhook() calls sharing one idempotency_key must get 2 "
        f"distinct F2 entries, not collapse via IDEMPOTENT_NOOP; "
        f"got {len(cost_entries)}"
    )
    entry_cores = {str(e[1].payload.entry_core) for e in audit_writer.appended}
    assert len(entry_cores) == 2, "each call's audit entry must reference its OWN F2 anchor"


# ---------------------------------------------------------------------------
# B-47 PR B2a merge-gate round-1 — signing-backend USE-half witness
# ---------------------------------------------------------------------------


class _CountingBackend:
    algorithm = "ed25519"

    def __init__(self) -> None:
        self.sign_calls = 0

    def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
        self.sign_calls += 1
        return b"c" * 64  # genuine ed25519 width — the OD seam validates length

    def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
        return True


class _RecordingAuditWriter:
    def __init__(self) -> None:
        self.appended: list[tuple[str | None, object]] = []

    def append(self, tenant_id: str | None, audit_entry: object) -> object:
        self.appended.append((tenant_id, audit_entry))
        return "appended"


def test_signing_backend_is_passed_into_cost_audit_composition() -> None:
    """Merge-gate round-1 BLOCK (PR B2a) — USE-half witness: the bootstrap
    witness proves the field is SET; this proves the field is PASSED into
    composition.

    Calls the real sync `_attribute_webhook_cost_best_effort` helper (the
    connecting line under test) with the cost substrates + a counting backend
    on the composer — the `signing_backend=self._signing_backend` kwarg must
    deliver the backend to `attribute_webhook_dispatch_cost` and on to the OD
    signing seam (sign invoked), not merely hold it as an inert field.
    """
    from decimal import Decimal

    from harness_od.rate_table_types import RateTable, WebhookRate
    from harness_runtime.lifecycle.cost_attribution import RuntimeCostAttributionChain

    rate_table = RateTable(
        version="2026-07-17-use-half-witness",
        providers={},
        tool_rates={},
        webhook_rate=WebhookRate(flat_per_attempt=Decimal("0.01"), plus_egress=False),
        cpu_rate_per_ms=Decimal("0.001"),
        egress_rate_per_byte=Decimal("0"),
    )
    backend = _CountingBackend()
    audit_writer = _RecordingAuditWriter()
    composer = WebhookDeliveryComposer(
        retry_max_attempts=1,
        rate_table=rate_table,
        cost_chain=RuntimeCostAttributionChain(),
        audit_writer=audit_writer,
        signing_backend=backend,
        workflow_id="wf-use-half",
        parent_action_id="hitl:wf-use-half:gate:0",
        parent_idempotency_key="parent-idem-1",
    )
    composer._attribute_webhook_cost_best_effort(
        url="https://ops.example.com/hitl",
        request_body={"summary": "approval needed"},
        idempotency_key="webhook-1",
    )
    assert len(audit_writer.appended) == 1, "cost-attribution must have fired"
    assert backend.sign_calls >= 1, (
        "USE-half: the composer's signing_backend must be passed into "
        "attribute_webhook_dispatch_cost (backend.sign never invoked)"
    )


# ---------------------------------------------------------------------------
# U-RT-136 (CP v1.101 §2, webhook-receipt site class) — post-effect carrier.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_u_rt_136_post_effect_signing_failure_carries_webhook_receipt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The POST completed (200) and cost-attribution signing then failed
    under `audit_signing_fail_closed=ON`: `deliver_webhook` raises the
    result-preserving `PostEffectAuditSigningError` whose `.result` is the
    already-composed `WebhookDeliveryResult` (delivered=True receipt) — the
    completed external effect is never discarded (CP v1.101 §2).

    Mutation probe: swapping the carrier wrap for a bare re-raise loses the
    receipt and FAILS the `.result` assertions."""
    import harness_runtime.lifecycle.cost_attribution_webhook_dispatch as attr_mod
    from harness_runtime.lifecycle.audit_signing_errors import (
        AuditSigningFailedError,
        PostEffectAuditSigningError,
        PostEffectClass,
    )

    def _signing_fails(**_k: Any) -> Any:
        raise AuditSigningFailedError("kms unavailable (u-rt-136 webhook test)")

    monkeypatch.setattr(attr_mod, "attribute_webhook_dispatch_cost", _signing_fails)

    client = _RecordingClient([_MockResponse(200)])
    composer = WebhookDeliveryComposer(
        retry_max_attempts=1,
        http_client_factory=lambda: client,
        rate_table=cast(Any, object()),
        cost_chain=cast(Any, object()),
        audit_writer=cast(Any, object()),
        workflow_id="wf-136",
        parent_action_id="workflow:wf-136:step:0",
        parent_idempotency_key="parent-idem-136",
        audit_signing_fail_closed=True,
    )
    with pytest.raises(PostEffectAuditSigningError) as excinfo:
        await composer.deliver_webhook(_make_webhook_config(), _make_payload(), "idem-136")
    carrier = excinfo.value
    assert carrier.effect_class is PostEffectClass.WEBHOOK_RECEIPT
    receipt = cast(WebhookDeliveryResult, carrier.result)
    assert receipt.delivered is True
    assert receipt.status_code == 200

    # Flag-OFF control — behavior preserved verbatim: delivery result
    # returned, signing failure ERROR-logged and swallowed.
    off_client = _RecordingClient([_MockResponse(200)])
    off_composer = WebhookDeliveryComposer(
        retry_max_attempts=1,
        http_client_factory=lambda: off_client,
        rate_table=cast(Any, object()),
        cost_chain=cast(Any, object()),
        audit_writer=cast(Any, object()),
        workflow_id="wf-136",
        parent_action_id="workflow:wf-136:step:0",
        parent_idempotency_key="parent-idem-136",
    )
    off_result = await off_composer.deliver_webhook(
        _make_webhook_config(), _make_payload(), "idem-136-off"
    )
    assert off_result.delivered is True


@pytest.mark.asyncio
async def test_legacy_ctor_tenant_used_when_per_call_tenant_omitted(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """codex [P2] round 8: a caller that constructs `WebhookDeliveryComposer
    (tenant_id="tenant-a")` and uses the legacy 3-arg `deliver_webhook` call
    (never adopting the newer per-call `tenant_id` kwarg) must still have
    its protected-store write land under tenant-a — the SAME tenant scope
    the audit-composition call for this identical failure already uses via
    `self._tenant_id`. Landing it under the untenanted scope instead would
    make a later, correctly-tenant-scoped recovery read wrongly refused as
    cross-tenant.

    Mutation probe: reverting the raise-site's `effective_tenant_id` back
    to the raw `tenant_id` parameter makes the `store.read("tenant-a",
    ref)` call below raise `ProtectedStoreCrossTenantError` instead of
    returning the receipt."""
    import harness_runtime.lifecycle.cost_attribution_webhook_dispatch as attr_mod
    from cryptography.fernet import Fernet
    from harness_runtime.lifecycle.audit_signing_errors import (
        AuditSigningFailedError,
        PostEffectAuditSigningError,
    )
    from harness_runtime.lifecycle.protected_result_store import ProtectedResultStore

    def _signing_fails(**_k: Any) -> Any:
        raise AuditSigningFailedError("kms unavailable (u-rt-136 webhook tenant test)")

    monkeypatch.setattr(attr_mod, "attribute_webhook_dispatch_cost", _signing_fails)

    store = ProtectedResultStore(
        tmp_path / "protected-results", codec=Fernet(Fernet.generate_key()), ttl_seconds=86400.0
    )
    client = _RecordingClient([_MockResponse(200)])
    composer = WebhookDeliveryComposer(
        retry_max_attempts=1,
        http_client_factory=lambda: client,
        rate_table=cast(Any, object()),
        cost_chain=cast(Any, object()),
        audit_writer=cast(Any, object()),
        workflow_id="wf-136-tenant",
        parent_action_id="workflow:wf-136-tenant:step:0",
        parent_idempotency_key="parent-idem-136-tenant",
        audit_signing_fail_closed=True,
        protected_result_store=store,
        tenant_id="tenant-a",
    )
    with pytest.raises(PostEffectAuditSigningError) as excinfo:
        # Legacy 3-positional-arg call — no per-call `tenant_id` kwarg.
        await composer.deliver_webhook(_make_webhook_config(), _make_payload(), "idem-136-tenant")
    ref = excinfo.value.result_ref
    assert isinstance(ref, str), f"expected a resolvable ref, got {ref!r}"
    receipt = cast(WebhookDeliveryResult, store.read("tenant-a", ref))
    assert receipt.delivered is True


@pytest.mark.asyncio
async def test_deliver_webhook_threads_effective_tenant_into_cost_attribution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """codex [P2] round 10: `_attribute_webhook_cost_best_effort` used
    `self._tenant_id` (ctor-bound, always `None` from the bootstrap
    factory today) even when a per-call `tenant_id` was supplied — as the
    real HITL webhook-escalation site does via `step_context.tenant_id`.
    The SAME delivery's audit record and its protected-store recovery ref
    would then diverge: the ref tenant-scoped, the audit record
    untenanted. `deliver_webhook` now threads its already-resolved
    `effective_tenant_id` into the cost-attribution call too.

    Mutation probe: reverting `_attribute_webhook_cost_best_effort`'s
    `tenant_id=` kwarg back to `self._tenant_id` makes the captured kwarg
    `None` instead of `"tenant-a"`."""
    import harness_runtime.lifecycle.cost_attribution_webhook_dispatch as attr_mod

    captured: dict[str, Any] = {}

    def _capture(**kwargs: Any) -> Any:
        captured.update(kwargs)
        return None

    monkeypatch.setattr(attr_mod, "attribute_webhook_dispatch_cost", _capture)

    client = _RecordingClient([_MockResponse(200)])
    composer = WebhookDeliveryComposer(
        retry_max_attempts=1,
        http_client_factory=lambda: client,
        rate_table=cast(Any, object()),
        cost_chain=cast(Any, object()),
        audit_writer=cast(Any, object()),
        workflow_id="wf-tenant-attr",
        parent_action_id="workflow:wf-tenant-attr:step:0",
        parent_idempotency_key="parent-idem-tenant-attr",
    )
    await composer.deliver_webhook(
        _make_webhook_config(), _make_payload(), "idem-tenant-attr", tenant_id="tenant-a"
    )
    assert captured.get("tenant_id") == "tenant-a"
