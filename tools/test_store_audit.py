"""C-HE-30: one authority per fact; every store the coordination modules touch is listed.

Static phase0 witness (U-HE-14). The audit one-pager at
`.harness/spec/store-audit-he-loop-lanes.md` must (a) exist, (b) carry exactly the eight
stores of the C-HE-30 table -- one row each, each authority cell naming the spec's fact for
that store and no fact owned twice -- plus the derived / new-fact families named in the
clearance-fold note, with ONE `| Authority for |` table, and (c) name every `QUEUE_DIR` /
`.harness` path literal the four coordination modules spell, as a path segment inside a
code span -- so a runtime path that creates a store the audit does not list turns this row
red (C-HE-30 Invariant 2).

The literal extractor covers the idioms the modules actually use: textual
`.harness/<name>`; pathlib chains `".harness" / "<name>"`; ANY `<ident> / "<name>"` or
`<ident> / f"<name>"` join (`QUEUE_DIR`, and alias roots such as `DOOR` / `RES` in the S4
modules; placeholders normalise to `*`); `<any>.glob("<pat>")`; `.with_suffix("<ext>")`;
`.tmp` stagers; and, for shell, `$(...)/<name>"` / `$var/<name>"` constructions. The plan's
bare-string regex saw zero literals in `tools/arc_metrics.py` (pathlib throughout) and
would have passed vacuously.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AUDIT = REPO / ".harness" / "spec" / "store-audit-he-loop-lanes.md"
#: Modules on main today -- MUST exist; a rename or deletion fails the row rather than
#: silently dropping its literals from coverage.
LANDED = [
    "tools/arc_metrics.py",
    "tools/hooks/loop_lib.sh",
]
#: S4 modules -- skipped until they land; U-HE-17 / U-HE-22 MUST move theirs into LANDED.
PENDING = [
    "tools/merge_door.py",
    "tools/reservations.py",
]
#: (first-cell name, phrase the spec's "Authority for" cell carries) -- C-HE-30 table order.
EIGHT: list[tuple[str, str]] = [
    ("Queue entries", "not yet in committed history"),
    ("Reservation files", "arc landing state"),
    ("Merge-door lease", "who is landing now"),
    ("arc-metrics.jsonl", "arc rows"),
    ("merge-gate-log", "gate verdicts"),
    ("loop_status.md", "operator-attention state"),
    ("Finding emission", "derived from the 8-field record"),
    ("Committed history on", "the only proof that a row is durable"),
]
DERIVED = [
    "reservations/<arc_id>/<gen>.json",
    "transition.<lease_token>",
    "released.",
    "reclaimed.",
    "lanes/<k>",
    "tier-clean-cycles",
    "hil-deliveries",
    "mechanized-checks-state.json",
    "mutation-probe-log.jsonl",
    "merge-gate-log.jsonl",
]
#: Transient writer-exclusion / staging artifacts -- MUST be listed as non-stores.
NON_STORES = [
    ".ledger-claim-",
    "merge-gate-log.jsonl.emit.lock",
    ".harness/tmp/",
]

_PLACEHOLDER = re.compile(r"\{[^}]*\}")
_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # textual `.harness/<name>` (shell + docstrings + frozensets)
    (re.compile(r"\.harness/[A-Za-z0-9_.\-]+"), "text"),
    # pathlib chain `".harness" / "<name>"`
    (re.compile(r'"\.harness"\s*/\s*"([^"]+)"'), "harness_seg"),
    # ANY identifier joined with a literal -- `QUEUE_DIR / "<name>"`, `QUEUE_DIR / f"<name>"`,
    # and alias roots such as `DOOR / "attempts"`, `RES / f"{gen}.json"` (the S4 modules)
    (re.compile(r'\b([A-Za-z_]\w*)\s*/\s*f?"([^"]+)"'), "join"),
    # `<any>.glob("<pat>")`
    (re.compile(r'\b\w+\.glob\("([^"]+)"\)'), "glob"),
    # `.with_suffix("<ext>")`
    (re.compile(r'\.with_suffix\("([^"]+)"\)'), "suffix"),
    # `.tmp` stagers (`with_name(f".{name}.{pid}.tmp")`)
    (re.compile(r'f?"[^"]*\.tmp"'), "tmp"),
    # shell: `$(dirname "$p")/.loop-status.lock"` / `$d/<name>"` (one segment before the quote)
    (re.compile(r'(?:\)|\$\{?\w+\}?)/([A-Za-z0-9_.\-]+)"'), "shell"),
]
#: Python-only idioms; a shell module spells its paths textually or via the `shell` form, and
#: `case` patterns like `"refs/heads/"*)` would otherwise read as joins.
_PY_ONLY = frozenset({"join", "glob", "suffix", "tmp"})
_SH_ONLY = frozenset({"shell"})
_HAS_WORD = re.compile(r"[A-Za-z0-9]")


def _token(kind: str, match: re.Match[str]) -> str | None:
    """The audit-page token a literal must appear as, or None when the literal carries no
    store name of its own (a pure-placeholder join such as `f"{prefix}.{token}"`)."""
    if kind == "join":
        root, raw = match.group(1), match.group(2)
    else:
        root = ""
        raw = match.group(1) if match.re.groups else match.group(0)
    raw = _PLACEHOLDER.sub("*", raw.strip('"'))
    if kind == "text":
        return raw
    if kind == "harness_seg":
        return f".harness/{raw}"
    if kind == "suffix":
        return f"*{raw}"
    if kind == "tmp" or raw.endswith(".tmp"):
        return ".tmp"
    if kind == "join":
        if raw == ".harness":
            return None  # the `".harness" / "<name>"` chain pattern carries this one
        if not _HAS_WORD.search(raw):
            return None
        return f"QUEUE_DIR/{raw}" if root == "QUEUE_DIR" else raw
    return raw


def store_literals(path: Path) -> set[str]:
    text = path.read_text()
    is_py = path.suffix == ".py"
    out: set[str] = set()
    for pat, kind in _PATTERNS:
        if (kind in _PY_ONLY and not is_py) or (kind in _SH_ONLY and is_py):
            continue
        for m in pat.finditer(text):
            tok = _token(kind, m)
            if tok is not None:
                out.add(tok)
    return out


_AUDIT_PLACEHOLDER = re.compile(r"<[^>]+>")
_CODE_SPAN = re.compile(r"`([^`]+)`")


def audit_spans(text: str) -> list[str]:
    """Every code span of the page with `<token>` / `<gen>` placeholders normalised to `*`
    (a literal carries `{token}`, which the extractor also normalises to `*`)."""
    return [_AUDIT_PLACEHOLDER.sub("*", s) for s in _CODE_SPAN.findall(text)]


def listed(token: str, spans: list[str]) -> bool:
    """A token is listed iff some code span IS it, ends with `/<token>`, has it as a whole
    `/`-segment, or -- for a bare-extension token (`.tmp`) -- has a segment ending in it. A
    glob (`*.json`) must match a glob segment; a bare substring anywhere (`state` inside
    `mechanized-checks-state.json`) is NOT a listing."""
    ext = token if token.startswith(".") and "/" not in token else None
    for span in spans:
        if span == token or span.endswith("/" + token):
            return True
        for seg in span.split("/"):
            if seg == token or (ext is not None and seg.endswith(ext)):
                return True
    return False


def _eight_store_rows(text: str) -> list[list[str]]:
    """Body rows of the `## The eight stores` table as cell lists (header + rule dropped)."""
    section = text.split("## The eight stores", 1)[1].split("\n## ", 1)[0]
    rows = [ln for ln in section.splitlines() if ln.startswith("|")]
    body = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in rows[2:]]
    assert rows[0].split("|")[1:4] == [" Store ", " Venue ", " Authority for "], rows[0]
    return body


def test_audit_exists_and_lists_eight_plus_derived() -> None:
    text = AUDIT.read_text()
    for name in [n for n, _ in EIGHT] + DERIVED + NON_STORES:
        assert name in text, name
    # hand-witness (not probe-expressible: the doc is not comment-out mutable): a second
    # `| Authority for |` table anywhere in the page fails this count
    assert text.count("| Authority for |") == 1
    # the probe log is a run log -- DERIVED, never an authority
    assert "`.harness/mutation-probe-log.jsonl`" in text.split("## Derived families")[1]


def test_eight_store_table_one_row_per_store_one_fact_per_row() -> None:
    """Exactly eight rows; each names one spec store in its first cell; each authority cell
    carries that store's C-HE-30 fact; no fact phrase is owned by two rows (a loose substring
    elsewhere in the page -- `merge-gate-log` in the lock section -- does not count)."""
    rows = _eight_store_rows(AUDIT.read_text())
    assert len(rows) == 8, [r[0] for r in rows]
    for r in rows:
        assert len(r) == 3 and all(r), r
    for name, fact in EIGHT:
        hits = [r for r in rows if name in r[0]]
        assert len(hits) == 1, (name, len(hits))
        assert fact in hits[0][2], (name, fact, hits[0][2])
        owners = [r[0] for r in rows if fact in r[2]]
        assert owners == [hits[0][0]], (fact, owners)


def test_every_path_literal_in_modules_is_listed() -> None:
    spans = audit_spans(AUDIT.read_text())
    for m in LANDED:
        assert (REPO / m).exists(), f"{m}: landed module missing -- update LANDED, not silently"
    for m in LANDED + [p for p in PENDING if (REPO / p).exists()]:
        tokens = store_literals(REPO / m)
        # per module, never vacuous: a coordination module that spells NO store literal the
        # extractor recognises is an extractor gap, not a clean module
        assert tokens, f"{m}: extractor saw no store literals"
        for token in sorted(tokens):
            # hand-witness: removing any listed token from the audit page turns this red
            assert listed(token, spans), f"{m}: store literal {token!r} not in audit"


def test_extractor_sees_module_idioms() -> None:
    py = store_literals(REPO / "tools" / "arc_metrics.py")
    for expected in (
        ".harness/arc-metrics.jsonl",
        "QUEUE_DIR/*.json",
        "*.taken",
        "QUEUE_DIR/.ledger-claim-*",
        ".tmp",
    ):
        assert expected in py, (expected, sorted(py))
    sh = store_literals(REPO / "tools" / "hooks" / "loop_lib.sh")
    assert ".loop-status.lock" in sh, sorted(sh)  # the `$(dirname "$p")/...` construction


def test_listed_is_segment_bound_not_substring() -> None:
    spans = [
        "QUEUE_DIR/merge-door/attempts/*/*",
        ".harness/mechanized-checks-state.json",
        ".*.*.tmp",
        "QUEUE_DIR/*.taken",
    ]
    assert listed("attempts", spans)
    assert listed(".tmp", spans)
    assert listed("*.taken", spans)
    assert listed(".harness/mechanized-checks-state.json", spans)
    assert not listed("*.json", spans)  # a glob needs a glob segment, not any `.json` file
    assert not listed("state", spans)
    assert not listed("merge-door/state", spans)
