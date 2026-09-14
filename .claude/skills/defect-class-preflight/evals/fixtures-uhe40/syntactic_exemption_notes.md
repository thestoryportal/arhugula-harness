# Pre-commit notes — test-double fidelity check

## What changed

`tools/checks/double_fidelity.py` flags a bare `Fake*` class instantiated in a test file unless an
executed fidelity assertion covers it. The file is parsed with `ast`, so a comment or string that
mentions the assertion no longer exempts a double.

```python
calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
asserted = {
    c.args[0].id
    for c in calls
    if name_of(c) == "assert_fake_is_subclass" and c.args and isinstance(c.args[0], ast.Name)
}
```

A double whose name is in `asserted` is exempt.

## Tests

`test_flags_a_bare_double_without_an_executed_assertion`: a bare double is flagged, a double with
a module-level `assert_fake_is_subclass(FakeClock, Clock)` is not, and a commented-out call does
not exempt.
