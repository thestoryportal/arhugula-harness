"""Exact CI result binding (WO-U10; plan WP-11; spec WS-10 §12.3-12.5, WS-18).

A green check name proves nothing about WHICH inputs it verified: check runs attach to
a head SHA, so a run against an old base, another repository, an older workflow or a
superseded attempt carries the same display names as the current one. This module
decides whether one recorded run verified exactly the inputs a merge needs.

The run reports its own binding: the CI `changes` job verifies the tested commit's
parents and emits one `::notice title=ci-binding::<json>` annotation. The adapter parses
that annotation plus the run/jobs payloads into `RunEvidence`; `validate_ci_binding`
compares it field by field with an `ExpectedBinding`. Nothing here matches by name.

Stdlib only: the CI `changes` job runs this under the runner's python3 with no uv setup.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

Result = Literal["passed", "held", "failed", "error"]
SubjectKind = Literal["merge_candidate", "landed_commit"]

BINDING_NOTICE_TITLE = "ci-binding"
_SHA = re.compile(r"[0-9a-f]{40}")


class BindingInputError(ValueError):
    """Malformed binding input; the message names the field (WS-18 `invalid_input`)."""


def _sha(value: object, field: str) -> str:
    if not isinstance(value, str) or not _SHA.fullmatch(value):
        raise BindingInputError(f"{field}: expected a full 40-hex SHA, got {value!r}")
    return value


def _positive_int(value: object, field: str) -> int:
    text = str(value)
    if isinstance(value, bool) or not text.isdigit() or int(text) <= 0:
        raise BindingInputError(f"{field}: expected a positive integer, got {value!r}")
    return int(text)


@dataclass(frozen=True)
class JobResult:
    name: str
    job_id: int
    status: str
    conclusion: str | None


@dataclass(frozen=True)
class ExpectedBinding:
    """The inputs a merge decision needs verified. `subject` says what the run must
    have executed: the synthetic merge of head onto base (PR) or the landed SHA (main).
    [LAW:types-are-the-program] the subject kind carries the one discriminator the
    tested-tree check needs; no caller re-derives it from the event name."""

    repository: str
    head_sha: str
    base_sha: str
    subject: SubjectKind
    workflow_path: str
    workflow_blob: str
    required_jobs: frozenset[str]


@dataclass(frozen=True)
class RunEvidence:
    repository: str
    event: str
    run_id: int
    run_attempt: int
    workflow_path: str
    status: str
    head_sha: str
    base_sha: str
    tested_sha: str
    tested_parents: tuple[str, ...]
    workflow_blob: str
    jobs: tuple[JobResult, ...]


@dataclass(frozen=True)
class CiBindingDecision:
    result: Result
    reason_codes: tuple[str, ...]
    detail: str
    run_id: int | None = None
    run_attempt: int | None = None


def _decision(result: Result, code: str, detail: str, run: RunEvidence | None = None):
    return CiBindingDecision(
        result,
        (code,),
        detail,
        None if run is None else run.run_id,
        None if run is None else run.run_attempt,
    )


def identity_mismatches(expected: ExpectedBinding, run: RunEvidence) -> list[str]:
    """Every input field on which `run` verified something other than `expected`."""
    tested_ok = (
        run.tested_parents == (expected.base_sha, expected.head_sha)
        if expected.subject == "merge_candidate"
        else run.event == "push" and run.tested_sha == expected.head_sha
    )
    pairs = {
        "repository": (run.repository, expected.repository),
        "head_sha": (run.head_sha, expected.head_sha),
        "base_sha": (run.base_sha, expected.base_sha),
        "workflow_path": (run.workflow_path, expected.workflow_path),
        "workflow_blob": (run.workflow_blob, expected.workflow_blob),
    }
    bad = [name for name, (seen, want) in pairs.items() if seen != want]
    return bad + ([] if tested_ok else ["tested_tree"])


def validate_ci_binding(expected: ExpectedBinding, observed: RunEvidence) -> CiBindingDecision:
    """Decide whether `observed` verified exactly `expected`.

    Stale identity holds (new verification is needed, the old result stays recorded);
    an unfinished run holds; only a completed run whose every required job concluded
    `success` exactly once passes. An unexpected skip, a missing job or any other
    conclusion fails. Pending is never success and never a test failure (WS-10 §12.5).
    """
    bad = identity_mismatches(expected, observed)
    if bad:
        return _decision("held", "binding_stale", "mismatched " + ",".join(bad), observed)
    by_name: dict[str, list[JobResult]] = {}
    for job in observed.jobs:
        by_name.setdefault(job.name, []).append(job)
    duplicated = sorted(n for n in expected.required_jobs if len(by_name.get(n, [])) > 1)
    if duplicated:
        # [LAW:no-silent-failure] two same-named jobs in one run cannot both be the
        # context; picking either would be choosing whichever is easiest to find.
        return _decision(
            "error", "invalid_input", "duplicate jobs " + ",".join(duplicated), observed
        )
    if observed.status != "completed":
        return _decision("held", "check_pending", f"run {observed.status}", observed)
    not_green = sorted(
        f"{name}={by_name[name][0].conclusion if name in by_name else 'missing'}"
        for name in expected.required_jobs
        if name not in by_name or by_name[name][0].conclusion != "success"
    )
    if not_green:
        return _decision("failed", "check_failed", " ".join(not_green), observed)
    return _decision("passed", "binding_exact", "all required jobs succeeded", observed)


def bind_runs(expected: ExpectedBinding, runs: Sequence[RunEvidence]) -> CiBindingDecision:
    """Select the current run among all runs reported for the head and decide it.

    Only runs whose identity matches compete; the newest (run id, attempt) among them is
    current, so a rerun supersedes its earlier attempt and an older green never outvotes
    a newer red. With no matching run the caller must dispatch verification for these
    exact inputs: the decision is `held`/`binding_stale` with detail `no_matching_run`.
    """
    matching = [run for run in runs if not identity_mismatches(expected, run)]
    if not matching:
        return _decision("held", "binding_stale", "no_matching_run")
    return validate_ci_binding(expected, max(matching, key=lambda r: (r.run_id, r.run_attempt)))


CI_WORKFLOW = ".github/workflows/ci.yml"
_UNBOUND = "0" * 40


def required_contexts(workflow_text: str) -> frozenset[str]:
    """The required contexts the workflow itself declares: every job named `... — blocking`
    (the same rule the split-brain backstop derives required PR contexts from)."""
    names = frozenset(re.findall(r"^    name: (.+ — blocking)\s*$", workflow_text, re.MULTILINE))
    if not names:
        raise BindingInputError("workflow declares no `— blocking` job names")
    return names


def reconcile_pr_binding(
    expected: ExpectedBinding, runs: Sequence[RunEvidence], dispatch: Callable[[], None]
) -> CiBindingDecision:
    """The integration observer's one step: decide the current run, and when none matches
    the exact head/base, dispatch verification for them - unless an unfinished run that has
    not yet reported its binding exists, which may be that verification (reconciled before
    launch instead of duplicated)."""
    decision = bind_runs(expected, runs)
    if decision.detail != "no_matching_run":
        return decision
    if any(r.status != "completed" and r.head_sha == _UNBOUND for r in runs):
        return _decision("held", "check_pending", "unbound run in progress")
    dispatch()
    return _decision("held", "check_pending", "dispatched exact head/base verification")


# --- dispatch inputs ------------------------------------------------------------------


@dataclass(frozen=True)
class DispatchBinding:
    """Dispatch inputs proven equal to the live same-repository open PR."""

    repository: str
    pr_number: int
    head_sha: str
    base_sha: str


DISPATCH_INPUTS = frozenset({"pr_number", "expected_head", "expected_base"})


def validate_dispatch(
    repository: str, inputs: Mapping[str, object], live_pr: Mapping[str, object]
) -> DispatchBinding:
    """[LAW:parse-dont-validate] the one crossing from dispatch inputs to a binding.

    Inputs are exactly pr_number/expected_head/expected_base; `live_pr` is the REST
    `pulls/{n}` payload read after dispatch. A moved head, retargeted base, closed or
    foreign PR raises: such a run must not publish a valid binding.
    """
    if set(inputs) != DISPATCH_INPUTS:
        raise BindingInputError(
            f"dispatch inputs: expected {sorted(DISPATCH_INPUTS)}, got {sorted(inputs)}"
        )
    number = _positive_int(inputs["pr_number"], "pr_number")
    head = _sha(inputs["expected_head"], "expected_head")
    base = _sha(inputs["expected_base"], "expected_base")
    pr_head, pr_base = live_pr["head"], live_pr["base"]
    assert isinstance(pr_head, Mapping) and isinstance(pr_base, Mapping)
    seen = {
        "number": (live_pr.get("number"), number),
        "state": (live_pr.get("state"), "open"),
        "head.repo": ((pr_head.get("repo") or {}).get("full_name"), repository),
        "base.repo": ((pr_base.get("repo") or {}).get("full_name"), repository),
        "head.sha": (pr_head.get("sha"), head),
        "base.sha": (pr_base.get("sha"), base),
    }
    moved = [f"{k} {got!r} != {want!r}" for k, (got, want) in seen.items() if got != want]
    if moved:
        raise BindingInputError("dispatch refused: " + "; ".join(moved))
    return DispatchBinding(repository, number, head, base)


# --- run evidence from GitHub payloads -------------------------------------------------


def parse_run_evidence(
    run: Mapping[str, object], jobs: Sequence[Mapping[str, object]], notice: str | None
) -> RunEvidence:
    """Build `RunEvidence` from the REST run, its attempt's jobs and the binding notice.

    A run without a binding notice (its `changes` job never verified the tested tree)
    records zero SHAs, so it can never match any expected binding.
    """
    recorded = json.loads(notice) if notice is not None else {}
    unknown = _UNBOUND
    repo = run["repository"]
    assert isinstance(repo, Mapping)
    return RunEvidence(
        repository=str(repo["full_name"]),
        event=str(run["event"]),
        run_id=_positive_int(run["id"], "run.id"),
        run_attempt=_positive_int(run["run_attempt"], "run.run_attempt"),
        workflow_path=str(run["path"]).split("@", 1)[0],
        status=str(run["status"]),
        head_sha=_sha(recorded.get("head", unknown), "notice.head"),
        base_sha=_sha(recorded.get("base", unknown), "notice.base"),
        tested_sha=_sha(recorded.get("tested", unknown), "notice.tested"),
        tested_parents=tuple(_sha(p, "notice.parents") for p in recorded.get("parents", [])),
        workflow_blob=_sha(recorded.get("workflow_blob", unknown), "notice.workflow_blob"),
        jobs=tuple(
            JobResult(str(j["name"]), int(str(j["id"])), str(j["status"]), j.get("conclusion"))  # type: ignore[arg-type]
            for j in jobs
        ),
    )


# --- bounded observation (WS-10 §12.5) -------------------------------------------------

INITIAL_POLL_S = 15.0
MAX_POLL_S = 60.0
PENDING_TIMEOUT_S = 30 * 60.0


@dataclass(frozen=True)
class Snapshot:
    """One read of a named run/attempt; `retry_after_s` carries a service backoff."""

    state: str
    retry_after_s: float = 0.0


@dataclass(frozen=True)
class Terminal:
    last: Snapshot


@dataclass(frozen=True)
class PendingTimeout:
    """Still not terminal after the bound: neither a test success nor a test failure.
    The same run remains the next observation; no duplicate run is launched."""

    last: Snapshot
    waited_s: float


def next_interval(previous_s: float | None, changed: bool, retry_after_s: float) -> float:
    """15 s after a change, doubling to at most 60 s while unchanged; a longer service
    retry instruction always wins."""
    base = INITIAL_POLL_S if previous_s is None or changed else min(previous_s * 2, MAX_POLL_S)
    return max(base, retry_after_s)


def observe_run(
    read: Callable[[], Snapshot],
    clock: Callable[[], float],
    sleep: Callable[[float], None],
) -> Terminal | PendingTimeout:
    start = clock()
    interval: float | None = None
    previous: str | None = None
    while True:
        snap = read()
        if snap.state == "completed":
            return Terminal(snap)
        waited = clock() - start
        if waited >= PENDING_TIMEOUT_S:
            return PendingTimeout(snap, waited)
        interval = next_interval(interval, snap.state != previous, snap.retry_after_s)
        previous = snap.state
        sleep(interval)


def pending_timeout_decision(timeout: PendingTimeout) -> CiBindingDecision:
    return _decision("held", "check_pending", f"pending_timeout after {timeout.waited_s:.0f}s")


# --- GitHub adapter and CLI (effects live only below) ---------------------------------


def _gh_json(*args: str) -> object:
    proc = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=60, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {proc.stderr.strip()}")
    return json.loads(proc.stdout)


def fetch_runs(repository: str, head_sha: str, workflow_file: str) -> list[RunEvidence]:
    """Every run of `workflow_file` for `head_sha`, with its jobs and binding notice."""
    page = _gh_json(
        "api",
        f"repos/{repository}/actions/workflows/{workflow_file}/runs?head_sha={head_sha}&per_page=100",
    )
    assert isinstance(page, dict)
    evidence = []
    for run in page["workflow_runs"]:
        jobs_page = _gh_json(
            "api",
            f"repos/{repository}/actions/runs/{run['id']}/attempts/{run['run_attempt']}/jobs?per_page=100",
        )
        assert isinstance(jobs_page, dict)
        jobs = jobs_page["jobs"]
        notices = [
            a["message"]
            for job in jobs
            for a in _gh_json("api", f"repos/{repository}/check-runs/{job['id']}/annotations")  # type: ignore[union-attr]
            if a.get("title") == BINDING_NOTICE_TITLE
        ]
        if len(notices) > 1:
            raise BindingInputError(f"run {run['id']}: {len(notices)} binding notices")
        evidence.append(parse_run_evidence(run, jobs, notices[0] if notices else None))
    return evidence


def _cmd_verify_dispatch(args: argparse.Namespace) -> int:
    inputs = {
        "pr_number": args.pr_number,
        "expected_head": args.expected_head,
        "expected_base": args.expected_base,
    }
    live = _gh_json(
        "api", f"repos/{args.repository}/pulls/{_positive_int(args.pr_number, 'pr_number')}"
    )
    assert isinstance(live, dict)
    try:
        binding = validate_dispatch(args.repository, inputs, live)
    except BindingInputError as exc:
        print(f"ci-binding: {exc}", file=sys.stderr)
        return 3
    print(json.dumps(binding.__dict__, sort_keys=True))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    verify = sub.add_parser(
        "verify-dispatch", help="prove dispatch inputs equal the live PR (exit 3 if not)"
    )
    for flag in ("--repository", "--pr-number", "--expected-head", "--expected-base"):
        verify.add_argument(flag, required=True)
    verify.set_defaults(run=_cmd_verify_dispatch)
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    raise SystemExit(main())
