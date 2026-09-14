"""wrong-fidelity test doubles (C-HE-31 §1, hybrid): a `Fake*` / `Stub*` / `Dummy*` class
declared with no base and instantiated in a changed test file, with no fidelity assertion.

Named `double_fidelity`, not `test_double_fidelity`, so pytest never collects this module as a
test file; the check_id keeps the class name the spec uses."""

from __future__ import annotations

import re
from pathlib import Path

from .core import MechFinding, Subject, line_of

BARE_DOUBLE = re.compile(r"^[ \t]*class[ \t]+(?P<name>(?:Fake|Stub|Dummy)\w*)[ \t]*:", re.M)


def assert_fake_is_subclass(fake: type, real: type) -> None:
    """Shared fixture helper: a double stands in for `real` only if it IS a `real` -- a
    wrong-fidelity double passes tests the real type would fail."""
    if not issubclass(fake, real):
        raise AssertionError(
            f"{fake.__name__} is not a subclass of {real.__name__}: wrong-fidelity test double"
        )


class Check:
    check_id = "test_double_fidelity"
    kind = "hybrid"

    def run(self, subject: Subject) -> list[MechFinding]:
        return [
            MechFinding(
                f"{rel}:{line_of(text, m.start())}",
                f"test double {m['name']} has no base class and no fidelity assertion",
                f"assert_fake_is_subclass({m['name']}, <real type>) in a shared fixture",
            )
            for rel, text in subject.changed_texts(".py")
            if Path(rel).name.startswith("test_")
            for m in BARE_DOUBLE.finditer(text)
            if re.search(rf"\b{m['name']}\(", text)
            and f"assert_fake_is_subclass({m['name']}" not in text
        ]
