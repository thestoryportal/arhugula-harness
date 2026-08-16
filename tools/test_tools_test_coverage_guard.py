"""Tests for `tools/tools_test_coverage_guard.py`.

Both directions for every rule, per this repo's gate discipline: the guard fires on the
drift it exists to catch, AND stays silent on the look-alike that is not drift. A guard
that fires on everything gets muted within two rounds, which is how a gate degrades into
a rubber stamp.

The fixtures build a miniature repo on disk rather than monkeypatching internals, because
the thing under test is precisely how the guard READS a repo — a stubbed reader would
prove nothing about the parse that `B-184` needed four attempts to get right.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import tools_test_coverage_guard as guard


def _repo(tmp_path: Path, *, modules: list[str], workflow: str = "", parity: str = "") -> Path:
    (tmp_path / "tools").mkdir(parents=True, exist_ok=True)
    for m in modules:
        (tmp_path / "tools" / m).write_text("# test module\n", encoding="utf-8")
    wf_dir = tmp_path / ".github" / "workflows"
    wf_dir.mkdir(parents=True)
    (wf_dir / "ci.yml").write_text(workflow or "jobs: {}\n", encoding="utf-8")
    if parity:
        (tmp_path / "tools" / "codex-parity-check.sh").write_text(parity, encoding="utf-8")
    return tmp_path


def _wf(run: str) -> str:
    return f"jobs:\n  a:\n    steps:\n      - run: {run}\n"


# --- the invariant holds ------------------------------------------------------


def test_silent_when_every_module_is_executed_by_a_workflow(tmp_path: Path) -> None:
    root = _repo(tmp_path, modules=["test_a.py"], workflow=_wf("pytest tools/test_a.py -q"))
    assert guard.validate(root) == []


def test_silent_when_a_module_is_executed_by_the_parity_script(tmp_path: Path) -> None:
    root = _repo(tmp_path, modules=["test_a.py"], parity="uv run pytest \\\n  tools/test_a.py\n")
    assert guard.validate(root) == []


def test_a_bare_filename_invocation_counts_as_executed(tmp_path: Path) -> None:
    """CI really invokes some modules bare, under `working-directory: tools`.

    A path-prefixed matcher misses these — that mistake is why `B-184`'s first sweep
    reported 33 dead modules instead of 15.
    """
    root = _repo(tmp_path, modules=["test_a.py"], workflow=_wf("pytest test_a.py -q"))
    assert guard.validate(root) == []


# --- the invariant is violated ------------------------------------------------


def test_fires_on_a_module_executed_by_nothing(tmp_path: Path) -> None:
    root = _repo(tmp_path, modules=["test_orphan.py"], workflow=_wf("echo hi"))
    problems = guard.validate(root)
    assert len(problems) == 1
    assert "test_orphan.py" in problems[0]
    assert "no EXCLUSIONS entry" in problems[0]


def test_the_message_warns_against_inferring_a_gate_from_the_filename(tmp_path: Path) -> None:
    """`B-184`'s worst error, encoded where the next person will hit it.

    Nine modules named `*_live_e2e` / `*_readiness` were assumed credential-gated; they
    held 64 provider-free tests passing in 5.5s with credentials stripped.
    """
    root = _repo(tmp_path, modules=["test_something_live_e2e.py"], workflow=_wf("echo hi"))
    (problem,) = guard.validate(root)
    assert "credentials" in problem and "stripped" in problem


def test_reports_every_orphan_not_just_the_first(tmp_path: Path) -> None:
    root = _repo(tmp_path, modules=["test_a.py", "test_b.py"], workflow=_wf("echo hi"))
    assert len(guard.validate(root)) == 2


# --- the exclusion mechanism, both directions --------------------------------


def test_an_excluded_module_with_a_reason_is_accepted(tmp_path: Path, monkeypatch) -> None:
    root = _repo(tmp_path, modules=["test_slow.py"], workflow=_wf("echo hi"))
    monkeypatch.setattr(guard, "EXCLUSIONS", {"test_slow.py": "too slow for the gate"})
    assert guard.validate(root) == []


def test_an_exclusion_with_an_empty_reason_is_rejected(tmp_path: Path, monkeypatch) -> None:
    """The reason IS the mechanism — without it, excluded and forgotten are the same."""
    root = _repo(tmp_path, modules=["test_slow.py"], workflow=_wf("echo hi"))
    monkeypatch.setattr(guard, "EXCLUSIONS", {"test_slow.py": "   "})
    (problem,) = guard.validate(root)
    assert "empty reason" in problem


def test_a_stale_exclusion_for_an_executed_module_is_rejected(tmp_path: Path, monkeypatch) -> None:
    """Two-way: an exclusion list that only grows becomes its own drift surface."""
    root = _repo(tmp_path, modules=["test_a.py"], workflow=_wf("pytest tools/test_a.py -q"))
    monkeypatch.setattr(guard, "EXCLUSIONS", {"test_a.py": "was slow once"})
    (problem,) = guard.validate(root)
    assert "IS executed" in problem


def test_an_exclusion_for_a_deleted_module_is_rejected(tmp_path: Path, monkeypatch) -> None:
    root = _repo(tmp_path, modules=["test_a.py"], workflow=_wf("pytest tools/test_a.py -q"))
    monkeypatch.setattr(guard, "EXCLUSIONS", {"test_gone.py": "deleted last year"})
    (problem,) = guard.validate(root)
    assert "no such module exists" in problem


# --- parse-not-scan -----------------------------------------------------------


def test_a_comment_naming_a_module_does_not_count_as_executing_it(tmp_path: Path) -> None:
    """The reason coverage is derived by PARSING `run:` blocks.

    `ci.yml` really does carry comments naming test modules it does not run; a text scan
    over the raw file counts those as coverage and silently blesses a dead module.
    """
    wf = (
        "# ci.yml mentions tools/test_orphan.py in prose only\n"
        "jobs:\n  a:\n    name: a job about tools/test_orphan.py\n"
        "    steps:\n      - run: echo hi\n"
    )
    root = _repo(tmp_path, modules=["test_orphan.py"], workflow=wf)
    (problem,) = guard.validate(root)
    assert "test_orphan.py" in problem


def test_a_malformed_workflow_does_not_crash_the_guard(tmp_path: Path) -> None:
    root = _repo(tmp_path, modules=["test_a.py"], parity="pytest tools/test_a.py\n")
    (root / ".github" / "workflows" / "ci.yml").write_text("{[not: valid", encoding="utf-8")
    assert guard.validate(root) == []


# --- the real tree ------------------------------------------------------------


def test_the_invariant_holds_on_this_repository() -> None:
    """The guard's own reason for existing: it must be green here, now."""
    assert guard.validate() == []


def test_the_repository_has_no_unexecuted_modules_left() -> None:
    """`B-184` left the tree with everything wired. Pinned so a regression is loud."""
    present, executed = guard.test_modules(), guard.executed_modules()
    assert present - executed == set(), (
        f"unexecuted modules reappeared: {sorted(present - executed)}"
    )
    assert len(present) >= 43, f"only {len(present)} modules found — the glob root is wrong"


# --- presence is not execution (out-of-family review round 1) ------------------


def test_a_non_pytest_command_naming_the_module_is_not_execution(tmp_path: Path) -> None:
    """`cat tools/test_x.py` reads the file; it does not run it."""
    root = _repo(tmp_path, modules=["test_orphan.py"], workflow=_wf("cat tools/test_orphan.py"))
    (problem,) = guard.validate(root)
    assert "test_orphan.py" in problem


def test_an_ignore_flag_is_not_execution_it_is_the_opposite(tmp_path: Path) -> None:
    """`--ignore=` naming a module means pytest was told NOT to run it."""
    root = _repo(
        tmp_path,
        modules=["test_orphan.py"],
        workflow=_wf("pytest tools --ignore=tools/test_orphan.py -q"),
    )
    (problem,) = guard.validate(root)
    assert "test_orphan.py" in problem


def test_a_deselect_flag_is_not_execution(tmp_path: Path) -> None:
    root = _repo(
        tmp_path,
        modules=["test_orphan.py"],
        workflow=_wf("pytest tools --deselect=tools/test_orphan.py -q"),
    )
    assert len(guard.validate(root)) == 1


def test_a_comment_inside_a_run_block_is_not_execution(tmp_path: Path) -> None:
    """The subtler sibling of the prose-comment case: a `#` line within the shell body."""
    wf = (
        "jobs:\n  a:\n    steps:\n      - run: |\n"
        "          # pytest tools/test_orphan.py\n          echo hi\n"
    )
    root = _repo(tmp_path, modules=["test_orphan.py"], workflow=wf)
    (problem,) = guard.validate(root)
    assert "test_orphan.py" in problem


def test_a_real_pytest_invocation_in_a_multiline_block_still_counts(tmp_path: Path) -> None:
    """The negative cases must not have broken the positive one."""
    wf = (
        "jobs:\n  a:\n    steps:\n      - run: |\n"
        "          # about to run it\n          pytest tools/test_a.py -q\n"
    )
    root = _repo(tmp_path, modules=["test_a.py"], workflow=wf)
    assert guard.validate(root) == []


def test_workflows_with_the_yaml_extension_are_scanned(tmp_path: Path) -> None:
    """GitHub honours both `.yml` and `.yaml`; a guard that reads one blocks CI on the other."""
    root = _repo(tmp_path, modules=["test_a.py"], workflow="jobs: {}\n")
    (root / ".github" / "workflows" / "nightly.yaml").write_text(
        _wf("pytest tools/test_a.py -q"), encoding="utf-8"
    )
    assert guard.validate(root) == []


def test_a_space_separated_ignore_flag_is_not_execution(tmp_path: Path) -> None:
    """`--ignore tools/test_x.py` — the value is a separate token (review round 2)."""
    root = _repo(
        tmp_path,
        modules=["test_orphan.py"],
        workflow=_wf("pytest tools --ignore tools/test_orphan.py -q"),
    )
    (problem,) = guard.validate(root)
    assert "test_orphan.py" in problem


def test_a_line_that_merely_mentions_pytest_is_not_execution(tmp_path: Path) -> None:
    """`echo pytest tools/test_x.py` prints a string; the COMMAND is `echo`."""
    root = _repo(
        tmp_path, modules=["test_orphan.py"], workflow=_wf("echo pytest tools/test_orphan.py")
    )
    (problem,) = guard.validate(root)
    assert "test_orphan.py" in problem


def test_runner_wrappers_before_pytest_still_count_as_execution(tmp_path: Path) -> None:
    """The positive control for the command walk: real invocations wear prefixes."""
    for i, cmd in enumerate(
        (
            "uv run pytest tools/test_a.py -q",
            "uv run python -m pytest tools/test_a.py -q",
            "env PYTHON_KEYRING_BACKEND=x uv run pytest tools/test_a.py",
        )
    ):
        root = _repo(tmp_path / f"case{i}", modules=["test_a.py"], workflow=_wf(cmd))
        assert guard.validate(root) == [], cmd
