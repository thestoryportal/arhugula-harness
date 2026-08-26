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
        # Exclusively-created temp inode + atomic LINK install (codex r8/r9 P1/P2):
        # O_NOFOLLOW stops symlinks but not HARD links -- O_TRUNC on a pre-planted
        # leaf hard-linked to a tracked file would destroy that file's content, and a
        # rename over an existing round log would silently discard a transcript the
        # gate log still counts (last-writer-wins on replay). O_EXCL guarantees a
        # fresh inode nothing else links; link() then installs the directory entry
        # ONLY if the name is free -- EEXIST is an atomic refusal, so round logs are
        # write-once evidence and any pre-planted entry (symlink, hard link, file)
        # is left untouched.
        tmp_name = f".{parts[-1]}.{os.getpid()}.{os.urandom(8).hex()}.tmp"
        try:
            out = os.open(
                tmp_name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                0o644,
                dir_fd=fd,
            )
        except OSError as exc:
            return _refuse(f"refused temp {tmp_name!r} in {rel!r}: {exc}")
        try:
            with os.fdopen(out, "wb") as sink:
                for chunk in iter(lambda: sys.stdin.buffer.read(65536), b""):
                    sink.write(chunk)
                    sys.stdout.buffer.write(chunk)
                    sys.stdout.buffer.flush()
                sink.flush()
                written = os.fstat(sink.fileno())
            try:
                os.link(tmp_name, parts[-1], src_dir_fd=fd, dst_dir_fd=fd)
            except FileExistsError:
                os.unlink(tmp_name, dir_fd=fd)
                return _refuse(
                    f"refused {rel!r}: destination already exists -- round logs are "
                    "write-once evidence; use a fresh per-round name"
                )
            os.unlink(tmp_name, dir_fd=fd)
            # link(2) resolves the temp NAME, not the inode we wrote (codex r10): a
            # concurrent unlink+replace of the (already unpredictable) temp name
            # between write and link would install a foreign inode under our name.
            # Verify the installed entry IS the written inode; on mismatch, remove
            # the entry we just created and refuse loud.
            check = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=fd)
            try:
                installed = os.fstat(check)
            finally:
                os.close(check)
            if (installed.st_dev, installed.st_ino) != (written.st_dev, written.st_ino):
                os.unlink(parts[-1], dir_fd=fd)
                return _refuse(
                    f"refused {rel!r}: installed inode is not the written one -- "
                    "temp name was swapped mid-publish"
                )
        except OSError as exc:
            try:
                os.unlink(tmp_name, dir_fd=fd)
            except OSError:
                print(f"round_log_publish: temp {tmp_name!r} left behind", file=sys.stderr)
            # _refuse also drains the remaining transcript to stdout -- a mid-copy
            # disk failure must not eat the verdict tail either
            return _refuse(f"publish of {rel!r} failed: {exc}")
    finally:
        os.close(fd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
