"""The CI axis-isolation legs test only roots that pytest is configured to collect."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEG = re.compile(r"\{ axis: (?P<axis>[a-z]+), test_root: (?P<root>[\w./-]+) \}")


def test_every_axis_isolation_root_is_a_configured_testpath() -> None:
    pytest_options = tomllib.loads((ROOT / "pyproject.toml").read_text())["tool"]["pytest"]
    testpaths = pytest_options["ini_options"]["testpaths"]
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    legs = {match["axis"]: match["root"] for match in LEG.finditer(ci)}

    # One-directional: the six existing isolation legs, each on a configured root.
    assert sorted(legs) == ["as", "core", "cp", "cxa", "is", "od"]
    assert [root for root in legs.values() if root not in testpaths] == []
