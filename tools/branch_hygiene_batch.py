"""Batched branch hygiene — one guarded push for every deferred deletion (B-230 Task 4).

Every landed arc defers the deletion of its two merged remote branches (the topic branch
and the door's `roadmap-refresh-post-<N>` branch) to an interactive session, because the
permission guard denies `git push --force-with-lease` unconditionally in loop mode. Each
deferral used to cost one approval prompt per branch. This tool reads the pending-HIL
reducer, verifies every branch against its PR, and prints ONE `--atomic` force-with-lease
push for the operator to paste — then, in a second rerunnable phase, appends the
`RESOLVED-HIL` row for every item whose branches are gone on origin, which is what makes
the reducer stop presenting them.

Two phases, each rerunnable:

  --emit-command  parse → verify every branch against `gh pr view` → print the push.
                  One mismatch aborts the whole batch with nothing on stdout: a partially
                  stale queue must never become a partially executed destructive push.
  --resolve       parse → probe origin (`git ls-remote --exit-code`, exit 2 is the one
                  "genuinely absent" signal) → `loop_resolve` each item whose branches are
                  ALL absent; report `still present:` for the rest. Never re-issues a push.

Input is the pending-HIL reducer (`loop_pending_hil_list`, last-write-wins per item id)
over the canonical shared ledger — never the raw ledger or a hard-coded path. Rows are
data, not program text: item ids are validated at parse time, every generated argument in
the printed push passes through `shlex.quote`, and `loop_resolve` receives the item and
note as `$1 $2` argv — no shell interpolation of ledger tokens anywhere.

Exit codes: 0 done · 1 verification mismatch / items still present / nothing to do ·
2 an unreadable branch-hygiene row. stdout carries only the pasteable push command;
everything human-facing goes to stderr.
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arc_metrics import ci_is_green  # sibling tool; the ONE C-HE-19 predicate

ROOT = Path(__file__).resolve().parents[1]

# [LAW:one-source-of-truth] the producer (both ship-pr carriers) and this parser share ONE
# row shape; the carrier-parity test imports these constants rather than restating them.
MARKER = "branch hygiene close-out pending: "
CANONICAL_DEFER_SHAPE = (
    "branch hygiene close-out pending: <branch> (PR #<N>, merged <merge-sha>, main run green) "
    "and roadmap-refresh-post-<N> (PR #<refresh-N>, merged <refresh-merge-sha>, main run green)"
)

_ROW = re.compile(r"^\[(?P<lane>[^\]]*)\] (?P<item>\S+) — (?P<detail>.*)$")
_ITEM_ID = re.compile(r"^[A-Za-z0-9._-]+$")
# One pair is `<branch> (PR #N, merged <sha>[, …])`; the text after the sha inside the
# parenthesis is free (older rows carry no "main run green", some carry a run id). The
# pair list must be consumed WHOLE — `A (…) and B (…)`, optionally followed by ` — <note>`
# — so a truncated or malformed second pair is an unreadable row, never a one-branch item
# whose refresh branch would be hidden forever once the first is resolved (codex r1 P2).
_PAIR = r"(\S+) \(PR #(\d+), merged [0-9a-f]{7,40}[^()]*\)"
_PAIRS = re.compile(rf"^(?P<pairs>{_PAIR}(?: and {_PAIR})*)(?: — .*)?$")
_ONE_PAIR = re.compile(_PAIR)


class UnreadableRow(Exception):  # noqa: N818 — B-230 Task 4 plan signature verbatim
    """A branch-hygiene row this tool claims but cannot read. Refused loudly, never skipped."""


class VerificationMismatch(Exception):  # noqa: N818 — B-230 Task 4 plan signature verbatim
    """A branch whose PR is not MERGED, or whose head branch is not the one recorded."""


class RemoteStateError(Exception):
    """`git ls-remote` failed for a reason other than "no such ref" (network, auth, ...)."""


class ResolveError(Exception):
    """`loop_resolve` did not land its RESOLVED-HIL row."""


@dataclass
class Deferral:
    item_id: str
    branches: list[tuple[str, str]]  # (branch, pr number as the row spells it)


@dataclass(frozen=True)
class ForeignRow:
    """A pending deferral that is not a branch-hygiene one — another gate's, left alone."""

    row: str


def parse_rows(text: str) -> list[Deferral | ForeignRow]:
    # [LAW:parse-dont-validate] the reducer's lines cross this one boundary and come out
    # typed: a Deferral this tool owns, or a ForeignRow it reports and leaves pending.
    out: list[Deferral | ForeignRow] = []
    for row in (ln for ln in text.splitlines() if ln.strip()):
        m = _ROW.match(row)
        if m is None:
            raise UnreadableRow(row)
        detail = m.group("detail")
        if not detail.startswith(MARKER):
            out.append(ForeignRow(row))
            continue
        item = m.group("item")
        pm = _PAIRS.match(detail.removeprefix(MARKER))
        if not _ITEM_ID.match(item) or pm is None:
            raise UnreadableRow(row)
        pairs = _ONE_PAIR.findall(pm.group("pairs"))
        out.append(Deferral(item, [(branch, pr) for branch, pr in pairs]))
    return out


def parse_pending(text: str) -> list[Deferral]:
    return [r for r in parse_rows(text) if isinstance(r, Deferral)]


# ── effectful edges (each replaced by the tests) ────────────────────────────
# [LAW:effects-at-boundaries] the three calls that touch GitHub, origin and the ledger
# live here; verify_all / build_push_command / resolve_cleared only combine their results.


def _gh(*args: str) -> str:
    proc = subprocess.run(["gh", *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise VerificationMismatch(
            f"gh {args[0]} {args[1]} failed (exit {proc.returncode}): {proc.stderr.strip()}"
        )
    return proc.stdout


def pr_view(pr: str) -> dict[str, Any]:
    return json.loads(
        _gh("pr", "view", pr, "--json", "state,baseRefName,headRefName,headRefOid,mergeCommit")
    )


def default_branch() -> str:
    return _gh(
        "repo", "view", "--json", "defaultBranchRef", "--jq", ".defaultBranchRef.name"
    ).strip()


def main_run_conclusion(merge_sha: str) -> str:
    """The merge commit's OWN post-merge run on main — the PR's pre-merge checks are not
    a substitute (the ship-pr close-out block, and C-HE-19 via `arc_metrics.ci_is_green`)."""
    return _gh(
        "run",
        "list",
        "--commit",
        merge_sha,
        "--json",
        "conclusion",
        "--jq",
        ".[0].conclusion // empty",
    ).strip()


def remote_absent(branch: str) -> bool:
    proc = subprocess.run(
        ["git", "ls-remote", "--exit-code", "--heads", "origin", f"refs/heads/{branch}"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    if proc.returncode == 0:
        return False
    if proc.returncode == 2:
        return True
    raise RemoteStateError(f"ls-remote exit {proc.returncode} for {branch}: {proc.stderr.strip()}")


def loop_resolve(item_id: str, note: str) -> None:
    # The item and note travel as argv ($1 $2), never interpolated into the script text.
    proc = subprocess.run(
        [
            "bash",
            "-c",
            'source tools/hooks/lib.sh && source tools/hooks/loop_lib.sh && loop_resolve "$1" "$2"',
            "branch_hygiene_batch",
            item_id,
            note,
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    if proc.returncode != 0:
        raise ResolveError(f"loop_resolve {item_id} exit {proc.returncode}: {proc.stderr.strip()}")


# ── pure combinators ─────────────────────────────────────────────────────────


def verify_all(deferrals: list[Deferral]) -> dict[str, str]:
    """The same four facts the ship-pr close-out block requires before ONE delete, for
    every branch in the batch: the PR is MERGED, into the default branch, its head branch
    is the one the row names, and the merge commit's own main run is green (codex r1 P1
    on b-230-task-4: a deferral is data — a PR merged into a side branch must not become
    a force-delete)."""
    base = default_branch()
    oids: dict[str, str] = {}
    for d in deferrals:
        for branch, pr in d.branches:
            info = pr_view(pr)
            concl = main_run_conclusion(info["mergeCommit"]["oid"]) if info["mergeCommit"] else ""
            reason = (
                f"state is {info['state']}"
                if info["state"] != "MERGED"
                else f"merged into {info['baseRefName']}, not {base}"
                if info["baseRefName"] != base
                else f"head branch is {info['headRefName']}"
                if info["headRefName"] != branch
                else f"post-merge CI on {base} is {concl or 'empty'}, not success"
                if not ci_is_green(concl)
                else None
            )
            if reason is not None:
                raise VerificationMismatch(f"verification mismatch: {branch} PR #{pr}: {reason}")
            oids[branch] = info["headRefOid"]
    return oids


def partition_present(oids: dict[str, str]) -> dict[str, str]:
    """The verified branches still on origin — the only ones a lease can be taken on.

    `gh pr view` reports a head OID for a merged PR whose branch was ALREADY deleted (an
    earlier interactive session ran the guarded block but never resolved the row), and a
    `--force-with-lease=<ref>:<oid>` on an absent ref is rejected as stale — under
    `--atomic` that rejects the whole push. Witnessed on the first live batch: 8 of 16
    branches were gone. Those items are phase 2's; they never enter the push.
    """
    return {b: oid for b, oid in oids.items() if not remote_absent(b)}


def build_push_command(branches: list[tuple[str, str]]) -> str:
    if not branches:
        raise ValueError("no branches to delete")
    # Branch names are git refs and may carry shell metacharacters; the operator pastes
    # this line, so every generated argument is quoted.
    leases = [shlex.quote(f"--force-with-lease=refs/heads/{b}:{oid}") for b, oid in branches]
    refspecs = [shlex.quote(f":refs/heads/{b}") for b, _ in branches]
    return " ".join(["git", "push", "--atomic", *leases, "origin", *refspecs])


def resolve_cleared(deferrals: list[Deferral]) -> list[Deferral]:
    """Resolve every item whose branches are ALL absent on origin; return the rest."""
    still_pending: list[Deferral] = []
    for d in deferrals:
        # [LAW:dataflow-not-control-flow] every branch is probed; the list decides.
        absent = [remote_absent(b) for b, _ in d.branches]
        if all(absent):
            names = ", ".join(b for b, _ in d.branches)
            loop_resolve(
                d.item_id, f"branch hygiene batch: {names} absent on origin (ls-remote exit 2)"
            )
        else:
            still_pending.append(d)
    return still_pending


# ── CLI ──────────────────────────────────────────────────────────────────────


def _read_pending(spec: str) -> str:
    return sys.stdin.read() if spec == "-" else Path(spec).read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--pending", required=True, metavar="PATH|-", help="pending-HIL reducer output (- = stdin)"
    )
    phase = ap.add_mutually_exclusive_group(required=True)
    phase.add_argument(
        "--emit-command", action="store_true", help="phase 1: verify and print the push"
    )
    phase.add_argument(
        "--resolve", action="store_true", help="phase 2: resolve items whose branches are gone"
    )
    args = ap.parse_args(argv)

    try:
        rows = parse_rows(_read_pending(args.pending))
    except UnreadableRow as e:
        print(f"unreadable pending row: {e}", file=sys.stderr)
        return 2
    for r in rows:
        if isinstance(r, ForeignRow):
            print(f"left pending (not a branch-hygiene deferral): {r.row}", file=sys.stderr)
    deferrals = [r for r in rows if isinstance(r, Deferral)]
    if not deferrals:
        print("nothing to do: no branch-hygiene deferrals pending", file=sys.stderr)
        return 1

    if args.emit_command:
        try:
            oids = verify_all(deferrals)
            present = partition_present(oids)
        except (VerificationMismatch, RemoteStateError) as e:
            print(str(e), file=sys.stderr)
            return 1
        for branch in oids.keys() - present.keys():
            print(
                f"already absent on origin (branch-hygiene-resolve clears it): {branch}",
                file=sys.stderr,
            )
        if not present:
            print(
                "nothing to push: every verified branch is already absent on origin",
                file=sys.stderr,
            )
            return 1
        for branch, oid in present.items():
            print(f"{branch} {oid}", file=sys.stderr)
        print(build_push_command(list(present.items())))
        return 0

    try:
        left = resolve_cleared(deferrals)
    except (RemoteStateError, ResolveError) as e:
        print(str(e), file=sys.stderr)
        return 1
    left_ids = {d.item_id for d in left}
    for d in deferrals:
        if d.item_id not in left_ids:
            print(f"resolved: {d.item_id}", file=sys.stderr)
    for d in left:
        print(f"still present: {d.item_id} {' '.join(b for b, _ in d.branches)}", file=sys.stderr)
    return 1 if left else 0


if __name__ == "__main__":
    sys.exit(main())
