"""U-RT-84 — ValidatorFramework stage-4 factory.

Implements runtime spec v1.18 §14.13.1 factory signature + §14.13.2 per-factory
invocation discipline + §14.13.3 stage-4 OD-bucket placement + §14.13.4
failure-mode taxonomy + §14.13.5 invariants.

- Opt-out branch (`config.validator_framework_config is None`) returns `None`
  unconditionally — preserves v1.17 production-default behavior; the
  workflow_driver.py:668 hook branch evaluates False.
- Opt-in branch (non-None config) builds the per-step validator registry from
  the operator's `ValidatorBinding`s (spec §14.13.7 implementer-discretion
  catalog): each class-qualified name resolves through the memory
  OPERATOR_DEFINED introspection discipline (spec §14.13.1), is constructed
  with its scalar params, and must satisfy the `Validator` Protocol with an
  async `validate` before the populated registry reaches
  `ConcreteValidatorFramework`. Any refusal raises
  `ValidatorFrameworkStageMaterializeError` (fail class
  `RT-FAIL-VALIDATOR-STAGE-MATERIALIZE`, permanent severity → bootstrap
  rollback per C-RT-02), so no workflow dispatches against a validator that
  could not run.
- `@runtime_checkable ValidatorFramework` Protocol-conformance enforced per
  spec §14.13.5 invariant 3.
- The return value is the CP async Protocol instance itself (Runtime v1.138
  §14.13.2/.5); it holds no per-run state. Each `run_workflow` invocation
  opens its own synchronous `ValidatorRunBinding` over it (§14.13.8).
- U-RT-85 real-bootstrap ValidatorFramework e2e binds through this factory:
  opt-in config materializes the operator-supplied framework slot on the
  runtime context before the workflow-driver validator hook can fire.
"""

from __future__ import annotations

import inspect
from typing import Any

from harness_core.identity import StepID
from harness_cp.validator_framework import ConcreteValidatorFramework
from harness_cp.validator_framework_types import (
    Validator,
    ValidatorFramework,
    ValidatorPostEvaluateHook,
)
from harness_od.rate_table_types import RateTable

from harness_runtime.bootstrap.factories.memory_tool_registry_factory import (
    _resolve_class_qualified_name,  # pyright: ignore[reportPrivateUsage]
)
from harness_runtime.lifecycle.audit_signing_errors import AUDIT_SIGNING_HARD_FAILURES
from harness_runtime.lifecycle.cost_attribution_validator_dispatch import (
    CostAttributingValidatorHook,
)
from harness_runtime.lifecycle.cost_record_sink import SupportsCostRecordAppend
from harness_runtime.lifecycle.memory_tool_types import MemoryBackendResolutionError
from harness_runtime.lifecycle.validator_framework_types import ValidatorBinding
from harness_runtime.types import AuditLedgerWriter, CostAttributionChain, RuntimeConfig


class ValidatorFrameworkStageMaterializeError(Exception):
    """Raised when `materialize_validator_framework_stage` cannot produce a
    Protocol-satisfying `ValidatorFramework` instance.

    Fail class: `RT-FAIL-VALIDATOR-STAGE-MATERIALIZE` per spec v1.18 §14.13.4.
    Permanent severity — triggers bootstrap rollback of stages 0..3b per
    C-RT-02. Surfaces on opt-in branch only; opt-out branch returns `None`
    unconditionally and cannot raise this class.
    """


def _instantiate_bound_validator(binding: ValidatorBinding) -> Validator:
    """Resolve, construct and conformance-check one operator validator.

    The returned instance is proof that the binding can be dispatched: its
    class resolved, `cls(**params)` accepted the configured params, and it
    exposes an async `validate` per the CP `Validator` Protocol.
    """
    subject = f"validator {binding.class_qualified_name!r} for step {binding.step_id!r}"
    try:
        # [LAW:one-source-of-truth] spec §14.13.1 requires the memory
        # OPERATOR_DEFINED introspection discipline; reuse it, not a copy.
        validator_cls = _resolve_class_qualified_name(binding.class_qualified_name)
    except MemoryBackendResolutionError as exc:
        raise ValidatorFrameworkStageMaterializeError(
            f"RT-FAIL-VALIDATOR-STAGE-MATERIALIZE: {subject} did not resolve: {exc}"
        ) from exc
    try:
        instance: object = validator_cls(**binding.params)
    except Exception as exc:
        # Mirrors the OPERATOR_DEFINED memory backend: params are not echoed;
        # the operator's exception stays chained for traceback debugging.
        raise ValidatorFrameworkStageMaterializeError(
            f"RT-FAIL-VALIDATOR-STAGE-MATERIALIZE: {subject} raised "
            f"{type(exc).__name__} during construction (params values are not echoed)"
        ) from exc
    # `isinstance` against a runtime_checkable Protocol only proves the
    # attribute exists; the driver awaits `validate`, so it must be async.
    if not isinstance(instance, Validator) or not inspect.iscoroutinefunction(instance.validate):
        raise ValidatorFrameworkStageMaterializeError(
            f"RT-FAIL-VALIDATOR-STAGE-MATERIALIZE: {subject} does not satisfy the "
            "Validator Protocol (an async validate(step, step_result, *, step_context))"
        )
    return instance


async def materialize_validator_framework_stage(
    config: RuntimeConfig,
    *,
    rate_table: RateTable | None = None,
    cost_chain: CostAttributionChain | None = None,
    audit_writer: AuditLedgerWriter | None = None,
    cost_record_sink: SupportsCostRecordAppend | None = None,
    ledger_writer: Any = None,
    procedural_tier_snapshot_resolver: Any = None,
    signing_backend: Any = None,
    audit_signing_fail_closed: bool = False,
) -> ValidatorFramework | None:
    """Construct the stage-4 `ValidatorFramework` instance from operator-supplied
    config, or return `None` when the operator has not opted in.

    Per spec v1.18 §14.13.1 + §14.13.2.

    Returns
    -------
    ValidatorFramework | None
        `None` when `config.validator_framework_config is None` — the
        operator has not opted in; `ctx.validator_framework` binds to `None`;
        the workflow_driver.py:668 hook branch evaluates False (the v1.17
        production-default state).

        Non-`None` when the operator has supplied a `ValidatorFrameworkConfig`
        — the driver-facing sync facade over a `ConcreteValidatorFramework`
        whose registry holds one constructed operator validator per bound
        step. Must be awaited on the event loop that later hosts
        `asyncio.to_thread(execute_workflow, ...)`.

    Raises
    ------
    ValidatorFrameworkStageMaterializeError
        Fail class `RT-FAIL-VALIDATOR-STAGE-MATERIALIZE` per spec §14.13.4 —
        if a binding's class does not resolve, construct or satisfy the
        `Validator` Protocol, or if the constructed framework fails
        `@runtime_checkable ValidatorFramework` Protocol-conformance per spec
        §14.13.5 invariant 3.
    """
    if config.validator_framework_config is None:
        # Empty-sentinel branch. Operator opted out; ctx.validator_framework
        # binds to None; driver hook dead-branch at workflow_driver.py:668
        # is unreachable per the False arm. Preserves v1.17 production-default
        # behavior per spec §14.13.5 invariant 2.
        return None

    # Operator opt-in branch: every binding becomes a dispatchable validator
    # before stage 4 completes; the carrier already refused empty catalogs
    # and duplicate step ids.
    validator_registry: dict[StepID, Validator] = {
        binding.step_id: _instantiate_bound_validator(binding)
        for binding in config.validator_framework_config.bindings
    }

    # U-OD-40 hook binding (CP spec v1.24 §28.10 + this factory's mechanism
    # (a) per §28.10.5): when all 3 cost-attribution substrates are bound
    # (rate_table + cost_chain + audit_writer), construct the
    # CostAttributingValidatorHook and inject via ConcreteValidatorFramework's
    # optional post_evaluate_hook ctor param. If any substrate is None,
    # hook=None preserves pre-v1.24 behavior (cost attribution disabled).
    post_evaluate_hook: ValidatorPostEvaluateHook | None = None
    if rate_table is not None and cost_chain is not None and audit_writer is not None:
        post_evaluate_hook = CostAttributingValidatorHook(
            rate_table=rate_table,
            cost_chain=cost_chain,
            audit_writer=audit_writer,
            cost_record_sink=cost_record_sink,
            ledger_writer=ledger_writer,
            procedural_tier_snapshot_resolver=procedural_tier_snapshot_resolver,
            signing_backend=signing_backend,
            # U-RT-136 (CP v1.101 §2 row 1) — the hook's audit-signing catch
            # is flag-consulting: ON → the typed family raises through it.
            audit_signing_fail_closed=audit_signing_fail_closed,
        )

    # U-RT-136 ⊕ U-CP-73 (CP v1.101 §2) — the composition root is the ONLY
    # place that knows both the resolved policy AND the OD-homed typed
    # family, so the CP firing site's invariant-2 carve-out is INJECTED here:
    # flag ON → the family raises through `evaluate()`'s hook swallow; flag
    # OFF → empty tuple, invariant 2's swallow unconditional (§2 row 3).
    framework: ValidatorFramework = ConcreteValidatorFramework(
        validator_registry=validator_registry,
        post_evaluate_hook=post_evaluate_hook,
        audit_signing_raise_through=(
            AUDIT_SIGNING_HARD_FAILURES if audit_signing_fail_closed else ()
        ),
    )

    # Spec §14.13.5 invariant 3 — Protocol-conformance enforcement. The
    # isinstance check is statically redundant (the local is annotated
    # `ValidatorFramework`) but is a spec-mandated runtime @runtime_checkable
    # verification, so the pyright warning is intentionally suppressed.
    if not isinstance(framework, ValidatorFramework):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise ValidatorFrameworkStageMaterializeError(
            "RT-FAIL-VALIDATOR-STAGE-MATERIALIZE: constructed validator framework "
            "instance fails @runtime_checkable ValidatorFramework Protocol-conformance "
            "per spec v1.18 §14.13.5 invariant 3."
        )

    return framework
