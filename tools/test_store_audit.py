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
    "tools/lanes_verify.py",  # C-HE-31 §4d evaluator site; reads the probe log today
    "tools/merge_door.py",  # U-HE-22
    "tools/reservations.py",  # U-HE-17
]
#: Planned store creators -- skipped until they land; the landing unit (U-HE-17 / U-HE-22 /
#: U-HE-31 lane-init) MUST move its module into LANDED in the same change.
PENDING = [
    "tools/hooks/lane-init.sh",
    "tools/mechanized_checks/__init__.py",  # STATE_PATH home (U-HE-40)
    "tools/mechanized_checks/runner.py",
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
#: (Path-cell key, required Relation cell) for the derived / new-fact family table. A sole
#: carrier holds a coordination fact no other store records (C-HE-06 §6 marker payload,
#: exclusive-create registries, promotion state); a derived row is recomputable from a store
#: above. Reverting a sole carrier to "derived" is the misclassification this pins.
SOLE = "sole carrier (new fact)"
FAMILY_RELATION: list[tuple[str, str]] = [
    ("reservations/<arc_id>/<gen>.json", "part of store 2"),
    ("reservations/.seq/<n>", SOLE),
    ("reservations/.reconcile.log", SOLE),
    ("transition.<lease_token>", SOLE),
    ("LEASE.<token>.<suffix>", "part of store 3"),
    ("released.<token>", "part of store 3"),
    ("attempts/<lane_id>", SOLE),
    ("tier-clean-cycles", SOLE),
    ("lanes/<k>", SOLE),
    ("hil-deliveries", SOLE),
    (".loop-active", "part of store 6"),
    ("mechanized-checks-state.json", SOLE),
    (".ledger-claim-<key>", SOLE),
    ("mutation-probe-log.jsonl", SOLE),
    ("merge-gate-log.jsonl", "part of store 5"),
]
#: Required fact phrase in each sole carrier's fourth cell -- the fact itself, pinned, so a
#: reworded/nonsense cell cannot pass on quoting + uniqueness alone.
SOLE_FACTS: list[tuple[str, str]] = [
    ("reservations/.seq/<n>", "highest `seq`"),
    ("reservations/.reconcile.log", "what the last `reconcile_all` pass observed"),
    ("transition.<lease_token>", "who won the transition"),
    ("attempts/<lane_id>", "attempts"),
    ("tier-clean-cycles", "clean cycles"),
    ("lanes/<k>", "lane indices"),
    ("hil-deliveries", "CLAIMED this"),
    ("mechanized-checks-state.json", "live `kind`"),
    (".ledger-claim-<key>", "by whom"),
    ("mutation-probe-log.jsonl", "which probe RAN"),
]
_PART_OF = re.compile(r"^part of store [1-8]\b")
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
    # ANY identifier or call joined with one or more literals -- `QUEUE_DIR / "<name>"`,
    # `QUEUE_DIR / f"<name>"`, `QUEUE_DIR / "merge-door" / "x"`, `reservations_root() / ".seq"`,
    # single- or double-quoted, and alias roots such as `DOOR / "attempts"`, `RES / f"{gen}.json"`
    # (the S4 modules); the whole literal chain is the token, so a new child of a listed dir
    # is itself unlisted
    (
        re.compile(r'\b([A-Za-z_]\w*(?:\([^()]*\))?)((?:\s*/\s*f?(?:"[^"]+"|\'[^\']+\'))+)'),
        "join",
    ),
    # `<any>.glob("<pat>")`
    (re.compile(r'\b\w+\.glob\((?:"([^"]+)"|\'([^\']+)\')\)'), "glob"),
    # `.with_suffix("<ext>")`
    (re.compile(r'\.with_suffix\((?:"([^"]+)"|\'([^\']+)\')\)'), "suffix"),
    # `.tmp` stagers (`with_name(f".{name}.{pid}.tmp")`)
    (re.compile(r'f?(?:"[^"]*\.tmp"|\'[^\']*\.tmp\')'), "tmp"),
    # shell: `$(dirname "$p")/.loop-status.lock"`, `$d/<name>"`, `${VAR:-default}/<name>` -- one
    # segment after a `)`, `}` or `$var` root, ended by a quote, slash, space or `;`
    (re.compile(r'(?:\)|\}|\$\w+)/([A-Za-z0-9_.\-]+)(?=["\'/\s;)]|$)', re.M), "shell"),
    # shell: a name derived by APPENDING a suffix to a path variable -- `"${legacy}.migrating-…"`,
    # `"${p}.XXXXXXXX"`. The `shell` pattern above requires a `/` before the segment, so this
    # idiom was invisible to it and the witness passed VACUOUSLY over the three on-disk
    # artifact names U-HE-29 introduced (merge-gate spec lens, #1426). A witness that cannot
    # see an idiom reports "nothing unlisted" for exactly the same reason it would report a
    # clean sheet -- which is the failure this page's own rule exists to prevent.
    (re.compile(r"\$\{\w+\}(\.[A-Za-z0-9_\-]+)"), "shellsuffix"),
]
#: Python-only idioms; a shell module spells its paths textually or via the `shell` form, and
#: `case` patterns like `"refs/heads/"*)` would otherwise read as joins.
_PY_ONLY = frozenset({"join", "glob", "suffix", "tmp"})
_SH_ONLY = frozenset({"shell", "shellsuffix"})
_HAS_WORD = re.compile(r"[A-Za-z0-9]")
_QUOTED = re.compile(r'"([^"]+)"|\'([^\']+)\'')


def _token(kind: str, match: re.Match[str]) -> str | None:
    """The audit-page token a literal must appear as, or None when the literal carries no
    store name of its own (a pure-placeholder join such as `f"{prefix}.{token}"`)."""
    if kind == "join":
        root = match.group(1)
        raw = "/".join(a or b for a, b in _QUOTED.findall(match.group(2)))
    else:
        root = ""
        raw = next((g for g in match.groups() if g), None) or match.group(0)
    raw = _PLACEHOLDER.sub("*", raw.strip("\"'"))
    if kind == "text":
        return raw
    if kind == "harness_seg":
        return f".harness/{raw}"
    if kind == "suffix":
        return f"*{raw}"
    if kind == "shellsuffix":
        # `${legacy}.migrating-` -> `*.migrating-*`: the variable is the path, the captured
        # text is the appended name, and anything after it is per-invocation.
        return f"*{raw}*"
    if kind == "tmp" or raw.endswith(".tmp"):
        return ".tmp"
    if kind == "join":
        if raw == ".harness":
            return None  # the `".harness" / "<name>"` chain pattern carries this one
        if not _HAS_WORD.search(raw):
            # a fully-templated join still names a store SHAPE: `DOOR / f"{prefix}.{token}"`
            # -> `*.*` must be listed (the audit carries the shape span); only a bare `*`
            # (no structure at all) is skipped
            return raw if raw not in ("", "*") else None
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
    """A token is listed iff its `/`-segments occur as a CONTIGUOUS run of some code span's
    segments (`QUEUE_DIR/reservations` inside `QUEUE_DIR/reservations/*/*.json`; `attempts`
    inside `QUEUE_DIR/merge-door/attempts/*/*`), or -- for a bare-extension token (`.tmp`)
    -- some segment ends in it. A glob (`*.json`) must match a glob segment; a bare
    substring (`state` inside `mechanized-checks-state.json`) or a new child of a listed
    dir (`merge-door/unlisted`) is NOT a listing."""
    want = token.split("/")
    ext = token if token.startswith(".") and "/" not in token else None
    for span in spans:
        segs = span.split("/")
        for i in range(len(segs) - len(want) + 1):
            if segs[i : i + len(want)] == want:
                return True
        if ext is not None and any(seg.endswith(ext) for seg in segs):
            return True
    return False


def _eight_store_rows(text: str) -> list[list[str]]:
    """Body rows of the `## The eight stores` table as cell lists (header + rule dropped)."""
    section = text.split("## The eight stores", 1)[1].split("\n## ", 1)[0]
    rows = [ln for ln in section.splitlines() if ln.startswith("|")]
    body = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in rows[2:]]
    assert rows[0].split("|")[1:4] == [" Store ", " Venue ", " Authority for "], rows[0]
    return body


def _family_rows(text: str) -> list[list[str]]:
    """Body rows of the `## Derived families + new-fact carriers` table as cell lists."""
    section = text.split("## Derived families", 1)[1].split("\n## ", 1)[0]
    rows = [ln for ln in section.splitlines() if ln.startswith("|")]
    assert rows[0].split("|")[1:4] == [" Family ", " Path ", " Relation "], rows[0]
    return [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in rows[2:]]


def test_family_table_relation_cells_are_classified() -> None:
    """Every family row carries a Relation cell; each pinned family is present exactly once
    and carries its required classification (a loose substring does not count)."""
    rows = _family_rows(AUDIT.read_text())
    for r in rows:
        assert len(r) == 4 and all(r), r
        assert r[2] == "derived" or r[2] == SOLE or _PART_OF.match(r[2]), r
        if r[2] == SOLE:
            # a sole carrier names its fact as a quoted phrase, not a description of a process
            assert r[3].startswith('"'), r
    owners: list[str] = []
    for key, relation in FAMILY_RELATION:
        hits = [r for r in rows if key in r[1]]
        assert len(hits) == 1, (key, [r[1] for r in hits])
        assert relation in hits[0][2], (key, relation, hits[0][2])
        owners.append(hits[0][0])
    # distinct families live in distinct rows (folding several paths into one row would let
    # one cell "own" five families)
    assert len(set(owners)) == len(owners), owners
    # each sole carrier's cell carries ITS fact, not just any unique quoted text
    for key, phrase in SOLE_FACTS:
        (row,) = [r for r in rows if key in r[1]]
        assert phrase in row[3], (key, phrase, row[3])
    # no fact is owned twice: the fourth cell (derived-from / fact) is distinct per row, and
    # no family claims one of the eight stores' facts as its own
    facts = [r[3] for r in rows]
    assert len(set(facts)) == len(facts), facts
    for r in rows:
        for name, fact in EIGHT:
            assert fact not in r[3], (r[0], "claims", name, fact)


def test_audit_exists_and_lists_eight_plus_derived() -> None:
    text = AUDIT.read_text()
    for name in [n for n, _ in EIGHT] + DERIVED + NON_STORES:
        assert name in text, name
    # hand-witness (not probe-expressible: the doc is not comment-out mutable): a second
    # `| Authority for |` table anywhere in the page fails this count
    assert text.count("| Authority for |") == 1
    # the probe log is classified in the family table (sole carrier of probe-run evidence;
    # the annotations stay the authority for which probes are REQUIRED)
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
    for m in PENDING:
        # the S4 unit that lands a module MUST promote it to LANDED in the same change -- a
        # module that exists while still PENDING fails here, so it can never later vanish
        # from coverage unnoticed
        assert not (REPO / m).exists(), f"{m}: landed -- move it from PENDING to LANDED"
    for m in LANDED:
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
    # The `${var}.<suffix>` idiom (U-HE-29's cutover artifacts). Without the `shellsuffix`
    # pattern these are INVISIBLE to the extractor and the listed-ness check above passes
    # VACUOUSLY over them — reporting "nothing unlisted" for the same reason it would report
    # a clean sheet. Asserting the extractor SEES them is what makes that check non-vacuous.
    assert "*.XXXXXXXX*" in sh, sorted(sh)  # the mktemp venue-header stager


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
    assert listed("QUEUE_DIR/merge-door", spans)
    assert listed("merge-door/attempts", spans)
    assert not listed("*.json", spans)  # a glob needs a glob segment, not any `.json` file
    assert not listed("state", spans)
    assert not listed("merge-door/state", spans)
    assert not listed("attempts/state", spans)  # a new child of a listed dir is unlisted
    assert not listed("QUEUE_DIR/attempts", spans)  # segments must be contiguous
