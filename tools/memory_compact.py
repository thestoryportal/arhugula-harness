#!/usr/bin/env python3
"""Deterministic gate + idempotent upsert for the auto-memory `MEMORY.md` index.

`MEMORY.md` (at `~/.claude/projects/<project-slug>/memory/MEMORY.md`) has a hard
24,400-byte cap per workspace `CLAUDE.md` §14. This script is NOT a semantic
compactor — it cannot judge which memory entries are stale, that stays the
agent's call. What it makes deterministic instead of hand-measured/hand-edited:

  * exact byte-size measurement (kills the "let me count roughly" failure mode
    that caused iterative, error-prone Edit passes)
  * idempotent index-line upsert keyed by the markdown link target
    (`[Title](slug.md)` — re-running with the same slug replaces, never
    duplicates)
  * a HARD gate: `--upsert` refuses to write if the resulting file would
    exceed the cap, printing the overage and headroom instead — the agent
    trims (drops/shortens other lines) and retries, rather than silently
    landing an over-cap file

Usage:
    python tools/memory_compact.py --measure MEMORY.md
    python tools/memory_compact.py --check MEMORY.md [--cap 24400] [--warn-ratio 0.9]
    python tools/memory_compact.py --upsert MEMORY.md --slug my-topic \\
        --line "- [My Topic](my-topic.md) — one-line hook" [--cap 24400]
    python tools/memory_compact.py --remove MEMORY.md --slug my-topic
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CAP = 24_400
DEFAULT_WARN_RATIO = 0.9

# An index bullet line: "- [Title](slug.md) — hook text" (any leading "- ").
_LINK_RE = re.compile(r"^-\s*\[[^\]]*\]\(([^)]+)\)")


class MemoryCompactError(ValueError):
    pass


def measure_bytes(path: Path) -> int:
    return len(path.read_bytes())


@dataclass(frozen=True)
class CapReport:
    size: int
    cap: int
    warn_ratio: float

    @property
    def over(self) -> bool:
        return self.size > self.cap

    @property
    def headroom(self) -> int:
        return self.cap - self.size

    @property
    def warn(self) -> bool:
        return self.size >= int(self.cap * self.warn_ratio)

    def as_text(self) -> str:
        pct = 100.0 * self.size / self.cap if self.cap else 0.0
        status = "OVER CAP" if self.over else ("WARN — near cap" if self.warn else "OK")
        return f"{self.size}/{self.cap} bytes ({pct:.1f}%) — {status} — headroom={self.headroom}"


def check_cap(
    path: Path, cap: int = DEFAULT_CAP, warn_ratio: float = DEFAULT_WARN_RATIO
) -> CapReport:
    return CapReport(size=measure_bytes(path), cap=cap, warn_ratio=warn_ratio)


def _slug_target(slug: str) -> str:
    return slug if slug.endswith(".md") else f"{slug}.md"


def _find_line_index(lines: list[str], slug: str) -> int | None:
    target = _slug_target(slug)
    for i, line in enumerate(lines):
        m = _LINK_RE.match(line.strip())
        if m and m.group(1) == target:
            return i
    return None


def upsert_line_text(text: str, slug: str, new_line: str) -> str:
    """Idempotent: a line already linking to `{slug}.md` is replaced in place
    (preserving position); otherwise the new line is appended at the end of
    the file (after a trailing blank line if the file doesn't already end in
    one)."""
    new_line = new_line.rstrip("\n")
    lines = text.splitlines()
    idx = _find_line_index(lines, slug)
    if idx is not None:
        if lines[idx] == new_line:
            return text  # already-applied no-op
        lines[idx] = new_line
        return "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    lines.append(new_line)
    return "\n".join(lines) + "\n"


def remove_line_text(text: str, slug: str) -> str:
    lines = text.splitlines()
    idx = _find_line_index(lines, slug)
    if idx is None:
        return text  # already-absent no-op
    del lines[idx]
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


# --- CLI ------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="MEMORY.md byte-cap gate + idempotent index upsert.")
    ap.add_argument(
        "path",
        nargs="?",
        type=Path,
        help="path to MEMORY.md (positional, or via a flag's own path)",
    )
    ap.add_argument("--measure", type=Path, help="print exact byte size of PATH and exit")
    ap.add_argument("--check", type=Path, help="print a cap report for PATH; exit 1 if over cap")
    ap.add_argument("--upsert", type=Path, help="idempotent upsert into PATH's index")
    ap.add_argument("--remove", type=Path, help="idempotent removal from PATH's index")
    ap.add_argument("--slug", help="the memory slug (matches [Title](slug.md))")
    ap.add_argument("--line", help="the full index line text for --upsert")
    ap.add_argument("--cap", type=int, default=DEFAULT_CAP)
    ap.add_argument("--warn-ratio", type=float, default=DEFAULT_WARN_RATIO)
    ap.add_argument("--dry-run", action="store_true", help="report what would happen; do not write")
    args = ap.parse_args(argv)

    if args.measure:
        print(measure_bytes(args.measure))
        return 0

    if args.check:
        report = check_cap(args.check, args.cap, args.warn_ratio)
        print(report.as_text())
        return 1 if report.over else 0

    if args.upsert:
        if not (args.slug and args.line):
            ap.error("--upsert requires --slug and --line")
        text = args.upsert.read_text()
        new_text = upsert_line_text(text, args.slug, args.line)
        new_size = len(new_text.encode("utf-8"))
        if new_size > args.cap:
            print(
                f"REFUSED — writing {args.slug!r} would put MEMORY.md at "
                f"{new_size}/{args.cap} bytes (over by {new_size - args.cap}). "
                "Trim an existing entry first, then retry.",
                file=sys.stderr,
            )
            return 1
        if args.dry_run:
            print(f"would write: {new_size}/{args.cap} bytes")
            return 0
        if new_text != text:
            args.upsert.write_text(new_text)
        report = CapReport(size=new_size, cap=args.cap, warn_ratio=args.warn_ratio)
        print(f"upserted {args.slug!r} — {report.as_text()}")
        return 0

    if args.remove:
        if not args.slug:
            ap.error("--remove requires --slug")
        text = args.remove.read_text()
        new_text = remove_line_text(text, args.slug)
        if args.dry_run:
            changed = new_text != text
            print(f"would remove {args.slug!r}: {'found' if changed else 'not found (no-op)'}")
            return 0
        if new_text != text:
            args.remove.write_text(new_text)
        print(f"removed {args.slug!r}")
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
