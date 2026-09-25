"""Typed evaluator verdict — the single accept signal for EVALUATOR_OPTIMIZER.

CP spec v1.121 (C-CP-25 §25.11 encoding; §25.17 verdict absent/malformed → FAILED). The
evaluator step's output is read through ONE checkpoint: `parse_evaluator_verdict_mapping`
either returns an `EvaluatorVerdict` or raises `EvaluatorVerdictMalformedError`.
Nothing downstream coerces or re-checks ([LAW:parse-dont-validate]); a missing,
string-typed or otherwise non-literal verdict is never treated as an accept or as an
implicit reject ([LAW:no-silent-failure]).

The contract is a mapping with a literal `bool` `accepted`, an optional `str`
`feedback`, and no other keys. Extracting that mapping from a provider response
(for example an Ollama assistant message) is a Runtime reader's job; it returns this
same type.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from pydantic import BaseModel, ConfigDict, StrictBool, StrictStr

__all__ = [
    "EvaluatorVerdict",
    "EvaluatorVerdictMalformedError",
    "parse_evaluator_verdict_mapping",
]

_ACCEPTED_KEY = "accepted"
_FEEDBACK_KEY = "feedback"
_ALLOWED_KEYS = frozenset({_ACCEPTED_KEY, _FEEDBACK_KEY})


class EvaluatorVerdict(BaseModel):
    """The evaluator's decision: accepted only when `accepted is True`."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    accepted: StrictBool
    feedback: StrictStr | None = None


class EvaluatorVerdictMalformedError(Exception):
    """An evaluator output that is not a valid verdict; `reason` names why."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"evaluator verdict malformed: {reason}")
        self.reason = reason


def parse_evaluator_verdict_mapping(evaluation: Any) -> EvaluatorVerdict:
    """Parse an evaluator output mapping into an `EvaluatorVerdict`, strictly.

    `accepted` must be present and a literal `bool` (no `"false"`, `1`, `None`);
    `feedback` must be absent or a `str`; any other key is rejected.
    """
    if not isinstance(evaluation, Mapping):
        raise EvaluatorVerdictMalformedError(
            f"output is {type(evaluation).__name__}, not a mapping"
        )
    fields = cast(Mapping[str, Any], evaluation)
    extra = sorted(str(key) for key in fields if key not in _ALLOWED_KEYS)
    if extra:
        raise EvaluatorVerdictMalformedError(f"unexpected keys {extra}")
    if _ACCEPTED_KEY not in fields:
        raise EvaluatorVerdictMalformedError("`accepted` is absent")
    accepted = fields[_ACCEPTED_KEY]
    if type(accepted) is not bool:
        raise EvaluatorVerdictMalformedError(
            f"`accepted` must be a JSON boolean, got {type(accepted).__name__} {accepted!r}"
        )
    feedback = fields.get(_FEEDBACK_KEY)
    if _FEEDBACK_KEY in fields and type(feedback) is not str:
        raise EvaluatorVerdictMalformedError(
            f"`feedback` must be a string when present, got {type(feedback).__name__}"
        )
    return EvaluatorVerdict(accepted=accepted, feedback=feedback)
