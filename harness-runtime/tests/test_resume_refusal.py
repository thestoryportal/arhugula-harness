"""U-RT-160b: the closed `harness.resume-refusal.v1` value, its projection and its strict parser.

Runtime spec v1.137 §D.1 + §D.5. Each test builds the real typed refusal `resume()` raises and
asserts the exact serialized object, so the kind/fail_class table, the copied flags and the
recorded depth are pinned against the spec text rather than against the module's own tables.
The parser tests feed hand-written JSON. No CLI, journal or MCP path is exercised here: those
are criterion 8's live witnesses, owed by the `harness resume` subcommand (plan v2.68 160b).
"""

from __future__ import annotations

import json
from typing import Any

import pytest
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
    RootResumeRefusal,
)
from harness_runtime.lifecycle.journal_workflow_pause_store import PauseJournalReadCause
from harness_runtime.resume_refusal import (
    HandleCause,
    ResumeRefusalError,
    ResumeRefusalProtocolError,
    parse,
    project,
    to_json,
)

PROTOCOL = "harness.resume-refusal.v1"
CANARY = "/srv/tenant-acme/secret-sk-CANARY-7f3a/pause-journal"


def _handle(
    cause: PauseJournalReadCause, *, retryable: bool, indeterminate: bool
) -> ResumeHandleUnknownError:
    return ResumeHandleUnknownError(
        f"read failed at {CANARY}", cause=cause, retryable=retryable, indeterminate=indeterminate
    )


def _claim(reason: RootResumeRefusal) -> ResumeClaimRefusedError:
    error = ResumeClaimRefusedError(reason)
    error.__cause__ = OSError(f"EACCES {CANARY}")
    return error


# The §D.1 table and the §D.5 row, transcribed: (typed refusal, exact `refusal` object).
SPEC_CASES: list[tuple[ResumeRefusalError, dict[str, object]]] = [
    (
        ResumeArgsError(f"both snapshot and handle given for {CANARY}"),
        {"kind": "arguments", "fail_class": "RT-FAIL-RESUME-ARGS"},
    ),
    (
        _handle(PauseJournalReadCause.READ_ERROR, retryable=True, indeterminate=False),
        {
            "kind": "handle",
            "fail_class": "RT-FAIL-RESUME-HANDLE-UNKNOWN",
            "cause": "read-error",
            "retryable": True,
            "indeterminate": False,
        },
    ),
    (
        ResumeDirectChildHandleError(depth=2),
        {"kind": "depth", "fail_class": "RT-FAIL-RESUME-DIRECT-CHILD-HANDLE", "depth": 2},
    ),
    (
        ResumeProtocolNotBoundError(f"no protocol in {CANARY}"),
        {"kind": "protocol-not-bound", "fail_class": "RT-FAIL-RESUME-PROTOCOL-NOT-BOUND"},
    ),
    (
        ResumePauseStateStaleError(f"stale at {CANARY}", claimed_token="tok-CANARY-digest"),
        {"kind": "pause-state-stale", "fail_class": "RT-FAIL-RESUME-PAUSE-STATE-STALE"},
    ),
    (
        ResumeWorkflowMismatchError(f"workflow wf-CANARY at {CANARY}"),
        {"kind": "workflow-mismatch", "fail_class": "RT-FAIL-RESUME-WORKFLOW-MISMATCH"},
    ),
    (
        ResumeStepIndexOutOfRangeError(f"step 9 of 3 in {CANARY}"),
        {
            "kind": "step-index-out-of-range",
            "fail_class": "RT-FAIL-RESUME-STEP-INDEX-OUT-OF-RANGE",
        },
    ),
    (
        _claim(RootResumeRefusal.CLAIM_BUSY),
        {"kind": "claim", "fail_class": "RT-FAIL-RESUME-CLAIM-REFUSED", "reason": "claim-busy"},
    ),
    (
        ResumePauseRecordSupersededError(f"superseded in {CANARY}"),
        {
            "kind": "pause-record-superseded",
            "fail_class": "RT-FAIL-RESUME-PAUSE-RECORD-SUPERSEDED",
        },
    ),
]


def _wire(error: ResumeRefusalError) -> dict[str, Any]:
    loaded: dict[str, Any] = json.loads(to_json(project(error)))
    return loaded


@pytest.mark.parametrize(("error", "expected"), SPEC_CASES, ids=lambda c: type(c).__name__)
def test_each_typed_refusal_serializes_to_its_exact_spec_arm(
    error: ResumeRefusalError, expected: dict[str, object]
) -> None:
    assert _wire(error) == {"protocol": PROTOCOL, "refusal": expected}


def test_the_nine_arms_are_distinct_and_each_round_trips_through_the_parser() -> None:
    values = [project(error) for error, _ in SPEC_CASES]
    assert len({v.kind for v in values}) == 9
    assert [parse(to_json(v)) for v in values] == values


def test_the_spec_example_value_parses() -> None:
    text = (
        '{"protocol":"harness.resume-refusal.v1","refusal":{"kind":"handle",'
        '"fail_class":"RT-FAIL-RESUME-HANDLE-UNKNOWN","cause":"read-error",'
        '"retryable":false,"indeterminate":false}}'
    )
    refusal = parse(text)
    assert to_json(refusal) == text


@pytest.mark.parametrize("cause", list(PauseJournalReadCause), ids=str)
@pytest.mark.parametrize("retryable", [True, False])
@pytest.mark.parametrize("indeterminate", [True, False])
def test_handle_flags_are_copied_from_the_typed_error_not_derived_from_the_cause(
    cause: PauseJournalReadCause, retryable: bool, indeterminate: bool
) -> None:
    body = _wire(_handle(cause, retryable=retryable, indeterminate=indeterminate))["refusal"]
    assert (body["cause"], body["retryable"], body["indeterminate"]) == (
        cause.value,
        retryable,
        indeterminate,
    )


def test_handle_cause_is_closed_at_five_and_supersession_is_its_own_arm() -> None:
    assert {c.value for c in HandleCause} == {
        "absent",
        "empty-journal",
        "read-error",
        "corrupt-latest",
        "workflow-mismatch",
    }
    superseded = _wire(ResumePauseRecordSupersededError("x"))["refusal"]
    assert superseded == {
        "kind": "pause-record-superseded",
        "fail_class": "RT-FAIL-RESUME-PAUSE-RECORD-SUPERSEDED",
    }


def test_durable_read_workflow_mismatch_cause_and_mismatch_arm_stay_separate() -> None:
    cause = _wire(
        _handle(PauseJournalReadCause.WORKFLOW_MISMATCH, retryable=False, indeterminate=False)
    )["refusal"]
    arm = _wire(ResumeWorkflowMismatchError("x"))["refusal"]
    assert (cause["kind"], cause["cause"]) == ("handle", "workflow-mismatch")
    assert arm == {"kind": "workflow-mismatch", "fail_class": "RT-FAIL-RESUME-WORKFLOW-MISMATCH"}


@pytest.mark.parametrize(("recorded", "wire"), [(None, None), (0, 0), (1, 1), (3, 3)])
def test_depth_is_the_recorded_integer_and_unknown_stays_null(
    recorded: int | None, wire: int | None
) -> None:
    body = _wire(ResumeDirectChildHandleError(depth=recorded))["refusal"]
    assert body["depth"] == wire
    assert type(body["depth"]) is type(wire)


@pytest.mark.parametrize("reason", list(RootResumeRefusal), ids=str)
def test_each_root_claim_reason_is_carried(reason: RootResumeRefusal) -> None:
    assert _wire(_claim(reason))["refusal"]["reason"] == reason.value


def test_wrong_tenant_and_absent_project_identically() -> None:
    absent = ResumeHandleUnknownError("no record", cause=PauseJournalReadCause.ABSENT)
    wrong_tenant = ResumeHandleUnknownError(
        "no record for tenant-acme", cause=PauseJournalReadCause.ABSENT
    )
    assert to_json(project(absent)) == to_json(project(wrong_tenant))


@pytest.mark.parametrize(("error", "_expected"), SPEC_CASES, ids=lambda c: type(c).__name__)
def test_no_message_path_secret_tenant_or_token_reaches_the_output(
    error: ResumeRefusalError, _expected: object
) -> None:
    text = to_json(project(error))
    for canary in ("CANARY", "/srv", "tenant-acme", "secret", "tok-"):
        assert canary not in text


def test_an_unrelated_failure_is_not_projected_as_a_refusal() -> None:
    with pytest.raises(AssertionError):
        project(RuntimeError("bootstrap failed"))  # pyright: ignore[reportArgumentType]


def _envelope(refusal: dict[str, object], **top: object) -> str:
    return json.dumps({"protocol": PROTOCOL, "refusal": refusal} | top)


HANDLE = {
    "kind": "handle",
    "fail_class": "RT-FAIL-RESUME-HANDLE-UNKNOWN",
    "cause": "corrupt-latest",
    "retryable": False,
    "indeterminate": True,
}

REFUSED_BY_THE_PARSER: dict[str, str] = {
    "malformed JSON": '{"protocol":"harness.resume-refusal.v1","refusal":',
    "trailing data": _envelope(HANDLE) + " x",
    "not an object": "[]",
    "prose": "RT-FAIL-RESUME-CLAIM-REFUSED:claim-busy: the durable root record was not admitted",
    "unknown protocol": json.dumps({"protocol": "harness.resume-refusal.v2", "refusal": HANDLE}),
    "missing protocol": json.dumps({"refusal": HANDLE}),
    "extra envelope field": _envelope(HANDLE, run_id="r-1"),
    "refusal not an object": json.dumps({"protocol": PROTOCOL, "refusal": "handle"}),
    "unknown kind": _envelope({"kind": "timeout", "fail_class": "RT-FAIL-RESUME-ARGS"}),
    "missing kind": _envelope({"fail_class": "RT-FAIL-RESUME-ARGS"}),
    "kind not a string": _envelope({"kind": 1, "fail_class": "RT-FAIL-RESUME-ARGS"}),
    "mismatched fail_class": _envelope(
        {"kind": "arguments", "fail_class": "RT-FAIL-RESUME-PROTOCOL-NOT-BOUND"}
    ),
    "superseded with the handle fail_class": _envelope(
        {"kind": "pause-record-superseded", "fail_class": "RT-FAIL-RESUME-HANDLE-UNKNOWN"}
    ),
    "validation arm with an extra field": _envelope(
        {"kind": "arguments", "fail_class": "RT-FAIL-RESUME-ARGS", "cause": "absent"}
    ),
    "handle missing a flag": _envelope({k: v for k, v in HANDLE.items() if k != "indeterminate"}),
    "quoted boolean": _envelope(HANDLE | {"retryable": "false"}),
    "integer boolean": _envelope(HANDLE | {"indeterminate": 1}),
    "unknown cause": _envelope(HANDLE | {"cause": "timeout"}),
    "superseded as a handle cause": _envelope(HANDLE | {"cause": "superseded"}),
    "handle carrying a claim reason": _envelope(HANDLE | {"reason": "claim-busy"}),
    "claim carrying a cause": _envelope(
        {
            "kind": "claim",
            "fail_class": "RT-FAIL-RESUME-CLAIM-REFUSED",
            "reason": "claim-busy",
            "cause": "absent",
        }
    ),
    "unknown reason": _envelope(
        {"kind": "claim", "fail_class": "RT-FAIL-RESUME-CLAIM-REFUSED", "reason": "timeout"}
    ),
    "boolean depth": _envelope(
        {"kind": "depth", "fail_class": "RT-FAIL-RESUME-DIRECT-CHILD-HANDLE", "depth": True}
    ),
    "string depth": _envelope(
        {"kind": "depth", "fail_class": "RT-FAIL-RESUME-DIRECT-CHILD-HANDLE", "depth": "1"}
    ),
    "float depth": _envelope(
        {"kind": "depth", "fail_class": "RT-FAIL-RESUME-DIRECT-CHILD-HANDLE", "depth": 1.0}
    ),
    "omitted depth": _envelope(
        {"kind": "depth", "fail_class": "RT-FAIL-RESUME-DIRECT-CHILD-HANDLE"}
    ),
    "duplicate key": (
        # Last-wins would leave a valid `arguments` value; only the duplicate makes it invalid.
        '{"protocol":"harness.resume-refusal.v1","refusal":{"kind":"claim",'
        '"kind":"arguments","fail_class":"RT-FAIL-RESUME-ARGS"}}'
    ),
    "non-JSON constant": _envelope(
        {"kind": "depth", "fail_class": "RT-FAIL-RESUME-DIRECT-CHILD-HANDLE", "depth": 0}
    ).replace('"depth": 0', '"depth": NaN'),
}


@pytest.mark.parametrize("text", REFUSED_BY_THE_PARSER.values(), ids=REFUSED_BY_THE_PARSER.keys())
def test_the_strict_parser_refuses_loudly(text: str) -> None:
    with pytest.raises(ResumeRefusalProtocolError):
        parse(text)
