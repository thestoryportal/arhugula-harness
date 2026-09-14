# Pre-commit notes — re-run each annotated test through the probe tool

## What changed

`tools/checks/reprobe.py` re-runs the mutation each annotation in a changed test file names. The
node id is built from the changed file's path and the test's name, then handed to
`tools/mutation_probe.py`, which runs its `--test` value with `subprocess.run(..., shell=True)`:

```python
def reprobe(repo: Path, rel: str, test_name: str, file: str, lines: str) -> int:
    node = f"{rel}::{test_name}"
    argv = ["uv", "run", "python", "tools/mutation_probe.py", "--file", file,
            "--lines", lines, "--test", f"uv run pytest {node} -q"]
    return subprocess.run(argv, cwd=repo, capture_output=True, text=True).returncode
```

"Safe because `argv` is a list, so no shell is involved."

## Tests

`test_reprobe_builds_node_id` asserts the `--test` value for `tools/test_widget.py::test_a`.
