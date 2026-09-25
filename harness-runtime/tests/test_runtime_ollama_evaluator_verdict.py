"""Provider-free contract checks for the Ollama evaluator verdict boundary."""

from __future__ import annotations

import copy
import json
from typing import Any

import pytest
from harness_cp.evaluator_verdict import EvaluatorVerdictMalformedError
from harness_runtime.lifecycle.evaluator_verdict import read_ollama_evaluator_verdict


def _response(content: Any, **changes: Any) -> dict[str, Any]:
    reply: dict[str, Any] = {
        "done": True,
        "done_reason": "stop",
        "message": {"role": "assistant", "content": content, "tool_calls": None},
    }
    reply.update(changes)
    return reply


@pytest.mark.parametrize(
    ("content", "accepted", "feedback"),
    [
        ('{"accepted":true}', True, None),
        (' {"accepted":false,"feedback":"revise"} \n', False, "revise"),
    ],
)
def test_valid_verdict_preserves_response(
    content: str, accepted: bool, feedback: str | None
) -> None:
    raw = _response(content)
    before = copy.deepcopy(raw)
    verdict = read_ollama_evaluator_verdict(raw)
    assert (verdict.accepted, verdict.feedback) == (accepted, feedback)
    assert raw == before


@pytest.mark.parametrize(
    "content",
    [
        '{"accepted":false,"accepted":true}',
        '{"accepted":true,"feedback":NaN}',
        '{"accepted":true,"feedback":Infinity}',
        '{"accepted":true,"extra":1}',
        '{"accepted":"true"}',
        '{"accepted":1}',
        '{"accepted":null}',
        '{"accepted":true,"feedback":null}',
        "{}",
        '```json\n{"accepted":true}\n```',
        '{"accepted":true} trailing',
        '{"accepted":',
        '[{"accepted":true}]',
        "[" * 2000 + "0" + "]" * 2000,
    ],
)
def test_malformed_json_is_one_typed_error_without_content(content: str) -> None:
    raw = _response(content)
    before = copy.deepcopy(raw)
    with pytest.raises(EvaluatorVerdictMalformedError) as caught:
        read_ollama_evaluator_verdict(raw)
    assert content not in str(caught.value)
    assert raw == before


@pytest.mark.parametrize(
    "raw",
    [
        _response(""),
        _response("  "),
        _response(None),
        _response('{"accepted":true}', done=False),
        _response('{"accepted":true}', done_reason="length"),
        _response('{"accepted":true}', message={"role": "user", "content": '{"accepted":true}'}),
        _response(
            '{"accepted":true}',
            message={
                "role": "assistant",
                "content": '{"accepted":true}',
                "tool_calls": [{"function": {"name": "x"}}],
            },
        ),
        _response(
            None,
            message={
                "role": "assistant",
                "content": None,
                "tool_calls": [{"function": {"name": "x"}}],
            },
        ),
        _response('{"accepted":true}', message=None),
        _response('{"accepted":true}', message="assistant"),
        _response(
            '{"accepted":true}',
            message={"role": "assistant", "content": [{"type": "text", "text": "yes"}]},
        ),
        {"provider": "cli", "content": [{"type": "text", "text": '{"accepted":true}'}]},
        {"message": {"role": "assistant", "content": '{"accepted":true}'}, "done": None},
    ],
)
def test_malformed_response_shape_is_one_typed_error(raw: dict[str, Any]) -> None:
    before = copy.deepcopy(raw)
    with pytest.raises(EvaluatorVerdictMalformedError):
        read_ollama_evaluator_verdict(raw)
    assert raw == before


def test_thinking_is_ignored_when_content_is_valid() -> None:
    raw = _response(json.dumps({"accepted": True}))
    raw["message"]["thinking"] = "private reasoning"
    assert read_ollama_evaluator_verdict(raw).accepted is True
