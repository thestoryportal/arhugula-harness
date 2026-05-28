"""U-RT-67 — `RuntimeToolDispatcher.dispatch()` body + sandbox span emission.

Per `Spec_Harness_Runtime_v1.md` v1.13 §14.9.1 RuntimeToolDispatcher
dispatch surface + §14.9.2 per-step invocation discipline + §14.9.4 span
emission + §14.9.5 failure-mode taxonomy.

Per `Implementation_Plan_Harness_Runtime_v2_11.md` §1 U-RT-67 (5 ACs).

The dispatcher satisfies the `AsyncStepDispatcher` Protocol
(`sync_dispatcher_facade.py`). Stage 5 wraps it with
`RetryBreakerFallbackDispatcher` (the spec calls for the same registry
key shape as `"llm_dispatch"`; the wrap is materialized at U-RT-68 +
governed by the Class-1 fork resolution recorded at
`.harness/class_1_fork_u_rt_68_retry_wrap_shape_gap.md`).

Composition surface:
- Consumes `MCPClientHost` (U-RT-63) → resolves ToolContract from
  `tool_registry` + invokes `call_tool`.
- Consumes `PerServerTrustEvaluator` (U-CP-68) → per-dispatch gate per
  spec §14.9.2 invariant 2 (no caching).
- Consumes `MCPClientNamespaceEmitter` (U-CP-69) → mutates the
  `mcp.tool.call` span with the 7-attribute `mcp.*` namespace.
- Operator supplies `sandbox_decision_resolver` at __init__ — the
  per-dispatch policy that selects sandbox tier + provider + tech (the
  spec defers to implementation discretion at §14.9.7; the dispatcher
  enforces tier-floor against `ToolContract.minimum_tier` but does not
  derive the tier itself).
"""

from __future__ import annotations

import hashlib
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, cast

import jsonschema

from harness_as.sandbox_fail_class import (
    MCPInvocationFailClass,
    project_mcp_to_sandbox_fail_class,
)
from harness_as.sandbox_tier import SandboxTier
from harness_as.tool_contract import ToolContract
from harness_cp.mcp_client_namespace_emitter import (
    MCPClientNamespaceEmitter,
)
from harness_cp.per_server_trust_evaluator import PerServerTrustEvaluator
from harness_cp.per_server_trust_types import (
    MCPPrimitive,
    TrustPolicy,
)
from harness_cp.workflow_driver_types import (
    StepExecutionContext,
    WorkflowStep,
)
from harness_cp.per_step_override_evaluator import StepEffectiveBinding

from harness_runtime.lifecycle.mcp_client_host import MCPClientHost

__all__ = [
    "MCPHostUnreachableError",
    "RuntimeToolDispatcher",
    "SandboxDecisionResolver",
    "SandboxDispatchDecision",
    "SandboxTierFloorViolationError",
    "ToolContractUnknownError",
    "ToolInvocationProtocolError",
    "ToolInvocationSchemaViolationError",
    "ToolInvocationTimeoutError",
    "ToolInvocationTrustViolationError",
]


# --- Sandbox decision carrier + resolver -----------------------------------


@dataclass(frozen=True)
class SandboxDispatchDecision:
    """Operator-resolved sandbox dispatch policy carrier per spec §14.9.4 +
    C-AS-15 §15 sandbox.* 7-attribute namespace.

    The dispatcher enforces tier-floor (`tier >= contract.minimum_tier`) and
    emits the 7 attributes from this carrier; it does NOT derive the
    decision. Per spec §14.9.7 deferral to implementation discretion.
    """

    tier: SandboxTier
    tech: str  # e.g., "linux-namespaces" / "docker" / "firecracker"
    provider: str  # e.g., "host" / "container-d" / "fly-machines"
    assigned_tier_reason: str  # human-readable cause of tier assignment
    cost_tier_overhead_ms: int  # estimated per-tier startup overhead


SandboxDecisionResolver = Callable[
    [ToolContract, WorkflowStep], SandboxDispatchDecision
]
"""Operator-supplied resolver mapping (contract, step) → dispatch decision.

Per spec §14.9.7 implementation-discretion: the runtime dispatcher
enforces invariants; the resolver carries the deployment-specific tier-
assignment policy. Default resolver raises on production misconfig
(mirrors U-CP-68 `_default_tier_resolver` + U-CP-69
`_default_info_lookup` loud-on-misconfig discipline).
"""


def _default_sandbox_decision_resolver(
    _contract: ToolContract, _step: WorkflowStep
) -> SandboxDispatchDecision:
    raise LookupError(
        "default SandboxDecisionResolver invoked — operator must supply a "
        "sandbox_decision_resolver at RuntimeToolDispatcher.__init__ that "
        "maps (tool_contract, step) to a SandboxDispatchDecision carrying "
        "the per-deployment tier + tech + provider + assigned_tier_reason + "
        "cost_tier_overhead_ms per C-AS-15 §15"
    )


# --- Typed fail classes (spec §14.9.5) -------------------------------------


class ToolContractUnknownError(LookupError):
    """`RT-FAIL-TOOL-CONTRACT-UNKNOWN` typed carrier per spec §14.9.5.

    Raised when `step.step_payload["tool_id"]` is not registered in the
    `MCPClientHost.tool_registry`. Permanent — the driver maps to
    `step-failure: RT-FAIL-TOOL-CONTRACT-UNKNOWN: ...`.
    """


class ToolInvocationTrustViolationError(PermissionError):
    """`RT-FAIL-TOOL-INVOCATION-TRUST-VIOLATION` typed carrier per spec §14.9.5.

    Raised when `PerServerTrustEvaluator.evaluate()` returns
    `permitted=False`. Permanent — does not retry.
    """


class ToolInvocationTimeoutError(TimeoutError):
    """`RT-FAIL-TOOL-INVOCATION-TIMEOUT` typed carrier per spec §14.9.5.

    Raised when `MCPClientHost.call_tool()` exceeds the tool-contract
    timeout. Retryable per C-RT-16.
    """


class ToolInvocationProtocolError(RuntimeError):
    """`RT-FAIL-TOOL-INVOCATION-PROTOCOL-ERROR` typed carrier per spec §14.9.5.

    Raised when MCP protocol error from the underlying transport. Permanent.
    """


class ToolInvocationSchemaViolationError(ValueError):
    """`RT-FAIL-TOOL-INVOCATION-SCHEMA-VIOLATION` typed carrier per spec §14.9.5.

    Raised when `call_tool` response fails `ToolContract.output_schema`
    validation. Permanent.
    """


class MCPHostUnreachableError(RuntimeError):
    """`RT-FAIL-MCP-HOST-UNREACHABLE` typed carrier per spec §14.9.5.

    Raised when `MCPClientHost.health_check()` reports `alive=False`
    mid-dispatch. Transient — retryable per C-RT-16.
    """


class SandboxTierFloorViolationError(RuntimeError):
    """`RT-FAIL-SANDBOX-TIER-FLOOR-VIOLATION` typed carrier per spec §14.9.5.

    Raised when the resolved `SandboxDispatchDecision.tier` is below the
    `ToolContract.minimum_tier`. Permanent (policy breach).
    """


# --- sandbox.* + tool.dispatch attribute name constants --------------------

ATTR_SANDBOX_TIER = "sandbox.tier"
ATTR_SANDBOX_TECH = "sandbox.tech"
ATTR_SANDBOX_PROVIDER = "sandbox.provider"
ATTR_SANDBOX_POLICY_ASSIGNED_TIER_REASON = "sandbox.policy.assigned_tier_reason"
ATTR_SANDBOX_COST_TIER_OVERHEAD_MS = "sandbox.cost.tier_overhead_ms"
ATTR_SANDBOX_FAIL_CLASS = "sandbox.fail.class"
ATTR_MCP_FAIL_CLASS = "mcp.fail.class"
ATTR_IDEMPOTENCY_KEY = "idempotency_key"

ATTR_TOOL_CONTRACT_NAME = "tool.contract.name"
ATTR_STEP_ID = "step.id"
ATTR_STEP_KIND = "step.step_kind"


_SANDBOX_TIER_RANK: Mapping[SandboxTier, int] = {
    SandboxTier.TIER_1_PROCESS: 1,
    SandboxTier.TIER_2_CONTAINER: 2,
    SandboxTier.TIER_3_MICROVM: 3,
    SandboxTier.TIER_4_FULL_VM: 4,
}


class RuntimeToolDispatcher:
    """Per-step TOOL_STEP dispatcher (C-RT-19 §14.9.1 surface).

    Satisfies the `AsyncStepDispatcher` Protocol. Stage 5 binds via
    `ctx.tool_dispatcher`; the step-dispatcher registry resolves
    `TOOL_STEP → ctx.tool_dispatcher`.

    Per spec §14.9.6:
    - inv 3: trust evaluated every dispatch (no caching)
    - inv 4: schema validation at both directions
    - inv 6: no retry inside the dispatcher (handled at C-RT-16 wrap)
    """

    def __init__(
        self,
        *,
        mcp_client_host: MCPClientHost,
        per_server_trust_evaluator: PerServerTrustEvaluator,
        mcp_namespace_emitter: MCPClientNamespaceEmitter,
        trust_policy: TrustPolicy,
        sandbox_decision_resolver: SandboxDecisionResolver | None = None,
        tracer_provider: Any = None,
    ) -> None:
        """Construct dispatcher with the cross-axis dependencies.

        Parameters
        ----------
        mcp_client_host:
            U-RT-63/64/65/66 client. The dispatcher reads `tool_registry`
            for contract resolution + invokes `call_tool` for execution.
        per_server_trust_evaluator:
            U-CP-68 evaluator. Invoked pre-call per spec §14.9.2 inv 2.
        mcp_namespace_emitter:
            U-CP-69 emitter. Mutates the `mcp.tool.call` span with the
            7-attribute `mcp.*` namespace per C-AS-14 §14.3.
        trust_policy:
            Immutable `TrustPolicy` loaded at bootstrap; passed to every
            `evaluate()` call (caching is FORBIDDEN per spec §14.9.2 inv 2
            since operators may revoke between dispatches).
        sandbox_decision_resolver:
            Operator-supplied resolver (default raises on production
            misconfig). Returns the `SandboxDispatchDecision` per dispatch.
        tracer_provider:
            OTel `TracerProvider`-shaped object (typed `Any` to avoid SDK
            coupling per C-RT-04 pattern). Used to open `tool.dispatch` +
            `sandbox.enter` + `mcp.tool.call` + `sandbox.exit` spans. If
            `None`, span emission is skipped (test-injection seam).
        """
        self._mcp_client_host = mcp_client_host
        self._trust_evaluator = per_server_trust_evaluator
        self._mcp_emitter = mcp_namespace_emitter
        self._trust_policy = trust_policy
        self._sandbox_resolver: SandboxDecisionResolver = (
            sandbox_decision_resolver or _default_sandbox_decision_resolver
        )
        self._tracer_provider = tracer_provider

    def _emit_sandbox_violation(
        self,
        tracer: Any,
        mcp_fail_class: MCPInvocationFailClass,
        idempotency_key: str,
    ) -> None:
        """Open the `sandbox.violation` child span with fail-class + idempotency attrs.

        Per AS spec v1.6 §15.9 dual-attribute emission discipline: the
        `sandbox.violation` event carries BOTH `mcp.fail.class` (direct from
        §15.8 enum) AND `sandbox.fail.class` (F4 projected via §15.10).
        Per §15.6 row 1 idempotency-key join: the event also carries the
        parent `tool.call` `idempotency_key` as the cross-axis join key
        for cost-attribution (D6) and engine event history (D1).
        """
        if tracer is None:
            return
        projected = project_mcp_to_sandbox_fail_class(mcp_fail_class)
        with tracer.start_as_current_span("sandbox.violation") as span:
            _set(span, ATTR_MCP_FAIL_CLASS, mcp_fail_class.value)
            _set(span, ATTR_SANDBOX_FAIL_CLASS, projected.value)
            _set(span, ATTR_IDEMPOTENCY_KEY, idempotency_key)

    async def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: StepExecutionContext,
    ) -> Mapping[str, Any]:
        """Invoke the TOOL_STEP body per spec §14.9.1 11-step sequence.

        Per the `AsyncStepDispatcher` Protocol the `step_context` carries
        per-step parent context; this dispatcher consumes
        `parent_idempotency_key` for idempotency-key composition (step 6).
        `binding` is reserved for future per-step override surfaces (e.g.,
        per-step trust-tier overrides at C-CP-19); not consumed at MVP.

        :returns: `Mapping[str, Any]` (step body output) per
            `AsyncStepDispatcher` Protocol contract.
        """
        _ = binding  # reserved for v1.14+ per-step override surfaces

        payload = step.step_payload
        tool_id_raw = payload.get("tool_id")
        if not isinstance(tool_id_raw, str) or not tool_id_raw:
            raise ToolContractUnknownError(
                f"TOOL_STEP payload missing or non-str 'tool_id' "
                f"(step_id={step.step_id!r}, payload_keys="
                f"{sorted(payload.keys())})"
            )
        tool_id: str = tool_id_raw
        tool_args_raw: Any = payload.get("tool_args")
        if tool_args_raw is None:
            tool_args: Mapping[str, Any] = {}
        elif isinstance(tool_args_raw, Mapping):
            tool_args = cast("Mapping[str, Any]", tool_args_raw)
        else:
            raise ToolContractUnknownError(
                f"TOOL_STEP 'tool_args' must be a mapping "
                f"(got {type(tool_args_raw).__name__})"
            )

        # --- Step 1: resolve ToolContract from registry ---------------------
        try:
            contract: ToolContract = self._mcp_client_host.tool_registry.get(
                tool_id  # type: ignore[arg-type]
            )
        except Exception as exc:
            raise ToolContractUnknownError(
                f"RT-FAIL-TOOL-CONTRACT-UNKNOWN: tool_id={tool_id!r} not "
                f"registered at MCPClientHost(server="
                f"{self._mcp_client_host.server_name!r})"
            ) from exc

        # --- Step 2: per-server-trust gate (no caching per inv 2) -----------
        trust_eval = await self._trust_evaluator.evaluate(
            self._mcp_client_host.server_name,
            MCPPrimitive.TOOL,
            contract,
            self._trust_policy,
        )
        if not trust_eval.permitted:
            raise ToolInvocationTrustViolationError(
                f"RT-FAIL-TOOL-INVOCATION-TRUST-VIOLATION: server="
                f"{self._mcp_client_host.server_name!r} tool={tool_id!r} "
                f"decision_reason={trust_eval.decision_reason.value}"
            )

        # --- Step 3-5: open tool.dispatch + sandbox.enter; tier-floor -------
        tracer = (
            self._tracer_provider.get_tracer("harness.runtime.tool_dispatch")
            if self._tracer_provider is not None
            else None
        )
        sandbox_decision = self._sandbox_resolver(contract, step)
        # Tier-floor enforcement per spec §14.9.6 inv 2.
        if (
            _SANDBOX_TIER_RANK[sandbox_decision.tier]
            < _SANDBOX_TIER_RANK[contract.minimum_tier]
        ):
            raise SandboxTierFloorViolationError(
                f"RT-FAIL-SANDBOX-TIER-FLOOR-VIOLATION: tool={tool_id!r} "
                f"resolved_tier={sandbox_decision.tier.value} "
                f"< minimum_tier={contract.minimum_tier.value}"
            )

        outer_span_cm = (
            tracer.start_as_current_span("tool.dispatch")
            if tracer is not None
            else _null_span_cm()
        )
        with outer_span_cm as outer_span:
            _set(outer_span, ATTR_STEP_ID, step.step_id)
            _set(outer_span, ATTR_STEP_KIND, step.step_kind.value)
            _set(outer_span, ATTR_TOOL_CONTRACT_NAME, contract.name)

            sandbox_enter_cm = (
                tracer.start_as_current_span("sandbox.enter")
                if tracer is not None
                else _null_span_cm()
            )
            with sandbox_enter_cm as sandbox_enter_span:
                _set(sandbox_enter_span, ATTR_SANDBOX_TIER, sandbox_decision.tier.value)
                _set(sandbox_enter_span, ATTR_SANDBOX_TECH, sandbox_decision.tech)
                _set(sandbox_enter_span, ATTR_SANDBOX_PROVIDER, sandbox_decision.provider)
                _set(
                    sandbox_enter_span,
                    ATTR_SANDBOX_POLICY_ASSIGNED_TIER_REASON,
                    sandbox_decision.assigned_tier_reason,
                )
                _set(
                    sandbox_enter_span,
                    ATTR_SANDBOX_COST_TIER_OVERHEAD_MS,
                    sandbox_decision.cost_tier_overhead_ms,
                )
                _set(sandbox_enter_span, ATTR_SANDBOX_FAIL_CLASS, "")

            # --- Step 6: compose idempotency key (per parent step) ----------
            idempotency_key = _compose_idempotency_key(
                step_context.parent_idempotency_key, step.step_id, tool_id
            )

            # --- Step 7: invoke + mcp.tool.call span emission ---------------
            # Per AS spec v1.6 §15.9 dual-attribute emission: any MCP-protocol
            # exception opens a `sandbox.violation` child span carrying BOTH
            # `mcp.fail.class` (§15.8 direct) AND `sandbox.fail.class` (F4
            # projected via §15.10) before re-raise. The producer-side
            # mapping owned at this dispatcher per runtime spec §14.9.
            mcp_call_cm = (
                tracer.start_as_current_span("mcp.tool.call")
                if tracer is not None
                else _null_span_cm()
            )
            try:
                with mcp_call_cm as mcp_call_span:
                    # Mutate span with the 7-attribute mcp.* namespace.
                    signature_hash = _compute_primitive_signature_hash(
                        contract.name, contract.input_schema, contract.output_schema
                    )
                    if mcp_call_span is not None:
                        self._mcp_emitter.emit_mcp_call_span(
                            mcp_call_span,
                            self._mcp_client_host.server_name,
                            MCPPrimitive.TOOL,
                            signature_hash,
                        )
                    response = await self._mcp_client_host.call_tool(
                        tool_id, tool_args, idempotency_key
                    )
            except ToolInvocationTimeoutError:
                self._emit_sandbox_violation(
                    tracer, MCPInvocationFailClass.TIMEOUT, idempotency_key
                )
                raise
            except ToolInvocationProtocolError:
                self._emit_sandbox_violation(
                    tracer, MCPInvocationFailClass.PROTOCOL_ERROR, idempotency_key
                )
                raise
            except MCPHostUnreachableError:
                self._emit_sandbox_violation(
                    tracer, MCPInvocationFailClass.TRANSPORT, idempotency_key
                )
                raise

            # --- Step 8: response schema validation -------------------------
            try:
                _validate_response_schema(response, contract.output_schema)
            except jsonschema.ValidationError as exc:
                self._emit_sandbox_violation(
                    tracer, MCPInvocationFailClass.SCHEMA_VIOLATION, idempotency_key
                )
                raise ToolInvocationSchemaViolationError(
                    f"RT-FAIL-TOOL-INVOCATION-SCHEMA-VIOLATION: tool="
                    f"{tool_id!r} response failed output_schema validation: "
                    f"{exc.message}"
                ) from exc

            # --- Step 9-10: sandbox.exit span (success path) ----------------
            sandbox_exit_cm = (
                tracer.start_as_current_span("sandbox.exit")
                if tracer is not None
                else _null_span_cm()
            )
            with sandbox_exit_cm as sandbox_exit_span:
                _set(sandbox_exit_span, ATTR_SANDBOX_FAIL_CLASS, "")

            # --- Step 11: wrap response + return ----------------------------
            return {
                "tool_id": tool_id,
                "response": response,
                "idempotency_key": idempotency_key,
                "trust_decision_reason": trust_eval.decision_reason.value,
                "sandbox_tier": sandbox_decision.tier.value,
            }


# --- private helpers -------------------------------------------------------


def _set(span: Any, key: str, value: Any) -> None:
    """Conditional set_attribute (null-span tolerant)."""
    if span is None:
        return
    span.set_attribute(key, value)


class _NullSpanContext:
    def __enter__(self) -> None:
        return None

    def __exit__(self, *_args: Any) -> None:
        return None


def _null_span_cm() -> _NullSpanContext:
    return _NullSpanContext()


def _compose_idempotency_key(
    parent_idempotency_key: str, step_id: str, tool_id: str
) -> str:
    """Per spec §14.9.7 suggested recipe — sha256 over parent key + step + tool."""
    digest = hashlib.sha256()
    digest.update(parent_idempotency_key.encode("utf-8"))
    digest.update(b":")
    digest.update(step_id.encode("utf-8"))
    digest.update(b":")
    digest.update(tool_id.encode("utf-8"))
    return digest.hexdigest()


def _compute_primitive_signature_hash(
    name: str,
    input_schema: Mapping[str, Any],
    output_schema: Mapping[str, Any],
) -> str:
    """Per C-AS-14 §14.3 tool-poisoning detection: sha256 over the
    primitive's name + input schema + output schema (sorted JSON)."""
    import json

    digest = hashlib.sha256()
    digest.update(name.encode("utf-8"))
    digest.update(b"|")
    digest.update(json.dumps(input_schema, sort_keys=True).encode("utf-8"))
    digest.update(b"|")
    digest.update(json.dumps(output_schema, sort_keys=True).encode("utf-8"))
    return digest.hexdigest()


def _validate_response_schema(
    response: Mapping[str, Any], output_schema: Mapping[str, Any]
) -> None:
    """Validate `response` against JSON Schema `output_schema`.

    Empty schema ({}) bypasses validation. Per spec §14.9.2 inv 4 the
    dispatcher validates BOTH directions; input validation is the
    operator's responsibility at the workflow-driver layer (the dispatcher
    enforces post-call shape only — the inbound `tool_args` already
    crossed the workflow boundary).
    """
    if not output_schema:
        return
    jsonschema.validate(instance=dict(response), schema=dict(output_schema))


# `time` imported above is intentional — reserved for future per-attempt
# latency emission at the C-RT-16 wrap layer per spec §14.9.7 deferral.
_ = time
