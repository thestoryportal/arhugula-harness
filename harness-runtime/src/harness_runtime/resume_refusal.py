"""The closed `harness.resume-refusal.v1` value: a root resume refused before its body ran.

Runtime spec v1.137 §D (the adopted B-313 v2 value plus the §D.5 ninth arm). A refusal is
built only from one of the nine typed `resume()` refusals (`project`), crosses a text boundary
as one JSON object (`to_json`), and is recovered on the receiving side only by the strict
`parse`, which returns the same discriminated value or raises `ResumeRefusalProtocolError`.
Nothing here reads an exception message: the value carries the typed facts of its arm and
nothing else, so raw errno text, paths, digests, tokens and tenant identifiers cannot reach it.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Final, Literal, assert_never, cast

from harness_runtime.api import (
    ResumeArgsError,
    ResumeClaimRefusedError,
    ResumeDirectChildHandleError,
    ResumeHandleUnknownError,
    ResumePauseRecordSupersededError,
    ResumePauseStateStaleError,
    ResumeProtocolNotBoundError,
    ResumeStepIndexOutOfRangeError,
    ResumeWorkflowMismatchError,
)
from harness_runtime.lifecycle.journal_workflow_pause_store import PauseJournalReadCause
from harness_runtime.lifecycle.root_resume_admission import RootResumeRefusal

__all__ = [
    "PROTOCOL",
    "ClaimRefusal",
    "DepthRefusal",
    "HandleCause",
    "HandleRefusal",
    "RefusalKind",
    "ResumeRefusal",
    "ResumeRefusalError",
    "ResumeRefusalProtocolError",
    "ValidationRefusal",
    "fail_class",
    "parse",
    "project",
    "to_json",
]

PROTOCOL: Final = "harness.resume-refusal.v1"


class RefusalKind(StrEnum):
    """The nine closed arms; each kind has exactly one `fail_class` (`fail_class`)."""

    ARGUMENTS = "arguments"
    HANDLE = "handle"
    DEPTH = "depth"
    PROTOCOL_NOT_BOUND = "protocol-not-bound"
    PAUSE_STATE_STALE = "pause-state-stale"
    WORKFLOW_MISMATCH = "workflow-mismatch"
    STEP_INDEX_OUT_OF_RANGE = "step-index-out-of-range"
    CLAIM = "claim"
    PAUSE_RECORD_SUPERSEDED = "pause-record-superseded"


class HandleCause(StrEnum):
    """The `handle` arm's `cause`: closed at five, whatever the journal read vocabulary grows to.

    A supersession is its own arm (§D.5), so it is never one of these.
    """

    ABSENT = "absent"
    EMPTY_JOURNAL = "empty-journal"
    READ_ERROR = "read-error"
    CORRUPT_LATEST = "corrupt-latest"
    WORKFLOW_MISMATCH = "workflow-mismatch"


type ValidationKind = Literal[
    RefusalKind.ARGUMENTS,
    RefusalKind.PROTOCOL_NOT_BOUND,
    RefusalKind.PAUSE_STATE_STALE,
    RefusalKind.WORKFLOW_MISMATCH,
    RefusalKind.STEP_INDEX_OUT_OF_RANGE,
    RefusalKind.PAUSE_RECORD_SUPERSEDED,
]


@dataclass(frozen=True)
class ValidationRefusal:
    """A pre-bootstrap validation arm: it identifies only its kind and fail_class."""

    kind: ValidationKind


@dataclass(frozen=True)
class HandleRefusal:
    """`retryable`/`indeterminate` are copied from the typed error, never derived from `cause`."""

    cause: HandleCause
    retryable: bool
    indeterminate: bool
    kind: Literal[RefusalKind.HANDLE] = RefusalKind.HANDLE


@dataclass(frozen=True)
class DepthRefusal:
    """`depth` is the recorded integer, or `None` when unknown; `None` never means root."""

    depth: int | None
    kind: Literal[RefusalKind.DEPTH] = RefusalKind.DEPTH


@dataclass(frozen=True)
class ClaimRefusal:
    reason: RootResumeRefusal
    kind: Literal[RefusalKind.CLAIM] = RefusalKind.CLAIM


type ResumeRefusal = ValidationRefusal | HandleRefusal | DepthRefusal | ClaimRefusal

type ResumeRefusalError = (
    ResumeArgsError
    | ResumeHandleUnknownError
    | ResumeDirectChildHandleError
    | ResumeProtocolNotBoundError
    | ResumePauseStateStaleError
    | ResumeWorkflowMismatchError
    | ResumeStepIndexOutOfRangeError
    | ResumeClaimRefusedError
    | ResumePauseRecordSupersededError
)
"""The nine typed refusals a root `resume()` raises before its body runs. Bootstrap, invalid
workflow, concurrent-run and transport failures are not among them and keep their own class."""


# [LAW:one-source-of-truth] The kind -> fail_class pairing and each arm's extra wire fields are
# stated once; the encoder and the strict parser both read these tables.
_FAIL_CLASS: Final[Mapping[RefusalKind, str]] = {
    RefusalKind.ARGUMENTS: "RT-FAIL-RESUME-ARGS",
    RefusalKind.HANDLE: "RT-FAIL-RESUME-HANDLE-UNKNOWN",
    RefusalKind.DEPTH: "RT-FAIL-RESUME-DIRECT-CHILD-HANDLE",
    RefusalKind.PROTOCOL_NOT_BOUND: "RT-FAIL-RESUME-PROTOCOL-NOT-BOUND",
    RefusalKind.PAUSE_STATE_STALE: "RT-FAIL-RESUME-PAUSE-STATE-STALE",
    RefusalKind.WORKFLOW_MISMATCH: "RT-FAIL-RESUME-WORKFLOW-MISMATCH",
    RefusalKind.STEP_INDEX_OUT_OF_RANGE: "RT-FAIL-RESUME-STEP-INDEX-OUT-OF-RANGE",
    RefusalKind.CLAIM: "RT-FAIL-RESUME-CLAIM-REFUSED",
    RefusalKind.PAUSE_RECORD_SUPERSEDED: "RT-FAIL-RESUME-PAUSE-RECORD-SUPERSEDED",
}

_EXTRA_FIELDS: Final[Mapping[RefusalKind, tuple[str, ...]]] = {kind: () for kind in RefusalKind} | {
    RefusalKind.HANDLE: ("cause", "retryable", "indeterminate"),
    RefusalKind.DEPTH: ("depth",),
    RefusalKind.CLAIM: ("reason",),
}


def fail_class(kind: RefusalKind) -> str:
    return _FAIL_CLASS[kind]


def _handle_cause(cause: PauseJournalReadCause) -> HandleCause:
    # [LAW:types-are-the-program] Exhaustive over the read vocabulary, so a member added there
    # fails type-checking here until it is given an arm instead of silently becoming a cause.
    match cause:
        case PauseJournalReadCause.ABSENT:
            return HandleCause.ABSENT
        case PauseJournalReadCause.EMPTY_JOURNAL:
            return HandleCause.EMPTY_JOURNAL
        case PauseJournalReadCause.READ_ERROR:
            return HandleCause.READ_ERROR
        case PauseJournalReadCause.CORRUPT_LATEST:
            return HandleCause.CORRUPT_LATEST
        case PauseJournalReadCause.WORKFLOW_MISMATCH:
            return HandleCause.WORKFLOW_MISMATCH
        case _:
            assert_never(cause)


def project(error: ResumeRefusalError) -> ResumeRefusal:
    """Map one typed refusal to its arm, reading typed attributes only, never the message."""
    match error:
        case ResumeArgsError():
            return ValidationRefusal(RefusalKind.ARGUMENTS)
        case ResumeHandleUnknownError():
            return HandleRefusal(_handle_cause(error.cause), error.retryable, error.indeterminate)
        case ResumeDirectChildHandleError():
            return DepthRefusal(error.depth)
        case ResumeProtocolNotBoundError():
            return ValidationRefusal(RefusalKind.PROTOCOL_NOT_BOUND)
        case ResumePauseStateStaleError():
            return ValidationRefusal(RefusalKind.PAUSE_STATE_STALE)
        case ResumeWorkflowMismatchError():
            return ValidationRefusal(RefusalKind.WORKFLOW_MISMATCH)
        case ResumeStepIndexOutOfRangeError():
            return ValidationRefusal(RefusalKind.STEP_INDEX_OUT_OF_RANGE)
        case ResumeClaimRefusedError():
            return ClaimRefusal(error.reason)
        case ResumePauseRecordSupersededError():
            return ValidationRefusal(RefusalKind.PAUSE_RECORD_SUPERSEDED)
        case _:
            assert_never(error)


def to_json(refusal: ResumeRefusal) -> str:
    """The one serialized form: `{"protocol": ..., "refusal": {kind, fail_class, extras}}`."""
    body: dict[str, object] = {"kind": refusal.kind, "fail_class": fail_class(refusal.kind)}
    body |= {name: getattr(refusal, name) for name in _EXTRA_FIELDS[refusal.kind]}
    return json.dumps({"protocol": PROTOCOL, "refusal": body}, separators=(",", ":"))


class ResumeRefusalProtocolError(ValueError):
    """The text is not exactly one `harness.resume-refusal.v1` value.

    It proves nothing about whether the body ran and never authorizes a replay (§D.2).
    """


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ResumeRefusalProtocolError(f"duplicate key {key!r}")
        result[key] = value
    return result


def _reject_constant(name: str) -> object:
    raise ResumeRefusalProtocolError(f"non-JSON constant {name}")


def _object(value: object, keys: set[str], where: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ResumeRefusalProtocolError(f"{where} is not an object")
    obj = cast(dict[str, object], value)
    if set(obj) != keys:
        raise ResumeRefusalProtocolError(f"{where} fields {sorted(obj)} are not {sorted(keys)}")
    return obj


def _member[E: StrEnum](enum: type[E], value: object, field: str) -> E:
    if type(value) is not str:
        raise ResumeRefusalProtocolError(f"{field} is not a string")
    try:
        return enum(value)
    except ValueError as exc:
        raise ResumeRefusalProtocolError(f"unknown {field} {value!r}") from exc


def _bool(value: object, field: str) -> bool:
    if type(value) is not bool:
        raise ResumeRefusalProtocolError(f"{field} is not a JSON boolean")
    return value


def _depth(value: object) -> int | None:
    if value is not None and type(value) is not int:
        raise ResumeRefusalProtocolError("depth is not an integer or null")
    return value


def parse(text: str) -> ResumeRefusal:
    """[LAW:parse-dont-validate] The receiving boundary: exactly one closed value, or a loud
    `ResumeRefusalProtocolError`. No default arm, no recovery from prose."""
    try:
        loaded: object = json.loads(
            text, object_pairs_hook=_no_duplicate_keys, parse_constant=_reject_constant
        )
    except (ValueError, RecursionError) as exc:
        # [LAW:no-silent-failure] Besides JSONDecodeError and the hooks' own refusals, the
        # decoder refuses text past its limits (integer digits, nesting) with ValueError or
        # RecursionError; each is still "not one value" and reaches the caller as the protocol
        # error (§D.2), with the decoder's reason chained.
        raise ResumeRefusalProtocolError("malformed JSON") from exc
    envelope = _object(loaded, {"protocol", "refusal"}, "envelope")
    if envelope["protocol"] != PROTOCOL or type(envelope["protocol"]) is not str:
        raise ResumeRefusalProtocolError("unknown protocol")
    raw = envelope["refusal"]
    if not isinstance(raw, dict):
        raise ResumeRefusalProtocolError("refusal is not an object")
    refusal = cast(dict[str, object], raw)
    kind = _member(RefusalKind, refusal.get("kind"), "kind")
    body = _object(refusal, {"kind", "fail_class", *_EXTRA_FIELDS[kind]}, f"{kind} refusal")
    if body["fail_class"] != fail_class(kind) or type(body["fail_class"]) is not str:
        raise ResumeRefusalProtocolError(f"fail_class does not belong to kind {kind}")
    match kind:
        case RefusalKind.HANDLE:
            return HandleRefusal(
                _member(HandleCause, body["cause"], "cause"),
                _bool(body["retryable"], "retryable"),
                _bool(body["indeterminate"], "indeterminate"),
            )
        case RefusalKind.DEPTH:
            return DepthRefusal(_depth(body["depth"]))
        case RefusalKind.CLAIM:
            return ClaimRefusal(_member(RootResumeRefusal, body["reason"], "reason"))
        case _:
            return ValidationRefusal(kind)
