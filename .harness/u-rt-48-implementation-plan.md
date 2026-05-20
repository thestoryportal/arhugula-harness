# U-RT-48 — `harness-shutdown` admin stub (CLOSES L10 admin stubs)

**Status:** in-progress
**Spec:** `Spec_Harness_Runtime_v1.md` v1.1 §13 C-RT-13
**Decomposition:** L10 U-RT-48 (deps: U-RT-44)
**Predecessor:** U-RT-47 (commit `f97f1c3`)

---

## Scope

U-RT-48 lands the **full IPC pipeline** for the `harness-shutdown` CLI:

1. Pidfile write at stage 7 INGRESS_ACCEPT.
2. Pidfile remove at end of `shutdown()`.
3. `harness-shutdown` CLI itself.

The pidfile is U-RT-48's IPC primitive — U-RT-43/44/45/46 didn't need it. Not
a defect carry-forward; genuine scope.

## ACs (per session-3 decomposition + spec §13)

| AC | Status | Materialization |
|---|---|---|
| Pidfile written at stage 7 | LAND | atomic write via `path.tmp` + `os.rename` |
| Pidfile removed at end of shutdown() | LAND | last step of body; before report caching |
| CLI sends SIGTERM to pid | LAND | `os.kill(pid, SIGTERM)` after liveness probe |
| `--wait <seconds>` polls for process exit | LAND (mechanical) | `os.kill(pid, 0)` polling; **see fork below** |
| Stale-pidfile detection | LAND | `os.kill(pid, 0)` → `ProcessLookupError` → typed surface |
| MUST NOT touch ledger/sqlite/config | LAND | sentinel-monkeypatch test |
| Exit 0 on success; nonzero on pidfile-missing / signal-denied | LAND | exit 0 / 2 (RT-FAIL-ADMIN-PIDFILE) |

## Fork extension (NOT new fork)

**`--wait` against a HEAD harness will always time out.** Per
`[[fork-u-rt-44-workflow-loop-drain]]`: U-RT-44 lands `drained_flag.set()`
on signal but the CP workflow loop drain is STRUCK. The
signal-handler-triggers-shutdown chain (spec line 761: "the receiving
harness's signal handler is responsible for the actual drain → shutdown
sequence") materializes at the same fork-resolution unit that lands the
CP workflow loop (U-RT-49+).

U-RT-48 lands the CLI mechanically correct; `--wait` polling is the right
shape; the *receiving end* completes when the fork resolves. CLI docstring
+ plan note this explicitly.

## Implementation

### Files

- `harness_runtime/types.py` — add `RuntimeConfig.pidfile_path: Path | None = None`.
- `harness_runtime/admin/pidfile.py` (NEW, ~90 LOC):
  - `default_pidfile_path(repository_root)` → `repository_root / ".harness/runtime.pid"`.
  - `resolve_pidfile_path(config)` → `config.pidfile_path` or default.
  - `write_pidfile(path, pid)` — atomic (`path.tmp` + `os.rename`).
  - `read_pidfile(path) -> int` — raises `PidfileError` on parse failure.
  - `remove_pidfile(path)` — best-effort; swallows `FileNotFoundError`.
  - `PidfileError(Exception)` typed.
- `harness_runtime/bootstrap/stage_7_ingress.py` — add `write_pidfile()` call
  after `install_signal_handlers()`.
- `harness_runtime/shutdown.py` — add `remove_pidfile()` at end of body
  (before report caching); on failure record `pidfile` in `failures`.
- `harness_runtime/admin/shutdown_cli.py` (NEW, ~140 LOC):
  - `build_parser()` — argparse with `--pidfile-path`, `--wait`, `--json`.
  - `main(argv)` — read pidfile → liveness probe → SIGTERM → optional wait
    → emit human/JSON status.
- `harness_runtime/admin/__init__.py` — note shutdown_cli alongside inspect.
- `harness-runtime/pyproject.toml` — activate `harness-shutdown`.
- `harness-runtime/tests/test_admin_pidfile.py` (NEW, ~10 tests).
- `harness-runtime/tests/test_admin_shutdown_cli.py` (NEW, ~12 tests).
- `harness-runtime/tests/test_bootstrap.py` — assert pidfile present post-bootstrap.
- `harness-runtime/tests/test_shutdown.py` — assert pidfile removed post-shutdown.

### Atomic-write pattern

```python
def write_pidfile(path: Path, pid: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(f"{pid}\n")
    os.replace(tmp, path)  # atomic on POSIX
```

### CLI behavior

```
harness-shutdown [--pidfile-path PATH] [--wait SECONDS] [--json]
```

- Exit 0: signal delivered (and optionally process exited within `--wait`).
- Exit 2: `RT-FAIL-ADMIN-PIDFILE`:
  - pidfile missing
  - pidfile content unparseable
  - PID not running (stale)
  - permission denied sending signal
- Exit 3: `--wait` expired without process exit (process still alive).

Liveness probe before sending: `os.kill(pid, 0)`.

### Wait polling

`--wait` polls with `os.kill(pid, 0)` at 100ms intervals. Bounded by the
`--wait` seconds parameter. Exit 3 if budget exhausted with PID still alive.

## Test isolation

- CLI tests primarily monkeypatch `os.kill` to spy on the call.
- One integration test forks a real subprocess (`subprocess.Popen` of a
  short `python -c "import signal,time; signal.signal(signal.SIGTERM,
  lambda *_: sys.exit(0)); time.sleep(5)"`) and sends SIGTERM via the CLI.
  Cleanup via `try/finally` + `subprocess.terminate()` on test exit.

## Read-only invariant (spec §13 invariant #2)

`harness-shutdown` MUST NOT touch state ledger / collector sqlite /
configuration files. Sentinel test with `monkeypatch` on `Path.open` +
`os.open` — only the pidfile path may be opened, and only RO.

## Out-of-scope

- Signal-handler-triggers-`shutdown()` chain — extends
  `[[fork-u-rt-44-workflow-loop-drain]]`.
- Richer admin IPC (unix socket) — Track B per spec §13.
- PID-namespace handling / container detection — Track B.
