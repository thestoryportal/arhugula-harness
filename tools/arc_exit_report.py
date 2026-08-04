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

Design: a PURE `render(data) -> str` plus a thin `collect()` that shells `gh`/`git`. Every
external call is validated (exit code + non-empty + parses) before its output flows
anywhere; a missing/unauthenticated `gh` degrades to explicit nulls plus a note in the
prose tail — it never crashes and never fabricates a value. In particular:

  * `refresh_commit` is null unless a commit after the merge is verified to be a
    terminating refresh per CLAUDE.md §12.2.1 — subject prefix AND a changed-file set of
    exactly `.harness/roadmap_status.md`. Never guessed from position.
  * `main_ci.conclusion` is copied VERBATIM from `gh` — never coerced to "success", never
    normalized. When several workflow runs share the merge commit, the reported run is
    the FIRST non-success one (any of failure / cancelled / null-while-pending); only when
    every run concluded `success` is `success` reported. A single red auxiliary workflow
    can therefore never be masked by a green one.
  * `checkpoint.confirmed` is true only when the newest gstack checkpoint's mtime is
    strictly newer than the merge commit's commit time; unknown → false, never assumed.

Usage:
    uv run python tools/arc_exit_report.py --pr 1202 [--merge-sha SHA] [--repo-root PATH]

Exit codes: 0 success (including degraded-with-nulls), 2 unusable inputs (not a git repo,
unresolvable `--merge-sha`, unwritable output). Re-running for the same PR is idempotent:
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


def _resolve_commit(sha: str, cwd: Path) -> str:
    """Full 40-char SHA for `sha`, or '' if it does not resolve to a commit in this repo."""
    rc, out = run(["git", "rev-parse", "--verify", "--quiet", f"{sha}^{{commit}}"], cwd)
    return out if rc == 0 and len(out) == 40 else ""


def _main_ci(commit: str, cwd: Path, notes: list[str]) -> dict[str, Any]:
    """The post-merge CI verdict for `commit`. Conclusion copied verbatim; worst-first
    selection across the commit's runs (see module docstring)."""
    blank: dict[str, Any] = {"commit": commit or None, "conclusion": None, "run_url": None}
    if not commit:
        return blank
    raw = _gh_json(
        [
            "run",
            "list",
            "--commit",
            commit,
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
        notes.append(f"No workflow runs found for merge commit {commit[:8]} — main_ci unresolved.")
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


def _refresh_commit(merge_commit: str, cwd: Path, notes: list[str]) -> str | None:
    """The FIRST §12.2.1 terminating-refresh commit landed after `merge_commit`, or None.

    Verified, not inferred: subject must start with the reserved prefix AND the commit's
    changed-file set must be exactly `.harness/roadmap_status.md`. A refresh-titled commit
    that touches anything else is NOT terminating and is deliberately not reported.
    """
    if not merge_commit:
        return None
    ref = _default_ref(cwd)
    rc, out = run(["git", "log", "--reverse", "--format=%H%x09%s", f"{merge_commit}..{ref}"], cwd)
    if rc != 0:
        notes.append(
            f"`git log {merge_commit[:8]}..{ref}` exited {rc} — refresh_commit unresolved."
        )
        return None
    for line in out.splitlines():
        sha, _, subject = line.partition("\t")
        if not subject.startswith(REFRESH_PREFIX):
            continue
        frc, files = run(["git", "show", "--name-only", "--format=", sha], cwd)
        if frc != 0:
            notes.append(
                f"`git show --name-only {sha[:8]}` exited {frc} — candidate refresh not verifiable."
            )
            continue
        changed = [f for f in files.splitlines() if f.strip()]
        if changed == [REFRESH_ONLY_FILE]:
            return sha
        notes.append(
            f"{sha[:8]} carries the refresh title but changed {len(changed)} file(s) — not a "
            "§12.2.1 terminating refresh; not reported."
        )
    if not out:
        notes.append(
            "No commits after the merge on the default branch — no refresh owed yet, or "
            "not yet landed."
        )
    return None


def _checkpoint(
    repo_root: Path, merge_commit: str, cwd: Path, gstack_root: Path | None
) -> dict[str, Any]:
    """The newest gstack `/context-save` checkpoint, and whether it post-dates the merge.

    Both slug spellings this workspace has produced are scanned (`<repo-dir-name>` and
    `<owner>-<repo>`); the globally newest file across them wins. `confirmed` is true only
    when the checkpoint's mtime is strictly after the merge commit's commit time — an
    unknown merge time yields false, never an assumption.
    """
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
    if newest is None:
        return {"path": None, "confirmed": False}
    merge_ts = None
    if merge_commit:
        trc, ts = run(["git", "show", "-s", "--format=%ct", merge_commit], cwd)
        if trc == 0 and ts.isdigit():
            merge_ts = int(ts)
    confirmed = merge_ts is not None and newest.stat().st_mtime > merge_ts
    return {"path": str(newest), "confirmed": confirmed}


def _todos(repo_root: Path, notes: list[str]) -> list[str]:
    """Still-pending DEFERRED-HIL rows, one per entry, via `loop_pending_hil_list`.

    Shells the real `loop_lib.sh` helper rather than re-parsing the ledger here — the
    ledger parse has exactly one implementation (`_loop_pending_hil_rows`), shared with
    the bounded `loop_pending_hil_summary` the SessionStart hook surfaces.
    """
    lib = repo_root / "tools" / "hooks" / "lib.sh"
    loop_lib = repo_root / "tools" / "hooks" / "loop_lib.sh"
    if not (lib.is_file() and loop_lib.is_file()):
        notes.append("tools/hooks/loop_lib.sh not found — todo_for_human could not be collected.")
        return []
    rc, out = run(
        [
            "bash",
            "-c",
            f'CLAUDE_PROJECT_DIR="{repo_root}"; . "{lib}"; . "{loop_lib}"; loop_pending_hil_list',
        ],
        repo_root,
    )
    if rc != 0:
        notes.append(
            f"`loop_pending_hil_list` exited {rc} — todo_for_human could not be collected."
        )
        return []
    return [line.strip() for line in out.splitlines() if line.strip()]


def collect(
    pr: int, merge_sha: str | None, repo_root: Path, gstack_root: Path | None = None
) -> dict[str, Any]:
    """Gather the arc's closure facts. Degrades to nulls + notes; never raises, never fabricates."""
    notes: list[str] = []
    pr_view = _as_dict(
        _gh_json(
            ["pr", "view", str(pr), "--json", "state,mergeCommit"], repo_root, notes, "merge_state"
        )
    )
    merge_state: str | None = pr_view.get("state")

    merge_commit = ""
    if merge_sha:
        merge_commit = _resolve_commit(merge_sha, repo_root)  # validated by the caller already
    if not merge_commit:
        oid: str = _as_dict(pr_view.get("mergeCommit")).get("oid") or ""
        if oid:
            merge_commit = _resolve_commit(oid, repo_root)
            if not merge_commit:
                notes.append(
                    f"gh reports merge commit {oid[:8]} but it is not present locally "
                    "(fetch needed?)."
                )
    if not merge_commit:
        notes.append(
            "Merge commit unresolved — main_ci, refresh_commit and checkpoint confirmation "
            "are unavailable."
        )

    return {
        "pr": pr,
        "merge_state": merge_state,
        "merge_commit": merge_commit or None,
        "main_ci": _main_ci(merge_commit, repo_root, notes),
        "refresh_commit": _refresh_commit(merge_commit, repo_root, notes),
        "checkpoint": _checkpoint(repo_root, merge_commit, repo_root, gstack_root),
        "todo_for_human": _todos(repo_root, notes),
        "notes": notes,
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
    todos: list[Any] = list(data.get("todo_for_human") or [])
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
    lines.append(
        f"Final checkpoint: `{ckpt.get('path')}`"
        + (
            " (written after the merge)."
            if ckpt.get("confirmed")
            else " — NOT confirmed to post-date the merge."
        )
        if ckpt.get("path")
        else "No gstack checkpoint was found for this workspace."
    )
    if todos:
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
    todos: list[Any] = list(data.get("todo_for_human") or [])
    detail = (
        f"pr=#{data.get('pr')} "
        f"ci={_sha8(ci.get('commit'))}:{ci.get('conclusion') or 'none'} "
        f"refresh={_sha8(data.get('refresh_commit'))} "
        f"todos={len(todos)} "
        f"path={rel_path}"
    )
    lib = repo_root / "tools" / "hooks" / "lib.sh"
    loop_lib = repo_root / "tools" / "hooks" / "loop_lib.sh"
    if not (lib.is_file() and loop_lib.is_file()):
        return False
    rc, _ = run(
        [
            "bash",
            "-c",
            f'CLAUDE_PROJECT_DIR="{repo_root}"; . "{lib}"; . "{loop_lib}"; '
            'loop_log EXIT-REPORT "$1"',
            "loop_log",
            detail,
        ],
        repo_root,
    )
    if rc != 0:
        return False
    ledger = repo_root / LEDGER_REL
    try:
        return ledger.is_file() and detail.replace("|", "\\|") in ledger.read_text(encoding="utf-8")
    except OSError:
        return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Write the arc EXIT REPORT for a merged PR (U-WT-03).")
    ap.add_argument("--pr", type=int, required=True, help="PR number this arc closed with")
    ap.add_argument(
        "--merge-sha", default=None, help="merge commit (defaults to gh's answer for --pr)"
    )
    ap.add_argument(
        "--repo-root", default=None, help="repository root (defaults to the enclosing repo)"
    )
    args = ap.parse_args(argv)

    if args.pr <= 0:
        print(f"ERROR: --pr must be a positive PR number (got {args.pr}).", file=sys.stderr)
        return 2

    root = Path(args.repo_root).resolve() if args.repo_root else Path.cwd()
    rc, top = run(["git", "rev-parse", "--show-toplevel"], root)
    if rc != 0 or not top:
        print(
            f"ERROR: {root} is not inside a git repository (git rev-parse exited {rc}).",
            file=sys.stderr,
        )
        return 2
    root = Path(top)

    if args.merge_sha and not _resolve_commit(args.merge_sha, root):
        print(
            f"ERROR: --merge-sha {args.merge_sha} does not resolve to a commit in {root}.",
            file=sys.stderr,
        )
        return 2

    data = collect(args.pr, args.merge_sha, root)
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
