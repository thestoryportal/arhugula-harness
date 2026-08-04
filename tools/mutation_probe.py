#!/usr/bin/env python3
"""Mutation probe — mechanize the revert-and-verify discipline (U-WT-06).

`[[mutation-probe-load-bearing-witness]]`: a green test proves nothing on its own. The only
witness that a test PINS a line is to remove that line, watch the test go red, and put the
line back. This tool automates exactly that loop, and nothing else:

    uv run python tools/mutation_probe.py --file F --lines A-B --test "<cmd>"

THIS TOOL WRITES SOURCE FILES BY DESIGN. That is the whole point, and the safety envelope
below is therefore the load-bearing part of the design — not the mutation:

  0. REFUSE if `git status --porcelain -- F` is non-empty. A dirty file has uncommitted
     work the restore step could not distinguish from the probe's own edit, and git could
     not witness a correct restore. Never mutate a dirty file.
  1. Run `<cmd>` and require rc 0. Probing against an already-red test is meaningless: the
     step-3 red would be the pre-existing red, so a vacuous test would be reported as a
     kill. Already-red exits 2 with its own message, never a probe verdict.
  2. Read the original bytes into memory, then comment lines A-B out (`# ` at column 0).
  2b. REQUIRE the mutated text to remain SYNTACTICALLY VALID (`ast.parse` for .py, `bash -n`
     for .sh, `yaml.safe_load_all` for .yaml/.yml). A syntax-invalid mutation makes even a
     VACUOUS test fail at import/collection time, which would fake a kill. Such a range is
     rejected (exit 2) BEFORE anything is written, so the file is never touched.
  3. Re-run `<cmd>` and require a FAIL that is identifiable as TEST-LEVEL — see
     `classify_step3`. Any other nonzero (collection error, missing binary, timeout, a
     signal-killed child) is INDETERMINATE and exits 2. A probe must never report PASS on
     a red it cannot attribute to a test.
  4. Restore in a `finally`, in this order: (a) verify the on-disk bytes are still EXACTLY
     what the probe wrote — if a concurrent writer touched F mid-probe, REFUSE to restore
     and fail loudly (exit 3), because a blind restore would silently clobber that edit and
     `git diff --quiet` would still pass afterwards; (b) write the in-memory original;
     (c) verify BOTH the on-disk bytes and `git diff --quiet -- F`, and hard-error loudly
     if either disagrees. There is NO `git stash` and NO `git checkout --` anywhere in this
     file — the only restore authority is the in-memory copy plus its on-disk sidecar.
  5. Exit 0 probe-pass / 1 `PROBE FAILED: test stayed green with F:A-B removed` /
     2 refused-or-indeterminate (file untouched or already restored) / 3 restore failure.

Crash safety (the sidecar). `F.mutprobe.<pid>.bak` is written BEFORE the mutation and
REMOVED atomically once a restore is verified. Retaining it on the success path would be a
defect, not belt-and-braces: a later dead-pid reconcile would restore it over whatever
valid edits the file had accumulated since. At startup the probe reconciles sidecars in the
target's directory whose embedded pid is DEAD (`kill(pid, 0)` raises `ProcessLookupError`);
a LIVE pid is another probe mid-run and is never touched — an unconditional reconcile would
restore a concurrent probe's file out from under it.

Termination guarantees, honestly bounded:
  * the test CHILD dying (any signal) → the runner's `finally` restores immediately;
  * the RUNNER receiving SIGTERM/SIGINT/SIGHUP → the installed handler RAISES, so the
    `finally` unwinds and restores (the test child is killed by process group first);
  * the RUNNER receiving SIGKILL → no in-process recovery is possible, by definition. The
    file stays mutated until the NEXT invocation's dead-pid reconcile restores it and says
    so. This exclusion is explicit; it is not an oversight.

Residual limits, stated rather than hidden:
  * reconcile scans the TARGET's directory only (bounded and predictable — no walk of
    `.venv`/`.git`). A sidecar left elsewhere by a SIGKILL'd probe of a different file is
    recovered the next time a probe runs against THAT directory.
  * pid reuse: if a dead probe's pid has been recycled by an unrelated process, reconcile
    conservatively SKIPS (leaving the sidecar) rather than risk racing a live probe.
  * for a non-pytest `--test`, "test-level failure" is a heuristic (see `classify_step3`).

Plan: `.harness/r-if-116-insights-residue-plan.md` Feature 5 / U-WT-06.
"""

from __future__ import annotations

import argparse
import ast
import os
import re
import signal
import subprocess
import sys
import tempfile
from pathlib import Path
from types import FrameType
from typing import NamedTuple

import yaml

# Extension → (mutation-comment prefix, syntax-check kind). Anything else is REFUSED: a
# comment prefix guessed wrong would corrupt the file, and a language whose syntax this
# tool cannot check would defeat gate 2b.
COMMENT_PREFIX = "# "
KINDS: dict[str, str] = {".py": "py", ".sh": "sh", ".yaml": "yaml", ".yml": "yaml"}

SIDECAR_RE = re.compile(r"^(?P<base>.+)\.mutprobe\.(?P<pid>\d+)\.bak$")
# pytest's summary counts. `\s+failed\b` deliberately does NOT match "1 xfailed" (no word
# boundary before "failed" there) — an xfail is not a failure.
PYTEST_FAILED_RE = re.compile(r"(\d+)\s+failed\b")
PYTEST_ERROR_RE = re.compile(r"(\d+)\s+errors?\b")
PYTEST_CMD_RE = re.compile(r"(?:^|[\s/])pytest\b")

KILLED = "KILLED"
SURVIVED = "SURVIVED"
INDETERMINATE = "INDETERMINATE"

# rc conventions for `run_shell`. 124 is OUR timeout marker (never the child's); 126/127 are
# the shell's not-executable / not-found codes; >= 128 is a shell reporting 128+signal, and
# < 0 is Python reporting a directly-signalled child.
TIMEOUT_RC = 124
# pytest's `ExitCode.TESTS_FAILED`. The ONLY pytest rc that means "tests ran and some
# failed"; 2/3/4/5 are interrupt / internal error / usage error / empty collection, and any
# of them can still print a stale `N failed` summary.
PYTEST_TESTS_FAILED_RC = 1


class TerminatedError(RuntimeError):
    """Raised from the signal handler so `finally` blocks unwind and restore the file."""


class Ran(NamedTuple):
    rc: int
    out: str
    err: str

    @property
    def combined(self) -> str:
        return f"{self.out}\n{self.err}"


# --- external-call layer (the only impure part) -----------------------------------------


def run(cmd: list[str], cwd: Path, timeout: int = 30) -> Ran:
    """Run `cmd` (no shell), return (rc, stdout, stderr) stripped. Never raises for tool
    absence/timeout — those surface as rc 127 / 124 so every call site can tell "tool
    absent" from "tool said no". A `TerminatedError` raised by the signal handler DOES propagate:
    that is how the caller's `finally` gets to run.
    """
    try:
        p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
        return Ran(p.returncode, p.stdout.strip(), p.stderr.strip())
    except FileNotFoundError:
        return Ran(127, "", "")
    except subprocess.TimeoutExpired:
        return Ran(TIMEOUT_RC, "", "")
    except OSError:
        return Ran(126, "", "")


def _kill_group(p: subprocess.Popen[str]) -> None:
    """SIGKILL the child's whole process group. `--test` is a SHELL command, so the thing
    that must die is the group (a `bash -c 'pytest ...'` may have grandchildren); killing
    only the shell would leave the real test running against a file we are about to
    restore."""
    try:
        os.killpg(os.getpgid(p.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        try:
            p.kill()
        except OSError:
            pass


def run_shell(cmd: str, cwd: Path, timeout: int) -> Ran:
    """Run the operator's `--test` string through a shell, in its own process group.

    `start_new_session=True` is what makes `_kill_group` correct AND keeps a terminal
    SIGINT from reaching the test independently of the runner. On timeout, and on ANY
    exception (notably `TerminatedError` from the SIGTERM handler), the whole group is killed
    before the exception is re-raised — the restore must never race a live test process.
    """
    try:
        # A shell command string IS this tool's interface (`--test "<cmd>"`).
        p = subprocess.Popen(
            cmd,
            shell=True,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
    except OSError as e:
        return Ran(126, "", f"could not start the test command: {e}")
    try:
        out, err = p.communicate(timeout=timeout)
        return Ran(p.returncode, out or "", err or "")
    except subprocess.TimeoutExpired:
        _kill_group(p)
        out, err = p.communicate()
        return Ran(TIMEOUT_RC, out or "", err or "")
    except BaseException:
        _kill_group(p)
        p.wait()
        raise


def pid_alive(pid: int) -> bool:
    """Is `pid` a live process? `PermissionError` means it exists under another uid, which
    for our purposes is ALIVE — the conservative answer, since the cost of a false "dead"
    is clobbering a concurrent probe's file."""
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return True
    return True


# --- pure helpers -----------------------------------------------------------------------


def parse_line_range(spec: str) -> tuple[int, int]:
    """`"12-20"` or `"12"` → (12, 20) / (12, 12), 1-indexed inclusive. Raises ValueError."""
    text = spec.strip()
    m = re.fullmatch(r"(\d+)(?:\s*-\s*(\d+))?", text)
    if not m:
        return _bad_range(spec)
    a = int(m.group(1))
    b = int(m.group(2)) if m.group(2) else a
    if a < 1 or b < a:
        return _bad_range(spec)
    return a, b


def _bad_range(spec: str) -> tuple[int, int]:
    raise ValueError(f"--lines must be A or A-B with 1 <= A <= B (got {spec!r})")


def comment_out(text: str, start: int, end: int, prefix: str = COMMENT_PREFIX) -> str:
    """Prefix lines `start..end` (1-indexed, inclusive) with `prefix`, preserving line
    endings and every other byte. Raises ValueError if the range is not inside the file.

    The prefix goes at COLUMN 0, not at the line's own indentation. That is deliberate: in
    Python it makes a range that was the sole body of a block collapse into an
    `IndentationError`, which gate 2b then rejects as an unprobeable range — exactly the
    honest outcome, instead of a fake kill.
    """
    lines = text.splitlines(keepends=True)
    if start < 1 or end > len(lines):
        raise ValueError(f"--lines {start}-{end} is outside {len(lines)}-line file")
    for i in range(start - 1, end):
        line = lines[i]
        body = line.rstrip("\r\n")
        ending = line[len(body) :]
        lines[i] = f"{prefix}{body}{ending}"
    return "".join(lines)


def looks_like_pytest(cmd: str) -> bool:
    """Does `--test` invoke pytest? Drives the strict step-3 classifier below."""
    return bool(PYTEST_CMD_RE.search(cmd))


def _last_count(rx: re.Pattern[str], text: str) -> int:
    """The LAST count matched by `rx` (pytest prints its authoritative counts in the final
    summary line), or 0."""
    found = rx.findall(text)
    return int(found[-1]) if found else 0


def classify_step3(rc: int, output: str, is_pytest: bool) -> tuple[str, str]:
    """Was the post-mutation red an identifiable TEST-LEVEL failure? Pure.

    Returns (KILLED | SURVIVED | INDETERMINATE, human reason). The asymmetry is the point:
    KILLED is the only verdict that can produce a probe PASS, so every doubt resolves to
    INDETERMINATE (exit 2), never to a probe-pass.

    * rc 0 → SURVIVED (the test stayed green with the lines gone).
    * abnormal termination → INDETERMINATE: rc < 0 (Python reporting a signalled child),
      rc >= 128 (a shell reporting 128+signal), our TIMEOUT_RC, or the shell's 126/127.
      Heuristic limit, stated: a runner that deliberately exits >= 128 to mean "tests
      failed" would be misread as abnormal — none is used here, and the failure direction
      is the safe one (exit 2, not a false pass).
    * pytest → require rc EXACTLY 1 (`ExitCode.TESTS_FAILED`) AND a reported `N failed`
      count AND no `N error` count. All three are load-bearing. rc 2/3/4 (interrupt /
      internal error / usage error) can still PRINT an `N failed` summary accumulated
      before the abort, so a count-only check would read an aborted run as a kill (codex
      round-1 P1); rc 5 is an empty collection. Errors mean collection/import breakage
      rather than a test-level failure; because step 1 required the suite green, any error
      here was CAUSED by the mutation and is not a witness that a test pins the lines.
    * any other command → nonzero is taken as a kill. This is honestly a weaker claim: an
      arbitrary script's nonzero rc cannot be attributed to an assertion. What IS excluded
      is launch failure, timeout and signal death (above) plus, by gate 2b, the dominant
      false-kill source (a syntax-invalid mutation). Prefer a pytest `--test` when the
      distinction matters.
    """
    if rc == 0:
        return SURVIVED, "the test command exited 0 with the lines removed"
    if rc < 0:
        return INDETERMINATE, f"the test command was killed by signal {-rc}"
    if rc == TIMEOUT_RC:
        return INDETERMINATE, "the test command timed out (--timeout)"
    if rc in (126, 127):
        return INDETERMINATE, f"the test command could not be executed (rc {rc})"
    if rc >= 128:
        return INDETERMINATE, f"the test command terminated abnormally (rc {rc} = 128+signal)"
    if is_pytest:
        failed = _last_count(PYTEST_FAILED_RE, output)
        errors = _last_count(PYTEST_ERROR_RE, output)
        if rc != PYTEST_TESTS_FAILED_RC:
            seen = f", though it printed '{failed} failed' before aborting" if failed else ""
            return (
                INDETERMINATE,
                f"pytest exited {rc}, not {PYTEST_TESTS_FAILED_RC} — an interrupt (2), "
                f"internal error (3), usage error (4) or empty collection (5) is not a "
                f"test-level failure{seen}",
            )
        if errors:
            return (
                INDETERMINATE,
                f"pytest reported {errors} error(s) — collection/import breakage caused by the "
                "mutation, not a test-level failure",
            )
        if failed:
            return KILLED, f"pytest reported {failed} failed test(s)"
        return (
            INDETERMINATE,
            f"pytest exited {rc} without reporting any failed test (usage error, internal "
            "error, or no tests ran)",
        )
    return KILLED, f"the test command exited {rc} (non-pytest heuristic — see --help)"


def sidecar_for(target: Path, pid: int) -> Path:
    return target.with_name(f"{target.name}.mutprobe.{pid}.bak")


def kind_for(target: Path) -> str | None:
    return KINDS.get(target.suffix)


# --- syntax gate (2b) --------------------------------------------------------------------


def syntax_error(kind: str, text: str, name: str) -> str | None:
    """The syntax error the MUTATED text would introduce, or None. `.sh` shells out to
    `bash -n`; the others are checked in-process. Checked BEFORE anything is written, so a
    rejected range leaves the file untouched."""
    if kind == "py":
        try:
            ast.parse(text, filename=name)
        except SyntaxError as e:
            return f"{type(e).__name__}: {e}"
        return None
    if kind == "yaml":
        try:
            list(yaml.safe_load_all(text))
        except yaml.YAMLError as e:
            return f"YAMLError: {e}"
        return None
    if kind == "sh":
        with tempfile.TemporaryDirectory() as td:
            probe = Path(td) / "mutated.sh"
            probe.write_text(text, encoding="utf-8")
            res = run(["bash", "-n", str(probe)], Path(td))
        if res.rc == 127:
            return "bash is not available to syntax-check the mutated .sh"
        if res.rc != 0:
            return f"bash -n: {res.err or res.out or f'rc {res.rc}'}"
        return None
    return f"no syntax checker for kind {kind!r}"


# --- sidecar reconcile -------------------------------------------------------------------


def reconcile_sidecars(directory: Path, self_pid: int) -> list[str]:
    """Restore originals left behind by SIGKILL'd probes. Returns human messages.

    ONLY sidecars whose embedded pid is dead are acted on: a live pid belongs to a probe
    that is mid-run and whose file must not be rewritten under it. A sidecar whose file
    already matches it is merely stale (the probe restored, then died before unlinking) —
    it is removed without rewriting anything.
    """
    msgs: list[str] = []
    try:
        candidates = sorted(directory.glob("*.mutprobe.*.bak"))
    except OSError:
        return msgs
    for sc in candidates:
        m = SIDECAR_RE.match(sc.name)
        if not m:
            continue
        pid = int(m.group("pid"))
        if pid == self_pid or pid_alive(pid):
            continue
        original = directory / m.group("base")
        try:
            saved = sc.read_bytes()
        except OSError as e:
            msgs.append(f"RECONCILE SKIPPED: cannot read sidecar {sc.name} ({e})")
            continue
        current: bytes | None
        try:
            current = original.read_bytes()
        except OSError:
            current = None
        if current == saved:
            try:
                sc.unlink()
                msgs.append(
                    f"RECONCILED: removed stale sidecar {sc.name} (pid {pid} dead, "
                    f"{original.name} already matches it)"
                )
            except OSError as e:
                msgs.append(f"RECONCILE SKIPPED: cannot remove stale sidecar {sc.name} ({e})")
            continue
        try:
            original.write_bytes(saved)
            sc.unlink()
        except OSError as e:
            msgs.append(f"RECONCILE FAILED: could not restore {original} from {sc.name} ({e})")
            continue
        msgs.append(
            f"RECONCILED: restored {original} from {sc.name} — a probe (pid {pid}) died "
            "without restoring (SIGKILL / power loss). Verify the file before trusting it."
        )
    return msgs


# --- restore -----------------------------------------------------------------------------


class RestoreOutcome(NamedTuple):
    ok: bool
    message: str


def restore(
    target: Path, original: bytes, written: bytes, sidecar: Path, cwd: Path
) -> RestoreOutcome:
    """Put `original` back — but only after proving nobody else edited the file.

    Order is load-bearing (merge-gate lens-1 on the plan): the on-disk bytes must still be
    EXACTLY `written` (what the probe put there). If they are not, a concurrent writer
    touched F mid-probe, and restoring would silently clobber that edit while leaving
    `git diff --quiet` green — an invisible data loss. Refuse instead, keep the sidecar,
    and say so loudly.

    On success the restore is verified twice — the on-disk bytes AND `git diff --quiet`
    (the same predicate step 0 gated on) — and only then is the sidecar unlinked, so no
    success-path sidecar survives for a later reconcile to replay. BOTH success paths take
    that verification, including the one where no bytes needed writing (codex round-1 P2b):
    matching content is not the same claim as a clean working tree — another process can
    put the original bytes back while leaving the index or the file's git state dirty, and
    releasing the sidecar there would drop the only remaining copy while the caller printed
    a verification it never ran.
    """
    try:
        current = target.read_bytes()
    except OSError as e:
        return RestoreOutcome(
            False,
            f"RESTORE FAILED: cannot read {target} ({e}); the original is preserved at {sidecar}",
        )
    if current == original:
        # Already the original (a concurrent writer restored it, or the mutation never
        # landed). Nothing to WRITE — but the git verification below still applies.
        return _verify_and_release(target, sidecar, cwd)
    if current != written:
        return RestoreOutcome(
            False,
            f"RESTORE REFUSED: {target} changed on disk during the probe — it is neither what "
            "this probe wrote nor the original, so a concurrent writer edited it. Refusing to "
            f"overwrite that edit. The original is preserved at {sidecar}; reconcile by hand.",
        )
    try:
        target.write_bytes(original)
    except OSError as e:
        return RestoreOutcome(
            False,
            f"RESTORE FAILED: could not write {target} ({e}); the original is preserved at "
            f"{sidecar}",
        )
    try:
        after = target.read_bytes()
    except OSError as e:
        return RestoreOutcome(
            False,
            f"RESTORE FAILED: could not re-read {target} ({e}); the original is preserved at "
            f"{sidecar}",
        )
    if after != original:
        return RestoreOutcome(
            False,
            f"RESTORE FAILED: {target} does not match the original after rewriting it; the "
            f"original is preserved at {sidecar}",
        )
    return _verify_and_release(target, sidecar, cwd)


def _verify_and_release(target: Path, sidecar: Path, cwd: Path) -> RestoreOutcome:
    """The shared restore tail: git must agree the file is back, and only then is the
    sidecar released. Reached from BOTH success paths — the one that rewrote the bytes and
    the one that found them already correct."""
    diff = run(["git", "diff", "--quiet", "--", str(target)], cwd)
    if diff.rc != 0:
        return RestoreOutcome(
            False,
            f"RESTORE FAILED: `git diff --quiet -- {target}` exited {diff.rc} after restoring — "
            f"the working tree still differs. The original is preserved at {sidecar}.",
        )
    _unlink(sidecar)
    return RestoreOutcome(True, "")


def _unlink(path: Path) -> None:
    try:
        path.unlink()
    except OSError:
        pass


# --- the probe ---------------------------------------------------------------------------


def _install_signal_handlers() -> None:
    """Turn a termination signal into an EXCEPTION so `finally` restores the file. SIGKILL
    cannot be caught — that gap is covered by the sidecar, not by this."""

    def handler(signum: int, _frame: FrameType | None) -> None:
        raise TerminatedError(f"received signal {signum}")

    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(sig, handler)


def _refuse(msg: str) -> int:
    print(f"REFUSED: {msg}", file=sys.stderr)
    return 2


def probe(target: Path, start: int, end: int, test_cmd: str, timeout: int) -> int:
    """The five steps. Returns the process exit code; see the module docstring."""
    # Step 0 — the repo, then the clean-file gate.
    top = run(["git", "rev-parse", "--show-toplevel"], target.parent)
    if top.rc != 0 or not top.out:
        return _refuse(
            f"{target} is not inside a git repository — the restore could not be witnessed by git."
        )
    repo_root = Path(top.out)

    for msg in reconcile_sidecars(target.parent, os.getpid()):
        print(msg)

    status = run(["git", "status", "--porcelain", "--", str(target)], repo_root)
    if status.rc != 0:
        return _refuse(
            f"`git status --porcelain -- {target}` exited {status.rc} — cannot "
            "establish that the file is clean."
        )
    if status.out:
        return _refuse(
            f"{target} is dirty ({status.out.splitlines()[0].strip()}) — refusing to mutate a "
            "file with uncommitted changes. The file was NOT touched. Commit or stash your "
            "own work first (this tool never runs git stash / git checkout on your behalf)."
        )

    kind = kind_for(target)
    if kind is None:
        return _refuse(
            f"{target.suffix or '(no extension)'} is not a probeable extension "
            f"({', '.join(sorted(KINDS))}) — the comment prefix and the syntax gate are "
            "language-specific."
        )

    try:
        original = target.read_bytes()
        text = original.decode("utf-8")
    except OSError as e:
        return _refuse(f"cannot read {target} ({e}).")
    except UnicodeDecodeError:
        return _refuse(f"{target} is not UTF-8 text — refusing to mutate it.")

    try:
        mutated_text = comment_out(text, start, end)
    except ValueError as e:
        return _refuse(str(e))

    # Step 1 — the baseline MUST be green.
    print(f"[1/3] baseline: {test_cmd}")
    base = run_shell(test_cmd, repo_root, timeout)
    if base.rc != 0:
        sys.stderr.write(base.combined)
        return _refuse(
            f"the test command is ALREADY RED before any mutation (rc {base.rc}). A probe "
            "against a red test proves nothing — its step-3 failure would be the pre-existing "
            f"one. Fix the test first. {target} was NOT touched."
        )

    # Step 2b — reject an unprobeable range BEFORE writing anything.
    err = syntax_error(kind, mutated_text, str(target))
    if err is not None:
        return _refuse(
            f"REJECTED RANGE: removing {target.name}:{start}-{end} leaves the file "
            f"syntactically invalid ({err}). Such a mutation makes even a VACUOUS test fail at "
            "import/collection time, which would fake a kill — so no verdict is possible for "
            f"this range. {target} was NOT touched; pick a range whose removal still parses."
        )

    # Step 2 — sidecar first, then the mutation.
    #
    # ORDERING (codex round-1 P2a). The mutating write happens INSIDE the `try` whose
    # `finally` restores, not before it. Publishing the mutation first and only then
    # entering the protected region leaves a window in which a SIGTERM/SIGINT/SIGHUP —
    # which the handler turns into an exception — unwinds past every restoration branch and
    # leaves the file mutated until the NEXT invocation's sidecar reconcile, breaking AC4b's
    # immediate guarantee. With the write inside, the window is closed BY CONSTRUCTION:
    # there is no point at which the target's bytes differ from `original` and an exception
    # can escape without running `restore`. (`test_p2a_the_mutating_write_is_inside_the_
    # restoring_try` asserts this structurally over the AST, since a closed window has no
    # observable behaviour left to test.)
    #
    # The remaining pre-`try` window writes only the SIDECAR, while the target still holds
    # its original bytes: a signal there leaves a stale sidecar that matches its file, which
    # the next reconcile removes without rewriting anything.
    sidecar = sidecar_for(target, os.getpid())
    written = mutated_text.encode("utf-8")
    try:
        sidecar.write_bytes(original)
    except OSError as e:
        return _refuse(f"cannot write the crash-recovery sidecar {sidecar} ({e}).")

    verdict = INDETERMINATE
    reason = "the probe did not complete"
    mutation_output = ""
    write_error: str | None = None
    signal_error: str | None = None
    outcome = RestoreOutcome(False, "RESTORE FAILED: the restore step did not run")
    try:
        try:
            target.write_bytes(written)
        except OSError as e:
            write_error = f"cannot write {target} ({e})"
        else:
            print(f"[2/3] mutated {target}:{start}-{end} ({end - start + 1} line(s) commented out)")
            print(f"[3/3] re-running: {test_cmd}")
            res = run_shell(test_cmd, repo_root, timeout)
            mutation_output = res.combined
            verdict, reason = classify_step3(res.rc, mutation_output, looks_like_pytest(test_cmd))
    except TerminatedError as e:
        signal_error = str(e)
    finally:
        # Unconditional: also runs when a BaseException this function does not name is on
        # its way out, which is the only way that path's restore ever happens.
        outcome = restore(target, original, written, sidecar, repo_root)
        if not outcome.ok:
            print(outcome.message, file=sys.stderr)

    if not outcome.ok:
        # A restore failure outranks the verdict: exit 2 promises "the file is untouched",
        # and that promise is exactly what no longer holds.
        if verdict != INDETERMINATE:
            print(f"(the probe's own verdict was {verdict}: {reason})", file=sys.stderr)
        return 3

    if write_error is not None:
        return _refuse(f"{write_error}; the file was left unchanged.")
    if signal_error is not None:
        print(
            f"REFUSED: {signal_error} — {target} was restored and verified; no verdict.",
            file=sys.stderr,
        )
        return 2

    print(f"restored {target} (verified byte-identical + `git diff --quiet`)")
    if verdict == KILLED:
        print(f"PROBE PASSED: {target}:{start}-{end} is pinned — {reason}.")
        return 0
    if verdict == SURVIVED:
        print(f"PROBE FAILED: test stayed green with {target}:{start}-{end} removed")
        print(f"  the test command does NOT pin those lines ({reason}).")
        return 1
    sys.stderr.write(mutation_output)
    print(
        f"REFUSED: INDETERMINATE — {reason}. That is not an identifiable test-level "
        f"failure, so no verdict is claimed for {target}:{start}-{end}. The file was restored.",
        file=sys.stderr,
    )
    return 2


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Prove a test pins named source lines by removing them (U-WT-06).",
        epilog=(
            "Exit codes: 0 probe-pass (the test went red) / 1 PROBE FAILED (the test stayed "
            "green) / 2 refused or indeterminate (file untouched or verifiably restored) / "
            "3 restore failure (the file may still be mutated — read the message). "
            "A non-pytest --test yields a weaker kill claim; see the module docstring."
        ),
    )
    ap.add_argument("--file", required=True, help="source file to mutate (.py/.sh/.yaml/.yml)")
    ap.add_argument("--lines", required=True, help="1-indexed inclusive range, 'A-B' or 'A'")
    ap.add_argument("--test", required=True, help="shell command that must pass, then fail")
    ap.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="per-run timeout in seconds for --test (default 600); a timeout is INDETERMINATE",
    )
    args = ap.parse_args(argv)

    target = Path(args.file).expanduser()
    if not target.is_file():
        print(f"REFUSED: {target} is not an existing file.", file=sys.stderr)
        return 2
    target = target.resolve()
    try:
        start, end = parse_line_range(args.lines)
    except ValueError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2
    if not args.test.strip():
        print("REFUSED: --test must be a non-empty command.", file=sys.stderr)
        return 2

    _install_signal_handlers()
    return probe(target, start, end, args.test, args.timeout)


if __name__ == "__main__":
    sys.exit(main())
