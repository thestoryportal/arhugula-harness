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

from harness_as.tool_contract import ToolContract
from harness_core import SandboxDecisionPolicy
from harness_cp.cp_shared_types import MCPTrustTier
from harness_cp.mcp_client_namespace_emitter import (
    MCPClientNamespaceEmitter,
    MCPServerInfo,
    MCPServerInfoLookup,
)
from harness_cp.per_server_trust_evaluator import PerServerTrustEvaluator
from harness_cp.per_server_trust_types import (
    TierDerivationRule,
    TrustPolicy,
)
from harness_cp.workflow_driver_types import WorkflowStep

from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.lifecycle.as_is_wiring import RuntimeAsIsWiring
from harness_runtime.lifecycle.mcp_client_host import MCPClientHost
from harness_runtime.lifecycle.retry_breaker_tool import RetryBreakerToolDispatcher
from harness_runtime.lifecycle.runtime_tool_dispatcher import (
    RuntimeToolDispatcher,
    SandboxDecisionResolver,
    SandboxDispatchDecision,
)
from harness_runtime.types import MCPClientConfig, RuntimeConfig

__all__ = [
    "DEFAULT_TRUST_POLICY",
    "materialize_runtime_tool_dispatcher_stage",
]


def _build_default_policy_sandbox_resolver(entry: MCPClientConfig) -> SandboxDecisionResolver:
    """Build a Reading-B per-server default-policy `SandboxDecisionResolver`
    (spec v1.41 §14.9.8, Gap C).

    Returns the operator-declared per-server sandbox decision for EVERY
    `(contract, step)` on this server (per-server-uniform per §14.9.8). The
    resolved `tier` is compared against `contract.minimum_tier` at the §14.9.4
    tier-floor check — so the operator must declare `default_sandbox_tier`
    consistently with `default_minimum_tier`.
    """
    tier = entry.default_sandbox_tier
    tech = entry.default_sandbox_tech
    provider = entry.default_sandbox_provider

    def resolve(_contract: ToolContract, _step: WorkflowStep) -> SandboxDispatchDecision:
        return SandboxDispatchDecision(
            tier=tier,
            tech=tech,
            provider=provider,
            assigned_tier_reason="per-server-default-sandbox-policy",
            cost_tier_overhead_ms=0,
        )

    return resolve


def _build_host_info_lookup(host: MCPClientHost) -> MCPServerInfoLookup:
    """Build a sync `MCPServerInfoLookup` from a started `MCPClientHost`
    (spec v1.41 §14.9.8 arc, Gap E).

    The emitter's `info_lookup` is sync and fires per dispatch (step 7); it
    reads the host's already-resolved fields (no async `health_check`). All
    four `MCPServerInfo` fields are host-derivable. The lookup ignores its
    `server_name` argument at the v1 single-server MVP (one host per bootstrap
    per §14.9.6 inv 1).
    """

    def lookup(_server_name: str) -> MCPServerInfo:
        return MCPServerInfo(
            transport=host.transport,
            protocol_version=host.protocol_version,
            auth_present=host.auth_present,
            trust_tier=host.trust_tier,
        )

    return lookup


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
    assert ctx.ledger_writer is not None, (
        "stage 1 IS must populate ctx.ledger_writer before stage 5 TOOL_STEP dispatch"
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

    # --- Step 2: MCP namespace emitter (Gap E — info_lookup from host) -------
    # spec v1.41 §14.9.8 arc: the emitter's per-dispatch step-7 info_lookup is
    # wired from ctx.mcp_client_host so it does not raise on the operator
    # api.run path. Bare `MCPClientNamespaceEmitter()` (default-raise lookup)
    # is preserved only when no host is configured (empty-sentinel; dispatch
    # never reaches step 7 because step 1 raises TOOL-CONTRACT-UNKNOWN first).
    info_lookup: MCPServerInfoLookup | None = (
        _build_host_info_lookup(ctx.mcp_client_host) if config.mcp_clients else None
    )
    mcp_namespace_emitter = MCPClientNamespaceEmitter(info_lookup=info_lookup)
    ctx.mcp_namespace_emitter = mcp_namespace_emitter

    # --- Step 2b: per-server default-policy sandbox resolver (Gap C) ----------
    # spec v1.41 §14.9.8 Reading B: build the resolver from the first server's
    # operator-declared per-server sandbox policy. None when no server is
    # configured (the bare dispatcher's default-raise resolver is unreachable
    # at step 3 because step 1 raises first on the empty registry).
    sandbox_decision_resolver: SandboxDecisionResolver | None = (
        _build_default_policy_sandbox_resolver(config.mcp_clients[0])
        if config.mcp_clients
        else None
    )

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
        sandbox_decision_resolver=sandbox_decision_resolver,
        tracer_provider=ctx.tracer_provider,
        cost_chain=ctx.cost_chain,
        audit_writer=ctx.audit_writer,
        rate_table=rate_table,
        provider_secret_resolver=ctx.keyring_resolver,
        secret_fetch_audit_emitter=RuntimeAsIsWiring(
            ctx.ledger_writer
        ).emit_secret_fetch_audit_entry,
        secret_fetch_backend=config.provider_secrets.backend.value,
    )

    # --- Step 4: RetryBreakerToolDispatcher (C-RT-21 §14.11) -----------------
    wrapper = RetryBreakerToolDispatcher(
        inner=bare_dispatcher,
        retry_breaker=ctx.retry_breaker,
        tracer_provider=ctx.tracer_provider,
    )

    # --- Step 5: return wrapper (caller binds to ctx.tool_dispatcher) --------
    return wrapper
