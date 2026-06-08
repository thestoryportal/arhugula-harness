#!/usr/bin/env python3
"""Extract the loop's fitness score from a promptfoo out.json (deterministic, no model call).

The self-improvement loop's keep/discard decision uses TWO numbers from here:
  - hard_gates_all_pass: every HARD gate (guardrails_preserved, pointers_resolve,
    scope_only_governance) passed on EVERY test. This is a VETO — a change that fails any hard
    gate is NEVER kept, no matter what the pass-rate does (loop-level anti-Goodhart, mirroring
    the assertion-level gates).
  - score: the weighted aggregate (mean of per-test promptfoo scores). Compared
    iteration-over-iteration; keep the change only if hard_gates_all_pass AND score strictly
    improved over the last kept score.
Also reports the assertion pass-rate + any failing assertions, for the iteration log.

Usage: python3 score.py [out.json]   (default: out.json in CWD)
Prints a one-line JSON summary to stdout.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Metric names (from promptfooconfig.yaml) whose failure must VETO keeping a change.
_HARD_GATES = {"guardrails", "pointers", "scope"}


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "out.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    results = data["results"]["results"]
    total = passed = 0
    hard_all = True
    fails: list[str] = []
    scores: list[float] = []
    for r in results:
        case = (r.get("vars") or {}).get("case", "?")
        scores.append(float(r.get("score") or 0.0))
        for c in r.get("gradingResult", {}).get("componentResults", []) or []:
            metric = (c.get("assertion") or {}).get("metric", "?")
            ok = bool(c.get("pass"))
            total += 1
            passed += int(ok)
            if not ok:
                fails.append(f"{case}:{metric}")
                if metric in _HARD_GATES:
                    hard_all = False
    summary = {
        "hard_gates_all_pass": hard_all,
        "score": round(sum(scores) / len(scores), 4) if scores else 0.0,
        "pass_rate": round(passed / total, 4) if total else 0.0,
        "passed": passed,
        "total": total,
        "fails": fails,
    }
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
