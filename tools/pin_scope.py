"""The mutation pin's binding theorem (U-SR-09 b1, plan §8 R2; [B] F7/c1).

A PINNED probe verdict says "commenting out THESE source lines made THIS test go red". The
pre-U-SR-09 pin bound that verdict to the digest of the whole source file and the whole test
file, so an edit ANYWHERE in either file -- a docstring, an unrelated function, a new assert in
another test -- staled every pin in the pair and forced a re-pin (12 of 13 pin commits on the
U-HE-35 arc, 1.07M IET). This module owns the scoped theorem the pin now carries instead:

    block  -- the probed lines' bytes still occur verbatim, contiguously, EXACTLY ONCE in the
              file (content-anchored: an insertion ABOVE the block shifts its line numbers but
              not its bytes, so the pin stays live and `lines` becomes provenance-at-probe-time,
              not a live locator; a block that occurs twice is never live -- deleting the
              probed copy would leave the other to vouch for it, codex u-sr-09 r1);
    test   -- the judging test's SLICE -- the test file with every OTHER top-level `test_*`
              function removed, so imports, fixtures, constants, helpers and marks stay bound
              (a swapped import or a module-wide skip hollows the test; only sibling-test
              churn, the [B] F7 cost, is excluded) -- is unchanged when the probe command names
              one node id; the whole artifact otherwise (`-k` selectors can match several
              tests, a shell suite has no `def`).

What the weaker theorem gives up, stated once so no reader re-derives it: an edit OUTSIDE the
block that makes the block dead code is not caught -- the merge-gate witness lens re-probes
contested changes, and charter §4 names whole-file scope as the one defect. The producer
(`mutation_probe.log_result`) writes the digests; the consumer (`lanes_verify._pin_is_live`)
re-derives them at HEAD. Both import from here so the format has ONE home.
[LAW:one-source-of-truth]

Pure: text in, digests out. No I/O, no clock, no repo. [LAW:effects-at-boundaries]
"""

from __future__ import annotations

import ast
import builtins
import hashlib
import re
from dataclasses import dataclass

# The pin scope a probe-log row carries (`pin_scope` field). Rows written before U-SR-09 carry
# no field and are read as FILE -- the legacy whole-file theorem stays live for them, so the
# landing of block scope never mass-stales the 1,300-row log. [LAW:types-are-the-program]
PIN_SCOPE_FILE = "file"
PIN_SCOPE_BLOCK = "block"
# How a block-scoped row binds its test (`test_scope` field).
TEST_SCOPE_SLICE = "slice"  # `test_slice_sha` = the test file minus its OTHER top-level tests
TEST_SCOPE_ARTIFACT = "artifact"  # `test_sha` = the whole test file / shell script


def digest16(data: bytes) -> str:
    """The 16-hex-char sha256 prefix every probe-log digest uses (`target_sha`, `test_sha`,
    `block_sha`, `test_slice_sha`) -- the one place the digest format lives."""
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


def block_occurrences(text: str, n_lines: int, digest: str) -> int:
    """How many contiguous windows of `n_lines` lines in `text` digest to `digest` -- the
    content anchor. Every window is hashed (files are small; a 3,000-line file is 3,000
    sha256 calls)."""
    lines = text.splitlines(keepends=True)
    if n_lines < 1 or n_lines > len(lines):
        return 0
    return sum(
        digest16("".join(lines[i : i + n_lines]).encode()) == digest
        for i in range(len(lines) - n_lines + 1)
    )


def block_is_present(text: str, n_lines: int, digest: str) -> bool:
    """The block occurs EXACTLY ONCE: present, and unambiguous (codex u-sr-09 r1 P2 -- a
    duplicated one-liner would let the other copy vouch for a deleted probed copy). A probe
    of a non-unique block is warned about at probe time (`mutation_probe`) and never live."""
    return block_occurrences(text, n_lines, digest) == 1


def pytest_targets(toks: list[str]) -> list[str]:
    """Every collection target of a split pytest command: an operand is a target unless it
    is the value of a value-taking option (`PYTEST_VALUE_OPTIONS`); `a.py::test_x b.py` and
    `a.py::test_x tests` both have two. The ONE parser both the producer (`mutation_probe`)
    and the consumer (`lanes_verify`) use (codex u-sr-09 r7: the consumer's own `.py` scan
    picked `--ignore`'s value)."""
    targets: list[str] = []
    args = toks[toks.index("pytest") + 1 :]
    i = 0
    while i < len(args):
        tok = args[i]
        if tok in PYTEST_VALUE_OPTIONS:
            i += 2
            continue
        if not tok.startswith("-"):
            targets.append(tok)
        i += 1
    return targets


#: pytest options that consume the NEXT token (the `--opt=value` spelling needs no entry:
#: it starts with `-` and carries its value). Anything else after `pytest` that does not
#: start with `-` is a collection target.
PYTEST_VALUE_OPTIONS = frozenset(
    {
        "-k", "-m", "-p", "-o", "-W", "-c", "-n", "--basetemp", "--rootdir", "--deselect",
        "--ignore", "--tb", "--durations", "--confcutdir", "--import-mode", "--maxfail",
    }
)  # fmt: skip


def node_tail(nodeid: str) -> str | None:
    """The test FUNCTION a pytest node id names: the last `::` component with any `[params]`
    stripped -- `tools/test_x.py::TestK::test_f[a-b]` → `test_f`. None for a bare file (no
    `::`), which selects every test in it."""
    if "::" not in nodeid:
        return None
    tail = nodeid.rsplit("::", 1)[1]
    return tail.split("[", 1)[0] or None


def _span(node: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[int, int]:
    """1-indexed inclusive line span of a function INCLUDING its decorators."""
    first = min([node.lineno, *(d.lineno for d in node.decorator_list)])
    return first, node.end_lineno or node.lineno


def test_slice_digest(source: str, name: str) -> str | None:
    """Digest of `source` with every top-level `test_*` function OTHER than `name` removed
    (decorators included) -- the slice of the test file that can change the named test's
    verdict: its own body, the imports, fixtures, helpers, constants and module-level marks
    (codex u-sr-09 r1 P2: a body-only digest let a swapped import or a module-wide skip hollow
    the test while its pin stayed live). Only sibling top-level tests -- the [B] F7 churn --
    are excluded, and a sibling the kept slice REFERENCES by name (a `test_helper()` the
    selected test calls; transitively, to a fixpoint) is kept too (codex r2 P2: hollowing
    the helper hollowed the judge), as is any sibling whose DEFINITION runs code at import --
    a decorator other than a plain `pytest.mark.<x>` (which covers every pytest fixture,
    aliased or not: an autouse `test_setup` is harness, codex r3/r4) or a default that
    calls something (codex r6). A test method inside a class keeps its class whole. None
    when the source does not parse, defines no function `name`, or defines it more than once
    (which one ran is not knowable from the name, so the caller falls back to the whole
    artifact)."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    named = [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef) and n.name == name
    ]
    if len(named) != 1:
        return None
    pytest_names = _pytest_names(tree)
    bound = _module_bound_names(tree)
    siblings = {
        n.name: n
        for n in tree.body
        if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)
        and n.name.startswith("test_")
        and n is not named[0]
        and not _runs_at_import(n, pytest_names, bound)
    }
    # a sibling referenced from the kept nodes stays; iterate until no new name is pulled in
    kept_nodes = [n for n in tree.body if n not in siblings.values()]
    referenced = _names_used(kept_nodes)
    while True:
        pulled = [n for name, n in siblings.items() if name in referenced and n not in kept_nodes]
        if not pulled:
            break
        kept_nodes.extend(pulled)
        referenced |= _names_used(pulled)
    # The slice is the kept nodes' OWN source segments, concatenated in file order -- never the
    # file minus the dropped lines: that kept the blank lines around a dropped sibling, so
    # INSERTING a sibling test anywhere re-staled every pin in the file (found on the arc's own
    # witness file at u-sr-09 r4), which is exactly the churn the slice exists to remove.
    lines = source.splitlines(keepends=True)
    kept = "".join("".join(lines[a - 1 : b]) for a, b in sorted(_node_span(n) for n in kept_nodes))
    return digest16(kept.encode())


def _node_span(node: ast.AST) -> tuple[int, int]:
    """1-indexed inclusive line span of any top-level node (decorators included)."""
    if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
        return _span(node)
    decorators = getattr(node, "decorator_list", [])
    first = min([node.lineno, *(d.lineno for d in decorators)])
    return first, node.end_lineno or node.lineno


_LITERAL_CONTAINERS = (ast.Tuple, ast.List, ast.Set)


def _is_literal(node: ast.AST, bound: frozenset[str]) -> bool:
    """An expression that is INERT at import: a constant; a unary op on one; a tuple/list/
    set/dict of those; or a name (or attribute chain) whose root the module already BINDS
    (an import, assignment, def or class -- all kept in every slice) or a builtin. An
    UNBOUND name is not inert: `def test_side(x=EXISTING)` → `x=MISSING` raises at
    collection (codex u-sr-09 r10), so a sibling reading one is a dependency and is kept.
    A bound name (`repo: Path`, `int`) adds nothing the slice does not already digest, so
    a sibling annotated with one stays droppable -- the [B] F7 churn must not come back."""
    if isinstance(node, ast.Constant):
        return True
    if isinstance(node, ast.Name):
        return node.id in bound
    if isinstance(node, ast.Attribute):
        root = node
        while isinstance(root, ast.Attribute):
            root = root.value
        return isinstance(root, ast.Name) and root.id in bound
    if isinstance(node, ast.UnaryOp):
        return _is_literal(node.operand, bound)
    if isinstance(node, _LITERAL_CONTAINERS):
        return all(_is_literal(e, bound) for e in node.elts)
    if isinstance(node, ast.Dict):
        return all(
            k is not None and _is_literal(k, bound) and _is_literal(v, bound)
            for k, v in zip(node.keys, node.values, strict=True)
        )
    return False


def _module_bound_names(tree: ast.Module) -> frozenset[str]:
    """Every name the module binds at top level -- imports, assignment targets, defs and
    classes -- plus the builtins: the names an inert definition-time expression may read."""
    names: set[str] = set(dir(builtins))
    for n in tree.body:
        if isinstance(n, ast.Import | ast.ImportFrom):
            names.update((a.asname or a.name).split(".")[0] for a in n.names)
        elif isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            names.add(n.name)
        elif isinstance(n, ast.Assign | ast.AnnAssign | ast.AugAssign):
            targets = n.targets if isinstance(n, ast.Assign) else [n.target]
            for t in targets:
                names.update(sub.id for sub in ast.walk(t) if isinstance(sub, ast.Name))
    return frozenset(names)


def _pytest_names(tree: ast.Module) -> set[str]:
    """Every local name bound to the pytest module (`import pytest`, `import pytest as pt`)
    -- the only roots under which `<root>.mark.<x>` is an inert pytest mark (codex u-sr-09
    r10: `custom.mark.register("A")` had passed for one)."""
    names: set[str] = set()
    for n in tree.body:
        if isinstance(n, ast.Import):
            for alias in n.names:
                if alias.name == "pytest":
                    names.add(alias.asname or alias.name)
    return names


def _runs_at_import(
    node: ast.FunctionDef | ast.AsyncFunctionDef, pytest_names: set[str], bound: frozenset[str]
) -> bool:
    """A sibling whose DEFINITION executes code beyond pytest's own marks -- a decorator
    that is not a plain `pytest.mark.<x>` (or `pytest.mark.<x>(...)` whose arguments call
    nothing), or a parameter default that calls something -- runs at import/collection even
    when only the selected test is collected, so it can change that test's verdict and is
    never a removable sibling (codex u-sr-09 r6: `@register(1)` on a sibling; this rule
    subsumes the r3/r4 fixture-decorator rule -- a mutation probe found that rule dead)."""
    for d in node.decorator_list:
        target = d.func if isinstance(d, ast.Call) else d
        is_mark = (
            isinstance(target, ast.Attribute)
            and isinstance(target.value, ast.Attribute)
            and target.value.attr == "mark"
            and isinstance(target.value.value, ast.Name)
            and target.value.value.id in pytest_names
        )
        if not is_mark:
            return True
        # a mark's arguments may only be literals (constants, containers of literals, bare
        # names/attributes): a call, a walrus, a lambda or a comprehension there executes
        # at import (codex u-sr-09 r6 `make()`, r7 `(state := 1)`)
        if isinstance(d, ast.Call) and not all(
            _is_literal(a, bound) for a in [*d.args, *(k.value for k in d.keywords)]
        ):
            return True
    # defaults AND annotations are evaluated when the module imports (no
    # `from __future__ import annotations` is assumed): a call in either runs code
    # (codex u-sr-09 r8: `def test_side(x: mark(1))`)
    params = [
        *node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs,
        *([node.args.vararg] if node.args.vararg else []),
        *([node.args.kwarg] if node.args.kwarg else []),
    ]  # fmt: skip
    evaluated = [
        *node.args.defaults, *node.args.kw_defaults, *(a.annotation for a in params), node.returns
    ]  # fmt: skip
    return any(e is not None and not _is_literal(e, bound) for e in evaluated)


def _names_used(nodes: list[ast.AST]) -> set[str]:
    """Every identifier read, attribute name, or STRING CONSTANT mentioned under `nodes` --
    a string is how a dynamic lookup names its target (`globals()["test_helper"]()`,
    `getattr(m, "test_helper")`, codex u-sr-09 r9), so a sibling whose name appears as a
    string is referenced too."""
    out: set[str] = set()
    for node in nodes:
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name):
                out.add(sub.id)
            elif isinstance(sub, ast.Attribute):
                out.add(sub.attr)
            elif isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                out.add(sub.value)
    return out


@dataclass(frozen=True)
class BlockPin:
    """A block-scoped pin PARSED out of a probe-log row -- the stamp `lanes_verify` carries
    inland: once constructed, every field is present and well-formed, so liveness is a pure
    comparison and no consumer re-checks the row. [LAW:parse-dont-validate]"""

    block_sha: str
    n_lines: int
    test_scope: str  # TEST_SCOPE_SLICE | TEST_SCOPE_ARTIFACT
    test_digest: str  # `test_slice_sha` under SLICE, `test_sha` under ARTIFACT
    test_node: str | None  # the function the SLICE is cut for (None under ARTIFACT)

    @classmethod
    def from_row(cls, row: dict, nodeid: str) -> BlockPin | None:
        """None when the row is not a well-formed block pin: no/garbled `lines`, a missing
        digest, an unknown `test_scope`, or a SLICE scope whose node id names no function --
        such a row is never live (the same disposition a digest-less legacy row gets)."""
        try:
            start, end = parse_line_range(str(row.get("lines") or ""))
        except ValueError:
            return None
        block_sha = row.get("block_sha")
        scope = row.get("test_scope")
        node = node_tail(nodeid) if scope == TEST_SCOPE_SLICE else None
        by_scope = {
            TEST_SCOPE_SLICE: row.get("test_slice_sha"),
            TEST_SCOPE_ARTIFACT: row.get("test_sha"),
        }
        digest = by_scope.get(str(scope))
        if not block_sha or not digest or (scope == TEST_SCOPE_SLICE and node is None):
            return None
        return cls(str(block_sha), end - start + 1, str(scope), str(digest), node)

    def live(self, src_text: str, test_data: bytes) -> bool:
        """The scoped theorem, evaluated against the CURRENT bytes: the block still occurs
        verbatim, exactly once, in `src_text`, and the test binding (slice or whole artifact)
        still digests to what the probe measured."""
        if not block_is_present(src_text, self.n_lines, self.block_sha):
            return False
        if self.test_scope == TEST_SCOPE_SLICE:
            try:
                digest = test_slice_digest(test_data.decode("utf-8"), self.test_node or "")
            except UnicodeDecodeError:
                return False
            return digest == self.test_digest
        return digest16(test_data) == self.test_digest
