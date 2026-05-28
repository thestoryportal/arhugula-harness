"""Stage 5 factory — `materialize_runtime_tool_dispatcher_stage(ctx, config)
→ RetryBreakerToolDispatcher`.

Per `Spec_Harness_Runtime_v1.md` v1.16 §14.9.3 stage-5 factory contract +
§14.11 C-RT-21 (added at v1.15 per U-RT-68 fork Q1=B + Q2=B2 ratification).

5-step composition body per spec §14.9.3 stage-5 prose:

  1. Construct `PerServerTrustEvaluator` (consumes `config.trust_policy`,
     or a runtime-supplied conservative default if `None`).
  2. Construct `MCPClientNamespaceEmitter` (consumes `ctx.mcp_client_host`
     downstream at `emit_mcp_call_span` time; the emitter is constructed
     with a default info-lookup at MVP — operator override is future arc).
  3. Construct the bare `RuntimeToolDispatcher` (C-RT-19) with refs to
     `ctx.mcp_client_host` + the new evaluator + the new emitter + the
     trust policy + `config.sandbox_decision_policy` (or
     `SandboxDecisionPolicy.default()` if `None`).
  4. Construct the `RetryBreakerToolDispatcher` (C-RT-21 §14.11)
     wrapping the bare dispatcher with `inner=<bare>` +
     `retry_breaker=ctx.retry_breaker` + `tracer_provider=ctx.tracer_provider`.
  5. Return the wrapper. The caller (U-RT-68 stage-5 wire-up at
     `stage_5_loop_init.py`) binds the wrapper to `ctx.tool_dispatcher`;
     intermediate carriers (evaluator + emitter) are bound to
     `ctx.per_server_trust_evaluator` + `ctx.mcp_namespace_emitter` by
     this factory (mutates `ctx` directly).

The bare `RuntimeToolDispatcher` is private to the wrapper per spec
§14.9.6 invariant 6 — not surfaced on `HarnessContext`.
"""

from __future__ import annotations

from typing import Any

from harness_core import SandboxDecisionPolicy
from harness_cp.cp_shared_types import MCPTrustTier
from harness_cp.mcp_client_namespace_emitter import MCPClientNamespaceEmitter
from harness_cp.per_server_trust_evaluator import PerServerTrustEvaluator
from harness_cp.per_server_trust_types import (
    TierDerivationRule,
    TrustPolicy,
)

from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.lifecycle.retry_breaker_tool import RetryBreakerToolDispatcher
from harness_runtime.lifecycle.runtime_tool_dispatcher import RuntimeToolDispatcher
from harness_runtime.types import RuntimeConfig

__all__ = [
    "DEFAULT_TRUST_POLICY",
    "materialize_runtime_tool_dispatcher_stage",
]


DEFAULT_TRUST_POLICY = TrustPolicy(
    default_tier=MCPTrustTier.LEVEL_0_REFUSE_REMOTE,
    per_server_overrides={},
    allow_list=frozenset(),
    deny_list=frozenset(),
    require_audit_below_tier=MCPTrustTier.LEVEL_3_ALLOW_WITH_AUDIT,
    tier_derivation=TierDerivationRule.CONSERVATIVE,
)
"""Runtime-supplied conservative default `TrustPolicy` per spec §14.11
"TrustPolicy.default() if None" prose — refuses all unknown remote servers
+ requires audit below the highest non-refuse tier."""


async def materialize_runtime_tool_dispatcher_stage(
    ctx: _MutableHarnessContext,
    config: RuntimeConfig,
    *,
    rate_table: Any = None,
) -> RetryBreakerToolDispatcher:
    """Compose the C-RT-21 retry-wrap around the bare C-RT-19 tool dispatcher.

    Mutates `ctx` in-place: binds `ctx.per_server_trust_evaluator` and
    `ctx.mcp_namespace_emitter` to the constructed sibling carriers. The
    caller (U-RT-68) binds the returned wrapper to `ctx.tool_dispatcher`.

    Per spec v1.16 §14.9.3 stage-5 factory contract + U-RT-75 AC
    (Implementation_Plan_Harness_Runtime_v2_13.md).
    """
    assert ctx.mcp_client_host is not None, (
        "stage 3a (U-RT-73) must populate ctx.mcp_client_host before stage 5"
    )
    assert ctx.retry_breaker is not None, (
        "stage 3b (U-RT-24) must populate ctx.retry_breaker before stage 5"
    )

    trust_policy = config.trust_policy if config.trust_policy is not None else DEFAULT_TRUST_POLICY
    sandbox_decision_policy = (
        config.sandbox_decision_policy
        if config.sandbox_decision_policy is not None
        else SandboxDecisionPolicy.default()
    )
    # `sandbox_decision_policy` is committed to the bare dispatcher's
    # interface via the runtime spec v1.16 §3 contract, but the existing
    # C-RT-19 dispatcher predates the field and does not yet consume it
    # (§14.9.1 step 5 reads only `sandbox.tier ≥ ToolContract.minimum_tier`
    # — dangling marker per spec v1.16 finding (i)). The policy is
    # received here for spec-contract conformance + future-arc consumption.
    _ = sandbox_decision_policy

    # --- Step 1: per-server trust evaluator ----------------------------------
    per_server_trust_evaluator = PerServerTrustEvaluator()
    ctx.per_server_trust_evaluator = per_server_trust_evaluator

    # --- Step 2: MCP namespace emitter ---------------------------------------
    mcp_namespace_emitter = MCPClientNamespaceEmitter()
    ctx.mcp_namespace_emitter = mcp_namespace_emitter

    # --- Step 3: bare RuntimeToolDispatcher (C-RT-19) ------------------------
    # U-OD-39: thread cost-attribution substrate (cost_chain + audit_writer
    # from ctx; rate_table from caller kwarg sourced from RATE_TABLE_V1 at
    # stage_5_loop_init.py). All 3 None-safe at unit-test path; production
    # bootstrap binds all 3 per `_attribute_tool_cost_best_effort` semantics.
    bare_dispatcher = RuntimeToolDispatcher(
        mcp_client_host=ctx.mcp_client_host,
        per_server_trust_evaluator=per_server_trust_evaluator,
        mcp_namespace_emitter=mcp_namespace_emitter,
        trust_policy=trust_policy,
        tracer_provider=ctx.tracer_provider,
        cost_chain=ctx.cost_chain,
        audit_writer=ctx.audit_writer,
        rate_table=rate_table,
    )

    # --- Step 4: RetryBreakerToolDispatcher (C-RT-21 §14.11) -----------------
    wrapper = RetryBreakerToolDispatcher(
        inner=bare_dispatcher,
        retry_breaker=ctx.retry_breaker,
        tracer_provider=ctx.tracer_provider,
    )

    # --- Step 5: return wrapper (caller binds to ctx.tool_dispatcher) --------
    return wrapper
