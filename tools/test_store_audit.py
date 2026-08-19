"""C-HE-30: one authority per fact; every store the coordination modules touch is listed.

Static phase0 witness (U-HE-14). The audit one-pager at
`.harness/spec/store-audit-he-loop-lanes.md` must (a) exist, (b) enumerate exactly the
eight stores of the C-HE-30 table plus the derived families named in its clearance-fold
note, with ONE `| Authority for |` table, and (c) name every `QUEUE_DIR` / `.harness`
path literal the four coordination modules spell -- so a runtime path that creates a
store the audit does not list turns this row red (C-HE-30 Invariant 2).

The literal extractor covers the idioms the modules actually use -- textual
`.harness/<name>`, pathlib chains `".harness" / "<name>"`, `QUEUE_DIR / "<name>"` and
`QUEUE_DIR / f"<name>"` (placeholders normalised to `*`), `QUEUE_DIR.glob("<pat>")`,
`.with_suffix("<ext>")`, `.tmp` stagers, and the merge-door / reservation literal family
-- not only the bare-string form, which would have let `tools/arc_metrics.py` (pathlib
throughout) pass vacuously.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AUDIT = REPO / ".harness" / "spec" / "store-audit-he-loop-lanes.md"
MODULES = [
    "tools/arc_metrics.py",
    "tools/merge_door.py",
    "tools/reservations.py",
    "tools/hooks/loop_lib.sh",
]
EIGHT = [
    "Queue entries",
    "Reservation files",
    "Merge-door lease",
    "arc-metrics.jsonl",
    "merge-gate-log",
    "loop_status.md",
    "Finding emission",
    "Committed history on",
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
    # `QUEUE_DIR / "<name>"` and `QUEUE_DIR / f"<name>"`
    (re.compile(r'QUEUE_DIR\s*/\s*f?"([^"]+)"'), "queue"),
    # `QUEUE_DIR.glob("<pat>")`
    (re.compile(r'QUEUE_DIR\.glob\("([^"]+)"\)'), "queue"),
    # `.with_suffix("<ext>")`
    (re.compile(r'\.with_suffix\("([^"]+)"\)'), "suffix"),
    # `.tmp` stagers (`with_name(f".{name}.{pid}.tmp")`)
    (re.compile(r'f?"[^"]*\.tmp"'), "tmp"),
    # merge-door / reservation literal family (S4 modules)
    (
        re.compile(
            r'"(reservations|merge-door|lanes|LEASE|transition\.|released\.|reclaimed\.)[^"]*"'
        ),
        "family",
    ),
]


def _token(kind: str, match: re.Match[str]) -> str:
    raw = match.group(1) if match.re.groups else match.group(0)
    raw = _PLACEHOLDER.sub("*", raw.strip('"'))
    if kind == "text":
        return raw
    if kind == "harness_seg":
        return f".harness/{raw}"
    if kind == "queue":
        return f"QUEUE_DIR/{raw}"
    if kind == "suffix":
        return f"*{raw}"
    if kind == "tmp":
        return ".tmp"
    return raw.split("/")[-1]


def store_literals(path: Path) -> set[str]:
    text = path.read_text()
    out: set[str] = set()
    for pat, kind in _PATTERNS:
        for m in pat.finditer(text):
            out.add(_token(kind, m))
    return out


def _eight_store_rows(text: str) -> list[list[str]]:
    """Body rows of the `## The eight stores` table as cell lists (header + rule dropped)."""
    section = text.split("## The eight stores", 1)[1].split("\n## ", 1)[0]
    rows = [ln for ln in section.splitlines() if ln.startswith("|")]
    body = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in rows[2:]]
    assert rows[0].split("|")[1:4] == [" Store ", " Venue ", " Authority for "], rows[0]
    return body


def test_audit_exists_and_lists_eight_plus_derived() -> None:
    text = AUDIT.read_text()
    for name in EIGHT + DERIVED + NON_STORES:
        assert name in text, name
    # the eight-store TABLE itself: exactly eight rows, each naming one spec store in its
    # first cell, each with a non-empty venue + authority cell (a loose substring elsewhere
    # in the page -- e.g. `merge-gate-log` in the lock section -- does not count)
    rows = _eight_store_rows(text)
    assert len(rows) == 8, [r[0] for r in rows]
    for name in EIGHT:
        hits = [r for r in rows if name in r[0]]
        assert len(hits) == 1, (name, len(hits))
    for r in rows:
        assert len(r) == 3 and all(r), r
    # hand-witness (not probe-expressible: the doc is not comment-out mutable): a second
    # `| Authority for |` table anywhere in the page fails this count
    assert text.count("| Authority for |") == 1
    # the probe log is a run log -- DERIVED, never an authority
    assert "`.harness/mutation-probe-log.jsonl`" in text.split("## Derived families")[1]


def test_every_path_literal_in_modules_is_listed() -> None:
    text = AUDIT.read_text()
    for m in MODULES:
        p = REPO / m
        if not p.exists():
            continue  # merge_door / reservations land in S4; the row re-runs then
        tokens = store_literals(p)
        # per module, never vacuous: a coordination module that spells NO store literal the
        # extractor recognises is an extractor gap, not a clean module
        assert tokens, f"{m}: extractor saw no store literals"
        for token in sorted(tokens):
            # hand-witness: removing any listed token from the audit page turns this red
            assert token in text, f"{m}: store literal {token!r} not in audit"


def test_extractor_sees_arc_metrics_idioms() -> None:
    lits = store_literals(REPO / "tools" / "arc_metrics.py")
    for expected in (
        ".harness/arc-metrics.jsonl",
        "QUEUE_DIR/*.json",
        "QUEUE_DIR/*.taken",
        "QUEUE_DIR/.ledger-claim-*",
        ".tmp",
    ):
        assert expected in lits, (expected, sorted(lits))
