"""`tools/branch_hygiene_batch.py` — one guarded push for every deferred deletion (B-230 Task 4).

The plan's eight cases are the specification. `test_hostile_branch_name_is_quoted` is the
plan's test corrected at this arc: as written it compared argv[3] without the `:<oid>`
suffix the interface appends, and its second assertion stripped only the lease argument
while the quoted refspec still carried `;touch` — both assertions failed against a
correct implementation. The round-trip through `shlex.split`/`shlex.join` is the
property those assertions were reaching for.
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import branch_hygiene_batch as m
from branch_hygiene_batch import (
    CANONICAL_DEFER_SHAPE,
    Deferral,
    ForeignRow,
    UnreadableRow,
    build_push_command,
    parse_pending,
    parse_rows,
    resolve_cleared,
)

ROOT = Path(__file__).resolve().parents[1]
CARRIERS = (
    ROOT / ".claude" / "skills" / "ship-pr" / "SKILL.md",
    ROOT / ".agents" / "skills" / "ship-pr" / "SKILL.md",
)

ROW_A = (
    "[lane-1] u-sr-08 — branch hygiene close-out pending: feat/u-sr-08-context-noise-deletions "
    "(PR #1489, merged 9032fead4, main run green) and roadmap-refresh-post-1489 "
    "(PR #1490, merged ff62189d2, main run green) — run the guarded force-with-lease delete block"
)


# ── the plan's cases ─────────────────────────────────────────────────────────


def test_two_branches_one_atomic_command() -> None:
    cmd = build_push_command([("feat/a", "aaa111"), ("roadmap-refresh-post-1", "bbb222")])
    assert cmd == (
        "git push --atomic --force-with-lease=refs/heads/feat/a:aaa111 "
        "--force-with-lease=refs/heads/roadmap-refresh-post-1:bbb222 "
        "origin :refs/heads/feat/a :refs/heads/roadmap-refresh-post-1"
    )


def test_hostile_branch_name_is_quoted() -> None:
    cmd = build_push_command([("feat/a;touch pwned", "aaa111")])
    argv = shlex.split(cmd)
    # one argv element each, not two — the `;` never reaches the shell
    assert argv == [
        "git",
        "push",
        "--atomic",
        "--force-with-lease=refs/heads/feat/a;touch pwned:aaa111",
        "origin",
        ":refs/heads/feat/a;touch pwned",
    ]
    assert shlex.join(argv) == cmd


def test_empty_list_is_an_error() -> None:
    with pytest.raises(ValueError):
        build_push_command([])


def test_parse_pending_row_finds_both_branches_and_the_item() -> None:
    assert parse_pending(ROW_A) == [
        Deferral(
            "u-sr-08",
            [
                ("feat/u-sr-08-context-noise-deletions", "1489"),
                ("roadmap-refresh-post-1489", "1490"),
            ],
        )
    ]


def test_bare_branch_row_is_refused_not_skipped() -> None:
    with pytest.raises(UnreadableRow):
        parse_pending(
            "[lane-1] u-x — branch hygiene close-out pending: feat/u-x — run the guarded block"
        )


def test_crafted_item_id_is_refused() -> None:
    with pytest.raises(UnreadableRow):
        parse_pending(
            "[lane-1] $(touch pwned) — branch hygiene close-out pending: "
            "feat/a (PR #1, merged 111, main run green)"
        )


def _merged(
    head: str, oid: str = "aaa", base: str = "main", state: str = "MERGED"
) -> dict[str, Any]:
    return {
        "state": state,
        "baseRefName": base,
        "headRefName": head,
        "headRefOid": oid,
        "mergeCommit": {"oid": "m" + oid},
    }


@pytest.fixture
def green_main(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(m, "default_branch", lambda: "main")
    monkeypatch.setattr(m, "main_run_conclusion", lambda sha: "success")


def test_one_mismatch_aborts_the_batch(monkeypatch: pytest.MonkeyPatch, green_main: None) -> None:
    monkeypatch.setattr(m, "pr_view", lambda pr: _merged("feat/a" if pr == "1" else "other"))
    with pytest.raises(m.VerificationMismatch):
        m.verify_all([Deferral("u-a", [("feat/a", "1")]), Deferral("u-b", [("feat/b", "2")])])


@pytest.mark.parametrize(
    ("info", "conclusion", "reason"),
    [
        (_merged("feat/a", state="OPEN"), "success", "state is OPEN"),
        (_merged("feat/a", base="release/1"), "success", "merged into release/1, not main"),
        (_merged("feat/a"), "cancelled", "post-merge CI on main is cancelled, not success"),
        (_merged("feat/a"), "", "post-merge CI on main is empty, not success"),
    ],
)
def test_verify_requires_default_branch_and_green_post_merge_run(
    monkeypatch: pytest.MonkeyPatch, info: dict[str, Any], conclusion: str, reason: str
) -> None:
    """codex r1 P1 on b-230-task-4: the ship-pr close-out block checks all four facts before
    ONE delete; a batch that checked two would turn a side-branch merge into a force-delete."""
    monkeypatch.setattr(m, "default_branch", lambda: "main")
    monkeypatch.setattr(m, "main_run_conclusion", lambda sha: conclusion)
    monkeypatch.setattr(m, "pr_view", lambda pr: info)
    with pytest.raises(m.VerificationMismatch, match=reason):
        m.verify_all([Deferral("u-a", [("feat/a", "1")])])


def test_resolve_only_items_whose_branches_are_all_gone(monkeypatch: pytest.MonkeyPatch) -> None:
    gone = {"feat/a": True, "roadmap-refresh-post-1": True, "feat/b": False}
    monkeypatch.setattr(m, "remote_absent", lambda branch: gone[branch])
    resolved: list[tuple[str, str]] = []
    monkeypatch.setattr(m, "loop_resolve", lambda item, note: resolved.append((item, note)))
    left = resolve_cleared(
        [
            Deferral("u-a", [("feat/a", "1"), ("roadmap-refresh-post-1", "2")]),
            Deferral("u-b", [("feat/b", "3")]),
        ]
    )
    assert [i for i, _ in resolved] == ["u-a"]
    assert left == [Deferral("u-b", [("feat/b", "3")])]


# ── the shapes the live ledger actually carries ──────────────────────────────


def test_rows_without_main_run_green_or_with_a_trailing_note_still_parse() -> None:
    rows = (
        "[l] u-sr-09 — branch hygiene close-out pending: feat/u-sr-09-r2 "
        "(PR #1493, merged f28c4edc5) and roadmap-refresh-post-1493 "
        "(PR #1494, merged 8f436411a) — run the guarded block\n"
        "[l] b-230-task-3 — branch hygiene close-out pending: feat/t3 (PR #1505, merged a8df62d59, "
        "main run 33789535987 green) and roadmap-refresh-post-1505 (PR #1506, merged a9173dc8d, "
        "main run 33791027069 green) — run the guarded block (Task 4 batches these)\n"
    )
    assert parse_pending(rows) == [
        Deferral("u-sr-09", [("feat/u-sr-09-r2", "1493"), ("roadmap-refresh-post-1493", "1494")]),
        Deferral("b-230-task-3", [("feat/t3", "1505"), ("roadmap-refresh-post-1505", "1506")]),
    ]


def test_another_gates_deferral_is_a_foreign_row_not_an_error() -> None:
    """The reducer lists EVERY pending gate. A credentials deferral beside the hygiene rows
    is not unreadable — it is another tool's; it is typed as such and left pending, never
    refused (which would fence every other gate behind branch hygiene) and never dropped."""
    foreign = "[l] r-830 — needs the AWS profile r830 login before the live e2e can run"
    rows = parse_rows(foreign + "\n" + ROW_A)
    assert rows[0] == ForeignRow(foreign)
    assert isinstance(rows[1], Deferral)
    assert parse_pending(foreign + "\n" + ROW_A) == [rows[1]]


def test_unshaped_line_is_unreadable() -> None:
    with pytest.raises(UnreadableRow):
        parse_rows("not a reducer row at all")


@pytest.mark.parametrize(
    "tail",
    [
        " and roadmap-refresh-post-1",  # second pair truncated before its parenthesis
        " and roadmap-refresh-post-1 (PR #2, merged",  # second pair never closes
        " and roadmap-refresh-post-1 (merged bbb)",  # second pair without its PR
        " roadmap-refresh-post-1 (PR #2, merged bbb)",  # pairs not joined by ` and `
    ],
)
def test_a_malformed_second_pair_is_unreadable_not_a_one_branch_item(tail: str) -> None:
    """codex r1 P2 on b-230-task-4: a row that parsed as ONE branch would have its refresh
    branch hidden forever once the first was deleted and the item resolved."""
    with pytest.raises(UnreadableRow):
        parse_pending(
            f"[l] u-a — branch hygiene close-out pending: feat/a (PR #1, merged aaa1111){tail}"
        )


# ── the effectful edges ──────────────────────────────────────────────────────


def _completed(rc: int) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=[], returncode=rc, stdout="", stderr="boom")


@pytest.mark.parametrize(("rc", "expect"), [(0, False), (2, True)])
def test_remote_absent_reads_only_exit_zero_and_two(
    monkeypatch: pytest.MonkeyPatch, rc: int, expect: bool
) -> None:
    monkeypatch.setattr(m.subprocess, "run", lambda *a, **k: _completed(rc))
    assert m.remote_absent("feat/a") is expect


def test_remote_absent_aborts_on_any_other_exit(monkeypatch: pytest.MonkeyPatch) -> None:
    """Exit 128 (network, auth, a missing remote) is NOT "already gone" — resolving on it
    would clear a deferral whose branch is still there."""
    monkeypatch.setattr(m.subprocess, "run", lambda *a, **k: _completed(128))
    with pytest.raises(m.RemoteStateError):
        m.remote_absent("feat/a")


def _bash(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "bash",
            "-c",
            "source tools/hooks/lib.sh && source tools/hooks/loop_lib.sh && " + script,
            "t",
            *args,
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )


def test_resolve_lands_the_row_the_reducer_keys_on(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """End to end through the REAL `loop_resolve`: the reducer is last-write-wins per item
    id, so the RESOLVED-HIL row this tool appends is exactly what stops the deferral from
    being re-presented. The venue is a private ledger — every subprocess inherits it."""
    venue = tmp_path / "loop_status.md"
    monkeypatch.setenv("HARNESS_LOOP_STATUS_PATH", str(venue))
    item, note = "u-a", ROW_A.split(" — ", 1)[1]
    assert _bash('loop_defer "$1" "$2"', item, note).returncode == 0
    before = _bash("loop_pending_hil_list").stdout
    assert item in before and "feat/u-sr-08-context-noise-deletions" in before
    monkeypatch.setattr(m, "remote_absent", lambda branch: True)

    hostile = "u-b"  # a note carrying shell metacharacters must land verbatim, not run
    left = resolve_cleared(
        [*parse_pending(before), Deferral(hostile, [("x/$(touch pwned);y", "9")])]
    )

    assert left == []
    after = _bash("loop_pending_hil_list").stdout
    assert after.strip() == ""
    ledger = venue.read_text(encoding="utf-8")
    assert ledger.count("| RESOLVED-HIL |") == 2
    assert "x/$(touch pwned);y absent on origin" in ledger
    assert not (tmp_path / "pwned").exists() and not (ROOT / "pwned").exists()


# ── the CLI contract: exit codes, and nothing on stdout unless verified ───────


def _cli(
    tmp_path: Path, pending: str, *flags: str, capsys: pytest.CaptureFixture[str]
) -> tuple[int, str, str]:
    p = tmp_path / "pending.txt"
    p.write_text(pending, encoding="utf-8")
    rc = m.main(["--pending", str(p), *flags])
    out = capsys.readouterr()
    return rc, out.out, out.err


def test_cli_unreadable_row_exits_2_with_nothing_on_stdout(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rc, out, err = _cli(
        tmp_path,
        "[l] u-x — branch hygiene close-out pending: feat/u-x",
        "--emit-command",
        capsys=capsys,
    )
    assert (rc, out) == (2, "")
    assert err.startswith("unreadable pending row: ")


def test_cli_mismatch_exits_1_with_nothing_on_stdout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    green_main: None,
) -> None:
    monkeypatch.setattr(m, "pr_view", lambda pr: _merged("x", state="OPEN"))
    rc, out, err = _cli(tmp_path, ROW_A, "--emit-command", capsys=capsys)
    assert (rc, out) == (1, "")
    assert (
        "verification mismatch: feat/u-sr-08-context-noise-deletions PR #1489: state is OPEN" in err
    )


def test_cli_emit_prints_the_review_table_on_stderr_and_the_push_on_stdout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    green_main: None,
) -> None:
    names = {"1489": "feat/u-sr-08-context-noise-deletions", "1490": "roadmap-refresh-post-1489"}
    monkeypatch.setattr(m, "pr_view", lambda pr: _merged(names[pr], "oid" + pr))
    monkeypatch.setattr(m, "remote_absent", lambda branch: False)
    foreign = "[l] r-830 — needs the AWS profile r830 login"
    rc, out, err = _cli(tmp_path, foreign + "\n" + ROW_A, "--emit-command", capsys=capsys)
    assert rc == 0
    assert out == (
        "git push --atomic "
        "--force-with-lease=refs/heads/feat/u-sr-08-context-noise-deletions:oid1489 "
        "--force-with-lease=refs/heads/roadmap-refresh-post-1489:oid1490 "
        "origin :refs/heads/feat/u-sr-08-context-noise-deletions "
        ":refs/heads/roadmap-refresh-post-1489\n"
    )
    assert (
        "feat/u-sr-08-context-noise-deletions oid1489\nroadmap-refresh-post-1489 oid1490\n" in err
    )
    assert "left pending (not a branch-hygiene deferral): " + foreign in err


def test_cli_emit_leaves_already_deleted_branches_out_of_the_lease(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    green_main: None,
) -> None:
    """Witnessed on the first live batch: a merged PR still reports a head OID after its
    branch was deleted, and a lease on an absent ref is rejected — under --atomic, the
    whole push. The absent branch is named on stderr and left to the resolve phase."""
    names = {"1489": "feat/u-sr-08-context-noise-deletions", "1490": "roadmap-refresh-post-1489"}
    monkeypatch.setattr(m, "pr_view", lambda pr: _merged(names[pr], "o" + pr))
    monkeypatch.setattr(m, "remote_absent", lambda branch: branch.startswith("roadmap-refresh"))
    rc, out, err = _cli(tmp_path, ROW_A, "--emit-command", capsys=capsys)
    assert rc == 0
    assert out == (
        "git push --atomic "
        "--force-with-lease=refs/heads/feat/u-sr-08-context-noise-deletions:o1489 "
        "origin :refs/heads/feat/u-sr-08-context-noise-deletions\n"
    )
    assert (
        "already absent on origin (branch-hygiene-resolve clears it): roadmap-refresh-post-1489"
        in err
    )


def test_cli_emit_with_every_branch_already_gone_prints_no_push(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    green_main: None,
) -> None:
    names = {"1489": "feat/u-sr-08-context-noise-deletions", "1490": "roadmap-refresh-post-1489"}
    monkeypatch.setattr(m, "pr_view", lambda pr: _merged(names[pr], "o" + pr))
    monkeypatch.setattr(m, "remote_absent", lambda branch: True)
    rc, out, err = _cli(tmp_path, ROW_A, "--emit-command", capsys=capsys)
    assert (rc, out) == (1, "")
    assert "nothing to push" in err


def test_cli_emit_aborts_when_origin_cannot_be_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    green_main: None,
) -> None:
    names = {"1489": "feat/u-sr-08-context-noise-deletions", "1490": "roadmap-refresh-post-1489"}
    monkeypatch.setattr(m, "pr_view", lambda pr: _merged(names[pr], "o" + pr))

    def _unreachable(branch: str) -> bool:
        raise m.RemoteStateError(f"ls-remote exit 128 for {branch}: could not read from remote")

    monkeypatch.setattr(m, "remote_absent", _unreachable)
    rc, out, err = _cli(tmp_path, ROW_A, "--emit-command", capsys=capsys)
    assert (rc, out) == (1, "")
    assert "ls-remote exit 128" in err


def test_cli_resolve_reports_still_present_and_exits_1(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(m, "remote_absent", lambda branch: branch.startswith("roadmap-refresh"))
    monkeypatch.setattr(m, "loop_resolve", lambda item, note: None)
    rc, out, err = _cli(tmp_path, ROW_A, "--resolve", capsys=capsys)
    assert (rc, out) == (1, "")
    assert (
        "still present: u-sr-08 feat/u-sr-08-context-noise-deletions roadmap-refresh-post-1489"
        in err
    )


def test_cli_nothing_pending_exits_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc, out, err = _cli(tmp_path, "", "--resolve", capsys=capsys)
    assert (rc, out) == (1, "")
    assert "nothing to do" in err


# ── producer / parser parity: both ship-pr carriers emit the ONE shape ────────


@pytest.mark.parametrize("carrier", CARRIERS, ids=lambda p: p.parts[-3])
def test_both_carriers_emit_the_canonical_shape_and_name_both_recipes(carrier: Path) -> None:
    body = carrier.read_text(encoding="utf-8")
    assert CANONICAL_DEFER_SHAPE in body, carrier
    assert "just branch-hygiene-pending" in body and "just branch-hygiene-resolve" in body, carrier
    # the pre-Task-4 bare shape (one branch, no PR pair) is exactly what the parser refuses
    assert 'branch hygiene close-out pending: <branch>"' not in body, carrier


def test_the_canonical_shape_parses_into_the_two_branches_it_names() -> None:
    filled = (
        CANONICAL_DEFER_SHAPE.replace("<branch>", "feat/x")
        .replace("<N>", "7")
        .replace("<merge-sha>", "abc1234")
        .replace("<refresh-N>", "8")
        .replace("<refresh-merge-sha>", "def5678")
    )
    assert parse_pending(f"[l] u-x — {filled}") == [
        Deferral("u-x", [("feat/x", "7"), ("roadmap-refresh-post-7", "8")])
    ]


@pytest.mark.parametrize(
    ("recipe", "flag"),
    [("branch-hygiene-pending", "--emit-command"), ("branch-hygiene-resolve", "--resolve")],
)
def test_recipes_pipe_the_reducer_into_the_matching_phase(recipe: str, flag: str) -> None:
    just = shutil.which("just")
    assert just is not None, "just must be installed: the recipe test resolves it"
    proc = subprocess.run(
        [just, "--dry-run", recipe],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env={**os.environ},
    )
    assert proc.returncode == 0, proc.stderr
    line = proc.stderr
    assert "loop_pending_hil_list |" in line
    assert f"tools/branch_hygiene_batch.py --pending - {flag}" in line
    assert "pipefail" in line
