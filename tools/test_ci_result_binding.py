"""WO-U10: exact CI result binding and metadata-safe event routing (WP-11, WS-10 §12.3-12.5).

Three lenses. The binding lens feeds `validate_ci_binding`/`bind_runs` evidence parsed from
recorded GitHub REST payloads and asserts no name-only match can pass. The dispatch lens
asserts the three inputs must equal the live same-repository PR. The routing lens loads the
real workflow files, decides which workflows an event triggers and evaluates their actual
concurrency expressions, so a body edit, a retarget and two landings are judged by the
workflows that ship rather than by a restatement of them."""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ci_result_binding import (
    MAX_POLL_S,
    PENDING_TIMEOUT_S,
    BindingInputError,
    ExpectedBinding,
    PendingTimeout,
    Snapshot,
    Terminal,
    bind_runs,
    observe_run,
    parse_run_evidence,
    pending_timeout_decision,
    reconcile_pr_binding,
    required_contexts,
    validate_ci_binding,
    validate_dispatch,
)

_REPO = Path(__file__).resolve().parent.parent
_WORKFLOWS = _REPO / ".github" / "workflows"
REPO = "thestoryportal/arhugula-build-eval"
HEAD, BASE, NEW_BASE, MERGE, BLOB = ("a" * 40, "b" * 40, "c" * 40, "d" * 40, "e" * 40)
REQUIRED = frozenset({"pytest (all axis packages) — blocking", "ruff (lint + format) — blocking"})


def _run_payload(
    run_id: int, attempt: int = 1, status: str = "completed", event: str = "pull_request"
):
    # Shape of GET /repos/{o}/{r}/actions/runs/{id} (fields this module reads).
    return {
        "id": run_id,
        "run_attempt": attempt,
        "event": event,
        "status": status,
        "conclusion": "success" if status == "completed" else None,
        "path": ".github/workflows/ci.yml@refs/pull/1651/merge",
        "head_sha": HEAD,
        "repository": {"full_name": REPO},
        "display_title": "feat: something",
    }


def _jobs(conclusion: str = "success", names=REQUIRED):
    return [
        {"id": 9000 + i, "name": n, "status": "completed", "conclusion": conclusion}
        for i, n in enumerate(sorted(names))
    ]


def _notice(base: str = BASE, head: str = HEAD, parents=None, tested: str = MERGE) -> str:
    parents = [base, head] if parents is None else parents
    return (
        f'{{"head": "{head}", "base": "{base}", "tested": "{tested}", '
        f'"parents": {list(parents)!r}, "workflow_blob": "{BLOB}"}}'.replace("'", '"')
    )


def _evidence(
    run_id=100,
    attempt=1,
    status="completed",
    conclusion="success",
    base=BASE,
    notice=True,
    names=REQUIRED,
):
    return parse_run_evidence(
        _run_payload(run_id, attempt, status),
        _jobs(conclusion, names),
        _notice(base) if notice else None,
    )


def _expected(base: str = BASE) -> ExpectedBinding:
    return ExpectedBinding(
        REPO, HEAD, base, "merge_candidate", ".github/workflows/ci.yml", BLOB, REQUIRED
    )


# --- binding lens ----------------------------------------------------------------------


def test_duplicate_context_name_cannot_select_wrong_base():
    old_base_green = _evidence(run_id=100, base=BASE)
    # Same head, same job names, all green - but verified against the previous base.
    assert validate_ci_binding(_expected(NEW_BASE), old_base_green).result != "passed"
    decision = bind_runs(_expected(NEW_BASE), [old_base_green])
    assert (decision.result, decision.reason_codes, decision.detail) == (
        "held",
        ("binding_stale",),
        "no_matching_run",
    )


def test_base_retarget_requires_matching_full_run():
    old = _evidence(run_id=100, base=BASE)
    assert bind_runs(_expected(BASE), [old]).result == "passed"
    # Retarget: the old green stays recorded but no longer binds; only a full run on
    # the new base does, and a red one there is a failure, not an older green.
    assert bind_runs(_expected(NEW_BASE), [old]).result == "held"
    new_green = _evidence(run_id=101, base=NEW_BASE)
    assert bind_runs(_expected(NEW_BASE), [old, new_green]).run_id == 101
    assert bind_runs(_expected(NEW_BASE), [old, new_green]).result == "passed"
    new_red = _evidence(run_id=101, base=NEW_BASE, conclusion="failure")
    assert bind_runs(_expected(NEW_BASE), [old, new_red]).result == "failed"


def test_newest_matching_attempt_is_current():
    green_1 = _evidence(run_id=100, attempt=1)
    red_2 = _evidence(run_id=100, attempt=2, conclusion="failure")
    assert bind_runs(_expected(), [red_2, green_1]).result == "failed"
    rerun_pending = _evidence(run_id=100, attempt=3, status="in_progress")
    assert bind_runs(_expected(), [green_1, rerun_pending]).result == "held"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("repository", "someone/fork"),
        ("workflow_blob", "f" * 40),
        ("workflow_path", ".github/workflows/other.yml"),
        ("tested_parents", (BASE, "f" * 40)),
        ("head_sha", "f" * 40),
    ],
)
def test_any_identity_mismatch_holds_as_stale(field, value):
    decision = validate_ci_binding(_expected(), replace(_evidence(), **{field: value}))
    assert (decision.result, decision.reason_codes) == ("held", ("binding_stale",))


def test_run_without_binding_notice_never_binds():
    assert bind_runs(_expected(), [_evidence(notice=False)]).detail == "no_matching_run"


def test_landed_commit_binds_only_its_own_push_run():
    landed = ExpectedBinding(
        REPO, HEAD, BASE, "landed_commit", ".github/workflows/ci.yml", BLOB, REQUIRED
    )
    push = parse_run_evidence(
        _run_payload(7, event="push"), _jobs(), _notice(parents=[BASE], tested=HEAD)
    )
    assert validate_ci_binding(landed, push).result == "passed"
    assert validate_ci_binding(landed, replace(push, event="pull_request")).result == "held"
    assert validate_ci_binding(landed, replace(push, tested_sha=MERGE)).result == "held"


@pytest.mark.parametrize(
    ("conclusion", "result"),
    [
        ("failure", "failed"),
        ("cancelled", "failed"),
        ("skipped", "failed"),
        ("timed_out", "failed"),
    ],
)
def test_only_success_passes_a_required_job(conclusion, result):
    assert validate_ci_binding(_expected(), _evidence(conclusion=conclusion)).result == result


def test_missing_required_job_fails_completed_run():
    partial = _evidence(names=frozenset({"ruff (lint + format) — blocking"}))
    decision = validate_ci_binding(_expected(), partial)
    assert decision.result == "failed"
    assert "pytest (all axis packages) — blocking=missing" in decision.detail


def test_duplicate_required_job_in_one_run_is_an_error():
    run = _evidence()
    doubled = replace(run, jobs=(*run.jobs, replace(run.jobs[0], job_id=1, conclusion="failure")))
    assert validate_ci_binding(_expected(), doubled).reason_codes == ("invalid_input",)


def test_unfinished_run_is_pending_not_a_result():
    decision = validate_ci_binding(_expected(), _evidence(status="in_progress"))
    assert (decision.result, decision.reason_codes) == ("held", ("check_pending",))


def test_malformed_notice_is_rejected_loudly():
    with pytest.raises(BindingInputError, match=r"notice\.base"):
        parse_run_evidence(_run_payload(1), _jobs(), _notice(base="main"))


def test_retarget_dispatches_once_and_reconciles_pending_run():
    dispatched: list[int] = []
    old = _evidence(run_id=100, base=BASE)
    held = reconcile_pr_binding(_expected(NEW_BASE), [old], lambda: dispatched.append(1))
    assert (held.result, held.detail, dispatched) == (
        "held",
        "dispatched exact head/base verification",
        [1],
    )
    # The dispatched run is queued and has not reported its binding yet: no second launch.
    queued = _evidence(run_id=101, status="queued", notice=False)
    again = reconcile_pr_binding(_expected(NEW_BASE), [old, queued], lambda: dispatched.append(2))
    assert (again.result, again.reason_codes, dispatched) == ("held", ("check_pending",), [1])
    # Once it reports the new base and succeeds, the binding passes without dispatch.
    done = _evidence(run_id=101, base=NEW_BASE)
    assert (
        reconcile_pr_binding(_expected(NEW_BASE), [old, done], lambda: dispatched.append(3)).result
        == "passed"
    )
    assert dispatched == [1]


def test_required_contexts_come_from_the_shipped_workflow():
    names = required_contexts((_WORKFLOWS / "ci.yml").read_text())
    assert REQUIRED <= names
    assert "classify diff (bookkeeping fast path)" not in names
    with pytest.raises(BindingInputError):
        required_contexts("jobs: {}\n")


# --- bounded observation ---------------------------------------------------------------


class FakeClock:
    def __init__(self):
        self.now = 0.0
        self.sleeps: list[float] = []

    def clock(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


def test_pending_timeout_after_thirty_minutes_is_neither_pass_nor_fail():
    fake = FakeClock()
    states = iter(["queued", "in_progress"])
    outcome = observe_run(lambda: Snapshot(next(states, "in_progress")), fake.clock, fake.sleep)
    assert isinstance(outcome, PendingTimeout)
    assert outcome.waited_s >= PENDING_TIMEOUT_S
    # 15 s initially and again after the queued->in_progress change, then doubling to 60.
    assert fake.sleeps[:4] == [15.0, 15.0, 30.0, 60.0]
    assert max(fake.sleeps) == MAX_POLL_S
    decision = pending_timeout_decision(outcome)
    assert decision.result not in ("passed", "failed")
    assert decision.reason_codes == ("check_pending",)


def test_service_backoff_is_honored_and_terminal_returns():
    fake = FakeClock()
    reads = iter(
        [
            Snapshot("in_progress", retry_after_s=120.0),
            Snapshot("in_progress"),
            Snapshot("completed"),
        ]
    )
    outcome = observe_run(lambda: next(reads), fake.clock, fake.sleep)
    assert isinstance(outcome, Terminal)
    assert fake.sleeps == [120.0, MAX_POLL_S]  # unchanged after backoff: capped, not reset


# --- dispatch lens ---------------------------------------------------------------------


def _live_pr(head=HEAD, base=BASE, state="open", head_repo=REPO, number=1651):
    # Shape of GET /repos/{o}/{r}/pulls/{n}.
    return {
        "number": number,
        "state": state,
        "head": {"sha": head, "repo": {"full_name": head_repo}},
        "base": {"sha": base, "repo": {"full_name": REPO}},
    }


_INPUTS = {"pr_number": "1651", "expected_head": HEAD, "expected_base": BASE}


def test_dispatch_binds_exact_live_pr():
    binding = validate_dispatch(REPO, _INPUTS, _live_pr())
    assert (binding.pr_number, binding.head_sha, binding.base_sha) == (1651, HEAD, BASE)


def test_dispatch_rejects_moved_head():
    with pytest.raises(BindingInputError, match=r"head\.sha"):
        validate_dispatch(REPO, _INPUTS, _live_pr(head="f" * 40))


@pytest.mark.parametrize(
    ("live", "inputs", "field"),
    [
        (_live_pr(base=NEW_BASE), _INPUTS, "base.sha"),
        (_live_pr(head_repo="someone/fork"), _INPUTS, "head.repo"),
        (_live_pr(state="closed"), _INPUTS, "state"),
        (_live_pr(number=7), _INPUTS, "number"),
        (_live_pr(), {**_INPUTS, "skip_tests": "true"}, "dispatch inputs"),
        (_live_pr(), {**_INPUTS, "expected_head": "main"}, "expected_head"),
        (_live_pr(), {**_INPUTS, "pr_number": "0"}, "pr_number"),
    ],
)
def test_dispatch_refuses_every_mismatch(live, inputs, field):
    with pytest.raises(BindingInputError, match=re.escape(field)):
        validate_dispatch(REPO, inputs, live)


def test_verify_dispatch_cli_refuses_without_valid_inputs():
    proc = subprocess.run(
        [
            sys.executable,
            str(_REPO / "tools" / "ci_result_binding.py"),
            "verify-dispatch",
            "--repository",
            REPO,
            "--pr-number",
            "x",
            "--expected-head",
            HEAD,
            "--expected-base",
            BASE,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode != 0
    assert "pr_number" in proc.stderr


# --- routing lens: the shipped workflow files ------------------------------------------


def _workflow(name: str) -> dict[str, Any]:
    return yaml.safe_load((_WORKFLOWS / name).read_text())


def _on(wf: dict[str, Any]) -> dict[str, Any]:
    return wf.get("on", wf.get(True))  # PyYAML reads the bare `on` key as boolean True


def _triggers(wf: dict[str, Any], event: str, action: str | None, ref: str = "") -> bool:
    spec = _on(wf).get(event, "absent")
    if spec == "absent":
        return False
    spec = spec or {}
    if action is not None and "types" in spec and action not in spec["types"]:
        return False
    return "branches" not in spec or ref.removeprefix("refs/heads/") in spec["branches"]


_TOKEN = re.compile(r"\s*('[^']*'|==|!=|&&|\|\||[A-Za-z_][\w.\-]*)")


def _evaluate(expr: str, ctx: dict[str, Any]) -> Any:
    """GitHub expression subset used by the concurrency keys: paths, 'literals', ==, !=,
    && and || with JavaScript-style operand results (precedence == > && > ||)."""
    tokens = [m.group(1) for m in _TOKEN.finditer(expr)]
    assert "".join(tokens) == re.sub(r"\s+", "", expr), f"unsupported expression: {expr}"

    def atom(t: str) -> Any:
        if t.startswith("'"):
            return t[1:-1]
        value: Any = ctx
        for part in t.split("."):
            value = value.get(part) if isinstance(value, dict) else None
        return value

    def split(seq: list[str], op: str) -> list[list[str]]:
        out: list[list[str]] = [[]]
        for t in seq:
            out.append([]) if t == op else out[-1].append(t)
        return out

    def compare(seq: list[str]) -> Any:
        if len(seq) == 3 and seq[1] in ("==", "!="):
            return (atom(seq[0]) == atom(seq[2])) == (seq[1] == "==")
        assert len(seq) == 1, seq
        return atom(seq[0])

    def conj(seq: list[str]) -> Any:
        value: Any = True
        for part in split(seq, "&&"):
            value = compare(part)
            if not value:
                return value
        return value

    value: Any = None
    for part in split(tokens, "||"):
        value = conj(part)
        if value:
            return value
    return value


def _render(template: Any, ctx: dict[str, Any]) -> str:
    return re.sub(r"\$\{\{(.*?)\}\}", lambda m: str(_evaluate(m.group(1), ctx)), str(template))


def _ctx(
    event: str,
    workflow: str,
    *,
    sha: str = MERGE,
    pr: int | None = None,
    ref: str = "",
    inputs=None,
):
    pull = {"number": pr} if pr is not None and event == "pull_request" else None
    return {
        "github": {
            "event_name": event,
            "workflow": workflow,
            "sha": sha,
            "ref": ref,
            "repository": REPO,
            "event": {"pull_request": pull},
        },
        "inputs": inputs or {},
    }


def _group(wf: dict[str, Any], ctx: dict[str, Any]) -> tuple[str, bool]:
    conc = wf["concurrency"]
    return _render(conc["group"], ctx), _render(conc["cancel-in-progress"], ctx) == "True"


def test_body_edit_preserves_inflight_code_run():
    ci, meta = _workflow("ci.yml"), _workflow("pr-metadata.yml")
    # A body or title edit arrives as pull_request/edited.
    assert not _triggers(ci, "pull_request", "edited")
    assert _triggers(meta, "pull_request", "edited")
    # The metadata run lives in its own group, so it can never cancel the code run.
    code_group, _ = _group(ci, _ctx("pull_request", ci["name"], pr=1651))
    meta_group, _ = _group(meta, _ctx("pull_request", meta["name"], pr=1651))
    assert code_group != meta_group
    # And it cannot publish under a required code-check name.
    meta_names = {job["name"] for job in meta["jobs"].values()}
    ci_names = {job["name"] for job in ci["jobs"].values()}
    assert not meta_names & ci_names


def test_code_events_still_trigger_code_verification():
    ci = _workflow("ci.yml")
    for action in ("opened", "synchronize", "reopened"):
        assert _triggers(ci, "pull_request", action)
    assert _triggers(ci, "push", None, "refs/heads/main")
    assert set(_on(ci)["workflow_dispatch"]["inputs"]) == {
        "pr_number",
        "expected_head",
        "expected_base",
    }


def test_title_edit_reruns_the_title_dependent_check():
    meta = _workflow("pr-metadata.yml")
    commands = " ".join(
        str(step.get("run", "")) for job in meta["jobs"].values() for step in job["steps"]
    )
    assert "roadmap_status_refresh.py --check" in commands
    assert "--shape-title-env PR_TITLE" in commands


def test_main_sha_groups_do_not_cancel_each_other():
    ci = _workflow("ci.yml")
    landing_a = _group(ci, _ctx("push", ci["name"], sha="1" * 40, ref="refs/heads/main"))
    landing_b = _group(ci, _ctx("push", ci["name"], sha="2" * 40, ref="refs/heads/main"))
    assert landing_a[0] != landing_b[0]
    assert not landing_a[1] and not landing_b[1]


def test_pr_group_supersedes_only_the_same_pr():
    ci = _workflow("ci.yml")
    first = _group(
        ci, _ctx("pull_request", ci["name"], sha="1" * 40, pr=1651, ref="refs/pull/1651/merge")
    )
    second = _group(
        ci, _ctx("pull_request", ci["name"], sha="2" * 40, pr=1651, ref="refs/pull/1651/merge")
    )
    other = _group(ci, _ctx("pull_request", ci["name"], pr=1652, ref="refs/pull/1652/merge"))
    dispatch = _group(
        ci,
        _ctx(
            "workflow_dispatch", ci["name"], ref="refs/heads/feat/x", inputs={"pr_number": "1651"}
        ),
    )
    assert first == second and first[1]
    assert dispatch[0] == first[0]  # a retarget dispatch supersedes that PR's older-base run
    assert other[0] != first[0]
