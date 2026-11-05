"""U-RT-83 / Trial193.4h4 — Validator framework type carrier.

Implements runtime spec §14.13.1 (architectural surfaces introduced) with the
§14.13.7 implementer-discretion operator-supply shape:

- `ValidatorBinding`: one operator-supplied validator for one workflow step —
  the step it guards, the class-qualified name of the operator `Validator`
  class (resolved with the same introspection discipline as
  `MemoryToolStorageBackend.OPERATOR_DEFINED`, spec §14.13.1), and the scalar
  keyword arguments its constructor receives.
- `ValidatorFrameworkConfig`: the operator's validator catalog. Presence at
  `RuntimeConfig.validator_framework_config` signals opt-in and carries at
  least one binding; absence (`None` default at C-RT-02) signals opt-out and
  yields `ctx.validator_framework is None`.

Both are frozen dataclasses so `RuntimeConfigSource` parses them straight from
a TOML `[[validator_framework_config.bindings]]` array of tables.

Module sits parallel to `memory_tool_types.py` under `lifecycle/` per the
§14.12 carrier-home precedent (RuntimeConfig sub-models that pair with stage
factories at runtime spec contracts live in harness-runtime/lifecycle/).
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, field

from harness_core.identity import StepID
from pydantic import ConfigDict

ValidatorParamValue = str | int | float | bool
"""A TOML-expressible scalar passed to an operator validator's constructor."""


@dataclass(frozen=True)
class ValidatorBinding:
    """One operator-supplied validator bound to one workflow step.

    The stage-4 factory resolves `class_qualified_name` (`module:Class` or
    `module.Class`) and constructs it as `cls(**params)`, so an unexpected
    parameter name fails construction instead of being ignored.
    """

    # [LAW:no-silent-failure] a misspelled TOML key is refused, not dropped.
    __pydantic_config__ = ConfigDict(extra="forbid")

    step_id: StepID
    class_qualified_name: str
    params: Mapping[str, ValidatorParamValue] = field(
        default_factory=dict[str, ValidatorParamValue]
    )


@dataclass(frozen=True)
class ValidatorFrameworkConfig:
    """Operator-supplied validator catalog: at most one validator per step.

    Opt-in means substantive validation, so an empty catalog is refused here
    rather than materializing a framework that can never PASS a step. The
    CP framework indexes its registry by step id, so a step bound twice is
    refused here too (CP spec §25.7 invariant 1).
    """

    __pydantic_config__ = ConfigDict(extra="forbid")

    bindings: tuple[ValidatorBinding, ...]

    def __post_init__(self) -> None:
        # [LAW:types-are-the-program] construction is the one place a catalog
        # can become empty or ambiguous; past it, every registry is well-formed.
        if not self.bindings:
            raise ValueError(
                "ValidatorFrameworkConfig.bindings must name at least one validator; "
                "leave validator_framework_config unset to opt out"
            )
        duplicated = sorted(
            step_id
            for step_id, count in Counter(b.step_id for b in self.bindings).items()
            if count > 1
        )
        if duplicated:
            raise ValueError(
                f"ValidatorFrameworkConfig.bindings binds step_id(s) {duplicated} more "
                "than once; CP §25.7 invariant 1 allows at most one validator per step"
            )
