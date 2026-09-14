# Pre-commit notes — re-verifying mutation-probe annotations

## What changed

`tools/checks/reverify.py` re-runs each annotation's logged mutation through
`tools/mutation_probe.py` (exit 0 pinned, 1 PROBE FAILED, 2 refused, 3 restore failure) and turns
the exit into a finding. Exit 3 stops the run, because the probed file may still be mutated.

```python
rc, output = self.probe(repo, target, lines, node)
if rc == 3:
    raise ProbeRestoreError(f"{node}: restore unverified -- the file may still be mutated")
outcomes = {
    0: [],
    1: [Finding(node, "annotation is FALSE", severity="hard")],
}
indeterminate = [Finding(node, f"probe indeterminate (exit {rc})")]
return outcomes.get(rc, indeterminate)
```

The probe tool's own docs say a SIGKILL of the runner leaves the file mutated until a later
probe reconciles it. The check runs advisory by default, so warnings never fail the run.

## Tests

`test_restore_failure_stops_the_run` (exit 3 raises) and
`test_indeterminate_is_named` (exit 2 yields a warning).
