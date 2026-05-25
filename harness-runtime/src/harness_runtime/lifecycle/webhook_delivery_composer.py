"""U-RT-69 — `WebhookDeliveryComposer` + `WebhookDeliveryResult` carriers.

Per `Spec_Harness_Runtime_v1.md` v1.13 §14.10.1 architectural surfaces +
§14.10.3 spans (`hitl.webhook.deliver` + `hitl.webhook.attempt`) +
§14.10.4 fail classes.

Per `Implementation_Plan_Harness_Runtime_v2_11.md` §1 U-RT-69 (5 ACs).

Asynchronous out-of-process HITL delivery via HTTP POST when the
operator's `AskUserQuestionSurface` is configured for webhook mode (vs
the default MCP-server-elicit mode at U-RT-60). Owns retry orchestration
via `ctx.retry_breaker.get_policy("hitl_webhook")`; exhaustion raises
`RT-FAIL-HITL-WEBHOOK-DELIVERY-EXHAUSTED`.
"""

from __future__ import annotations

import asyncio
import hashlib
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import httpx

from harness_cp.hitl_timeout_degradation import (
    WebhookConfig,
    WebhookPayload,
)

__all__ = [
    "WebhookDeliveryComposer",
    "WebhookDeliveryExhaustedError",
    "WebhookDeliveryResult",
    "WebhookDeliverySchemaViolationError",
]


# --- attribute-name constants (spec §14.10.3) -------------------------------

ATTR_WEBHOOK_URL_HASH = "webhook.url_hash"
ATTR_WEBHOOK_DELIVERY_ATTEMPTS = "webhook.delivery_attempts"
ATTR_WEBHOOK_IDEMPOTENCY_KEY = "webhook.idempotency_key"
ATTR_RETRY_ATTEMPT_NUMBER = "retry.attempt_number"
ATTR_WEBHOOK_STATUS_CODE = "webhook.status_code"
ATTR_WEBHOOK_ATTEMPT_LATENCY_MS = "webhook.attempt_latency_ms"


# --- typed errors (spec §14.10.4) ------------------------------------------


class WebhookDeliveryExhaustedError(RuntimeError):
    """`RT-FAIL-HITL-WEBHOOK-DELIVERY-EXHAUSTED` typed carrier.

    Raised when all retry attempts failed (per
    `ctx.retry_breaker.get_policy("hitl_webhook")`).
    """


class WebhookDeliverySchemaViolationError(ValueError):
    """`RT-FAIL-HITL-WEBHOOK-SCHEMA-VIOLATION` typed carrier.

    Raised when the response shape doesn't match the configured
    `WebhookConfig` schema expectations.
    """


# --- carrier ----------------------------------------------------------------


@dataclass(frozen=True)
class WebhookDeliveryResult:
    """Outcome carrier per spec §14.10.1.

    `delivered=True` iff at least one HTTP POST returned a 2xx status;
    `status_code` reflects the terminal attempt's response code (None on
    transport-level failure). `response_idempotency_key` echoes the
    inbound idempotency-key for caller-side dedupe at the audit layer.
    `final_attempt_at` is epoch-ms timestamp of the terminal attempt.
    """

    delivered: bool
    status_code: int | None
    response_idempotency_key: str
    delivery_attempts: int
    final_attempt_at: int


# --- composer ---------------------------------------------------------------


class WebhookDeliveryComposer:
    """Out-of-process HITL delivery composer per C-RT-20 §14.10.1.

    Owns the per-delivery retry loop + idempotency-key propagation +
    span emission discipline. Materialized at bootstrap stage 5 alongside
    `MCPBackedAskUserQuestionSurface` (per spec §14.10.2 — the existing
    surface extends to delegate to this composer when
    `ctx.surface_config.mode == "webhook"`).
    """

    def __init__(
        self,
        *,
        retry_max_attempts: int = 3,
        retry_base_delay_seconds: float = 0.5,
        tracer_provider: Any = None,
        http_client_factory: Callable[[], httpx.AsyncClient] | None = None,
        sleep_fn: Callable[[float], Any] | None = None,
    ) -> None:
        """Construct composer with retry-policy hyperparameters + tracer.

        Parameters
        ----------
        retry_max_attempts:
            Maximum number of HTTP POST attempts (default 3 per spec
            §14.10's mock-server test pattern). v1 MVP — operator-tunable
            via the bootstrap config that supplies the policy registry at
            `ctx.retry_breaker.get_policy("hitl_webhook")` per §14.10.6
            deferred-to-discretion.
        retry_base_delay_seconds:
            Base delay between attempts. Per §14.10.6 deferred — the
            staircase / jitter policy lives at the bootstrap-supplied
            registry; v1 MVP uses constant base-delay.
        tracer_provider:
            OTel `TracerProvider`-shaped object (typed `Any`). Used to
            open `hitl.webhook.deliver` outer + `hitl.webhook.attempt`
            per-attempt spans. If `None`, span emission is skipped.
        http_client_factory:
            Test-injection seam for the `httpx.AsyncClient`. Default
            constructs one per `deliver_webhook` call (production).
        sleep_fn:
            Test-injection seam for the inter-attempt sleep. Default
            uses `asyncio.sleep`. Tests inject a no-op for determinism.
        """
        self._retry_max_attempts = retry_max_attempts
        self._retry_base_delay_seconds = retry_base_delay_seconds
        self._tracer_provider = tracer_provider
        self._http_client_factory = http_client_factory or (
            lambda: httpx.AsyncClient()
        )
        self._sleep_fn: Callable[[float], Any] = sleep_fn or asyncio.sleep

    async def deliver_webhook(
        self,
        webhook_config: WebhookConfig,
        payload: WebhookPayload,
        idempotency_key: str,
    ) -> WebhookDeliveryResult:
        """Deliver `payload` to `webhook_config.endpoint_url` via HTTP POST
        with retry orchestration per spec §14.10.1.

        Per spec §14.10.5 inv 1: same `idempotency_key` → same outcome
        within retention window. The idempotency-key header is set on every
        attempt to enable server-side deduplication.

        :raises WebhookDeliveryExhaustedError: when all retry attempts fail.
        """
        url = webhook_config.endpoint_url
        url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()

        tracer = (
            self._tracer_provider.get_tracer("harness.runtime.webhook_delivery")
            if self._tracer_provider is not None
            else None
        )

        outer_cm = (
            tracer.start_as_current_span("hitl.webhook.deliver")
            if tracer is not None
            else _NullSpanContext()
        )

        delivered = False
        last_status_code: int | None = None
        delivery_attempts = 0

        with outer_cm as outer_span:
            _set(outer_span, ATTR_WEBHOOK_URL_HASH, url_hash)
            _set(outer_span, ATTR_WEBHOOK_IDEMPOTENCY_KEY, idempotency_key)

            request_body = {
                "approval_id": payload.approval_id,
                "idempotency_key": str(payload.idempotency_key),
                "gate_evaluation_ref": str(payload.gate_evaluation_ref),
                "payload_body": dict(payload.payload_body),
            }
            headers = {
                "Idempotency-Key": idempotency_key,
                "Content-Type": "application/json",
            }

            for attempt in range(1, self._retry_max_attempts + 1):
                delivery_attempts = attempt
                attempt_cm = (
                    tracer.start_as_current_span("hitl.webhook.attempt")
                    if tracer is not None
                    else _NullSpanContext()
                )
                start_ns = time.perf_counter_ns()
                attempt_status: int | None = None
                with attempt_cm as attempt_span:
                    _set(attempt_span, ATTR_RETRY_ATTEMPT_NUMBER, attempt)
                    try:
                        async with self._http_client_factory() as client:
                            response = await client.post(
                                url,
                                json=request_body,
                                headers=headers,
                                timeout=_duration_to_seconds(
                                    webhook_config.timeout
                                ),
                            )
                        attempt_status = response.status_code
                        last_status_code = attempt_status
                        if 200 <= attempt_status < 300:
                            delivered = True
                    except (httpx.HTTPError, OSError):
                        attempt_status = None
                    finally:
                        end_ns = time.perf_counter_ns()
                        latency_ms = (end_ns - start_ns) // 1_000_000
                        _set(
                            attempt_span,
                            ATTR_WEBHOOK_STATUS_CODE,
                            attempt_status if attempt_status is not None else -1,
                        )
                        _set(
                            attempt_span,
                            ATTR_WEBHOOK_ATTEMPT_LATENCY_MS,
                            latency_ms,
                        )
                if delivered:
                    break
                if attempt < self._retry_max_attempts:
                    await self._sleep_fn(self._retry_base_delay_seconds)

            _set(outer_span, ATTR_WEBHOOK_DELIVERY_ATTEMPTS, delivery_attempts)

        final_attempt_at = int(time.time() * 1000)
        result = WebhookDeliveryResult(
            delivered=delivered,
            status_code=last_status_code,
            response_idempotency_key=idempotency_key,
            delivery_attempts=delivery_attempts,
            final_attempt_at=final_attempt_at,
        )
        if not delivered:
            raise WebhookDeliveryExhaustedError(
                f"RT-FAIL-HITL-WEBHOOK-DELIVERY-EXHAUSTED: "
                f"webhook_id={webhook_config.webhook_id!r} attempts="
                f"{delivery_attempts} terminal_status={last_status_code}"
            )
        return result


# --- factory ----------------------------------------------------------------
#
# Note: the v1.26 stage-5 LOOP_INIT factory body — accepting `RuntimeConfig` +
# returning `WebhookDeliveryComposer | None` per spec §14.16.2 — lives at
# `bootstrap/factories/webhook_delivery_composer_factory.py` (U-RT-97). This
# module retains only the carrier class body (U-RT-69) per the
# carrier-vs-factory split established by validator_framework_types.py +
# pause_resume_protocol_types.py precedents.


# --- private helpers --------------------------------------------------------


def _set(span: Any, key: str, value: Any) -> None:
    if span is None:
        return
    span.set_attribute(key, value)


class _NullSpanContext:
    def __enter__(self) -> None:
        return None

    def __exit__(self, *_args: Any) -> None:
        return None


def _duration_to_seconds(duration: Any) -> float:
    """Best-effort coerce a `Duration` carrier to float seconds.

    The CP-side `Duration` shape (per C-CP-21 §21.6) is a thin numeric
    wrapper; the bootstrap-supplied value is duck-typed for the timeout
    parameter. Supports common shapes: float / int (seconds), object
    with `seconds: int|float` attribute, or `timedelta`-compatible.
    """
    if isinstance(duration, (int, float)):
        return float(duration)
    if hasattr(duration, "total_seconds"):
        return float(duration.total_seconds())
    if hasattr(duration, "seconds"):
        return float(duration.seconds)
    # Last-resort default — surface as 30s timeout (matches httpx default).
    return 30.0
