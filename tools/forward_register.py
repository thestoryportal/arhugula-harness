#!/usr/bin/env python3
"""Forward-register derivation + validation (post-Phase-8 forward-work schema).

Single source of truth: ``.harness/forward-register.yaml``. Mirrors
``tools/arc_ledger.py`` / ``tools/substitution_ledger.py`` (the proven R-600 pattern)
for a DIFFERENT, still-open lifecycle bucket: the post-Phase-8 ``B-*`` forward-work
items previously tracked only as ~14K words of hand-maintained prose at
``.harness/post-phase-8-forward-register.md``, with no queryable structure and no
drift gate — the exact defect class R-IF-114 fixed for the R-FS-1 arc via
``arc-ledger.yaml``. That fix does not cover this register (``arc-ledger.yaml``'s own
``rfs1_status: resolved`` pin requires zero open standalone rows), hence this sibling
schema/tool.

  * ``derive()`` is PURE — returns per-status counts. Asserts nothing.
  * ``validate()`` enforces invariants: unique ids, valid status enum, a closed item
    cites a deliverable (``pr``), every non-closed/non-held item carries a
    ``close_out`` + ``council`` disposition, and the ``snapshot:`` pin matches the
    derived counts (catches a silent status flip that structural checks would miss).
  * ``check_prose_drift()`` cross-references this file's row ids against
    ``.harness/post-phase-8-forward-register.md``'s own ``### ID · ...`` headings —
    a NEW forward item appended to the prose file without a matching structured row
    (the original gap this tool closes) fails ``--check``.

Usage:
    python tools/forward_register.py --check      # CI gate; exit 1 on any violation
    python tools/forward_register.py --summary    # human-readable counts
    python tools/forward_register.py --json       # machine-readable derivation
    python tools/forward_register.py --open       # id + title + status for open work
    python tools/forward_register.py --detail B-24  # full prose block from the register
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

# NB: `yaml` imported lazily inside load() only — mirrors arc_ledger.py so derive()/
# validate() stay pure-python and importable without PyYAML present.

STATUSES = frozenset(
    {
        "open",
        "design_substrate_gated",
        "registered_finding",
        "operator_gated",
        "held",
        "closed",
    }
)
#: the OPEN set — genuinely actionable-or-gated forward work (excludes closed/held).
OPEN_STATUSES = frozenset(
    {"open", "design_substrate_gated", "registered_finding", "operator_gated"}
)
#: statuses that must carry a close_out + council disposition (mirrors the source
#: register's own per-item shape — every non-closed/non-held entry states both).
_NEEDS_CLOSE_OUT_AND_COUNCIL = OPEN_STATUSES

DEFAULT_LEDGER = Path(__file__).resolve().parents[1] / ".harness" / "forward-register.yaml"
DEFAULT_PROSE = (
    Path(__file__).resolve().parents[1] / ".harness" / "post-phase-8-forward-register.md"
)

#: matches "### B-24 · ..." / "### R-1 confirmed-DEFERRED · ..." heading lines — the
#: convention every per-item heading in the register follows.
_HEADING_ID_RE = re.compile(r"^###\s+([A-Z]+-\d+)\b.*·", re.MULTILINE)
#: matches the rarer "## <Section> ... (B-14)" umbrella-heading shape (a section that
#: names its owning item id in a trailing parenthetical, e.g. B-14's CXA section).
#: Anchored to end-of-line so it can't false-positive on a section header that merely
#: mentions an id range in passing (e.g. "(R-300..R-399, decomposition-owed)").
_SECTION_HEADING_ID_RE = re.compile(r"^##\s+.*\(([A-Z]+-\d+)\)\s*$", re.MULTILINE)
#: Tier A (Phase-8 closure residuals, `## A-1` .. `## A-4`) is deliberately OUT OF
#: SCOPE for this register — the front summary table already shows all 4 ~~closed~~,
#: and they are historical Phase-8-accounting provenance, not post-Phase-8 forward
#: work (the register's own §0 "two tiers" framing). Neither regex above matches
#: their "## A-N · ..." heading shape, so they never surface as false drift.


class RegisterError(ValueError):
    """A structural violation in the forward register (fails ``--check`` / CI)."""


def _id_from_heading(heading: str) -> str | None:
    """Extract the item id a heading string names, or None if neither shape matches."""
    m = _HEADING_ID_RE.match(heading) or _SECTION_HEADING_ID_RE.match(heading)
    return m.group(1) if m else None


def _prose_heading_lines(text: str) -> list[tuple[str, str]]:
    """Every (id, complete heading line) pair in the prose file, in file order.

    Scans whole ``#``/``##``/``###`` lines rather than doing a substring search, so a
    row's ``heading`` must match a CURRENT, COMPLETE heading line — not merely be a
    substring somewhere in the file. This is what catches a heading that grew a
    status suffix (e.g. "... — CLOSED") without the YAML row being updated to match:
    the OLD, shorter heading is a substring of the NEW line, but not equal to it.
    """
    pairs: list[tuple[str, str]] = []
    for line in text.splitlines():
        heading_id = _id_from_heading(line)
        if heading_id is not None:
            pairs.append((heading_id, line))
    return pairs


def _identity_digest(items: list[dict[str, Any]]) -> str:
    """SHA-256 fingerprint of the sorted ``id:status`` pairs.

    Aggregate per-status COUNTS alone can't catch two items swapping statuses while
    the totals stay put (e.g. B-16 and B-17 trading `registered_finding` <->
    `operator_gated`) — the same "same-count identity substitution" class the
    B-35 evidence-matrix fix (this same register) already solved with an identical
    digest technique. Never spells out a single id/status in the digest itself.
    """
    pairs = sorted(f"{r['id']}:{r['status']}" for r in items)
    return hashlib.sha256(",".join(pairs).encode()).hexdigest()[:16]


def load(path: Path = DEFAULT_LEDGER) -> dict[str, Any]:
    import yaml  # lazy — see module-top note

    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict) or "items" not in data:
        raise RegisterError(f"{path}: missing top-level 'items' list")
    return data


def derive(data: dict[str, Any]) -> dict[str, Any]:
    """Pure derivation — per-status counts + the open-item projection. No assertions."""
    items = data["items"]
    status_count: Counter[str] = Counter(r.get("status") for r in items)
    open_items = [r for r in items if r.get("status") in OPEN_STATUSES]

    return {
        "items": items,
        "open_items": open_items,
        "total": len(items),
        "open": status_count.get("open", 0),
        "design_substrate_gated": status_count.get("design_substrate_gated", 0),
        "registered_finding": status_count.get("registered_finding", 0),
        "operator_gated": status_count.get("operator_gated", 0),
        "held": status_count.get("held", 0),
        "closed": status_count.get("closed", 0),
        "by_status": dict(status_count),
    }


def validate(data: dict[str, Any]) -> list[str]:
    """Return a list of violation strings (empty == OK). Used by ``--check`` + tests."""
    violations: list[str] = []
    items = data["items"]

    seen_ids: set[str] = set()
    seen_headings: dict[str, str] = {}
    for r in items:
        rid = r.get("id", "<no-id>")
        if rid in seen_ids:
            violations.append(f"duplicate id {rid}")
        seen_ids.add(rid)

        status = r.get("status")
        if status not in STATUSES:
            violations.append(f"{rid}: invalid status {status!r}")
            continue

        if not r.get("title"):
            violations.append(f"{rid}: missing non-empty 'title'")

        heading = r.get("heading")
        if not heading:
            violations.append(f"{rid}: missing 'heading' back-pointer into the prose file")
        else:
            if heading in seen_headings:
                violations.append(
                    f"{rid}: heading also claimed by {seen_headings[heading]!r} "
                    f"(copy-pasted heading — each row must bind to its own prose block)"
                )
            seen_headings[heading] = rid
            heading_id = _id_from_heading(heading)
            if heading_id is None:
                violations.append(
                    f"{rid}: heading {heading!r} does not match a recognized "
                    f"'### ID ·' or '## ... (ID)' shape"
                )
            elif heading_id != rid:
                violations.append(f"{rid}: heading names id {heading_id!r}, not the row's own id")

        if status == "closed":
            if not r.get("pr"):
                violations.append(f"{rid}: closed item needs a 'pr' deliverable citation")
        elif status in _NEEDS_CLOSE_OUT_AND_COUNCIL:
            if not r.get("close_out"):
                violations.append(f"{rid}: {status} item needs a 'close_out' field")
            if not r.get("council"):
                violations.append(f"{rid}: {status} item needs a 'council' disposition")

    d = derive(data)
    snap = data.get("snapshot")
    if not isinstance(snap, dict):
        violations.append("missing 'snapshot' pin block")
    else:
        for key in (
            "total",
            "open",
            "design_substrate_gated",
            "registered_finding",
            "operator_gated",
            "held",
            "closed",
        ):
            if snap.get(key) != d[key]:
                violations.append(
                    f"snapshot.{key}={snap.get(key)} but derived {key}={d[key]} "
                    f"— a row changed without a snapshot bump (forward-only transit?)"
                )

        expected_digest = _identity_digest(items)
        if snap.get("identity_digest") != expected_digest:
            violations.append(
                f"snapshot.identity_digest={snap.get('identity_digest')!r} but derived "
                f"{expected_digest!r} — two items may have swapped statuses while "
                f"the aggregate counts stayed put (the count checks above can't catch "
                f"this; bump identity_digest on every real transit too)"
            )

    return violations


def check_prose_drift(data: dict[str, Any], prose_path: Path = DEFAULT_PROSE) -> list[str]:
    """Cross-reference row ids against the prose file's own '### ID · ...' headings.

    Catches the original defect this tool exists to prevent: a new B-* item appended
    to the prose register without a matching structured row (or vice versa — a row
    whose heading no longer appears verbatim in the prose file).
    """
    violations: list[str] = []
    text = prose_path.read_text(encoding="utf-8")

    yaml_ids = {r["id"] for r in data["items"]}
    pairs = _prose_heading_lines(text)
    prose_id_counts = Counter(heading_id for heading_id, _line in pairs)
    prose_line_by_id = dict(pairs)  # last occurrence wins; duplicates flagged below

    for missing in sorted(set(prose_id_counts) - yaml_ids):
        violations.append(f"prose heading '{missing}' has no matching row in forward-register.yaml")

    for dup_id, count in sorted(prose_id_counts.items()):
        if count > 1:
            violations.append(
                f"prose heading '{dup_id}' appears {count} times in {prose_path.name} "
                f"(duplicated item block — each id must have exactly one heading)"
            )

    for r in data["items"]:
        heading = r.get("heading")
        if not heading:
            continue
        current_line = prose_line_by_id.get(r["id"])
        if current_line is None:
            violations.append(f"{r['id']}: no heading line for this id found in {prose_path.name}")
        elif heading != current_line:
            violations.append(
                f"{r['id']}: row heading is stale — prose now reads {current_line!r}, "
                f"row still has {heading!r} (a substring match would have hidden this)"
            )

    return violations


def _summary(d: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"total                {d['total']}",
            f"open                 {d['open']}",
            f"design_substrate_gated {d['design_substrate_gated']}",
            f"registered_finding   {d['registered_finding']}",
            f"operator_gated       {d['operator_gated']}",
            f"held                 {d['held']}",
            f"closed               {d['closed']}",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Forward-register derivation + validation.")
    ap.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    ap.add_argument("--prose", type=Path, default=DEFAULT_PROSE)
    ap.add_argument(
        "--check", action="store_true", help="validate + prose-drift; exit 1 on violation"
    )
    ap.add_argument("--summary", action="store_true", help="human-readable counts")
    ap.add_argument("--json", action="store_true", help="machine-readable derivation")
    ap.add_argument("--open", action="store_true", help="id + title + status for open work only")
    ap.add_argument("--detail", metavar="ID", help="print the full prose block for one item id")
    args = ap.parse_args(argv)

    data = load(args.ledger)

    if args.detail:
        row = next((r for r in data["items"] if r["id"] == args.detail), None)
        if row is None:
            print(f"no such id: {args.detail}", file=sys.stderr)
            return 1
        text = args.prose.read_text(encoding="utf-8")
        heading = row["heading"]
        lines = text.splitlines(keepends=True)
        offset = 0
        start: int | None = None
        for line in lines:
            if line.rstrip("\n") == heading:
                start = offset
                break
            offset += len(line)
        if start is None:
            print(f"heading not found as a complete line in prose: {heading!r}", file=sys.stderr)
            return 1
        rest = text[start:]
        next_heading = re.search(r"\n(#{2,3})\s", rest[len(heading) :])
        end = len(rest) if next_heading is None else len(heading) + next_heading.start() + 1
        print(rest[:end].rstrip())
        return 0

    if args.check:
        violations = validate(data)
        violations += check_prose_drift(data, args.prose)
        if violations:
            print("FORWARD REGISTER CHECK FAILED:", file=sys.stderr)
            for v in violations:
                print(f"  - {v}", file=sys.stderr)
            return 1
        d = derive(data)
        print(
            f"register OK — {d['total']} items: {d['open']} open / "
            f"{d['design_substrate_gated']} design_substrate_gated / "
            f"{d['registered_finding']} registered_finding / "
            f"{d['operator_gated']} operator_gated / {d['held']} held / "
            f"{d['closed']} closed"
        )
        return 0

    d = derive(data)
    if args.open:
        for r in d["open_items"]:
            print(f"{r['id']}\t{r['status']}\t{r['title']}")
        return 0
    if args.json:
        import json

        view = {k: v for k, v in d.items() if k not in ("items", "open_items")}
        print(json.dumps(view, indent=2))
        return 0

    print(_summary(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
