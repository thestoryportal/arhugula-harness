# Pre-commit notes — safe probe commands, matched against the probe log

## What changed

`tools/checks/reverify.py` re-runs a mutation probe for each annotated test. `mutation_probe.py`
runs `--test` through a shell and appends the command verbatim to
`.harness/mutation-probe-log.jsonl`, so the node, derived from a filename, is now quoted:

```python
def run_probe(repo, file, lines, node):
    cmd = f"uv run pytest {shlex.quote(node)} -q"
    return subprocess.run(["uv", "run", "python", "tools/mutation_probe.py",
                           "--file", file, "--lines", lines, "--test", cmd], cwd=repo).returncode
```

Evidence lookup reuses the probe tool's own parser, exactly as `lanes_verify` does:

```python
def probed(row, node):
    toks = row["test"].split()
    return pytest_targets(toks) == [node]
```

`mutation_probe.py` itself tokenizes `--test` with `test_cmd.split()` before calling
`pytest_targets`.

## Tests

`test_probe_command_quotes_the_filename_derived_node` asserts
`uv run pytest 'tools/test_$(id).py::test_t' -q`, and `test_reverify_matches_a_logged_row` uses
`tools/test_x.py::test_t`.
