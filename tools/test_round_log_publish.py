"""Round-log publisher containment tests (U-HE-34 codex r7).

The property under test is fail-closed containment: the publisher must refuse any
destination outside .harness/tmp/ and any path whose components can route the write
elsewhere (symlink leaf, symlink parent) -- while ALWAYS mirroring stdin to stdout so
a refused publish never eats the reviewer transcript. Mutation probes noted per test.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

TOOL = Path(__file__).resolve().parent / "round_log_publish.py"


def run(dest: str, cwd: Path, payload: bytes = b"verdict\n") -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(TOOL), dest],
        input=payload,
        capture_output=True,
        cwd=cwd,
    )


def test_happy_path_writes_and_mirrors(tmp_path):
    """Mutation probe: drop the sink write -> file empty, reds."""
    proc = run(".harness/tmp/u-x-rounds/r1.log", tmp_path)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout == b"verdict\n"
    assert (tmp_path / ".harness/tmp/u-x-rounds/r1.log").read_bytes() == b"verdict\n"


def test_refuses_destinations_outside_harness_tmp(tmp_path):
    """The destination policy IS the containment half the guard mirrors: a tracked
    file or ledger must be unreachable through an auto-allowed invocation.
    Mutation probe: drop the prefix check -> tools/x.py is written, reds."""
    (tmp_path / "tools").mkdir()
    for dest in (
        "tools/x.py",
        ".harness/merge-gate-log.jsonl",
        "/etc/x.log",
        ".harness/tmp/../../x.log",
        ".harness/tmp",
        ".harness/tmp/",
    ):
        proc = run(dest, tmp_path)
        assert proc.returncode == 4, dest
        # the transcript still reaches stdout on refusal -- a refused publish must
        # never eat the verdict
        assert proc.stdout == b"verdict\n", dest
    assert not (tmp_path / "tools" / "x.py").exists()


def test_symlink_leaf_refused_target_untouched(tmp_path):
    """A pre-planted leaf symlink is an EXISTING entry: the link() install refuses it
    atomically (write-once), the target is never opened, and the entry is untouched.
    Mutation probe: install with rename instead of link -> returncode 0, reds."""
    d = tmp_path / ".harness/tmp/rounds"
    d.mkdir(parents=True)
    outside = tmp_path / "outside-target"
    outside.write_bytes(b"precious")
    (d / "r1.log").symlink_to(outside)
    proc = run(".harness/tmp/rounds/r1.log", tmp_path)
    assert proc.returncode == 4
    assert proc.stdout == b"verdict\n", "refusal must still mirror the transcript"
    assert outside.read_bytes() == b"precious", "symlink target must never be written"
    assert (d / "r1.log").is_symlink(), "pre-planted entry must be left untouched"


def test_refuses_symlink_parent_component(tmp_path):
    """The parent-swap arm the dir-fd walk closes: a component that IS a symlink is
    refused at its own openat -- no pathname re-resolution window exists.
    Mutation probe: walk with a plain pathname open -> the write lands outside."""
    (tmp_path / ".harness/tmp").mkdir(parents=True)
    outside = tmp_path / "outside-dir"
    outside.mkdir()
    (tmp_path / ".harness/tmp/link").symlink_to(outside)
    proc = run(".harness/tmp/link/r1.log", tmp_path)
    assert proc.returncode == 4
    assert not (outside / "r1.log").exists(), "write escaped through a symlink parent"


def test_pre_planted_hard_link_refused_inode_survives(tmp_path):
    """codex r8 P1: O_NOFOLLOW does not stop a HARD link -- an O_TRUNC open through a
    pre-planted leaf hard-linked to a tracked file would destroy that file's content.
    The link() install refuses the existing entry atomically; the inode keeps its
    bytes. Mutation probe: revert to O_TRUNC on the leaf -> 'precious' destroyed."""
    d = tmp_path / ".harness/tmp/rounds"
    d.mkdir(parents=True)
    tracked = tmp_path / "tracked-file"
    tracked.write_bytes(b"precious")
    (d / "r1.log").hardlink_to(tracked)
    proc = run(".harness/tmp/rounds/r1.log", tmp_path)
    assert proc.returncode == 4
    assert tracked.read_bytes() == b"precious", "hard-linked inode was truncated"


def test_replay_refused_first_transcript_survives(tmp_path):
    """codex r9 P2: round logs are write-once evidence -- a replayed invocation must
    not silently discard the first transcript while the gate log still counts both
    outcomes. Mutation probe: install with rename -> second run wins and this reds."""
    proc1 = run(".harness/tmp/rounds/r1.log", tmp_path, payload=b"first\n")
    assert proc1.returncode == 0
    proc2 = run(".harness/tmp/rounds/r1.log", tmp_path, payload=b"second\n")
    assert proc2.returncode == 4
    assert proc2.stdout == b"second\n", "refusal must still mirror the transcript"
    assert (tmp_path / ".harness/tmp/rounds/r1.log").read_bytes() == b"first\n"
    # no temp litter after a refused replay
    assert [p.name for p in (tmp_path / ".harness/tmp/rounds").iterdir()] == ["r1.log"]


def test_creates_missing_intermediate_dirs(tmp_path):
    proc = run(".harness/tmp/a/b/c/r1.log", tmp_path)
    assert proc.returncode == 0, proc.stderr
    assert (tmp_path / ".harness/tmp/a/b/c/r1.log").read_bytes() == b"verdict\n"
