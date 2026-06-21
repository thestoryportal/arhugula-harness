#!/usr/bin/env python3
"""Arc-ledger derivation + validation (roadmap-dashboard overhaul).

Single source of truth: ``.harness/arc-ledger.yaml``. This module DERIVES every
arc/unit count + view from that file so the dashboard renders a computed status
instead of hand-maintaining it in parsed markdown (which drifted — the old §5
table lagged #671; ``test_dashboard_generate.py`` hardcoded counts that went stale
= R-IF-114). A stale/impossible tally becomes a ``--check`` (CI) failure rather
than a months-later discovery.

Mirrors ``tools/substitution_ledger.py`` exactly (the proven R-600 pattern):
  * ``derive()`` is PURE — returns counts + the {frozen, standalone} projection
    ``generate.py`` consumes; asserts nothing.
  * ``validate()`` enforces invariants — used by ``--check`` and the test suite.
  * The ``snapshot:`` pin catches a silent status flip (e.g. a registered arc
    quietly flipped to closed) that every structural invariant would pass.
    Forward-only: a real transit edits the row AND the snapshot in the same commit.
  * ``registered`` arcs are gate-forced to carry ``decompose_at_open: true`` +
    ``parent_arc`` + ``anticipated_scope`` and ZERO ``U-*`` unit ids — the
    "do not fabricate units for unbuilt arcs" discipline (units come from git
    as-built only).

Usage:
    python tools/arc_ledger.py --check      # CI gate; exit 1 on any violation
    python tools/arc_ledger.py --summary    # human-readable counts
    python tools/arc_ledger.py --json       # machine-readable (for generate.py)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

# NB: `yaml` is imported lazily inside load() (the ONLY function that needs it) — NOT
# at module level. This keeps `import arc_ledger` + derive()/validate() pure-python so
# generate.py can import this module + reuse derive() under the no-PyYAML system Python
# 3.9 the Codex dashboard guard regenerates the dashboard with (it hand-parses the YAML
# text itself, then feeds the rows through this module's derive()). See
# tools/dashboard/generate.py `_arc_ledger_fallback_load`.

# --- The status enums (the ONLY place this mapping lives) --------------------

#: frozen arcs are the completed 11-arc build order — always closed.
FROZEN_STATUSES = frozenset({"closed"})
#: standalone arcs carry a 4+1-way status.
STANDALONE_STATUSES = frozenset({"closed", "remaining", "gated", "resolved", "registered"})
#: the OPEN set — committed work not yet built+merged (drives the R-FS-1-active guard
#: + the generate.py FATAL invariant twin).
OPEN_STANDALONE = frozenset({"remaining", "gated", "registered"})

VALID_KINDS = frozenset({"frozen", "standalone"})

_UNIT_ID_RE = re.compile(r"\bU-[A-Z]{2}-\d+\b")

DEFAULT_LEDGER = Path(__file__).resolve().parents[1] / ".harness" / "arc-ledger.yaml"


class LedgerError(ValueError):
    """A structural violation in the arc ledger (fails ``--check`` / CI)."""


def load(path: Path = DEFAULT_LEDGER) -> dict[str, Any]:
    import yaml  # lazy — see module-top note; keeps derive()/validate() no-PyYAML-importable

    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict) or "arcs" not in data:
        raise LedgerError(f"{path}: missing top-level 'arcs' list")
    return data


def derive(data: dict[str, Any]) -> dict[str, Any]:
    """Pure derivation — counts + the {frozen, standalone} projection. No assertions."""
    rows = data["arcs"]
    frozen = sorted(
        (r for r in rows if r.get("kind") == "frozen"),
        key=lambda r: r.get("position", 0),
    )
    standalone = [r for r in rows if r.get("kind") == "standalone"]

    standalone_status: Counter[str] = Counter(r.get("status") for r in standalone)
    frozen_done = sum(1 for r in frozen if r.get("status") == "closed")

    open_standalone = [r for r in standalone if r.get("status") in OPEN_STANDALONE]

    return {
        "frozen": frozen,
        "standalone": standalone,
        "open_standalone": open_standalone,
        "frozen_total": len(frozen),
        "frozen_done": frozen_done,
        "standalone_total": len(standalone),
        "standalone_closed": standalone_status.get("closed", 0),
        "standalone_remaining": standalone_status.get("remaining", 0),
        "standalone_gated": standalone_status.get("gated", 0),
        "standalone_resolved": standalone_status.get("resolved", 0),
        "standalone_registered": standalone_status.get("registered", 0),
        # the build-ready denominator (excludes registered/decompose-at-open + resolved).
        "standalone_buildable": standalone_status.get("closed", 0)
        + standalone_status.get("remaining", 0),
        "by_status": dict(standalone_status),
    }


def validate(data: dict[str, Any]) -> list[str]:
    """Return a list of violation strings (empty == OK). Used by ``--check`` + tests."""
    violations: list[str] = []
    rows = data["arcs"]
    all_ids = {r.get("id") for r in rows}

    seen_ids: set[str] = set()
    for r in rows:
        rid = r.get("id", "<no-id>")
        if rid in seen_ids:
            violations.append(f"duplicate id {rid}")
        seen_ids.add(rid)

        kind = r.get("kind")
        status = r.get("status")
        if kind not in VALID_KINDS:
            violations.append(f"{rid}: invalid kind {kind!r}")
            continue

        if kind == "frozen":
            if status not in FROZEN_STATUSES:
                violations.append(
                    f"{rid}: frozen arc has invalid status {status!r} (must be closed)"
                )
            if not isinstance(r.get("position"), int) or not (1 <= r.get("position", 0) <= 11):
                violations.append(
                    f"{rid}: frozen arc needs position in 1..11, got {r.get('position')!r}"
                )
            if not r.get("units"):
                violations.append(f"{rid}: frozen arc must carry as-built units")
            continue

        # kind == standalone
        if status not in STANDALONE_STATUSES:
            violations.append(f"{rid}: standalone arc has invalid status {status!r}")
        if status == "closed":
            # contract-extenders mint no U-* unit: a pr OR units OR spec_delta is the deliverable.
            if not (r.get("pr") or r.get("units") or r.get("spec_delta")):
                violations.append(
                    f"{rid}: closed arc needs a deliverable (pr / units / spec_delta)"
                )
        elif status == "gated":
            if not r.get("depends_on"):
                violations.append(f"{rid}: gated arc needs a depends_on (the blocker)")
        elif status == "resolved":
            if not r.get("resolution"):
                violations.append(f"{rid}: resolved arc needs a resolution note")
        elif status == "registered":
            # The "do not fabricate units for unbuilt arcs" discipline, as a gate.
            if r.get("decompose_at_open") is not True:
                violations.append(f"{rid}: registered arc must set decompose_at_open: true")
            if not r.get("parent_arc"):
                violations.append(f"{rid}: registered arc must name a parent_arc")
            elif r.get("parent_arc") not in all_ids:
                violations.append(
                    f"{rid}: parent_arc {r.get('parent_arc')!r} is not a known arc id"
                )
            if not r.get("anticipated_scope"):
                violations.append(f"{rid}: registered arc must carry an anticipated_scope")
            unit_ids = [u.get("id") for u in (r.get("units") or []) if u.get("id")]
            if unit_ids:
                violations.append(
                    f"{rid}: registered arc must NOT carry U-* unit ids "
                    f"(units are decomposed at arc-open): {unit_ids}"
                )
            # belt-and-suspenders: no U-* anywhere in the row's anticipated_scope text either.
            if _UNIT_ID_RE.search(r.get("anticipated_scope", "")):
                violations.append(
                    f"{rid}: registered arc anticipated_scope must not name a concrete U-* unit"
                )

    d = derive(data)

    # R-FS-1-ACTIVE invariant (the generate.py FATAL twin): if the full-spec build is
    # ACTIVE there must be OPEN work — at least one open standalone (remaining/gated/
    # registered). All-closed/resolved with no open arc = drift (the whole point of the
    # forward register is to never be silently empty while R-FS-1 is ACTIVE).
    if not d["open_standalone"]:
        violations.append(
            "R-FS-1 is ACTIVE but zero OPEN standalone arcs (remaining/gated/registered) — "
            "the forward register has drifted empty"
        )

    # Snapshot pin — the guard against a silent status flip (every structural invariant
    # still passes; forward-only: a real transit bumps this block + the row).
    snap = data.get("snapshot")
    if not isinstance(snap, dict):
        violations.append("missing 'snapshot' pin block")
    else:
        for key in (
            "frozen_total",
            "frozen_done",
            "standalone_closed",
            "standalone_gated",
            "standalone_resolved",
            "standalone_registered",
        ):
            if snap.get(key) != d[key]:
                violations.append(
                    f"snapshot.{key}={snap.get(key)} but derived {key}={d[key]} "
                    f"— a row changed without a snapshot bump (forward-only transit?)"
                )

    return violations


def _summary(d: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"frozen build order   {d['frozen_done']}/{d['frozen_total']} done",
            f"standalone closed    {d['standalone_closed']}",
            f"standalone gated     {d['standalone_gated']}",
            f"standalone resolved  {d['standalone_resolved']}",
            f"standalone forward   {d['standalone_registered']} (registered / decompose-at-open)",
            "",
            "by status:           "
            + ", ".join(f"{k}={v}" for k, v in sorted(d["by_status"].items())),
        ]
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Arc-ledger derivation + validation.")
    ap.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    ap.add_argument("--check", action="store_true", help="validate; exit 1 on any violation")
    ap.add_argument("--summary", action="store_true", help="human-readable counts")
    ap.add_argument("--json", action="store_true", help="machine-readable derivation")
    args = ap.parse_args(argv)

    data = load(args.ledger)

    if args.check:
        violations = validate(data)
        if violations:
            print("ARC LEDGER CHECK FAILED:", file=sys.stderr)
            for v in violations:
                print(f"  - {v}", file=sys.stderr)
            return 1
        d = derive(data)
        print(
            f"ledger OK — frozen {d['frozen_done']}/{d['frozen_total']}, "
            f"standalone {d['standalone_closed']} closed / {d['standalone_gated']} gated / "
            f"{d['standalone_resolved']} resolved / {d['standalone_registered']} forward"
        )
        return 0

    d = derive(data)
    if args.json:
        # drop the heavy row lists for the machine view; generate.py reads the rows directly.
        view = {k: v for k, v in d.items() if k not in ("frozen", "standalone", "open_standalone")}
        print(json.dumps(view, indent=2))
    else:  # default / --summary
        print(_summary(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
