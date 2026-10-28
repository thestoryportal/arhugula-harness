"""WO-U06 / WP-04 — proportionate trial commits without duplicate unchanged local gates
(spec WS-07, WS-08 §10.1-10.2; verification WT-10, WT-11 local part).

Git's pre-commit hook runs the trial gate for a commit however the command that makes
it is spelled (Git's own bypasses aside), and only a worktree where Git runs that hook
can select trial; real-path witnesses drive the unmodified hooks and router. The
gate holds a commit whose staging is implicit, inspects the actual index and runs the
proportionate local set: Ruff and the behavior test for changed Python, the CI record
producers and parsers for records, and the named risk expansion — never whole-project
Pyright or closeout. Checks run in a Git checkout of exactly the staged tree, so unstaged
work neither reaches nor blocks them while Git-reading checks still work; a staged path
whose worktree bytes differ from the index, or a change to the index while they run,
holds. Every check receives only the pinned environment its receipt records. An
identical check runs once; any material input change, checker identity or environment
pin included, runs it again; failed, unavailable or corrupt results never pass. An
unreadable policy holds enrolled work. Legacy work keeps the existing gates.
"""

from __future__ import annotations

import dataclasses
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

import pytest

from tools import workflow_boundaries as wb
from tools import workflow_commit as wc
from tools.workflow_policy import (
    EligibleUnit,
    PolicyDefect,
    ProfileSelection,
    WorkflowPolicy,
    load_policy,
)

UNIT = "arhugula-harness-trial-193.7x7.nff"
CREATED = "2026-10-24T00:00:00.000000Z"
REPO_ROOT = Path(__file__).resolve().parent.parent
ENV = {"HOME": "/home/t", "PATH": "/usr/bin:/bin"}


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
    malformed stdin, and every other check passes unless `exit_code` overrides it. A
    `--version` probe answers from `versions` by the program asked (`ruff`, `bash`, `uv`,
    `python`), else `version`; None means unavailable. Each check records the files its
    directory held and the environment it received."""

    def __init__(
        self, version: bytes = b"ruff 0.0.1", exit_code: int | None = None, **versions: bytes | None
    ) -> None:
        self.version, self.exit_code, self.versions = version, exit_code, versions
        self.checks: list[list[str]] = []
        self.cwds: list[Path] = []
        self.files: list[dict[str, str]] = []
        self.environments: list[dict[str, str]] = []

    def __call__(
        self,
        argv: Sequence[str],
        stdin: bytes,
        cwd: Path,
        timeout: float,
        environment: Mapping[str, str],
    ) -> subprocess.CompletedProcess[bytes]:
        if argv[-1] in ("--version", wc.ENVIRONMENT_PROBE):
            program = "python" if argv[-1] == wc.ENVIRONMENT_PROBE else argv[-2]
            answer = self.versions.get(program, self.version)
            code, out = (127, b"") if answer is None else (0, answer + b"\n")
            return subprocess.CompletedProcess(argv, code, out, b"")
        self.checks.append(list(argv))
        self.cwds.append(cwd)
        self.environments.append(dict(environment))
        self.files.append(
            {
                str(path.relative_to(cwd)): path.read_text()
                for path in cwd.rglob("*")
                if path.is_file() and ".git" not in path.relative_to(cwd).parts
            }
        )
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


def commit(root: Path, ruff: FakeRuff, environment: Mapping[str, str] = ENV) -> wc.Outcome:
    return wc.commit_outcome(root, TRIAL, created_at=CREATED, environment=environment, run=ruff)


def stage(root: Path, path: str, text: str) -> None:
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text)
    git(root, "add", path)


# --- staged scope ------------------------------------------------------------------------


def test_parse_staged_excludes_deletions_and_names_divergent_paths() -> None:
    stage = b"100644 aa 0\ta.py\x00100644 bb 0\tb.md\x00"
    staged = wc.parse_staged(b"M\0a.py\0D\0gone.py\0A\0b.md\0", b"a.py\0other.py\0", stage)
    assert staged == wc.StagedScope(
        ("a.py", "b.md"),
        ("gone.py",),
        ("a.py",),
        ("a.py", "b.md"),
        hashlib.sha256(stage).hexdigest(),
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


def test_checks_read_an_index_snapshot_not_the_worktree(repo: Path) -> None:
    """F5/F6: checks that read files see exactly the index, so unstaged or untracked work
    in their domain neither reaches nor blocks them."""
    stage(repo, "tools/b.py", "y = 1\n")
    (repo / "tools" / "a.py").write_text("x = 9\n")
    (repo / "tools" / "scratch.py").write_text("draft\n")
    ruff = FakeRuff()
    assert commit(repo, ruff) == wc.PASSED
    assert ruff.files and repo not in ruff.cwds
    for files in ruff.files:
        assert (files["tools/a.py"], files["tools/b.py"]) == ("x = 1\n", "y = 1\n")
        assert "tools/scratch.py" not in files


def test_record_commit_ignores_unrelated_untracked_work(repo: Path) -> None:
    """F5 reproduction: an unrelated preserved file does not block a record commit."""
    stage(repo, "README.md", "record\n")
    (repo / "unrelated.txt").write_text("preserved\n")
    assert commit(repo, FakeRuff()) == wc.PASSED


def test_worktree_edit_while_checks_run_holds(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """F6 reproduction: the staged bytes are checked, and a worktree edit to a staged
    path after observation holds once the checks finish."""
    stage(repo, "tools/b.py", "y = 1\n")
    observe = wc.observe_staged

    def observed_then_edited(root: Path) -> wc.StagedScope:
        scope = observe(root)
        (root / "tools" / "b.py").write_text("y = 1  # LINT_BAD\n")
        return scope

    monkeypatch.setattr(wc, "observe_staged", observed_then_edited)
    ruff = FakeRuff()
    outcome = commit(repo, ruff)
    assert (outcome.result, outcome.reasons) == ("held", ("binding_stale",))
    assert len(ruff_runs(ruff)) == 2  # Ruff read the index, not the edit


def test_index_change_while_checks_run_holds(repo: Path) -> None:
    """F6: a restage during the checks voids what they verified."""
    stage(repo, "tools/b.py", "y = 1\n")
    ruff = FakeRuff()

    def restaging(
        argv: Sequence[str], stdin: bytes, cwd: Path, timeout: float, env: Mapping[str, str]
    ) -> subprocess.CompletedProcess[bytes]:
        if "pytest" in argv:
            stage(repo, "tools/b.py", "y = 2\n")
        return ruff(argv, stdin, cwd, timeout, env)

    outcome = wc.commit_outcome(repo, TRIAL, created_at=CREATED, environment=ENV, run=restaging)
    assert (outcome.result, outcome.reasons) == ("held", ("binding_stale",))


def test_commit_checks_the_staged_bytes_not_the_worktree(repo: Path) -> None:
    stage(repo, "tools/a.py", "x = 2  # LINT_BAD\n")
    outcome = commit(repo, FakeRuff())
    assert (outcome.result, outcome.reasons) == ("failed", ("check_failed",))


# --- proportionate checks ----------------------------------------------------------------


def test_record_only_commit_avoids_unrelated_pyright(repo: Path) -> None:
    stage(repo, "docs/note.md", "record\n")
    ruff = FakeRuff()
    assert commit(repo, ruff) == wc.PASSED
    expected = [[*wc.uv_prefix(repo), "python", *p] for p in wc.RECORD_PRODUCERS]
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
    start = len(wc.uv_prefix(repo)) + 1
    assert [argv[start:] for argv in ruff.checks] == [list(p) for p in wc.RECORD_PRODUCERS]


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
    pytest_argv = (*wc.uv_prefix(repo), "pytest", "-q", "-p", "no:cacheprovider", "tools/test_b.py")
    assert [tuple(argv) for argv in ruff.checks if "pytest" in argv] == [pytest_argv]


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


def _pytest_targets(fake: FakeRuff) -> list[str]:
    return [argv[-1] for argv in fake.checks if "pytest" in argv]


def test_hook_source_runs_the_tests_that_name_it(repo: Path) -> None:
    """F5: a test elsewhere that names the subject's file is its behavior test."""
    stage(repo, "tools/test_names.py", "ADAPTER = 'x_adapter.py'\n")
    git(repo, "commit", "-qm", "test")
    stage(repo, ".codex/hooks/x_adapter.py", "z = 1\n")
    ruff = FakeRuff()
    assert commit(repo, ruff) == wc.PASSED
    assert _pytest_targets(ruff) == ["tools/test_names.py", "tools/test_codex_workflow_parity.py"]


def test_source_named_by_module_runs_that_test(repo: Path) -> None:
    stage(repo, "tests/test_other.py", "import tools.c\n")
    git(repo, "commit", "-qm", "test")
    stage(repo, "tools/c.py", "z = 1\n")
    ruff = FakeRuff()
    assert commit(repo, ruff) == wc.PASSED
    assert _pytest_targets(ruff) == ["tests/test_other.py"]


def test_the_hook_adapter_source_has_its_behavior_tests() -> None:
    """F5 reproduction: the real adapter is exercised by this file and the parity test."""
    path = ".codex/hooks/codex_hook_adapter.py"
    naming = wc.observe_naming(REPO_ROOT, wc.subject_terms(path))
    tests = set(wc.tests_for(path, (), naming))
    assert {"tools/test_workflow_commit.py", "tools/test_codex_workflow_parity.py"} <= tests


@pytest.mark.parametrize(
    ("path", "terms"),
    [
        ("tools/workflow_commit.py", ("workflow_commit.py", "tools.workflow_commit")),
        ("harness-core/src/harness_core/x/__init__.py", ("__init__.py", "harness_core.x")),
        ("tools/hooks/stop-gate.sh", ("stop-gate.sh",)),
    ],
)
def test_subject_terms_name_the_file_and_module(path: str, terms: tuple[str, ...]) -> None:
    assert wc.subject_terms(path) == terms


def test_checks_run_from_the_observed_root(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """F4: the checker resolves config and paths from the root the manifest hashed."""
    monkeypatch.chdir(tmp_path)
    stage(repo, "tools/b.py", "y = 1\n")
    ruff = FakeRuff()
    assert commit(repo, ruff) == wc.PASSED
    assert len(set(ruff.cwds)) == 1
    assert all(files["pyproject.toml"] == "[tool.ruff]\n" for files in ruff.files)
    assert all(argv[argv.index("--config") + 1] == "pyproject.toml" for argv in ruff_runs(ruff))


def test_exhausted_budget_holds_instead_of_racing_the_hook_timeout(repo: Path) -> None:
    stage(repo, "tools/b.py", "y = 1\n")
    ticks = iter(range(0, 10_000, 1_000))
    outcome = wc.commit_outcome(
        repo,
        TRIAL,
        created_at=CREATED,
        environment=ENV,
        run=FakeRuff(),
        clock=lambda: float(next(ticks)),
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
        assert (
            wc.stop_outcome(repo, TRIAL, created_at=CREATED, environment=ENV, run=ruff) == wc.PASSED
        )
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
    wc.stop_outcome(repo, TRIAL, created_at=CREATED, environment=ENV, run=ruff)
    stage(repo, "docs/note.md", "record\n")
    git(repo, "commit", "-qm", "record")
    wc.stop_outcome(repo, TRIAL, created_at=CREATED, environment=ENV, run=ruff)
    assert len(ruff.checks) == 4


def test_checker_version_change_runs_the_check_again(repo: Path) -> None:
    stage(repo, "tools/b.py", "y = 1\n")
    first, second = FakeRuff(), FakeRuff(version=b"ruff 0.0.2")
    commit(repo, first)
    commit(repo, second)
    assert len(ruff_runs(second)) == 2


def _bash_runs(fake: FakeRuff) -> int:
    return sum(argv[0] == "bash" for argv in fake.checks)


def test_bash_identity_binds_shell_test_reuse(repo: Path) -> None:
    """F7 reproduction: a shell test's receipt names the Bash that ran it."""
    stage(repo, "tools/hooks/test_gate.sh", "true\n")
    first, second = FakeRuff(bash=b"GNU bash 5.2"), FakeRuff(bash=b"GNU bash 5.3")
    for fake in (first, second, second):
        assert commit(repo, fake) == wc.PASSED
    assert (_bash_runs(first), _bash_runs(second)) == (1, 1)


@pytest.mark.parametrize("probe", ["uv", "python"])
def test_uv_identity_binds_uv_run_check_reuse(repo: Path, probe: str) -> None:
    """F7: `uv run` checks name the uv and interpreter they resolve."""
    stage(repo, "tools/b.py", "y = 1\n")
    first, second = FakeRuff(), FakeRuff(**{probe: b"changed 9"})
    commit(repo, first)
    commit(repo, second)
    assert _pytest_targets(second) == ["tools/test_b.py"]
    assert ruff_runs(second) == []


@pytest.mark.parametrize("probe", ["bash", "uv", "python"])
def test_unknown_checker_identity_is_a_gap(repo: Path, probe: str) -> None:
    stage(repo, "tools/hooks/test_gate.sh", "true\n")
    outcome = commit(repo, FakeRuff(**{probe: None}))
    assert (outcome.result, outcome.reasons) == ("held", ("check_pending",))


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


def _adapter_at(monkeypatch: pytest.MonkeyPatch, profile: object):  # type: ignore[no-untyped-def]
    adapter, calls = _adapter(), []
    monkeypatch.setattr(adapter, "run_bounded", _recording(adapter, calls))
    monkeypatch.setattr(adapter.workflow_commit, "worktree_profile", lambda _root: profile)
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


def test_trial_commit_defers_to_the_git_gate(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """No Pyright, closeout or suite before a trial commit: Git's hook gates it."""
    adapter, calls = _adapter_at(monkeypatch, TRIAL)
    monkeypatch.setattr(
        adapter.workflow_commit, "commit_outcome", lambda *_a, **_k: pytest.fail("gated twice")
    )
    stage(repo, "tools/b.py", "y = 1  # LINT_BAD\n")
    assert adapter.pre_commit(_payload(repo)) == 0
    assert calls == []


def test_held_commit_blocks_without_the_legacy_gate(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    adapter, calls = _adapter_at(monkeypatch, wc.Held(("commit_gate_unbound",)))
    assert adapter.pre_commit(_payload(repo)) == 2
    assert adapter.pre_commit(_payload(repo, "git status")) == 0
    assert calls == []
    assert "commit_gate_unbound" in capsys.readouterr().err


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


# --- the Git commit boundary -------------------------------------------------------------


HOOK = REPO_ROOT / ".githooks" / "pre-commit"


def head(root: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()


def _gated(repo: Path, gate_exit: int) -> Path:
    """`repo` with the real pre-commit hook enabled and, in place of the gate, a stand-in
    that records its arguments and exits `gate_exit`."""
    (repo / ".githooks").mkdir()
    shutil.copy2(HOOK, repo / ".githooks" / "pre-commit")
    log = repo.parent / "gate.log"
    (repo / "tools" / "workflow_commit.py").write_text(
        "import sys\n"
        f"open({str(log)!r}, 'a').write(' '.join(sys.argv[1:]) + '\\n')\n"
        f"sys.exit({gate_exit})\n"
    )
    git(repo, "config", "core.hooksPath", ".githooks")
    return log


@pytest.mark.parametrize(("gate_exit", "recorded"), [(0, True), (3, False), (4, False)])
def test_a_commit_inside_a_script_runs_the_gate(repo: Path, gate_exit: int, recorded: bool) -> None:
    """F1 reproduction: Git runs the gate for a commit the Bash command text never shows,
    and the commit records only when the gate passes."""
    log = _gated(repo, gate_exit)
    stage(repo, "tools/b.py", "y = 1\n")
    script = repo.parent / "hidden.sh"
    script.write_text(f"git -C {repo} commit -qm hidden\n")
    before = head(repo)
    subprocess.run(["bash", str(script)], capture_output=True, check=False)
    assert log.read_text() == f"pre-commit --root {repo.resolve()}\n"
    assert (head(repo) != before) is recorded


def test_a_passing_gate_keeps_the_advisory_hook(repo: Path) -> None:
    _gated(repo, 0)
    stage(repo, "design-substrate/x.md", "design\n")
    proc = subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "x"], capture_output=True, text=True
    )
    assert proc.returncode == 0
    assert "X-AL-3 advisory" in proc.stdout + proc.stderr


def _exit_zero_file(tmp: Path) -> Path:
    path = tmp / "startup.sh"
    path.write_text("exit 0\n")
    return path


def _exit_zero_site(tmp: Path) -> Path:
    site = tmp / "site"
    site.mkdir()
    (site / "sitecustomize.py").write_text("import os\nos._exit(0)\n")
    return site


@pytest.mark.parametrize(
    "caller_env",
    [
        lambda tmp: {"BASH_ENV": str(_exit_zero_file(tmp))},
        lambda tmp: {"SHELLOPTS": "noexec"},
        lambda tmp: {"BASH_FUNC_git%%": "() { echo /nonexistent; }"},
        lambda tmp: {"PYTHONPATH": str(_exit_zero_site(tmp))},
    ],
    ids=["BASH_ENV", "SHELLOPTS", "exported-function", "PYTHONPATH"],
)
def test_caller_startup_state_cannot_skip_the_gate(
    repo: Path, tmp_path: Path, caller_env: Callable[[Path], dict[str, str]]
) -> None:
    """Pass-4 reproduction: shell and Python startup state the caller exports runs before
    the hook's first line, so none of it may end the hook or redirect the gate."""
    log = _gated(repo, 3)
    stage(repo, "tools/b.py", "y = 1\n")
    before = head(repo)
    proc = subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "x"],
        capture_output=True,
        env={**os.environ, **caller_env(tmp_path)},
        check=False,
    )
    assert log.read_text() == f"pre-commit --root {repo.resolve()}\n"
    assert (proc.returncode, head(repo)) == (1, before)


def _record_staging(root: Path, out: Path) -> None:
    """A pre-commit hook in `root` that writes the gate's staging verdict for the index
    Git hands it."""
    probe = root.parent / "staging_probe.py"
    probe.write_text(
        "import os, sys\nfrom pathlib import Path\n"
        f"sys.path.insert(0, {str(REPO_ROOT)!r})\n"
        "from tools import workflow_commit as wc\n"
        "outcome = wc.recorded_index(Path.cwd(), os.environ.get('GIT_INDEX_FILE'))\n"
        f"Path({str(out)!r}).write_text(outcome.result)\n"
    )
    hooks = root.parent / "probe-hooks"
    hooks.mkdir(exist_ok=True)
    (hooks / "pre-commit").write_text(f"#!/bin/sh\nexec {sys.executable} -I {probe}\n")
    (hooks / "pre-commit").chmod(0o755)
    git(root, "config", "core.hooksPath", str(hooks))


@pytest.mark.parametrize(
    ("args", "result"),
    [
        (("-m", "x"), "passed"),
        (("-am", "x"), "held"),
        (("-m", "x", "--", "tools/a.py"), "held"),
        (("-m", "x", "-i", "tools/a.py"), "held"),
    ],
    ids=["staged", "all", "only", "include"],
)
def test_only_a_commit_of_the_staged_index_is_explicit(
    repo: Path, args: tuple[str, ...], result: str
) -> None:
    """F1/F2 with real Git: the index Git records is the repository's own index only when
    staging was explicit."""
    out = repo.parent / "staging"
    _record_staging(repo, out)
    stage(repo, "tools/b.py", "y = 1\n")
    (repo / "tools" / "a.py").write_text("x = 2\n")
    subprocess.run(["git", "-C", str(repo), "commit", "-q", *args], check=True)
    assert out.read_text() == result


def test_a_linked_worktree_commit_of_its_staged_index_is_explicit(repo: Path) -> None:
    out = repo.parent / "staging"
    _record_staging(repo, out)
    linked = repo.parent / "linked"
    git(repo, "worktree", "add", "-q", str(linked))
    stage(linked, "tools/b.py", "y = 1\n")
    subprocess.run(["git", "-C", str(linked), "commit", "-qm", "x"], check=True)
    assert out.read_text() == "passed"


def _enrolled(monkeypatch: pytest.MonkeyPatch, repo: Path) -> None:
    policy = dataclasses.replace(_policy(), eligible_units=(EligibleUnit(UNIT, "u06"),))
    monkeypatch.setattr(wc, "observe_policy", lambda: policy)
    monkeypatch.setattr(wc, "select_profile", lambda *_: ProfileSelection("trial", (), ()))
    _bind_arc(repo)


def test_trial_requires_git_to_run_the_gate(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """F1: a worktree where Git would not run the gate cannot select trial."""
    _enrolled(monkeypatch, repo)
    assert wc.worktree_profile(repo) == wc.Held(("commit_gate_unbound",))
    git(repo, "config", "core.hooksPath", "elsewhere")
    assert wc.worktree_profile(repo) == wc.Held(("commit_gate_unbound",))
    git(repo, "config", "core.hooksPath", ".githooks")
    assert wc.worktree_profile(repo) == wc.Held(("commit_gate_unbound",))  # no hook there
    (repo / ".githooks").mkdir()
    shutil.copy2(HOOK, repo / ".githooks" / "pre-commit")
    assert isinstance(wc.worktree_profile(repo), wc.Trial)
    for unbound in (
        ("config", "core.hooksPath", "elsewhere"),
        ("config", "--unset", "core.hooksPath"),
    ):
        git(repo, *unbound)  # the gate is there, but Git would not run it
        assert wc.worktree_profile(repo) == wc.Held(("commit_gate_unbound",))


@pytest.mark.parametrize(
    ("profile", "text", "code"),
    [
        (wc.Legacy(), "y = 1  # LINT_BAD\n", 0),
        (wc.Held(("commit_gate_unbound",)), "y = 1\n", 3),
        (TRIAL, "y = 1\n", 0),
        (TRIAL, "y = 1  # LINT_BAD\n", 4),
    ],
    ids=["legacy", "held", "trial-passed", "trial-failed"],
)
def test_pre_commit_exit_code_is_the_outcome(
    repo: Path, monkeypatch: pytest.MonkeyPatch, profile: object, text: str, code: int
) -> None:
    ruff = FakeRuff()
    monkeypatch.setattr(wc, "worktree_profile", lambda _root: profile)
    gate = wc.commit_outcome
    monkeypatch.setattr(wc, "commit_outcome", lambda *a, **k: gate(*a, **{**k, "run": ruff}))
    monkeypatch.delenv("GIT_INDEX_FILE", raising=False)
    stage(repo, "tools/b.py", text)
    assert wc.main(["pre-commit", "--root", str(repo)]) == code


def test_pre_commit_holds_implicit_staging_before_any_check(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(wc, "worktree_profile", lambda _root: TRIAL)
    monkeypatch.setattr(wc, "commit_outcome", lambda *_a, **_k: pytest.fail("checked"))
    monkeypatch.setenv("GIT_INDEX_FILE", str(repo / ".git" / "index.lock"))
    assert wc.main(["pre-commit", "--root", str(repo)]) == 3


# --- the index snapshot ------------------------------------------------------------------


def test_snapshot_is_a_git_checkout_of_the_staged_tree(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """F5 reproduction: `git ls-files` and `git grep --cached`, which the selected test
    and record producer call, see exactly the staged tree inside the snapshot, under the
    hook's own Git variables, and the root keeps its refs and worktrees."""
    git(repo, "remote", "add", "origin", "https://github.com/o/r.git")
    stage(repo, "tools/b.py", "STAGED = 1\n")
    (repo / "tools" / "b.py").write_text("UNSTAGED = 1\n")
    (repo / "tools" / "scratch.py").write_text("UNTRACKED = 1\n")
    refs = subprocess.run(["git", "-C", str(repo), "show-ref"], capture_output=True).stdout
    monkeypatch.setenv("GIT_DIR", str(repo / ".git"))
    monkeypatch.setenv("GIT_INDEX_FILE", ".git/index")
    environment = wc.checker_environment(os.environ)
    with wc.index_snapshot(repo, environment) as snapshot:

        def inside(*args: str) -> str:
            proc = subprocess.run(
                ["git", *args], cwd=snapshot, env=environment, capture_output=True, text=True
            )
            return proc.stdout

        tracked = [
            "pyproject.toml",
            "tools/a.py",
            "tools/b.py",
            "tools/test_a.py",
            "tools/test_b.py",
        ]
        assert inside("ls-files").split() == tracked
        assert inside("grep", "--cached", "-l", "-e", "STAGED", "-e", "UNTRACKED").split() == [
            "tools/b.py"
        ]
        assert inside("rev-parse", "HEAD").strip() == head(repo)
        assert inside("diff", "--cached", "--name-only").split() == ["tools/b.py"]
        assert inside("diff", "--name-only") == ""
        assert inside("remote", "get-url", "origin").strip() == "https://github.com/o/r.git"
        assert (snapshot / "tools" / "b.py").read_text() == "STAGED = 1\n"
        assert not (snapshot / "tools" / "scratch.py").exists()
    monkeypatch.delenv("GIT_DIR")
    monkeypatch.delenv("GIT_INDEX_FILE")
    assert subprocess.run(["git", "-C", str(repo), "show-ref"], capture_output=True).stdout == refs
    listed = subprocess.run(
        ["git", "-C", str(repo), "worktree", "list", "--porcelain"], capture_output=True, text=True
    ).stdout
    assert listed.count("worktree ") == 1


# --- the checker environment -------------------------------------------------------------


def test_checks_receive_only_the_pinned_environment(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """F7: a check receives exactly the variables its manifest pins, never BASH_ENV,
    interpreter, uv or Git variables from the caller."""
    stage(repo, "tools/b.py", "y = 1\n")
    for name in ("BASH_ENV", "ENV", "PYTHONPATH", "UV_PYTHON", "GIT_INDEX_FILE", "PYTEST_ADDOPTS"):
        monkeypatch.setenv(name, "/elsewhere")
    environment = wc.checker_environment(os.environ)
    assert set(environment) <= set(wc.CHECK_VARIABLES)
    assert environment["PATH"] == os.environ["PATH"]
    monkeypatch.delenv("GIT_INDEX_FILE")  # the gate's own Git calls read the real index
    ruff = FakeRuff()
    assert commit(repo, ruff, environment) == wc.PASSED
    assert ruff.environments == [environment] * 3


def test_a_changed_environment_pin_runs_the_check_again(repo: Path) -> None:
    stage(repo, "tools/b.py", "y = 1\n")
    ruff = FakeRuff()
    for path in ("/usr/bin:/bin", "/usr/bin:/bin", "/opt/bin:/usr/bin:/bin"):
        assert commit(repo, ruff, {**ENV, "PATH": path}) == wc.PASSED
    assert len(ruff.checks) == 6


def test_a_shell_test_runs_without_the_callers_bash_startup(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """F7 reproduction with real Bash: a BASH_ENV that fails a direct run never reaches the
    check, so the receipt describes the run, and a later BASH_ENV change, which the check
    still never reads, reuses it."""
    failing, passing = repo.parent / "fail.sh", repo.parent / "pass.sh"
    failing.write_text("exit 1\n")
    passing.write_text("true\n")
    stage(repo, "scripts/gate.sh", "true\n")
    stage(repo, "scripts/test_gate.sh", "true\n")
    runs: list[tuple[list[str], Mapping[str, str]]] = []

    def counting(
        argv: Sequence[str], stdin: bytes, cwd: Path, timeout: float, env: Mapping[str, str]
    ) -> subprocess.CompletedProcess[bytes]:
        runs.append((list(argv), env))
        return wc.run_bounded(argv, stdin, cwd, timeout, env)

    for bash_env in (failing, passing):
        monkeypatch.setenv("BASH_ENV", str(bash_env))
        direct = subprocess.run(["bash", "scripts/test_gate.sh"], cwd=repo, check=False)
        assert direct.returncode == (1 if bash_env == failing else 0)
        outcome = wc.commit_outcome(
            repo, TRIAL, created_at=CREATED, environment=wc.checker_environment(os.environ),
            run=counting,
        )  # fmt: skip
        assert outcome == wc.PASSED
    probes = ("--version", wc.ENVIRONMENT_PROBE)
    assert [argv for argv, _ in runs if argv[-1] not in probes] == [
        ["bash", "scripts/test_gate.sh"]
    ]
    assert all("BASH_ENV" not in env for _, env in runs)


# --- additional cycle pass-1 corrections -------------------------------------------------


def test_a_deleted_source_runs_the_tests_that_remain(repo: Path) -> None:
    """Pass-1 C1/S2 reproduction: deleting a source can break the tests that still import
    it, so they run as its behavior check."""
    git(repo, "rm", "-q", "tools/a.py")
    assert commit(repo, FakeRuff(exit_code=1)).result == "failed"
    ruff = FakeRuff()
    assert commit(repo, ruff) == wc.PASSED
    assert _pytest_targets(ruff) == ["tools/test_a.py"]


def test_a_deleted_source_and_its_test_leave_nothing_to_hold(repo: Path) -> None:
    git(repo, "rm", "-q", "tools/a.py", "tools/test_a.py")
    ruff = FakeRuff()
    assert commit(repo, ruff) == wc.PASSED
    assert _pytest_targets(ruff) == []


def _environment_identity(python: Path) -> str:
    return subprocess.run(
        [str(python), "-I", "-c", wc.ENVIRONMENT_PROBE], capture_output=True, text=True,
        check=True,
    ).stdout  # fmt: skip


def test_environment_identity_names_every_installed_distribution(tmp_path: Path) -> None:
    """Pass-1 C2 reproduction with a real interpreter: reinstalling a dependency under the
    same Python changes the identity that keys every `uv run` check; nothing else does."""
    env = tmp_path / "env"
    subprocess.run([sys.executable, "-m", "venv", "--without-pip", str(env)], check=True)
    python = env / "bin" / "python"
    purelib = subprocess.run(
        [str(python), "-I", "-c", "import sysconfig; print(sysconfig.get_paths()['purelib'])"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()  # fmt: skip
    plugin = Path(purelib) / "plugin-1.0.dist-info"
    plugin.mkdir()
    identities = [_environment_identity(python)]
    for version, record in (
        ("1.0", "plugin.py,sha256=aaaa,1\n"),
        ("1.0", "plugin.py,sha256=bbbb,1\n"),
        ("1.1", "plugin.py,sha256=bbbb,1\n"),
    ):
        (plugin / "METADATA").write_text(
            f"Metadata-Version: 2.1\nName: plugin\nVersion: {version}\n"
        )
        (plugin / "RECORD").write_text(record)
        identities.append(_environment_identity(python))
    assert len(set(identities)) == 4
    assert _environment_identity(python) == identities[-1]
    assert all(identity.startswith("Python ") for identity in identities)


@pytest.mark.parametrize("winner_verifies", [True, False])
def test_a_concurrent_identical_check_accepts_the_receipt_published_first(
    repo: Path, winner_verifies: bool
) -> None:
    """Pass-1 C4/K1 reproduction: two gates both miss the stored receipt and run the same
    check; the one publishing second accepts the first's receipt when it verifies the
    check, and only otherwise reports the publication uncertain."""
    stage(repo, "tools/b.py", "y = 1\n")
    fake, concurrent = FakeRuff(), list[wc.Outcome]()

    def racing(
        argv: Sequence[str], stdin: bytes, cwd: Path, timeout: float, env: Mapping[str, str]
    ) -> subprocess.CompletedProcess[bytes]:
        if argv[-1] not in ("--version", wc.ENVIRONMENT_PROBE) and not concurrent:
            concurrent.append(commit(repo, FakeRuff()))  # the other gate finishes first
            for receipt in wc.CHECK_ROOT.glob("*.json"):
                receipt.write_bytes(receipt.read_bytes() if winner_verifies else b"{}")
        return fake(argv, stdin, cwd, timeout, env)

    outcome = wc.commit_outcome(repo, TRIAL, created_at=CREATED, environment=ENV, run=racing)
    assert concurrent == [wc.PASSED]
    expected = wc.PASSED if winner_verifies else ("error", ("publication_uncertain",))
    assert (outcome if winner_verifies else (outcome.result, outcome.reasons)) == expected


def _alive(pid: int) -> bool:
    """Whether `pid` is a live process; a zombie awaiting its reaper has already ended."""
    for _ in range(50):
        state = subprocess.run(
            ["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True, check=False
        ).stdout.strip()
        if not state or state.startswith("Z"):
            return False
        subprocess.run(["sleep", "0.1"], check=True)  # SIGKILL lands when it is scheduled
    return True


@pytest.mark.parametrize(
    ("script", "timeout", "code"),
    [
        ("sleep 60 >/dev/null 2>&1 & echo $! > {pid}; exit 0", 30.0, 0),
        ("sleep 60 & echo $! > {pid}; sleep 60", 1.0, 124),
    ],
    ids=["leader-exits", "leader-times-out"],
)
def test_no_checker_descendant_outlives_its_result(
    tmp_path: Path, script: str, timeout: float, code: int
) -> None:
    """Pass-1 K2 reproduction with real processes: a background descendant, detached from
    the output or holding it, ends with the checker's result instead of outliving it."""
    pid = tmp_path / "pid"
    proc = wc.run_bounded(["bash", "-c", script.format(pid=pid)], b"", tmp_path, timeout, ENV)
    assert proc.returncode == code
    assert not _alive(int(pid.read_text()))


# --- real-path trial witness (pass-1 W1) -------------------------------------------------

# Copied byte for byte into the witness repository: Git's hook, the Stop hook and the
# router with the modules it imports.
_REAL_PATH = (
    ".githooks/pre-commit",
    "tools/hooks/stop-gate.sh",
    "tools/hooks/lib.sh",
    "tools/workflow_commit.py",
    "tools/workflow_boundaries.py",
    "tools/workflow_evidence.py",
    "tools/workflow_policy.py",
)
# The witness's only stand-ins, appended to its copy of WP-02: selection yields trial,
# which every unit is held from until activation (WP-17) supplies its LIT facts, and the
# canonical root that holds receipts is private to the test.
_SELECTION_STAND_IN = """

CANONICAL_ROOT = Path({root!r})


def select_profile(policy: object, facts: object) -> ProfileSelection:
    return ProfileSelection("trial", (), ())
"""
_LEGAL = "def w() -> int:\n    return 1 + 0\n"


@pytest.fixture
def trial_repo(tmp_path: Path) -> Path:
    """An enrolled worktree whose commits and Stop run the unmodified hooks and router,
    with a real behavior test that logs each execution to `pytest.log`."""
    root = tmp_path / "repo"
    for name in _REAL_PATH:
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / name, root / name)
    with (root / "tools" / "workflow_policy.py").open("a") as policy:
        policy.write(_SELECTION_STAND_IN.format(root=str(tmp_path / "canonical")))
    enrolled = {**json.loads(wb.POLICY_PATH.read_bytes()), "eligible_units": [
        {"unit": UNIT, "arc": "u06"}
    ]}  # fmt: skip
    (root / ".harness").mkdir()
    (root / ".harness" / "workflow-policy.json").write_text(json.dumps(enrolled))
    _bind_arc(root)
    (root / "pyproject.toml").write_text("[tool.ruff]\n")
    (root / ".gitignore").write_text(".venv\n")
    (root / ".venv").symlink_to(sys.prefix)  # the environment `uv run` checks resolve
    (root / "tools" / "w.py").write_text("def w() -> int:\n    return 1\n")
    (root / "tools" / "test_w.py").write_text(
        "import w\n\n\ndef test_w() -> None:\n"
        f"    with open({str(tmp_path / 'pytest.log')!r}, 'a') as log:\n"
        "        log.write('ran\\n')\n"
        "    assert w.w() == 1\n"
    )
    git(root.parent, "init", "-q", "-b", "main", str(root))
    git(root, "config", "user.email", "t@t.t")
    git(root, "config", "user.name", "t")
    git(root, "remote", "add", "origin", "https://github.com/thestoryportal/arhugula-harness.git")
    git(root, "add", ".")
    git(root, "commit", "-qm", "base")
    git(root, "config", "core.hooksPath", ".githooks")
    return root


def _witness_env(tmp_path: Path, **extra: str) -> dict[str, str]:
    """The caller's environment: real uv, Ruff and pytest, with Ruff behind a shim that
    logs every check it runs to `ruff.log`."""
    tools, uv = Path(sys.executable).parent, shutil.which("uv")
    assert uv and (tools / "ruff").exists(), "the witness needs real uv and Ruff"
    shim = tmp_path / "bin" / "ruff"
    shim.parent.mkdir()
    shim.write_text(
        f'#!/bin/sh\n[ "$1" = --version ] || echo "$*" >> {tmp_path / "ruff.log"}\n'
        f'exec {tools / "ruff"} "$@"\n'
    )
    shim.chmod(0o755)
    path = f"{shim.parent}:{tools}:{Path(uv).parent}:/usr/bin:/bin"
    return {"HOME": os.environ["HOME"], "PATH": path, **extra}


def test_the_real_git_gate_refuses_admits_and_reuses(trial_repo: Path, tmp_path: Path) -> None:
    """Pass-1 W1: `git commit` through the unmodified pre-commit hook and router refuses a
    change its real behavior test rejects, admits a legal change, and reuses that result
    for the unchanged index instead of running the test again."""
    env, log, base = _witness_env(tmp_path), tmp_path / "pytest.log", head(trial_repo)

    def commit_with(message: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(trial_repo), "commit", "-q", "-m", message],
            env=env, capture_output=True, text=True, check=False,
        )  # fmt: skip

    stage(trial_repo, "tools/w.py", "def w() -> int:\n    return 2\n")
    refused = commit_with("illegal")
    assert refused.returncode != 0 and "check_failed" in refused.stderr, refused.stderr
    assert (head(trial_repo), log.read_text()) == (base, "ran\n")
    stage(trial_repo, "tools/w.py", _LEGAL)
    aborted = commit_with("")  # Git runs the gate, then aborts on the empty message
    assert "Aborting commit due to empty commit message" in aborted.stderr, aborted.stderr
    assert (head(trial_repo), log.read_text()) == (base, "ran\n" * 2)
    admitted = commit_with("legal")
    assert admitted.returncode == 0, admitted.stderr
    assert head(trial_repo) != base
    assert log.read_text() == "ran\n" * 2  # the unchanged index reused its receipt


def test_the_real_stop_hook_refuses_admits_and_reuses(trial_repo: Path, tmp_path: Path) -> None:
    """Pass-1 W1: the unmodified Stop hook and router block a turn whose change real Ruff
    rejects, allow a legal change, and do not run Ruff again for an unchanged turn."""
    env = _witness_env(tmp_path, CLAUDE_PROJECT_DIR=str(trial_repo))

    def stop() -> str:
        return subprocess.run(
            ["bash", str(trial_repo / "tools" / "hooks" / "stop-gate.sh")],
            input='{"stop_hook_active":false}', env=env, cwd=trial_repo,
            capture_output=True, text=True, check=True,
        ).stdout  # fmt: skip

    (trial_repo / "tools" / "w.py").write_text("import os\n\n\ndef w() -> int:\n    return 1\n")
    blocked = stop()
    assert "trial changed-subject check failed (check_failed)" in blocked, blocked
    (trial_repo / "tools" / "w.py").write_text(_LEGAL)
    assert (stop(), stop()) == ("", "")
    runs = (tmp_path / "ruff.log").read_text().splitlines()
    assert [run.split()[0] for run in runs] == ["check", "format", "check", "format"]


def test_uv_checks_are_keyed_by_the_installed_environment(trial_repo: Path, tmp_path: Path) -> None:
    """Pass-1 C2 wiring: the identity keying every `uv run` check is the environment
    probe's answer from the interpreter `uv run` resolves for the worktree."""
    toolchain = wc.observe_toolchain(trial_repo, wc.run_bounded, _witness_env(tmp_path))
    identity = _environment_identity(Path(sys.executable)).strip()
    assert toolchain.python is not None and toolchain.python.endswith(f"; {identity}")
