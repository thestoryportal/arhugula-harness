#!/usr/bin/env python3
"""Arc EXIT REPORT — the machine-readable closure record for one merged arc (U-WT-03).

Emitted at the FINAL `ship-pr` step, AFTER the reflect / `/context-save` block (U-WT-04).
That placement is load-bearing: the merge SHA, the post-merge main-CI conclusion, the
terminating-refresh commit AND the just-written checkpoint all exist only at that point,
so `checkpoint{path,confirmed}` records the arc's REAL final checkpoint instead of a
stale or fabricated one. (Stop hooks were rejected — they cannot distinguish an arc close
from a turn end; `post-merge-refresh.sh` was rejected — it fires before the refresh commit
and the post-merge CI conclusion exist. Plan: `.harness/r-if-116-insights-residue-plan.md`
Feature 3, codex round 11.)

Output: `.harness/.checkpoints/arc-exit-report-pr<NNN>.md` — PR-keyed and DATE-FREE, so a
closeout resumed on a later date overwrites the same file instead of orphaning a stale
sibling. The directory is gitignored (`.gitignore:106`): this is a local operator artifact
with zero CI/ledger surface. One `EXIT-REPORT` row is also appended to
`.harness/loop_status.md` as the index, through `loop_lib.sh`'s own `loop_log` (a bash
shim — NOT a second copy of the row format).

Both land under the MAIN checkout, not the (disposable) arc worktree a Codex-flow run is
normally invoked from — see `resolve_repo_root`. All three consumers (report path, ledger,
pending-HIL read) use that one resolved root.

Design: a PURE `render(data) -> str` plus a thin `collect()` that shells `gh`/`git`. Every
external call is validated (exit code + non-empty + parses) before its output flows
anywhere; a missing/unauthenticated `gh` degrades to explicit nulls plus a note in the
prose tail — it never crashes and never fabricates a value. In particular:

  * `refresh_commit` is bound by POSITION as well as shape: only the merge's IMMEDIATE
    first-parent successor on the default branch may qualify (both ship-pr carriers
    require the refresh to land as the immediate next commit), and it must also match
    CLAUDE.md §12.2.1's shape — subject prefix AND a changed-file set of exactly
    `.harness/roadmap_status.md`. A shape-match anywhere else belongs to a LATER arc and
    is reported as a note, never bound (codex round-4 P1).
  * `main_ci` is the merge commit's own `--branch <default> --event push` run — the
    post-merge verdict both carriers require, not the PR's pre-merge checks and not a
    manual dispatch that happens to share the SHA. Zero matching runs is UNRESOLVED, never
    a verdict. `conclusion` is copied VERBATIM from `gh` — never coerced to "success",
    never normalized. When several qualifying runs share the commit, the reported run is
    the FIRST non-success one (failure / cancelled / null-while-pending); only when every
    run concluded `success` is `success` reported, so a red workflow can never be masked
    by a green sibling.
  * `checkpoint` is BOUND, not guessed. `--checkpoint PATH` names the exact file the
    arc's own `/context-save` just wrote; only a bound checkpoint can ever be
    `confirmed: true`. Without it the newest workspace checkpoint is reported as a
    heuristic with `confirmed: false` and a note, because the roadmap authorizes a
    PARALLEL frontier — another live session can `/context-save` between this arc's save
    and this collection, and checkpoint OWNERSHIP is not discriminable by mtime (codex
    round-3 P1).
  * `checkpoint.confirmed` compares the bound checkpoint's mtime against the arc's
    CLOSING commit: the terminating-refresh commit's committer time when a refresh was
    verified, else the merge commit's. The report is emitted after the §12.2.1 fixed
    point, so a checkpoint written between merge and refresh is NOT the final one and
    must not confirm. Unknown anchor time → false, never assumed.
  * The PR's identity is checked before any of it is written: when `gh` answers, the PR
    must be `MERGED` and — if `--merge-sha` was supplied — must match its
    `mergeCommit.oid`. A mismatch exits 2 rather than attaching another PR's facts to
    this report. `gh` absent/failing degrades to nulls as before (nothing to contradict).

Usage:
    uv run python tools/arc_exit_report.py --pr 1202 [--merge-sha SHA] \
        [--checkpoint PATH] [--repo-root PATH]

Exit codes: 0 success (including degraded-with-nulls), 2 unusable inputs (not a git repo,
unresolvable `--merge-sha`, nonexistent `--checkpoint`, PR not merged / merge-sha
disagreeing with the PR, unwritable output). Re-running for the same PR is idempotent:
same filename, overwritten in place. One ledger row is appended per invocation (the ledger
is append-only by design, so a re-run leaves two index rows pointing at the same report).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

import yaml

# The exact YAML block contract (order preserved on render). `notes` is deliberately NOT
# here — degradation notes belong in the human prose tail, not in the machine block.
YAML_FIELDS = (
    "pr",
    "merge_state",
    "merge_commit",
    "main_ci",
    "refresh_commit",
    "checkpoint",
    "todo_for_human",
)

REPORT_DIR = ".harness/.checkpoints"
LEDGER_REL = ".harness/loop_status.md"
# CLAUDE.md §12.2.1 terminating-refresh discriminators (BOTH required).
REFRESH_PREFIX = "ops: roadmap status refresh "
REFRESH_ONLY_FILE = ".harness/roadmap_status.md"
GSTACK_PROJECTS = Path.home() / ".gstack" / "projects"


# --- external-call layer (the only impure part; monkeypatched wholesale in tests) -------


def run(cmd: list[str], cwd: Path, timeout: int = 20) -> tuple[int, str]:
    """Run `cmd`, return (returncode, stripped stdout). Never raises.

    A missing binary or a timeout is reported as rc=127 / rc=124 with empty stdout so
    every call site can distinguish "tool absent" from "tool said no" — callers MUST
    check rc before using stdout (an empty string interpolated downstream is how phantom
    state gets recorded).
    """
    try:
        p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout.strip()
    except FileNotFoundError:
        return 127, ""
    except subprocess.TimeoutExpired:
        return 124, ""
    except OSError:
        return 126, ""


# --- collect ---------------------------------------------------------------------------


def _as_dict(v: object) -> dict[str, Any]:
    """Narrow a decoded-JSON value to a mapping, or {} — nothing downstream may assume
    a shape `gh` did not actually return."""
    return cast("dict[str, Any]", v) if isinstance(v, dict) else {}


def _as_dicts(v: object) -> list[dict[str, Any]]:
    """Narrow a decoded-JSON value to a list of mappings, dropping any non-mapping entry."""
    if not isinstance(v, list):
        return []
    return [cast("dict[str, Any]", x) for x in cast("list[object]", v) if isinstance(x, dict)]


def _gh_json(args: list[str], cwd: Path, notes: list[str], what: str) -> object:
    """`gh <args>` → parsed JSON, or None with a recorded note. Validates rc, non-empty
    output, and that it actually parses — in that order. Returns `object`, not `Any`:
    callers MUST narrow (`_as_dict` / `_as_dicts`) rather than index blindly."""
    rc, out = run(["gh", *args], cwd)
    if rc == 127:
        notes.append(f"`gh` is not installed — {what} unresolved.")
        return None
    if rc != 0:
        notes.append(
            f"`gh {' '.join(args[:2])}` exited {rc} — {what} unresolved (offline/unauthenticated?)."
        )
        return None
    if not out:
        notes.append(f"`gh {' '.join(args[:2])}` returned no output — {what} unresolved.")
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        notes.append(f"`gh {' '.join(args[:2])}` output did not parse as JSON — {what} unresolved.")
        return None


def resolve_repo_root(start: Path, redirect: bool = True) -> tuple[Path | None, list[str]]:
    """The STABLE root to write into, plus any notes about how it was resolved.

    Returns `(None, notes)` when `start` is not inside a git repository at all.

    The Codex flow's normal shape is an isolated arc worktree (`AGENTS.md`), which is
    DISPOSABLE — `git rev-parse --show-toplevel` there points at a directory that the
    worktree-disposition step deletes. Writing the report + ledger index into it means the
    artifacts vanish, and a later controller rerun writes a DIFFERENT file instead of
    overwriting the PR-keyed one, defeating idempotency (codex round-6 P1).

    So the root is redirected to the MAIN checkout: a linked worktree's
    `--git-common-dir` lives inside the main checkout's `.git`, so its parent is that
    checkout. The redirect is only taken when the resolved root actually looks like this
    workspace (`.harness/` present) — otherwise the worktree toplevel is kept and a note
    says the location may be worktree-local. `redirect=False` (an explicit `--repo-root`)
    always wins.
    """
    notes: list[str] = []
    rc, top = run(["git", "rev-parse", "--show-toplevel"], start)
    if rc != 0 or not top:
        return None, notes
    toplevel = Path(top)
    if not redirect:
        return toplevel, notes

    # Ask for an ABSOLUTE path: the plain form is CWD-relative (`../../.git` from a
    # subdirectory — grounded live on git 2.39), so resolving it against anything but the
    # exact cwd git ran in is wrong. `--path-format` needs git >= 2.31; fall back to the
    # plain form resolved against that same cwd.
    rc, common = run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], start)
    if rc != 0 or not common:
        rc, common = run(["git", "rev-parse", "--git-common-dir"], start)
    if rc != 0 or not common:
        notes.append(
            "`git rev-parse --git-common-dir` did not resolve — writing to the current "
            f"worktree ({toplevel}); if this is a disposable arc worktree, this report's "
            "location is worktree-local and will not survive worktree disposition."
        )
        return toplevel, notes
    cdir = Path(common)
    if not cdir.is_absolute():
        cdir = start / cdir  # git reports it relative to the cwd we ran it in
    try:
        main_root = cdir.resolve().parent
    except OSError:
        return toplevel, notes
    if main_root == toplevel:
        return toplevel, notes  # already the main checkout — nothing to say
    if (main_root / ".harness").is_dir():
        notes.append(
            f"invoked from a linked worktree ({toplevel}); the report and its ledger row "
            f"were written to the MAIN checkout ({main_root}) so they survive worktree "
            "disposition and a rerun overwrites the same PR-keyed file."
        )
        return main_root, notes
    notes.append(
        f"invoked from a linked worktree ({toplevel}) but the resolved main checkout "
        f"({main_root}) has no .harness/ — writing to the worktree instead; this report's "
        "location may be worktree-local and will not survive worktree disposition."
    )
    return toplevel, notes


def _resolve_commit(sha: str, cwd: Path) -> str:
    """Full 40-char SHA for `sha`, or '' if it does not resolve to a commit in this repo."""
    rc, out = run(["git", "rev-parse", "--verify", "--quiet", f"{sha}^{{commit}}"], cwd)
    return out if rc == 0 and len(out) == 40 else ""


def _default_branch(cwd: Path) -> str:
    """The default branch NAME (not a ref) — `origin/HEAD`'s target when known, else `main`."""
    rc, out = run(["git", "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"], cwd)
    if rc == 0 and "/" in out:
        return out.split("/", 1)[1]
    return "main"


def _main_ci(commit: str, cwd: Path, notes: list[str]) -> dict[str, Any]:
    """The POST-MERGE CI verdict for `commit`. Conclusion copied verbatim; worst-first
    selection across the commit's runs (see module docstring).

    Scoped to `--branch <default> --event push` — the exact run both ship-pr carriers
    require ("the merge commit's own main CI run", not the PR's pre-merge checks). Querying
    by `--commit` alone mixes in manually-dispatched / non-main runs on the same SHA, so an
    unrelated `workflow_dispatch` success could fake green when the real push run is absent,
    and an unrelated failure could fake red (codex round-4 P2). Zero matching runs is
    UNRESOLVED (null + note), never a verdict.
    """
    blank: dict[str, Any] = {"commit": commit or None, "conclusion": None, "run_url": None}
    if not commit:
        return blank
    branch = _default_branch(cwd)
    raw = _gh_json(
        [
            "run",
            "list",
            "--commit",
            commit,
            "--branch",
            branch,
            "--event",
            "push",
            "--limit",
            "20",
            "--json",
            "conclusion,status,url,workflowName",
        ],
        cwd,
        notes,
        "main_ci",
    )
    if raw is None:
        return blank
    runs = _as_dicts(raw)
    if not runs:
        notes.append(
            f"No push-event workflow run on {branch} for merge commit {commit[:8]} — main_ci "
            "unresolved (a dispatch-only or PR-only run is not the post-merge verdict)."
        )
        return blank
    bad = [r for r in runs if r.get("conclusion") != "success"]
    chosen = bad[0] if bad else runs[0]
    if bad:
        notes.append(
            f"main CI is NOT confirmed green: {len(bad)} of {len(runs)} run(s) on {commit[:8]} "
            f"did not conclude success (reporting "
            f"'{chosen.get('workflowName') or 'unknown workflow'}')."
        )
    return {
        "commit": commit,
        "conclusion": chosen.get("conclusion"),  # VERBATIM — null while pending, never coerced
        "run_url": chosen.get("url"),
    }


def _default_ref(cwd: Path) -> str:
    """The ref to scan for the terminating refresh — the remote default branch when it is
    known locally, else the local default branch, else HEAD (each probed, never assumed)."""
    rc, out = run(["git", "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"], cwd)
    for candidate in ([out] if rc == 0 and out else []) + ["origin/main", "main", "HEAD"]:
        if _resolve_commit(candidate, cwd):
            return candidate
    return "HEAD"


def _refresh_shape_ok(sha: str, cwd: Path) -> bool | None:
    """Does `sha` change exactly `.harness/roadmap_status.md`? None = could not verify."""
    rc, files = run(["git", "show", "--name-only", "--format=", sha], cwd)
    if rc != 0:
        return None
    return [f for f in files.splitlines() if f.strip()] == [REFRESH_ONLY_FILE]


def _refresh_commit(merge_commit: str, cwd: Path, notes: list[str]) -> str | None:
    """THIS merge's §12.2.1 terminating-refresh commit, or None.

    Bound by POSITION, not merely by shape (codex round-4 P1). Both ship-pr carriers
    require the refresh to land as the **immediate next commit**, so only the merge's
    IMMEDIATE first-parent successor on the default branch is a candidate — and it must
    additionally match the shape (reserved subject prefix AND a changed-file set of exactly
    `.harness/roadmap_status.md`).

    Scanning the whole history for the first shape-match was the defect: when THIS arc's
    refresh is missing but a LATER arc lands its own one-file refresh, a shape-only scan
    binds the other arc's commit — which then also mis-anchors `checkpoint.confirmed`
    (`_checkpoint` anchors on the refresh). A shape-match anywhere else now yields None
    plus a note naming what was found, so a missing refresh reads as missing.
    """
    if not merge_commit:
        return None
    ref = _default_ref(cwd)
    rc, out = run(
        [
            "git",
            "log",
            "--first-parent",
            "--reverse",
            "--format=%H%x09%P%x09%s",
            f"{merge_commit}..{ref}",
        ],
        cwd,
    )
    if rc != 0:
        notes.append(
            f"`git log {merge_commit[:8]}..{ref}` exited {rc} — refresh_commit unresolved."
        )
        return None
    entries = [ln.split("\t", 2) for ln in out.splitlines() if ln.count("\t") >= 2]
    if not entries:
        notes.append(
            f"No commits after the merge on {ref} — the merge is the tip; no refresh has "
            "landed yet."
        )
        return None

    sha, parents, subject = entries[0]
    first_parent = parents.split(" ")[0] if parents else ""
    if first_parent != merge_commit:
        notes.append(
            f"{sha[:8]} is the oldest commit after the merge on {ref} but its first parent is "
            f"{first_parent[:8] or 'none'}, not the merge — the merge is not on this branch's "
            "first-parent chain; refresh not bound."
        )
        return None

    if subject.startswith(REFRESH_PREFIX):
        ok = _refresh_shape_ok(sha, cwd)
        if ok is None:
            notes.append(
                f"`git show --name-only {sha[:8]}` failed — the immediate successor's shape "
                "could not be verified; refresh_commit is null."
            )
            return None
        if ok:
            return sha
        notes.append(
            f"{sha[:8]} is the immediate successor and carries the refresh title, but is not "
            "roadmap-status-only — not a §12.2.1 terminating refresh."
        )
    else:
        notes.append(
            f"the merge's immediate successor {sha[:8]} is not a refresh commit — this arc's "
            "terminating refresh is missing or has not landed yet."
        )

    # A shape-match further down the history belongs to a LATER arc. Name it rather than
    # silently reporting null, so the reader can tell "missing" from "not looked for".
    for later_sha, _p, later_subject in entries[1:]:
        if later_subject.startswith(REFRESH_PREFIX) and _refresh_shape_ok(later_sha, cwd):
            notes.append(
                f"a later refresh-shaped commit exists ({later_sha[:8]}) but is not this "
                "merge's immediate successor — not this arc's refresh."
            )
            break
    return None


def _newest_checkpoint(repo_root: Path, cwd: Path, gstack_root: Path | None) -> Path | None:
    """The workspace-newest gstack checkpoint across both slug spellings this workspace has
    produced (`<repo-dir-name>` and `<owner>-<repo>`). A HEURISTIC — see `_checkpoint`."""
    root = gstack_root if gstack_root is not None else GSTACK_PROJECTS
    slugs = [repo_root.name]
    rc, url = run(["git", "remote", "get-url", "origin"], cwd)
    if rc == 0 and url:
        parts = url.rstrip("/").removesuffix(".git").replace(":", "/").split("/")
        if len(parts) >= 2:
            slugs.append(f"{parts[-2]}-{parts[-1]}")
    newest: Path | None = None
    for slug in dict.fromkeys(slugs):
        d = root / slug / "checkpoints"
        if not d.is_dir():
            continue
        for f in d.glob("*.md"):
            if not f.is_file():
                continue
            if newest is None or f.stat().st_mtime > newest.stat().st_mtime:
                newest = f
    return newest


def _commit_ts(commit: str, cwd: Path) -> int | None:
    """A commit's committer time as an epoch int, or None if it cannot be read."""
    if not commit:
        return None
    rc, ts = run(["git", "show", "-s", "--format=%ct", commit], cwd)
    return int(ts) if rc == 0 and ts.isdigit() else None


def _checkpoint(
    anchor_commit: str,
    anchor_kind: str,
    repo_root: Path,
    cwd: Path,
    gstack_root: Path | None,
    explicit: Path | None,
    notes: list[str],
) -> dict[str, Any]:
    """The arc's final checkpoint, and whether it post-dates the arc's CLOSING commit.

    Two modes, deliberately asymmetric (codex round-3 P1):

    * `explicit` (from `--checkpoint`) is a BINDING: the caller names the file its own
      `/context-save` step just reported, so ownership is known and `confirmed` is a real
      claim — mtime strictly after `anchor_commit`'s committer time.
    * Without it, the workspace-newest checkpoint is a HEURISTIC and `confirmed` is
      UNCONDITIONALLY false with a note. The roadmap authorizes a parallel frontier, so
      another live session's `/context-save` can be the newest file here; mtime cannot
      discriminate ownership, and a heuristic guess must never be dressed as confirmation.

    `anchor_kind` names which commit the anchor is (`refresh` / `merge`) for the note text;
    the caller picks the refresh commit when one was verified, since this report is emitted
    only after the §12.2.1 fixed point (a checkpoint written between merge and refresh is
    not the arc's final one).
    """
    if explicit is None:
        newest = _newest_checkpoint(repo_root, cwd, gstack_root)
        if newest is None:
            return {"path": None, "confirmed": False}
        notes.append(
            "checkpoint selected heuristically (workspace-newest) — pass --checkpoint to "
            "bind to this arc; not confirmed"
        )
        return {"path": str(newest), "confirmed": False}

    try:
        mtime = explicit.stat().st_mtime
    except OSError as e:
        notes.append(f"bound checkpoint {explicit} could not be read ({e}) — not confirmed.")
        return {"path": str(explicit), "confirmed": False}
    anchor_ts = _commit_ts(anchor_commit, cwd)
    if anchor_ts is None:
        notes.append(
            "checkpoint confirmation unavailable — the arc's closing commit time could not "
            "be read; not confirmed."
        )
        return {"path": str(explicit), "confirmed": False}
    if mtime <= anchor_ts:
        notes.append(
            f"bound checkpoint predates the {anchor_kind} commit {anchor_commit[:8]} — it is "
            "not this arc's FINAL checkpoint; not confirmed."
        )
        return {"path": str(explicit), "confirmed": False}
    return {"path": str(explicit), "confirmed": True}


def _todos(repo_root: Path, notes: list[str]) -> list[str] | None:
    """Still-pending DEFERRED-HIL rows via `loop_pending_hil_list`, or None when UNKNOWN.

    Shells the real `loop_lib.sh` helper rather than re-parsing the ledger here — the
    ledger parse has exactly one implementation (`_loop_pending_hil_rows`), shared with
    the bounded `loop_pending_hil_summary` the SessionStart hook surfaces.

    Collection failure (helper missing or nonzero) returns None → rendered as
    `todo_for_human: null` + a prose note. An UNKNOWN list must never be rendered as
    an authoritative empty [] (codex round-2): "nothing is waiting" and "could not
    look" are different claims.
    """
    lib = repo_root / "tools" / "hooks" / "lib.sh"
    loop_lib = repo_root / "tools" / "hooks" / "loop_lib.sh"
    if not (lib.is_file() and loop_lib.is_file()):
        notes.append("tools/hooks/loop_lib.sh not found — todo_for_human is UNKNOWN (null).")
        return None
    # The bash source is a CONSTANT; every path travels as an argv value read through "$N"
    # (codex round-6 P2). Interpolating the paths into the source made a metacharacter-
    # bearing repo path — `…/re"po; touch /tmp/x; #` — execute as code.
    rc, out = run(
        [
            "bash",
            "-c",
            'CLAUDE_PROJECT_DIR="$1"; . "$2"; . "$3"; loop_pending_hil_list',
            "arc_exit_report",  # $0
            str(repo_root),
            str(lib),
            str(loop_lib),
        ],
        repo_root,
    )
    if rc != 0:
        notes.append(f"`loop_pending_hil_list` exited {rc} — todo_for_human is UNKNOWN (null).")
        return None
    return [line.strip() for line in out.splitlines() if line.strip()]


def identity_error(pr: int, merge_state: str | None, pr_oid: str, resolved_sha: str) -> str | None:
    """Why this PR's facts must NOT be written, or None. Pure — the effect is the caller's.

    Only fires when `gh` actually answered (`merge_state` non-empty): with no PR data there
    is nothing to contradict and the tool degrades as before. Otherwise the arc must be
    MERGED, and an explicitly supplied merge SHA must be the one the PR merged at — a
    mistyped SHA that happens to resolve to some OTHER commit would otherwise silently
    attach a different arc's CI, refresh and checkpoint facts to this report (codex
    round-3 P2).
    """
    if not merge_state:
        return None
    if merge_state != "MERGED":
        return (
            f"PR #{pr} is {merge_state}, not MERGED — an exit report is an arc-CLOSURE "
            "record; refusing to write one for an unmerged PR."
        )
    if resolved_sha and pr_oid and resolved_sha != pr_oid:
        return (
            f"--merge-sha resolves to {resolved_sha[:8]} but PR #{pr} merged at "
            f"{pr_oid[:8]} — refusing to attach another commit's facts to this report."
        )
    return None


def collect(
    pr: int,
    merge_sha: str | None,
    repo_root: Path,
    gstack_root: Path | None = None,
    checkpoint: Path | None = None,
    seed_notes: list[str] | None = None,
) -> dict[str, Any]:
    """Gather the arc's closure facts. Degrades to nulls + notes; never raises, never fabricates.

    `seed_notes` carries observations made BEFORE collection began (currently the repo-root
    resolution's) so they reach the report's prose tail through the one notes channel.

    One non-degrading outcome exists: `identity_error` (a PR that is not this merged arc).
    It is returned as data under `identity_error`, not acted on here — `main()` turns it
    into exit 2 without writing anything, keeping the effect at the boundary.
    """
    notes: list[str] = list(seed_notes or [])
    pr_view = _as_dict(
        _gh_json(
            ["pr", "view", str(pr), "--json", "state,mergeCommit"], repo_root, notes, "merge_state"
        )
    )
    merge_state: str | None = pr_view.get("state")
    pr_oid: str = _as_dict(pr_view.get("mergeCommit")).get("oid") or ""

    merge_commit = ""
    if merge_sha:
        merge_commit = _resolve_commit(merge_sha, repo_root)  # validated by the caller already
    fatal = identity_error(pr, merge_state, pr_oid, merge_commit)
    if fatal:
        return {"pr": pr, "identity_error": fatal, "notes": notes}

    if not merge_commit and pr_oid:
        merge_commit = _resolve_commit(pr_oid, repo_root)
        if not merge_commit:
            notes.append(
                f"gh reports merge commit {pr_oid[:8]} but it is not present locally "
                "(fetch needed?)."
            )
    if not merge_commit:
        notes.append(
            "Merge commit unresolved — main_ci, refresh_commit and checkpoint confirmation "
            "are unavailable."
        )

    refresh = _refresh_commit(merge_commit, repo_root, notes)
    # The arc's CLOSING commit: the terminating refresh when one landed (this report is
    # emitted after the §12.2.1 fixed point), else the merge. Anything written before it is
    # not the arc's final checkpoint.
    anchor, anchor_kind = (refresh, "refresh") if refresh else (merge_commit, "merge")

    return {
        "pr": pr,
        "merge_state": merge_state,
        "merge_commit": merge_commit or None,
        "main_ci": _main_ci(merge_commit, repo_root, notes),
        "refresh_commit": refresh,
        "checkpoint": _checkpoint(
            anchor, anchor_kind, repo_root, repo_root, gstack_root, checkpoint, notes
        ),
        "todo_for_human": _todos(repo_root, notes),
        "notes": notes,
        "identity_error": None,
    }


# --- render (pure) ----------------------------------------------------------------------


def _sha8(v: Any) -> str:
    return str(v)[:8] if v else "none"


def render(data: dict[str, Any]) -> str:
    """The report file's text: a fenced yaml block (machine witness) + a short prose tail.

    Pure — no I/O, no clock, no subprocess. Only `YAML_FIELDS` reach the yaml block; the
    `notes` degradation list is rendered into the prose tail so the machine block stays
    exactly the declared contract.
    """
    block = yaml.safe_dump(
        {k: data.get(k) for k in YAML_FIELDS},
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
        width=100,
    )
    ci = _as_dict(data.get("main_ci"))
    ckpt = _as_dict(data.get("checkpoint"))
    # None = collection FAILED (rendered `todo_for_human: null` by the block above);
    # [] = genuinely nothing pending. The prose must keep the two claims apart.
    todos_raw = data.get("todo_for_human")
    todos: list[Any] | None = None if todos_raw is None else list(todos_raw)
    collect_notes: list[Any] = list(data.get("notes") or [])

    lines: list[str] = [
        f"# Arc exit report — PR #{data.get('pr')}",
        "",
        "```yaml",
        block.rstrip("\n"),
        "```",
        "",
    ]
    lines.append(
        f"PR #{data.get('pr')} is **{data.get('merge_state') or 'state unknown'}** at merge commit "
        f"`{_sha8(data.get('merge_commit'))}`; its post-merge main CI concluded "
        f"**{ci.get('conclusion') or 'unresolved'}**"
        + (f" ({ci['run_url']})" if ci.get("run_url") else "")
        + "."
    )
    lines.append(
        f"The §12.2.1 terminating refresh is `{_sha8(data.get('refresh_commit'))}`."
        if data.get("refresh_commit")
        else "No §12.2.1 terminating refresh commit was verified after the merge — one may "
        "still be owed."
    )
    anchor_word = "terminating refresh" if data.get("refresh_commit") else "merge"
    lines.append(
        f"Final checkpoint: `{ckpt.get('path')}`"
        + (
            f" (bound to this arc, written after the {anchor_word})."
            if ckpt.get("confirmed")
            else f" — NOT confirmed as this arc's final checkpoint (see notes); it is not"
            f" established to post-date the {anchor_word}."
        )
        if ckpt.get("path")
        else "No gstack checkpoint was found for this workspace."
    )
    if todos is None:
        lines += [
            "",
            "todo_for_human is UNKNOWN — the pending-HIL ledger could not be read "
            "(see notes); do NOT read this as 'nothing is waiting'.",
        ]
    elif todos:
        lines += ["", f"**{len(todos)} item(s) await a human** (still-pending DEFERRED-HIL rows):"]
        lines += [f"- {t}" for t in todos]
    else:
        lines += ["", "No pending DEFERRED-HIL items — nothing is waiting on a human."]
    if collect_notes:
        lines += ["", "Collection notes (degraded or unresolved fields):"]
        lines += [f"- {n}" for n in collect_notes]
    lines += [
        "",
        "*Generated by `just arc-exit-report` (U-WT-03) at the final ship-pr step, after the "
        "reflect / `/context-save` block. Regenerating for the same PR overwrites this file.*",
        "",
    ]
    return "\n".join(lines)


# --- write + index ----------------------------------------------------------------------


def report_path(repo_root: Path, pr: int) -> Path:
    """PR-keyed, date-free — a later re-run overwrites rather than orphaning a sibling."""
    return repo_root / REPORT_DIR / f"arc-exit-report-pr{pr}.md"


def append_ledger_row(repo_root: Path, data: dict[str, Any], rel_path: str) -> bool:
    """Append the `EXIT-REPORT` index row through `loop_lib.sh`'s own `loop_log`.

    A bash shim, deliberately: the row's timestamp + pipe-escaping + table format have
    exactly one implementation (`loop_log`, loop_lib.sh:77-85) and a Python copy would be
    a second authority free to drift. Returns False (never raises) on any failure — the
    report itself is the deliverable, the index row is a convenience.
    """
    ci = _as_dict(data.get("main_ci"))
    todos_raw = data.get("todo_for_human")
    # None = collection failed → `todos=unknown`, never a confident 0 (codex round-2).
    todos_field = "unknown" if todos_raw is None else str(len(list(todos_raw)))
    detail = (
        f"pr=#{data.get('pr')} "
        f"ci={_sha8(ci.get('commit'))}:{ci.get('conclusion') or 'none'} "
        f"refresh={_sha8(data.get('refresh_commit'))} "
        f"todos={todos_field} "
        f"path={rel_path}"
    )
    lib = repo_root / "tools" / "hooks" / "lib.sh"
    loop_lib = repo_root / "tools" / "hooks" / "loop_lib.sh"
    if not (lib.is_file() and loop_lib.is_file()):
        return False
    ledger = repo_root / LEDGER_REL
    # Pre/post growth check (codex round-1 P3): a substring match alone can false-pass on
    # an idempotent rerun by matching the PREVIOUS invocation's identical row while
    # loop_log's failure-invisible append silently did nothing (unwritable ledger, full
    # disk). Success = the file GREW this invocation AND the new tail carries the detail.
    try:
        before = len(ledger.read_text(encoding="utf-8")) if ledger.is_file() else 0
    except OSError:
        before = 0
    # Constant bash source; paths + detail all travel as argv values (codex round-6 P2).
    rc, _ = run(
        [
            "bash",
            "-c",
            'CLAUDE_PROJECT_DIR="$1"; . "$2"; . "$3"; loop_log EXIT-REPORT "$4"',
            "arc_exit_report",  # $0
            str(repo_root),
            str(lib),
            str(loop_lib),
            detail,
        ],
        repo_root,
    )
    if rc != 0:
        return False
    try:
        text = ledger.read_text(encoding="utf-8") if ledger.is_file() else ""
    except OSError:
        return False
    return len(text) > before and detail.replace("|", "\\|") in text[before:]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Write the arc EXIT REPORT for a merged PR (U-WT-03).")
    ap.add_argument("--pr", type=int, required=True, help="PR number this arc closed with")
    ap.add_argument(
        "--merge-sha", default=None, help="merge commit (defaults to gh's answer for --pr)"
    )
    ap.add_argument(
        "--checkpoint",
        default=None,
        help=(
            "the checkpoint file this arc's /context-save just wrote. Required for "
            "checkpoint.confirmed to be true — without it the workspace-newest file is "
            "reported as an unconfirmed heuristic (a parallel arc may own it)."
        ),
    )
    ap.add_argument(
        "--repo-root",
        default=None,
        help=(
            "repository root to write into. Defaults to the MAIN checkout of the enclosing "
            "repo (not a disposable arc worktree). An explicit value always wins."
        ),
    )
    args = ap.parse_args(argv)

    if args.pr <= 0:
        print(f"ERROR: --pr must be a positive PR number (got {args.pr}).", file=sys.stderr)
        return 2

    start = Path(args.repo_root).resolve() if args.repo_root else Path.cwd()
    # An explicit --repo-root is authoritative: no main-checkout redirect.
    resolved, root_notes = resolve_repo_root(start, redirect=not args.repo_root)
    if resolved is None:
        print(f"ERROR: {start} is not inside a git repository.", file=sys.stderr)
        return 2
    root = resolved

    if args.merge_sha and not _resolve_commit(args.merge_sha, root):
        print(
            f"ERROR: --merge-sha {args.merge_sha} does not resolve to a commit in {root}.",
            file=sys.stderr,
        )
        return 2

    ckpt: Path | None = None
    if args.checkpoint:
        ckpt = Path(args.checkpoint).expanduser()
        if not ckpt.is_file():
            print(f"ERROR: --checkpoint {ckpt} is not an existing file.", file=sys.stderr)
            return 2

    data = collect(args.pr, args.merge_sha, root, checkpoint=ckpt, seed_notes=root_notes)
    if data.get("identity_error"):
        # Write NOTHING: a report naming this PR while carrying another arc's facts is
        # worse than no report at all.
        print(f"ERROR: {data['identity_error']}", file=sys.stderr)
        return 2
    out = report_path(root, args.pr)
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(data), encoding="utf-8")
    except OSError as e:
        print(f"ERROR: could not write {out}: {e}", file=sys.stderr)
        return 2

    rel = str(out.relative_to(root))
    if not append_ledger_row(root, data, rel):
        print(
            f"WARNING: EXIT-REPORT ledger row could not be appended to {LEDGER_REL}.",
            file=sys.stderr,
        )
    print(f"wrote {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
