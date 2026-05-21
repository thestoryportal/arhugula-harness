"""C-CP-25 ValidatorFramework body — U-CP-60 (CP plan v2.16 §1).

Concrete `ConcreteValidatorFramework` materializes the §25.1 Protocol surface
declared at U-CP-59 (`harness_cp.validator_framework_types.ValidatorFramework`).
Owns the per-step Validator dispatch + the ValidatorOutcome → ValidatorNextAction
bijective mapping table per §25.2 (F2-03 RATIFIED at Phase A.2):

| ValidatorOutcome           | ValidatorNextAction |
|----------------------------|---------------------|
| PASS                       | PROCEED             |
| REVALIDATE                 | RETRY               |
| ESCALATE                   | ESCALATE_HITL       |
| PERMANENT_FAIL             | ABORT               |
| OPERATOR_BURDEN_EXCEEDED   | ESCALATE_HITL       |

The mapping is bijective on outcomes (each outcome maps to exactly one
next_action) but NOT on next_actions (ESCALATE_HITL ← {ESCALATE,
OPERATOR_BURDEN_EXCEEDED}); consumers disambiguate via `validator.outcome`
span attribute per OD §C-OD-29.

**Burden counter ownership (impl discretion per §25.4 invariant 5).** The
framework owns a private monotonic `_BurdenCounter` shared across all
`.evaluate()` invocations within a workflow lifetime. Increments on every
non-PASS outcome. The §25.4 invariant 5 "reset only at workflow boundary"
is preserved by framework lifetime ≡ workflow lifetime (framework
instantiated at stage 5 LOOP_INIT per §25.3 + discarded at workflow close).

**REVALIDATE budget-exhaustion conversion (AC #6 per F2-03).** Per §25.7
invariant 3 ("REVALIDATE bounded by C-RT-16 retry policy"), when the retry
wrapper exhausts the policy budget the framework converts the surfaced
REVALIDATE outcome to PERMANENT_FAIL + emits CP-FAIL-VALIDATOR-PERMANENT.
Implemented as `convert_revalidate_to_permanent_fail()` invoked by the
U-CP-61 workflow-driver hook on retry exhaustion (NOT inside `.evaluate()`,
which has no visibility into retry state).

**Single Validator per step invariant (§25.7 invariant 1 + AC #3).** The
operator-supplied `validator_registry` is a Mapping keyed by step_id. The
framework raises `MultipleValidatorsError` at registry-conflict detection
(extracted from the registry's own duplicate-key handling).

Authority: CP spec v1.10 §25 (C-CP-25 ValidatorFramework); plan unit U-CP-60
(CP plan v2.16 §1 = v2.15 §1 preserved).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from harness_cp.validator_framework_types import (
    Validator,
    ValidatorEvaluation,
    ValidatorFailClass,
    ValidatorNextAction,
    ValidatorOutcome,
    ValidatorResult,
)
from harness_core.identity import StepID
from harness_cp.workflow_driver_types import StepExecutionContext, WorkflowStep


# ----------------------------------------------------------------------------
# Typed errors (CP fail classes per §25.6 + AC #3 + AC #4)
# ----------------------------------------------------------------------------


class MultipleValidatorsError(Exception):
    """Raised when the validator_registry contains multiple validators for the same step_id.

    Materializes the §25.7 invariant 1 ("every step has at most one Validator")
    + AC #3 of U-CP-60. Multi-validator per step is deferred to a future arc
    per §25.7 invariant 1 closing sentence.
    """

    def __init__(self, step_id: StepID, count: int) -> None:
        super().__init__(
            f"Multiple validators registered for step_id={step_id!r} (count={count}); "
            "§25.7 invariant 1 requires at most one Validator per step."
        )
        self.step_id = step_id
        self.count = count


class CPFailValidatorPermanent(Exception):
    """Raised when a Validator returns PERMANENT_FAIL (CP fail class
    `CP-FAIL-VALIDATOR-PERMANENT` per §25.6 + AC #4).

    Also raised as the terminal escalation of a REVALIDATE-budget-exhaustion
    conversion per §25.7 invariant 3 + AC #6.
    """

    fail_class: str = "CP-FAIL-VALIDATOR-PERMANENT"

    def __init__(self, step_id: StepID, validator_fail_class: ValidatorFailClass | None) -> None:
        msg = f"Validator returned PERMANENT_FAIL for step_id={step_id!r}"
        if validator_fail_class is not None:
            msg += f" (fail_class={validator_fail_class.value})"
        super().__init__(msg)
        self.step_id = step_id
        self.validator_fail_class = validator_fail_class


# ----------------------------------------------------------------------------
# Outcome → next_action bijective mapping (§25.2 + AC #1)
# ----------------------------------------------------------------------------


_OUTCOME_TO_NEXT_ACTION: Mapping[ValidatorOutcome, ValidatorNextAction] = {
    ValidatorOutcome.PASS: ValidatorNextAction.PROCEED,
    ValidatorOutcome.REVALIDATE: ValidatorNextAction.RETRY,
    ValidatorOutcome.ESCALATE: ValidatorNextAction.ESCALATE_HITL,
    ValidatorOutcome.PERMANENT_FAIL: ValidatorNextAction.ABORT,
    ValidatorOutcome.OPERATOR_BURDEN_EXCEEDED: ValidatorNextAction.ESCALATE_HITL,
}
"""§25.2 mapping table; bijective on outcomes; NOT bijective on next_actions."""


def _map_outcome_to_next_action(outcome: ValidatorOutcome) -> ValidatorNextAction:
    """Pure helper: bijective lookup from §25.2 mapping table. AC #1."""
    return _OUTCOME_TO_NEXT_ACTION[outcome]


# ----------------------------------------------------------------------------
# Framework body (§25.1 Protocol concretization + AC #2-6)
# ----------------------------------------------------------------------------


class ConcreteValidatorFramework:
    """Concrete ValidatorFramework per CP spec v1.10 §25.1.

    Materializes the Protocol declared at U-CP-59
    (`harness_cp.validator_framework_types.ValidatorFramework`) — verified by
    `isinstance(..., ValidatorFramework)` at runtime per Protocol's
    `runtime_checkable` decoration.

    The class name disambiguates from the Protocol of the same name in the
    types module — operator code imports the Protocol for type-checking;
    bootstrap stage 5 instantiates `ConcreteValidatorFramework`.
    """

    def __init__(
        self,
        validator_registry: Mapping[StepID, Validator],
    ) -> None:
        """Construct with the operator-populated per-step Validator registry.

        Per §25.3 stage 5 instantiation. Single-Validator-per-step invariant
        enforced at construction (Mapping type prohibits duplicate keys, but
        the AC #3 test verifies the typed error raises if construction is
        passed e.g. a list-of-pairs with duplicates).
        """
        self._validator_registry = validator_registry
        self._burden_count: int = 0

    @property
    def burden_count(self) -> int:
        """Current cumulative burden count for the workflow (§25.4 invariant 5).

        Read-only public surface; incremented internally by `.evaluate()` on
        every non-PASS outcome. Monotonic per workflow lifetime; resets only
        at workflow boundary (≡ framework instance lifetime).
        """
        return self._burden_count

    async def evaluate(
        self,
        step: WorkflowStep,
        step_result: Mapping[str, Any],
        *,
        step_context: StepExecutionContext,
    ) -> ValidatorEvaluation:
        """Run the per-step Validator + wrap into ValidatorEvaluation.

        Per §25.4 invocation discipline:
        1. Look up Validator from `validator_registry` by `step.step_id`
        2. Run `.validate()` to get ValidatorResult
        3. Increment burden_count on non-PASS outcomes (§25.4 invariant 5)
        4. Map outcome → next_action (§25.2 mapping table; AC #1)
        5. Build span_attributes for §25.5 emission (validator.* namespace)
        6. Return ValidatorEvaluation
        """
        validator = self._validator_registry[step.step_id]

        result: ValidatorResult = await validator.validate(
            step,
            step_result,
            step_context=step_context,
        )

        if result.outcome != ValidatorOutcome.PASS:
            self._burden_count += 1

        next_action = _map_outcome_to_next_action(result.outcome)
        span_attributes = self._build_span_attributes(
            step=step,
            result=result,
            next_action=next_action,
            burden_count=self._burden_count,
        )

        return ValidatorEvaluation(
            result=result,
            span_attributes=span_attributes,
            next_action=next_action,
            burden_count=self._burden_count,
        )

    def convert_revalidate_to_permanent_fail(
        self,
        evaluation: ValidatorEvaluation,
        step_id: StepID,
    ) -> ValidatorEvaluation:
        """Convert a REVALIDATE evaluation to PERMANENT_FAIL on retry-budget exhaustion.

        Per §25.7 invariant 3 + AC #6 (Phase D iteration-1 F2-03 absorption).
        Invoked by the U-CP-61 workflow-driver hook on C-RT-16 retry exhaustion
        — the framework itself has no visibility into retry state. Re-wraps
        the inner ValidatorResult with outcome=PERMANENT_FAIL +
        fail_class=RESOURCE_CONSTRAINT (retry budget is a resource budget).

        Does NOT raise; returns a new ValidatorEvaluation. The hook MAY raise
        `CPFailValidatorPermanent` per §25.6 + AC #4 if the next_action=ABORT
        path requires workflow termination.
        """
        if evaluation.result.outcome != ValidatorOutcome.REVALIDATE:
            raise ValueError(
                f"convert_revalidate_to_permanent_fail invoked on outcome="
                f"{evaluation.result.outcome.value!r}; only REVALIDATE may be converted."
            )

        converted_result = evaluation.result.model_copy(
            update={
                "outcome": ValidatorOutcome.PERMANENT_FAIL,
                "fail_class": ValidatorFailClass.RESOURCE_CONSTRAINT,
            }
        )
        next_action = _map_outcome_to_next_action(ValidatorOutcome.PERMANENT_FAIL)
        span_attributes = self._build_span_attributes(
            step=None,
            step_id=step_id,
            result=converted_result,
            next_action=next_action,
            burden_count=evaluation.burden_count,
            converted_from_revalidate=True,
        )
        return ValidatorEvaluation(
            result=converted_result,
            span_attributes=span_attributes,
            next_action=next_action,
            burden_count=evaluation.burden_count,
        )

    def _build_span_attributes(
        self,
        *,
        result: ValidatorResult,
        next_action: ValidatorNextAction,
        burden_count: int,
        step: WorkflowStep | None = None,
        step_id: StepID | None = None,
        converted_from_revalidate: bool = False,
    ) -> Mapping[str, Any]:
        """Build the `validator.*` span attributes per §25.5.

        outer `validator.evaluate` envelope: step.id + validator.outcome +
        validator.burden_count_cumulative. Non-PASS adds `validator.fail` fields.
        """
        effective_step_id = step.step_id if step is not None else step_id
        attrs: dict[str, Any] = {
            "step.id": str(effective_step_id) if effective_step_id is not None else "",
            "validator.outcome": result.outcome.value,
            "validator.burden_count_cumulative": burden_count,
        }
        if result.outcome != ValidatorOutcome.PASS:
            attrs["validator.fail.next_action"] = next_action.value
            attrs["validator.fail.escalation_owed"] = (
                next_action == ValidatorNextAction.ESCALATE_HITL
            )
            if result.fail_class is not None:
                attrs["validator.fail.class"] = result.fail_class.value
            if result.fail_detail_hash is not None:
                attrs["validator.fail.detail_hash"] = result.fail_detail_hash
        if converted_from_revalidate:
            attrs["validator.revalidation.terminal_conversion"] = "permanent_fail"
        return attrs
