"""B-255: the append-only ledgers union-merge, and the rewritten one must NOT.

Two lanes appending to `.harness/merge-gate-log.jsonl` concurrently is the NORMAL case
under the C-HE-01 lane model, not a conflict — so git should union the two appends
rather than hand a human a conflict hunk to resolve by hand (measured 2026-09-17: one
held branch's rows fenced a sibling lane's selection gate on that file alone).

The dangerous half is the exclusion. `.harness/arc-metrics.jsonl` is whole-file
rewritten by `arc_metrics.relabel_arc_type_close`, so union would keep BOTH the pre-
and post-relabel row for one arc AND MERGE CLEAN while doing it — silent corruption of
exactly the SPLIT_BRAIN_LEDGER state that module refuses. These tests assert the split
by asking GIT what it will do (`check-attr`, then a real merge), never by reading
`.gitattributes` as text, so they still fail if the attribute is spelled correctly and
behaves wrongly.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

#: Strictly append-only: every writer opens with O_APPEND / mode "a" and adds whole
#: lines. An adjudication is appended as its own row, never an in-place edit.
UNION_LEDGERS = (
    ".harness/merge-gate-log.jsonl",
    ".harness/mutation-probe-log.jsonl",
    ".harness/codex_credential_gates.jsonl",
)

#: Whole-file rewritten, so union is WRONG for it. Named, not merely absent — an
#: unclassified ledger is what `test_every_tracked_jsonl_is_classified` refuses.
REWRITTEN_LEDGERS = (".harness/arc-metrics.jsonl",)

#: No global/system config, no ambient identity: the scratch repos below must behave
#: the same on any machine and in CI (hermetic-git-identity discipline).
HERMETIC_ENV = {
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@example.invalid",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@example.invalid",
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_SYSTEM": "/dev/null",
    "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin",
}


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, env=HERMETIC_ENV
    )
    if proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {repo}: {proc.stderr.strip()}")
    return proc.stdout


def _merge_attr(repo: Path, rel: str) -> str:
    """What git itself says it will do — `<path>: merge: <value>`."""
    out = _git(repo, "check-attr", "merge", "--", rel).strip()
    return out.rsplit(": ", 1)[-1]


@pytest.mark.parametrize("rel", UNION_LEDGERS)
def test_append_only_ledgers_are_union_merged(rel: str) -> None:
    assert _merge_attr(REPO, rel) == "union"


@pytest.mark.parametrize("rel", REWRITTEN_LEDGERS)
def test_rewritten_ledgers_are_not_union_merged(rel: str) -> None:
    """The load-bearing exclusion: union here merges clean AND corrupts."""
    assert _merge_attr(REPO, rel) != "union"


def test_every_tracked_jsonl_is_classified() -> None:
    """A new ledger must be a DECISION, not a default.

    Without this, adding `.harness/whatever.jsonl` silently inherits "no union" — fine
    by luck if it is rewritten, a permanent hand-merge tax if it is append-only — and
    nobody is ever asked which it is.
    """
    tracked = {p for p in _git(REPO, "ls-files", "*.jsonl").split() if p}
    assert tracked, "no tracked .jsonl files found — the ls-files query is wrong"
    assert tracked == set(UNION_LEDGERS) | set(REWRITTEN_LEDGERS)


def _scratch_repo(tmp_path: Path, rel: str, base: str, ours: str, theirs: str) -> Path:
    """Two branches each write `rel`, starting from `base`. Returns the repo with the
    merge ATTEMPTED on the first branch, carrying THIS repo's real .gitattributes."""
    repo = tmp_path / "r"
    (repo / ".harness").mkdir(parents=True)
    _git(repo.parent, "init", "-q", repo.name)
    (repo / ".gitattributes").write_text((REPO / ".gitattributes").read_text())
    (repo / rel).write_text(base)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")
    first = _git(repo, "rev-parse", "--abbrev-ref", "HEAD").strip()
    _git(repo, "checkout", "-q", "-b", "side")
    (repo / rel).write_text(theirs)
    _git(repo, "commit", "-qam", "side")
    _git(repo, "checkout", "-q", first)
    (repo / rel).write_text(ours)
    _git(repo, "commit", "-qam", "ours")
    # The exit code is deliberately UNCHECKED here and only here: whether this merge
    # conflicts is the very thing each caller asserts, so the verdict has to be read off
    # the resulting FILE, not off git's status. Every other git call goes through _git,
    # which raises on failure.
    subprocess.run(["git", "merge", "side"], cwd=repo, capture_output=True, env=HERMETIC_ENV)
    return repo


def test_concurrent_appends_to_the_gate_log_merge_without_a_conflict(tmp_path: Path) -> None:
    """The whole point: two lanes' rows survive, in one file, with no hand resolution."""
    rel = ".harness/merge-gate-log.jsonl"
    base = '{"row": "base"}\n'
    repo = _scratch_repo(
        tmp_path, rel, base, base + '{"row": "ours"}\n', base + '{"row": "theirs"}\n'
    )
    text = (repo / rel).read_text()
    assert "<<<<<<<" not in text, f"union did not resolve the append conflict:\n{text}"
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    assert [r["row"] for r in rows] == ["base", "ours", "theirs"]


def test_a_rewritten_ledger_still_conflicts_so_a_human_adjudicates(tmp_path: Path) -> None:
    """The exclusion has TEETH, not merely an absent attribute.

    One branch relabels an arc's row in place (the real relabel_arc_type_close shape)
    while the other appends. Unioned, this merges clean and leaves arc `a` twice with
    contradictory `arc_type`. It must conflict instead.
    """
    rel = ".harness/arc-metrics.jsonl"
    base = '{"arc_id": "a", "arc_type": "inventing"}\n'
    repo = _scratch_repo(
        tmp_path,
        rel,
        base,
        base + '{"arc_id": "b", "arc_type": "inventing"}\n',
        '{"arc_id": "a", "arc_type": "applying"}\n',
    )
    text = (repo / rel).read_text()
    assert "<<<<<<<" in text, (
        "the relabel/append pair merged without a conflict — arc 'a' can now appear "
        f"twice with contradictory arc_type:\n{text}"
    )
