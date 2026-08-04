"""Hermetic tests for tools/mutation_probe.py (U-WT-06). Zero network.

The probe is driven as a SUBPROCESS in every behavioural test, because its signal handling,
its `finally`-restore and its exit codes ARE the contract — an in-process call would test a
function, not the tool. Each test gets a throwaway `git init` repository under `tmp_path`
with its identity set LOCALLY (never touching the operator's global git config), and an
autouse fixture asserts that (a) this process never chdir'd and (b) the REAL repository's
`git status` is byte-identical before and after every test — the one thing a tool that
writes source files must never get wrong.

The pure layer (`comment_out`, `classify_step3`, `parse_line_range`) is additionally tested
directly, since those are where the honesty of the verdict lives.
"""

from __future__ import annotations

import os
import re
import shlex
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import mutation_probe as mp

PROBE = Path(__file__).resolve().parent / "mutation_probe.py"
REAL_REPO = Path(__file__).resolve().parent.parent

# The probed module. Line numbers are load-bearing for every test below:
#   1 def classify(n):
#   2     if n < 0:
#   3         return "negative"
#   4     return "non-negative"
#   5
#   6
#   7 def only(x):
#   8     return x * 2
SRC = """def classify(n):
    if n < 0:
        return "negative"
    return "non-negative"


def only(x):
    return x * 2
"""
PINNED = "2-3"  # removing these leaves valid Python AND breaks test_negative
SOLE_STATEMENT = "8"  # the sole statement of `only`'s suite — removal breaks indentation

TEST_REAL = """import src


def test_negative():
    assert src.classify(-1) == "negative"


def test_non_negative():
    assert src.classify(1) == "non-negative"
"""
TEST_VACUOUS = """import src


def test_module_imports():
    assert src is not None
"""
TEST_RED = """def test_always_fails():
    assert False
"""
# A module-level constant whose removal breaks the test file's IMPORT — pytest reports it
# as an error, not a failed test, so the probe must call it INDETERMINATE.
CONSTS = "LIMIT = 5\n"
TEST_CONSTS = """from consts import LIMIT


def test_limit():
    assert LIMIT == 5
"""

# A shell target: exercises the `bash -n` syntax gate and the non-pytest classifier.
#   1 #!/usr/bin/env bash
#   2 greet() {
#   3   echo "hello $1"
#   4 }
#   5 greet "$1"
SCRIPT_SH = """#!/usr/bin/env bash
greet() {
  echo "hello $1"
}
greet "$1"
"""
TEST_SCRIPT_SH = """#!/usr/bin/env bash
out=$(bash script.sh world)
[ "$out" = "hello world" ] || exit 1
exit 0
"""

PY = shlex.quote(sys.executable)


def pytest_cmd(*files: str) -> str:
    """A pytest command for the throwaway repo. `-p no:cacheprovider` keeps a `.pytest_cache`
    out of the probed tree."""
    return f"{PY} -m pytest -q -p no:cacheprovider {' '.join(files)}"


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=str(repo), capture_output=True, text=True, check=False
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A throwaway git repo carrying the probe fixtures, all committed (so the probe's
    clean-file gate passes and `git diff --quiet` is a meaningful restore witness)."""
    root = (tmp_path / "repo").resolve()
    root.mkdir()
    files = {
        "src.py": SRC,
        "consts.py": CONSTS,
        "test_real.py": TEST_REAL,
        "test_vacuous.py": TEST_VACUOUS,
        "test_red.py": TEST_RED,
        "test_consts.py": TEST_CONSTS,
        "script.sh": SCRIPT_SH,
        "test_script.sh": TEST_SCRIPT_SH,
    }
    for name, body in files.items():
        (root / name).write_text(body, encoding="utf-8")
    assert git(root, "init", "-q", "-b", "main").returncode == 0
    # LOCAL identity only — a global git config must never be read or written by a test.
    assert git(root, "config", "user.email", "probe@test.invalid").returncode == 0
    assert git(root, "config", "user.name", "Probe Test").returncode == 0
    assert git(root, "config", "commit.gpgsign", "false").returncode == 0
    assert git(root, "add", *files).returncode == 0
    commit = git(root, "commit", "-q", "-m", "fixtures")
    assert commit.returncode == 0, commit.stderr
    return root


@pytest.fixture(autouse=True)
def _no_collateral_damage():
    """Every test must leave this process's cwd and the REAL repository untouched."""
    cwd_before = os.getcwd()
    status_before = git(REAL_REPO, "status", "--porcelain").stdout
    yield
    assert os.getcwd() == cwd_before
    assert git(REAL_REPO, "status", "--porcelain").stdout == status_before, (
        "the probe suite modified the real repository tree"
    )


@pytest.fixture(scope="session", autouse=True)
def _no_stray_sidecars_in_the_real_repo():
    """Sidecars are GITIGNORED, so the per-test `git status` check above cannot see one.
    Scan for them once per session (scoped to `tools/`, where every probeable file this
    suite could plausibly reach lives — a repo-wide glob would walk `.venv`)."""
    yield
    assert not list((REAL_REPO / "tools").rglob("*.mutprobe.*.bak"))
    assert not list(REAL_REPO.glob("*.mutprobe.*.bak"))


def run_probe(
    repo: Path, file: str, lines: str, test: str, timeout: int | None = None
) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(PROBE), "--file", file, "--lines", lines, "--test", test]
    if timeout is not None:
        cmd += ["--timeout", str(timeout)]
    return subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True, timeout=300)


def sidecars(repo: Path) -> list[Path]:
    return sorted(repo.glob("*.mutprobe.*.bak"))


def counting_script(repo: Path, name: str, second_run_body: str) -> str:
    """A `--test` command that PASSES on its first invocation (the probe's baseline) and runs
    `second_run_body` on the second (the mutated run). The counter file is what makes a
    step-3-only behaviour expressible at all."""
    (repo / name).write_text(
        "#!/usr/bin/env bash\n"
        f"n=$(cat {name}.count 2>/dev/null || echo 0)\n"
        f"echo $((n+1)) > {name}.count\n"
        '[ "$n" = "0" ] && exit 0\n'
        f"{second_run_body}\n",
        encoding="utf-8",
    )
    return f"bash {name}"


# --- pure layer --------------------------------------------------------------------------


def test_comment_out_preserves_every_other_byte():
    text = "a\nb\r\nc\n"
    assert mp.comment_out(text, 2, 2) == "a\n# b\r\nc\n"
    assert mp.comment_out(text, 1, 3) == "# a\n# b\r\n# c\n"


def test_comment_out_rejects_a_range_past_eof():
    with pytest.raises(ValueError, match="outside"):
        mp.comment_out("a\nb\n", 2, 3)


@pytest.mark.parametrize(
    ("spec", "expected"), [("12", (12, 12)), ("2-3", (2, 3)), (" 4 - 9 ", (4, 9))]
)
def test_parse_line_range_accepts(spec, expected):
    assert mp.parse_line_range(spec) == expected


@pytest.mark.parametrize("spec", ["0-3", "5-2", "", "a-b", "-3", "1-"])
def test_parse_line_range_rejects(spec):
    with pytest.raises(ValueError):
        mp.parse_line_range(spec)


def test_classify_step3_green_is_survived():
    assert mp.classify_step3(0, "2 passed", True)[0] == mp.SURVIVED


@pytest.mark.parametrize("rc", [-9, 124, 126, 127, 137])
def test_classify_step3_abnormal_termination_is_never_a_kill(rc):
    """A signalled, timed-out or unlaunchable command is INDETERMINATE — reporting it as a
    kill is the exact false-pass this tool exists to avoid."""
    assert mp.classify_step3(rc, "", False)[0] == mp.INDETERMINATE
    assert mp.classify_step3(rc, "1 failed", True)[0] == mp.INDETERMINATE


def test_classify_step3_pytest_needs_a_reported_failure():
    assert mp.classify_step3(1, "= 1 failed, 1 passed in 0.1s =", True)[0] == mp.KILLED
    assert mp.classify_step3(4, "ERROR: usage error", True)[0] == mp.INDETERMINATE
    assert mp.classify_step3(5, "no tests ran in 0.01s", True)[0] == mp.INDETERMINATE


def test_classify_step3_pytest_collection_errors_are_indeterminate():
    verdict, why = mp.classify_step3(2, "= 1 error in 0.1s =", True)
    assert verdict == mp.INDETERMINATE
    assert "error" in why


def test_classify_step3_xfail_is_not_a_failure():
    """`1 xfailed` must not read as `1 failed` — the summary-count regex is the only thing
    standing between an xfail-only suite and a fabricated kill."""
    assert mp.classify_step3(1, "= 1 xfailed in 0.1s =", True)[0] == mp.INDETERMINATE


def test_classify_step3_generic_nonzero_is_a_kill_with_a_stated_caveat():
    verdict, why = mp.classify_step3(1, "assertion failed", False)
    assert verdict == mp.KILLED
    assert "heuristic" in why


@pytest.mark.parametrize(
    ("cmd", "expected"),
    [
        ("uv run pytest -q x.py", True),
        ("/usr/bin/python3 -m pytest tools/", True),
        ("bash tools/hooks/test_postedit_lint.sh", False),
        ("./run-pytests.sh", False),
    ],
)
def test_looks_like_pytest(cmd, expected):
    assert mp.looks_like_pytest(cmd) is expected


# --- AC1: a real test + load-bearing lines ------------------------------------------------


def test_ac1_real_test_pinning_the_lines_passes_and_restores(repo):
    before = (repo / "src.py").read_bytes()
    res = run_probe(repo, "src.py", PINNED, pytest_cmd("test_real.py"))
    assert res.returncode == 0, res.stdout + res.stderr
    assert "PROBE PASSED" in res.stdout
    assert (repo / "src.py").read_bytes() == before
    assert git(repo, "status", "--porcelain", "--", "src.py").stdout == ""
    # AC8: no success-path sidecar survives (a later dead-pid reconcile would replay it).
    assert sidecars(repo) == []


def test_ac1_the_mutation_really_happened(repo):
    """Guard against a probe that passes without ever writing the file: the test command
    snapshots the target during step 3, and the snapshot must carry the comment markers."""
    cmd = counting_script(
        repo, "snap.sh", "cp src.py src.during-step3\n" + pytest_cmd("test_real.py")
    )
    res = run_probe(repo, "src.py", PINNED, cmd)
    assert res.returncode == 0, res.stdout + res.stderr
    during = (repo / "src.during-step3").read_text(encoding="utf-8")
    # The prefix goes at COLUMN 0, ahead of the line's own indentation (see `comment_out`).
    assert "#     if n < 0:" in during
    assert '#         return "negative"' in during
    assert (repo / "src.py").read_text(encoding="utf-8") == SRC


def test_ac1_shell_target_under_a_non_pytest_command(repo):
    before = (repo / "script.sh").read_bytes()
    res = run_probe(repo, "script.sh", "5", "bash test_script.sh")
    assert res.returncode == 0, res.stdout + res.stderr
    assert "PROBE PASSED" in res.stdout
    assert (repo / "script.sh").read_bytes() == before


# --- AC2: a vacuous test ------------------------------------------------------------------


def test_ac2_vacuous_test_fails_the_probe_with_the_named_message(repo):
    before = (repo / "src.py").read_bytes()
    src = (repo / "src.py").resolve()
    res = run_probe(repo, "src.py", PINNED, pytest_cmd("test_vacuous.py"))
    assert res.returncode == 1, res.stdout + res.stderr
    assert f"PROBE FAILED: test stayed green with {src}:2-3 removed" in res.stdout
    assert (repo / "src.py").read_bytes() == before
    assert sidecars(repo) == []


# --- AC3: a dirty target ------------------------------------------------------------------


def test_ac3_dirty_target_is_refused_untouched(repo):
    dirty = SRC + "\n# uncommitted work\n"
    (repo / "src.py").write_text(dirty, encoding="utf-8")
    res = run_probe(repo, "src.py", PINNED, pytest_cmd("test_real.py"))
    assert res.returncode == 2, res.stdout + res.stderr
    assert "REFUSED" in res.stderr and "dirty" in res.stderr
    assert (repo / "src.py").read_text(encoding="utf-8") == dirty
    assert sidecars(repo) == []


def test_ac3_untracked_target_is_refused(repo):
    (repo / "extra.py").write_text("X = 1\n", encoding="utf-8")
    res = run_probe(repo, "extra.py", "1", pytest_cmd("test_real.py"))
    assert res.returncode == 2
    assert "dirty" in res.stderr
    assert (repo / "extra.py").read_text(encoding="utf-8") == "X = 1\n"


def test_ac3_outside_a_git_repo_is_refused(tmp_path):
    loose = tmp_path / "loose"
    loose.mkdir()
    (loose / "src.py").write_text(SRC, encoding="utf-8")
    res = run_probe(loose, "src.py", PINNED, "true")
    assert res.returncode == 2
    assert "not inside a git repository" in res.stderr
    assert (loose / "src.py").read_text(encoding="utf-8") == SRC


# --- AC4: the three-way termination story -------------------------------------------------


def test_ac4a_child_test_killed_mid_run_restores_immediately(repo):
    """The test CHILD dies by signal. The runner's `finally` restores at once, and the
    signalled rc is INDETERMINATE — never a kill."""
    before = (repo / "src.py").read_bytes()
    cmd = counting_script(repo, "selfkill.sh", "kill -9 $$")
    res = run_probe(repo, "src.py", PINNED, cmd)
    assert res.returncode == 2, res.stdout + res.stderr
    assert "INDETERMINATE" in res.stderr
    assert (repo / "src.py").read_bytes() == before
    assert sidecars(repo) == []


def test_ac4b_runner_sigterm_unwinds_the_finally_and_restores(repo):
    """SIGTERM the RUNNER mid-step-3: the installed handler raises, `finally` restores, and
    the slow test child is killed with its process group."""
    before = (repo / "src.py").read_bytes()
    cmd = counting_script(repo, "slow.sh", "touch step3-started\nsleep 60\nexit 1")
    proc = subprocess.Popen(
        [sys.executable, str(PROBE), "--file", "src.py", "--lines", PINNED, "--test", cmd],
        cwd=str(repo),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    marker = repo / "step3-started"
    deadline = time.time() + 60
    while not marker.exists() and time.time() < deadline:
        if proc.poll() is not None:
            break
        time.sleep(0.05)
    assert marker.exists(), "step 3 never started"
    proc.send_signal(signal.SIGTERM)
    out, err = proc.communicate(timeout=60)
    assert proc.returncode == 2, out + err
    assert "restored" in err
    assert (repo / "src.py").read_bytes() == before
    assert sidecars(repo) == []


def test_ac4c_dead_pid_sidecar_is_reconciled_at_startup(repo):
    """The SIGKILL case, simulated exactly as it would be found on disk (a mutated file plus
    a sidecar whose pid is dead) — never by actually SIGKILLing a runner in CI."""
    dead = subprocess.Popen([sys.executable, "-c", "pass"])
    dead.wait()
    src = repo / "src.py"
    sidecar = repo / f"src.py.mutprobe.{dead.pid}.bak"
    sidecar.write_bytes(SRC.encode())
    src.write_text(mp.comment_out(SRC, 2, 3), encoding="utf-8")  # the abandoned mutation

    res = run_probe(repo, "src.py", PINNED, pytest_cmd("test_real.py"))
    assert "RECONCILED: restored" in res.stdout
    assert str(dead.pid) in res.stdout
    assert not sidecar.exists()
    # Reconcile ran BEFORE the clean-file gate, so the probe then proceeds normally.
    assert res.returncode == 0, res.stdout + res.stderr
    assert src.read_text(encoding="utf-8") == SRC


def test_ac4c_dead_pid_sidecar_matching_the_file_is_just_removed(repo):
    """A probe that restored and died before unlinking leaves a STALE sidecar: nothing is
    rewritten, the sidecar is dropped."""
    dead = subprocess.Popen([sys.executable, "-c", "pass"])
    dead.wait()
    sidecar = repo / f"src.py.mutprobe.{dead.pid}.bak"
    sidecar.write_bytes(SRC.encode())
    res = run_probe(repo, "src.py", PINNED, pytest_cmd("test_real.py"))
    assert "RECONCILED: removed stale sidecar" in res.stdout
    assert not sidecar.exists()
    assert res.returncode == 0


def test_ac8_live_pid_sidecar_is_never_touched(repo):
    """A LIVE pid is a concurrent probe mid-run. Restoring its file out from under it is the
    defect the dead-pid check exists to prevent."""
    live = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
    try:
        other = repo / "consts.py"
        other.write_text("LIMIT = 999\n", encoding="utf-8")  # a concurrent probe's mutation
        sidecar = repo / f"consts.py.mutprobe.{live.pid}.bak"
        sidecar.write_bytes(CONSTS.encode())
        res = run_probe(repo, "src.py", PINNED, pytest_cmd("test_real.py"))
        assert res.returncode == 0, res.stdout + res.stderr
        assert "RECONCILED" not in res.stdout
        assert sidecar.read_bytes() == CONSTS.encode()
        assert other.read_text(encoding="utf-8") == "LIMIT = 999\n"
    finally:
        live.kill()
        live.wait()


# --- AC5: an already-red test -------------------------------------------------------------


def test_ac5_already_red_test_is_refused_with_a_distinct_message(repo):
    before = (repo / "src.py").read_bytes()
    res = run_probe(repo, "src.py", PINNED, pytest_cmd("test_red.py"))
    assert res.returncode == 2, res.stdout + res.stderr
    assert "ALREADY RED" in res.stderr
    assert "PROBE PASSED" not in res.stdout
    assert (repo / "src.py").read_bytes() == before
    assert sidecars(repo) == []


# --- AC6: a range whose removal breaks syntax ---------------------------------------------


def test_ac6_syntax_breaking_range_is_rejected_not_killed(repo):
    """A vacuous test paired with a syntax-breaking range is the fake-kill scenario: the
    suite WOULD go red (at import), and a naive probe would report it pinned."""
    before = (repo / "src.py").read_bytes()
    res = run_probe(repo, "src.py", SOLE_STATEMENT, pytest_cmd("test_vacuous.py"))
    assert res.returncode == 2, res.stdout + res.stderr
    assert "REJECTED RANGE" in res.stderr
    assert "PROBE PASSED" not in res.stdout
    assert (repo / "src.py").read_bytes() == before
    assert sidecars(repo) == []


def test_ac6_syntax_breaking_range_is_rejected_with_a_real_test_too(repo):
    res = run_probe(repo, "src.py", SOLE_STATEMENT, pytest_cmd("test_real.py"))
    assert res.returncode == 2
    assert "REJECTED RANGE" in res.stderr
    assert (repo / "src.py").read_text(encoding="utf-8") == SRC


def test_ac6_shell_syntax_breaking_range_is_rejected(repo):
    """`bash -n` is the .sh half of gate 2b — an emptied function body is a syntax error."""
    res = run_probe(repo, "script.sh", "3", "bash test_script.sh")
    assert res.returncode == 2, res.stdout + res.stderr
    assert "REJECTED RANGE" in res.stderr
    assert (repo / "script.sh").read_text(encoding="utf-8") == SCRIPT_SH


def test_ac6_import_breaking_range_is_indeterminate_not_killed(repo):
    """Syntactically valid but collection-breaking: pytest reports an ERROR, not a failed
    test, so no kill may be claimed."""
    res = run_probe(repo, "consts.py", "1", pytest_cmd("test_consts.py"))
    assert res.returncode == 2, res.stdout + res.stderr
    assert "INDETERMINATE" in res.stderr
    assert (repo / "consts.py").read_text(encoding="utf-8") == CONSTS
    assert sidecars(repo) == []


# --- AC7: a concurrent writer -------------------------------------------------------------


def test_ac7_concurrent_writer_makes_the_restore_refuse_loudly(repo):
    """The dangerous case: a blind restore would erase the concurrent edit AND leave
    `git diff --quiet` green, so the loss would be invisible. Refuse, keep the sidecar."""
    cmd = counting_script(repo, "writer.sh", "printf '# CONCURRENT\\n' >> src.py\nexit 1")
    res = run_probe(repo, "src.py", PINNED, cmd)
    assert res.returncode == 3, res.stdout + res.stderr
    assert "RESTORE REFUSED" in res.stderr
    after = (repo / "src.py").read_text(encoding="utf-8")
    assert "# CONCURRENT" in after, "the concurrent writer's edit was clobbered"
    assert "#     if n < 0:" in after, "the probe's own mutation vanished — restore ran anyway"
    kept = sidecars(repo)
    assert len(kept) == 1, "the sidecar is the only surviving copy of the original"
    assert kept[0].read_bytes() == SRC.encode()


def test_ac7_concurrent_writer_restoring_the_original_is_accepted(repo):
    """The benign sibling: if the concurrent write left exactly the original bytes, the end
    state is already correct — no refusal, no rewrite, sidecar dropped."""
    body = "cat src.py.orig > src.py\nexit 1"
    (repo / "src.py.orig").write_text(SRC, encoding="utf-8")
    cmd = counting_script(repo, "restorer.sh", body)
    res = run_probe(repo, "src.py", PINNED, cmd)
    assert "RESTORE REFUSED" not in res.stderr
    assert (repo / "src.py").read_text(encoding="utf-8") == SRC
    assert sidecars(repo) == []


# --- input gates + no-collateral-damage ---------------------------------------------------


def test_unprobeable_extension_is_refused(repo):
    (repo / "notes.txt").write_text("hello\n", encoding="utf-8")
    git(repo, "add", "notes.txt")
    git(repo, "commit", "-q", "-m", "notes")
    res = run_probe(repo, "notes.txt", "1", "true")
    assert res.returncode == 2
    assert "not a probeable extension" in res.stderr


def test_missing_file_is_refused(repo):
    res = run_probe(repo, "nope.py", "1", "true")
    assert res.returncode == 2
    assert "not an existing file" in res.stderr


def test_range_past_eof_is_refused_before_any_run(repo):
    res = run_probe(repo, "src.py", "99-100", pytest_cmd("test_real.py"))
    assert res.returncode == 2
    assert "outside" in res.stderr
    assert (repo / "src.py").read_text(encoding="utf-8") == SRC


def test_the_test_command_runs_inside_the_repo(repo):
    """The `--test` command's cwd is the repo root, not wherever the operator stood."""
    cmd = counting_script(repo, "pwd.sh", "pwd > where\n" + pytest_cmd("test_real.py"))
    res = run_probe(repo, "src.py", PINNED, cmd)
    assert res.returncode == 0, res.stdout + res.stderr
    assert Path((repo / "where").read_text().strip()).resolve() == repo


def test_no_git_stash_or_checkout_anywhere_in_the_tool():
    """The restore authority is the in-memory copy plus its sidecar. `git stash` /
    `git checkout --` would silently move the operator's OTHER work."""
    source = PROBE.read_text(encoding="utf-8")
    # Either word as a STANDALONE quoted token would be an argv element of a subprocess
    # call. A prose mention is fine, and is exactly what the module's own refusal message
    # carries ("commit or stash your own work first").
    assert not re.search(r"""['"]stash['"]""", source)
    assert not re.search(r"""['"]checkout['"]""", source)


def test_timeout_is_indeterminate_never_a_kill(repo):
    before = (repo / "src.py").read_bytes()
    cmd = counting_script(repo, "hang.sh", "sleep 120")
    res = run_probe(repo, "src.py", PINNED, cmd, timeout=3)
    assert res.returncode == 2, res.stdout + res.stderr
    assert "timed out" in res.stderr
    assert (repo / "src.py").read_bytes() == before
    assert sidecars(repo) == []
