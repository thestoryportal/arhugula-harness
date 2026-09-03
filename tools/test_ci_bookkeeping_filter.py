"""B-230 Task 1 — the CI bookkeeping fast path: classifier contract, the fenced path-set
copy, the stdlib-only witness, and the ci.yml shape the saving depends on."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import codex_context_guard as ccg
import merge_gate_log as mgl
import roadmap_status_refresh as rsr
from ci_bookkeeping_diff import BOOKKEEPING_PATHS, classify, main

_REPO = Path(__file__).resolve().parent.parent
_CI_YML = _REPO / ".github" / "workflows" / "ci.yml"
_SCRIPT = _REPO / "tools" / "ci_bookkeeping_diff.py"
_PINNED_CHECKOUT = "actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5"
_GATED_JOBS = frozenset(
    {"test", "coverage", "axis-isolation", "typecheck", "tools-test-coverage-and-codex-loop"}
)
_GATE_IF = "always() && needs.changes.outputs.bookkeeping != 'true'"


# --- classifier contract (the plan's four tests) -------------------------------------


def test_status_only_is_bookkeeping():
    assert classify([".harness/roadmap_status.md"]) is True


def test_gate_rows_only_is_bookkeeping():
    assert classify([".harness/merge-gate-log.jsonl", ".harness/merge-gate-log.md"]) is True


def test_any_other_file_is_not():
    assert classify([".harness/roadmap_status.md", "harness-cp/src/x.py"]) is False


def test_empty_diff_raises():
    with pytest.raises(ValueError):
        classify([])


# --- the fenced copy: every owner's set is inside ours --------------------------------


def test_owner_path_sets_are_subsets_of_the_allowlist():
    # merge_gate_log owns the gate-row pair; roadmap_status_refresh and the context guard
    # own the terminating-refresh file set. The classifier cannot import them (stdlib-only
    # process), so this is the fence on its copy.
    refresh_only = rsr._REFRESH_ONLY_FILE_SET  # pyright: ignore[reportPrivateUsage]
    assert mgl.GATE_ROW_FILES <= BOOKKEEPING_PATHS
    assert refresh_only <= BOOKKEEPING_PATHS
    assert frozenset().union(*ccg.TERMINATING_REFRESH_FILE_SETS) <= BOOKKEEPING_PATHS
    # and nothing else: the allowlist is exactly the union of what the owners write
    assert BOOKKEEPING_PATHS == mgl.GATE_ROW_FILES | refresh_only


# --- CLI contract over a real git range ---------------------------------------------


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        [
            "git",
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@example.invalid",
            "-c",
            "commit.gpgsign=false",
            *args,
        ],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _repo_with_two_commits(tmp_path: Path) -> tuple[Path, str, str]:
    _git(tmp_path, "init", "-q", "-b", "main")
    (tmp_path / ".harness").mkdir()
    (tmp_path / ".harness" / "roadmap_status.md").write_text("v1\n")
    (tmp_path / "code.py").write_text("x = 1\n")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "base")
    base = _git(tmp_path, "rev-parse", "HEAD")
    (tmp_path / ".harness" / "roadmap_status.md").write_text("v2\n")
    _git(tmp_path, "commit", "-q", "-am", "refresh")
    head = _git(tmp_path, "rev-parse", "HEAD")
    return tmp_path, base, head


def _run_script(cwd: Path, *argv: str, isolated: bool) -> subprocess.CompletedProcess[str]:
    # -S disables site-packages: the script must run with the stdlib alone, exactly as
    # the `changes` job's no-uv /usr/bin/python3 will run it.
    flags = ["-S"] if isolated else []
    return subprocess.run(
        [sys.executable, *flags, str(_SCRIPT), *argv],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def test_cli_status_only_range_prints_true_under_stdlib_only_python(tmp_path: Path):
    repo, base, head = _repo_with_two_commits(tmp_path)
    p = _run_script(repo, base, head, isolated=True)
    assert p.returncode == 0, p.stderr
    assert p.stdout == "bookkeeping=true\n"


def test_cli_code_change_prints_false(tmp_path: Path):
    repo, base, _ = _repo_with_two_commits(tmp_path)
    (repo / "code.py").write_text("x = 2\n")
    _git(repo, "commit", "-q", "-am", "code")
    head = _git(repo, "rev-parse", "HEAD")
    p = _run_script(repo, base, head, isolated=False)
    assert p.returncode == 0, p.stderr
    assert p.stdout == "bookkeeping=false\n"


def test_cli_rename_onto_bookkeeping_path_is_not_bookkeeping(tmp_path: Path):
    # A pure rename `code.py -> .harness/merge-gate-log.md` (identical content, destination
    # absent at base). Premise, asserted so the witness is self-proving: with git's default
    # rename detection `--name-only` lists only the destination, so the whole range looks
    # bookkeeping-only and would skip pytest; --no-renames lists the deletion too.
    repo, base, _ = _repo_with_two_commits(tmp_path)
    (repo / ".harness" / "merge-gate-log.md").write_text((repo / "code.py").read_text())
    (repo / "code.py").unlink()
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "rename onto a gate-log path")
    head = _git(repo, "rev-parse", "HEAD")
    with_renames = _git(repo, "diff", "--name-only", "-M", f"{base}...{head}").splitlines()
    assert ".harness/merge-gate-log.md" in with_renames and "code.py" not in with_renames
    assert set(with_renames) <= BOOKKEEPING_PATHS
    p = _run_script(repo, base, head, isolated=False)
    assert p.returncode == 0, p.stderr
    assert p.stdout == "bookkeeping=false\n"


def test_cli_empty_diff_exits_2_with_empty_stdout(tmp_path: Path):
    repo, _, head = _repo_with_two_commits(tmp_path)
    p = _run_script(repo, head, head, isolated=False)
    assert p.returncode == 2
    assert p.stdout == ""
    assert "empty diff" in p.stderr


def test_cli_unresolvable_sha_exits_2_with_empty_stdout(tmp_path: Path):
    repo, base, _ = _repo_with_two_commits(tmp_path)
    p = _run_script(repo, base, "0" * 40, isolated=False)
    assert p.returncode == 2
    assert p.stdout == ""
    assert "git diff failed" in p.stderr


def test_main_rejects_wrong_arity(capsys: pytest.CaptureFixture[str]):
    assert main(["only-one"]) == 2
    assert capsys.readouterr().out == ""


# --- ci.yml shape: the gate the saving depends on ------------------------------------


def _jobs() -> dict[str, dict[str, Any]]:
    ci: dict[str, Any] = yaml.safe_load(_CI_YML.read_text())
    return ci["jobs"]


def _steps(job: dict[str, Any]) -> list[dict[str, Any]]:
    return job["steps"]


def test_gated_jobs_need_changes_and_carry_the_always_guard():
    jobs = _jobs()
    for name in _GATED_JOBS:
        assert jobs[name]["needs"] == "changes", name
        assert jobs[name]["if"] == _GATE_IF, name


def test_changes_job_is_pinned_and_has_no_uv_setup():
    changes = _jobs()["changes"]
    uses = [str(s.get("uses", "")) for s in _steps(changes)]
    assert any(u.startswith(_PINNED_CHECKOUT) for u in uses)
    assert not any("setup-uv" in u for u in uses)
    assert changes["outputs"]["bookkeeping"] == "${{ steps.classify.outputs.bookkeeping }}"
    classify_step = next(s for s in _steps(changes) if s.get("id") == "classify")
    assert classify_step["shell"] == "bash"
    assert 'tee -a "$GITHUB_OUTPUT"' in classify_step["run"]


def test_gate_log_consistency_is_unconditional_and_blocking():
    job = _jobs()["gate-log-consistency"]
    assert "if" not in job and "needs" not in job
    assert str(job["name"]).endswith("— blocking")
    assert any("tools/merge_gate_log.py check" in str(s.get("run", "")) for s in _steps(job))
