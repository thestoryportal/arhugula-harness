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


# mutation-probe: drop the `any(...)` window scan in block_is_present (return False)
def test_block_is_present_is_content_anchored_not_line_anchored():
    d = ps.block_digest(SRC, 2, 3)
    assert ps.block_is_present(SRC, 2, d)
    # an insertion ABOVE the block shifts its lines but not its bytes: still present
    assert ps.block_is_present("import os\n\n" + SRC, 2, d)
    # an edit INSIDE the block: gone
    assert not ps.block_is_present(SRC.replace("b = 2", "b = 3"), 2, d)
    # the wrong window length never matches, and a window longer than the file is refused
    assert not ps.block_is_present(SRC, 1, d)
    assert not ps.block_is_present(SRC, 99, d)


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


def test_test_body_digest_spans_decorators_through_end_and_ignores_siblings():
    body = "@pytest.mark.x\ndef test_f():\n    assert f() == 3\n"
    assert ps.test_body_digest(TEST, "test_f") == _d(body)
    # editing an UNRELATED test leaves the digest alone; editing the body changes it
    assert ps.test_body_digest(TEST.replace("assert True", "assert 1"), "test_f") == _d(body)
    assert ps.test_body_digest(TEST.replace("== 3", "== 4"), "test_f") != _d(body)
    # the annotation comment above the decorator is not part of the body
    assert ps.test_body_digest(TEST.replace("drop b", "drop a"), "test_f") == _d(body)


def test_test_body_digest_is_none_when_unresolvable():
    assert ps.test_body_digest(TEST, "test_missing") is None
    assert ps.test_body_digest("def (:\n", "test_f") is None
    two = "class A:\n    def test_f(self): pass\nclass B:\n    def test_f(self): pass\n"
    assert ps.test_body_digest(two, "test_f") is None  # ambiguous: which one ran?


def _row(**over):
    row = {
        "lines": "2-3",
        "block_sha": ps.block_digest(SRC, 2, 3),
        "test_scope": ps.TEST_SCOPE_BODY,
        "test_body_sha": ps.test_body_digest(TEST, "test_f"),
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
    assert ps.BlockPin.from_row(_row(test_body_sha=None), "tools/test_x.py::test_f") is None
    # BODY scope needs a node id that names a function
    assert ps.BlockPin.from_row(_row(), "tools/test_x.py") is None
    art = ps.BlockPin.from_row(_row(test_scope=ps.TEST_SCOPE_ARTIFACT), "tools/test_x.py")
    assert art is not None and art.test_node is None and art.test_digest == _row()["test_sha"]


# mutation-probe: drop the `if self.test_scope == TEST_SCOPE_BODY` arm in BlockPin.live
def test_block_pin_live_is_the_scoped_theorem():
    pin = ps.BlockPin.from_row(_row(), "tools/test_x.py::test_f")
    assert pin is not None
    assert pin.live(SRC, TEST.encode())
    # unrelated edits on BOTH sides stay live: a line above the block, a sibling test
    assert pin.live("# header\n" + SRC, TEST.replace("assert True", "assert 1").encode())
    # the block edited -> stale; the body edited -> stale
    assert not pin.live(SRC.replace("b = 2", "b = 3"), TEST.encode())
    assert not pin.live(SRC, TEST.replace("== 3", "== 4").encode())
    # artifact scope: ANY test-file edit stales (the whole-file theorem, kept for -k / bash)
    art = ps.BlockPin.from_row(_row(test_scope=ps.TEST_SCOPE_ARTIFACT), "tools/test_x.py")
    assert art is not None and art.live(SRC, TEST.encode())
    assert not art.live(SRC, TEST.replace("assert True", "assert 1").encode())
    # a test artifact that is not UTF-8 under BODY scope is never live
    assert not pin.live(SRC, b"\xff\xfe")
