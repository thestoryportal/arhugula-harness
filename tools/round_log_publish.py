#!/usr/bin/env python3
"""Publish a review round log under .harness/tmp/ with symlink-proof containment.

Reads stdin, echoes it to stdout (tee behavior for the live transcript), and writes
the bytes to the destination via an O_NOFOLLOW dir-fd walk from the repo root:
every path component is opened relative to the previous component's fd and refuses
a symlink AT ITS OWN openat, so neither a pre-planted symlink nor a parent
directory swapped mid-flight can route the write outside the worktree (U-HE-34
codex r7 P1 — the check-then-act gap a pathname-based pre-check cannot close; same
idiom as the review_loop_gate/finding_record state writes). The destination policy
is part of the containment: only a relative path under .harness/tmp/ is writable
through this tool, so an auto-allowed invocation can never target a tracked source
file or ledger.

Exit 0 on success; 2 on usage error; 4 on a refused destination. Stdout mirrors
stdin even when the write is refused, so the caller still sees the transcript.
"""

from __future__ import annotations

import os
import sys

_O_DIR = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


def _refuse(msg: str) -> int:
    # the transcript still flows to stdout so a refused publish never eats the verdict
    print(f"round_log_publish: {msg}", file=sys.stderr)
    for chunk in iter(lambda: sys.stdin.buffer.read(65536), b""):
        sys.stdout.buffer.write(chunk)
        sys.stdout.buffer.flush()
    return 4


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: round_log_publish.py .harness/tmp/<...>.log", file=sys.stderr)
        return 2
    rel = args[0]
    parts = rel.split("/")
    if (
        rel.startswith("/")
        or ".." in parts
        or "" in parts
        or parts[:2] != [".harness", "tmp"]
        or len(parts) < 3
    ):
        return _refuse(
            f"refused destination {rel!r} -- must be a relative path under .harness/tmp/"
        )
    fd = os.open(".", _O_DIR)
    try:
        for comp in parts[:-1]:
            try:
                nxt = os.open(comp, _O_DIR, dir_fd=fd)
            except FileNotFoundError:
                try:
                    os.mkdir(comp, dir_fd=fd)
                except FileExistsError:
                    pass  # a concurrent lane won the mkdir -- the open below adjudicates
                try:
                    nxt = os.open(comp, _O_DIR, dir_fd=fd)
                except OSError as exc:
                    return _refuse(f"refused component {comp!r} in {rel!r}: {exc}")
            except OSError as exc:  # ELOOP (symlink) / ENOTDIR (regular file) / perms
                return _refuse(f"refused component {comp!r} in {rel!r}: {exc}")
            os.close(fd)
            fd = nxt
        try:
            out = os.open(
                parts[-1],
                os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW,
                0o644,
                dir_fd=fd,
            )
        except OSError as exc:  # ELOOP: pre-planted leaf symlink
            return _refuse(f"refused leaf {parts[-1]!r} in {rel!r}: {exc}")
        with os.fdopen(out, "wb") as sink:
            for chunk in iter(lambda: sys.stdin.buffer.read(65536), b""):
                sink.write(chunk)
                sys.stdout.buffer.write(chunk)
                sys.stdout.buffer.flush()
    finally:
        os.close(fd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
