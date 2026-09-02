"""Hermetic tests for tools/pin_scope.py (U-SR-09 b1): the scoped pin theorem, pure."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pin_scope as ps

SRC = "def f():\n    a = 1\n    b = 2\n    return a + b\n"
TEST = (
    "import pytest\n"
    "\n"
    "# mutation-probe: drop b\n"
    "@pytest.mark.x\n"
    "def test_f():\n"
    "    assert f() == 3\n"
    "\n"
    "def test_other():\n"
    "    assert True\n"
)


def _d(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def test_block_digest_is_the_range_bytes_with_line_endings():
    assert ps.block_digest(SRC, 2, 3) == _d("    a = 1\n    b = 2\n")
    assert ps.block_digest(SRC, 4, 4) == _d("    return a + b\n")
    with pytest.raises(ValueError):
        ps.block_digest(SRC, 4, 5)


# mutation-probe: drop the `== 1` uniqueness test in block_is_present (return occurrences > 0)
def test_block_is_present_is_content_anchored_and_requires_a_unique_block():
    d = ps.block_digest(SRC, 2, 3)
    assert ps.block_occurrences(SRC, 2, d) == 1 and ps.block_is_present(SRC, 2, d)
    # an insertion ABOVE the block shifts its lines but not its bytes: still present
    assert ps.block_is_present("import os\n\n" + SRC, 2, d)
    # an edit INSIDE the block: gone
    assert not ps.block_is_present(SRC.replace("b = 2", "b = 3"), 2, d)
    # the wrong window length never matches, and a window longer than the file is refused
    assert not ps.block_is_present(SRC, 1, d)
    assert not ps.block_is_present(SRC, 99, d)
    # codex u-sr-09 r1: a block that occurs TWICE is never present -- deleting the probed
    # copy would leave the other to vouch for it
    twice = SRC + "\n\ndef g():\n    a = 1\n    b = 2\n    return a\n"
    assert ps.block_occurrences(twice, 2, d) == 2 and not ps.block_is_present(twice, 2, d)


@pytest.mark.parametrize(
    ("nodeid", "tail"),
    [
        ("tools/test_x.py::test_f", "test_f"),
        ("tools/test_x.py::TestK::test_f[a-b]", "test_f"),
        ("tools/test_x.py", None),
        ("tools/test_x.py::", None),
    ],
)
def test_node_tail(nodeid, tail):
    assert ps.node_tail(nodeid) == tail


# mutation-probe: drop the `and not _runs_at_import(n)` clause in test_slice_digest
def test_test_slice_digest_drops_only_sibling_top_level_tests():
    # the slice = the kept top-level nodes' own segments (the import; the annotated,
    # decorated test_f), concatenated -- `test_other` and every inter-node blank line gone
    sliced = "import pytest\n" + "@pytest.mark.x\ndef test_f():\n    assert f() == 3\n"
    assert ps.test_slice_digest(TEST, "test_f") == _d(sliced)
    # INSERTING a sibling anywhere (with its blank lines) leaves the digest alone -- this is the
    # churn the slice exists to remove (found on the arc's own witness file, u-sr-09 r4)
    assert ps.test_slice_digest("def test_zero():\n    pass\n\n\n" + TEST, "test_f") == _d(sliced)
    assert ps.test_slice_digest(TEST + "\n\n\ndef test_more():\n    pass\n", "test_f") == _d(sliced)
    # editing an UNRELATED test leaves the digest alone; editing the body changes it
    assert ps.test_slice_digest(TEST.replace("assert True", "assert 1"), "test_f") == _d(sliced)
    assert ps.test_slice_digest(TEST.replace("== 3", "== 4"), "test_f") != _d(sliced)
    # codex u-sr-09 r1 P2: imports, marks and fixtures are BOUND -- swapping the import or
    # adding a module-wide skip changes the digest
    assert ps.test_slice_digest(
        TEST.replace("import pytest", "import pytest as _p"), "test_f"
    ) != _d(sliced)
    assert ps.test_slice_digest("pytestmark = pytest.mark.skip\n" + TEST, "test_f") != _d(sliced)
    # a comment BETWEEN nodes (the annotation line) is not part of any node's segment: its
    # target path is enforced by `required_probes`, not by this digest
    assert ps.test_slice_digest(TEST.replace("drop b", "drop a"), "test_f") == _d(sliced)
    # codex u-sr-09 r2 P2: a sibling test_* the selected test CALLS is part of its judgement
    # and stays in the slice (transitively); hollowing it changes the digest
    calls = (
        "def test_helper():\n    assert f() == 3\n\n\n"
        "def test_inner():\n    test_helper()\n\n\n"
        "def test_f():\n    test_inner()\n\n\n"
        "def test_other():\n    assert True\n"
    )
    base = ps.test_slice_digest(calls, "test_f")
    assert base == ps.test_slice_digest(
        calls.replace("def test_other():\n    assert True\n", ""), "test_f"
    )
    assert ps.test_slice_digest(calls.replace("assert f() == 3", "pass"), "test_f") != base
    assert ps.test_slice_digest(calls.replace("assert True", "assert 1"), "test_f") == base
    # codex u-sr-09 r3: a test_*-named pytest FIXTURE (autouse or not) is harness, never a
    # removable sibling -- editing it changes the digest
    fixt = (
        "import pytest\n\n\n"
        "@pytest.fixture(autouse=True)\ndef test_setup():\n    yield 1\n\n\n"
        "@pytest.fixture\ndef test_thing():\n    return 2\n\n\n"
        "def test_f():\n    assert f() == 3\n\n\n"
        "def test_other():\n    assert True\n"
    )
    base = ps.test_slice_digest(fixt, "test_f")
    assert base == ps.test_slice_digest(
        fixt.replace("def test_other():\n    assert True\n", ""), "test_f"
    )
    assert ps.test_slice_digest(fixt.replace("yield 1", "yield 0"), "test_f") != base
    assert ps.test_slice_digest(fixt.replace("return 2", "return 0"), "test_f") != base
    # codex u-sr-09 r4: the fixture decorator under an import alias is still a fixture
    aliased = (
        "from pytest import fixture as fx\n\n\n"
        "@fx(autouse=True)\ndef test_setup():\n    yield 1\n\n\n"
        "def test_f():\n    assert f() == 3\n\n\n"
        "def test_other():\n    assert True\n"
    )
    base = ps.test_slice_digest(aliased, "test_f")
    without = aliased.replace("def test_other():\n    assert True\n", "")
    assert base == ps.test_slice_digest(without, "test_f")
    assert ps.test_slice_digest(aliased.replace("yield 1", "yield 0"), "test_f") != base
    # codex u-sr-09 r6: a sibling whose decorator or default RUNS AT IMPORT (`@register(1)`,
    # `def test_s(x=setup())`) is kept -- a plain pytest mark or a mark with literal args
    # is not (its sibling stays droppable)
    imp = (
        "import pytest\n\n\n"
        "@register(1)\ndef test_side():\n    pass\n\n\n"
        "def test_dflt(x=setup()):\n    pass\n\n\n"
        '@pytest.mark.parametrize("a", [1, 2])\ndef test_param(a):\n    pass\n\n\n'
        '@pytest.mark.parametrize("a", make())\ndef test_call(a):\n    pass\n\n\n'
        "def test_f():\n    assert f() == 3\n"
    )
    base = ps.test_slice_digest(imp, "test_f")
    assert ps.test_slice_digest(imp.replace("@register(1)", "@register(0)"), "test_f") != base
    assert ps.test_slice_digest(imp.replace("x=setup()", "x=setup(1)"), "test_f") != base
    assert ps.test_slice_digest(imp.replace("make()", "make(2)"), "test_f") != base
    assert ps.test_slice_digest(imp.replace("[1, 2]", "[1, 3]"), "test_f") == base


def test_test_slice_digest_is_none_when_unresolvable():
    assert ps.test_slice_digest(TEST, "test_missing") is None
    assert ps.test_slice_digest("def (:\n", "test_f") is None
    two = "class A:\n    def test_f(self): pass\nclass B:\n    def test_f(self): pass\n"
    assert ps.test_slice_digest(two, "test_f") is None  # ambiguous: which one ran?


def _row(**over):
    row = {
        "lines": "2-3",
        "block_sha": ps.block_digest(SRC, 2, 3),
        "test_scope": ps.TEST_SCOPE_SLICE,
        "test_slice_sha": ps.test_slice_digest(TEST, "test_f"),
        "test_sha": ps.digest16(TEST.encode()),
    }
    row.update(over)
    return row


def test_block_pin_parses_a_well_formed_row_and_refuses_a_malformed_one():
    pin = ps.BlockPin.from_row(_row(), "tools/test_x.py::test_f")
    assert pin is not None and pin.n_lines == 2 and pin.test_node == "test_f"
    assert ps.BlockPin.from_row(_row(lines="x"), "tools/test_x.py::test_f") is None
    assert ps.BlockPin.from_row(_row(block_sha=None), "tools/test_x.py::test_f") is None
    assert ps.BlockPin.from_row(_row(test_scope="nope"), "tools/test_x.py::test_f") is None
    assert ps.BlockPin.from_row(_row(test_slice_sha=None), "tools/test_x.py::test_f") is None
    # SLICE scope needs a node id that names a function
    assert ps.BlockPin.from_row(_row(), "tools/test_x.py") is None
    art = ps.BlockPin.from_row(_row(test_scope=ps.TEST_SCOPE_ARTIFACT), "tools/test_x.py")
    assert art is not None and art.test_node is None and art.test_digest == _row()["test_sha"]


# mutation-probe: drop the `if self.test_scope == TEST_SCOPE_SLICE` arm in BlockPin.live
def test_block_pin_live_is_the_scoped_theorem():
    pin = ps.BlockPin.from_row(_row(), "tools/test_x.py::test_f")
    assert pin is not None
    assert pin.live(SRC, TEST.encode())
    # unrelated edits on BOTH sides stay live: a line above the block, a sibling test
    assert pin.live("# header\n" + SRC, TEST.replace("assert True", "assert 1").encode())
    # the block edited -> stale; the body edited -> stale; the block duplicated -> stale
    assert not pin.live(SRC.replace("b = 2", "b = 3"), TEST.encode())
    assert not pin.live(SRC, TEST.replace("== 3", "== 4").encode())
    assert not pin.live(SRC + SRC.replace("def f", "def h"), TEST.encode())
    # artifact scope: ANY test-file edit stales (the whole-file theorem, kept for -k / bash)
    art = ps.BlockPin.from_row(_row(test_scope=ps.TEST_SCOPE_ARTIFACT), "tools/test_x.py")
    assert art is not None and art.live(SRC, TEST.encode())
    assert not art.live(SRC, TEST.replace("assert True", "assert 1").encode())
    # a test artifact that is not UTF-8 under SLICE scope is never live
    assert not pin.live(SRC, b"\xff\xfe")
