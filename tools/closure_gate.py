#!/usr/bin/env python3
"""Closure gate — the binding "harness coding fully closed" predicate checker.

Operationalizes `.harness/audit/Closure_Gate_v1.md`: a two-tier predicate set
(Tier 1 build-complete → gates R-FS-1; Tier 2 quality/close → gates R-CL-C1).

It does NOT define a new source of truth — every predicate DELEGATES to an
existing CI-gated tool, the arc-ledger snapshot, or a roadmap R-NNN status:
  * G1.1  arc-ledger snapshot   (.harness/arc-ledger.yaml)
  * G1.2  arc_ledger.py --check
  * G1.3  overlay contract orphans   (overlay.py query --orphans)
  * G1.5  overlay cxa-seam-missing   (overlay.py query --orphans)
  * G1.6  substitution_ledger.py --check
  * G1.4/G1.7/G1.8 + Tier 2          (reported with status; not auto-asserted)

Usage:
    python tools/closure_gate.py            # human-readable report (all predicates)
    python tools/closure_gate.py --check    # exit 1 if any AUTOMATABLE predicate fails;
                                            #   prints manual predicates as a checklist
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ARC_LEDGER = REPO_ROOT / ".harness" / "arc-ledger.yaml"
ROADMAP = REPO_ROOT / "Project_Roadmap_v1.md"
CLEARANCE = REPO_ROOT / ".harness" / "clearance"
TIER1_MANUAL_SIGNOFF = REPO_ROOT / ".harness" / "r-fs-1-tier1-manual-signoff.json"
PY = sys.executable

# Documented-phantom contract IDs are excluded upstream, at the single source of
# truth `tools/semantic_overlay/overlay.py::DOCUMENTED_NON_CONTRACTS` (B-35 found
# this file's own local copy only listed C-IS-11, missing C-IS-14 per the SAME
# canonical citation — moved there so both consumers can't drift independently).


# --------------------------------------------------------------------------- #
# Delegated checks
# --------------------------------------------------------------------------- #
def _run(*argv: str) -> tuple[int, str]:
    proc = subprocess.run([PY, *argv], cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    return proc.returncode, (proc.stdout + proc.stderr)


def _arc_snapshot() -> dict[str, int]:
    """Parse the flat `snapshot:` block of arc-ledger.yaml (stdlib-only)."""
    out: dict[str, int] = {}
    if not ARC_LEDGER.is_file():
        return out
    in_snap = False
    for line in ARC_LEDGER.read_text(encoding="utf-8").splitlines():
        if line.rstrip() == "snapshot:":
            in_snap = True
            continue
        if in_snap:
            m = re.match(r"\s{2}(\w+):\s*(\d+)\s*$", line)
            if m:
                out[m.group(1)] = int(m.group(2))
            elif line and not line.startswith("  "):
                break
    return out


def _overlay_orphans() -> dict:
    _, out = _run("tools/semantic_overlay/overlay.py", "query", "--orphans")
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return {}


def _roadmap_status(rid: str) -> str:
    if not ROADMAP.is_file():
        return "?"
    txt = ROADMAP.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(txt):
        if re.match(rf"^{re.escape(rid)}:\s*$", line):
            for j in range(i + 1, min(i + 8, len(txt))):
                m = re.match(r"\s*status:\s*([A-Za-z0-9_\-]+)", txt[j])
                if m:
                    return m.group(1)
    return "?"


def _manual_signoff(pid: str, fallback: str) -> tuple[bool | None, str]:
    if not TIER1_MANUAL_SIGNOFF.is_file():
        return None, f"{fallback}; sign-off missing ({TIER1_MANUAL_SIGNOFF.name})"

    try:
        data = json.loads(TIER1_MANUAL_SIGNOFF.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"{fallback}; sign-off invalid: {exc}"

    if not isinstance(data, dict):
        return None, f"{fallback}; sign-off invalid: root object missing"

    gates = data.get("gates")
    if not isinstance(gates, dict):
        return None, f"{fallback}; sign-off invalid: gates object missing"

    gate = gates.get(pid)
    if not isinstance(gate, dict) or gate.get("status") != "signed":
        return None, f"{fallback}; sign-off missing ({TIER1_MANUAL_SIGNOFF.name})"

    evidence = gate.get("evidence")
    if not isinstance(evidence, str) or not evidence.strip():
        return None, f"{fallback}; sign-off missing evidence"
    return True, evidence.strip()


# --------------------------------------------------------------------------- #
# Predicate evaluation
# --------------------------------------------------------------------------- #
class Pred:
    def __init__(self, pid, desc, state, auto, detail=""):
        self.pid, self.desc, self.state, self.auto, self.detail = (
            pid,
            desc,
            state,
            auto,
            detail,
        )  # state: True | False | None (manual/unknown)


def evaluate() -> list[Pred]:
    p: list[Pred] = []
    snap = _arc_snapshot()
    orph = _overlay_orphans()  # `query --orphans` emits the orphans dict directly

    # ---- Tier 1 — build-complete (automatable subset) ---------------------- #
    reg, gated = snap.get("standalone_registered"), snap.get("standalone_gated")
    frozen = f"{snap.get('frozen_done')}/{snap.get('frozen_total')}"
    p.append(
        Pred(
            "G1.1",
            "Forward register empty (registered + gated == 0)",
            (reg == 0 and gated == 0) if reg is not None else None,
            True,
            f"registered={reg}, gated={gated}, frozen_done={frozen}",
        )
    )

    rc, _ = _run("tools/arc_ledger.py", "--check")
    p.append(
        Pred(
            "G1.2",
            "Arc-ledger tally consistent (arc_ledger.py --check)",
            rc == 0,
            True,
            f"exit={rc}",
        )
    )

    # Documented-phantom IDs are already excluded by overlay.py's own
    # `contract_without_code` derivation — nothing left to re-filter here.
    contracts = orph.get("contract_without_code", [])
    p.append(
        Pred(
            "G1.3",
            "No contract orphans (head-scoped, ex-documented)",
            len(contracts) == 0 if orph else None,
            True,
            f"{len(contracts)} real",
        )
    )

    seams = orph.get("cxa_seam_missing_endpoint", [])
    p.append(
        Pred(
            "G1.5",
            "CXA seams complete (no missing endpoint)",
            len(seams) == 0 if orph else None,
            True,
            f"{len(seams)} missing",
        )
    )

    rc, _ = _run("tools/substitution_ledger.py", "--check")
    p.append(
        Pred(
            "G1.6",
            "Substitutions retired/ratified (substitution_ledger --check)",
            rc == 0,
            True,
            f"exit={rc}",
        )
    )

    # ---- Tier 1 — manual / advisory (reported, not asserted) --------------- #
    units = orph.get("unit_without_code", [])
    state, detail = _manual_signoff(
        "G1.4",
        f"{len(units)} advisory (all audit-resolved non-gaps per RB-DOC-05)",
    )
    p.append(
        Pred(
            "G1.4",
            "Unit orphans (head-scoped, advisory — review)",
            state,
            False,
            detail,
        )
    )
    state, detail = _manual_signoff(
        "G1.7",
        "see audit RB-RT-07 (1 likely-stale OPEN fork to re-ground)",
    )
    p.append(
        Pred(
            "G1.7",
            "No genuinely-open forks (manual triage)",
            state,
            False,
            detail,
        )
    )
    state, detail = _manual_signoff(
        "G1.8",
        "RB-CP-09 / RB-SUB-01/02 — operator ratify-or-build",
    )
    p.append(
        Pred(
            "G1.8",
            "FULL-SPEC: no unbuilt deferred/bounded-residual unratified",
            state,
            False,
            detail,
        )
    )

    # ---- Tier 2 — quality/close (from roadmap R-CL statuses) --------------- #
    for pid, rid, label in [
        ("G2.1", "R-CL-Q1", "DevEx + code-review + simplification"),
        ("G2.2", "R-CL-Q2", "security testing + review"),
        ("G2.3", "R-CL-Q3", "QA + 100%-evidence (coverage matrix)"),
        ("G2.4", "R-CL-Q4", "portable packaging + deployment"),
        ("G2.5", "R-CL-D1", "documentation suite"),
        ("G2.6", "R-CL-C1", "closure certification + ship"),
    ]:
        st = _roadmap_status(rid)
        p.append(Pred(pid, f"{rid} {label}", st == "RESOLVED", False, f"status={st}"))

    return p


# --------------------------------------------------------------------------- #
# Report
# --------------------------------------------------------------------------- #
def _glyph(pred: Pred) -> str:
    if pred.state is True:
        return "PASS"
    if pred.state is False:
        return "FAIL" if pred.auto else "OPEN"
    return "n/a "  # state None — manual/reported predicate, not auto-asserted


def report(preds: list[Pred]) -> None:
    print("Closure gate — harness-coding-fully-closed predicate")
    print(
        "  (spec: .harness/audit/Closure_Gate_v1.md; each predicate delegates to a live source)\n"
    )
    print("  TIER 1 — build-complete (gates R-FS-1):")
    for pred in preds:
        if pred.pid.startswith("G1"):
            tag = "auto" if pred.auto else "manual"
            print(f"    [{_glyph(pred):4}] {pred.pid} {pred.desc}  ({tag}: {pred.detail})")
    print("\n  TIER 2 — quality/close (gates R-CL-C1):")
    for pred in preds:
        if pred.pid.startswith("G2"):
            print(f"    [{_glyph(pred):4}] {pred.pid} {pred.desc}  ({pred.detail})")

    auto = [p for p in preds if p.auto]
    auto_fail = [p for p in auto if p.state is not True]
    t1_manual = [p for p in preds if p.pid.startswith("G1") and not p.auto]
    t1_manual_open = [p for p in t1_manual if p.state is not True]
    t1_manual_signed = len(t1_manual) - len(t1_manual_open)
    t2 = [p for p in preds if p.pid.startswith("G2")]
    t2_open = [p for p in t2 if p.state is not True]
    print("\n  ── verdict ──")
    print(f"    automatable Tier-1 predicates: {len(auto) - len(auto_fail)}/{len(auto)} PASS")
    print(f"    manual Tier-1 signed:           {t1_manual_signed}/{len(t1_manual)}")
    print(f"    Tier-2 phases RESOLVED:         {len(t2) - len(t2_open)}/{len(t2)}")
    if auto_fail or t1_manual_open or t2_open:
        print("    => NOT fully closed (build + quality/close work remains).")
    else:
        print(
            "    => build-complete AND quality/close signed — eligible for R-CL-C1 certification."
        )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Closure gate predicate checker.")
    ap.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if any AUTOMATABLE predicate fails (manual ones reported only)",
    )
    args = ap.parse_args(argv)
    preds = evaluate()
    report(preds)
    if args.check:
        auto_fail = [p for p in preds if p.auto and p.state is not True]
        if auto_fail:
            print(
                f"\nclosure-gate --check: {len(auto_fail)} automatable predicate(s) failing "
                f"({', '.join(p.pid for p in auto_fail)}) — not build-complete.",
                file=sys.stderr,
            )
            return 1
        t1_manual_open = [
            p for p in preds if p.pid.startswith("G1") and not p.auto and p.state is not True
        ]
        manual_msg = (
            "manual Tier-1 sign-offs still required"
            if t1_manual_open
            else "manual Tier-1 sign-offs recorded"
        )
        print(f"\nclosure-gate --check: all automatable predicates PASS ({manual_msg}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
