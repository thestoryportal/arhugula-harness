"""U-RT-48 pidfile primitive tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from harness_runtime.admin.pidfile import (
    DEFAULT_PIDFILE_BASENAME,
    PidfileError,
    claim_pidfile,
    default_pidfile_path,
    pid_is_alive,
    read_pidfile,
    release_pidfile,
    remove_pidfile,
    write_pidfile,
)


def test_default_pidfile_basename() -> None:
    assert DEFAULT_PIDFILE_BASENAME == Path(".harness/runtime.pid")


def test_default_pidfile_path(tmp_path: Path) -> None:
    assert default_pidfile_path(tmp_path) == tmp_path / ".harness/runtime.pid"


def test_write_read_round_trip(tmp_path: Path) -> None:
    path = tmp_path / ".harness/runtime.pid"
    write_pidfile(path, 12345)
    assert read_pidfile(path) == 12345


def test_write_pidfile_creates_parent_directory(tmp_path: Path) -> None:
    path = tmp_path / "newly/nested/dir/runtime.pid"
    assert not path.parent.exists()
    write_pidfile(path, 42)
    assert path.parent.is_dir()
    assert path.is_file()


def test_write_pidfile_atomic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Tmp file must be renamed atomically via os.replace."""
    path = tmp_path / "runtime.pid"
    calls: list[tuple[str, str]] = []
    real_replace = os.replace

    def _spy_replace(src: object, dst: object, *args: object, **kwargs: object) -> object:
        calls.append((str(src), str(dst)))
        return real_replace(src, dst, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(os, "replace", _spy_replace)
    write_pidfile(path, 9999)

    assert len(calls) == 1
    src, dst = calls[0]
    assert src.endswith(".pid.tmp")
    assert dst == str(path)
    assert read_pidfile(path) == 9999


def test_write_pidfile_overwrites_prior_value(tmp_path: Path) -> None:
    path = tmp_path / "runtime.pid"
    write_pidfile(path, 100)
    write_pidfile(path, 200)
    assert read_pidfile(path) == 200


def test_read_pidfile_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(PidfileError, match="not found"):
        read_pidfile(tmp_path / "missing.pid")


def test_read_pidfile_empty_raises(tmp_path: Path) -> None:
    path = tmp_path / "empty.pid"
    path.write_text("")
    with pytest.raises(PidfileError, match="empty"):
        read_pidfile(path)


def test_read_pidfile_non_integer_raises(tmp_path: Path) -> None:
    path = tmp_path / "junk.pid"
    path.write_text("not-a-number\n")
    with pytest.raises(PidfileError, match="not an integer"):
        read_pidfile(path)


def test_read_pidfile_trims_whitespace(tmp_path: Path) -> None:
    path = tmp_path / "padded.pid"
    path.write_text("  4242\n  \n")
    assert read_pidfile(path) == 4242


def test_remove_pidfile_deletes(tmp_path: Path) -> None:
    path = tmp_path / "runtime.pid"
    write_pidfile(path, 1)
    remove_pidfile(path)
    assert not path.exists()


def test_remove_pidfile_idempotent(tmp_path: Path) -> None:
    """Second remove is a no-op (FileNotFoundError swallowed)."""
    path = tmp_path / "runtime.pid"
    write_pidfile(path, 1)
    remove_pidfile(path)
    remove_pidfile(path)  # must not raise
    assert not path.exists()


# --- one live owner per repository root (a daemon and a one-shot share the root) ----------


def _dead_pid() -> int:
    """A pid no process holds: a child that has already been reaped."""
    pid = os.fork()
    if pid == 0:
        os._exit(0)
    os.waitpid(pid, 0)
    return pid


def test_claim_writes_when_absent_and_releases_only_its_own(tmp_path: Path) -> None:
    path = tmp_path / "runtime.pid"
    me = os.getpid()

    assert claim_pidfile(path, me) is True
    assert read_pidfile(path) == me
    assert release_pidfile(path, me) is True
    assert not path.exists()
    assert release_pidfile(path, me) is True  # already absent


def test_a_second_process_does_not_clobber_a_live_owner(tmp_path: Path) -> None:
    path = tmp_path / "runtime.pid"
    owner = os.getppid()  # the test runner's parent is alive for the whole test
    write_pidfile(path, owner)

    assert claim_pidfile(path, os.getpid()) is False
    assert read_pidfile(path) == owner
    assert release_pidfile(path, os.getpid()) is False  # not ours: left in place
    assert read_pidfile(path) == owner


def test_a_stale_pidfile_is_claimed(tmp_path: Path) -> None:
    path = tmp_path / "runtime.pid"
    stale = _dead_pid()
    write_pidfile(path, stale)
    assert pid_is_alive(stale) is False

    assert claim_pidfile(path, os.getpid()) is True
    assert read_pidfile(path) == os.getpid()


def test_a_malformed_pidfile_is_claimed_and_released(tmp_path: Path) -> None:
    path = tmp_path / "runtime.pid"
    path.write_text("junk\n")

    assert claim_pidfile(path, os.getpid()) is True
    assert read_pidfile(path) == os.getpid()
    path.write_text("junk\n")
    assert release_pidfile(path, os.getpid()) is True  # nobody owns junk; it is cleared
    assert not path.exists()


def test_pid_is_alive_sees_this_process_and_not_a_reaped_child() -> None:
    assert pid_is_alive(os.getpid()) is True
    assert pid_is_alive(_dead_pid()) is False
