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
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import arc_exit_report as aer

MERGE = "995517e5990bf6d05069501a784b4d43ebcdf168"
REFRESH = "f7285f65344116c82a8ed92a74a7b0a5594df0b6"
OTHER = "aaaaaaaa1111111111111111111111111111aaaa"
LATER = "bbbbbbbb2222222222222222222222222222bbbb"
MERGE_TS = 1_754_000_000
# The terminating refresh lands AFTER the merge — the window between them is exactly where
# a not-yet-final checkpoint can be written (codex round-3 P1 finding 2).
REFRESH_TS = MERGE_TS + 1_000


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
        "commits": {MERGE, REFRESH, OTHER, LATER},
        # First-parent history AFTER the merge, oldest first: (sha, parents, subject). The
        # PARENTS column is load-bearing — only the merge's immediate first-parent successor
        # may be bound as this arc's refresh (codex round-4 P1).
        "log": [(REFRESH, MERGE, "ops: roadmap status refresh post-#1202 (#1203)")],
        "files": {REFRESH: [".harness/roadmap_status.md"]},
        # Per-commit committer times — the anchor for checkpoint.confirmed is the REFRESH
        # commit when one is verified, the merge otherwise.
        "ts": {MERGE: str(MERGE_TS), REFRESH: str(REFRESH_TS), OTHER: str(REFRESH_TS)},
        # `git rev-parse --git-common-dir`. A MAIN checkout answers the relative ".git"; a
        # linked worktree answers an absolute path inside the main checkout's .git, which is
        # what redirects the write location (codex round-6 P1). (rc, stdout).
        "common_dir": (0, ".git"),
        "todos": "",
        "todos_rc": 0,
    }
    base.update(over)
    return base


_REAL_RUN = aer.run  # captured before any monkeypatching, for the real-bash fixtures


def make_run(sc, toplevel: Path, real_bash: bool = False):
    """A fake `arc_exit_report.run` — every command shape the tool actually issues.

    `real_bash=True` lets the `loop_lib.sh` shims run for real (the ledger append + the
    pending-HIL read), which is what makes the round-6 root-resolution tests witness where
    the artifacts ACTUALLY land rather than only where the code says it would write.
    """
    calls: list[list[str]] = []

    def fake(cmd, cwd, timeout=20):
        calls.append(list(cmd))
        if cmd[0] == "gh":
            if sc["gh_absent"]:
                return 127, ""
            if cmd[1] == "pr":
                return (0, json.dumps(sc["pr_view"])) if sc["pr_view"] is not None else (1, "")
            if cmd[1] == "run":
                if sc["runs"] is None:
                    return 1, ""
                # Honour the SERVER-SIDE filters the tool passes. Dropping `--branch`/
                # `--event` from the argv therefore changes what comes back, which is what
                # makes the dispatch-only case a real discriminator (codex round-4 P2).
                rows = sc["runs"]
                filters = (("--event", "event", "push"), ("--branch", "branch", "main"))
                for flag, field, default in filters:
                    if flag in cmd:
                        want = cmd[cmd.index(flag) + 1]
                        rows = [r for r in rows if r.get(field, default) == want]
                return 0, json.dumps(rows)
            return 1, ""
        if cmd[0] == "git":
            if cmd[1] == "rev-parse" and "--show-toplevel" in cmd:
                return 0, str(toplevel)
            if cmd[1] == "rev-parse" and "--git-common-dir" in cmd:
                return sc["common_dir"]
            if cmd[1] == "rev-parse":
                want = cmd[-1].replace("^{commit}", "")
                for full in sc["commits"]:
                    if full.startswith(want) or want in ("origin/main", "HEAD", "main"):
                        return (0, full if full.startswith(want) else MERGE)
                return 1, ""
            if cmd[1] == "symbolic-ref":
                return 0, "origin/main"
            if cmd[1] == "log":
                return 0, "\n".join(f"{s}\t{p}\t{m}" for s, p, m in sc["log"])
            if cmd[1] == "show" and "--name-only" in cmd:
                # A files value of None means the QUERY ITSELF fails (rc != 0) — distinct
                # from "no files changed" ([]), so `_refresh_shape_ok`'s could-not-verify
                # branch is reachable from a fixture (merge-gate lens-3 item 6).
                entry = sc["files"].get(cmd[-1], [])
                if entry is None:
                    return 128, ""
                return 0, "\n".join(entry)
            if cmd[1] == "show" and "-s" in cmd:
                ts = sc["ts"].get(cmd[-1])
                return (0, ts) if ts is not None else (128, "")
            if cmd[1] == "remote":
                return 0, "https://github.com/thestoryportal/arhugula-harness.git"
            return 1, ""
        if cmd[0] == "bash":
            if real_bash:
                return _REAL_RUN(cmd, cwd)
            return sc["todos_rc"], sc["todos"]
        return 1, ""

    fake.calls = calls
    return fake


def mk_repo(root: Path) -> Path:
    """A throwaway 'repo' with the two hook libs the shim sources, and a .harness dir."""
    (root / "tools" / "hooks").mkdir(parents=True, exist_ok=True)
    (root / ".harness").mkdir(exist_ok=True)
    real = Path(__file__).resolve().parent / "hooks"
    for name in ("lib.sh", "loop_lib.sh"):
        shutil.copy(real / name, root / "tools" / "hooks" / name)
    return root


@pytest.fixture(autouse=True)
def shared_ledger(tmp_path):
    """Pin the SHARED loop ledger (C-HE-09 §2) into tmp_path for every test.

    Since U-HE-29 the ledger is worktree-independent -- `loop_status_path` resolves it
    from `HARNESS_LOOP_STATUS_PATH` / `ARC_METRICS_QUEUE_DIR`, NOT from the repo root a
    test builds. Without this pin the real `loop_lib.sh` copied into each fake repo would
    resolve the OPERATOR's live ledger and these tests would read (and grow) it.

    Deliberately NOT `monkeypatch.setenv`: several tests below call `monkeypatch.undo()`
    mid-test to drop their `run` stub, and `monkeypatch` is one function-scoped instance
    shared with this fixture — an undo() would silently unpin the venue mid-test and point
    the very next real subprocess at the operator's ledger.
    """
    p = tmp_path / "shared" / "loop_status.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    prev = os.environ.get("HARNESS_LOOP_STATUS_PATH")
    os.environ["HARNESS_LOOP_STATUS_PATH"] = str(p)
    try:
        yield p
    finally:
        if prev is None:
            os.environ.pop("HARNESS_LOOP_STATUS_PATH", None)
        else:
            os.environ["HARNESS_LOOP_STATUS_PATH"] = prev


@pytest.fixture
def repo(tmp_path):
    return mk_repo(tmp_path / "repo")


@pytest.fixture
def gstack(tmp_path):
    """A fake ~/.gstack/projects tree whose newest checkpoint post-dates BOTH commits —
    so any `confirmed: false` in an unbound run is attributable to the binding rule, never
    to the timestamps."""
    d = tmp_path / "gstack" / "repo" / "checkpoints"
    d.mkdir(parents=True)
    old = d / "20260801-000000-older.md"
    new = d / "20260803-210500-final.md"
    old.write_text("old", encoding="utf-8")
    new.write_text("new", encoding="utf-8")
    os.utime(old, (MERGE_TS - 500, MERGE_TS - 500))
    os.utime(new, (REFRESH_TS + 500, REFRESH_TS + 500))
    return tmp_path / "gstack"


def mk_ckpt(tmp_path, mtime: int, name: str = "bound.md") -> Path:
    """A checkpoint file at a controlled mtime, standing in for the one this arc's own
    `/context-save` step reported."""
    p = tmp_path / name
    p.write_text("bound checkpoint", encoding="utf-8")
    os.utime(p, (mtime, mtime))
    return p


def collect_with(sc, repo, gstack, monkeypatch, pr=1202, merge_sha=MERGE, checkpoint=None):
    monkeypatch.setattr(aer, "run", make_run(sc, repo))
    return aer.collect(pr, merge_sha, repo, gstack_root=gstack, checkpoint=checkpoint)


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
        log=[(OTHER, MERGE, "ops: roadmap status refresh post-#9 (#10)")],
        files={OTHER: [".harness/roadmap_status.md", "tools/other.py"]},
    )
    data = collect_with(sc, repo, gstack, monkeypatch)
    assert data["refresh_commit"] is None
    assert any("not a" in n and "terminating refresh" in n for n in data["notes"])


def test_ac2_verified_refresh_is_reported(repo, gstack, monkeypatch):
    data = collect_with(scenario(), repo, gstack, monkeypatch)
    assert data["refresh_commit"] == REFRESH


# --- ROUND-4 FINDING 1: the refresh is bound by POSITION, not merely by shape -----------
# Both ship-pr carriers require the refresh to land as the IMMEDIATE next commit. A
# shape-only scan of the whole history binds a LATER arc's refresh when this arc's is
# missing — and, because `_checkpoint` anchors on the refresh, mis-anchors confirmation too.


def test_r4f1_immediate_successor_matching_the_shape_is_bound(repo, gstack, monkeypatch):
    """(a) the green path: the refresh IS the merge's immediate first-parent successor."""
    sc = scenario(log=[(REFRESH, MERGE, "ops: roadmap status refresh post-#1202 (#1203)")])
    data = collect_with(sc, repo, gstack, monkeypatch)
    assert data["refresh_commit"] == REFRESH
    assert not any("not this arc's refresh" in n for n in data["notes"])


def test_r4f1_later_arcs_refresh_is_never_bound(repo, gstack, monkeypatch):
    """(b) THE round-4 defect: this arc's refresh is missing, a LATER arc lands its own
    perfectly-shaped one-file refresh. A whole-history shape scan binds it; the positional
    rule must report null + name what it found."""
    sc = scenario(
        log=[
            (OTHER, MERGE, "feat(x): a substantive commit that is NOT a refresh"),
            (LATER, OTHER, "ops: roadmap status refresh post-#1300 (#1301)"),
        ],
        files={OTHER: ["tools/x.py"], LATER: [".harness/roadmap_status.md"]},
    )
    data = collect_with(sc, repo, gstack, monkeypatch)
    assert data["refresh_commit"] is None, "a later arc's refresh must never be bound here"
    assert any("immediate successor" in n and "not a refresh commit" in n for n in data["notes"])
    assert any(
        "a later refresh-shaped commit exists" in n and "not this arc's refresh" in n
        for n in data["notes"]
    )


def test_r4f1_later_refresh_does_not_leak_into_the_checkpoint_anchor(
    repo, gstack, tmp_path, monkeypatch
):
    """The mis-binding's second-order harm: a later arc's refresh would move the anchor and
    wrongly REJECT (or accept) this arc's checkpoint. With refresh null, the merge anchors."""
    sc = scenario(
        log=[
            (OTHER, MERGE, "feat(x): substantive"),
            (LATER, OTHER, "ops: roadmap status refresh post-#1300 (#1301)"),
        ],
        files={OTHER: ["tools/x.py"], LATER: [".harness/roadmap_status.md"]},
        ts={MERGE: str(MERGE_TS), OTHER: str(REFRESH_TS), LATER: str(REFRESH_TS + 5_000)},
    )
    bound = mk_ckpt(tmp_path, MERGE_TS + 1)  # after THIS merge, before the later arc's refresh
    data = collect_with(sc, repo, gstack, monkeypatch, checkpoint=bound)
    assert data["refresh_commit"] is None
    assert data["checkpoint"]["confirmed"] is True, "merge is the anchor when no refresh is bound"


def test_r4f1_merge_is_tip_reports_null(repo, gstack, monkeypatch):
    """(c) nothing after the merge yet."""
    data = collect_with(scenario(log=[]), repo, gstack, monkeypatch)
    assert data["refresh_commit"] is None
    assert any("the merge is the tip" in n for n in data["notes"])


def test_r4f1_successor_not_first_parent_child_of_the_merge_is_not_bound(repo, gstack, monkeypatch):
    """Non-linear history: the oldest commit after the merge does not descend from it on
    the first-parent chain — refuse rather than bind by position alone."""
    sc = scenario(log=[(REFRESH, OTHER, "ops: roadmap status refresh post-#1202 (#1203)")])
    data = collect_with(sc, repo, gstack, monkeypatch)
    assert data["refresh_commit"] is None
    assert any("first-parent chain" in n for n in data["notes"])


def test_r4f1_later_refresh_titled_but_multifile_does_not_earn_the_later_note(
    repo, gstack, monkeypatch
):
    """The 'a later refresh-shaped commit exists' note is itself shape-verified — a
    refresh-TITLED bundled commit later on is not 'refresh-shaped'."""
    sc = scenario(
        log=[
            (OTHER, MERGE, "feat(x): substantive"),
            (LATER, OTHER, "ops: roadmap status refresh post-#1300 (#1301)"),
        ],
        files={OTHER: ["tools/x.py"], LATER: [".harness/roadmap_status.md", "tools/y.py"]},
    )
    data = collect_with(sc, repo, gstack, monkeypatch)
    assert data["refresh_commit"] is None
    assert not any("a later refresh-shaped commit exists" in n for n in data["notes"])


def test_r4f1_scan_is_first_parent_only(repo, gstack, monkeypatch):
    """The git query must walk the FIRST-PARENT chain — a full walk re-admits merged-in
    side-branch commits as 'the immediate successor'."""
    sc = scenario()
    fake = make_run(sc, repo)
    monkeypatch.setattr(aer, "run", fake)
    aer.collect(1202, MERGE, repo, gstack_root=gstack)
    log_calls = [c for c in fake.calls if c[:2] == ["git", "log"]]
    assert log_calls, "no git log call issued"
    assert "--first-parent" in log_calls[0]
    # --reverse is load-bearing, not cosmetic: without it `entries[0]` is the branch TIP,
    # the first-parent check then fails for every non-tip arc, refresh_commit nulls, and
    # checkpoint confirmation silently re-anchors on the merge — reopening round-4 P1 and
    # its F2 consequence with the whole suite still green (merge-gate lens-3).
    assert "--reverse" in log_calls[0], (
        "oldest-first ordering is what makes entries[0] the immediate successor"
    )
    assert "%H%x09%P%x09%s" in " ".join(log_calls[0]), "parents must be in the log format"


def test_r4f1_unverifiable_shape_query_never_binds(repo, gstack, monkeypatch):
    """`_refresh_shape_ok` returning None (the `git show --name-only` query itself failed)
    must yield refresh_commit null — could-not-verify is not a licence to bind. Binding on
    an unverified shape would re-admit exactly the commits the §12.2.1 file-set rule
    excludes (merge-gate lens-3 item 6)."""
    sc = scenario(files={REFRESH: None})  # the shape query fails for the successor
    data = collect_with(sc, repo, gstack, monkeypatch)
    assert data["refresh_commit"] is None, "an unverifiable shape must never bind"
    assert any("could not be verified" in n for n in data["notes"])


# --- ARGV FIDELITY: the fake can only be as faithful as the command shapes it sees -------
# Every assertion below pins a flag whose loss is SILENT under the behavioural suite: the
# fake keeps answering, the code keeps running, and a field quietly goes wrong (merge-gate
# lens-3, HIGH/MEDIUM fake-fidelity items 3-5).


def test_argv_fidelity_of_the_external_queries(repo, gstack, tmp_path, monkeypatch):
    fake = make_run(scenario(), repo)
    monkeypatch.setattr(aer, "run", fake)
    aer.collect(1202, MERGE, repo, gstack_root=gstack, checkpoint=mk_ckpt(tmp_path, REFRESH_TS + 5))

    def one(pred, label):
        hits = [c for c in fake.calls if pred(c)]
        assert hits, f"no {label} call issued"
        return hits[0]

    # 3. `git show -s` must ask for %ct (epoch seconds). A drift to %cI returns an ISO
    #    string, `ts.isdigit()` is False, the anchor time is None, and checkpoint.confirmed
    #    becomes unconditionally false — with every behavioural test still green.
    ts_call = one(lambda c: c[:3] == ["git", "show", "-s"], "git show -s")
    assert "--format=%ct" in ts_call, "the anchor time must be epoch seconds"

    # 4. `git show --name-only` must ask for an EMPTY format. Without it git prepends the
    #    commit header, the changed-file list never equals [REFRESH_ONLY_FILE], and
    #    refresh_commit is permanently null.
    files_call = one(
        lambda c: c[:2] == ["git", "show"] and "--name-only" in c, "git show --name-only"
    )
    assert "--format=" in files_call, "commit headers must be suppressed from the file list"

    # 5. `gh pr view --json` must request BOTH fields. Dropping mergeCommit silently
    #    disables the oid half of the identity check (round-3 P2) — no test would notice.
    pr_call = one(lambda c: c[:3] == ["gh", "pr", "view"], "gh pr view")
    fields = pr_call[pr_call.index("--json") + 1].split(",")
    assert "state" in fields and "mergeCommit" in fields, f"pr view --json fields: {fields}"


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


# --- ROUND-4 FINDING 2: main_ci is the merge's own push run on the default branch -------
# Querying by --commit alone mixes manually-dispatched / non-main runs into the verdict.


def test_r4f2_dispatch_only_run_is_unresolved_not_a_verdict(repo, gstack, monkeypatch):
    """A `workflow_dispatch` success on the same SHA must NOT be reported as the post-merge
    verdict when the real push run is absent — that is a faked green."""
    sc = scenario(
        runs=[
            {
                "conclusion": "success",
                "status": "completed",
                "url": "u",
                "workflowName": "Manual",
                "event": "workflow_dispatch",
            }
        ]
    )
    data = collect_with(sc, repo, gstack, monkeypatch)
    assert data["main_ci"]["conclusion"] is None, "a dispatch run is not the post-merge verdict"
    assert data["main_ci"]["run_url"] is None
    assert any("No push-event workflow run on main" in n for n in data["notes"])


def test_r4f2_non_default_branch_run_is_unresolved(repo, gstack, monkeypatch):
    """A run of the same SHA on a topic branch (the PR's pre-merge checks) is not main CI."""
    sc = scenario(
        runs=[
            {
                "conclusion": "failure",
                "status": "completed",
                "url": "u",
                "workflowName": "CI",
                "branch": "some-topic-branch",
            }
        ]
    )
    data = collect_with(sc, repo, gstack, monkeypatch)
    assert data["main_ci"]["conclusion"] is None, "an off-main run must not fake a red verdict"
    assert any("No push-event workflow run on main" in n for n in data["notes"])


def test_r4f2_push_run_on_main_is_still_reported(repo, gstack, monkeypatch):
    sc = scenario(
        runs=[
            {
                "conclusion": "success",
                "status": "completed",
                "url": "u",
                "workflowName": "Manual",
                "event": "workflow_dispatch",
            },
            {
                "conclusion": "failure",
                "status": "completed",
                "url": "real",
                "workflowName": "CI",
                "event": "push",
                "branch": "main",
            },
        ]
    )
    data = collect_with(sc, repo, gstack, monkeypatch)
    assert data["main_ci"]["conclusion"] == "failure", "the push run is the verdict, verbatim"
    assert data["main_ci"]["run_url"] == "real"


def test_r4f2_gh_argv_carries_the_branch_and_event_filters(repo, gstack, monkeypatch):
    sc = scenario()
    fake = make_run(sc, repo)
    monkeypatch.setattr(aer, "run", fake)
    aer.collect(1202, MERGE, repo, gstack_root=gstack)
    run_calls = [c for c in fake.calls if c[:3] == ["gh", "run", "list"]]
    assert run_calls, "no `gh run list` call issued"
    argv = run_calls[0]
    assert argv[argv.index("--commit") + 1] == MERGE
    assert argv[argv.index("--branch") + 1] == "main"
    assert argv[argv.index("--event") + 1] == "push"


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


def test_ac4_todo_collection_failure_is_unknown_null_never_empty(
    repo, gstack, monkeypatch, shared_ledger
):
    """codex round-2: an UNREADABLE ledger must render `todo_for_human: null` + an UNKNOWN
    note — never an authoritative [] ('nothing is waiting' and 'could not look' are
    different claims). The ledger index row mirrors it as todos=unknown."""
    data = collect_with(scenario(todos_rc=3, todos=""), repo, gstack, monkeypatch)
    assert data["todo_for_human"] is None
    assert any("UNKNOWN" in n for n in data["notes"])
    rendered = aer.render(data)
    loaded = yaml.safe_load(yaml_block(rendered))
    assert "todo_for_human" in loaded and loaded["todo_for_human"] is None
    assert "UNKNOWN" in rendered
    assert "No pending DEFERRED-HIL items — nothing is waiting on a human." not in rendered
    monkeypatch.undo()
    assert aer.append_ledger_row(repo, data, "p.md") is True
    assert "todos=unknown" in shared_ledger.read_text(encoding="utf-8")


def test_ac4_missing_helper_libs_are_unknown_not_empty(tmp_path):
    """The OTHER arm of the same round-2 finding, and the one the behavioural suite could
    not reach: when `code_root` has no `tools/hooks/` libs, `_todos` must report UNKNOWN.
    Returning [] there is a confident 'nothing is waiting' derived from never having
    looked — mutating this branch to `return []` survived the entire suite (merge-gate
    lens-3 BLOCK item 2). Direct unit call: no fake, no monkeypatch, real filesystem."""
    bare = tmp_path / "no-hooks"
    (bare / ".harness").mkdir(parents=True)
    assert not (bare / "tools" / "hooks" / "loop_lib.sh").exists()
    notes: list[str] = []
    assert aer._todos(bare, bare, notes) is None, "never [] — that would claim we looked"
    assert any("UNKNOWN" in n and "loop_lib.sh not found" in n for n in notes)


def test_ac4_missing_helper_libs_render_as_null_and_todos_unknown(repo, tmp_path, shared_ledger):
    """…and it propagates: the yaml carries null, the prose warns, the index row says
    unknown — the same end-to-end shape as the nonzero-exit arm above."""
    bare = tmp_path / "no-hooks"
    (bare / ".harness").mkdir(parents=True)
    notes: list[str] = []
    data = {
        "pr": 1202,
        "merge_state": "MERGED",
        "merge_commit": MERGE,
        "main_ci": {"commit": MERGE, "conclusion": "success", "run_url": "u"},
        "refresh_commit": REFRESH,
        "checkpoint": {"path": None, "confirmed": False},
        "todo_for_human": aer._todos(bare, bare, notes),
        "notes": notes,
    }
    rendered = aer.render(data)
    assert yaml.safe_load(yaml_block(rendered))["todo_for_human"] is None
    assert "UNKNOWN" in rendered
    assert "No pending DEFERRED-HIL items — nothing is waiting on a human." not in rendered
    assert aer.append_ledger_row(repo, data, "p.md") is True
    assert "todos=unknown" in shared_ledger.read_text(encoding="utf-8")


# --- AC5: idempotent per-PR re-run ------------------------------------------------------


def test_ac5_rerun_overwrites_the_same_file(repo, gstack, monkeypatch):
    monkeypatch.setattr(aer, "append_ledger_row", lambda *_a, **_k: True)
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


def test_gate_l1_vanished_ledger_is_unknown_not_empty(repo, monkeypatch, tmp_path):
    """merge-gate lens-1 on #1204: the ledger existed at root resolution but vanished
    before the read (concurrent worktree disposition) — the field must degrade to
    UNKNOWN (None), never an authoritative [] under a rows-were-read note."""
    notes: list[str] = []
    gone = tmp_path / "goneroot"
    (gone / ".harness").mkdir(parents=True)
    # ledger_was_present=True but the SHARED venue (the autouse fixture's path, which no
    # test wrote to) holds no file at read time.
    got = aer._todos(gone, repo, notes, ledger_was_present=True)
    assert got is None
    assert any("vanished" in n for n in notes)


def test_r9_failed_index_append_fails_closed_with_exit_3(repo, gstack, monkeypatch, capsys):
    """codex round-9: both skill carriers treat exit 0 + report path as closure, so a
    failed EXIT-REPORT index append must exit nonzero (3) — while the report file itself
    is still written (it is the deliverable the runner repairs-and-reruns around)."""
    monkeypatch.setattr(aer, "GSTACK_PROJECTS", gstack)
    monkeypatch.setattr(aer, "run", make_run(scenario(), repo))
    monkeypatch.setattr(aer, "append_ledger_row", lambda *_a, **_k: False)
    rc = aer.main(["--pr", "1202", "--merge-sha", MERGE, "--repo-root", str(repo)])
    assert rc == 3
    assert aer.report_path(repo, 1202).is_file(), "the report itself is still written"
    err = capsys.readouterr().err
    assert "failing closed" in err and "index row" in err


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


# --- FINDING 1: checkpoint ownership is BOUND, never guessed ----------------------------
# The roadmap authorizes a parallel frontier (another live session can /context-save between
# this arc's save and this collection). mtime cannot discriminate ownership, so an unbound
# run must report the workspace-newest file as an explicitly UNCONFIRMED heuristic.


def test_f1_unbound_run_reports_the_newest_but_never_confirms(repo, gstack, monkeypatch):
    data = collect_with(scenario(), repo, gstack, monkeypatch)  # no checkpoint= → heuristic
    assert data["checkpoint"]["path"].endswith("20260803-210500-final.md")
    assert data["checkpoint"]["confirmed"] is False, (
        "an unbound checkpoint can never be confirmed — ownership is undecidable by mtime"
    )
    assert any("heuristically (workspace-newest)" in n for n in data["notes"])
    assert any("pass --checkpoint" in n for n in data["notes"])


def test_f1_unbound_stays_unconfirmed_even_though_mtime_beats_both_commits(
    repo, gstack, monkeypatch
):
    """The fixture's newest checkpoint post-dates merge AND refresh — so `confirmed: false`
    here is attributable to the binding rule alone, not to a timestamp accident."""
    data = collect_with(scenario(), repo, gstack, monkeypatch)
    newest_mtime = Path(data["checkpoint"]["path"]).stat().st_mtime
    assert newest_mtime > REFRESH_TS > MERGE_TS
    assert data["checkpoint"]["confirmed"] is False


def test_f1_bound_checkpoint_is_used_verbatim_and_confirms(repo, gstack, tmp_path, monkeypatch):
    bound = mk_ckpt(tmp_path, REFRESH_TS + 5)
    data = collect_with(scenario(), repo, gstack, monkeypatch, checkpoint=bound)
    assert data["checkpoint"] == {"path": str(bound), "confirmed": True}
    assert not any("heuristically" in n for n in data["notes"])


def test_f1_bound_checkpoint_wins_over_a_newer_parallel_arc_file(
    repo, gstack, tmp_path, monkeypatch
):
    """A parallel arc's checkpoint being NEWER must not displace the bound one."""
    parallel = gstack / "repo" / "checkpoints" / "20260804-000000-other-arc.md"
    parallel.write_text("another arc", encoding="utf-8")
    os.utime(parallel, (REFRESH_TS + 10_000, REFRESH_TS + 10_000))
    bound = mk_ckpt(tmp_path, REFRESH_TS + 5)
    data = collect_with(scenario(), repo, gstack, monkeypatch, checkpoint=bound)
    assert data["checkpoint"]["path"] == str(bound)
    assert "other-arc" not in data["checkpoint"]["path"]


def test_f1_nonexistent_bound_checkpoint_exits_2(repo, gstack, tmp_path, monkeypatch):
    monkeypatch.setattr(aer, "GSTACK_PROJECTS", gstack)
    monkeypatch.setattr(aer, "run", make_run(scenario(), repo))
    rc = aer.main(
        [
            "--pr",
            "1202",
            "--merge-sha",
            MERGE,
            "--repo-root",
            str(repo),
            "--checkpoint",
            str(tmp_path / "nope.md"),
        ]
    )
    assert rc == 2
    assert not aer.report_path(repo, 1202).exists()


def test_f1_unreadable_bound_checkpoint_degrades_not_crashes(repo, gstack, tmp_path, monkeypatch):
    data = collect_with(scenario(), repo, gstack, monkeypatch, checkpoint=tmp_path / "vanished.md")
    assert data["checkpoint"]["confirmed"] is False
    assert any("could not be read" in n for n in data["notes"])


def test_checkpoint_absent_is_null_and_false(repo, tmp_path, monkeypatch):
    data = collect_with(scenario(), repo, tmp_path / "no-gstack", monkeypatch)
    assert data["checkpoint"] == {"path": None, "confirmed": False}
    assert "checkpoint:\n  path: null\n  confirmed: false" in yaml_block(aer.render(data))


# --- FINDING 2: the confirmation anchor is the arc's CLOSING commit ----------------------
# The report is emitted after the §12.2.1 fixed point, so a checkpoint written between the
# merge and the terminating refresh is NOT the arc's final checkpoint and must not confirm.


def test_f2_checkpoint_between_merge_and_refresh_does_not_confirm(
    repo, gstack, tmp_path, monkeypatch
):
    mid = mk_ckpt(tmp_path, MERGE_TS + 1)  # after the merge, before the refresh
    assert MERGE_TS < MERGE_TS + 1 < REFRESH_TS
    data = collect_with(scenario(), repo, gstack, monkeypatch, checkpoint=mid)
    assert data["refresh_commit"] == REFRESH
    assert data["checkpoint"]["confirmed"] is False, (
        "merge-time anchoring would wrongly confirm a pre-refresh checkpoint"
    )
    assert any("predates the refresh commit" in n for n in data["notes"])


def test_f2_checkpoint_after_the_refresh_confirms(repo, gstack, tmp_path, monkeypatch):
    after = mk_ckpt(tmp_path, REFRESH_TS + 1)
    data = collect_with(scenario(), repo, gstack, monkeypatch, checkpoint=after)
    assert data["checkpoint"]["confirmed"] is True


def test_f2_no_refresh_falls_back_to_the_merge_anchor(repo, gstack, tmp_path, monkeypatch):
    sc = scenario(log=[], files={})  # no terminating refresh landed yet
    after_merge = mk_ckpt(tmp_path, MERGE_TS + 1)
    data = collect_with(sc, repo, gstack, monkeypatch, checkpoint=after_merge)
    assert data["refresh_commit"] is None
    assert data["checkpoint"]["confirmed"] is True, "merge is the anchor when no refresh exists"

    before_merge = mk_ckpt(tmp_path, MERGE_TS - 1, name="early.md")
    data = collect_with(sc, repo, gstack, monkeypatch, checkpoint=before_merge)
    assert data["checkpoint"]["confirmed"] is False
    assert any("predates the merge commit" in n for n in data["notes"])


def test_f2_unreadable_anchor_time_is_not_confirmed(repo, gstack, tmp_path, monkeypatch):
    sc = scenario(ts={})  # `git show -s --format=%ct` fails for every commit
    bound = mk_ckpt(tmp_path, REFRESH_TS + 5)
    data = collect_with(sc, repo, gstack, monkeypatch, checkpoint=bound)
    assert data["checkpoint"]["confirmed"] is False
    assert any("closing commit time could not be read" in n for n in data["notes"])


def test_f2_render_names_the_anchor_it_confirmed_against(repo, gstack, tmp_path, monkeypatch):
    data = collect_with(
        scenario(), repo, gstack, monkeypatch, checkpoint=mk_ckpt(tmp_path, REFRESH_TS + 5)
    )
    assert "written after the terminating refresh" in aer.render(data)
    sc = scenario(log=[], files={})
    data = collect_with(
        sc, repo, gstack, monkeypatch, checkpoint=mk_ckpt(tmp_path, MERGE_TS + 5, "m.md")
    )
    assert "written after the merge" in aer.render(data)


# --- FINDING 3: PR identity is verified before any fact is attached ---------------------


def test_f3_unmerged_pr_exits_2_and_writes_nothing(repo, gstack, monkeypatch):
    sc = scenario(pr_view={"state": "OPEN", "mergeCommit": None})
    monkeypatch.setattr(aer, "GSTACK_PROJECTS", gstack)
    monkeypatch.setattr(aer, "run", make_run(sc, repo))
    assert aer.main(["--pr", "1202", "--repo-root", str(repo)]) == 2
    assert not aer.report_path(repo, 1202).exists()


def test_f3_merge_sha_disagreeing_with_the_pr_exits_2(repo, gstack, monkeypatch):
    """A mistyped SHA that still resolves to SOME commit must not silently attach another
    arc's CI / refresh / checkpoint facts to this PR's report."""
    sc = scenario()  # PR 1202 merged at MERGE
    monkeypatch.setattr(aer, "GSTACK_PROJECTS", gstack)
    monkeypatch.setattr(aer, "run", make_run(sc, repo))
    assert aer.main(["--pr", "1202", "--merge-sha", OTHER, "--repo-root", str(repo)]) == 2
    assert not aer.report_path(repo, 1202).exists()


def test_f3_matching_merge_sha_is_accepted(repo, gstack, monkeypatch):
    data = collect_with(scenario(), repo, gstack, monkeypatch)
    assert data["identity_error"] is None
    assert data["merge_commit"] == MERGE


def test_f3_gh_absent_still_degrades_to_success(repo, gstack, monkeypatch):
    """No PR data = nothing to contradict: identity checking must not turn a degraded run
    into a refusal."""
    monkeypatch.setattr(aer, "append_ledger_row", lambda *_a, **_k: True)
    sc = scenario(gh_absent=True)
    monkeypatch.setattr(aer, "GSTACK_PROJECTS", gstack)
    monkeypatch.setattr(aer, "run", make_run(sc, repo))
    assert aer.main(["--pr", "1202", "--merge-sha", MERGE, "--repo-root", str(repo)]) == 0
    assert aer.report_path(repo, 1202).is_file()


@pytest.mark.parametrize(
    "state,oid,sha,expected_none",
    [
        (None, "", "", True),  # gh silent → no check
        ("", "", "", True),
        ("MERGED", MERGE, MERGE, True),
        ("MERGED", MERGE, "", True),  # no --merge-sha supplied → oid half not applicable
        ("MERGED", "", MERGE, True),  # gh gave no oid → nothing to compare
        ("OPEN", "", "", False),
        ("CLOSED", "", "", False),
        ("MERGED", MERGE, OTHER, False),
    ],
)
def test_f3_identity_error_truth_table(state, oid, sha, expected_none):
    assert (aer.identity_error(1202, state, oid, sha) is None) is expected_none


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

# C-HE-09 §3 row shape: | ts | kind | lane=<id>;cause=<sig> | detail |
ROW = re.compile(
    r"^\| (?P<ts>[^|]+) \| (?P<kind>[^|]+) \| (?P<col>lane=[^|]*) \| (?P<detail>.*) \|$"
)


def unescape(detail: str) -> str:
    """Inverse of loop_log's `sed 's/|/\\|/g'` pipe escaping."""
    return detail.replace("\\|", "|")


def test_ledger_row_byte_format_via_the_real_loop_log(repo, gstack, monkeypatch, shared_ledger):
    data = collect_with(scenario(todos="R-410 — needs runtime"), repo, gstack, monkeypatch)
    monkeypatch.undo()  # the ledger append must use the REAL subprocess runner
    rel = f"{aer.REPORT_DIR}/arc-exit-report-pr1202.md"
    assert aer.append_ledger_row(repo, data, rel) is True

    lines = shared_ledger.read_text(encoding="utf-8").splitlines()
    rows = [ROW.match(ln) for ln in lines if ln.startswith("| ") and " | EXIT-REPORT | " in ln]
    assert len(rows) == 1, f"expected exactly one EXIT-REPORT row, got {len(rows)}"
    m = rows[0]
    assert m.group("kind") == "EXIT-REPORT"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", m.group("ts"))
    detail = unescape(m.group("detail"))
    assert detail == (f"pr=#1202 ci={MERGE[:8]}:success refresh={REFRESH[:8]} todos=1 path={rel}")


def test_ledger_row_marks_a_missing_refresh_as_none(repo, gstack, monkeypatch, shared_ledger):
    data = collect_with(scenario(log=[], files={}, todos=""), repo, gstack, monkeypatch)
    monkeypatch.undo()
    assert aer.append_ledger_row(repo, data, "p.md") is True
    text = shared_ledger.read_text(encoding="utf-8")
    assert "refresh=none todos=0" in text
    assert REFRESH[:8] not in text


def test_ledger_rerun_with_silent_append_failure_is_not_a_false_pass(repo, gstack, monkeypatch):
    """codex round-1 P3: on an idempotent rerun, a substring match against the PREVIOUS
    invocation's identical row must not mask a silently failed append. Success requires
    the ledger to GROW this invocation."""
    data = collect_with(scenario(todos=""), repo, gstack, monkeypatch)
    monkeypatch.undo()
    rel = f"{aer.REPORT_DIR}/arc-exit-report-pr1202.md"
    assert aer.append_ledger_row(repo, data, rel) is True  # first run really appends

    # Rerun with loop_log neutered to a silent no-op (rc 0, no write) — the prior
    # identical row is still present, so a substring check would false-pass.
    real_run = aer.run

    def neutered(cmd, cwd):
        if any("loop_log" in str(part) for part in cmd):
            return 0, ""
        return real_run(cmd, cwd)

    monkeypatch.setattr(aer, "run", neutered)
    assert aer.append_ledger_row(repo, data, rel) is False


def test_ledger_row_pipes_are_escaped_so_one_row_stays_one_row(
    repo, gstack, monkeypatch, shared_ledger
):
    data = collect_with(scenario(), repo, gstack, monkeypatch)
    monkeypatch.undo()
    assert aer.append_ledger_row(repo, data, "a|b.md") is True
    line = next(
        ln for ln in shared_ledger.read_text(encoding="utf-8").splitlines() if "EXIT-REPORT" in ln
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


# --- ROUND-6 FINDING 1: artifacts land in the MAIN checkout, not a disposable worktree ---
# The Codex flow runs inside an isolated arc worktree that worktree-disposition deletes. A
# toplevel-rooted write vanishes with it, and a controller rerun then writes a DIFFERENT
# file instead of overwriting the PR-keyed one.


@pytest.fixture
def worktree_pair(tmp_path):
    """(main_checkout, linked_worktree) — the worktree's `--git-common-dir` points into the
    main checkout's .git, exactly as real git reports it."""
    main = mk_repo(tmp_path / "main-checkout")
    (main / ".git").mkdir(exist_ok=True)
    wt = mk_repo(tmp_path / "arc-worktree")
    return main, wt


def test_r6f1_linked_worktree_writes_to_the_main_checkout(
    worktree_pair, gstack, monkeypatch, shared_ledger
):
    main, wt = worktree_pair
    sc = scenario(common_dir=(0, str(main / ".git")))
    monkeypatch.chdir(wt)  # invoked FROM the arc worktree, as the Codex flow does
    monkeypatch.setattr(aer, "GSTACK_PROJECTS", gstack)
    # real_bash: let loop_log actually append, so this witnesses where the ledger LANDS.
    monkeypatch.setattr(aer, "run", make_run(sc, wt, real_bash=True))
    assert aer.main(["--pr", "1202", "--merge-sha", MERGE]) == 0

    assert aer.report_path(main, 1202).is_file(), "report must land in the MAIN checkout"
    assert not aer.report_path(wt, 1202).exists(), "nothing may be left in the disposable worktree"
    # The REPORT is redirected to the main checkout; the ledger row is not "redirected"
    # anywhere -- it lands in the one shared venue (C-HE-09 §2), which is neither checkout.
    assert shared_ledger.is_file(), "ledger index must land in the SHARED venue"
    assert not (main / ".harness" / "loop_status.md").exists()
    assert not (wt / ".harness" / "loop_status.md").exists()
    assert "MAIN checkout" in aer.report_path(main, 1202).read_text(encoding="utf-8")


def test_r6f1_rerun_from_the_worktree_overwrites_the_same_main_file(
    worktree_pair, gstack, monkeypatch
):
    """The defect's actual cost: idempotency. Two runs must produce ONE report file."""
    monkeypatch.setattr(aer, "append_ledger_row", lambda *_a, **_k: True)
    main, wt = worktree_pair
    sc = scenario(common_dir=(0, str(main / ".git")))
    monkeypatch.chdir(wt)
    monkeypatch.setattr(aer, "GSTACK_PROJECTS", gstack)
    monkeypatch.setattr(aer, "run", make_run(sc, wt))
    assert aer.main(["--pr", "1202", "--merge-sha", MERGE]) == 0
    assert aer.main(["--pr", "1202", "--merge-sha", MERGE]) == 0
    written = sorted((main / aer.REPORT_DIR).glob("arc-exit-report-pr*.md"))
    assert [p.name for p in written] == ["arc-exit-report-pr1202.md"]


# --- ROUND-7 FINDING, as re-cut by U-HE-29 ---------------------------------------------
# The original finding was that the report's WRITE redirect (worktree → main checkout)
# must not drag the pending-HIL READ with it, because each worktree kept its OWN
# `.harness/loop_status.md` and reading the wrong one either lost this arc's obligations
# or surfaced a parallel session's. C-HE-09 §2 dissolves the premise: there is now exactly
# ONE ledger for every lane. What must still hold is that the read reaches THAT venue
# (never a per-checkout path) and that rows keep their lane attribution, which is what the
# tests below pin. The write redirect itself is unchanged and still covered above.


def write_ledger(path: Path, *details: str, lane: str = "-") -> Path:
    """A minimal SHARED loop ledger carrying one DEFERRED-HIL row per `details` entry.

    Rows are written in the C-HE-09 §3 structured shape (`lane=…;cause=…` BEFORE detail);
    `lane` sets the emitting lane so cross-lane attribution can be asserted.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = "".join(
        f"| 2026-08-04T00:01:00Z | DEFERRED-HIL | lane={lane};cause=- | {d} |\n" for d in details
    )
    with path.open("a", encoding="utf-8") as fh:
        if fh.tell() == 0:
            fh.write(
                "| timestamp | kind | lane;cause | detail |\n|---|---|---|---|\n"
                "| 2026-08-04T00:00:00Z | ACTIVATE | lane=-;cause=- | run |\n"
            )
        fh.write(rows)
    return path


def test_u_he_29_worktree_read_reaches_the_shared_venue_with_lane_attribution(
    worktree_pair, gstack, monkeypatch, shared_ledger
):
    """(a) THE discriminator, re-cut: a worktree closeout reads the SHARED venue, and every
    row arrives tagged with the lane that deferred it.

    Pre-U-HE-29 this test asserted the opposite shape — the worktree's private ledger won
    and a parallel lane's rows were excluded. That exclusion was a workaround for the venue
    split, not a goal: two lanes gated on the same operator are both real obligations, and
    the lane tag is what makes a shared list actionable rather than confusing."""
    main, wt = worktree_pair
    write_ledger(shared_ledger, "R-501 — needs a vendor pick", lane="L1")
    write_ledger(shared_ledger, "B-77 — needs paid-call authorization", lane="L1")
    write_ledger(shared_ledger, "R-999 — a sibling lane's item", lane="L2")
    sc = scenario(common_dir=(0, str(main / ".git")))
    monkeypatch.chdir(wt)
    monkeypatch.setattr(aer, "GSTACK_PROJECTS", gstack)
    monkeypatch.setattr(aer, "run", make_run(sc, wt, real_bash=True))
    assert aer.main(["--pr", "1202", "--merge-sha", MERGE]) == 0

    body = aer.report_path(main, 1202).read_text(encoding="utf-8")  # still written to MAIN
    loaded = yaml.safe_load(yaml_block(body))
    assert loaded["todo_for_human"] == [
        "[L1] B-77 — needs paid-call authorization",
        "[L1] R-501 — needs a vendor pick",
        "[L2] R-999 — a sibling lane's item",
    ], "with no resolvable lane id, every open deferral is kept, each carrying its lane"
    assert "SHARED loop ledger" in body, "the venue must be stated honestly"
    assert "every open row across lanes" in body, "an unfiltered list must SAY it is unfiltered"


def test_u_he_29_todo_for_human_annotates_lanes_and_never_drops_a_row(
    worktree_pair, gstack, monkeypatch, shared_ledger
):
    """Every open row is listed, with the lane split STATED — no row is ever dropped.

    Filtering was tried twice and hid a real row both times (B-196): excluding lane != mine
    dropped this arc's own unattributed rows, and excluding only demonstrably-foreign lanes
    still hid rows because the reducer collapses by ITEM — when two lanes defer the same
    item, only the last deferrer renders, so another lane's row can be the sole trace of an
    item this lane also has open."""
    main, wt = worktree_pair
    write_ledger(shared_ledger, "R-501 — needs a vendor pick", lane="L1")
    write_ledger(shared_ledger, "R-999 — a sibling lane's item", lane="L2")
    write_ledger(shared_ledger, "R-888 — a third lane's item", lane="L3")
    (wt / ".harness").mkdir(exist_ok=True)
    (wt / ".harness" / ".lane-id").write_text("L1\n", encoding="utf-8")
    sc = scenario(common_dir=(0, str(main / ".git")))
    monkeypatch.chdir(wt)
    monkeypatch.setattr(aer, "GSTACK_PROJECTS", gstack)
    monkeypatch.setattr(aer, "run", make_run(sc, wt, real_bash=True))
    assert aer.main(["--pr", "1202", "--merge-sha", MERGE]) == 0

    body = aer.report_path(main, 1202).read_text(encoding="utf-8")
    assert yaml.safe_load(yaml_block(body))["todo_for_human"] == [
        "[L1] R-501 — needs a vendor pick",
        "[L2] R-999 — a sibling lane's item",
        "[L3] R-888 — a third lane's item",
    ], "every row is listed; the rendered lane cannot prove sole ownership (B-196)"
    assert "1 render under this arc's lane (L1)" in body, "the split must be stated"
    assert "Rows are NOT filtered by lane" in body


def test_u_he_29_closeout_drains_a_pre_cutover_legacy_ledger(
    worktree_pair, gstack, monkeypatch, shared_ledger
):
    """codex r10 P1: a worktree whose session began BEFORE the U-HE-29 cutover still holds
    its pending rows in its own legacy ledger — SessionStart is the only other migration
    caller, and it did not run for this session.

    Reading only the shared venue would record an EMPTY todo list, and the worktree
    disposition this report is ordered before would then delete those obligations
    permanently. Closeout therefore drains first."""
    main, wt = worktree_pair
    # The migration enumerates through `git worktree list`, so the invoking worktree has to
    # be a real repo for the drain to run at all. Identity is passed inline — CI has none.
    subprocess.run(["git", "init", "-q", "."], cwd=wt, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.email=t@t",
            "-c",
            "user.name=t",
            "commit",
            "-q",
            "--allow-empty",
            "-m",
            "init",
        ],
        cwd=wt,
        check=True,
    )
    (wt / ".harness").mkdir(exist_ok=True)
    (wt / ".harness" / "loop_status.md").write_text(
        "| timestamp | kind | detail |\n|---|---|---|\n"
        "| 2026-08-04T00:01:00Z | DEFERRED-HIL | R-720 — pending since before the cutover |\n",
        encoding="utf-8",
    )
    sc = scenario(common_dir=(0, str(main / ".git")))
    monkeypatch.chdir(wt)
    monkeypatch.setattr(aer, "GSTACK_PROJECTS", gstack)
    monkeypatch.setattr(aer, "run", make_run(sc, wt, real_bash=True))
    assert aer.main(["--pr", "1202", "--merge-sha", MERGE]) == 0

    body = aer.report_path(main, 1202).read_text(encoding="utf-8")
    todos = yaml.safe_load(yaml_block(body))["todo_for_human"]
    assert todos is not None, "a drainable legacy ledger must not read as UNKNOWN"
    assert any("R-720" in t for t in todos), (
        "the pre-cutover obligation must survive into this arc's closure record"
    )
    assert not (wt / ".harness" / "loop_status.md").exists(), "the legacy ledger is retired"


def test_u_he_29_closeout_drains_an_orphan_only_recovery_state(
    worktree_pair, gstack, monkeypatch, shared_ledger
):
    """codex r18 P1: a migration that failed between claiming and retiring leaves NO
    `loop_status.md` — only a `.migrating-*` claim, which the migration knows how to recover.

    Gating the closeout drain on the ORIGINAL filename alone skipped the drain in exactly
    that recovery case, reported an empty todo list, and let the following worktree
    disposition delete the stranded rows permanently."""
    main, wt = worktree_pair
    subprocess.run(["git", "init", "-q", "."], cwd=wt, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.email=t@t",
            "-c",
            "user.name=t",
            "commit",
            "-q",
            "--allow-empty",
            "-m",
            "init",
        ],
        cwd=wt,
        check=True,
    )
    (wt / ".harness").mkdir(exist_ok=True)
    # Orphan ONLY — no loop_status.md at all. Dead owner pid so it is recoverable.
    (wt / ".harness" / "loop_status.md.migrating-2026-08-04T00:00:00Z-999999-1").write_text(
        "| 2026-08-04T00:01:00Z | DEFERRED-HIL | R-730 — stranded in an orphaned claim |\n",
        encoding="utf-8",
    )
    assert not (wt / ".harness" / "loop_status.md").exists()
    sc = scenario(common_dir=(0, str(main / ".git")))
    monkeypatch.chdir(wt)
    monkeypatch.setattr(aer, "GSTACK_PROJECTS", gstack)
    monkeypatch.setattr(aer, "run", make_run(sc, wt, real_bash=True))
    assert aer.main(["--pr", "1202", "--merge-sha", MERGE]) == 0

    body = aer.report_path(main, 1202).read_text(encoding="utf-8")
    todos = yaml.safe_load(yaml_block(body))["todo_for_human"]
    assert todos is not None, "an orphan-only state must not read as UNKNOWN"
    assert any("R-730" in t for t in todos), (
        "a row stranded in an orphaned claim must still reach this arc's closure record"
    )


def test_u_he_29_closeout_is_unknown_while_a_sibling_is_still_draining(
    repo, monkeypatch, tmp_path, shared_ledger
):
    """rc==2 from the migration means "the venue is not complete yet", and the report must
    NOT publish a list read from it.

    The shell side pins that `loop_status_migrate` EXITS 2 when it skips a live sibling's
    claim, but an exit code nobody consumes is not a fix — this pins the CONSUMER: a
    write-once, PR-keyed closure record must degrade to UNKNOWN rather than freeze a short
    todo list while another migrator is still importing. UNKNOWN is recoverable by re-running
    the report; a confidently-wrong closure record is not.
    """
    notes: list[str] = []
    root = tmp_path / "sibling-draining-wt"
    (root / ".harness").mkdir(parents=True)
    # An orphan-only state, so the drain gate fires and the migration is actually invoked.
    (root / ".harness" / "loop_status.md.migrating-2026-08-05T00:00:00Z-424242-1").write_text(
        "| 2026-08-05T00:01:00Z | DEFERRED-HIL | R-740 — held by a live sibling |\n",
        encoding="utf-8",
    )
    real_run = aer.run

    def run_stub(cmd, cwd, timeout=20):
        if len(cmd) > 2 and "loop_status_migrate" in cmd[2]:
            return 2, ""  # a live sibling holds the claim; venue incomplete
        return real_run(cmd, cwd, timeout)

    monkeypatch.setattr(aer, "run", run_stub)
    got = aer._todos(root, repo, notes)
    assert got is None, "a still-draining venue must be UNKNOWN, never a confident list"
    assert any("concurrent migration is still draining" in n for n in notes)
    assert any("not lost, only not yet visible" in n for n in notes), (
        "the note must say the rows survive, so UNKNOWN does not read as data loss"
    )


def test_u_he_29_closeout_fails_closed_when_the_legacy_drain_fails(
    repo, monkeypatch, tmp_path, shared_ledger
):
    """An UNDRAINABLE legacy ledger must degrade todo_for_human to UNKNOWN, never to [].

    "Could not drain" and "nothing pending" are exactly the two claims that must not be
    confused at the moment an arc closes and its worktree is disposed."""
    notes: list[str] = []
    root = tmp_path / "pre-cutover-wt"
    (root / ".harness").mkdir(parents=True)
    legacy = root / ".harness" / "loop_status.md"
    legacy.write_text("| t | DEFERRED-HIL | R-721 — unreachable |\n", encoding="utf-8")
    # `root` is not a git repo, so the migration cannot enumerate worktrees and fails.
    got = aer._todos(root, repo, notes)
    assert got is None, "an undrainable legacy ledger must be UNKNOWN, not []"
    assert any("could not be drained" in n for n in notes)
    assert any("before disposing the worktree" in n for n in notes)


def test_u_he_29_lane_id_resolves_in_the_same_order_as_the_writer(tmp_path, monkeypatch):
    """HARNESS_LANE_ID first, then the persisted `.harness/.lane-id` — the SAME order
    `loop_lib.sh`'s `_loop_lane_id` uses when it writes the lane into a row.

    The precedence must match the WRITER's, because the writer decides the lane a row is
    recorded under. Resolving the two sources in the opposite order would, whenever both
    exist and differ, make this arc classify its own freshly-written rows as foreign and omit
    them from its own closure record (codex r7 P2)."""
    root = tmp_path / "wt"
    (root / ".harness").mkdir(parents=True)
    monkeypatch.delenv("HARNESS_LANE_ID", raising=False)
    assert aer._lane_id(root) == ""
    (root / ".harness" / ".lane-id").write_text("  L1  \n", encoding="utf-8")
    assert aer._lane_id(root) == "L1", "the persisted marker is used when the env is unset"
    monkeypatch.setenv("HARNESS_LANE_ID", "L9")
    assert aer._lane_id(root) == "L9", "HARNESS_LANE_ID wins, matching the writer"


def test_u_he_29_lane_id_is_sanitized_the_way_the_ledger_stores_it(tmp_path, monkeypatch):
    """The writer strips separators out of the lane before recording it, so the reader must
    apply the identical strip — otherwise a separator-bearing id never matches its own rows
    and the arc's obligations read as foreign (codex r6/r7 P2)."""
    root = tmp_path / "wt"
    (root / ".harness").mkdir(parents=True)
    monkeypatch.setenv("HARNESS_LANE_ID", "la ne;x|y[z]")
    assert aer._lane_id(root) == "lanexyz"


def test_u_he_29_lane_annotation_never_drops_an_unattributed_row(tmp_path):
    """The regression this shape exists to prevent: rows written WITHOUT a lane (`-`) are
    this arc's own — `tools/04-loop/defer.sh` sets no HARNESS_LANE_ID — so a lane-equality
    filter would delete exactly the obligations most likely to be real. Nothing is dropped
    at all now (B-196), which subsumes the case."""
    root = tmp_path / "wt"
    (root / ".harness").mkdir(parents=True)
    (root / ".harness" / ".lane-id").write_text("L1\n", encoding="utf-8")
    notes: list[str] = []
    rows = ["[-] deferred-via-defer.sh — needs creds", "[L1] mine — x", "[L2] sibling — y"]
    assert aer._scope_to_lane(rows, root, notes) == rows, "no row may be dropped"
    assert any("Rows are NOT filtered by lane" in n for n in notes)


def test_u_he_29_lane_annotation_with_no_resolvable_lane(tmp_path):
    """No lane id: still every row, and the note says the list spans lanes."""
    notes: list[str] = []
    rows = ["[L1] a — x", "[L2] b — y"]
    assert aer._scope_to_lane(rows, tmp_path / "nonexistent", notes) == rows
    assert any("every open row across lanes" in n for n in notes)


def test_u_he_29_no_shared_ledger_is_an_honest_empty(worktree_pair, gstack, monkeypatch):
    """(b) With no ledger at the shared venue at all, nothing was ever deferred: the honest
    answer is [], never a fabricated row and never UNKNOWN (the ledger did not VANISH — it
    was never there, which `ledger_was_present=False` distinguishes)."""
    main, wt = worktree_pair
    sc = scenario(common_dir=(0, str(main / ".git")))
    monkeypatch.chdir(wt)
    monkeypatch.setattr(aer, "GSTACK_PROJECTS", gstack)
    monkeypatch.setattr(aer, "run", make_run(sc, wt, real_bash=True))
    assert aer.main(["--pr", "1202", "--merge-sha", MERGE]) == 0

    body = aer.report_path(main, 1202).read_text(encoding="utf-8")
    assert yaml.safe_load(yaml_block(body))["todo_for_human"] == []


def test_r7_neither_ledger_present_is_an_honest_empty(worktree_pair, gstack, monkeypatch):
    main, wt = worktree_pair
    sc = scenario(common_dir=(0, str(main / ".git")))
    monkeypatch.chdir(wt)
    monkeypatch.setattr(aer, "GSTACK_PROJECTS", gstack)
    monkeypatch.setattr(aer, "run", make_run(sc, wt, real_bash=True))
    assert aer.main(["--pr", "1202", "--merge-sha", MERGE]) == 0
    body = aer.report_path(main, 1202).read_text(encoding="utf-8")
    assert yaml.safe_load(yaml_block(body))["todo_for_human"] == []


def test_r7_main_checkout_invocation_reads_and_writes_one_root(
    repo, gstack, monkeypatch, shared_ledger
):
    """(c) unchanged for a main-checkout run: both roots are the same, no worktree note."""
    write_ledger(shared_ledger, "R-410 — needs container runtime")
    sc = scenario(common_dir=(0, str(repo / ".git")))
    monkeypatch.chdir(repo)
    monkeypatch.setattr(aer, "GSTACK_PROJECTS", gstack)
    monkeypatch.setattr(aer, "run", make_run(sc, repo, real_bash=True))
    assert aer.main(["--pr", "1202", "--merge-sha", MERGE]) == 0
    body = aer.report_path(repo, 1202).read_text(encoding="utf-8")
    assert yaml.safe_load(yaml_block(body))["todo_for_human"] == [
        "[-] R-410 — needs container runtime"
    ]
    assert "SHARED loop ledger" not in body, "no worktree redirect happened, so no note"
    assert "linked worktree" not in body


def test_r7_explicit_repo_root_sets_both_roots(worktree_pair, gstack, monkeypatch, shared_ledger):
    """An explicit --repo-root wins entirely — it is the read root as well as the write one.
    The ledger it reads is the shared venue either way (C-HE-09 §2)."""
    main, wt = worktree_pair
    write_ledger(shared_ledger, "R-999 — the one shared row")
    sc = scenario(common_dir=(0, str(main / ".git")))
    monkeypatch.chdir(wt)
    monkeypatch.setattr(aer, "GSTACK_PROJECTS", gstack)
    # `--repo-root main` makes git run with cwd=main, so `--show-toplevel` answers main —
    # the fake mirrors that rather than the (now irrelevant) process cwd.
    monkeypatch.setattr(aer, "run", make_run(sc, main, real_bash=True))
    assert aer.main(["--pr", "1202", "--merge-sha", MERGE, "--repo-root", str(main)]) == 0
    body = aer.report_path(main, 1202).read_text(encoding="utf-8")
    assert yaml.safe_load(yaml_block(body))["todo_for_human"] == ["[-] R-999 — the one shared row"]


def test_r7_stale_worktree_loop_lib_does_not_break_the_read(
    worktree_pair, gstack, monkeypatch, shared_ledger
):
    """Witnessed LIVE against a real worktree checked out at an older revision: sourcing the
    WORKTREE's `loop_lib.sh` exited 127 because that copy predates `loop_pending_hil_list`,
    degrading the whole field to UNKNOWN. The parser CODE must come from the main checkout,
    whose helper set is current — now doubly so, since a pre-U-HE-29 worktree copy would
    also resolve the ledger to the OLD per-worktree venue."""
    main, wt = worktree_pair
    write_ledger(shared_ledger, "R-501 — this arc's obligation")
    # Simulate the stale worktree: its loop_lib.sh has no loop_pending_hil_list.
    stale = (wt / "tools" / "hooks" / "loop_lib.sh").read_text(encoding="utf-8")
    (wt / "tools" / "hooks" / "loop_lib.sh").write_text(
        stale.replace("loop_pending_hil_list()", "loop_pending_hil_list_RENAMED()"),
        encoding="utf-8",
    )
    sc = scenario(common_dir=(0, str(main / ".git")))
    monkeypatch.chdir(wt)
    monkeypatch.setattr(aer, "GSTACK_PROJECTS", gstack)
    monkeypatch.setattr(aer, "run", make_run(sc, wt, real_bash=True))
    assert aer.main(["--pr", "1202", "--merge-sha", MERGE]) == 0

    body = aer.report_path(main, 1202).read_text(encoding="utf-8")
    assert yaml.safe_load(yaml_block(body))["todo_for_human"] == [
        "[-] R-501 — this arc's obligation"
    ]
    assert "UNKNOWN" not in body, "a stale worktree helper set must not blank the field"


def test_r7_resolve_repo_root_returns_both_roots(worktree_pair, monkeypatch):
    """Structural: the resolver's contract is a (write, read) pair, not one path."""
    main, wt = worktree_pair
    monkeypatch.setattr(aer, "run", make_run(scenario(common_dir=(0, str(main / ".git"))), wt))
    roots, notes = aer.resolve_repo_root(wt)
    assert roots is not None
    assert roots.write == main and roots.read == wt
    assert any("SHARED loop ledger" in n for n in notes)


def test_r6f1_main_checkout_invocation_is_unchanged(repo, gstack, monkeypatch):
    """A main checkout: `--git-common-dir`'s parent IS the toplevel → no redirect, no note."""
    monkeypatch.setattr(aer, "append_ledger_row", lambda *_a, **_k: True)
    monkeypatch.chdir(repo)
    monkeypatch.setattr(aer, "GSTACK_PROJECTS", gstack)
    monkeypatch.setattr(aer, "run", make_run(scenario(common_dir=(0, str(repo / ".git"))), repo))
    assert aer.main(["--pr", "1202", "--merge-sha", MERGE]) == 0
    assert aer.report_path(repo, 1202).is_file()
    body = aer.report_path(repo, 1202).read_text(encoding="utf-8")
    assert "linked worktree" not in body


def test_r6f1_unresolvable_common_dir_falls_back_to_toplevel_with_a_note(repo, gstack, monkeypatch):
    monkeypatch.setattr(aer, "append_ledger_row", lambda *_a, **_k: True)
    sc = scenario(common_dir=(128, ""))
    monkeypatch.chdir(repo)
    monkeypatch.setattr(aer, "GSTACK_PROJECTS", gstack)
    monkeypatch.setattr(aer, "run", make_run(sc, repo))
    assert aer.main(["--pr", "1202", "--merge-sha", MERGE]) == 0
    body = aer.report_path(repo, 1202).read_text(encoding="utf-8")
    assert "did not resolve" in body and "worktree-local" in body


def test_r6f1_main_root_without_harness_is_not_trusted(
    worktree_pair, tmp_path, gstack, monkeypatch
):
    """Resolution must be VALIDATED, not assumed — a common-dir parent that is not this
    workspace falls back to the worktree, with a note."""
    monkeypatch.setattr(aer, "append_ledger_row", lambda *_a, **_k: True)
    _main, wt = worktree_pair
    stranger = tmp_path / "stranger"
    (stranger / ".git").mkdir(parents=True)  # no .harness/
    sc = scenario(common_dir=(0, str(stranger / ".git")))
    monkeypatch.chdir(wt)
    monkeypatch.setattr(aer, "GSTACK_PROJECTS", gstack)
    monkeypatch.setattr(aer, "run", make_run(sc, wt))
    assert aer.main(["--pr", "1202", "--merge-sha", MERGE]) == 0
    assert aer.report_path(wt, 1202).is_file(), "untrusted resolution falls back to the worktree"
    assert not aer.report_path(stranger, 1202).exists()
    assert "has no .harness/" in aer.report_path(wt, 1202).read_text(encoding="utf-8")


def test_r6f1_explicit_repo_root_wins_over_the_redirect(worktree_pair, gstack, monkeypatch):
    monkeypatch.setattr(aer, "append_ledger_row", lambda *_a, **_k: True)
    main, wt = worktree_pair
    sc = scenario(common_dir=(0, str(main / ".git")))
    monkeypatch.chdir(wt)
    monkeypatch.setattr(aer, "GSTACK_PROJECTS", gstack)
    monkeypatch.setattr(aer, "run", make_run(sc, wt))
    assert aer.main(["--pr", "1202", "--merge-sha", MERGE, "--repo-root", str(wt)]) == 0
    assert aer.report_path(wt, 1202).is_file(), "an explicit --repo-root is authoritative"
    assert not aer.report_path(main, 1202).exists()


def test_r6f1_not_a_git_repo_still_exits_2(tmp_path, monkeypatch):
    monkeypatch.setattr(aer, "run", lambda cmd, cwd, timeout=20: (128, ""))
    assert aer.main(["--pr", "1", "--repo-root", str(tmp_path)]) == 2


# --- ROUND-6 FINDING 2: repo paths are argv values, never bash source -------------------
# `…/re"po; touch /tmp/x; #` interpolated into the shim's source executed as code.

EVIL_DIR = 'ev"il; touch SENTINEL; #'


@pytest.fixture
def evil_repo(tmp_path):
    """A repo whose PATH carries shell metacharacters, plus the sentinel an injection
    would create. Both live under tmp_path — nothing outside is ever touched."""
    sentinel = tmp_path / "pwned"
    root = mk_repo(tmp_path / EVIL_DIR.replace("SENTINEL", str(sentinel)))
    return root, sentinel


def test_r6f2_metacharacter_repo_path_does_not_execute_in_the_hil_read(evil_repo):
    root, sentinel = evil_repo
    notes: list[str] = []
    todos = aer._todos(root, root, notes)
    assert not sentinel.exists(), f"INJECTION EXECUTED: {sentinel} was created"
    assert todos == [], "the shim must still work on a metacharacter-bearing path"
    assert notes == []


def test_r6f2_metacharacter_repo_path_does_not_execute_in_the_ledger_append(
    evil_repo, shared_ledger
):
    root, sentinel = evil_repo
    data = {
        "pr": 1202,
        "main_ci": {"commit": MERGE, "conclusion": "success"},
        "refresh_commit": REFRESH,
        "todo_for_human": [],
    }
    assert aer.append_ledger_row(root, data, "p.md") is True
    assert not sentinel.exists(), f"INJECTION EXECUTED: {sentinel} was created"
    assert "EXIT-REPORT" in shared_ledger.read_text(encoding="utf-8")


def test_r6f2_shim_sources_are_constant_strings(evil_repo, monkeypatch):
    """Structural: the `bash -c` SOURCE must carry no interpolated path — every value
    travels in argv. A source string containing the repo path is the defect itself."""
    root, _sentinel = evil_repo
    seen: list[list[str]] = []

    def spy(cmd, cwd, timeout=20):
        seen.append(list(cmd))
        # Answer the ledger-path resolution with a real path so the callers proceed to
        # their own shims — a None answer would short-circuit the append entirely and
        # leave the very call this test exists to inspect unexercised.
        if len(cmd) > 2 and "loop_status_path" in cmd[2]:
            return 0, str(root / "shared-ledger.md")
        return 0, ""

    monkeypatch.setattr(aer, "run", spy)
    aer._todos(root, root, [])
    aer.append_ledger_row(
        root, {"pr": 1, "main_ci": {}, "refresh_commit": None, "todo_for_human": []}, "p.md"
    )
    bash_calls = [c for c in seen if c[0] == "bash"]
    # 4 = ledger_path (from _todos) + _todos' own list read + ledger_path (from the
    # append) + the append's loop_log.
    assert len(bash_calls) == 4
    for cmd in bash_calls:
        source = cmd[2]
        assert str(root) not in source, "the repo path leaked into the bash SOURCE"
        assert '"$1"' in source and '"$2"' in source
        # `ledger_path` passes the two lib paths (which contain root) rather than root
        # itself, so membership is by containment, not identity.
        assert any(str(root) in a for a in cmd[3:]), "the repo path must travel as an argv value"


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
