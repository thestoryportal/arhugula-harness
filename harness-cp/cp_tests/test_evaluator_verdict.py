"""Strict `EvaluatorVerdict` parse (CP spec v1.121 §25.11 encoding, first-release contract).

One typed result for the evaluator's accept signal. The parser is the single
checkpoint: a mapping either becomes an `EvaluatorVerdict` or raises
`EvaluatorVerdictMalformedError`; nothing downstream re-checks or coerces.
"""

from __future__ import annotations

from typing import Any

import pytest
from harness_cp.evaluator_verdict import (
    EvaluatorVerdict,
    EvaluatorVerdictMalformedError,
    parse_evaluator_verdict_mapping,
)
from pydantic import ValidationError


@pytest.mark.parametrize(
    ("mapping", "expected"),
    [
        ({"accepted": True}, EvaluatorVerdict(accepted=True, feedback=None)),
        ({"accepted": False}, EvaluatorVerdict(accepted=False, feedback=None)),
        ({"accepted": True, "feedback": "ok"}, EvaluatorVerdict(accepted=True, feedback="ok")),
        ({"accepted": False, "feedback": ""}, EvaluatorVerdict(accepted=False, feedback="")),
    ],
)
def test_a_literal_bool_accepted_with_optional_string_feedback_parses(
    mapping: dict[str, Any], expected: EvaluatorVerdict
) -> None:
    assert parse_evaluator_verdict_mapping(mapping) == expected


@pytest.mark.parametrize(
    "mapping",
    [
        {},
        {"feedback": "no verdict"},
        {"accepted": "false"},
        {"accepted": "true"},
        {"accepted": 1},
        {"accepted": 0},
        {"accepted": None},
        {"accepted": [True]},
        {"accepted": True, "extra": 1},
        {"accepted": True, "feedback": 3},
        {"accepted": True, "feedback": None},
        {"accepted": False, "feedback": ["x"]},
    ],
)
def test_anything_else_is_a_typed_malformed_error_never_coerced(mapping: dict[str, Any]) -> None:
    with pytest.raises(EvaluatorVerdictMalformedError):
        parse_evaluator_verdict_mapping(mapping)


@pytest.mark.parametrize("not_a_mapping", [None, "accepted", 1, True, ["accepted"]])
def test_a_non_mapping_is_malformed(not_a_mapping: Any) -> None:
    with pytest.raises(EvaluatorVerdictMalformedError):
        parse_evaluator_verdict_mapping(not_a_mapping)


def test_the_malformed_error_names_the_reason() -> None:
    with pytest.raises(EvaluatorVerdictMalformedError, match="accepted") as excinfo:
        parse_evaluator_verdict_mapping({"accepted": "false"})

    assert "false" in excinfo.value.reason


def test_the_verdict_is_frozen_and_refuses_a_non_bool_at_construction() -> None:
    verdict = EvaluatorVerdict(accepted=True, feedback=None)

    with pytest.raises(ValidationError):
        verdict.accepted = False  # pyright: ignore[reportAttributeAccessIssue]
    with pytest.raises(ValidationError):
        EvaluatorVerdict(accepted="false", feedback=None)  # pyright: ignore[reportArgumentType]
