#!/usr/bin/env python3
"""The edge of the C-HE-31 mechanized checks: gather a `Subject` from git and gh, run the
checks, append the C-HE-24 rows, report.

  check [--base REF]  `just mech-check`: the working tree against REF (default origin/main).
                      Exit 1 iff a BLOCKING check reports a warn or hard finding.
  replay CHECK_ID     `just mech-replay`: run CHECK_ID over the last 20 merged arcs (each a
                      detached worktree of its squash commit, measured once per arc,
                      checker implementation and PR body as fetched), then
                      evaluate §4(a). Exit 0 promoted; 1 not promoted (unmeasured, pending
                      adjudication, or a rejected finding).
  demote              `just lanes-verify`: record each blocking check's windows and apply any
                      due demotion (§4(b)/(c)). Exit 0.
  demotion-due        CI: exit 1 iff a blocking check's windows already require a demotion
                      that has not been recorded -- read-only, so it can run where state does
                      not persist.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
import tempfile
from collections.abc import Callable, Iterator, Sequence
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import finding_record as fr
import review_wrapper_common as rwc

from mechanized_checks import CHECKS, core

PrBody = Callable[[Path, "str | None"], "str | None"]
SQUASH_SUBJECT = re.compile(r"\(#(\d+)\)$", re.M)
REFRESH_PREFIX = "ops: roadmap status refresh "


class RunnerError(RuntimeError):
    """A git call the subject depends on failed. Never swallowed."""


class ReplayError(RunnerError):
    """Main's history cannot supply the replay's fixed arc count."""


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RunnerError(f"git {' '.join(args)} failed in {repo}: {proc.stderr.strip()}")
    return proc.stdout


def _paths(*outputs: str) -> tuple[str, ...]:
    """Paths from NUL-delimited git output (`-z`): without it git quotes and escapes any name with
    non-ASCII characters, tabs or quotes, and the escaped text is no longer the file's name."""
    return tuple(sorted({path for out in outputs for path in out.split("\0") if path}))


def gh_pr_body(repo: Path, ref: str | None) -> str | None:
    """The PR body for `ref` (None: the current branch's PR), or None when gh cannot produce
    one -- no PR, no auth, no network, no binary. The unrun_cli check reports that absence."""
    argv = [
        "gh",
        "pr",
        "view",
        *([ref] if ref is not None else []),
        "--json",
        "body",
        "--jq",
        ".body",
    ]
    try:
        # one `gh pr view` API round trip; a stalled network is the absence case, not a hang
        proc = subprocess.run(argv, cwd=repo, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return proc.stdout if proc.returncode == 0 else None


def working_tree_subject(repo: Path, *, base: str, pr_body: PrBody = gh_pr_body) -> core.Subject:
    """The change as a pre-commit / pre-review / pre-PR boundary sees it: the working tree
    against `base` (committed + staged + unstaged) plus untracked files that are not ignored."""
    untracked = _git(repo, "ls-files", "--others", "--exclude-standard", "-z")
    return core.Subject(
        repo,
        _paths(_git(repo, "diff", "--name-only", "-z", base), untracked),
        _paths(_git(repo, "ls-files", "--cached", "--others", "--exclude-standard", "-z")),
        _git(repo, "diff", "--unified=0", base),
        _git(repo, "log", "--format=%B", f"{base}..HEAD"),
        pr_body(repo, None),
    )


def arc_pr_body(repo: Path, sha: str, pr_body: PrBody = gh_pr_body) -> str | None:
    """The body of the PR a squash commit's `(#N)` names -- never the current branch's -- or None
    when the subject names none or gh cannot produce it."""
    number = SQUASH_SUBJECT.search(_git(repo, "log", "-1", "--format=%B", sha))
    return pr_body(repo, number.group(1)) if number is not None else None


def _body_key(body: str | None) -> str:
    return "nobody" if body is None else hashlib.sha256(body.encode()).hexdigest()[:16]


@contextmanager
def commit_subject(repo: Path, sha: str, *, body: str | None) -> Iterator[core.Subject]:
    """A merged arc as its squash commit left the tree: a detached worktree of `sha` -- a real
    checkout, so a mutation probe there can verify its restore against the index -- removed on
    exit. The change is the commit against its first parent; `body` is the arc's PR body as the
    replay fetched it (`arc_pr_body`)."""
    message = _git(repo, "log", "-1", "--format=%B", sha)
    changed = _paths(_git(repo, "diff", "--name-only", "-z", f"{sha}^", sha))
    universe = _paths(_git(repo, "ls-tree", "-r", "--name-only", "-z", sha))
    diff = _git(repo, "diff", "--unified=0", f"{sha}^", sha)
    with tempfile.TemporaryDirectory(prefix="mech-replay-") as tmp:
        tree = Path(tmp) / "tree"
        _git(repo, "worktree", "add", "--detach", str(tree), sha)
        try:
            yield core.Subject(tree, changed, universe, diff, message, body)
        finally:
            _git(repo, "worktree", "remove", "--force", str(tree))


def select_replay_commits(log_lines: Sequence[str], n: int) -> list[str]:
    """The last `n` merged arcs of main's first-parent history (`<sha>\\t<subject>` lines,
    newest first): a squash merge's subject ends in `(#NNN)`; a terminating roadmap refresh
    (CLAUDE.md §12.2.1) is bookkeeping, not an arc."""
    shas = [
        sha
        for sha, _tab, subject in (line.partition("\t") for line in log_lines)
        if SQUASH_SUBJECT.search(subject) and not subject.startswith(REFRESH_PREFIX)
    ]
    if len(shas) < n:
        raise ReplayError(
            f"only {len(shas)} merged arcs on the first-parent history; replay needs {n}"
        )
    return shas[:n]


def run_checks(
    subject: core.Subject,
    checks: Sequence[core.Check],
    state: dict[str, core.CheckState],
    *,
    arc_id: str,
    lane_id: str,
    head_sha: str | None,
) -> int:
    blocking = 0
    for check in checks:
        findings = check.run(subject)
        core.emit(
            check.check_id,
            check.kind,
            findings,
            arc_id=arc_id,
            lane_id=lane_id,
            head_sha=head_sha,
            lineage="fresh",
        )
        mode = "blocking" if isinstance(state[check.check_id], core.Blocking) else "advisory"
        print(f"{check.check_id} [{check.kind}, {mode}]: {len(findings)} finding(s)")
        for f in findings:
            print(f"  {f.severity:<4} {f.location} -- {f.evidence} (expected: {f.expected})")
        blocking += (mode == "blocking") * sum(f.severity != "info" for f in findings)
    return int(blocking > 0)


def implementation_digest() -> str:
    """The tools tree the runner imports from -- the check modules AND everything they delegate
    to (lanes_verify, pin_scope, finding_record, ...). Replay evidence and its adjudications
    belong to the implementation that produced them, so any change there re-measures every arc.
    Named bound: third-party libraries (jsonschema) are outside the digest."""
    h = hashlib.sha256()
    for path in sorted((core.REPO / "tools").rglob("*.py")):
        h.update(path.relative_to(core.REPO).as_posix().encode() + b"\0" + path.read_bytes())
    return h.hexdigest()[:16]


def replay(
    repo: Path,
    check: core.Check,
    *,
    lane_id: str,
    ref: str = "origin/main",
    pr_body: PrBody = gh_pr_body,
) -> core.ReplayVerdict:
    if not check.replayable:
        raise ReplayError(
            f"{check.check_id} executes subject tests; replaying it would run historical code in "
            "this environment -- its promotion waits on an isolated venue (B-241)"
        )
    log = _git(repo, "log", "--first-parent", "--format=%H%x09%s", ref).splitlines()
    shas = select_replay_commits(log, core.WINDOW)
    impl = implementation_digest()
    bodies = [arc_pr_body(repo, sha, pr_body) for sha in shas]
    # beyond its commit, an arc id binds the tools tree and the PR body as fetched now -- a body
    # edited since, or one gh could not fetch last time, re-measures the arc instead of reusing a
    # result read from other input. Named bound: third-party versions (ruff) stay outside the
    # key, as implementation_digest states.
    arc_ids = [
        f"replay-{sha[:12]}-{impl}-{_body_key(body)}"
        for sha, body in zip(shas, bodies, strict=True)
    ]
    measured = {
        r["arc_id"]
        for r in fr.read_rows()
        if r.get("producer") == check.check_id and r["record_kind"] in core.OBSERVATION_KINDS
    }
    # an arc already replayed keeps its rows and whatever adjudications they have gathered
    todo = [
        (sha, body, arc_id)
        for sha, body, arc_id in zip(shas, bodies, arc_ids, strict=True)
        if arc_id not in measured
    ]
    for sha, body, arc_id in todo:
        with commit_subject(repo, sha, body=body) as subject:
            findings = check.run(subject)
        core.emit(
            check.check_id,
            check.kind,
            findings,
            arc_id=arc_id,
            lane_id=lane_id,
            head_sha=sha,
            lineage="replay",
        )
    return core.replay_verdict(fr.read_rows(), check.check_id, arc_ids)


def report_replay(check_id: str, verdict: core.ReplayVerdict) -> int:
    match verdict:
        case core.Unmeasured(arcs):
            print(
                f"{check_id}: replay incomplete -- {len(arcs)} arc(s) unmeasured: {', '.join(arcs)}"
            )
            return 1
        case core.Pending(findings):
            print(
                f"{check_id}: {findings} replay finding(s) await a finding_adjudication row; "
                "promotion not evaluated"
            )
            return 1
        case core.Measured(rejected):
            promoted = core.evaluate_promotion(check_id, rejected)
            outcome = "PROMOTED to blocking" if promoted else "stays advisory"
            print(
                f"{check_id}: {sum(rejected)} of {len(rejected)} replayed arcs carry a rejected "
                f"finding -> {outcome}"
            )
            return 0 if promoted else 1


def _blocking_windows(state: dict[str, core.CheckState]) -> dict[str, tuple[str, list[int]]]:
    """Each blocking check's promotion stamp and the windows computed for that promotion."""
    rows = fr.read_rows()
    return {
        check_id: (s.promoted_at, core.rejected_windows(rows, check_id, since=s.promoted_at))
        for check_id, s in state.items()
        if isinstance(s, core.Blocking)
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mechanized_checks.runner")
    verbs = parser.add_subparsers(dest="verb", required=True)
    verbs.add_parser("check").add_argument("--base", default="origin/main")
    verbs.add_parser("replay").add_argument("check_id", choices=[c.check_id for c in CHECKS])
    verbs.add_parser("demote")
    verbs.add_parser("demotion-due")
    args = parser.parse_args(argv)
    repo = core.REPO
    state = core.load_state()
    arc_id, lane_id = rwc.env_arc_and_lane()
    match args.verb:
        case "check":
            head = _git(repo, "rev-parse", "HEAD").strip()
            subject = working_tree_subject(repo, base=args.base)
            return run_checks(subject, CHECKS, state, arc_id=arc_id, lane_id=lane_id, head_sha=head)
        case "replay":
            check = next(c for c in CHECKS if c.check_id == args.check_id)
            return report_replay(check.check_id, replay(repo, check, lane_id=lane_id))
        case "demote":
            for check_id, (promoted_at, windows) in _blocking_windows(state).items():
                demoted = core.evaluate_demotion(check_id, windows, promoted_at=promoted_at)
                print(
                    f"{check_id}: windows {windows} -> {'DEMOTED' if demoted else 'stays blocking'}"
                )
            return 0
        case _:
            due = {
                c: w
                for c, (_promoted_at, w) in _blocking_windows(state).items()
                if core.demotion_due(state[c], w)
            }
            for check_id, windows in due.items():
                print(f"DEMOTION DUE {check_id}: windows {windows} (run `just lanes-verify`)")
            return int(bool(due))


if __name__ == "__main__":
    raise SystemExit(main())
