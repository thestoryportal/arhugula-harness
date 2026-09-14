# Pre-commit notes — matching annotations to their probe-log rows

## What changed

Each test may carry one or more `# mutation-probe: <path>:<lines> <desc>` annotations; stacked
annotations above one test each bind it. The re-verifier finds each annotation's evidence in
`.harness/mutation-probe-log.jsonl` and re-runs that row's range.

```python
def annotations(path):
    # (test name, probed file) for every annotation
    return [(m["name"], m["path"]) for m in ANNOT.finditer(path.read_text())]

def logged_range(rows, node, target):
    pinned = [r for r in rows if r["rc"] == 0 and r["node"] == node and r["file"] == target]
    return pinned[-1]["lines"] if pinned else None

for node, target in annotated:
    lines = logged_range(rows, node, target)
    verify(node, target, lines)
```

## Tests

`test_reverify_detects_a_false_annotation` and `test_unprobed_annotation_is_named`, each with a
single annotation on a single test.
