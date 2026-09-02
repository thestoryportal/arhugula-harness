#!/usr/bin/env python3
"""U-HE-36 / U-WT-07 — prospective merge-tree check + O3 base rate (C-HE-13 §4-5).

Declared ``scope.files`` is a scheduling HINT (the forward register carries no such
keys); the gate is actual-write. Before a lane opens an arc, the candidate head is
``git merge-tree --write-tree``'d against every other lane's current head and selection
is refused on a non-empty conflict set. "Every other lane's current head" is the branch
of every NON-terminal reservation: C-HE-03 §4 keeps a lane ``pending`` for its whole
build and flips it ``open`` only at drain start, so an ``open``-only read would see no
lane until it was already landing.

``check`` exit codes are a contract: 0 disjoint · 1 textual conflict (one ``CONFLICT``
line per path) · 2 the check could not complete (unknown lane id, an other-lane branch
with no local or origin ref, a merge-tree error) — fail closed, never a clean pass by
omission.

``historical`` is the O3 base-rate recipe: replay the 172 historical colliding pairs
(``derive-pairs`` rebuilds the list from the P-R3 window) as concurrent lanes and report
the real textual-conflict rate against the 38.7 % file-overlap upper bound, with the
semantic-conflict rate reported as unmeasured, not zero.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import reservations as rs

REPO = Path(__file__).resolve().parent.parent
LANE_ID_FILE = REPO / ".harness" / ".lane-id"
O3_PAIRS = REPO / ".harness" / "plan" / "o3-colliding-pairs.txt"
UPPER_BOUND = 0.387
#: P-R3 conflict-surface window (parallel-lanes-2026-08-17): the 150 merged PRs
#: #1239..#1391 in merge order, paired PR i vs each of the next 3 (a 4-lane window).
O3_WINDOW = (1239, 1391)
O3_LANES = 4
#: The four near-universal loop-governance files P-R3 excluded from its 38.7 % figure;
#: a pair colliding only here does not count against that bound.
GOVERNANCE_FILES = frozenset(
    {
        ".harness/roadmap_status.md",
        ".harness/forward-register.yaml",
        ".harness/arc-ledger.yaml",
        ".harness/merge-gate-log.md",
    }
)
#: C-HE-03 §2 states that are a lane's live head (terminal = merged | abandoned).
NON_TERMINAL = frozenset({"pending", "open"})
#: Per git call (the plan's fetch bound, U-HE-36 step 3); a hung git must land on exit 2,
#: never hang a selection.
GIT_TIMEOUT_S = 60
_OID = re.compile(r"[0-9a-f]{40}")


class MergeTreeError(RuntimeError):
    """``git merge-tree`` (or a plumbing call it needs) exited with an error, not a verdict."""


class CheckIncompleteError(RuntimeError):
    """The prospective check cannot be completed; ``check`` exits 2 with this message."""


@dataclass(frozen=True)
class LaneHead:
    arc_id: str
    lane_id: str
    state: str
    branch: str
    ref: str | None  # full ref name the branch resolved to; None = no local or origin ref


def _git(
    repo: Path, *args: str, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        env=None if env is None else {**os.environ, **env},
        check=False,
        timeout=GIT_TIMEOUT_S,
    )


def _plumbing(repo: Path, *args: str, env: dict[str, str] | None = None) -> str:
    p = _git(repo, *args, env=env)
    if p.returncode != 0:
        raise MergeTreeError(f"git {' '.join(args)} failed ({p.returncode}): {p.stderr.strip()}")
    return p.stdout.strip()


def merge_conflicts(
    repo: Path, ours: str, theirs: str, env: dict[str, str] | None = None
) -> list[str]:
    """Conflicted paths of a real (``--write-tree``) merge of ``theirs`` into ``ours``.

    ``-z`` output is ``<tree-oid> NUL (<path> NUL)* NUL <informational messages>``: the
    path list ends at the first empty entry — the messages after it (``Auto-merging …``,
    ``CONFLICT (content): …``) are NOT paths. The conflict verdict is exit 1 WITH a tree
    OID: on git 2.39.5 an unresolvable ref also exits 1, with no OID and no paths, and
    reading that as "no conflict" would pass a check that never ran. Anything else is an
    error, never a verdict.
    """
    p = _git(repo, "merge-tree", "--write-tree", "--name-only", "-z", ours, theirs, env=env)
    parts = p.stdout.split("\0")
    if p.returncode == 0:
        return []
    if p.returncode == 1 and _OID.fullmatch(parts[0]):
        return list(itertools.takewhile(lambda s: s != "", parts[1:]))
    raise MergeTreeError(f"merge-tree {ours} {theirs} failed ({p.returncode}): {p.stderr.strip()}")


def conflicts(repo: Path, candidate_ref: str, other_refs: list[str]) -> list[str]:
    """Plan signature (U-HE-36 step 2): ``"<other>: <path>"`` per conflicted path."""
    return [
        f"{other}: {path}"
        for other in other_refs
        for path in merge_conflicts(repo, other, candidate_ref)
    ]


def resolve_ref(repo: Path, branch: str) -> str | None:
    """The local branch ref, else its origin tracking ref, else None.

    Lanes share one repository (worktrees under ``.codex-worktrees/`` / ``.claude/worktrees/``),
    so a sibling's head is normally a local branch fresher than anything pushed.
    """
    for full in (f"refs/heads/{branch}", f"refs/remotes/origin/{branch}"):
        if _git(repo, "rev-parse", "--verify", "--quiet", f"{full}^{{commit}}").returncode == 0:
            return full
    return None


def other_lane_heads(repo: Path, me: str) -> list[LaneHead]:
    """Every non-terminal reservation held by another lane, with its branch resolved.

    A corrupt or symlinked sibling raises (``reservations.current`` is the authority) — for a
    gate that is exit 2, not the best-effort skip ``sibling_open_count`` takes for a sensor.
    """
    root = rs.reservations_root()
    dirs = (
        sorted(d for d in root.iterdir() if d.is_dir() and not d.name.startswith("."))
        if root.is_dir()
        else []
    )
    heads = []
    for d in dirs:
        cur = rs.current(d.name)
        if cur is None:  # headless dir: a reserve that died before its first generation landed
            continue
        rec = cur[1]
        if rec["state"] in NON_TERMINAL and rec["lane_id"] != me:
            heads.append(
                LaneHead(
                    d.name,
                    rec["lane_id"],
                    rec["state"],
                    rec["branch"],
                    resolve_ref(repo, rec["branch"]),
                )
            )
    return heads


def lane_id() -> str:
    """This lane's id: ``HARNESS_LANE_ID`` (same shell as lane-init) else the persisted file.

    Shell exports do not survive across Bash tool calls; ``.harness/.lane-id`` is the durable
    form (U-HE-31). Neither present → the check cannot tell its own reservation from a
    sibling's and must not guess.
    """
    v = os.environ.get("HARNESS_LANE_ID", "")
    if not v:
        try:  # the arc_exit_report read shape: an unreadable marker is "absent"
            v = LANE_ID_FILE.read_text(encoding="utf-8").strip()
        except OSError:
            v = ""
    if not v:
        raise CheckIncompleteError(
            "lane id unknown: export HARNESS_LANE_ID (source tools/hooks/lane-init.sh) first"
        )
    return v


def check(repo: Path, candidate: str, me: str) -> int:
    fetch = _git(repo, "fetch", "-q", "origin")
    if fetch.returncode != 0:
        print(
            f"WARN fetch origin failed ({fetch.returncode}): {fetch.stderr.strip()}"
            " -- checking local refs only",
            file=sys.stderr,
        )
    heads = other_lane_heads(repo, me)
    unresolved = [h for h in heads if h.ref is None]
    for h in unresolved:
        print(
            f"UNRESOLVED {h.arc_id} [{h.lane_id}] {h.state}: branch {h.branch}"
            " has no local or origin ref"
            " -- cannot merge-tree it; if that lane is dead, abandon its reservation (C-HE-03 §5)"
        )
    if unresolved:
        return 2
    found = [(h, path) for h in heads if h.ref for path in merge_conflicts(repo, h.ref, candidate)]
    for h, path in found:
        print(f"CONFLICT {h.arc_id} [{h.lane_id}] {h.branch}: {path}")
    if not found:
        print(f"disjoint: {candidate} vs {len(heads)} other lane head(s)")
    return 1 if found else 0


# --- O3 historical base rate -------------------------------------------------------


@contextmanager
def scratch_objects(repo: Path) -> Iterator[dict[str, str]]:
    """Env that writes new objects to a temp dir while reading the repo's as an alternate.

    The replay mints synthetic commits and merged trees per pair; under this env none of
    them lands in the repository's object store (verified empirically on git 2.39.5).
    """
    objects = Path(_plumbing(repo, "rev-parse", "--git-path", "objects"))
    objects = objects if objects.is_absolute() else repo / objects
    with tempfile.TemporaryDirectory(prefix="arc-disjoint-objects-") as tmp:
        yield {
            "GIT_OBJECT_DIRECTORY": tmp,
            "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(objects.resolve()),
        }


def footprint(repo: Path, sha: str) -> frozenset[str]:
    """Changed-file set of a squash-merge commit, the P-R3 way (``git show --name-only``)."""
    return frozenset(
        ln for ln in _plumbing(repo, "show", "--name-only", "--format=", sha).splitlines() if ln
    )


def synthetic_commit(repo: Path, tree_of: str, parent: str, env: dict[str, str]) -> str:
    """A commit carrying ``tree_of``'s tree parented at ``parent`` (written under ``env``)."""
    return _plumbing(
        repo,
        "commit-tree",
        f"{tree_of}^{{tree}}",
        "-p",
        parent,
        "-m",
        "arc_disjoint_check replay",
        env=env,
    )


def pair_conflicts(repo: Path, a: str, b: str, env: dict[str, str]) -> list[str]:
    """Textual-conflict paths had ``b`` (merged later) been developed concurrently with ``a``.

    git 2.39 ``merge-tree`` has no ``--merge-base``, so the replay parents ``b``'s tree at
    ``a^`` (the pre-``a`` base) and merges it with ``a``. ``b``'s tree also carries the
    commits between ``a`` and ``b``; their overlap with ``a`` is measured separately (``b^``'s
    tree at the same base) and subtracted, and the result is restricted to ``b``'s own
    footprint minus the governance files. Conservative: a file where both an intermediate
    and ``b`` overlap ``a`` is masked (attributed to the earlier pair). For an adjacent
    pair ``b^ == a`` and the subtrahend is empty by construction.
    """
    base = _plumbing(repo, "rev-parse", f"{a}^")
    with_b = set(merge_conflicts(repo, a, synthetic_commit(repo, b, base, env), env))
    with_pre = set(merge_conflicts(repo, a, synthetic_commit(repo, f"{b}^", base, env), env))
    return sorted(((with_b - with_pre) & footprint(repo, b)) - GOVERNANCE_FILES)


@dataclass(frozen=True)
class MergedPr:
    number: int
    sha: str
    files: frozenset[str]


def window_pairs(prs: list[MergedPr], lanes: int = O3_LANES) -> list[tuple[MergedPr, MergedPr]]:
    """P-R3 §2: PR i vs each of the next ``lanes - 1`` in merge order, colliding iff their
    changed-file sets intersect after excluding the governance files."""
    return [
        (a, b)
        for i, a in enumerate(prs)
        for b in prs[i + 1 : i + lanes]
        if (a.files - GOVERNANCE_FILES) & (b.files - GOVERNANCE_FILES)
    ]


def merged_prs(repo: Path, first: int, last: int) -> list[MergedPr]:
    """Merged PRs ``first..last`` in ``mergedAt`` order, footprints from their merge commits."""
    p = subprocess.run(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "merged",
            "--limit",
            "1000",
            "--json",
            "number,mergedAt,mergeCommit",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if p.returncode != 0:
        raise MergeTreeError(f"gh pr list failed ({p.returncode}): {p.stderr.strip()}")
    rows = sorted(
        (r for r in json.loads(p.stdout) if first <= r["number"] <= last),
        key=lambda r: r["mergedAt"],
    )
    return [
        MergedPr(r["number"], r["mergeCommit"]["oid"], footprint(repo, r["mergeCommit"]["oid"]))
        for r in rows
    ]


def window_pair_count(n_prs: int, lanes: int = O3_LANES) -> int:
    """All window pairs, colliding or not — the 38.7 % bound's denominator (444 for 150 PRs)."""
    return sum(min(lanes - 1, n_prs - 1 - i) for i in range(n_prs))


@dataclass(frozen=True)
class PairList:
    window_pairs: int  # denominator every rate below is over
    pairs: list[tuple[str, str]]  # (earlier sha, later sha) — the colliding subset


_WINDOW_PAIRS_HEADER = "# window-pairs: "


def write_pairs(path: Path, prs: list[MergedPr], pairs: list[tuple[MergedPr, MergedPr]]) -> None:
    lines = [
        "# o3-colliding-pairs -- derived by"
        " `uv run python tools/arc_disjoint_check.py derive-pairs`",
        f"# window: merged PRs #{O3_WINDOW[0]}..#{O3_WINDOW[1]} by mergedAt ({len(prs)} PRs); "
        f"{O3_LANES}-lane window pairs (PR i vs the next {O3_LANES - 1})",
        "# collide = changed-file sets intersect after excluding: "
        + ", ".join(sorted(GOVERNANCE_FILES)),
        f"{_WINDOW_PAIRS_HEADER}{window_pair_count(len(prs))}",
        f"# pairs: {len(pairs)}",
        "# <sha earlier> <sha later> #<pr earlier> #<pr later>",
    ]
    lines += [f"{a.sha} {b.sha} #{a.number} #{b.number}" for a, b in pairs]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_pairs(path: Path) -> PairList:
    lines = path.read_text(encoding="utf-8").splitlines()
    denominators = [
        int(ln[len(_WINDOW_PAIRS_HEADER) :]) for ln in lines if ln.startswith(_WINDOW_PAIRS_HEADER)
    ]
    if len(denominators) != 1:
        raise ValueError(f"{path}: expected exactly one '{_WINDOW_PAIRS_HEADER}N' header line")
    rows = [ln.split() for ln in lines if ln.strip() and not ln.startswith("#")]
    return PairList(denominators[0], [(r[0], r[1]) for r in rows])


def historical(repo: Path, pairs_path: Path) -> int:
    pl = read_pairs(pairs_path)
    hits = 0
    with scratch_objects(repo) as env:
        for a, b in pl.pairs:
            paths = pair_conflicts(repo, a, b, env)
            hits += bool(paths)
            if paths:
                print(f"conflict {a[:12]} {b[:12]}: {', '.join(paths)}")
    n_win, n_col = pl.window_pairs, len(pl.pairs)
    print(
        f"O3: textual-conflict rate {hits}/{n_win} = {hits / n_win:.3f} of window pairs "
        f"(file-overlap upper bound {UPPER_BOUND} = {n_col}/{n_win}); "
        f"conditional on file overlap {hits}/{n_col} = {hits / n_col if n_col else 0.0:.3f}; "
        "governance files excluded; per-pair conservative"
    )
    print("semantic-conflict rate: unmeasured")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="prospective merge-tree check against every other lane's head")
    c.add_argument("--candidate", default="HEAD")
    h = sub.add_parser("historical", help="O3 base rate over the historical colliding pairs")
    h.add_argument("--pairs", type=Path, default=O3_PAIRS)
    d = sub.add_parser(
        "derive-pairs", help="rebuild the O3 pair list from the P-R3 window (needs gh)"
    )
    d.add_argument("--out", type=Path, default=O3_PAIRS)
    a = p.parse_args(argv)
    repo = REPO
    try:
        if a.cmd == "check":
            return check(repo, a.candidate, lane_id())
        if a.cmd == "historical":
            return historical(repo, a.pairs)
        prs = merged_prs(repo, *O3_WINDOW)
        pairs = window_pairs(prs)
        write_pairs(a.out, prs, pairs)
        print(f"{len(prs)} PRs, {len(pairs)} colliding pairs -> {a.out}")
        return 0
    except (
        CheckIncompleteError,
        MergeTreeError,
        subprocess.TimeoutExpired,
        # the sibling_open_count tuple: a corrupt/symlinked/short record is "cannot look"
        rs.ReservationError,
        OSError,
        ValueError,
        KeyError,
        TypeError,
    ) as e:
        # exit 1 is a VERDICT in this CLI's contract, so no failure may fall through to
        # Python's default exit 1 — every "cannot look" lands on 2, named.
        print(f"INCOMPLETE {type(e).__name__}: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
