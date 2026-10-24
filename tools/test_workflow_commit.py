"""WO-U06 / WP-04 — proportionate trial commits without duplicate unchanged local gates
(spec WS-07, WS-08 §10.1-10.2; verification WT-10, WT-11 local part).

A trial commit is found in any command spelling and routed by its own repository. It
inspects the actual index, refuses commit modes that record anything else, and runs the
proportionate local set from the repository root: Ruff and the behavior test for changed
Python, the CI record producers and parsers for records, and the named risk expansion —
never whole-project Pyright or closeout. A staged path whose worktree bytes differ from
the index, or a dirty path among a check's inputs, holds. An identical check runs once;
any material input change runs it again; failed, unavailable or corrupt results never
pass. An unreadable policy holds enrolled work. Legacy work keeps the existing gate.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
from collections.abc import Sequence
from pathlib import Path

import pytest

from tools import workflow_boundaries as wb
from tools import workflow_commit as wc
from tools.workflow_policy import PolicyDefect, WorkflowPolicy, load_policy

UNIT = "arhugula-harness-trial-193.7x7.nff"
CREATED = "2026-10-24T00:00:00.000000Z"
REPO_ROOT = Path(__file__).resolve().parent.parent


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
    for name, text in {"a.py": "x = 1\n", "test_a.py": "", "test_b.py": ""}.items():
        (root / "tools" / name).write_text(text)
    git(root, "add", ".")
    git(root, "commit", "-qm", "base")
    monkeypatch.setattr(wc, "CHECK_ROOT", tmp_path / "checks")
    return root


class FakeRuff:
    """Runner double. Ruff finds LINT_BAD in its stdin subject, the JSON parser rejects
    malformed stdin, and every other check passes unless `exit_code` overrides it."""

    def __init__(self, version: bytes = b"ruff 0.0.1", exit_code: int | None = None) -> None:
        self.version, self.exit_code = version, exit_code
        self.checks: list[list[str]] = []
        self.cwds: list[Path] = []

    def __call__(
        self, argv: Sequence[str], stdin: bytes, cwd: Path, timeout: float
    ) -> subprocess.CompletedProcess[bytes]:
        if argv[-1] == "--version":
            return subprocess.CompletedProcess(argv, 0, self.version + b"\n", b"")
        self.checks.append(list(argv))
        self.cwds.append(cwd)
        code = int(b"LINT_BAD" in stdin)
        if "json.tool" in argv:
            try:
                json.loads(stdin)
            except ValueError:
                code = 1
        code = self.exit_code if self.exit_code is not None else code
        return subprocess.CompletedProcess(argv, code, b"finding" if code else b"", b"")


def ruff_runs(fake: FakeRuff) -> list[list[str]]:
    return [argv for argv in fake.checks if "ruff" in argv]


def commit(root: Path, ruff: FakeRuff) -> wc.Outcome:
    return wc.commit_outcome(root, TRIAL, created_at=CREATED, run=ruff)


def stage(root: Path, path: str, text: str) -> None:
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text)
    git(root, "add", path)


# --- staged scope ------------------------------------------------------------------------


def test_parse_staged_excludes_deletions_and_names_divergent_paths() -> None:
    staged = wc.parse_staged(
        b"M\0a.py\0D\0gone.py\0A\0b.md\0", b"a.py\0other.py\0", b"new.txt\0", b"a.py\0b.md\0"
    )
    assert staged == wc.StagedScope(
        ("a.py", "b.md"),
        ("gone.py",),
        ("a.py",),
        ("a.py", "new.txt", "other.py"),
        ("a.py", "b.md"),
    )


def test_staged_divergence_requires_verified_index(repo: Path) -> None:
    stage(repo, "tools/a.py", "x = 2\n")
    (repo / "tools" / "a.py").write_text("x = 3  # LINT_BAD\n")
    ruff = FakeRuff()
    outcome = commit(repo, ruff)
    assert (outcome.result, outcome.reasons) == ("held", ("binding_stale",))
    assert ruff.checks == []


def test_unrelated_unstaged_work_does_not_block_the_commit(repo: Path) -> None:
    stage(repo, "tools/b.py", "y = 1\n")
    (repo / "notes").mkdir()
    (repo / "notes" / "scratch.txt").write_text("draft\n")
    assert commit(repo, FakeRuff()).result == "passed"


def test_dirty_path_among_a_checks_inputs_holds(repo: Path) -> None:
    """F5 soundness: the behavior test reads the working tree, so an unstaged edit in
    its domain would make the receipt describe bytes the commit does not record."""
    stage(repo, "tools/b.py", "y = 1\n")
    (repo / "tools" / "a.py").write_text("x = 9\n")
    outcome = commit(repo, FakeRuff())
    assert (outcome.result, outcome.reasons) == ("held", ("binding_stale",))
    assert any("tools/a.py" in line for line in outcome.detail)


def test_checker_reads_staged_bytes_after_a_later_worktree_edit(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The commit records the index, so an edit after observation does not change what
    the checker sees."""
    stage(repo, "tools/b.py", "y = 1\n")
    observe = wc.observe_staged

    def observed_then_edited(root: Path) -> wc.StagedScope:
        scope = observe(root)
        (root / "tools" / "b.py").write_text("y = 1  # LINT_BAD\n")
        return scope

    monkeypatch.setattr(wc, "observe_staged", observed_then_edited)
    ruff = FakeRuff()
    assert commit(repo, ruff) == wc.PASSED
    assert len(ruff_runs(ruff)) == 2


def test_commit_checks_the_staged_bytes_not_the_worktree(repo: Path) -> None:
    stage(repo, "tools/a.py", "x = 2  # LINT_BAD\n")
    outcome = commit(repo, FakeRuff())
    assert (outcome.result, outcome.reasons) == ("failed", ("check_failed",))


# --- proportionate checks ----------------------------------------------------------------


def test_record_only_commit_avoids_unrelated_pyright(repo: Path) -> None:
    stage(repo, "docs/note.md", "record\n")
    ruff = FakeRuff()
    assert commit(repo, ruff) == wc.PASSED
    expected = [["uv", "run", "--quiet", "python", *p] for p in wc.RECORD_PRODUCERS]
    assert ruff.checks == expected  # the record producers, and nothing else


def test_malformed_record_fails_its_parser(repo: Path) -> None:
    """F5: a record-only commit runs its record checks instead of passing unchecked."""
    stage(repo, "record.json", "{not json")
    outcome = commit(repo, FakeRuff())
    assert (outcome.result, outcome.reasons) == ("failed", ("check_failed",))
    assert any("record.json" in line for line in outcome.detail)


def test_deletion_runs_the_record_producers(repo: Path) -> None:
    git(repo, "rm", "-q", "tools/test_a.py")
    ruff = FakeRuff()
    assert commit(repo, ruff) == wc.PASSED
    assert [argv[4:] for argv in ruff.checks] == [list(p) for p in wc.RECORD_PRODUCERS]


def test_record_producers_are_the_ones_ci_runs() -> None:
    ci = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text()
    for producer in wc.RECORD_PRODUCERS:
        assert f"uv run python {' '.join(producer)}" in ci, producer


def test_source_checkpoint_runs_changed_subject_ruff_and_its_behavior_test(repo: Path) -> None:
    stage(repo, "tools/b.py", "y = 1\n")
    ruff = FakeRuff()
    assert commit(repo, ruff) == wc.PASSED
    commands = [" ".join(argv) for argv in ruff.checks]
    assert all("pyright" not in c for c in commands)
    assert {argv[argv.index("ruff") + 1] for argv in ruff_runs(ruff)} == {"check", "format"}
    assert all("tools/b.py" in c for c in map(" ".join, ruff_runs(ruff)))
    assert [c for c in commands if "pytest" in c] == [
        "uv run --quiet pytest -q -p no:cacheprovider tools/test_b.py"
    ]


def test_source_without_a_behavior_test_holds(repo: Path) -> None:
    """F5: changed Python needs its narrowest behavior test; none means pending."""
    stage(repo, "tools/c.py", "z = 1\n")
    outcome = commit(repo, FakeRuff())
    assert (outcome.result, outcome.reasons) == ("held", ("check_pending",))


def test_hook_subject_expands_to_the_named_risk_set(repo: Path) -> None:
    """F5: a named higher-risk subject adds its explicit local tests."""
    stage(repo, "tools/hooks/test_gate.sh", "true\n")
    ruff = FakeRuff()
    assert commit(repo, ruff) == wc.PASSED
    tests = [argv[-1] for argv in ruff.checks]
    assert tests == ["tools/hooks/test_gate.sh", "tools/test_codex_workflow_parity.py"]


def test_checks_run_from_the_observed_root(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """F4: the checker resolves config and paths from the root the manifest hashed."""
    monkeypatch.chdir(tmp_path)
    stage(repo, "tools/b.py", "y = 1\n")
    ruff = FakeRuff()
    assert commit(repo, ruff) == wc.PASSED
    assert ruff.cwds and set(ruff.cwds) == {repo}
    assert all(argv[argv.index("--config") + 1] == "pyproject.toml" for argv in ruff_runs(ruff))


def test_exhausted_budget_holds_instead_of_racing_the_hook_timeout(repo: Path) -> None:
    stage(repo, "tools/b.py", "y = 1\n")
    ticks = iter(range(0, 10_000, 1_000))
    outcome = wc.commit_outcome(
        repo, TRIAL, created_at=CREATED, run=FakeRuff(), clock=lambda: float(next(ticks))
    )
    assert (outcome.result, outcome.reasons) == ("held", ("check_pending",))


# --- reuse -------------------------------------------------------------------------------


def test_unchanged_checks_execute_once(repo: Path) -> None:
    stage(repo, "tools/b.py", "y = 1\n")
    ruff = FakeRuff()
    assert commit(repo, ruff) == wc.PASSED
    assert commit(repo, ruff) == wc.PASSED
    assert len(ruff.checks) == 3


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
    assert len(ruff_runs(ruff)) == 4


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
    assert len(ruff_runs(second)) == 2


def test_failed_result_is_never_reused(repo: Path) -> None:
    stage(repo, "tools/b.py", "y = 1  # LINT_BAD\n")
    ruff = FakeRuff()
    assert commit(repo, ruff).result == "failed"
    assert commit(repo, ruff).result == "failed"
    assert len(ruff_runs(ruff)) == 4


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


def _bind_arc(root: Path) -> None:
    (root / ".harness").mkdir(exist_ok=True)
    (root / ".harness" / "codex_loop_state.json").write_text(json.dumps({"arc_id": "u06"}))


def test_unbound_or_inactive_worktree_keeps_legacy(repo: Path) -> None:
    assert wc.worktree_profile(repo) == wc.Legacy()
    _bind_arc(repo)
    assert wc.worktree_profile(repo) == wc.Legacy()


def test_unreadable_policy_holds_an_arc_bound_worktree(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """F3: enrollment that cannot be read is not evidence of legacy work."""
    monkeypatch.setattr(wc, "observe_policy", lambda: PolicyDefect("unreadable"))
    assert wc.worktree_profile(repo) == wc.Legacy()  # no arc: nothing to enroll
    _bind_arc(repo)
    assert isinstance(wc.worktree_profile(repo), wc.Held)


def _no_aliases(_root: Path, _name: str) -> str | None:
    return None


@pytest.mark.parametrize(
    ("command", "args"),
    [
        ("git commit -m x", ("-m", "x")),
        ("git -C {repo} commit -m x", ("-m", "x")),
        ("cd {repo} && git commit -m x", ("-m", "x")),
        ("(cd {repo}; git commit -qm x) && ls", ("-qm", "x")),
        ("rtk /usr/bin/git --no-pager commit -m x 2>&1 | tail", ("-m", "x")),
        ("env A=1 git commit -m x", ("-m", "x")),
        ("echo $(git commit -m x)", ("-m", "x")),
        ("git commit -F - <<'EOF'\nsubject; git push\nEOF", ("-F", "-")),
    ],
)
def test_commit_spellings_are_found_with_their_directory(
    repo: Path, tmp_path: Path, command: str, args: tuple[str, ...]
) -> None:
    """F1: every supported spelling reaches the gate, rooted where git runs."""
    cwd = repo if command.startswith(("git commit", "rtk", "env", "echo")) else tmp_path
    commits = wc.read_commits(command.format(repo=repo), cwd, _no_aliases)
    assert commits == (wc.CommitCommand(repo, args),)


def test_alias_resolves_to_its_commit(repo: Path) -> None:
    aliases = {"ci": "commit -q", "c2": "ci"}
    commits = wc.read_commits("git c2 -m x", repo, lambda _r, name: aliases.get(name))
    assert commits == (wc.CommitCommand(repo, ("-q", "-m", "x")),)


@pytest.mark.parametrize(
    "command",
    [
        "GIT_DIR=elsewhere git commit -m x",
        "git -c alias.ci=commit ci -m x",
        "git --git-dir=x commit -m x",
        'bash -c "git commit -m x"',
        'echo "$(git commit -m x)"',
        "timeout 5 git commit -m x",
        "cd $TARGET && git commit -m x",
        "git commit -F - <<EOF\nnever ends",
        "git commit -m 'unbalanced",
    ],
)
def test_commit_effect_that_cannot_be_read_is_unreadable(repo: Path, command: str) -> None:
    assert isinstance(wc.read_commits(command, repo, _no_aliases), wc.Unreadable)


@pytest.mark.parametrize(
    "command", ["git status", "ls -la", "git log --oneline | head", "echo commit"]
)
def test_commands_without_a_commit_make_none(repo: Path, command: str) -> None:
    assert wc.read_commits(command, repo, _no_aliases) == ()


@pytest.mark.parametrize(
    "args",
    [("-am", "x"), ("-a", "-m", "x"), ("--only", "a.py"), ("-m", "x", "a.py"), ("-i", "a.py"),
     ("--patch",), ("--pathspec-from-file=f",), ("-m", "x", "--", "a.py"), ("--no-verify",)],
)  # fmt: skip
def test_commit_modes_that_change_what_is_recorded_are_refused(args: tuple[str, ...]) -> None:
    """F2: only an explicit-staging commit records exactly the inspected index."""
    assert wc.commit_selection(args) is not None


@pytest.mark.parametrize(
    "args",
    [(), ("-m", "x"), ("-qm", "x"), ("--amend", "--no-edit"), ("-F", "-"), ("--message=x",),
     ("-s", "-m", "x")],
)  # fmt: skip
def test_explicit_staging_commit_modes_are_accepted(args: tuple[str, ...]) -> None:
    assert wc.commit_selection(args) is None


def _trial_at(repo: Path):  # type: ignore[no-untyped-def]
    return lambda root: TRIAL if root == repo else wc.Legacy()


def test_commit_all_cannot_record_unchecked_worktree_bytes(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """F2 reproduction: `-am` would commit an unstaged invalid file the index lacks."""
    monkeypatch.setattr(wc, "worktree_profile", _trial_at(repo))
    (repo / "tools" / "a.py").write_text("x = (\n")
    outcome = wc.command_outcome("git commit -am x", repo, created_at=CREATED, run=FakeRuff())
    assert (outcome.result, outcome.reasons) == ("held", ("invalid_input",))


@pytest.mark.parametrize(
    "spelling", ["git -C {repo} commit -m x", "cd {repo}/tools && git commit -m x"]
)
def test_commit_spelled_elsewhere_is_gated_by_its_repository(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, spelling: str
) -> None:
    """F1 reproduction: neither the cwd nor a subdirectory hides the trial worktree."""
    monkeypatch.setattr(wc, "worktree_profile", _trial_at(repo))
    stage(repo, "tools/b.py", "y = 1  # LINT_BAD\n")
    command = spelling.format(repo=repo)
    outcome = wc.command_outcome(command, tmp_path, created_at=CREATED, run=FakeRuff())
    assert (outcome.result, outcome.reasons) == ("failed", ("check_failed",))


def test_unreadable_command_holds_trial_work_only(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(wc, "worktree_profile", _trial_at(repo))
    command = 'bash -c "git commit -m x"'
    assert wc.command_outcome(command, repo, created_at=CREATED).result == "held"
    assert wc.command_outcome(command, tmp_path, created_at=CREATED) == wc.PASSED


def _adapter():  # type: ignore[no-untyped-def]
    path = REPO_ROOT / ".codex" / "hooks" / "codex_hook_adapter.py"
    spec = importlib.util.spec_from_file_location("codex_hook_adapter", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _payload(root: Path, command: str = "git commit -m x") -> dict[str, object]:
    return {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(root)}


def _recording(adapter, calls: list[list[str]]):  # type: ignore[no-untyped-def]
    def run(args, **_):  # type: ignore[no-untyped-def]
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, "", "")

    return run


def _trial_adapter(monkeypatch: pytest.MonkeyPatch, profile: object, ruff: FakeRuff):  # type: ignore[no-untyped-def]
    adapter, calls = _adapter(), []
    monkeypatch.setattr(adapter, "run_bounded", _recording(adapter, calls))
    monkeypatch.setattr(adapter.workflow_commit, "worktree_profile", profile)
    gate = adapter.workflow_commit.commit_outcome
    monkeypatch.setattr(
        adapter.workflow_commit, "commit_outcome", lambda *a, **k: gate(*a, **{**k, "run": ruff})
    )
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    return adapter, calls


def test_legacy_commit_keeps_the_existing_pyright_gate(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter, calls = _adapter(), []
    monkeypatch.setattr(adapter, "run_bounded", _recording(adapter, calls))
    monkeypatch.delenv("CLAUDE_PROJECT_DIR", raising=False)
    assert adapter.pre_commit(_payload(repo)) == 0
    assert calls == [["uv", "run", "pyright"], ["git", "rev-parse", "--show-toplevel"]]


def test_commit_does_not_require_release_closeout(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ruff = FakeRuff()
    adapter, calls = _trial_adapter(monkeypatch, _trial_at(repo), ruff)
    stage(repo, "tools/b.py", "y = 1\n")
    assert adapter.pre_commit(_payload(repo)) == 0
    assert calls == []  # no Pyright, no closeout, no suite
    assert len(ruff_runs(ruff)) == 2


@pytest.mark.parametrize(
    "profile", [wc.Held(("authority_unavailable",)), "failed"], ids=["held", "failed"]
)
def test_trial_commit_blocks_on_a_held_or_failed_outcome(
    repo: Path, monkeypatch: pytest.MonkeyPatch, profile: object
) -> None:
    chosen = TRIAL if profile == "failed" else profile
    adapter, calls = _trial_adapter(monkeypatch, lambda _root: chosen, FakeRuff())
    stage(repo, "tools/b.py", "y = 1  # LINT_BAD\n")
    assert adapter.pre_commit(_payload(repo)) == 2
    assert calls == []  # never falls through to the legacy gate


def test_adapter_gates_a_commit_spelled_from_another_directory(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter, calls = _trial_adapter(monkeypatch, _trial_at(repo), FakeRuff())
    stage(repo, "tools/b.py", "y = 1  # LINT_BAD\n")
    assert adapter.pre_commit(_payload(tmp_path, f"cd {repo} && git commit -m x")) == 2
    assert adapter.pre_commit(_payload(repo, "git status")) == 0
    assert calls == []


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
    assert ruff_runs(ruff) == []
