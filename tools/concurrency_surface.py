"""Concurrency-surface detector over unified-diff text (plan Task 6, Steps 1–4).

Reads a diff (`git diff -U0 <base>..<head>`) and reports whether ANY added or removed
content line names a construct the merge-gate concurrency lens reviews
(`.claude/skills/merge-gate/SKILL.md` Reviewer 1: shared state, TOCTOU on files, timeout /
cancellation, check-then-act, process isolation) plus the path-TOCTOU and module-global
shapes. Both sides of the diff count, so a deleted file, a removed lock and a shell or
workflow change are all surfaces.

The allowlist is FAIL-OPEN for any surface it does not name: a check-then-act spelled
without these calls, or a shared dict mutated through a method, reads as `false`. That
residual is the bound plan Task 6 Step 5 measures and the Step 6 spec leg must state; this
module makes no fail-closed claim. Empty, header-only or binary-only input is UNKNOWN, never
"no surface": it raises `EmptyDiff`, and the CLI exits 2 so the lens runs.

CLI: reads stdin, prints `concurrency=true|false`, exit 0; exit 2 with `run the lens` on
`EmptyDiff`. A consumer (the merge-gate skill step, only after plan Task 6 Step 6's C-HE-34
spec leg clears) may skip the lens on nothing but a literal `concurrency=false`.
"""

from __future__ import annotations

import re
import sys

# [LAW:one-type-per-behavior] the surface vocabulary is data: one tuple, one matcher.
# Deliberately absent: `await ` and bare `asyncio` — nearly every harness diff is async.
SURFACE_PATTERNS: tuple[str, ...] = (
    r"asyncio\.(gather|create_task|Lock|Semaphore|Queue|timeout|wait_for|shield)",
    r"CancelledError",
    r"\.cancel\(",
    r"TimeoutError",
    r"threading",
    r"multiprocessing",
    r"concurrent\.futures",
    r"fcntl",
    r"flock",
    r"os\.link",
    r"O_EXCL",
    r"subprocess\.Popen",
    r"Lock\(",
    r"Semaphore\(",
    r"\.exists\(\)",
    r"\.is_file\(\)",
    r"os\.path\.exists",
    r"\.unlink\(",
    r"os\.remove",
    r"os\.rename",
    r"os\.replace",
    r"global ",
    r"nonlocal ",
    # GitHub Actions concurrency groups and in-progress cancellation (codex r1 P2 on this arc)
    r"concurrency:",
    r"cancel-in-progress:",
)
_SURFACE = re.compile("|".join(f"(?:{p})" for p in SURFACE_PATTERNS))

# A git diff header, not a content line. Only the git shapes count so that a removed content
# line whose text begins "-- " (rendered "--- ...") stays a content line.
_HEADER = re.compile(r"^(\+\+\+|---) (a/|b/|/dev/null)")


class EmptyDiff(ValueError):  # noqa: N818 — B-230 Task 6 plan signature verbatim
    """The input carries no `+`/`-` content line: the surface is unknown, not absent."""


def content_lines(diff: str) -> list[str]:
    """The added and removed lines of a unified diff, marker stripped. Raises `EmptyDiff`
    when there are none (empty, header-only, or binary-only input)."""
    lines = [
        line[1:] for line in diff.splitlines() if line[:1] in ("+", "-") and not _HEADER.match(line)
    ]
    if not lines:
        raise EmptyDiff("no added or removed content lines")
    return lines


def surface_hits(diff: str) -> tuple[str, ...]:
    """Every content line that names a surface, in diff order (empty = no named surface)."""
    return tuple(line for line in content_lines(diff) if _SURFACE.search(line))


def touches_concurrency(diff: str) -> bool:
    """True when any added or removed line names a construct on the allowlist."""
    return bool(surface_hits(diff))


def main() -> int:
    # [LAW:effects-at-boundaries] stdin, stdout and the exit code live here only.
    try:
        verdict = touches_concurrency(sys.stdin.read())
    except EmptyDiff as exc:
        print(f"run the lens: {exc}")
        return 2
    print(f"concurrency={'true' if verdict else 'false'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
