#!/usr/bin/env python3
"""B-230 Task 1 — classify a CI diff as bookkeeping-only.

`python3 tools/ci_bookkeeping_diff.py <base-sha> <head-sha>` prints exactly one line,
`bookkeeping=true` or `bookkeeping=false`, for the `changes` job in
`.github/workflows/ci.yml` to append to `$GITHUB_OUTPUT`. A diff is bookkeeping when
every changed path is one the loop's own machinery writes — the roadmap status pointer
(a terminating refresh PR and its merge push onto `main`) or the two merge-gate log
siblings (the gate-rows head) — and only on such a diff may the heavy jobs skip. The
gate emitter writes the JSONL row and its Markdown sibling together, so a JSONL change
WITHOUT the Markdown sibling is the emitter's warn-on-markdown-failure shape (C-HE-23 §2),
not the normal gate-rows head: it takes the full run (codex r1 P2 on b-230-task-1). A
Markdown-only change is `reconcile` re-emitting the derived view and stays bookkeeping;
the consistency job fails a Markdown row with no JSONL authority.

The workflow, not this script, refuses the fast path when the diff touches this file or
`ci.yml` itself: a classifier executed from the PR head cannot be trusted to judge a
change to itself (codex r1 P1 on b-230-task-1) — on an unchanged classifier, head and
base bytes are identical, so running from head is running from base.

Exit codes are the contract: 0 = classified (the line is on stdout); 2 = nothing could be
classified (an empty diff, or git could not resolve the range) with the cause on stderr
and NOTHING on stdout, so no partial line reaches `$GITHUB_OUTPUT`. The gated jobs'
`always()` turns that failure into a full run — an unclassifiable diff is a broken input,
never a licence to skip.

Stdlib only ON PURPOSE: the `changes` job runs under the runner's `/usr/bin/python3` with
no uv setup so it finishes in seconds. The two path sets have owners elsewhere —
`merge_gate_log.GATE_ROW_FILES` and `roadmap_status_refresh._REFRESH_ONLY_FILE_SET` —
which this module cannot import without dragging in their non-stdlib siblings; the copy
here is fenced by the subset assertions in `test_ci_bookkeeping_filter.py`.
"""

from __future__ import annotations

import subprocess
import sys

# [LAW:one-source-of-truth] exception: a fenced copy — the owners are not importable
# from a stdlib-only process; test_ci_bookkeeping_filter.py asserts owners ⊆ this set.
GATE_LOG_JSONL = ".harness/merge-gate-log.jsonl"
GATE_LOG_MD = ".harness/merge-gate-log.md"
BOOKKEEPING_PATHS: frozenset[str] = frozenset(
    {".harness/roadmap_status.md", GATE_LOG_JSONL, GATE_LOG_MD}
)


def classify(paths: list[str]) -> bool:
    """True iff every changed path is a bookkeeping file and a gate-log JSONL change
    carries its Markdown sibling. Raises on an empty list."""
    # [LAW:parse-dont-validate] an empty diff is not "no non-bookkeeping files" — it is
    # an input the caller cannot have meant; raise rather than answer.
    if not paths:
        raise ValueError("empty diff: nothing to classify")
    changed = set(paths)
    lone_jsonl = GATE_LOG_JSONL in changed and GATE_LOG_MD not in changed
    return changed <= BOOKKEEPING_PATHS and not lone_jsonl


def changed_paths(base: str, head: str) -> list[str]:
    """Paths changed on `base...head` (merge-base to head: the PR's own changes)."""
    # [LAW:effects-at-boundaries] the one git read; classify() stays pure.
    # --no-renames: with rename detection a `src/x.py -> .harness/roadmap_status.md`
    # rename would list only the destination and classify as bookkeeping; without it
    # both the deletion and the addition appear.
    out = subprocess.run(
        ["git", "diff", "--name-only", "--no-renames", f"{base}...{head}"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return [line for line in out.splitlines() if line]


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: ci_bookkeeping_diff.py <base-sha> <head-sha>", file=sys.stderr)
        return 2
    base, head = argv
    # [LAW:no-silent-failure] both failure arms are loud, on stderr, and leave stdout
    # empty — exit 2 is the "could not classify" contract the workflow relies on.
    try:
        verdict = classify(changed_paths(base, head))
    except subprocess.CalledProcessError as e:
        print(
            f"ci_bookkeeping_diff: git diff failed for {base}...{head}: {e.stderr.strip()}",
            file=sys.stderr,
        )
        return 2
    except ValueError as e:
        print(f"ci_bookkeeping_diff: {e} ({base}...{head})", file=sys.stderr)
        return 2
    print(f"bookkeeping={'true' if verdict else 'false'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
