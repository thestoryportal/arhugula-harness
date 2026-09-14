# Pre-commit notes — re-run claimed verification commands

## What changed

`tools/claims/rerun.py` re-runs every command a commit message claims under a `Verified:` line,
so a "clean" claim is checked rather than trusted. To keep that safe, only a read-only grammar
is executed:

```python
TOKEN = r"[\w./=:@,+-]+"
READ_ONLY = re.compile(rf"just [\w-]+-check(?: {TOKEN})*|uv run pytest(?: {TOKEN})*")

def rerun(cmd: str, repo: Path) -> tuple[int, str]:
    if READ_ONLY.fullmatch(cmd) is None:
        return 126, "not re-run"
    proc = subprocess.run(cmd.split(), cwd=repo, capture_output=True, text=True, timeout=1800)
    return proc.returncode, proc.stdout + proc.stderr
```

The checker itself is exposed as the justfile recipe `claims-check`
(`uv run python tools/claims/rerun.py --all`). The same justfile also carries `fmt` (rewrites
files in place) and `protection-rollback` (removes branch protection).

## Tests

`test_rerun_refuses_shell_syntax` asserts that `just lint-check; rm -rf /` is not executed.
