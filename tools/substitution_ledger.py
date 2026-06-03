#!/usr/bin/env python3
"""Substitution-ledger derivation + validation (R-600-substitution-ledger-schema).

Single source of truth: ``.harness/substitutions.yaml``. This module DERIVES the
bucket counts + the canonical integers (RETIRED / pipeline-advanced) from that file
so the prose docs cite a computed number instead of hand-maintaining it. An impossible
tally becomes a ``--check`` (CI) failure rather than a months-later draft discovery.

Why this exists: the R-700 Phase-8 close exposed ``48/54`` as internally impossible
(48 RETIRED with 3 PARTIAL ⇒ pipeline-advanced would be 51, not the published 49) —
a count hand-maintained across ~51 batch footers + 5 files with nothing reconciling
them. See ``.harness/phase-8-graduation.md`` + CLAUDE.md §10.9.

Design (per advisor, R-600 build arc):
  * ``derive()`` is PURE — returns counts, asserts nothing. ``generate.py`` consumes it.
  * ``validate()`` enforces invariants — used by ``--check`` and the test suite.
  * ``counted_in_retired`` is DERIVED from ``disposition``, NEVER from string-matching
    ``sign_off_label``. A ``RETIRED-AS-X`` label on a PARTIAL row (e.g. OD-4) is legal
    and uncounted — the label≠count-membership rule the R-700 close turned on.
  * The snapshot pin (``snapshot:`` block in the yaml) catches a *silent within-axis
    disposition flip* (e.g. OD-4 PARTIAL→SUBSTANTIVE_RETIRED) that every structural
    invariant would otherwise pass. Forward-only: a real transit edits the row AND the
    snapshot in the same commit.

Usage:
    python tools/substitution_ledger.py --check          # CI gate; exit 1 on any violation
    python tools/substitution_ledger.py --summary        # human-readable counts
    python tools/substitution_ledger.py --json           # machine-readable (for generate.py)
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

# --- The disposition enum + its count-membership (the ONLY place this mapping lives) ------

#: disposition -> counted in the RETIRED integer?
RETIRED_DISPOSITIONS = frozenset({"SUBSTANTIVE_RETIRED", "AUTHORING_ONLY", "BOUNDED_RESIDUAL"})
#: disposition -> counted in pipeline-advanced (RETIRED + RETIRE_READY + PARTIAL)?
PIPELINE_DISPOSITIONS = RETIRED_DISPOSITIONS | frozenset({"RETIRE_READY", "PARTIAL"})

VALID_DISPOSITIONS = PIPELINE_DISPOSITIONS | frozenset({"STILL_BOUNDED", "SB_INDEFINITE"})
VALID_AXES = frozenset({"IS", "AS", "CP", "OD", "CXA"})

DEFAULT_LEDGER = Path(__file__).resolve().parents[1] / ".harness" / "substitutions.yaml"


class LedgerError(ValueError):
    """A structural violation in the substitution ledger (fails ``--check`` / CI)."""


def load(path: Path = DEFAULT_LEDGER) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict) or "substitutions" not in data:
        raise LedgerError(f"{path}: missing top-level 'substitutions' list")
    return data


def derive(data: dict[str, Any]) -> dict[str, Any]:
    """Pure derivation — counts only, no assertions. ``generate.py`` consumes this."""
    rows = data["substitutions"]
    canonical = [r for r in rows if r.get("canonical", False)]

    by_disposition: Counter[str] = Counter(r["disposition"] for r in canonical)
    axis_rowcount: Counter[str] = Counter(r["axis"] for r in canonical)
    axis_retired: Counter[str] = Counter(
        r["axis"] for r in canonical if r["disposition"] in RETIRED_DISPOSITIONS
    )

    retired = sum(by_disposition[d] for d in RETIRED_DISPOSITIONS)
    pipeline_advanced = sum(by_disposition[d] for d in PIPELINE_DISPOSITIONS)
    total = len(canonical)

    return {
        "retired": retired,
        "pipeline_advanced": pipeline_advanced,
        "total_canonical": total,
        "non_canonical": len(rows) - total,
        "by_disposition": dict(by_disposition),
        "axis_rowcount": dict(axis_rowcount),  # IS 9 / AS 11 / CP 21 / OD 8 / CXA 5
        "axis_retired": dict(axis_retired),  # IS 9 / AS 9 / CP 20 / OD 7 / CXA 1
        # The 8 non-substantive rows with their terminal graduation sign-off labels.
        "sign_offs": [
            {
                "id": r["id"],
                "disposition": r["disposition"],
                "counted_in_retired": r["disposition"] in RETIRED_DISPOSITIONS,
                "sign_off_label": r.get("sign_off_label"),
                "r_pointer": r.get("r_pointer"),
            }
            for r in canonical
            if r["disposition"] not in {"SUBSTANTIVE_RETIRED", "AUTHORING_ONLY"}
            and r.get("sign_off_label")
        ],
    }


def validate(data: dict[str, Any]) -> list[str]:
    """Return a list of violation strings (empty == OK). Used by ``--check`` + tests."""
    violations: list[str] = []
    rows = data["substitutions"]

    # Per-row well-formedness.
    seen_ids: set[str] = set()
    for r in rows:
        rid = r.get("id", "<no-id>")
        if rid in seen_ids:
            violations.append(f"duplicate id {rid}")
        seen_ids.add(rid)
        if r.get("disposition") not in VALID_DISPOSITIONS:
            violations.append(f"{rid}: invalid disposition {r.get('disposition')!r}")
        if r.get("axis") not in VALID_AXES:
            violations.append(f"{rid}: invalid axis {r.get('axis')!r}")
        if "canonical" not in r or not isinstance(r["canonical"], bool):
            violations.append(f"{rid}: 'canonical' must be an explicit bool")
        # label≠count-membership: a sign_off_label may say RETIRED-AS-X, but the row's
        # count-membership is driven by `disposition`. Surface the (legal) case so a
        # future editor cannot quietly turn the label into a count.
        label = r.get("sign_off_label") or ""
        counted = r.get("disposition") in RETIRED_DISPOSITIONS
        if label.upper().startswith("RETIRED-AS") and counted:
            violations.append(
                f"{rid}: sign_off_label {label!r} starts with RETIRED-AS but the row is "
                f"counted via disposition {r['disposition']} — labels must NOT drive the count"
            )

    d = derive(data)

    # Structural invariant 1 — exactly 54 canonical rows (the entry's must_pass).
    if d["total_canonical"] != 54:
        violations.append(f"canonical row count is {d['total_canonical']}, expected 54")

    # Structural invariant 2 — the bucket sum equals the canonical total.
    bucket_sum = sum(d["by_disposition"].values())
    if bucket_sum != d["total_canonical"]:
        violations.append(f"bucket sum {bucket_sum} != canonical total {d['total_canonical']}")

    # Structural invariant 3 — the 48-vs-49 impossibility class. pipeline-advanced MUST
    # equal RETIRED + RETIRE_READY + PARTIAL by definition; this is the exact inconsistency
    # the R-700 draft caught (48 RETIRED + 3 PARTIAL cannot be 49 pipeline-advanced).
    rr = d["by_disposition"].get("RETIRE_READY", 0)
    partial = d["by_disposition"].get("PARTIAL", 0)
    if d["pipeline_advanced"] != d["retired"] + rr + partial:
        violations.append(
            f"pipeline_advanced {d['pipeline_advanced']} != RETIRED {d['retired']} "
            f"+ RETIRE_READY {rr} + PARTIAL {partial}"
        )

    # Snapshot pin — the ONLY guard against a silent within-axis disposition flip
    # (e.g. OD-4 PARTIAL→SUBSTANTIVE_RETIRED: every structural invariant still passes,
    # but RETIRED drifts 46→47). Forward-only: a real transit bumps this block + the row.
    snap = data.get("snapshot")
    if not isinstance(snap, dict):
        violations.append("missing 'snapshot' pin block")
    else:
        for key in ("retired", "pipeline_advanced", "total_canonical"):
            if snap.get(key) != d[key]:
                violations.append(
                    f"snapshot.{key}={snap.get(key)} but derived {key}={d[key]} "
                    f"— a row changed without a snapshot bump (forward-only transit?)"
                )

    return violations


def _summary(d: dict[str, Any]) -> str:
    lines = [
        f"RETIRED            {d['retired']}/54 ({100 * d['retired'] / d['total_canonical']:.1f}%)",
        f"pipeline-advanced  {d['pipeline_advanced']}/54 "
        f"({100 * d['pipeline_advanced'] / d['total_canonical']:.1f}%)",
        f"canonical rows     {d['total_canonical']} (+{d['non_canonical']} non-canonical)",
        "",
        "by disposition:    "
        + ", ".join(f"{k}={v}" for k, v in sorted(d["by_disposition"].items())),
        "axis row-count:    "
        + ", ".join(f"{k}={v}" for k, v in sorted(d["axis_rowcount"].items())),
        "axis RETIRED:      " + ", ".join(f"{k}={v}" for k, v in sorted(d["axis_retired"].items())),
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Substitution-ledger derivation + validation.")
    ap.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    ap.add_argument("--check", action="store_true", help="validate; exit 1 on any violation")
    ap.add_argument("--summary", action="store_true", help="human-readable counts")
    ap.add_argument("--json", action="store_true", help="machine-readable derivation")
    args = ap.parse_args(argv)

    data = load(args.ledger)

    if args.check:
        violations = validate(data)
        if violations:
            print("SUBSTITUTION LEDGER CHECK FAILED:", file=sys.stderr)
            for v in violations:
                print(f"  - {v}", file=sys.stderr)
            return 1
        d = derive(data)
        print(
            f"ledger OK — {d['retired']}/54 RETIRED, {d['pipeline_advanced']}/54 pipeline-advanced"
        )
        return 0

    d = derive(data)
    if args.json:
        print(json.dumps(d, indent=2))
    else:  # default / --summary
        print(_summary(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
