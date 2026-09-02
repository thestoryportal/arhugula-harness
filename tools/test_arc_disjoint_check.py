"""C-HE-13 §4-5 (U-HE-36): prospective merge-tree check + O3 historical base rate.

Every repo is a scratch ``git init`` on disk — the thing under test is how the tool
reads git's merge-tree output and the reservation store, so a stubbed subprocess would
prove nothing about either parse.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import arc_disjoint_check as adc
import reservations as rs

_ID = ["-c", "user.name=t", "-c", "user.email=t@example.invalid"]


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *_ID, *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def _commit(repo: Path, msg: str, **files: str) -> str:
    for name, body in files.items():
        (repo / name).write_text(body, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", msg)
    return _git(repo, "rev-parse", "HEAD")


FIVE = "l1\nl2\nl3\nl4\nl5\n"


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _commit(repo, "base", **{"a.txt": FIVE, "b.txt": "x\n"})
    return repo


def _branch_edit(repo: Path, branch: str, name: str, body: str, start: str = "main") -> str:
    _git(repo, "checkout", "-q", "-b", branch, start)
    sha = _commit(repo, branch, **{name: body})
    _git(repo, "checkout", "-q", "main")
    return sha


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    r = _init_repo(tmp_path)
    _branch_edit(r, "lane-a", "a.txt", "A1\nl2\nl3\nl4\nl5\n")
    _branch_edit(r, "lane-b", "a.txt", "B1\nl2\nl3\nl4\nl5\n")  # same hunk as lane-a
    _branch_edit(r, "lane-c", "b.txt", "C\n")  # disjoint file
    _branch_edit(r, "lane-d", "a.txt", "l1\nl2\nl3\nl4\nD5\n")  # same file, disjoint hunk
    return r


@pytest.fixture
def qdir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    q = tmp_path / "queue"
    q.mkdir()
    monkeypatch.setattr(rs, "QUEUE_DIR", q)
    return q


# --- merge-tree parse ---------------------------------------------------------------


def test_conflict_set_textual_vs_disjoint(repo: Path) -> None:
    """Plan step 1 verbatim: a textual conflict is non-empty, a disjoint pair is empty."""
    assert adc.conflicts(repo, "lane-a", ["lane-b"]) != []
    assert adc.conflicts(repo, "lane-a", ["lane-c"]) == []


def test_conflict_paths_are_paths_not_messages(repo: Path) -> None:
    """The plan snippet took every non-blank line after the OID; merge-tree also prints
    ``Auto-merging a.txt`` / ``CONFLICT (content): …`` after the path list, and those are
    not paths. Mutation witness: the exact list is the one conflicted file."""
    assert adc.merge_conflicts(repo, "lane-a", "lane-b") == ["a.txt"]
    assert adc.conflicts(repo, "lane-a", ["lane-b"]) == ["lane-b: a.txt"]


def test_same_file_disjoint_hunks_is_not_a_conflict(repo: Path) -> None:
    """File overlap is the 38.7 % UPPER bound; the gate measures hunks, not files."""
    assert adc.merge_conflicts(repo, "lane-a", "lane-d") == []


def test_merge_tree_error_is_not_a_verdict(repo: Path) -> None:
    with pytest.raises(adc.MergeTreeError):
        adc.merge_conflicts(repo, "lane-a", "no-such-ref")


# --- other-lane heads from the reservation store --------------------------------------


def test_other_lane_heads_are_the_non_terminal_siblings(repo: Path, qdir: Path) -> None:
    """C-HE-03 §4: a lane is ``pending`` for its whole build and ``open`` only from drain
    start — both are live heads; ``merged``/``abandoned`` are not; own lane excluded."""
    rs.reserve("arc-pending", lane_id="other-1", branch="lane-b", arc_type="applying")
    rs.reserve("arc-open", lane_id="other-2", branch="lane-c", arc_type="applying")
    rs.transition("arc-open", "open", lane_id="other-2")
    rs.reserve("arc-merged", lane_id="other-3", branch="lane-d", arc_type="applying")
    rs.transition("arc-merged", "open", lane_id="other-3")
    rs.transition("arc-merged", "merged", lane_id="other-3")
    rs.reserve("arc-mine", lane_id="me", branch="lane-a", arc_type="applying")

    heads = adc.other_lane_heads(repo, "me")

    assert [(h.arc_id, h.state, h.ref) for h in heads] == [
        ("arc-open", "open", "refs/heads/lane-c"),
        ("arc-pending", "pending", "refs/heads/lane-b"),
    ]


def test_other_lane_heads_empty_store(repo: Path, qdir: Path) -> None:
    assert adc.other_lane_heads(repo, "me") == []


def test_resolve_ref_local_then_origin_then_none(repo: Path) -> None:
    sha = _git(repo, "rev-parse", "lane-c")
    _git(repo, "update-ref", "refs/remotes/origin/pushed-only", sha)
    assert adc.resolve_ref(repo, "lane-c") == "refs/heads/lane-c"
    assert adc.resolve_ref(repo, "pushed-only") == "refs/remotes/origin/pushed-only"
    assert adc.resolve_ref(repo, "never-created") is None


def test_lane_id_env_then_file_then_incomplete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    f = tmp_path / ".lane-id"
    monkeypatch.setattr(adc, "LANE_ID_FILE", f)
    monkeypatch.setenv("HARNESS_LANE_ID", "from-env")
    assert adc.lane_id() == "from-env"
    monkeypatch.delenv("HARNESS_LANE_ID")
    f.write_text("from-file\n", encoding="utf-8")
    assert adc.lane_id() == "from-file"
    f.unlink()
    with pytest.raises(adc.CheckIncompleteError):
        adc.lane_id()


# --- `check` CLI: exit codes are the contract ------------------------------------------


@pytest.fixture
def cli(repo: Path, qdir: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(adc, "REPO", repo)
    monkeypatch.setenv("HARNESS_LANE_ID", "me")
    return repo


def test_check_exit_0_disjoint(cli: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rs.reserve("arc-c", lane_id="other", branch="lane-c", arc_type="applying")
    assert adc.main(["check", "--candidate", "lane-a"]) == 0
    assert "disjoint: lane-a vs 1 other lane head(s)" in capsys.readouterr().out


def test_check_exit_1_conflict_names_arc_lane_branch_path(
    cli: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rs.reserve("arc-b", lane_id="other", branch="lane-b", arc_type="applying")
    assert adc.main(["check", "--candidate", "lane-a"]) == 1
    assert "CONFLICT arc-b [other] lane-b: a.txt" in capsys.readouterr().out


def test_check_exit_2_unresolvable_head_fails_closed(
    cli: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A sibling whose branch has no ref cannot be merge-tree'd: refuse, never pass."""
    rs.reserve("arc-ghost", lane_id="other", branch="not-yet-created", arc_type="applying")
    rs.reserve("arc-c", lane_id="other-2", branch="lane-c", arc_type="applying")
    assert adc.main(["check", "--candidate", "lane-a"]) == 2
    out = capsys.readouterr().out
    assert "UNRESOLVED arc-ghost [other] pending: branch not-yet-created" in out
    assert "CONFLICT" not in out and "disjoint" not in out


def test_check_exit_2_without_lane_id(
    cli: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("HARNESS_LANE_ID")
    monkeypatch.setattr(adc, "LANE_ID_FILE", tmp_path / "absent")
    assert adc.main(["check"]) == 2
    assert "INCOMPLETE CheckIncompleteError: lane id unknown" in capsys.readouterr().err


def test_check_exit_2_on_a_malformed_sibling_record(
    cli: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Exit 1 is a verdict, so a record the parse cannot read must land on 2, not on
    Python's default exit 1 for an uncaught exception."""
    rs.reserve("arc-x", lane_id="other", branch="lane-c", arc_type="applying")
    gen = rs.reservations_root() / "arc-x" / "1.json"
    gen.write_text('{"state": "pending", "lane_id": "other"}', encoding="utf-8")  # no branch
    assert adc.main(["check", "--candidate", "lane-a"]) == 2
    assert "INCOMPLETE KeyError" in capsys.readouterr().err


def test_check_fetch_failure_is_loud_not_fatal(
    cli: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The scratch repo has no ``origin``: the fetch fails, the WARN lands on stderr, and
    the local-ref check still completes."""
    assert adc.main(["check", "--candidate", "lane-a"]) == 0
    assert "WARN fetch origin failed" in capsys.readouterr().err


# --- O3 historical replay -----------------------------------------------------------


def _linear_history(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    """Squash-merge-shaped main: base -> A(a.txt l1) -> I(a.txt l5) -> B(a.txt l1) -> C(b.txt)."""
    repo = _init_repo(tmp_path)
    shas = {
        "A": _commit(repo, "A", **{"a.txt": "A1\nl2\nl3\nl4\nl5\n"}),
        "I": _commit(repo, "I", **{"a.txt": "A1\nl2\nl3\nl4\nI5\n"}),
        "B": _commit(repo, "B", **{"a.txt": "B1\nl2\nl3\nl4\nI5\n"}),
        "C": _commit(repo, "C", **{"b.txt": "y\n"}),
    }
    return repo, shas


def test_pair_conflicts_replays_later_pr_as_a_concurrent_lane(tmp_path: Path) -> None:
    repo, s = _linear_history(tmp_path)
    with adc.scratch_objects(repo) as env:
        assert adc.pair_conflicts(repo, s["A"], s["B"], env) == ["a.txt"]  # same hunk
        assert adc.pair_conflicts(repo, s["A"], s["I"], env) == []  # same file, other hunk
        assert adc.pair_conflicts(repo, s["A"], s["C"], env) == []  # disjoint file


def test_pair_conflicts_subtracts_intermediate_overlap(tmp_path: Path) -> None:
    """B's tree at A^ carries I's hunk too; I's own overlap with A must not be charged
    to the (A, B) pair. Here I conflicts with A (l1 vs l1) while B only touches b.txt."""
    repo = _init_repo(tmp_path)
    a = _commit(repo, "A", **{"a.txt": "A1\nl2\nl3\nl4\nl5\n"})
    i = _commit(repo, "I", **{"a.txt": "I1\nl2\nl3\nl4\nl5\n"})
    b = _commit(repo, "B", **{"b.txt": "y\n"})
    with adc.scratch_objects(repo) as env:
        assert adc.pair_conflicts(repo, a, i, env) == ["a.txt"]
        assert adc.pair_conflicts(repo, a, b, env) == []


def test_pair_conflicts_excludes_governance_files(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    gov = ".harness/roadmap_status.md"
    (repo / ".harness").mkdir()
    base = _commit(repo, "base2", **{gov: FIVE})
    a = _commit(repo, "A", **{gov: "A1\nl2\nl3\nl4\nl5\n"})
    b = _commit(repo, "B", **{gov: "B1\nl2\nl3\nl4\nl5\n"})
    with adc.scratch_objects(repo) as env:
        assert adc.merge_conflicts(repo, a, adc.synthetic_commit(repo, b, base, env), env) == [gov]
        assert adc.pair_conflicts(repo, a, b, env) == []


def test_scratch_objects_keep_the_repo_store_clean(tmp_path: Path) -> None:
    repo, s = _linear_history(tmp_path)
    objects = repo / ".git" / "objects"
    before = sorted(p for p in objects.rglob("*") if p.is_file())
    with adc.scratch_objects(repo) as env:
        syn = adc.synthetic_commit(repo, s["B"], f"{s['A']}^", env)
        adc.merge_conflicts(repo, s["A"], syn, env)
    after = sorted(p for p in objects.rglob("*") if p.is_file())
    assert after == before
    assert (
        subprocess.run(
            ["git", "-C", str(repo), "cat-file", "-e", syn], check=False, capture_output=True
        ).returncode
        != 0
    )


def test_window_pairs_four_lane_window_with_governance_exclusion() -> None:
    gov = ".harness/roadmap_status.md"
    prs = [
        adc.MergedPr(1, "s1", frozenset({"x.py", gov})),
        adc.MergedPr(2, "s2", frozenset({gov})),  # collides with 1 only via governance
        adc.MergedPr(3, "s3", frozenset({"y.py"})),
        adc.MergedPr(4, "s4", frozenset({"x.py"})),  # in 1's window (i+3)
        adc.MergedPr(5, "s5", frozenset({"x.py"})),  # outside 1's window
    ]
    pairs = adc.window_pairs(prs)
    assert [(a.number, b.number) for a, b in pairs] == [(1, 4), (4, 5)]


def test_pairs_file_round_trip(tmp_path: Path) -> None:
    prs = [adc.MergedPr(1, "a" * 40, frozenset({"x"})), adc.MergedPr(2, "b" * 40, frozenset({"x"}))]
    out = tmp_path / "pairs.txt"
    adc.write_pairs(out, prs, adc.window_pairs(prs))
    text = out.read_text(encoding="utf-8")
    assert "# window-pairs: 1\n# pairs: 1\n" in text
    assert text.endswith(f"{'a' * 40} {'b' * 40} #1 #2\n")
    assert adc.read_pairs(out) == adc.PairList(1, [("a" * 40, "b" * 40)])


def test_window_pair_count_matches_p_r3() -> None:
    assert adc.window_pair_count(150) == 444  # P-R3 §2: 4-lane window over 150 PRs
    assert adc.window_pair_count(2) == 1 and adc.window_pair_count(1) == 0


def test_read_pairs_refuses_a_file_without_the_denominator(tmp_path: Path) -> None:
    f = tmp_path / "pairs.txt"
    f.write_text(f"# pairs: 1\n{'a' * 40} {'b' * 40}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="window-pairs"):
        adc.read_pairs(f)


def test_historical_reports_rate_and_unmeasured_semantic_line(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, s = _linear_history(tmp_path)
    pairs = tmp_path / "pairs.txt"
    pairs.write_text(f"# window-pairs: 5\n{s['A']} {s['B']}\n{s['A']} {s['C']}\n", encoding="utf-8")
    assert adc.historical(repo, pairs) == 0
    out = capsys.readouterr().out
    assert f"conflict {s['A'][:12]} {s['B'][:12]}: a.txt" in out
    assert (
        "O3: textual-conflict rate 1/5 = 0.200 of window pairs "
        "(file-overlap upper bound 0.387 = 2/5); conditional on file overlap 1/2 = 0.500"
    ) in out
    assert "semantic-conflict rate: unmeasured" in out


def test_committed_pair_list_has_the_172_p_r3_pairs() -> None:
    """The derived artifact is the P-R3 measurement re-run: 172 colliding 4-lane-window
    pairs over #1239..#1391 after the four-file governance exclusion."""
    pl = adc.read_pairs(adc.O3_PAIRS)
    assert pl.window_pairs == 444 and len(pl.pairs) == 172  # 172/444 = the 38.7 % bound
    assert all(len(a) == 40 and len(b) == 40 for a, b in pl.pairs)


# --- carriers -----------------------------------------------------------------------


def test_manifest_registers_the_c_he_13_row() -> None:
    import lanes_verify as lv

    assert (
        lv.Row("C-HE-13", "pytest:tools/test_arc_disjoint_check.py", "phase1", "local + CI", False)
        in lv.MANIFEST
    )
