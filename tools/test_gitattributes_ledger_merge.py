"""B-255: no tracked ledger may be `merge=union`, and here is the measurement why.

`merge=union` looks obviously right for an append-only JSONL log — two lanes appending
concurrently is the NORMAL case under the C-HE-01 lane model, and hand-resolving those
appends is pure overhead. It is still WRONG here, and the reason is worth a test rather
than a comment alone, because the failure is silent.

Append-only is not sufficient; the rows must also be INDEPENDENT. In
`.harness/merge-gate-log.jsonl` they are not: `finding_record.reduce_last_by_finding_id`
makes PHYSICAL FILE ORDER the ordering authority for a finding's disposition (and its
docstring refuses to reorder by `ts`), while `_check_against_prior_rows` runs only inside
the locked append path, so a merge never re-validates what it combines. Union therefore
lets MERGE DIRECTION decide whether a finding reads `accepted` or `rejected` —
`test_union_would_make_the_gate_log_merge_direction_dependent` measures exactly that.

So the guard is the absence: nothing tracked is union-merged, and a conflict is the
correct outcome — it routes two lanes' colliding rows to a human.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

#: No global/system config, no ambient identity: the scratch repos below must behave the
#: same on any machine and in CI (hermetic-git-identity discipline).
HERMETIC_ENV = {
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@example.invalid",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@example.invalid",
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_SYSTEM": "/dev/null",
    "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin",
}

GATE_LOG = ".harness/merge-gate-log.jsonl"


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, env=HERMETIC_ENV
    )
    if proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in {repo}: {proc.stderr.strip()}")
    return proc.stdout


def _tracked_jsonl() -> list[str]:
    tracked = [p for p in _git(REPO, "ls-files", "*.jsonl").split() if p]
    assert tracked, "no tracked .jsonl files found — the ls-files query is wrong"
    return tracked


def test_no_tracked_ledger_is_union_merged() -> None:
    """The guard. Asks GIT what it will do, so it still fails if the attribute is
    spelled in some other way that resolves to union."""
    unioned = [rel for rel in _tracked_jsonl() if _merge_attr(rel) == "union"]
    assert not unioned, (
        "these ledgers are set to union-merge, which silently lets merge direction "
        f"decide a finding's disposition (see this module's docstring): {unioned}"
    )


def _merge_attr(rel: str) -> str:
    """What git itself says it will do — `<path>: merge: <value>`."""
    return _git(REPO, "check-attr", "merge", "--", rel).strip().rsplit(": ", 1)[-1]


@pytest.mark.parametrize("direction", ["accepted-last", "rejected-last"])
def test_union_would_make_the_gate_log_merge_direction_dependent(
    tmp_path: Path, direction: str
) -> None:
    """The measurement behind the guard, kept executable rather than asserted in prose.

    Two lanes adjudicate the same finding_id differently. Each row is individually legal
    — each was written through the locked append path against its own view — so union
    merges them CLEANLY. The reduction that readers use then names whichever row landed
    physically last, which is decided by who merged into whom.
    """
    repo = tmp_path / "r"
    (repo / ".harness").mkdir(parents=True)
    _git(repo.parent, "init", "-q", repo.name)
    # force union HERE only: the real .gitattributes must never carry it
    (repo / ".gitattributes").write_text(f"{GATE_LOG} merge=union\n")
    (repo / GATE_LOG).write_text('{"finding_id": "f1", "disposition": null}\n')
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")
    base = _git(repo, "rev-parse", "HEAD").strip()

    def branch(name: str, disposition: str) -> None:
        _git(repo, "checkout", "-q", "-b", name, base)
        with (repo / GATE_LOG).open("a") as fh:
            fh.write(json.dumps({"finding_id": "f1", "disposition": disposition}) + "\n")
        _git(repo, "commit", "-qam", name)

    branch("accepts", "accepted")
    branch("rejects", "rejected")

    # merging X into Y puts X's row last, so Y's reader sees X's disposition
    into, other = ("rejects", "accepts") if direction == "accepted-last" else ("accepts", "rejects")
    _git(repo, "checkout", "-q", into)
    _git(repo, "merge", "-q", other)

    text = (repo / GATE_LOG).read_text()
    assert "<<<<<<<" not in text, "union was expected to merge cleanly — that is the danger"
    reduced: dict[str, dict] = {}
    for line in text.splitlines():
        if line.strip():
            row = json.loads(line)
            reduced[row["finding_id"]] = row  # reduce_last_by_finding_id, file order
    expected = "accepted" if direction == "accepted-last" else "rejected"
    assert reduced["f1"]["disposition"] == expected, (
        "union no longer orders unioned hunks by merge direction; re-derive whether the "
        "B-255 exclusion still needs to hold"
    )
