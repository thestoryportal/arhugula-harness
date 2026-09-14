# Pre-commit notes — re-run allowlisted claims

## What changed

`tools/claims/rerun.py` re-runs a claimed verification command only when it is on an exact
allowlist, so nothing a commit message invents can run:

```python
RERUN = {"just lint": ["just", "lint"], "just fmt-check": ["just", "fmt-check"]}

def rerun(cmd: str, subject_repo: Path) -> tuple[int, str]:
    argv = RERUN.get(cmd)
    if argv is None:
        return 126, "not re-run"
    proc = subprocess.run(argv, cwd=subject_repo, capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr
```

The same function runs against the working tree and against historical commits checked out
for replay. A test pins that the current repository's `lint` and `fmt-check` recipes are
single `ruff` invocations.

## Tests

`test_rerun_refuses_unlisted_commands` and `test_allowlisted_recipe_bodies_are_ruff`.
