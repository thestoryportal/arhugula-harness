#!/usr/bin/env python3
"""Re-cluster the live gate log against the skill's defect classes.

The checklist in SKILL.md is a distilled map of `.harness/merge-gate-log.jsonl`;
the log is the one authority and only grows. This prints (a) current per-class
counts — compare them to the counts baked into SKILL.md and refresh the text when
they have moved meaningfully — and (b) the most recent findings that match NO
known class: those are candidates for a new class, surfaced mechanically instead
of waiting for recall. Advisory by design: always exits 0, output is for the
agent running the preflight, never a gate.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# One definition per class, mirroring SKILL.md's ten sections. When a class is
# added or reworded there, extend this table in the same commit (the counts the
# skill cites are derived HERE, so a drifted table silently mis-buckets).
CLASSES: dict[str, str] = {
    "1 race / TOCTOU / atomicity / lock": (
        r"race|TOCTOU|atomic|lock|flock|concurrent|interleav|CAS|exclusive"
    ),
    "2 prose stale / counts / cites": (
        r"stale|close_out|mis-cite|cite|count|narrat|docstring claim|partition"
    ),
    "3 silent failure / fallback": (
        r"swallow|silent|fallback|2>/dev/null|\|\| true|exit code|ignored error"
    ),
    "4 vacuous witness": (
        r"witness|vacuous|stays green|cannot fail|only .*presence|never red"
        r"|does not red|remains green|unexercised"
    ),
    "5 timeout / retry / budget": r"timeout|retry|budget|backoff|deadline",
    "6 unreachable / dead branch": (
        r"unreachable|dead|never reach|no witness could|half-dead|cannot see|restore arm"
    ),
    "7 env-var mutation / restore": (r"monkeypatch|os\.environ|env var|setenv|restore|undo\(\)"),
    "8 subprocess boundary": (r"subprocess|child process|inherit|process boundary|spawns|nested"),
    "9 path / default resolution": (
        r"fallback ledger|venue|QUEUE_DIR|path default|resolves|home default|\$HOME"
    ),
    "10 fixture scope / lifecycle": (
        r"session-scoped|module-scoped|function-scoped|teardown|collection|autouse|fixture"
    ),
}


def main() -> int:
    log = Path(__file__).resolve().parents[3].parent / ".harness" / "merge-gate-log.jsonl"
    if not log.exists():
        # Fallback: resolve from the repo root when the skill is invoked from cwd.
        log = Path(".harness/merge-gate-log.jsonl")
    if not log.exists():
        print(f"refresh-classes: gate log not found at {log} — run from the repo root")
        return 0

    rows = []
    malformed = 0
    for lineno, line in enumerate(log.read_text().splitlines(), start=1):
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            # A damaged row silently dropped would understate counts while the
            # output still reads authoritative — report it and mark the result
            # incomplete below (no-silent-failure; codex round 2 on this PR).
            malformed += 1
            print(f"refresh-classes: WARNING malformed JSONL at line {lineno} — skipped")
            continue
        # Real findings only, by the log's own discriminator: record_kind. A severity
        # filter is NOT a finding filter — it drops warn-severity findings while
        # admitting hard-severity infrastructure rows, skewing the counts this file
        # claims to derive (codex round 1 on the skills PR measured the mismatch).
        if r.get("observed_evidence") and r.get("record_kind", "finding") == "finding":
            rows.append(r)

    counts = dict.fromkeys(CLASSES, 0)
    unmatched = []
    for r in rows:
        text = (r.get("observed_evidence") or "") + " " + (r.get("location") or "")
        hit = False
        for name, pat in CLASSES.items():
            if re.search(pat, text, re.I):
                counts[name] += 1
                hit = True
        if not hit:
            unmatched.append(r)

    status = f" (INCOMPLETE — {malformed} malformed row(s) skipped)" if malformed else ""
    print(f"refresh-classes: {len(rows)} findings in {log}{status}")
    print("\nPer-class counts (multi-match rows count in every class they touch):")
    for name, n in counts.items():
        print(f"  {n:5}  {name}")

    print(f"\nUnmatched findings (new-class candidates): {len(unmatched)}")
    for r in unmatched[-10:]:
        ev = (r.get("observed_evidence") or "").replace("\n", " ")[:150]
        print(f"  {r.get('ts', '')[:10]} {r.get('severity', '?'):3} {r.get('location', '')[:50]}")
        print(f"      {ev}")
    if unmatched:
        print(
            "\nEach unmatched finding is a candidate: either extend an existing class's"
            " pattern (here AND in SKILL.md) or add a new class in both places."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
