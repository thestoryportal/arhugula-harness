"""WO-U06 / WP-04 — proportionate trial commits without duplicate unchanged local gates
(spec WS-07, WS-08 §10.1-10.2; verification WT-10, WT-11 local part).

A trial commit inspects the actual index and checks only its changed Python subjects —
never whole-project Pyright or closeout — and a record-only commit runs no checker. A
staged path whose worktree bytes differ from the index holds. An identical check runs
once; any material input change runs it again; failed, unavailable or corrupt results
never pass. Legacy work keeps the existing commit gate exactly.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

from tools import workflow_boundaries as wb
from tools import workflow_commit as wc
from tools.workflow_policy import WorkflowPolicy, load_policy

UNIT = "arhugula-harness-trial-193.7x7.nff"
CREATED = "2026-10-24T00:00:00.000000Z"


def _policy() -> WorkflowPolicy:
    policy = load_policy(wb.POLICY_PATH.read_bytes())
    assert isinstance(policy, WorkflowPolicy)
    return policy


TRIAL = wc.Trial(UNIT, "thestoryportal/arhugula-harness", _policy())


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.email", "t@t.t")
    git(root, "config", "user.name", "t")
    (root / "pyproject.toml").write_text("[tool.ruff]\n")
    (root / "tools").mkdir()
    (root / "tools" / "a.py").write_text("x = 1\n")
    git(root, "add", "pyproject.toml", "tools/a.py")
    git(root, "commit", "-qm", "base")
    monkeypatch.setattr(wc, "CHECK_ROOT", tmp_path / "checks")
    return root


class FakeRuff:
    """Ruff double: a subject containing LINT_BAD has findings; `--version` names it."""

    def __init__(self, version: bytes = b"ruff 0.0.1", exit_code: int | None = None) -> None:
        self.version, self.exit_code = version, exit_code
        self.checks: list[list[str]] = []

    def __call__(self, argv: list[str], stdin: bytes) -> subprocess.CompletedProcess[bytes]:
        if argv[-1] == "--version":
            return subprocess.CompletedProcess(argv, 0, self.version + b"\n", b"")
        self.checks.append(argv)
        code = self.exit_code if self.exit_code is not None else int(b"LINT_BAD" in stdin)
        return subprocess.CompletedProcess(argv, code, b"finding" if code else b"", b"")


def commit(root: Path, ruff: FakeRuff) -> wc.Outcome:
    return wc.commit_outcome(root, TRIAL, created_at=CREATED, run=ruff)


def stage(root: Path, path: str, text: str) -> None:
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text)
    git(root, "add", path)


# --- staged scope ------------------------------------------------------------------------


def test_parse_staged_excludes_deletions_and_names_divergent_paths() -> None:
    staged = wc.parse_staged(b"M\0a.py\0D\0gone.py\0A\0b.md\0", b"a.py\0other.py\0")
    assert staged == wc.StagedScope(("a.py", "b.md"), ("a.py",))


def test_staged_divergence_requires_verified_index(repo: Path) -> None:
    stage(repo, "tools/a.py", "x = 2\n")
    (repo / "tools" / "a.py").write_text("x = 3  # LINT_BAD\n")
    ruff = FakeRuff()
    outcome = commit(repo, ruff)
    assert (outcome.result, outcome.reasons) == ("held", ("binding_stale",))
    assert ruff.checks == []


def test_unrelated_unstaged_work_does_not_block_the_commit(repo: Path) -> None:
    stage(repo, "tools/b.py", "y = 1\n")
    (repo / "tools" / "a.py").write_text("x = 9  # LINT_BAD\n")
    assert commit(repo, FakeRuff()).result == "passed"


def test_commit_checks_the_staged_bytes_not_the_worktree(repo: Path) -> None:
    stage(repo, "tools/a.py", "x = 2  # LINT_BAD\n")
    outcome = commit(repo, FakeRuff())
    assert (outcome.result, outcome.reasons) == ("failed", ("check_failed",))


# --- proportionate checks ----------------------------------------------------------------


def test_record_only_commit_avoids_unrelated_pyright(repo: Path) -> None:
    stage(repo, "docs/note.md", "record\n")
    ruff = FakeRuff()
    assert commit(repo, ruff) == wc.PASSED
    assert ruff.checks == []


def test_source_checkpoint_runs_only_changed_subject_ruff(repo: Path) -> None:
    stage(repo, "tools/b.py", "y = 1\n")
    ruff = FakeRuff()
    assert commit(repo, ruff) == wc.PASSED
    commands = [" ".join(argv) for argv in ruff.checks]
    assert len(commands) == 2
    assert all("tools/b.py" in c and "pyright" not in c and "pytest" not in c for c in commands)
    assert {argv[argv.index("ruff") + 1] for argv in ruff.checks} == {"check", "format"}


# --- reuse -------------------------------------------------------------------------------


def test_unchanged_checks_execute_once(repo: Path) -> None:
    stage(repo, "tools/b.py", "y = 1\n")
    ruff = FakeRuff()
    assert commit(repo, ruff) == wc.PASSED
    assert commit(repo, ruff) == wc.PASSED
    assert len(ruff.checks) == 2


def test_stop_reuses_a_result_for_identical_unchanged_subjects(repo: Path) -> None:
    (repo / "tools" / "a.py").write_text("x = 2\n")
    ruff = FakeRuff()
    for _ in range(2):
        assert wc.stop_outcome(repo, TRIAL, created_at=CREATED, run=ruff) == wc.PASSED
    assert len(ruff.checks) == 2


def _make_executable(root: Path) -> None:
    (root / "tools" / "b.py").chmod(0o755)
    git(root, "add", "tools/b.py")


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(lambda root: stage(root, "tools/b.py", "y = 2\n"), id="subject-bytes"),
        pytest.param(lambda root: stage(root, "pyproject.toml", "[tool.ruff]\n# x\n"), id="config"),
        pytest.param(_make_executable, id="mode"),
    ],
)
def test_material_change_runs_the_check_again(repo: Path, mutate) -> None:  # type: ignore[no-untyped-def]
    stage(repo, "tools/b.py", "y = 1\n")
    ruff = FakeRuff()
    assert commit(repo, ruff) == wc.PASSED
    mutate(repo)
    assert commit(repo, ruff) == wc.PASSED
    assert len(ruff.checks) == 4


def test_head_move_runs_the_check_again(repo: Path) -> None:
    (repo / "tools" / "a.py").write_text("x = 2\n")
    ruff = FakeRuff()
    wc.stop_outcome(repo, TRIAL, created_at=CREATED, run=ruff)
    stage(repo, "docs/note.md", "record\n")
    git(repo, "commit", "-qm", "record")
    wc.stop_outcome(repo, TRIAL, created_at=CREATED, run=ruff)
    assert len(ruff.checks) == 4


def test_checker_version_change_runs_the_check_again(repo: Path) -> None:
    stage(repo, "tools/b.py", "y = 1\n")
    first, second = FakeRuff(), FakeRuff(version=b"ruff 0.0.2")
    commit(repo, first)
    commit(repo, second)
    assert len(second.checks) == 2


def test_failed_result_is_never_reused(repo: Path) -> None:
    stage(repo, "tools/b.py", "y = 1  # LINT_BAD\n")
    ruff = FakeRuff()
    assert commit(repo, ruff).result == "failed"
    assert commit(repo, ruff).result == "failed"
    assert len(ruff.checks) == 4


def test_corrupt_receipt_is_never_reused_as_a_pass(repo: Path) -> None:
    stage(repo, "tools/b.py", "y = 1\n")
    commit(repo, FakeRuff())
    for receipt in wc.CHECK_ROOT.glob("*.json"):
        receipt.write_bytes(b"{}")
    ruff = FakeRuff()
    outcome = commit(repo, ruff)
    assert ruff.checks and outcome.result != "passed"


@pytest.mark.parametrize("code", [2, 124, 127])
def test_unavailable_checker_is_not_a_pass(repo: Path, code: int) -> None:
    stage(repo, "tools/b.py", "y = 1\n")
    outcome = commit(repo, FakeRuff(exit_code=code))
    assert (outcome.result, outcome.reasons) == ("held", ("check_pending",))
    assert list(wc.CHECK_ROOT.glob("*.json")) == []


# --- routing -----------------------------------------------------------------------------


def test_unbound_or_inactive_worktree_keeps_legacy(repo: Path) -> None:
    assert wc.worktree_profile(repo) == wc.Legacy()
    (repo / ".harness").mkdir()
    (repo / ".harness" / "codex_loop_state.json").write_text(json.dumps({"arc_id": "u06"}))
    assert wc.worktree_profile(repo) == wc.Legacy()


def _adapter():  # type: ignore[no-untyped-def]
    path = Path(__file__).resolve().parent.parent / ".codex" / "hooks" / "codex_hook_adapter.py"
    spec = importlib.util.spec_from_file_location("codex_hook_adapter", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _commit_payload(root: Path) -> dict[str, object]:
    return {"tool_name": "Bash", "tool_input": {"command": "git commit -m x"}, "cwd": str(root)}


def _recording(adapter, calls: list[list[str]]):  # type: ignore[no-untyped-def]
    def run(args, **_):  # type: ignore[no-untyped-def]
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, "", "")

    return run


def test_legacy_commit_keeps_the_existing_pyright_gate(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter, calls = _adapter(), []
    monkeypatch.setattr(adapter, "run_bounded", _recording(adapter, calls))
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    assert adapter.pre_commit(_commit_payload(repo)) == 0
    assert calls == [["uv", "run", "pyright"], ["git", "rev-parse", "--show-toplevel"]]


def test_commit_does_not_require_release_closeout(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter, calls = _adapter(), []
    monkeypatch.setattr(adapter, "run_bounded", _recording(adapter, calls))
    monkeypatch.setattr(adapter.workflow_commit, "worktree_profile", lambda _root: TRIAL)
    ruff, gate = FakeRuff(), adapter.workflow_commit.commit_outcome
    monkeypatch.setattr(
        adapter.workflow_commit, "commit_outcome", lambda *a, **k: gate(*a, **k, run=ruff)
    )
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    stage(repo, "tools/b.py", "y = 1\n")
    assert adapter.pre_commit(_commit_payload(repo)) == 0
    assert calls == []  # no Pyright, no closeout, no suite
    assert len(ruff.checks) == 2


@pytest.mark.parametrize(
    "profile", [wc.Held(("authority_unavailable",)), "failed"], ids=["held", "failed"]
)
def test_trial_commit_blocks_on_a_held_or_failed_outcome(
    repo: Path, monkeypatch: pytest.MonkeyPatch, profile: object
) -> None:
    adapter = _adapter()
    chosen = TRIAL if profile == "failed" else profile
    monkeypatch.setattr(adapter.workflow_commit, "worktree_profile", lambda _root: chosen)
    ruff, gate = FakeRuff(), adapter.workflow_commit.commit_outcome
    monkeypatch.setattr(
        adapter.workflow_commit, "commit_outcome", lambda *a, **k: gate(*a, **k, run=ruff)
    )
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    stage(repo, "tools/b.py", "y = 1  # LINT_BAD\n")
    assert adapter.pre_commit(_commit_payload(repo)) == 2


def test_stop_cli_reports_legacy_for_unbound_work(repo: Path) -> None:
    script = Path(wc.__file__)
    proc = subprocess.run(
        ["python3", str(script), "stop", "--root", str(repo)], capture_output=True, text=True
    )
    assert (proc.returncode, json.loads(proc.stdout)) == (0, {"profile": "legacy"})


def test_bytes_changed_after_observation_hold(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    stage(repo, "tools/b.py", "y = 1\n")
    monkeypatch.setattr(wc, "_subject_bytes", lambda *_: b"y = 2\n")
    ruff = FakeRuff()
    outcome = commit(repo, ruff)
    assert (outcome.result, outcome.reasons) == ("held", ("binding_stale",))
    assert ruff.checks == []
