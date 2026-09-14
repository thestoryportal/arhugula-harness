# Pre-commit notes — re-run a claimed lint with trusted ruff

## What changed

A claim of `Verified: `just lint`` is re-run without trusting the subject's justfile: the checker
invokes this interpreter's own ruff against the subject tree.

```python
RERUN = {"just lint": (sys.executable, "-m", "ruff", "check", ".")}

def rerun(cmd: str, subject_repo: Path) -> tuple[int, str]:
    argv = RERUN[cmd]
    proc = subprocess.run(list(argv), cwd=subject_repo, capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr
```

"Trusted because `sys.executable` is ours, not the subject's."

## Tests

`test_rerun_uses_this_interpreter` asserts `argv[0] == sys.executable`.
