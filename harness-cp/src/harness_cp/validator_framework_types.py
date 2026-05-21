"""C-CP-25 ValidatorFramework type carriers — 3 enums per CP spec v1.10 §25.2.

U-CP-58 — first unit of cluster 10-CP-A. Declares the three enums that the
C-CP-25 ValidatorFramework composer body (U-CP-60) and the validator.* span
emitter (U-CP-61) consume at runtime:

- `ValidatorOutcome` — the 5-class outcome a Validator returns from .validate()
- `ValidatorFailClass` — the 5-class pre-emit fail categorization (NEW at CP spec v1.10)
- `ValidatorNextAction` — the 4-class framework-derived next-action

Member string values for `ValidatorOutcome` and `ValidatorFailClass` are cited
verbatim from CP spec v1.10 §25.2. `ValidatorNextAction` value names are per
§25.8 deferred-to-implementation discretion; this impl arc selects lowercase
SCREAMING_SNAKE_CASE-rendered enum-value strings matching the §25.2 mapping
table's value-name column.

**Naming note (path β disambiguation, 2026-05-21).** This module's
`ValidatorFailClass` is distinct from the C-CP-21 §21.1 retry-exit taxonomy
homed at `harness_cp.validator_fail_taxonomy.ValidatorRetryExitClass`. The
two enums occupy different semantic domains: C-CP-21 = post-fail retry-exit
classification (which staircase to run); C-CP-25 = pre-emit fail categorization
(why validation failed). Per workspace `.harness/class_1_fork_u_cp_58_validator_fail_class_collision.md`
operator-ratified path β.

Authority: CP spec v1.10 §25.2 (NEW C-CP-25 ValidatorFramework); plan unit
U-CP-58 (CP plan v2.16 §1).
"""

from __future__ import annotations

from enum import StrEnum


class ValidatorOutcome(StrEnum):
    """The 5-class outcome a Validator returns from .validate() (CP spec v1.10 §25.2).

    Each outcome maps to exactly one `ValidatorNextAction` per the §25.2
    mapping table (bijective on outcomes; NOT on next_actions —
    ESCALATE_HITL is the next_action for both ESCALATE and
    OPERATOR_BURDEN_EXCEEDED, with disambiguation via `validator.outcome`
    span attribute per §C-OD-29).
    """

    PASS = "pass"
    """Validation succeeded; step result accepted."""

    REVALIDATE = "revalidate"
    """Mutate payload + retry via C-RT-16 retry wrapper."""

    ESCALATE = "escalate"
    """Validator-fail escalation arc per §25.7 invariant 4;
    opens HITL gate composition via C-RT-18 §14.8."""

    PERMANENT_FAIL = "permanent_fail"
    """Workflow aborts with `fail_class` propagation per §25.6."""

    OPERATOR_BURDEN_EXCEEDED = "operator_burden_exceeded"
    """Operator-burden threshold breach; degrade per persona-tier
    (runtime spec v1.13 §14.10 OperatorBurdenEvaluator)."""


class ValidatorFailClass(StrEnum):
    """The 5-class pre-emit fail categorization (CP spec v1.10 §25.2; NEW at C-CP-25).

    Distinct from C-CP-21 §21.1 ValidatorRetryExitClass (post-fail retry-exit
    classification) homed at `harness_cp.validator_fail_taxonomy`.
    """

    SCHEMA_VIOLATION = "schema_violation"
    """Output doesn't match input_schema."""

    SEMANTIC_INCONSISTENCY = "semantic_inconsistency"
    """Contradicts prior step state."""

    SAFETY_POLICY = "safety_policy"
    """Operator-defined policy hit."""

    RESOURCE_CONSTRAINT = "resource_constraint"
    """Cost/latency budget exceeded."""

    EXTERNAL_REJECTION = "external_rejection"
    """Downstream service rejected."""


class ValidatorNextAction(StrEnum):
    """The 4-class framework-derived next-action (CP spec v1.10 §25.2 mapping table).

    Per §25.8 deferred-to-implementation discretion: enum value names
    selected as SCREAMING_SNAKE_CASE-rendered lowercase strings matching
    the §25.2 mapping table's next_action column. Bijective on outcomes
    (each ValidatorOutcome maps to exactly one ValidatorNextAction);
    NOT bijective on next_actions (ESCALATE_HITL receives both ESCALATE
    and OPERATOR_BURDEN_EXCEEDED — disambiguation via `validator.outcome`
    per §C-OD-29).
    """

    PROCEED = "proceed"
    """ValidatorOutcome=PASS → step result accepted."""

    RETRY = "retry"
    """ValidatorOutcome=REVALIDATE → mutate + retry via C-RT-16."""

    ESCALATE_HITL = "escalate_hitl"
    """ValidatorOutcome ∈ {ESCALATE, OPERATOR_BURDEN_EXCEEDED}
    → open HITL gate via C-RT-18 §14.8."""

    ABORT = "abort"
    """ValidatorOutcome=PERMANENT_FAIL → workflow aborts."""
