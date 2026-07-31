"""`harness-shutdown` admin CLI — signal-running-instance (U-RT-48; C-RT-13).

Per `Spec_Harness_Runtime_v1.md` v1.1 §13:

> `harness-shutdown` (signal-running-instance).
> - Reads pidfile (location resolved via PATH_CLASS_REGISTRY; suggest
>   `.harness/runtime.pid`).
> - Sends `SIGTERM` to the pid.
> - Optionally waits for process exit with `--wait <seconds>` (default:
>   no wait).
> - Exits 0 on signal delivery success; nonzero on pidfile-missing or
>   signal-delivery error.
> - The receiving harness instance's signal handler is responsible for
>   the actual drain → shutdown sequence (per C-RT-10 + C-RT-11).

**Read-only invariant** (C-RT-13 invariant #2): `harness-shutdown` MUST
NOT touch state ledger / collector sqlite / configuration files. It
only reads the pidfile and emits a signal. Tested via sentinel
monkeypatch on `Path.open` + `os.open`.

**`--wait` semantics** (self-description refreshed at the `B-97`(a)
spec leg, per Runtime spec v1.108's stale-as-described fold-in (vi) —
docstring/help/message text only, ZERO logic change): `--wait` polls
the target process for exit via `os.kill(pid, 0)`.

**Whether SIGTERM leads to exit depends on the RECEIVING process's
own loop, and this tool cannot tell which shape it signalled.** The
signal handler installed at stage 7 only sets `ctx.drained_flag`
(U-RT-44); it never calls `shutdown()` itself. What happens next is
the receiver's business:

- A `harness daemon` process **does exit — but NOT via `drained_flag`,
  and the distinction matters for diagnosis.** While serving,
  `uvicorn.Server.serve()` runs inside `capture_signals()`, which
  **replaces** the stage-7 SIGTERM handler for the duration; SIGTERM
  therefore sets *uvicorn's* `should_exit`, the serve task returns, and
  `cli/app.py::_daemon_main` calls `_shutdown(ctx)` in its `finally`.
  The `drained_flag` race in `_daemon_main` is real code and is what
  handles a drain raised by any *other* route, but it is not the path a
  SIGTERM-during-serve takes.
- A `harness run` receiver drains at workflow-driver step boundaries
  first (C-RT-11, full-land 2026-05-20), so its exit is bounded by the
  in-flight step rather than immediate.
- A process that merely installs the stage-7 handlers without a loop
  that acts on the flag does **not** exit.

**These are the common shapes, not an exhaustive taxonomy** — a target
that ignores SIGTERM outright is another, and the tool cannot tell any
of them apart from outside. The diagnostic text is worded as examples
for that reason.

**And the probe itself has a known blind spot, so a timeout is NOT
proof the target is still running.** `_wait_for_exit` polls
`os.kill(pid, 0)`, which on POSIX keeps succeeding for an **unreaped
zombie** — a target that exited cleanly but whose parent/supervisor has
not called `wait()` still reads as alive. This is documented at
`tests/test_admin_shutdown_cli.py::test_shutdown_cli_signals_real_subprocess`,
which for exactly this reason exercises signal delivery without
`--wait`. So exit 3 means *"still observable via `os.kill(pid, 0)`
after the budget"*, which covers three distinct cases: shutdown outran
the budget, nothing acts on the flag, or the target is an unreaped
zombie.

What was STALE and is corrected here: this docstring, the `--wait`
help text and the wait-timeout runtime message all framed the timeout
as *"the CP workflow loop drain is STRUCK, pending
`[[fork-u-rt-44-workflow-loop-drain]]`"* — i.e. as unconditional and as
caused by an open fork. **That fork is CLOSED** —
`harness_runtime.drain`'s own module docstring records C-RT-11
FULL-LAND at 2026-05-20, with the CP workflow driver polling
`ctx.drained_flag` at driver-entry / per-step-pre-entry /
per-step-post-step boundaries. *(An intermediate draft of this refresh
replaced "STRUCK" with a flat "the process does not exit", which
out-of-family review correctly identified as swapping one false
unconditional for another — the daemon shape does exit. Recorded here
rather than quietly re-edited.)*

This matters beyond tidiness: Runtime spec v1.108 §13.7 makes
*"drain pauses before upgrading"* an operator recourse the pause-journal
tenant-keying cutover depends on, and a tool that describes its own
drain as struck is the second leg of why that recourse read as
unavailable.

**Framework discipline** (spec §13): argparse stdlib; no click/typer.

**Pidfile path resolution**: spec says "via PATH_CLASS_REGISTRY". At
HEAD `PATH_CLASS_REGISTRY` has 4 values (no PIDFILE class) per
`[[fork-trace-storage-pathclass-gap]]`. CLI takes `--pidfile-path`
(default `.harness/runtime.pid` CWD-relative).
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time
from pathlib import Path

from harness_runtime.admin.pidfile import PidfileError, read_pidfile

__all__ = ["build_parser", "main"]


# ---------------------------------------------------------------------------
# Defaults + exit codes.
# ---------------------------------------------------------------------------


_DEFAULT_PIDFILE_PATH = Path(".harness/runtime.pid")
_POLL_INTERVAL_SECONDS = 0.1

_EXIT_OK = 0
_EXIT_ADMIN_PIDFILE = 2  # RT-FAIL-ADMIN-PIDFILE per C-RT-13
_EXIT_WAIT_TIMEOUT = 3


# ---------------------------------------------------------------------------
# argparse.
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser. Factored for unit-testability."""
    parser = argparse.ArgumentParser(
        prog="harness-shutdown",
        description=(
            "Signal a running harness instance to drain (Track A admin "
            "stub per Spec_Harness_Runtime_v1.md §13 C-RT-13)."
        ),
    )
    parser.add_argument(
        "--pidfile-path",
        type=Path,
        default=_DEFAULT_PIDFILE_PATH,
        help=(
            f"Path to the pidfile (default: {_DEFAULT_PIDFILE_PATH}). "
            "Written by the receiving harness at stage 7 INGRESS_ACCEPT."
        ),
    )
    parser.add_argument(
        "--wait",
        type=float,
        default=0.0,
        help=(
            "Seconds to wait for the receiving process to exit. Default 0 "
            "(no wait). Polled at 100ms intervals via os.kill(pid, 0). "
            "NOTE: whether SIGTERM leads to exit is the receiver's business. "
            "A `harness daemon` does shut down -- via uvicorn's own captured "
            "SIGTERM handler, which replaces the stage-7 one while serving, "
            "not via drained_flag; a process that installs the stage-7 "
            "handlers without a loop acting on the flag does not exit. Exit 3 "
            "means only that os.kill(pid, 0) still succeeded after the budget "
            "-- which also holds for an UNREAPED ZOMBIE that already exited."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON output. Default is human-readable.",
    )
    return parser


# ---------------------------------------------------------------------------
# Liveness + signal delivery.
# ---------------------------------------------------------------------------


def _is_alive(pid: int) -> bool:
    """Return True iff `pid` is currently a live process.

    Uses `os.kill(pid, 0)` — POSIX existence probe. Returns False on
    `ProcessLookupError` (ESRCH) or `PermissionError` ambiguity (PID
    exists but caller lacks signal permission; for our purposes treat
    as not-our-process and surface as stale).
    """
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return False


def _send_sigterm(pid: int) -> bool:
    """Send SIGTERM to `pid`. Returns True on success, False on failure."""
    try:
        os.kill(pid, signal.SIGTERM)
        return True
    except (ProcessLookupError, PermissionError):
        return False


def _wait_for_exit(pid: int, timeout_seconds: float) -> bool:
    """Poll `pid` for exit. Returns True if exited within `timeout_seconds`."""
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if not _is_alive(pid):
            return True
        time.sleep(_POLL_INTERVAL_SECONDS)
    return not _is_alive(pid)


# ---------------------------------------------------------------------------
# Output.
# ---------------------------------------------------------------------------


def _emit(
    *,
    json_mode: bool,
    pidfile_path: Path,
    pid: int | None,
    status: str,
    detail: str,
    to_stderr: bool = False,
) -> None:
    # Resolve sys.stdout/stderr at call time (NOT def-time default) so
    # pytest's capsys monkey-patch is honored.
    stream = sys.stderr if to_stderr else sys.stdout
    if json_mode:
        payload = {
            "pidfile_path": str(pidfile_path),
            "pid": pid,
            "status": status,
            "detail": detail,
        }
        stream.write(json.dumps(payload, sort_keys=True) + "\n")
    else:
        stream.write(f"harness-shutdown: {status} — {detail}\n")


# ---------------------------------------------------------------------------
# Entry point.
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """`harness-shutdown` entry point.

    Returns the process exit code:
    - 0 (EXIT_OK) — signal delivered (and optionally process exited within
      --wait).
    - 2 (EXIT_ADMIN_PIDFILE) — RT-FAIL-ADMIN-PIDFILE: pidfile missing,
      unparseable, PID stale (not running), or signal delivery denied.
    - 3 (EXIT_WAIT_TIMEOUT) — --wait expired with PID still alive.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    pidfile_path: Path = args.pidfile_path
    wait_seconds: float = args.wait
    json_mode: bool = args.json

    # Step 1: read pidfile.
    try:
        pid = read_pidfile(pidfile_path)
    except PidfileError as exc:
        _emit(
            json_mode=json_mode,
            pidfile_path=pidfile_path,
            pid=None,
            status="RT-FAIL-ADMIN-PIDFILE",
            detail=str(exc),
            to_stderr=True,
        )
        return _EXIT_ADMIN_PIDFILE

    # Step 2: liveness probe (stale detection).
    if not _is_alive(pid):
        _emit(
            json_mode=json_mode,
            pidfile_path=pidfile_path,
            pid=pid,
            status="RT-FAIL-ADMIN-PIDFILE",
            detail=f"stale: pid {pid} not running",
            to_stderr=True,
        )
        return _EXIT_ADMIN_PIDFILE

    # Step 3: send SIGTERM.
    if not _send_sigterm(pid):
        _emit(
            json_mode=json_mode,
            pidfile_path=pidfile_path,
            pid=pid,
            status="RT-FAIL-ADMIN-PIDFILE",
            detail=f"signal delivery denied for pid {pid}",
            to_stderr=True,
        )
        return _EXIT_ADMIN_PIDFILE

    # Step 4: optional wait for exit.
    if wait_seconds > 0:
        exited = _wait_for_exit(pid, wait_seconds)
        if not exited:
            _emit(
                json_mode=json_mode,
                pidfile_path=pidfile_path,
                pid=pid,
                status="wait-timeout",
                detail=(
                    f"SIGTERM delivered to pid {pid}; still observable via "
                    f"os.kill(pid, 0) after {wait_seconds}s wait. This is not "
                    f"by itself proof the target is still working. Common "
                    f"causes, not an exhaustive list: shutdown outran the "
                    f"budget (a `harness daemon` exits via uvicorn's captured "
                    f"handler, not drained_flag; a `harness run` receiver "
                    f"drains at step boundaries first); nothing in the target "
                    f"acts on drained_flag; the target ignores SIGTERM; or it "
                    f"is an UNREAPED ZOMBIE that already exited."
                ),
            )
            return _EXIT_WAIT_TIMEOUT
        _emit(
            json_mode=json_mode,
            pidfile_path=pidfile_path,
            pid=pid,
            status="exited",
            detail=f"pid {pid} exited within wait budget",
        )
        return _EXIT_OK

    _emit(
        json_mode=json_mode,
        pidfile_path=pidfile_path,
        pid=pid,
        status="signaled",
        detail=f"SIGTERM delivered to pid {pid}",
    )
    return _EXIT_OK


if __name__ == "__main__":  # pragma: no cover — invoked via console_script
    raise SystemExit(main())
