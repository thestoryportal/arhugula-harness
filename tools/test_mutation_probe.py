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

import ast
import contextlib
import hashlib
import os
import re
import shlex
import signal
import stat
import subprocess
import sys
import time
from collections.abc import Iterator
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
# The subdirectory target's own real test (implicit namespace package — no __init__.py).
TEST_PKG = """import pkg.mod


def test_negative():
    assert pkg.mod.classify(-1) == "negative"
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

# A module whose line 2 can be commented out leaving GRAMMAR-valid but UNCOMPILABLE source
# (the `nonlocal` loses its binding). `ast.parse` accepts it; `compile` does not.
#   1 def counter():
#   2     count = 0
NONLOCAL_SRC = """def counter():
    count = 0

    def bump():
        nonlocal count
        count += 1
        return count

    return bump
"""
NONLOCAL_ORPHAN_LINE = "2"

# The bytes a probe of SRC:2-3 would have put on disk — the mutation witness a crash-shaped
# sidecar must record for the reconcile to consider itself applicable.
MUTATED_FIXTURE = mp.comment_out(SRC, 2, 3).encode()
# A stand-in git blob oid for the PURE tests (they never touch a repo).
OID = "0" * 40

PY = shlex.quote(sys.executable)


def plant_sidecar(path: Path, payload: bytes, mutated: bytes, index_oid: str | None = None) -> None:
    """Write a sidecar in the tool's real on-disk format, the way a crashed probe would have
    left it. Tests must never hand-roll the format.

    `mutated` is the APPLICABILITY witness — the bytes the crashed probe had put on the
    target — and the reconcile restores only while the target still matches it.
    `index_oid` is the GIT-IDENTITY witness; when omitted it is read from the repo for the
    target this sidecar names, i.e. exactly what a real probe would have recorded. The
    mismatch cases pass it explicitly."""
    if index_oid is None:
        m = mp.SIDECAR_RE.match(path.name)
        assert m is not None, f"{path.name} is not a sidecar name"
        index_oid = mp.index_oid(path.parent / m.group("base"), path.parent) or ""
    path.write_bytes(mp.sidecar_bytes(payload, mutated, index_oid))


def reap_grandchild(repo: Path) -> None:
    """Kill the escaped grandchild `grandchild.py` spawned. It is in its own session, so
    nothing else will reap it — the test owns that cleanup."""
    marker = repo / "grandchild.pid"
    for _ in range(100):
        if marker.exists():
            break
        time.sleep(0.05)
    with contextlib.suppress(OSError, ValueError):
        os.kill(int(marker.read_text().strip()), signal.SIGKILL)


def sidecar_payload(path: Path) -> bytes:
    """The verified payload of a sidecar on disk; fails the test if integrity is broken."""
    sidecar, err = mp.parse_sidecar(path.read_bytes())
    assert err is None, f"sidecar {path} failed its integrity check: {err}"
    assert sidecar is not None
    return sidecar.original


def pytest_cmd(*files: str) -> str:
    """A pytest command for the throwaway repo. `-p no:cacheprovider` keeps a `.pytest_cache`
    out of the probed tree."""
    return f"{PY} -m pytest -q -p no:cacheprovider {' '.join(files)}"


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=str(repo), capture_output=True, text=True, check=False
    )


@pytest.fixture
def repo(tmp_path: Path) -> Iterator[Path]:
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
        # A target in a SUBDIRECTORY, so a test can make that directory read-only without
        # touching the repo root (where the test scripts and their counters live).
        "pkg/mod.py": SRC,
        "test_pkg.py": TEST_PKG,
        "nonlocal_mod.py": NONLOCAL_SRC,
        # A grandchild that ESCAPES the test command's process group (its own session) and
        # keeps the inherited stdout/stderr pipes open long after the shell exits.
        "grandchild.py": (
            "import os\nimport time\n\n"
            "os.setsid()\n"
            'with open("grandchild.pid", "w") as fh:\n'
            "    fh.write(str(os.getpid()))\n"
            "time.sleep(300)\n"
        ),
        # A NON-pytest checker, deliberately: the compile-stage defect is only a false
        # PROBE PASSED under the generic heuristic, where any nonzero reads as a kill.
        "check_nonlocal.sh": (
            "#!/usr/bin/env bash\n"
            f"{PY} -c 'import nonlocal_mod; b = nonlocal_mod.counter(); assert b() == 1'\n"
        ),
        # `secret.py` is IGNORED and never created here — the gitignore test creates it.
        ".gitignore": "secret.py\n",
    }
    for name, body in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    assert git(root, "init", "-q", "-b", "main").returncode == 0
    # LOCAL identity only — a global git config must never be read or written by a test.
    assert git(root, "config", "user.email", "probe@test.invalid").returncode == 0
    assert git(root, "config", "user.name", "Probe Test").returncode == 0
    assert git(root, "config", "commit.gpgsign", "false").returncode == 0
    assert git(root, "add", *files).returncode == 0
    commit = git(root, "commit", "-q", "-m", "fixtures")
    assert commit.returncode == 0, commit.stderr
    yield root
    # A test that made a directory read-only must not break tmp_path teardown.
    for d in [root, *(p for p in root.rglob("*") if p.is_dir())]:
        with contextlib.suppress(OSError):
            d.chmod(0o755)


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
    # `*.mutprobe.*` covers ALL THREE names — the published `.bak`, the sidecar-staging
    # `.tmp`, and the mutation/restore-staging `.new`
    # staging fragment (codex round-3 P1).
    # `.lock` files are PERMANENT BY DESIGN (never unlinked — removing a held flock's file
    # is the classic re-create race). Everything else must be gone.
    leftover = [
        f
        for f in [*(REAL_REPO / "tools").rglob("*.mutprobe.*"), *REAL_REPO.glob("*.mutprobe.*")]
        if f.suffix != ".lock"
    ]
    assert leftover == [], leftover


def run_probe(
    repo: Path,
    file: str,
    lines: str,
    test: str,
    timeout: int | None = None,
    wall_timeout: float = 300,
) -> subprocess.CompletedProcess[str]:
    """Drive the probe as a subprocess. `timeout` is the probe's own `--timeout`;
    `wall_timeout` bounds OUR wait on it, so a probe that hangs fails the test instead of
    hanging the suite."""
    cmd = [sys.executable, str(PROBE), "--file", file, "--lines", lines, "--test", test]
    if timeout is not None:
        cmd += ["--timeout", str(timeout)]
    return subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True, timeout=wall_timeout)


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


@pytest.mark.parametrize("rc", [2, 3, 4, 5])
def test_p1_pytest_abort_codes_with_a_stale_failed_summary_are_not_kills(rc):
    """codex round-1 P1: pytest 2/3/4 (interrupt / internal error / usage error) can still
    PRINT an `N failed` summary accumulated before the abort. Only rc 1
    (`ExitCode.TESTS_FAILED`) means "tests ran and some failed"; anything else with a
    failed count is an aborted run, and attributing it to the mutation is a false
    PROBE PASSED."""
    verdict, why = mp.classify_step3(rc, "= 1 failed, 3 passed in 0.4s =", True)
    assert verdict == mp.INDETERMINATE
    assert f"exited {rc}, not 1" in why
    assert "before aborting" in why


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
        # codex round-4 P1: the `py.test` entry-point alias. Missing these meant a
        # collection error under py.test fell through to the LENIENT generic branch.
        ("py.test -q x.py", True),
        (".venv/bin/py.test -q", True),
        ("uv run py.test", True),
        ("bash ./py.test", True),
        (r"Scripts\pytest.exe -q", True),
        # Over-matching is deliberate and SAFE — the pytest branch is the stricter one, so
        # a false positive can only downgrade a kill to a refusal, never invent a pass.
        ("bash ./pytest-shim.sh", True),
        ("npm run pytest:ci", True),
        # A token that does not START with the entry-point name is not pytest.
        ("bash tools/hooks/test_postedit_lint.sh", False),
        ("bash my_pytest_helper.sh", False),
        ("bash copy.test", False),
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


def test_p2b_untracked_target_is_refused_by_the_witness_gate(repo):
    """codex round-2 P2b: an untracked file has no ordinary index entry, so both of the
    probe's witnesses would compare against nothing."""
    (repo / "extra.py").write_text("X = 1\n", encoding="utf-8")
    res = run_probe(repo, "extra.py", "1", pytest_cmd("test_real.py"))
    assert res.returncode == 2
    assert "not tracked by git" in res.stderr
    assert "untracked" in res.stderr
    assert (repo / "extra.py").read_text(encoding="utf-8") == "X = 1\n"


def test_p2b_gitignored_target_is_refused(repo):
    """The sharpest of the four: `git status --porcelain` reports NOTHING for an ignored
    file (asserted below as the actual hole), so the dirty gate alone waves it straight
    through and the probe would mutate it while both witnesses passed vacuously."""
    secret = repo / "secret.py"
    secret.write_text(SRC, encoding="utf-8")
    assert git(repo, "status", "--porcelain", "--", "secret.py").stdout == "", (
        "fixture precondition: an ignored file must be INVISIBLE to the dirty gate"
    )
    res = run_probe(repo, "secret.py", PINNED, pytest_cmd("test_real.py"))
    assert res.returncode == 2
    assert "not tracked by git" in res.stderr
    assert "IGNORED" in res.stderr
    assert secret.read_text(encoding="utf-8") == SRC
    assert sidecars(repo) == []


@pytest.mark.parametrize(
    ("flag", "needle", "clear"),
    [
        ("--skip-worktree", "SKIP-WORKTREE", "--no-skip-worktree"),
        ("--assume-unchanged", "ASSUME-UNCHANGED", "--no-assume-unchanged"),
    ],
)
def test_p2b_index_suppression_flags_are_refused(repo, flag, needle, clear):
    """Tracked, clean, and still unwitnessable: both flags tell git to stop looking at the
    worktree copy, so `status` and `diff` answer clean no matter what the probe writes."""
    assert git(repo, "update-index", flag, "src.py").returncode == 0
    before = (repo / "src.py").read_bytes()
    res = run_probe(repo, "src.py", PINNED, pytest_cmd("test_real.py"))
    assert res.returncode == 2, res.stdout + res.stderr
    assert needle in res.stderr
    assert clear in res.stderr, "the refusal must tell the operator how to clear the flag"
    assert (repo / "src.py").read_bytes() == before
    assert sidecars(repo) == []


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
    abandoned = mp.comment_out(SRC, 2, 3).encode()
    plant_sidecar(sidecar, SRC.encode(), abandoned)
    src.write_bytes(abandoned)  # the target still holds the abandoned mutation

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
    # The target matches the sidecar's ORIGINAL, so the stale branch must fire before the
    # applicability gate — the recorded mutation deliberately matches nothing on disk.
    plant_sidecar(sidecar, SRC.encode(), mp.comment_out(SRC, 2, 3).encode())
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
        plant_sidecar(sidecar, CONSTS.encode(), b"LIMIT = 999\n")
        res = run_probe(repo, "src.py", PINNED, pytest_cmd("test_real.py"))
        assert res.returncode == 0, res.stdout + res.stderr
        assert "RECONCILED" not in res.stdout
        assert sidecar_payload(sidecar) == CONSTS.encode()
        assert other.read_text(encoding="utf-8") == "LIMIT = 999\n"
    finally:
        live.kill()
        live.wait()


# --- AC5: an already-red test -------------------------------------------------------------


def test_p1a_a_baseline_that_writes_the_target_is_refused(repo):
    """codex round-6 P1a: an autofixer/generator/snapshot-updating test can PASS while
    rewriting the very file being probed. With the snapshot taken before the baseline, the
    mutation overwrote the test's edit and the restore put back the already-stale bytes —
    the test's work silently discarded behind an exit 0."""
    (repo / "autofix.sh").write_text(
        "#!/usr/bin/env bash\nprintf '# autofixed by the test\\n' >> src.py\nexit 0\n",
        encoding="utf-8",
    )
    res = run_probe(repo, "src.py", PINNED, "bash autofix.sh")
    assert res.returncode == 2, res.stdout + res.stderr
    assert "TEST COMMAND modified" in res.stderr
    # The file is left EXACTLY as the test wrote it — nothing restored over the top.
    assert (repo / "src.py").read_text(encoding="utf-8") == SRC + "# autofixed by the test\n"
    assert sidecars(repo) == [], "nothing may be published before this refusal"


def test_p1a_the_snapshot_is_read_after_the_baseline_runs():
    """The ordering half of P1a, asserted STRUCTURALLY.

    There is deliberately no behavioural case for the ordering ALONE: git compares content,
    so any baseline edit the ordering would matter for is exactly the edit the step-1b
    re-check already refuses. The ordering is defence in depth — it makes "the snapshot is
    what is on disk at mutation time" true by construction rather than by the git check
    happening to notice. So the construction itself is the witness.
    """
    tree = ast.parse(PROBE.read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "probe")
    baselines = [
        c.lineno
        for c in ast.walk(fn)
        if isinstance(c, ast.Call) and getattr(c.func, "id", "") == "run_shell"
    ]
    snapshots = [
        c.lineno
        for c in ast.walk(fn)
        if isinstance(c, ast.Call)
        and isinstance(c.func, ast.Attribute)
        and c.func.attr == "read_bytes"
        and getattr(c.func.value, "id", "") == "target"
    ]
    assert baselines, "probe() must run the baseline through run_shell"
    assert snapshots, "probe() must snapshot the target"
    assert min(snapshots) > min(baselines), (
        "the restore snapshot is read BEFORE the baseline runs — a baseline that writes the "
        "target would make it stale"
    )


def test_p1a_a_readonly_baseline_still_probes_normally(repo):
    """The positive control: a baseline that merely READS the target is unaffected."""
    res = run_probe(repo, "src.py", PINNED, pytest_cmd("test_real.py"))
    assert res.returncode == 0, res.stdout + res.stderr
    assert "TEST COMMAND modified" not in res.stderr


@pytest.mark.parametrize("attempt", range(3))
def test_primary_simultaneous_probes_of_one_target_cannot_both_proceed(repo, attempt):
    """merge-gate lens 1, the REPRODUCED defect (5 of 6 pre-fix launches misbehaved).

    Two probes of the SAME file launched together used to clear both point-in-time git gates
    within milliseconds, both snapshot the same original and both publish. The loser's step 3
    then ran against the file the winner had already RESTORED, saw green, and reported
    `PROBE FAILED: test stayed green` for a genuinely pinned range — tree clean, no sidecar,
    no warning. Exactly one probe may now proceed; the other is refused at the lock.

    The baseline is slowed so the second launch reliably arrives while the first still holds
    the lock — otherwise the two could legitimately serialize and the race would not be
    exercised at all.
    """
    (repo / "slow_real.sh").write_text(
        f"#!/usr/bin/env bash\nsleep 2\n{pytest_cmd('test_real.py')}\n", encoding="utf-8"
    )
    argv = [
        sys.executable, str(PROBE),
        "--file", "src.py", "--lines", PINNED, "--test", "bash slow_real.sh",
    ]  # fmt: skip
    launched = [
        subprocess.Popen(argv, cwd=str(repo), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True)
        for _ in range(2)
    ]  # fmt: skip
    outputs = [pr.communicate(timeout=180) for pr in launched]
    codes = [pr.returncode for pr in launched]

    assert 1 not in codes, (
        "a probe reported PROBE FAILED while another was mutating the same file — the "
        f"silent false verdict this lock exists to prevent (codes={codes})"
    )
    assert sorted(codes) == [0, 2], f"expected one winner and one lock-refusal, got {codes}"
    refused = outputs[codes.index(2)][1]
    assert "another mutation probe is already running" in refused, refused
    assert (repo / "src.py").read_text(encoding="utf-8") == SRC
    assert sidecars(repo) == []
    assert git(repo, "status", "--porcelain", "--", "src.py").stdout == ""


def test_primary_the_lock_is_target_scoped_not_global(repo):
    """Different files must still probe concurrently — the lock excludes same-target runs,
    not parallelism."""
    (repo / "slow_real.sh").write_text(
        f"#!/usr/bin/env bash\nsleep 2\n{pytest_cmd('test_real.py')}\n", encoding="utf-8"
    )
    (repo / "slow_consts.sh").write_text(
        f"#!/usr/bin/env bash\nsleep 2\n{pytest_cmd('test_consts.py')}\n", encoding="utf-8"
    )

    def launch(target: str, lines: str, script: str):
        return subprocess.Popen(
            [sys.executable, str(PROBE), "--file", target, "--lines", lines,
             "--test", f"bash {script}"],
            cwd=str(repo), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )  # fmt: skip

    a = launch("src.py", PINNED, "slow_real.sh")
    b = launch("consts.py", "1", "slow_consts.sh")
    out_a, out_b = a.communicate(timeout=180), b.communicate(timeout=180)
    assert a.returncode == 0, out_a
    assert b.returncode == 0, out_b


def test_primary_a_stale_lock_file_does_not_block_a_later_probe(repo):
    """An flock dies with its holder, so a lock FILE left by a SIGKILLed probe is inert.
    (This is why there is no dead-pid rule for the lock, unlike the sidecar.)"""
    stale = repo / "src.py.mutprobe.lock"
    stale.write_text("pid=999999\n", encoding="utf-8")
    res = run_probe(repo, "src.py", PINNED, pytest_cmd("test_real.py"))
    assert res.returncode == 0, res.stdout + res.stderr
    assert stale.exists(), "the lock file is never unlinked (re-create race)"


def test_second_guard_interference_downgrades_a_green_step3_to_indeterminate(repo):
    """The cheap half, independent of the lock: if the target no longer holds THIS probe's
    mutation when the test finishes, the run measured a different file. The dangerous shape
    is exactly this one — bytes back to the original, suite green, which would otherwise be
    reported as `PROBE FAILED` for a pinned range."""
    (repo / "src.py.orig").write_text(SRC, encoding="utf-8")
    cmd = counting_script(repo, "restorer.sh", "cat src.py.orig > src.py\nexit 0")
    res = run_probe(repo, "src.py", PINNED, cmd)
    assert res.returncode == 2, res.stdout + res.stderr
    assert "PROBE FAILED" not in res.stdout, "a false unpinned verdict escaped the guard"
    assert "no longer held this probe's mutation" in res.stderr
    assert (repo / "src.py").read_text(encoding="utf-8") == SRC


def test_secondary_c2_an_already_gone_sidecar_is_not_reported_as_partial(repo):
    """`_release` is the one definition of "released": already-gone counts. The reconcile
    used to call that a RECONCILE PARTIAL and send the operator hunting for a file that was
    correctly absent."""
    assert mp._release(repo / "nothing-here.mutprobe.1.bak") is None
    source = PROBE.read_text(encoding="utf-8")
    fn_start = source.index("def reconcile_sidecars(")
    fn_end = source.index("\ndef ", fn_start + 1)
    assert "sc.unlink()" not in source[fn_start:fn_end], (
        "reconcile removes sidecars directly instead of through _release, so "
        "already-gone is reported as a failure again"
    )


def test_secondary_f_a_staged_mutation_names_the_index_not_the_worktree(repo):
    """`git diff --quiet` compares worktree-vs-index, so a concurrent `git add` of the
    mutated file fails it even though the worktree is exactly right. Still a failure — a
    staged mutation is a real problem — but the diagnosis must name the INDEX."""
    cmd = counting_script(repo, "stager.sh", "git add src.py\nexit 1")
    res = run_probe(repo, "src.py", PINNED, cmd)
    assert res.returncode == 3, res.stdout + res.stderr
    assert "RESTORE FAILED" in res.stderr
    assert "it is the INDEX that differs" in res.stderr
    assert "the working tree still differs" not in res.stderr
    # The worktree really is correct — which is what makes the old message wrong.
    assert (repo / "src.py").read_text(encoding="utf-8") == SRC


def test_secondary_d_the_abandoned_process_note_is_honest():
    """Doc-only: what is abandoned is a LIVE unreachable process that can still write the
    target after the final verify — not merely a stdout tail."""
    assert "still RUNNING" in mp.ABANDONED_OUTPUT_NOTE
    # Collapse the wrapping — these are prose assertions, and the docstring is hard-wrapped.
    docstring = " ".join(PROBE.read_text(encoding="utf-8").split('"""')[1].split())
    assert "AFTER the final restore verification has passed" in docstring
    # gate 0 must no longer imply the git gates alone make simultaneous probes safe.
    assert "F.mutprobe.lock" in docstring
    assert "reproduced 5 times in 6" in docstring


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


def test_p1_pytest_abort_with_a_stale_failed_summary_is_refused_end_to_end(repo):
    """The P1 defect end to end: a pytest run that PRINTS `1 failed` and then exits 2 must
    come out as exit 2, never as a PROBE PASSED. The shim is named so that
    `looks_like_pytest` takes the strict pytest path (the `/pytest` token)."""
    before = (repo / "src.py").read_bytes()
    cmd = counting_script(repo, "pytest-shim.sh", "echo '= 1 failed, 3 passed in 0.4s ='\nexit 2")
    assert mp.looks_like_pytest(f"bash ./{cmd.split()[-1]}")
    res = run_probe(repo, "src.py", PINNED, f"bash ./{cmd.split()[-1]}")
    assert res.returncode == 2, res.stdout + res.stderr
    assert "PROBE PASSED" not in res.stdout
    assert "exited 2, not 1" in res.stderr
    assert (repo / "src.py").read_bytes() == before
    assert sidecars(repo) == []


def test_p2_compile_stage_error_is_rejected_not_killed(repo):
    """codex round-3 P2: `ast.parse` stops at the grammar. Commenting out the binding line
    leaves an orphaned `nonlocal` — well-formed source that only the COMPILE stage rejects.
    The mutated file then failed at import, and under a non-pytest command that nonzero read
    as a kill: a false PROBE PASSED on lines nothing pins."""
    mutated = mp.comment_out(NONLOCAL_SRC, 2, 2)
    ast.parse(mutated)  # precondition: grammar-valid, so this is NOT a plain SyntaxError
    with pytest.raises(SyntaxError):
        compile(mutated, "t.py", "exec", dont_inherit=True)

    before = (repo / "nonlocal_mod.py").read_bytes()
    res = run_probe(repo, "nonlocal_mod.py", NONLOCAL_ORPHAN_LINE, "bash check_nonlocal.sh")
    assert res.returncode == 2, res.stdout + res.stderr
    assert "REJECTED RANGE" in res.stderr
    assert "nonlocal" in res.stderr
    assert "PROBE PASSED" not in res.stdout
    assert (repo / "nonlocal_mod.py").read_bytes() == before
    assert sidecars(repo) == []


def test_p2_syntax_gate_runs_the_full_compile_not_just_the_grammar():
    """The pure half, over both classic compile-stage errors."""
    orphan_nonlocal = mp.comment_out(NONLOCAL_SRC, 2, 2)
    assert mp.syntax_error("py", orphan_nonlocal, "t.py") is not None
    assert mp.syntax_error("py", "for i in [1]:\n    pass\n\nbreak\n", "t.py") is not None
    assert mp.syntax_error("py", "def f():\n    return 1\n", "t.py") is None


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
    assert sidecar_payload(kept[0]) == SRC.encode()


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


def test_p2b_git_verification_runs_on_the_no_write_restore_path(repo):
    """codex round-1 P2b: matching CONTENT is not the same claim as a clean working tree.

    A concurrent process puts the original bytes back but leaves the index holding a
    different version. The no-bytes-to-write success path must still run `git diff --quiet`
    before releasing the sidecar — otherwise the probe drops the only remaining copy of the
    original while printing a verification it never ran.
    """
    (repo / "src.py.orig").write_text(SRC, encoding="utf-8")
    body = (
        "printf '# STAGED\\n' >> src.py\n"  # index will hold mutated + this
        "git add src.py\n"
        "cat src.py.orig > src.py\n"  # worktree back to the ORIGINAL bytes
        "exit 1"
    )
    cmd = counting_script(repo, "stager.sh", body)
    res = run_probe(repo, "src.py", PINNED, cmd)
    assert res.returncode == 3, res.stdout + res.stderr
    assert "RESTORE FAILED" in res.stderr
    assert "git diff --quiet" in res.stderr
    assert (repo / "src.py").read_text(encoding="utf-8") == SRC
    kept = sidecars(repo)
    assert len(kept) == 1, "the sidecar was released without a passing git verification"
    assert sidecar_payload(kept[0]) == SRC.encode()


def test_p2a_sidecar_release_failure_is_loud_and_nonzero(repo):
    """codex round-2 P2a: the file IS restored and git-verified, but the sidecar SURVIVES.

    Swallowing that leaves a dead-pid sidecar which the NEXT run's reconcile replays over
    whatever legitimate edits the file has accumulated since — so it must be loud and
    nonzero, while still not being misreported as a restore failure.

    Honest filesystem fixture, no monkeypatching and no test-only hook: the test command
    runs while the mutation is on disk and the sidecar already exists, and makes the
    TARGET'S DIRECTORY read-only. POSIX then still permits rewriting the EXISTING target
    file — directory write permission governs creating and removing ENTRIES, not modifying
    a file's contents — so the restore write and `git diff --quiet` both succeed and ONLY
    the unlink fails. (Verified live: write OK, unlink EACCES, `git diff` unaffected.)
    """
    pkg = repo / "pkg"
    cmd = counting_script(repo, "lockdir.sh", "chmod a-w pkg\nexit 1")
    try:
        res = run_probe(repo, "pkg/mod.py", PINNED, cmd)
        assert res.returncode == 3, res.stdout + res.stderr
        assert "SIDECAR NOT RELEASED" in res.stderr
        # NOT misreported as a restore failure — the file really is back.
        assert "RESTORE FAILED" not in res.stderr
        assert "RESTORE REFUSED" not in res.stderr
        # codex round-6 P1b: this fixture now ALSO exercises the documented fallback — the
        # read-only directory forbids the atomic rename, so the restore degrades to a
        # verified direct write and must SAY so rather than degrade silently. The outcome
        # of the original witness is unchanged, which is why it was kept as-is.
        assert "denies new entries" in res.stderr
        assert "direct write instead of an atomic replace" in res.stderr
        assert (pkg / "mod.py").read_text(encoding="utf-8") == SRC
        kept = sorted(pkg.glob("*.mutprobe.*.bak"))
        assert len(kept) == 1
        assert str(kept[0]) in res.stderr, "the message must name the retained sidecar"
        assert "DELETE" in res.stderr, "the message must tell the operator what to do"
    finally:
        pkg.chmod(0o755)


def test_p2a_a_clean_run_reports_the_released_state(repo):
    """The positive control for the state machine: an ordinary pass ends RESTORED, so the
    nonzero release path above is not simply always-on."""
    res = run_probe(repo, "pkg/mod.py", PINNED, pytest_cmd("test_pkg.py"))
    assert res.returncode == 0, res.stdout + res.stderr
    assert "SIDECAR NOT RELEASED" not in res.stderr
    assert sorted((repo / "pkg").glob("*.mutprobe.*.bak")) == []


def test_p1_py_test_alias_takes_the_strict_classifier_end_to_end(repo):
    """codex round-4 P1: a collection error under the `py.test` entry-point alias exits 2.
    Unrecognized, it fell through to the GENERIC branch where any nonzero is a kill — a
    false PROBE PASSED. Recognized, rc 2 is not `TESTS_FAILED` and the run is
    INDETERMINATE."""
    before = (repo / "src.py").read_bytes()
    cmd = counting_script(repo, "py.test", "echo '= 1 error in 0.12s ='\nexit 2")
    assert mp.looks_like_pytest(cmd), "the fixture must exercise the pytest branch"
    res = run_probe(repo, "src.py", PINNED, cmd)
    assert res.returncode == 2, res.stdout + res.stderr
    assert "PROBE PASSED" not in res.stdout
    assert "exited 2, not 1" in res.stderr
    assert (repo / "src.py").read_bytes() == before
    assert sidecars(repo) == []


def test_p2_kill_group_signals_the_known_pgid_and_never_re_reads_it(repo, monkeypatch):
    """codex round-4 P2: with `start_new_session=True` the pgid IS the pid, by construction.
    Re-reading it with `os.getpgid` at kill time can fail once the leader has exited, and
    the fallback cannot reach a surviving grandchild."""
    calls: list[tuple[int, int]] = []
    monkeypatch.setattr(mp.os, "killpg", lambda pgid, sig: calls.append((pgid, sig)))

    def exploding_getpgid(_pid):
        raise AssertionError("os.getpgid must not be consulted at kill time")

    monkeypatch.setattr(mp.os, "getpgid", exploding_getpgid)

    class FakePopen:
        pid = 4242

        def send_signal(self, _sig):
            raise AssertionError("the group signal succeeded; no fallback should run")

    mp._kill_group(FakePopen(), signal.SIGTERM)
    assert calls == [(4242, signal.SIGTERM)]


def test_p2_a_pipe_holding_grandchild_cannot_postpone_the_restore(repo):
    """The hazard end to end: a grandchild that `setsid`s out of the group inherits the
    stdout/stderr pipes, so no kill can reach it and EOF never arrives. Reading to EOF would
    block for the grandchild's whole lifetime (300s) WITH THE SOURCE MUTATED. The drain must
    give up and let the restore proceed."""
    before = (repo / "src.py").read_bytes()
    cmd = counting_script(repo, "orphan.sh", f"{PY} grandchild.py &\nexit 0")
    started = time.monotonic()
    try:
        res = run_probe(repo, "src.py", PINNED, cmd, timeout=3, wall_timeout=60)
    except subprocess.TimeoutExpired:
        pytest.fail(
            "the probe never returned — it waited on a grandchild's pipes while the "
            "source file stayed mutated"
        )
    finally:
        reap_grandchild(repo)
    elapsed = time.monotonic() - started
    assert res.returncode == 2, res.stdout + res.stderr
    assert "timed out" in res.stderr
    assert elapsed < 45, f"the probe waited {elapsed:.1f}s on a pipe-holding grandchild"
    assert (repo / "src.py").read_bytes() == before
    assert sidecars(repo) == []


def test_p2_no_wait_in_the_tool_is_unbounded():
    """Structural witness: every `communicate`/`wait` on the test child carries a timeout,
    and `os.getpgid` is never CALLED. Nothing may block while a mutation is on disk."""
    tree = ast.parse(PROBE.read_text(encoding="utf-8"))

    def bounded(call: ast.Call) -> bool:
        """A `timeout=` kwarg only counts if it is not the literal None — `timeout=None`
        is the API's own spelling of "wait forever" and would launder this witness
        (merge-gate lens 3, slip 3)."""
        for kw in call.keywords:
            if kw.arg == "timeout":
                return not (isinstance(kw.value, ast.Constant) and kw.value.value is None)
        return False

    unbounded = [
        call.func.attr
        for call in ast.walk(tree)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Attribute)
        and call.func.attr in {"communicate", "wait"}
        and not bounded(call)
    ]
    assert unbounded == [], f"unbounded wait(s) on the test child: {unbounded}"

    getpgid_calls = [
        call
        for call in ast.walk(tree)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Attribute)
        and call.func.attr == "getpgid"
    ]
    assert getpgid_calls == [], "the process group must be signalled by the pgid we know"


def test_slip1_the_published_sidecar_records_the_real_witnesses(repo):
    """merge-gate lens 3 slip 1: the tool's own sidecar AUTHORING was never round-tripped.

    Every reconcile test PLANTS its sidecar, so the consumer side was thoroughly witnessed
    while the producer side was not: making `publish_sidecar` record the ORIGINAL as the
    mutation witness, or a bogus index oid, passed the whole suite — and every real SIGKILL
    recovery would then refuse, silently killing the crash recovery that rounds 5-7 exist
    for. This captures the LIVE sidecar from inside step 3 and checks what it actually says.
    """
    cmd = counting_script(
        repo,
        "grab.sh",
        "command cp -f src.py.mutprobe.*.bak captured.bak\n" + pytest_cmd("test_real.py"),
    )
    res = run_probe(repo, "src.py", PINNED, cmd)
    assert res.returncode == 0, res.stdout + res.stderr

    captured = repo / "captured.bak"
    assert captured.is_file(), "no sidecar existed on disk during step 3"
    sidecar, err = mp.parse_sidecar(captured.read_bytes())
    assert err is None, err
    assert sidecar is not None
    # The payload is the pre-mutation source...
    assert sidecar.original == SRC.encode()
    # ...the applicability witness is the MUTATION, not the original (mutation M28)...
    assert sidecar.mutated_sha256 == hashlib.sha256(MUTATED_FIXTURE).hexdigest()
    assert sidecar.mutated_sha256 != hashlib.sha256(SRC.encode()).hexdigest()
    assert sidecar.mutated_len == len(MUTATED_FIXTURE)
    # ...and the identity witness is git's real index oid (mutation M29).
    assert sidecar.index_oid == git(repo, "ls-files", "-s", "--", "src.py").stdout.split()[1]


def test_slip2_the_atomic_publish_really_renames(tmp_path, monkeypatch):
    """merge-gate lens 3 slip 2: the AST witness alone is launderable — park the literal
    `os.replace` under an unreachable branch and write through `_write_private`, and all
    four structural facts still hold while nothing is atomic. This anchors the rename on
    the LIVE path behaviourally; keep BOTH."""
    calls: list[tuple[str, str]] = []

    def boom(src, dst):
        calls.append((str(src), str(dst)))
        raise OSError(13, "permission denied")

    monkeypatch.setattr(mp.os, "replace", boom)
    dest = tmp_path / "dest.txt"
    dest.write_bytes(b"old")
    staging = tmp_path / "dest.txt.mutprobe.1.new"

    err = mp._atomic_publish(staging, dest, b"new", None)
    assert err is not None and "cannot publish" in err, err
    assert calls == [(str(staging), str(dest))], "os.replace was never on the live path"
    assert dest.read_bytes() == b"old", "content changed without the rename succeeding"
    assert not staging.exists(), "the staging file must be cleaned up on failure"


def test_p1_sidecar_round_trips_through_its_integrity_header():
    mutated = b"# MUTATED\n"
    for payload in (b"", SRC.encode(), b"\x00\xff\nline\r\n"):
        parsed, err = mp.parse_sidecar(mp.sidecar_bytes(payload, mutated, OID))
        assert err is None
        assert parsed is not None
        assert parsed.original == payload  # binary + embedded newlines survive verbatim
        assert parsed.mutated_sha256 == hashlib.sha256(mutated).hexdigest()
        assert parsed.mutated_len == len(mutated)


@pytest.mark.parametrize(
    ("mangle", "needle"),
    [
        (lambda b: b[:-10], "truncated"),  # the P1 scenario: a short payload
        (lambda b: b + b"extra", "truncated or padded"),
        (lambda b: b.replace(b"\n", b"X"), "no header line"),  # no newline at all
        # Header's terminator eaten: magic and version still parse, the field count does
        # not — the reordered checks name that precisely instead of "not a sidecar".
        (lambda b: b.replace(b"\n", b"X", 1), "malformed header fields"),
        (lambda b: b"raw file with no header at all\n", "not a mutation-probe sidecar"),
        (lambda b: b.replace(b"v3", b"v9", 1), "unsupported sidecar version"),
    ],
)
def test_p1_damaged_sidecars_never_parse(mangle, needle):
    payload, err = mp.parse_sidecar(mangle(mp.sidecar_bytes(SRC.encode(), MUTATED_FIXTURE, OID)))
    assert payload is None
    assert err is not None and needle in err


def test_p1_sha256_mismatch_is_caught_even_at_the_right_length():
    """Length alone is not integrity: a same-length corruption must still be refused."""
    blob = bytearray(mp.sidecar_bytes(SRC.encode(), MUTATED_FIXTURE, OID))
    blob[-1] ^= 0xFF
    payload, err = mp.parse_sidecar(bytes(blob))
    assert payload is None
    assert err is not None and "sha256 mismatch" in err


def test_p1_truncated_dead_pid_sidecar_is_refused_never_replayed(repo):
    """codex round-3 P1, the reconcile-side defence: a corrupt sidecar must NEVER be written
    over live source. There is no way to recover the true original from a truncated payload,
    so the only sound behaviour is to refuse, retain, and tell the operator."""
    dead = subprocess.Popen([sys.executable, "-c", "pass"])
    dead.wait()
    src = repo / "src.py"
    sidecar = repo / f"src.py.mutprobe.{dead.pid}.bak"
    full = mp.sidecar_bytes(SRC.encode(), MUTATED_FIXTURE, OID)
    # Truncate into the PAYLOAD (a header-level cut is the separate 'no header' case).
    sidecar.write_bytes(full[:-10])  # a partial write, as a crash would leave
    live_edit = SRC + "\n# work done since the crash\n"
    src.write_text(live_edit, encoding="utf-8")

    res = run_probe(repo, "src.py", PINNED, pytest_cmd("test_real.py"))
    assert "RECONCILE REFUSED" in res.stdout
    assert "truncated" in res.stdout
    assert sidecar.exists(), "a sidecar that failed integrity must be RETAINED"
    assert src.read_text(encoding="utf-8") == live_edit, (
        "the corrupt sidecar was replayed over live source — the exact P1 defect"
    )
    # The probe then refuses on its own (the file the reconcile did not touch is dirty).
    assert res.returncode == 2


def test_p1_headerless_legacy_sidecar_is_refused_not_treated_as_raw(repo):
    """A sidecar from a pre-integrity build has no header. Falling back to 'treat the blob
    as the original' would reinstate the blind write, so it is refused too."""
    dead = subprocess.Popen([sys.executable, "-c", "pass"])
    dead.wait()
    sidecar = repo / f"src.py.mutprobe.{dead.pid}.bak"
    sidecar.write_bytes(SRC.encode())  # the OLD raw format
    res = run_probe(repo, "src.py", PINNED, pytest_cmd("test_real.py"))
    assert "RECONCILE REFUSED" in res.stdout
    assert sidecar.exists()


def test_p1_reconcile_restores_only_the_mutation_it_recorded(repo):
    """codex round-5 P1, the applicability witness — the SAFE case (a).

    Crash-shaped exactly as it would be found on disk: a dead-pid v2 sidecar whose recorded
    mutation is precisely what the target still holds. Undoing it is safe, so it is undone
    and the sidecar released."""
    dead = subprocess.Popen([sys.executable, "-c", "pass"])
    dead.wait()
    src = repo / "src.py"
    sidecar = repo / f"src.py.mutprobe.{dead.pid}.bak"
    plant_sidecar(sidecar, SRC.encode(), MUTATED_FIXTURE)
    src.write_bytes(MUTATED_FIXTURE)

    res = run_probe(repo, "src.py", PINNED, pytest_cmd("test_real.py"))
    assert "RECONCILED: restored" in res.stdout
    assert not sidecar.exists(), "a consumed sidecar must be released"
    assert src.read_text(encoding="utf-8") == SRC
    assert res.returncode == 0, res.stdout + res.stderr


@pytest.mark.parametrize(
    ("post_crash", "label"),
    [
        (SRC + "\n# work done after the crash\n", "operator edited the file"),
        ("COMPLETELY = 'different'\n", "operator replaced the file"),
        (SRC.replace("negative", "NEGATIVE"), "operator fixed it by hand"),
    ],
)
def test_p1_reconcile_refuses_when_the_target_moved_on_after_the_crash(repo, post_crash, label):
    """codex round-5 P1 — the UNSAFE case (b), which is why the witness exists.

    The sidecar records the ORIGINAL and the mutation. If the file no longer holds that
    mutation, the crash is over and something else has happened to it: restoring the
    original would DESTROY that work. Worse, this reconcile runs when probing ANY sibling
    file in the directory, so the blast radius reaches files the operator never probed.
    """
    dead = subprocess.Popen([sys.executable, "-c", "pass"])
    dead.wait()
    src = repo / "src.py"
    sidecar = repo / f"src.py.mutprobe.{dead.pid}.bak"
    plant_sidecar(sidecar, SRC.encode(), MUTATED_FIXTURE)
    src.write_text(post_crash, encoding="utf-8")

    # Probe a DIFFERENT file: the reconcile still sweeps the whole directory.
    res = run_probe(repo, "consts.py", "1", pytest_cmd("test_consts.py"))
    assert "RECONCILE REFUSED" in res.stdout, label
    assert "does not hold the mutation" in res.stdout
    assert src.read_text(encoding="utf-8") == post_crash, f"post-crash work destroyed: {label}"
    assert sidecar.exists(), "the sidecar must be RETAINED for the operator"
    # Both digests are named so the operator can tell what was expected from what is there.
    assert mp.parse_sidecar(sidecar.read_bytes())[0].mutated_sha256[:12] in res.stdout
    assert hashlib.sha256(post_crash.encode()).hexdigest()[:12] in res.stdout


def test_fix1_reconcile_refuses_when_the_branch_moved_under_it(repo):
    """codex round-7 fix 1: the byte digests can COINCIDE across branches.

    A killed probe leaves a sidecar. The operator then switches to a branch whose COMMITTED
    src.py happens to equal the recorded mutation exactly. Digest-only, the reconcile would
    call that "still mutated", replay the OLD branch's original, and dirty the NEW branch
    with a file nobody asked for. The index blob oid is what distinguishes them.
    """
    dead = subprocess.Popen([sys.executable, "-c", "pass"])
    dead.wait()
    src = repo / "src.py"
    main_oid = git(repo, "ls-files", "-s", "--", "src.py").stdout.split()[1]

    # A branch whose committed content coincides byte-for-byte with the recorded mutation.
    assert git(repo, "checkout", "-q", "-b", "other").returncode == 0
    src.write_bytes(MUTATED_FIXTURE)
    assert git(repo, "add", "src.py").returncode == 0
    assert git(repo, "commit", "-q", "-m", "coincidence").returncode == 0
    other_oid = git(repo, "ls-files", "-s", "--", "src.py").stdout.split()[1]
    assert other_oid != main_oid, "fixture precondition: the two branches differ in git"
    assert git(repo, "status", "--porcelain", "--", "src.py").stdout == ""

    sidecar = repo / f"src.py.mutprobe.{dead.pid}.bak"
    plant_sidecar(sidecar, SRC.encode(), MUTATED_FIXTURE, index_oid=main_oid)

    # Probe a DIFFERENT file — the reconcile sweeps the directory regardless.
    res = run_probe(repo, "consts.py", "1", pytest_cmd("test_consts.py"))
    assert "RECONCILE REFUSED" in res.stdout
    assert "no longer the file git was tracking" in res.stdout
    assert main_oid[:12] in res.stdout and other_oid[:12] in res.stdout
    assert src.read_bytes() == MUTATED_FIXTURE, "the new branch was dirtied — the fix1 defect"
    assert git(repo, "status", "--porcelain", "--", "src.py").stdout == ""
    assert sidecar.exists(), "a refused sidecar must be RETAINED"


def test_fix3_staging_and_sidecar_are_private_under_a_permissive_umask(repo):
    """codex round-7 fix 3: the sidecar is a COMPLETE copy of the source and it is the
    artifact that survives a crash. Created through a plain open(), umask 022 lands it 0644
    — silently widening access to a 0600 target's contents."""
    old_umask = os.umask(0o022)
    try:
        src = repo / "src.py"
        src.chmod(0o600)
        # The test command records the live sidecar's mode from inside step 3.
        cmd = counting_script(
            repo,
            "peek.sh",
            f'{PY} -c "import glob,os,stat,pathlib;'
            "pathlib.Path('modes').write_text(''.join("
            "f'{p}:{oct(stat.S_IMODE(os.stat(p).st_mode))}\\n' "
            "for p in sorted(glob.glob('*.mutprobe.*'))))\"\n" + pytest_cmd("test_real.py"),
        )
        res = run_probe(repo, "src.py", PINNED, cmd)
        assert res.returncode == 0, res.stdout + res.stderr
        observed = (repo / "modes").read_text().strip()
        assert observed, "no sidecar was visible during step 3"
        for line in observed.splitlines():
            assert line.endswith(":0o600"), f"world-readable probe artifact: {line}"
        assert stat.S_IMODE(src.stat().st_mode) == 0o600, "the target's own mode was widened"
    finally:
        os.umask(old_umask)


def test_fix3_private_write_ignores_the_umask_and_a_stale_mode(tmp_path):
    """The unit half: 0600 on creation, and 0600 even when a crash left the staging name
    behind with a wider mode (O_CREAT would not have re-applied it)."""
    old_umask = os.umask(0o022)
    try:
        fresh = tmp_path / "fresh.tmp"
        assert mp._write_private(fresh, b"x") is None
        assert stat.S_IMODE(fresh.stat().st_mode) == 0o600

        stale = tmp_path / "stale.tmp"
        stale.write_bytes(b"old")
        stale.chmod(0o644)
        assert mp._write_private(stale, b"y") is None
        assert stat.S_IMODE(stale.stat().st_mode) == 0o600
        assert stale.read_bytes() == b"y"
    finally:
        os.umask(old_umask)


def test_register2_the_metadata_bound_is_stated(repo):
    """codex round-7 item 2, REGISTERED not fixed: `os.replace` cannot preserve xattrs/ACLs/
    ownership, and git cannot see their loss. Probing for them would over-refuse on macOS's
    ubiquitous quarantine xattrs, so the bound is documented in both operator-facing
    surfaces instead."""
    source = PROBE.read_text(encoding="utf-8")
    docstring = source.split('"""')[1]
    for phrase in ("extended attributes", "ACL", "ownership", "quarantine"):
        assert phrase in docstring, f"the metadata bound omits {phrase!r}"
    helped = subprocess.run(
        [sys.executable, str(PROBE), "--help"], capture_output=True, text=True, timeout=60
    )
    assert helped.returncode == 0
    assert "extended attributes" in helped.stdout


def test_p1_v1_sidecar_is_refused_for_lacking_the_mutation_witness(repo):
    """codex round-5 P1, case (c): a v1 sidecar carries integrity but no applicability
    witness, so it cannot answer "does the target still hold that mutation?". Refused —
    never read as if it could."""
    dead = subprocess.Popen([sys.executable, "-c", "pass"])
    dead.wait()
    src = repo / "src.py"
    sidecar = repo / f"src.py.mutprobe.{dead.pid}.bak"
    original = SRC.encode()
    v1 = (
        f"{mp.SIDECAR_MAGIC} v1 sha256={hashlib.sha256(original).hexdigest()} "
        f"bytes={len(original)}\n"
    ).encode() + original
    sidecar.write_bytes(v1)
    src.write_bytes(MUTATED_FIXTURE)

    res = run_probe(repo, "src.py", PINNED, pytest_cmd("test_real.py"))
    assert "RECONCILE REFUSED" in res.stdout
    assert "unsupported sidecar version" in res.stdout
    assert sidecar.exists()
    assert src.read_bytes() == MUTATED_FIXTURE, "a refused sidecar must write nothing"


def test_p2_dead_pid_mutation_fragment_is_removed_and_never_restored(repo):
    """A `.new` fragment is an unpublished MUTATION: `os.replace` never ran, so the target
    still holds its original bytes and there is nothing to undo."""
    dead = subprocess.Popen([sys.executable, "-c", "pass"])
    dead.wait()
    frag = repo / f"src.py.mutprobe.{dead.pid}.new"
    frag.write_bytes(b"a half-written mutation")
    res = run_probe(repo, "src.py", PINNED, pytest_cmd("test_real.py"))
    assert "removed unpublished mutation fragment" in res.stdout
    assert "that write never landed" in res.stdout
    assert not frag.exists()
    assert res.returncode == 0, res.stdout + res.stderr
    assert (repo / "src.py").read_text(encoding="utf-8") == SRC


def test_p2_the_mutation_publish_preserves_the_file_mode(repo):
    """`os.replace` swaps in a NEW INODE, so the staging file's permissions become the
    target's. Losing an executable bit is not cosmetic — git tracks it, so the restore would
    then be reported broken. (Verified live before this was built.)"""
    script = repo / "script.sh"
    script.chmod(0o755)
    git(repo, "update-index", "--chmod=+x", "script.sh")
    git(repo, "commit", "-q", "-m", "exec bit")
    before = script.stat().st_mode
    res = run_probe(repo, "script.sh", "5", "bash test_script.sh")
    assert res.returncode == 0, res.stdout + res.stderr
    assert script.stat().st_mode == before, "the executable bit did not survive the probe"
    assert git(repo, "status", "--porcelain", "--", "script.sh").stdout == ""


def test_p1_dead_pid_tmp_fragment_is_removed_and_never_restored(repo):
    """A `.tmp` exists only BEFORE the atomic publish, and the mutation is written strictly
    after it — so a fragment proves the target was never mutated. Nothing to restore."""
    dead = subprocess.Popen([sys.executable, "-c", "pass"])
    dead.wait()
    frag = repo / f"src.py.mutprobe.{dead.pid}.tmp"
    frag.write_bytes(b"half a sidecar, no header")
    res = run_probe(repo, "src.py", PINNED, pytest_cmd("test_real.py"))
    assert "removed unpublished sidecar fragment" in res.stdout
    assert "that write never landed" in res.stdout
    assert not frag.exists()
    assert res.returncode == 0, res.stdout + res.stderr
    assert (repo / "src.py").read_text(encoding="utf-8") == SRC


def test_p1_live_pid_tmp_fragment_is_left_alone(repo):
    """A live pid's `.tmp` belongs to a probe mid-publish."""
    live = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
    try:
        frag = repo / f"consts.py.mutprobe.{live.pid}.tmp"
        frag.write_bytes(b"in flight")
        res = run_probe(repo, "src.py", PINNED, pytest_cmd("test_real.py"))
        assert res.returncode == 0, res.stdout + res.stderr
        # Match the MESSAGE, not the bare word — pytest's tmp_path carries the test's name.
        assert "removed unpublished sidecar fragment" not in res.stdout
        assert frag.read_bytes() == b"in flight"
    finally:
        live.kill()
        live.wait()


def test_p1_the_recognized_sidecar_name_is_only_ever_published_atomically():
    """Structural witness, mirroring the P2a ordering test: the `.bak` name must be reachable
    ONLY through `os.replace`, never through a direct write. A direct write truncates first,
    so a crash mid-write leaves a partial file under the name the reconcile trusts."""
    source = PROBE.read_text(encoding="utf-8")
    tree = ast.parse(source)

    replaces = [
        (fn, call)
        for fn in ast.walk(tree)
        if isinstance(fn, ast.FunctionDef)
        for call in ast.walk(fn)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Attribute)
        and call.func.attr == "replace"
        and getattr(call.func.value, "id", "") == "os"
    ]
    # One shared implementation of the atomic publish...
    assert len(replaces) == 1, "the atomic publish must have ONE implementation"
    assert replaces[0][0].name == "_atomic_publish"

    def callers_of(name: str) -> set[str]:
        return {
            fn.name
            for fn in ast.walk(tree)
            if isinstance(fn, ast.FunctionDef)
            for call in ast.walk(fn)
            if isinstance(call, ast.Call) and getattr(call.func, "id", "") == name
        }

    # ...reached by the sidecar publish directly, and by every write to a REAL target
    # through the one `write_target` gateway (codex round-6 P1b).
    assert callers_of("_atomic_publish") == {"publish_sidecar", "write_target"}
    assert callers_of("write_target") == {
        "publish_mutation",
        "restore",
        "reconcile_sidecars",
    }, callers_of("write_target")

    # The ONLY truncating write left in the tool is the documented read-only-directory
    # fallback, and it lives in exactly one named function.
    direct_writers = {
        fn.name
        for fn in ast.walk(tree)
        if isinstance(fn, ast.FunctionDef)
        for call in ast.walk(fn)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Attribute)
        and call.func.attr == "write_bytes"
    }
    assert direct_writers == {"_direct_write"}, (
        f"a truncating write_bytes escaped the atomic path in {direct_writers} — only the "
        "named read-only-directory fallback may write that way"
    )

    # No `<name>.write_bytes(...)` may target a variable that holds the .bak path.
    bak_holders = {"sidecar", "sc", "bak"}
    offenders = [
        call.func.value.id
        for call in ast.walk(tree)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Attribute)
        and call.func.attr == "write_bytes"
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id in bak_holders
    ]
    assert offenders == [], (
        f"the recognized sidecar name is written directly via {offenders} — a crash "
        "mid-write would leave a partial file that the reconcile trusts"
    )


def test_p2a_release_treats_an_already_gone_sidecar_as_released():
    """`released is released` — a vanished sidecar is the desired end state, not an error."""
    assert mp._release(Path("/nonexistent/dir/gone.mutprobe.1.bak")) is None


# --- input gates + no-collateral-damage ---------------------------------------------------


def test_p2a_the_mutation_is_published_atomically_inside_the_restoring_try():
    """codex round-1 P2a + round-5 P2, asserted STRUCTURALLY over the AST.

    Two properties, both closed BY CONSTRUCTION, so neither has observable behaviour left
    to test — the structure itself is the witness, and reverting either kills this:

      * ORDERING (round-1 P2a): the mutation is published INSIDE the `try` whose `finally`
        restores. Publishing first and entering the guard after left a window where a
        signal unwound past every restoration branch.
      * ATOMICITY (round-5 P2): the target is never written with `write_bytes` in `probe()`
        at all. `write_bytes` truncates then writes, so a signal in THAT window left bytes
        that were neither the original nor the mutation — which the restore's own
        bytes-verify then (correctly) refused to touch, stranding a damaged file.

    The RESTORE's `write_bytes` in `restore()` is deliberately untouched: it writes
    known-good original bytes, a torn restore is exactly what the sidecar + reconcile
    recover, and it needs no directory write permission.
    """
    tree = ast.parse(PROBE.read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "probe")
    guards = [
        node
        for node in ast.walk(fn)
        if isinstance(node, ast.Try)
        and any(
            isinstance(c, ast.Call) and getattr(c.func, "id", "") == "restore"
            for stmt in node.finalbody
            for c in ast.walk(stmt)
        )
    ]
    assert len(guards) == 1, "probe() must have exactly one restoring try/finally"
    protected = {id(c) for stmt in guards[0].body for c in ast.walk(stmt)}

    direct = [
        c
        for c in ast.walk(fn)
        if isinstance(c, ast.Call)
        and isinstance(c.func, ast.Attribute)
        and c.func.attr == "write_bytes"
        and getattr(c.func.value, "id", "") == "target"
    ]
    assert direct == [], (
        "probe() writes the target directly — the mutation must go through the atomic "
        "publish, or a signal mid-write strands a torn file"
    )

    publishes = [
        c
        for c in ast.walk(fn)
        if isinstance(c, ast.Call) and getattr(c.func, "id", "") == "publish_mutation"
    ]
    assert len(publishes) == 1, "probe() must publish the mutation exactly once"
    assert id(publishes[0]) in protected, (
        "the mutation publish sits OUTSIDE the restoring try/finally — a signal in that "
        "window leaves the file mutated"
    )


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
