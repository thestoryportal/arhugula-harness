"""The mutation pin's binding theorem (U-SR-09 b1, plan §8 R2; [B] F7/c1).

A PINNED probe verdict says "commenting out THESE source lines made THIS test go red". The
pre-U-SR-09 pin bound that verdict to the digest of the whole source file and the whole test
file, so an edit ANYWHERE in either file -- a docstring, an unrelated function, a new assert in
another test -- staled every pin in the pair and forced a re-pin (12 of 13 pin commits on the
U-HE-35 arc, 1.07M IET). This module owns the scoped theorem the pin now carries instead:

    block  -- the probed lines' bytes still occur verbatim, contiguously, somewhere in the file
              (content-anchored: an insertion ABOVE the block shifts its line numbers but not
              its bytes, so the pin stays live and `lines` becomes provenance-at-probe-time,
              not a live locator);
    test   -- the judging test's BODY (the `def` plus its decorators, by AST) is unchanged when
              the probe command names one node id; the whole artifact otherwise (`-k` selectors
              can match several tests, a shell suite has no `def`).

What the weaker theorem gives up, stated once so no reader re-derives it: an edit OUTSIDE the
block that makes the block dead code (or a fixture change that hollows the test) is not caught
-- the merge-gate witness lens re-probes contested changes, and charter §4 names whole-file
scope as the one defect. The producer (`mutation_probe.log_result`) writes the digests; the
consumer (`lanes_verify._pin_is_live`) re-derives them at HEAD. Both import from here so the
format has ONE home. [LAW:one-source-of-truth]

Pure: text in, digests out. No I/O, no clock, no repo. [LAW:effects-at-boundaries]
"""

from __future__ import annotations

import ast
import hashlib
import re
from dataclasses import dataclass

# The pin scope a probe-log row carries (`pin_scope` field). Rows written before U-SR-09 carry
# no field and are read as FILE -- the legacy whole-file theorem stays live for them, so the
# landing of block scope never mass-stales the 1,300-row log. [LAW:types-are-the-program]
PIN_SCOPE_FILE = "file"
PIN_SCOPE_BLOCK = "block"
# How a block-scoped row binds its test (`test_scope` field).
TEST_SCOPE_BODY = "body"  # `test_body_sha` = the named test function's source segment
TEST_SCOPE_ARTIFACT = "artifact"  # `test_sha` = the whole test file / shell script


def digest16(data: bytes) -> str:
    """The 16-hex-char sha256 prefix every probe-log digest uses (`target_sha`, `test_sha`,
    `block_sha`, `test_body_sha`) -- the one place the digest format lives."""
    return hashlib.sha256(data).hexdigest()[:16]


def parse_line_range(spec: str) -> tuple[int, int]:
    """`"12-20"` or `"12"` → (12, 20) / (12, 12), 1-indexed inclusive. Raises ValueError."""
    text = spec.strip()
    m = re.fullmatch(r"(\d+)(?:\s*-\s*(\d+))?", text)
    if not m:
        raise ValueError(f"--lines must be A or A-B with 1 <= A <= B (got {spec!r})")
    a = int(m.group(1))
    b = int(m.group(2)) if m.group(2) else a
    if a < 1 or b < a:
        raise ValueError(f"--lines must be A or A-B with 1 <= A <= B (got {spec!r})")
    return a, b


def block_digest(text: str, start: int, end: int) -> str:
    """Digest of lines `start..end` (1-indexed, inclusive) exactly as the probe commented them
    out -- line endings included, so CRLF↔LF drift is a real change. Raises ValueError when
    the range is outside the file (the same refusal `comment_out` makes)."""
    lines = text.splitlines(keepends=True)
    if start < 1 or end > len(lines):
        raise ValueError(f"--lines {start}-{end} is outside {len(lines)}-line file")
    return digest16("".join(lines[start - 1 : end]).encode())


def block_is_present(text: str, n_lines: int, digest: str) -> bool:
    """True when SOME contiguous window of `n_lines` lines in `text` digests to `digest` --
    the content anchor. Every window is hashed (files are small; a 3,000-line file is 3,000
    sha256 calls), and the FIRST hit answers: a block that appears twice is present."""
    lines = text.splitlines(keepends=True)
    if n_lines < 1 or n_lines > len(lines):
        return False
    return any(
        digest16("".join(lines[i : i + n_lines]).encode()) == digest
        for i in range(len(lines) - n_lines + 1)
    )


def node_tail(nodeid: str) -> str | None:
    """The test FUNCTION a pytest node id names: the last `::` component with any `[params]`
    stripped -- `tools/test_x.py::TestK::test_f[a-b]` → `test_f`. None for a bare file (no
    `::`), which selects every test in it."""
    if "::" not in nodeid:
        return None
    tail = nodeid.rsplit("::", 1)[1]
    return tail.split("[", 1)[0] or None


def test_body_digest(source: str, name: str) -> str | None:
    """Digest of the source segment of the ONE function `name` defines in `source` -- from its
    first decorator (or the `def` line) through `end_lineno`, line endings included. None when
    the source does not parse, defines no such function, or defines it more than once (two
    classes with a `test_f` each: which one ran is not knowable from the name, so the caller
    falls back to the whole artifact rather than pin the wrong body)."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    defs = [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef) and n.name == name
    ]
    if len(defs) != 1:
        return None
    node = defs[0]
    first = min([node.lineno, *(d.lineno for d in node.decorator_list)])
    lines = source.splitlines(keepends=True)
    return digest16("".join(lines[first - 1 : node.end_lineno]).encode())


@dataclass(frozen=True)
class BlockPin:
    """A block-scoped pin PARSED out of a probe-log row -- the stamp `lanes_verify` carries
    inland: once constructed, every field is present and well-formed, so liveness is a pure
    comparison and no consumer re-checks the row. [LAW:parse-dont-validate]"""

    block_sha: str
    n_lines: int
    test_scope: str  # TEST_SCOPE_BODY | TEST_SCOPE_ARTIFACT
    test_digest: str  # `test_body_sha` under BODY, `test_sha` under ARTIFACT
    test_node: str | None  # the function BODY binds (None under ARTIFACT)

    @classmethod
    def from_row(cls, row: dict, nodeid: str) -> BlockPin | None:
        """None when the row is not a well-formed block pin: no/garbled `lines`, a missing
        digest, an unknown `test_scope`, or a BODY scope whose node id names no function --
        such a row is never live (the same disposition a digest-less legacy row gets)."""
        try:
            start, end = parse_line_range(str(row.get("lines") or ""))
        except ValueError:
            return None
        block_sha = row.get("block_sha")
        scope = row.get("test_scope")
        node = node_tail(nodeid) if scope == TEST_SCOPE_BODY else None
        by_scope = {
            TEST_SCOPE_BODY: row.get("test_body_sha"),
            TEST_SCOPE_ARTIFACT: row.get("test_sha"),
        }
        digest = by_scope.get(str(scope))
        if not block_sha or not digest or (scope == TEST_SCOPE_BODY and node is None):
            return None
        return cls(str(block_sha), end - start + 1, str(scope), str(digest), node)

    def live(self, src_text: str, test_data: bytes) -> bool:
        """The scoped theorem, evaluated against the CURRENT bytes: the block still occurs
        verbatim in `src_text`, and the test binding (body or whole artifact) still digests
        to what the probe measured."""
        if not block_is_present(src_text, self.n_lines, self.block_sha):
            return False
        if self.test_scope == TEST_SCOPE_BODY:
            try:
                body = test_body_digest(test_data.decode("utf-8"), self.test_node or "")
            except UnicodeDecodeError:
                return False
            return body == self.test_digest
        return digest16(test_data) == self.test_digest
