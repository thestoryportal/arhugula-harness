"""`U-CP-73` (v2.38 amendment) — §28.10.4 invariant-2 audit-signing carve-out.

Implements CP plan v2.38 §2 witness (b) per CP spec v1.101 §2 (C-CP-28
AMENDED invariant 2): the `audit_signing_raise_through` tuple injected at the
composition root carves EXACTLY the typed audit-signing family out of the
hook swallow; every other hook exception class remains swallowed; the empty
default preserves invariant 2 unconditionally (flag OFF / every pre-v1.101
construction site).

`harness-cp` never imports `harness-od` (the family's canonical home per the
axis direction), so these witnesses inject test-local exception classes —
the mechanism under test is the injected-tuple carve-out itself; the
composition root's binding of the REAL `AUDIT_SIGNING_HARD_FAILURES` family
(+ the flag consult) is witnessed runtime-side at
`harness-runtime/tests/test_u_rt_136_audit_signing_flag_wiring.py`.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest
from harness_as.sandbox_tier import SandboxTier
from harness_core.identity import StepID
from harness_cp.sub_agent_gate_level_descent import GateLevel
from harness_cp.validator_framework import ConcreteValidatorFramework
from harness_cp.validator_framework_types import (
    ValidatorEvaluation,
    ValidatorOutcome,
    ValidatorResult,
)
from harness_cp.workflow_driver_types import StepExecutionContext, StepKind, WorkflowStep
from harness_is.state_ledger_entry_schema import Actor, ActorClass

# ----------------------------------------------------------------------------
# Fixtures (mirrors test_validator_framework_post_evaluate_hook.py)
# ----------------------------------------------------------------------------


class _FakeSigningError(RuntimeError):
    """Test-local stand-in for a member of `AUDIT_SIGNING_HARD_FAILURES`."""


def _make_step(step_id_str: str = "step-1") -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID(step_id_str),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={},
    )


def _make_step_context() -> StepExecutionContext:
    return StepExecutionContext(
        workflow_id="wf-test",
        parent_action_id="workflow:wf-test:step:0",
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=Actor(actor_class=ActorClass.AGENT, actor_id="test-carve-out"),
        parent_entry_hash="",
        parent_idempotency_key="idem-key-test",
        tenant_id=None,
        step_index=0,
    )


class _PassValidator:
    async def validate(
        self,
        step: WorkflowStep,
        step_result: Mapping[str, Any],
        *,
        step_context: StepExecutionContext,
    ) -> ValidatorResult:
        _ = (step, step_result, step_context)
        return ValidatorResult(outcome=ValidatorOutcome.PASS)


class _RaisingHook:
    """Raises the configured exception on every firing; counts firings."""

    def __init__(self, exc: BaseException) -> None:
        self.exc = exc
        self.calls = 0

    async def on_post_evaluate(
        self,
        *,
        step: WorkflowStep,
        step_context: StepExecutionContext,
        evaluation: ValidatorEvaluation,
        execution_time_ms: float,
    ) -> None:
        _ = (step, step_context, evaluation, execution_time_ms)
        self.calls += 1
        raise self.exc


def _framework(
    hook: _RaisingHook,
    *,
    raise_through: tuple[type[BaseException], ...],
) -> ConcreteValidatorFramework:
    step = _make_step()
    return ConcreteValidatorFramework(
        validator_registry={step.step_id: _PassValidator()},
        post_evaluate_hook=hook,
        audit_signing_raise_through=raise_through,
    )


# ----------------------------------------------------------------------------
# Witness (b) — carve-out narrow-scope.
# ----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_flag_on_typed_family_raises_through_hook_and_nonmember_still_swallowed() -> None:
    """§2 rows 1 + 2: with the family injected (the composition root's
    flag-ON binding), a member raised at the hook RAISES through
    `evaluate()`; a NON-member (cost-computation failure, rate-table miss,
    span-attribute build error — here `ValueError`) remains swallowed and
    `evaluate()` returns the evaluation per invariant 2. Row 4: the hook
    fired exactly once on the raise path.

    Mutation probe: widening the firing-site carve-out to a bare
    `except Exception: raise` makes the non-member leg raise → FAILS; and
    deleting the carve-out arm makes the member leg return → FAILS."""
    member_hook = _RaisingHook(_FakeSigningError("kms unavailable (test)"))
    framework = _framework(member_hook, raise_through=(_FakeSigningError,))
    with pytest.raises(_FakeSigningError):
        await framework.evaluate(_make_step(), {}, step_context=_make_step_context())
    assert member_hook.calls == 1, "invariant 4: the hook fires at most once"

    nonmember_hook = _RaisingHook(ValueError("rate-table miss (test)"))
    framework_nm = _framework(nonmember_hook, raise_through=(_FakeSigningError,))
    evaluation = await framework_nm.evaluate(_make_step(), {}, step_context=_make_step_context())
    assert evaluation.result.outcome is ValidatorOutcome.PASS
    assert nonmember_hook.calls == 1


@pytest.mark.asyncio
async def test_flag_off_both_swallowed_as_today() -> None:
    """§2 row 3: with the EMPTY default tuple (flag OFF / every pre-v1.101
    construction site), invariant 2's swallow holds UNCONDITIONALLY — the
    would-be family member and the non-member are both swallowed and
    `evaluate()` returns the evaluation, byte-preserving current behavior."""
    for exc in (_FakeSigningError("kms unavailable (test)"), ValueError("miss")):
        hook = _RaisingHook(exc)
        framework = _framework(hook, raise_through=())
        evaluation = await framework.evaluate(_make_step(), {}, step_context=_make_step_context())
        assert evaluation.result.outcome is ValidatorOutcome.PASS
        assert hook.calls == 1


@pytest.mark.asyncio
async def test_raise_through_default_is_empty_at_legacy_construction() -> None:
    """AC #3 lineage: a construction site that never heard of v1.101
    (no `audit_signing_raise_through` kwarg) gets the empty tuple — every
    pre-v1.101 caller is byte-identical."""
    hook = _RaisingHook(_FakeSigningError("kms unavailable (test)"))
    step = _make_step()
    framework = ConcreteValidatorFramework(
        validator_registry={step.step_id: _PassValidator()},
        post_evaluate_hook=hook,
    )
    evaluation = await framework.evaluate(step, {}, step_context=_make_step_context())
    assert evaluation.result.outcome is ValidatorOutcome.PASS
