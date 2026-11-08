"""Operator input for HITL gates at the harness ingresses (Runtime v1.144 C1, C1a, C2, C5).

An ingress turns whatever the operator did (a Python callback, a terminal line, nothing at
all) into one `OperatorDecision`, which travels to the server as an elicitation `accept`
carrying the ingress name. The server's gate message is the deterministic C1a text; the
ingress parses it back into an `OperatorRequest` so a Python operator sees the same fields
the terminal operator reads.
"""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable, Mapping
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, model_validator

__all__ = [
    "UNATTENDED_REASON",
    "HarnessIngress",
    "OperatorAction",
    "OperatorDecision",
    "OperatorInput",
    "OperatorRequest",
    "compose_operator_gate_message",
    "operator_elicitation_callback",
    "parse_operator_gate_message",
    "parse_operator_line",
]

OperatorAction = Literal["approve", "edit", "reject", "respond", "hold", "cancel", "refuse"]
HarnessIngress = Literal["python", "cli-tty", "daemon-client-tty", "unattended"]

# Which optional field each action may carry, and which it must carry (C1 table).
_ALLOWED_FIELDS: Mapping[str, frozenset[str]] = {
    "approve": frozenset({"response_text"}),
    "edit": frozenset({"edited_proposal"}),
    "reject": frozenset({"rejection_reason"}),
    "respond": frozenset({"response_text"}),
    "hold": frozenset(),
    "cancel": frozenset(),
    "refuse": frozenset({"rejection_reason"}),
}
_REQUIRED_FIELD: Mapping[str, str] = {
    "edit": "edited_proposal",
    "respond": "response_text",
    "refuse": "rejection_reason",
}


class OperatorDecision(BaseModel):
    """The one value every harness ingress produces for a HITL gate (C1).

    `refuse` is never operator-chosen: an ingress produces it, with a literal reason, for
    unattended or invalid input, and the server audits it as a reject.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    action: OperatorAction
    edited_proposal: str | None = None
    """JSON object text replacing the gated step's payload (`edit` only)."""
    response_text: str | None = None
    rejection_reason: str | None = None

    @model_validator(mode="after")
    def _fields_match_action(self) -> OperatorDecision:
        # [LAW:parse-dont-validate] a decision exists only in a C1 shape.
        carried = {
            name
            for name in ("edited_proposal", "response_text", "rejection_reason")
            if getattr(self, name) is not None
        }
        if not carried <= _ALLOWED_FIELDS[self.action]:
            raise ValueError(f"action {self.action!r} cannot carry {sorted(carried)}")
        required = _REQUIRED_FIELD.get(self.action)
        if required is not None and required not in carried:
            raise ValueError(f"action {self.action!r} requires {required}")
        return self

    def elicitation_content(self, ingress: HarnessIngress) -> dict[str, str]:
        """The `accept` data this decision sends under the elicitation schema (C1, C5)."""
        fields = self.model_dump(exclude_none=True, exclude={"action"})
        return {"response": self.action, "ingress": ingress, **fields}


class OperatorRequest(BaseModel):
    """The decision-relevant gate request an operator answers (C1a)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    position: str
    step_id: str
    step_kind: str
    payload: dict[str, Any]
    payload_sha256: str
    options: tuple[str, ...]
    message: str


OperatorInput = Callable[[OperatorRequest], Awaitable[OperatorDecision]]
"""A Python operator: answers one request with one decision (C2 `api.run(operator=...)`)."""


def _canonical_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def compose_operator_gate_message(
    *,
    position: str,
    step_id: str,
    step_kind: str,
    payload: Mapping[str, Any],
    payload_sha256: str,
) -> str:
    """The C1a gate message: the complete canonical payload, never truncated."""
    return (
        f"HITL gate at {position}\n"
        f"step: {step_id} ({step_kind})\n"
        f"payload sha256: {payload_sha256}\n"
        f"payload: {_canonical_json(payload)}"
    )


def parse_operator_gate_message(message: str, options: tuple[str, ...]) -> OperatorRequest:
    """Read a C1a message back into its fields; raises ValueError on any other text."""
    lines = message.split("\n", 3)
    if len(lines) != 4:
        raise ValueError("not a C1a HITL gate message")
    gate, step, digest, payload = lines
    prefixes = ("HITL gate at ", "step: ", "payload sha256: ", "payload: ")
    if not all(line.startswith(p) for line, p in zip(lines, prefixes, strict=True)):
        raise ValueError("not a C1a HITL gate message")
    step_id, _, kind = step.removeprefix("step: ").rpartition(" (")
    parsed_payload = json.loads(payload.removeprefix("payload: "))
    if not kind.endswith(")") or not isinstance(parsed_payload, dict):
        raise ValueError("not a C1a HITL gate message")
    return OperatorRequest(
        position=gate.removeprefix("HITL gate at "),
        step_id=step_id,
        step_kind=kind.removesuffix(")"),
        payload=parsed_payload,
        payload_sha256=digest.removeprefix("payload sha256: "),
        options=options,
        message=message,
    )


INVALID_OPERATOR_INPUT = "invalid operator input"


def parse_operator_line(line: str) -> OperatorDecision:
    """The shared terminal grammar for both CLI ingresses (C2).

    `approve`, `reject [reason]`, `edit <JSON object>`, `respond <text>`, `hold`,
    `cancel`; any other line is a refusal, never a re-prompt.
    """
    word, _, rest = line.strip().partition(" ")
    rest = rest.strip()
    fields: dict[str, dict[str, str | None]] = {
        "approve": {},
        "hold": {},
        "cancel": {},
        "reject": {"rejection_reason": rest or None},
        "edit": {"edited_proposal": rest or None},
        "respond": {"response_text": rest or None},
    }
    takes_argument = word in {"reject", "edit", "respond"}
    if word not in fields or (rest and not takes_argument):
        return OperatorDecision(action="refuse", rejection_reason=INVALID_OPERATOR_INPUT)
    try:
        return OperatorDecision(action=word, **fields[word])  # type: ignore[arg-type]
    except ValueError:
        return OperatorDecision(action="refuse", rejection_reason=INVALID_OPERATOR_INPUT)


UNATTENDED_REASON = "unattended: no operator input bound"
_GATE_OPTIONS: tuple[str, ...] = ("approve", "edit", "reject", "respond", "hold", "cancel")


def operator_elicitation_callback(
    operator: OperatorInput | None, ingress: HarnessIngress
) -> Callable[[Any, Any], Awaitable[Any]]:
    """An MCP client `elicitation_callback` that answers every gate through `operator` (C2).

    No operator answers `refuse` from the `unattended` ingress. A failing operator (it
    raises, or returns something other than an `OperatorDecision`) answers `refuse` naming
    the failure; the gate is never left waiting on it.
    """
    from mcp.types import ElicitResult

    async def _answer(context: Any, params: Any) -> ElicitResult:
        _ = context
        if operator is None:
            decision = OperatorDecision(action="refuse", rejection_reason=UNATTENDED_REASON)
            return ElicitResult(action="accept", content=decision.elicitation_content("unattended"))
        try:
            answered: object = await operator(
                parse_operator_gate_message(params.message, _GATE_OPTIONS)
            )
        except Exception as exc:  # every failure becomes an audited refusal
            answered = exc
        decision = (
            answered
            if isinstance(answered, OperatorDecision)
            else OperatorDecision(
                action="refuse",
                rejection_reason=f"operator input callback failed: {type(answered).__name__}",
            )
        )
        return ElicitResult(action="accept", content=decision.elicitation_content(ingress))

    return _answer
