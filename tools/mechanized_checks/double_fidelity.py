"""wrong-fidelity test doubles (C-HE-31 §1, hybrid): a `Fake*` / `Stub*` / `Dummy*` class
declared with no base and instantiated in a changed test file, with no executed fidelity assertion.

The file is parsed, not searched: only a MODULE-LEVEL `assert_fake_is_subclass(<double>, ...)`
statement exempts a double, since it runs whenever the file imports. A comment or string that
merely mentions one does not, and neither does a call that may never run -- under an `if` or
`try`, or inside a helper nobody calls. Named `double_fidelity`, not
`test_double_fidelity`, so pytest never collects this module; the check_id keeps the spec's name."""

from __future__ import annotations

import ast
from pathlib import Path

from .core import MechFinding, Subject

DOUBLE_PREFIXES = ("Fake", "Stub", "Dummy")
ASSERTION = "assert_fake_is_subclass"


def assert_fake_is_subclass(fake: type, real: type) -> None:
    """Shared fixture helper: a double stands in for `real` only if it IS a `real` -- a
    wrong-fidelity double passes tests the real type would fail."""
    if not issubclass(fake, real):
        raise AssertionError(
            f"{fake.__name__} is not a subclass of {real.__name__}: wrong-fidelity test double"
        )


def _called(call: ast.Call) -> str | None:
    match call.func:
        case ast.Name(id=name) | ast.Attribute(attr=name):
            return name
        case _:
            return None


def _asserted(stmt: ast.stmt) -> str | None:
    """The double a module-level `assert_fake_is_subclass(<double>, ...)` statement names."""
    match stmt:
        case ast.Expr(value=ast.Call(args=[ast.Name(id=double), *_]) as call) if (
            _called(call) == ASSERTION
        ):
            return double
        case _:
            return None


def _findings(rel: str, text: str) -> list[MechFinding]:
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return [
            MechFinding(
                f"{rel}:{exc.lineno or 1}",
                f"test file does not parse ({exc.msg}); its test doubles were not checked",
                "a changed test file parses",
            )
        ]
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
    instantiated = {_called(call) for call in calls}
    asserted = {_asserted(stmt) for stmt in tree.body}
    return [
        MechFinding(
            f"{rel}:{double.lineno}",
            f"test double {double.name} has no base class and no fidelity assertion",
            f"{ASSERTION}({double.name}, <real type>) as a module-level statement",
        )
        for double in ast.walk(tree)
        if isinstance(double, ast.ClassDef) and double.name.startswith(DOUBLE_PREFIXES)
        if not double.bases and double.name in instantiated
        if double.name not in asserted
    ]


class Check:
    check_id = "test_double_fidelity"
    kind = "hybrid"
    replayable = True

    def run(self, subject: Subject) -> list[MechFinding]:
        return [
            finding
            for rel, text in subject.changed_texts(".py")
            if Path(rel).name.startswith("test_")
            for finding in _findings(rel, text)
        ]
