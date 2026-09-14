# Pre-commit notes — re-verify mutation-probe annotations in the advisory checker

## What changed

`tools/checks/probe_reverify.py` re-runs the mutation each `# mutation-probe:` annotation names,
through `tools/mutation_probe.py`, whose exit codes are: `0` the test went red (pinned), `1` the
test stayed green (the annotation is false), `2` refused or indeterminate (file untouched or
verifiably restored), `3` restore failure (the file may still be mutated).

```python
def verify(node: str, file: str, lines: str) -> list[Finding]:
    argv = ["uv", "run", "python", "tools/mutation_probe.py", "--file", file,
            "--lines", lines, "--test", f"uv run pytest {node} -q"]
    rc = subprocess.run(argv, capture_output=True).returncode
    if rc == 0:
        return []
    if rc == 1:
        return [Finding(node, "annotation is FALSE", severity="hard")]
    return [Finding(node, f"probe indeterminate (exit {rc})", severity="warn")]
```

The checker ships in advisory mode: findings are logged, and the run exits 0 unless a blocking
check reports one. After each annotation it continues with the next annotation, then with the
remaining checks.

## Tests

`test_false_annotation_is_hard` (exit 1) and `test_indeterminate_is_warn` (exit 2).
