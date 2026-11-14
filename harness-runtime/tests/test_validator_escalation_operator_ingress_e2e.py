"""Validator escalation through the public `api.run` ingress (Runtime v1.144 C1a, C-RT-25).

The T03 scenario without its pre-action placement: the gated step's validator ESCALATEs
with a brief, so the gate fires post-dispatch from the CP driver's worker thread and must
still reach the operator through the session's elicitation. Rows: a Python operator
approves (completed; it saw the brief as a C1a request), rejects (failed, gate rejected),
and no operator at all (unattended refusal, bounded — the regression for an escalation
ask awaited off the session's loop, which used to hang to the gate deadline).
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

from harness_core.identity import StepID
from harness_cp.validator_framework_types import (
    HITLEscalationBrief,
    ValidatorFailClass,
    ValidatorOutcome,
    ValidatorResult,
)
from harness_runtime import api
from harness_runtime.lifecycle.operator_input import (
    UNATTENDED_REASON,
    OperatorDecision,
    OperatorRequest,
)
from harness_runtime.lifecycle.validator_framework_types import (
    ValidatorBinding,
    ValidatorFrameworkConfig,
)

from . import test_t03_operator_ingress_e2e as t03
from .integration.test_r_cc_1_api_resume import (
    _patched_runtime,  # noqa: F401  # pyright: ignore[reportPrivateUsage, reportUnusedImport]
)

pytestmark = t03.pytestmark
gated = t03.gated

_REASON = "mac acceptance: validator asks the operator to confirm this output"
_BOUND_SECONDS = 30.0


class _EscalatingValidator:
    """Always ESCALATE with a brief naming the gated step."""

    async def validate(self, step: Any, step_result: Any, *, step_context: Any) -> ValidatorResult:
        _ = step_result
        brief = HITLEscalationBrief(
            parent_step_id=str(step.step_id),
            parent_action_id=f"workflow:{step_context.workflow_id}:step:{step_context.step_index}",
            fail_class=ValidatorFailClass.SEMANTIC_INCONSISTENCY,
            escalation_reason=_REASON,
        )
        return ValidatorResult(
            outcome=ValidatorOutcome.ESCALATE,
            fail_class=ValidatorFailClass.SEMANTIC_INCONSISTENCY,
            escalation_brief=brief,
        )


def _run(gated: t03.Scenario, operator: Any) -> tuple[Any, float]:
    config = gated.config().model_copy(
        update={
            "validator_framework_config": ValidatorFrameworkConfig(
                bindings=(
                    ValidatorBinding(
                        step_id=StepID(t03._GATED_STEP),  # pyright: ignore[reportPrivateUsage]
                        class_qualified_name=f"{__name__}:{_EscalatingValidator.__qualname__}",
                    ),
                )
            )
        }
    )
    started = time.monotonic()
    result = asyncio.run(
        api.run(
            t03._workflow(place_gate=False),  # pyright: ignore[reportPrivateUsage]
            config=config,
            operator=operator,
        )
    )
    return result, time.monotonic() - started


def _assert_gate_rejected(result: Any, reason: str) -> None:
    assert result.status == "failed", result
    assert "RT-FAIL-HITL-GATE-REJECTED" in result.failure_cause.detail, result
    assert reason in result.failure_cause.detail, result


def test_1_approve_completes_and_the_operator_saw_the_brief_as_a_c1a_request(
    gated: t03.Scenario,
) -> None:
    seen: list[OperatorRequest] = []

    result, _ = _run(gated, t03._answering(OperatorDecision(action="approve"), seen))  # pyright: ignore[reportPrivateUsage]

    assert result.status == "completed", result
    # The gate is post-dispatch: the step's one effect precedes the question.
    assert gated.marker() == [t03._GATED_STEP]  # pyright: ignore[reportPrivateUsage]
    [request] = seen
    assert request.position == "post-dispatch"
    assert request.step_id == t03._GATED_STEP  # pyright: ignore[reportPrivateUsage]
    assert request.step_kind == "validator-escalation"
    assert request.payload["escalation_reason"] == _REASON
    assert "approve" in request.payload["responses"]


def test_2_reject_fails_the_run_with_the_operator_reason(gated: t03.Scenario) -> None:
    seen: list[OperatorRequest] = []
    reason = "validator says no"

    result, _ = _run(
        gated,
        t03._answering(OperatorDecision(action="reject", rejection_reason=reason), seen),  # pyright: ignore[reportPrivateUsage]
    )

    _assert_gate_rejected(result, reason)
    assert len(seen) == 1


def test_3_no_operator_refuses_as_unattended_within_the_bound(gated: t03.Scenario) -> None:
    result, elapsed = _run(gated, None)

    _assert_gate_rejected(result, UNATTENDED_REASON)
    assert elapsed < _BOUND_SECONDS, f"the escalation gate waited {elapsed:.1f}s for a reply"
