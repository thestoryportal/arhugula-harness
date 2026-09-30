"""C-RT-37 §14.26: read a completed Ollama reply as a CP evaluator verdict."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, cast

from harness_cp.evaluator_verdict import (
    EvaluatorVerdict,
    EvaluatorVerdictMalformedError,
    parse_evaluator_verdict_mapping,
)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise ValueError("nonfinite JSON constant")


def read_ollama_evaluator_verdict(response: object) -> EvaluatorVerdict:
    """Parse the raw ``ChatResponse.model_dump()`` without changing it."""
    # [LAW:parse-dont-validate] The provider boundary returns CP's proven verdict.
    # [LAW:no-silent-failure] Every invalid reply has one explicit malformed arm.
    try:
        if not isinstance(response, Mapping):
            raise EvaluatorVerdictMalformedError("response is not a mapping")
        reply = cast(Mapping[str, Any], response)
        if reply.get("done") is not True or reply.get("done_reason") == "length":
            raise EvaluatorVerdictMalformedError("response incomplete or truncated")
        message = reply.get("message")
        if not isinstance(message, Mapping):
            raise EvaluatorVerdictMalformedError("assistant message absent")
        assistant = cast(Mapping[str, Any], message)
        if assistant.get("role") != "assistant":
            raise EvaluatorVerdictMalformedError("assistant message absent")
        if assistant.get("tool_calls") not in (None, [], ()):
            raise EvaluatorVerdictMalformedError("assistant tool calls present")
        content = assistant.get("content")
        if not isinstance(content, str) or not content.strip():
            raise EvaluatorVerdictMalformedError("assistant content absent")
        payload = json.loads(
            content, object_pairs_hook=_unique_object, parse_constant=_reject_constant
        )
        if not isinstance(payload, dict):
            raise EvaluatorVerdictMalformedError("verdict is not a JSON object")
        return parse_evaluator_verdict_mapping(payload)
    except EvaluatorVerdictMalformedError:
        failure_reason = "invalid Ollama evaluator verdict"
    except (ValueError, TypeError, RecursionError):
        failure_reason = "invalid Ollama evaluator JSON"
    # [LAW:no-silent-failure] Raise after the handler unwinds so no model text survives
    # in __cause__, __context__, or a formatted traceback.
    raise EvaluatorVerdictMalformedError(failure_reason)
