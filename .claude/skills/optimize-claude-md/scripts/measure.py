#!/usr/bin/env python3
"""measure.py — CLAUDE.md governance-portfolio measurer for the optimize-claude-md skill.

WHY THIS EXISTS
    Every session loads the workspace CLAUDE.md files into context. When they bloat, the
    cost is paid on *every* turn of *every* session — so the first job of any optimization
    pass is to see, precisely, where the bytes are. This script does that once, the same
    way each time, so the skill never re-derives an ad-hoc `awk` and never optimizes blind.

WHAT IT REPORTS
    For each tracked governance CLAUDE.md: bytes, estimated tokens, lines, and the gap to
    its ICM context-budget target. Then, for the worst offenders, *where* the weight sits —
    a per-section byte breakdown and the longest individual lines — because in practice a
    handful of history-laden tables carry most of the file, and those are what you relocate.

SCOPE IS ENFORCED, NOT ASSUMED
    The governance set is whatever `git ls-files` returns named CLAUDE.md. git naturally
    omits gitignored paths, so vendored (ICM) and skill-bundled CLAUDE.md files are excluded
    mechanically — the same scope-guard the skill states as a hard invariant. Outside a git
    repo (e.g. an eval sandbox working on a copy) it falls back to a filesystem scan, or you
    can point it straight at one file with --file.

ICM BUDGET TARGETS  (source: ICM_Alignment_Audit_v1.md §3 / §5; token estimate = bytes / 4,
the audit's own method, so numbers reconcile with the audit)
    L0  repo-root CLAUDE.md ............ ~800 tokens
    L2  per-axis subdir CLAUDE.md ...... 200-500 tokens   (the audit's "L2-analog")

    These are DIAGNOSTIC targets that frame the gap. They are NOT truncation gates. The
    audit is explicit: "a naive 'shrink to 800 tokens' would destroy a load-bearing
    governance system." Reconcile, don't teardown. --check exits non-zero ONLY if asked.

USAGE
    python measure.py                     # report the whole tracked portfolio
    python measure.py --root /path/repo   # measure a specific repo root
    python measure.py --file CLAUDE.md    # measure one explicit file (eval sandbox)
    python measure.py --json              # machine-readable (for the sweep mode / CI)
    python measure.py --top 15            # show the N longest lines per offender (default 8)
    python measure.py --check             # exit 1 if any file is over target (opt-in gate)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

L0_TARGET = 800  # tokens — repo-root CLAUDE.md (ICM L0)
L2_TARGET_LO = 200  # tokens — per-axis subdir CLAUDE.md (ICM L2-analog)
L2_TARGET_HI = 500
BYTES_PER_TOKEN = 4  # ICM audit convention (B/4)
HOTSPOT_LINE_CHARS = 1000  # a line longer than this is a relocation candidate


def discover(root: str) -> tuple[list[str], str]:
    """Return (relative CLAUDE.md paths, source-label). git-tracked first; FS-scan fallback."""
    try:
        out = subprocess.run(
            ["git", "-C", root, "ls-files"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        files = sorted(p for p in out.splitlines() if os.path.basename(p) == "CLAUDE.md")
        if files:
            return files, "git-tracked"
    except Exception:
        pass
    # Fallback: scan, skipping the dirs that hold vendored / bundled / build artifacts.
    skip = {
        ".git",
        "node_modules",
        ".venv",
        "__pycache__",
        ".claude",
        "ai-docs",
        "dashboard-design",
        "dist",
        "build",
    }
    found = []
    for dp, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip]
        if "CLAUDE.md" in filenames:
            found.append(os.path.relpath(os.path.join(dp, "CLAUDE.md"), root))
    return sorted(found), "fs-scan"


def kind_of(relpath: str) -> str:
    """L0 = repo-root CLAUDE.md; everything else is an L2-analog governance pointer."""
    return "L0" if relpath in ("CLAUDE.md", "./CLAUDE.md") else "L2"


def target_str(kind: str) -> str:
    return f"~{L0_TARGET}" if kind == "L0" else f"{L2_TARGET_LO}-{L2_TARGET_HI}"


def over_ratio(tokens: int, kind: str) -> float:
    """How many times over the (upper) target a file sits. <1.0 means within budget."""
    hi = L0_TARGET if kind == "L0" else L2_TARGET_HI
    return tokens / hi if hi else 0.0


def analyze(abspath: str, top: int) -> dict:
    with open(abspath, "rb") as fh:
        raw = fh.read()
    text = raw.decode("utf-8", errors="replace")
    lines = text.split("\n")
    # `split("\n")` yields a trailing "" when the file ends in a newline; count lines the
    # way `wc -l` does (newline-terminated) so the report reconciles with shell tools.
    nlines = len(text.splitlines())

    # Walk lines once: track the enclosing top-level "## " section, tally bytes per section,
    # and collect the longest lines. Byte cost of a line = its UTF-8 length + 1 (the newline).
    section = "(preamble)"
    section_bytes: dict[str, int] = {}
    section_order: list[str] = []
    long_lines: list[tuple[int, int, str]] = []  # (1-based lineno, char-length, section)
    big_count = 0
    big_bytes = 0
    for idx, ln in enumerate(lines):
        stripped = ln.lstrip()
        if stripped.startswith("## ") and not stripped.startswith("###"):
            section = ln.strip()
            if section not in section_bytes:
                section_order.append(section)
        cost = len(ln.encode("utf-8")) + 1
        section_bytes[section] = section_bytes.get(section, 0) + cost
        if len(ln) >= HOTSPOT_LINE_CHARS:
            big_count += 1
            big_bytes += cost
        long_lines.append((idx + 1, len(ln), section))

    long_lines.sort(key=lambda t: t[1], reverse=True)
    nbytes = len(raw)
    sections_sorted = sorted(section_bytes.items(), key=lambda kv: kv[1], reverse=True)
    return {
        "bytes": nbytes,
        "tokens": nbytes // BYTES_PER_TOKEN,
        "lines": nlines,
        "sections": [(name, b, round(100 * b / nbytes, 1)) for name, b in sections_sorted],
        "hotspots": long_lines[:top],
        "big_count": big_count,
        "big_bytes": big_bytes,
        "big_pct": round(100 * big_bytes / nbytes, 1) if nbytes else 0.0,
    }


def human(n: int) -> str:
    return f"{n:,}"


def collect(files: list[tuple[str, str]], top: int) -> list[dict]:
    rows = []
    for rel, ab in files:
        kind = kind_of(rel)
        a = analyze(ab, top)
        rows.append({"path": rel, "kind": kind, "ratio": over_ratio(a["tokens"], kind), **a})
    return rows


def print_report(rows: list[dict], source: str) -> None:
    total_tokens = sum(r["tokens"] for r in rows)
    print(f"\nCLAUDE.md governance portfolio  ({source}, {len(rows)} files)")
    print("=" * 72)
    print(f"{'FILE':<34}{'KIND':<5}{'TOKENS':>9}  {'TARGET':>8}  {'STATUS'}")
    print("-" * 72)
    for r in sorted(rows, key=lambda x: x["tokens"], reverse=True):
        status = (
            f"{r['ratio']:.0f}x OVER" if r["ratio"] >= 1.5 else "OVER" if r["ratio"] > 1.0 else "ok"
        )
        print(
            f"{r['path']:<34}{r['kind']:<5}{human(r['tokens']):>9}  "
            f"{target_str(r['kind']):>8}  {status}"
        )
    print("-" * 72)
    print(
        f"{'TOTAL always-loaded governance':<34}{'':<5}{human(total_tokens):>9}"
        f"  tokens across {len(rows)} files\n"
    )

    for r in sorted(rows, key=lambda x: x["tokens"], reverse=True):
        if r["ratio"] <= 1.0:
            continue
        print(
            f"v {r['path']}  —  {human(r['bytes'])} B / ~{human(r['tokens'])} tok / "
            f"{r['lines']} lines"
        )
        if r["big_count"]:
            print(
                f"  {r['big_count']} line(s) over {HOTSPOT_LINE_CHARS} chars carry "
                f"{human(r['big_bytes'])} B = {r['big_pct']}% of the file "
                f"(relocate these first)"
            )
        print("  Heaviest sections:")
        for name, b, pct in r["sections"][:6]:
            bar = "#" * max(1, round(pct / 4))
            print(f"    {pct:>5.1f}%  {human(b):>9} B  {bar} {name}")
        print("  Longest lines:")
        for lineno, length, sec in r["hotspots"]:
            print(f"    L{lineno:<5} {human(length):>8} chars   in {sec}")
        print()


def to_payload(rows: list[dict], source: str) -> dict:
    return {
        "source": source,
        "total_tokens": sum(r["tokens"] for r in rows),
        "files": [
            {
                "path": r["path"],
                "kind": r["kind"],
                "ratio": round(r["ratio"], 2),
                "bytes": r["bytes"],
                "tokens": r["tokens"],
                "lines": r["lines"],
                "big_count": r["big_count"],
                "big_bytes": r["big_bytes"],
                "big_pct": r["big_pct"],
                "sections": [{"name": n, "bytes": b, "pct": p} for n, b, p in r["sections"]],
                "hotspots": [{"line": ln, "chars": c, "section": s} for ln, c, s in r["hotspots"]],
            }
            for r in rows
        ],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Measure CLAUDE.md governance context cost.")
    ap.add_argument("--root", default=None, help="repo root (default: git toplevel of CWD, else .)")
    ap.add_argument(
        "--file", action="append", default=[], help="measure one explicit file (repeatable)"
    )
    ap.add_argument("--top", type=int, default=8, help="longest lines to show per offender")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of the human report")
    ap.add_argument("--check", action="store_true", help="exit 1 if any file is over target")
    args = ap.parse_args(argv)

    if args.file:
        files = [(os.path.relpath(f), os.path.abspath(f)) for f in args.file]
        source = "explicit"
    else:
        root = args.root
        if root is None:
            try:
                root = (
                    subprocess.run(
                        ["git", "rev-parse", "--show-toplevel"],
                        capture_output=True,
                        text=True,
                        check=True,
                    ).stdout.strip()
                    or "."
                )
            except Exception:
                root = "."
        rels, source = discover(root)
        files = [(rel, os.path.join(root, rel)) for rel in rels]

    files = [(rel, ab) for rel, ab in files if os.path.isfile(ab)]
    if not files:
        print("no CLAUDE.md governance files found", file=sys.stderr)
        return 2

    rows = collect(files, args.top)
    if args.json:
        print(json.dumps(to_payload(rows, source), indent=2))
    else:
        print_report(rows, source)

    if args.check:
        over = [r for r in rows if r["ratio"] > 1.0]
        if over:
            print(f"[check] {len(over)} file(s) over ICM target", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
