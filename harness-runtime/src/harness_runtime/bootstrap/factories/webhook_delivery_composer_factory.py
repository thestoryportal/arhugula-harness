"""U-RT-97 stage-5 webhook composer factory for local operator binding.

`None` preserves production opt-out. The legacy empty marker still constructs
an unconfigured composer, except when a pause protocol is bound: that unsafe
combination is refused at bootstrap. A complete config binds only literal
loopback HTTP, one attempt, fail-closed behavior and an isolated HTTP client.
Construction failures use RT-FAIL-WEBHOOK-COMPOSER-STAGE-MATERIALIZE.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import httpx
from harness_cp.hitl_timeout_degradation import WebhookConfig

from harness_runtime.lifecycle.audit_signing_fail_closed_validation import (
    resolve_audit_signing_fail_closed,
)
from harness_runtime.lifecycle.webhook_delivery_composer import WebhookDeliveryComposer
from harness_runtime.lifecycle.webhook_delivery_composer_types import (
    parse_loopback_webhook_endpoint,
)
from harness_runtime.types import RuntimeConfig

if TYPE_CHECKING:
    from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext


class WebhookDeliveryComposerStageMaterializeError(Exception):
    """Raised when `materialize_webhook_delivery_composer_stage` cannot produce
    a `WebhookDeliveryComposer` instance.

    Fail class: `RT-FAIL-WEBHOOK-COMPOSER-STAGE-MATERIALIZE` per spec v1.26
    §14.16.4. Permanent severity — triggers bootstrap rollback per C-RT-02
    (stages 0..4 + sibling stage-5 bindings already constructed). Surfaces
    on opt-in branch only; opt-out branch returns `None` unconditionally and
    cannot raise this class.
    """


async def materialize_webhook_delivery_composer_stage(
    config: RuntimeConfig,
    ctx: _MutableHarnessContext,
) -> WebhookDeliveryComposer | None:
    """Construct the stage-5 `WebhookDeliveryComposer` instance from
    operator-supplied config, or return `None` when the operator has not
    opted in.

    Per spec v1.26 §14.16.2 + §14.16.3.

    Parameters
    ----------
    config : RuntimeConfig
        Runtime config; `config.webhook_delivery_composer_config` is the
        operator opt-in signal.
    ctx : _MutableHarnessContext
        Mutable bootstrap context. Provides the `tracer_provider` carrier from
        stage 4 OD-bucket for span-attribute emission at the composer's
        `deliver_webhook(...)` body per C-RT-20 §14.10.1.

    Returns
    -------
    WebhookDeliveryComposer | None
        `None` when `config.webhook_delivery_composer_config is None` — the
        operator has not opted in; `ctx.webhook_delivery_composer` binds to
        `None`; the §14.8.8.1 step 0 OR-form precondition AND-arm at
        `ctx.webhook_delivery_composer is None` evaluates False (durable-async
        branch falls through to sync-blocking; pre-v1.26 production-default
        state preserved per spec §14.16.5 invariant analog).

        Non-`None` when the operator has supplied a
        `WebhookDeliveryComposerConfig` instance — returns the C-RT-20
        §14.10.1 `WebhookDeliveryComposer` instance bound to
        `ctx.tracer_provider` (when present at stage-5 invocation).

    Raises
    ------
    WebhookDeliveryComposerStageMaterializeError
        Fail class `RT-FAIL-WEBHOOK-COMPOSER-STAGE-MATERIALIZE` per spec
        §14.16.4. An invalid local endpoint, timeout or incomplete pause
        binding is refused before workflow execution.
    """
    operator = config.webhook_delivery_composer_config
    if operator is None:
        # Empty-sentinel branch. Operator opted out;
        # ctx.webhook_delivery_composer binds to None; §14.8.8.1 step 0
        # OR-form precondition AND-arm at ctx.webhook_delivery_composer is
        # None evaluates False (durable-async branch falls through to
        # sync-blocking). Pre-v1.26 production-default state preserved.
        return None

    configured = any(
        field is not None
        for field in (operator.webhook_id, operator.endpoint_url, operator.timeout_seconds)
    )
    webhook_config = None
    if configured:
        try:
            if (
                not isinstance(operator.webhook_id, str)
                or re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", operator.webhook_id) is None
            ):
                raise ValueError("webhook_id must be a non-secret public identifier")
            if not isinstance(operator.endpoint_url, str):
                raise ValueError("endpoint_url is required with webhook_id")
            timeout_seconds = operator.timeout_seconds
            if (
                not isinstance(timeout_seconds, int)
                or isinstance(timeout_seconds, bool)
                or not 1 <= timeout_seconds <= 5
            ):
                raise ValueError("timeout_seconds must be an integer from 1 to 5")
            webhook_config = WebhookConfig(
                webhook_id=operator.webhook_id,
                endpoint_url=parse_loopback_webhook_endpoint(operator.endpoint_url),
                timeout=timeout_seconds,
                degradation_mode="fail-closed",
            )
        except ValueError as exc:
            raise WebhookDeliveryComposerStageMaterializeError(
                f"RT-FAIL-WEBHOOK-COMPOSER-STAGE-MATERIALIZE: {exc}"
            ) from exc
    elif config.pause_resume_protocol_config is not None:
        raise WebhookDeliveryComposerStageMaterializeError(
            "RT-FAIL-WEBHOOK-COMPOSER-STAGE-MATERIALIZE: bound pause needs a webhook endpoint"
        )

    # Construct the C-RT-20 carrier with the stage-4 tracer and the validated
    # local endpoint when supplied. Legacy empty markers stay unconfigured.
    tracer_provider = ctx.tracer_provider
    # R-FS-1 arc CA — thread the run-scoped cost accumulator so webhook
    # SpanCostRecords feed `RunResult.cost_attribution` (runtime v1.53 §9). The
    # v1.26 empty-marker factory binds no cost substrates yet (pre-existing), so
    # the composer's cost wrapper early-returns in production — the sink is
    # forward-ready, dormant until the FM-2 webhook config arc binds substrates.
    return WebhookDeliveryComposer(
        webhook_config=webhook_config,
        # The local profile allows one bounded attempt. Retry behavior needs a
        # separate response-class and deadline contract before production use.
        retry_max_attempts=1 if webhook_config is not None else 3,
        http_client_factory=(
            (lambda: httpx.AsyncClient(follow_redirects=False, trust_env=False))
            if webhook_config is not None
            else None
        ),
        tracer_provider=tracer_provider,
        # B-INTERSTEP-PERRUN-ISOLATION — the run-scoped accumulator PROXY (not its
        # `.records` list) so any appended SpanCostRecord routes to the current
        # run's accumulator at append-time.
        cost_record_sink=ctx.cost_record_accumulator,
        # B-23 — threaded so a future cost-substrate-bound composer (FM-2
        # webhook config arc) F2-writes its cost fact with a real entry_core
        # instead of a fabricated `cp-audit:<action_id>` marker. Dormant at
        # v1.26 (this factory binds no cost substrates yet, so the composer's
        # cost wrapper early-returns), same as `cost_record_sink` above.
        ledger_writer=ctx.ledger_writer,
        procedural_tier_snapshot_resolver=ctx.procedural_tier_snapshot_resolver,
        # B-47 PR B2a — OD spec v1.33 §21.2.1 signing seam.
        signing_backend=ctx.audit_signing_backend,
        # U-RT-136 — OD v1.34 §21.2.3 fail-closed policy (rows 1/5/7).
        audit_signing_fail_closed=resolve_audit_signing_fail_closed(config),
        # B-65-A (Runtime spec v1.103 §14.8.11) — stage-4-constructed
        # protected result store.
        protected_result_store=ctx.protected_result_store,
    )
