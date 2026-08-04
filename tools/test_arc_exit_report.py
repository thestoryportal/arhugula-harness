"""Hermetic tests for tools/arc_exit_report.py (U-WT-03). Zero network, zero real `gh`.

The collect layer's single external-call primitive (`arc_exit_report.run`) is monkeypatched
wholesale with a scenario-driven fake, so every `gh`/`git` shape the tool depends on is
asserted here as a contract rather than exercised live. Three scenarios mirror the plan's
fixtures — clean close / CI-not-green / no-refresh-owed — plus a `gh`-absent degradation
case. The one test that does NOT fake anything is the ledger-row byte-format test: it runs
the real `loop_lib.sh` `loop_log` against a throwaway repo copy and parses the row back
using the same pipe-escape rules, because a Python-side copy of that format is exactly what
the shim exists to avoid.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import arc_exit_report as aer

MERGE = "995517e5990bf6d05069501a784b4d43ebcdf168"
REFRESH = "f7285f65344116c82a8ed92a74a7b0a5594df0b6"
OTHER = "aaaaaaaa1111111111111111111111111111aaaa"
MERGE_TS = 1_754_000_000


def scenario(**over):
    """Default = the clean-close fixture; keyword args override one facet at a time."""
    base = {
        "toplevel": None,  # filled in by make_run
        "gh_absent": False,
        "pr_view": {"state": "MERGED", "mergeCommit": {"oid": MERGE}},
        "runs": [
            {
                "conclusion": "success",
                "status": "completed",
                "url": "https://github.com/o/r/actions/runs/1",
                "workflowName": "CI",
            }
        ],
        "commits": {MERGE, REFRESH, OTHER},
        "log": [(REFRESH, "ops: roadmap status refresh post-#1202 (#1203)")],
        "files": {REFRESH: [".harness/roadmap_status.md"]},
        "merge_ts": str(MERGE_TS),
        "todos": "",
        "todos_rc": 0,
    }
    base.update(over)
    return base


def make_run(sc, toplevel: Path):
    """A fake `arc_exit_report.run` — every command shape the tool actually issues."""
    calls: list[list[str]] = []

    def fake(cmd, cwd, timeout=20):
        calls.append(list(cmd))
        if cmd[0] == "gh":
            if sc["gh_absent"]:
                return 127, ""
            if cmd[1] == "pr":
                return (0, json.dumps(sc["pr_view"])) if sc["pr_view"] is not None else (1, "")
            if cmd[1] == "run":
                return (0, json.dumps(sc["runs"])) if sc["runs"] is not None else (1, "")
            return 1, ""
        if cmd[0] == "git":
            if cmd[1] == "rev-parse" and "--show-toplevel" in cmd:
                return 0, str(toplevel)
            if cmd[1] == "rev-parse":
                want = cmd[-1].replace("^{commit}", "")
                for full in sc["commits"]:
                    if full.startswith(want) or want in ("origin/main", "HEAD", "main"):
                        return (0, full if full.startswith(want) else MERGE)
                return 1, ""
            if cmd[1] == "symbolic-ref":
                return 0, "origin/main"
            if cmd[1] == "log":
                return 0, "\n".join(f"{s}\t{m}" for s, m in sc["log"])
            if cmd[1] == "show" and "--name-only" in cmd:
                return 0, "\n".join(sc["files"].get(cmd[-1], []))
            if cmd[1] == "show" and "-s" in cmd:
                return 0, sc["merge_ts"]
            if cmd[1] == "remote":
                return 0, "https://github.com/thestoryportal/arhugula-harness.git"
            return 1, ""
        if cmd[0] == "bash":
            return sc["todos_rc"], sc["todos"]
        return 1, ""

    fake.calls = calls
    return fake


@pytest.fixture
def repo(tmp_path):
    """A throwaway 'repo' with the two hook libs the shim sources, and a checkpoints dir."""
    root = tmp_path / "repo"
    (root / "tools" / "hooks").mkdir(parents=True)
    (root / ".harness").mkdir()
    real = Path(__file__).resolve().parent / "hooks"
    for name in ("lib.sh", "loop_lib.sh"):
        shutil.copy(real / name, root / "tools" / "hooks" / name)
    return root


@pytest.fixture
def gstack(tmp_path):
    """A fake ~/.gstack/projects tree whose newest checkpoint post-dates the merge."""
    d = tmp_path / "gstack" / "repo" / "checkpoints"
    d.mkdir(parents=True)
    old = d / "20260801-000000-older.md"
    new = d / "20260803-210500-final.md"
    old.write_text("old", encoding="utf-8")
    new.write_text("new", encoding="utf-8")
    import os

    os.utime(old, (MERGE_TS - 500, MERGE_TS - 500))
    os.utime(new, (MERGE_TS + 500, MERGE_TS + 500))
    return tmp_path / "gstack"


def collect_with(sc, repo, gstack, monkeypatch, pr=1202, merge_sha=MERGE):
    monkeypatch.setattr(aer, "run", make_run(sc, repo))
    return aer.collect(pr, merge_sha, repo, gstack_root=gstack)


def yaml_block(text: str) -> str:
    m = re.search(r"```yaml\n(.*?)\n```", text, re.DOTALL)
    assert m, f"no fenced yaml block in:\n{text}"
    return m.group(1)


# --- AC1: the rendered yaml block round-trips through yaml.safe_load -------------------


@pytest.mark.parametrize(
    "sc",
    [
        scenario(),
        scenario(
            runs=[
                {"conclusion": "failure", "status": "completed", "url": "u", "workflowName": "CI"}
            ]
        ),
        scenario(log=[], files={}),
    ],
    ids=["clean-close", "ci-not-green", "no-refresh-owed"],
)
def test_ac1_yaml_block_round_trips(sc, repo, gstack, monkeypatch):
    data = collect_with(sc, repo, gstack, monkeypatch)
    loaded = yaml.safe_load(yaml_block(aer.render(data)))
    assert isinstance(loaded, dict)
    assert set(loaded) == set(aer.YAML_FIELDS), (
        "the yaml block must carry EXACTLY the contract fields"
    )
    assert loaded["pr"] == 1202 and isinstance(loaded["pr"], int)
    assert set(loaded["main_ci"]) == {"commit", "conclusion", "run_url"}
    assert set(loaded["checkpoint"]) == {"path", "confirmed"}
    assert isinstance(loaded["todo_for_human"], list)


def test_ac1_notes_never_leak_into_the_machine_block(repo, gstack, monkeypatch):
    """`notes` is prose-tail-only — a degradation note must not become a yaml field."""
    data = collect_with(scenario(gh_absent=True), repo, gstack, monkeypatch)
    assert data["notes"], "gh-absent must record notes"
    text = aer.render(data)
    assert "notes" not in yaml.safe_load(yaml_block(text))
    assert data["notes"][0] in text, "notes belong in the human prose tail"


# --- AC2: a missing refresh is null, NEVER fabricated ----------------------------------


def test_ac2_no_refresh_renders_null_and_never_borrows_a_sha(repo, gstack, monkeypatch):
    data = collect_with(scenario(log=[], files={}), repo, gstack, monkeypatch)
    assert data["refresh_commit"] is None
    block = yaml_block(aer.render(data))
    assert "refresh_commit: null" in block
    loaded = yaml.safe_load(block)
    assert loaded["refresh_commit"] is None
    # The strong form: no OTHER known sha may be substituted in its place.
    assert MERGE not in block.split("refresh_commit")[1].split("\n")[0]
    assert REFRESH not in block


def test_ac2_refresh_titled_but_multifile_commit_is_not_reported(repo, gstack, monkeypatch):
    """§12.2.1 requires BOTH the title prefix and a changed set of exactly
    roadmap_status.md — a bundled commit carrying the prefix is not a terminating refresh
    and must not be reported as one."""
    sc = scenario(
        log=[(OTHER, "ops: roadmap status refresh post-#9 (#10)")],
        files={OTHER: [".harness/roadmap_status.md", "tools/other.py"]},
    )
    data = collect_with(sc, repo, gstack, monkeypatch)
    assert data["refresh_commit"] is None
    assert any("not a" in n and "terminating refresh" in n for n in data["notes"])


def test_ac2_verified_refresh_is_reported(repo, gstack, monkeypatch):
    data = collect_with(scenario(), repo, gstack, monkeypatch)
    assert data["refresh_commit"] == REFRESH


# --- AC3: a non-success CI conclusion is reported VERBATIM ------------------------------


@pytest.mark.parametrize("concl", ["failure", "cancelled", "timed_out", "action_required"])
def test_ac3_non_success_conclusion_verbatim(concl, repo, gstack, monkeypatch):
    sc = scenario(
        runs=[{"conclusion": concl, "status": "completed", "url": "u", "workflowName": "CI"}]
    )
    data = collect_with(sc, repo, gstack, monkeypatch)
    assert data["main_ci"]["conclusion"] == concl
    assert yaml.safe_load(yaml_block(aer.render(data)))["main_ci"]["conclusion"] == concl


def test_ac3_pending_run_stays_null_not_coerced(repo, gstack, monkeypatch):
    sc = scenario(
        runs=[{"conclusion": None, "status": "in_progress", "url": "u", "workflowName": "CI"}]
    )
    data = collect_with(sc, repo, gstack, monkeypatch)
    assert data["main_ci"]["conclusion"] is None
    assert "conclusion: null" in yaml_block(aer.render(data))


def test_ac3_one_red_run_is_not_masked_by_a_green_sibling(repo, gstack, monkeypatch):
    sc = scenario(
        runs=[
            {"conclusion": "success", "status": "completed", "url": "g", "workflowName": "Docs"},
            {"conclusion": "failure", "status": "completed", "url": "r", "workflowName": "CI"},
        ]
    )
    data = collect_with(sc, repo, gstack, monkeypatch)
    assert data["main_ci"]["conclusion"] == "failure"
    assert data["main_ci"]["run_url"] == "r"


# --- AC4: todo_for_human is PRESENT even when empty -------------------------------------


def test_ac4_empty_todo_list_present_not_omitted(repo, gstack, monkeypatch):
    data = collect_with(scenario(todos=""), repo, gstack, monkeypatch)
    assert data["todo_for_human"] == []
    block = yaml_block(aer.render(data))
    assert "todo_for_human: []" in block
    loaded = yaml.safe_load(block)
    assert "todo_for_human" in loaded and loaded["todo_for_human"] == []


def test_ac4_populated_todos_carry_full_rows(repo, gstack, monkeypatch):
    sc = scenario(todos="R-410 — needs container runtime\nB-48 — needs an executor pick")
    data = collect_with(sc, repo, gstack, monkeypatch)
    loaded = yaml.safe_load(yaml_block(aer.render(data)))
    assert loaded["todo_for_human"] == [
        "R-410 — needs container runtime",
        "B-48 — needs an executor pick",
    ]


def test_ac4_todo_collection_failure_degrades_to_empty_with_a_note(repo, gstack, monkeypatch):
    data = collect_with(scenario(todos_rc=3, todos=""), repo, gstack, monkeypatch)
    assert data["todo_for_human"] == []
    assert any("loop_pending_hil_list" in n for n in data["notes"])


# --- AC5: idempotent per-PR re-run ------------------------------------------------------


def test_ac5_rerun_overwrites_the_same_file(repo, gstack, monkeypatch):
    monkeypatch.setattr(aer, "GSTACK_PROJECTS", gstack)
    monkeypatch.setattr(aer, "run", make_run(scenario(), repo))
    assert aer.main(["--pr", "1202", "--merge-sha", MERGE, "--repo-root", str(repo)]) == 0
    first = aer.report_path(repo, 1202).read_text(encoding="utf-8")

    sc2 = scenario(
        runs=[{"conclusion": "failure", "status": "completed", "url": "u", "workflowName": "CI"}]
    )
    monkeypatch.setattr(aer, "run", make_run(sc2, repo))
    assert aer.main(["--pr", "1202", "--merge-sha", MERGE, "--repo-root", str(repo)]) == 0

    written = sorted((repo / aer.REPORT_DIR).glob("arc-exit-report-pr*.md"))
    assert [p.name for p in written] == ["arc-exit-report-pr1202.md"], "PR-keyed: no dated sibling"
    second = written[0].read_text(encoding="utf-8")
    assert first != second and "conclusion: failure" in second, "re-run overwrites with fresh facts"


def test_ac5_filename_is_pr_keyed_and_date_free():
    p = aer.report_path(Path("/x"), 77)
    assert p.name == "arc-exit-report-pr77.md"
    assert not re.search(r"\d{4}-?\d{2}-?\d{2}", p.name)


# --- gh-absent degradation --------------------------------------------------------------


def test_gh_absent_degrades_with_nulls_and_notes_never_crashes(repo, gstack, monkeypatch):
    data = collect_with(scenario(gh_absent=True), repo, gstack, monkeypatch, merge_sha=None)
    assert data["merge_state"] is None
    assert data["merge_commit"] is None
    assert data["main_ci"] == {"commit": None, "conclusion": None, "run_url": None}
    assert data["refresh_commit"] is None
    assert data["checkpoint"]["confirmed"] is False, "unknown merge time must NOT be assumed"
    assert any("not installed" in n for n in data["notes"])
    loaded = yaml.safe_load(yaml_block(aer.render(data)))
    assert set(loaded) == set(aer.YAML_FIELDS)


def test_gh_absent_but_merge_sha_supplied_still_resolves_git_side_fields(repo, gstack, monkeypatch):
    data = collect_with(scenario(gh_absent=True), repo, gstack, monkeypatch)
    assert data["merge_commit"] == MERGE
    assert data["refresh_commit"] == REFRESH, "git-side collection is independent of gh"
    assert data["main_ci"]["conclusion"] is None


# --- checkpoint honesty -----------------------------------------------------------------


def test_checkpoint_picks_the_newest_and_confirms_against_the_merge_time(repo, gstack, monkeypatch):
    data = collect_with(scenario(), repo, gstack, monkeypatch)
    assert data["checkpoint"]["path"].endswith("20260803-210500-final.md")
    assert data["checkpoint"]["confirmed"] is True


def test_checkpoint_before_the_merge_is_not_confirmed(repo, gstack, monkeypatch):
    data = collect_with(scenario(merge_ts=str(MERGE_TS + 10_000)), repo, gstack, monkeypatch)
    assert data["checkpoint"]["confirmed"] is False


def test_checkpoint_absent_is_null_and_false(repo, tmp_path, monkeypatch):
    data = collect_with(scenario(), repo, tmp_path / "no-gstack", monkeypatch)
    assert data["checkpoint"] == {"path": None, "confirmed": False}
    assert "checkpoint:\n  path: null\n  confirmed: false" in yaml_block(aer.render(data))


# --- exit codes -------------------------------------------------------------------------


def test_exit_2_when_not_a_git_repo(repo, tmp_path, monkeypatch):
    monkeypatch.setattr(aer, "run", lambda cmd, cwd, timeout=20: (128, ""))
    assert aer.main(["--pr", "1", "--repo-root", str(tmp_path)]) == 2


def test_exit_2_on_unresolvable_merge_sha(repo, gstack, monkeypatch):
    monkeypatch.setattr(aer, "run", make_run(scenario(commits=set()), repo))
    assert aer.main(["--pr", "1", "--merge-sha", "deadbeef", "--repo-root", str(repo)]) == 2


def test_exit_2_on_nonpositive_pr(repo, monkeypatch):
    monkeypatch.setattr(aer, "run", make_run(scenario(), repo))
    assert aer.main(["--pr", "0", "--repo-root", str(repo)]) == 2


# --- ledger index row (real loop_log, real byte-format) ---------------------------------

ROW = re.compile(r"^\| (?P<ts>[^|]+) \| (?P<kind>[^|]+) \| (?P<detail>.*) \|$")


def unescape(detail: str) -> str:
    """Inverse of loop_log's `sed 's/|/\\|/g'` pipe escaping."""
    return detail.replace("\\|", "|")


def test_ledger_row_byte_format_via_the_real_loop_log(repo, gstack, monkeypatch):
    data = collect_with(scenario(todos="R-410 — needs runtime"), repo, gstack, monkeypatch)
    monkeypatch.undo()  # the ledger append must use the REAL subprocess runner
    rel = f"{aer.REPORT_DIR}/arc-exit-report-pr1202.md"
    assert aer.append_ledger_row(repo, data, rel) is True

    lines = (repo / aer.LEDGER_REL).read_text(encoding="utf-8").splitlines()
    rows = [ROW.match(ln) for ln in lines if ln.startswith("| ") and " | EXIT-REPORT | " in ln]
    assert len(rows) == 1, f"expected exactly one EXIT-REPORT row, got {len(rows)}"
    m = rows[0]
    assert m.group("kind") == "EXIT-REPORT"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", m.group("ts"))
    detail = unescape(m.group("detail"))
    assert detail == (f"pr=#1202 ci={MERGE[:8]}:success refresh={REFRESH[:8]} todos=1 path={rel}")


def test_ledger_row_marks_a_missing_refresh_as_none(repo, gstack, monkeypatch):
    data = collect_with(scenario(log=[], files={}, todos=""), repo, gstack, monkeypatch)
    monkeypatch.undo()
    assert aer.append_ledger_row(repo, data, "p.md") is True
    text = (repo / aer.LEDGER_REL).read_text(encoding="utf-8")
    assert "refresh=none todos=0" in text
    assert REFRESH[:8] not in text


def test_ledger_row_pipes_are_escaped_so_one_row_stays_one_row(repo, gstack, monkeypatch):
    data = collect_with(scenario(), repo, gstack, monkeypatch)
    monkeypatch.undo()
    assert aer.append_ledger_row(repo, data, "a|b.md") is True
    line = next(
        ln
        for ln in (repo / aer.LEDGER_REL).read_text(encoding="utf-8").splitlines()
        if "EXIT-REPORT" in ln
    )
    assert r"path=a\|b.md" in line
    assert unescape(ROW.match(line).group("detail")).endswith("path=a|b.md")


def test_ledger_failure_never_breaks_the_caller(tmp_path, gstack, monkeypatch, repo):
    """A repo without the hook libs must degrade to a warning, not an exception or a
    nonzero exit — the report file is the deliverable, the index row is a convenience."""
    bare = tmp_path / "bare"
    (bare / ".harness").mkdir(parents=True)
    data = collect_with(scenario(), repo, gstack, monkeypatch)
    monkeypatch.undo()
    assert aer.append_ledger_row(bare, data, "p.md") is False


def test_main_still_exits_0_when_the_ledger_row_cannot_be_written(tmp_path, gstack, monkeypatch):
    """Full path: hook libs absent → warning on stderr, report still written, exit 0."""
    root = tmp_path / "noledger"
    root.mkdir()
    monkeypatch.setattr(aer, "GSTACK_PROJECTS", gstack)
    monkeypatch.setattr(aer, "run", make_run(scenario(), root))
    assert aer.main(["--pr", "5", "--merge-sha", MERGE, "--repo-root", str(root)]) == 0
    assert aer.report_path(root, 5).is_file()


# --- render purity ----------------------------------------------------------------------


def test_render_is_pure_no_subprocess(monkeypatch):
    def explode(*a, **k):
        raise AssertionError("render must not shell out")

    monkeypatch.setattr(aer, "run", explode)
    data = {
        "pr": 9,
        "merge_state": "MERGED",
        "merge_commit": MERGE,
        "main_ci": {"commit": MERGE, "conclusion": "success", "run_url": "u"},
        "refresh_commit": None,
        "checkpoint": {"path": None, "confirmed": False},
        "todo_for_human": [],
        "notes": [],
    }
    first = aer.render(data)
    assert first == aer.render(data), "render must be deterministic (no clock, no randomness)"
    assert yaml.safe_load(yaml_block(first))["merge_state"] == "MERGED"
