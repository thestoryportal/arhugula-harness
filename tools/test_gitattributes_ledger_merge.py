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
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import finding_record as fr

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


LOCATION = "tools/x.py:1"
#: minted by the production constructor: the id encodes sha1(location)[:12], and
#: `validate` rejects a hand-built one that disagrees.
FINDING_ID = fr.make_finding_id("codex_review_wrapper", "a" * 40, LOCATION, 1)


def _row(kind: str, ts: str, disposition: str | None = None) -> dict:
    """A schema-complete row for ONE finding_id. Built here rather than hand-rolled into
    the log so `finding_record.validate` is what judges it."""
    return {
        "finding_id": FINDING_ID,
        "location": LOCATION,
        "observed_evidence": "e",
        "expected_contract": "c",
        "severity": "P2",
        "finding_type": "terminal-block",
        "lineage_claim": "fresh",
        "producer": "codex_review_wrapper",
        "record_kind": kind,
        "ts": ts,
        "arc_id": "b-255-fixture",
        "lane_id": "lane-fixture",
        "head_sha": "a" * 40,
        "base_sha": "c" * 40,
        "diff_digest": "d" * 64,
        "round_n": 1,
        "cause_attribution": None,
        "disposition": disposition,
        "disposition_actor": "claude_absorber" if disposition else None,
        "unique_catch": None,
    }


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

    Two lanes adjudicate the same finding_id differently. Every row here is written
    through the PRODUCTION path — `finding_record.append_row`, which runs `validate()`
    and `_check_against_prior_rows` under the log's own lock — so the branch states are
    demonstrably legal rather than merely claimed to be (codex r3 P3). They are legal on
    BOTH branches because each branch carries exactly one adjudication, and C-HE-24 §5
    permits further adjudications to follow an adjudication anyway, so even the MERGED
    two-adjudication state breaks no write-time invariant. Nothing refuses it; the only
    thing that changes is which row is physically last, and `reduce_last_by_finding_id`
    reads exactly that.
    """
    repo = tmp_path / "r"
    (repo / ".harness").mkdir(parents=True)
    _git(repo.parent, "init", "-q", repo.name)
    # force union HERE only: the real .gitattributes must never carry it
    (repo / ".gitattributes").write_text(f"{GATE_LOG} merge=union\n")
    log = repo / GATE_LOG
    fr.append_row(_row("finding", "2026-01-01T00:00:00Z"), path=log)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "base")
    base = _git(repo, "rev-parse", "HEAD").strip()

    def branch(name: str, disposition: str, ts: str) -> None:
        _git(repo, "checkout", "-q", "-b", name, base)
        # the production writer, so validate() + _check_against_prior_rows both run
        fr.append_row(_row("finding_adjudication", ts, disposition), path=log)
        _git(repo, "commit", "-qam", name)

    branch("accepts", "accepted", "2026-01-01T00:01:00Z")
    branch("rejects", "rejected", "2026-01-01T00:02:00Z")

    # merging X into Y puts X's row last, so Y's reader sees X's disposition
    into, other = ("rejects", "accepts") if direction == "accepted-last" else ("accepts", "rejects")
    _git(repo, "checkout", "-q", into)
    _git(repo, "merge", "-q", other)

    text = (repo / GATE_LOG).read_text()
    assert "<<<<<<<" not in text, "union was expected to merge cleanly — that is the danger"
    # the PRODUCTION reducer, never a local copy of it: if reduce_last_by_finding_id ever
    # stops treating file order as authoritative, this witness must stop passing rather
    # than keep vouching for a rule the reader no longer follows (codex r2 P3)
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    reduced = fr.reduce_last_by_finding_id(rows)
    expected = "accepted" if direction == "accepted-last" else "rejected"
    assert reduced[FINDING_ID]["disposition"] == expected, (
        "union no longer orders unioned hunks by merge direction; re-derive whether the "
        "B-255 exclusion still needs to hold"
    )
