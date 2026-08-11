#!/usr/bin/env python3
"""Clearance-marker YAML frontmatter: fail-closed parse gate + quote-only repairer.

R-CTX-1 / U-CTX-10.

`.harness/clearance/*.md` markers carry YAML frontmatter (`.harness/clearance/README.md`,
`TEMPLATE.md`). At the time this tool was authored 71 of 288 markers FAILED `yaml.safe_load`
on their frontmatter block — plain scalars carrying `: ` (colon-space) inside prose, which
YAML reads as a nested mapping key. A whitespace-preceded `#` is the sibling hazard: it
parses, but silently truncates the value at the `#` (`PR #529` -> `PR`).

Two surfaces:

* ``--check``  — the CI gate. Enumerates EVERY `.harness/clearance/*.md`, subtracts only the
  files explicitly enumerated in `.harness/clearance/parse-manifest.md`, and requires every
  remaining file to (a) have a frontmatter block that parses to a mapping carrying
  `artifact` + `version`, and (b) carry no LOSSY scalar — one whose stored text is not what
  YAML reads back. **Fail-closed**: a file that is neither parseable nor manifest-listed is
  an ERROR, never a skip. A manifest-listed file that HAS become a valid marker is also an
  error (stale exemption).

* ``--fix``   — the quote-only repairer. Rewrites ONLY scalars that are broken (unparseable)
  or lossy (the YAML round-trip does not return the source text byte-for-byte). The repair
  is pure quoting: the emitted value is the source text, double-quoted. No content is
  reworded, reordered, added, or dropped, and any scalar already carrying an explicit YAML
  style (quoted / folded / literal) is left byte-identical.

Deliberately stdlib + PyYAML only (PyYAML arrives via harness-runtime, as for
`tools/substitution_ledger.py`).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CLEARANCE_DIR = REPO_ROOT / ".harness" / "clearance"
MANIFEST_PATH = CLEARANCE_DIR / "parse-manifest.md"

FRONTMATTER_OPEN = "---\n"
FRONTMATTER_CLOSE = "\n---\n"

REQUIRED_KEYS = ("artifact", "version")

_KEY_INLINE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*): (.+)$")
_KEY_BLOCK = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):[ \t]*$")
_ITEM_INLINE = re.compile(r"^([ \t]+)- (.+)$")
_ITEM_BLOCK = re.compile(r"^([ \t]+)-[ \t]*$")
_CONTINUATION = re.compile(r"^[ \t]+\S")

# `| `README.md` | class | reason |` rows in the manifest table.
_MANIFEST_ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*([^|]+?)\s*\|\s*(.+?)\s*\|\s*$")


class ClearanceFrontmatterError(Exception):
    """A marker's frontmatter could not be read as a clearance-marker mapping."""


@dataclass(frozen=True)
class Marker:
    """A parsed clearance marker."""

    path: Path
    data: dict[str, Any]

    @property
    def artifact(self) -> str:
        return str(self.data["artifact"])

    @property
    def version(self) -> str:
        return str(self.data["version"])


def iter_marker_paths(directory: Path = CLEARANCE_DIR) -> list[Path]:
    """Every `*.md` under the clearance directory, sorted. No filtering happens here."""
    return sorted(directory.glob("*.md"))


def split_frontmatter(text: str) -> str | None:
    """Return the raw frontmatter block (trailing newline included), or None if absent.

    The block is delimited by a leading `---\\n` and the FIRST subsequent `\\n---\\n`.
    """
    if not text.startswith(FRONTMATTER_OPEN):
        return None
    end = text.find(FRONTMATTER_CLOSE, len(FRONTMATTER_OPEN))
    if end == -1:
        return None
    return text[len(FRONTMATTER_OPEN) : end + 1]


def parse_marker(path: Path) -> Marker:
    """Parse one marker. Raises ClearanceFrontmatterError — never returns a partial read."""
    text = path.read_text(encoding="utf-8")
    block = split_frontmatter(text)
    if block is None:
        raise ClearanceFrontmatterError(f"{path.name}: no YAML frontmatter block")
    try:
        data = yaml.safe_load(block)
    except yaml.YAMLError as exc:  # pragma: no cover - message shape only
        first = str(exc).splitlines()[0] if str(exc) else exc.__class__.__name__
        raise ClearanceFrontmatterError(
            f"{path.name}: frontmatter does not parse ({first})"
        ) from exc
    if not isinstance(data, dict):
        raise ClearanceFrontmatterError(f"{path.name}: frontmatter is not a mapping")
    for key in REQUIRED_KEYS:
        value = data.get(key)
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ClearanceFrontmatterError(f"{path.name}: frontmatter is missing `{key}`")
    return Marker(path=path, data=data)


# ── manifest ────────────────────────────────────────────────────────────────────────────


def load_manifest(path: Path = MANIFEST_PATH) -> dict[str, tuple[str, str]]:
    """Read the exemption manifest: `{filename: (class, reason)}`.

    A missing manifest is an EMPTY exemption set, not a permissive one — every marker must
    then parse.
    """
    if not path.exists():
        return {}
    entries: dict[str, tuple[str, str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _MANIFEST_ROW.match(line)
        if not match:
            continue
        name, klass, reason = match.group(1), match.group(2), match.group(3)
        if klass.strip("- ") == "" or set(klass) <= {"-", " "}:
            continue  # the table's `|---|---|---|` separator row
        entries[name] = (klass, reason)
    return entries


# ── quote-only repair ───────────────────────────────────────────────────────────────────


def _double_quote(value: str) -> str:
    """A YAML double-quoted scalar carrying `value` exactly.

    JSON string escaping is a subset of YAML's double-quoted escaping (`\\"`, `\\\\`,
    `\\n`, `\\t`, `\\uXXXX`), so `json.dumps` output is a valid YAML double-quoted scalar.
    """
    return json.dumps(value, ensure_ascii=False)


def _scalar_is_clean(source_lines: list[str]) -> bool:
    """True when YAML reads `source_lines` back as exactly the text they carry.

    `source_lines[0]` is the inline value; the rest are its plain-scalar continuation lines
    (already stripped). Only an unquoted (PLAIN) scalar can carry the `: ` and `#` hazards,
    so anything already written with an explicit YAML style — quoted, folded, literal — is
    clean by construction. A multi-line value is never clean: it is collapsed to one quoted
    line so the stored text is unambiguous.
    """
    raw = source_lines[0]
    # Block scalars (codex round-1 on PR-4): an inline value that is exactly a
    # literal/folded header (`|`, `|-`, `>-`, optionally with an indentation
    # indicator) carries an EXPLICIT YAML style whose body is the indented
    # continuation below — the `: `/`#` hazards cannot apply, and collapsing it
    # to a quoted string CORRUPTS the value (the style token becomes content).
    # Preserve byte-identically.
    if re.fullmatch(r"[|>][+-]?[0-9]?", raw.strip()):
        return True
    if len(source_lines) != 1:
        return False
    try:
        node = yaml.compose("x: " + raw)
    except yaml.YAMLError:
        return False
    if not isinstance(node, yaml.MappingNode) or len(node.value) != 1:
        return False
    value_node = node.value[0][1]
    if not isinstance(value_node, yaml.ScalarNode):
        # A flow collection or anchor shape this repairer does not model. Quoting it would
        # change its meaning, so leave it byte-identical; if it is broken, the gate says so.
        return True
    if value_node.style is not None:
        # Explicitly quoted / folded / literal — the hazards cannot apply.
        return True
    try:
        loaded = yaml.safe_load("x: " + raw)
    except yaml.YAMLError:
        return False
    if not isinstance(loaded, dict) or set(loaded) != {"x"}:
        return False
    value = loaded["x"]
    if isinstance(value, str):
        return value == raw
    # Non-string (timestamp / int / bool / null): the existing typed reading is intentional
    # and already parses — leave it byte-identical.
    return True


def repair_frontmatter(block: str) -> str:
    """Return `block` with every broken-or-lossy plain scalar re-emitted double-quoted.

    Structure (key order, list order, blank lines, indentation) is preserved exactly.
    Raises ClearanceFrontmatterError on a shape this repairer does not model, rather than
    guessing.
    """
    lines = block.split("\n")
    out: list[str] = []
    # The scalar currently being accumulated: (emit prefix, [value lines]).
    pending: tuple[str, list[str]] | None = None

    def flush() -> None:
        nonlocal pending
        if pending is None:
            return
        prefix, values = pending
        pending = None
        if _scalar_is_clean(values):
            out.append(prefix + values[0])
            return
        # YAML folds a plain multi-line scalar's newlines to single spaces; joining with a
        # space is therefore the value the source text denotes.
        out.append(prefix + _double_quote(" ".join(values)))

    for raw_line in lines:
        if raw_line == "":
            flush()
            out.append(raw_line)
            continue
        key_inline = _KEY_INLINE.match(raw_line)
        if key_inline:
            flush()
            pending = (f"{key_inline.group(1)}: ", [key_inline.group(2)])
            continue
        key_block = _KEY_BLOCK.match(raw_line)
        if key_block:
            flush()
            out.append(raw_line)
            continue
        item_inline = _ITEM_INLINE.match(raw_line)
        if item_inline:
            flush()
            pending = (f"{item_inline.group(1)}- ", [item_inline.group(2)])
            continue
        if _ITEM_BLOCK.match(raw_line):
            flush()
            out.append(raw_line)
            continue
        if _CONTINUATION.match(raw_line) and pending is not None:
            pending[1].append(raw_line.strip())
            continue
        raise ClearanceFrontmatterError(f"unmodelled frontmatter line: {raw_line[:80]!r}")

    flush()
    return "\n".join(out)


def repair_file(path: Path) -> bool:
    """Quote-repair one marker in place. Returns True when bytes changed.

    Verifies the repaired block parses before writing — a repair that does not parse is
    surfaced, never written.
    """
    text = path.read_text(encoding="utf-8")
    block = split_frontmatter(text)
    if block is None:
        raise ClearanceFrontmatterError(f"{path.name}: no YAML frontmatter block")
    repaired = repair_frontmatter(block)
    if repaired == block:
        return False
    try:
        parsed = yaml.safe_load(repaired)
    except yaml.YAMLError as exc:
        raise ClearanceFrontmatterError(
            f"{path.name}: repaired frontmatter still fails ({exc})"
        ) from exc
    if not isinstance(parsed, dict):
        raise ClearanceFrontmatterError(f"{path.name}: repaired frontmatter is not a mapping")
    path.write_text(
        FRONTMATTER_OPEN + repaired + text[len(FRONTMATTER_OPEN) + len(block) :],
        encoding="utf-8",
    )
    return True


# ── gate ────────────────────────────────────────────────────────────────────────────────


def check(directory: Path = CLEARANCE_DIR, manifest_path: Path = MANIFEST_PATH) -> list[str]:
    """Return the (possibly empty) list of violations. Fail-closed by construction."""
    violations: list[str] = []
    manifest = load_manifest(manifest_path)
    paths = iter_marker_paths(directory)
    names = {p.name for p in paths}

    for name in sorted(manifest):
        if name not in names:
            violations.append(
                f"{name}: listed in {manifest_path.name} but absent from {directory.name}/"
            )

    for path in paths:
        exempt = path.name in manifest
        try:
            parse_marker(path)
        except ClearanceFrontmatterError as exc:
            if not exempt:
                violations.append(str(exc))
            continue
        if exempt:
            violations.append(
                f"{path.name}: parses as a valid marker but is still listed in "
                f"{manifest_path.name} — remove the stale exemption row"
            )
            continue
        # Parsing is necessary but not sufficient: a whitespace-preceded `#` parses and then
        # silently DROPS everything after it. Require every stored scalar to denote exactly
        # the text it carries, so the truncation class cannot re-enter.
        block = split_frontmatter(path.read_text(encoding="utf-8"))
        if block is not None and repair_frontmatter(block) != block:
            violations.append(
                f"{path.name}: frontmatter parses but carries a lossy plain scalar "
                f"(a `: ` or whitespace-`#` value) — run "
                f"`uv run python tools/clearance_frontmatter.py --fix`"
            )
    return violations


def load_all_markers(
    directory: Path = CLEARANCE_DIR, manifest_path: Path = MANIFEST_PATH
) -> Iterator[Marker]:
    """Yield every non-exempt marker, parsed. Raises on the first unreadable one."""
    manifest = load_manifest(manifest_path)
    for path in iter_marker_paths(directory):
        if path.name in manifest:
            continue
        yield parse_marker(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--check", action="store_true", help="validate; exit 1 on any violation")
    parser.add_argument(
        "--fix", action="store_true", help="quote-repair broken/lossy scalars in place"
    )
    parser.add_argument("--dir", type=Path, default=CLEARANCE_DIR)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    args = parser.parse_args(argv)

    if args.fix:
        manifest = load_manifest(args.manifest)
        changed: list[str] = []
        for path in iter_marker_paths(args.dir):
            if path.name in manifest:
                continue
            if split_frontmatter(path.read_text(encoding="utf-8")) is None:
                continue
            if repair_file(path):
                changed.append(path.name)
        print(f"repaired {len(changed)} marker(s)")
        for name in changed:
            print(f"  {name}")

    if args.check or not args.fix:
        violations = check(args.dir, args.manifest)
        if violations:
            print(
                f"clearance frontmatter FAILED — {len(violations)} violation(s):", file=sys.stderr
            )
            for violation in violations:
                print(f"  {violation}", file=sys.stderr)
            return 1
        total = len(iter_marker_paths(args.dir))
        exempt = len(load_manifest(args.manifest))
        print(
            f"clearance frontmatter OK — {total - exempt}/{total} markers parse, "
            f"{exempt} manifest-exempt"
        )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
