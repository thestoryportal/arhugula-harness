"""Verdict for the required context `pytest (all axis packages) — blocking`.

WO-U09 (WS-10 §12.2) splits the provider-free package suite and the codex-parity suite
into independent CI jobs so neither waits on the other. Branch protection still requires
the one historical context, so a final job keeps that exact name and asks this module
whether the classification plus both constituent results add up to a pass.

The decision is a lookup in `ACCEPTED`, the spec's truth table written as data: every
row that may pass is enumerated with its reason, and anything absent from the table
fails. A failed, canceled or missing classifier yields no `Classification`, so no row
can match it. An unexpected skip, a canceled superseded constituent and a malformed
result string all land in the terminal default. Pending never reaches this module:
the aggregate job `needs:` both constituents, so it runs only after they are terminal.

Stdlib-only under the runner's python3, like `ci_bookkeeping_diff.py`, so the aggregate
adds no uv setup to the critical path. Exit 0 = pass, 1 = fail verdict, 2 = unparseable
input; the workflow treats any non-zero exit as a failed required context.
"""

from __future__ import annotations

import enum
import os
import sys
from collections.abc import Mapping
from dataclasses import dataclass


class JobResult(enum.Enum):
    """`needs.<job>.result` — GitHub's four terminal job states."""

    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class Classification(enum.Enum):
    """The `changes` job's `bookkeeping` output, valid only when that job succeeded."""

    SUBSTANTIVE = "false"
    BOOKKEEPING = "true"


@dataclass(frozen=True)
class Inputs:
    classifier: JobResult
    bookkeeping: str
    package: JobResult
    parity: JobResult


@dataclass(frozen=True)
class Verdict:
    passed: bool
    reason: str


_S, _K = JobResult.SUCCESS, JobResult.SKIPPED

# [LAW:dataflow-not-control-flow] The truth table is data; `decide` is one lookup with a
# failing default, so an unenumerated combination cannot pass by falling through a branch.
ACCEPTED: Mapping[tuple[Classification, JobResult, JobResult], str] = {
    (Classification.SUBSTANTIVE, _S, _S): "substantive diff: package and parity both passed",
    (Classification.BOOKKEEPING, _K, _K): "validated bookkeeping: both suites skipped as expected",
    (Classification.BOOKKEEPING, _S, _S): "validated bookkeeping: conservative full run passed",
}


class InputError(ValueError):
    """A result or variable that is not one of the states this verdict understands."""


def parse_inputs(env: Mapping[str, str]) -> Inputs:
    # [LAW:parse-dont-validate] Raw workflow strings cross here once and leave as enums;
    # an unknown job state is an input error, never a silently failing or passing row.
    def result(var: str) -> JobResult:
        if var not in env:
            raise InputError(f"{var} is not set")
        try:
            return JobResult(env[var])
        except ValueError:
            raise InputError(f"{var}={env[var]!r} is not a terminal job result") from None

    if "BOOKKEEPING" not in env:
        raise InputError("BOOKKEEPING is not set")
    return Inputs(
        classifier=result("CLASSIFIER_RESULT"),
        bookkeeping=env["BOOKKEEPING"],
        package=result("PACKAGE_RESULT"),
        parity=result("PARITY_RESULT"),
    )


def classification(inputs: Inputs) -> Classification | None:
    """The validated classification, or None when it is failed, missing or malformed."""
    if inputs.classifier is not JobResult.SUCCESS:
        return None
    try:
        return Classification(inputs.bookkeeping)
    except ValueError:
        return None


def decide(inputs: Inputs) -> Verdict:
    kind = classification(inputs)
    observed = (
        f"classifier={inputs.classifier.value} bookkeeping={inputs.bookkeeping!r} "
        f"package={inputs.package.value} parity={inputs.parity.value}"
    )
    reason = None if kind is None else ACCEPTED.get((kind, inputs.package, inputs.parity))
    if reason is None:
        return Verdict(False, f"FAIL: no accepted row for {observed}")
    return Verdict(True, f"PASS: {reason} ({observed})")


def main(env: Mapping[str, str]) -> int:
    try:
        verdict = decide(parse_inputs(env))
    except InputError as exc:
        print(f"FAIL: unparseable aggregate input: {exc}", file=sys.stderr)
        return 2
    print(verdict.reason, file=sys.stdout if verdict.passed else sys.stderr)
    return 0 if verdict.passed else 1


if __name__ == "__main__":
    sys.exit(main(os.environ))
